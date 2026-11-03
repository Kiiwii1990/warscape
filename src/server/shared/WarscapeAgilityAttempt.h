/*
 * This file is part of the TrinityCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 */

#ifndef TRINITY_WARSCAPE_AGILITY_ATTEMPT_H
#define TRINITY_WARSCAPE_AGILITY_ATTEMPT_H

#include <cstdint>

namespace Warscape
{
    // roll is an integer in [0, 99], which makes a 100% obstacle chance certain.
    inline bool ShouldAcceptAgilityAttempt(bool eligible, bool traversalActive,
        std::uint8_t successChancePercent, std::uint32_t roll)
    {
        return eligible && !traversalActive && successChancePercent <= 100 && roll < 100 &&
            roll < successChancePercent;
    }

    template <typename AwardReward, typename BeginTraversal>
    inline bool ExecuteAgilityAttempt(bool eligible, bool traversalActive,
        std::uint8_t successChancePercent, std::uint32_t roll,
        AwardReward awardReward, BeginTraversal beginTraversal)
    {
        if (!ShouldAcceptAgilityAttempt(eligible, traversalActive, successChancePercent, roll))
            return false;

        awardReward();
        beginTraversal();
        return true;
    }
}

#endif
