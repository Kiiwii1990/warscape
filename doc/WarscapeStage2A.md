# Stage 2A — interactive skills panel

Source: `addons/WarscapeSkills`. Original client interface version: 30300
(WoW 3.3.5a, build 12340). No executable patch or database migration is needed.

## Use and appearance

Enable **Warscape Skills** in the character selection AddOns list. **N** toggles
the panel when N is still assigned to the original Talents action. `/wskills`
also toggles it; Escape or the integrated close button closes it. Drag the frame
to move it. Position is saved per character by the client's SavedVariables system.
The panel starts closed and subscribes automatically on login and UI reload.

The seven combat skills retain their original native WoW spell/item icons. The
26 October UI correction supersedes the original native-dialog appearance with
separate textures sliced locally from the approved reference: fully opaque dark
stone, thick gold/metal borders, sculpted corner dragons, recessed cells, silver
icon sockets and a total-level footer. The skin uses real nine-slice frames and
independent ornaments; it is not a flattened illustration of the panel.
Tooltips show base level, available current level, cumulative XP, next threshold,
remaining XP and progress. Maximum-level bars are full. No boosts currently exist;
the server sends an unavailable marker, and both sides display the base level
(for example `12 / 12`). Future current levels can display `15 / 12`. Total level
sums base levels from the complete server snapshot, never temporary boosts.
The reference's unimplemented tabs and Slayer skill are deliberately absent.

The supported addon action **Toggle Warscape Skills** appears under **Warscape**
in Key Bindings. A session-local override replaces the default N/Talents binding
without changing saved bindings, modifying Blizzard talent functions or disabling
the talent system. A custom action on N, an unbound N, or an explicit key assigned
to the addon takes precedence over the automatic default. Changes reapply after
login, UI reload or binding changes; protected binding changes defer until combat
ends. If N is custom-bound, use `/wskills` or assign the addon action yourself.

## Data channel and safeguards

The addon sends `WCSkills` addon-prefix traffic by whisper to its own character:
`HELLO|1|<session token>`. The server accepts only this read-only handshake from
an in-world player targeting themselves. The reserved prefix is consumed on all
supported addon distributions before ordinary chat and GM command handling. It
cannot relay forged skills to another player or dispatch a privileged command.
Subscriptions are session-local and rate-limited to one per second. Existing
server addon-channel configuration remains authoritative.

The server reads the same `rsSkills` used by `.rs stats` and persistence. Login
subscription sends a complete snapshot; successful XP or GM skill changes mark
it dirty. Updates are coalesced to at most four snapshots per second, with no
continuous polling once synchronized. The first login handshake retries every two
seconds until data arrives. An incomplete snapshot expires after five seconds
and requests a replacement. No skill writes or schema changes are made by the UI.

Version 1 messages (each below the client's 255-byte addon limit):

```
B|1|token|revision|count
S|1|token|revision|stable_id|base|effective_or_-|xp|level_floor|next_threshold_or_-
E|1|token|revision
```

Only complete snapshots with matching token/revision, unique IDs and validated
numeric ranges are displayed. The receiver accepts only self-whisper responses;
old revisions and other senders are ignored. The token correlates UI reloads,
not an authentication secret. Stable IDs separate protocol identity from labels.
New skills require persistence/server metadata and optional client label/icon
metadata; the grid expands automatically and unknown IDs use a question-mark icon.
Mining, Smithing, Stage 2B and Stage 1H are not implemented.

## Automated verification

Build the full configured x64 solution with `cmake --build build --config Release`.
Run `build/bin/Release/tests.exe --reporter compact` with the server runtime DLLs
on PATH. The C++ suite covers handshake rejection, level threshold serialization
and packet bounds in addition to existing combat tests.

Run `python addons/WarscapeSkills/tests/test_addon.py` and
`python addons/WarscapeSkills/tests/test_bindings.py` with `lupa` installed.
It explicitly uses Lua 5.1 and tests malformed/duplicate/incomplete/replayed
snapshots, max level, future IDs, tooltip handlers, open/close, saved position and
the login handshake, total base level, reference column order, current/base
formatting, integrated close action and dynamic sizing. Binding tests cover the
default N, customized/unbound keys, explicit addon bindings and combat deferral.
Run `python addons/WarscapeSkills/tests/test_skin.py` with Pillow installed to
check all 12 TGA formats, alpha and dimensions. The UI mock and local preview do
not verify real client rendering/networking. No server rebuild is needed for the
UI-only correction; the server channel and combat code are unchanged.

## Safe local deployment

Keep the client closed while replacing addon files. Keep authserver/worldserver
stopped when replacing server binaries. Back up previous versions outside Git.
For a UI-only update, leave server processes/binaries untouched. Copy runtime files
(`.toc`, `.lua`, `Bindings.xml`, and `art/*.tga`), and compare SHA-256 hashes. Do not
copy generated configuration over local configuration. Keep database updater
settings unchanged and do not start an updater as part of deployment.

## In-game acceptance

1. Restart the client after installation so it discovers `Bindings.xml`. Press N:
   only Skills should toggle. Also test `/wskills`, the close button and Escape.
   Check opaque stone, both dragons, beveled borders, labels and the native icons.
2. Compare Attack, Strength, Defence, Hitpoints, Ranged, Magic and Prayer against
   `.rs stats` on your QA character. Check `current / base` and the summed total.
   Ordinary players need no GM rights for UI data.
3. Hover each skill: check total XP, next threshold, remaining XP and percentage.
4. Gain actual combat XP from eligible creatures; verify automatic bar/tooltip
   updates. Training dummies deliberately award no XP.
5. Gain a skill level; verify the new level and progress without reopening the UI.
6. Move the panel, `/reload`, reopen with N, and confirm position/current data.
   Relog and repeat. Verify a custom action on N remains intact, then restore your
   default binding or assign **Toggle Warscape Skills** explicitly.

Stop Stage 2A development at this handoff until the user confirms these tests.
