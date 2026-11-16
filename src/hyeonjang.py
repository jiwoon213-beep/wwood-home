# 내 현장함(/hyeonjang.html) — 손님 휴대폰(localStorage)에 저장한 재단표·미리 재단 주문을 모아 보는 화면. 서버 저장 없음.

def gen(page, E, CTA, TEL):
    T = TEL.replace("-", "")
    body = f'''<section class="wrap sec"><h1>내 현장함</h1>
<p class="lead">저장한 재단표·계산 결과·공정표와 미리 재단 주문을 모아 둡니다. 이 휴대폰(브라우저)에만 저장돼요. 매장에서 이 화면을 보여 주시면 그대로 준비해 드립니다.</p>
<div id="hjl" class="hjl"></div>
<div class="hjem" id="hjem" hidden><b>아직 저장한 게 없어요</b><span>재단 미리보기에서 크기를 넣고 <u>내 현장함에 저장</u>이나 <u>미리 재단 주문하기</u>를 누르세요.</span><a class="b r" href="/cut.html">재단 미리보기 열기 ›</a></div>
<h2>미리 재단 주문은 이렇게</h2>
<ol class="sstp"><li><i>1</i><p>재단 미리보기에서 크기를 넣고 <b>미리 재단 주문하기</b> → 주문서 보내기</p></li><li><i>2</i><p><b>매장에 전화</b>해 주문번호를 알려 주세요({E(TEL)}). 메일은 바로 확인하지 못할 수 있어요.</p></li><li><i>3</i><p><b>입금(결제) 확인 후 재단</b>을 시작합니다. 다 되면 연락드려요.</p></li></ol>
<div class="row"><a class="b r" href="/cut.html">재단 미리보기</a><a class="b" href="/calc.html">자재 계산기</a><a class="b" href="/yeongyeol/">시공팀 연결</a></div></section>{CTA}
<style>.hjl{{display:flex;flex-direction:column;gap:10px;margin:14px 0}}.hjc{{background:#fff;border:1px solid #ece6dc;border-radius:16px;padding:14px;display:flex;flex-direction:column;gap:6px}}.hjc.o{{border:2px solid #c41a1f}}
.hjt{{display:flex;justify-content:space-between;gap:8px;align-items:center}}.hjt b{{font-size:16px}}.hjt small{{color:#8a8378;font-size:12px;white-space:nowrap}}
.hjbg{{display:inline-block;background:#c41a1f;color:#fff;border-radius:999px;padding:2px 9px;font-size:12px;font-weight:800;margin-right:4px}}.hjbg.s{{background:#1D1B18}}
.hjno{{font-size:22px;font-weight:900;color:#c41a1f;letter-spacing:.5px}}.hjs{{white-space:pre-line;font-size:14px;line-height:1.6;color:#3b3731;background:#faf8f4;border-radius:10px;padding:10px 12px;margin:0}}
.hjw{{background:#fff4e5;border-radius:10px;padding:8px 12px;font-size:13.5px;line-height:1.5}}.hja{{display:flex;flex-wrap:wrap;gap:6px}}.hja .b{{font-size:14px;padding:9px 13px}}.hjx{{background:none;border:0;color:#8a8378;font-size:13px;text-decoration:underline;cursor:pointer;margin-left:auto}}
.hjem{{display:flex;flex-direction:column;gap:6px;background:#fff;border:1px dashed #d8d0c2;border-radius:16px;padding:18px;text-align:center}}.hjem u{{text-decoration:none;font-weight:800}}</style>
<script>(function(){{function L(){{try{{return JSON.parse(localStorage.getItem("wwHJ")||"[]")}}catch(e){{return[]}}}}function S(a){{try{{localStorage.setItem("wwHJ",JSON.stringify(a))}}catch(e){{}}}}
function esc(t){{return String(t||"").replace(/[&<>"]/g,function(c){{return{{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[c]}})}}
function dt(ts){{var d=new Date(ts);return (d.getMonth()+1)+"/"+d.getDate()+" "+("0"+d.getHours()).slice(-2)+":"+("0"+d.getMinutes()).slice(-2)}}
function draw(){{var a=L(),el=document.getElementById("hjl");document.getElementById("hjem").hidden=!!a.length;
el.innerHTML=a.map(function(o,i){{var od=o.t=="order";return '<div class="hjc'+(od?' o':'')+'"><div class="hjt"><b><span class="hjbg'+(od?'':' s')+'">'+(od?'미리 주문':({{calc:'계산',plan:'공정표'}}[o.t]||'재단표'))+'</span>'+esc(o.title)+'</b><small>'+dt(o.ts)+'</small></div>'
+(od?'<div class="hjno">'+esc(o.no)+'</div><div class="hjw">'+esc(o.how)+(o.date?' · '+esc(o.date):'')+' — 전화로 주문번호를 알려 주셨나요? <b>입금 확인 후 재단</b>합니다.</div>':'')
+'<p class="hjs">'+esc(o.sum)+'</p><div class="hja"><a class="b o" href="'+esc(o.url)+'">다시 열기</a>'+(od?'<a class="b r" href="tel:{T}">매장 전화</a>':'')+'<button class="hjx" data-i="'+i+'">지우기</button></div></div>'}}).join("");
[].forEach.call(el.querySelectorAll(".hjx"),function(b){{b.onclick=function(){{if(!confirm("이 항목을 지울까요?"))return;var a=L();a.splice(+b.dataset.i,1);S(a);draw()}}}})}}draw()}})();</script>'''
    page("hyeonjang.html", "내 현장함 — 저장한 재단표·미리 재단 주문 | 영진목재", "재단 미리보기에서 저장한 재단표와 미리 재단 주문(주문번호)을 한곳에서. 매장에서 화면만 보여 주시면 준비해 드립니다.", body, "/cut.html")
