"""Build and run production smelting methods with controlled engine-service fakes on Windows."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[3]
OUT=Path('C:/WoWDev/Artifacts/WarscapeBronze-20261101/runtime-checks')
CMAKE=Path('C:/Program Files/Microsoft Visual Studio/2022/Community/Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe')
s=(ROOT/'src/server/game/Entities/Player/Player.cpp').read_text()
methods=s[s.index('bool Player::HasWarscapeCraftingFocus'):]
half=s[s.index('void Player::AddRSSkillHalfXP'):s.index('Warscape::SkillUpdateResult Player::SetRSSkillLevel')]
g=(ROOT/'src/server/game/Grids/Notifiers/GridNotifiers.h').read_text();focus=g[g.index('    class GameObjectFocusCheck'):g.index('    // Find the nearest Fishing')]
h=(Path(__file__).with_name('smelting_harness.cpp')).read_text().replace('// PRODUCTION METHODS',methods+'\n'+half).replace('// NATIVE FOCUS PREDICATE',focus)
assert 'plrMover->CancelWarscapeSmelting();' in (ROOT/'src/server/game/Handlers/MovementHandler.cpp').read_text()
assert 'player->CancelWarscapeSmelting();' in (ROOT/'src/server/game/Combat/CombatManager.cpp').read_text()
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'main.cpp').write_text(h)
(OUT/'CMakeLists.txt').write_text('cmake_minimum_required(VERSION 3.20)\nproject(SmeltingChecks LANGUAGES CXX)\nadd_executable(SmeltingChecks main.cpp)\ntarget_compile_features(SmeltingChecks PRIVATE cxx_std_20)\ntarget_include_directories(SmeltingChecks PRIVATE "'+str(ROOT/'src/server/game/Entities/Unit').replace('\\','/')+'")\n')
subprocess.run([str(CMAKE),'-S',str(OUT),'-B',str(OUT/'build')],check=True)
subprocess.run([str(CMAKE),'--build',str(OUT/'build'),'--config','Release'],check=True)
subprocess.run([str(OUT/'build/Release/SmeltingChecks.exe')],check=True)
