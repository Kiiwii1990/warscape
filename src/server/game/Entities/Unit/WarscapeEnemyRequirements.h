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
}
#endif
