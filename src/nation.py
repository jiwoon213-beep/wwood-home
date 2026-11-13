# 전국 배송 지역 페이지 — 재단해서 용달로 (오프라인 3000평 매장 + 전국 용달) — /jeonguk/
# 확인 안 된 숫자(거리·운임·소요시간) 금지. 운임은 견적.
import re
from urllib.parse import quote

REG = [  # slug, 이름, 주요 지역, 많이 쓰는 곳, 사례 키워드
 ("seoul", "서울", "강남·서초·송파·강동·마포·영등포·성동·노원·은평 등 25개 구", "아파트·상가 인테리어 목공, 카페·매장 공사, 원룸 리모델링", r"서울"),
 ("gyeonggi-south", "경기 남부", "수원·용인·화성·평택·안산·오산·안성·이천·여주·광주", "전원주택 데크, 창고·공장 칸막이, 상가 인테리어", r"이천|용인|화성|평택|수원|경기"),
 ("gyeonggi-north", "경기 북부", "고양·파주·김포·의정부·남양주·양주·포천·가평·양평", "전원주택·펜션 데크, 목조 창고·온실, 카페 인테리어", r"파주|양평|가평|남양주|경기"),
 ("incheon", "인천", "남동·부평·연수·서구·계양·미추홀·강화", "아파트 리모델링, 공장·물류창고 보수, 강화 전원주택", r"인천|강화"),
 ("gangwon", "강원", "춘천·원주·강릉·속초·홍천·평창·횡성·양양", "펜션·전원주택 데크와 내장 루바, 목조 주택", r"강원|춘천|원주|강릉|홍천"),
 ("chungbuk", "충북", "충주·제천·음성·진천·괴산·보은·영동 (청주는 별도 안내)", "농가 창고·전원주택, 공장 보수", r"충북|충주|제천|음성|진천"),
 ("chungnam", "충남", "서산·당진·홍성·보령·부여·서천·예산·태안 (천안·아산·공주·논산은 별도 안내)", "전원주택 데크, 농가 창고, 펜션", r"충남|서산|당진|홍성|보령|부여|태안"),
 ("jeonbuk", "전북", "전주·익산·군산·정읍·완주·무주·진안", "한옥 보수·데크·평상, 전원주택", r"전북|전주|익산|군산"),
 ("gwangju-jeonnam", "광주·전남", "광주 5개 구, 여수·순천·목포·광양·나주·담양", "아파트·상가 인테리어, 펜션·조경 데크", r"광주|전남|여수|순천|목포"),
 ("daegu-gyeongbuk", "대구·경북", "대구 수성·달서·북구, 포항·구미·경주·안동·김천·경산", "아파트 리모델링, 공장 보수, 한옥·전원주택", r"대구|경북|포항|구미|경주|안동"),
 ("busan-gyeongnam", "부산·울산·경남", "부산 해운대·기장·강서, 울산, 창원·김해·진주·양산·거제·통영", "상가·카페 인테리어, 조선소 인근 공장·숙소 보수, 데크", r"부산|울산|경남|창원|김해|진주"),
 ("jeju", "제주", "제주시·서귀포", "펜션·카페·전원주택 데크와 내장재", r"제주"),
]
PX = [("합판 12mm 내수 4×8", r"4\*8 @12mm\(내수/A급\)"), ("OSB 11.1mm 4×8", r"OSB 4\*8 @ 11.1"), ("MDF 15mm 4×8", r"^MDF 4\*8 @15mm"),
      ("구조재 2×4", r"Ⅱ 2\* 4"), ("방부목 데크 25×140", r"25\*140"), ("미송 집성판 18T", r"미송.*18T")]


