# 현장 근처 찾기 데이터 변환: localdata(행정안전부 인허가) 영업중 유료직업소개소(J)·건설폐기물처리업(W)
# 입력 raw.tsv: 종류\t이름\t주소\t전화\tX\tY\t인허가일자[\t처리업구분]  (좌표 EPSG:5174 Bessel 중부원점TM)
# 출력 data/geuncheo.tsv: 시도\t시군구\t종류\t이름\t주소\t전화\t위도\t경도\t구분
import sys, math, os, re
a = 6377397.155; f = 1 / 299.1528128; e2 = 2 * f - f * f
lat0 = math.radians(38.0); lon0 = math.radians(127.0028902777778); k0 = 1.0; FE = 200000.0; FN = 500000.0
def M(p):
    e4, e6 = e2 * e2, e2 ** 3
    return a * ((1 - e2 / 4 - 3 * e4 / 64 - 5 * e6 / 256) * p - (3 * e2 / 8 + 3 * e4 / 32 + 45 * e6 / 1024) * math.sin(2 * p) + (15 * e4 / 256 + 45 * e6 / 1024) * math.sin(4 * p) - (35 * e6 / 3072) * math.sin(6 * p))
M0 = M(lat0)
def tm_inv(x, y):
    m = M0 + (y - FN) / k0
    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    mu = m / (a * (1 - e2 / 4 - 3 * e2 ** 2 / 64 - 5 * e2 ** 3 / 256))
    p1 = mu + (3 * e1 / 2 - 27 * e1 ** 3 / 32) * math.sin(2 * mu) + (21 * e1 ** 2 / 16 - 55 * e1 ** 4 / 32) * math.sin(4 * mu) + (151 * e1 ** 3 / 96) * math.sin(6 * mu) + (1097 * e1 ** 4 / 512) * math.sin(8 * mu)
    ep2 = e2 / (1 - e2); C1 = ep2 * math.cos(p1) ** 2; T1 = math.tan(p1) ** 2
    N1 = a / math.sqrt(1 - e2 * math.sin(p1) ** 2); R1 = a * (1 - e2) / (1 - e2 * math.sin(p1) ** 2) ** 1.5
    D = (x - FE) / (N1 * k0)
    lat = p1 - (N1 * math.tan(p1) / R1) * (D * D / 2 - (5 + 3 * T1 + 10 * C1 - 4 * C1 * C1 - 9 * ep2) * D ** 4 / 24 + (61 + 90 * T1 + 298 * C1 + 45 * T1 * T1 - 252 * ep2 - 3 * C1 * C1) * D ** 6 / 720)
    lon = lon0 + (D - (1 + 2 * T1 + C1) * D ** 3 / 6 + (5 - 2 * C1 + 28 * T1 - 3 * C1 * C1 + 8 * ep2 + 24 * T1 * T1) * D ** 5 / 120) / math.cos(p1)
    return lat, lon
def bessel_to_wgs(lat, lon):
    N = a / math.sqrt(1 - e2 * math.sin(lat) ** 2)
    X = N * math.cos(lat) * math.cos(lon); Y = N * math.cos(lat) * math.sin(lon); Z = N * (1 - e2) * math.sin(lat)
    tx, ty, tz = -115.80, 474.99, 674.11; s = 6.43e-6
    rx, ry, rz = [math.radians(v / 3600) for v in (1.16, -2.31, -1.63)]
    X2 = tx + (1 + s) * (X - rz * Y + ry * Z); Y2 = ty + (1 + s) * (rz * X + Y - rx * Z); Z2 = tz + (1 + s) * (-ry * X + rx * Y + Z)
    aw = 6378137.0; fw = 1 / 298.257223563; ew = 2 * fw - fw * fw
    p = math.hypot(X2, Y2); lon2 = math.atan2(Y2, X2); lat2 = math.atan2(Z2, p * (1 - ew))
    for _ in range(6):
        Nw = aw / math.sqrt(1 - ew * math.sin(lat2) ** 2); lat2 = math.atan2(Z2 + ew * Nw * math.sin(lat2), p)
    return math.degrees(lat2), math.degrees(lon2)
SIDO = {"강원도": "강원특별자치도", "전라북도": "전북특별자치도", "광주광역시": "전남광주통합특별시", "전라남도": "전남광주통합특별시"}
def tel(t):
    t = re.sub(r"\D", "", t or "")
    if len(t) < 8: return ""
    if t.startswith("02"): return f"02-{t[2:-4]}-{t[-4:]}"
    return f"{t[:3]}-{t[3:-4]}-{t[-4:]}"
def main(src, dst):
    out = []
    for ln in open(src, encoding="utf-8"):
        c = ln.rstrip("\n").split("\t")
        if len(c) < 7: continue
        k, nm, ad, ph, x, y = c[:6]; gb = c[7] if len(c) > 7 else ""
        w = ad.split()
        if len(w) < 2 or not nm: continue
        sd = SIDO.get(w[0], w[0]); sg = w[1]
        if sd == "세종특별자치시": sg = "세종시"  # 세종은 시군구 없이 바로 읍면동·도로명
        elif not re.search(r"[시군구]$", sg): continue
        if sg.endswith("시") and len(w) > 2 and w[2].endswith("구"): sg = sg + " " + w[2]
        la = lo = ""
        try:
            if x.strip() and y.strip():
                p, q = tm_inv(float(x), float(y)); p, q = bessel_to_wgs(p, q)
                if 33 < p < 39 and 124 < q < 132: la, lo = f"{p:.5f}", f"{q:.5f}"
        except Exception: pass
        gb = re.sub(r"\(건설폐기물\)", "", gb).strip()
        out.append("\t".join([sd, sg, k, nm.strip(), ad.strip(), tel(ph), la, lo, gb]))
    out = sorted(set(out))
    if len(out) < 5000: sys.exit(f"too few rows: {len(out)}")  # 데이터 이상 시 덮어쓰지 않음
    open(dst, "w", encoding="utf-8").write("\n".join(out) + "\n"); print(len(out), "rows")
if __name__ == "__main__": main(sys.argv[1], sys.argv[2])
