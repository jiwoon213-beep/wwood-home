# -*- coding: utf-8 -*-
"""만들기 자재 완성 그림(등각 투영 3D 그림) — python3 mkdraw.py  →  assets/mandeul/<slug>.jpg
모델 단위는 mm. B(x, y, z, 가로x, 깊이y, 높이z, 재질). 보는 쪽은 +x·+y·+z(앞쪽이 +y).
새 만들기를 추가하면 MODELS 에 같은 방식으로 상자들을 넣고 다시 실행하세요."""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

MAT = {  # 기본색, 결 방향 표시 여부
    "bangbu": ((168, 146, 104), True), "gujo": ((224, 198, 152), True), "misong": ((228, 192, 140), True),
    "acacia": ((190, 132, 78), True), "rubber": ((214, 168, 110), True), "spruce": ((232, 206, 160), True),
    "mdf": ((190, 152, 110), False), "mdf6": ((176, 140, 100), False), "hapan": ((218, 182, 126), True),
    "osb": ((198, 158, 92), False), "pink": ((238, 160, 172), False), "gyp": ((232, 232, 226), False),
    "daru": ((214, 184, 138), True), "metal": ((58, 58, 62), False), "soil": ((92, 68, 48), False),
    "plant": ((86, 140, 70), False), "wood2": ((150, 104, 64), True), "deck2": ((160, 138, 98), True),
    "conc": ((178, 176, 170), False), "wrap": ((236, 238, 240), False), "siding": ((196, 190, 178), True), "white": ((242, 240, 234), False),
    "maru": ((170, 122, 80), True), "hapdeck": ((112, 86, 66), True), "foam": ((236, 214, 120), False), "stained": ((128, 84, 52), True),
    "tempa": ((206, 168, 120), True), "tempa2": ((120, 86, 56), False), "acoustic": ((214, 186, 146), True), "hinoki": ((236, 214, 170), True), "putty": ((246, 246, 242), False),
}
S = 2  # 슈퍼샘플


def B(x, y, z, w, d, h, m):
    return (x, y, z, w, d, h, m)


