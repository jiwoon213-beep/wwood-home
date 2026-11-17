# K-apt '관리비공개의무단지 기본정보'(매주 금요일) → 대전·세종 아파트 단지 목록 src/data/apt.tsv
import re, sys, io, html, requests, openpyxl
U = "https://www.k-apt.go.kr"
s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0 (wwood.co.kr apt list)"
h0 = s.get(U + "/web/board/webReference/boardList.do?boardType=03&scodeT=04", timeout=60).text
tok = re.search(r'name="_csrf" content="([^"]+)"', h0) or re.search(r'name="_csrf"[^>]*value="([^"]+)"', h0)
seq = None
for sc in ("01", "04"):
    if not tok: break
    h = s.post(U + "/web/board/webReference/boardListAjax.do", data={"scode": sc, "boardType": "03", "pageNo": "1", "stype": "", "keyword": "", "_csrf": tok.group(1)}, headers={"X-CSRF-TOKEN": tok.group(1), "X-Requested-With": "XMLHttpRequest"}, timeout=60).text
    for m in re.finditer(r"fileDown\('(\d+)','03','1'\)", h):
        if "기본정보" in h[max(0, m.start() - 1500):m.start() + 200]: seq = m.group(1); break
    if seq: break
print("html", len(h0), bool(tok), seq)
if not (tok and seq): print("목록 못 읽음", bool(tok), seq); sys.exit(0)
r = s.post(U + f"/board/getFileDownload.do?seq={seq}&boardType=03", data={"_csrf": tok.group(1), "fileNum": "1"}, headers={"X-CSRF-TOKEN": tok.group(1)}, timeout=180)
if len(r.content) < 1_000_000: print("파일 작음", len(r.content)); sys.exit(0)
wb = openpyxl.load_workbook(io.BytesIO(r.content), read_only=True)
_ws = wb.active; _ws.reset_dimensions()
rows = [tuple(html.unescape(html.unescape(c)).strip() if isinstance(c, str) else c for c in x) for x in _ws.iter_rows(values_only=True)]
print("행", len(rows), [str(x)[:120] for x in rows[:3]])
hi = next(i for i, x in enumerate(rows) if x and "단지명" in x); H = list(rows[hi])
SD = {"서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구", "인천광역시": "인천", "광주광역시": "광주", "대전광역시": "대전", "울산광역시": "울산", "세종특별자치시": "세종", "경기도": "경기", "강원도": "강원", "강원특별자치도": "강원", "충청북도": "충북", "충청남도": "충남", "전라북도": "전북", "전북특별자치도": "전북", "전라남도": "전남", "경상북도": "경북", "경상남도": "경남", "제주특별자치도": "제주"}
W = ["시도", "시군구", "동리", "단지코드", "단지명", "단지분류", "도로명주소", "사용승인일", "동수", "세대수", "난방방식", "복도유형", "최고층수", "시공사"]
I = [H.index(w) for w in W]
out = []
for x in rows[hi + 1:]:
    if not x or not x[I[0]]: continue
    v = ["" if x[i] is None else str(x[i]).strip() for i in I]
    if v[5] not in ("아파트", "주상복합"): continue
    try: n = int(float(v[9]))
    except Exception: continue
    if n < 100: continue
    v[0] = SD.get(v[0], v[0][:2]); v[5] = "주" if v[5] == "주상복합" else "아"; v[6] = re.sub(r"^\S+(특별시|광역시|특별자치시|특별자치도|도)\s+", "", v[6]); v[7] = v[7][:6]; v[9] = str(n)
    v[8] = str(int(float(v[8]))) if re.match(r"^[\d.]+$", v[8] or "") else v[8]; v[12] = str(int(float(v[12]))) if re.match(r"^[\d.]+$", v[12] or "") else v[12]
    out.append("\t".join(re.sub(r"[\t\n]", " ", t) for t in v))
if len(out) < 8000: print("행 적음", len(out)); sys.exit(0)
open("src/data/apt.tsv", "w", encoding="utf-8").write("\t".join(W) + "\n" + "\n".join(out) + "\n")
print("단지", len(out), "seq", seq)
