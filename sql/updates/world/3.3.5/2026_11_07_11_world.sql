-- OSRS Coin stack capacity; preserve item identity and every existing character amount.
UPDATE item_template SET stackable=2147483647 WHERE entry=902006 AND name='Coins' AND stackable=200;
