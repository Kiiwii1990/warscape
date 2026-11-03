/*
 * Warscape Mining rocks share one lifecycle and reward engine. Ore-specific
 * rates are configured below; provisional values are explicitly marked.
 */

#include "GameObject.h"
#include "GameObjectAI.h"
#include "ItemDefines.h"
#include "Log.h"
#include "Map.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "UpdateFields.h"
#include "WorldSession.h"
#include "WarscapeMiningTools.h"

#include <algorithm>
#include <array>
#include <mutex>
#include <unordered_map>

namespace
{
constexpr uint32 DepletionDurationMs = 9000;
constexpr uint8 MainHandEquipmentSlot = EQUIPMENT_SLOT_MAINHAND;
constexpr float MiningRockScale = 0.5f;
static_assert(MainHandEquipmentSlot < EQUIPMENT_SLOT_END, "Mining visual must use an equipment slot");
static_assert(PLAYER_VISIBLE_ITEM_1_ENCHANTMENT + MainHandEquipmentSlot * 2 < PLAYER_END,
    "Mining entry/enchantment fields must fit the player update-field allocation");

struct OreConfig
{
    uint32 activeEntry, depletedEntry, activeDisplay, depletedDisplay, itemEntry;
    char const* scriptName;
    char const* oreName;
    uint16 xpHalfPoints, low, high;
    bool provisional;
    uint8 requiredLevel = 1;
};

// OSRS comparable ores use per-rock low/high parameters. WotLK-only ores use
// explicit provisional parameters so each has a nonzero level-1 success chance.
constexpr std::array<OreConfig, 15> OreConfigs{{
    {900101, 900103, 310, 900102, 2770, "go_warscape_copper_rock", "Copper", 35, 100, 350, false},
    {900110, 900111, 900118, 900104, 900201, "go_warscape_mining_tin", "Tin", 35, 100, 350, false},
    {900112, 900113, 900119, 900105, 900202, "go_warscape_mining_silver", "Silver", 80, 25, 200, false},
    {900114, 900115, 900120, 900106, 900203, "go_warscape_mining_iron", "Iron", 70, 96, 350, false},
    {900116, 900117, 900121, 900107, 900204, "go_warscape_mining_gold", "Gold", 130, 7, 75, false},
    {900118, 900119, 900122, 900108, 900205, "go_warscape_mining_mithril", "Mithril", 160, 4, 50, false},
    {900120, 900121, 900123, 900109, 900206, "go_warscape_mining_truesilver", "Truesilver", 80, 18, 180, true},
    {900122, 900123, 900124, 900110, 900207, "go_warscape_mining_dark_iron", "Dark Iron", 180, 24, 200, true},
    {900124, 900125, 900125, 900111, 900208, "go_warscape_mining_thorium", "Thorium", 200, 20, 190, true},
    {900126, 900127, 900126, 900112, 900209, "go_warscape_mining_fel_iron", "Fel Iron", 180, 28, 220, true},
    {900128, 900129, 900127, 900113, 900210, "go_warscape_mining_adamantite", "Adamantite", 190, 3, 25, false},
    {900130, 900131, 900128, 900114, 900211, "go_warscape_mining_khorium", "Khorium", 240, 30, 230, true},
    {900132, 900133, 900129, 900115, 900212, "go_warscape_mining_cobalt", "Cobalt", 160, 32, 220, true},
    {900134, 900135, 900130, 900116, 900213, "go_warscape_mining_saronite", "Saronite", 200, 24, 200, true},
    {900136, 900137, 900131, 900117, 900214, "go_warscape_mining_titanium", "Titanium", 250, 15, 170, true}
}};

constexpr bool OreConfigsAreSafe()
{
    for (size_t i = 0; i < OreConfigs.size(); ++i)
    {
        OreConfig const& ore = OreConfigs[i];
        if (ore.activeEntry == ore.depletedEntry || !ore.scriptName || !ore.oreName ||
            !ore.requiredLevel || !ore.low || ore.high > 1024)
            return false;
        for (size_t j = i + 1; j < OreConfigs.size(); ++j)
        {
            OreConfig const& other = OreConfigs[j];
            if (ore.activeEntry == other.activeEntry || ore.activeEntry == other.depletedEntry ||
                ore.depletedEntry == other.activeEntry || ore.depletedEntry == other.depletedEntry ||
                ore.activeDisplay == other.activeDisplay || ore.activeDisplay == other.depletedDisplay ||
                ore.depletedDisplay == other.activeDisplay || ore.depletedDisplay == other.depletedDisplay ||
                ore.itemEntry == other.itemEntry)
                return false;
        }
    }
    return true;
}
static_assert(OreConfigsAreSafe(), "Warscape Mining ore entries, displays, levels and rewards must be valid and unique");

std::mutex MiningSessionMutex;
std::unordered_map<ObjectGuid, ObjectGuid> ActiveMiningRocks;

bool ReserveMiningSession(ObjectGuid const& playerGuid, ObjectGuid const& rockGuid)
{
    std::lock_guard<std::mutex> lock(MiningSessionMutex);
    return ActiveMiningRocks.emplace(playerGuid, rockGuid).second;
}

void ReleaseMiningSession(ObjectGuid const& playerGuid, ObjectGuid const& rockGuid)
{
    std::lock_guard<std::mutex> lock(MiningSessionMutex);
    auto const session = ActiveMiningRocks.find(playerGuid);
    if (session != ActiveMiningRocks.end() && session->second == rockGuid)
        ActiveMiningRocks.erase(session);
}

bool HasOreSpace(Player* player, OreConfig const& config)
{
    ItemPosCountVec destination;
    return player->CanStoreNewItem(NULL_BAG, NULL_SLOT, destination, config.itemEntry, 1) == EQUIP_ERR_OK;
}
}

