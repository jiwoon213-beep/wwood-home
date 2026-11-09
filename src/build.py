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
NAV = [("/jajae/", "자재 백과"), ("/video/", "영상"), ("/price.html", "기준가"), ("/dome.html", "도매·납품"), ("/sigong.html", "시공"), ("/visit.html", "매장 안내")]

def page(path, title, desc, body, active="", jsonld=None):
    canon = BASE + ("/" + path if path != "index.html" else "/").replace("index.html", "")
    nav = "".join(f'<a href="{h}"{" class=on" if active==h else ""}>{t}</a>' for h, t in NAV)
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    doc = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canon}"><meta property="og:type" content="website"><meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canon}"><meta property="og:image" content="https://i.ytimg.com/vi/xPsUVr7exLU/hqdefault.jpg">
<link rel="stylesheet" href="/assets/style.css">{'<meta name="robots" content="noindex,nofollow">' if PREVIEW else ''}{ld}</head><body>
<div class="top"><div class="wrap row sb"><span>{HOURS} · {ADDR}</span><span><a href="/dome.html">업체·도매회원</a> <a href="/visit.html">매장 길찾기</a></span></div></div>
<header><div class="wrap row sb hd"><a class="logo" href="/"><b>월드건축자재</b><small>영진종합목재 · 충청권 최대규모 목재상</small></a>
<nav>{nav}</nav></div></header>
<main>{body}</main>
<footer><div class="wrap">월드건축자재 · 영진종합목재 | {ADDR} | {TEL} | {HOURS}<br>
시공: 월드아키텍쳐 | 대표 김지운 | 사업자등록번호 281-05-03197 | {LIC}<br>
유튜브 <a href="{YT}">@월드건축자재DIY</a> · 도매회원 쇼핑몰 <a href="{DOME}">wwood.kr</a> · 표시 가격은 부가세 별도 소매 기준가이며 결제·재단은 매장에서 합니다.</div></footer>
<div class="mbar"><a class="b g" href="/visit.html">매장 길찾기</a><a class="b d" href="tel:{TEL.replace('-','')}">전화</a></div>
<script src="/assets/site.js" defer></script></body></html>"""
    if PREFIX: doc = doc.replace('href="/', f'href="{PREFIX}/').replace('src="/', f'src="{PREFIX}/')
    fp = os.path.join(OUT, path); os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(doc)
    SITEMAP.append(canon)

def vcard(v, big=False):
    return f"""<a class="vc{' big' if big else ''}" href="{vurl(v)}" target="_blank" rel="noopener" data-yt="{v['id']}">
