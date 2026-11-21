from urllib.parse import quote
import glob
import collections, re
#!/usr/bin/env python3
"""월드건축자재 홍보 사이트 생성기. python3 build.py [BASE_URL]"""
import csv, html, json, math, os, re, shutil, sys, datetime
from mats import MATS, CATS

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out")
BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://www.wwoodkr.com").rstrip("/")
PREFIX = sys.argv[2].rstrip("/") if len(sys.argv) > 2 else ""   # 미리보기용 하위 경로 (예: /lumber-price/wwood)
OUT = sys.argv[3] if len(sys.argv) > 3 else OUT
PREVIEW = bool(PREFIX)
MALL = "https://wwood.kr/home/mall/"
DOME = "https://wwood.kr/home/sub06/menu03.php"  # 도매회원 쇼핑몰 연결 주소(사장님 지정)
YT = "https://www.youtube.com/@월드건축자재DIY"
YT2 = "https://www.youtube.com/@worlddoor"
KAKAO = "https://pf.kakao.com/_JxhxoxeX"
BLOG = "https://blog.naver.com/swr4083"
TEL = "042-545-2900"
ADDR = "대전 유성대로 44, 1층"
EMAIL = "yjwood2021@naver.com"
NPLACE = "https://naver.me/GEdDcn2S"  # 네이버 플레이스(스마트플레이스 승인)
RVBOX = ('<div class="rvw"><p class="rvh">다녀가셨다면 리뷰 한 줄 부탁드려요</p><div class="rvg">'
  f'<a class="rv nv" href="{NPLACE}" target="_blank" rel="noopener"><span class="rvi">N</span><span class="rvt"><b>네이버 리뷰 쓰기</b><span class="rvs">★★★★★</span><small>네이버 지도 · 영수증 인증</small></span></a>'
  '<a class="rv gg" href="https://g.page/r/CZcZc9J-M0L0EAE/review" target="_blank" rel="noopener"><span class="rvi">G</span><span class="rvt"><b>구글 리뷰 쓰기</b><span class="rvs">★★★★★</span><small>누르면 바로 별점 화면</small></span></a>'
  '</div></div>')
HOURS = "평일 07:00~18:00 · 토·일 07:00~15:00 · 공휴일 07:00~16:00"
LIC = "실내건축공사업 대전서구24-나-19"
E = html.escape

# ---------- data ----------
V = []
for r in csv.reader(open(f"{ROOT}/data/videos.tsv", encoding="utf-8"), delimiter="\t"):
    if len(r) < 6: continue
    vid, typ, n, cat, mats, title = r[:6]
    V.append(dict(id=vid, type=typ, n=int(n or 0), cat=cat, mats=[m for m in mats.split("/") if m], title=title.strip()))
P = [dict(cat=r["cat"], name=r["name"], price=int(float(r["price"])), qty=float(r["qty"] or 0))
     for r in csv.DictReader(open(f"{ROOT}/data/prices.csv", encoding="utf-8"))]
CATN = {c: n for c, n, _ in CATS}
# 가격 변동 표시: data/prices_prev.csv(지난 기준가)와 비교해 실제로 바뀐 품목만 ▲▼ (가격 갱신 시 이전 파일을 prices_prev.csv로 남김)
PREV = {r["name"]: int(float(r["price"])) for r in csv.DictReader(open(f"{ROOT}/data/prices_prev.csv", encoding="utf-8"))} if os.path.exists(f"{ROOT}/data/prices_prev.csv") else {}
PMETA = json.load(open(f"{ROOT}/data/price_meta.json", encoding="utf-8")) if os.path.exists(f"{ROOT}/data/price_meta.json") else {}
RANK = {p["name"]: i + 1 for i, p in enumerate(sorted(P, key=lambda p: -p["qty"]))}
def chg(p):
    o = PREV.get(p["name"])
    if not o or o == p["price"]: return ''
    d = p["price"] - o; pc = d / o * 100
    return f'<span class="ch {"up" if d > 0 else "dn"}">{"▲" if d > 0 else "▼"} {abs(d):,}원 ({pc:+.1f}%)</span>'
PLINK = {"문": "/jajae/door.html", "문틀": "/jajae/door.html", "문제": "/jajae/door.html", "몰딩": "/jajae/molding.html", "내장": "/jaryo/naejang.html",
         "진열": "/jajae/hardware.html", "피스": "/jajae/hardware.html", "타카": "/jajae/hardware.html", "철물": "/jajae/hardware.html",
         "합판": "/jajae/hapan.html", "엠디": "/jajae/mdf.html", "부재": "/jaryo/sopum.html", "본드": "/jaryo/sopum.html", "공구": "/jaryo/sopum.html",
         "오일": "/jajae/stain.html", "집성판": "/jajae/jipseong.html", "사이딩": "/jajae/siding.html", "외장": "/jajae/siding.html",
         "단열": "/jajae/insul.html", "합성": "/jajae/hapdeck.html", "필름": "/jajae/film.html", "방부": "/jajae/bangbu.html",
         "목재": "/jajae/gujo.html", "각재": "/jajae/gujo.html", "구조": "/jajae/gujo.html", "계단": "/jaryo/gakjae.html", "석고": "/jajae/gypsum.html",
         "가든": "/jajae/chimmok.html", "마루": "/jajae/maru.html", "데크": "/jajae/maru.html", "루바": "/jajae/hinoki.html", "특수": "/jajae/hinoki.html"}
MALLCAT = {"hapan": ("24", "합판·판재"), "osb": ("24", "OSB·판재"), "mdf": ("24", "MDF·판재"), "gujo": ("23", "각재·구조재"), "gakjae": ("23", "각재·구조재"), "bangbu": ("23", "방부목·각재"),
           "chimmok": ("23", "침목·각재"), "hapdeck": ("25", "데크재"), "jipseong": ("53", "집성판·우드슬랩"), "hinoki": ("27", "루바·내장재"), "molding": ("27", "몰딩·내장재"), "film": ("27", "내장재"),
           "gypsum": ("27", "석고·내장재"), "maru": ("26", "마루·후로링"), "tile": ("28", "스톤·타일"), "siding": ("31", "외장재·사이딩"), "insul": ("30", "방음·단열·방수"), "sound": ("30", "방음·흡음"),
           "door": ("29", "실내 도어·문틀"), "hardware": ("32", "철물"), "stain": ("35", "페인트·스테인")}
def mallbox(mats, mx=2):
    """설명 끝에 '이 자재 사러 가기' — 매장 쇼핑몰(wwood.kr) 해당 분류로 바로"""
    seen, a = set(), []
    for m in mats:
        c = MALLCAT.get(m)
        if not c or c[0] in seen: continue
        seen.add(c[0]); a.append(f'<a class="b r" href="https://wwood.kr/home/mall/shoplist.php?depth=1&amp;code1_idx={c[0]}">{c[1]} 쇼핑몰에서 보기 ›</a>')
        if len(a) >= mx: break
    if not a: return ""
    return '<section class="wrap sec"><div class="card mallbox"><h2>이 자재 사러 가기</h2><p class="small muted">영진종합목재 쇼핑몰(wwood.kr)에서 바로 보거나, 매장에서 원하는 크기로 재단해 가세요.</p><div class="row">' + "".join(a) + '<a class="b o" href="/cut.html">재단 그림 만들기</a><a class="b o" href="/visit.html">매장 길찾기</a></div></div></section>'
def plink(p):
    if p["cat"] == "합판" and re.search(r"OSB", p["name"], re.I): return "/jajae/osb.html"
    return PLINK.get(p["cat"], "/jaryo/")
def badge(p): return '<span class="bd hot">인기 TOP10</span>' if RANK.get(p["name"], 999) <= 10 else ('<span class="bd">많이 찾는</span>' if RANK.get(p["name"], 999) <= 50 else "")

# 소식·정보 글: data/posts/YYYY-MM-DD-slug.html, 첫 줄 <!--{"title","desc","date","videos":[]}--> 다음 본문 HTML
POSTS = []
_pd = f"{ROOT}/data/posts"
for fn in sorted(os.listdir(_pd) if os.path.isdir(_pd) else [], reverse=True):
    if not fn.endswith(".html"): continue
    raw = open(f"{_pd}/{fn}", encoding="utf-8").read()
    m = re.match(r"\s*<!--(\{.*?\})-->\s*", raw, re.S)
    if not m: continue
    meta = json.loads(m.group(1)); meta["slug"] = fn[:-5]; meta["body"] = re.sub(r"<(li|p)[^>]*>[^<]*(카카오톡|카톡)[^<]*<a [^>]*pf\.kakao\.com[^>]*>.*?</a>[^<]*</\1>", "", raw[m.end():], flags=re.S)  # 카톡 상담 링크 제거(사장님 요청)
    POSTS.append(meta)
POSTS.sort(key=lambda p: (p.get("date", ""), p["slug"]), reverse=True)
# 쇼핑몰(wwood.kr) 자재 목록: data/products.tsv  (# 줄 = 분류코드, 나머지 = id, 이름, 사진, 분류들) — 가격 없음
MCAT, PROD = {}, []
for line in open(f"{ROOT}/data/products.tsv", encoding="utf-8") if os.path.exists(f"{ROOT}/data/products.tsv") else []:
    r = line.rstrip("\n").split("\t")
    if r[0] == "#": MCAT[r[1]] = r[2]; continue
    if len(r) < 4 or not r[1].strip(): continue
    img = r[2].replace("@", "/common/ezs_data/product/", 1) if r[2].startswith("@") else r[2].replace("!", "/modules/shop/files/", 1) if r[2].startswith("!") else r[2]
    _loc = f"/assets/mall/{r[0]}.webp" if os.path.exists(f"{ROOT}/assets/mall/{r[0]}.webp") else None  # 작은 사진(Actions mallthumbs.yml이 만듦)
    PROD.append(dict(id=r[0], name=r[1].strip(), img=_loc or ("https://www.wwood.kr" + img), img0="https://www.wwood.kr" + img, cats=[c for c in r[3].split(",") if c]))
# 홈페이지 전체 자재 분류 (쇼핑몰 대분류 코드 → 주소)
JCAT = [("23", "gakjae", "각재·구조재", "다루끼·구조재·방부목·히노끼·탄화목·침목"), ("24", "panjae", "판재·합판", "합판·MDF·OSB·집성판·고재판재·임가공판재"),
        ("53", "jipseong", "우드슬랩·집성판", "고무나무·아카시아·멀바우·히노끼 집성판"), ("25", "deck", "데크재", "방부데크·천연데크·합성데크·탄화데크·데크철물"),
        ("26", "maru", "마루·후로링", "원목후로링·강마루·강화마루·바닥도료"), ("27", "naejang", "내장재", "루바·고재·월판넬·아트월·천정재·몰딩·타공판"),
        ("28", "stone", "스톤·타일", "스톤·북유럽타일·파벽돌·조약돌"), ("31", "siding", "외장재·사이딩", "사이딩·지붕재·기와·타이벡"),
        ("29", "door", "실내 도어·문틀", "ABS도어·유리도어·문틀·합판문"), ("29w", "window", "주택 창호", "수입 주택창호·파티오도어·고정창"), ("30", "insul", "방음·단열·방수", "방음·흡음·단열·보온·방수·환기"),
        ("32", "hardware", "철물", "건축철물·타카·인테리어철물·공학목재철물"), ("35", "paint", "페인트·스테인", "오일스테인·페인트·작업도구"),
        ("37", "sopum", "소품·부자재", "정원가구·목재소품·철제가구·공구·접착제")]
JTOP = {c for c, *_ in JCAT}
# 전체 자재 분류별 관련 유튜브 영상(제목 정규식)
JVRX = {"23": r"각재|구조재|방부목|다루끼|히노끼 각|투바이|2x4|2×4|목조|탄화목|침목", "24": r"합판|MDF|OSB|판재|자작|코아", "53": r"집성|우드슬랩|상판|원목 테이블",
        "25": r"데크", "26": r"마루|후로링|데코타일|장판", "27": r"루바|템바|몰딩|걸레받이|월판|아트월|타공|천장|석고보드|인테리어 벽",
        "28": r"(?<!데코)타일|스톤|파벽돌|조약돌", "31": r"사이딩|외장|외벽|지붕|슁글|타이벡|기와", "29": r"문틀|방문|도어|중문|문짝", "29w": r"창호|창문|샷시|시스템창",
        "30": r"단열|아이소핑크|방음|흡음|스티로폼", "32": r"철물|타카|피스|장선걸이|앙카|브라켓|경첩", "35": r"스테인|페인트|오일|바니시|바니쉬|도장|칠하기",
        "37": r"공구|본드|실리콘|소품|정원|평상|벤치"}
JEXC = {"23": r"루바|사이딩|판재|우드블럭|데크|후로링|마루|래티스|클립|엠보",
        "24": r"본드|프라이머|실리콘|석고|아이소|스티로|에이스|도깨비|페인트|부식|산화제",
        "27": r"프라이머|도깨비|페인트|부식|산화제", "28": r"세라픽스|멘트|드라이픽스|시공사례", "31": r"코르크", "32": r"프라이머"}
# 이름으로 분류를 바로잡는 규칙 (쇼핑몰 분류 대신 사용)
JFORCE = [(r"^석고보드$", ["27/166"]), (r"시공사례", ["54/375"]), (r"본드|실리콘(?!건)|파워멘트|세라픽스|드라이픽스|백시멘트", ["37/400"]),
          (r"프라이머|도깨비|규조토 페인트|부식 (산화제|마감제)", ["35/356"])]
MCAT["29w/367"] = MCAT.get("29/367", "주택창호(수입)"); MCAT["29w/"] = "주택 창호"
for p in PROD:
    p["cats"] = ["29w/367" if c == "29/367" else c for c in p["cats"]]
    if p["name"] == "합판문": p["cats"].append("29/274")
    for rx, cs in JFORCE:
        if re.search(rx, p["name"]) and not re.search(r"실리콘건", p["name"]): p["cats"] = cs; break
    tops = [c.split("/")[0] for c in p["cats"]]
    p["top"] = next((t for t in tops if t in JTOP), None)
    if not p["top"] and not any(t in ("54", "59") for t in tops):  # 매출탑·세일 분류에만 있는 자재는 이름으로 분류
        for rx, c in (("집성", "53/349"), ("루바", "27/156"), ("코코넛", "27/160"), ("핸드레일", "23/136"), ("데크|난간", "25/146"), ("철물", "32/333")):
            if re.search(rx, p["name"]): p["top"] = c.split("/")[0]; p["cats"].append(c); break
    p["tops"] = [t for t in dict.fromkeys(tops) if t in JTOP] or ([p["top"]] if p["top"] else [])
    # 쇼핑몰에서 엉뚱한 분류에 같이 들어간 것 정리 (예: 본드가 합판/MDF에)
    ok = [t for t in p["tops"] if not (t in JEXC and re.search(JEXC[t], p["name"]))]
    if ok != p["tops"]:
        if not ok:
            for rx, c in ((r"사이딩", "31/186"), (r"마루|후로링", "26/148"), (r"루바", "27/156"), (r"데크|클립", "25/147"), (r"판재|엠보", "24/318"),
                          (r"석고|아이소|스티로|에이스|단열", "30/183"), (r".", "37/397")):
                if re.search(rx, p["name"]): p["cats"].append(c); ok = [c.split("/")[0]]; break
        p["tops"] = ok; p["top"] = ok[0]
    p["sub"] = next((c for c in p["cats"] if c.split("/")[0] == p["top"] and c.split("/")[1]), None)
# 페인트·스테인(35): 본덱스(이몰링)에 같은 제품이 있는 기존 제품만 뺌(중복 제거, 사장님 지시 2026-11-14). 나머지는 그대로.
if os.path.exists(f"{ROOT}/data/emall.tsv"):
    _EMN = [l.split("|")[2] for l in open(f"{ROOT}/data/emall.tsv", encoding="utf-8") if l.count("|") >= 3]
    def _inbd(n):
        toks = [w for w in re.split(r"[\s\-\(\)\[\]/,]+", re.sub(r"천연|내추럴|식물성|목재보수제", " ", n)) if len(w) >= 2]
        return bool(toks) and any(sum(w.replace(" ", "") in e.replace(" ", "") for w in toks) >= (len(toks) if len(toks) <= 3 else len(toks) - 1) for e in _EMN)
    PROD = [p for p in PROD if "35" not in p["tops"] or not _inbd(p["name"])]  # 본덱스에 같은 제품이 있으면 본덱스 쪽만(중복 제거)
# 외장재·사이딩(31): 니치하 페이지(/nichiha/)에 같은 품번이 있는 기존 제품은 뺌(중복 제거)
if os.path.exists(f"{ROOT}/data/nichiha.tsv"):
    _NHC = [l.split("|")[1] for l in open(f"{ROOT}/data/nichiha.tsv", encoding="utf-8") if l.strip() and not l.startswith("#")]
    PROD = [p for p in PROD if "31" not in p["tops"] or not any(re.search(c + r"(?!\d)", p["name"]) for c in _NHC)]
# 건축자재 카탈로그(/geonjae/, samik.py)에 같은 이름 제품이 있으면 기존 쇼핑몰 자재 쪽을 뺌(중복 제거)
# 크나우프 카탈로그(/knauf/)가 있으면 기존 쇼핑몰의 크나우프 상품은 뺌(중복 제거)
if os.path.exists(f"{ROOT}/data/knauf.tsv"):
    PROD = [p for p in PROD if not re.search(r"크나우프|knauf", p["name"], re.I)]
if os.path.exists(f"{ROOT}/data/samik.tsv"):
    _SMK = {re.sub(r"[\s\-·()\[\]/,.]", "", l.split("|")[3]).lower() for l in open(f"{ROOT}/data/samik.tsv", encoding="utf-8") if l.count("|") >= 4}
    PROD = [p for p in PROD if re.sub(r"[\s\-·()\[\]/,.]", "", p["name"]).lower() not in _SMK]
def subof(p, top): return next((c for c in p["cats"] if c.split("/")[0] == top and c.split("/")[1]), None)
# 자재 백과 사진: slug → (쇼핑몰 분류, 이름 정규식, 제외 정규식)
MPHOTO = {"hapan": (["24/140"], "합판|판넬|보드", "OSB|O\\.S\\.B|M\\.?D\\.?F|석고|아이소|스티로|본드|실리콘|프라이머|에이스|문$"), "osb": ([], "OSB|O\\.S\\.B|스마트랩", None),
          "mdf": ([], "M\\.?D\\.?F", None), "gujo": (["23/134"], ".", None), "bangbu": (["23/135", "25/144"], ".", "주춧돌"),
          "hapdeck": (["25/146"], ".", "주춧돌|핸드레일"), "jipseong": (["53/349", "24/141"], "집성", None), "hinoki": (["23/137", "27/156"], "히노끼|삼목|스기|향목|편백|오비스기", None),
          "gypsum": ([], "석고보드|불연", "본드"), "siding": (["31/186"], ".", None), "insul": (["30/183"], ".", None), "stain": (["35/206", "25/249"], ".", None),
          "hardware": (["32/332", "32/333"], ".", None), "maru": (["26/247", "26/148", "26/149", "26/315"], ".", None), "film": ([], None, None),
          "molding": (["27/381"], ".", None), "chimmok": (["23/314"], "침목|우드빔|탄화|SYP", None), "tile": (["28/168", "28/167"], ".", None), "sound": (["30/182", "27/322"], ".", None), "door": (["29/274"], ".", None)}
def mat_photos(slug):
    cats, inc, exc = MPHOTO.get(slug, ([], None, None))
    if not inc: return []
    return [p for p in PROD if (not cats or any(c in p["cats"] for c in cats)) and re.search(inc, p["name"]) and not (exc and re.search(exc, p["name"]))]
def mall_links(m):
    cats = [c for c in MPHOTO.get(m["slug"], ([], None, None))[0] if "/" in c and MCAT.get(c)]
    if not cats: return ""
    lk = " · ".join(f'<a href="https://wwood.kr/home/mall/shoplist.php?depth=2&amp;code1_idx={c.split("/")[0]}&amp;code2_idx={c.split("/")[1]}" target="_blank" rel="noopener">{E(MCAT[c].replace("ㆍ","").strip())}</a>' for c in cats)
    return f'<p class="small" style="margin-top:10px">🛒 쇼핑몰에서 {E(m["name"])} 상품 보기: {lk}</p>'
PSPEC = json.load(open(f"{ROOT}/data/pspec.json", encoding="utf-8")) if os.path.exists(f"{ROOT}/data/pspec.json") else {}
def _psp(p):  # 사진 크게 보기(라이트박스)에 넣을 규격 요약
    rs = [[c.strip() for c in r] for r in PSPEC.get(str(p["id"]), []) if r and r[0].strip()]
    if not rs: return ""
    out = []
    sz = list(dict.fromkeys(r[0] for r in rs))
    out.append("규격\t" + " / ".join(sz[:6]) + (f" 외 {len(sz) - 6}가지" if len(sz) > 6 else ""))
    for k, nm in ((1, "단위"), (2, "원산지"), (3, "수종")):
        v = list(dict.fromkeys(r[k] for r in rs if len(r) > k and r[k] and r[k] not in ("품절", "재입고준비중")))
        if v and k != 3 or (k == 3 and v and len(" / ".join(v[:4])) < 60): out.append(nm + "\t" + " / ".join(v[:4]))
    return "\n".join(out)
def _pdata(p):
    return f' data-big="{E(p.get("img0") or p["img"])}" data-n="{E(p["name"])}" data-sp="{E(_psp(p))}"'
def pcard(p):
    sub = MCAT.get(p["sub"] or "", "")
    _own = p.get("tops") and p.get("top") in {c for c, *_ in JCAT}  # 새 홈페이지에 상품 페이지(/p/)가 있으면 그쪽으로 연결(내부 링크 → 색인에 도움)
    return ((f'<a class="pd" href="/p/{p["id"]}.html"{_pdata(p)}>' if _own else f'<a class="pd" href="https://wwood.kr/home/mall/shoplist.php?idx={p["id"]}&amp;pmode=view" target="_blank" rel="noopener"{_pdata(p)}>')
            + f'<span class="pi"><img loading="lazy" src="{E(p["img"])}" alt="{E(p["name"])}"></span><b>{E(p["name"])}</b>{f"<small>{E(sub)}</small>" if sub else ""}</a>')
# 유튜브 채널 숫자: data/stats.json {"subs": "1.36만", "videos": 940, "date": "YYYY-MM-DD"} (하루 1번 자동 갱신)
ST = json.load(open(f"{ROOT}/data/stats.json", encoding="utf-8")) if os.path.exists(f"{ROOT}/data/stats.json") else {"subs": "1.3만", "videos": 900}
# 최신 영상: data/latest.txt (영상 ID, 최신이 위)
def _steps(steps):
    # 순서: 번호 동그라미 + 숫자(치수·개수) 굵게, 단계마다 칸 나눔
    def _hl(t):
        return re.sub(r"(\d[\d,.]*(?:\s?[×x]\s?\d[\d,.]*)*\s?(?:mm|cm|m|개|곳|줄|장|회|단|T)?)", r"<b>\1</b>", E(t))
    return '<ol class="sstp">' + "".join(f'<li><i>{k + 1}</i><p>{_hl(x)}</p></li>' for k, x in enumerate(steps)) + '</ol>'


def faqslide(items):
    return '<div class="fqs">' + "".join(f'<div class="fq"><b>Q. {E(q)}</b><p>{E(a)}</p></div>' for q, a in items) + '</div>' + ('<p class="small muted fqh">옆으로 밀어서 더 보기 ›</p>' if len(items) > 1 else "")
MFAQ = json.load(open(f"{ROOT}/data/mat_faq.json", encoding="utf-8")) if os.path.exists(f"{ROOT}/data/mat_faq.json") else {}
LATEST = [l.strip() for l in open(f"{ROOT}/data/latest.txt", encoding="utf-8")] if os.path.exists(f"{ROOT}/data/latest.txt") else []

import gzip as _gz
VD = {k: x for k, x in (json.loads(_gz.open(f"{ROOT}/data/vdesc.json.gz").read()) if os.path.exists(f"{ROOT}/data/vdesc.json.gz") else {}).items() if len(x[0]) >= 120}  # 설명이 충분한 영상만 개별 페이지(얇은 페이지 방지)
def vpage(v): return f"/v/{v['id']}.html" if v["id"] in VD else vurl(v)
def vurl(v): return f"https://www.youtube.com/{'shorts/' if v['type']=='S' else 'watch?v='}{v['id']}"
def vshort(t):
    p = [x.strip() for x in t.split("|")]
    return p[0] if len(p) > 1 and len(p[0]) >= 3 else t
def views(n): return f"{n/10000:.1f}만회".replace(".0만", "만") if n >= 10000 else f"{n:,}회"
def won(x): return f"{x:,}원~"
PFX = {"구조": "구조재 ", "타카": "타카핀 ", "피스": "피스 ", "철물": "철물 ", "진열": "", "문제": "", "합판": "합판 ", "엠디": "", "석고": "석고보드 ",
       "방부": "방부목 ", "합성": "합성 ", "단열": "", "몰딩": "몰딩 ", "필름": "필름 ", "본드": "", "부재": "", "공구": "", "외장": "", "사이딩": "사이딩 ",
       "루바": "루바 ", "집성판": "집성판 ", "데크": "데크 ", "마루": "", "오일": "오일 ", "계단": "계단 ", "각재": "각재 ", "가든": "", "내장": "", "목재": "", "특수": ""}
def clean_name(n):  # "합판- 일반 4*8 @ 8.5mm(베)" → "합판 일반 4×8 · 8.5mm(베)"
    m = re.match(r"^([^-]+?)\s*-\s*(.*)$", n)
    cat, rest = (m.group(1).strip(), m.group(2)) if m else ("", n)
    rest = rest.replace("*", "×").replace("@", " · ")
    out = PFX.get(cat, "") + rest
    out = re.sub(r"\s+", " ", out).strip(" ·")
    out = re.sub(r"(\d)\s*×\s*", r"\1×", out).replace("( ", "(")
    return out

def prod_ld(rows, url, img=None):
    if not rows: return []
    im = img or "/assets/store/yard-aisle.jpg"
    im = im if im.startswith("http") else BASE + im
    return [{"@context": "https://schema.org", "@type": "Product", "name": clean_name(r["name"]),
             "image": im, "description": f"{clean_name(r['name'])} — {r['cat']}. 대전 유성 영진종합목재 매장 기준가(부가세 별도), 원하는 크기로 즉석 재단.",
             "offers": {"@type": "Offer", "price": int(r["price"]), "priceCurrency": "KRW", "url": url, "availability": "https://schema.org/InStoreOnly",
                        "priceSpecification": {"@type": "UnitPriceSpecification", "price": int(r["price"]), "priceCurrency": "KRW", "valueAddedTaxIncluded": False},
                        "seller": {"@type": "Organization", "name": "영진종합목재"}}} for r in rows]

def mat_prices(m, k=10):
    cats, inc, exc = m["price"]
    if not cats: return []
    rows = [p for p in P if p["cat"] in cats and re.search(inc, p["name"]) and not (exc and re.search(exc, p["name"]))]
    return sorted(rows, key=lambda p: -p["qty"])[:k]

# ---------- layout ----------
NAV = [("/visit.html", "매장 안내"), ("/jaryo/", "전체 자재"), ("/news/", "소식·정보"), ("/tteori/", "떨이몰"), ("/price.html", "기준가"), ("/mandeul/", "DIY 만들기"), ("/sigongbeop/", "자재 시공법"), ("/trend/", "인테리어 트렌드"), ("/gonggan/", "공간 사진"), ("/calc.html", "자재비 계산기"), ("/cut.html", "목재 재단"), ("/sajin.html", "사진으로 찾기"), ("/video/", "영상"), ("/dome.html", "도매·납품"), ("/sigong.html", "시공"), ("/yeongyeol/", "시공팀 연결")]

NAVI = {'/gonggan/': '<path d="M13 4H5.5A2.5 2.5 0 0 0 3 6.5v11A2.5 2.5 0 0 0 5.5 20h13a2.5 2.5 0 0 0 2.5-2.5V11.5"/><g stroke="#b06a2c"><path d="M8.6 13.6v-1.3a1.3 1.3 0 0 1 1.3-1.3h4.2a1.3 1.3 0 0 1 1.3 1.3v1.3"/><path d="M6.6 13.4v3.4h10.8v-3.4"/></g><circle cx="18.3" cy="5.7" r="3.6" fill="#2f8bff" stroke="none"/><path d="M18.3 4.1v3.2M16.7 5.7h3.2" stroke="#fff" stroke-width="1.6"/>', "/tteori/": '<path d="M3.5 12.5 11.5 4.5H19.5v8l-8 8z"/><path d="M10 14l5-5"/><circle cx="10.5" cy="9.5" r=".9"/><circle cx="14.5" cy="13.5" r=".9"/>', "/yeongyeol/": '<circle cx="8" cy="8" r="3"/><circle cx="16.5" cy="9" r="2.5"/><path d="M3 19c.6-3.2 2.6-5 5-5s4.4 1.8 5 5"/><path d="M13.5 18.5c.4-2.6 1.6-4 3-4s2.6 1.4 3 4"/>', "/calc.html": '<rect x="5" y="3" width="14" height="18" rx="2.5"/><path d="M8 7h8M8 11h2M12 11h2M16 11h0M8 15h2M12 15h2M8 18h2M12 18h2"/><path d="M16 14v4"/>', '/visit.html': '<path d="M12 21s-6-5.3-6-10a6 6 0 1 1 12 0c0 4.7-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/>', '/jaryo/': '<rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.5"/>', '/news/': '<path d="M5 4.5h11.5v15H6.5A1.5 1.5 0 0 1 5 18z"/><path d="M16.5 8.5H19v9.5a1.5 1.5 0 0 1-3 0"/><path d="M8 8.5h5.5M8 12h5.5M8 15.5h3.5"/>', '/price.html': '<path d="M3.5 12.5 11.5 4.5H19.5v8l-8 8z"/><circle cx="15.5" cy="8.5" r="1.4"/>', '/mandeul/': '<path d="M14.5 5.5l4 4L9 19H5v-4z"/><path d="M12.5 7.5l4 4"/>', '/sigongbeop/': '<path d="M4 20h16"/><path d="M6 20V9l6-4.5L18 9v11"/><path d="M10 20v-5h4v5"/>', '/apt/': '<path d="M4 20V8l5-3v15M9 20V4l7 3v13M16 20v-9l4 2v7"/><path d="M3 20h18"/>', '/doumi.html': '<circle cx="12" cy="12" r="8.5"/><path d="M9.6 9.5a2.5 2.5 0 1 1 3.4 2.3c-.6.3-1 .8-1 1.4v.6"/><circle cx="12" cy="16.8" r=".6"/>', '/trend/': '<path d="M12 3.5l2.4 5 5.4.6-4 3.7 1.1 5.4L12 15.5l-4.9 2.7 1.1-5.4-4-3.7 5.4-.6z"/>', '/cut.html': '<circle cx="6.5" cy="6.5" r="2.5"/><circle cx="6.5" cy="17.5" r="2.5"/><path d="M8.6 8 20 19M8.6 16 20 5"/>', '/sajin.html': '<path d="M3.5 8.5A2.5 2.5 0 0 1 6 6h1.7l1.4-1.9h5.8L16.3 6H18a2.5 2.5 0 0 1 2.5 2.5v8.5A2.5 2.5 0 0 1 18 19.5H6A2.5 2.5 0 0 1 3.5 17z"/><circle cx="12" cy="12.6" r="3.5"/>', '/video/': '<rect x="3" y="5.5" width="18" height="13" rx="3"/><path d="M10.5 9.5v5l4.5-2.5z"/>', '/dome.html': '<path d="M3.5 17V8h10v9"/><path d="M13.5 11h4l3 3v3h-7"/><circle cx="7.5" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>', '/sigong.html': '<path d="M14 6.5a4 4 0 0 0-5 5L4 16.5 7.5 20l5-5a4 4 0 0 0 5-5l-2.5 2.5-2.5-.5-.5-2.5z"/>'}

# PC 상단 메뉴: 묶음 + 펼침(모바일은 NAV 그대로)
DNAV = [
    ("자재·가격", "/jaryo/", [("/jaryo/", "전체 자재", "목재·합판·내장·외장·철물 전부"), ("/price.html", "기준가", "매장 소매 기준가 한눈에"), ("/tteori/", "떨이몰", "자투리·B급 싸게 가져가기"), ("/sajin.html", "사진으로 찾기", "사진 찍으면 비슷한 자재 찾기")]),
    ("재단·계산", "/cut.html", [("/cut.html", "목재 재단", "원하는 크기로 재단 미리보기"), ("/calc.html", "자재비 계산기", "몇 장·몇 평 필요한지 계산")]),
    ("DIY·시공법", "/mandeul/", [("/mandeul/", "DIY 만들기", "가구·데크 자재와 재단 크기"), ("/sigongbeop/", "자재 시공법", "붙이는 순서·주의할 점"), ("/video/", "영상", "현장 시공·자재 영상")]),
    ("인테리어", "/gonggan/", [("/doumi.html", "셀프 인테리어 도우미", "질문 4개로 필요한 것 한 번에"), ("/apt/", "전국 아파트별 자재", "우리 단지 연식에 맞는 자재"), ("/gonggan/", "공간 사진", "사진 속 + 누르면 자재·시공법"), ("/trend/", "인테리어 트렌드", "스타일별 도어·벽재·바닥")]),
    ("시공·도매", "/sigong.html", [("/sigong.html", "시공", "월드아키텍쳐 직접 시공"), ("/yeongyeol/", "시공팀 연결", "공정별 시공팀 연결"), ("/dome.html", "도매·납품", "업체·현장 도매 회원")]),
    ("소식", "/news/", []),
]
def _dnav(active):
    o = ""
    for t, h, sub in DNAV:
        on = active == h or any(active == x[0] for x in sub)
        if not sub:
            o += f'<div class="dg"><a class="dt{" on" if on else ""}" href="{h}">{t}</a></div>'; continue
        o += (f'<div class="dg"><a class="dt{" on" if on else ""}" href="{h}" aria-haspopup="true">{t}<i class="dc"></i></a><div class="dm">'
              + "".join(f'<a href="{a}"{" class=on" if active == a else ""}><svg class="ni" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{NAVI.get(a, "")}</svg><span><b>{n}</b><small>{d}</small></span></a>' for a, n, d in sub)
              + '</div></div>')
    return f'<nav class="dnav" aria-label="주 메뉴">{o}<a class="dv" href="/visit.html">매장 안내</a></nav>'
_GTHC = {}
def _gth(src, w=640, sub="t"):
    k = (src, w, sub)
    if k not in _GTHC: _GTHC[k] = _gth0(src, w, sub)
    return _GTHC[k]
def _ggsq(src, x, y):
    # 정사각형으로 잘라 보여 줄 때 + 위치를 잘린 화면에 맞춤(밖이면 None)
    try:
        from PIL import Image as _I
        fp = f"{ROOT}{src}" if src.startswith("/assets/") else None
        w, h = _I.open(fp).size if fp and os.path.exists(fp) else (1, 1)
    except Exception:
        w, h = 1, 1
    if w > h: x = (x / 100 * w - (w - h) / 2) / h * 100
    elif h > w: y = (y / 100 * h - (h - w) / 2) / w * 100
    return (round(x, 1), round(y, 1)) if 3 <= x <= 97 and 3 <= y <= 97 else None
def _gth0(src, w, sub):
    # 공간 사진 미리보기(작은 사진) — 우리 사진만, 없으면 만들고 실패하면 원본
    _yl = src.startswith("https://s3.ap-northeast-2.amazonaws.com/younglim-bucket/")
    if not (src.startswith("/assets/gonggan/") or _yl): return src
    nm = src.rsplit("/", 1)[1]; rel = f"assets/gonggan/{sub}/{nm}"
    if _yl:  # 영림 공간 사진(회사 허락) — 원본을 한 번 받아 두고 작은 사진을 만듦
        org = f"{ROOT}/assets/gonggan/yl/{nm}"
        if src in _GTHC.get("_fail", ()): return src
        if not os.path.exists(org):
            try:
                import urllib.request
                os.makedirs(os.path.dirname(org), exist_ok=True)
                dat = urllib.request.urlopen(urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"}), timeout=8).read()
                if len(dat) < 5000: return src
                open(org, "wb").write(dat)
            except Exception:
                _GTHC.setdefault("_fail", set()).add(src); return src
        srcf = org
    else:
        srcf = f"{ROOT}{src}"
    for base in (ROOT, OUT):
        dst = f"{base}/{rel}"
        if not os.path.exists(dst):
            try:
                from PIL import Image as _I
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                im = _I.open(srcf).convert("RGB"); im.thumbnail((w, w)); im.save(dst, quality=78, optimize=True, progressive=True)
            except Exception:
                return src
    return "/" + rel
_PSEEN = set()
POPEN = set()  # 내용이 충분해 검색에 여는 제품 상세(/p/)
VTHIN = set(l.strip() for l in open(f"{ROOT}/data/vthin.txt", encoding="utf-8")) if os.path.exists(f"{ROOT}/data/vthin.txt") else set()
def _noidx(path):
    if path == "price-change.html" and not _HASCHG: return True
    if path == "r/index.html": return True  # 리뷰 남기기 안내(QR용) — 검색에 낼 내용 없음
    # 얇거나 다른 페이지와 거의 같은 페이지는 검색 제외(사람은 볼 수 있음) — 구글 '크롤링됨-색인 안 됨' 줄이기
    if path.startswith("p/"): return path not in POPEN
    if re.match(r"(daejeon|sejong)/(?!index\.html)[^/]+\.html$", path): return True  # 대전·세종 × 자재 = /jajae/ 와 거의 같음
    if path.startswith("v/") and path[2:-5] in VTHIN: return True
    if re.match(r"bupum/samu(-\d+)?\.html$", path): return True
    if re.match(r"bupum/(?!index\.html)[a-z]+(-\d+)?\.html$", path): return True  # 철물박사 분류 목록 100여 쪽: 원 판매처와 같은 목록이라 구글 '크롤링됨-색인 안 됨'(11/18 확인) — 사람은 그대로 보고, 크롤링은 우리만의 페이지로
    if path.startswith("bupum/p/") and path != "bupum/p/index.html": return True  # 철물박사 상품 6천여 개: 원 판매처와 같은 사진·이름이라 구글이 색인 안 함 — 크롤링을 우리만의 페이지로  # 사무용품: 우리 업종과 무관 — 크롤링 예산 낭비
    return False
def _tshort(t):
    # 60자 넘는 제목: 끝의 업체명은 두고, 나열·부제부터 줄임(검색 결과에서 잘리지 않게)
    if len(t) <= 60: return t
    main, suf = (t.rsplit(" | ", 1)[0], " | " + t.rsplit(" | ", 1)[1]) if " | " in t else (t, "")
    lim = 60 - len(suf)
    for sep in (", ", " | ", " — ", " "):
        while len(main) > lim and sep in main: main = main.rsplit(sep, 1)[0].rstrip(" ,·—")
        if len(main) <= lim: break
    if len(main) > lim: main = main[:lim - 1] + "…"
    return main + suf
_SHR = ('<section class="wrap sec shr"><p class="shrt">도움이 됐다면 <b>필요한 분께 보내 주세요</b></p>'
        '<div class="shrb"><button type="button" class="shx" data-s="os">공유하기</button>'
        '<button type="button" class="shx" data-s="copy">링크 복사</button>'
        '<button type="button" class="shx nv" data-s="naver">네이버</button>'
        '<button type="button" class="shx bd" data-s="band">밴드</button>'
        '<button type="button" class="shx ig" data-s="insta">인스타</button>'
        '<button type="button" class="shx fb" data-s="fb">페이스북</button></div></section>')


PGMETA = {}


_REL = {  # 새 검색용 페이지로 가는 내부 링크(관련 있는 기존 페이지에만)
    **{k: [("/gonggan/", "공간 사진 둘러보기 — 사진 속 + 누르면 자재·시공법")] for k in ("trend/index.html", "qna/index.html", "younglim/jungmun.html", "younglim/jungmun-slim.html", "younglim/maru.html", "younglim/wall.html", "younglim/door-apel.html", "sigongbeop/index.html", "jaryo/maru.html", "jaryo/jipseong.html", "jaryo/door.html", "visit.html")},
    **{f"{d}/index.html": [(f"/{d}/p/", "제품별 자세히 보기(사진·규격)")] for d in ("younglim", "yerim", "shenu", "bondex", "geonjae", "suip", "bupum", "taka", "nichiha")},
    "deck-pis.html": [("/pis-gilee.html", "피스 길이 고르는 법(전체)"), ("/seokgo-pis.html", "석고보드 피스")],
    "seokgo-pis.html": [("/pis-gilee.html", "피스 길이 고르는 법(전체)"), ("/deck-pis.html", "데크 피스")],
    "jajae/hardware.html": [("/bigyo/taka-vs-pis.html", "타카 vs 피스"), ("/pis-gilee.html", "피스 길이 고르는 법"), ("/deck-pis.html", "데크 피스")],
    "gyugyeok.html": [("/pis-gilee.html", "피스 길이 고르는 법"), ("/bangbu-gyugyeok.html", "방부목 규격표"), ("/muge.html", "자재 무게 계산기"), ("/deck-pis.html", "데크 피스 길이·개수"), ("/bigyo/gypsum-vs-hapan-wall.html", "석고보드 vs 합판 벽")],
    "calc.html": [("/muge.html", "자재 무게 계산기"), ("/deck-pis.html", "데크 피스 개수"), ("/island-size.html", "아일랜드 식탁 사이즈")],
    "deck-gyesan.html": [("/deck-pis.html", "데크 피스 길이·개수"), ("/bangbu-gyugyeok.html", "방부목 규격표"), ("/muge.html", "자재 무게(용달 몇 번?)")],
    "jaedan-bi.html": [("/jaedan-baesong.html", "재단해서 전국 배송"), ("/mokgongso.html", "근처 목공소 대신 목재 재단"), ("/muge.html", "자재 무게 계산기"), ("/island-size.html", "아일랜드 식탁 사이즈")],
    "cut.html": [("/mokgongso.html", "목재 재단(목공소)"), ("/muge.html", "자재 무게 계산기")],
    "baesong.html": [("/jaedan-baesong.html", "원하는 크기로 재단해서 전국 배송"), ("/muge.html", "자재 무게 계산기 — 1톤에 몇 장")],
    "jajae/molding.html": [("/bigyo/molding-types.html", "몰딩 종류 비교")],
    "issue/winter-gyeolro.html": [("/qna/beranda-danyeol.html", "베란다 단열 셀프"), ("/qna/bukjjok-byeok-gyeolro.html", "북쪽 방 벽 결로"), ("/qna/changgo-danyeol.html", "창고·작업실 겨울 단열"), ("/qna/aircon-gumeong.html", "에어컨 배관 구멍 막기")],
    "issue/hanpa-dongpa-daebi.html": [("/qna/beranda-danyeol.html", "베란다 단열 셀프"), ("/qna/changgo-danyeol.html", "창고 겨울 단열")],
    "qna/eboard-dobae-vs-paint.html": [("/bigyo/isopink-vs-eboard.html", "아이소핑크 vs 이보드")],
    "qna/molding-ireum.html": [("/bigyo/mdf-vs-pvc-molding.html", "MDF 몰딩 vs PVC 몰딩")],
    "qna/cement-board.html": [("/bigyo/cement-vs-gypsum-board.html", "시멘트보드 vs 석고보드")],
    "qna/jeoksammok.html": [("/bigyo/jeoksammok-vs-bangbu.html", "적삼목 vs 방부목")],
    "qna/pombond-sseugi.html": [("/bigyo/foam-ilhoe-vs-gun.html", "일회용 폼 vs 건용 폼")],
    "qna/munteul-joint.html": [("/bigyo/foam-ilhoe-vs-gun.html", "일회용 폼 vs 건용 폼"), ("/qna/pombond-sseugi.html", "폼본드 쏘는 법")],
    "bigyo/gypsum-types.html": [("/knauf/seokgo.html", "크나우프 석고보드 전 종류 사진"), ("/gyugyeok/seokgo.html", "석고보드 규격표"), ("/gagyeok/seokgo-gagyeok.html", "석고보드 가격·1평 몇 장"), ("/qna/bangsu-seokgo.html", "방수석고보드 쓰는 곳"), ("/qna/banghwa-seokgo.html", "방화석고보드 쓰는 곳"), ("/bigyo/seokgo-95-vs-125.html", "9.5T vs 12.5T")],
    "jajae/sound.html": [("/bigyo/heupeum-board.html", "흡음보드 vs 흡음재"), ("/gagyeok/heupeum-gagyeok.html", "흡음보드 가격·1평 몇 장")],
    "bigyo/heupeum-board.html": [("/gagyeok/heupeum-gagyeok.html", "흡음보드 가격·1평 몇 장"), ("/sigongbeop/heumeum-byeok.html", "흡음보드 시공 순서")],
    "gagyeok/heupeum-gagyeok.html": [("/bigyo/heupeum-board.html", "흡음보드 vs 흡음재 — 종류 비교"), ("/bigyo/sound-types.html", "방음·흡음·차음재 비교")],
    "jajae/hinoki.html": [("/bigyo/tempa-vs-ruba.html", "템바보드 vs 루바")],
    "jajae/gypsum.html": [("/bigyo/gypsum-vs-hapan-wall.html", "석고보드 vs 합판 벽"), ("/muge.html", "석고보드 무게")],
    "jajae/hapan.html": [("/muge.html", "합판 무게"), ("/bigyo/gypsum-vs-hapan-wall.html", "석고보드 vs 합판 벽")],
    "jajae/bangbu.html": [("/bigyo/bangbu-vs-gujo.html", "방부목 vs 구조목"), ("/bangbu-gyugyeok.html", "방부목 규격표"), ("/deck-pis.html", "데크 피스")],
    "jajae/jipseong.html": [("/bigyo/mdf-vs-jipseong.html", "MDF vs 집성판"), ("/island-size.html", "아일랜드 식탁 사이즈")],
    "jajae/mdf.html": [("/bigyo/mdf-vs-jipseong.html", "MDF vs 집성판")],
    "jajae/gujo.html": [("/bigyo/bangbu-vs-gujo.html", "방부목 vs 구조목")],
    "taka/index.html": [("/bigyo/taka-vs-pis.html", "타카 vs 피스"), ("/pis-gilee.html", "피스 길이 고르는 법")],
    "mandeul/aillaendeu.html": [("/island-size.html", "아일랜드 식탁 사이즈 — 높이·깊이·통로")],
    "sigongbeop/seokgo-byeok.html": [("/seokgo-pis.html", "석고보드 피스 길이·간격·개수"), ("/bigyo/gypsum-vs-hapan-wall.html", "석고보드 vs 합판 벽")],
    "sigongbeop/seokgo-cheonjang.html": [("/seokgo-pis.html", "석고보드 피스 길이·간격·개수")],
    "gagyeok/seokgo-gagyeok.html": [("/seokgo-pis.html", "석고보드 피스 개수"), ("/muge.html", "석고보드 무게")],
    "sigongbeop/molding-georebatgi.html": [("/bigyo/molding-types.html", "몰딩 종류 비교")],
    "sigongbeop/tempa-byeok.html": [("/bigyo/tempa-vs-ruba.html", "템바보드 vs 루바")],
    "sigongbeop/heumeum-byeok.html": [("/bigyo/heupeum-board.html", "흡음보드 vs 흡음재"), ("/gagyeok/heupeum-gagyeok.html", "흡음보드 가격·1평 몇 장")],
    "sigongbeop/hapdeck-sigong.html": [("/deck-pis.html", "데크 피스·클립")],
    "mandeul/deck.html": [("/deck-pis.html", "데크 피스 길이·개수"), ("/bangbu-gyugyeok.html", "방부목 규격표")],
    "gagyeok/deck-gagyeok.html": [("/bangbu-gyugyeok.html", "방부목 규격표"), ("/deck-pis.html", "데크 피스")],
    "gagyeok/molding-gagyeok.html": [("/bigyo/molding-types.html", "몰딩 종류 비교")],
    "gagyeok/tempa-board.html": [("/bigyo/tempa-vs-ruba.html", "템바보드 vs 루바")],
    "gagyeok/jipseong-gagyeok.html": [("/island-size.html", "아일랜드 식탁 사이즈")],
}
for _k, _v in {'qna/2x4-cheolmul.html': [('/qna/2x4-size.html', '2x4 사이즈')], 'qna/nagyeopsong-gakjae.html': [('/qna/lvl-tteut.html', 'LVL 뜻')], 'qna/lvl-tteut.html': [('/qna/clt-glulam.html', 'CLT·글루램')], 'qna/clt-glulam.html': [('/qna/lvl-tteut.html', 'LVL 뜻')], 'gyugyeok/gujo.html': [('/qna/2x4-size.html', '2x4 실제 치수'), ('/qna/2x4-cheolmul.html', '투바이포 철물')], 'gagyeok/gakjae-gagyeok.html': [('/qna/2x4-size.html', '2x4 사이즈'), ('/qna/darugi-1dan.html', '다루끼 1단 몇 개')], 'yongeo/darugi.html': [('/qna/darugi-1dan.html', '다루끼 1단 몇 개')], 'yongeo/jeoksammok.html': [('/qna/jeoksammok-deck.html', '적삼목 데크·사이딩')], 'pyeong.html': [('/qna/1pyeong-keugi.html', '1평 크기')], 'yongeo/rube.html': [('/qna/rube-gyesan.html', '루베 계산법')]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {'qna/banself-gamri.html': [('/qna/banself-tteut.html', '반셀프 인테리어 뜻')], 'gongjeong.html': [('/qna/banself-tteut.html', '반셀프 인테리어 뜻'), ('/qna/banself-gamri.html', '반셀프 감리 체크')], 'gagyeok/jipseong-gagyeok.html': [('/qna/merbau-seonban.html', '멀바우 선반·테이블'), ('/qna/redpine-gagu.html', '레드파인 가구')], 'qna/jajak-hapan.html': [('/qna/jajak-sangpan.html', '자작나무 상판')], 'jajae/chimmok.html': [('/qna/chimmok-bench.html', '침목 벤치')], 'qna/hardwood-deck.html': [('/qna/ipe-deck.html', '이페 데크')], 'qna/mokgong-ipmun-jangbi.html': [('/qna/gagu-mandeulgi-jaeryo.html', '가구 만들기 재료'), ('/qna/holsaw-sayong.html', '홀쏘 사용법'), ('/qna/samgakja-sayong.html', '삼각자 사용법')]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {'qna/beranda-nusu.html': [('/qna/changmun-nusu.html', '창문 누수')], 'qna/changmun-gyeolro.html': [('/qna/changmun-nusu.html', '창문 누수')], 'qna/sash-silicone.html': [('/qna/changmun-nusu.html', '창문 누수 해결')], 'qna/asphalt-shingle.html': [('/qna/jibung-nusu.html', '지붕 누수 잡는 법')], 'qna/darak-interior.html': [('/qna/darak-danyeol.html', '다락 단열')], 'qna/yoksil-cheonjang.html': [('/qna/yoksil-danyeol.html', '욕실 단열')], 'gagyeok/danyeol-gagyeok.html': [('/qna/darak-danyeol.html', '다락 단열'), ('/qna/yoksil-danyeol.html', '욕실 단열')]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {'qna/bubun-dobae.html': [('/qna/byeokji-jjijeojim.html', '벽지 찢어짐 보수')], 'qna/cheonjang-dobae-tteoreojim.html': [('/qna/bubun-dobae.html', '부분 도배')], 'qna/self-dobae.html': [('/qna/bubun-dobae.html', '부분 도배'), ('/qna/chobaeji.html', '초배지'), ('/qna/byeokji-jjijeojim.html', '벽지 찢어짐 보수')], 'qna/handycoat.html': [('/qna/mot-gumeong-meugi.html', '못 구멍 메우기')], 'qna/cheonjang-cheojim.html': [('/qna/cheonjang-dobae-tteoreojim.html', '천장 도배 떨어짐')], 'dobae-jangpan.html': [('/qna/bubun-dobae.html', '부분 도배 셀프'), ('/qna/chobaeji.html', '도배 초배지')]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {'qna/bangbadak-gallajim.html': [('/qna/self-leveling.html', '셀프레벨링')], 'qna/supyeong-moltal.html': [('/qna/self-leveling.html', '셀프레벨링')], 'qna/jangpan-self.html': [('/qna/jangpan-duggae.html', '장판 두께 고르기')], 'qna/jangpan-deultteum.html': [('/qna/jangpan-gompang.html', '장판 곰팡이')], 'qna/kangmaru-eolluk.html': [('/qna/maru-geulkim-bosu.html', '마루 긁힘 보수')], 'sigongbeop/decotile.html': [('/qna/decotile-deultteum.html', '데코타일 들뜸 보수')], 'bigyo/kangmaru-vs-kanghwa.html': [('/qna/maru-cheolgeo.html', '마루 철거')]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {'qna/bangmun-cheojim.html': [('/qna/mun-gyeongcheop-gyoche.html', '문 경첩 교체')], 'qna/mun-kkiik.html': [('/qna/bangmun-cheojim.html', '방문 처짐')], 'qna/mun-gyeongcheop-gyoche.html': [('/qna/bangmun-cheojim.html', '방문 처짐')], 'qna/bangmun-doorlock.html': [('/qna/mungori-gyoche.html', '문고리 교체')], 'gagyeok/door-gagyeok.html': [('/qna/mungori-gyoche.html', '문고리 교체'), ('/qna/bangmun-cheojim.html', '방문 처짐 고치기')], 'qna/hyeongwanmun-cheojim.html': [('/qna/bangmun-cheojim.html', '방문 처짐')], 'qna/bangmun-sonjabi-sal-got.html': [('/qna/mungori-gyoche.html', '문고리 교체 방법')]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {'yongeo/deungbox.html': [('/qna/deungbox-sigong.html', '등박스 시공 순서')], 'qna/uomul-cheonjang-molding.html': [('/qna/uomul-cheonjang-ganjeop.html', '우물천장 간접조명')], 'qna/dayongdosil-seonban.html': [('/qna/setaksil-seonban.html', '세탁실 선반')], 'mandeul/chimdae.html': [('/qna/family-chimdae.html', '패밀리침대 만들기')], 'qna/beranda-danyeol.html': [('/qna/beranda-changgojang.html', '베란다 창고장')]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {'gongjeong.html': [('/qna/dobae-jangpan-sunseo.html', '도배·장판 순서'), ('/qna/molding-dobae-sunseo.html', '몰딩·도배 순서'), ('/qna/film-dobae-sunseo.html', '필름·도배 순서'), ('/qna/interior-mokgong-tteut.html', '인테리어 목공이란')], 'yeongyeol/mokgong.html': [('/qna/interior-mokgong-tteut.html', '인테리어 목공 뜻'), ('/qna/cheonjang-mokgong-bangbeop.html', '천장 목공 방법')], 'gabyeok-gyesan.html': [('/qna/samusil-kanmagi.html', '사무실 칸막이')], 'yeongyeol/dobae.html': [('/qna/dobae-jangpan-sunseo.html', '도배·장판 순서')], 'yeongyeol/film.html': [('/qna/film-dobae-sunseo.html', '필름·도배 순서')]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {'gagyeok/seokgo-gagyeok.html': [('/qna/seokgo-duggae.html', '석고보드 두께 종류'), ('/qna/seokgo-sigong-juui.html', '석고보드 시공 주의사항')], 'bigyo/gypsum-types.html': [('/qna/seokgo-duggae.html', '석고보드 두께 9.5T·12.5T')], 'gyugyeok/seokgo.html': [('/qna/seokgo-duggae.html', '석고보드 두께 종류')], 'gagyeok/jipseong-gagyeok.html': [('/qna/jipseongmok-jongryu.html', '집성목 종류'), ('/qna/wonmok-jongryu.html', '원목 종류 비교')], 'gyugyeok/jipseong.html': [('/qna/jipseongmok-jongryu.html', '집성목 종류와 가격')], 'qna/mokjae-jongryu.html': [('/qna/wonmok-jongryu.html', '원목 종류 비교'), ('/qna/jipseongmok-jongryu.html', '집성목 종류')], 'gagyeok/deck-gagyeok.html': [('/qna/bangbumok-jongryu.html', '방부목 종류·규격'), ('/qna/deck-cheolgeo.html', '데크 철거'), ('/qna/nongmak-deck.html', '농막 데크')], 'gyugyeok/deck.html': [('/qna/bangbumok-jongryu.html', '방부목 종류·규격')], 'gagyeok/molding-gagyeok.html': [('/qna/georebatgi-jongryu.html', '걸레받이 종류'), ('/qna/cherry-molding-paint.html', '체리몰딩 페인트')], 'bigyo/molding-types.html': [('/qna/georebatgi-jongryu.html', '걸레받이 종류')], 'gagyeok/heupeum-gagyeok.html': [('/qna/heubeumjae-jongryu.html', '흡음재 종류')], 'bigyo/heupeum-board.html': [('/qna/heubeumjae-jongryu.html', '흡음재 종류')], 'gagyeok/danyeol-gagyeok.html': [('/qna/jibung-danyeol-jongryu.html', '지붕 단열재 종류'), ('/qna/oebyeok-danyeol-self.html', '외벽 단열 셀프'), ('/qna/glasswool-milldo.html', '그라스울 48K 뜻')], 'bigyo/insulation-types.html': [('/qna/glasswool-milldo.html', '그라스울 밀도'), ('/qna/jibung-danyeol-jongryu.html', '지붕 단열재 종류')], 'gagyeok/hapan-gagyeok.html': [('/qna/misong-hapan.html', '미송합판'), ('/qna/bangsu-hapan-jaedan.html', '방수합판 재단')], 'gyugyeok/gakjae.html': [('/qna/gakjae-gyugyeok-bogi.html', '각재 규격 보는 법')], 'gagyeok/gakjae-gagyeok.html': [('/qna/gakjae-gyugyeok-bogi.html', '각재 규격 보는 법')], 'jaedan-bi.html': [('/qna/sason-jaedan.html', '각도·사선 재단'), ('/qna/jaedan-jedan.html', '재단·제단 차이')], 'cut.html': [('/qna/sason-jaedan.html', '각도·사선 재단')], 'sigongbeop/decotile.html': [('/qna/decotile-cheolgeo.html', '데코타일 철거')], 'sigongbeop/yoksil-tile.html': [('/qna/yoksil-tile-deotbang.html', '욕실 타일 덧방')]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {"qna/munteul-jegeo-self.html": [("/qna/munteul-jegeo-hu-mijang.html", "문틀 제거 후 마감")], "qna/munteul-jegeo-hu-mijang.html": [("/qna/munteul-jegeo-self.html", "문틀 제거 셀프")], "qna/seokgo-wi-tile.html": [("/qna/hapan-badak-tile.html", "합판 위 타일")], "qna/ruba-vs-hapan-cheonjang.html": [("/qna/hapan-cheonjang-dobae.html", "합판 천장 도배")], "qna/seonban-cheojim.html": [("/qna/hapan-seonban-duggae.html", "합판 선반 두께")], "qna/hapan-gagu.html": [("/qna/hapan-chaeksang.html", "합판 책상 만들기")], "qna/mokjae-oil-jongryu.html": [("/qna/mokjae-bangsu-coating.html", "목재 방수 코팅")], "qna/deck-bosu.html": [("/qna/namu-sseogeum-bangji.html", "나무 썩음 방지")], "qna/sangpan-mul-eolluk.html": [("/qna/wonmok-sangpan-bokwon.html", "원목 상판 복원")], "qna/mdf-paint.html": [("/qna/mdf-seonban-bangsu.html", "MDF 선반 방수")]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {"qna/anbang-jungmun.html": [("/qna/geosil-jungmun.html", "거실 중문")], "qna/munteul-jegeo-self.html": [("/qna/munteul-jegeo-hu-mijang.html", "문틀 제거 후 마감")], "qna/seokgo-putty.html": [("/qna/seokgo-gumeong-bosu.html", "석고보드 구멍 보수")], "qna/seokgo-anka.html": [("/qna/seokgo-gumeong-bosu.html", "석고보드 구멍 보수")], "sigongbeop/munteul-gyoche.html": [("/qna/munteul-jegeo-self.html", "문틀 제거 셀프")], "gagyeok/hapan-gagyeok.html": [("/qna/beniyeo-hapan-tteut.html", "베니어 합판 뜻"), ("/qna/rawang-hapan.html", "라왕 합판")], "yongeo/bulyeon.html": [("/qna/junbulyeon-tteut.html", "준불연 뜻")], "yongeo/rawang.html": [("/qna/rawang-hapan.html", "라왕 합판")], "qna/jajak-hapan.html": [("/qna/rawang-hapan.html", "라왕 합판")], "gagyeok/jipseong-gagyeok.html": [("/qna/oak-walnut-sonamu.html", "오크·월넛·소나무 차이")], "qna/mokjae-jongryu.html": [("/qna/oak-walnut-sonamu.html", "오크·월넛·소나무 원목 차이")], "mandeul/chaekjang.html": [("/qna/wonmok-sunapjang-mandeulgi.html", "원목 수납장 만들기")]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {"qna/hwajangsil-mulmagi.html": [("/qna/hwajangsil-mun-gyoche.html", "화장실 문 교체")], "qna/wonmok-paint.html": [("/qna/wonmok-paint-beotgigi.html", "원목 페인트 벗기기")], "qna/anbang-jungmun.html": [("/qna/jungmun-suri.html", "중문 수리")], "qna/geosil-jungmun.html": [("/qna/anbang-jungmun.html", "안방 중문"), ("/qna/jungmun-suri.html", "중문 수리")], "jeonguk/chungbuk.html": [("/qna/cheongju-mokjae.html", "청주 목재 판매·재단")], "jeonguk/chungnam.html": [("/qna/cheonan-mokjae.html", "천안 목재 구입"), ("/qna/sejong-mokjae.html", "세종 목재")], "jaedan-bi.html": [("/qna/hapan-jaedan-biyong.html", "합판 재단 비용")], "qna/hapan-jaedan-jumun.html": [("/qna/hapan-jaedan-biyong.html", "합판 재단 비용")], "qna/mokjae-gumae.html": [("/qna/mokjaeso-tteut.html", "목재소 뜻")], "gagyeok/deck-gagyeok.html": [("/qna/bangbumok-panmaecheo.html", "방부목 판매처")], "gagyeok/seokgo-gagyeok.html": [("/qna/seokgo-panmaecheo.html", "석고보드 판매처")], "gagyeok/molding-gagyeok.html": [("/qna/molding-panmaecheo.html", "몰딩 판매처")], "local/jungmun-daejeon.html": [("/qna/geosil-jungmun.html", "거실 중문"), ("/qna/anbang-jungmun.html", "안방 중문"), ("/qna/jungmun-suri.html", "중문 수리")], "qna/mutagong-jungmun.html": [("/qna/geosil-jungmun.html", "거실 중문")]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {"qna/bangmun-ripom-mdf.html": [("/qna/bangmun-ripom.html", "방문 리폼")], "qna/hwajangsil-mun-gyoche.html": [("/qna/hwajangsil-mulmagi.html", "화장실 물막이")], "qna/yoksilmun-buksik.html": [("/qna/hwajangsil-mun-gyoche.html", "화장실 문 교체")], "qna/deck-tile.html": [("/qna/beranda-badakjae.html", "베란다 바닥재")], "gagyeok/deck-gagyeok.html": [("/qna/oksang-deck.html", "옥상 데크"), ("/qna/terrace-deck-chai.html", "테라스와 데크 차이")], "qna/oksang-deck.html": [("/qna/terrace-deck-chai.html", "테라스와 데크 차이")], "qna/jangpan-self.html": [("/qna/jangpan-cheolgeo.html", "장판 셀프 철거")], "qna/decotile-self-ganeung.html": [("/qna/decotile-junbimul.html", "데코타일 준비물")], "qna/paint-beotgyeojim.html": [("/qna/wonmok-paint-beotgigi.html", "원목 페인트 벗기기")], "qna/wonmok-paint-beotgigi.html": [("/qna/wonmok-paint.html", "원목 페인트 칠하기")], "qna/jesso.html": [("/qna/wonmok-paint.html", "원목 페인트 칠하기")], "qna/seokgo-putty.html": [("/qna/putty-jakeop-tteut.html", "퍼티 작업 뜻")], "qna/pis-jongryu.html": [("/qna/nasa-jongryu-myeongching.html", "나사 종류와 명칭")]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {"qna/sink-sangpan-bosu.html": [("/qna/sink-sangpan-sheet.html", "싱크대 상판 시트지")], "qna/jageunbang-kkumigi.html": [("/qna/mujiju-byeokseonban.html", "무지주 벽선반")], "qna/bangmun-ripom.html": [("/qna/bangmun-ripom-mdf.html", "방문 MDF 덧대기"), ("/qna/bangmun-sonjabi-sal-got.html", "방문 손잡이 고르기")], "qna/mun-sheetji.html": [("/qna/bangmun-ripom.html", "방문 리폼")], "qna/bangmun-paint.html": [("/qna/bangmun-ripom.html", "방문 리폼")], "qna/son-jabi-gyoche.html": [("/qna/bangmun-sonjabi-sal-got.html", "방문 손잡이 고르기")], "qna/chang-gyeolro.html": [("/qna/changmun-bangpung.html", "창문 방풍")], "qna/nongmak-danyeol.html": [("/qna/container-danyeol.html", "컨테이너 단열"), ("/qna/nongmak-naebu.html", "농막 내부 꾸미기")], "qna/siding-haji.html": [("/qna/siding-seolchi.html", "사이딩 설치 전체 순서")], "gagyeok/siding-gagyeok.html": [("/qna/siding-seolchi.html", "외벽 사이딩 설치 방법")], "cheolmul/mokjo.html": [("/qna/mokjo-jutaek-jajae.html", "목조주택 자재")], "qna/dressroom.html": [("/qna/otbang-mandeulgi.html", "옷방 만들기"), ("/qna/pantry-seonban.html", "팬트리 선반")], "qna/heupeum-partition.html": [("/qna/partition-seolchi.html", "파티션 설치")], "mandeul/patisyeon.html": [("/qna/partition-seolchi.html", "파티션 설치")]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {"qna/butbakijang-idong.html": [("/qna/butbakijang-cheolgeo.html", "붙박이장 셀프 철거")], "qna/sunapjang-mun-jejak.html": [("/qna/sunapjang-mun-dalgi.html", "수납장 문 달기")], "qna/sink-sangpan-sheet.html": [("/qna/sink-sangpan-bosu.html", "싱크대 상판 보수")], "qna/jageunbang-kkumigi.html": [("/qna/aibang-kkumigi.html", "아이방 꾸미기"), ("/qna/chimsil-byeok-kkumigi.html", "침실 벽 꾸미기")], "qna/seonban-bracket.html": [("/qna/mujiju-byeokseonban.html", "무지주 벽선반"), ("/qna/jubang-byeok-seonban.html", "주방 벽선반")], "mandeul/byeokseonban.html": [("/qna/mujiju-byeokseonban.html", "무지주 벽선반")], "qna/crown-molding.html": [("/qna/uomul-cheonjang-molding.html", "우물천장 몰딩")], "qna/molding-jegeo.html": [("/qna/uomul-cheonjang-molding.html", "우물천장 몰딩")], "qna/artwall-mandeulgi.html": [("/qna/artwall-jegeo.html", "아트월 제거")], "qna/sink-film.html": [("/qna/sink-sangpan-sheet.html", "싱크대 상판 시트지")], "qna/sink-sangpan-wonmok.html": [("/qna/sink-sangpan-bosu.html", "싱크대 상판 보수")], "mandeul/aillaendeu.html": [("/qna/island-siktak-jejak.html", "아일랜드 식탁 제작")], "qna/uija-heundeullim.html": [("/qna/namu-uija-ripom.html", "나무 의자 리폼")], "qna/drill-hanaro.html": [("/qna/drill-bit-kkiugi.html", "드릴 비트 끼우는 법")], "mandeul/aichaeksang.html": [("/qna/aibang-kkumigi.html", "아이방 꾸미기")], "qna/tempa-headboard.html": [("/qna/chimsil-byeok-kkumigi.html", "침실 벽 꾸미기")], "qna/camping-diy.html": [("/qna/camping-table-mandeulgi.html", "캠핑 테이블 만들기")], "mandeul/yangnyeomseonban.html": [("/qna/jubang-byeok-seonban.html", "주방 벽선반")]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {"qna/georebatgi-saek.html": [("/qna/georebatgi-gyoche.html", "걸레받이 교체")], "qna/butbakijang-self.html": [("/qna/butbakijang-cheolgeo.html", "붙박이장 셀프 철거"), ("/qna/butbakijang-idong.html", "붙박이장 옮기기")], "qna/butbakijang-cheolgeo.html": [("/qna/butbakijang-idong.html", "붙박이장 옮기기")], "qna/sunapjang-mun-dalgi.html": [("/qna/sunapjang-mun-jejak.html", "수납장 문 제작")], "qna/gyeongcheop-jongryu.html": [("/qna/sunapjang-mun-dalgi.html", "수납장 문 달기")], "qna/gujomok-seonban.html": [("/qna/changgo-seonban.html", "창고 선반 만들기")], "qna/dayongdosil-seonban.html": [("/qna/beranda-seonbanjang.html", "베란다 선반장 제작")], "qna/silicone-jegeo.html": [("/qna/yoksil-silicone.html", "욕실 실리콘 셀프"), ("/qna/sash-silicone.html", "샷시 실리콘")], "qna/silicone-jongryu.html": [("/qna/yoksil-silicone.html", "욕실 실리콘 셀프"), ("/qna/sash-silicone.html", "샷시 실리콘")], "qna/taka-jongryu.html": [("/qna/taka-sayongbeop.html", "타카 사용법")], "qna/mun-sheetji.html": [("/qna/munteul-sheet-bosu.html", "문틀 시트지 보수")], "qna/bangbu-deck-gyedan.html": [("/qna/deck-gyedan-pok.html", "데크 계단 폭·간격")], "gagyeok/hapan-gagyeok.html": [("/qna/hapan-gagu.html", "합판 가구 만들기")], "qna/danish-oil.html": [("/qna/mokjae-oil-jongryu.html", "목재 오일 종류")], "gagyeok/oilstain.html": [("/qna/mokjae-oil-jongryu.html", "목재 오일 종류")], "mandeul/hyeongwanbench.html": [("/qna/hyeongwan-sunap-bench.html", "현관 수납 벤치")], "mandeul/minichanggo.html": [("/qna/changgo-seonban.html", "창고 선반 만들기")]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {"qna/georebatgi-saek.html": [("/qna/georebatgi-gyoche.html", "걸레받이 교체")], "qna/georebatgi-gyoche.html": [("/qna/georebatgi-saek.html", "걸레받이 색상")], "qna/georebatgi-ppaegi.html": [("/qna/georebatgi-gyoche.html", "걸레받이 교체"), ("/qna/georebatgi-saek.html", "걸레받이 색상")], "qna/bangmun-teumsae.html": [("/qna/bangmun-bangeum.html", "방문 방음")], "qna/son-jabi-gyoche.html": [("/qna/bangmun-jamgyeosseul-ttae.html", "방문이 잠겼을 때")], "bigyo/slide-vs-swing-jungmun.html": [("/qna/jungmun-swing.html", "스윙 중문"), ("/qna/danjo-jungmun.html", "단조 중문")], "mandeul/gabyeok.html": [("/qna/gabyeok-mun.html", "가벽에 문 달기"), ("/qna/gabyeok-otjang.html", "가벽 옷장"), ("/qna/tempa-gabyeok.html", "템바보드 가벽")], "bigyo/heupeum-board.html": [("/qna/heupeum-partition.html", "흡음 파티션")], "bigyo/gakjae-types.html": [("/qna/gakjae-panjae-chai.html", "각재와 판재 차이"), ("/qna/lvl-gakjae.html", "LVL 각재")], "sigongbeop/osb-byeok.html": [("/qna/osb-interior.html", "OSB 인테리어")], "gagyeok/tempa-board.html": [("/qna/tempa-sunapjang.html", "템바보드 수납장"), ("/qna/tempa-gabyeok.html", "템바보드 가벽")], "qna/bangbu-size.html": [("/qna/misong-bangbumok.html", "미송 방부목"), ("/qna/junggo-bangbumok.html", "중고 방부목")], "gagyeok/mdf-gagyeok.html": [("/qna/mdf-jumun-jejak.html", "MDF 주문제작"), ("/qna/mdf-box.html", "MDF 박스 만들기")], "mandeul/chimdae.html": [("/qna/pyeongsang-chimdae.html", "평상 침대")], "sigongbeop/ruba-byeok.html": [("/qna/ruba-panel.html", "루바 패널")]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {"qna/oilstain-color.html": [("/bigyo/oilstain-saek-gagyeok.html", "오일스테인 색상·용량별 가격")], "gagyeok/oilstain.html": [("/bigyo/oilstain-saek-gagyeok.html", "색상·용량별 가격 비교")], "qna/deck-oilstain-daeyongnyang.html": [("/bigyo/oilstain-saek-gagyeok.html", "오일스테인 용량별 가격")], "qna/hapan-edge.html": [("/qna/edge-film.html", "엣지필름 붙이는 법"), ("/qna/myeondae.html", "면대 뜻")], "yongeo/tubai.html": [("/qna/sanseunggak.html", "산승각 뜻")], "yongeo/darugi.html": [("/qna/sokdae.html", "속대 뜻")], "qna/goguchi.html": [("/qna/edge-film.html", "엣지필름"), ("/qna/myeondae.html", "면대")]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {"qna/glue-gun.html": [("/qna/spray-bond.html", "스프레이 본드")], "qna/silicone-jongryu.html": [("/bigyo/silicone-color-gagyeok.html", "실리콘 색·종류별 가격"), ("/qna/urethane-silicone.html", "우레탄 실리콘")], "qna/silicone-ssogi.html": [("/bigyo/silicone-color-gagyeok.html", "실리콘 색·종류별 가격")], "qna/pis-jongryu.html": [("/bigyo/pis-gyugyeok-gagyeok.html", "피스 규격별 가격"), ("/qna/magazine-pis.html", "매거진 피스")], "pis-gilee.html": [("/bigyo/pis-gyugyeok-gagyeok.html", "피스 규격별 가격")], "seokgo-pis.html": [("/qna/magazine-pis.html", "매거진 피스")], "qna/seokgo-putty.html": [("/qna/handycoat.html", "핸디코트")], "qna/taka-jongryu.html": [("/qna/gun-nail.html", "건네일")], "qna/mokgong-bond.html": [("/qna/spray-bond.html", "스프레이 본드"), ("/qna/glue-gun.html", "글루건")]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {"qna/overlay-hapan.html": [("/qna/munuimok-hapan.html", "무늬목 합판")], "qna/munuimok-hapan.html": [("/qna/overlay-hapan.html", "오버레이 합판")], "knauf/mineral.html": [("/qna/maitex-cheonjang.html", "마이텍스 천장재")], "qna/hapan-edge.html": [("/qna/goguchi.html", "고구찌 뜻")], "qna/pvc-sopit.html": [("/qna/raft-vent.html", "래프트벤트")], "yongeo/seokkarae.html": [("/qna/raft-vent.html", "래프트벤트")]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {"gagyeok/hapan-gagyeok.html": [("/bigyo/hapan-be-in-okume.html", "합판 베·인·오쿠메 차이"), ("/qna/taego-hapan.html", "태고합판(코팅합판)"), ("/qna/ojingeo-hapan.html", "오징어합판"), ("/qna/munuimok-hapan.html", "무늬목 합판")], "bigyo/hapan-types.html": [("/bigyo/hapan-be-in-okume.html", "합판 베·인·오쿠메 차이"), ("/qna/taego-hapan.html", "태고합판"), ("/qna/ojingeo-hapan.html", "오징어합판"), ("/qna/munuimok-hapan.html", "무늬목 합판")], "gyugyeok/hapan.html": [("/bigyo/hapan-be-in-okume.html", "합판 베·인·오쿠메 차이")]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {"gagyeok/tempa-board.html": [("/qna/tempa-sal-got.html", "템바보드 파는 곳")], "gagyeok/hinoki-ruba.html": [("/qna/hinoki-ruba-sal-got.html", "히노끼 루바 파는 곳")], "gagyeok/hapan-gagyeok.html": [("/qna/jajak-hapan-sal-got.html", "자작합판 파는 곳"), ("/qna/mokjae-soryang.html", "목재 소량 구매")], "gagyeok/danyeol-gagyeok.html": [("/qna/isopink-sal-got.html", "아이소핑크 파는 곳")], "gagyeok/seokgo-gagyeok.html": [("/qna/seokgo-natjang.html", "석고보드 낱장 구매")], "gagyeok/mdf-gagyeok.html": [("/qna/mdf-sal-got.html", "MDF 파는 곳")], "gagyeok/jipseong-gagyeok.html": [("/qna/jipseong-sal-got.html", "집성목 파는 곳")], "gagyeok/deck-gagyeok.html": [("/qna/bangbu-sal-got.html", "방부목 파는 곳")], "visit.html": [("/qna/mokjae-jumal.html", "주말에 목재 사는 곳"), ("/qna/mokjae-soryang.html", "목재 소량 구매")], "daejeon.html": [("/qna/mokjae-jumal.html", "주말 영업"), ("/qna/mokjae-soryang.html", "소량 구매")]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {"qna/1ton-hapan.html": [("/qna/hapan-muge.html", "합판 무게"), ("/qna/seokgo-muge.html", "석고보드 무게")], "qna/kangmaru-cheongso.html": [("/qna/kangmaru-eolluk.html", "강마루 얼룩")], "qna/deck-cheongso.html": [("/qna/bangbu-cheongso.html", "방부목 이끼 청소")], "qna/julnun-gompang.html": [("/qna/julnun-cheongso.html", "줄눈 청소")], "qna/film-deultteum.html": [("/qna/film-cheongso.html", "필름 청소")], "qna/ruba-oil.html": [("/qna/ruba-cheongso.html", "루바 청소")], "qna/tempa-paint.html": [("/qna/tempa-cheongso.html", "템바보드 청소")], "qna/wonmok-gagu-gompang.html": [("/qna/wonmok-gagu-cheongso.html", "원목 가구 청소")], "qna/bangmun-paint.html": [("/qna/mun-sonttae.html", "방문 손때")]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {"muge.html": [("/qna/hapan-muge.html", "합판 1장 무게"), ("/qna/seokgo-muge.html", "석고보드 1장 무게"), ("/qna/mdf-muge.html", "MDF 무게"), ("/qna/osb-muge.html", "OSB 무게"), ("/qna/jipseong-muge.html", "집성판 무게"), ("/qna/bangbu-muge.html", "방부목 무게"), ("/qna/gujomok-muge.html", "구조목 무게"), ("/qna/isopink-muge.html", "아이소핑크 무게"), ("/qna/1ton-hapan.html", "1톤 트럭 합판 몇 장"), ("/qna/seungyongcha-jajae.html", "승용차에 자재 싣기")], "baesong.html": [("/qna/1ton-hapan.html", "1톤 트럭 합판 몇 장"), ("/qna/seungyongcha-jajae.html", "승용차에 자재 싣기")], "gyugyeok/hapan.html": [("/qna/hapan-muge.html", "합판 1장 무게")], "gyugyeok/seokgo.html": [("/qna/seokgo-muge.html", "석고보드 무게")], "gyugyeok/mdf.html": [("/qna/mdf-muge.html", "MDF 무게")], "gyugyeok/jipseong.html": [("/qna/jipseong-muge.html", "집성판 무게")], "gyugyeok/gujo.html": [("/qna/gujomok-muge.html", "구조목 무게")], "jaedan-bi.html": [("/qna/seungyongcha-jajae.html", "승용차에 자재 싣기")]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {"qna/siktak-nopi.html": [("/bigyo/gagu-nopi.html", "가구 높이 표준")], "qna/chaeksang-nopi.html": [("/bigyo/gagu-nopi.html", "가구 높이 표준")], "qna/bench-nopi.html": [("/bigyo/gagu-nopi.html", "가구 높이 표준")], "qna/sink-nopi.html": [("/bigyo/gagu-nopi.html", "가구 높이 표준")], "qna/chimdae-nopi.html": [("/bigyo/gagu-nopi.html", "가구 높이 표준")], "qna/jakeopdae-nopi.html": [("/bigyo/gagu-nopi.html", "가구 높이 표준")], "qna/chaekjang-kan-nopi.html": [("/bigyo/sunap-gipi.html", "수납장 깊이 비교")], "qna/sinbaljang-gipi.html": [("/bigyo/sunap-gipi.html", "수납장 깊이 비교")], "qna/otjang-gipi.html": [("/bigyo/sunap-gipi.html", "수납장 깊이 비교")], "qna/sunap-ijeum-gipi.html": [("/bigyo/sunap-gipi.html", "수납장 깊이 비교"), ("/qna/otjang-gipi.html", "옷장 깊이")], "qna/seonban-ganggyeok.html": [("/bigyo/sunap-gipi.html", "수납장 깊이 비교")], "mandeul/teibeul.html": [("/qna/siktak-nopi.html", "식탁 높이")], "mandeul/aichaeksang.html": [("/qna/chaeksang-nopi.html", "책상 높이")], "mandeul/benchi.html": [("/qna/bench-nopi.html", "벤치 높이")], "mandeul/chaekjang.html": [("/qna/chaekjang-kan-nopi.html", "책장 칸 높이")], "mandeul/sinbaljang.html": [("/qna/sinbaljang-gipi.html", "신발장 깊이")], "mandeul/chimdae.html": [("/qna/chimdae-nopi.html", "침대 높이")], "mandeul/pyeongsang.html": [("/qna/pyeongsang-nopi.html", "평상 높이")], "mandeul/deck.html": [("/qna/deck-nopi.html", "데크 높이")], "mandeul/jakeopdae.html": [("/qna/jakeopdae-nopi.html", "작업대 높이")], "mandeul/hwajangdae.html": [("/qna/hwajangdae-nopi.html", "화장대 높이")], "mandeul/haenggeo.html": [("/qna/otjang-gipi.html", "옷장 깊이")]}.items(): _REL[_k] = _REL.get(_k, []) + _v
for _k, _v in {"gagyeok/deck-gagyeok.html": [("/bigyo/bangbu-deck-duggae.html", "방부목 데크 두께 비교"), ("/bigyo/hapdeck-duggae.html", "합성데크 사이즈 비교")], "bangbu-gyugyeok.html": [("/bigyo/bangbu-deck-duggae.html", "방부목 데크 두께 비교"), ("/bigyo/bangbu-gakjae-size.html", "방부목 각재 사이즈 비교")], "gagyeok/osb-gagyeok.html": [("/bigyo/osb-duggae.html", "OSB 두께 비교")], "gyugyeok/hapan.html": [("/bigyo/osb-duggae.html", "OSB 두께 비교"), ("/bigyo/jajak-duggae.html", "자작합판 두께 비교"), ("/bigyo/misong-hapan-duggae.html", "미송합판 두께 비교")], "gagyeok/mdf-gagyeok.html": [("/bigyo/mdf-duggae.html", "MDF 두께 비교")], "gyugyeok/mdf.html": [("/bigyo/mdf-duggae.html", "MDF 두께 비교")], "sigongbeop/tempa-byeok.html": [("/bigyo/tempa-bujajae.html", "템바보드 마감 부속·가격")], "gagyeok/tempa-board.html": [("/bigyo/tempa-bujajae.html", "템바보드 마감 부속·가격")], "qna/tempa-headboard.html": [("/bigyo/tempa-bujajae.html", "템바보드 마감 부속")], "qna/sliding-hanger-door.html": [("/bigyo/hanger-rail-types.html", "행거 레일 세트·가격")], "bigyo/slide-vs-swing-jungmun.html": [("/bigyo/hanger-rail-types.html", "행거 레일 세트·가격")], "qna/son-jabi-gyoche.html": [("/bigyo/gagu-sonjabi-types.html", "가구 손잡이 종류·가격")], "qna/sink-sonjabi.html": [("/bigyo/gagu-sonjabi-types.html", "가구 손잡이 종류·가격")], "qna/yoksil-cheonjang.html": [("/bigyo/living-cheonjang-gilee.html", "리빙 천장재 길이별 가격")], "qna/yoksil-panel.html": [("/bigyo/living-cheonjang-gilee.html", "리빙 천장재 길이별 가격")], "qna/sink-gyeongcheop.html": [("/bigyo/sink-gyeongcheop-types.html", "싱크대 경첩 종류·가격")], "qna/ggeoksoe-bogang.html": [("/bigyo/ggeoksoe-bracket-types.html", "꺾쇠·브라켓 종류·가격")], "qna/seonban-bracket.html": [("/bigyo/ggeoksoe-bracket-types.html", "꺾쇠·브라켓 종류·가격")], "qna/seonban-cheojim.html": [("/bigyo/ggeoksoe-bracket-types.html", "꺾쇠·브라켓 종류·가격")], "qna/merbau-jipseong.html": [("/bigyo/jipseongpan-sujong.html", "집성판 수종별 가격 비교")], "qna/redpine-jipseong.html": [("/bigyo/jipseongpan-sujong.html", "집성판 수종별 가격 비교")], "qna/gomu-vs-samnamu-jipseong.html": [("/bigyo/jipseongpan-sujong.html", "집성판 수종별 가격 비교")], "bigyo/jipseong-types.html": [("/bigyo/jipseongpan-sujong.html", "집성판 수종별 가격 비교")], "yongeo/darugi.html": [("/bigyo/darugi-types.html", "다루끼 종류·가격")], "qna/duchigak-darugi.html": [("/bigyo/darugi-types.html", "다루끼 종류·가격")], "qna/jeoksammok.html": [("/bigyo/jeoksammok-size.html", "적삼목 사이즈·가격")], "bigyo/jeoksammok-vs-bangbu.html": [("/bigyo/jeoksammok-size.html", "적삼목 사이즈·가격")], "qna/metal-siding-bujajae.html": [("/bigyo/metal-siding-bujajae-gagyeok.html", "메탈 사이딩 부자재 가격")], "sigongbeop/metal-siding.html": [("/bigyo/metal-siding-bujajae-gagyeok.html", "메탈 사이딩 부자재 가격")], "qna/dosuki-topnal.html": [("/bigyo/dosuki-size.html", "도스끼 톱날 길이 비교")], "qna/silicone-gun.html": [("/bigyo/silicone-gun-types.html", "실리콘건 vs 폼건")], "qna/pombond-sseugi.html": [("/bigyo/silicone-gun-types.html", "실리콘건 vs 폼건")], "qna/pvc-lattice.html": [("/bigyo/pvc-lattice-types.html", "PVC 래티스 종류·가격")], "qna/jeomgeomgu.html": [("/bigyo/jeomgeomgu-size.html", "점검구 사이즈·가격 비교")], "qna/boyang.html": [("/bigyo/boyangjae-types.html", "보양재 종류·가격 비교")], "qna/gyeongcheop-jongryu.html": [("/bigyo/gyeongcheop-types.html", "경첩 종류·가격 비교")], "qna/easy-gyeongcheop.html": [("/bigyo/gyeongcheop-types.html", "경첩 종류·가격 비교")], "qna/mun-cylinder.html": [("/bigyo/cylinder-types.html", "실린더 종류·가격 비교")], "qna/doorlock-gyoche.html": [("/bigyo/cylinder-types.html", "실린더 종류·가격 비교")], "qna/asphalt-shingle.html": [("/bigyo/shingle-types.html", "슁글 육각 vs 사각")], "qna/pergola-jibung.html": [("/bigyo/shingle-types.html", "슁글 육각 vs 사각")], "qna/gyedanjae-sujong.html": [("/bigyo/gyedanpan-jongryu.html", "계단판 종류·가격 비교")], "qna/wonmok-gyedan.html": [("/bigyo/gyedanpan-jongryu.html", "계단판 종류·가격 비교")], "qna/janseon-geori.html": [("/bigyo/janseon-geori-vs-bracket.html", "장선걸이 vs 연결 철물")], "cheolmul/janseon.html": [("/bigyo/janseon-geori-vs-bracket.html", "장선걸이 vs 연결 철물")], "qna/cement-board.html": [("/bigyo/cement-board-haji-vs-magam.html", "시멘트보드 하지용 vs 마감용")], "bigyo/cement-vs-gypsum-board.html": [("/bigyo/cement-board-haji-vs-magam.html", "시멘트보드 하지용 vs 마감용")], "cheolmul/gidungbatchim.html": [("/bigyo/juchudol-vs-gidungbatchim.html", "주춧돌 vs 기둥받침 비교")], "cheolmul/juchudol.html": [("/bigyo/juchudol-vs-gidungbatchim.html", "주춧돌 vs 기둥받침 비교")], "qna/ultari-gidung.html": [("/bigyo/juchudol-vs-gidungbatchim.html", "주춧돌 vs 기둥받침 비교")], "qna/hapdeck-20t-vs-25t.html": [("/bigyo/hapdeck-duggae.html", "합성데크 사이즈·가격 비교")], "qna/hapdeck-jongryu.html": [("/bigyo/hapdeck-duggae.html", "합성데크 사이즈·가격 비교")], "gagyeok/molding-gagyeok.html": [("/bigyo/pyeong-molding-pok.html", "평몰딩 폭 비교")], "qna/molding-ireum.html": [("/bigyo/pyeong-molding-pok.html", "평몰딩 폭 비교")], "bigyo/molding-types.html": [("/bigyo/pyeong-molding-pok.html", "평몰딩 폭 비교")], "qna/bangbu-size.html": [("/bigyo/bangbu-gakjae-size.html", "방부목 각재 사이즈 비교")], "bigyo/isopink-vs-styrofoam.html": [("/bigyo/styrofoam-duggae.html", "스티로폼 두께 비교"), ("/bigyo/isopink-duggae.html", "아이소핑크 두께 비교")], "gagyeok/danyeol-gagyeok.html": [("/bigyo/isopink-duggae.html", "아이소핑크 두께 비교"), ("/bigyo/eboard-duggae.html", "이보드 두께 비교")], "gyugyeok/danyeol.html": [("/bigyo/isopink-duggae.html", "아이소핑크 두께 비교"), ("/bigyo/eboard-duggae.html", "이보드 두께 비교")], "qna/eboard-dobae-vs-paint.html": [("/bigyo/eboard-duggae.html", "이보드 두께 비교")], "qna/beranda-danyeol.html": [("/bigyo/isopink-duggae.html", "아이소핑크 두께 비교")], "gagyeok/hapan-gagyeok.html": [("/bigyo/jajak-duggae.html", "자작합판 두께 비교"), ("/bigyo/misong-hapan-duggae.html", "미송합판 두께 비교")], "gagyeok/jipseong-gagyeok.html": [("/bigyo/jipseongpan-duggae.html", "집성판 두께 비교")], "gyugyeok/jipseong.html": [("/bigyo/jipseongpan-duggae.html", "집성판 두께 비교"), ("/bigyo/jipseongpan-sujong.html", "집성판 수종별 가격")], "gyugyeok/gujo.html": [("/bigyo/gujomok-size.html", "구조목 사이즈 비교"), ("/bigyo/gujomok-1x-size.html", "구조목 1×4~1×12 비교")], "bigyo/gujomok-size.html": [("/bigyo/gujomok-1x-size.html", "구조목 1×4~1×12 비교")], "bigyo/gujomok-1x-size.html": [("/bigyo/gujomok-size.html", "구조목 2×2~2×8 비교")], "gagyeok/gakjae-gagyeok.html": [("/bigyo/gujomok-size.html", "구조목 사이즈 비교"), ("/bigyo/darugi-types.html", "다루끼 종류·가격")]}.items():
    _REL[_k] = _REL.get(_k, []) + _v
for _a, _b, _n in [("hapan", "hapan-gagyeok", "합판"), ("mdf", "mdf-gagyeok", "MDF"), ("jipseong", "jipseong-gagyeok", "집성판"), ("seokgo", "seokgo-gagyeok", "석고보드"),
                   ("danyeol", "danyeol-gagyeok", "단열재"), ("gakjae", "gakjae-gagyeok", "각재"), ("deck", "deck-gagyeok", "데크재")]:
    _REL.setdefault(f"gagyeok/{_b}.html", []).append((f"/gyugyeok/{_a}.html", f"{_n} 규격표(크기·두께)"))
for _a, _j, _n in [("hapan", "hapan", "합판"), ("mdf", "mdf", "MDF"), ("jipseong", "jipseong", "집성판"), ("seokgo", "gypsum", "석고보드"), ("danyeol", "insul", "단열재"), ("gujo", "gujo", "구조재"), ("deck", "hapdeck", "데크재")]:
    _REL.setdefault(f"jajae/{_j}.html", []).append((f"/gyugyeok/{_a}.html", f"{_n} 규격표(크기·두께)"))


_SW_SKIP = {"cut.html", "price.html", "jae.html", "index.html", "stats/index.html", "muge.html"}
def _tbl_cards(body):
    """표를 휴대폰에서 옆으로 넘기는 카드로(데스크톱은 표 그대로)."""
    def conv(m):
        t = m.group(0)
        rows = re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S)
        cells = [re.findall(r"<(th|td)[^>]*>(.*?)</t[hd]>", r, re.S) for r in rows]
        cells = [c for c in cells if c]
        if len(cells) < 3: return t
        hdr = [v for _, v in cells[0]] if all(k == "th" for k, _ in cells[0]) else None
        data = cells[1:] if hdr else cells
        if not data or max(len(c) for c in data) < 2: return t
        cards = ""
        for c in data:
            vals = [v for _, v in c]
            ttl = re.sub(r"<[^>]+>", "", vals[0]).strip() or "-"
            lis = "".join(f'<li><span>{(re.sub(r"<[^>]+>", "", hdr[i]).strip() if hdr and i < len(hdr) else "")}</span> {v}</li>' for i, v in enumerate(vals) if i > 0 and re.sub(r"<[^>]+>|\s", "", v))
            cards += f'<div class="fq tcd"><b>{ttl}</b><ul>{lis}</ul></div>'
        return f'<div class="tsw-t">{t}</div><div class="tsw-c"><div class="fqs">{cards}</div><p class="small muted fqh">옆으로 밀어서 더 보기 ›</p></div>'
    return re.sub(r"<table\b.*?</table>", conv, body, flags=re.S)

def _lazyimg(doc):
    """본문 이미지: 첫 장(대표 사진)만 바로, 나머지는 화면에 보일 때 불러오기"""
    n = [0]
    def f(m):
        t = m.group(0)
        if "loading=" in t: return t
        n[0] += 1
        if n[0] == 1: return t.replace("<img ", '<img decoding="async" fetchpriority="high" ', 1)
        return t.replace("<img ", '<img loading="lazy" decoding="async" ', 1)
    b = doc.find("<main>")
    if b < 0: b = doc.find("<body")
    return doc[:b] + re.sub(r"<img [^>]*>", f, doc[b:]) if b >= 0 else doc


_MKW = [("hapdeck", r"합성\s?데크"), ("bangbu", r"방부목|방부 ?데크"), ("hapan", r"합판"), ("osb", r"OSB"), ("mdf", r"MDF"), ("jipseong", r"집성"), ("gypsum", r"석고"),
        ("insul", r"단열|아이소핑크|이보드"), ("hinoki", r"루바|편백|히노끼"), ("molding", r"몰딩|걸레받이"), ("film", r"필름|시트지"), ("siding", r"사이딩"), ("maru", r"마루|장판|데코타일"),
        ("stain", r"스테인|페인트|바니쉬"), ("gujo", r"구조목|구조재|각재|다루끼|2×4"), ("door", r"도어|중문|문틀|방문"), ("tile", r"타일"), ("sound", r"흡음|방음"), ("hardware", r"철물|앙카|피스")]
def _guessmats(t):
    sc = sorted(((len(re.findall(rx, t)), k) for k, rx in _MKW), reverse=True)
    return [k for n, k in sc if n >= 2][:2]
_PMATS = None
_HASCHG = bool(PREV) and any(True for r in csv.DictReader(open(f"{ROOT}/data/prices.csv", encoding="utf-8")) if r.get("price") and r["name"] in PREV and PREV[r["name"]] != int(float(r["price"])))
def _newrel(path, body):
    global _PMATS
    if not re.match(r"(jajae|gagyeok|sigongbeop|mandeul|bigyo|qna)/(?!index)[^/]+\.html$", path): return ""
    if _PMATS is None:
        import datetime as _d
        _cut = (_d.date.today() - _d.timedelta(days=14)).isoformat()
        _PMATS = [(p, set(_guessmats(p["title"] + " " + p.get("desc", "") + " " + p["title"]))) for p in POSTS if p.get("date", "") >= _cut and not p["title"].startswith("[영상]")]
    mm = set([path.split("/")[1][:-5]] if path.startswith("jajae/") else _guessmats(re.sub(r"<[^>]+>", " ", body)))
    if not mm: return ""
    hit = [p for p, pm in _PMATS if pm & mm and f"/news/{p['slug']}.html" not in body][:3]
    if not hit: return ""
    return ('<section class="wrap sec"><h2>새로 올라온 관련 글</h2><div class="pl hs">' + "".join(f'<a class="pc" href="/news/{p["slug"]}.html"><b>{html.escape(p["title"])}</b><span>{p.get("date", "")}</span></a>' for p in hit) + '</div></section>')
# 검색 클릭률 개선: data/title_override.json {"경로.html": {"title": .., "desc": .., "date": .., "why": ..}} — 주간 자동 작업이 서치콘솔 실적 보고 고침
TOV = json.load(open(f"{ROOT}/data/title_override.json", encoding="utf-8")) if os.path.exists(f"{ROOT}/data/title_override.json") else {}
_THC = {}
def _thumbs(body):
    """목록 카드의 lazy 사진: 480px webp 썸네일 + srcset + width/height(모바일 속도·화면 들썩임 방지)."""
    def rep(m):
        tag, rel = m.group(0), m.group(2)
        if "srcset=" in tag: return tag
        srcf = f"{ROOT}/assets/{rel}"
        if not os.path.exists(srcf): return tag
        if rel not in _THC:
            try:
                from PIL import Image
                tr = re.sub(r"\.(jpe?g|png)$", ".webp", rel, flags=re.I); tf = f"{ROOT}/assets/t/{tr}"
                with Image.open(srcf) as im: W, H = im.size
                if W <= 520: _THC[rel] = None
                else:
                    if not os.path.exists(tf) or os.path.getmtime(tf) < os.path.getmtime(srcf):
                        os.makedirs(os.path.dirname(tf), exist_ok=True)
                        with Image.open(srcf) as im:
                            im = im.convert("RGB"); im.thumbnail((480, 480 * H // W + 1)); im.save(tf, "WEBP", quality=72, method=4)
                    of = f"{OUT}/assets/t/{tr}"
                    if not os.path.exists(of): os.makedirs(os.path.dirname(of), exist_ok=True); shutil.copy2(tf, of)
                    _THC[rel] = (tr, W, H)
            except Exception: _THC[rel] = None
        v = _THC[rel]
        if not v: return tag
        tr, W, H = v
        add = f' srcset="/assets/t/{tr} 480w, /assets/{rel} {W}w" sizes="(max-width: 640px) 48vw, 300px"'
        if " width=" not in tag: add += f' width="{W}" height="{H}"'
        return tag[:-1].rstrip("/").rstrip() + add + ">"
    return re.sub(r'<img\b(?=[^>]*loading="lazy")[^>]*\bsrc="(/assets/((?:store|mandeul|sigongbeop|tteori|gonggan|gj|vis)/[^"]+\.(?:jpe?g|png)))"[^>]*>', rep, body, flags=re.I)

_YGL = None
def _yglink(path, body):
    """본문에 나온 현장 용어 첫 번째를 /yongeo/ 뜻 페이지로 연결(문단·목록 글자만, 링크·제목·스크립트 안은 건드리지 않음)."""
    global _YGL
    if _YGL is None:
        _YGL = {}
        try:
            _ok = set("다루끼 오비끼 덴조 가베 떡가베 와꾸 마구사 오사마리 시마이 단도리 데나오시 바라시 나라시 도끼다시 곰방 야리끼리 아시바 반생 빠루 데모도 함바 하바끼 헤베 루베 공구리 빠데 헤라 고데 렌가 나가시 시아게 데스리 가꾸목 뺑끼 후끼 사춤 오야지 구루마 기레바시 투바이 등박스 구배".split())
            for _g, _ts in json.load(open(f"{ROOT}/data/yongeo.json", encoding="utf-8")):
                for _t in _ts:
                    _k = re.split(r"[(·]", _t[0])[0]
                    if len(_t) > 4 and _t[4] and _k in _ok: _YGL[_k] = _t[4]
        except Exception: _YGL = {}
    if not _YGL or not re.match(r"(qna|sigongbeop|mandeul|news|bigyo|gagyeok|jajae)/(?!index)", path): return body
    rx = re.compile("(" + "|".join(sorted(map(re.escape, _YGL), key=len, reverse=True)) + ")")
    _cr = re.findall(r'<p class="crumb">.*?</p>', body); body = re.sub(r'<p class="crumb">.*?</p>', "\x00CRUMB\x00", body)
    parts = re.split(r"(<[^>]+>)", body); used = set(); skip = 0; inp = 0
    for i, x in enumerate(parts):
        if x.startswith("<"):
            t = x[1:].split()[0].rstrip(">").lower() if len(x) > 2 else ""
            if t in ("a", "script", "style", "h1", "h2", "h3", "title", "button", "summary", "label"): skip += 1
            elif t in ("/a", "/script", "/style", "/h1", "/h2", "/h3", "/title", "/button", "/summary", "/label"): skip = max(0, skip - 1)
            elif t in ("p", "li", "dd", "td"): inp += 1
            elif t in ("/p", "/li", "/dd", "/td"): inp = max(0, inp - 1)
            continue
        if skip or not inp or not x.strip(): continue
        def _r(m):
            k = m.group(1)
            if k in used or len(used) >= 5: return k
            used.add(k); return f'<a class="ygl" href="/yongeo/{_YGL[k]}.html" title="{k} 뜻">{k}</a>'
        parts[i] = rx.sub(_r, x)
    out = "".join(parts)
    for c in _cr: out = out.replace("\x00CRUMB\x00", c, 1)
    return out

def page(path, title, desc, body, active="", jsonld=None, img=None):
    if 'card mallbox' not in body and re.match(r"(jajae|mandeul|sigongbeop|gagyeok|gonggan)/(?!index)", path) or path in ("calc.html", "cut.html", "price.html"):
        _mm = [path.split("/")[1][:-5]] if path.startswith("jajae/") else (["hapan", "gujo", "hapdeck"] if path in ("calc.html", "cut.html", "price.html") else _guessmats(re.sub(r"<[^>]+>", " ", body)))
        if path in ("calc.html", "cut.html", "price.html"): _mb = mallbox(_mm, 3)
        else: _mb = mallbox(_mm)
        if _mb: body = body.replace('<section class="cta">', _mb + '<section class="cta">', 1) if '<section class="cta">' in body else body + _mb
    body = _yglink(path, body)
    body = _thumbs(body)
    _nr = _newrel(path, body)
    if _nr: body = body.replace('<section class="cta">', _nr + '<section class="cta">', 1) if '<section class="cta">' in body else body + _nr
    if path not in _SW_SKIP and "<table" in body and "/p/" not in path: body = _tbl_cards(body)
    if path in TOV: title = TOV[path].get("title") or title; desc = TOV[path].get("desc") or desc
    title = _tshort(title)
    if path in _REL:
        _rb = '<section class="wrap sec"><div class="qk qk2"><b>👉 함께 보기</b>' + "".join(f'<a href="{h}">{t}</a>' for h, t in _REL[path]) + '</div></section>'
        body = body.replace('<section class="cta">', _rb + '<section class="cta">', 1) if '<section class="cta">' in body else body + _rb
    if img and img.startswith("/"): img = BASE + img  # 상대 주소 사진은 전체 주소로(사이트맵·공유 미리보기 오류 방지)
    if img and (" " in img.strip() or not img.strip().lower().split("?")[0].endswith((".jpg", ".jpeg", ".png", ".webp"))): img = None  # 깨진 대표 사진 주소는 버림
    if not img and not _noidx(path) and path != "404.html":
        try:
            import og as _og
            _t0 = title.split(" | ")[0]
            _m, _sb = (_t0.split(" — ", 1) + [""])[:2]
            _pr = re.search(r"(\d{1,3}(?:,\d{3})+)원?\s*[~–]\s*\d{1,3}(?:,\d{3})+원", desc)
            _pm = re.search(r"\d{1,3}(?:,\d{3})+원(?:~|부터)?", desc)
            if _pr: _pm = re.match(r"(.*)", _pr.group(1) + "원~")
            _nm = re.sub(r"[^0-9A-Za-z]+", "-", path[:-5]).strip("-") or "home"
            _rel = _og.make(ROOT, _nm, _m.strip(), _sb.strip(), (_pm.group(0).replace("부터", "~") if _pm else ""))
            if _rel:
                os.makedirs(f"{OUT}/assets/og", exist_ok=True)
                if os.path.exists(ROOT + _rel): shutil.copy(ROOT + _rel, OUT + _rel)
                img = BASE + _rel
        except Exception as _e:
            pass
    if ' data-big="' in body and 'id="ylb"' not in body:
        import yerim as _ylb; body += _ylb.LB
    if 'class="yri" href="#" data-big=' in body and "ItemList" not in json.dumps(jsonld or {}):  # 제품 사진 카드가 있는 페이지는 제품 목록(ItemList) 정보 자동 추가
        _it = re.findall(r'<a class="yri" href="#" data-big="([^"]+)" data-n="([^"]+)"', body)[:60]
        if _it:
            _il = {"@context": "https://schema.org", "@type": "ItemList", "name": title.split(" | ")[0].split(" — ")[0], "numberOfItems": len(_it),
                   "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": html.unescape(n_), "image": u_} for i, (u_, n_) in enumerate(_it)]}
            jsonld = _il if jsonld is None else ((jsonld if isinstance(jsonld, list) else [jsonld]) + [_il])
    if len(desc) > 80:  # 네이버 권장: 설명 80자 이내 — 문장·쉼표 경계에서 자름
        cut = desc[:80]; k = cut.rfind(".")
        if k < 40: k = cut.rfind(", ")
        desc = (cut[:k + 1] if k >= 40 else cut[:79] + "…").rstrip(" ,")
    if len(desc) < 58:  # 너무 짧은 설명은 매장 정보로 보강(80자 이내)
        for add in (" 대전 유성 3000평 매장, 즉석 재단·전국 용달 배송.", " 대전 유성 매장·전국 배송.", " 대전 영진목재."):
            if len(desc) + len(add) <= 80: desc = desc.rstrip() + add; break
    canon = BASE + ("/" + path if path != "index.html" else "/").replace("index.html", "")
    PGMETA[path] = (title.split(" | ")[0], desc, img)
    nav = "".join(f'<a href="{h}"{" class=on" if active==h else ""}><svg class="ni" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{NAVI.get(h, "")}</svg><span>{t}</span></a>' for h, t in NAV)
    lds = jsonld if isinstance(jsonld, list) else ([jsonld] if jsonld else [])
    lds = lds + [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "홈", "item": BASE + "/"}] +
                 ([{"@type": "ListItem", "position": 2, "name": dict(NAV)[active], "item": BASE + active}] if active in dict(NAV) and active != "/" else []) +
                 ([{"@type": "ListItem", "position": 3 if (active in dict(NAV) and active != "/") else 2, "name": title.split(" — ")[0].split(" | ")[0], "item": canon}] if (canon.rstrip("/") != (BASE + active).rstrip("/") or active not in dict(NAV)) and path != "index.html" else [])}]
    ld = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    if path != "index.html": ld += '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "Organization", "@id": BASE + "/#org", "name": "영진종합목재", "alternateName": ["영진목재", "월드건축자재", "월드아키텍쳐"], "url": BASE + "/", "logo": BASE + "/assets/icon-512.png", "telephone": TEL, "sameAs": [YT, YT2, "https://www.wwood.kr/", MALL, NPLACE, "https://g.page/r/CZcZc9J-M0L0EAE"]}, ensure_ascii=False) + '</script>'
    doc = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="alternate" type="application/rss+xml" title="영진종합목재 소식" href="/rss.xml">
<link rel="canonical" href="{canon}">{'<meta name="robots" content="noindex,follow">' if _noidx(path) else ('' if PREVIEW else '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">')}<meta name="naver-site-verification" content="a59ff6921fc90666c920da00bf9a23ecb0ba3514"><meta property="og:type" content="website"><meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canon}"><meta property="og:image" content="{E(img or (BASE + "/assets/store/storefront.jpg"))}">{"" if img else '<meta property="og:image:width" content="1280"><meta property="og:image:height" content="853">'}<meta property="og:image:alt" content="{E(title.split(" | ")[0]) if img else "영진종합목재(월드건축자재) 매장"}"><meta name="twitter:title" content="{E(title)}"><meta name="twitter:description" content="{E(desc)}"><meta name="twitter:image" content="{E(img or (BASE + "/assets/store/storefront.jpg"))}"><meta property="og:site_name" content="영진종합목재 (월드건축자재)"><meta property="og:locale" content="ko_KR"><meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://www.wwood.kr"><link rel="icon" href="/assets/logo-mark.svg" type="image/svg+xml"><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","G-6EC3G8PSDX",{{linker:{{domains:["wwood.co.kr","wwood.kr"]}}}});addEventListener("load",function(){{setTimeout(function(){{var s=document.createElement("script");s.async=1;s.src="https://www.googletagmanager.com/gtag/js?id=G-6EC3G8PSDX";document.head.appendChild(s)}},1200)}});</script><link rel="icon" href="/assets/favicon-48.png" sizes="48x48"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><link rel="manifest" href="/assets/manifest.webmanifest"><meta name="theme-color" content="#1D1B18"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="영진목재"><link rel="stylesheet" href="/assets/style.css?v={ASSET_V}">{'<meta name="robots" content="noindex,nofollow">' if PREVIEW else ''}{ld}</head><body>
<div class="top"><div class="wrap row sb"><span>{HOURS} · {ADDR}</span><span><a href="#" id="appi" class="appi">홈 화면에 추가</a> <a href="/dome.html">업체·도매회원</a> <a class="tvis" href="/visit.html">매장 길찾기</a></span></div></div><div id="appg" class="appg" hidden><div class="appgb"><span class="appgh"></span><div class="appgtop"><img src="/assets/icon-192.png" width="64" height="64" alt=""><div><b>영진목재 앱</b><small>대전 3000평 목재·건축자재 · 무료</small></div></div><div id="appgt"></div><button type="button" id="appgx" class="appgx">다음에 할게요</button></div></div>
<header><div class="wrap row sb hd"><a class="logo" href="/"><img class="lm" src="/assets/logo-mark.svg" width="46" height="46" alt=""><span class="lt"><b>영진종합목재</b><small><em>월드건축자재</em> · 충청권 최대규모 목재상</small></span></a>
{_dnav(active)}<div class="hbtn"><a class="hcam" href="/sajin.html#cam" title="사진으로 제품 찾기" aria-label="카메라로 제품 찾기"><i><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3.5 8.5A2.5 2.5 0 0 1 6 6h1.7l1.4-1.9A1.5 1.5 0 0 1 10.3 3.5h3.4a1.5 1.5 0 0 1 1.2.6L16.3 6H18a2.5 2.5 0 0 1 2.5 2.5v8.5A2.5 2.5 0 0 1 18 19.5H6A2.5 2.5 0 0 1 3.5 17z"/><circle cx="12" cy="12.6" r="3.7"/></svg></i><small>사진찾기</small></a><button class="mnb" type="button" aria-expanded="false" aria-controls="gnav" onclick="var h=this.closest('header'),o=h.classList.toggle('open');this.setAttribute('aria-expanded',o);this.innerHTML=o?'✕ 닫기':'☰ 메뉴'">☰ 메뉴</button></div><nav id="gnav">{nav}</nav></div></header>
<main>{body}{_SHR if path not in ("offline.html", "404.html") else ""}</main>
<footer><div class="wrap">월드건축자재 · 영진종합목재(영진목재) · 상호 영진우드 · <a href="/daejeon.html">대전 목재</a> · <a href="/sejong.html">세종 목재</a> · <a href="/calc.html">자재 계산기</a> · <a href="/cut.html">합판 재단 미리보기</a> · <a href="/mokgongso.html">목재 재단(목공소)</a> · <a href="/jaedan-baesong.html">재단 후 전국 배송</a> · <a href="/sajin.html">사진으로 제품 찾기</a> · <a href="/doumi.html">셀프 인테리어 도우미</a> · <a href="/widget.html">계산기 퍼가기</a> · <a href="/apt/">아파트별 자재</a> · <a href="/mandeul/">DIY 만들기</a> · <a href="/sigongbeop/">인테리어 자재 시공법</a> · <a href="/baesong.html">전국 배송</a> · <a href="/jeonguk/">배송 지역</a> · <a href="/jajae/">자재 백과</a> · <a href="/bigyo/">자재·인테리어 비교</a> · <a href="/qna/">하는 법 Q&amp;A</a> · <a href="/issue/">이슈·시즌 자재</a> · <a href="/gyugyeok.html">규격표</a> · <a href="/bangbu-gyugyeok.html">방부목 규격</a> · <a href="/deck-pis.html">데크 피스</a> · <a href="/island-size.html">아일랜드 식탁 사이즈</a> · <a href="/muge.html">자재 무게 계산</a> · <a href="/seokgo-pis.html">석고보드 피스</a> · <a href="/pis-gilee.html">피스 길이</a> · <a href="/gagyeok/">자재 가격 가이드</a> · <a href="/cheolmul/">목재 철물</a> · <a href="/taka/">타카·타카핀</a> · <a href="/yerim/">예림 중문·도어</a> · <a href="/younglim/">영림 도어·중문·필름</a> · <a href="/shenu/">쉐누 도어·몰딩</a> · <a href="/bupum/">철물·공구·부속</a> · <a href="/bondex/">본덱스 스테인·페인트</a> · <a href="/nichiha/">니치하 세라믹 사이딩</a> · <a href="/geonjae/">목조·외장·내장 건축자재</a> · <a href="/suip/">수입 목조주택 자재·창호</a> · <a href="/local/">지역별 시공</a> · <a href="/faq.html">자주 묻는 질문</a> · <a href="/about.html">영진종합목재 한눈에</a> · <a href="/yongeo.html">현장 용어</a> · <a href="/jeonche.html">전체 페이지</a> · <a href="/privacy.html">개인정보처리방침</a> | {ADDR} | {TEL} | <a href="mailto:{EMAIL}">{EMAIL}</a> | {HOURS}<br>
시공: 월드아키텍쳐 | 대표 김지운 | 사업자등록번호 281-05-03197 | {LIC}<br>사이트의 매장·상품·시공 사진은 영진종합목재가 직접 촬영한 저작물로(제조사 제품 사진 제외) 무단 복제·사용을 금합니다.<br>
유튜브 <a href="{YT}">@월드건축자재DIY</a> · <a href="{YT2}">@월드도어</a> · 도매회원 쇼핑몰 <a href="{DOME}">wwood.kr</a> · 표시 가격은 부가세 별도 소매 기준가이며 결제·재단은 매장에서 합니다.</div></footer><script>addEventListener("load",function(){{setTimeout(function(){{(function(){{try{{var k=new Date(Date.now()+9*3600e3).toISOString().slice(0,10).replace(/-/g,""),b="https://abacus.jasoncameron.dev/hit/wwood-co-kr/";
function rd(x){{var v=null;try{{v=localStorage.getItem(x)}}catch(e){{}}if(v===null){{var m=document.cookie.match(new RegExp("(?:^|; )"+x+"=([^;]*)"));v=m?m[1]:null}}return v}}
function wr(x,v){{try{{localStorage.setItem(x,v)}}catch(e){{}}try{{document.cookie=x+"="+v+"; max-age=34560000; path=/; SameSite=Lax"}}catch(e){{}}}}
function lq(){{try{{return JSON.parse(localStorage.getItem("wwq")||"[]")}}catch(e){{return []}}}}function sq(q){{try{{localStorage.setItem("wwq",JSON.stringify(q.slice(-40)))}}catch(e){{}}}}
var busy=0;function fl(){{if(busy)return;var q=lq();if(!q.length)return;busy=1;var x=q[0];fetch(b+x,{{cache:"no-store",keepalive:true}}).then(function(r){{if(!r.ok)throw 0;var z=lq();z.shift();sq(z);busy=0;setTimeout(fl,150)}}).catch(function(){{busy=0;setTimeout(fl,8000)}})}}
window.WWH=function(x){{var q=lq();q.push(x);sq(q);fl()}};
var bot=navigator.webdriver||/bot|crawl|spider|slurp|lighthouse|headless|preview/i.test(navigator.userAgent);
if(!bot&&rd("vcd")!==k){{wr("vcd",k);var rf=document.referrer||"",src=/youtube|youtu\\.be/.test(rf)?"yt":/naver/.test(rf)?"naver":/google/.test(rf)?"google":/daum|kakao/.test(rf)?"daum":/bing/.test(rf)?"bing":/daangn|karrot/.test(rf)?"daangn":/wwood\\.kr/.test(rf)?"wwoodkr":rf&&rf.indexOf(location.host)<0?"etc":"direct";
WWH("d"+k);WWH("total");WWH("src-"+src);WWH("src-"+src+"-d"+k)}}else fl();
addEventListener("online",fl);addEventListener("pagehide",function(){{busy=0;fl()}})}}catch(e){{}}}})()}},800)}});</script>
<div class="mbar"><a class="b g" href="/visit.html">매장 길찾기</a><a class="b d" href="tel:{TEL.replace('-','')}">전화</a></div>
<script src="/assets/site.js?v={ASSET_V}" defer></script></body></html>"""
    if PREFIX: doc = doc.replace('href="/', f'href="{PREFIX}/').replace('src="/', f'src="{PREFIX}/')
    doc = _lazyimg(doc)
    fp = os.path.join(OUT, path); os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(doc)
    if not _noidx(path): SITEMAP.append(canon); SIMG[canon] = img  # 상품 상세(/p/)는 얇은 페이지라 색인 제외(구글: 크롤링됨-색인 안 됨 734건)

def vcard(v, big=False):
    return f"""<a class="vc{' big' if big else ''}{' sh' if v['type']=='S' else ''}" href="{vpage(v)}"{'' if v['id'] in VD else ' target="_blank" rel="noopener"'} data-yt="{v['id']}">
<span class="th"><img loading="lazy" decoding="async" width="480" height="360" src="https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg" alt="{E(vshort(v['title']))}"><i class="play"></i>{'<em>쇼츠</em>' if v['type']=='S' else '<em>라이브</em>' if v['type']=='V' else ''}</span>
<b>{E(v['title'])}</b>{f"<small>조회 {views(v['n'])}</small>" if v['n'] else ""}</a>"""

def vrank(vs, grid="vg"):
    return f'<div class="{grid}">' + "".join(vcard(v).replace('<span class="th">', f'<span class="th"><i class="rk{" r3" if i < 3 else ""}">{i + 1}</i>', 1) for i, v in enumerate(vs)) + '</div>'

def vsplit(vs, hl="h2", nl=None, ns=None):
    """일반 영상(라이브 포함)과 쇼츠를 나눠서 표시"""
    L = [v for v in vs if v["type"] != "S"][:nl]; S = [v for v in vs if v["type"] == "S"][:ns]
    out = ""
    if L: out += f'<{hl} class="vh">▶ 영상 <small class="muted">{len(L)}편</small></{hl}><div class="vg">{"".join(vcard(v) for v in L)}</div>'
    if S: out += f'<{hl} class="vh">⚡ 쇼츠 <small class="muted">{len(S)}편</small></{hl}><div class="sg">{"".join(vcard(v) for v in S)}</div>' + ('<p class="hsh">옆으로 밀어서 더 보기 ›</p>' if len(S) > 2 else '')
    return out

def embed(v):
    return f'<div class="emb"><iframe loading="lazy" src="https://www.youtube.com/embed/{v["id"]}" title="{E(vshort(v["title"]))}" allowfullscreen></iframe></div>'

def ptable(rows):
    if not rows: return '<p class="muted">이 자재는 규격·수종이 다양해 매장에서 실물 보고 안내해 드립니다.</p>'
    tr = "".join(f"<tr><td>{E(clean_name(p['name']))}</td><td class=r><b>{won(p['price'])}</b></td></tr>" for p in rows)
    return f'<div class="tw"><table><thead><tr><th>품목·규격</th><th class=r>소매 기준가</th></tr></thead><tbody>{tr}</tbody></table></div><p class="muted small">부가세 별도 · 규격·수량에 따라 달라집니다 · <a href="/cut.html#fee">재단비</a> 1컷 1,000원~(두께별) · 운임은 매장에서 계산 · 도매가는 회원 로그인 후</p>'

CTA = f"""<section class="cta"><div class="wrap g2"><div><h2>실물 보고, 원하는 사이즈로 잘라 가세요</h2>
<p>{ADDR} · {HOURS}. 3000평 매장에서 바로 고르고 즉석 재단해 드립니다.</p></div>
<div class="row"><a class="b g" href="/visit.html">매장 길찾기</a><a class="b r" href="/sigong.html">시공 맡기기</a></div></div></section>"""

BIZ = {"@context": "https://schema.org", "@type": "HardwareStore", "name": "영진종합목재", "description": "대전 유성 3000평 목재·건축자재 매장. 합판·MDF·집성판·구조재·방부목·데크재 원하는 크기 즉석 재단(1컷 1,000원부터), 전국 용달 배송, 도매·시공.", "email": EMAIL, "hasMap": "https://naver.me/GEdDcn2S", "logo": "https://www.wwood.co.kr/assets/icon-512.png", "knowsAbout": ["목재 재단", "합판", "MDF", "구조재", "방부목", "데크", "집성판", "석고보드", "사이딩", "인테리어 자재"],
       "telephone": "+82-42-545-2900", "address": {"@type": "PostalAddress", "streetAddress": "유성대로 44, 1층", "addressLocality": "대전", "addressCountry": "KR"},
       "openingHours": ["Mo-Fr 07:00-18:00", "Sa-Su 07:00-15:00"], "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "07:00", "closes": "18:00"}, {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Saturday", "Sunday"], "opens": "07:00", "closes": "15:00"}, {"@type": "OpeningHoursSpecification", "dayOfWeek": "PublicHolidays", "opens": "07:00", "closes": "16:00"}], "url": BASE + "/", "@id": BASE + "/#org", "sameAs": [YT, YT2, "https://www.wwood.kr/", MALL, KAKAO, NPLACE, "https://g.page/r/CZcZc9J-M0L0EAE"], "alternateName": ["영진목재", "월드건축자재", "영진우드"], "legalName": "영진우드",
       "image": [BASE + "/assets/store/storefront.jpg", BASE + "/assets/store/yard-aisle2.jpg", BASE + "/assets/store/showroom.jpg"], "priceRange": "₩", "areaServed": ["대전", "세종", "공주", "계룡", "논산", "금산", "옥천", "천안", "청주", {"@type": "Country", "name": "대한민국"}],
       "subOrganization": {"@type": "GeneralContractor", "name": "월드아키텍쳐", "description": "실내건축공사업 대전서구24-나-19 · 외벽 사이딩 전국 시공, 실내 공정 대전·세종·공주·계룡·금산·옥천·천안·청주", "telephone": "+82-42-545-2900", "url": BASE + "/sigong.html", "areaServed": {"@type": "Country", "name": "대한민국"}}}

# ---------- pages ----------
def build():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT); shutil.copytree(f"{ROOT}/assets", f"{OUT}/assets")
    shutil.copy(f"{ROOT}/sw.js", f"{OUT}/sw.js")  # 앱(PWA) 서비스워커 — 사이트 전체 범위라 루트에
    open(f"{OUT}/offline.html", "w", encoding="utf-8").write('<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>인터넷 연결 없음 | 영진목재</title><meta name="description" content="인터넷이 연결되지 않았을 때 보이는 영진목재 앱 안내 화면입니다."><link rel="stylesheet" href="/assets/style.css"></head><body><main><section class="wrap sec"><h1>인터넷이 연결되지 않았어요</h1><p class="lead">연결되면 다시 열어 주세요. 앞서 본 페이지·기준가·재단 미리보기는 저장돼 있으면 그대로 열립니다.</p><p><a class="b r" href="tel:0425452900">전화 042-545-2900</a> <a class="b o" href="/">처음으로</a></p></section></main></body></html>')
    byid = {v["id"]: v for v in V}
    top = lambda f, k: sorted([v for v in V if f(v)], key=lambda v: -v["n"])[:k]

    # index
    tour = byid.get("xPsUVr7exLU")
    use = "".join(f'<a class="uc" href="/video/{c}.html"><b>{n}</b><small>{d}</small></a>' for c, n, d in CATS)
    mats = "".join(f'<a class="mc" href="/jajae/{m["slug"]}.html"><b>{m["name"]}</b><small>{m["where"][0]}</small></a>' for m in MATS)
    _hl = [v for v in top(lambda v: v["id"] != "xPsUVr7exLU" and v["type"] != "S", 8)]
    _hs = [v for v in top(lambda v: v["type"] == "S", 6)]
    hot = '<h3 class="vh">▶ 영상 TOP 8</h3>' + vrank(_hl) + '<h3 class="vh">⚡ 쇼츠 TOP 6</h3>' + vrank(_hs, "sg")
    ids = LATEST
    if not ids and os.path.exists(f"{ROOT}/data/yt_all.tsv"):
        rows = [l.rstrip("\n").split("\t") for l in open(f"{ROOT}/data/yt_all.tsv", encoding="utf-8") if l.strip()]
        rows = [r for r in rows if len(r) > 3 and r[3].isdigit()]
        rows.sort(key=lambda r: -int(r[3]))
        ids = [r[0] for r in rows if r[1] != "S"][:4] + [r[0] for r in rows if r[1] == "S"][:4]
    newv = [byid[i] for i in ids if i in byid][:8]
    newsec = (f'<section class="wrap sec"><h2>새로 올라온 영상</h2>{vsplit(newv, "h3")}</section>' if newv else "")
    def _pth(p):
        vs = p.get("videos") or []
        if vs and p["title"].startswith("[영상]"): return f'<img loading="lazy" decoding="async" width="480" height="270" src="https://i.ytimg.com/vi/{vs[0]}/hqdefault.jpg" alt="">'  # 영상 썸네일은 영상 소식에만, 글은 글 카드로
        t = re.sub(r"\s*[—|].*$", "", p["title"])[:18]
        return f'<i class="pci"><em>{"자재·인테리어 소식" if "-news-" in p.get("slug", "") else "자재 정보"}</em>{E(t)}</i>'
    plist = lambda ps: "".join(f'<a class="pc" href="/news/{p["slug"]}.html">{_pth(p)}<small>{E(p.get("date",""))}</small><b>{E(p["title"])}</b><span>{E(p.get("desc",""))}</span></a>' for p in ps)
    _isv = lambda p: p["title"].startswith("[영상]")
    _vtyp = {l.split("\t")[0]: l.split("\t")[1] for l in open(f"{ROOT}/data/yt_all.tsv", encoding="utf-8") if l.count("\t") >= 2}
    _iss = lambda p: _vtyp.get((p.get("videos") or [""])[0]) == "S" or "#shorts" in p["title"].lower() or "쇼츠" in p["title"]
    def nrow(h, ps): return (f'<h2 class="gt">{h} <small>옆으로 넘겨 보세요 ›</small></h2><div class="pl hs nw">{plist(ps)}</div>') if ps else ""
    import gonggan_data as _GG0
    postsec = f'<section class="wrap sec"><h2>공간 사진 둘러보기 <small class="muted">사진 속 + 누르면 자재·시공법</small></h2><div class="pl hs">' + "".join(f'<a class="pc" href="/gonggan/{x[0]}.html"><span class="ggi"><img loading="lazy" src="{_gth(x[2])}" alt="">' + "".join(f'<i style="left:{q[0]}%;top:{q[1]}%"></i>' for q in (_ggsq(_gth(x[2]), sp[0], sp[1]) for sp in x[5]) if q) + f'</span><b>{E(x[1].split(" — ")[0])}</b></a>' for x in _GG0.SCENES) + '</div><p class="hsh">옆으로 밀어서 더 보기 ›</p><p><a href="/gonggan/">전체 보기 →</a></p></section>'
    postsec += (f'<section class="wrap sec"><h2>소식·자재 정보</h2><div class="pl hs nw">{plist(POSTS[:10])}</div><p class="hsh">옆으로 밀어서 더 보기 ›</p><p><a href="/news/">전체 글 보기 →</a></p></section>' if POSTS else "")
    base8 = [("합판","일반 4×8 · 8.5mm(베트남)",22800),("OSB합판","T&G 4×8 · 18.3mm",35200),("MDF","4×8 · 9mm",14800),("구조재 2×4","38×89 · 12ft",10700),
             ("방부목 데크재","20×120 · 12자",10500),("석고보드","3×6 · 9.5T",5200),("합성데크","20×140 · 3000",21500),("다루끼(소송)","1.0×1.0 · 12자 · 12개",42400)]
    bt = "".join(f"<tr><td>{a}</td><td>{b}</td><td class=r><b>{won(c)}</b></td></tr>" for a, b, c in base8)
    body = f"""
<section class="hero"><div class="wrap g2">
<div><span class="chip red">영상으로 보고 · 매장에서 바로</span>
<h1>어디에 쓰는 나무인지<br>영상으로 먼저 보고<br>매장에서 바로 가져가세요</h1>
<p class="lead">현장 목수·기술자가 직접 쓰는 자재를 영상마다 정리했습니다. 대전 3000평 매장에서 실물 확인부터 원하는 사이즈 재단까지 그 자리에서 해드립니다.</p>
<div class="row hb2"><a class="b r" href="/visit.html">매장 길찾기</a><a class="b o" href="/price.html">기준가 보기</a><a class="b o" href="/mandeul/">DIY 만들기</a><a class="b o" href="/sigongbeop/">자재 시공법</a><a class="b o" href="/calc.html">자재 계산기</a><a class="b d" href="/dome.html">업체·도매회원</a></div></div>
<div>{embed(tour) if tour else ''}<p class="small muted">대전 목재소·건축자재 백화점 3000평 투어 · 조회 18만회</p></div></div></section>
<section class="stat"><div class="wrap g4"><div><b>구독 {ST["subs"]}명</b><small>유튜브 월드건축자재DIY</small></div><div><b>영상 {int(ST["videos"]):,}개</b><small>시공·DIY·자재 정보</small></div>
<div><b>소매 + 도매</b><small>셀프 고객부터 현장 납품까지</small></div><div><b>직접 시공</b><small>월드아키텍쳐 · {LIC}</small></div></div></section>
<section class="wrap sec"><div class="tl4"><a class="ttl" href="/tteori/"><b>🏷 떨이몰</b><span>자투리·B급·재고 정리 싸게 · 수량 한정</span></a><a href="/cut.html"><b>✂ 재단 미리보기</b><span>치수만 넣으면 원판에서 어떻게 잘리는지 그림으로</span></a><a href="/mandeul/"><b>🪚 DIY 만들기</b><span>평상·책장·데크·울타리 재단 목록</span></a><a href="/gyugyeok.html"><b>📏 규격표</b><span>합판 두께·2×4 실제 치수 한눈에</span></a><a href="/baesong.html"><b>🚚 전국 배송</b><span>재단해서 용달로 전국 현장까지</span></a><a href="/jaedan-bi.html"><b>💲 재단비</b><span>두께별 1컷 1,000원부터</span></a><a href="/yesi/"><b>📐 몇 평이면 얼마?</b><span>데크·루바·석고 평수별 자재비</span></a><a href="/doumi.html"><b>🧭 셀프 인테리어 도우미</b><span>질문 4개 → 시공법·자재·가격·영상 한 번에</span></a><a href="/apt/"><b>🏢 아파트별 자재</b><span>전국 우리 단지 평형·연식에 맞는 자재</span></a><a href="/gongjeong.html"><b>🗂 공정 순서 플래너</b><span>철거부터 입주까지 순서표·체크</span></a><a href="/hyeonjang.html"><b>📋 내 현장함</b><span>저장한 재단표·미리 재단 주문</span></a><a href="/yeongyeol/"><b>🤝 시공팀 연결</b><span>사이딩·목공·도배·타일 등 14개 공정</span></a></div><p class="tlh">옆으로 밀어서 더 보기 ›</p></section><!--MKHOME-->
<style>.tl4{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}.tl4 a{{display:block;background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px;color:inherit;text-decoration:none}}.tl4 a:hover{{border-color:var(--red)}}.tl4 b{{display:block;font-size:17px;margin-bottom:4px}}.tl4 span{{font-size:13px;color:var(--mut)}}@media(max-width:760px){{.tl4{{grid-template-columns:none;grid-template-rows:repeat(2,auto);grid-auto-flow:column;grid-auto-columns:44%;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;padding-bottom:4px;-webkit-overflow-scrolling:touch}}.tl4::-webkit-scrollbar{{display:none}}.tl4 a{{scroll-snap-align:start;min-height:118px;box-sizing:border-box}}.tl4+.tlh{{display:block}}}}.tlh{{display:none;text-align:right;font-size:13px;color:var(--mut);margin:6px 0 0}}</style>
<div class="hx"><section class="wrap sec"><h2>무엇을 만들고 싶으세요?</h2><p class="muted">고르면 그 용도의 자재와 시공 영상이 한 번에 나옵니다.</p><div class="ug">{use}</div></section>
<section class="wrap sec"><h2>자재 백과 — 이 나무, 어디에 쓰나요?</h2><p class="muted">용도·인테리어 효과·기준가·관련 영상을 자재별로 정리했습니다.</p><div class="mg">{mats}</div></section>
{postsec}{newsec}
<section class="wrap sec"><h2>🏆 많이 본 영상 TOP</h2><p class="small muted">조회수가 많은 순서입니다.</p>{hot}<p><a class="b o" href="/video/top.html">많이 본 영상 TOP 50 전체 보기 ›</a> <a href="{YT}" target="_blank" rel="noopener">유튜브 채널 →</a></p></section></div>
<section class="wrap sec g2"><div class="card"><h2>기본 자재 기준가</h2><p class="muted small">부가세 별도 · 규격·수량에 따라 달라집니다</p>
<div class="tw"><table><thead><tr><th>자재</th><th>규격</th><th class=r>기준가</th></tr></thead><tbody>{bt}</tbody></table></div>
<p class="small"><a href="/cut.html#fee">재단비</a> 1컷 1,000원~(두께별) · 운임·수량 할인은 매장에서 계산 · 고재·수입목·특수목은 매장 문의 · 도매가는 회원 로그인 후</p><a href="/price.html">기준가 전체 보기 →</a><div class="qk"><b>💰 1평에 얼마?</b><a href="/gagyeok/hapan-gagyeok.html">합판</a><a href="/gagyeok/seokgo-gagyeok.html">석고보드</a><a href="/gagyeok/deck-gagyeok.html">데크</a><a href="/gagyeok/danyeol-gagyeok.html">아이소핑크</a><a href="/gagyeok/hinoki-ruba.html">루바</a><a href="/gagyeok/tempa-board.html">템바보드</a><a href="/gagyeok/">전체 가격 가이드</a></div></div>
<div class="card dark"><h2>직접 하기 어렵다면, 시공까지</h2><p>자재를 가장 잘 아는 목재상이 직접 시공합니다. 월드아키텍쳐({LIC})가 대전·세종 전 공정을 시공하고, 모든 현장은 유튜브에 공개합니다.</p>
<a class="b r" href="/sigong.html">시공 사례 보기</a></div></section>{CTA}"""
    import nation as _nt
    _jg = '<section class="wrap sec"><h2>전국 배송 — 원하는 크기로 재단해서 보내 드립니다</h2><p>서울·경기부터 부산·제주까지, 3000평 매장의 자재를 재단해 용달(제주는 배편)로 보냅니다. 운임은 품목·수량을 보고 먼저 견적 드립니다.</p><div class="qk">' + "".join(f'<a href="/jeonguk/{r[0]}.html">{r[1]} 목재 배송</a>' for r in _nt.REG) + '<a href="/jaedan-baesong.html">재단 후 전국 배송 방법</a></div></section>'
    _jg += '<section class="wrap sec"><h2>제품별로 찾아보기 — 사진·규격·기준가</h2><div class="qk">' + "".join(f'<a href="{h}">{t}</a>' for h, t in [("/bupum/p/", "철물·공구·부속 제품"), ("/bondex/p/", "본덱스 스테인·페인트"), ("/younglim/p/", "영림 도어·몰딩·필름"), ("/yerim/p/", "예림 중문·도어"), ("/shenu/p/", "쉐누 도어·몰딩"), ("/knauf/", "크나우프 석고·천장·단열"), ("/geonjae/p/", "목조·외장·내장 건축자재"), ("/suip/p/", "수입 창호·목조주택 자재"), ("/bigyo/", "자재·인테리어 비교")]) + '</div></section>'
    # 새로 올라온 하는 법·비교 — 새 글이 첫 화면에서 바로 링크되게(색인·노출 빨라짐)
    try:
        from qna_data import QNA as _HQ
        _hc = json.load(open(f"{ROOT}/data/compare.json", encoding="utf-8"))
        _nl = [(f"/qna/{q[0]}.html", q[1].split(" — ")[0]) for q in reversed(_HQ[-8:])] + [(f"/bigyo/{c['slug']}.html", c["title"].split(" — ")[0]) for c in reversed(_hc[-4:])]
        _jg += '<section class="wrap sec"><h2>새로 올라온 하는 법·비교</h2><div class="qk">' + "".join(f'<a href="{h}">{html.escape(t)}</a>' for h, t in _nl) + '</div><p class="small"><a href="/qna/">하는 법 Q&amp;A 전체 ›</a> · <a href="/bigyo/">자재 비교 전체 ›</a></p></section>'
    except Exception as _e: print("home new guide skip", _e)
    body = body.replace('<section class="cta">', _jg + '<section class="cta">', 1) if '<section class="cta">' in body else body + _jg
    # 처음 온 손님용 3단계 동선 + 나머지는 탭으로 접기(내용은 그대로 HTML에 있음 — 검색엔진은 전부 읽음)
    _f3 = ('<section class="wrap sec flow3"><h2>3단계로 끝내기</h2><div class="f3">'
           '<div class="f3c"><span class="f3n">1</span><b>자재 찾기·계산</b><p>어떤 자재가 얼마나 필요한지 확인해요.</p><div class="f3l"><a href="/jaryo/">전체 자재</a><a href="/calc.html">자재비 계산기</a><a href="/sajin.html">사진으로 찾기</a><a href="/price.html">기준가</a></div></div>'
           '<div class="f3c"><span class="f3n">2</span><b>재단·배송 문의</b><p>원하는 크기로 잘라 매장 픽업 또는 전국 배송.</p><div class="f3l"><a href="/cut.html">재단 그림 만들기</a><a href="/jeonguk/">전국 배송</a><a href="https://wwood.kr/home/mall/">쇼핑몰 주문</a><a href="tel:' + TEL.replace("-", "") + '">전화 ' + TEL + '</a></div></div>'
           '<div class="f3c"><span class="f3n">3</span><b>시공 의뢰</b><p>직접 하기 어렵다면 시공까지 맡기세요.</p><div class="f3l"><a href="/yeongyeol/">시공팀 연결</a><a href="/sigong.html">시공 사례</a><a href="/local/">지역별 시공</a></div></div>'
           '</div></section>')
    _TG = [("make", "만들기·시공법", r"DIY 만들기|자재 시공법|무엇을 만들고"), ("mat", "자재·가격", r"자재 백과|제품별로 찾아보기|기본 자재 기준가"), ("photo", "공간 사진", r"공간 사진 둘러보기"),
           ("video", "영상", r"새로 올라온 영상|많이 본 영상"), ("news", "소식", r"소식·자재 정보")]
    _first = [None]
    def _tag(mm):
        head = body[mm.end():mm.end() + 600]
        h = re.search(r"<h2[^>]*>(.*?)</h2>", head, re.S)
        if not h: return mm.group(0)
        for tid, _n, rx in _TG:
            if re.search(rx, re.sub(r"<[^>]+>", "", h.group(1))):
                if _first[0] is None: _first[0] = mm.start()
                return mm.group(0)[:-1] + f' data-tg="{tid}">'
        return mm.group(0)
    body = re.sub(r'<section class="wrap sec[^"]*">', _tag, body)
    _bar = '<section class="wrap sec tgbar" id="more"><h2>더 둘러보기</h2><div class="tgb" role="tablist">' + "".join(f'<button role="tab" data-t="{t}"{" class=on" if i == 0 else ""}>{n}</button>' for i, (t, n, _r) in enumerate(_TG)) + '</div></section>'
    body = body.replace("<!--MKHOME-->", _bar + "<!--MKHOME-->", 1) if "<!--MKHOME-->" in body else body
    _tl = body.find('<section class="wrap sec"><div class="tl4">')
    body = (body[:_tl] + _f3 + body[_tl:]) if _tl >= 0 else _f3 + body
    page("index.html", "대전 목재 영진목재 | 3000평 목재소, 원하는 사이즈 재단·전국 배송", "대전 영진목재(월드건축자재) 3000평 목재소. 합판·방부목·데크·구조재를 원하는 크기로 재단해 서울·경기·부산·제주까지 전국 배송, 기준가·시공 영상.", body, "", BIZ)

    # 소식·정보
    page("news/index.html", "소식·자재 정보 — 목재·건축자재 가격, 시공 팁 | 대전 월드건축자재", "대전 월드건축자재(영진목재)의 자재 정보, 기준가, 시공 사례, 새 영상 소식.",
         f'<section class="wrap sec"><h1>소식·자재 정보</h1><p class="lead">자재 고르는 법, 기준가, 시공 사례와 새 영상 소식을 매일 올립니다.</p>{nrow("▶ 새 영상", [p for p in POSTS if _isv(p) and not _iss(p)])}{nrow("⚡ 새 쇼츠", [p for p in POSTS if _isv(p) and _iss(p)])}{nrow("📘 자재 정보 글", [p for p in POSTS if not _isv(p) and "-news-" not in p.get("slug", "")])}{nrow("📰 자재·인테리어 소식", [p for p in POSTS if "-news-" in p.get("slug", "")])}</section>{CTA}', "/news/")
    for p in POSTS:
        vids = "".join(embed(byid[i]) if i in byid else f'<div class="emb"><iframe loading="lazy" src="https://www.youtube.com/embed/{E(i)}" allowfullscreen></iframe></div>' for i in p.get("videos", [])[:2])
        art = {"@context": "https://schema.org", "@type": "Article", "headline": p["title"], "datePublished": p.get("date", ""), "author": {"@type": "Organization", "name": "월드건축자재(영진종합목재)"}, "publisher": {"@type": "Organization", "name": "월드건축자재(영진종합목재)"}}
        pimg = f"https://i.ytimg.com/vi/{p['videos'][0]}/hqdefault.jpg" if p.get("videos") else None
        if pimg: art["image"] = pimg
        page(f"news/{p['slug']}.html", f"{p['title']} | 대전 월드건축자재", p.get("desc", p["title"]),
             f'<article class="wrap sec post"><p class="crumb"><a href="/news/">소식·정보</a> › {E(p.get("date",""))}</p><h1>{E(p["title"])}</h1>{vids}<div class="pb">{p["body"]}</div></article>{CTA}', "/news/", art, pimg)

    # 자재 백과
    lst = "".join(f'<a class="mc" href="/jajae/{m["slug"]}.html"><b>{m["name"]}</b><small>{" · ".join(m["where"][:2])}</small></a>' for m in MATS)
    page("jajae/index.html", "자재 백과 — 합판·MDF·방부목·석고보드 용도와 가격 | 월드건축자재 대전", "자재별 용도, 인테리어 효과, 소매 기준가, 시공 영상을 한 번에. 대전 월드건축자재(영진목재).",
         f'<section class="wrap sec"><h1>자재 백과</h1><p class="lead">손님들이 가장 헷갈리는 "이 자재 어디에 쓰나요?"를 자재별로 정리했습니다.</p><p><a class="b o" href="/bigyo/">자재 비교 전체 보기 (14종)</a> <a class="b o" href="/calc.html">자재 계산기</a> <a class="b o" href="/cut.html">재단 미리보기</a> <a class="b o" href="/mandeul/">만들기 자재 목록</a> <a class="b o" href="/yongeo.html">현장 용어 사전</a></p><div class="mg m2">{lst}</div></section>{CTA}', "/jajae/")
    for m in MATS:
        vs = top(lambda v: m["tag"] in v["mats"], 10**6)
        rel = [x for x in MATS if x is not m][:0]
        where = "".join(f"<li>{E(w)}</li>" for w in m["where"])
        tips = "".join(f"<li>{E(t)}</li>" for t in m["tips"])
        lf = [v for v in vs if v["type"] != "S"]
        vid = ((embed(lf[0]) if lf else "") + vsplit([v for v in vs if not lf or v is not lf[0]], "h3")) if vs else f'<p><a href="{YT}">유튜브 채널에서 보기</a></p>'
        _jj = (ord(m["name"][-1])-0xAC00)%28 if "가"<=m["name"][-1]<="힣" else 1
        faq = [{"@type": "Question", "name": f"{m['name']}{'은' if _jj else '는'} 어디에 쓰나요?", "acceptedAnswer": {"@type": "Answer", "text": ", ".join(m["where"])}},
               {"@type": "Question", "name": f"대전에서 {m['name']}{'을' if _jj else '를'} 어디서 사나요?", "acceptedAnswer": {"@type": "Answer", "text": f"월드건축자재(영진종합목재), {ADDR}, {TEL}. {HOURS}. 원하는 사이즈로 재단해 드립니다."}}]
        cmpl = {"hapan":"hapan-types","osb":"hapan-osb-mdf","mdf":"hapan-osb-mdf","bangbu":"bangbu-hapdeck","hapdeck":"bangbu-hapdeck","gypsum":"gypsum-types","siding":"siding-types","insul":"insulation-types","maru":"floor-types","tile":"floor-types","door":"door-types","stain":"stain-oil-water","hinoki":"louver-types","jipseong":"jipseong-types","gujo":"gakjae-types","sound":"sound-types","film":"door-types"}.get(m["slug"])
        cutln = f' · <a href="/cut.html#m={m["slug"]}">원하는 크기로 재단 그림 보기</a>' if m["slug"] in {"hapan","osb","mdf","gujo","bangbu","hapdeck","jipseong","hinoki","gypsum","insul"} else ""
        cmpln = f'<p>👉 <a href="/bigyo/{cmpl}.html">비슷한 자재와 비교해 보기</a> · <a href="/calc.html">필요한 양 계산하기</a>{cutln}</p>' if cmpl else (f'<p>👉 <a href="/calc.html#door">문짝·문틀 크기 계산하기</a></p>' if m["slug"] == "door" else f'<p>👉 <a href="/calc.html">필요한 양 계산하기</a>{cutln}</p>')
        import gagyeok as _g0
        cmpln += _g0.links(_g0.BYMAT.get(m["slug"], []))
        if m["slug"] in ("hardware", "bangbu", "hapdeck", "gujo"): cmpln += '<div class="qk qk2"><b>🔩 목재 철물</b><a href="/cheolmul/janseon.html">장선걸이</a><a href="/cheolmul/gidungbatchim.html">기둥받침</a><a href="/cheolmul/juchudol.html">주춧돌</a><a href="/cheolmul/mokjo.html">목조주택 철물</a><a href="/cheolmul/">전체 철물</a></div>'
        mf = MFAQ.get(m["slug"], []) + [(f"{m['name']} 지방(전국)으로도 배송되나요?", f"네, 전국 어디든 용달차로 보내 드립니다. 품목·수량·도착지를 알려 주시면 사무실에서 용달 운임 견적을 드리고, 입금 확인 후 바로 출고합니다. 대전·세종·공주·계룡·논산·금산·옥천은 직접 배송·현장 납품합니다. 문의 {TEL}")]
        _seen = {re.sub(r"[^가-힣A-Za-z0-9]|은|는|을|를", "", q) for q, a in mf}
        faq = [x for x in faq if re.sub(r"[^가-힣A-Za-z0-9]|은|는|을|를", "", x["name"]) not in _seen] + [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in mf]
        faqsec = (f'<section class="wrap sec"><h2>{m["name"]} 자주 묻는 질문</h2>' + faqslide(mf) + '</section>') if mf else ""
        ph = mat_photos(m["slug"])
        gal = (f'<section class="wrap sec"><h2>{m["name"]} 사진으로 보기 <small class="muted">매장 취급 {len(ph)}종</small></h2><div class="pg hrow">{"".join(pcard(p) for p in ph[:12])}</div>'
               + (f'<p class="small muted">사진을 누르면 상세 사진이 열립니다 · 전체 {len(ph)}종 중 {min(12,len(ph))}종 표시 · <a href="/jaryo/">전체 자재 보기 →</a></p>' if ph else '') + '</section>') if ph else ""
        body = f"""<section class="wrap sec"><p class="crumb"><a href="/jajae/">자재 백과</a> › {m['name']}</p>
<h1>{m['name']} — {m['kw']}</h1><p class="lead">{E(m['lead'])}</p>
<div class="row"><span class="chip">사용 장소: {E(m['place'])}</span><span class="chip">셀프 난이도: {E(m['diy'])}</span></div></section>{gal}
<section class="wrap sec g2"><div class="card"><h2>어디에 쓰나요?</h2><ul>{where}</ul><h3>인테리어 효과</h3><p>{E(m['effect'])}</p><h3>고를 때 알아둘 것</h3><ul>{tips}</ul>{cmpln}</div>
<div class="card"><h2>{m['name']} 소매 기준가</h2>{ptable(mat_prices(m))}<a href="/price.html">전체 기준가 →</a>{mall_links(m)}</div></section>
<section class="wrap sec"><h2>{m['name']} 시공·사용 영상</h2>{vid}</section><!--MK:{m['slug']}-->{faqsec}{CTA}"""
        _mp = mat_prices(m, 200); _lo = min((x["price"] for x in _mp if m["slug"] != "door" or (x["cat"] == "문" and re.search(r"@\d{3}", x["name"]))), default=0)
        page(f"jajae/{m['slug']}.html", (f"{m['kw']} — {_lo:,}원부터 · 규격 {len(_mp)}종 기준가 | 대전 영진목재" if _lo else f"{m['kw']} — 용도·기준가·시공 영상 | 대전 영진목재"),
             (f"{m['name']} 기준가 {_lo:,}원부터(부가세 별도), 규격 {len(_mp)}종. " if _lo else f"{m['name']} 용도와 인테리어 효과. ") + (f"실물 사진 {len(ph)}장, " if ph else "") + "시공 영상. 대전 유성 매장 즉석 재단·전국 배송.", body, "/jajae/",
             [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq}] + prod_ld(mat_prices(m, 5), f"{BASE}/jajae/{m['slug']}.html", ph[0]["img"] if ph else None),
             (ph[0]["img"] if ph else (f"https://i.ytimg.com/vi/{vs[0]['id']}/hqdefault.jpg" if vs else None)))

    # 전체 자재 검색용 목록
    jname = {c: n for c, sl, n, d in JCAT}; jslug = {c: sl for c, sl, n, d in JCAT}
    idx = [{"n": p["name"], "i": p["img"], "c": " · ".join(jname[t] for t in p["tops"] if t in jname), "s": MCAT.get(p["sub"] or "", ""), "u": jslug.get(p["top"], ""), "d": p["id"]}
           for p in PROD if p["tops"]]
    os.makedirs(f"{OUT}/assets", exist_ok=True)
    json.dump(idx, open(f"{OUT}/assets/jaryo.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    SEARCH = ('<div class="srch"><span class="si">🔍</span><input id="jq" type="search" placeholder="자재 이름으로 찾기 (예: 히노끼, OSB, 경첩)" autocomplete="off" aria-label="자재 검색"><a class="scam" href="/sajin.html#cam" title="카메라로 찾기" aria-label="카메라로 제품 찾기"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3.5 8.5A2.5 2.5 0 0 1 6 6h1.7l1.4-1.9A1.5 1.5 0 0 1 10.3 3.5h3.4a1.5 1.5 0 0 1 1.2.6L16.3 6H18a2.5 2.5 0 0 1 2.5 2.5v8.5A2.5 2.5 0 0 1 18 19.5H6A2.5 2.5 0 0 1 3.5 17z"/><circle cx="12" cy="12.6" r="3.7"/></svg></a>'
              '<p id="jqn" class="small muted"></p></div><div id="jsr" class="pg"></div>')
    # 전체 자재 (쇼핑몰 자재 사진 목록)
    cnt = {c: sum(1 for p in PROD if c in p["tops"]) for c, *_ in JCAT}
    thumb = {c: next((p["img"] for p in PROD if c in p["tops"]), "") for c, *_ in JCAT}
    jl = "".join(f'<a class="pd" href="/jaryo/{sl}.html"><span class="pi"><img loading="lazy" src="{E(thumb[c])}" alt="{n}"></span><b>{n}</b><small>{d} · {cnt[c]}종</small></a>' for c, sl, n, d in JCAT if cnt[c])
    jchips = "".join(f'<a class="chip" href="#c{sl}">{n} <small>{cnt[c]}</small></a>' for c, sl, n, d in JCAT if cnt[c])
    import cheolmul as _cm0
    _mtj = json.load(open(f"{ROOT}/data/megatie.json", encoding="utf-8"))
    _chrow = '<div class="chr" id="cheolmul"><p class="chl"><b>🔩 목재 철물</b> 데크·정자·파고라·목조주택·농막용 · <a class="cha" href="/cheolmul/">전체 보기 ›</a></p><div class="gcs">' + "".join(f'<a class="gc gpc" href="/cheolmul/{c[0]}.html">' + (f'<img loading="lazy" decoding="async" referrerpolicy="no-referrer" src="https://megatie.cafe24.com/web/product/{_mtj[c[0]][0][1][1:]}" alt="{E(c[1])}">' if _mtj.get(c[0]) else "") + f'<span>{E(c[1])}</span></a>' for c in _cm0.CH) + '</div></div>'
    import taka as _tk0, taka_data as _tkd
    _tkimg = {s: _tk0.IMG(_tkd.TOOLS[s][2][0][5]) for s in _tk0.ORDER}; _tkimg.update(pin=_tk0.IMG("4단위.jpg"), nail=_tk0.IMG("코일 네일못(플랫).png"), compressor=_tk0.IMG("JQS225-870.jpg"), etc=_tk0.IMG("폴리우레탄-연질-호스.jpg"))
    _chrow += '<div class="chr" id="taka"><p class="chl"><b>타카·타카핀·콤프레셔</b> 제일타카 422·F30·실핀·콘크리트 타카 · <a class="cha" href="/taka/">전체 보기 ›</a></p><div class="gcs">' + "".join(f'<a class="gc gpc" href="/taka/{s}.html"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" src="{_tkimg[s]}" alt="{E(v[0])}"><span>{E(v[0])}</span></a>' for s, v in [(k, _tk0.PG[k]) for k in _tk0.ORDER + ["pin", "nail", "compressor", "etc"]]) + '</div></div>'
    import cmbs as _cb0
    _cbc0, _cbr0 = _cb0.load(ROOT)
    if _cbr0:
        _cbt = {t: [r for r in _cbr0 if (lambda n: (lambda f: f(f, n))(lambda f, n: n if _cbc0.get(n, (1,))[0] == 1 else f(f, _cbc0[n][0])))(r[0]) == t] for t in _cb0.TOP}
        _chrow += '<div class="chr" id="bupum"><p class="chl"><b>철물·공구·부속</b> 손잡이·경첩·공구·욕실·전기·피스 ' + str(len(_cbr0)) + '종 · <a class="cha" href="/bupum/">전체 보기 ›</a></p><div class="gcs">' + "".join(f'<a class="gc gpc" href="/bupum/{v[0]}.html"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" src="{_cb0.IMG(_cbt[t][0][3])}" alt="{E(v[1])}"><span>{E(v[1])}</span></a>' for t, v in _cb0.TOP.items() if _cbt[t]) + '</div></div>'
    import yerim as _yr0
    _yrows = [l.rstrip("\n").split("|") for l in open(f"{ROOT}/data/yerim.tsv", encoding="utf-8") if l.strip()]
    _yrrow = '<div class="chr" id="yerim"><p class="chl"><b>예림 중문·도어·문틀</b> 3연동 중문·간살·ABS 도어·방화문 · <a class="cha" href="/yerim/">전체 보기 ›</a></p><div class="gcs">' + "".join(f'<a class="gc gpc" href="/yerim/{pg[0]}.html"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" src="{_yr0.IMG(next(r for r in _yrows if pg[4](r[0], r[1]))[4])}" alt="{E(pg[1])}"><span>{E(pg[1])}</span></a>' for pg in _yr0.PAGES) + '</div></div>'
    import younglim as _yl0
    _ylr = _yl0.load(ROOT)
    if _ylr: _yrrow += '<div class="chr" id="younglim"><p class="chl"><b>영림 도어·중문·마감재</b> ABS·멤브레인 도어·슬림 중문·몰딩·필름 · <a class="cha" href="/younglim/">전체 보기 ›</a></p><div class="gcs">' + "".join(f'<a class="gc gpc" href="/younglim/{pg[0]}.html"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" src="{_yl0.IMG(next(r for r in _ylr if r[0] in pg[2])[6])}" alt="{E(pg[1])}"><span>{E(pg[1])}</span></a>' for pg in _yl0.PAGES if any(r[0] in pg[2] for r in _ylr)) + '</div></div>'
    import shenu as _sh0
    _shr = _sh0.load(ROOT)
    if _shr: _yrrow += '<div class="chr" id="shenu"><p class="chl"><b>쉐누 도어·중문·몰딩</b> ABS·글래스 도어·3연동 중문·PVC 몰딩 · <a class="cha" href="/shenu/">전체 보기 ›</a></p><div class="gcs">' + "".join(f'<a class="gc gpc" href="/shenu/{pg[0]}.html"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" src="{_sh0.IMG(next(r for r in _shr if r[0] in pg[2])[1])}" alt="{E(pg[1])}"><span>{E(pg[1])}</span></a>' for pg in _sh0.PAGES if any(r[0] in pg[2] for r in _shr)) + '</div></div>'
    import emall as _em0
    _emc, _emr = _em0.load(ROOT)
    _bdrow = ""
    if _emr:
        _bdrow = '<div class="chr" id="bondex"><p class="chl"><b>본덱스 스테인·페인트·오일</b> 오일스테인·바니쉬·페인트·도장도구 ' + str(len(_emr)) + '종 · <a class="cha" href="/bondex/">전체 보기 ›</a></p><div class="gcs">' + "".join(f'<a class="gc gpc" href="/bondex/{sl}.html"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" width="300" height="300" src="{_em0.IMG(next(r for r in _emr if r[0] == t or _emc.get(r[0], (0,))[0] == t)[3])}" alt="본덱스 {E(_emc[t][1])}"><span>{E(_emc[t][1].replace("/", "·"))}</span></a>' for t, sl in _em0.SLUG.items() if t in _emc and any(r[0] == t or _emc.get(r[0], (0,))[0] == t for r in _emr)) + '</div></div>'
        if not cnt.get("35"): cnt["35"] = len(_emr); thumb["35"] = _em0.IMG(_emr[0][3])
    import samik as _sm0
    _smr = _sm0.load(ROOT)
    def _smrow(c):
        ts = [t for t, cc in _sm0.JC.items() if cc == c and any(r[0] == t for r in _smr)]
        if not ts: return ""
        return ('<div class="chr" id="gjr' + c + '"><p class="chl"><b>건축자재 ' + "·".join(ts) + '</b> ' + str(sum(1 for r in _smr if r[0] in ts)) + '종 · <a class="cha" href="/geonjae/' + _sm0.SLUG[ts[0]] + '.html">전체 보기 ›</a></p><div class="gcs">'
                + "".join(f'<a class="gc gpc" href="/geonjae/{_sm0.SLUG[t]}.html#s{i}"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" width="300" height="300" src="{(lambda r_: _sm0.IMG(r_[4], r_[2]))(next(r for r in _smr if r[0] == t and r[1] == sb))}" alt="{E(sb)}"><span>{E(sb)}</span></a>' for t in ts for i, sb in enumerate(dict.fromkeys(r[1] for r in _smr if r[0] == t))) + '</div></div>')
    import knauf as _kn0
    _knr = _kn0.load(ROOT)
    def _knrow(c):
        gs = [g for g, v in _kn0.GRP.items() if v[1] == c and any(r[0] == g for r in _knr)]
        if not gs: return ""
        return ('<div class="chr" id="knauf' + c + '"><p class="chl"><b>크나우프 ' + ("석고보드·천장재" if len(gs) > 2 else "·".join(gs)) + '</b> ' + str(sum(1 for r in _knr if r[0] in gs)) + '종 · <a class="cha" href="/knauf/' + _kn0.GRP[gs[0]][0] + '.html">전체 보기 ›</a></p><div class="gcs">'
                + "".join(f'<a class="gc gpc" href="/knauf/{_kn0.GRP[g][0]}.html"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" width="300" height="300" src="{_kn0.IMG(next(r for r in _knr if r[0] == g)[4], 400)}" alt="크나우프 {E(g)}"><span>{E(g)}</span></a>' for g in gs) + '</div></div>')
    import homewood as _hw0
    _hwr = _hw0.load(ROOT)
    def _hwrow(c):
        gs = [g for g in _hw0.GRP if g[3] == c and any(r["g"] == g[0] for r in _hwr)]
        if not gs: return ""
        xs = [r for r in _hwr if r["g"] in [g[0] for g in gs]]
        subs = list(dict.fromkeys((r["g"], r["sub"]) for r in xs))[:14]
        return ('<div class="chr" id="suip' + c + '"><p class="chl"><b>수입 목조주택 ' + "·".join(g[0] for g in gs) + '</b> ' + str(len(xs)) + '종 · <a class="cha" href="/suip/' + gs[0][1] + '.html">전체 보기 ›</a></p><div class="gcs">'
                + "".join(f'<a class="gc gpc" href="/suip/{_hw0.GN[g][1]}.html"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" width="247" height="300" src="{_hw0.img(next(r for r in xs if r["g"] == g and r["sub"] == sb)["i"])}" alt="{E(sb)}"><span>{E(sb)}</span></a>' for g, sb in subs) + '</div></div>')
    import nichiha as _nh0
    _nhr = _nh0.load(ROOT)
    _nhrow = ('<div class="chr" id="nichiha"><p class="chl"><b>니치하 세라믹 사이딩</b> 16×455×3,030mm · 우드·스톤·타일벽돌 ' + str(len(_nhr)) + '종 · <a class="cha" href="/nichiha/">전체 보기 ›</a></p><div class="gcs">'
              + "".join(f'<a class="gc gpc" href="/nichiha/#{k}"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" width="300" height="300" src="{_nh0.TH(next(r for r in _nhr if r[0] == k)[1])}" alt="니치하 {E(nm)}"><span>{E(nm)}</span></a>' for k, nm, d in _nh0.VIS if any(r[0] == k for r in _nhr)) + '</div></div>') if _nhr else ""
    jrows = "".join(f'<section class="wrap sec jall" id="c{sl}"><h2>{n} <small class="muted">{cnt[c]}종</small> <a class="small" href="/jaryo/{sl}.html">전체 보기 ›</a></h2><p class="small muted">{d}</p>{_chrow if c == "32" else ""}{_yrrow if c == "29" else ""}{_bdrow if c == "35" else ""}{_nhrow if c == "31" else ""}{_knrow(c)}{_hwrow(c)}{_smrow(c)}<div class="pg hrow">' + "".join(pcard(p) for p in [p for p in PROD if c in p["tops"]][:16]) + f'<a class="pd more" href="/jaryo/{sl}.html"><span class="pi"><b>+{max(0,cnt[c]-16)}</b></span><b>{n} 전체 보기 ›</b><small>{cnt[c]}종</small></a></div><p class="hsh">옆으로 밀어서 더 보기 ›</p></section>' for c, sl, n, d in JCAT if cnt[c])
    page("jaryo/index.html", f"전체 자재 사진 {len([p for p in PROD if p['tops']])}종 — 각재·합판·데크·사이딩·철물 | 대전 영진목재", "대전 월드건축자재(영진목재) 매장 취급 자재를 사진으로 확인하세요. 각재, 합판, 집성판, 데크, 마루, 내장재, 타일, 사이딩, 철물, 스테인.",
         f'<section class="wrap sec"><h1>전체 자재</h1>{SEARCH}<p class="lead">매장에서 취급하는 자재를 사진으로 모았습니다. 실물은 대전 매장에서 보고, 원하는 사이즈로 재단해 가세요. 가격은 <a href="/price.html">기준가</a> 또는 매장에서 안내합니다.</p><div class="chips jall jchips">{jchips}</div></section>{jrows}{CTA}', "/jaryo/", None, thumb.get("24"))
    for c, sl, n, d in JCAT:
        ps = [p for p in PROD if c in p["tops"]]
        if not ps and not (c == "35" and _bdrow): continue
        subs = []
        for p in ps:
            if subof(p, c) not in subs: subs.append(subof(p, c))
        secs = (_yrrow if c == "29" else (_bdrow if c == "35" else (_nhrow if c == "31" else ""))) + _knrow(c) + _hwrow(c) + _smrow(c)
        for sb in subs:
            g = [p for p in ps if subof(p, c) == sb]
            title = MCAT.get(sb or "", "") or "기타"
            secs += f'<h2 id="s{(sb or "x").split("/")[-1] or "x"}">{E(title)} <small class="muted">{len(g)}종</small></h2>{_chrow if "건축철물" in title else ""}<div class="pg hrow">{"".join(pcard(p) for p in g)}</div>' + ('<p class="hsh">옆으로 밀어서 더 보기 ›</p>' if len(g) > 2 else '')
        toc = " · ".join(f'<a href="#s{(sb or "x").split("/")[-1] or "x"}">{E(MCAT.get(sb or "", "") or "기타")}</a>' for sb in subs)
        _jv = sorted([v for v in V if re.search(JVRX.get(c, "$^"), v["title"].split("|")[0] + " " + v["title"])], key=lambda v: -v["n"])
        _jvs = (f'<section class="wrap sec"><h2>{n} 관련 영상 <small class="muted">{len(_jv)}편</small></h2><p class="small muted">월드건축자재DIY 채널에서 이 자재를 직접 쓰고 고르는 영상입니다.</p>' + vsplit(_jv, "h3", 6, 12) + '</section>') if _jv else ""
        if not ps: ps_n = cnt[c]
        page(f"jaryo/{sl}.html", f"{n} 종류 사진 {len(ps) or cnt[c]}종 — {d} | 대전 월드건축자재", f"{n} 종류를 사진으로 확인하세요: {d}. 대전 유성 월드건축자재(영진목재) 매장 취급, 즉석 재단.",
             f'<section class="wrap sec"><p class="crumb"><a href="/jaryo/">전체 자재</a> › {n}</p><h1>{n} <small class="muted">{len(ps)}종</small></h1><p class="lead">{d}. 사진을 누르면 상세 사진이 열립니다. 실물 확인·재단은 대전 매장에서 합니다.</p>{SEARCH}<div class="jall"><p class="small">{toc}</p>{secs}</div></section>{_jvs}{CTA}', "/jaryo/",
             {"@context": "https://schema.org", "@type": "ItemList", "name": f"{n} 종류", "numberOfItems": len(ps),
              "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": p["name"], "image": p.get("img0") or p["img"]} for i, p in enumerate(ps[:100])]}, (ps[0].get("img0") or ps[0]["img"]) if ps else thumb.get(c))

    # 영상
    vl = "".join(f'<a class="uc" href="/video/{c}.html"><b>{n}</b><small>{d} · {sum(1 for v in V if v["cat"]==c)}편</small></a>' for c, n, d in CATS)
    PLS = [('PLFOIw225ouPo', '건축자재 종류 & 방부목 데크'), ('PLVA2J1KAJvsk', '목조 비닐하우스 짓기'), ('PLahzdcM8tSYQ', '목공 기초 & 원목 가구'), ('PLdOhbZ-KJAiQ', '싱크대 셀프 리폼'), ('PLSZCoKnD3ZJs', '세라믹사이딩 외벽 시공'), ('PLRSwZ8WxHpV8', '인테리어 필름 시공·견적'), ('PLbvlO5h0i7mo', '반셀프 인테리어 공정 순서'), ('PLfQ12jGtwTx0', '인테리어 견적 비교'), ('PLCMIh2xFaEFE', '주차장·토목 현장'), ('PLE3-sMP7uo2k', '건축자재 꿀팁 쇼츠'), ('PLEp1gBHSiHds', 'CNC 목공 라이브')]
    plh = "".join(f'<a href="https://www.youtube.com/playlist?list={i}" target="_blank" rel="noopener">▶ {n}</a>' for i, n in PLS)
    _tl = top(lambda v: v["type"] != "S", 50); _ts = top(lambda v: v["type"] == "S", 50)
    _tld = {"@context": "https://schema.org", "@type": "ItemList", "name": "월드건축자재DIY 많이 본 영상 TOP 50", "itemListOrder": "https://schema.org/ItemListOrderDescending",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": BASE + vpage(v) if vpage(v).startswith("/") else vpage(v), "name": v["title"][:100]} for i, v in enumerate(_tl)]}
    page("video/top.html", f"많이 본 영상 TOP 50 — 셀프 인테리어·목공·데크 인기 영상 순위 | 월드건축자재DIY", "월드건축자재DIY 유튜브에서 조회수가 가장 많은 영상과 쇼츠 순위입니다. 데크, 목조 온실, 샷시, 싱크대, 원목가구 시공 영상.",
         f'<section class="wrap sec"><p class="crumb"><a href="/video/">영상</a> › 많이 본 영상 TOP</p><h1>🏆 많이 본 영상 TOP 50</h1><p class="lead">유튜브 「월드건축자재DIY」·「월드도어」 영상 {len(V)}편 중 조회수가 많은 순서입니다. 순위는 새 영상이 올라올 때마다 자동으로 바뀝니다.</p>'
         f'<p><a class="b o" href="#tl">▶ 일반 영상 TOP 50</a> <a class="b o" href="#ts">⚡ 쇼츠 TOP 50</a></p><h2 id="tl">▶ 일반 영상 TOP 50</h2>{vrank(_tl)}<h2 id="ts">⚡ 쇼츠 TOP 50</h2>{vrank(_ts, "sgt")}</section>{CTA}', "/video/", _tld)
    page("video/index.html", "시공·DIY 영상 모음 — 데크·온실·가구·외벽·인테리어 | 월드건축자재DIY", "월드건축자재DIY 유튜브 영상을 용도별로 정리했습니다. 데크, 목조 온실, 원목가구, 싱크대, 외벽, 바닥, 전기.",
         f'<section class="wrap sec"><h1>영상으로 찾기</h1><p class="lead">유튜브 「월드건축자재DIY」·「월드도어」 공개 영상 {len(V)}편(일반·쇼츠·라이브)을 용도별로 모두 모았습니다. 새 영상은 자동으로 추가됩니다.</p><p><a class="b r" href="/video/top.html">🏆 많이 본 영상 TOP 50</a></p><div class="ug m2">{vl}</div><h2>유튜브 재생목록</h2><div class="plc">{plh}</div><p><a href="{YT}">유튜브 채널 바로가기 →</a></p></section>{CTA}', "/video/")
    for c, n, d in CATS:
        vs = top(lambda v: v["cat"] == c, 10**6)
        page(f"video/{c}.html", f"{n} 영상 — {d} | 월드건축자재DIY 대전", f"{n} 관련 시공·DIY 영상 모음({d}). 영상에 나온 자재는 대전 월드건축자재 매장에서.",
             f'<section class="wrap sec"><p class="crumb"><a href="/video/">영상</a> › {n}</p><h1>{n}</h1><p class="lead">{d}</p>{vsplit(vs)}<p><a href="{YT}">더 많은 영상은 유튜브에서 →</a></p></section>{CTA}', "/video/",
             {"@context": "https://schema.org", "@type": "ItemList", "name": f"{n} 영상", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": vurl(v), "name": v["title"]} for i, v in enumerate(vs)]},
             f"https://i.ytimg.com/vi/{vs[0]['id']}/hqdefault.jpg" if vs else None)

    # 기준가
    groups = {}
    for p in sorted(P, key=lambda p: -p["qty"]):
        groups.setdefault(p["cat"], []).append(p)
    skip = {"-호차 영림", "가공"}
    row = lambda p, rk="": f"<tr><td class=pn>{rk}<a class=plk href=\"{plink(p)}\">{E(clean_name(p['name']))}<i>›</i></a>{"" if rk else badge(p)}</td><td class=pp><b>{won(p['price'])}</b>{chg(p)}</td></tr>"
    th = '<thead><tr><th>품목·규격 <small>(누르면 자재 안내)</small></th><th class=r>소매 기준가</th></tr></thead>'
    GN = {"문": "도어(문짝)", "문틀": "문틀", "문제": "문 부속·레일", "진열": "인테리어 철물", "부재": "부자재", "엠디": "MDF", "합성": "합성데크",
          "오일": "오일스테인", "목재": "다루끼·각재", "구조": "구조재", "방부": "방부목", "석고": "석고보드", "단열": "단열재", "가든": "침목·조경",
          "데크": "원목 마루재", "특수": "적삼목·특수목", "내장": "내장재", "외장": "외장재", "본드": "본드·접착제", "필름": "인테리어필름", "계단": "계단재",
          "피스": "피스", "타카": "타카핀", "철물": "건축 철물", "몰딩": "몰딩", "루바": "루바", "마루": "마루", "집성판": "집성판", "합판": "합판",
          "사이딩": "사이딩", "각재": "각재", "공구": "공구"}
    order = sorted([k for k in groups if k not in skip], key=lambda k: -max(p["qty"] for p in groups[k]))
    chips = "".join(f'<button type="button" class="chip{" on" if i == 0 else ""}" data-k="{i}">{E(GN.get(k, k))} <small>{len(groups[k])}</small></button>' for i, k in enumerate(order))
    psearch = '<div class="srch ptop"><span class="si">🔍</span><input id="pq" type="search" placeholder="품목 검색 (예: 9.5T, 투바이, 경첩, OSB)" autocomplete="off" aria-label="기준가 품목 검색"><p id="pqn" class="small muted"></p></div>'
    secs = (f'<div class="chips" id="pchips">{chips}</div><div class="pnav"><button type="button" id="pprev">◀ 이전</button><span id="pcur"></span><button type="button" id="pnext">다음 ▶</button></div>'
            + '<div id="psecs">' + "".join(f'<div class="psec{" on" if i == 0 else ""}" data-k="{i}" data-n="{E(GN.get(k, k))}"><h2>{E(GN.get(k, k))} <small class="muted">{len(groups[k])}개</small></h2><div class="tw"><table class="pt">{th}<tbody>'
                                         + "".join(row(p) for p in groups[k]) + "</tbody></table></div></div>" for i, k in enumerate(order)) + '</div>'
            + '<p class="small muted swipe-hint">← 옆으로 밀면 다음 분류로 넘어갑니다 →</p>')
    top10 = sorted(P, key=lambda p: -p["qty"])[:10]
    upn = sum(1 for p in P if PREV.get(p["name"]) and PREV[p["name"]] < p["price"]); dnn = sum(1 for p in P if PREV.get(p["name"]) and PREV[p["name"]] > p["price"])
    board = (f'<div class="card pb2"><h2>많이 찾는 자재 TOP 10</h2><p class="small muted">매장 판매 순위 기준 · 기준가 갱신일 {E(PMETA.get("updated",""))} · '
             f'지난 갱신 대비 <span class="up">▲ 오른 품목 {upn}</span> · <span class="dn">▼ 내린 품목 {dnn}</span></p>'
             + '<div class="tslide" id="tslide">' + "".join('<div class="tpage"><table class="pt">' + th + '<tbody>' + "".join(row(p, f'<span class="rk">{i+1}</span>') for i, p in list(enumerate(top10))[a:a+5]) + '</tbody></table></div>' for a in (0, 5)) + '</div>'
             + '<div class="tdots"><button type="button" class="tb" data-d="-1">◀</button><span id="tdot">1–5위 / 6–10위 ▶ 옆으로 밀기</span><button type="button" class="tb" data-d="1">▶</button></div></div>')
    secs = '<div class="pboard">' + board + '</div>' + secs
    page("price.html", "목재 가격 기준가 공개 — 합판·MDF·구조재·방부목·석고보드 | 대전 영진목재", "대전 월드건축자재(영진목재) 소매 기준가. 부가세 별도, 결제·재단은 매장에서.",
         f'<section class="wrap sec ptsec"><h1>소매 기준가</h1>{psearch}<p class="lead">자주 찾는 자재의 소매 기준가입니다(부가세 별도). 규격·수량에 따라 달라지며 <a href="/cut.html#fee">재단비</a> 1컷 1,000원~(두께별) · 운임은 매장에서 계산합니다. 도매가는 <a href="/dome.html">도매회원</a> 로그인 후 확인하세요. 크기·두께는 <a href="/gyugyeok.html">규격표</a>, 어떻게 잘리는지는 <a href="/cut.html">재단 미리보기</a>에서 보세요.</p>{secs}<div class="qk"><b>💰 1평에 얼마?</b><a href="/gagyeok/hapan-gagyeok.html">합판</a><a href="/gagyeok/seokgo-gagyeok.html">석고보드</a><a href="/gagyeok/osb-gagyeok.html">OSB</a><a href="/gagyeok/mdf-gagyeok.html">MDF</a><a href="/gagyeok/danyeol-gagyeok.html">아이소핑크</a><a href="/gagyeok/jipseong-gagyeok.html">집성판</a><a href="/gagyeok/deck-gagyeok.html">데크재</a><a href="/gagyeok/gakjae-gagyeok.html">구조재·각재</a><a href="/gagyeok/siding-gagyeok.html">사이딩</a><a href="/gagyeok/molding-gagyeok.html">몰딩</a><a href="/gagyeok/door-gagyeok.html">방문·문틀</a><a href="/gagyeok/hinoki-ruba.html">히노끼 루바</a><a href="/gagyeok/spruce-ruba.html">스프러스 루바</a><a href="/gagyeok/tempa-board.html">템바보드</a><a href="/gagyeok/tempa-ruba.html">템바 루바</a><a href="/gagyeok/interior-film.html">인테리어 필름</a><a href="/gagyeok/oilstain.html">오일스테인</a><a href="/gagyeok/">자재 가격 가이드</a></div></section>{CTA}', "/price.html")

    # 도매
    page("dome.html", "건축자재 도매·현장 납품 — 인테리어 업체·목수 도매회원 | 대전 월드건축자재", "인테리어 업체·목수·시공사 도매회원. 사업자등록증·명함 확인 후 승인, 회원가 적용, 현장 납품, 세금계산서 월 1회.",
         f"""<section class="wrap sec"><h1>건축자재 도매 · 현장 납품</h1><p class="lead">인테리어 업체, 목수팀, 시공사는 도매회원으로 등록하면 회원가로 거래합니다. 각재·합판부터 데크·사이딩·철물까지 한 곳에서 맞추세요.</p>
<div class="g4"><div class="card"><b>도매회원가</b><p class="small">로그인하면 소매 기준가보다 낮은 회원가로 표시</p></div><div class="card"><b>현장 납품</b><p class="small">대량 주문 현장 직접 배송 · 전국운임표</p></div>
<div class="card"><b>세금계산서</b><p class="small">당월 거래분 월 1회(10일) 발행</p></div><div class="card"><b>자재 한 번에</b><p class="small">800여 품목 · 재단 가공 · 매장 상차</p></div></div>
<h2>가입 절차</h2><ol><li>도매회원 쇼핑몰에서 회원가입</li><li>사업자등록증과 명함 업로드</li><li>두 서류 정보가 일치하면 승인 → 회원가 적용</li></ol>
<a class="b r" href="{DOME}">도매회원 쇼핑몰(wwood.kr)로 가기</a></section>{CTA}""", "/dome.html")

    # 시공
    sv = vsplit(top(lambda v: v["cat"] in ("exterior", "greenhouse", "deck"), 10**6), "h3", 12, 6)
    tips = vsplit(top(lambda v: v["cat"] == "tips", 10**6), "h3", 8, 6)
    case = [p for p in PROD if any(c.split("/")[0] in ("54", "59") for c in p["cats"]) and not re.search(r"company|INC", p["name"], re.I)]
    casesec = f'<section class="wrap sec"><h2>시공 사례 사진 <small class="muted">{len(case)}건</small></h2><div class="pg hrow">{"".join(pcard(p) for p in case)}</div></section>' if case else ""
    page("sigong.html", "대전·세종 인테리어 시공 — 외벽·샷시·데크·리모델링 | 월드아키텍쳐(실내건축공사업)", f"월드아키텍쳐 {LIC}. 대전·세종 외벽 사이딩, 샷시 교체, 데크, 실내 인테리어 시공. 관급·대기업 공사 수행. 전화 {TEL}.",
         f"""<section class="hero dark"><div class="wrap"><span class="chip red">월드아키텍쳐 · {LIC}</span><h1>직접 하기 어렵다면,<br>자재 파는 저희가 시공까지 합니다</h1>
<p class="lead">자재를 가장 잘 아는 목재상이 직접 시공합니다. 관급·대기업 공사를 수행하는 시공팀이 작업하고, 모든 시공 현장은 유튜브에 그대로 공개합니다.</p>
<div class="row"><a class="b r" href="tel:{TEL.replace('-','')}">시공 상담 전화 {TEL}</a><a class="b" href="/yeongyeol/">공정별 시공팀 연결 ›</a></div><p class="small">시공 지역: 외벽 사이딩은 전국 · 실내 공정은 대전·세종·공주·계룡·금산·옥천·천안·청주 · 관급·대기업 공사는 전화 문의</p></div></section><section class="wrap sec gg"><h2 class="gt">우리 동네 시공 찾기</h2><div class="qk">{"".join(f'<a href="/local/{a}-{b}.html">{c} {d}</a>' for a, d in (("jungmun", "중문"), ("door", "방문 교체"), ("film", "필름"), ("molding", "몰딩"), ("wall", "템바보드 벽")) for b, c in (("yuseong", "유성구"), ("seogu", "서구"), ("sejong", "세종")))}<a href="/local/">전체 지역 보기 ›</a></div></section>
{"".join([]) if not os.path.exists(ROOT+"/data/cases.json") else "<section class=\"wrap sec\"><h2>시공 사례</h2><div class=\"pl hs\">" + "".join(f'<a class="pc" href="/sigong/{c["slug"]}.html"><img loading="lazy" src="https://i.ytimg.com/vi/{c["videos"][0]}/mqdefault.jpg" alt=""><small>{E(c["place"] or "월드아키텍쳐 시공")}</small><b>{E(c["title"])}</b><span>{E(c["desc"][:70])}…</span></a>' for c in json.load(open(ROOT+"/data/cases.json", encoding="utf-8"))) + "</div><p class=\"hsh\">옆으로 밀어서 더 보기 ›</p></section>"}
<section class="wrap sec"><h2>시공 현장 영상</h2>{sv}</section>{casesec}
<section class="wrap sec g2"><div class="card"><h2>상담 순서</h2><ol><li>전화 상담 {TEL}</li><li>현장 방문 · 실측</li><li>견적서</li><li>시공 (현장은 유튜브 공개)</li></ol></div>
<div class="card"><h2>업체 고르기 전에 꼭 보세요</h2><p>면허 확인, 하자 예방, 견적 보는 법 영상을 모았습니다. 월드아키텍쳐는 실내건축공사업 등록 업체입니다.</p><a href="/video/tips.html">업체 고르는 법 영상 모음 →</a></div></section>
<section class="wrap sec">{tips}</section>{CTA}""", "/sigong.html")

    # 매장
    # 전국 용달 배송 안내 (회원 70%가 대전 밖)
    _BR = [("경기·서울·인천", "수도권 인테리어·목공 현장, 카페·상가 공사"), ("충남·충북", "천안·아산·청주·공주·논산 주택·창고 공사"), ("경북·경남·대구·부산·울산", "영남권 데크·목조 주택·리모델링"),
           ("전북·전남·광주", "호남권 데크·평상·조경 목재"), ("강원", "전원주택·펜션 데크·내장재")]
    _BF = [("대전에서 먼 지역도 보내 주나요?", "네. 대전·세종·공주·계룡·논산·금산·옥천은 직접 배송·현장 납품하고, 그 밖의 전국은 용달(화물차)로 보내 드립니다."),
           ("운임은 얼마인가요?", "거리·차량 크기·수량에 따라 달라 정해진 금액이 없습니다. 품목과 수량, 받는 주소를 알려 주시면 사무실에서 운임을 먼저 알려 드리고, 입금 확인 후 출고합니다."),
           ("재단비는 얼마인가요?", "1컷(한 번 자르기)당 두께별로 12T 이하 1,000원, 15·18T 1,500원, 20T 이하 2,000원, 24T 이하 2,500원, 30T 이하 3,000원입니다(부가세 별도). 30T가 넘는 두께(2×4·2×6·4×4 등)는 전화로 문의해 주세요. 재단 미리보기에서 크기를 넣으면 컷 수와 재단비가 바로 계산됩니다."),
           ("재단해서 보내 주나요?", "네. 원하는 크기로 재단한 뒤 보내 드립니다. 재단 크기는 재단 미리보기에서 그림으로 만들어 메일로 보내 주시면 정확합니다."),
           ("한두 장도 보내 주나요?", "소량도 보낼 수 있지만 용달 운임이 자재값보다 클 수 있습니다. 가까운 분은 방문 구매가 경제적이고, 먼 곳은 한 번에 모아서 주문하시는 것을 권합니다."),
           ("주문은 어떻게 하나요?", f"전화({TEL})나 메일({EMAIL})로 품목·규격·수량·받는 주소·받는 분 연락처를 알려 주세요. 사업자는 도매회원(wwood.kr)으로 가입하시면 회원가로 주문할 수 있습니다.")]
    # 규격표 — 매장 취급 제품 기준 크기·두께(가격 없음)
    def _gy():
        rows = list(csv.DictReader(open(ROOT + "/data/prices.csv", encoding="utf-8")))
        SZ = {"4*8": "1220×2440", "3*6": "900×1800"}
        def sheet(cat, label, note):
            g = collections.OrderedDict()
            for r in rows:
                if r["cat"] != cat: continue
                n = re.sub(r"^[^-]+-\s*", "", r["name"])
                m = re.search(r"(\d{3,4})\s*\*\s*(\d{3,4})\s*\*\s*(\d+(?:\.\d+)?)\s*T", n)
                if m: size, th, typ = f"{m.group(1)}×{m.group(2)}", m.group(3), n[:n.find("@")].strip() or label
                else:
                    m2 = re.search(r"([34])\s*\*\s*([68])", n); t = re.search(r"@\s*(\d+(?:\.\d+)?)\s*(?:mm|T)", n)
                    if not (m2 and t): continue
                    size, th = SZ[m2.group(1) + "*" + m2.group(2)], t.group(1)
                    typ = re.sub(r"\s*[34]\s*\*\s*[68].*$", "", n).strip() or label
                typ = re.sub(r"\s+", " ", typ)
                g.setdefault((typ, size), set()).add(float(th))
            if not g: return ""
            trs = "".join(f"<tr><td>{E(t)}</td><td>{sz}</td><td>{', '.join(('%g' % x) for x in sorted(v))}</td></tr>" for (t, sz), v in g.items())
            return f'<div class="gs" data-l="{label}"><h2>{label} 규격</h2><p class="muted small">{note}</p><div class="tw"><table><thead><tr><th>종류</th><th>크기(mm)</th><th>두께(mm)</th></tr></thead><tbody>{trs}</tbody></table></div></div>'
        def lin(cats, label, note):
            trs = []
            for r in rows:
                if r["cat"] not in cats: continue
                n = re.sub(r"^[^-]+-\s*", "", r["name"])
                if re.search(r"클립|브라켓|캡|지주|본드", n): continue
                a, _, b = n.partition("@")
                trs.append(f"<tr><td>{E(a.strip() or n)}</td><td>{E(b.strip())}</td></tr>")
            return f'<div class="gs" data-l="{label}"><h2>{label} 규격</h2><p class="muted small">{note}</p><div class="tw"><table><thead><tr><th>종류</th><th>단면·길이</th></tr></thead><tbody>{"".join(trs)}</tbody></table></div></div>' if trs else ""
        body = (sheet("합판", "합판", "4×8 = 1220×2440mm, 3×6 = 900×1800mm. (베)=베트남, (인)=인도네시아, OSB·태고(코팅)·오쿠메 등은 종류별로 따로 표시했습니다.")
              + sheet("엠디", "MDF", "MDF는 4×8(1220×2440) 원판 기준입니다. 고밀도·LPM(백색 코팅)은 따로 표시했습니다.")
              + sheet("집성판", "집성판", "수종에 따라 원판 크기가 1200×2400 또는 1220×2440으로 조금 다릅니다.")
              + sheet("석고", "석고보드", "3×6 = 900×1800mm. 일반·방수·방화 석고보드.")
              + sheet("단열", "단열재", "아이소핑크·스티로폼은 900×1800, 이보드는 900×2400 기준입니다.")
              + lin(["구조"], "구조재", "2×4는 실제 38×89mm입니다. 12ft는 약 3.6m입니다.")
              + lin(["방부"], "방부목", "12자는 약 3.6m입니다. 데크재와 각재(2×4, 4×4 등).")
              + lin(["목재", "각재"], "각재·다루끼", "1.0×1.0은 1치×1치(약 30×30mm), 12자는 약 3.6m입니다.")
              + lin(["합성", "데크"], "데크재", "합성데크와 하드우드 데크재(시우리·캠퍼스·큐링)."))
        labs = re.findall(r'class="gs" data-l="([^"]+)"', body)
        chips = "".join(f'<button type="button" data-i="{i}"{" class=on" if i == 0 else ""}>{E(l)}</button>' for i, l in enumerate(labs))
        css = ('<style>.gsrch{position:relative;margin:0 0 12px}.gsrch input{width:100%;box-sizing:border-box;font-size:17px;padding:13px 14px 13px 42px;border:2px solid #d9d3c7;border-radius:12px;background:#fff}.gsrch input:focus{outline:0;border-color:#c8101a}.gsrch span{position:absolute;left:14px;top:12px;font-size:18px}'
               '.gchip{display:flex;gap:6px;overflow-x:auto;padding:2px 0 10px;scrollbar-width:none}.gchip::-webkit-scrollbar{display:none}.gchip button{flex:0 0 auto;border:1px solid #d9d3c7;background:#fff;border-radius:999px;padding:8px 14px;font-size:15px;font-weight:700;color:#333}.gchip button.on{background:#1f1d1a;color:#fff;border-color:#1f1d1a}'
               '.gyc{display:flex;align-items:flex-start;overflow-x:auto;scroll-snap-type:x mandatory;gap:14px;scrollbar-width:none;-webkit-overflow-scrolling:touch}.gyc::-webkit-scrollbar{display:none}.gs{flex:0 0 100%;scroll-snap-align:start;box-sizing:border-box;background:#fff;border:1px solid #e6e0d4;border-radius:16px;padding:16px}.gs h2{margin-top:0}.gs .tw{overflow-x:auto}'
               '.gnav{display:flex;justify-content:space-between;align-items:center;margin-top:8px;font-size:14px;color:#777}.gnav button{border:1px solid #d9d3c7;background:#fff;border-radius:10px;padding:8px 14px;font-size:15px}.gyc.q{display:block}.gyc.q .gs{margin-bottom:12px}.gyc.q .gs.no{display:none}#gyn{min-height:1em}</style>')
        js = ('<script>(function(){var c=document.getElementById("gyc"),S=[].slice.call(c.querySelectorAll(".gs")),B=[].slice.call(document.querySelectorAll(".gchip button")),pg=document.getElementById("gpg"),q=document.getElementById("gyq"),n=document.getElementById("gyn");'
              'function W(){return S.length>1?S[1].offsetLeft-S[0].offsetLeft:c.clientWidth}function cur(){return Math.round(c.scrollLeft/W())}function mark(i){B.forEach(function(b,k){b.classList.toggle("on",k==i)});if(B[i])B[i].scrollIntoView({block:"nearest",inline:"center"});pg.textContent=(i+1)+" / "+S.length+" · 옆으로 밀어서 넘기기"}'
              'function go(i){i=Math.max(0,Math.min(S.length-1,i));if(c.classList.contains("q")){q.value="";filt()}c.scrollTo({left:i*W(),behavior:"smooth"});mark(i)}'
              'var t;c.addEventListener("scroll",function(){clearTimeout(t);t=setTimeout(function(){if(!c.classList.contains("q"))mark(cur())},80)});'
              'B.forEach(function(b){b.onclick=function(){go(+b.dataset.i)}});document.getElementById("gpv").onclick=function(){go(cur()-1)};document.getElementById("gnx").onclick=function(){go(cur()+1)};'
              'function norm(x){return x.toLowerCase().replace(/[\\s×x*\\-]/g,"").replace(/투바이포|투바이/g,"24")}'
              'function filt(){var v=norm(q.value),hit=0,nm=v.match(/^(\\d+(?:\\.\\d+)?)(t|mm|미리)$/);c.classList.toggle("q",!!v);S.forEach(function(s){var any=0;[].forEach.call(s.querySelectorAll("tbody tr"),function(r){var td=r.cells,tx=[].map.call(td,function(x){return x.textContent}).join(" | ");var ok=!v||(nm?(td.length==3?(" "+td[2].textContent.replace(/[^0-9.]+/g," ")+" ").indexOf(" "+nm[1]+" ")>=0:new RegExp("(^|[^0-9.])"+nm[1].replace(".","\\\\.")+"(t|mm)","i").test(tx.replace(/\\s/g,""))):norm(tx+" "+s.dataset.l).indexOf(v)>=0);r.style.display=ok?"":"none";if(ok&&v){any++;hit++}});s.classList.toggle("no",!!v&&!any)});n.textContent=v?(hit?hit+"개 찾음":"찾는 규격이 없어요. 매장에 전화로 물어봐 주세요."):"";document.querySelector(".gnav").style.display=v?"none":"";document.querySelector(".gchip").style.display=v?"none":""}'
              'q.addEventListener("input",filt);mark(0)})();</script>')
        return ('<div class="gsrch"><span>🔍</span><input id="gyq" type="search" placeholder="규격 검색 (예: 12T, OSB, 2x4)" autocomplete="off" aria-label="규격 검색"></div><p id="gyn" class="small muted"></p>'
                + f'<div class="gchip">{chips}</div><div class="gyc" id="gyc">{body}</div><div class="gnav"><button type="button" id="gpv">‹ 이전</button><span id="gpg"></span><button type="button" id="gnx">다음 ›</button></div>' + css + js)
    _gyb = _gy()
    # 자재별 규격표 전용 페이지(/gyugyeok/<slug>.html) — "합판 규격", "석고보드 사이즈" 검색용
    _GYP = {"합판": ("hapan", "합판 규격·사이즈 — 4×8 두께별 표(2.7~24T)", "합판은 4×8(1220×2440mm)과 3×6(900×1800mm) 두 크기가 기본이고, 두께는 2.7mm부터 24mm까지 있습니다. 같은 두께라도 베트남·인도네시아 산지와 등급(A급·내수)에 따라 품질과 값이 다릅니다.", [("4×8 합판은 몇 mm인가요?", "1220×2440mm(약 2.98㎡)입니다. 3×6은 900×1800mm(약 1.62㎡)입니다."), ("합판 두께는 어떻게 고르나요?", "뒤판·얇은 마감은 2.7~4.5mm, 바닥 덧방은 8.5~11.5mm, 선반·작업대·가구 몸통은 17.5mm 이상을 많이 씁니다. 물이 닿는 곳은 내수합판을 씁니다.")], [("/gagyeok/hapan-gagyeok.html", "합판 가격 가이드"), ("/jajae/hapan.html", "합판 자재 백과"), ("/cut.html", "합판 재단 미리보기")]),
             "MDF": ("mdf", "MDF 규격·두께표 — 4×8 원판 기준", "MDF는 나무 섬유를 압축해 만든 판재로 4×8(1220×2440mm) 원판이 기본입니다. 표면이 매끈해 도장·필름 마감 가구에 많이 쓰고, 물에는 약합니다.", [("MDF 크기는?", "4×8 원판(1220×2440mm) 기준이며 원하는 크기로 재단해 드립니다."), ("MDF와 합판 차이는?", "MDF는 표면이 고르고 가공이 쉽지만 물과 나사 힘에 약하고, 합판은 결이 있고 나사가 잘 잡히며 더 튼튼합니다.")], [("/gagyeok/mdf-gagyeok.html", "MDF 가격 가이드"), ("/jajae/mdf.html", "MDF 자재 백과"), ("/cut.html", "MDF 재단 미리보기")]),
             "집성판": ("jipseong", "집성판 규격·두께표 — 수종별 원판 크기", "집성판은 원목 조각을 이어 붙인 판재로, 수종(미송·레드파인·고무나무·아카시아 등)에 따라 원판 크기가 1200×2400 또는 1220×2440mm로 조금 다릅니다. 가구 상판·선반에 18T, 두꺼운 상판에 30T 안팎을 많이 씁니다.", [("집성판 두께는 몇 T를 많이 쓰나요?", "선반·수납장·가구 몸통은 18T, 식탁·작업대 상판은 24~30T 안팎을 많이 씁니다."), ("집성판 재단 되나요?", "네. 매장에서 치수대로 잘라 드립니다.")], [("/gagyeok/jipseong-gagyeok.html", "집성판 가격 가이드"), ("/bigyo/jipseong-types.html", "집성목 종류 비교"), ("/jajae/jipseong.html", "집성판 자재 백과")]),
             "석고보드": ("seokgo", "석고보드 규격·사이즈 — 3×6 일반·방수·방화 두께표", "석고보드는 3×6(900×1800mm)이 기본 크기이고, 두께는 9.5mm와 12.5mm를 가장 많이 씁니다. 물기 있는 곳은 방수, 내화가 필요한 곳은 방화 석고보드를 씁니다.", [("석고보드 사이즈는?", "3×6 = 900×1800mm(약 1.62㎡)가 기본입니다. 1평에 로스 포함 약 2.2장이 듭니다."), ("석고보드 9.5T와 12.5T 차이는?", "9.5T는 일반 벽·천장, 12.5T는 더 단단하고 방음·내화 보강에 유리합니다.")], [("/gagyeok/seokgo-gagyeok.html", "석고보드 가격 가이드"), ("/seokgo-pis.html", "석고보드 피스 길이"), ("/qna/seokgo-jareugi.html", "석고보드 자르기")]),
             "단열재": ("danyeol", "단열재 규격·두께표 — 아이소핑크·스티로폼·이보드", "아이소핑크·스티로폼은 900×1800mm, 이보드는 900×2400mm 판이 기준이고, 두께는 쓰는 곳(벽·바닥·천장)과 단열 기준에 따라 고릅니다.", [("아이소핑크 크기는?", "900×1800mm 판 기준이며 두께별로 있습니다."), ("단열재 두께는 어떻게 정하나요?", "벽·바닥·지붕마다 필요한 단열 성능이 다르니, 신축·증축은 도면의 단열 기준을 따르고 셀프 보강은 공간 높이와 마감 두께를 고려해 고릅니다.")], [("/gagyeok/danyeol-gagyeok.html", "단열재 가격 가이드"), ("/bigyo/insulation-types.html", "단열재 종류 비교"), ("/bigyo/isopink-vs-styrofoam.html", "아이소핑크 vs 스티로폼")]),
             "구조재": ("gujo", "구조재(구조목) 규격 — 2×4·2×6 실제 치수표", "구조재는 이름(2×4·2×6)과 실제 치수가 다릅니다. 2×4는 건조·대패 후 약 38×89mm, 2×6은 약 38×140mm이고, 길이는 ft(12ft ≈ 3.6m)로 부릅니다.", [("2×4 구조목 실제 치수는?", "약 38×89mm입니다. 12ft 길이는 약 3.6m입니다."), ("구조목은 어디에 쓰나요?", "목조주택 벽체·지붕, 데크 하부, 평상·작업대 틀처럼 하중을 받는 곳에 씁니다.")], [("/gagyeok/gakjae-gagyeok.html", "각재·구조재 가격"), ("/qna/gujomok-yeongyeol.html", "구조목 연결 방법"), ("/yongeo/tubai.html", "투바이(2×4) 뜻")]),
             "각재·다루끼": ("gakjae", "각재·다루끼 규격표 — 치·자 단위 읽는 법", "각재는 '치'(약 3cm)와 '자'(약 30.3cm) 단위로 많이 부릅니다. 다루끼 1.0×1.0은 약 30×30mm, 12자는 약 3.6m이고, 묶음(단) 단위로 팝니다.", [("다루끼 1.0×1.0은 몇 mm?", "1치×1치로 약 30×30mm입니다. 실제 치수는 제품마다 조금씩 작게 나올 수 있습니다."), ("각재 12자는 몇 m?", "약 3.6m입니다. 8자는 약 2.4m입니다.")], [("/qna/duchigak-darugi.html", "두치각·다루끼 규격 읽는 법"), ("/gagyeok/gakjae-gagyeok.html", "각재 가격 가이드"), ("/yongeo/darugi.html", "다루끼 뜻")]),
             "데크재": ("deck", "데크재 규격 — 합성데크·하드우드 단면·길이표", "데크재는 단면(두께×폭)과 길이로 고릅니다. 합성데크는 2400~3000mm, 방부목 데크재는 12자(약 3.6m)가 많고, 하드우드(이페·시우리 등)는 수종별로 규격이 다릅니다.", [("데크재는 몇 mm를 많이 쓰나요?", "방부목은 20×120·25×140mm, 합성데크는 20~25mm 두께에 폭 130~150mm를 많이 씁니다."), ("데크재 길이는?", "방부목 12자(약 3.6m), 합성데크 2.4~3m가 일반적입니다.")], [("/gagyeok/deck-gagyeok.html", "데크 자재 가격"), ("/bigyo/deck-finish.html", "데크 마감재 비교"), ("/deck-gyesan.html", "데크 계산기")])}
    _gyl = []
    for _lab, _blk in re.findall(r'<div class="gs" data-l="([^"]+)">(.*?</table></div></div>)', _gyb, re.S):
        if _lab not in _GYP: continue
        _sl, _tt, _ld, _fq, _ln = _GYP[_lab]
        _blk = _blk.replace("<h2>", "<h2 style=display:none>", 1)
        _gyl.append((_sl, _tt.split(" — ")[0]))
        page(f"gyugyeok/{_sl}.html", f"{_tt} | 영진목재", _ld[:150],
             f"""<section class="wrap sec"><p class="crumb"><a href="/gyugyeok.html">규격표</a> › {E(_lab)}</p><h1>{E(_tt.split(" — ")[0])}</h1><p class="lead">{E(_ld)}</p>
<div class="gs" style="border:1px solid #e6e0d4;border-radius:16px;padding:16px">{_blk}</div>
<p class="small muted">매장에서 실제로 파는 제품 기준입니다. 원하는 크기로 바로 재단해 드립니다.</p>
<h2>같이 보면 좋은 페이지</h2><div class="olk">{"".join(f'<a href="{h}">{E(n)}</a>' for h, n in _ln)}<a href="/gyugyeok.html">전체 규격표</a></div>
<h2>자주 묻는 질문</h2>{"".join(f'<details class="faq"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in _fq)}</section>{CTA}""", "",
             {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in _fq]})
    _gyb = '<p class="small">자재별로 따로 보기: ' + " · ".join(f'<a href="/gyugyeok/{a}.html">{E(b)}</a>' for a, b in _gyl) + ' · <a href="/bangbu-gyugyeok.html">방부목 규격</a></p>' + _gyb
    page("gyugyeok.html", "합판·MDF·석고보드·구조재 규격표 — 두께·크기 한눈에 | 영진목재", "합판 두께, MDF 규격, 석고보드 크기, 구조재 2x4 실제 치수, 방부목·각재·다루끼 규격을 한 표로 정리했습니다. 대전 영진목재 매장 취급 제품 기준.",
         f"""<section class="wrap sec"><h1>목재·합판 규격표</h1><p class="lead">매장에서 실제로 파는 제품 기준으로 크기와 두께를 정리했습니다. 원하는 크기는 매장에서 바로 재단해 드리고, 어떻게 잘리는지는 <a href="/cut.html">재단 미리보기</a>에서 그림으로 볼 수 있습니다.</p>
<div class="card"><h2>단위 읽는 법</h2><ul><li><b>4×8</b> = 4피트×8피트 = 1220×2440mm, <b>3×6</b> = 900×1800mm</li><li><b>T</b> = 두께(mm). 8.5T = 8.5mm</li><li><b>1치</b> ≈ 30mm, <b>1자</b> ≈ 303mm → <b>12자</b> ≈ 3.6m, 8자 ≈ 2.4m</li><li><b>12ft</b> ≈ 3.6m (구조재)</li><li><b>2×4</b>(투바이포)는 이름일 뿐, 실제 치수는 38×89mm</li></ul></div></section>
<section class="wrap sec">{_gyb}<p style="margin-top:14px">가격은 <a href="/price.html">기준가</a>, 필요한 양은 <a href="/calc.html">자재 계산기</a>, 자재별 용도는 <a href="/jajae/">자재 백과</a>에서 보세요.</p></section>{CTA}""", "",
         [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
           {"@type": "Question", "name": "합판 4×8은 몇 mm인가요?", "acceptedAnswer": {"@type": "Answer", "text": "4×8 합판은 1220×2440mm입니다. 3×6은 900×1800mm입니다."}},
           {"@type": "Question", "name": "구조재 2×4 실제 치수는?", "acceptedAnswer": {"@type": "Answer", "text": "2×4 구조재의 실제 단면은 38×89mm이고, 12ft 길이는 약 3.6m입니다."}},
           {"@type": "Question", "name": "다루끼 1치는 몇 mm인가요?", "acceptedAnswer": {"@type": "Answer", "text": "1치는 약 30mm입니다. 다루끼 1.0×1.0은 약 30×30mm, 12자는 약 3.6m입니다."}}]}])
    import nation as _nt0
    page("baesong.html", "전국 목재 배송 — 합판·구조재 재단해서 용달로 | 영진목재(대전)", "합판·MDF·구조재·방부목·데크재를 원하는 크기로 재단해 전국에 용달로 보내 드립니다. 경기·서울·충청·영남·호남·강원. 운임은 미리 견적. 대전 영진목재.",
         f"""<section class="wrap sec"><h1>전국 목재 배송 — 재단해서 용달로 보내 드립니다</h1><p class="lead">영진종합목재(월드건축자재) 쇼핑몰 회원의 절반 이상이 대전 밖에 계십니다. 합판·MDF·집성판·구조재·방부목·데크재·석고보드·몰딩·도어까지 원하는 크기로 재단해서 전국 현장으로 보내 드립니다.</p>
<div class="row"><a class="b r" href="mailto:{EMAIL}?subject=%EB%B0%B0%EC%86%A1%20%EA%B2%AC%EC%A0%81%20%EC%9A%94%EC%B2%AD&body=%ED%92%88%EB%AA%A9%C2%B7%EA%B7%9C%EA%B2%A9%C2%B7%EC%88%98%EB%9F%89%3A%0A%EB%B0%9B%EB%8A%94%20%EC%A3%BC%EC%86%8C%3A%0A%EB%B0%9B%EB%8A%94%20%EB%B6%84%20%EC%97%B0%EB%9D%BD%EC%B2%98%3A%0A%ED%9D%AC%EB%A7%9D%20%EB%82%A0%EC%A7%9C%3A%0A">메일로 배송 견적 요청</a><a class="b d" href="tel:{TEL.replace('-','')}">전화 {TEL}</a><a class="b o" href="/cut.html">재단 그림 만들기</a></div></section>
<section class="wrap sec g2"><div class="card"><h2>배송 방법</h2><ul><li><b>대전·세종·공주·계룡·논산·금산·옥천</b>: 직접 배송·현장 납품</li><li><b>그 밖의 전국</b>: 용달(화물차) 배송 — 운임 별도, 미리 견적</li><li>원하는 크기로 재단한 뒤 출고</li></ul></div>
<div class="card"><h2>주문 순서</h2><ol><li>품목·규격·수량·받는 주소를 전화나 메일로 알려 주세요.</li><li>사무실에서 자재값과 운임을 알려 드립니다.</li><li>입금 확인 후 재단·상차하고 출고합니다.</li></ol></div></section>
<section class="wrap sec gg"><h2 class="gt">지역별 배송 안내</h2><div class="qk">{"".join(f'<a href="/jeonguk/{a}.html">{b}</a>' for a, b, *_ in _nt0.REG)}</div></section><section class="wrap sec"><h2>지역별로 많이 보내는 자재</h2><ul>{"".join(f"<li><b>{E(a)}</b> — {E(b)}</li>" for a, b in _BR)}</ul><p>자재별 용도와 규격은 <a href="/jajae/">자재 백과</a>, 기준가는 <a href="/price.html">기준가</a>, 필요한 양은 <a href="/calc.html">자재 계산기</a>에서 미리 보실 수 있습니다.</p></section>
<section class="wrap sec"><h2>자주 묻는 질문</h2>{faqslide(_BF)}</section>{CTA}""", "", [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in _BF]}], BASE + "/assets/store/delivery.jpg")
    page("visit.html", "대전 목재소 영진목재 위치·영업시간 — 유성대로 44, 즉석 재단", f"월드건축자재(영진종합목재) {ADDR}. {HOURS}. 3000평 매장, 즉석 재단, 대전·세종 배송. {TEL}.",
         f"""<section class="wrap sec g2"><div>{embed(tour) if tour else ''}</div><div><h1>매장 오시는 길</h1>
<div class="tw"><table><tbody><tr><th>주소</th><td>{ADDR} 월드건축자재(영진목재)</td></tr><tr><th>영업</th><td>{HOURS}</td></tr><tr><th>전화</th><td><a href="tel:{TEL.replace('-','')}">{TEL}</a></td></tr>
<tr><th>재단</th><td>원하는 사이즈로 즉석 재단</td></tr><tr><th>배송</th><td>대전·세종·공주·계룡·논산·금산·옥천 배송 · 현장 납품 · 그 외 전국은 용달 배송(전화로 운임 견적 → 입금 확인 후 출고)</td></tr><tr><th>도매</th><td>사업자등록증·명함 확인 후 도매회원 승인</td></tr><tr><th>시공</th><td>월드아키텍쳐 · 대전·세종 · 전화 상담</td></tr></tbody></table></div>
<div class="row"><a class="b g" href="{NPLACE}" target="_blank" rel="noopener">네이버 지도로 길찾기</a><a class="b d" href="tel:{TEL.replace('-','')}">전화</a><a class="b o" href="mailto:{EMAIL}?subject=%EB%AC%B8%EC%9D%98">메일 문의</a></div>{RVBOX}</div></section>{"" if not os.path.exists(ROOT+"/data/store_photos.json") else '<section class="wrap sec"><h2>매장 사진</h2><div class="pg hrow">' + "".join(f'<a class="ph" href="/assets/store/{n}.jpg" target="_blank"><img loading="lazy" src="/assets/store/{n}.jpg" alt="{E(t)}"><small>{E(t)}</small></a>' for n, t in json.load(open(ROOT+"/data/store_photos.json", encoding="utf-8"))) + '</div><p class="hsh">옆으로 밀어서 더 보기 ›</p></section>'}""", "/visit.html", BIZ, BASE+"/assets/store/storefront.jpg")

    # 지역 시공 사례 (data/cases.json — 영상 설명에 지역이 확인된 실제 현장만)
    CASES = json.load(open(f"{ROOT}/data/cases.json", encoding="utf-8")) if os.path.exists(f"{ROOT}/data/cases.json") else []
    matname = {m["slug"]: m["name"] for m in MATS}
    def casecards(cs):
        return "".join(f'<a class="pc" href="/sigong/{c["slug"]}.html"><img loading="lazy" src="https://i.ytimg.com/vi/{c["videos"][0]}/mqdefault.jpg" alt=""><small>{E(c["place"] or "월드아키텍쳐 시공")}</small><b>{E(c["title"])}</b><span>{E(c["desc"][:70])}…</span></a>' for c in cs)
    def area_cases(slug):
        cs = [c for c in CASES if c["area"] == slug or (slug == "daejeon" and c["area"] in ("yuseong","seogu","daedeok","junggu-donggu"))]
        return f'<section class="wrap sec"><h2>이 지역 시공 사례</h2><div class="pl hs">{casecards(cs)}</div><p class="hsh">옆으로 밀어서 더 보기 ›</p></section>' if cs else ""
    for c in CASES:
        vs = [byid[i] for i in c["videos"] if i in byid]
        ml = " · ".join(f'<a href="/jajae/{m}.html">{matname[m]}</a>' for m in c["mats"] if m in matname)
        page(f"sigong/{c['slug']}.html", c["title"] + (" | 월드아키텍쳐·월드도어" if c.get("by") else " | 월드아키텍쳐"), c["desc"],
             f"""<section class="wrap sec"><p class="muted"><a href="/sigong.html">시공</a> › 시공 사례</p><h1>{E(c["title"])}</h1><p class="lead">{E(c["intro"])}</p>
<div class="tw"><table><tbody>{f'<tr><th>현장</th><td>{E(c["place"])}</td></tr>' if c["place"] else ""}<tr><th>시공</th><td>{E(c.get("by") or "월드아키텍쳐 (실내건축공사업 대전서구24-나-19)")}</td></tr>{f'<tr><th>관련 자재</th><td>{ml}</td></tr>' if ml else ''}</tbody></table></div></section>
<section class="wrap sec"><h2>시공 영상</h2>{vsplit(vs, "h3")}</section>
<section class="wrap sec"><h2>공사 내용</h2><ul>{"".join(f"<li>{E(w)}</li>" for w in c["works"])}</ul>
<p>비슷한 공사를 준비 중이시면 현장 실측 후 견적을 드립니다 — 전화 <a href="tel:{TEL.replace('-','')}">{TEL}</a>. 자재만 필요하시면 영진목재(월드건축자재) 매장에서 재단해 드립니다.</p></section>
<section class="wrap sec"><h2>다른 시공 사례</h2><div class="pl hs">{casecards([x for x in CASES if x is not c])}</div><p class="hsh">옆으로 밀어서 더 보기 ›</p><p>{f'<a href="/{c["area"]}.html">이 지역 자재·배송 안내 →</a>' if c["area"] else '<a href="/sigong.html">시공 안내 →</a>'}</p></section>{CTA}""", f"/sigong/{c['slug']}.html", BIZ, img=f"https://i.ytimg.com/vi/{c['videos'][0]}/hqdefault.jpg")

    # 지역 안내 (대전 목재 / 세종 목재)
    matlinks = "".join(f'<a class="mc" href="/jajae/{m["slug"]}.html"><b>{m["name"]}</b><small>{m["where"][0]}</small></a>' for m in MATS)
    AREAS = [("daejeon","대전 목재"),("sejong","세종 목재"),("yuseong","유성구"),("seogu","서구"),("daedeok","대덕구"),("junggu-donggu","중구·동구"),("sejong-sinsi","세종 신도심"),("sejong-eupmyeon","세종 조치원·읍면"),("gyeryong-nonsan","계룡·논산"),("gongju","공주"),("geumsan-okcheon","금산·옥천"),("cheongju","청주"),("cheonan-asan","천안·아산")]
    areanav = '<section class="wrap sec"><h2>지역별 목재·자재 안내</h2><p>' + " · ".join(f'<a href="/{a}.html">{n}</a>' for a, n in AREAS) + '</p></section>'
    for slug, area, t, lead, extra in [
        ("daejeon", "대전", "대전 목재 영진목재 — 3000평 목재소, 즉석 재단·대전 배송",
         "대전에서 목재를 찾으신다면 유성대로 44의 영진목재(영진종합목재·월드건축자재)로 오세요. 충청권 최대규모 3000평 매장에 합판·OSB·MDF·구조재·다루끼·방부목·합성데크·석고보드·몰딩·도어까지 한곳에 있고, 원하는 사이즈로 바로 재단해 드립니다.",
         "<li>대전 전 지역(유성·서구·중구·동구·대덕) 배송·현장 납품</li><li>DIY 소량 구매부터 인테리어·건축 현장 자재까지</li><li>대전 인테리어·데크·샷시 시공은 월드아키텍쳐(실내건축공사업 등록)</li>"),
        ("sejong", "세종", "세종 목재 — 영진목재 즉석 재단, 세종까지 배송 | 합판·구조재·방부목",
         "세종에서 목재가 필요하시면 대전 유성대로 44의 영진목재(영진종합목재·월드건축자재)를 이용하세요. 3000평 매장에서 합판·OSB·MDF·구조재·방부목·데크재·석고보드를 원하는 사이즈로 재단해 세종까지 배송·현장 납품합니다.",
         "<li>세종시 전 지역 배송·현장 납품 (수량·위치에 따라 전화 상담)</li><li>세종 신축·리모델링 현장 자재 일괄 납품</li><li>세종 인테리어·데크 시공은 월드아키텍쳐(실내건축공사업 등록)</li>"),
    ]:
        page(f"{slug}.html", t, lead[:150],
             f"""<section class="wrap sec"><h1>{area} 목재 · 건축자재 — 영진목재</h1><p class="lead">{lead}</p>
<div class="row"><a class="b g" href="/visit.html">매장 위치·영업시간</a><a class="b d" href="tel:{TEL.replace('-','')}">전화 {TEL}</a></div></section>
<section class="wrap sec g2"><div class="card"><h2>{area} 목재 구매 안내</h2><ul><li>매장: {ADDR} 영진목재(월드건축자재)</li><li>영업: {HOURS}</li><li>원하는 사이즈 즉석 재단</li>{extra}<li>사업자는 도매회원 가입(사업자등록증·명함 확인)</li></ul></div>
<div class="card"><h2>가격은 어떻게 보나요</h2><p>자주 찾는 목재·자재의 소매 기준가(부가세 별도)를 공개해 두었습니다. 규격·수량에 따라 달라지니 매장이나 전화로 확인해 주세요.</p><a href="/price.html">{area} 목재 기준가 보기 →</a><br><a href="/jaryo/">전체 자재 사진 보기 →</a></div></section>
<section class="wrap sec"><h2>{area}에서 많이 찾는 목재·자재</h2><div class="mg m2">{"".join(f'<a class="mc" href="/{slug}/{m["slug"]}.html"><b>{area} {m["name"]}</b><small>{m["where"][0]}</small></a>' for m in MATS)}</div></section>
<section class="wrap sec"><h2>자주 묻는 질문</h2>{faqslide([(area+"에서 목재 소량도 사나요?","네, 한 장·한 개부터 구매하실 수 있고 원하는 크기로 재단해 드립니다."),(area+" 현장으로 배송되나요?","네, 대전·세종·공주·계룡·논산·금산·옥천은 배송과 현장 납품을 하고, 그 외 전국 어디든 용달차로 보내 드립니다(사무실에서 운임 견적 → 입금 확인 후 출고). 수량과 위치를 알려 주시면 안내해 드립니다("+TEL+")."),("시공도 맡길 수 있나요?","월드아키텍쳐가 대전·세종 인테리어·데크·샷시 시공을 직접 합니다. 모든 현장은 유튜브에 공개합니다.")])}</section>{area_cases(slug)}{areanav}{CTA}""", f"/{slug}.html", BIZ)

    # 지역×자재 페이지 (대전 합판, 세종 방부목 …) — 구매·재단·배송 중심
    CASES_ = CASES
    RA = {"daejeon": ("대전", {"yuseong", "seogu", "junggu-donggu", "daedeok"}, "대전 전 지역(유성·서구·중구·동구·대덕)으로 배송·현장 납품합니다. 매장에서 직접 고르고 바로 재단해 가져가셔도 됩니다."),
          "sejong": ("세종", {"sejong-sinsi", "sejong-eupmyeon"}, "세종시 신도심·조치원·읍면 현장까지 배송·납품합니다(수량·위치에 따라 전화 상담). 대전 유성 매장에서 고르고 재단해 바로 가져가셔도 됩니다."),
          "gongju": ("공주", {"gongju"}, "공주 현장까지 배송·납품합니다(수량·위치에 따라 전화 상담). 대전 유성 매장에서 고르고 재단해 바로 가져가셔도 됩니다."),
          "gyeryong-nonsan": ("계룡·논산", {"gyeryong-nonsan"}, "계룡·논산 현장까지 배송·납품합니다(수량·위치에 따라 전화 상담). 대전 유성 매장에서 고르고 재단해 바로 가져가셔도 됩니다."),
          "geumsan-okcheon": ("금산·옥천", {"geumsan-okcheon"}, "금산·옥천 현장까지 배송·납품합니다(수량·위치에 따라 전화 상담). 대전 유성 매장에서 고르고 재단해 바로 가져가셔도 됩니다."),
          "cheongju": ("청주", {"cheongju"}, "청주는 원하는 크기로 재단한 뒤 용달로 보내 드립니다(사무실에서 운임 견적 → 입금 확인 후 출고). 대전 유성 매장에서 고르고 재단해 바로 가져가셔도 됩니다."),
          "cheonan-asan": ("천안·아산", {"cheonan-asan"}, "천안·아산은 원하는 크기로 재단한 뒤 용달로 보내 드립니다(사무실에서 운임 견적 → 입금 확인 후 출고). 대전 유성 매장에서 고르고 재단해 바로 가져가셔도 됩니다.")}
    for rs, (ra, rset, rdel) in RA.items():
        for m in MATS:
            nm = m["name"]
            vs = top(lambda v: m["tag"] in v["mats"], 10**6)
            ph = mat_photos(m["slug"])
            cs = [c for c in CASES_ if c.get("area") in rset and m["slug"] in c.get("mats", [])][:4]
            csec = (f'<section class="wrap sec"><h2>{ra} {nm} 시공 사례</h2><ul>' + "".join(f'<li><a href="/sigong/{c["slug"]}.html">{E(c["title"])}</a></li>' for c in cs) + '</ul></section>') if cs else ""
            gal = f'<section class="wrap sec"><h2>매장에 있는 {nm} <small class="muted">{len(ph)}종</small></h2><div class="pg hrow">{"".join(pcard(x) for x in ph[:10])}</div></section>' if ph else ""
            lf = [v for v in vs if v["type"] != "S"]
            vsec = f'<section class="wrap sec"><h2>{nm} 영상</h2>{vsplit(vs[:12], "h3")}</section>' if vs else ""
            fq = [(f"{ra}에서 {nm} 어디서 사나요?", f"대전 유성대로 44(유성구 원내동) 영진목재(영진종합목재·월드건축자재) 3000평 매장에서 사실 수 있습니다. {HOURS}. 전화 {TEL}."),
                  (f"{nm} 원하는 사이즈로 잘라 주나요?", "네, 매장에서 원하는 치수로 즉석 재단해 드립니다. 도면이나 치수 메모를 가져오시면 빠릅니다."),
                  (f"{ra} 현장으로 {nm} 배송되나요?", rdel),
                  (f"{nm} 한 장(한 개)도 살 수 있나요?", "네, 소량 DIY 구매도 됩니다. 사업자는 도매회원 가입(사업자등록증·명함 확인) 후 회원가로 구매하실 수 있습니다.")]
            body = f"""<section class="wrap sec"><p class="crumb"><a href="/{rs}.html">{ra} 목재</a> › {nm}</p>
<h1>{ra} {nm} — 파는 곳·기준가·재단·배송</h1><p class="lead">{ra}에서 {nm}{"이" if (ord(nm[-1])-0xAC00)%28 else "가"} 필요하시면 영진목재(월드건축자재) 매장에서 실물을 보고 고르세요. {E(m['lead'])} 원하는 사이즈로 바로 재단하고, {rdel}</p>
<div class="row"><a class="b g" href="/visit.html">매장 위치·영업시간</a><a class="b d" href="tel:{TEL.replace('-','')}">전화 {TEL}</a></div></section>{gal}
<section class="wrap sec g2"><div class="card"><h2>{nm} 소매 기준가</h2>{ptable(mat_prices(m))}<p class="small muted">부가세 별도 · 규격·수량에 따라 다릅니다.</p><a href="/price.html">전체 기준가 →</a></div>
<div class="card"><h2>{ra}에서 {nm} 쓰는 곳</h2><ul>{"".join(f"<li>{E(w)}</li>" for w in m["where"])}</ul><p><a href="/jajae/{m['slug']}.html">{nm} 용도·고르는 법 자세히 →</a> · <a href="/calc.html">필요한 양 계산</a>{f' · <a href="/cut.html#m={m["slug"]}">{nm} 재단 그림 보기</a>' if m["slug"] in {"hapan","osb","mdf","gujo","bangbu","hapdeck","jipseong","hinoki","gypsum","insul"} else ""}</p></div></section>
{csec}{vsec}<section class="wrap sec"><h2>{ra} {nm} 자주 묻는 질문</h2>{faqslide(fq)}</section>
<section class="wrap sec"><p class="small">{ra} 다른 자재: {" · ".join(f'<a href="/{rs}/{x["slug"]}.html">{x["name"]}</a>' for x in MATS if x is not m)}</p></section>{CTA}"""
            page(f"{rs}/{m['slug']}.html", f"{ra} {nm} 파는 곳 — 기준가·즉석 재단·배송 | 영진목재",
                 f"{ra} {nm} 구매는 대전 유성 영진목재(월드건축자재). 규격별 기준가, 원하는 사이즈 재단, {ra} 배송.", body, "",
                 {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]},
                 (ph[0]["img"] if ph else None))

    # 대전 구별 안내 — 동네마다 실제로 다른 정보만 (거리·소요시간 등 확인 안 된 숫자 금지)
    for slug, gu, t, lead, jobs, note in [
        ("yuseong", "유성구", "유성구 목재·건축자재 — 원내동 영진목재 3000평 매장 | 재단·배송",
         "영진목재(영진종합목재·월드건축자재)는 유성구 원내동(진잠) 유성대로 44에 있습니다. 도안·학하·노은·관평·신성 등 유성구 어디서든 합판·구조재·방부목·석고보드를 원하는 사이즈로 재단해 가져가시거나 현장으로 받으실 수 있습니다.",
         [("deck","전원주택·마당 데크"),("greenhouse","목조 온실·창고"),("furniture","원목가구·선반 DIY"),("tips","신축 아파트 인테리어 상식")],
         "유성구는 매장이 있는 구라 직접 오셔서 자재를 보고 고르기 좋습니다. 재단은 매장에서 바로 해 드립니다."),
        ("seogu", "서구", "서구 목재·건축자재 — 둔산·가수원·관저·도안 인테리어 자재 | 영진목재",
         "대전 서구(둔산·탄방·가수원·관저·도안·정림 등)에서 인테리어·리모델링 자재가 필요하시면 영진목재(월드건축자재)를 이용하세요. 시공 파트너 월드아키텍쳐 사무실도 서구 가수원로 42에 있어 서구 현장 상담이 빠릅니다.",
         [("tips","아파트 리모델링 순서"),("finish","도배·페인트·필름"),("exterior","샷시 교체"),("kitchen","싱크대·주방")],
         "아파트 현장은 엘리베이터·주차 조건에 맞춰 길이를 재단해 납품합니다(수량·위치는 전화 상담)."),
        ("daedeok", "대덕구", "대덕구 목재·건축자재 — 신탄진·대화동·오정동 현장 납품 | 영진목재",
         "대전 대덕구(신탄진·대화동·오정동·송촌·법동 등)의 공장·창고 보수, 주택 수리, 매장 인테리어에 필요한 합판·각재·구조재·석고보드를 영진목재(월드건축자재)에서 재단해 현장으로 납품합니다.",
         [("gujo","각재·구조재(창고·칸막이)"),("tips","상가·공장 인테리어 상식"),("exterior","외벽·지붕 보수"),("deck","마당 데크")],
         "공장·창고 현장은 사업자 도매회원 가입 시 회원가로 받으실 수 있습니다(사업자등록증·명함 확인)."),
        ("junggu-donggu", "중구·동구", "중구·동구 목재·건축자재 — 노후주택 수리·리모델링 자재 | 영진목재",
         "대전 중구(은행·대흥·문화·유천·태평 등)와 동구(가양·용전·판암·대동 등) 구도심의 노후주택·상가 수리에 필요한 문·문틀·몰딩·합판·석고보드를 영진목재(월드건축자재)에서 한곳에 구하세요.",
         [("door","방문·문틀 교체"),("exterior","샷시·외벽 보수"),("finish","도배·필름·페인트"),("tips","노후주택 리모델링 상식")],
         "오래된 집은 문틀·창틀 치수가 제각각이라 실측 치수를 알려 주시면 맞춰 재단해 드립니다."),
        ("sejong-sinsi", "세종 신도심", "세종 신도심 목재·인테리어 자재 — 보람·도담·새롬·나성·고운 | 영진목재",
         "세종 신도심(행복도시 — 보람·도담·새롬·다정·나성·종촌·고운·아름·반곡·해밀 등) 아파트·상가 인테리어에 필요한 합판·MDF·몰딩·문·석고보드·필름을 대전 유성 영진목재(월드건축자재)에서 재단해 세종 현장까지 배송합니다.",
         [("door","방문·중문 교체"),("film","인테리어 필름"),("molding","몰딩·걸레받이"),("tips","아파트 인테리어 상식")],
         "신도심 아파트·상가 현장 납품은 수량과 동·호수, 반입 조건을 알려 주시면 맞춰 드립니다(전화 상담)."),
        ("sejong-eupmyeon", "세종 조치원·읍면", "세종 조치원·읍면 목재 — 전원주택 데크·창고·방부목 | 영진목재",
         "세종 조치원읍과 연기·연동·연서·전의·전동·소정·부강·금남·장군면의 전원주택·농가 창고·마당 작업에 필요한 방부목·구조재·합판·데크재·침목을 대전 유성 영진목재(월드건축자재)에서 재단해 배송합니다.",
         [("deck","전원주택 데크·마당"),("bangbu","방부목·데크재"),("greenhouse","목조 온실·창고 짓기"),("chimmok","침목 조경")],
         "읍면 지역 배송은 위치와 수량에 따라 달라지니 전화로 먼저 확인해 주세요."),
        ("gyeryong-nonsan", "계룡·논산", "계룡·논산 목재·건축자재 — 대전 유성 영진목재 3000평 | 재단·배송",
         "계룡·논산(연산·두마·엄사·논산 시내 등)에서 목재·건축자재가 필요하시면 대전 유성구 원내동(진잠)의 영진목재(영진종합목재·월드건축자재)를 이용하세요. 합판·구조재·방부목·데크재·석고보드를 원하는 사이즈로 재단해 드립니다.",
         [("deck","전원주택 데크"),("bangbu","방부목·데크재"),("greenhouse","목조 온실·창고"),("gujo","구조재·각재")],
         "배송·현장 납품 지역입니다(배송 지역: 대전·세종·공주·계룡·논산·금산·옥천). 수량과 위치를 알려 주시면 안내해 드립니다."),
        ("gongju", "공주", "공주 목재·건축자재 — 대전 영진목재 3000평 | 재단·공주 배송",
         "공주(신관·금흥·반포·계룡면 등)에서 주택 수리·전원주택·한옥 보수에 필요한 목재를 찾으신다면 대전 유성 영진목재(월드건축자재) 3000평 매장에서 합판·구조재·방부목·히노끼·루바를 한 번에 고르고 재단하실 수 있습니다.",
         [("hinoki","히노끼·루바(내장)"),("bangbu","방부목·데크재"),("deck","마당 데크"),("tips","노후주택 리모델링 상식")],
         "배송·현장 납품 지역입니다(배송 지역: 대전·세종·공주·계룡·논산·금산·옥천). 수량과 위치를 알려 주시면 안내해 드립니다."),
        ("geumsan-okcheon", "금산·옥천", "금산·옥천 목재·건축자재 — 전원주택·창고 자재 배송 | 대전 영진목재",
         "금산·옥천의 전원주택·농가 창고·펜션 보수에 필요한 방부목·구조재·합판·침목·사이딩을 대전 유성 영진목재(월드건축자재)에서 재단해 드립니다.",
         [("deck","전원주택 데크"),("siding","사이딩(외장재)"),("chimmok","침목 조경"),("greenhouse","목조 창고 짓기")],
         "금산·옥천 모두 배송·현장 납품 지역입니다(배송 지역: 대전·세종·공주·계룡·논산·금산·옥천). 수량과 위치를 알려 주시면 안내해 드립니다. 매장으로 직접 오시면 원하는 사이즈로 바로 재단해 드립니다."),
        ("cheongju", "청주", "청주 목재·건축자재 — 대전 영진목재 3000평 목재소 | 합판·구조재·재단",
         "청주·오송·오창에서 대량 목재·건축자재가 필요한 인테리어·건축 현장이라면 충청권 최대규모(3000평) 목재상인 대전 영진목재(월드건축자재)를 비교해 보세요. 합판·OSB·MDF·구조재·석고보드·몰딩·도어를 한곳에서 구하고 원하는 사이즈로 재단합니다.",
         [("hapan","합판 종류·규격"),("osb","OSB합판"),("gypsum","석고보드"),("door","실내 도어·문틀")],
         "배송은 대전·세종·공주·계룡·논산·금산·옥천까지 하고, 청주·천안 등 그 외 전국 어디든 용달차로 보내 드립니다(사무실에서 운임 견적 → 입금 확인 후 출고). 매장으로 오시면 재단해 드리며, 사업자는 도매회원(사업자등록증·명함 확인)으로 회원가를 받으실 수 있습니다."),
        ("cheonan-asan", "천안·아산", "천안·아산 목재·건축자재 — 대전 영진목재 3000평 목재소 | 도매·재단",
         "천안·아산 지역 인테리어 업체·건축 현장에서 합판·구조재·석고보드·몰딩·데크재를 한 번에 구하신다면 충청권 최대규모(3000평) 대전 영진목재(월드건축자재)를 확인해 보세요. 자재 기준가와 사진을 홈페이지에서 미리 보고 전화로 수량을 상담하실 수 있습니다.",
         [("hapan","합판 종류·규격"),("gujo","구조재·각재"),("molding","몰딩·걸레받이"),("hapdeck","합성데크")],
         "배송은 대전·세종·공주·계룡·논산·금산·옥천까지 하고, 청주·천안 등 그 외 전국 어디든 용달차로 보내 드립니다(사무실에서 운임 견적 → 입금 확인 후 출고). 매장으로 오시면 재단해 드리며, 사업자는 도매회원(사업자등록증·명함 확인)으로 회원가를 받으실 수 있습니다."),
    ]:
        jl = "".join(f'<li><a href="/video/{c}.html">{n} 영상 보기</a></li>' if c not in [m["slug"] for m in MATS] else f'<li><a href="/jajae/{c}.html">{n} 자재 보기</a></li>' for c, n in jobs)
        page(f"{slug}.html", t, lead[:150],
             f"""<section class="wrap sec"><h1>{"대전 " if gu in ("유성구","서구","대덕구","중구·동구") else ""}{gu} 목재 · 건축자재 — 영진목재</h1><p class="lead">{lead}</p>
<div class="row"><a class="b g" href="/visit.html">매장 위치·영업시간</a><a class="b d" href="tel:{TEL.replace('-','')}">전화 {TEL}</a></div></section>
<section class="wrap sec g2"><div class="card"><h2>{gu}에서 자주 하는 작업</h2><ul>{jl}</ul></div>
<div class="card"><h2>{gu} 구매·배송 안내</h2><ul><li>매장: {ADDR} 영진목재(월드건축자재)</li><li>영업: {HOURS}</li><li>원하는 사이즈 즉석 재단</li><li>{note}</li><li><a href="/price.html">자재 기준가 보기</a> · <a href="/jaryo/">전체 자재 사진</a></li></ul></div></section>
<section class="wrap sec"><h2>많이 찾는 목재·자재</h2><div class="mg">{matlinks}</div></section>
<section class="wrap sec"><h2>{gu} 시공 문의</h2><p>인테리어·데크·샷시·문 교체 시공은 월드아키텍쳐(실내건축공사업 등록 대전서구24-나-19)가 직접 합니다. 현장 실측 후 견적을 드리며 모든 현장은 유튜브에 공개합니다. <a href="/sigong.html">시공 안내 보기 →</a></p></section>{area_cases(slug)}{areanav}{CTA}""", f"/{slug}.html", BIZ)

    # 자재 계산기 — 옆으로 넘기는 카드
    CALC_FAQ = [("데크 1평에 방부목 몇 장 들어가나요?","1평(약 3.3㎡)에 폭 120mm·길이 3.6m 데크재를 5mm 간격으로 깔면 약 7~8장, 로스 10%를 더하면 8~9장 정도입니다. 하지(장선) 각재는 별도입니다."),
                ("석고보드 1장은 몇 ㎡인가요?","3×6(900×1800mm)은 1.62㎡, 3×8(900×2400mm)은 2.16㎡입니다. 2겹(2P) 시공이면 장수가 2배입니다."),
                ("합판 1장은 몇 ㎡인가요?","4×8(1220×2440mm) 합판·OSB·MDF 1장은 약 2.98㎡입니다."),
                ("아이소핑크 1장은 몇 ㎡인가요?","900×1800mm 1장은 1.62㎡입니다. 두께는 필요한 단열 성능에 맞춰 고릅니다."),
                ("문짝 크기는 어떻게 재나요?","문틀 안쪽 가로를 위·중간·아래, 세로를 좌·중간·우에서 재고 가장 작은 값을 기준으로 합니다. 문틀째 바꿀 때는 벽 구멍 크기와 벽 두께를 잽니다."),
                ("3연동 중문은 어떻게 재나요?","설치할 자리의 벽~벽 가로와 바닥~천장 세로를 위·중간·아래 여러 번 재고 가장 작은 값을 기준으로 합니다. 정확한 크기는 현장 실측 후 확정합니다."),
                ("1평은 몇 제곱미터인가요?","1평은 약 3.3058㎡입니다.")]
    faqld = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in CALC_FAQ]}
    def fld(i, label, val, step="0.1"):
        return f'<label>{label}<input id="{i}" type="number" step="{step}" value="{val}" inputmode="decimal"></label>'
    def sel(i, label, opts):
        return f'<label>{label}<select id="{i}">' + "".join(f'<option value="{v}">{t}</option>' for v, t in opts) + '</select></label>'
    CALCS = [
     ("deck","데크", "데크 자재 (방부목·합성데크)",
      fld("dw","데크 가로(m)",4)+fld("dl","데크 세로(m)",3)+sel("dt","데크재",[("120,3600","방부목 120mm × 3.6m"),("140,3000","합성데크 140mm × 3.0m"),("95,3600","방부목 95mm × 3.6m")])+sel("dj","장선 간격",[("400","400mm (권장)"),("450","450mm"),("300","300mm")]),
      '<a href="/jajae/bangbu.html">방부목</a> · <a href="/jajae/hapdeck.html">합성데크</a> · <a href="/video/deck.html">데크 시공 영상</a>', "기초·멍에·기둥은 현장마다 달라 따로 상담해 주세요."),
     ("gyp","석고보드", "석고보드 장수",
      fld("gw","벽 길이 합계(m)",10)+fld("gh","벽 높이(m)",2.4)+fld("go","창·문 면적(㎡)",2)+sel("gs","규격",[("1.62","3×6 (900×1800)"),("2.16","3×8 (900×2400)")])+sel("gp","겹수",[("1","1겹(1P)"),("2","2겹(2P)")]),
      '<a href="/jajae/gypsum.html">석고보드 종류</a> · <a href="/jajae/gujo.html">목상(각재)</a>', ""),
     ("ply","합판", "합판·OSB·MDF 장수",
      fld("pa","시공 면적(㎡)",20)+sel("ps","판재 규격",[("2.9768","4×8 (1220×2440)"),("1.62","3×6 (900×1800)")]),
      '<a href="/jajae/hapan.html">합판</a> · <a href="/jajae/osb.html">OSB</a> · <a href="/jajae/mdf.html">MDF</a>', ""),
     ("mol","몰딩", "몰딩·걸레받이 길이",
      fld("mw","방 가로(m)",4)+fld("ml","방 세로(m)",3)+fld("mr","방 개수",1,"1")+fld("md","문 개수(걸레받이 제외)",1,"1")+sel("mk","계산",[("both","천장몰딩 + 걸레받이"),("ceil","천장몰딩만"),("base","걸레받이만")])+sel("mp","1개 길이",[("2.4","2.4m"),("2.7","2.7m")]),
      '<a href="/jajae/molding.html">몰딩·걸레받이</a> · <a href="/video/wall.html">몰딩 시공 영상</a>', "문 1개당 약 0.9m를 걸레받이에서 뺐습니다."),
     ("flo","바닥재", "데코타일·강마루 박스 수",
      fld("fa","바닥 면적(㎡)",20)+fld("fb","박스당 면적(㎡)",3.3)+sel("fl","로스",[("1.05","5% (직사각형 방)"),("1.1","10% (모서리 많음)"),("1.15","15% (사선·헤링본)")]),
      '<a href="/jajae/tile.html">데코타일</a> · <a href="/jajae/maru.html">마루·장판</a>', "박스당 면적은 제품마다 달라요. 제품 포장에 적힌 값을 넣으세요."),
     ("ins","단열재", "단열재(아이소핑크) 장수",
      fld("ia","단열 면적(㎡)",15)+sel("is","규격",[("1.62","900×1800"),("1.08","600×1800"),("2.16","900×2400")])+fld("il","겹수",1,"1"),
      '<a href="/jajae/insul.html">단열재</a> · <a href="/video/electric.html">단열·전기 영상</a>', "틈새를 채울 우레탄 폼도 함께 준비하세요."),
     ("pnt","페인트", "페인트 양",
      fld("ta","칠할 면적(㎡)",30)+fld("tc","칠 횟수",2,"1")+fld("tr","1L당 칠 면적(㎡, 1회)",8),
      '<a href="/jajae/stain.html">오일스테인·도료</a> · <a href="/video/finish.html">페인트 시공 영상</a>', "1L당 칠 면적은 제품·바탕면에 따라 다릅니다. 통에 적힌 값을 넣으세요."),
     ("door","문짝·문틀", "문짝·문틀 크기 계산",
      sel("om","교체 범위",[("leaf","문짝만 교체 (문틀 그대로)"),("frame","문틀째 교체 (벽 구멍 기준)")])+fld("ow","가로(mm)",780,"1")+fld("oh","세로(mm)",2050,"1")+fld("od","벽 두께(mm, 문틀째)",110,"1")+fld("of","문틀 두께(mm, 한쪽)",30,"1")+sel("ot","문 종류",[("10","방문 (하부 틈 10mm)"),("15","욕실문 (하부 틈 15mm)"),("5","기타 (하부 틈 5mm)")])+fld("os","문짝 좌우 틈 합계(mm)",6,"1")+fld("on","문 개수",1,"1"),
      '<a href="/jajae/door.html">실내 도어·문틀</a> · <a href="/video/door.html">문 교체 영상</a>', "문짝만 교체: 문틀 안쪽 크기를, 문틀째 교체: 벽 구멍(개구부) 크기를 넣으세요. 위·중간·아래 여러 번 재서 가장 작은 값을 씁니다. 틈·문틀 두께는 제품·현장에 따라 달라 참고용이며, 주문 전 매장에서 실측 치수를 확인해 드립니다."),
     ("jungmun","중문", "중문 (3연동·슬라이딩) 크기 계산",
      sel("jt","중문 종류",[("3","3연동 중문 (문짝 3장)"),("2","2짝 슬라이딩 중문"),("1","원슬라이딩 중문 (문짝 1장)")])+fld("jw","설치 자리 가로(mm)",1400,"1")+fld("jh","설치 자리 세로(mm)",2300,"1")+fld("jf","프레임 두께(mm, 한쪽)",40,"1")+fld("jo","문짝 겹침(mm, 한 곳)",40,"1"),
      '<a href="/jajae/door.html">실내 도어·중문</a> · <a href="/video/door.html">중문 시공 영상</a> · <a href="/sigong/door-daejeon-yuseong.html">중문 시공 사례</a>', "설치 자리(벽~벽, 바닥~천장)를 위·중간·아래 여러 번 재서 가장 작은 값을 넣으세요. 프레임 두께·겹침은 제품마다 달라 참고용이며, 주문 전 현장 실측으로 확정합니다."),
     ("py","평↔㎡", "평 ↔ ㎡ 변환", fld("yp","평",1)+fld("ym","㎡",3.31), "", ""),
    ]
    chips = "".join(f'<button class="chip" data-i="{i}">{t}</button>' for i, (k, t, *_ ) in enumerate(CALCS))
    def _clinks(links):
        # 관련 자재·영상 링크를 사진 없는 작은 카드로(자재=책 아이콘, 영상=재생 아이콘)
        if not links: return ""
        out = ""
        for a in links.split(" · "):
            m = re.match(r'<a href="([^"]+)">([^<]+)</a>', a.strip())
            if not m: continue
            vid = m.group(1).startswith("/video/")
            ic = '<svg viewBox="0 0 24 24"><path d="M9 7.5v9l7.5-4.5z" fill="currentColor"/></svg>' if vid else '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 5.5A1.5 1.5 0 0 1 6.5 4H18v14H6.5A1.5 1.5 0 0 0 5 19.5z"/><path d="M5 19.5A1.5 1.5 0 0 0 6.5 21H18"/></svg>'
            out += f'<a class="clc{" v" if vid else ""}" href="{m.group(1)}"><i>{ic}</i><span><small>{"시공 영상" if vid else "자재 알아보기"}</small><b>{m.group(2).replace(" 시공 영상","").replace(" 영상","")}</b></span><u>›</u></a>'
        return f'<div class="clk">{out}</div>'
    slides = "".join(f'<div class="cslide" id="{k}"><div class="card"><h2>{h}</h2><div class="cg">{inner}</div>' + ('' if k == "py" else f'<div class="cr" id="{k}r"></div>') + (f'<p class="cnote">{note}</p>' if note else "") + _clinks(links) + '</div></div>' for k, t, h, inner, links, note in CALCS)
    # 재단 미리보기 — 매장 취급 원판·각재 규격(가격 없음)
    def _cutdata():
        rows = list(csv.DictReader(open(ROOT + "/data/prices.csv", encoding="utf-8")))
        def ln(n):
            m = re.search(r"(\d+)\s*ft", n, re.I)
            if m: return int(m.group(1)) * 300
            m = re.search(r"(\d+(?:\.\d+)?)\s*자", n)
            if m: return round(float(m.group(1)) * 300)
            m = re.findall(r"\*\s*(\d{4})\b", n)
            return int(m[-1]) if m else 0
        def nm(n): return re.sub(r"\s+", " ", re.sub(r"^[^-]+-\s*", "", n)).strip()
        G = [("합판", ["합판"], 0), ("MDF", ["엠디"], 0), ("집성판", ["집성판"], 0), ("석고보드", ["석고"], 0), ("단열재", ["단열"], 0),
             ("구조재", ["구조"], 1), ("방부목", ["방부"], 1), ("각재·다루끼", ["목재", "각재"], 1), ("데크", ["데크", "합성"], 1)]
        cats = []
        for label, cs, lin in G:
            items = []
            for r in sorted([r for r in rows if r["cat"] in cs], key=lambda r: -int(r["qty"] or 0)):
                n = r["name"]
                if lin:
                    L = ln(n)
                    if L >= 600 and not re.search(r"클립|스타터|브라켓|캡|지주", n): items.append([nm(n), L, n])
                else:
                    m = re.search(r"(\d{3,4})\s*\*\s*(\d{3,4})\s*\*\s*\d", n)
                    if m: w, h = int(m.group(1)), int(m.group(2))
                    else:
                        m = re.search(r"([34])\s*\*\s*([68])", n)
                        if not m: continue
                        w, h = {"4*8": (1220, 2440), "3*6": (900, 1800)}[m.group(1) + "*" + m.group(2)]
                    items.append([nm(n), w, h, n])
            if items: cats.append({"n": label, "lin": lin, "items": items})
        J = {x["n"]: x["i"] for x in json.load(open(ROOT + "/../assets/jaryo.json", encoding="utf-8"))} if os.path.exists(ROOT + "/../assets/jaryo.json") else {}
        PIC = [(r"자작", "자작합판"), (r"OSB", "O.S.B합판"), (r"코아", "코아합판"), (r"태고|코팅", "코팅(태고)합판"), (r"^합판-미송", "미송합판(국산)"), (r"요꼬", "요꼬합판(오징어합판)"),
               (r"라치", "라찌(낙엽송)엠보합판"), (r"^합판.*내수", "방수(내수)합판(국산)"), (r"^합판.*\(베\)", "베트남합판(보양합판)"), (r"^합판", "일반합판(말레이시아/인도네시아/MLH)"), (r"^엠디", "M.D.F"),
               (r"집성판-고무", "고무나무집성판(AAA등급)"), (r"집성판-아카시아", "아카시아집성판"), (r"집성판-미송", "미송집성판"), (r"집성판-멀바우", "멀바우집성판"), (r"집성판-참죽", "참죽집성판"),
               (r"집성판-애쉬", "애쉬집성판"), (r"집성판-히노끼", "일본산 히노끼 집성판(무절)"), (r"집성판-레드파인", "레드파인집성판"), (r"집성판-삼목", "삼나무 솔리드 집성판"),
               (r"^석고", "석고보드"), (r"핑크", "아이소핑크"), (r"스티로폴", "스티로폼"), (r"^구조\(마감재\)", "구조마감재(JAS)"), (r"^구조", "2급 구조재"),
               (r"^방부.*(데크)", "방부데크"), (r"^방부", "방부각재"), (r"다루끼\(소송\)", "인테리어각재(소송)"), (r"라왕\(집성\)", "라왕각재(한치각)"), (r"라왕\(속대\)", "라왕속대"),
               (r"라왕\(후지\)", "라왕후지"), (r"육송", "골조용다루끼(육송)"), (r"면대\(합판\)", "합판 쫄대"), (r"스프러스", "집성/솔리드각재(스프러스)"), (r"^합성", "합성데크/기둥/난간재")]
        for c in cats:
            for it in c["items"]:
                raw = it.pop()  # 원래 이름(맨 끝) — 사진 매칭용
                for rx, jn in PIC:
                    if re.search(rx, raw) and jn in J: it.append([J[jn], jn]); break
        _pm = {}
        for r in rows:
            k = nm(r["name"])
            if r["price"].strip().isdigit() and k not in _pm: _pm[k] = int(r["price"])
        for c in cats:
            c["pr"] = [_pm.get(it[0], 0) for it in c["items"]]
            c["bu"] = [(lambda m: int(m.group(1)) if m and 1 < int(m.group(1)) <= 50 else 1)(re.search(r"\((\d+)(?:EA)?\)\s*$", it[0])) for it in c["items"]]
        cats += [{"n": "판재 직접입력", "lin": 0, "custom": 1}, {"n": "각재 직접입력", "lin": 1, "custom": 1}]
        def fx(cn, rx=None):
            for ci, c in enumerate(cats):
                if c["n"] == cn:
                    if not rx: return [ci, 0]
                    for ii, it in enumerate(c.get("items", [])):
                        if re.search(rx, it[0]): return [ci, ii]
                    return [ci, 0]
        M = {"hapan": fx("합판"), "osb": fx("합판", "OSB"), "mdf": fx("MDF"), "gujo": fx("구조재"), "bangbu": fx("방부목"), "hapdeck": fx("데크", "합성"),
             "jipseong": fx("집성판"), "hinoki": fx("집성판", "히노끼"), "gypsum": fx("석고보드"), "insul": fx("단열재")}
        return {"cats": cats, "m": {k: v for k, v in M.items() if v}}
    _cd = _cutdata()
    def cutlink(cn, rx, parts, label="재단 그림 보기"):
        for ci, c in enumerate(_cd["cats"]):
            if c["n"] == cn:
                ii = next((i for i, it in enumerate(c.get("items", [])) if re.search(rx, it[0])), 0) if rx else 0
                return f'/cut.html#c={ci}&p={ii}&g=0&s=' + "_".join(f"{a}x{b}x{q}" for a, b, q in parts)
        return "/cut.html"
    CUTSLUG = _cd["m"]
    _CF = [("재단비는 얼마인가요?", "1컷(한 번 자르기)당 두께별로 12T 이하 1,000원, 15·18T 1,500원, 20T 이하 2,000원, 24T 이하 2,500원, 30T 이하 3,000원입니다(부가세 별도). 30T가 넘는 두께(2×4·2×6·4×4 등)는 전화로 문의해 주세요. 위 계산기에서 크기를 넣으면 컷 수와 재단비가 바로 계산됩니다."), ("합판·MDF 원하는 사이즈로 잘라 주나요?", "네. 대전 유성대로 44 매장에서 합판, MDF, 집성판, OSB, 석고보드, 단열재와 구조재·각재·방부목을 원하는 크기로 즉석 재단해 드립니다. 한 장, 한 개 소량도 됩니다."),
           ("4×8 합판 한 장에서 몇 조각 나오나요?", "4×8 합판 원판은 1220×2440mm입니다. 이 페이지에 자를 크기와 개수를 넣으면 톱날 두께 3mm를 빼고 몇 장이 필요한지, 어떻게 잘리는지 그림으로 바로 보여드립니다."),
           ("재단할 때 톱날 두께는 얼마나 빠지나요?", "한 번 자를 때마다 약 3mm가 빠집니다. 이 계산기는 3mm를 빼고 배치하므로 실제 재단과 거의 같게 나옵니다."),
           ("나뭇결 방향을 맞춰서 자를 수 있나요?", "네. 집성판이나 무늬목처럼 결이 중요한 자재는 '나뭇결 방향 유지'를 체크하면 조각을 돌리지 않고 배치합니다."),
           ("재단 그림을 매장에 어떻게 보내나요?", "'링크 복사'를 눌러 카톡이나 문자로 보내시거나, 화면을 매장에 보여주시면 그대로 잘라 드립니다. 인쇄도 됩니다.")]
    def _szcard(c):
        sz = sorted({(i[1], i[2]) if not c["lin"] else (i[1], 0) for i in c["items"]}, key=lambda x: (x[0] * (x[1] or 1)))
        if c["lin"]:
            mx = max(w for w, _ in sz)
            pic = '<svg viewBox="0 0 100 40">' + "".join(f'<rect x="4" y="{6 + k * 9}" width="{max(8, 92 * w / mx):.0f}" height="5" rx="1.5" fill="#d9ad74" stroke="#8f5f2c" stroke-width=".6"/>' for k, (w, _) in enumerate(sz[:4])) + '</svg>'
            chips = "".join(f"<span>{w:,}mm</span>" for w, _ in sz)
        else:
            L0 = max(max(w, h) for w, h in sz); S0 = max(min(w, h) for w, h in sz)
            sc = min(84 / L0, 30 / S0)
            pic = '<svg viewBox="0 0 100 40">' + "".join(f'<rect x="{8 + k * 3}" y="{4 + k * 2}" width="{max(w, h) * sc:.1f}" height="{min(w, h) * sc:.1f}" rx="1.5" fill="{["#ecd6ad", "#e3c38f", "#d9ad74"][k % 3]}" stroke="#8f5f2c" stroke-width=".6"/>' for k, (w, h) in enumerate(sorted(sz, key=lambda x: -x[0] * x[1])[:3])) + '</svg>'
            chips = "".join(f"<span>{w}×{h}</span>" for w, h in sz)
        return f'<div class="szc"><div class="szp">{pic}</div><b>{E(c["n"])}</b><small>{"길이" if c["lin"] else "원판 크기(mm)"}</small><div class="szs">{chips}</div></div>'
    _sz = "".join(_szcard(c) for c in _cd["cats"] if c.get("items"))
    _STEP = [("자재 고르기", "합판·MDF·집성판·석고보드·단열재·구조재·방부목·각재·데크 중에서"), ("크기 넣기", "가로×세로×개수, 각재는 길이×개수"), ("그림·금액 확인", "원판 장수·재단 그림·컷 수·재단비가 바로 나와요"), ("매장에 보여주기", "링크를 보내거나 화면을 보여주면 그대로 잘라 드려요")]
    _seo = (f'<section class="wrap sec cuts2"><h2>매장 원판·각재 규격 <small>재단 기준</small></h2><div class="szg">{_sz}</div>'
            '<h2>재단 미리보기 사용법</h2><div class="stp">' + "".join(f'<div><i>{k + 1}</i><b>{t}</b><span>{d}</span></div>' for k, (t, d) in enumerate(_STEP)) + '</div>'
            '<h2>자주 묻는 질문</h2>' + faqslide(_CF) +
            '<div class="cul"><a href="/jaedan-bi.html"><b>재단비</b><span>두께별 1컷 단가</span></a><a href="/gyugyeok.html"><b>규격표</b><span>합판 두께·2×4 실제 치수</span></a><a href="/mandeul/"><b>DIY 만들기</b><span>평상·책장·데크 재단 목록</span></a><a href="/calc.html"><b>자재 계산기</b><span>몇 장 필요한지</span></a><a href="/visit.html"><b>매장 안내</b><span>길찾기·영업시간</span></a></div></section>'
            '<style>.cuts2 h2 small{font-size:13px;color:#8a8378;font-weight:700;margin-left:4px}.szg{display:grid;grid-template-columns:1fr 1fr;gap:10px}@media(min-width:760px){.szg{grid-template-columns:repeat(3,1fr)}}.szc{background:#fff;border:1px solid #ece6dc;border-radius:16px;padding:12px;display:flex;flex-direction:column;gap:3px}.szp{background:#f7f4ee;border-radius:10px;padding:6px;margin-bottom:6px}.szp svg{display:block;width:100%;height:44px}.szc b{font-size:16px}.szc small{font-size:11.5px;color:#8a8378;font-weight:700}.szs{display:flex;flex-wrap:wrap;gap:4px;margin-top:4px}.szs{gap:3px!important}.szs span{font-size:11px;font-weight:800;background:#f3ece4;color:#6b4a26;border-radius:6px;padding:2px 5px;letter-spacing:-.3px}'
            '.stp{display:flex;gap:10px;overflow-x:auto;scroll-snap-type:x mandatory;padding:2px 2px 10px;scrollbar-width:none}.stp::-webkit-scrollbar{display:none}.stp div{flex:0 0 72%;max-width:260px;scroll-snap-align:start;background:#fff;border:1px solid #ece6dc;border-radius:16px;padding:14px;display:flex;flex-direction:column;gap:4px}.stp i{font-style:normal;width:30px;height:30px;border-radius:50%;background:#c41a1f;color:#fff;font-weight:900;display:grid;place-items:center;margin-bottom:4px}.stp b{font-size:16px}.stp span{font-size:13px;color:#6b645a;line-height:1.5}'
            '.cul{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:18px}.cul a{display:flex;flex-direction:column;gap:2px;background:#fff;border:1px solid #ece6dc;border-radius:14px;padding:12px;color:#1D1B18!important;text-decoration:none!important}.cul a:first-child{grid-column:1/-1;background:#1D1B18;color:#fff!important;border-color:#1D1B18}.cul b{font-size:15px}.cul span{font-size:12.5px;opacity:.7}</style>')
    _ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in _CF]},
           {"@context": "https://schema.org", "@type": "WebApplication", "name": "재단 미리보기 — 영진종합목재", "applicationCategory": "UtilityApplication", "operatingSystem": "All", "url": BASE + "/cut.html", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"}, "provider": {"@type": "HardwareStore", "name": "영진종합목재(월드건축자재)", "telephone": TEL, "address": ADDR}}]
    # 만들기별 자재 안내 — 자재 목록·재단 크기·재단 미리보기 연결(가격 없음)
    def ffd(L, parts):
        bins = []
        for l in sorted([a for a, _, q in parts for _ in range(q)], reverse=True):
            for b in bins:
                if b[0] + (3 if b[1] else 0) + l <= L: b[0] += (3 if b[1] else 0) + l; b[1].append(l); break
            else: bins.append([l, [l]])
        return len(bins)
    MK = [
     ("pyeongsang", "원목 평상", "평상 만들기 자재 — 1800×1200 방부목 평상 재단 목록", "마당·옥상·텃밭에 두는 1800×1200, 높이 약 40cm 평상입니다. 방부목 데크재로 상판을 깔고, 2×4로 틀, 4×4로 다리를 세웁니다.",
      [("상판", "방부목", r"25\*140", [(1790, 0, 8)], "데크재 25×140 · 1790mm 8장 (사이 간격 약 10mm)"),
       ("틀·장선", "방부목", r"2\* 4", [(1790, 0, 2), (1124, 0, 4)], "2×4(38×89) · 긴 쪽 1790mm 2개, 짧은 쪽·가운데 1124mm 4개"),
       ("다리", "방부목", r"4\*4", [(375, 0, 6)], "4×4(89×89) · 375mm 6개")],
      ["틀(1790×2, 1124×4)을 직사각형으로 짜고 모서리를 피스로 고정합니다.", "다리 6개를 네 모서리와 긴 쪽 가운데에 붙입니다.", "상판 8장을 10mm 간격으로 올리고 장선마다 피스 2개씩 박습니다.", "모서리를 사포로 다듬고 오일스테인을 바르면 오래 갑니다."],
      ["방부목 데크재", "방부목 2×4", "방부목 4×4", "데크 피스(스테인리스)", "오일스테인"]),
     ("chaekjang", "책장·수납장", "책장 만들기 자재 — 집성판 18T 책장 재단 목록", "폭 800, 높이 1800, 깊이 300mm 5칸 책장입니다. 집성판 18T 한 장으로 옆판과 선반이 모두 나오고, 뒷판은 MDF로 막습니다.",
      [("옆판·선반", "집성판", r"미송.*18T", [(300, 1800, 2), (764, 300, 6)], "집성판 18T · 옆판 300×1800 2장, 선반(위·아래 포함) 764×300 6장"),
       ("뒷판", "MDF", r"6mm", [(800, 1800, 1)], "MDF 6mm · 800×1800 1장")],
      ["옆판 2장 사이에 위·아래 판을 먼저 끼워 상자 모양을 만듭니다.", "가운데 선반 4장을 같은 간격(약 340mm)으로 고정합니다.", "뒷판 MDF를 타카나 짧은 피스로 붙이면 흔들림이 잡힙니다.", "키 큰 책장은 벽에 고정 철물로 잡아 주세요."],
      ["집성판 18T", "MDF 6mm", "목공 피스·목공본드", "넘어짐 방지 철물"]),
     ("tutbat", "텃밭상자", "텃밭상자 만들기 자재 — 1200×600 방부목 텃밭상자", "베란다·마당용 1200×600, 높이 약 280mm 텃밭상자입니다. 방부목 2×6을 두 단으로 쌓고 모서리는 2×2 기둥으로 잡습니다.",
      [("벽판", "방부목", r"2\* 6", [(1200, 0, 4), (524, 0, 4)], "2×6(38×140) · 긴 쪽 1200mm 4개, 짧은 쪽 524mm 4개"),
       ("모서리 기둥", "방부목", r"2\* 2", [(280, 0, 4)], "2×2(38×38) · 280mm 4개")],
      ["짧은 판 2장을 모서리 기둥 2개에 붙여 양쪽 끝판을 만듭니다.", "긴 판을 끝판에 붙여 상자를 완성합니다(두 단).", "바닥에 부직포나 방초시트를 깔면 흙이 덜 빠집니다."],
      ["방부목 2×6", "방부목 2×2", "데크 피스(스테인리스)", "방초시트"]),
     ("deck", "작은 데크", "소형 데크 만들기 자재 — 2400×1800 방부목 데크", "마당이나 현관 앞 2400×1800 낮은 데크입니다. 2×4 장선을 400mm 간격으로 놓고 데크재를 1800 길이로 깝니다.",
      [("데크재", "방부목", r"25\*140", [(1790, 0, 17)], "데크재 25×140 · 1790mm 17장 (간격 약 5mm)"),
       ("장선·테두리", "방부목", r"2\* 4", [(1790, 0, 7), (2400, 0, 2)], "2×4(38×89) · 장선 1790mm 7개, 테두리 2400mm 2개")],
      ["바닥을 평평하게 고르고 주춧돌이나 받침을 놓습니다.", "테두리 2400 2개 사이에 장선 1790 7개를 400mm 간격으로 고정합니다.", "데크재를 5mm 간격으로 깔고 장선마다 피스 2개씩 박습니다.", "끝선을 맞춰 한 번에 잘라내면 깔끔합니다."],
      ["방부목 데크재", "방부목 2×4", "주춧돌·받침", "데크 피스(스테인리스)", "오일스테인"]),
     ("gabyeok", "가벽", "가벽 만들기 자재 — 2400×2400 목공 가벽(석고보드 마감)", "방을 나누는 폭 2400, 높이 2400 실내 가벽입니다. 구조재 2×4로 틀을 짜고 양면에 석고보드를 붙입니다.",
      [("틀(스터드)", "구조재", r"Ⅱ 2\* 4", [(2400, 0, 2), (2324, 0, 7)], "구조재 2×4 · 위·아래 깔도리 2400mm 2개, 세로 기둥 2324mm 7개(약 400mm 간격)")],
      ["바닥·천장에 깔도리 2400을 고정합니다.", "세로 기둥 7개를 약 400mm 간격으로 세웁니다.", "석고보드 900×1800을 양면에 붙입니다(한쪽 약 4장, 남는 부분은 재단).", "이음매에 퍼티를 바르고 도배·페인트로 마감합니다."],
      ["구조재 2×4", "석고보드 9.5T(900×1800) 양면 약 8장", "석고 피스", "퍼티·조인트 테이프"]),
     ("byeokseonban", "벽선반", "벽선반 만들기 자재 — 집성판 3단 벽선반 재단 목록", "거실·주방·현관 벽에 다는 폭 800, 깊이 200mm 3단 선반입니다. 집성판 18T를 잘라 선반 브라켓으로 겁니다. 남는 집성판으로 같은 선반을 더 만들 수 있습니다.",
      [("선반판", "집성판", r"미송.*18T", [(800, 200, 3)], "집성판 18T · 800×200 3장")],
      ["선반 높이를 정하고 수평자로 벽에 선을 긋습니다.", "브라켓을 선반 1장당 2개, 벽 속 기둥이나 앵커에 고정합니다(석고벽은 석고 앵커 필수).", "선반판을 올리고 아래에서 짧은 피스로 브라켓에 고정합니다.", "오일이나 바니시를 바르면 물·얼룩에 강해집니다."],
      ["집성판 18T", "선반 브라켓 6개", "앵커·피스", "목재 오일 또는 바니시"]),
     ("ultari", "목재 울타리", "목재 울타리(펜스) 만들기 자재 — 방부목 3.6m 울타리", "마당·텃밭 경계에 세우는 길이 3.6m, 높이 약 1.2m 방부목 울타리입니다. 4×4 기둥 3개를 1.8m 간격으로 세우고 2×4 가로대에 데크재 살을 붙입니다.",
      [("기둥", "방부목", r"4\*4", [(1500, 0, 3)], "4×4(89×89) · 1500mm 3개 (땅에 약 300mm 묻힘)"),
       ("가로대", "방부목", r"2\* 4", [(3600, 0, 2)], "2×4(38×89) · 3600mm 2개 (위·아래)"),
       ("세로 살", "방부목", r"20\*120", [(1190, 0, 21)], "데크재 20×120 · 1190mm 21개 (살 간격 약 50mm)")],
      ["기둥 자리를 1.8m 간격으로 표시하고 300mm 이상 파서 기둥을 세운 뒤 수직을 맞춥니다(시멘트로 굳히면 튼튼합니다).", "위·아래 가로대를 기둥에 피스로 고정합니다.", "세로 살을 간격 맞춰 위·아래 가로대에 피스로 박습니다.", "윗면을 수평으로 맞추고 오일스테인을 바릅니다."],
      ["방부목 4×4", "방부목 2×4", "방부목 데크재 20×120", "데크 피스(스테인리스)", "레미탈 또는 기초 블록", "오일스테인"]),
     ("teibeul", "원목 테이블", "원목 테이블 상판 만들기 자재 — 집성판 1200×600 테이블", "작업대·식탁·책상으로 쓰는 1200×600 원목 테이블입니다. 두꺼운 집성판을 상판으로 쓰고 아래에 선반을 하나 두며, 다리는 철제 테이블 다리를 씁니다.",
      [("상판·하부 선반", "집성판", r"고무.*30T", [(1200, 600, 1), (1100, 400, 1)], "고무나무 집성판 30T · 상판 1200×600 1장, 하부 선반 1100×400 1장")],
      ["상판 모서리를 사포(120→240방)로 둥글게 다듬습니다.", "철제 다리를 상판 아래 네 모서리에 피스로 고정합니다.", "하부 선반을 다리 사이 받침에 올려 고정합니다.", "오일이나 우레탄 바니시로 2~3회 칠하면 물자국이 덜 남습니다."],
      ["고무나무 집성판 30T", "철제 테이블 다리 4개(또는 프레임)", "목공 피스", "사포", "목재 오일 또는 바니시"]),

     ("sinbaljang", "신발장", "신발장 만들기 자재 — 집성판 18T 5단 신발장 재단 목록", "현관에 두는 폭 900, 높이 1000, 깊이 350mm 5단 신발장입니다. 미송 집성판 18T 한 장으로 옆판·천판·선반이 나오고, 뒷판은 MDF 6mm로 막습니다.",
      [("옆판·천판·지판", "집성판", r"미송.*18T", [(350, 1000, 2), (864, 350, 2)], "집성판 18T · 옆판 350×1000 2장, 천판·지판 864×350 2장"),
       ("선반", "집성판", r"미송.*18T", [(864, 330, 3)], "집성판 18T · 선반 864×330 3장 (뒷판 자리만큼 깊이를 줄임)"),
       ("뒷판", "MDF", r"6mm", [(900, 1000, 1)], "MDF 6mm · 900×1000 1장")],
      ["옆판 2장 사이에 천판·지판을 끼워 상자를 만듭니다(목공본드+피스).", "선반 3장을 약 190mm 간격으로 고정합니다. 부츠 칸은 한 칸을 넓게 두세요.", "뒷판 MDF를 타카나 짧은 피스로 붙여 직각을 잡습니다.", "바닥에 가구 발이나 실리콘 패드를 붙이면 습기에 강해집니다."],
      ["미송 집성판 18T", "MDF 6mm", "목공 피스·목공본드", "가구 발 또는 패드"]),
     ("benchi", "원목 벤치", "야외 벤치 만들기 자재 — 방부목 1500 벤치 재단 목록", "마당·베란다·캠핑장에 두는 길이 1500, 높이 약 450mm 2~3인용 벤치입니다. 데크재 3장을 상판으로 깔고 4×4 다리와 2×4 틀로 받칩니다.",
      [("상판", "방부목", r"25\*140", [(1500, 0, 3)], "데크재 25×140 · 1500mm 3장 (간격 약 10mm)"),
       ("틀", "방부목", r"2\* 4", [(1500, 0, 2), (364, 0, 3)], "2×4(38×89) · 긴 쪽 1500mm 2개, 짧은 쪽·가운데 364mm 3개"),
       ("다리", "방부목", r"4\*4", [(425, 0, 4)], "4×4(89×89) · 425mm 4개")],
      ["2×4로 1500×440 직사각형 틀을 짜고 가운데에 보강 1개를 넣습니다.", "네 모서리 안쪽에 4×4 다리를 피스 4개씩으로 고정합니다.", "상판 3장을 10mm 간격으로 올리고 틀마다 피스 2개씩 박습니다.", "앉는 모서리를 사포로 둥글게 다듬고 오일스테인을 바릅니다."],
      ["방부목 데크재 25×140", "방부목 2×4", "방부목 4×4", "데크 피스(스테인리스)", "오일스테인"]),
     ("chimdae", "침대 프레임", "평상형 침대 프레임 만들기 자재 — 퀸 1500×2000 원목 침대", "퀸 매트리스(1500×2000)를 올리는 낮은 평상형 침대입니다. 구조재 2×6 테두리에 2×4 장선을 걸고, 위에 두꺼운 합판을 깔아 매트리스를 받칩니다.",
      [("테두리", "구조재", r"마감재\) 2\* 6", [(2040, 0, 2), (1500, 0, 2)], "구조재 2×6(38×140) · 긴 쪽 2040mm 2개, 짧은 쪽 1500mm 2개"),
       ("장선·다리", "구조재", r"Ⅱ 2\* 4", [(1500, 0, 5), (200, 0, 6)], "구조재 2×4 · 가로 장선 1500mm 5개(약 400mm 간격), 다리 200mm 6개"),
       ("받침판", "합판", r"17.5mm\(인\)", [(1000, 1500, 2)], "합판 17.5T · 1000×1500 2장 (이어서 2000×1500)")],
      ["2×6 테두리를 피스로 짜서 2040×1576 직사각형을 만듭니다.", "장선 1500mm 5개를 테두리 안쪽에 약 400mm 간격으로 고정합니다.", "다리 6개를 네 모서리와 긴 쪽 가운데 안쪽에 붙입니다.", "합판 2장을 장선 위에 깔고 피스로 고정한 뒤, 모서리를 사포로 다듬습니다."],
      ["구조재 2×6", "구조재 2×4", "합판 17.5T", "목공 피스", "사포·목재 오일"]),
     ("jakeopdae", "작업대", "목공 작업대 만들기 자재 — 1800×600 구조재 작업대", "창고·공방·베란다에 두는 1800×600, 높이 850mm 튼튼한 작업대입니다. 구조재 2×4로 다리와 위·아래 틀을 짜고, 두꺼운 합판을 상판과 아래 선반으로 씁니다.",
      [("다리·틀", "구조재", r"Ⅱ 2\* 4", [(812, 0, 4), (1800, 0, 4), (524, 0, 4)], "구조재 2×4 · 다리 812mm 4개, 긴 틀 1800mm 4개(위·아래), 짧은 틀 524mm 4개"),
       ("상판·선반", "합판", r"17.5mm\(인\)", [(1800, 600, 1), (1724, 524, 1)], "합판 17.5T · 상판 1800×600 1장, 아래 선반 1724×524 1장 (한 장에서 나옴)")],
      ["긴 틀 1800과 짧은 틀 524로 위·아래 직사각형 틀 2개를 만듭니다.", "다리 4개를 두 틀 사이 모서리에 끼워 피스로 고정합니다(아래 틀은 바닥에서 약 150mm 위).", "아래 선반 합판을 아래 틀 위에 올려 고정합니다.", "상판을 올리고 피스로 고정합니다. 바이스를 달 자리는 미리 비워 두세요."],
      ["구조재 2×4", "합판 17.5T", "목공 피스(65mm·40mm)", "가구 발 또는 바퀴"]),
     ("monitor", "모니터 받침대", "모니터 받침대 만들기 자재 — 집성판 600×250 원목 받침대", "책상 위에 올리는 폭 600, 깊이 250, 높이 약 100mm 모니터 받침대입니다. 아래 공간에 키보드를 밀어 넣을 수 있습니다. 집성판 남는 조각으로도 충분합니다.",
      [("상판·다리판", "집성판", r"아카시아.*18T", [(600, 250, 1), (250, 82, 2)], "아카시아 집성판 18T · 상판 600×250 1장, 다리판 250×82 2장")],
      ["다리판 2장을 상판 양 끝 아래에 맞춥니다.", "목공본드를 바르고 위에서 피스로 고정합니다(피스 자리는 미리 구멍).", "모서리를 사포로 둥글게 다듬고 오일을 2회 바릅니다.", "바닥에 미끄럼 방지 패드를 붙입니다."],
      ["아카시아 집성판 18T", "목공본드·피스", "사포·목재 오일", "미끄럼 방지 패드"]),
     ("beranda", "베란다 선반", "베란다 수납 선반 만들기 자재 — 1200×450 4단 원목 선반", "베란다·창고·다용도실에 두는 폭 1200, 깊이 450, 높이 1800mm 4단 선반입니다. 구조재 2×4 기둥과 가로대에 합판 선반을 얹어 무거운 짐도 버팁니다.",
      [("기둥·가로대", "구조재", r"Ⅱ 2\* 4", [(1800, 0, 4), (1200, 0, 8), (374, 0, 8)], "구조재 2×4 · 기둥 1800mm 4개, 앞뒤 가로대 1200mm 8개, 옆 가로대 374mm 8개"),
       ("선반판", "합판", r"17.5mm\(인\)", [(1200, 450, 4)], "합판 17.5T · 1200×450 4장 (한 장에서 나옴)")],
      ["기둥 2개에 옆 가로대 374mm 4개를 높이별로 붙여 사다리 모양 옆틀 2개를 만듭니다.", "두 옆틀을 앞뒤 가로대 1200mm로 연결합니다.", "각 단에 합판 선반을 올리고 피스로 고정합니다.", "벽에 ㄱ자 철물로 고정하면 넘어지지 않습니다."],
      ["구조재 2×4", "합판 17.5T", "목공 피스", "ㄱ자 철물(벽 고정)"]),
     ("dannyeolbyeok", "벽 단열", "벽 단열 자재 — 3m 벽 아이소핑크+석고보드 셀프 단열", "외풍이 들어오는 3000×2400 벽 한 면을 단열하는 자재입니다. 다루끼로 틀을 대고 사이에 아이소핑크를 끼운 뒤 석고보드로 덮고 도배합니다.",
      [("다루끼 틀", "각재·다루끼", r"1.0\*1.0\*12자", [(2400, 0, 9), (3000, 0, 2)], "다루끼 1.0×1.0(약 30×30) · 세로 2400mm 9개(약 375mm 간격), 가로 3000mm 2개")],
      ["벽에 위·아래 가로 다루끼를 콘크리트못이나 앵커로 고정합니다.", "세로 다루끼 9개를 약 375mm 간격으로 세웁니다.", "다루끼 사이에 아이소핑크 30T를 잘라 끼우고 틈은 우레탄폼으로 메웁니다.", "석고보드 9.5T를 다루끼에 피스로 박고, 이음매 퍼티 후 도배합니다."],
      ["다루끼 1.0×1.0 12자", "아이소핑크 30T(900×1800) 약 5장", "석고보드 9.5T(900×1800) 약 5장", "우레탄폼", "석고 피스·콘크리트못"]),
     ("saideu", "사이드테이블", "사이드테이블 만들기 자재 — 집성판 상자형 협탁", "소파·침대 옆에 두는 폭 450, 깊이 400, 높이 500mm 상자형 사이드테이블(협탁)입니다. 아래 칸에 책이나 리모컨을 둘 수 있습니다.",
      [("상판·옆판·선반", "집성판", r"아카시아.*18T", [(450, 400, 1), (400, 482, 2), (414, 400, 1)], "아카시아 집성판 18T · 상판 450×400 1장, 옆판 400×482 2장, 아래 선반 414×400 1장")],
      ["옆판 2장 사이에 아래 선반을 바닥에서 약 80mm 띄워 고정합니다.", "상판을 옆판 위에 올려 목공본드와 피스로 고정합니다.", "피스 머리는 목심으로 막고 사포질합니다.", "오일이나 바니시를 2~3회 바릅니다."],
      ["아카시아 집성판 18T", "목공본드·피스·목심", "사포", "목재 오일 또는 바니시"]),
     ("hyeongwanbench", "현관 수납벤치", "현관 수납 벤치 만들기 자재 — 집성판 900 신발 신는 의자", "현관에서 앉아 신발을 신는 폭 900, 깊이 350, 높이 450mm 벤치입니다. 아래 칸에 슬리퍼나 우산을 넣습니다.",
      [("상판·옆판·바닥", "집성판", r"미송.*18T", [(900, 350, 1), (350, 432, 2), (864, 350, 1)], "미송 집성판 18T · 상판 900×350 1장, 옆판 350×432 2장, 바닥판 864×350 1장"),
       ("뒷판", "MDF", r"6mm", [(900, 450, 1)], "MDF 6mm · 900×450 1장")],
      ["옆판 2장 사이에 바닥판을 끼워 ㄷ자를 만듭니다.", "상판을 올려 목공본드와 피스로 고정합니다(앉는 곳이라 피스를 넉넉히).", "뒷판 MDF를 붙여 흔들림을 잡습니다.", "앉는 모서리를 둥글게 다듬고 바니시로 마감합니다."],
      ["미송 집성판 18T", "MDF 6mm", "목공 피스·목공본드", "바니시"]),
     ("gaejip", "강아지집", "강아지집 만들기 자재 — 소형견 합판 개집 재단 목록", "소·중형견용 바닥 800×600, 높이 600mm 상자형 개집입니다. 내수합판 12mm로 벽과 지붕을 만들고, 방부목 2×2로 바닥을 띄웁니다. 실외에 둘 때는 방수 페인트를 꼭 칠하세요.",
      [("벽·지붕·바닥", "합판", r"4\*8 @12mm\(내수/A급\)", [(800, 600, 2), (576, 600, 2), (900, 700, 1), (776, 576, 1)], "내수합판 12mm · 앞·뒤 벽 800×600 2장, 옆벽 576×600 2장, 지붕 900×700 1장, 바닥 776×576 1장"),
       ("받침 다리", "방부목", r"2\* 2", [(100, 0, 4)], "방부목 2×2(38×38) · 100mm 4개")],
      ["앞벽에 출입구(폭 약 300, 높이 약 400mm)를 직소로 따냅니다.", "앞·뒤 벽 사이에 옆벽을 끼워 상자를 만들고, 안쪽에 바닥판을 넣습니다.", "바닥 아래 네 모서리에 2×2 받침을 붙여 땅에서 띄웁니다.", "지붕판을 사방 50mm쯤 남게 올려 고정하고, 겉면에 방수 페인트를 2회 칠합니다."],
      ["내수합판 12mm", "방부목 2×2", "목공 피스", "방수 페인트(외부용)", "직소"]),

     ("hwabundae", "계단식 화분대", "화분대 만들기 자재 — 방부목 3단 계단식 화분 선반", "베란다·마당에 두는 폭 900, 깊이 750, 높이 900mm 3단 계단식 화분대입니다. 뒤로 갈수록 높아져 화분마다 햇빛이 고르게 듭니다.",
      [("옆틀·선반 받침", "방부목", r"2\* 4", [(900, 0, 2), (600, 0, 2), (300, 0, 2), (750, 0, 2), (250, 0, 6)], "2×4(38×89) · 뒤 기둥 900mm 2개, 가운데 600mm 2개, 앞 300mm 2개, 바닥 가로대 750mm 2개, 선반 받침 250mm 6개"),
       ("선반", "방부목", r"25\*140", [(900, 0, 6)], "데크재 25×140 · 900mm 6장 (단마다 2장)")],
      ["바닥 가로대 750mm 위에 앞·가운데·뒤 기둥을 250mm 간격으로 세워 옆틀 2개를 만듭니다.", "기둥 윗부분에 선반 받침 250mm를 붙입니다.", "옆틀 2개를 세우고 선반 데크재를 단마다 2장씩 올려 고정합니다.", "흙·물이 닿으니 오일스테인을 넉넉히 바릅니다."],
      ["방부목 2×4", "방부목 데크재 25×140", "데크 피스(스테인리스)", "오일스테인"]),
     ("aichaeksang", "아이 책상", "아이 책상 만들기 자재 — 집성판 1000×550 어린이 책상", "초등학생용 폭 1000, 깊이 550, 높이 600mm 원목 책상입니다. 집성판 18T로 상판과 옆판을 만들고 뒤쪽 보강판으로 흔들림을 잡습니다.",
      [("상판·옆판·보강판", "집성판", r"아카시아.*18T", [(1000, 550, 1), (550, 582, 2), (964, 200, 1)], "아카시아 집성판 18T · 상판 1000×550 1장, 옆판 550×582 2장, 뒤 보강판 964×200 1장")],
      ["옆판 2장 사이 위쪽 뒤편에 보강판을 끼워 ㄷ자를 만듭니다.", "상판을 올려 목공본드와 피스로 고정합니다.", "아이가 다치지 않게 모든 모서리를 사포로 둥글게 갈아냅니다.", "무독성 수성 바니시나 오일로 마감합니다."],
      ["아카시아 집성판 18T", "목공본드·피스·목심", "사포", "수성 바니시(무독성)"]),
     ("geosiljang", "거실장", "TV 거실장 만들기 자재 — 집성판 1500 낮은 거실장", "TV 아래 두는 폭 1500, 깊이 400, 높이 450mm 낮은 거실장입니다. 가운데 칸막이로 두 칸을 나누고 셋톱박스·책을 넣습니다.",
      [("상판·지판", "집성판", r"미송.*18T", [(1500, 400, 2)], "미송 집성판 18T · 상판·지판 1500×400 2장"),
       ("옆판·칸막이", "집성판", r"미송.*18T", [(400, 414, 3)], "미송 집성판 18T · 옆판·칸막이 400×414 3장"),
       ("뒷판", "MDF", r"6mm", [(1500, 450, 1)], "MDF 6mm · 1500×450 1장 (전선 구멍은 뚫어서 사용)")],
      ["지판 위에 옆판 2장과 가운데 칸막이를 세워 고정합니다.", "상판을 덮고 목공본드와 피스로 고정합니다.", "뒷판 MDF에 전선 구멍(지름 약 50mm)을 뚫고 붙입니다.", "바닥에 가구 발을 달고 오일로 마감합니다."],
      ["미송 집성판 18T", "MDF 6mm", "목공 피스·목공본드", "가구 발", "목재 오일"]),
     ("seutul", "원목 스툴", "원목 스툴 만들기 자재 — 집성판 300각 의자", "주방·작업대·현관에서 쓰는 300×300, 높이 450mm 원목 스툴입니다. 집성판 남는 조각으로 여러 개 만들 수 있습니다.",
      [("상판·다리판·가로대", "집성판", r"아카시아.*18T", [(300, 300, 1), (300, 432, 2), (264, 80, 1)], "아카시아 집성판 18T · 상판 300×300 1장, 다리판 300×432 2장, 가로대 264×80 1장")],
      ["다리판 2장 아래쪽 가운데를 반달 모양으로 따내면 흔들림이 줄어듭니다.", "다리판 사이 아래쪽에 가로대를 끼워 고정합니다.", "상판을 올려 목공본드와 피스로 고정합니다.", "모서리를 둥글게 다듬고 오일을 바릅니다."],
      ["아카시아 집성판 18T", "목공본드·피스", "직소(곡선 따기)", "목재 오일"]),
     ("nopeuntutbat", "다리 달린 텃밭상자", "높은 텃밭상자 만들기 자재 — 허리 높이 방부목 텃밭", "허리를 굽히지 않고 쓰는 1200×600, 높이 약 800mm 다리 달린 텃밭상자입니다. 베란다·옥상·마당 어디든 놓을 수 있습니다.",
      [("상자 벽", "방부목", r"2\* 6", [(1200, 0, 2), (524, 0, 2)], "2×6(38×140) · 긴 쪽 1200mm 2개, 짧은 쪽 524mm 2개"),
       ("다리", "방부목", r"4\*4", [(800, 0, 4)], "4×4(89×89) · 800mm 4개"),
       ("바닥판", "방부목", r"25\*140", [(524, 0, 8)], "데크재 25×140 · 524mm 8장 (물 빠지게 약 5mm 간격)")],
      ["2×6으로 1200×600 상자 틀을 짭니다.", "네 모서리 안쪽에 4×4 다리를 붙이고, 다리 윗면을 상자 위와 맞춥니다.", "상자 아래쪽 안에 받침을 대고 바닥 데크재 8장을 5mm 간격으로 깝니다.", "안쪽에 부직포를 깔고 흙을 채웁니다."],
      ["방부목 2×6", "방부목 4×4", "방부목 데크재 25×140", "데크 피스(스테인리스)", "부직포"]),
     ("haenggeo", "원목 옷걸이 행거", "원목 행거 만들기 자재 — 각재로 만드는 1000 옷걸이", "방·드레스룸에 두는 폭 1000, 높이 1600mm 원목 옷걸이 행거입니다. 스프러스 45각 집성 각재 두 개로 만들 수 있습니다.",
      [("기둥·받침·봉", "각재·다루끼", r"45각", [(1600, 0, 2), (500, 0, 2), (1000, 0, 1)], "스프러스 집성 45각 · 기둥 1600mm 2개, 바닥 받침 500mm 2개, 가로봉 1000mm 1개")],
      ["바닥 받침 500mm 가운데에 기둥을 세워 ㅗ자 다리 2개를 만듭니다(L자 철물로 보강).", "두 기둥 윗부분 사이에 가로봉 1000mm를 피스로 고정합니다.", "흔들리면 받침 사이에 각재 하나를 더 대 줍니다.", "옷걸이가 잘 미끄러지게 가로봉을 사포질하고 오일을 바릅니다."],
      ["스프러스 집성 45각 8자", "L자 철물", "목공 피스", "목재 오일"]),
     ("yaoeteibeul", "야외 테이블", "야외 원목 테이블 만들기 자재 — 방부목 1500×740 테이블", "마당·캠핑·옥상에 두는 1500×740, 높이 720mm 방부목 테이블입니다. 데크재 5장으로 상판을 깔고 4×4 다리로 받칩니다.",
      [("상판", "방부목", r"25\*140", [(1500, 0, 5)], "데크재 25×140 · 1500mm 5장 (간격 약 10mm)"),
       ("틀", "방부목", r"2\* 4", [(1500, 0, 2), (664, 0, 3)], "2×4(38×89) · 긴 쪽 1500mm 2개, 짧은 쪽·가운데 664mm 3개"),
       ("다리", "방부목", r"4\*4", [(695, 0, 4)], "4×4(89×89) · 695mm 4개")],
      ["2×4로 1500×740 틀을 짜고 가운데 보강을 넣습니다.", "네 모서리 안쪽에 다리를 피스 4개씩으로 고정합니다.", "상판 데크재 5장을 10mm 간격으로 올려 고정합니다.", "다리 사이에 대각선 보강을 대면 흔들림이 없어집니다. 오일스테인으로 마감합니다."],
      ["방부목 데크재 25×140", "방부목 2×4", "방부목 4×4", "데크 피스(스테인리스)", "오일스테인"]),
     ("jangjak", "장작 보관대", "장작 보관대 만들기 자재 — 방부목 1200 장작 거치대", "화목난로·캠핑용 장작을 쌓는 폭 1200, 높이 1000mm 보관대입니다. 바닥에서 띄워 장작이 잘 마르게 합니다.",
      [("레일·기둥", "방부목", r"2\* 4", [(1200, 0, 4), (1000, 0, 4), (400, 0, 4)], "2×4(38×89) · 위·아래 레일 1200mm 4개, 기둥 1000mm 4개, 양 끝 가로대 400mm 4개")],
      ["아래 레일 2개를 400mm 간격으로 놓고 양 끝을 가로대로 연결합니다.", "네 모서리에 기둥을 세웁니다.", "기둥 위를 위 레일과 가로대로 연결해 상자 틀을 만듭니다.", "블록 위에 올려 땅에서 띄우면 오래 갑니다. 지붕이 필요하면 골함석을 얹으세요."],
      ["방부목 2×4", "데크 피스(스테인리스)", "받침 블록", "골함석(선택)"]),
     ("gongguborad", "공구 정리 벽판", "공구 정리 벽판 만들기 자재 — OSB 합판 벽걸이 공구판", "창고·차고 벽에 거는 1200×1200 공구 정리판입니다. OSB 합판에 고리·못을 박아 공구를 걸고, 뒤에 다루끼를 대서 벽과 띄웁니다.",
      [("벽판", "합판", r"OSB 4\*8 @ 11.1", [(1200, 1220, 1)], "OSB 11.1T · 1200×1220 1장"),
       ("뒷받침", "각재·다루끼", r"1.0\*1.0\*12자", [(1200, 0, 3)], "다루끼 1.0×1.0 · 1200mm 3개 (위·가운데·아래)")],
      ["벽에 다루끼 3개를 수평으로 앵커 고정합니다.", "OSB 벽판을 다루끼에 피스로 박습니다.", "공구를 대 보고 자리를 정한 뒤 고리·못·선반을 답니다.", "공구 윤곽을 매직으로 그려 두면 제자리 찾기가 쉽습니다."],
      ["OSB 11.1T", "다루끼 1.0×1.0", "앵커·피스", "공구 고리·S고리"]),
     ("cube", "수납 큐브", "수납 큐브 만들기 자재 — MDF 350 큐브 정리함 4개", "책·장난감·바구니를 넣는 350×350×350mm 수납 큐브 4개입니다. 쌓거나 옆으로 붙여 원하는 모양의 수납장을 만듭니다.",
      [("상하판·옆판", "MDF", r"^MDF 4\*8 @15mm", [(350, 350, 8), (320, 350, 8)], "MDF 15mm · 위·아래판 350×350 8장, 옆판 320×350 8장 (큐브 4개분)"),
       ("뒷판", "MDF", r"6mm", [(350, 350, 4)], "MDF 6mm · 350×350 4장")],
      ["위·아래판 사이에 옆판 2장을 끼워 상자를 만듭니다(목공본드+피스).", "뒷판을 타카나 짧은 피스로 붙입니다.", "큐브끼리는 짧은 피스나 클램프 볼트로 연결합니다.", "MDF는 물에 약하니 수성 페인트로 칠해 마감합니다."],
      ["MDF 15mm", "MDF 6mm", "목공 피스·목공본드", "수성 페인트"]),
     ("sadariseonban", "원목 사다리 선반", "사다리 선반 만들기 자재 — 45각 각재 800×300×1500 4단 선반", "거실·베란다·주방에 두는 폭 800, 깊이 300, 높이 1500mm 4단 사다리 선반입니다. 45각 각재로 사다리 두 개를 만들고, 그 가로대 위에 집성판 선반을 얹습니다.",
      [("사다리 기둥·가로대", "각재·다루끼", r"45각", [(1500, 0, 4), (710, 0, 10)], "스프러스 집성 45각 · 기둥 1500mm 4개, 가로대 710mm 10개 (앞·뒤 사다리 각 5개)"),
       ("선반", "집성판", r"미송.*18T", [(710, 300, 4)], "집성판 18T · 710×300 4장")],
      ["45각 기둥 2개 사이에 가로대 5개를 같은 높이(아래부터 약 360mm 간격)로 박아 앞쪽 사다리를 만듭니다.", "같은 방법으로 뒤쪽 사다리를 하나 더 만듭니다.", "두 사다리를 300mm 간격으로 세우고, 아래 4단 가로대 위에 선반을 올려 앞·뒤 가로대에 피스로 고정합니다.", "벽에 넘어짐 방지 철물로 잡고 사포질 후 오일로 마감합니다."],
      ["스프러스 집성 45각 8자", "집성판 18T", "목공 피스·목공본드", "넘어짐 방지 철물", "목재 오일"]),
     ("aillaendeu", "아일랜드 작업대", "아일랜드 작업대 만들기 자재 — 집성판 1200×600 주방 아일랜드 수납 작업대", "주방 가운데나 벽 앞에 두는 폭 1200, 깊이 600, 높이 900mm 아일랜드 작업대입니다. 집성판 18T로 몸통과 선반 2단을 만들고, 상판은 두꺼운 고무나무 30T를 얹습니다.",
      [("옆판·선반·걸레받이", "집성판", r"미송.*18T", [(600, 870, 2), (1164, 594, 2), (1164, 60, 2)], "집성판 18T · 옆판 600×870 2장, 선반 1164×594 2장, 앞·뒤 걸레받이 1164×60 2장"),
       ("뒷판", "MDF", r"6mm", [(1164, 870, 1)], "MDF 6mm · 1164×870 1장"),
       ("상판", "집성판", r"고무.*30T", [(1200, 600, 1)], "고무나무 집성판 30T · 1200×600 1장")],
      ["옆판 2장 아래쪽 앞·뒤에 걸레받이(1164×60)를 끼워 몸통 틀을 만듭니다.", "아래 선반을 걸레받이 위에, 가운데 선반을 높이 약 450mm에 끼워 고정합니다.", "뒷판 MDF 6mm를 옆판 사이에 붙여 흔들림을 잡습니다.", "고무나무 30T 상판을 올려 아래에서 피스로 고정하고, 물에 강한 오일로 마감합니다."],
      ["집성판 18T", "고무나무 집성판 30T", "MDF 6mm", "목공 피스·목공본드", "목재 오일(식품 안전 등급 권장)"]),
     ("balpan", "2단 원목 발판", "2단 발판 만들기 자재 — 집성판 400×350×400 아이·주방 스텝 발판", "세면대·주방·높은 수납장 앞에 두는 폭 400, 깊이 350, 높이 400mm 2단 발판입니다. 집성판 18T 한 가지로 만들어 가볍고 튼튼합니다.",
      [("옆판·디딤판·보강판", "집성판", r"미송.*18T", [(350, 400, 2), (364, 350, 1), (364, 175, 1), (364, 100, 1)], "집성판 18T · 옆판 350×400 2장, 아래 디딤판 364×350 1장, 위 디딤판 364×175 1장, 뒤 보강판 364×100 1장")],
      ["옆판 2장 안쪽 높이 182mm에 아래 디딤판을 끼워 목공본드+피스로 고정합니다.", "옆판 맨 위 뒤쪽 절반에 위 디딤판(364×175)을 고정합니다.", "뒤쪽 아래에 보강판을 붙여 좌우 흔들림을 잡습니다.", "모서리를 사포로 둥글게 갈고, 디딤면에 미끄럼 방지 패드를 붙입니다."],
      ["집성판 18T", "목공 피스·목공본드", "사포", "미끄럼 방지 패드", "목재 오일"]),
     ("bunrisugeo", "분리수거함", "분리수거함 만들기 자재 — 집성판 1050×400×700 3칸 분리수거 정리함", "베란다·주방에 두는 폭 1050, 깊이 400, 높이 700mm 3칸 분리수거함입니다. 칸마다 종량제·재활용 봉투나 바구니를 넣어 씁니다.",
      [("바닥·옆판·칸막이", "집성판", r"미송.*18T", [(1050, 400, 1), (400, 682, 4)], "집성판 18T · 바닥 1050×400 1장, 옆판·칸막이 400×682 4장"),
       ("뒷판", "MDF", r"6mm", [(1050, 682, 1)], "MDF 6mm · 1050×682 1장")],
      ["바닥판 위에 바깥 옆판 2장을 세워 고정합니다.", "칸막이 2장을 약 330mm 간격으로 세워 3칸을 나눕니다.", "뒷판 MDF 6mm를 붙여 틀이 비틀어지지 않게 잡습니다.", "물이 닿을 수 있으니 바니시나 수성 우레탄으로 2회 칠합니다."],
      ["집성판 18T", "MDF 6mm", "목공 피스·목공본드", "바니시(수성 우레탄)"]),
     ("kaetower", "원목 캣타워", "캣타워 만들기 자재 — 집성판·45각 각재 600×600×1240 3단 고양이 캣타워", "고양이가 오르내리는 바닥 600×600, 높이 약 1240mm 3단 캣타워입니다. 45각 기둥 3개와 집성판 선반 3장으로 만들고 기둥에 삼줄을 감아 스크래처로 씁니다.",
      [("바닥판·선반", "집성판", r"미송.*18T", [(600, 600, 1), (300, 300, 3)], "집성판 18T · 바닥 600×600 1장, 선반 300×300 3장"),
       ("기둥", "각재·다루끼", r"45각", [(800, 0, 1), (400, 0, 1), (382, 0, 1)], "스프러스 집성 45각 · 기둥 800mm·400mm·382mm 각 1개")],
      ["바닥판 앞쪽 모서리에 400mm 기둥, 뒤쪽 모서리에 800mm 기둥을 아래에서 피스로 고정합니다.", "400mm 기둥 위에 첫째 선반, 800mm 기둥 위에 둘째 선반을 얹어 고정합니다.", "둘째 선반 위에 382mm 기둥을 세우고 맨 위 선반을 얹습니다.", "기둥에 삼줄을 본드로 감고, 키가 높으니 벽에 넘어짐 방지 철물로 꼭 잡습니다."],
      ["집성판 18T", "스프러스 집성 45각", "목공 피스·목공본드", "삼줄(사이잘 로프)", "넘어짐 방지 철물"]),
     ("jangnangam", "장난감 수납함", "장난감 수납함 만들기 자재 — 집성판 800×400×468 뚜껑 있는 수납 상자", "거실·아이방에 두는 폭 800, 깊이 400, 높이 약 470mm 뚜껑 있는 수납함입니다. 장난감·이불·캠핑용품 정리에 좋고, 뚜껑을 닫으면 벤치처럼 앉을 수 있습니다.",
      [("바닥·뚜껑·앞뒤·옆판", "집성판", r"미송.*18T", [(800, 400, 2), (800, 432, 2), (364, 432, 2)], "집성판 18T · 바닥·뚜껑 800×400 2장, 앞·뒤판 800×432 2장, 옆판 364×432 2장")],
      ["바닥판 위에 앞·뒤판을 세우고 사이에 옆판 2장을 끼워 상자를 만듭니다.", "모서리를 목공본드+피스로 고정하고 피스 머리는 메움 처리합니다.", "뚜껑을 뒤판에 경첩으로 답니다 — 아이가 쓰면 천천히 닫히는 뚜껑 지지대(소프트 다운)를 꼭 다세요.", "모서리를 둥글게 갈고 수성 페인트나 오일로 마감합니다."],
      ["집성판 18T", "목공 피스·목공본드", "경첩 2개", "뚜껑 지지대(소프트 다운)", "수성 페인트·목재 오일"]),
     ("jwatak", "원목 좌탁", "좌탁 만들기 자재 — 고무나무 30T 1000×600×350 거실 좌식 테이블", "거실·원룸에 두는 폭 1000, 깊이 600, 높이 350mm 좌식 테이블(좌탁)입니다. 두꺼운 고무나무 30T 상판에 45각 다리와 집성판 띠장을 짜서 흔들림이 적습니다.",
      [("상판", "집성판", r"고무.*30T", [(1000, 600, 1)], "고무나무 집성판 30T · 1000×600 1장"),
       ("다리", "각재·다루끼", r"45각", [(320, 0, 4)], "스프러스 집성 45각 · 320mm 4개"),
       ("띠장(에이프런)", "집성판", r"미송.*18T", [(850, 80, 2), (450, 80, 2)], "집성판 18T · 앞·뒤 850×80 2장, 옆 450×80 2장")],
      ["다리 4개 사이에 띠장을 끼워 다리 틀을 만듭니다(다리 위쪽에 맞춰 목공본드+피스).", "틀을 뒤집어 대각선 길이가 같은지 재서 직각을 맞춥니다.", "상판을 엎어 놓고 틀을 올려, 띠장 안쪽에서 비스듬히 피스를 박아 고정합니다.", "상판 모서리를 둥글게 갈고 물에 강한 오일로 마감합니다."],
      ["고무나무 집성판 30T", "스프러스 집성 45각", "집성판 18T", "목공 피스·목공본드", "목재 오일"]),
     ("renjidae", "주방 렌지대", "렌지대 만들기 자재 — 집성판 600×400×1200 4단 전자레인지 수납장", "주방에 두는 폭 600, 깊이 400, 높이 1200mm 4단 렌지대입니다. 전자레인지·밥솥·에어프라이어를 올리는 선반장으로, 집성판 18T와 MDF 뒷판으로 만듭니다.",
      [("옆판·선반", "집성판", r"미송.*18T", [(400, 1200, 2), (564, 394, 4)], "집성판 18T · 옆판 400×1200 2장, 선반 564×394 4장"),
       ("뒷판", "MDF", r"6mm", [(564, 1200, 1)], "MDF 6mm · 564×1200 1장")],
      ["옆판 2장에 선반 높이(아래부터 60·420·780mm, 맨 위)를 표시합니다.", "선반 4장을 표시선에 맞춰 목공본드+피스로 고정합니다.", "뒷판을 붙이되, 전자레인지 칸 뒤에는 열이 빠지게 구멍이나 틈을 냅니다.", "밥솥 김이 닿는 칸은 바니시로 2회 칠하고, 벽에 넘어짐 방지 철물로 잡습니다."],
      ["집성판 18T", "MDF 6mm", "목공 피스·목공본드", "바니시", "넘어짐 방지 철물"]),
     ("sunappyeongsang", "수납 평상", "수납 평상 만들기 자재 — 집성판 18T 1800×900×400 3칸 수납 원목 평상", "방·베란다에 두는 폭 1800, 깊이 900, 높이 400mm 수납 평상입니다. 앉거나 눕는 평상 아래에 앞이 트인 수납칸 3개(폭 576mm)가 있어 바구니·이불을 넣을 수 있습니다.",
      [("상판·바닥판", "집성판", r"미송.*18T", [(1800, 900, 2)], "집성판 18T · 1800×900 2장"),
       ("옆판·칸막이·뒷판", "집성판", r"미송.*18T", [(900, 364, 2), (882, 364, 2), (1764, 364, 1)], "집성판 18T · 옆판 900×364 2장, 칸막이 882×364 2장, 뒷판 1764×364 1장")],
      ["바닥판 위 양 끝에 옆판 2장을, 뒤쪽에 뒷판을 세워 목공본드+피스로 고정합니다.", "바닥판 안쪽 폭 1764mm를 3칸(576mm씩)으로 나눠 칸막이 2장을 세웁니다.", "상판을 덮고 옆판·칸막이·뒷판 위치에 맞춰 피스를 박습니다(피스 간격 150~200mm).", "모서리를 사포로 둥글게 갈고 오일로 마감한 뒤 수납 바구니를 넣습니다."],
      ["집성판 18T", "목공 피스·목공본드", "사포", "목재 오일", "수납 바구니"]),
     ("hwajangdae", "원목 화장대", "화장대 만들기 자재 — 집성판 900×400×750 윗선반 있는 원목 화장대", "폭 900, 깊이 400, 높이 750mm 원목 화장대입니다. 상판 뒤쪽에 높이 250mm 윗선반을 올려 화장품을 세워 두고, 거울은 벽에 따로 겁니다. 집성판 18T 한 가지로 만듭니다.",
      [("옆판(다리판)", "집성판", r"미송.*18T", [(400, 732, 2)], "집성판 18T · 400×732 2장"),
       ("상판·띠장·윗선반", "집성판", r"미송.*18T", [(900, 400, 1), (864, 100, 2), (900, 150, 1), (150, 232, 2)], "집성판 18T · 상판 900×400 1장, 앞·뒤 띠장 864×100 2장, 윗선반 900×150 1장, 윗선반 기둥 150×232 2장")],
      ["옆판 2장 위쪽 안에 앞·뒤 띠장을 끼워 목공본드+피스로 다리 틀을 만듭니다.", "상판을 올려 옆판·띠장에 피스로 고정합니다(무릎 공간 높이 약 630mm).", "상판 뒤쪽 양 끝에 윗선반 기둥 2개를 세우고 윗선반을 덮어 고정합니다.", "모서리를 사포로 갈고 바니시로 마감한 뒤, 거울은 벽에 걸고 화장대는 넘어짐 방지 철물로 잡습니다."],
      ["집성판 18T", "목공 피스·목공본드", "사포", "넘어짐 방지 철물", "벽걸이 거울", "바니시"]),
     ("sangbujang", "주방 상부장", "상부장 만들기 자재 — 집성판 18T 800×300×700 문 2짝 벽걸이 주방 수납장", "주방 벽에 거는 폭 800, 깊이 300(문 포함 318), 높이 700mm 상부장 1개입니다. 가운데 선반 1개와 여닫이 문 2짝이 있고, 천판 아래 걸이 띠장으로 벽에 고정합니다.",
      [("옆판·천판·바닥판·선반", "집성판", r"미송.*18T", [(294, 700, 2), (764, 294, 2), (764, 274, 1), (764, 80, 1)], "집성판 18T · 옆판 294×700 2장, 천판·바닥판 764×294 2장, 선반 764×274 1장, 걸이 띠장 764×80 1장"),
       ("문짝", "집성판", r"미송.*18T", [(397, 697, 2)], "집성판 18T · 397×697 2장(덮개식, 가운데 틈 3mm)"),
       ("뒷판", "MDF", r"6mm", [(800, 700, 1)], "MDF 6mm · 800×700 1장")],
      ["옆판 2장 사이에 천판·바닥판을 끼워 목공본드+피스로 상자를 짭니다.", "대각선 길이를 맞춰 뒷판을 붙이고, 천판 아래 뒤쪽에 걸이 띠장을 고정합니다.", "가운데 선반을 바닥에서 약 340mm 높이에 선반다보나 피스로 놓습니다.", "문짝에 35mm 경첩 홈을 파서 달고, 걸이 띠장을 통해 벽 샛기둥이나 앵커에 단단히 고정합니다(무거운 그릇은 아래 칸에)."],
      ["집성판 18T", "MDF 6mm", "35mm 싱크 경첩 4개", "손잡이 2개", "벽 앵커·긴 피스", "목공 피스·목공본드", "바니시"]),
     ("silwoegi", "에어컨 실외기 커버", "실외기 커버 만들기 자재 — 방부목 1040×400×800 에어컨 실외기 가림막", "베란다·마당의 에어컨 실외기를 가리는 폭 1040, 깊이 400, 높이 800mm 커버입니다. 방부목 2×2 틀에 데크재 20×120을 옆과 위에만 대고, 바람이 나오는 앞면과 뒷면은 비워 둡니다. 안쪽 폭 924·높이 742mm 이하 실외기에 맞습니다.",
      [("기둥·윗띠장", "방부목", r"2\* 2", [(780, 0, 4), (924, 0, 2)], "방부목 2×2(38×38) · 기둥 780mm 4개, 앞·뒤 윗띠장 924mm 2개"),
       ("윗판·옆 살", "방부목", r"20\*120", [(1040, 0, 3), (400, 0, 6)], "방부목 20×120 · 윗판 1040mm 3장, 옆 살 400mm 6장")],
      ["기둥 4개 위쪽 사이에 앞·뒤 윗띠장(924mm)을 끼워 피스로 틀을 짭니다.", "양 옆에 옆 살(400mm)을 3장씩 넓은 간격으로 박아 바람이 통하게 합니다.", "위에 윗판(1040mm) 3장을 20mm 간격으로 덮어 피스로 고정합니다.", "앞면은 바람이 나오는 쪽이라 막지 않고, 실외기와 띄워 씌운 뒤 오일스테인을 칠합니다."],
      ["방부목 2×2", "방부목 20×120", "스테인리스 피스", "오일스테인"]),
     ("deckgyedan", "데크 계단 2단", "데크 계단 만들기 자재 — 방부목 900×560 2단 계단(한 단 165mm)", "데크·현관 앞에 놓는 폭 900, 깊이 560mm 2단 계단입니다. 방부목 2×6 틀 상자 두 개를 쌓고 데크재 25×140을 덮는 방식이라, 한 단 높이 165mm·디딤 깊이 280mm로 오르내리기 편합니다. 데크 바닥 높이가 약 495mm(165×3)면 마지막 한 칸이 데크 바닥으로 이어집니다.",
      [("계단 틀", "방부목", r"2\* 6", [(900, 0, 4), (484, 0, 3), (204, 0, 3)], "방부목 2×6(38×140) · 앞·뒤 틀 900mm 4개, 아래 단 옆·가운데 484mm 3개, 위 단 옆·가운데 204mm 3개"),
       ("디딤판", "방부목", r"25\*140", [(900, 0, 6)], "방부목 데크재 25×140 · 900mm 6장 (아래 단 4장, 위 단 2장)")],
      ["2×6 앞·뒤 틀(900mm) 사이에 옆·가운데 484mm 3개를 끼워 900×560 아래 단 틀을 짜고 피스로 고정합니다.", "아래 단 틀 위에 데크재 900mm 4장을 덮어 피스로 박습니다.", "같은 방법으로 900×280 위 단 틀(옆·가운데 204mm)을 짜서 아래 단 뒤쪽 절반 위에 올리고, 옆·가운데 틀이 아래 단 틀과 겹치게 맞춰 피스로 고정합니다.", "위 단에 데크재 2장을 덮고, 계단을 데크에 붙여 수평을 맞춘 뒤 오일스테인을 칠합니다."],
      ["방부목 2×6", "방부목 데크재 25×140", "스테인리스 피스(65mm·75mm)", "오일스테인"]),
     ("kaempingbox", "원목 캠핑 박스", "캠핑 박스 만들기 자재 — 집성판 600×380×350 뚜껑 달린 원목 수납 박스", "캠핑 장비·공구·차량 짐을 담는 폭 600, 깊이 380, 높이 350mm(뚜껑 포함) 원목 박스입니다. 미송 집성판 18T 한 가지로 만들고, 뚜껑을 덮으면 간이 테이블로도 씁니다.",
      [("바닥·뚜껑·앞뒤·옆판", "집성판", r"미송.*18T", [(600, 380, 2), (600, 314, 2), (344, 314, 2)], "미송 집성판 18T · 바닥·뚜껑 600×380 2장, 앞·뒤판 600×314 2장, 옆판 344×314 2장")],
      ["바닥판(600×380) 위 앞·뒤 가장자리에 앞·뒤판(600×314)을 세워 목공본드와 피스로 고정합니다.", "앞·뒤판 사이 양쪽 끝에 옆판(344×314)을 끼워 상자를 완성합니다.", "양 옆판 바깥쪽에 손잡이를 하나씩 피스로 답니다.", "뚜껑(600×380)을 경첩 2개로 뒤쪽에 달고, 모서리를 사포로 다듬어 오일을 칠합니다."],
      ["미송 집성판 18T", "목공 피스·목공본드", "경첩 2개·손잡이 2개", "사포·오일"]),
     ("sinkmunjjak", "싱크대 문짝", "싱크대 문짝 만들기 자재 — MDF 15T 하부장 문짝 셀프 교체 재단 목록", "몸통은 그대로 두고 문짝만 새로 만들어 거는 방법입니다. 폭 800, 높이 720mm 하부장 2짝 기준(문짝 397×720 2장)이며, 집 싱크대 치수에 맞춰 바꿔 쓰세요. MDF 15T 원판 1장에서 같은 크기 문짝을 최대 9장까지 뽑을 수 있습니다.",
      [("문짝", "MDF", r"^MDF 4\*8 @15mm", [(397, 720, 2)], "MDF 15mm · 397×720 2장 (양옆·가운데 틈 약 1~4mm)")],
      ["기존 문짝과 경첩을 떼고, 몸통 칸의 폭·높이와 경첩 위치를 잽니다.", "MDF 15T를 치수대로 재단해 모서리를 사포로 다듬고, 인테리어 필름이나 페인트로 마감합니다.", "문짝 안쪽에 35mm 경첩 홈을 파서 컵경첩을 달고, 바깥쪽에 손잡이를 붙입니다.", "문짝을 몸통에 걸고 경첩 나사로 위아래·좌우 유격을 맞추면 끝입니다."],
      ["MDF 15T", "싱크대 컵경첩(35mm) 4개", "손잡이 2개", "35mm 보링 비트", "인테리어 필름 또는 페인트", "사포"]),
     ("headboard", "원목 침대 헤드보드", "침대 헤드보드 만들기 자재 — 집성판 1600×1018 선반 달린 원목 헤드보드", "퀸 침대(폭 1500) 뒤 벽에 세우는 폭 1600, 높이 약 1018mm 원목 헤드보드입니다. 구조재 2×4 다리 2개에 미송 집성판 18T 패널을 붙이고, 맨 위에 휴대폰·안경을 올려 두는 좁은 선반을 얹습니다.",
      [("다리·가로대", "구조재", r"Ⅱ 2\* 4", [(1000, 0, 2), (1364, 0, 1)], "2×4(38×89) · 다리 1000mm 2개, 아래 가로대 1364mm 1개"),
       ("패널·상단 선반", "집성판", r"미송.*18T", [(1600, 600, 1), (1640, 150, 1)], "미송 집성판 18T · 패널 1600×600 1장, 상단 선반 1640×150 1장")],
      ["다리 2개(1000mm)를 1364mm 간격으로 세우고, 바닥에서 150mm 높이에 가로대를 피스로 고정합니다.", "다리 앞면 위쪽(높이 400~1000mm)에 패널(1600×600)을 목공본드와 피스로 붙입니다.", "다리와 패널 윗면에 상단 선반(1640×150)을 얹어 피스로 고정합니다.", "모서리를 사포로 다듬고 오일을 바른 뒤, 넘어지지 않게 고정 철물로 벽에 잡아 줍니다."],
      ["구조재 2×4", "미송 집성판 18T", "목공 피스·목공본드", "벽 고정 철물(ㄱ자 브라켓)", "사포·오일"]),
     ("silnaehwa", "원목 실내화 선반", "실내화 선반 만들기 자재 — 미송 집성판 600×260×600 3단 오픈형 슬리퍼 선반", "현관이나 거실 입구에 두는 폭 600, 깊이 260, 높이 600mm 3단 오픈형 실내화(슬리퍼) 선반입니다. 미송 집성판 18T 한 가지로 만들고, 칸 높이가 약 240mm라 슬리퍼를 한 칸에 2~3켤레씩 올립니다. 맨 윗면에는 열쇠·소품을 둡니다.",
      [("옆판·선반·뒷막이", "집성판", r"미송.*18T", [(260, 600, 2), (564, 260, 3), (564, 60, 2)], "미송 집성판 18T · 옆판 260×600 2장, 선반 564×260 3장, 뒷막이 564×60 2장")],
      ["옆판 2장(260×600) 사이 바닥에서 30mm 높이에 맨 아래 선반(564×260)을 끼워 목공본드와 피스로 고정합니다.", "높이 290mm에 가운데 선반을 같은 방법으로 고정합니다.", "옆판 맨 위에 윗선반을 끼워 고정하면 상자 모양이 완성됩니다.", "아래·가운데 선반 뒤쪽에 뒷막이(564×60)를 세워 붙여 슬리퍼가 뒤로 빠지지 않게 하고, 사포로 다듬어 오일을 칠합니다."],
      ["미송 집성판 18T", "목공 피스·목공본드", "사포", "목재 오일"]),
     ("hwabunonsil", "소형 화분 온실", "소형 온실 만들기 자재 — 방부목 1200×600×1500 3단 선반 화분 온실", "마당·베란다에서 화분을 겨울나기 시키는 폭 1200, 깊이 600, 높이 1500mm 소형 온실입니다. 방부목 2×2 틀에 데크재 20×120 선반 3단을 얹고, 겉은 폴리카보네이트판이나 온실용 비닐로 씌웁니다. 칸 높이는 약 500mm입니다(그림은 덮개 아래 골조).",
      [("기둥·띠장·받침", "방부목", r"2\* 2", [(1500, 0, 4), (1124, 0, 4), (524, 0, 8)], "방부목 2×2(38×38) · 기둥 1500mm 4개, 앞·뒤 띠장 1124mm 4개(아래·위), 옆 받침 524mm 8개(선반 3단·윗 테두리)"),
       ("선반판", "방부목", r"20\*120", [(1190, 0, 12)], "방부목 20×120 · 1190mm 12장 (한 단에 4장)")],
      ["기둥 4개(1500mm) 바닥에서 100mm 높이에 앞·뒤 띠장(1124mm)과 양옆 받침(524mm)을 피스로 고정해 1200×600 아래 틀을 짭니다.", "높이 600·1100mm에 양옆 받침을 더 달고, 맨 위(높이 1462mm)에 앞·뒤 띠장과 옆 받침으로 윗 테두리를 짭니다.", "세 단의 옆 받침 위에 선반판(1190mm)을 4장씩 약 15mm 간격으로 얹어 피스로 박습니다.", "오일스테인을 칠하고 지붕·옆·뒤에 폴리카보네이트판이나 온실용 비닐을 씌운 뒤, 앞은 비닐 커튼으로 막고 벽이나 바닥에 고정합니다."],
      ["방부목 2×2", "방부목 20×120", "스테인리스 피스", "폴리카보네이트판 또는 온실용 비닐", "타카·비닐 고정 띠", "오일스테인", "벽·바닥 고정 철물"]),
     ("gangajigyedan", "강아지 계단", "강아지 계단 만들기 자재 — 미송 집성판 400×600×450 3단 반려견 계단", "소파·침대 옆에 두는 폭 400, 깊이 600, 높이 450mm 3단 강아지(반려견) 계단입니다. 한 단 높이 150mm, 디딤 깊이 약 200mm로 낮게 잡아 소형견·노견이 오르내리기 편하고, 미송 집성판 18T 한 가지로 만듭니다.",
      [("옆판·디딤판·챌판·뒤판", "집성판", r"미송.*18T", [(600, 450, 2), (364, 218, 2), (364, 200, 1), (364, 132, 3), (364, 432, 1)], "미송 집성판 18T · 옆판 600×450 2장(계단 모양으로 재단), 디딤판 364×218 2장·364×200 1장, 챌판 364×132 3장, 뒤판 364×432 1장")],
      ["옆판 2장(600×450)을 단 높이 150·깊이 200mm 계단 모양으로 잘라 세우고, 뒤쪽에 뒤판(364×432)을 끼워 목공본드와 피스로 고정합니다.", "맨 앞 아래에 챌판(364×132)을 세우고 그 위에 1단 디딤판(364×218)을 얹어 고정합니다.", "1단 디딤판 위에 챌판을 세우고 2단 디딤판(364×218)을, 다시 챌판과 3단 디딤판(364×200)을 같은 방법으로 고정합니다.", "모서리를 사포로 둥글게 갈고 오일을 칠한 뒤, 디딤면마다 미끄럼 방지 매트를 붙여 발이 미끄러지지 않게 합니다."],
      ["미송 집성판 18T", "목공 피스·목공본드", "사포", "미끄럼 방지 매트", "목재 오일"]),
     ("yangnyeomseonban", "원목 양념통 선반", "양념통 선반 만들기 자재 — 미송 집성판 500×200×450 2단 주방 조미료 선반", "싱크대·조리대 위에 두는 폭 500, 깊이 200, 높이 450mm 2단 양념통(조미료) 선반입니다. 칸 높이가 약 200mm라 일반 양념통·소스병이 들어가고, 앞에 낮은 막이를 달아 병이 앞으로 떨어지지 않게 합니다. 미송 집성판 18T 한 가지로 만듭니다.",
      [("옆판·선반·앞막이", "집성판", r"미송.*18T", [(200, 450, 2), (464, 200, 3), (464, 40, 2)], "미송 집성판 18T · 옆판 200×450 2장, 선반 464×200 3장, 앞막이 464×40 2장")],
      ["옆판 2장(200×450) 사이 맨 아래에 바닥 선반(464×200)을 끼워 목공본드와 피스로 고정합니다.", "높이 216mm에 가운데 선반을 같은 방법으로 고정합니다.", "옆판 맨 위에 윗선반을 끼워 고정하면 상자 모양이 완성됩니다.", "아래·가운데 칸 앞쪽에 앞막이(464×40)를 붙여 병이 떨어지지 않게 하고, 사포로 다듬어 식물성 오일을 칠합니다."],
      ["미송 집성판 18T", "목공 피스·목공본드", "사포", "식물성 목재 오일"]),     ("mdfseonbanjang", "MDF 다용도 선반장", "선반장 만들기 자재 — MDF 15T 800×300×1500 5단 다용도 수납 선반장", "거실·창고·다용도실에 두는 폭 800, 깊이 300, 높이 1500mm 다용도 선반장입니다(뒷판 6mm 별도). 칸 높이 약 345mm 4칸으로 책·상자·생활용품을 넣고, MDF 15T 한 장으로 옆판과 선반이 모두 나오며 뒷판은 MDF 6mm로 막아 흔들림을 잡습니다.",
      [("옆판·선반", "MDF", r"^MDF 4\*8 @15mm", [(300, 1500, 2), (770, 300, 5)], "MDF 15T · 옆판 300×1500 2장, 바닥·윗판·선반 770×300 5장(옆판 두께 15×2를 뺀 안쪽 폭)"),
       ("뒷판", "MDF", r"6mm", [(800, 1500, 1)], "MDF 6mm · 뒷판 800×1500 1장")],
      ["옆판 2장(300×1500) 사이 맨 아래에 바닥판, 맨 위에 윗판(770×300)을 끼워 목공본드와 피스로 고정해 큰 틀을 만듭니다.", "높이 약 360·720·1080mm에 선반 3장(770×300)을 수평을 보며 같은 방법으로 고정합니다.", "뒤쪽에 뒷판(MDF 6mm 800×1500)을 대고 실타카나 짧은 피스로 촘촘히 박아 틀이 비틀리지 않게 잡습니다.", "MDF 모서리를 사포로 다듬고 젯소·페인트나 인테리어 필름으로 마감한 뒤, 키 큰 가구라 벽에 넘어짐 방지 철물로 고정합니다."],
      ["MDF 15T", "MDF 6mm", "목공 피스·목공본드", "실타카", "사포", "젯소·페인트 또는 인테리어 필름", "넘어짐 방지 철물"]),
     ("teureongkeu", "차량 트렁크 정리함", "트렁크 정리함 만들기 자재 — 합판 12mm 800×400×300 3칸 차량 수납함·차박 정리함", "자동차 트렁크에 넣는 폭 800, 깊이 400, 높이 300mm 3칸 정리함입니다. 캠핑·차박 짐, 장바구니, 세차 용품을 칸별로 나눠 넣고, 양옆에 손잡이 구멍을 뚫어 들고 다닙니다. 내수 합판 12mm 한 장으로 모두 나옵니다(트렁크 크기를 먼저 재고 맞추세요).",
      [("바닥·앞뒤판·옆판·칸막이", "합판", r"4\*8 @12mm\(내수/A급\)", [(800, 400, 1), (800, 288, 2), (376, 288, 2), (376, 200, 2)], "내수 합판 12mm · 바닥 800×400 1장, 앞뒤판 800×288 2장, 옆판 376×288 2장(앞뒤판 두께 12×2를 뺀 길이), 칸막이 376×200 2장")],
      ["바닥판(800×400) 위 앞뒤 가장자리에 앞뒤판(800×288)을 세워 목공본드와 피스로 고정합니다.", "앞뒤판 사이 양 끝에 옆판(376×288)을 끼워 고정하고, 옆판 위쪽에 손잡이 구멍을 뚫습니다.", "안쪽을 3칸으로 나눠 칸막이 2장(376×200)을 끼워 고정합니다.", "모서리를 사포로 둥글게 갈고 오일이나 바니시를 칠한 뒤, 바닥에 미끄럼 방지 패드를 붙여 주행 중 밀리지 않게 합니다."],
      ["내수 합판 12mm", "목공 피스·목공본드", "자유비트·직소(손잡이 구멍)", "사포", "목재 오일 또는 바니시", "미끄럼 방지 패드"]),
     ("deskseonban", "책상 위 2단 선반", "책상 위 선반 만들기 자재 — 미송 집성판 800×200×450 2단 데스크 선반", "책상 뒤쪽에 올려 두는 폭 800, 깊이 200, 높이 450mm 2단 선반입니다. 아래 칸(높이 약 210mm)에는 필기구·작은 상자를, 위 칸과 윗판에는 책·소품을 올려 책상 위를 정리합니다. 미송 집성판 18T 한 가지로 만듭니다.",
      [("옆판·선반·윗판·뒷막이", "집성판", r"미송.*18T", [(200, 432, 2), (800, 200, 1), (764, 200, 1), (764, 60, 1)], "미송 집성판 18T · 옆판 200×432 2장, 윗판 800×200 1장, 가운데 선반 764×200 1장(옆판 두께 18×2를 뺀 안쪽 폭), 뒷막이 764×60 1장")],
      ["옆판 2장(200×432)을 세우고, 바닥에서 210mm 높이에 가운데 선반(764×200)을 끼워 목공본드와 피스로 고정합니다.", "옆판 맨 위 뒤쪽에 뒷막이(764×60)를 끼워 고정해 좌우 흔들림을 잡습니다.", "옆판과 뒷막이 위에 윗판(800×200)을 얹어 목공본드와 피스로 고정합니다.", "모서리를 사포로 다듬고 오일을 칠한 뒤, 옆판 바닥에 미끄럼 방지 패드를 붙여 책상에 올립니다."],
      ["미송 집성판 18T", "목공 피스·목공본드", "사포", "목재 오일", "미끄럼 방지 패드"]),
     ("minichanggo", "미니 창고", "미니 창고 만들기 자재 — 방부목·내수합판 1200×900 소형 정원 창고(공구·캠핑 용품 보관)", "마당·텃밭 한쪽에 두는 바닥 1200×900, 높이 앞 약 1540·뒤 약 1440mm 소형 창고입니다. 방부목 2×4로 바닥틀과 기둥을 짜고 내수 합판 12mm로 벽·문·지붕을 막으며, 지붕은 뒤로 기울여 빗물이 흘러내리게 합니다. 공구·호스·캠핑 용품 보관용이고, 사람이 들어가 쓰는 공간은 아닙니다.",
      [("바닥틀·기둥·띠장·서까래", "방부목", r"2\* 4", [(1200, 0, 4), (824, 0, 3), (1400, 0, 2), (1300, 0, 3), (1050, 0, 3)], "방부목 2×4(38×89) · 바닥틀 앞뒤·윗 띠장 1200mm 4개, 바닥 장선 824mm 3개(앞뒤 틀 두께 38×2를 뺀 길이), 앞 기둥 1400mm 2개, 뒤 기둥·가운데 샛기둥 1300mm 3개, 서까래 1050mm 3개"),
       ("바닥·벽·문·지붕", "합판", r"4\*8 @12mm\(내수/A급\)", [(1200, 900, 1), (1200, 1440, 1), (912, 1540, 2), (596, 1420, 2), (1200, 101, 1), (1320, 1020, 1)], "내수 합판 12mm · 바닥 1200×900 1장, 뒷벽 1200×1440 1장, 옆벽 912×1540 2장(뒤쪽 높이 1440으로 비스듬히 재단), 문 596×1420 2장, 앞 걸레받이 1200×101 1장, 지붕 1320×1020 1장")],
      ["방부목 2×4로 앞뒤 틀(1200mm) 사이에 장선(824mm) 3개를 피스로 박아 바닥틀을 짜고, 수평을 본 블록 위에 놓은 뒤 바닥 합판(1200×900)을 덮습니다.", "네 모서리에 앞 기둥(1400mm)·뒤 기둥(1300mm)과 뒤 가운데 샛기둥을 세우고, 기둥 위에 앞·뒤 윗 띠장(1200mm)을 눕혀 피스로 고정합니다.", "뒷벽(1200×1440)과 비스듬히 재단한 옆벽(912×1540) 2장을 바깥에서 대고 피스로 박습니다.", "띠장 위에 서까래(1050mm) 3개와 지붕 합판(1320×1020)을 얹어 방수 시트를 붙이고, 걸레받이와 문 2짝(596×1420)을 경첩으로 단 뒤 외부용 칠로 마감합니다."],
      ["방부목 2×4", "내수 합판 12mm", "스테인리스 피스", "문 경첩 4개·걸쇠", "지붕 방수 시트 또는 아스팔트 슁글", "오일스테인 또는 외부용 페인트", "기초 블록(수평 받침)"]),
     ("gongutong", "트럭 공구통", "트럭 공구통 만들기 자재 — 내수합판 12mm 1000×450×450 뚜껑 달린 적재함 공구보관함", "트럭 적재함·캠핑카 뒤칸에 싣는 폭 1000, 깊이 450, 높이 450mm(뚜껑 포함) 공구통입니다. 내수 합판 12mm 원판 1장에서 바닥·뚜껑·앞뒤·옆판을 모두 뽑고, 안쪽 네 모서리는 2×2 각재로 보강합니다. 차에 실을 때는 끈으로 적재함 고리에 단단히 묶어 두세요.",
      [("바닥·뚜껑·앞뒤판·옆판", "합판", r"4\*8 @12mm\(내수/A급\)", [(1000, 450, 2), (1000, 426, 2), (426, 426, 2)], "내수 합판 12mm · 바닥·뚜껑 1000×450 2장, 앞뒤판 1000×426 2장, 옆판 426×426 2장(앞뒤판 두께 12×2를 뺀 길이)"),
       ("모서리 보강", "구조재", r"마감재\) 2\* 2", [(426, 0, 4)], "구조재 2×2(38×38) · 안쪽 네 모서리 세로 보강 426mm 4개")],
      ["바닥판(1000×450) 위 앞뒤 가장자리에 앞뒤판(1000×426)을 세워 목공본드와 피스로 고정합니다.", "앞뒤판 사이 양 끝에 옆판(426×426)을 끼워 고정하고, 안쪽 네 모서리에 2×2 각재(426mm)를 대고 양쪽 판에서 피스를 박아 보강합니다.", "양 옆판 바깥쪽 위쪽에 손잡이를 하나씩 피스로 답니다.", "뚜껑(1000×450)을 뒤쪽에 경첩 2개로 달고 앞에 걸쇠를 단 뒤, 겉면에 방수 도료를 칠합니다."],
      ["내수 합판 12mm", "구조재 2×2", "목공 피스·목공본드", "경첩 2개·손잡이 2개·걸쇠", "사포", "방수 도료 또는 오일스테인", "고정 끈(라싱 벨트)"]),
     ("maegeojinraek", "원목 매거진랙", "매거진랙 만들기 자재 — 아카시아 집성판 400×300×1000 3단 잡지꽂이·그림책 선반", "잡지·그림책 표지가 앞으로 보이게 비스듬히 기대 세워 두는 폭 400, 깊이 300, 높이 1000mm 3단 원목 매거진랙입니다. 칸마다 앞쪽 턱이 책 아래를 잡고 뒤쪽 막대가 책을 받쳐 주며, 윗판에는 작은 소품을 올립니다. 아카시아 집성판 18T 원판 1장으로 만듭니다.",
      [("옆판·선반·앞 턱·뒷막이·윗판", "집성판", r"아카시아.*18T", [(300, 982, 2), (400, 300, 1), (364, 300, 3), (364, 80, 3), (364, 60, 3)], "아카시아 집성판 18T · 옆판 300×982 2장, 윗판 400×300 1장, 선반 364×300 3장(옆판 두께 18×2를 뺀 안쪽 폭), 앞 턱 364×80 3장, 뒷막이 364×60 3장")],
      ["옆판 2장(300×982)을 세우고 바닥에서 60·380·700mm 높이에 선반 3장(364×300)을 끼워 목공본드와 피스로 고정합니다.", "선반마다 앞쪽 끝 위에 앞 턱(364×80)을 세워 옆판과 선반에 피스로 고정합니다.", "선반 윗면에서 200mm 위, 옆판 뒤쪽 끝에 뒷막이(364×60)를 하나씩 끼워 고정해 책이 기댈 자리를 만듭니다.", "윗판(400×300)을 얹어 고정하고 사포질·오일 칠 후, 넘어짐 방지 철물로 벽에 고정합니다."],
      ["아카시아 집성판 18T", "목공 피스·목공본드", "사포", "목재 오일", "넘어짐 방지 철물", "미끄럼 방지 패드"]),
     ("patisyeon", "원목 파티션", "원목 파티션 만들기 자재 — 스프러스 구조재 2×4·다루끼 1200×1800 간살 공간분리 칸막이", "거실·원룸·사무실을 나누는 폭 1200, 높이 1800mm 간살 파티션입니다. 구조재 2×4로 기둥·가로대·발을 짜고, 다루끼 16개를 세로로 세워 시선은 가리되 빛과 바람은 통하게 합니다. 발이 600mm라 혼자 서기는 하지만 키가 커서, 사람이 자주 지나가는 곳이면 벽·가구에 철물로 한 번 더 고정하세요.",
      [("기둥·가로대·발", "구조재", r"마감재\) 2\* 4", [(1711, 0, 2), (1124, 0, 2), (600, 0, 2)], "구조재 2×4(38×89) · 기둥 1711mm 2개(발 높이 89를 뺀 길이), 위·아래 가로대 1124mm 2개(기둥 두께 38×2를 뺀 안쪽 폭), 발 600mm 2개"),
       ("간살", "각재·다루끼", r"1.0\*1.0\*12자", [(1574, 0, 16)], "다루끼 1.0×1.0(약 30×30) · 세로 간살 1574mm 16개(약 38mm 간격, 위·아래 가로대 사이 길이)")],
      ["발(600mm) 2개를 세워 놓고 그 가운데 위에 기둥(1711mm)을 하나씩 올린 뒤, 양쪽에 L자 철물을 대고 피스로 단단히 고정합니다.", "바닥에 눕혀 놓고 기둥 사이에 아래 가로대(바닥에서 약 150mm)와 위 가로대(맨 위)를 눕혀 끼운 다음, 기둥 바깥에서 긴 피스 2개씩 박습니다.", "가로대 사이에 다루끼 간살(1574mm) 16개를 약 38mm 간격으로 세우고, 가로대 위·아래에서 피스를 박아 고정합니다.", "세워서 흔들림을 확인하고 모서리를 사포로 다듬은 뒤 오일이나 스테인을 칠합니다. 통로 쪽이면 벽·가구에 철물로 한 번 더 고정합니다."],
      ["구조재 2×4", "다루끼 1.0×1.0 12자", "목공 피스(긴 피스 90mm 포함)", "L자 철물 4개", "사포", "목재 오일 또는 스테인", "넘어짐 방지 철물"]),
     ("gyedanpan", "원목 계단 디딤판 교체", "계단 디딤판 교체 자재 — 고무나무 집성판 30T 디딤판·18T 챌판 폭 900 콘크리트 계단 원목 마감(3단 기준)", "집 안 콘크리트 계단(폭 900, 단 높이 180, 단 깊이 260mm, 3단 기준)을 원목으로 마감하는 자재입니다. 디딤판은 고무나무 집성판 30T, 챌판(세운 판)은 18T로 붙이고, 디딤판 앞 끝을 챌판보다 약 22mm 내밀어 발끝이 걸리지 않게 합니다. 계단 수·치수는 집마다 다르니 꼭 실제로 재서 맞추고, 아래층 바닥 마감 높이에 따라 첫 단 높이가 달라지니 단 높이가 고른지 먼저 확인하세요.",
      [("디딤판", "집성판", r"고무.*30T", [(900, 300, 3)], "고무나무 집성판 30T · 디딤판 900×300 3장(단 깊이 260 + 챌판 18 + 앞 내밈 22)"),
       ("챌판", "집성판", r"고무.*18T", [(900, 180, 1), (900, 150, 2)], "고무나무 집성판 18T · 첫 단 챌판 900×180 1장, 둘째·셋째 단 챌판 900×150 2장(아래 디딤판 두께 30을 뺀 높이)")],
      ["기존 계단 마감을 걷어내고 콘크리트 면의 들뜬 곳을 갈아 평평하게 정리한 뒤, 단마다 실제 높이·깊이·폭을 재서 재단 치수를 맞춥니다.", "첫 단 앞면에 챌판(900×180)을 우레탄 본드로 붙이고, 그 위에 디딤판(900×300)을 뒤쪽 벽면까지 밀어 붙여 앞 끝이 챌판보다 약 22mm 나오게 고정합니다.", "둘째·셋째 단도 같은 순서로, 아래 디딤판 위에 챌판(900×150)을 세워 붙이고 그 위에 디딤판을 얹어 고정합니다(본드가 굳을 때까지 무거운 것으로 눌러 둡니다).", "벽과 만나는 틈은 실리콘으로 마감하고, 우레탄 바니시나 오일을 칠한 뒤 디딤판 앞 끝에 미끄럼 방지 논슬립을 붙입니다."],
      ["고무나무 집성판 30T", "고무나무 집성판 18T", "계단용 우레탄 본드", "콘크리트 피스·칼블럭(필요한 곳)", "그라인더·사포", "실리콘", "우레탄 바니시 또는 목재 오일", "계단 논슬립"]),
    ]
    _PRICE = {}
    for _r in csv.DictReader(open(ROOT + "/data/prices.csv", encoding="utf-8")):
        _k = re.sub(r"\s+", " ", re.sub(r"^[^-]+-\s*", "", _r["name"])).strip()
        if _r["price"].strip().isdigit() and _k not in _PRICE: _PRICE[_k] = int(_r["price"])
    def _bundle(n):
        m = re.search(r"\((\d+)(?:EA)?\)\s*$", n)
        return int(m.group(1)) if m and 1 < int(m.group(1)) <= 50 else 1
    def _sheets(W, H, parts, k=3):
        return min(_sheets1(W, H, parts, k), _sheets1(H, W, parts, k))
    def _sheets1(W, H, parts, k=3):
        ps = sorted([(max(a, b), min(a, b)) for a, b, q in parts for _ in range(q)], key=lambda t: (-t[0], -t[1]))
        bins = []  # 시트마다 선반 목록 [y사용, [(선반높이, x사용)]]
        for L, S in ps:
            done = False
            for sh in bins:
                for shelf in sh[1]:
                    for w_, h_ in ((L, S), (S, L)):
                        if h_ <= shelf[0] and shelf[1] + w_ + (k if shelf[1] else 0) <= W:
                            shelf[1] += w_ + (k if shelf[1] else 0); done = True; break
                    if done: break
                if not done:
                    for w_, h_ in ((L, S), (S, L)):
                        if w_ <= W and sh[0] + h_ + (k if sh[0] else 0) <= H:
                            sh[0] += h_ + (k if sh[0] else 0); sh[1].append([h_, w_]); done = True; break
                if done: break
            if not done:
                for w_, h_ in ((S, L), (L, S)):
                    if w_ <= W and h_ <= H: bins.append([h_, [[h_, w_]]]); done = True; break
                if not done: bins.append([H, [[H, W]]])
        return len(bins)
    mk_cards = ""
    # 만들기별 관련 유튜브 영상(제목 키워드). 없는 slug는 짧은 이름으로 찾음
    MKV = {"pyeongsang": r"평상(?!형)", "chaekjang": r"책장", "tutbat": r"텃밭|화분만들기|방부목 화분", "deck": r"데크 셀프|방부목 데크|데크 시공|데크만들기|데크 만들기",
           "gabyeok": r"가벽", "byeokseonban": r"^(?!.*온실).*(벽선반|원목선반|선반 만들|선반만들)", "ultari": r"울타리|펜스", "teibeul": r"테이블",
           "sinbaljang": r"신발장|수납장", "benchi": r"벤치|의자", "chimdae": r"(?<!받)침대", "jakeopdae": r"작업대|가구만들기|합판으로 가구", "monitor": r"모니터|컴퓨터받침대",
           "beranda": r"^(?!.*온실).*(선반|수납장)", "dannyeolbyeok": r"단열", "saideu": r"협탁|사이드", "hyeongwanbench": r"수납 의자|벤치|의자",
           "gaejip": r"강아지집|개집", "hwabundae": r"화분", "aichaeksang": r"책상", "geosiljang": r"티비다이|TV 수납|거실장", "seutul": r"스툴|의자",
           "nopeuntutbat": r"텃밭|화분만들기|방부목 화분", "haenggeo": r"행거|옷장", "yaoeteibeul": r"테이블", "jangjak": r"장작", "gongguborad": r"공구통|타공판|공구 수납|수납장",
           "cube": r"나무박스|박스만들기|수납박스|정리함",
           "sadariseonban": r"사다리 선반|사다리", "aillaendeu": r"아일랜드", "balpan": r"발판|스텝", "bunrisugeo": r"분리수거", "kaetower": r"캣타워|고양이", "jangnangam": r"장난감|수납함", "jwatak": r"좌탁|밥상", "renjidae": r"렌지대|전자레인지", "sunappyeongsang": r"평상(?!형)", "hwajangdae": r"화장대", "sangbujang": r"상부장", "silwoegi": r"실외기 ?(커버|가림)", "deckgyedan": r"DIY 계단|계단 만들", "kaempingbox": r"나무박스|캠핑 ?박스", "sinkmunjjak": r"싱크대 ?문짝", "headboard": r"침대프레임만들기|명품 침대 만드는", "silnaehwa": r"슬리퍼|실내화", "hwabunonsil": r"온실", "gangajigyedan": r"강아지 계단", "yangnyeomseonban": r"양념통", "mdfseonbanjang": r"4단 선반|선반 만들 때|MDF 가구", "teureongkeu": r"차박|정리함", "deskseonban": r"데스크|선반 만들 때", "minichanggo": r"창고", "gongutong": r"공구통|적재함", "maegeojinraek": r"매거진랙|잡지꽂이", "patisyeon": r"파티션", "gyedanpan": r"계단판|원목 계단"}
    def mkvids(slug, nm):
        rx = MKV.get(slug) or re.escape(re.sub(r"^(원목|목재|야외|작은)\s*", "", nm).split()[0])
        hit = [v for v in V if re.search(rx, v["title"])]
        hit.sort(key=lambda v: (0 if re.match(r"\W*(?:" + rx + ")", v["title"]) else 1 if re.search(rx, v["title"].split("|")[0]) else 2, 0 if v["type"] != "S" else 1, -v["n"]))
        return hit[:6]
    import gagyeok as _gg0
    import matinfo as _mi, cmbs as _cmx
    MI = _mi.M(E, cutlink, lambda n: _cmx.catlink(ROOT, n))
    for slug, nm, title, lead, rows, steps, mats in MK:
        trs, btns = "", ""
        _mv = mkvids(slug, nm)
        _hi = os.path.exists(f"{ROOT}/assets/mandeul/{slug}.jpg"); _si = os.path.exists(f"{ROOT}/assets/mandeul/{slug}-steps.jpg")
        _hero = f'<figure class="mkfig"><img src="/assets/mandeul/{slug}.jpg" width="1200" height="800" alt="{E(nm)} 완성 모습 그림"><figcaption class="small muted">완성 모습 그림 — 표의 크기대로 만들면 이렇게 됩니다.</figcaption></figure>' if _hi else ""
        _stp = f'<section class="wrap sec"><h2>{E(nm)} 만드는 순서 (그림 설명서)</h2><img class="mkfig" loading="lazy" src="/assets/mandeul/{slug}-steps.jpg" alt="{E(nm)} 만드는 순서 그림 설명서" style="width:100%;height:auto;border-radius:14px;border:1px solid #e6e0d4"><p class="small muted">빨간 테두리가 그 단계에서 새로 붙이는 부재입니다.</p></section>' if _si else ""
        _tot = 0; _grp = {}; _seen = set(); _ml = []; _pl = []
        _ms = []
        for r_ in rows:
            m_ = {"합판": "hapan", "MDF": "mdf", "집성판": "jipseong", "석고보드": "gypsum", "단열재": "insul", "구조재": "gujo", "방부목": "bangbu", "각재·다루끼": "gujo", "데크": "hapdeck"}.get(r_[1])
            if m_ and m_ not in _ms: _ms.append(m_)
        _ph = []
        for m_ in _ms:
            for q in mat_photos(m_)[:6]:
                if q not in _ph: _ph.append(q)
        _gal = (f'<section class="wrap sec"><h2>필요한 자재 실물 사진</h2><p class="small muted">매장에서 실제로 파는 제품 사진입니다. 누르면 상세 사진과 규격이 열립니다.</p><div class="pg hrow">' + "".join(pcard(q) for q in _ph[:10]) + '</div><p class="hsh">옆으로 밀어서 더 보기 ›</p></section>') if _ph else ""
        for part, cat, rx, parts, desc in rows:
            c = next(c for c in _cd["cats"] if c["n"] == cat)
            it = next((x for x in c["items"] if re.search(rx, x[0])), c["items"][0])
            _grp.setdefault((cat, it[0]), [c, it, []])[2].extend(parts)
        for part, cat, rx, parts, desc in rows:
            c = next(c for c in _cd["cats"] if c["n"] == cat)
            it = next((x for x in c["items"] if re.search(rx, x[0])), c["items"][0])
            key = (cat, it[0]); allp = _grp[key][2]
            pr = _PRICE.get(it[0]); bun = _bundle(it[0])
            if c["lin"]:
                n_ = ffd(it[1], allp); unit = f"{it[1]}mm"
                units = -(-n_ // bun) if bun > 1 else n_
            else:
                n_ = _sheets(it[1], it[2], allp); unit = f"{it[1]}×{it[2]} 원판"
                units = n_
            if key in _seen:
                cnt = "위 줄과 같은 자재에서 함께 재단"; money = "위 금액에 포함"
            else:
                _seen.add(key)
                cnt = (f'{n_}개 ({unit} 기준)' if c["lin"] else f'약 {n_}장 ({unit})') + (" — 아래 줄 포함" if len([r for r in rows if (r[1], next((x for x in next(cc for cc in _cd["cats"] if cc["n"] == r[1])["items"] if re.search(r[2], x[0])), None) and next((x for x in next(cc for cc in _cd["cats"] if cc["n"] == r[1])["items"] if re.search(r[2], x[0])))[0]) == key]) > 1 else "")
                if pr:
                    amt = pr * units; _tot += amt
                    money = f'약 {amt:,}원' + (f' <small class="muted">({bun}개 1단 {pr:,}원 × {units}단)</small>' if bun > 1 else f' <small class="muted">({pr:,}원 × {units})</small>')
                else:
                    money = "매장 문의"
            trs += f'<tr><th>{E(part)}</th><td data-l="자재·재단 크기">{E(desc)}</td><td data-l="필요 수량">{cnt}</td><td data-l="기준가 예상 금액">{money}</td></tr>'
            _ml.append(f"- {part}: {desc} / {re.sub(r'<[^>]+>', '', cnt)} / {re.sub(r'<[^>]+>', '', money)}")
            _pl.append((part, desc, re.sub(r'<[^>]+>', '', cnt)))
            btns += f'<a class="mkc" href="{cutlink(cat, rx, parts)}"><span>✂</span>{E(part)} 재단 그림</a>'
        try:
            import mkpdf as _mkp
            if _mkp.make(ROOT, slug, nm, title, lead, _pl, steps, mats, BASE): print("도면 PDF", slug)
        except Exception as _e: print("PDF 실패", slug, _e)
        _pdf = os.path.exists(f"{ROOT}/assets/mandeul/pdf/{slug}.pdf")
        if _pdf and not os.path.exists(f"{OUT}/assets/mandeul/pdf/{slug}.pdf"): os.makedirs(f"{OUT}/assets/mandeul/pdf", exist_ok=True); shutil.copy(f"{ROOT}/assets/mandeul/pdf/{slug}.pdf", f"{OUT}/assets/mandeul/pdf/{slug}.pdf")
        _pdfb = f'<a class="mkpdf" href="/assets/mandeul/pdf/{slug}.pdf" download="{nm}_도면_영진종합목재.pdf"><i>PDF</i><span><b>무료 도면 받기</b><small>완성 그림·재단 목록·순서 · A4 인쇄용</small></span><u>⬇</u></a>' if _pdf else ""
        body = f"""<section class="wrap sec"><p class="crumb"><a href="/mandeul/">DIY 만들기</a> › {E(nm)}</p><h1>{E(title.split(" — ")[0])}</h1><p class="lead">{E(lead)}</p>
{_hero}<div class="tw"><table class="rt"><thead><tr><th>부분</th><th>자재·재단 크기</th><th>필요 수량</th><th>기준가 예상 금액</th></tr></thead><tbody>{trs}</tbody></table></div>
{f'<div class="est"><b>예상 자재비 약 {_tot:,}원</b><span>소매 기준가 기준 · 부가세 별도 · 피스·철물·마감재 제외 · <a href="/cut.html#fee">재단비</a> 1컷 1,000원~(두께별) · 운임은 매장에서 계산 · 가격은 바뀔 수 있어요</span></div>' if _tot else ''}
<p class="small muted">톱날 3mm를 빼고 계산했습니다. 크기를 바꾸고 싶으면 아래 재단 그림에서 숫자만 고치세요.</p><div class="mkact"><div class="mkcut">{btns}</div>{_pdfb}<div class="mkcta"><a class="b r" href="mailto:{EMAIL}?subject={quote(nm + ' 재단·견적 요청')}&amp;body={quote('안녕하세요. 아래 목록대로 재단·견적 부탁드립니다.' + chr(10) + chr(10) + nm + ' (' + BASE + '/mandeul/' + slug + '.html)' + chr(10) + chr(10).join(_ml) + chr(10) + (f'예상 자재비(기준가): 약 {_tot:,}원' if _tot else '') + chr(10) + chr(10) + '수량·크기 변경:' + chr(10) + '이름:' + chr(10) + '연락처:' + chr(10) + '방문(또는 배송) 희망일:' + chr(10))}">✉ 이 목록으로 재단·견적 요청</a><a class="b d" href="tel:{TEL.replace('-', '')}">전화 문의</a></div></div></section>
{_gal}{_stp}<section class="wrap sec g2"><div class="card"><h2>만드는 순서</h2>{_steps(steps)}</div>
<div class="card"><h2>준비할 자재</h2><ul class="mli">{MI.mk_list(mats, rows, steps)}</ul><p class="hsh">옆으로 넘겨 보세요 ›</p><h3>필요한 공구</h3><ul class="mli">{MI.mk_tools(mats, rows, steps)}</ul><p class="hsh">옆으로 넘겨 보세요 ›</p><p class="small muted">피스 길이는 고정할 판 두께의 약 2~2.5배 기준 참고치입니다. 매장에서 실물 보고 맞춰 드려요.</p><p>매장({ADDR})에서 위 크기대로 즉석 재단해 드립니다. 이 페이지를 보여주시면 됩니다.</p></div></section>
{(f'<section class="wrap sec"><h2>{E(nm)} 만들기 영상</h2>' + embed(_mv[0]) + vsplit(_mv[1:], "h3") + '</section>') if _mv else ''}<!--MKFAQ--><section class="wrap sec"><p class="small muted">© 영진종합목재(월드건축자재). 이 페이지의 완성 그림·그림 설명서·재단표는 영진종합목재가 직접 만든 저작물입니다. 무단 복제·배포·상업적 사용을 금합니다(링크 공유는 환영합니다).</p></section><section class="wrap sec">{_gg0.links([p for r_ in rows for p in _gg0.BYCAT.get(r_[1], [])])}<h2>다른 만들기</h2><div class="olk">{"".join(f'<a href="/mandeul/{x[0]}.html">{E(x[1])}</a>' for x in MK if x[0] != slug)}<a class="ac" href="/cut.html">✂ 재단 미리보기</a><a class="ac" href="/calc.html">🧮 자재 계산기</a></div><p class="hsh olh">옆으로 넘겨 보세요 ›</p></section>{CTA}"""
        _qa = []
        if _tot: _qa.append((f"{nm} 만들려면 자재비가 얼마나 드나요?", f"이 페이지의 크기 기준으로 소매 기준가 약 {_tot:,}원입니다(부가세 별도, 피스·철물·마감재 제외). 크기를 바꾸면 재단 그림 페이지에서 다시 계산됩니다."))
        _qa.append((f"{nm} 만들 때 어떤 자재가 필요한가요?", ", ".join(mats) + "가 필요합니다. 부분별 재단 크기와 수량은 위 표에 있습니다."))
        _qa.append((f"{nm} 자재를 원하는 크기로 재단해 주나요?", f"네. 대전 {ADDR} 영진종합목재에서 표의 크기대로 즉석 재단해 드립니다. 한 개 소량도 됩니다."))
        _qa.append(("지방에서도 자재를 받을 수 있나요?", "대전·세종·공주·계룡·논산·금산·옥천은 배송하고, 그 외 전국은 용달로 보내 드립니다(운임 견적 후 출고)."))
        body = body.replace("<!--MKFAQ-->", f'<section class="wrap sec"><h2>{E(nm)} 자주 묻는 질문</h2>' + faqslide(_qa) + '</section>')
        fq = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a_}} for q, a_ in _qa]
        ALLFAQ.append(("DIY 만들기", _qa[:2], f"/mandeul/{slug}.html", nm))
        page(f"mandeul/{slug}.html", f"{nm} 만들기 — 재단 크기·" + (f"예상 자재비 약 {_tot:,}원" if _tot else "필요한 자재") + " | 영진목재", (f"{nm} 만들기 자재비 약 {_tot:,}원(기준가). " if _tot else "") + "재단 크기표·그림 설명서·영상. " + lead[:90], body, "/mandeul/", [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": fq}] + ([{"@context": "https://schema.org", "@type": "ImageObject", "contentUrl": BASE + f"/assets/mandeul/{slug}{sfx}.jpg", "name": f"{nm} " + ("완성 모습 그림" if not sfx else "만드는 순서 그림 설명서"), "creator": {"@type": "Organization", "name": "영진종합목재(월드건축자재)", "url": BASE + "/"}, "copyrightHolder": {"@type": "Organization", "name": "영진종합목재(월드건축자재)"}, "copyrightNotice": "© 영진종합목재(월드건축자재) www.wwood.co.kr", "creditText": "영진종합목재", "license": BASE + "/mandeul/", "acquireLicensePage": BASE + "/visit.html"} for sfx in ([""] if _hi else []) + (["-steps"] if _si else [])]), (BASE + f"/assets/mandeul/{slug}.jpg") if _hi else (f"https://i.ytimg.com/vi/{_mv[0]['id']}/hqdefault.jpg" if _mv else None))
        mk_cards += f'<a class="mc" href="/mandeul/{slug}.html">' + (f'<img loading="lazy" src="/assets/mandeul/{slug}.jpg" alt="{E(nm)}" style="width:100%;height:auto;border-radius:8px;margin-bottom:6px">' if _hi else "") + f'<b>{E(nm)}</b><small>{E(lead[:40])}…</small><span hidden>{E(" ".join(r[1] + " " + r[4] for r in rows) + " " + " ".join(mats) + " " + lead)}</span></a>'
    # 자재 백과 ↔ 만들기 연결: 자재 페이지에 "이 자재로 만들 수 있는 것"
    MATKW = {"hapan": r"합판", "osb": r"OSB", "mdf": r"MDF", "gujo": r"구조재", "bangbu": r"방부목", "jipseong": r"집성판", "gypsum": r"석고보드",
             "insul": r"아이소핑크|단열재", "stain": r"스테인|오일|바니시", "hardware": r"피스|철물|브라켓|경첩|앵커", "hapdeck": r"합성데크"}
    _mkmat = {}
    for x in MK:
        tx = " ".join(r[1] + " " + r[4] for r in x[4]) + " " + " ".join(x[6])
        for ms, rx in MATKW.items():
            if re.search(rx, tx): _mkmat.setdefault(ms, []).append(x)
    MKMAT_HTML = {ms: f'<section class="wrap sec"><h2>이 자재로 만들 수 있는 것</h2><p class="small muted">재단 크기·수량과 만드는 순서, 만들기 영상까지 정리했습니다. 매장에서 그 크기대로 잘라 드려요.</p><div class="mg m2">'
                  + "".join(f'<a class="mc" href="/mandeul/{x[0]}.html"><b>{E(x[1])}</b><small>{E(x[3][:40])}…</small></a>' for x in xs[:12]) + '</div></section>' for ms, xs in _mkmat.items()}
    import gagyeok as _gg
    GGLIST = _gg.gen(page, P, E, CTA, prod_ld, faqslide, BASE, ADDR, HOURS, TEL, ALLFAQ, mat_photos)
    import gyeonjeok as _gj
    _gj.gen(page, P, E, CTA, faqslide, TEL)
    _gj.gen2(page, E, CTA, faqslide, TEL)
    _gj.gen3(page, P, E, CTA, faqslide, TEL)
    import mirigi as _mr
    _mr.gen(page, P, E, CTA, faqslide, TEL, PROD, ROOT)
    import yesi as _ys; _ys.gen(page, P, E, CTA, faqslide, TEL)
    import yeongyeol as _yg; _yg.gen(page, E, CTA, faqslide, TEL, ROOT)
    import hyeonjang as _hj; _hj.gen(page, E, CTA, TEL)
    import gongjeong as _gjp; _gjp.gen(page, E, CTA, TEL)
    import tteori as _tt; _tt.gen(page, E, CTA, TEL, ADDR, HOURS, BASE, ROOT)
    import qrposter as _qrp; _qrp.gen(OUT)
    import specpg as _spg; _spg.gen(page, P, E, CTA, faqslide, TEL); _spg.gen2(page, P, E, CTA, faqslide, TEL); _spg.gen3(page, P, E, CTA, faqslide, TEL); _spg.gen4(page, P, E, CTA, faqslide, TEL)
    import muge as _mg; _mg.gen(page, E, CTA, faqslide, TEL)
    import mokgongso as _mgs; _mgs.gen(page, E, CTA, faqslide, TEL, ADDR, HOURS)
    import unit as _un; _un.gen(page, E, CTA, faqslide, TEL)
    # 가격 가이드·자재 백과 → 평수별 예시 링크(같은 자재끼리)
    _YK = {"gagyeok/deck-gagyeok": "데크", "gagyeok/hinoki-ruba": "루바", "gagyeok/spruce-ruba": "루바", "gagyeok/seokgo-gagyeok": "석고보드",
           "gagyeok/tempa-board": "템바보드", "gagyeok/siding-gagyeok": "사이딩", "gagyeok/hapan-gagyeok": "합판", "gagyeok/danyeol-gagyeok": "단열재",
           "jajae/bangbu": "데크", "jajae/hapdeck": "데크", "jajae/hinoki": "루바", "jajae/gypsum": "석고보드", "jajae/siding": "사이딩",
           "jajae/hapan": "합판", "jajae/insul": "단열재", "nichiha/index": "사이딩", "deck-gyesan": "데크", "gabyeok-gyesan": "석고보드"}
    for _k in ("gagyeok/hapan-gagyeok", "gagyeok/osb-gagyeok", "gagyeok/mdf-gagyeok", "gagyeok/jipseong-gagyeok", "gagyeok/seokgo-gagyeok", "gagyeok/gakjae-gagyeok", "gagyeok/deck-gagyeok", "jajae/hapan", "jajae/mdf", "jajae/osb", "jajae/jipseong", "baesong", "price"):
        _f = os.path.join(OUT, _k + ".html")
        if not os.path.exists(_f): continue
        _h = open(_f, encoding="utf-8").read()
        if "jfeebox" in _h: continue
        _box = '<section class="wrap sec jfeebox"><a class="jfb" href="/jaedan-bi.html"><b>✂ 원하는 크기로 재단</b><span>재단비 1컷 1,000원부터(12T 이하) · 15·18T 1,500원 · 30T까지 3,000원</span><u>재단비 보기 ›</u></a></section><style>.jfb{display:flex;flex-direction:column;gap:3px;background:#1D1B18;color:#fff!important;border-radius:16px;padding:14px 16px;text-decoration:none!important}.jfb b{font-size:16px}.jfb span{font-size:13px;opacity:.8}.jfb u{text-decoration:none;color:#ffd27a;font-weight:800;font-size:14px;margin-top:4px}</style>'
        _i = _h.rfind('<section class="wrap sec shr">')
        if _i < 0: _i = _h.rfind("</main>")
        if _i > 0: open(_f, "w", encoding="utf-8").write(_h[:_i] + _box + _h[_i:])
    for _k, _kind in _YK.items():
        _f = os.path.join(OUT, _k + ".html")
        _ls = [l for l in _ys.LINKS if l[0] == _kind]
        if not os.path.exists(_f) or not _ls: continue
        _h = open(_f, encoding="utf-8").read()
        if "ylinks" in _h: continue
        _box = ('<section class="wrap sec ylinks"><h2>' + E(_kind) + ' 몇 평이면 얼마? 평수별 자재비 예시</h2><div class="ylk">'
                + "".join(f'<a href="/yesi/{sl}.html"><b>{E(t)}</b><small>{lo:,}원~</small></a>' for _, sl, t, lo, hi in _ls)
                + '</div></section><style>.ylk{display:flex;gap:8px;overflow-x:auto;padding:2px 0 8px;scrollbar-width:none}.ylk a{flex:0 0 auto;display:flex;flex-direction:column;gap:2px;background:#fff;border:1px solid #ece6dc;border-radius:14px;padding:10px 14px;color:#1D1B18;text-decoration:none}.ylk b{font-size:14px}.ylk small{color:#c41a1f;font-weight:800;font-size:12.5px}</style>')
        _i = _h.rfind('<section class="wrap sec shr">')
        if _i < 0: _i = _h.rfind("</main>")
        if _i > 0: open(_f, "w", encoding="utf-8").write(_h[:_i] + _box + _h[_i:])
    import cheolmul as _ch
    CHLIST = _ch.gen(page, P, E, CTA, faqslide, BASE, ADDR, HOURS, ALLFAQ)
    import taka as _tk
    TKLIST = _tk.gen(page, P, E, CTA, faqslide, BASE, ADDR, HOURS, ALLFAQ)
    import yerim as _yr
    YRLIST = _yr.gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT, ALLFAQ)
    import younglim as _yl
    YLLIST = _yl.gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT)
    import shenu as _shn
    SHLIST = _shn.gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT)
    import samik as _smk
    SMLIST = _smk.gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT)
    import knauf as _knf
    KNLIST = _knf.gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT)
    import homewood as _hwd
    HWLIST = _hwd.gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT)
    HWBR = _hwd.gen_brands(page, E, CTA, faqslide, ADDR, HOURS, ROOT)
    import nichiha as _nh
    NHLIST = _nh.gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT)
    import emall as _em
    EMLIST = _em.gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT)
    import cmbs as _cmb
    CBLIST = _cmb.gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT)
    import prodpg as _ppg
    def _pvid(ws):
        rx = re.compile("|".join(map(re.escape, ws)))
        vs = top(lambda v: rx.search(v["title"]) is not None, 6)
        return vsplit(vs, "h3") if vs else ""
    PPN = _ppg.gen(page, E, CTA, faqslide, HOURS, ROOT, _pvid)
    print("product pages:", PPN, "cat pages linked:", _ppg.inject(OUT, E))
    _fx = lambda t: html.escape(re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", str(t)))
    open(f"{OUT}/merchant-feed.xml", "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0"><channel><title>영진종합목재(월드건축자재)</title><link>' + BASE + '</link><description>건축자재·철물·도료</description>\n' + "".join(
        f'<item><g:id>{_fx(i)}</g:id><title>{_fx(t[:150])}</title><description>{_fx(dsc[:4900])}</description><link>{BASE}{u}</link><g:image_link>{_fx(im)}</g:image_link>'
        f'<g:availability>in_stock</g:availability><g:price>{p} KRW</g:price><g:condition>new</g:condition>' + (f'<g:brand>{_fx(br)}</g:brand>' if br else '<g:identifier_exists>no</g:identifier_exists>') + f'<g:product_type>{_fx(c)}</g:product_type></item>\n'
        for i, t, dsc, u, im, p, br, c in dict((x[0], x) for x in _ppg.FEED).values()) + '</channel></rss>\n')
    # 매장 재고(무료 로컬 등록정보) — 상품 정보(링크 없음) + 매장 재고(store_code, id, 재고, 가격)
    _STORE = "11962997655006403809"
    _fd = list(dict((x[0], x) for x in _ppg.FEED).values())
    open(f"{OUT}/merchant-local-products.xml", "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0"><channel><title>영진종합목재(월드건축자재) 매장 상품</title><link>' + BASE + '</link><description>매장 판매 건축자재·철물·도료</description>\n' + "".join(
        f'<item><g:id>{_fx(i)}</g:id><title>{_fx(t[:150])}</title><description>{_fx(dsc[:4900])}</description><g:image_link>{_fx(im)}</g:image_link>'
        f'<g:price>{p} KRW</g:price><g:condition>new</g:condition>' + (f'<g:brand>{_fx(br)}</g:brand>' if br else '<g:identifier_exists>no</g:identifier_exists>') + f'<g:product_type>{_fx(c)}</g:product_type></item>\n'
        for i, t, dsc, u, im, p, br, c in _fd) + '</channel></rss>\n')
    open(f"{OUT}/merchant-local-inventory.txt", "w", encoding="utf-8").write("store_code\tid\tavailability\tprice\tpickup_method\tpickup_sla\n" + "".join(f"{_STORE}\t{x[0]}\tin_stock\t{x[5]} KRW\tbuy\tsame_day\n" for x in _fd))
    import local as _lc
    LCLIST = _lc.gen(page, E, CTA, faqslide, ADDR, HOURS, TEL, ROOT, CASES, top, vsplit)
    import nation as _nt
    NTLIST = _nt.gen(page, E, CTA, faqslide, TEL, EMAIL, ADDR, HOURS, CASES, top, vsplit, P)
    import trend as _trd
    TRLIST = _trd.gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT)
    MKNM = {x[0]: x[1] for x in MK}
    # 자재 시공법(내장재·외장재·바닥·도어 등) — /sigongbeop/
    from sigong_data import SG, SGP
    _PROWS = [(r["name"], int(r["price"])) for r in csv.DictReader(open(ROOT + "/data/prices.csv", encoding="utf-8")) if r["price"].strip().isdigit()]
    def sgvids(rx):
        hit = [v for v in V if re.search(rx, v["title"])]
        hit.sort(key=lambda v: (0 if re.match(r"\W*(?:" + rx + ")", v["title"]) else 1 if re.search(rx, v["title"].split("|")[0]) else 2, 0 if v["type"] != "S" else 1, -v["n"]))
        return hit[:6]
    _mname = {m["slug"]: m["name"] for m in MATS}
    sg_cards = ""
    for slug, nm, title, lead, ex, rows, steps, tools, tips, ms, vrx in SG:
        _sv = sgvids(vrx)
        _hi = os.path.exists(f"{ROOT}/assets/sigongbeop/{slug}.jpg"); _si = os.path.exists(f"{ROOT}/assets/sigongbeop/{slug}-steps.jpg")
        hero = f'<figure class="mkfig"><img src="/assets/sigongbeop/{slug}.jpg" width="1200" height="800" alt="{E(nm)} 완성 모습 그림"><figcaption class="small muted">시공이 끝난 모습 그림</figcaption></figure>' if _hi else ""
        stp = f'<section class="wrap sec"><h2>{E(nm)} 순서 (그림 설명서)</h2><img class="mkfig" loading="lazy" src="/assets/sigongbeop/{slug}-steps.jpg" alt="{E(nm)} 순서 그림 설명서" style="width:100%;height:auto;border-radius:14px;border:1px solid #e6e0d4"><p class="small muted">빨간 테두리가 그 단계에서 새로 붙이는 부분입니다.</p></section>' if _si else ""
        trs = "".join(f'<tr><th>{E(a)}{MI.sg_links(a, b)}</th><td data-l="규격">{E(b) or "—"}</td><td data-l="예시 수량">{E(c)}</td></tr>' for a, b, c in rows)
        _ph = mat_photos(ms)[:10]
        _gal = (f'<section class="wrap sec"><h2>{E(_mname.get(ms, ""))} 실물 사진</h2><p class="small muted">매장에서 실제로 파는 제품 사진입니다. 누르면 상세 사진과 규격이 열립니다.</p><div class="pg hrow">' + "".join(pcard(q) for q in _ph) + '</div><p class="hsh">옆으로 밀어서 더 보기 ›</p></section>') if _ph else ""
        _el = []
        for lab, prx, q in SGP.get(slug, []):
            hit = next((pp for nn, pp in _PROWS if re.search(prx, nn)), None)
            if hit: _el.append((lab, hit, q))
        _est = ("<h3>기준가 예상 금액</h3><div class=\"tw\"><table class=\"rt\"><thead><tr><th>품목</th><th>기준가</th><th>수량</th><th>예상 금액</th></tr></thead><tbody>"
                + "".join(f'<tr><th>{E(l)}</th><td data-l="기준가">{p_:,}원</td><td data-l="수량">{q}</td><td data-l="예상 금액"><b>약 {p_ * q:,}원</b></td></tr>' for l, p_, q in _el)
                + f'</tbody></table></div><div class="est"><b>예상 자재비 약 {sum(p_ * q for l, p_, q in _el):,}원</b><span>위 품목만 더한 금액 · 소매 기준가 · 부가세 별도 · 표에 없는 품목(피스·본드·마감재 등)은 매장 문의 · 규격·길이·제품에 따라 달라져요</span></div>') if _el else ""
        body = f"""<section class="wrap sec"><p class="crumb"><a href="/sigongbeop/">자재 시공법</a> › {E(nm)}</p><h1>{E(title.split(" — ")[0])}</h1><p class="lead">{E(lead)}</p>{hero}
<h2>필요한 자재</h2><p class="small muted" style="margin:-4px 0 8px">예시: {E(ex)}</p><div class="tw"><table class="rt"><thead><tr><th>자재</th><th>규격</th><th>예시 수량</th></tr></thead><tbody>{trs}</tbody></table></div>
{_est}<p><a class="b r" href="mailto:{EMAIL}?subject={quote(nm + ' 자재 견적 요청')}&amp;body={quote('안녕하세요. ' + nm + ' 자재 견적 부탁드립니다.' + chr(10) + '(' + BASE + '/sigongbeop/' + slug + '.html)' + chr(10) + chr(10) + '시공할 곳 크기(가로×세로):' + chr(10) + chr(10) + chr(10).join(f'- {a}: {b} / {c}' for a, b, c in rows) + chr(10) + chr(10) + '이름:' + chr(10) + '연락처:' + chr(10) + '시공도 맡기실지(예/아니오):' + chr(10))}">✉ 내 크기로 자재 견적 요청</a> <a class="b d" href="tel:{TEL.replace('-', '')}">전화 문의</a></p><p class="small muted">수량은 예시 크기 기준 참고치입니다(로스 포함). 실제 크기를 알려 주시면 매장에서 다시 계산해 드리고, 원하는 크기로 재단해 드립니다. <a href="/calc.html">자재 계산기</a> · <a href="/jajae/{ms}.html">{E(_mname.get(ms, ""))} 용도·기준가</a></p>{_gg.links(_gg.BYMAT.get(ms, []))}</section>{_gal}{stp}
<section class="wrap sec g2"><div class="card"><h2>시공 순서</h2>{_steps(steps)}<h3>필요한 공구</h3><ul class="mli">{MI.sg_tools(tools)}</ul><p class="hsh">옆으로 넘겨 보세요 ›</p></div>
<div class="card"><h2>주의할 점</h2><ul>{"".join(f"<li>{E(t)}</li>" for t in tips)}</ul><p>자재는 매장({ADDR})에서 실물 보고 고를 수 있고, 시공이 어려우면 월드아키텍쳐(실내건축공사업 등록)에서 직접 시공합니다.</p></div></section>
{(f'<section class="wrap sec"><h2>{E(nm)} 영상</h2>' + embed(_sv[0]) + vsplit(_sv[1:], "h3") + '</section>') if _sv else ''}
<!--SGFAQ--><section class="wrap sec"><p class="small muted">© 영진종합목재(월드건축자재). 이 페이지의 그림·그림 설명서·자재표는 영진종합목재가 직접 만든 저작물입니다. 무단 복제·배포·상업적 사용을 금합니다(링크 공유는 환영합니다).</p><h2>다른 시공법</h2><div class="olk">{"".join(f'<a href="/sigongbeop/{x[0]}.html">{E(x[1])}</a>' for x in SG if x[0] != slug)}<a class="ac" href="/mandeul/">🔨 만들기 자재</a></div><p class="hsh olh">옆으로 넘겨 보세요 ›</p></section>{CTA}"""
        _sq = []
        if _el: _sq.append((f"{nm} 자재비는 얼마나 드나요?", f"예시({ex}) 기준으로 확인된 품목만 더하면 소매 기준가 약 {sum(p_ * q for l, p_, q in _el):,}원입니다(부가세 별도). 실제 크기를 알려 주시면 다시 계산해 드립니다."))
        _sq.append((f"{nm}에 어떤 자재가 필요한가요?", ", ".join(a for a, b, c in rows) + "가 필요합니다. 규격과 예시 수량은 위 표에 있습니다."))
        _sq.append((f"{nm} 시공도 맡길 수 있나요?", "네. 월드아키텍쳐(실내건축공사업 등록)가 대전·세종에서 직접 시공합니다. 전화 042-545-2900으로 문의하세요."))
        _sq.append(("자재를 원하는 크기로 잘라 주나요?", f"네. 대전 {ADDR} 매장에서 원하는 크기로 재단해 드리고, 전국 용달 배송도 됩니다."))
        ALLFAQ.append(("자재 시공법", _sq[:3], f"/sigongbeop/{slug}.html", nm))
        body = body.replace("<!--SGFAQ-->", f'<section class="wrap sec"><h2>{E(nm)} 자주 묻는 질문</h2>' + faqslide(_sq) + '</section>')
        ld = [{"@context": "https://schema.org", "@type": "HowTo", "name": title.split(" — ")[0], "description": lead,
               "supply": [{"@type": "HowToSupply", "name": a} for a, b, c in rows], "tool": [{"@type": "HowToTool", "name": t} for t in tools],
               "step": [{"@type": "HowToStep", "position": k + 1, "text": t} for k, t in enumerate(steps)]}, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a_}} for q, a_ in _sq]}]
        if _hi: ld[0]["image"] = BASE + f"/assets/sigongbeop/{slug}.jpg"
        ld += [{"@context": "https://schema.org", "@type": "ImageObject", "contentUrl": BASE + f"/assets/sigongbeop/{slug}{sfx}.jpg", "name": nm + (" 완성 그림" if not sfx else " 그림 설명서"), "creator": {"@type": "Organization", "name": "영진종합목재(월드건축자재)"}, "copyrightNotice": "© 영진종합목재(월드건축자재) www.wwood.co.kr", "creditText": "영진종합목재", "license": BASE + "/sigongbeop/", "acquireLicensePage": BASE + "/visit.html"} for sfx in ([""] if _hi else []) + (["-steps"] if _si else [])]
        page(f"sigongbeop/{slug}.html", title.split(" — ")[0] + (f" — 순서·필요 자재·예상 자재비 약 {sum(p_ * q for l, p_, q in _el):,}원" if _el else " — 순서·필요 자재·공구") + " | 영진목재", (f"{nm} 예상 자재비 약 {sum(p_ * q for l, p_, q in _el):,}원(기준가). " if _el else "") + "순서 그림 설명서·공구·주의점. " + lead[:90], body, "/sigongbeop/", ld, (BASE + f"/assets/sigongbeop/{slug}.jpg") if _hi else (f"https://i.ytimg.com/vi/{_sv[0]['id']}/hqdefault.jpg" if _sv else None))
        sg_cards += f'<a class="mc" href="/sigongbeop/{slug}.html">' + (f'<img loading="lazy" src="/assets/sigongbeop/{slug}.jpg" alt="{E(nm)}" style="width:100%;height:auto;border-radius:8px;margin-bottom:6px">' if _hi else "") + f'<b>{E(nm)}</b><small>{E(lead[:40])}…</small><span hidden>{E(lead + ' ' + ' '.join(a + ' ' + b for a, b, c in rows) + ' ' + _mname.get(ms, ''))}</span></a>'
    # 방문자가 사진 찍어 올린 도면(가구 만들기·자재 시공법) — data/plan_visitor.json (Claude가 사진 확인 후 추가)
    _PL2CSS = re.search(r"\.pl2\{.*?@media print\{.*?\}\}", open(ROOT + "/sajin_tpl.html", encoding="utf-8").read()).group(0)
    _VPL = json.load(open(ROOT + "/data/plan_visitor.json", encoding="utf-8")) if os.path.exists(ROOT + "/data/plan_visitor.json") else []
    _VPH = {"mandeul": "", "sigong": ""}
    for _v in _VPL:
        _dir = "mandeul" if _v["k"] == "mandeul" else "sigongbeop"; _pid = "v-" + _v["id"]; _who = _v.get("who") or "방문자"
        _img = _v.get("img", ""); _nm = _v.get("name", "방문자 도면")
        _st = "".join(f"<li>{E(x)}</li>" for x in _v.get("steps", []))
        _bd = (f'<section class="wrap sec"><p class="crumb"><a href="/{_dir}/">{"DIY 만들기" if _dir == "mandeul" else "자재 시공법"}</a> › 방문자 도면</p><h1>{E(_nm)}</h1><p class="lead">{E(_v.get("lead", ""))}</p><p class="small muted">{E(_who)}님이 사진을 올려 주셨고, 사진을 보고 도면 초안을 그렸어요. 치수를 바꾸면 도면·재단 목록이 바로 바뀝니다.</p>'
               + (f'<figure class="mkfig"><img src="{E(_img)}" alt="{E(_nm)} — {E(_who)}님 사진" style="width:100%;height:auto;border-radius:14px"><figcaption class="small muted">사진: {E(_who)}님 제공</figcaption></figure>' if _img else "")
               + '<div class="pl2" id="pl2"><h2>도면 (정면·측면)</h2><div class="pl2in"><label>가로<input type="number" id="plw"></label><label id="pld0">' + ("세로" if _v["k"] == "sigong" else "깊이") + '<input type="number" id="pld"></label><label id="plh0">높이<input type="number" id="plh"></label><label id="pls0">선반<input type="number" id="pls"></label><span>mm</span></div><div class="pl2d" id="pl2svg"></div><h3>재단 목록 · 필요한 자재</h3><div id="pl2tb"></div><div class="pl2b"><button type="button" class="pl2pdf" id="pl2pdf">PDF로 저장</button></div></div>'
               + (f'<h2>{"만드는" if _v["k"] == "mandeul" else "시공"} 순서</h2><ol>{_st}</ol>' if _st else f'<h2>{"만드는" if _v["k"] == "mandeul" else "시공"} 방법</h2><ol class="pl2st" id="pl2st"></ol>') + f'<h2>{"만드는" if _v["k"] == "mandeul" else "시공"} 순서 (그림 설명서)</h2><div id="pl2iso"></div>'
               + f'<p><a class="sjgo" href="/sajin.html?m={_v["k"]}"><span><b>나도 사진 찍어서 도면 받기</b><small>찍으면 바로 도면·재단 목록이 나와요</small></span><u aria-hidden="true">›</u></a></p></section>'
               + '<script src="/assets/plan2d.js"></script><script>(function(){var P=PL2,p=' + json.dumps(_v["plan"]) + ',g=function(i){return document.getElementById(i)};function draw(){var t=P.T[p.t];g("pld0").style.display=(t.k=="sigong"&&p.t.charAt(0)=="w")?"none":"";g("plh0").style.display=(t.k=="sigong"&&p.t.charAt(0)!="w")?"none":"";g("pls0").style.display=t.s?"":"none";g("plw").value=p.w;g("pld").value=p.d;g("plh").value=p.h;g("pls").value=p.s||0;g("pl2svg").innerHTML=P.svg(p);g("pl2tb").innerHTML=P.table(p);var o=g("pl2st");if(o)o.innerHTML=P.steps(p).map(function(x){return"<li>"+x+"</li>"}).join("");var q=g("pl2iso");if(q)q.innerHTML=P.iso(p,0)}["plw","pld","plh","pls"].forEach(function(i){g(i).onchange=function(){p[{plw:"w",pld:"d",plh:"h",pls:"s"}[i]]=Math.max(i=="pls"?0:50,Math.min(20000,Math.round(+g(i).value||0)));draw()}});g("pl2pdf").onclick=function(){document.body.classList.add("pl2print");print();setTimeout(function(){document.body.classList.remove("pl2print")},500)};draw()})()</script>'
               + '<style>' + _PL2CSS + '</style>')
        page(f"{_dir}/{_pid}.html", f"{_nm} — 방문자 사진으로 그린 도면·재단 목록 | 영진목재", f"{_nm}: {_who}님이 올린 사진을 보고 그린 도면(정면·측면), 재단 목록, 필요한 자재와 기준가 링크. PDF로 저장할 수 있어요.", _bd, "/" + _dir + "/", img=_img or None)
        _VPH[_v["k"]] += f'<a class="mc" href="/{_dir}/{_pid}.html">' + (f'<img loading="lazy" src="{E(_img)}" alt="" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;margin-bottom:6px">' if _img else "") + f'<b>{E(_nm)}</b><small>{E(_who)}님 · 도면·재단 목록</small></a>'
    for _k in _VPH:
        if _VPH[_k]: _VPH[_k] = '<h2 style="margin-top:22px">방문자가 올린 도면</h2><div class="mg m2">' + _VPH[_k] + '</div>'
    page("sigongbeop/index.html", "자재 시공법 — 석고보드·루바·사이딩·몰딩·강마루·필름·문 교체 셀프 시공 | 영진목재", "석고보드 벽, 루바 천장, 외벽 사이딩, 몰딩·걸레받이, 강마루, 템바보드, 흡음판, 합성데크, 방문 교체, 필름, 오일스테인, OSB 벽 시공 방법을 자재 수량·그림 설명서·영상으로 정리했습니다.",
         f'<section class="wrap sec"><h1>자재 시공법</h1><p class="lead">내장재·외장재·바닥재·도어를 직접 시공하는 순서를 자재 수량, 그림 설명서, 영상으로 정리했습니다. 자재는 매장에서 원하는 크기로 잘라 드리고, 어려운 공사는 직접 시공도 합니다.</p><a class="sjgo" href="/sajin.html?m=sigong"><i aria-hidden="true"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8.5A2.5 2.5 0 0 1 6.5 6h1.6l1.3-1.8A1.5 1.5 0 0 1 10.6 3.5h2.8a1.5 1.5 0 0 1 1.2.7L15.9 6h1.6A2.5 2.5 0 0 1 20 8.5v8A2.5 2.5 0 0 1 17.5 19h-11A2.5 2.5 0 0 1 4 16.5z"/><circle cx="12" cy="12.3" r="3.4"/></svg></i><span><b>사진 찍으면 시공법 찾기</b><small>벽·바닥·문·데크 사진으로 어떤 자재로 어떻게 시공하는지</small></span><u aria-hidden="true">›</u></a>{_VPH["sigong"]}<div class="gsrch"><span>🔍</span><input id="sgq" type="search" placeholder="시공법 검색 (예: 석고보드, 사이딩, 마루, 문)" autocomplete="off" aria-label="검색"></div><p id="sgqn" class="small muted" style="margin:-4px 0 8px"></p><div class="mg m2" id="sgqg">{sg_cards}</div><script>(function(){{var q=document.getElementById("sgq"),n=document.getElementById("sgqn"),C=[].slice.call(document.querySelectorAll("#sgqg .mc"));function f(){{var v=q.value.replace(/\\s/g,"").toLowerCase(),k=0;C.forEach(function(c){{var ok=!v||c.textContent.replace(/\\s/g,"").toLowerCase().indexOf(v)>=0;c.style.display=ok?"":"none";if(ok)k++}});n.textContent=v?(k?k+"개 찾음":"찾는 게 없어요. 매장에 물어보세요."):""}}q.addEventListener("input",f)}})();</script><p><a class="b o" href="/mandeul/">가구·소품 만들기 자재 보기 ›</a></p></section>{CTA}', "/sigongbeop/")
    SGMAT_HTML = {}
    for x in SG:
        SGMAT_HTML.setdefault(x[9], []).append(x)
    SGMAT_HTML = {k: '<section class="wrap sec"><h2>시공법</h2><div class="mg m2">' + "".join(f'<a class="mc" href="/sigongbeop/{x[0]}.html">' + (f'<img loading="lazy" src="/assets/sigongbeop/{x[0]}.jpg" alt="{E(x[1])}" style="width:100%;height:auto;border-radius:8px;margin-bottom:6px">' if os.path.exists(f"{ROOT}/assets/sigongbeop/{x[0]}.jpg") else "") + f'<b>{E(x[1])}</b><small>자재 수량·그림 설명서·영상</small></a>' for x in v) + '</div></section>' for k, v in SGMAT_HTML.items()}
    page("mandeul/index.html", "만들기 자재 목록 — 평상·책장·침대·신발장·작업대·데크·개집 재단 크기 | 영진목재", "평상, 책장, 신발장, 침대 프레임, 작업대, 벤치, 베란다 선반, 벽 단열, 데크, 가벽, 울타리, 테이블, 강아지집을 만들 때 필요한 자재와 재단 크기를 정리했습니다. 재단 그림까지 바로 확인하세요.",
         f'<section class="wrap sec"><h1>DIY 만들기</h1><p class="lead">자주 만드는 것들의 자재와 재단 크기를 정리했습니다. 크기만 바꿔서 재단 그림으로 확인하고, 매장에 보여주시면 그대로 잘라 드려요.</p><p class="small"><b>모든 만들기는 무료 도면 PDF</b>(완성 그림·재단 목록·순서 그림, A4 인쇄용)를 받을 수 있습니다 — 각 페이지의 <b>⬇ 무료 도면 PDF</b> 버튼.</p><a class="sjgo" href="/sajin.html?m=mandeul"><i aria-hidden="true"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8.5A2.5 2.5 0 0 1 6.5 6h1.6l1.3-1.8A1.5 1.5 0 0 1 10.6 3.5h2.8a1.5 1.5 0 0 1 1.2.7L15.9 6h1.6A2.5 2.5 0 0 1 20 8.5v8A2.5 2.5 0 0 1 17.5 19h-11A2.5 2.5 0 0 1 4 16.5z"/><circle cx="12" cy="12.3" r="3.4"/></svg></i><span><b>사진 찍으면 만드는 법 찾기</b><small>가구·소품 사진으로 비슷한 만들기의 도면·재단 크기·자재</small></span><u aria-hidden="true">›</u></a>{_VPH["mandeul"]}<div class="gsrch"><span>🔍</span><input id="mkq" type="search" placeholder="만들 것 검색 (예: 책장, 데크, 방부목, 집성판)" autocomplete="off" aria-label="검색"></div><p id="mkqn" class="small muted" style="margin:-4px 0 8px"></p><div class="mg m2" id="mkqg">{mk_cards}</div><script>(function(){{var q=document.getElementById("mkq"),n=document.getElementById("mkqn"),C=[].slice.call(document.querySelectorAll("#mkqg .mc"));function f(){{var v=q.value.replace(/\\s/g,"").toLowerCase(),k=0;C.forEach(function(c){{var ok=!v||c.textContent.replace(/\\s/g,"").toLowerCase().indexOf(v)>=0;c.style.display=ok?"":"none";if(ok)k++}});n.textContent=v?(k?k+"개 찾음":"찾는 게 없어요. 매장에 물어보세요."):""}}q.addEventListener("input",f)}})();</script></section><section class="wrap sec"><div class="card"><h2>직접 만드신 작품을 보내 주세요</h2><p>영진종합목재 자재로 만든 평상·선반·데크·가구 사진을 메일로 보내 주시면 이 페이지 「손님이 만든 작품」에 소개해 드립니다(이름은 원하시는 대로, 얼굴·주소가 나온 사진은 빼고 올립니다).</p><p><a class="b r" href="mailto:{EMAIL}?subject=%EC%9E%91%ED%92%88%20%EC%82%AC%EC%A7%84%20%EB%B3%B4%EB%83%85%EB%8B%88%EB%8B%A4&body=%EB%A7%8C%EB%93%A0%20%EA%B2%83%3A%0A%EC%93%B4%20%EC%9E%90%EC%9E%AC%3A%0A%EC%86%8C%EA%B0%9C%ED%95%A0%20%EC%9D%B4%EB%A6%84(%EB%8B%89%EB%84%A4%EC%9E%84)%3A%0A">작품 사진 메일로 보내기</a></p></div></section>{CTA}', "/mandeul/")
    # 목재·합판 재단비 안내(/jaedan-bi.html) — "합판 재단 비용", "목재 재단 가격" 검색용
    _FEE = [("12T 이하", 1000, "합판 4.8·8.5·11.5T, MDF 9T, 석고보드 9.5T 등"), ("15T·18T", 1500, "합판 15·17.5T, MDF 15·18T, 집성판 18T, OSB 18T 등"),
            ("20T 이하", 2000, "1×4 구조재(19T), 데크재 19·20T 등"), ("24T 이하", 2500, "집성판·원목 판재 24T 등"), ("30T 이하", 3000, "집성판 30T, 데크재 25T, 다루끼 30각 등")]
    _EX = [("4×8 합판 반으로(1220×1220 두 장)", 1), ("4×8 합판 4등분(610×1220 네 장)", 3), ("4×8 합판 선반 폭 300 여덟 장(300×1220)", 8), ("3×6 석고보드 반으로", 1), ("집성판 1장 책장 옆판 2장 + 선반 4장", 6)]
    _fe_rows = "".join(f'<tr><th>{t}</th><td data-l="1컷"><b>{f:,}원</b></td><td data-l="예">{E(e)}</td></tr>' for t, f, e in _FEE)
    _ex_rows = "".join(f'<tr><th>{E(n)}</th><td data-l="컷 수">약 {c}컷</td><td data-l="12T 이하">{c*1000:,}원</td><td data-l="15·18T">{c*1500:,}원</td><td data-l="30T 이하">{c*3000:,}원</td></tr>' for n, c in _EX)
    _jfq = [("합판 재단비는 얼마인가요?", "1컷(한 번 자르기)당 12T 이하 1,000원, 15T·18T 1,500원, 20T 이하 2,000원, 24T 이하 2,500원, 30T 이하 3,000원입니다(부가세 별도)."),
            ("2×4 구조재나 4×4 각재도 잘라 주나요?", "네, 잘라 드립니다. 30T가 넘는 두께(2×4·2×6·4×4 등)의 재단비는 전화로 문의해 주세요."),
            ("몇 컷인지 어떻게 알 수 있나요?", "재단 미리보기에 자재와 크기를 넣으면 원판에서 자르는 그림과 함께 컷 수, 재단비, 자재비 합계가 바로 나옵니다. 그 화면을 매장에 보여 주시면 그대로 잘라 드립니다."),
            ("재단해서 택배·용달로 보내 주나요?", "네. 원하는 크기로 재단한 뒤 대전·세종·공주·계룡·논산·금산·옥천은 배송, 그 밖의 지역은 전국 용달로 보내 드립니다(운임은 견적).")]
    _jld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in _jfq]}
    page("jaedan-bi.html", "합판·목재 재단비 — 두께별 1컷 1,000원부터, 컷 수 바로 계산 | 영진목재", "합판·MDF·집성판·OSB 재단비 1컷 1,000~3,000원(두께별, 부가세 별도). 4×8 합판 반·4등분 예시, 재단 미리보기로 컷 수·재단비 자동 계산. 대전 영진목재, 전국 배송.",
         f"""<section class="wrap sec"><p class="crumb"><a href="/cut.html">목재 재단</a> › 재단비</p><h1>합판·목재 재단비</h1>
<p class="lead">원하는 크기로 잘라 드립니다. 재단비는 <b>두께에 따라 1컷(한 번 자르기)당</b> 정해져 있어요. 정확한 컷 수와 금액은 <a href="/cut.html">재단 미리보기</a>에 크기를 넣으면 바로 나옵니다.</p>
<h2>두께별 1컷 재단비</h2><div class="tw"><table class="rt"><thead><tr><th>두께</th><th>1컷</th><th>이런 자재</th></tr></thead><tbody>{_fe_rows}<tr><th>30T 넘음</th><td data-l="1컷"><a href="tel:{TEL.replace('-', '')}">전화 문의</a></td><td data-l="예">2×4·2×6·4×4 구조재·각재 등</td></tr></tbody></table></div>
<p class="small muted">부가세 별도 · 18.3mm OSB처럼 소수점 두께는 가까운 두께로 봅니다.</p>
<h2>자주 하는 재단 예시</h2><div class="tw"><table class="rt"><thead><tr><th>재단</th><th>컷 수</th><th>12T 이하</th><th>15·18T</th><th>30T 이하</th></tr></thead><tbody>{_ex_rows}</tbody></table></div>
<p class="small muted">자르는 순서에 따라 컷 수가 조금 달라질 수 있어요. 내 크기는 아래 버튼으로 바로 계산하세요.</p>
<div class="yact"><a class="b r" href="/cut.html">재단 미리보기에서 컷 수·재단비 계산 ›</a><a class="b" href="/gagyeok/hapan-gagyeok.html">합판 가격</a><a class="b" href="/gagyeok/jipseong-gagyeok.html">집성판 가격</a><a class="b" href="/mandeul/">DIY 만들기 재단 목록</a><a class="b" href="/baesong.html">전국 배송</a></div>
<h2>자주 묻는 질문</h2>{faqslide(_jfq)}</section>{CTA}<style>.yact{{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}}.yact .b{{font-size:14px}}</style>""", "/cut.html", _jld)
    page("cut.html", "합판·MDF 재단 미리보기 — 원하는 사이즈 재단 그림 | 대전 영진목재", "합판·MDF·집성판·석고보드·구조재를 원하는 사이즈로 넣으면 원판에서 어떻게 잘리는지, 몇 장 필요한지 그림으로 보여드립니다. 대전 영진목재 즉석 재단.",
         open(ROOT + "/cut_tpl.html", encoding="utf-8").read().replace("__DATA__", json.dumps(_cd, ensure_ascii=False, separators=(",", ":"))).replace("__TELD__", TEL).replace("__TEL__", TEL.replace("-", "")).replace("__EMAIL__", EMAIL) + _seo + CTA, "/cut.html", _ld, BASE + "/assets/store/plywood-rack.jpg")
    try:
        import apt as _apt
        _APTP = _apt.build(ROOT, page, E, CTA); print("아파트 페이지", len(_APTP))
        os.makedirs(f"{OUT}/assets/apt", exist_ok=True)
        for _f in os.listdir(f"{ROOT}/assets/apt"): shutil.copy(f"{ROOT}/assets/apt/{_f}", f"{OUT}/assets/apt/{_f}")  # 빌드 중 새로 만든 검색 데이터·평면도 반영
    except Exception as _e: print("아파트 페이지 실패", _e)
    import embed as _em
    os.makedirs(f"{OUT}/embed", exist_ok=True)
    open(f"{OUT}/embed/jajae.html", "w", encoding="utf-8").write(_em.EMBED)
    page("widget.html", "자재 계산기 퍼가기 — 블로그·홈페이지에 무료로 붙이는 평수·장수 계산기 | 영진목재", "평수↔㎡, 합판·석고보드 장수, 데크재 개수를 계산하는 자재 계산기를 블로그·카페·홈페이지에 무료로 붙이세요. 코드 복사 한 번이면 됩니다.", _em.body(E) + CTA, "/calc.html")
    import doumi as _dm
    page("doumi.html", "셀프 인테리어 도우미 — 질문 4개로 시공법·자재·가격 한 번에 | 영진목재", "벽·바닥·천장·문·가구·단열·데크 중 하고 싶은 것을 고르면 필요한 시공법, 만들기 재단 목록, 자재 가격, 영상, 계산기를 순서대로 모아 드립니다. 대전 영진종합목재(월드건축자재).", _dm.body(E, ROOT) + CTA, "/doumi.html")
    page("calc.html", "자재 계산기 — 데크·석고보드·합판 몇 장? 문짝·중문 크기까지 | 영진목재", "데크 방부목·합성데크 장수, 석고보드·합판·단열재 장수, 몰딩·걸레받이 길이, 데코타일·강마루 박스 수, 페인트 양, 평↔㎡를 바로 계산하세요. 대전 영진목재(월드건축자재) 재단·배송.",
f"""<section class="wrap sec"><h1>자재 계산기</h1><p class="lead">필요한 양을 미리 계산해 오시면 매장에서 바로 재단해 드려요. 결과는 로스 포함 참고용입니다.</p>
<div class="ctl">
<a class="ct ctf" href="/mirigi.html"><i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/></svg></i><span><em>NEW</em><b>공사 미리보기</b><small>사진에 데크·루바·벽을 입혀 보고 예상 자재비까지</small></span><u>›</u></a>
<a class="ct" href="/gyeonjeok.html"><i style="background:#fdf1e3;color:#b4651c"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11l9-7 9 7v9H3z"/><path d="M9 20v-6h6v6"/></svg></i><span><b>방 통째로 계산</b><small>공정별 자재비 합계</small></span></a>
<a class="ct" href="/dobae-jangpan.html"><i style="background:#eaf2ec;color:#2f7a4a"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="13" height="7" rx="2"/><path d="M16 7.5h3v5h-7v3"/><rect x="10.5" y="15.5" width="3" height="5" rx="1"/></svg></i><span><b>도배·장판·타일</b><small>롤·m·장·페인트 L</small></span></a>
<a class="ct" href="/deck-gyesan.html"><i style="background:#f3ece4;color:#8a5a2b"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9h18M3 13h18M3 17h18"/><path d="M6 9v10M18 9v10"/></svg></i><span><b>데크 자재</b><small>데크재·장선·기둥</small></span></a>
<a class="ct" href="/gabyeok-gyesan.html"><i style="background:#e9eef6;color:#3b5b8c"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="1.5"/><path d="M10 4v16M4 10h6M4 15h6"/></svg></i><span><b>가벽 자재</b><small>각재·석고·단열</small></span></a>
<a class="ct" href="/pyeong.html"><i style="background:#eef3e6;color:#4a7a2c"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M4 12h16M12 4v16"/></svg></i><span><b>평수 계산기</b><small>평 ↔ ㎡ 바로 변환</small></span></a>
<a class="ct" href="/jae.html"><i style="background:#f6efe2;color:#9a6a2a"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8l8-4 8 4-8 4z"/><path d="M4 8v8l8 4 8-4V8"/></svg></i><span><b>목재 재 계산기</b><small>재 수·㎥ 계산</small></span></a>
<a class="ct ctw" href="/yesi/"><i style="background:#fdecec;color:#c41a1f"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg></i><span><b>평수별 자재비 예시</b><small>데크 3평·천장 루바 4평·농막 사이딩… 몇 평이면 얼마?</small></span></a>
</div>
<h2 class="cqh">빠른 계산</h2>
<div class="chips" id="cchips">{chips}</div>
<div class="cnav"><button class="cb" data-d="-1">◀ 이전</button><span id="cpos" class="small muted"></span><button class="cb" data-d="1">다음 ▶</button></div>
<div class="cslider" id="cslider">{slides}</div>
<h2 class="cfaq">자주 묻는 질문</h2>{faqslide(CALC_FAQ)}</section>
<style>.cslider{{display:flex;align-items:flex-start;transition:height .2s;overflow-x:auto;overflow-y:hidden;scroll-snap-type:x mandatory;gap:12px;scrollbar-width:none;-webkit-overflow-scrolling:touch}}.cslider::-webkit-scrollbar{{display:none}}.cslide{{flex:0 0 100%;scroll-snap-align:start}}.cslide .card{{margin:0;border-radius:18px;border:1px solid #ece6dc;box-shadow:0 2px 10px rgba(0,0,0,.04);padding:18px 16px}}.cslide h2{{font-size:19px;margin:0 0 4px}}.cnote{{display:flex;gap:8px;align-items:flex-start;margin:12px 0 0;padding:10px 12px;background:#f7f4ee;border-radius:12px;font-size:13px;color:#6b645a;line-height:1.5}}.cnote:before{{content:"i";flex:none;width:18px;height:18px;border-radius:50%;background:#d8d1c5;color:#fff;font-size:12px;font-weight:900;display:grid;place-items:center;font-style:italic}}.clk{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px}}.clc{{display:flex;align-items:center;gap:10px;padding:11px 12px;background:#fff;border:1px solid #ece6dc;border-radius:14px;color:#1D1B18!important;text-decoration:none!important;min-width:0}}.clc i{{flex:none;width:34px;height:34px;border-radius:10px;background:#f3ece4;color:#8a5a2b;display:grid;place-items:center}}.clc.v i{{background:#fdecec;color:#c41a1f}}.clc i svg{{width:18px;height:18px}}.clc span{{flex:1;min-width:0;display:flex;flex-direction:column}}.clc small{{font-size:11px;color:#8a8378;font-weight:700}}.clc b{{font-size:14.5px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.clc u{{text-decoration:none;color:#c9c1b5;font-size:18px}}.clk .clc:last-child:nth-child(odd){{grid-column:1/-1}}.cfaq{{margin:22px 0 10px;font-size:22px}}
.cnav{{display:flex;justify-content:space-between;align-items:center;margin:4px 0 10px}}.cb{{width:38px;height:38px;padding:0;border:1px solid #e6dfd5;border-radius:50%;background:#fff;font-size:0;cursor:pointer;position:relative}}.cb:before{{content:"‹";font-size:22px;line-height:36px;color:#1D1B18}}.cb[data-d="1"]:before{{content:"›"}}.cnav .small{{font-size:12.5px}}
#cchips{{display:flex;gap:6px;overflow-x:auto;flex-wrap:nowrap;padding:2px 0 6px;scrollbar-width:none}}#cchips::-webkit-scrollbar{{display:none}}#cchips .chip{{flex:0 0 auto;border:1px solid #e6dfd5;background:#fff;cursor:pointer;font-size:14px;font-weight:700;padding:9px 15px;border-radius:999px;color:#5c564d}}#cchips .chip.on{{background:#1D1B18;color:#fff;border-color:#1D1B18}}.ctl{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:16px 0 6px}}@media(min-width:760px){{.ctl{{grid-template-columns:repeat(4,1fr)}}.ctf{{grid-column:1/-1}}}}.ct{{display:flex;flex-direction:column;gap:10px;background:#fff;border:1px solid #ece6dc;border-radius:18px;padding:14px;text-decoration:none!important;color:#1D1B18!important;box-shadow:0 2px 10px rgba(0,0,0,.04);transition:transform .15s}}.ct:active{{transform:scale(.98)}}.ct i{{width:40px;height:40px;border-radius:12px;display:grid;place-items:center}}.ct i svg{{width:22px;height:22px}}.ct span{{display:flex;flex-direction:column;gap:3px}}.ct b{{font-size:15.5px;font-weight:800;letter-spacing:-.3px}}.ct small{{font-size:12.5px;color:#8a8378;line-height:1.4}}.ctf{{grid-column:1/-1;flex-direction:row;align-items:center;background:linear-gradient(135deg,#2a2520,#1D1B18);border:0;color:#fff!important;padding:16px}}.ctf i{{background:#c41a1f;color:#fff;flex:none;width:48px;height:48px;border-radius:14px}}.ctf span{{flex:1}}.ctf b{{font-size:17px}}.ctf small{{color:rgba(255,255,255,.65)}}.ctf em{{font-style:normal;font-size:10.5px;font-weight:900;color:#f5d27a;letter-spacing:.5px}}.ctf u{{text-decoration:none;font-size:24px;color:rgba(255,255,255,.5)}}.ctw{{grid-column:1/-1;flex-direction:row;align-items:center}}.ctw i{{flex:none}}.cqh{{font-size:18px;margin:22px 0 10px}}
.cg{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 10px;margin:10px 0}}@media(min-width:760px){{.cg{{grid-template-columns:repeat(4,minmax(0,1fr))}}}}.cg label{{display:flex;flex-direction:column;font-size:14px;font-weight:700;color:#5c564d;gap:6px}}.cg input,.cg select{{font-size:20px;font-weight:700;height:52px;padding:0 14px;border:1.5px solid #e0d9cd;border-radius:12px;width:100%;box-sizing:border-box;background:#fff;color:var(--ink)}}.cg select{{font-size:16px;appearance:none;-webkit-appearance:none;background:#fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8'%3E%3Cpath d='M1 1l5 5 5-5' fill='none' stroke='%238a8378' stroke-width='2'/%3E%3C/svg%3E") no-repeat right 14px center;padding-right:36px}}@media(max-width:759px){{.cg label:has(select){{grid-column:1/-1}}}}.cg input:focus,.cg select:focus{{border-color:var(--red);outline:none}}
.cr{{background:#faf8f4;border:1px solid #ece6dc;border-radius:16px;padding:4px 14px 14px;font-size:15px;line-height:1.5}}.crh{{margin:12px 0 2px;color:#8a8378;font-size:13.5px;font-weight:700}}.crw{{display:flex;align-items:center;gap:8px;padding:13px 0;border-bottom:1px solid #ece6dc;color:#1D1B18!important;text-decoration:none!important}}.crw span{{flex:1;min-width:0;font-weight:700;font-size:15.5px}}.crw b{{font-size:23px;font-weight:900;color:#c41a1f;letter-spacing:-.4px;white-space:nowrap}}.crw b small{{font-size:14px;font-weight:700;color:#1D1B18;margin-left:3px}}.crw i{{font-style:normal;color:#b5ada2;font-size:20px;margin-left:2px}}.crn{{color:#8a8378;font-size:12.5px;margin:8px 0 0}}.qb{{margin-top:14px;display:flex;flex-wrap:wrap;gap:6px}}.qb small{{width:100%;color:#8a8378;font-size:12.5px;font-weight:700}}.qb .qc{{padding:8px 13px;border-radius:999px;background:#fff;border:1px solid #e6dfd5;color:#1D1B18!important;font-size:13.5px;font-weight:700;text-decoration:none!important}}</style>
<script>
(function(){{var $=function(i){{return document.getElementById(i)}},v=function(i){{return parseFloat($(i).value)||0}},n=function(x){{return Math.ceil(x).toLocaleString()}};
var Q=function(t,k){{return '<a class="qc" href="/jaryo/?q='+encodeURIComponent(k||t)+'">'+t+'</a>'}};
var H=function(t){{return '<p class="crh">'+t+'</p>'}};
var R=function(l,v,u,k){{var lk=k!==0,o=lk?'<a class="crw" href="/jaryo/?q='+encodeURIComponent(k||l)+'">':'<div class="crw">';return o+'<span>'+l+'</span><b>'+v+'<small>'+(u||'')+'</small></b>'+(lk?'<i>›</i></a>':'</div>')}};
var N_=function(t){{return '<p class="crn">'+t+'</p>'}};
var B=function(a){{return '<div class="qb"><small>함께 필요한 것</small>'+a.map(function(x){{return Q(x[0],x[1])}}).join('')+'</div>'}};
var C={{
deck:function(){{var W=v('dw'),L=v('dl'),t=$('dt').value.split(','),bw=+t[0],bl=+t[1]/1000,J=+$('dj').value/1000,rows=Math.ceil(W/((bw+5)/1000)),per=Math.ceil(L/bl),boards=rows*per*1.1,joists=Math.floor(W/J)+1,jp=joists*L/3.6*1.1,sc=rows*per*joists/per*2*1.1;
 var dk=bw==140?'합성데크':'방부데크';return H('데크 면적 '+(W*L).toFixed(1)+'㎡ · '+(W*L/3.3058).toFixed(1)+'평')+R('데크재',n(boards),'장',dk)+R('장선 각재 3.6m',n(jp),'개','방부각재')+R('피스','약 '+n(sc),'개','피스')+B([['오일스테인','스테인'],['방부원주목','방부원주목'],['난간재','난간']])}},
gyp:function(){{var A=Math.max(0,v('gw')*v('gh')-v('go'));return H('시공 면적 '+A.toFixed(1)+'㎡')+R('석고보드',n(A/parseFloat($('gs').value)*(+$('gp').value)*1.1),'장')+B([['석고본드'],['피스'],['타카핀'],['목상 각재','각재']])}},
ply:function(){{return R('합판·OSB·MDF',n(v('pa')/parseFloat($('ps').value)*1.1),'장','합판')+B([['피스'],['타카핀'],['목공본드','본드']])}},
mol:function(){{var per=2*(v('mw')+v('ml'))*Math.max(1,v('mr')),k=$('mk').value,p=parseFloat($('mp').value),ce=per,ba=Math.max(0,per-0.9*v('md')),out=H('방 둘레 '+per.toFixed(1)+'m · '+p+'m 기준 · 로스 10%');
 if(k!='base')out+=R('천장몰딩',n(ce*1.1/p),'개','몰딩');if(k!='ceil')out+=R('걸레받이',n(ba*1.1/p),'개','몰딩');return out+B([['실타카핀','타카핀'],['실리콘'],['본드']])}},
flo:function(){{var b=v('fb')||1;return H('필요 면적 '+(v('fa')*parseFloat($('fl').value)).toFixed(1)+'㎡')+R('바닥재',n(v('fa')*parseFloat($('fl').value)/b),'박스','마루')+B([['걸레받이·몰딩','몰딩'],['본드']])}},
ins:function(){{return R('단열재(아이소핑크)',n(v('ia')/parseFloat($('is').value)*Math.max(1,v('il'))*1.1),'장','아이소핑크')+B([['우레탄폼','우레탄'],['아이소핑크본드','아이소핑크본드']])}},
door:function(){{var m=$('om').value,W=v('ow'),H_=v('oh'),F=v('of'),Nn=Math.max(1,v('on')),out='';
 if(m=='frame'){{var fw=W-10,fh=H_-5;out+=R('문틀 바깥',Math.round(fw)+' × '+Math.round(fh),'mm','문틀')+R('문틀 폭(벽 두께)',Math.round(v('od')),'mm',0);W=fw-2*F;H_=fh-F;out+=R('문틀 안쪽',Math.round(W)+' × '+Math.round(H_),'mm',0)}}
 var dw=W-v('os'),dh=H_-3-(+$('ot').value),hg=dh>2100?4:3;
 return H(Nn+'짝 기준')+out+R('문짝 크기',Math.round(dw)+' × '+Math.round(dh),'mm','도어')+R('경첩',hg*Nn,'개')+R('손잡이',Nn,'개')+(m=='frame'?R('문틀',Nn,'세트','문틀'):'')+B([['도어스토퍼'],['우레탄폼','우레탄'],['실리콘'],['피스']])}},
jungmun:function(){{var n_=+$('jt').value,W=v('jw'),H_=v('jh'),F=v('jf'),O=v('jo'),fw=W-10,fh=H_-5,iw=fw-2*F,ih=fh-F,pw=n_==1?(iw+O):(iw+(n_-1)*O)/n_;
 return R('프레임 바깥',Math.round(fw)+' × '+Math.round(fh),'mm','중문')+R('프레임 안쪽',Math.round(iw)+' × '+Math.round(ih),'mm',0)+R('문짝 '+n_+'장 · 1장 폭',Math.round(pw),'mm',0)+(n_==1?N_('원슬라이딩은 벽 쪽 여유 공간이 필요해요'):'')+B([['실리콘'],['우레탄폼','우레탄'],['피스']])}},
pnt:function(){{var L=v('ta')*Math.max(1,v('tc'))/(v('tr')||1);return R('페인트·스테인','약 '+L.toFixed(1),'L','스테인')+R('18L 통',n(L/18),'통',0)+R('4L 통',n(L/4),'통',0)+B([['붓·롤러','롤러'],['마스킹테이프','테이프']])}}
}};
Object.keys(C).forEach(function(k){{var s=$(k);s.querySelectorAll('input,select').forEach(function(e){{e.addEventListener('input',function(){{$(k+'r').innerHTML=C[k]();if(typeof fit=='function')fit()}})}});$(k+'r').innerHTML=C[k]()}});
$('yp').addEventListener('input',function(){{$('ym').value=(v('yp')*3.3058).toFixed(2)}});$('ym').addEventListener('input',function(){{$('yp').value=(v('ym')/3.3058).toFixed(2)}});
var sl=$('cslider'),ch=[].slice.call(document.querySelectorAll('#cchips .chip')),N=ch.length;
function cur(){{return Math.round(sl.scrollLeft/sl.clientWidth)}}
function fit(){{var c=sl.children[cur()];if(c)sl.style.height=c.offsetHeight+'px'}}
function upd(){{var i=cur();fit();ch.forEach(function(c,j){{c.classList.toggle('on',i==j)}});$('cpos').textContent=(i+1)+' / '+N+' · 옆으로 밀어서 넘기기';var a=ch[i];if(a)a.scrollIntoView({{block:'nearest',inline:'center'}})}}
function go(i){{i=Math.max(0,Math.min(N-1,i));sl.scrollTo({{left:i*sl.clientWidth,behavior:'smooth'}})}}
ch.forEach(function(c){{c.onclick=function(){{go(+c.dataset.i)}}}});document.querySelectorAll('.cnav .cb').forEach(function(b){{b.onclick=function(){{go(cur()+(+b.dataset.d))}}}});
sl.addEventListener('scroll',function(){{clearTimeout(sl._t);sl._t=setTimeout(upd,80)}},{{passive:true}});
var h=location.hash.slice(1);if(h){{var ix=[].slice.call(sl.children).findIndex(function(e){{return e.id==h}});if(ix>=0)setTimeout(function(){{sl.scrollLeft=ix*sl.clientWidth;upd()}},50)}}upd();window.addEventListener('resize',fit);
}})();
</script>{CTA}""", "/calc.html", faqld)

    _GRPN = [("판재(합판·MDF·OSB·집성)", {"hapan", "mdf", "osb", "jipseong"}), ("구조목·방부목·데크", {"gujo", "gakjae", "bangbu", "hapdeck"}),
             ("석고·단열·방음", {"gypsum", "insul", "sound"}), ("도어·중문", {"door"}), ("몰딩·필름·벽 마감", {"molding", "film"}), ("바닥·타일", {"maru", "tile"}),
             ("스테인·페인트·오일", {"stain"}), ("외장·루바", {"siding", "hinoki"}), ("철물·공구·부자재", {"hardware"})]
    def _grp_of(mats):
        for n_, st_ in _GRPN:
            if mats and mats[0] in st_: return n_
        for n_, st_ in _GRPN:
            if set(mats) & st_: return n_
        return "기타"
    def _swipe_rows(items, card):  # items: [(mats, ...)] → 분류별 옆으로 넘기는 줄
        g = {}
        for it in items: g.setdefault(_grp_of(it[0]), []).append(it)
        order = [n_ for n_, _ in _GRPN if n_ in g] + [k for k in g if k not in dict(_GRPN)]
        return "".join(f'<h2 class="gt"><span>{E(k)} <small style="font-size:14px">{len(g[k])}개</small></span><small>옆으로 넘겨 보세요 ›</small></h2><div class="pl hs">' + "".join(card(it) for it in g[k]) + '</div>' for k in order)
    # 자재 비교 (data/compare.json)
    CMP = json.load(open(f"{ROOT}/data/compare.json", encoding="utf-8"))
    matname2 = {m["slug"]: m["name"] for m in MATS}
    cmpnav = lambda cur: '<div class="pl hs">' + "".join(f'<a class="pc" href="/bigyo/{c["slug"]}.html"><small>자재 비교</small><b>{E(c["short"])}</b><span>{E(c["desc"][:60])}…</span></a>' for c in CMP if c["slug"] != cur) + '</div><p class="hsh">옆으로 밀어서 더 보기 ›</p>'
    def _jo(w, x, y):  # 받침 있으면 x, 없으면 y
        ch = re.sub(r"[^가-힣A-Za-z0-9]", "", re.sub(r"\(.*?\)", "", w))[-1:] or "가"
        if "가" <= ch <= "힣": return w + (x if (ord(ch) - 0xAC00) % 28 else y)
        return w + (x if ch.lower() in "lmnr0136789" else y)
    def _cfq(c):
        a, b = c["cols"][0], c["cols"][1]
        out = [(f"{_jo(a, '과', '와')} {b}의 차이는 무엇인가요?", c["concl"])]
        for r in c["rows"]:
            if r[0] in ("어울리는 곳", "어울리는 작업"):
                out.append((f"{_jo(a, '과', '와')} {_jo(b, '은', '는')} 각각 어디에 쓰나요?", f"{a}: {r[1]}. {b}: {r[2]}."))
        for r in c["rows"]:
            if r[0] in ("물", "물 흡수", "관리", "시공", "작업"):
                out.append((f"{_jo(a, '과', '와')} {b}, {_jo(r[0], '은', '는')} 어떻게 다른가요?", f"{_jo(a, '은', '는')} {r[1]}, {_jo(b, '은', '는')} {r[2]}.")); break
        out += [tuple(x) for x in c.get("faq", [])]
        out.append(("매장에서 실물을 볼 수 있나요?", "대전 유성구 영진종합목재(월드건축자재) 매장에서 실물을 비교해 보실 수 있고, 원하는 크기로 재단해 전국 배송도 합니다. 전화 문의 후 방문하시면 편합니다."))
        return out
    for c in CMP:
        th = "<tr><th></th>" + "".join(f"<th>{E(x)}</th>" for x in c["cols"]) + "</tr>"
        tb = "".join("<tr><th>" + E(r[0]) + "</th>" + "".join(f"<td>{E(x)}</td>" for x in r[1:]) + "</tr>" for r in c["rows"])
        vs = top(lambda v, kw=c["kw"]: re.search(kw, v["title"]) is not None, 8)
        ml = " · ".join(f'<a href="/jajae/{m}.html">{matname2[m]} 용도·기준가</a>' for m in c["mats"] if m in matname2)
        page(f"bigyo/{c['slug']}.html", c["title"] + " | 영진목재", c["desc"],
             f"""<section class="wrap sec"><p class="crumb"><a href="/bigyo/">자재 비교</a> › {E(c["short"])}</p><h1>{E(c["title"])}</h1><p class="lead">{E(c["desc"])}</p>
<div class="tw"><table class="cmp"><thead>{th}</thead><tbody>{tb}</tbody></table></div>
<h2>정리하면</h2><p>{E(c["concl"])}</p>{"".join(f'<h2>{E(h)}</h2>' + (("<" + k + ">" + "".join(f"<li>{x}</li>" for x in L) + "</" + k + ">") if k in ("ul", "ol") else "".join(f"<p>{x}</p>" for x in L)) for h, k, L in c.get("secs", []))}<p><a class="b o" href="/jaryo/?q={c['q']}">매장 취급 제품 사진 보기</a> <a class="b o" href="/calc.html">자재 계산기</a></p><p>{ml}</p>
<p class="small muted">일반적인 특징을 정리한 것으로 제품·등급에 따라 다를 수 있습니다. 매장에서 실물을 비교해 보세요.</p></section>
<section class="wrap sec"><h2>관련 영상</h2>{vsplit(vs, "h3")}</section>
<section class="wrap sec"><h2>자주 묻는 질문</h2>{"".join(f'<details class="cfq"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in _cfq(c))}</section>
<section class="wrap sec"><h2>다른 자재 비교</h2>{cmpnav(c["slug"])}</section>{mallbox(c["mats"])}{CTA}""", "/jajae/",
             {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in _cfq(c)]})
    page("bigyo/index.html", "자재 비교 — 합판·사이딩·단열재·바닥재·도어·루바 종류별 차이 | 영진목재", "헷갈리는 건축 자재를 종류별로 비교했습니다. 합판 vs OSB vs MDF, 세라믹·메탈·비닐 사이딩, 단열재, 바닥재, 실내 도어, 루바, 집성판, 각재, 방음·흡음재.",
         f'<section class="wrap sec"><p class="crumb"><a href="/jajae/">자재 백과</a> › 자재 비교</p><h1>자재·인테리어 비교 <small>{len(CMP)}가지</small></h1><p class="lead">비슷해 보여도 쓰는 곳이 다른 자재들을 분류별로 비교했습니다.</p>' + _swipe_rows([(c["mats"], c) for c in CMP], lambda it: f'<a class="pc" href="/bigyo/{it[1]["slug"]}.html"><small>자재 비교</small><b>{E(it[1]["short"])}</b><span>{E(it[1]["desc"][:70])}…</span></a>') + f'</section>{CTA}', "/jajae/")

    # 공간 사진 둘러보기 — 사진 위 +를 누르면 자재·시공법·제품 페이지로 (src/gonggan_data.py)
    import gonggan_data as _GG
    def _gscene(sc, big=True):
        slug, ttl, img, cred, lead, spots = sc
        dots = "".join(f'<button class="hsd" style="left:{x}%;top:{y}%" data-i="{i}" aria-label="{E(n)} 자세히"><span>+</span></button>' for i, (x, y, n, *_r) in enumerate(spots))
        pops = ""
        for i, (x, y, n, k, w, h1, t1, more) in enumerate(spots):
            kn, how = _GG.K[k]
            ml = "".join(f'<a href="{a}">{E(b)}</a>' for a, b in more)
            pops += (f'<div class="hsp" id="hs-{slug}-{i}" data-i="{i}"><small>{E(kn)}</small><b>{E(n)}</b><p>{E(w)}</p>'
                     f'<p class="hsh2">이렇게 시공해요</p><ol>' + "".join(f"<li>{E(t)}</li>" for t in how) + '</ol>'
                     f'<a class="b r hsgo" href="{h1}">{E(t1)} ›</a><div class="hsm">{ml}</div></div>')
        _ss = f' srcset="{_gth(img, 1000, "m")} 1000w, {img} 1600w" sizes="(max-width:900px) 100vw, 820px"' if _gth(img, 1000, "m") != img else ""
        return (f'<div class="hsw" data-s="{slug}"><div class="hsi"><img src="{_gth(img, 1000, chr(109))}"{_ss} alt="{E(ttl.split(" — ")[0])}">{dots}</div><p class="hsc">{E(cred)} · +를 누르면 자재와 시공법이 나와요</p>'
                f'<div class="hsl">{pops}</div><p class="hsh">옆으로 밀어서 더 보기 ›</p></div>')
    _GORD = [x for k, t, d in _GG.CATS for x in _GG.SCENES if _GG.cat(x[0]) == k]
    _GIX = {x[0]: i for i, x in enumerate(_GORD)}
    for sc in _GG.SCENES:
        slug, ttl, img, cred, lead, spots = sc
        _gi = _GIX[slug]; _gp = _GORD[_gi - 1]; _gn = _GORD[(_gi + 1) % len(_GORD)]
        _gnav = (f'<div class="ggnav" data-prev="/gonggan/{_gp[0]}.html" data-next="/gonggan/{_gn[0]}.html">'
                 f'<a class="ggp" href="/gonggan/{_gp[0]}.html" rel="prev">‹ <span>{E(_gp[1].split(" — ")[0])}</span></a>'
                 f'<b>{_gi + 1} / {len(_GORD)}</b>'
                 f'<a class="ggn" href="/gonggan/{_gn[0]}.html" rel="next"><span>{E(_gn[1].split(" — ")[0])}</span> ›</a></div>'
                 f'<link rel="prefetch" href="/gonggan/{_gn[0]}.html"><p class="hsh ggsw">사진을 옆으로 밀면 다음 현장 ›</p>')
        _mc = _GG.cat(slug); _mct = dict((k, t) for k, t, d in _GG.CATS)[_mc]
        oth = [x for x in _GG.SCENES if x[0] != slug and _GG.cat(x[0]) == _mc]
        oth2 = [x for x in _GG.SCENES if _GG.cat(x[0]) != _mc]
        ld = {"@context": "https://schema.org", "@type": "ImageObject", "contentUrl": img if img.startswith("http") else BASE + img, "name": ttl, "description": lead,
              "about": [{"@type": "Thing", "name": sp[2], "url": BASE + sp[5]} for sp in spots]}
        page(f"gonggan/{slug}.html", ttl + " | 영진목재", (lead + " " + ", ".join(sp[2] for sp in spots))[:155],
             f'''<section class="wrap sec"><p class="crumb"><a href="/gonggan/">공간 사진 둘러보기</a> › {E(ttl.split(" — ")[0])}</p><h1>{E(ttl)}</h1><p class="lead">{E(lead)}</p>
{_gscene(sc).replace('<div class="hsl', _gnav + '<div class="hsl', 1)}
<p class="small muted">사진 속 제품은 매장에서 주문·상담할 수 있습니다(가격·재고는 매장 문의). 비슷한 다른 자재로 같은 느낌을 내는 방법도 안내해 드립니다.</p></section>
<section class="wrap sec">{(f'<h2>같은 분류: {E(_mct)}</h2><div class="pl hs">' + "".join(f'<a class="pc" href="/gonggan/{x[0]}.html"><img loading="lazy" src="{_gth(x[2])}" alt=""><b>{E(x[1].split(" — ")[0])}</b><span>+ {len(x[5])}곳</span></a>' for x in oth) + '</div><p class="hsh">옆으로 밀어서 더 보기 ›</p>') if oth else ""}<h2>다른 공간 사진</h2><div class="pl hs">{"".join(f'<a class="pc" href="/gonggan/{x[0]}.html"><img loading="lazy" src="{_gth(x[2])}" alt=""><b>{E(x[1].split(" — ")[0])}</b><span>+ {len(x[5])}곳</span></a>' for x in oth2[:24])}</div><p class="hsh">옆으로 밀어서 더 보기 ›</p><p><a class="b" href="/gonggan/">분류별로 전체 보기 ›</a></p></section>{CTA}''', "/trend/", ld, img)
    def _ggcard(x):
        _src = _gth(x[2]); _pts = [p for p in (_ggsq(_src, sp[0], sp[1]) for sp in x[5]) if p]
        return (f'<a class="pc" href="/gonggan/{x[0]}.html"><span class="ggi"><img loading="lazy" src="{_src}" alt="{E(x[1].split(" — ")[0])}">'
                + "".join(f'<i style="left:{a}%;top:{b}%"></i>' for a, b in _pts)
                + f'</span><b>{E(x[1].split(" — ")[0])}</b><span>+ {len(x[5])}곳 · {E(x[4][:40])}…</span></a>')
    _ggidx = '<nav class="ggc">' + "".join(f'<a href="#c-{k}">{E(t)} <small>{sum(1 for x in _GG.SCENES if _GG.cat(x[0]) == k)}</small></a>' for k, t, d in _GG.CATS) + '</nav>'
    _ggidx += '<h2 id="c-new" class="ggh">새로 올라온 공간 <small>최근 8곳</small></h2><p class="small muted">가장 최근에 올린 사진부터 보여 드립니다.</p><div class="pl hs gg">' + "".join(_ggcard(x) for x in _GG.SCENES[::-1][:8]) + '</div><p class="hsh">옆으로 밀어서 더 보기 ›</p>'
    for k, t, d in _GG.CATS:
        _xs = [x for x in _GG.SCENES[::-1] if _GG.cat(x[0]) == k]
        if _xs:
            _ggidx += f'<h2 id="c-{k}" class="ggh">{E(t)} <small>{len(_xs)}곳</small></h2><p class="small muted">{E(d)}</p><div class="pl hs gg">{"".join(_ggcard(x) for x in _xs)}</div><p class="hsh">옆으로 밀어서 더 보기 ›</p>'
    page("gonggan/index.html", "공간 사진 둘러보기 — 사진 속 자재·시공법 바로 찾기 | 영진목재", "거실·현관·방 사진 속 +를 누르면 어떤 자재인지, 어떻게 시공하는지, 어디서 사는지 바로 볼 수 있어요. 중문·도어·마루·아트월·우드월·수납장.",
         f'''<section class="wrap sec"><p class="crumb"><a href="/trend/">인테리어 트렌드</a> › 공간 사진 둘러보기</p><h1>공간 사진 둘러보기 <small>{len(_GG.SCENES)}곳</small></h1><p class="lead">사진 속 <b>+</b>를 누르면 그 자재가 무엇인지, 어떻게 시공하는지 나오고 제품 페이지로 바로 넘어갑니다.</p><a class="sjgo" href="/sajin.html?m=gonggan"><i aria-hidden="true"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8.5A2.5 2.5 0 0 1 6.5 6h1.6l1.3-1.8A1.5 1.5 0 0 1 10.6 3.5h2.8a1.5 1.5 0 0 1 1.2.7L15.9 6h1.6A2.5 2.5 0 0 1 20 8.5v8A2.5 2.5 0 0 1 17.5 19h-11A2.5 2.5 0 0 1 4 16.5z"/><circle cx="12" cy="12.3" r="3.4"/></svg></i><span><b>내 공간 사진 찍어서 자재 알아보기·올리기</b><small>거실·방·가게 사진을 찍으면 쓰인 자재를 모아 보여 주고, 이곳 공간 사진에 올릴 수 있어요</small></span><u aria-hidden="true">›</u></a>
{_ggidx}</section>{CTA}''', "/trend/")

    # 하는 법 Q&A (실제 유튜브 검색어 기준, src/qna_data.py) — /qna/
    from qna_data import QNA as _QNA
    for slug, q, a, steps, warn, kw, mats, links in _QNA:
        vs = top(lambda v, kw=kw: re.search(kw, v["title"]) is not None, 6)
        ml = " · ".join(f'<a href="/jajae/{m}.html">{matname2[m]} 용도·기준가</a>' for m in mats if m in matname2)
        oth = [x for x in _QNA if x[0] != slug and (set(x[6]) & set(mats))][:6]
        _hd = "단점" if "단점" in q else "사는 법" if ("파는 곳" in q or "구매" in q) else "확인할 것" if "살 때" in q else "차이 정리" if " vs " in q else "고르는 법" if ("어떤 나무" in q or "어떤 자재" in q or "어떤 판" in q) else "순서"
        ld = [{"@context": "https://schema.org", "@type": "HowTo", "name": q, "description": a, "step": [{"@type": "HowToStep", "position": i + 1, "text": t} for i, t in enumerate(steps)]},
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q.split(" — ")[0] + "?", "acceptedAnswer": {"@type": "Answer", "text": a}}]}]
        if _hd != "순서": ld = ld[1:]
        page(f"qna/{slug}.html", q + " | 영진목재", a[:150],
             f"""<section class="wrap sec"><p class="crumb"><a href="/qna/">하는 법 Q&amp;A</a> › {E(q.split(" — ")[0])}</p><h1>{E(q)}</h1><p class="lead">{E(a)}</p>
<h2>{_hd}</h2><ol class="gtip">{"".join(f"<li>{E(t)}</li>" for t in steps)}</ol>
{('<h2>주의할 점</h2><ul class="gtip">' + "".join(f"<li>{E(w)}</li>" for w in warn) + '</ul>') if warn else ''}
<div class="qk">{"".join(f'<a href="{h}">{E(t)}</a>' for h, t in links)}</div><p>{ml}</p>
<p class="small muted">일반적인 방법을 정리한 것으로 제품·현장 상태에 따라 다를 수 있습니다. 자재 고르기는 매장(042-545-2900)에서 도와 드립니다.</p></section>
{f'<section class="wrap sec"><h2>관련 영상 — 월드건축자재DIY</h2>{vsplit(vs, "h3")}</section>' if vs else ''}
{('<section class="wrap sec"><h2>같이 많이 찾는 질문</h2><ul class="mgl">' + "".join(f'<li><a href="/qna/{x[0]}.html">{E(x[1].split(" — ")[0])}</a></li>' for x in oth) + '</ul></section>') if oth else ''}{mallbox(mats)}{CTA}""", "/jajae/", ld)
    page("qna/index.html", "하는 법 Q&A — 석고보드 앙카·실리콘 쏘는법·경첩 조절·오일스테인 건조 | 영진목재",
         "사람들이 실제로 많이 검색하는 목공·인테리어 '하는 법' 질문에 매장에서 답했습니다. 석고보드 보수, 합판 자르기, 실리콘 제거, 경첩 조절, 데크 보수 등.",
         f'<section class="wrap sec"><p class="crumb"><a href="/jajae/">자재 백과</a> › 하는 법 Q&amp;A</p><h1>하는 법 Q&amp;A <small>{len(_QNA)}가지</small></h1><p class="lead">유튜브·검색에서 많이 찾는 질문을 골라 순서대로 답했습니다. 분류별로 옆으로 넘겨 보세요.</p>'
         + _swipe_rows([(x[6], x) for x in _QNA], lambda it: f'<a class="pc" href="/qna/{it[1][0]}.html"><small>하는 법</small><b>{E(it[1][1].split(" — ")[0])}</b><span>{E(it[1][2][:64])}…</span></a>') + f'</section>{CTA}', "/jajae/")

    # 시즌·뉴스 이슈 × 자재 (src/issue_data.py) — /issue/
    from issue_data import ISSUE as _ISS
    for slug, t, dt, summ, secs, srcs, mats, links, kw in _ISS:
        vs = top(lambda v, kw=kw: re.search(kw, v["title"]) is not None, 6)
        ml = " · ".join(f'<a href="/jajae/{m}.html">{matname2[m]} 용도·기준가</a>' for m in mats if m in matname2)
        body = "".join(f"<h2>{E(h)}</h2><ul class='gtip'>" + "".join(f"<li>{E(x)}</li>" for x in xs) + "</ul>" for h, xs in secs)
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": t, "datePublished": dt, "dateModified": dt, "author": {"@type": "Organization", "name": "영진종합목재(월드건축자재)"}, "publisher": {"@type": "Organization", "name": "영진종합목재(월드건축자재)"}, "description": summ}
        page(f"issue/{slug}.html", t + " | 영진목재", summ[:150],
             f"""<section class="wrap sec"><p class="crumb"><a href="/issue/">이슈·시즌 자재</a> › {E(t.split(" — ")[0])}</p><h1>{E(t)}</h1><p class="small muted">{dt} · 영진종합목재</p><p class="lead">{E(summ)}</p>{body}
<div class="qk">{"".join(f'<a href="{h}">{E(x)}</a>' for h, x in links)}</div><p>{ml}</p>
<p class="small">참고: {" · ".join(f'<a href="{u}" target="_blank" rel="noopener nofollow">{E(n)}</a>' for n, u in srcs)}</p>
<p class="small muted">제도·기준은 바뀔 수 있으니 공식 기관 안내를 꼭 확인하세요. 자재 상담은 매장(042-545-2900).</p></section>
{f'<section class="wrap sec"><h2>관련 영상 — 월드건축자재DIY</h2>{vsplit(vs, "h3")}</section>' if vs else ''}{CTA}""", "/jajae/", ld)
    page("issue/index.html", "이슈·시즌 자재 — 농촌체류형 쉼터·겨울 결로 등 지금 필요한 자재 | 영진목재", "요즘 뉴스·계절에 맞춰 필요한 목재·건축자재와 방법을 정리했습니다.",
         '<section class="wrap sec"><h1>이슈·시즌 자재</h1><p class="lead">뉴스와 계절에 맞춰 지금 많이 찾는 자재를 정리합니다.</p><h2 class="gt"><span>최신 글</span><small>옆으로 넘겨 보세요 ›</small></h2><div class="pl hs">' + "".join(f'<a class="pc" href="/issue/{x[0]}.html"><small>{x[2]}</small><b>{E(x[1].split(" — ")[0])}</b><span>{E(x[3][:70])}…</span></a>' for x in sorted(_ISS, key=lambda x: x[2], reverse=True)) + f'</div></section>{CTA}', "/jajae/")

    # 영상 개별 페이지 (data/vdesc.json.gz — 유튜브 설명·길이·게시일)
    import datetime as _dt
    matname3 = {m["slug"]: m["name"] for m in MATS}
    def vbody(d, vid):
        out, lis, chk = [], [], []
        for line in d.split("\n"):
            t = line.strip()
            if not t: continue
            m = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(.*)$", t)
            if m:
                sec = (int(m.group(1)) * 60 + int(m.group(2))) if not m.group(3) else int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
                lis.append(f'<li><a href="https://www.youtube.com/watch?v={vid}&amp;t={sec}s" target="_blank" rel="noopener">{E(t.split()[0])}</a> {E(m.group(4))}</li>'); continue
            if t.startswith("✔"): chk.append(f"<li>{E(t.lstrip('✔ ').strip())}</li>"); continue
            out.append(f"<p>{E(t)}</p>")
        h = "".join(out)
        if chk: h += "<h2>이 영상에서 알 수 있는 것</h2><ul>" + "".join(chk) + "</ul>"
        if lis: h += "<h2>영상 목차</h2><ul class=\"toc\">" + "".join(lis) + "</ul>"
        return h
    _vt_used = set()
    def _vtitle(v):  # 영상 페이지 제목 겹침 방지(구글 중복 제목 경고)
        _cl = lambda t: re.sub(r"[“”\"']", "", t).strip()
        def _cut(t, n):  # 단어 중간에서 자르지 않기
            t = t.strip()
            if len(t) <= n: return t
            u = t[:n]; i = u.rfind(" ")
            return (u[:i] if i >= n * 0.6 else u).rstrip(" ,·-—|")
        b = _cut(_cl(vshort(v["title"])), 40)
        if len(b) < 10: b = _cut(_cl(v["title"]), 40).strip(" ,")
        for c in (b, _cut(v["title"], 44), b + (" (쇼츠)" if v["type"] == "S" else " (영상)"), _cut(v["title"], 44) + (" 쇼츠" if v["type"] == "S" else " 풀영상")):
            if c not in _vt_used: _vt_used.add(c); return c
        k = 2
        while f"{b} {k}" in _vt_used: k += 1
        _vt_used.add(f"{b} {k}"); return f"{b} {k}"
    for v in sorted(V, key=lambda x: -x["n"]):
        if v["id"] not in VD: continue
        d, ln, ts = VD[v["id"]]
        st = _vtitle(v)
        _dl = "\n".join(l for l in (d or "").split("\n") if l.strip() and not re.match(r"\s*(📍|▶|📦|#|https?://|\d+:\d\d)", l))
        first = re.split(r"(?<=[.!?다요])\s", _dl.replace("\n", " "), maxsplit=1)[0] if _dl else v["title"]
        rel = [x for x in V if x["cat"] == v["cat"] and x["id"] != v["id"]]
        rel = sorted(rel, key=lambda x: -x["n"])[:8]
        ml = " · ".join(f'<a href="/jajae/{m}.html">{matname3[m]} 용도·기준가</a>' for m in v["mats"] if m in matname3)
        ld = {"@context": "https://schema.org", "@type": "VideoObject", "name": v["title"][:100], "description": (d or v["title"])[:300],
              "thumbnailUrl": f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg", "embedUrl": f"https://www.youtube.com/embed/{v['id']}",
              "contentUrl": vurl(v)}
        if ts: ld["uploadDate"] = _dt.datetime.fromtimestamp(ts, _dt.timezone(_dt.timedelta(hours=9))).isoformat()
        if ln: ld["duration"] = f"PT{ln // 60}M{ln % 60}S"
        cn = CATN.get(v["cat"], "영상")
        vds = (("1분 쇼츠: " if v["type"] == "S" else "") + (first or st))[:110]
        if len(vds) < 60: vds = (vds + " " + (v["title"] if v["title"] not in vds else "") + f" — 대전 영진종합목재(월드건축자재) {cn} 영상. 자재 재단·전국 배송.").replace("  ", " ")[:150]
        VSM.append((f"{BASE}/v/{v['id']}.html", v, (d or v["title"]), ts, ln))
        _mfq = json.load(open(f"{ROOT}/data/mat_faq.json", encoding="utf-8")) if "_MFQ" not in globals() else _MFQ
        globals()["_MFQ"] = _mfq
        _ms = list(v["mats"])
        if not _ms:
            for rx_, sl_ in [(r"OSB", "osb"), (r"MDF", "mdf"), (r"합판", "hapan"), (r"다루끼|각재|구조재|투바이|2[xX×]4|목상", "gujo"), (r"방부", "bangbu"), (r"합성데크|합성목", "hapdeck"), (r"데크", "bangbu"), (r"집성", "jipseong"),
                             (r"히노끼|편백|삼나무|루바", "hinoki"), (r"석고", "gypsum"), (r"사이딩", "siding"), (r"단열|아이소핑크", "insul"), (r"스테인|오일", "stain"), (r"마루|후로링|장판|데코타일", "maru"),
                             (r"필름", "film"), (r"몰딩|걸레받이", "molding"), (r"침목", "chimmok"), (r"타일", "tile"), (r"문짝|방문|도어|문틀|중문", "door"), (r"흡음|방음", "sound"), (r"피스|타카|경첩|철물", "hardware"), (r"온실|비닐하우스|골조|파고라|퍼걸러|창고", "gujo"), (r"아트월|원목|라왕|테이블|선반|책상", "jipseong"), (r"벽|천장", "gypsum")]:
                if re.search(rx_, v["title"]) and sl_ not in _ms: _ms.append(sl_)
        if not _ms:
            _cf = {"deck": "bangbu", "greenhouse": "gujo", "furniture": "jipseong", "kitchen": "jipseong", "exterior": "siding", "wall": "gypsum", "floor": "maru", "finish": "film", "electric": "insul", "door": "door", "tool": "hardware"}.get(v["cat"])
            if _cf: _ms = [_cf]
        _mm = [m for sl_ in _ms for m in MATS if m["slug"] == sl_][:2]
        _vx = '<section class="wrap sec"><h2>영상 정보</h2><div class="tw"><table class="rt"><tbody>' + \
              f'<tr><th>분류</th><td><a href="/video/{v["cat"]}.html">{E(cn)}</a></td></tr>' + \
              (f'<tr><th>길이</th><td>{ln // 60}분 {ln % 60}초</td></tr>' if ln else '') + \
              (f'<tr><th>게시일</th><td>{_dt.datetime.fromtimestamp(ts, _dt.timezone(_dt.timedelta(hours=9))).strftime("%Y년 %m월 %d일")}</td></tr>' if ts else '') + \
              f'<tr><th>조회수</th><td>{views(v["n"])}</td></tr><tr><th>형식</th><td>{"쇼츠(짧은 영상)" if v["type"] == "S" else "일반 영상"}</td></tr>' + \
              (f'<tr><th>나온 자재</th><td>{" · ".join(E(m["name"]) for m in _mm)}</td></tr>' if _mm else '') + '</tbody></table></div></section>'
        for m in _mm:
            _vx += (f'<section class="wrap sec"><h2>영상에 나온 자재 — {E(m["name"])}</h2><p>{E(m["lead"])}</p><h3>어디에 쓰나요</h3><ul>' + "".join(f"<li>{E(w)}</li>" for w in m["where"][:5]) + '</ul>'
                    + f'<h3>{E(m["name"])} 소매 기준가</h3>' + ptable(mat_prices(m, 6))
                    + (('<h3>자주 묻는 질문</h3>' + faqslide([tuple(x) for x in _mfq.get(m["slug"], [])[:3]])) if _mfq.get(m["slug"]) else '')
                    + f'<p><a href="/jajae/{m["slug"]}.html">{E(m["name"])} 용도·규격·시공 영상 전체 보기 ›</a> · <a href="/calc.html">필요한 양 계산</a> · <a href="/cut.html">원하는 크기로 재단 그림</a></p></section>')
        _seg = v["title"].split("|")[0]
        _mks = sorted(((re.search(rx, _seg).start(), k) for k, rx in MKV.items() if k in MKNM and k not in ("jakeopdae", "beranda", "sinbaljang") and re.search(rx, _seg)))
        _mks = [k for _, k in _mks][:2]
        _mkln = ('<p>🪚 직접 만들어 보기: ' + " · ".join(f'<a href="/mandeul/{k}.html">{E(MKNM[k])} 자재·재단 크기</a>' for k in _mks) + '</p>') if _mks else ""
        _sgs = [x for x in SG if x[10] and re.search(x[10], v["title"])][:2]
        if _sgs: _mkln += '<p>🔨 시공법 보기: ' + " · ".join(f'<a href="/sigongbeop/{x[0]}.html">{E(x[1])} 순서·필요 자재</a>' for x in _sgs) + '</p>'
        _PV = [(r"중문|3연동|슬라이딩도어", "/yerim/p/", "예림 중문 제품"), (r"방문|도어|문틀|ABS", "/younglim/p/", "영림 도어·문틀 제품"), (r"몰딩|걸레받이|필름|시트지", "/younglim/p/", "영림 몰딩·필름 제품"),
               (r"스테인|오일|페인트|바니쉬|칠하", "/bondex/p/", "본덱스 스테인·페인트 제품"), (r"경첩|손잡이|피스|앙카|철물|실리콘|레일|선반|공구|드릴|타카", "/bupum/p/", "철물·공구 제품"),
               (r"석고|텍스|천장|흡음|단열", "/knauf/", "크나우프 석고·천장·단열 제품"), (r"사이딩|외벽|루바|계단|목조주택", "/geonjae/p/", "외장·내장 건축자재 제품"), (r"창호|창문|천창|지붕", "/suip/p/", "수입 창호·지붕재 제품")]
        _pvs = list(dict.fromkeys((h, t) for rx, h, t in _PV if re.search(rx, v["title"])))[:3]
        if _pvs: _mkln += '<p>🛒 영상에 나온 제품 찾기: ' + " · ".join(f'<a href="{h}">{t}</a>' for h, t in _pvs) + '</p>'
        page(f"v/{v['id']}.html", f"{st} — {'쇼츠' if v['type'] == 'S' else '영상'}" + (f" 조회 {views(v['n'])}" if v['n'] >= 1000 else "") + " | 영진목재", vds,
             f"""<section class="wrap sec"><p class="crumb"><a href="/video/">영상</a> › <a href="/video/{v['cat']}.html">{E(cn)}</a></p><h1 class="vt1">{E(v['title'])}</h1>
<div class="{'emb sh1' if v['type']=='S' else 'emb'}"><iframe loading="lazy" src="https://www.youtube.com/embed/{v['id']}" title="{E(st)}" allowfullscreen></iframe></div>
<p class="small muted">{f"조회 {views(v['n'])} · " if v['n'] else ""}{'쇼츠 · ' if v['type']=='S' else ''}<a href="{vurl(v)}" target="_blank" rel="noopener">유튜브에서 보기</a></p>
<div class="vdesc">{vbody(d, v['id'])}</div>
{f'<p>👉 영상에 나온 자재: {ml}</p>' if ml else ''}{_mkln}<p>👉 <a href="/calc.html">필요한 양 계산하기</a> · <a href="/visit.html">매장에서 재단해 가기</a></p></section>
{_vx}{f'<section class="wrap sec"><h2>비슷한 영상</h2>{vsplit(rel, "h3")}</section>' if rel else ''}{CTA}""", f"/video/", ld, f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg")

    # 건축 현장 용어 사전
    YG = json.load(open(f"{ROOT}/data/yongeo.json", encoding="utf-8")) if os.path.exists(f"{ROOT}/data/yongeo.json") else []
    if YG:
        mn = {m["slug"]: m["name"] for m in MATS}
        terms = [t for _, ts in YG for t in ts]
        ygld = {"@context": "https://schema.org", "@type": "DefinedTermSet", "name": "건축·인테리어 현장 용어 사전", "hasDefinedTerm": [{"@type": "DefinedTerm", "name": t[0], "description": f"{t[1]}. {t[2]}"} for t in terms]}
        toc = " · ".join(f'<a href="#t{i}">{E(t[0])}</a>' for i, t in enumerate(terms))
        body = ""; i = 0
        for g, ts in YG:
            body += f'<h2>{E(g)}</h2><dl class="yg">'
            for t in ts:
                ln = f' <a class="small" href="/jajae/{t[3]}.html">{mn[t[3]]} 보기 ›</a>' if t[3] in mn else ""
                body += f'<dt id="t{i}">{f"<a href=/yongeo/{t[4]}.html>{E(t[0])}</a>" if len(t) > 4 and t[4] else E(t[0])} <span class="muted">= {E(t[1])}</span></dt><dd>{E(t[2])}{ln}</dd>'; i += 1
            body += "</dl>"
        byid = {v["id"]: v for v in V}
        yv = [byid[x] for x in ["GGm4laQFUMg", "FNylPstDD4I", "jcqTf-1G5mA"] if x in byid]
        # 용어별 전용 페이지(/yongeo/<slug>.html) — "○○ 뜻" 검색용. 사전 본문의 각 용어에서 링크
        _GG = {"hapan": "hapan-gagyeok", "gujo": "gakjae-gagyeok", "hinoki": "hinoki-ruba", "molding": "molding-gagyeok", "door": "door-gagyeok"}
        _XL = {'haseuri': [('/qna/supyeong-moltal.html', '수평 몰탈'), ('/qna/concrete-bunjin.html', '콘크리트 분진')], 'wari': [('/qna/tile-jareugi.html', '타일 자르기'), ('/qna/decotile-herringbone.html', '데코타일 헤링본')], 'kirikaki': [('/qna/gakjae-yeongyeol.html', '각재 연결'), ('/qna/ultari-gidung.html', '울타리 기둥')], 'mizu': [('/qna/seonban-bracket.html', '선반 브라켓'), ('/yongeo/supyeonggi.html', '수평기 뜻')], 'nori': [('/qna/self-dobae.html', '셀프 도배'), ('/qna/byeokji-deultteum.html', '벽지 들뜸')], 'sanding': [('/qna/sander-sapo.html', '샌더·사포 고르기'), ('/qna/sanding-meonji.html', '샌딩 먼지')], 'maerip': [('/qna/maeip-sliding-jungmun.html', '매립 슬라이딩 중문'), ('/qna/hidden-georebatgi.html', '히든 걸레받이')], 'baekhwa': [('/qna/damjang-bosu.html', '담장 보수'), ('/qna/epoxy-julnun.html', '에폭시 줄눈')], 'deultteum': [('/qna/kangmaru-deultteum.html', '강마루 들뜸'), ('/qna/film-deultteum.html', '필름 들뜸'), ('/qna/tile-deultteum.html', '타일 들뜸')], 'crack': [('/qna/seokgo-bosu.html', '석고보드 보수'), ('/qna/concrete-crack.html', '콘크리트 균열')], 'kane': [('/qna/gakjae-jikgak.html', '각재 직각 자르기'), ('/yongeo/clamp.html', '클램프 뜻')], 'masking': [('/qna/self-paint-junbimul.html', '셀프 페인트 준비물')], 'moksang': [('/sigongbeop/seokgo-cheonjang.html', '석고보드 천장'), ('/yongeo/darugi.html', '다루끼 뜻')], 'banjateul': [('/qna/cheonjang-cheojim.html', '천장 처짐')], 'gakgwan': [('/qna/pergola-mandeulgi.html', '파고라 만들기')], 'angle': [('/qna/changgo-interior.html', '창고 정리')], 'magamjae': [('/qna/self-interior-sunseo.html', '셀프 인테리어 순서'), ('/yongeo/haji.html', '하지 뜻')], 'interior-film-tteut': [('/gagyeok/interior-film.html', '인테리어 필름 가격')], 'dojang': [('/qna/roller-paint.html', '롤러 페인트'), ('/qna/paint-beotgyeojim.html', '페인트 벗겨짐')], "misong": [("/qna/redpine-vs-misong.html", "레드파인 vs 미송"), ("/bigyo/misong-hapan-duggae.html", "미송합판 두께")], "sosong": [("/bigyo/darugi-types.html", "다루끼 종류")], "yuksong": [("/qna/yuksong-gakjae.html", "육송 각재")], "rawang": [("/qna/rawang-gakjae.html", "라왕 각재"), ("/bigyo/gyedanpan-jongryu.html", "계단판 종류")], "merbau": [("/qna/merbau-jipseong.html", "멀바우 집성"), ("/bigyo/jipseongpan-sujong.html", "집성판 수종별")], "acacia": [("/bigyo/jipseongpan-sujong.html", "집성판 수종별"), ("/qna/doma-namu-goreugi.html", "도마 나무")], "gomunamu": [("/qna/gomu-vs-samnamu-jipseong.html", "고무나무 vs 삼나무"), ("/bigyo/jipseongpan-sujong.html", "집성판 수종별")], "samnamu": [("/bigyo/hinoki-vs-samnamu.html", "편백 vs 삼나무"), ("/qna/gomu-vs-samnamu-jipseong.html", "고무나무 vs 삼나무")], "jeoksammok": [("/bigyo/jeoksammok-size.html", "적삼목 사이즈"), ("/qna/jeoksammok.html", "적삼목")], "odong": [("/qna/camping-namu.html", "캠핑 나무")], "ash": [("/qna/gagu-namu-chai.html", "가구 나무별 차이")], "chamjuk": [("/bigyo/jipseongpan-sujong.html", "집성판 수종별")], "haja": [("/qna/kangmaru-deultteum.html", "강마루 들뜸"), ("/qna/interior-huhoe.html", "인테리어 후회")], "gyeonjeok": [("/qna/gyeonjeokseo-check.html", "견적서 확인"), ("/calc.html", "자재비 계산기")], "pyeongtan": [("/qna/supyeong-moltal.html", "수평 몰탈"), ("/qna/chabak-pyeongtan.html", "평탄 작업")], "gasket": [("/qna/hyeongwanmun-packing.html", "현관문 패킹"), ("/qna/bangmun-teumsae.html", "방문 틈새막이")], "bangyeom": [("/qna/sangga-jajae.html", "상가 셀프 인테리어")], "bulyeon": [("/knauf/", "크나우프 천장재")], "naesu": [("/qna/bangsu-hapan.html", "방수 합판"), ("/bigyo/hapan-types.html", "합판 종류")], "tg": [("/bigyo/osb-duggae.html", "OSB 두께"), ("/qna/nongmak-badak.html", "농막 바닥")], "yujeol-mujeol": [("/qna/ruba-yujeol-mujeol.html", "루바 유절·무절")], "t-duggae": [("/bigyo/mdf-duggae.html", "MDF 두께"), ("/bigyo/jajak-duggae.html", "자작합판 두께")], "anka": [("/qna/anka-jongryu.html", "앙카 종류"), ("/qna/anka-bakgi.html", "앙카 박기")], "kalbeulleok": [("/qna/curtain-rail.html", "커튼 레일 달기"), ("/qna/anka-heotdol.html", "앙카 헛돎")], "ggeoksoe": [("/bigyo/ggeoksoe-bracket-types.html", "꺾쇠·브라켓 종류"), ("/qna/ggeoksoe-bogang.html", "꺾쇠 보강")], "dabo": [("/qna/seonban-dabo.html", "선반 다보"), ("/qna/mokdabo.html", "목다보")], "gyeongcheop": [("/bigyo/gyeongcheop-types.html", "경첩 종류·가격"), ("/qna/gyeongcheop-gyoche.html", "경첩 교체")], "cylinder": [("/bigyo/cylinder-types.html", "실린더 종류·가격"), ("/qna/mun-cylinder.html", "문 실린더")], "bracket": [("/bigyo/ggeoksoe-bracket-types.html", "꺾쇠·브라켓 종류"), ("/qna/seonban-bracket.html", "선반 브라켓")], "siltaka": [("/qna/taka-jongryu.html", "타카 종류"), ("/taka/", "타카·타카핀")], "washer": [("/qna/anka-bolt-gilee.html", "앙카볼트 길이")], "holdown": [("/cheolmul/mokjo.html", "목조주택 철물")], "hurricane-tie": [("/cheolmul/mokjo.html", "목조주택 철물"), ("/yongeo/seokkarae.html", "서까래 뜻")], "rail": [("/bigyo/hanger-rail-types.html", "행거 레일 세트"), ("/qna/seorap-3dan-rail.html", "3단 서랍 레일")], "varnish": [("/qna/varnish-gwangdo.html", "바니쉬 광도"), ("/bigyo/oilstain-vs-varnish.html", "오일스테인 vs 바니쉬")], "oilstain": [("/sigongbeop/oilstain.html", "오일스테인 칠하는 법"), ("/qna/oilstain-color.html", "오일스테인 색상")], "sealant": [("/qna/silicone-jongryu.html", "실리콘 종류"), ("/qna/molding-teum.html", "몰딩 틈 메우기")], "urethane-foam": [("/qna/pombond-sseugi.html", "폼본드 쓰기"), ("/bigyo/silicone-gun-types.html", "실리콘건 vs 폼건")], "sopit": [("/qna/pvc-sopit.html", "PVC 소핏")], "flashing": [("/qna/siding-flashing.html", "사이딩 후레싱")], "shingle": [("/qna/asphalt-shingle.html", "아스팔트 슁글"), ("/bigyo/shingle-types.html", "슁글 육각 vs 사각")], "siding": [("/bigyo/siding-types.html", "사이딩 종류"), ("/sigongbeop/siding-oebyeok.html", "사이딩 외벽 시공")], "lattice": [("/qna/pvc-lattice.html", "PVC 래티스"), ("/bigyo/pvc-lattice-types.html", "PVC 래티스 종류")], "grinder": [("/qna/gongu-geochi.html", "공구 거치")], "jigsaw": [("/qna/jigsaw-sayong.html", "직소 사용법"), ("/bigyo/circular-vs-jigsaw.html", "원형톱 vs 직소")], "trimmer": [("/qna/trimmer-sayong.html", "트리머 사용법")], "sander": [("/qna/sander-sapo.html", "샌더·사포 고르기"), ("/qna/sanding-meonji.html", "샌딩 먼지")], "gakdo-jeoldangi": [("/qna/gakdotop-sayong.html", "각도톱 사용법"), ("/qna/miter-molding.html", "몰딩 45도 자르기")], "impact": [("/bigyo/drill-vs-impact.html", "드릴 vs 임팩"), ("/qna/drill-pis-bakgi.html", "드릴로 피스 박기")], "supyeonggi": [("/qna/seonban-bracket.html", "선반 브라켓"), ("/qna/ultari-gidung.html", "울타리 기둥 세우기")], "clamp": [("/qna/jipseong-ieobutigi.html", "집성목 이어 붙이기"), ("/qna/mokgong-bond.html", "목공본드")], "deotbang": [("/sigongbeop/hapan-badak-deotbang.html", "합판 바닥 덧방"), ("/qna/hyeongwan-tile-deotbang.html", "현관 타일 덧방")], "julnun": [("/qna/epoxy-julnun.html", "에폭시 줄눈"), ("/yongeo/meji.html", "메지 뜻")], "cornerbead": [("/qna/seokgo-putty.html", "석고보드 퍼티"), ("/sigongbeop/seokgo-byeok.html", "석고보드 벽")], "silcheuk": [("/qna/door-silcheuk.html", "문 실측하는 법"), ("/qna/jungmun-size.html", "중문 사이즈")], "jaedan": [("/cut.html", "매장 재단 미리보기"), ("/jaedan-bi.html", "재단비 안내")], "gyeonchul": [("/qna/concrete-crack.html", "콘크리트 균열")], "bangtong": [("/qna/supyeong-moltal.html", "수평 몰탈"), ("/yongeo/mijang.html", "미장 뜻")], "cheolgeo": [("/qna/molding-jegeo.html", "몰딩 제거"), ("/qna/kangmaru-cheolgeo.html", "강마루 철거")], "janseon": [("/qna/janseon-geori.html", "장선걸이"), ("/bigyo/janseon-geori-vs-bracket.html", "장선걸이 vs 연결 철물")], "meonge": [("/yongeo/obiki.html", "오비끼 뜻"), ("/bigyo/bangbu-gakjae-size.html", "방부목 각재 사이즈")], "seokkarae": [("/qna/pergola-jibung.html", "파고라 지붕"), ("/bigyo/shingle-types.html", "슁글 육각 vs 사각")], "inbang": [("/sigongbeop/munteul-gyoche.html", "문틀 교체")], "ttijang": [("/qna/ruba-banghyang.html", "루바 붙이는 방향"), ("/bigyo/darugi-types.html", "다루끼 종류")], "haji": [("/bigyo/cement-board-haji-vs-magam.html", "시멘트보드 하지용"), ("/sigongbeop/seokgo-byeok.html", "석고보드 벽")], "mijang": [("/qna/supyeong-moltal.html", "수평 몰탈"), ("/yongeo/moltal.html", "몰탈 뜻")], "jjolde": [("/bigyo/pyeong-molding-pok.html", "평몰딩 폭 비교"), ("/qna/molding-teum.html", "몰딩 틈 메우기")], "jipseongmok": [("/gyugyeok/jipseong.html", "집성목 규격"), ("/qna/jipseong-varnish.html", "집성목 바니쉬")], "gujomok": [("/gyugyeok/gujo.html", "구조목 규격"), ("/bigyo/bangbu-vs-gujo.html", "방부목 vs 구조목")], "bangbumok": [("/qna/bangbu-size.html", "방부목 사이즈"), ("/bigyo/tanhwa-vs-bangbu.html", "탄화목 vs 방부목")], "hapan": [("/gyugyeok/hapan.html", "합판 규격"), ("/bigyo/hapan-types.html", "합판 종류")], "primer": [("/qna/tile-primer.html", "타일 프라이머"), ("/qna/jesso.html", "젯소")], "coking": [("/qna/silicone-jongryu.html", "실리콘 종류"), ("/qna/silicone-ssogi.html", "실리콘 쏘는 법")], "moltal": [("/qna/supyeong-moltal.html", "수평 몰탈"), ("/qna/concrete-crack.html", "콘크리트 균열")], "tempa-board": [("/bigyo/tempa-vs-ruba.html", "템바보드 vs 루바"), ("/gagyeok/tempa-board.html", "템바보드 가격")], "pis": [("/pis-gilee.html", "피스 길이 고르는 법"), ("/bigyo/sus-vs-normal-screw.html", "스텐 vs 일반 피스")], "taka": [("/taka/", "타카·타카핀"), ("/bigyo/taka-vs-pis.html", "타카 vs 피스")], "hinoki": [("/gagyeok/hinoki-ruba.html", "히노끼 루바 가격"), ("/bigyo/hinoki-vs-spruce-ruba.html", "히노끼 vs 스프러스")], "spruce": [("/qna/spruce-gakjae.html", "스프러스 각재"), ("/gagyeok/spruce-ruba.html", "스프러스 루바 가격")], "oepung": [("/qna/changmun-oepung.html", "창문 외풍 막기"), ("/qna/munteul-joint.html", "문틀 틈새 막기")], "putty": [("/qna/seokgo-putty.html", "석고보드 퍼티작업"), ("/qna/wood-filler.html", "우드필러")], "jesso": [("/qna/jesso.html", "젯소 바르는 법"), ("/qna/hapan-paint.html", "합판 페인트칠")], "gyeolro": [("/qna/chang-gyeolro.html", "창틀 결로 줄이기"), ("/issue/winter-gyeolro.html", "겨울 결로·단열")], "georebatgi": [("/qna/georebatgi-ppaegi.html", "걸레받이 빼는법"), ("/qna/georebatgi-silicone.html", "걸레받이 실리콘")], "mdf": [("/gyugyeok/mdf.html", "MDF 규격표"), ("/qna/mdf-sheet.html", "MDF 시트지")], "osb": [("/bigyo/osb-vs-hapan-roof.html", "OSB vs 합판"), ("/qna/osb-magam.html", "OSB 마감")], "pagora": [("/qna/pergola-mandeulgi.html", "파고라 만들기"), ("/cheolmul/jeongja.html", "정자·파고라 철물")], "deck": [("/mandeul/deck.html", "데크 만들기"), ("/bigyo/deck-finish.html", "데크 마감재 종류")], "sane": [("/qna/ruba-jongryu.html", "루바 종류"), ("/qna/pyeonbaek-ruba-self.html", "편백 루바 셀프 시공")], "haba": [("/yongeo/munseon.html", "문선 뜻")], "odoriba": [("/qna/gyedanjae-sujong.html", "계단재 수종 고르기")], "yokko-dade": [("/qna/pyeonbaek-ruba-self.html", "루바 붙이는 순서")], "hebe": [("/pyeong.html", "평·㎡(헤베) 환산 계산기")], "rube": [("/pyeong.html", "평·㎡ 환산 계산기"), ("/muge.html", "자재 무게 계산기")],
               "ja-chi": [("/qna/duchigak-darugi.html", "두치각·다루끼 규격 읽는 법"), ("/jae.html", "목재 재(才) 계산기")], "jae": [("/jae.html", "목재 재(才) 계산기")],
               "darugi": [("/qna/duchigak-darugi.html", "두치각·다루끼 규격"), ("/gagyeok/gakjae-gagyeok.html", "각재 가격")], "tubai": [("/bigyo/bangbu-vs-gujo.html", "방부목 vs 구조목"), ("/qna/gujomok-yeongyeol.html", "구조목 연결 방법")],
               "ppade": [("/qna/", "하는 법 Q&A")], "habaki": [("/sigongbeop/molding-georebatgi.html", "걸레받이·몰딩 시공")], "molding": [("/sigongbeop/molding-georebatgi.html", "몰딩 시공법"), ("/bigyo/molding-types.html", "몰딩 종류 비교")],
               "munseon": [("/sigongbeop/munteul-gyoche.html", "방문·문틀 교체")], "ruba": [("/bigyo/hinoki-vs-spruce-ruba.html", "히노끼 vs 스프러스 루바")], "denjo": [("/sigongbeop/seokgo-cheonjang.html", "석고보드 천장 시공")],
               "gabe": [("/gabyeok-gyesan.html", "가벽 자재 계산기")], "uma": [("/cheolmul/diy.html", "우마·벤치 프레임 철물")], "desuri": [("/sigongbeop/deck-nangan.html", "데크 난간")], "nagasi": [("/mandeul/sinkmunjjak.html", "싱크대 문짝 만들기")],
               "gakkumok": [("/gyugyeok/gakjae.html", "각재 규격표"), ("/gagyeok/gakjae-gagyeok.html", "각재 가격")], "niseu": [("/bigyo/oilstain-vs-varnish.html", "오일스테인 vs 바니시")],
               "hukki": [("/qna/oilstain-spray.html", "오일스테인 스프레이건 칠하기")], "ppaengkki": [("/bigyo/water-vs-oil-paint.html", "수성 vs 유성 페인트")],
               "giri": [("/qna/anka-ppaegi.html", "앙카 빼는 법"), ("/cheolmul/bolt.html", "앙카볼트·구조 피스")], "gada": [("/gyugyeok/hapan.html", "합판 규격표")]}
        _pos = {t[4]: (g, j) for g, ts in YG for j, t in enumerate(ts)}
        for g, ts in YG:
            for t in ts:
                if not t[4]: continue
                key = re.split(r"[(·]", t[0])[0]
                _c = t[0].rstrip(")")[-1]; _eun = "은" if ("가" <= _c <= "힣" and (ord(_c) - 0xAC00) % 28) else "는"
                rv = [v for v in V if key in v["title"]][:6] if len(key) >= 2 and key not in ("시다", "네다") else []
                sib = "".join(f'<a href="/yongeo/{x[4]}.html">{E(x[0])}</a>' for x in ts if x[4] and x[4] != t[4])
                links = []
                if t[3] in mn: links.append((f"/jajae/{t[3]}.html", f"{mn[t[3]]} 자재 백과"))
                if t[3] in _GG: links.append((f"/gagyeok/{_GG[t[3]]}.html", f"{mn.get(t[3], '')} 가격 가이드".strip()))
                links += _XL.get(t[4], [])
                fq = [(f"{t[0]} 뜻이 뭔가요?", f"{t[1]}. {t[2]}"), *([(f"{t[0]}{_eun} 현장에서 어떻게 쓰나요?", t[5])] if len(t) > 5 and t[5] else []), (f"{t[0]}{_eun} 표준어로 뭐라고 하나요?", f"표준어·우리말로는 '{t[1]}'(이)라고 합니다. 현장·지역에 따라 조금 다르게 쓰기도 합니다.")]
                ld = {"@context": "https://schema.org", "@graph": [{"@type": "DefinedTerm", "name": t[0], "description": f"{t[1]}. {t[2]}", "inDefinedTermSet": "https://www.wwood.co.kr/yongeo.html"},
                      {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}]}
                page(f"yongeo/{t[4]}.html", f"{t[0]} 뜻 — {t[1]} | 현장 용어 · 영진목재", f"{t[0]} 뜻: {t[1]}. {t[2]}"[:150],
                     f"""<section class="wrap sec"><p class="crumb"><a href="/yongeo.html">현장 용어 사전</a> › {E(g)}</p><h1>{E(t[0])} 뜻</h1>
<p class="lead"><b>{E(t[0])}</b> = <b>{E(t[1])}</b></p><p>{E(t[2])}</p>
{f'<h2>현장에서 이렇게 써요</h2><p>{E(t[5])}</p>' if len(t) > 5 and t[5] else ''}
<p class="small muted">목수·인테리어 현장에서 오래 써 온 말이라 견적서·상담에서 자주 나옵니다. 뜻을 알면 자재 주문과 업체 상담이 쉬워집니다.</p>
{('<h2>같이 보면 좋은 페이지</h2><div class="olk">' + "".join(f'<a href="{h}">{E(n)}</a>' for h, n in links) + '</div>') if links else ''}
<h2>자주 묻는 질문</h2>{"".join(f'<details class="faq"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in fq)}
<h2>{E(g)} — 다른 용어</h2><div class="olk">{sib}</div><p><a class="b o" href="/yongeo.html">현장 용어 사전 전체 ({len(terms)}개) ›</a></p></section>
{f'<section class="wrap sec"><h2>"{E(key)}" 나오는 영상</h2>{vsplit(rv, "h3")}</section>' if rv else ''}{CTA}""", "/jajae/", ld)
        page("yongeo.html", "건축 현장 용어 사전 — 다루끼·덴조·가베·오사마리·하바끼 뜻 | 영진목재", "목수·인테리어 현장에서 쓰는 일본어 잔재 용어와 자재 용어의 뜻을 정리했습니다. 다루끼, 덴조, 가베, 오사마리, 하바끼, 나라시, 메지 등.",
             f"""<section class="wrap sec"><h1>건축 현장 용어 사전</h1><p class="lead">현장에서 오가는 말을 알아야 자재 주문과 업체 상담이 쉬워집니다. 목수·인테리어 현장에서 자주 쓰는 용어 {len(terms)}개를 쉬운 말로 풀었습니다. 표준어로 바꿔 쓰는 것이 좋지만, 현장 소통을 위해 뜻은 알아 두세요.</p>
<p class="small">바로가기: {toc}</p>{body}<p class="small muted">현장·지역마다 쓰는 뜻이 조금씩 다를 수 있습니다. 헷갈리는 자재는 매장(042-545-2900)에 물어보세요.</p></section>
{f'<section class="wrap sec"><h2>관련 영상</h2>{vsplit(yv, "h3")}</section>' if yv else ''}{CTA}""", "/jajae/", ygld)

    # 제품 개별 페이지 (/p/<id>.html)
    jn = {c: (sl, n, d) for c, sl, n, d in JCAT}
    mname = {m["slug"]: m for m in MATS}
    def pcard2(p):
        sub = MCAT.get(subof(p, p["top"]) or "", "")
        return (f'<a class="pd" href="/p/{p["id"]}.html"{_pdata(p)}><span class="pi"><img loading="lazy" src="{E(p["img"])}" alt="{E(p["name"])}"></span><b>{E(p["name"])}</b>{f"<small>{E(sub)}</small>" if sub else ""}</a>')
    for p in PROD:
        if not p["tops"] or p["top"] not in jn: continue
        sl, cn, cd = jn[p["top"]]
        _sp = [r for r in PSPEC.get(str(p["id"]), []) if r and r[0].strip()]
        _sp = [[c.strip() for c in r] for r in _sp][:40]
        _cols = [k for k, nm_ in enumerate(["규격", "단위", "원산지", "수종", "비고"]) if any(r[k] for r in _sp)]
        _sv = lambda v: "재고 문의" if v == "품절" else v
        spec = (f'<h2>{E(p["name"])} 규격</h2><div class="tw"><table class="rt"><thead><tr>' + "".join(f'<th>{["규격", "단위", "원산지", "수종", "비고"][k]}</th>' for k in _cols) + '</tr></thead><tbody>'
                + "".join('<tr>' + "".join((f'<th>{E(r[k])}</th>' if k == 0 else f'<td data-l="{["규격", "단위", "원산지", "수종", "비고"][k]}">{E(_sv(r[k]))}</td>') for k in _cols) + '</tr>' for r in _sp)
                + f'</tbody></table></div><p class="small muted">규격 {len(_sp)}가지 · 표에 없는 크기도 원하는 사이즈로 재단해 드립니다. 가격·재고는 쇼핑몰이나 매장(042-545-2900)에서 확인하세요.</p>') if _sp else ""
        _sz = ", ".join(dict.fromkeys(r[0] for r in _sp))[:70]
        _cov = []
        if not re.search(r"각재|구조재|다루끼|2[xX×*]\d|투바이|원주목|기둥|철물|피스|본드|스테인|오일|페인트", p["name"]):
            for r in _sp:
                d_ = sorted(float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*mm", r[0], flags=re.I))
                if len(d_) not in (2, 3) or d_[-1] < 600 or d_[-2] < 80 or (len(d_) == 3 and d_[0] > 45): continue
                a_ = d_[-1] * d_[-2] / 1e6
                if a_ <= 0: continue
                _cov.append((r[0], a_))
        _cov = list(dict((k, a) for k, a in _cov).items())[:20]
        cov = (f'<h2>{E(p["name"])} — 1평에 몇 장?</h2><div class="tw"><table class="rt"><thead><tr><th>규격</th><th>1장 면적</th><th>1평(3.3㎡)</th><th>10㎡</th></tr></thead><tbody>'
               + "".join(f'<tr><th>{E(k)}</th><td data-l="1장 면적">{a:.2f}㎡</td><td data-l="1평">약 {math.ceil(3.3058 / a)}장</td><td data-l="10㎡">약 {math.ceil(10 / a)}장</td></tr>' for k, a in _cov)
               + '</tbody></table></div><p class="small muted">면적만으로 나눈 수량입니다(자투리·로스 제외). 실제 주문은 5~10% 여유를 두고, 정확한 양은 <a href="/calc.html">자재 계산기</a>로 확인하세요.</p>') if _cov else ""
        _ok_ = (p["top"], sb, tuple(r[0] for r in _sp))  # 색상만 다른 같은 규격 제품은 하나만 검색에 엶
        if _cov and len(_sp) >= 2 and _ok_ not in _PSEEN: POPEN.add(f"p/{p['id']}.html"); _PSEEN.add(_ok_)
        sb = subof(p, p["top"]); sname = MCAT.get(sb or "", "")
        sim = [q for q in PROD if q is not p and q["tops"] and q["top"] == p["top"] and subof(q, q["top"]) == sb][:12]
        if len(sim) < 6: sim += [q for q in PROD if q is not p and q not in sim and q["tops"] and q["top"] == p["top"]][:12 - len(sim)]
        mt = None
        for rx, ms in [(r"OSB", "osb"), (r"MDF", "mdf"), (r"합판", "hapan"), (r"다루끼|각재|구조재|투바이|2[xX×]4", "gujo"), (r"방부", "bangbu"), (r"합성데크|합성목|뉴데크|퀵데크|에코젠", "hapdeck"), (r"집성", "jipseong"),
                       (r"히노끼|편백|삼나무|삼목|적삼목|루바", "hinoki"), (r"석고보드", "gypsum"), (r"사이딩|아이큐브", "siding"), (r"아이소핑크|단열", "insul"), (r"스테인|오일", "stain"),
                       (r"피스|타카|경첩|철물|손잡이", "hardware"), (r"마루|후로링|장판", "maru"), (r"몰딩|걸레받이", "molding"), (r"침목", "chimmok"), (r"타일", "tile"), (r"도어|문틀|합판문", "door"), (r"흡음|방음|타공", "sound")]:
            if re.search(rx, p["name"]): mt = mname.get(ms); break
        use = (f'<h2>{E(mt["name"])} — 어디에 쓰나요?</h2><ul>' + "".join(f"<li>{E(w)}</li>" for w in mt["where"]) + f'</ul><p>{E(mt["effect"])}</p><p><a href="/jajae/{mt["slug"]}.html">{E(mt["name"])} 용도·기준가·시공 영상 자세히 ›</a></p>') if mt else ""
        cat = f"{cn}{' · ' + sname if sname else ''}"
        page(f"p/{p['id']}.html", f"{p['name']} 규격·사진 — {cat} | 대전 영진목재" if _sp else f"{p['name']} — {cat} | 대전 영진목재", (f"{p['name']} 규격: {_sz}. " if _sp else f"{p['name']} ({cat}) 사진. ") + "대전 영진목재(월드건축자재) 매장 취급, 원하는 사이즈 재단·배송.",
             f"""<section class="wrap sec"><p class="crumb"><a href="/jaryo/">전체 자재</a> › <a href="/jaryo/{sl}.html">{E(cn)}</a>{f' › {E(sname)}' if sname else ''}</p>
<div class="g2 pdet"><div><img class="pimg" src="{E(p['img'])}" alt="{E(p['name'])}"></div><div><h1>{E(p['name'])}</h1><p class="muted">{E(cat)}</p>
<p>대전 유성 영진목재(월드건축자재) 3000평 매장에서 실물을 보고 고를 수 있습니다. 원하는 사이즈로 재단해 드리고 대전·세종·공주·계룡·논산·금산·옥천은 배송하고, 그 외 전국은 용달차로 보내 드립니다(운임 견적 → 입금 확인 후 출고). 가격·재고는 쇼핑몰이나 매장(042-545-2900)에서 확인하세요.</p>
<div class="row"><a class="b r" href="https://wwood.kr/home/mall/shoplist.php?idx={p['id']}&amp;pmode=view" target="_blank" rel="noopener">쇼핑몰에서 가격 보기</a><a class="b d" href="tel:{TEL.replace('-','')}">전화 문의</a></div>
<p class="small"><a href="/calc.html">필요한 양 계산하기</a> · <a href="/visit.html">매장 위치</a> · <a href="/jaryo/{sl}.html">{E(cn)} 전체 보기</a></p><div class="ylv pv" data-n="{E(p['name'])}" data-c="{E(cat)}"></div></div></div>{spec}{cov}{use}</section>
<section class="wrap sec"><h2>같은 분류 제품</h2><div class="pg hrow">{"".join(pcard2(q) for q in sim)}</div></section>{CTA}""", "/jaryo/", None, p.get("img0") or p["img"])

    # 매장 카운터 QR 안내판이 여는 페이지(/r/) — 리뷰·채널 링크는 여기서만 바꾸면 됨(재인쇄 불필요)
    RV_NAVER = NPLACE
    RV_GOOGLE = "https://g.page/r/CZcZc9J-M0L0EAE/review"  # 구글 리뷰 바로 쓰기
    RV_KAKAOMAP = "https://map.kakao.com/?q=%EC%98%81%EC%A7%84%EC%A2%85%ED%95%A9%EB%AA%A9%EC%9E%AC"
    rbtn = lambda href, bg, fg, t, sub: f'<a href="{href}" target="_blank" rel="noopener" style="display:block;background:{bg};color:{fg};border-radius:14px;padding:18px 20px;margin:12px 0;text-decoration:none;font-size:20px;font-weight:800">{t}<small style="display:block;font-size:14px;font-weight:500;opacity:.85;margin-top:4px">{sub}</small></a>'
    page("r/index.html", "영진종합목재 방문 리뷰 남기기", "영진종합목재(월드건축자재) 방문 리뷰 남기기(네이버·구글·카카오맵), 자재 정보 보기.",
         '<section class="wrap sec" style="max-width:520px"><h1 style="font-size:26px">방문해 주셔서 감사합니다</h1><p class="lead">리뷰 한 줄이 동네 손님들께 큰 도움이 됩니다.</p>'
         + RVBOX
         + rbtn(RV_KAKAOMAP, "#3b82f6", "#fff", "카카오맵 후기 쓰기", "카카오맵에서 영진종합목재 검색")
         + rbtn("/jajae/", "#333", "#fff", "자재 사진·기준가 보기", "합판·각재·데크·사이딩 등 용도와 기준가")
         + f'<p class="small muted">{ADDR} · {TEL} · {HOURS}</p></section>', "")
    SITEMAP[:] = [u for u in SITEMAP if not u.endswith("/r/")]
    _hp = ["pyeongsang", "chaekjang", "chimdae", "deck", "sinbaljang", "gaejip", "teibeul", "beranda"]
    _hm = [x for k in _hp for x in MK if x[0] == k]
    _nx0 = set(json.load(open(f"{ROOT}/data/new_exclude.json", encoding="utf-8"))) if os.path.exists(f"{ROOT}/data/new_exclude.json") else set()
    _fsx = json.load(open(f"{ROOT}/data/firstseen.json", encoding="utf-8")) if os.path.exists(f"{ROOT}/data/firstseen.json") else {}
    _recent = lambda x, k_: (x[0] in _nx0, -int(_fsx.get(f"{BASE}/{k_}/{x[0]}.html", "9999-99-99").replace("-", "")[:8] or 0) if x[0] not in _nx0 else 0)
    _newmk = sorted([x for x in MK if x[0] not in _nx0], key=lambda x: _recent(x, "mandeul"))[:4]
    _hm = (_newmk + [x for x in _hm if x not in _newmk])[:8]
    _sgh = sorted(SG, key=lambda x: _recent(x, "sigongbeop"))[:8]  # 새 시공법 먼저
    MKHOME = ('<section class="wrap sec" data-tg="make"><h2>DIY 만들기 — 자재와 재단 크기</h2><p class="small muted">만들 것을 고르면 필요한 자재, 몇 mm로 몇 개 자를지, 만드는 순서와 영상까지 나옵니다. 매장에서 그 크기대로 잘라 드려요.</p><div class="mg m2">'
              + "".join(f'<a class="mc" href="/mandeul/{x[0]}.html">' + (f'<img loading="lazy" src="/assets/mandeul/{x[0]}.jpg" alt="{E(x[1])}" style="width:100%;height:auto;border-radius:8px;margin-bottom:6px">' if os.path.exists(f"{ROOT}/assets/mandeul/{x[0]}.jpg") else "") + f'<b>{E(x[1])}</b><small>{E(x[3][:40])}…</small></a>' for x in _hm)
              + f'</div><p><a class="b o" href="/mandeul/">DIY 만들기 {len(MK)}가지 전체 보기 ›</a></p></section>'
              + '<section class="wrap sec" data-tg="make"><h2>인테리어 자재 시공법</h2><p class="small muted">석고보드·루바·사이딩·몰딩·마루·필름·문 교체까지 — 필요한 자재 수량, 그림 설명서, 시공 영상을 정리했습니다. 어려운 공사는 직접 시공도 합니다.</p><div class="mg m2">'
              + "".join(f'<a class="mc" href="/sigongbeop/{x[0]}.html">' + (f'<img loading="lazy" src="/assets/sigongbeop/{x[0]}.jpg" alt="{E(x[1])}" style="width:100%;height:auto;border-radius:8px;margin-bottom:6px">' if os.path.exists(f"{ROOT}/assets/sigongbeop/{x[0]}.jpg") else "") + f'<b>{E(x[1])}</b><small>{E(x[3][:40])}…</small></a>' for x in _sgh)
              + f'</div><p><a class="b o" href="/sigongbeop/">시공법 {len(SG)}가지 전체 보기 ›</a></p></section>')
    # 첫 화면: 제품 사진(제조사)·인테리어 트렌드·우리 동네 시공·전국 배송 — 주요 섹션으로 내부 링크
    import taka as _tkH, taka_data as _tkdH
    _bc = []
    try: _bc.append(("/yerim/", "예림 중문·도어", f"{len(_yrows)}종", _yr0.IMG(_yrows[0][4])))
    except Exception: pass
    if _ylr: _bc.append(("/younglim/", "영림 도어·중문·필름", f"{len(_ylr)}종", _yl0.IMG(next(r for r in _ylr if r[0] == "040300")[6]) if any(r[0] == "040300" for r in _ylr) else _yl0.IMG(_ylr[0][6])))
    if _shr: _bc.append(("/shenu/", "쉐누 도어·몰딩", f"{len(_shr)}종", _sh0.IMG(_shr[0][1])))
    _bc.append(("/taka/", "제일타카 타카·핀", "타카·핀·콤프레셔", _tkH.IMG(_tkdH.TOOLS["interior"][2][0][5])))
    try:
        import samik as _smH
        _smh = _smH.load(ROOT)
        if _smh: _bc.append(("/geonjae/", "목조·외장·내장 건축자재", f"{len(_smh)}종", _smH.IMG(_smh[0][4], _smh[0][2])))
    except Exception: pass
    try:
        import nichiha as _nhH
        _nhh = _nhH.load(ROOT)
        if _nhh: _bc.append(("/nichiha/", "니치하 세라믹 사이딩", f"{len(_nhh)}종", _nhH.TH(_nhh[0][1])))
    except Exception: pass
    try:
        import knauf as _knH
        _knh = _knH.load(ROOT)
        if _knh: _bc.append(("/knauf/", "크나우프 석고보드·천장재·단열재", f"{len(_knh)}종", _knH.IMG(_knh[0][4], 400)))
    except Exception: pass
    try:
        import homewood as _hwH
        _hwh = _hwH.load(ROOT)
        if _hwh: _bc.append(("/suip/", "수입 목조주택 자재·창호", f"{len(_hwh)}종", _hwH.img(next((r["i"] for r in _hwh if "벨룩스" in r["n"]), _hwh[0]["i"]))))
    except Exception: pass
    try:
        import emall as _emH
        _ehc, _ehr = _emH.load(ROOT)
        if _ehr: _bc.append(("/bondex/", "본덱스 스테인·페인트", f"{len(_ehr)}종", _emH.IMG(_ehr[0][3])))
    except Exception: pass
    try:
        import cmbs as _cbH
        _cbc, _cbr = _cbH.load(ROOT)
        if _cbr: _bc.append(("/bupum/", "철물·공구·부속", f"{len(_cbr)}종", _cbH.IMG(_cbr[0][3])))
    except Exception: pass
    _bc.append(("/cheolmul/", "목재 철물", "데크·정자·목조주택", "https://megatie.cafe24.com/web/product/" + _mtj["janseon"][0][1][1:]))
    MKTAIL = ('<div class="gg hmt" style="grid-column:1/-1;min-width:0"><h2 class="gt">제품 사진으로 고르기 <small>옆으로 넘겨 보세요 ›</small></h2><div class="gcs">'
               + "".join(f'<a class="gc gpc" href="{h}"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" width="300" height="300" src="{im}" alt="{E(n)}"><span>{E(n)} <small>{E(k)}</small></span></a>' for h, n, k, im in _bc) + '</div>'
               + '<div class="qk"><a href="/trend/">인테리어 트렌드</a>' + "".join(f'<a href="/trend/{a}.html">{b}</a>' for a, b in (("modern", "모던"), ("natural", "내추럴·우드"), ("japandi", "간살·재팬디"), ("hotel", "호텔·럭셔리"), ("classic", "클래식"))) + '</div>'
               + '<h2 class="gt">우리 동네 시공 (대전·세종)</h2><div class="qk">' + "".join(f'<a href="/local/{a}-{b}.html">{c} {d}</a>' for b, c in (("daejeon", "대전"), ("sejong", "세종")) for a, d in (("jungmun", "중문"), ("door", "방문 교체"), ("film", "필름"), ("molding", "몰딩"), ("wall", "템바보드 벽"))) + '<a href="/local/">동네별 보기 ›</a></div>'
               + '<h2 class="gt">전국 배송 — 재단해서 용달로</h2><div class="qk">' + "".join(f'<a href="/jeonguk/{a}.html">{b}</a>' for a, b, *_ in __import__("nation").REG) + '</div></div>')
    _ip = f"{OUT}/index.html"; _it = open(_ip, encoding="utf-8").read()
    if "<!--MKHOME-->" in _it:
        _it = _it.replace("<!--MKHOME-->", MKHOME)
        _k = _it.find('<div class="card dark"><h2>직접 하기')
        if _k > 0: _it = _it[:_k] + MKTAIL + _it[_k:]
        open(_ip, "w", encoding="utf-8").write(_it)
    # 사이트 전체: 소식·제품·자재 사진·지역×자재 페이지에 "직접 만들어 보기"(완성 그림 카드) 자동 삽입 — 새 글도 빌드 때 자동 적용
    def _mkcard(x):
        im = f'<img loading="lazy" src="/assets/mandeul/{x[0]}.jpg" alt="{E(x[1])}" style="width:100%;height:auto;border-radius:8px;margin-bottom:6px">' if os.path.exists(f"{ROOT}/assets/mandeul/{x[0]}.jpg") else ""
        return f'<a class="mc" href="/mandeul/{x[0]}.html">{im}<b>{E(x[1])}</b><small>재단 크기·그림 설명서·영상</small></a>'
    _MKD = {x[0]: x for x in MK}
    def _mkrel(title, body):
        got = []
        for k, rx in MKV.items():
            if k in _MKD and k not in ("jakeopdae", "beranda", "sinbaljang") and re.search(rx, title) and _MKD[k] not in got: got.append(_MKD[k])
        mats = sorted(((m_.start(), ms) for ms, rx in MATKW.items() for m_ in [re.search(rx, title if ms in ("hardware", "stain") else title + " " + body[:3000])] if m_ and ms in _mkmat), key=lambda t: t[0])
        for _, ms in mats[:2]:
            for x in _mkmat[ms]:
                if x not in got: got.append(x)
        return got[:6]
    for _f in glob.glob(f"{OUT}/news/*.html") + glob.glob(f"{OUT}/p/*.html") + glob.glob(f"{OUT}/jaryo/*.html") + glob.glob(f"{OUT}/daejeon/*.html") + glob.glob(f"{OUT}/sejong/*.html") + glob.glob(f"{OUT}/gongju/*.html") + glob.glob(f"{OUT}/cheongju/*.html") + glob.glob(f"{OUT}/cheonan-asan/*.html") + glob.glob(f"{OUT}/gyeryong-nonsan/*.html") + glob.glob(f"{OUT}/geumsan-okcheon/*.html"):
        if _f.endswith("index.html"): continue
        _t = open(_f, encoding="utf-8").read()
        if "직접 만들어 보기</h2>" in _t or '<section class="cta">' not in _t: continue
        _h1 = re.search(r"<h1[^>]*>(.*?)</h1>", _t, re.S); _h1 = re.sub(r"<[^>]+>", "", _h1.group(1)) if _h1 else ""
        _main = re.sub(r"<[^>]+>", " ", _t.split("<main>")[-1].split('<section class="cta">')[0]) if "/news/" in _f else ""
        _r = _mkrel(_h1, _main)
        _sgm = {ms for ms, rx in MATKW.items() if re.search(rx, _h1)} | {ms for ms in ("hinoki", "siding", "molding", "maru", "film", "door", "sound", "stain") if re.search({"hinoki": r"루바|히노끼|편백", "siding": r"사이딩", "molding": r"몰딩|걸레받이", "maru": r"마루", "film": r"필름", "door": r"도어|문틀|방문", "sound": r"흡음|방음|템바|타공", "stain": r"스테인"}[ms], _h1)}
        _sgr = [x for x in SG if re.search(x[10], _h1) or x[9] in _sgm][:4]
        if _sgr:
            _sgsec = '<section class="wrap sec"><h2>🔨 시공법 보기</h2><div class="mg m2">' + "".join(f'<a class="mc" href="/sigongbeop/{x[0]}.html">' + (f'<img loading="lazy" src="/assets/sigongbeop/{x[0]}.jpg" alt="{E(x[1])}" style="width:100%;height:auto;border-radius:8px;margin-bottom:6px">' if os.path.exists(f"{ROOT}/assets/sigongbeop/{x[0]}.jpg") else "") + f'<b>{E(x[1])}</b><small>자재 수량·그림 설명서·영상</small></a>' for x in _sgr) + '</div></section>'
            _t = _t.replace('<section class="cta">', _sgsec + '<section class="cta">', 1)
        if not _r:
            if _sgr: open(_f, "w", encoding="utf-8").write(_t)
            continue
        _sec = ('<section class="wrap sec"><h2>🪚 직접 만들어 보기</h2><p class="small muted">이 자재로 만들 수 있는 것 — 재단 크기, 그림 설명서, 만들기 영상까지 정리했습니다. 매장에서 그 크기대로 잘라 드려요.</p><div class="mg m2">'
                + "".join(_mkcard(x) for x in _r) + '</div><p><a href="/mandeul/">만들기 전체 보기 ›</a></p></section>')
        open(_f, "w", encoding="utf-8").write(_t.replace('<section class="cta">', _sec + '<section class="cta">', 1))
    for _f in glob.glob(f"{OUT}/jajae/*.html"):
        _t = open(_f, encoding="utf-8").read()
        _t2 = re.sub(r"<!--MK:([\w-]+)-->", lambda mm: SGMAT_HTML.get(mm.group(1), "") + MKMAT_HTML.get(mm.group(1), ""), _t)
        if _t2 != _t: open(_f, "w", encoding="utf-8").write(_t2)
    # 자주 묻는 질문 모음(/faq.html) — 자재·재단·만들기·시공 질문을 한 페이지에
    _mn = {m["slug"]: m["name"] for m in MATS}
    _groups = [("재단·배송", [(q, a_, "/cut.html", "재단 미리보기") for q, a_ in _CF])]
    _mat = []
    for k_, v_ in MFAQ.items():
        for q, a_ in v_[:2]: _mat.append((q, a_, f"/jajae/{k_}.html", _mn.get(k_, "자재 백과")))
    _groups.append(("자재 고르기", _mat))
    _groups.append(("필요한 양 계산", [(q, a_, "/calc.html", "자재 계산기") for q, a_ in CALC_FAQ]))
    for g_ in ("DIY 만들기", "자재 시공법", "자재 가격", "목재 철물", "타카·콤프레셔", "예림 중문·도어"):
        _groups.append((g_, [(q, a_, u_, n_) for gg, qa_, u_, n_ in ALLFAQ if gg == g_ for q, a_ in qa_]))
    _fb = ""; _fld = []; _toc = []
    for gi, (gn, qs) in enumerate(_groups):
        if not qs: continue
        _toc.append(f'<a href="#g{gi}">{E(gn)} ({len(qs)})</a>')
        _fb += f'<h2 id="g{gi}">{E(gn)} <small class="muted" style="font-size:14px">{len(qs)}개 · 옆으로 밀어 보세요 ›</small></h2><div class="fqs faqx">' + "".join(f'<div class="fq"><b>Q. {E(q)}</b><p>{E(a_)} <a href="{u_}">{E(n_)} 보기 ›</a></p></div>' for q, a_, u_, n_ in qs) + '</div>'
        _fld += [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a_}} for q, a_, u_, n_ in qs]
    page("sajin.html", "사진으로 제품 찾기 — 카메라로 찍으면 비슷한 자재·철물 바로 찾기 | 영진목재", "철물·도어·몰딩·스테인·공구를 휴대폰 카메라로 찍으면 영진목재(월드건축자재) 홈페이지 제품 중 가장 비슷한 제품을 바로 찾아 드립니다. 사진은 휴대폰 안에서만 비교합니다.",
         open(ROOT + "/sajin_tpl.html", encoding="utf-8").read().replace("__TEL__", TEL) + CTA, "/sajin.html")
    page("privacy.html", "개인정보처리방침 — 영진종합목재(월드건축자재) 홈페이지·앱", "영진종합목재(월드건축자재) 홈페이지(www.wwood.co.kr)와 영진목재 앱의 개인정보처리방침입니다.",
         f'''<section class="wrap sec"><h1>개인정보처리방침</h1><p class="lead">영진종합목재(월드건축자재, 이하 "회사")는 홈페이지(www.wwood.co.kr)와 영진목재 앱(안드로이드, kr.co.wwood.app)을 운영하며, 이용자의 개인정보를 소중히 다룹니다. 시행일: 2026년 11월 14일</p>
<h2>1. 수집하는 개인정보</h2><p>홈페이지와 앱은 <b>회원가입·로그인이 없으며, 이름·전화번호·주소 등 개인정보를 직접 수집하지 않습니다.</b></p>
<h2>2. 자동으로 처리되는 정보</h2><ul><li><b>방문자 수 집계</b>: 하루 방문 여부를 기기 안(쿠키·로컬 저장소)에 날짜로만 기록하고, 외부 집계 서비스에 "방문 1회"와 유입 경로(유튜브·네이버·구글 등 사이트 이름)만 보냅니다. 개인을 알아볼 수 있는 정보는 보내지 않습니다.</li><li><b>앱 저장 공간</b>: 인터넷이 약할 때도 볼 수 있도록 본 페이지를 기기 안에만 저장합니다(서비스워커 캐시). 회사로 전송되지 않습니다.</li><li><b>외부 콘텐츠</b>: 유튜브 영상, 구글 글꼴, 제조사 제품 사진(예림·영림·쉐누·니치하·본덱스·철물박사 등)은 해당 회사 서버에서 불러오며, 이때 그 회사가 자체 방침에 따라 접속 정보(IP 등)를 처리할 수 있습니다.</li></ul>
<h2>3. 이용자가 직접 연락하는 경우</h2><p>전화({TEL}), 이메일({EMAIL}), 카카오톡·문자 등으로 견적·재단·배송을 문의하시면, 그 답변과 거래 처리를 위해서만 연락처·주소를 이용하며 관계 법령에 따른 보관 기간이 지나면 파기합니다.</p>
<h2>4. 제3자 제공·위탁</h2><p>법령에 따른 경우를 제외하고 개인정보를 제3자에게 제공하지 않습니다.</p>
<h2>5. 이용자의 권리</h2><p>쿠키·앱 저장 정보는 브라우저 설정이나 앱 삭제로 언제든 지울 수 있습니다. 문의하신 연락처 정보의 열람·정정·삭제를 요청하실 수 있습니다.</p>
<h2>6. 문의처</h2><p>영진종합목재(월드건축자재) · {ADDR} · 전화 {TEL} · 이메일 <a href="mailto:{EMAIL}">{EMAIL}</a></p></section>''', "")
    page("faq.html", f"목재·합판 자주 묻는 질문 {len(_fld)}가지 — 재단·가격·만들기·시공 | 영진목재", "합판 재단, 자재 고르기, 필요한 양 계산, DIY 만들기 자재비, 석고보드·사이딩·마루 시공까지 손님들이 자주 묻는 질문과 답을 모았습니다. 대전 영진종합목재.",
         f'<section class="wrap sec"><h1>자주 묻는 질문</h1><p class="lead">매장과 전화로 가장 많이 받는 질문을 모았습니다. 찾는 답이 없으면 042-545-2900으로 물어보세요.</p><div class="gsrch"><span>🔍</span><input id="fq" type="search" placeholder="질문 검색 (예: 재단, 몇 장, 평상, 석고보드)" autocomplete="off" aria-label="질문 검색"></div><p class="small">{" · ".join(_toc)}</p>{_fb}</section>'
         + '<style>.faqx details{background:#fff;border:1px solid var(--line);border-radius:12px;margin:0 0 8px;padding:0 14px}.faqx summary{cursor:pointer;font-weight:700;padding:12px 0;list-style:none}.faqx summary::-webkit-details-marker{display:none}.faqx summary:before{content:"Q. ";color:var(--red)}.faqx p{margin:0 0 12px;color:var(--mut)}</style>'
         + '<script>(function(){var q=document.getElementById("fq"),D=[].slice.call(document.querySelectorAll(".faqx .fq"));q.addEventListener("input",function(){var v=q.value.replace(/\\s/g,"");D.forEach(function(d){var ok=!v||d.textContent.replace(/\\s/g,"").indexOf(v)>=0;d.style.display=ok?"":"none";d.open=!!v&&ok});[].forEach.call(document.querySelectorAll(".faqx"),function(x){var h=x.previousElementSibling,n=[].some.call(x.querySelectorAll(".fq"),function(d){return d.style.display!="none"});x.style.display=n?"":"none";if(h)h.style.display=n?"":"none"})})})();</script>' + CTA, "",
         {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": _fld[:120]})
    # 속도: 유튜브 iframe → 썸네일+재생 버튼(누르면 그때 영상 로드). 페이지가 훨씬 빨리 뜸(구글 순위 요소)
    _yrx = re.compile(r'<iframe[^>]*src="https://www\.youtube\.com/embed/([A-Za-z0-9_-]{11})[^"]*"([^>]*)></iframe>')
    def _yf(m):
        t = re.search(r'title="([^"]*)"', m.group(0)); t = t.group(1) if t else "영상"
        return f'<button type="button" class="ytf" data-id="{m.group(1)}" aria-label="{t} 재생"><img src="https://i.ytimg.com/vi/{m.group(1)}/hqdefault.jpg" loading="lazy" decoding="async" alt="{t}"><span class="ytp"></span></button>'
    for _f in glob.glob(f"{OUT}/**/*.html", recursive=True):
        _t = open(_f, encoding="utf-8").read()
        if "youtube.com/embed/" in _t and "<iframe" in _t:
            _t2 = _yrx.sub(_yf, _t)
            if 'fetchpriority="high"' not in _t: _t2 = _t2.replace('/hqdefault.jpg" loading="lazy" decoding="async"', '/hqdefault.jpg" fetchpriority="high"', 1)  # 첫 영상 썸네일은 바로(화면 첫 그림)
            _fm = re.search(r'src="(https://i\.ytimg\.com/vi/[^"/]+/hqdefault\.jpg)" fetchpriority="high"', _t2)
            if _fm and 'rel="preload" as="image"' not in _t2: _t2 = _t2.replace('<meta charset="utf-8">', f'<meta charset="utf-8"><link rel="preconnect" href="https://i.ytimg.com"><link rel="preload" as="image" href="{_fm.group(1)}" fetchpriority="high">', 1)
            if _t2 != _t: open(_f, "w", encoding="utf-8").write(_t2)
    # NEW 표시 — 7일 안에 새로 올라온 DIY 만들기·시공법·유튜브 영상/쇼츠·소식 글 카드
    _nd = datetime.date.today(); _NEWD = 7
    def _isnew(d):
        try: return 0 <= (_nd - datetime.date.fromisoformat(d[:10])).days < _NEWD
        except Exception: return False
    _fs0 = json.load(open(f"{ROOT}/data/firstseen.json", encoding="utf-8")) if os.path.exists(f"{ROOT}/data/firstseen.json") else {}
    _nx = set(json.load(open(f"{ROOT}/data/new_exclude.json", encoding="utf-8"))) if os.path.exists(f"{ROOT}/data/new_exclude.json") else set()
    _newpg = set()
    for x in MK + SG:
        k_ = "mandeul" if x in MK else "sigongbeop"
        if x[0] not in _nx and _isnew(_fs0.get(f"{BASE}/{k_}/{x[0]}.html", _nd.isoformat())): _newpg.add(f"/{k_}/{x[0]}.html")
    for p_ in POSTS:
        if _isnew(p_.get("date", "")): _newpg.add(f"/news/{p_['slug']}.html")
    _newv = set()
    for l_ in open(f"{ROOT}/data/yt_all.tsv", encoding="utf-8") if os.path.exists(f"{ROOT}/data/yt_all.tsv") else []:
        r_ = l_.split("\t")
        try:
            if 0 <= (datetime.datetime.now().timestamp() - int(r_[3])) < _NEWD * 86400: _newv.add(r_[0])
        except Exception: pass
    _NB = '<i class="newb">NEW</i>'
    _rxp = re.compile(r'(<a class="(?:mc|pc)" href="(/(?:mandeul|sigongbeop|news)/[^"]+\.html)">)')
    _rxv = re.compile(r'(<a class="vc[^"]*" href="[^"]*"[^>]*data-yt="([^"]+)">)')
    for _dp, _dn, _fn in os.walk(OUT):
        for _n in _fn:
            if not _n.endswith(".html"): continue
            _f = os.path.join(_dp, _n); _t = open(_f, encoding="utf-8").read()
            _t2 = _rxp.sub(lambda m: m.group(1) + (_NB if m.group(2) in _newpg else ""), _t)
            _t2 = _rxv.sub(lambda m: m.group(1) + (_NB if m.group(2) in _newv else ""), _t2)
            if "<main>" in _t2:
                _h, _m = _t2.split("<main>", 1); _m, _e = _m.split("</main>", 1) if "</main>" in _m else (_m, "")
                _m = re.sub(r'<a href="([^"]+)"((?: target="_blank" rel="noopener")?)>([^<>]{1,40}?)\s*(?:→|›)</a>', lambda m: f'<a class="mr" href="{m.group(1)}"{m.group(2)}>{m.group(3).strip()}<i>›</i></a>', _m)
                def _q2(m):
                    ls = re.findall(r'<a (?:class="mr" )?href="[^"]+"[^>]*>.*?</a>', m.group(1))
                    rest = re.sub(r'<a [^>]*>.*?</a>|\s|·|<i>›</i>', "", m.group(1))
                    return ('<div class="qk qk2"><b>👉 함께 보기</b>' + "".join(re.sub(r'class="mr" |<i>›</i>', "", l) for l in ls) + '</div>') if ls and not rest else m.group(0)
                _m = re.sub(r'<p>👉 (.*?)</p>', _q2, _m)
                _t2 = _h + "<main>" + _m + ("</main>" + _e if _e or "</main>" in _t2 else "")
            if _t2 != _t: open(_f, "w", encoding="utf-8").write(_t2)
    print("NEW:", len(_newpg), "pages,", len(_newv), "videos")
    for rs, (ra, _r1, _r2) in RA.items():
        if rs in ("daejeon", "sejong"): continue
        _af = f"{OUT}/{rs}.html"
        if os.path.exists(_af):
            _at = open(_af, encoding="utf-8").read()
            if f'href="/{rs}/' not in _at:
                _sec = f'<section class="wrap sec"><h2>{ra}에서 많이 찾는 목재·자재</h2><div class="mg m2">' + "".join(f'<a class="mc" href="/{rs}/{m["slug"]}.html"><b>{ra} {m["name"]}</b><small>{m["where"][0]}</small></a>' for m in MATS) + '</div></section>'
                _at = _at.replace('<section class="cta">', _sec + '<section class="cta">', 1)
                open(_af, "w", encoding="utf-8").write(_at)
    # 전체 페이지 모아보기(HTML 사이트맵) — 깊숙한 페이지까지 검색로봇이 2번 클릭 안에 닿게
    _SECN = {"": "기본 안내", "jaryo": "전체 자재", "gagyeok": "자재 가격 가이드", "yesi": "몇 평이면 얼마? 예시 견적", "local": "지역별 시공", "yeongyeol": "공정별 시공팀 연결",
             "tteori": "떨이몰", "mandeul": "DIY 만들기", "sigongbeop": "자재 시공법", "jajae": "자재 백과", "cheolmul": "목재 철물", "taka": "타카·타카핀",
             "yerim": "예림 중문·도어", "younglim": "영림 도어·중문·필름", "shenu": "쉐누 도어·몰딩", "bupum": "철물·공구·부속", "bondex": "본덱스 스테인·페인트",
             "nichiha": "니치하 세라믹 사이딩", "geonjae": "목조·외장·내장 건축자재", "knauf": "크나우프 석고보드·단열재", "suip": "수입 목조주택 자재·창호", "trend": "인테리어 트렌드", "jeonguk": "전국 배송 지역",
             "sigong": "시공 사례", "video": "시공 영상", "v": "영상별 페이지", "news": "소식", "bigyo": "자재 비교", "daejeon": "대전", "sejong": "세종", "p": "상품 안내", "gongju": "공주", "cheongju": "청주", "cheonan-asan": "천안·아산", "gyeryong-nonsan": "계룡·논산", "geumsan-okcheon": "금산·옥천"}
    _grp = {}
    for _u in SITEMAP:
        if "/bupum/p/" in _u: continue  # 철물박사 상품 6천여 개는 빼서 핵심 페이지 목록을 가볍게
        if re.search(r"/p/[^/]+\.html$", _u) or re.search(r"/apt/[a-z]+/[^/]+\.html$", _u): continue  # 제품 상세·아파트 동 페이지는 각 목록(/…/p/, /apt/)과 XML 사이트맵으로
        _p = _u[len(BASE) + 1:]
        _k = _p.split("/")[0] if "/" in _p else ""
        _pp = (_p if _p.endswith(".html") else _p + "index.html") or "index.html"
        _ti = (PGMETA.get(_pp) or PGMETA.get(_p) or (_p,))[0]
        _grp.setdefault(_k, []).append((_u[len(BASE):], _ti))
    _order = [k for k in _SECN if k in _grp] + sorted(k for k in _grp if k not in _SECN)
    _jb = '<section class="wrap sec"><h1>전체 페이지 모아보기</h1><p class="lead">영진종합목재 홈페이지의 모든 안내 페이지를 분류별로 모았습니다. 찾는 자재·시공·지역을 눌러 보세요.</p><div class="jcx">' + "".join(f'<a href="#g-{k or "home"}">{_SECN.get(k, k)} <small>{len(_grp[k])}</small></a>' for k in _order) + '</div>'
    for k in _order:
        _jb += f'<h2 id="g-{k or "home"}">{_SECN.get(k, k)} <small>({len(_grp[k])})</small></h2><ul class="jcl">' + "".join(f'<li><a href="{h}">{E(t)}</a></li>' for h, t in _grp[k]) + '</ul>'
    _jb += '</section>'
    page("jeonche.html", "전체 페이지 모아보기 — 자재·가격·시공·지역 한눈에 | 영진목재", f"영진종합목재 홈페이지 전체 {len(SITEMAP)}개 페이지를 자재·가격·시공법·지역별로 모아 둔 목록입니다.", _jb)
    # robots, sitemap
    if PREVIEW: print(len(SITEMAP), "preview pages →", OUT); return
    json.dump({"cats": [[c, n, d] for c, n, d in CATS], "v": [[v["id"], v["type"], v["cat"], v["n"], v["title"]] for v in V]}, open(f"{OUT}/assets/videos.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))  # wwood.kr 시공영상 페이지용
    # 404 — 없는 주소로 들어온 손님을 주요 페이지로
    # 페이지를 만든 뒤 끼워 넣은 카드 사진까지 썸네일로(첫 화면 등)
    for _hf in glob.glob(f"{OUT}/**/*.html", recursive=True):
        _ht = open(_hf, encoding="utf-8").read()
        if 'loading="lazy" src="/assets/' not in _ht: continue
        _h2 = _thumbs(_ht)
        if _h2 != _ht: open(_hf, "w", encoding="utf-8").write(_h2)
    open(f"{OUT}/404.html", "w", encoding="utf-8").write(open(f"{OUT}/index.html", encoding="utf-8").read().split("<main>")[0].replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="x-canonical"').replace(re.search(r"<title>.*?</title>", open(f"{OUT}/index.html", encoding="utf-8").read()).group(0), "<title>페이지를 찾을 수 없어요 | 영진목재</title>").replace(re.search(r'<meta name="description" content="[^"]*">', open(f"{OUT}/index.html", encoding="utf-8").read()).group(0), '<meta name="description" content="찾으시는 페이지가 없습니다. 영진목재 홈페이지 처음 화면이나 전체 자재에서 찾아보세요.">') + '<main><section class="wrap sec"><div id="vwait" hidden style="background:#fff8e6;border:2px solid #f0c040;border-radius:14px;padding:18px 20px;margin:0 0 22px"><h1 style="margin:0 0 8px">올려주신 사진을 확인하고 있어요</h1><p class="lead" style="margin:0">사진은 잘 받았어요. 얼굴·번호판을 가리고 자재 표시를 단 뒤 이 주소에 공개돼요(보통 반나절~하루). 조금 뒤에 다시 열어 주세요. 급하면 매장 042-545-2900.</p></div><div id="nf404"><h1>찾으시는 페이지가 없어요</h1><p class="lead">주소가 바뀌었거나 없어진 페이지입니다. 아래에서 찾아보세요.</p></div><script>if(/\/(mandeul|sigongbeop|gonggan)\/v-[0-9a-z]{10,40}\.html$/.test(location.pathname)){document.getElementById("vwait").hidden=false;var h=document.getElementById("nf404");if(h)h.hidden=true}</script><div class="row"><a class="b r" href="/">처음으로</a><a class="b o" href="/jaryo/">전체 자재</a><a class="b o" href="/cut.html">재단 미리보기</a><a class="b o" href="/price.html">기준가</a><a class="b o" href="/mandeul/">DIY 만들기</a><a class="b o" href="/sigongbeop/">자재 시공법</a><a class="b o" href="/faq.html">자주 묻는 질문</a><a class="b d" href="/visit.html">매장 안내</a></div></section></main></body></html>')
    # 사장님용 방문 통계(검색 제외, 메뉴 링크 없음)
    os.makedirs(f"{OUT}/stats", exist_ok=True)
    open(f"{OUT}/stats/index.html", "w", encoding="utf-8").write("""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>방문 통계 · 영진종합목재</title><meta name="description" content="영진종합목재 홈페이지 방문 통계(사장님용).">
<style>body{font-family:Pretendard,'Noto Sans KR',sans-serif;background:#f6f3ee;color:#1d1b18;margin:0;padding:18px;max-width:640px;margin:auto}h1{font-size:22px}.k{display:flex;gap:10px}.k div{flex:1;background:#fff;border:1px solid #e4ded4;border-radius:14px;padding:14px}.k b{display:block;font-size:30px}small{color:#5e574e}
table{width:100%;border-collapse:collapse;background:#fff;border-radius:14px;overflow:hidden;margin-top:14px;font-size:15px}th,td{padding:10px;border-bottom:1px solid #eee;text-align:right}th:first-child,td:first-child{text-align:left}th{background:#1d1b18;color:#fff;font-weight:700}.bar{height:8px;background:#c62a1f;border-radius:4px;display:inline-block;vertical-align:middle;margin-left:6px}</style></head><body>
<h1>www.wwood.co.kr 방문 통계</h1><div class="k"><div><small>오늘 방문</small><b id="td">…</b></div><div><small>전체 방문(누적)</small><b id="tt">…</b></div></div><p><small>같은 사람(같은 휴대폰·컴퓨터)이 하루에 여러 번 들어와도 그날은 1명으로 셉니다. 전체 방문은 날마다 방문자를 더한 누적입니다. 검색 로봇은 세지 않습니다.</small></p>
<table id="src"><tr><th>어디서 왔나</th><th>오늘</th><th>누적</th></tr></table>
<table id="ev"><tr><th>앱·저장·주문</th><th>오늘</th><th>누적</th></tr></table><p><small>앱 설치는 크롬·삼성인터넷에서 설치를 끝까지 누른 횟수예요. 아이폰은 홈 화면 추가 여부를 알 수 없어 안내 화면을 본 횟수로 셉니다. 브라우저 즐겨찾기(별표)는 어떤 사이트도 셀 수 없어요. 2026-11-16부터 집계.</small></p>
<table id="days"><tr><th>날짜</th><th>방문</th></tr></table>
<p id="note" style="display:none;background:#fff3f2;border:1px solid #f3c2bd;color:#c62a1f;padding:12px;border-radius:12px">카운터 서버 응답이 늦어 일부 숫자는 이 기기에서 마지막으로 확인한 값으로 보여 드려요. 방문 기록은 손님 기기에 잠시 저장됐다가 서버가 살아나면 다시 보내져서 빠지지 않습니다.</p>
<p><small>같은 사람이 하루에 여러 번 들어와도 1번으로 셉니다. 경로 집계는 2026-11-11 오후부터 시작했어요.</small></p>
<script>
var b="https://abacus.jasoncameron.dev/get/wwood-co-kr/",S=[["yt","유튜브"],["naver","네이버"],["google","구글"],["daum","다음·카카오"],["bing","빙"],["daangn","당근"],["wwoodkr","쇼핑몰(wwood.kr)"],["etc","다른 사이트"],["direct","주소 입력·즐겨찾기"]];
var fail=0,Q=[],act=0;function pump(){while(act<6&&Q.length){act++;Q.shift()()}}
var C={};try{C=JSON.parse(localStorage.getItem("wws")||"{}")}catch(e){}function sv(){try{localStorage.setItem("wws",JSON.stringify(C))}catch(e){}}
function g1(k,n){return fetch(b+k,{cache:"no-store"}).then(function(r){if(r.status==404)return {value:0};if(!r.ok)throw r.status;return r.json()}).then(function(j){var v=j.value||0;if(C[k]==null||v>=C[k]){C[k]=v;sv()}return C[k]}).catch(function(e){if(n<2)return new Promise(function(ok){setTimeout(ok,1200*(n+1))}).then(function(){return g1(k,n+1)});fail++;return C[k]!=null?C[k]:0})}
function g(k){return new Promise(function(ok){Q.push(function(){g1(k,0).then(function(v){act--;pump();ok(v)})});pump()})}
setInterval(function(){if(fail){var p=document.getElementById("note");p.style.display="block"}},3000);
function day(i){return new Date(Date.now()+9*3600e3-i*864e5).toISOString().slice(0,10).replace(/-/g,"")}
var k=day(0);g("d"+k).then(function(v){td.textContent=v.toLocaleString()});g("total").then(function(v){tt.textContent=v.toLocaleString()});
var mx=1,RW=[];S.forEach(function(s,i){var t=document.createElement("tr");t.innerHTML="<td>"+s[1]+"</td><td>…</td><td>…<span class=bar></span></td>";document.getElementById("src").appendChild(t);RW[i]=t;
 g("src-"+s[0]+"-d"+k).then(function(v){t.children[1].textContent=v.toLocaleString()});g("src-"+s[0]).then(function(v){t.dataset.v=v;mx=Math.max(mx,+v||0);t.children[2].firstChild.textContent=(+v).toLocaleString();RW.forEach(function(r){if(r.dataset.v!=null)r.querySelector(".bar").style.width=Math.round((+r.dataset.v||0)/mx*60)+"px"})})});
var EV=[["appinstall","앱 설치(홈 화면 추가)"],["appguide","아이폰 홈 화면 안내 본 횟수"],["appopen","앱으로 들어온 사람(하루 1번)"],["hjsave","내 현장함 저장"],["order","미리 재단 주문서 보냄"],["share","공유 버튼 누름"]];
EV.forEach(function(s){var t=document.createElement("tr");t.innerHTML="<td>"+s[1]+"</td><td>…</td><td>…</td>";document.getElementById("ev").appendChild(t);g("ev-"+s[0]+"-d"+k).then(function(v){t.children[1].textContent=v.toLocaleString()});g("ev-"+s[0]).then(function(v){t.children[2].textContent=v.toLocaleString()})});
[0,1,2,3,4,5,6].forEach(function(i){var d=day(i),t=document.createElement("tr");t.innerHTML="<td>"+d.slice(4,6)+"/"+d.slice(6)+(i?"":" (오늘)")+"</td><td>…</td>";document.getElementById("days").appendChild(t);g("d"+d).then(function(v){t.children[1].textContent=v.toLocaleString()})});
</script></body></html>""")
    open(f"{OUT}/b4237bce57cfb60c93b64e5203857f41.txt", "w").write("b4237bce57cfb60c93b64e5203857f41")  # IndexNow 키(네이버·빙)
    # RSS (네이버 서치어드바이저 RSS 제출용)
    def _rfc(d):
        try: return datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%a, %d %b %Y 09:00:00 +0900")
        except Exception: return ""
    items = "".join(f"<item><title>{html.escape(p['title'])}</title><link>{BASE}/news/{p['slug']}.html</link><guid>{BASE}/news/{p['slug']}.html</guid><pubDate>{_rfc(p.get('date',''))}</pubDate><description>{html.escape(p.get('desc',''))}</description><content:encoded><![CDATA[{p['body'].replace(']]>',']]&gt;').replace('href="/', 'href="'+BASE+'/').replace('src="/', 'src="'+BASE+'/')}]]></content:encoded></item>\n" for p in POSTS[:50])
    # DIY 만들기·시공법도 RSS에(처음 올라간 날짜 기록) — 네이버가 새 글을 빨리 가져가게
    _fsf = f"{ROOT}/data/firstseen.json"
    _fs = json.load(open(_fsf, encoding="utf-8")) if os.path.exists(_fsf) else {}
    _today = datetime.date.today().isoformat(); _ex = []
    for x in MK:
        u = f"{BASE}/mandeul/{x[0]}.html"; _fs.setdefault(u, _today); _ex.append((_fs[u], x[2].split(" — ")[0] + " — DIY 만들기 자재·재단 크기", u, x[3], f"/assets/mandeul/{x[0]}.jpg"))
    for x in SG:
        u = f"{BASE}/sigongbeop/{x[0]}.html"; _fs.setdefault(u, _today); _ex.append((_fs[u], x[2].split(" — ")[0], u, x[3], f"/assets/sigongbeop/{x[0]}.jpg"))
    for _pth, (_t, _d, _im) in PGMETA.items():  # 평수별 자재비·시공팀 연결·지역 시공·공정 플래너·떨이몰도 RSS에
        if _noidx(_pth) or not re.match(r"(yesi|yeongyeol|local|tteori)/|gongjeong\.html|jaedan-bi\.html|hyeonjang\.html", _pth) or _pth.endswith("hyeonjang.html"): continue
        u = BASE + "/" + _pth.replace("index.html", ""); _fs.setdefault(u, _today)
        _ex.append((_fs[u], _t, u, _d, (_im or "").replace(BASE, "") or "/assets/icon-512.png"))
    json.dump(_fs, open(_fsf, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    _ex.sort(key=lambda t: t[0], reverse=True)
    items += "".join(f"<item><title>{html.escape(t)}</title><link>{u}</link><guid>{u}</guid><pubDate>{_rfc(d)}</pubDate><description>{html.escape(ld)}</description>"
                     + (f'<content:encoded><![CDATA[<p><img src="{BASE}{im}" alt="{html.escape(t)}"></p><p>{html.escape(ld)}</p>]]></content:encoded>' if os.path.exists(ROOT + im.replace("/assets", "/assets", 1)) or True else "") + "</item>\n" for d, t, u, ld, im in _ex[:220])
    open(f"{OUT}/rss.xml", "w", encoding="utf-8").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel><title>영진종합목재 소식·자재 정보</title><link>{BASE}/news/</link><description>대전 영진종합목재(월드건축자재) 자재 정보와 시공 소식</description><language>ko</language>\n{items}</channel></rss>\n')
    # wwood.kr(쇼핑몰) 상품 사이트맵 — 서치콘솔에서 두 사이트 모두 소유 확인되어 교차 제출 가능
    _ids = []
    for _p in open(ROOT + "/data/wwoodkr_products.txt").read().strip().split(","):
        _a, _, _b = _p.partition("-"); _ids += range(int(_a), int(_b or _a) + 1)
    _cats = "22,22-133,22-132,22-139,22-316,22-317,22-128,22-129,39-296,23,23-134,23-135,23-136,23-137,23-314,24,24-140,24-141,24-318,24-319,24-320,26,26-149,26-148,26-247,26-315,26-152,25,25-144,25-145,25-146,25-147,25-249,25-266,28,28-167,28-168,28-172,28-248,27,27-156,27-321,27-157,27-159,27-160,27-161,27-237,27-166,27-322,27-163,27-381,31,31-186,31-331,31-188,29,29-274,29-367,30,30-182,30-183,30-184,30-351,32,32-332,32-333,32-334,53,53-348,53-349,54,54-373,54-375,54-378,54-374,54-380,54-391,35,35-356,35-206,35-357,37,37-400,37-396,37-397,37-361,37-362,37-363,37-366,37-360,58,58-405,58-407,58-404,58-406,58-408,58-403,58-409,58-411,58-412,59,59-422,59-423,59-424,59-425".split(",")
    _cu = [("https://wwood.kr/home/mall/shoplist.php?depth=1&amp;code1_idx=" + c) if "-" not in c else ("https://wwood.kr/home/mall/shoplist.php?depth=2&amp;code1_idx=%s&amp;code2_idx=%s" % tuple(c.split("-"))) for c in _cats]
    _pu = ["https://wwood.kr/home/mall/shoplist.php?idx=%d&amp;pmode=view" % i for i in _ids]
    # 전국 배송 지역 → 외벽 사이딩 전국 시공 안내
    for _f in glob.glob(os.path.join(OUT, "jeonguk", "*.html")):
        _h = open(_f, encoding="utf-8").read()
        if "sdbox" in _h: continue
        _m = re.search(r"<h1>([^<]*)", _h); _rn = re.sub(r"\s*(목재|건축자재|자재).*$", "", _m.group(1)) if _m else ""
        _box = ('<section class="wrap sec sdbox"><a class="jfb" href="/yeongyeol/siding.html"><b>🏠 ' + E(_rn) + ' 외벽 사이딩 공사도 직접 합니다</b>'
                '<span>세라믹사이딩·시멘트사이딩·금속사이딩 — 월드아키텍쳐(실내건축공사업) 전국 직접 시공, 자재는 용달로 함께</span><u>외벽 시공 보기 ›</u></a></section>')
        _i = _h.rfind('<section class="wrap sec shr">')
        if _i < 0: _i = _h.rfind("</main>")
        if _i > 0: open(_f, "w", encoding="utf-8").write(_h[:_i] + _box + _h[_i:])
    # 떨이몰 상품을 관련 페이지에 연결(문짝 → 문·중문 페이지, 판재·고재 → 내장재 페이지)
    try:
        import tteori as _ttm
        _tti = [d for d in _ttm.load(ROOT) if d["status"] != "판매완료"]
        _ttmap = [(r"문짝|방문|도어", ["gagyeok/door-gagyeok", "yeongyeol/shassi", "local/door-daejeon", "local/door-sejong", "yerim/index", "younglim/index", "shenu/index"]),
                  (r"판재|고재|패널|루바", ["gagyeok/tempa-board", "gagyeok/hinoki-ruba", "trend/index"]),
                  (r"테이블|좌탁|가구|벤치", ["mandeul/index", "yeongyeol/gagu", "mandeul/benchi"]), (r"천장재|흡음", ["knauf/index", "sigongbeop/seokgo-cheonjang", "yesi/gypsum-ceiling-5py"]), (r"데코타일", ["sigongbeop/decotile", "yeongyeol/decotile"])]
        for _rx, _pgs in _ttmap:
            _its = [d for d in _tti if re.search(_rx, d["title"])]
            if not _its: continue
            _cards = "".join('<a class="ttm" href="/tteori/' + d["id"] + '.html">' + (('<img loading="lazy" width="300" height="300" src="' + (("/assets/t/tteori/" + os.path.splitext(d["photos"][0])[0] + ".webp") if os.path.exists(ROOT + "/assets/t/tteori/" + os.path.splitext(d["photos"][0])[0] + ".webp") else ("/assets/tteori/" + d["photos"][0])) + '" alt="' + E(d["title"]) + '">') if d["photos"] else '') + '<b>' + E(d["title"]) + '</b><span>' + ((_ttm.won(d["price"]) + ("/" + E(d["unit"]) if d["unit"] else "")) if d["price"] else "매장 문의") + '</span></a>' for d in _its[:6])
            _box = ('<section class="wrap sec ttbx"><h2 class="tth">🏷 떨이몰 <small>수량 한정 재고 정리 · 옆으로 넘겨 보세요 ›</small></h2><div class="ttmr">' + _cards + '<a class="ttm ttall" href="/tteori/"><b>떨이몰 전체 보기 ›</b></a></div></section>')
            for _k in _pgs:
                _f = os.path.join(OUT, _k + ".html")
                if not os.path.exists(_f): continue
                _h = open(_f, encoding="utf-8").read()
                if "ttbx" in _h: continue
                _i = _h.rfind('<section class="wrap sec shr">')
                if _i < 0: _i = _h.rfind("</main>")
                if _i > 0: open(_f, "w", encoding="utf-8").write(_h[:_i] + _box + _h[_i:])
    except Exception as _e:
        print("tteori link skip", _e)
    # 시공법·만들기 → 평수별 자재비 예시 연결
    for _k, _kind in {"sigongbeop/seokgo-byeok": "석고보드", "sigongbeop/seokgo-cheonjang": "석고보드", "sigongbeop/rubaa-cheonjang": "루바",
                      "sigongbeop/siding-oebyeok": "사이딩", "sigongbeop/ceramic-siding": "사이딩", "sigongbeop/metal-siding": "사이딩", "sigongbeop/tempa-byeok": "템바보드",
                      "sigongbeop/hapdeck-sigong": "데크", "sigongbeop/deck-gyedan": "데크", "sigongbeop/deck-nangan": "데크", "sigongbeop/isopink-badak": "단열재",
                      "mandeul/deck": "데크", "mandeul/deckgyedan": "데크", "mandeul/dannyeolbyeok": "단열재", "mandeul/gabyeok": "석고보드"}.items():
        _f = os.path.join(OUT, _k + ".html")
        _ls = [l for l in _ys.LINKS if l[0] == _kind]
        if not os.path.exists(_f) or not _ls: continue
        _h = open(_f, encoding="utf-8").read()
        if "ylinks" in _h: continue
        _box = ('<section class="wrap sec ylinks"><h2>' + E(_kind) + ' 몇 평이면 얼마? 평수별 자재비</h2><div class="ylk">'
                + "".join(f'<a href="/yesi/{sl}.html"><b>{E(t)}</b><small>{lo:,}원~</small></a>' for _, sl, t, lo, hi in _ls)
                + '</div><p class="hsh">옆으로 넘겨 보세요 ›</p></section><style>.ylk{display:flex;gap:8px;overflow-x:auto;padding:2px 0 8px;scrollbar-width:none}.ylk a{flex:0 0 auto;display:flex;flex-direction:column;gap:2px;background:#fff;border:1px solid #ece6dc;border-radius:14px;padding:10px 14px;color:#1D1B18;text-decoration:none}.ylk b{font-size:14px}.ylk small{color:#c41a1f;font-weight:800;font-size:12.5px}</style>')
        _i = _h.rfind('<section class="wrap sec shr">')
        if _i < 0: _i = _h.rfind("</main>")
        if _i > 0: open(_f, "w", encoding="utf-8").write(_h[:_i] + _box + _h[_i:])
    open(f"{OUT}/wwoodkr-sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n<url><loc>https://wwood.kr/home/mall/</loc></url>\n<url><loc>https://wwood.kr/home/sub05/video.php</loc></url>\n' + "".join(f"<url><loc>{u}</loc></url>\n" for u in [f"https://wwood.kr/home/mall/board2.php?pmode=view&amp;idx={l.strip()}" for l in (open(f"{ROOT}/data/wwoodkr_posts.txt").read().split() if os.path.exists(f"{ROOT}/data/wwoodkr_posts.txt") else [])] + _cu + _pu) + "</urlset>\n")
    # wwood.kr(쇼핑몰)용 RSS — wwood.kr/home/mall/rss.php 가 이 파일을 그대로 내보냄(네이버 RSS 제출용). 가격 없음.
    _psx = json.load(open(f"{ROOT}/data/pspec.json", encoding="utf-8")) if os.path.exists(f"{ROOT}/data/pspec.json") else {}
    _fsf2 = f"{ROOT}/data/firstseen.json"; _fs2 = json.load(open(_fsf2, encoding="utf-8")) if os.path.exists(_fsf2) else {}
    _ri = []
    for _p in sorted(PROD, key=lambda q: -int(q["id"]))[:60]:
        _u = f"https://wwood.kr/home/mall/shoplist.php?idx={_p['id']}&pmode=view"
        _d = _fs2.setdefault(_u, datetime.date.today().isoformat())
        _sz = ", ".join(dict.fromkeys(r[0].strip() for r in _psx.get(str(_p["id"]), []) if r and r[0].strip()))[:120]
        _ds = f"{_p['name']}" + (f" 규격: {_sz}." if _sz else ".") + " 대전 유성 영진종합목재(월드건축자재) 매장에서 실물 확인, 원하는 사이즈 재단, 전국 용달 배송."
        _ri.append((_d, _p, _u, _ds))
    json.dump(_fs2, open(_fsf2, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    _ri.sort(key=lambda t: (t[0], int(t[1]["id"])), reverse=True)
    def _rfc2(d):
        try: return datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%a, %d %b %Y 09:00:00 +0900")
        except Exception: return ""
    open(f"{OUT}/wwoodkr-rss.xml", "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>영진종합목재(월드건축자재) 쇼핑몰 새 상품</title><link>https://wwood.kr/home/mall/</link><description>대전 유성 영진종합목재(월드건축자재) 목재·합판·건축자재 쇼핑몰 상품 소식</description><language>ko</language>\n'
        + "".join(f"<item><title>{html.escape(p_['name'])} 규격·주문</title><link>{html.escape(u_)}</link><guid>{html.escape(u_)}</guid><pubDate>{_rfc2(d_)}</pubDate><description>{html.escape(ds_)}</description>" + (f'<enclosure url="{html.escape(p_["img"])}" type="image/jpeg" length="0"/>' if p_.get("img", "").startswith("http") else "") + "</item>\n" for d_, p_, u_, ds_ in _ri)
        + "</channel></rss>\n")
    _CUR = {r["name"]: (r["cat"], int(float(r["price"]))) for r in csv.DictReader(open(f"{ROOT}/data/prices.csv", encoding="utf-8")) if r.get("price")}
    _chg = sorted([(c, n, PREV[n], p) for n, (c, p) in _CUR.items() if n in PREV and PREV[n] != p], key=lambda x: -abs(x[3] - x[2]) / max(x[2], 1))
    _up = [x for x in _chg if x[3] > x[2]]; _dn = [x for x in _chg if x[3] < x[2]]
    def _ctab(rows): return '<div class="tw"><table><tr><th>분류</th><th>자재</th><th class="r">이전</th><th class="r">지금</th><th class="r">변동</th></tr>' + "".join(f'<tr><td>{E(c)}</td><td>{E(clean_name(n))}</td><td class="r">{a:,}원</td><td class="r"><b>{b:,}원</b></td><td class="r">{"▲" if b > a else "▼"} {abs(b - a):,}원 ({(b - a) / a * 100:+.1f}%)</td></tr>' for c, n, a, b in rows) + '</table></div>'
    _pcb = (f'<section class="wrap sec"><h1>이번 기준가 변동 — 오른 자재·내린 자재</h1><p class="lead">매장 소매 기준가(부가세 별도)를 지난 갱신({E(PMETA.get("prev", ""))})과 비교해 실제로 바뀐 품목만 모았습니다. 기준일 {E(PMETA.get("updated", ""))}.</p>'
            + (f'<h2>내린 자재 {len(_dn)}개</h2>' + _ctab(_dn) if _dn else "") + (f'<h2>오른 자재 {len(_up)}개</h2>' + _ctab(_up) if _up else "")
            + ("" if _chg else '<p>이번 갱신에서는 기준가가 바뀐 품목이 없습니다. 전체 기준가는 <a href="/price.html">기준가</a>에서 보세요.</p>')
            + '<p class="small muted">규격·수량·재고에 따라 다를 수 있습니다. 정확한 금액은 매장(042-545-2900)에 확인해 주세요.</p><p><a class="b r" href="/price.html">전체 기준가 보기 ›</a></p></section>')
    page("price-change.html", "목재·건축자재 기준가 변동 — 이번 주 오른·내린 자재 | 영진목재", f"대전 영진목재 매장 기준가 변동: 내린 자재 {len(_dn)}개, 오른 자재 {len(_up)}개. 합판·구조재·방부목·석고보드 등 실제로 바뀐 품목만 정리.", _pcb, "/price.html")
    import aiinfo as _AI
    _FQ = _AI.facts(BASE, TEL, ADDR, HOURS, YT); _PR = _AI.prices(ROOT)
    _ab = ('<section class="wrap sec"><h1>영진종합목재 한눈에 — 자주 묻는 사실 정리</h1><p class="lead">대전 유성 영진종합목재(영진목재·월드건축자재)에 대해 손님이 가장 많이 묻는 것을 짧게 정리했습니다. 내용은 매장 안내·재단비·기준가 페이지와 같습니다.</p>'
           + '<dl class="abf">' + "".join(f'<dt>{E(q)}</dt><dd>{E(a)} <a href="{u[len(BASE):]}">자세히 ›</a></dd>' for q, a, u in _FQ) + '</dl>'
           + '<h2>대표 자재 기준가 (부가세 별도)</h2><div class="tw"><table><tr><th>자재</th><th class="r">기준가</th></tr>' + "".join(f'<tr><td>{E(n)}</td><td class="r">{p:,}원</td></tr>' for n, p in _PR) + '</table></div><p class="small muted">매장 소매 기준가이며 규격·수량에 따라 다를 수 있습니다. 전체 목록은 <a href="/price.html">기준가</a>.</p>'
           + f'<h2>기본 정보</h2><ul><li>상호: 영진종합목재(영진목재 · 월드건축자재), 사업자 상호 영진우드</li><li>주소: 대전광역시 유성구 유성대로 44, 1층</li><li>전화: {TEL}</li><li>영업시간: {HOURS}</li><li>규모: 3000평 목재·건축자재 매장, 원하는 크기 즉석 재단</li><li>쇼핑몰(도매회원 주문): <a href="https://www.wwood.kr/">www.wwood.kr</a></li><li>유튜브: <a href="{YT}" rel="noopener">월드건축자재DIY</a></li></ul></section>')
    page("about.html", "영진종합목재 한눈에 — 대전 목재 재단·기준가·배송 자주 묻는 사실 | 영진목재", "대전 유성 영진종합목재(월드건축자재) 위치·영업시간·재단비·기준가·전국 배송·도매·시공을 짧은 질문과 답으로 정리했습니다.", _ab, "/about.html",
         [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a, u in _FQ]}])
    _llmf = "\n".join(f"### {q}\n{a}\n출처: {u}\n" for q, a, u in _FQ) + "\n## 대표 자재 기준가(부가세 별도)\n" + "\n".join(f"- {n}: {p:,}원" for n, p in _PR)
    open(f"{OUT}/llms-full.txt", "w", encoding="utf-8").write(f"# 영진종합목재 (영진목재 · 월드건축자재) — 사실 정리\n\n> 대전 유성구 유성대로 44, 1층 · {TEL} · {HOURS}\n> 3000평 목재·건축자재 매장, 원하는 크기 즉석 재단, 전국 배송. 정보 페이지 {BASE} · 쇼핑몰 https://www.wwood.kr/\n\n## 자주 묻는 질문\n" + _llmf + "\n")
    open(f"{OUT}/llms.txt", "w", encoding="utf-8").write(f"""# 영진종합목재 (영진목재 · 월드건축자재 · 월드아키텍쳐)

> 대전에 있는 3000평 규모 목재·건축자재 매장입니다. 합판·각재·방부목·데크·집성판·도어·중문·사이딩·단열재를 원하는 크기로 재단해 전국으로 보냅니다. 이 사이트(www.wwood.co.kr)는 자재 정보·시공법·계산기 사이트이고, 상품 주문은 매장 쇼핑몰 https://www.wwood.kr/ 에서 합니다.

- 매장: 대전광역시 유성구 유성대로 44, 1층 · 전화 {TEL} · {HOURS} · 길찾기 {BASE}/visit.html\n- 재단비: 1컷 12T 이하 1,000원 · 15·18T 1,500원 · 30T 이하 3,000원(부가세 별도) {BASE}/jaedan-bi.html\n- 사실 정리(질문·답): {BASE}/about.html · 전체판: {BASE}/llms-full.txt
- 쇼핑몰(주문): https://www.wwood.kr/
- 유튜브: {YT} , {YT2}

## 자주 찾는 정보
- [하는 법 Q&A]({BASE}/qna/): 자재 시공·보수 질문 답변
- [자재 비교]({BASE}/bigyo/): 합판 vs OSB vs MDF, 강마루 vs 강화마루 등
- [자재 가격 가이드]({BASE}/gagyeok/): 품목별 기준가와 1평 계산
- [자재 시공법]({BASE}/sigongbeop/) · [DIY 만들기]({BASE}/mandeul/)
- [자재비 계산기]({BASE}/calc.html) · [목재 재단 그림]({BASE}/cut.html) · [규격표]({BASE}/gyugyeok.html)
- [공간 사진 둘러보기]({BASE}/gonggan/) · [인테리어 트렌드]({BASE}/trend/)
- [전국 배송 지역]({BASE}/jeonguk/) · [시공팀 연결]({BASE}/yeongyeol/)
""")
    open(f"{OUT}/robots.txt", "w").write(f"User-agent: *\nAllow: /\n\nUser-agent: Googlebot\nAllow: /\n\nUser-agent: Bingbot\nAllow: /\n\nUser-agent: Yeti\nAllow: /\n\nUser-agent: Daumoa\nAllow: /\n\nUser-agent: OAI-SearchBot\nAllow: /\n\nUser-agent: ChatGPT-User\nAllow: /\n\nUser-agent: GPTBot\nAllow: /\n\nUser-agent: ClaudeBot\nAllow: /\n\nUser-agent: Claude-SearchBot\nAllow: /\n\nUser-agent: Claude-User\nAllow: /\n\nUser-agent: PerplexityBot\nAllow: /\n\nUser-agent: Perplexity-User\nAllow: /\n\nUser-agent: Google-Extended\nAllow: /\n\nUser-agent: Applebot\nAllow: /\n\nUser-agent: Applebot-Extended\nAllow: /\n\nUser-agent: Bravebot\nAllow: /\n\nUser-agent: DuckAssistBot\nAllow: /\n\nUser-agent: Amazonbot\nAllow: /\n\nUser-agent: meta-externalagent\nAllow: /\n\nUser-agent: CCBot\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\nSitemap: {BASE}/sitemap-video.xml\nSitemap: {BASE}/sitemap-products.xml\nSitemap: {BASE}/sitemap-apt.xml\nSitemap: {BASE}/rss.xml\n\n#DaumWebMasterTool:99e0908a419948d27287fb3d562fb5c6a299e4c3c385ed57b261247546dd22cc:VC4npJliHmrJLtJDnWYFDA==\n")
    today = datetime.date.today().isoformat()
    # lastmod: 내용이 실제로 바뀐 날만 갱신(매일 오늘 날짜면 구글이 lastmod를 무시함)
    _lmf = f"{ROOT}/data/lastmod.json"
    _lm = json.load(open(_lmf, encoding="utf-8")) if os.path.exists(_lmf) else {}
    def _lmod(u):
        rel = u[len(BASE):].lstrip("/") or "index.html"
        if rel.endswith("/"): rel += "index.html"
        try: b = open(f"{OUT}/{rel}", "rb").read()
        except OSError: return today
        b = re.sub(rb"\?v=[0-9a-f]{8}", b"", b)
        i0, i1 = b.find(b"<main"), b.rfind(b"</main>")
        if i0 >= 0 and i1 > i0: b = b[i0:i1]  # 메뉴·바닥글 변경은 빼고 본문만 비교
        b = re.sub(rb"<head>.*?</head>", b"", b, flags=re.S)
        h = "m1" + hashlib.md5(b).hexdigest()[:12]
        if _lm.get(u, [None])[0] != h: _lm[u] = [h, today]
        return _lm[u][1]
    LMD = {u: _lmod(u) for u in SITEMAP}
    json.dump(_lm, open(_lmf, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    X = lambda t: html.escape(t, quote=True)
    open(f"{OUT}/sitemap-video.xml", "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">\n' +
        "".join(f"<url><loc>{u}</loc><video:video><video:thumbnail_loc>https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg</video:thumbnail_loc><video:title>{X(v['title'][:100])}</video:title><video:description>{X(dd[:2000])}</video:description><video:player_loc>https://www.youtube.com/embed/{v['id']}</video:player_loc>"
                + (f"<video:duration>{ln}</video:duration>" if ln else "")
                + (f"<video:publication_date>{_dt.datetime.fromtimestamp(ts, _dt.timezone(_dt.timedelta(hours=9))).isoformat()}</video:publication_date>" if ts else "")
                + "<video:family_friendly>yes</video:family_friendly></video:video></url>\n" for u, v, dd, ts, ln in VSM if v["id"] not in VTHIN) + "</urlset>\n")
    _isp = lambda u: re.search(r"/[a-z]+/p/[^/]+\.html$", u) is not None
    _isapt = lambda u: bool(re.search(r"/apt/[a-z]+/[^/]+\.html$", u))
    for _fn, _us in (("sitemap.xml", [u for u in SITEMAP if not _isp(u) and not _isapt(u)]), ("sitemap-products.xml", [u for u in SITEMAP if _isp(u) and "/bupum/p/" not in u]), ("sitemap-apt.xml", [u for u in SITEMAP if _isapt(u)])):
      open(f"{OUT}/{_fn}", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' +
        "".join(f"<url><loc>{quote(u, safe=':/?=&%#')}</loc><lastmod>{LMD[u]}</lastmod>" + (f"<image:image><image:loc>{html.escape((BASE + SIMG[u]) if SIMG[u].startswith('/') else SIMG[u])}</image:loc></image:image>" if SIMG.get(u) else "") + "".join(f"<image:image><image:loc>{BASE}/assets/{d_}/{u.rsplit('/', 1)[1][:-5]}-steps.jpg</image:loc></image:image>" for d_ in ("mandeul", "sigongbeop") if f"/{d_}/" in u and not u.endswith("/") and os.path.exists(f"{ROOT}/assets/{d_}/{u.rsplit('/', 1)[1][:-5]}-steps.jpg")) + "</url>\n" for u in _us) + "</urlset>\n")
    # 전체 자재 검색: 쇼핑몰 자재 + 제조사·철물·본덱스 사진 카드(.yri) 전부 → /assets/search.json
    _sx, _seen = list(idx), set()
    for d_ in ("bondex", "bupum", "yerim", "younglim", "shenu", "nichiha", "geonjae", "knauf", "suip"):
        for fn in sorted(os.listdir(f"{OUT}/{d_}")) if os.path.isdir(f"{OUT}/{d_}") else []:
            if not fn.endswith(".html"): continue
            tx = open(f"{OUT}/{d_}/{fn}", encoding="utf-8").read()
            sec = re.search(r"<title>([^<|—]*)", tx); sec = (sec.group(1).strip() if sec else "")
            for m in re.finditer(r'<a class="yri" href="#" data-big="([^"]*)" data-n="([^"]*)"[^>]*>.*?</a>', tx, re.S):
                im_ = re.search(r'<img[^>]*src="([^"]+)"', m.group(0))
                k_ = (m.group(2), m.group(1))
                if k_ in _seen: continue
                _seen.add(k_)
                pz = re.search(r'class="cbp">([\d,]+원~)', m.group(0))
                _sx.append({"n": html.unescape(m.group(2)), "i": im_.group(1) if im_ else m.group(1), "c": sec, "s": (pz.group(1) + " · " if pz else "") + sec, "l": f"/{d_}/{fn}".replace("/index.html", "/")})
    # 가구 만들기·자재 시공법 대표 사진도 넣기 → 사진찾기에서 "이렇게 만들어요/시공해요" 페이지를 찾아 줌(t: m=만들기, g=시공법)
    for d_, t_ in (("mandeul", "m"), ("sigongbeop", "g")):
        for fn in sorted(os.listdir(f"{OUT}/{d_}")) if os.path.isdir(f"{OUT}/{d_}") else []:
            if not fn.endswith(".html") or fn == "index.html": continue
            sl = fn[:-5]
            if not os.path.exists(f"{ROOT}/assets/{d_}/{sl}.jpg"): continue
            tx = open(f"{OUT}/{d_}/{fn}", encoding="utf-8").read()
            ti = re.search(r"<title>([^<|]*)", tx); ti = html.unescape(ti.group(1).strip()) if ti else sl
            for im_ in (f"/assets/{d_}/{sl}.jpg", f"/assets/{d_}/{sl}-steps.jpg"):
                if os.path.exists(f"{ROOT}{im_}"):
                    _sx.append({"n": ti, "i": im_, "s": "가구 만들기" if t_ == "m" else "자재 시공법", "l": f"/{d_}/{fn}", "t": t_})
    _PF = ["https://m.xn--392bopf4iwtp.com/web/product/medium/", "https://www.emalling.co.kr/web/product/medium/", "https://s3.ap-northeast-2.amazonaws.com/younglim-bucket/", "https://www.yerim.net/upload/product/", "https://namuip.com/cnd_home/assets/img/", "https://www.wwood.kr/", "https://media.knauf.com/a/"]
    for x in _sx:
        for k_, pf in enumerate(_PF):
            if x["i"].startswith(pf): x["i"] = f"~{k_}" + x["i"][len(pf):]; break
        if x.get("l"): x.pop("c", None)
    json.dump({"p": _PF, "d": _sx}, open(f"{OUT}/assets/search.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    # 제목·설명 중복 정리: 같은 제목이 여러 페이지면 두 번째부터 품번/주소로 구분
    _TT = {}
    for _f in sorted(glob.glob(f"{OUT}/**/*.html", recursive=True)):
        _t = open(_f, encoding="utf-8").read()
        if 'http-equiv="refresh"' in _t: continue
        _m = re.search(r"<title>(.*?)</title>", _t)
        if not _m: continue
        _k = _m.group(1)
        if _k not in _TT: _TT[_k] = _f; continue
        _id = os.path.basename(_f)[:-5] if "/p/" in _f else os.path.relpath(_f, OUT)[:-5].replace("/index", "")
        if "/p/" in _f and len(_id) > 15: _id = "-".join(_id.split("-")[-2:]).upper()
        _tag = f" (품번 {_id})" if "/p/" in _f else f" ({_id})"
        _new = re.sub(r"( [|—] )", _tag + r"\1", _k, count=1) if re.search(r" [|—] ", _k) else _k + _tag
        if len(_new) > 62 and " | " in _new:  # 품번을 붙여 길어지면 앞 이름을 줄임(업체명·품번은 유지)
            _hd, _tl = _new.split(_tag, 1); _new = _hd[:max(10, 62 - len(_tag) - len(_tl)) - 1].rstrip() + "…" + _tag + _tl
        _t = _t.replace(f"<title>{_k}</title>", f"<title>{_new}</title>", 1).replace(f'content="{_k}"', f'content="{_new}"')
        _t = re.sub(r'(<meta name="description" content=")([^"]*)"', lambda m: m.group(1) + m.group(2).rstrip(". ") + f". 품번 {_id}." + '"', _t, count=1) if "/p/" in _f else _t
        open(_f, "w", encoding="utf-8").write(_t)
    # 첫 화면 속도: 홈은 style.css를 문서 안에 넣어 렌더링 차단 요청 1개를 없앰
    _ix = f"{OUT}/index.html"; _ih = open(_ix, encoding="utf-8").read()
    _ih = re.sub(r'<link rel="stylesheet" href="/assets/style\.css\?v=[^"]*">', lambda m: "<style>" + open(f"{OUT}/assets/style.css", encoding="utf-8").read() + "</style>", _ih, count=1)
    open(_ix, "w", encoding="utf-8").write(_ih)
    print(len(SITEMAP), "pages →", OUT)

import hashlib
ASSET_V = hashlib.md5((open(f"{ROOT}/assets/style.css","rb").read()+open(f"{ROOT}/assets/site.js","rb").read())).hexdigest()[:8]
SITEMAP = []
VSM = []
ALLFAQ = []
SIMG = {}
build()
