"""Build eleven individually generated 128x128 Axoria Minecraft item sprites.

The source atlas is an ORIGINAL 128x1408 PNG committed to this repository.
Each 128x128 region is extracted losslessly; its transparent background uses
alpha 0 and the visible pixels alpha 255 (never half-transparent).
"""
import json
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw

NAMES=["trichterherz","schmiedekern","haendlervertrag","titanfaust",
       "abyss_dreizack","raketenwerfer","krabbenschere","dimensionsklinge",
       "sternenbogen","gravitationsbrecher"]
BASE=["heart_of_the_sea","magma_cream","paper","netherite_hoe","trident",
      "carrot_on_a_stick","shears","netherite_sword","bow","mace"]
ATLAS=Path("premium_generated_atlas/axoria128_item_art.png")
SIZE=128

def _png(image):
    if image.size!=(SIZE,SIZE):
        raise ValueError("Each Axoria texture must be exactly 128x128 pixels")
    pixels=image.getdata()
    alpha={p[3] for p in pixels}
    if alpha!={0,255}:
        raise ValueError("Item texture must have an entirely clear background and fully opaque pixels")
    buffer=BytesIO()
    image.save(buffer,format="PNG",optimize=True)
    return buffer.getvalue()

def _put(files,name,image):
    files["assets/axoria/textures/item/"+name+".png"]=_png(image)
    files["assets/axoria/models/item/"+name+".json"]=json.dumps({
        "parent":"minecraft:item/generated",
        "textures":{"layer0":"axoria:item/"+name}
    },separators=(",",":")).encode()

def render_items(files):
    if not ATLAS.is_file():
        raise FileNotFoundError("Missing original 128px Axoria art source: "+str(ATLAS))
    atlas=Image.open(ATLAS).convert("RGBA")
    if atlas.size!=(SIZE,SIZE*11):
        raise ValueError("The generated Axoria item atlas must be 128x1408 pixels")

    for index,name in enumerate(NAMES):
        texture=atlas.crop((0,index*SIZE,SIZE,(index+1)*SIZE))
        # The rocket art has its RED FIREWORK visible at the upper-left,
        # AWAY FROM the bottom-right holding grip, never pointed at the user.
        # The crab claw stays orange/red, the abyss trident is turquoise and
        # the forge core glows orange; deliberately NOT a uniform purple set.
        _put(files,name,texture)

    # Replace the actual Skyblock hotbar BOOK, CustomModelData 1016, too.
    # It shows a PINK AXOLOTL centered on an ornate blue/gold cover.
    book=atlas.crop((0,10*SIZE,SIZE,11*SIZE))
    _put(files,"skyblock_menu_book",book)

    # Five landed bow hits: charged item has a separate glowing icon, CMD 1111.
    charged=atlas.crop((0,8*SIZE,SIZE,9*SIZE))
    draw=ImageDraw.Draw(charged)
    draw.polygon([(106,4),(112,17),(126,23),(112,29),(106,43),
                  (100,29),(86,23),(100,17)],fill="#ffe76c")
    draw.polygon([(106,13),(110,23),(106,34),(102,23)],fill="#fffce3")
    for x,y in ((15,17),(95,59),(38,104),(105,102)):
        draw.rectangle((x-2,y-2,x+2,y+2),fill="#f6a5ff")
        draw.line(((x-6,y),(x+6,y)),fill="#fff4c7",width=2)
        draw.line(((x,y-6),(x,y+6)),fill="#fff4c7",width=2)
    _put(files,"sternenbogen_charged",charged)
