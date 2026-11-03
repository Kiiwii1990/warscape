#ifndef WARSCAPE_SMELTING_H
#define WARSCAPE_SMELTING_H
#include <array>
#include <cstdint>
namespace Warscape
{
    constexpr std::uint32_t FurnaceFocus = 3;
    constexpr std::uint32_t AnvilFocus = 1;
    // Keep paired with the native client's forge 173063 centre radius.
    // Rebalance both client/server together; the focus search remains 10 yards.
    constexpr float DefaultFurnaceInteractionDistance = 4.0f;

    struct SmeltingIngredient
    {
        std::uint32_t Item = 0;
        std::uint32_t Count = 0;
    };

    // Stable recipe IDs also define the approved two-by-four UI order.
    // Disabled entries intentionally have no item, costs, levels, XP or timing.
    struct SmeltingRecipe
    {
        char const* Id;
        char const* Name;
        bool Implemented;
        std::uint32_t BarItem;
        std::array<SmeltingIngredient, 2> Ingredients;
        std::uint8_t SmithingLevel;
        std::uint32_t XPTenths;
        std::uint32_t DurationMs;
        bool Guaranteed;
    };

    inline constexpr std::array<SmeltingRecipe, 8> SmeltingRecipes = {{
        {"bronze", "Bronze", true, 900500, {{{2770, 1}, {900201, 1}}}, 1, 62, 3000, true},
        {"iron", "Iron", false, 0, {}, 0, 0, 0, false},
        {"steel", "Steel", false, 0, {}, 0, 0, 0, false},
        {"silver", "Silver", false, 0, {}, 0, 0, 0, false},
        {"gold", "Gold", false, 0, {}, 0, 0, 0, false},
        {"mithril", "Mithril", false, 0, {}, 0, 0, 0, false},
        {"adamant", "Adamant", false, 0, {}, 0, 0, 0, false},
        {"rune", "Rune", false, 0, {}, 0, 0, 0, false}
    }};

    // Preserve the existing Bronze engine's API and exact recipe behaviour.
    constexpr std::uint32_t BronzeCopperOre = SmeltingRecipes[0].Ingredients[0].Item;
    constexpr std::uint32_t BronzeTinOre = SmeltingRecipes[0].Ingredients[1].Item;
    constexpr std::uint32_t BronzeBar = SmeltingRecipes[0].BarItem;
    constexpr std::uint32_t BronzeXP = SmeltingRecipes[0].XPTenths;
}
#endif
