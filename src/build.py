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
BLOG = "https://blog.naver.com/swr4083"
TEL = "042-545-2900"
ADDR = "대전 유성대로 44, 1층"
HOURS = "월~토 08:00~18:00"
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
    if not o or o == p["price"]: return '<td class="r ch">-</td>'
    d = p["price"] - o; pc = d / o * 100
    return f'<td class="r ch {"up" if d > 0 else "dn"}">{"▲" if d > 0 else "▼"} {abs(d):,}원 ({pc:+.1f}%)</td>'
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
def pcard(p):
    sub = MCAT.get(p["sub"] or "", "")
    return (f'<a class="pd" href="https://wwood.kr/home/mall/shoplist.php?idx={p["id"]}&amp;pmode=view" target="_blank" rel="noopener">'
            f'<span class="pi"><img loading="lazy" src="{E(p["img"])}" alt="{E(p["name"])}"></span><b>{E(p["name"])}</b>{f"<small>{E(sub)}</small>" if sub else ""}</a>')
# 유튜브 채널 숫자: data/stats.json {"subs": "1.36만", "videos": 940, "date": "YYYY-MM-DD"} (하루 1번 자동 갱신)
ST = json.load(open(f"{ROOT}/data/stats.json", encoding="utf-8")) if os.path.exists(f"{ROOT}/data/stats.json") else {"subs": "1.3만", "videos": 900}
# 최신 영상: data/latest.txt (영상 ID, 최신이 위)
LATEST = [l.strip() for l in open(f"{ROOT}/data/latest.txt", encoding="utf-8")] if os.path.exists(f"{ROOT}/data/latest.txt") else []

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

def mat_prices(m, k=10):
    cats, inc, exc = m["price"]
    if not cats: return []
    rows = [p for p in P if p["cat"] in cats and re.search(inc, p["name"]) and not (exc and re.search(exc, p["name"]))]
    return sorted(rows, key=lambda p: -p["qty"])[:k]

# ---------- layout ----------
NAV = [("/jajae/", "자재 백과"), ("/jaryo/", "전체 자재"), ("/video/", "영상"), ("/news/", "소식·정보"), ("/price.html", "기준가"), ("/dome.html", "도매·납품"), ("/sigong.html", "시공"), ("/visit.html", "매장 안내")]

def page(path, title, desc, body, active="", jsonld=None, img=None):
    canon = BASE + ("/" + path if path != "index.html" else "/").replace("index.html", "")
    nav = "".join(f'<a href="{h}"{" class=on" if active==h else ""}>{t}</a>' for h, t in NAV)
    lds = jsonld if isinstance(jsonld, list) else ([jsonld] if jsonld else [])
    lds = lds + [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "홈", "item": BASE + "/"}] +
                 ([{"@type": "ListItem", "position": 2, "name": dict(NAV).get(active, ""), "item": BASE + active}] if active and active != "/" else []) +
                 ([{"@type": "ListItem", "position": 3 if active else 2, "name": title.split(" — ")[0].split(" | ")[0], "item": canon}] if canon.rstrip("/") != (BASE + active).rstrip("/") and path != "index.html" else [])}]
    ld = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    doc = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canon}"><meta name="naver-site-verification" content="a59ff6921fc90666c920da00bf9a23ecb0ba3514"><meta property="og:type" content="website"><meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canon}"><meta property="og:image" content="{E(img or "https://i.ytimg.com/vi/xPsUVr7exLU/hqdefault.jpg")}"><meta property="og:site_name" content="영진종합목재 (월드건축자재)"><meta property="og:locale" content="ko_KR"><meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/assets/style.css">{'<meta name="robots" content="noindex,nofollow">' if PREVIEW else ''}{ld}</head><body>
