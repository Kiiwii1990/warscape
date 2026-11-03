-- Warscape Agility: the default preserves existing character XP exactly.
ALTER TABLE `warscape_skills`
  ADD COLUMN `agility_xp` INT UNSIGNED NOT NULL DEFAULT 0 AFTER `smithing_xp`;
