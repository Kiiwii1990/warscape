-- Refillable spray: charges stored in native item_instance charges slot 1.
-- Slot 0 stays unlimited for client item-use/refill availability when empty.
INSERT INTO item_template (entry,class,subclass,name,displayid,Quality,BuyCount,stackable,AllowableClass,AllowableRace,description,Material,ScriptName,spellid_1,spelltrigger_1,spellcharges_1,spellcharges_2) SELECT 902585,0,0,'Fungicide spray',displayid,1,1,1,-1,-1,'Ten charges. Use empty spray with Fungicide in bags to refill.',Material,'item_warscape_fungicide_spray',900780,0,0,10 FROM item_template WHERE entry=2459;
