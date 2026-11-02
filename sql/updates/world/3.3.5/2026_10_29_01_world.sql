-- Adds a standalone, non-interactable grayscale copper-rock test prop.
-- This is deliberately separate from the mineable 900101 template.
INSERT INTO `gameobject_template`
    (`entry`, `type`, `displayId`, `name`, `size`, `AIName`, `ScriptName`, `VerifiedBuild`)
VALUES
    (900103, 5, 900102, 'Warscape Grayscale Copper Rock', 1, '', '', 12340);

INSERT INTO `gameobject_template_addon`
    (`entry`, `flags`)
VALUES
    (900103, 16);
