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
                items.append({"n": n, "u": unit, "a": area if isinstance(area, float) else 0, "p": hit["price"], "l": loss, "g": sl, "r": hit["name"]})
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
        ("계산 결과를 매장에 가져가도 되나요?", "네. '결과 보내기'를 눌러 문자·카톡으로 보내거나 화면을 보여 주시면 그대로 자재를 준비하고 원하는 크기로 재단해 드립니다."),
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
<div class="gjact"><button type="button" class="b r" id="gjcopy">결과 보내기</button><button type="button" class="b" id="gjcopyhj">현장함에 저장</button><a class="b" href="tel:{TEL}">전화로 견적 받기</a><a class="b" href="/cut.html">재단 미리보기</a></div></div></div></section>
<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{fq}<p class="small">품목별 1장·1평 가격은 <a href="/gagyeok/">자재 가격 가이드</a>, 장 수만 빠르게 계산하려면 <a href="/calc.html">자재 계산기</a>, 벽지·장판·타일·페인트는 <a href="/dobae-jangpan.html">도배·장판 계산기</a>를 보세요.</p></section>{CTA}
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
$("gjcopyhj").onclick=function(){{WWHJ("calc",last,this)}};$("gjcopy").onclick=function(){{try{{if(navigator.share){{navigator.share({{title:document.title,text:last,url:location.href.split("#")[0]}}).catch(function(){{}});return}}navigator.clipboard.writeText(last);this.textContent="복사됐어요"}}catch(e){{prompt("아래 내용을 복사하세요",last)}}}};calc()}})();</script>'''
    page("gyeonjeok.html", "셀프 인테리어 자재비 계산기 — 방 크기만 넣으면 석고보드·단열재·템바보드·데크 장 수와 비용 | 영진목재",
         "방 가로·세로·높이만 넣으면 석고보드·단열재·루바·템바보드·합판·데크·사이딩·방문·필름 필요 수량과 자재비를 기준가로 바로 계산합니다. 결과 복사해 매장에 보여 주세요.",
         body, "/calc.html")


def gen2(page, E, CTA, faqslide, TEL):
    """도배·장판·타일·페인트 필요량 계산기(/dobae-jangpan.html) — 수량만(가격 없음). 규격은 일반 시판 규격을 고를 수 있게, 바꿀 수 있게."""
    fq = faqslide([
        ("벽지 몇 롤 필요한지 어떻게 계산하나요?", "방 둘레를 벽지 폭으로 나눠 필요한 '폭(줄)' 수를 구하고, 한 롤에서 천장 높이+여유만큼 몇 줄이 나오는지로 나눕니다. 무늬를 맞춰야 하는 벽지는 무늬 반복 길이만큼 더 듭니다."),
        ("실크벽지와 합지벽지 규격이 다른가요?", "실크는 보통 폭 106cm·길이 15.6m(광폭), 합지는 소폭 53cm·12.5m나 광폭 93cm·17.75m가 많습니다. 제품마다 다를 수 있어 포장 표기를 넣어 계산하세요."),
        ("장판은 몇 m 사야 하나요?", "장판은 폭(보통 1.83m 또는 2m)으로 나오고 길이(m)로 잘라 팝니다. 방의 짧은 쪽을 폭으로 덮을 줄 수를 구하고, 긴 쪽 길이+여유 10cm를 곱합니다."),
        ("페인트 1L로 얼마나 칠하나요?", "제품마다 달라 통에 적힌 '이론 도포 면적(㎡/L)'을 넣으세요. 보통 2회 칠을 기준으로 계산하고, 거친 벽은 더 먹습니다.")])
    body = f'''<section class="wrap sec gg dbw"><p class="crumb"><a href="/calc.html">자재 계산기</a> › 도배·장판·타일·페인트</p>
