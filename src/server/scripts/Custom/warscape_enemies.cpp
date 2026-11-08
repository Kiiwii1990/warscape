/* Warscape encounter prototypes. Uses native creature, spell, item and aura lifecycles. */
#include "ScriptMgr.h"
#include "ScriptedCreature.h"
#include "SpellScript.h"
#include "SpellAuraEffects.h"
#include "SpellAuras.h"
#include "Spell.h"
#include "SpellMgr.h"
#include "Player.h"
#include "Item.h"
#include "Chat.h"
#include "WorldSession.h"
#include "ObjectMgr.h"
#include "ObjectAccessor.h"
#include "WarscapeEnemyCatalogue.h"
#include "WarscapeEnemyMechanics.h"
#include "WarscapeEnemyRequirements.h"
#include "WarscapeSpecialWeapons.h"
#include "WarscapeCombat.h"
#include "WarscapeEquipment.h"

namespace {
constexpr uint32 NatureBolt = 900701;
constexpr uint32 ScarabPoison = 900702;
void DealSourceSpellDamage(Unit* caster, Unit* target, uint32 spell, uint32 osrsDamage, bool periodic = false)
{
    SpellInfo const* info = sSpellMgr->GetSpellInfo(spell);
    if (!info || !target->IsAlive() || target->IsImmunedToDamage(info))
        return;
    SpellNonMeleeDamage damage(caster,target,spell,info->GetSchoolMask());
    damage.damage = Warscape::ScaleHealthOrDamage(osrsDamage);
    damage.periodicLog = periodic;
    caster->SendSpellNonMeleeDamageLog(&damage);
    caster->DealSpellDamage(&damage,true);
}
bool HasOffhand(Unit* target, uint32 entry)
{
    Player* player=target->ToPlayer();
    Item* item=player ? player->GetItemByPos(INVENTORY_SLOT_BAG_0,EQUIPMENT_SLOT_OFFHAND) : nullptr;
    return item && item->GetEntry()==entry;
}
bool HasHearingProtection(Unit* target, uint32 entry)
{
    Player* player=target->ToPlayer();
    Item* head=player ? player->GetItemByPos(INVENTORY_SLOT_BAG_0,EQUIPMENT_SLOT_HEAD) : nullptr;
    return head && head->GetEntry()==entry;
}

bool HasObstacleProtection(Unit* target, Warscape::EnemyBehaviour const& b)
{
    Player* p=target->ToPlayer();
    Item* item=p && b.ProtectionSlot ? p->GetItemByPos(INVENTORY_SLOT_BAG_0,uint8(b.ProtectionSlot-1)) : nullptr;
    return item && item->GetEntry()==b.ProtectionItem;
}

void ApplyEnemyPoison(Unit* source, Unit* target)
{
    auto const* b=Warscape::FindEnemyBehaviour(source->GetEntry());
    if (!b || !b->PoisonMaxHit || !target->IsAlive() || target->GetTypeId()!=TYPEID_PLAYER || !roll_chance_i(25)) return;
    uint32 const spell=b->PoisonSpell ? b->PoisonSpell : ScarabPoison;
    Aura* aura=target->GetAura(spell,source->GetGUID());
    if (!aura)
    {
        source->CastSpell(target,spell,TRIGGERED_FULL_MASK);
        aura=target->GetAura(spell,source->GetGUID());
    }
    if (aura)
    {
        aura->SetMaxDuration(Warscape::PoisonDuration(b->PoisonMaxHit));
        aura->SetDuration(aura->GetMaxDuration());
    }
}

}

struct npc_warscape_enemy : ScriptedAI
{
    explicit npc_warscape_enemy(Creature* creature) : ScriptedAI(creature) { }
    uint32 meleeWarningDelay = 0;
    bool switchedToMelee = false;
    Warscape::DrakeBreathSequence breath;
    ObjectGuid breathTarget;
    Position breathPosition;
    Warscape::RevenantRecovery recovery;
    bool revenantOpened = false;
    uint32 encounterState = 0;
    uint32 attackCycle = 0;
    Warscape::FastNaturalRegeneration naturalRegeneration;
    bool rockslugWandering = false;
    bool rockslugCouldRegenerate = true;
    ReactStates rockslugPreviousReact = REACT_DEFENSIVE;
    uint32 GetData(uint32 key) const override { return key==Warscape::EncounterStateData ? encounterState : 0; }
    void SetData(uint32 key,uint32 value) override { if (key==Warscape::EncounterStateData) encounterState|=value; }

