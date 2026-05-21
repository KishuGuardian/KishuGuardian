
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from pathlib import Path
from collections import deque
import os, math, random

ROOT = Path(r'C:\Users\ash2inf3rn0\Desktop\KishuGuardian')
SRC_FULL = ROOT / 'Generated Masters' / 'KishuGuardian Generated Full Body.png'
OUT = ROOT / 'Matched Head Set'
OUT.mkdir(parents=True, exist_ok=True)

PURPLE = (35, 18, 96, 255)
PURPLE_DARK = (18, 10, 56, 255)
PURPLE_MID = (75, 54, 205, 255)
CYAN = (0, 190, 226, 255)
CYAN_DARK = (0, 125, 166, 255)
CYAN_LIGHT = (101, 235, 245, 255)
WHITE = (255,255,255,255)
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


def flood_remove_light_bg(im):
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
        if a < 8:
            return True
        # Only remove edge-connected light neutral background. Tan fur is not edge-connected.
        mx, mn = max(r,g,b), min(r,g,b)
        return (r > 218 and g > 218 and b > 213 and (mx - mn) < 38) or (r > 235 and g > 232 and b > 226)
    while q:
        x,y = q.popleft()
        if x < 0 or y < 0 or x >= w or y >= h:
            continue
        i = y*w+x
        if visited[i]:
            continue
        r,g,b,a = pix[x,y]
        if not is_bg(r,g,b,a):
            continue
        visited[i] = 1
        q.append((x+1,y)); q.append((x-1,y)); q.append((x,y+1)); q.append((x,y-1))
    alpha = im.getchannel('A')
    ad = alpha.load()
    for y in range(h):
        for x in range(w):
            if visited[y*w+x]:
                ad[x,y] = 0
    # Remove tiny isolated light flecks connected to old background and feather edges.
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.45))
    im.putalpha(alpha)
    return im


def alpha_bbox(im, threshold=6):
    a = im.getchannel('A')
    # Increase threshold to avoid faint source background residue.
    mask = a.point(lambda p: 255 if p > threshold else 0)
    return mask.getbbox()


def crop_alpha(im, pad=18, threshold=10):
    bbox = alpha_bbox(im, threshold)
    if not bbox:
        return im
    x0,y0,x1,y1 = bbox
    x0=max(0,x0-pad); y0=max(0,y0-pad); x1=min(im.width,x1+pad); y1=min(im.height,y1+pad)
    return im.crop((x0,y0,x1,y1))


def make_outline(asset, color=PURPLE_DARK, radius=8, opacity=185):
    a = asset.getchannel('A')
    grow = a.filter(ImageFilter.MaxFilter(radius*2+1)).filter(ImageFilter.GaussianBlur(1.2))
    outline = Image.new('RGBA', asset.size, color[:3]+(opacity,))
    outline.putalpha(grow)
    out = Image.new('RGBA', asset.size, TRANSPARENT)
    out.alpha_composite(outline)
    out.alpha_composite(asset)
    return out


def add_shadow(asset, blur=16, offset=(0,12), alpha=72):
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
            r=round(0 + 10*v)
            g=round((199-26*v)*(1-t)+(128-16*v)*t)
            b=round((230-8*v)*(1-t)+(178-15*v)*t)
            pix[x,y]=(r,g,b,255)
    overlay = Image.new('RGBA', (w,h), TRANSPARENT)
    d=ImageDraw.Draw(overlay)
    d.polygon([(round(w*.52),0),(w,0),(w,h),(round(w*.69),h)], fill=(0,118,160,190))
    d.polygon([(0,round(h*.68)),(round(w*.48),round(h*.58)),(round(w*.68),h),(0,h)], fill=(244,254,255,232))
    d.rectangle((0,0,w,round(h*.08)), fill=(105,234,245,70))
    random.seed(53)
    for _ in range(58 if w > 1500 else 30):
        x=random.randint(24,w-24); y=random.randint(24,h-24); rr=random.choice([2,2,3])
        d.ellipse((x-rr,y-rr,x+rr,y+rr), fill=(255,255,255,68))
    for px,py,sc in [(0.08,0.18,1.0),(0.89,0.23,.9),(0.15,.78,.7),(0.76,.69,.75)]:
        cx,cy=round(w*px), round(h*py); fill=(255,255,255,38)
        for dx,dy,rx,ry in [(-18,-12,12,15),(0,-22,13,16),(19,-12,12,15),(0,8,22,18)]:
            d.ellipse((cx+(dx-rx)*sc,cy+(dy-ry)*sc,cx+(dx+rx)*sc,cy+(dy+ry)*sc), fill=fill)
    im.alpha_composite(overlay)
    return im


