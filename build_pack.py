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
    ("stone_axe", "holzfaelleraxt", 1011),
    ("chest", "backpack", 1012),
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

# Restore the special Holzfälleraxt as a pack-only texture; players without
# the pack get the ordinary stone axe via vanilla's default item model.
# Preserve any existing source-pack timber artwork rather than overwriting it.
timber_texture = "assets/axoria/textures/item/holzfaelleraxt.png"
timber_model = "assets/axoria/models/item/holzfaelleraxt.json"
if timber_texture not in files:
    from PIL import ImageDraw
    canvas = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    # Original-style wooden handle with an iron axe head. Every actual sprite
    # pixel is fully opaque, leaving only the empty background transparent.
    d.line([(7, 29), (11, 24), (15, 19), (19, 14), (23, 9)], fill="#181c29", width=6)
    d.line([(7, 29), (11, 24), (15, 19), (19, 14), (23, 9)], fill="#81522e", width=4)
    d.line([(7, 28), (12, 23), (16, 18), (20, 13)], fill="#bf8242", width=1)
    d.polygon([(14, 12), (19, 5), (24, 3), (28, 4), (31, 8), (27, 14),
               (22, 19), (17, 18)], fill="#1c2533")
    d.polygon([(17, 12), (21, 6), (25, 5), (29, 7), (27, 12),
               (22, 17), (18, 16)], fill="#607789")
    d.polygon([(19, 10), (23, 6), (28, 7), (26, 11), (22, 15)],
              fill="#98b5c3")
    d.line([(23, 6), (28, 7), (26, 11)], fill="#e0eff3", width=1)
    d.polygon([(17, 14), (20, 11), (23, 14), (20, 17)], fill="#2d394b")
    output = BytesIO()
    canvas.save(output, format="PNG", optimize=True)
    files[timber_texture] = output.getvalue()
if timber_model not in files:
    files[timber_model] = json.dumps({
        "parent": "minecraft:item/handheld",
        "textures": {"layer0": "axoria:item/holzfaelleraxt"}
    }, separators=(",", ":")).encode()

# Backpack sprite: transparent exterior (alpha 0), solid pixels only (alpha 255).
# Semitransparent pixels are never allowed, avoiding visible halos in Minecraft.
backpack_png = base64.b64decode(Path("backpack.png.b64").read_text().strip())
backpack_image = Image.open(BytesIO(backpack_png)).convert("RGBA")
backpack_alpha = {a for *_, a in backpack_image.getdata()}
if backpack_image.size != (32, 32) or not backpack_alpha.issubset({0, 255}) or backpack_alpha != {0, 255}:
    raise ValueError("Backpack must be a 32x32 sprite with transparent background and opaque item pixels")
files["assets/axoria/textures/item/backpack.png"] = backpack_png
files["assets/axoria/models/item/backpack.json"] = json.dumps({
    "parent": "minecraft:item/generated",
    "textures": {"layer0": "axoria:item/backpack"}
}, separators=(",", ":")).encode()

files["assets/axoria/textures/item/eissense.png"] = create_eissense_png()
files["assets/axoria/models/item/eissense.json"] = json.dumps({
    "parent": "minecraft:item/generated",
    "textures": {"layer0": "axoria:item/eissense"}
}, separators=(",", ":")).encode()

