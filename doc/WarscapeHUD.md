# Warscape HUD

`addons/WarscapeHUD` contains the bottom-centred native live minimap, five
navigation slots on each side, a continuous metal rail and the approved Design 5
armoured gryphon end caps. The slot immediately left of the map opens Inventory (B); the
slot immediately right opens Skills (N). Eight slots remain empty placeholders.

## Original artwork and layout

- Gryphon: `WarscapeGryphonDesign5Source.png` is the approved 494 x 299 source.
  The charcoal backdrop is removed with an exterior-connected matte; the
  source colours are not graded. The result is proportionally fitted into the
  existing 128 x 76 texture slice beginning at row 52, with one-pixel horizontal
  padding. Both Lua texture frames remain 160 x 95 at their existing anchors;
  the right side is mirrored through its existing texture coordinates.
  `build_art.py` creates `WarscapeGryphonDesign5.tga` reproducibly.
- The original Dwarf BLP remains preserved for provenance, but is no longer
  used for the HUD gryphons.
- Rail: the blank 192 x 43 metal strip at `(64,85)-(256,128)` in Blizzard's
  `UI-MainMenuBar-Dwarf.blp`. Uniformly scaled sections repeat behind both button
  groups and the map; the final section is cropped. The rail ends underneath
  the gryphons, without independent centre borders or a stretched panel footer.
- Map: a 140 x 140 native renderer with a concentric 152 x 152 housing. The
  border uses source `(92,29)-(244,181)` in `UI-Minimap-Border`, centred at atlas
  `(168,105)`. Its lower housing margin is eight design units. The detached stock
  header, zone label and collapse control are hidden, alongside calendar/clock.
- Native zoom buttons retain their scripts and original centre-to-centre
  spacing at approximately 2 and 3 o'clock, just outside the housing. Native
  tracking/world-map controls remain on the left. North/compass regions follow
  the map centre; native rotation behavior remains.
- Ten 44 x 44 navigation slots use the Skills panel's existing Cell border.

The root stays anchored to the exact bottom centre. A child assembly fits 52%
of viewport width at 100% saved HUD scale, including after resolution and global
UI scale changes. The saved user multiplier then scales that complete assembly:
50% occupies 26% of viewport width; 150% occupies 78%. Existing preferences are
retained, so an existing 50% preference remains 50% after upgrade.

## User-selected Skills icon and behavior

The user selected `Interface\Icons\INV_Misc_PunchCards_Prismatic.blp`, the
multicoloured data card from `locale-enUS.MPQ`. Original colours remain. Its
source crop `(4,4)-(60,60)` fills 56/68 of the square button width, matching the
comparison's proportions, and inherits the entire HUD's scale.

`doc/WarscapeHUDIconCatalog.tsv` records all 6,308 distinct archived icon paths.
All were decoded successfully and visually reviewed. The data-card selection
supersedes the earlier belt, book, checklist and data-display proposals; see
[rescue diagnosis](WarscapeHUDRescue.md).

The Skills addon still owns its panel, server data, calculations, N binding and
`/wskills` command. Both Inventory and Skills register with `WarscapePanels`;
opening one closes the other. The manager synchronizes HUD state from actual
visibility, including keyboard, click, close and Escape. An active button locks
its native highlight and dims while its panel is open. Inventory uses Blizzard's
original `Interface\Buttons\Button-Backpack-Up` in the existing left-hand slot.

Hold Ctrl over the HUD or Skills panel and use the mouse wheel to scale that
component independently. The existing magnifier/percentage display and HUD
`WarscapeHUDScales.hud` remain. `WarscapePanelScales` stores each registered
panel's scale, migrating the legacy Skills scale once. HUD, Skills and Inventory
have 50-150% bounds; panel maxima reduce when needed to fit the screen. Existing
Skills dimensions and saved position remain. See [Inventory Phase 1](WarscapeInventoryPhase1.md).

## Validation and visual acceptance

```powershell
py addons\WarscapeHUD\tests\test_art.py
py addons\WarscapeHUD\tests\test_hud.py
py addons\WarscapeSkills\tests\test_addon.py
py addons\WarscapeSkills\tests\test_bindings.py
py -m unittest discover -s addons\WarscapeUIHide\tests -v
```

Checks cover the pinned Dwarf asset hash, unchanged alpha and crop geometry,
reproducible grading, unstretched continuous rail, measured claw overlap,
concentric map/border, original control callbacks, icon crop/size, panel toggle
state, independent saved scales and 36 viewport/UI-scale/user-scale combinations.
These checks do not render the native minimap or establish in-game acceptance.

The tools directory rebuilds the runtime TGAs from local client assets and
renders the actual Lua geometry as an offline proof with an empty map viewport.
The addon uses interpreted Lua and runtime textures; no native client rebuild
or executable change is needed for this update.

The user performs final visual/input review: gryphon silhouette/claw overlaps,
rail joins, complete circle, zoom controls, coloured card, N/click/close highlight,
independent 50/100/150% scaling and persistence after reload.

## Prayer-texture HUD background and padding, 28 October 2026

The HUD rail now uses the same `WarscapeSkills\art\Stone.tga` material as the
Prayer panel, with the same tiled 100-pixel backdrop style. A generated
transparent rail overlay preserves only the original bronze top trim. The
backing is 74 UI units high, and the existing 95%-size buttons are raised to
26 UI units from its bottom so their labels remain inside it. The minimap,
gryphons, button centers, button spacing and 95% size are unchanged. Details
and deployment status are recorded in
[WarscapeUIFrameworkPhase1.md](WarscapeUIFrameworkPhase1.md).

