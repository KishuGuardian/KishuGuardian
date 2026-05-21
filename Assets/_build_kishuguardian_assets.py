
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import math, os, random

OUT = Path(r'C:\Users\ash2inf3rn0\Desktop\KishuGuardian')
OUT.mkdir(parents=True, exist_ok=True)

# Brand palette pulled from the KishuGuard references but redrawn as original assets.
PURPLE = (41, 17, 112, 255)
PURPLE_DARK = (26, 14, 78, 255)
PURPLE_MID = (75, 46, 178, 255)
CYAN = (0, 191, 226, 255)
CYAN_DARK = (0, 132, 176, 255)
CYAN_LIGHT = (100, 232, 245, 255)
FUR = (255, 226, 154, 255)
FUR_LIGHT = (255, 242, 195, 255)
FUR_SHADOW = (236, 192, 119, 255)
MUZZLE = (255, 250, 232, 255)
PINK = (255, 105, 135, 255)
ARMOR = (42, 55, 97, 255)
ARMOR_2 = (58, 72, 119, 255)
ARMOR_DARK = (31, 42, 80, 255)
SILVER = (218, 226, 244, 255)
SILVER_DARK = (136, 151, 184, 255)
GOLD = (250, 195, 63, 255)
WHITE = (255, 255, 255, 255)
TRANSPARENT = (0, 0, 0, 0)

S = 3
BASE = 1254

def font(size, bold=False):
    candidates = [
        r'C:\Windows\Fonts\arialbd.ttf' if bold else r'C:\Windows\Fonts\arial.ttf',
        r'C:\Windows\Fonts\bahnschrift.ttf',
        r'C:\Windows\Fonts\segoeuib.ttf' if bold else r'C:\Windows\Fonts\segoeui.ttf',
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

class Canvas:
    def __init__(self, w=BASE, h=BASE, bg=TRANSPARENT):
        self.w, self.h = w, h
        self.img = Image.new('RGBA', (w*S, h*S), bg)
        self.draw = ImageDraw.Draw(self.img)
    def sc(self, xy):
        return tuple(round(v*S) for v in xy)
    def ellipse(self, box, fill=None, outline=None, width=1):
        self.draw.ellipse(self.sc(box), fill=fill, outline=outline, width=width*S if outline else 1)
    def rounded(self, box, radius, fill=None, outline=None, width=1):
        self.draw.rounded_rectangle(self.sc(box), radius=radius*S, fill=fill, outline=outline, width=width*S if outline else 1)
    def rect(self, box, fill=None, outline=None, width=1):
        self.draw.rectangle(self.sc(box), fill=fill, outline=outline, width=width*S if outline else 1)
    def poly(self, pts, fill=None, outline=None, width=1):
        pts2 = [(round(x*S), round(y*S)) for x,y in pts]
        self.draw.polygon(pts2, fill=fill)
        if outline:
            self.draw.line(pts2 + [pts2[0]], fill=outline, width=width*S, joint='curve')
    def line(self, pts, fill, width=1, joint='curve'):
        pts2 = [(round(x*S), round(y*S)) for x,y in pts]
        self.draw.line(pts2, fill=fill, width=width*S, joint=joint)
    def arc(self, box, start, end, fill, width=1):
        self.draw.arc(self.sc(box), start=start, end=end, fill=fill, width=width*S)
    def text_center(self, xy, text, fnt, fill, stroke_width=0, stroke_fill=None):
        x,y = xy
        d = ImageDraw.Draw(self.img)
        bbox = d.textbbox((0,0), text, font=fnt, stroke_width=stroke_width*S)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        d.text((round(x*S - tw/2), round(y*S - th/2)), text, font=fnt, fill=fill, stroke_width=stroke_width*S, stroke_fill=stroke_fill)
    def paste(self, im, xy):
        self.img.alpha_composite(im, dest=self.sc(xy))
    def finish(self):
        return self.img.resize((self.w, self.h), Image.Resampling.LANCZOS)

def add_shadow(img, offset=(0, 14), blur=18, alpha=88):
    a = img.getchannel('A')
    shadow = Image.new('RGBA', img.size, (0,0,0,0))
    sh = Image.new('RGBA', img.size, (20, 8, 60, alpha))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(blur)))
    shadow.alpha_composite(sh, dest=offset)
    shadow.alpha_composite(img)
    return shadow

