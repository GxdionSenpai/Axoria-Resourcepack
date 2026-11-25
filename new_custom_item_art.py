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

def titanfaust_sprite():
    # Vanilla iron horse armor provides the metal palette and shading.
    # No vanilla gauntlet exists; build a compact, custom closed fist.
    raw=base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAABAAAAAQBAMAAADt3eJSAAAAJ1BMVEUAAADZ2dm9vb2qqqqDg4NpaWk/Pz8cHBxFBQUXFxc6BAQyBAQMDAysHaQzAAAAAXRSTlMAQObYZgAAAE tJREFUeNpjIASY4QxTKMOIOQAioGQEZZimJTAwOFqUN4cBeSwiEdOXpYGEXbMq25wdgCJhWTO3hQDVsoZGn9kWChRhSwOBBCzWAQAjXxBdqDMTTgAAAABJRU5ErkJggg==".replace(" ",""))
    metal=Image.open(BytesIO(raw)).convert("RGBA")
    shades=sorted({p[0] for p in metal.getdata() if p[3] and p[0]==p[1]==p[2]})
    def steel(i):
        v=shades[round((len(shades)-1)*i/4)]
        return (max(0,v-20),max(0,v-12),min(255,v+16),255)
    im=Image.new("RGBA",(32,32),(0,0,0,0))
    d=ImageDraw.Draw(im)
    ink=(24,19,36,255); gold=(201,133,37,255); bright=(255,215,105,255)
    blue=(24,62,137,255); light=(55,126,217,255)
    d.polygon([(3,23),(11,15),(12,9),(16,5),(20,3),(26,5),(30,10),(29,16),
               (24,21),(18,22),(11,30),(6,29)],fill=ink)
    d.polygon([(5,23),(13,15),(19,20),(10,28),(7,27)],fill=blue)
    d.line([(6,23),(12,17),(16,20),(9,26)],fill=light,width=2)
    d.polygon([(12,15),(13,10),(17,6),(23,5),(28,10),(27,15),(22,20),(18,20)],fill=steel(2))
    for x,y in ((18,7),(22,6),(26,8),(28,12)):
        d.polygon([(x-2,y),(x,y-2),(x+2,y),(x+1,y+4),(x-2,y+3)],fill=ink)
        d.polygon([(x-1,y),(x,y-1),(x+1,y),(x,y+3),(x-1,y+2)],fill=steel(4))
    d.polygon([(13,11),(17,10),(19,13),(17,17),(13,16),(11,14)],fill=ink)
    d.polygon([(13,12),(16,11),(17,13),(15,15),(13,14)],fill=steel(3))
    # Gold reinforcement bands and a compact blue energy core.
    d.line([(5,23),(9,27),(12,25)],fill=gold,width=2)
    d.line([(11,17),(16,22),(19,19)],fill=gold,width=2)
    d.line([(6,23),(9,26)],fill=bright)
    d.polygon([(14,16),(18,13),(22,16),(18,20)],fill=ink)
    d.polygon([(15,16),(18,14),(21,16),(18,19)],fill=gold)
    d.polygon([(16,16),(18,15),(20,16),(18,18)],fill=(53,205,255,255))
    d.point((18,15),fill=(220,252,255,255))
    return im.resize((128,128),Image.Resampling.NEAREST)