class go_warscape_mining_rock : public GameObjectScript
{
public:
    go_warscape_mining_rock(char const* scriptName, OreConfig const& config) : GameObjectScript(scriptName), _config(config) { }

    struct MiningRockAI final : GameObjectAI
    {
        MiningRockAI(GameObject* gameObject, OreConfig const& config) : GameObjectAI(gameObject), _config(config), _activePhaseMask(gameObject->GetPhaseMask())
        {
            // Apply to all persisted and newly GM-spawned 900101 objects at runtime;
            // the object scale field also drives its server VMap collision model.
            me->SetObjectScale(MiningRockScale);
        }

        ~MiningRockAI() override
        {
            StopMining();
            RemoveDepletedCounterpart();
        }

        bool OnGossipHello(Player* player) override
        {
            if (player->IsWarscapeSmelting())
            {
                player->GetSession()->SendNotification("Finish smelting before Mining.");
                return true;
            }
            if (_depleted)
            {
                player->GetSession()->SendNotification("This mining rock is depleted.");
                return true;
            }

            auto const* pickaxe = SelectPickaxe(player);
            if (!pickaxe)
            {
                TC_LOG_INFO("scripts", "WarscapeMining: {} interaction rejected; no carried pickaxe meets the attained Mining level.", _config.oreName);
                player->GetSession()->SendNotification("You need a pickaxe usable at your attained Mining level in your inventory.");
                return true;
            }

            if (!HasOreSpace(player, _config))
            {
                TC_LOG_INFO("scripts", "WarscapeMining: rock interaction rejected; inventory has no ore space.");
                player->GetSession()->SendNotification("Your inventory is full.");
                return true;
            }

            if (!_minerGuid.IsEmpty())
            {
                if (_minerGuid != player->GetGUID())
                    player->GetSession()->SendNotification("Someone is already mining this rock.");
                return true;
            }

            if (!ReserveMiningSession(player->GetGUID(), me->GetGUID()))
            {
                player->GetSession()->SendNotification("You are already mining another rock.");
                return true;
            }

            if (!EnsureDepletedCounterpart())
            {
                ReleaseMiningSession(player->GetGUID(), me->GetGUID());
                TC_LOG_ERROR("scripts", "WarscapeMining: failed to create hidden depleted counterpart for rock GUID {}.", me->GetGUID().ToString());
                player->GetSession()->SendNotification("This mining rock is temporarily unavailable.");
                return true;
            }

            _minerGuid = player->GetGUID();
            _selectedPickaxe = pickaxe;
            _attemptTimer = pickaxe->IntervalMs();
            ShowMiningTool(player);
            TC_LOG_INFO("scripts", "WarscapeMining: {} interaction started; rock entry {} GUID {} display ID before Mining {}.",
                _config.oreName, me->GetEntry(), me->GetGUID().ToString(), me->GetDisplayId());
            player->GetSession()->SendNotification("Mining with %s. Attempts repeat every %.1f seconds.", pickaxe->Name, pickaxe->IntervalMs() / 1000.0);
            player->SetEmoteState(EMOTE_STATE_WORK_MINING);
            return true;
        }

