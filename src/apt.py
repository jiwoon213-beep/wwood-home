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
    return [r for r in rows if r["n"] >= 100 and r["단지명"].strip()]


def slug(s):
    return re.sub(r"[^0-9a-zA-Z가-힣]", "", s)


def gu_key(r):
    return ("sejong" if r["시도"] == "세종" else {"동구": "donggu", "중구": "junggu", "서구": "seogu", "유성구": "yuseong", "대덕구": "daedeok"}.get(r["시군구"], "etc"))


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


def build(root, page, E, CTA):
    rows = load(root)
    if not rows: return []
    by = {}
    for r in rows:
        by.setdefault((r["시도"], r["시군구"], r["동리"]), []).append(r)
    pages = []
    for (sd, gu, dong), L in sorted(by.items()):
        L.sort(key=lambda r: -r["n"])
        tot = sum(r["n"] for r in L)
        if len(L) < 2 and tot < 300: continue
        fn = f"apt/{gu_key(L[0])}-{slug(dong)}.html"
        area = f"{'세종' if sd == '세종' else '대전 ' + gu} {dong}"
        ys = [r["y"] for r in L if r["y"]]
        cards = ""
        for r in L:
            tips = "".join(f'<a href="{u}">{E(t)}</a>' for t, u in age_tips(r["y"]))
            meta = " · ".join(x for x in [f'{r["n"]:,}세대', f'{r["동수"]}개 동' if r.get("동수") else "", f'{r["y"]}년' if r["y"] else "", r.get("복도유형", ""), r.get("난방방식", "")] if x)
            cards += (f'<article class="apc" id="{E(r["단지코드"])}"><h3>{E(r["단지명"].strip())}</h3><p class="small muted">{E(meta)}</p>'
                      f'<p>{E(age_text(r["y"]))}</p><div class="apl">{tips}</div></article>')
        oth = [k for k in by if k[0] == sd and k[1] == gu and k[2] != dong]
        near = "".join(f'<a href="/apt/{gu_key(by[k][0])}-{slug(k[2])}.html">{E(k[2])}</a>' for k in sorted(oth) if not (len(by[k]) < 2 and sum(r["n"] for r in by[k]) < 300))
        title = f"{area} 아파트 인테리어 자재 — 중문·방문·몰딩·필름 | 영진목재"
        desc = f"{area} 아파트 {len(L)}개 단지({tot:,}세대)의 준공연도·복도유형에 맞춘 중문·방문 교체·몰딩·필름·바닥 자재 안내. " + ", ".join(r["단지명"].strip() for r in L[:4]) + " 등. 대전 영진종합목재 재단·배송."
        body = (f'<section class="wrap sec"><p class="crumb"><a href="/apt/">아파트별 자재</a> › {E(area)}</p><h1>{E(area)} 아파트 인테리어 자재</h1>'
                f'<p class="lead">{E(area)}에는 100세대 이상 아파트가 <b>{len(L)}개 단지, {tot:,}세대</b> 있습니다' + (f' (사용승인 {min(ys)}~{max(ys)}년)' if ys else '') + '. 단지 연식에 맞춰 많이 하는 공사와 자재를 모았습니다. 단지마다 문 크기·벽 상태가 다르니 <b>현장 치수</b>를 재 오시면 매장에서 맞춰 드립니다.</p>'
                f'<div class="apg">{cards}</div>'
                '<p class="small muted">단지 정보: 국토교통부 공동주택관리정보시스템(K-apt) 공개 단지 기본정보, 매주 갱신. 실제와 다를 수 있습니다. 이 페이지는 해당 단지·관리사무소와 관계없는 자재 안내입니다.</p></section>'
                '<section class="wrap sec"><h2>아파트에서 많이 하는 것</h2><div class="olk"><a href="/sigongbeop/jungmun.html">원슬라이딩 중문 셀프 설치</a><a href="/sigongbeop/munteul-gyoche.html">방문 교체</a><a href="/sigongbeop/film-sigong.html">인테리어 필름</a><a href="/sigongbeop/molding-georebatgi.html">걸레받이·천장 몰딩</a><a href="/sigongbeop/tempa-byeok.html">템바보드 아트월</a><a href="/mandeul/beranda.html">베란다 선반</a><a class="ac" href="/doumi.html">🧭 셀프 인테리어 도우미</a><a class="ac" href="/calc.html">🧮 문짝·중문 크기 계산</a></div><p class="hsh olh">옆으로 넘겨 보세요 ›</p></section>'
                + (f'<section class="wrap sec"><h2>{E(gu if sd != "세종" else "세종")} 다른 동</h2><div class="olk">{near}</div><p class="hsh olh">옆으로 넘겨 보세요 ›</p></section>' if near else "")
                + CTA)
        page(fn, title, desc[:155], body, "/apt/")
        pages.append((fn, area, len(L), tot, gu_key(L[0]), gu, sd))
    # 목록
    G = {}
    for p in pages: G.setdefault((p[6], p[5]), []).append(p)
    sec = ""
    for (sd, gu), ps in sorted(G.items(), key=lambda kv: (kv[0][0] != "대전", kv[0][1])):
        sec += f'<h2 class="ggh">{E("세종시" if sd == "세종" else "대전 " + gu)}</h2><div class="olk aplk">' + "".join(f'<a href="/{p[0]}">{E(p[1].split()[-1])}<small> {p[2]}단지</small></a>' for p in sorted(ps, key=lambda p: -p[3])) + "</div>"
    page("apt/index.html", "대전·세종 아파트별 인테리어 자재 — 동네 단지 연식에 맞춘 안내 | 영진목재",
         f"대전·세종 {len(pages)}개 동, {sum(p[2] for p in pages)}개 아파트 단지의 준공연도에 맞춘 중문·방문·몰딩·필름·바닥 자재 안내. 영진종합목재(대전 유성) 재단·배송.",
         f'<section class="wrap sec"><h1>아파트별 인테리어 자재</h1><p class="lead">우리 동네 아파트를 고르면 단지 연식에 맞춰 많이 하는 공사와 자재를 보여 드립니다. (대전·세종 100세대 이상, K-apt 공개 정보)</p>{sec}</section>' + CTA, "/apt/")
    return pages