def checker(size, block=44):
    im = Image.new('RGBA', size, (232,237,246,255))
    d=ImageDraw.Draw(im)
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
        if bb[2]-bb[0] <= max_w or s <= 24:
            break
        s-=2; f=font(s,bold=True)
    bb=d.textbbox((0,0), text, font=f)
    tw,th=bb[2]-bb[0],bb[3]-bb[1]
    d.rounded_rectangle((x-28,y-18,x+tw+28,y+th+24), radius=16, fill=PURPLE)
    d.text((x,y), text, font=f, fill=WHITE)


def draw_banner_details(im, w, h):
    d=ImageDraw.Draw(im)
    draw_label(d, round(w*.045), round(h*.145), 'KishuGuardian', round(h*.105), max_w=round(w*.43))
    fsmall=font(round(h*.052), bold=True)
    spam=(round(w*.06),round(h*.36),round(w*.235),round(h*.485))
    d.rounded_rectangle(spam, radius=18, fill=PURPLE_MID, outline=PURPLE_DARK, width=max(3,round(h*.007)))
    d.text((spam[0]+round(w*.025), spam[1]+round(h*.027)), 'SPAM', font=fsmall, fill=WHITE)
    d.line((spam[0]+10,spam[3]-15,spam[2]-10,spam[1]+18), fill=GOLD, width=max(5,round(h*.012)))
    d.ellipse((round(w*.285),round(h*.37),round(w*.365),round(h*.53)), fill=PURPLE_MID, outline=PURPLE_DARK, width=max(3,round(h*.007)))
    d.text((round(w*.315),round(h*.392)), '!', font=font(round(h*.098), bold=True), fill=WHITE)
    d.rounded_rectangle((round(w*.06),round(h*.62),round(w*.39),round(h*.72)), radius=16, fill=(255,255,255,235), outline=CYAN_DARK, width=max(2,round(h*.004)))
    d.text((round(w*.083),round(h*.642)), 'Community Shield', font=font(round(h*.048), bold=True), fill=PURPLE)
    # small bot bubble
    d.ellipse((round(w*.415),round(h*.43),round(w*.495),round(h*.59)), fill=(72,55,185,232), outline=PURPLE_DARK, width=max(3,round(h*.007)))
    d.rounded_rectangle((round(w*.437),round(h*.475),round(w*.473),round(h*.525)), radius=5, fill=(176,190,223,255))
    d.ellipse((round(w*.445),round(h*.488),round(w*.453),round(h*.496)), fill=PURPLE_DARK)
    d.ellipse((round(w*.460),round(h*.488),round(w*.468),round(h*.496)), fill=PURPLE_DARK)


def make_banner(asset, w, h, with_bg):
    im = bg(w,h) if with_bg else Image.new('RGBA', (w,h), TRANSPARENT)
    draw_banner_details(im, w, h)
    fit(im, asset, (round(w*.55), round(-h*.04), round(w*1.00), round(h*1.06)))
    if with_bg:
        im.putalpha(255)
    return im


def make_full(asset, with_bg, platform=None):
    im = bg(1254,1254) if with_bg else Image.new('RGBA',(1254,1254),TRANSPARENT)
    fit(im, asset, (80,50,1174,1190))
    d=ImageDraw.Draw(im)
    if platform == 'rd':
        d.rounded_rectangle((1056,116,1130,180), radius=18, fill=(255,255,255,238), outline=CYAN_DARK, width=3)
        for x in [1079,1098,1117]:
            d.ellipse((x,145,x+7,152), fill=CYAN_DARK)
    if with_bg:
        im.putalpha(255)
    return im


