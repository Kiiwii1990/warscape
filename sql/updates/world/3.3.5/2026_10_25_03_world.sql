-- Development utility only. No permanent map spawns are added by this migration.
-- Borrow only the stock dummy model; no stock combat/AI/immunity flags are copied.
INSERT INTO `creature_template`
    (`entry`, `modelid1`, `name`, `minlevel`, `maxlevel`, `faction`, `unit_class`,
     `type`, `npcflag`, `unit_flags`, `dynamicflags`, `MovementType`, `RegenHealth`,
     `lootid`, `pickpocketloot`, `skinloot`, `mingold`, `maxgold`, `ExperienceModifier`,
     `KillCredit1`, `KillCredit2`, `AIName`, `ScriptName`, `flags_extra`)
SELECT 900001, `modelid1`, 'Warscape Training Dummy', 1, 1, 14, 1,
       9, 0, 0, 0, 0, 1,
       0, 0, 0, 0, 0, 0,
       0, 0, '', 'npc_warscape_training_dummy', 262466
FROM `creature_template` WHERE `entry`=31144;
-- Flags: civilian (2), no XP (64), no taunt (256), no weapon-skill gains (262144).
