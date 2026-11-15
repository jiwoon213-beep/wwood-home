# -*- coding: utf-8 -*-
"""셀프 인테리어 자재비 계산기(/gyeonjeok.html) — 방 크기만 넣으면 공정별 필요 수량·자재비(소매 기준가)를 계산.
품목·판매단위·1단위 면적·로스는 gagyeok.py GG(판매 단위 확인된 것만)를 그대로 씀. 시공비·부자재는 넣지 않음(확인 안 된 숫자 금지)."""
import json, re
import gagyeok as G

# (키, 공정 이름, 가격가이드 slug들, 적용 면: ceil·wall·floor·art·doors·film, 한 줄 설명)
WORK = [
    ("ceil_gyp", "천장 석고보드", ["seokgo-gagyeok"], "ceil", "천장 면적 기준 · 1겹"),
    ("wall_gyp", "벽 석고보드(가벽·덧방)", ["seokgo-gagyeok"], "wall", "벽 면적(문·창 뺌) 기준 · 1겹"),
    ("wall_ins", "벽 단열(아이소핑크·이보드)", ["danyeol-gagyeok"], "wall", "벽 면적 기준 · 결로·외풍 막기"),
    ("ceil_ruba", "천장 루바(히노끼·스프러스)", ["hinoki-ruba", "spruce-ruba"], "ceil", "천장 면적 기준"),
    ("art", "아트월 템바보드", ["tempa-board", "tempa-ruba"], "art", "아트월 면적 기준(기본: 벽 1면)"),
    ("floor_ply", "바닥 합판 덧방", ["hapan-gagyeok", "osb-gagyeok"], "floor", "바닥 면적 기준 · 마루·장판 밑 평탄 작업"),
    ("deck", "데크 바닥(방부·합성)", ["deck-gagyeok"], "floor", "바닥 면적 기준 · 장선·기초 별도"),
    ("siding", "외벽 사이딩", ["siding-gagyeok"], "wall", "벽 면적 기준 · 코너·J찬넬 별도"),
    ("door", "방문 교체(문짝·문틀)", ["door-gagyeok"], "doors", "문 개수 기준"),
    ("film", "방문 필름 리폼", ["interior-film"], "film", "문 1짝 양면 약 5m 기준"),
]


def data(P):
    by = {g[0]: g for g in G.GG}
    out = []
    for k, nm, slugs, face, note in WORK:
        items = []
        for sl in slugs:
            g = by.get(sl)
            if not g: continue
            loss = g[7]
            for rx, unit, area in g[4]:
                hit = next((p for p in P if re.search(rx, p["name"])), None)
                if not hit: continue
                ok = isinstance(area, float) or (face == "doors" and area == "plain") or (face == "film" and unit == "1m")
                if not ok: continue
                n = re.sub(r"^[^-]+-\s*", "", hit["name"]).replace("*", "×").replace("@", " · ").strip(" ·")
                n = re.sub(r"\s+", " ", n)
                if face == "doors": n = ("문틀 " if hit["cat"] == "문틀" else "문짝 ") + n
                items.append({"n": n, "u": unit, "a": area if isinstance(area, float) else 0, "p": hit["price"], "l": loss, "g": sl})
        if face == "doors":  # 문짝·문틀 각각 한 개씩 고르게
            items = [i for i in items if i["n"].startswith("문짝")][:14] + [i for i in items if i["n"].startswith("문틀")][:10]
        if items: out.append({"k": k, "nm": nm, "f": face, "note": note, "it": items if face == "doors" else items[:16]})
    return out


