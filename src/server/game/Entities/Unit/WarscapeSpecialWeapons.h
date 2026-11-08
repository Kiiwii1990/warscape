#ifndef WARSCAPE_SPECIAL_WEAPONS_H
#define WARSCAPE_SPECIAL_WEAPONS_H
#include <cstdint>
namespace Warscape {
constexpr std::uint32_t BrineSabre = 902589;
constexpr std::uint32_t LeafBladedSword = 902590;
constexpr std::uint32_t LeafBladedSpear = 902591;
inline bool CanUseSpecialWeapon(std::uint32_t item, std::uint32_t attackLevel) {
    if (item==BrineSabre) return attackLevel>=40;
    if (item==LeafBladedSword || item==LeafBladedSpear) return attackLevel>=50;
    return true;
}
inline bool IsLeafyCreature(std::uint32_t entry) { return entry==902304 || (entry>=902404 && entry<=902407); }
inline bool CanDamageLeafyCreature(std::uint32_t entry, std::uint32_t mainhand, std::uint32_t offhandWeapon,
    std::uint32_t attackLevel, bool directPlayerMelee, bool usable) {
    bool const validHands=(mainhand==LeafBladedSword && (!offhandWeapon || offhandWeapon==LeafBladedSword))
        || (mainhand==LeafBladedSpear && !offhandWeapon);
    return !IsLeafyCreature(entry) || (validHands && attackLevel>=50 && directPlayerMelee && usable);
}
inline bool CanBypassRockslugSalt(std::uint32_t target, std::uint32_t mainhand, std::uint32_t attackLevel, bool directPlayerMelee, bool usable) {
    return target==902401 && mainhand==BrineSabre && attackLevel>=40 && directPlayerMelee && usable;
}
}
#endif
