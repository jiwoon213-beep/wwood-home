import re
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
    meta = json.loads(m.group(1)); meta["slug"] = fn[:-5]; meta["body"] = raw[m.end():]
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
    return (f'<a class="pd" href="https://wwood.kr/home/mall/shoplist.php?idx={p["id"]}&amp;pmode=view" target="_blank" rel="noopener">'
            f'<span class="pi"><img loading="lazy" src="{E(p["img"])}" alt="{E(p["name"])}"></span><b>{E(p["name"])}</b>{f"<small>{E(sub)}</small>" if sub else ""}</a>')
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
NAV = [("/jajae/", "자재 백과"), ("/jaryo/", "전체 자재"), ("/video/", "영상"), ("/news/", "소식·정보"), ("/price.html", "기준가"), ("/calc.html", "계산기"), ("/dome.html", "도매·납품"), ("/sigong.html", "시공"), ("/visit.html", "매장 안내")]

def page(path, title, desc, body, active="", jsonld=None, img=None):
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
<link rel="canonical" href="{canon}"><meta name="naver-site-verification" content="a59ff6921fc90666c920da00bf9a23ecb0ba3514"><meta property="og:type" content="website"><meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canon}"><meta property="og:image" content="{E(img or "https://i.ytimg.com/vi/xPsUVr7exLU/hqdefault.jpg")}"><meta property="og:site_name" content="영진종합목재 (월드건축자재)"><meta property="og:locale" content="ko_KR"><meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://i.ytimg.com"><link rel="preconnect" href="https://www.wwood.kr"><link rel="stylesheet" href="/assets/style.css?v={ASSET_V}">{'<meta name="robots" content="noindex,nofollow">' if PREVIEW else ''}{ld}</head><body>
<div class="top"><div class="wrap row sb"><span>{HOURS} · {ADDR}</span><span><a href="/dome.html">업체·도매회원</a> <a href="/visit.html">매장 길찾기</a></span></div></div>
<header><div class="wrap row sb hd"><a class="logo" href="/"><b>영진종합목재 (월드건축자재)</b><small>· 충청권 최대규모 목재상</small></a>
<nav>{nav}</nav></div></header>
<main>{body}</main>
<footer><div class="wrap">월드건축자재 · 영진종합목재(영진목재) · 상호 영진우드 · <a href="/daejeon.html">대전 목재</a> · <a href="/sejong.html">세종 목재</a> · <a href="/calc.html">자재 계산기</a> · <a href="/yongeo.html">현장 용어</a> | {ADDR} | {TEL} | {HOURS}<br>
시공: 월드아키텍쳐 | 대표 김지운 | 사업자등록번호 281-05-03197 | {LIC}<br>
카카오톡 <a href="{KAKAO}/chat">영진종합목재 채널 상담</a> · 유튜브 <a href="{YT}">@월드건축자재DIY</a> · <a href="{YT2}">@월드도어</a> · 도매회원 쇼핑몰 <a href="{DOME}">wwood.kr</a> · 표시 가격은 부가세 별도 소매 기준가이며 결제·재단은 매장에서 합니다.</div></footer>
<div class="mbar"><a class="b g" href="/visit.html">매장 길찾기</a><a class="b d" href="tel:{TEL.replace('-','')}">전화</a></div>
<script src="/assets/site.js?v={ASSET_V}" defer></script></body></html>"""
    if PREFIX: doc = doc.replace('href="/', f'href="{PREFIX}/').replace('src="/', f'src="{PREFIX}/')
    fp = os.path.join(OUT, path); os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(doc)
    SITEMAP.append(canon); SIMG[canon] = img

def vcard(v, big=False):
    return f"""<a class="vc{' big' if big else ''}{' sh' if v['type']=='S' else ''}" href="{vpage(v)}"{'' if v['id'] in VD else ' target="_blank" rel="noopener"'} data-yt="{v['id']}">
