#include "WarscapeEnemyCatalogue.h"
#include "WarscapeEnemyRequirements.h"
#include "WarscapeSpecialWeapons.h"
#include "WarscapeCombat.h"
#include "WarscapeEnemyMechanics.h"
#include "WarscapeEquipment.h"
#include "WarscapeCurrency.h"
#include <cassert>
#include <map>
#include <string_view>
int main() {
    assert(!Warscape::CanUseSpecialWeapon(Warscape::LeafBladedBattleaxe,64));
    assert(Warscape::CanUseSpecialWeapon(Warscape::LeafBladedBattleaxe,65));
    for (unsigned entry : {902304u,902404u,902405u,902406u,902407u}) {
        assert(Warscape::CanDamageLeafyCreature(entry,Warscape::LeafBladedBattleaxe,0,65,true,true));
        assert(Warscape::CanDamageLeafyCreature(entry,Warscape::LeafBladedBattleaxe,Warscape::LeafBladedSword,65,true,true));
        assert(!Warscape::CanDamageLeafyCreature(entry,Warscape::LeafBladedBattleaxe,2131,65,true,true));
        assert(!Warscape::CanDamageLeafyCreature(entry,Warscape::LeafBladedBattleaxe,0,64,true,true));
        assert(!Warscape::CanDamageLeafyCreature(entry,Warscape::LeafBladedBattleaxe,0,65,false,true));
        assert(!Warscape::CanDamageLeafyCreature(entry,Warscape::LeafBladedBattleaxe,0,65,true,false));
        assert(Warscape::LeafWeaponMaximumHit(entry,Warscape::LeafBladedBattleaxe,0,65,true,true,40)==47);
        assert(Warscape::LeafWeaponMaximumHit(entry,Warscape::LeafBladedBattleaxe,0,65,true,true,5)==5);
        assert(Warscape::LeafWeaponMaximumHit(entry,Warscape::LeafBladedBattleaxe,0,65,true,true,6)==7);
        assert(Warscape::LeafWeaponMaximumHit(entry,Warscape::LeafBladedBattleaxe,0,65,true,true,0)==0);
        assert(Warscape::LeafWeaponMaximumHit(entry,Warscape::LeafBladedBattleaxe,0,65,true,true,0xFFFFFFFF)==0xFFFFFFFF);
        assert(Warscape::LeafWeaponMaximumHit(entry,Warscape::LeafBladedSword,0,65,true,true,40)==40);
        assert(Warscape::LeafWeaponMaximumHit(entry,Warscape::LeafBladedBattleaxe,2131,65,true,true,40)==40);
        assert(Warscape::LeafWeaponMaximumHit(entry,Warscape::LeafBladedBattleaxe,0,64,true,true,40)==40);
        assert(Warscape::LeafWeaponMaximumHit(entry,Warscape::LeafBladedBattleaxe,0,65,false,true,40)==40);
        assert(Warscape::LeafWeaponMaximumHit(entry,Warscape::LeafBladedBattleaxe,0,65,true,false,40)==40);
    }
    assert(Warscape::LeafWeaponMaximumHit(902600,Warscape::LeafBladedBattleaxe,0,65,true,true,40)==40);
    for (unsigned entry=902600; entry<=902606; ++entry) {
        auto const* variant=Warscape::FindEnemyVariant(entry);
        assert(variant && variant->FamilyId==95 && variant->SourceCombat);
        assert(Warscape::EnemyMaximumHit(entry,99)==(entry<902605 ? 1u : 2u));
        auto const* pool=Warscape::FindEnemyLootPool(entry);
        assert(pool && pool->Total==4096000);
        assert(Warscape::SelectEnemyLootOutcome(entry,0));
        assert(Warscape::SelectEnemyLootOutcome(entry,pool->Total-1));
        assert(!Warscape::SelectEnemyLootOutcome(entry,pool->Total));
    }
    assert(!Warscape::CanUseSpecialWeapon(Warscape::LeafBladedSpear,49));
    assert(Warscape::CanUseSpecialWeapon(Warscape::LeafBladedSpear,50));
    for (unsigned entry : {902304u,902404u,902405u,902406u,902407u}) {
        assert(Warscape::CanDamageLeafyCreature(entry,Warscape::LeafBladedSpear,0,50,true,true));
        assert(!Warscape::CanDamageLeafyCreature(entry,Warscape::LeafBladedSpear,Warscape::LeafBladedSword,50,true,true));
        assert(!Warscape::CanDamageLeafyCreature(entry,Warscape::LeafBladedSword,Warscape::LeafBladedSpear,50,true,true));
        assert(!Warscape::CanDamageLeafyCreature(entry,Warscape::LeafBladedSpear,0,49,true,true));
        assert(!Warscape::CanDamageLeafyCreature(entry,Warscape::LeafBladedSpear,0,50,false,true));
        assert(!Warscape::CanDamageLeafyCreature(entry,Warscape::LeafBladedSpear,0,50,true,false));
    }
    assert(!Warscape::CanUseSpecialWeapon(Warscape::LeafBladedSword,49));
    assert(Warscape::CanUseSpecialWeapon(Warscape::LeafBladedSword,50));
    for (unsigned entry : {902304u,902404u,902405u,902406u,902407u}) {
        assert(Warscape::CanDamageLeafyCreature(entry,Warscape::LeafBladedSword,0,50,true,true));
        assert(!Warscape::CanDamageLeafyCreature(entry,2131,0,50,true,true));
        assert(!Warscape::CanDamageLeafyCreature(entry,Warscape::LeafBladedSword,2131,50,true,true));
        assert(!Warscape::CanDamageLeafyCreature(entry,Warscape::LeafBladedSword,0,49,true,true));
        assert(!Warscape::CanDamageLeafyCreature(entry,Warscape::LeafBladedSword,0,50,false,true));
        assert(!Warscape::CanDamageLeafyCreature(entry,Warscape::LeafBladedSword,0,50,true,false));
    }
    assert(Warscape::CanDamageLeafyCreature(902400,0,0,1,false,false));
    assert(!Warscape::CanUseSpecialWeapon(Warscape::BrineSabre,39));
    assert(Warscape::CanUseSpecialWeapon(Warscape::BrineSabre,40));
    assert(Warscape::CanUseSpecialWeapon(2131,1));
    assert(Warscape::CanBypassRockslugSalt(902401,Warscape::BrineSabre,40,true,true));
    assert(!Warscape::CanBypassRockslugSalt(902409,Warscape::BrineSabre,40,true,true));
    assert(!Warscape::CanBypassRockslugSalt(902401,2131,40,true,true));
    assert(!Warscape::CanBypassRockslugSalt(902401,Warscape::BrineSabre,39,true,true));
    assert(!Warscape::CanBypassRockslugSalt(902401,Warscape::BrineSabre,40,false,true));
    assert(!Warscape::CanBypassRockslugSalt(902401,Warscape::BrineSabre,40,true,false));
    assert(!Warscape::RockslugShouldWander(902401,0));
    assert(Warscape::RockslugShouldWander(902401,1));
    assert(Warscape::RockslugShouldWander(902401,10));
    assert(!Warscape::RockslugShouldWander(902401,11));
    assert(!Warscape::RockslugShouldWander(902409,10));
    assert(Warscape::RockslugWanderCanRemain(true,30.f));
    assert(!Warscape::RockslugWanderCanRemain(true,30.1f));
    assert(!Warscape::RockslugWanderCanRemain(false,0.f));
    assert(Warscape::HasFastNaturalRegeneration(902103));
    assert(Warscape::HasFastNaturalRegeneration(902304));
    assert(!Warscape::HasFastNaturalRegeneration(902404));
    assert(!Warscape::HasFastNaturalRegeneration(902401));
    Warscape::FastNaturalRegeneration regeneration;
    assert(regeneration.Advance(2999)==0);
    assert(regeneration.Advance(1)==1 && regeneration.Elapsed==0);
    assert(regeneration.Advance(6500)==2 && regeneration.Elapsed==500);
    assert(regeneration.Advance(2500)==1 && regeneration.Elapsed==0);
    assert(Warscape::FastNaturalHealing(0,100,1)==0);
    assert(Warscape::FastNaturalHealing(100,100,1)==0);
    assert(Warscape::FastNaturalHealing(110,100,1)==0);
    assert(Warscape::FastNaturalHealing(50,100,1)==10);
    assert(Warscape::FastNaturalHealing(99,100,1)==1);
    assert(Warscape::FastNaturalHealing(50,100,1000000)==50);
    assert(Warscape::FastNaturalHealing(1,0xFFFFFFFFu,0xFFFFFFFFu)==0xFFFFFFFEu);
    assert(regeneration.Advance(0xFFFFFFFFu)==1431655u && regeneration.Elapsed==2295);
    regeneration={}; assert(regeneration.Elapsed==0);

    auto const* dust=Warscape::FindEnemyRangedMeleeProtection(902204);
    assert(dust && dust->ProtectedMaximum==8 && dust->UnprotectedHit==16);
    assert(!Warscape::HasRangedMeleeProtection(*dust,0));
    assert(!Warscape::HasRangedMeleeProtection(*dust,902588));
    assert(Warscape::HasRangedMeleeProtection(*dust,902587));
    assert(Warscape::FindEnemyRangedMeleeProtection(902205)->ProtectedMaximum==10);
    assert(!Warscape::FindEnemyRangedMeleeProtection(902402));
    auto const* acid=Warscape::FindUnprotectedProjectile(902403,900771,0);
    assert(acid && acid->Minimum==20 && acid->Maximum==30);
    assert(Warscape::FindUnprotectedProjectile(902403,900771,902587));
    assert(!Warscape::FindUnprotectedProjectile(902403,900771,902588));
    assert(!Warscape::FindUnprotectedProjectile(902403,900770,0));
    assert(!Warscape::FindUnprotectedProjectile(902402,900771,0));
    assert(!Warscape::MeetsEnemyEquipmentRequirement(902402,0,0));
    assert(!Warscape::MeetsEnemyEquipmentRequirement(902402,902475,0));
    assert(!Warscape::MeetsEnemyEquipmentRequirement(902402,0,902587));
    assert(Warscape::MeetsEnemyEquipmentRequirement(902402,902587,0));
    assert(Warscape::MeetsEnemyEquipmentRequirement(902402,902587,902586));
    assert(!Warscape::MeetsEnemyEquipmentRequirement(902301,902586,0));
    assert(!Warscape::MeetsEnemyEquipmentRequirement(902301,0,0));
    assert(!Warscape::MeetsEnemyEquipmentRequirement(902301,0,902476));
    assert(Warscape::MeetsEnemyEquipmentRequirement(902301,0,902586));
    assert(Warscape::MeetsEnemyEquipmentRequirement(902300,0,0));
    assert(Warscape::CanSummonDeathSpawn(0,true) && Warscape::CanSummonDeathSpawn(1,true));
    assert(!Warscape::CanSummonDeathSpawn(2,true) && !Warscape::CanSummonDeathSpawn(0,false));
    assert(Warscape::DeathSpawnCanRemain(true,true,21.f));
    assert(!Warscape::DeathSpawnCanRemain(false,true,0.f));
    assert(!Warscape::DeathSpawnCanRemain(true,false,0.f));
    assert(!Warscape::DeathSpawnCanRemain(true,true,21.1f));
    assert(Warscape::FungicideAfterUse(10)==9 && Warscape::FungicideAfterUse(1)==0);
    assert(Warscape::FungicideAfterUse(0)==0);
    assert(Warscape::CanRefillFungicide(0,true));
    assert(!Warscape::CanRefillFungicide(1,true) && !Warscape::CanRefillFungicide(0,false));
    assert(!Warscape::CanUseConsumableFinisher(0,40));
    assert(Warscape::CanUseConsumableFinisher(40,40));
    assert(!Warscape::CanUseConsumableFinisher(41,40));
    assert(Warscape::CanUseConsumableFinisher(79,79));
    assert(!Warscape::CanUseConsumableFinisher(80,79));
    for (unsigned start : {0u,3u}) {
        auto p=start;
        for(unsigned i=0;i<18;++i) {
            assert(Warscape::CycleUsesMagic(p)==((start+i)%6<3));
            p=Warscape::AdvanceAttackCycle(p);
        }
    }
    assert(Warscape::FindEnemyBehaviour(902302)->CycleThree==1);
    assert(!Warscape::CanSmashGargoyle(0));
    assert(Warscape::CanSmashGargoyle(1) && Warscape::CanSmashGargoyle(80));
    assert(!Warscape::CanSmashGargoyle(81));
    assert(Warscape::FindEnemyBehaviour(902208)->FinisherItem==902531);
    assert(Warscape::EnemyFlatArmour(902208)==-2);
    assert(Warscape::FindEnemyBehaviour(902103)->PoisonMaxHit==8);
    assert(Warscape::FindEnemyBehaviour(902105)->PoisonMaxHit==3);
    assert(Warscape::StatefulDefence(0,60,true,false,0)==60);
    assert(Warscape::StatefulDefence(0,60,true,false,Warscape::LureCutState)==10);
    assert(Warscape::StatefulDefence(1,80,true,false,Warscape::LureCutState)==80);
    assert(Warscape::StatefulDefence(0,30,false,true,Warscape::ReinforcedState)==50);
    assert(Warscape::StatefulDefence(1,50,false,true,Warscape::ReinforcedState)==70);
    assert(Warscape::StatefulDefence(2,50,false,true,Warscape::ReinforcedState)==10);
    unsigned venom=6;
    for(unsigned i=0;i<20;++i) { assert(Warscape::VenomDamage(venom*10)==std::min(6+2*i,20u));venom=Warscape::NextVenomDamage(venom); }
    assert(Warscape::VenomDamage(-100)==6 && Warscape::VenomDamage(10000)==20);
    assert(Warscape::EnemyFlatArmour(902001)==-4 && Warscape::EnemyFlatArmour(902003)==-4);
    for(unsigned entry=902000;entry<=902009;++entry) {
        auto const* pool=Warscape::FindEnemyLootPool(entry); assert(pool);
        std::uint64_t cursor=0;
        for(unsigned i=pool->First;i<pool->First+pool->Count;++i) {
            auto const& o=Warscape::EnemyLootOutcomes[i];
            assert(Warscape::SelectEnemyLootOutcome(entry,cursor)==&o);
            assert(Warscape::SelectEnemyLootOutcome(entry,cursor+o.Weight-1)==&o);
            cursor+=o.Weight;
        }
        assert(cursor==pool->Total);
    }

    Warscape::MonsterProfile noMelee;
    noMelee.Base={0,0,128,105,105,128}; noMelee.Growth.fill(0);
    assert(noMelee.Scale(1)==noMelee.Base);
    assert(Warscape::MinimumMonsterStat(Warscape::Defence)==1 && Warscape::MinimumMonsterStat(Warscape::Hitpoints)==1);
    assert(Warscape::RevenantStyle(100,100,100,true)==0);
    assert(Warscape::RevenantStyle(100,99,1,false)==1);
    assert(Warscape::RevenantStyle(100,99,1,true)==2);
    assert(Warscape::RevenantStyle(1,99,100,true)==0);
    Warscape::RevenantRecovery healing;
    healing.Remaining=8;
    assert(healing.TryHeal(500,1000)==0);
    assert(healing.TryHeal(0,1000)==0);
    assert(healing.TryHeal(499,1000)==200);
    assert(healing.Remaining==7 && healing.TryHeal(1,1000)==0);
    healing.Advance(8999);assert(healing.TryHeal(1,1000)==0);
    healing.Advance(1);assert(healing.TryHeal(49,100)==51);
    for (unsigned i=0;i<6;++i) { healing.Advance(9000);assert(healing.TryHeal(1,1000)==200); }
    healing.Advance(999999);assert(healing.Remaining==0 && healing.TryHeal(1,1000)==0);
    healing={};assert(healing.TryHeal(1,1000)==0);
    for (unsigned entry : {901902u,901904u}) {
        auto const* pool=Warscape::FindEnemyLootPool(entry);bool found=false;
        for (unsigned i=pool->First;i<pool->First+pool->Count;++i) {
            auto const& o=Warscape::EnemyLootOutcomes[i];
            if (o.ExtraItem==Warscape::CoinsItem) { assert(o.Loot==0);found=true; }
        }
        assert(found);
    }
    for (auto const& pool:Warscape::EnemyBonusPools) {
        assert((pool.Entry>=901903 && pool.Entry<=901904) || (pool.Entry>=902000 && pool.Entry<=902009) || (pool.Entry>=902100 && pool.Entry<=902106) || (pool.Entry>=902200 && pool.Entry<=902208) || (pool.Entry>=902300 && pool.Entry<=902304));
        std::uint64_t cursor=0;
        for (unsigned i=pool.First;i<pool.First+pool.Count;++i) {
            auto const& o=Warscape::EnemyBonusDrops[i];
            assert(Warscape::SelectEnemyBonus(pool,cursor)==&o);
            assert(Warscape::SelectEnemyBonus(pool,cursor+o.Weight-1)==&o);
            assert(o.Step && o.Max>=o.Min && (o.Max-o.Min)%o.Step==0);
            if (o.Item==902463) {
                for (unsigned count=o.Min;count<=o.Max;count+=o.Step) assert(count%2==0);
            }
            cursor+=o.Weight;
        }
        assert(cursor==pool.Total && !Warscape::SelectEnemyBonus(pool,cursor));
    }

    assert(Warscape::FindEnemyVariant(901806)->MeleeLane==0); // Wyvern slash accuracy rolls against Stab defence.
    Warscape::DrakeBreathSequence sequence;
    assert(!sequence.Ready());
    for (unsigned i=0;i<7;++i) ++sequence.NormalAttacks;
    assert(sequence.Ready());
    sequence.Launch();
    assert(sequence.Advance(1199)==0);
    assert(sequence.Advance(1)==1);
    assert(sequence.Advance(600)==1);
    assert(sequence.Advance(999999)==2);
    assert(sequence.Advance(999999)==0);
    assert(!sequence.Ready());
    sequence.Launch();
    sequence = {}; // Evade/death cancellation cannot emit any later pulse.
    assert(sequence.Advance(999999)==0 && !sequence.Ready());
    assert(Warscape::DrakeBreathMaximum(true)==4 && Warscape::DrakeBreathMaximum(false)==8);
    assert(Warscape::WyvernBreathMaximum(true)==10 && Warscape::WyvernBreathMaximum(false)==60);
    for (unsigned i=0;i<7;++i) {
        assert(Warscape::WyvernFreezes(true,i)==(i==0));
        assert(Warscape::WyvernFreezes(false,i));
    }
    for (unsigned entry=901800;entry<=901806;++entry) {
        auto const* pool=Warscape::FindEnemyLootPool(entry);
        assert(pool);
        std::uint64_t cursor=0;
        for (unsigned i=pool->First;i<pool->First+pool->Count;++i) {
            auto const& o=Warscape::EnemyLootOutcomes[i];
            assert(Warscape::SelectEnemyLootOutcome(entry,cursor)==&o);
            assert(Warscape::SelectEnemyLootOutcome(entry,cursor+o.Weight-1)==&o);
            if (o.ExtraItem) assert(o.ExtraMin>0 && o.ExtraMin<=o.ExtraMax && o.ExtraMax<=10000);
            cursor+=o.Weight;
        }
        assert(cursor==pool->Total && !Warscape::SelectEnemyLootOutcome(entry,cursor));
    }

    assert(Warscape::ItemStackLimit(Warscape::CoinsItem, 2147483647) == 2147483647u);
    assert(Warscape::ItemStackLimit(Warscape::CoinsItem, 200) == 200u);
    assert(Warscape::ItemStackLimit(1, 2147483647) == 2147483646u);
    assert(Warscape::ItemStackLimit(1, -1) == 2147483646u);
    assert(Warscape::ItemStackLimit(1, 200) == 200u);
    assert(Warscape::MergeCoinCount(200, 7000, Warscape::CoinStackLimit) == 7000u);
    assert(Warscape::MergeCoinCount(Warscape::CoinStackLimit - 3, 7000, Warscape::CoinStackLimit) == 3u);
    assert(Warscape::MergeCoinCount(Warscape::CoinStackLimit, 1, Warscape::CoinStackLimit) == 0u);
    assert(Warscape::MergeCoinCount(0, 0xffffffffu, Warscape::CoinStackLimit) == Warscape::CoinStackLimit);
    assert(Warscape::LootStackCount(7000, Warscape::CoinStackLimit) == 1u);
    assert(Warscape::LootStackCount(0xffffffffu, Warscape::CoinStackLimit) == 3u);
    // Reference-expanded piles conserve every coin and occupy one slot at normal sizes.
    for (unsigned total : {255u, 256u, 3000u, 7000u}) {
        unsigned pile = 0, remaining = total;
        while (remaining) {
            unsigned amount = std::min(remaining, 200u);
            unsigned merged = Warscape::MergeCoinCount(pile, amount, Warscape::CoinStackLimit);
            assert(merged == amount);
            pile += merged;
            remaining -= amount;
        }
        assert(pile == total);
    }

    std::map<unsigned,unsigned> counts;
    for (unsigned r=0;r<128;++r) { auto id=Warscape::SelectEnemyLoot(901000,r); assert(id>=901000 && id<=901016); ++counts[id]; }
    assert(counts[901005]==28); // 15 coins, Wiki 28/128
    assert(counts[901006]==2);  // 20 coins, Wiki 2/128
    assert(counts[901007]==1);  // 1 coin, Wiki 1/128
    assert(counts[901008]==44); // F2P nothing outcome; bones still guaranteed
    assert(Warscape::SelectEnemyLoot(901000,128)==0);
    assert(Warscape::SelectEnemyLoot(622,0)==0);
    assert(Warscape::MaxHit(1,-15)==1);
    assert(Warscape::ScaleHealthOrDamage(5)==50);
    assert(Warscape::CombatRoll(9,-21)==387);
    assert(Warscape::CombatRoll(9,-15)==441);
    assert(Warscape::MaxHit(1,-53)==0); // Ordinary rats can hit zero only.
    assert(Warscape::MaxHit(23,0)==3);
    assert(Warscape::ScaleHealthOrDamage(8)==80);
    assert(Warscape::SelectEnemyLoot(901010,0)==901100);
    assert(Warscape::SelectEnemyLoot(901020,0)==0); // No unconditional rat loot.
    assert(Warscape::SelectEnemyLoot(901021,0)==901120);
    assert(Warscape::SelectEnemyLoot(901022,0)==901130);
    assert(Warscape::SelectEnemyLoot(901023,0)==901140);
    assert(Warscape::SelectEnemyLoot(901024,0)==901150);
    for (auto const& pool: Warscape::EnemyLootPools) {
        assert(pool.Total>0 && pool.First+pool.Count<=Warscape::EnemyLootOutcomes.size());
        std::uint64_t total=0;
        for(unsigned i=pool.First;i<pool.First+pool.Count;++i) total+=Warscape::EnemyLootOutcomes[i].Weight;
        assert(total==pool.Total);
        assert(Warscape::SelectEnemyLoot(pool.Entry,pool.Total)==0);
    }
    assert(Warscape::FindEnemyVariant(622)==nullptr);
    assert(Warscape::FindEnemyVariant(901000)->FamilyId==1);
    assert(Warscape::FindEnemyVariant(901010)->FamilyId==2);
    for(unsigned id=901020;id<=901024;++id) {
        auto const* v=Warscape::FindEnemyVariant(id);
        assert(v && v->FamilyId==3 && std::string_view(v->Family)=="Rats");
    }
    // Previously accepted families continue using their loaded profile formulas.
    assert(Warscape::EnemyMaximumHit(901000,9)==9);
    assert(Warscape::EnemyMaximumHit(901010,9)==9);
    assert(Warscape::EnemyMeleeDefence(901020,0,42)==42);
    assert(Warscape::EnemyMaximumHit(622,5)==5);
    assert(Warscape::EnemyMeleeDefence(622,1,17)==17);
    assert(Warscape::EnemyMaximumHit(901033,2)==3); // Published Black bear cap.
    assert(Warscape::EnemyMaximumHit(901035,4)==5);
    assert(Warscape::EnemyMaximumHit(901041,9)==0); // Explicit zero must stay zero.
    assert(Warscape::EnemyMaximumHit(901042,0)==1);
    assert(Warscape::EnemyMeleeDefence(901030,0,0)==2);
    assert(Warscape::EnemyMeleeDefence(901030,2,0)==5);
    assert(Warscape::EnemyMeleeDefence(901049,0,0)==35);
    assert(Warscape::EnemyMeleeDefence(901049,1,0)==15);
    assert(Warscape::EnemyMeleeDefence(901049,3,123)==123);
    for(unsigned id=901030;id<=901050;++id) {
        auto const* v=Warscape::FindEnemyVariant(id);
        assert(v && v->SourceCombat && v->NativeAttackAnimation && v->MeleeLane<=2);
        if(v->FamilyId==7 || v->FamilyId==8) assert(Warscape::SelectEnemyLoot(id,0)==0);
    }
    assert(Warscape::EnemyVariants.size()==351);
    // New batch: all 128 chicken slots and every training-crab roll stay in their own pool.
    for (std::uint32_t entry : {901062u, 901063u, 901064u, 901065u}) {
        auto const* pool = Warscape::FindEnemyLootPool(entry);
        assert(pool && pool->Total == 128);
        auto const first = Warscape::SelectEnemyLoot(entry, 0);
        for (std::uint32_t roll = 0; roll < 128; ++roll)
            assert(Warscape::SelectEnemyLoot(entry, roll) == first + (roll < 64 ? 0 : roll < 96 ? 1 : 2));
        assert(Warscape::EnemyMaximumHit(entry, 99) == 0);
    }
    for (std::uint32_t entry : {901071u, 901072u, 901073u, 901074u}) {
        auto const* pool = Warscape::FindEnemyLootPool(entry);
        assert(pool && pool->Total == 16384);
        for (std::uint32_t roll = 0; roll < pool->Total; ++roll) {
            auto const loot = Warscape::SelectEnemyLoot(entry, roll);
            auto const first = 903000 + (entry - 901060) * 100;
            assert(loot == 0 || (loot >= first && loot < first + pool->Count));
        }
    }
    assert(Warscape::SelectEnemyLoot(901068, 0) == 0);
    assert(Warscape::EnemyMeleeDefence(901075, 1, 999) == 12);
    for (std::uint32_t entry = 901100; entry <= 901138; ++entry) {
        auto const* pool = Warscape::FindEnemyLootPool(entry);
        auto const* variant = Warscape::FindEnemyVariant(entry);
        assert(pool && variant && variant->SourceCombat && variant->NativeAttackAnimation);
        // Exhaustive selection also covers the 1,638,400-slot composed Hellhound pool.
        for (std::uint32_t roll = 0; roll < pool->Total; ++roll) {
            auto const selected = Warscape::SelectEnemyLoot(entry, roll);
            auto const first = 906000 + (entry - 901100) * 100;
            assert(selected == 0 || (selected >= first && selected < first + pool->Count));
        }
    }
    assert(Warscape::SelectEnemyLoot(901130, 0) == 0);
    assert(Warscape::EnemyMeleeDefence(901137, 0, 999) == -21);
    assert(Warscape::EnemyMeleeDefence(901138, 1, 999) == -10);
    assert(Warscape::EnemyMaximumHit(901134, 0) == 11);
    assert(Warscape::EnemyMaximumHit(901136, 0) == 13);
    for (std::uint32_t entry = 901200; entry <= 901252; ++entry) {
        auto const* pool = Warscape::FindEnemyLootPool(entry);
        auto const* variant = Warscape::FindEnemyVariant(entry);
        assert(pool && variant && variant->SourceCombat && variant->NativeAttackAnimation);
        std::uint32_t cursor = 0;
        for (std::uint32_t i = 0; i < pool->Count; ++i) {
            auto const& outcome = Warscape::EnemyLootOutcomes[pool->First + i];
            assert(Warscape::SelectEnemyLoot(entry, cursor) == outcome.Loot);
            assert(Warscape::SelectEnemyLoot(entry, cursor + outcome.Weight - 1) == outcome.Loot);
            cursor += outcome.Weight;
        }
        assert(cursor == pool->Total);
        assert(Warscape::SelectEnemyLoot(entry, cursor) == 0);
    }
    assert(Warscape::EnemyMaximumHit(901243, 99) == 1);
    assert(Warscape::EnemyMaximumHit(901245, 99) == 1);
    assert(Warscape::FindEnemyVariant(901236)->MeleeLane == 2);
    assert(Warscape::FindEnemyVariant(901237)->MeleeLane == 0);
    Warscape::MonsterProfile zeroCaster;
    zeroCaster.Base = {40,75,40,0,0,90}; zeroCaster.Growth.fill(0);
    auto const zeroStats = zeroCaster.Scale(1);
    assert(zeroStats[Warscape::Ranged] == 0 && zeroStats[Warscape::Magic] == 0);
    assert(zeroCaster.Scale(100) == zeroStats);
    Warscape::MonsterDefinition inherited;
    assert(inherited.Calculate(zeroCaster,1) == zeroStats);
    Warscape::MonsterProfile defaultStats;
    assert(defaultStats.Scale(1)[Warscape::Ranged] == 1);
    assert(defaultStats.Scale(1)[Warscape::Hitpoints] == 10);
    zeroCaster.Base[Warscape::Hitpoints] = 0;
    assert(zeroCaster.Scale(1)[Warscape::Hitpoints] == 1);
    for (std::uint32_t entry = 901300; entry <= 901356; ++entry) {
        auto const* pool = Warscape::FindEnemyLootPool(entry);
        assert(pool && Warscape::FindEnemyVariant(entry)->SourceCombat);
        std::uint32_t cursor = 0;
        for (std::uint32_t i = 0; i < pool->Count; ++i) {
            auto const& o = Warscape::EnemyLootOutcomes[pool->First+i];
            assert(Warscape::SelectEnemyLoot(entry,cursor) == o.Loot);
            assert(Warscape::SelectEnemyLoot(entry,cursor+o.Weight-1) == o.Loot);
            cursor += o.Weight;
        }
        assert(cursor == pool->Total);
    }

    for (std::uint32_t entry = 901400; entry <= 901469; ++entry) {
        auto const* pool = Warscape::FindEnemyLootPool(entry);
        assert(pool && Warscape::FindEnemyVariant(entry)->SourceCombat);
        std::uint64_t cursor = 0;
        for (std::uint32_t i = 0; i < pool->Count; ++i) {
            auto const& o = Warscape::EnemyLootOutcomes[pool->First+i];
            assert(Warscape::SelectEnemyLoot(entry,cursor) == o.Loot);
            assert(Warscape::SelectEnemyLoot(entry,cursor+o.Weight-1) == o.Loot);
            cursor += o.Weight;
        }
        assert(cursor == pool->Total);
        assert(Warscape::SelectEnemyLoot(entry,cursor) == 0);
    }
    assert(Warscape::EnemyDefenceLevel(901416,99,1) == 29);
    assert(Warscape::EnemyDefenceLevel(901416,1,99) == 69);
    assert(Warscape::EnemyDefenceLevel(901300,99,1) == 99);
    assert(Warscape::EnemyDefenceLevel(0,99,1) == 99);
    assert(Warscape::FindEnemyVariant(901409)->RequiredSlayerLevel == 85);
    std::array<std::uint32_t,4> draws = {0,0,0xFFFFFFFF,0xFFFFFFFF};
    std::size_t drawIndex = 0;
    // Reject the incomplete bottom range before applying modulo.
    assert(Warscape::DrawEnemyLootRoll(10,[&] {return draws.at(drawIndex++);}) == 5);
    assert(drawIndex == 4);
    assert(Warscape::DrawEnemyLootRoll(0,[] {assert(false);return 0u;}) == 0);
    auto const largeTotal = Warscape::FindEnemyLootPool(901409)->Total;
    assert(largeTotal > 0xFFFFFFFFULL);
    assert(Warscape::DrawEnemyLootRoll(largeTotal,[] {return 0xFFFFFFFFu;}) == 0xFFFFFFFFFFFFFFFFULL%largeTotal);

    for (auto const& v : Warscape::EnemyVariants)
        if (v.Entry < 901500) assert(v.FlatArmour == 0);
    assert(Warscape::EnemyFlatArmour(901500) == -2);
    assert(Warscape::EnemyFlatArmour(901501) == -3);
    assert(Warscape::EnemyFlatArmour(0) == 0);
    // Successful zeroes gain negative armour; misses/evades never do.
    assert(Warscape::ApplyFlatArmour(0,-2,true) == 2);
    assert(Warscape::ApplyFlatArmour(10,-3,true) == 13);
    assert(Warscape::ApplyFlatArmour(10,-3,false) == 0);
    assert(Warscape::ApplyFlatArmour(0,-3,false) == 0);
    assert(Warscape::ApplyFlatArmour(10,4,true) == 6);
    assert(Warscape::ApplyFlatArmour(2,4,true) == 0);
    assert(Warscape::ApplyFlatArmour(10,0,true) == 10);
    assert(Warscape::ApplyFlatArmour(0xFFFFFFFFu,-2147483647,true) == 0xFFFFFFFFu);
    assert(Warscape::ApplyFlatArmour(0,2147483647,true) == 0);
    // Damage and XP use the adjusted OSRS roll, still capped by remaining health.
    auto const adjusted = Warscape::ApplyFlatArmour(5,Warscape::EnemyFlatArmour(901500),true);
    assert(Warscape::ScaleHealthOrDamage(adjusted) == 70);
    assert(Warscape::OSRSDamageForXP(adjusted,45) == 5);
    for (std::uint32_t entry : {901500u,901501u}) {
        auto const* pool = Warscape::FindEnemyLootPool(entry);
        assert(pool && Warscape::FindEnemyVariant(entry)->SourceCombat);
        std::uint64_t cursor = 0;
        for (std::uint32_t i=0; i<pool->Count; ++i) {
            auto const& o = Warscape::EnemyLootOutcomes[pool->First+i];
            assert(Warscape::SelectEnemyLoot(entry,cursor) == o.Loot);
            assert(Warscape::SelectEnemyLoot(entry,cursor+o.Weight-1) == o.Loot);
            cursor += o.Weight;
        }
        assert(cursor == pool->Total && Warscape::SelectEnemyLoot(entry,cursor) == 0);
    }

    assert(Warscape::NonFinishingDamage(400,999) == 390);
    assert(Warscape::NonFinishingDamage(10,999) == 0);
    assert(Warscape::NonFinishingDamage(5,999) == 0);
    assert(Warscape::NonFinishingDamage(400,20) == 20);
    assert(Warscape::OSRSDamageForXP(10,Warscape::NonFinishingDamage(40,40)) == 3);
    assert(Warscape::OSRSDamageForXP(10,Warscape::NonFinishingDamage(10,10)) == 0);
    assert(Warscape::CanCoolLizard(49) && Warscape::CanCoolLizard(10));
    assert(!Warscape::CanCoolLizard(50) && !Warscape::CanCoolLizard(0));
    assert(Warscape::PoisonDuration(3) == 270000);
    assert(Warscape::PoisonHit(3,18000) == 3);
    assert(Warscape::PoisonHit(3,90000) == 3);
    assert(Warscape::PoisonHit(3,108000) == 2);
    assert(Warscape::PoisonHit(3,198000) == 1);
    assert(Warscape::PoisonHit(3,270000) == 1);
    assert(Warscape::PoisonHit(3,288000) == 0);
    assert(Warscape::MagicDefenceLevel(99,1) == 69);
    assert(Warscape::PlayerMagicDefenceLevel(99,1,0)==77);
    assert(Warscape::PlayerMagicDefenceLevel(99,1,2)==80);
    assert(Warscape::PlayerMagicDefenceLevel(99,1,3)==78);
    assert(Warscape::MonsterAttackIntervalMilliseconds(1) == 600);
    assert(Warscape::AttackIntervalMilliseconds(1) == 2400);
    assert(Warscape::FindEnemyBehaviour(901600)->FinisherItem == 902361);
    assert(!Warscape::FindEnemyBehaviour(901100));
    for (std::uint32_t entry=901600; entry<=901605; ++entry) {
        auto const* p=Warscape::FindEnemyLootPool(entry);
        assert(p);std::uint64_t cursor=0;
        for (std::uint32_t i=0; i<p->Count; ++i) {
            auto const& o=Warscape::EnemyLootOutcomes[p->First+i];
            assert(Warscape::SelectEnemyLoot(entry,cursor)==o.Loot);
            assert(Warscape::SelectEnemyLoot(entry,cursor+o.Weight-1)==o.Loot);
            cursor+=o.Weight;
        }
        assert(cursor==p->Total && Warscape::SelectEnemyLoot(entry,cursor)==0);
    }

    assert(Warscape::FindEnemyVariant(901700)->SourceSlayerXPTenths==1075);
    assert(Warscape::FindEnemyVariant(901705)->SourceSlayerXPTenths==1076);
    assert(Warscape::FindEnemyVariant(901100)->SourceSlayerXPTenths==0);
    assert(Warscape::RejectAirborneMelee(true,true,false));
    assert(Warscape::RejectAirborneMelee(true,false,true));
    assert(!Warscape::RejectAirborneMelee(true,false,false));
    assert(!Warscape::RejectAirborneMelee(false,true,true));
    assert(Warscape::PlayerRangedDefenceLevel(50,0)==58);
    assert(Warscape::PlayerRangedDefenceLevel(50,2)==61);
    assert(Warscape::PlayerRangedDefenceLevel(50,3)==59);
    assert(!Warscape::MagicRangeAllowed(true,false,true,true));
    assert(Warscape::MagicRangeAllowed(true,true,true,true));
    assert(Warscape::MagicRangeAllowed(false,false,true,true));
    assert(!Warscape::MagicRangeAllowed(false,true,false,true));
    for (std::uint32_t entry=901700; entry<=901705; ++entry) {
        auto const* pool=Warscape::FindEnemyLootPool(entry);assert(pool);
        std::uint64_t cursor=0;
        for (std::uint32_t i=0; i<pool->Count; ++i) {
            auto const& o=Warscape::EnemyLootOutcomes[pool->First+i];
            assert(Warscape::SelectEnemyLoot(entry,cursor)==o.Loot);
            assert(Warscape::SelectEnemyLoot(entry,cursor+o.Weight-1)==o.Loot);
            cursor+=o.Weight;
        }
        assert(cursor==pool->Total && Warscape::SelectEnemyLoot(entry,cursor)==0);
    }
}
