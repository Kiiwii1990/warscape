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
#include <array>
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

    // Explicit OSRS material tiers, never inferred from WoW item level/quality.
    constexpr uint32_t DefaultEquipmentTier = 1;
    constexpr uint32_t MaximumEquipmentTier = 6;

    struct WeaponRule
    {
        uint32_t Tier = DefaultEquipmentTier;
        WeaponArchetype Archetype = WeaponArchetype::Auto;
    };

    inline char const* EquipmentTierName(uint32_t tier)
    {
        constexpr char const* Names[] = { "Unspecified", "Bronze", "Iron", "Steel", "Mithril", "Adamant", "Rune" };
        return tier <= MaximumEquipmentTier ? Names[tier] : "Custom";
    }

    inline EquipmentBonuses BaselineWeaponBonuses(WeaponArchetype archetype, uint32_t tier)
    {
        // OSRS Wiki metal equipment tables: stab, slash, crush, melee strength.
        // See doc/WarscapeStage1G.md for sources and the deliberate scope.
        struct Stats { int32_t Stab, Slash, Crush, Strength; };
        constexpr Stats Table[][6] = {
            {}, // Auto is resolved from the WoW subclass before lookup.
            { {4,2,-4,3}, {5,3,-4,4}, {8,4,-4,7}, {11,5,-4,10}, {15,8,-4,14}, {25,12,-4,24} }, // Dagger
            { {1,7,-2,6}, {2,10,-2,9}, {3,15,-2,14}, {5,21,-2,20}, {6,29,-2,28}, {7,45,-2,44} }, // Scimitar
            { {4,3,-2,5}, {6,4,-2,7}, {11,8,-2,12}, {16,11,-2,17}, {23,18,-2,24}, {38,26,-2,39} }, // Short sword
            { {4,5,-2,7}, {6,8,-2,10}, {9,14,-2,16}, {15,20,-2,22}, {20,29,-2,31}, {38,47,-2,49} }, // Longsword
            { {-4,9,8,10}, {-4,13,10,14}, {-4,21,16,22}, {-4,30,24,31}, {-4,43,30,44}, {-4,69,50,70} }, // 2h sword
            { {-2,6,3,9}, {-2,8,5,13}, {-2,16,11,20}, {-2,22,17,29}, {-2,31,26,41}, {-2,48,43,64} }, // Battleaxe
            { {-4,-4,10,8}, {-4,-4,11,11}, {-4,-4,18,18}, {-4,-4,25,27}, {-4,-4,35,39}, {-4,-4,53,62} }, // Warhammer
            { {1,-2,6,5}, {4,-2,9,7}, {7,-2,13,11}, {11,-2,18,16}, {13,-2,25,23}, {20,-2,39,36} }, // Mace
            { {5,5,5,6}, {8,8,8,10}, {12,12,12,12}, {17,17,17,18}, {24,24,24,28}, {36,36,36,42} }, // Spear
            { {7,8,0,8}, {9,12,0,12}, {14,19,0,20}, {22,28,0,29}, {28,41,0,42}, {48,67,0,68} } // Halberd
        };
        EquipmentBonuses bonuses;
        auto const index = static_cast<uint32_t>(archetype);
        if (!index || index >= std::size(Table))
            return bonuses; // No automatic stats for armour, ranged, caster or unknown weapons.
        tier = tier >= DefaultEquipmentTier && tier <= MaximumEquipmentTier ? tier : DefaultEquipmentTier;
        Stats const& stats = Table[index][tier - 1];
        bonuses.AttackStab = stats.Stab;
        bonuses.AttackSlash = stats.Slash;
        bonuses.AttackCrush = stats.Crush;
        bonuses.MeleeStrength = stats.Strength;
        return bonuses;
    }

    inline EquipmentBonuses ResolveEquipmentBonuses(WeaponArchetype archetype, uint32_t tier, EquipmentBonuses const* custom)
    {
        return custom ? *custom : BaselineWeaponBonuses(archetype, tier);
    }

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
