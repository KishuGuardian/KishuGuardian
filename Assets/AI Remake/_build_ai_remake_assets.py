
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from pathlib import Path
from collections import deque
import os, math, random

ROOT = Path(r'C:\Users\ash2inf3rn0\Desktop\KishuGuardian')
SRC = ROOT / 'Generated Masters'
OUT = ROOT / 'AI Remake'
OUT.mkdir(parents=True, exist_ok=True)

FULL_IN = SRC / 'KishuGuardian Generated Full Body.png'
PROFILE_IN = SRC / 'KishuGuardian Generated Profile.png'
PURPLE = (35, 18, 96, 255)
PURPLE_DARK = (18, 10, 56, 255)
CYAN = (0, 190, 226, 255)
CYAN_DARK = (0, 125, 166, 255)
CYAN_LIGHT = (101, 235, 245, 255)
WHITE = (255,255,255,255)
NAVY = (25, 34, 67, 255)
GOLD = (248, 188, 52, 255)
TRANSPARENT = (0,0,0,0)


def font(size, bold=False):
    candidates = [
        r'C:\Windows\Fonts\arialbd.ttf' if bold else r'C:\Windows\Fonts\arial.ttf',
        r'C:\Windows\Fonts\segoeuib.ttf' if bold else r'C:\Windows\Fonts\segoeui.ttf',
        r'C:\Windows\Fonts\bahnschrift.ttf',
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def flood_remove_background(im, mode='white'):
    im = im.convert('RGBA')
    w,h = im.size
    pix = im.load()
    visited = bytearray(w*h)
    q = deque()
    for x in range(w):
        q.append((x,0)); q.append((x,h-1))
    for y in range(h):
        q.append((0,y)); q.append((w-1,y))
    def is_bg(r,g,b,a):
        if a < 10:
            return True
        if mode == 'white':
            return r > 218 and g > 218 and b > 214
        # dark teal/blue gradient edges around profile badge
        mx, mn = max(r,g,b), min(r,g,b)
        return (b > 45 and g > 35 and r < 85 and b >= r + 28 and g >= r + 12) or (r < 35 and g < 45 and b < 75)
    while q:
        x,y = q.popleft()
        if x < 0 or y < 0 or x >= w or y >= h: continue
        i = y*w+x
        if visited[i]: continue
        r,g,b,a = pix[x,y]
        if not is_bg(r,g,b,a): continue
        visited[i] = 1
        q.append((x+1,y)); q.append((x-1,y)); q.append((x,y+1)); q.append((x,y-1))
    alpha = im.getchannel('A')
    ad = alpha.load()
    for y in range(h):
        for x in range(w):
            if visited[y*w+x]:
                ad[x,y] = 0
            elif mode == 'white':
                r,g,b,a = pix[x,y]
                # soften near-white halos from the source image background
                if r > 230 and g > 230 and b > 225:
                    ad[x,y] = min(ad[x,y], 120)
    # Feather and trim tiny residue.
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.7))
    im.putalpha(alpha)
    return im


def crop_alpha(im, pad=24):
    bbox = im.getchannel('A').getbbox()
    if not bbox:
        return im
    x0,y0,x1,y1 = bbox
    x0=max(0,x0-pad); y0=max(0,y0-pad); x1=min(im.width,x1+pad); y1=min(im.height,y1+pad)
    return im.crop((x0,y0,x1,y1))


def add_shadow(asset, blur=18, offset=(0,14), alpha=85):
    a = asset.getchannel('A')
    sh = Image.new('RGBA', asset.size, (20, 8, 62, alpha))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(blur)))
    out = Image.new('RGBA', asset.size, TRANSPARENT)
    out.alpha_composite(sh, offset)
    out.alpha_composite(asset)
    return out


