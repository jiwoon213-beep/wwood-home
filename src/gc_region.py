# 현장 근처 찾기 — 지역별 페이지(/geuncheo/<지역>.html)와 내 위치 근처 공식 등록 업체 데이터(/assets/gc/*.json)
# 데이터: data/geuncheo.tsv (gc_convert.py가 행정안전부 인허가데이터 영업중 업체로 매일 갱신)
import os, json, math, re, datetime
I = "g kk n d tt r m b pp s ss  j jj ch k t p h".split(" ")
I = ["g", "kk", "n", "d", "tt", "r", "m", "b", "pp", "s", "ss", "", "j", "jj", "ch", "k", "t", "p", "h"]
V = ["a", "ae", "ya", "yae", "eo", "e", "yeo", "ye", "o", "wa", "wae", "oe", "yo", "u", "wo", "we", "wi", "yu", "eu", "ui", "i"]
F = ["", "k", "k", "k", "n", "n", "n", "t", "l", "k", "m", "l", "l", "l", "p", "l", "m", "p", "p", "t", "t", "ng", "t", "t", "k", "t", "p", "t"]
def rom(s):
    o = ""
    for ch in s:
        c = ord(ch) - 0xAC00
        if 0 <= c < 11172: o += I[c // 588] + V[(c % 588) // 28] + F[c % 28]
        elif ch.isalnum(): o += ch.lower()
        else: o += "-"
    return re.sub(r"-+", "-", o).strip("-")
SD = {"서울특별시": "seoul", "부산광역시": "busan", "대구광역시": "daegu", "인천광역시": "incheon", "전남광주통합특별시": "jeonnam-gwangju", "대전광역시": "daejeon", "울산광역시": "ulsan", "세종특별자치시": "sejong", "경기도": "gyeonggi", "강원특별자치도": "gangwon", "충청북도": "chungbuk", "충청남도": "chungnam", "전북특별자치도": "jeonbuk", "경상북도": "gyeongbuk", "경상남도": "gyeongnam", "제주특별자치도": "jeju"}
SDS = {"서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구", "인천광역시": "인천", "전남광주통합특별시": "광주·전남", "대전광역시": "대전", "울산광역시": "울산", "세종특별자치시": "세종", "경기도": "경기", "강원특별자치도": "강원", "충청북도": "충북", "충청남도": "충남", "전북특별자치도": "전북", "경상북도": "경북", "경상남도": "경남", "제주특별자치도": "제주"}
MAPQ = [("철물점", "철물점"), ("장비 임대", "중장비 임대"), ("공구 렌탈", "공구 렌탈"), ("용달·화물", "용달 화물"), ("건재상", "건재상"), ("전기 자재", "전기자재"), ("설비 자재", "설비자재"), ("기사식당", "기사식당")]
# 인력사무소는 건설·일용직 위주만: 이름에 인력·용역·건설 등이 있고 간병·가사·해외 알선 등은 제외
INC = re.compile(r"인력|용역|건설|인부|노무|일용|잡부|공사|대기소|일꾼|근로")
EXC = re.compile(r"간병|요양|가사|파출|산후|베이비|돌봄|헬퍼|해외|외국|글로벌|국제|global|recruit|병원|의료|간호|유학|모델|연예|캐스팅|웨딩|호텔|선원|헤드헌|서치|에이치알|\bhr\b|다문화|파견|아웃소싱|컨설팅|이민|비자", re.I)
def load(root):
    p = f"{root}/data/geuncheo.tsv"
    if not os.path.exists(p): return []
    R = []
    for ln in open(p, encoding="utf-8"):
        c = ln.rstrip("\n").split("\t")
        if len(c) >= 9 and c[0] in SD and (c[2] != "J" or (INC.search(c[3]) and not EXC.search(c[3]))): R.append(c)
    return R
def slug(sd, sg): return SD[sd] + "-" + rom(sg.replace(" ", ""))
def gen(page, E, CTA, faqslide, TEL, ROOT, OUT, SITEMAP_ADD=None):
    R = load(ROOT)
    if not R: return []
    mt = datetime.date.fromtimestamp(os.path.getmtime(f"{ROOT}/data/geuncheo.tsv")).isoformat()
    G = {}
    for c in R: G.setdefault((c[0], c[1]), []).append(c)
    os.makedirs(f"{OUT}/geuncheo", exist_ok=True); os.makedirs(f"{OUT}/assets/gc", exist_ok=True)
    q = lambda s: __import__("urllib.parse").parse.quote(s)
    def card(c):
        sd, sg, k, nm, ad, ph, la, lo, gb = c[:9]
        mq = q(nm + " " + " ".join(ad.split()[:3]))
        btn = (f'<a class="gcc" href="tel:{ph.replace("-", "")}">📞 {E(ph)}</a>' if ph else '') + f'<a class="gcm" href="https://map.naver.com/p/search/{mq}" target="_blank" rel="noopener">지도·전화번호</a>'
        return f'<li><b>{E(nm)}</b>{(" <small>" + E(gb) + "</small>") if gb else ""}<span>{E(ad)}</span><div>{btn}</div></li>'
    idx = {}
    for (sd, sg), L in sorted(G.items()):
        sl = slug(sd, sg); J = [c for c in L if c[2] == "J"]; W = [c for c in L if c[2] == "W"]
        idx.setdefault(sd, []).append((sg, sl, len(J), len(W)))
        nb = [x for x in G if x[0] == sd and x != (sd, sg)]
        name = f"{SDS[sd]} {sg}"
        mapb = "".join(f'<a href="https://map.naver.com/p/search/{q(name + " " + mq_)}" target="_blank" rel="noopener">{E(n)}</a>' for n, mq_ in MAPQ)
        body = (f'<section class="wrap sec"><p class="crumb"><a href="/">홈</a> › <a href="/geuncheo.html">현장 근처 찾기</a> › <a href="/geuncheo/">지역별</a> › {E(name)}</p>'
                f'<h1>{E(name)} 인력사무소·건설폐기물 처리업체 — 영업 중 {len(J) + len(W)}곳</h1>'
                f'<p class="lead">{E(name)}에 등록된 <b>영업 중</b> 건설·일용직 인력사무소 {len(J)}곳과 건설폐기물 처리업체 {len(W)}곳입니다. 폐업한 곳은 빼고 매일 갱신합니다(기준일 {mt}).</p>'
                f'<div class="gct"><a href="#j">👷 인력사무소 {len(J)}</a><a href="#w">🚛 폐기물 처리 {len(W)}</a><a href="/geuncheo.html">📍 내 위치로 찾기</a></div>'
                f'<h2>{E(name)} 철물점·장비·용달 바로 찾기</h2><div class="gcq">{mapb}</div>'
                + (f'<h2 id="j">{E(name)} 인력사무소 {len(J)}곳</h2><ul class="gcl2">' + "".join(card(c) for c in J) + '</ul>' if J else '')
                + (f'<h2 id="w">{E(name)} 건설폐기물 처리업체 {len(W)}곳</h2><p class="small muted">수집운반업은 폐기물을 실어 가는 곳, 중간처분업은 파쇄·선별 등 처리하는 곳입니다.</p><ul class="gcl2">' + "".join(card(c) for c in W) + '</ul>' if W else '')
                + f'<p class="small muted">출처: 행정안전부 지방행정 인허가데이터(공공데이터포털) — 영업 상태가 ‘영업/정상’인 곳만. 인력사무소는 이름에 인력·용역·건설 등이 들어간 곳만 추렸고 간병·가사·해외 알선 소개소는 뺐습니다. 전화번호가 없는 곳은 ‘지도·전화번호’를 누르면 지도에서 확인할 수 있어요. 방문 전 전화로 영업 여부를 확인하세요.</p>'
                + (f'<h2>{E(SDS[sd])} 다른 지역</h2><div class="gcq">' + "".join(f'<a href="/geuncheo/{slug(*x)}.html">{E(x[1])}</a>' for x in sorted(nb)) + '</div>' if nb else '')
                + f'<div class="gcad"><b>🪵 {E(name)} 현장 목재·합판·석고보드는 영진종합목재</b><span>원하는 크기로 재단해 용달로 현장까지 · 대전 유성대로 44</span><a class="b r" href="tel:{TEL.replace("-", "")}">📞 {TEL}</a></div></section>'
                + '<style>.gct,.gcq{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}.gct a,.gcq a{padding:12px 14px;border-radius:12px;background:#f6f3ee;border:1px solid #e4ded4;font-weight:800;font-size:17px;text-decoration:none;color:#1D1B18}.gcl2{list-style:none;padding:0;display:grid;gap:8px}.gcl2 li{background:#fff;border:1px solid #e4ded4;border-radius:12px;padding:12px}.gcl2 b{font-size:18px}.gcl2 small{color:#c62a1f;font-weight:700}.gcl2 span{display:block;color:#5e574e;font-size:15px;margin:4px 0}.gcl2 div{display:flex;gap:8px;flex-wrap:wrap}.gcc,.gcm{padding:10px 12px;border-radius:10px;font-weight:800;text-decoration:none}.gcc{background:#c62a1f;color:#fff}.gcm{background:#03C75A;color:#fff}.gcad{display:flex;flex-direction:column;gap:8px;background:#fff8e6;border:2px solid #f0c040;border-radius:16px;padding:16px;margin:16px 0}</style>' + CTA)
        fq = [(f"{name} 인력사무소는 어디 있나요?", f"{name}에 등록된 영업 중 유료직업소개소는 {len(J)}곳입니다. 이 페이지에서 주소와 전화번호(등록된 경우)를 볼 수 있습니다."),
              (f"{name} 건설폐기물은 어디에 맡기나요?", f"{name}에 등록된 영업 중 건설폐기물 처리업체는 {len(W)}곳입니다. 수집운반업체는 현장에서 폐기물을 실어 가고, 중간처분업체는 파쇄·선별 처리합니다.")]
        body = body.replace('<div class="gcad">', f'<h2>자주 묻는 질문</h2>{faqslide(fq)}<div class="gcad">', 1)
        # 종류별 단독 페이지(검색어 '○○구 인력사무소', '○○구 건설폐기물' 직접 대응)
        CSS = body[body.find('<style>'):body.find('</style>') + 8]
        for kk, LL, suf, ttl, dsc, h in (("J", J, "inryeok", f"{name} 인력사무소 {len(J)}곳 — 건설 일용직·용역 전화번호(영업 중) | 영진목재",
                                          f"{name} 영업 중 인력사무소(건설·일용직·용역) {len(J)}곳 주소·전화번호. 폐업한 곳은 빼고 매일 갱신. 현장 근처 철물점·장비 임대도 바로 찾기.", f"{name} 인력사무소"),
                                         ("W", W, "pyegimul", f"{name} 건설폐기물 처리업체 {len(W)}곳 — 폐기물 수거·처리 전화번호 | 영진목재",
                                          f"{name} 영업 중 건설폐기물 수집운반·처리업체 {len(W)}곳 주소·전화번호. 폐업한 곳은 빼고 매일 갱신. 인테리어 철거 폐기물 맡길 곳 찾기.", f"{name} 건설폐기물 처리업체")):
            if not LL: continue
            other = (f'<a href="/geuncheo/{sl}-pyegimul.html">🚛 {E(name)} 건설폐기물 처리업체 {len(W)}곳 ›</a>' if kk == "J" and W else (f'<a href="/geuncheo/{sl}-inryeok.html">👷 {E(name)} 인력사무소 {len(J)}곳 ›</a>' if kk == "W" and J else ""))
            sb = (f'<section class="wrap sec"><p class="crumb"><a href="/">홈</a> › <a href="/geuncheo.html">현장 근처 찾기</a> › <a href="/geuncheo/{sl}.html">{E(name)}</a> › {E(h.split(" ", 2)[-1])}</p>'
                  f'<h1>{E(h)} — 영업 중 {len(LL)}곳</h1><p class="lead">{E(name)}에 등록된 <b>영업 중</b> {E(h.split(" ", 2)[-1])} {len(LL)}곳의 주소와 전화번호입니다. 폐업·휴업한 곳은 빼고 매일 갱신합니다(기준일 {mt}).</p>'
                  f'<div class="gct">{other}<a href="/geuncheo.html">📍 내 위치로 찾기</a><a href="/geuncheo/{sl}.html">{E(name)} 전체 보기</a></div>'
                  + ('<p class="small muted">수집운반업은 폐기물을 실어 가는 곳, 중간처분업은 파쇄·선별 등 처리하는 곳입니다.</p>' if kk == "W" else '')
                  + '<ul class="gcl2">' + "".join(card(c) for c in LL) + '</ul>'
                  + f'<h2>{E(name)} 철물점·장비·용달 바로 찾기</h2><div class="gcq">{mapb}</div>'
                  + (f'<h2>{E(SDS[sd])} 다른 지역 {E(h.split(" ", 2)[-1])}</h2><div class="gcq">' + "".join(f'<a href="/geuncheo/{slug(*x)}-{suf}.html">{E(x[1])}</a>' for x in sorted(nb) if any(c[2] == kk for c in G[x])) + '</div>' if nb else '')
                  + f'<h2>자주 묻는 질문</h2>{faqslide([fq[0] if kk == "J" else fq[1], ("영업 중인지 어떻게 확인하나요?", "행정안전부 인허가데이터에서 영업 상태가 영업/정상인 곳만 보여 주고 매일 갱신합니다. 방문 전 전화로 한 번 더 확인하세요.")])}'
                  + f'<div class="gcad"><b>🪵 {E(name)} 현장 목재·합판·석고보드는 영진종합목재</b><span>원하는 크기로 재단해 용달로 현장까지 · 대전 유성대로 44</span><a class="b r" href="tel:{TEL.replace("-", "")}">📞 {TEL}</a></div></section>' + CSS + CTA)
            page(f"geuncheo/{sl}-{suf}.html", ttl, dsc, sb)
        body = body.replace(f'<a href="#j">👷 인력사무소 {len(J)}</a>', f'<a href="/geuncheo/{sl}-inryeok.html">👷 인력사무소 {len(J)}</a>' if J else '', 1).replace(f'<a href="#w">🚛 폐기물 처리 {len(W)}</a>', f'<a href="/geuncheo/{sl}-pyegimul.html">🚛 폐기물 처리 {len(W)}</a>' if W else '', 1)
        page(f"geuncheo/{sl}.html", f"{name} 인력사무소·건설폐기물 처리업체 {len(J) + len(W)}곳 — 전화·주소(영업 중) | 영진목재",
             f"{name} 영업 중 인력사무소 {len(J)}곳, 건설폐기물 처리업체 {len(W)}곳 주소·전화번호. 철물점·장비 임대·용달도 바로 찾기. 매일 갱신.", body)
    # 지역 목록
    lb = '<section class="wrap sec"><p class="crumb"><a href="/">홈</a> › <a href="/geuncheo.html">현장 근처 찾기</a> › 지역별</p><h1>전국 지역별 인력사무소·건설폐기물 처리업체</h1><p class="lead">시·군·구를 누르면 영업 중인 인력사무소와 건설폐기물 처리업체 주소·전화번호가 나옵니다. 매일 갱신(기준일 ' + mt + ').</p>'
    for sd in SD:
        if sd not in idx: continue
        lb += f'<h2>{E(SDS[sd])}</h2><div class="gcq">' + "".join(f'<a href="/geuncheo/{sl}.html">{E(sg)} <small>{j + w}</small></a>' for sg, sl, j, w in idx[sd]) + '</div>'
    lb += '<style>.gcq{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}.gcq a{padding:10px 12px;border-radius:12px;background:#f6f3ee;border:1px solid #e4ded4;font-weight:800;text-decoration:none;color:#1D1B18}.gcq small{color:#5e574e;font-weight:500}</style></section>' + CTA
    page("geuncheo/index.html", "전국 인력사무소·건설폐기물 처리업체 지역별 목록 — 영업 중만, 매일 갱신 | 영진목재",
         f"전국 시·군·구별 영업 중 인력사무소와 건설폐기물 처리업체 {len(R):,}곳 주소·전화번호. 폐업한 곳은 빼고 매일 갱신.", lb)
    # 내 위치 근처용 시도별 데이터
    cent = {}
    for sd in SD:
        P = [c for c in R if c[0] == sd and c[6]]
        if not P: continue
        json.dump([[c[2], c[3], c[4], c[5], float(c[6]), float(c[7]), c[8]] for c in P], open(f"{OUT}/assets/gc/{SD[sd]}.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        cent[SD[sd]] = [round(sum(float(c[6]) for c in P) / len(P), 3), round(sum(float(c[7]) for c in P) / len(P), 3)]
    json.dump({"d": mt, "c": cent}, open(f"{OUT}/assets/gc/index.json", "w"), separators=(",", ":"))
    return mt