<span class="th"><img loading="lazy" src="https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg" alt="{E(vshort(v['title']))}"><i class="play"></i>{'<em>쇼츠</em>' if v['type']=='S' else ''}</span>
<b>{E(v['title'])}</b><small>조회 {views(v['n'])}</small></a>"""

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
       "openingHours": "Mo-Sa 08:00-18:00", "url": BASE + "/", "sameAs": [YT, MALL]}

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
    hot = "".join(vcard(v) for v in top(lambda v: v["id"] != "xPsUVr7exLU", 8))
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
<section class="stat"><div class="wrap g4"><div><b>구독 1.3만+</b><small>유튜브 월드건축자재DIY</small></div><div><b>영상 900+</b><small>시공·DIY·자재 정보</small></div>
<div><b>소매 + 도매</b><small>셀프 고객부터 현장 납품까지</small></div><div><b>직접 시공</b><small>월드아키텍쳐 · {LIC}</small></div></div></section>
<section class="wrap sec"><h2>무엇을 만들고 싶으세요?</h2><p class="muted">고르면 그 용도의 자재와 시공 영상이 한 번에 나옵니다.</p><div class="ug">{use}</div></section>
<section class="wrap sec"><h2>자재 백과 — 이 나무, 어디에 쓰나요?</h2><p class="muted">용도·인테리어 효과·기준가·관련 영상을 자재별로 정리했습니다.</p><div class="mg">{mats}</div></section>
<section class="wrap sec"><h2>많이 본 영상</h2><div class="vg">{hot}</div><p><a href="{YT}" target="_blank" rel="noopener">유튜브 채널 전체 보기 →</a></p></section>
<section class="wrap sec g2"><div class="card"><h2>기본 자재 기준가</h2><p class="muted small">부가세 별도 · 규격·수량에 따라 달라집니다</p>
<div class="tw"><table><thead><tr><th>자재</th><th>규격</th><th class=r>기준가</th></tr></thead><tbody>{bt}</tbody></table></div>
<p class="small">재단비·운임·수량 할인은 매장에서 계산 · 고재·수입목·특수목은 매장 문의 · 도매가는 회원 로그인 후</p><a href="/price.html">기준가 전체 보기 →</a></div>
<div class="card dark"><h2>직접 하기 어렵다면, 시공까지</h2><p>자재를 가장 잘 아는 목재상이 직접 시공합니다. 월드아키텍쳐({LIC})가 대전·세종 전 공종을 시공하고, 모든 현장은 유튜브에 공개합니다.</p>
<a class="b r" href="/sigong.html">시공 사례 보기</a></div></section>{CTA}"""
    page("index.html", "대전 목재소·건축자재 월드건축자재(영진목재) | 합판·방부목·데크·재단", "대전 3000평 목재·건축자재 매장. 합판·OSB·MDF·구조재·방부목·데크 기준가와 사용법 영상, 즉석 재단, 대전·세종 시공(월드아키텍쳐).", body, "", BIZ)

    # 자재 백과
    lst = "".join(f'<a class="mc" href="/jajae/{m["slug"]}.html"><b>{m["name"]}</b><small>{" · ".join(m["where"][:2])}</small></a>' for m in MATS)
    page("jajae/index.html", "자재 백과 — 합판·MDF·방부목·석고보드 용도와 가격 | 월드건축자재 대전", "자재별 용도, 인테리어 효과, 소매 기준가, 시공 영상을 한 번에. 대전 월드건축자재(영진목재).",
         f'<section class="wrap sec"><h1>자재 백과</h1><p class="lead">손님들이 가장 헷갈리는 "이 자재 어디에 쓰나요?"를 자재별로 정리했습니다.</p><div class="mg">{lst}</div></section>{CTA}', "/jajae/")
    for m in MATS:
        vs = top(lambda v: m["tag"] in v["mats"], 9)
        rel = [x for x in MATS if x is not m][:0]
        where = "".join(f"<li>{E(w)}</li>" for w in m["where"])
        tips = "".join(f"<li>{E(t)}</li>" for t in m["tips"])
        vid = (embed(vs[0]) + '<div class="vg">' + "".join(vcard(v) for v in vs[1:]) + "</div>") if vs else f'<p><a href="{YT}">유튜브 채널에서 보기</a></p>'
        faq = [{"@type": "Question", "name": f"{m['name']}은(는) 어디에 쓰나요?", "acceptedAnswer": {"@type": "Answer", "text": ", ".join(m["where"])}},
               {"@type": "Question", "name": f"대전에서 {m['name']}을(를) 어디서 사나요?", "acceptedAnswer": {"@type": "Answer", "text": f"월드건축자재(영진종합목재), {ADDR}, {TEL}. {HOURS}. 원하는 사이즈로 재단해 드립니다."}}]
        body = f"""<section class="wrap sec"><p class="crumb"><a href="/jajae/">자재 백과</a> › {m['name']}</p>
<h1>{m['name']} — {m['kw']}</h1><p class="lead">{E(m['lead'])}</p>
<div class="row"><span class="chip">사용 장소: {E(m['place'])}</span><span class="chip">셀프 난이도: {E(m['diy'])}</span></div></section>
<section class="wrap sec g2"><div class="card"><h2>어디에 쓰나요?</h2><ul>{where}</ul><h3>인테리어 효과</h3><p>{E(m['effect'])}</p><h3>고를 때 알아둘 것</h3><ul>{tips}</ul></div>
<div class="card"><h2>{m['name']} 소매 기준가</h2>{ptable(mat_prices(m))}<a href="/price.html">전체 기준가 →</a></div></section>
<section class="wrap sec"><h2>{m['name']} 시공·사용 영상</h2>{vid}</section>{CTA}"""
        page(f"jajae/{m['slug']}.html", f"{m['kw']} — {m['name']} 용도·기준가 | 대전 월드건축자재",
             f"{m['name']} 용도와 인테리어 효과, 규격별 소매 기준가, 시공 영상. 대전 유성 월드건축자재 매장에서 즉석 재단.", body, "/jajae/",
             {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq})

    # 영상
    vl = "".join(f'<a class="uc" href="/video/{c}.html"><b>{n}</b><small>{d} · {sum(1 for v in V if v["cat"]==c)}편</small></a>' for c, n, d in CATS)
    page("video/index.html", "시공·DIY 영상 모음 — 데크·온실·가구·외벽·인테리어 | 월드건축자재DIY", "월드건축자재DIY 유튜브 영상을 용도별로 정리했습니다. 데크, 목조 온실, 원목가구, 싱크대, 외벽, 바닥, 전기.",
         f'<section class="wrap sec"><h1>영상으로 찾기</h1><p class="lead">유튜브 「월드건축자재DIY」 영상을 용도별로 모았습니다. 새 영상은 계속 추가됩니다.</p><div class="ug">{vl}</div><p><a href="{YT}">유튜브 채널 바로가기 →</a></p></section>{CTA}', "/video/")
    for c, n, d in CATS:
        vs = top(lambda v: v["cat"] == c, 40)
        page(f"video/{c}.html", f"{n} 영상 — {d} | 월드건축자재DIY 대전", f"{n} 관련 시공·DIY 영상 모음({d}). 영상에 나온 자재는 대전 월드건축자재 매장에서.",
             f'<section class="wrap sec"><p class="crumb"><a href="/video/">영상</a> › {n}</p><h1>{n}</h1><p class="lead">{d}</p><div class="vg">{"".join(vcard(v) for v in vs)}</div><p><a href="{YT}">더 많은 영상은 유튜브에서 →</a></p></section>{CTA}', "/video/")

    # 기준가
    groups = {}
    for p in sorted(P, key=lambda p: -p["qty"]):
        groups.setdefault(p["cat"], []).append(p)
    skip = {"-호차 영림", "문", "문틀", "가공"}
    secs = "".join(f'<h2 id="{E(k)}">{E(k)}</h2><div class="tw"><table><tbody>' + "".join(f"<tr><td>{E(clean_name(p['name']))}</td><td class=r><b>{won(p['price'])}</b></td></tr>" for p in g[:25]) + "</tbody></table></div>"
                   for k, g in sorted(groups.items()) if k not in skip)
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
    sv = "".join(vcard(v) for v in top(lambda v: v["cat"] in ("exterior", "greenhouse", "deck") and v["n"] > 3000, 12))
    tips = "".join(vcard(v) for v in top(lambda v: v["cat"] == "tips", 8))
    page("sigong.html", "대전·세종 인테리어 시공 — 외벽·샷시·데크·리모델링 | 월드아키텍쳐(실내건축공사업)", f"월드아키텍쳐 {LIC}. 대전·세종 외벽 사이딩, 샷시 교체, 데크, 실내 인테리어 시공. 관급·대기업 공사 수행. 전화 {TEL}.",
         f"""<section class="hero dark"><div class="wrap"><span class="chip red">월드아키텍쳐 · {LIC}</span><h1>직접 하기 어렵다면,<br>자재 파는 저희가 시공까지 합니다</h1>
<p class="lead">자재를 가장 잘 아는 목재상이 직접 시공합니다. 관급·대기업 공사를 수행하는 시공팀이 작업하고, 모든 시공 현장은 유튜브에 그대로 공개합니다.</p>
<div class="row"><a class="b r" href="tel:{TEL.replace('-','')}">시공 상담 전화 {TEL}</a></div><p class="small">시공 지역: 대전·세종 전 공종 · 관급·대기업·전국 공사는 전화 문의</p></div></section>
<section class="wrap sec"><h2>시공 현장 영상</h2><div class="vg">{sv}</div></section>
<section class="wrap sec g2"><div class="card"><h2>상담 순서</h2><ol><li>전화 상담 {TEL}</li><li>현장 방문 · 실측</li><li>견적서</li><li>시공 (현장은 유튜브 공개)</li></ol></div>
<div class="card"><h2>업체 고르기 전에 꼭 보세요</h2><p>면허 확인, 하자 예방, 견적 보는 법 영상을 모았습니다. 월드아키텍쳐는 실내건축공사업 등록 업체입니다.</p><a href="/video/tips.html">업체 고르는 법 영상 모음 →</a></div></section>
<section class="wrap sec"><div class="vg">{tips}</div></section>{CTA}""", "/sigong.html")

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
