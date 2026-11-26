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
# Recolour authentic vanilla 1.21.11 weapon sprites; preserve all silhouettes.
import base64
from PIL import ImageDraw
weapon_sources={"diamond_spear":"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAMFBMVEUAAAAIJSAoHguJZyceincz68vy//2k/fArx6y6XzRoTh6jSyJBGAVnKQtJNhUOPzZI1cKBAAAAAXRSTlMAQObYZgAAAEdJREFUeNqFyzkSwCAMA0CZ4CMX/v9vM6mwaFC30giUzGS6SaW6qUyGazEy/r3Xh1pUY3j0WoyrCflogAh5Zu939fmwbzZWf1aQAisoA8WXAAAAAElFTkSuQmCC","crossbow_standby":"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAKlBMVEUAAABNLhFtQhgqGgmQWB87JA21cy9IKxCXl5dtbW2WlpY2IAtEREQfEgbgySe3AAAAAXRSTlMAQObYZgAAAGhJREFUeNoFwYEBgjAQBLDct6hAb/91TQBAACDJmgC/W/aemQT8OJ/rupYD3PK5igNw9pXUDZB9JZMHwHybyZMCspfmyaRA9uLJZFKQ4dZM5gVrO2gmU2RyQN/JW6wF0DdTANBpAYDWHyfQAnPEy7OdAAAAAElFTkSuQmCC","crossbow_pulling_0":"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAKlBMVEUAAABNLhFtQhgqGgk2IAuQWB87JA21cy9IKxCXl5dERESWlpZtbW0fEgZmTV4YAAAAAXRSTlMAQObYZgAAAGlJREFUeNoFwYEBwyAMAzA5FLoC+f/dSQAgAJBkVIDvypxVlYCP/a61hg1ceVfDBuy5kuYCMldS6QtQv06lcgCZQ6dy0kDmoHNupUEK96RSDxiTS6dSjVT2hn4qT2MMgH5SDQC6ugGAbn8/aQKQl1W/vgAAAABJRU5ErkJggg==","crossbow_pulling_1":"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAKlBMVEUAAABNLhFtQhgqGgk2IAuQWB87JA21cy9IKxCXl5dERESWlpZtbW0fEgZmTV4YAAAAAXRSTlMAQObYZgAAAGpJREFUeNoFwYEBwyAMAzA5FLoC+f/dSQAgAJBkVIDvypxVlYCP/a61hg1ceVfDBuy5ksYFMldSaRdQv06l0gfIHDqVygEyB53KSYMUdM6tB4yJe04q1Uhl74t+Kk9jDIB+Ug0AuroBgG5/RVUCpiXCW8kAAAAASUVORK5CYII=","crossbow_pulling_2":"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAKlBMVEUAAABNLhFtQhgqGgmQWB87JA21cy9IKxCXl5c2IAtERESWlpZtbW0fEgYfy/EgAAAAAXRSTlMAQObYZgAAAGdJREFUeNpVylECgzAIA9AEipu0uf91py1ODV95BM/wVUi3ku8AWzMzcnUgt4hw5BoMcAsBuADZgtR8zfDsRv3BPqJNGTVwlNxQ0hcYULIW3nBJ1xwwcxzpx+2nuKOinSY8I5PwFuEHQpUCyPXLZ+cAAAAASUVORK5CYII=","crossbow_arrow":"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAOVBMVEUAAABNLhFtbW0qGgmWlpaQWB9EREQ7JA3///+1cy9IKxDY2NhFMg02IAttTxiJZydUPRJtQhgfEgbSCYY+AAAAAXRSTlMAQObYZgAAAHBJREFUeNpVzFkSBCEIA9AgLj1Lq+T+hx1H6S38wKsUuEceh4jakm0LkJTMTBw+Mb9KKYq8yiG2KhzLAci19SnB3yXprRtPsDddghcUtCkXuMQFBkypfTU0weUbOQuScxiJY/a/qMLDXYy4h0biKcQPUpcEyZ8ZLIwAAAAASUVORK5CYII=","crossbow_firework":"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAASFBMVEUAAAAfEgZtQhhtbW2WlpYiJTAvNk0XGiTWKiq5KSmEGxuZKSlcgYmyzNFtFxf09PS1cy9IKxA7JA02IAtERESQWB8qGglNLhFECIfZAAAAAXRSTlMAQObYZgAAAIBJREFUeNpVylsWgyAMRdGbKDWIaItA5j/TQqQPT76y14WIDxgpWl7WzR7Vyl3CvkWBlsLM2mFfg5fjmVKqyLBCPKIQWgOweXHaZYKlZXUPx/QFfpGaDNBSQWzyA5OF5wsY6LK45VrUgo/MZAPNeWrN7c4utWJEpzLhP2Ii3IXwBnOeBWQmvYbvAAAAAElFTkSuQmCC"}
for source_name,encoded in weapon_sources.items():
    spear=source_name=="diamond_spear"
    name="seelenspeer" if spear else "donnerarmbrust"+source_name.removeprefix("crossbow").replace("_standby","")
    original=Image.open(BytesIO(base64.b64decode(encoded))).convert("RGBA")
    def recolour(px):
        r,g,b,a=px
        if not a:return (0,0,0,0)
        light=(.2126*r+.7152*g+.0722*b)/255
        if spear:
            palette=((30,13,55),(89,35,139),(170,86,224),(245,210,255)) if g>r*1.15 or b>r*1.15 else ((9,7,15),(24,19,35),(49,39,66),(79,65,99))
        else:
            palette=((8,12,24),(25,40,64),(59,91,125),(140,191,217)) if r>g*1.15 and r>b*1.2 else ((12,38,59),(25,103,139),(72,195,225),(222,253,255))
            if source_name=="crossbow_firework" and r>g*1.7: return (r,g,b,255)
        pos=min(2.999,light*3);i=int(pos);t=pos-i
        return tuple(round(palette[i][k]*(1-t)+palette[i+1][k]*t) for k in range(3))+(255,)
    original.putdata([recolour(px) for px in original.getdata()])
    im=original.resize((128,128),Image.Resampling.NEAREST)
    if not spear:
        # Preserve the outline, string and bolt; add a central faceted crystal
        # only on the solid stock, with a dark socket and sharp cyan highlights.
        mask=im.getchannel("A")
        detail=Image.new("RGBA",(128,128),(0,0,0,0))
        d=ImageDraw.Draw(detail)
        d.polygon([(64,53),(75,64),(64,75),(53,64)],fill=(13,36,59,255))
        d.polygon([(64,56),(72,64),(64,72),(56,64)],fill=(67,208,239,255))
        d.polygon([(64,56),(64,64),(56,64)],fill=(218,255,255,255))
        d.polygon([(64,64),(72,64),(64,72)],fill=(27,117,177,255))
        from PIL import ImageChops
        detail.putalpha(ImageChops.multiply(detail.getchannel("A"),mask))
        im=Image.alpha_composite(im,detail)
    weapon_png=BytesIO();im.save(weapon_png,format="PNG")
    files["assets/axoria/textures/item/"+name+".png"]=weapon_png.getvalue()
    files["assets/axoria/models/item/"+name+".json"]=json.dumps({
        "parent":"minecraft:item/handheld" if spear else "minecraft:item/crossbow",
        "textures":{"layer0":"axoria:item/"+name}
    },separators=(",",":")).encode()
