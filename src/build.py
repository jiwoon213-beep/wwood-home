from urllib.parse import quote
import glob
import collections, re
#!/usr/bin/env python3
"""월드건축자재 홍보 사이트 생성기. python3 build.py [BASE_URL]"""
import csv, html, json, os, re, shutil, sys, datetime
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
    PROD.append(dict(id=r[0], name=r[1].strip(), img="https://www.wwood.kr" + img, cats=[c for c in r[3].split(",") if c]))
# 홈페이지 전체 자재 분류 (쇼핑몰 대분류 코드 → 주소)
JCAT = [("23", "gakjae", "각재·구조재", "다루끼·구조재·방부목·히노끼·탄화목·침목"), ("24", "panjae", "판재·합판", "합판·MDF·OSB·집성판·고재판재·임가공판재"),
        ("53", "jipseong", "우드슬랩·집성판", "고무나무·아카시아·멀바우·히노끼 집성판"), ("25", "deck", "데크재", "방부데크·천연데크·합성데크·탄화데크·데크철물"),
        ("26", "maru", "마루·후로링", "원목후로링·강마루·강화마루·바닥도료"), ("27", "naejang", "내장재", "루바·고재·월판넬·아트월·천정재·몰딩·타공판"),
        ("28", "stone", "스톤·타일", "스톤·북유럽타일·파벽돌·조약돌"), ("31", "siding", "외장재·사이딩", "사이딩·지붕재·기와·타이벡"),
        ("29", "door", "실내 도어·문틀", "ABS도어·유리도어·문틀·합판문"), ("29w", "window", "주택 창호", "수입 주택창호·파티오도어·고정창"), ("30", "insul", "방음·단열·방수", "방음·흡음·단열·보온·방수·환기"),
        ("32", "hardware", "철물", "건축철물·타카·인테리어철물·공학목재철물"), ("35", "paint", "페인트·스테인", "오일스테인·페인트·작업도구"),
        ("37", "sopum", "소품·부자재", "정원가구·목재소품·철제가구·공구·접착제")]
JTOP = {c for c, *_ in JCAT}
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
# 페인트·스테인(35): 본덱스(이몰링)에 없는 제품은 홈페이지에서 뺌(사장님 지시 2026-11-14). 본덱스에 같은 제품이 있는 것만 남김.
if os.path.exists(f"{ROOT}/data/emall.tsv"):
    _EMN = [l.split("|")[2] for l in open(f"{ROOT}/data/emall.tsv", encoding="utf-8") if l.count("|") >= 3]
    def _inbd(n):
        toks = [w for w in re.split(r"[\s\-\(\)\[\]/,]+", re.sub(r"천연|내추럴|식물성|목재보수제", " ", n)) if len(w) >= 2]
        return bool(toks) and any(sum(w.replace(" ", "") in e.replace(" ", "") for w in toks) >= (len(toks) if len(toks) <= 3 else len(toks) - 1) for e in _EMN)
    PROD = [p for p in PROD if "35" not in p["tops"]]  # 본덱스로 합침(사장님 지시 2026-11-14)
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
def pcard(p):
    sub = MCAT.get(p["sub"] or "", "")
    _own = p.get("tops") and p.get("top") in {c for c, *_ in JCAT}  # 새 홈페이지에 상품 페이지(/p/)가 있으면 그쪽으로 연결(내부 링크 → 색인에 도움)
    return ((f'<a class="pd" href="/p/{p["id"]}.html">' if _own else f'<a class="pd" href="https://wwood.kr/home/mall/shoplist.php?idx={p["id"]}&amp;pmode=view" target="_blank" rel="noopener">')
            + f'<span class="pi"><img loading="lazy" src="{E(p["img"])}" alt="{E(p["name"])}"></span><b>{E(p["name"])}</b>{f"<small>{E(sub)}</small>" if sub else ""}</a>')
# 유튜브 채널 숫자: data/stats.json {"subs": "1.36만", "videos": 940, "date": "YYYY-MM-DD"} (하루 1번 자동 갱신)
ST = json.load(open(f"{ROOT}/data/stats.json", encoding="utf-8")) if os.path.exists(f"{ROOT}/data/stats.json") else {"subs": "1.3만", "videos": 900}
# 최신 영상: data/latest.txt (영상 ID, 최신이 위)
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
    return [{"@context": "https://schema.org", "@type": "Product", "name": clean_name(r["name"]), "category": r["cat"],
             **({"image": img} if img else {}),
             "offers": {"@type": "Offer", "price": int(r["price"]), "priceCurrency": "KRW", "url": url,
                        "priceSpecification": {"@type": "UnitPriceSpecification", "price": int(r["price"]), "priceCurrency": "KRW", "valueAddedTaxIncluded": False},
                        "seller": {"@type": "Organization", "name": "영진종합목재"}}} for r in rows]

def mat_prices(m, k=10):
    cats, inc, exc = m["price"]
    if not cats: return []
    rows = [p for p in P if p["cat"] in cats and re.search(inc, p["name"]) and not (exc and re.search(exc, p["name"]))]
    return sorted(rows, key=lambda p: -p["qty"])[:k]

# ---------- layout ----------
NAV = [("/visit.html", "매장 안내"), ("/jaryo/", "전체 자재"), ("/news/", "소식·정보"), ("/price.html", "기준가"), ("/mandeul/", "DIY 만들기"), ("/sigongbeop/", "자재 시공법"), ("/trend/", "인테리어 트렌드"), ("/cut.html", "목재 재단"), ("/video/", "영상"), ("/dome.html", "도매·납품"), ("/sigong.html", "시공")]

def page(path, title, desc, body, active="", jsonld=None, img=None):
    if len(desc) < 45:  # 너무 짧은 설명은 매장 정보로 보강(80자 이내)
        for add in (" 대전 유성 3000평 매장, 즉석 재단·전국 용달 배송.", " 대전 유성 매장·전국 배송."):
            if len(desc) + len(add) <= 80: desc = desc.rstrip() + add; break
    if len(desc) > 80:  # 네이버 권장: 설명 80자 이내 — 문장·쉼표 경계에서 자름
        cut = desc[:80]; k = cut.rfind(".")
        if k < 40: k = cut.rfind(", ")
        desc = (cut[:k + 1] if k >= 40 else cut[:79] + "…").rstrip(" ,")
    canon = BASE + ("/" + path if path != "index.html" else "/").replace("index.html", "")
    nav = "".join(f'<a href="{h}"{" class=on" if active==h else ""}>{t}</a>' for h, t in NAV)
    lds = jsonld if isinstance(jsonld, list) else ([jsonld] if jsonld else [])
    lds = lds + [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "홈", "item": BASE + "/"}] +
                 ([{"@type": "ListItem", "position": 2, "name": dict(NAV)[active], "item": BASE + active}] if active in dict(NAV) and active != "/" else []) +
                 ([{"@type": "ListItem", "position": 3 if (active in dict(NAV) and active != "/") else 2, "name": title.split(" — ")[0].split(" | ")[0], "item": canon}] if (canon.rstrip("/") != (BASE + active).rstrip("/") or active not in dict(NAV)) and path != "index.html" else [])}]
    ld = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    doc = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="alternate" type="application/rss+xml" title="영진종합목재 소식" href="/rss.xml">
