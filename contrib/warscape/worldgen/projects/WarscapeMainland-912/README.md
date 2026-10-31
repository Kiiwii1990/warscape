# Warscape Mainland (map 912)

A blank editing template for **Noggit 3.3580 / WoW 3.3.5a**. The map has
exactly **25 ADTs**, covering **X=30-34, Y=30-34** inclusive. Click **(32,32)**
in the map preview to enter the centre tile.

All terrain is flat at **height 30**, painted with the native
`Tileset\Elwynn\ElwynnGrassBase.blp` texture. Randomised ground detail was
explicitly disabled (`ground_detail.flat: true`). There are no placed objects,
buildings, scenery, water or NPC setup.

## Open the project

1. Check out the Warscape development branch `feature/osrs-monster-stats` from
   `https://github.com/Kiiwii1990/warscape` and pull the latest changes. Save any
   work in another Noggit project before switching projects.
2. In **Noggit 3.3580 -> Settings**, set **Game Path** to your own installed
   Warscape WoW 3.3.5a game directory: the directory containing `Data` and the
   client executable. The primary local setup is:
   ```text
   C:\WoWDev\wowdecomp\bin\Win
   ```
   The client and its standard archives must already be installed separately.
3. Set **Project Path** to this checkout's **NoggitProject** directory. For a
   checkout at `C:\WoWDev\TrinityCore`, the exact path is:
   ```text
   C:\WoWDev\TrinityCore\contrib\warscape\worldgen\projects\WarscapeMainland-912\NoggitProject
   ```
   If your checkout is elsewhere, replace the checkout prefix. Select the
   `NoggitProject` folder itself, not its parent or its `World` subfolder.
4. Save settings, restart Noggit, select **Warscape Mainland (912)**, and click
   the preview square **(32,32)**. All 25 tiles already exist; do not create
   additional tiles to open the project.
5. Save map edits into this checkout's project directory. Local placement UID
   storage starts at `uid.ini` -> `912=0`; no MySQL UID connection is required.

The earlier standalone project at
`C:\WoWDev\Worldgen\WarscapeMainland-912\NoggitProject` remains separate.
Saving there does not update this Git copy. Use the Project Path above when
editing files that will be shared through this repository. Coordinate tile
ownership with other editors; ADT/WDT/DBC binaries require deliberate conflict
resolution, and placed objects must retain unique placement IDs.

## Included project data

- `NoggitProject/World/Maps/WarscapeMainland/`: 25 `.adt` files and one matching
  `WarscapeMainland.wdt`.
- `NoggitProject/DBFilesClient/Map.dbc`: the complete editor Map table with map
  912 named Warscape Mainland, preserving every existing row from its source.
- `NoggitProject/uid.ini`: initial map-local placement UID state.
- `validation.json`: validation results and SHA-256 hashes of all 28 data files.

The other standard DBCs and the native grass texture are loaded from the Game
Path archives. `Map.dbc` is the only project DBC override needed by this blank
map. Existing map registrations in that table do not include their terrain in
this package; edit Warscape Mainland here.

## Validation and deployment status

On 31 October 2026, all 6,400 MCNKs and 928,000 stored terrain samples were
validated at exactly height 30. The WDT references exactly the supplied 25
ADTs. All 40 shared tile borders (5,160 edge samples) match in height and
normal; native XY header float rounding is below 0.0001 world units. The
installed Windows TrinityCore map extractor independently read all 25 tiles,
with no liquids or terrain holes. The Git data files were checked byte for
byte against that validated snapshot.

Noggit appearance and in-game play have not been manually tested. This package
has not been deployed. It includes no game client, MPQ archives, credentials,
server executables, extracted server maps, collision or navigation output.
No database migration is required for editor use. Do not replace live DBCs
with this editor snapshot; any future deployment must freshly merge the
current map registrations and use the normal deployment workflow.
