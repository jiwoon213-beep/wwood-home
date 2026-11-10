# IndexNow: 도매몰 wwood.kr 사이트맵 주소를 네이버·빙에 알림 (키 파일은 wwood.kr/<KEY>.txt 에 FTP로 올려 둠)
import json, re, urllib.request
KEY = "b4237bce57cfb60c93b64e5203857f41"; HOST = "wwood.kr"; BASE = "https://" + HOST
try:
    r = urllib.request.urlopen(urllib.request.Request(BASE + "/sitemap.xml", headers={"User-Agent": "Mozilla/5.0"}), timeout=60)
    xml = r.read().decode("utf-8", "replace"); print("wwood.kr sitemap", r.status, len(xml), xml[:120].replace("\n", " "))
except Exception as e:
    xml = ""; print("wwood.kr sitemap ERR", getattr(e, "code", ""), str(e)[:200])
try:
    k = urllib.request.urlopen(urllib.request.Request(f"{BASE}/{KEY}.txt", headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode()
    print("key file:", k.strip() == KEY)
except Exception as e:
    print("key file ERR", str(e)[:200])
if "<loc>" not in xml:
    xml = open("wwoodkr-sitemap.xml", encoding="utf-8").read()  # 같은 목록 사본(www.wwood.co.kr 에 올려 둔 것)
urls = sorted(set(u.replace("&amp;", "&") for u in re.findall(r"<loc>([^<]+)</loc>", xml)))[:10000]
print(len(urls), "URLs")
if not urls:
    raise SystemExit(0)
body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"{BASE}/{KEY}.txt", "urlList": urls}).encode()
for ep in ["https://searchadvisor.naver.com/indexnow", "https://api.indexnow.org/indexnow"]:
    try:
        r = urllib.request.urlopen(urllib.request.Request(ep, body, {"Content-Type": "application/json; charset=utf-8"}), timeout=60)
        print(ep, r.status)
    except Exception as e:
        print(ep, "ERR", getattr(e, "code", ""), str(e)[:300])
