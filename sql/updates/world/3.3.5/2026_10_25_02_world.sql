-- Stage 1G: explicit material tiers for baseline weapons only.
-- Existing warscape_item_bonus rows remain complete authoritative overrides.
-- No item_template, character, speed, or existing balance data is changed.
CREATE TABLE `warscape_weapon_rule` (
    `item_id` INT UNSIGNED NOT NULL,
    `tier` TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '1 Bronze, 2 Iron, 3 Steel, 4 Mithril, 5 Adamant, 6 Rune',
    `archetype` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '0 WoW subclass inference; 1-10 explicit melee archetype',
    PRIMARY KEY (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Deliberately small QA mapping, not a general WoW-to-OSRS material inference.
-- Both are subclass 7 swords; retain automatic Longsword classification.
INSERT INTO `warscape_weapon_rule` (`item_id`, `tier`, `archetype`) VALUES
    (2850, 1, 0), -- Bronze Shortsword: Bronze baseline
    (7944, 4, 0); -- Dazzling Mithril Rapier: Mithril baseline