    void Reset() override
    {
        if (rockslugWandering) {
            me->SetReactState(rockslugPreviousReact);
            me->SetRegenerateHealth(rockslugCouldRegenerate);
            me->GetMotionMaster()->InitializeDefault();
        }
        rockslugWandering=false;
        meleeWarningDelay = 0;
        naturalRegeneration = {};
        if (Warscape::HasFastNaturalRegeneration(me->GetEntry()))
            me->SetRegenerateHealth(false); // Replace, never stack with, native percentage regeneration.
        switchedToMelee = false;
        encounterState = 0;
        attackCycle = urand(0,1)*3;
        revenantOpened = false;
        recovery = {};
        if (auto const* b=Warscape::FindEnemyBehaviour(me->GetEntry()); b && b->TriStyle)
            recovery.Remaining=urand(8,25);
        breath = {};
        breathTarget.Clear();
        if (auto const* b=Warscape::FindEnemyBehaviour(me->GetEntry()); b && b->PoisonImmune)
            me->ApplySpellImmune(0,IMMUNITY_DISPEL,DISPEL_POISON,true);
        if (auto const* b=Warscape::FindEnemyBehaviour(me->GetEntry()); b && b->Airborne)
        {
            me->SetHoverHeight(1.5f);
            me->SetHover(true);
        }
    }
    void JustDied(Unit*) override
    {
        recovery = {};
        breath = {};
        breathTarget.Clear();
        if (auto const* b=Warscape::FindEnemyBehaviour(me->GetEntry()); b && b->Airborne)
            me->SetHover(false);
    }
    void AttackStart(Unit* who) override
    {
        if (rockslugWandering || Warscape::RockslugShouldWander(me->GetEntry(),me->GetHealth())) return;
        if (auto const* b=Warscape::FindEnemyBehaviour(me->GetEntry()); b && (b->CastOnly || (b->RangedMaxHit && !b->Killerwatt)))
            AttackStartCaster(who,20.f);
        else
            ScriptedAI::AttackStart(who);
    }
    void DamageTaken(Unit* attacker,uint32& damage,DamageEffectType type,SpellInfo const* spell) override
    {
        auto const* b=Warscape::FindEnemyBehaviour(me->GetEntry());
        Player* owner=attacker ? attacker->GetCharmerOrOwnerPlayerOrPlayerItself() : nullptr;
        if (owner && Warscape::IsLeafyCreature(me->GetEntry())) {
            Player* player=attacker->ToPlayer();
            Item* mainhand=player ? player->GetWeaponForAttack(BASE_ATTACK,true) : nullptr;
            Item* offhand=player ? player->GetWeaponForAttack(OFF_ATTACK,true) : nullptr;
            bool const allowed=Warscape::CanDamageLeafyCreature(me->GetEntry(),mainhand ? mainhand->GetEntry() : 0,
                offhand ? offhand->GetEntry() : 0,owner->GetRSSkillLevel(Player::RS_Skill::Attack),
                player && type==DIRECT_DAMAGE && !spell,mainhand && !mainhand->IsBroken());
            if (!allowed) {
                damage=0;
                if (!meleeWarningDelay) {
                    ChatHandler(owner->GetSession()).SendSysMessage("Its thick hide resists that attack. Use a leaf-bladed sword; remove any ordinary off-hand weapon.");
                    meleeWarningDelay=3000;
                }
                return;
            }
        }
        if (auto const* rule=Warscape::FindEnemyEquipmentRequirement(me->GetEntry()); rule && owner) {
            Item* head=owner->GetItemByPos(INVENTORY_SLOT_BAG_0,EQUIPMENT_SLOT_HEAD);
            Item* offhand=owner->GetItemByPos(INVENTORY_SLOT_BAG_0,EQUIPMENT_SLOT_OFFHAND);
            if (!Warscape::MeetsEnemyEquipmentRequirement(me->GetEntry(),head ? head->GetEntry() : 0,offhand ? offhand->GetEntry() : 0)) {
                damage=0;
                if (!meleeWarningDelay) {
                    ChatHandler(owner->GetSession()).SendSysMessage(rule->Message);
                    meleeWarningDelay=3000;
                }
                return;
            }
        }
        if (b && attacker && attacker->GetTypeId()==TYPEID_PLAYER && Warscape::RejectAirborneMelee(
            b->Airborne!=0,type==DIRECT_DAMAGE,spell && spell->DmgClass==SPELL_DAMAGE_CLASS_MELEE))
        {
            damage=0;
            if (!meleeWarningDelay)
            {
                ChatHandler(attacker->ToPlayer()->GetSession()).SendSysMessage("The Aviansie is flying too high for you to attack using melee.");
                meleeWarningDelay=3000;
            }
        }
        if (b && b->EarthenArmour && !(encounterState & Warscape::ReinforcedState) && damage
            && type!=DOT && uint64(me->GetHealth())*100 < uint64(me->GetMaxHealth())*60)
        {
            encounterState|=Warscape::ReinforcedState;
            if (attacker && attacker->GetTypeId()==TYPEID_PLAYER)
                ChatHandler(attacker->ToPlayer()->GetSession()).SendSysMessage("The nagua reinforces its outer body to protect itself.");
        }
        if (b && b->FinisherItem) {
            Player* player=attacker ? attacker->ToPlayer() : nullptr;
            Item* weapon=player ? player->GetItemByPos(INVENTORY_SLOT_BAG_0,EQUIPMENT_SLOT_MAINHAND) : nullptr;
            bool const bypass=Warscape::CanBypassRockslugSalt(me->GetEntry(),weapon ? weapon->GetEntry() : 0,
                player ? player->GetRSSkillLevel(Player::RS_Skill::Attack) : 0,
                player && type==DIRECT_DAMAGE && !spell,weapon && !weapon->IsBroken());
            if (!bypass) damage=Warscape::NonFinishingDamage(me->GetHealth(),damage);
        }
    }
    void DamageDealt(Unit* victim,uint32& damage,DamageEffectType type) override
    {
        if (type==DIRECT_DAMAGE && damage)
        {
            ApplyEnemyPoison(me,victim);
            auto const* b=Warscape::FindEnemyBehaviour(me->GetEntry());
            if (b && b->VenomSpell && victim->IsAlive() && victim->GetTypeId()==TYPEID_PLAYER
                && !victim->HasAura(b->VenomSpell) && roll_chance_i(25))
            {
                me->CastSpell(victim,b->VenomSpell,TRIGGERED_FULL_MASK);
                if (Aura* venom=victim->GetAura(b->VenomSpell,me->GetGUID()))
                {
                    venom->SetMaxDuration(-1);
                    venom->SetDuration(-1);
                }
            }
        }
    }

