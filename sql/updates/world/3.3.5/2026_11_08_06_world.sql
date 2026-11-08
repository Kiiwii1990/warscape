-- Generated enemy release 2026_11_08_06_world; additive to prior releases.
INSERT INTO creature_template (entry,modelid1,name,minlevel,maxlevel,faction,scale,speed_walk,speed_run,BaseAttackTime,RangeAttackTime,unit_class,type,lootid,AIName,ExperienceModifier,RegenHealth) VALUES (902500,4449,'Death spawn (OSRS regular_46)',46,46,31,0.7,1,1.14286,2400,2400,1,3,1640000,'AggressorAI',0,1);
INSERT INTO warscape_monster_profile (id,name,base_attack,base_strength,base_defence,base_ranged,base_magic,base_hitpoints,growth_attack,growth_strength,growth_defence,growth_ranged,growth_magic,growth_hitpoints,attack_bonus,strength_bonus,defence_bonus) VALUES (2500,'Death spawn (OSRS regular_46)',67,7,30,1,1,60,0,0,0,0,0,0,0,0,20);
INSERT INTO warscape_monster_template (entry,profile_id) VALUES (902500,2500);
INSERT INTO warscape_monster_attack_speed VALUES (902500,4);
INSERT INTO creature_loot_template (Entry,Item,Chance,MinCount,MaxCount,Comment) VALUES (1640000,902327,100,1,1,'OSRS family catalogue guaranteed outcome');
INSERT INTO warscape_enemy_variant (creature_entry,family_id,subcategory,source_url,source_npc_ids,source_sha256,attack_style,source_max_hit,slayer_xp,respawn_ticks,source_poison_resistance) VALUES (902500,88,'death_spawn_46','https://oldschool.runescape.wiki/w/Death_spawn','10','b52de258d0d72d201262962a10e4c2fd16a721a30b8a5e4ed08f412c282fbc98','slash',2,0,15,0);
UPDATE warscape_enemy_variant SET defence_stab=20,defence_slash=20,defence_crush=20,use_source_combat=1,flat_armour=0,source_slayer_level=0 WHERE creature_entry=902500;
UPDATE warscape_enemy_variant SET source_slayer_xp_tenths=0 WHERE creature_entry=902500;
UPDATE creature_template SET AIName='',ScriptName='npc_warscape_death_spawn' WHERE entry=902500;
UPDATE creature_template SET AIName='',ScriptName='npc_warscape_nechryael' WHERE entry=902400;
