# 현장 근처 찾기(/geuncheo.html) — 전국 현장에서 철물점·인력사무소·장비 임대·폐기물·용달 등을 114 대신 바로 찾기
# 업체 정보는 저장하지 않고, 지도 앱(네이버·카카오·구글) 검색으로 넘겨줌 — 전국 어디서나, 정보가 낡지 않음.
# 글씨·버튼 크게(현장 어르신용), 한 번 누르면 지도 앱에서 근처 업체·전화번호.

CATS = [  # 키, 버튼 글자, 검색어, 작은 설명
    ("cheolmul", "철물점", "철물점", "피스·앙카·실리콘·공구"),
    ("inryeok", "인력사무소", "인력사무소", "일용직·잡부·조공"),
    ("jangbi", "장비 임대", "중장비 임대", "포크레인·스카이·지게차"),
    ("rental", "공구 렌탈", "공구 렌탈", "브레이커·코어·발전기"),
    ("pegi", "폐기물 처리", "건설폐기물 처리", "폐기물 수거·마대·컨테이너"),
    ("yongdal", "용달·화물", "용달 화물", "1톤·용달·화물차"),
    ("geonjae", "건재상", "건재상", "시멘트·벽돌·몰탈"),
    ("jeongi", "전기 자재", "전기자재", "전선·차단기·조명"),
    ("seolbi", "설비 자재", "설비자재 배관", "배관·수도·보일러 부속"),
    ("tile", "타일 매장", "타일", "타일·접착제·줄눈"),
    ("juyu", "주유소", "주유소", "장비 기름·경유"),
    ("sikdang", "기사식당", "기사식당", "현장 점심·함바"),
]


