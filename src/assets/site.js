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
