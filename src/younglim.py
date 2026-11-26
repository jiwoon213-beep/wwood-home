# 영림(YOUNGLIM) 도어·중문·몰딩/월/마루·인테리어 필름 — /younglim/ (회사 허락, 사진은 영림 S3 링크)
# 데이터 src/data/younglim.tsv: 목록코드|실제분류|pi_index|품번|이름|스타일코드|이미지파일 (.github/scripts/fetch_younglim.py 가 매일 갱신)
import os, re
from yerim import LB

IMG = lambda f: "https://s3.ap-northeast-2.amazonaws.com/younglim-bucket/" + f
STY = {"1301": "모던", "1302": "내추럴", "1303": "클래식", "1304": "유니크", "1305": ""}
PAGES = [
 ("door-apel", "아펠 프리미엄 도어", ["030100"], "알루미늄 시스템 라인·프로스트 라인 등 고급 디자인 도어.", ["프리미엄 라인은 문틀·하드웨어까지 세트로 맞추면 완성도가 높습니다."]),
 ("door-abs", "ABS 도어", ["030300"], "물과 충격에 강해 욕실·방문으로 가장 많이 쓰는 ABS 도어. 엠보스·매트 등 디자인별.", ["욕실 문은 ABS를 권합니다.", "문 크기(폭×높이)와 벽 두께를 재 오시면 규격을 찾아 드립니다."]),
 ("door-membrane", "멤브레인 도어", ["030400"], "필름을 입힌 멤브레인 도어. 무늬·색상이 다양해 방문 디자인 선택 폭이 넓습니다.", ["욕실처럼 물이 직접 닿는 곳은 ABS가 낫습니다."]),
 ("door-tagong", "타공 도어", ["030500"], "문짝에 무늬 구멍(타공)이나 유리 창을 낸 디자인 도어.", ["타공·유리 부분으로 빛이 들어와 복도·드레스룸이 밝아집니다."]),
 ("door-special", "키즈·기능성 도어", ["030600", "030700"], "아이방 키즈 도어와 차음·방화·펫 등 기능성 도어.", ["아이방은 손 끼임 방지 경첩·스토퍼를 함께."]),
 ("door-hardware", "도어 하드웨어", ["030801"], "문 손잡이·도어락·경첩·스토퍼 등 도어 하드웨어.", ["문 두께와 손잡이 구멍(백셋) 거리를 확인하세요."]),
 ("door-frame", "도어 시스템·문틀", ["030900", "031000"], "미닫이·슬라이딩 도어 시스템과 문틀.", ["욕실은 물에 강한 PVC 문틀."]),
 ("jungmun", "슬라이딩·기타 중문", ["040100", "040700"], "현관 슬라이딩 중문과 스윙·원슬라이딩 등 다양한 중문.", ["현관 폭과 신발장 위치를 재 오시면 맞는 형태를 골라 드립니다."]),
 ("jungmun-yanggae", "양개 중문", ["040200"], "가운데서 양쪽으로 여는 양개(여닫이) 중문.", ["현관 폭이 넓을 때 잘 어울립니다."]),
 ("jungmun-slim", "슬림 알루미늄 중문", ["040300"], "프레임이 얇은 알루미늄 슬림 중문. 유리가 넓어 현관이 환해집니다.", ["3연동은 좁은 현관에서도 넓게 열립니다."]),
 ("jungmun-folding", "폴딩도어·파티션", ["040400", "040500"], "접어서 활짝 여는 폴딩도어와 공간을 나누는 파티션.", ["베란다·카페 테라스는 단열형 폴딩도어."]),
 ("jungmun-glass", "중문 유리 옵션", ["040600"], "중문에 넣는 무늬·컬러 유리 옵션.", ["같은 중문도 유리에 따라 분위기가 크게 달라집니다."]),
 ("jungmun-system", "중문 시스템·프레임", ["040800", "040900"], "중문 레일·자동·연동 시스템과 프레임.", ["자동 중문은 전기 배선 위치를 미리 확인하세요."]),
 ("molding", "몰딩·걸레받이", ["060101"], "천장 몰딩·걸레받이·문선 등 영림 몰딩.", ["몰딩 색은 문·문틀과 맞추면 깔끔합니다."]),
 ("wall", "스타일월·월판넬·벽장식", ["060300", "060500", "060601"], "벽에 붙이는 스타일월·월판넬과 벽장식 포인트.", ["거실 TV벽·침대 헤드벽에 포인트로."]),
 ("maru", "마루", ["060702"], "영림 마루 바닥재.", ["바닥 면적(평) × 3.3 = ㎡, 로스 5~10% 더해 주문합니다."]),
 ("film", "인테리어 필름", ["080100"], "가구·문·벽에 붙이는 영림 인테리어 필름(우드·솔리드·스톤·메탈 등).", ["필름 시공 전 프라이머를 바르면 잘 붙고 오래갑니다.", "샘플을 실제 조명 아래서 보고 고르세요."]),
]


