# 철물박사(철물박사.com — 회사 허락) 철물·공구·욕실·전기·안전·피스볼트·생활·사무용품 사진 카탈로그 — /bupum/
# 데이터: src/data/cmbs.tsv (분류번호|상품번호|이름|이미지경로), src/data/cmbs_cats.tsv (분류번호|상위|이름)
#   .github/scripts/fetch_cmbs.py 가 매일 갱신(vendors.yml). 가격은 넣지 않음(매장 문의).
import os, re
from yerim import LB

IMG = lambda p: "https://m.xn--392bopf4iwtp.com/web/product/medium/" + p
TOP = {48: ("cheolmul", "철물·부속", "손잡이·경첩·도어부속·가구부속·목조주택 철물·선반·진열 부속"),
       49: ("gongu", "공구", "수작업·측정·안전·전동공구와 실리콘·폼·테이프·접착제"),
       50: ("yoksil", "욕실·주방 부속", "수전·배수구·환기구·변기부속·샤워부스·욕실 악세사리"),
       51: ("jeongi", "전기·조명", "콘센트·스위치·차단기·멀티탭·조명·전선몰딩"),
       52: ("anjeon", "안전용품", "논슬립·모서리보호대·핸드레일·주차·소방·보양재"),
       53: ("piseu", "피스·볼트·앙카", "목공용·직결·스텐 피스, 칼블럭·앙카, 볼트·너트"),
       54: ("saenghwal", "생활용품", "방충망·보수제·자동차·캠핑·생활 용품"),
       55: ("samu", "사무용품", "복사용지·사무기기·필기구·화일·청소 용품")}
CAP = 24


def nice(n):
    n = re.sub(r"\[[^\]]*할인[^\]]*\]|\[[^\]]*특가[^\]]*\]", "", n)
    n = re.sub(r"/?옵션선택/?", "/", n)
    n = re.sub(r"\s*/\s*", " · ", n).strip(" ·")
    return re.sub(r"\s+", " ", n)


def load(ROOT):
    d = os.path.join(ROOT, "data")
    pc, pr = os.path.join(d, "cmbs_cats.tsv"), os.path.join(d, "cmbs.tsv")
    if not (os.path.exists(pc) and os.path.exists(pr)): return {}, []
    cats = {}
    for l in open(pc, encoding="utf-8"):
        x = l.rstrip("\n").split("|")
        if len(x) >= 3: cats[int(x[0])] = (int(x[1]), x[2])
    rows = []
    for l in open(pr, encoding="utf-8"):
        x = l.rstrip("\n").split("|")
        if len(x) >= 4 and x[0].isdigit(): rows.append((int(x[0]), x[1], nice(x[2]), x[3]))
    return cats, rows


def gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT):
    cats, rows = load(ROOT)
    if not rows: return []
    kids = {}
    for n, (p, _) in cats.items(): kids.setdefault(p, []).append(n)
    by = {}
    for r in rows: by.setdefault(r[0], []).append(r)
    def items(n):  # 하위 분류 포함
        out = list(by.get(n, []))
        for k in kids.get(n, []): out += items(k)
        return out
    def top_of(n):
        while n in cats and cats[n][0] != 1: n = cats[n][0]
        return n
    url = lambda n: f"/bupum/{TOP[n][0]}.html" if n in TOP else f"/bupum/{TOP[top_of(n)][0]}-{n}.html"
    card = lambda r, pre="": f'<a class="yri" href="#" data-big="{IMG(r[3])}" data-n="{E(r[2])}"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" width="300" height="300" src="{IMG(r[3])}" alt="{E(pre + r[2])}"><span>{E(r[2])}</span></a>'
    topnav = lambda cur: '<div class="glk tkn">' + "".join(f'<a href="{url(t)}"{" class=on" if t == cur else ""}>{E(TOP[t][1])}</a>' for t in TOP if items(t)) + '</div>'
    note = '<p class="gs">사진은 철물박사(철물박사.com)에서 허락받아 싣습니다. 사진을 누르면 크게 볼 수 있습니다. 매장 재고·가격·주문 가능 여부는 전화나 매장에서 확인해 주세요. 없는 품목은 비슷한 제품을 찾아 드립니다.</p>'
    def fq(nm):
        return faqslide([(f"{nm} 어디서 사나요?", f"{ADDR} 영진종합목재(월드건축자재) 매장에서 상담·주문할 수 있습니다. {HOURS}. 사진이나 쓰던 부품을 가져오시면 맞는 규격을 찾기 쉽습니다."),
                         (f"{nm} 가격은 얼마인가요?", "품목·수량·재고에 따라 달라서 매장이나 전화로 안내해 드립니다. 목재·합판과 같이 사시면 한 번에 실어 드립니다(전국 용달 배송 가능).")])
    out = []
    def grid_page(n, tn):
        xs = items(n)
        par = cats[n][0]
        nm = cats[n][1] if par in TOP else f"{cats[par][1]} {cats[n][1]}"
        crumb = f'<a href="/bupum/">철물·공구·부속</a> › <a href="{url(tn)}">{E(TOP[tn][1])}</a>' + (f' › <a href="{url(par)}">{E(cats[par][1])}</a>' if par not in TOP else "")
        body = (f'<section class="wrap sec gg"><p class="crumb">{crumb} › {E(cats[n][1])}</p><h1>{E(nm)} <small>{len(xs)}가지</small></h1>{topnav(tn)}'
                f'<div class="yrg cbg">{"".join(card(r, nm + " ") for r in xs)}</div>{note}</section>'
                f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{fq(nm)}</section>{CTA}' + LB)
        page(url(n)[1:], f"{nm} {len(xs)}종 사진 — 철물·공구·부속 | 대전 영진목재", f"{nm} {len(xs)}가지 제품 사진. 대전 유성 영진종합목재 매장 상담·주문, 전국 용달 배송.", body, "/jaryo/", None, IMG(xs[0][3]))
    for t in TOP:
        if t not in cats or not items(t): continue
        mids = [m for m in kids.get(t, []) if items(m)]
        tsec = ""
        for m in mids:
            leaves = [l for l in kids.get(m, []) if items(l)]
            xs = items(m)
            if leaves:  # 중분류 페이지: 소분류별 한 줄
                sec = ""
                for l in leaves:
                    ls = items(l)
                    more = f'<a class="yri ymore" href="{url(l)}"><span>전체 {len(ls)}가지 보기 ›</span></a>' if len(ls) > CAP else ""
                    sec += f'<h2 class="gt" id="c{l}"><a href="{url(l)}" style="color:inherit;text-decoration:none">{E(cats[l][1])}</a> {len(ls)}가지 <small>옆으로 넘겨 보세요 ›</small></h2><div class="yrg">{"".join(card(r, cats[l][1] + " ") for r in ls[:CAP])}{more}</div>'
                    if len(ls) > CAP: grid_page(l, t)
                chips = '<div class="qk">' + "".join(f'<a href="#c{l}">{E(cats[l][1])}</a>' for l in leaves) + '</div>'
                nm = cats[m][1]
                body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/bupum/">철물·공구·부속</a> › <a href="{url(t)}">{E(TOP[t][1])}</a> › {E(nm)}</p><h1>{E(nm)} <small>{len(xs)}가지</small></h1>{topnav(t)}{chips}{sec}{note}</section>'
                        f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{fq(nm)}</section>{CTA}' + LB)
                page(url(m)[1:], f"{nm} {len(xs)}종 — " + ", ".join(cats[l][1] for l in leaves[:4]) + " | 대전 영진목재",
                     f"{nm} {len(xs)}가지 사진: " + ", ".join(cats[l][1] for l in leaves[:8]) + ". 대전 유성 영진종합목재 매장 상담·주문.", body, "/jaryo/", None, IMG(xs[0][3]))
            else:
                grid_page(m, t)
            tsec += f'<a class="gi gim" href="{url(m)}"><img loading="lazy" referrerpolicy="no-referrer" src="{IMG(xs[0][3])}" alt=""><b>{E(cats[m][1])} <small>{len(xs)}가지</small></b></a>'
        tx = items(t)
        tn = TOP[t][1]
        body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/bupum/">철물·공구·부속</a> › {E(tn)}</p><h1>{E(tn)} <small>{len(tx)}가지</small></h1><p class="glead">{E(TOP[t][2])}.</p>{topnav(t)}<div class="gig">{tsec}</div>{note}</section>{CTA}')
        page(url(t)[1:], f"{tn} {len(tx)}종 사진 — {TOP[t][2][:30]} | 대전 영진목재", f"{tn} {len(tx)}가지: {TOP[t][2]}. 대전 유성 영진종합목재 매장 상담·주문, 전국 용달 배송.", body, "/jaryo/", None, IMG(tx[0][3]))
        out.append((t, tn, TOP[t][2], len(tx), IMG(tx[0][3])))
    tot = sum(x[3] for x in out)
    cards = "".join(f'<a class="gi gim" href="{url(t)}"><img loading="lazy" referrerpolicy="no-referrer" src="{im}" alt=""><b>{E(n)} <small>{k}가지</small></b><small>{E(d[:36])}</small></a>' for t, n, d, k, im in out)
    page("bupum/index.html", f"철물·공구·욕실·전기 부속 {tot}종 사진 | 대전 영진목재",
         f"손잡이·경첩·도어부속·공구·수전·배수구·콘센트·피스·앙카 등 {tot}가지 사진. 대전 유성 영진종합목재 매장 상담·주문, 전국 용달 배송.",
         f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › 철물·공구·부속</p><h1>철물·공구·부속</h1><p class="glead">문 손잡이·경첩부터 공구·욕실 수전·전기 부품·피스·앙카까지 {tot}가지를 종류별로 모았습니다(같은 제품은 한 번만).</p><div class="gig">{cards}</div>{note}<div class="glk"><a href="/cheolmul/">목재 철물(데크·정자·목조주택)</a><a href="/taka/">타카·타카핀</a><a href="/visit.html">매장 길찾기</a></div></section>{CTA}', "/jaryo/")
    return out
