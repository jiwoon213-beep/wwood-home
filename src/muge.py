# 자재 무게 계산기(/muge.html) — '합판 무게', '석고보드 무게', '1톤 트럭 몇 장' 검색용
# 무게는 일반적인 밀도로 계산한 대략값(제품·수종·함수율에 따라 차이) — 페이지에 분명히 표시.

MAT = [  # 이름, 밀도 kg/m³, 기본 두께들, 기본 크기(mm)
    ("합판(라왕·일반)", 550, [4.8, 8.5, 11.5, 15, 18], (1220, 2440)),
    ("MDF", 720, [3, 6, 9, 12, 15, 18], (1220, 2440)),
    ("OSB", 620, [11.1, 18.3], (1220, 2440)),
    ("석고보드", 800, [9.5, 12.5], (900, 1800)),
    ("집성판(고무나무·아카시아)", 650, [15, 18, 24, 30], (1220, 2440)),
    ("집성판(소나무·스프러스)", 480, [15, 18, 24, 30], (1220, 2440)),
    ("방부목(소나무)", 600, [20, 25, 38], (140, 3600)),
    ("구조재(SPF)", 450, [38], (89, 3600)),
    ("아이소핑크(압출 단열재)", 35, [30, 50, 100], (900, 1800)),
]


def gen(page, E, CTA, faqslide, TEL):
    import json
    rows = ""
    for n, d, ts, (w, l) in MAT:
        for t in ts:
            kg = w / 1000 * l / 1000 * t / 1000 * d
            rows += f"<tr><td>{n}</td><td>{t:g}T · {w}×{l}</td><td><b>약 {kg:.1f}kg</b></td><td>{'부피가 먼저 참' if d < 100 else f'약 {int(1000 // kg)}장'}</td></tr>"
    fq = [("합판 1장 무게는 얼마인가요?", "4×8(1220×2440) 일반 합판은 대략 11.5T 약 19kg, 18T 약 29kg입니다. 수종과 습기에 따라 10~20% 차이가 납니다."),
          ("석고보드 1장 무게는요?", "3×6(900×1800) 일반 석고보드 9.5T는 약 12kg, 12.5T는 약 16kg 안팎입니다(밀도 약 800kg/㎥로 계산)."),
          ("1톤 트럭에 합판 몇 장 실을 수 있나요?", "무게로만 보면 18T 합판은 약 33장, 11.5T는 약 52장입니다. 실제로는 적재함 크기와 안전 기준이 있으니 매장에서 배송 상담하세요."),
          ("이 무게는 정확한가요?", "일반적인 밀도로 계산한 대략값입니다. 같은 자재도 제품·수종·마른 정도에 따라 달라지니 참고용으로 쓰세요.")]
    js = json.dumps([[n, d, ts, [w, l]] for n, d, ts, (w, l) in MAT], ensure_ascii=False)
    body = f'''<section class="wrap sec"><p class="crumb"><a href="/">홈</a> › <a href="/calc.html">자재 계산기</a> › 무게 계산</p>
<h1>합판·석고보드 무게 계산기 — 1장 몇 kg, 1톤에 몇 장</h1>
<p class="lead">자재와 두께·크기·장수를 넣으면 대략 무게와 1톤 트럭 기준 장수가 나옵니다. 차에 실을지, 용달을 부를지 정할 때 참고하세요.</p>
<div class="mgc"><label>자재<select id="mm"></select></label><label>두께(mm)<input id="mt" type="number" step="0.1" inputmode="decimal"></label>
<label>가로(mm)<input id="mw" type="number" inputmode="numeric"></label><label>세로·길이(mm)<input id="ml" type="number" inputmode="numeric"></label><label>장수<input id="mn" type="number" value="1" inputmode="numeric"></label></div>
<div class="mgr" id="mr"></div>
<p class="small muted">일반적인 밀도로 계산한 대략값입니다(제품·수종·습기에 따라 10~20% 차이). 실제 배송은 <a href="/baesong.html">전국 배송</a>에서 상담하세요.</p>
<h2>자주 쓰는 자재 1장 무게</h2>
<div class="tw"><table><tr><th>자재</th><th>두께·크기(mm)</th><th>1장 무게</th><th>1톤 기준</th></tr>{rows}</table></div>
<p class="small muted">1톤 기준은 무게로만 나눈 장수입니다. 적재함 크기·고정·안전 기준은 따로 따져야 해요.</p>
<div class="row"><a class="b r" href="/cut.html">재단 미리보기</a><a class="b o" href="/gyugyeok.html">규격표</a><a class="b o" href="/calc.html">자재 계산기</a><a class="b d" href="tel:{TEL.replace('-', '')}">배송 전화 문의</a></div>
<h2>자주 묻는 질문</h2>{faqslide(fq)}</section>
<style>.mgc{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin:14px 0}}.mgc label{{display:flex;flex-direction:column;font-size:14px;font-weight:700;gap:4px}}.mgc select,.mgc input{{font-size:17px;padding:10px;border:1px solid #d8d0c4;border-radius:10px}}.mgr{{background:#1D1B18;color:#fff;border-radius:14px;padding:16px;font-size:18px;line-height:1.6}}.mgr b{{color:#ffd65a;font-size:26px}}</style>
<script>(function(){{var M={js},s=document.getElementById("mm");M.forEach(function(m,i){{var o=document.createElement("option");o.value=i;o.textContent=m[0];s.appendChild(o)}});
function q(i){{return document.getElementById(i)}}function f(){{var m=M[s.value],t=+q("mt").value,w=+q("mw").value,l=+q("ml").value,n=+q("mn").value||1;var kg=w/1000*l/1000*t/1000*m[1];
q("mr").innerHTML=kg>0?("1장 약 <b>"+kg.toFixed(1)+"kg</b><br>"+n+"장 합계 약 <b>"+(kg*n).toFixed(0)+"kg</b><br><small>1톤 트럭 무게 기준 약 "+Math.floor(1000/kg)+"장</small>"):"두께와 크기를 넣어 주세요";}}
function d(){{var m=M[s.value];q("mt").value=m[2][Math.min(1,m[2].length-1)];q("mw").value=m[3][0];q("ml").value=m[3][1];f()}}
s.onchange=d;["mt","mw","ml","mn"].forEach(function(i){{q(i).oninput=f}});d();}})();</script>''' + CTA
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}
    page("muge.html", "합판·석고보드 무게 계산기 — 1장 몇 kg, 1톤 트럭에 몇 장 | 영진목재",
         "합판 18T 1장 약 29kg, 석고보드 9.5T 약 12kg. 자재·두께·크기·장수로 무게와 1톤 트럭 기준 장수 계산.", body, jsonld=ld)
