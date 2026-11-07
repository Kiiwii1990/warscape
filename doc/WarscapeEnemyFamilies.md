# Enemy families: Cows and Rats release

Current expansion: [Elf/Aviansie/Hobgoblin/Suqah checkpoint](WarscapeElvesAviansieSuqah.md).
The preceding [Lizard/Scarab/Druid/Dwarf checkpoint](WarscapeOrderedEnemyBatch.md)
was user-confirmed working with drops.
The preceding [two-enemy spectral checkpoint](WarscapeSpectralEnemies.md) was
user-confirmed working with drops.
The preceding [70-variant Slayer and melee prototype batch](WarscapeSlayerPrototypesBatch.md)
has its own acceptance checklist.
The preceding [57-variant giants/demons batch](WarscapeGiantsDemonsBatch.md) was
user-confirmed working with drops.
The previous [53-variant martial batch](WarscapeMartialFamiliesBatch.md) was user-confirmed
with drops.
The previous [39-variant dungeon batch](WarscapeDungeonHumanoidBatch.md) was user-confirmed
working with drops.
The previous [28-variant coastal batch](WarscapeCoastalWildlifeBatch.md) was user-confirmed
working with correct drops.
The user confirmed both the Cow/Rat release and the
[previous 21-variant wildlife batch](WarscapeWildlifeBatch.md) with correct drops. The stock Cow attack-clip
gap remains documented; no custom animation was added.

## Confirmed design

Kieran's notes supplied by the user on 7 November 2026 establish shared enemy
families with level/role subcategories, distinct loot tables and potentially
different WoW models. Future Slayer tasks target the family, allowing a choice of
subcategory. The 96 supplied model directions are preserved in
`contrib/warscape/enemies/family-roadmap.json`. Most are planned, not implemented.
The user confirmed that the first Goblin works and drops Bones; do not read that
as confirmation of all rare-drop or interruption paths.

This release implements six additional melee variants and registers the existing
Goblin in the same family metadata. It adds no permanent world populations or
Slayer task engine. Those systems can refer to the stable family IDs below.

| Entry | Family ID / name | Subcategory | OSRS combat level | Displayed HP | Guaranteed main loot |
| --- | --- | --- | ---: | ---: | --- |
| 901000 | 1 / Goblins | regular_2 | 2 | 50 | Existing Bones + weighted F2P pool |
| 901010 | 2 / Cows | regular | 2 | 80 | Cowhide, Raw beef, Bones |
| 901020 | 3 / Rats | regular | 1 | 20 | None |
| 901021 | 3 / Rats | stronghold | 1 | 20 | Bones |
| 901022 | 3 / Rats | giant_3 | 3 | 50 | Bones, Raw rat meat |
| 901023 | 3 / Rats | giant_6 | 6 | 100 | Bones, Raw rat meat |
| 901024 | 3 / Rats | giant_26 | 26 | 250 | Bones |

