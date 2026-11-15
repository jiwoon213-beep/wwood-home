# 공사 미리보기용: 쇼핑몰 제품 사진(데크·루바·아트월·사이딩·타일)의 대표 색을 뽑아 src/data/prodcolor.json 에 저장
import io, json, os, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
CATS = {"deck": ("25/144", "25/145", "25/146", "25/147"), "ruba": ("27/156", "23/137", "27/163"),
        "tempa": ("27/161", "27/321", "27/157", "27/159", "27/160", "27/237", "27/166", "27/322", "24/319", "24/320"),
        "maru": ("26/148", "26/247", "26/315", "23/136"), "siding": ("31/186", "31/188"), "tile": ("28/",)}
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
os.makedirs("src/assets/mt", exist_ok=True)
def tile(pid, im):
    # 무늬 조각: 가운데(워터마크 자리)는 피하고, 네 귀퉁이 중 흰 배경이 없고 가장 고른 곳을 잘라 저장
    w, h = im.size
    g = im.convert("L").resize((64, int(64 * h / w) or 1))
    gw, gh = g.size; px = g.load()
    xs = [x for x in range(gw) if any(px[x, y] < 235 for y in range(gh))]
    ys = [y for y in range(gh) if any(px[x, y] < 235 for x in range(gw))]
    if not xs or not ys: return
    bx0, bx1, by0, by1 = min(xs) / gw * w, (max(xs) + 1) / gw * w, min(ys) / gh * h, (max(ys) + 1) / gh * h
    bw, bh = bx1 - bx0, by1 - by0
    best = None
    for fx, fy in ((.08, .08), (.54, .08), (.08, .54), (.54, .54), (.31, .06), (.31, .58)):
        box = (int(bx0 + bw * fx), int(by0 + bh * fy), int(bx0 + bw * (fx + .38)), int(by0 + bh * (fy + .38)))
        c = im.crop(box).convert("L").resize((24, 24)); d = list(c.getdata())
        white = sum(1 for v in d if v > 235) / len(d)
        m = sum(d) / len(d); sd = (sum((v - m) ** 2 for v in d) / len(d)) ** .5
        sc = white * 200 + sd
        if best is None or sc < best[0]: best = (sc, box, white)
    if best[2] > .15: return
    t = im.crop(best[1]); t.thumbnail((256, 256))
    t.save(f"src/assets/mt/{pid}.jpg", "JPEG", quality=72, optimize=True)
def col(r):
    try:
        req = urllib.request.Request(r[2], headers={"User-Agent": "Mozilla/5.0"})
        im = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=20).read())).convert("RGB")
        w, h = im.size
        c = im.crop((int(w * .3), int(h * .3), int(w * .7), int(h * .7))).resize((24, 24))
        px = [p for p in c.getdata() if not (p[0] > 238 and p[1] > 238 and p[2] > 238)] or list(c.getdata())  # 흰 배경 빼고
        px.sort(key=sum); px = px[len(px) // 10: len(px) * 9 // 10] or px  # 너무 어둡고 밝은 점 빼기
        rgb = [sum(p[i] for p in px) // len(px) for i in range(3)]
        try: tile(r[0], im)
        except Exception: pass
        return r[0], {"m": r[1], "c": "#%02x%02x%02x" % tuple(rgb)}
    except Exception as e:
        return r[0], None
with ThreadPoolExecutor(8) as ex:
    out = {k: v for k, v in ex.map(col, rows) if v}
json.dump(out, open("src/data/prodcolor.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(rows), "items,", len(out), "colors")
