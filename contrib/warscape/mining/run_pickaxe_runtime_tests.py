"""Compile actual Mining selection/show/stop methods against a small player fixture.

This exercises server callbacks, not the client renderer or an in-game session.
Generated code, CMake files and binaries stay in the requested artifact directory.
"""
import argparse
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
CMAKE = Path(r'C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe')


def function(source, signature):
    start = source.index(signature)
    opening = source.index('{', start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


PREFIX = r'''
#include "WarscapeMiningTools.h"
#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <vector>
using uint8 = std::uint8_t;
using uint16 = std::uint16_t;
using uint32 = std::uint32_t;
int checks = 0;
#define CHECK(x) do { ++checks; if (!(x)) throw std::runtime_error(#x); } while (0)
constexpr uint8 MainHandEquipmentSlot = 15;
constexpr uint8 INVENTORY_SLOT_BAG_0 = 255;
constexpr uint16 PLAYER_VISIBLE_ITEM_1_ENTRYID = 1000;
constexpr uint32 EMOTE_STATE_WORK_MINING = 233, EMOTE_STATE_NONE = 0;
struct ObjectGuid { uint32 value = 0; bool IsEmpty() const { return !value; } void Clear() { value = 0; } };
struct Item { uint32 entry; uint32 enchant; };
struct Rock { ObjectGuid guid; ObjectGuid GetGUID() const { return guid; } };
struct Player {
    enum class RS_Skill { Mining };
    uint8 level = 1;
    std::vector<Item> carried;
    Item *equipped = nullptr;
    uint32 visible = 0, enchant = 0, emote = EMOTE_STATE_WORK_MINING;
    uint8 GetRSSkillLevel(RS_Skill) const { return level; }
    Item* GetItemByEntry(uint32 entry) {
        for (auto& item : carried) if (item.entry == entry) return &item;
        return equipped && equipped->entry == entry ? equipped : nullptr;
    }
    Item* GetItemByPos(uint8 bag, uint8 slot) {
        CHECK(bag == INVENTORY_SLOT_BAG_0 && slot == MainHandEquipmentSlot); return equipped;
    }
    void SetVisibleItemSlot(uint8 slot, Item* item) {
        CHECK(slot == MainHandEquipmentSlot);
        visible = item ? item->entry : 0; enchant = item ? item->enchant : 0;
    }
    uint32 GetUInt32Value(uint16 field) {
        CHECK(field == PLAYER_VISIBLE_ITEM_1_ENTRYID + MainHandEquipmentSlot * 2); return visible;
    }
    uint32 GetEmoteState() const { return emote; }
    void SetEmoteState(uint32 value) { emote = value; }
};
Player* online = nullptr;
int released = 0;
namespace ObjectAccessor { Player* FindPlayer(ObjectGuid) { return online; } }
void ReleaseMiningSession(ObjectGuid player, ObjectGuid rock) { CHECK(player.value == 1 && rock.value); ++released; }
'''

FIXTURE = r'''
struct MiningFixture {
    Rock* me;
    ObjectGuid _minerGuid{1};
    uint32 _attemptTimer = 123;
    Warscape::MiningPickaxe const* _selectedPickaxe = nullptr;
    bool _miningToolVisualActive = false;
'''

MAIN = r'''
};
int main() {
    // Exhaustive carried combinations at every supported attained level.
    for (uint8 level = 0; level <= 99; ++level) for (unsigned mask = 0; mask < 16; ++mask) {
        Player player; player.level = level;
        Warscape::MiningPickaxe const* expected = nullptr;
        for (unsigned i = 0; i < 4; ++i) if (mask & (1u << i)) {
            auto const& candidate = Warscape::MiningPickaxes[i];
            player.carried.push_back({candidate.ItemEntry, 0});
            if (level >= candidate.MiningLevel && (!expected || candidate.IntervalMs() < expected->IntervalMs())) expected = &candidate;
        }
        CHECK(MiningFixture::SelectPickaxe(&player) == expected);
    }
    for (auto const& ore : OreConfigs) for (auto const& tier : Warscape::MiningPickaxes) {
        Rock rock{{ore.activeEntry}};
        Player player; player.level = tier.MiningLevel;
        Item sword{1234, 99}; player.equipped = &sword;
        player.carried.push_back({tier.ItemEntry, 7});
        online = &player;
        MiningFixture fixture; fixture.me = &rock;
        fixture._selectedPickaxe = MiningFixture::SelectPickaxe(&player);
        CHECK(fixture._selectedPickaxe == &tier);
        fixture.ShowMiningTool(&player);
        CHECK(player.visible == tier.ItemEntry && player.enchant == 7);
        CHECK(player.equipped == &sword); // Tool remains in carried inventory.
        fixture.StopMining();
        CHECK(player.visible == sword.entry && player.enchant == sword.enchant);
        CHECK(player.emote == EMOTE_STATE_NONE && fixture._minerGuid.IsEmpty());
        CHECK(!fixture._selectedPickaxe && !fixture._miningToolVisualActive && !fixture._attemptTimer);

        // Restore current equipment if it changed after the visual override.
        Item replacement{5678, 77};
        fixture._minerGuid = {1}; fixture._selectedPickaxe = &tier;
        fixture.ShowMiningTool(&player); player.equipped = &replacement;
        fixture.StopMining();
        CHECK(player.visible == replacement.entry && player.enchant == 77);

        // Originally unarmed must return to no weapon/enchant.
        player.equipped = nullptr;
        fixture._minerGuid = {1}; fixture._selectedPickaxe = &tier;
        fixture.ShowMiningTool(&player); fixture.StopMining();
        CHECK(player.visible == 0 && player.enchant == 0);

        // An equipment operation already replaced our visible override: preserve it.
        fixture._minerGuid = {1}; fixture._selectedPickaxe = &tier;
        fixture.ShowMiningTool(&player); player.SetVisibleItemSlot(15, &replacement);
        fixture.StopMining();
        CHECK(player.visible == replacement.entry && player.enchant == 77);

        // Tool removed before visual application and logout are safe.
        fixture._minerGuid = {1}; fixture._selectedPickaxe = &tier; player.carried.clear();
        fixture.ShowMiningTool(&player); CHECK(!fixture._miningToolVisualActive);
        online = nullptr; fixture.StopMining(); CHECK(fixture._minerGuid.IsEmpty());
    }
    CHECK(released == 15 * 4 * 5);
    std::cout << "Actual selection/show/stop callbacks: " << checks << " checks passed across all 15 ores and 4 tools.\n";
}
'''


def run(output):
    source = (ROOT / 'src/server/scripts/Custom/warscape_copper_mining.cpp').read_text()
    config = source[source.index('struct OreConfig\n'):source.index('constexpr bool OreConfigsAreSafe')]
    methods = '\n'.join(function(source, name) for name in (
        'static Warscape::MiningPickaxe const* SelectPickaxe(Player* player)',
        'void ShowMiningTool(Player* player)', 'void StopMining()'))
    output.mkdir(parents=True, exist_ok=True)
    (output / 'main.cpp').write_text(PREFIX + config + FIXTURE + methods + MAIN)
    includes = (ROOT / 'src/server/game/Entities/Unit').as_posix()
    (output / 'CMakeLists.txt').write_text('cmake_minimum_required(VERSION 3.20)\n'
        'project(PickaxeCallbacks LANGUAGES CXX)\nadd_executable(PickaxeCallbacks main.cpp)\n'
        f'target_include_directories(PickaxeCallbacks PRIVATE "{includes}")\n'
        'target_compile_features(PickaxeCallbacks PRIVATE cxx_std_17)\n')
    with (output / 'build.log').open('w') as log:
        for args in ((str(CMAKE), '-S', str(output), '-B', str(output / 'build'), '-A', 'x64'),
                     (str(CMAKE), '--build', str(output / 'build'), '--config', 'Release', '--parallel', '2')):
            subprocess.run(args, stdout=log, stderr=subprocess.STDOUT, check=True)
    subprocess.run([str(output / 'build/Release/PickaxeCallbacks.exe')], check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args().output)