items.extend((("diamond_spear","seelenspeer",1112),("crossbow","donnerarmbrust",1113)))

items.extend(("carrot_on_a_stick","raketenwerfer_reload_"+str(i),1211+i) for i in range(3))

# Original vanilla 1.21.4 sprites with small opaque Guardian ornaments.
# Embed the small source PNGs so builds are deterministic and offline.
guardian_vanilla={"diamond_sword":"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAJFBMVEUAAAAOPzYIJSAz68uk/fArx6weincVY1VoTh5JNhUoHguJZycazUdMAAAAAXRSTlMAQObYZgAAAExJREFUGNN1jsENwDAMAgGndpLuv29/jZFa/+4QwkA/ks5jyPky8cHxwyQAxslZNAaYiux9Zlb4A0XjNcVu1r0hvYacGwB0Rq0OSC4ehwkBE0lygnsAAAAASUVORK5CYII=","bow":"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAaklEQVR42mNgoCfwNBP9j4xJ1tSZrv4/w08OjEFsDTnu/wQ1wjTBNCBjvJqzs7PBGrFpcHFxIax52rRpYBpdnnaaYQaAnE22ZlwhS1Azsu3oBhClGZcL6KMZm/NJ0oxuAMmaCcUA0YBczQDVGni1vuKfywAAAABJRU5ErkJggg==","bow_pulling_0":"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQBAMAAADt3eJSAAAAIVBMVEUAAAD////Y2NixsbGWlpZra2uJZydoTh5ERERJNhUoHgt9szO9AAAAAXRSTlMAQObYZgAAAF5JREFUeNolyaEOwjAAANFHMG2/go8iwc4QSD0hQVUiUSOdqqrYV25Z1V3unADOF8T6o1PndyZN9ZHXhn7bUbDcCYjXbsgrTQrmpgf4N+lpFAUx84X4EQwJhWMN0oANNRsW0569NXMAAAAASUVORK5CYII=","bow_pulling_1":"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQBAMAAADt3eJSAAAAIVBMVEUAAAD////Y2NixsbGWlpZra2uJZydoTh5ERERJNhUoHgt9szO9AAAAAXRSTlMAQObYZgAAAF5JREFUeNpFiiESgCAUBTcKybN4FmesFGWGbjERjSYdTKQfOKXAD76yOzuPfyNAumCqSD6AdclvJQOylEIE3hWamFlgAMxuXZc7I/3yZKyLWhBQacEEOGlyKGtRQlZ8XgEYhJSXcScAAAAASUVORK5CYII=","bow_pulling_2":"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAkklEQVR42mNgGFTgPxCgi3maif7HhTEM2Lhx4/8bN278R9bYma7+P8NPDkzDMIyvIceNaQhIECSZnZ0NVgji48JYvQGyFdkQXN51cXH5j1UzSNO0adPghpBsAMjZMJtxGYJTM7aAwWYIXtuxBQ66ISS5AJshZBmAL0yINgCrzfjCAKQBGePNB8guIEoDLj+SqgcAmHKbjbKf/yEAAAAASUVORK5CYII=","trident":"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAbUlEQVQ4y2NgoAeYNm3afxCgSPONGzfABoBoog3DpRkkTrQBZGsGgezs7P96cQH/0TUT7Q2Q5oi5fWBD0DWDDCfKAIfKTDBGdglRmsXcLcEaQTQIgzTBMNE2gzSSHO8wf480zWQHGCy6yNYMBACktqum4kbbjgAAAABJRU5ErkJggg=="}
# Sternenbogen: original bow silhouette and draw stages, with gold star arrowhead.
def star_bow_sprite(source,charged):
    im=Image.open(BytesIO(base64.b64decode(guardian_vanilla[source]))).convert("RGBA")
    colors=[]
    for r,g,b,a in im.getdata():
        if not a:
            colors.append((0,0,0,0));continue
        v=(r+g+b)/765
        if max(r,g,b)-min(r,g,b)<22:
            c=(round(145+100*v),round(108+132*v),round(45+155*v))
        else:
            c=(round(25+65*v),round(24+100*v),round(85+145*v))
        colors.append(c+(255,))
    im.putdata(colors)
    im=im.resize((32,32),Image.Resampling.NEAREST)
    from PIL import ImageDraw
    d=ImageDraw.Draw(im)
    gold=(255,205,67,255) if not charged else (255,239,150,255)
    outline=(117,68,24,255)
    def star(x,y):
        d.polygon([(x,y-3),(x+1,y-1),(x+3,y),(x+1,y+1),(x,y+3),
                   (x-1,y+1),(x-3,y),(x-1,y-1)],fill=outline)
        d.line((x-2,y,x+2,y),fill=gold)
        d.line((x,y-2,x,y+2),fill=gold)
        d.point((x,y),fill=(255,255,225,255))
    if source.startswith("bow_pulling"):
        # Vanilla loaded arrow points to the upper-left of the bow sprite.
        # Locate its grey/white tip along the upper-left diagonal.
        original=Image.open(BytesIO(base64.b64decode(guardian_vanilla[source]))).convert("RGBA")
        candidates=[(x,y) for y in range(16) for x in range(16)
                    if original.getpixel((x,y))[3] and max(original.getpixel((x,y))[:3])-min(original.getpixel((x,y))[:3])<22
                    and min(original.getpixel((x,y))[:3])>90 and abs(x-y)<=2]
        if candidates:
            x,y=min(candidates,key=lambda p:p[0]+p[1])
            star(max(3,min(28,x*2+1)),max(3,min(28,y*2+1)))
        else:
            star(5,5)
    else:
        # Small gold star on the bow grip, not a floating arrow.
        points=[(x,y) for y in range(9,23) for x in range(9,23) if im.getpixel((x,y))[3]]
        if points:
            x,y=max(points,key=lambda p:p[0]-p[1])
            star(x,y)
    im=im.resize((128,128),Image.Resampling.NEAREST)
    assert {a for *_,a in im.getdata()}=={0,255}
    out=BytesIO();im.save(out,format="PNG",optimize=True)
    return out.getvalue()

for bow_name in ("sternenbogen","sternenbogen_charged"):
    for suffix,source in [("","bow")]+[("_pulling_"+str(i),"bow_pulling_"+str(i)) for i in range(3)]:
        name=bow_name+suffix
        files["assets/axoria/textures/item/"+name+".png"]=star_bow_sprite(source,bow_name.endswith("_charged"))
        files["assets/axoria/models/item/"+name+".json"]=json.dumps({
            "parent":"minecraft:item/generated",
            "textures":{"layer0":"axoria:item/"+name}
        },separators=(",",":")).encode()

