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
#include "WarscapeEnemyCatalogue.h"
#include "WarscapeEnemyMechanics.h"
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
}

struct npc_warscape_enemy : ScriptedAI
{
    explicit npc_warscape_enemy(Creature* creature) : ScriptedAI(creature) { }
    uint32 meleeWarningDelay = 0;
    void Reset() override
    {
        meleeWarningDelay = 0;
        if (auto const* b=Warscape::FindEnemyBehaviour(me->GetEntry()); b && b->Airborne)
        {
            me->SetHoverHeight(1.5f);
            me->SetHover(true);
        }
    }
    void JustDied(Unit*) override
    {
        if (auto const* b=Warscape::FindEnemyBehaviour(me->GetEntry()); b && b->Airborne)
            me->SetHover(false);
    }
    void AttackStart(Unit* who) override
    {
        if (auto const* b=Warscape::FindEnemyBehaviour(me->GetEntry()); b && b->RangedMaxHit)
            AttackStartCaster(who,20.f);
        else
            ScriptedAI::AttackStart(who);
    }
    void DamageTaken(Unit* attacker,uint32& damage,DamageEffectType type,SpellInfo const* spell) override
    {
        auto const* b=Warscape::FindEnemyBehaviour(me->GetEntry());
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
        if (b && b->FinisherItem)
            damage=Warscape::NonFinishingDamage(me->GetHealth(),damage);
    }
    void DamageDealt(Unit* victim,uint32& damage,DamageEffectType type) override
    {
        auto const* b=Warscape::FindEnemyBehaviour(me->GetEntry());
        if (!b || !b->PoisonMaxHit || type!=DIRECT_DAMAGE || !damage || victim->GetTypeId()!=TYPEID_PLAYER || !roll_chance_i(25))
            return;
        Aura* aura=victim->GetAura(ScarabPoison,me->GetGUID());
        if (!aura)
        {
            me->CastSpell(victim,ScarabPoison,TRIGGERED_FULL_MASK);
            aura=victim->GetAura(ScarabPoison,me->GetGUID());
        }
        if (aura)
        {
            // Refresh severity/duration without postponing the next 18-second tick.
            aura->SetMaxDuration(Warscape::PoisonDuration(b->PoisonMaxHit));
            aura->SetDuration(aura->GetMaxDuration());
        }
    }
    void UpdateAI(uint32 diff) override
    {
        meleeWarningDelay=diff>=meleeWarningDelay ? 0 : meleeWarningDelay-diff;
        if (!UpdateVictim() || me->HasUnitState(UNIT_STATE_CASTING))
            return;
        auto const* b=Warscape::FindEnemyBehaviour(me->GetEntry());
        Unit* victim=me->GetVictim();
        if (!b || (!b->MagicMaxHit && !b->RangedMaxHit))
        {
            DoMeleeAttackIfReady();
            return;
        }
        bool const inMelee=me->IsWithinMeleeRange(victim);
        bool const inRange=me->IsWithinDistInMap(victim,30.f);
        bool const lineOfSight=me->IsWithinLOSInMap(victim);
        if (b && b->RangedMaxHit)
        {
            if (victim->GetTypeId()==TYPEID_PLAYER && me->isAttackReady() && inRange && lineOfSight)
            {
                me->StopMoving();
                me->CastSpell(victim,b->AttackSpell,CastSpellExtraArgs(TRIGGERED_IGNORE_POWER_AND_REAGENT_COST));
                me->resetAttackTimer();
            }
            return; // Ranged-only enemies never fall back to melee.
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
        auto const stats=sObjectMgr->GetWarscapeMonsterStats(GetCaster()->GetEntry());
        auto const& profile=sObjectMgr->GetWarscapeMonsterProfile(GetCaster()->GetEntry());
        auto const equipment=target->GetWarscapeEquipmentBonuses();
        uint32 const style=target->GetWarscapeAttackStyle();
        bool const ranged=b->RangedMaxHit!=0;
        uint64 const attack=Warscape::CombatRoll(stats[ranged ? Warscape::Ranged : Warscape::Magic]+9,profile.AttackBonus);
        uint32 const level=ranged ? Warscape::PlayerRangedDefenceLevel(target->GetRSSkillLevel(Player::RS_Skill::Defence),style)
            : Warscape::PlayerMagicDefenceLevel(target->GetRSSkillLevel(Player::RS_Skill::Magic),target->GetRSSkillLevel(Player::RS_Skill::Defence),style);
        uint64 const defence=Warscape::CombatRoll(level,ranged ? equipment.DefenceRanged : equipment.DefenceMagic);
        bool const accurate=double(urand(0,999999))<Warscape::HitChance(attack,defence)*1000000.0;
        bool const ice=GetSpellInfo()->Id==900712;
        uint32 const hit=accurate ? (ice ? 10 : urand(0,ranged ? b->RangedMaxHit : b->MagicMaxHit)) : 0;
        DealSourceSpellDamage(GetCaster(),target,GetSpellInfo()->Id,hit);
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
        DealSourceSpellDamage(source,GetUnitOwner(),ScarabPoison,hit,true);
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

void AddSC_warscape_enemies()
{
    RegisterCreatureAI(npc_warscape_enemy);
    RegisterSpellScript(spell_warscape_enemy_magic);
    RegisterSpellScript(spell_warscape_enemy_ranged_hybrid);
    RegisterSpellScript(spell_warscape_enemy_poison);
    new item_warscape_ice_cooler();
}