# Three individually readable crate-key rarities. Every painted pixel is
# fully opaque (alpha 255); only the exterior silhouette is transparent.
# Never recolor or replace Minecraft's normal trial_key outside CustomModelData.
from PIL import ImageDraw
def create_axoria_key_png(tier):
    themes = {
        "normal": ("#192635", "#758da5", "#e4f5ff", "#31b9e3", "#215672"),
        "epic": ("#291737", "#8350b4", "#e8c3ff", "#d85fff", "#603482"),
        "legendary": ("#563013", "#edac35", "#fff3a2", "#ff4d57", "#a65a16")
    }
    outline, metal, shine, crystal, shadow = themes[tier]
    canvas=Image.new("RGBA",(32,32),(0,0,0,0))
    d=ImageDraw.Draw(canvas)
    # A stout pixel-art shaft with two key teeth, visible even at 16px.
    d.rectangle((13,16,20,28),fill=outline)
    d.rectangle((15,16,18,27),fill=metal)
    d.rectangle((16,18,16,25),fill=shine)
    d.rectangle((19,22,25,25),fill=outline)
    d.rectangle((19,23,23,24),fill=metal)
    d.rectangle((19,27,24,30),fill=outline)
    d.rectangle((19,28,22,29),fill=metal)
    # Outer jeweled key head with a solid, shaded center (no interior holes).
    d.polygon([(10,3),(22,3),(27,8),(27,15),(21,20),
               (11,20),(5,15),(5,9)],fill=outline)
    d.polygon([(11,5),(21,5),(25,9),(25,14),(20,18),
               (12,18),(7,14),(7,10)],fill=metal)
    d.polygon([(11,6),(21,6),(24,10),(22,15),(19,17),
               (12,17),(8,13),(8,10)],fill=shadow)
    d.polygon([(15,7),(19,7),(23,11),(20,15),(16,17),
               (11,13),(11,10)],fill=crystal)
    d.polygon([(15,8),(18,8),(20,10),(16,13),(13,11)],fill=shine)
    d.rectangle((12,7,13,8),fill=shine)
    if tier=="epic":
        # Purple arcane finials and a brighter magenta core.
        d.polygon([(5,10),(2,7),(3,14),(7,16)],fill=outline)
        d.polygon([(27,10),(30,7),(29,14),(25,16)],fill=outline)
        d.rectangle((15,12,19,14),fill="#faacff")
        d.rectangle((6,10,7,12),fill=crystal)
        d.rectangle((25,10,26,12),fill=crystal)
    elif tier=="legendary":
        # Gold crown, scarlet gem, flame-like gold fins.
        d.polygon([(9,5),(7,0),(12,3),(16,1),(20,3),(25,0),
                   (23,6)],fill=outline)
        d.polygon([(10,4),(9,2),(13,5),(16,3),(20,5),(23,2),
                   (22,5)],fill=shine)
        d.rectangle((15,9,19,12),fill="#ff183a")
        d.rectangle((16,9,17,10),fill="#fff3ac")
        d.rectangle((6,10,7,13),fill=shine)
        d.rectangle((24,10,25,13),fill=shine)
    else:
        # Inlaid steel bolts distinguish the common key at a glance.
        d.rectangle((9,11,10,12),fill=shine)
        d.rectangle((22,11,23,12),fill=shine)
    alphas={pixel[3] for pixel in canvas.getdata()}
    if not alphas.issubset({0,255}):
        raise ValueError("A crate key has partially transparent pixels")
    output=BytesIO()
    canvas.save(output,"PNG",optimize=True)
    return output.getvalue()

for rarity in ("normal","epic","legendary"):
    texture_name="axoria_key_"+rarity
    files["assets/axoria/textures/item/"+texture_name+".png"]=create_axoria_key_png(rarity)
    files["assets/axoria/models/item/"+texture_name+".json"]=json.dumps({
        "parent":"minecraft:item/generated",
        "textures":{"layer0":"axoria:item/"+texture_name}
    },separators=(",",":")).encode()

# These exact IDs match AxoriaCrates.keyTextureId(). Unmarked vanilla
# TRIAL_KEYs, and all players who decline the entire pack, stay vanilla.
trial_key_fallback={"type":"minecraft:model","model":"minecraft:item/trial_key"}
trial_key_entries=[]
for numeric,rarity in ((1013,"normal"),(1014,"epic"),(1015,"legendary")):
    trial_key_entries.extend([
        {"threshold":numeric,"model":{"type":"minecraft:model",
            "model":"axoria:item/axoria_key_"+rarity}},
        {"threshold":numeric+0.5,"model":trial_key_fallback}
    ])
files["assets/minecraft/items/trial_key.json"]=json.dumps({
    "model":{"type":"minecraft:range_dispatch",
             "property":"minecraft:custom_model_data",
             "index":0,
             "fallback":trial_key_fallback,
             "entries":trial_key_entries}
},separators=(",",":")).encode()

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
    vanilla_model = {"type": "minecraft:model", "model": vanilla}
    if base == "chest":
        # A chest is a special block-entity item, NOT an ordinary JSON item
        # model. Falling back to minecraft:model / minecraft:item/chest renders
        # normal chests as invisible/missing items when the pack is enabled.
        # Keep the vanilla normal/christmas chest rendering intact.
        def chest_model(texture):
            return {
                "type": "minecraft:special",
                "base": "minecraft:item/chest",
                "model": {"type": "minecraft:chest", "texture": "minecraft:" + texture}
            }
        vanilla_model = {
            "type": "minecraft:select",
            "property": "minecraft:local_time",
            "pattern": "MM-dd",
            "cases": [
                {"when": ["12-24", "12-25", "12-26"], "model": chest_model("christmas")}
            ],
            "fallback": chest_model("normal")
        }
    model = {
        "model": {
            "type": "minecraft:range_dispatch",
            "property": "minecraft:custom_model_data",
            "index": 0,
            "fallback": vanilla_model,
            "entries": [
                {"threshold": value, "model": {"type": "minecraft:model", "model": "axoria:item/" + custom}},
                {"threshold": value + 0.5, "model": vanilla_model}
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
