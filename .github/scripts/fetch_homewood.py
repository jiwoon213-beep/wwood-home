# 수입 목조주택 자재·창호(/suip/) — homewood.co.kr 상품 사진·이름 → src/data/homewood_raw.txt (사장님 허락 2026-11-16, 가격 없음)
# 형식: slug|이름|사진경로(wp-content/uploads/ 뒤)|분류(빵부스러기, 'Home / ' 뺌). 같은 slug 한 번만.
# 이상하게 적게 읽히면(사이트 장애) 덮어쓰지 않음.
import re, html, sys, time, urllib.request, urllib.parse
B = "https://homewood.co.kr"
OUT = "src/data/homewood_raw.txt"
def get(u):
    err = None
    for i in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (wwood.co.kr catalog sync)"}), timeout=40).read().decode("utf-8", "replace")
        except Exception as e: err = e; time.sleep(4)
    raise err
T = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
cats = [u for u in re.findall(r"<loc>([^<]+)</loc>", get(B + "/product_cat-sitemap.xml")) if "/product-category/" in u]
P = {}
for c in cats:
    for pg in range(1, 15):
        u = c if pg == 1 else c.rstrip("/") + f"/page/{pg}/"
        try: t = get(u)
        except Exception: break
        bc = re.search(r'<nav[^>]*class="[^"]*breadcrumb[^"]*"[^>]*>([\s\S]*?)</nav>', t)
        bc = re.sub(r"^Home\s*/\s*", "", T(bc.group(1))) if bc else ""
        blocks = re.split(r'<div class="product-small col', t)[1:]
        for b in blocks:
            a = re.search(r'href="https://homewood\.co\.kr/product/([^"/]+)/?"', b)
            if not a: continue
            slug = urllib.parse.unquote(a.group(1))
            im = re.search(r'(?:data-src|src)="https://homewood\.co\.kr/wp-content/uploads/([^"]+)"', b)
            nm = re.search(r'class="[^"]*(?:product-title|woocommerce-loop-product__title)[^"]*"[^>]*>([\s\S]*?)</(?:p|h2|div)>', b)
            nm = T(nm.group(1)) if nm else ""
            if not nm:
                al = re.search(r'alt="([^"]+)"', b); nm = html.unescape(al.group(1)) if al else ""
            if not im or not nm: continue
            o = P.setdefault(slug, [nm, im.group(1), []])
            if bc and bc not in o[2]: o[2].append(bc)
        if not re.search(r'class="[^"]*next page-number', t): break
rows = [f"{s}|{v[0].replace('|', '/')}|{v[1]}|{sorted(v[2], key=len, reverse=True)[0] if v[2] else ''}" for s, v in P.items()]
print(len(cats), "categories,", len(rows), "products")
if len(rows) < 200: print("too few — keep old file"); sys.exit(0)
open(OUT, "w", encoding="utf-8").write("\n".join(rows) + "\n")
