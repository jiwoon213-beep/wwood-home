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
  function load(cb) { if (data) return cb(); fetch("/assets/search.json").then(function (r) { return r.json(); }).then(function (J) { var j = J.d || J; data = j; j.forEach(function (p) { if (J.p && p.i && p.i.charAt(0) === "~") p.i = J.p[+p.i.charAt(1)] + p.i.slice(2); p.k = norm(p.n + (p.c || "") + (p.s || "")); }); cb(); }); }
  function run() {
    var v = norm(q.value);
    if (!v) { box.innerHTML = ""; cnt.textContent = ""; all.forEach(function (e) { e.style.display = ""; }); return; }
    load(function () {
      var r = data.filter(function (p) { return p.k.indexOf(v) >= 0; });
      all.forEach(function (e) { e.style.display = "none"; });
      cnt.textContent = r.length ? "검색 결과 " + r.length + "종" + (r.length > 120 ? " (앞 120종 표시)" : "") : "검색 결과가 없습니다. 매장(042-545-2900)에 문의하시면 취급 여부를 알려드립니다.";
      box.innerHTML = r.slice(0, 120).map(function (p) {
        return '<a class="pd" href="' + (p.l ? esc(p.l) : p.d ? "https://wwood.kr/home/" + (/Mobi|Android|iPhone|iPod|iPad/i.test(navigator.userAgent) ? "mobile" : "mall") + "/shoplist.php?idx=" + p.d + "&pmode=view" : "/jaryo/" + esc(p.u) + ".html") + '"' + (p.l ? "" : ' target="_blank" rel="noopener"') + '><span class="pi"><img loading="lazy" referrerpolicy="no-referrer" src="' + esc(p.i) + '" alt="' + esc(p.n) + '"></span><b>' + esc(p.n) + "</b><small>" + esc(p.s || p.c) + "</small></a>";
      }).join("");
    });
  }
  var t; q.addEventListener("input", function () { clearTimeout(t); t = setTimeout(run, 150); });
  q.addEventListener("focus", function () { load(function () {}); });
  var pq = new URLSearchParams(location.search).get("q"); if (pq) { q.value = pq; run(); setTimeout(function () { q.scrollIntoView({ block: "start" }); }, 50); }
})();
// 기준가: 분류 탭·좌우 넘기기·검색
(function () {
  var secs = document.querySelectorAll(".psec"); if (!secs.length) return;
  var chips = document.querySelectorAll("#pchips .chip"), cur = document.getElementById("pcur"), q = document.getElementById("pq"), qn = document.getElementById("pqn"), i = 0, n = secs.length;
  function show(k) {
    i = (k + n) % n;
    secs.forEach(function (s, j) { s.classList.toggle("on", j === i); });
    chips.forEach(function (c, j) { c.classList.toggle("on", j === i); if (j === i) c.scrollIntoView({ block: "nearest", inline: "center", behavior: "smooth" }); });
    cur.textContent = (i + 1) + " / " + n + " · " + secs[i].dataset.n;
  }
  chips.forEach(function (c) { c.addEventListener("click", function () { show(+c.dataset.k); }); });
  document.getElementById("pprev").onclick = function () { show(i - 1); };
  document.getElementById("pnext").onclick = function () { show(i + 1); };
  var box = document.getElementById("psecs"), x0 = null, y0 = null;
  box.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
  box.addEventListener("touchend", function (e) {
    if (x0 === null || document.body.classList.contains("psearch")) return;
    var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0; x0 = null;
    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) show(i + (dx < 0 ? 1 : -1));
  }, { passive: true });
  var norm = function (s) { return (s || "").toLowerCase().replace(/[\s·×x*\-_.,()]/g, ""); };
  q.addEventListener("input", function () {
    var v = norm(q.value), hit = 0;
    document.body.classList.toggle("psearch", !!v);
    secs.forEach(function (s) {
      var any = 0;
      s.querySelectorAll("tbody tr").forEach(function (tr) { var ok = !v || norm(tr.textContent + s.dataset.n).indexOf(v) >= 0; tr.style.display = ok ? "" : "none"; if (ok) any++; });
      s.style.display = v ? (any ? "block" : "none") : ""; if (v) hit += any;
    });
    qn.textContent = v ? (hit ? "검색 결과 " + hit + "개" : "검색 결과가 없습니다. 매장(042-545-2900)에 문의하세요.") : "";
    if (!v) show(i);
  });
  show(0);
})();
// TOP10 슬라이드
(function () {
  var s = document.getElementById("tslide"); if (!s) return;
  var dot = document.getElementById("tdot");
  function upd() { var p = Math.round(s.scrollLeft / s.clientWidth); dot.textContent = p ? "◀ 1–5위 / 6–10위" : "1–5위 / 6–10위 ▶ 옆으로 밀기"; }
  s.addEventListener("scroll", function () { clearTimeout(s._t); s._t = setTimeout(upd, 80); }, { passive: true });
  document.querySelectorAll(".tdots .tb").forEach(function (b) { b.onclick = function () { s.scrollBy({ left: s.clientWidth * +b.dataset.d, behavior: "smooth" }); }; });
})();

