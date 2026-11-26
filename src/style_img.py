# 스타일 따라 만들기 대표 그림(완성 모습+제목) 만들기 — 없는 것만. 크롬·playwright 있을 때만 동작.
import json,asyncio,os
from playwright.async_api import async_playwright
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
L=json.load(open('data/style_diy.json'))
js=open('assets/plan2d.js').read()
os.makedirs('assets/style',exist_ok=True)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':800,'height':600},device_scale_factor=1)
        await pg.set_content('<html><head><style>body{margin:0;background:#f6f3ee;font-family:"Noto Sans CJK KR",sans-serif}#w{width:800px;height:500px;display:flex;align-items:center;justify-content:center}#w svg{width:700px;height:470px}</style></head><body><div id="w"></div><div style="position:absolute;left:0;right:0;bottom:0;padding:14px 22px;background:rgba(29,27,24,.86);color:#fff"><div id="c1" style="font-size:30px;font-weight:900"></div><div style="display:flex;justify-content:space-between;font-size:20px;margin-top:4px;color:#e9e2d6"><span id="c2"></span><span>영진종합목재 wwood.co.kr</span></div></div><script>'+js+'</script></body></html>')
        n=0
        for x in L:
            out=f"assets/style/{x['slug']}.jpg"
            if os.path.exists(out): continue
            html=await pg.evaluate("p=>{var d=document.createElement('div');d.innerHTML=PL2.iso(p,0);var s=d.querySelectorAll('svg');return s.length?s[s.length-1].outerHTML:''}",x['plan'])
            cap=f"{x['brand']} {x['ref'].split('(')[0].strip()} 스타일 · {x['name']}"
            dim=f"{x['plan']['w']}×{x['plan']['d']}×{x['plan']['h']}mm · 2D 도면·재단 목록"
            await pg.evaluate("a=>{var w=document.getElementById('w');w.innerHTML=a[0];w.querySelectorAll('circle').forEach(function(c){var n=c.nextElementSibling;if(n&&n.tagName=='text')n.remove();c.remove()});document.getElementById('c1').textContent=a[1];document.getElementById('c2').textContent=a[2]}",[html,cap,dim])
            await pg.wait_for_timeout(50)
            await pg.screenshot(path=out,type='jpeg',quality=82); n+=1
        await b.close(); print('rendered',n)
if __name__=='__main__':
    if any(not os.path.exists(f"assets/style/{x['slug']}.jpg") for x in L): asyncio.run(main())
