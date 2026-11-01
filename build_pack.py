#!/usr/bin/env python3
"""Build Axoria resourcepack with vanilla fallbacks for CustomModelData."""
import hashlib
import json
from pathlib import Path
import zipfile
import struct
import zlib
from io import BytesIO
from collections import deque
from PIL import Image

items = [
    ("clock", "zeitstab", 1001),
    ("iron_pickaxe", "gluecks_spitzhacke", 1002),
    ("shears", "gaertnerschere", 1003),
    ("blaze_rod", "flammenstab", 1004),
    ("fishing_rod", "enterhaken", 1005),
    ("feather", "phoenix_feder", 1006),
    ("spyglass", "monster_lupe", 1007),
    ("stick", "blitzstab", 1008),
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
# The approved cyan/black scythe art is stored losslessly in this
# repository as base64, keeping the source PNG available to the builder.
# In-game the silhouette has strictly 0/255 alpha (no semi-transparent
# item pixels), and the exterior remains transparent.
import base64
def create_eissense_png():
    raw = base64.b64decode(Path("eissense.png.b64").read_text().strip())
    image = Image.open(BytesIO(raw)).convert("RGBA")
    if image.size != (32, 32):
        raise ValueError("Eissense texture must be exactly 32x32")
    alphas = {a for *_, a in image.getdata()}
    if not alphas.issubset({0, 255}):
        raise ValueError("Eissense must have full pixels with binary alpha")
    return raw

files["assets/axoria/textures/item/eissense.png"] = create_eissense_png()
files["assets/axoria/models/item/eissense.json"] = json.dumps({
    "parent": "minecraft:item/generated",
    "textures": {"layer0": "axoria:item/eissense"}
}, separators=(",", ":")).encode()

# Explicit vanilla fallbacks avoid missing-model squares on modern Minecraft
# when clock or lightning_rod is not a normal standalone model asset.
for plain, texture in (("clock", "clock_00"),):
    files["assets/axoria/models/item/vanilla_" + plain + ".json"] = json.dumps({
        "parent": "minecraft:item/generated",
        "textures": {"layer0": "minecraft:item/" + texture}
    }, separators=(",", ":")).encode()

for base, custom, value in items:
    # When no pack is active, the client always uses Minecraft's native item model.
    # When Axoria is active, only the numeric CustomModelData selects the custom model.
    vanilla = ("axoria:item/vanilla_clock" if base == "clock" else "minecraft:item/" + base)
    model = {
        "model": {
            "type": "minecraft:range_dispatch",
            "property": "minecraft:custom_model_data",
            "index": 0,
            "fallback": {"type": "minecraft:model", "model": vanilla},
            "entries": [
                {"threshold": value, "model": {"type": "minecraft:model", "model": "axoria:item/" + custom}},
                {"threshold": value + 0.5, "model": {"type": "minecraft:model", "model": vanilla}}
            ]
        }
    }
    files["assets/minecraft/items/" + base + ".json"] = json.dumps(model, separators=(",", ":")).encode()
def repair_enclosed_holes(png_bytes):
    """Fill only enclosed transparent gaps; preserve the exterior silhouette."""
    image = Image.open(BytesIO(png_bytes)).convert("RGBA")
    w, h = image.size
    px = image.load()
    exterior = set()
    queue = deque()
    for x in range(w):
        if px[x, 0][3] == 0: queue.append((x, 0))
        if px[x, h-1][3] == 0: queue.append((x, h-1))
    for y in range(h):
        if px[0, y][3] == 0: queue.append((0, y))
        if px[w-1, y][3] == 0: queue.append((w-1, y))
    while queue:
        x, y = queue.popleft()
        if (x, y) in exterior or px[x, y][3] != 0: continue
        exterior.add((x, y))
        for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in exterior:
                if px[nx, ny][3] == 0: queue.append((nx, ny))
    holes = [(x,y) for y in range(h) for x in range(w)
             if px[x,y][3] == 0 and (x,y) not in exterior]
    for x, y in holes:
        neighbors = [px[nx,ny] for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1))
                     if 0 <= nx < w and 0 <= ny < h and px[nx,ny][3] > 0]
        if neighbors:
            r = sum(c[0] for c in neighbors)//len(neighbors)
            g = sum(c[1] for c in neighbors)//len(neighbors)
            b = sum(c[2] for c in neighbors)//len(neighbors)
            px[x,y] = (r,g,b,255)
    # Source art uses partially transparent colored pixels that appear as
    # faint gaps in-game. Make every non-background pixel fully opaque.
    semitransparent = 0
    for y in range(h):
        for x in range(w):
            r,g,b,a = px[x,y]
            if 0 < a < 255:
                px[x,y] = (r,g,b,255)
                semitransparent += 1
    if not holes and not semitransparent: return png_bytes
    if semitransparent:
        print("Made", semitransparent, "partially transparent pixels opaque")
    result = BytesIO()
    image.save(result, "PNG", optimize=True)
    print("Filled", len(holes), "enclosed transparent pixels")
    return result.getvalue()

# Repair accidental fully enclosed holes in all item texture PNGs.
for path, data in list(files.items()):
    if path.startswith("assets/axoria/textures/item/") and path.endswith(".png"):
        try:
            files[path] = repair_enclosed_holes(data)
        except Exception as exc:
            raise RuntimeError("Invalid item PNG texture: " + path) from exc

with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as result_zip:
    for path, content in files.items():
        result_zip.writestr(path, content)
sha = hashlib.sha1(out.read_bytes()).hexdigest()
Path("pack-info.properties").write_text(
    "url=https://github.com/GxdionSenpai/Axoria-Resourcepack/releases/download/latest/axoria-resourcepack.zip\n"
    + "sha1=" + sha + "\n"
)
print("Published SHA-1:", sha)