def gravitationsbrecher_sprite():
    # Authentic vanilla mace, preserving its heavy square head and grip.
    base=Image.open(BytesIO(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAUVBMVEWHibWAhbB9grBsdqtic6peb6FXbJ1rU2Z+PixTSVt2OSdqMSJeLx9QJxoAAAC/zue1pcqZoa56gsR8hJFmbHpQY5BVXGlCR1IjQmkuMzseIil9yPOhAAAAD3RSTlMAAAAAAAAAAAAAAAAAAAAnp8O0AAAAgklEQVR42k3K2xKDIAyE4dQDPVjXKsJC3v9BG6B22JvM908E18h6pGl5cN+ISMjfcd80K6T6Zc7eCn7BTDOjtgCe3vuNtNI+StlJzWwBd+jZ/K5hlHCYilGCG8KRoMUrxDyFT7o9ocUW3GweRqw2lADz5HBNyCPNDl04FZ0hqrqg2xfZ/BBADZQUEQAAAABJRU5ErkJggg=="))).convert("RGBA")
    palette=((20,12,34),(49,26,76),(89,47,143),(148,85,207),(213,159,245))
    pixels=[]
    for r,g,b,a in base.getdata():
        if not a:
            pixels.append((0,0,0,0));continue
        v=max(0,min(4,((r+g+b)/3-25)/185*4))
        i=min(3,int(v));t=v-i
        pixels.append(tuple(round(palette[i][k]*(1-t)+palette[i+1][k]*t) for k in range(3))+(255,))
    base.putdata(pixels)
    im=base.resize((48,48),Image.Resampling.NEAREST)
    original=im.copy()
    d=ImageDraw.Draw(im)
    # Locate the heavy head from the opaque upper-right vanilla pixels.
    points=[(x,y) for y in range(24) for x in range(24,48) if original.getpixel((x,y))[3]]
    if points:
        x=(min(p[0] for p in points)+max(p[0] for p in points))//2
        y=(min(p[1] for p in points)+max(p[1] for p in points))//2
        # Compact black-hole core, purple event horizon and gold housing.
        d.polygon([(x,y-7),(x+6,y-4),(x+7,y+2),(x+3,y+6),(x-3,y+6),(x-7,y+2),(x-6,y-4)],fill=(32,15,49,255))
        d.ellipse((x-5,y-5,x+5,y+5),fill=(207,141,54,255))
        d.ellipse((x-4,y-4,x+4,y+4),fill=(181,74,246,255))
        d.ellipse((x-2,y-2,x+2,y+2),fill=(13,7,29,255))
        d.line([(x-4,y-2),(x-2,y-4),(x+1,y-4)],fill=(246,204,255,255))
        # Solid segmented orbit crossing the core, not transparent glow.
        d.line([(x-9,y+3),(x-6,y+5),(x-1,y+4)],fill=(87,35,145,255),width=2)
        d.line([(x+3,y+1),(x+7,y-2),(x+8,y-5)],fill=(194,110,255,255),width=2)
        d.point((x+7,y-4),fill=(240,213,255,255))
    # Reinforced gold bands only where the existing shaft is opaque.
    for y in (29,30,38,39):
        for x in range(25):
            if original.getpixel((x,y))[3]:
                d.point((x,y),fill=(210,145,53,255) if y%2 else (255,210,109,255))
    # Scale without interpolation or partial alpha.
    return im.resize((128,128),Image.Resampling.NEAREST)

def abyss_dreizack_sprite():
    # Original vanilla trident silhouette, with a deep-ocean sapphire palette.
    # Deliberately distinct from the green Elder Guardian eye design.
    base=Image.open(BytesIO(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAbUlEQVQ4y2NgoAeYNm3afxCgSPONGzfABoBoog3DpRkkTrQBZGsGgezs7P96cQH/0TUT7Q2Q5oi5fWBD0DWDDCfKAIfKTDBGdglRmsXcLcEaQTQIgzTBMNE2gzSSHO8wf480zWQHGCy6yNYMBACktqum4kbbjgAAAABJRU5ErkJggg=="))).convert("RGBA")
    palette=((9,19,46),(15,40,91),(23,83,161),(42,159,222),(163,237,255))
    pixels=[]
    for r,g,b,a in base.getdata():
        if not a:
            pixels.append((0,0,0,0));continue
        v=max(0,min(4,(0.2126*r+0.7152*g+0.0722*b-25)/205*4))
        i=min(3,int(v));t=v-i
        pixels.append(tuple(round(palette[i][k]*(1-t)+palette[i+1][k]*t) for k in range(3))+(255,))
    base.putdata(pixels)
    im=base.resize((32,32),Image.Resampling.NEAREST)
    original=im.copy()
    d=ImageDraw.Draw(im)
    # Add icy cyan highlights to the three prongs, inside their outlines.
    for y in range(1,12):
        xs=[x for x in range(14,32) if original.getpixel((x,y))[3]]
        runs=[]
        for x in xs:
            if runs and x==runs[-1][-1]+1:runs[-1].append(x)
            else:runs.append([x])
        for run in runs:
            if len(run)>=2 and y%3!=2:
                d.point((run[len(run)//2],y),fill=(132,233,255,255))
    # A compact asymmetric whirlpool wraps around the shaft below the fork.
    # Use connected, opaque pixels rather than an eye or a floating glow.
    y=14
    xs=[x for x in range(32) if original.getpixel((x,y))[3]]
    if xs:
        x=xs[len(xs)//2]
        outer=[(x-3,y-4),(x-6,y-2),(x-6,y+1),(x-3,y+4),
               (x+2,y+4),(x+5,y+2),(x+6,y-1)]
        d.line(outer,fill=(9,32,77,255),width=3)
        d.line(outer,fill=(30,136,220,255),width=2)
        d.line([(x-5,y-1),(x-5,y+1),(x-3,y+3),(x+1,y+3)],fill=(154,239,255,255))
        d.line([(x+2,y+1),(x+1,y-1),(x-1,y-1),(x-2,y+1)],
               fill=(68,191,247,255))
    # Silver-blue shaft bands, kept inside the original silhouette.
    for y in (20,21,25,26):
        for x in range(32):
            if original.getpixel((x,y))[3]:
                d.point((x,y),fill=(151,224,249,255) if y%2==0 else (46,108,176,255))
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
        _put(files,name,trichterherz_sprite() if name=="trichterherz" else dimensionsklinge_sprite() if name=="dimensionsklinge" else titanfaust_sprite() if name=="titanfaust" else gravitationsbrecher_sprite() if name=="gravitationsbrecher" else abyss_dreizack_sprite() if name=="abyss_dreizack" else texture)

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
