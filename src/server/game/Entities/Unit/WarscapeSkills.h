/*
 * This file is part of the TrinityCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or (at
 * your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program. If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef WARSCAPE_SKILLS_H
#define WARSCAPE_SKILLS_H

#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <cstddef>
#include <cstdint>

namespace Warscape
{
    constexpr std::size_t SkillCount = 7;
    constexpr std::uint32_t MaxSkillXP = 200000000;
    constexpr std::uint8_t MaxSkillLevel = 99;
    constexpr std::uint8_t MinHitpointsLevel = 10;

    enum class SkillUpdateResult : std::uint8_t
    {
        Success,
        InvalidLevel,
        InvalidXP
    };

    struct SkillProgress
    {
        std::uint8_t Level = 1;
        std::uint32_t XP = 0;
    };

    inline int SkillIndexFromName(char const* name)
    {
        static char const* names[SkillCount] = { "attack", "strength", "defence", "hitpoints", "ranged", "magic", "prayer" };
        if (!name)
            return -1;
        for (std::size_t i = 0; i < SkillCount; ++i)
        {
            std::size_t j = 0;
            for (; name[j] && names[i][j]; ++j)
                if (std::tolower(static_cast<unsigned char>(name[j])) != names[i][j])
                    break;
            if (!name[j] && !names[i][j])
                return static_cast<int>(i);
        }
        return -1;
    }

    inline bool CanModifySkills(bool hasPermission)
    {
        return hasPermission;
    }

    inline std::uint32_t XPForLevel(std::uint8_t level)
    {
        if (level <= 1)
            return 0;

        level = std::min(level, MaxSkillLevel);

        std::uint32_t points = 0;
        for (std::uint32_t i = 1; i < level; ++i)
            points += std::uint32_t(std::floor(i + 300.0 * std::pow(2.0, i / 7.0)));

        return points / 4;
    }

    inline std::uint8_t LevelForXP(std::uint32_t xp)
    {
        for (int level = MaxSkillLevel; level >= 2; --level)
            if (xp >= XPForLevel(std::uint8_t(level)))
                return std::uint8_t(level);

        return 1;
    }

    // Returns true only when this XP award increases the skill level.
    inline bool AddSkillXP(SkillProgress& skill, std::uint32_t amount)
    {
        std::uint8_t const previousLevel = skill.Level;
        skill.XP = std::uint32_t(std::min<std::uint64_t>(MaxSkillXP, std::uint64_t(skill.XP) + amount));
        skill.Level = LevelForXP(skill.XP);
        return skill.Level > previousLevel;
    }

    inline SkillUpdateResult SetSkillLevel(SkillProgress& skill, std::uint32_t level, bool hitpoints)
    {
        std::uint32_t const minimumLevel = hitpoints ? MinHitpointsLevel : 1U;
        if (level < minimumLevel || level > MaxSkillLevel)
            return SkillUpdateResult::InvalidLevel;
        skill.Level = static_cast<std::uint8_t>(level);
        skill.XP = XPForLevel(skill.Level);
        return SkillUpdateResult::Success;
    }

    inline SkillUpdateResult SetSkillXP(SkillProgress& skill, std::uint32_t xp, bool hitpoints)
    {
        if (xp > MaxSkillXP || (hitpoints && xp < XPForLevel(MinHitpointsLevel)))
            return SkillUpdateResult::InvalidXP;
        skill.XP = xp;
        skill.Level = LevelForXP(xp);
        return SkillUpdateResult::Success;
    }

    template <std::size_t N>
    inline std::array<std::uint32_t, N> SerializeSkillXP(std::array<SkillProgress, N> const& skills)
    {
        std::array<std::uint32_t, N> savedXP = {};
        for (std::size_t i = 0; i < N; ++i)
            savedXP[i] = skills[i].XP;
        return savedXP;
    }

    template <std::size_t N>
    inline void RestoreSkillXP(std::array<SkillProgress, N>& skills, std::array<std::uint32_t, N> const& savedXP)
    {
        for (std::size_t i = 0; i < N; ++i)
        {
            skills[i].XP = std::min(savedXP[i], MaxSkillXP);
            skills[i].Level = LevelForXP(skills[i].XP);
        }
    }
}

#endif
