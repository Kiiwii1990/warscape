# Warscape Agility traversal prototypes

These developer-only commands test server-controlled player splines near Northshire Abbey on map 0. The AGI-001B stream remains a prototype. The AGI-003A log route now uses the AGI-004A obstacle reward and requires the prepared character migration before the updated worldserver can run.

## AGI-001B stream prototype

The user confirmed the short Northshire stream crossing was smooth, reached its destination, ignored WASD input during the spline, and restored control on completion. This confirms only that happy path. Use `.agi start` for the earlier route, or `.agi stop` to interrupt an active route.

## AGI-003A measured log route

The seven positions below were measured by the user with `.gps` on map 0, in traversal order. Points 3–5 were recorded while standing normally on the log.

| # | Point | X | Y | Z |
|---|---|---:|---:|---:|
| 1 | Approach | -9074.780273 | -195.128021 | 71.909966 |
| 2 | Takeoff | -9075.851562 | -197.076318 | 70.528038 |
| 3 | Near-log | -9076.198242 | -199.217316 | 71.087822 |
| 4 | Log midpoint | -9077.499023 | -203.898041 | 71.180267 |
| 5 | Far-log | -9078.817383 | -209.583771 | 71.663506 |
| 6 | Step-off | -9079.299805 | -211.528687 | 70.387108 |
| 7 | Landing | -9079.845703 | -213.721573 | 70.746696 |

The first and second readings differ in height by about 1.38 game units, and the far-log to step-off readings differ by about 1.28. The route follows the measured Z values; it does not add guessed jump or fall animations. It uses a walking spline at 2.5 units/second with a 30-second timeout. Facing follows the spline path. Server/client presentation and traversal through the measured elevation changes require in-game acceptance.

## Run the GM test

1. Build the `RelWithDebInfo` `worldserver` target and start the local Warscape server normally.
2. Log in as a GM and visually check the crossing is clear of hazards and nearby players. The client `patch-4.MPQ` only changes client terrain data; it does **not** prove that server VMAP collision includes the log. Do not treat this waypoint route as a collision-safe gameplay path until server collision is independently verified.
3. Stand within 30 yards horizontally of the measured approach point on map 0:

   ```text
   .go xyz -9074.780273 -195.128021 71.909966 0
   .gps
   ```

4. Run `.agi start log`. Observe the approach descent, log crossing, step-off drop, and landing. Use `.agi stop` to interrupt.
5. After arrival, confirm control is restored. Repeat from the approach point only after checking the player and crossing are in a safe state.

The handler accepts only a living GM on non-instanced map 0, outside combat, flight, mount, and vehicle states. Only one route may own a map instance at a time. The start point is included in the spline (seven measured points, so the path has more than one point); route coordinates must be finite. Completion clears the session; explicit stop, replacement movement, combat/death, map leave, logout, and timeout stop/clear the active session. These cleanup paths are implemented, but require in-game validation.

### AGI-003A user-confirmed in-game result

The user confirmed that the seven-waypoint Northshire log traversal worked in-game. They spammed movement buttons during traversal and the route continued to hold. This confirms the tested traversal and movement-button behavior only. It does not confirm interruption cleanup, server collision coverage, exact collision support, or behavior in other scenarios.

## AGI-004A obstacle reward

The Northshire log is registered as a reusable obstacle definition, separate
from the shared traversal/session runner. It requires Agility level 1 and has a
50% success chance for testing. A failed roll displays `Agility Roll Failed`,
awards no XP and starts no movement. A successful roll awards exactly 8 Agility
XP immediately before starting the existing spline. Traversal completion only
clears the session; interruption after acceptance does not remove XP, and
repeated commands while active are rejected without another reward. These
attempt/reward timings need in-game verification. See
[WarscapeAgilityAGI004A.md](WarscapeAgilityAGI004A.md) for migration, rollback
limits and acceptance steps. At level 1, 83 is XP required for level 2; inspect
the tooltip's `Total XP` line to confirm earned XP.

## Acceptance checks

- Confirm `.gps` reports map 0 and the player starts within 30 horizontal yards of point 1.
- Observe whether the character descends toward point 2, stays on/near points 3–5, steps off near point 6, and reaches point 7. Record where client/server position diverges, if it does.
- Check whether movement input is ignored while the spline is active and whether ordinary control returns after arrival. **User-confirmed for the tested traversal, including spamming movement buttons.**
- Interrupt with `.agi stop`, ordinary movement, combat, death, map leave, and logout/relogin where practical; verify the route ends and a later attempt can start.
- Verify a second player cannot start another route in the same map instance while one is active.
- Treat interruption behavior, server-side log/terrain collision coverage, and exact collision support as unverified until tested separately. In particular, successful traversal does not establish that VMAP includes the client-only ADT patch.
