# Warscape Training Dummy

For timed, real-event melee measurements and compact chat reports, see
[the automated attack test](WarscapeAttackTest.md): `.rs attacktest <1-30 minutes>`.

This is a reusable development utility, not a gameplay stage or a balance change.
Creature entry `900001` uses the stock training-dummy model with a separate,
passive AI script. It is hostile/attackable, rooted, immune to displacement and
charm, and never attacks or moves to a victim. It has no loot, money, kill-credit
aliases, kill XP, weapon-skill gains, quests or spell-school immunity.

## Spawn, attack and remove

Start the installed servers from `C:\WoWDev\TrinityServer` and log into a GM QA
character with the normal NPC-add permission. Creating a permanent dummy also
uses that permission; removal requires NPC-delete permission.

```text
.rs dummy
```

This summons a temporary dummy approximately three yards ahead, in your phase.
Leave combat and transports before spawning. Select the dummy, switch `.gm off`
if needed for normal hostile targeting, and right-click/auto-attack as usual.
Use `.rs accurate`, `.rs aggressive`, `.rs defensive`, `.rs controlled`,
`.rs bonuses`, and the normal combat log to compare Stage 1G weapons and tiers.
Combat log damage is the calculated post-mitigation damage, not zero or a
one-HP-survival clamp. The dummy's health remains unchanged. Misses and zero
rolls remain normal; attack intervals, weapon switching and bonuses are unchanged.
It reports no melee/ranged/magic damage of its own and never retaliates.

To test accuracy, select the dummy and use:

```text
.rs dummy defence 50
```

The supported range is 1–99. Default Defence is 1 with zero equipment defence
bonus, using the existing OSRS melee hit formula. This is a per-dummy session
setting: it resets to 1 when the creature reloads or the server restarts.
It does not configure future ranged/magic accuracy formulas; those attacks keep
their currently implemented native rules. Their ordinary damage paths still hit
the protected target; no ranged/magic/gem gameplay is added by this utility.

Stop auto-attacking and cancel damaging periodic effects when done. Combat clears
after approximately 15 seconds without damage; ongoing melee attacks remain in
combat even through a run of misses. Select the dummy to remove it:

```text
.rs dummy remove
```

Only a selected Warscape Training Dummy can be removed by this command. Ordinary
creatures are refused. Temporary summons disappear on removal, grid unload or
restart. To save one in the world database instead:

```text
.rs dummy permanent
```

Permanent spawns are allowed on non-instance maps, use normal TrinityCore spawn
storage, and return at the saved position after server restart. Select one and
use `.rs dummy remove` to delete its saved spawn as well as despawn it. These
explicit GM commands edit spawn content; the migration itself creates no map
spawns. Avoid making permanent test content in player-facing areas.

## Damage and reward isolation

The stock `npc_training_dummy` script zeroes incoming damage and is left intact.
The Warscape script leaves damage untouched. An entry-scoped guard in
`Unit::DealDamage` returns the full calculated damage before health consumption,
death, loot tagging, achievements or Warscape XP processing. Normal combat
packets and spell/proc damage calculations remain available for comparison.
Independent guards reject direct health loss, instant-kill calls and attacks
made by this entry, even when AI is absent. Kill/event quest-credit paths also
reject this dummy. It cannot be used to farm combat XP, loot, money or kills.

The large HP reserve reduces overkill displays during ordinary tests; immortality
depends on the core guards, not that reserve. Direct GM removal/despawn is
intentional. This tool does not sandbox every possible spell side effect or add
new ability systems: avoid scripts designed to grant item/quest rewards on use.

## Migration and validation

`2026_10_25_03_world.sql` adds one template using only the model from stock entry
31144. It sets explicit passive utility/reward flags and the custom AI script.
It refuses an existing entry or spawn collision through the workflow's reviewed
preconditions. Existing templates, Stage 1G equipment/tier rows and character
data are preserved. Apply it only through `contrib/warscape/db.py`, after approval,
with stopped servers and the workflow's fresh verified backup.

Automated checks cover reserved-entry isolation, Defence bounds and its expected
effect on the existing accuracy formula, alongside all earlier combat tests.
The Release x64 build verifies integration. Live spawn/attack/removal and a
permanent-spawn restart remain for the user's in-game confirmation.

Quick acceptance: record `.rs stats`, hit the dummy with several weapons and
verify damage/misses/speeds while HP and XP remain unchanged; compare Defence 1
and 99; remove a temporary dummy; then save one, restart, verify its return, and
remove the permanent spawn. No Stage 1G balance or Stage 1H work is included.