        void UpdateAI(uint32 diff) override
        {
            if (!_counterpartInitialized)
            {
                _counterpartInitialized = true;
                if (!EnsureDepletedCounterpart())
                    TC_LOG_ERROR("scripts", "WarscapeMining: could not initialize hidden depleted counterpart for rock GUID {}.", me->GetGUID().ToString());
            }

            if (_depleted)
            {
                if (_depletionTimer <= diff)
                {
                    GameObject* counterpart = me->GetMap()->GetGameObject(_depletedRockGuid);
                    uint32 const displayBeforeRestore = counterpart ? counterpart->GetDisplayId() : _config.depletedDisplay;
                    _depleted = false;
                    _depletionTimer = 0;
                    RestoreActiveAppearance();
                    TC_LOG_INFO("scripts", "WarscapeMining: rock entry {} GUID {} recovered from depleted display {}; active display is {}.",
                        me->GetEntry(), me->GetGUID().ToString(), displayBeforeRestore, me->GetDisplayId());
                }
                else
                {
                    _depletionTimer -= diff;
                    if (!_depletionMidpointLogged && _depletionTimer <= DepletionDurationMs / 2)
                    {
                        _depletionMidpointLogged = true;
                        TC_LOG_INFO("scripts", "WarscapeMining: during depletion, rock entry {} GUID {} display ID {} with {} ms remaining.",
                            me->GetEntry(), me->GetGUID().ToString(), me->GetDisplayId(), _depletionTimer);
                    }
                }
                return;
            }

            if (_minerGuid.IsEmpty())
                return;

            Player* player = ObjectAccessor::FindPlayer(_minerGuid);
            char const* interruption = nullptr;
            if (!player)
                interruption = "player offline or logged out";
            else if (!player->IsAlive())
                interruption = "player died";
            else if (player->IsInCombat())
                interruption = "player entered combat";
            else if (player->isMoving())
                interruption = "player moved";
            else if (!player->IsWithinDistInMap(me, 5.0f))
                interruption = "player left interaction range";

            if (interruption)
            {
                TC_LOG_INFO("scripts", "WarscapeMining: attempt loop interrupted: {}.", interruption);
                StopMining();
                return;
            }

            if (player->GetRSSkillLevel(Player::RS_Skill::Mining) < _config.requiredLevel)
            {
                player->GetSession()->SendNotification("Your Mining level is too low.");
                StopMining();
                return;
            }

            auto const* pickaxe = SelectPickaxe(player);
            if (!pickaxe)
            {
                player->GetSession()->SendNotification("No usable pickaxe remains in your inventory.");
                StopMining();
                return;
            }
            if (pickaxe != _selectedPickaxe)
            {
                _selectedPickaxe = pickaxe;
                _attemptTimer = pickaxe->IntervalMs();
                ShowMiningTool(player);
                return; // A changed tool starts a full interval; no immediate bonus roll.
            }

            if (_attemptTimer > diff)
            {
                _attemptTimer -= diff;
                return;
            }

            _attemptTimer = _selectedPickaxe->IntervalMs();

            if (!HasOreSpace(player, _config))
            {
                TC_LOG_INFO("scripts", "WarscapeMining: attempt loop stopped; inventory became full.");
                player->GetSession()->SendNotification("Your inventory is full.");
                StopMining();
                return;
            }

            uint16 const chance = Warscape::MiningSuccessOutOf256(
                player->GetRSSkillLevel(Player::RS_Skill::Mining),
                _config.low, _config.high);
            if (urand(0, 255) >= chance)
                return;

            ItemPosCountVec destination;
            if (player->CanStoreNewItem(NULL_BAG, NULL_SLOT, destination, _config.itemEntry, 1) != EQUIP_ERR_OK)
            {
                TC_LOG_INFO("scripts", "WarscapeMining: {} successful roll aborted; inventory could not store one ore.", _config.oreName);
                player->GetSession()->SendNotification("Your inventory is full.");
                StopMining();
                return;
            }

            if (!player->StoreNewItem(destination, _config.itemEntry, true))
            {
                TC_LOG_ERROR("scripts", "WarscapeMining: inventory storage failed after CanStoreNewItem succeeded.");
                StopMining();
                return;
            }

            player->AddRSSkillHalfXP(Player::RS_Skill::Mining, _config.xpHalfPoints);
            StopMining();
            uint32 const displayBeforeDepletion = me->GetDisplayId();
            _depleted = true;
            _depletionTimer = DepletionDurationMs;
            _depletionMidpointLogged = false;
            ShowDepletedAppearance();
            TC_LOG_INFO("scripts", "WarscapeMining: {} extraction; rock entry {} GUID {} active display {} hidden; counterpart display {} shown at scale {}; depletion {} ms.",
                _config.oreName, me->GetEntry(), me->GetGUID().ToString(), displayBeforeDepletion, _config.depletedDisplay,
                MiningRockScale, DepletionDurationMs);
        }

