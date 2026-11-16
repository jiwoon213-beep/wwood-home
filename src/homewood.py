# -*- coding: utf-8 -*-
"""수입 목조주택 자재·창호(/suip/) — homewood.co.kr((주)홈우드, 사장님 '허락 받음, 주문 가능' 2026-11-16) 상품 사진·이름.
화면에 공급 업체 이름은 쓰지 않음(제조사 브랜드명만). 가격은 매장 문의.
데이터: src/data/homewood_raw.txt (slug|이름|사진경로|분류) — 내장 브라우저로 수집. 우리 사이트(쇼핑몰·크나우프·메가타이·제일타카)와 같은 상품은 DROP으로 뺌."""
import os, re
from yerim import LB

BASE = "https://homewood.co.kr/wp-content/uploads/"
# 기존 쇼핑몰·다른 카탈로그와 같은 상품(중복) — 빼기
DROP = re.compile(r"^(knauf-|megatie-|kcc-gypsum|plywood-(mdf|sungchang|malaysia|vietnam|core|waterproof|tego)|plywood_china|"
                  r"redpine-board|hinoki-board|lawang-laminated|rubber-tree-board|아카시아-집성판|merbau-board|"
                  r"stairs-ash|stairs-redpine|woodpanel-redpine|woodpanel-cedar|woodpanel-clear-wrc|woodpanel-spruce|woodpanel-hinoki-(panel|clear)|"
                  r"birch_plywood|pine_plywood|skytech|lp-|wing-screws|coil_nail|roofing-coil-nail|easy-seal|vinyl-siding|woodsiding-log|"
                  r"deck-bangkirai|mebau-flooring|h3-treated-redpine-|tacker-|타카핀-st|brad-nails-dt|headless-pins)")
GRP = [("목재", "wood", "구조목(일림·스프러스·레드파인), 소할재, 하슬라커 글루램", "23"),
       ("토대/바닥/데크", "floor", "바닥 장선, 방부 토대재, 하드우드 데크, 히노끼 온돌마루·후로링, 온돌 시스템", "25"),
       ("벽체용", "wall", "벽체·지붕용 OSB, 인테리어 OSB, 시멘트보드, 석고보드 부자재", "24"),
       ("지붕재", "roof", "아스팔트 슁글(CT·써튼티드), 웨스턴 레드시다 쉐이크", "31"),
       ("윈도우/도어", "window", "살라만더 시스템 창호·현관도어, 플라이젬 3중창, 벨룩스 지붕창·천창, 테니·캡스톤·도어코 현관도어, 우딘 실내 도어", "29w"),
       ("단열재/습기/관리", "insul", "오웬스코닝·존스맨빌 단열재, YS 락울, 아이씬폼, 타이벡 투습방수지·테이프, 방수시트, 환기 벤트", "30"),
       ("내장재", "inner", "루바(레드파인·히노끼·사스나·적삼목·햄록), 인테리어 합판, 우딘 몰딩, 계단재", "27"),
       ("외장재", "outer", "코노시마 세라믹사이딩·부자재, 메탈사이딩, 시멘트·목재 사이딩, 포미스톤, 하이클래딩, 릭실 아키타일", "31"),
       ("DIY자재", "diy", "집성판, 인테리어 마감재, 티쿠릴라 오일스테인·페인트, 산마르코 도장재, 목재용 글루, 래티스, DIY 키트", "35"),
       ("악세사리/철물/공구", "acc", "구조용 스크류·건네일·루핑네일, 다락방 사다리, 씰실러", "32")]
GN = {g[0]: g for g in GRP}

def img(p, big=False):
    p = p.strip()
    if big: p = re.sub(r"-\d+x\d+(\.\w+)$", r"\1", p)
    return BASE + p


PFX = [(r"^doorco-", "도어코 "), (r"^woodin-(?!moldings|.*maru)", "우딘 "), (r"^(capstone-|designer-collection)", "캡스톤 "),
       (r"^(konoshima-ceramic-siding-(?!premire|kaijansen|yunagi|grandroche|shinjan|tools)|ceramic-siding-topper)", "세라믹 사이딩 ")]
