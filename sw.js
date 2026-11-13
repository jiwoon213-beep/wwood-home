// 영진목재 앱(PWA) — 인터넷이 끊겨도 본 페이지·기준가·재단 미리보기를 볼 수 있게 저장. 항상 새 내용 우선.
const C = "wwood-v3";
const PRE = ["/", "/price.html", "/cut.html", "/calc.html", "/visit.html", "/offline.html", "/assets/style.css", "/assets/site.js", "/assets/icon-192.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(C).then(c => c.addAll(PRE)).catch(() => {})); self.skipWaiting(); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k))))); self.clients.claim(); });
self.addEventListener("fetch", e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== "GET" || u.origin !== location.origin) return;
  e.respondWith(fetch(r).then(res => {
    if (res.ok && (r.mode === "navigate" || u.pathname.startsWith("/assets/"))) { const cp = res.clone(); caches.open(C).then(c => c.put(r, cp)); }
    return res;
  }).catch(() => caches.match(r, { ignoreSearch: true }).then(m => m || (r.mode === "navigate" ? caches.match("/offline.html") : undefined))));
});
