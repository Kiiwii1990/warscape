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

#include <catch2/catch.hpp>
#include <algorithm>
#include <limits>
#include <random>
#include "WarscapeCombat.h"
#include "WarscapeEquipment.h"
#include "WarscapeSkills.h"

TEST_CASE("Warscape monster families scale independently", "[warscape]")
{
    Warscape::MonsterProfile goblin;
    goblin.Growth[Warscape::Defence] = 60;
    Warscape::MonsterProfile golem;
    golem.Base[Warscape::Defence] = 10;
    golem.Growth[Warscape::Defence] = 150;
    CHECK(goblin.Scale(50)[Warscape::Defence] == 30);
    CHECK(golem.Scale(50)[Warscape::Defence] == 83);
    CHECK(golem.Scale(1)[Warscape::Defence] == 10);
    CHECK(golem.Scale(0) == golem.Scale(1));
    golem.Growth[Warscape::Hitpoints] = 0;
    CHECK(golem.Scale(99)[Warscape::Hitpoints] == 10);
    CHECK(golem.Scale(0xFFFFFFFFu)[Warscape::Defence] == Warscape::MaxStat);
}

TEST_CASE("Warscape accuracy handles equality, bonuses and extreme rolls", "[warscape]")
{
    CHECK(Warscape::HitChance(0, 0) == 0.0);
    CHECK(Warscape::HitChance(0, 100) == 0.0);
    CHECK(Warscape::HitChance(100, 100) == 100.0 / 202.0);
    CHECK(Warscape::HitChance(200, 100) == 1.0 - 102.0 / 402.0);
    CHECK(Warscape::CombatRoll(10, -64) == 0);
    CHECK(Warscape::CombatRoll(10, -100) == 0);
    CHECK(Warscape::CombatRoll(10, 20) == 840);
    CHECK(Warscape::CombatRoll(1000008, 1000000) > 0xFFFFFFFFull);
    CHECK(Warscape::HitChance(12 * 64, 9 * 64) > Warscape::HitChance(9 * 64, 9 * 64));
    CHECK(Warscape::HitChance(10 * 64, 9 * 64) > Warscape::HitChance(9 * 64, 9 * 64));
}
TEST_CASE("Warscape creature overrides inherit other stats", "[warscape]")
{
    Warscape::MonsterProfile profile;
    Warscape::MonsterDefinition boss;
    CHECK(boss.Calculate(profile, 50) == profile.Scale(50));
    boss.Overrides[Warscape::Defence] = 200;
    boss.Overrides[Warscape::Hitpoints] = 500;
    auto stats = boss.Calculate(profile, 50);
    CHECK(stats[Warscape::Defence] == 200);
    CHECK(stats[Warscape::Hitpoints] == 500);
    CHECK(stats[Warscape::Attack] == 50);
    CHECK(boss.Calculate(profile, 1)[Warscape::Defence] == 200);
}

TEST_CASE("Warscape accuracy responds to skills, styles and family defence", "[warscape]")
{
    for (unsigned level = 1; level <= 99; ++level)
    {
        auto chance = [&](unsigned bonus, unsigned defence) {
            return Warscape::HitChance(Warscape::CombatRoll(level + bonus + 8, 0), Warscape::CombatRoll(defence + 8, 0));
        };
        CHECK(chance(3, 30) > chance(1, 30));
        CHECK(chance(1, 30) > chance(0, 30));
        CHECK(chance(0, 30) > chance(0, 83));
        for (unsigned defence = 1; defence <= 100; ++defence)
        {
            CHECK(chance(0, defence) >= 0.0);
            CHECK(chance(0, defence) <= 1.0);
        }
    }
}

TEST_CASE("Warscape temporary damage uses OSRS Strength and ignores WoW levels", "[warscape]")
{
    CHECK(Warscape::MaxHit(1, 0) == 1);
    CHECK(Warscape::MaxHit(1, 0, 3) == 1);
    CHECK(Warscape::MaxHit(10, 0) == 2);
    CHECK(Warscape::MaxHit(20, 0) == 3);
    CHECK(Warscape::MaxHit(20, 0, 3) == 3);
    CHECK(Warscape::MaxHit(20, 40) > Warscape::MaxHit(20, 0));

    Warscape::MonsterProfile golem;
    golem.Base[Warscape::Attack] = 8;
    golem.Base[Warscape::Strength] = 8;
    golem.Base[Warscape::Defence] = 10;
    golem.Base[Warscape::Hitpoints] = 10;
    Warscape::MonsterDefinition definition;
    auto const combatStats = definition.Calculate(golem, 1);
    CHECK(combatStats[Warscape::Defence] == 10);
    CHECK(combatStats[Warscape::Hitpoints] == 10);
    CHECK(definition.Calculate(golem, 1) == combatStats);
}

