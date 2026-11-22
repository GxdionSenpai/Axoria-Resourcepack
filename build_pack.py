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

# Approved Guardian Season 1 weapon sprites, looking right in the standard
# Minecraft inventory orientation. The compact atlas stores three indexed
# 64x64 sprites with binary transparency, then scales losslessly to 128x128.
# Keeping the approved original art in the repository means pack releases
# are deterministic and do not depend on a live image service.
import zlib
import base64
weapon_bytes=zlib.decompress(base64.b85decode(
    Path("season1_guardian_weapons.b85").read_text().strip()))
cursor=0
for item_name,vanilla_item,model_id in (
    ("s1_gezeitenklinge","diamond_sword",1201),
    ("s1_tiefenjaegerbogen","bow",1202),
    ("s1_elderdreizack","trident",1203)):
    palette_size=weapon_bytes[cursor];cursor+=1
    palette=[(0,0,0,0)]
    for _ in range(palette_size):
        r,g,b=weapon_bytes[cursor:cursor+3];cursor+=3
        palette.append((r,g,b,255))
    index_bytes=weapon_bytes[cursor:cursor+64*64];cursor+=64*64
    sprite=Image.new("RGBA",(64,64))
    sprite.putdata([palette[index] for index in index_bytes])
    sprite=sprite.resize((128,128),Image.Resampling.NEAREST)
    if {a for *_,a in sprite.getdata()}!={0,255}:
        raise ValueError("Season 1 texture must be strictly transparent/opaque: "+item_name)
    out_buffer=BytesIO()
    sprite.save(out_buffer,format="PNG",optimize=True)
    files["assets/axoria/textures/item/"+item_name+".png"]=out_buffer.getvalue()
    files["assets/axoria/models/item/"+item_name+".json"]=json.dumps({
        "parent":"minecraft:item/generated",
        "textures":{"layer0":"axoria:item/"+item_name}
    },separators=(",",":")).encode()
    # Direct minecraft:item_model component points here (modern clients).
    # Keep the numerical CMD fallback below for older Season-1 item stacks.
    files["assets/axoria/items/"+item_name+".json"]=json.dumps({
        "model":{"type":"minecraft:model","model":"axoria:item/"+item_name}
    },separators=(",",":")).encode()
    items.append((vanilla_item,item_name,model_id))
if cursor!=len(weapon_bytes):
    raise ValueError("Invalid Guardian weapon art payload: trailing bytes")

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
    if base=="trident":
        # Tridents do NOT have a generic flat item-model fallback when held.
        # Vanilla uses a 2D item in GUI/ground/fixed, and a special 3D
        # trident renderer in first/third person. Preserve both contexts.
        # Without this, players see the purple/black missing model in hand.
        trident_special=lambda base_name: {
            "type":"minecraft:special",
            "base":"minecraft:item/"+base_name,
            "model":{"type":"minecraft:trident"}
        }
        vanilla_model={
            "type":"minecraft:select",
            "property":"minecraft:display_context",
            "cases":[{
                "when":["gui","ground","fixed"],
                "model":{"type":"minecraft:model","model":"minecraft:item/trident"}
            }],
            "fallback":{
                "type":"minecraft:condition",
                "property":"minecraft:using_item",
                "on_true":trident_special("trident_throwing"),
                "on_false":trident_special("trident_in_hand")
            }
        }
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


# Official Axoria pause-menu styling. Keep ALL built-in font providers.
# Earlier pack versions replaced default.json with incomplete references,
# breaking symbols and resource pack rendering for other players.
from PIL import ImageDraw

logo_file=Path("assets/axoria/textures/font/esc_logo.png")
if not logo_file.is_file():
    raise RuntimeError("Missing actual Axoria ESC logo asset: "+str(logo_file))
logo_data=logo_file.read_bytes()
with Image.open(BytesIO(logo_data)) as validated_logo:
    validated_logo.verify()
# Exact freshly generated ESC crest; never silently publish an older image.
# Changing this source file also triggers the existing resourcepack release
# workflow, which updates the downloadable ZIP and its SHA-1 manifest.
with Image.open(BytesIO(logo_data)) as logo_check:
    if logo_check.size != (256, 118):
        raise RuntimeError("Axoria ESC logo must be 256x118 PNG, got "+str(logo_check.size))
files["assets/axoria/textures/font/esc_logo.png"]=logo_data
font_file="assets/minecraft/font/default.json"
# Match vanilla Minecraft 1.21 font/default.json exactly, only prepending
# one bitmap glyph. This preserves all standard, uniform and unifont symbols.
try:
    existing_font=json.loads(files[font_file].decode("utf-8")) if font_file in files else {}
