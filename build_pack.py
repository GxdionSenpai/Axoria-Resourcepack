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
    ("book", "skyblock_menu_book", 1016),
]
source = Path("source-pack.zip")
if not source.is_file():
    raise SystemExit("Upload source-pack.zip first")
out = Path("axoria-resourcepack.zip")
with zipfile.ZipFile(source) as source_zip:
    assert source_zip.testzip() is None
    assert "pack.mcmeta" in source_zip.namelist()
    files = {name: source_zip.read(name) for name in source_zip.namelist() if not name.endswith("/")}
# Vanilla high furnace item rendering must never be overridden by a special
# item model. Schmiedekern now uses non-placeable MAGMA_CREAM instead.
files.pop("assets/minecraft/items/blast_furnace.json",None)
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
# Approved 128x128 Axoria backpack, losslessly embedded as a 33-color indexed sprite.
import zlib
_backpack_data = zlib.decompress(base64.b85decode("c-rln&5kQM6@YX5c2zpAireXN%CYMwkw6H<XvBh9AwXg=GjG5Gi3KafjtvM{^As#u^B_pP1<wJ+`LSKDO46yi-AJ>@xk}$k*>ygjWBd5nmDP%*U#-4@|Gw#^`(g#3UVZVaUjOtDz5D8~eZASN;L~@{+ZBBJ?<ui@PyhXw?Fv5q4>s!+eEKgByA^!;FTeg>|Mhq3{+B;I_P_q^U;5wt=)3*zfBbp>=bwGv|LvQf^#A(fFZzG~{pbCE{_$1+-+%t8U)|*{ce%@5?sAuJqkOj7%0#wsV_v;?lHE#;1a7>k-f|Hmd3(J@^8CE9b#0Bc)|eWuHqXzO>TN&6dNoxu_Ikagy|1)rPp7USIi60f(CSh}u6N{m9oPHh9(Z_+A{FR8dVY62HA1P!3!*0V+Ht)l^v8$CEDGrj_LE&oWfz3&9k0}Te0W&Yf|1^)>)M*6?T*bAeo6JZP_G-;TVg+WD_^hIPb^B6$akpLvEFPb^#V82cKUj1D9vYg!2>!!ho=rKS`K`+OJ+l<7r2qh3BOc&D9ynK4>S8<!e{&I%Y3|g!oR>TU*|v0cYdC@m-&r#FtaV_txJ_XT@c{c=qD80v@P<J;(S&YJgmS^Ywoh4|7*~O@yDWG<gZyK{SW-Mwa#%p;3xf$e?j#p@HO)ZZ`+hVv7h;5zHjGS_)pjQ`XV3eUGe`ye$J10@&4!j_jctZL!C8zOZ&<AdP9Y!{G4>=gWlM$#Lx0G34D?|Z71sTQ}9iE_G_Z|I={KVf3y8@T$Na9D&>3Hzh-_`k|?coMWVGXv+DxIz8*YMma;5G#(Wq7i}*aIvY5;$)~m#8_^cf2d3hmz{z-he6q=@;DT7}5I$uUU$14T=EawTZfX~Liz>;Q9u%;i6-v36wT#UUj2EBN`mfaC@rIUe0Q1K90z~`|CD?jsLRadIgY}f02@V~}Epd>uRe5t}1T*`;c>jT^0N%4Xr<SqN<3s-z$`>PL_g)HZj|D|pr-#K=$g6>0<%h#{*lc)#}LBGL-Tx35k{*TyR98E73XaGN+h5E}fuC`w9;ZbxQWnrxHaZ&OokPjN>;c>xARwd-q)5DBekbez)Ske-u6QoaWV#$Qh_RGMZmw!D(`=#!V-9GoZXp(cpRS$-E=Q})4>hR^hX<Fc`$X`9o-h33egB8dR_z9nGGoPo+c^f^Scf-Z9EyyPF_xXBcKV9Z~m=X|HTjKj~ukp*xvi%p>uN3<~^e8IcgOIa9aRXrJVdOV}$<uOrAow3dmc?SevBrV=eLnDWh$yE$&Sp?tfBaY@AODAmj(7K5p75a@R^tl%znG892m9ai0pRtc#V{{G`{9ZIKepL>^TB?L_OCDUJDS`$`#PSaxXKbge-Hi^`PRk$_u&`PpBBd4;bTK{n`eKAF|y4Nj>SF#$Np#j<`ekFfoV9Np4JKf6!-u|Gh4p=co_KHf)Rg_{kxs_f8YoE9c=9rJ~p8BS8P9&hZSgI|8CJ)$X2N-pH{IfBNwzmnkHW2-Nq-T7x+sC-xd$@X#7$CqyKYUP$9}>U?FsY-wqGbu<=0WdQ<<)Z85V8cB=v+k1?)xHIIMd@59{B$kP|(K*q;8xc1}Ufg)qIRK>gl!5vOM4e+LJy#4ExpI_&XVo>0NZ$O#G1JRj$@V<6<-jVWi?qhUwdzp^~EzbcAS_8kXodf%~^X)Iu{tJBOwBgTyrms!7ZU_61@4)Ba*YMn9H0&=@KJ1aue!6bL9Q5O_ZrJ}z`0Rfee+eJ+H=1qef2~!@r>`x~Mb7pTKAi|G<>M)CWjb0{DgM&Pi~NfCJnM<CBR`%Ecs_1htX;%c$hW4#^#@~oJY?A89wdWE3%g6)U7%$KyF+Ol|5&;o_$|f8<@{~R_aQK(|LEN~|M;vmo&Q;KFtX=`@jduYJ_NKJ<szTDW0-$f(w+`)=1b-q&woloP@ByEwvCgL=RaKs{?ps}bdnzSU!LDwk3Y@8hm`aHtp^2xKRf>Ig8z*vg>2&x$oJ&#*W$k$f)5+7L^;?$cL_$mBR)7H;Zq25zz0t^yz=6mmWN@xhZ4L<_#I$z9((`K&ivyshV=Fy_6Od;W?>SXODKWyzuzCc{fQ<yD+?-^uSwtv{`w}w6S14(ogWo|5MRyY!;ZnXTB-36m?N?Cr6^NPGu}xSAW~T0qbT*z1?&ARK2#f=Uk{oZE7Z2w7B`I-Hsp3FDs%xf;t-EHAls$$9TF&MKIVDYlOHJ`W#@Y|tr||KTSEZ&LVOtU!HH!lybA_?gWC^28$%iK$#?<J2~h_;@U0Ny7GDWd+tg_d&BE9PBmRl_C+26KADj;lRmP;68taUBeHH>A&u}4Q<D?cpGz6d(*aac$u4|uJP(^4O<ijBo?|9Dz{JLq91R32>&*3L6=11`;KnUJ)QB-MZWp67lc#U_4a)I72-6%oF2GsNHPX(Mn=b6|Aywwc+uHv)qs$+f^E3|wLJL<=Qzk8JrTdbPjbwt7RsT57?cY1Bd{%`q+*BS5sE>>uS&~#islA5RB4L+=S&Wr`TS1D+LDETY}=O`XI7)otxgNGpk3rNuST2)XqQ3E@QdHl(P_*UO&JbI^IB>?j={esO6WZAWlcwcZ6Bsw2|GcYluvE^JouD^WrPWBs!pk?yoj)9N%cWi$w9QgcW1Xcq*JBtq%nL4iOHu9wm171tf;P|(!pZPkJN*Vb!s;SZc^)3E3;Zs~Y9WDER#IL}946%Ov<4f5Q9|k}DQp32T50K2i+5cNr!h_CK3BQW=tHgffa|c;7;d4cL$PWAp?KiXLA51Si(Zg6q+c%8Dq&5yE;&(xJNBk-j65nw2>b#m`Lu%ZO__K}i2U5q1Jj;Q@5})5eLUdrhUwe+shubtB9rJks!~EA&4XJ4<{ua0S{y~1-&JPB@k2sh3#ur-R+f+@;zmbA$oc{qyhr_$2<Adn`5Xn5h<7nKae8+rkc=^Cl!uFFIx4D&jOI+_Ip8U7E(y*pz!TBKOPu{`K;wvT{I~*?I20Did73OagE${%F)f_8<i<p$J=is#W!UvhJkS|dmbRt~Xu$a*c#yA}ny`H2Hj{%v-KQ_Ab{08}`SjpAy=H3VLEoFjZk&o8Wu#S9<3!)Co6WE4)7=M9}KEa%~ifRnyWApeG?)(QnPHgZp+V7(MT8V*QDrgX1VVUKLN?}3|{EANDZu0Tqe-7X1$hVciDrbD7%Q0Wg;Dh}*&4*P>g{3t3pQbrFU2{x<$ssfyvZVf}MO*4PL=6wj?HoSx1g++<*6WLW2mESC>?=3rTS^*K=|vbWkaPKd+k~UYFQt+1uJFnKO=>^RS}*v04!>Z&o8%v!@2>G{J}(>l-;R=>`FuCZ-H_i{KmMZB6Fy6b|IBye9MaC^+ezwpgWq1_LmJVzNfJ9}{CWEm>q!;!-3&hZU-Qw8GiUsA24DK>b?8ydasB$^!U`PvpEq{g|7<_6f8>8xdo`}6A7jk)zaMjP^MoOe^AF<lpd8t+eUqtq9RJ}e-Tqjb!LnH0UVj2V3Xb-aPu;@thjv!xGT)8)7Ww6z`0uBS-vBnqH*|tw>@YOO<3Hlj|9IwMCVV%`eth>+Z1Lwtlf8?kMUYo~S`Mlz=9^WL3UG0CQGwbP#q+!qFriH~5>?7-DmwheNS_rcA<rt$eg}>xaMR|e$$ym6?+4K_{PQ4M_Tm<xO5B2J%uIe!lqF?U^h=(2e0FAK4DQnsUE#W=#~R8-@8ApCX3~z5K4qeChRFDM(6Z?L?`BuXGg-txlVZ17@&dLfQy~i$@x9~1j$ADL{lf*HloLt4TMqq1vRS>mFkj+7Is)-04RYEnyd(b~d@{4VAR@W#uZq=O?sAvA+~wOX{{ufZ(Bu"))
_backpack_palette = [_backpack_data[i:i+4] for i in range(0,132,4)]
_backpack_pixels = b"".join(_backpack_palette[index] for index in _backpack_data[132:])
backpack_image = Image.frombytes("RGBA", (128,128), _backpack_pixels)
_backpack_output = BytesIO()
backpack_image.save(_backpack_output,format="PNG",optimize=True)
backpack_png = _backpack_output.getvalue()
backpack_image = Image.open(BytesIO(backpack_png)).convert("RGBA")
backpack_alpha = {a for *_, a in backpack_image.getdata()}
if backpack_image.size != (128, 128) or not backpack_alpha.issubset({0, 255}) or backpack_alpha != {0, 255}:
    raise ValueError("Backpack must be a 128x128 sprite with transparent background and opaque item pixels")
