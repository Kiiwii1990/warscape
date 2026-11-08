#ifndef WARSCAPE_ENEMY_REQUIREMENTS_H
#define WARSCAPE_ENEMY_REQUIREMENTS_H
#include <array>
#include <cstdint>
namespace Warscape {
struct EnemyOffhandRequirement { std::uint32_t Entry, Item; char const* Message; };
inline constexpr std::array<EnemyOffhandRequirement,1> EnemyOffhandRequirements = {{{902301,902586,"You must equip a lit bug lantern in your off-hand to harm this swarm."}}};
inline EnemyOffhandRequirement const* FindEnemyOffhandRequirement(std::uint32_t entry) {
    for (auto const& rule : EnemyOffhandRequirements) if (rule.Entry==entry) return &rule;
    return nullptr;
}
inline bool MeetsEnemyOffhandRequirement(std::uint32_t entry, std::uint32_t offhand) {
    auto const* rule=FindEnemyOffhandRequirement(entry);
    return !rule || offhand==rule->Item;
}
}
#endif
