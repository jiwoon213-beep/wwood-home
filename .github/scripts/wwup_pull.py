# 방문자가 올린 공간 사진 가져오기 → 얼굴·번호판 자동 모자이크 → 1200px·워터마크 → src/data/gonggan_visitor.json 에 추가 → 서버 원본 삭제
import json, os, re, sys, urllib.request, urllib.parse, time
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
KEY = os.environ.get("WWUP_KEY", ""); EP = "https://wwood.kr/home/wwup.php"
ROOT = os.getcwd(); OUT = f"{ROOT}/src/assets/gonggan"; DB = f"{ROOT}/src/data/gonggan_visitor.json"
if not KEY: print("no key"); sys.exit(0)
def get(q, raw=False):
    with urllib.request.urlopen(EP + "?" + urllib.parse.urlencode(dict(q, key=KEY)), timeout=60) as r:
        b = r.read()
    return b if raw else json.loads(b.decode("utf-8"))
ids = get({"list": 1}).get("ids", [])
db = json.load(open(DB, encoding="utf-8")) if os.path.exists(DB) else []
have = {x["id"] for x in db}
face = cv2.FaceDetectorYN.create("/tmp/yunet.onnx", "", (320, 320), 0.6, 0.3, 5000)
plate = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_russian_plate_number.xml")
def pix(img, x, y, w, h):
    H, W = img.shape[:2]; m = int(max(w, h) * .25)
    x0, y0, x1, y1 = max(0, x - m), max(0, y - m), min(W, x + w + m), min(H, y + h + m)
    if x1 - x0 < 4 or y1 - y0 < 4: return
    roi = img[y0:y1, x0:x1]; s = max(1, min(x1 - x0, y1 - y0) // 10)
    img[y0:y1, x0:x1] = cv2.resize(cv2.resize(roi, ((x1 - x0) // s or 1, (y1 - y0) // s or 1)), (x1 - x0, y1 - y0), interpolation=cv2.INTER_NEAREST)
def KEYOF(t):
    for k, rx in [("door", "도어|방문|문틀|문짝"), ("jungmun", "중문"), ("maru", "마루|후로링|장판|데코타일"), ("tile", "타일|스톤"), ("molding", "몰딩|걸레받이"),
                  ("siding", "사이딩|외장"), ("deck", "데크"), ("roof", "지붕|슁글"), ("hardware", "철물|경첩|피스|볼트|부자재|공구"), ("handle", "손잡이"),
                  ("paint", "페인트|스테인|오일"), ("gakjae", "각재|구조"), ("jipseong", "집성|우드슬랩|합판|판재"), ("wall", "내장|벽|판넬|패널|단열|방음")]:
        if re.search(rx, t): return k
    return "wall"
CATMAP = {"siding": "ext", "roof": "ext", "deck": "out"}
new = 0
for i in ids:
    if i in have:
        get({"id": i, "del": 1}); continue
    try:
        meta = json.loads(get({"id": i, "meta": 1}, raw=True).decode("utf-8") or "{}")
        b = get({"id": i, "img": 1}, raw=True)
        img = cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR)
        if img is None: get({"id": i, "del": 1}); continue
        H, W = img.shape[:2]; sc = 1600 / max(H, W)
        if sc < 1: img = cv2.resize(img, (int(W * sc), int(H * sc)), interpolation=cv2.INTER_AREA); H, W = img.shape[:2]
        nf = 0
        for s in (1.0, 0.5):  # 작은 얼굴도 잡게 두 크기로
            im2 = cv2.resize(img, (int(W * s), int(H * s))) if s != 1 else img
            face.setInputSize((im2.shape[1], im2.shape[0]))
            _, F = face.detect(im2)
            for f in (F if F is not None else []):
                x, y, w, h = [int(v / s) for v in f[:4]]; pix(img, x, y, w, h); nf += 1
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        P = plate.detectMultiScale(g, 1.08, 4, minSize=(40, 12))
        for (x, y, w, h) in P: pix(img, x, y, w, h)
        pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if max(pil.size) > 1200: pil.thumbnail((1200, 1200))
        d = ImageDraw.Draw(pil, "RGBA"); w, h = pil.size; fs = max(16, w // 34)
        try: ft = ImageFont.truetype("/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf", fs)
        except Exception: ft = ImageFont.load_default()
        t = "영진종합목재 www.wwood.co.kr"; tw = d.textlength(t, font=ft)
        d.text((w - tw - fs * .8 + 1, h - fs * 1.8 + 1), t, font=ft, fill=(0, 0, 0, 120)); d.text((w - tw - fs * .8, h - fs * 1.8), t, font=ft, fill=(255, 255, 255, 220))
        fn = f"v-{i}.jpg"; pil.save(f"{OUT}/{fn}", "JPEG", quality=84, optimize=True)
        sp = []
        for s in (meta.get("spots") or [])[:6]:
            lab = str(s.get("c", ""))[:30]; nm = str(s.get("n", ""))[:60]
            sp.append({"x": round(float(s.get("x", 50)), 1), "y": round(float(s.get("y", 50)), 1), "c": lab, "n": nm,
                       "l": str(s.get("l", ""))[:300], "u": re.sub(r"[^a-z0-9-]", "", str(s.get("u", "")))[:40], "k": KEYOF(lab + nm)})
        ks = [x["k"] for x in sp]; cat = next((CATMAP[k] for k in ks if k in CATMAP), "home")
        how = [{"n": str(h.get("n", ""))[:80], "l": str(h.get("l", ""))} for h in (meta.get("how") or [])[:2] if re.match(r"^/(mandeul|sigongbeop)/[a-z0-9-]+\.html$", str(h.get("l", "")))]
        who = re.sub(r"[<>\"'&]", "", str(meta.get("who", "")))[:16].strip()
        db.append({"who": who, "how": how, "id": i, "img": fn, "title": str(meta.get("title", ""))[:60], "t": int(meta.get("t", time.time())), "spots": sp, "cat": cat, "faces": nf, "plates": len(P)})
        new += 1
        get({"id": i, "del": 1})  # 서버 원본(모자이크 전) 삭제
    except Exception as e:
        print("ERR", i, e)
json.dump(db, open(DB, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("new", new)
