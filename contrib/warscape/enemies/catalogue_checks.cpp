#include "WarscapeEnemyCatalogue.h"
#include "WarscapeCombat.h"
#include "WarscapeEnemyMechanics.h"
#include "WarscapeEquipment.h"
#include <cassert>
#include <map>
#include <string_view>
int main() {
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
    assert(Warscape::EnemyVariants.size()==283);
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
}