Sources, retrieved 7 November with SHA-256 provenance in `farm_animals_rats.json`:
[OSRS Wiki Cow](https://oldschool.runescape.wiki/w/Cow),
[Rat](https://oldschool.runescape.wiki/w/Rat), and
[Giant rat](https://oldschool.runescape.wiki/w/Giant_rat).
The distinction between ordinary and Stronghold Rats is deliberate. Quest-only
rat tails/bones, wilderness looting bags and tertiary clues are not unconditional
loot and are not awarded by this prototype.

## Combat and appearance

All new variants use the existing Warscape profile, melee, HP scale and damage-XP
paths. Every stat, combat bonus, attack interval and maximum-hit check comes from
the selected Wiki variant. All attack every four ticks (2.4 seconds); ordinary
Rats have source max hit zero, reproduced by Strength bonus -53. Giant Rat maximum
hits are 1, 1 and 3 for levels 3, 6 and 26 respectively. Existing Warscape damage
variation remains active around the tenfold displayed damage scale.

Cow display 1060 is the stock Bess/farm-cow model. Rat display 1141 is the stock
Black Rat. Normal Rats use scale 1; Giant Rats use 1.5, 2 and 2.7 to distinguish
tiers. Every entry is a Beast rather than a critter, so combat/death and XP paths
remain available. Cows and small Rats are neutral; Giant Rats are hostile using
native AggressorAI. WoW aggression/leash rules currently apply, including the
absence of OSRS's player-combat-level aggression cutoff and ten-minute tolerance.

Read-only model checks verified stock standing/walking/running/death sequences.
The Rat has unarmed attack sequences. **The stock Cow has no attack animation**:
it can retaliate mechanically, but retains the intended Bess appearance while
visible attack animation work remains outstanding. `.rs enemy` reports this gap.
Native audio is inherited from the stock display; visual/audio acceptance is manual.
No client executable, object-field layout or allocation code changed.

Attack style, source poison resistance, Slayer XP and respawn ticks are recorded
as metadata. They do not implement Slayer awards, poison/venom mechanics, or OSRS
attack-style-specific player equipment defence. The current Warscape melee
accuracy path remains in use. Permanent spawn authors will need to map 600ms
source respawn ticks to native whole-second spawn timers; the ordinary Rat's
1.2-second source timer cannot be represented exactly by that schema.

## Family, combat, loot and spawn ownership

- `warscape_enemy_family`: stable family ID/key, display name, Kieran model direction.
- `warscape_enemy_variant`: creature entry, family, subcategory and source provenance;
  also source melee style, max hit, Slayer XP, poison resistance and respawn ticks.
- `creature_template`: display, scale, neutral/hostile faction, native melee AI,
  displayed level and default loot linkage.
- `warscape_monster_profile` / `warscape_monster_template`: loaded combat stats.
- `warscape_monster_attack_speed`: attack cadence.
- `creature_loot_template`: native corpse ownership/distribution and item quantities.
- `creature.id`: permanent spawn placement, unchanged by this release.
- `farm_animals_rats.json`: reviewed release facts, per-variant guaranteed/main loot,
  model choices and explicit known animation capabilities.

For example, contributors can inspect family membership with:

```sql
SELECT f.name, v.subcategory, v.creature_entry, c.name
FROM warscape_enemy_variant v
JOIN warscape_enemy_family f ON f.id = v.family_id
JOIN creature_template c ON c.entry = v.creature_entry
ORDER BY f.id, v.creature_entry;
```

The shared runtime header is generated from both releases. The first Goblin's
128-slot weights, native loot records and item IDs remain unchanged. New loot
supports multiple guaranteed items and explicitly empty outcomes, so ordinary
Rats do not accidentally receive Bones. Both Rat tiers reuse deployed Bones item
902000. New entries 902015 Cowhide, 902016 Raw beef and 902017 Raw rat meat remain
collectibles: crafting, food effects and their economies are not implemented yet.

The family database metadata mirrors the generated catalogue. `.rs enemy` reads
family/source labels from the compiled registry and live combat stats from the
existing loaded profile system; it does not issue a database query per click.
Changes to metadata/loot definitions require a generated build plus a new release
migration. Do not edit applied SQL or rehash it to bypass migration checks.

## Contributor workflow

1. Review sourced facts and unsupported mechanics; update a new release snapshot.
   Existing `goblins.json` and `2026_11_07_00_world.sql` remain immutable.
2. The compiler checks both immutable SQL/verification releases and rebuilds the
   combined runtime header. Run `py contrib/warscape/enemies/compile.py --check`.
   Initial creation of new release files uses `--write`; changed existing SQL or
   verification files are refused. Add another release generator for future packs,
   rather than modifying this release after it has been applied.
3. Run `py contrib/warscape/enemies/run_checks.py`. Tests cover invalid sources,
   shared-ID preservation, loot collisions, all old Goblin roll outcomes, empty
   Rat loot, family membership, Cow drops and Giant Rat progression.
4. With asset-tool dependencies installed, run `check_models.py --client <game>`.
   Prepare new item assets with `build_assets.py --catalogue
   contrib/warscape/enemies/farm_animals_rats.json --client <game>
   --server-data <runtime-data> --output <new-staging-directory>`.
   All prior DBC rows, strings and unrelated locale-patch payloads are preserved.
5. Build RelWithDebInfo worldserver. Inspect status and permissions using `db.py`;
   stop servers/updaters and use its backup/apply/verify workflow for
   `2026_11_07_01_world.sql`. The generated verification checks the new family
   tables, every new creature/profile/loot/item row and all provenance rows.
6. Back up and deploy matching worldserver/PDB, server Item.dbc and client locale
   patch with the game closed; restart and check logs. Local targets remain
   `C:\Warscape\Server` and `C:\Wrath of the Lich King`.

This migration inserts family metadata, six new creatures/profiles/speeds, their
loot and three new collectible item definitions. It does not modify existing
creature templates, old Goblin loot, inventories or character XP. Source profile
IDs are 1010 and 1020-1024; native loot IDs reserved by this release are 901100,
901110 (empty, no native rows), 901120, 901130, 901140 and 901150.

Do not remove item/DBC records while inventories may contain collectibles. Rollback
requires a reviewed forward migration and preservation of player inventory data;
a world database restore is not routine rollback. Old binaries lack the combined
pool/family diagnostics, so do not spawn these entries under an older runtime.

## In-game acceptance

Restart the client to load the three new item records. Use a GM QA character on
open ground; spawn one creature at a time. The earlier Northshire QA location is:

```text
.go xyz -9066.463867 -199.568985 70.600822 0
.npc add temp loot 901010
```

Select it and use `.rs enemy` to inspect family and stats. Kill it and confirm
exactly Cowhide + Raw beef + Bones. Repeat the temporary spawn command with each
Rat entry from the table: regular Rats should have no loot; Stronghold Rats drop
Bones; level-3/6 Giants drop Bones + Raw rat meat; level-26 Giants drop Bones only.
The `loot` parameter retains the temporary corpse for 30 seconds. Giant Rats are
hostile and stronger tiers can kill a low-level player. Check Rat attack/death
presentation and the Cow's known missing attack animation, return-to-home behavior,
XP updates and persistence of new collectibles after relogging. Recheck the original
Goblin as a regression. Small manual samples do not validate the old rare-drop rates.

The remaining 93 family model directions are a roadmap. Ranged/caster variants,
conditional/tertiary loot, functional items/economy, Slayer tasks and persistent
world populations remain separate milestones.

## Deployment record - 7 November 2026

The RelWithDebInfo worldserver build passed. Ten Python source/guard tests and
isolated C++ checks passed, including every original Goblin roll, Rat zero-max-hit,
empty loot, family membership and Giant Rat tier outcomes. Model checks verified
Rat attack/death and explicitly detected the known Cow attack-clip gap.
The new migration applied through `db.py` and both enemy releases verified.
Startup reached ready state for authserver and worldserver, with no new enemy,
loot or item-record errors; the prior Mining/item-900500 warnings remain.
Client/server item records matched SQL displays. Every prior client/server DBC
row/string and unrelated MPQ payload was preserved and compared after installation.
At that deployment, new-family manual acceptance was pending. The user later
confirmed the release working with correct drops, as recorded above.

Verified world backup:
`C:\WarscapeBackups\world_20261107T071947_916937Z_9fb950ae.sql`.
Executable/PDB, server DBC and locale-patch backups:
`C:\WarscapeBackups\EnemyFamilies-20261107-deploy`.