TEST_CASE("Warscape OSRS XP thresholds and level changes are exact", "[warscape]")
{
    CHECK(Warscape::XPForLevel(2) == 83);
    CHECK(Warscape::XPForLevel(3) == 174);
    CHECK(Warscape::XPForLevel(4) == 276);
    CHECK(Warscape::XPForLevel(5) == 388);
    CHECK(Warscape::XPForLevel(99) == 13034431);

    CHECK(Warscape::LevelForXP(82) == 1);
    CHECK(Warscape::LevelForXP(83) == 2);
    CHECK(Warscape::LevelForXP(173) == 2);
    CHECK(Warscape::LevelForXP(174) == 3);
    CHECK(Warscape::LevelForXP(275) == 3);
    CHECK(Warscape::LevelForXP(276) == 4);
    CHECK(Warscape::LevelForXP(387) == 4);
    CHECK(Warscape::LevelForXP(388) == 5);

    Warscape::SkillProgress attack;
    CHECK_FALSE(Warscape::AddSkillXP(attack, 82));
    CHECK(attack.Level == 1);
    CHECK(Warscape::AddSkillXP(attack, 1));
    CHECK(attack.Level == 2);
    CHECK(Warscape::AddSkillXP(attack, 305));
    CHECK(attack.XP == 388);
    CHECK(attack.Level == 5);
}

TEST_CASE("Warscape Attack Strength and Defence XP remain independent of legacy combat skills", "[warscape]")
{
    Warscape::SkillProgress attack;
    Warscape::SkillProgress strength;
    Warscape::SkillProgress defence;

    CHECK_FALSE(Warscape::AddSkillXP(attack, 82));
    CHECK(Warscape::AddSkillXP(attack, 1));
    CHECK(attack.Level == 2);
    CHECK(attack.XP == 83);

    CHECK(Warscape::AddSkillXP(strength, 388));
    CHECK(strength.Level == 5);
    CHECK(strength.XP == 388);

    CHECK(Warscape::AddSkillXP(defence, 174));
    CHECK(defence.Level == 3);
    CHECK(defence.XP == 174);
}

TEST_CASE("Warscape skill XP persistence restores levels from saved XP", "[warscape]")
{
    std::array<Warscape::SkillProgress, Warscape::SkillCount> skills = {};
    skills[0].XP = 388;
    skills[0].Level = 5;
    skills[1].XP = 174;
    skills[1].Level = 3;
    skills[3].XP = 1154;
    skills[3].Level = 10;

    auto const savedXP = Warscape::SerializeSkillXP(skills);
    std::array<Warscape::SkillProgress, Warscape::SkillCount> restored = {};
    Warscape::RestoreSkillXP(restored, savedXP);

    CHECK(restored[0].XP == 388);
    CHECK(restored[0].Level == 5);
    CHECK(restored[1].XP == 174);
    CHECK(restored[1].Level == 3);
    CHECK(restored[3].XP == 1154);
    CHECK(restored[3].Level == 10);

    CHECK(Warscape::SetSkillLevel(restored[0], 50, false) == Warscape::SkillUpdateResult::Success);
    auto const gmSavedXP = Warscape::SerializeSkillXP(restored);
    std::array<Warscape::SkillProgress, Warscape::SkillCount> gmRestored = {};
    Warscape::RestoreSkillXP(gmRestored, gmSavedXP);
    CHECK(gmRestored[0].Level == 50);
    CHECK(gmRestored[0].XP == Warscape::XPForLevel(50));
}

TEST_CASE("Warscape accuracy uses increased OSRS Attack and attack style only", "[warscape]")
{
    uint64_t const defenceRoll = Warscape::CombatRoll(9, 0);
    uint64_t const level1AttackRoll = Warscape::PlayerAttackRoll(1, 0);
    uint64_t const level5AttackRoll = Warscape::PlayerAttackRoll(5, 0);

    CHECK(level1AttackRoll == Warscape::CombatRoll(12, 0));
    CHECK(level5AttackRoll == Warscape::CombatRoll(16, 0));
    CHECK(Warscape::HitChance(level5AttackRoll, defenceRoll) > Warscape::HitChance(level1AttackRoll, defenceRoll));
    CHECK(Warscape::PlayerAttackRoll(5, 1) == Warscape::CombatRoll(13, 0));
    CHECK(Warscape::PlayerAttackRoll(5, 2) == Warscape::CombatRoll(13, 0));
    CHECK(Warscape::PlayerAttackRoll(5, 3) == Warscape::CombatRoll(14, 0));
}

