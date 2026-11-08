#ifndef WARSCAPE_SPECIAL_WEAPONS_H
#define WARSCAPE_SPECIAL_WEAPONS_H
#include <cstdint>
namespace Warscape {
constexpr std::uint32_t BrineSabre = 902589;
constexpr std::uint32_t LeafBladedSword = 902590;
inline bool CanUseSpecialWeapon(std::uint32_t item, std::uint32_t attackLevel) {
    if (item==BrineSabre) return attackLevel>=40;
    if (item==LeafBladedSword) return attackLevel>=50;
    return true;
}
inline bool IsLeafyCreature(std::uint32_t entry) { return entry==902304 || (entry>=902404 && entry<=902407); }
inline bool CanDamageLeafyCreature(std::uint32_t entry, std::uint32_t mainhand, std::uint32_t offhandWeapon,
    std::uint32_t attackLevel, bool directPlayerMelee, bool usable) {
    return !IsLeafyCreature(entry) || (mainhand==LeafBladedSword && (!offhandWeapon || offhandWeapon==LeafBladedSword)
        && attackLevel>=50 && directPlayerMelee && usable);
}
inline bool CanBypassRockslugSalt(std::uint32_t target, std::uint32_t mainhand, std::uint32_t attackLevel, bool directPlayerMelee, bool usable) {
    return target==902401 && mainhand==BrineSabre && attackLevel>=40 && directPlayerMelee && usable;
}
}
#endif
