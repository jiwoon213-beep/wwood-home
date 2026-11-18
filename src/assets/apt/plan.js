/* 단지별 추정 평면도 — 그 단지의 전용면적·준공연도·복도/계단식·주상복합·층수로 그때그때 그림 (영진종합목재 직접 작도, 실제 도면 아님) */
(function () {
  var MK = {1: ["현관 중문", "/sigongbeop/jungmun.html"], 2: ["방문·문틀 교체", "/sigongbeop/munteul-gyoche.html"], 3: ["걸레받이·몰딩", "/sigongbeop/molding-georebatgi.html"],
    4: ["거실 아트월", "/sigongbeop/tempa-byeok.html"], 5: ["주방 상부장·필름", "/mandeul/sangbujang.html"], 6: ["욕실 실리콘·타일", "/sigongbeop/silicone-julnun.html"],
    7: ["베란다 선반·수납", "/mandeul/beranda.html"], 8: ["바닥(강마루·데코타일)", "/sigongbeop/gangmaru.html"], 9: ["붙박이·드레스룸 수납", "/mandeul/chaekjang.html"], 10: ["신발장", "/mandeul/sinbaljang.html"]};
  var C = {room: "#fbf7ef", wet: "#e9f1f4", kit: "#f5efe3", bal: "#eef4f7", etc: "#f3efe8"};
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]; }); }

  function spec(A, Y, hall, typ, fl) {
    var old = Y && Y < 1998, mid = Y && Y < 2008;
    var B = A < 50 ? 2 : old ? 2 : mid ? 3 : (A >= 59 ? 4 : 3);
    if (A >= 96 && B < 3) B = 3;
    var R = A < 50 ? 1 : A < 66 ? (old ? 2 : 3) : A < 96 ? 3 : A < 135 ? 4 : 5;
    if (B - 1 > R) B = R + 1;
    return {B: B, R: R, bath: ((A >= 59 && !(Y && Y < 1993)) || A >= 85) ? 2 : 1,
      corridor: /복도/.test(hall || ""), tower: A >= 59 && (/주/.test(typ || "") || (Y >= 2005 && +fl >= 30)),
      ext: Y >= 2006, ac: Y >= 2010, alpha: Y >= 2015 && A >= 74, pantry: Y >= 2015 && A >= 84, util: A >= 59};
  }

  function Canvas() { this.o = []; this.t = []; this.m = []; this.pos = {}; }
  Canvas.prototype.box = function (x, y, w, h, name, kind, sw) {
    this.o.push('<rect x="' + x.toFixed(1) + '" y="' + y.toFixed(1) + '" width="' + w.toFixed(1) + '" height="' + h.toFixed(1) + '" fill="' + (C[kind] || C.room) + '" stroke="#3a342c" stroke-width="' + (sw || 6) + '"/>');
    if (name) {
      var fs = w > 130 && h > 60 ? 18 : 13;
      this.t.push('<text x="' + (x + w / 2).toFixed(1) + '" y="' + (y + h / 2 + 6).toFixed(1) + '" text-anchor="middle" font-size="' + fs + '" font-weight="700" fill="#6b6257">' + esc(name) + '</text>');
      this.pos[name] = [x, y, w, h];
    }
  };
  Canvas.prototype.door = function (x, y) {
    this.o.push('<line x1="' + (x - 24) + '" y1="' + y + '" x2="' + (x + 24) + '" y2="' + y + '" stroke="#fbf7ef" stroke-width="9"/><path d="M' + (x - 24) + ' ' + y + ' A48 48 0 0 1 ' + (x + 24) + ' ' + (y - 42) + '" fill="none" stroke="#b9ad9b" stroke-width="2"/>');
  };
  Canvas.prototype.win = function (x1, y1, x2, y2) { this.o.push('<line x1="' + x1.toFixed(1) + '" y1="' + y1.toFixed(1) + '" x2="' + x2.toFixed(1) + '" y2="' + y2.toFixed(1) + '" stroke="#7fb3cf" stroke-width="4"/>'); };
  Canvas.prototype.mk = function (n, name, dx, dy) { var p = this.pos[name]; if (p) this.m.push([n, p[0] + (dx < 0 ? p[2] + dx : dx), p[1] + (dy < 0 ? p[3] + dy : dy)]); };

  function flat(c, A, s, x0, y0, bw, bh) {
    var balH = bh * (s.ext ? 0.06 : 0.13), frontH = bh * 0.5, backH = bh - balH - frontH, fy = y0 + backH;
    var fr = [];
    if (A < 50) fr = [["거실 겸 방", 1.3], ["방", 1]];
    else { for (var i = 0; i < s.B - 2; i++) fr.push(["방 " + (i + 2), 1]); fr.push(["거실", s.B <= 2 ? 1.5 : 1.35]); fr.push(["안방", 1.15]); }
    var tw = fr.reduce(function (a, b) { return a + b[1]; }, 0), x = x0, firstRoom = null;
    fr.forEach(function (f) { var w = bw * f[1] / tw; c.box(x, fy, w, frontH, f[0]); c.win(x + 8, fy + frontH, x + w - 8, fy + frontH); if (!firstRoom && /^방/.test(f[0])) firstRoom = f[0]; x += w; });
    var extra = s.R - (A < 50 ? 1 : (s.B - 1));
    var bk = [["현관", 0.9], [s.bath > 1 ? "공용 욕실" : "욕실", 0.9, "wet"]];
    for (var j = 0; j < extra; j++) bk.push(["방 " + (s.B + j), 1.25]);
    if (s.alpha) bk.push(["알파룸", 0.8]);
    bk.push([A < 50 ? "주방" : "주방·식당", A < 50 ? 1.2 : 2.0, "kit"]);
    if (s.pantry) bk.push(["팬트리", 0.45, "etc"]);
    if (s.util) bk.push(["다용도실", 0.55, "etc"]);
    if (A >= 50) { if (s.bath > 1) bk.push(["안방 욕실", 0.8, "wet"]); bk.push([A >= 85 ? "드레스룸" : "수납", 0.7]); }
    if (s.ac) bk.push(["실외기실", 0.35, "etc"]);
    var bt = bk.reduce(function (a, b) { return a + b[1]; }, 0); x = x0;
    bk.forEach(function (b) { var w = bw * b[1] / bt; c.box(x, y0, w, backH, b[0], b[2]); if (!/실외기|다용도|팬트리/.test(b[0])) c.door(x + w / 2, y0 + backH); x += w; });
    c.box(x0, fy + frontH, bw, balH, s.ext ? "발코니 확장(일부 남음)" : "발코니", "bal", 3);
    var lv = c.pos["거실"] ? "거실" : "거실 겸 방";
    c.mk(1, "현관", 22, 26); c.mk(10, "현관", 22, -26); c.mk(6, c.pos["공용 욕실"] ? "공용 욕실" : "욕실", -22, 26);
    c.mk(5, c.pos["주방·식당"] ? "주방·식당" : "주방", 24, 26); c.mk(9, c.pos["드레스룸"] ? "드레스룸" : "수납", 22, -26);
    c.mk(4, lv, 22, 40); c.mk(3, lv, -22, -24); c.mk(8, lv, 70, -60); c.mk(2, firstRoom || "안방", 30, 26);
    c.m.push([7, x0 + bw - 30, fy + frontH + balH / 2]);
    return y0 + bh;
  }

  function tower(c, A, s, x0, y0, bw, bh) {
    // 타워형: 거실이 모서리(아래·오른쪽 두 면에 창), 방들이 두 면을 둘러쌈
    var W = bw * 0.86, H = bh * 1.08; x0 += (bw - W) / 2;
    var cR = W * 0.44, cM = W * 0.24, cL = W - cR - cM;
    var rT = H * 0.24, rM = H * 0.3, rB = H - rT - rM;
    var xL = x0, xM = x0 + cL, xR = x0 + cL + cM, yT = y0, yM = y0 + rT, yB = y0 + rT + rM;
    c.box(xR, yB, cR, rB, "거실");
    c.box(xR, yM, cR, rM, "주방·식당", "kit");
    if (s.ac || s.util) { c.box(xR, yT, cR * 0.55, rT, s.util ? "다용도실" : "실외기실", "etc"); c.box(xR + cR * 0.55, yT, cR * 0.45, rT, s.alpha ? "알파룸" : (s.pantry ? "팬트리" : "수납"), s.alpha ? "room" : "etc"); }
    else c.box(xR, yT, cR, rT, "수납", "etc");
    c.box(xL, yB, cL, rB, "안방");
    c.box(xM, yB, cM, rB, "방 2");
    if (s.bath > 1) { c.box(xL, yM, cL * 0.55, rM, "안방 욕실", "wet"); c.box(xL + cL * 0.55, yM, cL * 0.45, rM, "드레스룸"); }
    else c.box(xL, yM, cL, rM, "드레스룸");
    c.box(xM, yM, cM, rM, s.bath > 1 ? "공용 욕실" : "욕실", "wet");
    if (s.R >= 4) { c.box(xL, yT, cL * 0.5, rT, "방 3"); c.box(xL + cL * 0.5, yT, cL * 0.5, rT, "방 4"); }
    else c.box(xL, yT, cL, rT, s.R >= 3 ? "방 3" : "수납");
    c.box(xM, yT, cM, rT, "현관");
    c.win(xR + 8, y0 + H, xR + cR - 8, y0 + H); c.win(xR + cR, yB + 8, xR + cR, yB + rB - 8); c.win(xR + cR, yM + 8, xR + cR, yM + rM - 8);
    c.win(xL + 8, y0 + H, xL + cL - 8, y0 + H); c.win(xM + 8, y0 + H, xM + cM - 8, y0 + H); c.win(xL, yT + 8, xL, yT + rT - 8);
    c.door(xM + cM / 2, yM); c.door(xL + cL / 2, yB); c.door(xM + cM / 2, yB);
    var bal = bh * (s.ext ? 0.05 : 0.1);
    c.box(xL, y0 + H, W, bal, s.ext ? "확장(창 앞 일부)" : "발코니", "bal", 3);
    c.mk(1, "현관", 22, 26); c.mk(10, "현관", -22, -24); c.mk(6, s.bath > 1 ? "공용 욕실" : "욕실", -22, 26); c.mk(5, "주방·식당", 24, 26);
    c.mk(9, "드레스룸", 22, 26); c.mk(4, "거실", 22, 40); c.mk(3, "거실", -24, -24); c.mk(8, "거실", 90, -60); c.mk(2, "방 2", 30, 26);
    c.m.push([7, xL + W - 30, y0 + H + bal / 2]);
    return y0 + H + bal;
  }

  function draw(A, Y, hall, typ, fl, name) {
    var s = spec(A, Y, hall, typ, fl), c = new Canvas();
    var k = Math.max(0.62, Math.min(1, Math.sqrt(A / 135)));
    var W = 1000, bw = 900 * k, bh = 520 * k, x0 = (W - bw) / 2, y0 = 130;
    var bottom = s.tower ? tower(c, A, s, x0, y0, bw, bh) : flat(c, A, s, x0, y0, bw, bh);
    if (s.corridor && !s.tower) { c.o.unshift('<rect x="' + x0 + '" y="' + (y0 - 38) + '" width="' + bw + '" height="30" fill="#efebe4"/>'); c.t.push('<text x="' + (x0 + 10) + '" y="' + (y0 - 17) + '" font-size="14" fill="#8a8278">공용 복도 (복도식)</text>'); }
    else { var hx = (c.pos["현관"] || [x0])[0]; c.o.unshift('<rect x="' + (hx + 4) + '" y="' + (y0 - 44) + '" width="120" height="36" fill="#efebe4" stroke="#c9bfb0"/>'); c.t.push('<text x="' + (hx + 64) + '" y="' + (y0 - 20) + '" text-anchor="middle" font-size="14" fill="#8a8278">계단실·승강기</text>'); }
    var H = Math.round(bottom + 50);
    var m = c.m.map(function (q) { return '<a href="' + MK[q[0]][1] + '"><title>' + esc(MK[q[0]][0]) + '</title><circle cx="' + q[1].toFixed(1) + '" cy="' + q[2].toFixed(1) + '" r="16" fill="#b06a2c" stroke="#fff" stroke-width="3"/><text x="' + q[1].toFixed(1) + '" y="' + (q[2] + 6).toFixed(1) + '" text-anchor="middle" font-size="16" font-weight="900" fill="#fff">' + q[0] + '</text></a>'; });
    var tags = [(s.tower ? "타워형" : s.B + "베이 판상형"), "방 " + s.R, "욕실 " + s.bath, (Y ? Y + "년" : ""), (s.tower ? "" : (s.corridor ? "복도식" : "계단식")), (s.ext ? "확장형" : ""), (s.alpha ? "알파룸" : "")].filter(Boolean).join(" · ");
    var head = '<text x="30" y="40" font-size="24" font-weight="900" fill="#1d1b18">' + esc(name) + ' · 전용 ' + A + '㎡</text>' +
      '<text x="30" y="66" font-size="15" fill="#8a8278">' + esc(tags) + ' (공개자료로 추정)</text>';
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + W + ' ' + H + '" font-family="Noto Sans KR,Apple SD Gothic Neo,Malgun Gothic,sans-serif"><rect width="' + W + '" height="' + H + '" fill="#fff"/>' + head + c.o.join("") + c.t.join("") + m.join("") +
      '<text x="' + (W - 20) + '" y="' + (H - 12) + '" text-anchor="end" font-size="13" fill="#9a9086">영진종합목재가 단지 공개자료(면적·연식·구조)로 직접 그린 추정 평면 · 실제 도면 아님</text></svg>';
  }

  function legend() {
    return '<ol class="apleg">' + Object.keys(MK).map(function (n) { return '<li value="' + n + '"><a href="' + MK[n][1] + '">' + MK[n][0] + '</a></li>'; }).join("") + "</ol>";
  }

  function mount(el) {
    if (el.dataset.done) return; el.dataset.done = 1;
    var ar = el.dataset.a.split(",").map(function (p) { var q = p.split(":"); return [+q[0], +q[1]]; }).filter(function (q) { return q[0] > 0; });
    if (!ar.length) return;
    var Y = +el.dataset.y || 0, hall = el.dataset.h || "", typ = el.dataset.t || "", fl = el.dataset.f || "", nm = el.dataset.n || "";
    var cur = ar.slice().sort(function (a, b) { return b[1] - a[1]; })[0][0];
    var tabs = ar.length > 1 ? '<div class="aptab">' + ar.map(function (q) { return '<button type="button" data-a="' + q[0] + '">' + q[0] + '㎡ <small>' + q[1].toLocaleString() + '세대</small></button>'; }).join("") + "</div>" : "";
    el.innerHTML = tabs + '<div class="apsv"></div><details class="aplg"><summary>번호 설명 (누르면 시공법)</summary>' + legend() + "</details>";
    function show(a) { el.querySelector(".apsv").innerHTML = draw(a, Y, hall, typ, fl, nm); el.querySelectorAll(".aptab button").forEach(function (b) { b.classList.toggle("on", +b.dataset.a === a); }); }
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