<div class="top"><div class="wrap row sb"><span>{HOURS} · {ADDR}</span><span><a href="/dome.html">업체·도매회원</a> <a href="/visit.html">매장 길찾기</a></span></div></div>
<header><div class="wrap row sb hd"><a class="logo" href="/"><b>영진종합목재 (월드건축자재)</b><small>· 충청권 최대규모 목재상</small></a>
<nav>{nav}</nav></div></header>
<main>{body}</main>
<footer><div class="wrap">월드건축자재 · 영진종합목재 | {ADDR} | {TEL} | {HOURS}<br>
시공: 월드아키텍쳐 | 대표 김지운 | 사업자등록번호 281-05-03197 | {LIC}<br>
유튜브 <a href="{YT}">@월드건축자재DIY</a> · <a href="{YT2}">@월드도어</a> · 네이버 블로그 <a href="{BLOG}">swr4083</a> · 도매회원 쇼핑몰 <a href="{DOME}">wwood.kr</a> · 표시 가격은 부가세 별도 소매 기준가이며 결제·재단은 매장에서 합니다.</div></footer>
<div class="mbar"><a class="b g" href="/visit.html">매장 길찾기</a><a class="b d" href="tel:{TEL.replace('-','')}">전화</a></div>
<script src="/assets/site.js" defer></script></body></html>"""
    if PREFIX: doc = doc.replace('href="/', f'href="{PREFIX}/').replace('src="/', f'src="{PREFIX}/')
    fp = os.path.join(OUT, path); os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(doc)
    SITEMAP.append(canon)

def vcard(v, big=False):
    return f"""<a class="vc{' big' if big else ''}{' sh' if v['type']=='S' else ''}" href="{vurl(v)}" target="_blank" rel="noopener" data-yt="{v['id']}">
