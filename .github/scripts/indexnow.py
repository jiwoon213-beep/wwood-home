# IndexNow: 바뀐 페이지를 네이버·빙에 바로 알림
import json, re, subprocess, sys, urllib.request
KEY = "b4237bce57cfb60c93b64e5203857f41"; HOST = "www.wwood.co.kr"; BASE = "https://" + HOST
mode = sys.argv[1] if len(sys.argv) > 1 else ""
if mode == "all":
    urls = re.findall(r"<loc>([^<]+)</loc>", open("sitemap.xml").read())
else:
    try:
        files = subprocess.check_output(["git", "diff", "--name-only", mode, "HEAD"], text=True).split()
    except Exception:
        files = []
    urls = []
    for f in files:
        if not f.endswith(".html") or f.startswith(("src/", ".github/")) or f.startswith(("google", "naver")):
            continue
        u = "/" + f
        u = u[:-10] if u.endswith("/index.html") else u
        urls.append(BASE + (u or "/"))
urls = sorted(set(urls))[:10000]
print(len(urls), "URLs")
if not urls:
    sys.exit(0)
body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"{BASE}/{KEY}.txt", "urlList": urls}).encode()
for ep in ["https://searchadvisor.naver.com/indexnow", "https://api.indexnow.org/indexnow"]:
    try:
        r = urllib.request.urlopen(urllib.request.Request(ep, body, {"Content-Type": "application/json; charset=utf-8"}), timeout=60)
        print(ep, r.status)
    except Exception as e:
        print(ep, "ERR", getattr(e, "code", ""), str(e)[:200])
