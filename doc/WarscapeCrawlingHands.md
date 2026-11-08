# Crawling Hand custom-model checkpoint

Implemented on 8 November 2026 using the three friend-supplied assets and the existing enemy catalogue, monster profiles, combat formula, native AggressorAI and weighted loot runner. No custom client executable/memory-layout or object-lifecycle code changed. Source: [OSRS Wiki Crawling Hand](https://oldschool.runescape.wiki/w/Crawling_Hand), fetched as raw Wiki API wikitext on 8 November; SHA256 is recorded in crawling_hands.json. Source provenance/asset hashes are in assets/crawling_hand/README.md and manifest.json.

## Variants

| Warscape entry | OSRS NPC | Combat level | Attack / Strength / Defence | Hitpoints | Max hit | Source Slayer XP |
|---|---|---|---|---|---|---|
|902600|450|7|7 / 3 / 3|15|1|12|
|902601|448|8|8 / 4 / 4|16|1|16|
|902602|449|8|8 / 4 / 4|16|1|16|
|902603|451|8|8 / 4 / 4|16|1|16|
|902604|452|8|8 / 4 / 4|16|1|16|
|902605|453|12|11 / 7 / 7|19|2|19|
|902606|454|12|11 / 7 / 7|19|2|19|

All seven live source variants: non-aggressive undead, Crush, four ticks/2.4 seconds, Ranged/Magic1, zero source combat bonuses, poison susceptibility. Source Slayer5/XP and respawn15ticks are catalogue metadata; Slayer training/gates and exact persistent-spawn timer policy remain outside this checkpoint. Source unused NPC455/456/457 and superior Crushing hand excluded. No permanent map placements were guessed.

One white-hand custom model serves all seven; level12 variants use scale1.35, others1. Custom display40000/model4000, with native Ghoul sound metadata as a stand-in. Radius0.7, reach1 yard; collision width1.88/height1.61 based on supplied model bounds. Sizes/reach are prototype WoW tuning, not an exact OSRS tile conversion. Idle/death/walk/run/attack entries and embedded animation flags checked. Visual scale, grounding, selection, reach, sounds and actual clip playback remain manual acceptance.

## Loot

Bones always. Main table: Leather gloves21/128; Purple/Yellow/Red/Teal gloves2/128 each; Gold ring3/128; Sapphire/Emerald rings2/128 each; Nothing53/128; Coins8 at24/128; Energy potion(4)13/128; gem table2/128. Trophy Crawling hand (item) independently1/500, including on a Nothing main roll. Existing gem-table helper preserves no-wealth/surface/pre-Legends policy: Nature talisman substitutes conditional mega-rares. Underground Chaos/location, wealth, quest, collection-log/taxidermy and superior/task systems remain future.

New collectibles902592-902600 use native icons; the glove colours are distinct item names sharing a native glove icon. Gloves/rings are not usable gear, potion is not a new consumable, and trophy has no taxidermy action. Original source items and old loot remain unchanged. Creature902600 and trophy item902600 have separate native table/command namespaces; use `.npc add` versus `.additem` appropriately.

## Test in game

Fully exit and reopen C:\Wrath of the Lich King\Wow.exe to load the new patch. For an open known test area use `.tele NorthshireValley`; no permanent creature placements are added. Move to clear ground. Spawn one at a time:

```
.npc add temp loot 902600
.npc add temp loot 902601
.npc add temp loot 902602
.npc add temp loot 902603
.npc add temp loot 902604
.npc add temp loot 902605
.npc add temp loot 902606
```

Use `.gm off` before combat. Check visible textured hand, sensible scale/ground contact, idle/walk/chase/attack/hit/death, selection/reach and sound behaviour. Hands should remain passive until attacked, then retaliate; level12 should be larger and stronger. Check normal combat XP, guaranteed Bones every kill and main loot across repeated kills. Ordinary drops/trophy can coincide; trophy is rare, so a short run cannot establish its rate. Automated exact marginal tests cover the probabilities. Confirm earlier enemies/gear still work. Report visual clipping/sliding/grounding separately from combat or loot failures. No automated client gameplay was performed.

## Automated and deployment evidence

145 Python tests, focused Debug C++ matrices, immutable-release/header regeneration check, RelWithDebInfo worldserver build and full installed-model capability audit passed. New tests cover all source IDs/stats, exact main/gem/trophy marginals and pairing, additive model metadata, asset dependency hashes/embedded clips, DBC preservation and collision refusal. Existing C++ expected catalogue count updated to351 entries/95 families.

Migration2026_11_08_14_world.sql applied and verified with db.py after permissions/status/precondition/hash review, zero online players, stopped servers and fresh verified world backup. Only new family, seven creatures/profiles/bindings, nine collectibles, loot outcomes and custom model-info row added; metadata updates target only these new entries. No character migration. All17 preservation hashes match (existing world data, model/item profiles, skills, inventory instances/links and wallets).

World backup: C:\WarscapeBackups\world_20261108T132652_826006Z_1738147f.sql; SHA256 c7422fbd0b0f3e6cdbcf31d57a2ccc6dbba0594bad11e434b1af4eb192642c49. Backup completed/verified; restore untested. Runtime backup: C:\WarscapeBackups\CrawlingHand-20261108-deploy.

Deployed matching EXE/PDB, runtime Item/CreatureDisplayInfo/CreatureModelData DBCs, and verified Wrath client's Data/enUS/patch-enUS-Z.MPQ. Existing DBC records/string offsets and unrelated MPQ payloads preserved; custom source assets byte-identical. Client was closed during installation. Server ready, auth/world ports listening, DB verification passed, no new Crawling Hand/model startup errors. Existing unrelated native warnings remain. User gameplay acceptance pending.

## Rollback

Stop servers/updaters with players offline. Backed-up binary/PDB, three runtime DBCs and client patch form the previous coordinated runtime set. Before restoring it, check for new spawned creatures or character-owned new items: rolling back client records while those references remain is unsafe. Prefer retaining additive asset/DBC definitions and leaving new templates dormant when reverting runtime logic. Do not delete inventories, restore character data, edit applied migration hashes or remove world rows in place. A full world restore would discard later changes and requires separate review; backup restore has not been rehearsed.

## Reproduction

Use the existing enemy asset virtual environment for packaging/model audit; source tests use Python3.13:

```
py -3.13 contrib/warscape/enemies/compile.py --check
py -3.13 contrib/warscape/enemies/run_checks.py
cmake --build build --config RelWithDebInfo --target worldserver -- /m
work/enemies-venv/Scripts/python.exe contrib/warscape/enemies/custom_creatures.py --client "C:\Wrath of the Lich King" --server-data Server/data --catalogue contrib/warscape/enemies/crawling_hands.json --manifest contrib/warscape/enemies/assets/crawling_hand/manifest.json --output work/crawling-hand-assets
```

Preparation requires a fresh output directory and pre-install inputs; it intentionally refuses existing IDs/asset paths after installation. Use backed-up pre-install inputs in an isolated directory for reproduction, not live rollback. Existing release SQL/specifications remain immutable.
