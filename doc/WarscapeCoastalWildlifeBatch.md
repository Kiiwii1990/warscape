# Coastal wildlife checkpoint: 28 variants, seven families

## Scope and source

The user confirmed the previous 21-variant batch with correct drops and asked for
an even larger batch from the updated Kieran model list. This checkpoint adds
28 distinct source variants, bringing the catalogue to 56 entries in 15 families.
Source IDs distinguish real appearance/location variants; flying Vulture state,
crab hidden/bloom states and water-only Crocodiles are not counted as extra enemies.
No permanent world spawns are installed.

Reviewed primary OSRS Wiki pages, retrieval date and raw SHA-256 provenance are
recorded in `contrib/warscape/enemies/coastal_wildlife.json`: Bird, Chicken,
Seagull, Duck, Vulture, Rock Crab, Sand Crab, Swamp Crab, Ammonite Crab, Crocodile,
Guard dog, Wild dog, Jackal, Monkey (monster), Snake and Terrorbird. The pack also
records the shared Wiki Gem drop table, Module:GemDropLines and Template:HerbDropLines.
Published combat stats, tick intervals, maximum hits and melee defence lanes use
the existing opt-in source-combat architecture. Previous 28 entries are unchanged.

| Entry | Variant | Combat | Displayed HP | Source max hit | Loot |
| --- | --- | ---: | ---: | ---: | --- |
| 901060 | Bird (OSRS jungle_1) | 5 | 50 | 1 | Bones |
| 901061 | Bird (OSRS jungle_2) | 11 | 100 | 2 | Bones |
| 901062 | Chicken (OSRS normal) | 1 | 30 | 0 | Bones, Raw chicken + main roll |
| 901063 | Chicken (OSRS miscellania) | 1 | 30 | 0 | Bones, Raw chicken + main roll |
| 901064 | Chicken (OSRS falador_farm) | 1 | 30 | 0 | Bones, Raw chicken + main roll |
| 901065 | Chicken (OSRS gordon_mary_farm) | 1 | 30 | 0 | Bones, Raw chicken + main roll |
| 901066 | Seagull (OSRS seagull_1) | 2 | 60 | 0 | Bones |
| 901067 | Seagull (OSRS seagull_2) | 3 | 100 | 0 | Bones |
| 901068 | Duck (OSRS duck_male) | 1 | 30 | 0 | None |
| 901069 | Duck (OSRS duck_female) | 1 | 30 | 0 | None |
| 901070 | Vulture (OSRS vulture_landed) | 31 | 100 | 5 | Bones |
| 901071 | Rock Crab (OSRS rock_crab) | 13 | 500 | 1 | NoneMain roll |
| 901072 | Sand Crab (OSRS sand_crab) | 15 | 600 | 1 | NoneMain roll |
| 901073 | Swamp Crab (OSRS swamp_crab) | 55 | 750 | 1 | NoneMain roll |
| 901074 | Ammonite Crab (OSRS ammonite_crab) | 25 | 1000 | 1 | NoneMain roll |
| 901075 | Crocodile (OSRS land_63) | 63 | 620 | 6 | Bones + main roll |
| 901076 | Guard dog (OSRS guard_normal) | 44 | 490 | 5 | Bones |
| 901077 | Guard dog (OSRS guard_hosidius) | 44 | 490 | 5 | Bones |
| 901078 | Wild dog (OSRS wild_63) | 63 | 620 | 6 | Bones |
| 901079 | Jackal (OSRS jackal_21) | 21 | 270 | 3 | Bones |
| 901080 | Monkey (OSRS common_3) | 3 | 60 | 1 | Monkey bones |
| 901081 | Monkey (OSRS mos_le_harmless_3) | 3 | 60 | 1 | Monkey bones |
| 901082 | Snake (OSRS regular_5) | 5 | 60 | 1 | Bones |
| 901083 | Snake (OSRS varlamore_5) | 5 | 60 | 1 | Bones |
| 901084 | Snake (OSRS sailing_5) | 5 | 60 | 1 | Bones |
| 901085 | Terrorbird (OSRS appearance_1) | 28 | 340 | 3 | Bones |
| 901086 | Terrorbird (OSRS appearance_2) | 28 | 340 | 3 | Bones |
| 901087 | Terrorbird (OSRS appearance_3) | 28 | 340 | 3 | Bones |

