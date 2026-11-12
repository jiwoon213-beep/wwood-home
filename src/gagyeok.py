# 품목별 가격 가이드(/gagyeok/) — 판매 단위가 확인된 품목만. 소매 기준가(prices.csv)만 사용.
import math, re
PY = 3.3058
# slug, 이름, 자재백과 slug, 시공법 slug, [(정규식, 판매단위, 1단위 면적㎡ 또는 None)], 설명, 단위설명, 로스, 예시 면적들(㎡), FAQ
def _lw(w, L=2438, n=8, vis=None): return round((vis or w) / 1000 * L / 1000 * n, 3)
GG = [
 ("hinoki-ruba", "히노끼 루바", "hinoki", "rubaa-cheonjang",
  [(r"루바-히노끼/유절\(오카\)@100\*10\*8자", "1단(8장)", _lw(100, vis=90)), (r"루바-히노끼/무절\(오카\)@100\*10\*8자", "1단(8장)", _lw(100, vis=90))],
  "히노끼 루바는 1단(8장) 단위로 팝니다. 폭 100mm·두께 10mm·길이 8자(약 2.4m)이고, 끼우고 나면 보이는 폭이 약 90mm라 1단이 약 1.75㎡를 덮습니다.",
  "1단 = 8장 · 1장 100×10×2438mm · 시공 면적 약 1.75㎡/단(보이는 폭 90mm 기준)", 0.10,
  [("방 천장 3×3m", 9.0), ("거실 천장 4×5m", 20.0), ("벽 1면 3×2.4m", 7.2)],
  [("히노끼 루바 1평에 몇 단 필요한가요?", "보이는 폭 90mm 기준으로 1평(3.3㎡)에 약 1.9단, 로스 10%를 더하면 약 2.1단입니다. 천장 모양·자르는 양에 따라 달라집니다."),
   ("유절과 무절 차이는요?", "유절은 옹이가 있어 자연스러운 느낌이고 값이 낮습니다. 무절은 옹이가 거의 없어 깔끔하고 값이 높습니다. 매장에서 실물 비교가 가능합니다.")]),
 ("spruce-ruba", "스프러스 루바", "hinoki", "rubaa-cheonjang",
  [(r"루바-스프러스\(유절\)@120\*12\* 8자", "1단(8장)", _lw(120, vis=110))],
  "스프러스 루바(유절, 120×12mm, 8자)는 1단(8장) 단위로 팝니다. 보이는 폭 약 110mm 기준 1단이 약 2.1㎡를 덮어, 히노끼보다 같은 면적에 단 수가 적게 듭니다.",
  "1단 = 8장 · 1장 120×12×2438mm · 시공 면적 약 2.1㎡/단(보이는 폭 110mm 기준)", 0.10,
  [("방 천장 3×3m", 9.0), ("거실 천장 4×5m", 20.0), ("벽 1면 3×2.4m", 7.2)],
  [("스프러스 루바 1평에 몇 단 필요한가요?", "보이는 폭 110mm 기준 1평에 약 1.5단, 로스 10%를 더하면 약 1.7단입니다."),
   ("히노끼 루바와 뭐가 다른가요?", "히노끼는 향과 습기에 강한 점 때문에 욕실·사우나 천장에 많이 쓰고, 스프러스는 결이 밝고 폭이 넓어 거실·카페 벽·천장에 많이 씁니다.")]),
 ("tempa-board", "템바보드", "sound", "tempa-byeok",
  [(r"템바보드 직각\(예림\)소@12\*1200\*2400", "1장", 2.88), (r"템바보드 직각\(영림\)소@15\*1200\*2400", "1장", 2.88), (r"템바보드 직각\(영림\)대@15\*1200\*2400", "1장", 2.88),
   (r"템바보드 직각\(랩핑\)소@12\*1200\*2400", "1장", 2.88), (r"템바보드 직각\(방염\)대@15\*1200\*2400", "1장", 2.88), (r"템바보드 반달\(백골\)소@ 9\*1200\*2400", "1장", 2.88),
   (r"템바보드 반달\( \)소@ 9\*1220\*2440", "1장", 2.977), (r"템바보드 삼각\( \)소@ 9\*1220\*2440", "1장", 2.977)],
  "템바보드는 1장(1200×2400 또는 1220×2440mm) 단위로 팝니다. 1장이 약 2.9㎡라 1평에 약 1.2장(로스 포함) 듭니다. 직각·반달·삼각 모양과 두께(9·12·15T), 마감(백골·랩핑·방염)에 따라 값이 다릅니다.",
  "1장 = 1200×2400mm(2.88㎡) 또는 1220×2440mm(2.98㎡)", 0.10,
  [("TV 벽 1면 3×2.4m", 7.2), ("아트월 2×2.4m", 4.8), ("카페 벽 5×2.7m", 13.5)],
  [("템바보드 1평에 몇 장 필요한가요?", "1장이 약 2.9㎡라 1평(3.3㎡)에 약 1.15장, 로스 10%를 더하면 약 1.3장입니다. 실제로는 벽 폭에 맞춰 장 단위로 올림합니다."),
   ("템바보드 위·아래 마감은 어떻게 하나요?", "보드 두께에 맞는 상하 마감재를 씁니다(9T·12T·15T용 따로). 매장에서 같이 고르시면 됩니다.")]),
 ("tempa-ruba", "템바 루바", "sound", "tempa-byeok",
  [(r"템바\(예림S22\)루바@112\*12\*8자\(6장\)", "1묶음(6장)", _lw(112, n=6)), (r"템바\(예림S14\)루바 @114\*12\*8자\(6장\)", "1묶음(6장)", _lw(114, n=6)),
   (r"템바\(예림S33\)루바@163\*12\*8자\(6장\)", "1묶음(6장)", _lw(163, n=6)), (r"템바\(루바 소\)영림 @100\*12\*8자\(6장\)", "1묶음(6장)", _lw(100, n=6))],
  "템바 루바는 1묶음(6장) 단위로 팝니다. 길이 8자(약 2.4m)이고 제품마다 폭(100~163mm)이 달라 1묶음이 덮는 면적이 1.5~2.4㎡입니다.",
  "1묶음 = 6장 · 길이 2438mm · 면적은 제품 폭 기준 계산", 0.10,
  [("TV 벽 1면 3×2.4m", 7.2), ("아트월 2×2.4m", 4.8), ("카페 벽 5×2.7m", 13.5)],
  [("템바 루바 1평에 몇 묶음 필요한가요?", "폭 112mm 제품 기준 1묶음이 약 1.6㎡라 1평에 약 2묶음, 로스 10%를 더하면 약 2.2묶음입니다. 폭이 넓은 제품일수록 적게 듭니다."),
   ("템바보드와 템바 루바 차이는요?", "템바보드는 큰 판 1장에 홈이 파인 것이라 빨리 붙고, 템바 루바는 긴 쪽판을 하나씩 끼우는 방식이라 길이 방향 이음이 없어 깔끔합니다.")]),
 ("interior-film", "인테리어 필름", "film", "film-sigong",
  [(r"필름-인테리어 @예림135", "1m", None), (r"필름-인테리어 @예림114", "1m", None), (r"필름-인테리어 @예림113\(차콜\)", "1m", None), (r"필름-인테리어 영림@ 175", "1m", None),
   (r"필름-인테리어 영림@ 176", "1m", None), (r"필름-인테리어 영림@ 188", "1m", None), (r"필름-인테리어 영림@ 60번", "1m", None),
   (r"필름-인테리어 쉐누@ 05번", "1m", None), (r"필름-인테리어 쉐누@ 06번", "1m", None), (r"필름-인테리어 쉐누@ 95번", "1m", None)],
  "인테리어 필름은 1m 단위로 잘라 팝니다(m 단가). 폭은 보통 1220mm 안팎이라 1m가 약 1.2㎡입니다. 방문 1짝 양면이면 여유 포함 약 5m 듭니다.",
  "1m 단가 · 폭 약 1220mm(제품마다 조금씩 다름)", 0.0,
  [], [("인테리어 필름 방문 1짝에 몇 m 필요한가요?", "방문(약 900×2100mm) 앞뒤 2면이면 여유 포함 약 5m입니다. 문틀까지 하면 더 필요합니다."),
       ("필름 붙이기 전에 프라이머를 꼭 발라야 하나요?", "네. 프라이머를 바르지 않으면 모서리부터 들뜨기 쉽습니다. 매장에서 필름용 수성 프라이머를 함께 팝니다.")]),
 ("oilstain", "오일스테인", "stain", "oilstain",
  [(r"오일-투명 @3\.5L\(유성/에코\)", "1통(3.5L)", None), (r"오일-월넛 @3\.5L\(유성/에코\)", "1통(3.5L)", None), (r"오일-티크 @3\.5L\(유성/에코\)", "1통(3.5L)", None),
   (r"오일-밤나무 @3\.5L\(유성/에코/404\)", "1통(3.5L)", None), (r"오일-투명 @ 16L\(유성/에코\)", "1통(16L)", None), (r"오일-월넛 @ 16L\(유성/에코\)", "1통(16L)", None),
   (r"오일-투명 @ 1L\(수성/동우\)", "1통(1L)", None), (r"오일-티크 @ 1L\(수성/동우\)", "1통(1L)", None)],
  "오일스테인은 통 단위(1L·3.5L·16L)로 팝니다. 색(투명·월넛·티크·밤나무 등)이 달라도 같은 용량은 기준가가 같습니다. 칠할 면적이 넓으면 큰 통이 1L당 값이 낮습니다.",
  "1통 단가 · 바를 수 있는 면적은 제품 표기 확인(2회 칠 기준으로 계산)", 0.0,
  [], [("오일스테인 데크 10㎡에 몇 통 필요한가요?", "제품 표기 도포량에 따라 다르지만 보통 2회 칠에 3.5L 1통이면 충분한 경우가 많습니다. 나무가 마른 상태면 더 먹습니다."),
       ("유성과 수성 중 뭘 써야 하나요?", "바깥 데크·울타리는 유성이 오래가고, 실내 가구·소품은 냄새가 적은 수성이 편합니다.")]),
]