def proj(p, sc, ox, oy):
    x, y, z = p
    return (ox + (x - y) * math.cos(math.pi / 6) * sc, oy + (x + y) * math.sin(math.pi / 6) * sc - z * sc)


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def wmark(img):
    """오른쪽 아래 저작권 표시 + 옅은 사선 반복 워터마크"""
    W, H = img.size
    try:
        f = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", max(14, W // 60))
    except OSError:
        f = ImageFont.load_default()
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    t = "© 영진종합목재 wwood.co.kr"
    step = max(260, W // 4)
    for yy in range(-H, H * 2, step // 2):
        for xx in range(-W, W * 2, step):
            d.text((xx + (yy // (step // 2)) % 2 * step // 2, yy), t, fill=(120, 100, 80, 22), font=f)
    lay = lay.rotate(22, resample=Image.BICUBIC, center=(W / 2, H / 2))
    d2 = ImageDraw.Draw(lay)
    tw = d2.textlength(t, font=f)
    d2.rounded_rectangle([W - tw - 30, H - 44, W - 10, H - 12], 8, fill=(255, 255, 255, 190))
    d2.text((W - tw - 20, H - 41), t, fill=(150, 20, 26, 255), font=f)
    out = img.convert("RGBA"); out.alpha_composite(lay)
    return out.convert("RGB")


def save_c(img, path, q):
    ex = img.getexif()
    ex[0x013B] = "영진종합목재(월드건축자재) www.wwood.co.kr".encode("utf-8").decode("latin-1", "ignore") or "Youngjin Wood"
    ex[0x8298] = "Copyright (c) Youngjin Wood (wwood.co.kr). All rights reserved. Unauthorized use prohibited."
    ex[0x013B] = "Youngjin Wood (wwood.co.kr)"
    img.save(path, quality=q, exif=ex)


def render(slug, boxes, out=None, label="", hl=None, size=(1200, 800)):
    random.seed(slug)
    W, H = size[0] * S, size[1] * S
    img = Image.new("RGB", (W, H), (246, 242, 234))
    g = ImageDraw.Draw(img)
    for i in range(H):  # 배경 그라데이션
        t = i / H
        g.line([(0, i), (W, i)], fill=(int(250 - 14 * t), int(247 - 16 * t), int(240 - 20 * t)))
    # 화면 맞춤
    pts = []
    for x, y, z, w, d, h, m in boxes:
        for dx in (0, w):
            for dy in (0, d):
                for dz in (0, h):
                    pts.append((x + dx, y + dy, z + dz))
    p0 = [proj(p, 1, 0, 0) for p in pts]
    minx, maxx = min(p[0] for p in p0), max(p[0] for p in p0)
    miny, maxy = min(p[1] for p in p0), max(p[1] for p in p0)
    sc = min((W * 0.78) / (maxx - minx), (H * 0.70) / (maxy - miny))
    ox = W / 2 - (minx + maxx) / 2 * sc
    oy = H * 0.53 - (miny + maxy) / 2 * sc
    # 바닥 그림자
    gx0 = min(p[0] for p in pts); gx1 = max(p[0] for p in pts); gy0 = min(p[1] for p in pts); gy1 = max(p[1] for p in pts)
    sh = Image.new("L", (W, H), 0); sg = ImageDraw.Draw(sh)
    pad = 60
    sg.polygon([proj(q, sc, ox, oy) for q in [(gx0 - pad, gy0 - pad, 0), (gx1 + pad, gy0 - pad, 0), (gx1 + pad * 3, gy1 + pad * 3, 0), (gx0 - pad, gy1 + pad, 0)]], fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(28 * S))
    img.paste(Image.new("RGB", (W, H), (120, 105, 85)), (0, 0), sh)
    # 면 목록 (+z 윗면, +x 오른면, +y 앞면)
    faces = []
    for (x, y, z, w, d, h, m) in boxes:
        X, Y, Z = x + w, y + d, z + h
        L = max(w, d, h)
        ax = "x" if L == w else ("y" if L == d else "z")
        bi = len(faces) // 3
        faces.append(((x + X) / 2 + (y + Y) / 2 + Z, [(x, y, Z), (X, y, Z), (X, Y, Z), (x, Y, Z)], m, 1.06, ax, "top", bi))
        faces.append((X + (y + Y) / 2 + (z + Z) / 2, [(X, y, z), (X, Y, z), (X, Y, Z), (X, y, Z)], m, 0.80, ax, "x", bi))
        faces.append(((x + X) / 2 + Y + (z + Z) / 2, [(x, Y, z), (X, Y, z), (X, Y, Z), (x, Y, Z)], m, 0.92, ax, "y", bi))
    # 상자 단위 위상 정렬: A가 B 뒤(어느 축으로든 A 최대 ≤ B 최소)면 A 먼저
    nb = len(boxes)
    def behind(a, b):
        ax0, ay0, az0, aw, ad, ah, _ = a; bx0, by0, bz0, bw, bd, bh, _ = b
        return (ax0 + aw <= bx0 + 0.01) or (ay0 + ad <= by0 + 0.01) or (az0 + ah <= bz0 + 0.01)
    order, done = [], [False] * nb
    for _ in range(nb):
        best = None
        for i in range(nb):
            if done[i]: continue
            if all(done[j] or j == i or not (behind(boxes[i], boxes[j]) is False and behind(boxes[j], boxes[i])) for j in range(nb)):
                best = i; break
        if best is None: best = min((i for i in range(nb) if not done[i]), key=lambda i: sum(boxes[i][:3]))
        done[best] = True; order.append(best)
    rank = {i: r for r, i in enumerate(order)}
    faces = [f + (rank[f[6]],) for f in faces]
    faces.sort(key=lambda f: (f[-1], f[0]))
    faces = [f[:-1] for f in faces]
    for _, quad, m, k, ax, fn, bi in faces:
        base, grain = MAT[m]
        if hl is not None and bi not in hl: base = tuple(int(v * 0.55 + 235 * 0.45) for v in base)
        poly = [proj(q, sc, ox, oy) for q in quad]
        g.polygon(poly, fill=shade(base, k))
        if grain or m in ("osb",):
            lay = Image.new("RGB", (W, H)); lg = ImageDraw.Draw(lay)
            mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon(poly, fill=255)
            # 결 방향: 부재의 긴 축
            a, b2, c, d2 = quad
            if m == "osb":
                bb = [min(p[0] for p in poly), min(p[1] for p in poly), max(p[0] for p in poly), max(p[1] for p in poly)]
                lg.rectangle(bb, fill=shade(base, k))
                for _ in range(int((bb[2] - bb[0]) * (bb[3] - bb[1]) / (60 * S * S)) + 5):
                    cx = random.uniform(bb[0], bb[2]); cy = random.uniform(bb[1], bb[3]); r = random.uniform(4, 12) * S
                    lg.ellipse([cx - r, cy - r * 0.5, cx + r, cy + r * 0.5], fill=shade(base, k * random.uniform(0.8, 1.15)))
            else:
                lg.polygon(poly, fill=shade(base, k))
                # 면 위 두 방향 벡터
                u = (quad[1][0] - quad[0][0], quad[1][1] - quad[0][1], quad[1][2] - quad[0][2])
                v = (quad[3][0] - quad[0][0], quad[3][1] - quad[0][1], quad[3][2] - quad[0][2])
                axis = {"x": 0, "y": 1, "z": 2}[ax]
                along, across = (u, v) if abs(u[axis]) >= abs(v[axis]) else (v, u)
                n = max(3, int(math.hypot(*across) / 9) + 2)
                for i in range(n):
                    t = (i + random.uniform(-0.3, 0.3)) / n
                    p1 = [quad[0][j] + across[j] * t for j in range(3)]
                    seg = []
                    for s_ in range(0, 21):
                        tt = s_ / 20
                        wob = math.sin(tt * 6 + i) * 0.012
                        seg.append(proj([p1[j] + along[j] * tt + across[j] * wob for j in range(3)], sc, ox, oy))
                    lg.line(seg, fill=shade(base, k * random.uniform(0.82, 0.95)), width=max(1, int(S * random.uniform(0.8, 1.8))))
            img.paste(lay, (0, 0), mask)
        g.line(poly + [poly[0]], fill=(214, 72, 30) if (hl is not None and bi in hl) else shade(base, k * 0.62), width=S * (2 if (hl is not None and bi in hl) else 1))
    img = img.resize(size, Image.LANCZOS)
    if label:
        dr = ImageDraw.Draw(img)
        try:
            f = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 30)
            f2 = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 20)
        except OSError:
            f = f2 = ImageFont.load_default()
        dr.text((40, 34), label, fill=(40, 34, 28), font=f)
        dr.text((40, 76), "완성 모습 그림 · 영진종합목재 www.wwood.co.kr", fill=(120, 108, 92), font=f2)
    if out: save_c(wmark(img), out, 86)
    return img


def rows(n, x0, y0, z, L, wd, gap, th, m, along="x"):
    out = []
    for i in range(n):
        if along == "x": out.append(B(x0, y0 + i * (wd + gap), z, L, wd, th, m))
        else: out.append(B(x0 + i * (wd + gap), y0, z, wd, L, th, m))
    return out


def box_cab(W, D, H, t, m, shelves=(), back="mdf6", top_over=0):
    """옆판 2 + 천판/지판 + 선반 + 뒷판(뒤쪽 y=0)"""
    b = [B(0, 0, 0, t, D, H, m), B(W - t, 0, 0, t, D, H, m), B(t, 0, 0, W - 2 * t, D, t, m), B(t, 0, H - t, W - 2 * t, D, t, m)]
    for z in shelves: b.append(B(t, 6, z, W - 2 * t, D - 6, t, m))
    if back: b.insert(0, B(0, 0, 0, W, 6, H, back))
    return b


def table(L, Wd, H, top_m, leg_m, leg=89, boards=None, frame=True, fm="bangbu"):
    b = []
    for (x, y) in [(0, 0), (L - leg, 0), (0, Wd - leg), (L - leg, Wd - leg)]:
        b.append(B(x, y, 0, leg, leg, H - 25 - (89 if frame else 0) + (89 if frame else 0) - 0, leg_m))
    if frame:
        b += [B(0, 0, H - 25 - 89, L, 38, 89, fm), B(0, Wd - 38, H - 25 - 89, L, 38, 89, fm)]
    b += boards if boards is not None else [B(0, 0, H - 25, L, Wd, 25, top_m)]
    return b


MODELS = {}
# 평상 1800×1200 h400
m = []
for (x, y) in [(0, 0), (1711, 0), (0, 1111), (1711, 1111), (855, 0), (855, 1111)]: m.append(B(x, y, 0, 89, 89, 375, "bangbu"))
m += [B(0, 0, 286, 1800, 38, 89, "bangbu"), B(0, 1162, 286, 1800, 38, 89, "bangbu")]
m += rows(8, 0, 5, 375, 1800, 140, 10, 25, "bangbu")
m += [B(89, 38, 286, 38, 1124, 89, "bangbu"), B(1673, 38, 286, 38, 1124, 89, "bangbu"), B(950, 38, 286, 38, 1124, 89, "bangbu")]
MODELS["pyeongsang"] = ("원목 평상 1800×1200", m)
MODELS["chaekjang"] = ("책장 800×300×1800", box_cab(800, 300, 1800, 18, "misong", shelves=[340, 680, 1020, 1360]))
# 텃밭상자 1200×600×280 + 흙
m = [B(0, 0, 0, 38, 38, 280, "bangbu"), B(1162, 0, 0, 38, 38, 280, "bangbu"), B(0, 562, 0, 38, 38, 280, "bangbu"), B(1162, 562, 0, 38, 38, 280, "bangbu"),
     B(38, 38, 0, 1124, 524, 230, "soil")]
for z in (0, 140):
    m += [B(0, 0, z, 1200, 38, 140, "bangbu"), B(0, 562, z, 1200, 38, 140, "bangbu"), B(0, 38, z, 38, 524, 140, "bangbu"), B(1162, 38, z, 38, 524, 140, "bangbu")]
m += [B(200 + i * 300, 200, 230, 90, 90, 120, "plant") for i in range(3)]
MODELS["tutbat"] = ("텃밭상자 1200×600", m)
# 작은 데크 2400×1800
m = [B(0, 0, 0, 2400, 38, 89, "bangbu"), B(0, 1762, 0, 2400, 38, 89, "bangbu")] + [B(i * 394, 38, 0, 38, 1724, 89, "bangbu") for i in range(7)]
m += rows(15, 0, 0, 89, 1800, 140, 5, 25, "bangbu", along="y")
MODELS["deck"] = ("작은 데크 2400×1800", m)
# 가벽: 스터드 한쪽만 석고보드
m = [B(0, 0, 0, 2400, 89, 38, "gujo"), B(0, 0, 2362, 2400, 89, 38, "gujo")] + [B(i * 394, 0, 38, 38, 89, 2324, "gujo") for i in range(7)]
m += [B(0, 89, 0, 900, 10, 1800, "gyp"), B(0, 89, 1800, 900, 10, 600, "gyp")]
MODELS["gabyeok"] = ("가벽 틀 2400×2400 (석고보드 붙이는 중)", m)
# 벽선반 3단 + 벽
m = [B(0, 0, 0, 1000, 20, 1200, "gyp")]
for z in (250, 600, 950):
    m += [B(150, 20, z - 120, 20, 180, 120, "metal"), B(830, 20, z - 120, 20, 180, 120, "metal"), B(100, 20, z, 800, 200, 18, "misong")]
MODELS["byeokseonban"] = ("벽선반 800×200 3단", m)
# 울타리
m = [B(i * 1800, 0, 0, 89, 89, 1200, "bangbu") for i in range(3)]
m += [B(0, 89, 200, 3689, 38, 89, "bangbu"), B(0, 89, 1000, 3689, 38, 89, "bangbu")]
m += [B(40 + i * 170, 127, 50, 120, 20, 1190, "bangbu") for i in range(21)]
MODELS["ultari"] = ("목재 울타리 3.6m", m)
# 원목 테이블 1200×600 철제다리
m = [B(x, y, 0, 40, 40, 690, "metal") for x, y in [(60, 60), (1100, 60), (60, 500), (1100, 500)]]
m += [B(60, 100, 150, 1080, 400, 30, "rubber"), B(0, 0, 690, 1200, 600, 30, "rubber")]
MODELS["teibeul"] = ("원목 테이블 1200×600", m)
MODELS["sinbaljang"] = ("신발장 900×350×1000", box_cab(900, 350, 1000, 18, "misong", shelves=[190, 380, 570, 760]))
# 벤치
m = [B(x, y, 0, 89, 89, 425, "bangbu") for x, y in [(38, 38), (1373, 38), (38, 313), (1373, 313)]]
m += [B(0, 0, 336, 1500, 38, 89, "bangbu"), B(0, 402, 336, 1500, 38, 89, "bangbu")] + rows(3, 0, 0, 425, 1500, 140, 10, 25, "bangbu")
MODELS["benchi"] = ("원목 벤치 1500", m)
# 침대
m = [B(x, y, 0, 89, 38, 200, "gujo") for x, y in [(40, 40), (1450, 40), (40, 1950), (1450, 1950)]]
m += [B(0, 0, 60, 38, 2040, 140, "gujo"), B(1538, 0, 60, 38, 2040, 140, "gujo"), B(38, 0, 60, 1500, 38, 140, "gujo"), B(38, 2002, 60, 1500, 38, 140, "gujo")]
m += [B(38, 38, 200, 1500, 1964, 18, "hapan"), B(60, 60, 218, 1456, 1920, 220, "gyp")]
m += [B(38, 300 + i * 360, 111, 1500, 38, 89, "gujo") for i in range(5)]
MODELS["chimdae"] = ("평상형 침대 프레임 (퀸)", m)
# 작업대
m = [B(x, y, 0, 38, 89, 812, "gujo") for x, y in [(0, 0), (1762, 0), (0, 511), (1762, 511)]]
m += [B(0, 0, 150, 1800, 38, 89, "gujo"), B(0, 562, 150, 1800, 38, 89, "gujo"), B(38, 38, 239, 1724, 524, 18, "hapan")]
m += [B(0, 0, 723, 1800, 38, 89, "gujo"), B(0, 562, 723, 1800, 38, 89, "gujo"), B(0, 0, 812, 1800, 600, 18, "hapan")]
MODELS["jakeopdae"] = ("목공 작업대 1800×600", m)
MODELS["monitor"] = ("모니터 받침대 600×250", [B(0, 0, 0, 18, 250, 82, "acacia"), B(582, 0, 0, 18, 250, 82, "acacia"), B(0, 0, 82, 600, 250, 18, "acacia")])
# 베란다 선반
m = [B(x, y, 0, 38, 89, 1800, "gujo") for x, y in [(0, 0), (1162, 0), (0, 361), (1162, 361)]]
for z in (100, 600, 1100, 1600):
    m += [B(0, 89, z, 1200, 38, 89, "gujo"), B(0, 323, z, 1200, 38, 89, "gujo"), B(0, 0, z + 89, 1200, 450, 18, "hapan")]
MODELS["beranda"] = ("베란다 수납 선반 4단", m)
# 벽 단열 (다루끼 + 아이소핑크 + 일부 석고)
m = [B(0, 0, 0, 3000, 20, 2400, "gyp"), B(0, 20, 0, 3000, 30, 30, "daru"), B(0, 20, 2370, 3000, 30, 30, "daru")]
m += [B(i * 371, 20, 30, 30, 30, 2340, "daru") for i in range(9)]
m += [B(30 + i * 371, 20, 30, 341, 30, 2340, "pink") for i in range(5)] + [B(0, 50, 0, 1100, 10, 2400, "gyp")]
MODELS["dannyeolbyeok"] = ("벽 단열 — 다루끼 + 아이소핑크 + 석고보드", m)
MODELS["saideu"] = ("사이드테이블 450×400×500", [B(0, 0, 0, 18, 400, 482, "acacia"), B(432, 0, 0, 18, 400, 482, "acacia"), B(18, 0, 80, 414, 400, 18, "acacia"), B(0, 0, 482, 450, 400, 18, "acacia")])
MODELS["hyeongwanbench"] = ("현관 수납 벤치 900", box_cab(900, 350, 450, 18, "misong") )
# 강아지집
m = [B(x, y, 0, 38, 38, 100, "bangbu") for x, y in [(0, 0), (762, 0), (0, 562), (762, 562)]]
m += [B(0, 0, 100, 800, 12, 600, "hapan"), B(0, 12, 100, 12, 576, 600, "hapan"), B(788, 12, 100, 12, 576, 600, "hapan"), B(12, 12, 100, 776, 576, 12, "hapan")]
m += [B(0, 588, 100, 250, 12, 600, "hapan"), B(550, 588, 100, 250, 12, 600, "hapan"), B(250, 588, 500, 300, 12, 200, "hapan")]
m += [B(-50, -50, 700, 900, 700, 12, "hapan")]
MODELS["gaejip"] = ("강아지집 800×600", m)
# 화분대 3단
m = []
for x in (0, 862):
    m += [B(x, 0, 0, 38, 750, 89, "bangbu"), B(x, 0, 0, 38, 89, 900, "bangbu"), B(x, 250, 0, 38, 89, 600, "bangbu"), B(x, 500, 0, 38, 89, 300, "bangbu")]
for i, z in enumerate((900, 600, 300)):
    m += rows(2, 0, i * 250 - 0, z, 900, 120, 10, 25, "bangbu")
    m += [B(150, i * 250 + 30, z + 25, 160, 160, 170, "wood2"), B(500, i * 250 + 30, z + 25, 160, 160, 170, "wood2"), B(170, i * 250 + 50, z + 195, 120, 120, 90, "plant")]
MODELS["hwabundae"] = ("계단식 화분대 3단", m)
MODELS["aichaeksang"] = ("아이 책상 1000×550", [B(0, 0, 0, 18, 550, 582, "acacia"), B(982, 0, 0, 18, 550, 582, "acacia"), B(18, 0, 382, 964, 18, 200, "acacia"), B(0, 0, 582, 1000, 550, 18, "acacia")])
MODELS["geosiljang"] = ("TV 거실장 1500×400", box_cab(1500, 400, 450, 18, "misong") + [B(741, 6, 18, 18, 394, 414, "misong")])
MODELS["seutul"] = ("원목 스툴 300×300", [B(0, 0, 0, 18, 300, 432, "acacia"), B(282, 0, 0, 18, 300, 432, "acacia"), B(18, 110, 120, 264, 18, 80, "acacia"), B(0, 0, 432, 300, 300, 18, "acacia")])
m = [B(x, y, 0, 89, 89, 800, "bangbu") for x, y in [(0, 0), (1111, 0), (0, 511), (1111, 511)]]
m += [B(0, 0, 520, 1200, 38, 280, "bangbu"), B(0, 562, 520, 1200, 38, 280, "bangbu"), B(0, 38, 520, 38, 524, 280, "bangbu"), B(1162, 38, 520, 38, 524, 280, "bangbu"),
      B(38, 38, 520, 1124, 524, 240, "soil")] + [B(200 + i * 300, 200, 760, 90, 90, 120, "plant") for i in range(3)]
MODELS["nopeuntutbat"] = ("다리 달린 텃밭상자", m)
MODELS["haenggeo"] = ("원목 옷걸이 행거 1000", [B(0, 0, 0, 45, 500, 45, "spruce"), B(955, 0, 0, 45, 500, 45, "spruce"), B(0, 228, 45, 45, 45, 1600, "spruce"), B(955, 228, 45, 45, 45, 1600, "spruce"), B(0, 228, 1600, 1000, 45, 45, "spruce")])
m = [B(x, y, 0, 89, 89, 695, "bangbu") for x, y in [(40, 40), (1371, 40), (40, 611), (1371, 611)]]
m += [B(0, 0, 606, 1500, 38, 89, "bangbu"), B(0, 702, 606, 1500, 38, 89, "bangbu")] + rows(5, 0, 0, 695, 1500, 140, 10, 25, "bangbu")
MODELS["yaoeteibeul"] = ("야외 테이블 1500×740", m)
m = [B(0, 0, 0, 1200, 89, 38, "bangbu"), B(0, 400, 0, 1200, 89, 38, "bangbu")] + [B(x, y, 38, 38, 89, 1000, "bangbu") for x, y in [(0, 0), (1162, 0), (0, 400), (1162, 400)]]
m += [B(0, 0, 1000, 1200, 89, 38, "bangbu"), B(0, 400, 1000, 1200, 89, 38, "bangbu")]
for i in range(5):
    for j in range(4): m.append(B(50 + j * 280, 40, 38 + i * 160, 260, 420, 150, "wood2"))
MODELS["jangjak"] = ("장작 보관대 1200", m)
m = [B(0, 0, 0, 1220, 20, 1300, "gyp"), B(0, 20, 100, 1200, 30, 30, "daru"), B(0, 20, 600, 1200, 30, 30, "daru"), B(0, 20, 1100, 1200, 30, 30, "daru"), B(0, 50, 50, 1220, 11, 1200, "osb")]
m += [B(150, 61, 800, 30, 120, 30, "metal"), B(350, 61, 800, 30, 120, 30, "metal"), B(600, 61, 700, 200, 150, 18, "misong"), B(150, 61, 400, 300, 60, 40, "metal")]
MODELS["gongguborad"] = ("공구 정리 벽판 1200×1220", m)
m = []
for (x, z) in [(0, 0), (360, 0), (0, 360), (720, 0)]:
    m += [B(x, 0, z, 350, 6, 350, "mdf6"), B(x, 0, z, 15, 350, 350, "mdf"), B(x + 335, 0, z, 15, 350, 350, "mdf"), B(x + 15, 0, z, 320, 350, 15, "mdf"), B(x + 15, 0, z + 335, 320, 350, 15, "mdf")]
MODELS["cube"] = ("수납 큐브 350 × 4개", m)


# ── 자재 시공법(sigong_data.SG) 그림 ──
SGM = {}
def _wall(W, H, t=100): return [B(0, -t, 0, W, t, H, "conc")]
m = _wall(3000, 2400) + [B(0, 0, 0, 3000, 30, 30, "daru"), B(0, 0, 2370, 3000, 30, 30, "daru")] + [B(i * 424, 0, 30, 30, 30, 2340, "daru") for i in range(8)]
for x in (0, 900, 1800, 2700):
    w = min(900, 3000 - x); m += [B(x, 30, 0, w, 10, 1800, "gyp"), B(x, 30, 1800, w, 10, 600, "gyp")]
m += [B(x - 25, 40, 0, 50, 1, 2400, "putty") for x in (900, 1800, 2700)]
SGM["seokgo-byeok"] = ("석고보드 벽 3.0×2.4m", m, "0:3|3:11|11:19|19:22")
m = [B(0, 0, -100, 3000, 3000, 100, "conc")] + [B(0, 30 + i * 360, 0, 3000, 30, 30, "daru") for i in range(9)]
m += [B(0, i * 100, 30, 3000, 100, 10, "hinoki") for i in range(30)]
m += [B(-20, -20, 40, 3040, 20, 40, "white"), B(-20, 0, 40, 20, 3000, 40, "white")]
SGM["rubaa-cheonjang"] = ("루바 천장 3.0×3.0m (아래에서 본 모습)", m, "0:10|10:12|12:39|39:42")
m = _wall(4000, 2400) + [B(0, 0, 0, 4000, 2, 2400, "wrap")] + [B(i * 440, 2, 0, 38, 38, 2400, "bangbu") for i in range(10)]
m += [B(0, 40, 0, 4000, 10, 60, "metal")] + [B(0, 40 + 0, 40 + i * 200, 4000, 8, min(230, 2400 - 40 - i * 200), "siding") for i in range(12)]
SGM["siding-oebyeok"] = ("외벽 시멘트 사이딩 4.0×2.4m", m, "0:2|2:12|12:14|14:25")
m = [B(0, 0, -40, 3600, 3000, 40, "maru"), B(0, 0, 0, 3600, 20, 2400, "white"), B(0, 0, 0, 20, 3000, 2400, "white")]
m += [B(20, 20, 0, 3580, 9, 90, "wood2"), B(20, 29, 0, 9, 2971, 90, "wood2"), B(20, 20, 2340, 3580, 40, 60, "wood2"), B(20, 60, 2340, 40, 2940, 60, "wood2")]
SGM["molding-georebatgi"] = ("걸레받이·천장 몰딩", m, "0:3|3:5|5:7|*")
m = [B(0, 0, -60, 3600, 3000, 60, "conc"), B(0, -20, 0, 3600, 20, 1200, "white"), B(-20, -20, 0, 20, 3020, 1200, "white")]
for r in range(15):
    off = 0 if r % 2 == 0 else 600; x = -off; k = 0
    while x < 3600:
        L = 1200 if (x + 1200) <= 3600 else 3600 - x
        if x < 0: L = 1200 + x; x = 0
        m.append(B(x, 10 + r * 198, 0, L - 2, 196, 8, "maru")); x += L; k += 1
nb = len(m)
m += [B(0, 0, 8, 3600, 9, 80, "white"), B(0, 9, 8, 9, 2991, 80, "white")]
SGM["gangmaru"] = ("강마루 바닥 시공", m, f"0:3|3:12|12:{nb}|{nb}:{nb + 2}")
m = _wall(3000, 2400)
for p_ in range(3):
    w = 1200 if p_ < 2 else 600
    for j in range(w // 30):
        m.append(B(p_ * 1200 + j * 30, 0, 30, 24, 12, 2340, "tempa")); m.append(B(p_ * 1200 + j * 30 + 24, 0, 30, 6, 6, 2340, "tempa2"))
n1 = 1 + 80; n2 = 1 + 160
m += [B(0, 0, 0, 3000, 18, 30, "wood2"), B(0, 0, 2370, 3000, 18, 30, "wood2")]
SGM["tempa-byeok"] = ("템바보드 포인트 벽", m, f"0|1:{n1}|{n1}:{len(m) - 2}|{len(m) - 2}:{len(m)}")
m = _wall(3600, 2400) + [B(i * 395, 0, 0, 30, 30, 2400, "daru") for i in range(10)]
m += [B(i * 395 + 30, 0, 0, 365, 28, 2400, "pink") for i in range(9)]
m += [B(x, 30, 0, 1200, 9, 2400, "acoustic") for x in (0, 1200, 2400)]
m += [B(0, 39, 0, 3600, 12, 40, "wood2"), B(0, 39, 2360, 3600, 12, 40, "wood2")]
SGM["heumeum-byeok"] = ("흡음 타공판 벽", m, "0:11|11:20|20:22|22:25")
m = [B(0, i * 375, 0, 2400, 38, 89, "bangbu") for i in range(9)]
m += [B(i * 145 - 0, -20, 89, 140, 3040, 20, "hapdeck") for i in range(17)]
m += [B(-40, -60, 69, 40, 3120, 40, "hapdeck"), B(2425, -60, 69, 40, 3120, 40, "hapdeck")]
SGM["hapdeck-sigong"] = ("합성데크 2.4×3.0m", m, "0:9|9:10|10:26|26:28")
m = [B(0, 0, 0, 600, 130, 2400, "gyp"), B(1500, 0, 0, 600, 130, 2400, "gyp"), B(600, 0, 2100, 900, 130, 300, "gyp")]
m += [B(605, -5, 0, 40, 140, 2095, "white"), B(1455, -5, 0, 40, 140, 2095, "white"), B(605, -5, 2055, 890, 140, 40, "white")]
m += [B(600, 20, 0, 5, 90, 2100, "foam"), B(1495, 20, 0, 5, 90, 2100, "foam"), B(600, 20, 2095, 900, 90, 5, "foam")]
m += [B(648, 95, 3, 804, 38, 2048, "white"), B(1380, 133, 1000, 20, 60, 20, "metal")]
SGM["munteul-gyoche"] = ("방문·문틀 교체", m, "0:3|3:6|6:9|9:11")
m = [B(0, 0, 0, 900, 40, 2100, "white"), B(0, 40, 1050, 900, 1, 1050, "wood2"), B(0, 40, 0, 900, 1, 1050, "wood2"), B(780, 41, 1000, 80, 40, 20, "metal")]
SGM["film-sigong"] = ("인테리어 필름 — 문짝", m, "0|0|1|2:4")
m = [B(0, i * 400, 0, 2400, 38, 89, "bangbu") for i in range(9)]
bb = [B(i * 145, -20, 89, 140, 3260, 25, "bangbu") for i in range(17)]
m += bb + [B(i * 145, -20, 114, 140, 3260, 1, "stained") for i in range(17)]
SGM["oilstain"] = ("오일스테인 칠하기 — 데크", m, f"0:26|26:31|31:43|*")
m = _wall(3600, 2400) + [B(i * 395, 0, 0, 30, 30, 2400, "daru") for i in range(10)]
m += [B(0, 30, 0, 1220, 11, 2400, "osb"), B(1223, 30, 0, 1220, 11, 2400, "osb"), B(2446, 30, 0, 1154, 11, 2400, "osb")]
SGM["osb-byeok"] = ("OSB 벽 마감", m, "0:11|11|12|13")

m = [B(x, y, 0, 45, 45, 1500, "spruce") for x, y in [(0, 0), (755, 0), (0, 255), (755, 255)]]
m += [B(45, 0, z, 710, 45, 45, "spruce") for z in (100, 460, 820, 1180, 1455)] + [B(45, 255, z, 710, 45, 45, "spruce") for z in (100, 460, 820, 1180, 1455)]
m += [B(45, 0, z + 45, 710, 300, 18, "misong") for z in (100, 460, 820, 1180)]
MODELS["sadariseonban"] = ("원목 사다리 선반 800×300×1500", m)
m = [B(0, 0, 0, 18, 600, 870, "misong"), B(1182, 0, 0, 18, 600, 870, "misong"), B(18, 582, 0, 1164, 18, 60, "misong"), B(18, 6, 0, 1164, 18, 60, "misong"),
     B(18, 6, 60, 1164, 594, 18, "misong"), B(18, 6, 450, 1164, 594, 18, "misong"), B(18, 0, 0, 1164, 6, 870, "mdf6"), B(0, 0, 870, 1200, 600, 30, "rubber")]
MODELS["aillaendeu"] = ("아일랜드 작업대 1200×600×900", m)

STEPS = {"pyeongsang": "6:8,16:19|0:6|8:16|*", "chaekjang": "1:5|5:9|0|*", "tutbat": "0:4,7:9,11:13|5:7,9:11|4,13:16", "deck": "0:2|2:9|9:24|*",
         "gabyeok": "0:2|2:9|9:11|*", "byeokseonban": "0|1:3,4:6,7:9|3,6,9|*", "ultari": "0:3|3:5|5:26|*", "teibeul": "5|0:4|4|*",
         "sinbaljang": "1:5|5:9|0|*", "benchi": "4:6|0:4|6:9|*", "chimdae": "4:8|10:15|0:4|8:10", "jakeopdae": "4:6,7:9|0:4|6|9",
         "monitor": "0:2|2|*|*", "beranda": "0:4|4:6,7:9,10:12,13:15|6,9,12,15|*", "dannyeolbyeok": "1:3|3:12|12:17|17", "saideu": "0:3|3|*|*",
         "hyeongwanbench": "1:4|4|0|*", "gaejip": "8:11|4:8|0:4|11", "hwabundae": "0:8|8:10|13:15,18:20|10:13,15:18,20:23", "aichaeksang": "0:3|3|*|*",
         "geosiljang": "1:4,5|4|0|*", "seutul": "0:2|2|3|*", "nopeuntutbat": "4:8|0:4|8|9:12", "haenggeo": "0:4|4|*|*", "yaoeteibeul": "4:6|0:4|6:11|*",
         "jangjak": "0:2|2:6|6:8|8:28", "gongguborad": "1:4|4|5:9|*", "cube": "1:5|0|5:20|*",
         "sadariseonban": "0,1,4:9|2,3,9:14|14:18|*", "aillaendeu": "0:4|4:6|6|*"}


def _idx(spec, n):
    if spec == "*": return set(range(n))
    out = set()
    for part in spec.split(","):
        if ":" in part: a, b = part.split(":"); out |= set(range(int(a), int(b)))
        else: out.add(int(part))
    return out


def mk_steps_text(root):
    import ast
    src = open(os.path.join(root, "build.py"), encoding="utf-8").read()
    i = src.find("    MK = ["); j = src.find("\n    ]\n", i)
    lst = ast.literal_eval(src[i + 9:j + 6].strip())
    return {x[0]: (x[1], x[5]) for x in lst}


def render_steps(slug, boxes, out, title, caps, spec):
    parts = spec.split("|"); n = len(boxes)
    shown = set(); panels = []
    for k, sp in enumerate(parts):
        new = _idx(sp, n); shown |= new
        sub = [boxes[i] for i in sorted(shown)]
        hl = None if sp == "*" else {sorted(shown).index(i) for i in new}
        panels.append(render(slug + str(k), sub, None, "", hl, (600, 400)))
    cols = 2; rows_ = (len(panels) + 1) // 2
    W, H = 1200, 70 + rows_ * 470
    img = Image.new("RGB", (W, H), (250, 247, 241)); dr = ImageDraw.Draw(img)
    fb = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"; fr = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    F = lambda p, z: ImageFont.truetype(p, z)
    dr.text((30, 18), title if title.endswith("순서") else f"{title} 만드는 순서", fill=(40, 34, 28), font=F(fb, 30))
    for k, pnl in enumerate(panels):
        x0 = (k % cols) * 600; y0 = 70 + (k // cols) * 470
        img.paste(pnl, (x0, y0))
        dr.ellipse([x0 + 16, y0 + 12, x0 + 60, y0 + 56], fill=(200, 16, 26)); dr.text((x0 + 38, y0 + 34), str(k + 1), fill="white", font=F(fb, 26), anchor="mm")
        cap = caps[k] if k < len(caps) else ""
        lines, cur = [], ""
        for ch in cap:
            if dr.textlength(cur + ch, font=F(fr, 19)) > 560: lines.append(cur); cur = ch
            else: cur += ch
        if cur: lines.append(cur)
        for li, t in enumerate(lines[:3]): dr.text((x0 + 20, y0 + 400 + li * 23), t, fill=(60, 52, 44), font=F(fr, 19))
    dr.line([(600, 70), (600, H)], fill=(225, 218, 205), width=2)
    for r in range(1, rows_): dr.line([(0, 70 + r * 470), (W, 70 + r * 470)], fill=(225, 218, 205), width=2)
    dr.text((W - 20, H - 14), "영진종합목재 www.wwood.co.kr", fill=(150, 138, 120), font=F(fr, 16), anchor="rs")
    save_c(wmark(img), out, 84)


if __name__ == "__main__":
    root = os.path.dirname(os.path.abspath(__file__))
    od = os.path.join(root, "assets", "mandeul"); os.makedirs(od, exist_ok=True)
    only = set(sys.argv[1:])
    TXT = mk_steps_text(root)
    sys.path.insert(0, root)
    from sigong_data import SG as _SG
    SGT = {x[0]: x[6] for x in _SG}
    od2 = os.path.join(root, "assets", "sigongbeop"); os.makedirs(od2, exist_ok=True)
    for slug, (label, boxes, spec) in SGM.items():
        if only and slug not in only: continue
        render(slug, boxes, os.path.join(od2, slug + ".jpg"), label)
        render_steps(slug, boxes, os.path.join(od2, slug + "-steps.jpg"), label.split(" — ")[0].split(" (")[0] + " 순서", SGT.get(slug, []), spec)
        print("ok", slug)
    for slug, (label, boxes) in MODELS.items():
        if only and slug not in only: continue
        render(slug, boxes, os.path.join(od, slug + ".jpg"), label)
        if slug in STEPS and slug in TXT:
            render_steps(slug, boxes, os.path.join(od, slug + "-steps.jpg"), TXT[slug][0], TXT[slug][1], STEPS[slug])
        print("ok", slug)
