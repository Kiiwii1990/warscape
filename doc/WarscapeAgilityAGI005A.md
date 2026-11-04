# AGI-005A: Northshire log clickable GameObject

## Implemented

Entry `900700` is a client-visible Goober GameObject named **Northshire Agility
Log**. It uses the stock WotLK display `8028` (`World\\Azeroth\\RedRidge\\PassiveDoodads\\Trees\\RedRidgeFallenTree01.mdx`) at the existing template's tested scale of `0.65`. Its permanent map-0 spawn is at the measured first waypoint, `(-9074.780273, -195.128021, 71.909966)`, orientation `4.446` radians. That places the interaction target at the start of the proven seven-point route; the model's visual fit over the ShadowWorld terrain log still needs in-game confirmation.

The GameObject template binds `go_warscape_agility_obstacle`. Its shared `GameObjectAI::OnGossipHello` resolves the entry through the obstacle registry and starts the existing attempt runner. The Northshire definition keeps the level-1 requirement, 8 XP reward, 100% success chance, 30-yard route-start validation radius, walk speed and seven measured waypoints. XP is granted at accepted attempt time, before the server spline starts. The GM command remains available for diagnostics, but normal use is a right-click on the visible log object.

## Stock 3.3.5a behavior

The core validates a normal `CMSG_GAMEOBJ_USE` by object GUID, map/phase and the GameObject's interaction distance before calling `GameObject::Use`. Goober objects use the default interaction distance (normally five yards). The stock client supports Click-to-Move for right-clicking interactive objects: from beyond interaction range it can move the character to range, then send the interaction. Therefore:

- A right-click at interaction range should reach the server script immediately, award 8 Agility XP, and begin the existing server-controlled spline.
- A distant right-click should still work as one click with Click-to-Move enabled. The initial approach is client-controlled; the server attempt, XP award and locked traversal begin only when the normal use request reaches the server at interaction range.
- Immediate server acceptance, XP before approach, and server movement lock across the entire distant approach require a client click-intent change. No client executable or addon changes are included in AGI-005A.

The accepted use handler and obstacle script log the GameObject GUID, player position, range-check result, attempt result, XP before/after, spline result, completion and interruption. If the client queues its use until it reaches range, the first server packet log will appear on arrival; the server cannot log the original mouse-down in that case. These diagnostics are intended to verify that stock-client behavior in-game.

## Database migration and rollback

`sql/updates/world/3.3.5/2026_11_04_00_world.sql` additively creates
the custom template and permanent spawn. Its verification file checks that the
reserved template/spawn IDs were free and that the expected template and Northshire
spawn exist after application. The migration leaves all vanilla rows, terrain
assets, character data and existing skill XP unchanged.

`2026_11_04_01_world.sql` stores the spawn's normalized yaw quaternion. Its first
apply executed the update but an overly exact float verification failed. The
stored row was inspected, the verifier was corrected to account for float
precision, and `db.py recover` verified the postcondition and recorded the
existing migration without rerunning its SQL. The retained lock was released
only after the update ledger confirmed the migration.

The migration is applied through `contrib/warscape/db.py` after stopping the
worldserver and other schema writers; the tool creates a fresh verified backup
before execution. Since the migration is recorded in `updates`, do not remove its
rows with an ad-hoc delete. If the prototype must be removed later, add and review
a new forward migration deleting only this spawn and template, after checking for
references. Keeping the template/spawn while rolling back the server binary leaves
an inert custom Goober object, so it should not be treated as a complete feature
rollback.

## In-game acceptance

1. Travel to the Northshire log, map 0, near `-9074.78, -195.13, 71.91`.
2. Right-click the visible fallen-tree/log proxy from within interaction range.
3. Confirm `Agility Roll Succeeded (+8 XP).` appears, Agility XP increases by
   exactly 8 before the character steps onto the log, and the seven-waypoint
   traversal begins with movement locked.
4. Confirm normal control returns at landing and repeated valid crossings each
   add exactly 8 XP.
5. With Click-to-Move enabled, right-click the object from farther away. Confirm
   the client approaches and then the obstacle starts. Compare server log packet
   timestamps with arrival to determine whether this client sends an initial
   distant use packet or queues use until the normal interaction range.
6. Confirm the XP and skill UI persist after relogging, and check startup logs
   for the registered GameObject script and migration-loaded spawn.

Visual placement, collision interaction with the existing terrain log, and
stock-client distant-click packet timing require user in-game acceptance.
