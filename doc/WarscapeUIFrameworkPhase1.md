# Warscape Universal UI Framework — Phase 1

Approved implementation direction, 27 October 2026. This addendum supersedes
older HUD and Inventory descriptions where they specify one global open panel,
independent custom-panel scales, or 500 x 514 panel exteriors.

## Panel management

`WarscapePanels` is the shared registry for main menus. Registrations declare a
`left` or `right` group. A new panel closes only its peers in that group, and
the manager synchronizes direct Show/Hide, close buttons, HUD highlights and
keyboard/button toggles. One panel per group may be open, so left and right
panels can remain open together. Temporary loot, tooltip and confirmation
interfaces are not registered.

Custom panels share a 350 x 514 base exterior and one character-saved scale from
50% to 150%. Ctrl + mouse wheel and the magnifier indicator control that scale.
HUD scale remains independent. Custom panels can be dragged and keep their own
saved positions. Native Blizzard panels keep their native dimensions and
content while integrating with the manager where available.

## HUD assignments

| Position | Function | Key | Interface |
| --- | --- | --- | --- |
| Left 1 | Settings / Logout | ESC | Native game menu |
| Left 2 | Friends / Social | O | Native social interface |
| Left 3 | Reserved | — | Empty and non-interactive |
| Left 4 | Quest Journal | L | Native quest journal |
| Left 5 | Inventory | B | Warscape Inventory |
| Right 1 | Skills / Stats | N | Warscape Skills |
| Right 2 | Character Equipment | C | Native equipment |
| Right 3 | Attack Styles | K | Empty Warscape panel |
| Right 4 | Prayer | I | Empty Warscape panel |
| Right 5 | Spellbook / Magic | P | Empty Warscape panel |

The icon choices in this phase are original client assets. Quest Journal uses
`INV_Misc_Note_05`; Spellbook uses `INV_Misc_Book_01`; Skills retains the
approved multicoloured data-card icon. Existing backpack, minimap and gryphon
art are preserved. The third left button is blank. Labels are displayed below
assigned buttons. Invisible anchors reserve layout room for future Health and
Prayer bars; no resource mechanics or placeholder bars are implemented.

## Inventory

Inventory retains native item storage and interactions. It displays 28 slots in
four columns and seven rows: 24 usable native slots and four greyed, locked
positions. The final four are not fake storage; tutorial unlock work remains
future scope. The grid is square and compact.

## Validation and deployment

Targeted Lua 5.1 harnesses validate HUD bindings, same-side replacement,
opposite-side coexistence, highlighting, scaling and saved preferences; native
item/loot callbacks; locked-slot behavior; menu bindings; Skills and UIHide
compatibility. These checks do not replace the user's visual and gameplay
review in the client.

Deployment is to the verified local wowdecomp client only. The client executable
path and command line are checked before each copy; any previous addon folders
are backed up outside Git. No client launch is part of this workflow. The user
performs visual inspection and manual gameplay acceptance.

## Implementation and deployment record, 27 October 2026

Targeted checks passed: `test_bindings.py` for the menu bindings;
`test_hud.py` for HUD geometry, assets, highlighting and scale; and
`test_inventory.py` for side-group behavior, O/L/C/B/N/K/I/P interaction,
native inventory actions, locked slots and scaling. The Skills addon, Skills
bindings/skin and UIHide test suites also passed. No native build was needed;
this change consists of Lua addon files and runtime textures.

Runtime addons were deployed to
`C:\WoWDev\wowdecomp\bin\Win\Interface\AddOns` after verifying the running
client executable at `C:\WoWDev\wowdecomp\bin\Win\WowClient64.exe` and
confirming no `-datadir` override. Eighteen runtime files across Panels, Skills,
Inventory, MenuPanels and HUD were copied. Their SHA-256 hashes match source.
The four pre-existing addon folders were backed up outside Git at
`C:\WoWDev\Backups\WarscapeUIFrameworkPhase1-Deploy-20261027-225514`.

