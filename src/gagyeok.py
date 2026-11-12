# 품목별 가격 가이드(/gagyeok/) — 판매 단위가 확인된 품목만. 소매 기준가(prices.csv)만 사용.
import math, re
PY = 3.3058
# slug, 이름, 자재백과 slug, 시공법 slug, [(정규식, 판매단위, 1단위 면적㎡ 또는 None)], 설명, 단위설명, 로스, 예시 면적들(㎡), FAQ
def _lw(w, L=2438, n=8, vis=None): return round((vis or w) / 1000 * L / 1000 * n, 3)
GG = [
 ("hinoki-ruba", "히노끼 루바", "hinoki", "rubaa-cheonjang",
  [(r"루바-히노끼/유절\(오카\)@100\*10\*8자", "1단(8장)", _lw(100, vis=90)), (r"루바-히노끼/무절\(오카\)@100\*10\*8자", "1단(8장)", _lw(100, vis=90))],
  "히노끼 루바는 1단(8장) 단위로 팝니다. 폭 100mm·두께 10mm·길이 8자(약 2.4m)이고, 끼우고 나면 보이는 폭이 약 90mm라 1단이 약 1.75㎡를 덮습니다.",
  "1단 = 8장 · 1장 100×10×2438mm · 시공 면적 약 1.75㎡/단(보이는 폭 90mm 기준)", 0.10,
  [("방 천장 3×3m", 9.0), ("거실 천장 4×5m", 20.0), ("벽 1면 3×2.4m", 7.2)],
  [("히노끼 루바 1평에 몇 단 필요한가요?", "보이는 폭 90mm 기준으로 1평(3.3㎡)에 약 1.9단, 로스 10%를 더하면 약 2.1단입니다. 천장 모양·자르는 양에 따라 달라집니다."),
   ("유절과 무절 차이는요?", "유절은 옹이가 있어 자연스러운 느낌이고 값이 낮습니다. 무절은 옹이가 거의 없어 깔끔하고 값이 높습니다. 매장에서 실물 비교가 가능합니다.")]),
 ("spruce-ruba", "스프러스 루바", "hinoki", "rubaa-cheonjang",
  [(r"루바-스프러스\(유절\)@120\*12\* 8자", "1단(8장)", _lw(120, vis=110))],
  "스프러스 루바(유절, 120×12mm, 8자)는 1단(8장) 단위로 팝니다. 보이는 폭 약 110mm 기준 1단이 약 2.1㎡를 덮어, 히노끼보다 같은 면적에 단 수가 적게 듭니다.",
  "1단 = 8장 · 1장 120×12×2438mm · 시공 면적 약 2.1㎡/단(보이는 폭 110mm 기준)", 0.10,
  [("방 천장 3×3m", 9.0), ("거실 천장 4×5m", 20.0), ("벽 1면 3×2.4m", 7.2)],
  [("스프러스 루바 1평에 몇 단 필요한가요?", "보이는 폭 110mm 기준 1평에 약 1.5단, 로스 10%를 더하면 약 1.7단입니다."),
   ("히노끼 루바와 뭐가 다른가요?", "히노끼는 향과 습기에 강한 점 때문에 욕실·사우나 천장에 많이 쓰고, 스프러스는 결이 밝고 폭이 넓어 거실·카페 벽·천장에 많이 씁니다.")]),
 ("tempa-board", "템바보드", "sound", "tempa-byeok",
  [(r"템바보드 직각\(예림\)소@12\*1200\*2400", "1장", 2.88), (r"템바보드 직각\(영림\)소@15\*1200\*2400", "1장", 2.88), (r"템바보드 직각\(영림\)대@15\*1200\*2400", "1장", 2.88),
   (r"템바보드 직각\(랩핑\)소@12\*1200\*2400", "1장", 2.88), (r"템바보드 직각\(방염\)대@15\*1200\*2400", "1장", 2.88), (r"템바보드 반달\(백골\)소@ 9\*1200\*2400", "1장", 2.88),
   (r"템바보드 반달\( \)소@ 9\*1220\*2440", "1장", 2.977), (r"템바보드 삼각\( \)소@ 9\*1220\*2440", "1장", 2.977)],
  "템바보드는 1장(1200×2400 또는 1220×2440mm) 단위로 팝니다. 1장이 약 2.9㎡라 1평에 약 1.2장(로스 포함) 듭니다. 직각·반달·삼각 모양과 두께(9·12·15T), 마감(백골·랩핑·방염)에 따라 값이 다릅니다.",
  "1장 = 1200×2400mm(2.88㎡) 또는 1220×2440mm(2.98㎡)", 0.10,
  [("TV 벽 1면 3×2.4m", 7.2), ("아트월 2×2.4m", 4.8), ("카페 벽 5×2.7m", 13.5)],
  [("템바보드 1평에 몇 장 필요한가요?", "1장이 약 2.9㎡라 1평(3.3㎡)에 약 1.15장, 로스 10%를 더하면 약 1.3장입니다. 실제로는 벽 폭에 맞춰 장 단위로 올림합니다."),
   ("템바보드 위·아래 마감은 어떻게 하나요?", "보드 두께에 맞는 상하 마감재를 씁니다(9T·12T·15T용 따로). 매장에서 같이 고르시면 됩니다.")]),
 ("tempa-ruba", "템바 루바", "sound", "tempa-byeok",
  [(r"템바\(예림S22\)루바@112\*12\*8자\(6장\)", "1묶음(6장)", _lw(112, n=6)), (r"템바\(예림S14\)루바 @114\*12\*8자\(6장\)", "1묶음(6장)", _lw(114, n=6)),
   (r"템바\(예림S33\)루바@163\*12\*8자\(6장\)", "1묶음(6장)", _lw(163, n=6)), (r"템바\(루바 소\)영림 @100\*12\*8자\(6장\)", "1묶음(6장)", _lw(100, n=6))],
  "템바 루바는 1묶음(6장) 단위로 팝니다. 길이 8자(약 2.4m)이고 제품마다 폭(100~163mm)이 달라 1묶음이 덮는 면적이 1.5~2.4㎡입니다.",
  "1묶음 = 6장 · 길이 2438mm · 면적은 제품 폭 기준 계산", 0.10,
  [("TV 벽 1면 3×2.4m", 7.2), ("아트월 2×2.4m", 4.8), ("카페 벽 5×2.7m", 13.5)],
  [("템바 루바 1평에 몇 묶음 필요한가요?", "폭 112mm 제품 기준 1묶음이 약 1.6㎡라 1평에 약 2묶음, 로스 10%를 더하면 약 2.2묶음입니다. 폭이 넓은 제품일수록 적게 듭니다."),
   ("템바보드와 템바 루바 차이는요?", "템바보드는 큰 판 1장에 홈이 파인 것이라 빨리 붙고, 템바 루바는 긴 쪽판을 하나씩 끼우는 방식이라 길이 방향 이음이 없어 깔끔합니다.")]),
 ("interior-film", "인테리어 필름", "film", "film-sigong",
  [(r"필름-인테리어 @예림135", "1m", None), (r"필름-인테리어 @예림114", "1m", None), (r"필름-인테리어 @예림113\(차콜\)", "1m", None), (r"필름-인테리어 영림@ 175", "1m", None),
   (r"필름-인테리어 영림@ 176", "1m", None), (r"필름-인테리어 영림@ 188", "1m", None), (r"필름-인테리어 영림@ 60번", "1m", None),
   (r"필름-인테리어 쉐누@ 05번", "1m", None), (r"필름-인테리어 쉐누@ 06번", "1m", None), (r"필름-인테리어 쉐누@ 95번", "1m", None)],
  "인테리어 필름은 1m 단위로 잘라 팝니다(m 단가). 폭은 보통 1220mm 안팎이라 1m가 약 1.2㎡입니다. 방문 1짝 양면이면 여유 포함 약 5m 듭니다.",
  "1m 단가 · 폭 약 1220mm(제품마다 조금씩 다름)", 0.0,
  [], [("인테리어 필름 방문 1짝에 몇 m 필요한가요?", "방문(약 900×2100mm) 앞뒤 2면이면 여유 포함 약 5m입니다. 문틀까지 하면 더 필요합니다."),
       ("필름 붙이기 전에 프라이머를 꼭 발라야 하나요?", "네. 프라이머를 바르지 않으면 모서리부터 들뜨기 쉽습니다. 매장에서 필름용 수성 프라이머를 함께 팝니다.")]),
 ("oilstain", "오일스테인", "stain", "oilstain",
  [(r"오일-투명 @3\.5L\(유성/에코\)", "1통(3.5L)", None), (r"오일-월넛 @3\.5L\(유성/에코\)", "1통(3.5L)", None), (r"오일-티크 @3\.5L\(유성/에코\)", "1통(3.5L)", None),
   (r"오일-밤나무 @3\.5L\(유성/에코/404\)", "1통(3.5L)", None), (r"오일-투명 @ 16L\(유성/에코\)", "1통(16L)", None), (r"오일-월넛 @ 16L\(유성/에코\)", "1통(16L)", None),
   (r"오일-투명 @ 1L\(수성/동우\)", "1통(1L)", None), (r"오일-티크 @ 1L\(수성/동우\)", "1통(1L)", None)],
  "오일스테인은 통 단위(1L·3.5L·16L)로 팝니다. 색(투명·월넛·티크·밤나무 등)이 달라도 같은 용량은 기준가가 같습니다. 칠할 면적이 넓으면 큰 통이 1L당 값이 낮습니다.",
  "1통 단가 · 바를 수 있는 면적은 제품 표기 확인(2회 칠 기준으로 계산)", 0.0,
  [], [("오일스테인 데크 10㎡에 몇 통 필요한가요?", "제품 표기 도포량에 따라 다르지만 보통 2회 칠에 3.5L 1통이면 충분한 경우가 많습니다. 나무가 마른 상태면 더 먹습니다."),
       ("유성과 수성 중 뭘 써야 하나요?", "바깥 데크·울타리는 유성이 오래가고, 실내 가구·소품은 냄새가 적은 수성이 편합니다.")]),
]

