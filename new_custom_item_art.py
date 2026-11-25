"""Build eleven individually generated 128x128 Axoria Minecraft item sprites.

The source atlas is an ORIGINAL 128x1408 PNG committed to this repository.
Each 128x128 region is extracted losslessly; its transparent background uses
alpha 0 and the visible pixels alpha 255 (never half-transparent).
"""
import json
import base64
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

def trichterherz_sprite():
    # Original vanilla hopper item silhouette (Minecraft 1.21.4).
    raw=base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAABAAAAAQBAMAAADt3eJSAAAAGFBMVEUAAABiYWJSVVJKTEpBREE+Pj44ODgwMDAGhTNBAAAAAXRSTlMAQObYZgAAAFxJREFUeNpjwAaMgYABCILTgMCEgYFVLb28vCypgIE1SL283Ek1gIEh1FFQUKWUgYGB1TQ0NKQArFrJxJ0BBIIEhSEMVkHlAghDUQTCYAg0Z4CAIHcGCGAtQLYaAO5rD2YxW90wAAAAAElFTkSuQmCC")
    base=Image.open(BytesIO(raw)).convert("RGBA")
    palette=((65,16,49),(115,26,77),(181,46,116),(236,91,165),(255,166,215))
    colors=[]
    for r,g,b,a in base.getdata():
        if not a:
            colors.append((0,0,0,0));continue
        v=max(0,min(4,((r+g+b)/3-42)/60*4))
        i=min(3,int(v));t=v-i
        colors.append(tuple(round(palette[i][k]*(1-t)+palette[i+1][k]*t) for k in range(3))+(255,))
    base.putdata(colors)
    # Leave room for three axolotl gills on each side, without stretching
    # the original hopper. Work on a crisp 32-pixel grid.
    im=Image.new("RGBA",(32,32),(0,0,0,0))
    d=ImageDraw.Draw(im)
    for side in (-1,1):
        for y,dy in ((9,-4),(13,-1),(17,2)):
            x=7 if side==-1 else 24
            tip=x+side*5
            d.line((x,y,tip,y+dy),fill=(83,19,58,255),width=3)
            d.line((x,y,tip,y+dy),fill=(243,88,157,255),width=1)
            d.point((tip,y+dy-1),fill=(255,171,209,255))
    im.alpha_composite(base.resize((24,24),Image.Resampling.NEAREST),(4,4))
    d=ImageDraw.Draw(im)
    # Centered pixel heart on the front of the hopper.
    heart=[".##.##.","#######","#######",".#####.","..###..","...#..."]
    for yy,row in enumerate(heart):
        for xx,c in enumerate(row):
            if c=="#":
                d.point((12+xx,12+yy),fill=(255,211,235,255) if yy==0 else (255,54,128,255))
    d.point((13,13),fill=(255,245,249,255))
    return im.resize((128,128),Image.Resampling.NEAREST)

def dimensionsklinge_sprite():
    # Original Minecraft 1.21.4 netherite sword item PNG.
    raw=base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAABAAAAAQBAMAAADt3eJSAAAAKlBMVEUAAACGe4ZwZ3BdVl1zRUNRRE5PPD5gNDI7OTtKKUAyJycvISIjEBIWCBTo6UOrAAAAAXRSTlMAQObYZgAAAFVJREFUeNpjgADOmVDGRBmogBCUMTHwAERAVQciMDkYJDCTgTMqB8ydMHXZAbACzawciEqlZQegSmMgNHdNFkRky4Eza0D0zB4GhjMgxiyoSoY7UAYAZfEWu0XQZ4wAAAAASUVORK5CYII=")
    base=Image.open(BytesIO(raw)).convert("RGBA")
    palette=((17,10,33),(42,24,76),(79,40,145),(147,80,221),(221,168,255))
    pixels=[]
    for r,g,b,a in base.getdata():
        if not a:
            pixels.append((0,0,0,0));continue
        v=max(0,min(4,((r+g+b)/3-15)/122*4))
        i=min(3,int(v));t=v-i
        pixels.append(tuple(round(palette[i][k]*(1-t)+palette[i+1][k]*t) for k in range(3))+(255,))
    base.putdata(pixels)
    im=base.resize((32,32),Image.Resampling.NEAREST)
    original=im.copy()
    draw=ImageDraw.Draw(im)
    # A narrow cyan dimensional fissure inside the blade, retaining the
    # vanilla blade edges. A broken diagonal gives a portal-energy effect.
    for y in range(5,18):
        xs=[x for x in range(12,31) if original.getpixel((x,y))[3]==255]
        if len(xs)>=4 and y not in (9,13):
            x=xs[len(xs)//2]
            draw.point((x,y),fill=(112,220,255,255))
            if y%3==0 and original.getpixel((x-1,y))[3]:
                draw.point((x-1,y),fill=(204,166,255,255))
    # Small angular portal crystal set into the blade/guard transition.
    y=20
    xs=[x for x in range(32) if original.getpixel((x,y))[3]==255]
    if xs:
        x=xs[len(xs)//2]
        draw.polygon([(x,y-5),(x+4,y-1),(x+3,y+3),(x,y+5),
                      (x-4,y+1),(x-3,y-3)],fill=(25,12,52,255))
        draw.polygon([(x,y-4),(x+3,y),(x,y+4),(x-3,y)],
                     fill=(124,48,199,255))
        draw.polygon([(x,y-3),(x+2,y),(x,y+2),(x-1,y)],
                     fill=(91,209,248,255))
        draw.point((x,y-1),fill=(236,225,255,255))
    return im.resize((128,128),Image.Resampling.NEAREST)

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
        _put(files,name,trichterherz_sprite() if name=="trichterherz" else dimensionsklinge_sprite() if name=="dimensionsklinge" else texture)

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