def draw_paw(c, cx, cy, scale=1.0):
    o = PURPLE
    fill = WHITE
    for dx, dy, rx, ry in [(-26,-25,17,21),(0,-34,18,24),(27,-25,17,21)]:
        c.ellipse((cx+(dx-rx)*scale, cy+(dy-ry)*scale, cx+(dx+rx)*scale, cy+(dy+ry)*scale), fill=fill, outline=o, width=8)
    c.ellipse((cx-34*scale, cy-2*scale, cx+34*scale, cy+54*scale), fill=fill, outline=o, width=8)
    c.ellipse((cx-20*scale, cy+12*scale, cx+20*scale, cy+46*scale), fill=PURPLE, outline=None)

def draw_shield(c, cx, cy, scale=1.0, emblem=True):
    pts = [(cx-120*scale,cy-115*scale),(cx+120*scale,cy-115*scale),(cx+135*scale,cy+10*scale),(cx+85*scale,cy+148*scale),(cx,cy+205*scale),(cx-85*scale,cy+148*scale),(cx-135*scale,cy+10*scale)]
    c.poly(pts, fill=PURPLE, outline=PURPLE_DARK, width=8)
    pts2 = [(cx-88*scale,cy-82*scale),(cx+88*scale,cy-82*scale),(cx+98*scale,cy+8*scale),(cx+58*scale,cy+118*scale),(cx,cy+158*scale),(cx-58*scale,cy+118*scale),(cx-98*scale,cy+8*scale)]
    c.poly(pts2, fill=ARMOR_2, outline=(113,126,160,255), width=5)
    c.poly([(cx,cy-76*scale),(cx+86*scale,cy-76*scale),(cx+92*scale,cy+2*scale),(cx+50*scale,cy+110*scale),(cx,cy+146*scale)], fill=(73,89,137,210))
    if emblem:
        c.rounded((cx-48*scale, cy+4*scale, cx+48*scale, cy+72*scale), 16*scale, fill=(21,32,70,220), outline=CYAN_LIGHT, width=4)
        f = font(round(40*S*scale), bold=True)
        # text_center expects a high-res font already; compensate by drawing separately on high-res canvas.
        d = ImageDraw.Draw(c.img)
        text = 'KG'
        bbox = d.textbbox((0,0), text, font=f, stroke_width=0)
        d.text((round(cx*S - (bbox[2]-bbox[0])/2), round((cy+38*scale)*S - (bbox[3]-bbox[1])/2)), text, font=f, fill=WHITE)

def draw_sword(c, x, y, angle=-38, scale=1.0):
    # Draw a stylized sword as transformed polygons.
    rad = math.radians(angle)
    def tr(px, py):
        return (x + (px*math.cos(rad)-py*math.sin(rad))*scale, y + (px*math.sin(rad)+py*math.cos(rad))*scale)
    blade = [tr(-22,-225), tr(22,-225), tr(16,44), tr(0,92), tr(-16,44)]
    c.poly(blade, fill=SILVER, outline=PURPLE, width=8)
    c.poly([tr(0,-218), tr(22,-225), tr(16,44), tr(0,92)], fill=(176,190,223,210))
    c.poly([tr(-9,-190), tr(0,-218), tr(0,72), tr(-11,38)], fill=(245,248,255,180))
    guard = [tr(-72,54), tr(72,54), tr(72,83), tr(-72,83)]
    c.poly(guard, fill=GOLD, outline=PURPLE, width=7)
    grip = [tr(-20,82), tr(20,82), tr(20,172), tr(-20,172)]
    c.poly(grip, fill=(82,91,120,255), outline=PURPLE, width=7)
    c.ellipse((*tr(-27,160), *tr(27,214)), fill=GOLD, outline=PURPLE, width=7)

