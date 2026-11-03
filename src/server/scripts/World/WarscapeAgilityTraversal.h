/*
 * This file is part of the TrinityCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 */

#ifndef TRINITY_WARSCAPE_AGILITY_TRAVERSAL_H
#define TRINITY_WARSCAPE_AGILITY_TRAVERSAL_H

#include "ObjectGuid.h"

class Player;

namespace WarscapeAgilityTraversal
{
    enum class StartStatus
    {
        Rejected,
        RollFailed,
        Started
    };

    struct StartResult
    {
        StartStatus status;
        uint32 rewardXP;
    };

    enum class Route
    {
        StreamPrototype,
        NorthshireLog
    };

    StartResult Start(Player* player, Route route = Route::StreamPrototype);
    bool Stop(Player* player, bool interrupted);
}

#endif
