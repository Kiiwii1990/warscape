# AGI-001B automatic traversal prototype

This developer-only prototype tests whether the server can drive a player over a short WotLK spline on the Eastern Kingdoms map (map 0), near Northshire Abbey. It adds no skill data, XP, persistence, obstacles, spawns, database changes or client assets.

## AGI-001B manual result

The user confirmed an in-game Northshire stream crossing was smooth, reached the destination, ignored WASD input while the spline was active, and restored normal player control when it completed. This confirms the tested happy path only. Explicit `.agi stop`, replacement movement, combat, death, map leave, logout/relogin and timeout interruption cases have not been confirmed as passing.

## Activation

1. Build the `RelWithDebInfo` `worldserver` target and start the local Warscape server normally.
2. Log in with a GM character and teleport to the Northshire test start:

   ```text
   .go xyz -9066.463867 -199.568985 70.600822 0
   ```

3. Run `.gps` at the start and confirm map 0 and the measured start position/ground (`X=-9066.463867 Y=-199.568985 Z=70.600822`, ground `70.599129`). The endpoint was measured as `X=-9072.518555 Y=-214.185699 Z=70.450348`, ground `70.451462`. The direct spline crosses the small stream between these endpoints; its intermediate surface/path, collision and any log collision have not been verified. Do not run it unless you have visually checked the crossing and it is clear of hazards and nearby players; stop if uncertain.
4. Run `.agi start`. The command starts a server-controlled spline directly to the measured endpoint. It only accepts a living GM within 8 yards of the Northshire test origin, outside combat, flight, mount and vehicle states.
5. Run `.agi stop` to interrupt and clear the attempt. A completed spline is detected by its spline ID/finalized state. Death, combat, map leave, logout, replacement movement or a 12-second timeout ends the session.

The endpoints are in-game measured positions. Only the endpoints and ground heights have been verified; the intermediate stream surface/path and any log collision are unverified. This direct two-point route is a minimal movement experiment, not a terrain-safe path or obstacle course. The prototype deliberately does not root the player. The observed WASD result applies to the confirmed test only; other inputs and interruption paths remain unverified.

## Manual client check

- Confirm `.gps` reports map 0 and the measured start `(-9066.463867, -199.568985, 70.600822)` (ground `70.599129`); inspect the full stream crossing before `.agi start`.
- Confirm the player's model moves smoothly and reaches the measured endpoint `(-9072.518555, -214.185699, 70.450348)` (ground `70.451462`).
- Confirm the player remains controllable after arrival. **Confirmed by user.**
- Hold WASD during traversal and confirm the spline continues. **Confirmed by user.** Other inputs have not been tested.
- `.agi stop` control restoration and each interruption scenario below remain follow-up checks, not passed results.
- Repeat the command and verify one attempt per map instance.
- Interrupt with ordinary movement input, then retry; verify no movement lock or stale session remains.
- If practical, interrupt with combat, death, map leave and logout/relogin; verify cleanup and that a later attempt works.

Server compilation does not establish WotLK client synchronization or in-game movement behavior. The developer-only W-input experiment remains deferred until this baseline is observed.
