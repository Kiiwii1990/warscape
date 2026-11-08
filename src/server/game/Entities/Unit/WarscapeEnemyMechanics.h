#ifndef WARSCAPE_ENEMY_MECHANICS_H
#define WARSCAPE_ENEMY_MECHANICS_H
#include <algorithm>
#include <cstdint>
namespace Warscape {
// Keep a full OSRS hitpoint until the required finishing item is used.
inline std::uint32_t NonFinishingDamage(std::uint32_t health, std::uint32_t damage) {
    return std::min(damage,health > 10 ? health-10 : 0);
}
inline bool CanSmashGargoyle(std::uint32_t health) { return health > 0 && health <= 80; }
inline bool CanCoolLizard(std::uint32_t health) { return health > 0 && health < 50; }
inline bool CycleUsesMagic(std::uint32_t position) { return position % 6 < 3; }
inline std::uint32_t AdvanceAttackCycle(std::uint32_t position) { return (position+1)%6; }
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
constexpr std::uint32_t ElementalShield = 902379;
constexpr std::uint32_t AntiDragonShield = 902380;
inline std::uint32_t DrakeBreathMaximum(bool protectedByShield) { return protectedByShield ? 4 : 8; }
inline std::uint32_t WyvernBreathMaximum(bool protectedByShield) { return protectedByShield ? 10 : 60; }
inline bool WyvernFreezes(bool protectedByShield, std::uint32_t roll) { return !protectedByShield || roll == 0; }

// One launch after seven normal attacks. Bounded to four pulses even after a lag spike.
struct DrakeBreathSequence
{
    std::uint32_t NormalAttacks = 0, Pulses = 0, Delay = 0;
    bool Ready() const { return NormalAttacks >= 7 && !Pulses; }
    void Launch() { NormalAttacks = 0; Pulses = 4; Delay = 1200; }
    std::uint32_t Advance(std::uint32_t diff)
    {
        std::uint32_t due = 0;
        while (Pulses && diff >= Delay)
        {
            diff -= Delay;
            --Pulses;
            ++due;
            Delay = 600;
        }
        if (Pulses) Delay -= diff;
        return due;
    }
};

constexpr std::uint32_t Earmuffs = 902428;
inline std::uint8_t RevenantStyle(std::uint64_t magicDefence, std::uint64_t rangedDefence,
    std::uint64_t meleeDefence, bool inMelee)
{
    // Magic wins equal defensive rolls; melee is never selected outside reach.
    std::uint8_t style = rangedDefence < magicDefence ? 1 : 0;
    auto const lowest = std::min(magicDefence, rangedDefence);
    return inMelee && meleeDefence < lowest ? 2 : style;
}
struct RevenantRecovery
{
    std::uint32_t Remaining = 0, Cooldown = 0;
    void Advance(std::uint32_t diff) { Cooldown = diff >= Cooldown ? 0 : Cooldown - diff; }
    std::uint32_t TryHeal(std::uint32_t current, std::uint32_t maximum)
    {
        if (!current || !Remaining || Cooldown || std::uint64_t(current)*2 >= maximum) return 0;
        --Remaining;
        Cooldown = 9000;
        return std::min(200u, maximum-current); // Twenty source HP at the existing tenfold scale.
    }
};

constexpr std::uint32_t EncounterStateData = 0x57534501;
constexpr std::uint32_t LureCutState = 1, ReinforcedState = 2;
inline std::int32_t StatefulDefence(std::uint8_t lane, std::int32_t fallback,
    bool cutLure, bool earthen, std::uint32_t state)
{
    if (cutLure && (state & LureCutState) && lane==0) return 10;
    if (earthen && (state & ReinforcedState))
        return lane==0 ? 50 : lane==1 ? 70 : lane==2 ? 10 : fallback;
    return fallback;
}
inline std::uint32_t VenomDamage(std::int32_t scaledAmount) { return std::uint32_t(std::clamp(scaledAmount/10,6,20)); }
inline std::uint32_t NextVenomDamage(std::uint32_t current) { return std::min(current+2,20u); }

}
#endif
