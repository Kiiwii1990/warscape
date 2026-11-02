"""Pin the requested Blizzard variant and verify lossless geometry/alpha crops."""
from io import BytesIO
from pathlib import Path
import struct
import hashlib
import json
import sys

from PIL import Image

ART = Path(__file__).resolve().parents[1] / "art"
panel_reference = Image.open(ART.parent.parent / "WarscapeSkills" / "art" / "Dragon.tga").convert("RGBA")
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
from build_art import grade, grade_gryphon, prepare_design5
# Pillow's DDS and BLP RGB565 decoders round a few color values differently;
# use the builder's BLP decoder for a byte-exact color reproduction check.
blp_original = Image.open(BytesIO(source)).convert("RGBA")
recolored = grade_gryphon(blp_original, panel_reference)
assert graded.tobytes() == recolored.tobytes()
assert graded.size == original.size == (128, 128)
assert graded.getchannel("A").tobytes() == original.getchannel("A").tobytes(), "recolour preserves the exact gryphon silhouette"
eye = graded.getpixel((108, 65))[:3]
panel_eye = panel_reference.getpixel((176, 63))[:3]
assert max(abs(eye[i] - panel_eye[i]) for i in range(3)) <= 20, "eye colour/intensity follows the actual panel eye sample"
design_source = Image.open(ART / "WarscapeGryphonDesign5Source.png").convert("RGBA")
design_texture = Image.open(ART / "WarscapeGryphonDesign5.tga").convert("RGBA")
assert design_source.size == (494, 299)
assert design_source.getchannel("A").getextrema() == (255, 255)
assert design_texture.size == (128, 128)
assert design_texture.getchannel("A").crop((0, 0, 128, 52)).getbbox() is None
assert design_texture.tobytes() == prepare_design5(design_source).tobytes(), "Design 5 texture is reproducible from its supplied source"
assert design_texture.getchannel("A").crop((0, 52, 128, 128)).getbbox() is not None
rail_source = (ART / "WarscapeRailOriginal.blp").read_bytes()
assert hashlib.sha256(rail_source).hexdigest() == "e5b65d2252b35b50a75714e118130a672b9714becc8bf251777e18e0a826cb16"
rail_original = Image.open(BytesIO(rail_source)).convert("RGBA").crop((64, 85, 256, 128))
rail = Image.open(ART / "WarscapeRail.tga").convert("RGBA")
rail_trim = Image.open(ART / "WarscapeRailTrim.tga").convert("RGBA")
assert rail.size == (256, 64)
assert rail.crop((0, 0, 192, 43)).tobytes() == grade(rail_original).tobytes()
assert rail.getchannel("A").getbbox() == (0, 0, 192, 43), "power-of-two padding is never sampled"
assert rail_trim.size == (256, 64)
assert rail_trim.crop((0, 0, 256, 5)).tobytes() == rail.crop((0, 0, 256, 5)).tobytes()
assert rail_trim.getchannel("A").getbbox() == (0, 0, 192, 5), "only the complete original bronze top bevel stays opaque"
manifest = json.loads((ART / "sources.json").read_text())
assert manifest[0]["asset"] == "WarscapeGryphonDesign5Source.png"
assert manifest[1]["asset"].endswith("UI-MainMenuBar-EndCap-Dwarf.blp")
assert manifest[3]["runtime"] == "WarscapeRailTrim.tga"
assert manifest[3]["operation"] == "Preserve original top five rail rows; clear brown center"
print("PASS: Design 5 and Dwarf textures, reproducible artwork, unscaled gold trim alpha and transparent rail fill")

# Preserve the approved design and UV geometry, retaining source detail rather
# than upscaling the old 128-pixel runtime. No change to the other runtime art.
hd_path=ART / 'WarscapeGryphonDesign5HD.tga'
hd=Image.open(hd_path).convert('RGBA')
assert hd.size==(512,512)
assert hd_path.read_bytes()[2]==2 and hd_path.read_bytes()[16:18]==bytes([32,8])
assert hd.getchannel('A').crop((0,0,512,208)).getbbox() is None
assert hd.tobytes()==prepare_design5(design_source,512).tobytes()
assert hd.getchannel('A').getextrema()==(0,255)
legacy_mask=design_texture.getchannel('A').crop((0,52,128,128))
new_mask=hd.getchannel('A').crop((0,208,512,512)).resize((128,76),Image.Resampling.LANCZOS)
different=sum((a>=128)!=(b>=128) for a,b in zip(legacy_mask.tobytes(),new_mask.tobytes()))
assert different/(128*76)<.015, 'High resolution preserves the same normalized silhouette'
assert manifest[-1]['runtime']==hd_path.name and manifest[-1]['source_size']==[494,299]
print('PASS: same-design 512x512 RGBA runtime, source reproducibility, transparent padding and matching silhouette')
