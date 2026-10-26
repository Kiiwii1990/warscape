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
#include "WarscapeSkillsAddon.h"
#include "WarscapeTrainingDummy.h"
#include "WarscapeAttackTest.h"

TEST_CASE("Warscape skills addon accepts only bounded read-only subscriptions", "[warscape]")
{
    CHECK(Warscape::ParseSkillsSubscription("WCSkills\tHELLO|1|abc123") == "abc123");
    for (char const* invalid : { "WCSkills\tHELLO|2|abc", "WCSkills\tHELLO|1|", "WCSkills\tHELLO|1|abcdefghijklmnopq",
        "WCSkills\tHELLO|1|a|b", "WCSkills\tSET|1|attack|99", "WCSkills\tHELLO|1|a\n" })
        CHECK(Warscape::ParseSkillsSubscription(invalid).empty());
    CHECK(Warscape::IsSkillsAddonMessage("WCSkills\tmalformed"));
    CHECK_FALSE(Warscape::IsSkillsAddonMessage("Other\tHELLO|1|abc"));
    CHECK_FALSE(Warscape::IsSkillsAddonMessage("WCSkillsX\tHELLO|1|abc"));
    CHECK(Warscape::SkillsRow("1|abc|2", "attack", {1, 0}) == "S|1|abc|2|attack|1|-|0|0|83");
    CHECK(Warscape::SkillsRow("1|abc|3", "prayer", {99, 200000000}) == "S|1|abc|3|prayer|99|-|200000000|13034431|-");
    for (auto id : Warscape::SkillIds)
        CHECK(Warscape::SkillsRow("1|abcdefghijklmnop|4294967295", id, {99, 200000000}).size() + 9 <= 255);
}

TEST_CASE("Warscape attack test uses bounded real-time sessions and refuses overlap", "[warscape]")
{
    Warscape::AttackTestSession test;
    Warscape::AttackTestXP xp = {};
    Warscape::AttackTestSetup setup;
    CHECK_FALSE(test.Start(1000, 0, xp, setup));
    CHECK_FALSE(test.Start(1000, 31, xp, setup));
    REQUIRE(test.Start(1000, 1, xp, setup));
    CHECK_FALSE(test.Start(2000, 5, xp, setup));
    CHECK(test.StartMs == 1000);
    CHECK(test.DeadlineMs == 61000);
    CHECK(test.RemainingMs(2000) == 59000);
    CHECK_FALSE(test.Expired(60999));
    CHECK(test.Expired(61000));
    CHECK(test.RecordSwing(60999, true, 10));
    CHECK_FALSE(test.RecordSwing(61000, true, 10));
    REQUIRE(test.Finish(61025, xp));
    CHECK(test.ElapsedMs() == 60025);
    CHECK(test.DPS() == Approx(10.0 / 60.025));
    CHECK_FALSE(test.RecordSwing(62000, true, 100));
    CHECK_FALSE(test.Finish(62000, xp));
    REQUIRE(test.Start(0xFFFFFFF0ULL, 30, xp, setup));
    CHECK(test.DeadlineMs == 0xFFFFFFF0ULL + 1800000);
}

TEST_CASE("Warscape attack test counts real zero hits, misses, damage and intervals", "[warscape]")
{
    Warscape::AttackTestSession test;
    Warscape::AttackTestXP xp = { 1, 2, 3, 4, 5, 6, 7 };
    REQUIRE(test.Start(1000, 5, xp, {}));
    REQUIRE(test.RecordSwing(1000, true, 0));
    REQUIRE(test.RecordSwing(3400, false, 0));
    REQUIRE(test.RecordSwing(5800, true, 20));
    CHECK_FALSE(test.RecordSwing(5700, true, 200));
    REQUIRE(test.Finish(7000, xp));
    CHECK(test.Timestamps == std::vector<std::uint64_t>{1000, 3400, 5800});
    CHECK(test.Hits == 2);
    CHECK(test.ZeroHits == 1);
    CHECK(test.Misses == 1);
    CHECK(test.Accuracy() == Approx(200.0 / 3));
    CHECK(test.TotalDamage == 20);
    CHECK(test.AverageHit() == 10);
    CHECK(test.MinHit == 0);
    CHECK(test.MaxHit == 20);
    CHECK(test.AverageIntervalSeconds() == Approx(2.4));
    CHECK(test.DPS() == Approx(20.0 / 6));
    CHECK(test.ChangedSkills == 0);
    CHECK(test.TotalXPDelta == 0);
    CHECK(test.StartXP == xp); // Collecting damage never awards or rewrites XP.
}

