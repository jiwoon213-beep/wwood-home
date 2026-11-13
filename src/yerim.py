# 예림(YERIM) 중문·도어·문틀 — /yerim/ (회사 허락, 사진은 yerim.net/upload/product/ 링크)
import os, csv
LB = r'''<div id="ylb" class="ylb" hidden><button class="ylx" aria-label="닫기">×</button><button class="ylp" aria-label="이전">‹</button><figure><img alt=""><figcaption><b></b><span>예림(YERIM) 제품 · 색상·규격·가격은 매장 문의</span><span class="yla"><a class="b g" href="/visit.html">매장 길찾기</a><a class="b d" href="tel:0425452900">전화 문의</a></span></figcaption></figure><button class="yln" aria-label="다음">›</button></div>
<script>(function(){var lb=document.getElementById("ylb");if(!lb)return;var im=lb.querySelector("img"),nm=lb.querySelector("figcaption b"),L=[],i=0;
function show(){var a=L[i];im.src=a.getAttribute("data-big");im.alt=a.getAttribute("data-n");nm.textContent=a.getAttribute("data-n")+"  ("+(i+1)+"/"+L.length+")";}
document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest(".yri");if(!a)return;e.preventDefault();L=[].slice.call(a.parentNode.querySelectorAll(".yri"));i=L.indexOf(a);show();lb.hidden=false;document.body.style.overflow="hidden";});
function cl(){lb.hidden=true;im.src="";document.body.style.overflow="";}
lb.querySelector(".ylx").onclick=cl;lb.onclick=function(e){if(e.target===lb)cl();};
lb.querySelector(".ylp").onclick=function(){i=(i-1+L.length)%L.length;show();};lb.querySelector(".yln").onclick=function(){i=(i+1)%L.length;show();};
document.addEventListener("keydown",function(e){if(lb.hidden)return;if(e.key=="Escape")cl();if(e.key=="ArrowLeft")lb.querySelector(".ylp").click();if(e.key=="ArrowRight")lb.querySelector(".yln").click();});
var sx=0;lb.addEventListener("touchstart",function(e){sx=e.touches[0].clientX},{passive:true});lb.addEventListener("touchend",function(e){var d=e.changedTouches[0].clientX-sx;if(Math.abs(d)>50)(d>0?lb.querySelector(".ylp"):lb.querySelector(".yln")).click();});})();</script>'''
IMG = lambda p: "https://www.yerim.net/upload/product/2039376550_" + p[1:]
D3 = {"97": "슈퍼 슬림", "99": "슬림", "98": "자동문", "551": "리안", "550": "뉴 밸런스", "549": "피봇", "553": "프레임리스 글래스", "555": "클래식", "554": "폴딩", "574": "시스템 프레임·연결", "546": "LED", "547": "간살", "548": "슈퍼슬림 간살",
      "557": "이지", "558": "이지 슬림", "534": "AL 모듈러", "535": "벨로체", "536": "벨리니", "537": "올글래스", "77": "ABS", "80": "리얼 텍스처", "82": "라인", "540": "우드데코 포인트", "541": "완자·격자·갤러리", "83": "키즈", "84": "칠판", "539": "합판·도장용",
      "91": "프리미엄 방화문", "92": "일반형 방화문", "93": "보급형 방화문", "572": "울트라 문틀", "573": "발포·목재 문틀", "488": "AL 문틀"}