## Map 905 terrain limitation

The native renderer reads terrain through `Textures\Minimap\md5translate.trs`.
The installed lookup tables have no `map905_` entries, so Briarbrook has no
terrain tiles for the native minimap to draw. The renderer, player arrow,
tracking and movement/orientation updates remain. This HUD correction supplies
no static map image and changes no terrain or map data.

## Deployment, 27 October 2026

WarscapeHUD 1.2.0 was deployed with the client stopped to
`C:\WoWDev\wowdecomp\bin\Win\Interface\AddOns\WarscapeHUD`. The executable and
default game directory were verified against `Client.cpp::SetPaths()` and the
client README launcher. The prior HUD, Skills and UIHide deployments are backed
up at `C:\WoWDev\Backups\WarscapeHUD-Rescue-Deploy-20261027-141600`.

Only the HUD TOC, Lua, gryphon TGA and rail TGA were copied. All four deployed
SHA-256 hashes match the source and `out/WarscapeHUD-1.2.0.zip` package. The
automated checks above pass. The client was not launched; native rendering and
manual visual/input acceptance await the user's review.

## Universal UI framework revision, 27 October 2026

The approved Phase 1 revision replaces the earlier global single-panel rule
with independent left and right main-panel groups, and replaces independent
custom-panel scales with one shared custom scale. It assigns the existing ten
buttons to the functions and shortcuts documented in
[WarscapeUIFrameworkPhase1.md](WarscapeUIFrameworkPhase1.md), adds labels and
empty Attack Styles, Prayer and Spellbook panels, and preserves the original
HUD art. The chosen Quest Journal and Spellbook icons are `INV_Misc_Note_05` and
`INV_Misc_Book_01`. The Skills button retains the user-approved multicoloured
data card. Historical deployment records above describe prior releases; current
deployment and review status is recorded in the framework implementation.

## HUD layout and Prayer binding refinement, 27 October 2026

The next user-approved refinement lowered the HUD buttons, aligned the complete
assembly to the viewport bottom, shifted the original gryphon textures outward
without stretching, hid minimap tracking/world-map controls while preserving
Blizzard handlers, and moved the zoom controls inward to meet the ring. Prayer's
I shortcut now has an explicit priority override to resolve the reported key
conflict. The user selected `INV_Jewelry_Talisman_08` (golden sun symbol) as the
Prayer icon. It is deployed in HUD 1.6.0. Runtime deployment details and test
results are in [WarscapeUIFrameworkPhase1.md](WarscapeUIFrameworkPhase1.md).

The 28 October 2026 deployment includes the Prayer `Stone` backdrop and taller
HUD rail padding correction. The deployed Stone asset was verified against the
Skills source texture; the HUD Lua, TOC and generated rail-trim texture hashes
match source. Prior HUD deployment files are backed up at
`C:\WoWDev\Backups\WarscapeHUDFinalCorrections-Deploy-20261028-003741`. Manual
visual acceptance is pending.

## Inventory-referenced button alignment, 28 October 2026

HUD 1.8.0 reads the Inventory button's existing vertical frame anchor and applies
that y offset to all other button frames, preserving each x offset. Other labels
reuse the Inventory label's anchor and spacing. The Inventory frame itself is
left untouched. Targeted HUD geometry and scaling tests pass.

The Inventory-reference alignment was deployed as HUD 1.8.0 on 28 October 2026.
The running client path and no-override game directory were verified before
copying; source and deployed Lua/TOC hashes match. The previous HUD directory is
backed up outside Git at
`C:\WoWDev\Backups\WarscapeHUDButtonAlignment-Deploy-20261028-081015`. Reload
or restart the client to load the updated anchors; Codex did not operate the game.

## Finished backing trim and lower button row, 28 October 2026

HUD 1.8.1 finishes the full-width black HUD backing with the original
Warcraft bronze top bevel. `WarscapeRailTrim.tga` now preserves the first five
source rows of the Blizzard rail art over the tiled Stone fill, instead of only
the thin first two rows. The entire button row, including Inventory, is lowered
four UI units (Inventory center y=44); all other buttons and labels continue to
inherit its exact vertical anchor and label spacing. Horizontal positions,
minimap, gryphons, artwork, bindings and panel behavior are unchanged.

## Visible top border, 28 October 2026

The user confirmed that the earlier rail bevel did not show clearly in-game.
HUD 1.8.2 adds a separate six-unit border above the button row, cropped from the
existing Skills-panel `HeaderRail.tga`. It spans the backing, renders above its
Stone fill and below the minimap/buttons/gryphons, and remains anchored to the
scaled assembly. Button geometry and all other approved HUD elements stay fixed.

## HUD gryphon metal recolour, 28 October 2026

The two gryphons continue to use the original Dwarf Blizzard cap texture and
the same alpha silhouette, UVs, mirroring, dimensions and anchors. The texture
builder applies a higher-contrast neutral/silver-to-bronze palette based on the
custom menu Dragon ornament, with a small warm eye light at the existing eye.
The panel artwork and HUD layout are unchanged.

## Gryphon palette correction, second pass, 28 October 2026

The gryphon builder now samples the shared upper-corner `Dragon.tga` used by
Inventory and Attack Styles. It classifies sampled panel pixels as dark shadow,
bronze or silver, maps the source gryphon's luminance ranks to the panel's
visible tone distribution, then applies the closest panel colour at that tone.
The small eye light uses the panel eye's actual core and surrounding halo
colours. Original alpha, texture dimensions and the HUD's shared/mirrored
gryphon rendering are preserved.
