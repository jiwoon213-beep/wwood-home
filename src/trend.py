# 인테리어 트렌드 — 느낌(스타일)별로 예림 중문·도어와 매장 자재를 묶어 보여 줌 — /trend/
import os, re
from yerim import IMG as YIMG, LB
import younglim as _yl
import shenu as _sh
SHPG = {"modern": ("door_tot_line.php", "door_frt_al3.php"), "natural": ("door_tot_ntr.php",), "classic": ("door_glass_at.php",), "unique": ("door_tot_pit.php",)}
SHRX = {"modern": r"화이트|그레이|백색|블랙|슬림", "natural": r"오크|애쉬|월넛|우드|원목", "classic": r"클래식|고딕|아치", "japandi": r"간살", "hanok": r"5구|격자|완자", "hotel": r"브론즈|블랙유리", "unique": r"아크릴|큐빅|포인트"}
YLSTY = {"modern": "1301", "natural": "1302", "classic": "1303", "unique": "1304"}
YLRX = {"hanok": r"완자|격자|고방|한옥|창살", "hotel": r"프레임리스|피봇|아치|상부구동|포켓|히든|글라스 도어|LED|무문틀"}
YLONLY = {"kids": ("030600",), "cafe": ("040400", "040500")}

# slug, 이름, 한 줄, 설명, 색·자재 팁, 예림 제품 이름 정규식(제외 정규식), 같이 쓰는 매장 자재 [(주소, 이름)]
STYLES = [
 ("modern", "모던·미니멀", "하얀 벽, 얇은 프레임, 군더더기 없는 선",
  "몰딩과 장식을 줄이고 흰색·회색·검정 같은 무채색으로 정리하는 스타일입니다. 문은 민자(무늬 없음)나 매트 마감, 중문은 프레임이 얇은 슬림형이 잘 어울립니다.",
  ["벽·천장은 화이트, 문은 화이트·그레이 매트로 맞추면 넓어 보입니다.", "걸레받이·몰딩은 얇게(60mm 이하) 하거나 히든 마감.", "손잡이는 블랙·실버 일자형."],
  r"민자|수퍼매트|슈퍼매트|폴라화이트|원톤|스무스|매트|무몰딩|히든|슈퍼 ?슬림|슬림|YAL-|라인|AL 모듈러|모듈러", r"프로방스|완자|격자|키즈|냥이",
  [("/gagyeok/molding-gagyeok.html", "얇은 몰딩·걸레받이"), ("/gagyeok/interior-film.html", "인테리어 필름(화이트·그레이)"), ("/gagyeok/seokgo-gagyeok.html", "석고보드")]),
 ("natural", "내추럴·우드", "오크·월넛 나뭇결로 따뜻하게",
  "나무 무늬와 따뜻한 베이지 톤을 살리는 스타일입니다. 오크·월넛 무늬 문, 원목 루바, 집성목 선반을 함께 쓰면 집 전체가 편안해집니다.",
  ["밝은 오크 + 화이트 벽 조합이 가장 무난합니다.", "벽 한 면을 히노끼·스프러스 루바로 하면 포인트가 됩니다.", "선반·책상은 집성목(아카시아·고무나무)."],
  r"오크|월넛|워시|리얼파인|리얼애쉬|자작|우드|그레인|플랭크|로베레|노체|카타니아|스카이|헤링|YV-|베넷|루앙|목재", r"",
  [("/gagyeok/hinoki-ruba.html", "히노끼 루바"), ("/gagyeok/spruce-ruba.html", "스프러스 루바"), ("/gagyeok/jipseong-gagyeok.html", "집성판"), ("/gagyeok/oilstain.html", "오일스테인")]),
 ("japandi", "간살·재팬디", "세로 살·홈 패턴으로 차분하게",
  "일본식 간결함과 북유럽 나무 감성을 섞은 '재팬디' 스타일입니다. 세로 간살 중문, 홈이 파인(플루트·그루브) 문, 템바보드 벽이 대표적입니다.",
  ["간살 중문 + 템바보드 벽 + 우드톤 바닥 조합.", "색은 베이지·연회색·월넛 중 2가지만.", "조명은 따뜻한 전구색(3000K)."],
  r"간살|플루트|그루브|하프|라코닉|윈디|스팅|템바|버티컬|라이너|체커|노트", r"칠판",
  [("/gagyeok/tempa-board.html", "템바보드"), ("/gagyeok/tempa-ruba.html", "템바 루바"), ("/gagyeok/hinoki-ruba.html", "히노끼 루바")]),
 ("hotel", "호텔·럭셔리", "유리·조명·큰 문으로 고급스럽게",
  "높고 넓은 문, 프레임 없는 유리, 은은한 간접조명으로 호텔 로비 같은 느낌을 내는 스타일입니다. 피봇 도어·LED 무드 도어·그란데 도어가 잘 어울립니다.",
  ["문 높이를 천장 가까이(2.3m 이상) 올리면 공간이 커 보입니다.", "다크그레이·블랙 프레임 + 브론즈 유리 조합.", "간접조명 자리는 목공 단계에서 미리 만드세요."],
  r"벨리니|BE-0|메모리아|오르마|웨이브|스킨|젠|LED|피봇|그란데|프레임리스|올 ?글래스|글래스 도어|자기부상|상부구동|그로시|L-700|L-600|LS-0|아치 도어", r"리젠",
  [("/gagyeok/molding-gagyeok.html", "몰딩"), ("/gagyeok/interior-film.html", "인테리어 필름"), ("/sigong.html", "시공 상담")]),
 ("classic", "클래식·프로방스", "아치·무늬 유리로 아늑하게",
  "아치·무늬 유리·몰딩 장식으로 유럽 시골집처럼 아늑하게 꾸미는 스타일입니다. 프로방스 유리 중문, 아치 도어, 웨인스코팅(벽 몰딩)이 대표적입니다.",
  ["벽 아래쪽에 몰딩을 붙여 웨인스코팅을 만들면 분위기가 확 삽니다.", "크림·연그린·연블루 같은 파스텔 톤.", "문 손잡이는 골드·앤틱 브라스."],
  r"프로방스|아치|플로리아|로렐|아델라|셀리나|YAT-830M|베르너|그랑|스테인드|천리향|화향|블레어|들바람|로맨틱|겨울숲|나무그늘|도레미|리듬|버블링|스펙트럼|YG-10|YGF-10|일리|리프|데이지|델리스|페블|뮬리|무이|베니", r"프레임리스",
  [("/gagyeok/molding-gagyeok.html", "웨인스코팅 몰딩"), ("/gagyeok/interior-film.html", "인테리어 필름")]),
 ("hanok", "한옥·전통", "완자·격자·고방 무늬",
  "완자·격자 창살 무늬로 한옥 느낌을 내는 스타일입니다. 전원주택·카페·한식당에도 잘 어울립니다.",
  ["완자문 + 원목(히노끼·삼나무) 천장 조합.", "한지 느낌 유리나 반투명 유리를 고르세요.", "(미)는 미닫이, (여)는 여닫이용입니다."],
  r"완자|격자|고방|YW-|YWF-", r"",
  [("/gagyeok/hinoki-ruba.html", "히노끼 루바"), ("/jaryo/gakjae.html", "각재·구조재")]),
 ("kids", "아이방·키즈", "칠판·캐릭터 문으로 즐겁게",
  "아이 방에 어울리는 캐릭터·컬러 도어와 칠판 도어입니다. 펫도어는 반려동물이 드나드는 집에 좋습니다.",
  ["손 끼임 방지 쿠션·도어 스토퍼를 같이 다세요.", "칠판 도어는 분필·마커로 씁니다.", "아이방 벽은 닦기 쉬운 필름·페인트."],
  r"키즈|냥이|프렌즈|YA-301|YAT-301|YMT-306|칠판|펫", r"",
  [("/gagyeok/interior-film.html", "인테리어 필름"), ("/mandeul/", "DIY 만들기")]),
 ("unique", "유니크·포인트", "컬러·패턴으로 개성 있게",
  "한 가지 색이나 무늬로 공간에 확실한 포인트를 주는 스타일입니다. 컬러 도어, 패턴 필름, 장식 월판넬로 거실·아이방·매장을 개성 있게 꾸밉니다.",
  ["포인트는 한 공간에 한 곳만 — 나머지는 무채색으로.", "문 색을 바꾸기 어려우면 인테리어 필름으로 먼저 시도.", "벽 한 면만 월판넬·벽장식으로."],
  r"컬러|패턴|포인트|체커|큐브|애로우|스테인드", r"",
  [("/gagyeok/interior-film.html", "인테리어 필름"), ("/gagyeok/tempa-board.html", "템바보드")]),
 ("cafe", "카페·오픈 공간", "폴딩·자동문으로 활짝",
  "폴딩도어로 벽 전체를 열거나, 자동문·파티션으로 공간을 나누는 카페·상가 스타일입니다. 베란다 확장·테라스에도 씁니다.",
  ["바깥과 맞닿는 곳은 단열형 폴딩도어.", "상가 출입구는 자동문(전기 배선 확인).", "파티션은 반투명 유리로 시선만 가리기."],
  r"폴딩|루버|자동문|파티션|시스템 프레임|오피스|연동형 목재", r"",
  [("/sigong.html", "시공 상담"), ("/gagyeok/deck-gagyeok.html", "테라스 데크")]),
]


def gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT, ALLFAQ=None):
    rows = [l.rstrip("\n").split("|") for l in open(os.path.join(ROOT, "data", "yerim.tsv"), encoding="utf-8") if l.strip()]
    nav = lambda cur: '<div class="glk tkn">' + "".join(f'<a href="/trend/{s[0]}.html"{" class=on" if s[0] == cur else ""}>{E(s[1])}</a>' for s in STYLES) + '</div>'
    yrows = [r for r in _yl.load(ROOT) if r[0] not in ("030801",)]
    shrows = [r for r in _sh.load(ROOT) if r[0] not in ("hardware.php", "color.php") and not r[0].startswith("moulding")]
    ygrid = lambda xs, nm: '<div class="yrg">' + "".join(f'<a class="yri" href="#" data-big="{_yl.IMG(r[6])}" data-n="{E(_yl.card(r)[0])}"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" src="{_yl.IMG(r[6])}" alt="{E(nm)} 인테리어 영림 {E(_yl.card(r)[0])}"><span>{E(_yl.card(r)[0])}</span></a>' for r in xs) + '</div>'
    def ylsec(slug, rx, nx):
        nm = next(x[1] for x in STYLES if x[0] == slug)
        xs = [r for r in yrows if (YLSTY.get(slug) == r[5]) or (r[0] in YLONLY.get(slug, ())) or (re.search(YLRX.get(slug, rx), r[4] + " " + r[3]) and not (nx and re.search(nx, r[4])))]
        h = ""
        for lab, pre in (("영림 중문", "040"), ("영림 방문", "03"), ("영림 몰딩·벽재·마루", "060"), ("영림 인테리어 필름", "080")):
            g = [r for r in xs if r[0].startswith(pre)]
            if g: h += f'<h2 class="gt">어울리는 {lab} {len(g)}가지 <small>옆으로 넘겨 보세요 ›</small></h2>{ygrid(g, nm)}'
        shx = [r for r in shrows if r[0] in SHPG.get(slug, ()) or (SHRX.get(slug) and re.search(SHRX[slug], r[2] + " " + r[3]))]
        if shx: h += f'<h2 class="gt">어울리는 쉐누 도어·중문 {len(shx)}가지 <small>옆으로 넘겨 보세요 ›</small></h2><div class="yrg">' + "".join(f'<a class="yri" href="#" data-big="{_sh.IMG(r[1])}" data-n="{E(_sh.name(r))}"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" src="{_sh.IMG(r[1])}" alt="{E(nm)} 인테리어 쉐누 {E(_sh.name(r))}"><span>{E(_sh.name(r))}</span></a>' for r in shx) + '</div>'
        return h
    out = []
    for slug, nm, one, desc, tips, rx, nx, rel in STYLES:
        its = [r for r in rows if re.search(rx, r[3]) and not (nx and re.search(nx, r[3]))]
        nsh = sum(1 for r in shrows if r[0] in SHPG.get(slug, ()) or (SHRX.get(slug) and re.search(SHRX[slug], r[2] + ' ' + r[3])))
        nyl = nsh + sum(1 for r in yrows if (YLSTY.get(slug) == r[5]) or (r[0] in YLONLY.get(slug, ())) or (re.search(YLRX.get(slug, rx), r[4] + ' ' + r[3]) and not (nx and re.search(nx, r[4]))))
        jm = [r for r in its if r[0] in ("544", "545", "34", "556", "207")]
        dr = [r for r in its if r not in jm]
        grid = lambda xs: '<div class="yrg">' + "".join(f'<a class="yri" href="#" data-big="{YIMG(r[4])}" data-n="{E(r[3])}"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" src="{YIMG(r[4])}" alt="{E(nm)} 인테리어 예림 {E(r[3])}"><span>{E(r[3])}</span></a>' for r in xs) + '</div>'
        body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/trend/">인테리어 트렌드</a> › {E(nm)}</p><h1>{E(nm)} 인테리어</h1><p class="glead">{E(one)}. {E(desc)}</p>{nav(slug)}'
                f'<h2 class="gt">이렇게 맞추세요</h2><ul class="gtip">{"".join(f"<li>{E(t)}</li>" for t in tips)}</ul>'
                + (f'<h2 class="gt">어울리는 중문 {len(jm)}가지 <small>옆으로 넘겨 보세요 ›</small></h2>{grid(jm)}' if jm else "")
                + (f'<h2 class="gt">어울리는 방문·문틀 {len(dr)}가지 <small>옆으로 넘겨 보세요 ›</small></h2>{grid(dr)}' if dr else "")
                + ylsec(slug, rx, nx)
                + f'<h2 class="gt">같이 쓰는 자재</h2><div class="glk">{"".join(f"<a href={chr(34)}{h}{chr(34)}>{E(t)}</a>" for h, t in rel)}<a href="/yerim/">예림 중문·도어 전체</a></div>'
                f'<p class="gs">사진은 예림(YERIM)·영림(YOUNGLIM)·쉐누(SHENU) 제품이며 누르면 크게 볼 수 있습니다. 색상·규격·가격은 매장에 문의해 주세요.</p></section>')
        fq = [(f"{nm} 인테리어 자재는 어디서 보나요?", f"{ADDR} 영진종합목재(월드건축자재) 매장에서 문·중문 샘플과 루바·몰딩·필름 실물을 보고 고를 수 있습니다. {HOURS}. 대전·세종은 설치 시공(월드아키텍쳐)도 상담합니다.")]
        body += f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{faqslide(fq)}</section>{CTA}' + LB
        img = YIMG(its[0][4]) if its else None
        page(f"trend/{slug}.html", f"{nm} 인테리어 — {one}, 어울리는 중문·도어·마감재 {len(its) + nyl}가지 | 대전 영진목재",
             f"{nm} 인테리어 꾸미는 법과 어울리는 중문·방문 {len(its)}가지, 같이 쓰는 루바·몰딩·필름. 대전 유성 영진종합목재.", body, "/trend/", None, img)
        out.append((slug, nm, one, len(its) + nyl, img or ""))
    cards = "".join(f'<a class="gi gim" href="/trend/{s}.html"><img loading="lazy" referrerpolicy="no-referrer" src="{im}" alt=""><b>{E(n)}</b><small>{E(o)} · {k}가지</small></a>' for s, n, o, k, im in out)
    page("trend/index.html", "인테리어 트렌드 — 모던·내추럴·간살 재팬디·호텔·클래식·한옥 스타일별 중문·도어·필름·몰딩 | 대전 영진목재",
         "인테리어 느낌(스타일)별로 어울리는 중문·방문·루바·몰딩을 모았습니다. 모던 미니멀, 내추럴 우드, 간살 재팬디, 호텔 럭셔리, 클래식 프로방스, 한옥, 아이방, 카페.",
         f'<section class="wrap sec gg"><h1>인테리어 트렌드</h1><p class="glead">원하는 집 느낌을 먼저 고르세요. 그 느낌에 어울리는 중문·방문과 같이 쓰는 자재를 모아 두었습니다. 사진을 캡처해 매장에 보여 주시면 맞는 자재를 바로 찾아 드립니다.</p><div class="gig">{cards}</div></section>{CTA}', "/trend/")
    return out
