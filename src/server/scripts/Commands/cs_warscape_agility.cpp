/*
 * This file is part of the TrinityCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 */

#include "ScriptMgr.h"
#include "Chat.h"
#include "World/WarscapeAgilityTraversal.h"
#include "WorldSession.h"

using namespace Trinity::ChatCommands;

namespace
{
    class WarscapeAgilityCommandScript final : public CommandScript
    {
    public:
        WarscapeAgilityCommandScript() : CommandScript("WarscapeAgilityCommandScript") { }

        ChatCommandTable GetCommands() const override
        {
            static ChatCommandTable commandTable =
            {
                { "agi", HandleAgilityCommand, rbac::RBAC_PERM_COMMAND_DEBUG, Console::No }
            };
            return commandTable;
        }

    private:
        static bool HandleAgilityCommand(ChatHandler* handler, Optional<std::string_view> action, Optional<std::string_view> route)
        {
            Player* player = handler->GetSession()->GetPlayer();
            if (!action || *action == "start")
            {
                WarscapeAgilityTraversal::Route selectedRoute = WarscapeAgilityTraversal::Route::StreamPrototype;
                if (route)
                {
                    if (*route != "log")
                    {
                        handler->SendSysMessage("Usage: .agi start [log] | .agi stop");
                        return false;
                    }
                    selectedRoute = WarscapeAgilityTraversal::Route::NorthshireLog;
                }

                WarscapeAgilityTraversal::StartResult const result = WarscapeAgilityTraversal::Start(player, selectedRoute);
                if (result.status == WarscapeAgilityTraversal::StartStatus::RollFailed)
                    handler->SendSysMessage("Agility Roll Failed");
                else if (result.status == WarscapeAgilityTraversal::StartStatus::Rejected)
                    handler->SendSysMessage(selectedRoute == WarscapeAgilityTraversal::Route::NorthshireLog
                        ? "AGI-003A: rejected. Stand within 30 horizontal yards of the measured approach point on map 0; Agility level 1 is required, and you must be alive, out of combat/flight/mount/vehicle, with no traversal active in this map instance."
                        : "AGI-001B: stand at the Northshire Abbey test start on map 0; the route is GM-only and unavailable while dead, mounted, in combat, or already active.");
                else if (selectedRoute == WarscapeAgilityTraversal::Route::NorthshireLog)
                    handler->PSendSysMessage("Agility Roll Succeeded: %u Agility XP awarded. Traversal started.", result.rewardXP);
                else
                    handler->SendSysMessage("AGI-001B: automatic player spline started. Use .agi stop to interrupt.");
                return true;
            }

            if (*action == "stop")
            {
                if (!WarscapeAgilityTraversal::Stop(player, true))
                    handler->SendSysMessage("AGI-001B: no traversal is active for this player.");
                else
                    handler->SendSysMessage("AGI-001B: traversal stopped and session cleaned up.");
                return true;
            }

            handler->SendSysMessage("Usage: .agi start [log] | .agi stop");
            return false;
        }
    };
}

void AddSC_warscape_agility_commandscript()
{
    new WarscapeAgilityCommandScript();
}
