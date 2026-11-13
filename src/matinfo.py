# -*- coding: utf-8 -*-
"""DIY 만들기·자재 시공법의 '준비할 자재'·'필요한 공구'를 자세하게(피스 길이·제품) 만들고
판재·각재는 재단 미리보기(/cut.html, 해당 자재 선택), 부자재·공구는 철물·공구·부속(/bupum/) 해당 분류로 연결합니다.
피스 길이는 일반 기준(고정할 판 두께의 약 2~2.5배)으로 안내하는 참고치입니다."""
import re

# 철물·공구·부속 분류번호
B = {"목공피스": 277, "목공피스봉": 281, "직결피스": 278, "스텐피스": 279, "피스세트": 280, "칼블럭": 285, "앙카": 286,
     "볼트": 289, "접착제": 259, "실리콘": 260, "우레탄폼": 261, "페인트": 262, "테이프": 257, "제거제": 258,
     "보강철물": 170, "서랍레일": 162, "조절발": 163, "바퀴": 164, "다리": 165, "쇼바": 166, "가구경첩": 133, "씽크경첩": 131,
     "가구손잡이": 118, "다보": 175, "고리": 181, "다용도걸이": 183, "선반": 64, "목재보강": 188, "정자철물": 189, "기초보강": 187,
     "드릴": 248, "절단": 250, "사포": 226, "클램프": 230, "줄자": 235, "직각자": 236, "수평기": 237, "각도자": 238,
     "페인트공구": 231, "실리콘건": 232, "미장공구": 228, "망치": 227, "톱": 225, "커터칼": 223, "드라이버": 229,
     "장갑": 241, "보안경": 242, "마스크": 244, "에어공구": 249, "모서리몰딩": 457, "논슬립": 89, "보양재": 486}


