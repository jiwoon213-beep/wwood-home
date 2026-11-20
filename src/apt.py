# 아파트 단지별 인테리어 자재 안내 (/apt/) — K-apt 공개 단지 기본정보(대전·세종)
# 동(읍면동)마다 한 페이지: 단지별 준공연도·세대수·복도유형·난방 + 연식에 맞는 자재 안내.
# 단지 이름은 공개 정보 그대로. 시공비·가격 숫자 없음.
import os, re, csv
import aptplan as AP
from urllib.parse import quote

YEAR = 2026
# 월드아키텍쳐 실제 시공 현장 (data/cases.json 의 시공 사례와 단지 연결) — 단지코드: (사례 slug, 한 일, 영상 순번)
CASEMAP = {"A30272404": ("door-daejeon-seogu", "노후 방문 교체", 0), "A30515002": ("door-daejeon-yuseong", "문 교체", 0),
           "A30581204": ("door-daejeon-yuseong", "문 교체", 1), "A30009002": ("door-daejeon-donggu-junggu", "문 교체", 1),
           "A30175801": ("door-daejeon-donggu-junggu", "문 교체", 2), "A33983501": ("door-sejong", "문 1세트 교체(욕실문 ABS 도어·문틀 필름)", 0)}
# 단지가 특정되지 않은 동 단위 현장
DONGCASE = {("대전", "서구", "복수동"): ("door-daejeon-seogu", "복수동 초록마을 중문·방문 교체", 1)}


