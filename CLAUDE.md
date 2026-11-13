# wwood-home 저장소 규칙

- www.wwood.co.kr 홍보 사이트(GitHub Pages, main 브랜치 루트). 도매회원 쇼핑몰은 wwood.kr(이지스호스팅) 그대로.
- 사이트 파일은 `src/build.py`로 생성합니다: `cd src && python3 build.py https://www.wwood.co.kr && cp -r out/. ..` 후 `CNAME`(www.wwood.co.kr)·`.nojekyll` 유지 확인.
- 데이터: `src/data/videos.tsv`(유튜브 영상), `src/data/prices.csv`(소매 기준가 = 사장님 단가 × 1.3, 100원 올림). qty는 정렬 순서일 뿐 실제 판매량이 아닙니다.
- 입고가·마진·도매가·실제 판매량은 절대 올리지 마세요.
- 커밋 전 `git pull --rebase`.
- 루트의 googlebdb67d0a828cfb44.html(구글), naverba93ea476932b627cd632929e26465dd.html(네이버) 소유확인 파일은 지우지 마세요.
- 기준가 갱신 시: 먼저 현재 `src/data/prices.csv`를 `src/data/prices_prev.csv`로 복사하고 `price_meta.json`의 prev←updated, updated←오늘로 바꾼 뒤 새 가격을 넣으세요. ▲▼는 실제 가격 차이로만 표시합니다(가짜 변동·가짜 재고 표시 금지).
- 유튜브 전체 영상 목록 갱신: `src/data/yt_all.tsv`(id, L/S/V, 조회수, 게시시각, 제목) → `cd src && python3 merge_videos.py data/yt_all.tsv`.
- 자재 가격 가이드(/gagyeok/): 글에 가격·"1평에 얼마" 이야기가 나오면 해당 페이지로 내부 링크를 넣으세요 — hapan-gagyeok, osb-gagyeok, mdf-gagyeok, seokgo-gagyeok, danyeol-gagyeok, jipseong-gagyeok, deck-gagyeok, gakjae-gagyeok, hinoki-ruba, spruce-ruba, tempa-board, tempa-ruba, interior-film, oilstain, molding-gagyeok, siding-gagyeok, door-gagyeok (.html). 새 품목은 판매 단위가 확인된 것만 src/gagyeok.py 에 추가.
- 목재 철물(/cheolmul/): janseon(장선걸이), gidungbatchim(기둥받침·캡), jeongja(정자·파고라 지붕 철물), deck-fence, mokjo(목조주택 철물: 홀다운·허리케인 타이), juchudol(주춧돌·농막 기초), bolt(앙카볼트·구조 피스), diy(우마·벤치 프레임). 검색어 글 주제로 "장선걸이 규격", "데크 기둥받침", "농막 주춧돌", "정자 지붕 철물", "허리케인 타이" 등을 쓰고 해당 페이지로 링크하세요. 철물 가격은 prices.csv에 있는 것만, 없으면 '매장 문의'.
- wwood.kr 게시판(admin/board/board2.php) 글: 공개 주소는 https://wwood.kr/home/mall/board2.php?pmode=view&idx=번호. 관리자가 쓴 600바이트 이상 글만 검색 허용(board2.php가 자동 판단). 새 글을 올리면 그 idx를 src/data/wwoodkr_posts.txt 맨 아래에 한 줄 추가(사이트맵 반영). **본문·제목에 이모지(👉📍▶️ 등 4바이트 문자) 금지 — DB가 그 자리에서 글을 잘라 버림.** ▶·※ 같은 일반 기호는 됨.
- wwood.kr 메뉴 "소식·자재정보"(PC 상단 3번째·모바일 메뉴) → /home/mall/info.php(모바일 /home/mobile/info.php). 내용은 서버 /www/home/include/ww_info.php(목재 철물 8칸 + 게시판 글 목록 + 가격 가이드 칩). 새 게시글을 올리면 ww_info.php 글 목록 맨 위에도 한 줄 추가. 철물(code1 32)·데크철물(code2 266) 목록 상단 배너는 include/ww_chban.php(header.php·m_header.php 끝에서 include). 원본 백업: 내 PC Downloads\wwood_c71\header.php·m_header.php.
- 타카·타카핀·콤프레셔(/taka/): 제일타카(JITOOL, jitool.com — 회사 허락) 제품. 데이터 src/taka_data.py, 생성 src/taka.py. 사진은 jitool.com/upload/prod/thumb_l/ 링크(referrerpolicy no-referrer). 제조사 규격표(갑당 수량)와 매장 기준가(prices.csv '타카' 행)는 섞지 말고 따로 표시.
- 예림 중문·도어·문틀(/yerim/): 예림(yerim.net — 회사 허락) 제품 416종. 데이터 src/data/yerim.tsv(depth2|depth3|uid|이름|~이미지), 생성 src/yerim.py(PAGES 13개). 사진은 yerim.net/upload/product/2039376550_ 링크. 가격은 넣지 않음(매장 문의).