def gen(page, P, E, CTA, faqslide, TEL):
    D = data(P)
    if not D: return
    js = json.dumps(D, ensure_ascii=False, separators=(",", ":"))
    fq = faqslide([
        ("이 계산기 금액에 시공비도 들어가나요?", "아니요. 홈페이지 소매 기준가(부가세 별도)로 계산한 자재비만입니다. 피스·본드·몰딩 같은 부자재와 시공비는 현장마다 달라 매장에서 견적을 드립니다."),
        ("평수만 알면 되나요?", "방 가로·세로·천장 높이를 넣으면 바닥·천장·벽 면적을 자동으로 계산합니다. 평수만 알면 '평수로 넣기'를 쓰세요(정사각형 방으로 가정)."),
        ("계산 결과를 매장에 가져가도 되나요?", "네. '결과 복사'를 눌러 문자·카톡으로 보내거나 화면을 보여 주시면 그대로 자재를 준비하고 원하는 크기로 재단해 드립니다."),
        ("왜 실제 필요량이 다를 수 있나요?", "자르는 방향, 창·문 위치, 모서리 처리에 따라 로스가 달라집니다. 계산기는 품목별로 5~10% 로스를 더해 넉넉하게 잡습니다.")])
    body = f'''<section class="wrap sec gg gjw"><p class="crumb"><a href="/calc.html">자재 계산기</a> › 셀프 인테리어 자재비</p>
<h1>셀프 인테리어 자재비 계산기</h1>
<p class="glead">방 크기만 넣고 할 공정을 고르면 <b>필요한 장 수와 자재비</b>가 바로 나옵니다. 석고보드·단열재·루바·템바보드·합판·데크·사이딩·방문·필름까지, 홈페이지 기준가(부가세 별도)로 계산합니다.</p>
<div class="gjc"><div class="gjin">
<div class="gjm"><button type="button" class="on" data-m="dim">가로·세로로 넣기</button><button type="button" data-m="py">평수로 넣기</button></div>
<div class="gjr" id="gjdim"><label>가로<input id="gw" type="number" inputmode="decimal" step="0.1" value="3.6"><i>m</i></label><label>세로<input id="gd" type="number" inputmode="decimal" step="0.1" value="3.0"><i>m</i></label></div>
<div class="gjr" id="gjpy" hidden><label>평수<input id="gp" type="number" inputmode="decimal" step="0.5" value="3.3"><i>평</i></label></div>
<div class="gjr"><label>천장 높이<input id="gh" type="number" inputmode="decimal" step="0.1" value="2.4"><i>m</i></label><label>문<input id="gdr" type="number" inputmode="numeric" value="1"><i>개</i></label><label>창<input id="gwn" type="number" inputmode="numeric" value="1"><i>개</i></label></div>
<p class="gjarea" id="garea"></p></div>
<h2 class="gt">할 공정 고르기</h2><div id="gjw" class="gjws"></div>
<div class="gjres"><h2 class="gt">예상 자재비</h2><div id="gjout"></div>
<div class="gjtot"><span>합계(자재비)</span><b id="gjsum">0원</b></div>
<p class="small muted">홈페이지 소매 기준가(부가세 별도) · 로스 포함 · 시공비·피스·본드·몰딩 등 부자재 별도. 실제 금액은 수량·재고에 따라 매장에서 안내합니다.</p>
<div class="gjact"><button type="button" class="b r" id="gjcopy">결과 복사</button><a class="b" href="tel:{TEL}">전화로 견적 받기</a><a class="b" href="/cut.html">재단 미리보기</a></div></div></div></section>
<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{fq}<p class="small">품목별 1장·1평 가격은 <a href="/gagyeok/">자재 가격 가이드</a>, 장 수만 빠르게 계산하려면 <a href="/calc.html">자재 계산기</a>를 보세요.</p></section>{CTA}
<style>.gjc{{background:#fff;border:1px solid #e9e3d9;border-radius:20px;padding:18px;box-shadow:0 6px 20px rgba(0,0,0,.05)}}.gjm{{display:flex;gap:6px;margin-bottom:12px}}.gjm button{{flex:1;height:42px;border-radius:12px;border:1.5px solid #1D1B18;background:#fff;font:inherit;font-weight:700;cursor:pointer}}.gjm button.on{{background:#1D1B18;color:#fff}}
.gjr{{display:flex;gap:8px;margin-bottom:8px}}.gjr[hidden]{{display:none}}.gjr label{{flex:1;display:flex;flex-direction:column;font-size:13px;font-weight:700;color:#6b645a;position:relative}}.gjr input{{height:46px;border:1.5px solid #ddd5c8;border-radius:12px;padding:0 30px 0 12px;font:inherit;font-size:18px;font-weight:800;color:#1D1B18;margin-top:4px;width:100%;box-sizing:border-box}}.gjr i{{position:absolute;right:11px;bottom:13px;font-style:normal;color:#8a8378;font-size:14px}}
.gjarea{{background:#f6f2ec;border-radius:12px;padding:10px 12px;font-size:14px;margin:6px 0 0}}.gjws{{display:grid;gap:8px}}.gjwi{{border:1.5px solid #e6dfd5;border-radius:14px;padding:12px;background:#fff}}.gjwi.on{{border-color:#1D1B18;background:#fbf9f6}}.gjwi>label{{display:flex;align-items:center;gap:10px;font-weight:800;cursor:pointer}}.gjwi input[type=checkbox]{{width:22px;height:22px;accent-color:#1D1B18}}.gjwi small{{display:block;font-weight:500;color:#8a8378;font-size:12.5px}}
.gjwi select{{width:100%;margin-top:10px;height:42px;border-radius:10px;border:1.5px solid #ddd5c8;font:inherit;font-size:14px;padding:0 8px;background:#fff}}.gjwi .gjx{{display:flex;gap:8px;margin-top:8px}}.gjwi .gjx label{{flex:1;font-size:12.5px;color:#6b645a;font-weight:700}}.gjwi .gjx input{{width:100%;height:38px;border:1.5px solid #ddd5c8;border-radius:10px;padding:0 8px;font:inherit;font-weight:700;box-sizing:border-box}}.gjwi:not(.on) select,.gjwi:not(.on) .gjx{{display:none}}
.gjres{{margin-top:16px}}#gjout .gjl{{display:flex;justify-content:space-between;gap:10px;padding:10px 0;border-bottom:1px dashed #e6dfd5;font-size:14px}}#gjout .gjl b{{display:block}}#gjout .gjl small{{color:#8a8378}}#gjout .gjl em{{font-style:normal;font-weight:800;white-space:nowrap}}#gjout .gje{{color:#8a8378;font-size:14px;padding:8px 0}}
.gjtot{{display:flex;justify-content:space-between;align-items:center;background:#1D1B18;color:#fff;border-radius:14px;padding:14px 16px;margin:12px 0 8px}}.gjtot b{{font-size:24px;color:#f5d27a}}.gjact{{display:flex;gap:8px;flex-wrap:wrap}}.gjact .b{{flex:1;min-width:120px;text-align:center}}</style>
<script>(function(){{var D={js};var M="dim",$=function(i){{return document.getElementById(i)}};
function won(x){{return Math.round(x).toLocaleString("ko-KR")+"원"}}
var W=$("gjw");D.forEach(function(w,ix){{var d=document.createElement("div");d.className="gjwi"+(ix<3?" on":"");d.dataset.k=w.k;
 var opt=w.it.map(function(t,j){{return '<option value="'+j+'">'+t.n.replace(/</g,"")+' — '+won(t.p)+'/'+t.u+'</option>'}}).join("");
 var extra=w.f=="art"?'<div class="gjx"><label>아트월 가로(m)<input class="gax" type="number" step="0.1" inputmode="decimal"></label><label>높이(m)<input class="gay" type="number" step="0.1" inputmode="decimal"></label></div>':w.f=="doors"?'<select class="gs2">'+w.it.map(function(t,j){{return t.n.indexOf("문틀")==0?'<option value="'+j+'">'+t.n+' — '+won(t.p)+'</option>':""}}).join("")+'<option value="-1">문틀은 그대로(문짝만)</option></select>':"";
 if(w.f=="doors")opt=w.it.map(function(t,j){{return t.n.indexOf("문짝")==0?'<option value="'+j+'">'+t.n+' — '+won(t.p)+'</option>':""}}).join("");
 d.innerHTML='<label><input type="checkbox"'+(ix<3?" checked":"")+'><span>'+w.nm+'<small>'+w.note+'</small></span></label><select class="gs1">'+opt+'</select>'+extra;W.appendChild(d)}});
function area(){{var h=+$("gh").value||2.4,w,d;if(M=="py"){{var a=(+$("gp").value||0)*3.3058;w=d=Math.sqrt(a)}}else{{w=+$("gw").value||0;d=+$("gd").value||0}}
 var fl=w*d,wall=Math.max(0,2*(w+d)*h-(+$("gdr").value||0)*1.9-(+$("gwn").value||0)*1.5);return {{w:w,d:d,h:h,fl:fl,ce:fl,wa:wall,dr:+$("gdr").value||0}}}}
var last="";function calc(){{var A=area();$("garea").innerHTML="바닥 <b>"+A.fl.toFixed(1)+"㎡</b>("+(A.fl/3.3058).toFixed(1)+"평) · 천장 <b>"+A.ce.toFixed(1)+"㎡</b> · 벽 <b>"+A.wa.toFixed(1)+"㎡</b>(문·창 뺌)";
 var html="",sum=0,txt=["[영진목재 자재비 계산] 바닥 "+A.fl.toFixed(1)+"㎡ / 벽 "+A.wa.toFixed(1)+"㎡"];
 [].forEach.call(W.children,function(d,ix){{var w=D[ix],on=d.querySelector("input[type=checkbox]").checked;d.classList.toggle("on",on);if(!on)return;
  var t=w.it[+d.querySelector(".gs1").value],q=0,base="",cost=0,line2="";
  if(w.f=="doors"){{var n=A.dr||1,t2i=+d.querySelector(".gs2").value,t2=t2i>=0?w.it[t2i]:null;q=n;cost=t.p*n+(t2?t2.p*n:0);base="문 "+n+"개";line2=t.n+" "+n+"개"+(t2?" + "+t2.n+" "+n+"개":"")}}
  else if(w.f=="film"){{q=Math.ceil((A.dr||1)*5);cost=t.p*q;base="문 "+(A.dr||1)+"짝 양면";line2=t.n+" "+q+"m"}}
  else{{var s=w.f=="ceil"?A.ce:w.f=="floor"?A.fl:w.f=="wall"?A.wa:0;if(w.f=="art"){{var ax=+d.querySelector(".gax").value||A.w,ay=+d.querySelector(".gay").value||A.h;s=ax*ay;base="아트월 "+s.toFixed(1)+"㎡"}}else base=s.toFixed(1)+"㎡";
   q=Math.ceil(s*(1+(t.l||0))/t.a);cost=q*t.p;line2=t.n+" "+q+t.u.replace(/^1/,"")}}
  sum+=cost;html+='<div class="gjl"><span><b>'+w.nm+'</b><small>'+line2+' · '+base+'</small></span><em>'+won(cost)+'</em></div>';txt.push("- "+w.nm+": "+line2+" ("+won(cost)+")")}});
 $("gjout").innerHTML=html||'<p class="gje">위에서 할 공정을 골라 주세요.</p>';$("gjsum").textContent=won(sum);txt.push("합계(자재비, 기준가·부가세 별도): "+won(sum));txt.push("https://www.wwood.co.kr/gyeonjeok.html");last=txt.join("\\n")}}
document.querySelector(".gjm").addEventListener("click",function(e){{var b=e.target.closest("button");if(!b)return;M=b.dataset.m;[].forEach.call(this.children,function(x){{x.classList.toggle("on",x==b)}});$("gjdim").hidden=M!="dim";$("gjpy").hidden=M!="py";calc()}});
document.querySelector(".gjw").addEventListener("input",calc);document.querySelector(".gjw").addEventListener("change",calc);
$("gjcopy").onclick=function(){{try{{navigator.clipboard.writeText(last);this.textContent="복사됐어요"}}catch(e){{prompt("아래 내용을 복사하세요",last)}}}};calc()}})();</script>'''
    page("gyeonjeok.html", "셀프 인테리어 자재비 계산기 — 방 크기만 넣으면 석고보드·단열재·템바보드·데크 장 수와 비용 | 영진목재",
         "방 가로·세로·높이만 넣으면 석고보드·단열재·루바·템바보드·합판·데크·사이딩·방문·필름 필요 수량과 자재비를 기준가로 바로 계산합니다. 결과 복사해 매장에 보여 주세요.",
         body, "/calc.html")
