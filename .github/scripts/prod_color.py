# 공사 미리보기용: 쇼핑몰 제품 사진(데크·루바·아트월·사이딩·타일)의 대표 색을 뽑아 src/data/prodcolor.json 에 저장
import io, json, os, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
CATS = {"deck": ("25/144", "25/145", "25/146", "25/147"), "ruba": ("27/156",), "tempa": ("27/161",), "siding": ("31/186",), "tile": ("28/",)}
rows = []
for l in open("src/data/products.tsv", encoding="utf-8"):
    if l.startswith("#"): continue
    x = l.rstrip("\n").split("\t")
    if len(x) < 4: continue
    cs = x[3].split(",")
    m = next((k for k, v in CATS.items() if any(c.startswith(p) if p.endswith("/") else c == p for c in cs for p in v)), None)
    if not m: continue
    img = x[2].replace("@", "/common/ezs_data/product/", 1) if x[2].startswith("@") else x[2].replace("!", "/modules/shop/files/", 1) if x[2].startswith("!") else x[2]
    rows.append((x[0], m, "https://www.wwood.kr" + img))
def col(r):
    try:
        req = urllib.request.Request(r[2], headers={"User-Agent": "Mozilla/5.0"})
        im = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=20).read())).convert("RGB")
        w, h = im.size
        c = im.crop((int(w * .3), int(h * .3), int(w * .7), int(h * .7))).resize((24, 24))
        px = [p for p in c.getdata() if not (p[0] > 238 and p[1] > 238 and p[2] > 238)] or list(c.getdata())  # 흰 배경 빼고
        px.sort(key=sum); px = px[len(px) // 10: len(px) * 9 // 10] or px  # 너무 어둡고 밝은 점 빼기
        rgb = [sum(p[i] for p in px) // len(px) for i in range(3)]
        return r[0], {"m": r[1], "c": "#%02x%02x%02x" % tuple(rgb)}
    except Exception as e:
        return r[0], None
with ThreadPoolExecutor(8) as ex:
    out = {k: v for k, v in ex.map(col, rows) if v}
json.dump(out, open("src/data/prodcolor.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(rows), "items,", len(out), "colors")
