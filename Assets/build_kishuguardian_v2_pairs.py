from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import random

ROOT = Path(r"C:\Users\ash2inf3rn0\Desktop")
OUT = ROOT / "Kishu Inu V2"
SRC = ROOT / "KishuGuardian" / "Matched Head Set"
FULL_SRC = SRC / "KishuGuardian Matched Full Body Source.png"
HEAD_SRC = SRC / "KishuGuardian Matched Head Source.png"
PREVIEW = OUT / "KishuGuardian x12 Pair Preview.png"

OUT.mkdir(parents=True, exist_ok=True)

PURPLE = (33, 12, 78, 255)
PURPLE_2 = (69, 32, 155, 255)
CYAN = (0, 198, 220, 255)
CYAN_DARK = (0, 114, 145, 255)
TEAL = (0, 157, 163, 255)
RED = (242, 43, 65, 255)
RED_DARK = (160, 23, 42, 255)
GOLD = (255, 184, 32, 255)
ORANGE = (255, 124, 18, 255)
WHITE = (255, 255, 255, 255)
INK = (16, 8, 42, 255)
CLEAR = (0, 0, 0, 0)


def font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\bahnschrift.ttf",
    ]
    for item in candidates:
        if item and Path(item).exists():
            return ImageFont.truetype(item, size)
    return ImageFont.load_default()


def crop_alpha(im, pad=14, threshold=4):
    im = im.convert("RGBA")
    a = im.getchannel("A")
    mask = a.point(lambda p: 255 if p > threshold else 0)
    box = mask.getbbox()
    if not box:
        return im
    x0, y0, x1, y1 = box
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(im.width, x1 + pad)
    y1 = min(im.height, y1 + pad)
    return im.crop((x0, y0, x1, y1))


def make_outline(asset, radius=8, color=(255, 255, 255, 245)):
    asset = asset.convert("RGBA")
    alpha = asset.getchannel("A")
    base = Image.new("RGBA", (asset.width + radius * 4, asset.height + radius * 4), CLEAR)
    mask = Image.new("L", base.size, 0)
    mask.paste(alpha, (radius * 2, radius * 2))
    expanded = mask.filter(ImageFilter.MaxFilter(radius * 2 + 1))
    blurred = expanded.filter(ImageFilter.GaussianBlur(radius / 2))
    outline = Image.new("RGBA", base.size, color)
    outline.putalpha(blurred)
    out = Image.new("RGBA", base.size, CLEAR)
    out.alpha_composite(outline)
    out.alpha_composite(asset, (radius * 2, radius * 2))
    return crop_alpha(out, pad=0)


def add_shadow(asset, blur=18, offset=(0, 14), alpha=96):
    asset = asset.convert("RGBA")
    shadow = Image.new("RGBA", (asset.width + blur * 5, asset.height + blur * 5), CLEAR)
    m = asset.getchannel("A").filter(ImageFilter.GaussianBlur(blur))
    sh = Image.new("RGBA", asset.size, (0, 0, 0, alpha))
    sh.putalpha(m.point(lambda p: min(alpha, p)))
    shadow.alpha_composite(sh, (blur * 2 + offset[0], blur * 2 + offset[1]))
    shadow.alpha_composite(asset, (blur * 2, blur * 2))
    return crop_alpha(shadow, pad=0)


def fit(canvas, asset, box, align=(0.5, 0.5)):
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    scale = min(bw / asset.width, bh / asset.height)
    nw, nh = max(1, round(asset.width * scale)), max(1, round(asset.height * scale))
    resized = asset.resize((nw, nh), Image.Resampling.LANCZOS)
    x = round(x0 + (bw - nw) * align[0])
    y = round(y0 + (bh - nh) * align[1])
    canvas.alpha_composite(resized, (x, y))
    return (x, y, x + nw, y + nh)


