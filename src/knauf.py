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
            fq = [(f"크나우프 {r[1]} 어디서 사나요?", f"대전 서구 영진종합목재(월드건축자재) 매장에서 상담·주문하실 수 있고, 전국 용달 배송도 됩니다. {HOURS}."),
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
        fq = faqslide([(f"크나우프 {g} 어디서 사나요?", f"{ADDR} 영진종합목재(월드건축자재) 매장에서 상담·주문합니다. {HOURS}. 전국 용달 배송도 됩니다."),
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
