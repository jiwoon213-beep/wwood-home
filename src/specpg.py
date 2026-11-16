# 검색어 겨냥 안내 페이지: 방부목 규격, 데크 피스, 아일랜드 식탁 사이즈
# 가격은 prices.csv(매장 기준가)에 있는 것만. 확인 안 된 시공비·소요일 숫자 금지.
import re


def _fq(fq):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}


def _tbl(head, rows):
    return '<div class="tw"><table><tr>' + "".join(f"<th>{h}</th>" for h in head) + "</tr>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</table></div>"


def gen(page, P, E, CTA, faqslide, TEL):
    tel = TEL.replace("-", "")
    # ── 1. 방부목 규격 ──
    rows = []
    for p in P:
        if p["cat"] not in ("방부", "가공") or "방부" not in p["name"]: continue
        m = re.search(r"@\s*(\d+)\s*\*\s*(\d+)\s*\*\s*(\d+)", p["name"]) or re.search(r"-\s*(\d+)\s*\*\s*(\d+)\s*\*\s*(\d+)자", p["name"])
        if not m: continue
        a, b, c = (int(x) for x in m.groups())
        if c < 100: c = round(c * 303.03 / 100) * 100  # 12자 → 3600
        use = "데크재(바닥판)" if (a <= 40 and b >= 90 and ("데크" in p["name"])) else ("각재·기둥" if a == b or (a >= 60 and b <= 120) else ("구조재·장선" if a == 38 else "판재"))
        if "의자" in p["name"]: use = "의자목·벤치"
        rows.append((use, f"{a}×{b}", f"{c:,}mm", p["price"], E(p["name"])))
    rows.sort(key=lambda r: ("데크재(바닥판)", "구조재·장선", "각재·기둥", "판재", "의자목·벤치").index(r[0]) if r[0] in ("데크재(바닥판)", "구조재·장선", "각재·기둥", "판재", "의자목·벤치") else 9)
    tb = _tbl(["용도", "두께×폭(mm)", "길이", "매장 기준가", "매장 품명"], [(u, s, l, f"{pr:,}원~", n) for u, s, l, pr, n in rows])
    fq = [("방부목 데크재 규격은 몇 가지인가요?", "매장 기준가 표에 있는 방부 데크재는 두께 15·20·25·40mm, 폭 95~140mm, 길이 1800~3600mm입니다. 정확한 재고는 전화로 확인해 주세요."),
          ("방부목 장선(구조재)은 어떤 규격을 쓰나요?", "데크 장선은 보통 38×89(2×4)나 38×140(2×6) 방부 구조재를 씁니다. 간격과 길이에 따라 달라지니 데크 계산기로 수량을 먼저 확인해 보세요."),
          ("방부목도 원하는 길이로 잘라 주나요?", "네. 매장에서 산 자재는 원하는 길이로 재단해 드립니다. 30T가 넘는 두께는 재단비를 전화로 문의해 주세요."),
          ("12자는 몇 mm인가요?", "1자는 약 303mm라서 12자는 약 3,600mm, 8자는 약 2,400mm, 6자는 약 1,800mm입니다.")]
    body = f'''<section class="wrap sec"><p class="crumb"><a href="/">홈</a> › <a href="/gyugyeok.html">규격표</a> › 방부목 규격</p>
<h1>방부목 규격표 — 데크재·구조재·각재 사이즈와 기준가</h1>
<p class="lead">대전 영진목재 매장 기준가 표에 있는 방부목 {len(rows)}가지 규격을 용도별로 모았습니다. 두께×폭은 mm, 12자는 약 3,600mm입니다.</p>
<div class="row"><a class="b r" href="/deck-gyesan.html">데크 수량 계산기</a><a class="b o" href="/deck-pis.html">데크 피스 고르기</a><a class="b o" href="/gagyeok/deck-gagyeok.html">데크 가격 가이드</a><a class="b d" href="tel:{tel}">재고 전화 확인</a></div>
<h2>방부목 규격·기준가</h2>{tb}
<p class="small muted">매장 소매 기준가(부가세 별도) · 재고와 수종은 바뀔 수 있어요 · 전체 기준가는 <a href="/price.html">기준가 표</a></p>
<h2>용도별로 이렇게 고릅니다</h2>
<ul class="mgl"><li><b>데크 바닥판</b><span>방부 데크재(두께 20~25mm, 폭 95~140mm). 두꺼울수록 장선 간격을 넓힐 수 있어요.</span></li><li><b>장선·멍에</b><span>38×89(2×4), 38×140(2×6) 방부 구조재</span></li><li><b>기둥</b><span>89×89(4×4), 120×120 방부 각재. 기초는 <a href="/cheolmul/juchudol.html">주춧돌·기둥받침</a></span></li><li><b>울타리·평상·벤치</b><span>판재·의자목 — <a href="/mandeul/">DIY 만들기</a> 도안 참고</span></li></ul>
<h2>자주 묻는 질문</h2>{faqslide(fq)}</section>''' + CTA
    page("bangbu-gyugyeok.html", "방부목 규격표 — 데크재·구조재·각재 사이즈와 기준가 | 영진목재",
         "방부목 데크재·장선 구조재·기둥 각재 규격(두께×폭×길이)과 매장 기준가를 한 표로. 12자=약 3,600mm.", body, jsonld=_fq(fq))

    # ── 2. 데크 피스 ──
    pis = [p for p in P if p["cat"] == "피스" and re.search(r"(아연|스텐)", p["name"]) and re.search(r"@\s*\d+\s*\*\s*(\d+)", p["name"]) and int(re.search(r"@\s*\d+\s*\*\s*(\d+)", p["name"]).group(1)) >= 38 and "석고" not in p["name"]]
    pis.sort(key=lambda p: int(re.search(r"\*\s*(\d+)", p["name"]).group(1)))
    clip = [p for p in P if p["cat"] == "합성" and ("클립" in p["name"] or "스타터" in p["name"])]
    ptb = _tbl(["매장 품명", "기준가"], [(E(p["name"]), f"{p['price']:,}원~") for p in pis + clip])
    sz = _tbl(["데크재 두께", "피스 길이(대략)", "이유"],
              [("15~20mm", "38~50mm", "판 두께의 약 2.2~2.5배"), ("25mm", "50~65mm", "장선에 25mm 이상 박히게"), ("40mm", "75mm 이상", "두꺼운 판·평상 상판")])
    calc = _tbl(["조건", "값"], [("데크재 폭", "140mm + 틈 5mm"), ("장선 간격", "400mm"), ("1㎡에 지나가는 판", "약 7줄"), ("1㎡에 걸리는 장선", "약 3.5줄"),
                                 ("판 1줄·장선 1개마다", "피스 2개"), ("1㎡ 피스", "약 48~50개"), ("10㎡(약 3평)", "약 500개 = 500EA 한 통")])
    fq2 = [("데크 피스는 몇 mm를 쓰나요?", "판 두께의 약 2.2~2.5배가 기준입니다. 20mm 데크재는 50mm 안팎, 25mm는 50~65mm, 40mm는 75mm 이상을 많이 씁니다."),
           ("데크 1평에 피스가 몇 개 드나요?", "폭 140mm 데크재·장선 간격 400mm·판마다 2개씩 박는다고 하면 1㎡에 약 48~50개, 1평(약 3.3㎡)에 160개 안팎입니다. 장선 간격과 판 폭에 따라 달라져요."),
           ("방부목에는 어떤 피스가 좋나요?", "밖에 쓰는 방부목은 녹이 덜 슬도록 스텐 피스를 많이 씁니다. 아연 피스는 값이 싸서 실내나 비를 덜 맞는 곳에 씁니다."),
           ("합성데크도 피스로 박나요?", "합성데크는 보통 판 옆 홈에 끼우는 전용 클립과 스타터로 고정합니다. 두께(20T·25T)에 맞는 클립을 고르세요.")]
    body2 = f'''<section class="wrap sec"><p class="crumb"><a href="/">홈</a> › <a href="/gagyeok/deck-gagyeok.html">데크</a> › 데크 피스</p>
<h1>데크 피스 길이·개수 — 두께별 고르는 법과 1평 계산</h1>
<p class="lead">데크 피스는 판 두께에 맞는 길이를 고르고, 판 폭과 장선 간격으로 개수를 계산합니다. 매장에 있는 피스 규격과 기준가도 함께 정리했습니다.</p>
<div class="row"><a class="b r" href="/deck-gyesan.html">데크 수량 계산기</a><a class="b o" href="/bangbu-gyugyeok.html">방부목 규격</a><a class="b o" href="/bupum/">철물·공구·부속</a><a class="b d" href="tel:{tel}">전화 문의</a></div>
<h2>데크 두께별 피스 길이</h2>{sz}
<h2>1㎡에 피스 몇 개? (계산 예)</h2>{calc}
<p class="small muted">계산 예시입니다. 판 폭이 좁거나 장선 간격이 촘촘하면 더 들어가요. 넉넉히 10% 더 준비하세요.</p>
<h2>매장 피스·데크 클립 기준가</h2>{ptb}
<p class="small muted">매장 소매 기준가(부가세 별도)</p>
<h2>자주 묻는 질문</h2>{faqslide(fq2)}</section>''' + CTA
    page("deck-pis.html", "데크 피스 길이·개수 — 두께별 고르는 법과 1평 계산 | 영진목재",
         "데크 피스 몇 mm? 20T는 50mm 안팎, 25T는 50~65mm. 1㎡에 약 48~50개 계산 예와 매장 피스 기준가.", body2, jsonld=_fq(fq2))

    # ── 3. 아일랜드 식탁 사이즈 ──
    jp = [p for p in P if "집성" in p["name"] and re.search(r"(?:\*|@)\s*(?:18|24|30)T", p["name"])][:8]
    jtb = _tbl(["매장 품명", "기준가"], [(E(p["name"]), f"{p['price']:,}원~") for p in jp]) if jp else ""
    st = _tbl(["항목", "많이 쓰는 치수", "메모"],
              [("높이(식탁 겸 조리대)", "850~900mm", "싱크대 상판 높이에 맞추면 깔끔"), ("높이(바 테이블형)", "1,000~1,100mm", "높은 바 의자(좌판 약 750mm)와 함께"),
               ("깊이(한쪽만 앉을 때)", "600~700mm", ""), ("깊이(양쪽에 앉을 때)", "900mm 이상", ""), ("1인당 폭", "약 600mm", "3명이면 1,800mm"),
               ("무릎 공간(상판 돌출)", "250~300mm", "앉는 쪽 상판을 이만큼 내밀기"), ("둘레 통로", "900~1,000mm 이상", "냉장고·싱크대와의 간격")])
    fq3 = [("아일랜드 식탁 높이는 얼마가 좋나요?", "싱크대와 같은 850~900mm가 가장 많고, 바 의자를 쓰는 바 테이블형은 1,000~1,100mm로 합니다."),
           ("아일랜드 식탁 깊이·길이는요?", "한쪽만 앉으면 깊이 600~700mm, 양쪽에 앉으면 900mm 이상이 편합니다. 길이는 앉을 사람 수 × 약 600mm로 잡으세요."),
           ("상판은 어떤 자재로 만드나요?", "DIY로는 집성판 24~30T 상판을 많이 씁니다. 원하는 크기로 매장에서 재단해 드립니다.")]
    body3 = f'''<section class="wrap sec"><p class="crumb"><a href="/">홈</a> › <a href="/mandeul/">DIY 만들기</a> › 아일랜드 식탁 사이즈</p>
<h1>아일랜드 식탁 사이즈 — 높이·깊이·길이·통로 한눈에</h1>
<p class="lead">아일랜드 식탁을 짜거나 주문하기 전에 많이 쓰는 치수를 정리했습니다. 상판 자재는 집성판을 원하는 크기로 잘라 가실 수 있어요.</p>
<div class="row"><a class="b r" href="/cut.html">상판 재단 미리보기</a><a class="b o" href="/gagyeok/jipseong-gagyeok.html">집성판 가격</a><a class="b o" href="/yeongyeol/gagu.html">가구 시공팀 연결</a><a class="b d" href="tel:{tel}">전화 문의</a></div>
<h2>많이 쓰는 치수</h2>{st}
<p class="small muted">일반적으로 많이 쓰는 범위입니다. 주방 크기와 의자에 맞춰 조정하세요.</p>
{('<h2>상판용 집성판 기준가</h2>' + jtb + '<p class="small muted">매장 소매 기준가(부가세 별도) · 원하는 크기로 재단</p>') if jtb else ''}
<h2>자주 묻는 질문</h2>{faqslide(fq3)}</section>''' + CTA
    page("island-size.html", "아일랜드 식탁 사이즈 — 높이·깊이·길이·통로 한눈에 | 영진목재",
         "아일랜드 식탁 높이 850~900mm(바 테이블형 1,000~1,100mm), 깊이·1인당 폭·무릎 공간·통로 치수와 상판 집성판.", body3, jsonld=_fq(fq3))
