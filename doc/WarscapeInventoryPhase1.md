# Warscape Inventory Phase 1

Approved scope: one 28-slot panel in a four-column, seven-row grid; 24 slots
usable initially; four tutorial-locked slots; the existing Skills exterior;
native Warcraft item behavior; B/Inventory left of the minimap and N/Skills
right of it. The user performs in-game visual/gameplay acceptance.

## Shared main-panel manager

`addons/WarscapePanels/Panels.lua` manages only explicitly registered Warscape
main panels. It closes the old panel before opening another, handles direct
Show/Hide and Escape dismissal, and synchronizes attached HUD buttons from
actual frame visibility. Loot, bank bags, confirmation dialogs and tooltips
are not registered and are not closed by the manager.

Future main panels use the same API after setting up and hiding their frame:

```lua
WarscapePanels:Register("equipment", frame, {onShow = requestData})
WarscapePanels:AttachButton("equipment", button, styleButton)
-- styleButton(button, open) draws the normal/active state.
-- Keyboard, slash and button actions all use this same entry point:
WarscapePanels:Toggle("equipment")
```

Registration supplies generic independent scaling. `WarscapePanelScales` saves
each panel's preference per character; the existing Skills preference migrates
from `WarscapeHUDScales.skills` once. The HUD retains `WarscapeHUDScales.hud`.
Ctrl-wheel, magnifier and percentage feedback remain. Limits are 50-150% with
the existing screen-fit cap. Switching panels does not reset their scales.
Visible dialog panels take precedence over the HUD when their rectangles overlap.

## HUD and panel

- Existing button 5, immediately left of the map, uses the original
  `Interface\Buttons\Button-Backpack-Up` texture. Size, borders, positions,
  gryphons, rail and minimap layout are unchanged. Button 6 remains Skills with
  the user-selected prismatic data card. Eight other buttons remain placeholders.
- Default B and N overrides have distinct owners, honor explicit custom
  bindings, defer during combat and never rewrite account/character bindings.
- Inventory reuses `WarscapeSkillsSkin.Panel` at 500 x 514 with optional title
  and unique close/footer region names. Skills defaults and contents remain.
- Slots 1-16 map to native backpack slots 1-16. Slots 17-28 map to native carried
  bag 1 slots 1-12. The last row is greyed out with the original Blizzard
  `Interface\LFGFrame\UI-LFG-ICON-LOCK` until the server unlocks it.
- Native `ContainerFrameItemButtonTemplate` scripts handle item use/equipment,
  pickup/drop, stack splitting, modified clicks, merchant confirmation and
  tooltips. Bag/lock/cooldown events refresh native item data. Locked actions
  return before native callbacks and preserve any item on the cursor.
- Original carried-bag windows (IDs 0-4) redirect to this Inventory panel.
  Bank-bag and other temporary windows remain native and functional.
- `WarscapeInventoryPosition` saves the independently movable panel location.

## Real server storage and unlock

The server retains its native 16-slot backpack. A reserved native 12-slot
Mageweave Bag (existing item template 10050) occupies carried-bag slot 19. Its
actual `CONTAINER_FIELD_NUM_SLOTS` is eight initially, then twelve after unlock.
Thus native client APIs, native auto-loot/store loops and normal item persistence
have real capacity for 24 or 28 items. No logical slots invent extra storage and
no client executable changes or item-template edits are required.

`WarscapeInventory.h/.cpp` implements this setup. A direct-slot validation in
`CanStoreItem_InSpecificSlot` also checks the current native container size,
including direct packets. The reserved storage bag cannot be removed, replaced,
traded/mailed, sold or destroyed. Ordinary carried items and normal equipment
continue through native handlers. Extra carried bags cannot expand this fixed
Warscape capacity; bank bags remain unaffected.

Two unused bits of the existing per-character `characters.extra_flags` field
are reserved: `0x1000` for managed storage and `0x2000` for tutorial unlock.
They fit the native 16-bit load/save path. Allocation and the marker are saved
through normal player inventory transactions, not a schema or offline data
migration. The future server-side tutorial reward calls
`Player::UnlockWarscapeInventory()`, which expands the real container, saves the
character and notifies the addon. No tutorial quest or client unlock command is
implemented in Phase 1.

