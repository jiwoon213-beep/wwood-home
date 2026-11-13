# -*- coding: utf-8 -*-
"""본덱스코리아(이몰링 emalling.co.kr — 회사 허락) 스테인·바니쉬·페인트·오일·도장도구 — /bondex/
데이터: src/data/emall.tsv (분류|상품번호|이름|이미지|판매가|옵션|원산지), emall_cats.tsv (분류|상위|이름)
  .github/scripts/fetch_emall.py 가 매일 갱신(vendors.yml). 표시가 = 판매가 × 1.3, 100원 올림, '~', 부가세 포함.
같은 상품번호·같은 이름은 한 번만. 철물박사(/bupum/)의 본덱스 계열 상품은 cmbs.py 에서 뺍니다."""
import os, re
from yerim import LB

IMG = lambda p: "https://www.emalling.co.kr/web/product/medium/" + p
SLUG = {24: "stain", 25: "paint", 26: "oil", 27: "bond", 64: "spray", 57: "brush", 69: "maco"}
DESC = {24: "방부방충 도료·수용성 스테인·수성/유성 바니쉬·실러", 25: "벽면·리폼·방수·콘크리트 페인트, 조색제·젯소", 26: "원목가구 하도·마감·컬러 오일, 왁스·신너",
        27: "목재 접착제·세척/제거제·우드필러", 64: "그레이코·에어렉스 도장기와 부속", 57: "브러쉬·로울러·트레이·샌딩도구", 69: "마코 도장도구(바니쉬·스테인·벽면용)"}
BRAND = re.compile(r"본덱스|bondex|비오파|biopa|드라이락|drylok|그레이코|graco|에어렉스|실카|sirca|마코", re.I)