TEST_CASE("Warscape attack test measures interruption time without fabricating swings", "[warscape]")
{
    Warscape::AttackTestSession test;
    REQUIRE(test.Start(0, 1, {}, {}));
    test.ObservePause(0, 0);
    REQUIRE(test.RecordSwing(1000, true, 10));
    test.ObservePause(2000, Warscape::AttackTestRange);
    test.ObservePause(5000, Warscape::AttackTestFacing);
    test.ObservePause(8000, 0);
    REQUIRE(test.RecordSwing(10000, true, 10));
    REQUIRE(test.Finish(12000, {}));
    CHECK(test.Timestamps.size() == 2);
    CHECK(test.PauseCount == 1);
    CHECK(test.PausedMs == 6000);
    CHECK(test.PauseReasons == (Warscape::AttackTestRange | Warscape::AttackTestFacing));
    CHECK(test.AverageIntervalSeconds() == Approx(9.0));
    CHECK(test.DPS() == Approx(20.0 / 12));
}

TEST_CASE("Warscape attack test cancellation discards samples and permits a fresh session", "[warscape]")
{
    Warscape::AttackTestSession test;
    REQUIRE(test.Start(1000, 1, {}, {}));
    REQUIRE(test.RecordSwing(1000, true, 100));
    test.ObservePause(1500, Warscape::AttackTestAutoStopped);
    test.Cancel();
    CHECK_FALSE(test.Active);
    CHECK(test.Timestamps.empty());
    CHECK(test.TotalDamage == 0);
    CHECK(test.PauseCount == 0);
    CHECK(test.RemainingMs(2000) == 0);
    CHECK_FALSE(test.RecordSwing(2000, true, 100));
    CHECK_FALSE(test.Finish(2000, {}));
    REQUIRE(test.Start(3000, 1, {}, {}));
    REQUIRE(test.Finish(3000, {}));
    CHECK(test.DPS() == 0);
    CHECK(test.Accuracy() == 0);
    CHECK(test.ChangedSkills == 0);
}

TEST_CASE("Warscape attack test checks every combat skill and detects offsetting XP changes", "[warscape]")
{
    Warscape::AttackTestXP initial = {100,100,100,100,100,100,100};
    for (std::size_t skill = 0; skill < initial.size(); ++skill)
    {
        Warscape::AttackTestSession test;
        REQUIRE(test.Start(0, 1, initial, {}));
        REQUIRE(test.RecordSwing(100, true, 100));
        REQUIRE(test.RecordSwing(2500, false, 0));
        REQUIRE(test.RecordSwing(4900, true, 0));
        auto end = initial;
        ++end[skill];
        REQUIRE(test.Finish(5000, end));
        CHECK(test.ChangedSkills == 1);
        CHECK(test.XPDelta[skill] == 1);
    }
    Warscape::AttackTestSession test;
    REQUIRE(test.Start(0, 1, initial, {}));
    auto end = initial;
    ++end[0]; --end[6];
    REQUIRE(test.Finish(5000, end));
    CHECK(test.TotalXPDelta == 0);
    CHECK(test.ChangedSkills == 2);
}

TEST_CASE("Warscape attack test labels mixed setups and bounds timestamp storage", "[warscape]")
{
    Warscape::AttackTestSession test;
    Warscape::AttackTestSetup initial;
    initial.Weapon = 2488;
    REQUIRE(test.Start(0, 30, {}, initial));
    auto changed = initial;
    changed.Weapon = 2489;
    changed.Style = 1;
    changed.Defence = 50;
    changed.IntervalMs = 4200;
    test.ObserveSetup(changed);
    test.ObserveSetup(initial);
    CHECK(test.MixedSetup);
    CHECK(test.WeaponChanged);
    CHECK(test.StyleChanged);
    CHECK(test.DefenceChanged);
    CHECK(test.MinExpectedMs == 2400);
    CHECK(test.MaxExpectedMs == 4200);
    for (std::size_t i = 0; i < Warscape::AttackTestSession::MaximumSamples; ++i)
        REQUIRE(test.RecordSwing(i, true, 0));
    CHECK_FALSE(test.RecordSwing(Warscape::AttackTestSession::MaximumSamples, true, 10));
    CHECK(test.TotalDamage == 0);
    CHECK(test.Timestamps.size() == Warscape::AttackTestSession::MaximumSamples);
}

