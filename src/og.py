"""공유 대표 사진(카톡·검색 미리보기, 1200×630) 만들기 — src/assets/og/<이름>.jpg
폰트·Pillow가 없는 곳(예: Actions)에서는 건너뛰고, 이미 만든 파일을 그대로 씁니다."""
import os

FM = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
if not os.path.exists(FB): FB = FM
KR = 1  # ttc 안의 KR 폰트 번호


def _font(path, size):
    from PIL import ImageFont
    for i in (KR, 0, 2, 3, 4):
        try:
            f = ImageFont.truetype(path, size, index=i)
            if "KR" in " ".join(f.getname()):
                return f
        except Exception:
            pass
    return ImageFont.truetype(path, size)


def _wrap(d, text, font, width):
    lines, cur = [], ""
    for ch in text:
        if d.textlength(cur + ch, font=font) > width and cur:
            lines.append(cur); cur = ch.lstrip()
        else:
            cur += ch
    if cur: lines.append(cur)
    return lines


def make(root, name, title, sub="", big="", tag="영진종합목재 · 월드건축자재"):
    """big: 크게 강조할 숫자/가격(예: '127,200원~'). 반환: 사이트 경로(/assets/og/name.jpg) 또는 None"""
    out = os.path.join(root, "assets", "og", name + ".jpg")
    rel = "/assets/og/" + name + ".jpg"
    sig = os.path.join(root, "assets", "og", name + ".txt")
    key = "|".join((title, sub, big, tag))
    if os.path.exists(out) and os.path.exists(sig) and open(sig, encoding="utf-8").read() == key:
        return rel
    try:
        from PIL import Image, ImageDraw
        if not os.path.exists(FB): return rel if os.path.exists(out) else None
    except Exception:
        return rel if os.path.exists(out) else None
    os.makedirs(os.path.dirname(out), exist_ok=True)
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), (29, 27, 24))
    d = ImageDraw.Draw(im)
    # 나뭇결 느낌 줄무늬
    for y in range(0, H, 18):
        d.line([(0, y), (W, y + 40)], fill=(36, 33, 29), width=2)
    d.rectangle([0, 0, 18, H], fill=(196, 26, 31))
    d.rounded_rectangle([70, 64, 150, 144], 18, fill=(196, 26, 31))
    d.text((110, 104), "W", font=_font(FB, 58), fill="white", anchor="mm")
    d.text((172, 80), tag, font=_font(FM, 34), fill=(255, 210, 122))
    d.text((172, 122), "대전 유성 3000평 · 원하는 크기 즉석 재단 · 전국 배송", font=_font(FM, 24), fill=(190, 184, 174))
    ft = _font(FB, 74 if len(title) <= 14 else 62)
    y = 210
    for ln in _wrap(d, title, ft, W - 150)[:2]:
        d.text((70, y), ln, font=ft, fill="white"); y += ft.size + 18
    if sub:
        fs = _font(FM, 34)
        for ln in _wrap(d, sub, fs, W - 150)[:2]:
            d.text((70, y + 6), ln, font=fs, fill=(214, 208, 198)); y += 48
    if big:
        fb = _font(FB, 80)
        tw = d.textlength(big, font=fb)
        d.rounded_rectangle([60, H - 150, 60 + tw + 50, H - 46], 22, fill=(196, 26, 31))
        d.text((85, H - 98), big, font=fb, fill="white", anchor="lm")
    d.text((W - 60, H - 60), "www.wwood.co.kr", font=_font(FM, 30), fill=(150, 144, 134), anchor="rm")
    im.save(out, "JPEG", quality=84, optimize=True)
    open(sig, "w", encoding="utf-8").write(key)
    return rel
