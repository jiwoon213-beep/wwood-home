# 쉐누(SHENU, namuip.com) ABS도어·글래스도어·중문·몰딩·하드웨어·시트색상 — /shenu/ (회사 허락, 사진은 namuip.com 링크)
# 데이터 src/data/shenu.tsv: 페이지|이미지|이름|부가설명 (.github/scripts/fetch_shenu.py 가 매일 갱신·중복 제거)
import os
from yerim import LB

IMG = lambda p: "https://namuip.com/cnd_home/assets/img/" + p
LINE = {"door_tot_bsc.php": "베이직", "door_tot_ntr.php": "내추럴", "door_tot_line.php": "라인", "door_tot_pit.php": "포인트",
        "door_glass_at.php": "아치형(AT)", "door_glass_td.php": "사각형(TD)", "door_glass_td_d.php": "TD 디자인",
        "door_frt_wood3.php": "목재 3연동", "door_frt_wood.php": "목재 미닫이·여닫이", "door_frt_al3.php": "알루미늄 3연동",
        "moulding1.php": "문선 몰딩", "moulding2.php": "계단 몰딩", "moulding3.php": "천정 몰딩", "moulding4.php": "걸레받이", "moulding5.php": "기둥·루바·기타",
        "hardware.php": "도어락·손잡이", "color.php": "시트 색상"}
PAGES = [
 ("door-abs", "ABS 도어", ["door_tot_bsc.php", "door_tot_ntr.php", "door_tot_line.php", "door_tot_pit.php"], "물에 강한 ABS 도어. 베이직·내추럴·라인·포인트 디자인.", ["욕실 문은 ABS 도어를 권합니다.", "현대L&C 시트 색상(S·ZX 번호)과 쉐누 색상([번호])으로 표면 색을 고릅니다."]),
 ("door-glass", "글래스 도어", ["door_glass_at.php", "door_glass_td.php", "door_glass_td_d.php"], "유리가 들어간 방문. 아치형(AT)·사각형(TD) 디자인.", ["유리 종류(망입·아쿠아·브론즈 등)에 따라 비치는 정도가 다릅니다."]),
 ("jungmun", "중문·창호", ["door_frt_wood3.php", "door_frt_wood.php", "door_frt_al3.php"], "현관 3연동 중문(목재·알루미늄)과 목재 미닫이·여닫이 창호.", ["3연동은 좁은 현관에서도 넓게 열립니다.", "유리는 5T 망입·아쿠아·미스트·워터큐브 등에서 고릅니다."]),
 ("molding", "PVC 몰딩·걸레받이", ["moulding1.php", "moulding2.php", "moulding3.php", "moulding4.php", "moulding5.php"], "문선·계단·천정 몰딩, 걸레받이, 기둥·루바 마감재(PVC).", ["몰딩 색은 문·문틀 색과 맞추면 깔끔합니다.", "PVC 몰딩은 물에 강해 욕실·주방 주변에도 씁니다."]),
 ("hardware", "도어락·손잡이", ["hardware.php"], "방문 도어락·손잡이·하드웨어.", ["문 두께와 손잡이 구멍 위치를 확인하세요."]),
 ("color", "시트 색상표", ["color.php"], "쉐누 도어·문틀·몰딩에 입히는 시트 색상.", ["모니터에 따라 실제 색과 다를 수 있어 매장 샘플로 확인하세요."]),
]


def load(ROOT):
    p = os.path.join(ROOT, "data", "shenu.tsv")
    if not os.path.exists(p): return []
    return [l.rstrip("\n").split("|") for l in open(p, encoding="utf-8") if l.count("|") >= 3]


def name(r):
    return (r[2] + (" · " + r[3] if r[3] and r[3] not in r[2] else "")).strip(" ·") or LINE.get(r[0], "")


def gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT):
    rows = load(ROOT)
    if not rows: return []
    nav = lambda cur: '<div class="glk tkn">' + "".join(f'<a href="/shenu/{p[0]}.html"{" class=on" if p[0] == cur else ""}>{E(p[1])}</a>' for p in PAGES) + '</div>'
    out = []
    for slug, nm, pgs, lead, tips in PAGES:
        its = [r for r in rows if r[0] in pgs]
        if not its: continue
        sec = ""
        for pg in pgs:
            xs = [r for r in its if r[0] == pg]
            if not xs: continue
            sec += f'<h2 class="gt">{E(LINE.get(pg, ""))} {len(xs)}가지 <small>옆으로 넘겨 보세요 ›</small></h2><div class="yrg">'
            sec += "".join(f'<a class="yri" href="#" data-big="{IMG(r[1])}" data-n="{E(name(r))}"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" src="{IMG(r[1])}" alt="쉐누 {E(name(r))}"><span>{E(name(r))}</span></a>' for r in xs) + '</div>'
        fq = [(f"쉐누 {nm} 어디서 보고 주문하나요?", f"{ADDR} 영진종합목재(월드건축자재) 매장에서 상담·주문할 수 있습니다. {HOURS}. 문 크기·벽 두께를 재 오시면 맞는 규격을 찾아 드리고, 대전·세종은 설치 시공(월드아키텍쳐)도 상담합니다.")]
        body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › <a href="/shenu/">쉐누 도어·몰딩</a> › {E(nm)}</p><h1>쉐누 {E(nm)}</h1><p class="glead">{E(lead)} 총 {len(its)}가지.</p>{nav(slug)}{sec}'
                f'<p class="gs">쉐누(SHENU) 제품입니다. 사진을 누르면 크게 볼 수 있습니다. 색상·규격·가격·납기는 매장에 문의해 주세요.</p>'
                f'<h2 class="gt">고를 때 알아둘 것</h2><ul class="gtip">{"".join(f"<li>{E(t)}</li>" for t in tips)}</ul>'
                f'<div class="glk"><a href="/trend/">인테리어 트렌드</a><a href="/younglim/">영림 도어·중문</a><a href="/yerim/">예림 중문·도어</a><a href="/visit.html">매장 길찾기</a></div></section>'
                f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{faqslide(fq)}</section>{CTA}' + LB)
        page(f"shenu/{slug}.html", f"쉐누 {nm} {len(its)}종 — 디자인·색상 사진 | 대전 영진목재", f"쉐누 {nm} {len(its)}가지 사진. {lead} 대전 유성 영진종합목재 매장 상담·주문.", body, "/jaryo/", None, IMG(its[0][1]))
        out.append((slug, nm, lead, len(its), IMG(its[0][1])))
    cards = "".join(f'<a class="gi gim" href="/shenu/{s}.html"><img loading="lazy" referrerpolicy="no-referrer" src="{im}" alt=""><b>{E(n)} <small>{k}종</small></b><small>{E(l[:40])}</small></a>' for s, n, l, k, im in out)
    tot = sum(x[3] for x in out)
    page("shenu/index.html", f"쉐누 ABS도어·글래스도어·중문·PVC 몰딩 {tot}종 | 대전 영진목재",
         f"쉐누(SHENU) ABS도어·글래스도어·3연동 중문·PVC 몰딩·도어락·시트색상 {tot}가지 사진. 대전 유성 영진종합목재 매장 상담·주문.",
         f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › 쉐누 도어·몰딩</p><h1>쉐누 도어·중문·몰딩</h1><p class="glead">쉐누(SHENU) ABS 도어·글래스 도어·중문·PVC 몰딩·하드웨어·시트 색상 {tot}가지를 종류별로 모았습니다(같은 제품은 한 번만).</p><div class="gig">{cards}</div><div class="glk"><a href="/trend/">인테리어 트렌드</a><a href="/younglim/">영림 도어·중문</a><a href="/yerim/">예림 중문·도어</a></div></section>{CTA}', "/jaryo/")
    return out