except (UnicodeError,ValueError):
    existing_font={}
providers=existing_font.get("providers")
if not isinstance(providers,list) or not providers:
    providers=[
        {"type":"reference","id":"minecraft:include/space"},
        {"type":"reference","id":"minecraft:include/default","filter":{"uniform":False}},
        {"type":"reference","id":"minecraft:include/unifont"}]
providers=[entry for entry in providers
           if not(isinstance(entry,dict) and entry.get("file")=="axoria:font/esc_logo.png")]
providers.insert(0,{
    "type":"bitmap","file":"axoria:font/esc_logo.png",
    "ascent":19,"height":105,"chars":[chr(0xE000)]
})
files[font_file]=json.dumps({"providers":providers},ensure_ascii=False,separators=(",",":")).encode("utf-8")
for lang in ("en_us","de_de"):
    lang_file="assets/minecraft/lang/"+lang+".json"
    try:
        translations=json.loads(files[lang_file].decode("utf-8")) if lang_file in files else {}
    except (UnicodeError,ValueError):
        translations={}
    translations["menu.game"]=chr(0xE000)
    files[lang_file]=json.dumps(translations,ensure_ascii=False,separators=(",",":")).encode("utf-8")

def axoria_pause_button(hover=False,disabled=False):
    # Close to the approved poster's physical slate-grey buttons and
    # luminous pink diagonal corner trims (not solid purple buttons).
    picture=Image.new("RGBA",(200,20),(0,0,0,0))
    d=ImageDraw.Draw(picture)
    # Ink-black drop shadow, then bevelled 9-slice-safe 3 px frame.
    d.rectangle((0,1,199,19),fill=(10,6,14,255))
    d.rectangle((1,1,198,17),fill=(36,34,40,255))
    for y in range(3,16):
        if disabled:
            grey=49+y//5; color=(grey,grey-1,grey+3,255)
        elif hover:
            grey=102-y//4; color=(grey+3,grey-6,grey+10,255)
        else:
            grey=96-y//5; color=(grey,grey-1,grey+4,255)
        d.line((3,y,196,y),fill=color)
    # Silver bevel and thin lilac border, dark underside.
    d.line((3,2,196,2),fill=(174,162,182,255))
    d.line((2,3,2,16),fill=(112,100,120,255))
    d.line((197,3,197,16),fill=(82,68,90,255))
    d.line((2,17,197,17),fill=(22,17,29,255))
    d.line((3,18,197,18),fill=(7,5,10,255))
    # Important: diagonal magenta decorations exactly like the reference.
    if not disabled:
        pink=(255,124,246,255) if hover else (224,84,220,255)
        glow=(247,167,248,255) if hover else (169,67,184,255)
        d.line([(3,4),(7,8),(12,14)],fill=glow,width=2)
        d.line([(4,3),(8,8),(13,14)],fill=pink,width=1)
        d.line((12,14,18,14),fill=pink,width=1)
        d.line([(196,4),(192,8),(187,14)],fill=glow,width=2)
        d.line([(195,3),(191,8),(186,14)],fill=pink,width=1)
        d.line((181,14,187,14),fill=pink,width=1)
    buf=BytesIO();picture.save(buf,format="PNG",optimize=True)
    return buf.getvalue()

for filename,hover,disabled in (
    ("button.png",False,False),("button_highlighted.png",True,False),
    ("button_disabled.png",False,True)):
    asset="assets/minecraft/textures/gui/sprites/widget/"+filename
    files[asset]=axoria_pause_button(hover,disabled)
    files[asset+".mcmeta"]=json.dumps({
        "gui":{"scaling":{"type":"nine_slice","width":200,"height":20,"border":3}}
    },separators=(",",":")).encode("utf-8")

