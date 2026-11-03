-- Stage 1F extends the existing item profiles without changing item_template
-- or character inventory data. MariaDB's IF NOT EXISTS makes schema replay safe.
ALTER TABLE `warscape_item_bonus`
    ADD COLUMN IF NOT EXISTS `attack_speed_ticks` TINYINT UNSIGNED NOT NULL DEFAULT 4
    COMMENT 'Warscape melee interval in 600ms ticks; supported values 2-12'
    AFTER `attack_speed`;

-- Assign the fixed provisional Stage 1F test speeds only while a profile still
-- has the default. Re-running this migration preserves non-default overrides.
UPDATE `warscape_item_bonus` SET `attack_speed_ticks`=3 WHERE `item_id`=2494 AND `attack_speed_ticks`=4;
UPDATE `warscape_item_bonus` SET `attack_speed_ticks`=7 WHERE `item_id`=2489 AND `attack_speed_ticks`=4;
UPDATE `warscape_item_bonus` SET `attack_speed_ticks`=5 WHERE `item_id`=2493 AND `attack_speed_ticks`=4;

CREATE TABLE IF NOT EXISTS `warscape_monster_attack_speed` (
    `creature_entry` INT UNSIGNED NOT NULL,
    `attack_speed_ticks` TINYINT UNSIGNED NOT NULL DEFAULT 4 COMMENT 'Warscape melee interval in 600ms ticks; supported values 2-12',
    PRIMARY KEY (`creature_entry`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Harvest Golem is a mapped Warscape test creature; other entries default to 4.
INSERT IGNORE INTO `warscape_monster_attack_speed` (`creature_entry`, `attack_speed_ticks`) VALUES
    (36, 5);