def load(root):
    p = f"{root}/data/apt.tsv"
    if not os.path.exists(p): return []
    rows = list(csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"))
    for r in rows:
        try: r["n"] = int(r["세대수"])
        except Exception: r["n"] = 0
        y = r.get("사용승인일", "")[:4]
        r["y"] = int(y) if y.isdigit() else 0
        if r["시도"] == "전남" and r["시군구"].endswith("구"): r["시도"] = "광주"  # K-apt 표기 보정
    A = {}
    pa = f"{root}/data/apt_area.tsv"
    if os.path.exists(pa):
        for l in open(pa, encoding="utf-8"):
            k, _, v = l.rstrip("\n").partition("\t")
            A[k] = [(int(a), int(n)) for a, n in (x.split(":") for x in v.split(",") if ":" in x)]
    for r in rows: r["ar"] = A.get(r["단지코드"], [])
    return [r for r in rows if r["n"] >= 100 and r["단지명"].strip()]


def slug(s):
    return re.sub(r"[^0-9a-zA-Z가-힣]", "", s)


SDS = {"서울": "seoul", "부산": "busan", "대구": "daegu", "인천": "incheon", "광주": "gwangju", "대전": "daejeon", "울산": "ulsan", "세종": "sejong", "경기": "gyeonggi", "강원": "gangwon", "충북": "chungbuk", "충남": "chungnam", "전북": "jeonbuk", "전남": "jeonnam", "경북": "gyeongbuk", "경남": "gyeongnam", "제주": "jeju"}
SDO = list(SDS)
NEAR = ("대전", "세종", "충남", "충북")
GN = re.compile(r"고양|파주|김포|의정부|남양주|양주|동두천|포천|연천|가평|구리")


def reg(sd, gu):
    if sd == "경기": return "gyeonggi-north" if GN.search(gu) else "gyeonggi-south"
    return {"서울": "seoul", "인천": "incheon", "강원": "gangwon", "충북": "chungbuk", "충남": "chungnam", "전북": "jeonbuk", "광주": "gwangju-jeonnam", "전남": "gwangju-jeonnam",
            "대구": "daegu-gyeongbuk", "경북": "daegu-gyeongbuk", "부산": "busan-gyeongnam", "울산": "busan-gyeongnam", "경남": "busan-gyeongnam", "제주": "jeju"}.get(sd)


def fname(sd, gu, dong):
    g = slug(gu) if gu and gu != sd and not gu.startswith("세종") else ""
    return f"apt/{SDS.get(sd, 'etc')}/{(g + '-') if g else ''}{slug(dong)}.html"


def areaname(sd, gu, dong):
    return " ".join(x for x in [sd, gu if gu and not gu.startswith("세종") else "", dong] if x)


def age_tips(y):
    a = YEAR - y if y else 0
    if not y: return []
    if a >= 25: return [("방문·문틀 교체", "/sigongbeop/munteul-gyoche.html"), ("창틀 결로·외풍", "/qna/chang-gyeolro.html"), ("바닥 덧방(합판·데코타일)", "/sigongbeop/hapan-badak-deotbang.html"), ("욕실 타일", "/sigongbeop/yoksil-tile.html")]
    if a >= 15: return [("방문 교체·필름", "/sigongbeop/munteul-gyoche.html"), ("현관 중문", "/sigongbeop/jungmun.html"), ("몰딩·걸레받이", "/sigongbeop/molding-georebatgi.html"), ("강마루·데코타일", "/sigongbeop/gangmaru.html")]
    if a >= 7: return [("인테리어 필름", "/sigongbeop/film-sigong.html"), ("현관 중문", "/sigongbeop/jungmun.html"), ("템바보드 아트월", "/sigongbeop/tempa-byeok.html"), ("붙박이·수납 만들기", "/mandeul/chaekjang.html")]
    return [("현관 중문", "/sigongbeop/jungmun.html"), ("템바보드 아트월", "/sigongbeop/tempa-byeok.html"), ("베란다 선반", "/mandeul/beranda.html"), ("거실장·수납", "/mandeul/geosiljang.html")]


def age_text(y):
    if not y: return ""
    a = YEAR - y
    if a >= 25: return f"{y}년 사용승인(약 {a}년 차) — 문틀·방문, 창틀 주변 결로, 바닥 들뜸을 손보는 집이 많은 연식입니다."
    if a >= 15: return f"{y}년 사용승인(약 {a}년 차) — 방문·몰딩 색을 바꾸거나 중문을 새로 다는 경우가 많은 연식입니다."
    if a >= 7: return f"{y}년 사용승인(약 {a}년 차) — 필름으로 문·가구 색을 바꾸거나 중문·아트월을 더하는 경우가 많습니다."
    return f"{y}년 사용승인(약 {max(a,0)}년 차) — 입주 때 중문·아트월·수납을 더하는 경우가 많습니다."


def _cases(root):
    import json
    p = f"{root}/data/cases.json"
    return {c["slug"]: c for c in json.load(open(p, encoding="utf-8"))} if os.path.exists(p) else {}


def casecard(C, slug, work, vi, E, place=""):
    c = C.get(slug)
    if not c: return ""
    v = c.get("videos") or []
    img = f'<img loading="lazy" src="https://i.ytimg.com/vi/{v[min(vi, len(v) - 1)]}/mqdefault.jpg" alt="" width="320" height="180">' if v else ""
    return f'<a class="apcase" href="/sigong/{slug}.html">{img}<span><small>월드아키텍쳐 실제 시공 현장</small><b>{E((place + " " if place else "") + work)}</b><em>시공 사례·영상 보기 ›</em></span></a>'


LOCSVC = [("jungmun", "중문 설치"), ("door", "방문·문틀 교체"), ("film", "필름 시공"), ("molding", "몰딩 교체"), ("wall", "템바보드 벽")]


def locreg(sd, gu):
    if sd == "대전": return {"유성구": "yuseong", "서구": "seogu", "대덕구": "daedeok", "중구": "junggu-donggu", "동구": "junggu-donggu"}.get(gu)
    if sd == "세종": return "sejong"
    for k, v in (("공주", "gongju"), ("계룡", "gyeryong"), ("금산", "geumsan"), ("옥천", "okcheon"), ("천안", "cheonan"), ("청주", "cheongju")):
        if gu.startswith(k): return v
    return None


def ok(L):
    return len(L) >= 2 or sum(r["n"] for r in L) >= 300


def _dongstat(L, area, E, plan_link):
    """동마다 다른 통계·FAQ (K-apt 공개 정보에서 계산한 숫자만)."""
    import json as _j
    ys = [r["y"] for r in L if r["y"]]
    dec = {}
    for y in ys:
        k = "1990년 이전" if y < 1990 else f"{y // 10 * 10}년대"
        dec[k] = dec.get(k, 0) + 1
    ar = {"60㎡ 미만(소형)": 0, "60~85㎡(중형)": 0, "85㎡ 초과(대형)": 0}; at = {}
    for r in L:
        for a, n in r["ar"]:
            ar["60㎡ 미만(소형)" if a < 60 else ("60~85㎡(중형)" if a <= 85 else "85㎡ 초과(대형)")] += n
            at[a] = at.get(a, 0) + n
    ast = sum(ar.values())
    def cnt(key):
        d = {}
        for r in L:
            v = (r.get(key) or "").strip()
            if v: d[v] = d.get(v, 0) + 1
        return sorted(d.items(), key=lambda x: -x[1])
    heat = cnt("난방방식"); hall = cnt("복도유형")
    import re as _re
    _b = {}
    for r in L:
        v = _re.sub(r"\(.*?\)|㈜|주식회사|\(주\)", "", (r.get("시공사") or "")).split(",")[0].strip()
        v = _re.sub(r"\s+", "", v)
        if v and v not in ("-", "기타", "미상"): _b[v] = _b.get(v, 0) + 1
    bld = sorted(_b.items(), key=lambda x: -x[1])
    fl = [int(r["최고층수"]) for r in L if str(r.get("최고층수", "")).isdigit() and int(r["최고층수"]) > 0]
    rows = []
    if dec: rows.append(("준공 시기", ", ".join(f"{k} {v}곳" for k, v in sorted(dec.items()))))
    if ast: rows.append(("평형(세대 기준)", ", ".join(f"{k} {round(v * 100 / ast)}%" for k, v in ar.items() if v)))
    if heat: rows.append(("난방", ", ".join(f"{k} {v}곳" for k, v in heat[:3])))
    if hall: rows.append(("복도 구조", ", ".join(f"{k} {v}곳" for k, v in hall[:3])))
    if fl: rows.append(("최고 층수", f"{min(fl)}층 ~ {max(fl)}층"))
    if bld: rows.append(("많이 지은 건설사", ", ".join(f"{k}({v})" for k, v in bld[:3])))
    tb = "".join(f"<tr><th>{E(a)}</th><td>{E(b)}</td></tr>" for a, b in rows)
    pt = ""
    if at:
        top = max(at.items(), key=lambda x: x[1])
        pt = (f'<p>이 동네에서 가장 흔한 집은 <b>전용 {top[0]}㎡</b>({top[1]:,}세대)입니다. '
              f'<a href="{plan_link(top[0])}">{top[0]}㎡ 평면 예시와 자리별 자재</a>를 먼저 보세요.</p>')
    tip = []
    if ys:
        o = sum(1 for y in ys if YEAR - y >= 25); n = sum(1 for y in ys if YEAR - y <= 10)
        if o * 2 >= len(ys): tip.append("25년 넘은 단지가 절반 이상이라 방문·문틀 교체, 몰딩·걸레받이 교체, 샷시 주변 단열·결로 보수를 많이 합니다")
        elif n * 2 >= len(ys): tip.append("10년 안쪽 새 단지가 많아 큰 공사보다 중문 추가, 아트월(템바보드), 베란다 선반·수납 같은 꾸밈 공사가 많습니다")
        else: tip.append("연식이 섞여 있어 단지마다 필요한 공사가 다릅니다. 아래 단지별 안내를 보세요")
    if hall and any("복도" in k for k, _ in hall[:1]): tip.append("복도식 단지가 많아 현관 쪽 외풍을 막는 중문·현관문 패킹 수요가 큽니다")
    if heat and any("중앙" in k or "지역" in k for k, _ in heat[:1]): tip.append("중앙·지역난방 단지가 많아 바닥을 뜯는 공사는 관리사무소 확인이 먼저입니다")
    tips = "".join(f"<li>{E(t)}</li>" for t in tip)
    # FAQ (데이터로 답이 정해지는 질문만)
    Ly = [r for r in L if r["y"]]
    fq = []
    if Ly:
        ol = min(Ly, key=lambda r: r["y"]); nw = max(Ly, key=lambda r: r["y"])
        fq.append((f"{area}에서 가장 오래된 아파트는?", f'{ol["단지명"].strip()}({ol["y"]}년 사용승인, {ol["n"]:,}세대)입니다. {age_text(ol["y"])}'))
        if nw is not ol: fq.append((f"{area}에서 가장 최근에 지은 아파트는?", f'{nw["단지명"].strip()}({nw["y"]}년 사용승인, {nw["n"]:,}세대)입니다.'))
    big = max(L, key=lambda r: r["n"])
    fq.append((f"{area}에서 세대수가 가장 많은 아파트는?", f'{big["단지명"].strip()}({big["n"]:,}세대)입니다.'))
    fq.append((f"{area} 아파트 인테리어 자재는 어디서 사나요?", "영진종합목재(대전 유성구 유성대로 44)에서 중문·방문·몰딩·필름·합판·각재를 원하는 크기로 재단해 드리고, 전국 배송도 합니다. 전화 042-545-2900."))
    fh = "".join(f"<details class=\"faq\"><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in fq)
    ld = _j.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}, ensure_ascii=False).replace("</", "<\\/")
    return (f'<section class="wrap sec"><h2>{E(area)} 아파트 한눈에 보기</h2>'
            + (f'<table class="tbl"><tbody>{tb}</tbody></table>' if tb else '') + pt
            + (f'<ul>{tips}</ul>' if tips else '')
            + f'<h2>자주 묻는 질문</h2>{fh}<script type="application/ld+json">{ld}</script></section>')