## Loot and gameplay policies

- Chickens always drop Bones and Raw chicken, plus 5 Feathers at 64/128 or
  15 Feathers at 32/128; the remaining 32/128 adds no feathers. Maximum hit is zero.
- Ducks have no ordinary loot and hit zero. Jungle birds, Seagulls, Vulture,
  Dogs, Snakes and Terrorbirds drop Bones; Monkey uses pre-Tai Bwo Wannai Trio
  Monkey bones. Corpse/paw/wing/spine quest rewards are not granted unconditionally.
- Training Crabs include complete ordinary main tables and the 1/128 gem-table
  branch, using exact integer weights with denominator 16384. Rock/Sand/Swamp/
  Ammonite Crabs have no guaranteed Bones. Swamp Crab's Bloom-only three fungi
  are omitted; its normal 2/128 single-fungus main drop is present.
- Ammonite Crab Calcite/Pyrophosphite are one paired 1/128 outcome. Both appear
  together. Quantity ranges remain native uniform min/max rolls; the main-table
  probability is not expanded or rounded.
- Shared gem-table policy: members-style drops for all Warscape accounts, no
  Ring of Wealth, surface Nature talisman, and pre-Legends quest state. The
  1/128 mega-rare branch becomes a Nature talisman; the table therefore has four
  talisman slots out of 128. Rune/Dragon spears and Shield left half do not drop.
  This is explicit prototype policy until location, equipment and quest gating
  exist; it is not a claim that all OSRS variants always drop Nature talismans.
- Only the land Crocodile (source 11582) is included: guaranteed Bones and a 1/20
  herb-table roll. The eleven herb weights are 32/24/18/14/11/8/6/5/4/3/3 out of
  128 within that branch, without using the Wiki's rounded display denominators.
  Water-only and amphibious variants are deferred, including conditional Bones.
- Crabs start exposed and aggressive: no rock/log disguise, waking, ten-minute
  tolerance reset or reburrowing. Native WoW leash/aggro remains. Guard dogs use
  the hostile policy for both variants; source aggression varies by location.
- Missing Snake respawns use the regular Snake's 30 ticks as metadata. Snake and
  Duck lack an explicit Slayer-XP field; HP is stored as reference only. Neither
  this reference nor any family metadata enables Slayer tasks/rewards.
- Clues, ensouled heads, quest drops, fossils, Wilderness/Slayer tertiary rolls and
  elemental weaknesses remain outside this checkpoint. This also excludes
  poisonous snakes, Slayer lizards, ridden tortoises and other special mechanics.

## Models and items

Native stock models follow Kieran's directions: kaliri/owl for jungle birds and
small duck stand-ins, carrion birds for Seagulls/Vulture, Chicken for Chickens,
Darkshore crabs, Dreadmaw crocolisk, Scarlet Tracking Hound (stock hyena asset),
small Stranglethorn gorillas, Adders and unsaddled Mulgore plainstriders.
Ducks/Seagulls are silhouette stand-ins, not custom OSRS models. Native bird flight
clips do not imply flight AI; all entries use the current ground melee navigation.
All newly selected models have stand/walk/run/attack/death clips in the verified
stock client. Actual appearance, sound and ground contact need user acceptance.

53 new collectibles (902022-902074) use existing stock item artwork. Prior items
are reused by identity, including Bones and Coins; collectibles retain the current
stackable, non-functional policy. No Prayer/cooking/crafting/equipment/currency
behaviour is introduced by these items. All prior DBC rows/strings and unrelated
locale-patch payloads must be preserved. No executable, memory layout, field map,
allocator, object lifetime or client source changes are included.

## Implementation and verification

The new immutable pack is `coastal_wildlife.json`, appended to `releases.json`.
`family_catalogue.py` supports optional `quantity_max` and `additional` items in
one selected outcome. Duplicate items and inverted/out-of-bounds counts are
rejected. The native server loot generator handles quantities and paired items;
there is no second custom runtime loot engine. Older SQL/specifications reproduce
byte-for-byte and were not rewritten. The new migration is
`2026_11_07_03_world.sql` with a generated verification specification. It inserts
seven families, 28 templates/profiles/speeds and 53 items; metadata updates touch
only newly inserted entries. It changes no schema or character data.

