# 이몰링(본덱스코리아 온라인쇼핑몰, emalling.co.kr — 회사 허락) 상품 사진·이름·판매가·옵션 → src/data/emall.tsv, emall_cats.tsv
# 사이트 표시가 = 판매가 × 1.3, 100원 올림(src/emall.py). 같은 상품번호는 처음 나온 분류에만.
import re, html, json, sys, time, urllib.request, concurrent.futures as cf
B = "https://www.emalling.co.kr"
def get(u):
    err = None
    for i in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 wwood.co.kr catalog sync"}), timeout=30).read().decode("utf-8", "replace")
        except Exception as e: err = e; time.sleep(3)
    raise err
T = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
cats = json.loads(get(B + "/exec/front/Product/SubCategory"))
SKIP = {28, 78, 79, 90}
byno = {c["cate_no"]: c for c in cats}
kids = {}
for c in cats: kids.setdefault(c["parent_cate_no"], []).append(c["cate_no"])
order = []
def walk(p):
    for n in kids.get(p, []):
        if n in SKIP: continue
        order.append(n); walk(n)
walk(1)
rows, seen = [], set()
for n in order:
    if n in kids and any(k not in SKIP for k in kids[n]): continue
    for pg in range(1, 60):
        t = get(f"{B}/product/list.html?cate_no={n}&page={pg}")
        a = t.find("xans-product-listnormal"); b = t.find("xans-product-normalpaging", a)
        t = t[a:b if b > 0 else None] if a > 0 else ""
        new = 0
        for li in re.split(r'<li id="anchorBoxId_', t)[1:]:
            pno = re.match(r"(\d+)", li).group(1)
            im = re.search(r'/web/product/(?:medium|small|big|tiny)/([^"]+?\.(?:jpg|jpeg|png|gif|webp))"', li)
            nm = re.search(r'id="eListPrdImage\d+_\d+"[^>]*alt="([^"]*)"', li) or re.search(r'alt="([^"]+)"', li)
            pr = re.search(r'data-price="\^?(\d+)', li)
            if not (im and nm) or pno in seen: continue
            seen.add(pno); new += 1
            rows.append([n, pno, T(nm.group(1)).replace("|", "/"), im.group(1), pr.group(1) if pr else ""])
        if new == 0: break
        time.sleep(0.2)
    print(n, byno[n]["name"], file=sys.stderr)
if len(rows) < 50: sys.exit(f"too few {len(rows)}")
def det(r):
    try: h = get(f"{B}/product/detail.html?product_no={r[1]}")
    except Exception: return r[1], ["", ""]
    ops = []
    for sel in re.findall(r'<select[^>]*id="product_option_id\d+"[\s\S]*?</select>', h):
        tt = re.search(r'option_title="([^"]*)"', sel)
        vals = [T(x) for v, x in re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([\s\S]*?)</option>', sel) if v not in ("*", "**", "")]
        if vals: ops.append((T(tt.group(1)) if tt else "옵션") + ":" + ",".join(v.replace("|", "/").replace(";", " ").replace(":", " ") for v in vals[:40]))
    org = re.search(r'원산지</span></th>\s*<td><span[^>]*>([^<]*)<', h)
    return r[1], [";".join(ops), T(org.group(1)) if org else ""]
D = {}
with cf.ThreadPoolExecutor(4) as ex:
    for pno, v in ex.map(det, rows): D[pno] = v
open("src/data/emall.tsv", "w", encoding="utf-8").write("".join("|".join(map(str, r + D.get(r[1], ["", ""]))) + "\n" for r in rows))
open("src/data/emall_cats.tsv", "w", encoding="utf-8").write("".join(f'{n}|{byno[n]["parent_cate_no"]}|{byno[n]["name"]}\n' for n in order))
print("rows", len(rows), file=sys.stderr)