def fixname(slug, n):
    for rx, p in PFX:
        if re.search(rx, slug) and not n.startswith(p.strip()): return p + n
    if slug == "torem" and "데크" not in n: return n + " 데크"
    return n

SUBKW = [("천창", "벨룩스 천창"), ("벨룩스|VELUX", "벨룩스 지붕창"), ("캡스톤", "캡스톤 현관도어"), ("도어코", "도어코 현관도어"), ("^우딘", "우딘 도어"), ("살라만더", "살라만더 현관도어"), ("집성판", "집성판"), ("래티스", "래티스"), ("키트|브라켓", "DIY 키트"), ("마감재", "인테리어 마감재"), ("루바", "루바"), ("계단재", "계단재"),
         ("몰딩", "몰딩"), ("사이딩", "목재 사이딩"), ("포미스톤", "포미스톤"), ("도어", "도어"), ("OSB", "OSB"), ("합판", "합판"), ("벤트", "환기 벤트"),
         ("타이벡|에어가드", "듀폰 타이벡"), ("단열|락울|아이씬", "단열재"), ("데크|토렘|방킬라이", "하드우드 데크"), ("마루|후로링", "마루·후로링"), ("온돌", "바닥 난방"), ("장선|2X(8|10|12)", "바닥장선")]
def guess(top, sub, n):
    if sub and sub != top: return sub
    for kw, lab in SUBKW:
        if re.search(kw, n): return lab
    return top

def load(ROOT):
    f = os.path.join(ROOT, "data", "homewood_raw.txt")
    if not os.path.exists(f): return []
    rows, seen = [], set()
    for l in open(f, encoding="utf-8"):
        x = l.rstrip("\n").split("|")
        if len(x) < 4 or x[0] in seen or DROP.search(x[0]) or "placeholder" in x[2] or "비공개" in x[1]: continue
        seen.add(x[0])
        top, _, sub = [s.strip() for s in re.sub(r"\s*/\s*Page \d+", "", x[3]).partition(" / ")]
        if top not in GN: continue
        n = fixname(x[0], x[1].strip())
        rows.append(dict(s=x[0], n=n, i=x[2], g=top, sub=guess(top, sub, n)))
    return rows

def gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT):
    rows = load(ROOT)
    if not rows: return []
    def card(r):
        sp = f"분류\t{r['sub']}\n가격\t매장 문의(042-545-2900)"
        return (f'<a class="yri" href="#" data-big="{img(r["i"], True)}" data-n="{E(r["n"])}" data-sp="{E(sp)}">'
                f'<img loading="lazy" decoding="async" referrerpolicy="no-referrer" width="247" height="300" src="{img(r["i"])}" alt="{E(r["n"])}"><span>{E(r["n"])}</span><em class="cbp q">매장 문의</em></a>')
    tops = [g for g in GRP if any(r["g"] == g[0] for r in rows)]
    nav = lambda cur: '<div class="glk tkn">' + "".join(f'<a href="/suip/{g[1]}.html"{" class=on" if g[0] == cur else ""}>{E(g[0])}</a>' for g in tops) + '</div>'
    out = []
    for g, slug, desc, _c in tops:
        xs = [r for r in rows if r["g"] == g]
        subs = list(dict.fromkeys(r["sub"] for r in xs))
        sec = "".join(f'<h2 class="gt"><span>{E(s)} <small style="font-size:14px">{sum(1 for r in xs if r["sub"] == s)}가지</small></span><small>옆으로 넘겨 보세요 ›</small></h2><div class="yrg">{"".join(card(r) for r in xs if r["sub"] == s)}</div>' for s in subs)
        fq = faqslide([(f"{g} 수입 자재 어디서 사나요?", f"{ADDR} 영진종합목재(월드건축자재) 매장에서 상담·주문합니다. {HOURS}. 전국 용달 배송도 됩니다."),
                       (f"{g} 가격은 얼마인가요?", "제품·규격·수량에 따라 달라서 매장이나 전화(042-545-2900)로 견적을 드립니다."),
                       ("재고가 매장에 다 있나요?", "일부는 주문 후 입고되는 제품입니다. 필요한 날짜를 알려 주시면 입고 일정을 확인해 드립니다.")])
        body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › <a href="/suip/">수입 목조주택 자재·창호</a> › {E(g)}</p><h1>{E(g)} 수입 자재 <small>{len(xs)}가지</small></h1>'
                f'<p class="glead">{E(desc)}. 사진을 누르면 크게 볼 수 있습니다. 가격·재고는 매장 문의.</p>{nav(g)}{sec}</section>'
                f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{fq}</section>{CTA}' + LB)
        nm = ", ".join(subs)
        page(f"suip/{slug}.html", f"{g} 수입 자재 {len(xs)}종 — {nm[:42]} | 대전 영진목재",
             f"목조주택 {g} 수입 자재 {len(xs)}가지 사진: {desc}. 대전 유성 영진종합목재 상담·주문·전국 배송.", body, "/jaryo/", None, img(xs[0]["i"], True))
        out.append((g, slug, xs))
    rws = "".join(f'<h2 class="gt"><span><a href="/suip/{s}.html" style="color:inherit;text-decoration:none">{E(g)}</a> <small style="font-size:14px">{len(xs)}가지</small></span><small>옆으로 넘겨 보세요 ›</small></h2><div class="yrg">{"".join(card(r) for r in xs[:12])}<a class="yri ymore" href="/suip/{s}.html"><span>{E(g)} 전체 보기 ›</span></a></div>' for g, s, xs in out)
    page("suip/index.html", f"수입 목조주택 자재·창호 {len(rows)}종 — 벨룩스·살라만더·타이벡·티쿠릴라 | 대전 영진목재",
         f"벨룩스 지붕창, 살라만더 시스템 창호, 타이벡, 오웬스코닝 단열재, 코노시마 세라믹사이딩, 티쿠릴라 등 수입 목조주택 자재 {len(rows)}가지. 대전 영진목재 상담·주문.",
         f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/">전체 자재</a> › 수입 목조주택 자재·창호</p><h1>수입 목조주택 자재·창호</h1><p class="glead">목조주택에 쓰는 수입 구조목·창호·지붕창·단열재·투습방수지·외장재·DIY 도료까지 {len(rows)}가지를 사진으로 모았습니다. 가격·재고는 매장(042-545-2900)에 물어보세요.</p>{nav("")}<div class="glk tkn" style="margin-top:6px">' + "".join(f'<a href="/suip/b-{b[0]}.html">{E(b[1])}</a>' for b in BRANDS) + f'</div>{rws}</section>{CTA}' + LB,
         "/jaryo/", None, img(rows[0]["i"], True))
    return out


