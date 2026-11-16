# 떨이몰(/tteori/) — 매장 악성재고·자투리·B급을 싸게. 사장님이 사진+한 줄을 주면 add_tteori.py 로 등록.
# 데이터 src/data/tteori.tsv: id|등록일|제목|규격|수량|가격(원, 숫자 또는 빈칸=매장 문의)|단위|설명|사진들(쉼표)|상태(판매중/판매완료)
# 가격·수량은 사장님이 준 그대로만. 가짜 할인율·가짜 재고·가짜 마감 시간 금지.
import os, json

COLS = ["id", "date", "title", "size", "qty", "price", "unit", "note", "photos", "status"]


def load(ROOT):
    f = os.path.join(ROOT, "data", "tteori.tsv")
    if not os.path.exists(f): return []
    out = []
    for ln in open(f, encoding="utf-8"):
        if not ln.strip() or ln.startswith("#"): continue
        c = (ln.rstrip("\n").split("|") + [""] * 10)[:10]
        d = dict(zip(COLS, c)); d["photos"] = [p for p in d["photos"].split(",") if p]
        out.append(d)
    out.sort(key=lambda d: (d["status"] == "판매완료", d["date"]), reverse=False)
    on = sorted([d for d in out if d["status"] != "판매완료"], key=lambda d: d["date"], reverse=True)
    off = sorted([d for d in out if d["status"] == "판매완료"], key=lambda d: d["date"], reverse=True)
    return on + off


def won(p):
    try: return f"{int(p):,}원"
    except Exception: return ""


