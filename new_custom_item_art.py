"""Premium 64x64 individual Axoria in-game item textures from the curated atlas."""
import base64
import json
from io import BytesIO
from pathlib import Path
from PIL import Image

NAMES=["trichterherz","schmiedekern","haendlervertrag","titanfaust","abyss_dreizack","raketenwerfer","krabbenschere","dimensionsklinge","sternenbogen","gravitationsbrecher"]
# Schmiedekern must never inherit a placeable furnace block model.
BASE=["heart_of_the_sea","magma_cream","paper","netherite_hoe","trident","crossbow","shears","netherite_sword","bow","mace"]

def render_items(files):
    atlas_data=base64.b64decode(Path("premium_item_atlas.png.b64").read_text(encoding="ascii").strip(),validate=True)
    atlas=Image.open(BytesIO(atlas_data)).convert("RGBA")
    if atlas.size!=(64,640):
        raise ValueError("Custom item atlas must be 64x640 (ten 64x64 sprites)")
    for index,name in enumerate(NAMES):
        sprite=atlas.crop((0,index*64,64,(index+1)*64))
        alpha={pixel[3] for pixel in sprite.getdata()}
        if alpha!={0,255}:
            raise ValueError(name+" must have opaque pixels and a transparent exterior, no half alpha")
        output=BytesIO()
        sprite.save(output,format="PNG",optimize=True)
        files["assets/axoria/textures/item/"+name+".png"]=output.getvalue()
        files["assets/axoria/models/item/"+name+".json"]=json.dumps({
            "parent":"minecraft:item/generated",
            "textures":{"layer0":"axoria:item/"+name}
        },separators=(",",":")).encode()