def build(root, page, E, CTA):
    rows = load(root)
    if not rows: return []
    by = {}
    for r in rows:
        by.setdefault((r["시도"], r["시군구"], r["동리"]), []).append(r)
    C = _cases(root)
    bygu = {}
    for k, L in by.items():
        if ok(L): bygu.setdefault((k[0], k[1]), []).append(k)
    pages = []; SRCH = []
    for (sd, gu, dong), L in sorted(by.items()):
        if not ok(L): continue
        L.sort(key=lambda r: (r["단지코드"] not in CASEMAP, -r["n"]))
        tot = sum(r["n"] for r in L)
        fn = fname(sd, gu, dong); area = areaname(sd, gu, dong)
        ys = [r["y"] for r in L if r["y"]]
        avg = round(sum(YEAR - y for y in ys) / len(ys)) if ys else 0
        old = sum(1 for y in ys if YEAR - y >= 20)
        bok = sum(1 for r in L if "복도" in r.get("복도유형", ""))
        cards = ""
        for r in L[:40]:
            tips = "".join(f'<a href="{u}">{E(t)}</a>' for t, u in age_tips(r["y"]))
            meta = " · ".join(x for x in [f'{r["n"]:,}세대', f'{r["동수"]}개 동' if r.get("동수") not in ("", "0") else "", f'{r["y"]}년' if r["y"] else "", r.get("복도유형", ""), r.get("난방방식", "")] if x)
            pl = ""
            if r["ar"]:
                da = ",".join(f"{a}:{n}" for a, n in r["ar"])
                pl = (f'<div class="apfp" data-a="{da}" data-y="{r["y"] or ""}" data-h="{E(r.get("복도유형", ""))}" data-t="{E(r.get("단지분류", ""))}" data-f="{E(r.get("최고층수", ""))}" data-n="{E(r["단지명"].strip())}">'
                      + "".join(f'<a href="/apt/plan/{AP.ptype(a, r["y"])}.html">{a}㎡ {n:,}세대</a> ' for a, n in r["ar"]) + '</div>')
            if r["단지코드"] in CASEMAP:
                cs = CASEMAP[r["단지코드"]]; pl = casecard(C, cs[0], cs[1], cs[2], E) + pl
            nq = quote(f'{r["단지명"].strip()} {dong} 평면도')
            qty = ""
            if r["ar"]:
                import math as _m
                _q = []
                for a, n in sorted(r["ar"], key=lambda x: -x[1])[:3]:
                    try: af = float(a)
                    except Exception: continue
                    _q.append(f'{a}㎡(약 {af / 3.3058:.1f}평): 바닥 전체 덧방 시 합판 4×8 약 {_m.ceil(af / 2.98)}장·데코타일 약 {_m.ceil(af / 3.3058)}평 분량')
                if _q: qty = '<p class="small">바닥 자재 어림(전용면적 기준, 실제 바닥은 이보다 조금 적고 자를 여유분은 따로): ' + E(" / ".join(_q)) + ' <a href="/calc.html">계산기</a></p>'
            cards += (f'<article class="apc" id="{E(r["단지코드"])}"><h3>{E(r["단지명"].strip())}</h3><p class="small muted">{E(meta)}</p>'
                      f'<p>{E(age_text(r["y"]))}</p>{pl}{qty}<div class="apl">{tips}</div>'
                      f'<p class="small"><a class="apreal" href="https://search.naver.com/search.naver?query={nq}" target="_blank" rel="noopener nofollow">이 단지 실제 평면도 보기(네이버) ↗</a></p></article>')
        more = (f'<p class="small muted">그 밖에 {len(L) - 40}개 단지: ' + ", ".join(E(r["단지명"].strip()) for r in L[40:]) + "</p>") if len(L) > 40 else ""
        near = "".join(f'<a href="/{fname(*k)}">{E(k[2])}</a>' for k in sorted(bygu.get((sd, gu), [])) if k[2] != dong)
        stat = (f'평균 약 {avg}년 차' + (f', 20년 넘은 단지 {old}곳' if old else '') + (f', 복도식 {bok}곳' if bok else '')) if ys else ""
        if sd in NEAR:
            how = '자재는 대전 유성 매장에서 실물을 보고 원하는 크기로 잘라 가실 수 있고, 현장까지 배송도 됩니다.'
            _lr = locreg(sd, gu)
            if _lr: how += ' 이 지역은 <b>시공도</b> 합니다(실측 후 견적).'
            rl = '<a href="/visit.html">매장 길찾기</a><a href="/jaedan-baesong.html">재단 후 배송</a>'
            if _lr: rl += "".join(f'<a href="/local/{k}-{_lr}.html">{E(gu if sd != "세종" else "세종")} {t}</a>' for k, t in LOCSVC)
        else:
            rg = reg(sd, gu)
            how = f'{E(sd)} 현장은 치수대로 재단해서 <b>전국 배송</b>으로 보내 드립니다(운임은 견적). 중문·방문·몰딩은 문 크기를 재서 보내 주세요.'
            rl = (f'<a href="/jeonguk/{rg}.html">{E(sd)} 배송 안내</a>' if rg else '') + '<a href="/jaedan-baesong.html">재단 후 전국 배송</a>'
        _nm = [r["단지명"].strip() for r in L[:2]]
        title = f"{area} 아파트 {len(L)}곳 인테리어 자재 — " + "·".join(_nm) + (" 등" if len(L) > 2 else "") + " | 영진목재"
        desc = f"{area} 아파트 {len(L)}개 단지({tot:,}세대) 준공연도별 중문·방문 교체·몰딩·필름·바닥 자재 안내. " + ", ".join(r["단지명"].strip() for r in L[:3]) + " 등. 재단·전국 배송."
        body = (f'<section class="wrap sec"><p class="crumb"><a href="/apt/">아파트별 자재</a> › <a href="/apt/{SDS.get(sd, "etc")}/">{E(sd)}</a> › ' + (f'<a href="/apt/{SDS.get(sd, "etc")}/{slug(gu)}.html">{E(gu)}</a> › ' if gu and gu != sd and not gu.startswith("세종") and len(bygu.get((sd, gu), [])) >= 2 else '') + f'{E(dong)}</p><h1>{E(area)} 아파트 인테리어 자재</h1>'
                f'<p class="lead">{E(area)}에는 100세대 이상 아파트가 <b>{len(L)}개 단지, {tot:,}세대</b> 있습니다' + (f' (사용승인 {min(ys)}~{max(ys)}년, {stat})' if ys else '') + '. 단지 연식에 맞춰 많이 하는 공사와 자재를 모았습니다.</p>'
                f'<p>{how}</p><div class="olk">{rl}<a class="ac" href="/doumi.html">🧭 셀프 인테리어 도우미</a><a class="ac" href="/calc.html">🧮 문짝·중문 크기 계산</a></div>'
                + (('<h2>이 동네 실제 시공 현장</h2>' + casecard(C, *DONGCASE[(sd, gu, dong)][:3], E)) if (sd, gu, dong) in DONGCASE else '')
                + f'<div class="apg">{cards}</div>{more}'
                + '</section>' + _dongstat(L, area, E, lambda a: f"/apt/plan/{AP.ptype(a, max(ys) if ys else 2000)}.html") + '<section class="wrap sec">'
                '<p class="small muted">단지 정보: 국토교통부 공동주택관리정보시스템(K-apt) 공개 단지 기본정보, 매주 갱신. 실제와 다를 수 있습니다. 이 페이지는 해당 단지·관리사무소와 관계없는 자재 안내입니다.</p></section>'
                '<section class="wrap sec"><h2>아파트에서 많이 하는 것</h2><div class="olk"><a href="/sigongbeop/jungmun.html">원슬라이딩 중문 셀프 설치</a><a href="/sigongbeop/munteul-gyoche.html">방문 교체</a><a href="/sigongbeop/film-sigong.html">인테리어 필름</a><a href="/sigongbeop/molding-georebatgi.html">걸레받이·천장 몰딩</a><a href="/sigongbeop/tempa-byeok.html">템바보드 아트월</a><a href="/mandeul/beranda.html">베란다 선반</a></div><p class="hsh olh">옆으로 넘겨 보세요 ›</p></section>'
                + (f'<section class="wrap sec"><h2>{E(areaname(sd, gu, ""))} 다른 동</h2><div class="olk">{near}</div><p class="hsh olh">옆으로 넘겨 보세요 ›</p></section>' if near else "")
                + '<script src="/assets/apt/plan.js?v=4" defer></script>' + CTA)
        page(fn, title, desc[:155], body, "/apt/")
        pages.append((fn, sd, gu, dong, len(L), tot))
        for r in L: SRCH.append([r["단지명"].strip(), fn[4:-5], r["단지코드"][1:], r["n"]])
    import json
    RG = {}
    for p in pages:
        r_ = locreg(p[1], p[2])
        if r_: RG.setdefault(r_, []).append([p[0], p[3], p[4], p[5]])
        if r_ in ("yuseong", "seogu", "daedeok", "junggu-donggu"): RG.setdefault("daejeon", []).append([p[0], p[3], p[4], p[5]])
    RG = {k: sorted(v, key=lambda x: -x[3])[:24] for k, v in RG.items()}
    rp = f"{root}/data/apt_reg.json"; rj = json.dumps(RG, ensure_ascii=False, indent=0)
    if not os.path.exists(rp) or open(rp, encoding="utf-8").read() != rj: open(rp, "w", encoding="utf-8").write(rj)
    os.makedirs(f"{root}/assets/apt", exist_ok=True)
    js = json.dumps(SRCH, ensure_ascii=False, separators=(",", ":"))
    jp = f"{root}/assets/apt/search.json"
    if not os.path.exists(jp) or open(jp, encoding="utf-8").read() != js: open(jp, "w", encoding="utf-8").write(js)
    SBOX = ('<div class="apsrch"><input id="apq" type="search" placeholder="아파트 이름 또는 동 이름 (예: 래미안, 봉명동)" autocomplete="off" aria-label="아파트·동 검색"><div id="apr" class="apr"></div></div>'
            "<script>(function(){var q=document.getElementById('apq'),o=document.getElementById('apr'),D=null,ld=0;"
            "function load(){if(ld)return;ld=1;fetch('/assets/apt/search.json').then(function(r){return r.json()}).then(function(j){D=j;run()})}"
            "var SN={seoul:'서울',busan:'부산',daegu:'대구',incheon:'인천',gwangju:'광주',daejeon:'대전',ulsan:'울산',sejong:'세종',gyeonggi:'경기',gangwon:'강원',chungbuk:'충북',chungnam:'충남',jeonbuk:'전북',jeonnam:'전남',gyeongbuk:'경북',gyeongnam:'경남',jeju:'제주'};function ar(p){var q=p.split('/');return (SN[q[0]]||'')+' '+q[1].replace(/-/g,' ')}function nz(s){return s.replace(/\\s|아파트|APT/gi,'').toLowerCase()}"
            "function run(){var v=nz(q.value);if(!D||v.length<2){o.innerHTML='';return}var R=[];for(var i=0;i<D.length&&R.length<30;i++){var d=D[i];if(nz(d[0]).indexOf(v)>=0||nz(d[1]).indexOf(v)>=0)R.push(d)}"
            "R.sort(function(a,b){return b[3]-a[3]});o.innerHTML=R.length?R.map(function(d){return '<a href=\"/apt/'+d[1]+'.html#A'+d[2]+'\"><b>'+d[0].replace(/</g,'&lt;')+'</b><small>'+ar(d[1])+' · '+d[3].toLocaleString()+'세대</small></a>'}).join(''):'<p class=\"small muted\">찾는 단지가 없어요. 100세대 이상 단지만 있습니다.</p>'}"
            "q.addEventListener('focus',load);q.addEventListener('input',function(){load();run()});})();</script>")
    # 시도 페이지
    S = {}
    for p in pages: S.setdefault(p[1], {}).setdefault(p[2], []).append(p)
    # 시·군·구 페이지 (전국 지역 검색용) — 그 구의 동 목록·큰 단지·연식 통계
    GUP = {}
    _CP = ("수원", "성남", "안양", "부천", "고양", "용인", "안산", "청주", "천안", "전주", "포항", "창원", "화성")
    def _gname(gu):
        for c in _CP:
            if gu.startswith(c) and gu.endswith("구") and len(gu) > len(c) + 1: return f"{c}시 {gu[len(c):]}"
        return gu
    for sd in S:
        for gu, ps in S[sd].items():
            if not gu or gu == sd or gu.startswith("세종") or len(ps) < 2: continue
            fn = f"apt/{SDS.get(sd, 'etc')}/{slug(gu)}.html"
            Lall = [r for p in ps for r in by[(sd, gu, p[3])]]
            gn = _gname(gu); area = f"{sd} {gn}"
            nd = len(ps); nc = len(Lall); tot = sum(r["n"] for r in Lall)
            ys = [r["y"] for r in Lall if r["y"]]
            big = sorted(Lall, key=lambda r: -r["n"])[:15]
            dl = "".join(f'<a href="/{p[0]}">{E(p[3])}<small> {p[4]}단지</small></a>' for p in sorted(ps, key=lambda p: -p[5]))
            bl = "".join(f'<li><a href="/{fname(sd, gu, r["동리"])}#{E(r["단지코드"])}">{E(r["단지명"].strip())}</a> <span class="small muted">{E(r["동리"])} · {r["n"]:,}세대' + (f' · {r["y"]}년' if r["y"] else '') + '</span></li>' for r in big)
            if sd in NEAR:
                how = f'{E(gn)}은(는) 대전 유성 매장에서 가까워 실물을 보고 원하는 크기로 잘라 가실 수 있고, 현장 배송도 됩니다.'
                _lr = locreg(sd, gu)
                rl = '<a href="/visit.html">매장 길찾기</a><a href="/jaedan-baesong.html">재단 후 배송</a>' + ("".join(f'<a href="/local/{k}-{_lr}.html">{E(gn)} {t}</a>' for k, t in LOCSVC) if _lr else "")
            else:
                rg = reg(sd, gu)
                how = f'{E(area)} 현장은 대전 매장에서 치수대로 재단해 <b>전국 배송</b>으로 보내 드립니다(운임은 견적). 중문·방문·몰딩은 문 크기를 재서 보내 주세요.'
                rl = (f'<a href="/jeonguk/{rg}.html">{E(sd)} 배송 안내</a>' if rg else '') + '<a href="/jaedan-baesong.html">재단 후 전국 배송</a><a href="/cut.html">재단 미리보기</a>'
            title = f"{area} 아파트 인테리어 자재 — {nd}개 동 {nc}개 단지 연식별 안내 | 영진목재"
            desc = f"{area} 아파트 {nc}개 단지({tot:,}세대)를 동별로 모아 준공연도에 맞는 중문·방문 교체·몰딩·필름·바닥 자재를 안내합니다. " + ", ".join(r["단지명"].strip() for r in big[:3]) + " 등. 재단·전국 배송."
            body = (f'<section class="wrap sec"><p class="crumb"><a href="/apt/">아파트별 자재</a> › <a href="/apt/{SDS.get(sd, "etc")}/">{E(sd)}</a> › {E(gn)}</p><h1>{E(area)} 아파트 인테리어 자재</h1>'
                    f'<p class="lead">{E(area)}의 100세대 이상 아파트 <b>{nc}개 단지, {tot:,}세대</b>를 {nd}개 동으로 나눠 모았습니다' + (f' (사용승인 {min(ys)}~{max(ys)}년)' if ys else '') + '. 동을 고르면 단지마다 연식에 맞는 공사와 자재를 볼 수 있어요.</p>'
                    f'<p>{how}</p><div class="olk">{rl}<a class="ac" href="/doumi.html">🧭 셀프 인테리어 도우미</a></div>'
                    f'<h2>{E(gn)} 동별 아파트</h2><div class="olk aplk">{dl}</div><h2>{E(gn)} 큰 단지</h2><ul>{bl}</ul></section>'
                    + _dongstat(Lall, area, E, lambda a: f"/apt/plan/{AP.ptype(a, max(ys) if ys else 2000)}.html")
                    + '<section class="wrap sec"><p class="small muted">단지 정보: 국토교통부 공동주택관리정보시스템(K-apt) 공개 단지 기본정보. 실제와 다를 수 있습니다. 이 페이지는 해당 단지·관리사무소와 관계없는 자재 안내입니다.</p></section>' + CTA)
            page(fn, title, desc[:155], body, "/apt/")
            GUP[(sd, gu)] = fn
    idx = ""
    for sd in sorted(S, key=lambda x: SDO.index(x) if x in SDO else 99):
        G = S[sd]; nd = sum(len(v) for v in G.values()); nc = sum(p[4] for v in G.values() for p in v)
        sec = ""
        for gu in sorted(G):
            ps = sorted(G[gu], key=lambda p: -p[5])
            sec += ((f'<h2 class="ggh"><a href="/{GUP[(sd, gu)]}">{E(areaname(sd, gu, ""))}</a></h2>' if (sd, gu) in GUP else f'<h2 class="ggh">{E(areaname(sd, gu, ""))}</h2>') if gu and not gu.startswith("세종") else "") + '<div class="olk aplk">' + "".join(f'<a href="/{p[0]}">{E(p[3])}<small> {p[4]}단지</small></a>' for p in ps) + "</div>"
        page(f"apt/{SDS.get(sd, 'etc')}/index.html", f"{sd} 아파트별 인테리어 자재 — 동네 단지 연식에 맞춘 안내 | 영진목재",
             f"{sd} {nd}개 동, {nc}개 아파트 단지의 준공연도에 맞춘 중문·방문·몰딩·필름·바닥 자재 안내. 영진종합목재 재단·전국 배송.",
             f'<section class="wrap sec"><p class="crumb"><a href="/apt/">아파트별 자재</a> › {E(sd)}</p><h1>{E(sd)} 아파트별 인테리어 자재</h1><p class="lead">동네를 고르면 단지 연식에 맞춰 많이 하는 공사와 자재를 보여 드립니다. ({nd}개 동 · {nc:,}개 단지, K-apt 공개 정보)</p>{SBOX}{sec}</section>' + CTA, "/apt/")
        idx += f'<a href="/apt/{SDS.get(sd, "etc")}/"><b>{E(sd)}</b><small> {nd}개 동 · {nc:,}단지</small></a>'
    page("apt/index.html", "전국 아파트별 인테리어 자재 — 우리 단지 연식에 맞춘 안내 | 영진목재",
         f"전국 {len(pages):,}개 동, {sum(p[4] for p in pages):,}개 아파트 단지의 준공연도에 맞춘 중문·방문·몰딩·필름·바닥 자재 안내. 영진종합목재(대전) 재단·전국 배송.",
         f'<section class="wrap sec"><h1>전국 아파트별 인테리어 자재</h1><p class="lead">우리 동네 아파트를 고르면 단지 연식에 맞춰 많이 하는 공사와 자재를 보여 드립니다. (전국 100세대 이상, K-apt 공개 정보 · 매주 갱신)</p>{SBOX}<div class="olk aplk apsd">{idx}</div></section>' + CTA, "/apt/")
    AP.write(root)
    for k in AP.ORDER:
        t, d = AP.P[k][0], AP.P[k][1]
        oth = "".join(f'<a href="/apt/plan/{x}.html">{E(AP.P[x][0])}</a>' for x in AP.ORDER if x != k)
        page(f"apt/plan/{k}.html", f"아파트 {t} 평면도 예시 — 중문·방문·몰딩 위치 | 영진목재",
             f"아파트 {t} 예시 평면도에 현관 중문, 방문, 걸레받이·몰딩, 아트월, 주방 상부장, 베란다 선반 자리를 번호로 표시했습니다. 누르면 시공법·자재로 이동합니다.",
             f'<section class="wrap sec"><p class="crumb"><a href="/apt/">아파트별 자재</a> › 평면도 예시</p><h1>아파트 {E(t)} 평면도 예시</h1><p class="lead">{E(d)} 번호를 누르면 그 자리에 많이 쓰는 자재·시공법으로 이동합니다.</p>'
             f'<figure class="apfig"><img src="/assets/apt/plan-{k}.svg" width="1000" height="680" alt="아파트 {E(t)} 예시 평면도 — 자재 위치 번호"></figure>{AP.legend(k, E)}'
             '<p class="small muted">영진종합목재가 흔한 구조를 참고해 직접 그린 <b>예시</b>입니다. 실제 구조·치수는 단지와 세대마다 다르니, 문 크기·벽 길이는 현장에서 재 주세요. 실제 평면도는 각 단지 카드의 "실제 평면도 보기"로 확인하세요.</p></section>'
             f'<section class="wrap sec"><h2>다른 평형</h2><div class="olk">{oth}</div><p class="hsh olh">옆으로 넘겨 보세요 ›</p></section>' + CTA, "/apt/")
    return pages