def draw_kishu_head(c, cx=627, cy=395, scale=1.0, happy=True):
    # Ears
    c.poly([(cx-230*scale,cy-112*scale),(cx-360*scale,cy-322*scale),(cx-90*scale,cy-165*scale)], fill=FUR, outline=PURPLE, width=10)
    c.poly([(cx+230*scale,cy-112*scale),(cx+360*scale,cy-322*scale),(cx+90*scale,cy-165*scale)], fill=FUR, outline=PURPLE, width=10)
    c.poly([(cx-244*scale,cy-150*scale),(cx-318*scale,cy-276*scale),(cx-145*scale,cy-178*scale)], fill=PINK, outline=PURPLE, width=6)
    c.poly([(cx+244*scale,cy-150*scale),(cx+318*scale,cy-276*scale),(cx+145*scale,cy-178*scale)], fill=PINK, outline=PURPLE, width=6)
    # Head
    c.ellipse((cx-270*scale, cy-230*scale, cx+270*scale, cy+235*scale), fill=FUR, outline=PURPLE, width=10)
    c.ellipse((cx-68*scale, cy-222*scale, cx+75*scale, cy-150*scale), fill=FUR_LIGHT, outline=None)
    # Cheeks / muzzle
    c.ellipse((cx-145*scale, cy+25*scale, cx+145*scale, cy+205*scale), fill=MUZZLE, outline=None)
    # Face
    c.arc((cx-170*scale,cy-55*scale,cx-75*scale,cy+35*scale), 190, 340, fill=PURPLE, width=10)
    c.arc((cx+75*scale,cy-55*scale,cx+170*scale,cy+35*scale), 200, 350, fill=PURPLE, width=10)
    c.ellipse((cx-48*scale, cy+34*scale, cx+48*scale, cy+92*scale), fill=PURPLE_DARK, outline=PURPLE, width=4)
    c.ellipse((cx-24*scale, cy+42*scale, cx+26*scale, cy+58*scale), fill=(255,255,255,95), outline=None)
    c.line([(cx,cy+92*scale),(cx,cy+140*scale)], fill=PURPLE, width=9)
    c.arc((cx-86*scale,cy+98*scale,cx+3*scale,cy+180*scale), 20, 165, fill=PURPLE, width=9)
    c.arc((cx-3*scale,cy+98*scale,cx+86*scale,cy+180*scale), 15, 160, fill=PURPLE, width=9)
    c.paste(Image.new('RGBA', (1,1), TRANSPARENT), (0,0))
    # Open smile and tongue
    c.arc((cx-68*scale,cy+105*scale,cx+68*scale,cy+228*scale), 20, 160, fill=PURPLE, width=11)
    c.ellipse((cx-38*scale, cy+165*scale, cx+38*scale, cy+225*scale), fill=(254,91,110,255), outline=None)
    c.line([(cx-40*scale,cy+165*scale),(cx+40*scale,cy+165*scale)], fill=PURPLE, width=9)

