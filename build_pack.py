#!/usr/bin/env python3
"""Build Axoria resourcepack with vanilla fallbacks for CustomModelData."""
import hashlib
import json
from pathlib import Path
import zipfile
import struct
import zlib

items = [
    ("clock", "zeitstab", 1001),
    ("iron_pickaxe", "gluecks_spitzhacke", 1002),
    ("shears", "gaertnerschere", 1003),
    ("blaze_rod", "flammenstab", 1004),
    ("fishing_rod", "enterhaken", 1005),
    ("feather", "phoenix_feder", 1006),
    ("spyglass", "monster_lupe", 1007),
    ("lightning_rod", "blitzstab", 1008),
    ("snowball", "frostkugel", 1009),
    ("diamond_hoe", "eissense", 1010),
]
source = Path("source-pack.zip")
if not source.is_file():
    raise SystemExit("Upload source-pack.zip first")
out = Path("axoria-resourcepack.zip")
with zipfile.ZipFile(source) as source_zip:
    assert source_zip.testzip() is None
    assert "pack.mcmeta" in source_zip.namelist()
    files = {name: source_zip.read(name) for name in source_zip.namelist() if not name.endswith("/")}
# Generate a 32x32 ice scythe texture with a continuous, opaque silhouette.
# Transparent pixels are only used outside the item (not as interior holes).
def create_eissense_png():
    w = h = 32
    pixels = [[(0, 0, 0, 0) for _ in range(w)] for _ in range(h)]
    def put(x, y, color):
        if 0 <= x < w and 0 <= y < h:
            pixels[y][x] = (*color, 255)
    dark = (21, 65, 111)
    steel = (77, 188, 226)
    glow = (174, 244, 255)
    # Diagonal reinforced handle, lower left toward top right.
    for t in range(5, 27):
        x, y = t, 31-t
        for dx in (-1, 0, 1):
            put(x+dx, y, dark if dx == -1 else (steel if dx == 0 else glow))
    # Curved blade swept leftward across the upper edge.
    for y in range(3, 17):
        tip = 4 + (y-3)//2
        edge = 22 - (y-3)//3
        for x in range(tip, edge+1):
            if y <= 5 or x >= tip + (y//5):
                put(x, y, dark if y >= 13 else (glow if y <= 6 or x < tip+2 else steel))
    # A deliberate continuous blade-to-handle connection.
    for y in range(11, 17):
        for x in range(17, 24):
            put(x, y, steel if x < 22 else dark)
    raw = b"".join(b"\\x00" + b"".join(bytes(pixel) for pixel in row) for row in pixels)
    def chunk(kind, payload):
        return struct.pack("!I", len(payload)) + kind + payload + struct.pack("!I", zlib.crc32(kind + payload) & 0xffffffff)
    return (b"\\x89PNG\\r\\n\\x1a\\n" + chunk(b"IHDR", struct.pack("!2I5B", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))

files["assets/axoria/textures/item/eissense.png"] = create_eissense_png()
files["assets/axoria/models/item/eissense.json"] = json.dumps({
    "parent": "minecraft:item/generated",
    "textures": {"layer0": "axoria:item/eissense"}
}, separators=(",", ":")).encode()

for base, custom, value in items:
    # When no pack is active, the client always uses Minecraft's native item model.
    # When Axoria is active, only the numeric CustomModelData selects the custom model.
    model = {
        "model": {
            "type": "minecraft:range_dispatch",
            "property": "minecraft:custom_model_data",
            "index": 0,
            "fallback": {"type": "minecraft:model", "model": "minecraft:item/" + base},
            "entries": [
                {"threshold": value, "model": {"type": "minecraft:model", "model": "axoria:item/" + custom}},
                {"threshold": value + 0.5, "model": {"type": "minecraft:model", "model": "minecraft:item/" + base}}
            ]
        }
    }
    files["assets/minecraft/items/" + base + ".json"] = json.dumps(model, separators=(",", ":")).encode()
with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as result_zip:
    for path, content in files.items():
        result_zip.writestr(path, content)
sha = hashlib.sha1(out.read_bytes()).hexdigest()
Path("pack-info.properties").write_text(
    "url=https://github.com/GxdionSenpai/Axoria-Resourcepack/releases/download/latest/axoria-resourcepack.zip\n"
    + "sha1=" + sha + "\n"
)
print("Published SHA-1:", sha)
