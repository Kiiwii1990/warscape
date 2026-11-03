-- Warscape Smithing: additive defaults preserve all existing skill progress.
ALTER TABLE `warscape_skills`
  ADD COLUMN `smithing_xp` INT UNSIGNED NOT NULL DEFAULT 0 AFTER `mining_xp`,
  ADD COLUMN `smithing_half_xp` TINYINT UNSIGNED NOT NULL DEFAULT 0 AFTER `mining_half_xp`;
