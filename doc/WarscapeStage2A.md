# Stage 2A — interactive skills panel

Source: `addons/WarscapeSkills`. Original client interface version: 30300
(WoW 3.3.5a, build 12340). No executable patch or database migration is needed.

## Use and appearance

Enable **Warscape Skills** in the character selection AddOns list. `/wskills`
toggles the panel; Escape or the native close button closes it. Drag the frame
to move it. Position is saved per character by the client's SavedVariables system.
The panel starts closed and subscribes automatically on login and UI reload.

The seven combat skills use native WoW spell/item icons, gold labels, green XP
bars and a native dialog frame. Two mirrored native elite-target dragon ornaments
are the close WoW-style equivalent of the approved illustrated dragons. The exact
reference artwork is not reproduced; the ornaments are separate UI textures.
Tooltips show base level, available current level, cumulative XP, next threshold,
remaining XP and progress. Maximum-level bars are full. No boosts currently exist;
the server sends an unavailable marker, and the addon displays the base level.
Future current levels can display `15/12` without replacing the layout.

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

Run `python addons/WarscapeSkills/tests/test_addon.py` with `lupa` installed.
It explicitly uses Lua 5.1 and tests malformed/duplicate/incomplete/replayed
snapshots, max level, future IDs, tooltip handlers, open/close, saved position and
the login handshake. Its UI mock does not verify real client rendering/networking.

## Safe local deployment

Keep the client and authserver/worldserver stopped while replacing files. Back up
existing deployed executables and any previous addon outside Git, copy only built
executables and the three addon runtime files, and compare SHA-256 hashes. Do not
copy generated configuration over local configuration. Keep database updater
settings unchanged and do not start an updater as part of deployment.

## In-game acceptance

1. Open/close with `/wskills`, the close button and Escape. Check both dragons,
   labels and all seven icons at your normal UI scale.
2. Compare Attack, Strength, Defence, Hitpoints, Ranged, Magic and Prayer against
   `.rs stats` on your QA character. Ordinary players need no GM rights for UI data.
3. Hover each skill: check total XP, next threshold, remaining XP and percentage.
4. Gain actual combat XP from eligible creatures; verify automatic bar/tooltip
   updates. Training dummies deliberately award no XP.
5. Gain a skill level; verify the new level and progress without reopening the UI.
6. Move the panel, `/reload`, reopen and confirm position and current data persist.

Stop Stage 2A development at this handoff until the user confirms these tests.
