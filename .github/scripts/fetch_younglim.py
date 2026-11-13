# 영림(yl.co.kr) 도어·중문·몰딩/월/마루·인테리어 필름 목록 → src/data/younglim.tsv
# (키친·붙박이장·바스·타일 제외 — 사장님 요청). 회사 허락 받은 제품 사진 링크용. 가격은 가져오지 않음.
import re, html, sys, time, urllib.request
CODES = ['030100','030300','030400','030500','030600','030700','030801','030900','031000',
         '040100','040200','040300','040400','040500','040600','040700','040800','040900',
         '060101','060300','060500','060601','060702','080100']
RX = re.compile(r"\{ pi_index: (\d+),\s*pi_categoryCode: '(\d+)',\s*pi_categoryFullCode: '([^']*)',[\s\S]*?pi_productCode: (?:'([^']*)'|null),\s*pi_productName: '([^']*)',\s*pi_styleCode: (?:'([^']*)'|null),[\s\S]*?\"ifi_s3UrlPc\":\"([^\"]*)\"")
def get(u):
    for i in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (wwood.co.kr catalog sync)"}), timeout=30).read().decode("utf-8", "replace")
        except Exception as e:
            err = e; time.sleep(3)
    raise err
seen = {}
for c in CODES:
    for pg in range(1, 100):
        t = html.unescape(get(f"https://www.yl.co.kr/product/category?pi_categoryCode={c}&page={pg}"))
        n = 0
        for m in RX.finditer(t):
            idx, rc, full, code, name, sty, img = m.groups()
            if rc != c and c not in full: continue
            if idx in seen: continue
            n += 1
            seen[idx] = [c, rc, idx, code or "", re.sub(r"[|\n\t]", " ", name).strip(), sty or "", img.replace("https://s3.ap-northeast-2.amazonaws.com/younglim-bucket/", "")]
        if not n: break
        time.sleep(0.3)
rows = list(seen.values())
if len(rows) < 300:
    sys.exit(f"too few rows ({len(rows)}) — site changed? not overwriting")
open("src/data/younglim.tsv", "w", encoding="utf-8").write("".join("|".join(r) + "\n" for r in rows))
print(len(rows), "rows")
