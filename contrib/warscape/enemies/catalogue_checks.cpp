#include "WarscapeEnemyCatalogue.h"
#include "WarscapeCombat.h"
#include <cassert>
#include <map>
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
}