def gen(page, P, E, CTA, prod_ld, faqslide, BASE, ADDR, HOURS, TEL):
    import json
    pages = []
    for slug, nm, js, sg, specs, lead, unitdesc, loss, exs, faq in GG:
        rows = []
        for rx, unit, area in specs:
            hit = next((p for p in P if re.search(rx, p["name"])), None)
            if hit: rows.append((hit, unit, area))
        if not rows: continue
        def cn(n): return re.sub(r"^[^-]+-\s*", "", n).replace("*", "×").replace("@", " · ").strip(" ·")
        hasA = any(a for _, _, a in rows)
        th = "<tr><th>품목·규격</th><th>판매 단위</th><th class=r>기준가</th>" + ("<th class=r>1단위 면적</th><th class=r>1평 필요량(로스 포함)</th><th class=r>1평 예상 금액</th>" if hasA else ("<th class=r>1L당</th>" if slug == "oilstain" else "<th class=r>1㎡당(폭 1.22m)</th>")) + "</tr>"
        trs = ""
        for p, unit, a in rows:
            pr = p["price"]
            if hasA:
                need = PY / a * (1 + loss)
                ext = f'<td class=r data-l="1단위 면적">{a:.2f}㎡</td><td class=r data-l="1평 필요량">약 {need:.1f}</td><td class=r data-l="1평 예상"><b>약 {round(pr * need, -2):,.0f}원</b></td>'
            elif slug == "oilstain":
                L = float(re.search(r"([\d.]+)L", unit).group(1)); ext = f'<td class=r data-l="1L당">약 {round(pr / L, -2):,.0f}원</td>'
            else:
                ext = f'<td class=r data-l="1㎡당">약 {round(pr / 1.22, -2):,.0f}원</td>'
            trs += f'<tr><td>{E(cn(p["name"]))}</td><td data-l="단위">{unit}</td><td class=r data-l="기준가"><b>{pr:,}원</b></td>{ext}</tr>'
        exh = ""
        if exs and hasA:
            p0, u0, a0 = rows[0]
            et = "".join(f'<tr><th>{E(t)}</th><td class=r>{m2:g}㎡ ({m2 / PY:.1f}평)</td><td class=r>{math.ceil(m2 / a0 * (1 + loss))} {u0.split("(")[0][1:] or "개"}</td><td class=r><b>약 {math.ceil(m2 / a0 * (1 + loss)) * p0["price"]:,}원</b></td></tr>' for t, m2 in exs)
            exh = f'<h2>{E(nm)} 크기별 예상 금액</h2><p class="small muted">기준: {E(cn(p0["name"]))} · 로스 {int(loss * 100)}% 포함 · 올림 계산</p><div class="tw"><table class="rt"><thead><tr><th>예시</th><th class=r>면적</th><th class=r>필요량</th><th class=r>자재비</th></tr></thead><tbody>{et}</tbody></table></div>'
            calc = f'''<div class="card" id="ggc"><h3>내 면적으로 계산</h3><p><label>면적 <input id="gga" type="number" inputmode="decimal" value="3" min="0" step="0.1" style="width:90px"></label> <select id="ggu"><option value="py">평</option><option value="m2">㎡</option></select> <select id="ggp">{"".join(f'<option value="{p["price"]}|{a}">{E(cn(p["name"]))} — {p["price"]:,}원/{u}</option>' for p, u, a in rows)}</select></p><p id="ggr" class="est"></p>
<script>(function(){{var a=document.getElementById("gga"),u=document.getElementById("ggu"),s=document.getElementById("ggp"),r=document.getElementById("ggr");function f(){{var v=parseFloat(a.value)||0,m=u.value=="py"?v*{PY}:v,x=s.value.split("|"),n=Math.ceil(m/parseFloat(x[1])*{1 + loss});r.innerHTML="<b>약 "+n+"단위 · 예상 자재비 약 "+(n*parseInt(x[0])).toLocaleString()+"원</b><span>로스 {int(loss * 100)}% 포함 · 소매 기준가 · 부가세 별도</span>";}}[a,u,s].forEach(function(e){{e.addEventListener("input",f);e.addEventListener("change",f)}});f();}})();</script></div>'''
            exh += calc
        lo = min(p["price"] for p, _, _ in rows)
        title = f"{nm} 가격 — {rows[0][1].split('(')[0]} 기준가 {lo:,}원부터" + (" · 1평에 얼마" if hasA else (" · 1L당 비교" if slug == "oilstain" else " · m당 단가"))
        desc = f"{nm} 소매 기준가 {lo:,}원부터({rows[0][1]}). " + (f"1평에 몇 {rows[0][1][1:].split('(')[0]} 드는지, 크기별 예상 금액 계산." if hasA else "판매 단위와 품목별 기준가 정리.") + " 대전 영진목재."
        body = f'''<section class="wrap sec"><p class="crumb"><a href="/gagyeok/">자재 가격 가이드</a> › {E(nm)}</p><h1>{E(nm)} 가격</h1><p class="lead">{E(lead)}</p>
<p class="small muted">{E(unitdesc)}</p><div class="tw"><table class="rt"><thead>{th}</thead><tbody>{trs}</tbody></table></div><p class="small muted">소매 기준가 · 부가세 별도 · 면적·필요량은 계산 참고치(시공 방법·자르는 양에 따라 달라짐) · 재단·운임은 매장에서 계산</p>
{exh}
<p>👉 <a href="/jajae/{js}.html">{E(nm)} 용도·사진</a> · <a href="/sigongbeop/{sg}.html">시공 방법과 예상 자재비</a> · <a href="/calc.html">자재 계산기</a> · <a href="/price.html">전체 기준가</a></p></section>
<section class="wrap sec"><h2>{E(nm)} 가격 자주 묻는 질문</h2>{faqslide(faq + [(f"{nm} 어디서 사나요?", f"{ADDR} 영진종합목재(월드건축자재) 매장에서 실물을 보고 살 수 있습니다. {HOURS}. 전국 용달 배송도 됩니다.")])}</section>
<section class="wrap sec"><h2>다른 자재 가격</h2><p>{" · ".join(f'<a href="/gagyeok/{g[0]}.html">{E(g[1])} 가격</a>' for g in GG if g[0] != slug)}</p></section>{CTA}'''
        ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]
        ld += prod_ld([{"name": p["name"], "cat": p["cat"], "price": p["price"]} for p, _, _ in rows[:6]], f"{BASE}/gagyeok/{slug}.html")
        page(f"gagyeok/{slug}.html", title + " | 대전 영진목재", desc, body, "/price.html", ld)
        pages.append((slug, nm, lo, rows[0][1], lead))
    cards = "".join(f'<a class="mc" href="/gagyeok/{s}.html"><b>{E(n)} 가격</b><span>{E(u)} {lo:,}원부터 · {E(l[:50])}…</span></a>' for s, n, lo, u, l in pages)
    page("gagyeok/index.html", "자재 가격 가이드 — 루바·템바보드·인테리어 필름·오일스테인 1평에 얼마 | 영진목재",
         "히노끼·스프러스 루바, 템바보드, 템바 루바, 인테리어 필름, 오일스테인의 판매 단위와 소매 기준가, 1평 예상 금액을 정리했습니다.",
         f'<section class="wrap sec"><h1>자재 가격 가이드</h1><p class="lead">"1단에 몇 장이에요?", "1평에 얼마 들어요?" — 자주 묻는 판매 단위와 예상 금액을 자재별로 정리했습니다. 모두 소매 기준가(부가세 별도)입니다.</p><div class="mg m2">{cards}</div><p><a href="/price.html">전체 기준가 보기</a> · <a href="/sigongbeop/">자재 시공법</a></p></section>{CTA}', "/price.html")
    return [(s, n) for s, n, *_ in pages]
