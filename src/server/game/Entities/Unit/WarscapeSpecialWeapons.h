#ifndef WARSCAPE_SPECIAL_WEAPONS_H
#define WARSCAPE_SPECIAL_WEAPONS_H
#include <cstdint>
namespace Warscape {
constexpr std::uint32_t BrineSabre = 902589;
inline bool CanUseSpecialWeapon(std::uint32_t item, std::uint32_t attackLevel) { return item!=BrineSabre || attackLevel>=40; }
inline bool CanBypassRockslugSalt(std::uint32_t target, std::uint32_t mainhand, std::uint32_t attackLevel, bool directPlayerMelee, bool usable) {
    return target==902401 && mainhand==BrineSabre && attackLevel>=40 && directPlayerMelee && usable;
}
}
#endif