# Season 1 wearable Guardian/Elder-Guardian armor from the user's EXACT
# 64x64 NameMC skins. Equipment assets are selected per item via
# ItemMeta.getEquippable().setModel(axoria:s1_guardian / s1_elder_guardian).
# Vanilla leather armor and all other custom items remain unaffected.
for gear_name,source_name in (
    ("s1_guardian","season1_guardian_skin.png"),
    ("s1_elder_guardian","season1_elder_guardian_skin.png")
):
    with Image.open(source_name) as skin_file:
        skin=skin_file.convert("RGBA")
    if skin.size!=(64,64):
        raise ValueError("Season 1 skin must be 64x64: "+source_name)
    # Standard player skin and Minecraft humanoid armor share the classic
    # helmet UV layout. Merge modern second-head-layer pixels into the
    # base head for the exact eye/face markings from each uploaded skin.
    upper=skin.crop((0,0,64,32)).copy()
    for sy in range(16):
        for sx in range(32):
            under=upper.getpixel((sx,sy))
            above=skin.getpixel((sx+32,sy))
            if above[3]:
                composite=Image.alpha_composite(
                    Image.new("RGBA",(1,1),under),
                    Image.new("RGBA",(1,1),above))
                upper.putpixel((sx,sy),composite.getpixel((0,0)))
    # The skin's head hat-layer data isn't a separate armor cube.
    for sy in range(16):
        for sx in range(32,64):upper.putpixel((sx,sy),(0,0,0,0))
    lower=Image.new("RGBA",(64,32),(0,0,0,0))
    lower.paste(skin.crop((0,16,16,32)),(0,16))
    for category,image in (("humanoid",upper),("humanoid_leggings",lower)):
        encoded=BytesIO()
        image.save(encoded,format="PNG",optimize=True)
        files["assets/axoria/textures/entity/equipment/"+category+"/"+gear_name+".png"]=encoded.getvalue()
    files["assets/axoria/equipment/"+gear_name+".json"]=json.dumps({
        "layers":{
            "humanoid":[{"texture":"axoria:"+gear_name}],
            "humanoid_leggings":[{"texture":"axoria:"+gear_name}]
        }
    },separators=(",",":")).encode("utf-8")

# Emerald & Amethyst custom wearable armor. These are true vanilla-format
# 64x32 UV maps (helmet/body/arms/boots and leggings), not preview images.
# No vanilla armor assets are overwritten. Equipped Axoria pieces select
# axoria:emerald / axoria:amethyst through their Equippable component.
from PIL import ImageDraw

