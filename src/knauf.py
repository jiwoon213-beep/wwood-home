# -*- coding: utf-8 -*-
"""크나우프(knauf.com/ko-KR — 회사 허락, 사장님 2026-11-15) 석고보드·흡음 천장재·단열재·아쿠아패널·경량철골·본드 — /knauf/
데이터: src/data/knauf.tsv (분류|이름|한줄설명|상품주소|사진id|특징(;)|규격|색상·용량). 가격은 매장 문의.
같은 상품주소는 한 번만. 기존 쇼핑몰 '[크나우프] 인슐레이션'은 build.py에서 뺌(중복 제거)."""
import os, re
from yerim import LB

def IMG(i, w=600): return f"https://media.knauf.com/a/{i}?wid={w}"
# 화면 분류(순서) → (주소, 전체 자재 분류코드, 설명)
GRP = {"석고보드": ("seokgo", "27", "일반·방화·방수·방균·차음·고강도 석고보드"),
       "흡음 석고보드·석고 천장재": ("heubeum", "27", "유공 흡음 석고보드, 석고텍스·석고 천장재, 미네랄 천장재"),
       "미네랄 천장재": ("mineral", "27", "T바용 미네랄 흡음 천장 타일"),
       "금속 천장재": ("metal-ceiling", "27", "클립인·레이인 금속 천장, 금속 배플"),
       "목모 흡음 패널": ("mokmo", "27", "목재 울(목모) 흡음 천장·벽 패널"),
       "흡음 배플·플로팅 패널": ("baffle", "27", "공간에 매다는 흡음 배플, 플로팅 캐노피, 펠트 패널"),
       "단열재": ("danyeol", "30", "목조주택 벽·지붕용 글라스울, 상업용 천장·칸막이·외단열"),
       "아쿠아패널(시멘트보드)": ("aquapanel", "31", "실내·외부·천장용 메쉬 보강 시멘트보드"),
       "경량철골·천장틀": ("steel", "32", "고차음 스터드·러너, 천장 T바·몰딩"),
       "본드·컴파운드·부자재": ("bond", "37", "석고보드 본드, 조인트 컴파운드, 프라이머, 메쉬·테이프·나사")}

# 분류 페이지 추가 FAQ — 구글 검색어(크나우프 석고보드·천장재·단열재·아쿠아보드, 2026-11-20) 보강
GFAQ = {
    "석고보드": [("크나우프 석고보드 종류는 어떤 게 있나요?", "일반석고보드(9.5·12.5·15mm), 방균석고보드, 방화석고보드(12.5~25mm), 방수석고보드(9.5·12.5mm), 방화방수석고보드(12.5·15·19mm), 차음석고보드, 고강도 하드월, 방수·방균 아쿠아락E 등이 있습니다. 아래 사진을 누르면 제품별 규격을 볼 수 있습니다."),
              ("방수석고보드는 몇 T를 쓰나요?", "크나우프 방수석고보드는 9.5mm·12.5mm 두 가지입니다. 두께별 쓰임은 '방수석고보드 두께' 글(/qna/bangsu-seokgo-duggae.html)에 정리했습니다."),
              ("석고보드를 벽에 바로 붙이는 본드도 있나요?", "콘크리트·블록 벽에는 크나우프 집본드·집본드S 같은 석고보드 부착용 본드로 붙이기도 합니다. 붙이는 순서는 '집본드 에스' 글(/qna/jibbond-s.html)을 참고하세요.")],
    "흡음 석고보드·석고 천장재": [("크나우프 천장재는 어떤 종류가 있나요?", "구멍 뚫린 흡음 석고보드(아트사운드·크리네오·디자인패널 등), T바에 얹는 석고 천장재, 미네랄 천장재, 금속 천장재, 목모 흡음 패널로 나뉩니다. 위 분류 버튼으로 종류별로 볼 수 있습니다."),
              ("유공석고보드와 크리네오는 무엇이 다른가요?", "둘 다 구멍 뚫린 흡음 석고보드인데, 크리네오는 판 이음 자리에도 구멍 무늬가 끊기지 않고 이어지는 '무한유공' 제품입니다. 고르는 법은 '유공석고보드' 글(/qna/yugong-seokgo.html)에 정리했습니다.")],
    "아쿠아패널(시멘트보드)": [("아쿠아보드·아쿠아판넬이 이 제품인가요?", "현장에서 아쿠아보드, 아쿠아판넬이라고도 부르는 크나우프 아쿠아패널은 메쉬로 보강한 시멘트보드입니다. 실내용 12.5mm, 외부용 12.5mm, 8mm(기존 벽 보강용·천장용) 4가지가 있습니다."),
              ("석고보드 대신 아쿠아패널을 쓰는 곳은 어디인가요?", "물이 직접 닿는 욕실 벽이나 외벽 바탕처럼 석고보드가 견디기 어려운 곳에 씁니다. 이음매는 전용 조인트 테이프·필러로 처리합니다.")],
    "단열재": [("크나우프 인슐레이션 단열재는 어떤 건가요?", "크나우프 인슐레이션은 에코배트 글라스울 계열 단열재로, 목조주택 벽용(월), 지붕·천장용(루프&실링), 칸막이용(인터널 파티션), 상업용 천장(커머셜 실링), 외벽용(스마트 파사드) 등으로 나뉩니다."),
              ("크나우프 단열재는 두께를 어떻게 고르나요?", "벽·지붕 구조와 지역 단열 기준에 따라 달라집니다. 도면이나 시공 부위를 알려 주시면 매장에서 맞는 제품을 골라 드립니다.")],
}
GFAQ["석고보드"] += [("방균·방화·차음 석고보드는 어떻게 고르나요?", "곰팡이가 걱정되면 방균(/qna/banggyun-seokgo.html), 내화가 필요한 벽은 방화(/qna/banghwa-seokgo-duggae.html), 옆방 소리를 줄이려면 차음석고보드(/qna/chaeum-seokgo.html)를 고릅니다. 종류 비교는 /bigyo/gypsum-types.html 에 있습니다."),
    ("석고보드 1장 가격은요?", "매장 기준가는 '석고보드 가격'(/gagyeok/seokgo-gagyeok.html)에 정리했습니다. 크나우프 품번별 가격은 매장에 문의해 주세요.")]
