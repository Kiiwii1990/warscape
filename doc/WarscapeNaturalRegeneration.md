# Cave Crawler / Kurask natural regeneration

Closes source-backed rapid regeneration for Cave Crawler902103 and Kurask902304. Sources: [Cave crawler](https://oldschool.runescape.wiki/w/Cave_crawler), [Kurask](https://oldschool.runescape.wiki/w/Kurask). Both describe one source Hitpoint per five600ms ticks. Warscape therefore heals10 displayed HP every3000ms. Turoth was listed in earlier prototype notes, but the reviewed Turoth source text did not state this rate; its regeneration is left unchanged pending reliable evidence.

HasFastNaturalRegeneration selects only these two entries. Reset clears a creature-local timer and locks native percentage regeneration for those entries using SetRegenerateHealth(false). UpdateAI advances the source timer before its no-victim return, so regeneration runs in and out of combat while the creature is active/loaded. Healing is capped by missing HP; zero/dead creatures are never healed. Evading creatures skip pulses and retain normal core evade/home reset behaviour. Lag advances elapsed pulses arithmetically, not with an unbounded loop;64-bit arithmetic avoids overflow. Full-health pulses are discarded and cannot become stored healing. Timer phase restarts on Reset; it is not globally synchronised with OSRS ticks or persisted across grid unload/server restart. Other creatures keep native regeneration.

No profile, loot, attack cadence, XP, item or spell changes. No database migration or client patch. No client memory-layout-sensitive code changed. Existing native full-health evade resets are distinct from normal source regeneration.

## Manual acceptance

`.gm off`; `.npc add temp loot 902103`. On open ground hit once, stop auto-attacking and stay close enough to remain in combat. Watch target health: it should recover10 displayed HP each3seconds, capped at maximum. Crawler poison still applies, so use a suitable test character. Repeat with `.npc add temp loot 902304` Kurask. Native health-bar rounding can hide one small tick; use target health numbers if available. Landing hits resets damage, not the regeneration timer.

Check no extra native percentage jump while idle, and no regeneration on corpse. Kill and respawn/resummon, then repeat. Evade/home may restore full health normally and is not the3-second test. Check Turoth/ordinary creature as controls and previous mask/goggles/lantern/spray mechanics. No client restart required. Exact loaded in-game timing remains pending user acceptance.

## Validation / deployment

140 Python catalogue tests and focused Debug C++ checks passed; RelWithDebInfo worldserver build passed. C++ covers selected/unrelated entries,2999+1ms boundary, lag pulses/remainder/reset, full/dead/invalid maximum-health cases, partial overheal and32-bit extreme arithmetic. Creature native regeneration lock and Unit AI update paths reviewed. Automated tests do not substitute for runtime health/timing acceptance.

World migration status inspected:56 applied, none pending. Zero online characters before stopping services. Runtime binary/PDB backup C:\WarscapeBackups\NaturalRegen-20261108-deploy. Only executable/PDB deployed, no database or client asset writes. Existing world/profile/loot/XP/inventory/wallet hashes checked. Rollback: stop services, restore backed-up executable/PDB and restart; no database/character restore. Existing unrelated native warnings remain separate.

Post-deployment: EXE/PDB match build; both services listening/ready with no new affected-entry startup errors. Existing world and character preservation hashes match. Manual timing/gameplay acceptance remains pending.
