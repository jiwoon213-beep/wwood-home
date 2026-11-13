# 타카·타카핀·콤프레셔 (제일타카 JITOOL 취급 제품) — /taka/
import re
from urllib.parse import quote
from taka_data import TOOLS, PINS, NAILS, ETC, COMP

IMG = lambda f: "https://www.jitool.com/upload/prod/thumb_l/" + quote(f) if f else ""
ORDER = ["battery", "interior", "concrete", "coil", "framing", "special"]
PG = {  # slug: (짧은 이름, 검색 제목 꼬리)
    "battery": ("배터리 타카", "무선 충전 타카 BF30·B635 규격"),
    "interior": ("인테리어 에어타카", "422·F30·630R·1022·T핀 타카 규격과 용도"),
    "concrete": ("콘크리트 타카", "CT64RS·ST25R·CS26 콘크리트 타카와 핀"),
    "coil": ("코일 타카", "파렛트·포장용 JCN55·JCN70·JCN80 코일 네일러"),
    "framing": ("목조주택 타카", "FN21/90 프레이밍 네일러·철물 타카"),
    "special": ("특수 타카", "데크 각관·사이딩·보온핀·칼블럭·못빼기·C링"),
    "pin": ("타카핀 규격표", "422·F30·T·DT·ST·실핀 규격과 맞는 타카"),
    "nail": ("코일못·스틱네일·보온핀", "코일못 플랫·돔, FAP·루핑못, 보온핀, 호그링"),
    "compressor": ("콤프레셔", "제일타카 벨트식·오일리스 저소음 콤프레셔 규격"),
    "etc": ("에어호스·타카 오일·소모품", "우레탄 호스·코일 호스·타카 오일·에어건"),
}
FAQ = {
    "battery": [("배터리 타카와 에어타카 차이는?", "배터리 타카는 콤프레셔·호스 없이 바로 쓰여 이동이 잦은 현장·셀프 인테리어에 편합니다. 연속 작업량이 많으면 에어타카가 가볍고 빠릅니다."),
                ("BF30/422는 핀 두 종류를 다 쓰나요?", "네. F단위 일자핀(10~30mm)과 4단위 ㄷ자핀(10~22mm)을 한 대로 씁니다. 배터리는 별도입니다.")],
    "interior": [("인테리어 타카는 뭘 사야 하나요?", "합판·석고는 422(ㄷ자), 몰딩·목천장은 F30(일자), 못자국 없는 마감은 630R(실핀)이 기본입니다. 각재 접합은 T핀 타카(BN16 시리즈)를 씁니다."),
                 ("F30과 1850A 차이는?", "같은 F핀을 쓰지만 F30은 30mm까지, 1850A는 50mm까지 씁니다. 1850A가 조금 크고 무겁습니다.")],
    "concrete": [("콘크리트에 타카핀을 바로 박을 수 있나요?", "ST25R에 ST18·ST25 핀, CS 타카에 25mm 이하 CS핀만 직접 박힙니다. 그보다 긴 핀은 반드시 목재를 대고 쏘세요."),
                 ("CT64RS는 어떤 핀을 쓰나요?", "목재용 DT핀(30~64mm)과 콘크리트용 ST핀(18~64mm)을 씁니다. ST핀은 목재를 대고 콘크리트에 고정합니다.")],
    "coil": [("코일못 플랫과 돔 차이는?", "못이 감긴 모양 차이입니다. 플랫은 평평하고 돔은 가운데가 솟아 있습니다. 타카에 맞는 타입을 쓰면 작업 차이는 없습니다."),
             ("파렛트 작업에는 어떤 코일 타카?", "일반 파렛트는 JCN55(25~57mm), 두꺼운 목재는 JCN70·JCN80, 100mm 못은 JN100C입니다.")],
    "framing": [("장선걸이 같은 철물에 못을 타카로 박을 수 있나요?", "JMCN150 메탈 커넥터 네일러가 철물 구멍에 맞춰 못을 박는 전용 타카입니다."),
                ("목조주택 골조 못은?", "FN21/90 프레이밍 네일러로 스틱네일 50~90mm를 씁니다. 녹이 걱정되면 용융아연도금(HDG) 못을 고르세요.")],
    "special": [("데크를 아연 각관 위에 바로 고정하는 타카가 있나요?", "JN65D 데크 코일 네일러가 2mm 이하 강철·2.9mm 이하 아연 각관 위에 데크재를 바로 고정합니다."),
                ("단열재 보온핀은 어떤 타카로?", "IN100(~100mm)·IN160(~160mm)·IN220(~220mm) 단발 보온핀 타카를 씁니다. 천장에는 보온핀을 쓰지 마세요.")],
    "pin": [("422핀과 F30핀 차이는?", "422는 ㄷ자(폭 4mm) 스테이플로 합판·석고 고정용, F30은 일자 브래드핀으로 몰딩·목천장용입니다. 타카도 각각 다릅니다."),
            ("실핀(6단위)은 언제 쓰나요?", "머리가 없는 아주 얇은 핀이라 못자국이 거의 안 남습니다. 몰딩·가구 마감에 씁니다(630R·640S·B635)."),
            ("타카핀 녹 방지는?", "422·F30·실핀(618·622·625·630)은 스테인리스 핀이 따로 있습니다. 욕실·사우나에 쓰세요.")],
    "nail": [("보온핀 길이는 어떻게 고르나요?", "단열재 두께 + 콘크리트에 박힐 길이(약 20~30mm)를 더해 고릅니다. IN30~IN220까지 있습니다."),
             ("스틱네일 도금 차이는?", "용융아연도금(HDG)이 가장 녹에 강하고, 전기도금(EG), 무도금(BRT) 순입니다.")],
    "compressor": [("타카용 콤프레셔는 몇 마력?", "422·F30 등 인테리어 타카 1~2대는 2마력 오일리스(25~40L)로 충분합니다. 여러 대·코일 타카·도장은 3.5~6.5마력 벨트식을 권합니다."),
                   ("오일리스 저소음 콤프레셔 장점은?", "오일 관리가 필요 없고 조용해서 실내·아파트 인테리어 현장에 좋습니다.")],
    "etc": [("에어타카에 아무 오일이나 넣어도 되나요?", "안 됩니다. 에어타카 전용 오일만 쓰세요. 작업 전 에어 플러그에 1~2초 넣어 주면 됩니다."),
            ("에어호스 굵기는?", "타카 1대는 Ø8, 길게 빼거나 여러 대 쓰면 Ø10을 권합니다.")],
}