    void UpdateAI(uint32 diff) override
    {
        if (!rockslugWandering && Warscape::RockslugShouldWander(me->GetEntry(),me->GetHealth()) && !me->IsInEvadeMode()) {
            rockslugWandering=true;
            rockslugPreviousReact=me->GetReactState();
            rockslugCouldRegenerate=me->CanRegenerateHealth();
            me->SetReactState(REACT_PASSIVE);
            me->SetRegenerateHealth(false); // Preserve the finishing window instead of native out-of-combat healing.
            me->AttackStop();
            me->GetMotionMaster()->Remove(CHASE_MOTION_TYPE);
            me->GetMotionMaster()->MoveRandom(3.f);
        }
        if (rockslugWandering) {
            if (!me->IsAlive() || me->IsInEvadeMode()) return;
            Player* owner=me->GetLootRecipient(); // Resolve native tap ownership each update; never retain a player pointer.
            bool const valid=owner && owner->IsAlive() && owner->IsInMap(me);
            if (!Warscape::RockslugWanderCanRemain(valid,owner ? me->GetExactDist2d(owner) : 1000.f))
                EnterEvadeMode(EVADE_REASON_NO_HOSTILES);
            return;
        }
        if (Warscape::HasFastNaturalRegeneration(me->GetEntry())) {
            uint32 const pulses=naturalRegeneration.Advance(diff);
            if (me->IsAlive() && !me->IsInEvadeMode()) {
                uint32 const healing=Warscape::FastNaturalHealing(me->GetHealth(),me->GetMaxHealth(),pulses);
                if (healing) me->SetHealth(me->GetHealth()+healing);
            }
        }
        meleeWarningDelay=diff>=meleeWarningDelay ? 0 : meleeWarningDelay-diff;
        recovery.Advance(diff);
        if (!UpdateVictim())
        {
            breath = {};
            breathTarget.Clear();
            return;
        }
        uint32 const pulses=breath.Advance(diff);
        if (pulses)
        {
            Player* target=ObjectAccessor::GetPlayer(*me,breathTarget);
            if (target && target->IsAlive() && me->IsValidAttackTarget(target) && target->IsInMap(me)
                && target->GetExactDist2d(&breathPosition)<=2.5f && std::abs(target->GetPositionZ()-breathPosition.GetPositionZ())<4.f)
            {
                bool const protectedByShield=HasOffhand(target,Warscape::AntiDragonShield);
                for (uint32 i=0;i<pulses && target->IsAlive() && me->IsAlive();++i)
                    DealSourceSpellDamage(me,target,900725,urand(protectedByShield ? 0 : 6,Warscape::DrakeBreathMaximum(protectedByShield)));
            }
        }
        if (!me->IsAlive() || me->HasUnitState(UNIT_STATE_CASTING)) return;
        Unit* victim=me->GetVictim();
        if (!victim || !victim->IsAlive()) return; // A breath pulse may have killed/cleared the victim.
        auto const* b=Warscape::FindEnemyBehaviour(me->GetEntry());
        if (b && b->ScreamHit && victim->GetTypeId()==TYPEID_PLAYER && !HasHearingProtection(victim,b->HearingItem))
        {
            if (me->isAttackReady() && me->IsWithinMeleeRange(victim) && me->IsWithinLOSInMap(victim))
            {
                me->CastSpell(victim,b->AttackSpell,TRIGGERED_FULL_MASK);
                me->resetAttackTimer();
                if (!meleeWarningDelay)
                {
                    ChatHandler(victim->ToPlayer()->GetSession()).SendSysMessage("The Banshee's scream hurts! Wear earmuffs on your head.");
                    meleeWarningDelay=15000;
                }
            }
            return;
        }
        if (b && b->DoubleFirst)
        {
            bool const reach=b->DoubleMagic ? me->IsWithinDistInMap(victim,30.f) : me->IsWithinMeleeRange(victim);
            if (victim->GetTypeId()==TYPEID_PLAYER && me->isAttackReady() && reach && me->IsWithinLOSInMap(victim))
            {
                me->StopMoving();
                me->CastSpell(victim,b->AttackSpell,TRIGGERED_FULL_MASK);
                me->resetAttackTimer();
            }
            return;
        }
        if (!b || (!b->MagicMaxHit && !b->RangedMaxHit))
        {
            DoMeleeAttackIfReady();
            return;
        }
        bool const inMelee=me->IsWithinMeleeRange(victim);
        bool const inRange=me->IsWithinDistInMap(victim,30.f);
        bool const lineOfSight=me->IsWithinLOSInMap(victim);
        if (b && b->CastOnly)
        {
            if (victim->GetTypeId()==TYPEID_PLAYER && me->isAttackReady() && inRange && lineOfSight)
            {
                me->StopMoving();
                me->CastSpell(victim,b->AttackSpell,TRIGGERED_FULL_MASK);
                me->resetAttackTimer();
            }
            return;
        }
        if (b && b->TriStyle)
        {
            if (victim->GetTypeId()==TYPEID_PLAYER && me->isAttackReady() && inRange && lineOfSight)
            {
                Player* player=victim->ToPlayer();
                auto const equipment=player->GetWarscapeEquipmentBonuses();
                uint32 const stance=player->GetWarscapeAttackStyle();
                uint64 const magicDefence=Warscape::CombatRoll(Warscape::PlayerMagicDefenceLevel(
                    player->GetRSSkillLevel(Player::RS_Skill::Magic),player->GetRSSkillLevel(Player::RS_Skill::Defence),stance),equipment.DefenceMagic);
                uint64 const rangedDefence=Warscape::CombatRoll(Warscape::PlayerRangedDefenceLevel(player->GetRSSkillLevel(Player::RS_Skill::Defence),stance),equipment.DefenceRanged);
                auto const* variant=Warscape::FindEnemyVariant(me->GetEntry());
                int32 const meleeBonus=variant && variant->MeleeLane==1 ? equipment.DefenceSlash : equipment.DefenceStab;
                uint64 const meleeDefence=Warscape::CombatRoll(player->GetRSSkillLevel(Player::RS_Skill::Defence)+8,meleeBonus);
                uint8 const choice=revenantOpened ? Warscape::RevenantStyle(magicDefence,rangedDefence,meleeDefence,inMelee) : 0;
                if (uint32 const heal=recovery.TryHeal(me->GetHealth(),me->GetMaxHealth()))
                {
                    me->ModifyHealth(int32(heal));
                    me->CastSpell(me,b->HealVisual,TRIGGERED_FULL_MASK);
                }
                revenantOpened=true;
                me->StopMoving();
                if (choice==2)
                {
                    me->Attack(victim,true);
                    DoMeleeAttackIfReady();
                }
                else
                {
                    me->Attack(victim,false);
                    me->CastSpell(victim,choice==1 ? b->AlternateSpell : b->AttackSpell,TRIGGERED_FULL_MASK);
                    me->resetAttackTimer();
                }
            }
            return;
        }
        if (b && b->MagicRanged)
        {
            if (victim->GetTypeId()==TYPEID_PLAYER && me->isAttackReady() && inRange && lineOfSight)
            {
                me->StopMoving();
                bool const magic=b->CycleThree ? Warscape::CycleUsesMagic(attackCycle) : roll_chance_i(50);
                me->CastSpell(victim,magic ? b->AttackSpell : b->AlternateSpell,TRIGGERED_FULL_MASK);
                if (b->CycleThree) attackCycle=Warscape::AdvanceAttackCycle(attackCycle);
                me->resetAttackTimer();
            }
            return;
        }
        if (b && b->RangedMaxHit)
        {
            if (b->Killerwatt && inMelee) { DoMeleeAttackIfReady(); return; }
            if (b->RangedToMelee && inMelee && !switchedToMelee && me->isAttackReady())
            {
                switchedToMelee=true;
                me->GetMotionMaster()->MoveChase(victim);
                me->resetAttackTimer(); // Source Xil spends a turn changing styles.
                return;
            }
            if (b->RangedToMelee && switchedToMelee)
            {
                DoMeleeAttackIfReady();
                return;
            }
            if (victim->GetTypeId()==TYPEID_PLAYER && me->isAttackReady() && inRange && lineOfSight
                && ((b->DrakeBreath && breath.Ready()) || (b->WyvernBreath && roll_chance_i(33))))
            {
                me->StopMoving();
                if (b->DrakeBreath)
                {
                    breathTarget=victim->GetGUID();
                    breathPosition.Relocate(victim);
                    breath.Launch();
                    ChatHandler(victim->ToPlayer()->GetSession()).SendSysMessage("The Drake launches volcanic breath at your position. Move!");
                    me->CastSpell(breathPosition,900725,TRIGGERED_FULL_MASK);
                }
                else me->CastSpell(victim,900727,TRIGGERED_FULL_MASK);
                me->resetAttackTimer();
                return;
            }
            if (b->MixedRanged && inMelee && roll_chance_i(50))
            {
                DoMeleeAttackIfReady();
                return;
            }
            if (victim->GetTypeId()==TYPEID_PLAYER && me->isAttackReady() && inRange && lineOfSight)
            {
                me->StopMoving();
                me->CastSpell(victim,b->AttackSpell,CastSpellExtraArgs(TRIGGERED_IGNORE_POWER_AND_REAGENT_COST));
                if (b->DrakeBreath) ++breath.NormalAttacks;
                me->resetAttackTimer();
            }
            return;
        }
        if (b && b->MagicMaxHit && victim->GetTypeId()==TYPEID_PLAYER && me->isAttackReady()
            && Warscape::MagicRangeAllowed(b->MagicMeleeOnly!=0,inMelee,inRange,lineOfSight)
            && (!inMelee || roll_chance_i(50)))
        {
            uint32 spell=b->AttackSpell ? b->AttackSpell : NatureBolt;
            if (b->AlternateSpell && roll_chance_i(50)) spell=b->AlternateSpell;
            me->StopMoving();
            me->CastSpell(victim,spell,CastSpellExtraArgs(TRIGGERED_IGNORE_POWER_AND_REAGENT_COST));
            me->resetAttackTimer();
            return;
        }
        DoMeleeAttackIfReady();
    }
};

