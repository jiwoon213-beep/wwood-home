# wwood-home 저장소 규칙

- www.wwood.co.kr 홍보 사이트(GitHub Pages, main 브랜치 루트). 도매회원 쇼핑몰은 wwood.kr(이지스호스팅) 그대로.
- 사이트 파일은 `src/build.py`로 생성합니다: `cd src && python3 build.py https://www.wwood.co.kr && cp -r out/. ..` 후 `CNAME`(www.wwood.co.kr)·`.nojekyll` 유지 확인.
- 데이터: `src/data/videos.tsv`(유튜브 영상), `src/data/prices.csv`(소매 기준가 = 사장님 단가 × 1.3, 100원 올림). qty는 정렬 순서일 뿐 실제 판매량이 아닙니다.
- 입고가·마진·도매가·실제 판매량은 절대 올리지 마세요.
- 커밋 전 `git pull --rebase`.
- 루트의 googlebdb67d0a828cfb44.html(구글), naverba93ea476932b627cd632929e26465d.html(네이버) 소유확인 파일은 지우지 마세요.