class M:
    def __init__(self, E, cutlink, catlink):
        self.E, self.cut, self.cl = E, cutlink, catlink

    def bl(self, key, label=None):
        u = self.cl(B[key]) if key in B else ""
        return f'<a class="mlk" href="{u}">{self.E(label or "제품 보기")} ›</a>' if u else ""

    # ── 판재·각재 → 재단 미리보기 ──
    @staticmethod
    def panel(t):
        if re.search(r"피스|못|핀|타카|테이프|퍼티|본드|클립|몰딩|걸레받이|철물|마감재|실리콘|폼", t): return None
        th = re.search(r"(\d+(?:\.\d+)?)\s*(?:T|mm)", t)
        th = th.group(1) if th else ""
        num = (lambda v: rf"(?<![\d.]){re.escape(v)}(?![\d])") if th else (lambda v: "")
        dm = re.search(r"(\d)\s*[×x\*]\s*(\d)(?!\d)", t)
        dk = re.search(r"(\d{2})\s*[×x\*]\s*(\d{2,3})", t)
        if "석고" in t: return ("석고보드", r"9\.5" if "9.5" in t else "")
        if re.search("아이소핑크|단열", t): return ("단열재", num(th) if th else r"30")
        if "OSB" in t: return ("합판", r"OSB")
        if "MDF" in t: return ("MDF", num(th))
        if "집성" in t and "각" not in t: return ("집성판", num(th))
        if "합판" in t: return ("합판", num(th))
        if "다루끼" in t: return ("각재·다루끼", r"다루끼|1\.0")
        if "방부목" in t or "데크재" in t:
            if dk: return ("방부목", rf"{dk.group(1)}\*{dk.group(2)}")
            if dm: return ("방부목", rf"{dm.group(1)}\* ?{dm.group(2)}")
            return ("방부목", "")
        if "구조재" in t: return ("구조재", rf"{dm.group(1)}\* ?{dm.group(2)}" if dm else "")
        return None

    def cutfor(self, t, rows):
        pc = self.panel(t)
        if not pc: return ""
        cat, rx = pc
        for part, c, r, parts, desc in rows or []:  # 이 페이지 재단표에 같은 자재가 있으면 그 크기 그대로
            if c == cat and (not rx or re.search(rx, desc + " " + r.replace("\\", "")) or len([1 for x in rows if x[1] == cat]) == 1):
                allp = [p for x in rows if x[1] == c and x[2] == r for p in x[3]]
                return f'<a class="mlk c" href="{self.cut(c, r, allp)}">재단 그림 ›</a>'
        return f'<a class="mlk c" href="{self.cut(cat, rx, [])}">재단 미리보기 ›</a>'

    # ── 피스 길이 추천 ──
    @staticmethod
    def thick(mats, rows):
        txt = " ".join(mats) + " " + " ".join(r[4] + " " + r[1] for r in rows or [])
        out = set()
        for m in re.finditer(r"(\d+(?:\.\d+)?)\s*T", txt): out.add(float(m.group(1)))
        for m in re.finditer(r"MDF\s*(\d+)\s*mm|합판\s*(\d+)\s*mm", txt): out.add(float(m.group(1) or m.group(2)))
        if re.search(r"2\s*[×x\*]\s*[246]|4\s*[×x\*]\s*4|구조재", txt): out.add(38.0)
        if re.search(r"25\s*[×x\*]\s*140|데크재\s*25", txt): out.add(25.0)
        if re.search(r"20\s*[×x\*]\s*120", txt): out.add(20.0)
        return out, txt

    @staticmethod
    def plen(t):  # 고정할 판 두께 → 권장 피스 길이(mm)
        need = t * 2.2
        for L in (16, 25, 32, 38, 41, 50, 57, 65, 75, 90):
            if L >= need: return L
        return 90

    def screws(self, mats, rows):
        th, txt = self.thick(mats, rows)
        outdoor = bool(re.search("방부목|데크|외부|야외|울타리|평상", txt))
        rec = []
        if 38.0 in th: rec.append(("각재 38mm(2×4·4×4) 고정", "스텐 피스 65~75mm" if outdoor else "구조용 피스 65~75mm", "스텐피스" if outdoor else "목공피스봉"))
        if 25.0 in th and outdoor: rec.append(("데크재 25T 상판", "스텐 데크 피스 50mm (장선마다 2개)", "스텐피스"))
        if 20.0 in th and outdoor: rec.append(("데크재 20T 상판", "스텐 데크 피스 45mm", "스텐피스"))
        for t in sorted(x for x in th if 9 <= x <= 32 and x not in (20.0, 25.0) or (x in (20.0, 25.0) and not outdoor)):
            L = self.plen(t)
            d = "3.5" if L <= 41 else "4"
            rec.append((f"{t:g}T 판 고정", f"{'스텐 ' if outdoor else '목공 '}피스 {d}×{L}mm", "스텐피스" if outdoor else "목공피스"))
        if any(x <= 6 for x in th): rec.append(("뒷판(6mm 이하)", "실타카 F15~F19 또는 3×16mm 짧은 피스", "taka"))
        return rec

    # ── DIY 만들기: 준비할 자재 목록 ──
    def mk_list(self, mats, rows, steps=()):
        E = self.E
        rec = self.screws(mats, rows)
        li, used = [], set()
        for t in mats:
            links, note = self.cutfor(t, rows), ""
            if re.search("피스|못", t) and not re.search("석고|콘크리트|앵커", t):
                for lab, what, key in rec:
                    if lab in used: continue
                    used.add(lab)
                    note += f'<span class="mnote">{E(lab)}: <b>{E(what)}</b></span>'
                    if key not in used: links += f'<a class="mlk" href="/taka/">타카핀 보기 ›</a>' if key == "taka" else self.bl(key, "피스 보기")
                    used.add(key)
                if not note:
                    links += self.bl("목공피스", "피스 보기")
                if "본드" in t: links += self.bl("접착제", "본드 보기"); note += '<span class="mnote">맞닿는 면에 목공본드를 얇게 바르고 피스로 조이면 훨씬 튼튼합니다.</span>'
                if "목심" in t: note += '<span class="mnote">피스 구멍은 8mm 목심으로 메우고 사포로 평평하게.</span>'
            elif re.search("석고 피스|콘크리트못", t):
                note = '<span class="mnote">석고 피스 <b>25~32mm</b>, 콘크리트 벽은 칼블럭 6mm + 피스</span>'; links += self.bl("직결피스", "피스 보기") + self.bl("칼블럭", "칼블럭 보기")
            elif re.search("앵커|앙카", t):
                note = '<span class="mnote">콘크리트 벽: 칼블럭 6~8mm + 피스 4×40mm 이상</span>'; links += self.bl("칼블럭", "칼블럭 보기") + self.bl("앙카", "앙카 보기")
            elif re.search("넘어짐|ㄱ자 철물|L자 철물|브라켓", t):
                note = '<span class="mnote">벽 고정은 칼블럭 + 피스, 가구 쪽은 16~25mm 피스</span>'; links += self.bl("보강철물", "철물 보기")
            elif "싱크 경첩" in t or "35mm" in t:
                note = '<span class="mnote">문짝에 35mm 구멍(포스트너 비트) + 피스 3.5×16mm</span>'; links += self.bl("씽크경첩", "경첩 보기")
            elif "경첩" in t:
                links += self.bl("가구경첩", "경첩 보기") + (self.bl("가구손잡이", "손잡이 보기") if "손잡이" in t else "")
            elif "손잡이" in t: links += self.bl("가구손잡이", "손잡이 보기")
            elif "지지대" in t: links += self.bl("쇼바", "지지대 보기")
            elif "바퀴" in t: links += self.bl("바퀴", "바퀴 보기") + self.bl("조절발", "가구 발 보기")
            elif re.search("가구 발|미끄럼|패드", t): links += self.bl("조절발", "가구 발 보기")
            elif "다리" in t: links += self.bl("다리", "다리 보기")
            elif re.search("고리", t): links += self.bl("고리", "고리 보기")
            elif re.search("오일스테인", t): links += '<a class="mlk" href="/gagyeok/oilstain.html">오일스테인 가격 ›</a>' + self.bl("페인트공구", "붓·롤러 보기")
            elif re.search("오일|바니시|페인트", t): links += self.bl("페인트", "도료 보기") + self.bl("페인트공구", "붓·롤러 보기")
            elif "사포" in t: note = '<span class="mnote">#120으로 모서리 → #220으로 마감</span>'; links += self.bl("사포", "사포 보기")
            elif "우레탄폼" in t: links += self.bl("우레탄폼", "폼 보기")
            elif re.search("퍼티|조인트", t): links += self.bl("미장공구", "헤라 보기")
            elif re.search("주춧돌|받침|기초|블록|레미탈", t): links += '<a class="mlk" href="/cheolmul/juchudol.html">주춧돌·기초 ›</a>'
            elif "직소" in t: links += self.bl("절단", "직소 보기")
            li.append(f"<li><b>{E(t)}</b>{note}{('<span class=mlks>' + links + '</span>') if links else ''}</li>")
        for lab, what, key in rec:  # 자재 목록에 피스가 없었던 경우에도 안내
            if lab in used: continue
            used.add(lab)
            li.append(f'<li><b>{E(what)}</b><span class="mnote">{E(lab)}</span><span class=mlks>' + ('<a class="mlk" href="/taka/">타카핀 보기 ›</a>' if key == "taka" else self.bl(key, "피스 보기")) + '</span></li>')
        return "".join(li)

    def mk_tools(self, mats, rows, steps=()):
        th, txt = self.thick(mats, rows)
        txt += " " + " ".join(steps)
        T = [("충전 드릴·드라이버", "드릴", "피스 박기 + 3mm 기리로 먼저 구멍(집성판 갈라짐 방지)"), ("줄자·직각자", "줄자", "")]
        if re.search("본드|집성|합판|MDF", txt): T.append(("클램프 2개 이상", "클램프", "본드 굳는 동안 고정"))
        if any(x <= 6 for x in th): T.append(("실타카(에어·충전)", None, "뒷판 고정"))
        if re.search("곡선|직소", txt): T.append(("직소", "절단", "곡선 따기"))
        if re.search("오일|바니시|페인트|스테인|사포", txt): T.append(("사포·샌딩 블록", "사포", "")); T.append(("붓·롤러", "페인트공구", ""))
        if re.search("앵커|칼블럭|콘크리트|벽에 고정|벽 고정", txt): T.append(("해머 드릴(콘크리트 비트)", "드릴", "벽 고정 구멍"))
        if re.search("수평|기초|주춧돌|평상|데크", txt): T.append(("수평기", "수평기", ""))
        T.append(("장갑·보안경", "장갑", ""))
        E = self.E
        return "".join(f'<li><b>{E(n)}</b>{f"<span class=mnote>{E(d)}</span>" if d else ""}<span class=mlks>' + ('<a class="mlk" href="/taka/">타카 보기 ›</a>' if k is None else self.bl(k, "제품 보기")) + "</span></li>" for n, k, d in T)

    # ── 자재 시공법: 표의 자재 이름 옆 링크 ──
    def sg_links(self, name, spec):
        t = name + " " + spec
        l = self.cutfor(t, [])
        if re.search("석고 피스", t): l += self.bl("직결피스", "피스")
        elif re.search("데크 클립", t): l += '<a class="mlk" href="/cheolmul/deck-fence.html">데크 철물 ›</a>'
        elif re.search("스텐 못|스텐 피스", t): l += self.bl("스텐피스", "피스")
        elif re.search("피스", t): l += self.bl("목공피스", "피스")
        if re.search("칼블럭|콘크리트 고정|콘크리트못", t): l += self.bl("칼블럭", "칼블럭")
        if re.search("실타카|타카", t): l += '<a class="mlk" href="/taka/">타카핀 ›</a>'
        if re.search("본드", t): l += self.bl("접착제", "본드")
        if re.search("실리콘", t): l += self.bl("실리콘", "실리콘")
        if re.search("우레탄폼|폼본드", t): l += self.bl("우레탄폼", "폼")
        if re.search("테이프", t): l += self.bl("테이프", "테이프")
        if re.search("오일스테인", t): l += '<a class="mlk" href="/gagyeok/oilstain.html">가격 ›</a>'
        if re.search("사포", t): l += self.bl("사포", "사포")
        if re.search("붓|롤러|헤라", t): l += self.bl("페인트공구" if re.search("붓|롤러", t) else "미장공구", "공구")
        if re.search("몰딩|걸레받이", t): l += '<a class="mlk" href="/gagyeok/molding-gagyeok.html">몰딩 가격 ›</a>'
        if re.search("템바보드", t): l += '<a class="mlk" href="/gagyeok/tempa-board.html">가격 ›</a>'
        if re.search("루바", t): l += '<a class="mlk" href="/gagyeok/hinoki-ruba.html">가격 ›</a>'
        if re.search("필름", t): l += '<a class="mlk" href="/gagyeok/interior-film.html">가격 ›</a>'
        if re.search("문틀|문짝|행거", t): l += '<a class="mlk" href="/yerim/">문·문틀 사진 ›</a>'
        return f'<span class=mlks>{l}</span>' if l else ""

    def sg_tools(self, tools):
        E = self.E
        K = [("임팩트|드릴|드라이버", "드릴"), ("수평", "수평기"), ("줄자|먹줄", "줄자"), ("직각자", "직각자"), ("실리콘 건|본드 건|폼 건", "실리콘건"),
             ("원형톱|직소|각도 톱|마이터|그라인더|커터|재단기", "절단"), ("헤라", "미장공구"), ("망치", "망치"), ("붓|롤러", "페인트공구"),
             ("사포", "사포"), ("장갑", "장갑"), ("마스크", "마스크"), ("칼", "커터칼")]
        out = []
        for t in tools:
            k = next((k for rx, k in K if re.search(rx, t)), None)
            lk = '<a class="mlk" href="/taka/">타카 ›</a>' if re.search("타카", t) else (self.bl(k, "제품 보기") if k else "")
            out.append(f"<li><b>{E(t)}</b>{('<span class=mlks>' + lk + '</span>') if lk else ''}</li>")
        return "".join(out)