class spell_warscape_enemy_magic : public SpellScript
{
    PrepareSpellScript(spell_warscape_enemy_magic);
    bool Load() override
    {
        auto const* b=Warscape::FindEnemyBehaviour(GetCaster()->GetEntry());
        return GetCaster()->GetTypeId()==TYPEID_UNIT && b && b->MagicMaxHit;
    }
    void Hit(SpellEffIndex index)
    {
        PreventHitDefaultEffect(index);
        Player* target=GetHitPlayer();
        auto const* b=Warscape::FindEnemyBehaviour(GetCaster()->GetEntry());
        if (!target || !b)
            return;
        auto const stats=sObjectMgr->GetWarscapeMonsterStats(GetCaster()->GetEntry());
        auto const equipment=target->GetWarscapeEquipmentBonuses();
        uint64 const attack=Warscape::CombatRoll(stats[Warscape::Magic]+9,0);
        uint64 const defence=Warscape::CombatRoll(Warscape::PlayerMagicDefenceLevel(
            target->GetRSSkillLevel(Player::RS_Skill::Magic),target->GetRSSkillLevel(Player::RS_Skill::Defence),target->GetWarscapeAttackStyle()),equipment.DefenceMagic);
        bool const accurate=double(urand(0,999999))<Warscape::HitChance(attack,defence)*1000000.0;
        DealSourceSpellDamage(GetCaster(),target,NatureBolt,accurate ? urand(0,b->MagicMaxHit) : 0);
    }
    void Register() override { OnEffectHitTarget += SpellEffectFn(spell_warscape_enemy_magic::Hit,EFFECT_0,SPELL_EFFECT_SCHOOL_DAMAGE); }
};

// Dedicated ranged/hybrid spell records keep all prior spells and scripts scoped.
class spell_warscape_enemy_ranged_hybrid : public SpellScript
{
    PrepareSpellScript(spell_warscape_enemy_ranged_hybrid);
    bool Load() override
    {
        if (GetCaster()->GetTypeId()!=TYPEID_UNIT) return false;
        auto const* b=Warscape::FindEnemyBehaviour(GetCaster()->GetEntry());
        uint32 const spell=GetSpellInfo()->Id;
        return b && (b->RangedMaxHit || b->MagicMaxHit) && (spell==b->AttackSpell || spell==b->AlternateSpell);
    }
    void Hit(SpellEffIndex index)
    {
        PreventHitDefaultEffect(index);
        Player* target=GetHitPlayer();
        auto const* b=Warscape::FindEnemyBehaviour(GetCaster()->GetEntry());
        if (!target || !b || target->IsImmunedToDamage(GetSpellInfo())) return;
        if (b->MagicMeleeOnly && !GetCaster()->IsWithinMeleeRange(target)) return;
        Item* head=target->GetItemByPos(INVENTORY_SLOT_BAG_0,EQUIPMENT_SLOT_HEAD);
        if (auto const* rule=Warscape::FindUnprotectedProjectile(GetCaster()->GetEntry(),GetSpellInfo()->Id,head ? head->GetEntry() : 0)) {
            // Unprotected saliva bypasses the custom accuracy roll, retaining native damage immunity above.
            DealSourceSpellDamage(GetCaster(),target,GetSpellInfo()->Id,urand(rule->Minimum,rule->Maximum));
            if (target->IsAlive())
                ChatHandler(target->GetSession()).SendSysMessage("The Sourhog's acid burns your eyes! Wear reinforced goggles.");
            return;
        }
        auto const stats=sObjectMgr->GetWarscapeMonsterStats(GetCaster()->GetEntry());
        auto const& profile=sObjectMgr->GetWarscapeMonsterProfile(GetCaster()->GetEntry());
        auto const equipment=target->GetWarscapeEquipmentBonuses();
        uint32 const style=target->GetWarscapeAttackStyle();
        bool const ranged=b->RangedMaxHit && (!b->MagicMaxHit || GetSpellInfo()->Id==b->AlternateSpell);
        bool const magicDefence=!ranged || b->MagicRanged || b->RangedMagicDefence;
        uint64 const attack=Warscape::CombatRoll(stats[ranged ? Warscape::Ranged : Warscape::Magic]+9,ranged ? ((b->SeparateBonuses || b->RangedBonus) ? int32(b->RangedBonus) : profile.AttackBonus) : (b->MagicBonus ? int32(b->MagicBonus) : profile.AttackBonus));
        uint32 const level=!magicDefence ? Warscape::PlayerRangedDefenceLevel(target->GetRSSkillLevel(Player::RS_Skill::Defence),style)
            : Warscape::PlayerMagicDefenceLevel(target->GetRSSkillLevel(Player::RS_Skill::Magic),target->GetRSSkillLevel(Player::RS_Skill::Defence),style);
        uint64 const defence=Warscape::CombatRoll(level,magicDefence ? equipment.DefenceMagic : equipment.DefenceRanged);
        bool const unprotected=b->ProtectionItem && !HasObstacleProtection(target,*b);
        bool const accurate=(unprotected && !b->Killerwatt) || double(urand(0,999999))<Warscape::HitChance(attack,defence)*1000000.0;
        bool const ice=GetSpellInfo()->Id==900712;
        uint32 const hit=accurate ? (ice ? 10 : urand(0,unprotected ? b->UnprotectedHit : ranged ? b->RangedMaxHit : b->MagicMaxHit)) : 0;
        DealSourceSpellDamage(GetCaster(),target,GetSpellInfo()->Id,hit);
        if (ranged && hit) ApplyEnemyPoison(GetCaster(),target);
        if (!ranged && b->TriStyle && b->RootSpell && hit && target->IsAlive() && roll_chance_i(25))
        {
            GetCaster()->CastSpell(target,b->RootSpell,TRIGGERED_FULL_MASK);
            if (Aura* root=target->GetAura(b->RootSpell,GetCaster()->GetGUID()))
            {
                root->SetMaxDuration(3000);
                root->SetDuration(3000);
            }
        }
        if (ice && accurate && target->IsAlive())
        {
            GetCaster()->CastSpell(target,900713,TRIGGERED_FULL_MASK);
            if (Aura* root=target->GetAura(900713,GetCaster()->GetGUID()))
            {
                root->SetMaxDuration(3000);
                root->SetDuration(3000);
            }
        }
    }
    void Register() override { OnEffectHitTarget += SpellEffectFn(spell_warscape_enemy_ranged_hybrid::Hit,EFFECT_0,SPELL_EFFECT_SCHOOL_DAMAGE); }
};