<link rel="canonical" href="{canon}">{'<meta name="robots" content="noindex,follow">' if path.startswith("p/") else ('' if PREVIEW else '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">')}<meta name="naver-site-verification" content="a59ff6921fc90666c920da00bf9a23ecb0ba3514"><meta property="og:type" content="website"><meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canon}"><meta property="og:image" content="{E(img or (BASE + "/assets/store/storefront.jpg"))}">{"" if img else '<meta property="og:image:width" content="1280"><meta property="og:image:height" content="853">'}<meta property="og:image:alt" content="{E(title.split(" | ")[0]) if img else "영진종합목재(월드건축자재) 매장"}"><meta name="twitter:title" content="{E(title)}"><meta name="twitter:description" content="{E(desc)}"><meta name="twitter:image" content="{E(img or (BASE + "/assets/store/storefront.jpg"))}"><meta property="og:site_name" content="영진종합목재 (월드건축자재)"><meta property="og:locale" content="ko_KR"><meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&amp;display=swap"><link rel="preconnect" href="https://i.ytimg.com"><link rel="preconnect" href="https://www.wwood.kr"><link rel="icon" href="/assets/logo-mark.svg" type="image/svg+xml"><link rel="icon" href="/assets/favicon-48.png" sizes="48x48"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><link rel="stylesheet" href="/assets/style.css?v={ASSET_V}">{'<meta name="robots" content="noindex,nofollow">' if PREVIEW else ''}{ld}</head><body>
<div class="top"><div class="wrap row sb"><span>{HOURS} · {ADDR}</span><span><span id="vcnt" class="vcnt"></span> <a href="/dome.html">업체·도매회원</a> <a href="/visit.html">매장 길찾기</a></span></div></div>
<header><div class="wrap row sb hd"><a class="logo" href="/"><img class="lm" src="/assets/logo-mark.svg" width="46" height="46" alt=""><span class="lt"><b>영진종합목재</b><small><em>월드건축자재</em> · 충청권 최대규모 목재상</small></span></a>
<button class="mnb" type="button" aria-expanded="false" aria-controls="gnav" onclick="var h=this.closest('header'),o=h.classList.toggle('open');this.setAttribute('aria-expanded',o);this.innerHTML=o?'✕ 닫기':'☰ 메뉴'">☰ 메뉴</button><nav id="gnav">{nav}</nav></div></header>
<main>{body}</main>
<footer><div class="wrap">월드건축자재 · 영진종합목재(영진목재) · 상호 영진우드 · <a href="/daejeon.html">대전 목재</a> · <a href="/sejong.html">세종 목재</a> · <a href="/calc.html">자재 계산기</a> · <a href="/cut.html">합판 재단 미리보기</a> · <a href="/mandeul/">DIY 만들기</a> · <a href="/sigongbeop/">인테리어 자재 시공법</a> · <a href="/baesong.html">전국 배송</a> · <a href="/jeonguk/">배송 지역</a> · <a href="/jajae/">자재 백과</a> · <a href="/calc.html">자재 계산기</a> · <a href="/gyugyeok.html">규격표</a> · <a href="/gagyeok/">자재 가격 가이드</a> · <a href="/cheolmul/">목재 철물</a> · <a href="/taka/">타카·타카핀</a> · <a href="/yerim/">예림 중문·도어</a> · <a href="/younglim/">영림 도어·중문·필름</a> · <a href="/shenu/">쉐누 도어·몰딩</a> · <a href="/bupum/">철물·공구·부속</a> · <a href="/bondex/">본덱스 스테인·페인트</a> · <a href="/local/">지역별 시공</a> · <a href="/faq.html">자주 묻는 질문</a> · <a href="/yongeo.html">현장 용어</a> | {ADDR} | {TEL} | <a href="mailto:{EMAIL}">{EMAIL}</a> | {HOURS}<br>
시공: 월드아키텍쳐 | 대표 김지운 | 사업자등록번호 281-05-03197 | {LIC}<br>사이트의 매장·상품·시공 사진은 영진종합목재가 직접 촬영한 저작물로(제조사 제품 사진 제외) 무단 복제·사용을 금합니다.<br>
유튜브 <a href="{YT}">@월드건축자재DIY</a> · <a href="{YT2}">@월드도어</a> · 도매회원 쇼핑몰 <a href="{DOME}">wwood.kr</a> · 표시 가격은 부가세 별도 소매 기준가이며 결제·재단은 매장에서 합니다.</div></footer><script>(function(){{try{{var k=new Date(Date.now()+9*3600e3).toISOString().slice(0,10).replace(/-/g,""),b="https://abacus.jasoncameron.dev/",n="wwood-co-kr";
function rd(x){{var v=null;try{{v=localStorage.getItem(x)}}catch(e){{}}if(v===null){{var m=document.cookie.match(new RegExp("(?:^|; )"+x+"=([^;]*)"));v=m?m[1]:null}}return v}}
function wr(x,v){{try{{localStorage.setItem(x,v)}}catch(e){{}}try{{document.cookie=x+"="+v+"; max-age=34560000; path=/; SameSite=Lax"}}catch(e){{}}}}
var bot=navigator.webdriver||/bot|crawl|spider|slurp|lighthouse|headless|preview/i.test(navigator.userAgent),nd=!bot&&rd("vcd")!==k,ne=nd;
if(nd){{wr("vcd",k);try{{var rf=document.referrer||"",src=/youtube|youtu\\.be/.test(rf)?"yt":/naver/.test(rf)?"naver":/google/.test(rf)?"google":/daum|kakao/.test(rf)?"daum":/bing/.test(rf)?"bing":/daangn|karrot/.test(rf)?"daangn":/wwood\\.kr/.test(rf)?"wwoodkr":rf&&rf.indexOf(location.host)<0?"etc":"direct";fetch(b+"hit/"+n+"/src-"+src).catch(function(){{}});fetch(b+"hit/"+n+"/src-"+src+"-d"+k).catch(function(){{}});}}catch(e){{}}}}
Promise.all([fetch(b+(nd?"hit":"get")+"/"+n+"/d"+k).then(function(r){{return r.json()}}),fetch(b+(ne?"hit":"get")+"/"+n+"/total").then(function(r){{return r.json()}})]).then(function(v){{var t=v[0].value||0,a=v[1].value||0;var el=document.getElementById("vcnt");if(el)el.textContent="오늘 "+t.toLocaleString()+" · 전체 "+a.toLocaleString();}}).catch(function(){{}});}}catch(e){{}}}})();</script>
<div class="mbar"><a class="b g" href="/visit.html">매장 길찾기</a><a class="b d" href="tel:{TEL.replace('-','')}">전화</a></div>
<script src="/assets/site.js?v={ASSET_V}" defer></script></body></html>"""
    if PREFIX: doc = doc.replace('href="/', f'href="{PREFIX}/').replace('src="/', f'src="{PREFIX}/')
    fp = os.path.join(OUT, path); os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(doc)
    if not path.startswith("p/"): SITEMAP.append(canon); SIMG[canon] = img  # 상품 상세(/p/)는 얇은 페이지라 색인 제외(구글: 크롤링됨-색인 안 됨 734건)

def vcard(v, big=False):
    return f"""<a class="vc{' big' if big else ''}{' sh' if v['type']=='S' else ''}" href="{vpage(v)}"{'' if v['id'] in VD else ' target="_blank" rel="noopener"'} data-yt="{v['id']}">