    private:
        bool EnsureDepletedCounterpart()
        {
            if (!_depletedRockGuid.IsEmpty())
            {
                GameObject* counterpart = me->GetMap()->GetGameObject(_depletedRockGuid);
                if (counterpart && counterpart->IsInWorld())
                    return true;
                _depletedRockGuid.Clear();
            }

            Map* map = me->GetMap();
            GameObject* counterpart = new GameObject();
            if (!counterpart->Create(map->GenerateLowGuid<HighGuid::GameObject>(), _config.depletedEntry, map, 0,
                me->GetPosition(), me->GetLocalRotation(), 255, GO_STATE_READY, me->GetGoArtKit()))
            {
                delete counterpart;
                return false;
            }

            counterpart->SetObjectScale(MiningRockScale);
            counterpart->SetFlag(GO_FLAG_NOT_SELECTABLE);
            if (!map->AddToMap(counterpart))
            {
                delete counterpart;
                return false;
            }

            _depletedRockGuid = counterpart->GetGUID();
            return true;
        }

        void ShowDepletedAppearance()
        {
            if (GameObject* counterpart = me->GetMap()->GetGameObject(_depletedRockGuid))
            {
                // Keep the alternate object out of every player's phase until
                // after the active rock has been hidden.
                me->SetPhaseMask(0, true);
                counterpart->SetPhaseMask(_activePhaseMask, true);
                counterpart->EnableCollision(true);
            }
            else
                TC_LOG_ERROR("scripts", "WarscapeMining: depleted counterpart {} vanished for active rock {}.",
                    _depletedRockGuid.ToString(), me->GetGUID().ToString());
        }

        void RestoreActiveAppearance()
        {
            if (GameObject* counterpart = me->GetMap()->GetGameObject(_depletedRockGuid))
            {
                counterpart->SetPhaseMask(0, true);
                me->SetPhaseMask(_activePhaseMask, true);
                me->EnableCollision(true);
                return;
            }
            me->SetPhaseMask(_activePhaseMask, true);
            me->EnableCollision(true);
        }

        void RemoveDepletedCounterpart()
        {
            if (_depletedRockGuid.IsEmpty())
                return;

            if (Map* map = me->FindMap())
                if (GameObject* counterpart = map->GetGameObject(_depletedRockGuid))
                    if (counterpart->IsInWorld())
                        counterpart->Delete();
            _depletedRockGuid.Clear();
        }

        static Warscape::MiningPickaxe const* SelectPickaxe(Player* player)
        {
            // GetItemByEntry covers carried bags/equipment, never bank storage.
            // GetRSSkillLevel reads the permanently attained Warscape skill level.
            return Warscape::SelectMiningPickaxe(player->GetRSSkillLevel(Player::RS_Skill::Mining),
                [player](uint32 entry) { return player->GetItemByEntry(entry) != nullptr; });
        }

        void ShowMiningTool(Player* player)
        {
            if (Item* pick = player->GetItemByEntry(_selectedPickaxe->ItemEntry))
            {
                _miningToolVisualActive = true;
                player->SetVisibleItemSlot(MainHandEquipmentSlot, pick);
            }
        }

        void StopMining()
        {
            if (!_minerGuid.IsEmpty())
            {
                ReleaseMiningSession(_minerGuid, me->GetGUID());
                if (Player* player = ObjectAccessor::FindPlayer(_minerGuid))
                {
                    if (player->GetEmoteState() == EMOTE_STATE_WORK_MINING)
                        player->SetEmoteState(EMOTE_STATE_NONE);

                    if (_miningToolVisualActive)
                    {
                        uint16 const visibleItemField = PLAYER_VISIBLE_ITEM_1_ENTRYID + MainHandEquipmentSlot * 2;
                        if (Warscape::ShouldRestoreMiningTool(player->GetUInt32Value(visibleItemField),
                            _selectedPickaxe ? _selectedPickaxe->ItemEntry : 0))
                        {
                            // Restore actual equipment, including enchants or changes
                            // made while mining. The tool was only a visible-slot override.
                            player->SetVisibleItemSlot(MainHandEquipmentSlot,
                                player->GetItemByPos(INVENTORY_SLOT_BAG_0, MainHandEquipmentSlot));
                        }
                    }
                }
            }
            _minerGuid.Clear();
            _attemptTimer = 0;
            _selectedPickaxe = nullptr;
            _miningToolVisualActive = false;
        }

        OreConfig const& _config;
        ObjectGuid _minerGuid;
        uint32 _attemptTimer = 0;
        uint32 _depletionTimer = 0;
        Warscape::MiningPickaxe const* _selectedPickaxe = nullptr;
        ObjectGuid _depletedRockGuid;
        uint32 _activePhaseMask;
        bool _counterpartInitialized = false;
        bool _depleted = false;
        bool _miningToolVisualActive = false;
        bool _depletionMidpointLogged = false;
    };

    GameObjectAI* GetAI(GameObject* gameObject) const override
    {
        return new MiningRockAI(gameObject, _config);
    }

private:
    OreConfig const& _config;
};

void AddSC_warscape_copper_mining()
{
    for (size_t index = 0; index < OreConfigs.size(); ++index)
        new go_warscape_mining_rock(OreConfigs[index].scriptName, OreConfigs[index]);
}