<span class="th"><img loading="lazy" src="https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg" alt="{E(vshort(v['title']))}"><i class="play"></i>{'<em>쇼츠</em>' if v['type']=='S' else '<em>라이브</em>' if v['type']=='V' else ''}</span>
<b>{E(v['title'])}</b><small>조회 {views(v['n'])}</small></a>"""

def vsplit(vs, hl="h2", nl=None, ns=None):
    """일반 영상(라이브 포함)과 쇼츠를 나눠서 표시"""
    L = [v for v in vs if v["type"] != "S"][:nl]; S = [v for v in vs if v["type"] == "S"][:ns]
    out = ""
    if L: out += f'<{hl} class="vh">▶ 영상 <small class="muted">{len(L)}편</small></{hl}><div class="vg">{"".join(vcard(v) for v in L)}</div>'
    if S: out += f'<{hl} class="vh">⚡ 쇼츠 <small class="muted">{len(S)}편</small></{hl}><div class="sg">{"".join(vcard(v) for v in S)}</div>'
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

BIZ = {"@context": "https://schema.org", "@type": "HardwareStore", "name": "월드건축자재(영진종합목재)",
       "telephone": "+82-42-545-2900", "address": {"@type": "PostalAddress", "streetAddress": "유성대로 44, 1층", "addressLocality": "대전", "addressCountry": "KR"},
       "openingHours": "Mo-Sa 08:00-18:00", "url": BASE + "/", "sameAs": [YT, YT2, BLOG, MALL], "alternateName": ["영진종합목재", "월드건축자재", "영진목재"],
       "image": "https://i.ytimg.com/vi/xPsUVr7exLU/hqdefault.jpg", "priceRange": "₩", "areaServed": ["대전", "세종"]}

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
    newv = [byid[i] for i in LATEST if i in byid][:4]
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
<div class="row"><a class="b r" href="/visit.html">매장 길찾기</a><a class="b o" href="/price.html">기준가 보기</a><a class="b d" href="/dome.html">업체·도매회원</a></div></div>
<div>{embed(tour) if tour else ''}<p class="small muted">대전 목재소·건축자재 백화점 3000평 투어 · 조회 18만회</p></div></div></section>
<section class="stat"><div class="wrap g4"><div><b>구독 {ST["subs"]}명</b><small>유튜브 월드건축자재DIY</small></div><div><b>영상 {int(ST["videos"]):,}개</b><small>시공·DIY·자재 정보</small></div>
<div><b>소매 + 도매</b><small>셀프 고객부터 현장 납품까지</small></div><div><b>직접 시공</b><small>월드아키텍쳐 · {LIC}</small></div></div></section>
<section class="wrap sec"><h2>무엇을 만들고 싶으세요?</h2><p class="muted">고르면 그 용도의 자재와 시공 영상이 한 번에 나옵니다.</p><div class="ug">{use}</div></section>
<section class="wrap sec"><h2>자재 백과 — 이 나무, 어디에 쓰나요?</h2><p class="muted">용도·인테리어 효과·기준가·관련 영상을 자재별로 정리했습니다.</p><div class="mg">{mats}</div></section>
{postsec}{newsec}
<section class="wrap sec"><h2>많이 본 영상</h2>{hot}<p><a href="{YT}" target="_blank" rel="noopener">유튜브 채널 전체 보기 →</a></p></section>
<section class="wrap sec g2"><div class="card"><h2>기본 자재 기준가</h2><p class="muted small">부가세 별도 · 규격·수량에 따라 달라집니다</p>
<div class="tw"><table><thead><tr><th>자재</th><th>규격</th><th class=r>기준가</th></tr></thead><tbody>{bt}</tbody></table></div>
<p class="small">재단비·운임·수량 할인은 매장에서 계산 · 고재·수입목·특수목은 매장 문의 · 도매가는 회원 로그인 후</p><a href="/price.html">기준가 전체 보기 →</a></div>
<div class="card dark"><h2>직접 하기 어렵다면, 시공까지</h2><p>자재를 가장 잘 아는 목재상이 직접 시공합니다. 월드아키텍쳐({LIC})가 대전·세종 전 공종을 시공하고, 모든 현장은 유튜브에 공개합니다.</p>
<a class="b r" href="/sigong.html">시공 사례 보기</a></div></section>{CTA}"""
    page("index.html", "대전 목재소·건축자재 월드건축자재(영진목재) | 합판·방부목·데크·재단", "대전 3000평 목재·건축자재 매장. 합판·OSB·MDF·구조재·방부목·데크 기준가와 사용법 영상, 즉석 재단, 대전·세종 시공(월드아키텍쳐).", body, "", BIZ)

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
         f'<section class="wrap sec"><h1>자재 백과</h1><p class="lead">손님들이 가장 헷갈리는 "이 자재 어디에 쓰나요?"를 자재별로 정리했습니다.</p><div class="mg">{lst}</div></section>{CTA}', "/jajae/")
    for m in MATS:
        vs = top(lambda v: m["tag"] in v["mats"], 10**6)
        rel = [x for x in MATS if x is not m][:0]
        where = "".join(f"<li>{E(w)}</li>" for w in m["where"])
        tips = "".join(f"<li>{E(t)}</li>" for t in m["tips"])
        lf = [v for v in vs if v["type"] != "S"]
        vid = ((embed(lf[0]) if lf else "") + vsplit([v for v in vs if not lf or v is not lf[0]], "h3")) if vs else f'<p><a href="{YT}">유튜브 채널에서 보기</a></p>'
        faq = [{"@type": "Question", "name": f"{m['name']}은(는) 어디에 쓰나요?", "acceptedAnswer": {"@type": "Answer", "text": ", ".join(m["where"])}},
               {"@type": "Question", "name": f"대전에서 {m['name']}을(를) 어디서 사나요?", "acceptedAnswer": {"@type": "Answer", "text": f"월드건축자재(영진종합목재), {ADDR}, {TEL}. {HOURS}. 원하는 사이즈로 재단해 드립니다."}}]
        ph = mat_photos(m["slug"])
        gal = (f'<section class="wrap sec"><h2>{m["name"]} 사진으로 보기 <small class="muted">매장 취급 {len(ph)}종</small></h2><div class="pg">{"".join(pcard(p) for p in ph[:12])}</div>'
               + (f'<p class="small muted">사진을 누르면 상세 사진이 열립니다 · 전체 {len(ph)}종 중 {min(12,len(ph))}종 표시 · <a href="/jaryo/">전체 자재 보기 →</a></p>' if ph else '') + '</section>') if ph else ""
        body = f"""<section class="wrap sec"><p class="crumb"><a href="/jajae/">자재 백과</a> › {m['name']}</p>
<h1>{m['name']} — {m['kw']}</h1><p class="lead">{E(m['lead'])}</p>
<div class="row"><span class="chip">사용 장소: {E(m['place'])}</span><span class="chip">셀프 난이도: {E(m['diy'])}</span></div></section>{gal}
<section class="wrap sec g2"><div class="card"><h2>어디에 쓰나요?</h2><ul>{where}</ul><h3>인테리어 효과</h3><p>{E(m['effect'])}</p><h3>고를 때 알아둘 것</h3><ul>{tips}</ul></div>
<div class="card"><h2>{m['name']} 소매 기준가</h2>{ptable(mat_prices(m))}<a href="/price.html">전체 기준가 →</a></div></section>
<section class="wrap sec"><h2>{m['name']} 시공·사용 영상</h2>{vid}</section>{CTA}"""
        page(f"jajae/{m['slug']}.html", f"{m['kw']} — {m['name']} 용도·기준가 | 대전 월드건축자재",
             f"{m['name']} 용도와 인테리어 효과, 규격별 소매 기준가, 시공 영상. 대전 유성 월드건축자재 매장에서 즉석 재단.", body, "/jajae/",
             {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq},
             (ph[0]["img"] if ph else (f"https://i.ytimg.com/vi/{vs[0]['id']}/hqdefault.jpg" if vs else None)))

    # 전체 자재 (쇼핑몰 자재 사진 목록)
    cnt = {c: sum(1 for p in PROD if c in p["tops"]) for c, *_ in JCAT}
    thumb = {c: next((p["img"] for p in PROD if c in p["tops"]), "") for c, *_ in JCAT}
    jl = "".join(f'<a class="pd" href="/jaryo/{sl}.html"><span class="pi"><img loading="lazy" src="{E(thumb[c])}" alt="{n}"></span><b>{n}</b><small>{d} · {cnt[c]}종</small></a>' for c, sl, n, d in JCAT if cnt[c])
    page("jaryo/index.html", f"전체 자재 사진 {len([p for p in PROD if p['tops']])}종 — 목재·합판·데크·사이딩·철물 | 대전 월드건축자재", "대전 월드건축자재(영진목재) 매장 취급 자재를 사진으로 확인하세요. 각재, 합판, 집성판, 데크, 마루, 내장재, 타일, 사이딩, 철물, 스테인.",
         f'<section class="wrap sec"><h1>전체 자재</h1><p class="lead">매장에서 취급하는 자재를 사진으로 모았습니다. 실물은 대전 매장에서 보고, 원하는 사이즈로 재단해 가세요. 가격은 <a href="/price.html">기준가</a> 또는 매장에서 안내합니다.</p><div class="pg">{jl}</div></section>{CTA}', "/jaryo/", None, thumb.get("24"))
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
            secs += f'<h2 id="s{(sb or "x").split("/")[-1] or "x"}">{E(title)} <small class="muted">{len(g)}종</small></h2><div class="pg">{"".join(pcard(p) for p in g)}</div>'
        toc = " · ".join(f'<a href="#s{(sb or "x").split("/")[-1] or "x"}">{E(MCAT.get(sb or "", "") or "기타")}</a>' for sb in subs)
        page(f"jaryo/{sl}.html", f"{n} 종류 사진 {len(ps)}종 — {d} | 대전 월드건축자재", f"{n} 종류를 사진으로 확인하세요: {d}. 대전 유성 월드건축자재(영진목재) 매장 취급, 즉석 재단.",
             f'<section class="wrap sec"><p class="crumb"><a href="/jaryo/">전체 자재</a> › {n}</p><h1>{n} <small class="muted">{len(ps)}종</small></h1><p class="lead">{d}. 사진을 누르면 상세 사진이 열립니다. 실물 확인·재단은 대전 매장에서 합니다.</p><p class="small">{toc}</p>{secs}</section>{CTA}', "/jaryo/",
             {"@context": "https://schema.org", "@type": "ItemList", "name": f"{n} 종류", "numberOfItems": len(ps),
              "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": p["name"], "image": p["img"]} for i, p in enumerate(ps[:100])]}, ps[0]["img"])

    # 영상
    vl = "".join(f'<a class="uc" href="/video/{c}.html"><b>{n}</b><small>{d} · {sum(1 for v in V if v["cat"]==c)}편</small></a>' for c, n, d in CATS)
    page("video/index.html", "시공·DIY 영상 모음 — 데크·온실·가구·외벽·인테리어 | 월드건축자재DIY", "월드건축자재DIY 유튜브 영상을 용도별로 정리했습니다. 데크, 목조 온실, 원목가구, 싱크대, 외벽, 바닥, 전기.",
         f'<section class="wrap sec"><h1>영상으로 찾기</h1><p class="lead">유튜브 「월드건축자재DIY」·「월드도어」 공개 영상 {len(V)}편(일반·쇼츠·라이브)을 용도별로 모두 모았습니다. 새 영상은 자동으로 추가됩니다.</p><div class="ug">{vl}</div><p><a href="{YT}">유튜브 채널 바로가기 →</a></p></section>{CTA}', "/video/")
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
    row = lambda p: f"<tr><td>{E(clean_name(p['name']))} {badge(p)}</td><td class=r><b>{won(p['price'])}</b></td>{chg(p)}</tr>"
    th = '<thead><tr><th>품목·규격</th><th class=r>소매 기준가</th><th class=r>지난 갱신 대비</th></tr></thead>'
    secs = "".join(f'<h2 id="{E(k)}">{E(k)}</h2><div class="tw"><table>{th}<tbody>' + "".join(row(p) for p in g[:25]) + "</tbody></table></div>"
                   for k, g in sorted(groups.items()) if k not in skip)
    top10 = sorted(P, key=lambda p: -p["qty"])[:10]
    upn = sum(1 for p in P if PREV.get(p["name"]) and PREV[p["name"]] < p["price"]); dnn = sum(1 for p in P if PREV.get(p["name"]) and PREV[p["name"]] > p["price"])
    board = (f'<div class="card pb2"><h2>많이 찾는 자재 TOP 10</h2><p class="small muted">매장 판매 순위 기준 · 기준가 갱신일 {E(PMETA.get("updated",""))} · '
             f'지난 갱신 대비 <span class="up">▲ 오른 품목 {upn}</span> · <span class="dn">▼ 내린 품목 {dnn}</span></p><div class="tw"><table>{th}<tbody>'
             + "".join(f"<tr><td><b>{i+1}</b> {E(clean_name(p['name']))}</td><td class=r><b>{won(p['price'])}</b></td>{chg(p)}</tr>" for i, p in enumerate(top10)) + "</tbody></table></div></div>")
    secs = board + secs
    page("price.html", "목재·건축자재 소매 기준가 — 합판·MDF·구조재·방부목·석고보드 | 대전 월드건축자재", "대전 월드건축자재(영진목재) 소매 기준가. 부가세 별도, 결제·재단은 매장에서.",
         f'<section class="wrap sec"><h1>소매 기준가</h1><p class="lead">자주 찾는 자재의 소매 기준가입니다(부가세 별도). 규격·수량에 따라 달라지며 재단비·운임은 매장에서 계산합니다. 도매가는 <a href="/dome.html">도매회원</a> 로그인 후 확인하세요.</p>{secs}</section>{CTA}', "/price.html")

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
    casesec = f'<section class="wrap sec"><h2>시공 사례 사진 <small class="muted">{len(case)}건</small></h2><div class="pg">{"".join(pcard(p) for p in case)}</div></section>' if case else ""
    page("sigong.html", "대전·세종 인테리어 시공 — 외벽·샷시·데크·리모델링 | 월드아키텍쳐(실내건축공사업)", f"월드아키텍쳐 {LIC}. 대전·세종 외벽 사이딩, 샷시 교체, 데크, 실내 인테리어 시공. 관급·대기업 공사 수행. 전화 {TEL}.",
         f"""<section class="hero dark"><div class="wrap"><span class="chip red">월드아키텍쳐 · {LIC}</span><h1>직접 하기 어렵다면,<br>자재 파는 저희가 시공까지 합니다</h1>
<p class="lead">자재를 가장 잘 아는 목재상이 직접 시공합니다. 관급·대기업 공사를 수행하는 시공팀이 작업하고, 모든 시공 현장은 유튜브에 그대로 공개합니다.</p>
<div class="row"><a class="b r" href="tel:{TEL.replace('-','')}">시공 상담 전화 {TEL}</a></div><p class="small">시공 지역: 대전·세종 전 공종 · 관급·대기업·전국 공사는 전화 문의</p></div></section>
<section class="wrap sec"><h2>시공 현장 영상</h2>{sv}</section>{casesec}
<section class="wrap sec g2"><div class="card"><h2>상담 순서</h2><ol><li>전화 상담 {TEL}</li><li>현장 방문 · 실측</li><li>견적서</li><li>시공 (현장은 유튜브 공개)</li></ol></div>
<div class="card"><h2>업체 고르기 전에 꼭 보세요</h2><p>면허 확인, 하자 예방, 견적 보는 법 영상을 모았습니다. 월드아키텍쳐는 실내건축공사업 등록 업체입니다.</p><a href="/video/tips.html">업체 고르는 법 영상 모음 →</a></div></section>
<section class="wrap sec">{tips}</section>{CTA}""", "/sigong.html")

    # 매장
    page("visit.html", "대전 목재소 위치 — 월드건축자재(영진목재) 유성대로 44 | 영업시간·재단", f"월드건축자재(영진종합목재) {ADDR}. {HOURS}. 3000평 매장, 즉석 재단, 대전·세종 배송. {TEL}.",
         f"""<section class="wrap sec g2"><div>{embed(tour) if tour else ''}</div><div><h1>매장 오시는 길</h1>
<div class="tw"><table><tbody><tr><th>주소</th><td>{ADDR} 월드건축자재(영진목재)</td></tr><tr><th>영업</th><td>{HOURS}</td></tr><tr><th>전화</th><td><a href="tel:{TEL.replace('-','')}">{TEL}</a></td></tr>
<tr><th>재단</th><td>원하는 사이즈로 즉석 재단</td></tr><tr><th>배송</th><td>대전·세종 배송 · 현장 납품</td></tr><tr><th>도매</th><td>사업자등록증·명함 확인 후 도매회원 승인</td></tr><tr><th>시공</th><td>월드아키텍쳐 · 대전·세종 · 전화 상담</td></tr></tbody></table></div>
<div class="row"><a class="b g" href="https://map.naver.com/p/search/{ADDR.replace(' ','%20')}%20월드건축자재" target="_blank" rel="noopener">네이버 지도로 길찾기</a><a class="b d" href="tel:{TEL.replace('-','')}">전화</a></div></div></section>""", "/visit.html", BIZ)

    # robots, sitemap
    if PREVIEW: print(len(SITEMAP), "preview pages →", OUT); return
    open(f"{OUT}/robots.txt", "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
    today = datetime.date.today().isoformat()
    open(f"{OUT}/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        "".join(f"<url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in SITEMAP) + "</urlset>\n")
    print(len(SITEMAP), "pages →", OUT)

SITEMAP = []
build()
