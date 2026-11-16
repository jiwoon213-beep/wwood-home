# 셀프 인테리어 공정 플래너(/gongjeong.html) — 순서표 + 체크(손님 휴대폰 저장) + 단계별 시공팀 연결·계산기·시공법 링크.
# 기간·비용 숫자는 넣지 않음(확인 안 된 숫자 금지).
import json

STEPS = [  # id, 공정, 하는 일, 순서 이유·팁, 링크들, 해당(apt/house/shop/all), 기본 포함
    ("plan", "계획·실측", "공사 범위 정하기, 방마다 크기 재기, 자재 고르기", "바꿀 곳과 그대로 둘 곳을 먼저 정하면 견적·자재가 흔들리지 않아요. 콘센트·조명 위치도 이때 정해 두세요.",
     [("/calc.html", "자재 계산기"), ("/yesi/", "몇 평이면 얼마?"), ("/mirigi.html", "공사 미리보기")], "all", 1),
    ("cheolgeo", "철거", "기존 마감재·가구·타일 뜯기, 폐기물 정리", "모든 공정의 시작이에요. 철거 후에 숨어 있던 누수·곰팡이를 확인할 수 있어요.",
     [("/yeongyeol/cheolgeo.html", "철거팀 연결")], "all", 1),
    ("seolbi", "설비·방수", "급수·배수 배관, 욕실 방수", "배관은 벽·바닥이 덮이기 전에 끝내야 해요. 욕실은 방수를 먼저 하고 타일로 덮어요.",
     [("/yeongyeol/tile.html", "타일·설비팀 연결")], "all", 1),
    ("jeongi", "전기 배선", "콘센트·스위치·조명 위치 배선", "목공으로 벽·천장을 막기 전에 선을 깔아야 해요. 나중에 하면 도배를 다시 뜯게 돼요.",
     [("/yeongyeol/jeongi.html", "전기팀 연결")], "all", 1),
    ("shassi", "샷시·창호·현관문", "창호 교체, 현관문·중문 틀", "창틀이 바뀌면 주변 마감이 달라져서 목공·도배 전에 해요.",
     [("/yeongyeol/shassi.html", "샷시팀 연결"), ("/yeongyeol/folding.html", "폴딩도어")], "all", 0),
    ("oebyeok", "외벽 사이딩", "외벽 하지·투습방수지·사이딩", "단독주택·농막·상가 외벽. 창호를 바꾼다면 창호 다음에 해요.",
     [("/yeongyeol/siding.html", "외벽 시공(직접 시공)"), ("/sigongbeop/ceramic-siding.html", "세라믹사이딩 시공법"), ("/yesi/siding-house-30py.html", "외벽 사이딩 자재비")], "house", 1),
    ("mokgong", "목공", "천장·가벽·문틀·몰딩·아트월, 단열", "전기·설비가 끝난 뒤 벽과 천장을 만들어요. 단열도 이때 넣어요.",
     [("/yeongyeol/mokgong.html", "목공팀 연결"), ("/gabyeok-gyesan.html", "가벽 계산기"), ("/yesi/gypsum-wall-5py.html", "벽 석고보드 몇 장?"), ("/cut.html", "재단 미리보기")], "all", 1),
    ("tile", "타일", "욕실·주방·현관 타일", "목공 다음, 도배 전에 해요. 먼지·물이 나오는 공정이라서요.",
     [("/yeongyeol/tile.html", "타일팀 연결"), ("/sigongbeop/yoksil-tile.html", "욕실 타일 시공법")], "all", 1),
    ("film", "인테리어 필름", "문·문틀·싱크대·몰딩 필름", "도배 전에 붙여야 필름 끝선이 벽지 밑으로 깔끔하게 들어가요.",
     [("/yeongyeol/film.html", "필름팀 연결"), ("/gagyeok/interior-film.html", "필름 가격")], "all", 1),
    ("paint", "페인트", "수성 페인트·탄성코트", "도배 대신 페인트를 칠할 벽, 베란다 탄성코트는 이때.",
     [("/yeongyeol/paint.html", "페인트팀 연결"), ("/bondex/", "본덱스 페인트")], "all", 0),
    ("dobae", "도배", "벽지 도배", "먼지 나는 공정이 다 끝난 뒤에 해요. 바닥보다 먼저 하면 바닥이 더러워지지 않아요.",
     [("/yeongyeol/dobae.html", "도배팀 연결"), ("/yesi/eboard-wall-4py.html", "이보드(단열 도배)")], "all", 1),
    ("badak", "바닥", "강마루·장판·데코타일", "도배 다음에 깔아요. 바닥을 먼저 깔면 도배·가구 작업 중에 긁힐 수 있어요.",
     [("/yeongyeol/maru.html", "마루팀 연결"), ("/yeongyeol/decotile.html", "데코타일팀 연결"), ("/sigongbeop/gangmaru.html", "강마루 시공법")], "all", 1),
    ("gagu", "가구", "싱크대·붙박이장·신발장", "바닥이 끝나야 높이가 맞아요. 싱크대와 마루 순서는 현장에 따라 달라지니 미리 상의하세요.",
     [("/yeongyeol/gagu.html", "가구팀 연결")], "all", 1),
    ("deck", "데크·마당", "방부목·합성 데크, 울타리", "외부 공사라 실내와 따로 진행할 수 있어요.",
     [("/deck-gyesan.html", "데크 계산기"), ("/yesi/deck-5py.html", "데크 몇 평이면 얼마?"), ("/mandeul/deck.html", "데크 만들기")], "house", 0),
    ("majimak", "조명·마감", "조명·스위치 커버, 실리콘, 블라인드·커튼", "마지막 마감 공정. 블라인드는 창틀·천장 마감이 끝난 뒤 달아요.",
     [("/yeongyeol/jeongi.html", "전기·조명"), ("/yeongyeol/blind.html", "블라인드·커튼팀 연결"), ("/sigongbeop/silicone-julnun.html", "실리콘 시공법")], "all", 1),
    ("cheongso", "입주 청소·점검", "청소, 하자 확인", "문 여닫힘, 수전 물샘, 콘센트를 하나씩 확인하세요.",
     [], "all", 1),
]