<span class="th"><img loading="lazy" src="https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg" alt="{E(vshort(v['title']))}"><i class="play"></i>{'<em>쇼츠</em>' if v['type']=='S' else '<em>라이브</em>' if v['type']=='V' else ''}</span>
<b>{E(v['title'])}</b><small>조회 {views(v['n'])}</small></a>"""

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
       "openingHours": ["Mo-Fr 07:00-18:00", "Sa-Su 07:00-15:00"], "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "07:00", "closes": "18:00"}, {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Saturday", "Sunday"], "opens": "07:00", "closes": "15:00"}, {"@type": "OpeningHoursSpecification", "dayOfWeek": "PublicHolidays", "opens": "07:00", "closes": "16:00"}], "url": BASE + "/", "sameAs": [YT, YT2, MALL, KAKAO], "alternateName": ["영진목재", "월드건축자재", "영진우드"], "legalName": "영진우드",
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
    hot = vsplit(top(lambda v: v["id"] != "xPsUVr7exLU", 10**6), "h3", 8, 6)
    ids = LATEST
    if not ids and os.path.exists(f"{ROOT}/data/yt_all.tsv"):
        rows = [l.rstrip("\n").split("\t") for l in open(f"{ROOT}/data/yt_all.tsv", encoding="utf-8") if l.strip()]
        rows = [r for r in rows if len(r) > 3 and r[3].isdigit()]
        rows.sort(key=lambda r: -int(r[3]))
        ids = [r[0] for r in rows if r[1] != "S"][:4] + [r[0] for r in rows if r[1] == "S"][:4]
    newv = [byid[i] for i in ids if i in byid][:8]
    newsec = (f'<section class="wrap sec"><h2>새로 올라온 영상</h2>{vsplit(newv, "h3")}</section>' if newv else "")
    plist = lambda ps: "".join(f'<a class="pc" href="/news/{p["slug"]}.html"><small>{E(p.get("date",""))}</small><b>{E(p["title"])}</b><span>{E(p.get("desc",""))}</span></a>' for p in ps)
    postsec = (f'<section class="wrap sec"><h2>소식·자재 정보</h2><div class="pl">{plist(POSTS[:6])}</div><p><a href="/news/">전체 글 보기 →</a></p></section>' if POSTS else "")
    base8 = [("합판","일반 4×8 · 8.5mm(베트남)",22800),("OSB합판","T&G 4×8 · 18.3mm",35200),("MDF","4×8 · 9mm",14800),("구조재 2×4","38×89 · 12ft",10700),
             ("방부목 데크재","20×120 · 12자",10500),("석고보드","3×6 · 9.5T",5200),("합성데크","20×140 · 3000",21500),("다루끼(소송)","1.0×1.0 · 12자 · 12개",42400)]
    bt = "".join(f"<tr><td>{a}</td><td>{b}</td><td class=r><b>{won(c)}</b></td></tr>" for a, b, c in base8)
    body = f"""
