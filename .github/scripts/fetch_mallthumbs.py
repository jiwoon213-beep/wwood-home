# 쇼핑몰(wwood.kr) 상품 사진을 작은 webp(가로 최대 480)로 받아 src/assets/mall/<id>.webp 에 저장 — 홈페이지 속도용
import os, io, sys, urllib.request
from PIL import Image
R = os.path.join(os.path.dirname(__file__), "..", "..", "src")
D = os.path.join(R, "assets", "mall"); os.makedirs(D, exist_ok=True)
n = ok = 0
for line in open(os.path.join(R, "data", "products.tsv"), encoding="utf-8"):
    r = line.rstrip("\n").split("\t")
    if r[0] == "#" or len(r) < 4 or not r[2]: continue
    out = os.path.join(D, r[0] + ".webp")
    if os.path.exists(out): continue
    p = r[2]
    p = p.replace("@", "/common/ezs_data/product/", 1) if p.startswith("@") else p.replace("!", "/modules/shop/files/", 1) if p.startswith("!") else p
    u = p if p.startswith("http") else "https://www.wwood.kr" + p
    n += 1
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 wwood-thumb"}), timeout=20).read()
        im = Image.open(io.BytesIO(b)); im.seek(0); im = im.convert("RGB")
        if im.width > 480: im = im.resize((480, round(im.height * 480 / im.width)), Image.LANCZOS)
        im.save(out, "WEBP", quality=72, method=6); ok += 1
    except Exception as e:
        print("fail", r[0], u, e)
print("tried", n, "saved", ok)
