-- Adds the persistent Warscape copper mining rock template only.
-- GM-created spawns use this template and remain independent per GameObject.
INSERT INTO `gameobject_template`
    (`entry`, `type`, `displayId`, `name`, `size`, `AIName`, `ScriptName`, `VerifiedBuild`)
VALUES
    (900101, 3, 310, 'Warscape Copper Rock', 1, '', 'go_warscape_copper_rock', 12340);
