# -*- coding: utf-8 -*-
"""제조사 제품별 상세 페이지 — 영림·예림·쉐누·본덱스·건축자재(samik)·수입 자재(homewood)
/{dir}/p/{id}.html + 제품 목록 /{dir}/p/index.html. 가격은 본덱스만(판매가×1.3, 부가세 포함, '~'), 나머지 매장 문의.
화면에 공급 업체 이름(삼익·홈우드) 표기 금지 — 제조사 브랜드명만."""
import os, re
import prodguide as PG

TEL = "042-545-2900"
FEED = []  # 구글 머천트 센터 상품 목록(가격 있는 것만)
CATL = {}  # 분류 페이지 → [(제품 주소, 이름)] (분류 페이지에 제품별 링크 넣기)


def _ld(name, img, desc, brand, cat, price=None):
    d = {"@context": "https://schema.org", "@type": "Product", "name": name[:150], "image": img if img.startswith("http") else "https://www.wwood.co.kr" + img,
         "description": desc[:300], "category": cat}
    if brand: d["brand"] = {"@type": "Brand", "name": brand}
    if price: d["offers"] = {"@type": "Offer", "priceCurrency": "KRW", "price": str(price), "availability": "https://schema.org/InStoreOnly",
                             "seller": {"@type": "Organization", "name": "영진종합목재(월드건축자재)"}}
    return d


