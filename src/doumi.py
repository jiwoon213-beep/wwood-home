# 셀프 인테리어 질문 마법사 (/doumi.html) — 질문 4개 → 시공법·만들기·가격·영상·계산기 묶음
# 링크만 모아 주는 안내. 시공비·소요일 숫자 없음.
import json, os

SP = [("living", "거실·방"), ("kitchen", "주방"), ("bath", "욕실"), ("entry", "현관·복도"), ("veranda", "베란다"), ("yard", "마당·옥상·농막"), ("shop", "가게·카페")]
TK = [("wall", "벽 꾸미기"), ("floor", "바닥"), ("ceil", "천장"), ("door", "문·중문"), ("furn", "수납·가구 만들기"), ("insul", "단열·결로·곰팡이"), ("out", "데크·울타리·외벽")]
HOW = [("diy", "직접 해볼래요"), ("pro", "시공 맡기고 싶어요"), ("mat", "자재만 사러 갈래요")]
ST = [("modern", "모던·미니멀"), ("natural", "내추럴·우드"), ("japandi", "간살·재팬디"), ("classic", "클래식"), ("hotel", "호텔·고급"), ("kids", "아이방"), ("cafe", "카페 느낌"), ("", "상관없음")]

# 할 일별 기본 묶음: (주소, 이름, 종류)  종류: s 시공법, m 만들기, g 가격, q Q&A, v 영상, c 계산기, y 시공팀
T = {
 "wall": [("/sigongbeop/tempa-byeok.html", "템바보드 벽 시공", "s"), ("/sigongbeop/film-sigong.html", "인테리어 필름 시공", "s"), ("/sigongbeop/seokgo-byeok.html", "석고보드 벽 시공", "s"), ("/sigongbeop/heumeum-byeok.html", "흡음보드 벽", "s"), ("/mandeul/gabyeok.html", "가벽 만들기", "m"), ("/mandeul/byeokseonban.html", "벽선반 만들기", "m"), ("/gagyeok/tempa-board.html", "템바보드 가격", "g"), ("/gagyeok/interior-film.html", "인테리어 필름 가격", "g"), ("/gagyeok/seokgo-gagyeok.html", "석고보드 가격", "g"), ("/video/wall.html", "벽 시공 영상", "v"), ("/calc.html", "석고보드 몇 장? 계산기", "c"), ("/yeongyeol/film.html", "필름 시공팀 연결", "y"), ("/yeongyeol/mokgong.html", "목공 시공팀 연결", "y")],
 "floor": [("/sigongbeop/decotile.html", "데코타일 셀프 시공", "s"), ("/sigongbeop/gangmaru.html", "강마루 셀프 시공", "s"), ("/sigongbeop/hapan-badak-deotbang.html", "합판 바닥 덧방", "s"), ("/sigongbeop/isopink-badak.html", "바닥 단열", "s"), ("/qna/badakjae-goreugi.html", "바닥재 고르는 법", "q"), ("/qna/decotile-deotbang.html", "데코타일 덧방", "q"), ("/video/floor.html", "바닥 시공 영상", "v"), ("/calc.html", "데코타일·마루 박스 수 계산기", "c"), ("/yeongyeol/decotile.html", "데코타일 시공팀 연결", "y"), ("/yeongyeol/maru.html", "마루 시공팀 연결", "y")],
 "ceil": [("/sigongbeop/rubaa-cheonjang.html", "루바 천장 시공", "s"), ("/sigongbeop/seokgo-cheonjang.html", "석고보드 천장 시공", "s"), ("/sigongbeop/molding-georebatgi.html", "천장 몰딩 시공", "s"), ("/sigongbeop/minus-molding-sigong.html", "마이너스 몰딩", "s"), ("/gagyeok/hinoki-ruba.html", "히노끼 루바 가격", "g"), ("/gagyeok/spruce-ruba.html", "스프러스 루바 가격", "g"), ("/gagyeok/molding-gagyeok.html", "몰딩 가격", "g"), ("/calc.html", "몰딩 길이 계산기", "c"), ("/yeongyeol/mokgong.html", "목공 시공팀 연결", "y")],
 "door": [("/sigongbeop/jungmun.html", "원슬라이딩 중문 셀프 설치", "s"), ("/sigongbeop/munteul-gyoche.html", "방문 교체 방법", "s"), ("/qna/3yeondong-self.html", "3연동 중문 셀프 시공", "q"), ("/gagyeok/door-gagyeok.html", "방문·도어 가격", "g"), ("/yerim/", "예림 중문·도어 사진", "g"), ("/younglim/", "영림 도어·중문 사진", "g"), ("/video/door.html", "문·중문 영상", "v"), ("/calc.html", "문짝·중문 크기 계산기", "c"), ("/yeongyeol/mokgong.html", "문·중문 시공 연결", "y")],
 "furn": [("/mandeul/chaekjang.html", "책장·수납장 만들기", "m"), ("/mandeul/sinbaljang.html", "신발장 만들기", "m"), ("/mandeul/geosiljang.html", "거실장 만들기", "m"), ("/mandeul/teibeul.html", "원목 테이블 만들기", "m"), ("/mandeul/cube.html", "수납 큐브 만들기", "m"), ("/gagyeok/jipseong-gagyeok.html", "집성판 가격", "g"), ("/gagyeok/hapan-gagyeok.html", "합판 가격", "g"), ("/cut.html", "목재 재단 미리보기", "c"), ("/video/furniture.html", "가구 만들기 영상", "v"), ("/yeongyeol/gagu.html", "가구 제작 연결", "y")],
 "insul": [("/sigongbeop/isopink-badak.html", "아이소핑크 바닥 단열", "s"), ("/mandeul/dannyeolbyeok.html", "벽 단열 만들기", "m"), ("/qna/chang-gyeolro.html", "창틀 결로 줄이기", "q"), ("/qna/changmun-oepung.html", "창문 외풍 막기", "q"), ("/qna/byeokji-gompang.html", "벽지 곰팡이 제거", "q"), ("/qna/dannyeol-duggae.html", "단열재 두께", "q"), ("/gagyeok/danyeol-gagyeok.html", "단열재 가격", "g"), ("/calc.html", "단열재 장수 계산기", "c"), ("/knauf/", "단열재·석고보드 제품", "g")],
 "out": [("/mandeul/deck.html", "작은 데크 만들기", "m"), ("/sigongbeop/hapdeck-sigong.html", "합성데크 시공", "s"), ("/sigongbeop/deck-nangan.html", "데크 난간 만들기", "s"), ("/sigongbeop/oilstain.html", "오일스테인 칠하기", "s"), ("/mandeul/ultari.html", "목재 울타리 만들기", "m"), ("/sigongbeop/siding-oebyeok.html", "사이딩 외벽 시공", "s"), ("/gagyeok/deck-gagyeok.html", "데크 가격", "g"), ("/gagyeok/siding-gagyeok.html", "사이딩 가격", "g"), ("/video/deck.html", "데크 영상", "v"), ("/calc.html", "데크 자재 계산기", "c"), ("/yeongyeol/siding.html", "사이딩·외벽 시공(직접 시공·전국)", "y")],
}
# 공간별로 앞에 붙일 것
S = {
 "kitchen": [("/mandeul/sangbujang.html", "주방 상부장 만들기", "m"), ("/mandeul/renjidae.html", "주방 렌지대 만들기", "m"), ("/mandeul/sinkmunjjak.html", "싱크대 문짝 만들기", "m"), ("/mandeul/aillaendeu.html", "아일랜드 작업대 만들기", "m"), ("/video/kitchen.html", "주방 영상", "v")],
 "bath": [("/sigongbeop/yoksil-tile.html", "욕실 벽 타일 셀프 시공", "s"), ("/sigongbeop/silicone-julnun.html", "욕실 실리콘 다시 쏘기", "s"), ("/yeongyeol/tile.html", "타일 시공팀 연결", "y")],
 "entry": [("/mandeul/hyeongwanbench.html", "현관 수납벤치 만들기", "m"), ("/mandeul/sinbaljang.html", "신발장 만들기", "m"), ("/sigongbeop/jungmun.html", "현관 중문 셀프 설치", "s")],
 "veranda": [("/mandeul/beranda.html", "베란다 선반 만들기", "m"), ("/mandeul/silwoegi.html", "실외기 커버 만들기", "m"), ("/mandeul/hwabundae.html", "계단식 화분대 만들기", "m")],
 "yard": [("/mandeul/pyeongsang.html", "원목 평상 만들기", "m"), ("/mandeul/tutbat.html", "텃밭상자 만들기", "m"), ("/mandeul/yaoeteibeul.html", "야외 테이블 만들기", "m"), ("/mandeul/jangjak.html", "장작 보관대 만들기", "m")],
 "shop": [("/trend/cafe.html", "카페·오픈 공간 인테리어", "g"), ("/sigongbeop/osb-byeok.html", "OSB 합판 벽", "s"), ("/sigongbeop/heumeum-byeok.html", "흡음보드 벽", "s")],
 "living": [("/trend/", "인테리어 트렌드 8가지", "g")],
}
KN = {"s": "시공법", "m": "만들기", "g": "자재·가격", "q": "Q&A", "v": "영상", "c": "계산기", "y": "시공 연결"}


