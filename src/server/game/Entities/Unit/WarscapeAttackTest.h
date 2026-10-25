/*
 * This file is part of the TrinityCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 */
#ifndef WARSCAPE_ATTACK_TEST_H
#define WARSCAPE_ATTACK_TEST_H

#include <algorithm>
#include <array>
#include <cstdint>
#include <limits>
#include <vector>

namespace Warscape
{
    using AttackTestXP = std::array<std::uint32_t, 7>;

    struct AttackTestSetup
    {
        std::uint32_t Weapon = 0, Style = 0, IntervalMs = 2400, Defence = 1;
        std::int32_t AttackBonus = 0, StrengthBonus = 0;
        bool operator==(AttackTestSetup const&) const = default;
    };

    enum AttackTestPause : std::uint32_t
    {
        AttackTestRange = 1, AttackTestFacing = 2, AttackTestLOS = 4,
        AttackTestControl = 8, AttackTestAutoStopped = 16, AttackTestInvalidTarget = 32
    };

    // A passive event collector: no attacks, timers, XP or game objects are owned here.
    // The caller supplies monotonic timestamps, allowing deterministic tests.
    class AttackTestSession
    {
    public:
        bool Start(std::uint64_t now, std::uint32_t minutes, AttackTestXP const& xp, AttackTestSetup const& setup)
        {
            if (Active || minutes < 1 || minutes > 30)
                return false;
            *this = AttackTestSession{};
            Active = true;
            StartMs = LastObservationMs = now;
            DeadlineMs = now + minutes * 60000ULL;
            StartXP = xp;
            InitialSetup = LatestSetup = setup;
            MinExpectedMs = MaxExpectedMs = setup.IntervalMs;
            Timestamps.reserve(minutes * 60 + 32);
            return true;
        }

        bool Expired(std::uint64_t now) const { return Active && now >= DeadlineMs; }
        std::uint64_t RemainingMs(std::uint64_t now) const { return Active && now < DeadlineMs ? DeadlineMs - now : 0; }

        void ObserveSetup(AttackTestSetup const& setup)
        {
            if (!Active)
                return;
            MixedSetup |= !(setup == InitialSetup);
            WeaponChanged |= setup.Weapon != InitialSetup.Weapon;
            StyleChanged |= setup.Style != InitialSetup.Style;
            DefenceChanged |= setup.Defence != InitialSetup.Defence;
            LatestSetup = setup;
            MinExpectedMs = std::min(MinExpectedMs, setup.IntervalMs);
            MaxExpectedMs = std::max(MaxExpectedMs, setup.IntervalMs);
        }

        void ObservePause(std::uint64_t now, std::uint32_t reason)
        {
            if (!Active || now < LastObservationMs)
                return;
            AccountUntil(now);
            if (reason && !CurrentPause)
                ++PauseCount;
            CurrentPause = reason;
            PauseReasons |= reason;
        }

        bool RecordSwing(std::uint64_t now, bool connected, std::uint64_t damage)
        {
            if (!Active || now < StartMs || now >= DeadlineMs ||
                (!Timestamps.empty() && now < Timestamps.back()) || Timestamps.size() >= MaximumSamples)
                return false;
            Timestamps.push_back(now);
            TotalDamage += damage;
            if (connected)
            {
                ++Hits;
                HitDamage += damage;
                ZeroHits += damage == 0;
                MinHit = std::min(MinHit, damage);
                MaxHit = std::max(MaxHit, damage);
            }
            else
                ++Misses;
            return true;
        }

        bool Finish(std::uint64_t now, AttackTestXP const& xp)
        {
            if (!Active)
                return false;
            EndMs = std::max({now, LastObservationMs, StartMs});
            AccountUntil(EndMs);
            for (std::size_t i = 0; i < StartXP.size(); ++i)
            {
                XPDelta[i] = std::int64_t(xp[i]) - StartXP[i];
                ChangedSkills += XPDelta[i] != 0;
                TotalXPDelta += XPDelta[i];
            }
            Active = false;
            return true;
        }

        void Cancel() { *this = AttackTestSession{}; }
        std::uint64_t ElapsedMs() const { return EndMs >= StartMs ? EndMs - StartMs : 0; }
        double Accuracy() const { return Timestamps.empty() ? 0.0 : Hits * 100.0 / Timestamps.size(); }
        double AverageHit() const { return Hits ? double(HitDamage) / Hits : 0.0; }
        double DPS() const { return ElapsedMs() ? double(TotalDamage) * 1000.0 / ElapsedMs() : 0.0; }
        double AverageIntervalSeconds() const
        {
            return Timestamps.size() < 2 ? 0.0 : double(Timestamps.back() - Timestamps.front()) / (Timestamps.size() - 1) / 1000.0;
        }

        static constexpr std::size_t MaximumSamples = 50000;
        bool Active = false, MixedSetup = false, WeaponChanged = false, StyleChanged = false, DefenceChanged = false;
        std::uint64_t StartMs = 0, DeadlineMs = 0, EndMs = 0;
        std::uint64_t Hits = 0, Misses = 0, ZeroHits = 0, TotalDamage = 0, HitDamage = 0;
        std::uint64_t MinHit = std::numeric_limits<std::uint64_t>::max(), MaxHit = 0;
        std::uint64_t PausedMs = 0;
        std::uint32_t PauseCount = 0, PauseReasons = 0, MinExpectedMs = 0, MaxExpectedMs = 0;
        AttackTestSetup InitialSetup, LatestSetup;
        AttackTestXP StartXP = {};
        std::array<std::int64_t, 7> XPDelta = {};
        std::int64_t TotalXPDelta = 0;
        std::uint32_t ChangedSkills = 0;
        std::vector<std::uint64_t> Timestamps;

    private:
        void AccountUntil(std::uint64_t now)
        {
            if (CurrentPause)
                PausedMs += now - LastObservationMs;
            LastObservationMs = now;
        }
        std::uint64_t LastObservationMs = 0;
        std::uint32_t CurrentPause = 0;
    };
}

#endif
