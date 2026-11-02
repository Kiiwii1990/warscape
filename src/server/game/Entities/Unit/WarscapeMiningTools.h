#ifndef WARSCAPE_MINING_TOOLS_H
#define WARSCAPE_MINING_TOOLS_H

#include <array>
#include <cstdint>

namespace Warscape
{
    struct MiningPickaxe
    {
        std::uint32_t ItemEntry;
        char const* Name;
        std::uint8_t MiningLevel;
        std::uint8_t FutureAttackToWield; // Metadata only; never gates inventory mining.
        std::uint8_t RollTicks;

        constexpr std::uint32_t IntervalMs() const { return RollTicks * 600u; }
    };

    // New bronze precedes the legacy tool to give the custom appearance priority
    // on an equal-speed tie. No pickaxe changes the ore's success probability.
    constexpr std::array<MiningPickaxe, 4> MiningPickaxes{{
        {900220, "Warscape Bronze Pickaxe", 1, 1, 8},
        {900221, "Warscape Iron Pickaxe", 1, 1, 7},
        {900222, "Warscape Steel Pickaxe", 6, 5, 6},
        {2901, "Mining Pick", 1, 1, 8}
    }};

    template<class HasCarriedItem>
    MiningPickaxe const* SelectMiningPickaxe(std::uint8_t attainedMiningLevel, HasCarriedItem const& hasItem)
    {
        MiningPickaxe const* selected = nullptr;
        for (MiningPickaxe const& candidate : MiningPickaxes)
            if (attainedMiningLevel >= candidate.MiningLevel && hasItem(candidate.ItemEntry) &&
                (!selected || candidate.RollTicks < selected->RollTicks))
                selected = &candidate;
        return selected;
    }

    // Don't overwrite a weapon appearance changed by real equipment operations.
    constexpr bool ShouldRestoreMiningTool(std::uint32_t visibleEntry, std::uint32_t selectedEntry)
    {
        return selectedEntry && visibleEntry == selectedEntry;
    }
}

#endif