def guardian_weapon_sprite(source,elder=False):
    sprite=Image.open(BytesIO(base64.b64decode(guardian_vanilla[source]))).convert("RGBA")
    palette=((37,40,42),(77,80,79),(128,129,122),(179,178,165),(222,219,203)) if elder else (
        (21,48,49),(43,92,94),(74,143,138),(126,190,177),(207,237,218))
    colors=[]
    for r,g,b,a in sprite.getdata():
        if not a:
            colors.append((0,0,0,0))
            continue
        # Preserve the original pixel silhouette and tonal contrast.
        v=(0.2126*r+0.7152*g+0.0722*b)/255*4
        i=min(3,int(v)); t=v-i
        colors.append(tuple(round(palette[i][k]*(1-t)+palette[i+1][k]*t) for k in range(3))+(255,))
    sprite.putdata(colors)
    # Work on a 32px pixel grid: small solid coral spurs and crystal
    # inlays, rather than oversized ornaments or translucent glows.
    sprite=sprite.resize((32,32),Image.Resampling.NEAREST)
    original=sprite.copy()
    coral=(220,126,64,255) if not elder else (173,143,107,255)
    edge=(24,69,64,255) if not elder else (54,56,55,255)
    crystal=(173,235,208,255) if not elder else (208,205,188,255)
    def opaque(x,y):
        return 0<=x<32 and 0<=y<32 and original.getpixel((x,y))[3]==255
    def spur(x,y,dx,dy):
        # A two-pixel connected fin with a dark root and bright tip.
        if not opaque(x,y):return
        for step,color in ((1,edge),(2,coral)):
            xx,yy=x+dx*step,y+dy*step
            if not (0<=xx<32 and 0<=yy<32) or opaque(xx,yy):break
            sprite.putpixel((xx,yy),color)
    if source=="diamond_sword":
        # Pair of Guardian-like spines along the blade, crystal at guard.
        for y in (8,14):
            xs=[x for x in range(8,30) if opaque(x,y)]
            if xs:
                spur(min(xs),y,-1,0)
                spur(max(xs),y,1,0)
        for x,y in ((10,21),(11,20),(12,19)):
            if opaque(x,y):sprite.putpixel((x,y),crystal)
    elif source.startswith("bow"):
        # Coral fin tips on the outer limbs, never on the string or arrow.
        for y in (5,10,21,26):
            xs=[x for x in range(32) if opaque(x,y)]
            if not xs:continue
            # Bow limb is the thickest local run; avoid one-pixel string.
            runs=[]
            for x in xs:
                if runs and x==runs[-1][-1]+1:runs[-1].append(x)
                else:runs.append([x])
            limb=max(runs,key=len)
            if len(limb)>=3:
                x=limb[0] if y<16 else limb[-1]
                spur(x,y,-1 if y<16 else 1,0)
                sprite.putpixel((x,y),crystal)
    else:
        # Dark prismarine prong shoulders and a pair of shaft fins.
        for y in (8,12,18):
            xs=[x for x in range(32) if opaque(x,y)]
            if xs:
                spur(min(xs),y,-1,0)
                spur(max(xs),y,1,0)
        for y in (19,23):
            xs=[x for x in range(32) if opaque(x,y)]
            if xs:sprite.putpixel((xs[len(xs)//2],y),crystal)
    # Larger readable motifs, still on the same opaque 32px grid.
    from PIL import ImageDraw
    draw=ImageDraw.Draw(sprite)
    if source=="trident":
        # Restore original eye height and move it two grid pixels left.
        y=13
        xs=[x for x in range(32) if opaque(x,y)]
        if xs:
            x=xs[len(xs)//2]-2
            draw.polygon([(x-5,y),(x-3,y-3),(x+3,y-3),(x+5,y),
                          (x+3,y+3),(x-3,y+3)],fill=(61,58,48,255))
            draw.polygon([(x-4,y),(x-2,y-2),(x+2,y-2),(x+4,y),
                          (x+2,y+2),(x-2,y+2)],fill=(186,183,150,255))
            draw.line((x-2,y-2,x+2,y-2),fill=(229,222,184,255))
            draw.rectangle((x-1,y-1,x+1,y+1),fill=(154,95,63,255))
            draw.line((x,y-1,x,y+1),fill=(67,38,34,255))
            draw.point((x-1,y-1),fill=(245,230,196,255))
    elif source=="diamond_sword":
        # A curling crest of sea foam at the blade/guard transition.
        y=17
        xs=[x for x in range(32) if opaque(x,y)]
        if xs:
            x=xs[len(xs)//2]
            draw.polygon([(x-5,y+2),(x-5,y-1),(x-3,y-4),(x,y-5),
                          (x+2,y-3),(x+1,y-1),(x-1,y-1),(x,y+1),
                          (x+3,y+1),(x+3,y+3),(x-2,y+4)],fill=(25,79,87,255))
            draw.line([(x-4,y+1),(x-4,y-1),(x-2,y-3),(x,y-3),
                       (x-1,y-1),(x-2,y),(x,y+2),(x+2,y+2)],fill=(85,190,187,255),width=2)
            draw.line([(x-3,y-2),(x-2,y-3),(x,y-3)],fill=(213,249,233,255))
    sprite=sprite.resize((128,128),Image.Resampling.NEAREST)
    assert {a for *_,a in sprite.getdata()}=={0,255}
    output=BytesIO()
    sprite.save(output,format="PNG",optimize=True)
    return output.getvalue()

for item_name,vanilla_item,model_id in (
    ("s1_gezeitenklinge","diamond_sword",1201),
    ("s1_tiefenjaegerbogen","bow",1202),
    ("s1_elderdreizack","trident",1203)):
    variants=[(item_name,vanilla_item)]
    if vanilla_item=="bow":
        variants.extend((item_name+"_pulling_"+str(i),"bow_pulling_"+str(i)) for i in range(3))
    for name,source in variants:
        files["assets/axoria/textures/item/"+name+".png"]=guardian_weapon_sprite(source,vanilla_item=="trident")
        files["assets/axoria/models/item/"+name+".json"]=json.dumps({
            "parent":"minecraft:item/handheld" if vanilla_item=="diamond_sword" else "minecraft:item/generated",
            "textures":{"layer0":"axoria:item/"+name}
        },separators=(",",":")).encode()
    files["assets/axoria/items/"+item_name+".json"]=json.dumps({
        "model":{"type":"minecraft:model","model":"axoria:item/"+item_name}
    },separators=(",",":")).encode()
    items.append((vanilla_item,item_name,model_id))

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
    if base=="crossbow":
        def crossbow_state(prefix):
            def model(suffix):
                return {"type":"minecraft:model","model":prefix+suffix}
            return {"type":"minecraft:select","property":"minecraft:charge_type",
                "cases":[{"when":"arrow","model":model("_arrow")},{"when":"rocket","model":model("_firework")}],
                "fallback":{"type":"minecraft:condition","property":"minecraft:using_item",
                    "on_false":model(""),
                    "on_true":{"type":"minecraft:range_dispatch","property":"minecraft:crossbow/pull",
                        "fallback":model("_pulling_0"),"entries":[
                            {"threshold":0.58,"model":model("_pulling_1")},
                            {"threshold":1.0,"model":model("_pulling_2")}]}}}
        vanilla_model=crossbow_state("minecraft:item/crossbow")
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
        custom_model={"type":"minecraft:model","model":"axoria:item/"+custom}
        if custom=="donnerarmbrust":
            custom_model=crossbow_state("axoria:item/donnerarmbrust")
        if custom in ("s1_tiefenjaegerbogen","sternenbogen","sternenbogen_charged"):
            custom_model={"type":"minecraft:condition","property":"minecraft:using_item",
                "on_false":custom_model,
                "on_true":{"type":"minecraft:range_dispatch","property":"minecraft:use_duration","scale":0.05,
                    "fallback":{"type":"minecraft:model","model":"axoria:item/"+custom+"_pulling_0"},
                    "entries":[{"threshold":0.65,"model":{"type":"minecraft:model","model":"axoria:item/"+custom+"_pulling_1"}},
                               {"threshold":0.9,"model":{"type":"minecraft:model","model":"axoria:item/"+custom+"_pulling_2"}}]}}
        entries.append({"threshold":value,"model":custom_model})
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
        if Path(path).stem in set(NEW_NAMES)|{"sternenbogen_charged","skyblock_menu_book"} or Path(path).stem.startswith(("s1_gezeitenklinge","s1_tiefenjaegerbogen","s1_elderdreizack","sternenbogen","raketenwerfer_reload_","donnerarmbrust","seelenspeer")):
            image=Image.open(BytesIO(data)).convert("RGBA")
            if image.size!=(128,128) or {a for *_,a in image.getdata()}!={0,255}:
                raise ValueError("Custom Axoria 128px item texture invalid: "+path)
            continue
        try:
            files[path] = repair_enclosed_holes(data)
        except Exception as exc:
            raise RuntimeError("Invalid item PNG texture: " + path) from exc


# Clean stray dark islands outside the original silhouettes of the reported
# legacy tools. Eight-neighbor connectivity preserves diagonal pixel art.
# Never erase dark pixels attached to the main sprite, or colored particles.
def clean_legacy_black_specks(data):
    im=Image.open(BytesIO(data)).convert("RGBA")
    w,h=im.size
    px=im.load()
    remaining={(x,y) for y in range(h) for x in range(w) if px[x,y][3]}
    components=[]
    while remaining:
        seed=remaining.pop()
        component=[seed]
        queue=deque([seed])
        while queue:
            x,y=queue.popleft()
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    p=(x+dx,y+dy)
                    if p in remaining:
                        remaining.remove(p);component.append(p);queue.append(p)
        components.append(component)
    if not components:return data
    main=max(components,key=len)
    removed=0
    for component in components:
        if component is main:continue
        if len(component)>max(4,len(main)//12):continue
        # Isolated near-black artifacts, not intentional colored details.
        if all(max(px[x,y][:3])<=55 for x,y in component):
            for x,y in component:px[x,y]=(0,0,0,0)
            removed+=len(component)
    if not removed:return data
    out=BytesIO()
    im.save(out,format="PNG",optimize=True)
    print("Removed stray dark pixels:",removed)
    return out.getvalue()

for name in ("gluecks_spitzhacke","gaertnerschere","enterhaken","flammenstab",
             "blitzstab","phoenix_feder","monster_lupe","frostkugel"):
    path="assets/axoria/textures/item/"+name+".png"
    if path in files:
        files[path]=clean_legacy_black_specks(files[path])

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
    "ascent":32,"height":32,"chars":[chr(0xE000)]
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

# Emerald & Amethyst custom wearable armor. These are true vanilla-format
# 64x32 UV maps (helmet/body/arms/boots and leggings), not preview images.
# No vanilla armor assets are overwritten. Equipped Axoria pieces select
# axoria:emerald / axoria:amethyst through their Equippable component.
from PIL import ImageDraw

# The ORIGINAL Mojang diamond armor UV and 16x16 icons are kept in
# diamond-vanilla/. Recoloring their real pixels (instead of redrawing UV
# rectangles) preserves the exact diamond armor shape, edges and shading.
# Emerald and Amethyst use block-inspired patterns, preserving the original UV.
def recolor_diamond(source,kind,output_size):
    image=Image.open(source).convert("RGBA")
    if kind in ("emerald","amethyst"):
        emerald=kind=="emerald"
        palette=((8,77,32),(13,122,48),(19,161,64),(43,199,99),(108,232,154)) if emerald else (
            (49,28,86),(77,48,125),(107,70,163),(145,103,196),(200,157,222))
        # Emerald block: inset concentric square facets; amethyst block:
        # irregular crystal patches and bright glints, at native pixel scale.
        crystal=((1,1,2,3,2,0,1,2),(2,3,3,2,1,1,2,3),
                 (3,4,2,1,0,2,3,2),(2,2,1,0,1,3,4,2),
                 (1,0,2,3,3,2,1,1),(2,1,3,4,2,1,0,2),
                 (3,2,2,1,1,2,3,3),(2,1,0,2,3,4,2,1))
        lum=[0.2126*r+0.7152*g+0.0722*b for r,g,b,a in image.getdata() if a]
        low,high=min(lum),max(lum)
        for y in range(image.height):
            for x in range(image.width):
                r,g,b,a=image.getpixel((x,y))
                if not a:continue
                v=(0.2126*r+0.7152*g+0.0722*b-low)/max(1,high-low)
                if emerald:
                    xx,yy=x%8,y%8
                    ring=min(xx,yy,7-xx,7-yy)
                    idx=4 if ring in (1,3) and (xx==ring or yy==ring) else 0 if ring in (1,3) else 2 if ring==0 else 3
                else:
                    idx=crystal[y%8][x%8]
                shade=0.72+0.40*v
                image.putpixel((x,y),tuple(min(255,round(ch*shade)) for ch in palette[idx])+(a,))
        return image.resize(output_size,Image.Resampling.NEAREST)
    if kind in ("s1_guardian","s1_elder_guardian"):
        # Repeating block-style pixel mosaic, masked by original diamond UV.
        # Dark prismarine has staggered rectangular tiles; normal prismarine
        # has irregular mottled square fragments. Keep diamond facet shading.
        dark=kind=="s1_elder_guardian"
        palette=((24,53,45),(33,72,59),(43,92,75),(53,110,87)) if dark else (
            (58,107,109),(75,129,132),(91,149,148),(120,172,165),(144,190,179))
        lum=[0.2126*r+0.7152*g+0.0722*b for r,g,b,a in image.getdata() if a]
        low,high=min(lum),max(lum)
        for y in range(image.height):
            for x in range(image.width):
                r,g,b,a=image.getpixel((x,y))
                if not a:continue
                v=(0.2126*r+0.7152*g+0.0722*b-low)/max(1,high-low)
                if dark:
                    row=y//2
                    xx=(x+(row%2)*2)%4
                    idx=0 if y%2==1 or xx==3 else 1+((x//4+row*3+xx)%3)
                else:
                    # Compact irregular patches with a deterministic pixel pattern.
                    pattern=((1,1,3,3,2,0,0,2),(1,3,4,2,2,0,1,1),
                             (2,2,3,1,0,1,3,3),(3,2,1,1,0,2,4,3),
                             (0,1,1,3,3,2,2,1),(0,0,2,4,3,1,0,1),
                             (2,3,3,2,1,1,2,4),(2,4,2,0,0,3,3,2))
                    idx=pattern[y%8][x%8]
                shade=0.62+0.52*v
                image.putpixel((x,y),tuple(min(255,round(c*shade)) for c in palette[idx])+(a,))
        return image.resize(output_size,Image.Resampling.NEAREST)
    if kind=="beta":
        gradient=((54,20,5),(112,44,6),(190,85,15),
                  (241,139,28),(255,209,85))
    elif kind=="emerald":
        gradient=((6,32,21),(12,80,43),(21,147,75),
                  (45,205,111),(125,255,181))
    elif kind=="s1_guardian":
        gradient=((29,65,65),(53,106,103),(79,145,134),
                  (116,179,165),(169,218,196))
    elif kind=="s1_elder_guardian":
        gradient=((9,27,24),(20,52,44),(34,82,67),
                  (54,113,94),(86,151,123))
    else:
        gradient=((27,11,53),(59,26,102),(111,52,174),
                  (172,104,231),(228,183,255))
    lum=[(0.2126*r+0.7152*g+0.0722*b)
         for (r,g,b,a) in image.getdata() if a>0]
    low=min(lum); high=max(lum)
    if high<=low:raise ValueError("Invalid vanilla diamond texture: "+str(source))
    def pixel(color):
        r,g,b,alpha=color
        if alpha==0:return (0,0,0,0)
        luma=0.2126*r+0.7152*g+0.0722*b
        normalized=max(0.0,min(1.0,(luma-low)/(high-low)))
        # Fixed four-stop gradient: keep Minecraft's precise diamond facet
        # shading and dark border pixels; only change the color palette.
        pos=normalized*4
        low_index=min(3,int(pos))
        t=pos-low_index
        c0=gradient[low_index];c1=gradient[low_index+1]
        return tuple(round(c0[k]*(1-t)+c1[k]*t) for k in range(3))+(alpha,)
    image.putdata([pixel(p) for p in image.getdata()])
    return image.resize(output_size,Image.Resampling.NEAREST)

def make_axoria_armor_layer(kind,leggings=False):
    source=Path("diamond-vanilla")/("humanoid_leggings.png" if leggings else "humanoid.png")
    image=recolor_diamond(source,kind,(256,128))
    if image.size!=(256,128):raise ValueError("Worn armor UV must remain 2:1")
    return image

for armor_id in ("emerald","amethyst","beta","s1_guardian","s1_elder_guardian"):
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
    # Exact diamond helmet/chest/legs/boots inventory silhouette in 128x128.
    if piece not in ("helmet","chestplate","leggings","boots"):
        raise ValueError("Unknown armor part "+piece)
    return recolor_diamond(Path("diamond-vanilla")/(piece+".png"),
                           theme,(128,128))

# These four ids are per-ITEM, not per leather material. In Minecraft
# 26.3 item_model (assets/axoria/items/*.json) is authoritative and keeps
# all 8 inventory icons isolated from other leather armor or packs.
# Do NOT override assets/minecraft/items/leather_*.json: that previously
# produced misleading common icons and damaged vanilla fallbacks.
armor_parts=("helmet","chestplate","leggings","boots")
for gear_name in ("emerald","amethyst","beta","s1_guardian","s1_elder_guardian"):
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

# Optional-icon fallback: items keep their normal minecraft:leather_* item
# model, with a numeric CMD only. If Axoria is installed, the range dispatch
# selects the 128px recolored diamond sprite; without the pack Minecraft
# renders the original dyeable leather icon instead of a black/pink cube.
for part_index,part in enumerate(armor_parts):
    vanilla="leather_"+part
    path="assets/minecraft/items/"+vanilla+".json"
    if path in files:
        existing=json.loads(files[path].decode("utf-8"))["model"]
    else:
        # Vanilla leather armor has dye tint default and uses vanilla model.
        existing={"type":"minecraft:model","model":"minecraft:item/"+vanilla,
                  "tints":[{"type":"minecraft:dye","default":[160,101,64]}]}
    choices=[]
    for theme,number in (("emerald",1301+part_index),("amethyst",1311+part_index),
                         ("s1_guardian",1321+part_index),("s1_elder_guardian",1331+part_index)):
        model={"type":"minecraft:model","model":"axoria:item/"+theme+"_"+part}
        choices.extend([
            {"threshold":number,"model":model},
            {"threshold":number+0.5,"model":existing}
        ])
    files[path]=json.dumps({"model":{
        "type":"minecraft:range_dispatch",
        "property":"minecraft:custom_model_data","index":0,
        "fallback":existing,
        "entries":sorted(choices,key=lambda x:x["threshold"])
    }},separators=(",",":")).encode("utf-8")

# Fail pack release instead of silently shipping blank, corrupt or shared
# armor art. Both equipped variants have two independent 256x128 atlases,
# and eight exact 128x128 individual inventory textures.
for gear_name in ("emerald","amethyst","beta","s1_guardian","s1_elder_guardian"):
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

# BETA inventory icons use golden-* vanilla fallback; never replace diamond or leather.
# Reuse the original diamond silhouettes, recolored orange at 128x128.
for idx,part in enumerate(armor_parts):
    fallback="golden_"+part
    name="beta_"+part
    default={"type":"minecraft:model","model":"minecraft:item/"+fallback}
    item_path="assets/minecraft/items/"+fallback+".json"
    if item_path in files:
        default=json.loads(files[item_path].decode("utf-8"))["model"]
    custom={"type":"minecraft:model","model":"axoria:item/"+name}
    files[item_path]=json.dumps({"model":{"type":"minecraft:range_dispatch",
        "property":"minecraft:custom_model_data","index":0,
        "fallback":default,"entries":[
            {"threshold":1401+idx,"model":custom},
            {"threshold":1401.5+idx,"model":default}
        ]}},separators=(",",":")).encode("utf-8")

# Recolour authentic vanilla gold sprites; never redraw their silhouettes.
# The in-repository source files reproduce Minecraft's original 16x16 pixel
# layout. Recolour only the gold facets and preserve the dark wood tool handles.
import base64 as beta_base64
beta_vanilla=json.loads(Path("beta-vanilla-sprites.json").read_text())
def beta_sprite(kind):
    # Recolour the ORIGINAL vanilla upgrade template; preserve its shape.
    vanilla=("gold_ingot" if kind=="ingot" else
             "netherite_upgrade_smithing_template" if kind=="template"
             else "golden_"+kind)
    with Image.open(BytesIO(beta_base64.b64decode(beta_vanilla[vanilla]))) as source_image:
        im=source_image.convert("RGBA")
    if im.size!=(16,16):
        raise ValueError("Invalid vanilla gold source sprite: "+vanilla)
    def tint(pixel):
        r,g,b,a=pixel
        if a==0:return (0,0,0,0)
        # Preserve the exact Mojang shading, transparent shape and tool handle.
        # Only the GOLD parts get a warmer, richer orange Beta palette.
        if kind=="template":
            # Gold-orange mapping of the original vanilla texture palette.
            luma=0.2126*r+0.7152*g+0.0722*b
            if luma < 40:return (58,23,10,a)
            if luma < 85:return (120,51,12,a)
            if luma < 140:return (203,99,22,a)
            return (255,185,67,a)
        if r>=145 and g>=93 and r>g*1.12:
            strength=0.76 if kind=="ingot" else 0.67
            return (min(255,int(r*1.05)),int(g*strength),int(b*0.87),a)
        return pixel
    im.putdata([tint(px) for px in im.getdata()])
    return im.resize((128,128),Image.Resampling.NEAREST)
beta_base={
    "gold_ingot":("ingot",1460),
    "netherite_upgrade_smithing_template":("template",1461),
    "golden_pickaxe":("pickaxe",1405),
    "golden_axe":("axe",1406),
    "golden_shovel":("shovel",1407),
    "golden_hoe":("hoe",1408),
    "golden_sword":("sword",1409)
}
for vanilla,(kind,cmd) in beta_base.items():
    sprite=beta_sprite(kind)
    bio=BytesIO();sprite.save(bio,format="PNG",optimize=True)
    name="beta_"+kind
    files["assets/axoria/textures/item/"+name+".png"]=bio.getvalue()
    files["assets/axoria/models/item/"+name+".json"]=json.dumps({
        "parent":"minecraft:item/generated" if kind in ("ingot","template") else "minecraft:item/handheld",
        "textures":{"layer0":"axoria:item/"+name}
    },separators=(",",":")).encode()
    path="assets/minecraft/items/"+vanilla+".json"
    fallback=json.loads(files[path].decode())["model"] if path in files else {
        "type":"minecraft:model","model":"minecraft:item/"+vanilla}
    model={"type":"minecraft:model","model":"axoria:item/"+name}
    files[path]=json.dumps({"model":{"type":"minecraft:range_dispatch",
        "property":"minecraft:custom_model_data","index":0,
        "fallback":fallback,"entries":[
            {"threshold":cmd,"model":model},
            {"threshold":cmd+0.5,"model":fallback}
        ]}},separators=(",",":")).encode()
# Fail publication if any BETA armor sprite/layer is blank or wrongly sized.
for part in armor_parts:
    assert Image.open(BytesIO(files["assets/axoria/textures/item/beta_"+part+".png"])).size==(128,128)
for name in ("humanoid","humanoid_leggings"):
    assert Image.open(BytesIO(files["assets/axoria/textures/entity/equipment/"+name+"/beta.png"])).size==(256,128)

# Validate the generated icon mapping; fail publishing if it is accidentally
# encoded as six literal characters ('\\uE000') or missing its font provider.
font_check=json.loads(files[font_file])
assert font_check["providers"][0]["chars"][0]==chr(0xE000)
assert all(any(p.get("id")==id for p in font_check["providers"])
           for id in ("minecraft:include/space","minecraft:include/default",
                      "minecraft:include/unifont"))

# Exclusive Axoria treasure chest: sculpted gold frame and axolotl mascot.
from PIL import ImageDraw
im=Image.new("RGBA",(64,64))
d=ImageDraw.Draw(im)
# Sixteen 16x16 atlas tiles; deliberate broad pixel clusters instead of noise.
palettes=[
    ("#48251c","#693923","#895032","#a4673c"),
    ("#805019","#bd812b","#e8b64c","#ffe09a"),
    ("#492e3b","#674455","#876375","#ae8795"),
    ("#491a76","#7930ad","#b95ae6","#f0a7ff"),
    ("#656970","#a3a8af","#d0d5db","#f2f4f7"),
    ("#454a53","#777e88","#b0b7c0","#dde2e8"),
    ("#24182e","#38243f","#593b5e","#80516e"),
    ("#fff0d6","#fff0d6","#fff0d6","#fff0d6"),
    ("#39201a","#512d23","#70402b","#885238"),
    ("#86551b","#bc842e","#e3ab43","#f9d576"),
    ("#31154c","#6a2695","#ab45d2","#e9a1ff"),
    ("#81868e","#bbc1c8","#e2e6eb","#fafbfd"),
]
for i,pal in enumerate(palettes):
    ox,oy=(i%4)*16,(i//4)*16
    d.rectangle((ox,oy,ox+15,oy+15),fill=pal[1])
    d.rectangle((ox,oy,ox+15,oy+1),fill=pal[3])
    d.rectangle((ox,oy+14,ox+15,oy+15),fill=pal[0])
    d.rectangle((ox,oy+2,ox+1,oy+13),fill=pal[2])
    d.rectangle((ox+14,oy+2,ox+15,oy+13),fill=pal[0])
    if i in (0,8):
        for y in (5,10):
            d.line((ox,oy+y,ox+15,oy+y),fill=pal[0])
            d.line((ox+2,oy+y+1,ox+10,oy+y+1),fill=pal[2])
    elif i in (3,10):
        d.polygon([(ox+2,oy+5),(ox+8,oy+2),(ox+13,oy+5),(ox+8,oy+9)],fill=pal[3])
        d.polygon([(ox+2,oy+5),(ox+8,oy+9),(ox+8,oy+14),(ox+3,oy+10)],fill=pal[2])
        d.polygon([(ox+13,oy+5),(ox+8,oy+9),(ox+8,oy+14),(ox+13,oy+10)],fill=pal[0])
bio=BytesIO();im.save(bio,format="PNG")
files["assets/axoria/textures/block/treasure_chest.png"]=bio.getvalue()
elements=[]
def treasure_box(lo,hi,tile,top=None,side=None):
    def uv(i):
        x,y=(i%4)*4,(i//4)*4
        return [x,y,x+4,y+4]
    elements.append({"from":lo,"to":hi,"faces":{f:{"uv":uv(top if f=="up" and top is not None else side if f in ("east","west") and side is not None else tile),"texture":"#chest"} for f in ("north","south","east","west","up","down")}})
# Broad, low chest with a stepped lid and thick golden corner armour.
treasure_box([1,1,2],[15,8,14],0,8,8)
treasure_box([1,8.3,2],[15,11.5,14],0,0,8)
treasure_box([2,11.5,2],[14,13,14],0)
treasure_box([3,13,2],[13,14,14],0)
treasure_box([0.5,0,1.5],[15.5,1.5,14.5],1)
treasure_box([0.5,7.2,1.5],[15.5,8,14.5],9)
for x in (0.5,12.5):
    treasure_box([x,1.5,1.3],[x+3,7.2,14.7],1,9)
    treasure_box([x,8.3,1.3],[x+3,11.5,14.7],1)
for x in (1.5,12):
    treasure_box([x,11.5,1.8],[x+2.5,13,14.2],1)
for x in (3,11):
    treasure_box([x,13,2],[x+2,14.3,14],9)
# Four inset purple crystal mounts, raised facets and gold rims.
for x in (2.3,10.7):
    treasure_box([x,11.6,1],[x+3,14,3.8],1)
    treasure_box([x+.4,12,0.6],[x+2.6,13.8,1.2],3)
    treasure_box([x+.4,14,1.4],[x+2.6,14.7,3.4],10)
    treasure_box([x,2,0.9],[x+3,5,2],1)
    treasure_box([x+.4,2.4,0.3],[x+2.6,4.6,1],3)
# Golden escutcheon behind the pink axolotl face.
treasure_box([4.3,4.3,0.6],[11.7,11.3,2],1)
treasure_box([5,3.7,0.6],[11,4.5,2],9)
# Three stepped gills per side, deliberately chunky Minecraft geometry.
for x,sign in ((5,-1),(11,1)):
    for y,length in ((10,2),(8.5,2.6),(7,1.8)):
        lo=x-length if sign<0 else x
        hi=x if sign<0 else x+length
        treasure_box([lo,y,0.1],[hi,y+1.1,1.4],5,4)
        tip=lo if sign<0 else hi-.6
        treasure_box([tip,y+.6,-.1],[tip+.6,y+1.3,1.2],4)
treasure_box([5,5.7,-.25],[11,10.8,1.3],4,11)
treasure_box([5.6,5.2,-.3],[10.4,6.1,1.3],4)
# Dark eyes with tiny ivory reflections, smiling mouth and pink cheeks.
for x in (6,9):
    treasure_box([x,8.2,-.55],[x+1,9.4,-.24],6)
    treasure_box([x+.15,8.85,-.65],[x+.5,9.2,-.54],7)
for x in (5.5,10):
    treasure_box([x,7.2,-.48],[x+.5,7.8,-.24],5)
treasure_box([7,6.8,-.55],[9,7.15,-.24],6)
treasure_box([6.7,7.1,-.55],[7,7.5,-.24],6)
treasure_box([9,7.1,-.55],[9.3,7.5,-.24],6)
# Small lock below the mascot, not a skull.
treasure_box([7,3.1,-.1],[9,5.1,.7],1)
treasure_box([7.7,3.7,-.25],[8.3,4.5,-.1],6)
# Decorative chain links on the lower front, kept within the hitbox.
for x,y in ((3,5.7),(4.3,5.1),(5.6,4.5),(9.4,4.5),(10.7,5.1),(12,5.7)):
    treasure_box([x,y,0.1],[x+1.3,y+.45,.75],9)
    treasure_box([x,y+.9,0.1],[x+1.3,y+1.35,.75],1)
    treasure_box([x,y+.4,0.1],[x+.35,y+1,.75],1)
    treasure_box([x+.95,y+.4,0.1],[x+1.3,y+1,.75],9)
# Prevent z-fighting on overlapping coplanar decorative surfaces.
# Move only the later face outward by a tiny amount; keep all UVs and the silhouette.
def separate_treasure_faces(boxes):
    for index,box in enumerate(boxes):
        for axis in range(3):
            for bound,opposite,direction in (("from","to",-1),("to","from",1)):
                original=box[bound][axis]
                other_axes=[a for a in range(3) if a!=axis]
                # Coplanar touching faces of opposite orientation are internal;
                # only same-facing overlapping surfaces compete for depth.
                while any(abs(previous[bound][axis]-box[bound][axis])<0.002
                          and all(min(previous["to"][a],box["to"][a]) >
                                  max(previous["from"][a],box["from"][a])+0.0001 for a in other_axes)
                          for previous in boxes[:index]):
                    box[bound][axis]=round(box[bound][axis]+direction*0.025,4)
                assert abs(box[bound][axis]-original)<0.25, "Excessive treasure face offset"
    return boxes
elements=separate_treasure_faces(elements)
files["assets/axoria/models/item/treasure_chest.json"]=json.dumps({"textures":{"chest":"axoria:block/treasure_chest","particle":"axoria:block/treasure_chest"},"elements":elements}).encode()
files["assets/axoria/items/treasure_chest.json"]=json.dumps({"model":{"type":"minecraft:model","model":"axoria:item/treasure_chest"}}).encode()

# Optional recorded Elder Guardian introduction.
# GxdionSenpai story voice lines: optional until each recording is supplied.
# Keep existing Elder Guardian voices and all other sound definitions.
for quest_number in range(1, 25):
    voice_name = f"gxdion_quest_{quest_number:02d}"
    voice_file = Path(__file__).resolve().parent / "audio" / f"{voice_name}.ogg"
    if not voice_file.is_file():
        continue
    import subprocess
    import tempfile
    # Convert to verified mono Vorbis and use the same vanilla namespace
    # compatibility path as the existing Elder Guardian soundtrack.
    with tempfile.TemporaryDirectory() as temp:
        output = Path(temp) / (voice_name + ".ogg")
        subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
                        "-y", "-i", str(voice_file), "-map", "0:a:0", "-vn",
                        "-c:a", "libvorbis", "-q:a", "5", "-ar", "44100",
                        "-ac", "1", str(output)], check=True)
        raw = output.read_bytes()
    if not raw.startswith(b"OggS") or b"\x01vorbis" not in raw[:65536]:
        raise RuntimeError("Invalid Guardian voice: " + voice_name)
    files[f"assets/axoria/sounds/guardian/{voice_name}.ogg"] = raw
    files[f"assets/minecraft/sounds/axoria/guardian/{voice_name}.ogg"] = raw
    sound_definitions = json.loads(files.get("assets/axoria/sounds.json", b"{}"))
    sound_definitions[f"guardian.{voice_name}"] = {"sounds": [{"name": f"axoria:guardian/{voice_name}", "stream": True, "attenuation_distance": 64}]}
    files["assets/axoria/sounds.json"] = json.dumps(sound_definitions).encode()
    vanilla_definitions = json.loads(files.get("assets/minecraft/sounds.json", b"{}"))
    vanilla_definitions[f"axoria.guardian.{voice_name}"] = {"sounds": [{"name": f"minecraft:axoria/guardian/{voice_name}", "stream": True, "attenuation_distance": 64}]}
    files["assets/minecraft/sounds.json"] = json.dumps(vanilla_definitions).encode()
    print("Verified Guardian quest voice:", voice_name, len(raw), "bytes")

elder_intro = Path(__file__).resolve().parent / "audio" / "elder_intro.ogg"
if elder_intro.is_file():
    files["assets/axoria/sounds/guardian/elder_intro.ogg"] = elder_intro.read_bytes()
    sound_definitions = json.loads(files.get("assets/axoria/sounds.json", b"{}"))
    sound_definitions["guardian.elder_intro"] = {"sounds": [{"name": "axoria:guardian/elder_intro", "stream": True, "attenuation_distance": 64}]}
    files["assets/axoria/sounds.json"] = json.dumps(sound_definitions).encode()
else:
    print("WARNING: audio/elder_intro.ogg missing; Elder voice not included")

# Recorded Elder Guardian final dialogue.
elder_death = Path(__file__).resolve().parent / "audio" / "elder_death.ogg"
if elder_death.is_file():
    files["assets/axoria/sounds/guardian/elder_death.ogg"] = elder_death.read_bytes()
    sound_definitions = json.loads(files.get("assets/axoria/sounds.json", b"{}"))
    sound_definitions["guardian.elder_death"] = {"sounds": [{"name": "axoria:guardian/elder_death", "stream": True, "attenuation_distance": 64}]}
    files["assets/axoria/sounds.json"] = json.dumps(sound_definitions).encode()
else:
    print("WARNING: audio/elder_death.ogg missing; Elder final voice not included")

# Elder Guardian combat playlist, streamed to avoid decoding the full tracks into memory.
for track in ("elder_battle_1", "elder_battle_2"):
    source = Path(__file__).resolve().parent / "audio" / (track + ".ogg")
    if source.is_file():
        files["assets/axoria/sounds/guardian/" + track + ".ogg"] = source.read_bytes()
        sound_definitions = json.loads(files.get("assets/axoria/sounds.json", b"{}"))
        sound_definitions["guardian." + track] = {"sounds": [{"name": "axoria:guardian/" + track, "stream": True}]}
        files["assets/axoria/sounds.json"] = json.dumps(sound_definitions).encode()
    else:
        print("WARNING: missing combat track " + str(source))

# Validate the published audio and make the music available under the default
# namespace as well, for clients with custom namespace sound lookup problems.
for track in ("elder_battle_1", "elder_battle_2"):
    asset = "assets/axoria/sounds/guardian/" + track + ".ogg"
    if asset not in files:
        raise RuntimeError("Missing boss soundtrack: " + asset)
    # Normalize uploaded audio regardless of its file extension or source codec.
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as temp:
        output = Path(temp) / (track + ".ogg")
        source = Path(__file__).resolve().parent / "audio" / (track + ".ogg")
        subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
                        "-y", "-i", str(source), "-map", "0:a:0", "-vn",
                        "-c:a", "libvorbis", "-q:a", "5", "-ar", "44100",
                        "-ac", "2", str(output)], check=True)
        raw = output.read_bytes()
    if not raw.startswith(b"OggS") or b"\x01vorbis" not in raw[:65536]:
        raise RuntimeError("Conversion failed: " + track)
    files[asset] = raw
    print("Verified boss soundtrack:", track, len(raw), "bytes")
    definitions = json.loads(files.get("assets/minecraft/sounds.json", b"{}"))
    definitions["axoria.guardian." + track] = {"sounds": [{"name": "axoria:guardian/" + track, "stream": True, "attenuation_distance": 256}]}
    files["assets/minecraft/sounds.json"] = json.dumps(definitions).encode()
# Vanilla cannot adjust the volume of a sound instance after it starts.
# Pre-render a quiet intro that rises into the first track, and short
# position-matched fade-out excerpts for the Elder's final dialogue.
import subprocess
import tempfile
import math
music_durations = (263.267846, 347.533061)
music_definitions = json.loads(files.get("assets/minecraft/sounds.json", b"{}"))

def guardian_music_clip(source, target, start, length, filters=None, quality=4, loop=False):
    with tempfile.TemporaryDirectory() as temp:
        output = Path(temp) / (target + ".ogg")
        cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y"]
        if loop:
            cmd += ["-stream_loop", "-1"]
        if start:
            cmd += ["-ss", str(start)]
        cmd += ["-i", str(source), "-map", "0:a:0", "-vn"]
        if length is not None:
            cmd += ["-t", str(length)]
        if filters:
            cmd += ["-af", filters]
        cmd += ["-c:a", "libvorbis", "-q:a", str(quality), "-ar", "44100", "-ac", "2", str(output)]
        subprocess.run(cmd, check=True)
        raw = output.read_bytes()
    if not raw.startswith(b"OggS") or b"\x01vorbis" not in raw[:65536]:
        raise RuntimeError("Invalid cinematic music segment: " + target)
    files["assets/axoria/sounds/guardian/" + target + ".ogg"] = raw
    music_definitions["axoria.guardian." + target] = {
        "sounds": [{"name": "axoria:guardian/" + target, "stream": True, "attenuation_distance": 256}]
    }

with tempfile.TemporaryDirectory() as temp:
    for index, duration in enumerate(music_durations, 1):
        track = "elder_battle_" + str(index)
        source = Path(temp) / (track + ".ogg")
        source.write_bytes(files["assets/axoria/sounds/guardian/" + track + ".ogg"])
        if index == 1:
            guardian_music_clip(source, track + "_intro", 0, 15,
                "volume='if(lt(t,13.17),0.18,min(1,0.18+0.82*(t-13.17)/1.83))':eval=frame,afade=t=in:st=0:d=0.3",
                quality=5)
            guardian_music_clip(source, track + "_continue", 15, None, quality=5)
        # Quiet, 14-second endings selected from the nearest 8-second song position.
        # Loop across the source's end if necessary so music reaches the return TP.
        for offset in range(0, int(duration) + 1, 8):
            guardian_music_clip(source, track + "_outro_" + str(offset), offset, 14,
                "volume='if(lt(t,0.65),1-0.82*t/0.65,0.18)':eval=frame,afade=t=out:st=12:d=2",
                quality=3, loop=True)
files["assets/minecraft/sounds.json"] = json.dumps(music_definitions).encode()
print("Generated cinematic music intro, continuation and position-matched endings.")
with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as result_zip:
    for path, content in files.items():
        result_zip.writestr(path, content)
sha = hashlib.sha1(out.read_bytes()).hexdigest()
Path("pack-info.properties").write_text(
    "url=https://raw.githubusercontent.com/GxdionSenpai/Axoria-Resourcepack/main/axoria-resourcepack.zip\n"
    + "sha1=" + sha + "\n"
)
print("Published SHA-1:", sha)