class spell_warscape_enemy_double : public SpellScript
{
    PrepareSpellScript(spell_warscape_enemy_double);
    bool Load() override { auto const* b=Warscape::FindEnemyBehaviour(GetCaster()->GetEntry()); return GetCaster()->GetTypeId()==TYPEID_UNIT && b && b->DoubleFirst; }
    void Hit(SpellEffIndex index)
    {
        PreventHitDefaultEffect(index);
        Player* target=GetHitPlayer();auto const* b=Warscape::FindEnemyBehaviour(GetCaster()->GetEntry());
        if (!target || !b || (!b->DoubleMagic && !GetCaster()->IsWithinMeleeRange(target))) return;
        auto stats=sObjectMgr->GetWarscapeMonsterStats(GetCaster()->GetEntry());
        auto const& profile=sObjectMgr->GetWarscapeMonsterProfile(GetCaster()->GetEntry());
        auto eq=target->GetWarscapeEquipmentBonuses();auto const* variant=Warscape::FindEnemyVariant(GetCaster()->GetEntry());
        uint64 const attack=Warscape::CombatRoll(stats[b->DoubleMagic ? Warscape::Magic : Warscape::Attack]+(b->DoubleMagic ? 9 : 8),b->DoubleMagic ? int32(b->MagicBonus) : profile.AttackBonus);
        uint32 const level=b->DoubleMagic ? Warscape::PlayerMagicDefenceLevel(target->GetRSSkillLevel(Player::RS_Skill::Magic),target->GetRSSkillLevel(Player::RS_Skill::Defence),target->GetWarscapeAttackStyle()) : target->GetRSSkillLevel(Player::RS_Skill::Defence)+8;
        int32 const bonus=b->DoubleMagic ? eq.DefenceMagic : variant && variant->MeleeLane==1 ? eq.DefenceSlash : eq.DefenceStab;
        uint64 const defence=Warscape::CombatRoll(level,bonus);
        for (uint32 max : {b->DoubleFirst,b->DoubleSecond})
        {
            if (!target->IsAlive() || !GetCaster()->IsAlive()) break;
            bool const accurate=double(urand(0,999999))<Warscape::HitChance(attack,defence)*1000000.0;
            DealSourceSpellDamage(GetCaster(),target,GetSpellInfo()->Id,accurate ? urand(0,max) : 0);
        }
    }
    void Register() override { OnEffectHitTarget += SpellEffectFn(spell_warscape_enemy_double::Hit,EFFECT_0,SPELL_EFFECT_SCHOOL_DAMAGE); }
};
class spell_warscape_enemy_venom : public AuraScript
{
    PrepareAuraScript(spell_warscape_enemy_venom);
    bool Load() override
    {
        if (!GetCasterGUID().IsCreature() || GetUnitOwner()->GetTypeId()!=TYPEID_PLAYER) return false;
        auto const* b=Warscape::FindEnemyBehaviour(GetCasterGUID().GetEntry());
        return b && b->VenomSpell==GetSpellInfo()->Id;
    }
    void Period(AuraEffect const*,bool& periodic,int32& period) { periodic=true;period=18000; }
    void Amount(AuraEffect const*,int32& amount,bool& recalculate) { amount=60;recalculate=false; }
    void Tick(AuraEffect const* effect)
    {
        PreventDefaultAction();
        uint32 const hit=Warscape::VenomDamage(effect->GetAmount());
        Unit* caster=GetCaster() ? GetCaster() : GetUnitOwner();
        const_cast<AuraEffect*>(effect)->SetAmount(Warscape::NextVenomDamage(hit)*10);
        DealSourceSpellDamage(caster,GetUnitOwner(),GetSpellInfo()->Id,hit,true);
    }
    void Register() override
    {
        DoEffectCalcPeriodic += AuraEffectCalcPeriodicFn(spell_warscape_enemy_venom::Period,EFFECT_0,SPELL_AURA_PERIODIC_DAMAGE);
        DoEffectCalcAmount += AuraEffectCalcAmountFn(spell_warscape_enemy_venom::Amount,EFFECT_0,SPELL_AURA_PERIODIC_DAMAGE);
        OnEffectPeriodic += AuraEffectPeriodicFn(spell_warscape_enemy_venom::Tick,EFFECT_0,SPELL_AURA_PERIODIC_DAMAGE);
    }
};

class spell_warscape_enemy_scream : public SpellScript
{
    PrepareSpellScript(spell_warscape_enemy_scream);
    bool Load() override
    {
        auto const* b=Warscape::FindEnemyBehaviour(GetCaster()->GetEntry());
        return GetCaster()->GetTypeId()==TYPEID_UNIT && b && b->ScreamHit;
    }
    void Hit(SpellEffIndex index)
    {
        PreventHitDefaultEffect(index);
        Player* target=GetHitPlayer();
        auto const* b=Warscape::FindEnemyBehaviour(GetCaster()->GetEntry());
        if (!target || !b || HasHearingProtection(target,b->HearingItem) || !GetCaster()->IsWithinMeleeRange(target)) return;
        DealSourceSpellDamage(GetCaster(),target,GetSpellInfo()->Id,b->ScreamHit);
    }
    void Register() override { OnEffectHitTarget += SpellEffectFn(spell_warscape_enemy_scream::Hit,EFFECT_0,SPELL_EFFECT_SCHOOL_DAMAGE); }
};

