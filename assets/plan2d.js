/* 사진 → 2D 도면 초안 (가구 만들기·자재 시공법) — 영진종합목재. sajin.html 과 방문자 도면 페이지에서 같이 씀 */
(function(){
var T={
 /* 가구 만들기 */
 cab:{k:"mandeul",n:"수납장",d:[800,350,900],s:2,m:"jip",rx:/수납|장(?!작)|협탁|렌지대|신발|거실장|상부장|정리함|캐비|화장대/},
 book:{k:"mandeul",n:"책장",d:[800,300,1800],s:4,m:"jip",rx:/책장|매거진|진열/},
 shelf:{k:"mandeul",n:"벽선반",d:[800,200,600],s:3,m:"jip",rx:/선반/},
 table:{k:"mandeul",n:"테이블·책상",d:[1200,600,740],m:"jip",rx:/테이블|책상|식탁|작업대|아일랜드|좌탁|밥상/},
 bench:{k:"mandeul",n:"벤치·스툴",d:[1000,350,450],m:"jip",rx:/벤치|스툴|의자|발판/},
 pyeong:{k:"mandeul",n:"평상",d:[1800,1200,400],m:"bang",rx:/평상|침대/},
 box:{k:"mandeul",n:"상자·화분",d:[800,400,300],m:"hap",rx:/상자|화분|텃밭|박스|공구통|장난감|분리수거|개집/},
 /* 자재 시공법 */
 wgyp:{k:"sigong",n:"벽 석고보드",d:[3000,0,2400],m:"gyp",sh:[900,1800],ha:1,rx:/석고|가벽|단열/},
 whap:{k:"sigong",n:"벽 합판 덧방",d:[3000,0,2400],m:"hap",sh:[1220,2440],ha:1,rx:/합판|아트월|템바|루바|벽/},
 fhap:{k:"sigong",n:"바닥 합판 덧방",d:[3000,2400,0],m:"hap",sh:[1220,2440],rx:/바닥|마루|데코타일/},
 deck:{k:"sigong",n:"데크 깔기",d:[3600,2400,0],m:"bang",bd:[140,3600],rx:/데크|마당/}
};
var MT={jip:["집성판 18T",18,"/gagyeok/jipseong-gagyeok.html"],hap:["합판 12T",12,"/gagyeok/hapan-gagyeok.html"],bang:["방부목",25,"/gagyeok/deck-gagyeok.html"],
 gyp:["석고보드 9.5T",9.5,"/gagyeok/seokgo-gagyeok.html"],mdf:["MDF 6T(뒷판)",6,"/gagyeok/mdf-gagyeok.html"],gak:["각재·구조목",38,"/gagyeok/gakjae-gagyeok.html"]};
function guess(name,mode){var b=mode=="sigong"?"whap":"cab",O=["book","shelf","table","bench","pyeong","box","cab","wgyp","fhap","deck","whap"];for(var i=0;i<O.length;i++){var k=O[i];if(T[k].k==(mode=="sigong"?"sigong":"mandeul")&&T[k].rx.test(name||"")){b=k;break}}return b}
function dims(name){var t=String(name||""),f=function(rx){var m=t.match(rx);if(!m)return 0;var v=+m[1].replace(/,/g,"");return/cm/.test(m[2]||"")?v*10:v};
 var x=t.match(/(\d{3,4})\s*[×xX*]\s*(\d{2,4})(?:\s*[×xX*]\s*(?:h\s*)?(\d{2,4}))?/),w=f(/(?:폭|가로|길이)\s*(?:약\s*)?([\d,]{2,6})\s*(cm|mm)?/),d=f(/(?:깊이|세로)\s*(?:약\s*)?([\d,]{2,6})\s*(cm|mm)?/),h=f(/높이\s*(?:약\s*)?([\d,]{2,6})\s*(cm|mm)?/);
 if(x){w=w||+x[1];d=d||+x[2];h=h||(x[3]?+x[3]:0)}return w?[w,d,h]:null}
function parts(p){var t=T[p.t],W=p.w,D=p.d,H=p.h,n=p.s||0,th=MT[t.m][1],r=[],m=t.m;
 if(p.t=="cab"||p.t=="book"){r.push(["옆판",D+"×"+H,2,m],["천판·지판",(W-2*th)+"×"+D,2,m]);if(n)r.push(["선반",(W-2*th)+"×"+(D-10),n,m]);r.push(["뒷판",W+"×"+H,1,"mdf"])}
 else if(p.t=="shelf"){r.push(["선반판",W+"×"+D,n||1,m],["선반 받침 철물(까치발)","—",(n||1)*2,"gak"])}
 else if(p.t=="table"||p.t=="bench"){var l=p.t=="table"?60:45;r.push(["상판",W+"×"+D,1,m],["다리 ("+l+"각)",l+"×"+l+"×"+(H-th),4,"gak"],["앞뒤 띠장",(W-2*l-100)+"×80",2,m],["옆 띠장",(D-2*l-100)+"×80",2,m])}
 else if(p.t=="pyeong"){var bn=Math.ceil(D/150);r.push(["윗판 (폭 140)",W+"×140",bn,m],["멍에 (2×4)",W+"",2,"gak"],["장선 (2×4)",(D-76)+"",Math.max(3,Math.ceil(W/450)+1),"gak"],["기둥 (4×4)","89×89×"+(H-25-89),W>1500?6:4,"gak"])}
 else if(p.t=="box"){r.push(["앞뒤판",W+"×"+H,2,m],["옆판",(D-2*th)+"×"+H,2,m],["바닥판",(W-2*th)+"×"+(D-2*th),1,m])}
 else if(t.sh){var a=t.sh[0],b=t.sh[1],L1=W,L2=t.k=="sigong"&&p.t.charAt(0)=="w"?H:D,c=Math.ceil(L1/a)*Math.ceil(L2/b);r.push([MT[m][0]+" 원판",a+"×"+b,c,m]);if(t.ha)r.push(["벽 하지 각재 (455 간격)",L2+"",Math.ceil(L1/455)+1,"gak"])}
 else if(t.bd){var c2=Math.ceil(D/(t.bd[0]+5))*Math.ceil(W/t.bd[1]);r.push(["데크재 (폭 140)",t.bd[1]+"×140",c2,m],["장선 (2×4, 400 간격)",W+"",Math.ceil(D/400)+1,"gak"])}
 return r}
var F="font-family:inherit";
function dl(x1,y1,x2,y2,tx,v){/* 치수선 */var o='<line x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+'" stroke="#c0392b" stroke-width="1.2" marker-start="url(#ar)" marker-end="url(#ar)"/>';var cx=(x1+x2)/2,cy=(y1+y2)/2;
 return o+(v?'<text x="'+(cx-8)+'" y="'+cy+'" transform="rotate(-90 '+(cx-8)+' '+cy+')" text-anchor="middle" font-size="19" fill="#c0392b" font-weight="700">'+tx+'</text>':'<text x="'+cx+'" y="'+(cy-7)+'" text-anchor="middle" font-size="19" fill="#c0392b" font-weight="700">'+tx+'</text>')}
function R(x,y,w,h,f,dash){return'<rect x="'+x.toFixed(1)+'" y="'+y.toFixed(1)+'" width="'+Math.max(.5,w).toFixed(1)+'" height="'+Math.max(.5,h).toFixed(1)+'" fill="'+(f||"#f3e3c6")+'" stroke="#3b3128" stroke-width="1.4"'+(dash?' stroke-dasharray="5 4"':'')+'/>'}
function view(p,x0,y0,bw,bh,front,K){/* 한 면 그림 → svg 조각 */var t=T[p.t],W=front?p.w:(p.d||p.w),H=p.h||p.d,th=MT[t.m][1];if(!t.sh&&!t.bd&&p.t!="pyeong"){}
 var k=K||Math.min(bw/W,bh/H),w=W*k,h=H*k,x=x0+(bw-w)/2,y=y0+(bh-h),s="",i,n=p.s||0,tk=Math.max(2,th*k);
 if(p.t=="cab"||p.t=="book"){if(front){s+=R(x,y,w,h,"#fbf1df")+R(x,y,tk,h)+R(x+w-tk,y,tk,h)+R(x+tk,y,w-2*tk,tk)+R(x+tk,y+h-tk,w-2*tk,tk);for(i=1;i<=n;i++){var yy=y+h-tk-(h-2*tk)*i/(n+1);s+=R(x+tk,yy-tk/2,w-2*tk,tk)}}else{s+=R(x,y,w,h,"#fbf1df")+R(x+w-Math.max(2,6*k),y,Math.max(2,6*k),h,"#e8d6b6")+R(x,y,w,tk)+R(x,y+h-tk,w,tk)}}
 else if(p.t=="shelf"){n=n||1;var bk=Math.min(40,h/4);for(i=0;i<n;i++){var y2=n==1?y+h/2:y+(h-tk-bk)*i/(n-1);s+=R(x,y2,w,tk);if(front){s+='<path d="M'+(x+w*.15)+' '+(y2+tk)+'v'+Math.min(40,h/4)+'h'+Math.min(30,w/8)+'z" fill="#888" stroke="#3b3128"/><path d="M'+(x+w*.85)+' '+(y2+tk)+'v'+Math.min(40,h/4)+'h-'+Math.min(30,w/8)+'z" fill="#888" stroke="#3b3128"/>'}}s+='<line x1="'+(x-10)+'" y1="'+y+'" x2="'+(x-10)+'" y2="'+(y+h)+'" stroke="#999" stroke-dasharray="4 4"/>'}
 else if(p.t=="table"||p.t=="bench"){var l=(p.t=="table"?60:45)*k;s+=R(x,y,w,tk)+R(x+8,y+tk,l,h-tk)+R(x+w-8-l,y+tk,l,h-tk)+R(x+8+l,y+tk,w-16-2*l,80*k,"#ead6b4")}
 else if(p.t=="pyeong"){if(front){var lg=89*k;s+=R(x,y,w,25*k)+R(x,y+25*k,w,89*k,"#ead6b4");var cnt=W>1500?3:2;for(i=0;i<cnt;i++){var lx=x+(w-lg)*i/(cnt-1);s+=R(lx,y+25*k+89*k,lg,h-25*k-89*k)}}else{var bn=Math.ceil(W/150);for(i=0;i<bn;i++)s+=R(x+i*w/bn+1,y,w/bn-2,25*k);s+=R(x,y+25*k,w,89*k,"#ead6b4")+R(x,y+114*k,89*k,h-114*k)+R(x+w-89*k,y+114*k,89*k,h-114*k)}}
 else if(p.t=="box"){s+=R(x,y,w,h,"#fbf1df");if(front){s+='<line x1="'+x+'" y1="'+(y+h-tk)+'" x2="'+(x+w)+'" y2="'+(y+h-tk)+'" stroke="#3b3128" stroke-dasharray="5 4"/>'}else{s+=R(x,y,tk,h)+R(x+w-tk,y,tk,h)}}
 else if(t.sh){var a=t.sh[0]*k,b=t.sh[1]*k;s+=R(x,y,w,h,"#fff");for(var yy2=0;yy2<h-.5;yy2+=b)for(var xx=0;xx<w-.5;xx+=a)s+=R(x+xx,y+h-yy2-Math.min(b,h-yy2),Math.min(a,w-xx),Math.min(b,h-yy2),"#f1e4cc");if(t.ha)for(var hx=0;hx<=W;hx+=455)s+='<line x1="'+(x+hx*k)+'" y1="'+y+'" x2="'+(x+hx*k)+'" y2="'+(y+h)+'" stroke="#2b6fe8" stroke-dasharray="6 5" stroke-width="1.2"/>'}
 else if(t.bd){var bw2=140*k,L=t.bd[1]*k,row=0;s+=R(x,y,w,h,"#fff");for(var by=0;by<h-.5;by+=bw2+5*k,row++){var off=(row%2)*L/2;for(var bx=-off;bx<w;bx+=L){var sx=Math.max(0,bx),ex=Math.min(w,bx+L);if(ex>sx)s+=R(x+sx,y+by,ex-sx,Math.min(bw2,h-by),"#e2c79a")}}}
 var vtxt=t.k=="sigong"?(t.sh&&t.ha?"높이":"세로"):"높이";
 s+=dl(x,y-14,x+w,y-14,(front?p.w:(p.d||p.w))+" mm");s+=dl(x-26,y,x-26,y+h,(H)+" mm",1);
 return s}
function svg(p){var t=T[p.t],two=t.k=="mandeul",VW=two?760:640,VH=two?436:456,s='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '+VW+' '+VH+'" style="'+F+';width:100%;height:auto;background:#fff"><defs><marker id="ar" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1L10 5L0 9z" fill="#c0392b"/></marker></defs>';
 var q={t:p.t,w:p.w,d:p.d,h:t.k=="sigong"?(p.t.charAt(0)=="w"?p.h:p.d):p.h,s:p.s};
 if(two){var K=Math.min(330/q.w,270/(q.d||1),320/q.h);s+=view(q,50,50,330,320,1,K)+view(q,440,50,280,320,0,K);s+='<text x="215" y="404" text-anchor="middle" font-size="19" font-weight="800" fill="#333">정면도</text><text x="585" y="404" text-anchor="middle" font-size="19" font-weight="800" fill="#333">측면도</text>'}
 else{q.d=0;s+=view({t:p.t,w:p.w,d:0,h:q.h,s:0},60,50,540,340,1);s+='<text x="330" y="424" text-anchor="middle" font-size="19" font-weight="800" fill="#333">'+(p.t.charAt(0)=="w"?"벽 입면도":"바닥 평면도")+(t.ha?" · 파란 점선 = 하지 각재":"")+'</text>'}
 return s+'<text x="'+(VW-8)+'" y="'+(VH-8)+'" text-anchor="end" font-size="13" fill="#b5a99a">영진종합목재 wwood.co.kr · 초안 도면</text></svg>'}
function table(p){var r=parts(p),E=function(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})};var used={};
 var h='<table class="pl2t"><tr><th>부재</th><th>크기(mm)</th><th>수량</th><th>자재</th></tr>'+r.map(function(x){used[x[3]]=1;return'<tr><td>'+E(x[0])+'</td><td>'+E(x[1])+'</td><td>'+x[2]+'</td><td><a href="'+MT[x[3]][2]+'">'+MT[x[3]][0]+'</a></td></tr>'}).join("")+'</table>';
 h+='<div class="pl2m">'+Object.keys(used).map(function(k){return'<a href="'+MT[k][2]+'"><b>'+MT[k][0]+'</b><small>기준가·규격 보기 ›</small></a>'}).join("")+'<a href="/cut.html"><b>재단 맡기기</b><small>원판에서 재단 그림 ›</small></a></div>';return h}
