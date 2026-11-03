ALTER TABLE `warscape_skills`
  ADD COLUMN `mining_xp` INT UNSIGNED NOT NULL DEFAULT 0 AFTER `prayer_xp`,
  ADD COLUMN `mining_half_xp` TINYINT UNSIGNED NOT NULL DEFAULT 0 AFTER `mining_xp`;
