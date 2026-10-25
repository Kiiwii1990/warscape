/*
 * This file is part of the TrinityCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 */

#ifndef WARSCAPE_EQUIPMENT_H
#define WARSCAPE_EQUIPMENT_H

#include <algorithm>
#include <cstdint>
#include <limits>
#include <vector>

namespace Warscape
{
    enum class WeaponArchetype : uint8_t
    {
        Auto = 0,
        Dagger = 1,
        Scimitar = 2,
        ShortSword = 3,
        Longsword = 4,
        TwoHandedSword = 5,
        Battleaxe = 6,
        Warhammer = 7,
        Mace = 8,
        Spear = 9,
        Halberd = 10,
        Bow = 11,
        Crossbow = 12,
        Staff = 13,
        Wand = 14,
        Unknown = 255
    };

    enum class MeleeDamageType : uint8_t { Stab = 0, Slash = 1, Crush = 2 };
    enum class AttackBonusType : uint8_t { Stab = 0, Slash = 1, Crush = 2, Ranged = 3, Magic = 4 };
    constexpr uint32_t CombatTickMilliseconds = 600;
    constexpr uint32_t DefaultAttackSpeedTicks = 4;
    constexpr uint32_t MinimumAttackSpeedTicks = 2;
    constexpr uint32_t MaximumAttackSpeedTicks = 12;

    inline uint32_t NormalizeAttackSpeedTicks(uint32_t ticks)
    {
        return ticks >= MinimumAttackSpeedTicks && ticks <= MaximumAttackSpeedTicks ? ticks : DefaultAttackSpeedTicks;
    }

    inline uint32_t AttackIntervalMilliseconds(uint32_t ticks)
    {
        return NormalizeAttackSpeedTicks(ticks) * CombatTickMilliseconds;
    }

    inline uint32_t AttackTimerAfterReset(uint32_t ticks)
    {
        return AttackIntervalMilliseconds(ticks);
    }

    inline uint32_t AttackTimerAfterWeaponChange(uint32_t currentTimer, uint32_t newWeaponTicks)
    {
        return std::max(currentTimer, AttackIntervalMilliseconds(newWeaponTicks));
    }

    inline bool AllowsOffhandAutoAttack(bool warscapeMelee)
    {
        return !warscapeMelee;
    }

    struct EquipmentBonuses
    {
        int32_t AttackStab = 0;
        int32_t AttackSlash = 0;
        int32_t AttackCrush = 0;
        int32_t AttackRanged = 0;
        int32_t AttackMagic = 0;
        int32_t DefenceStab = 0;
        int32_t DefenceSlash = 0;
        int32_t DefenceCrush = 0;
        int32_t DefenceRanged = 0;
        int32_t DefenceMagic = 0;
        int32_t MeleeStrength = 0;
        int32_t RangedStrength = 0;
        int32_t MagicDamage = 0;
        int32_t Prayer = 0;

        EquipmentBonuses& operator+=(EquipmentBonuses const& other)
        {
            AttackStab = Add(AttackStab, other.AttackStab);
            AttackSlash = Add(AttackSlash, other.AttackSlash);
            AttackCrush = Add(AttackCrush, other.AttackCrush);
            AttackRanged = Add(AttackRanged, other.AttackRanged);
            AttackMagic = Add(AttackMagic, other.AttackMagic);
            DefenceStab = Add(DefenceStab, other.DefenceStab);
            DefenceSlash = Add(DefenceSlash, other.DefenceSlash);
            DefenceCrush = Add(DefenceCrush, other.DefenceCrush);
            DefenceRanged = Add(DefenceRanged, other.DefenceRanged);
            DefenceMagic = Add(DefenceMagic, other.DefenceMagic);
            MeleeStrength = Add(MeleeStrength, other.MeleeStrength);
            RangedStrength = Add(RangedStrength, other.RangedStrength);
            MagicDamage = Add(MagicDamage, other.MagicDamage);
            Prayer = Add(Prayer, other.Prayer);
            return *this;
        }

        int32_t AttackBonus(MeleeDamageType type) const
        {
            switch (type)
            {
                case MeleeDamageType::Slash: return AttackSlash;
                case MeleeDamageType::Crush: return AttackCrush;
                case MeleeDamageType::Stab:
                default: return AttackStab;
            }
        }