def bg_gradient(w, h, mode="wide"):
    im = Image.new("RGBA", (w, h), WHITE)
    pix = im.load()
    for y in range(h):
        for x in range(w):
            t = x / max(1, w - 1)
            v = y / max(1, h - 1)
            if mode == "square":
                r = round(12 * (1 - t) + 0 * t)
                g = round(185 * (1 - v) + 127 * t + 15 * v)
                b = round(216 * (1 - v) + 168 * t + 20 * v)
            else:
                r = round(0 + 8 * v)
                g = round(195 * (1 - t) + 122 * t)
                b = round(226 * (1 - t) + 170 * t)
            pix[x, y] = (r, g, b, 255)
    d = ImageDraw.Draw(im, "RGBA")
    if mode == "square":
        d.ellipse((-w * 0.08, h * 0.03, w * 1.04, h * 0.91), fill=(0, 219, 234, 62), outline=(255, 255, 255, 70), width=10)
        d.polygon([(0, 0), (w, 0), (w, h * 0.22), (0, h * 0.10)], fill=(120, 239, 245, 38))
        d.polygon([(0, h * 0.74), (w * 0.50, h * 0.64), (w * 0.70, h), (0, h)], fill=(244, 253, 255, 218))
    else:
        d.ellipse((w * 0.16, -h * 0.32, w * 1.06, h * 1.28), fill=(0, 211, 226, 45), outline=(255, 255, 255, 52), width=8)
        d.polygon([(w * 0.54, 0), (w, 0), (w, h), (w * 0.70, h)], fill=(0, 105, 145, 148))
        d.polygon([(0, h * 0.69), (w * 0.44, h * 0.58), (w * 0.68, h), (0, h)], fill=(245, 253, 255, 226))
    random.seed(315)
    for _ in range(46 if w > 1500 else 28):
        x = random.randint(28, w - 28)
        y = random.randint(28, h - 28)
        r = random.choice([2, 2, 3])
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, 56))
    for px, py, s in [(0.08, 0.16, 1.0), (0.88, 0.22, .86), (0.14, .78, .72), (0.78, .70, .76)]:
        draw_paw(d, round(w * px), round(h * py), round(32 * s), fill=(255, 255, 255, 42))
    return im


