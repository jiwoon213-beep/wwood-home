/* 단지별 추정 평면도 — 그 단지의 전용면적·준공연도·복도/계단식으로 그때그때 그림 (영진종합목재) */
(function () {
  var MK = {1: ["현관 중문", "/sigongbeop/jungmun.html"], 2: ["방문·문틀 교체", "/sigongbeop/munteul-gyoche.html"], 3: ["걸레받이·몰딩", "/sigongbeop/molding-georebatgi.html"],
    4: ["거실 아트월", "/sigongbeop/tempa-byeok.html"], 5: ["주방 상부장·필름", "/mandeul/sangbujang.html"], 6: ["욕실 실리콘·타일", "/sigongbeop/silicone-julnun.html"],
    7: ["베란다 선반·수납", "/mandeul/beranda.html"], 8: ["바닥(강마루·데코타일)", "/sigongbeop/gangmaru.html"], 9: ["붙박이·드레스룸 수납", "/mandeul/chaekjang.html"], 10: ["신발장", "/mandeul/sinbaljang.html"]};
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]; }); }

  function spec(A, Y, hall) {
    var old = Y && Y < 1998, mid = Y && Y < 2008;
    var B = A < 50 ? 2 : old ? 2 : mid ? 3 : (A >= 59 ? 4 : 3);
    if (A >= 96 && B < 3) B = 3;
    var R = A < 50 ? 1 : A < 66 ? (old ? 2 : 3) : A < 96 ? 3 : A < 135 ? 4 : 5;
    if (B - 1 > R) B = R + 1;
    var bath = (A >= 59 && !(Y && Y < 1993)) || A >= 85 ? 2 : 1;
    var corridor = /복도/.test(hall || "");
    var ext = Y && Y >= 2006;
    return {B: B, R: R, bath: bath, corridor: corridor, ext: ext, old: old};
  }

  function draw(A, Y, hall, name) {
    var s = spec(A, Y, hall);
    var k = Math.max(0.62, Math.min(1, Math.sqrt(A / 135)));
    var W = 1000, bw = 900 * k, bh = 520 * k, x0 = (W - bw) / 2, y0 = 130, H = Math.round(y0 + bh + 50);
    var balH = bh * 0.13, frontH = bh * 0.5, backH = bh - balH - frontH;
    var o = [], marks = [], t = [];
    function rect(x, y, w, h, fill, sw) { o.push('<rect x="' + x.toFixed(1) + '" y="' + y.toFixed(1) + '" width="' + w.toFixed(1) + '" height="' + h.toFixed(1) + '" fill="' + fill + '" stroke="#3a342c" stroke-width="' + (sw || 6) + '"/>'); }
    function lab(x, y, w, h, n) { if (n) t.push('<text x="' + (x + w / 2).toFixed(1) + '" y="' + (y + h / 2 + 6).toFixed(1) + '" text-anchor="middle" font-size="' + (w > 120 ? 18 : 14) + '" font-weight="700" fill="#6b6257">' + esc(n) + '</text>'); }
    function door(x, y) { o.push('<line x1="' + (x - 26) + '" y1="' + y + '" x2="' + (x + 26) + '" y2="' + y + '" stroke="#fbf7ef" stroke-width="9"/><path d="M' + (x - 26) + ' ' + y + ' A52 52 0 0 1 ' + (x + 26) + ' ' + (y - 46) + '" fill="none" stroke="#b9ad9b" stroke-width="2"/>'); }
    function mk(n, x, y) { marks.push([n, x, y]); }
    // 앞줄(남향): 방들 · 거실 · 안방
    var fr = [];
    for (var i = 0; i < s.B - 2; i++) fr.push(["방 " + (i + 2), 1]);
    fr.push([A < 50 ? "거실 겸 방" : "거실", s.B <= 2 ? 1.5 : 1.35]);
    fr.push(["안방", 1.15]);
    if (A < 50) fr = [["거실 겸 방", 1.3], ["방", 1]];
    var tw = fr.reduce(function (a, b) { return a + b[1]; }, 0), x = x0, fy = y0 + backH, livX = 0, livW = 0, roomX = -1, anX = 0, anW = 0;
    fr.forEach(function (f, j) {
      var w = bw * f[1] / tw; rect(x, fy, w, frontH, "#fbf7ef"); lab(x, fy, w, frontH, f[0]);
      if (/거실/.test(f[0])) { livX = x; livW = w; } else if (f[0] === "안방" || (A < 50 && j === 1)) { anX = x; anW = w; } else if (roomX < 0) roomX = x + w / 2;
      x += w;
    });
    // 뒷줄: 현관 · 욕실 · 나머지 방 · 주방 · (안방 욕실·드레스룸)
    var extra = s.R - (A < 50 ? 1 : (s.B - 1));
    var bk = [["현관", 0.9, "#fbf7ef"], [s.bath > 1 ? "공용 욕실" : "욕실", 0.9, "#e9f1f4"]];
    for (i = 0; i < extra; i++) bk.push(["방 " + (s.B + i), 1.25, "#fbf7ef"]);
    bk.push([A < 50 ? "주방" : "주방·식당", A < 50 ? 1.2 : 2.1, "#f5efe3"]);
    if (A >= 50) { if (s.bath > 1) bk.push(["안방 욕실", 0.85, "#e9f1f4"]); bk.push([A >= 85 ? "드레스룸" : "수납", 0.75, "#fbf7ef"]); }
    var bt = bk.reduce(function (a, b) { return a + b[1]; }, 0); x = x0;
    var pos = {};
    bk.forEach(function (b) { var w = bw * b[1] / bt; rect(x, y0, w, backH, b[2]); lab(x, y0, w, backH, b[0]); pos[b[0].split(" ")[0] === "방" ? b[0] : b[0].replace(/·.*/, "").replace(/^공용 /, "")] = [x, w]; door(x + w / 2, y0 + backH); x += w; });
    // 발코니
    rect(x0, y0 + backH + frontH, bw, balH, "#eef4f7", 3);
    lab(x0, y0 + backH + frontH, bw, balH, s.ext ? "발코니 (확장한 집 많음)" : "발코니");
    // 복도식/계단식
    if (s.corridor) { o.push('<rect x="' + x0 + '" y="' + (y0 - 38) + '" width="' + bw + '" height="30" fill="#efebe4"/>'); t.push('<text x="' + (x0 + 10) + '" y="' + (y0 - 17) + '" font-size="14" fill="#8a8278">공용 복도 (복도식)</text>'); }
    else { o.push('<rect x="' + (x0 + 10) + '" y="' + (y0 - 44) + '" width="110" height="36" fill="#efebe4" stroke="#c9bfb0"/>'); t.push('<text x="' + (x0 + 65) + '" y="' + (y0 - 20) + '" text-anchor="middle" font-size="14" fill="#8a8278">계단실·승강기</text>'); }
    var hx = pos["현관"], ux = pos["욕실"] || pos["공용 욕실"], kx = pos["주방"], dx = pos["드레스룸"] || pos["수납"];
    if (hx) { mk(1, hx[0] + 22, y0 + 26); mk(10, hx[0] + 22, y0 + backH - 26); }
    if (ux) mk(6, ux[0] + ux[1] - 22, y0 + 26);
    if (kx) mk(5, kx[0] + 24, y0 + 26);
    if (dx) mk(9, dx[0] + dx[1] / 2, y0 + 26);
    mk(4, livX + 22, fy + frontH / 2 - 40); mk(3, livX + livW - 22, fy + frontH - 24); mk(8, livX + livW / 2, fy + frontH / 2 + 40);
    if (roomX > 0) mk(2, roomX, fy + 26); else mk(2, anX + anW / 2, fy + 26);
    mk(7, x0 + bw - 30, y0 + backH + frontH + balH / 2);
    var m = marks.map(function (q) { return '<a href="' + MK[q[0]][1] + '"><title>' + esc(MK[q[0]][0]) + '</title><circle cx="' + q[1].toFixed(1) + '" cy="' + q[2].toFixed(1) + '" r="16" fill="#b06a2c" stroke="#fff" stroke-width="3"/><text x="' + q[1].toFixed(1) + '" y="' + (q[2] + 6).toFixed(1) + '" text-anchor="middle" font-size="16" font-weight="900" fill="#fff">' + q[0] + '</text></a>'; });
    var head = '<text x="30" y="40" font-size="24" font-weight="900" fill="#1d1b18">' + esc(name) + ' · 전용 ' + A + '㎡</text>' +
      '<text x="30" y="66" font-size="15" fill="#8a8278">방 ' + s.R + ' · 욕실 ' + s.bath + ' · ' + s.B + '베이 · ' + (Y ? Y + '년 · ' : '') + (s.corridor ? '복도식' : '계단식') + ' (자료로 추정)</text>';
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + W + ' ' + H + '" font-family="Noto Sans KR,Apple SD Gothic Neo,Malgun Gothic,sans-serif"><rect width="' + W + '" height="' + H + '" fill="#fff"/>' + head + o.join("") + t.join("") + m.join("") +
      '<text x="' + (W - 20) + '" y="' + (H - 12) + '" text-anchor="end" font-size="13" fill="#9a9086">단지 공개자료(면적·연식·복도유형)로 그린 추정 평면 · 실제 구조와 다를 수 있음 · 영진종합목재</text></svg>';
  }

  function legend() {
    return '<ol class="apleg">' + Object.keys(MK).map(function (n) { return '<li value="' + n + '"><a href="' + MK[n][1] + '">' + MK[n][0] + '</a></li>'; }).join("") + "</ol>";
  }

  function mount(el) {
    if (el.dataset.done) return; el.dataset.done = 1;
    var ar = el.dataset.a.split(",").map(function (p) { var q = p.split(":"); return [+q[0], +q[1]]; }).filter(function (q) { return q[0] > 0; });
    if (!ar.length) return;
    var Y = +el.dataset.y || 0, hall = el.dataset.h || "", nm = el.dataset.n || "";
    var cur = ar.slice().sort(function (a, b) { return b[1] - a[1]; })[0][0];
    var tabs = ar.length > 1 ? '<div class="aptab">' + ar.map(function (q) { return '<button type="button" data-a="' + q[0] + '">' + q[0] + '㎡ <small>' + q[1].toLocaleString() + '세대</small></button>'; }).join("") + "</div>" : "";
    el.innerHTML = tabs + '<div class="apsv"></div><details class="aplg"><summary>번호 설명 (누르면 시공법)</summary>' + legend() + "</details>";
    function show(a) { el.querySelector(".apsv").innerHTML = draw(a, Y, hall, nm); el.querySelectorAll(".aptab button").forEach(function (b) { b.classList.toggle("on", +b.dataset.a === a); }); }
    el.addEventListener("click", function (e) { var b = e.target.closest(".aptab button"); if (b) show(+b.dataset.a); });
    show(cur);
  }
  var L = document.querySelectorAll(".apfp");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { mount(e.target); io.unobserve(e.target); } }); }, {rootMargin: "400px"});
    L.forEach(function (el) { io.observe(el); });
  } else L.forEach(mount);
  window.addEventListener("hashchange", function () { var t = document.getElementById(location.hash.slice(1)); if (t) { var f = t.querySelector(".apfp"); if (f) mount(f); } });
})();