TEST_CASE("Warscape weapon archetypes infer WoW categories and allow explicit overrides", "[warscape]")
{
    using Warscape::WeaponArchetype;
    CHECK(Warscape::InferWeaponArchetype(2, 15) == WeaponArchetype::Dagger);
    CHECK(Warscape::InferWeaponArchetype(2, 7) == WeaponArchetype::Longsword);
    CHECK(Warscape::InferWeaponArchetype(2, 8) == WeaponArchetype::TwoHandedSword);
    CHECK(Warscape::InferWeaponArchetype(2, 5) == WeaponArchetype::Warhammer);
    CHECK(Warscape::InferWeaponArchetype(2, 2) == WeaponArchetype::Bow);
    CHECK(Warscape::InferWeaponArchetype(4, 7) == WeaponArchetype::Unknown);
    CHECK(Warscape::ResolveWeaponArchetype(2, 7, WeaponArchetype::Auto) == WeaponArchetype::Longsword);
    CHECK(Warscape::ResolveWeaponArchetype(2, 7, WeaponArchetype::Scimitar) == WeaponArchetype::Scimitar);
    CHECK(Warscape::ResolveWeaponArchetype(2, 7, WeaponArchetype::ShortSword) == WeaponArchetype::ShortSword);
}

TEST_CASE("Warscape equipment bonuses add across slots and recalculate on removal or switching", "[warscape]")
{
    Warscape::EquipmentBonuses dagger;
    dagger.AttackStab = 8;
    dagger.AttackSlash = -2;
    dagger.MeleeStrength = 2;

    Warscape::EquipmentBonuses armour;
    armour.DefenceStab = 5;
    armour.DefenceMagic = -1;
    armour.Prayer = 3;

    std::vector<Warscape::EquipmentBonuses> equipped = { dagger, armour };
    auto total = Warscape::SumEquipmentBonuses(equipped);
    CHECK(total.AttackStab == 8);
    CHECK(total.AttackSlash == -2);
    CHECK(total.DefenceStab == 5);
    CHECK(total.DefenceMagic == -1);
    CHECK(total.MeleeStrength == 2);
    CHECK(total.Prayer == 3);

    equipped.erase(equipped.begin()); // unequip weapon; no cached value can accumulate
    total = Warscape::SumEquipmentBonuses(equipped);
    CHECK(total.AttackStab == 0);
    CHECK(total.MeleeStrength == 0);
    CHECK(total.DefenceStab == 5);

    Warscape::EquipmentBonuses sword;
    sword.AttackSlash = 12;
    sword.MeleeStrength = 9;
    equipped.push_back(sword); // switch weapon
    total = Warscape::SumEquipmentBonuses(equipped);
    CHECK(total.AttackSlash == 12);
    CHECK(total.MeleeStrength == 9);

    CHECK(Warscape::SumEquipmentBonuses({}).AttackStab == 0); // unknown items contribute zero
}

TEST_CASE("Warscape weapon archetypes and styles select distinct melee attack bonuses", "[warscape]")
{
    using Warscape::MeleeDamageType;
    using Warscape::WeaponArchetype;
    CHECK(Warscape::SelectMeleeDamageType(WeaponArchetype::Dagger, 0) == MeleeDamageType::Stab);
    CHECK(Warscape::SelectMeleeDamageType(WeaponArchetype::Scimitar, 0) == MeleeDamageType::Slash);
    CHECK(Warscape::SelectMeleeDamageType(WeaponArchetype::Warhammer, 0) == MeleeDamageType::Crush);
    CHECK(Warscape::SelectMeleeDamageType(WeaponArchetype::Longsword, 2) == MeleeDamageType::Stab);
    CHECK(Warscape::SelectMeleeDamageType(WeaponArchetype::Mace, 1) == MeleeDamageType::Crush);

    Warscape::EquipmentBonuses bonuses;
    bonuses.AttackStab = 5;
    bonuses.AttackSlash = 15;
    bonuses.AttackCrush = 25;
    CHECK(bonuses.AttackBonus(MeleeDamageType::Stab) == 5);
    CHECK(bonuses.AttackBonus(MeleeDamageType::Slash) == 15);
    CHECK(bonuses.AttackBonus(MeleeDamageType::Crush) == 25);
}