# ---- 판재·각재 자동 목록(규격이 이름에 있는 것만) ----
import csv as _csv, os as _os
_ROWS = [r for r in _csv.DictReader(open(_os.path.dirname(_os.path.abspath(__file__)) + "/data/prices.csv", encoding="utf-8")) if r["price"].strip().isdigit()]
def _sheet_area(n):
    m = re.search(r"(\d{3,4})\*\s*(\d{3,4})(?:\*|$)", n.replace(" ", ""))
    if m: return round(int(m.group(1)) * int(m.group(2)) / 1e6, 3)
    if "4*8" in n.replace(" ", ""): return 2.977
    if "3*6" in n.replace(" ", ""): return 1.62
    return None
def _pick(cat, rx, ex=None, k=14):
    rs = [r for r in _ROWS if r["cat"] == cat and re.search(rx, r["name"]) and not (ex and re.search(ex, r["name"]))]
    rs.sort(key=lambda r: -float(r["qty"] or 0))
    return [(re.escape(r["name"]) + "$", "1장", _sheet_area(r["name"])) for r in rs[:k] if _sheet_area(r["name"])]
def _deck(cat, rx, gap=5):
    out = []
    for r in _ROWS:
        if r["cat"] == cat and re.search(rx, r["name"]):
            m = re.search(r"@?(\d{2})\*\s*(\d{2,3})\*\s*(\d{4}|\d+자)", r["name"])
            if not m: continue
            L = int(m.group(3)) if m.group(3).isdigit() else round(int(m.group(3)[:-1]) * 303.03)
            out.append((re.escape(r["name"]) + "$", "1개", round((int(m.group(2)) + gap) / 1000 * L / 1000, 3)))
    return out
