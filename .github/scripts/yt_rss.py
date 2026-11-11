#!/usr/bin/env python3
"""유튜브 RSS로 새 영상을 찾아 src/data/new_videos/<id>.tsv 로 만듭니다(1시간마다 Actions에서 실행).
채널: 월드건축자재DIY, 월드도어. 쇼츠 여부는 /shorts/<id> 응답(200=쇼츠, 리다이렉트=일반)으로 판별."""
import os, re, sys, time, urllib.request, urllib.error, xml.etree.ElementTree as ET, calendar
CH = {"UCANbkO40IlYW1d_aiYuHlgA": "월드건축자재", "UCevVBDbNIOWrbX-Yi42dc_A": "월드도어"}
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015", "m": "http://search.yahoo.com/mrss/"}
UA = {"User-Agent": "Mozilla/5.0 (wwood-home yt sync)"}
known = set()
for f in ("src/data/videos.tsv", "src/data/yt_all.tsv"):
    if os.path.exists(f):
        known |= {l.split("\t", 1)[0] for l in open(f, encoding="utf-8")}
os.makedirs("src/data/new_videos", exist_ok=True)
known |= {n[:-4] for n in os.listdir("src/data/new_videos")}

class NoRedir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
op = urllib.request.build_opener(NoRedir)
def is_short(vid):
    try:
        r = op.open(urllib.request.Request(f"https://www.youtube.com/shorts/{vid}", headers=UA), timeout=15); return r.status == 200
    except urllib.error.HTTPError as e: return False if e.code in (301, 302, 303, 307, 308) else None
    except Exception: return None

added = 0
for cid, name in CH.items():
    try:
        x = urllib.request.urlopen(urllib.request.Request(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}", headers=UA), timeout=20).read()
        root = ET.fromstring(x)
    except Exception as e:
        print("feed fail", name, e); continue
    author = root.findtext("a:author/a:name", "", NS) or root.findtext("a:title", "", NS)
    print("feed", name, author, len(root.findall("a:entry", NS)))
    for en in root.findall("a:entry", NS):
        vid = en.findtext("yt:videoId", "", NS)
        if not vid or vid in known: continue
        title = re.sub(r"[\t\r\n]+", " ", en.findtext("a:title", "", NS)).strip()
        pub = en.findtext("a:published", "", NS)[:19]
        ts = calendar.timegm(time.strptime(pub, "%Y-%m-%dT%H:%M:%S")) if pub else int(time.time())
        st = en.find("m:group/m:community/m:statistics", NS)
        views = st.get("views", "0") if st is not None else "0"
        s = is_short(vid)
        if s is None: s = bool(re.search(r"#shorts?", title, re.I))
        open(f"src/data/new_videos/{vid}.tsv", "w", encoding="utf-8").write(f"{vid}\t{'S' if s else 'L'}\t{views}\t{ts}\t{title}\n")
        known.add(vid); added += 1; print("new", vid, "S" if s else "L", title)
print("added", added)