/* 휴대폰이면 쇼핑몰 상품을 모바일 페이지로 바로 연결 */
(function () {
  if (!/Mobi|Android|iPhone|iPod|iPad/i.test(navigator.userAgent)) return;
  function fix(a) {
    if (a && a.href && a.href.indexOf("/home/mall/shoplist.php") > -1 && a.href.indexOf("pmode=view") > -1)
      a.href = a.href.replace("/home/mall/shoplist.php", "/home/mobile/shoplist.php");
  }
  document.querySelectorAll('a[href*="/home/mall/shoplist.php"]').forEach(fix);
  document.addEventListener("click", function (e) { fix(e.target.closest && e.target.closest("a")); }, true);
})();

/* 사진 무단 저장 방지(우클릭·드래그·길게 누르기) */
(function(){function b(e){var t=e.target;if(t&&t.tagName==="IMG"){e.preventDefault();return false}}document.addEventListener("contextmenu",b,true);document.addEventListener("dragstart",b,true);})();

(function(){function p(e){var t=e.target;if(t&&t.tagName==="IMG"&&(t.getAttribute("src")||"").indexOf("/assets/")>-1){e.preventDefault();return false}}document.addEventListener("contextmenu",p,true);document.addEventListener("dragstart",p,true)})();

document.addEventListener("click",function(e){var b=e.target.closest&&e.target.closest(".ytf");if(!b)return;var f=document.createElement("iframe");f.src="https://www.youtube.com/embed/"+b.dataset.id+"?autoplay=1&rel=0";f.allow="autoplay; encrypted-media; picture-in-picture";f.allowFullscreen=true;f.title=b.getAttribute("aria-label")||"영상";f.style.cssText="position:absolute;inset:0;width:100%;height:100%;border:0";b.replaceWith(f)});
/* NEW 표시가 붙은 DIY 만들기·시공법 카드는 목록 맨 앞으로 */
(function(){try{[].forEach.call(document.querySelectorAll(".mg"),function(g){[].slice.call(g.children).filter(function(c){return c.classList.contains("mc")&&c.querySelector(".newb")}).reverse().forEach(function(c){g.insertBefore(c,g.firstChild)})})}catch(e){}})();
// 앱(PWA) 등록
if ("serviceWorker" in navigator) window.addEventListener("load", function () { navigator.serviceWorker.register("/sw.js").catch(function () {}); });
// 홈 화면에 추가(앱 설치) 버튼 — 크롬·엣지·삼성인터넷(폰·PC)은 '설치' 한 번 누르면 바로 생김
(function () {
  var b = document.getElementById("appi"), g = document.getElementById("appg"), gt = document.getElementById("appgt"); if (!b) return;
  var st = window.matchMedia && matchMedia("(display-mode: standalone)").matches || navigator.standalone;
  if (st) { b.hidden = true; return; }
  var dp = null, ua = navigator.userAgent, waiters = [];
  window.addEventListener("beforeinstallprompt", function (e) { e.preventDefault(); dp = e; waiters.splice(0).forEach(function (f) { f(); }); if (/[?&]app=1/.test(location.search)) offer(); });
  window.addEventListener("appinstalled", function () { b.hidden = true; g.hidden = true; });
  function guide(t) { gt.innerHTML = /appgl/.test(t) ? t : '<div class="appgs2">' + t + '</div>'; g.hidden = false; }
  function install() { if (!dp) return; var d = dp; dp = null; g.hidden = true; d.prompt(); d.userChoice.then(function (c) { if (c && c.outcome === "accepted") b.hidden = true; }); }
  function offer() { guide('<ul class="appgl"><li><i>💰</i>기준가·1평 가격 <b>한 번에</b></li><li><i>✂️</i>재단 미리보기·자재 계산기 <b>바로 실행</b></li><li><i>🔍</i>자재 1만 가지 <b>사진으로 검색</b></li><li><i>📶</i>인터넷 약해도 <b>본 페이지 그대로</b></li></ul><button type="button" class="appgo"><span>앱 설치하기</span><small>무료 · 1초 · 용량 거의 안 차지해요</small></button><p class="appgs">누르고 <b>설치</b>만 한 번 더 누르면 ' + (/Mobi|Android/i.test(ua) ? "홈 화면" : "바탕화면") + '에 생겨요</p>'); gt.querySelector(".appgo").onclick = install; }
  document.getElementById("appgx").onclick = function () { g.hidden = true; };
  g.addEventListener("click", function (e) { if (e.target === g) g.hidden = true; });
  b.addEventListener("click", function (e) {
    e.preventDefault();
    if (dp) return install();
    var inapp = /KAKAOTALK|NAVER\(inapp|Instagram|FBAN|FBAV|Line\/|DaumApps|everytimeApp|; wv\)/i.test(ua);
    if (/Android/i.test(ua) && inapp) { location.href = "intent://" + location.host + location.pathname + "?app=1#Intent;scheme=https;package=com.android.chrome;end"; return; }
    if (/iPhone|iPad|iPod/i.test(ua)) return guide(inapp ? "지금 화면은 앱 안 브라우저라 추가가 안 돼요. 오른쪽 아래 <b>⋯</b> → <b>Safari로 열기</b> 후, 아래 <b>공유(□↑)</b> → <b>홈 화면에 추가</b>를 누르세요.<br><small>아이폰은 애플 정책상 자동 설치가 안 되고 이 방법만 돼요.</small>" : "아래쪽 <b>공유(□↑)</b> 버튼 → <b>홈 화면에 추가</b> → <b>추가</b>를 누르세요.<br><small>아이폰은 애플 정책상 자동 설치가 안 되고 이 방법만 돼요.</small>");
    var done = false; waiters.push(function () { if (!done) { done = true; offer(); } });
    setTimeout(function () { if (done) return; done = true;
      if (/SamsungBrowser/i.test(ua)) return guide("아래쪽 <b>≡</b> → <b>현재 페이지 추가</b> → <b>홈 화면</b>을 누르세요.");
      if (/Firefox/i.test(ua) && !/Android/i.test(ua)) return guide("PC 파이어폭스는 앱 설치가 안 돼요. <b>크롬</b>이나 <b>엣지</b>로 열고 이 버튼을 누르세요.");
      if (/Mobi|Android/i.test(ua)) return guide("오른쪽 위 <b>⋮</b> → <b>홈 화면에 추가</b>(또는 <b>앱 설치</b>) → <b>설치</b>를 누르세요.");
      guide("주소창 오른쪽 <b>설치 아이콘(⊕ 또는 모니터 모양)</b>을 누르거나, <b>⋮</b> → <b>앱 설치</b>(엣지: <b>앱</b> → <b>이 사이트를 앱으로 설치</b>)를 누르세요.");
    }, 1200);
  });
})();

