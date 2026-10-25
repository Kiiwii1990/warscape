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
