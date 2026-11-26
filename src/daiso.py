# 다이소 철물·실리콘·공구 품목 + 내 위치 근처 다이소 찾기(/geuncheo/daiso.html)
# 품목·가격: daisomall.co.kr 공개 검색 결과(조사일 DATE). 다이소와 관계없는 안내 페이지, 매장마다 재고·가격 다를 수 있음.
import os
DATE = "2026-11-26"
GROUPS = [  # 이름, 다이소 소분류들, 우리 쪽 안내(링크, 글)
    ("실리콘·실란트·보수제", ["윤활방청/보수제"], ("/qna/silicone-jongryu.html", "실리콘 종류와 용도"), "욕실·창틀 틈 보수는 다이소 300ml 실리콘으로 충분한 경우가 많습니다. 현장에서 여러 통이 필요하거나 외부·창호용 전문 실리콘이 필요하면 철물점·자재상이 낫습니다."),
    ("접착제", ["다용도접착제"], ("/qna/mokgong-bond.html", "목공본드 고르기"), "순간접착제·에폭시는 소품 수리용입니다. 가구 조립·판재 접착은 목공본드, 석고보드는 전용 본드를 씁니다."),
    ("테이프", ["공구테이프", "양면테이프"], ("/qna/silicone-ssogi.html", "실리콘 쏘는 법(마스킹)"), "마스킹·청면·알루미늄·방수 테이프까지 있습니다. 넓은 면적 보양용은 보양재·롤 단위가 경제적입니다."),
    ("못·나사·장석·경첩", ["못/나사", "기타공구"], ("/pis-gilee.html", "피스 길이 고르는 법"), "소포장 나사못·못·장석·경첩이 있어 소품 수리에 좋습니다. 데크·구조용처럼 길고 많이 쓰는 피스는 박스 단위로 사는 편이 낫습니다."),
    ("수공구", ["드라이버", "렌치", "펜치류", "망치", "줄/톱", "측정/측량도구", "공구함", "보안/안전용품"], ("/bupum/", "철물·공구·부속 전체"), "드라이버·펜치·망치·줄자·톱 같은 기본 수공구가 있습니다. 매일 쓰는 현장 공구는 내구성 좋은 제품을 따로 갖추는 편이 좋습니다."),
    ("사포·스크래퍼·붓·페인트·바니쉬", ["스크래퍼/사포", "페인트/락카", "페인트붓/브러쉬"], ("/bondex/", "본덱스 스테인·페인트"), "소용량 바니쉬·젯소·벽면 페인트가 있어 작은 가구 리폼에 맞습니다. 데크·외부 목재는 오일스테인을 씁니다."),
    ("타카·글루건", ["타카", "글루건"], ("/taka/", "타카·타카핀 규격"), "손 타카와 심, 글루건이 있습니다. 루바·몰딩 시공용 에어·충전 타카와 실타카 핀은 공구점·자재상에서 구합니다."),
    ("문풍지·방충망", ["문풍지", "방충망"], ("/qna/munpungji.html", "문풍지 붙이는 법"), "문풍지·문틈막이·방충망 보수 테이프가 종류별로 있습니다."),
    ("전기·전선 정리", ["멀티탭", "전선정리용품", "케이블타이", "전구", "철사/노끈"], ("/qna/", "하는 법 Q&A"), "멀티탭·케이블타이·전선 보호관·LED 전구가 있습니다. 전기 배선 공사는 전문 자격자에게 맡깁니다."),
    ("시트지·리폼", ["시트지도구", "디자인시트지", "주방시트지/타일"], ("/younglim/film.html", "인테리어 필름"), "작은 면 리폼용 시트지·밀대가 있습니다. 문·몰딩·싱크대 전체를 바꾸려면 폭이 넓은 인테리어 필름이 이음매 없이 깔끔합니다."),
    ("문·후크·안전", ["방문닫힘방지", "부착식행거"], ("/qna/", "하는 법 Q&A"), "도어스토퍼·후크·못 후크 같은 소품이 있습니다."),
]


SLUG = ['silicone', 'jeopchakje', 'tape', 'nasa-mot', 'gongu', 'sapo-paint', 'taka-gluegun', 'munpungji', 'jeongi', 'sheetji', 'hook']
STITLE = ['다이소 실리콘·실란트 종류와 가격 — 실리콘건·제거 스크래퍼까지', '다이소 접착제 종류 — 순간접착제·에폭시·벽지 보수 접착제', '다이소 테이프 종류 — 마스킹·청면·알루미늄·방수 테이프', '다이소 나사못·못·경첩·장석 — 길이별 소포장 정리', '다이소 공구 — 드라이버·펜치·망치·톱·줄자 가격', '다이소 사포·페인트·바니쉬·젯소 — 가구 리폼 재료', '다이소 타카·글루건 — 손 타카 심·글루건 심', '다이소 문풍지·방충망 — 종류와 가격', '다이소 멀티탭·케이블타이·전선 정리·LED 전구', '다이소 시트지 — 리폼 시트지·주방 시트지·밀대', '다이소 도어스토퍼·후크 — 문·벽 소품']


