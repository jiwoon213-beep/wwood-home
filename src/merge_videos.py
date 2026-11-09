#!/usr/bin/env python3
"""채널 공개 영상 전체(yt_all.tsv: id, 종류 L/S/V, 조회수, 게시시각, 제목)를 videos.tsv에 합칩니다.
기존 영상은 분류·자재를 유지하고 조회수만 갱신, 새 영상은 제목 키워드로 분류합니다.
사용: python3 merge_videos.py data/yt_all.tsv"""
import csv, re, sys

MAT = [("osb", r"OSB"), ("mdf", r"MDF"), ("hapan", r"합판"), ("gujo", r"다루끼|각재|구조재|2x4|투바이"), ("bangbu", r"방부"),
       ("hapdeck", r"합성데크|합성목"), ("jipseong", r"집성"), ("hinoki", r"히노끼|편백|삼나무|적삼목|루바"), ("gypsum", r"석고보드"),
       ("siding", r"사이딩|외장재"), ("insul", r"단열|아이소핑크"), ("stain", r"오일스테인|스테인"), ("hardware", r"피스|타카|경첩|철물"),
       ("maru", r"강마루|강화마루|마루|장판|바닥재"), ("film", r"필름|시트지"), ("molding", r"몰딩|걸레받이"), ("chimmok", r"침목"),
       ("tile", r"타일"), ("sound", r"방음|흡음")]
CAT = [("deck", r"데크|마당|조경|화분|잔디|울타리|침목"), ("greenhouse", r"온실|비닐하우스|목조주택|하우스|지붕|트러스"),
       ("kitchen", r"싱크대|주방|아일랜드|수전"), ("exterior", r"샷시|샤시|창호|창문|외벽|사이딩|외장|베란다"),
       ("electric", r"전기|콘센트|조명|스위치|전선|배선|단열|아이소핑크|에어컨|경보기"), ("floor", r"마루|장판|바닥|타일|욕실|데코타일"),
       ("finish", r"도배|필름|페인트|칠하|실리콘|코킹|시트지"), ("wall", r"석고보드|가벽|몰딩|천장|천정|방음|목공|다루끼|아트월|문틀|문짝|방문|도어"),
       ("material", r"합판|MDF|OSB|집성|각재|구조재|자재|목재|원목|나무 종류|히노끼|루바"),
       ("furniture", r"가구|테이블|책상|선반|침대|책장|수납|만들기|DIY|의자|평상|박스|사다리|파티션|간판"),
       ("tool", r"공구|드릴|톱|타카|피스|못|안전")]

def first(rules, t):
    best, bi = None, 10**9
    for k, rx in rules:
        m = re.search(rx, t, re.I)
        if m and m.start() < bi: best, bi = k, m.start()
    return best

def main(src):
    old = {}
    for r in csv.reader(open("data/videos.tsv", encoding="utf-8"), delimiter="\t"):
        if len(r) >= 6: old[r[0]] = r
    rows, added = [], 0
    for r in csv.reader(open(src, encoding="utf-8"), delimiter="\t"):
        if len(r) < 5: continue
        vid, typ, n, ts, title = r[:5]
        title = re.sub(r"\s*#shorts?\b", "", title, flags=re.I).strip()
        if vid in old:
            o = old[vid]; rows.append([vid, typ, n or o[2], o[3], o[4], o[5]])
        else:
            cat = first(CAT, title) or "tips"
            mats = "/".join(dict.fromkeys(k for k, rx in MAT if re.search(rx, title, re.I)))
            rows.append([vid, typ, n or "0", cat, mats, title]); added += 1
    ids = {r[0] for r in rows}
    rows += [o for v, o in old.items() if v not in ids]  # 목록에 없던 기존 영상도 유지
    with open("data/videos.tsv", "w", encoding="utf-8", newline="") as f:
        csv.writer(f, delimiter="\t", lineterminator="\n").writerows(rows)
    print("total", len(rows), "added", added)

if __name__ == "__main__":
    main(sys.argv[1])
