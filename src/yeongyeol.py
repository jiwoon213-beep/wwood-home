# 공정별 시공팀 연결(/yeongyeol/) — 거래처 이름·번호는 화면에 넣지 않음. 손님은 매장으로 전화, 매장이 거래처에 연결.
import os, re

GJ = [  # slug, 공정, 하는 일, 영상 검색어(정규식), 같이 볼 페이지
    ("mokgong", "목공(목수)", "가벽·천장·몰딩·문틀·아트월 등 인테리어 목공", r"목공|목수|가벽|천장 공사|몰딩|문틀", [("/sigongbeop/seokgo-byeok.html", "석고보드 벽 시공법"), ("/gabyeok-gyesan.html", "가벽 자재 계산기")]),
    ("dobae", "도배·장판", "벽지 도배, 장판 교체", r"도배|장판|벽지", [("/sigongbeop/", "자재 시공법")]),
    ("tile", "타일·수전·설비", "욕실·주방 타일, 수전 교체, 배관 설비", r"(?<!데코)타일|욕실|수전|설비", [("/sigongbeop/yoksil-tile.html", "욕실 타일 시공법")]),
    ("film", "인테리어 필름", "문·문틀·싱크대·가구 필름 리폼", r"필름", [("/sigongbeop/film-sigong.html", "필름 시공법"), ("/gagyeok/interior-film.html", "필름 가격")]),
    ("shassi", "샷시·현관문·유리", "샷시 교체, 현관문·터닝도어·방화문, 유리", r"샷시|현관문|방화문|유리|창호", [("/gagyeok/door-gagyeok.html", "문 가격")]),
    ("folding", "폴딩도어", "베란다·카페·상가 폴딩도어", r"폴딩", []),
    ("cheolgeo", "철거", "인테리어 철거, 폐기물 정리", r"철거", []),
    ("decotile", "데코타일", "데코타일 바닥 시공", r"데코타일", [("/sigongbeop/decotile.html", "데코타일 시공법")]),
    ("maru", "마루", "강마루·강화마루 시공(시공만도 가능)", r"마루", [("/sigongbeop/gangmaru.html", "강마루 시공법")]),
    ("paint", "페인트", "수성 페인트, 탄성코트", r"페인트|탄성", [("/bondex/", "본덱스 페인트·스테인")]),
    ("jeongi", "전기·조명", "전기 배선, 콘센트·스위치, 조명 교체", r"전기공사|전기 공사|조명|배선|전선", []),
    ("gagu", "가구", "싱크대, 붙박이장 등 맞춤 가구", r"싱크대|붙박이|가구|수납장", []),
    ("blind", "블라인드·커튼", "블라인드, 커튼 설치", r"블라인드|커튼", []),
]


