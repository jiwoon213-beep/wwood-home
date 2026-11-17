# DIY 만들기 무료 도면 PDF (A4 2쪽: 완성 그림·재단표·자재·순서 / 그림 설명서)
# Pillow 만으로 그림 PDF를 만든다. 내용이 바뀐 것만 다시 만든다(해시 기록).
import os, json, hashlib, textwrap
from PIL import Image, ImageDraw, ImageFont

FONTS = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
         "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"]
W, H = 1240, 1754  # A4 150dpi
INK, MUTE, RED, LINE, BG = (29, 27, 24), (110, 104, 96), (176, 106, 44), (220, 212, 198), (250, 247, 241)


def _font(sz, bold=True):
    for p in (FONTS if bold else FONTS[1:2] + FONTS):
        if os.path.exists(p):
            try: return ImageFont.truetype(p, sz)
            except Exception: pass
    return None


def _wrap(d, text, f, maxw):
    out, cur = [], ""
    for ch in text:
        if d.textlength(cur + ch, font=f) > maxw and cur:
            out.append(cur); cur = ch.lstrip()
        else: cur += ch
    if cur: out.append(cur)
    return out


def _page(base, slug, title, url, pg, total):
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 96], fill=INK)
    d.text((60, 26), "영진종합목재 · 월드건축자재", font=_font(30), fill="white")
    d.text((W - 60, 32), "무료 DIY 도면", font=_font(26), fill=(240, 200, 150), anchor="ra")
    d.rectangle([0, H - 80, W, H], fill=BG); d.line([0, H - 80, W, H - 80], fill=LINE, width=2)
    d.text((60, H - 58), f"{url}  ·  재단·자재: 042-545-2900  ·  대전 유성구 유성대로 44", font=_font(20, False), fill=MUTE)
    d.text((W - 60, H - 58), f"{pg}/{total}", font=_font(20, False), fill=MUTE, anchor="ra")
    d.text((60, H - 112), "© 영진종합목재. 개인 사용·인쇄는 자유, 무단 재배포·상업적 사용 금지.", font=_font(17, False), fill=MUTE)
    return im, d