The client was already running during file deployment and was not operated or
reloaded. The new files will take effect after the user next reloads the UI or
restarts the client. Codex did not launch the game. The user's visual and manual
input review is pending; no build, server or database change, commit or push was
performed.

## HUD refinement revision, 27 October 2026

The user reports in-game approval of the current panel groups, shortcuts and
compact Inventory grid. This focused revision lowered the ten HUD buttons,
removed the bottom inset, extended gryphon art outward without scaling it, hid
the minimap tracking and world-map controls while retaining native scripts,
and moved zoom buttons inward to overlap the ring slightly. Prayer's I binding
now takes a priority override to resolve conflicting saved Blizzard bindings;
the panel manager still controls visibility, right-side replacement and button
highlighting. The user selected `INV_Jewelry_Talisman_08`, the golden sun symbol,
as the Prayer button icon. The selection is implemented in HUD 1.6.0 and its
deployment is recorded below.

Targeted HUD, menu-binding and Inventory integration tests pass, including
resolution/scale cases, minimap visibility/zoom anchors, I conflict override,
side-group behavior and locked inventory positions. Deployment copied the HUD
Lua/TOC and menu-panel binding Lua/TOC to the verified client directory after
the client stopped. The previous HUD and MenuPanels directories are backed up
outside Git at `C:\WoWDev\Backups\WarscapeHUDRefinement-Deploy-20261027-234218`;
all four deployed file hashes match source. No native build was needed and no
client/server was launched or changed. User visual inspection is pending.

The user subsequently selected the golden sun symbol `INV_Jewelry_Talisman_08`
for Prayer. HUD 1.6.0 updated the icon reference, and `test_hud.py` passed. The
HUD Lua and TOC were deployed with the client stopped to the verified local
client directory; source and destination hashes match. Previous HUD files were
backed up outside Git at
`C:\WoWDev\Backups\WarscapePrayerIcon-Deploy-20261028-000622`. No native build,
server/database change, commit or push was performed. Manual visual review is
pending.

## Final HUD corrections, 28 October 2026

The HUD now uses the same `WarscapeSkills\\art\\Stone.tga` tiled backdrop as
the Prayer panel (`tileSize=100`, white/opaque tint). The original rail's gold
upper edge is retained in `WarscapeRailTrim.tga`; its brown center is
transparent. The backing height is 74 UI units, and the existing 95% buttons
are raised to y=26 with their labels attached below. Their horizontal centers,
minimap, gryphons, icons, panel behavior and scaling are unchanged.

`build_art.py` generated the trim overlay from the local original Dwarf rail.
`test_art.py` and `test_hud.py` passed, including exact Prayer backdrop,
transparent trim, button containment, horizontal centers and existing
resolution/scale cases. No native build was needed. Deployment copied only the
HUD Lua, TOC and new trim texture after verifying the stopped client's default
game directory from the wowdecomp README and `Client.cpp::SetPaths()`. The
existing deployed `WarscapeSkills\\art\\Stone.tga` matched source. All copied
SHA-256 hashes match source. Previous HUD files are backed up outside Git at
`C:\\WoWDev\\Backups\\WarscapeHUDFinalCorrections-Deploy-20261028-003741`.
No game or server was launched or modified. User visual review is pending.

HUD 1.8.0 applies the Inventory frame's anchor and label offsets to all other
HUD buttons, including the empty reserved slot, while retaining their existing
horizontal offsets. The Inventory button itself is untouched. `test_hud.py`
passed. The HUD Lua and TOC were deployed to the verified local client; the
client was running, so a UI reload or restart is needed to load the update. The
pre-deployment HUD backup is
`C:\WoWDev\Backups\WarscapeHUDButtonAlignment-Deploy-20261028-081015`. No native
build, game operation, commit or push was performed.

The follow-up polish completes the top edge of the full-width black backing
with five rows of the original bronze rail bevel and lowers the entire
button/label row four UI units. Inventory remains the shared anchor reference at
y=44; horizontal positions, minimap, gryphons, icons, panel behavior and scaling
remain unchanged. Targeted validation and deployment details are recorded in
the current HUD refinement entry.


