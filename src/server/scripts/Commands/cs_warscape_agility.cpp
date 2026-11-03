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

                if (!WarscapeAgilityTraversal::Start(player, selectedRoute))
                    handler->SendSysMessage(selectedRoute == WarscapeAgilityTraversal::Route::NorthshireLog
                        ? "AGI-003A: stand within 3 yards of the measured Northshire approach on map 0; the route requires a living GM outside combat, flight, mount, or vehicle states, with no route active in this map instance."
                        : "AGI-001B: stand at the Northshire Abbey test start on map 0; the route is GM-only and unavailable while dead, mounted, in combat, or already active.");
                else
                    handler->SendSysMessage(selectedRoute == WarscapeAgilityTraversal::Route::NorthshireLog
                        ? "AGI-003A: measured Northshire log route started. Watch the descent and collision; use .agi stop to interrupt."
                        : "AGI-001B: automatic player spline started. Use .agi stop to interrupt.");
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