files["assets/axoria/textures/item/backpack.png"] = backpack_png
files["assets/axoria/models/item/backpack.json"] = json.dumps({
    "parent": "minecraft:item/generated",
    "textures": {"layer0": "axoria:item/backpack"}
}, separators=(",", ":")).encode()

# Permanent Skyblock menu book (CustomModelData 1016).
# 64x64 opaque silhouette extracted from the approved Axoria artwork.
# Empty exterior pixels are alpha 0; no partial-alpha pixels are allowed.
skyblock_menu_png=base64.b64decode(Path("skyblock_menu_book.png.b64").read_text().strip())
skyblock_menu_image=Image.open(BytesIO(skyblock_menu_png)).convert("RGBA")
if skyblock_menu_image.size!=(64,64):
    raise ValueError("Skyblock menu book must be a 64x64 sprite")
skyblock_menu_alphas={alpha for *_,alpha in skyblock_menu_image.getdata()}
if skyblock_menu_alphas!={0,255}:
    raise ValueError("Skyblock menu book requires only 0 and 255 alpha")
files["assets/axoria/textures/item/skyblock_menu_book.png"]=skyblock_menu_png
files["assets/axoria/models/item/skyblock_menu_book.json"]=json.dumps({
    "parent":"minecraft:item/generated",
    "textures":{"layer0":"axoria:item/skyblock_menu_book"}
},separators=(",",":")).encode()