def bg(w,h):
    im = Image.new('RGBA', (w,h), WHITE)
    pix = im.load()
    for y in range(h):
        for x in range(w):
            t=x/max(1,w-1); v=y/max(1,h-1)
            r=round(0 + 14*v)
            g=round((198-28*v)*(1-t)+(128-18*v)*t)
            b=round((230-8*v)*(1-t)+(178-18*v)*t)
            pix[x,y]=(r,g,b,255)
    d=ImageDraw.Draw(im)
    d.polygon([(round(w*.52),0),(w,0),(w,h),(round(w*.69),h)], fill=(0,118,160,192))
    d.polygon([(0,round(h*.69)),(round(w*.48),round(h*.59)),(round(w*.68),h),(0,h)], fill=(244,254,255,232))
    d.rectangle((0,0,w,round(h*.08)), fill=(105,234,245,70))
    random.seed(31)
    for _ in range(55 if w>1300 else 24):
        x=random.randint(24,w-24); y=random.randint(24,h-24); rr=random.choice([2,2,3])
        d.ellipse((x-rr,y-rr,x+rr,y+rr), fill=(255,255,255,70))
    # faint paw prints
    for px,py,sc in [(0.08,0.18,1.0),(0.89,0.23,.9),(0.15,.78,.7),(0.76,.69,.75)]:
        cx,cy=round(w*px), round(h*py); fill=(255,255,255,42)
        for dx,dy,rx,ry in [(-18,-12,12,15),(0,-22,13,16),(19,-12,12,15),(0,8,22,18)]:
            d.ellipse((cx+(dx-rx)*sc,cy+(dy-ry)*sc,cx+(dx+rx)*sc,cy+(dy+ry)*sc), fill=fill)
    return im