class spell_warscape_enemy_breath : public SpellScript
{
    PrepareSpellScript(spell_warscape_enemy_breath);
    bool Load() override
    {
        auto const* b=Warscape::FindEnemyBehaviour(GetCaster()->GetEntry());
        return GetCaster()->GetTypeId()==TYPEID_UNIT && b && (b->DrakeBreath || b->WyvernBreath);
    }
    void Hit(SpellEffIndex index)
    {
        PreventHitDefaultEffect(index);
        if (GetSpellInfo()->Id!=900727) return; // Ground effect is visual; AI owns the four Drake pulses.
        Player* target=GetHitPlayer();
        if (!target || target->IsImmunedToDamage(GetSpellInfo())) return;
        bool const protectedByShield=HasOffhand(target,Warscape::ElementalShield);
        DealSourceSpellDamage(GetCaster(),target,GetSpellInfo()->Id,urand(0,Warscape::WyvernBreathMaximum(protectedByShield)));
        if (target->IsAlive() && Warscape::WyvernFreezes(protectedByShield,urand(0,6)))
        {
            GetCaster()->CastSpell(target,900728,TRIGGERED_FULL_MASK);
            if (Aura* root=target->GetAura(900728,GetCaster()->GetGUID()))
            {
                root->SetMaxDuration(6600);
                root->SetDuration(6600);
            }
        }
    }
    void Register() override { OnEffectHitTarget += SpellEffectFn(spell_warscape_enemy_breath::Hit,EFFECT_ALL,SPELL_EFFECT_SCHOOL_DAMAGE); }
};

class spell_warscape_enemy_poison : public AuraScript
{
    PrepareAuraScript(spell_warscape_enemy_poison);
    bool Load() override
    {
        if (!GetCasterGUID().IsCreature()) return false;
        auto const* b=Warscape::FindEnemyBehaviour(GetCasterGUID().GetEntry());
        return GetUnitOwner()->GetTypeId()==TYPEID_PLAYER && GetCasterGUID().IsCreature() && b && b->PoisonMaxHit;
    }
    void Period(AuraEffect const*,bool& periodic,int32& amplitude) { periodic=true;amplitude=Warscape::PoisonPeriod; }
    void Amount(AuraEffect const*,int32& amount,bool& recalculate)
    {
        auto const* b=Warscape::FindEnemyBehaviour(GetCasterGUID().GetEntry());
        amount=b ? Warscape::ScaleHealthOrDamage(b->PoisonMaxHit) : 0;recalculate=false;
    }
    void Tick(AuraEffect const*)
    {
        PreventDefaultAction();
        auto const* b=Warscape::FindEnemyBehaviour(GetCasterGUID().GetEntry());
        if (!b) return;
        uint32 const elapsed=std::max(0,GetMaxDuration()-GetDuration());
        uint32 const hit=Warscape::PoisonHit(b->PoisonMaxHit,elapsed);
        // The aura's saved duration keeps decay after relog; no raw creature pointer is retained.
        Unit* source=GetCaster() ? GetCaster() : GetUnitOwner();
        DealSourceSpellDamage(source,GetUnitOwner(),GetSpellInfo()->Id,hit,true);
    }
    void Register() override
    {
        DoEffectCalcPeriodic += AuraEffectCalcPeriodicFn(spell_warscape_enemy_poison::Period,EFFECT_0,SPELL_AURA_PERIODIC_DAMAGE);
        DoEffectCalcAmount += AuraEffectCalcAmountFn(spell_warscape_enemy_poison::Amount,EFFECT_0,SPELL_AURA_PERIODIC_DAMAGE);
        OnEffectPeriodic += AuraEffectPeriodicFn(spell_warscape_enemy_poison::Tick,EFFECT_0,SPELL_AURA_PERIODIC_DAMAGE);
    }
};

class item_warscape_ice_cooler : public ItemScript
{
public:
    item_warscape_ice_cooler() : ItemScript("item_warscape_ice_cooler") { }
    bool OnUse(Player* player,Item* item,SpellCastTargets const& targets) override
    {
        // Complete every scripted item-use path so the stock client releases its item cursor.
        player->SendEquipError(EQUIP_ERR_OK,item,nullptr);
        Unit* unit=targets.GetUnitTarget();
        Creature* target=unit ? unit->ToCreature() : nullptr;
        auto const* b=target ? Warscape::FindEnemyBehaviour(target->GetEntry()) : nullptr;
        if (!player->IsAlive() || !target || !b || b->FinisherItem!=item->GetEntry() || !target->IsAlive() || target->IsInEvadeMode()
            || !player->IsValidAttackTarget(target) || !player->IsWithinDistInMap(target,5.f) || !player->IsWithinLOSInMap(target)
            || (target->GetLootRecipient() && !target->isTappedBy(player)))
        {
            ChatHandler(player->GetSession()).SendSysMessage("Select a living desert lizard within 5 yards that you may loot.");
            return true;
        }
        bool const ready=Warscape::CanCoolLizard(target->GetHealth());
        uint32 const entry=item->GetEntry();
        player->DestroyItemCount(entry,1,true);
        if (!ready)
        {
            ChatHandler(player->GetSession()).SendSysMessage("The lizard needs less than 5 Hitpoints. Ice cooler consumed.");
            return true;
        }
        if (!target->GetLootRecipient()) target->SetLootRecipient(player);
        target->LowerPlayerDamageReq(target->GetHealth());
        Unit::Kill(player,target);
        ChatHandler(player->GetSession()).SendSysMessage("The ice cooler finishes the lizard.");
        return true;
    }
};

