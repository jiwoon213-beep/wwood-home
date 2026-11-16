"""단위 계산기: 평수 계산기(/pyeong.html), 목재 재(才) 계산기(/jae.html)
확인된 환산만 씀: 1평 = 400/121 ㎡(약 3.3058㎡), 1치 = 30.303mm(1자=303.03mm의 1/10), 1재 = 1치×1치×12자."""
import json


def gen(page, E, CTA, faqslide, TEL):
    css = '''<style>.ucard{background:#fff;border:1px solid #ece6dc;border-radius:20px;padding:16px;box-shadow:0 6px 20px rgba(0,0,0,.05)}.urow{display:flex;gap:10px;align-items:flex-end}.urow label{flex:1;display:flex;flex-direction:column;gap:6px;font-size:13px;font-weight:700;color:#6b645a}.urow input,.urow select{height:58px;border:1.5px solid #e0d9cd;border-radius:14px;padding:0 14px;font:inherit;font-size:24px;font-weight:800;width:100%;box-sizing:border-box;background:#fff}.uswap{flex:none;width:46px;height:58px;border:0;border-radius:14px;background:#1D1B18;color:#fff;font-size:20px;cursor:pointer}
.ures{margin-top:14px;background:#1D1B18;color:#fff;border-radius:18px;padding:16px 18px}.ures small{display:block;font-size:12.5px;opacity:.65;font-weight:700}.ures b{display:block;font-size:34px;font-weight:900;color:#ffd27a;letter-spacing:-.5px}.ures span{font-size:13px;opacity:.75}
.uqs{display:flex;gap:8px;overflow-x:auto;padding:12px 0 4px;scrollbar-width:none}.uqs::-webkit-scrollbar{display:none}.uqs button{flex:none;height:42px;padding:0 14px;border:1px solid #e6dfd5;border-radius:999px;background:#fff;font:inherit;font-weight:800;font-size:14px;cursor:pointer}
.utb{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px}.utb div{background:#fff;border:1px solid #ece6dc;border-radius:14px;padding:10px 12px}.utb b{display:block;font-size:17px}.utb small{color:#8a8378;font-size:12px}
.ulk{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:16px}.ulk a{display:flex;flex-direction:column;gap:2px;background:#fff;border:1px solid #ece6dc;border-radius:14px;padding:12px;color:#1D1B18!important;text-decoration:none!important}.ulk b{font-size:15px}.ulk span{font-size:12.5px;color:#8a8378}</style>'''
    links = '''<div class="ulk"><a href="/yesi/"><b>몇 평이면 얼마?</b><span>데크·루바·석고 평수별 자재비</span></a><a href="/gyeonjeok.html"><b>방 통째로 계산</b><span>공정별 자재비 합계</span></a><a href="/calc.html"><b>자재 계산기</b><span>몇 장·몇 개 필요한지</span></a><a href="/cut.html"><b>재단 미리보기</b><span>원하는 크기·재단비</span></a></div>'''

    # 1) 평수 계산기
    PY = 400 / 121
    tbl = "".join(f'<div><b>{p}평</b><small>{p * PY:.2f}㎡</small></div>' for p in (1, 3, 5, 10, 15, 18, 20, 24, 25, 30, 32, 34, 40, 45, 50))
    fq = [("1평은 몇 ㎡인가요?", "1평은 약 3.3058㎡(400/121㎡)입니다. ㎡를 평으로 바꿀 때는 ㎡ × 0.3025, 평을 ㎡로 바꿀 때는 평 × 3.3058 을 하면 됩니다."),
          ("가로·세로 m로 평수를 구하려면요?", "가로(m) × 세로(m)로 ㎡를 구한 뒤 0.3025를 곱하면 평입니다. 예를 들어 3.6m × 2.7m = 9.72㎡ ≈ 2.9평입니다. 위 계산기의 '가로×세로' 칸에 넣으면 바로 나옵니다."),
          ("평수로 자재가 몇 장 필요한지도 알 수 있나요?", "네. 평수별 자재비 예시에서 데크·루바·석고보드·합판·단열재가 몇 장·얼마인지 볼 수 있고, 자재 계산기에서 내 크기로 바로 계산할 수 있습니다.")]
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}
    body = f'''<section class="wrap sec"><p class="crumb"><a href="/calc.html">자재 계산기</a> › 평수 계산기</p><h1>평수 계산기 — 평 ↔ ㎡ 바로 변환</h1>
<p class="lead">평을 넣으면 ㎡, ㎡를 넣으면 평이 바로 나옵니다. 방 가로·세로(m)로도 평수를 구할 수 있어요. (1평 = 약 3.3058㎡)</p>
<div class="ucard"><div class="urow"><label>평<input id="up" type="number" inputmode="decimal" step="0.1" value="10"></label><button class="uswap" type="button" aria-label="바꾸기">⇄</button><label>㎡<input id="um" type="number" inputmode="decimal" step="0.1"></label></div>
<div class="uqs">{"".join(f'<button type="button" data-p="{p}">{p}평</button>' for p in (1, 3, 5, 10, 18, 24, 32, 34, 40))}</div>
<h2 style="font-size:16px;margin:14px 0 8px">가로 × 세로로 구하기</h2><div class="urow"><label>가로(m)<input id="uw" type="number" inputmode="decimal" step="0.1" value="3.6"></label><label>세로(m)<input id="uh" type="number" inputmode="decimal" step="0.1" value="2.7"></label></div>
<div class="ures"><small>가로 × 세로 넓이</small><b id="ur">0평</b><span id="ur2"></span></div></div>
<h2>자주 쓰는 평수 → ㎡</h2><div class="utb">{tbl}</div>
<p class="small muted">1평 = 400/121㎡ ≈ 3.3058㎡ 로 계산합니다(소수 둘째 자리 반올림).</p>{links}
<h2>자주 묻는 질문</h2>{faqslide(fq)}</section>{CTA}{css}
<script>(function(){{var $=function(i){{return document.getElementById(i)}},K=400/121,f=function(x){{return (Math.round(x*100)/100).toLocaleString("ko-KR")}};
function p2m(){{$("um").value=Math.round((+$("up").value||0)*K*100)/100}}function m2p(){{$("up").value=Math.round((+$("um").value||0)/K*100)/100}}
function wh(){{var a=(+$("uw").value||0)*(+$("uh").value||0);$("ur").textContent=f(a/K)+"평";$("ur2").textContent=f(a)+"㎡ ("+$("uw").value+"m × "+$("uh").value+"m)"}}
$("up").oninput=p2m;$("um").oninput=m2p;$("uw").oninput=$("uh").oninput=wh;document.querySelector(".uswap").onclick=function(){{var a=$("up").value;$("up").value=$("um").value;$("um").value=a;m2p();p2m()}};
[].forEach.call(document.querySelectorAll(".uqs button"),function(b){{b.onclick=function(){{$("up").value=b.dataset.p;p2m()}}}});p2m();wh()}})();</script>'''
    page("pyeong.html", "평수 계산기 — 평 ㎡ 변환, 가로×세로로 평수 구하기 | 영진목재", "평수 계산기: 평을 ㎡로, ㎡를 평으로 바로 변환(1평=3.3058㎡). 방 가로·세로로 평수 구하기, 자주 쓰는 평수 표, 평수별 자재비까지.", body, "/calc.html", ld)

    # 2) 목재 재 계산기
    CHI = 303.03 / 10  # 1치(mm)
    JAE = CHI * CHI * 3636.36 / 1e9  # 1재(m³)
    ex = [("2×4 (38×89mm) 12자(3.6m)", 38, 89, 3600), ("다루끼 30×30mm 12자", 30, 30, 3600), ("방부 데크재 20×120mm 3.6m", 20, 120, 3600), ("각재 89×89mm(4×4) 3.6m", 89, 89, 3600), ("판재 25×150mm 2.4m", 25, 150, 2400)]
    extb = "".join(f'<tr><th>{E(n)}</th><td data-l="1개">{t * w * l / 1e9 / JAE:.2f}재</td><td data-l="10개">{10 * t * w * l / 1e9 / JAE:.1f}재</td><td data-l="부피(1개)">{t * w * l / 1e9:.4f}㎥</td></tr>' for n, t, w, l in ex)
    fq2 = [("목재 1재는 얼마만큼인가요?", f"1재(才)는 1치 × 1치 × 12자 크기의 부피입니다. 1치는 약 30.3mm, 12자는 약 3.64m라서 1재는 약 {JAE:.5f}㎥, 1㎥는 약 {1 / JAE:.0f}재입니다."),
           ("재 수는 어떻게 계산하나요?", "두께(mm) × 폭(mm) × 길이(mm) × 개수로 부피를 구한 뒤 1재 부피로 나눕니다. 위 계산기에 mm로 넣으면 재 수와 ㎥가 바로 나옵니다."),
           ("2×4 한 개는 몇 재인가요?", f"2×4 실제 치수 38×89mm, 길이 3.6m 기준으로 1개 약 {38 * 89 * 3600 / 1e9 / JAE:.2f}재입니다. 길이·치수에 따라 달라지니 계산기로 확인하세요.")]
    ld2 = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq2]}
    body2 = f'''<section class="wrap sec"><p class="crumb"><a href="/calc.html">자재 계산기</a> › 목재 재 계산기</p><h1>목재 재(才) 계산기 — 재 수·㎥ 바로 계산</h1>
<p class="lead">두께·폭·길이(mm)와 개수를 넣으면 재 수와 부피(㎥)가 바로 나옵니다. 1재 = 1치 × 1치 × 12자(약 {JAE:.5f}㎥).</p>
<div class="ucard"><div class="urow"><label>두께(mm)<input id="jt" type="number" inputmode="decimal" value="38"></label><label>폭(mm)<input id="jw" type="number" inputmode="decimal" value="89"></label></div>
<div class="urow" style="margin-top:10px"><label>길이(mm)<select id="jl"><option value="1800">1800 (6자)</option><option value="2400">2400 (8자)</option><option value="2700">2700 (9자)</option><option value="3000">3000 (10자)</option><option value="3600" selected>3600 (12자)</option><option value="0">직접 입력</option></select></label><label>개수<input id="jn" type="number" inputmode="numeric" value="10"></label></div>
<div class="urow" id="jlw" style="margin-top:10px;display:none"><label>길이 직접(mm)<input id="jlc" type="number" inputmode="numeric" value="3600"></label></div>
<div class="uqs"><button type="button" data-v="38,89">2×4</button><button type="button" data-v="38,140">2×6</button><button type="button" data-v="19,89">1×4</button><button type="button" data-v="30,30">다루끼 30각</button><button type="button" data-v="89,89">4×4</button><button type="button" data-v="20,120">데크 20×120</button></div>
<div class="ures"><small>합계</small><b id="jr">0재</b><span id="jr2"></span></div></div>
<h2>자주 쓰는 목재 재 수</h2><div class="tw"><table class="rt"><thead><tr><th>목재</th><th>1개</th><th>10개</th><th>부피(1개)</th></tr></thead><tbody>{extb}</tbody></table></div>
<p class="small muted">1치 = 30.303mm, 12자 = 3636.36mm 기준. 판매 단위·가격은 품목마다 달라 <a href="/price.html">기준가</a>에서 확인하세요.</p>{links}
<h2>자주 묻는 질문</h2>{faqslide(fq2)}</section>{CTA}{css}
<script>(function(){{var $=function(i){{return document.getElementById(i)}},J={JAE!r};
function run(){{var L=+$("jl").value||+$("jlc").value||0;$("jlw").style.display=+$("jl").value?"none":"";var v=(+$("jt").value||0)*(+$("jw").value||0)*L*(+$("jn").value||0)/1e9;$("jr").textContent=(Math.round(v/J*100)/100).toLocaleString("ko-KR")+"재";$("jr2").textContent=(Math.round(v*10000)/10000)+"㎥ · 1개 "+(Math.round(v/(+$("jn").value||1)/J*100)/100)+"재"}}
["jt","jw","jl","jn","jlc"].forEach(function(i){{$(i).oninput=$(i).onchange=run}});[].forEach.call(document.querySelectorAll(".uqs button"),function(b){{b.onclick=function(){{var a=b.dataset.v.split(",");$("jt").value=a[0];$("jw").value=a[1];run()}}}});run()}})();</script>'''
    page("jae.html", "목재 재(才) 계산기 — 재 수·㎥ 계산, 2×4 몇 재 | 영진목재", f"목재 재 계산기: 두께·폭·길이·개수로 재 수와 ㎥를 바로 계산. 1재=1치×1치×12자(약 {JAE:.5f}㎥). 2×4·다루끼·데크재 재 수 표.", body2, "/calc.html", ld2)
