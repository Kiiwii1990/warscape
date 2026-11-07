#ifndef WARSCAPE_ENEMY_MECHANICS_H
#define WARSCAPE_ENEMY_MECHANICS_H
#include <algorithm>
#include <cstdint>
namespace Warscape {
// Keep a full OSRS hitpoint until the required finishing item is used.
inline std::uint32_t NonFinishingDamage(std::uint32_t health, std::uint32_t damage) {
    return std::min(damage,health > 10 ? health-10 : 0);
}
inline bool CanCoolLizard(std::uint32_t health) { return health > 0 && health < 50; }
constexpr std::uint32_t PoisonPeriod = 18000;
inline std::uint32_t PoisonDuration(std::uint32_t initial) { return initial*5*PoisonPeriod; }
inline std::uint32_t PoisonHit(std::uint32_t initial, std::uint32_t elapsed) {
    // The fifth tick still deals the old severity; the sixth drops by one.
    auto const lost = (elapsed ? elapsed-1 : 0)/(5*PoisonPeriod);
    return lost < initial ? initial-lost : 0;
}
inline std::uint32_t MagicDefenceLevel(std::uint32_t magic,std::uint32_t defence) {
    return (7*magic)/10+(3*defence)/10;
}
inline std::uint32_t PlayerMagicDefenceLevel(std::uint32_t magic,std::uint32_t defence,std::uint32_t style) {
    return MagicDefenceLevel(magic,defence)+8+(style==2 ? 3 : style==3 ? 1 : 0);
}
inline std::uint32_t PlayerRangedDefenceLevel(std::uint32_t defence,std::uint32_t style) {
    return defence+8+(style==2 ? 3 : style==3 ? 1 : 0);
}
inline bool RejectAirborneMelee(bool airborne,bool directAuto,bool meleeSpell) {
    return airborne && (directAuto || meleeSpell);
}
inline bool MagicRangeAllowed(bool meleeOnly,bool inMelee,bool inRange,bool lineOfSight) {
    return inRange && lineOfSight && (!meleeOnly || inMelee);
}
}
#endif