def make(root, slug, nm, title, lead, lines, steps, mats, base):
    """lines: [(부분, 재단 설명, 수량)] — 새로 만들었으면 True"""
    fd = _font(20)
    if fd is None: return False
    hero = f"{root}/assets/mandeul/{slug}.jpg"; stp = f"{root}/assets/mandeul/{slug}-steps.jpg"
    out = f"{root}/assets/mandeul/pdf/{slug}.pdf"
    url = f"www.wwood.co.kr/mandeul/{slug}.html"
    key = json.dumps([nm, title, lead, lines, steps, mats, os.path.getsize(hero) if os.path.exists(hero) else 0,
                      os.path.getsize(stp) if os.path.exists(stp) else 0, 3], ensure_ascii=False)
    h = hashlib.md5(key.encode()).hexdigest()[:12]
    hp = f"{root}/data/mkpdf_hash.json"
    try: H_ = json.load(open(hp))
    except Exception: H_ = {}
    if H_.get(slug) == h and os.path.exists(out): return False
    os.makedirs(os.path.dirname(out), exist_ok=True)
    total = 2 if os.path.exists(stp) else 1
    im, d = _page(base, slug, title, url, 1, total)
    y = 130
    d.text((60, y), f"{nm} 만들기 도면", font=_font(52), fill=INK); y += 78
    for ln in _wrap(d, lead, _font(24, False), W - 120)[:3]:
        d.text((60, y), ln, font=_font(24, False), fill=MUTE); y += 36
    y += 12
    if os.path.exists(hero):
        hi = Image.open(hero).convert("RGB"); tw = W - 120; th = int(hi.height * tw / hi.width)
        th = min(th, 560); hi = hi.resize((tw, int(hi.height * tw / hi.width)), Image.LANCZOS).crop((0, 0, tw, th))
        im.paste(hi, (60, y)); d.rectangle([60, y, 60 + tw, y + th], outline=LINE, width=2); y += th + 26
    # 재단표
    d.text((60, y), "재단 목록 (톱날 3mm 감안)", font=_font(30), fill=RED); y += 50
    cx = [60, 250, 930, W - 60]
    d.rectangle([60, y, W - 60, y + 44], fill=BG)
    for i, t in enumerate(["부분", "자재 · 재단 크기", "필요 수량"]): d.text((cx[i] + 14, y + 9), t, font=_font(22), fill=INK)
    y += 44
    for part, desc, cnt in lines:
        f2 = _font(21, False)
        dl = _wrap(d, desc, f2, cx[2] - cx[1] - 28); cl = _wrap(d, cnt, f2, cx[3] - cx[2] - 28)
        rh = max(len(dl), len(cl), 1) * 30 + 16
        d.text((cx[0] + 14, y + 8), part, font=_font(21), fill=INK)
        for i, l in enumerate(dl): d.text((cx[1] + 14, y + 8 + i * 30), l, font=f2, fill=INK)
        for i, l in enumerate(cl): d.text((cx[2] + 14, y + 8 + i * 30), l, font=f2, fill=INK)
        y += rh; d.line([60, y, W - 60, y], fill=LINE, width=1)
    y += 26
    # 순서 + 준비물 (2단)
    colw = (W - 120 - 40) // 2; y0 = y
    d.text((60, y), "만드는 순서", font=_font(30), fill=RED); y += 48
    for i, s in enumerate(steps, 1):
        ls = _wrap(d, s, _font(21, False), colw - 44)
        d.ellipse([60, y + 2, 92, y + 34], fill=INK); d.text((76, y + 18), str(i), font=_font(18), fill="white", anchor="mm")
        for j, l in enumerate(ls): d.text((104, y + 4 + j * 30), l, font=_font(21, False), fill=INK)
        y += len(ls) * 30 + 14
        if y > H - 170: break
    x2 = 60 + colw + 40; y2 = y0
    d.text((x2, y2), "준비할 자재·공구", font=_font(30), fill=RED); y2 += 48
    for m in mats:
        for j, l in enumerate(_wrap(d, "□ " + m, _font(21, False), colw)):
            d.text((x2, y2), l, font=_font(21, False), fill=INK); y2 += 30
        y2 += 6
    y2 += 14
    for l in ["자재·재단은 매장에서 한 번에.", "이 도면을 보여주시면 바로 재단해 드립니다.", "재단비 12T 이하 1컷 1,000원~ (두께별)"]:
        d.text((x2, y2), l, font=_font(20, False), fill=MUTE); y2 += 30
    pages = [im]
    if total == 2:
        im2, d2 = _page(base, slug, title, url, 2, total)
        d2.text((60, 130), f"{nm} 만드는 순서 그림 설명서", font=_font(40), fill=INK)
        d2.text((60, 190), "빨간 테두리가 그 단계에서 새로 붙이는 부재입니다.", font=_font(22, False), fill=MUTE)
        si = Image.open(stp).convert("RGB"); tw = W - 120; th = int(si.height * tw / si.width)
        mh = H - 260 - 140
        if th > mh: tw = int(tw * mh / th); th = mh
        im2.paste(si.resize((tw, th), Image.LANCZOS), ((W - tw) // 2, 240))
        pages.append(im2)
    tmp = out + ".tmp"
    pages[0].save(tmp, "PDF", resolution=150, save_all=True, append_images=pages[1:], quality=82,
                  title=f"{nm} 만들기 도면 - 영진종합목재", author="영진종합목재(월드건축자재)")
    os.replace(tmp, out)
    H_[slug] = h; json.dump(H_, open(hp, "w"), ensure_ascii=False, indent=0, sort_keys=True)
    return True