# slug, 이름, 검색 꼬리, 리드, 고르는(d2, d3 목록) 조건, 팁, FAQ
PAGES = [
 ("jungmun-slim", "슬림·슈퍼슬림 3연동 중문", "현관 3연동·4연동 중문, 자동문·반자동 중문 종류",
  "현관 중문으로 가장 많이 하는 3연동 슬라이딩. 프레임이 얇은 슈퍼 슬림, 알루미늄 슬림, 자기부상·반자동 자동문까지.",
  lambda d2, d3: d2 in ("34", "556") and d3 in ("97", "99", "98", "557", "558"),
  ["3연동은 문짝 3장이 함께 밀려 좁은 현관에서도 넓게 열립니다(열린 폭 약 2/3).", "프레임 폭이 얇을수록(슈퍼 슬림) 유리가 넓어 보여 현관이 환해집니다.", "자동문·반자동은 전기 배선 위치를 미리 확인하세요."],
  [("3연동 중문과 원슬라이딩 차이는?", "3연동은 문짝 3장이 겹치며 열려 벽 쪽 공간이 적게 필요하고, 원슬라이딩은 문 1장이 통째로 밀려 열려 옆 벽이 문 폭만큼 있어야 합니다."),
   ("중문 설치하면 단열·소음 효과가 있나요?", "현관 바람과 냉난방 손실, 계단·복도 소음이 줄어듭니다. 유리·프레임 종류에 따라 차이가 납니다.")]),
 ("jungmun-sliding", "슬라이딩·피봇·글래스 중문", "리안 슬라이딩 상부구동·파티션·프레임리스 글래스 중문",
  "레일이 바닥에 없는 상부구동 슬라이딩(리안), 축으로 도는 피봇 도어, 프레임 없는 글래스 도어와 파티션.",
  lambda d2, d3: d2 in ("34", "544") and d3 in ("551", "550", "549", "553", ""),
  ["상부구동은 바닥 레일이 없어 턱이 없고 청소가 쉽습니다.", "피봇 도어는 문 폭이 넓을 때 무게를 축이 받쳐 부드럽게 열립니다.", "파티션(고정창)과 같이 쓰면 거실·주방 공간 나누기에 좋습니다."],
  [("슬라이딩 중문은 벽에 공간이 얼마나 필요한가요?", "문짝이 밀려 들어갈 옆 벽이 문짝 폭만큼 필요합니다. 연동형은 더 적게 필요합니다."),
   ("상부구동 중문 장점은?", "바닥 레일이 없어 걸려 넘어질 턱이 없고, 로봇청소기도 지나갑니다.")]),
 ("jungmun-ganssal", "간살·LED 중문", "간살 슬라이딩·간살 파티션·LED 무드 중문",
  "세로 살(간살)이 들어간 중문과 파티션, 은은한 LED 조명이 들어간 무드 도어.", lambda d2, d3: d2 == "545",
  ["간살은 시선을 적당히 가려 주면서 빛은 통과시킵니다.", "LED 무드 도어는 전원 위치를 시공 전에 정해야 합니다."],
  [("간살 중문은 청소가 어렵나요?", "살 사이 먼지는 마른 솔이나 극세사로 털면 됩니다. 유리면이 안쪽에 있는 제품이 관리가 쉽습니다.")]),
 ("jungmun-classic", "클래식·여닫이 중문", "여닫이 중문·2·4·6연동·유리 디자인(입구·심플·프로방스)",
  "문처럼 여닫는 클래식 중문과 유리 무늬(입구·심플·프로방스 등) 디자인, 2·4·6연동.", lambda d2, d3: (d2 == "34" and d3 == "555") or d2 == "207",
  ["여닫이 중문은 문이 열리는 방향에 신발장·벽이 걸리지 않는지 확인하세요.", "유리 무늬(망입·스트라이프·워터큐브 등)로 분위기가 크게 달라집니다."],
  [("여닫이 중문 열리는 방향은?", "보통 현관 안쪽(거실 쪽)으로 열립니다. 신발장 문과 부딪히지 않는지 먼저 봅니다.")]),
 ("jungmun-folding", "폴딩도어·시스템 파티션", "폴딩도어(아파트형·단열형·창문형)·시스템 프레임 파티션·루버셔터",
  "접어서 활짝 여는 폴딩도어와, 문과 고정창을 이어 붙이는 시스템 프레임 파티션.", lambda d2, d3: d2 == "34" and d3 in ("554", "574"),
  ["폴딩도어는 베란다·카페·상가 입구처럼 전체를 열고 싶은 곳에 씁니다.", "단열형은 바깥과 맞닿는 곳, 고하중형은 문짝이 큰 곳에."],
  [("폴딩도어 단열형은 어디에 쓰나요?", "베란다 확장·카페 테라스처럼 바깥 공기와 맞닿는 곳에 씁니다.")]),
 ("door-premium", "프리미엄·디자인 도어", "벨리니·벨로체·AL 모듈러·히든·아치 도어",
  "고급 마감(수퍼매트·슈퍼그로시·오크 무늬)의 벨리니·벨로체, 알루미늄 모듈러, 히든·아치·그란데 도어.", lambda d2, d3: d2 in ("533", "538"),
  ["히든 도어는 문틀이 벽과 같은 면으로 묻혀 벽처럼 보입니다.", "매트·그로시 마감은 같은 색이라도 느낌이 크게 다르니 실물 샘플을 보세요."],
  [("히든 도어는 일반 문틀에 달 수 있나요?", "전용 히든 문틀이 필요합니다. 벽 마감 전에 문틀을 먼저 세웁니다.")]),
 ("door-abs", "ABS 도어", "방문 ABS 도어 디자인·리얼 텍스처 도어",
  "욕실·방문으로 가장 많이 쓰는 ABS 도어. 물에 강하고 휨이 적습니다. 무늬·라인·리얼 텍스처까지.", lambda d2, d3: d2 == "10" and d3 in ("77", "80"),
  ["ABS 도어는 습기에 강해 욕실 문으로 많이 씁니다.", "모델명 YA는 ABS, YM은 멤브레인(필름 마감) 계열입니다.", "문 크기(폭×높이)와 벽 두께(문틀 폭)를 재 오시면 맞는 규격을 찾아 드립니다."],
  [("ABS 도어와 멤브레인 도어 차이는?", "ABS는 플라스틱 표면이라 물·충격에 강하고, 멤브레인은 필름을 입혀 무늬가 다양합니다. 욕실은 ABS를 권합니다.")]),
 ("door-point", "포인트·라인·키즈·칠판 도어", "우드데코 포인트·라인 도어·아이방 키즈 도어·칠판 도어",
  "방문에 포인트를 주는 우드데코·라인 디자인과 아이방용 키즈·칠판 도어.", lambda d2, d3: d2 == "10" and d3 in ("540", "82", "83", "84"),
  ["아이방 문은 손 끼임 방지 제품(도어 스토퍼·완충 경첩)과 같이 고르세요.", "칠판 도어는 분필·마커로 쓸 수 있습니다."],
  [("키즈 도어는 일반 방문 크기와 같나요?", "같은 규격으로 나옵니다. 기존 문틀에 맞는지 문 크기를 재 오세요.")]),
 ("door-wanja", "완자·격자·갤러리·합판 도어", "한식 완자문·격자 유리문·통풍 갤러리 도어·도장용 합판 도어",
  "한옥 느낌의 완자문, 유리 격자문, 통풍되는 갤러리 도어, 직접 칠하는 도장용·합판 도어.", lambda d2, d3: d2 == "10" and d3 in ("541", "539"),
  ["(미)는 미닫이, (여)는 여닫이용 모델입니다.", "갤러리 도어는 보일러실·에어컨실처럼 통풍이 필요한 곳에.", "도장용·합판 도어는 원하는 색 페인트·스테인으로 마감합니다."],
  [("도장용 도어는 어떤 페인트를 쓰나요?", "젯소(프라이머) 후 수성 우레탄·실내용 페인트를 권합니다.")]),
 ("door-glass", "글래스(유리) 도어", "방문 유리 도어·무몰딩 글래스·아크릴 도어 디자인",
  "유리가 들어가 빛이 통하는 방문. 무늬 유리·블라인드 내장·아크릴 도어까지.", lambda d2, d3: d2 == "32",
  ["(W)는 멤브레인, (A)는 ABS 계열입니다.", "블라인드 내장형은 유리 안쪽 블라인드로 빛을 조절합니다."],
  [("유리 도어는 깨질 위험이 없나요?", "실내 도어용 강화·접합 또는 아크릴 제품을 씁니다. 아이 있는 집은 아크릴 도어도 좋습니다.")]),
 ("door-ez", "이지·차음·펫·방염 도어", "가성비 이지 도어·차음 도어·펫도어·휨 방지·준불연 도어",
  "가성비 좋은 이지(EZ) 도어와, 소음을 줄이는 차음 도어, 반려동물 펫도어, 휨 방지·방염·준불연 도어.", lambda d2, d3: d2 in ("542", "248", "543"),
  ["차음 도어는 공부방·침실·홈오피스에 좋습니다.", "준불연·방염 도어는 다중이용시설·상가에 필요할 수 있습니다."],
  [("차음 도어는 얼마나 조용해지나요?", "일반 방문보다 문짝 속이 꽉 차 있고 틈을 막아 대화 소리가 확실히 줄어듭니다. 문틀 틈 마감도 같이 해야 효과가 납니다.")]),
 ("door-fire", "방화문", "아파트·상가 방화문 FDP·FDG 시리즈, 람마형 방화문틀",
  "철제 방화문(프리미엄 FDP·일반 FDG·보급형). 현관·계단실·기계실용.", lambda d2, d3: d2 == "43",
  ["방화문은 인증 제품·문틀 세트로 설치해야 합니다.", "S가 붙은 모델은 디자인(스텐 등) 마감형입니다."],
  [("방화문 교체는 직접 해도 되나요?", "인증 규격대로 문틀·도어클로저까지 설치해야 해서 시공을 권합니다(월드아키텍쳐 시공 상담).")]),
 ("door-frame", "문틀", "울트라·히든·슬림·발포·목재·AL 문틀 종류",
  "문짝을 잡아 주는 문틀. 얇고 깔끔한 슬림·히든 문틀, 물에 강한 발포(PVC) 문틀, 목재·알루미늄 문틀.", lambda d2, d3: d2 == "47",
  ["욕실은 물에 강한 발포(PVC) 문틀을 씁니다.", "문틀 폭은 벽 두께에 맞춰 고릅니다(벽 두께를 재 오세요).", "히든 문틀은 벽 마감 전에 먼저 세웁니다."],
  [("문틀만 교체할 수 있나요?", "가능하지만 벽 마감을 같이 손봐야 할 때가 많습니다. 문짝과 함께 교체하는 경우가 일반적입니다.")]),
]


def gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT, ALLFAQ=None):
    rows = [l.rstrip("\n").split("|") for l in open(os.path.join(ROOT, "data", "yerim.tsv"), encoding="utf-8") if l.strip()]
    nav = lambda cur: '<div class="glk tkn">' + "".join(f'<a href="/yerim/{p[0]}.html"{" class=on" if p[0] == cur else ""}>{E(p[1])}</a>' for p in PAGES) + '</div>'
    out = []
    for slug, nm, tail, lead, sel, tips, faq in PAGES:
        items = [r for r in rows if sel(r[0], r[1])]
        groups = {}
        for d2, d3, uid, n, im in items:
            groups.setdefault(D3.get(d3, ""), []).append((uid, n, im))
        sec = ""
        for g, its in groups.items():
            sec += (f'<h2 class="gt">{E(g) + " " if g else ""}{len(its)}가지 <small>옆으로 넘겨 보세요 ›</small></h2><div class="yrg">' if len(groups) > 1 else f'<h2 class="gt">디자인 {len(its)}가지 <small>옆으로 넘겨 보세요 ›</small></h2><div class="yrg">')
            sec += "".join(f'<a class="yri" href="#" data-big="{IMG(im)}" data-n="{E(n)}"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" width="300" height="300" src="{IMG(im)}" alt="예림 {E(n)}"><span>{E(n)}</span></a>' for uid, n, im in its) + '</div>'
        fq = faq + [(f"예림 {nm} 어디서 보고 살 수 있나요?", f"{ADDR} 영진종합목재(월드건축자재) 매장에서 상담·주문할 수 있습니다. {HOURS}. 문 크기·벽 두께를 재 오시면 맞는 규격을 찾아 드리고, 대전·세종 설치 시공(월드아키텍쳐)도 상담합니다.")]
        body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › <a href="/yerim/">예림 중문·도어</a> › {E(nm)}</p><h1>예림 {E(nm)}</h1><p class="glead">{E(lead)}</p>{nav(slug)}'
                f'{sec}<p class="gs">예림(YERIM) 제품입니다. 사진을 누르면 크게 볼 수 있습니다. 색상·규격·가격·납기는 매장에 문의해 주세요(주문 제작품 포함).</p>'
                f'<h2 class="gt">고를 때 알아둘 것</h2><ul class="gtip">{"".join(f"<li>{E(t)}</li>" for t in tips)}</ul>'
                f'<div class="glk"><a href="/gagyeok/door-gagyeok.html">방문·문틀 기준가</a><a href="/calc.html#door">문 크기 계산기</a><a href="/sigong.html">설치 시공 맡기기</a><a href="/visit.html">매장 길찾기</a></div></section>'
                f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{faqslide(fq)}</section>{CTA}' + LB)
        ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]
        if ALLFAQ is not None: ALLFAQ.append(("예림 중문·도어", faq, f"/yerim/{slug}.html", nm))
        page(f"yerim/{slug}.html", f"예림 {nm} — {tail} {len(items)}종 | 대전 영진목재", f"예림 {nm} {len(items)}가지 사진. {lead} 대전 유성 영진종합목재 매장 상담·주문, 대전·세종 시공.", body, "/jaryo/", ld, IMG(items[0][4]) if items else None)
        out.append((slug, nm, tail, len(items), IMG(items[0][4]) if items else ""))
    cards = "".join(f'<a class="gi gim" href="/yerim/{s}.html"><img loading="lazy" referrerpolicy="no-referrer" src="{im}" alt=""><b>{E(n)} <small>{k}종</small></b><small>{E(t)}</small></a>' for s, n, t, k, im in out)
    tot = sum(x[3] for x in out)
    page("yerim/index.html", f"예림 중문·도어·문틀 {tot}종 — 3연동 중문·슬라이딩·간살·ABS 도어·방화문 | 대전 영진목재",
         f"예림(YERIM) 중문·방문·문틀 {tot}가지를 종류별 사진으로. 대전 유성 영진종합목재 매장 상담·주문, 대전·세종 설치 시공.",
         f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › 예림 중문·도어</p><h1>예림 중문·도어·문틀</h1><p class="glead">예림(YERIM) 중문·방문·문틀 {tot}가지를 종류별로 모았습니다. 마음에 드는 디자인을 골라 매장에 오시면 크기·색상·납기를 안내해 드립니다. 대전·세종은 설치 시공도 합니다.</p><div class="gig">{cards}</div><div class="glk"><a href="/gagyeok/door-gagyeok.html">방문·문틀 기준가</a><a href="/jaryo/door.html">도어 전체 자재</a><a href="/sigong.html">시공 맡기기</a></div></section>{CTA}', "/jaryo/")
    return out