TEST_CASE("Warscape training utility is scoped to its reserved entry and bounded Defence", "[warscape]")
{
    CHECK(Warscape::IsTrainingDummyEntry(900001));
    for (uint32_t entry : {0u, 36u, 480u, 31144u, 900000u, 900002u, std::numeric_limits<uint32_t>::max()})
        CHECK_FALSE(Warscape::IsTrainingDummyEntry(entry));
    CHECK(Warscape::NormalizeTrainingDefence(0) == 1);
    CHECK(Warscape::NormalizeTrainingDefence(1) == 1);
    CHECK(Warscape::NormalizeTrainingDefence(50) == 50);
    CHECK(Warscape::NormalizeTrainingDefence(99) == 99);
    CHECK(Warscape::NormalizeTrainingDefence(100) == 99);
    CHECK(Warscape::NormalizeTrainingDefence(std::numeric_limits<uint32_t>::max()) == 99);
    CHECK(Warscape::HitChance(Warscape::PlayerAttackRoll(50, 0), Warscape::CombatRoll(1 + 8, 0))
        > Warscape::HitChance(Warscape::PlayerAttackRoll(50, 0), Warscape::CombatRoll(99 + 8, 0)));
}

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

TEST_CASE("Warscape baseline tiers retain archetype identity and preserve full custom profiles", "[warscape]")
{
    using namespace Warscape;
    auto const dagger = BaselineWeaponBonuses(WeaponArchetype::Dagger, 1);
    CHECK(dagger.AttackStab == 4);
    CHECK(dagger.AttackSlash == 2);
    CHECK(dagger.MeleeStrength == 3);
    auto const sword = BaselineWeaponBonuses(WeaponArchetype::Longsword, 1);
    CHECK(sword.AttackSlash == 5);
    CHECK(sword.MeleeStrength == 7);
    auto const mace = BaselineWeaponBonuses(WeaponArchetype::Mace, 1);
    CHECK(mace.AttackCrush == 6);
    CHECK(mace.MeleeStrength == 5);
    auto const hammer = BaselineWeaponBonuses(WeaponArchetype::Warhammer, 1);
    CHECK(hammer.AttackCrush == 10);
    CHECK(hammer.MeleeStrength == 8);
    CHECK(BaselineWeaponBonuses(WeaponArchetype::Longsword, 4).AttackSlash == 20);
    CHECK(BaselineWeaponBonuses(WeaponArchetype::Longsword, 4).MeleeStrength == 22);
    CHECK(BaselineWeaponBonuses(WeaponArchetype::TwoHandedSword, 3).AttackSlash == 21);
    CHECK(BaselineWeaponBonuses(WeaponArchetype::Spear, 3).MeleeStrength == 12);
    CHECK(BaselineWeaponBonuses(WeaponArchetype::Halberd, 3).AttackStab == 14);
    CHECK(BaselineWeaponBonuses(WeaponArchetype::Halberd, 3).MeleeStrength == 20);
    for (uint32_t type = 1; type <= 10; ++type)
    {
        auto const archetype = static_cast<WeaponArchetype>(type);
        auto previous = BaselineWeaponBonuses(archetype, 1);
        for (uint32_t tier = 2; tier <= MaximumEquipmentTier; ++tier)
        {
            auto const next = BaselineWeaponBonuses(archetype, tier);
            CHECK(next.AttackBonus(DefaultMeleeDamageType(archetype)) > previous.AttackBonus(DefaultMeleeDamageType(archetype)));
            CHECK(next.MeleeStrength > previous.MeleeStrength);
            previous = next;
        }
    }
    CHECK(BaselineWeaponBonuses(WeaponArchetype::Dagger, 0).AttackStab == dagger.AttackStab);
    CHECK(BaselineWeaponBonuses(WeaponArchetype::Dagger, 999).AttackStab == dagger.AttackStab);
    for (auto archetype : {WeaponArchetype::Auto, WeaponArchetype::Bow, WeaponArchetype::Staff, WeaponArchetype::Unknown})
        CHECK(BaselineWeaponBonuses(archetype, 6).MeleeStrength == 0);
    EquipmentBonuses custom;
    custom.AttackStab = -12;
    custom.MeleeStrength = 9;
    custom.Prayer = 7;
    auto const preserved = ResolveEquipmentBonuses(WeaponArchetype::Dagger, 6, &custom);
    CHECK(preserved.AttackStab == -12);
    CHECK(preserved.MeleeStrength == 9);
    CHECK(preserved.Prayer == 7);
    EquipmentBonuses zero;
    CHECK(ResolveEquipmentBonuses(WeaponArchetype::Dagger, 6, &zero).MeleeStrength == 0);
    CHECK(ResolveEquipmentBonuses(WeaponArchetype::Longsword, 4, nullptr).MeleeStrength == 22);
}