def gen(page, E, CTA, faqslide, TEL):
    import json
    btns = "".join(f'<button type="button" class="gcb" data-k="{k}" data-q="{E(q)}"><b>{E(n)}</b><span>{E(s)}</span></button>' for k, n, q, s in CATS)
    fq = [("114에 묻는 것과 뭐가 다른가요?", "버튼 한 번이면 지도 앱이 열려 지금 위치(또는 적은 동네) 근처 업체가 지도·전화번호·영업시간과 함께 바로 나옵니다. 여러 곳을 비교하고 누르면 바로 전화됩니다."),
          ("업체 정보는 어디서 나오나요?", "네이버지도·카카오맵·구글지도에 등록된 정보입니다. 이 페이지는 업체를 따로 저장하지 않고 지도 앱 검색으로 바로 연결해 줍니다. 영업 여부는 전화로 한 번 확인하세요."),
          ("현장 주소를 모르면요?", "'내 위치로 찾기'를 누르면 휴대폰 위치로 근처를 찾습니다. 위치 허용을 묻는 창이 뜨면 '허용'을 눌러 주세요. 동네 이름(예: 청주 오송읍)만 적어도 됩니다."),
          ("자재도 여기서 구할 수 있나요?", f"목재·합판·석고보드·단열재·데크 등은 대전 영진종합목재에서 원하는 크기로 재단해 전국 현장까지 용달로 보내 드립니다. 전화 {TEL}.")]
    body = f'''<section class="wrap sec"><p class="crumb"><a href="/">홈</a> › 현장 근처 찾기</p>
<h1>현장 근처 철물점·인력사무소·장비 임대·폐기물·용달 찾기</h1>
<p class="lead gcl">전국 어느 현장이든 <b>114에 물을 필요 없이</b> 버튼 한 번으로 근처 업체와 전화번호를 찾습니다.</p>
<div class="gcw"><label class="gcla">① 위치 — 비워 두면 내 위치로</label>
<div class="gcin"><input id="gcp" type="text" placeholder="동네 이름 (예: 청주 오송읍)" autocomplete="off"><button type="button" id="gcme" class="gcme">📍 내 위치로 찾기</button></div>
<p class="zqs" id="gcst">비워 두면 <b>내 위치(GPS) 근처</b>로 찾아요. 다른 현장을 찾을 땐 동네 이름을 적으세요.</p>
<label class="gcla">② 찾을 곳 누르기</label>
<div class="gcg">{btns}</div>
<div id="gcr" class="zqr" hidden></div></div>
<p class="small muted">업체 정보는 각 지도 앱에 등록된 내용입니다. 영업 여부·가격은 전화로 확인하세요.</p><p><a class="b o" href="/geuncheo/">📋 전국 지역별 인력사무소·건설폐기물 처리업체 목록(영업 중만, 매일 갱신)</a></p>
<div class="gcad"><b>🪵 목재·합판·석고·단열재·데크는 영진종합목재</b><span>원하는 크기로 재단해서 전국 현장까지 용달 배송 · 대전 유성대로 44</span><a class="b r" href="tel:{TEL.replace('-', '')}">📞 {TEL} 전화</a><a class="b o" href="/jaedan-baesong.html">재단·전국 배송 보기</a></div>
<h2>이럴 때 쓰세요</h2>
<ul class="gtip"><li>외지 현장에서 피스·실리콘이 떨어졌을 때 — <b>철물점</b></li><li>내일 잡부·조공이 한 명 더 필요할 때 — <b>인력사무소</b></li><li>포크레인·스카이·지게차가 필요할 때 — <b>장비 임대</b></li><li>철거 후 폐기물을 치워야 할 때 — <b>폐기물 처리</b></li><li>자재를 다른 현장으로 옮길 때 — <b>용달·화물</b></li><li>점심 먹을 곳 — <b>기사식당</b></li></ul>
<h2>자주 묻는 질문</h2>{faqslide(fq)}</section>
<style>.gcl{{font-size:19px}}.gcw{{background:#fff;border:2px solid #e4ded4;border-radius:18px;padding:16px;margin:14px 0}}.gcla{{display:block;font-size:19px;font-weight:900;margin:6px 0 8px}}
.gcin{{display:flex;gap:8px;flex-wrap:wrap}}.gcin input{{flex:1 1 220px;font-size:20px;padding:14px;border:2px solid #d8d0c4;border-radius:12px}}.gcme{{font-size:18px;font-weight:800;padding:14px 16px;border-radius:12px;border:0;background:#1D1B18;color:#fff}}
.zqs{{font-size:15px;color:#5e574e;margin:8px 0 14px}}.gcg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}}
.gcb{{display:flex;flex-direction:column;align-items:flex-start;gap:4px;text-align:left;padding:16px;border-radius:14px;border:2px solid #e4ded4;background:#f6f3ee;cursor:pointer}}.gcb b{{font-size:22px}}.gcb span{{font-size:14px;color:#5e574e}}.gcb.on{{border-color:#c62a1f;background:#fff3f2}}
.zqr{{display:block!important;margin-top:14px;background:#1D1B18;color:#fff;border-radius:14px;padding:16px}}.zqr h3{{color:#fff;line-height:1.4;margin:0 0 10px;font-size:20px}}.zqr>a{{display:block;width:100%;box-sizing:border-box;text-align:center;font-size:20px;font-weight:900;padding:16px;border-radius:12px;margin:8px 0;text-decoration:none}}
.zqr .nv{{background:#03C75A;color:#fff}}.zqr .kk{{background:#FEE500;color:#191919}}.zqr .gg{{background:#fff;color:#1D1B18}}.zqr small{{display:block;color:#ddd;margin-top:6px}}
.gcn{{margin-top:12px;background:#2a2622;border-radius:12px;padding:12px}}.gcni{{background:#fff;color:#1D1B18;border-radius:10px;padding:10px;margin:8px 0}}.gcni span{{display:block;font-size:14px;color:#5e574e;margin:4px 0}}.gcni a{{display:inline-block!important;font-size:16px!important;padding:10px 12px!important;margin:4px 6px 0 0!important}}.gcc{{background:#c62a1f;color:#fff}}.gcm{{background:#03C75A;color:#fff}}.gcad{{display:flex;flex-direction:column;gap:8px;background:#fff8e6;border:2px solid #f0c040;border-radius:16px;padding:16px;margin:16px 0}}.gcad b{{font-size:19px}}</style>
<script>(function(){{var P=document.getElementById("gcp"),S=document.getElementById("gcst"),R=document.getElementById("gcr"),L=null,cur=null;
try{{P.value=localStorage.getItem("gcp")||""}}catch(e){{}}
function enc(s){{return encodeURIComponent(s)}}
var GC=null;function near(t,n){{var box=document.createElement("div");box.className="gcn";box.innerHTML="<b>📋 내 위치 근처 등록 업체(영업 중) 불러오는 중…</b>";R.appendChild(box);
function dist(a,b,c,d){{var r=Math.PI/180,x=(d-b)*r*Math.cos((a+c)/2*r),y=(c-a)*r;return Math.sqrt(x*x+y*y)*6371}}
(GC?Promise.resolve(GC):fetch("/assets/gc/index.json?h="+Math.floor(Date.now()/36e5)).then(function(r){{return r.json()}})).then(function(ix){{GC=ix;var la=+L[0],lo=+L[1];var ks=Object.keys(ix.c).sort(function(a,b){{return dist(la,lo,ix.c[a][0],ix.c[a][1])-dist(la,lo,ix.c[b][0],ix.c[b][1])}}).slice(0,2);
return Promise.all(ks.map(function(k){{return fetch("/assets/gc/"+k+".json?d="+ix.d).then(function(r){{return r.json()}})}})).then(function(A){{var P=[].concat.apply([],A).filter(function(x){{return x[0]===t}});P.forEach(function(x){{x.d=dist(la,lo,x[4],x[5])}});P.sort(function(a,b){{return a.d-b.d}});P=P.slice(0,6);
box.innerHTML="<b>📋 내 위치 근처 "+n+" (공식 등록·영업 중, "+ix.d+" 기준)</b>"+P.map(function(x){{var q=enc(x[1]+" "+x[2].split(" ").slice(0,3).join(" "));return "<div class=gcni><b>"+x[1]+"</b> <small>약 "+x.d.toFixed(1)+"km"+(x[6]?" · "+x[6]:"")+"</small><span>"+x[2]+"</span>"+(x[3]?"<a class=gcc href='tel:"+x[3].replace(/-/g,"")+"'>📞 "+x[3]+"</a>":"")+"<a class=gcm href='https://map.naver.com/p/search/"+q+"' target=_blank rel=noopener>지도·전화번호</a></div>"}}).join("")+"<small>출처: 행정안전부 인허가데이터(폐업 제외, 매일 갱신). <a href='/geuncheo/' style='color:#ffd65a'>지역별 전체 목록 ›</a></small>"}})}}).catch(function(){{box.innerHTML="<small>근처 등록 업체 목록을 못 불러왔어요. 위 지도 버튼으로 찾아 주세요.</small>"}})}}
function tw(){{var d=new Date(),h=d.getHours(),w=d.getDay(),m='';if(h<7||h>=19)m='지금은 이른 아침·저녁 시간이라 문 닫은 곳이 많아요. 영업시간을 꼭 확인하세요.';else if(w===0)m='오늘은 일요일이라 쉬는 곳이 많아요. 영업 중 표시를 확인하세요.';return m?'<small style="color:#ffd65a">⏰ '+m+'</small>':''}}
function show(b){{var q=b.getAttribute("data-q"),n=b.querySelector("b").textContent,p=P.value.trim();try{{localStorage.setItem("gcp",p)}}catch(e){{}}
var qq=p?(p+" "+q):q,g=L?("https://www.google.com/maps/search/"+enc(q)+"/@"+L[0]+","+L[1]+",14z"):("https://www.google.com/maps/search/?api=1&query="+enc(p?qq:("내 주변 "+q)));
var nv="https://map.naver.com/p/search/"+enc(qq);if(L&&!p){{var x=L[1]*20037508.34/180,y=Math.log(Math.tan((90+ +L[0])*Math.PI/360))/(Math.PI/180)*20037508.34/180;nv+="?c="+x.toFixed(2)+","+y.toFixed(2)+",15,0,0,0,dh"}}
R.innerHTML="<h3>"+(p?p+" ":(L?"내 위치 근처 ":"근처 "))+n+" 찾기</h3><a class=nv href='"+nv+"' target=_blank rel=noopener>네이버지도에서 보기</a>"+(L&&!p?"<a class=gg href='"+g+"' target=_blank rel=noopener>구글지도에서 보기 (내 위치 근처)</a>":"<a class=kk href='https://map.kakao.com/link/search/"+enc(qq)+"' target=_blank rel=noopener>카카오맵에서 보기</a><a class=gg href='"+g+"' target=_blank rel=noopener>구글지도에서 보기</a>")+"<small>지도 목록에 <b>영업 중·영업 종료·영업시간</b>이 함께 나와요(네이버·카카오는 위쪽 ‘영업중’ 필터를 누르면 지금 문 연 곳만). 업체를 누르면 전화 버튼으로 바로 연결됩니다.</small>"+tw()+"";
R.hidden=false;var kk=b.getAttribute("data-k");if(L&&(kk==="inryeok"||kk==="pegi"))near(kk==="inryeok"?"J":"W",n);[].forEach.call(document.querySelectorAll(".gcb"),function(x){{x.classList.toggle("on",x===b)}});R.scrollIntoView({{behavior:"smooth",block:"start"}});
try{{if(window.WWC)WWC("geuncheo_"+b.getAttribute("data-k"))}}catch(e){{}}}}
function loc(cb){{if(!navigator.geolocation){{S.textContent="이 휴대폰은 위치 찾기를 지원하지 않아요. 동네 이름을 적어 주세요.";cb&&cb();return}}
S.textContent="📍 내 위치 찾는 중… 위치 허용 창이 뜨면 '허용'을 눌러 주세요";navigator.geolocation.getCurrentPosition(function(p){{L=[p.coords.latitude.toFixed(5),p.coords.longitude.toFixed(5)];P.value="";S.textContent="✔ 내 위치 근처로 찾아요.";cb&&cb()}},
function(){{S.textContent="위치를 못 찾았어요. 휴대폰 위치(GPS)를 켜거나 동네 이름(예: 청주 오송읍)을 적어 주세요.";cb&&cb()}},{{enableHighAccuracy:true,timeout:10000,maximumAge:300000}})}}
[].forEach.call(document.querySelectorAll(".gcb"),function(b){{b.onclick=function(){{cur=b;if(!P.value.trim()&&!L){{loc(function(){{show(b)}})}}else show(b)}}}});
document.getElementById("gcme").onclick=function(){{loc(function(){{if(cur)show(cur)}})}};}})();</script>''' + CTA
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}
    page("geuncheo.html", "현장 근처 철물점·인력사무소·장비 임대·폐기물·용달 찾기 — 114 대신 한 번에 | 영진목재",
         "전국 어느 현장이든 근처 철물점·인력사무소·포크레인 장비 임대·건설폐기물 처리·용달 화물·건재상을 버튼 한 번으로 지도·전화번호까지. 큰 글씨, 내 위치로 찾기.", body, jsonld=ld)
