# 지역 × 시공 서비스 페이지 (대전 중문, 세종 방문 교체 …) — /local/
# 시공은 월드아키텍쳐(대전·세종). 확인 안 된 숫자(시공비·소요일·거리) 쓰지 않음.
import re, os
import younglim as _yl, shenu as _sh
from yerim import IMG as YIMG, LB

REG = [  # slug, 이름, 동네들
 ("daejeon", "대전", "유성·서구·중구·동구·대덕구 대전 전 지역"),
 ("yuseong", "대전 유성구", "도안·학하·노은·관평·반석·신성·원내동(진잠)"),
 ("seogu", "대전 서구", "둔산·탄방·가수원·관저·도안·정림·월평"),
 ("daedeok", "대전 대덕구", "신탄진·송촌·법동·오정·대화동"),
 ("junggu-donggu", "대전 중구·동구", "은행·대흥·문화·유천·태평·가양·용전·판암·가오동"),
 ("sejong", "세종", "보람·도담·새롬·다정·나성·종촌·고운·아름·반곡·해밀·조치원"),
]
SVC = [  # slug, 이름, 검색 꼬리, 설명, 순서, 자재 링크, 갤러리 소스, 영상 정규식, 사례 정규식
 ("jungmun", "중문 설치·교체", "3연동·슬라이딩·간살 중문 시공",
  "현관 중문을 새로 달거나 바꿉니다. 3연동·원슬라이딩·여닫이·간살·자동 중문 중 현관 폭과 신발장 위치에 맞는 형태를 고르고, 영림·예림·쉐누 제품 중에서 디자인을 고르실 수 있습니다.",
  ["현관 폭·높이·신발장 위치 실측", "형태(3연동·슬라이딩·여닫이)와 유리·색상 선택", "제품 주문(주문 제작)", "프레임 고정·문짝 설치·마감 실리콘"],
  [("/yerim/jungmun-slim.html", "예림 3연동 중문"), ("/younglim/jungmun-slim.html", "영림 슬림 중문"), ("/shenu/jungmun.html", "쉐누 중문"), ("/trend/", "인테리어 트렌드")],
  "jungmun", r"중문", r"중문"),
 ("door", "방문·문틀 교체", "ABS·멤브레인 방문, 욕실문·문틀 교체 시공",
  "오래된 방문과 욕실문, 문틀을 새것으로 바꿉니다. 욕실은 물에 강한 ABS 도어와 PVC 문틀, 방은 멤브레인·ABS·글래스 도어 중에서 고르실 수 있습니다.",
  ["문 폭·높이·벽 두께 실측", "문짝·문틀·손잡이 디자인 선택", "기존 문·문틀 철거", "새 문틀 고정·문짝 달기·몰딩 마감"],
  [("/gagyeok/door-gagyeok.html", "방문·문틀 기준가"), ("/younglim/door-abs.html", "영림 ABS 도어"), ("/yerim/door-abs.html", "예림 ABS 도어"), ("/shenu/door-abs.html", "쉐누 ABS 도어")],
  "door", r"문 ?교체|방문|욕실문|문틀|ABS", r"문 교체|문틀"),
 ("film", "인테리어 필름 시공", "방문·문틀·싱크대·붙박이장 필름 리폼",
  "문·문틀·싱크대·붙박이장·몰딩에 인테리어 필름을 붙여 새것처럼 바꿉니다. 철거 없이 색과 무늬만 바꿔 공사가 간단합니다.",
  ["붙일 곳과 면적 확인", "필름 색·무늬 선택(샘플 확인)", "표면 정리·프라이머", "필름 부착·모서리 마감"],
  [("/gagyeok/interior-film.html", "인테리어 필름 기준가"), ("/younglim/film.html", "영림 인테리어 필름"), ("/sigongbeop/film-sigong.html", "필름 시공법")],
  "film", r"필름", r"필름"),
 ("molding", "몰딩·걸레받이 교체", "천장 몰딩·걸레받이·문선 교체",
  "누렇게 변하거나 들뜬 천장 몰딩·걸레받이·문선을 바꿉니다. 요즘은 얇은 몰딩이나 마이너스 몰딩으로 깔끔하게 마감하는 경우가 많습니다.",
  ["교체할 길이 실측", "몰딩 모양·색 선택", "기존 몰딩 철거", "새 몰딩 부착·코너 마감"],
  [("/gagyeok/molding-gagyeok.html", "몰딩·걸레받이 기준가"), ("/younglim/molding.html", "영림 몰딩"), ("/shenu/molding.html", "쉐누 PVC 몰딩")],
  "molding", r"몰딩|걸레받이", r"몰딩"),
 ("wall", "템바보드·간살 포인트 벽", "거실·침실 템바보드·루바 포인트 월",
  "거실 TV벽·침대 헤드벽·현관 벽에 템바보드·간살·루바·월판넬로 포인트를 줍니다.",
  ["벽 크기 실측·콘센트 위치 확인", "템바보드·루바·월판넬 선택", "하지 작업(필요 시)", "부착·마감"],
  [("/gagyeok/tempa-board.html", "템바보드 기준가"), ("/gagyeok/hinoki-ruba.html", "히노끼 루바"), ("/younglim/wall.html", "영림 스타일월·월판넬"), ("/trend/japandi.html", "간살·재팬디 인테리어")],
  "wall", r"템바|루바|간살|아트월", r"템바|루바|아트월"),
]


