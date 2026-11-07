"""Run catalogue regression checks without changing the worldserver build configuration."""
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
out=ROOT/'work/enemy-catalogue-checks';out.mkdir(parents=True,exist_ok=True)
def run(args):subprocess.run([str(x) for x in args],cwd=ROOT,check=True)
run([sys.executable,HERE/'compile.py','--check'])
run([sys.executable,'-m','unittest','discover','-s',HERE,'-p','test_catalogue.py','-v'])
(out/'CMakeLists.txt').write_text('cmake_minimum_required(VERSION 3.20)\nproject(EnemyChecks LANGUAGES CXX)\nadd_executable(EnemyChecks "'+(HERE/'catalogue_checks.cpp').as_posix()+'")\ntarget_compile_features(EnemyChecks PRIVATE cxx_std_17)\ntarget_include_directories(EnemyChecks PRIVATE "'+(ROOT/'src/server/game/Entities/Unit').as_posix()+'")\n')
run(['cmake','-S',out,'-B',out/'build'])
run(['cmake','--build',out/'build','--config','Debug'])
run([out/'build/Debug/EnemyChecks.exe'])
print('PASS: source validation, family tiers, empty loot, exhaustive Goblin selection and combat formula checks')