def make_axoria_armor_layer(kind,leggings=False):
    # Real equipped texture, with the Minecraft-required 2:1 UV ratio.
    # Paint at 128x64 (2x vanilla UV detail) and export 256x128.
    if kind=="emerald":
        edge="#062319"; shadow="#0A402E"; base="#0D7451"
        high="#24BD7B"; shine="#63F0A0"; core="#B9FFE0"
        trim="#F1C35E"; trim_dark="#92601D"; gem="#30E87D"
    else:
        edge="#1A0F37"; shadow="#33205C"; base="#6531A6"
        high="#AD60ED"; shine="#D99BFF"; core="#FFE2FF"
        trim="#D8C6EF"; trim_dark="#8270B1"; gem="#E18EFF"
    im=Image.new("RGBA",(128,64),(0,0,0,0))
    d=ImageDraw.Draw(im)
    U=2
    def R(x,y,w,h,c):
        d.rectangle((x*U,y*U,(x+w)*U-1,(y+h)*U-1),fill=c)
    def L(points,c,width=1):
        d.line([(x*U,y*U) for x,y in points],fill=c,width=width*U)
    def P(x,y,c):
        d.point((x*U,y*U),fill=c)
    def gem_at(x,y,scale=1):
        # Highlighted emerald / amethyst facets on front-facing panels.
        d.polygon([(x*U,(y-2*scale)*U),((x+2*scale)*U,y*U),
                   (x*U,(y+2*scale)*U),((x-2*scale)*U,y*U)],
                   fill=gem,outline=edge,width=1)
        L([(x-1*scale,y-1*scale),(x,y-2*scale)],core)
        P(x,y-1*scale,shine)
    def face(x,y,w,h):
        R(x,y,w,h,edge)
        R(x+1,y+1,w-2,h-2,shadow)
        if w>=4 and h>=5:
            R(x+1,y+2,w-2,h-4,base)
            L([(x+1,y+1),(x+w-2,y+1)],high)
            L([(x+1,y+2),(x+1,y+h-3)],high)
            L([(x+w-2,y+2),(x+w-2,y+h-2)],edge)
            L([(x+2,y+h-2),(x+w-2,y+h-2)],trim_dark)
    # Standard 64x32 classic armor UV. Build every face: helmet cap,
    # front + side + rear cuirass, sleeves, leg guards and footwear.
    for q in ((8,0,8,8),(16,0,8,8),(0,8,8,8),(8,8,8,8),
              (16,8,8,8),(24,8,8,8),
              (20,16,8,4),(28,16,8,4),(16,20,4,12),
              (20,20,8,12),(28,20,4,12),(32,20,8,12),
              (40,16,4,4),(44,16,4,4),(48,16,4,4),(52,16,4,4),
              (40,20,4,12),(44,20,4,12),(48,20,4,12),(52,20,4,12),
              (4,16,4,4),(8,16,4,4),(0,20,4,12),
              (4,20,4,12),(8,20,4,12),(12,20,4,12)):
        face(*q)
    if not leggings:
        # Crown: frontal gemstone, broad decorative lower rim and
        # framed eye area. Gold metal for emerald, silver for amethyst.
        L([(9,14),(14,14)],trim)
        L([(17,14),(22,14)],trim)
        L([(9,12),(9,9),(12,8),(15,9)],trim)
        gem_at(12,11,1)
        L([(16,13),(18,15),(21,13)],trim_dark)
        L([(24,11),(27,11),(30,12)],shine)
        L([(0,12),(3,13),(6,12)],trim)
        # Chest: angular pauldrons and central jewel, with a separate
        # upper/lower plate, so this does not become a flat dyed shirt.
        L([(17,20),(19,22),(20,21),(23,23)],trim)
        L([(25,23),(28,21),(29,22),(31,20)],trim)
        L([(21,24),(23,22),(25,22),(27,24)],shine)
        gem_at(24,25,1)
        L([(20,29),(22,31),(26,31),(28,29)],trim)
        L([(21,27),(22,29)],trim_dark)
        L([(27,27),(26,29)],trim_dark)
        # Engraved arm braces with a contrasting cuff on every face.
        for x in (40,44,48,52):
            L([(x+1,23),(x+2,24),(x+2,26)],high)
            L([(x+1,29),(x+2,29)],trim)
        # Greaves and boots: knee and toe trims are visible from front,
        # back and side, not only on a 2D inventory icon.
        for x in (0,4,8,12):
            L([(x,25),(x+3,25)],trim)
            L([(x+1,28),(x+2,29)],shine)
            L([(x,30),(x+3,30)],trim_dark)
    else:
        # Leggings use their own 2:1 sheet. Sculpt a highlighted belt,
        # faceted thigh plates and shining knees on all mapped sides.
        for x in (0,4,8,12):
            L([(x,22),(x+3,22)],trim)
            L([(x+1,24),(x+2,25)],shine)
            L([(x,28),(x+1,29),(x+3,28)],trim)
        L([(21,21),(26,21)],trim)
        gem_at(24,25,1)
        L([(20,30),(27,30)],trim_dark)
    if kind=="amethyst":
        # Extra crystal tips: unique elder-purple silhouette markings.
        for x,y in ((10,7),(13,7),(21,22),(27,22),(3,22),(10,27)):
            P(x,y,core)
    else:
        # Emerald: slender gilded gold-corner ornaments.
        for x,y in ((10,7),(14,7),(21,22),(27,22),(3,23),(9,27)):
            P(x,y,trim)
    # 2026 S1 custom armor v3: visibly distinct face-level ornamentation
    # on WORN armor, not just the 128px inventory icon. All coordinates
    # stay inside Minecraft's exact classic armor cube UV islands.
    # Large contrasting trim defines the silhouette even at distance.
    # Helmet front 8..15 x 8..15
    L([(8,15),(8,11),(9,9),(10,8)],trim,width=1)
    L([(15,15),(15,11),(14,9),(13,8)],trim,width=1)
    L([(9,15),(11,14),(12,15),(14,14)],shine)
    P(10,10,core); P(13,10,core)
    # Helmet both side panels (0..7 and 16..23)
    for x in (0,16):
        L([(x+1,10),(x+3,8),(x+6,10)],trim)
        L([(x+1,13),(x+3,14),(x+6,13)],high)
        P(x+3,11,gem)
    # Chest FRONT face has a polished torso centerpiece with two
    # distinct shoulder bosses and crosscut facets.
    L([(20,21),(22,21),(24,23),(26,21),(27,21)],trim)
    L([(20,25),(22,27),(24,25),(26,27),(27,25)],high)
    L([(21,29),(23,30),(25,30),(27,29)],trim)
    P(24,24,core)
    for x in (16,28):
        L([(x,23),(x+2,21),(x+3,23)],trim)
        P(x+2,25,shine)
    # Arm front/side: crystal guards and high-contrast ornamental cuffs.
    for x in (40,44,48,52):
        L([(x+1,20),(x+2,21),(x+2,23)],trim)
        L([(x,28),(x+3,28)],trim)
        P(x+1,25,core)
    # Leg greaves on every UV face.
    for x in (0,4,8,12):
        L([(x+1,21),(x+2,23),(x+1,25)],shine)
        L([(x,27),(x+1,28),(x+3,27)],trim)
        L([(x,30),(x+3,30)],high)
    if kind=="amethyst":
        # Amethyst is spiky / arcane, with brighter crystal veins.
        for cx,cy in ((12,7),(23,23),(24,27),(3,25),(7,10)):
            P(cx,cy,core)
        L([(20,23),(22,24),(21,26)],shine)
        L([(27,23),(25,24),(26,26)],shine)
        L([(10,12),(12,9),(14,12)],core)
        L([(20,26),(22,28),(20,30)],trim)
        L([(27,26),(25,28),(27,30)],trim)
    else:
        # Emerald is royal, with strong gilded plate lines.
        L([(9,9),(12,8),(14,9)],trim)
        L([(20,22),(23,24),(24,23),(25,24),(27,22)],trim)
        L([(20,30),(24,28),(27,30)],trim)
        for x in (40,44,48,52):
            L([(x,30),(x+3,30)],trim)
        for x in (0,4,8,12):
            L([(x,22),(x+3,22)],trim)
    if im.getbbox() is None:raise RuntimeError("Empty armor UV for "+kind)
    return im.resize((256,128),Image.Resampling.NEAREST)

