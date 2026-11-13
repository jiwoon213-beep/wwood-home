# 영림(YOUNGLIM) 도어·중문·몰딩/월/마루·인테리어 필름 — /younglim/ (회사 허락, 사진은 영림 S3 링크)
# 데이터 src/data/younglim.tsv: 목록코드|실제분류|pi_index|품번|이름|스타일코드|이미지파일 (.github/scripts/fetch_younglim.py 가 매일 갱신)
import os
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


def gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT, ALLFAQ=None):
    rows = load(ROOT)
    if not rows: return []
    nav = lambda cur: '<div class="glk tkn">' + "".join(f'<a href="/younglim/{p[0]}.html"{" class=on" if p[0] == cur else ""}>{E(p[1])}</a>' for p in PAGES) + '</div>'
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
                sec += f'<a class="yri" href="#" data-big="{im}" data-n="{E(n)}"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" src="{im}" alt="영림 {E(n)}"><span>{E(n)}</span></a>'
            sec += '</div>'
        fq = [(f"영림 {nm} 어디서 보고 주문하나요?", f"{ADDR} 영진종합목재(월드건축자재) 매장에서 상담·주문할 수 있습니다. {HOURS}. 크기를 재 오시면 맞는 규격을 찾아 드리고, 대전·세종은 설치 시공(월드아키텍쳐)도 상담합니다.")]
        body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › <a href="/younglim/">영림 도어·중문·마감재</a> › {E(nm)}</p><h1>영림 {E(nm)}</h1><p class="glead">{E(lead)} 총 {len(its)}가지.</p>{nav(slug)}{sec}'
                f'<p class="gs">영림(YOUNGLIM) 제품입니다. 사진을 누르면 크게 볼 수 있습니다. 색상·규격·가격·납기는 매장에 문의해 주세요.</p>'
                f'<h2 class="gt">고를 때 알아둘 것</h2><ul class="gtip">{"".join(f"<li>{E(t)}</li>" for t in tips)}</ul>'
                f'<div class="glk"><a href="/trend/">인테리어 트렌드</a><a href="/yerim/">예림 중문·도어</a><a href="/sigong.html">설치 시공 맡기기</a><a href="/visit.html">매장 길찾기</a></div></section>'
                f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{faqslide(fq)}</section>{CTA}' + LB)
        page(f"younglim/{slug}.html", f"영림 {nm} {len(its)}종 — 모던·내추럴·클래식 디자인 사진 | 대전 영진목재",
             f"영림 {nm} {len(its)}가지 사진. {lead} 대전 유성 영진종합목재 매장 상담·주문, 대전·세종 시공.", body, "/jaryo/", None, IMG(its[0][6]))
        out.append((slug, nm, lead, len(its), IMG(its[0][6])))
    cards = "".join(f'<a class="gi gim" href="/younglim/{s}.html"><img loading="lazy" referrerpolicy="no-referrer" src="{im}" alt=""><b>{E(n)} <small>{k}종</small></b><small>{E(l[:40])}</small></a>' for s, n, l, k, im in out)
    tot = sum(x[3] for x in out)
    page("younglim/index.html", f"영림 도어·중문·몰딩·월판넬·마루·인테리어 필름 {tot}종 | 대전 영진목재",
         f"영림(YOUNGLIM) 방문·중문·몰딩·스타일월·마루·인테리어 필름 {tot}가지를 종류별 사진으로. 대전 유성 영진종합목재 매장 상담·주문, 대전·세종 시공.",
         f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › 영림 도어·중문·마감재</p><h1>영림 도어·중문·마감재</h1><p class="glead">영림(YOUNGLIM) 방문·중문·몰딩·벽재·마루·인테리어 필름 {tot}가지를 종류별로 모았습니다. 마음에 드는 디자인을 골라 매장에 오시면 크기·색상·납기를 안내해 드립니다.</p><div class="gig">{cards}</div><div class="glk"><a href="/trend/">인테리어 트렌드</a><a href="/yerim/">예림 중문·도어</a><a href="/gagyeok/door-gagyeok.html">방문·문틀 기준가</a></div></section>{CTA}', "/jaryo/")
    return out