BRANDS = [("velux", "벨룩스(VELUX) 지붕창·천창", r"VELUX|벨룩스", "경사지붕 지붕창(GGL·GPL·GGU·GPU), 평지붕창, 테라스·발코니창, 천창과 후레싱·블라인드"),
          ("salamander", "살라만더 시스템 창호·현관도어", r"살라만더", "독일식 시스템 창호(L/S·T/T·T/S 등)와 멀리언·기본 라인 현관도어"),
          ("plygem", "플라이젬 3중창", r"플라이젬", "비스타 3중창 싱글슬라이더·싱글헝·어닝·픽스·파티오"),
          ("tyvek", "듀폰 타이벡 투습방수지·테이프", r"타이벡|듀폰", "하우스랩·드레인랩·UV 파사드·수프로 플러스·에어가드, 타이트씰·전용 테이프"),
          ("konoshima", "코노시마 세라믹사이딩 드레스·부자재", r"코노시마|세라믹 사이딩|세라믹 소핏", "드레스 프레미르·카이잔센·유나기·그랜드 로슈·신잔과 클립·후레싱·조이너·실란트"),
          ("tikkurila", "티쿠릴라 오일스테인·바니쉬·페인트", r"티쿠릴라", "발티 플러스 수용성 오일스테인, 파넬리·파게티 아싸, 키바 바니쉬, 헤르미 퍼니처 페인트"),
          ("sanmarco", "산마르코 이탈리아 도장재", r"산마르코", "마모리노·마르모 엔티크·콘크리트아트·카도로 등 특수 미장·도장재"),
          ("woodin", "우딘 실내 도어·몰딩·마루", r"우딘", "ABS·멤브레인·글래스·피노 슬림 도어, 페이퍼·클래식 몰딩, 우딘 마루"),
          ("insulation", "오웬스코닝·존스맨빌 글라스울 단열재", r"오웬스코닝|존스맨빌|락울", "가·나·다 등급 글라스울 단열재, 스틸하우스용, YS 프리미엄 락울"),
          ("ilim", "일림 구조목(스프러스·레드파인)", r"일림", "J-Grade·#2&BTR 스프러스, 레드파인 2×2~2×12·4×4"),
          ("metalsiding", "메탈사이딩 무늬", r"메탈사이딩", "라임스톤·롱스톤·브릭·스타코마블·스팬드럴 등 메탈사이딩"),
          ("shingle", "아스팔트 슁글·시다쉐이크 지붕재", r"슁글|쉐이크", "CT·써튼티드 이중그림자·육각·일반사각 슁글, 웨스턴 레드시다 쉐이크")]

def gen_brands(page, E, CTA, faqslide, ADDR, HOURS, ROOT):
    rows = load(ROOT)
    out = []
    for slug, title, rx, desc in BRANDS:
        xs = [r for r in rows if re.search(rx, r["n"])]
        if len(xs) < 3: continue
        cards = "".join(f'<a class="yri" href="#" data-big="{img(r["i"], True)}" data-n="{E(r["n"])}" data-sp="{E("분류" + chr(9) + r["sub"] + chr(10) + "가격" + chr(9) + "매장 문의(042-545-2900)")}"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" width="247" height="300" src="{img(r["i"])}" alt="{E(r["n"])}"><span>{E(r["n"])}</span><em class="cbp q">매장 문의</em></a>' for r in xs)
        short = re.sub(r"\(.*?\)", "", title).split()[0]
        fq = faqslide([(f"{short} 제품 대전에서 살 수 있나요?", f"네. {ADDR} 영진종합목재(월드건축자재)에서 상담·주문합니다. {HOURS}. 전국 용달 배송도 됩니다."),
                       (f"{short} 가격은 얼마인가요?", "제품·규격·수량에 따라 달라 매장이나 전화(042-545-2900)로 견적을 드립니다."),
                       ("바로 가져갈 수 있나요?", "일부 제품은 주문 후 입고됩니다. 필요한 날짜를 알려 주시면 입고 일정을 확인해 드립니다.")])
        body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/suip/">수입 목조주택 자재·창호</a> › {E(title)}</p><h1>{E(title)} <small>{len(xs)}가지</small></h1>'
                f'<p class="glead">{E(desc)}. 사진을 누르면 크게 볼 수 있습니다. 가격·재고는 매장 문의.</p>'
                f'<div class="yrg">{cards}</div><p class="small muted" style="margin-top:12px">다른 수입 자재: ' + " · ".join(f'<a href="/suip/b-{b[0]}.html">{E(b[1])}</a>' for b in BRANDS if b[0] != slug) + '</p></section>'
                f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{fq}</section>{CTA}' + LB)
        page(f"suip/b-{slug}.html", f"{title} {len(xs)}종 — 사진·종류 | 대전 영진목재", f"{title} {len(xs)}가지: {desc}. 대전 유성 영진종합목재 상담·주문·전국 배송.", body, "/jaryo/", None, img(xs[0]["i"], True))
        out.append((slug, title, len(xs)))
    return out
