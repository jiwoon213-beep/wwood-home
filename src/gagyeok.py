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

def _plain(cat, rx, k=20, ex=None):
    rs = [r for r in _ROWS if r["cat"] == cat and re.search(rx, r["name"]) and not (ex and re.search(ex, r["name"]))]
    rs.sort(key=lambda r: -float(r["qty"] or 0))
    return [(re.escape(r["name"]) + "$", "1개", "plain") for r in rs[:k]]
GG += [
 ("molding-gagyeok", "몰딩·걸레받이", "molding", "molding-georebatgi", _plain("몰딩", r"평|걸레|천정|마이너스|계단", 24),
  "몰딩·걸레받이는 1개 단위로 팝니다. 폭(30~100mm)과 모양(평·걸레받이·천장·마이너스), 색상(중백색·오크·쉐누·영림 등)에 따라 값이 다릅니다. 방 둘레 길이를 재 오시면 필요한 개수를 계산해 드립니다.",
  "1개 단가 · 길이는 제품마다 다름(매장 확인)", 0.0, [],
  [("몰딩은 몇 개 필요한가요?", "방 둘레 길이(가로+세로)×2를 몰딩 1개 길이로 나누고, 모서리 자르는 양을 생각해 1~2개 여유를 둡니다. 몰딩 1개 길이는 제품마다 달라 매장에서 같이 계산해 드립니다."),
   ("걸레받이와 천장 몰딩은 같은 색으로 하나요?", "보통 문틀·문과 같은 색으로 맞추거나 벽지에 맞춰 백색으로 많이 합니다. 실물 샘플을 매장에서 비교해 보세요.")]),
 ("siding-gagyeok", "사이딩", "siding", "siding-oebyeok",
  [(re.escape(r["name"]) + "$", "1장", 0.727) for r in _ROWS if re.search(r"사이딩- 시멘트 @6\.5\*230\*12자", r["name"])]
  + [(re.escape(r["name"]) + "$", "1장", 1.379) for r in _ROWS if re.search(r"사이딩-V16 16\*455\*3030", r["name"])]
  + [(re.escape(r["name"]) + "$", "1박스", "plain") for r in _ROWS if re.search(r"사이딩-메탈\(.*\)@380\*3000", r["name"])],
  "시멘트 사이딩(6.5×230×12자)과 세라믹 사이딩 아이큐브(V16, 16×455×3030)는 1장, 메탈 사이딩은 1박스 단위로 팝니다. 시멘트 사이딩은 겹침(약 30mm)을 빼면 1장이 약 0.73㎡, 아이큐브는 1장이 약 1.38㎡를 덮습니다.",
  "시멘트 1장 ≈ 0.73㎡(보이는 폭 200mm) · 아이큐브 1장 ≈ 1.38㎡ · 메탈 1박스 단가", 0.10, [("외벽 1면 6×2.4m", 14.4), ("창고 외벽 4면 3×3×2.4m", 28.8), ("주택 한쪽 벽 8×2.7m", 21.6)],
  [("시멘트 사이딩 1평에 몇 장 필요한가요?", "겹침 30mm를 빼면 1장이 약 0.73㎡라 1평에 약 4.5장, 로스 10% 포함 약 5장입니다. 창·문 자리는 빼고 모서리 마감재는 따로 계산합니다."),
   ("메탈 사이딩과 세라믹 사이딩 차이는요?", "메탈은 가볍고 시공이 빠르며, 세라믹(아이큐브)은 두껍고 단열·내구성이 좋아 주택 외벽에 많이 씁니다. J찬넬·코너·스타터 같은 부자재가 같이 듭니다.")]),
 ("door-gagyeok", "방문·문틀", "door", "munteul-gyoche", _plain("문", r"@\d{3,4}\*\d{4}", 20) + _plain("문틀", r"@\d{3,4}\*\d{4}", 12),
  "방문과 문틀은 1개 단위로 팝니다. 같은 디자인이라도 크기(폭×높이)와 색상(쉐누·예림·영림 번호), 문틀 폭(110·130·155·175·230mm)에 따라 값이 다릅니다. 교체할 문 크기와 벽 두께를 재 오시면 맞는 제품을 찾아 드립니다.",
  "1개 단가 · @ 뒤 숫자가 크기(폭×높이 mm), 앞 숫자(110·155 등)가 문틀 폭", 0.0, [],
  [("방문 교체하려면 뭐가 필요한가요?", "문짝, 문틀(벽 두께에 맞는 폭), 경첩 3개, 손잡이(실린더)가 기본입니다. 문틀째 바꾸면 몰딩·실리콘도 같이 듭니다."),
   ("문 크기는 어떻게 재나요?", "기존 문짝의 폭·높이·두께와, 문틀이 감싸는 벽 두께를 재 오세요. 문 크기 계산기도 있습니다(/calc.html#door).")]),
]