def gen(page, E, CTA, TEL, ADDR, HOURS, BASE, ROOT):
    T = TEL.replace("-", "")
    items = load(ROOT)
    def card(d):
        so = d["status"] == "판매완료"
        im = d["photos"][0] if d["photos"] else ""
        pr = won(d["price"])
        return (f'<a class="ttc{" so" if so else ""}" href="/tteori/{d["id"]}.html">' + (f'<span class="tti"><img loading="lazy" src="/assets/tteori/{im}" alt="{E(d["title"])}">' + ('<em>판매완료</em>' if so else '') + '</span>' if im else '')
                + f'<b>{E(d["title"])}</b><small>{E(d["size"])}{(" · " + E(d["qty"])) if d["qty"] else ""}</small>'
                + f'<span class="ttp">{(pr + ("/" + E(d["unit"]) if d["unit"] else "")) if pr else "매장 문의"}</span><i>{E(d["date"][5:].replace("-", "/"))} 등록</i></a>')
    on = [d for d in items if d["status"] != "판매완료"]
    grid = "".join(card(d) for d in items) or '<div class="ttem"><b>지금 올라온 떨이 상품이 없어요</b><span>매장에 자투리·B급·재고 정리 자재가 생기면 사진과 함께 여기에 올립니다. 홈 화면에 추가해 두시면 바로 보실 수 있어요.</span></div>'
    css = '''<style>.ttg{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:14px 0}.ttc{display:flex;flex-direction:column;gap:3px;background:#fff;border:1px solid #ece6dc;border-radius:16px;padding:8px 8px 12px;color:#1D1B18!important;text-decoration:none!important}
.tti{position:relative;display:block}.tti img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:11px;display:block;margin-bottom:4px}.tti em{position:absolute;inset:0;display:grid;place-items:center;background:rgba(0,0,0,.55);color:#fff;font-style:normal;font-weight:900;font-size:18px;border-radius:11px}
.ttc b{font-size:15px;line-height:1.35;padding:0 4px}.ttc small{font-size:12.5px;color:#6b655c;padding:0 4px}.ttp{font-size:18px;font-weight:900;color:#c41a1f;padding:2px 4px 0}.ttc i{font-style:normal;font-size:11.5px;color:#9a9388;padding:0 4px}.ttc.so{opacity:.75}.ttc.so .ttp{color:#8a8378;text-decoration:line-through}
.ttr{display:flex!important;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;gap:10px;padding-bottom:6px}.ttr::-webkit-scrollbar{display:none}.ttr .ttc{flex:0 0 44%;scroll-snap-align:start}.tths{font-size:13px;color:#8a8378;font-weight:700}
.ttem{grid-column:1/-1;display:flex;flex-direction:column;gap:6px;background:#fff;border:1px dashed #d8d0c2;border-radius:16px;padding:20px;text-align:center}
.tthero{background:#1D1B18;color:#fff;border-radius:18px;padding:16px;margin:12px 0}.tthero b{font-size:18px;display:block;margin-bottom:4px}.tthero span{opacity:.85;font-size:14px;line-height:1.6}
.ttph{display:flex;gap:8px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none}.ttph img{flex:0 0 100%;width:100%;aspect-ratio:1;object-fit:cover;border-radius:16px;scroll-snap-align:start}
.ttbox{background:#fff;border:1px solid #ece6dc;border-radius:16px;padding:14px;margin:12px 0}.ttbox table{width:100%;border-collapse:collapse}.ttbox th{text-align:left;color:#6b655c;font-weight:700;width:30%;padding:7px 0;font-size:14px}.ttbox td{padding:7px 0;font-weight:800;font-size:15px}.ttbig{font-size:26px;font-weight:900;color:#c41a1f}</style>'''
    how = '<div class="tthero"><b>🏷 떨이몰 — 매장 재고 정리 자재</b><span>자투리·B급·단종·재고 정리 자재를 싸게 내놓습니다. 수량이 적어 <b>먼저 오시는 분께</b> 드려요. 전화로 남아 있는지 확인하고 오세요.</span></div>'
    page("tteori/index.html", "떨이몰 — 목재·건축자재 재고 정리, 자투리·B급 싸게 | 대전 영진목재",
         "대전 영진종합목재 매장의 자투리·B급·단종·재고 정리 자재를 사진과 가격으로. 수량 한정, 전화로 재고 확인 후 방문.",
         f'<section class="wrap sec"><h1>떨이몰</h1>{how}<div class="ttg">{grid}</div><div class="row"><a class="b r" href="tel:{T}">재고 확인 전화 {TEL}</a><a class="b" href="/visit.html">매장 길찾기</a></div><p class="small muted">사진은 매장에서 직접 찍은 실물입니다. 가격은 부가세 별도이며 표시 수량이 다 팔리면 판매완료로 바뀝니다.</p></section>{CTA}{css}',
         "/tteori/", None, (BASE + "/assets/tteori/" + on[0]["photos"][0]) if on and on[0]["photos"] else None)
    for d in items:
        so = d["status"] == "판매완료"
        pr = won(d["price"])
        ph = "".join(f'<img src="/assets/tteori/{p}" alt="{E(d["title"])} 실물 사진 {k + 1}"{" loading=lazy" if k else ""}>' for k, p in enumerate(d["photos"]))
        rows = "".join(f'<tr><th>{a}</th><td>{E(b)}</td></tr>' for a, b in (("규격", d["size"]), ("수량", d["qty"]), ("등록일", d["date"])) if b)
        body = (f'<section class="wrap sec"><p class="crumb"><a href="/tteori/">떨이몰</a> › {E(d["title"])}</p><h1>{E(d["title"])}{" (판매완료)" if so else ""}</h1>'
                + (f'<div class="ttph">{ph}</div>' + (f'<p class="hsh">옆으로 넘겨 보세요 ›</p>' if len(d["photos"]) > 1 else '') if ph else '')
                + f'<div class="ttbox"><div class="ttbig">{(pr + ("/" + E(d["unit"]) if d["unit"] else "")) if pr else "가격은 매장 문의"}</div><table>{rows}</table>' + (f'<p style="margin:8px 0 0;line-height:1.7">{E(d["note"])}</p>' if d["note"] else '') + '</div>'
                + ('<p class="tthero"><b>판매가 끝났어요</b><span>비슷한 자재는 매장에 문의해 주세요.</span></p>' if so else f'<div class="row"><a class="b r" href="tel:{T}">남았는지 전화 확인 {TEL}</a><a class="b" href="/visit.html">매장 길찾기</a></div><p class="small muted">수량이 적어 먼저 오시는 분께 드립니다. {E(ADDR)} · {E(HOURS)} · 부가세 별도.</p>')
                + f'<h2>다른 떨이 상품 <small class="tths">옆으로 넘겨 보세요 ›</small></h2><div class="ttg ttr">{"".join(card(x) for x in items if x["id"] != d["id"])[:20000] or "<p>다른 상품이 없어요.</p>"}</div></section>{CTA}{css}')
        ld = None
        if pr and d["photos"]:
            ld = {"@context": "https://schema.org", "@type": "Product", "name": d["title"], "image": [BASE + "/assets/tteori/" + p for p in d["photos"]], "description": (d["note"] or d["title"])[:200],
                  "offers": {"@type": "Offer", "price": int(d["price"]), "priceCurrency": "KRW", "availability": "https://schema.org/" + ("SoldOut" if so else "InStoreOnly"),
                             "seller": {"@type": "Organization", "name": "영진종합목재"}}}
        page(f"tteori/{d['id']}.html", f"{d['title']}{' ' + d['size'] if d['size'] else ''} — 떨이 {pr or '매장 문의'}{' (판매완료)' if so else ''} | 대전 영진목재",
             f"{d['title']} {d['size']} {d['qty']} 재고 정리 {pr or ''}. {d['note'][:80]} 대전 영진종합목재 매장, 수량 한정.", body, "/tteori/", ld,
             (BASE + "/assets/tteori/" + d["photos"][0]) if d["photos"] else None)
    return items
