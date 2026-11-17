# K-apt '관리비공개의무단지 기본정보'(매주 금요일) → 대전·세종 아파트 단지 목록 src/data/apt.tsv
import re, sys, io, requests, openpyxl
U = "https://www.k-apt.go.kr"
s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0 (wwood.co.kr apt list)"
h = s.get(U + "/web/board/webReference/boardView.do?seq=20&boardSecret=0&boardType=03&pageNo=1&keyword=&board_pwd=&scodeT=04", timeout=60).text
tok = re.search(r'name="_csrf"[^>]*value="([^"]+)"', h) or re.search(r'name="_csrf" content="([^"]+)"', h)
seq = None
for m in re.finditer(r"fileDown\('(\d+)','03','1'\)", h):
    if "기본정보" in h[max(0, m.start() - 1500):m.start() + 1500]: seq = m.group(1); break
if not (tok and seq): print("목록 못 읽음", bool(tok), seq); sys.exit(0)
r = s.post(U + f"/board/getFileDownload.do?seq={seq}&boardType=03", data={"_csrf": tok.group(1), "fileNum": "1"}, headers={"X-CSRF-TOKEN": tok.group(1)}, timeout=180)
if len(r.content) < 1_000_000: print("파일 작음", len(r.content)); sys.exit(0)
wb = openpyxl.load_workbook(io.BytesIO(r.content), read_only=True)
rows = list(wb.active.iter_rows(values_only=True))
hi = next(i for i, x in enumerate(rows) if x and "단지명" in x); H = list(rows[hi])
W = ["시도", "시군구", "동리", "단지코드", "단지명", "단지분류", "도로명주소", "사용승인일", "동수", "세대수", "난방방식", "복도유형", "최고층수", "시공사"]
I = [H.index(w) for w in W]
out = []
for x in rows[hi + 1:]:
    if not x or x[I[0]] not in ("대전광역시", "세종특별자치시"): continue
    v = ["" if x[i] is None else str(x[i]).strip() for i in I]
    if v[5] not in ("아파트", "주상복합"): continue
    try: n = int(float(v[9]))
    except Exception: continue
    if n < 100: continue
    v[0] = v[0][:2]; v[5] = "주" if v[5] == "주상복합" else "아"; v[6] = re.sub(r"^(대전광역시|세종특별자치시)\s*", "", v[6]); v[7] = v[7][:6]; v[9] = str(n)
    v[8] = str(int(float(v[8]))) if re.match(r"^[\d.]+$", v[8] or "") else v[8]; v[12] = str(int(float(v[12]))) if re.match(r"^[\d.]+$", v[12] or "") else v[12]
    out.append("\t".join(re.sub(r"[\t\n]", " ", t) for t in v))
if len(out) < 500: print("행 적음", len(out)); sys.exit(0)
open("src/data/apt.tsv", "w", encoding="utf-8").write("\t".join(W) + "\n" + "\n".join(out) + "\n")
print("단지", len(out), "seq", seq)