def gen(page, E, CTA, TEL):
    T = TEL.replace("-", "")
    data = [dict(id=i, n=n, d=d, tip=tip, l=l, k=k, on=on) for i, n, d, tip, l, k, on in STEPS]
    body = f'''<section class="wrap sec"><h1>셀프 인테리어 공정 순서 플래너</h1>
<p class="lead">공사는 <b>순서</b>가 반이에요. 순서가 틀리면 다 한 걸 다시 뜯게 됩니다. 집 종류를 고르면 순서표가 나오고, 끝낸 공정은 체크해 두세요. 체크는 이 휴대폰에 저장돼요.</p>
<div class="gjk" id="gjk"><button type="button" data-k="apt" class="on">아파트·빌라</button><button type="button" data-k="house">단독주택·농막</button><button type="button" data-k="shop">상가·사무실</button></div>
<div class="gjp"><div class="gjbar"><i id="gjbi"></i></div><b id="gjpn">0 / 0</b></div>
<ol class="gjl" id="gjl"></ol>
<div class="row"><button type="button" class="b r" id="gjsv">내 현장함에 저장</button><a class="b" href="/yeongyeol/">공정별 시공팀 연결</a><button type="button" class="b" id="gjrs">체크 다 지우기</button></div>
<p class="small muted">현장마다 순서가 조금 달라질 수 있어요. 직접 하기 어려운 공정은 매장({E(TEL)})으로 전화하시면 거래 시공팀을 연결해 드립니다.</p></section>{CTA}
<style>.gjk{{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin:14px 0 10px}}.gjk button{{border:1px solid #ddd5c8;background:#fff;border-radius:12px;padding:11px 4px;font-weight:800;font-size:14px;font-family:inherit;cursor:pointer}}.gjk button.on{{background:#1D1B18;color:#fff;border-color:#1D1B18}}
.gjp{{display:flex;align-items:center;gap:10px;margin:6px 0 12px}}.gjbar{{flex:1;height:10px;background:#ece6dc;border-radius:99px;overflow:hidden}}.gjbar i{{display:block;height:100%;width:0;background:#c41a1f;transition:width .3s}}.gjp b{{font-size:14px;white-space:nowrap}}
.gjl{{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:10px;counter-reset:g}}.gjl li{{background:#fff;border:1px solid #ece6dc;border-radius:16px;padding:14px;counter-increment:g}}.gjl li.dn{{background:#f3f7f1;border-color:#cfe3c6}}.gjl li.op{{border-style:dashed}}
.gjh{{display:flex;gap:10px;align-items:flex-start;cursor:pointer}}.gjh input{{width:24px;height:24px;flex:none;margin:2px 0 0;accent-color:#c41a1f}}.gjh b{{font-size:17px;display:block}}.gjh b::before{{content:counter(g) ". ";color:#c41a1f}}.gjh span{{display:block;font-size:13.5px;color:#6b655c;margin-top:2px}}
.gjl li.dn .gjh b{{text-decoration:line-through;color:#7a8a72}}.gjt{{margin:8px 0 0 34px;font-size:14px;line-height:1.6;color:#3b3731}}.gjlk{{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 0 34px}}.gjlk a{{font-size:13px;font-weight:800;border:1px solid #e6dfd5;border-radius:999px;padding:6px 11px;color:#1D1B18;text-decoration:none;background:#faf8f4}}.gjop{{font-size:11.5px;color:#8a8378;font-weight:700;margin-left:6px}}</style>
<script>(function(){{var S={json.dumps(data, ensure_ascii=False)},K="apt",st={{}};try{{var o=JSON.parse(localStorage.getItem("wwPLAN")||"{{}}");K=o.k||K;st=o.s||{{}}}}catch(e){{}}
function sv(){{try{{localStorage.setItem("wwPLAN",JSON.stringify({{k:K,s:st}}))}}catch(e){{}}}}
function vis(){{return S.filter(function(x){{return x.k=="all"||(x.k=="house"&&K=="house")}})}}
function draw(){{[].forEach.call(document.querySelectorAll("#gjk button"),function(b){{b.className=b.dataset.k==K?"on":""}});var v=vis(),dn=0;
document.getElementById("gjl").innerHTML=v.map(function(x){{var c=!!st[x.id];if(c)dn++;return '<li class="'+(c?"dn ":"")+(x.on?"":"op")+'"><label class="gjh"><input type="checkbox" data-id="'+x.id+'"'+(c?" checked":"")+'><div><b>'+x.n+(x.on?"":'<small class="gjop">필요하면</small>')+'</b><span>'+x.d+'</span></div></label><p class="gjt">'+x.tip+'</p>'+(x.l.length?'<div class="gjlk">'+x.l.map(function(a){{return '<a href="'+a[0]+'">'+a[1]+' ›</a>'}}).join("")+'</div>':'')+'</li>'}}).join("");
document.getElementById("gjpn").textContent=dn+" / "+v.length+" 완료";document.getElementById("gjbi").style.width=(v.length?dn/v.length*100:0)+"%";
[].forEach.call(document.querySelectorAll("#gjl input"),function(i){{i.onchange=function(){{if(i.checked)st[i.dataset.id]=1;else delete st[i.dataset.id];sv();draw()}}}})}}
[].forEach.call(document.querySelectorAll("#gjk button"),function(b){{b.onclick=function(){{K=b.dataset.k;sv();draw()}}}});
document.getElementById("gjrs").onclick=function(){{if(confirm("체크를 모두 지울까요?")){{st={{}};sv();draw()}}}};
document.getElementById("gjsv").onclick=function(){{var v=vis();WWHJ("plan",v.map(function(x,i){{return (st[x.id]?"[완료] ":"[  ] ")+(i+1)+". "+x.n}}).join("\\n"),this)}};draw()}})();</script>'''
    ld = {"@context": "https://schema.org", "@type": "HowTo", "name": "셀프 인테리어 공정 순서",
          "step": [{"@type": "HowToStep", "position": k + 1, "name": n, "text": d + ". " + tip} for k, (i, n, d, tip, l, kk, on) in enumerate(STEPS)]}
    page("gongjeong.html", "인테리어 공정 순서 플래너 — 철거부터 입주 청소까지 순서표·체크리스트 | 영진목재",
         "셀프·반셀프 인테리어 공정 순서: 철거→설비→전기→샷시→목공→타일→필름→도배→바닥→가구→마감. 공정별 이유와 시공팀 연결, 체크리스트 저장.", body, "/calc.html", ld)