function steps(p){var t=T[p.t],th=MT[t.m][1],W=p.w,D=p.d,H=p.h,n=p.s||0,iw=W-2*th,mt=MT[t.m][0];
 var S={cab:["재단 목록대로 "+mt+" 판재를 재단합니다(매장에서 잘라 드려요). 자른 면은 사포로 다듬습니다.","옆판 2장("+D+"×"+H+")을 세우고 그 사이에 천판·지판("+iw+"×"+D+")을 끼워 목공본드를 바르고 피스로 고정합니다. 피스 자리는 먼저 구멍을 뚫어야 갈라지지 않습니다.",n?"선반 "+n+"장("+iw+"×"+(D-10)+")을 높이를 나눠 끼우고 옆판 밖에서 피스로 고정합니다.":"",
  "대각선 길이 두 개가 같은지 재서 직각을 맞춘 뒤, 뒷판("+W+"×"+H+")을 뒤에 대고 타카나 짧은 피스로 고정합니다.","오일이나 바니시로 마감하고, 키가 큰 장은 넘어짐 방지 철물로 벽에 고정합니다."],
 shelf:["선반판 "+(n||1)+"장("+W+"×"+D+")을 재단하고 모서리를 사포로 다듬은 뒤 오일로 마감합니다.","벽에 수평자로 선반 높이를 표시하고, 벽 속 각재나 콘크리트 위치를 확인합니다.","까치발을 수평에 맞춰 벽에 고정합니다(석고벽은 석고 앵커, 콘크리트는 칼블럭).","까치발 위에 선반판을 올리고 아래에서 짧은 피스로 고정합니다."],
 table:["재단 목록대로 상판·다리·띠장을 재단하고 사포로 다듬습니다.","다리 4개 사이에 앞뒤 띠장과 옆 띠장을 대고 목공본드와 피스로 사각 틀을 짭니다.","틀의 대각선 길이를 맞춰 직각을 잡습니다.","틀 위에 상판을 올리고 띠장 아래에서 위로 피스를 박아 고정합니다(상판을 뚫고 나오지 않는 길이).","오일이나 바니시로 마감합니다."],
 pyeong:["멍에·장선·기둥·윗판을 재단 목록대로 준비합니다(방부목).","멍에 2개 사이에 장선을 450 간격 정도로 대고 피스로 고정해 바닥틀을 짭니다.","모서리와 가운데에 기둥을 세워 바닥틀에 고정하고 수평을 맞춥니다.","윗판을 틈을 조금씩 띄워 깔고 장선마다 스테인리스 피스 2개씩 박습니다.","오일스테인으로 마감합니다."],
 box:["앞뒤판·옆판·바닥판을 재단 목록대로 자릅니다.","앞뒤판 사이에 옆판을 끼워 목공본드와 피스로 사각 틀을 만듭니다.","틀 안쪽 아래에 바닥판을 끼워 고정합니다(화분이면 물빠짐 구멍을 뚫습니다).","사포로 다듬고 용도에 맞게 오일·방수 도료로 마감합니다."],
 wgyp:["벽에 수직·수평 기준선을 긋고, 하지 각재를 455 간격으로 세워 고정합니다.","석고보드를 세로로 세워 하지 각재 위에서 이음이 생기게 붙이고 석고 피스로 고정합니다.","창·콘센트 자리는 미리 재서 칼로 잘라 냅니다.","이음 부분에 메시 테이프와 퍼티로 메운 뒤 사포로 다듬고 마감(도배·페인트)합니다."],
 whap:["벽에 기준선을 긋고 하지 각재를 455 간격으로 고정합니다.","합판을 하지 각재 위에서 이음이 생기게 대고 피스로 고정합니다.","창·콘센트 자리는 미리 재서 잘라 냅니다.","이음은 퍼티로 메우거나 몰딩으로 가리고 마감합니다."],
 fhap:["기존 바닥의 들뜬 곳과 먼지를 정리하고 수평을 확인합니다.","합판을 이음이 한 줄로 몰리지 않게 엇갈려 깝니다.","본드와 피스(또는 타카)로 고정하고 벽 쪽은 조금 띄웁니다.","이음 단차를 사포로 다듬고 바닥재를 시공합니다."],
 deck:["바닥을 다지고 기초(주춧돌·블록)를 수평으로 놓습니다.","장선을 400 간격으로 놓고 수평을 맞춰 고정합니다.","데크재를 틈을 일정하게 띄워 깔고 장선마다 스테인리스 피스 2개씩 박습니다.","이음은 장선 위에서 엇갈리게 하고, 끝을 정리한 뒤 오일스테인으로 마감합니다."]};
 S.book=S.cab;S.bench=S.table;return(S[p.t]||[]).filter(function(x){return x})}