def draw_full_body_master():
    c = Canvas(BASE, BASE)
    # Ground shadow
    c.ellipse((365,1100,900,1180), fill=(28,12,85,70), outline=None)
    # Tail behind body
    c.line([(815,840),(975,770),(990,930),(870,960)], fill=PURPLE, width=44)
    c.line([(820,840),(950,805),(950,910),(855,925)], fill=FUR, width=30)
    # Sword and shield behind arms/head
    draw_sword(c, 400, 510, angle=-38, scale=1.05)
    draw_shield(c, 880, 590, scale=1.0, emblem=True)
    # Legs and feet
    c.rounded((485,900,602,1135), 45, fill=FUR, outline=PURPLE, width=9)
    c.rounded((655,900,772,1135), 45, fill=FUR, outline=PURPLE, width=9)
    c.ellipse((430,1080,625,1190), fill=FUR, outline=PURPLE, width=9)
    c.ellipse((630,1080,825,1190), fill=FUR, outline=PURPLE, width=9)
    for x in [485,535,690,740]:
        c.arc((x,1120,x+55,1185), 220, 340, fill=PURPLE, width=5)
    # Body armor
    c.rounded((405,570,850,1015), 100, fill=ARMOR, outline=PURPLE, width=11)
    c.rounded((442,608,813,982), 66, fill=(49,61,107,255), outline=None)
    c.poly([(625,580),(790,620),(760,960),(625,1015),(490,960),(460,620)], fill=(36,48,91,210), outline=None)
    c.line([(625,612),(625,1005)], fill=CYAN_LIGHT, width=10)
    c.rounded((600,665,650,735), 18, fill=CYAN_LIGHT, outline=PURPLE, width=5)
    c.line([(450,650),(540,650)], fill=CYAN_LIGHT, width=8)
    c.line([(710,650),(800,650)], fill=CYAN_LIGHT, width=8)
    c.line([(455,965),(795,965)], fill=CYAN_LIGHT, width=10)
    # Chest badge
    c.rounded((690,705,807,785), 18, fill=(30,39,80,230), outline=GOLD, width=6)
    fkg = font(43*S, bold=True)
    d = ImageDraw.Draw(c.img)
    bbox = d.textbbox((0,0),'KG',font=fkg)
    d.text((round(748*S-(bbox[2]-bbox[0])/2), round(746*S-(bbox[3]-bbox[1])/2)), 'KG', font=fkg, fill=WHITE)
    # Arms
    c.line([(430,630),(320,745)], fill=PURPLE, width=64)
    c.line([(432,630),(330,735)], fill=FUR, width=46)
    c.ellipse((275,695,410,820), fill=FUR, outline=PURPLE, width=8)
    draw_paw(c, 342, 755, scale=0.72)
    c.line([(790,640),(925,720)], fill=PURPLE, width=70)
    c.line([(785,640),(910,715)], fill=FUR, width=50)
    c.ellipse((885,680,1008,790), fill=FUR, outline=PURPLE, width=8)
    # Shoulder armor caps
    c.ellipse((375,550,515,680), fill=ARMOR_2, outline=PURPLE, width=8)
    c.ellipse((740,550,880,680), fill=ARMOR_2, outline=PURPLE, width=8)
    # Head on top
    draw_kishu_head(c, 627, 385, scale=1.0)
    # Small guardian sparkle bits
    for x,y in [(250,205),(1018,303),(970,260),(300,890),(905,980)]:
        c.ellipse((x-7,y-7,x+7,y+7), fill=CYAN_LIGHT, outline=None)
    master = c.finish()
    return add_shadow(master, offset=(0,8), blur=14, alpha=70)

def draw_profile_master(label=True):
    c = Canvas(BASE, BASE)
    draw_shield(c, 627, 465, scale=1.75, emblem=False)
    # Profile head centered, slightly larger.
    draw_kishu_head(c, 627, 455, scale=1.12)
    if label:
        c.rounded((222, 825, 1032, 970), 34, fill=PURPLE, outline=(73, 37, 166, 255), width=6)
        f = font(106*S, bold=True)
        d = ImageDraw.Draw(c.img)
        text = 'KishuGuardian'
        bbox = d.textbbox((0,0), text, font=f)
        d.text((round(627*S-(bbox[2]-bbox[0])/2), round(897*S-(bbox[3]-bbox[1])/2)), text, font=f, fill=WHITE)
    return add_shadow(c.finish(), offset=(0,10), blur=16, alpha=72)

def draw_head_only_master():
    c = Canvas(BASE, BASE)
    draw_kishu_head(c, 627, 565, scale=1.34)
    return add_shadow(c.finish(), offset=(0,10), blur=16, alpha=72)

def bg(width, height, mode='banner'):
    im = Image.new('RGBA', (width, height), (0,0,0,0))
    pix = im.load()
    for y in range(height):
        for x in range(width):
            t = x / max(1,width-1)
            v = y / max(1,height-1)
            r = round(0*(1-t) + 0*t)
            g = round((198 - 35*v)*(1-t) + (135 - 20*v)*t)
            b = round((230 - 5*v)*(1-t) + (190 - 15*v)*t)
            pix[x,y] = (r,g,b,255)
    d = ImageDraw.Draw(im)
    # large angled panels
    d.polygon([(round(width*0.52),0),(width,0),(width,height),(round(width*0.68),height)], fill=(0,119,160,185))
    d.polygon([(0,round(height*0.68)),(round(width*0.47),round(height*0.58)),(round(width*0.66),height),(0,height)], fill=(242,253,254,224))
    # soft paw prints / circuit dots
    for i, (px,py,sc) in enumerate([(0.08,0.18,1.0),(0.88,0.20,0.9),(0.18,0.78,0.7),(0.72,0.70,0.8)]):
        cx,cy = round(width*px), round(height*py)
        fill=(255,255,255,45)
        for dx,dy,rx,ry in [(-18,-12,12,15),(0,-22,13,16),(19,-12,12,15),(0,8,22,18)]:
            d.ellipse((cx+(dx-rx)*sc,cy+(dy-ry)*sc,cx+(dx+rx)*sc,cy+(dy+ry)*sc), fill=fill)
    random.seed(17)
    for _ in range(42):
        x=random.randint(20,width-20); y=random.randint(20,height-20)
        d.ellipse((x-2,y-2,x+2,y+2), fill=(255,255,255,70))
    return im