class item_warscape_rock_hammer : public ItemScript
{
public:
    item_warscape_rock_hammer() : ItemScript("item_warscape_rock_hammer") { }
    bool OnUse(Player* player,Item* item,SpellCastTargets const& targets) override
    {
        // Complete every scripted item-use path so the stock client releases its item cursor.
        player->SendEquipError(EQUIP_ERR_OK,item,nullptr);
        Unit* unit=targets.GetUnitTarget();
        Creature* target=unit ? unit->ToCreature() : nullptr;
        auto const* b=target ? Warscape::FindEnemyBehaviour(target->GetEntry()) : nullptr;
        if (!player->IsAlive() || !target || !b || b->FinisherItem!=item->GetEntry() || !target->IsAlive() || target->IsInEvadeMode()
            || !player->IsValidAttackTarget(target) || !player->IsWithinDistInMap(target,5.f) || !player->IsWithinLOSInMap(target)
            || (target->GetLootRecipient() && !target->isTappedBy(player)))
        {
            ChatHandler(player->GetSession()).SendSysMessage("Select a living gargoyle within 5 yards that you may loot.");
            return true;
        }
        bool const ready=Warscape::CanSmashGargoyle(target->GetHealth());
        if (!ready)
        {
            ChatHandler(player->GetSession()).SendSysMessage("The gargoyle must have 8 Hitpoints or lower.");
            return true;
        }
        if (!target->GetLootRecipient()) target->SetLootRecipient(player);
        target->LowerPlayerDamageReq(target->GetHealth());
        Unit::Kill(player,target);
        ChatHandler(player->GetSession()).SendSysMessage("The rock hammer smashes the gargoyle.");
        return true;
    }
};

class item_warscape_consumable_finisher : public ItemScript
{
public:
    item_warscape_consumable_finisher(char const* name, uint32 maximum) : ItemScript(name), maximumHealth(maximum) { }
    uint32 maximumHealth;
    bool OnUse(Player* player,Item* item,SpellCastTargets const& targets) override
    {
        // Complete every scripted item-use path so the stock client releases its item cursor.
        player->SendEquipError(EQUIP_ERR_OK,item,nullptr);
        Unit* unit=targets.GetUnitTarget();
        Creature* target=unit ? unit->ToCreature() : nullptr;
        auto const* b=target ? Warscape::FindEnemyBehaviour(target->GetEntry()) : nullptr;
        if (!player->IsAlive() || !target || !b || b->FinisherItem!=item->GetEntry() || !target->IsAlive() || target->IsInEvadeMode()
            || !player->IsValidAttackTarget(target) || !player->IsWithinDistInMap(target,5.f) || !player->IsWithinLOSInMap(target)
            || (target->GetLootRecipient() && !target->isTappedBy(player)))
        {
            ChatHandler(player->GetSession()).SendSysMessage("Select the matching living obstacle creature within 5 yards that you may loot.");
            return true;
        }
        bool const ready=Warscape::CanUseConsumableFinisher(target->GetHealth(),maximumHealth);
        player->DestroyItemCount(item->GetEntry(),1,true);
        if (!ready)
        {
            ChatHandler(player->GetSession()).SendSysMessage("The creature is not weak enough. One dose was consumed.");
            return true;
        }
        if (!target->GetLootRecipient()) target->SetLootRecipient(player);
        target->LowerPlayerDamageReq(target->GetHealth());
        Unit::Kill(player,target);
        ChatHandler(player->GetSession()).SendSysMessage("The finishing dose kills the creature.");
        return true;
    }
};

class item_warscape_fungicide_spray : public ItemScript
{
public:
    item_warscape_fungicide_spray() : ItemScript("item_warscape_fungicide_spray") { }
    bool OnUse(Player* player,Item* item,SpellCastTargets const& targets) override
    {
        player->SendEquipError(EQUIP_ERR_OK,item,nullptr);
        if (!player->IsAlive()) return true;
        int32 const charges=item->GetSpellCharges(Warscape::FungicideChargeSlot);
        if (charges<0 || charges>10) {
            ChatHandler(player->GetSession()).SendSysMessage("This spray has invalid charges; please report it.");
            return true;
        }
        if (!charges) {
            if (!Warscape::CanRefillFungicide(charges,player->HasItemCount(Warscape::FungicideRefill,1))) {
                ChatHandler(player->GetSession()).SendSysMessage("The spray is empty. Carry one Fungicide and use it again to refill.");
                return true;
            }
            player->DestroyItemCount(Warscape::FungicideRefill,1,true);
            item->SetSpellCharges(Warscape::FungicideChargeSlot,10);
            item->SetState(ITEM_CHANGED,player);
            ChatHandler(player->GetSession()).SendSysMessage("Fungicide spray refilled: 10 charges.");
            return true;
        }
        Unit* unit=targets.GetUnitTarget();
        Creature* target=unit ? unit->ToCreature() : nullptr;
        auto const* b=target ? Warscape::FindEnemyBehaviour(target->GetEntry()) : nullptr;
        if (!target || !b || b->FinisherItem!=Warscape::FungicideDose || !target->IsAlive() || target->IsInEvadeMode()
            || !player->IsValidAttackTarget(target) || !player->IsWithinDistInMap(target,5.f) || !player->IsWithinLOSInMap(target)
            || (target->GetLootRecipient() && !target->isTappedBy(player))) {
            ChatHandler(player->GetSession()).SendSysMessage("Select a living Zygomite within 5 yards that you may loot.");
            return true;
        }
        // Check readiness before changing item state; normal kill runs only once.
        bool const ready=Warscape::CanUseConsumableFinisher(target->GetHealth(),79);
        int32 const remaining=Warscape::FungicideAfterUse(charges);
        item->SetSpellCharges(Warscape::FungicideChargeSlot,remaining);
        item->SetState(ITEM_CHANGED,player);
        ChatHandler(player->GetSession()).PSendSysMessage("Fungicide spray: {} charges remaining.",remaining);
        if (!ready) {
            ChatHandler(player->GetSession()).SendSysMessage("The Zygomite must be below 8 Hitpoints. One charge was used.");
            return true;
        }
        if (!target->GetLootRecipient()) target->SetLootRecipient(player);
        target->LowerPlayerDamageReq(target->GetHealth());
        Unit::Kill(player,target);
        return true;
    }
};

// Only this parent owns its list; callbacks remove GUIDs through the native lifecycle.
struct npc_warscape_nechryael : npc_warscape_enemy
{
    explicit npc_warscape_nechryael(Creature* creature) : npc_warscape_enemy(creature), summons(creature) { }
    SummonList summons;
    uint32 summonDelay = 12000;
    void Reset() override { summons.DespawnAll(); summonDelay=12000; npc_warscape_enemy::Reset(); }
    void JustSummoned(Creature* summon) override { summons.Summon(summon); }
    void SummonedCreatureDespawn(Creature* summon) override { summons.Despawn(summon); }
    void JustDied(Unit* killer) override { summons.DespawnAll(); npc_warscape_enemy::JustDied(killer); }
    void UpdateAI(uint32 diff) override
    {
        npc_warscape_enemy::UpdateAI(diff);
        Unit* target=me->GetVictim();
        bool const reachable=me->IsAlive() && target && target->IsAlive() && target->GetTypeId()==TYPEID_PLAYER
            && me->IsWithinMeleeRange(target) && me->IsWithinLOSInMap(target);
        if (!Warscape::CanSummonDeathSpawn(summons.size(),reachable)) return;
        if (diff < summonDelay) { summonDelay-=diff; return; }
        summonDelay=12000;
        me->SummonCreature(Warscape::DeathSpawnEntry,me->GetPosition(),TEMPSUMMON_TIMED_DESPAWN,60s);
    }
};

