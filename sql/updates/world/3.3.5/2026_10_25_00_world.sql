CREATE TABLE IF NOT EXISTS `warscape_item_bonus` (
    `item_id` INT UNSIGNED NOT NULL,
    `archetype` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '0=WoW subclass inference; 1-14=explicit Warscape archetype',
    `tier` INT UNSIGNED NOT NULL DEFAULT 0,
    `attack_stab` INT NOT NULL DEFAULT 0,
    `attack_slash` INT NOT NULL DEFAULT 0,
    `attack_crush` INT NOT NULL DEFAULT 0,
    `attack_ranged` INT NOT NULL DEFAULT 0,
    `attack_magic` INT NOT NULL DEFAULT 0,
    `defence_stab` INT NOT NULL DEFAULT 0,
    `defence_slash` INT NOT NULL DEFAULT 0,
    `defence_crush` INT NOT NULL DEFAULT 0,
    `defence_ranged` INT NOT NULL DEFAULT 0,
    `defence_magic` INT NOT NULL DEFAULT 0,
    `melee_strength` INT NOT NULL DEFAULT 0,
    `ranged_strength` INT NOT NULL DEFAULT 0,
    `magic_damage` INT NOT NULL DEFAULT 0,
    `prayer` INT NOT NULL DEFAULT 0,
    `attack_speed` INT UNSIGNED NOT NULL DEFAULT 0,
    `generation_version` INT UNSIGNED NOT NULL DEFAULT 0,
    `generation_seed` BIGINT UNSIGNED DEFAULT NULL,
    PRIMARY KEY (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Fixed Stage 1E QA profiles. INSERT IGNORE keeps this migration repeatable and
-- preserves any profile already customized on a server.
INSERT IGNORE INTO `warscape_item_bonus`
    (`item_id`, `archetype`, `tier`, `attack_stab`, `attack_slash`, `attack_crush`, `melee_strength`)
VALUES
    (2494, 1, 1, 8, -2, -4, 2),  -- Stiletto: Dagger
    (2488, 4, 1, 2, 8, 0, 4),    -- Gladius: Longsword
    (2489, 5, 1, 0, 12, -2, 9),  -- Two-handed Sword
    (2493, 7, 1, -3, -4, 10, 7); -- Wooden Mallet: Warhammer
