/*
 * This file is part of the TrinityCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program. If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef WARSCAPE_COMBAT_H
#define WARSCAPE_COMBAT_H

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstddef>

namespace Warscape
{
    enum Stat : std::size_t { Attack, Strength, Defence, Ranged, Magic, Hitpoints, StatCount };
    constexpr std::uint32_t MaxStat = 1000000;
    constexpr std::int32_t MaxBonus = 1000000;

    struct MonsterProfile
    {
        std::array<std::uint32_t, StatCount> Base = { 1, 1, 1, 1, 1, 10 };
        // Hundredths of a skill level gained per creature level after level 1.
        std::array<std::uint32_t, StatCount> Growth = { 100, 100, 100, 100, 100, 100 };
        std::int32_t AttackBonus = 0;
        std::int32_t StrengthBonus = 0;
        std::int32_t DefenceBonus = 0;

        std::array<std::uint32_t, StatCount> Scale(std::uint32_t level) const
        {
            std::array<std::uint32_t, StatCount> result;
            for (std::size_t i = 0; i < StatCount; ++i)
                result[i] = std::uint32_t(std::clamp<std::uint64_t>(
                    Base[i] + std::uint64_t(level > 0 ? level - 1 : 0) * Growth[i] / 100, 1, MaxStat));
            return result;
        }
    };

    struct MonsterDefinition
    {
        std::uint32_t Profile = 0;
        // Zero means inherit the scaled profile; positive values are final skill overrides.
        std::array<std::uint32_t, StatCount> Overrides = {};

        std::array<std::uint32_t, StatCount> Calculate(MonsterProfile const& profile, std::uint32_t level) const
        {
            auto stats = profile.Scale(level);
            for (std::size_t i = 0; i < StatCount; ++i)
                if (Overrides[i])
                    stats[i] = Overrides[i];
            return stats;
        }
    };

    inline std::uint64_t CombatRoll(std::uint32_t effectiveLevel, std::int32_t bonus)
    {
        return std::uint64_t(effectiveLevel) * std::uint64_t(std::max<std::int64_t>(0, std::int64_t(bonus) + 64));
    }

    inline double HitChance(std::uint64_t attack, std::uint64_t defence)
    {
        return attack > defence
            ? 1.0 - (double(defence) + 2.0) / (2.0 * (double(attack) + 1.0))
            : double(attack) / (2.0 * (double(defence) + 1.0));
    }

    // Temporary OSRS melee damage until item bonuses are data-driven. The base
    // bonus is zero; aggressive style contributes its OSRS +3 Strength levels.
    inline std::uint32_t MaxHit(std::uint32_t strengthLevel, std::int32_t strengthBonus, std::uint32_t styleBonus = 0)
    {
        std::uint64_t const effectiveStrength = std::uint64_t(strengthLevel) + styleBonus + 8;
        std::uint64_t const bonus = std::uint64_t(std::max<std::int64_t>(0, std::int64_t(strengthBonus) + 64));
        return std::uint32_t(std::min<std::uint64_t>((effectiveStrength * bonus + 320) / 640, MaxStat));
    }
}
#endif