function model(p){var t=T[p.t],th=MT[t.m][1],W=p.w,D=p.d||0,H=p.h||0,n=p.s||0,iw=W-2*th,B=[],C=[],i,j,A=function(g,x,y,z,w,d,h){B.push({g:g,b:[x,y,z,w,d,h]})};
 if(p.t=="cab"||p.t=="book"){A(0,0,0,0,th,D,H);A(0,W-th,0,0,th,D,H);A(1,th,0,0,iw,D,th);A(1,th,0,H-th,iw,D,th);for(i=1;i<=n;i++)A(2,th,6,th+(H-2*th)*i/(n+1)-th/2,iw,D-10,th);A(n?3:2,0,-6,0,W,6,H);
  C=["옆판 2장("+D+"×"+H+")을 세웁니다.","천판·지판("+iw+"×"+D+")을 끼워 본드·피스로 고정합니다."];if(n)C.push("선반 "+n+"장("+iw+"×"+(D-10)+")을 같은 간격으로 고정합니다.");C.push("직각을 맞추고 뒷판("+W+"×"+H+")을 뒤에 고정합니다.")}
 else if(p.t=="shelf"){n=n||1;var bk=Math.min(150,H/4);A(-1,-100,-20,0,W+200,20,H+60);for(i=0;i<n;i++){var z=n==1?H/2:bk+(H-th-bk)*i/(n-1);A(0,W*.15,0,z-bk,20,D*.8,bk);A(0,W*.85-20,0,z-bk,20,D*.8,bk);A(1,0,0,z,W,D,th)}
  C=["벽에 수평을 보고 까치발 "+(n*2)+"개를 고정합니다.","까치발 위에 선반판("+W+"×"+D+") "+n+"장을 올려 고정합니다."]}
 else if(p.t=="table"||p.t=="bench"){var l=p.t=="table"?60:45,lh=H-th;[[0,0],[W-l,0],[0,D-l],[W-l,D-l]].forEach(function(q){A(0,q[0],q[1],0,l,l,lh)});A(1,l,l/2-10,lh-80,W-2*l,20,80);A(1,l,D-l/2-10,lh-80,W-2*l,20,80);A(1,l/2-10,l,lh-80,20,D-2*l,80);A(1,W-l/2-10,l,lh-80,20,D-2*l,80);A(2,0,0,lh,W,D,th);
  C=["다리 4개("+l+"각 "+lh+")를 준비해 자리를 잡습니다.","다리 사이에 띠장을 대고 사각 틀을 짭니다.","틀 위에 상판("+W+"×"+D+")을 올려 아래에서 피스로 고정합니다."]}
 else if(p.t=="pyeong"){var hl=H-25-89;A(0,0,0,hl,W,38,89);A(0,0,D-38,hl,W,38,89);var nj=Math.max(3,Math.ceil(W/450)+1);for(i=0;i<nj;i++)A(0,(W-38)*i/(nj-1),38,hl,38,D-76,89);var lx=W>1500?[0,(W-89)/2,W-89]:[0,W-89];lx.forEach(function(x){A(1,x,0,0,89,89,hl);A(1,x,D-89,0,89,89,hl)});var bn=Math.ceil(D/150);for(i=0;i<bn;i++)A(2,0,i*D/bn+4,H-25,W,D/bn-8,25);
  C=["멍에 2개 사이에 장선을 대고 바닥틀을 짭니다.","기둥(89×89)을 세워 바닥틀에 고정하고 수평을 맞춥니다.","윗판(폭 140) "+bn+"장을 틈을 띄워 깔고 피스로 고정합니다."]}
 else if(p.t=="box"){A(0,0,0,0,W,th,H);A(0,0,D-th,0,W,th,H);A(0,0,th,0,th,D-2*th,H);A(0,W-th,th,0,th,D-2*th,H);A(1,th,th,th,W-2*th,D-2*th,th);
  C=["앞뒤판("+W+"×"+H+") 사이에 옆판을 끼워 사각 틀을 만듭니다.","틀 안쪽에 바닥판("+(W-2*th)+"×"+(D-2*th)+")을 고정합니다."]}
 else if(t.sh&&t.ha){var a=t.sh[0],b=t.sh[1];A(-1,0,-100,0,W,100,H);for(i=0;i<=W;i+=455)A(0,Math.min(i,W-38),0,0,38,38,H);for(i=0;i<W;i+=a)for(j=0;j<H;j+=b)A(1,i+2,38,j+2,Math.min(a,W-i)-4,th,Math.min(b,H-j)-4);
  C=["벽에 하지 각재를 455 간격으로 세워 고정합니다.",MT[t.m][0]+" 원판("+a+"×"+b+")을 각재 위에서 이음이 생기게 붙입니다."]}
 else if(t.sh){var a2=t.sh[0],b2=t.sh[1];A(-1,-60,-60,-40,W+120,D+120,40);for(j=0;j<D;j+=a2)for(i=-(j/a2%2)*b2/2;i<W;i+=b2){var x0=Math.max(0,i),x1=Math.min(W,i+b2);if(x1>x0)A(0,x0+2,j+2,0,x1-x0-4,Math.min(a2,D-j)-4,th)}
  C=["합판을 이음이 한 줄로 몰리지 않게 엇갈려 깔고 고정합니다."]}
 else if(t.bd){var nj2=Math.ceil(W/400)+1;for(i=0;i<nj2;i++)A(0,Math.min(i*400,W-38),0,0,38,D,89);var bw=145,row=0;for(j=0;j<D;j+=bw,row++){var off=(row%2)*t.bd[1]/2;for(i=-off;i<W;i+=t.bd[1]){var a3=Math.max(0,i),b3=Math.min(W,i+t.bd[1]);if(b3>a3)A(1,a3,j,89,b3-a3-3,Math.min(140,D-j),25)}}
  C=["장선(2×4)을 400 간격으로 놓고 수평을 맞춥니다.","데크재를 틈을 일정하게 띄워 깔고 장선마다 피스로 고정합니다."]}
 return{B:B,C:C}}
