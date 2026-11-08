#ifndef WARSCAPE_ENEMY_REQUIREMENTS_H
#define WARSCAPE_ENEMY_REQUIREMENTS_H
#include <array>
#include <cstdint>
namespace Warscape {
enum class EnemyEquipmentSlot { Head, Offhand };
struct EnemyEquipmentRequirement { std::uint32_t Entry, Item; EnemyEquipmentSlot Slot; char const* Message; };
inline constexpr std::array<EnemyEquipmentRequirement,2> EnemyEquipmentRequirements = {{
    {902301,902586,EnemyEquipmentSlot::Offhand,"You must equip a lit bug lantern in your off-hand to harm this swarm."},
    {902402,902587,EnemyEquipmentSlot::Head,"You must wear a facemask to harm this Smoke Devil."}
}};
inline EnemyEquipmentRequirement const* FindEnemyEquipmentRequirement(std::uint32_t entry) {
    for (auto const& rule : EnemyEquipmentRequirements) if (rule.Entry==entry) return &rule;
    return nullptr;
}
inline bool MeetsEnemyEquipmentRequirement(std::uint32_t entry, std::uint32_t head, std::uint32_t offhand) {
    auto const* rule=FindEnemyEquipmentRequirement(entry);
    return !rule || (rule->Slot==EnemyEquipmentSlot::Head ? head : offhand)==rule->Item;
}
struct EnemyProjectileProtection { std::uint32_t Entry, Spell, HeadItem, Minimum, Maximum; };
inline constexpr std::array<EnemyProjectileProtection,1> EnemyProjectileProtections = {{{902403,900771,902588,20,30}}};
inline EnemyProjectileProtection const* FindUnprotectedProjectile(std::uint32_t entry, std::uint32_t spell, std::uint32_t head) {
    for (auto const& rule : EnemyProjectileProtections)
        if (rule.Entry==entry && rule.Spell==spell && head!=rule.HeadItem) return &rule;
    return nullptr;
}
struct EnemyRangedMeleeProtection { std::uint32_t Entry, Spell, HeadItem, ProtectedMaximum, UnprotectedHit; };
inline constexpr std::array<EnemyRangedMeleeProtection,2> EnemyRangedMeleeProtections = {{
    {902204,900790,902587,8,16}, {902205,900790,902587,10,16}
}};
inline EnemyRangedMeleeProtection const* FindEnemyRangedMeleeProtection(std::uint32_t entry) {
    for (auto const& rule : EnemyRangedMeleeProtections) if (rule.Entry==entry) return &rule;
    return nullptr;
}
inline bool HasRangedMeleeProtection(EnemyRangedMeleeProtection const& rule, std::uint32_t head) { return head==rule.HeadItem; }
}
#endif
