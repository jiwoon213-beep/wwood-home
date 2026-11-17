# 아파트 단지별 인테리어 자재 안내 (/apt/) — K-apt 공개 단지 기본정보(대전·세종)
# 동(읍면동)마다 한 페이지: 단지별 준공연도·세대수·복도유형·난방 + 연식에 맞는 자재 안내.
# 단지 이름은 공개 정보 그대로. 시공비·가격 숫자 없음.
import os, re, csv
from urllib.parse import quote

YEAR = 2026


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


def ok(L):
    return len(L) >= 2 or sum(r["n"] for r in L) >= 300


def build(root, page, E, CTA):
    rows = load(root)
    if not rows: return []
    by = {}
    for r in rows:
        by.setdefault((r["시도"], r["시군구"], r["동리"]), []).append(r)
    bygu = {}
    for k, L in by.items():
        if ok(L): bygu.setdefault((k[0], k[1]), []).append(k)
    pages = []
    for (sd, gu, dong), L in sorted(by.items()):
        if not ok(L): continue
        L.sort(key=lambda r: -r["n"])
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
            cards += (f'<article class="apc" id="{E(r["단지코드"])}"><h3>{E(r["단지명"].strip())}</h3><p class="small muted">{E(meta)}</p>'
                      f'<p>{E(age_text(r["y"]))}</p><div class="apl">{tips}</div></article>')
        more = (f'<p class="small muted">그 밖에 {len(L) - 40}개 단지: ' + ", ".join(E(r["단지명"].strip()) for r in L[40:]) + "</p>") if len(L) > 40 else ""
        near = "".join(f'<a href="/{fname(*k)}">{E(k[2])}</a>' for k in sorted(bygu.get((sd, gu), [])) if k[2] != dong)
        stat = (f'평균 약 {avg}년 차' + (f', 20년 넘은 단지 {old}곳' if old else '') + (f', 복도식 {bok}곳' if bok else '')) if ys else ""
        if sd in NEAR:
            how = '자재는 대전 유성 매장에서 실물을 보고 원하는 크기로 잘라 가실 수 있고, 현장까지 배송도 됩니다.'
            rl = '<a href="/visit.html">매장 길찾기</a><a href="/jaedan-baesong.html">재단 후 배송</a>'
        else:
            rg = reg(sd, gu)
            how = f'{E(sd)} 현장은 치수대로 재단해서 <b>전국 배송</b>으로 보내 드립니다(운임은 견적). 중문·방문·몰딩은 문 크기를 재서 보내 주세요.'
            rl = (f'<a href="/jeonguk/{rg}.html">{E(sd)} 배송 안내</a>' if rg else '') + '<a href="/jaedan-baesong.html">재단 후 전국 배송</a>'
        title = f"{area} 아파트 인테리어 자재 — 중문·방문·몰딩·필름 | 영진목재"
        desc = f"{area} 아파트 {len(L)}개 단지({tot:,}세대) 준공연도별 중문·방문 교체·몰딩·필름·바닥 자재 안내. " + ", ".join(r["단지명"].strip() for r in L[:3]) + " 등. 재단·전국 배송."
        body = (f'<section class="wrap sec"><p class="crumb"><a href="/apt/">아파트별 자재</a> › <a href="/apt/{SDS.get(sd, "etc")}/">{E(sd)}</a> › {E(area)}</p><h1>{E(area)} 아파트 인테리어 자재</h1>'
                f'<p class="lead">{E(area)}에는 100세대 이상 아파트가 <b>{len(L)}개 단지, {tot:,}세대</b> 있습니다' + (f' (사용승인 {min(ys)}~{max(ys)}년, {stat})' if ys else '') + '. 단지 연식에 맞춰 많이 하는 공사와 자재를 모았습니다.</p>'
                f'<p>{how}</p><div class="olk">{rl}<a class="ac" href="/doumi.html">🧭 셀프 인테리어 도우미</a><a class="ac" href="/calc.html">🧮 문짝·중문 크기 계산</a></div>'
                f'<div class="apg">{cards}</div>{more}'
                '<p class="small muted">단지 정보: 국토교통부 공동주택관리정보시스템(K-apt) 공개 단지 기본정보, 매주 갱신. 실제와 다를 수 있습니다. 이 페이지는 해당 단지·관리사무소와 관계없는 자재 안내입니다.</p></section>'
                '<section class="wrap sec"><h2>아파트에서 많이 하는 것</h2><div class="olk"><a href="/sigongbeop/jungmun.html">원슬라이딩 중문 셀프 설치</a><a href="/sigongbeop/munteul-gyoche.html">방문 교체</a><a href="/sigongbeop/film-sigong.html">인테리어 필름</a><a href="/sigongbeop/molding-georebatgi.html">걸레받이·천장 몰딩</a><a href="/sigongbeop/tempa-byeok.html">템바보드 아트월</a><a href="/mandeul/beranda.html">베란다 선반</a></div><p class="hsh olh">옆으로 넘겨 보세요 ›</p></section>'
                + (f'<section class="wrap sec"><h2>{E(areaname(sd, gu, ""))} 다른 동</h2><div class="olk">{near}</div><p class="hsh olh">옆으로 넘겨 보세요 ›</p></section>' if near else "")
                + CTA)
        page(fn, title, desc[:155], body, "/apt/")
        pages.append((fn, sd, gu, dong, len(L), tot))
    # 시도 페이지
    S = {}
    for p in pages: S.setdefault(p[1], {}).setdefault(p[2], []).append(p)
    idx = ""
    for sd in sorted(S, key=lambda x: SDO.index(x) if x in SDO else 99):
        G = S[sd]; nd = sum(len(v) for v in G.values()); nc = sum(p[4] for v in G.values() for p in v)
        sec = ""
        for gu in sorted(G):
            ps = sorted(G[gu], key=lambda p: -p[5])
            sec += (f'<h2 class="ggh">{E(areaname(sd, gu, ""))}</h2>' if gu and not gu.startswith("세종") else "") + '<div class="olk aplk">' + "".join(f'<a href="/{p[0]}">{E(p[3])}<small> {p[4]}단지</small></a>' for p in ps) + "</div>"
        page(f"apt/{SDS.get(sd, 'etc')}/index.html", f"{sd} 아파트별 인테리어 자재 — 동네 단지 연식에 맞춘 안내 | 영진목재",
             f"{sd} {nd}개 동, {nc}개 아파트 단지의 준공연도에 맞춘 중문·방문·몰딩·필름·바닥 자재 안내. 영진종합목재 재단·전국 배송.",
             f'<section class="wrap sec"><p class="crumb"><a href="/apt/">아파트별 자재</a> › {E(sd)}</p><h1>{E(sd)} 아파트별 인테리어 자재</h1><p class="lead">동네를 고르면 단지 연식에 맞춰 많이 하는 공사와 자재를 보여 드립니다. ({nd}개 동 · {nc:,}개 단지, K-apt 공개 정보)</p>{sec}</section>' + CTA, "/apt/")
        idx += f'<a href="/apt/{SDS.get(sd, "etc")}/"><b>{E(sd)}</b><small> {nd}개 동 · {nc:,}단지</small></a>'
    page("apt/index.html", "전국 아파트별 인테리어 자재 — 우리 단지 연식에 맞춘 안내 | 영진목재",
         f"전국 {len(pages):,}개 동, {sum(p[4] for p in pages):,}개 아파트 단지의 준공연도에 맞춘 중문·방문·몰딩·필름·바닥 자재 안내. 영진종합목재(대전) 재단·전국 배송.",
         f'<section class="wrap sec"><h1>전국 아파트별 인테리어 자재</h1><p class="lead">우리 동네 아파트를 고르면 단지 연식에 맞춰 많이 하는 공사와 자재를 보여 드립니다. (전국 100세대 이상, K-apt 공개 정보 · 매주 갱신)</p><div class="olk aplk apsd">{idx}</div></section>' + CTA, "/apt/")
    return pages
