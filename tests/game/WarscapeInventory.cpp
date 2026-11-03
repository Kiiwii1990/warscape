#include <catch2/catch.hpp>
#include "WarscapeInventory.h"

TEST_CASE("Warscape inventory capacity is backed by 16 native and 8 or 12 extension slots", "[warscape][inventory]")
{
    using namespace Warscape::Inventory;
    CHECK(UsableSlots(false) == 24);
    CHECK(UsableSlots(true) == 28);
    CHECK(ExtensionSlots(false) == 8);
    CHECK(ExtensionSlots(true) == ExtensionCapacity);
    CHECK(ExtensionBagSlot == 19);
    CHECK((ManagedFlag & UnlockedFlag) == 0);
    CHECK(static_cast<std::uint16_t>(ManagedFlag | UnlockedFlag) == (ManagedFlag | UnlockedFlag));
    CHECK((ManagedFlag & 0x0fff) == 0);
    CHECK((UnlockedFlag & 0x0fff) == 0);
}

TEST_CASE("Warscape inventory enrollment preserves existing bags and occupied locked tails", "[warscape][inventory]")
{
    using namespace Warscape::Inventory;
    CHECK(CanProvision(false, false));
    CHECK_FALSE(CanProvision(false, true));
    CHECK_FALSE(CanProvision(true, false));
    CHECK_FALSE(CanProvision(true, true));
    CHECK(CanActivate(ContainerEntry, false, false, false));
    CHECK(CanActivate(ContainerEntry, false, true, true));
    CHECK_FALSE(CanActivate(ContainerEntry, false, true, false));
    CHECK_FALSE(CanActivate(ContainerEntry, true, false, true));
    CHECK_FALSE(CanActivate(0, false, false, false));
    CHECK_FALSE(CanActivate(ContainerEntry + 1, false, false, true));
}

TEST_CASE("Inventory addon protocol accepts read-only self-subscription tokens only", "[warscape][inventory]")
{
    using namespace Warscape::Inventory;
    CHECK(IsMessage("WCInventory\tUNLOCK|1|abc"));
    CHECK_FALSE(IsMessage("WCInventoryX\tHELLO|1|abc"));
    CHECK(Subscription("WCInventory\tHELLO|1|abc123") == "abc123");
    for (auto invalid : {"WCInventory\tUNLOCK|1|abc", "WCInventory\tMOVE|1|abc|25", "WCInventory\tHELLO|2|abc",
        "WCInventory\tHELLO|1|", "WCInventory\tHELLO|1|abcdefghijklmnopq", "WCInventory\tHELLO|1|a|b",
        "WCInventory\tHELLO|1|a\n", "Other\tHELLO|1|abc"})
        CHECK(Subscription(invalid).empty());
}
