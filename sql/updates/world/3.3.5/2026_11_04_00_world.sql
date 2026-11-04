-- AGI-005A: clickable Northshire Agility log proxy.
-- Uses the stock fallen-tree display and preserves the terrain log and all existing rows.
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `AIName`, `ScriptName`, `VerifiedBuild`)
VALUES (900700, 10, 8028, 'Northshire Agility Log', 0.65, '', 'go_warscape_agility_obstacle', 12340);

INSERT INTO `gameobject` (`id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `VerifiedBuild`)
VALUES (900700, 0, 12, 9, 1, 1, -9074.780273, -195.128021, 71.909966, 4.446, 0, 0, 0.795, -0.606, 0, 255, 1, 12340);
