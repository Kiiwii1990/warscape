-- AGI-005A follow-up: store a normalized GameObject rotation quaternion.
UPDATE `gameobject`
SET `rotation2` = 0.794748233601,
    `rotation3` = -0.606939243407
WHERE `id` = 900700
  AND `map` = 0
  AND ABS(`position_x` - (-9074.780273)) < 0.001
  AND ABS(`position_y` - (-195.128021)) < 0.001
  AND ABS(`position_z` - 71.909966) < 0.001
  AND ABS(`orientation` - 4.446) < 0.001;
