# Warscape UI Hide

`addons/WarscapeUIHide` selectively hides standard WoW 3.3.5a gameplay HUD frames. It never hides `UIParent`, chat, chat input, `GameMenuFrame`, tooltips, `UIErrorsFrame`, or WarscapeSkills frames. Frame names were checked against the custom wowdecomp client's local 3.3.5a `FrameXML` assets.

The maintained frame list covers the player/target/focus/pet frames; the main action bar (including its XP/reputation display, micro menu and bag buttons); the four multibars; default buffs and temporary enchants; player, pet, target and focus cast bars; stance, pet, possess, bonus, multicasting and vehicle bars; combo points, runes and alternate player resource bars. The minimap cluster is left available for WarscapeHUD, which reparents it into the replacement bottom-centre HUD. Nameplates, unit names, chat bubbles and combat text remain under their existing settings and are not modified.

Visibility is snapshotted per frame and restored to its previous shown/hidden state. `OnShow` hooks hide only listed HUD frames that appear later, such as vehicle bars. HUD changes requested during combat are deferred until `PLAYER_REGEN_ENABLED`. The existing `WarscapeUIHidden` per-character preference is preserved. A one-time upgrade path restores the previous addon's saved presentation CVar values, then leaves those CVars untouched.

## Use and recovery

- `/warscapeui hide`, `/warscapeui show`, and `/warscapeui toggle` work through the visible chat frame.
- **Ctrl+Alt+F12** toggles the HUD when chat is unavailable. It is an owner-scoped, session-only override and does not replace WarscapeSkills' N binding or modify saved keybindings.
- First login with the addon enabled starts in Warscape mode. Subsequent login/reload restores the saved mode.
- The main action buttons and their keybindings remain loaded. Bag, character, spellbook, quest, map and game-menu windows remain accessible through their existing bindings; **Escape** remains unmodified.

## Automated checks

Run:

```powershell
py -m unittest discover -s addons\WarscapeUIHide\tests -v
py addons\WarscapeSkills\tests\test_addon.py
py addons\WarscapeSkills\tests\test_bindings.py
```

The UI Hide Lua 5.1 mock verifies that `UIParent` is never hidden, listed Blizzard HUD frames are hidden/restored, hidden frames preserve their original visibility, chat/input, tooltips, errors, game menu and WarscapeSkills remain available, legacy CVars restore, dynamic vehicle bars are suppressed, the N binding is retained, combat deferral works, and slash/recovery toggles work. WarscapeSkills' existing UI and binding tests verify its panel open/close and N-key policy. These offline tests do not replace the user's in-game visual/input confirmation.

## Local deployment

The runtime target is `C:\WoWDev\wowdecomp\bin\Win\Interface\AddOns\WarscapeUIHide`. The custom client source's `SetPaths()` uses `-datadir` when supplied and otherwise the executable directory. Before each deployment, verify the wowdecomp executable and effective data directory; keep the client closed, back up the previous addon directory outside Git, copy only `.toc`, `.lua` and `Bindings.xml`, and compare SHA-256 hashes. No server, database, gameplay, client executable, local settings or SavedVariables files are modified by deployment.

Selective HUD deployment record (2026-10-26): the client was stopped; the default game directory was selected from the wowdecomp `SetPaths()` source fallback, and the three runtime files were hash-verified after copying. The previous deployed addon is backed up at `C:\WoWDev\Backups\WarscapeUIHide-selective-20261026-210926-014`. The client was not launched for manual testing.

## Known boundaries

This addon hides only the selected in-world HUD. It does not hide normal chat, menus, open inventory/quest/map windows, tooltips, system errors, player/NPC names, nameplates, floating combat feedback, loading/login screens, cinematics or the cursor. It does not create replacement UI. Final visual behavior and gameplay input require user in-game confirmation.