GFAQ["흡음 석고보드·석고 천장재"] += [("천장 흡음보드는 어떻게 시공하나요?", "T바·M바 천장틀에 얹거나 석고보드 천장 위에 붙입니다. 기존 텍스 교체는 '흡음텍스 교체'(/qna/heubeum-tex-gyoche.html)를 보세요."),
    ("흡음보드와 흡음재는 무엇이 다른가요?", "흡음재는 벽 속 솜, 흡음보드는 겉에 마감까지 되는 판입니다(/bigyo/heupeum-board.html).")]
GFAQ["아쿠아패널(시멘트보드)"] += [("아쿠아패널은 어떻게 자르나요?", "시멘트보드라 칼로 한쪽 면을 긋고 꺾은 뒤 반대쪽 메쉬를 자르는 방식이나 전용 톱날로 자릅니다. 이음매는 전용 테이프와 조인트필러로 처리합니다.")]
GFAQ["단열재"] += [("단열재 가등급·나등급은 무엇인가요?", "열이 통하는 정도로 나눈 등급으로 가등급이 성능이 가장 좋습니다(/qna/danyeoljae-deunggeup.html)."),
    ("그라스울과 미네랄울은 어떻게 다른가요?", "둘 다 불에 강한 무기질 솜 단열재로, 원료(유리·암석)와 무게·흡음 특성이 다릅니다(/bigyo/glasswool-vs-mineralwool.html).")]
GFAQ["경량철골·천장틀"] = [("시그마 스터드는 무엇인가요?", "크나우프 시그마 스터드는 1등급 단일 고차음 시스템용 경량철골 스터드로, 러너(바닥·천장 레일)와 짝을 이뤄 석고보드 벽의 뼈대가 됩니다. 규격은 1000·1150·1300×124×45mm가 있습니다."),
    ("스터드와 러너는 어떻게 다른가요?", "러너는 바닥·천장에 먼저 고정하는 ㄷ자 레일이고, 스터드는 러너 사이에 세로로 세우는 기둥입니다. 간격은 '스터드·장선 간격'(/qna/stud-ganggyeok.html) 글을 참고하세요."),
    ("T바 천장틀은 어디에 쓰나요?", "메인 러너·L 몰딩으로 격자를 만들고 그 위에 600×600 등 천장재를 얹는 방식으로, 사무실·상가 천장에 많이 씁니다.")]
GFAQ["본드·컴파운드·부자재"] = [("집본드와 집본드S는 무엇이 다른가요?", "둘 다 콘크리트·블록 바탕에 석고보드를 붙이는 본드입니다. 쓰는 법은 '집본드 에스'(/qna/jibbond-s.html)에 정리했습니다."),
    ("아쿠아패널 이음매는 무엇으로 처리하나요?", "전용 조인트 테이프를 붙이고 아쿠아패널 조인트필러로 메운 뒤, 필요하면 스킴코트로 표면을 정리합니다.")]

