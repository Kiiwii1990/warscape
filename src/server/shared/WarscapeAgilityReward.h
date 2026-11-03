/*
 * This file is part of the TrinityCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or (at
 * your option) any later version.
 */

#ifndef TRINITY_WARSCAPE_AGILITY_REWARD_H
#define TRINITY_WARSCAPE_AGILITY_REWARD_H

#include <cmath>

namespace Warscape
{
    // A traversal reward can be claimed once, and only after its owned spline
    // finalizes with an eligible player at the configured landing point.
    inline bool TryClaimAgilityTraversalReward(bool& rewardPending, bool trackedSpline, bool finalized,
        bool eligible, float distanceSquared, float landingRadius)
    {
        if (!rewardPending || !trackedSpline || !finalized || !eligible ||
            !std::isfinite(distanceSquared) || !std::isfinite(landingRadius) ||
            distanceSquared < 0.0f || landingRadius < 0.0f ||
            distanceSquared > landingRadius * landingRadius)
            return false;

        rewardPending = false;
        return true;
    }
}

#endif
