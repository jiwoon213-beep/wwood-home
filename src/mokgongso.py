# '근처 목공소', '목재 재단 해주는 곳', 'plywood near me' 검색용 안내 페이지(/mokgongso.html)
# 숫자는 재단비 페이지(jaedan-bi)·매장 정보에 이미 있는 것만 씀.

FQ = [
    ("목공소처럼 나무를 원하는 크기로 잘라 주나요?", "네. 합판·MDF·집성판·OSB·석고보드·구조재 등 매장에서 산 자재를 원하는 크기로 바로 잘라 드립니다. 1컷당 재단비는 두께에 따라 12T 이하 1,000원부터입니다(부가세 별도)."),
    ("가구나 붙박이장 제작도 하나요?", "매장에서는 자재 판매와 재단을 합니다. 가구·붙박이장 제작이나 목공 시공은 매장에 접수하시면 대전·세종·공주·계룡·금산·옥천·천안·청주 지역 목공 시공팀을 연결해 드립니다."),
    ("가져온 나무도 잘라 주나요?", "매장 사정에 따라 다르니 전화(042-545-2900)로 먼저 물어봐 주세요."),
    ("몇 컷인지, 재단비가 얼마인지 미리 알 수 있나요?", "재단 미리보기에 자재와 크기를 넣으면 원판에서 자르는 그림, 컷 수, 재단비, 자재비 합계가 바로 나옵니다. 그 화면을 매장에 보여 주시면 그대로 잘라 드립니다."),
    ("잘라서 배송도 되나요?", "네. 재단한 뒤 대전·세종 인근은 배송, 그 밖의 지역은 전국 용달로 보내 드립니다(운임은 견적)."),
]

ROWS = [("12T 이하", "1,000원", "합판 4.8·8.5·11.5T, MDF 9T, 석고보드 9.5T"),
        ("15T·18T", "1,500원", "합판 15·17.5T, MDF 15·18T, 집성판 18T, OSB 18T"),
        ("20T 이하", "2,000원", "1×4 구조재(19T), 데크재 19·20T"),
        ("24T 이하", "2,500원", "집성판·원목 판재 24T"),
        ("30T 이하", "3,000원", "집성판 30T, 데크재 25T, 다루끼 30각"),
        ("30T 넘음", "전화 문의", "2×4·2×6·4×4 구조재·각재")]


def gen(page, E, CTA, faqslide, TEL, ADDR, HOURS):
    t = "".join(f"<tr><td>{a}</td><td><b>{b}</b></td><td>{c}</td></tr>" for a, b, c in ROWS)
    body = f'''<section class="wrap sec"><p class="crumb"><a href="/">홈</a> › <a href="/jaedan-bi.html">목재 재단</a> › 근처 목공소</p>
<h1>근처 목공소 찾으세요? 대전 목재 재단</h1>
<p class="lead">나무를 원하는 크기로 잘라 줄 곳을 찾는다면, 대전 영진종합목재에서 자재를 고르고 그 자리에서 잘라 가세요. 합판·MDF·집성판·OSB·석고보드·구조재까지 3000평 매장에서 바로 고르고 즉석 재단합니다.</p>
<div class="row"><a class="b r" href="/cut.html">재단 미리보기(크기 넣으면 컷 수·재단비)</a><a class="b o" href="tel:{TEL.replace('-', '')}">전화 {TEL}</a><a class="b d" href="/visit.html">매장 길찾기</a></div>
<h2>목공소 대신 이렇게 하면 됩니다</h2>
<ul class="mgl"><li><b>판재·각재 자르기</b><span>매장에서 산 자재를 원하는 크기로 바로 재단</span></li><li><b>미리 계산</b><span><a href="/cut.html">재단 미리보기</a>에 크기를 넣고 그 화면을 매장에 보여 주기</span></li><li><b>DIY 도안</b><span>선반·책장·평상·벤치 등 <a href="/mandeul/">DIY 만들기</a> 재단 목록 그대로 주문</span></li><li><b>가구·목공 시공</b><span>직접 만들기 어렵다면 <a href="/yeongyeol/mokgong.html">목공 시공팀 연결</a>(매장 접수)</span></li></ul>
<h2>두께별 1컷 재단비</h2>
<div class="tw"><table><tr><th>두께</th><th>1컷</th><th>이런 자재</th></tr>{t}</table></div>
<p class="small muted">부가세 별도 · 자세한 예시는 <a href="/jaedan-bi.html">합판·목재 재단비</a></p>
<h2>많이 자르는 자재</h2>
<div class="row"><a class="b o" href="/gagyeok/hapan-gagyeok.html">합판 가격</a><a class="b o" href="/gagyeok/mdf-gagyeok.html">MDF 가격</a><a class="b o" href="/gagyeok/jipseong-gagyeok.html">집성판 가격</a><a class="b o" href="/gagyeok/osb-gagyeok.html">OSB 가격</a><a class="b o" href="/gagyeok/gakjae-gagyeok.html">각재 가격</a><a class="b o" href="/gagyeok/seokgo-gagyeok.html">석고보드 가격</a><a class="b o" href="/tteori/">떨이몰(자투리·재고)</a></div>
<h2>매장 위치·시간</h2>
<p>{ADDR} · {HOURS}<br>대전 유성·서구·대덕·중구·동구, 세종, 공주, 계룡, 논산, 금산, 옥천에서 오시기 편합니다.</p>
<h2>Plywood &amp; lumber cutting in Daejeon</h2>
<p lang="en">Looking for plywood or lumber near you in Daejeon, Korea? Yeongjin Lumber sells plywood, MDF, OSB, glulam boards and studs, and cuts them to your size on the spot. Address: 44 Yuseong-daero, Daejeon. Tel {TEL}.</p>
<h2>자주 묻는 질문</h2>{faqslide(FQ)}</section>''' + CTA
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FQ]}
    page("mokgongso.html", "근처 목공소 찾으세요? 대전 목재 재단 — 합판·집성판 원하는 크기로 | 영진목재",
         "나무 잘라 주는 곳을 찾는다면 대전 영진목재. 합판·MDF·집성판·구조재를 고르고 즉석 재단, 1컷 1,000원부터(부가세 별도).", body, jsonld=ld)
