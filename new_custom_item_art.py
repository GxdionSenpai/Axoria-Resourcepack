"""Premium 64x64 individual Axoria in-game item textures from the curated atlas."""
import base64
import json
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw

NAMES=["trichterherz","schmiedekern","haendlervertrag","titanfaust","abyss_dreizack","raketenwerfer","krabbenschere","dimensionsklinge","sternenbogen","gravitationsbrecher"]
# Schmiedekern must never inherit a placeable furnace block model.
BASE=["heart_of_the_sea","magma_cream","paper","netherite_hoe","trident","carrot_on_a_stick","shears","netherite_sword","bow","mace"]

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


    # Distinct, much brighter charged Sternenbogen. The actual icon (not chat)
    # switches automatically to this special 64px texture at 5/5 hits.
    charged=atlas.crop((0,8*64,64,9*64))
    draw=ImageDraw.Draw(charged)
    # Pixel-hard 8-pointed gold star and four crystal sparks. No antialiasing.
    gold="#ffe66a";core="#fffbd2";purple="#ec7aff"
    draw.polygon([(53,3),(56,10),(63,12),(56,14),(53,21),(50,14),(43,12),(50,10)],fill=gold)
    draw.polygon([(53,7),(55,12),(53,17),(51,12)],fill=core)
    for x,y in ((10,7),(47,29),(21,50),(51,51)):
        draw.rectangle((x-1,y-1,x+1,y+1),fill=purple)
        draw.line([(x-3,y),(x+3,y)],fill=core,width=1)
        draw.line([(x,y-3),(x,y+3)],fill=core,width=1)
    charged_alpha={px[3] for px in charged.getdata()}
    if charged_alpha!={0,255}:
        raise ValueError("Charged Sternenbogen must have alpha 0/255 only")
    output=BytesIO()
    charged.save(output,format="PNG",optimize=True)
    files["assets/axoria/textures/item/sternenbogen_charged.png"]=output.getvalue()
    files["assets/axoria/models/item/sternenbogen_charged.json"]=json.dumps({
        "parent":"minecraft:item/generated",
        "textures":{"layer0":"axoria:item/sternenbogen_charged"}
    },separators=(",",":")).encode()
