/*
 * This file is part of the TrinityCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 */

#ifndef WARSCAPE_TRAINING_DUMMY_H
#define WARSCAPE_TRAINING_DUMMY_H

#include <algorithm>
#include <cstdint>

namespace Warscape
{
    constexpr std::uint32_t TrainingDummyEntry = 900001;
    constexpr std::uint32_t TrainingDummyDefenceData = 1;

    constexpr bool IsTrainingDummyEntry(std::uint32_t entry)
    {
        return entry == TrainingDummyEntry;
    }

    constexpr std::uint32_t NormalizeTrainingDefence(std::uint32_t level)
    {
        return std::clamp<std::uint32_t>(level, 1, 99);
    }
}

#endif
