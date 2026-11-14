# 삼익산업(siwood.com — 회사 허락) 제품 사진·이름·규격 → src/data/samik.tsv (1차|2차|idx|이름|사진|브랜드·두께|규격 설명)
import re, html, sys, time, urllib.request, urllib.parse
B = "https://www.siwood.com"
TOP = {"1561097791": "구조재", "1558068431": "외장재", "1558068439": "지붕재", "1558512838": "내장재", "1558512823": "창호", "1561439870": "도어", "1558512834": "기능재", "1561450066": "조경", "1558512844": "기타"}
def req(u, data=None):
    for i in range(3):
        try:
            r = urllib.request.Request(B + u, data=data.encode() if data else None, headers={"User-Agent": "Mozilla/5.0 wwood.co.kr catalog sync", "Content-Type": "application/x-www-form-urlencoded"})
            return urllib.request.urlopen(r, timeout=30).read().decode("utf-8", "replace")
        except Exception as e: err = e; time.sleep(3)
    raise err
T = lambda s: re.sub(r"[ \t]+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
rows, seen = [], set()
for tc, tn in TOP.items():
    subs = re.findall(r'value="(\d+)"[\s\S]*?<label[^>]*>([^<]*)<', req("/_lib/getSubCategory_MOBILE.asp", f"catecode={tc}&depth=1")) or [(tc, tn)]
    for sc, sn in subs:
        for pg in range(1, 40):
            t = req("/product/ajax_productList.asp", f"page={pg}&sercatecode={sc}")
            new = 0
            for idx in dict.fromkeys(re.findall(r"product_view\.asp\?idx=(\d+)", t)):
                if idx in seen: continue
                seen.add(idx); new += 1; rows.append([tn, sn.strip(), idx])
            if new == 0: break
            time.sleep(0.2)
        print(tn, sn, file=sys.stderr)
out = []
for tn, sn, idx in rows:
    try: h = req(f"/product/product_view.asp?idx={idx}")
    except Exception: continue
    ti = re.search(r'<div class="title">([\s\S]*?)</div>', h)
    tx = re.search(r'<div class="text">([\s\S]*?)</div>', h)
    im = re.search(r'<div class="imgArea"><img src="([^"]+)"', h)
    if not (ti and im): continue
    name = T(ti.group(1))
    lines = [T(x) for x in re.split(r"<br\s*/?>", tx.group(1), flags=re.I)] if tx else []
    lines = [x for x in lines if x and x != name]
    brand = next((x for x in lines if "ㅣ" in x and ":" not in x), "")
    spec = " / ".join(x for x in lines if x != brand)
    out.append("|".join(v.replace("|", "/") for v in [tn, sn, idx, name, im.group(1), brand, spec[:300]]))
    time.sleep(0.15)
if len(out) < 100: sys.exit(f"too few {len(out)}")
open("src/data/samik.tsv", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("rows", len(out), file=sys.stderr)
