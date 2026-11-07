#ifndef WARSCAPE_CURRENCY_H
#define WARSCAPE_CURRENCY_H

#include <algorithm>
#include <cstdint>

namespace Warscape
{
constexpr std::uint32_t CoinsItem = 902006;
constexpr std::uint32_t CoinStackLimit = 2147483647;

inline std::uint32_t ItemStackLimit(std::uint32_t entry, std::int32_t configured)
{
    // Keep TrinityCore's unlimited-stack sentinel behaviour for every other item.
    if (entry == CoinsItem && configured == 2147483647)
        return CoinStackLimit;
    return configured <= 0 || configured == 2147483647 ? 2147483646u : std::uint32_t(configured);
}

inline std::uint32_t MergeCoinCount(std::uint32_t current, std::uint32_t incoming, std::uint32_t maximum)
{
    return current < maximum ? std::min(incoming, maximum - current) : 0;
}

inline std::uint32_t LootStackCount(std::uint32_t count, std::uint32_t size)
{
    // Division first avoids overflow in the usual (count + size - 1) formula.
    return size ? count / size + (count % size != 0) : 0;
}
}
#endif
