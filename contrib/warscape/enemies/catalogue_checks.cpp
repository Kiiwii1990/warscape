#include "WarscapeEnemyCatalogue.h"
#include "WarscapeCombat.h"
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
        unsigned total=0;
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
    assert(Warscape::EnemyVariants.size()==28);
}
