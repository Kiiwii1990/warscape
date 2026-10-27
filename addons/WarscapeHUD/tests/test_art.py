"""Pin the requested Blizzard variant and verify lossless geometry/alpha crops."""
from io import BytesIO
from pathlib import Path
import struct
import hashlib
import json
import sys

from PIL import Image

ART = Path(__file__).resolve().parents[1] / "art"
source = (ART / "WarscapeGryphonOriginal.blp").read_bytes()
assert hashlib.sha256(source).hexdigest() == "3d5c6d5706d6bdba5b2ab6b879b50e9ed82475297d91fa73061eaa3f5a74dead", "must be the original Dwarf cap, not the Human variant"
assert source[:4] == b"BLP2"
assert tuple(source[8:12]) == (2, 8, 1, 1)  # DXT3, eight-bit alpha, mipmaps
width, height = struct.unpack_from("<II", source, 12)
offset, size = struct.unpack_from("<I", source, 20)[0], struct.unpack_from("<I", source, 84)[0]

pixel_format = struct.pack("<8I", 32, 4, int.from_bytes(b"DXT3", "little"), 0, 0, 0, 0, 0)
header = struct.pack("<7I", 124, 0x00081007, height, width, size, 0, 1)
header += struct.pack("<11I", *([0] * 11)) + pixel_format + struct.pack("<5I", 0x1000, 0, 0, 0, 0)
original = Image.open(BytesIO(b"DDS " + header + source[offset : offset + size])).convert("RGBA")
graded = Image.open(ART / "WarscapeGryphonWarscape.tga").convert("RGBA")
assert graded.size == original.size == (128, 128)
assert graded.getchannel("A").tobytes() == original.getchannel("A").tobytes()
assert graded.convert("RGB").tobytes() != original.convert("RGB").tobytes()
assert original.getchannel("A").getbbox() == (0, 52, 128, 128)
claw_alpha = original.getchannel("A").point(lambda value: 255 if value > 200 else 0)
assert claw_alpha.crop((64, 112, 128, 128)).getbbox()[2] + 64 == 101
sys.path.insert(0, str(ART.parent / "tools"))
from build_art import grade
# Pillow's DDS and BLP RGB565 decoders round a few color values differently;
# use the builder's BLP decoder for a byte-exact color reproduction check.
blp_original = Image.open(BytesIO(source)).convert("RGBA")
assert graded.tobytes() == grade(blp_original).tobytes()
rail_source = (ART / "WarscapeRailOriginal.blp").read_bytes()
assert hashlib.sha256(rail_source).hexdigest() == "e5b65d2252b35b50a75714e118130a672b9714becc8bf251777e18e0a826cb16"
rail_original = Image.open(BytesIO(rail_source)).convert("RGBA").crop((64, 85, 256, 128))
rail = Image.open(ART / "WarscapeRail.tga").convert("RGBA")
assert rail.size == (256, 64)
assert rail.crop((0, 0, 192, 43)).tobytes() == grade(rail_original).tobytes()
assert rail.getchannel("A").getbbox() == (0, 0, 192, 43), "power-of-two padding is never sampled"
manifest = json.loads((ART / "sources.json").read_text())
assert manifest[0]["asset"].endswith("UI-MainMenuBar-EndCap-Dwarf.blp")
print("PASS: pinned original Dwarf gryphon, unchanged source alpha/crop, reproducible palette and native rail region without resampling")
