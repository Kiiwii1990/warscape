# Crawling Hand source assets

Supplied by the user on 8 November 2026 from a friend, from Downloads/CrawlingHand. These three source asset files are copied byte-for-byte, not converted or re-exported. Creator tooling/source project was not supplied. GhoulSkinWhite.blp is the texture referenced by the model, with its original filename preserved.

manifest.json records exact SHA256 hashes, destination paths and collision-checked custom IDs. M2 is MD20/version264, has one SKIN view, an explicit BLP2 texture and embedded animation sequences. Idle/death/walk/run/attack entries exist; audible sounds, visual quality, grounding, scale and animation playback require manual client acceptance.

Model4000/display40000 copy native Ghoul model45/display137 metadata into NEW rows. Model path, bounds, collision dimensions and display scale/texture fields are set explicitly. Original metadata rows remain unchanged. Ghoul sound set45 is a stand-in, not OSRS audio. Baseline scale1 and level12 scale1.35 are provisional visual choices.

Prepare using contrib/warscape/enemies/custom_creatures.py; never overwrite native asset paths or install these files loose over the client. The prepared patch merges existing payloads and adds the model, skin, texture, custom creature DBC rows and new collectible Item.dbc rows.
