# 철물박사 상품 사진에 다른 회사(쇼핑몰·업체) 워터마크가 있는지 OCR로 검사 → src/data/cmbs_block.txt (빼는 상품번호)
# 검사 결과 캐시: src/data/cmbs_wm.tsv (상품번호|판정 1/0|읽힌 글자 일부). 철물박사 로고는 허용.
import os, re, subprocess, sys, time, urllib.request, concurrent.futures as cf
from PIL import Image, ImageOps
B = "https://m.xn--392bopf4iwtp.com/web/product/medium/"
D = "src/data/"
rows = [l.rstrip("\n").split("|") for l in open(D + "cmbs.tsv", encoding="utf-8") if l.count("|") >= 3]
cache = {}
if os.path.exists(D + "cmbs_wm.tsv"):
    for l in open(D + "cmbs_wm.tsv", encoding="utf-8"):
        x = l.rstrip("\n").split("|")
        if len(x) >= 2: cache[x[0]] = (x[1], x[2] if len(x) > 2 else "")
# 이미 읽은 글자로 판정만 다시 계산(정규식을 고쳤을 때)
def judge(txt): return "1" if WM.search(OK.sub("", txt)) else "0"
# 워터마크로 보는 표시: 주소·저작권 문구·쇼핑몰 단어
WM = re.compile(r"(www\.|https?:|\b[a-z0-9][a-z0-9-]{2,}\.(?:com|co\.kr|kr|net|shop|store)\b|copyright|무단\s*(?:도용|복제|사용)|스토어|STORE|SHOP|쇼핑몰|MALL|쿠팡|coupang|11번가|지마켓|gmarket|옥션|auction|인터파크|네이버\s*쇼핑|naver)", re.I)
OK = re.compile(r"철물박사|chulmulbaksa|철물박사닷컴", re.I)
os.makedirs("/tmp/wm", exist_ok=True)
def scan(r):
    pno, img = r[1], r[3]
    f = f"/tmp/wm/{pno}.png"
    for i in range(3):
        try:
            data = urllib.request.urlopen(urllib.request.Request(B + img, headers={"User-Agent": "Mozilla/5.0 wwood.co.kr check"}), timeout=30).read(); break
        except Exception:
            time.sleep(2); data = None
    if not data: return pno, None, ""
    try:
        open(f + ".src", "wb").write(data)
        im = Image.open(f + ".src").convert("L")
        if im.width < 600: im = im.resize((im.width * 2, im.height * 2))
        im.save(f)
        txt = ""
        for g in (im,):
            g.save(f)
            txt += " " + subprocess.run(["tesseract", f, "-", "-l", "eng", "--psm", "11"], capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return pno, None, ""
    finally:
        for x in (f, f + ".src"):
            try: os.remove(x)
            except Exception: pass
    txt = re.sub(r"\s+", " ", txt).strip()
    hit = bool(WM.search(OK.sub("", txt)))
    return pno, "1" if hit else "0", txt[:120].replace("|", "/")
todo = [r for r in rows if r[1] not in cache][:9000]  # 한 번에 최대 2500장(시간 제한), 나머지는 다음 실행에
print("todo", len(todo), file=sys.stderr)
t0 = time.time()
with cf.ThreadPoolExecutor(4) as ex:
    futs = [ex.submit(scan, r) for r in todo]
    for k, fu in enumerate(cf.as_completed(futs)):
        if time.time() - t0 > 110 * 60:
            for f2 in futs: f2.cancel()
            break
        pno, v, txt = fu.result()
        if v is not None: cache[pno] = (v, txt)
        if k % 500 == 0: print(k, time.time() - t0, file=sys.stderr)
cache = {k: (judge(v[1]) if v[1] else v[0], v[1]) for k, v in cache.items()}
live = {r[1] for r in rows}
open(D + "cmbs_wm.tsv", "w", encoding="utf-8").write("".join(f"{k}|{v[0]}|{v[1]}\n" for k, v in cache.items() if k in live))
bl = sorted(k for k, v in cache.items() if v[0] == "1" and k in live)
open(D + "cmbs_block.txt", "w").write("\n".join(bl) + ("\n" if bl else ""))
print("blocked", len(bl), "of", len(cache), file=sys.stderr)
