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
#include "MapManager.h"
#include "MoveSpline.h"
#include "MoveSplineInit.h"
#include "MotionMaster.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "WorldSession.h"

#include <array>
#include <algorithm>
#include <cmath>
#include <unordered_map>
#include <vector>

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

    struct RoutePoint
    {
        float x;
        float y;
        float z;
    };

    // Measured by the user in-game with .gps while standing on the edited log.
    constexpr std::array<RoutePoint, 7> NORTHSHIRE_LOG_ROUTE = {{
        { -9074.780273f, -195.128021f, 71.909966f }, // approach
        { -9075.851562f, -197.076318f, 70.528038f }, // takeoff
        { -9076.198242f, -199.217316f, 71.087822f }, // near log
        { -9077.499023f, -203.898041f, 71.180267f }, // log midpoint
        { -9078.817383f, -209.583771f, 71.663506f }, // far log
        { -9079.299805f, -211.528687f, 70.387108f }, // step-off
        { -9079.845703f, -213.721573f, 70.746696f }  // landing
    }};

    struct TraversalSession
    {
        ObjectGuid playerGuid;
        uint32 splineId;
        uint32 elapsedMs;
        uint32 timeoutMs;
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

    bool IsValidRoute(std::vector<G3D::Vector3> const& path)
    {
        return path.size() > 1 && std::all_of(path.begin(), path.end(), [](G3D::Vector3 const& point)
        {
            return std::isfinite(point.x) && std::isfinite(point.y) && std::isfinite(point.z) &&
                MapManager::IsValidMapCoord(TEST_MAP_ID, point.x, point.y, point.z);
        });
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
            if (itr->second.elapsedMs >= itr->second.timeoutMs)
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
        if (itr->second.elapsedMs >= itr->second.timeoutMs)
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

bool WarscapeAgilityTraversal::Start(Player* player, Route route)
{
    if (!player || !player->GetSession() || !player->IsInWorld() || !player->IsAlive() ||
        player->GetMapId() != TEST_MAP_ID || player->GetMap()->GetInstanceId() != 0 ||
        player->IsInCombat() || player->IsInFlight() || player->GetVehicle() || player->IsMounted())
        return false;

    std::vector<G3D::Vector3> path;
    float startX = START_X;
    float startY = START_Y;
    float startDistance = MAX_START_DISTANCE;
    bool walk = false;
    float speed = 4.5f;
    if (route == Route::NorthshireLog)
    {
        path.reserve(NORTHSHIRE_LOG_ROUTE.size());
        for (RoutePoint const& point : NORTHSHIRE_LOG_ROUTE)
            path.emplace_back(point.x, point.y, point.z);
        startX = NORTHSHIRE_LOG_ROUTE.front().x;
        startY = NORTHSHIRE_LOG_ROUTE.front().y;
        startDistance = 3.0f;
        walk = true;
        speed = 2.5f;
    }
    else
    {
        path.emplace_back(START_X, START_Y, 0.0f);
        path.emplace_back(END_X, END_Y, END_Z);
    }

    if (!IsValidRoute(path))
        return false;

    float dx = player->GetPositionX() - startX;
    float dy = player->GetPositionY() - startY;
    if (dx * dx + dy * dy > startDistance * startDistance)
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

    uint32 const timeoutMs = route == Route::NorthshireLog ? 30000 : MAX_TRAVERSAL_MS;
    std::function<void(Movement::MoveSplineInit&)> initializer = [path = std::move(path), walk, speed](Movement::MoveSplineInit& init)
    {
        init.Path() = path;
        init.SetWalk(walk);
        init.SetVelocity(speed);
    };
    player->GetMotionMaster()->LaunchMoveSpline(std::move(initializer), TRAVERSAL_MOTION_ID,
        MOTION_PRIORITY_HIGHEST, POINT_MOTION_TYPE);

    if (player->movespline->Finalized())
        return false;

    sessions.emplace(map, TraversalSession{ player->GetGUID(), player->movespline->GetId(), 0, timeoutMs });
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