Creature entries are 901060-901087, profiles 1060-1087, family IDs 9-15 and native
outcome reservations 903000-905700 in steps of 100. Each pool is collision checked
against all earlier releases. No reservations are existing Blizzard entries.

Checks:

```text
py -3.13 contrib/warscape/enemies/run_checks.py
<asset-python> contrib/warscape/enemies/check_models.py --client <game>
cmake --build build --config RelWithDebInfo --target worldserver -- /m
```

The suite has 27 Python tests and isolated C++ checks. New coverage includes exact
Chicken rolls, empty Duck loot, paired minerals, native quantity ranges, invalid
paired/range inputs, Crab gem and Crocodile herb probabilities, and exhaustive
selection of all 16384 rolls for each Crab. Previous Goblin selection, source caps,
defence lanes and accepted-family fallback checks remain.

## In-game acceptance

Restart the stock game client to load the new collectible records. Teleport to
the existing test area, then spawn one creature at a time:

```text
.go xyz -9066.463867 -199.568985 70.600822 0
.npc add temp loot 901062
.rs enemy
```

Select the creature before `.rs enemy`. Use the full table above for entries.
Temporary loot-enabled corpses remain for 30 seconds. Confirm the displayed stats,
model/scale, melee cadence, HP, aggression, death animation and drops. Some entries
can kill low-level characters quickly.

1. Chicken 901062: Bones + Raw chicken every kill; Feathers may be 5, 15 or absent.
2. Duck 901068: zero maximum hit, no loot. Bird 901060 and Seagull 901066: Bones.
3. Crabs 901071-901074: high HP, low maximum hit; ordinary main rolls can be empty.
   Swamp Crab has high melee defence. Do not expect guaranteed Bones or Bloom fungi.
   The rare Calcite outcome must include Pyrophosphite, never separately.
4. Crocodile 901075: Bones every kill; herbs occasional. Small samples cannot prove
   a probability, including rare gems, herbs and paired minerals.
5. Guard dog 901076: Bones, hostile. Wild dog 901078: Bones, initially neutral.
6. Monkey 901080: Monkey bones. Snake 901082 and Terrorbird 901085: Bones.
7. Relog with new loot and check inventory/skill XP persistence. Recheck accepted
   Goblin/Cow/Rat and previous wildlife entries for regressions.

Manual gameplay acceptance of these 28 entries is pending. Automated checks and
successful startup do not establish visual, sound, collision or combat-feel proof.

## Rollback

Back up before migration/deployment through `db.py` with stopped writers. An export
integrity check is not a tested restoration. Routine rollback must not restore a
world backup or delete item records that players may own. Keep all prior and new
item records/patch payloads. Disable or remove only this batch's spawned test NPCs
if needed; there are no persistent spawns to clean. Deploy a compatible reviewed
binary together with its matching runtime catalogue, or prepare a new corrective
migration; never rewrite applied migration hashes or change player inventories.

## Deployment record - 7 November 2026

27 Python tests and isolated C++ checks passed, along with the RelWithDebInfo
worldserver build. All new models passed the native sequence audit. Both servers
started successfully, loading 59 monster profiles, 61 creature definitions and
57 speed overrides. The catalogue has 56 entries across 15 families. All four
enemy migrations pass postconditions; migration status has 35 applied, 6952
archived and none pending. No errors for the new creature/item/loot IDs appeared.
Existing Mining script-reference and item-900500 DBC warnings remain unrelated.

The stock game client was closed and no characters were online for deployment.
Matching worldserver binary/PDB, server Item.dbc and the merged client locale
patch were deployed and checksum verified. All 53 new client/server item records
match database displays. Every earlier DBC row/string and unrelated patch payload
was compared and preserved. New in-game acceptance is pending the user's test.

Fresh verified world backup (integrity checked, restore not tested):
`C:\WarscapeBackups\world_20261107T075802_633627Z_98f6d62d.sql`.
Previous binary/PDB/server DBC/client patch:
`C:\WarscapeBackups\Coastal-20261107-deploy`.
Prepared new assets: `C:\WarscapeBackups\Coastal-20261107-prepared`.

## User acceptance - next checkpoint

The user confirmed this 28-variant batch working with correct drops on
7 November 2026 and requested the next large batch. This records the reported
gameplay/drop result, without inferring statistical rare-drop or exhaustive
visual/navigation acceptance.