/* 관련 유튜브 영상(제품 사진 크게 보기·제품 상세 공통) */
(function(){var VJ=null,Q=[],SY=[[/구조재|2&Btr|SPF|투바이|2x4|J-Grade|다루끼|각재|각목/i,"구조재|각재|각목|투바이|2x4|다루끼"],[/TJI|JOIST|장선|PSL|LVL|Parallam|글루램|집성보|I-?빔/i,"목조|장선|구조재"],[/중문/,"중문"],[/도어|방문|문짝|ABS/,"도어|방문|문 교체|문짝"],[/문틀/,"문틀"],[/몰딩|걸레받이/,"몰딩|걸레받이"],[/필름/,"필름"],[/스테인|오일|페인트|도료|바니쉬|젯소/,"스테인|오일|페인트|칠"],[/사이딩/,"사이딩"],[/합판/,"합판"],[/MDF/i,"MDF"],[/OSB/i,"OSB"],[/집성/,"집성"],[/석고/,"석고"],[/단열|아이소핑크|스티로폼|글라스울/,"단열"],[/데크/,"데크"],[/방부/,"방부목|데크"],[/루바/,"루바"],[/템바/,"템바"],[/타카|핀/,"타카"],[/피스|나사|볼트|앙카|못/,"피스|볼트|앙카|못"],[/경첩|손잡이|도어락|레버|도어록/,"손잡이|도어락|경첩|문 교체"],[/실리콘|우레탄폼|폼건/,"실리콘|폼"],[/지붕|슁글|아스팔트|기와/,"지붕|슁글"],[/방수/,"방수"],[/타일/,"타일"],[/마루|장판/,"마루|장판"],[/천장|루버/,"천장"],[/샌딩|사포|연마/,"샌딩|사포"],[/톱|드릴|그라인더|공구|드라이버|임팩/,"공구|원형톱|드릴|임팩"],[/히노끼|편백/,"히노끼|편백"],[/스프러스/,"스프러스"],[/선반|브라켓|까치발/,"선반|까치발"],[/싱크|수전/,"싱크|수전"],[/조명|콘센트|스위치/,"조명|콘센트|스위치"],[/창호|샷시|창문/,"샷시|창"],[/철물|장선걸이|기둥받침|허리케인|홀다운/,"철물|기둥|장선"],[/우드슬랩|상판/,"상판|우드슬랩"],[/벽지|도배/,"도배|벽지"]];
function vrx(t){var r=[];SY.forEach(function(x){if(x[0].test(t))r.push(x[1])});return r.length?new RegExp(r.join("|"),"i"):null}
function draw(el,n,c){var r1=vrx(n),r2=vrx(c),tk=(n.match(/[가-힣A-Za-z]{2,}/g)||[]).filter(function(w){return!/^(제품|매장|문의|세트|타입|국산|수입|일반|소형|대형|중형|화이트|블랙|그레이|브라운|색상|규격|the|and)$/i.test(w)}).slice(0,5);
var S=VJ.map(function(v){var t=v[4],s=0;if(r1&&r1.test(t))s+=5;tk.forEach(function(w){if(t.indexOf(w)>=0)s+=2});if(r2&&r2.test(t))s+=1;return[s+(v[1]=="L"?.3:0)+Math.min(v[3],5000)/50000,v]}).filter(function(x){return x[0]>=(r1?5:1.5)}).sort(function(a,b){return b[0]-a[0]}).slice(0,3);
if(!S.length){el.innerHTML="";return}el.innerHTML='<p class="ylvh">▶ 관련 영상</p><div class="ylvl">'+S.map(function(x){var v=x[1];return'<a href="https://www.youtube.com/watch?v='+v[0]+'" data-v="'+v[0]+'"><img src="https://i.ytimg.com/vi/'+v[0]+'/mqdefault.jpg" alt=""><span></span></a>'}).join("")+"</div>";[].forEach.call(el.querySelectorAll("a span"),function(e,k){e.textContent=S[k][1][4].split("|")[0]})}
window.WV=function(el,n,c,ok){if(VJ){draw(el,n,c);return}Q.push([el,n,c,ok]);if(Q.length>1)return;fetch("/assets/videos.json").then(function(r){return r.json()}).then(function(j){VJ=j.v;Q.forEach(function(q){if(!q[3]||q[3]())draw(q[0],q[1],q[2])});Q=[]}).catch(function(){})};
document.addEventListener("click",function(e){var x=e.target.closest&&e.target.closest(".ylv a[data-v]");if(!x)return;e.preventDefault();var l=x.closest(".ylvl");l.outerHTML='<div class="ylvf"><iframe src="https://www.youtube.com/embed/'+x.getAttribute("data-v")+'?autoplay=1&playsinline=1&rel=0" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe></div>'});
[].forEach.call(document.querySelectorAll(".ylv[data-n]"),function(el){WV(el,el.getAttribute("data-n"),el.getAttribute("data-c")||"")});})();

/* 어느 페이지에서든 📷 누르면 찍은 사진을 들고 사진으로 찾기 페이지로 */
document.addEventListener("change",function(e){var t=e.target;if(!t.classList||!t.classList.contains("sjq")||!t.files[0])return;var f=t.files[0],u=URL.createObjectURL(f),im=new Image();im.onload=function(){var s=Math.min(1,640/Math.max(im.width,im.height)),c=document.createElement("canvas");c.width=Math.round(im.width*s);c.height=Math.round(im.height*s);c.getContext("2d").drawImage(im,0,0,c.width,c.height);try{sessionStorage.setItem("sjimg",c.toDataURL("image/jpeg",.85))}catch(x){}location.href="/sajin.html"};im.src=u});
