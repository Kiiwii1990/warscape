/*
 * This file is part of the TrinityCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or (at
 * your option) any later version.
 */

#ifndef TRINITY_WARSCAPE_SKILL_STATEMENTS_H
#define TRINITY_WARSCAPE_SKILL_STATEMENTS_H

#include <cstddef>
#include <cstdint>

namespace Warscape::SkillStatements
{
    inline constexpr std::size_t PersistedSkillCount = 10;

    inline constexpr std::uint8_t SelectGuidParameter = 0;
    inline constexpr std::uint8_t SaveGuidParameter = 0;
    inline constexpr std::uint8_t FirstSkillXPParameter = 1;
    inline constexpr std::uint8_t MiningHalfXPParameter = PersistedSkillCount + 1;
    inline constexpr std::uint8_t SmithingTenthXPParameter = PersistedSkillCount + 2;
    inline constexpr std::uint8_t AttackStyleParameter = PersistedSkillCount + 3;
    inline constexpr std::uint8_t SaveParameterCount = PersistedSkillCount + 4;

    inline constexpr char SelectSql[] =
        "SELECT attack_xp, strength_xp, defence_xp, hitpoints_xp, ranged_xp, magic_xp, prayer_xp, mining_xp, smithing_xp, agility_xp, mining_half_xp, smithing_tenth_xp, attack_style FROM warscape_skills WHERE guid = ?";

    inline constexpr char SaveSql[] =
        "INSERT INTO warscape_skills (guid, attack_xp, strength_xp, defence_xp, hitpoints_xp, ranged_xp, magic_xp, prayer_xp, mining_xp, smithing_xp, agility_xp, mining_half_xp, smithing_tenth_xp, attack_style) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON DUPLICATE KEY UPDATE "
        "attack_xp=VALUES(attack_xp), strength_xp=VALUES(strength_xp), defence_xp=VALUES(defence_xp), "
        "hitpoints_xp=VALUES(hitpoints_xp), ranged_xp=VALUES(ranged_xp), magic_xp=VALUES(magic_xp), "
        "prayer_xp=VALUES(prayer_xp), mining_xp=VALUES(mining_xp), smithing_xp=VALUES(smithing_xp), agility_xp=VALUES(agility_xp), mining_half_xp=VALUES(mining_half_xp), smithing_tenth_xp=VALUES(smithing_tenth_xp), attack_style=VALUES(attack_style)";

    constexpr std::size_t CountParameters(char const* sql)
    {
        std::size_t count = 0;
        for (; *sql != '\0'; ++sql)
            if (*sql == '?')
                ++count;
        return count;
    }

    static_assert(CountParameters(SelectSql) == 1);
    static_assert(CountParameters(SaveSql) == SaveParameterCount);
    static_assert(AttackStyleParameter + 1 == SaveParameterCount);
}

#endif