def gen(page, E, CTA, faqslide, ROOT):
    p = os.path.join(ROOT, "data", "daiso_items.tsv")
    if not os.path.exists(p): return
    rows = [l.rstrip("\n").split("\t") for l in open(p, encoding="utf-8") if l.strip()]
    sec = ""; tot = 0; toc = []
    for i, (gn, subs, (lk, lkn), note) in enumerate(GROUPS):
        its = [r for r in rows if r[4] in subs]
        if not its: continue
        tot += len(its); toc.append(f'<a href="/geuncheo/daiso-{SLUG[i]}.html">{E(gn)} {len(its)}</a>')
        sec += (f'<h2 id="g{i}">다이소 {E(gn)} <small class="muted">{len(its)}가지</small></h2><p>{E(note)} <a href="{lk}">{E(lkn)} ›</a></p>'
                '<div class="tw"><table class="rt"><thead><tr><th>다이소 품목</th><th>다이소 판매가</th></tr></thead><tbody>'
                + "".join(f'<tr><th>{E(r[1])}</th><td data-l="판매가">{int(r[2]):,}원</td></tr>' for r in sorted(its, key=lambda r: (int(r[2]), r[1])))
                + '</tbody></table></div>')
    fq = [("다이소에서 실리콘 살 수 있나요?", "네. 다이소에 300ml 백색 실리콘·투명·회색 실란트와 실리콘 건, 실리콘 제거·마감 스크래퍼가 있습니다(" + DATE + " 다이소몰 기준). 매장마다 재고가 다를 수 있습니다."),
          ("다이소에 피스·못도 있나요?", "목재용 나사못(12·16·20·40·60mm 세트), 못, 콘크리트용 못 세트, 장석·경첩이 소포장으로 있습니다. 데크·구조용처럼 많이 쓰는 피스는 철물점·자재상에서 박스로 사는 편이 낫습니다."),
          ("근처 다이소는 어떻게 찾나요?", "이 페이지 위의 '내 위치 근처 다이소 찾기'를 누르면 휴대폰 위치로 지도 앱(네이버·카카오·구글)에서 가까운 다이소가 바로 나옵니다."),
          ("다이소에 없는 현장 자재는요?", "목재·합판·석고보드·단열재·데크재·대용량 철물은 철물점·자재상에서 구합니다. 대전 영진종합목재는 원하는 크기로 재단해 전국 배송합니다.")]
    body = (f'<section class="wrap sec"><p class="crumb"><a href="/geuncheo.html">현장 근처 찾기</a> › 다이소 철물·실리콘</p><h1>다이소 철물·실리콘·공구 — 파는 품목 {tot}가지와 근처 다이소 찾기</h1>'
            f'<p class="lead">현장에서 실리콘·테이프·나사가 급할 때, 가까운 다이소에서 살 수 있는 철물·공구·보수용품을 정리했습니다. 버튼 한 번으로 <b>내 위치 근처 다이소</b>도 찾습니다.</p>'
            '<div class="dsw"><button type="button" id="dsme" class="dsme">📍 내 위치 근처 다이소 찾기</button><div id="dsr" hidden></div></div>'
            f'<p class="small muted">품목·가격은 다이소몰 공개 정보({DATE} 조사)이며 매장마다 재고·가격이 다를 수 있습니다. 이 페이지는 다이소와 관계없는 안내 페이지입니다.</p>'
            f'<div class="olk">{"".join(toc)}</div>{sec}'
            '<div class="gcad" style="margin-top:18px"><b>🪵 다이소에 없는 목재·합판·석고보드·단열재·데크재</b><span>대전 영진종합목재 — 원하는 크기로 재단해 전국 현장까지 배송</span></div>'
            f'<h2>자주 묻는 질문</h2>{faqslide(fq)}<p><a class="b o" href="/geuncheo.html">현장 근처 철물점·인력사무소·용달 찾기 ›</a></p></section>'
            '<style>.dsw{background:#fff;border:2px solid #e4ded4;border-radius:18px;padding:16px;margin:14px 0}.dsme{width:100%;font-size:20px;font-weight:900;padding:16px;border:0;border-radius:14px;background:#1D1B18;color:#fff;cursor:pointer}#dsr a{display:block;text-align:center;font-weight:800;font-size:18px;padding:14px;border-radius:12px;margin-top:10px;text-decoration:none}#dsr .nv{background:#03C75A;color:#fff}#dsr .kk{background:#FEE500;color:#191919}#dsr .gg{background:#f1efe9;color:#1D1B18}</style>'
            '<script>(function(){var b=document.getElementById("dsme"),r=document.getElementById("dsr"),q=encodeURIComponent("다이소");function show(L){var nv="https://map.naver.com/p/search/"+q,g="https://www.google.com/maps/search/?api=1&query="+encodeURIComponent("내 주변 다이소");if(L){var x=L[1]*20037508.34/180,y=Math.log(Math.tan((90+ +L[0])*Math.PI/360))/(Math.PI/180)*20037508.34/180;nv+="?c="+x.toFixed(2)+","+y.toFixed(2)+",15,0,0,0,dh";g="https://www.google.com/maps/search/"+q+"/@"+L[0]+","+L[1]+",14z"}r.hidden=false;r.innerHTML=(L?"<b>내 위치 근처 다이소</b>":"<b>위치를 못 받아서 지도 앱에서 근처로 찾아요</b>")+"<a class=nv href=\\""+nv+"\\">네이버지도에서 보기</a><a class=kk href=\\"https://map.kakao.com/link/search/"+q+"\\">카카오맵에서 보기</a><a class=gg href=\\""+g+"\\">구글지도에서 보기</a>"}b.onclick=function(){b.textContent="위치 확인 중…";if(!navigator.geolocation){show(null);return}navigator.geolocation.getCurrentPosition(function(p){b.textContent="📍 내 위치 근처 다이소 찾기";show([p.coords.latitude.toFixed(5),p.coords.longitude.toFixed(5)])},function(){b.textContent="📍 내 위치 근처 다이소 찾기";show(null)},{timeout:8000})}})()</script>' + CTA)
    page("geuncheo/daiso.html", f"다이소 철물·실리콘·공구 {tot}가지 — 파는 품목·가격, 내 위치 근처 다이소 찾기 | 영진목재",
         f"다이소에서 파는 실리콘·실란트·피스·못·경첩·테이프·공구·문풍지·방충망·시트지 {tot}가지를 가격과 함께 정리. 버튼 한 번으로 내 위치 근처 다이소 찾기.", body, "/geuncheo.html",
         [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}])

    _js = body[body.find('<style>.dsw'):body.find('</script>') + 9]
    for i, (gn, subs, (lk, lkn), note) in enumerate(GROUPS):
        its = [r for r in rows if r[4] in subs]
        if not its: continue
        lo = min(int(r[2]) for r in its)
        tb = ('<div class="tw"><table class="rt"><thead><tr><th>다이소 품목</th><th>다이소 판매가</th></tr></thead><tbody>'
              + "".join(f'<tr><th>{E(r[1])}</th><td data-l="판매가">{int(r[2]):,}원</td></tr>' for r in sorted(its, key=lambda r: (int(r[2]), r[1]))) + '</tbody></table></div>')
        ofq = [(f"다이소 {gn}는 얼마인가요?", f"{DATE} 다이소몰 기준 {lo:,}원부터 있으며, 품목별 가격은 위 표에 있습니다. 매장마다 재고·가격이 다를 수 있습니다."),
               (f"다이소 {gn}로 충분할까요?", note),
               ("근처 다이소는 어떻게 찾나요?", "위의 '내 위치 근처 다이소 찾기' 버튼을 누르면 지도 앱에서 가까운 다이소가 바로 나옵니다.")]
        ob = (f'<section class="wrap sec"><p class="crumb"><a href="/geuncheo.html">현장 근처 찾기</a> › <a href="/geuncheo/daiso.html">다이소 철물·실리콘</a> › {E(gn)}</p><h1>{E(STITLE[i].split(" — ")[0])}</h1>'
              f'<p class="lead">다이소에서 파는 {E(gn)} {len(its)}가지를 가격과 함께 정리했습니다({lo:,}원부터). {E(note)}</p>'
              '<div class="dsw"><button type="button" id="dsme" class="dsme">📍 내 위치 근처 다이소 찾기</button><div id="dsr" hidden></div></div>'
              + tb + f'<p><a class="b o" href="{lk}">{E(lkn)} ›</a></p>'
              f'<p class="small muted">품목·가격은 다이소몰 공개 정보({DATE} 조사)이며 매장마다 다를 수 있습니다. 다이소와 관계없는 안내 페이지입니다.</p>'
              f'<h2>자주 묻는 질문</h2>{faqslide(ofq)}<h2>다른 다이소 품목</h2><div class="olk">' + "".join(f'<a href="/geuncheo/daiso-{SLUG[k]}.html">다이소 {E(g[0])}</a>' for k, g in enumerate(GROUPS) if k != i) + '</div>'
              '<div class="gcad" style="margin-top:18px"><b>🪵 목재·합판·석고보드·단열재·데크재는 영진종합목재</b><span>원하는 크기로 재단해 전국 현장까지 배송 · 대전 유성대로 44</span></div></section>' + _js + CTA)
        page(f"geuncheo/daiso-{SLUG[i]}.html", f"{STITLE[i]} | 영진목재", f"다이소 {gn} {len(its)}가지 가격({lo:,}원부터, {DATE} 기준)과 쓰임. 내 위치 근처 다이소 바로 찾기.", ob, "/geuncheo/daiso.html",
             [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in ofq]}])
