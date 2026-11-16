#!/usr/bin/env python3
# 떨이몰 상품 등록·판매완료 처리.
#   등록: python3 add_tteori.py --title "방부목 2×4 자투리" --size "38×89×1200" --qty "20개" --price 2000 --unit 개 --note "약간 갈라짐" 사진1.jpg 사진2.jpg
#   판매완료: python3 add_tteori.py --sold 20261116-1
#   다시 판매중: python3 add_tteori.py --onsale 20261116-1
# 사진: 회전 바로잡기 → 긴 변 1200px → 위치정보(EXIF) 지움 → 오른쪽 아래 '영진종합목재 www.wwood.co.kr' 표시
import argparse, datetime, os, sys
from PIL import Image, ImageOps, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(ROOT, "data", "tteori.tsv")
IMG = os.path.join(ROOT, "assets", "tteori")
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def clean(s): return (s or "").replace("|", "/").replace("\n", " ").strip()


def photo(src, dst):
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    im.thumbnail((1200, 1200))
    d = ImageDraw.Draw(im, "RGBA"); w, h = im.size; fs = max(16, w // 34)
    try: f = ImageFont.truetype(FONT, fs)
    except Exception: f = ImageFont.load_default()
    t = "영진종합목재 www.wwood.co.kr"; bb = d.textbbox((0, 0), t, font=f); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x, y, p = w - tw - fs, h - th - fs, fs // 3
    d.rounded_rectangle((x - p, y - p, x + tw + p, y + th + p * 2), radius=p, fill=(0, 0, 0, 110))
    d.text((x, y), t, font=f, fill=(255, 255, 255, 230))
    im.save(dst, "JPEG", quality=82, optimize=True)  # EXIF 없이 저장 → 위치정보 안 남음


def rows():
    return [l.rstrip("\n").split("|") for l in open(TSV, encoding="utf-8") if l.strip() and not l.startswith("#")] if os.path.exists(TSV) else []


def write(rs):
    with open(TSV, "w", encoding="utf-8") as f:
        f.write("# id|등록일|제목|규격|수량|가격|단위|설명|사진|상태\n")
        for r in rs: f.write("|".join((r + [""] * 10)[:10]) + "\n")


ap = argparse.ArgumentParser()
ap.add_argument("--title"); ap.add_argument("--size", default=""); ap.add_argument("--qty", default=""); ap.add_argument("--price", default="")
ap.add_argument("--unit", default=""); ap.add_argument("--note", default=""); ap.add_argument("--date", default="")
ap.add_argument("--sold"); ap.add_argument("--onsale"); ap.add_argument("photos", nargs="*")
a = ap.parse_args()
rs = rows()
if a.sold or a.onsale:
    tid = a.sold or a.onsale; hit = False
    for r in rs:
        if r[0] == tid: r += [""] * (10 - len(r)); r[9] = "판매완료" if a.sold else "판매중"; hit = True
    if not hit: sys.exit("그 번호가 없어요: " + tid)
    write(rs); print("바꿈:", tid); sys.exit()
if not a.title: sys.exit("--title 이 필요해요")
price = "".join(ch for ch in a.price if ch.isdigit())
day = a.date or datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d")
base = day.replace("-", ""); n = 1
while any(r[0] == f"{base}-{n}" for r in rs): n += 1
tid = f"{base}-{n}"
os.makedirs(IMG, exist_ok=True); names = []
for k, p in enumerate(a.photos):
    nm = f"{tid}-{k + 1}.jpg"; photo(p, os.path.join(IMG, nm)); names.append(nm)
rs.append([tid, day, clean(a.title), clean(a.size), clean(a.qty), price, clean(a.unit), clean(a.note), ",".join(names), "판매중"])
write(rs)
print("등록:", tid, a.title, (price + "원") if price else "매장 문의", len(names), "장")