def checker(size, block=44):
    im = Image.new('RGBA', size, (232,237,246,255))
    d = ImageDraw.Draw(im)
    for y in range(0,size[1],block):
        for x in range(0,size[0],block):
            if ((x//block+y//block)%2):
                d.rectangle((x,y,x+block-1,y+block-1), fill=(205,214,228,255))
    return im


def fit(canvas, asset, box, pad=0):
    x0,y0,x1,y1=box
    bw,bh=x1-x0-2*pad,y1-y0-2*pad
    scale=min(bw/asset.width,bh/asset.height)
    nw,nh=max(1,round(asset.width*scale)),max(1,round(asset.height*scale))
    im=asset.resize((nw,nh), Image.Resampling.LANCZOS)
    canvas.alpha_composite(im,(round(x0+pad+(bw-nw)/2),round(y0+pad+(bh-nh)/2)))
    return canvas


def draw_label(d, x, y, text, size, max_w=None):
    s=size
    f=font(s,bold=True)
    while max_w:
        bb=d.textbbox((0,0), text, font=f)
        if bb[2]-bb[0] <= max_w or s <= 24: break
        s-=2; f=font(s,bold=True)
    bb=d.textbbox((0,0), text, font=f)
    tw,th=bb[2]-bb[0],bb[3]-bb[1]
    d.rounded_rectangle((x-28,y-18,x+tw+28,y+th+24), radius=16, fill=PURPLE)
    d.text((x,y), text, font=f, fill=WHITE)
    return tw,th


def make_banner(asset, w, h, text=True, compact=False):
    im=bg(w,h); d=ImageDraw.Draw(im)
    if text:
        draw_label(d, round(w*.045), round(h*.145), 'KishuGuardian', round(h*.105), max_w=round(w*.43))
        # anti-spam control chips
        fsmall=font(round(h*.052), bold=True)
        spam=(round(w*.06),round(h*.36),round(w*.235),round(h*.485))
        d.rounded_rectangle(spam, radius=18, fill=(76,54,207,255), outline=PURPLE_DARK, width=5)
        d.text((spam[0]+round(w*.025), spam[1]+round(h*.027)), 'SPAM', font=fsmall, fill=WHITE)
        d.line((spam[0]+10,spam[3]-15,spam[2]-10,spam[1]+18), fill=GOLD, width=max(5,round(h*.012)))
        d.ellipse((round(w*.285),round(h*.37),round(w*.365),round(h*.53)), fill=(75,54,204,255), outline=PURPLE_DARK, width=5)
        d.text((round(w*.315),round(h*.392)), '!', font=font(round(h*.098), bold=True), fill=WHITE)
        d.rounded_rectangle((round(w*.06),round(h*.62),round(w*.39),round(h*.72)), radius=16, fill=(255,255,255,235), outline=CYAN_DARK, width=3)
        d.text((round(w*.083),round(h*.642)), 'Community Shield', font=font(round(h*.048), bold=True), fill=PURPLE)
        # small bot bubble
        d.ellipse((round(w*.415),round(h*.43),round(w*.495),round(h*.59)), fill=(72,55,185,230), outline=PURPLE_DARK, width=5)
        d.rounded_rectangle((round(w*.437),round(h*.475),round(w*.473),round(h*.525)), radius=5, fill=(176,190,223,255))
        d.ellipse((round(w*.445),round(h*.488),round(w*.453),round(h*.496)), fill=PURPLE_DARK)
        d.ellipse((round(w*.460),round(h*.488),round(w*.468),round(h*.496)), fill=PURPLE_DARK)
    if compact:
        fit(im, asset, (round(w*.50), round(h*.02), round(w*.98), round(h*.98)))
    else:
        fit(im, asset, (round(w*.55), round(-h*.04), round(w*1.00), round(h*1.06)))
    return im


def make_square(asset, profile=False, platform=None):
    im=bg(1254,1254)
    if profile:
        fit(im, asset, (68,58,1186,1170))
    else:
        fit(im, asset, (95,55,1159,1184))
    d=ImageDraw.Draw(im)
    if platform == 'yt':
        d.rounded_rectangle((116,116,194,170), radius=14, fill=(255,54,73,255))
        d.polygon([(148,128),(148,158),(176,143)], fill=WHITE)
    if platform == 'rd':
        d.rounded_rectangle((1056,116,1130,180), radius=18, fill=(255,255,255,238), outline=CYAN_DARK, width=3)
        for x in [1079,1098,1117]: d.ellipse((x,145,x+7,152), fill=CYAN_DARK)
    return im


def make_trans(asset, profile=False):
    im=Image.new('RGBA',(1254,1254),TRANSPARENT)
    if profile:
        fit(im, asset, (60,60,1194,1190))
    else:
        fit(im, asset, (80,50,1174,1190))
    return im


def make_preview(files):
    tw,th,lh=520,340,36
    cols=3; rows=math.ceil(len(files)/cols)
    sheet=Image.new('RGBA',(cols*tw,rows*(th+lh)),(18,29,51,255))
    lf=font(12)
    for i,p in enumerate(files):
        im=Image.open(p).convert('RGBA')
        cell=checker((tw,th)) if im.getchannel('A').getextrema()[0] < 255 else Image.new('RGBA',(tw,th),(235,247,248,255))
        scale=min(tw/im.width, th/im.height); nw,nh=round(im.width*scale), round(im.height*scale)
        r=im.resize((nw,nh), Image.Resampling.LANCZOS)
        cell.alpha_composite(r,((tw-nw)//2,(th-nh)//2))
        x=(i%cols)*tw; y=(i//cols)*(th+lh)
        sheet.alpha_composite(cell,(x,y))
        d=ImageDraw.Draw(sheet); d.rectangle((x,y+th,x+tw,y+th+lh), fill=(18,29,51,255))
        d.text((x+8,y+th+11), Path(p).name, font=lf, fill=(235,241,255,255))
    sheet.convert('RGB').save(OUT/'KishuGuardian AI Remake x12 Preview.jpg', quality=94)
    sheet.save(OUT/'KishuGuardian AI Remake x12 Preview.png')

full_raw=Image.open(FULL_IN).convert('RGBA')
profile_raw=Image.open(PROFILE_IN).convert('RGBA')
full=cut = crop_alpha(flood_remove_background(full_raw, 'white'), 18)
profile_cut=crop_alpha(flood_remove_background(profile_raw, 'blue'), 18)
full=add_shadow(full, blur=16, offset=(0,12), alpha=82)
profile=add_shadow(profile_cut, blur=16, offset=(0,12), alpha=82)
full.save(OUT/'KishuGuardian AI Full Body Source.png')
profile.save(OUT/'KishuGuardian AI Profile Badge Source.png')

outputs=[]
def save(name, im):
    p=OUT/name; im.save(p); outputs.append(p)

save('KishuGuardian AI Banner.png', make_banner(full,2048,1024,text=True,compact=False))
save('KishuGuardian AI Banner2.png', make_banner(full,2048,1024,text=False,compact=True))
save('KishuGuardian AI Big Banner.png', make_banner(full,2048,1152,text=True,compact=False))
save('KishuGuardian AI Big Banner2.png', make_banner(full,2048,1152,text=False,compact=True))
save('KishuGuardian AI Profile Pic1.png', make_trans(full))
save('KishuGuardian AI Profile Pic2.png', make_square(full))
save('KishuGuardian AI Profile Pic3.png', make_trans(profile,profile=True))
save('KishuGuardian AI Profile Pic4.png', make_square(profile,profile=True))
save('KishuGuardian AI RD.png', make_trans(full))
save('KishuGuardian AI RD2.png', make_square(full,platform='rd'))
save('KishuGuardian AI YT.png', make_trans(profile,profile=True))
save('KishuGuardian AI YT2.png', make_square(profile,profile=True,platform='yt'))
make_preview(outputs)

print('AI remake built:', OUT)
for p in outputs:
    im=Image.open(p)
    print(p.name, im.size, im.mode)
print('Preview:', OUT/'KishuGuardian AI Remake x12 Preview.jpg')
