-- Copper Ore should occupy one inventory slot per item.
-- Preserve maxcount (the per-character ownership limit) and all other item data.
UPDATE `item_template`
SET `stackable` = 1
WHERE `entry` = 2770 AND `stackable` = 20 AND `maxcount` = 0;