def gen(page, E, CTA, faqslide, TEL, ROOT):
    vids = []
    for ln in open(f"{ROOT}/data/videos.tsv", encoding="utf-8"):
        c = ln.rstrip("\n").split("\t")
        if len(c) >= 6 and os.path.exists(f"{ROOT}/../v/{c[0]}.html"): vids.append((c[0], c[1], c[5].strip('"').replace('""', '"')))
    T = TEL.replace("-", "")
    how = ('<ol class="sstp"><li><i>1</i><p>아래에서 <b>공정</b>을 고르고 매장으로 전화하세요.</p></li>'
           '<li><i>2</i><p><b>지역·현장 크기·원하는 작업</b>을 알려 주세요. 현장 사진이 있으면 더 빠릅니다.</p></li>'
           '<li><i>3</i><p>매장이 그 공정을 하는 <b>거래 시공팀</b>에 연결해 드립니다. 견적·일정은 시공팀과 바로 상의하세요.</p></li></ol>')
    cards, links = "", []
    for slug, nm, job, rx, rel in GJ:
        vs = [v for v in vids if re.search(rx, v[2])]
        vs = [v for v in vs if v[1] == "L"][:4] + [v for v in vs if v[1] != "L"][:4]
        vs = vs[:6]
        vh = "".join(f'<a class="ygv" href="/v/{i}.html"><img loading="lazy" src="https://i.ytimg.com/vi/{i}/mqdefault.jpg" alt=""><span>{E(t[:40])}</span></a>' for i, k, t in vs)
        fq = [(f"대전·세종 {nm} 시공팀을 소개받을 수 있나요?", f"네. 매장({TEL})으로 전화해 지역과 작업 내용을 알려 주시면 영진종합목재와 거래하는 {nm} 시공팀에 연결해 드립니다."),
              ("견적과 일정은 어떻게 정하나요?", "현장 크기·상태에 따라 달라 시공팀이 직접 보고 정합니다. 현장 사진을 준비해 두시면 빠릅니다."),
              ("자재도 같이 살 수 있나요?", "네. 필요한 자재는 매장에서 고르고 원하는 크기로 재단해 드립니다.")]
        fld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}
        relh = "".join(f'<a class="b" href="{u}">{E(n)}</a>' for u, n in rel)
        body = f'''<section class="wrap sec"><p class="crumb"><a href="/yeongyeol/">시공팀 연결</a> › {E(nm)}</p><h1>대전·세종 {E(nm)} 시공팀 연결</h1>
<p class="lead">{E(job)}. 영진종합목재와 거래하는 {E(nm)} 시공팀을 매장에서 연결해 드립니다.</p>
<div class="ygbox"><b>{E(nm)}</b><span>{E(job)}</span><small>시공 지역: 대전·세종 (그 밖 지역은 전화로 확인)</small><a class="b r" href="tel:{T}">매장에 연결 요청 · {TEL}</a></div>
<h2>이렇게 연결해 드려요</h2>{how.replace('아래에서 <b>공정</b>을 고르고 매장으로 전화하세요.', '위 버튼으로 <b>매장에 전화</b>하세요.')}
{('<h2>' + E(nm) + ' 시공 영상</h2><div class="ygvs">' + vh + '</div><p class="hsh">옆으로 넘겨 보세요 ›</p>') if vh else ''}
{('<div class="yact">' + relh + '</div>') if relh else ''}
<h2>자주 묻는 질문</h2>{faqslide(fq)}
<h2>다른 공정</h2><div class="olk">{"".join(f'<a href="/yeongyeol/{s}.html">{E(n)}</a>' for s, n, *_ in GJ if s != slug)}</div></section>{CTA}'''
        page(f"yeongyeol/{slug}.html", f"대전·세종 {nm} 시공팀 연결 — {job} | 영진목재", f"대전·세종 {nm}({job}) 시공팀을 영진종합목재 매장에서 연결해 드립니다. 전화 {TEL}. 자재 구매·재단도 함께.", body, "/sigong.html", fld)
        cards += f'<a class="ygc" href="/yeongyeol/{slug}.html"><b>{E(nm)}</b><span>{E(job)}</span><u>연결 요청 ›</u></a>'
        links.append((slug, nm))
    page("yeongyeol/index.html", "대전·세종 인테리어 시공팀 연결 — 목공·도배·타일·샷시·필름·마루·전기 13개 공정 | 영진목재",
         f"목공, 도배·장판, 타일·설비, 필름, 샷시·현관문, 폴딩도어, 철거, 데코타일, 마루, 페인트, 전기·조명, 가구, 블라인드 — 영진종합목재가 거래 시공팀을 연결해 드립니다. 전화 {TEL}.",
         f'''<section class="wrap sec"><h1>공정별 시공팀 연결</h1><p class="lead">자재를 사 가시는 분들이 "시공할 사람 없나요?" 많이 물으십니다. 영진종합목재와 오래 거래한 공정별 시공팀을 매장에서 연결해 드립니다.</p>
<div class="ygg">{cards}</div>
<h2>이렇게 연결해 드려요</h2>{how}<div class="row"><a class="b r" href="tel:{T}">매장에 연결 요청 · {TEL}</a><a class="b" href="/sigong.html">월드아키텍쳐 직접 시공</a></div>
<p class="small muted">시공 지역: 대전·세종 중심(그 밖 지역은 전화로 확인). 견적·일정은 연결된 시공팀과 상의합니다.</p></section>{CTA}''', "/sigong.html")
    return links


CSS = '''
/* 시공팀 연결 */
.ygg{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:14px 0}
.ygc{display:flex;flex-direction:column;gap:4px;background:#fff;border:1px solid #ece6dc;border-radius:16px;padding:14px;color:#1D1B18!important;text-decoration:none!important}
.ygc b{font-size:16.5px;font-weight:900}.ygc span{font-size:13px;color:#6b655c;line-height:1.45;flex:1}.ygc u{text-decoration:none;color:#c41a1f;font-weight:800;font-size:13.5px;margin-top:4px}
.ygbox{display:flex;flex-direction:column;gap:4px;background:#1D1B18;color:#fff;border-radius:18px;padding:16px;margin:14px 0}
.ygbox b{font-size:20px}.ygbox span{opacity:.85}.ygbox small{opacity:.65}.ygbox .b{margin-top:10px;text-align:center}
.ygvs{display:flex;gap:10px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;padding-bottom:6px}
.ygv{flex:0 0 220px;scroll-snap-align:start;color:#1D1B18!important;text-decoration:none!important;font-size:13.5px;font-weight:700;line-height:1.4}
.ygv img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:12px;display:block;margin-bottom:6px}
'''
