# OSRS Coin stacks — 7 November 2026

## Behaviour

Coins (item 902006) now stack to **2,147,483,647 per bag/bank slot**, matching
[OSRS Wiki Coins](https://oldschool.runescape.wiki/w/Coins). This is a finite
maximum, not unlimited storage. No platinum-token or currency-conversion system
is added. The native WoW gold/silver/copper wallet remains separate.

The existing Coins identity is retained. Migration
`2026_11_07_11_world.sql` changes only its stackable value from 200 to 2147483647;
it does not modify any character table, amounts, loot chances or item prices.
Previously separate stacks are preserved and can be merged through normal bag
operations. Ordinary item storage fills a stack to its cap and uses another slot
for excess; full bags retain the normal inventory-full behaviour.

Creature loot generation coalesces unconditional, non-quest, non-FFA Coins from
reference-expanded tables into a single pile where possible. Server loot and
group-roll quantities now use 32 bits, matching the existing loot packet and
inventory quantity fields. Native SQL loot row quantity limits remain unchanged.
Container loot keeps its existing generation behaviour. Other item stack limits,
loot ownership, quest/conditional drops and the 18-slot corpse limit are retained.
This improves existing reference-expanded coin drops; support for new enemy
source ranges above the native SQL row limit still needs catalogue work.

No addon or DBC patch is required: stack capacity is an item-template response.
Deployment increments the runtime ClientCacheVersion so the next client session
refreshes cached item data. Fully exit WoW before reconnecting.

## Verification and history

The original Goblin migration/specification is immutable. Its historical
verification expected Coins to stack to 200. The new specification explicitly
supersedes only that assertion, retaining every other Goblin assertion. `db.py
verify` accepts such a replacement only from a later applied migration with
matching migration and original-query hashes. Pending replacements do not relax
verification. Apply/recover always use the migration's original specification.

Automated checks cover the exact cap, preservation of non-Coin sentinel behaviour,
merging counts above 255, exact-cap and overflow boundaries, and conservation of
reference-expanded coin quantities. A RelWithDebInfo worldserver build is required.
Before/after database hashes cover all item instances, skill XP, character wallet
balances and progression, all non-stack item-template columns, and every other
item's stack limit. These checks do not establish stock-client visual acceptance.

## In-game acceptance

Use a test character with spare bag space, after fully restarting WoW:

1. Record Coins and the native wallet balance. Existing stacks must keep their
   exact amounts. Drag two old Coins stacks together: they should merge above 200.
2. For a deterministic test, `.additem 902006 250` grants 250 test Coins. Repeat:
   the same stack should grow by another 250 rather than splitting at 200. This
   deliberately creates currency; use a test character and account for it.
3. Kill and loot existing catalogue enemies that drop Coins. Confirm the corpse
   quantity is added exactly and that Bones/other drops remain normal. Multi-row
   Coins drops should appear as one pile, including quantities above 255.
4. Split off a small amount, merge it back, deposit/withdraw at a bank, and test a
   small player trade if another tester is available. Totals must remain exact.
5. Log out normally and back in. Confirm Coins persist, stack capacity remains
   above 200, and native wallet/skill XP are unchanged apart from deliberate play.
6. Check a normal non-Coin item still follows its existing stack limit.

The maximum is tested automatically; do not mint a maximum stack on a normal
character just to test it. Native wallet conversion, spending OSRS Coins at WoW
vendors, and a universal OSRS economy remain separate future work.

## Rollback

Prefer a forward fix. Never blindly lower the stack limit to 200 after larger
stacks exist: first stop writers, take verified backups, and review inventories,
banks, mail, auctions and guild-bank storage for Coins stacks above 200. A safe
reduction requires a separately reviewed redistribution plan that preserves every
coin and handles insufficient slots. No destructive rollback SQL is supplied.
Do not restore an old character backup over current progress. Preserve runtime
and configuration backups; keep the increased cache version when correcting item
metadata. Historical migrations and their ledger hashes must not be rewritten.


## Deployment record

Applied and verified on 7 November 2026. Fresh verified world backup:
`C:\WarscapeBackups\world_20261107T191646_567516Z_bf190701.sql`
(190 tables, three views; restore not exercised). Runtime executable, PDB and
configuration backup: `C:\WarscapeBackups\Coins-20261107-deploy`.
ClientCacheVersion is now 26092. No client files or character rows were modified.

Both RelWithDebInfo builds passed. The 96 catalogue Python tests, 15 database
safety tests and isolated Debug C++ assertions passed, as did all twelve current
enemy/currency migration contracts and preservation hashes. Authserver and
worldserver restarted successfully, with ports 3724/8085 listening and worldserver
reporting ready. No Coin-specific startup errors appeared. Existing unrelated
Mining/item/GameObject database warnings remain. Server-side LootItem/Roll
quantity widths changed; client object layouts and wire field widths did not.
Manual bag, bank, trade, loot-display and relog acceptance remains pending.