def _lumber(cat, rx):
    rs = [r for r in _ROWS if r["cat"] == cat and re.search(rx, r["name"])]
    return [(re.escape(r["name"]) + "$", "1개", "len") for r in sorted(rs, key=lambda r: -float(r["qty"] or 0))]
_EX_SHEET = [("방 바닥 3×3m", 9.0), ("벽 1면 3×2.4m", 7.2), ("창고 벽·지붕 2×3m", 6.0)]
GG += [
 ("hapan-gagyeok", "합판", "hapan", "isopink-badak", _pick("합판", r"일반 [34]\*[68]"),
  "합판은 1장 단위로 팝니다. 4×8 합판(1220×2440mm)은 1장이 약 3㎡, 3×6 합판(900×1800mm)은 약 1.6㎡입니다. 두께(2.7~18mm)와 수종(베트남·인니·오쿠메), 등급에 따라 값이 다릅니다.",
  "4×8 = 1220×2440mm(약 2.98㎡) · 3×6 = 900×1800mm(약 1.62㎡) · 1장 단가", 0.10, _EX_SHEET,
  [("합판 1평에 몇 장 필요한가요?", "4×8 합판 1장이 약 3㎡라 1평(3.3㎡)에 약 1.1장, 로스 10%를 더하면 약 1.2장입니다. 실제로는 벽·바닥 크기에 맞춰 장 단위로 올림합니다."),
   ("바닥 덧방에는 몇 mm 합판을 쓰나요?", "장선 위 바닥은 보통 11.5mm 이상, 기존 바닥 위 덧방은 8.5~11.5mm를 많이 씁니다. 하중과 장선 간격에 따라 매장에서 같이 정해 드립니다.")]),
 ("osb-gagyeok", "OSB 합판", "osb", "osb-byeok", _pick("합판", r"OSB"),
  "OSB 합판은 1장(1220×2440mm, 약 3㎡) 단위로 팝니다. 같은 두께 일반 합판보다 값이 낮아 창고·가벽·지붕 바탕, 인더스트리얼 벽 마감에 많이 씁니다.",
  "1장 = 1220×2440mm(약 2.98㎡)", 0.10, _EX_SHEET,
  [("OSB 1평에 몇 장 필요한가요?", "1장이 약 3㎡라 1평에 약 1.1장, 로스 10% 포함 약 1.2장입니다."),
   ("OSB와 일반 합판 중 뭐가 좋나요?", "값과 강도는 OSB가 유리하고, 표면이 매끈하고 습기에 강한 쪽은 일반 합판입니다. 칠·필름 마감이 필요하면 합판, 거친 질감을 그대로 쓰면 OSB가 어울립니다.")]),
 ("mdf-gagyeok", "MDF", "mdf", "film-sigong", _pick("엠디", r"4\*8"),
  "MDF는 1장(1220×2440mm, 약 3㎡) 단위로 팝니다. 두께 3~18mm, 일반·고밀도·LPM(백색 마감)에 따라 값이 다르고, 원하는 크기로 재단해 드립니다.",
  "1장 = 1220×2440mm(약 2.98㎡)", 0.10, [("벽 1면 3×2.4m", 7.2), ("수납장 옆판·선반 (약 4㎡)", 4.0), ("방 벽 4면 3×3m 방", 28.8)],
  [("MDF 1장에 얼마인가요?", "두께에 따라 다르며 위 표의 소매 기준가(부가세 별도)를 참고하세요. 원하는 크기로 잘라 드리고 재단비는 매장에서 계산합니다."),
   ("MDF는 물에 약한가요?", "네. 물에 닿으면 부풀기 쉬워 욕실·바깥에는 쓰지 않습니다. 습기 있는 곳은 합판을 권합니다.")]),
 ("seokgo-gagyeok", "석고보드", "gypsum", "seokgo-byeok", _pick("석고", r"3\*6"),
  "석고보드는 1장(900×1800mm, 약 1.62㎡) 단위로 팝니다. 일반 9.5T가 가장 많이 쓰이고, 방수(욕실·주방), 방화(12.5T)는 값이 더 높습니다.",
  "1장 = 900×1800mm(약 1.62㎡)", 0.10, [("벽 1면 3×2.4m (1겹)", 7.2), ("방 천장 3×3m", 9.0), ("방 벽 4면 3×3m 방 (1겹)", 28.8)],
  [("석고보드 1평에 몇 장 필요한가요?", "1장이 약 1.62㎡라 1평에 약 2장, 로스 10% 포함 약 2.2장입니다. 2겹 시공이면 2배입니다."),
   ("욕실에는 어떤 석고보드를 쓰나요?", "물기가 닿는 욕실·주방 벽은 방수 석고보드를 씁니다. 타일 바탕은 시멘트보드를 쓰기도 합니다.")]),
 ("danyeol-gagyeok", "아이소핑크·단열재", "insul", "isopink-badak", _pick("단열", r"아이소핑크|스티로폴|이보드"),
  "아이소핑크·스티로폴은 1장(900×1800mm, 약 1.62㎡), 이보드는 1장(900×2400mm, 약 2.16㎡) 단위로 팝니다. 두께가 두꺼울수록 단열이 좋고 값도 올라갑니다.",
  "아이소핑크·스티로폴 900×1800mm(1.62㎡) · 이보드 900×2400mm(2.16㎡)", 0.05, [("방 바닥 3×3m", 9.0), ("외벽 1면 3×2.4m", 7.2), ("창고 천장 2×3m", 6.0)],
  [("아이소핑크 1평에 몇 장 필요한가요?", "1장이 약 1.62㎡라 1평에 약 2장, 로스 5% 포함 약 2.1장입니다."),
   ("이보드는 어디에 쓰나요?", "단열재에 도배·페인트용 표면이 붙어 있어, 벽에 바로 붙이고 도배하는 단열 리모델링에 많이 씁니다.")]),
 ("jipseong-gagyeok", "집성판", "jipseong", "film-sigong", _pick("집성판", r"\d{3,4}\*\d{4}\*\d+T"),
  "집성판은 1장(보통 1200×2400 또는 1220×2440mm) 단위로 팝니다. 미송·아카시아·고무나무·멀바우 등 수종과 두께(12~30T)에 따라 값이 크게 다르고, 원하는 크기로 재단해 드립니다.",
  "1장 = 1200×2400mm(2.88㎡) 또는 1220×2440mm(2.98㎡)", 0.0, [],
  [("집성판은 어떤 수종이 좋나요?", "가구 상판은 아카시아·고무나무, 가볍고 값이 낮은 건 미송, 짙은 색은 멀바우를 많이 씁니다. 매장에서 실물 결을 보고 고르세요."),
   ("집성판 재단도 해 주나요?", "네. 원하는 크기로 잘라 드립니다. 재단 그림은 재단 미리보기 페이지에서 먼저 볼 수 있습니다.")]),
 ("deck-gagyeok", "데크재(방부·합성)", "hapdeck", "hapdeck-sigong", _deck("방부", r"\(데크\)") + _deck("합성", r"데크\(솔리드\) @\d"),
  "데크재는 1개(1본) 단위로 팝니다. 방부목 데크는 12자(약 3.6m), 합성데크는 3m·2.4m 길이이고, 1개가 덮는 면적은 폭+틈(약 5mm) 기준으로 계산했습니다. 장선·클립은 따로 듭니다.",
  "1개 단가 · 면적 = (폭+틈 5mm) × 길이", 0.10, [("마당 데크 3×3m", 9.0), ("베란다 데크 2×4m", 8.0), ("넓은 데크 4×5m", 20.0)],
  [("데크 1평에 몇 개 필요한가요?", "방부목 25×140×12자 기준 1개가 약 0.52㎡라 1평에 약 6.4개, 로스 10% 포함 약 7개입니다. 장선 방부목·피스(또는 합성데크 클립)는 따로 계산합니다."),
   ("방부목 데크와 합성데크 중 뭐가 좋나요?", "방부목은 값이 낮고 칠로 색을 낼 수 있지만 오일스테인 관리가 필요합니다. 합성데크는 값이 높지만 썩지 않고 칠할 필요가 거의 없습니다.")]),
 ("gakjae-gagyeok", "구조재·방부목 각재", "gujo", "hapdeck-sigong", _lumber("구조", r"12ft") + _lumber("방부", r"^방부- ?\d(?!.*데크)"),
  "구조재(2×4, 2×6 등)와 방부목 각재는 1개 단위로 팝니다. 길이는 12ft·12자(약 3.6m)이고 원하는 길이로 잘라 드립니다. 1m당 금액도 같이 적었습니다.",
  "1개 단가 · 길이 약 3.6m(12자·12ft)", 0.0, [],
  [("구조재 2×4는 실제 크기가 얼마인가요?", "2×4는 실제 38×89mm, 2×6은 38×140mm입니다. 이름은 건조 전 치수(인치)라 실제보다 큽니다."),
   ("방부목은 실내에 써도 되나요?", "방부목은 바깥 데크·울타리·화단용입니다. 실내 가구·벽에는 구조재나 집성판을 권합니다.")]),
]

