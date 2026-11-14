# -*- coding: utf-8 -*-
"""삼익산업(siwood.com — 회사 허락) 구조재·외장재·지붕재·내장재·창호·도어·기능재·조경·기타 — /samik/
데이터: src/data/samik.tsv (1차|2차|idx|이름|사진|브랜드·두께|규격 설명) — .github/scripts/fetch_samik.py 가 매일 갱신.
같은 상품번호·같은 이름은 한 번만. 우리 쇼핑몰 자재(products.tsv)와 이름이 같은 건 build.py 에서 기존 쪽을 뺌. 가격은 매장 문의."""
import os, re
from yerim import LB

IMG = lambda p: "https://www.siwood.com" + p
SLUG = {"구조재": "gujo", "외장재": "oejang", "지붕재": "jibung", "내장재": "naejang", "창호": "changho", "도어": "door", "기능재": "gineung", "조경": "jogyeong", "기타": "etc"}
JC = {"구조재": "23", "외장재": "31", "지붕재": "31", "내장재": "27", "창호": "29w", "도어": "29", "기능재": "30", "조경": "25", "기타": "37"}  # 전체 자재 분류 연결
DESC = {"구조재": "경량목구조·중목구조·특수목구조 자재", "외장재": "세라믹·시멘트 사이딩, 외장목재, 석재·타일, 스타코", "지붕재": "세라믹·적삼목 지붕재, 아스팔트슁글, 물받이",
        "내장재": "내장목재·인테리어패널·몰딩·계단재·판재·석고·마루", "창호": "PVC·ALU 시스템창, 천창", "도어": "현관도어·실내도어·인테리어도어",
        "기능재": "단열재·기밀/방습·실리콘·방수", "조경": "데크재·방부목·조경용품", "기타": "철물·스테인·방부액·공구·임가공"}
key = lambda s: re.sub(r"[\s\-·()\[\]/,.]", "", s).lower()


def load(ROOT):
    p = os.path.join(ROOT, "data", "samik.tsv")
    if not os.path.exists(p): return []
    rows, si, sn = [], set(), set()
    for l in open(p, encoding="utf-8"):
        x = l.rstrip("\n").split("|")
        if len(x) < 7 or x[2] in si or key(x[3]) in sn: continue
        si.add(x[2]); sn.add(key(x[3])); rows.append(x)
    return rows


def spec(r):
    out = []
    if r[5]:
        b = [s.strip() for s in r[5].split("ㅣ") if s.strip()]
        if b: out.append(("브랜드·두께", " · ".join(b)))
    for part in re.split(r"\s*(?:ㅣ|/)\s*", r[6]):
        if ":" in part:
            k, _, v = part.partition(":")
            if k.strip() and v.strip(): out.append((k.strip(), v.strip()))
        elif part.strip() and len(part) < 60: out.append(("설명", part.strip()))
    return out[:8]


def gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT):
    rows = load(ROOT)
    if not rows: return []
    def card(r):
        sp = "\n".join(f"{a}\t{b}" for a, b in spec(r))
        return (f'<a class="yri" href="#" data-big="{IMG(r[4])}" data-n="{E(r[3])}"' + (f' data-sp="{E(sp)}"' if sp else "") +
                f'><img loading="lazy" decoding="async" referrerpolicy="no-referrer" width="300" height="300" src="{IMG(r[4])}" alt="{E(r[1] + " " + r[3])}"><span>{E(r[3])}</span><em class="cbp q">매장 문의</em></a>')
    tops = [t for t in SLUG if any(r[0] == t for r in rows)]
    nav = lambda cur: '<div class="glk tkn">' + "".join(f'<a href="/samik/{SLUG[t]}.html"{" class=on" if t == cur else ""}>{E(t)}</a>' for t in tops) + '</div>'
    out = []
    for t in tops:
        xs = [r for r in rows if r[0] == t]
        subs = list(dict.fromkeys(r[1] for r in xs))
        sec = "".join(f'<h2 class="gt" id="s{i}"><span>{E(s)} <small style="font-size:14px">{sum(1 for r in xs if r[1] == s)}가지</small></span><small>옆으로 넘겨 보세요 ›</small></h2><div class="yrg">{"".join(card(r) for r in xs if r[1] == s)}</div>' for i, s in enumerate(subs))
        ch = ('<div class="qk">' + "".join(f'<a href="#s{i}">{E(s)}</a>' for i, s in enumerate(subs)) + '</div>') if len(subs) > 1 else ""
        fq = faqslide([(f"{t} 어디서 사나요?", f"{ADDR} 영진종합목재(월드건축자재) 매장에서 상담·주문합니다. {HOURS}. 전국 용달 배송도 됩니다."),
                       (f"{t} 가격은 얼마인가요?", "제품·규격·수량에 따라 달라서 매장이나 전화(042-545-2900)로 견적을 드립니다.")])
        body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › <a href="/samik/">삼익산업</a> › {E(t)}</p><h1>삼익산업 {E(t)} <small>{len(xs)}가지</small></h1><p class="glead">{E(DESC.get(t, ""))}. 사진을 누르면 크게 보고 규격을 확인할 수 있습니다.</p>{nav(t)}{ch}{sec}</section>'
                f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{fq}</section>{CTA}' + LB)
        page(f"samik/{SLUG[t]}.html", f"삼익산업 {t} {len(xs)}종 — {', '.join(subs[:4])} | 대전 영진목재", f"삼익산업 {t} {len(xs)}가지 사진·규격: {DESC.get(t, '')}. 대전 유성 영진종합목재 상담·전국 배송.", body, "/jaryo/", None, IMG(xs[0][4]))
        out.append((t, xs))
    rws = "".join(f'<h2 class="gt"><span><a href="/samik/{SLUG[t]}.html" style="color:inherit;text-decoration:none">{E(t)}</a> <small style="font-size:14px">{len(xs)}가지</small></span><small>옆으로 넘겨 보세요 ›</small></h2><div class="yrg">{"".join(card(r) for r in xs[:12])}<a class="yri ymore" href="/samik/{SLUG[t]}.html"><span>{E(t)} 전체 {len(xs)}가지 보기 ›</span></a></div>' for t, xs in out)
    page("samik/index.html", f"삼익산업 건축자재 {len(rows)}종 — 사이딩·지붕재·내장재·창호·단열재 | 대전 영진목재",
         f"삼익산업 세라믹 사이딩·지붕재·내장목재·시스템창·도어·단열재 {len(rows)}가지 사진과 규격. 대전 유성 영진종합목재 상담·전국 배송.",
         f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › 삼익산업</p><h1>삼익산업 건축자재</h1><p class="glead">목조주택·외장·지붕·내장·창호·단열까지 {len(rows)}가지(같은 제품은 한 번만). 사진을 누르면 규격을 볼 수 있습니다.</p>{nav(None)}{rws}</section>{CTA}' + LB, "/jaryo/", None, IMG(rows[0][4]))
    return out