## Docked landscape menus and independent controls, 31 October 2026

The approved wide-menu reference supersedes the earlier default portrait,
freely draggable layout. All nine HUD menus now have landscape shells docked
directly to the HUD rail, with minimap/zoom clearance. Their default size is
700 x 400 design units, fitted to the actual HUD artwork. Portrait custom menus
retain 350 x 514 design units; native pages use 460 x 650 to retain their native
384 x 512 content and bottom tabs. Dragon/foot dimensions, gryphon artwork,
textures and icons are unchanged. Only plain frame segments resize. The bottom
button gap increases from 4 to 24 design units. The HUD fills 90% of the viewport
at its default scale, capped at 98% when enlarged so buttons remain accessible.

Each header has a padlock at top left, an orientation arrow next to it, and the
existing close X at top right. New menus start locked and landscape. Unlocking
preserves the current position and enables dragging only through the title hit
area; item slots and controls cannot initiate panel dragging. Relocking clears
the detached location and immediately restores the side's inner HUD dock, keeping
orientation and scale. Orientation can change while locked or unlocked. Detached
menus retain their bottom centre; screen-fit/clamping keeps controls reachable.

Inventory reuses the same 28 buttons and native bag/slot mappings: landscape is
7 x 4 and portrait is the existing 4 x 7. Capacity authorization, four locked
positions, native item actions and cursor safety remain unchanged. Skills uses
six landscape columns or three portrait columns, retaining scrolling, tooltips,
current/base levels, XP and future stable IDs. Empty Attack Styles, Prayer and
Spellbook panels gain the shared controls without adding gameplay content.
Settings reflows its original buttons into two columns in landscape. Social,
Quests and Equipment retain native widgets, tabs, selection and callbacks inside
scrollable viewports, rather than reducing text to fit. Use their edge scrollbars
when needed; ordinary wheel scrolling remains native, Shift-wheel scrolls the
outer viewport horizontally, and Ctrl-wheel adjusts the shared panel scale.

The existing universal 50-150% panel preference remains
`WarscapePanelScales.universal`; HUD scale remains `WarscapeHUDScales.hud`.
The dock/viewport fit is applied separately, so the saved user preference does
not change just because a resolution or HUD size changed. All menu shells now
participate in the shared scale. Protected native reparenting is deferred during
combat; protected layout changes apply when combat ends. No object/memory-layout
code, native executable, gameplay or database data changes are involved.

New per-character preferences are saved by the Panels addon in
`WarscapePanelLayouts[menuID] = {locked, orientation, position}`. Detached position
is normalized bottom-centre X/Y in UIParent coordinates. Locked positions are
always derived from HUD anchors. Closing/reopening and UI reload retain each
menu's independent choices. Existing legacy position variables remain untouched
but no longer own placement. SavedVariables are managed normally by WoW; no
account settings or SavedVariables files are edited during installation.

Lua 5.1 checks cover all nine menus, default docking, direct rail attachment,
independent lock/orientation controls, shared scaling and stable detached
bottom-centre positions, same-side replacement, close/reopen, a fresh-runtime
saved-state restore, native inventory callbacks and locked slots, native controls,
and 648 resolution/UI-scale/HUD-scale/preference/orientation combinations. Original
artwork hashes remain unchanged and new control asset paths are verified against
the installed client. These are automated geometry/code checks, not in-game
visual or gameplay acceptance. The user performs the final client inspection.

Run the added interaction/geometry check with:

```powershell
py -B addons/WarscapePanels/tests/test_layout.py
```

Restart the client after installation to reliably load the new native adapter
file and SavedVariables declaration. Then open B and N together, try both
header controls, drag an unlocked menu, Ctrl-scroll in both shapes, relock in
portrait, replace detached menus via same-side shortcuts, and reload to confirm
persistence. Check native-page scrolling and inventory use/drag/split actions.


