# Stage 2A reference skin

These twelve textures were prepared **locally on Windows** from the approved
reference supplied by the user on 26 October 2026. No image-generation service
was used. `tools/build_skin.py` records the crops, silhouette mattes and interior
replacement operations against the full-resolution 1312 × 1199 reference.

- `Dragon`, `Foot`, `Side` and the three rail textures make the outer frame.
- `Stone` is fully opaque and contains no UI text.
- `Cell` and `Total` have blank interiors and are rendered as nine-slice frames.
- `Icon` is a transparent-centered socket surrounding each native WoW icon.
- `Track` is an empty XP track; a real StatusBar draws progress above it.
- `Close` is artwork for a real close button.

All files are uncompressed 32-bit TGA with power-of-two dimensions at or below
1024. WoW 3.3.5a loads these directly. The .tga extension is intentionally omitted
in Lua texture paths. Do not convert them to JPEG or discard alpha on ornaments.

The original generated skill illustrations, text, fake XP values, tab strip,
Slayer cell, tooltip and background scene are not part of the runtime skin.
The right ornaments mirror their left counterparts for a matched pair.

The standalone preview tool executes the actual Lua layout in a widget harness
with sample data and reads native textures/fonts from the local client. It is
a layout preview, not an in-game verification. Its output belongs under `build/`.
