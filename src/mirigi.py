# -*- coding: utf-8 -*-
"""공사 미리보기(/mirigi.html) — 사진을 찍고 네 모서리를 찍으면 데크·템바보드·루바·벽·사이딩·타일 무늬를 원근에 맞게 입혀 보여 줌.
무늬는 그림으로 직접 만든 것(다른 회사 사진 아님). 크기를 넣으면 gyeonjeok.data()의 판매 단위·기준가로 수량·자재비 계산. 소요 시간·시공비는 넣지 않음."""
import json
import gyeonjeok as GJ


def gen(page, P, E, CTA, faqslide, TEL, PROD=None, ROOT="."):
    D = {w["k"]: w for w in GJ.data(P)}
    import os
    pc = json.load(open(os.path.join(ROOT, "data", "prodcolor.json"), encoding="utf-8")) if os.path.exists(os.path.join(ROOT, "data", "prodcolor.json")) else {}
    PR = {}
    for p_ in (PROD or []):
        c_ = pc.get(str(p_["id"]))
        if c_: PR.setdefault(c_["m"], []).append([p_["name"], c_["c"], p_["img"], f"https://wwood.kr/home/mall/shoplist.php?idx={p_['id']}&pmode=view"])
    prj = json.dumps({k: v[:14] for k, v in PR.items()}, ensure_ascii=False, separators=(",", ":"))
    pick = lambda k: [{"n": i["n"], "u": i["u"], "a": i["a"], "p": i["p"], "l": i["l"]} for i in D.get(k, {}).get("it", []) if i["a"]][:8]
    M = {"deck": pick("deck"), "tempa": pick("art"), "ruba": pick("ceil_ruba"), "gyp": pick("wall_gyp"), "siding": pick("siding")}
    js = json.dumps(M, ensure_ascii=False, separators=(",", ":"))
    fq = faqslide([
        ("사진이 어디로 올라가나요?", "올라가지 않습니다. 사진은 휴대폰 안에서만 그림을 입히고, 저장·공유도 손님이 직접 할 때만 됩니다."),
        ("실제와 똑같이 보이나요?", "자재 무늬를 원근에 맞춰 입힌 미리보기라 느낌을 보는 용도입니다. 실제 색·결은 매장에서 실물로 확인하세요."),
        ("공사 기간이나 시공비도 나오나요?", "현장 상태에 따라 크게 달라서 숫자로 보여 드리지 않습니다. 저장한 사진과 크기를 보내 주시면 상담해 드립니다(042-545-2900)."),
        ("네 모서리는 어떻게 찍나요?", "자재를 입힐 곳(데크 바닥, 벽면 등)의 네 귀퉁이에 동그라미 4개를 손가락으로 끌어다 놓으면 됩니다. 멀리 있는 쪽은 좁게, 가까운 쪽은 넓게 맞추면 원근이 살아납니다.")])
    body = f'''<section class="wrap sec gg mrw"><p class="crumb"><a href="/calc.html">자재 계산기</a> › 공사 미리보기</p>
<div class="mrhero"><span class="mrtag">공사 미리보기</span><h1>찍으면, 공사 후 모습이 보여요</h1>
<p>마당·벽·천장을 찍고 네 모서리만 맞추면 데크·템바보드·루바·벽 색이 실제처럼 입혀지고 <b>예상 자재비</b>까지 나옵니다.</p>
<div class="mrs"><label class="mrb"><input type="file" accept="image/*" capture="environment" id="mrc"><i>CAM</i><span>사진 찍기</span></label><label class="mrb mrg"><input type="file" accept="image/*" id="mra"><span>앨범에서 고르기</span></label></div>
<button type="button" class="mrex" id="mrd">예시 사진으로 먼저 해 보기 ›</button></div>
<ol class="mrst"><li><i>1</i>사진 올리기</li><li><i>2</i>모서리 4개 맞추기</li><li><i>3</i>자재·색 고르기</li></ol>
<div class="mrcard"><div class="mrv" id="mrv"><canvas id="mrcv"></canvas><div id="mrh"></div><p class="mrtip" id="mrtip">빨간 점 4개를 바꿀 곳 네 귀퉁이에 끌어다 놓으세요</p></div></div>
<h2 class="mrh2">자재</h2><div class="mrt" id="mrt"><button type="button" data-m="deck" class="on"><b></b>데크</button><button type="button" data-m="tempa"><b></b>템바보드</button><button type="button" data-m="ruba"><b></b>루바</button><button type="button" data-m="paint"><b></b>벽 색</button><button type="button" data-m="siding"><b></b>사이딩</button><button type="button" data-m="tile"><b></b>타일</button></div>
<h2 class="mrh2">제품·색상 <small style="font-weight:600;color:#8a8378;font-size:12.5px">우리 매장 제품 사진</small></h2><div class="mrcol" id="mrcol"></div>
<h2 class="mrh2">실제 크기</h2><div class="gjr"><label>가로<input id="mw" type="number" inputmode="decimal" step="0.1" value="3.6"><i>m</i></label><label>세로<input id="mh" type="number" inputmode="decimal" step="0.1" value="2.4"><i>m</i></label><label>원래 그늘<select id="msh"><option value="0.35">살리기</option><option value="0.15">조금</option><option value="0">없음</option></select></label></div>
<div class="mro" id="mro"></div>
<button type="button" class="mrsave" id="mrsv">사진 저장·카톡 공유</button>
<div class="mract"><a href="tel:{TEL}">이대로 견적 문의</a><a id="mrcalc" href="/deck-gyesan.html">자세히 계산 ›</a></div>
<p class="mrnote">사진은 휴대폰 안에서만 처리되고 어디에도 올라가지 않아요. 무늬는 느낌을 보는 미리보기이고, 금액은 홈페이지 소매 기준가(부가세 별도) 자재비만입니다. 공사 기간·시공비는 현장 상담으로 안내합니다.</p></section>
<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{fq}</section>{CTA}
<style>.mrhero{{background:radial-gradient(120% 90% at 100% 0,#3a332b 0,#1D1B18 62%);color:#fff;border-radius:24px;padding:24px 20px 18px;text-align:center;box-shadow:0 14px 34px rgba(29,27,24,.22)}}.mrtag{{display:inline-block;font-size:12px;font-weight:800;color:#f5d27a;border:1px solid rgba(245,210,122,.45);border-radius:999px;padding:4px 11px}}.mrhero h1{{color:#fff;font-size:25px;margin:12px 0 8px;letter-spacing:-.02em;word-break:keep-all}}.mrhero p{{color:rgba(255,255,255,.78);font-size:14.5px;line-height:1.6;margin:0 0 16px;word-break:keep-all}}.mrhero p b{{color:#fff}}
.mrs{{display:flex;gap:8px}}.mrb{{flex:1;position:relative;display:flex;align-items:center;justify-content:center;gap:8px;height:54px;border-radius:14px;background:#fff;color:#1D1B18;font-weight:800;font-size:15.5px;cursor:pointer}}.mrb i{{display:none}}.mrb.mrg{{background:rgba(255,255,255,.1);color:#fff;border:1px solid rgba(255,255,255,.25)}}.mrb input{{position:absolute;inset:0;opacity:0;cursor:pointer}}.mrex{{margin-top:12px;background:none;border:0;color:#f5d27a;font:inherit;font-weight:700;font-size:14px;cursor:pointer}}
.mrst{{list-style:none;display:grid;grid-template-columns:repeat(3,1fr);gap:6px;padding:0;margin:14px 0}}.mrst li{{display:flex;flex-direction:column;align-items:center;gap:5px;background:#fff;border:1px solid #e9e3d9;border-radius:14px;padding:10px 4px;font-size:12.5px;font-weight:700;text-align:center;word-break:keep-all}}.mrst i{{font-style:normal;width:22px;height:22px;border-radius:50%;background:#1D1B18;color:#fff;font-size:12px;display:flex;align-items:center;justify-content:center}}
.mrcard{{background:#fff;border:1px solid #e9e3d9;border-radius:20px;padding:8px;box-shadow:0 8px 24px rgba(0,0,0,.07)}}.mrv{{position:relative;border-radius:14px;overflow:hidden;background:#2a2620;touch-action:none;user-select:none}}.mrv canvas{{display:block;width:100%;height:auto}}#mrh i{{position:absolute;width:30px;height:30px;margin:-15px 0 0 -15px;border-radius:50%;border:3px solid #fff;background:#c41a1f;box-shadow:0 0 0 6px rgba(196,26,31,.25),0 2px 8px rgba(0,0,0,.4);touch-action:none;cursor:grab}}.mrtip{{position:absolute;left:10px;right:10px;top:10px;margin:0;background:rgba(0,0,0,.6);backdrop-filter:blur(4px);color:#fff;font-size:12.5px;border-radius:10px;padding:7px 10px;text-align:center}}
.mrh2{{font-size:15px;margin:18px 0 8px;font-weight:800}}.mrt{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}}.mrt button{{display:flex;flex-direction:column;align-items:stretch;gap:6px;padding:6px 6px 9px;border-radius:14px;border:1.5px solid #e6dfd5;background:#fff;font:inherit;font-weight:800;font-size:13.5px;cursor:pointer;color:#1D1B18}}.mrt button b{{display:block;height:46px;border-radius:9px;background-size:cover;background-position:center}}.mrt button.on{{border-color:#1D1B18;box-shadow:0 0 0 1.5px #1D1B18}}
.mrcol{{display:flex;gap:8px;overflow-x:auto;padding-bottom:4px;scrollbar-width:none}}.mrcol::-webkit-scrollbar{{display:none}}.mrcol button{{flex:none;display:flex;align-items:center;gap:7px;height:40px;padding:0 13px 0 6px;border-radius:999px;border:1.5px solid #e6dfd5;background:#fff;font:inherit;font-size:13px;font-weight:700;cursor:pointer;color:#1D1B18}}.mrcol button i{{width:28px;height:28px;border-radius:50%;box-shadow:inset 0 0 0 1px rgba(0,0,0,.12)}}.mrcol button.on{{border-color:#1D1B18;box-shadow:0 0 0 1px #1D1B18}}.mrcol button img{{width:30px;height:30px;border-radius:50%;object-fit:cover;background:#eee}}.mrcol button span{{max-width:110px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}.mrsel{{display:flex;gap:10px;align-items:center;background:rgba(255,255,255,.08);border-radius:12px;padding:8px;margin-bottom:10px}}.mrsel img{{width:52px;height:52px;border-radius:10px;object-fit:cover;background:#fff}}.mrsel span{{display:flex;flex-direction:column;font-size:13.5px;font-weight:700}}.mrsel small{{font-size:11.5px;color:rgba(255,255,255,.6);font-weight:600}}.mrsel a{{color:#f5d27a!important;font-size:12.5px;margin-top:2px}}
.gjr{{display:flex;gap:8px}}.gjr label{{flex:1;display:flex;flex-direction:column;font-size:12.5px;font-weight:700;color:#6b645a;position:relative}}.gjr input,.gjr select{{height:46px;border:1.5px solid #e6dfd5;border-radius:12px;padding:0 28px 0 12px;font:inherit;font-size:17px;font-weight:800;margin-top:4px;width:100%;box-sizing:border-box;background:#fff;color:#1D1B18}}.gjr select{{font-size:14px;padding:0 8px}}.gjr i{{position:absolute;right:10px;bottom:13px;font-style:normal;color:#8a8378;font-size:13px}}
.mro{{background:#1D1B18;color:#fff;border-radius:18px;padding:16px 18px;margin:16px 0 10px}}.mro:before{{content:"예상 자재비";display:block;font-size:12.5px;font-weight:700;color:rgba(255,255,255,.6);margin-bottom:2px}}.mro b{{color:#f5d27a;font-size:28px;letter-spacing:-.02em}}.mro p{{margin:6px 0 0;font-size:13.5px;line-height:1.5;color:rgba(255,255,255,.85)}}.mro select{{width:100%;margin-top:10px;height:42px;border-radius:10px;border:0;font:inherit;font-size:13.5px;padding:0 8px;background:rgba(255,255,255,.95)}}
.mrsave{{width:100%;height:56px;border:0;border-radius:16px;background:#c41a1f;color:#fff;font:inherit;font-size:17px;font-weight:800;cursor:pointer;box-shadow:0 8px 20px rgba(196,26,31,.3)}}.mract{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px}}.mract a{{display:flex;align-items:center;justify-content:center;height:48px;border-radius:14px;border:1.5px solid #1D1B18;color:#1D1B18!important;text-decoration:none!important;font-weight:800;font-size:14.5px;background:#fff}}.mrnote{{font-size:12.5px;color:#8a8378;line-height:1.6;margin:14px 2px 0}}</style>
<script>(function(){{var MP={js},PR={prj};var $=function(i){{return document.getElementById(i)}},cv=$("mrcv"),cx=cv.getContext("2d"),img=null,Q=[],mat="deck",col=0,prod=0;
var COL={{deck:[["방부목","#c49a63"],["월넛 오일","#7a4f2c"],["티크","#a8703d"],["회색 합성","#8a857d"]],tempa:[["화이트","#efece6"],["오크","#c8a073"],["월넛","#6e4a2e"],["블랙","#2d2b29"]],ruba:[["히노끼","#e3c99a"],["스프러스","#e9d6ad"],["화이트워시","#eee5d6"]],
 paint:[["화이트","#f3f0ea"],["웜 그레이","#bdb6aa"],["세이지","#a7b39a"],["올리브","#7d8463"],["테라코타","#c27a5a"],["네이비","#36435a"]],siding:[["화이트","#eceae5"],["라이트 그레이","#b9b9b4"],["차콜","#4b4a48"],["우드","#b1825a"]],tile:[["화이트","#f1efeb"],["라이트 그레이","#c9c6c0"],["다크 그레이","#6f6c68"],["베이지","#d8c8ad"]]}};
Object.keys(PR).forEach(function(k){{if(COL[k])COL[k]=PR[k].concat(COL[k])}});
function hx(c,a){{var n=parseInt(c.slice(1),16),r=n>>16,g=n>>8&255,b=n&255;return function(d){{return "rgb("+Math.max(0,Math.min(255,r+d))+","+Math.max(0,Math.min(255,g+d))+","+Math.max(0,Math.min(255,b+d))+")"}}}}
function rnd(s){{return function(){{s=(s*16807)%2147483647;return s/2147483647}}}}
function tex(){{var Wm=+$("mw").value||3,Hm=+$("mh").value||2.4,ppm=Math.min(320,2400/Math.max(Wm,Hm)),W=Math.max(64,Math.round(Wm*ppm)),H=Math.max(64,Math.round(Hm*ppm)),t=document.createElement("canvas");t.width=W;t.height=H;var g=t.getContext("2d"),c=hx(COL[mat][col][1]),R=rnd(7),mm=ppm/1000;
 g.fillStyle=c(0);g.fillRect(0,0,W,H);
 function grain(x,y,w,h,horiz,k){{for(var i=0;i<k;i++){{g.strokeStyle=c((R()-0.5)*40);g.globalAlpha=0.25+R()*0.25;g.lineWidth=0.6+R()*1.2;g.beginPath();if(horiz){{var yy=y+R()*h;g.moveTo(x,yy);g.bezierCurveTo(x+w*.3,yy+(R()-.5)*h*.3,x+w*.7,yy+(R()-.5)*h*.3,x+w,yy+(R()-.5)*2)}}else{{var xx=x+R()*w;g.moveTo(xx,y);g.bezierCurveTo(xx+(R()-.5)*w*.3,y+h*.3,xx+(R()-.5)*w*.3,y+h*.7,xx,y+h)}}g.stroke()}}g.globalAlpha=1}}
 if(mat=="deck"||mat=="siding"){{var bh=(mat=="deck"?140:200)*mm,gap=(mat=="deck"?5:0)*mm,y=0,row=0;while(y<H){{var off=R()*3600*mm;g.fillStyle=c((R()-.5)*26);g.fillRect(0,y,W,bh);if(mat=="deck")grain(0,y,W,bh,1,6);else{{g.fillStyle="rgba(0,0,0,.28)";g.fillRect(0,y+bh-3*mm-2,W,3*mm+2);g.fillStyle="rgba(255,255,255,.18)";g.fillRect(0,y,W,2)}}
  if(mat=="deck"){{for(var x=-off;x<W;x+=3600*mm){{g.fillStyle="rgba(0,0,0,.35)";g.fillRect(x,y,Math.max(1.5,3*mm),bh)}}g.fillStyle="rgba(0,0,0,.55)";g.fillRect(0,y+bh,W,Math.max(2,gap))}}y+=bh+gap;row++}}}}
 else if(mat=="tempa"){{var sw=30*mm;for(var x=0;x<W;x+=sw){{var gr=g.createLinearGradient(x,0,x+sw,0);gr.addColorStop(0,c(-35));gr.addColorStop(.25,c(10));gr.addColorStop(.6,c(18));gr.addColorStop(1,c(-30));g.fillStyle=gr;g.fillRect(x,0,sw,H)}}}}
 else if(mat=="ruba"){{var pw=90*mm;for(var x=0;x<W;x+=pw){{g.fillStyle=c((R()-.5)*22);g.fillRect(x,0,pw,H);grain(x,0,pw,H,0,5);g.fillStyle="rgba(0,0,0,.3)";g.fillRect(x,0,Math.max(1.5,2*mm),H)}}}}
 else if(mat=="tile"){{var ts=600*mm,jt=Math.max(1.5,3*mm);for(var y=0;y<H;y+=ts)for(var x=0;x<W;x+=ts){{g.fillStyle=c((R()-.5)*12);g.fillRect(x,y,ts,ts)}}g.fillStyle="rgba(120,115,108,.9)";for(var y=0;y<H;y+=ts)g.fillRect(0,y,W,jt);for(var x=0;x<W;x+=ts)g.fillRect(x,0,jt,H)}}
 else{{for(var i=0;i<W*H/900;i++){{g.fillStyle=c((R()-.5)*10);g.globalAlpha=.25;g.fillRect(R()*W,R()*H,2,2)}}g.globalAlpha=1}}
 return t}}
function homog(p){{var x0=p[0][0],y0=p[0][1],x1=p[1][0],y1=p[1][1],x2=p[2][0],y2=p[2][1],x3=p[3][0],y3=p[3][1],dx1=x1-x2,dx2=x3-x2,dy1=y1-y2,dy2=y3-y2,sx=x0-x1+x2-x3,sy=y0-y1+y2-y3,g=0,h=0;
 if(sx||sy){{var den=dx1*dy2-dx2*dy1;g=(sx*dy2-dx2*sy)/den;h=(dx1*sy-sx*dy1)/den}}var a=x1-x0+g*x1,b=x3-x0+h*x3,c=x0,d=y1-y0+g*y1,e=y3-y0+h*y3,f=y0;
 return function(u,v){{var w=g*u+h*v+1;return [(a*u+b*v+c)/w,(d*u+e*v+f)/w]}}}}
function tri(g,im,s0,s1,s2,d0,d1,d2){{var x0=s0[0],y0=s0[1],x1=s1[0],y1=s1[1],x2=s2[0],y2=s2[1],den=x0*(y1-y2)+x1*(y2-y0)+x2*(y0-y1);if(!den)return;
 var a=(d0[0]*(y1-y2)+d1[0]*(y2-y0)+d2[0]*(y0-y1))/den,b=(d0[0]*(x2-x1)+d1[0]*(x0-x2)+d2[0]*(x1-x0))/den,c=(d0[0]*(x1*y2-x2*y1)+d1[0]*(x2*y0-x0*y2)+d2[0]*(x0*y1-x1*y0))/den,
 d=(d0[1]*(y1-y2)+d1[1]*(y2-y0)+d2[1]*(y0-y1))/den,e=(d0[1]*(x2-x1)+d1[1]*(x0-x2)+d2[1]*(x1-x0))/den,f=(d0[1]*(x1*y2-x2*y1)+d1[1]*(x2*y0-x0*y2)+d2[1]*(x0*y1-x1*y0))/den;
 var mx=(d0[0]+d1[0]+d2[0])/3,my=(d0[1]+d1[1]+d2[1])/3,ex=function(p){{var dx=p[0]-mx,dy=p[1]-my,l=Math.hypot(dx,dy)||1;return [p[0]+dx/l*1.2,p[1]+dy/l*1.2]}},e0=ex(d0),e1=ex(d1),e2=ex(d2);
 g.save();g.beginPath();g.moveTo(e0[0],e0[1]);g.lineTo(e1[0],e1[1]);g.lineTo(e2[0],e2[1]);g.closePath();g.clip();g.setTransform(a,d,b,e,c,f);g.drawImage(im,0,0);g.restore()}}
function draw(){{if(!img)return;cx.setTransform(1,0,0,1,0,0);cx.drawImage(img,0,0,cv.width,cv.height);var T=tex(),H=homog(Q),N=14,W=T.width,Ht=T.height,P=[];
 for(var j=0;j<=N;j++){{P[j]=[];for(var i=0;i<=N;i++)P[j][i]=H(i/N,j/N)}}
 for(var j=0;j<N;j++)for(var i=0;i<N;i++){{var s00=[i/N*W,j/N*Ht],s10=[(i+1)/N*W,j/N*Ht],s01=[i/N*W,(j+1)/N*Ht],s11=[(i+1)/N*W,(j+1)/N*Ht];tri(cx,T,s00,s10,s11,P[j][i],P[j][i+1],P[j+1][i+1]);tri(cx,T,s00,s11,s01,P[j][i],P[j+1][i+1],P[j+1][i])}}
 var sh=+$("msh").value;if(sh>0){{cx.save();cx.beginPath();Q.forEach(function(p,k){{k?cx.lineTo(p[0],p[1]):cx.moveTo(p[0],p[1])}});cx.closePath();cx.clip();cx.globalCompositeOperation="multiply";cx.globalAlpha=sh;cx.filter="grayscale(1) contrast(1.4) brightness(1.25)";cx.drawImage(img,0,0,cv.width,cv.height);cx.restore();cx.filter="none";cx.globalCompositeOperation="source-over";cx.globalAlpha=1}}
 place();cost()}}
function place(){{var r=cv.getBoundingClientRect(),s=r.width/cv.width;$("mrh").innerHTML="";Q.forEach(function(p,k){{var e=document.createElement("i");e.style.left=p[0]*s+"px";e.style.top=p[1]*s+"px";e.dataset.k=k;$("mrh").appendChild(e)}})}}
var drag=-1;$("mrv").addEventListener("pointerdown",function(e){{if(e.target.tagName!="I")return;drag=+e.target.dataset.k;e.target.setPointerCapture(e.pointerId);e.preventDefault()}});
$("mrv").addEventListener("pointermove",function(e){{if(drag<0)return;var r=cv.getBoundingClientRect(),s=cv.width/r.width;Q[drag]=[Math.max(0,Math.min(cv.width,(e.clientX-r.left)*s)),Math.max(0,Math.min(cv.height,(e.clientY-r.top)*s))];var el=$("mrh").children[drag];el.style.left=(e.clientX-r.left)+"px";el.style.top=(e.clientY-r.top)+"px";
 if(!draw.p){{draw.p=1;requestAnimationFrame(function(){{draw.p=0;draw()}})}}$("mrtip").hidden=true}});
window.addEventListener("pointerup",function(){{drag=-1}});
function load(src){{var im=new Image();im.onload=function(){{var s=Math.min(1,1200/Math.max(im.width,im.height));cv.width=Math.round(im.width*s);cv.height=Math.round(im.height*s);img=im;var w=cv.width,h=cv.height;
 Q=mat=="deck"||mat=="tile"?[[w*.3,h*.55],[w*.7,h*.55],[w*.92,h*.92],[w*.08,h*.92]]:[[w*.2,h*.15],[w*.8,h*.15],[w*.8,h*.85],[w*.2,h*.85]];draw()}};im.src=src}}
function file(f){{if(f)load(URL.createObjectURL(f))}}$("mrc").onchange=function(){{file(this.files[0])}};$("mra").onchange=function(){{file(this.files[0])}};
$("mrd").onclick=function(){{var c=document.createElement("canvas");c.width=1200;c.height=900;var g=c.getContext("2d"),gr=g.createLinearGradient(0,0,0,900);gr.addColorStop(0,"#cfe0ee");gr.addColorStop(.5,"#e9eef0");gr.addColorStop(.5,"#9aa58b");gr.addColorStop(1,"#6f7c5f");g.fillStyle=gr;g.fillRect(0,0,1200,900);g.fillStyle="#d9d2c4";g.fillRect(150,120,900,330);g.fillStyle="#8a7f72";g.fillRect(150,430,900,25);g.fillStyle="#5b6f7f";g.fillRect(260,200,180,170);g.fillRect(760,200,180,170);g.fillStyle="#6b5644";g.fillRect(520,230,150,220);load(c.toDataURL())}};
function chips(){{$("mrcol").innerHTML=COL[mat].map(function(c,i){{return '<button type="button" data-i="'+i+'"'+(i==col?' class="on"':'')+'>'+(c[2]?'<img src="'+c[2]+'" alt="" loading="lazy" referrerpolicy="no-referrer">':'<i style="background:'+c[1]+'"></i>')+'<span>'+c[0].replace(/</g,"")+'</span></button>'}}).join("")}}
$("mrcol").onclick=function(e){{var b=e.target.closest("button");if(!b)return;col=+b.dataset.i;chips();draw()}};
$("mrt").onclick=function(e){{var b=e.target.closest("button");if(!b)return;mat=b.dataset.m;col=0;prod=0;[].forEach.call(this.children,function(x){{x.classList.toggle("on",x==b)}});chips();
 $("mrcalc").href={{deck:"/deck-gyesan.html",tempa:"/gyeonjeok.html",ruba:"/gyeonjeok.html",paint:"/dobae-jangpan.html",siding:"/gyeonjeok.html",tile:"/dobae-jangpan.html"}}[mat];if(img&&!draw.moved){{}}draw();if(!img)cost()}};
function won(x){{return Math.round(x).toLocaleString("ko-KR")+"원"}}
function cost(){{var Wm=+$("mw").value||0,Hm=+$("mh").value||0,A=Wm*Hm,o="",L=MP[mat];
 if(L&&L.length){{var t=L[Math.min(prod,L.length-1)],q=Math.ceil(A*(1+(t.l||0))/t.a);o="<b>"+won(q*t.p)+"</b><p>"+A.toFixed(1)+"㎡ · "+t.n+" "+q+t.u.replace(/^1/,"")+" (로스 포함)"+(mat=="deck"?" · 장선·기둥은 '자세히 계산'":"")+"</p><select id='mrp'>"+L.map(function(x,i){{return "<option value='"+i+"'"+(i==prod?" selected":"")+">"+x.n+" — "+won(x.p)+"/"+x.u+"</option>"}}).join("")+"</select>"}}
 else if(mat=="paint"){{o="<b>"+(A*2/10).toFixed(1)+"L</b><p>"+A.toFixed(1)+"㎡ 2회 칠 기준(도포 10㎡/L 가정) · 정확한 양은 '자세히 계산'</p>"}}
 else if(mat=="tile"){{o="<b>"+Math.ceil(A*1.1/0.36)+"장</b><p>600×600 타일 기준 · "+A.toFixed(1)+"㎡ · 로스 10%</p>"}}
 var cc=COL[mat][col];if(cc&&cc[2])o='<div class="mrsel"><img src="'+cc[2]+'" alt="" referrerpolicy="no-referrer"><span><small>고른 제품</small>'+cc[0].replace(/</g,"")+'<a href="'+cc[3]+'" target="_blank" rel="noopener">제품 보기 ›</a></span></div>'+o;$("mro").innerHTML=o;var s=$("mrp");if(s)s.onchange=function(){{prod=+this.value;cost()}}}}
$("mw").oninput=$("mh").oninput=function(){{draw();if(!img)cost()}};$("msh").onchange=draw;window.addEventListener("resize",place);
$("mrsv").onclick=function(){{if(!img){{alert("먼저 사진을 찍거나 골라 주세요");return}}cv.toBlob(function(b){{var f=new File([b],"영진목재-공사미리보기.jpg",{{type:"image/jpeg"}});if(navigator.canShare&&navigator.canShare({{files:[f]}}))navigator.share({{files:[f],title:"공사 미리보기",text:"영진목재 공사 미리보기 · www.wwood.co.kr/mirigi.html"}}).catch(function(){{}});else{{var a=document.createElement("a");a.href=URL.createObjectURL(b);a.download=f.name;a.click()}}}},"image/jpeg",.9)}};
chips();cost();(function(){{var m0=mat,c0=col,w0=$("mw").value,h0=$("mh").value;$("mw").value=1.2;$("mh").value=.6;[].forEach.call($("mrt").children,function(b){{mat=b.dataset.m;col=0;b.querySelector("b").style.backgroundImage="url("+tex().toDataURL()+")"}});mat=m0;col=c0;$("mw").value=w0;$("mh").value=h0}})();$("mrd").click()}})();</script>'''
    page("mirigi.html", "공사 미리보기 — 사진에 데크·템바보드·루바·벽 색·사이딩 입혀 보기 + 예상 자재비 | 영진목재",
         "공사할 곳 사진을 찍고 네 모서리만 맞추면 데크·템바보드·루바·벽 색·사이딩·타일이 실제처럼 입혀지고, 크기를 넣으면 필요한 자재와 예상 자재비가 나옵니다. 사진은 폰 안에서만 처리.",
         body, "/calc.html")