def price(v):
    try: n = int(v)
    except Exception: return 0
    return 0 if n <= 0 else -(-int(n * 1.3 + 0.5) // 100) * 100


def load(ROOT):
    d = os.path.join(ROOT, "data")
    pc, pr = os.path.join(d, "emall_cats.tsv"), os.path.join(d, "emall.tsv")
    if not (os.path.exists(pc) and os.path.exists(pr)): return {}, []
    cats = {}
    for l in open(pc, encoding="utf-8"):
        x = l.rstrip("\n").split("|")
        if len(x) >= 3: cats[int(x[0])] = (int(x[1]), x[2])
    rows, seenp, seenn = [], set(), set()
    for l in open(pr, encoding="utf-8"):
        x = l.rstrip("\n").split("|")
        if len(x) < 5 or not x[0].isdigit(): continue
        key = re.sub(r"[\s\[\]()]", "", x[2]).lower()
        if x[1] in seenp or key in seenn: continue  # 같은 상품·같은 이름은 한 번만
        seenp.add(x[1]); seenn.add(key)
        rows.append((int(x[0]), x[1], re.sub(r"\s+", " ", x[2]).strip(), x[3], price(x[4]), x[5] if len(x) > 5 else "", x[6] if len(x) > 6 else ""))
    return cats, rows


def spec(r):
    out = []
    for op in [o for o in r[5].split(";") if o]:
        t, _, v = op.partition(":")
        vs = [s for s in v.split(",") if s.strip()]
        if vs: out.append((t.strip() or "옵션", " · ".join(vs[:20]) + (f" 외 {len(vs) - 20}가지" if len(vs) > 20 else "")))
    m = re.findall(r"\d+(?:\.\d+)?\s*(?:ml|mL|ML|L|l|kg|KG|g)(?![A-Za-z가-힣])", r[2])
    if m: out.insert(0, ("용량", " · ".join(dict.fromkeys(m))))
    if r[6] and r[6] not in ("기타", "기타국가", "상세설명참조"): out.append(("원산지", r[6]))
    return out


def gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT):
    cats, rows = load(ROOT)
    if not rows: return []
    kids = {}
    for n, (p, _) in cats.items(): kids.setdefault(p, []).append(n)
    by = {}
    for r in rows: by.setdefault(r[0], []).append(r)
    def items(n):
        o = list(by.get(n, []))
        for k in kids.get(n, []): o += items(k)
        return o
    def card(r, pre=""):
        sp = "\n".join(f"{a}\t{b}" for a, b in spec(r))
        pz = f'<em class="cbp">{r[4]:,}원~ <small>부가세 포함</small></em>' if r[4] else '<em class="cbp q">매장 문의</em>'
        return (f'<a class="yri" href="#" data-big="{IMG(r[3])}" data-n="{E(r[2])}"' + (f' data-sp="{E(sp)}"' if sp else "") +
                f'><img loading="lazy" decoding="async" referrerpolicy="no-referrer" width="300" height="300" src="{IMG(r[3])}" alt="{E(pre + r[2])}"><span>{E(r[2])}</span>{pz}</a>')
    tops = [t for t in SLUG if t in cats and items(t)]
    url = lambda t: f"/bondex/{SLUG[t]}.html"
    nav = lambda cur: '<div class="glk tkn">' + "".join(f'<a href="{url(t)}"{" class=on" if t == cur else ""}>{E(cats[t][1])}</a>' for t in tops) + '</div>'
    def fq(nm):
        return faqslide([(f"{nm} 어디서 사나요?", f"{ADDR} 영진종합목재(월드건축자재) 매장에서 상담·주문할 수 있습니다. {HOURS}. 칠할 나무·면적을 알려 주시면 양과 색을 같이 골라 드립니다."),
                         ("오일스테인은 1L로 몇 평 칠하나요?", "제품·나무 상태에 따라 다르지만 보통 1L로 약 8~10㎡(2회 칠 기준 4~5㎡) 정도입니다. 정확한 양은 제품 설명과 매장 상담으로 확인하세요.")])
    out = []
    for t in tops:
        subs = [k for k in kids.get(t, []) if items(k)] or [t]
        tx = items(t)
        sec = "".join(f'<h2 class="gt" id="c{k}"><span>{E(cats[k][1])} <small style="font-size:14px">{len(items(k))}가지</small></span><small>옆으로 넘겨 보세요 ›</small></h2><div class="yrg">{"".join(card(r, cats[k][1] + " ") for r in items(k))}</div>' for k in subs)
        ch = '<div class="qk">' + "".join(f'<a href="#c{k}">{E(cats[k][1])}</a>' for k in subs) + '</div>' if len(subs) > 1 else ""
        nm = cats[t][1].replace("/", "·")
        body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/paint.html">페인트·스테인</a> › <a href="/bondex/">본덱스</a> › {E(nm)}</p><h1>{E(nm)} <small>{len(tx)}가지</small></h1><p class="glead">{E(DESC.get(t, ""))}.</p>{nav(t)}{ch}{sec}'
                f'<div class="glk"><a href="/gagyeok/oilstain.html">오일스테인 가격 가이드</a><a href="/sigongbeop/">자재 시공법</a><a href="/bupum/">철물·공구·부속</a></div></section>'
                f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{fq(nm)}</section>{CTA}' + LB)
        page(url(t)[1:], f"본덱스 {nm} {len(tx)}종 — 가격·색상 | 대전 영진목재", f"본덱스 {nm} {len(tx)}가지 사진·가격·색상. {DESC.get(t, '')}. 대전 유성 영진종합목재 매장 상담·주문, 전국 배송.", body, "/jaryo/", None, IMG(tx[0][3]))
        out.append((t, nm, len(tx), tx))
    tot = sum(x[2] for x in out)
    rws = "".join(f'<h2 class="gt"><span><a href="{url(t)}" style="color:inherit;text-decoration:none">{E(nm)}</a> <small style="font-size:14px">{k}가지</small></span><small>옆으로 넘겨 보세요 ›</small></h2><div class="yrg">{"".join(card(r) for r in tx[:12])}<a class="yri ymore" href="{url(t)}"><span>{E(nm)} 전체 {k}가지 보기 ›</span></a></div>' for t, nm, k, tx in out)
    page("bondex/index.html", f"본덱스 스테인·바니쉬·페인트·오일 {tot}종 — 가격·색상 | 대전 영진목재",
         f"본덱스 오일스테인·수용성 스테인·바니쉬·페인트·원목가구 오일·도장도구 {tot}가지 사진과 가격. 대전 유성 영진종합목재 매장 상담·주문, 전국 배송.",
         f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/paint.html">페인트·스테인</a> › 본덱스</p><h1>본덱스 스테인·페인트·오일</h1><p class="glead">덴마크 본덱스 오일스테인부터 바니쉬·페인트·원목가구 오일·붓·로울러까지 {tot}가지(같은 제품은 한 번만). 사진을 누르면 색상·용량을 볼 수 있습니다.</p>{nav(None)}{rws}'
         f'<div class="glk"><a href="/gagyeok/oilstain.html">오일스테인 가격 가이드</a><a href="/jaryo/paint.html">페인트·스테인 전체</a><a href="/visit.html">매장 길찾기</a></div></section>{CTA}' + LB, "/jaryo/", None, IMG(out[0][3][0][3]))
    return out