def make_head(asset, with_bg, platform=None, label=False):
    im = bg(1254,1254) if with_bg else Image.new('RGBA',(1254,1254),TRANSPARENT)
    fit(im, asset, (74,68,1180,1115))
    d=ImageDraw.Draw(im)
    if label:
        f=font(78,bold=True)
        text='KishuGuardian'
        bb=d.textbbox((0,0), text, font=f)
        tw,th=bb[2]-bb[0],bb[3]-bb[1]
        x=(1254-tw)//2; y=1060
        d.rounded_rectangle((x-34,y-18,x+tw+34,y+th+22), radius=22, fill=PURPLE)
        d.text((x,y), text, font=f, fill=WHITE)
    if platform == 'yt':
        d.rounded_rectangle((116,116,194,170), radius=14, fill=(255,54,73,255))
        d.polygon([(148,128),(148,158),(176,143)], fill=WHITE)
    if with_bg:
        im.putalpha(255)
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
    sheet.convert('RGB').save(OUT/'KishuGuardian Matched Head x12 Preview.jpg', quality=94)
    sheet.save(OUT/'KishuGuardian Matched Head x12 Preview.png')

# Build single-source full body cutout and matching head crop.
raw = Image.open(SRC_FULL).convert('RGBA')
cut = crop_alpha(flood_remove_light_bg(raw), pad=12, threshold=14)
# Remove some bottom floor-shadow residue from transparent versions by lightly fading neutral gray pixels near bottom.
pix = cut.load()
w,h = cut.size
for y in range(round(h*.82), h):
    for x in range(w):
        r,g,b,a = pix[x,y]
        if a and abs(r-g)<18 and abs(g-b)<22 and 100 < r < 190:
            pix[x,y] = (r,g,b, min(a, 82))
full_source = crop_alpha(make_outline(cut, radius=2, opacity=120), pad=8, threshold=10)
# Head crop from the same source, not the separate generated profile.
fw,fh = full_source.size
head_box = (round(fw*0.20), 0, round(fw*0.755), round(fh*0.515))
head = crop_alpha(full_source.crop(head_box), pad=16, threshold=8)

full_source.save(OUT/'KishuGuardian Matched Full Body Source.png')
head.save(OUT/'KishuGuardian Matched Head Source.png')
full_for_bg = add_shadow(full_source, blur=15, offset=(0,12), alpha=72)
head_for_bg = add_shadow(head, blur=15, offset=(0,12), alpha=72)

outputs=[]
def save(name, im):
    p=OUT/name; im.save(p); outputs.append(p)

# x6 transparent/clear background.
save('KishuGuardian Matched Banner Clear.png', make_banner(full_source,2048,1024,with_bg=False))
save('KishuGuardian Matched Big Banner Clear.png', make_banner(full_source,2048,1152,with_bg=False))
save('KishuGuardian Matched Full Body Clear.png', make_full(full_source,with_bg=False))
save('KishuGuardian Matched Profile Pic Clear.png', make_head(head,with_bg=False,label=True))
save('KishuGuardian Matched RD Clear.png', make_full(full_source,with_bg=False,platform='rd'))
save('KishuGuardian Matched YT Clear.png', make_head(head,with_bg=False,platform='yt',label=True))
# Same x6 with actual backgrounds.
save('KishuGuardian Matched Banner BG.png', make_banner(full_for_bg,2048,1024,with_bg=True))
save('KishuGuardian Matched Big Banner BG.png', make_banner(full_for_bg,2048,1152,with_bg=True))
save('KishuGuardian Matched Full Body BG.png', make_full(full_for_bg,with_bg=True))
save('KishuGuardian Matched Profile Pic BG.png', make_head(head_for_bg,with_bg=True,label=True))
save('KishuGuardian Matched RD BG.png', make_full(full_for_bg,with_bg=True,platform='rd'))
save('KishuGuardian Matched YT BG.png', make_head(head_for_bg,with_bg=True,platform='yt',label=True))

make_preview(outputs)
print('Built matched-head set:', OUT)
for p in outputs:
    im=Image.open(p)
    print(p.name, im.size, im.mode)
print('Preview:', OUT/'KishuGuardian Matched Head x12 Preview.jpg')