<section class="hero"><div class="wrap g2">
<div><span class="chip red">영상으로 보고 · 매장에서 바로</span>
<h1>어디에 쓰는 나무인지<br>영상으로 먼저 보고<br>매장에서 바로 가져가세요</h1>
<p class="lead">현장 목수·기술자가 직접 쓰는 자재를 영상마다 정리했습니다. 대전 3000평 매장에서 실물 확인부터 원하는 사이즈 재단까지 그 자리에서 해드립니다.</p>
<div class="row"><a class="b r" href="/visit.html">매장 길찾기</a><a class="b o" href="/price.html">기준가 보기</a><a class="b o" href="/calc.html">자재 계산기</a><a class="b d" href="/dome.html">업체·도매회원</a></div></div>
<div>{embed(tour) if tour else ''}<p class="small muted">대전 목재소·건축자재 백화점 3000평 투어 · 조회 18만회</p></div></div></section>
<section class="stat"><div class="wrap g4"><div><b>구독 {ST["subs"]}명</b><small>유튜브 월드건축자재DIY</small></div><div><b>영상 {int(ST["videos"]):,}개</b><small>시공·DIY·자재 정보</small></div>
<div><b>소매 + 도매</b><small>셀프 고객부터 현장 납품까지</small></div><div><b>직접 시공</b><small>월드아키텍쳐 · {LIC}</small></div></div></section>
<div class="hx"><section class="wrap sec"><h2>무엇을 만들고 싶으세요?</h2><p class="muted">고르면 그 용도의 자재와 시공 영상이 한 번에 나옵니다.</p><div class="ug">{use}</div></section>
<section class="wrap sec"><h2>자재 백과 — 이 나무, 어디에 쓰나요?</h2><p class="muted">용도·인테리어 효과·기준가·관련 영상을 자재별로 정리했습니다.</p><div class="mg">{mats}</div></section>
{postsec}{newsec}
<section class="wrap sec"><h2>많이 본 영상</h2>{hot}<p><a href="{YT}" target="_blank" rel="noopener">유튜브 채널 전체 보기 →</a></p></section></div>
<section class="wrap sec g2"><div class="card"><h2>기본 자재 기준가</h2><p class="muted small">부가세 별도 · 규격·수량에 따라 달라집니다</p>
<div class="tw"><table><thead><tr><th>자재</th><th>규격</th><th class=r>기준가</th></tr></thead><tbody>{bt}</tbody></table></div>
<p class="small">재단비·운임·수량 할인은 매장에서 계산 · 고재·수입목·특수목은 매장 문의 · 도매가는 회원 로그인 후</p><a href="/price.html">기준가 전체 보기 →</a></div>
<div class="card dark"><h2>직접 하기 어렵다면, 시공까지</h2><p>자재를 가장 잘 아는 목재상이 직접 시공합니다. 월드아키텍쳐({LIC})가 대전·세종 전 공정을 시공하고, 모든 현장은 유튜브에 공개합니다.</p>
<a class="b r" href="/sigong.html">시공 사례 보기</a></div></section>{CTA}"""
    page("index.html", "대전 목재·세종 목재 영진목재 | 3000평 목재소, 원하는 사이즈 즉석 재단", "대전 목재·세종 목재 영진목재(월드건축자재). 3000평 목재소, 합판·방부목·데크 즉석 재단, 기준가·시공 영상.", body, "", BIZ)

    # 소식·정보
    page("news/index.html", "소식·자재 정보 — 목재·건축자재 가격, 시공 팁 | 대전 월드건축자재", "대전 월드건축자재(영진목재)의 자재 정보, 기준가, 시공 사례, 새 영상 소식.",
         f'<section class="wrap sec"><h1>소식·자재 정보</h1><p class="lead">자재 고르는 법, 기준가, 시공 사례와 새 영상 소식을 매일 올립니다.</p><div class="pl">{plist(POSTS)}</div></section>{CTA}', "/news/")
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
         f'<section class="wrap sec"><h1>자재 백과</h1><p class="lead">손님들이 가장 헷갈리는 "이 자재 어디에 쓰나요?"를 자재별로 정리했습니다.</p><p><a class="b o" href="/bigyo/">자재 비교 전체 보기 (14종)</a> <a class="b o" href="/calc.html">자재 계산기</a> <a class="b o" href="/yongeo.html">현장 용어 사전</a></p><div class="mg m2">{lst}</div></section>{CTA}', "/jajae/")
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
        cmpln = f'<p>👉 <a href="/bigyo/{cmpl}.html">비슷한 자재와 비교해 보기</a> · <a href="/calc.html">필요한 양 계산하기</a></p>' if cmpl else (f'<p>👉 <a href="/calc.html#door">문짝·문틀 크기 계산하기</a></p>' if m["slug"] == "door" else '<p>👉 <a href="/calc.html">필요한 양 계산하기</a></p>')
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
<section class="wrap sec"><h2>{m['name']} 시공·사용 영상</h2>{vid}</section>{faqsec}{CTA}"""
        page(f"jajae/{m['slug']}.html", f"{m['kw']} — 용도·기준가·시공 영상 | 대전 영진목재",
             f"{m['name']} 용도와 인테리어 효과, 규격별 소매 기준가, 시공 영상. 대전 유성 월드건축자재 매장에서 즉석 재단.", body, "/jajae/",
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
    jrows = "".join(f'<section class="wrap sec jall" id="c{sl}"><h2>{n} <small class="muted">{cnt[c]}종</small> <a class="small" href="/jaryo/{sl}.html">전체 보기 ›</a></h2><p class="small muted">{d}</p><div class="pg hrow">' + "".join(pcard(p) for p in [p for p in PROD if c in p["tops"]][:16]) + f'<a class="pd more" href="/jaryo/{sl}.html"><span class="pi"><b>+{max(0,cnt[c]-16)}</b></span><b>{n} 전체 보기 ›</b><small>{cnt[c]}종</small></a></div><p class="hsh">옆으로 밀어서 더 보기 ›</p></section>' for c, sl, n, d in JCAT if cnt[c])
    page("jaryo/index.html", f"전체 자재 사진 {len([p for p in PROD if p['tops']])}종 — 각재·합판·데크·사이딩·철물 | 대전 영진목재", "대전 월드건축자재(영진목재) 매장 취급 자재를 사진으로 확인하세요. 각재, 합판, 집성판, 데크, 마루, 내장재, 타일, 사이딩, 철물, 스테인.",
         f'<section class="wrap sec"><h1>전체 자재</h1>{SEARCH}<p class="lead">매장에서 취급하는 자재를 사진으로 모았습니다. 실물은 대전 매장에서 보고, 원하는 사이즈로 재단해 가세요. 가격은 <a href="/price.html">기준가</a> 또는 매장에서 안내합니다.</p><div class="chips jall jchips">{jchips}</div></section>{jrows}{CTA}', "/jaryo/", None, thumb.get("24"))
    for c, sl, n, d in JCAT:
        ps = [p for p in PROD if c in p["tops"]]
        if not ps: continue
        subs = []
        for p in ps:
            if subof(p, c) not in subs: subs.append(subof(p, c))
        secs = ""
        for sb in subs:
            g = [p for p in ps if subof(p, c) == sb]
            title = MCAT.get(sb or "", "") or "기타"
            secs += f'<h2 id="s{(sb or "x").split("/")[-1] or "x"}">{E(title)} <small class="muted">{len(g)}종</small></h2><div class="pg hrow">{"".join(pcard(p) for p in g)}</div>' + ('<p class="hsh">옆으로 밀어서 더 보기 ›</p>' if len(g) > 2 else '')
        toc = " · ".join(f'<a href="#s{(sb or "x").split("/")[-1] or "x"}">{E(MCAT.get(sb or "", "") or "기타")}</a>' for sb in subs)
        page(f"jaryo/{sl}.html", f"{n} 종류 사진 {len(ps)}종 — {d} | 대전 월드건축자재", f"{n} 종류를 사진으로 확인하세요: {d}. 대전 유성 월드건축자재(영진목재) 매장 취급, 즉석 재단.",
             f'<section class="wrap sec"><p class="crumb"><a href="/jaryo/">전체 자재</a> › {n}</p><h1>{n} <small class="muted">{len(ps)}종</small></h1><p class="lead">{d}. 사진을 누르면 상세 사진이 열립니다. 실물 확인·재단은 대전 매장에서 합니다.</p>{SEARCH}<div class="jall"><p class="small">{toc}</p>{secs}</div></section>{CTA}', "/jaryo/",
             {"@context": "https://schema.org", "@type": "ItemList", "name": f"{n} 종류", "numberOfItems": len(ps),
              "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": p["name"], "image": p["img"]} for i, p in enumerate(ps[:100])]}, ps[0]["img"])

    # 영상
    vl = "".join(f'<a class="uc" href="/video/{c}.html"><b>{n}</b><small>{d} · {sum(1 for v in V if v["cat"]==c)}편</small></a>' for c, n, d in CATS)
    PLS = [('PLFOIw225ouPo', '건축자재 종류 & 방부목 데크'), ('PLVA2J1KAJvsk', '목조 비닐하우스 짓기'), ('PLahzdcM8tSYQ', '목공 기초 & 원목 가구'), ('PLdOhbZ-KJAiQ', '싱크대 셀프 리폼'), ('PLSZCoKnD3ZJs', '세라믹사이딩 외벽 시공'), ('PLRSwZ8WxHpV8', '인테리어 필름 시공·견적'), ('PLbvlO5h0i7mo', '반셀프 인테리어 공정 순서'), ('PLfQ12jGtwTx0', '인테리어 견적 비교'), ('PLCMIh2xFaEFE', '주차장·토목 현장'), ('PLE3-sMP7uo2k', '건축자재 꿀팁 쇼츠'), ('PLEp1gBHSiHds', 'CNC 목공 라이브')]
    plh = "".join(f'<a href="https://www.youtube.com/playlist?list={i}" target="_blank" rel="noopener">▶ {n}</a>' for i, n in PLS)
    page("video/index.html", "시공·DIY 영상 모음 — 데크·온실·가구·외벽·인테리어 | 월드건축자재DIY", "월드건축자재DIY 유튜브 영상을 용도별로 정리했습니다. 데크, 목조 온실, 원목가구, 싱크대, 외벽, 바닥, 전기.",
         f'<section class="wrap sec"><h1>영상으로 찾기</h1><p class="lead">유튜브 「월드건축자재DIY」·「월드도어」 공개 영상 {len(V)}편(일반·쇼츠·라이브)을 용도별로 모두 모았습니다. 새 영상은 자동으로 추가됩니다.</p><div class="ug m2">{vl}</div><h2>유튜브 재생목록</h2><div class="plc">{plh}</div><p><a href="{YT}">유튜브 채널 바로가기 →</a></p></section>{CTA}', "/video/")
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
         f'<section class="wrap sec ptsec"><h1>소매 기준가</h1>{psearch}<p class="lead">자주 찾는 자재의 소매 기준가입니다(부가세 별도). 규격·수량에 따라 달라지며 재단비·운임은 매장에서 계산합니다. 도매가는 <a href="/dome.html">도매회원</a> 로그인 후 확인하세요.</p>{secs}</section>{CTA}', "/price.html")

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
<div class="row"><a class="b r" href="tel:{TEL.replace('-','')}">시공 상담 전화 {TEL}</a></div><p class="small">시공 지역: 대전·세종 전 공정 · 관급·대기업·전국 공사는 전화 문의</p></div></section>
{"".join([]) if not os.path.exists(ROOT+"/data/cases.json") else "<section class=\"wrap sec\"><h2>시공 사례</h2><div class=\"pl hs\">" + "".join(f'<a class="pc" href="/sigong/{c["slug"]}.html"><img loading="lazy" src="https://i.ytimg.com/vi/{c["videos"][0]}/mqdefault.jpg" alt=""><small>{E(c["place"] or "월드아키텍쳐 시공")}</small><b>{E(c["title"])}</b><span>{E(c["desc"][:70])}…</span></a>' for c in json.load(open(ROOT+"/data/cases.json", encoding="utf-8"))) + "</div><p class=\"hsh\">옆으로 밀어서 더 보기 ›</p></section>"}
<section class="wrap sec"><h2>시공 현장 영상</h2>{sv}</section>{casesec}
<section class="wrap sec g2"><div class="card"><h2>상담 순서</h2><ol><li>전화 상담 {TEL}</li><li>현장 방문 · 실측</li><li>견적서</li><li>시공 (현장은 유튜브 공개)</li></ol></div>
<div class="card"><h2>업체 고르기 전에 꼭 보세요</h2><p>면허 확인, 하자 예방, 견적 보는 법 영상을 모았습니다. 월드아키텍쳐는 실내건축공사업 등록 업체입니다.</p><a href="/video/tips.html">업체 고르는 법 영상 모음 →</a></div></section>
<section class="wrap sec">{tips}</section>{CTA}""", "/sigong.html")

    # 매장
    page("visit.html", "대전 목재소 영진목재 위치·영업시간 — 유성대로 44, 즉석 재단", f"월드건축자재(영진종합목재) {ADDR}. {HOURS}. 3000평 매장, 즉석 재단, 대전·세종 배송. {TEL}.",
         f"""<section class="wrap sec g2"><div>{embed(tour) if tour else ''}</div><div><h1>매장 오시는 길</h1>