    private:
        static int32_t Add(int32_t left, int32_t right)
        {
            int64_t const sum = int64_t(left) + right;
            return int32_t(std::clamp<int64_t>(sum, std::numeric_limits<int32_t>::min(), std::numeric_limits<int32_t>::max()));
        }
    };

    struct ItemProfile
    {
        WeaponArchetype Archetype = WeaponArchetype::Auto;
        EquipmentBonuses Bonuses;
        uint32_t Tier = 0;
        uint32_t AttackSpeedTicks = DefaultAttackSpeedTicks;
        uint32_t GenerationVersion = 0;
        uint64_t GenerationSeed = 0;
        bool HasGenerationSeed = false;
    };

    inline EquipmentBonuses SumEquipmentBonuses(std::vector<EquipmentBonuses> const& equipped)
    {
        EquipmentBonuses total;
        for (EquipmentBonuses const& bonuses : equipped)
            total += bonuses;
        return total;
    }

    // WoW sword subclasses do not distinguish OSRS scimitars and short swords.
    // Those distinctions are supplied by explicit item-ID overrides in the DB.
    inline WeaponArchetype InferWeaponArchetype(uint32_t itemClass, uint32_t subClass)
    {
        constexpr uint32_t WeaponClass = 2;
        if (itemClass != WeaponClass)
            return WeaponArchetype::Unknown;

        switch (subClass)
        {
            case 0: return WeaponArchetype::Battleaxe;       // Axe
            case 1: return WeaponArchetype::Battleaxe;       // Two-handed axe
            case 2: return WeaponArchetype::Bow;
            case 4: return WeaponArchetype::Mace;
            case 5: return WeaponArchetype::Warhammer;       // Two-handed mace
            case 6: return WeaponArchetype::Spear;           // Polearm; override halberds
            case 7: return WeaponArchetype::Longsword;        // Override scimitars/short swords
            case 8: return WeaponArchetype::TwoHandedSword;
            case 10: return WeaponArchetype::Staff;
            case 15: return WeaponArchetype::Dagger;
            case 17: return WeaponArchetype::Spear;
            case 18: return WeaponArchetype::Crossbow;
            case 19: return WeaponArchetype::Wand;
            default: return WeaponArchetype::Unknown;
        }
    }

    inline WeaponArchetype ResolveWeaponArchetype(uint32_t itemClass, uint32_t subClass, WeaponArchetype overrideArchetype)
    {
        return overrideArchetype != WeaponArchetype::Auto ? overrideArchetype : InferWeaponArchetype(itemClass, subClass);
    }

    inline MeleeDamageType DefaultMeleeDamageType(WeaponArchetype archetype)
    {
        switch (archetype)
        {
            case WeaponArchetype::Scimitar:
            case WeaponArchetype::Longsword:
            case WeaponArchetype::TwoHandedSword:
            case WeaponArchetype::Battleaxe:
            case WeaponArchetype::Halberd:
                return MeleeDamageType::Slash;
            case WeaponArchetype::Warhammer:
            case WeaponArchetype::Mace:
                return MeleeDamageType::Crush;
            case WeaponArchetype::Dagger:
            case WeaponArchetype::ShortSword:
            case WeaponArchetype::Spear:
            default:
                return MeleeDamageType::Stab;
        }
    }

    // The four current style buttons do not encode an attack type in WoW.
    // Accurate/Controlled follow the archetype default; Aggressive asks for
    // slash (or a natural crush/stab fallback); Defensive prefers stab except
    // for blunt weapons. This stays deterministic and only selects a bonus lane.
    inline MeleeDamageType SelectMeleeDamageType(WeaponArchetype archetype, uint32_t style)
    {
        MeleeDamageType const natural = DefaultMeleeDamageType(archetype);
        if (style == 1)
            return natural == MeleeDamageType::Crush ? natural : (natural == MeleeDamageType::Stab ? natural : MeleeDamageType::Slash);
        if (style == 2)
            return natural == MeleeDamageType::Crush ? natural : MeleeDamageType::Stab;
        return natural;
    }
}

#endif
