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
#include "WarscapeCombat.h"
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
