"""Check the centered Warscape forge boundary against its 3.3.5a DBC model."""
import math
import struct
from pathlib import Path

DBC = Path(r"C:\WoWDev\TrinityServer\dbc\GameObjectDisplayInfo.dbc")
ROOT = Path(__file__).resolve().parents[3]
SERVER_GO = ROOT / "src/server/game/Entities/GameObject/GameObject.cpp"
SERVER_PLAYER = ROOT / "src/server/game/Entities/Player/Player.cpp"
SERVER_FOCUS = ROOT / "src/server/game/Grids/Notifiers/GridNotifiers.h"
SERVER_CONFIG = ROOT / "src/server/game/Entities/Unit/WarscapeSmelting.h"
CLIENT_GO = Path(r"C:\WoWDev\wowdecomp\WoW\Source\Object\ObjectClient\GameObject_C.cpp")
DISPLAY_ID = 305
TEMPLATE_SCALE = 1.08
INTERACTION_RADIUS = 4.0

raw = DBC.read_bytes()
magic, records, fields, record_size, _ = struct.unpack_from("<4s4I", raw)
assert magic == b"WDBC" and fields == 19 and record_size == 76
display = None
for i in range(records):
    offset = 20 + i * record_size
    row = struct.unpack_from("<19I", raw, offset)
    if row[0] == DISPLAY_ID:
        display = struct.unpack_from("<6f", raw, offset + 12 * 4)
        break
assert display is not None
mins, maxs = display[:3], display[3:]
assert mins == (-2.67602801322937, -1.6841169595718384, 0.0)
assert maxs == (2.162074089050293, 5.829826831817627, 6.0071330070495605)
center = ((mins[0] + maxs[0]) * 0.5 * TEMPLATE_SCALE,
          (mins[1] + maxs[1]) * 0.5 * TEMPLATE_SCALE,
          0.0)
assert abs(center[0] - -0.2775344) < 1e-5
assert abs(center[1] - 2.238683) < 1e-5

server_go = SERVER_GO.read_text()
server_player = SERVER_PLAYER.read_text()
server_focus = SERVER_FOCUS.read_text()
client_go = CLIENT_GO.read_text()
server_config = SERVER_CONFIG.read_text()
assert "radius = std::min(radius, Warscape::DefaultFurnaceInteractionDistance)" in server_go
assert "DefaultFurnaceInteractionDistance = 4.0f" in server_config
assert "forge->IsAtInteractDistance(*this, Warscape::DefaultFurnaceInteractionDistance)" in server_player
assert "float const dist = go->GetGOInfo()->spellFocus.dist;" in server_focus
assert "(displayInfo->GeoBoxMin.X + displayInfo->GeoBoxMax.X) * 0.5f * scale" in server_go
assert "(displayInfo->GeoBoxMin.Y + displayInfo->GeoBoxMax.Y) * 0.5f * scale" in server_go
assert "GetWorldRotation()" in server_go
assert "if (isWarscapeForge && range > 4.0f)" in client_go
assert "(displayInfo->m_geoBoxMin[0] + displayInfo->m_geoBoxMax[0]) * 0.5f * scale" in client_go
assert "(displayInfo->m_geoBoxMin[1] + displayInfo->m_geoBoxMax[1]) * 0.5f * scale" in client_go
assert "C3Vector local = player->GetPosition() * inverse" in client_go
assert "delta.SquaredMag() <= range * range" in client_go

def rotate(point, yaw):
    x, y, z = point
    return (x * math.cos(yaw) - y * math.sin(yaw),
            x * math.sin(yaw) + y * math.cos(yaw), z)

def within(local_point):
    return sum((a - b) ** 2 for a, b in zip(local_point, center)) <= INTERACTION_RADIUS ** 2

def check_inside(name, point):
    assert within(point), f"{name} should be within the forge boundary: {point}"

def check_outside(name, point):
    assert not within(point), f"{name} should be outside the forge boundary: {point}"

points = {
    "firebox side": (0.0, 0.0, 0.0),
    "bellows side": (0.0, 5.5, 0.0),
    "between furnace sections": (0.0, center[1], 0.0),
    "front approach": (center[0], center[1] - 3.8, 0.0),
    "rear approach": (center[0], center[1] + 3.8, 0.0),
    "left side": (center[0] - 3.8, center[1], 0.0),
    "right side": (center[0] + 3.8, center[1], 0.0),
    "just inside boundary": (center[0] + INTERACTION_RADIUS - 0.01, center[1], 0.0),
    "just outside boundary": (center[0] + INTERACTION_RADIUS + 0.01, center[1], 0.0),
}
for yaw in (0.0, 0.73, math.pi / 2, math.pi, -1.1):
    for name, point in points.items():
        recovered_local = rotate(rotate(point, yaw), -yaw)
        if name == "just outside boundary":
            check_outside(name, recovered_local)
        else:
            check_inside(name, recovered_local)
    far = (center[0] + INTERACTION_RADIUS + 0.01, center[1], 0.0)
    check_outside("rotated just outside boundary", rotate(rotate(far, yaw), -yaw))

print(f"PASS: center={center}, radius={INTERACTION_RADIUS}; firebox, bellows, front/rear, sides, 5 rotations and exact boundary")
