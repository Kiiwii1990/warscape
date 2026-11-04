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
#include "GameObject.h"
#include "GameObjectAI.h"
#include "Log.h"
#include "MoveSpline.h"
#include "MoveSplineInit.h"
#include "MotionMaster.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "WorldSession.h"
#include "Random.h"
#include "WarscapeAgilityAttempt.h"

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

    struct ObstacleDefinition
    {
        char const* id;
        uint32 gameObjectEntry;
        uint32 mapId;
        uint32 instanceId;
        std::array<RoutePoint, 7> const* route;
        float startRadius;
        float speed;
        uint32 timeoutMs;
        uint8 requiredAgility;
        uint32 rewardXP;
        uint8 successChancePercent;
    };

    // Keep obstacle data independent from the shared spline/session runner.
    constexpr std::array<ObstacleDefinition, 1> OBSTACLES = {{
        { "northshire_log", 900700, TEST_MAP_ID, 0, &NORTHSHIRE_LOG_ROUTE, 30.0f, 2.5f, 30000, 1, 8, 100 }
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

    ObstacleDefinition const* FindObstacleByEntry(uint32 entry)
    {
        auto const itr = std::find_if(OBSTACLES.begin(), OBSTACLES.end(), [entry](ObstacleDefinition const& obstacle)
        {
            return obstacle.gameObjectEntry == entry;
        });
        return itr == OBSTACLES.end() ? nullptr : &*itr;
    }

    WarscapeAgilityTraversal::StartResult StartObstacle(Player* player, ObstacleDefinition const& obstacle);

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
            TC_LOG_INFO("scripts", "WarscapeAgility: traversal interrupted player={} obstacle spline={} reason=player-state",
                player->GetGUID().ToString(), itr->second.splineId);
            StopSpline(player, itr->second);
            Sessions().erase(itr);
            return;
        }

        if (player->movespline->GetId() != itr->second.splineId)
        {
            TC_LOG_INFO("scripts", "WarscapeAgility: traversal interrupted player={} expectedSpline={} actualSpline={}",
                player->GetGUID().ToString(), itr->second.splineId, player->movespline->GetId());
            Sessions().erase(itr);
            return;
        }

        if (player->movespline->Finalized())
        {
            TC_LOG_INFO("scripts", "WarscapeAgility: traversal completed player={} spline={}",
                player->GetGUID().ToString(), itr->second.splineId);
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

    class go_warscape_agility_obstacle final : public GameObjectScript
    {
    public:
        go_warscape_agility_obstacle() : GameObjectScript("go_warscape_agility_obstacle") { }

        struct ObstacleAI final : GameObjectAI
        {
            explicit ObstacleAI(GameObject* gameObject) : GameObjectAI(gameObject) { }

            bool OnReportUse(Player* player) override
            {
                if (player)
                    TC_LOG_INFO("scripts", "WarscapeAgility: GameObject report-use received entry={} guid={} player={} position=({:.3f},{:.3f},{:.3f})",
                        me->GetEntry(), me->GetGUID().ToString(), player->GetGUID().ToString(),
                        player->GetPositionX(), player->GetPositionY(), player->GetPositionZ());
                return false;
            }

            bool OnGossipHello(Player* player) override
            {
                if (!player)
                    return true;

                TC_LOG_INFO("scripts", "WarscapeAgility: GameObject use accepted at interaction range entry={} guid={} player={} position=({:.3f},{:.3f},{:.3f})",
                    me->GetEntry(), me->GetGUID().ToString(), player->GetGUID().ToString(),
                    player->GetPositionX(), player->GetPositionY(), player->GetPositionZ());

                WarscapeAgilityTraversal::StartResult const result =
                    WarscapeAgilityTraversal::StartFromGameObject(player, me->GetEntry());
                switch (result.status)
                {
                    case WarscapeAgilityTraversal::StartStatus::Started:
                        player->GetSession()->SendNotification("Agility Roll Succeeded (+%u XP).", result.rewardXP);
                        break;
                    case WarscapeAgilityTraversal::StartStatus::RollFailed:
                        player->GetSession()->SendNotification("Agility Roll Failed");
                        break;
                    case WarscapeAgilityTraversal::StartStatus::Rejected:
                        player->GetSession()->SendNotification("You cannot start this Agility obstacle right now.");
                        break;
                }
                return true;
            }
        };

        GameObjectAI* GetAI(GameObject* gameObject) const override
        {
            return new ObstacleAI(gameObject);
        }
    };
}

namespace
{
WarscapeAgilityTraversal::StartResult StartObstacle(Player* player, ObstacleDefinition const& obstacle)
{
    if (!player || !player->GetSession() || !player->IsInWorld() || !player->IsAlive() ||
        player->GetMapId() != TEST_MAP_ID || player->GetMap()->GetInstanceId() != 0 ||
        player->IsInCombat() || player->IsInFlight() || player->GetVehicle() || player->IsMounted())
        return { WarscapeAgilityTraversal::StartStatus::Rejected, 0 };

    if (player->GetMapId() != obstacle.mapId || player->GetMap()->GetInstanceId() != obstacle.instanceId ||
        player->GetRSSkillLevel(Player::RS_Skill::Agility) < obstacle.requiredAgility)
        return { WarscapeAgilityTraversal::StartStatus::Rejected, 0 };

    std::vector<G3D::Vector3> path;
    path.reserve(obstacle.route->size());
    for (RoutePoint const& point : *obstacle.route)
        path.emplace_back(point.x, point.y, point.z);

    if (!IsValidRoute(path))
        return { WarscapeAgilityTraversal::StartStatus::Rejected, 0 };

    float dx = player->GetPositionX() - obstacle.route->front().x;
    float dy = player->GetPositionY() - obstacle.route->front().y;
    if (dx * dx + dy * dy > obstacle.startRadius * obstacle.startRadius)
        return { WarscapeAgilityTraversal::StartStatus::Rejected, 0 };

    SessionMap& sessions = Sessions();
    Map* const map = player->GetMap();
    auto existing = sessions.find(map);
    if (existing != sessions.end())
    {
        if (existing->second.playerGuid != player->GetGUID())
            return { WarscapeAgilityTraversal::StartStatus::Rejected, 0 };
        if (player->movespline->GetId() == existing->second.splineId && !player->movespline->Finalized())
            return { WarscapeAgilityTraversal::StartStatus::Rejected, 0 };
        sessions.erase(existing);
    }

    // Roll only after every eligibility, route and duplicate-session check has passed.
    uint32 const roll = urand(0, 99);

    uint32 const timeoutMs = obstacle.timeoutMs;
    std::function<void(Movement::MoveSplineInit&)> initializer = [path = std::move(path), speed = obstacle.speed](Movement::MoveSplineInit& init)
    {
        init.Path() = path;
        init.SetWalk(true);
        init.SetVelocity(speed);
    };
    auto beginTraversal = [&]()
    {
        player->GetMotionMaster()->LaunchMoveSpline(std::move(initializer), TRAVERSAL_MOTION_ID,
            MOTION_PRIORITY_HIGHEST, POINT_MOTION_TYPE);
    };

    uint32 const oldXP = player->GetRSSkillXP(Player::RS_Skill::Agility);
    bool const accepted = Warscape::ExecuteAgilityAttempt(true, false, obstacle.successChancePercent, roll,
        [&]()
        {
            player->AddRSSkillXP(Player::RS_Skill::Agility, obstacle.rewardXP);
            TC_LOG_INFO("scripts", "WarscapeAgility: XP awarded player={} obstacle={} oldXP={} reward={} newXP={}",
                player->GetGUID().ToString(), obstacle.id, oldXP, obstacle.rewardXP,
                player->GetRSSkillXP(Player::RS_Skill::Agility));
        }, beginTraversal);
    if (!accepted)
    {
        TC_LOG_INFO("scripts", "WarscapeAgility: attempt roll failed player={} obstacle={} roll={} chance={}",
            player->GetGUID().ToString(), obstacle.id, roll, obstacle.successChancePercent);
        return { WarscapeAgilityTraversal::StartStatus::RollFailed, 0 };
    }

    sessions.emplace(map, TraversalSession{ player->GetGUID(), player->movespline->GetId(), 0, timeoutMs });
    TC_LOG_INFO("scripts", "WarscapeAgility: attempt accepted player={} obstacle={} spline={} level={} chance={}",
        player->GetGUID().ToString(), obstacle.id, player->movespline->GetId(),
        player->GetRSSkillLevel(Player::RS_Skill::Agility), obstacle.successChancePercent);
    return { WarscapeAgilityTraversal::StartStatus::Started, obstacle.rewardXP };
}
}

WarscapeAgilityTraversal::StartResult WarscapeAgilityTraversal::Start(Player* player, Route route)
{
    if (route == Route::NorthshireLog)
        return StartObstacle(player, OBSTACLES.front());

    if (!player || !player->GetSession() || !player->IsInWorld() || !player->IsAlive() ||
        player->GetMapId() != TEST_MAP_ID || player->GetMap()->GetInstanceId() != 0 ||
        player->IsInCombat() || player->IsInFlight() || player->GetVehicle() || player->IsMounted())
        return { StartStatus::Rejected, 0 };

    std::vector<G3D::Vector3> path;
    path.emplace_back(START_X, START_Y, 0.0f);
    path.emplace_back(END_X, END_Y, END_Z);
    if (!IsValidRoute(path))
        return { StartStatus::Rejected, 0 };

    float const dx = player->GetPositionX() - START_X;
    float const dy = player->GetPositionY() - START_Y;
    if (dx * dx + dy * dy > MAX_START_DISTANCE * MAX_START_DISTANCE)
        return { StartStatus::Rejected, 0 };

    SessionMap& sessions = Sessions();
    Map* const map = player->GetMap();
    auto existing = sessions.find(map);
    if (existing != sessions.end())
    {
        if (existing->second.playerGuid != player->GetGUID())
            return { StartStatus::Rejected, 0 };
        if (player->movespline->GetId() == existing->second.splineId && !player->movespline->Finalized())
            return { StartStatus::Rejected, 0 };
        sessions.erase(existing);
    }

    std::function<void(Movement::MoveSplineInit&)> initializer = [path = std::move(path)](Movement::MoveSplineInit& init)
    {
        init.Path() = path;
        init.SetVelocity(4.5f);
    };
    player->GetMotionMaster()->LaunchMoveSpline(std::move(initializer), TRAVERSAL_MOTION_ID,
        MOTION_PRIORITY_HIGHEST, POINT_MOTION_TYPE);
    sessions.emplace(map, TraversalSession{ player->GetGUID(), player->movespline->GetId(), 0, MAX_TRAVERSAL_MS });
    return { StartStatus::Started, 0 };
}

WarscapeAgilityTraversal::StartResult WarscapeAgilityTraversal::StartFromGameObject(Player* player, uint32 gameObjectEntry)
{
    ObstacleDefinition const* obstacle = FindObstacleByEntry(gameObjectEntry);
    if (!obstacle)
    {
        TC_LOG_INFO("scripts", "WarscapeAgility: unregistered obstacle interaction player={} entry={}",
            player ? player->GetGUID().ToString() : "unknown", gameObjectEntry);
        return { StartStatus::Rejected, 0 };
    }

    StartResult const result = StartObstacle(player, *obstacle);
    if (result.status == StartStatus::Rejected)
        TC_LOG_INFO("scripts", "WarscapeAgility: attempt rejected player={} obstacle={} level={} position=({:.3f},{:.3f},{:.3f})",
            player ? player->GetGUID().ToString() : "unknown", obstacle->id,
            player ? player->GetRSSkillLevel(Player::RS_Skill::Agility) : 0,
            player ? player->GetPositionX() : 0.0f, player ? player->GetPositionY() : 0.0f,
            player ? player->GetPositionZ() : 0.0f);
    return result;
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
    new go_warscape_agility_obstacle();
}