# 자재백과 slug·재단 카테고리 → 가격 가이드
BYMAT = {"molding": [("molding-gagyeok", "몰딩·걸레받이")], "siding": [("siding-gagyeok", "사이딩")], "door": [("door-gagyeok", "방문·문틀")], "hinoki": [("hinoki-ruba", "히노끼 루바"), ("spruce-ruba", "스프러스 루바")], "sound": [("tempa-board", "템바보드"), ("tempa-ruba", "템바 루바")], "film": [("interior-film", "인테리어 필름")], "stain": [("oilstain", "오일스테인")], "hapan": [("hapan-gagyeok", "합판")], "osb": [("osb-gagyeok", "OSB")], "mdf": [("mdf-gagyeok", "MDF")], "gypsum": [("seokgo-gagyeok", "석고보드")], "insul": [("danyeol-gagyeok", "아이소핑크·단열재")], "jipseong": [("jipseong-gagyeok", "집성판")], "hapdeck": [("deck-gagyeok", "데크재")], "bangbu": [("deck-gagyeok", "방부목 데크"), ("gakjae-gagyeok", "방부목 각재")], "gujo": [("gakjae-gagyeok", "구조재")]}
BYCAT = {"합판": [("hapan-gagyeok", "합판")], "MDF": [("mdf-gagyeok", "MDF")], "집성판": [("jipseong-gagyeok", "집성판")], "석고보드": [("seokgo-gagyeok", "석고보드")], "단열재": [("danyeol-gagyeok", "단열재")], "구조재": [("gakjae-gagyeok", "구조재")], "방부목": [("gakjae-gagyeok", "방부목")], "각재·다루끼": [("gakjae-gagyeok", "각재")], "데크": [("deck-gagyeok", "데크재")]}
def links(pairs):
    seen = []; [seen.append(p) for p in pairs if p not in seen]
    return ('<p>💰 <b>가격 가이드</b> ' + " · ".join(f'<a href="/gagyeok/{a}.html">{b} 가격 — 1평에 얼마</a>' for a, b in seen) + '</p>') if seen else ""

