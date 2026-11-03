# HUD rescue diagnosis, 27 October 2026

The supplied in-game capture is the evidence for the defects. Offline asset
comparisons and Lua checks below are not in-game visual acceptance.

## Findings before implementation

- The old texture is `Interface\MainMenuBar\UI-MainMenuBar-EndCap-Human`.
  Its 128 x 128 canvas contains an upright silhouette at rows 42 through 127.
  Blizzard's own `MainMenuBar.xml` instead uses
  `UI-MainMenuBar-EndCap-Dwarf`. That 128 x 128 asset contains the requested
  forward beak, folded wing, curled tail and projecting claw at rows 52 through
  127. The Human variant cannot acquire the requested shape through sizing.
- The old 256 x 256 cap retained its transparent upper canvas, but its 24-unit
  overlap placed only the far edge of the wrong creature over a button.
- `Minimap` was resized from 140 to 210, while `MinimapBackdrop`,
  `MinimapBorder`, the compass, north label and stock header kept their XML
  dimensions and offsets. The border therefore described a smaller, displaced
  circle. The native renderer uses the actual minimap rectangle; it does not
  impose a hardcoded 140-pixel render size.
- The backing stretched a Skills panel footer into a complete nine-slice bar.
  Its existing horizontal footer ornaments became doubled strips, while the
  unchanged minimap header produced a separate floating rectangle.
- `Interface\Icons\Achievement_Level_10` really contains a belt. Its semantics
  were misidentified in the earlier report. The 34 x 34 image also filled only
  half of its 68 x 68 menu button.
- The old fixed 1,434-unit assembly could occupy most of a wide screen at 100%.
  A saved scale below 100% then reduced the incorrectly fixed-size map border
  further. Saved scales must be preserved; default layout size must be defined
  independently from that user preference.

## Correction structure

Use the Dwarf end cap with its alpha bounds cropped by UV coordinates. Set its
display height from the crop's aspect ratio, never from a second arbitrary
dimension. Preserve an unmodified source BLP and reproducible color grading.
Place the claw over the first/last placeholder slot.

Use one backing behind both groups and the map, made from the blank metal
section of Blizzard's Dwarf action-bar atlas. Repeat uniformly scaled texture
sections and crop the final section; do not stretch ornaments or put independent
end borders at the map joins.

Make the map and cropped native circular border concentric. Remove the stock
header and its unused collapse control. Position the north/compass and native
zoom/tracking/world-map controls relative to that same circle. Preserve their
scripts and native minimap rendering.

Keep the existing user scaling logic on the HUD root. A child assembly fits
52% of the viewport width at default user scale; its geometry scales uniformly
with resolution or UI scale changes. The saved 50–150% multiplier then scales
that complete assembly independently of the Skills panel.

## Skills icon search following the OSRS reference

The user subsequently clarified that the icon must represent graphs or data,
using the coloured OSRS bar chart as the target. Books and a skills checklist
do not meet that visual direction. At the comparison stage, icon selection was
held pending the user's decision.

The archive listfiles provide 6,308 distinct `Interface\Icons` BLP paths,
recorded in `WarscapeHUDIconCatalog.tsv`. All 6,308 were decoded successfully
and inspected on eight indexed visual sheets. Enlarged follow-up sheets checked
engineering displays, crystals, punch cards and other possible data symbols.
No literal multicoloured bar-chart icon was found in that visual review.

The strongest proposed match is
`Interface\Icons\INV_Misc_EngGizmos_20.blp`, from `locale-enUS.MPQ`:
a yellow graph-like trace above a multicoloured display. The alternative
`Interface\Icons\INV_Misc_PunchCards_Prismatic.blp` represents encoded data
with a multicoloured punched card. Both are original 64 x 64 Blizzard assets.
`images/WarscapeHUDGraphIconCandidates.png` compares them with the OSRS reference
at the existing 68 x 68 button design size and enlarged below. The comparison
uses a 4-pixel source-edge crop and a 56 x 56 icon interior for both candidates.

The user subsequently selected the multicoloured data card. The HUD now uses
`Interface\Icons\INV_Misc_PunchCards_Prismatic` with that crop and the same
icon-to-button proportions. This supersedes the proposed engineering display.

## Implemented correction

The Dwarf cap is displayed at its exact visible-source aspect ratio (160 x 95).
Source-alpha measurements put the opaque front-claw tip at x=101 in rows
112-127. The layout anchors that point one quarter of a menu slot over the
outer button. Anchoring the beak instead leaves the claw outside the slot.

The map, 152-unit circular border and backdrop are concentric. Border UVs
`(92,29)-(244,181)` isolate the native atlas circle centred at `(168,105)`.
The compass retains its 365/140 size ratio because wowdecomp's native
`CSimpleTexture::SetRotation` expands the texture coordinates. Native zoom
spacing is preserved as a chord on a shared radius outside the map housing.

The native blank rail repeats with a uniform source-to-display ratio and its
final section is clipped, avoiding distorted artwork and centre joins. The
assembly fits 52% of viewport width before applying saved user scale. No Skills
panel code, server, database, executable or map data is changed.

`images/WarscapeHUDGryphonEvidence.png` shows original and graded source artwork.
`images/WarscapeHUDLayoutProof.png` renders the actual Lua geometry offline,
with an empty map viewport. These are asset/layout evidence only. The user's
in-game visual acceptance remains pending after deployment.
