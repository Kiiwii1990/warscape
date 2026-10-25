-- Warscape world database extension. Additive and safe to run more than once.
-- Does not change creature_template, live health, or character data.
CREATE TABLE IF NOT EXISTS `warscape_monster_profile` (
  `id` INT UNSIGNED NOT NULL,
  `name` VARCHAR(80) NOT NULL,
  `base_attack` INT UNSIGNED NOT NULL DEFAULT 1,
  `base_strength` INT UNSIGNED NOT NULL DEFAULT 1,
  `base_defence` INT UNSIGNED NOT NULL DEFAULT 1,
  `base_ranged` INT UNSIGNED NOT NULL DEFAULT 1,
  `base_magic` INT UNSIGNED NOT NULL DEFAULT 1,
  `base_hitpoints` INT UNSIGNED NOT NULL DEFAULT 10,
  `growth_attack` INT UNSIGNED NOT NULL DEFAULT 100,
  `growth_strength` INT UNSIGNED NOT NULL DEFAULT 100,
  `growth_defence` INT UNSIGNED NOT NULL DEFAULT 100,
  `growth_ranged` INT UNSIGNED NOT NULL DEFAULT 100,
  `growth_magic` INT UNSIGNED NOT NULL DEFAULT 100,
  `growth_hitpoints` INT UNSIGNED NOT NULL DEFAULT 100,
  `attack_bonus` INT NOT NULL DEFAULT 0,
  `strength_bonus` INT NOT NULL DEFAULT 0,
  `defence_bonus` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `warscape_monster_template` (
  `entry` INT UNSIGNED NOT NULL COMMENT 'creature_template.entry',
  `profile_id` INT UNSIGNED NOT NULL DEFAULT 0,
  `attack_override` INT UNSIGNED NOT NULL DEFAULT 0,
  `strength_override` INT UNSIGNED NOT NULL DEFAULT 0,
  `defence_override` INT UNSIGNED NOT NULL DEFAULT 0,
  `ranged_override` INT UNSIGNED NOT NULL DEFAULT 0,
  `magic_override` INT UNSIGNED NOT NULL DEFAULT 0,
  `hitpoints_override` INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`entry`),
  KEY `idx_profile` (`profile_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Existing balance edits survive migration reapplication.
INSERT INTO `warscape_monster_profile` (`id`, `name`, `base_defence`, `growth_defence`)
VALUES (0, 'Neutral fallback', 1, 100), (1, 'Goblin', 1, 60), (2, 'Golem', 10, 150)
ON DUPLICATE KEY UPDATE `id` = VALUES(`id`);
-- Test entries verified against the shipped TDB world dump:
-- Harvest Golem (36), Rusty Harvest Golem (480), and three Warsong goblins.
-- Keep existing per-creature tuning if this additive seed is reapplied.
INSERT INTO `warscape_monster_template` (`entry`, `profile_id`)
VALUES (36, 2), (480, 2), (622, 1), (638, 1), (641, 1)
ON DUPLICATE KEY UPDATE `entry` = VALUES(`entry`);