<h1>도배·장판·타일·페인트 계산기</h1>
<p class="glead">방 크기만 넣으면 <b>벽지 몇 롤, 장판 몇 m, 타일 몇 장, 페인트 몇 L</b>인지 바로 계산합니다. 규격은 포장에 적힌 값으로 바꿔 넣을 수 있어요.</p>
<div class="gjc"><div class="gjr"><label>가로<input id="dw" type="number" inputmode="decimal" step="0.1" value="3.6"><i>m</i></label><label>세로<input id="dd" type="number" inputmode="decimal" step="0.1" value="3.0"><i>m</i></label><label>높이<input id="dh" type="number" inputmode="decimal" step="0.1" value="2.3"><i>m</i></label></div>
<div class="gjr"><label>문<input id="ddr" type="number" inputmode="numeric" value="1"><i>개</i></label><label>창<input id="dwn" type="number" inputmode="numeric" value="1"><i>개</i></label></div>
<p class="gjarea" id="dar"></p></div>
<div class="dbt" id="dbt"><button type="button" class="on" data-t="paper">벽지</button><button type="button" data-t="floor">장판</button><button type="button" data-t="tile">타일</button><button type="button" data-t="paint">페인트</button></div>
<div class="gjc dbp" data-p="paper"><div class="gjr"><label>벽지 종류<select id="pk"><option value="1.06,15.6">실크 광폭 106cm×15.6m</option><option value="0.93,17.75">합지 광폭 93cm×17.75m</option><option value="0.53,12.5">합지 소폭 53cm×12.5m</option></select></label></div>
<div class="gjr"><label>무늬 반복<input id="prp" type="number" inputmode="numeric" value="0"><i>cm</i></label><label>천장도 도배<select id="pce"><option value="1">예</option><option value="0">아니요</option></select></label></div><div class="dbo" id="pout"></div></div>
<div class="gjc dbp" data-p="floor" hidden><div class="gjr"><label>장판 폭<select id="fw"><option value="1.83">1.83m</option><option value="2">2.0m</option></select></label><label>여유<input id="fx" type="number" inputmode="numeric" value="10"><i>cm</i></label></div><div class="dbo" id="fout"></div></div>
<div class="gjc dbp" data-p="tile" hidden><div class="gjr"><label>붙일 곳<select id="tf"><option value="floor">바닥</option><option value="wall">벽 전체</option><option value="cus">직접 입력</option></select></label><label>면적<input id="ta" type="number" inputmode="decimal" step="0.1"><i>㎡</i></label></div>
<div class="gjr"><label>타일 크기<select id="ts"><option value="300,300">300×300</option><option value="300,600" selected>300×600</option><option value="600,600">600×600</option><option value="600,1200">600×1200</option><option value="200,200">200×200</option><option value="250,400">250×400</option></select></label><label>1박스 장 수<input id="tb" type="number" inputmode="numeric" placeholder="포장 표기"><i>장</i></label></div><div class="dbo" id="tout"></div></div>
<div class="gjc dbp" data-p="paint" hidden><div class="gjr"><label>칠할 곳<select id="pf"><option value="wall">벽</option><option value="wc">벽+천장</option><option value="ceil">천장</option></select></label><label>횟수<input id="pc" type="number" inputmode="numeric" value="2"><i>회</i></label><label>도포 면적<input id="pr" type="number" inputmode="decimal" value="10"><i>㎡/L</i></label></div><div class="dbo" id="aout"></div></div>
<p class="small muted">로스 포함 참고값입니다. 자르는 방향·무늬·창 위치에 따라 달라질 수 있어요. 방 전체 자재비는 <a href="/gyeonjeok.html">셀프 인테리어 자재비 계산기</a>로 보세요.</p>
<div class="gjact"><button type="button" class="b r" id="dbcopy">결과 보내기</button><button type="button" class="b" id="dbcopyhj">현장함에 저장</button><a class="b" href="tel:{TEL}">전화 문의</a><a class="b" href="/gyeonjeok.html">자재비 계산기</a></div></section>
<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{fq}</section>{CTA}
<style>.dbt{{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:14px 0}}.dbt button{{height:46px;border-radius:12px;border:1.5px solid #1D1B18;background:#fff;font:inherit;font-weight:800;cursor:pointer}}.dbt button.on{{background:#1D1B18;color:#fff}}.dbp[hidden]{{display:none}}.gjr select{{height:46px;border:1.5px solid #ddd5c8;border-radius:12px;font:inherit;font-weight:700;margin-top:4px;background:#fff;padding:0 6px;width:100%}}
.dbo{{margin-top:10px;background:#1D1B18;color:#fff;border-radius:14px;padding:14px 16px}}.dbo b{{font-size:26px;color:#f5d27a}}.dbo p{{margin:4px 0 0;font-size:13.5px;opacity:.85}}
.gjc{{background:#fff;border:1px solid #e9e3d9;border-radius:20px;padding:16px;box-shadow:0 6px 20px rgba(0,0,0,.05)}}.gjr{{display:flex;gap:8px;margin-bottom:8px}}.gjr label{{flex:1;display:flex;flex-direction:column;font-size:13px;font-weight:700;color:#6b645a;position:relative}}.gjr input{{height:46px;border:1.5px solid #ddd5c8;border-radius:12px;padding:0 34px 0 12px;font:inherit;font-size:18px;font-weight:800;color:#1D1B18;margin-top:4px;width:100%;box-sizing:border-box}}.gjr i{{position:absolute;right:11px;bottom:13px;font-style:normal;color:#8a8378;font-size:13px}}.gjarea{{background:#f6f2ec;border-radius:12px;padding:10px 12px;font-size:14px;margin:6px 0 0}}.gjact{{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}}.gjact .b{{flex:1;min-width:110px;text-align:center}}</style>
<script>(function(){{var $=function(i){{return document.getElementById(i)}},T="paper",last="";
function A(){{var w=+$("dw").value||0,d=+$("dd").value||0,h=+$("dh").value||0,op=(+$("ddr").value||0)*1.9+(+$("dwn").value||0)*1.5;return{{w:w,d:d,h:h,fl:w*d,per:2*(w+d),wa:Math.max(0,2*(w+d)*h-op)}}}}
function calc(){{var a=A(),o="",t="";$("dar").innerHTML="바닥 <b>"+a.fl.toFixed(1)+"㎡</b>("+(a.fl/3.3058).toFixed(1)+"평) · 벽 <b>"+a.wa.toFixed(1)+"㎡</b> · 둘레 "+a.per.toFixed(1)+"m";
 if(T=="paper"){{var k=$("pk").value.split(","),bw=+k[0],bl=+k[1],rp=(+$("prp").value||0)/100,strip=a.h+0.1+rp,per=Math.floor(bl/strip)||1,n=Math.ceil(a.per*0.95/bw),r=Math.ceil(n/per),c=0;if($("pce").value=="1"){{var cs=Math.ceil(Math.min(a.w,a.d)/bw),cl=Math.max(a.w,a.d)+0.1+rp,cp=Math.floor(bl/cl)||1;c=Math.ceil(cs/cp)}}
  o="<b>"+(r+c)+"롤</b><p>벽 "+r+"롤("+n+"폭, 1롤에 "+per+"폭)"+(c?" + 천장 "+c+"롤":"")+" · 문·창 자리 약간 뺌</p>";t="벽지 "+(r+c)+"롤 ("+$("pk").selectedOptions[0].text+")"}}
 else if(T=="floor"){{var fw=+$("fw").value,x=(+$("fx").value||0)/100,s1=Math.ceil(Math.min(a.w,a.d)/fw),L1=s1*(Math.max(a.w,a.d)+x),s2=Math.ceil(Math.max(a.w,a.d)/fw),L2=s2*(Math.min(a.w,a.d)+x),L=Math.min(L1,L2);
  o="<b>"+L.toFixed(1)+"m</b><p>폭 "+fw+"m 장판 "+(L1<=L2?s1:s2)+"줄 × "+((L1<=L2?Math.max(a.w,a.d):Math.min(a.w,a.d))+x).toFixed(2)+"m · 이음이 적은 방향 기준</p>";t="장판 폭 "+fw+"m × "+L.toFixed(1)+"m"}}
 else if(T=="tile"){{var f=$("tf").value,ar=f=="floor"?a.fl:f=="wall"?a.wa:(+$("ta").value||0);if(f!="cus")$("ta").value=ar.toFixed(1);var sz=$("ts").value.split(","),one=sz[0]*sz[1]/1e6,n2=Math.ceil(ar*1.1/one),bx=+$("tb").value;
  o="<b>"+n2+"장</b><p>"+ar.toFixed(1)+"㎡ ÷ "+sz.join("×")+"mm(1장 "+one.toFixed(2)+"㎡) · 로스 10% 포함"+(bx?" · <b style='font-size:18px'>"+Math.ceil(n2/bx)+"박스</b>":" · 1박스 장 수를 넣으면 박스 수도 계산")+"</p>";t="타일 "+sz.join("×")+" "+n2+"장"+(bx?" ("+Math.ceil(n2/bx)+"박스)":"")}}
 else{{var pf=$("pf").value,ar2=(pf!="ceil"?a.wa:0)+(pf!="wall"?a.fl:0),L3=ar2*(+$("pc").value||1)/(+$("pr").value||10);var c18=Math.floor(L3/18),rem=L3-c18*18,c4=Math.floor(rem/4),r2=rem-c4*4,c1=0;if(r2>2)c4++;else if(r2>0)c1=Math.ceil(r2);
  o="<b>"+L3.toFixed(1)+"L</b><p>"+ar2.toFixed(1)+"㎡ × "+$("pc").value+"회 ÷ "+$("pr").value+"㎡/L · 예: "+[c18?"18L "+c18+"통":"",c4?"4L "+c4+"통":"",c1?"1L "+c1+"통":""].filter(Boolean).join(" + ")+"</p>";t="페인트 "+L3.toFixed(1)+"L"}}
 var id={{paper:"pout",floor:"fout",tile:"tout",paint:"aout"}}[T];$(id).innerHTML=o;last="[영진목재 계산] 방 "+a.w+"×"+a.d+"m 높이 "+a.h+"m → "+t+"\\nhttps://www.wwood.co.kr/dobae-jangpan.html"}}
$("dbt").addEventListener("click",function(e){{var b=e.target.closest("button");if(!b)return;T=b.dataset.t;[].forEach.call(this.children,function(x){{x.classList.toggle("on",x==b)}});[].forEach.call(document.querySelectorAll(".dbp"),function(p){{p.hidden=p.dataset.p!=T}});calc()}});
document.querySelector(".dbw").addEventListener("input",calc);document.querySelector(".dbw").addEventListener("change",calc);
$("dbcopyhj").onclick=function(){{WWHJ("calc",last,this)}};$("dbcopy").onclick=function(){{try{{if(navigator.share){{navigator.share({{title:document.title,text:last,url:location.href.split("#")[0]}}).catch(function(){{}});return}}navigator.clipboard.writeText(last);this.textContent="복사됐어요"}}catch(e){{prompt("복사하세요",last)}}}};calc()}})();</script>'''
    page("dobae-jangpan.html", "도배·장판·타일·페인트 계산기 — 벽지 몇 롤, 장판 몇 m, 타일 몇 장 | 영진목재",
         "방 가로·세로·높이만 넣으면 실크·합지 벽지 롤 수, 장판 길이, 타일 장 수·박스 수, 페인트 L를 바로 계산합니다. 로스 포함, 결과 복사 가능.", body, "/calc.html")


def _price(P, rx):
    h = next((p for p in P if re.search(rx, p["name"])), None)
    return h["price"] if h else 0


def _page(page, slug, title, desc, h1, lead, inputs, js, fq, CTA, TEL, extra=""):
    body = f'''<section class="wrap sec gg cxw"><p class="crumb"><a href="/calc.html">자재 계산기</a> › {h1}</p><h1>{h1}</h1><p class="glead">{lead}</p>
<div class="gjc">{inputs}<p class="gjarea" id="cxa"></p></div>
<div class="gjres"><h2 class="gt">필요한 자재</h2><div id="cxo"></div><div class="gjtot"><span>합계(자재비)</span><b id="cxs">0원</b></div>
<p class="small muted">홈페이지 소매 기준가(부가세 별도) · 로스 포함 참고값 · 시공비 별도. 실물·재고는 매장에서 확인하고 원하는 길이로 잘라 드립니다.</p>{extra}
<div class="gjact"><button type="button" class="b r" id="cxc">결과 보내기</button><button type="button" class="b" id="cxchj">현장함에 저장</button><a class="b" href="tel:{TEL}">전화 문의</a><a class="b" href="/gyeonjeok.html">방 전체 자재비</a></div></div></section>
<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{fq}</section>{CTA}
<style>.gjc{{background:#fff;border:1px solid #e9e3d9;border-radius:20px;padding:16px;box-shadow:0 6px 20px rgba(0,0,0,.05)}}.gjr{{display:flex;gap:8px;margin-bottom:8px}}.gjr label{{flex:1;display:flex;flex-direction:column;font-size:13px;font-weight:700;color:#6b645a;position:relative}}.gjr input,.gjr select{{height:46px;border:1.5px solid #ddd5c8;border-radius:12px;padding:0 34px 0 12px;font:inherit;font-size:17px;font-weight:800;color:#1D1B18;margin-top:4px;width:100%;box-sizing:border-box;background:#fff}}.gjr select{{font-size:14px;padding:0 6px}}.gjr i{{position:absolute;right:11px;bottom:13px;font-style:normal;color:#8a8378;font-size:13px}}.gjarea{{background:#f6f2ec;border-radius:12px;padding:10px 12px;font-size:14px;margin:6px 0 0}}
.gjres{{margin-top:16px}}#cxo .gjl{{display:flex;justify-content:space-between;gap:10px;padding:10px 0;border-bottom:1px dashed #e6dfd5;font-size:14px}}#cxo .gjl b{{display:block}}#cxo .gjl small{{color:#8a8378}}#cxo .gjl em{{font-style:normal;font-weight:800;white-space:nowrap}}.gjtot{{display:flex;justify-content:space-between;align-items:center;background:#1D1B18;color:#fff;border-radius:14px;padding:14px 16px;margin:12px 0 8px}}.gjtot b{{font-size:24px;color:#f5d27a}}.gjact{{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}}.gjact .b{{flex:1;min-width:110px;text-align:center}}</style>
<script>(function(){{var $=function(i){{return document.getElementById(i)}},last="";function won(x){{return Math.round(x).toLocaleString("ko-KR")+"원"}}
function out(rows,area,head){{$("cxa").innerHTML=area;var s=0,h="",t=[head];rows.forEach(function(r){{s+=r[3]*r[2];h+='<div class="gjl"><span><b>'+r[0]+'</b><small>'+r[1]+' · '+r[2]+r[4]+'</small></span><em>'+(r[3]?won(r[3]*r[2]):"매장 문의")+'</em></div>';t.push("- "+r[0]+" "+r[1]+" "+r[2]+r[4]+(r[3]?" ("+won(r[3]*r[2])+")":""))}});$("cxo").innerHTML=h;$("cxs").textContent=won(s);t.push("합계(자재비, 기준가·부가세 별도): "+won(s));t.push(location.href.split("?")[0]);last=t.join("\\n")}}
{js}
document.querySelector(".cxw").addEventListener("input",calc);document.querySelector(".cxw").addEventListener("change",calc);$("cxchj").onclick=function(){{WWHJ("calc",last,this)}};$("cxc").onclick=function(){{try{{if(navigator.share){{navigator.share({{title:document.title,text:last,url:location.href.split("#")[0]}}).catch(function(){{}});return}}navigator.clipboard.writeText(last);this.textContent="복사됐어요"}}catch(e){{prompt("복사하세요",last)}}}};calc()}})();</script>'''
    page(slug, title, desc, body, "/calc.html")


def gen3(page, P, E, CTA, faqslide, TEL):
    """데크 자재 계산기(/deck-gyesan.html), 가벽 자재 계산기(/gabyeok-gyesan.html)"""
    pr = lambda rx: _price(P, rx)
    DB = [("25×140 방부 데크재(12자)", 140, 3.6, pr(r"방부-25\*140\*12자\(데크\)")), ("20×120 방부 데크재(12자)", 120, 3.6, pr(r"방부-20\*120\*12자\(데크\)")),
          ("15×95 방부 데크재(12자)", 95, 3.6, pr(r"방부-15\* 95\*12자\(데크\)")), ("40×140 방부 데크(1800)", 140, 1.8, pr(r"방부-방부데크 @40\*140\*1800"))]
    LUM = {"b24": pr(r"방부- 2\* 4\*12자\(파인\)"), "b26": pr(r"방부- 2\* 6\*12자\(파인\)"), "b44": pr(r"방부- 4\*4\*12자"), "g24": pr(r"구조-Ⅱ 2\* 4\*12ft"),
           "gyp": pr(r"석고-일반 3\*6 @ 9\.5T$"), "gyp12": pr(r"석고-일반 3\*6 @12\.5T"), "pink50": pr(r"단열-아이소핑크 @900\*1800\*50T")}
    dj = json.dumps({"db": DB, "l": LUM}, ensure_ascii=False)
    opts = "".join(f'<option value="{i}">{n}{" — " + format(p, ",") + "원/개" if p else ""}</option>' for i, (n, w, L, p) in enumerate(DB))
    inp = f'''<div class="gjr"><label>데크 길이(판 방향)<input id="dl" type="number" inputmode="decimal" step="0.1" value="3.6"><i>m</i></label><label>데크 폭<input id="dw" type="number" inputmode="decimal" step="0.1" value="2.4"><i>m</i></label></div>
<div class="gjr"><label>데크재<select id="dt">{opts}</select></label><label>바닥에서 높이<input id="dh" type="number" inputmode="decimal" step="0.05" value="0.4"><i>m</i></label></div>
<div class="gjr"><label>장선 간격<select id="ds"><option value="0.4">400mm(권장)</option><option value="0.45">450mm</option><option value="0.3">300mm(얇은 판)</option></select></label><label>기둥 간격<select id="dp"><option value="1.2">1.2m</option><option value="1.5">1.5m</option></select></label></div>'''
    js = f'''var D={dj};function calc(){{var L=+$("dl").value||0,W=+$("dw").value||0,h=+$("dh").value||0,t=D.db[+$("dt").value],sp=+$("ds").value,pp=+$("dp").value;
var rows=Math.ceil(W*1000/(t[1]+5)),per=Math.ceil(L/t[2]),boards=Math.ceil(rows*per*1.05);
var nj=Math.ceil(L/sp)+1,jp=Math.ceil(W/3.6),joist=nj*jp;
var nb=Math.ceil(W/pp)+1,beam=nb*Math.ceil(L/3.6);
var np=nb*(Math.ceil(L/pp)+1),cut=Math.max(1,Math.floor(3.6/Math.max(h+0.1,0.3))),post=Math.ceil(np/cut);
var screws=rows*nj*2;
out([["데크재",t[0],boards,t[3],"개"],["장선(방부 2×4, 3.6m)",sp*1000+"mm 간격 "+nj+"줄",joist,D.l.b24,"개"],["멍에(방부 2×6, 3.6m)",nb+"줄 · 기둥 위",beam,D.l.b26,"개"],["기둥(방부 4×4, 3.6m)",np+"개 자리 · 높이 "+h+"m씩 잘라 씀",post,D.l.b44,"개"],["데크용 스텐 피스","판 1장이 장선을 지날 때마다 2개",screws,0,"개(약)"]],
"데크 면적 <b>"+(L*W).toFixed(1)+"㎡</b>("+(L*W/3.3058).toFixed(1)+"평) · 판 "+rows+"줄 · 장선 "+nj+"줄 · 기둥 "+np+"개","[영진목재 데크 자재 계산] "+L+"×"+W+"m, 높이 "+h+"m")}}'''
    fq = faqslide([("데크 장선 간격은 얼마로 하나요?", "25T 데크재는 보통 400mm, 얇은 판(15~20T)은 300~400mm로 촘촘하게 합니다. 간격이 넓으면 밟을 때 출렁입니다."),
                   ("데크 기초는 어떻게 하나요?", "땅이면 주춧돌·기초석이나 콘크리트 기초 위에 기둥받침 철물로 기둥을 세웁니다. 기초 자재는 현장 상태에 따라 달라 이 계산에는 넣지 않았습니다(목재 철물 > 주춧돌·기둥받침 참고)."),
                   ("데크재 사이 간격은요?", "물빠짐과 수축을 위해 판 사이 3~5mm를 띄웁니다. 계산기는 5mm로 계산합니다."),
                   ("오일스테인은 얼마나 필요하나요?", "제품 표기 도포량에 따라 다릅니다. 데크 면적×2회÷도포량(㎡/L)으로 계산하세요(도배·장판 계산기 페인트 탭 활용).")])
    _page(page, "deck-gyesan.html", "데크 자재 계산기 — 데크재·장선·멍에·기둥·피스 몇 개? 비용까지 | 영진목재",
          "데크 크기와 높이만 넣으면 방부 데크재·장선(2×4)·멍에(2×6)·기둥(4×4)·피스 수량과 자재비를 기준가로 바로 계산합니다. 결과 복사 가능.",
          "데크 자재 계산기", "데크 크기와 높이를 넣으면 <b>데크재·장선·멍에·기둥·피스</b>가 몇 개 필요하고 자재비가 얼마인지 바로 나옵니다. 방부목은 원하는 길이로 잘라 드립니다.",
          inp, js, fq, CTA, TEL, '<p class="small">기둥받침·주춧돌 같은 기초 철물은 <a href="/cheolmul/gidungbatchim.html">기둥받침·캡</a>, <a href="/cheolmul/juchudol.html">주춧돌</a>, 장선 고정은 <a href="/cheolmul/janseon.html">장선걸이</a>를 보세요.</p>')
    inp2 = '''<div class="gjr"><label>가벽 길이<input id="gl" type="number" inputmode="decimal" step="0.1" value="3.0"><i>m</i></label><label>천장 높이<input id="gh" type="number" inputmode="decimal" step="0.1" value="2.4"><i>m</i></label></div>
<div class="gjr"><label>문 구멍<select id="gd"><option value="0">없음</option><option value="1">문 1개</option></select></label><label>스터드 간격<select id="gs"><option value="0.45">450mm</option><option value="0.4">400mm</option><option value="0.6">600mm</option></select></label></div>
<div class="gjr"><label>석고보드<select id="gb"><option value="2,1">양면 1겹 9.5T</option><option value="2,2">양면 2겹 9.5T</option><option value="1,1">한면 1겹 9.5T</option><option value="2,1,12">양면 1겹 12.5T</option></select></label><label>속채움 단열<select id="gi"><option value="0">없음</option><option value="1">아이소핑크 50T</option></select></label></div>'''
    js2 = f'''var D={dj};function calc(){{var L=+$("gl").value||0,H=+$("gh").value||0,dr=+$("gd").value,s=+$("gs").value,b=$("gb").value.split(","),sides=+b[0],lay=+b[1],thick=b[2]?"12.5T":"9.5T",ins=+$("gi").value;
var studs=Math.ceil(L/s)+1+(dr?2:0),sp=Math.ceil(H/3.6),plates=Math.ceil(L*2/3.6)+(dr?1:0);
var area=Math.max(0,L*H-(dr?1.9:0)),gyp=Math.ceil(area*sides*lay*1.1/1.62),ins_n=ins?Math.ceil(area*1.1/1.62):0,sc=gyp*25;
var r=[["스터드(구조재 2×4, 3.6m)",s*1000+"mm 간격 "+studs+"개"+(dr?" (문 양옆 보강 포함)":""),studs*sp,D.l.g24,"개"],["상·하부 깔도리(구조재 2×4)","바닥·천장 "+L+"m씩",plates,D.l.g24,"개"],["석고보드 "+thick+" 900×1800",(sides==2?"양면":"한면")+" "+lay+"겹",gyp,thick=="12.5T"?D.l.gyp12:D.l.gyp,"장"]];
if(ins)r.push(["아이소핑크 50T 900×1800","벽 속 채움",ins_n,D.l.pink50,"장"]);r.push(["석고보드 피스","1장에 약 25개",sc,0,"개(약)"]);
out(r,"가벽 면적 <b>"+area.toFixed(1)+"㎡</b> · 스터드 "+studs+"개 · 석고 "+gyp+"장","[영진목재 가벽 자재 계산] 길이 "+L+"m × 높이 "+H+"m")}}'''
    fq2 = faqslide([("가벽 각재는 뭘 쓰나요?", "방 칸막이는 구조재 2×4(38×89mm)를 많이 씁니다. 얇게 하려면 다루끼(30×30·30×60)나 경량철골도 씁니다. 매장에서 원하는 길이로 잘라 드립니다."),
                    ("석고보드는 몇 겹이 좋나요?", "일반 칸막이는 양면 1겹, 소리를 더 막고 싶으면 양면 2겹에 속을 단열재·흡음재로 채웁니다."),
                    ("문을 달 수 있나요?", "네. 문 자리 양옆에 스터드를 겹쳐 세우고 위에 상인방을 대면 됩니다. 문틀·문짝은 방문·문틀 가격 가이드를 보세요.")])
    _page(page, "gabyeok-gyesan.html", "가벽 자재 계산기 — 각재(2×4)·석고보드·단열재 몇 개? 비용까지 | 영진목재",
          "가벽 길이와 높이만 넣으면 구조재 2×4 스터드·깔도리, 석고보드(1·2겹), 아이소핑크, 피스 수량과 자재비를 기준가로 바로 계산합니다.",
          "가벽 자재 계산기", "칸막이(가벽) 길이와 높이를 넣으면 <b>각재·석고보드·단열재·피스</b>가 몇 개 필요하고 자재비가 얼마인지 바로 나옵니다.",
          inp2, js2, fq2, CTA, TEL, '<p class="small">시공 순서는 <a href="/sigongbeop/">자재 시공법</a>, 석고보드 종류는 <a href="/knauf/seokgo.html">석고보드</a>를 보세요.</p>')
