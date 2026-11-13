# 철물박사(철물박사.com, 주식회사 철물박사 — 사용 허락) 전체 상품 사진·이름 → src/data/cmbs.tsv, src/data/cmbs_cats.tsv
# 가격: 철물박사 판매가를 그대로 저장(사이트에는 ×1.4, 100원 올림으로 표시 — src/cmbs.py). 같은 상품번호는 처음 나온 분류에만(중복 제거)
import re, html, json, sys, time, urllib.request, urllib.parse
B = "https://m.xn--392bopf4iwtp.com"
def get(u):
    for i in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (Linux; Android 13) wwood.co.kr catalog sync"}), timeout=30).read().decode("utf-8", "replace")
        except Exception as e: err = e; time.sleep(3)
    raise err
cats = json.loads(get(B + "/exec/front/Product/SubCategory"))
kids = {}
for c in cats: kids.setdefault(c["parent_cate_no"], []).append(c["cate_no"])
order = []
def walk(p):
    for n in kids.get(p, []):
        order.append(n); walk(n)
walk(1)
byno = {c["cate_no"]: c for c in cats}
SKIP = {374}
def under_skip(n):
    while n in byno:
        if n in SKIP: return True
        n = byno[n]["parent_cate_no"]
    return False
T = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
seen, rows = set(), []
for n in order:
    if n in kids or under_skip(n): continue
    got = 0
    for pg in range(1, 400):
        t = get(f"{B}/product/list.html?cate_no={n}&page={pg}")
        t = t.split("xans-product-listnormal", 1)[-1]
        new = 0
        for li in re.split(r'<div class="thumbnail">', t)[1:]:
            m = re.search(r'href="/product/[^"]*?/(\d+)/category/' + str(n) + "/", li)
            im = re.search(r'<img src="(?:https?:)?//[^/]+/web/product/(?:medium|small|big|tiny)/([^"]+)"', li)
            nm = re.search(r'<strong class="name[^"]*">([\s\S]*?)</strong>', li)
            if not (m and im and nm): continue
            pno = m.group(1)
            if (n, pno) in seen: continue
            seen.add((n, pno)); new += 1
            pr = re.search(r'<li class="price\s*">\s*([\d,]+)\s*원', li)
            rows.append((n, pno, T(nm.group(1)).replace("|", "/"), im.group(1), pr.group(1).replace(",", "") if pr else ""))
        if new == 0: break
        got += new
        time.sleep(0.15)
    print(n, byno[n]["name"], got, file=sys.stderr)
# 같은 상품번호는 처음 나온 분류에만
out, used = [], set()
for n, pno, nm, im, pr in rows:
    if pno in used: continue
    used.add(pno); out.append(f"{n}|{pno}|{nm}|{im}|{pr}")
if len(out) < 1000: sys.exit(f"too few: {len(out)}")
# 상세(옵션·원산지·짧은 설명) — 캐시에 없는 상품만, 한 번에 최대 45분
import os
DP = "src/data/cmbs_detail.tsv"
det = {}
if os.path.exists(DP):
    for l in open(DP, encoding="utf-8"):
        x = l.rstrip("\n").split("|")
        if len(x) >= 4: det[x[0]] = x[1:4]
t0 = time.time(); live = {l.split("|")[1] for l in out}
for pno in [l.split("|")[1] for l in out]:
    if pno in det: continue
    if time.time() - t0 > 45 * 60: break
    try: h = get(f"{B}/product/detail.html?product_no={pno}")
    except Exception: continue
    opts = []
    for sel in re.findall(r'<select[^>]*id="product_option_id\d+"[\s\S]*?</select>', h):
        for v, txt in re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([\s\S]*?)</option>', sel):
            txt = T(txt)
            if v in ("*", "**", "") or txt.startswith("-"): continue
            opts.append(txt.replace("|", "/").replace(";", ","))
    org = re.search(r'원산지</span></th>\s*<td><span[^>]*>([^<]*)<', h)
    d = ""
    k = h.find('id="prdDetailContent"')
    if k > 0:
        seg = h[k:k + 60000]
        for stop in ('id="prdInfo"', 'xans-product-additional', 'id="prdReview"'):
            j = seg.find(stop)
            if j > 0: seg = seg[:j]
        d = re.sub(r"#\S+", "", T(re.sub(r"<(script|style|iframe)[\s\S]*?</\1>", " ", seg)))
        d = re.sub(r"\s+", " ", d).strip()[:220].replace("|", "/")
    det[pno] = [";".join(opts[:40]), T(org.group(1)) if org else "", d]
    time.sleep(0.1)
open(DP, "w", encoding="utf-8").write("".join(f"{k}|{v[0]}|{v[1]}|{v[2]}\n" for k, v in det.items() if k in live))
print("detail", len(det), file=sys.stderr)
open("src/data/cmbs.tsv", "w", encoding="utf-8").write("\n".join(out) + "\n")
open("src/data/cmbs_cats.tsv", "w", encoding="utf-8").write("\n".join(f'{n}|{byno[n]["parent_cate_no"]}|{byno[n]["name"]}' for n in order if not under_skip(n)) + "\n")
print("rows", len(out), file=sys.stderr)