struct npc_warscape_death_spawn : ScriptedAI
{
    explicit npc_warscape_death_spawn(Creature* creature) : ScriptedAI(creature) { }
    ObjectGuid parentGuid, targetGuid;
    void MoveInLineOfSight(Unit*) override { }
    void IsSummonedBy(WorldObject* summoner) override
    {
        Creature* parent=summoner ? summoner->ToCreature() : nullptr;
        Unit* target=parent ? parent->GetVictim() : nullptr;
        if (!parent || parent->GetEntry()!=902400 || !target || target->GetTypeId()!=TYPEID_PLAYER) {
            me->DespawnOrUnsummon(); return;
        }
        parentGuid=parent->GetGUID();targetGuid=target->GetGUID();
        AttackStart(target);
    }
    void AttackStart(Unit* target) override
    {
        if (target && target->GetGUID()==targetGuid) ScriptedAI::AttackStart(target);
    }
    void UpdateAI(uint32) override
    {
        Creature* parent=ObjectAccessor::GetCreature(*me,parentGuid);
        Player* target=ObjectAccessor::GetPlayer(*me,targetGuid);
        bool const valid=target && target->IsAlive() && target->IsInMap(me) && me->IsValidAttackTarget(target);
        if (!Warscape::DeathSpawnCanRemain(parent && parent->IsAlive() && !parent->IsInEvadeMode(),valid,
                target ? me->GetExactDist2d(target) : 1000.f)) {
            me->DespawnOrUnsummon(); return;
        }
        if (me->GetVictim()!=target) AttackStart(target);
        if (me->IsWithinLOSInMap(target)) DoMeleeAttackIfReady();
    }
};

struct npc_warscape_dust_devil : npc_warscape_enemy
{
    explicit npc_warscape_dust_devil(Creature* creature) : npc_warscape_enemy(creature) { }
    void UpdateAI(uint32) override
    {
        if (!UpdateVictim() || me->HasUnitState(UNIT_STATE_CASTING)) return;
        Unit* target=me->GetVictim();
        auto const* rule=Warscape::FindEnemyRangedMeleeProtection(me->GetEntry());
        if (!rule || !target || target->GetTypeId()!=TYPEID_PLAYER || !target->IsAlive()) return;
        if (me->isAttackReady() && me->IsWithinMeleeRange(target) && me->IsWithinLOSInMap(target)) {
            me->CastSpell(target,rule->Spell,TRIGGERED_FULL_MASK);
            me->resetAttackTimer();
        }
    }
};

class spell_warscape_ranged_melee : public SpellScript
{
    PrepareSpellScript(spell_warscape_ranged_melee);
    bool Load() override {
        auto const* rule=Warscape::FindEnemyRangedMeleeProtection(GetCaster()->GetEntry());
        return GetCaster()->GetTypeId()==TYPEID_UNIT && rule && rule->Spell==GetSpellInfo()->Id;
    }
    void Hit(SpellEffIndex index)
    {
        PreventHitDefaultEffect(index);
        Player* target=GetHitPlayer();
        auto const* rule=Warscape::FindEnemyRangedMeleeProtection(GetCaster()->GetEntry());
        if (!target || !rule || !target->IsAlive() || !GetCaster()->IsWithinMeleeRange(target)
            || !GetCaster()->IsWithinLOSInMap(target) || target->IsImmunedToDamage(GetSpellInfo())) return;
        Item* head=target->GetItemByPos(INVENTORY_SLOT_BAG_0,EQUIPMENT_SLOT_HEAD);
        if (!Warscape::HasRangedMeleeProtection(*rule,head ? head->GetEntry() : 0)) {
            ChatHandler(target->GetSession()).SendSysMessage("The dust burns! Wear a facemask.");
            DealSourceSpellDamage(GetCaster(),target,GetSpellInfo()->Id,rule->UnprotectedHit);
            return;
        }
        auto const stats=sObjectMgr->GetWarscapeMonsterStats(GetCaster()->GetEntry());
        auto const& profile=sObjectMgr->GetWarscapeMonsterProfile(GetCaster()->GetEntry());
        auto const equipment=target->GetWarscapeEquipmentBonuses();
        uint64 const attack=Warscape::CombatRoll(stats[Warscape::Attack]+9,profile.AttackBonus);
        uint64 const defence=Warscape::CombatRoll(Warscape::PlayerRangedDefenceLevel(
            target->GetRSSkillLevel(Player::RS_Skill::Defence),target->GetWarscapeAttackStyle()),equipment.DefenceRanged);
        bool const accurate=double(urand(0,999999))<Warscape::HitChance(attack,defence)*1000000.0;
        DealSourceSpellDamage(GetCaster(),target,GetSpellInfo()->Id,accurate ? urand(0,rule->ProtectedMaximum) : 0);
    }
    void Register() override { OnEffectHitTarget += SpellEffectFn(spell_warscape_ranged_melee::Hit,EFFECT_0,SPELL_EFFECT_SCHOOL_DAMAGE); }
};

void AddSC_warscape_enemies()
{
    RegisterCreatureAI(npc_warscape_enemy);
    RegisterCreatureAI(npc_warscape_dust_devil);
    RegisterSpellScript(spell_warscape_ranged_melee);
    RegisterCreatureAI(npc_warscape_nechryael);
    RegisterCreatureAI(npc_warscape_death_spawn);
    RegisterSpellScript(spell_warscape_enemy_magic);
    RegisterSpellScript(spell_warscape_enemy_ranged_hybrid);
    RegisterSpellScript(spell_warscape_enemy_poison);
    RegisterSpellScript(spell_warscape_enemy_breath);
    RegisterSpellScript(spell_warscape_enemy_scream);
    RegisterSpellScript(spell_warscape_enemy_double);
    RegisterSpellScript(spell_warscape_enemy_venom);
    new item_warscape_ice_cooler();
    new item_warscape_rock_hammer();
    new item_warscape_fungicide_spray();
    new item_warscape_consumable_finisher("item_warscape_salt",40);
    new item_warscape_consumable_finisher("item_warscape_fungicide_dose",79);
}
