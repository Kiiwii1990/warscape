-- Dust Devil attack carrier; source profile/loot remain unchanged.
INSERT INTO spell_script_names (spell_id,ScriptName) VALUES (900790,'spell_warscape_ranged_melee');
UPDATE creature_template SET AIName='',ScriptName='npc_warscape_dust_devil' WHERE entry IN (902204,902205);
