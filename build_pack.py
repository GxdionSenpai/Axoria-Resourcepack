#!/usr/bin/env python3
"""Build Axoria resourcepack with vanilla fallbacks for CustomModelData."""
import hashlib
import json
from pathlib import Path
import zipfile

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
]
source = Path("source-pack.zip")
if not source.is_file():
    raise SystemExit("Upload source-pack.zip first")
out = Path("axoria-resourcepack.zip")
with zipfile.ZipFile(source) as source_zip:
    assert source_zip.testzip() is None
    assert "pack.mcmeta" in source_zip.namelist()
    files = {name: source_zip.read(name) for name in source_zip.namelist() if not name.endswith("/")}
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
    "url=https://github.com/GxdionSenpai/Axoria-Resourcepack/releases/download/latest/axoria-resourcepack.zip\\n"
    + "sha1=" + sha + "\\n"
)
print("Published SHA-1:", sha)