for armor_id in ("emerald","amethyst"):
    for layer_name,is_leggings in (("humanoid",False),("humanoid_leggings",True)):
        texture=make_axoria_armor_layer(armor_id,is_leggings)
        output_png=BytesIO()
        texture.save(output_png,format="PNG",optimize=True)
        if texture.size!=(256,128):
            raise ValueError("Wearable armor must have 2:1 UV, 256x128")
        files["assets/axoria/textures/entity/equipment/"+layer_name+"/"+armor_id+".png"]=output_png.getvalue()
    files["assets/axoria/equipment/"+armor_id+".json"]=json.dumps({
        "layers":{
            "humanoid":[{"texture":"axoria:"+armor_id}],
            "humanoid_leggings":[{"texture":"axoria:"+armor_id}]
        }
    },separators=(",",":")).encode("utf-8")

# Pixel-sharp Season-independent inventory armor icons. CMD thresholds are
# deliberately dedicated to Axoria's two custom sets only; preserve the
# existing vanilla dyed-leather rendering for all unmarked armor.
def make_custom_armor_icon(theme,piece):
    if theme=="emerald":
        outline=(8,43,31,255);base=(15,105,65,255)
        mid=(36,177,103,255);light=(108,238,151,255)
        trim=(241,200,94,255);glow=(197,255,204,255)
    else:
        outline=(38,20,69,255);base=(84,41,133,255)
        mid=(145,72,215,255);light=(212,136,251,255)
        trim=(211,197,244,255);glow=(255,220,255,255)
    icon=Image.new("RGBA",(32,32),(0,0,0,0))
    d=ImageDraw.Draw(icon)
    def jewel(x,y,r=2):
        d.polygon([(x,y-r),(x+r,y),(x,y+r),(x-r,y)],
                  fill=light,outline=outline)
        d.point((x,y-1),fill=glow)
    if piece=="helmet":
        d.polygon([(7,14),(8,8),(12,5),(20,5),(24,8),
                   (25,14),(24,24),(20,27),(19,20),
                   (13,20),(12,27),(8,24)],fill=base,outline=outline)
        d.polygon([(10,13),(11,9),(15,7),(18,7),(22,10),
                   (22,14)],fill=mid)
        d.line((9,15,23,15),fill=trim,width=2)
        d.line((9,22,12,24),fill=light,width=2)
        d.line((20,24,23,22),fill=light,width=2)
        jewel(16,11,3)
    elif piece=="chestplate":
        d.polygon([(7,6),(12,4),(14,7),(18,7),(20,4),
                   (25,6),(29,13),(25,18),(23,15),(23,27),
                   (9,27),(9,15),(7,18),(3,13)],fill=base,outline=outline)
        d.polygon([(9,8),(14,10),(18,10),(23,8),
                   (21,23),(11,23)],fill=mid)
        d.line((10,24,22,24),fill=trim,width=2)
        d.line((5,14,9,10),fill=light,width=2)
        d.line((23,10,27,14),fill=light,width=2)
        jewel(16,15,4)
    elif piece=="leggings":
        d.polygon([(8,5),(24,5),(25,14),(22,27),
                   (17,27),(16,17),(15,27),(10,27),
                   (7,14)],fill=base,outline=outline)
        d.rectangle((10,7,22,11),fill=mid)
        d.line((9,12,23,12),fill=trim,width=2)
        d.line((10,23,14,23),fill=light,width=2)
        d.line((18,23,22,23),fill=light,width=2)
        jewel(16,9,2)
    else:
        for off in (0,12):
            d.polygon([(5+off,8),(13+off,8),
                       (13+off,21),(16+off,23),(16+off,27),
                       (3+off,27),(3+off,23),(5+off,20)],
                      fill=base,outline=outline)
            d.rectangle((7+off,10,11+off,19),fill=mid)
            d.line((4+off,23,14+off,23),fill=trim,width=2)
            d.line((7+off,12,10+off,12),fill=light)
    if icon.getbbox() is None:raise ValueError("Missing icon art: "+theme+" "+piece)
    # Four independently assigned pieces, each exactly 128x128 pixels.
    return icon.resize((128,128),Image.Resampling.NEAREST)

