/*
 * This file is part of the TrinityCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 */

#include "WarscapeAgilityTraversal.h"
#include "Map.h"
#include "MoveSpline.h"
#include "MoveSplineInit.h"
#include "MotionMaster.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "WorldSession.h"

#include <unordered_map>

namespace
{
    constexpr uint32 TEST_MAP_ID = 0;
    constexpr float START_X = -9066.463867f;
    constexpr float START_Y = -199.568985f;
    constexpr float END_X = -9072.518555f;
    constexpr float END_Y = -214.185699f;
    constexpr float END_Z = 70.450348f;
    constexpr float MAX_START_DISTANCE = 8.0f;
    constexpr uint32 MAX_TRAVERSAL_MS = 12000;
    constexpr uint32 TRAVERSAL_MOTION_ID = 0xA61001;

    struct TraversalSession
    {
        ObjectGuid playerGuid;
        uint32 splineId;
        uint32 elapsedMs;
    };

    using SessionMap = std::unordered_map<Map*, TraversalSession>;
    SessionMap& Sessions()
    {
        static SessionMap sessions;
        return sessions;
    }

    bool IsOwner(Player const* player, TraversalSession const& session)
    {
        return player && player->GetGUID() == session.playerGuid && player->GetSession();
    }

    void StopSpline(Player* player, TraversalSession const& session)
    {
        if (!IsOwner(player, session))
            return;

        if (!player->movespline->Finalized() && player->movespline->GetId() == session.splineId)
        {
            player->GetMotionMaster()->Remove(POINT_MOTION_TYPE, MOTION_SLOT_ACTIVE);
            Movement::MoveSplineInit stop(player);
            stop.Stop(true);
        }
    }

    void UpdateTraversal(Map* map, uint32 diff)
    {
        auto itr = Sessions().find(map);
        if (itr == Sessions().end())
            return;

        Player* player = nullptr;
        for (auto const& playerRef : map->GetPlayers())
            if (playerRef.GetSource() && playerRef.GetSource()->GetGUID() == itr->second.playerGuid)
            {
                player = playerRef.GetSource();
                break;
            }

        if (!IsOwner(player, itr->second))
        {
            itr->second.elapsedMs += diff;
            if (itr->second.elapsedMs >= MAX_TRAVERSAL_MS)
            {
                if (player)
                    StopSpline(player, itr->second);
                Sessions().erase(itr);
            }
            return;
        }

        if (player->IsBeingTeleported() || !player->IsAlive() || player->IsInCombat() ||
            player->GetMap() != map || player->GetVehicle() || player->IsMounted())
        {
            StopSpline(player, itr->second);
            Sessions().erase(itr);
            return;
        }

        if (player->movespline->GetId() != itr->second.splineId || player->movespline->Finalized())
        {
            Sessions().erase(itr);
            return;
        }

        itr->second.elapsedMs += diff;
        if (itr->second.elapsedMs >= MAX_TRAVERSAL_MS)
        {
            StopSpline(player, itr->second);
            Sessions().erase(itr);
        }
    }

    class WarscapeAgilityTestMapScript final : public WorldMapScript
    {
    public:
        WarscapeAgilityTestMapScript() : WorldMapScript("WarscapeAgilityTestMapScript", TEST_MAP_ID) { }

        void OnUpdate(Map* map, uint32 diff) override
        {
            UpdateTraversal(map, diff);
        }

        void OnPlayerLeave(Map* map, Player* player) override
        {
            auto itr = Sessions().find(map);
            if (itr != Sessions().end() && itr->second.playerGuid == player->GetGUID())
            {
                StopSpline(player, itr->second);
                Sessions().erase(itr);
            }
        }
    };

    class WarscapeAgilityPlayerScript final : public PlayerScript
    {
    public:
        WarscapeAgilityPlayerScript() : PlayerScript("WarscapeAgilityPlayerScript") { }

        void OnLogout(Player* player) override
        {
            WarscapeAgilityTraversal::Stop(player, true);
        }
    };
}

bool WarscapeAgilityTraversal::Start(Player* player)
{
    if (!player || !player->GetSession() || !player->IsInWorld() || !player->IsAlive() ||
        player->GetMapId() != TEST_MAP_ID || player->GetMap()->GetInstanceId() != 0 ||
        player->IsInCombat() || player->IsInFlight() || player->GetVehicle() || player->IsMounted())
        return false;

    float dx = player->GetPositionX() - START_X;
    float dy = player->GetPositionY() - START_Y;
    if (dx * dx + dy * dy > MAX_START_DISTANCE * MAX_START_DISTANCE)
        return false;

    SessionMap& sessions = Sessions();
    Map* const map = player->GetMap();
    auto existing = sessions.find(map);
    if (existing != sessions.end())
    {
        if (existing->second.playerGuid != player->GetGUID())
            return false;
        if (player->movespline->GetId() == existing->second.splineId && !player->movespline->Finalized())
            return false;
        sessions.erase(existing);
    }

    std::function<void(Movement::MoveSplineInit&)> initializer = [](Movement::MoveSplineInit& init)
    {
        init.Path().emplace_back(START_X, START_Y, 0.0f);
        init.Path().emplace_back(END_X, END_Y, END_Z);
        init.SetWalk(false);
    };
    player->GetMotionMaster()->LaunchMoveSpline(std::move(initializer), TRAVERSAL_MOTION_ID,
        MOTION_PRIORITY_HIGHEST, POINT_MOTION_TYPE);

    if (player->movespline->Finalized())
        return false;

    sessions.emplace(map, TraversalSession{ player->GetGUID(), player->movespline->GetId(), 0 });
    return true;
}

bool WarscapeAgilityTraversal::Stop(Player* player, bool interrupted)
{
    if (!player || !player->GetMap())
        return false;

    auto itr = Sessions().find(player->GetMap());
    if (itr == Sessions().end() || itr->second.playerGuid != player->GetGUID())
        return false;

    StopSpline(player, itr->second);
    Sessions().erase(itr);
    return interrupted;
}

void AddSC_WarscapeAgilityTraversal()
{
        new WarscapeAgilityTestMapScript();
    new WarscapeAgilityPlayerScript();
}