TEST_CASE("Warscape equipment bonuses affect OSRS accuracy and melee max hit", "[warscape]")
{
    uint64_t const baselineAttack = Warscape::PlayerAttackRoll(50, 0, 0);
    uint64_t const betterStabAttack = Warscape::PlayerAttackRoll(50, 0, 12);
    uint64_t const worseStabAttack = Warscape::PlayerAttackRoll(50, 0, -12);
    CHECK(betterStabAttack > baselineAttack);
    CHECK(worseStabAttack < baselineAttack);
    CHECK(Warscape::HitChance(betterStabAttack, 1000) > Warscape::HitChance(baselineAttack, 1000));

    uint32_t const baseMaxHit = Warscape::MaxHit(50, 0, 3);
    CHECK(Warscape::MaxHit(50, 10, 3) > baseMaxHit);
    CHECK(Warscape::MaxHit(50, -10, 3) < baseMaxHit);
}

TEST_CASE("Warscape attack speed uses fixed 600ms ticks, defaults and safe limits", "[warscape]")
{
    CHECK(Warscape::CombatTickMilliseconds == 600);
    CHECK(Warscape::AttackIntervalMilliseconds(2) == 1200);
    CHECK(Warscape::AttackIntervalMilliseconds(3) == 1800);
    CHECK(Warscape::AttackIntervalMilliseconds(4) == 2400);
    CHECK(Warscape::AttackIntervalMilliseconds(5) == 3000);
    CHECK(Warscape::AttackIntervalMilliseconds(6) == 3600);
    CHECK(Warscape::AttackIntervalMilliseconds(7) == 4200);
    CHECK(Warscape::AttackIntervalMilliseconds(0) == 2400);
    CHECK(Warscape::AttackIntervalMilliseconds(1) == 2400);
    CHECK(Warscape::AttackIntervalMilliseconds(13) == 2400);
    CHECK(Warscape::DefaultAttackSpeedTicks == 4);

    // These item-ID profiles are permanent definitions; native WoW delay and
    // haste values are not parameters to the Warscape interval calculation.
    CHECK(Warscape::AttackTimerAfterReset(3) == 1800); // Stiletto 2494
    CHECK(Warscape::AttackTimerAfterReset(4) == 2400); // Gladius 2488
    CHECK(Warscape::AttackTimerAfterReset(7) == 4200); // Two-handed Sword 2489
    CHECK(Warscape::AttackTimerAfterReset(5) == 3000); // Wooden Mallet 2493
    CHECK(Warscape::AttackTimerAfterReset(Warscape::DefaultAttackSpeedTicks) == 2400);
}

TEST_CASE("Warscape weapon switching cannot shorten a pending swing and dual wield does not add attacks", "[warscape]")
{
    CHECK(Warscape::AttackTimerAfterWeaponChange(500, 7) == 4200);
    CHECK(Warscape::AttackTimerAfterWeaponChange(4000, 3) == 4000);
    CHECK(Warscape::AttackTimerAfterWeaponChange(0, 4) == 2400);
    CHECK_FALSE(Warscape::AllowsOffhandAutoAttack(true));
    CHECK(Warscape::AllowsOffhandAutoAttack(false));
}

TEST_CASE("Warscape monster attack speeds use explicit ticks or the four-tick default", "[warscape]")
{
    CHECK(Warscape::AttackIntervalMilliseconds(Warscape::DefaultAttackSpeedTicks) == 2400);
    CHECK(Warscape::AttackIntervalMilliseconds(5) == 3000); // Harvest Golem entry 36 test override
    CHECK(Warscape::NormalizeAttackSpeedTicks(0) == Warscape::DefaultAttackSpeedTicks);
    CHECK(Warscape::NormalizeAttackSpeedTicks(255) == Warscape::DefaultAttackSpeedTicks);
}

TEST_CASE("Warscape health and melee damage scale by 100 without scaling zero", "[warscape]")
{
    CHECK(Warscape::ScaleHealthOrDamage(10) == 1000);
    CHECK(Warscape::ScaleHealthOrDamage(11) == 1100);
    CHECK(Warscape::ScaleHealthOrDamage(20) == 2000);
    CHECK(Warscape::ScaleHealthOrDamage(1) == 100);
    CHECK(Warscape::ScaleHealthOrDamage(0) == 0);
    CHECK(Warscape::ToOSRSDamage(200) == 2);
    CHECK(Warscape::ToOSRSDamage(0) == 0);
    CHECK(Warscape::ScaleHealing(1, 1000) == 100);
    CHECK(Warscape::ScaleHealing(20, 1000) == 1000);
    CHECK(Warscape::ScaleHealing(0, 1000) == 0);

    Warscape::MonsterProfile profile;
    Warscape::MonsterDefinition creature;
    creature.Overrides[Warscape::Hitpoints] = 25;
    auto const stats = creature.Calculate(profile, 1);
    CHECK(stats[Warscape::Hitpoints] == 25);
    CHECK(Warscape::ScaleHealthOrDamage(stats[Warscape::Hitpoints]) == 2500);
}

