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
    n = re.sub(r"^\[[^\]]*\]\s*(?:\([A-Z]+\))?\s*※?\s*", "", n)
    n = re.sub(r"\[[^\]]*할인[^\]]*\]|\[[^\]]*특가[^\]]*\]", "", n)
    n = re.sub(r"/?옵션선택/?", "/", n)
    n = re.sub(r"\s*/\s*", " · ", n).strip(" ·")
    return re.sub(r"\s+", " ", n)


def price(v):  # 철물박사 판매가 × 1.4, 100원 단위 올림
    try: n = int(v)
    except Exception: return 0
    return 0 if n <= 0 else -(-int(n * 1.4 + 0.5) // 100) * 100


def load(ROOT):
    d = os.path.join(ROOT, "data")
    pc, pr = os.path.join(d, "cmbs_cats.tsv"), os.path.join(d, "cmbs.tsv")
    if not (os.path.exists(pc) and os.path.exists(pr)): return {}, []
    cats = {}
    for l in open(pc, encoding="utf-8"):
        x = l.rstrip("\n").split("|")
        if len(x) >= 3: cats[int(x[0])] = (int(x[1]), x[2])
    bp = os.path.join(d, "cmbs_block.txt")
    block = set(open(bp).read().split()) if os.path.exists(bp) else set()  # 다른 회사 워터마크 사진 상품은 뺌
    rows = []
    for l in open(pr, encoding="utf-8"):
        x = l.rstrip("\n").split("|")
        if len(x) >= 4 and x[0].isdigit() and x[1] not in block: rows.append((int(x[0]), x[1], nice(x[2]), x[3], (price(x[4]) if len(x) > 4 else None), x[2]))
    seen = {}
    for i, r in enumerate(rows):  # 같은 상품번호가 두 줄이면 가격 있는 줄만
        if r[1] not in seen or (rows[seen[r[1]]][4] is None and r[4] is not None): seen[r[1]] = i
    rows = [r for i, r in enumerate(rows) if seen[r[1]] == i]
    return cats, rows


U = r"(?:A|mm|㎜|cm|CM|M|m|T|t|파이|Φ|인치|L|ml|ML|kg|KG|g|W|V|구|평|자|ah|Ah|\"|')"
SZ = re.compile(r"[\d.,]*\d\s*" + U + r"(?:\s*[~\-]\s*[\d.,]+\s*" + U + r"?)?|[\d.,]+\s*[~\-]\s*[\d.,]+\s*" + U + r"|[\d.]+\s*[xX×*]\s*[\d.]+(?:\s*[xX×*]\s*[\d.]+)?\s*" + U + r"?")
QT = re.compile(r"\d+\s*(?:개입|개|EA|ea|매|롤|봉|박스|족|조|입|pcs|PCS|세트|SET|set|장)|소포장|봉단위|박스단위|낱개|조당|봉|SET|세트")


CL = re.compile(r"(?:흑색|백색|검정|블랙|화이트|아이보리|골드|금색|실버|은색|크롬|흑니켈|니켈|브론즈|엔틱|앤틱|스텐|스텐레스|신주|황동|아연|알루미늄|AL|핑크|그린|블루|레드|빨강|노랑|옐로우|회색|그레이|다크그레이|투명|우드|월넛|오크|무광|유광|PB|SST|SSS)")
PRE = re.compile(r"^\[[^\]]*\]\s*(?:\([A-Z]+\))?\s*※?\s*")


def toks(raw):
    raw = PRE.sub("", raw)
    m = re.match(r"^(.*?)\((.*)\)\s*$", raw)
    if m and "/" not in m.group(1):
        return [m.group(1).strip()] + re.split(r"[/,]", m.group(2))
    return raw.split("/")


def spec(raw, det):
    """사진 크게 보기에 넣을 규격 줄: (라벨, 값) 목록"""
    tk = [t.strip() for t in toks(raw) if t.strip() and t.strip() not in ("옵션선택", "규격선택", "사이즈선택", "용량선택", "색상선택")]
    out = []
    sz = [t for t in tk[1:] if SZ.fullmatch(t) or t in ("대", "중", "소", "특대", "대형", "중형", "소형", "미니", "대,소", "대,중,소")]
    qt = [t for t in tk if QT.fullmatch(t)]
    if sz: out.append(("규격", " · ".join(sz)))
    if qt: out.append(("수량·포장", " · ".join(qt)))
    cl = [t for t in tk[1:] if CL.fullmatch(t)]
    if cl: out.append(("색상·재질", " · ".join(cl)))
    if det:
        op = [o for o in det[0].split(";") if o]
        if op:
            def cv(o):  # 옵션 추가금도 같은 방식(×1.4, 100원 올림)
                return re.sub(r"\(\s*([+-])\s*([\d,]+)\s*원\s*\)", lambda m: f"({m.group(1)}{price(m.group(2).replace(',', '')):,}원)", o)
            out.append(("선택 옵션", " · ".join(cv(o) for o in op[:16]) + (f" 외 {len(op) - 16}가지" if len(op) > 16 else "")))
        if det[1] and det[1] not in ("기타", "상세설명참조"): out.append(("원산지", det[1]))
        if len(det[2]) >= 15: out.append(("설명", det[2][:160] + ("…" if len(det[2]) > 160 else "")))
    return out


def load_det(ROOT):
    p = os.path.join(ROOT, "data", "cmbs_detail.tsv")
    d = {}
    if os.path.exists(p):
        for l in open(p, encoding="utf-8"):
            x = l.rstrip("\n").split("|")
            if len(x) >= 4: d[x[0]] = x[1:4]
    return d


def gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT):
    cats, rows = load(ROOT)
    if not rows: return []
    DET = load_det(ROOT)
    def sp(r):
        x = spec(r[5], DET.get(r[1]))
        return ("\n".join(f"{a}\t{b}" for a, b in x)) if x else ""
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
    card = lambda r, pre="": f'<a class="yri" href="#" data-big="{IMG(r[3])}" data-n="{E(r[2])}"{(' data-sp="' + E(sp(r)) + '"') if sp(r) else ''}><img loading="lazy" decoding="async" referrerpolicy="no-referrer" width="300" height="300" src="{IMG(r[3])}" alt="{E(pre + r[2])}"><span>{E(r[2])}</span>{"" if r[4] is None else (f'<em class="cbp">{r[4]:,}원~ <small>부가세 포함</small></em>' if r[4] else '<em class="cbp q">매장 문의</em>')}</a>'
    topnav = lambda cur: '<div class="glk tkn">' + "".join(f'<a href="{url(t)}"{" class=on" if t == cur else ""}>{E(TOP[t][1])}</a>' for t in TOP if items(t)) + '</div>'
    note = ''
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
                    sec += f'<h2 class="gt" id="c{l}"><span>{(f'<a href="{url(l)}" style="color:inherit;text-decoration:none">' + E(cats[l][1]) + '</a>') if len(ls) > CAP else E(cats[l][1])} <small style="font-size:14px">{len(ls)}가지</small></span><small>옆으로 넘겨 보세요 ›</small></h2><div class="yrg">{"".join(card(r, cats[l][1] + " ") for r in ls[:CAP])}{more}</div>'
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
