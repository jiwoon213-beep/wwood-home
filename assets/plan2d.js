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
window.PL2={T:T,MT:MT,guess:guess,dims:dims,parts:parts,svg:svg,table:table};
})();