def checker(w, h, block=42):
    im = Image.new("RGBA", (w, h), (235, 239, 247, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, h, block):
        for x in range(0, w, block):
            if (x // block + y // block) % 2:
                d.rectangle((x, y, x + block - 1, y + block - 1), fill=(212, 220, 232, 255))
    return im


def rounded_label(d, xy, text, size, fill=PURPLE, fg=WHITE, max_w=None):
    x, y = xy
    s = size
    f = font(s, bold=True)
    while max_w:
        bb = d.textbbox((0, 0), text, font=f)
        if bb[2] - bb[0] <= max_w or s <= 26:
            break
        s -= 2
        f = font(s, bold=True)
    bb = d.textbbox((0, 0), text, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.rounded_rectangle((x - 30, y - 18, x + tw + 30, y + th + 22), radius=18, fill=fill)
    d.text((x, y), text, font=f, fill=fg)


def draw_confetti(d, w, h, count=18):
    random.seed(w * 7 + h)
    colors = [ORANGE, GOLD, CYAN, TEAL, RED, PURPLE_2, (255, 79, 139, 255)]
    for _ in range(count):
        x = random.randint(28, w - 28)
        y = random.randint(28, h - 28)
        c = random.choice(colors)
        if random.random() < .55:
            d.rounded_rectangle((x, y, x + 18, y + 9), radius=3, fill=c)
        else:
            d.polygon([(x, y - 12), (x + 4, y - 2), (x + 15, y), (x + 4, y + 4), (x, y + 16), (x - 5, y + 4), (x - 15, y), (x - 5, y - 2)], fill=c)


def draw_paw(d, cx, cy, r, fill=WHITE, outline=None, width=0):
    d.ellipse((cx - r * .85, cy - r * .15, cx + r * .85, cy + r * .92), fill=fill, outline=outline, width=width)
    for dx, dy, rr in [(-.75, -.58, .28), (-.25, -.86, .30), (.25, -.86, .30), (.75, -.58, .28)]:
        d.ellipse((cx + dx * r - rr * r, cy + dy * r - rr * r, cx + dx * r + rr * r, cy + dy * r + rr * r), fill=fill, outline=outline, width=width)


def draw_spam_icon(d, x, y, scale=1.0):
    w, h = round(176 * scale), round(108 * scale)
    d.rounded_rectangle((x, y, x + w, y + h), radius=round(13 * scale), fill=PURPLE_2, outline=PURPLE, width=max(3, round(5 * scale)))
    d.text((x + round(25 * scale), y + round(24 * scale)), "SPAM", font=font(round(32 * scale), bold=True), fill=WHITE)
    d.line((x + 14 * scale, y + h - 18 * scale, x + w - 14 * scale, y + 18 * scale), fill=GOLD, width=max(4, round(7 * scale)))


def draw_alert(d, x, y, r):
    d.ellipse((x - r, y - r, x + r, y + r), fill=PURPLE_2, outline=PURPLE, width=max(3, r // 10))
    d.text((x - r * .16, y - r * .58), "!", font=font(round(r * 1.25), bold=True), fill=WHITE)


def draw_chat(d, x, y, w, h, color=CYAN):
    d.rounded_rectangle((x, y, x + w, y + h), radius=round(h * .22), fill=color, outline=PURPLE, width=max(4, round(h * .07)))
    d.polygon([(x + w * .30, y + h), (x + w * .42, y + h), (x + w * .28, y + h * 1.22)], fill=color, outline=PURPLE)
    dot = round(h * .10)
    for i in range(3):
        cx = x + round(w * (.32 + i * .18))
        cy = y + round(h * .48)
        d.ellipse((cx - dot, cy - dot, cx + dot, cy + dot), fill=WHITE)


def draw_reddit(d, x, y, r):
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 68, 47, 255), outline=PURPLE, width=max(4, r // 9))
    d.ellipse((x - r * .52, y - r * .28, x + r * .52, y + r * .52), fill=WHITE)
    d.line((x + r * .10, y - r * .34, x + r * .30, y - r * .72), fill=WHITE, width=max(4, r // 9))
    d.ellipse((x + r * .22, y - r * .87, x + r * .44, y - r * .65), fill=WHITE)
    for dx in [-.22, .22]:
        d.ellipse((x + dx * r - r * .08, y + r * .02 - r * .08, x + dx * r + r * .08, y + r * .02 + r * .08), fill=(255, 68, 47, 255))
    d.arc((x - r * .25, y + r * .12, x + r * .25, y + r * .40), 0, 180, fill=PURPLE, width=max(3, r // 13))


def draw_youtube(d, x, y, w, h):
    d.rounded_rectangle((x, y, x + w, y + h), radius=round(h * .20), fill=(255, 28, 44, 255), outline=PURPLE, width=max(6, round(h * .06)))
    d.polygon([(x + w * .43, y + h * .30), (x + w * .43, y + h * .70), (x + w * .72, y + h * .50)], fill=WHITE)


def draw_code_shield(d, x, y, w, h):
    d.rounded_rectangle((x, y, x + w, y + h), radius=round(w * .10), fill=(255, 255, 255, 236), outline=CYAN_DARK, width=max(3, round(w * .018)))
    f = font(round(h * .24), bold=True)
    d.text((x + w * .15, y + h * .21), "{ }", font=f, fill=PURPLE)
    d.text((x + w * .14, y + h * .56), "Community Shield", font=font(round(h * .16), bold=True), fill=PURPLE)


def draw_terminal_card(d, x, y, w, h, title="Guardian Scan"):
    d.rounded_rectangle((x, y, x + w, y + h), radius=round(h * .16), fill=(255, 255, 255, 238), outline=PURPLE, width=max(4, round(h * .045)))
    d.rounded_rectangle((x + 10, y + 10, x + w - 10, y + round(h * .30)), radius=round(h * .10), fill=PURPLE)
    d.text((x + round(w * .08), y + round(h * .075)), title, font=font(round(h * .14), bold=True), fill=WHITE)
    rows = [("{ }", CYAN_DARK), ("SPAM", RED), ("OK", TEAL)]
    for i, (label, color) in enumerate(rows):
        yy = y + round(h * (.40 + i * .18))
        d.rounded_rectangle((x + round(w * .08), yy, x + round(w * .21), yy + round(h * .10)), radius=round(h * .045), fill=color)
        d.text((x + round(w * .27), yy - round(h * .01)), label, font=font(round(h * .13), bold=True), fill=PURPLE)
        d.line((x + round(w * .48), yy + round(h * .05), x + round(w * .90), yy + round(h * .05)), fill=(0, 151, 170, 120), width=max(3, round(h * .018)))


def draw_cube(d, x, y, s, color=CYAN):
    side = (round(s * .22), round(s * .16))
    d.polygon([(x, y), (x + s, y), (x + s + side[0], y + side[1]), (x + side[0], y + side[1])], fill=tuple(min(255, c + 28) for c in color[:3]) + (235,), outline=PURPLE)
    d.polygon([(x, y), (x + side[0], y + side[1]), (x + side[0], y + s + side[1]), (x, y + s)], fill=color, outline=PURPLE)
    d.polygon([(x + side[0], y + side[1]), (x + s + side[0], y + side[1]), (x + s + side[0], y + s + side[1]), (x + side[0], y + s + side[1])], fill=tuple(max(0, c - 28) for c in color[:3]) + (235,), outline=PURPLE)
    draw_paw(d, x + round(s * .58), y + round(s * .58), round(s * .18), fill=WHITE)


def draw_guardian_props(d, w, h, density="wide"):
    scale = h / 1024
    draw_terminal_card(d, round(w * .055), round(h * .46), round(w * .31), round(h * .22), title="Guardian Scan")
    draw_cube(d, round(w * .075), round(h * .72), round(110 * scale), color=CYAN)
    draw_cube(d, round(w * .245), round(h * .74), round(96 * scale), color=(255, 133, 26, 255))
    draw_chat(d, round(w * .405), round(h * .255), round(w * .105), round(h * .075), color=(114, 102, 210, 255))
    draw_alert(d, round(w * .317), round(h * .315), round(h * .058))
    for px, py, s in [(0.18, 0.34, .9), (0.38, 0.72, .68), (0.48, 0.18, .56)]:
        d.rounded_rectangle((round(w * px), round(h * py), round(w * px + 78 * scale * s), round(h * py + 54 * scale * s)), radius=round(12 * scale * s), fill=(255, 255, 255, 210), outline=PURPLE, width=max(3, round(4 * scale * s)))
        d.text((round(w * px + 18 * scale * s), round(h * py + 10 * scale * s)), "{ }", font=font(round(18 * scale * s), bold=True), fill=CYAN_DARK)


def draw_caption_bar(d, w, h, text):
    f = font(round(h * .068), bold=True)
    bb = d.textbbox((0, 0), text, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x = (w - tw) // 2
    y = round(h * .84)
    d.rounded_rectangle((x - 32, y - 18, x + tw + 32, y + th + 18), radius=18, fill=PURPLE)
    d.text((x, y), text, font=f, fill=WHITE)


def make_head_badge(head, label=False, youtube=False):
    w = h = 1160
    im = Image.new("RGBA", (w, h), CLEAR)
    d = ImageDraw.Draw(im, "RGBA")
    d.ellipse((76, 72, 1084, 1078), fill=(0, 181, 210, 238), outline=(255, 255, 255, 245), width=24)
    d.ellipse((132, 132, 1028, 1028), fill=(255, 255, 255, 42), outline=PURPLE, width=16)
    d.polygon([(580, 1044), (884, 910), (820, 1110), (580, 1150), (340, 1110), (276, 910)], fill=(30, 16, 84, 246), outline=WHITE)
    fit(im, head, (74, 2, 1086, 960))
    d.rounded_rectangle((380, 870, 780, 1052), radius=34, fill=(21, 10, 56, 235), outline=(255, 255, 255, 230), width=8)
    draw_paw(d, 580, 958, 54, fill=WHITE)
    if label:
        f = font(76, bold=True)
        text = "KishuGuardian"
        bb = d.textbbox((0, 0), text, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        x = (w - tw) // 2
        y = 1005
        d.rounded_rectangle((x - 34, y - 20, x + tw + 34, y + th + 24), radius=24, fill=PURPLE)
        d.text((x, y), text, font=f, fill=WHITE)
    if youtube:
        draw_youtube(d, 812, 132, 190, 122)
    return crop_alpha(im, pad=8)


def clear_canvas(w, h):
    return Image.new("RGBA", (w, h), CLEAR)


def make_banner(asset, with_bg=False, big=False):
    w, h = (2048, 1024) if not big else (2048, 1152)
    im = bg_gradient(w, h, "wide") if with_bg else clear_canvas(w, h)
    d = ImageDraw.Draw(im, "RGBA")
    if not with_bg:
        draw_confetti(d, w, h, 26)
    rounded_label(d, (round(w * .055), round(h * .115)), "KishuGuardian", round(h * .085), max_w=round(w * .42))
    draw_spam_icon(d, round(w * .060), round(h * .285), h / 760)
    draw_guardian_props(d, w, h)
    fit(im, asset, (round(w * .48), round(-h * .04), round(w * .98), round(h * .99)))
    if with_bg:
        im.putalpha(255)
    return im


def make_full_square(asset, with_bg=False, platform=None):
    w = h = 1254
    im = bg_gradient(w, h, "square") if with_bg else clear_canvas(w, h)
    d = ImageDraw.Draw(im, "RGBA")
    if not with_bg:
        draw_confetti(d, w, h, 24)
    draw_terminal_card(d, 70, 820, 390, 210, title="Shield")
    draw_cube(d, 830, 875, 138, color=CYAN)
    draw_cube(d, 970, 795, 108, color=(255, 135, 24, 255))
    fit(im, asset, (92, 22, 1126, 1160))
    if platform == "rd":
        draw_chat(d, 980, 94, 110, 76, color=(255, 255, 255, 230))
    if with_bg:
        im.putalpha(255)
    return im


def make_profile_head(head, with_bg=False, alt=False, platform=None):
    w = h = 1254
    im = bg_gradient(w, h, "square") if with_bg else clear_canvas(w, h)
    d = ImageDraw.Draw(im, "RGBA")
    if not with_bg:
        draw_confetti(d, w, h, 14)
    badge = make_head_badge(head, label=alt, youtube=(platform == "yt"))
    fit(im, badge, (74, 58, 1180, 1190))
    if platform == "yt":
        draw_youtube(d, 920, 118, 182, 120)
    if with_bg:
        im.putalpha(255)
    return im


def make_social_square(asset, head, with_bg=False, youtube=False):
    w = h = 1254
    im = bg_gradient(w, h, "square") if with_bg else clear_canvas(w, h)
    d = ImageDraw.Draw(im, "RGBA")
    if youtube:
        badge = make_head_badge(head, label=True, youtube=False)
        fit(im, badge, (74, 78, 832, 1148))
        draw_youtube(d, 820, 172, 294, 184)
    else:
        draw_chat(d, 105, 124, 210, 128, CYAN)
        draw_chat(d, 900, 166, 210, 128, RED)
        draw_reddit(d, 900, 450, 108)
        draw_alert(d, 168, 470, 78)
        fit(im, asset, (242, 72, 1000, 1160))
    if with_bg:
        im.putalpha(255)
    return im


def save(path, image):
    image.save(path)
    return path


def preview(paths):
    cell_w, cell_h = 520, 390
    label_h = 34
    cols = 4
    rows = math.ceil(len(paths) / cols)
    board = Image.new("RGBA", (cols * cell_w, rows * (cell_h + label_h)), (12, 24, 46, 255))
    for i, p in enumerate(paths):
        r, c = divmod(i, cols)
        x, y = c * cell_w, r * (cell_h + label_h)
        bg = checker(cell_w, cell_h) if p.name.replace(".png", "").endswith(("Banner", "Big Banner", "Profile Pic1", "Profile Pic3", "RD", "YT")) else Image.new("RGBA", (cell_w, cell_h), (236, 248, 250, 255))
        board.alpha_composite(bg, (x, y))
        im = Image.open(p).convert("RGBA")
        fit(board, im, (x + 0, y + 0, x + cell_w, y + cell_h))
        d = ImageDraw.Draw(board)
        d.rectangle((x, y + cell_h, x + cell_w, y + cell_h + label_h), fill=(12, 24, 46, 255))
        d.text((x + 8, y + cell_h + 8), p.name, font=font(13), fill=WHITE)
    board.convert("RGB").save(PREVIEW)


def main():
    full_raw = crop_alpha(Image.open(FULL_SRC).convert("RGBA"), pad=0)
    full = full_raw
    head = crop_alpha(Image.open(HEAD_SRC).convert("RGBA"), pad=0)
    full = make_outline(full, radius=8, color=(255, 255, 255, 245))
    head = make_outline(head, radius=8, color=(255, 255, 255, 245))
    full_bg = add_shadow(full, blur=18, offset=(0, 16), alpha=100)
    head_bg = add_shadow(head, blur=18, offset=(0, 16), alpha=100)

    outputs = []
    outputs.append(save(OUT / "KishuGuardian Banner.png", make_banner(full, with_bg=False, big=False)))
    outputs.append(save(OUT / "KishuGuardian Banner2.png", make_banner(full_bg, with_bg=True, big=False)))
    outputs.append(save(OUT / "KishuGuardian Big Banner.png", make_banner(full, with_bg=False, big=True)))
    outputs.append(save(OUT / "KishuGuardian Big Banner2.png", make_banner(full_bg, with_bg=True, big=True)))
    outputs.append(save(OUT / "KishuGuardian Profile Pic1.png", make_profile_head(head, with_bg=False, alt=False)))
    outputs.append(save(OUT / "KishuGuardian Profile Pic2.png", make_profile_head(head_bg, with_bg=True, alt=False)))
    outputs.append(save(OUT / "KishuGuardian Profile Pic3.png", make_profile_head(head, with_bg=False, alt=True)))
    outputs.append(save(OUT / "KishuGuardian Profile Pic4.png", make_profile_head(head_bg, with_bg=True, alt=True)))
    outputs.append(save(OUT / "KishuGuardian RD.png", make_social_square(full, head, with_bg=False, youtube=False)))
    outputs.append(save(OUT / "KishuGuardian RD2.png", make_social_square(full_bg, head_bg, with_bg=True, youtube=False)))
    outputs.append(save(OUT / "KishuGuardian YT.png", make_social_square(full, head, with_bg=False, youtube=True)))
    outputs.append(save(OUT / "KishuGuardian YT2.png", make_social_square(full_bg, head_bg, with_bg=True, youtube=True)))
    preview(outputs)
    print("Built:", OUT)
    for p in outputs:
        im = Image.open(p).convert("RGBA")
        print(f"{p.name} | {im.size} | alpha {im.getchannel('A').getextrema()}")
    print("Preview:", PREVIEW)


if __name__ == "__main__":
    main()
