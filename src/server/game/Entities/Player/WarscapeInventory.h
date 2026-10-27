#ifndef WARSCAPE_INVENTORY_H
#define WARSCAPE_INVENTORY_H

#include <cstdint>
#include <string>
#include <string_view>

namespace Warscape::Inventory
{
    inline constexpr char Prefix[] = "WCInventory";
    inline constexpr std::uint32_t ContainerEntry = 10050; // Native 12-slot Mageweave Bag.
    inline constexpr std::uint8_t BackpackSlots = 16;
    inline constexpr std::uint8_t ExtensionBagSlot = 19; // Native carried bag 1.
    inline constexpr std::uint8_t ExtensionCapacity = 12;
    inline constexpr std::uint8_t InitialExtensionSlots = 8;
    inline constexpr std::uint16_t ManagedFlag = 0x1000;
    inline constexpr std::uint16_t UnlockedFlag = 0x2000;

    constexpr std::uint8_t ExtensionSlots(bool unlocked)
    {
        return unlocked ? ExtensionCapacity : InitialExtensionSlots;
    }

    constexpr std::uint8_t UsableSlots(bool unlocked)
    {
        return BackpackSlots + ExtensionSlots(unlocked);
    }

    // Existing bags are never replaced, emptied or silently hidden by enrollment.
    constexpr bool CanProvision(bool alreadyManaged, bool anyCarriedBag)
    {
        return !alreadyManaged && !anyCarriedBag;
    }

    constexpr bool CanActivate(std::uint32_t entry, bool otherCarriedBag, bool lockedTailOccupied, bool unlocked)
    {
        return entry == ContainerEntry && !otherCarriedBag && (unlocked || !lockedTailOccupied);
    }

    inline bool IsMessage(std::string_view message)
    {
        return message.substr(0, 12) == "WCInventory\t";
    }

    inline std::string Subscription(std::string_view message)
    {
        constexpr std::string_view header = "WCInventory\tHELLO|1|";
        if (message.substr(0, header.size()) != header)
            return {};
        auto token = message.substr(header.size());
        if (token.empty() || token.size() > 16)
            return {};
        for (char c : token)
            if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')))
                return {};
        return std::string(token);
    }
}

#endif
