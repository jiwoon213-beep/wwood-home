# wwood-home 저장소 규칙

- www.wwood.co.kr 홍보 사이트(GitHub Pages, main 브랜치 루트). 도매회원 쇼핑몰은 wwood.kr(이지스호스팅) 그대로.
- 사이트 파일은 `src/build.py`로 생성합니다: `cd src && python3 build.py https://www.wwood.co.kr && cp -r out/. ..` 후 `CNAME`(www.wwood.co.kr)·`.nojekyll` 유지 확인.
- 데이터: `src/data/videos.tsv`(유튜브 영상), `src/data/prices.csv`(소매 기준가 = 사장님 단가 × 1.3, 100원 올림). qty는 정렬 순서일 뿐 실제 판매량이 아닙니다.
- 입고가·마진·도매가·실제 판매량은 절대 올리지 마세요.
- 커밋 전 `git pull --rebase`.
- 루트의 googlebdb67d0a828cfb44.html(구글), naverba93ea476932b627cd632929e26465dd.html(네이버) 소유확인 파일은 지우지 마세요.
- 기준가 갱신 시: 먼저 현재 `src/data/prices.csv`를 `src/data/prices_prev.csv`로 복사하고 `price_meta.json`의 prev←updated, updated←오늘로 바꾼 뒤 새 가격을 넣으세요. ▲▼는 실제 가격 차이로만 표시합니다(가짜 변동·가짜 재고 표시 금지).
- 유튜브 전체 영상 목록 갱신: `src/data/yt_all.tsv`(id, L/S/V, 조회수, 게시시각, 제목) → `cd src && python3 merge_videos.py data/yt_all.tsv`.
- 자재 가격 가이드(/gagyeok/): 글에 가격·"1평에 얼마" 이야기가 나오면 해당 페이지로 내부 링크를 넣으세요 — hapan-gagyeok, osb-gagyeok, mdf-gagyeok, seokgo-gagyeok, danyeol-gagyeok, jipseong-gagyeok, deck-gagyeok, gakjae-gagyeok, hinoki-ruba, spruce-ruba, tempa-board, tempa-ruba, interior-film, oilstain (.html). 새 품목은 판매 단위가 확인된 것만 src/gagyeok.py 에 추가.