def gen(page, P, E, CTA, prod_ld, faqslide, BASE, ADDR, HOURS, TEL, ALLFAQ=None):
    pages = []
    def won(x): return f"{int(round(x, -2)):,}원"
    for slug, nm, js, sg, specs, lead, unitdesc, loss, exs, faq in GG:
        rows = []
        for rx, unit, area in specs:
            hit = next((p for p in P if re.search(rx, p["name"])), None)
            if hit: rows.append((hit, unit, area))
        if not rows: continue
        def cn(p):
            n = re.sub(r"^[^-]+-\s*", "", p["name"]).replace("*", "×").replace("@", " · ").strip(" ·")
            n = re.sub(r"\s+", " ", n)
            return (("문틀 " if p["cat"] == "문틀" else "문짝 ") if slug == "door-gagyeok" else "") + n
        hasA = bool(exs) and any(isinstance(a, float) for _, _, a in rows)
        isM2 = not exs and any(isinstance(a, float) for _, _, a in rows)
        isLen = any(a == "len" for _, _, a in rows)
        isPlain = all(a == "plain" for _, _, a in rows)
        uw = rows[0][1][1:].split("(")[0]  # 장·단·개·묶음·m·통
        # 카드: 큰 숫자 하나 + 작은 정보 줄
        cards = []; per = []
        for p, unit, a in rows:
            pr = p["price"]; li = [("기준가", f"{pr:,}원 / {unit}")]
            if hasA and isinstance(a, float):
                need = PY / a * (1 + loss); v = pr * need; per.append(v)
                big, lab = "약 " + won(v), "1평 예상"
                li += [(f"{unit.split('(')[0]} 면적", f"{a:.2f}㎡"), ("1평에", f"약 {need:.1f}{uw}")]
            elif isM2 and isinstance(a, float):
                v = pr / a; per.append(v); big, lab = "약 " + won(v), "1㎡당"
                li += [(f"{unit} 면적", f"{a:.2f}㎡")]
            elif isLen:
                v = pr / 3.6; per.append(v); big, lab = "약 " + won(v), "1m당"; li += [("길이", "약 3.6m")]
            elif slug == "oilstain":
                L = float(re.search(r"([\d.]+)L", unit).group(1)); v = pr / L; per.append(v); big, lab = "약 " + won(v), "1L당"
            elif slug == "interior-film":
                v = pr / 1.22; per.append(v); big, lab = "약 " + won(v), "1㎡당"
            else:
                big, lab = f"{pr:,}원", unit; li = []
            cards.append(f'<div class="gc"><div class="gn">{E(cn(p))}</div><div class="gp"><small>{lab}</small>{big}</div>' + ("<ul>" + "".join(f"<li><span>{x}</span><b>{y}</b></li>" for x, y in li) + "</ul>" if li else "") + "</div>")
        lo = min(p["price"] for p, _, _ in rows)
        if hasA: hl, hv = "1평 예상", "약 " + won(min(per)) + "부터"
        elif per: hl, hv = ("1㎡당" if isM2 or slug == "interior-film" else "1m당" if isLen else "1L당"), "약 " + won(min(per)) + "부터"
        else: hl, hv = f"{rows[0][1]} 기준가", f"{lo:,}원부터"
        a0 = next((a for _, _, a in rows if isinstance(a, float)), None)
        hero = f'<div class="ghero"><div class="gh1"><small>{hl}</small><b>{hv}</b></div>' + (f'<div><small>기준가</small><b>{lo:,}원~</b><span>{E(rows[0][1])}</span></div>' if per else f'<div><small>판매 단위</small><b>{E(rows[0][1])}</b><span>{E(unitdesc.split(" · ")[0])}</span></div>') + f'<div><small>종류</small><b>{len(rows)}가지</b><span class="gsw">옆으로 넘겨 보기</span></div></div>'
        exh = ""
        if exs and hasA:
            p0, u0, a0 = next(r for r in rows if isinstance(r[2], float))
            ex_c = "".join(f'<div class="gc gx"><div class="gn">{E(t)}</div><div class="gp"><small>{m2:g}㎡ · {m2 / PY:.1f}평</small>약 {math.ceil(m2 / a0 * (1 + loss)) * p0["price"]:,}원</div><ul><li><span>필요량</span><b>{math.ceil(m2 / a0 * (1 + loss))}{uw}</b></li></ul></div>' for t, m2 in exs)
            opts = "".join(f'<option value="{p["price"]}|{a}">{E(cn(p))} ({p["price"]:,}원)</option>' for p, u, a in rows if isinstance(a, float))
            exh = f"""<h2 class="gt">이 크기면 얼마?</h2><p class="gs">{E(cn(p0))} 기준 · 로스 {int(loss * 100)}% 포함</p><div class="gcs">{ex_c}</div>
<div class="gcalc"><b>내 면적으로 계산</b><div class="gcr"><input id="gga" type="number" inputmode="decimal" value="3" min="0" step="0.1" aria-label="면적"><select id="ggu" aria-label="단위"><option value="py">평</option><option value="m2">㎡</option></select></div><select id="ggp" aria-label="제품">{opts}</select><div id="ggr" class="gres"></div></div>
<script>(function(){{var a=document.getElementById("gga"),u=document.getElementById("ggu"),s=document.getElementById("ggp"),r=document.getElementById("ggr");function f(){{var v=parseFloat(a.value)||0,m=u.value=="py"?v*{PY}:v,x=s.value.split("|"),n=Math.ceil(m/parseFloat(x[1])*{1 + loss});r.innerHTML="<small>필요량 "+n+"{uw}</small><b>약 "+(n*parseInt(x[0])).toLocaleString()+"원</b>";}}[a,u,s].forEach(function(e){{e.addEventListener("input",f);e.addEventListener("change",f)}});f();}})();</script>"""
        others = "".join(f'<a href="/gagyeok/{g[0]}.html">{E(g[1])}</a>' for g in GG if g[0] != slug)
        title = f"{nm} 가격 — {rows[0][1].split('(')[0]} 기준가 {lo:,}원부터" + (" · 1평에 얼마" if hasA else (" · 1L당 비교" if slug == "oilstain" else " · 1m당 단가" if isLen else " · 1㎡당 비교" if isM2 else " · 종류별 기준가" if isPlain else " · m당 단가"))
        desc = f"{nm} 소매 기준가 {lo:,}원부터({rows[0][1]}). " + (f"1평에 몇 {uw} 드는지, 크기별 예상 금액 계산." if hasA else "판매 단위와 종류별 기준가 정리.") + " 대전 영진목재."
        body = f"""<section class="wrap sec gg"><p class="crumb"><a href="/gagyeok/">자재 가격 가이드</a> › {E(nm)}</p><h1>{E(nm)} 가격</h1>{hero}<p class="glead">{E(lead)}</p>
<h2 class="gt">종류별 가격 <small>옆으로 넘겨 보세요 ›</small></h2><div class="gcs">{"".join(cards)}</div><p class="gs">{E(unitdesc)} · 소매 기준가(부가세 별도) · 필요량은 계산 참고치 · 재단·운임은 매장에서</p>
{exh}<div class="glk"><a href="/jajae/{js}.html">용도·사진</a><a href="/sigongbeop/{sg}.html">시공 방법</a><a href="/calc.html">자재 계산기</a><a href="/price.html">전체 기준가</a></div></section>
<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{faqslide(faq + [(f"{nm} 어디서 사나요?", f"{ADDR} 영진종합목재(월드건축자재) 매장에서 실물을 보고 살 수 있습니다. {HOURS}. 전국 용달 배송도 됩니다.")])}</section>
<section class="wrap sec gg"><h2 class="gt">다른 자재 가격</h2><div class="glk">{others}</div></section>{CTA}"""
        ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]
        ld += prod_ld([{"name": p["name"], "cat": p["cat"], "price": p["price"]} for p, _, _ in rows[:6]], f"{BASE}/gagyeok/{slug}.html")
        if ALLFAQ is not None: ALLFAQ.append(("자재 가격", faq, f"/gagyeok/{slug}.html", nm + " 가격"))
        page(f"gagyeok/{slug}.html", title + " | 대전 영진목재", desc, body, "/price.html", ld)
        pages.append((slug, nm, hl, hv))
    cards = "".join(f'<a class="gi" href="/gagyeok/{s}.html"><b>{E(n)}</b><small>{E(hl)}</small><span>{E(hv)}</span></a>' for s, n, hl, hv in pages)
    page("gagyeok/index.html", "자재 가격 가이드 — 합판·석고보드·데크·사이딩·몰딩·방문·루바 1평에 얼마 | 영진목재",
         "합판·석고보드·단열재·집성판·데크·구조재·사이딩·몰딩·방문·루바·템바보드·필름·오일스테인의 판매 단위와 소매 기준가, 1평 예상 금액.",
         f'<section class="wrap sec gg"><h1>자재 가격 가이드</h1><p class="glead">"1장에 얼마예요?" "1평에 얼마 들어요?" 자재별로 한눈에 정리했습니다. 모두 소매 기준가(부가세 별도)입니다.</p><div class="gig">{cards}</div><div class="glk"><a href="/price.html">전체 기준가</a><a href="/sigongbeop/">자재 시공법</a><a href="/calc.html">자재 계산기</a></div></section>{CTA}', "/price.html")
    return [(s, n) for s, n, *_ in pages]
