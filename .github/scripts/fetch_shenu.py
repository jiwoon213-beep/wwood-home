# 쉐누(namuip.com/cnd_home) ABS도어·글래스도어·중문·몰딩·하드웨어·시트색상 → src/data/shenu.tsv (회사 허락, 가격 없음)
# 형식: 페이지|이미지경로(assets/img/ 뒤)|이름|부가설명 — 같은 사진·같은 이름+색상은 한 번만(중복 제거)
import re, html, sys, time, urllib.request
B = "https://namuip.com/cnd_home/"
PAGES = ["door_tot_bsc.php", "door_tot_ntr.php", "door_tot_line.php", "door_tot_pit.php", "door_glass_at.php", "door_glass_td.php", "door_glass_td_d.php",
         "door_frt_wood3.php", "door_frt_wood.php", "door_frt_al3.php", "moulding1.php", "moulding2.php", "moulding3.php", "moulding4.php", "moulding5.php", "hardware.php", "color.php"]
def get(u):
    for i in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (wwood.co.kr catalog sync)"}), timeout=30).read().decode("utf-8", "replace")
        except Exception as e: err = e; time.sleep(3)
    raise err
T = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
rows, seen_img, seen_nm = [], set(), set()
for p in PAGES:
    t = re.sub(r"<!--[\s\S]*?-->", "", get(B + p))
    t = t.split('id="footer"')[0]
    blocks = re.split(r'<div class="product-wrapper', t)[1:]
    if blocks:
        for b in blocks:
            m = re.search(r'<img src="assets/img/(product-details/[^"]+)"', b)
            if not m: continue
            img = m.group(1)
            h4 = re.search(r"<h4>([\s\S]*?)</h4>", b); sp = re.search(r"</h4>\s*<span>([\s\S]*?)</span>", b)
            nm = T(h4.group(1)) if h4 else ""; sub = T(sp.group(1)) if sp else ""
            rows.append((p, img, nm, sub))
    else:  # 몰딩·하드웨어·색상: 사진 + 근처 글
        for m in re.finditer(r'<img src="assets/img/(product-details/[^"]+)"[^>]*>([\s\S]{0,400})', t):
            img, after = m.group(1), m.group(2)
            if re.search(r"_main|banner|00\.jpg", img): continue
            al = re.search(r'alt="([^"]+)"', t[m.start():m.end()])
            cap = T(re.split(r"<img|<div class=\"col", after)[0])
            nm = (al.group(1) if al and al.group(1).strip() else cap)[:80]
            rows.append((p, img, nm, cap if nm != cap else ""))
    time.sleep(0.3)
out = []
for p, img, nm, sub in rows:
    key = (re.sub(r"\W", "", nm), re.sub(r"\W", "", sub))
    if img in seen_img or (nm and key in seen_nm): continue
    seen_img.add(img); seen_nm.add(key)
    out.append("|".join([p, img, nm.replace("|", "/"), sub.replace("|", "/")]))
if len(out) < 100: sys.exit(f"too few rows ({len(out)})")
open("src/data/shenu.tsv", "w", encoding="utf-8").write("\n".join(out) + "\n")
print(len(rows), "found,", len(out), "after de-dup")