def sub(r):
    g, n = r[0], r[1]
    if g != "수입 흡음 천장재": return g
    if "METALWORKS" in n: return "금속 천장재"
    if "HERADESIGN" in n: return "목모 흡음 패널"
    if re.search("SOUNDSCAPES|FELTWORKS|OPTRA Wall", n): return "흡음 배플·플로팅 패널"
    return "미네랄 천장재"

def load(ROOT):
    p = os.path.join(ROOT, "data", "knauf.tsv")
    if not os.path.exists(p): return []
    rows, seen = [], set()
    for l in open(p, encoding="utf-8"):
        x = l.rstrip("\n").split("|")
        if len(x) < 8 or x[3] in seen: continue
        seen.add(x[3]); x[0] = sub(x); rows.append(x)
    return rows

def spec(r):
    out = []
    if r[2]: out.append(("용도", r[2]))
    if r[5]: out.append(("특징", " · ".join(s.strip() for s in r[5].split(";") if s.strip())))
    if r[6]: out.append(("규격(mm)" if "×" in r[6] else "규격", r[6].replace("mm", "") if "×" in r[6] else r[6]))
    if r[7]: out.append(("용량" if "kg" in r[7] else "색상", r[7]))
    out.append(("제조사", "크나우프(Knauf)"))
    return out

def gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT):
    rows = load(ROOT)
    if not rows: return []
    def card(r):
        sp = "\n".join(f"{a}\t{b}" for a, b in spec(r))
        return (f'<a class="yri" href="#" data-big="{IMG(r[4], 900)}" data-n="{E(r[1])}" data-sp="{E(sp)}">'
                f'<img loading="lazy" decoding="async" referrerpolicy="no-referrer" width="300" height="300" src="{IMG(r[4], 400)}" alt="크나우프 {E(r[1])}"><span>{E(r[1])}</span><em class="cbp q">매장 문의</em></a>')
    tops = [g for g in GRP if any(r[0] == g for r in rows)]
    nav = lambda cur: '<div class="glk tkn">' + "".join(f'<a href="/knauf/{GRP[g][0]}.html"{" class=on" if g == cur else ""}>{E(g)}</a>' for g in tops) + '</div>'
    def pslug(r):
        t = re.sub(r"[^a-z0-9.-]+", "-", r[3].lower()).strip("-")
        return t if len(t) <= 80 else t[:64] + "-" + t[-15:]
    for g in tops:  # 제품별 상세 페이지 /knauf/p/
        xs = [r for r in rows if r[0] == g]
        for r in xs:
            sp = spec(r)
            rel = [x for x in xs if x is not r][:8]
            tb = "".join(f"<tr><th>{E(a)}</th><td>{E(b)}</td></tr>" for a, b in sp)
            fq = [(f"크나우프 {r[1]} 어디서 사나요?", f"대전 유성구 영진종합목재(월드건축자재) 매장에서 상담·주문하실 수 있고, 전국 용달 배송도 됩니다. {HOURS}."),
                  (f"크나우프 {r[1]} 가격은 얼마인가요?", "규격·수량에 따라 달라 매장이나 전화(042-545-2900)로 견적을 드립니다."),
                  (f"크나우프 {r[1]}는 어디에 쓰나요?", r[2] or g)]
            ld = [{"@context": "https://schema.org", "@type": "Product", "name": f"크나우프 {r[1]}", "image": IMG(r[4], 900), "description": (r[2] or g)[:200], "brand": {"@type": "Brand", "name": "Knauf"}, "category": g},
                  {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}]
            body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › <a href="/knauf/">크나우프</a> › <a href="/knauf/{GRP[g][0]}.html">{E(g)}</a> › {E(r[1])}</p>'
                    f'<h1>크나우프 {E(r[1])}</h1><p class="glead">{E(r[2] or g)}</p>'
                    f'<p><img src="{IMG(r[4], 800)}" alt="크나우프 {E(r[1])}" width="600" height="600" referrerpolicy="no-referrer" style="max-width:100%;height:auto;border-radius:12px;background:#fff"></p>'
                    f'<div class="tw"><table class="cmp"><tbody>{tb}<tr><th>가격</th><td>매장 문의 (규격·수량별 견적)</td></tr></tbody></table></div>'
                    f'<div class="row"><a class="b d" href="tel:0425452900">전화 문의 042-545-2900</a><a class="b o" href="/jeonguk/">전국 배송 지역</a><a class="b o" href="/knauf/{GRP[g][0]}.html">{E(g)} 전체 보기</a></div></section>'
                    f'<section class="wrap sec gg"><h2 class="gt">같은 분류 제품</h2><ul class="mgl">' + "".join(f'<li><a href="/knauf/p/{pslug(x)}.html">크나우프 {E(x[1])}</a></li>' for x in rel) + '</ul></section>'
                    f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{faqslide(fq)}</section>{CTA}')
            page(f"knauf/p/{pslug(r)}.html", f"크나우프 {r[1]} — 규격·특징·구매 | 대전 영진목재",
                 f"크나우프(Knauf) {r[1]}: {(r[2] or g)[:70]}. 규격 {r[6] or '확인'}. 대전 영진종합목재 상담·전국 배송.", body, "/jaryo/", ld, IMG(r[4], 800))
    out = []
    for g in tops:
        xs = [r for r in rows if r[0] == g]
        fq = faqslide(GFAQ.get(g, []) + [(f"크나우프 {g} 어디서 사나요?", f"{ADDR} 영진종합목재(월드건축자재) 매장에서 상담·주문합니다. {HOURS}. 전국 용달 배송도 됩니다."),
                       (f"크나우프 {g} 가격은 얼마인가요?", "제품·규격·수량에 따라 달라서 매장이나 전화(042-545-2900)로 견적을 드립니다.")])
        body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › <a href="/knauf/">크나우프</a> › {E(g)}</p><h1>크나우프 {E(g)} <small>{len(xs)}가지</small></h1>'
                f'<p class="glead">{E(GRP[g][2])}. 사진을 누르면 크게 보고 규격·특징을 확인할 수 있습니다.</p>{nav(g)}'
                f'<h2 class="gt"><span>{E(g)} <small style="font-size:14px">{len(xs)}가지</small></span><small>옆으로 넘겨 보세요 ›</small></h2><div class="yrg">{"".join(card(r) for r in xs)}</div></section>'
                f'<section class="wrap sec gg"><h2 class="gt">제품별 자세히 보기</h2><ul class="mgl">' + "".join(f'<li><a href="/knauf/p/{pslug(r)}.html">{E(r[1])}</a></li>' for r in xs) + '</ul></section>'
                f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{fq}</section>{CTA}' + LB)
        nm = ", ".join(dict.fromkeys(re.sub(r"\s*[\d.]+mm.*$|\s*\(.*$", "", r[1]) for r in xs))
        page(f"knauf/{GRP[g][0]}.html", f"크나우프 {g} {len(xs)}종 — {nm[:40]} | 대전 영진목재",
             f"크나우프(Knauf) {g} {len(xs)}가지 사진·규격: {GRP[g][2]}. 대전 유성 영진종합목재 상담·전국 배송.", body, "/jaryo/", None, IMG(xs[0][4], 800))
        out.append((g, xs))
    rws = "".join(f'<h2 class="gt"><span><a href="/knauf/{GRP[g][0]}.html" style="color:inherit;text-decoration:none">{E(g)}</a> <small style="font-size:14px">{len(xs)}가지</small></span><small>옆으로 넘겨 보세요 ›</small></h2><div class="yrg">{"".join(card(r) for r in xs[:12])}' + (f'<a class="yri ymore" href="/knauf/{GRP[g][0]}.html"><span>{E(g)} 전체 {len(xs)}가지 보기 ›</span></a>' if len(xs) > 12 else "") + '</div>' for g, xs in out)
    page("knauf/index.html", f"크나우프 석고보드·흡음 천장재·단열재 {len(rows)}종 — 아쿠아패널·경량철골 | 대전 영진목재",
         f"크나우프(Knauf) 석고보드·방화·방수·흡음 천장재·에코배트 단열재·아쿠아패널 {len(rows)}가지 사진과 규격. 대전 유성 영진종합목재 상담·전국 배송.",
         f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › 크나우프</p><h1>크나우프(Knauf) 석고보드·천장재·단열재</h1><p class="glead">석고보드부터 흡음 천장재, 에코배트 단열재, 아쿠아패널 시멘트보드, 경량철골·본드까지 {len(rows)}가지. 사진을 누르면 규격과 특징을 볼 수 있고, 가격은 매장에서 안내합니다.</p>{nav(None)}{rws}</section>{CTA}' + LB,
         "/jaryo/", None, IMG(rows[0][4], 800))
    return out