def gallery(kind, E, ROOT, k=14):
    out = []
    yl = _yl.load(ROOT); sh = _sh.load(ROOT)
    yr = [l.rstrip("\n").split("|") for l in open(os.path.join(ROOT, "data", "yerim.tsv"), encoding="utf-8") if l.strip()]
    if kind == "jungmun":
        out += [("예림", YIMG(r[4]), r[3]) for r in yr if r[0] in ("34", "545", "544")][:k // 3]
        out += [("영림", _yl.IMG(r[6]), _yl.card(r)[0]) for r in yl if r[0] in ("040100", "040200", "040300")][:k // 3]
        out += [("쉐누", _sh.IMG(r[1]), _sh.name(r)) for r in sh if r[0].startswith("door_frt")][:k // 3]
    elif kind == "door":
        out += [("영림", _yl.IMG(r[6]), _yl.card(r)[0]) for r in yl if r[0] in ("030300", "030400")][:k // 3]
        out += [("예림", YIMG(r[4]), r[3]) for r in yr if r[0] in ("10", "32")][:k // 3]
        out += [("쉐누", _sh.IMG(r[1]), _sh.name(r)) for r in sh if r[0].startswith("door_tot")][:k // 3]
    elif kind == "film":
        out += [("영림", _yl.IMG(r[6]), _yl.card(r)[0]) for r in yl if r[0] == "080100"][:k]
    elif kind == "molding":
        out += [("영림", _yl.IMG(r[6]), _yl.card(r)[0]) for r in yl if r[0] == "060101"][:k // 2]
        out += [("쉐누", _sh.IMG(r[1]), _sh.name(r)) for r in sh if r[0].startswith("moulding")][:k // 2]
    elif kind == "wall":
        out += [("영림", _yl.IMG(r[6]), _yl.card(r)[0]) for r in yl if r[0] in ("060300", "060500", "060601")][:k]
    return out


def gen(page, E, CTA, faqslide, ADDR, HOURS, TEL, ROOT, CASES, top, vsplit):
    hub = []
    for ss, sn, tail, desc, steps, links, gk, vrx, crx in SVC:
        gal = gallery(gk, E, ROOT)
        gsec = ('<h2 class="gt">고를 수 있는 제품 예시 <small>옆으로 넘겨 보세요 ›</small></h2><div class="yrg">' + "".join(
            f'<a class="yri" href="#" data-big="{im}" data-n="{E(b + " " + n)}"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" src="{im}" alt="{E(b)} {E(n)}"><span>{E(b)} · {E(n)}</span></a>' for b, im, n in gal) + '</div>') if gal else ""
        vs = top(lambda v: re.search(vrx, v["title"]), 8)
        for rs, rn, hood in REG:
            area_set = {"daejeon": {"yuseong", "seogu", "daedeok", "junggu-donggu"}, "sejong": {"sejong-sinsi", "sejong-eupmyeon"}}.get(rs, {rs})
            cs = [c for c in CASES if c.get("area") in area_set and re.search(crx, c["title"])][:3] or [c for c in CASES if re.search(crx, c["title"])][:2]
            csec = ('<h2 class="gt">시공 사례</h2><ul class="gtip">' + "".join(f'<li><a href="/sigong/{c["slug"]}.html">{E(c["title"])}</a></li>' for c in cs) + '</ul>') if cs else ""
            fq = [(f"{rn} {sn.split('·')[0]} 시공도 하나요?", f"네. 대전·세종은 영진목재 시공 파트너 월드아키텍쳐(실내건축공사업 등록)가 실측부터 설치까지 합니다. {rn}({hood}) 현장 상담은 전화 {TEL}."),
                  (f"{sn.split('·')[0]} 비용은 얼마인가요?", "제품·크기·현장 상태에 따라 달라 실측 후 견적을 드립니다. 자재 기준가는 홈페이지 기준가 페이지에서 미리 보실 수 있습니다."),
                  (f"자재만 사서 직접 해도 되나요?", f"네. {ADDR} 매장에서 자재만 사실 수 있고 원하는 크기로 재단해 드립니다. {HOURS}.")]
            body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/local/">지역별 시공</a> › {E(rn)} › {E(sn)}</p><h1>{E(rn)} {E(sn)}</h1>'
                    f'<p class="glead">{E(rn)}({E(hood)}) {E(desc)} 자재는 대전 유성 영진목재 매장에서 바로 준비하고, 시공은 월드아키텍쳐가 맡습니다.</p>'
                    f'<div class="row"><a class="b r" href="/sigong.html">시공 상담 신청</a><a class="b d" href="tel:{TEL.replace("-", "")}">전화 {TEL}</a></div>'
                    f'<h2 class="gt">진행 순서</h2><ol class="gtip">{"".join(f"<li>{E(x)}</li>" for x in steps)}</ol>{gsec}{csec}'
                    f'<div class="glk">{"".join(f"<a href={chr(34)}{h}{chr(34)}>{E(t)}</a>" for h, t in links)}<a href="/{rs if rs in ("daejeon", "sejong") else rs}.html">{E(rn)} 목재·자재</a></div></section>'
                    + (f'<section class="wrap sec"><h2>{E(sn)} 영상</h2>{vsplit(vs, "h3")}</section>' if vs else "")
                    + f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{faqslide(fq)}</section>'
                    + f'<section class="wrap sec"><p class="small">{E(rn)} 다른 시공: {" · ".join(f"<a href=/local/{x[0]}-{rs}.html>{E(x[1])}</a>" for x in SVC if x[0] != ss)} · 다른 지역 {E(sn)}: {" · ".join(f"<a href=/local/{ss}-{r[0]}.html>{E(r[1])}</a>" for r in REG if r[0] != rs)}</p></section>{CTA}' + LB)
            ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}
            page(f"local/{ss}-{rs}.html", f"{rn} {sn} — {tail} | 월드아키텍쳐·영진목재", f"{rn}({hood}) {sn}. {desc[:70]} 실측·견적·시공 상담 {TEL}.", body, "/sigong.html", ld, gal[0][1] if gal else None)
        hub.append((ss, sn, tail))
    rows = "".join(f'<h2 class="gt">{E(sn)}</h2><div class="qk">' + "".join(f'<a href="/local/{ss}-{r[0]}.html">{E(r[1])} {E(sn.split("·")[0])}</a>' for r in REG) + '</div>' for ss, sn, tail in hub)
    page("local/index.html", "대전·세종 지역별 인테리어 시공 — 중문·방문 교체·필름·몰딩·템바보드 | 월드아키텍쳐·영진목재",
         "대전(유성·서구·대덕·중구·동구)·세종 지역별 중문 설치, 방문·문틀 교체, 인테리어 필름, 몰딩·걸레받이, 템바보드 포인트 벽 시공 안내.",
         f'<section class="wrap sec gg"><h1>지역별 인테리어 시공</h1><p class="glead">대전·세종은 영진목재 시공 파트너 월드아키텍쳐가 실측부터 설치까지 합니다. 사시는 동네와 공사를 고르세요.</p>{rows}</section>{CTA}', "/sigong.html")
    return hub