Deployment for this revision copied 12 Lua/TOC files across Panels, Skills,
Inventory, MenuPanels and HUD to
`C:\WoWDev\wowdecomp\bin\Win\Interface\AddOns`. The client was stopped.
Its default directory was verified from `WoW/Source/Client.cpp::SetPaths()`
(executable directory when no data-directory argument is supplied), matching the
previously observed executable/command line. All 12 deployed SHA-256 hashes
match source; 14 referenced runtime textures already matched and were not copied.

The fresh verified runtime backup is
`C:\WoWDev\Backups\WarscapeMenuLayout-Deploy-20261031-221757`.
The pre-edit source and full addon snapshot is
`C:\WoWDev\Backups\WarscapeMenuLayout-before-20261031-214246`.
No WoW process was launched, no service restarted, and no client settings,
SavedVariables, database data, maps or native executables were changed. No commit
or push was performed for this UI revision. No actual in-game screenshot or
manual acceptance is available; the user should launch the client and perform
the inspection checklist above.


## Symmetry, visual sizing and source-resolution gryphons, 31 October 2026

The user confirmed the menu interactions work and requested a focused visual
refinement. This revision changes shared measurements and artwork resolution,
not gameplay, menu bindings, scale ownership, slot identities or persistence.
The pasted brief referenced a 2037 x 478 screenshot; only its text and approximate
measurements were present in this message. No matching current screenshot was
available for visual acceptance.

The actual source and deployed Lua matched at inspection. Their left/right
landscape frames already had the same nominal dimensions and vertical position.
The concrete positional mismatch was a left dock at -86 HUD units and a right
dock at +110. Native portrait wrappers also had a different exterior profile
from custom menus. Both docks now use +/- (half the minimap ring + the actual
native zoom-button width + 2). With the existing 152-wide ring and 32-wide zoom
buttons, this is exactly +/-110. Both dock to the rail's same upper edge. Native
and custom menus now use the same exterior profile for a chosen orientation:
700 x 460 landscape, 430 x 756 portrait. Different chosen orientations remain
independent, and unlocked positions are not forced into a mirrored arrangement.

Shared visual metrics retain the established 44-unit HUD placement grid and
24-unit gaps but reduce the button frame from 41.8 to 34 units. Inventory slots
increase to 76 units in both orientations, with 6-unit gaps: still 7 x 4 or
4 x 7, using the same buttons, native bag/slot identities and item callbacks.
Skills keeps its established three/six-column reflow, with 80 x 104 cells,
64-unit icons, 18-unit current/base fractions and 112-unit row pitch. XP data,
progress calculations and scrolling remain unchanged. Utility controls remain
30 units. Only plain rails/sides resize; corner ornaments retain their sizes.
The taller profiles accommodate larger readable content and preserve footer gaps.

At the common 1920 x 1080, global/UI/HUD/panel preference = 1 reference, modelled
physical sizes are: HUD buttons 55.93 pixels, Inventory slots 46.30 pixels,
Skills tiles 48.74 x 63.36 pixels (the extra height holds level/XP information).
Both landscape frames are 426.45 x 280.24 pixels at equal offsets. Actual client
values can be recorded with `/wgeometry`; it prints shown frame bounds and
paired width/height/top/bottom/mirror errors. The complete table is retained in
`WarscapePanels.geometrySnapshot`, in memory only. The diagnostic handles legacy
texture regions using the parent frame's scale and does not move any frame or
change saved preferences.

The approved gryphon source is 494 x 299. Its old runtime was 128 x 128 with only
128 x 76 visible texels, displayed at about 263 x 156 pixels at the reference
scale (over 2x enlargement). The new `WarscapeGryphonDesign5HD.tga` is compiled
directly from that original source into a 512 x 512 RGBA canvas, with a 512 x 304
visible region. Both sides use the same file and opposite horizontal UVs. The
source RGB palette, silhouette, matte algorithm and displayed 160 x 95 design
shape are retained. No sharpening, repainting, new design or client filter change
is used. All 19 pre-existing image files, including dragons, remain byte-identical.