# These four ids are per-ITEM, not per leather material. In Minecraft
# 26.3 item_model (assets/axoria/items/*.json) is authoritative and keeps
# all 8 inventory icons isolated from other leather armor or packs.
# Do NOT override assets/minecraft/items/leather_*.json: that previously
# produced misleading common icons and damaged vanilla fallbacks.
armor_parts=("helmet","chestplate","leggings","boots")
for gear_name in ("emerald","amethyst"):
    for armor_part in armor_parts:
        art_name=gear_name+"_"+armor_part
        image=make_custom_armor_icon(gear_name,armor_part)
        if image.size!=(128,128):
            raise ValueError("Custom armor inventory texture must be 128x128: "+art_name)
        bio=BytesIO()
        image.save(bio,format="PNG",optimize=True)
        files["assets/axoria/textures/item/"+art_name+".png"]=bio.getvalue()
        files["assets/axoria/models/item/"+art_name+".json"]=json.dumps({
            "parent":"minecraft:item/generated",
            "textures":{"layer0":"axoria:item/"+art_name}
        },separators=(",",":")).encode("utf-8")
        files["assets/axoria/items/"+art_name+".json"]=json.dumps({
            "model":{"type":"minecraft:model","model":"axoria:item/"+art_name}
        },separators=(",",":")).encode("utf-8")

# Fail pack release instead of silently shipping blank, corrupt or shared
# armor art. Both equipped variants have two independent 256x128 atlases,
# and eight exact 128x128 individual inventory textures.
for gear_name in ("emerald","amethyst"):
    path="assets/axoria/equipment/"+gear_name+".json"
    parsed=json.loads(files[path])
    for layer_name in ("humanoid","humanoid_leggings"):
        texture_id=parsed["layers"][layer_name][0]["texture"]
        if texture_id!="axoria:"+gear_name:
            raise ValueError("Wrong wearable texture id: "+path+" "+layer_name)
        tex="assets/axoria/textures/entity/equipment/"+layer_name+"/"+gear_name+".png"
        image=Image.open(BytesIO(files[tex]))
        if image.size!=(256,128) or image.getbbox() is None:
            raise ValueError("Invalid 256x128 wearable texture: "+tex)
    for part in armor_parts:
        key=gear_name+"_"+part
        png=Image.open(BytesIO(files["assets/axoria/textures/item/"+key+".png"]))
        if png.size!=(128,128) or png.getbbox() is None:
            raise ValueError("Invalid 128x128 armor icon: "+key)
        if json.loads(files["assets/axoria/items/"+key+".json"])["model"]["model"]!="axoria:item/"+key:
            raise ValueError("Wrong item model: "+key)

# Validate the generated icon mapping; fail publishing if it is accidentally
# encoded as six literal characters ('\\uE000') or missing its font provider.
font_check=json.loads(files[font_file])
assert font_check["providers"][0]["chars"][0]==chr(0xE000)
assert all(any(p.get("id")==id for p in font_check["providers"])
           for id in ("minecraft:include/space","minecraft:include/default",
                      "minecraft:include/unifont"))

with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as result_zip:
    for path, content in files.items():
        result_zip.writestr(path, content)
sha = hashlib.sha1(out.read_bytes()).hexdigest()
Path("pack-info.properties").write_text(
    "url=https://github.com/GxdionSenpai/Axoria-Resourcepack/releases/download/latest/axoria-resourcepack.zip\n"
    + "sha1=" + sha + "\n"
)
print("Published SHA-1:", sha)