def _price_map(P):
    m = {}
    for p in P:
        n = p["name"]
        if not n.startswith("타카"):
            continue
        k = re.sub(r"^타카-\s*", "", n)
        k = k.replace("실핀", "").replace("(=ND", " (=ND")
        k = re.sub(r"\s*\(=ND\d+\)", "", k).replace("-", "").replace("422J", "422").strip()
        m[k] = p["price"]
    return m


def gen(page, P, E, CTA, faqslide, BASE, ADDR, HOURS, ALLFAQ=None):
    PM = _price_map(P)
    nav = lambda cur: '<div class="glk tkn">' + "".join(f'<a href="/taka/{s}.html"{" class=on" if s == cur else ""}>{E(PG[s][0])}</a>' for s in ORDER + ["pin", "nail", "compressor", "etc"]) + '</div>'
    where = lambda nm: [(f"{nm} 어디서 사나요?", f"{ADDR} 영진종합목재(월드건축자재) 매장에서 실물을 보고 살 수 있습니다. {HOURS}. 목재·합판과 함께 한 번에 준비해 드립니다. 재고는 전화로 확인해 주세요.")]
    out = []

    def finish(slug, h1, lead, body, img):
        nm, tail = PG[slug]
        fq = FAQ.get(slug, [])
        full = (f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › <a href="/taka/">타카·타카핀·콤프레셔</a> › {E(nm)}</p><h1>{E(h1)}</h1><p class="glead">{E(lead)}</p>{nav(slug)}{body}'
                f'<p class="gs">제일타카(JITOOL) 제품입니다. 사진·규격은 제조사 자료 기준이며, 재고와 가격은 매장에 문의해 주세요.</p></section>'
                f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{faqslide(fq + where(nm))}</section>{CTA}')
        ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}] if fq else None
        if ALLFAQ is not None and fq: ALLFAQ.append(("타카·콤프레셔", fq, f"/taka/{slug}.html", nm))
        page(f"taka/{slug}.html", f"{nm} — {tail} | 대전 영진목재", f"{lead} 대전 유성 영진종합목재(월드건축자재) 매장 취급.", full, "/jaryo/", ld, img)
        out.append((slug, nm, tail, img))

    for slug in ORDER:
        h1, lead, items = TOOLS[slug]
        cards = "".join(
            f'<div class="gc tk"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" src="{IMG(im)}" alt="제일타카 {E(m)} {E(sub)}">'
            f'<div class="gn">{E(m)}</div><p class="tks">{E(sub)}</p><ul><li><span>사용핀</span><b>{E(pin)}</b></li><li><span>무게</span><b>{E(w)}</b></li><li><span>쓰는 곳</span><b>{E(use)}</b></li></ul><p class="tkd">{E(d)}</p></div>'
            for m, sub, pin, w, use, im, im2, d in items)
        tbl = ('<div class="tw"><table class="rt"><thead><tr><th>모델</th><th>구분</th><th>사용핀</th><th>무게</th><th>쓰는 곳</th></tr></thead><tbody>'
               + "".join(f'<tr><td><b>{E(m)}</b></td><td>{E(sub)}</td><td>{E(pin)}</td><td>{E(w)}</td><td>{E(use)}</td></tr>' for m, sub, pin, w, use, *_ in items) + '</tbody></table></div>')
        body = (f'<h2 class="gt">{E(h1)} {len(items)}가지 <small>옆으로 넘겨 보세요 ›</small></h2><div class="gcs">{cards}</div>'
                f'<h2 class="gt">한눈에 비교</h2>{tbl}<div class="glk"><a href="/taka/pin.html">맞는 타카핀 규격표 ›</a><a href="/taka/compressor.html">콤프레셔 고르기 ›</a></div>')
        finish(slug, h1, f"{h1} — {lead}. 모델별 사용핀·무게·쓰는 곳을 정리했습니다.", body, IMG(items[0][5]))

    # 타카핀
    secs = []
    for nm, kind, im, fit, use, warn, rows in PINS:
        aid = re.sub(r"\W", "", nm.split(" ")[0])
        trs = "".join(f'<tr><td><b>{E(code)}</b></td><td>{ln}mm</td><td>{pcs}발</td></tr>' for code, ln, pcs in rows)
        secs.append(f'<div class="tkp" id="{aid}"><img loading="lazy" referrerpolicy="no-referrer" src="{IMG(im)}" alt="{E(nm)} 타카핀"><div><h3>{E(nm)}</h3><p class="tks">{E(kind)}</p>'
                    f'<p><b>맞는 타카</b> {E(fit)}<br><b>쓰는 곳</b> {E(use)}</p>{f"<p class=tkw>※ {E(warn)}</p>" if warn else ""}'
                    f'<div class="tw"><table class="rt tkt"><thead><tr><th>품번</th><th>길이</th><th>1갑 수량</th></tr></thead><tbody>{trs}</tbody></table></div></div></div>')

    _pp = [p for p in P if p["name"].startswith("타카")]
    pbox = ('<h2 class="gt">매장 타카핀 소매 기준가</h2><div class="qk">' + "".join(f'<a href="/price.html">{E(re.sub(r"^타카-\s*", "", p["name"]))} <b>{p["price"]:,}원</b></a>' for p in sorted(_pp, key=lambda p: p["name"])) + '</div><p class="gs">매장 판매 단위 기준 소매 기준가(부가세 별도)입니다. 브랜드·포장 수량은 재고에 따라 다를 수 있어 위 제조사 규격표의 갑당 수량과 다를 수 있습니다.</p>') if _pp else ""
    chips = '<div class="qk">' + "".join(f'<a href="#{re.sub(chr(92)+"W", "", n.split(" ")[0])}">{E(n.split(" (")[0])}</a>' for n, *_ in PINS) + '</div>'
    body = (f'<h2 class="gt">핀 종류 {len(PINS)}가지</h2>{chips}{"".join(secs)}{pbox}'
            '<h2 class="gt">핀 고르는 순서</h2><ul class="gtip"><li>① 타카 모델을 확인하세요 — 타카마다 쓰는 핀 단위가 정해져 있습니다.</li><li>② 길이는 붙일 자재 두께의 2~2.5배가 기본입니다(합판 9mm → 19~22mm).</li><li>③ 습기 있는 곳은 스텐 핀, 콘크리트는 ST·CS·FST 핀을 쓰세요.</li></ul>')
    finish("pin", "타카핀 규격표", "422·F핀·T핀·DT핀·ST 콘크리트핀·실핀 등 타카핀 15가지의 품번·길이·갑당 수량과 맞는 타카", body, IMG("4단위.jpg"))

    cards = "".join(f'<div class="gc tk"><img loading="lazy" referrerpolicy="no-referrer" src="{IMG(im)}" alt="{E(n)}"><div class="gn">{E(n)}</div><ul><li><span>맞는 타카</span><b>{E(fit)}</b></li><li><span>쓰는 곳</span><b>{E(use)}</b></li></ul><p class="tkd">{E(note)}</p></div>' for n, _, fit, use, note, im in NAILS)
    finish("nail", "코일못·스틱네일·보온핀·호그링", "코일 타카·프레이밍 타카·보온핀 타카·C링 타카에 쓰는 못 종류", f'<h2 class="gt">못 종류 {len(NAILS)}가지 <small>옆으로 넘겨 보세요 ›</small></h2><div class="gcs">{cards}</div><div class="glk"><a href="/taka/coil.html">코일 타카 ›</a><a href="/taka/special.html">보온핀·C링 타카 ›</a></div>', IMG(NAILS[0][5]))

    def ctab(rows):
        return ('<div class="tw"><table class="rt"><thead><tr><th>모델</th><th>형식</th><th>모터</th><th>탱크</th><th>토출량</th><th>무게</th></tr></thead><tbody>'
                + "".join(f'<tr><td><b>{E(m)}</b></td><td>{E(t)}</td><td>{E(mo)}</td><td>{E(tk)}</td><td>{q}L/min</td><td>{w}kg</td></tr>' for m, t, mo, tk, q, w, im in rows) + '</tbody></table></div>')
    grp = [("오일리스 저소음 (실내·인테리어)", [c for c in COMP if "오일리스" in c[1] or "직결" in c[1]]),
           ("벨트식 알루미늄 탱크 (가벼움)", [c for c in COMP if c[0].startswith("JCA")]),
           ("벨트식 스틸 탱크 (현장용)", [c for c in COMP if c[0].startswith("JCS")])]
    body = ""
    for gname, rows in grp:
        pick = rows[::4] if len(rows) > 8 else rows
        body += (f'<h2 class="gt">{E(gname)} {len(rows)}종 <small>옆으로 넘겨 보세요 ›</small></h2><div class="gcs">'
                 + "".join(f'<div class="gc tk"><img loading="lazy" referrerpolicy="no-referrer" src="{IMG(im)}" alt="제일타카 콤프레셔 {E(m)}"><div class="gn">{E(m)}</div><ul><li><span>모터</span><b>{E(mo)}</b></li><li><span>탱크</span><b>{E(tk)}</b></li><li><span>토출량</span><b>{q}L/min</b></li></ul></div>' for m, t, mo, tk, q, w, im in pick)
                 + '</div>' + ctab(rows))
    body += '<h2 class="gt">고르는 법</h2><ul class="gtip"><li>타카 1~2대 인테리어: 2마력 오일리스 25~40L (조용함)</li><li>타카 여러 대·코일 타카·도장: 3.5~5.5마력 벨트식 50~80L</li><li>공장·연속 작업: 6.5마력 9.5bar 벨트식 80~120L</li><li>자주 옮기면 알루미늄 탱크(JCA), 고정해 두면 스틸 탱크(JCS)</li></ul>'
    finish("compressor", "콤프레셔", f"제일타카 콤프레셔 {len(COMP)}종 — 오일리스 저소음·벨트식 알루미늄·스틸 탱크의 마력·탱크·토출량 비교", body, IMG("JQS225-870.jpg"))

    cards = "".join(f'<div class="gc tk"><img loading="lazy" referrerpolicy="no-referrer" src="{IMG(im)}" alt="{E(n)}"><div class="gn">{E(n)}</div><p class="tkd">{E(d)}</p></div>' for n, d, im in ETC)
    finish("etc", "에어호스·타카 오일·소모품", "타카와 콤프레셔를 잇는 에어호스, 타카 전용 오일, 에어건·장갑·보안경", f'<div class="gcs">{cards}</div>', IMG(ETC[0][2]))

    # 목록
    cards = "".join(f'<a class="gi gim" href="/taka/{s}.html"><img loading="lazy" referrerpolicy="no-referrer" src="{im}" alt=""><b>{E(n)}</b><small>{E(t)}</small></a>' for s, n, t, im in out)
    ntool = sum(len(TOOLS[s][2]) for s in ORDER)
    page("taka/index.html", "타카·타카핀·콤프레셔 — 422·F30·실핀·콘크리트 타카, 타카핀 규격표 | 대전 영진목재",
         f"제일타카(JITOOL) 타카 {ntool}종, 타카핀 {len(PINS)}종, 콤프레셔 {len(COMP)}종을 용도별로 정리. 대전 유성 영진종합목재(월드건축자재) 매장 취급.",
         f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › 타카·타카핀·콤프레셔</p><h1>타카·타카핀·콤프레셔</h1><p class="glead">제일타카(JITOOL) 타카 {ntool}종, 타카핀 {len(PINS)}종, 콤프레셔 {len(COMP)}종을 용도별로 정리했습니다. 목재·합판 사실 때 맞는 핀까지 한 번에 챙겨 드립니다.</p><div class="gig">{cards}</div><div class="glk"><a href="/cheolmul/">목재 철물</a><a href="/jaryo/hardware.html">철물 전체</a><a href="/gagyeok/">자재 가격 가이드</a></div></section>{CTA}', "/jaryo/")
    return out
