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
    """Detailed pixel-art scythe: dark outline, warm haft, shaded icy crescent."""
    from PIL import ImageDraw
    canvas = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    # Long dark wooden/iron haft, diagonal and outlined like other Axoria weapons.
    d.line([(6, 29), (12, 23), (18, 17), (23, 12)], fill="#241c29", width=6)
    d.line([(6, 29), (12, 23), (18, 17), (23, 12)], fill="#6f4729", width=4)
    d.line([(7, 28), (13, 22), (19, 16), (23, 12)], fill="#b58b49", width=1)
    # Iron bindings and handle cap.
    d.polygon([(4, 28), (7, 25), (10, 28), (7, 31)], fill="#1d2632")
    d.line([(10, 24), (13, 27)], fill="#d6b761", width=2)
    d.line([(16, 18), (19, 21)], fill="#c9ad5a", width=2)
    # Outer silhouette of a curved, hooked ice blade.
    d.polygon([(21, 15), (18, 12), (14, 9), (9, 6), (4, 5), (1, 7),
               (3, 3), (8, 1), (14, 2), (20, 5), (25, 9),
               (27, 13), (26, 17), (23, 18)], fill="#172333")
    d.polygon([(21, 13), (17, 10), (12, 7), (7, 5), (4, 5),
               (9, 3), (14, 4), (20, 7), (24, 10), (25, 14),
               (23, 16)], fill="#2c668b")
    d.polygon([(20, 11), (16, 8), (11, 5), (8, 4), (14, 4),
               (20, 7), (23, 10), (24, 13), (22, 14)], fill="#53b4ce")
    # Brighter beveled cutting edge and individually placed glints.
    d.line([(4, 4), (8, 2), (14, 3), (19, 6), (23, 10)], fill="#d6f9ff", width=1)
    d.line([(7, 5), (12, 6), (17, 9)], fill="#93e8f0", width=1)
    d.line([(23, 13), (21, 15), (20, 16)], fill="#142e47", width=2)
    # Dark metal socket binds blade to the haft.
    d.polygon([(21, 13), (24, 12), (27, 15), (24, 19), (20, 17)], fill="#202734")
    d.polygon([(22, 14), (24, 14), (25, 16), (23, 18), (21, 16)], fill="#b39a53")
    d.point([(24, 15), (22, 16)], fill="#ffe29a")
    # Keep the actual object entirely opaque, with a transparent outside.
    out = BytesIO()
    canvas.save(out, format="PNG", optimize=True)
    return out.getvalue()

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
