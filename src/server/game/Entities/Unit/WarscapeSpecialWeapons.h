#ifndef WARSCAPE_SPECIAL_WEAPONS_H
#define WARSCAPE_SPECIAL_WEAPONS_H
#include <cstdint>
#include <limits>
namespace Warscape {
constexpr std::uint32_t BrineSabre = 902589;
constexpr std::uint32_t LeafBladedSword = 902590;
constexpr std::uint32_t LeafBladedSpear = 902591;
constexpr std::uint32_t LeafBladedBattleaxe = 902607;
inline bool CanUseSpecialWeapon(std::uint32_t item, std::uint32_t attackLevel) {
    if (item==BrineSabre) return attackLevel>=40;
    if (item==LeafBladedBattleaxe) return attackLevel>=65;
    if (item==LeafBladedSword || item==LeafBladedSpear) return attackLevel>=50;
    return true;
}
inline bool IsLeafyCreature(std::uint32_t entry) { return entry==902304 || (entry>=902404 && entry<=902407); }
inline bool CanDamageLeafyCreature(std::uint32_t entry, std::uint32_t mainhand, std::uint32_t offhandWeapon,
    std::uint32_t attackLevel, bool directPlayerMelee, bool usable) {
    bool const validHands=((mainhand==LeafBladedSword || mainhand==LeafBladedBattleaxe) && (!offhandWeapon || offhandWeapon==LeafBladedSword))
        || (mainhand==LeafBladedSpear && !offhandWeapon);
    return !IsLeafyCreature(entry) || (validHands && CanUseSpecialWeapon(mainhand,attackLevel) && directPlayerMelee && usable);
}
inline std::uint32_t LeafWeaponMaximumHit(std::uint32_t target, std::uint32_t mainhand, std::uint32_t offhandWeapon,
    std::uint32_t attackLevel, bool directMainhandMelee, bool usable, std::uint32_t maximum) {
    if (mainhand!=LeafBladedBattleaxe || !IsLeafyCreature(target)
        || !CanDamageLeafyCreature(target,mainhand,offhandWeapon,attackLevel,directMainhandMelee,usable)) return maximum;
    // Source passive modifies the OSRS maximum BEFORE the uniform damage roll.
    std::uint64_t const boosted=std::uint64_t(maximum)*47/40;
    constexpr auto limit=(std::numeric_limits<std::uint32_t>::max)();
    return boosted>limit ? limit : static_cast<std::uint32_t>(boosted);
}
inline bool CanBypassRockslugSalt(std::uint32_t target, std::uint32_t mainhand, std::uint32_t attackLevel, bool directPlayerMelee, bool usable) {
    return target==902401 && mainhand==BrineSabre && attackLevel>=40 && directPlayerMelee && usable;
}
}
#endif