def _vendor(page, E, CTA, faqslide, HOURS, d, label, home, items, VID=None):
    """items: dict(id, name, img, spec[(k,v)], cat, cathref, lead, tips[], brand, price)"""
    if not items: return 0
    used, bycat, ids = set(), {}, set()
    for it in items:
        CATL.setdefault(it["cathref"], [])
        b, k = it["id"], 2
        while it["id"] in ids: it["id"] = f"{b}-{k}"; k += 1
        ids.add(it["id"])
        bycat.setdefault(it["cat"], []).append(it)
        t = it["name"]
        if t in used: t = f'{t} ({it["id"]})'
        used.add(t); it["title"] = t
        CATL[it["cathref"]].append((f"/{d}/p/{it['id']}.html", t))
    _vc = {}
    def vids(c):
        if VID is None: return ""
        if c not in _vc:
            ws = [w for w in re.split(r"[·,\s/()]+", c) if len(w) >= 2 and w not in ("기타", "부자재", "제품", "자재", "시스템", "옵션")]
            _vc[c] = VID(ws) if ws else ""
        return _vc[c]
    for it in items:
        sib = [x for x in bycat[it["cat"]] if x is not it]
        k = sib.index(next((x for x in sib if x["id"] > it["id"]), sib[0])) if sib else 0
        rel = (sib[k:] + sib[:k])[:10]
        pz = f'{it["price"]:,}원~ (부가세 포함)' if it.get("price") else "매장 문의 (규격·수량별 견적)"
        tb = "".join(f"<tr><th>{E(a)}</th><td>{E(b)}</td></tr>" for a, b in it["spec"]) + f"<tr><th>분류</th><td>{E(it['cat'])}</td></tr><tr><th>가격</th><td>{E(pz)}</td></tr>"
        use = it["lead"] or it["cat"]
        fq = [(f"{it['title']} 어디서 사나요?", f"대전 유성구 영진종합목재(월드건축자재) 매장에서 상담·주문하실 수 있고, 전국 용달 배송도 됩니다. {HOURS}."),
              (f"{it['title']} 가격은 얼마인가요?", (f"매장 기준 {pz}입니다. 색상·용량·수량에 따라 달라질 수 있습니다." if it.get("price") else f"규격·수량에 따라 달라 매장이나 전화({TEL})로 견적을 드립니다.")),
              (f"{PG._jo(it['title'], '은', '는')} 어떤 제품인가요?", use)]
        gd = PG.find(it["cat"]) or PG.find(" ".join(b for a, b in it["spec"] if a in ("세부 분류", "라인"))) or PG.find(it["name"])
        allt = (gd["how"] if gd else []) + [t for t in it["tips"] if not gd or t not in gd["how"]]
        tips = ("<h2 class='gt'>" + (E(gd["t"]) + " 고르는 법" if gd else "고를 때 확인할 점") + "</h2><ul class='gtip'>" + "".join(f"<li>{E(t)}</li>" for t in allt) + "</ul>") if allt else ""
        if gd:
            tips = f"<h2 class='gt'>{E(gd['t'])}{'은' if (ord(gd['t'][-1]) - 0xAC00) % 28 else '는'} 어디에 쓰나요</h2><p>{E(gd['use'])}</p>" + tips
            if gd["warn"]: tips += "<h2 class='gt'>주의할 점</h2><ul class='gtip'>" + "".join(f"<li>{E(w)}</li>" for w in gd["warn"]) + "</ul>"
            if gd["links"]: tips += '<div class="qk">' + "".join(f'<a href="{h}">{E(t)}</a>' for h, t in gd["links"]) + "</div>"
        itro = PG.intro(it["title"], it["cat"], it["spec"], it.get("price"))
        if it.get("price") and it["img"].startswith("http"): FEED.append((f"{d}-{it['id']}", it["title"], itro, f"/{d}/p/{it['id']}.html", it["img"], it["price"], it.get("brand"), it["cat"]))
        if allt: fq.append((f"{it['title']} 고를 때 무엇을 확인하나요?", " ".join(allt[:3])))
        body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › <a href="{home}">{E(label)}</a> › <a href="{it["cathref"]}">{E(it["cat"])}</a> › {E(it["title"][:40])}</p>'
                f'<h1>{E(it["title"])}</h1><p class="glead">{E(use)}</p><p>{E(itro)}</p>'
                f'<p><img src="{it["img"]}" alt="{E(it["title"])}" width="600" height="600" referrerpolicy="no-referrer" style="max-width:100%;height:auto;border-radius:12px;background:#fff;object-fit:contain"></p>'
                f'<div class="tw"><table class="cmp"><tbody>{tb}</tbody></table></div>'
                f'<div class="row"><a class="b d" href="tel:{TEL.replace("-", "")}">전화 문의 {TEL}</a><a class="b o" href="/jeonguk/">전국 배송 지역</a><a class="b o" href="{it["cathref"]}">{E(it["cat"])} 전체 사진</a></div>{tips}</section>'
                + (f'<section class="wrap sec gg"><h2 class="gt">같은 분류 제품</h2><ul class="mgl">' + "".join(f'<li><a href="/{d}/p/{x["id"]}.html">{E(x["name"])}</a></li>' for x in rel) + '</ul></section>' if rel else "")
                + (f'<section class="wrap sec"><h2>관련 영상 — 월드건축자재DIY</h2>{vids(it["cat"])}</section>' if vids(it["cat"]) else "")
                + f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{faqslide(fq)}</section>{CTA}')
        ld = [_ld(it["title"], it["img"], use, it.get("brand"), it["cat"], it.get("price")),
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}]
        sd = " · ".join(f"{a} {b}" for a, b in it["spec"][:2])
        page(f"{d}/p/{it['id']}.html", (f"{it['title']} 가격 {it['price']:,}원~ · 규격 | 대전 영진목재" if it.get("price") else f"{it['title']} — 사진·규격·구매 | 대전 영진목재"),
             (itro[:150] if len(itro) > 60 else f"{it['title']}: {use[:60]}. {sd[:50]} 대전 영진종합목재 상담·전국 배송.").replace("  ", " "), body, "/jaryo/", ld, it["img"] if it["img"].startswith("http") or it["img"].startswith("/") else None)
    lst = "".join(f'<h2 class="gt">{E(c)} <small>{len(xs)}가지</small></h2><ul class="mgl">' + "".join(f'<li><a href="/{d}/p/{x["id"]}.html">{E(x["title"])}</a></li>' for x in xs) + '</ul>' for c, xs in bycat.items())
    page(f"{d}/p/index.html", f"{label} 제품별 목록 {len(items)}가지 | 대전 영진목재", f"{label} {len(items)}가지 제품별 사진·규격 페이지 목록. 대전 영진종합목재 상담·전국 배송.",
         f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › <a href="{home}">{E(label)}</a> › 제품별 목록</p><h1>{E(label)} 제품별 목록 <small>{len(items)}가지</small></h1><p class="glead">제품 이름을 누르면 사진·규격과 구매 안내를 볼 수 있습니다.</p>{lst}</section>{CTA}', "/jaryo/")
    return len(items)


def gen(page, E, CTA, faqslide, HOURS, ROOT, VID=None):
    n = {}
    # 영림
    import younglim as yl
    its = []
    for r in yl.load(ROOT):
        pg = next((p for p in yl.PAGES if r[0] in p[2]), None)
        if not pg or not r[2].isdigit(): continue
        nm, im = yl.card(r)
        sty = yl.STY.get(r[5], "")
        sp = ([("모델", r[3])] if r[3] else []) + ([("스타일", sty)] if sty else []) + [("제조사", "영림")]
        its.append(dict(id=r[2], name="영림 " + nm, img=im, spec=sp, cat=pg[1], cathref=f"/younglim/{pg[0]}.html", lead=pg[3], tips=pg[4], brand="영림"))
    n["younglim"] = _vendor(page, E, CTA, faqslide, HOURS, "younglim", "영림 도어·중문·몰딩·필름", "/younglim/", its, VID)
    # 예림
    import yerim as yr
    its, seen = [], set()
    for l in open(os.path.join(ROOT, "data", "yerim.tsv"), encoding="utf-8"):
        x = l.rstrip("\n").split("|")
        if len(x) < 5 or not x[2].isdigit() or x[2] in seen: continue
        pg = next((p for p in yr.PAGES if p[4](x[0], x[1])), None)
        if not pg: continue
        seen.add(x[2]); line = yr.D3.get(x[1], "")
        sp = ([("라인", line)] if line else []) + [("제조사", "예림(YERIM)")]
        its.append(dict(id=x[2], name="예림 " + x[3], img=yr.IMG(x[4]), spec=sp, cat=pg[1], cathref=f"/yerim/{pg[0]}.html", lead=pg[3], tips=pg[5], brand="예림"))
    n["yerim"] = _vendor(page, E, CTA, faqslide, HOURS, "yerim", "예림 중문·도어·문틀", "/yerim/", its, VID)
    # 쉐누
    import shenu as sh
    its, seen = [], set()
    for r in sh.load(ROOT):
        pg = next((p for p in sh.PAGES if r[0] in p[2]), None)
        sid = re.sub(r"[^a-z0-9]+", "-", os.path.splitext(os.path.basename(r[1]))[0].lower()).strip("-")
        if not pg or not sid or sid in seen: continue
        seen.add(sid)
        sp = [("라인", sh.LINE.get(r[0], ""))] + ([("색상", r[3])] if r[3] else []) + [("제조사", "쉐누")]
        its.append(dict(id=sid, name="쉐누 " + sh.name(r), img=sh.IMG(r[1]), spec=[s for s in sp if s[1]], cat=pg[1], cathref=f"/shenu/{pg[0]}.html", lead=pg[3], tips=pg[4], brand="쉐누"))
    n["shenu"] = _vendor(page, E, CTA, faqslide, HOURS, "shenu", "쉐누 도어·중문·몰딩", "/shenu/", its, VID)
    # 본덱스(이몰링)
    import emall as em
    cats, rows = em.load(ROOT)
    def top(c):
        k = 0
        while c not in em.SLUG and c in cats and k < 6: c = cats[c][0]; k += 1
        return c if c in em.SLUG else None
    its = []
    for r in rows:
        t = top(r[0])
        if not t or not r[1].isdigit(): continue
        sub = cats.get(r[0], (0, ""))[1]
        its.append(dict(id=r[1], name=r[2], img=em.IMG(r[3]), spec=em.spec(r), cat=cats[t][1], cathref=f"/bondex/{em.SLUG[t]}.html",
                        lead=f"{sub or cats[t][1]} 제품. {em.DESC.get(t, '')}.", tips=["칠할 나무 종류·면적과 실내·외부 여부를 알려 주시면 양과 색을 같이 골라 드립니다."], brand=(re.match(r"\[?([가-힣A-Za-z]+)", r[2]) or [None, None])[1], price=r[4]))
    n["bondex"] = _vendor(page, E, CTA, faqslide, HOURS, "bondex", "본덱스 스테인·페인트·오일", "/bondex/", its, VID)
    # 목조·외장·내장 건축자재(samik) — 업체 이름 표기 금지
    import samik as sm
    its = []
    for r in sm.load(ROOT):
        if r[0] not in sm.SLUG or not r[2].isdigit(): continue
        sp = sm.spec(r)
        lead = next((b for a, b in sp if a in ("용도", "설명")), "") or f"{r[1]} 자재. {sm.DESC.get(r[0], '')}."
        its.append(dict(id=r[2], name=r[3], img=sm.IMG(r[4], r[2]), spec=sp + [("세부 분류", r[1])] if r[1] else sp, cat=r[0], cathref=f"/geonjae/{sm.SLUG[r[0]]}.html",
                        lead=lead, tips=[], brand=None))
    n["geonjae"] = _vendor(page, E, CTA, faqslide, HOURS, "geonjae", "목조·외장·내장 건축자재", "/geonjae/", its, VID)
    # 수입 목조주택 자재·창호(homewood) — 업체 이름 표기 금지
    import homewood as hw
    its = []
    for r in hw.load(ROOT):
        g = hw.GN[r["g"]]
        sid = re.sub(r"[^a-z0-9-]+", "-", r["s"].lower()).strip("-")[:80]
        its.append(dict(id=sid, name=r["n"], img=hw.img(r["i"], True), spec=[("세부 분류", r["sub"])], cat=r["g"], cathref=f"/suip/{g[1]}.html",
                        lead=f"{r['sub']} — 수입 목조주택 자재. {g[2]}.", tips=["규격·수량과 현장 위치를 알려 주시면 견적과 배송 일정을 안내해 드립니다."], brand=None))
    n["suip"] = _vendor(page, E, CTA, faqslide, HOURS, "suip", "수입 목조주택 자재·창호", "/suip/", its, VID)
    # 철물·공구·부속(철물박사) — 가격 = 판매가 × 1.4(부가세 포함, '~')
    import cmbs as cb
    cats, rows = cb.load(ROOT)
    DET = cb.load_det(ROOT)
    def ctop(c):
        k = 0
        while c in cats and cats[c][0] != 1 and k < 8: c = cats[c][0]; k += 1
        return c
    curl = lambda c: f"/bupum/{cb.TOP[c][0]}.html" if c in cb.TOP else f"/bupum/{cb.TOP[ctop(c)][0]}-{c}.html"
    its, seen = [], set()
    for r in rows:
        t = ctop(r[0])
        if t not in cb.TOP or t == 55 or r[0] not in cats or not r[1].isdigit() or r[1] in seen: continue
        seen.add(r[1])
        par = cats[r[0]][0]
        cn = cats[r[0]][1] if (par in cb.TOP or par not in cats) else f"{cats[par][1]} {cats[r[0]][1]}"
        its.append(dict(id=r[1], name=r[2], img=cb.IMG(r[3]), spec=cb.spec(r[5], DET.get(r[1])) or [], cat=cn, cathref=(cb.catlink(ROOT, r[0]) or curl(r[0])).split("#")[0] if (cb.catlink(ROOT, r[0]) or "").split("#")[0] else curl(r[0]),
                        lead=f"{cn} — {cb.TOP[t][1]}({cb.TOP[t][2]}).", tips=["쓰던 부품이나 사진을 가져오시면 맞는 규격을 찾기 쉽습니다.", "목재·합판과 같이 주문하시면 한 번에 실어 보내 드립니다."], brand=None, price=r[4]))
    n["bupum"] = _vendor(page, E, CTA, faqslide, HOURS, "bupum", "철물·공구·부속", "/bupum/", its, VID)
    # 제일타카(JITOOL) 타카·콤프레셔 — 제조사 규격(가격은 매장 문의, 기준가와 섞지 않음)
    import taka_data as TD, taka as TK
    its = []
    for key, (gname, glead, models) in TD.TOOLS.items():
        for m, kind, pin, wt, use, im, im2, dsc in models:
            sid = re.sub(r"[^a-z0-9]+", "-", m.lower()).strip("-")
            its.append(dict(id=sid, name=f"제일타카 {m} {kind}", img=TK.IMG(im), spec=[("모델", m), ("종류", kind), ("사용 핀", pin), ("무게", wt), ("쓰는 곳", use), ("제조사", "제일타카(JITOOL)")],
                            cat=gname, cathref=f"/taka/{key}.html", lead=dsc, tips=["쓸 핀 규격(4단위·F핀·T핀·실핀 등)과 고정할 재료 두께를 먼저 정하세요.", "에어타카는 콤프레셔·에어호스가 함께 필요합니다."], brand="제일타카"))
    for m, t, mo, tk, q, w, im in TD.COMP:
        sid = "comp-" + re.sub(r"[^a-z0-9]+", "-", m.lower()).strip("-")
        its.append(dict(id=sid, name=f"제일타카 콤프레셔 {m}", img=TK.IMG(im), spec=[("모델", m), ("방식", t), ("모터", mo), ("탱크", tk), ("토출량", f"{q}L/min"), ("무게", f"{w}kg"), ("제조사", "제일타카(JITOOL)")],
                        cat="콤프레셔", cathref="/taka/compressor.html", lead=f"{t} {mo} {tk} 콤프레셔. 에어타카·에어공구에 공기를 공급합니다.", tips=["타카 한두 대는 소형 오일리스, 여러 대·프레이밍 타카는 큰 탱크가 편합니다.", "실내 작업은 저소음 오일리스형이 좋습니다."], brand="제일타카"))
    n["taka"] = _vendor(page, E, CTA, faqslide, HOURS, "taka", "제일타카 타카·콤프레셔", "/taka/", its, VID)
    # 니치하 세라믹 사이딩 — 품번별(가격은 매장 문의, 기준가는 /nichiha/ 참고)
    import nichiha as NH
    VN = {v[0]: (v[1], v[2]) for v in NH.VIS}
    its = []
    for r in NH.load(ROOT):
        if len(r) < 4: continue
        v, code, fl, img = r[:4]
        vn, vd = VN.get(v, ("", ""))
        sp = [("품번", code), ("무늬", vn)] + list(NH.SPEC) + ([("표면", "니치가드(NG) — 오염이 덜 붙는 표면 처리")] if fl == "NG" else []) + [("제조사", "니치하(NICHIHA, 일본)")]
        its.append(dict(id=re.sub(r"[^a-z0-9]+", "-", code.lower()).strip("-"), name=f"니치하 세라믹 사이딩 {code}", img=NH.BIG(img), spec=sp, cat=f"니치하 {vn}" if vn else "니치하 세라믹 사이딩",
                        cathref="/nichiha/", lead=f"{vd}. 길이 3,030mm EX 시리즈 세라믹 사이딩입니다." if vd else "길이 3,030mm EX 시리즈 세라믹 사이딩입니다.", tips=[], brand="니치하"))
    n["nichiha"] = _vendor(page, E, CTA, faqslide, HOURS, "nichiha", "니치하 세라믹 사이딩", "/nichiha/", its, VID)
    return n


def inject(OUT, E):
    """분류(사진 목록) 페이지 아래에 제품별 상세 페이지 링크 목록을 넣음(내부 링크)."""
    n = 0
    for href, lst in CATL.items():
        fp = os.path.join(OUT, href.lstrip("/") + ("index.html" if href.endswith("/") else ""))
        if not os.path.exists(fp) or not lst: continue
        h = open(fp, encoding="utf-8").read()
        if "제품별 자세히 보기</h2>" in h: continue
        sec = ('<section class="wrap sec gg"><h2 class="gt">제품별 자세히 보기</h2><ul class="mgl">' +
               "".join(f'<li><a href="{u}">{E(t)}</a></li>' for u, t in lst[:400]) + '</ul></section>')
        i = h.find('<section class="cta">')
        h = h[:i] + sec + h[i:] if i > 0 else h.replace("</main>", sec + "</main>", 1)
        open(fp, "w", encoding="utf-8").write(h); n += 1
    return n