TEST_CASE("Warscape tenfold display scale preserves ratios, minimum damage and XP", "[warscape]")
{
    CHECK(Warscape::HealthDamageScale == 10);
    CHECK(Warscape::ScaleHealthOrDamage(7) == 70);
    CHECK(Warscape::ScaleHealthOrDamage(7) / Warscape::ScaleHealthOrDamage(1) == 7);
    CHECK(Warscape::VaryScaledDamage(1, 85) == 8);
    CHECK(Warscape::VaryScaledDamage(1, 115) == 12);
    CHECK(Warscape::VaryScaledDamage(1, 1) == 1);
    CHECK(Warscape::VaryScaledDamage(1, 0) == 0);
    CHECK(Warscape::OSRSDamageForXP(5, std::numeric_limits<uint32_t>::max()) == 5);
    CHECK(Warscape::OSRSDamageForXP(5, 1) == 1);
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

TEST_CASE("Warscape health and melee damage scale by 10 without scaling zero", "[warscape]")
{
    CHECK(Warscape::ScaleHealthOrDamage(10) == 100);
    CHECK(Warscape::ScaleHealthOrDamage(11) == 110);
    CHECK(Warscape::ScaleHealthOrDamage(20) == 200);
    CHECK(Warscape::ScaleHealthOrDamage(1) == 10);
    CHECK(Warscape::ScaleHealthOrDamage(0) == 0);
    CHECK(Warscape::ToOSRSDamage(20) == 2);
    CHECK(Warscape::ToOSRSDamage(0) == 0);
    CHECK(Warscape::ScaleHealing(1, 100) == 10);
    CHECK(Warscape::ScaleHealing(20, 100) == 100);
    CHECK(Warscape::ScaleHealing(0, 100) == 0);

    Warscape::MonsterProfile profile;
    Warscape::MonsterDefinition creature;
    creature.Overrides[Warscape::Hitpoints] = 25;
    auto const stats = creature.Calculate(profile, 1);
    CHECK(stats[Warscape::Hitpoints] == 25);
    CHECK(Warscape::ScaleHealthOrDamage(stats[Warscape::Hitpoints]) == 250);
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
    CHECK(Warscape::VaryScaledDamage(1, 80) == 8);
    CHECK(Warscape::VaryScaledDamage(1, 120) == 12);
    CHECK(Warscape::VaryScaledDamage(1, 1) == 1);
    CHECK(Warscape::VaryScaledDamage(2, 80) == 16);
    CHECK(Warscape::VaryScaledDamage(2, 120) == 24);
    CHECK(Warscape::VaryScaledDamage(5, 80) == 40);
    CHECK(Warscape::VaryScaledDamage(5, 120) == 60);
    CHECK(Warscape::ScaleHealthOrDamage(10) == 100);

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
    CHECK(minimum >= 8);
    CHECK(maximum <= 12);
    CHECK(total / double(SampleCount) == Approx(10.0).epsilon(0.001));

    // XP uses the unvaried OSRS hit roll, so low and high display rolls award alike.
    CHECK(Warscape::OSRSDamageForXP(1, 1000) * 4 == 4);
    CHECK(Warscape::OSRSDamageForXP(1, 12) * 4 == 4);
    CHECK(Warscape::OSRSDamageForXP(5, 12) * 4 == 8);
    CHECK(Warscape::OSRSDamageForXP(5, 0) == 0);
}