def fit_paste(canvas, asset, box, pad=0):
    x0,y0,x1,y1 = box
    bw, bh = x1-x0-2*pad, y1-y0-2*pad
    scale = min(bw/asset.width, bh/asset.height)
    nw, nh = max(1,round(asset.width*scale)), max(1,round(asset.height*scale))
    im = asset.resize((nw,nh), Image.Resampling.LANCZOS)
    x = round(x0 + pad + (bw-nw)/2)
    y = round(y0 + pad + (bh-nh)/2)
    canvas.alpha_composite(im, (x,y))
    return canvas

def make_square_with_bg(asset, label=False, platform=None, profile=False):
    W=H=1254
    im = bg(W,H)
    if profile:
        fit_paste(im, asset, (92,80,1162,1160), pad=0)
    else:
        fit_paste(im, asset, (115,70,1139,1155), pad=0)
    d=ImageDraw.Draw(im)
    if platform == 'yt':
        d.rounded_rectangle((120,115,195,168), radius=14, fill=(255, 54, 73, 255))
        d.polygon([(148,127),(148,156),(174,142)], fill=WHITE)
    if platform == 'rd':
        d.rounded_rectangle((1055,112,1125,175), radius=18, fill=(255,255,255,238), outline=CYAN_DARK, width=3)
        d.ellipse((1075,142,1082,149), fill=CYAN_DARK)
        d.ellipse((1094,142,1101,149), fill=CYAN_DARK)
        d.ellipse((1112,142,1119,149), fill=CYAN_DARK)
    if label:
        f=font(78, bold=True)
        text='KishuGuardian'
        tb=d.textbbox((0,0), text, font=f)
        d.rounded_rectangle((W//2-(tb[2]-tb[0])//2-42,1032,W//2+(tb[2]-tb[0])//2+42,1142), radius=24, fill=PURPLE)
        d.text((W//2-(tb[2]-tb[0])//2,1062), text, font=f, fill=WHITE)
    return im

def transparent_square(asset, profile=False):
    im = Image.new('RGBA', (1254,1254), TRANSPARENT)
    box = (80,60,1174,1170) if not profile else (72,70,1182,1165)
    fit_paste(im, asset, box)
    return im

def make_banner(asset, W, H, text=True, compact=False):
    im=bg(W,H)
    d=ImageDraw.Draw(im)
    # Left communications / anti-spam icons.
    if text:
        fbig=font(round(H*0.108), bold=True)
        fsmall=font(round(H*0.065), bold=True)
        d.rounded_rectangle((round(W*0.045), round(H*0.14), round(W*0.515), round(H*0.285)), radius=28, fill=PURPLE)
        d.text((round(W*0.065), round(H*0.165)), 'KishuGuardian', font=fbig, fill=WHITE)
        d.rounded_rectangle((round(W*0.060), round(H*0.365), round(W*0.245), round(H*0.490)), radius=24, fill=(83,58,210,255), outline=PURPLE_DARK, width=6)
        d.text((round(W*0.094), round(H*0.388)), 'SPAM', font=fsmall, fill=WHITE)
        d.line((round(W*0.072), round(H*0.475), round(W*0.232), round(H*0.382)), fill=GOLD, width=9)
        d.ellipse((round(W*0.285), round(H*0.375), round(W*0.385), round(H*0.555)), fill=(73,54,201,255), outline=PURPLE_DARK, width=6)
        d.text((round(W*0.320), round(H*0.400)), '!', font=font(round(H*0.11), bold=True), fill=WHITE)
        d.rounded_rectangle((round(W*0.060), round(H*0.610), round(W*0.405), round(H*0.715)), radius=20, fill=(255,255,255,230), outline=CYAN_DARK, width=4)
        d.text((round(W*0.085), round(H*0.638)), 'Community Shield', font=font(round(H*0.050), bold=True), fill=PURPLE)
    # Right mascot.
    if compact:
        fit_paste(im, asset, (round(W*0.52), round(H*0.02), round(W*0.98), round(H*0.99)))
    else:
        fit_paste(im, asset, (round(W*0.60), round(-H*0.05), round(W*1.02), round(H*1.08)))
    return im

def checker(size, block=44):
    im=Image.new('RGBA', size, (232,237,246,255))
    d=ImageDraw.Draw(im)
    for y in range(0,size[1],block):
        for x in range(0,size[0],block):
            if ((x//block + y//block) % 2):
                d.rectangle((x,y,x+block-1,y+block-1), fill=(205,214,228,255))
    return im

def make_preview(files):
    thumb_w, thumb_h, label_h = 520, 340, 36
    cols=3; rows=math.ceil(len(files)/cols)
    sheet=Image.new('RGBA',(cols*thumb_w, rows*(thumb_h+label_h)), (18,29,51,255))
    labelfont=font(12, bold=False)
    for i,p in enumerate(files):
        im=Image.open(p).convert('RGBA')
        has_trans=im.getchannel('A').getextrema()[0] < 255
        cell=checker((thumb_w,thumb_h)) if has_trans else Image.new('RGBA',(thumb_w,thumb_h),(235,247,248,255))
        scale=min(thumb_w/im.width, thumb_h/im.height)
        nw,nh=round(im.width*scale), round(im.height*scale)
        r=im.resize((nw,nh), Image.Resampling.LANCZOS)
        cell.alpha_composite(r, ((thumb_w-nw)//2,(thumb_h-nh)//2))
        x=(i%cols)*thumb_w; y=(i//cols)*(thumb_h+label_h)
        sheet.alpha_composite(cell,(x,y))
        d=ImageDraw.Draw(sheet)
        d.rectangle((x,y+thumb_h,x+thumb_w,y+thumb_h+label_h), fill=(18,29,51,255))
        d.text((x+8,y+thumb_h+11), Path(p).name, font=labelfont, fill=(235,241,255,255))
    sheet.convert('RGB').save(OUT/'KishuGuardian x12 Preview.jpg', quality=94)
    sheet.save(OUT/'KishuGuardian x12 Preview.png')

full = draw_full_body_master()
profile = draw_profile_master(label=True)
head = draw_head_only_master()
full.save(OUT/'KishuGuardian Full Body Source.png')
profile.save(OUT/'KishuGuardian Profile Badge Source.png')
head.save(OUT/'KishuGuardian Head Only Source.png')

outputs=[]
def save(name, im):
    p=OUT/name
    im.save(p)
    outputs.append(p)

save('KishuGuardian Banner.png', make_banner(full, 2048, 1024, text=True, compact=False))
save('KishuGuardian Banner2.png', make_banner(full, 2048, 1024, text=False, compact=True))
save('KishuGuardian Big Banner.png', make_banner(full, 2048, 1152, text=True, compact=False))
save('KishuGuardian Big Banner2.png', make_banner(full, 2048, 1152, text=False, compact=True))
save('KishuGuardian Profile Pic1.png', transparent_square(full))
save('KishuGuardian Profile Pic2.png', make_square_with_bg(full, label=False))
save('KishuGuardian Profile Pic3.png', transparent_square(profile, profile=True))
save('KishuGuardian Profile Pic4.png', make_square_with_bg(profile, label=False, profile=True))
save('KishuGuardian RD.png', transparent_square(full))
save('KishuGuardian RD2.png', make_square_with_bg(full, platform='rd'))
save('KishuGuardian YT.png', transparent_square(profile, profile=True))
save('KishuGuardian YT2.png', make_square_with_bg(profile, platform='yt', profile=True))
make_preview(outputs)

print('Created KishuGuardian assets in', OUT)
for p in outputs:
    im=Image.open(p)
    print(p.name, im.size, im.mode)
print('Preview:', OUT/'KishuGuardian x12 Preview.jpg')