def body(E, root):
    T2 = {k: [x for x in v if os.path.exists(root + "/.." + x[0] + ("index.html" if x[0].endswith("/") else ""))] for k, v in T.items()}
    S2 = {k: [x for x in v if os.path.exists(root + "/.." + x[0] + ("index.html" if x[0].endswith("/") else ""))] for k, v in S.items()}
    data = json.dumps({"T": T2, "S": S2, "K": KN}, ensure_ascii=False)
    def grp(nm, q, opts):
        return f'<fieldset class="dq" data-q="{q}"><legend>{nm}</legend><div class="dqo">' + "".join(f'<button type="button" data-v="{v}">{E(l)}</button>' for v, l in opts) + "</div></fieldset>"
    return (f'<section class="wrap sec"><h1>셀프 인테리어 도우미</h1><p class="lead">질문 4개만 누르면 필요한 <b>시공법·만들기·자재 가격·영상·계산기</b>를 한 번에 모아 드립니다. 고른 결과는 주소로 저장되니 가족·시공팀에게 그대로 보내도 됩니다.</p>'
            f'<div class="dwz">{grp("1. 어디를 바꾸나요?", "sp", SP)}{grp("2. 무엇을 하고 싶나요?", "tk", TK)}{grp("3. 어떻게 할 생각인가요?", "how", HOW)}{grp("4. 원하는 느낌은?", "st", ST)}</div>'
            '<div id="dres" class="dres" hidden></div></section>'
            f'<script>window.DOUMI={data};</script>'
            "<script>(function(){var D=window.DOUMI,sel={};var qs=new URLSearchParams(location.search);"
            "var ST={modern:'/trend/modern.html',natural:'/trend/natural.html',japandi:'/trend/japandi.html',classic:'/trend/classic.html',hotel:'/trend/hotel.html',kids:'/trend/kids.html',cafe:'/trend/cafe.html'};"
            "function esc(s){return s.replace(/[&<>\"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]})}"
            "function draw(){document.querySelectorAll('.dq').forEach(function(f){f.querySelectorAll('button').forEach(function(b){b.classList.toggle('on',sel[f.dataset.q]===b.dataset.v)})});"
            "var r=document.getElementById('dres');if(!sel.tk){r.hidden=true;return;}"
            "var L=[],seen={};function add(x){if(!seen[x[0]]){seen[x[0]]=1;L.push(x)}}"
            "(D.S[sel.sp]||[]).forEach(function(x){if(sel.sp=='living'||['furn','door','wall','floor'].indexOf(sel.tk)>=0||sel.sp=='bath'||sel.sp=='yard')add(x)});(D.T[sel.tk]||[]).forEach(add);"
            "if(sel.st&&ST[sel.st])L.unshift([ST[sel.st],'원하는 느낌: 스타일 모아 보기','g']);"
            "var ord=sel.how=='pro'?'ygsvcqm':sel.how=='mat'?'gcsmqvy':'smqvcgy';L.sort(function(a,b){return ord.indexOf(a[2])-ord.indexOf(b[2])});"
            "if(sel.how!='pro')L=L.filter(function(x){return x[2]!='y'||sel.how=='pro'});"
            "var h='<h2>추천 순서대로 보세요</h2><ol class=\"dli\">'+L.map(function(x){return '<li><a href=\"'+x[0]+'\"><small>'+D.K[x[2]]+'</small><b>'+esc(x[1])+'</b><i>›</i></a></li>'}).join('')+'</ol>';"
            "h+=sel.how=='pro'?'<p class=\"small muted\">시공은 매장에서 접수한 뒤 공정에 맞는 시공팀을 연결해 드립니다. 비용은 현장을 보고 정해집니다.</p>':'<p class=\"small muted\">자재·재단은 매장에서 한 번에 준비해 드립니다. 이 화면을 보여주시면 됩니다.</p>';"
            "h+='<p><a class=\"b r\" href=\"/visit.html\">매장 길찾기</a> <a class=\"b o\" href=\"tel:0425452900\">전화 042-545-2900</a> <button type=\"button\" class=\"b o\" id=\"dshare\">이 결과 공유</button></p>';"
            "r.innerHTML=h;r.hidden=false;document.getElementById('dshare').onclick=function(){var u=location.href;if(navigator.share)navigator.share({title:'셀프 인테리어 도우미 결과',url:u}).catch(function(){});else if(navigator.clipboard)navigator.clipboard.writeText(u).then(function(){alert('주소를 복사했어요')})};}"
            "function save(){var p=new URLSearchParams();for(var k in sel)if(sel[k])p.set(k,sel[k]);history.replaceState(null,'','?'+p.toString());}"
            "document.querySelectorAll('.dq').forEach(function(f){var q=f.dataset.q;if(qs.get(q)!==null)sel[q]=qs.get(q);f.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;sel[q]=b.dataset.v;save();draw();try{if(window.gtag)gtag('event','doumi_pick',{q:q,v:b.dataset.v})}catch(_){}"
            "if(q=='tk'||(q!='st'&&sel.tk)){}var n=f.nextElementSibling;if(n&&n.classList.contains('dq')&&!sel[n.dataset.q])n.scrollIntoView({behavior:'smooth',block:'center'});else if(sel.tk&&q=='st')document.getElementById('dres').scrollIntoView({behavior:'smooth'});})});draw();})();</script>")
