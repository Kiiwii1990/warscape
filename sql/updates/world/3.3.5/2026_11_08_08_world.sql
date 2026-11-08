-- Facemask: new head-slot equipment. Existing Smoke Devil stats/loot/AI rows unchanged.
INSERT INTO item_template (entry,class,subclass,name,displayid,Quality,BuyCount,stackable,AllowableClass,AllowableRace,InventoryType,description,Material) SELECT 902587,4,1,'Facemask',displayid,1,1,1,-1,-1,1,'Wear on your head to fight Smoke Devils.',Material FROM item_template WHERE entry=10504;
