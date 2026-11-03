# Stage 1G: deterministic weapons and tenfold health display

## Classification and precedence

WoW item class/subclass drives automatic classification. Daggers use stab,
one-handed swords use Longsword/slash, two-handed swords use slash, one-handed
maces use crush, and two-handed maces use Warhammer/crush. Existing mappings for
axes, polearms and explicit OSRS archetypes remain. Names are not parsed to
guess a scimitar, rapier or material. WoW sword subclasses do not distinguish
those shapes; use `warscape_weapon_rule.archetype` for a reviewed exception.
Explicit OSRS ShortSword retains its established stab-oriented behavior.

Precedence is deliberately conservative:

1. An existing `warscape_item_bonus` row is a complete custom profile. Every
   bonus, including zero and negative values, remains authoritative. Its tier
   is descriptive; no baseline is added to or multiplied into custom bonuses.
2. Otherwise `warscape_weapon_rule` optionally selects tier and archetype.
3. Otherwise the WoW subclass selects archetype and Bronze is the default tier.

The existing slot summation, style selection and combat formulas are preserved.
Stage 1G supplies only stab/slash/crush accuracy and melee Strength for baseline
melee weapons. Other channels remain zero unless explicitly customized. Armour,
ranged weapons, caster weapons and unsupported subclasses receive no automatic
bonuses. Broken/unusable main-hand weapons retain the existing diagnostic/speed
fallback. No randomized item definitions, instance rolls or Stage 1H work exists.

## Material tiers and references

Rules use 1 Bronze, 2 Iron, 3 Steel, 4 Mithril, 5 Adamant, 6 Rune. They select
actual OSRS weapon bonus tables, rather than a universal linear multiplier.
Only the four melee offensive fields are taken from those tables; defensive,
magic and prayer attributes and OSRS wield requirements are outside this batch.
Attack speeds remain the existing Stage 1F values, including its defaults.

References checked for the baseline table:
[Bronze](https://oldschool.runescape.wiki/w/Bronze_equipment),
[Iron](https://oldschool.runescape.wiki/w/Iron_equipment),
[Steel](https://oldschool.runescape.wiki/w/Steel_equipment),
[Mithril](https://oldschool.runescape.wiki/w/Mithril_equipment),
[Adamant](https://oldschool.runescape.wiki/w/Adamant_equipment),
[Rune](https://oldschool.runescape.wiki/w/Rune_equipment).

Inspection found 4,598 WoW weapons and four custom profiles. WoW item level,
quality, required level and generic material IDs do not establish a reliable
OSRS metal tier. No broad tier inference is attempted. The additive migration
`2026_10_25_02_world.sql` creates one rule table and seeds just two reviewed QA
mappings: Bronze Shortsword 2850 -> Bronze, Dazzling Mithril Rapier 7944 ->
Mithril. Both retain subclass-based Longsword classification. This is an explicit
test-set mapping, not a rule that all WoW material names imply OSRS tiers.
Existing item templates, inventories, custom profiles and attack speeds are not
modified. Future reviewed rules can cover additional items without code changes.

## Health, damage and healing

The shared `HealthDamageScale` changes from 100 to 10. It feeds player maximum
health, creature maximum health, melee damage, damage variation, flat healing,
flat regeneration, HP level-up increments and displayed-damage conversion.
Seven OSRS HP now means 70 displayed HP; a one-point melee hit averages 10
displayed damage. Positive variation rounds to nearest with ties to even and
retains a minimum of one displayed point; misses/zero rolls stay zero.

Flat periodic heals now use the same scale as direct heals. Percentage and leech
heals already calculated from displayed health/damage are not multiplied again.
Percentage regeneration uses the scaled maximum directly; flat regeneration
additions are scaled once. Ordinary spell/ranged damage, item spell values and
the broader WoW spell system are not converted to OSRS combat in this batch.
Mixed flat/percentage healing spells remain subject to the existing combined
heal pipeline and should receive separate integration coverage before balancing.

Unchanged OSRS rolls produce the same approximate damage/health ratios and
time-to-kill, subject to smaller-display integer rounding. New weapon bonuses
intentionally change combat outcomes for previously unprofiled weapons. Existing
QA profiles preserve their previous relative balance. XP rates, thresholds and
unvaried melee-roll XP awards are unchanged. Persisted character HP is not bulk
rewritten; login clamps saved health to the new maximum through the existing path.

## 10–15 minute in-game check

Start the installed authserver and worldserver from `C:\WoWDev\TrinityServer`.
Use a GM QA character able to equip the test weapons (7944 requires higher WoW
level/weapon proficiency); do not change a production character just for QA.

1. **3 minutes: archetypes.** Remove other bonus gear. Add/equip each of
   `.additem 7166` (Copper Dagger), `.additem 2847` (Copper Shortsword), and
   `.additem 2844` (Copper Mace). Use `.rs accurate` and `.rs bonuses`.
   Expected stab/slash/crush/Strength are respectively `(4,2,-4,3)`,
   `(4,5,-2,7)`, and `(1,-2,6,5)`. Natural lanes are stab, slash and crush.
2. **2 minutes: tiers.** Add/equip `.additem 2850`, then `.additem 7944`.
   `.rs bonuses` should report Bronze vs Mithril, slash 5 vs 20, Strength 7
   vs 22. Compare at unchanged Attack/Strength levels and style.
3. **3 minutes: scale.** `.rs stats` shows OSRS Hitpoints; displayed maximum
   HP should be ten times that level (10 -> 100). Fight the same familiar
   creature with an existing custom weapon. HP/damage should be about one tenth
   of Stage 1F, with similar kill time. Zero rolls remain zero. Check a direct
   heal, flat HoT and out-of-combat regeneration; percentage heals should restore
   their intended fraction. Keep spell/ranged balance outside this melee check.
4. **3 minutes: speed/custom regressions.** Check 2494/2488/2489/2493 with
   `.rs bonuses`: their old custom bonuses remain and speeds are still
   3/4/7/5 ticks (1.8/2.4/4.2/3.0 seconds). Weapon swaps must not bring a
   pending swing forward; no extra offhand auto-attacks. Target entry 36 and
   run `.rs monsterspeed`: 5 ticks/3.0 seconds; entry 480 defaults to 4/2.4.
5. **1–2 minutes: persistence.** Watch `.rs stats` XP progress, switch styles,
   unequip/re-equip and relog. Bonus totals must not accumulate. Record the
   expected diagnostic values and any timing, healing or XP discrepancies.
