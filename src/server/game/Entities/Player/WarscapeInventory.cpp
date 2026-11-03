#include "WarscapeInventory.h"
#include "Player.h"
#include "Bag.h"
#include "ChatPackets.h"
#include "ObjectMgr.h"
#include "UpdateFields.h"
#include "UpdateData.h"
#include "WorldPacket.h"
#include <algorithm>
#include <utility>

bool Player::HasWarscapeInventory() const
{
    return (m_ExtraFlags & Warscape::Inventory::ManagedFlag) != 0;
}

bool Player::IsWarscapeInventoryUnlocked() const
{
    return (m_ExtraFlags & Warscape::Inventory::UnlockedFlag) != 0;
}

bool Player::IsWarscapeInventoryContainer(uint8 bag, uint8 slot) const
{
    return HasWarscapeInventory() && bag == INVENTORY_SLOT_BAG_0
        && slot == Warscape::Inventory::ExtensionBagSlot;
}

bool Player::InitializeWarscapeInventory()
{
    using namespace Warscape::Inventory;
    bool anyBag = false, otherBag = false;
    for (uint8 slot = INVENTORY_SLOT_BAG_START; slot < INVENTORY_SLOT_BAG_END; ++slot)
        if (GetItemByPos(INVENTORY_SLOT_BAG_0, slot))
        {
            anyBag = true;
            otherBag |= slot != ExtensionBagSlot;
        }

    if (!HasWarscapeInventory())
    {
        if (!CanProvision(false, anyBag))
            return _warscapeInventoryReady = false;
        ItemTemplate const* proto = sObjectMgr->GetItemTemplate(ContainerEntry);
        if (!proto || proto->GetInventoryType() != INVTYPE_BAG
            || proto->GetContainerSlots() != ExtensionCapacity || proto->GetBagFamily())
            return _warscapeInventoryReady = false;
        Item* item = EquipNewItem(uint16(INVENTORY_SLOT_BAG_0) << 8 | ExtensionBagSlot, ContainerEntry, false);
        if (!item || !item->IsBag())
            return _warscapeInventoryReady = false;
        item->SetBinding(true);
        m_ExtraFlags |= ManagedFlag;
        _warscapeInventoryNeedsSave = true;
    }

    Bag* bag = GetBagByPos(ExtensionBagSlot);
    bool tailOccupied = false;
    if (bag)
        for (uint8 slot = InitialExtensionSlots; slot < ExtensionCapacity; ++slot)
            tailOccupied |= bag->GetItemByPos(slot) != nullptr;
    if (!bag || !CanActivate(bag->GetEntry(), otherBag, tailOccupied, IsWarscapeInventoryUnlocked()))
        return _warscapeInventoryReady = false;
    // The actual native container has 8 or 12 slots. Native auto-store, loot,
    // split/merge and direct placement all observe that same server-side limit.
    bag->SetUInt32Value(CONTAINER_FIELD_NUM_SLOTS, ExtensionSlots(IsWarscapeInventoryUnlocked()));
    return _warscapeInventoryReady = true;
}

bool Player::UnlockWarscapeInventory()
{
    // Future server-side tutorial reward entry point. No client unlock command.
    if (!_warscapeInventoryReady || !HasWarscapeInventory())
        return false;
    if (IsWarscapeInventoryUnlocked())
        return true;
    m_ExtraFlags |= Warscape::Inventory::UnlockedFlag;
    if (!InitializeWarscapeInventory())
    {
        m_ExtraFlags &= ~Warscape::Inventory::UnlockedFlag;
        return false;
    }
    SaveToDB(); // Native per-character transaction; no new table or migration.
    // wowdecomp initializes CGBag_C::m_numSlots in the container constructor.
    // Recreate this owner's bag view with ordinary object packets so its cached
    // capacity changes now, without moving/deleting any server-side items.
    if (Bag* bag = GetBagByPos(Warscape::Inventory::ExtensionBagSlot))
    {
        for (uint8 slot = 0; slot < bag->GetBagSize(); ++slot)
            if (Item* item = bag->GetItemByPos(slot))
                item->DestroyForPlayer(this);
        bag->DestroyForPlayer(this);
        UpdateData update;
        WorldPacket packet;
        bag->BuildCreateUpdateBlockForPlayer(&update, this);
        update.BuildPacket(&packet);
        SendDirectMessage(&packet);
    }
    SendWarscapeInventoryState();
    return true;
}

bool Player::HandleWarscapeInventoryAddon(std::string_view message, std::string const& target, bool whisper)
{
    if (!Warscape::Inventory::IsMessage(message))
        return false;
    if (!whisper || target != GetName() || !IsInWorld() || _warscapeInventoryRequestCooldown)
        return true;
    std::string token = Warscape::Inventory::Subscription(message);
    if (token.empty())
        return true;
    _warscapeInventoryToken = std::move(token);
    _warscapeInventoryRequestCooldown = 1000;
    SendWarscapeInventoryState();
    return true;
}

void Player::UpdateWarscapeInventoryAddon(uint32 diff)
{
    _warscapeInventoryRequestCooldown -= std::min(diff, _warscapeInventoryRequestCooldown);
    if (_warscapeInventoryNeedsSave)
    {
        // Persist the allocated native bag and its character marker together.
        SaveToDB();
        _warscapeInventoryNeedsSave = false;
    }
}

void Player::SendWarscapeInventoryState()
{
    if (_warscapeInventoryToken.empty())
        return;
    std::string state = _warscapeInventoryReady ? "READY" : "CONVERSION_REQUIRED";
    uint32 slots = _warscapeInventoryReady ? Warscape::Inventory::UsableSlots(IsWarscapeInventoryUnlocked()) : 0;
    std::string message = "STATE|1|" + _warscapeInventoryToken + "|" + std::to_string(++_warscapeInventoryRevision)
        + "|" + state + "|" + std::to_string(slots) + "|1";
    WorldPackets::Chat::Chat packet;
    packet.Initialize(CHAT_MSG_WHISPER, LANG_ADDON, this, this, message, 0, "", LOCALE_enUS, Warscape::Inventory::Prefix);
    SendDirectMessage(packet.Write());
}
