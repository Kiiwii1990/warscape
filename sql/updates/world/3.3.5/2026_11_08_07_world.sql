-- Lit bug lantern uses native off-hand equipment and a shared source damage requirement.
INSERT INTO item_template (entry,class,subclass,name,displayid,Quality,BuyCount,stackable,AllowableClass,AllowableRace,InventoryType,description,Material) SELECT 902586,4,0,'Lit bug lantern',displayid,1,1,1,-1,-1,23,'Equip in your off-hand to harm Harpie Bug Swarms.',Material FROM item_template WHERE entry=5323;
UPDATE creature_template SET AIName='',ScriptName='npc_warscape_enemy' WHERE entry=902301;