def load(ROOT):
    p = os.path.join(ROOT, "data", "younglim.tsv")
    if not os.path.exists(p): return []
    import re
    rows = [l.rstrip("\n").split("|") for l in open(p, encoding="utf-8") if l.count("|") >= 6]
    for r in rows: r[4] = re.sub(r"\s{2,}", " · ", r[4]).strip()
    return rows


def card(r, alt_pre=""):
    nm = r[4] + (f" {r[3]}" if r[3] and r[3] not in r[4] else "")
    return nm, IMG(r[6])



# 페이지별 추가 FAQ — 구글 검색어(영림 중문·영림도어·멤브레인·타공 도어 등, 2026-11-22)
XFQ2 = {
 "film": [("영림 인테리어 필름 색상은 어떻게 고르나요?", "같은 색이라도 화면과 실물이 달라 보입니다. 매장에서 실물 샘플을 보고, 붙일 곳(문·몰딩·싱크대)의 조명 아래에서 비교해 고르는 것이 좋습니다."), ("영림 필름 품번(예: PW974·PS102)으로 찾을 수 있나요?", "네. 제품 사진 아래 품번이 적혀 있고, 품번을 알려 주시면 매장에서 같은 제품을 찾아 드립니다. 영림 216처럼 숫자로 부르는 색도 품번으로 확인합니다."), ("인테리어 필름 셀프 시공 순서는?", "기존 면 세척 → 샌딩·퍼티 → 프라이머 → 필름 붙이기 → 모서리 정리 순서입니다. 자세한 순서는 /qna/ 의 필름 시공 글을 참고하세요.")],
 "jungmun-system": [("영림 중문 종류는 어떻게 나뉘나요?", "슬라이딩(원슬라이딩), 양개, 3연동 슬림, 폴딩 등으로 나뉩니다. 전체 디자인은 /younglim/jungmun-all.html 에서 종류별로 볼 수 있습니다."), ("영림 중문 가격은 얼마인가요?", "크기·유리·프레임 색에 따라 달라 매장에서 견적을 드립니다. 현관 가로·세로·높이를 재 오시면 빠릅니다."), ("자동 중문은 전기 공사가 필요한가요?", "자동 중문은 전원이 필요하니 설치 위치 근처 전기 배선을 미리 확인합니다.")],
 "door-abs": [("ABS 도어는 욕실에만 쓰나요?", "물에 강해 욕실 문에 많이 쓰지만 방문에도 씁니다."), ("ABS 도어와 멤브레인 도어 차이는?", "멤브레인은 MDF에 필름을 씌운 문, ABS는 겉을 ABS 수지로 감싸 물·습기에 더 강합니다(/qna/abs-door-ran.html).")],
 "door-apel": [("영림 도어 사이즈는 어떻게 재나요?", "문틀 안쪽 폭과 높이를 위·가운데·아래 여러 곳 재서 가장 작은 값을 기준으로 알려 주시면 맞는 규격을 찾아 드립니다.")],
 "jungmun-yanggae": [("양개 중문은 현관 폭이 얼마나 되어야 하나요?", "문 두 짝이 양쪽으로 열리므로 현관 폭이 넉넉한 곳에 어울립니다. 정확한 가능 여부는 현관 치수를 재서 매장에서 확인합니다.")],
 "wall": [("영림 월패널은 어떻게 붙이나요?", "제품마다 전용 부자재와 붙이는 방식이 다르니, 벽 바탕 상태(석고보드·콘크리트)를 알려 주시면 맞는 방법을 안내해 드립니다.")],
 "molding": [("영림 몰딩 종류는?", "천장몰딩, 걸레받이, 문선, 평몰딩 등이 있습니다. 차이는 /bigyo/molding-types.html 에 정리했습니다.")],
 "maru": [("강마루와 강화마루 차이는?", "강마루는 바닥에 본드로 붙이고, 강화마루는 끼워 맞춰 띄워 깝니다(/bigyo/kangmaru-vs-kanghwa.html).")],
}
XFQ = {
    "jungmun": [("영림 슬라이딩 도어는 어떤 종류가 있나요?", "벽 쪽으로 밀어 여는 원슬라이딩, 레일을 숨긴 히든 슬라이딩, 거울을 붙인 미러 히든 슬라이딩, 손잡이 없이 누르는 히든 푸시 슬라이딩 등이 있습니다(/qna/hidden-sliding-door.html).")],
    "jungmun-slim": [("슬림 중문은 일반 중문과 무엇이 다른가요?", "프레임(알루미늄 테두리)이 얇아 유리 면이 넓게 보여 현관이 넓고 밝아 보입니다. 유리 종류는 '중문 유리 옵션'(/younglim/jungmun-glass.html)에서 볼 수 있습니다.")],
    "door-membrane": [("멤브레인 도어는 어떤 문인가요?", "MDF 판을 성형한 뒤 필름을 진공 압착한 문으로 몰딩·무늬 디자인이 다양합니다. ABS 도어와의 차이는 '실내 도어 비교'(/bigyo/door-types.html)에 있습니다.")],
    "door-tagong": [("타공 도어는 무엇인가요?", "문짝에 유리·장식 구멍(타공)을 낸 디자인 문입니다. 빛이 들어와 복도·드레스룸 문에 많이 쓰며, 유리 종류는 사틴·모루 등으로 고릅니다(/qna/satin-yuri.html).")],
    "door-hardware": [("영림 도어 손잡이는 문짝과 따로 고르나요?", "네, 문짝 디자인과 색에 맞춰 손잡이·경첩·도어스토퍼를 따로 고릅니다. 기존 문 손잡이 교체는 '방문 손잡이 교체'를 참고하세요(/qna/mun-cylinder.html).")],
}

def gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT, ALLFAQ=None):
    rows = load(ROOT)
    if not rows: return []
    nav = lambda cur: '<div class="glk tkn"><a href="/younglim/jungmun-all.html"' + (' class=on' if cur == 'jungmun-all' else '') + '>중문 전체</a>' + "".join(f'<a href="/younglim/{p[0]}.html"{" class=on" if p[0] == cur else ""}>{E(p[1])}</a>' for p in PAGES) + '</div>'
    out = []
    for slug, nm, codes, lead, tips in PAGES:
        its = [r for r in rows if r[0] in codes]
        if not its: continue
        groups = {}
        for r in its: groups.setdefault(STY.get(r[5], ""), []).append(r)
        order = [g for g in ("모던", "내추럴", "클래식", "유니크", "") if g in groups]
        sec = ""
        for g in order:
            xs = groups[g]
            sec += f'<h2 class="gt">{(E(g) + " 스타일 ") if g else ("기타 " if len(order) > 1 else "")}{len(xs)}가지 <small>옆으로 넘겨 보세요 ›</small></h2><div class="yrg">'
            for r in xs:
                n, im = card(r)
                sec += f'<a class="yri" href="#" data-big="{im}" data-n="{E(n)}"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" width="300" height="300" src="{im}" alt="영림 {E(n)}"><span>{E(n)}</span></a>'
            sec += '</div>'
        fq = [(f"영림 {nm} 어디서 보고 주문하나요?", f"{ADDR} 영진종합목재(월드건축자재) 매장에서 상담·주문할 수 있습니다. {HOURS}. 크기를 재 오시면 맞는 규격을 찾아 드리고, 대전·세종은 설치 시공(월드아키텍쳐)도 상담합니다.")]
        fq += XFQ.get(slug, [])
        fq += [x for x in XFQ2.get(slug, []) if x[0] not in {q for q, _ in fq}]
        body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › <a href="/younglim/">영림 도어·중문·마감재</a> › {E(nm)}</p><h1>영림 {E(nm)}</h1><p class="glead">{E(lead)} 총 {len(its)}가지.</p>' + ('<p class="glead"><a class="b r" href="/younglim/jungmun-all.html">영림 중문 디자인 전체(슬라이딩·양개·3연동·폴딩) 보기 ›</a></p>' if slug == 'jungmun-system' else '') + f'{nav(slug)}{sec}'
                f'<p class="gs">영림(YOUNGLIM) 제품입니다. 사진을 누르면 크게 볼 수 있습니다. 색상·규격·가격·납기는 매장에 문의해 주세요.</p>'
                f'<h2 class="gt">고를 때 알아둘 것</h2><ul class="gtip">{"".join(f"<li>{E(t)}</li>" for t in tips)}</ul>'
                f'<div class="glk"><a href="/trend/">인테리어 트렌드</a><a href="/yerim/">예림 중문·도어</a><a href="/sigong.html">설치 시공 맡기기</a><a href="/visit.html">매장 길찾기</a></div></section>'
                f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{faqslide(fq)}</section>{CTA}' + LB)
        page(f"younglim/{slug}.html", (f"영림 중문 레일·자동·연동 시스템과 프레임 {len(its)}종 — 중문 부속 사진 | 대전 영진목재" if slug == "jungmun-system" else f"영림 {nm} {len(its)}종 — 모던·내추럴·클래식 디자인 사진 | 대전 영진목재"),
             f"영림 {nm} {len(its)}가지 사진. {lead} 대전 유성 영진종합목재 매장 상담·주문, 대전·세종 시공.", body, "/jaryo/", {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in fq]}, IMG(its[0][6]))
        out.append((slug, nm, lead, len(its), IMG(its[0][6])))
    # 영림 중문 종류 총정리(허브) — '영림 중문' 검색용
    JM = [p for p in PAGES if p[0].startswith("jungmun") and p[0] not in ("jungmun-glass", "jungmun-system")]
    jsec = ""; jtot = 0
    for slug, nm, codes, lead, tips in JM:
        its = [r for r in rows if r[0] in codes]
        if not its: continue
        jtot += len(its)
        prev = "".join(f'<a class="yri" href="/younglim/{slug}.html"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" width="300" height="300" src="{card(r)[1]}" alt="영림 {E(card(r)[0])}"><span>{E(card(r)[0])}</span></a>' for r in its[:8])
        jsec += (f'<h2 class="gt"><a href="/younglim/{slug}.html">영림 {E(nm)} {len(its)}종 ›</a></h2><p class="gs">{E(lead)} {E(" ".join(tips[:1]))}</p><div class="yrg">{prev}</div>')
    if jsec:
        jfq = [("영림 중문은 어떤 종류가 있나요?", "현관 폭과 여는 방식에 따라 슬라이딩(원슬라이딩·스윙), 가운데서 양쪽으로 여는 양개, 프레임이 얇은 슬림 알루미늄(3연동 등), 접어서 여는 폴딩도어가 있습니다. 같은 중문도 유리 옵션에 따라 분위기가 달라집니다."),
               ("우리 집 현관에는 어떤 중문이 맞나요?", "현관 폭이 좁으면 문이 겹쳐 열리는 3연동 슬림·원슬라이딩, 넓으면 양개 중문이 잘 어울립니다. 신발장 위치와 현관 바닥 턱 높이에 따라 달라지니 현관 가로·세로·높이를 재 오시면 맞는 제품을 골라 드립니다."),
               ("영림 중문 가격은 얼마인가요?", "중문은 크기·유리·프레임 색에 따라 가격이 크게 달라 매장에서 견적을 드립니다. 현관 치수와 원하는 디자인 사진을 가져오시면 바로 비교해 드립니다."),
               ("영림 중문 설치도 해 주나요?", f"대전·세종은 설치 시공까지 상담해 드립니다. {ADDR} 영진종합목재(월드건축자재) 매장, {HOURS}.")]
        page("younglim/jungmun-all.html", f"영림 중문(영림도어 중문) 종류 총정리 — 슬라이딩·양개·3연동·폴딩 {jtot}종 사진 | 대전 영진목재",
             f"영림 중문 {jtot}가지를 종류별 사진으로: 슬라이딩·원슬라이딩, 양개 중문, 3연동 슬림 알루미늄, 폴딩도어. 현관 폭에 맞는 중문 고르는 법과 대전 유성 영진종합목재 매장 상담·설치.",
             f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › <a href="/younglim/">영림 도어·중문·마감재</a> › 영림 중문 전체</p><h1>영림 중문 종류 총정리</h1>'
             f'<p class="glead">영림(YOUNGLIM) 현관 중문 {jtot}가지를 종류별로 모았습니다. 현관이 좁으면 3연동 슬림·원슬라이딩, 넓으면 양개 중문이 잘 어울립니다. 사진을 누르면 종류별 전체 목록으로 갑니다.</p>{nav("")}{jsec}'
             f'<div class="glk"><a href="/younglim/jungmun-glass.html">중문 유리 옵션</a><a href="/younglim/jungmun-system.html">중문 시스템·프레임</a><a href="/sigongbeop/jungmun.html">원슬라이딩 중문 셀프 설치</a><a href="/yerim/">예림 중문</a><a href="/apt/">아파트별 자재</a><a href="/visit.html">매장 길찾기</a></div></section>'
             f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{faqslide(jfq)}</section>{CTA}', "/jaryo/",
             {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in jfq]})
        out.insert(0, ("jungmun-all", "중문 전체(종류별)", "슬라이딩·양개·3연동 슬림·폴딩 중문을 한눈에", jtot, IMG([r for r in rows if r[0] in JM[0][2]][0][6])))
    cards = "".join(f'<a class="gi gim" href="/younglim/{s}.html"><img loading="lazy" referrerpolicy="no-referrer" src="{im}" alt=""><b>{E(n)} <small>{k}종</small></b><small>{E(l[:40])}</small></a>' for s, n, l, k, im in out)
    tot = sum(x[3] for x in out)
    page("younglim/index.html", f"영림 도어·중문·몰딩·월판넬·마루·인테리어 필름 {tot}종 | 대전 영진목재",
         f"영림(YOUNGLIM) 방문·중문·몰딩·스타일월·마루·인테리어 필름 {tot}가지를 종류별 사진으로. 대전 유성 영진종합목재 매장 상담·주문, 대전·세종 시공.",
         f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › 영림 도어·중문·마감재</p><h1>영림 도어·중문·마감재</h1><p class="glead">영림(YOUNGLIM) 방문·중문·몰딩·벽재·마루·인테리어 필름 {tot}가지를 종류별로 모았습니다. 마음에 드는 디자인을 골라 매장에 오시면 크기·색상·납기를 안내해 드립니다.</p><div class="gig">{cards}</div><div class="glk"><a href="/trend/">인테리어 트렌드</a><a href="/yerim/">예림 중문·도어</a><a href="/gagyeok/door-gagyeok.html">방문·문틀 기준가</a></div></section>{CTA}', "/jaryo/")
    return out