Inspection of the local engine confirms UI textures use `GxTex_Linear`
(`CSimpleRender.cpp`, `CSimpleTexture_Scripts.cpp`). The TGA loader generates
its mip chain (`Services/Texture.cpp`). The source image was already reduced to
128 visible texels before those stages, so filtering could not recover its lost
detail. The new high-resolution base fixes that authoring reduction while
preserving the native filtering/mipmap path. The new asset passes uncompressed
32-bit TGA/8-bit alpha, power-of-two, reproducibility and silhouette checks.

All 10 targeted suite commands pass: paired geometry and interaction tests,
HUD geometry/assets, native Inventory interactions and bindings, Skills protocol,
layout/scrolling/bindings/skin, MenuPanels bindings, and UIHide. Geometry tests
check 40 matching menu pairs and 216 viewport/UI/HUD/panel-scale/orientation
configurations. The existing nine-menu suite separately checks each menu over
those 216 configurations (1,944 frame-bound checks), plus locks, dragging,
replacement, retained orientation, cursor safety and fresh-runtime saved-state
restore. The earlier report's label of 648 configurations was a counting error;
the actual nested loop contains 216. Current labels and reports use the actual
count. These are automated code/geometry checks, not in-game visual testing.

Offline evidence is at
`C:\WoWDev\UIReviews\WarscapeUISymmetry-20261031-224914`:
`before-geometry.json`, `after-geometry.json`, and `gryphon-comparison.png`.
The gryphon comparison shows the same supplied artwork with linear-resampling
approximation and is explicitly not an in-game screenshot. The source/runtime
pre-edit backup is
`C:\WoWDev\Backups\WarscapeUISymmetry-before-20261031-224914`.


Deployment copied 11 reviewed Lua/TOC/TGA files to
`C:\WoWDev\wowdecomp\bin\Win\Interface\AddOns`, with the client stopped.
The executable/default directory was verified against the process inventory and
`Client.cpp::SetPaths()`; no data-directory override was active. Every copied
file matches source by SHA-256. Every pre-existing runtime file outside the exact
copy list remained unchanged. The fresh verified runtime backup is
`C:\WoWDev\Backups\WarscapeUISymmetry-Deploy-20261031-231137`.
No game, server, native build, database operation, commit or push was performed.
No memory-layout-sensitive code changed, so native mirror-layout tests were not
applicable. SavedVariables and detached user preferences were not edited on disk.

Start the client normally. A full client restart is recommended if it was open
before installation, to load the new HD texture without an old texture cache;
`/reload` suffices for Lua-only updates. No server restart is needed. For user
review, open B and N, lock both to the same orientation, run `/wgeometry`, then
check the glyph/icon sizes, XP fractions, lock/rotate/drag/scale behaviour and
texture edges. Actual rendered appearance remains pending the user's review;
Codex has not launched or operated WoW for this pass.


## Persistent left/right window ownership, 31 October 2026

The user corrected the layout ownership rule: menu switching must replace the
contents of a HUD-side window while preserving that side's position, lock,
orientation and scale. This supersedes per-menu layout ownership and the single
universal menu scale from the preceding revisions. HUD scale stays independent.
Actual menu-to-side assignments and all artwork/content implementations remain
unchanged. Inventory/Friends/Quests/Settings are left; Skills/Equipment/Attack
Styles/Prayer/Spellbook are right.

The existing registry now has exactly two logical owners,
`WarscapePanels.windows.left` and `.right`. Existing menu frames remain reusable
content views, with `entry.window` pointing to their owner. `State(menuID)`
resolves the same table for every menu on that side. The shared controls therefore
operate on a side even though their buttons remain on each view's existing
chrome. No reparenting or reconstruction of native content is needed.

Per-character `WarscapeWindowLayouts` stores `version=1` and `left`/`right` records
with `{locked, orientation, position, scale, lastMenu, migratedFrom}`. Position is
the preferred normalized bottom centre; the effective viewport-clamped anchor is
kept separately in the logical window, not written over the saved preference.
Locking clears the detached position and uses the side's original HUD dock.
Orientation and the 50-150% user scale are retained. The sides have independent
scales and states; `WarscapeHUDScales.hud` continues to control the HUD alone.