The wowdecomp container constructor caches its slot count. The unlock helper
therefore refreshes the owner's container and contained item views using native
destroy/create object packets, preserving their server GUIDs and positions.
The addon also detects delayed native capacity replication before enabling the
four extra buttons. No client executable patch or relog is required by the API.

The read-only `WCInventory` self-whisper subscription returns authorized capacity
and a token/revision. Other senders, malformed/replayed states and client write
or unlock requests cannot authorize storage. Actual item data/actions use native
item packets and container fields, not addon-generated inventory contents.

Existing carried-bag profiles are never overwritten or silently hidden. A
character with pre-existing equipped bags, an unexpected backing container or
occupied locked tail requires a separately reviewed conversion. The addon fails
closed in that case. Read-only preflight against the current installation
verified the expected native bag template, unused flag allocation and that no
existing character currently needs this conversion. Future legacy imports may.

## Automated validation

The Release `worldserver` and `tests` targets were built locally. The native
Warscape suite passes 32 cases / 70,606 assertions, including capacity policy,
safe enrollment/locked-tail handling and the read-only protocol.

```powershell
py addons\WarscapeInventory\tests\test_inventory.py
py addons\WarscapeInventory\tests\test_bindings.py
py addons\WarscapeHUD\tests\test_hud.py
py addons\WarscapeHUD\tests\test_art.py
py addons\WarscapeSkills\tests\test_addon.py
py addons\WarscapeSkills\tests\test_bindings.py
py addons\WarscapeSkills\tests\test_skin.py
py -m unittest discover -s addons\WarscapeUIHide\tests -v
```

The combined test loads the real addons plus original item-button/container
scripts from the installed wowdecomp assets. It checks B/N/HUD toggles, exclusive
visibility, highlighting, all 28 positions, 24 initial native mappings, locked
actions, native pickup/use/split/drag/tooltip callbacks, bag updates, protocol
validation, future registration, transient windows and all three saved scales.
The HUD regression covers 36 viewport/UI-scale/user-scale cases. These mocks
validate code flow and API delegation, not a live loot session or rendered UI.

## User's in-game acceptance

Start the deployed servers and custom client through the established local
workflow. For the Briarbrook town centre:

```text
.go xyz -322.666667 -257.666667 33.5 905
```

1. B opens/closes Inventory; N opens/closes Skills. Switch both directions and
   click both HUD buttons. Confirm only one main panel and one active highlight.
2. Confirm four columns/seven rows, 24 usable positions, four grey padlocks and
   matching Skills exterior. Try dropping an item onto a locked slot: it must
   stay on the cursor and not move into that slot.
3. Loot, move, split, use/equip and delete ordinary items using native actions.
   Keep Inventory open while looting and using confirmation dialogs.
4. Scale HUD, Skills and Inventory independently; switch panels and reload/relog
   to verify their own preferences, item contents and the initial locked state.

For a GM's temporary normal-loot wolf test, the local command implementation
supports `.npc add temp loot 299` (Young Wolf). This is a temporary summon; no
persistent spawn/migration is needed. Codex has not spawned it or launched the
game. Live looting, persistence and visual acceptance await the user's feedback.

## Deployment record, 27 October 2026

The locally built Release worldserver is deployed to
`C:\WoWDev\TrinityServer\worldserver.exe`. Runtime files for `WarscapePanels`,
`WarscapeInventory`, updated Skills integration and HUD 1.3.0 are deployed under
`C:\WoWDev\wowdecomp\bin\Win\Interface\AddOns`. The stopped client's executable
and effective directory were verified from its source/README launch fallback.
Server database endpoints were privately checked against the source config.

All 29 runtime files match their packaged/source SHA-256 hashes. The package is
`out/WarscapeInventory-Phase1-1.0.0.zip`. Initial pre-feature runtime/character
backups are at
`C:\WoWDev\Backups\WarscapeInventory-Phase1-Deploy-20261027-154742`; final
pre-refresh runtime backups and another fresh verified private character
snapshot are at
`C:\WoWDev\Backups\WarscapeInventory-Phase1-Final-20261027-155942`.

No offline character rewrite, schema migration, privilege change or automatic
updater was executed. Client settings/SavedVariables and native executable were
not edited. The client and both servers remain stopped; no manual game test,
commit or push was performed.
