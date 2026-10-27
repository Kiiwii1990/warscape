# Warscape HUD

`addons/WarscapeHUD` contains the bottom-centred native live minimap, five
navigation slots on each side, a continuous metal rail and Blizzard's Dwarf
gryphon end caps. The slot immediately left of the map opens Inventory (B); the
slot immediately right opens Skills (N). Eight slots remain empty placeholders.

## Original artwork and layout

- Gryphon: `Interface\MainMenuBar\UI-MainMenuBar-EndCap-Dwarf.blp` from the
  primary client's `locale-enUS.MPQ`. The unmodified BLP is preserved in
  `addons/WarscapeHUD/art/WarscapeGryphonOriginal.blp`; `sources.json` records its
  hash and provenance. The previous Human variant was the wrong silhouette.
- The visible source region is 128 x 76, beginning at row 52. A separate
  pointwise bronze/silver grade preserves every alpha pixel. Lua crops the
  transparent upper padding and draws the region at 160 x 95, preserving its
  aspect ratio exactly. The right side is mirrored. The measured front-claw tip
  at source x=101 anchors a quarter-slot over the outer button border.
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

The tools directory rebuilds the two runtime TGAs from local client assets and
renders the actual Lua geometry as an offline proof with an empty map viewport.
The addon uses interpreted Lua and runtime textures; no native client rebuild
or executable change is needed for this update.

The user performs final visual/input review: gryphon silhouette/claw overlaps,
rail joins, complete circle, zoom controls, coloured card, N/click/close highlight,
independent 50/100/150% scaling and persistence after reload.

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
