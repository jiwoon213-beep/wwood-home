"""평수별 자재비 예시(/yesi/) — '데크 3평 자재비', '방 천장 루바 4평' 같은 검색어용.
홈페이지 소매 기준가(prices.csv)로 계산한 값만 씀. 시공비·소요일 같은 확인 안 된 숫자는 넣지 않음."""
import math, json, re
import gyeonjeok as GJ

PY = 3.3058
LINKS = []


def _won(x):
    return f"{int(round(x)):,}원"


def _ceil(x):
    return int(math.ceil(x - 1e-9))


def gen(page, P, E, CTA, faqslide, TEL):
    D = {w["k"]: w for w in GJ.data(P)}
    pr = lambda rx: GJ._price(P, rx)
    b24 = pr(r"방부- 2\* 4\*12자\(파인\)")

    def items(k, names):
        out = []
        for nm in names:
            for it in D.get(k, {}).get("it", []):
                if it["n"].startswith(nm) and it["a"] and it["p"]:
                    out.append(it); break
        return out

    pages = []

    # 1) 데크
    DECK = [(1, 1.8, 1.8, "현관 앞·작은 테라스"), (2, 2.7, 2.4, "현관·뒷마당 테라스"), (3, 3.6, 2.7, "베란다·마당 한쪽"), (4, 3.6, 3.6, "마당 데크"), (5, 4.5, 3.6, "마당 데크"), (6, 4.5, 4.4, "전원주택 마당"), (8, 5.4, 4.9, "전원주택 마당"), (10, 6.0, 5.4, "넓은 마당·펜션 테라스"), (15, 7.2, 6.9, "펜션·카페 테라스"), (20, 8.1, 8.1, "펜션·카페 테라스")]
    dk = [("방부목 20×120 데크재", "20×120×12자(데크)", 120, 3.6), ("방부목 25×140 데크재", "25×140×12자(데크)", 140, 3.6), ("합성데크 20×140 솔리드", "데크(솔리드) · 20×140×3000", 140, 3.0)]
    for py, L, W, where in DECK:
        A = L * W
        rows = []
        for lab, nm, bw, bl in dk:
            it = next((i for i in D["deck"]["it"] if i["n"].startswith(nm.split(" · ")[0]) and (" · " not in nm or nm.split(" · ")[1] in i["n"])), None)
            if not it: continue
            n_rows = _ceil(W / ((bw + 5) / 1000)); q = _ceil(n_rows * L / bl * 1.05)  # 판 방향 길이 기준(자투리는 이어서 씀)
            jo = math.floor(W / 0.4) + 1; jq = _ceil(jo * L / 3.6 * 1.05)
            rows.append((lab, it["n"], q, int(it["p"]), jq))
        if not rows: continue
        body_rows = []
        for lab, nm, q, p, jq in rows:
            body_rows.append((lab, f"{q}개", q * p, f"+ 장선 2×4(3.6m) {jq}개", jq * b24 if b24 else 0))
        pages.append(dict(slug=f"deck-{py}py", kind="데크", h1=f"데크 {py}평 자재비 — 방부목·합성데크 비교",
                          title=f"데크 {py}평 자재비 얼마? 방부목·합성데크 수량·가격 비교", area=A, size=f"{L:g}m × {W:g}m", where=where, rows=body_rows,
                          note="장선(2×4, 400mm 간격)까지 넣은 값입니다. 멍에·기둥·기초·철물·피스는 높이와 바닥 상태에 따라 달라 따로 계산하세요.",
                          calc="/deck-gyesan.html", calcn="데크 자재 계산기", mat="/jajae/bangbu.html", matn="방부목", gg="/gagyeok/deck-gagyeok.html", vn="데크 만들기 방부목 합성데크"))

    # 2) 천장 루바
    for py, where in [(2, "욕실 앞·베란다 천장"), (3, "베란다·작은 방 천장"), (4, "작은 방 천장"), (5, "다락·사우나 천장"), (6, "안방 천장"), (8, "거실 천장"), (10, "거실·카페 천장")]:
        A = py * PY
        its = items("ceil_ruba", ["히노끼/유절", "히노끼/무절", "스프러스"])
        rows = [(i["n"].replace("/", " "), f'{_ceil(A * 1.1 / i["a"])}단', _ceil(A * 1.1 / i["a"]) * int(i["p"]), "", 0) for i in its]
        if rows:
            pages.append(dict(slug=f"ruba-ceiling-{py}py", kind="루바", h1=f"천장 루바 {py}평 자재비 — 히노끼·스프러스 비교",
                              title=f"천장 루바 {py}평 몇 단·얼마? 히노끼 유절·무절·스프러스 비교", area=A, size=f"천장 {A:.1f}㎡", where=where, rows=rows,
                              note="루바는 1단(8장) 단위입니다. 로스 10% 포함. 다루끼(바탕 각재)·타카핀·몰딩은 따로 필요합니다.",
                              calc="/gyeonjeok.html", calcn="방 통째로 계산", mat="/jajae/hinoki.html", matn="히노끼·루바", gg="/gagyeok/hinoki-ruba.html", vn="루바 천장 히노끼 시공"))

    # 3) 석고보드 천장·가벽
    for py in (3, 5, 8, 10, 15, 20):
        A = py * PY
        its = items("ceil_gyp", ["일반 3×6 · 9.5T", "방화 3×6 · 12.5T", "방수 3×6 · 9.5T"])
        rows = [(i["n"], f'{_ceil(A * 1.1 / i["a"])}장', _ceil(A * 1.1 / i["a"]) * int(i["p"]), "", 0) for i in its]
        if rows:
            pages.append(dict(slug=f"gypsum-ceiling-{py}py", kind="석고보드", h1=f"천장 석고보드 {py}평 몇 장? 일반·방화·방수 비교",
                              title=f"천장 석고보드 {py}평 몇 장·자재비? 9.5T·12.5T 비교", area=A, size=f"천장 {A:.1f}㎡", where="방·거실 천장", rows=rows,
                              note="3×6(900×1800) 한 겹 기준, 로스 10% 포함. 두 겹 시공은 두 배로 잡으세요. 각재·피스·퍼티는 따로입니다.",
                              calc="/gabyeok-gyesan.html", calcn="가벽 자재 계산기", mat="/jajae/gypsum.html", matn="석고보드", gg="/gagyeok/seokgo-gagyeok.html", vn="석고보드 천장 시공"))

    # 4) 아트월(템바보드)
    for W, H, where in [(1.2, 2.4, "포인트 벽 한 칸"), (2.4, 2.4, "침실 헤드 벽"), (3.6, 2.4, "거실 TV 아트월")]:
        A = W * H
        its = [i for i in D["art"]["it"] if i["a"] and i["p"]][:4]
        rows = [(i["n"], f'{_ceil(W / 1.2 - 1e-6)}장', _ceil(W / 1.2 - 1e-6) * int(i["p"]), "", 0) for i in its]
        if rows:
            pages.append(dict(slug=f"tempa-wall-{str(W).replace('.', '')}m", kind="템바보드", h1=f"템바보드 아트월 {W:g}m 벽 자재비",
                              title=f"템바보드 아트월 {W:g}m×{H:g}m 몇 장·얼마? 예림·영림 비교", area=A, size=f"{W:g}m × {H:g}m", where=where, rows=rows,
                              note="1200×2400 한 장을 세로로 세워 벽 폭만큼 붙인 기준입니다(높이 2.4m 이하). 본드·실리콘·마감 몰딩은 따로입니다.",
                              calc="/gyeonjeok.html", calcn="방 통째로 계산", mat="/jajae/molding.html", matn="몰딩·아트월", gg="/gagyeok/tempa-board.html", vn="템바보드 아트월 시공"))

    # 5) 외벽 사이딩
    for nm_, A, where in [("농막 6×3m", (6 + 3) * 2 * 2.4 * 0.85, "농막·창고 외벽(창·문 15% 뺌)"), ("단층 주택 30평", 120 * 0.85, "주택 외벽 약 120㎡(창·문 15% 뺌)")]:
        its = [i for i in D["siding"]["it"] if i["a"] and i["p"]][:2]
        rows = [(("시멘트사이딩 " if i["n"].startswith("시멘트") else "세라믹사이딩 ") + i["n"].replace("시멘트 · ", ""), f'{_ceil(A * 1.1 / i["a"])}장', _ceil(A * 1.1 / i["a"]) * int(i["p"]), "", 0) for i in its]
        if rows:
            sl = "siding-nongmak" if "농막" in nm_ else "siding-house-30py"
            pages.append(dict(slug=sl, kind="사이딩", h1=f"{nm_} 외벽 사이딩 자재비 — 시멘트·세라믹 비교",
                              title=f"{nm_} 외벽 사이딩 몇 장·얼마? 시멘트사이딩·세라믹사이딩(V16) 비교", area=A, size=f"외벽 {A:.0f}㎡", where=where, rows=rows,
                              note="로스 10% 포함. 하지(각재·각관)·투습방수지·후레싱·코너 마감재·실리콘은 따로입니다.",
                              calc="/gyeonjeok.html", calcn="방 통째로 계산", mat="/jajae/siding.html", matn="사이딩", gg="/gagyeok/siding-gagyeok.html", vn="세라믹사이딩 외벽 시공"))

    # 6) 바닥 합판
    for py in (3, 4, 5, 8, 10):
        A = py * PY
        its = items("floor_ply", ["일반 4×8 · 11.5mm(인)A급", "일반 4×8 · 8.5mm(베)"])
        rows = [(i["n"], f'{_ceil(A * 1.1 / i["a"])}장', _ceil(A * 1.1 / i["a"]) * int(i["p"]), "", 0) for i in its]
        if rows:
            pages.append(dict(slug=f"floor-plywood-{py}py", kind="합판", h1=f"방 바닥 합판 {py}평 몇 장? 두께별 자재비",
                              title=f"바닥 합판 {py}평 몇 장·얼마? 4×8 합판 두께별 비교", area=A, size=f"바닥 {A:.1f}㎡", where="방 바닥 덧방·다락 바닥", rows=rows,
                              note="4×8(1220×2440) 기준, 로스 10% 포함. 각재·피스·본드는 따로입니다.",
                              calc="/calc.html", calcn="자재 계산기", mat="/jajae/hapan.html", matn="합판", gg="/gagyeok/hapan-gagyeok.html", vn="합판 바닥 시공"))

    # 7) 벽 단열
    for py in (3, 4, 5, 8):
        A = (math.sqrt(py * PY) * 4) * 2.4 * 0.85
        its = items("wall_ins", ["아이소핑크 · 900×1800×30T", "아이소핑크 · 900×1800×50T"])
        rows = [(i["n"], f'{_ceil(A * 1.1 / i["a"])}장', _ceil(A * 1.1 / i["a"]) * int(i["p"]), "", 0) for i in its]
        if rows:
            pages.append(dict(slug=f"wall-insul-{py}py", kind="단열재", h1=f"방 {py}평 벽 단열 아이소핑크 몇 장? 30T·50T 비교",
                              title=f"방 {py}평 벽 단열 아이소핑크 몇 장·얼마? 30T·50T 비교", area=A, size=f"벽 약 {A:.0f}㎡(높이 2.4m, 창·문 15% 뺌)", where="결로·외풍 잡는 방 벽", rows=rows,
                              note="네 벽 모두 한 겹 기준, 로스 10% 포함. 아이소핑크 본드·우레탄폼·석고보드 마감은 따로입니다.",
                              calc="/gabyeok-gyesan.html", calcn="가벽 자재 계산기", mat="/jajae/insul.html", matn="단열재", gg="/gagyeok/danyeol-gagyeok.html", vn="아이소핑크 단열 시공"))

    # 8) 방 벽 석고보드
    for py in (3, 4, 5, 8, 10):
        A = (math.sqrt(py * PY) * 4) * 2.4 * 0.85
        its = items("wall_gyp", ["일반 3×6 · 9.5T", "방화 3×6 · 12.5T", "방수 3×6 · 9.5T"])
        rows = [(i["n"], f'{_ceil(A * 1.1 / i["a"])}장', _ceil(A * 1.1 / i["a"]) * int(i["p"]), "", 0) for i in its]
        if rows:
            pages.append(dict(slug=f"gypsum-wall-{py}py", kind="석고보드", h1=f"방 {py}평 벽 석고보드 몇 장? 일반·방화·방수 비교",
                              title=f"방 {py}평 벽 석고보드 몇 장·자재비? 9.5T·12.5T 비교", area=A, size=f"벽 약 {A:.0f}㎡(높이 2.4m, 창·문 15% 뺌)", where="방 네 벽 마감·리모델링", rows=rows,
                              note="네 벽 한 겹 기준, 로스 10% 포함. 두 겹이면 두 배로 잡으세요. 각재·피스·퍼티·코너비드는 따로입니다.",
                              calc="/gabyeok-gyesan.html", calcn="가벽 자재 계산기", mat="/jajae/gypsum.html", matn="석고보드", gg="/gagyeok/seokgo-gagyeok.html", vn="석고보드 벽 시공"))

    # 9) 방 벽 이보드(단열 도배)
    for py in (3, 4, 5, 8):
        A = (math.sqrt(py * PY) * 4) * 2.4 * 0.85
        its = items("wall_ins", ["이보드(도배용)", "아이소핑크 · 900×1800×30T"])
        rows = [(i["n"], f'{_ceil(A * 1.1 / i["a"])}장', _ceil(A * 1.1 / i["a"]) * int(i["p"]), "", 0) for i in its]
        if rows:
            pages.append(dict(slug=f"eboard-wall-{py}py", kind="단열재", h1=f"방 {py}평 이보드 몇 장? 결로·곰팡이 벽 단열",
                              title=f"방 {py}평 이보드 몇 장·얼마? 도배용 단열보드·아이소핑크 비교", area=A, size=f"벽 약 {A:.0f}㎡(높이 2.4m, 창·문 15% 뺌)", where="결로·곰팡이 생기는 방 벽", rows=rows,
                              note="네 벽 한 겹 기준, 로스 10% 포함. 이보드는 붙이고 바로 도배할 수 있는 단열보드입니다. 본드·폼·도배지는 따로입니다.",
                              calc="/gabyeok-gyesan.html", calcn="가벽 자재 계산기", mat="/jajae/insul.html", matn="단열재", gg="/gagyeok/danyeol-gagyeok.html", vn="이보드 단열 시공"))

    # 10) 벽 루바
    for py in (3, 4, 5):
        A = (math.sqrt(py * PY) * 4) * 2.4 * 0.85
        its = items("ceil_ruba", ["히노끼/유절", "히노끼/무절", "스프러스"])
        rows = [(i["n"].replace("/", " "), f'{_ceil(A * 1.1 / i["a"])}단', _ceil(A * 1.1 / i["a"]) * int(i["p"]), "", 0) for i in its]
        if rows:
            pages.append(dict(slug=f"ruba-wall-{py}py", kind="루바", h1=f"방 {py}평 벽 루바 자재비 — 히노끼·스프러스 비교",
                              title=f"방 {py}평 벽 루바 몇 단·얼마? 히노끼 유절·무절·스프러스 비교", area=A, size=f"벽 약 {A:.0f}㎡(높이 2.4m, 창·문 15% 뺌)", where="편백 방·황토방·사우나 벽", rows=rows,
                              note="루바는 1단(8장) 단위, 네 벽 기준, 로스 10% 포함. 다루끼(바탕 각재)·타카핀·몰딩은 따로 필요합니다.",
                              calc="/gyeonjeok.html", calcn="방 통째로 계산", mat="/jajae/hinoki.html", matn="히노끼·루바", gg="/gagyeok/hinoki-ruba.html", vn="루바 벽 히노끼 시공"))

    # 페이지 생성
    links = []
    for d in pages:
        rows = d["rows"]
        tot = [(r[0], r[2] + r[4]) for r in rows]
        lo, hi = min(tot, key=lambda x: x[1]), max(tot, key=lambda x: x[1])
        tb = "".join(f'<tr><th>{E(r[0])}</th><td data-l="수량">{E(r[1])}{("<br><small>" + E(r[3]) + "</small>") if r[3] else ""}</td><td data-l="자재비"><b>{_won(r[2] + r[4])}</b></td></tr>' for r in rows)
        py_ = d["area"] / PY
        fq = [(f"{d['kind']} {d['size']}이면 자재비가 얼마인가요?", f"홈페이지 소매 기준가로 {_won(lo[1])}({lo[0]})부터 {_won(hi[1])}({hi[0]})까지입니다. 부가세 별도이고, 재고와 규격에 따라 달라질 수 있습니다."),
              (f"가장 싼 것과 비싼 것 차이는요?", f"이 크기에서 {lo[0]}와 {hi[0]}의 자재비 차이는 약 {_won(hi[1] - lo[1])}입니다. 내구성·관리·느낌이 달라 매장에서 실물을 보고 고르시길 권합니다."),
              ("원하는 크기로 잘라 주나요?", "네, 매장에서 원하는 길이로 재단해 드립니다. 대전·세종·공주·계룡·논산·금산·옥천은 배송하고, 그 밖의 지역은 용달로 보내 드립니다(운임 견적).")]
        fld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}
        body = f'''<section class="wrap sec"><p class="crumb"><a href="/yesi/">평수별 자재비</a> › {E(d["kind"])}</p><h1>{E(d["h1"])}</h1>
<p class="lead">{E(d["where"])} {E(d["size"])}(약 {py_:.1f}평, {d["area"]:.1f}㎡)을 할 때 필요한 자재 수량과 홈페이지 기준가 자재비입니다.</p>
<div class="ysum"><div><small>가장 적게</small><b>{_won(lo[1])}</b><span>{E(lo[0])}</span></div><div><small>가장 많이</small><b>{_won(hi[1])}</b><span>{E(hi[0])}</span></div></div>
<h2>자재별 수량·자재비</h2><div class="tw"><table class="rt"><thead><tr><th>자재</th><th>수량</th><th>자재비</th></tr></thead><tbody>{tb}</tbody></table></div>
<p class="small muted">{E(d["note"])} 홈페이지 소매 기준가(부가세 별도) · 시공비 별도 · 재고·규격에 따라 달라집니다.</p>
<div class="yact"><a class="b r" href="{d["calc"]}">내 크기로 다시 계산 › {E(d["calcn"])}</a><a class="b" href="{d["gg"]}">{E(d["kind"])} 가격 가이드</a><a class="b" href="{d["mat"]}">{E(d["matn"])} 용도·규격</a><a class="b" href="/mirigi.html">사진에 입혀 보기</a><button type="button" class="b" onclick="WWHJ('calc',document.querySelector('.ysum').innerText+'\n\n'+document.querySelector('.rt').innerText,this)">현장함에 저장</button></div>
<h2>관련 시공 영상</h2><div class="ylv pv" data-n="{E(d["vn"])}" data-c="{E(d["kind"])}"></div>
<h2>자주 묻는 질문</h2>{faqslide(fq)}</section>{CTA}
<style>.ysum{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:14px 0}}.ysum div{{background:#1D1B18;color:#fff;border-radius:16px;padding:14px}}.ysum div+div{{background:#fff;color:#1D1B18;border:1px solid #ece6dc}}.ysum small{{display:block;font-size:12px;opacity:.7;font-weight:700}}.ysum b{{display:block;font-size:22px;font-weight:900;letter-spacing:-.5px;margin:2px 0}}.ysum span{{font-size:12.5px;opacity:.8}}.yact{{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}}.yact .b{{font-size:14px}}</style>'''
        desc = f"{d['kind']} {d['size']}(약 {py_:.1f}평) 자재비 {_won(lo[1])}~{_won(hi[1])}. 수량·기준가 비교, 원하는 크기 재단·배송."
        page(f"yesi/{d['slug']}.html", d["title"] + " | 영진목재", desc, body, "/calc.html", fld)
        links.append((d, lo, hi))

    global LINKS
    LINKS = [(d["kind"], d["slug"], d["h1"].split(" — ")[0], lo[1], hi[1]) for d, lo, hi in links]
    # 허브
    grp = {}
    for d, lo, hi in links: grp.setdefault(d["kind"], []).append((d, lo, hi))
    def _big(d):
        m = re.search(r"(\d+(?:\.\d+)?)\s*평", d["h1"]) or (re.search(r"아트월 (\d+(?:\.\d+)?)m", d["h1"]) if d["kind"] == "템바보드" else None)
        if m: return (m.group(1), "평" if "평" in m.group(0) else "m 벽")
        return (f'{d["area"]:.0f}', "㎡")
    hub = "".join(f'<h2>{E(k)} <small class="yhs">{len(v)}가지 · 옆으로 넘겨 보세요</small></h2><div class="yrow">' + "".join(
        f'<a class="ycd" href="/yesi/{d["slug"]}.html"><span class="ybg"><b>{_big(d)[0]}</b>{_big(d)[1]}</span><span class="ynm">{E(d["h1"].split(" — ")[0])}</span><span class="ypr">{_won(lo[1])}~</span><span class="ypr2">최대 {_won(hi[1])}</span></a>'
        for d, lo, hi in v) + "</div>" for k, v in grp.items())
    page("yesi/index.html", "평수별 자재비 예시 — 데크·루바·석고보드·사이딩·단열 몇 평이면 얼마? | 영진목재",
         "데크 3평, 천장 루바 4평, 농막 외벽 사이딩처럼 자주 묻는 크기별 자재 수량과 기준가 자재비를 한눈에. 내 크기는 계산기로.",
         f'''<section class="wrap sec"><h1>평수별 자재비 예시</h1><p class="lead">자주 묻는 크기로 자재 수량과 홈페이지 기준가 자재비를 미리 계산해 두었습니다. 내 크기는 <a href="/calc.html">자재 계산기</a>로 바로 계산하세요.</p>{hub}
<p class="small muted">홈페이지 소매 기준가(부가세 별도) · 시공비 별도 · 재고·규격에 따라 달라집니다.</p></section>{CTA}
<style>.yhs{{font-size:12.5px;color:#8a8378;font-weight:700;margin-left:4px}}.yrow{{display:flex;gap:10px;overflow-x:auto;scroll-snap-type:x mandatory;padding:4px 2px 12px;scrollbar-width:none;-webkit-overflow-scrolling:touch}}.yrow::-webkit-scrollbar{{display:none}}.ycd{{flex:0 0 150px;scroll-snap-align:start;display:flex;flex-direction:column;gap:4px;background:#fff;border:1px solid #ece6dc;border-radius:18px;padding:14px;color:#1D1B18!important;text-decoration:none!important;box-shadow:0 2px 10px rgba(0,0,0,.04)}}.ycd:first-child{{background:#1D1B18;color:#fff!important;border-color:#1D1B18}}.ybg{{font-size:15px;font-weight:800;color:#8a8378}}.ybg b{{font-size:34px;font-weight:900;letter-spacing:-1px;color:#1D1B18;margin-right:2px}}.ycd:first-child .ybg b{{color:#fff}}.ynm{{font-size:13px;font-weight:700;opacity:.75}}.ypr{{margin-top:6px;font-size:17px;font-weight:900;color:#c41a1f}}.ycd:first-child .ypr{{color:#ffd27a}}.ypr2{{font-size:12px;opacity:.6}}</style>''', "/calc.html")
    return len(links)