def gen(page, E, CTA, faqslide, TEL, EMAIL, ADDR, HOURS, CASES, top, vsplit, P):
    rows = []
    for nm, rx in PX:
        hit = sorted([p for p in P if re.search(rx, p["name"])], key=lambda p: p["price"])
        if hit: rows.append((nm, hit[0]["price"]))
    ptab = ('<table class="rt"><thead><tr><th>자재</th><th>소매 기준가(부가세 별도)</th></tr></thead><tbody>' + "".join(f'<tr><td>{E(n)}</td><td>{p:,}원~</td></tr>' for n, p in rows) + '</tbody></table>') if rows else ""
    vs = top(lambda v: re.search(r"재단|합판|데크|방부목|구조재", v["title"]), 8)
    out = []
    for slug, nm, cities, uses, crx in REG:
        jeju = slug == "jeju"
        cs = [c for c in CASES if re.search(crx, c["title"])][:3]
        mail = "mailto:" + EMAIL + "?subject=" + quote(f"{nm} 배송 견적 요청") + "&body=" + quote("품목·규격·수량:\n재단 크기(있으면):\n받는 주소:\n받는 분 연락처:\n희망 날짜:\n")
        ship = ("제주는 육지 용달이 바로 갈 수 없어 화물 배편을 이용합니다. 운임·도착 일정은 품목·수량을 보고 따로 상담해 드립니다."
                if jeju else f"{nm}까지는 용달(화물차)로 보내 드립니다. 운임은 거리·차량 크기·수량에 따라 달라 주문 전에 먼저 알려 드리고, 입금 확인 후 재단·상차해 출고합니다.")
        fq = [(f"대전 목재상에서 {nm}까지 보내 주나요?", ship),
              (f"{nm} 운임은 얼마인가요?", "정해진 금액이 없습니다. 품목·수량·받는 주소를 알려 주시면 사무실에서 운임을 먼저 견적 드립니다. 여러 품목을 한 번에 모으면 운임 부담이 줄어듭니다."),
              ("원하는 크기로 재단해서 보내 주나요?", "네. 3000평 매장에 쌓인 원자재를 원하는 치수로 재단한 뒤 보냅니다. 재단 미리보기(/cut.html)에서 그림을 만들어 메일로 보내 주시면 정확합니다."),
              ("사진만 보고 사기 불안한데요?", "유튜브 '월드건축자재DIY'에 매장과 자재가 그대로 나옵니다. 영상 통화나 사진으로 실물 상태를 보여 드릴 수도 있습니다(전화 상담)."),
              ("사업자 회원가가 있나요?", "사업자등록증·명함 확인 후 도매회원(wwood.kr)으로 가입하시면 회원가로 주문하실 수 있습니다.")]
        csec = ('<h2 class="gt">이 지역 시공·납품 사례</h2><ul class="gtip">' + "".join(f'<li><a href="/sigong/{c["slug"]}.html">{E(c["title"])}</a></li>' for c in cs) + '</ul>') if cs else ""
        body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/baesong.html">전국 배송</a> › {E(nm)}</p><h1>{E(nm)} 목재 배송 — 대전 3000평 목재소에서 재단해서 보내 드립니다</h1>'
                f'<p class="glead">{E(nm)}({E(cities)})에서 합판·OSB·MDF·구조재·방부목·데크재·집성판·석고보드·몰딩·도어가 필요하시면, 대전 유성 영진종합목재(월드건축자재) 3000평 매장에서 원하는 크기로 재단해 {"화물 배편" if jeju else "용달"}로 보내 드립니다. 이 지역에서는 주로 {E(uses)}에 많이 씁니다.</p>'
                f'<div class="row"><a class="b r" href="{mail}">메일로 배송 견적 요청</a><a class="b d" href="tel:{TEL.replace("-", "")}">전화 {TEL}</a><a class="b o" href="/cut.html">재단 그림 만들기</a></div>'
                f'<h2 class="gt">왜 대전에서 받아요?</h2><ul class="gtip"><li>오프라인 3000평 매장 — 합판·구조재·방부목·데크·집성·몰딩·도어를 한곳에서 모아 한 번에 보냅니다.</li><li>원하는 크기로 재단해서 보내 현장에서 자를 일이 줄어듭니다.</li><li>유튜브 영상 1,200여 편에 매장·자재·시공이 그대로 나와 실물을 미리 볼 수 있습니다.</li></ul>'
                f'<h2 class="gt">배송 방법</h2><p>{E(ship)}</p><ol class="gtip"><li>품목·규격·수량·재단 크기·받는 주소를 전화나 메일로 보내 주세요.</li><li>자재값과 운임을 먼저 알려 드립니다.</li><li>입금 확인 후 재단·상차하고 출고합니다.</li></ol>'
                f'<h2 class="gt">자주 보내는 자재 기준가</h2>{ptab}<p class="gs">소매 기준가(부가세 별도) · 운임 별도 · 규격·수량에 따라 다릅니다. <a href="/price.html">전체 기준가</a></p>'
                f'<div class="qk"><a href="/gagyeok/hapan-gagyeok.html">합판 1평에 얼마</a><a href="/gagyeok/deck-gagyeok.html">데크 1평에 얼마</a><a href="/gagyeok/gakjae-gagyeok.html">구조재·각재</a><a href="/gagyeok/seokgo-gagyeok.html">석고보드</a><a href="/mandeul/">DIY 재단 목록</a><a href="/younglim/">영림 도어·중문</a><a href="/yerim/">예림 중문</a></div>'
                f'{csec}</section>'
                + (f'<section class="wrap sec"><h2>매장·재단 영상</h2>{vsplit(vs, "h3")}</section>' if vs else "")
                + f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{faqslide(fq)}</section>'
                + f'<section class="wrap sec"><p class="small">다른 지역: {" · ".join(f"<a href=/jeonguk/{r[0]}.html>{E(r[1])}</a>" for r in REG if r[0] != slug)} · <a href="/cheongju.html">청주</a> · <a href="/cheonan-asan.html">천안·아산</a> · <a href="/daejeon.html">대전</a> · <a href="/sejong.html">세종</a></p></section>{CTA}')
        ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}
        page(f"jeonguk/{slug}.html", f"{nm} 목재 배송 — 합판·구조재·방부목 재단해서 {'배편으로' if jeju else '용달로'} | 대전 영진목재 3000평",
             f"{nm}({cities[:40]}) 목재·건축자재 배송. 대전 3000평 매장에서 원하는 크기로 재단해 {'화물 배편' if jeju else '용달'}로 보내 드립니다. 운임 견적 {TEL}.", body, "", ld)
        out.append((slug, nm, cities))
    cards = "".join(f'<a class="gi" href="/jeonguk/{s}.html"><b>{E(n)}</b><small>{E(c[:44])}</small></a>' for s, n, c in out)
    page("jeonguk/index.html", "전국 목재 배송 지역 — 서울·경기·강원·영남·호남·제주까지 재단해서 보내 드립니다 | 대전 영진목재",
         "대전 3000평 목재소 영진목재에서 합판·구조재·방부목·데크재를 원하는 크기로 재단해 전국 용달로 보내 드립니다. 지역별 배송 안내.",
         f'<section class="wrap sec gg"><h1>전국 목재 배송 지역</h1><p class="glead">유튜브로 보고 연락 주시는 분들이 전국에 계십니다. 대전 3000평 매장에서 원하는 크기로 재단해 용달로 보내 드립니다. 지역을 고르세요.</p><div class="gig">{cards}</div><div class="glk"><a href="/baesong.html">배송 방법 자세히</a><a href="/cut.html">재단 미리보기</a><a href="/price.html">기준가</a></div></section>{CTA}', "")
    return out