def gen(page, P, E, CTA, prod_ld, faqslide, BASE, ADDR, HOURS, TEL):
    import json
    pages = []
    for slug, nm, js, sg, specs, lead, unitdesc, loss, exs, faq in GG:
        rows = []
        for rx, unit, area in specs:
            hit = next((p for p in P if re.search(rx, p["name"])), None)
            if hit: rows.append((hit, unit, area))
        if not rows: continue
        def cn(n): return re.sub(r"^[^-]+-\s*", "", n).replace("*", "×").replace("@", " · ").strip(" ·")
        hasA = bool(exs) and any(isinstance(a, float) for _, _, a in rows)
        isM2 = not exs and any(isinstance(a, float) for _, _, a in rows)
        isLen = any(a == "len" for _, _, a in rows)
        th = "<tr><th>품목·규격</th><th>판매 단위</th><th class=r>기준가</th>" + ("<th class=r>1단위 면적</th><th class=r>1평 필요량(로스 포함)</th><th class=r>1평 예상 금액</th>" if hasA else ("<th class=r>1L당</th>" if slug == "oilstain" else "<th class=r>1m당</th>" if isLen else "<th class=r>1㎡당</th>" if isM2 else "<th class=r>1㎡당(폭 1.22m)</th>")) + "</tr>"
        trs = ""
        for p, unit, a in rows:
            pr = p["price"]
            if hasA and not isinstance(a, float):
                ext = '<td class=r>—</td><td class=r>—</td><td class=r>—</td>'
            elif hasA:
                need = PY / a * (1 + loss)
                ext = f'<td class=r data-l="1단위 면적">{a:.2f}㎡</td><td class=r data-l="1평 필요량">약 {need:.1f}</td><td class=r data-l="1평 예상"><b>약 {round(pr * need, -2):,.0f}원</b></td>'
            elif slug == "oilstain":
                L = float(re.search(r"([\d.]+)L", unit).group(1)); ext = f'<td class=r data-l="1L당">약 {round(pr / L, -2):,.0f}원</td>'
            elif isM2:
                ext = f'<td class=r data-l="1㎡당">약 {round(pr / a, -2):,.0f}원</td>'
            elif isLen:
                ext = f'<td class=r data-l="1m당">약 {round(pr / 3.6, -2):,.0f}원</td>'
            else:
                ext = f'<td class=r data-l="1㎡당">약 {round(pr / 1.22, -2):,.0f}원</td>'
            trs += f'<tr><td>{E(cn(p["name"]))}</td><td data-l="단위">{unit}</td><td class=r data-l="기준가"><b>{pr:,}원</b></td>{ext}</tr>'
        exh = ""
        if exs and hasA:
            p0, u0, a0 = rows[0]
            et = "".join(f'<tr><th>{E(t)}</th><td class=r>{m2:g}㎡ ({m2 / PY:.1f}평)</td><td class=r>{math.ceil(m2 / a0 * (1 + loss))} {u0.split("(")[0][1:] or "개"}</td><td class=r><b>약 {math.ceil(m2 / a0 * (1 + loss)) * p0["price"]:,}원</b></td></tr>' for t, m2 in exs)
            exh = f'<h2>{E(nm)} 크기별 예상 금액</h2><p class="small muted">기준: {E(cn(p0["name"]))} · 로스 {int(loss * 100)}% 포함 · 올림 계산</p><div class="tw"><table class="rt"><thead><tr><th>예시</th><th class=r>면적</th><th class=r>필요량</th><th class=r>자재비</th></tr></thead><tbody>{et}</tbody></table></div>'
            calc = f'''<div class="card" id="ggc"><h3>내 면적으로 계산</h3><p><label>면적 <input id="gga" type="number" inputmode="decimal" value="3" min="0" step="0.1" style="width:90px"></label> <select id="ggu"><option value="py">평</option><option value="m2">㎡</option></select> <select id="ggp">{"".join(f'<option value="{p["price"]}|{a}">{E(cn(p["name"]))} — {p["price"]:,}원/{u}</option>' for p, u, a in rows)}</select></p><p id="ggr" class="est"></p>
<script>(function(){{var a=document.getElementById("gga"),u=document.getElementById("ggu"),s=document.getElementById("ggp"),r=document.getElementById("ggr");function f(){{var v=parseFloat(a.value)||0,m=u.value=="py"?v*{PY}:v,x=s.value.split("|"),n=Math.ceil(m/parseFloat(x[1])*{1 + loss});r.innerHTML="<b>약 "+n+"단위 · 예상 자재비 약 "+(n*parseInt(x[0])).toLocaleString()+"원</b><span>로스 {int(loss * 100)}% 포함 · 소매 기준가 · 부가세 별도</span>";}}[a,u,s].forEach(function(e){{e.addEventListener("input",f);e.addEventListener("change",f)}});f();}})();</script></div>'''
            exh += calc
        lo = min(p["price"] for p, _, _ in rows)
        title = f"{nm} 가격 — {rows[0][1].split('(')[0]} 기준가 {lo:,}원부터" + (" · 1평에 얼마" if hasA else (" · 1L당 비교" if slug == "oilstain" else " · 1m당 단가" if isLen else " · 1㎡당 비교" if isM2 else " · m당 단가"))
        desc = f"{nm} 소매 기준가 {lo:,}원부터({rows[0][1]}). " + (f"1평에 몇 {rows[0][1][1:].split('(')[0]} 드는지, 크기별 예상 금액 계산." if hasA else "판매 단위와 품목별 기준가 정리.") + " 대전 영진목재."
        body = f'''<section class="wrap sec"><p class="crumb"><a href="/gagyeok/">자재 가격 가이드</a> › {E(nm)}</p><h1>{E(nm)} 가격</h1><p class="lead">{E(lead)}</p>
<p class="small muted">{E(unitdesc)}</p><div class="tw"><table class="rt"><thead>{th}</thead><tbody>{trs}</tbody></table></div><p class="small muted">소매 기준가 · 부가세 별도 · 면적·필요량은 계산 참고치(시공 방법·자르는 양에 따라 달라짐) · 재단·운임은 매장에서 계산</p>
{exh}
<p>👉 <a href="/jajae/{js}.html">{E(nm)} 용도·사진</a> · <a href="/sigongbeop/{sg}.html">시공 방법과 예상 자재비</a> · <a href="/calc.html">자재 계산기</a> · <a href="/price.html">전체 기준가</a></p></section>
<section class="wrap sec"><h2>{E(nm)} 가격 자주 묻는 질문</h2>{faqslide(faq + [(f"{nm} 어디서 사나요?", f"{ADDR} 영진종합목재(월드건축자재) 매장에서 실물을 보고 살 수 있습니다. {HOURS}. 전국 용달 배송도 됩니다.")])}</section>
<section class="wrap sec"><h2>다른 자재 가격</h2><p>{" · ".join(f'<a href="/gagyeok/{g[0]}.html">{E(g[1])} 가격</a>' for g in GG if g[0] != slug)}</p></section>{CTA}'''
        ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]
        ld += prod_ld([{"name": p["name"], "cat": p["cat"], "price": p["price"]} for p, _, _ in rows[:6]], f"{BASE}/gagyeok/{slug}.html")
        page(f"gagyeok/{slug}.html", title + " | 대전 영진목재", desc, body, "/price.html", ld)
        pages.append((slug, nm, lo, rows[0][1], lead))
    cards = "".join(f'<a class="mc" href="/gagyeok/{s}.html"><b>{E(n)} 가격</b><span>{E(u)} {lo:,}원부터 · {E(l[:50])}…</span></a>' for s, n, lo, u, l in pages)
    page("gagyeok/index.html", "자재 가격 가이드 — 합판·석고보드·OSB·MDF·데크·루바·템바보드 1평에 얼마 | 영진목재",
         "합판·OSB·MDF·석고보드·단열재·집성판·데크·구조재·루바·템바보드·필름·오일스테인의 판매 단위와 소매 기준가, 1평 예상 금액.",
         f'<section class="wrap sec"><h1>자재 가격 가이드</h1><p class="lead">"1단에 몇 장이에요?", "1평에 얼마 들어요?" — 자주 묻는 판매 단위와 예상 금액을 자재별로 정리했습니다. 모두 소매 기준가(부가세 별도)입니다.</p><div class="mg m2">{cards}</div><p><a href="/price.html">전체 기준가 보기</a> · <a href="/sigongbeop/">자재 시공법</a></p></section>{CTA}', "/price.html")
    return [(s, n) for s, n, *_ in pages]
