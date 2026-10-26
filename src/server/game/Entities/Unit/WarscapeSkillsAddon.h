#ifndef WARSCAPE_SKILLS_ADDON_H
#define WARSCAPE_SKILLS_ADDON_H

#include "WarscapeSkills.h"
#include <string>
#include <string_view>

namespace Warscape
{
    inline constexpr char SkillsAddonPrefix[] = "WCSkills";
    inline constexpr std::array<char const*, SkillCount> SkillIds = {
        "attack", "strength", "defence", "hitpoints", "ranged", "magic", "prayer"
    };

    inline bool IsSkillsAddonMessage(std::string_view message)
    {
        return message.substr(0, 9) == "WCSkills\t";
    }

    // Read-only subscription: no target GUID, command or writable skill input.
    inline std::string ParseSkillsSubscription(std::string_view message)
    {
        constexpr std::string_view header = "WCSkills\tHELLO|1|";
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

    inline std::string SkillsRow(std::string const& header, char const* id, SkillProgress const& skill)
    {
        // '-' reserves effective level for future boosts; none exist today.
        return "S|" + header + "|" + id + "|" + std::to_string(skill.Level) + "|-|"
            + std::to_string(skill.XP) + "|" + std::to_string(XPForLevel(skill.Level)) + "|"
            + (skill.Level >= MaxSkillLevel ? "-" : std::to_string(XPForLevel(skill.Level + 1)));
    }
}

#endif