function iso(p,lock){var M=model(p),B=M.B,C=M.C,ng=C.length,co=Math.cos(Math.PI/6),si=.5,pr=function(x,y,z){return[(x-y)*co,(x+y)*si-z]};
 var mn=[1e9,1e9],mx=[-1e9,-1e9];B.forEach(function(o){var b=o.b;for(var a=0;a<8;a++){var q=pr(b[0]+(a&1?b[3]:0),b[1]+(a&2?b[4]:0),b[2]+(a&4?b[5]:0));mn[0]=Math.min(mn[0],q[0]);mn[1]=Math.min(mn[1],q[1]);mx[0]=Math.max(mx[0],q[0]);mx[1]=Math.max(mx[1],q[1])}});
 var PW=360,PH=250,k=Math.min((PW-40)/(mx[0]-mn[0]||1),(PH-40)/(mx[1]-mn[1]||1)),ox=(PW-(mx[0]-mn[0])*k)/2-mn[0]*k,oy=(PH-(mx[1]-mn[1])*k)/2-mn[1]*k;
 var S=(function(L){var n=L.length,e=1,ins=[],out=[],i,j,R=[],key=function(o){var a=o.b;return a[0]+a[3]/2+a[1]+a[4]/2+a[2]+a[5]/2};
 /* a가 b보다 먼저(뒤쪽) 그려져야 하면 true: 한 축에서 완전히 떨어져 있고 a가 보는 쪽 반대편 */
 var bef=function(a,b){return a[0]+a[3]<=b[0]+e||a[1]+a[4]<=b[1]+e||a[2]+a[5]<=b[2]+e};
 for(i=0;i<n;i++){ins.push(0);out.push([])}
 for(i=0;i<n;i++)for(j=0;j<n;j++)if(i!=j){var A=L[i].b,Bb=L[j].b;if(bef(A,Bb)&&!bef(Bb,A)){out[i].push(j);ins[j]++}}
 var q=[];for(i=0;i<n;i++)if(!ins[i])q.push(i);var done={};
 while(R.length<n){if(!q.length){var m=-1;for(i=0;i<n;i++)if(!done[i]&&(m<0||key(L[i])<key(L[m])))m=i;q.push(m)}
  q.sort(function(a,b){return key(L[a])-key(L[b])});var c=q.shift();if(done[c])continue;done[c]=1;R.push(L[c]);out[c].forEach(function(j){if(--ins[j]==0&&!done[j])q.push(j)})}
 return R})(B);
 function pt(x,y,z){var q=pr(x,y,z);return(q[0]*k+ox).toFixed(1)+","+(q[1]*k+oy).toFixed(1)}
 function face(c,f){return'<polygon points="'+c.join(" ")+'" fill="'+f[0]+'" stroke="'+f[1]+'" stroke-width="'+f[2]+'" stroke-linejoin="round"/>'}
 function panel(st){var o="";S.forEach(function(it){if(it.g>st&&st<ng)return;var b=it.b,x=b[0],y=b[1],z=b[2],w=b[3],d=b[4],h=b[5],cur=it.g==st,ctx=it.g<0;
  var top=cur?"#f08a52":ctx?"#d9d6d0":"#e6cfa6",fr=cur?"#e0703a":ctx?"#c9c5be":"#d4b98c",rt=cur?"#c95e2c":ctx?"#b9b4ac":"#bfa276",sk=cur?["#b3261e",1.6]:["#6b5a46",.6];
  o+=face([pt(x,y+d,z),pt(x+w,y+d,z),pt(x+w,y+d,z+h),pt(x,y+d,z+h)],[fr,sk[0],sk[1]])+face([pt(x+w,y,z),pt(x+w,y+d,z),pt(x+w,y+d,z+h),pt(x+w,y,z+h)],[rt,sk[0],sk[1]])+face([pt(x,y,z+h),pt(x+w,y,z+h),pt(x+w,y+d,z+h),pt(x,y+d,z+h)],[top,sk[0],sk[1]])});return o}
 var E=function(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})};
 var h='<div class="pl2iso">';for(var st=0;st<=ng;st++){var cap=st<ng?C[st]:"완성! 흔들림을 확인하고 모서리를 사포로 다듬은 뒤 오일·스테인으로 마감합니다.";if(lock)cap=cap.replace(/\d+(×\d+)+|\d{3,5}/g,"●●●");
  h+='<figure><svg viewBox="0 0 '+PW+' '+PH+'" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="13" fill="#c0392b"/><text x="20" y="25" text-anchor="middle" font-size="14" font-weight="800" fill="#fff">'+(st+1)+'</text>'+panel(st)+'</svg><figcaption>'+E(cap)+'</figcaption></figure>'}
 return h+'</div><p class="pl2isoc">빨간색이 그 단계에서 새로 붙이는 부재예요.</p>'}
window.PL2={iso:iso,model:model,steps:steps,T:T,MT:MT,guess:guess,dims:dims,parts:parts,svg:svg,table:table};
})();
