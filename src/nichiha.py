# -*- coding: utf-8 -*-
"""니치하(NICHIHA) 세라믹 사이딩 — 길이 3,030mm EX 시리즈 85종 — /nichiha/
데이터: src/data/nichiha.tsv (무늬|품번|NG·A2|사진 파일). 출처 nichiha.co.jp/global 라인업(영문) → 한글로 정리.
가격: 홈페이지 기준가(prices.csv '사이딩-V16 16*455*3030' 줄)만 참고로 표시, 품번별 가격은 매장 문의."""
import csv, os, re
from yerim import LB

BIG = lambda f: "https://www.nichiha.co.jp/assets/img/global/lineup/main/" + f
TH = lambda c: f"https://www.nichiha.co.jp/global/products/product_lineup/length2/{c}.webp"
VIS = [("simple", "심플·단색", "줄눈 없이 깔끔한 단색·면 무늬"), ("designers", "디자이너스", "입체 줄무늬·패턴이 들어간 디자인형"),
       ("wood", "우드(나무결)", "나무 판자·목재결 무늬"), ("stone", "스톤(석재)", "석재·암석 질감 무늬"), ("tile", "타일·벽돌", "벽돌·타일을 쌓은 무늬")]
SPEC = [("규격", "16mm(두께) × 455mm(폭) × 3,030mm(길이)"), ("포장", "1팩 2장"), ("시공 면적", "1장 약 1.38㎡ (1평 약 2.4장)"),
        ("시공 방식", "클립 시공(못이 겉에 안 보임) · 위아래 암수 끼움"), ("하지", "목조 각재 하지·경량 철골 하지 모두 가능"), ("재질", "세라믹(시멘트·섬유 보강) 사이딩")]


def load(ROOT):
    p = os.path.join(ROOT, "data", "nichiha.tsv")
    if not os.path.exists(p): return []
    return [l.rstrip("\n").split("|") for l in open(p, encoding="utf-8") if l.strip() and not l.startswith("#")]


def prices(ROOT):
    out = []
    for r in csv.DictReader(open(os.path.join(ROOT, "data", "prices.csv"), encoding="utf-8")):
        if re.search(r"V16", r["name"]) and r["price"].strip().isdigit(): out.append((r["name"].replace("사이딩-", "").strip(), int(r["price"])))
    return out


def gen(page, E, CTA, faqslide, ADDR, HOURS, ROOT):
    rows = load(ROOT)
    if not rows: return []
    pz = prices(ROOT)
    board = [p for n, p in pz if "3030" in n]
    lo = min(board) if board else 0
    def card(r):
        v, code, fl, img = r
        sp = "\n".join(f"{a}\t{b}" for a, b in SPEC + ([("표면", "니치가드(NG) — 오염이 덜 붙는 표면 처리 제품")] if fl == "NG" else []) + ([("불연 등급", "유럽 화재 등급 A2-s1,d0 (불연 수준)")] if fl == "A2" else []))
        tag = {"NG": " · 니치가드", "A2": " · 불연 A2"}.get(fl, "")
        return (f'<a class="yri" href="#" data-big="{BIG(img)}" data-n="니치하 {E(code)}{tag}" data-sp="{E(sp)}"><img loading="lazy" decoding="async" referrerpolicy="no-referrer" width="300" height="300" src="{TH(code)}" alt="니치하 세라믹 사이딩 {E(code)}">'
                f'<span>{E(code)}{tag}</span><em class="cbp q">{"기준가 " + format(lo, ",") + "원~ /장" if lo else "매장 문의"}</em></a>')
    secs = ""
    for k, nm, d in VIS:
        xs = [r for r in rows if r[0] == k]
        if not xs: continue
        secs += f'<h2 class="gt" id="{k}"><span>{E(nm)} <small style="font-size:14px">{len(xs)}가지</small></span><small>옆으로 넘겨 보세요 ›</small></h2><p class="small muted" style="margin:-6px 0 8px">{E(d)}</p><div class="yrg">{"".join(card(r) for r in xs)}</div>'
    chips = '<div class="qk">' + "".join(f'<a href="#{k}">{E(nm)}</a>' for k, nm, d in VIS if any(r[0] == k for r in rows)) + '</div>'
    ptab = ""
    if pz:
        ptab = ('<div class="tw"><table class="rt"><thead><tr><th>품목</th><th>기준가</th></tr></thead><tbody>' + "".join(f'<tr><th>{E(n)}</th><td data-l="기준가"><b>{p:,}원</b></td></tr>' for n, p in pz) + '</tbody></table></div>'
                + (f'<div class="est"><b>1평(3.3㎡) 약 2.4장 → 판재만 약 {round(lo * 3.3 / 1.38, -2):,.0f}원~</b><span>홈페이지 기준가(부가세 별도) 중 가장 낮은 품번 기준 · 로스·스타터·클립·코너 별도 · 품번·색상별 가격은 매장 문의</span></div>' if lo else ""))
    spec = '<div class="tw"><table class="rt"><tbody>' + "".join(f'<tr><th>{E(a)}</th><td>{E(b)}</td></tr>' for a, b in SPEC) + '<tr><th>표시 설명</th><td>NG = 니치가드(오염 방지 표면) 제품 · A2 = 유럽 화재 등급 A2-s1,d0 제품</td></tr></tbody></table></div>'
    fq = faqslide([("세라믹 사이딩 1평에 몇 장 드나요?", "16×455×3,030mm 한 장이 약 1.38㎡라 1평(3.3㎡)에 약 2.4장입니다. 창문·로스를 생각해 10% 정도 여유 있게 잡으세요."),
                   ("세라믹 사이딩은 어떻게 붙이나요?", "각재나 경량 철골 하지 위에 스타터를 대고, 전용 클립으로 판을 잡아 위로 끼워 올라가는 방식입니다. 못이 겉에 보이지 않습니다."),
                   ("니치하 사이딩 어디서 사나요?", f"{ADDR} 영진종합목재(월드건축자재) 매장에서 상담·주문합니다. {HOURS}. 전국 용달 배송도 됩니다.")])
    body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/jaryo/siding.html">외장재·사이딩</a> › 니치하 세라믹 사이딩</p><h1>니치하 세라믹 사이딩 <small>{len(rows)}가지</small></h1>'
            f'<p class="glead">일본 니치하(NICHIHA)의 외벽용 세라믹 사이딩, 길이 3,030mm EX 시리즈입니다. 무늬별로 모았고 사진을 누르면 크게 보고 규격을 확인할 수 있습니다.</p>{chips}{secs}'
            f'<h2 class="gt">규격·시공</h2>{spec}<h2 class="gt">기준가</h2>{ptab or "<p>품번·색상별 가격은 매장에 문의해 주세요.</p>"}'
            f'<div class="glk"><a href="/jaryo/siding.html">외장재·사이딩 전체</a><a href="/sigongbeop/">자재 시공법</a><a href="/gagyeok/siding-gagyeok.html">사이딩 가격 가이드</a><a href="/visit.html">매장 길찾기</a></div></section>'
            f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{fq}</section>{CTA}' + LB)
    page("nichiha/index.html", f"니치하 세라믹 사이딩 {len(rows)}종 — 16×455×3030 규격·기준가 | 대전 영진목재",
         f"니치하(NICHIHA) 세라믹 사이딩 3,030mm {len(rows)}가지 — 우드·스톤·타일벽돌·심플 무늬, 규격·1평 장수·기준가. 대전 유성 영진종합목재 상담·전국 배송.", body, "/jaryo/", None, BIG(rows[0][3]))
    return rows