<span class="th"><img loading="lazy" decoding="async" width="480" height="360" src="https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg" alt="{E(vshort(v['title']))}"><i class="play"></i>{'<em>쇼츠</em>' if v['type']=='S' else '<em>라이브</em>' if v['type']=='V' else ''}</span>
<b>{E(v['title'])}</b><small>조회 {views(v['n'])}</small></a>"""

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
    return f'<div class="tw"><table><thead><tr><th>품목·규격</th><th class=r>소매 기준가</th></tr></thead><tbody>{tr}</tbody></table></div><p class="muted small">부가세 별도 · 규격·수량에 따라 달라집니다 · 재단비·운임은 매장에서 계산 · 도매가는 회원 로그인 후</p>'

CTA = f"""<section class="cta"><div class="wrap g2"><div><h2>실물 보고, 원하는 사이즈로 잘라 가세요</h2>
<p>{ADDR} · {HOURS}. 3000평 매장에서 바로 고르고 즉석 재단해 드립니다.</p></div>
<div class="row"><a class="b g" href="/visit.html">매장 길찾기</a><a class="b r" href="/sigong.html">시공 맡기기</a></div></div></section>"""

BIZ = {"@context": "https://schema.org", "@type": "HardwareStore", "name": "영진종합목재",
       "telephone": "+82-42-545-2900", "address": {"@type": "PostalAddress", "streetAddress": "유성대로 44, 1층", "addressLocality": "대전", "addressCountry": "KR"},
       "openingHours": ["Mo-Fr 07:00-18:00", "Sa-Su 07:00-15:00"], "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "07:00", "closes": "18:00"}, {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Saturday", "Sunday"], "opens": "07:00", "closes": "15:00"}, {"@type": "OpeningHoursSpecification", "dayOfWeek": "PublicHolidays", "opens": "07:00", "closes": "16:00"}], "url": BASE + "/", "sameAs": [YT, YT2, MALL, KAKAO, NPLACE, "https://g.page/r/CZcZc9J-M0L0EAE"], "alternateName": ["영진목재", "월드건축자재", "영진우드"], "legalName": "영진우드",
       "image": [BASE + "/assets/store/storefront.jpg", BASE + "/assets/store/yard-aisle2.jpg", BASE + "/assets/store/showroom.jpg"], "priceRange": "₩", "areaServed": ["대전", "세종", "공주", "계룡", "논산", "금산", "옥천"]}

# ---------- pages ----------
def build():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT); shutil.copytree(f"{ROOT}/assets", f"{OUT}/assets")
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
        if vs: return f'<img loading="lazy" decoding="async" width="480" height="270" src="https://i.ytimg.com/vi/{vs[0]}/hqdefault.jpg" alt="">'
        t = re.sub(r"\s*[—|].*$", "", p["title"])[:18]
        return f'<i class="pci"><em>{"자재·인테리어 소식" if "-news-" in p.get("slug", "") else "자재 정보"}</em>{E(t)}</i>'
    plist = lambda ps: "".join(f'<a class="pc" href="/news/{p["slug"]}.html">{_pth(p)}<small>{E(p.get("date",""))}</small><b>{E(p["title"])}</b><span>{E(p.get("desc",""))}</span></a>' for p in ps)
    _isv = lambda p: p["title"].startswith("[영상]")
    def nrow(h, ps): return (f'<h2 class="gt">{h} <small>옆으로 넘겨 보세요 ›</small></h2><div class="pl hs nw">{plist(ps)}</div>') if ps else ""
    postsec = (f'<section class="wrap sec"><h2>소식·자재 정보</h2><div class="pl hs nw">{plist(POSTS[:10])}</div><p class="hsh">옆으로 밀어서 더 보기 ›</p><p><a href="/news/">전체 글 보기 →</a></p></section>' if POSTS else "")
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
<section class="wrap sec"><div class="tl4"><a href="/cut.html"><b>✂ 재단 미리보기</b><span>치수만 넣으면 원판에서 어떻게 잘리는지 그림으로</span></a><a href="/mandeul/"><b>🪚 DIY 만들기</b><span>평상·책장·데크·울타리 재단 목록</span></a><a href="/gyugyeok.html"><b>📏 규격표</b><span>합판 두께·2×4 실제 치수 한눈에</span></a><a href="/baesong.html"><b>🚚 전국 배송</b><span>재단해서 용달로 전국 현장까지</span></a></div></section><!--MKHOME-->
<style>.tl4{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}.tl4 a{{display:block;background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px;color:inherit;text-decoration:none}}.tl4 a:hover{{border-color:var(--red)}}.tl4 b{{display:block;font-size:17px;margin-bottom:4px}}.tl4 span{{font-size:13px;color:var(--mut)}}@media(max-width:760px){{.tl4{{grid-template-columns:1fr 1fr}}}}</style>
<div class="hx"><section class="wrap sec"><h2>무엇을 만들고 싶으세요?</h2><p class="muted">고르면 그 용도의 자재와 시공 영상이 한 번에 나옵니다.</p><div class="ug">{use}</div></section>
<section class="wrap sec"><h2>자재 백과 — 이 나무, 어디에 쓰나요?</h2><p class="muted">용도·인테리어 효과·기준가·관련 영상을 자재별로 정리했습니다.</p><div class="mg">{mats}</div></section>
{postsec}{newsec}
<section class="wrap sec"><h2>🏆 많이 본 영상 TOP</h2><p class="small muted">조회수가 많은 순서입니다.</p>{hot}<p><a class="b o" href="/video/top.html">많이 본 영상 TOP 50 전체 보기 ›</a> <a href="{YT}" target="_blank" rel="noopener">유튜브 채널 →</a></p></section></div>
<section class="wrap sec g2"><div class="card"><h2>기본 자재 기준가</h2><p class="muted small">부가세 별도 · 규격·수량에 따라 달라집니다</p>
<div class="tw"><table><thead><tr><th>자재</th><th>규격</th><th class=r>기준가</th></tr></thead><tbody>{bt}</tbody></table></div>
<p class="small">재단비·운임·수량 할인은 매장에서 계산 · 고재·수입목·특수목은 매장 문의 · 도매가는 회원 로그인 후</p><a href="/price.html">기준가 전체 보기 →</a><div class="qk"><b>💰 1평에 얼마?</b><a href="/gagyeok/hapan-gagyeok.html">합판</a><a href="/gagyeok/seokgo-gagyeok.html">석고보드</a><a href="/gagyeok/deck-gagyeok.html">데크</a><a href="/gagyeok/danyeol-gagyeok.html">아이소핑크</a><a href="/gagyeok/hinoki-ruba.html">루바</a><a href="/gagyeok/tempa-board.html">템바보드</a><a href="/gagyeok/">전체 가격 가이드</a></div></div>
<div class="card dark"><h2>직접 하기 어렵다면, 시공까지</h2><p>자재를 가장 잘 아는 목재상이 직접 시공합니다. 월드아키텍쳐({LIC})가 대전·세종 전 공정을 시공하고, 모든 현장은 유튜브에 공개합니다.</p>
<a class="b r" href="/sigong.html">시공 사례 보기</a></div></section>{CTA}"""
    page("index.html", "대전 목재·세종 목재 영진목재 | 3000평 목재소, 원하는 사이즈 즉석 재단", "대전 목재·세종 목재 영진목재(월드건축자재). 3000평 목재소, 합판·방부목·데크 즉석 재단, 기준가·시공 영상.", body, "", BIZ)

    # 소식·정보
    page("news/index.html", "소식·자재 정보 — 목재·건축자재 가격, 시공 팁 | 대전 월드건축자재", "대전 월드건축자재(영진목재)의 자재 정보, 기준가, 시공 사례, 새 영상 소식.",
         f'<section class="wrap sec"><h1>소식·자재 정보</h1><p class="lead">자재 고르는 법, 기준가, 시공 사례와 새 영상 소식을 매일 올립니다.</p>{nrow("📘 자재 정보·가격", [p for p in POSTS if not _isv(p) and "-news-" not in p.get("slug", "")])}{nrow("▶ 새 영상 소식", [p for p in POSTS if _isv(p)])}{nrow("📰 자재·인테리어 소식", [p for p in POSTS if "-news-" in p.get("slug", "")])}</section>{CTA}', "/news/")
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
    SEARCH = ('<div class="srch"><span class="si">🔍</span><input id="jq" type="search" placeholder="자재 이름으로 찾기 (예: 히노끼, OSB, 경첩)" autocomplete="off" aria-label="자재 검색">'
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
    jrows = "".join(f'<section class="wrap sec jall" id="c{sl}"><h2>{n} <small class="muted">{cnt[c]}종</small> <a class="small" href="/jaryo/{sl}.html">전체 보기 ›</a></h2><p class="small muted">{d}</p>{_chrow if c == "32" else ""}{_yrrow if c == "29" else ""}{_bdrow if c == "35" else ""}<div class="pg hrow">' + "".join(pcard(p) for p in [p for p in PROD if c in p["tops"]][:16]) + f'<a class="pd more" href="/jaryo/{sl}.html"><span class="pi"><b>+{max(0,cnt[c]-16)}</b></span><b>{n} 전체 보기 ›</b><small>{cnt[c]}종</small></a></div><p class="hsh">옆으로 밀어서 더 보기 ›</p></section>' for c, sl, n, d in JCAT if cnt[c])
    page("jaryo/index.html", f"전체 자재 사진 {len([p for p in PROD if p['tops']])}종 — 각재·합판·데크·사이딩·철물 | 대전 영진목재", "대전 월드건축자재(영진목재) 매장 취급 자재를 사진으로 확인하세요. 각재, 합판, 집성판, 데크, 마루, 내장재, 타일, 사이딩, 철물, 스테인.",
         f'<section class="wrap sec"><h1>전체 자재</h1>{SEARCH}<p class="lead">매장에서 취급하는 자재를 사진으로 모았습니다. 실물은 대전 매장에서 보고, 원하는 사이즈로 재단해 가세요. 가격은 <a href="/price.html">기준가</a> 또는 매장에서 안내합니다.</p><div class="chips jall jchips">{jchips}</div></section>{jrows}{CTA}', "/jaryo/", None, thumb.get("24"))
    for c, sl, n, d in JCAT:
        ps = [p for p in PROD if c in p["tops"]]
        if not ps and not (c == "35" and _bdrow): continue
        subs = []
        for p in ps:
            if subof(p, c) not in subs: subs.append(subof(p, c))
        secs = _yrrow if c == "29" else (_bdrow if c == "35" else "")
        for sb in subs:
            g = [p for p in ps if subof(p, c) == sb]
            title = MCAT.get(sb or "", "") or "기타"
            secs += f'<h2 id="s{(sb or "x").split("/")[-1] or "x"}">{E(title)} <small class="muted">{len(g)}종</small></h2>{_chrow if "건축철물" in title else ""}<div class="pg hrow">{"".join(pcard(p) for p in g)}</div>' + ('<p class="hsh">옆으로 밀어서 더 보기 ›</p>' if len(g) > 2 else '')
        toc = " · ".join(f'<a href="#s{(sb or "x").split("/")[-1] or "x"}">{E(MCAT.get(sb or "", "") or "기타")}</a>' for sb in subs)
        if not ps: ps_n = cnt[c]
        page(f"jaryo/{sl}.html", f"{n} 종류 사진 {len(ps) or cnt[c]}종 — {d} | 대전 월드건축자재", f"{n} 종류를 사진으로 확인하세요: {d}. 대전 유성 월드건축자재(영진목재) 매장 취급, 즉석 재단.",
             f'<section class="wrap sec"><p class="crumb"><a href="/jaryo/">전체 자재</a> › {n}</p><h1>{n} <small class="muted">{len(ps)}종</small></h1><p class="lead">{d}. 사진을 누르면 상세 사진이 열립니다. 실물 확인·재단은 대전 매장에서 합니다.</p>{SEARCH}<div class="jall"><p class="small">{toc}</p>{secs}</div></section>{CTA}', "/jaryo/",
             {"@context": "https://schema.org", "@type": "ItemList", "name": f"{n} 종류", "numberOfItems": len(ps),
              "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": p["name"], "image": p["img"]} for i, p in enumerate(ps[:100])]}, ps[0]["img"] if ps else thumb.get(c))

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
         f'<section class="wrap sec ptsec"><h1>소매 기준가</h1>{psearch}<p class="lead">자주 찾는 자재의 소매 기준가입니다(부가세 별도). 규격·수량에 따라 달라지며 재단비·운임은 매장에서 계산합니다. 도매가는 <a href="/dome.html">도매회원</a> 로그인 후 확인하세요. 크기·두께는 <a href="/gyugyeok.html">규격표</a>, 어떻게 잘리는지는 <a href="/cut.html">재단 미리보기</a>에서 보세요.</p>{secs}<div class="qk"><b>💰 1평에 얼마?</b><a href="/gagyeok/hapan-gagyeok.html">합판</a><a href="/gagyeok/seokgo-gagyeok.html">석고보드</a><a href="/gagyeok/osb-gagyeok.html">OSB</a><a href="/gagyeok/mdf-gagyeok.html">MDF</a><a href="/gagyeok/danyeol-gagyeok.html">아이소핑크</a><a href="/gagyeok/jipseong-gagyeok.html">집성판</a><a href="/gagyeok/deck-gagyeok.html">데크재</a><a href="/gagyeok/gakjae-gagyeok.html">구조재·각재</a><a href="/gagyeok/siding-gagyeok.html">사이딩</a><a href="/gagyeok/molding-gagyeok.html">몰딩</a><a href="/gagyeok/door-gagyeok.html">방문·문틀</a><a href="/gagyeok/hinoki-ruba.html">히노끼 루바</a><a href="/gagyeok/spruce-ruba.html">스프러스 루바</a><a href="/gagyeok/tempa-board.html">템바보드</a><a href="/gagyeok/tempa-ruba.html">템바 루바</a><a href="/gagyeok/interior-film.html">인테리어 필름</a><a href="/gagyeok/oilstain.html">오일스테인</a><a href="/gagyeok/">자재 가격 가이드</a></div></section>{CTA}', "/price.html")

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
<div class="row"><a class="b r" href="tel:{TEL.replace('-','')}">시공 상담 전화 {TEL}</a></div><p class="small">시공 지역: 대전·세종 전 공정 · 관급·대기업·전국 공사는 전화 문의</p></div></section><section class="wrap sec gg"><h2 class="gt">우리 동네 시공 찾기</h2><div class="qk">{"".join(f'<a href="/local/{a}-{b}.html">{c} {d}</a>' for a, d in (("jungmun", "중문"), ("door", "방문 교체"), ("film", "필름"), ("molding", "몰딩"), ("wall", "템바보드 벽")) for b, c in (("yuseong", "유성구"), ("seogu", "서구"), ("sejong", "세종")))}<a href="/local/">전체 지역 보기 ›</a></div></section>
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
          "sejong": ("세종", {"sejong-sinsi", "sejong-eupmyeon"}, "세종시 신도심·조치원·읍면 현장까지 배송·납품합니다(수량·위치에 따라 전화 상담). 대전 유성 매장에서 고르고 재단해 바로 가져가셔도 됩니다.")}
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
    slides = "".join(f'<div class="cslide" id="{k}"><div class="card"><h2>{h}</h2><div class="cg">{inner}</div>' + ('' if k == "py" else f'<div class="cr" id="{k}r"></div>') + (f'<p class="small muted">{note}</p>' if note else "") + (f'<p class="small">{links}</p>' if links else "") + '</div></div>' for k, t, h, inner, links, note in CALCS)
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
    _CF = [("합판·MDF 원하는 사이즈로 잘라 주나요?", "네. 대전 유성대로 44 매장에서 합판, MDF, 집성판, OSB, 석고보드, 단열재와 구조재·각재·방부목을 원하는 크기로 즉석 재단해 드립니다. 한 장, 한 개 소량도 됩니다."),
           ("4×8 합판 한 장에서 몇 조각 나오나요?", "4×8 합판 원판은 1220×2440mm입니다. 이 페이지에 자를 크기와 개수를 넣으면 톱날 두께 3mm를 빼고 몇 장이 필요한지, 어떻게 잘리는지 그림으로 바로 보여드립니다."),
           ("재단할 때 톱날 두께는 얼마나 빠지나요?", "한 번 자를 때마다 약 3mm가 빠집니다. 이 계산기는 3mm를 빼고 배치하므로 실제 재단과 거의 같게 나옵니다."),
           ("나뭇결 방향을 맞춰서 자를 수 있나요?", "네. 집성판이나 무늬목처럼 결이 중요한 자재는 '나뭇결 방향 유지'를 체크하면 조각을 돌리지 않고 배치합니다."),
           ("재단 그림을 매장에 어떻게 보내나요?", "'링크 복사'를 눌러 카톡이나 문자로 보내시거나, 화면을 매장에 보여주시면 그대로 잘라 드립니다. 인쇄도 됩니다.")]
    _sz = "".join(f"<li><b>{E(c['n'])}</b> — " + ", ".join(sorted({(f"{i[1]}×{i[2]}mm" if not c['lin'] else f"길이 {i[1]}mm") for i in c['items']})) + "</li>" for c in _cd["cats"] if c.get("items"))
    _seo = (f'<section class="wrap sec"><h2>매장 원판·각재 규격 (재단 기준)</h2><ul>{_sz}</ul>'
            '<h2>재단 미리보기 사용법</h2><ol><li>자재(합판·MDF·집성판·석고보드·단열재·구조재·방부목·각재·데크)를 고릅니다.</li><li>자를 크기(가로×세로×개수, 각재는 길이×개수)를 넣습니다.</li><li>필요한 원판 장수와 재단 그림을 확인하고, 링크를 매장에 보내거나 화면을 보여주세요.</li></ol>'
            '<h2>자주 묻는 질문</h2>' + "".join(f"<h3>{E(q)}</h3><p>{E(a)}</p>" for q, a in _CF) +
            '<p>👉 <a href="/gyugyeok.html">합판·목재 규격표</a> · <a href="/mandeul/">만들기 자재 목록(평상·책장·데크·가벽)</a> · <a href="/calc.html">자재 계산기(몇 장 필요한지)</a> · <a href="/jajae/">자재 백과</a> · <a href="/visit.html">매장 안내·길찾기</a></p></section>')
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
           "sadariseonban": r"사다리 선반|사다리", "aillaendeu": r"아일랜드", "balpan": r"발판|스텝", "bunrisugeo": r"분리수거", "kaetower": r"캣타워|고양이", "jangnangam": r"장난감|수납함", "jwatak": r"좌탁|밥상", "renjidae": r"렌지대|전자레인지", "sunappyeongsang": r"평상(?!형)", "hwajangdae": r"화장대", "sangbujang": r"상부장", "silwoegi": r"실외기 ?(커버|가림)", "deckgyedan": r"DIY 계단|계단 만들", "kaempingbox": r"나무박스|캠핑 ?박스"}
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
        _tot = 0; _grp = {}; _seen = set(); _ml = []
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
            btns += f'<a class="b o" href="{cutlink(cat, rx, parts)}">{E(part)} 재단 그림</a> '
        body = f"""<section class="wrap sec"><p class="crumb"><a href="/mandeul/">DIY 만들기</a> › {E(nm)}</p><h1>{E(title.split(" — ")[0])}</h1><p class="lead">{E(lead)}</p>
{_hero}<div class="tw"><table class="rt"><thead><tr><th>부분</th><th>자재·재단 크기</th><th>필요 수량</th><th>기준가 예상 금액</th></tr></thead><tbody>{trs}</tbody></table></div>
{f'<div class="est"><b>예상 자재비 약 {_tot:,}원</b><span>소매 기준가 기준 · 부가세 별도 · 피스·철물·마감재 제외 · 재단비·운임은 매장에서 계산 · 가격은 바뀔 수 있어요</span></div>' if _tot else ''}
<p class="small muted">톱날 3mm를 빼고 계산했습니다. 크기를 바꾸고 싶으면 아래 재단 그림에서 숫자만 고치세요.</p><p>{btns}</p><p><a class="b r" href="mailto:{EMAIL}?subject={quote(nm + ' 재단·견적 요청')}&amp;body={quote('안녕하세요. 아래 목록대로 재단·견적 부탁드립니다.' + chr(10) + chr(10) + nm + ' (' + BASE + '/mandeul/' + slug + '.html)' + chr(10) + chr(10).join(_ml) + chr(10) + (f'예상 자재비(기준가): 약 {_tot:,}원' if _tot else '') + chr(10) + chr(10) + '수량·크기 변경:' + chr(10) + '이름:' + chr(10) + '연락처:' + chr(10) + '방문(또는 배송) 희망일:' + chr(10))}">✉ 이 목록으로 재단·견적 요청</a> <a class="b d" href="tel:{TEL.replace('-', '')}">전화 문의</a></p></section>
{_gal}{_stp}<section class="wrap sec g2"><div class="card"><h2>만드는 순서</h2><ol>{"".join(f"<li>{E(x)}</li>" for x in steps)}</ol></div>
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
    import emall as _em
    EMLIST = _em.gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT)
    import cmbs as _cmb
    CBLIST = _cmb.gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT)
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
<section class="wrap sec g2"><div class="card"><h2>시공 순서</h2><ol>{"".join(f"<li>{E(x)}</li>" for x in steps)}</ol><h3>필요한 공구</h3><ul class="mli">{MI.sg_tools(tools)}</ul><p class="hsh">옆으로 넘겨 보세요 ›</p></div>
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
    page("sigongbeop/index.html", "자재 시공법 — 석고보드·루바·사이딩·몰딩·강마루·필름·문 교체 셀프 시공 | 영진목재", "석고보드 벽, 루바 천장, 외벽 사이딩, 몰딩·걸레받이, 강마루, 템바보드, 흡음판, 합성데크, 방문 교체, 필름, 오일스테인, OSB 벽 시공 방법을 자재 수량·그림 설명서·영상으로 정리했습니다.",
         f'<section class="wrap sec"><h1>자재 시공법</h1><p class="lead">내장재·외장재·바닥재·도어를 직접 시공하는 순서를 자재 수량, 그림 설명서, 영상으로 정리했습니다. 자재는 매장에서 원하는 크기로 잘라 드리고, 어려운 공사는 직접 시공도 합니다.</p><div class="gsrch"><span>🔍</span><input id="sgq" type="search" placeholder="시공법 검색 (예: 석고보드, 사이딩, 마루, 문)" autocomplete="off" aria-label="검색"></div><p id="sgqn" class="small muted" style="margin:-4px 0 8px"></p><div class="mg m2" id="sgqg">{sg_cards}</div><script>(function(){{var q=document.getElementById("sgq"),n=document.getElementById("sgqn"),C=[].slice.call(document.querySelectorAll("#sgqg .mc"));function f(){{var v=q.value.replace(/\\s/g,"").toLowerCase(),k=0;C.forEach(function(c){{var ok=!v||c.textContent.replace(/\\s/g,"").toLowerCase().indexOf(v)>=0;c.style.display=ok?"":"none";if(ok)k++}});n.textContent=v?(k?k+"개 찾음":"찾는 게 없어요. 매장에 물어보세요."):""}}q.addEventListener("input",f)}})();</script><p><a class="b o" href="/mandeul/">가구·소품 만들기 자재 보기 ›</a></p></section>{CTA}', "/sigongbeop/")
    SGMAT_HTML = {}
    for x in SG:
        SGMAT_HTML.setdefault(x[9], []).append(x)
    SGMAT_HTML = {k: '<section class="wrap sec"><h2>시공법</h2><div class="mg m2">' + "".join(f'<a class="mc" href="/sigongbeop/{x[0]}.html">' + (f'<img loading="lazy" src="/assets/sigongbeop/{x[0]}.jpg" alt="{E(x[1])}" style="width:100%;height:auto;border-radius:8px;margin-bottom:6px">' if os.path.exists(f"{ROOT}/assets/sigongbeop/{x[0]}.jpg") else "") + f'<b>{E(x[1])}</b><small>자재 수량·그림 설명서·영상</small></a>' for x in v) + '</div></section>' for k, v in SGMAT_HTML.items()}
    page("mandeul/index.html", "만들기 자재 목록 — 평상·책장·침대·신발장·작업대·데크·개집 재단 크기 | 영진목재", "평상, 책장, 신발장, 침대 프레임, 작업대, 벤치, 베란다 선반, 벽 단열, 데크, 가벽, 울타리, 테이블, 강아지집을 만들 때 필요한 자재와 재단 크기를 정리했습니다. 재단 그림까지 바로 확인하세요.",
         f'<section class="wrap sec"><h1>DIY 만들기</h1><p class="lead">자주 만드는 것들의 자재와 재단 크기를 정리했습니다. 크기만 바꿔서 재단 그림으로 확인하고, 매장에 보여주시면 그대로 잘라 드려요.</p><div class="gsrch"><span>🔍</span><input id="mkq" type="search" placeholder="만들 것 검색 (예: 책장, 데크, 방부목, 집성판)" autocomplete="off" aria-label="검색"></div><p id="mkqn" class="small muted" style="margin:-4px 0 8px"></p><div class="mg m2" id="mkqg">{mk_cards}</div><script>(function(){{var q=document.getElementById("mkq"),n=document.getElementById("mkqn"),C=[].slice.call(document.querySelectorAll("#mkqg .mc"));function f(){{var v=q.value.replace(/\\s/g,"").toLowerCase(),k=0;C.forEach(function(c){{var ok=!v||c.textContent.replace(/\\s/g,"").toLowerCase().indexOf(v)>=0;c.style.display=ok?"":"none";if(ok)k++}});n.textContent=v?(k?k+"개 찾음":"찾는 게 없어요. 매장에 물어보세요."):""}}q.addEventListener("input",f)}})();</script></section><section class="wrap sec"><div class="card"><h2>직접 만드신 작품을 보내 주세요</h2><p>영진종합목재 자재로 만든 평상·선반·데크·가구 사진을 메일로 보내 주시면 이 페이지 「손님이 만든 작품」에 소개해 드립니다(이름은 원하시는 대로, 얼굴·주소가 나온 사진은 빼고 올립니다).</p><p><a class="b r" href="mailto:{EMAIL}?subject=%EC%9E%91%ED%92%88%20%EC%82%AC%EC%A7%84%20%EB%B3%B4%EB%83%85%EB%8B%88%EB%8B%A4&body=%EB%A7%8C%EB%93%A0%20%EA%B2%83%3A%0A%EC%93%B4%20%EC%9E%90%EC%9E%AC%3A%0A%EC%86%8C%EA%B0%9C%ED%95%A0%20%EC%9D%B4%EB%A6%84(%EB%8B%89%EB%84%A4%EC%9E%84)%3A%0A">작품 사진 메일로 보내기</a></p></div></section>{CTA}', "/mandeul/")
    page("cut.html", "합판·MDF 재단 미리보기 — 원하는 사이즈 재단 그림 | 대전 영진목재", "합판·MDF·집성판·석고보드·구조재를 원하는 사이즈로 넣으면 원판에서 어떻게 잘리는지, 몇 장 필요한지 그림으로 보여드립니다. 대전 영진목재 즉석 재단.",
         open(ROOT + "/cut_tpl.html", encoding="utf-8").read().replace("__DATA__", json.dumps(_cd, ensure_ascii=False, separators=(",", ":"))).replace("__TEL__", TEL.replace("-", "")).replace("__EMAIL__", EMAIL) + _seo + CTA, "/cut.html", _ld, BASE + "/assets/store/plywood-rack.jpg")
    page("calc.html", "자재 계산기 — 데크·석고보드·합판 몇 장? 문짝·중문 크기까지 | 영진목재", "데크 방부목·합성데크 장수, 석고보드·합판·단열재 장수, 몰딩·걸레받이 길이, 데코타일·강마루 박스 수, 페인트 양, 평↔㎡를 바로 계산하세요. 대전 영진목재(월드건축자재) 재단·배송.",
f"""<section class="wrap sec"><h1>자재 계산기</h1><p class="lead">필요한 양을 미리 계산해 오시면 매장에서 바로 재단해 드립니다. 결과는 참고용입니다(로스 포함). 어떻게 잘리는지는 <a href="/cut.html">재단 미리보기</a>에서 그림으로 확인하세요.</p>
<div class="chips" id="cchips">{chips}</div>
<div class="cnav"><button class="cb" data-d="-1">◀ 이전</button><span id="cpos" class="small muted"></span><button class="cb" data-d="1">다음 ▶</button></div>
<div class="cslider" id="cslider">{slides}</div>
<h2 class="cfaq">자주 묻는 질문</h2>{faqslide(CALC_FAQ)}</section>
<style>.cslider{{display:flex;align-items:flex-start;transition:height .2s;overflow-x:auto;overflow-y:hidden;scroll-snap-type:x mandatory;gap:12px;scrollbar-width:none;-webkit-overflow-scrolling:touch}}.cslider::-webkit-scrollbar{{display:none}}.cslide{{flex:0 0 100%;scroll-snap-align:start}}.cslide .card{{margin:0}}.cfaq{{margin:22px 0 10px;font-size:22px}}
.cnav{{display:flex;justify-content:space-between;align-items:center;margin:6px 0 10px}}.cb{{padding:12px 18px;border:1px solid var(--line);border-radius:12px;background:#fff;font-weight:800;font-size:16px;cursor:pointer}}
#cchips{{display:flex;gap:6px;overflow-x:auto;flex-wrap:nowrap;padding-bottom:4px}}#cchips .chip{{flex:0 0 auto;border:1px solid var(--line);background:#fff;cursor:pointer;font-size:17px;padding:11px 18px}}#cchips .chip.on{{background:var(--red);color:#fff;border-color:var(--red)}}
.cg{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 10px;margin:10px 0}}@media(min-width:760px){{.cg{{grid-template-columns:repeat(4,minmax(0,1fr))}}}}.cg label{{display:flex;flex-direction:column;font-size:16px;font-weight:800;gap:6px}}.cg input,.cg select{{font-size:21px;font-weight:700;height:56px;padding:0 12px;border:2px solid #cfc7ba;border-radius:12px;width:100%;box-sizing:border-box;background:#fff;color:var(--ink)}}.cg select{{font-size:17px}}@media(max-width:759px){{.cg label:has(select){{grid-column:1/-1}}}}.cg input:focus,.cg select:focus{{border-color:var(--red);outline:none}}
.cr{{background:#fff7ed;border:1px solid #f5d9b8;border-radius:14px;padding:16px;font-size:18px;line-height:1.8}}.cr b{{font-size:28px;color:#c2410c}}.ql{{color:#1d4ed8;font-weight:700;text-decoration:underline}}.qb{{margin-top:10px;font-size:16px;line-height:2.2}}.qb .ql{{display:inline-block;margin-right:8px;padding:2px 8px;border:1px solid #c7d2fe;border-radius:14px;background:#fff;text-decoration:none}}</style>
<script>
(function(){{var $=function(i){{return document.getElementById(i)}},v=function(i){{return parseFloat($(i).value)||0}},n=function(x){{return Math.ceil(x).toLocaleString()}};
var Q=function(t,k){{return '<a class="ql" href="/jaryo/?q='+encodeURIComponent(k||t)+'">'+t+' ›</a>'}};
var B=function(a){{return '<div class="qb">함께 필요한 부자재: '+a.map(function(x){{return Q(x[0],x[1])}}).join(' ')+'</div>'}};
var C={{
deck:function(){{var W=v('dw'),L=v('dl'),t=$('dt').value.split(','),bw=+t[0],bl=+t[1]/1000,J=+$('dj').value/1000,rows=Math.ceil(W/((bw+5)/1000)),per=Math.ceil(L/bl),boards=rows*per*1.1,joists=Math.floor(W/J)+1,jp=joists*L/3.6*1.1,sc=rows*per*joists/per*2*1.1;
 var dk=bw==140?'합성데크':'방부데크';return '데크 면적 '+(W*L).toFixed(1)+'㎡ ('+(W*L/3.3058).toFixed(1)+'평)<br>'+Q('데크재',dk)+' <b>'+n(boards)+'장</b> · '+Q('장선 각재(3.6m)','방부각재')+' <b>'+n(jp)+'개</b> · '+Q('피스','피스')+' 약 <b>'+n(sc)+'개</b>'+B([['오일스테인','스테인'],['방부원주목(기둥)','방부원주목'],['난간재','난간']])}},
gyp:function(){{var A=Math.max(0,v('gw')*v('gh')-v('go'));return '시공 면적 '+A.toFixed(1)+'㎡<br>'+Q('석고보드')+' <b>'+n(A/parseFloat($('gs').value)*(+$('gp').value)*1.1)+'장</b>'+B([['석고본드'],['피스'],['타카핀'],['목상 각재','각재']])}},
ply:function(){{return Q('합판·OSB·MDF','합판')+' <b>'+n(v('pa')/parseFloat($('ps').value)*1.1)+'장</b>'+B([['피스'],['타카핀'],['목공본드','본드']])}},
mol:function(){{var per=2*(v('mw')+v('ml'))*Math.max(1,v('mr')),k=$('mk').value,p=parseFloat($('mp').value),ce=per,ba=Math.max(0,per-0.9*v('md')),out='방 둘레 '+per.toFixed(1)+'m<br>';
 if(k!='base')out+=Q('천장몰딩','몰딩')+' <b>'+n(ce*1.1/p)+'개</b> ';if(k!='ceil')out+=Q('걸레받이','몰딩')+' <b>'+n(ba*1.1/p)+'개</b>';return out+' <span class="small">('+p+'m 기준, 로스 10%)</span>'+B([['실타카핀','타카핀'],['실리콘'],['본드']])}},
flo:function(){{var b=v('fb')||1;return '필요 면적 '+(v('fa')*parseFloat($('fl').value)).toFixed(1)+'㎡<br>'+Q('바닥재','마루')+' <b>'+n(v('fa')*parseFloat($('fl').value)/b)+'박스</b>'+B([['걸레받이·몰딩','몰딩'],['본드']])}},
ins:function(){{return Q('단열재(아이소핑크)','아이소핑크')+' <b>'+n(v('ia')/parseFloat($('is').value)*Math.max(1,v('il'))*1.1)+'장</b>'+B([['우레탄폼','우레탄'],['아이소핑크본드','아이소핑크본드']])}},
door:function(){{var m=$('om').value,W=v('ow'),H=v('oh'),F=v('of'),N=Math.max(1,v('on')),out='';
 if(m=='frame'){{var fw=W-10,fh=H-5;out+='문틀 바깥 크기 약 <b>'+Math.round(fw)+' × '+Math.round(fh)+'mm</b> · 문틀 폭 <b>'+Math.round(v('od'))+'mm</b>(벽 두께)<br>';W=fw-2*F;H=fh-F;out+='문틀 안쪽 약 '+Math.round(W)+' × '+Math.round(H)+'mm<br>'}}
 var dw=W-v('os'),dh=H-3-(+$('ot').value),hg=dh>2100?4:3;
 return out+Q('문짝','도어')+' 크기 약 <b>'+Math.round(dw)+' × '+Math.round(dh)+'mm</b><br>'+Q('경첩')+' '+(hg*N)+'개 · '+Q('손잡이')+' '+N+'개'+(m=='frame'?' · 문틀 '+N+'세트':'')+' <span class="small">('+N+'짝 기준)</span>'+B([['도어스토퍼'],['우레탄폼','우레탄'],['실리콘'],['피스']])}},
jungmun:function(){{var n=+$('jt').value,W=v('jw'),H=v('jh'),F=v('jf'),O=v('jo'),fw=W-10,fh=H-5,iw=fw-2*F,ih=fh-F,pw=n==1?(iw+O):(iw+(n-1)*O)/n;
 return '중문 프레임 바깥 약 <b>'+Math.round(fw)+' × '+Math.round(fh)+'mm</b><br>프레임 안쪽 약 '+Math.round(iw)+' × '+Math.round(ih)+'mm<br>문짝 '+n+'장 · 1장 폭 약 <b>'+Math.round(pw)+'mm</b>'+(n==1?' <span class="small">(원슬라이딩은 벽 쪽 여유 공간 필요)</span>':'')+B([['실리콘'],['우레탄폼','우레탄'],['피스']])}},
pnt:function(){{var L=v('ta')*Math.max(1,v('tc'))/(v('tr')||1);return Q('페인트·스테인','스테인')+' 약 <b>'+L.toFixed(1)+'L</b><br>18L 기준 '+n(L/18)+'통 또는 4L 기준 '+n(L/4)+'통'+B([['붓·롤러','롤러'],['마스킹테이프','테이프']])}}
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

    # 자재 비교 (data/compare.json)
    CMP = json.load(open(f"{ROOT}/data/compare.json", encoding="utf-8"))
    matname2 = {m["slug"]: m["name"] for m in MATS}
    cmpnav = lambda cur: '<div class="pl hs">' + "".join(f'<a class="pc" href="/bigyo/{c["slug"]}.html"><small>자재 비교</small><b>{E(c["short"])}</b><span>{E(c["desc"][:60])}…</span></a>' for c in CMP if c["slug"] != cur) + '</div><p class="hsh">옆으로 밀어서 더 보기 ›</p>'
    for c in CMP:
        th = "<tr><th></th>" + "".join(f"<th>{E(x)}</th>" for x in c["cols"]) + "</tr>"
        tb = "".join("<tr><th>" + E(r[0]) + "</th>" + "".join(f"<td>{E(x)}</td>" for x in r[1:]) + "</tr>" for r in c["rows"])
        vs = top(lambda v, kw=c["kw"]: re.search(kw, v["title"]) is not None, 8)
        ml = " · ".join(f'<a href="/jajae/{m}.html">{matname2[m]} 용도·기준가</a>' for m in c["mats"] if m in matname2)
        page(f"bigyo/{c['slug']}.html", c["title"] + " | 영진목재", c["desc"],
             f"""<section class="wrap sec"><p class="crumb"><a href="/bigyo/">자재 비교</a> › {E(c["short"])}</p><h1>{E(c["title"])}</h1><p class="lead">{E(c["desc"])}</p>
<div class="tw"><table class="cmp"><thead>{th}</thead><tbody>{tb}</tbody></table></div>
<h2>정리하면</h2><p>{E(c["concl"])}</p><p><a class="b o" href="/jaryo/?q={c['q']}">매장 취급 제품 사진 보기</a> <a class="b o" href="/calc.html">자재 계산기</a></p><p>{ml}</p>
<p class="small muted">일반적인 특징을 정리한 것으로 제품·등급에 따라 다를 수 있습니다. 매장에서 실물을 비교해 보세요.</p></section>
<section class="wrap sec"><h2>관련 영상</h2>{vsplit(vs, "h3")}</section>
<section class="wrap sec"><h2>다른 자재 비교</h2>{cmpnav(c["slug"])}</section>{CTA}""", "/jajae/")
    page("bigyo/index.html", "자재 비교 — 합판·사이딩·단열재·바닥재·도어·루바 종류별 차이 | 영진목재", "헷갈리는 건축 자재를 종류별로 비교했습니다. 합판 vs OSB vs MDF, 세라믹·메탈·비닐 사이딩, 단열재, 바닥재, 실내 도어, 루바, 집성판, 각재, 방음·흡음재.",
         '<section class="wrap sec"><p class="crumb"><a href="/jajae/">자재 백과</a> › 자재 비교</p><h1>자재 비교</h1><p class="lead">비슷해 보여도 쓰는 곳이 다른 자재들을 한눈에 비교했습니다.</p><div class="pl">' + "".join(f'<a class="pc" href="/bigyo/{c["slug"]}.html"><small>자재 비교</small><b>{E(c["short"])}</b><span>{E(c["desc"][:70])}…</span></a>' for c in CMP) + f'</div></section>{CTA}', "/jajae/")

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
        b = vshort(v["title"])[:40]
        for c in (b, v["title"][:44].strip(), b + (" (쇼츠)" if v["type"] == "S" else " (영상)"), v["title"][:44].strip() + (" 쇼츠" if v["type"] == "S" else " 풀영상")):
            if c not in _vt_used: _vt_used.add(c); return c
        k = 2
        while f"{b} {k}" in _vt_used: k += 1
        _vt_used.add(f"{b} {k}"); return f"{b} {k}"
    for v in sorted(V, key=lambda x: -x["n"]):
        if v["id"] not in VD: continue
        d, ln, ts = VD[v["id"]]
        st = _vtitle(v)
        first = re.split(r"(?<=[.!?다요])\s", d.replace("\n", " "), maxsplit=1)[0] if d else v["title"]
        rel = [x for x in V if x["cat"] == v["cat"] and x["id"] != v["id"]]
        rel = sorted(rel, key=lambda x: -x["n"])[:8]
        ml = " · ".join(f'<a href="/jajae/{m}.html">{matname3[m]} 용도·기준가</a>' for m in v["mats"] if m in matname3)
        ld = {"@context": "https://schema.org", "@type": "VideoObject", "name": v["title"][:100], "description": (d or v["title"])[:300],
              "thumbnailUrl": f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg", "embedUrl": f"https://www.youtube.com/embed/{v['id']}",
              "contentUrl": vurl(v)}
        if ts: ld["uploadDate"] = _dt.datetime.fromtimestamp(ts, _dt.timezone(_dt.timedelta(hours=9))).isoformat()
        if ln: ld["duration"] = f"PT{ln // 60}M{ln % 60}S"
        cn = CATN.get(v["cat"], "영상")
        vds = (first or st)[:110]
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
        page(f"v/{v['id']}.html", f"{st} — {'쇼츠' if v['type'] == 'S' else '영상'}" + (f" 조회 {views(v['n'])}" if v['n'] >= 1000 else "") + " | 영진목재", vds,
             f"""<section class="wrap sec"><p class="crumb"><a href="/video/">영상</a> › <a href="/video/{v['cat']}.html">{E(cn)}</a></p><h1 class="vt1">{E(v['title'])}</h1>
<div class="{'emb sh1' if v['type']=='S' else 'emb'}"><iframe loading="lazy" src="https://www.youtube.com/embed/{v['id']}" title="{E(st)}" allowfullscreen></iframe></div>
<p class="small muted">조회 {views(v['n'])}{' · 쇼츠' if v['type']=='S' else ''} · <a href="{vurl(v)}" target="_blank" rel="noopener">유튜브에서 보기</a></p>
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
                body += f'<dt id="t{i}">{E(t[0])} <span class="muted">= {E(t[1])}</span></dt><dd>{E(t[2])}{ln}</dd>'; i += 1
            body += "</dl>"
        byid = {v["id"]: v for v in V}
        yv = [byid[x] for x in ["GGm4laQFUMg", "FNylPstDD4I", "jcqTf-1G5mA"] if x in byid]
        page("yongeo.html", "건축 현장 용어 사전 — 다루끼·덴조·가베·오사마리·하바끼 뜻 | 영진목재", "목수·인테리어 현장에서 쓰는 일본어 잔재 용어와 자재 용어의 뜻을 정리했습니다. 다루끼, 덴조, 가베, 오사마리, 하바끼, 나라시, 메지 등.",
             f"""<section class="wrap sec"><h1>건축 현장 용어 사전</h1><p class="lead">현장에서 오가는 말을 알아야 자재 주문과 업체 상담이 쉬워집니다. 목수·인테리어 현장에서 자주 쓰는 용어 {len(terms)}개를 쉬운 말로 풀었습니다. 표준어로 바꿔 쓰는 것이 좋지만, 현장 소통을 위해 뜻은 알아 두세요.</p>
<p class="small">바로가기: {toc}</p>{body}<p class="small muted">현장·지역마다 쓰는 뜻이 조금씩 다를 수 있습니다. 헷갈리는 자재는 매장(042-545-2900)에 물어보세요.</p></section>
{f'<section class="wrap sec"><h2>관련 영상</h2>{vsplit(yv, "h3")}</section>' if yv else ''}{CTA}""", "/jajae/", ygld)

    # 제품 개별 페이지 (/p/<id>.html)
    jn = {c: (sl, n, d) for c, sl, n, d in JCAT}
    mname = {m["slug"]: m for m in MATS}
    def pcard2(p):
        sub = MCAT.get(subof(p, p["top"]) or "", "")
        return (f'<a class="pd" href="/p/{p["id"]}.html"><span class="pi"><img loading="lazy" src="{E(p["img"])}" alt="{E(p["name"])}"></span><b>{E(p["name"])}</b>{f"<small>{E(sub)}</small>" if sub else ""}</a>')
    PSPEC = json.load(open(f"{ROOT}/data/pspec.json", encoding="utf-8")) if os.path.exists(f"{ROOT}/data/pspec.json") else {}
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
<p class="small"><a href="/calc.html">필요한 양 계산하기</a> · <a href="/visit.html">매장 위치</a> · <a href="/jaryo/{sl}.html">{E(cn)} 전체 보기</a></p></div></div>{spec}{use}</section>
<section class="wrap sec"><h2>같은 분류 제품</h2><div class="pg hrow">{"".join(pcard2(q) for q in sim)}</div></section>{CTA}""", "/jaryo/", None, p["img"])

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
    MKHOME = ('<section class="wrap sec"><h2>DIY 만들기 — 자재와 재단 크기</h2><p class="small muted">만들 것을 고르면 필요한 자재, 몇 mm로 몇 개 자를지, 만드는 순서와 영상까지 나옵니다. 매장에서 그 크기대로 잘라 드려요.</p><div class="mg m2">'
              + "".join(f'<a class="mc" href="/mandeul/{x[0]}.html">' + (f'<img loading="lazy" src="/assets/mandeul/{x[0]}.jpg" alt="{E(x[1])}" style="width:100%;height:auto;border-radius:8px;margin-bottom:6px">' if os.path.exists(f"{ROOT}/assets/mandeul/{x[0]}.jpg") else "") + f'<b>{E(x[1])}</b><small>{E(x[3][:40])}…</small></a>' for x in _hm)
              + f'</div><p><a class="b o" href="/mandeul/">DIY 만들기 {len(MK)}가지 전체 보기 ›</a></p></section>'
              + '<section class="wrap sec"><h2>인테리어 자재 시공법</h2><p class="small muted">석고보드·루바·사이딩·몰딩·마루·필름·문 교체까지 — 필요한 자재 수량, 그림 설명서, 시공 영상을 정리했습니다. 어려운 공사는 직접 시공도 합니다.</p><div class="mg m2">'
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
    for _f in glob.glob(f"{OUT}/news/*.html") + glob.glob(f"{OUT}/p/*.html") + glob.glob(f"{OUT}/jaryo/*.html") + glob.glob(f"{OUT}/daejeon/*.html") + glob.glob(f"{OUT}/sejong/*.html"):
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
        _fb += f'<h2 id="g{gi}">{E(gn)}</h2><div class="faqx">' + "".join(f'<details><summary>{E(q)}</summary><p>{E(a_)} <a href="{u_}">{E(n_)} 보기 ›</a></p></details>' for q, a_, u_, n_ in qs) + '</div>'
        _fld += [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a_}} for q, a_, u_, n_ in qs]
    page("faq.html", f"목재·합판 자주 묻는 질문 {len(_fld)}가지 — 재단·가격·만들기·시공 | 영진목재", "합판 재단, 자재 고르기, 필요한 양 계산, DIY 만들기 자재비, 석고보드·사이딩·마루 시공까지 손님들이 자주 묻는 질문과 답을 모았습니다. 대전 영진종합목재.",
         f'<section class="wrap sec"><h1>자주 묻는 질문</h1><p class="lead">매장과 전화로 가장 많이 받는 질문을 모았습니다. 찾는 답이 없으면 042-545-2900으로 물어보세요.</p><div class="gsrch"><span>🔍</span><input id="fq" type="search" placeholder="질문 검색 (예: 재단, 몇 장, 평상, 석고보드)" autocomplete="off" aria-label="질문 검색"></div><p class="small">{" · ".join(_toc)}</p>{_fb}</section>'
         + '<style>.faqx details{background:#fff;border:1px solid var(--line);border-radius:12px;margin:0 0 8px;padding:0 14px}.faqx summary{cursor:pointer;font-weight:700;padding:12px 0;list-style:none}.faqx summary::-webkit-details-marker{display:none}.faqx summary:before{content:"Q. ";color:var(--red)}.faqx p{margin:0 0 12px;color:var(--mut)}</style>'
         + '<script>(function(){var q=document.getElementById("fq"),D=[].slice.call(document.querySelectorAll(".faqx details"));q.addEventListener("input",function(){var v=q.value.replace(/\\s/g,"");D.forEach(function(d){var ok=!v||d.textContent.replace(/\\s/g,"").indexOf(v)>=0;d.style.display=ok?"":"none";d.open=!!v&&ok});[].forEach.call(document.querySelectorAll(".faqx"),function(x){var h=x.previousElementSibling,n=[].some.call(x.querySelectorAll("details"),function(d){return d.style.display!="none"});x.style.display=n?"":"none";if(h)h.style.display=n?"":"none"})})})();</script>' + CTA, "",
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
    # robots, sitemap
    if PREVIEW: print(len(SITEMAP), "preview pages →", OUT); return
    json.dump({"cats": [[c, n, d] for c, n, d in CATS], "v": [[v["id"], v["type"], v["cat"], v["n"], v["title"]] for v in V]}, open(f"{OUT}/assets/videos.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))  # wwood.kr 시공영상 페이지용
    # 404 — 없는 주소로 들어온 손님을 주요 페이지로
    open(f"{OUT}/404.html", "w", encoding="utf-8").write(open(f"{OUT}/index.html", encoding="utf-8").read().split("<main>")[0].replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="x-canonical"') + '<main><section class="wrap sec"><h1>찾으시는 페이지가 없어요</h1><p class="lead">주소가 바뀌었거나 없어진 페이지입니다. 아래에서 찾아보세요.</p><div class="row"><a class="b r" href="/">처음으로</a><a class="b o" href="/jaryo/">전체 자재</a><a class="b o" href="/cut.html">재단 미리보기</a><a class="b o" href="/price.html">기준가</a><a class="b o" href="/mandeul/">DIY 만들기</a><a class="b o" href="/sigongbeop/">자재 시공법</a><a class="b o" href="/faq.html">자주 묻는 질문</a><a class="b d" href="/visit.html">매장 안내</a></div></section></main></body></html>')
    # 사장님용 방문 통계(검색 제외, 메뉴 링크 없음)
    os.makedirs(f"{OUT}/stats", exist_ok=True)
    open(f"{OUT}/stats/index.html", "w", encoding="utf-8").write("""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>방문 통계 · 영진종합목재</title>
<style>body{font-family:Pretendard,'Noto Sans KR',sans-serif;background:#f6f3ee;color:#1d1b18;margin:0;padding:18px;max-width:640px;margin:auto}h1{font-size:22px}.k{display:flex;gap:10px}.k div{flex:1;background:#fff;border:1px solid #e4ded4;border-radius:14px;padding:14px}.k b{display:block;font-size:30px}small{color:#5e574e}
table{width:100%;border-collapse:collapse;background:#fff;border-radius:14px;overflow:hidden;margin-top:14px;font-size:15px}th,td{padding:10px;border-bottom:1px solid #eee;text-align:right}th:first-child,td:first-child{text-align:left}th{background:#1d1b18;color:#fff;font-weight:700}.bar{height:8px;background:#c62a1f;border-radius:4px;display:inline-block;vertical-align:middle;margin-left:6px}</style></head><body>
<h1>www.wwood.co.kr 방문 통계</h1><div class="k"><div><small>오늘 방문</small><b id="td">…</b></div><div><small>전체 방문(누적)</small><b id="tt">…</b></div></div><p><small>같은 사람(같은 휴대폰·컴퓨터)이 하루에 여러 번 들어와도 그날은 1명으로 셉니다. 전체 방문은 날마다 방문자를 더한 누적입니다. 검색 로봇은 세지 않습니다.</small></p>
<table id="src"><tr><th>어디서 왔나</th><th>오늘</th><th>누적</th></tr></table>
<table id="days"><tr><th>날짜</th><th>방문</th></tr></table>
<p id="note" style="display:none;background:#fff3f2;border:1px solid #f3c2bd;color:#c62a1f;padding:12px;border-radius:12px">방문자 숫자를 세는 외부 카운터 서버가 지금 응답하지 않아요(일시 장애). 사이트는 정상이고, 서버가 돌아오면 다시 숫자가 나옵니다. 잠시 후 새로고침해 주세요.</p>
<p><small>같은 사람이 하루에 여러 번 들어와도 1번으로 셉니다. 경로 집계는 2026-11-11 오후부터 시작했어요.</small></p>
<script>
var b="https://abacus.jasoncameron.dev/get/wwood-co-kr/",S=[["yt","유튜브"],["naver","네이버"],["google","구글"],["daum","다음·카카오"],["bing","빙"],["daangn","당근"],["wwoodkr","쇼핑몰(wwood.kr)"],["etc","다른 사이트"],["direct","주소 입력·즐겨찾기"]];
var fail=0;function g(k){var c=window.AbortController?new AbortController():null;if(c)setTimeout(function(){c.abort()},9000);return fetch(b+k,c?{signal:c.signal}:{}).then(function(r){return r.ok?r.json():{value:0}}).then(function(j){return j.value||0}).catch(function(){fail++;return "-"})}
setTimeout(function(){if(fail){var p=document.getElementById("note");p.style.display="block"}},9500);
function day(i){return new Date(Date.now()+9*3600e3-i*864e5).toISOString().slice(0,10).replace(/-/g,"")}
var k=day(0);g("d"+k).then(function(v){td.textContent=v.toLocaleString()});g("total").then(function(v){tt.textContent=v.toLocaleString()});
Promise.all(S.map(function(s){return Promise.all([g("src-"+s[0]+"-d"+k),g("src-"+s[0])])})).then(function(R){var mx=Math.max.apply(null,R.map(function(r){return +r[1]||0}).concat([1]));
 S.forEach(function(s,i){var t=document.createElement("tr");t.innerHTML="<td>"+s[1]+"</td><td>"+R[i][0]+"</td><td>"+R[i][1]+"<span class=bar style='width:"+Math.round((+R[i][1]||0)/mx*60)+"px'></span></td>";document.getElementById("src").appendChild(t)})});
Promise.all([0,1,2,3,4,5,6,7,8,9,10,11,12,13].map(function(i){return g("d"+day(i))})).then(function(R){R.forEach(function(v,i){var d=day(i),t=document.createElement("tr");t.innerHTML="<td>"+d.slice(4,6)+"/"+d.slice(6)+(i?"":" (오늘)")+"</td><td>"+v+"</td>";document.getElementById("days").appendChild(t)})});
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
    json.dump(_fs, open(_fsf, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    _ex.sort(key=lambda t: t[0], reverse=True)
    items += "".join(f"<item><title>{html.escape(t)}</title><link>{u}</link><guid>{u}</guid><pubDate>{_rfc(d)}</pubDate><description>{html.escape(ld)}</description>"
                     + (f'<content:encoded><![CDATA[<p><img src="{BASE}{im}" alt="{html.escape(t)}"></p><p>{html.escape(ld)}</p>]]></content:encoded>' if os.path.exists(ROOT + im.replace("/assets", "/assets", 1)) or True else "") + "</item>\n" for d, t, u, ld, im in _ex[:60])
    open(f"{OUT}/rss.xml", "w", encoding="utf-8").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel><title>영진종합목재 소식·자재 정보</title><link>{BASE}/news/</link><description>대전 영진종합목재(월드건축자재) 자재 정보와 시공 소식</description><language>ko</language>\n{items}</channel></rss>\n')
    # wwood.kr(쇼핑몰) 상품 사이트맵 — 서치콘솔에서 두 사이트 모두 소유 확인되어 교차 제출 가능
    _ids = []
    for _p in open(ROOT + "/data/wwoodkr_products.txt").read().strip().split(","):
        _a, _, _b = _p.partition("-"); _ids += range(int(_a), int(_b or _a) + 1)
    _cats = "22,22-133,22-132,22-139,22-316,22-317,22-128,22-129,39-296,23,23-134,23-135,23-136,23-137,23-314,24,24-140,24-141,24-318,24-319,24-320,26,26-149,26-148,26-247,26-315,26-152,25,25-144,25-145,25-146,25-147,25-249,25-266,28,28-167,28-168,28-172,28-248,27,27-156,27-321,27-157,27-159,27-160,27-161,27-237,27-166,27-322,27-163,27-381,31,31-186,31-331,31-188,29,29-274,29-367,30,30-182,30-183,30-184,30-351,32,32-332,32-333,32-334,53,53-348,53-349,54,54-373,54-375,54-378,54-374,54-380,54-391,35,35-356,35-206,35-357,37,37-400,37-396,37-397,37-361,37-362,37-363,37-366,37-360,58,58-405,58-407,58-404,58-406,58-408,58-403,58-409,58-411,58-412,59,59-422,59-423,59-424,59-425".split(",")
    _cu = [("https://wwood.kr/home/mall/shoplist.php?depth=1&amp;code1_idx=" + c) if "-" not in c else ("https://wwood.kr/home/mall/shoplist.php?depth=2&amp;code1_idx=%s&amp;code2_idx=%s" % tuple(c.split("-"))) for c in _cats]
    _pu = ["https://wwood.kr/home/mall/shoplist.php?idx=%d&amp;pmode=view" % i for i in _ids]
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
    open(f"{OUT}/robots.txt", "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\nSitemap: {BASE}/sitemap-video.xml\nSitemap: {BASE}/rss.xml\n\n#DaumWebMasterTool:99e0908a419948d27287fb3d562fb5c6a299e4c3c385ed57b261247546dd22cc:VC4npJliHmrJLtJDnWYFDA==\n")
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
        h = hashlib.md5(b).hexdigest()[:12]
        if _lm.get(u, [None])[0] != h: _lm[u] = [h, today]
        return _lm[u][1]
    LMD = {u: _lmod(u) for u in SITEMAP}
    json.dump(_lm, open(_lmf, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    X = lambda t: html.escape(t, quote=True)
    open(f"{OUT}/sitemap-video.xml", "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">\n' +
        "".join(f"<url><loc>{u}</loc><video:video><video:thumbnail_loc>https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg</video:thumbnail_loc><video:title>{X(v['title'][:100])}</video:title><video:description>{X(dd[:2000])}</video:description><video:player_loc>https://www.youtube.com/embed/{v['id']}</video:player_loc>"
                + (f"<video:duration>{ln}</video:duration>" if ln else "")
                + (f"<video:publication_date>{_dt.datetime.fromtimestamp(ts, _dt.timezone(_dt.timedelta(hours=9))).isoformat()}</video:publication_date>" if ts else "")
                + "<video:family_friendly>yes</video:family_friendly></video:video></url>\n" for u, v, dd, ts, ln in VSM) + "</urlset>\n")
    open(f"{OUT}/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' +
        "".join(f"<url><loc>{u}</loc><lastmod>{LMD[u]}</lastmod>" + (f"<image:image><image:loc>{html.escape(SIMG[u])}</image:loc></image:image>" if SIMG.get(u) else "") + "".join(f"<image:image><image:loc>{BASE}/assets/{d_}/{u.rsplit('/', 1)[1][:-5]}-steps.jpg</image:loc></image:image>" for d_ in ("mandeul", "sigongbeop") if f"/{d_}/" in u and not u.endswith("/") and os.path.exists(f"{ROOT}/assets/{d_}/{u.rsplit('/', 1)[1][:-5]}-steps.jpg")) + "</url>\n" for u in SITEMAP) + "</urlset>\n")
    # 전체 자재 검색: 쇼핑몰 자재 + 제조사·철물·본덱스 사진 카드(.yri) 전부 → /assets/search.json
    _sx, _seen = list(idx), set()
    for d_ in ("bondex", "bupum", "yerim", "younglim", "shenu"):
        for fn in sorted(os.listdir(f"{OUT}/{d_}")) if os.path.isdir(f"{OUT}/{d_}") else []:
            if not fn.endswith(".html"): continue
            tx = open(f"{OUT}/{d_}/{fn}", encoding="utf-8").read()
            sec = re.search(r"<title>([^<|—]*)", tx); sec = (sec.group(1).strip() if sec else "")
            for m in re.finditer(r'<a class="yri" href="#" data-big="([^"]*)" data-n="([^"]*)"[^>]*>.*?</a>', tx, re.S):
                k_ = (m.group(2), m.group(1))
                if k_ in _seen: continue
                _seen.add(k_)
                pz = re.search(r'class="cbp">([\d,]+원~)', m.group(0))
                _sx.append({"n": html.unescape(m.group(2)), "i": m.group(1), "c": sec, "s": (pz.group(1) + " · " if pz else "") + sec, "l": f"/{d_}/{fn}".replace("/index.html", "/")})
    _PF = ["https://m.xn--392bopf4iwtp.com/web/product/medium/", "https://www.emalling.co.kr/web/product/medium/", "https://s3.ap-northeast-2.amazonaws.com/younglim-bucket/", "https://www.yerim.net/upload/product/", "https://namuip.com/cnd_home/assets/img/", "https://www.wwood.kr/"]
    for x in _sx:
        for k_, pf in enumerate(_PF):
            if x["i"].startswith(pf): x["i"] = f"~{k_}" + x["i"][len(pf):]; break
        if x.get("l"): x.pop("c", None)
    json.dump({"p": _PF, "d": _sx}, open(f"{OUT}/assets/search.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(len(SITEMAP), "pages →", OUT)

import hashlib
ASSET_V = hashlib.md5((open(f"{ROOT}/assets/style.css","rb").read()+open(f"{ROOT}/assets/site.js","rb").read())).hexdigest()[:8]
SITEMAP = []
VSM = []
ALLFAQ = []
SIMG = {}
build()