files["assets/axoria/textures/item/eissense.png"] = create_eissense_png()
files["assets/axoria/models/item/eissense.json"] = json.dumps({
    "parent": "minecraft:item/generated",
    "textures": {"layer0": "axoria:item/eissense"}
}, separators=(",", ":")).encode()

# Three individually readable crate-key rarities. Every painted pixel is
# fully opaque (alpha 255); only the exterior silhouette is transparent.
# Never recolor or replace Minecraft's normal trial_key outside CustomModelData.
def create_axoria_key_png(tier):
    # Source sprites are taken from the previously approved Axoria key
    # comparison illustration and hand-prepared as crisp 64x64 item sprites.
    # The silhouette remains pixel-sharp with no partially transparent pixels.
    raw=base64.b64decode(Path("axoria_key_"+tier+".png.b64").read_text().strip())
    image=Image.open(BytesIO(raw)).convert("RGBA")
    if image.size!=(64,64):
        raise ValueError("Axoria "+tier+" key texture must be exactly 64x64")
    alphas={a for *_,a in image.getdata()}
    if not alphas.issubset({0,255}) or 0 not in alphas or 255 not in alphas:
        raise ValueError("Axoria "+tier+" key must have opaque sprite pixels and a transparent exterior")
    return raw

for rarity in ("normal","epic","legendary","mythical"):
    texture_name="axoria_key_"+rarity
    files["assets/axoria/textures/item/"+texture_name+".png"]=create_axoria_key_png(rarity)
    files["assets/axoria/models/item/"+texture_name+".json"]=json.dumps({
        "parent":"minecraft:item/generated",
        "textures":{"layer0":"axoria:item/"+texture_name}
    },separators=(",",":")).encode()

