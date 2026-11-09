# 월드건축자재 홍보 사이트 생성기

- `python3 build.py <BASE_URL> [PREFIX] [OUT]` → 정적 사이트 생성
  - 정식: `python3 build.py https://www.wwoodkr.com` (out/ 에 생성, robots·sitemap 포함)
  - 미리보기: `python3 build.py https://jiwoon213-beep.github.io/lumber-price/wwood /lumber-price/wwood ../wwood` (noindex)
- `data/videos.tsv`: 유튜브 영상(ID, L/S, 조회수, 분류, 자재태그, 제목)
- `data/prices.csv`: 소매 기준가(사장님 단가 × 1.3, 100원 올림). qty는 정렬 순서만 (실제 판매량 아님)
- `mats.py`: 자재 백과 내용·분류
- 입고가·마진·도매가는 절대 넣지 않습니다.
