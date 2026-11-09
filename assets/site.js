// 영상 카드: 일반 클릭은 페이지 안에서 재생, Ctrl/새 탭은 유튜브로
document.addEventListener("click", function (e) {
  var a = e.target.closest && e.target.closest("a.vc[data-yt]");
  if (!a || e.ctrlKey || e.metaKey || e.shiftKey) return;
  var th = a.querySelector(".th");
  if (!th || th.querySelector("iframe")) return;
  e.preventDefault();
  var f = document.createElement("iframe");
  f.src = "https://www.youtube.com/embed/" + a.dataset.yt + "?autoplay=1";
  f.allow = "autoplay; encrypted-media"; f.allowFullscreen = true;
  f.style.cssText = "position:absolute;inset:0;width:100%;height:100%;border:0";
  th.appendChild(f);
});
// 전체 자재 검색
(function () {
  var q = document.getElementById("jq"); if (!q) return;
  var box = document.getElementById("jsr"), cnt = document.getElementById("jqn"), all = document.querySelectorAll(".jall"), data = null;
  var norm = function (s) { return (s || "").toLowerCase().replace(/[\s·\-_.,()\[\]]/g, ""); };
  var esc = function (s) { return (s || "").replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  function load(cb) { if (data) return cb(); fetch("/assets/jaryo.json").then(function (r) { return r.json(); }).then(function (j) { data = j; j.forEach(function (p) { p.k = norm(p.n + p.c + p.s); }); cb(); }); }
  function run() {
    var v = norm(q.value);
    if (!v) { box.innerHTML = ""; cnt.textContent = ""; all.forEach(function (e) { e.style.display = ""; }); return; }
    load(function () {
      var r = data.filter(function (p) { return p.k.indexOf(v) >= 0; });
      all.forEach(function (e) { e.style.display = "none"; });
      cnt.textContent = r.length ? "검색 결과 " + r.length + "종" + (r.length > 120 ? " (앞 120종 표시)" : "") : "검색 결과가 없습니다. 매장(042-545-2900)에 문의하시면 취급 여부를 알려드립니다.";
      box.innerHTML = r.slice(0, 120).map(function (p) {
        return '<a class="pd" href="/jaryo/' + esc(p.u) + '.html"><span class="pi"><img loading="lazy" src="' + esc(p.i) + '" alt="' + esc(p.n) + '"></span><b>' + esc(p.n) + "</b><small>" + esc(p.s || p.c) + "</small></a>";
      }).join("");
    });
  }
  var t; q.addEventListener("input", function () { clearTimeout(t); t = setTimeout(run, 150); });
  q.addEventListener("focus", function () { load(function () {}); });
})();