<div class="tw"><table><tbody><tr><th>주소</th><td>{ADDR} 월드건축자재(영진목재)</td></tr><tr><th>영업</th><td>{HOURS}</td></tr><tr><th>전화</th><td><a href="tel:{TEL.replace('-','')}">{TEL}</a></td></tr>
<tr><th>재단</th><td>원하는 사이즈로 즉석 재단</td></tr><tr><th>배송</th><td>대전·세종·공주·계룡·논산·금산·옥천 배송 · 현장 납품 · 그 외 전국은 용달 배송(전화로 운임 견적 → 입금 확인 후 출고)</td></tr><tr><th>도매</th><td>사업자등록증·명함 확인 후 도매회원 승인</td></tr><tr><th>시공</th><td>월드아키텍쳐 · 대전·세종 · 전화 상담</td></tr></tbody></table></div>
<div class="row"><a class="b g" href="https://map.naver.com/p/search/{ADDR.replace(' ','%20')}%20영진종합목재" target="_blank" rel="noopener">네이버 지도로 길찾기</a><a class="b d" href="tel:{TEL.replace('-','')}">전화</a><a class="b" style="background:#fee500;color:#191919" href="{KAKAO}/chat" target="_blank" rel="noopener">카톡 문의</a></div></div></section>{"" if not os.path.exists(ROOT+"/data/store_photos.json") else '<section class="wrap sec"><h2>매장 사진</h2><div class="pg hrow">' + "".join(f'<a class="ph" href="/assets/store/{n}.jpg" target="_blank"><img loading="lazy" src="/assets/store/{n}.jpg" alt="{E(t)}"><small>{E(t)}</small></a>' for n, t in json.load(open(ROOT+"/data/store_photos.json", encoding="utf-8"))) + '</div><p class="hsh">옆으로 밀어서 더 보기 ›</p></section>'}""", "/visit.html", BIZ, BASE+"/assets/store/storefront.jpg")

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
<div class="card"><h2>{ra}에서 {nm} 쓰는 곳</h2><ul>{"".join(f"<li>{E(w)}</li>" for w in m["where"])}</ul><p><a href="/jajae/{m['slug']}.html">{nm} 용도·고르는 법 자세히 →</a> · <a href="/calc.html">필요한 양 계산</a></p></div></section>
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
    page("calc.html", "자재 계산기 — 데크·석고보드·합판 몇 장? 문짝·중문 크기까지 | 영진목재", "데크 방부목·합성데크 장수, 석고보드·합판·단열재 장수, 몰딩·걸레받이 길이, 데코타일·강마루 박스 수, 페인트 양, 평↔㎡를 바로 계산하세요. 대전 영진목재(월드건축자재) 재단·배송.",
f"""<section class="wrap sec"><h1>자재 계산기</h1><p class="lead">필요한 양을 미리 계산해 오시면 매장에서 바로 재단해 드립니다. 결과는 참고용입니다(로스 포함).</p>
<div class="chips" id="cchips">{chips}</div>
<div class="cnav"><button class="cb" data-d="-1">◀ 이전</button><span id="cpos" class="small muted"></span><button class="cb" data-d="1">다음 ▶</button></div>
<div class="cslider" id="cslider">{slides}</div>
<h2 class="cfaq">자주 묻는 질문</h2>{faqslide(CALC_FAQ)}</section>
<style>.cslider{{display:flex;align-items:flex-start;transition:height .2s;overflow-x:auto;overflow-y:hidden;scroll-snap-type:x mandatory;gap:12px;scrollbar-width:none;-webkit-overflow-scrolling:touch}}.cslider::-webkit-scrollbar{{display:none}}.cslide{{flex:0 0 100%;scroll-snap-align:start}}.cslide .card{{margin:0}}.cfaq{{margin:22px 0 10px;font-size:22px}}
.cnav{{display:flex;justify-content:space-between;align-items:center;margin:6px 0 10px}}.cb{{padding:8px 14px;border:1px solid var(--line);border-radius:10px;background:#fff;font-weight:700;cursor:pointer}}
#cchips{{display:flex;gap:6px;overflow-x:auto;flex-wrap:nowrap;padding-bottom:4px}}#cchips .chip{{flex:0 0 auto;border:1px solid var(--line);background:#faf8f5;cursor:pointer;font-size:14px}}#cchips .chip.on{{background:var(--red);color:#fff;border-color:var(--red)}}
.cg{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 10px;margin:10px 0}}@media(min-width:760px){{.cg{{grid-template-columns:repeat(4,minmax(0,1fr))}}}}.cg label{{display:flex;flex-direction:column;font-size:14px;gap:4px}}.cg input,.cg select{{font-size:16px;padding:9px;border:1px solid #ccc;border-radius:8px;width:100%;box-sizing:border-box}}
.cr{{background:#fff7ed;border-radius:10px;padding:12px 14px;font-size:16px;line-height:1.7}}.cr b{{font-size:20px;color:#c2410c}}.ql{{color:#1d4ed8;font-weight:700;text-decoration:underline}}.qb{{margin-top:8px;font-size:14px;line-height:2}}.qb .ql{{display:inline-block;margin-right:8px;padding:2px 8px;border:1px solid #c7d2fe;border-radius:14px;background:#fff;text-decoration:none}}</style>
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
    for v in V:
        if v["id"] not in VD: continue
        d, ln, ts = VD[v["id"]]
        st = vshort(v["title"])
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
        page(f"v/{v['id']}.html", f"{st} — 영상 | 대전 영진목재", (first or st)[:80],
             f"""<section class="wrap sec"><p class="crumb"><a href="/video/">영상</a> › <a href="/video/{v['cat']}.html">{E(cn)}</a></p><h1 class="vt1">{E(v['title'])}</h1>
<div class="{'emb sh1' if v['type']=='S' else 'emb'}"><iframe loading="lazy" src="https://www.youtube.com/embed/{v['id']}" title="{E(st)}" allowfullscreen></iframe></div>
<p class="small muted">조회 {views(v['n'])}{' · 쇼츠' if v['type']=='S' else ''} · <a href="{vurl(v)}" target="_blank" rel="noopener">유튜브에서 보기</a></p>
<div class="vdesc">{vbody(d, v['id'])}</div>
{f'<p>👉 영상에 나온 자재: {ml}</p>' if ml else ''}<p>👉 <a href="/calc.html">필요한 양 계산하기</a> · <a href="/visit.html">매장에서 재단해 가기</a></p></section>
{f'<section class="wrap sec"><h2>비슷한 영상</h2>{vsplit(rel, "h3")}</section>' if rel else ''}{CTA}""", f"/video/", ld, f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg")

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
    for p in PROD:
        if not p["tops"] or p["top"] not in jn: continue
        sl, cn, cd = jn[p["top"]]
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
        page(f"p/{p['id']}.html", f"{p['name']} — {cat} | 대전 영진목재", f"{p['name']} ({cat}) 사진. 대전 영진목재(월드건축자재) 매장 취급, 원하는 사이즈 재단·배송.",
             f"""<section class="wrap sec"><p class="crumb"><a href="/jaryo/">전체 자재</a> › <a href="/jaryo/{sl}.html">{E(cn)}</a>{f' › {E(sname)}' if sname else ''}</p>
<div class="g2 pdet"><div><img class="pimg" src="{E(p['img'])}" alt="{E(p['name'])}"></div><div><h1>{E(p['name'])}</h1><p class="muted">{E(cat)}</p>
<p>대전 유성 영진목재(월드건축자재) 3000평 매장에서 실물을 보고 고를 수 있습니다. 원하는 사이즈로 재단해 드리고 대전·세종·공주·계룡·논산·금산·옥천은 배송하고, 그 외 전국은 용달차로 보내 드립니다(운임 견적 → 입금 확인 후 출고). 가격·재고는 쇼핑몰이나 매장(042-545-2900)에서 확인하세요.</p>
<div class="row"><a class="b r" href="https://wwood.kr/home/mall/shoplist.php?idx={p['id']}&amp;pmode=view" target="_blank" rel="noopener">쇼핑몰에서 가격 보기</a><a class="b d" href="tel:{TEL.replace('-','')}">전화 문의</a></div>
<p class="small"><a href="/calc.html">필요한 양 계산하기</a> · <a href="/visit.html">매장 위치</a> · <a href="/jaryo/{sl}.html">{E(cn)} 전체 보기</a></p></div></div>{use}</section>
<section class="wrap sec"><h2>같은 분류 제품</h2><div class="pg hrow">{"".join(pcard2(q) for q in sim)}</div></section>{CTA}""", "/jaryo/", None, p["img"])

    # 매장 카운터 QR 안내판이 여는 페이지(/r/) — 리뷰·채널 링크는 여기서만 바꾸면 됨(재인쇄 불필요)
    RV_NAVER = "https://map.naver.com/p/search/%EC%98%81%EC%A7%84%EC%A2%85%ED%95%A9%EB%AA%A9%EC%9E%AC"
    RV_GOOGLE = "https://www.google.com/maps/search/?api=1&query=%EC%98%81%EC%A7%84%EC%A2%85%ED%95%A9%EB%AA%A9%EC%9E%AC+%EB%8C%80%EC%A0%84+%EC%9C%A0%EC%84%B1%EB%8C%80%EB%A1%9C+44"
    RV_KAKAOMAP = "https://map.kakao.com/?q=%EC%98%81%EC%A7%84%EC%A2%85%ED%95%A9%EB%AA%A9%EC%9E%AC"
    rbtn = lambda href, bg, fg, t, sub: f'<a href="{href}" target="_blank" rel="noopener" style="display:block;background:{bg};color:{fg};border-radius:14px;padding:18px 20px;margin:12px 0;text-decoration:none;font-size:20px;font-weight:800">{t}<small style="display:block;font-size:14px;font-weight:500;opacity:.85;margin-top:4px">{sub}</small></a>'
    page("r/index.html", "영진종합목재 리뷰·카톡 채널", "영진종합목재(월드건축자재) 방문 리뷰 남기기, 카카오톡 채널 추가, 자재 정보 보기.",
         '<section class="wrap sec" style="max-width:520px"><h1 style="font-size:26px">방문해 주셔서 감사합니다</h1><p class="lead">리뷰 한 줄이 동네 손님들께 큰 도움이 됩니다.</p>'
         + rbtn(RV_NAVER, "#03c75a", "#fff", "네이버 리뷰 쓰기", "지도에서 영진종합목재 → 리뷰 → 영수증 인증")
         + rbtn(f"{KAKAO}/friend", "#fee500", "#191919", "카카오톡 채널 추가", "재고·가격 문의를 카톡으로 바로")
         + rbtn(RV_GOOGLE, "#1a73e8", "#fff", "구글 리뷰 쓰기", "구글 지도 → 영진종합목재 → 리뷰 작성")
         + rbtn(RV_KAKAOMAP, "#3b82f6", "#fff", "카카오맵 후기 쓰기", "카카오맵에서 영진종합목재 검색")
         + rbtn("/jajae/", "#333", "#fff", "자재 사진·기준가 보기", "합판·각재·데크·사이딩 등 용도와 기준가")
         + f'<p class="small muted">{ADDR} · {TEL} · {HOURS}</p></section>', "")
    SITEMAP[:] = [u for u in SITEMAP if not u.endswith("/r/")]
    # robots, sitemap
    if PREVIEW: print(len(SITEMAP), "preview pages →", OUT); return
    open(f"{OUT}/b4237bce57cfb60c93b64e5203857f41.txt", "w").write("b4237bce57cfb60c93b64e5203857f41")  # IndexNow 키(네이버·빙)
    # RSS (네이버 서치어드바이저 RSS 제출용)
    def _rfc(d):
        try: return datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%a, %d %b %Y 09:00:00 +0900")
        except Exception: return ""
    items = "".join(f"<item><title>{html.escape(p['title'])}</title><link>{BASE}/news/{p['slug']}.html</link><guid>{BASE}/news/{p['slug']}.html</guid><pubDate>{_rfc(p.get('date',''))}</pubDate><description>{html.escape(p.get('desc',''))}</description><content:encoded><![CDATA[{p['body'].replace(']]>',']]&gt;').replace('href="/', 'href="'+BASE+'/').replace('src="/', 'src="'+BASE+'/')}]]></content:encoded></item>\n" for p in POSTS[:50])
    open(f"{OUT}/rss.xml", "w", encoding="utf-8").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel><title>영진종합목재 소식·자재 정보</title><link>{BASE}/news/</link><description>대전 영진종합목재(월드건축자재) 자재 정보와 시공 소식</description><language>ko</language>\n{items}</channel></rss>\n')
    # wwood.kr(쇼핑몰) 상품 사이트맵 — 서치콘솔에서 두 사이트 모두 소유 확인되어 교차 제출 가능
    _ids = []
    for _p in open(ROOT + "/data/wwoodkr_products.txt").read().strip().split(","):
        _a, _, _b = _p.partition("-"); _ids += range(int(_a), int(_b or _a) + 1)
    _cats = "22,22-133,22-132,22-139,22-316,22-317,22-128,22-129,39-296,23,23-134,23-135,23-136,23-137,23-314,24,24-140,24-141,24-318,24-319,24-320,26,26-149,26-148,26-247,26-315,26-152,25,25-144,25-145,25-146,25-147,25-249,25-266,28,28-167,28-168,28-172,28-248,27,27-156,27-321,27-157,27-159,27-160,27-161,27-237,27-166,27-322,27-163,27-381,31,31-186,31-331,31-188,29,29-274,29-367,30,30-182,30-183,30-184,30-351,32,32-332,32-333,32-334,53,53-348,53-349,54,54-373,54-375,54-378,54-374,54-380,54-391,35,35-356,35-206,35-357,37,37-400,37-396,37-397,37-361,37-362,37-363,37-366,37-360,58,58-405,58-407,58-404,58-406,58-408,58-403,58-409,58-411,58-412,59,59-422,59-423,59-424,59-425".split(",")
    _cu = [("https://wwood.kr/home/mall/shoplist.php?depth=1&amp;code1_idx=" + c) if "-" not in c else ("https://wwood.kr/home/mall/shoplist.php?depth=2&amp;code1_idx=%s&amp;code2_idx=%s" % tuple(c.split("-"))) for c in _cats]
    _pu = ["https://wwood.kr/home/mall/shoplist.php?idx=%d&amp;pmode=view" % i for i in _ids]
    open(f"{OUT}/wwoodkr-sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n<url><loc>https://wwood.kr/home/mall/</loc></url>\n' + "".join(f"<url><loc>{u}</loc></url>\n" for u in _cu + _pu) + "</urlset>\n")
    open(f"{OUT}/robots.txt", "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\nSitemap: {BASE}/rss.xml\n")
    today = datetime.date.today().isoformat()
    open(f"{OUT}/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' +
        "".join(f"<url><loc>{u}</loc><lastmod>{today}</lastmod>" + (f"<image:image><image:loc>{html.escape(SIMG[u])}</image:loc></image:image>" if SIMG.get(u) else "") + "</url>\n" for u in SITEMAP) + "</urlset>\n")
    print(len(SITEMAP), "pages →", OUT)

import hashlib
ASSET_V = hashlib.md5((open(f"{ROOT}/assets/style.css","rb").read()+open(f"{ROOT}/assets/site.js","rb").read())).hexdigest()[:8]
SITEMAP = []
SIMG = {}
build()
