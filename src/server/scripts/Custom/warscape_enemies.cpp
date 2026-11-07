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
    SpellNonMeleeDamage damage(caster,target,spell,SPELL_SCHOOL_MASK_NATURE);
    damage.damage = Warscape::ScaleHealthOrDamage(osrsDamage);
    damage.periodicLog = periodic;
    caster->SendSpellNonMeleeDamageLog(&damage);
    caster->DealSpellDamage(&damage,true);
}
}

struct npc_warscape_enemy : ScriptedAI
{
    explicit npc_warscape_enemy(Creature* creature) : ScriptedAI(creature) { }
    void DamageTaken(Unit*,uint32& damage,DamageEffectType,SpellInfo const*) override
    {
        auto const* b=Warscape::FindEnemyBehaviour(me->GetEntry());
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
    void UpdateAI(uint32) override
    {
        if (!UpdateVictim() || me->HasUnitState(UNIT_STATE_CASTING))
            return;
        auto const* b=Warscape::FindEnemyBehaviour(me->GetEntry());
        Unit* victim=me->GetVictim();
        if (b && b->MagicMaxHit && victim->GetTypeId()==TYPEID_PLAYER && me->isAttackReady()
            && me->IsWithinDistInMap(victim,30.f) && me->IsWithinLOSInMap(victim)
            && (!me->IsWithinMeleeRange(victim) || roll_chance_i(50)))
        {
            // Preserve native cast timing/visuals, but the scoped effect owns OSRS accuracy/damage.
            me->StopMoving();
            me->CastSpell(victim,NatureBolt,CastSpellExtraArgs(TRIGGERED_IGNORE_POWER_AND_REAGENT_COST));
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
    RegisterSpellScript(spell_warscape_enemy_poison);
    new item_warscape_ice_cooler();
}