# Ten handcrafted solid-pixel 64x64 Axoria item sprites.
from new_custom_item_art import render_items, NAMES as NEW_NAMES, BASE as NEW_BASE
render_items(files)
items.extend((base,name,1101+i) for i,(base,name) in enumerate(zip(NEW_BASE,NEW_NAMES)))
# Bright bow model for charged starshot after five hits.
items.append(("bow","sternenbogen_charged",1111))

# These exact IDs match AxoriaCrates.keyTextureId(). Unmarked vanilla
# TRIAL_KEYs, and all players who decline the entire pack, stay vanilla.
trial_key_fallback={"type":"minecraft:model","model":"minecraft:item/trial_key"}
trial_key_entries=[]
for numeric,rarity in ((1013,"normal"),(1014,"epic"),(1015,"legendary"),(1016,"mythical")):
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

# One dispatch per vanilla item: preserve all pre-existing magic item models
# even if several Axoria items share the same base (e.g. both custom shears).
grouped={}
for base,custom,value in items:
    grouped.setdefault(base,[]).append((custom,value))
for base, models in grouped.items():
    vanilla = ("axoria:item/vanilla_clock" if base=="clock" else "minecraft:item/"+base)
    vanilla_model={"type":"minecraft:model","model":vanilla}
    if base=="chest":
        def chest_model(texture):
            return {"type":"minecraft:special","base":"minecraft:item/chest",
                    "model":{"type":"minecraft:chest","texture":"minecraft:"+texture}}
        vanilla_model={"type":"minecraft:select","property":"minecraft:local_time",
            "pattern":"MM-dd","cases":[{"when":["12-24","12-25","12-26"],
                "model":chest_model("christmas")}],
            "fallback":chest_model("normal")}
    entries=[]
    for custom,value in sorted(models,key=lambda pair:pair[1]):
        entries.append({"threshold":value,"model":{"type":"minecraft:model",
            "model":"axoria:item/"+custom}})
        entries.append({"threshold":value+0.5,"model":vanilla_model})
    files["assets/minecraft/items/"+base+".json"]=json.dumps({
        "model":{"type":"minecraft:range_dispatch",
                 "property":"minecraft:custom_model_data",
                 "index":0,"fallback":vanilla_model,"entries":entries}
    },separators=(",",":")).encode()

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
        # Preserve intentional transparent holes, especially the OPEN space
        # between Sternenbogen's bow limbs and string, the crab claw opening
        # and the rocket's actual muzzle. The old generic "fill enclosed holes"
        # pass destroyed these important original art details.
        if Path(path).stem in set(NEW_NAMES)|{"sternenbogen_charged","skyblock_menu_book"}:
            image=Image.open(BytesIO(data)).convert("RGBA")
            if image.size!=(128,128) or {a for *_,a in image.getdata()}!={0,255}:
                raise ValueError("Custom Axoria 128px item texture invalid: "+path)
            continue
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