Before Show (also for native toggles), the registry captures an unfinished move,
reflows the side's views using the shared orientation, applies that side's scale,
and positions every replacement at the same anchor. It then hides the previous
content and shows the replacement. Direct native Show paths use the same owner.
The side reserves the largest registered content width/height when fitting and
clamping, so a smaller/larger menu switch cannot choose a different anchor or
scale. A newly registered larger view can require a new viewport fit, but the
preferred saved position survives. Existing tooltips, native item callbacks,
scrolling, keybinds, active highlights and one-open-menu-per-side rules remain.

Migration occurs once per missing side record. It prefers an unlocked legacy
layout with a valid detached position, then another unlocked layout, then a
portrait choice. Ambiguous ties use the established primary-menu order:
Inventory/Friends/Quests/Settings on the left and Skills/Attack Styles/Equipment/
Prayer/Spellbook on the right. Old records have no timestamp, so a most-recent
choice cannot reliably be inferred. Both side scales initially copy the old
universal preference (or its existing Skills/HUD fallback). Fallback scale
persistence waits for PLAYER_LOGIN so every addon's SavedVariables is loaded.

`WarscapePanelLayouts` and `WarscapePanelScales` remain declared and untouched as
legacy fallback copies; the manager no longer writes competing per-menu layout
or universal-scale values. Existing `WarscapeWindowLayouts` records win on later
reloads; edits to the archive do not remigrate an already configured side. No
WTF/SavedVariables files are read or modified by the deployment tooling. The game
performs normal SavedVariables persistence when the user reloads/exits.

Runtime changes are confined to `addons/WarscapePanels/Panels.lua` and
`WarscapePanels.toc` (1.4.0). Focused tests and the shared `ui_fixture.py` loader
were updated to the corrected side-owned contract. The added
`test_side_windows.py` verifies Attack Styles -> Skills -> Equipment, Inventory
-> other left menus, before-OnShow positioning, independent side/HUD scales,
shared orientation/lock state within a side, close/reopen, native visibility,
HUD highlighting, small/large views, preferred-anchor retention at viewport
edges, two fresh Lua runtime reload/restart simulations, migration and legacy
record preservation.

All nine focused suite commands passed, including the new handoff suite, the
216-configuration/nine-menu control suite, 40 matching menu-pair checks, HUD
geometry, real native item-script integration, Skills protocol/scrolling,
bindings and UIHide. The untouched individual-menu/HUD runtime code and artwork
were byte-checked against the pre-edit snapshot. These are automated Lua 5.1
checks, not actual client reload/restart or in-game testing. No game was launched.

Pre-edit verified source/runtime backup:
`C:\WoWDev\Backups\WarscapeSideWindows-before-20261031-232946`.
After deployment, restart the client to reliably pick up the new per-character
SavedVariables declaration, then drag Attack Styles and select Skills/Equipment,
and drag Inventory and select Friends/Quests. Each side should retain its layout;
changing one side's scale or orientation should leave the other alone.


Deployment installed only `Panels.lua` and `WarscapePanels.toc` to
`C:\WoWDev\wowdecomp\bin\Win\Interface\AddOns\WarscapePanels`.
The client was stopped. Its executable/default directory was verified using
process inventory and `Client.cpp::SetPaths()`; no data-directory override was
active. Both installed SHA-256 hashes match source. The fresh verified runtime
backup is `C:\WoWDev\Backups\WarscapeSideWindows-Deploy-20261031-234853`.
No client/server executable or memory-layout-sensitive code changed, and no
native build/mirror-layout test was applicable. No game was launched, service
restarted, database modified, commit made or push performed. Actual in-client
switching and persistence remain for user acceptance after the recommended
client restart; automated reload/restart checks used fresh Lua runtimes only.
