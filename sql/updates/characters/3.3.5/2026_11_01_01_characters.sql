-- Preserve the deployed half-point carry exactly; legacy column retained.
ALTER TABLE warscape_skills ADD COLUMN smithing_tenth_xp TINYINT UNSIGNED NOT NULL DEFAULT 0 AFTER smithing_half_xp;
UPDATE warscape_skills SET smithing_tenth_xp=smithing_half_xp*5;
