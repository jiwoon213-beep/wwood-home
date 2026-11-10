// 유튜브 고정 댓글 도우미 — youtube.com 탭(로그인된 채널)에서 javascript_tool로 이 파일 내용을 그대로 실행한 뒤
// await __pinOne(영상ID, '/v/영상ID.html' 또는 '/jajae/slug.html', '분류이름') 호출. 결과: ok/already/otherpinned/posted-nopinact 등.
window.__sh=async function(){const sap=document.cookie.match(/SAPISID=([^;]+)/)[1];const t=Math.floor(Date.now()/1000);const b=await crypto.subtle.digest('SHA-1',new TextEncoder().encode(t+' '+sap+' https://www.youtube.com'));return 'SAPISIDHASH '+t+'_'+[...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join('');};
window.__yt=async function(ep,body){const ctx=JSON.parse(JSON.stringify(ytcfg.get('INNERTUBE_CONTEXT')));ctx.user={...ctx.user,onBehalfOfUser:ytcfg.get('DELEGATED_SESSION_ID')};const r=await fetch('/youtubei/v1/'+ep+'?prettyPrint=false',{method:'POST',headers:{'Content-Type':'application/json','Authorization':await __sh(),'X-Origin':'https://www.youtube.com','X-Goog-AuthUser':'0','X-Goog-PageId':ytcfg.get('DELEGATED_SESSION_ID'),'X-Youtube-Client-Name':'1','X-Youtube-Client-Version':ytcfg.get('INNERTUBE_CLIENT_VERSION')},body:JSON.stringify({context:ctx,...body}),credentials:'include'});return [r.status,await r.json()];};
window.__cmts=async function(id){const [s,j]=await __yt('next',{videoId:id});const t=JSON.stringify(j);const ci=t.indexOf('comment-item-section');if(ci<0)return null;const sec=t.lastIndexOf('"continuationCommand"',ci);const tok=(t.slice(sec).match(/"token":"([^"]+)"/)||[])[1];if(!tok)return null;const [s2,j2]=await __yt('next',{continuation:tok});return JSON.stringify(j2);};
window.__pinMine=async function(id,t2){ t2=t2||await __cmts(id); if(!t2) return 'nocmts'; const wi=t2.indexOf('wwood.co.kr'); if(wi<0) return 'notfound'; const myid=(t2.slice(0,wi).match(/"commentId":"([^"]+)"[^]*$/)||[])[1]; const acts=[...t2.matchAll(/"performCommentActionEndpoint":\{"action":"([^"]+)"/g)].map(m=>m[1]).filter(a=>a.startsWith('CAsQ'));
 const dec=a=>{try{return atob(decodeURIComponent(a).replace(/-/g,'+').replace(/_/g,'/'))}catch(e){return ''}}; const a=acts.find(x=>myid&&dec(x).includes(myid)); if(!a) return 'nopinact'; const [s]=await __yt('comment/perform_comment_action',{actions:[a]}); return s===200?'ok':'pin'+s; };
window.__pinOne=async function(id,path,cat){
 const t2=await __cmts(id); if(!t2) return 'nocomments';
 if(t2.includes('wwood.co.kr')) return t2.includes('"pinnedText"')?'already':await __pinMine(id,t2);
 if(t2.includes('"pinnedText"')) return 'otherpinned';
 const p=(t2.match(/"createCommentParams":"([^"]+)"/)||[])[1]; if(!p) return 'noparams';
 const head=cat?`📍 영상 속 ${cat} 자재는`:'📍 영상 속 자재는';
 const txt=`${head} 대전 유성 영진목재(월드건축자재) 3000평 매장에서 실물 보고 원하는 사이즈로 재단해 드립니다.\n▶ 자재 사진·기준가·필요 수량 계산: https://www.wwood.co.kr${path}\n☎ 042-545-2900 · 대전 유성대로 44 · 대전·세종·공주·계룡·논산·금산·옥천 배송`;
 const [s3]=await __yt('comment/create_comment',{createCommentParams:p,commentText:txt}); if(s3!==200) return 'create'+s3;
 await new Promise(x=>setTimeout(x,5000)); let r=await __pinMine(id); if(r!=='ok'){ await new Promise(x=>setTimeout(x,8000)); r=await __pinMine(id);} return r==='ok'?'ok':'posted-'+r; };
'pin helpers loaded';
