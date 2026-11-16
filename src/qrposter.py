# 매장 카운터용 인쇄 안내문(/qr.html, 검색 제외) — 리뷰·홈페이지·재단 미리보기·떨이몰 QR. QR 그림은 손님 브라우저에서 api.qrserver.com 이 그림.
from urllib.parse import quote

ITEMS = [
    ("네이버 리뷰", "네이버 지도에서 영진목재 리뷰 남기기", "https://naver.me/GEdDcn2S", "#03c75a"),
    ("구글 리뷰", "구글 지도에 리뷰 남기기", "https://g.page/r/CZcZc9J-M0L0EAE/review", "#1a73e8"),
    ("재단 미리보기", "크기 넣으면 재단 그림·재단비 바로", "https://www.wwood.co.kr/cut.html", "#c41a1f"),
    ("떨이몰", "자투리·B급·재고 정리 싸게", "https://www.wwood.co.kr/tteori/", "#1D1B18"),
]


def gen(OUT):
    cards = "".join(f'<div class="q"><img src="https://api.qrserver.com/v1/create-qr-code/?size=360x360&margin=8&data={quote(u, safe="")}" alt="{n} QR"><b style="color:{c}">{n}</b><span>{d}</span></div>' for n, d, u, c in ITEMS)
    html = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>매장 QR 안내문(인쇄용) | 영진목재</title>
<style>@page{{size:A4;margin:12mm}}body{{font-family:'Noto Sans KR',sans-serif;margin:0;padding:16px;color:#1D1B18;background:#fff}}h1{{font-size:30px;margin:0 0 4px;text-align:center}}p.s{{text-align:center;font-size:17px;margin:0 0 18px;color:#555}}
.g{{display:grid;grid-template-columns:1fr 1fr;gap:16px;max-width:720px;margin:auto}}.q{{border:2px solid #e6dfd5;border-radius:18px;padding:14px;text-align:center;display:flex;flex-direction:column;align-items:center;gap:4px}}.q img{{width:100%;max-width:240px;aspect-ratio:1}}.q b{{font-size:24px}}.q span{{font-size:15px;color:#444}}
.bn{{max-width:720px;margin:0 auto 16px;background:#c41a1f;color:#fff;border-radius:16px;padding:14px;text-align:center;font-size:22px;font-weight:700}}.bn b{{font-size:26px;color:#ffe08a}}.bn small{{display:block;font-size:14px;opacity:.9;margin-top:4px;font-weight:500}}.f{{text-align:center;margin-top:18px;font-size:16px;font-weight:700}}.pb{{display:block;margin:16px auto;padding:12px 22px;font-size:17px;font-weight:800;border:0;border-radius:12px;background:#c41a1f;color:#fff}}@media print{{.pb{{display:none}}}}</style></head><body>
<h1>영진종합목재 · 월드건축자재</h1><p class="s">휴대폰 카메라로 찍어 보세요</p><div class="bn">✂ QR 찍은 화면을 보여 주시면 <b>재단 1컷 무료</b><small>리뷰 작성과 상관없이 QR을 찍으신 분 누구나 · 1회</small></div><div class="g">{cards}</div>
<p class="f">www.wwood.co.kr · 042-545-2900 · 대전 유성대로 44</p><button class="pb" onclick="print()">인쇄하기</button></body></html>'''
    open(f"{OUT}/qr.html", "w", encoding="utf-8").write(html)