TEST_CASE("Warscape GM skill setters validate permissions, names, levels and XP", "[warscape]")
{
    CHECK_FALSE(Warscape::CanModifySkills(false));
    CHECK(Warscape::CanModifySkills(true));
    CHECK(Warscape::SkillIndexFromName("attack") == 0);
    CHECK(Warscape::SkillIndexFromName("AtTaCk") == 0);
    CHECK(Warscape::SkillIndexFromName("hitpoints") == 3);
    CHECK(Warscape::SkillIndexFromName("invalid") == -1);

    Warscape::SkillProgress attack;
    CHECK(Warscape::SetSkillLevel(attack, 2, false) == Warscape::SkillUpdateResult::Success);
    CHECK(attack.Level == 2);
    CHECK(attack.XP == 83);
    CHECK(Warscape::SetSkillXP(attack, 500, false) == Warscape::SkillUpdateResult::Success);
    CHECK(attack.Level == 5);
    CHECK(attack.XP == 500);
    CHECK(Warscape::SetSkillLevel(attack, 99, false) == Warscape::SkillUpdateResult::Success);
    CHECK(Warscape::SetSkillLevel(attack, 0, false) == Warscape::SkillUpdateResult::InvalidLevel);
    CHECK(Warscape::SetSkillLevel(attack, 100, false) == Warscape::SkillUpdateResult::InvalidLevel);
    CHECK(Warscape::SetSkillXP(attack, Warscape::MaxSkillXP + 1, false) == Warscape::SkillUpdateResult::InvalidXP);

    Warscape::SkillProgress hitpoints;
    CHECK(Warscape::SetSkillLevel(hitpoints, 10, true) == Warscape::SkillUpdateResult::Success);
    CHECK(hitpoints.XP == 1154);
    CHECK(Warscape::SetSkillLevel(hitpoints, 9, true) == Warscape::SkillUpdateResult::InvalidLevel);
    CHECK(Warscape::SetSkillXP(hitpoints, 1153, true) == Warscape::SkillUpdateResult::InvalidXP);
    CHECK(Warscape::SetSkillLevel(hitpoints, 20, true) == Warscape::SkillUpdateResult::Success);
    CHECK(hitpoints.XP == Warscape::XPForLevel(20));
}

TEST_CASE("Warscape damage variation is bounded, symmetric and leaves XP on OSRS rolls", "[warscape]")
{
    CHECK(Warscape::VaryScaledDamage(0, 80) == 0);
    CHECK(Warscape::VaryScaledDamage(0, 120) == 0);
    CHECK(Warscape::VaryScaledDamage(1, 80) == 80);
    CHECK(Warscape::VaryScaledDamage(1, 120) == 120);
    CHECK(Warscape::VaryScaledDamage(1, 1) == 1);
    CHECK(Warscape::VaryScaledDamage(2, 80) == 160);
    CHECK(Warscape::VaryScaledDamage(2, 120) == 240);
    CHECK(Warscape::VaryScaledDamage(5, 80) == 400);
    CHECK(Warscape::VaryScaledDamage(5, 120) == 600);
    CHECK(Warscape::ScaleHealthOrDamage(10) == 1000);

    std::mt19937 random(0x57525343);
    std::uniform_int_distribution<uint32_t> multiplier(80, 120);
    uint64_t total = 0;
    uint32_t minimum = std::numeric_limits<uint32_t>::max();
    uint32_t maximum = 0;
    constexpr uint32_t SampleCount = 1000000;
    for (uint32_t i = 0; i < SampleCount; ++i)
    {
        uint32_t const varied = Warscape::VaryScaledDamage(1, multiplier(random));
        minimum = std::min(minimum, varied);
        maximum = std::max(maximum, varied);
        total += varied;
    }
    CHECK(minimum >= 80);
    CHECK(maximum <= 120);
    CHECK(total / double(SampleCount) == Approx(100.0).epsilon(0.001));

    // XP uses the unvaried OSRS hit roll, so low and high display rolls award alike.
    CHECK(Warscape::OSRSDamageForXP(1, 1000) * 4 == 4);
    CHECK(Warscape::OSRSDamageForXP(1, 117) * 4 == 4);
    CHECK(Warscape::OSRSDamageForXP(5, 117) * 4 == 8);
    CHECK(Warscape::OSRSDamageForXP(5, 0) == 0);
}
