# -*- coding: utf-8 -*-
# 프랜차이즈·체인점 매장 인테리어 업체용 자재 납품 안내 — /franchise/
# 사장님 지시(2026-11-28): 전국 체인점 인테리어 공사 업체에게 노출·클릭되게.
# 지킬 것: 특정 프랜차이즈 브랜드 이름 쓰지 않음(관계 있는 듯 보이면 안 됨), 거래처라고 꾸미지 않음,
# 확인 안 된 시공비·운임·납기·할인 숫자 금지, 가격은 prices.csv 기준가(부가세 별도)만.
import re
from urllib.parse import quote

# (slug, 업종, 검색 별칭, 주로 하는 공사, [자재 slug], [주의·팁], [(내부 링크, 이름)])
BIZ = [
 ("cafe", "카페", "커피숍·디저트 카페", "카운터·바 테이블 목공, 벽 우드 마감, 천장 루바·노출 천장, 좌석 칸막이",
  ["hapan", "jipseong", "gypsum", "molding", "film", "hinoki"],
  ["카운터·바 상판은 물과 열이 닿으니 집성판·상판 마감을 꼼꼼히 합니다.", "벽 우드 마감은 템바보드·루바·합판 도장 중 매장 콘셉트에 맞춰 고릅니다."],
  [("/qna/cafe-self-interior.html", "카페 셀프 인테리어"), ("/qna/bar-table.html", "바 테이블 만들기"), ("/gonggan/cafe-dark-window-bar.html", "카페 공간 사진")]),
 ("bakery", "베이커리·제과점", "빵집", "진열대·쇼케이스 받침 목공, 주방 벽 방수 마감, 매장 벽·천장",
  ["jipseong", "mdf", "film", "gypsum", "tile"],
  ["주방 쪽 벽은 방수 석고보드나 타일로 마감합니다.", "진열대 판재는 하중을 생각해 두께를 넉넉히 정합니다."],
  [("/qna/hapan-seonban-duggae.html", "선반 판 두께"), ("/qna/bangsu-seokgo.html", "방수 석고보드")]),
 ("chicken", "치킨·호프", "치킨집·호프집", "홀 테이블·벽 마감, 주방 벽, 좌석 칸막이, 간판 하지",
  ["hapan", "gypsum", "molding", "film", "tile"],
  ["기름과 열이 많은 주방 벽은 불연·방수 자재를 씁니다.", "홀 벽은 청소하기 쉬운 필름·도장 마감이 관리가 편합니다."],
  [("/qna/banghwa-seokgo.html", "방화 석고보드"), ("/qna/jubang-tile-gireumttae.html", "주방 타일 기름때")]),
 ("restaurant", "한식·일반 음식점", "식당", "좌식·입식 홀, 칸막이, 주방 벽, 천장",
  ["hapan", "gujo", "gypsum", "molding", "film", "maru"],
  ["좌식 단(평상형 좌석)은 각재로 틀을 짜고 합판·마루로 덮습니다.", "칸막이는 간살·반벽으로 하면 답답하지 않습니다."],
  [("/qna/gansal-partition.html", "간살 파티션"), ("/qna/jwasik-pyeongsang.html", "좌식 평상")]),
 ("bbq", "고깃집", "구이 전문점", "테이블·후드 주변 마감, 벽·천장, 칸막이",
  ["gypsum", "hapan", "film", "tile", "molding"],
  ["불과 연기가 닿는 곳은 방화 석고보드 등 불에 강한 자재를 씁니다.", "벽 마감은 기름때를 닦기 쉬운 재질로 고릅니다."],
  [("/qna/banghwa-seokgo.html", "방화 석고보드"), ("/qna/junbulyeon-tteut.html", "준불연 뜻")]),
 ("snack", "분식·김밥", "분식집", "작은 홀 테이블·벽 선반, 주방 벽, 카운터",
  ["mdf", "film", "gypsum", "tile"],
  ["좁은 매장은 벽 선반·상부장으로 수납을 늘립니다.", "카운터 앞판은 필름으로 마감하면 관리가 쉽습니다."],
  [("/qna/mujiju-byeokseonban.html", "무지주 벽선반"), ("/qna/mdf-film.html", "MDF 필름")]),
 ("pizza", "피자·배달 전문점", "배달 매장", "주방 위주 소형 매장, 픽업 카운터, 대기 공간",
  ["mdf", "film", "gypsum", "hardware"],
  ["픽업 카운터와 대기석을 작게 짜고 주방 동선을 넓게 잡습니다.", "주방 쪽 벽·천장은 방수·불연 자재를 씁니다."],
  [("/qna/bangsu-seokgo.html", "방수 석고보드"), ("/qna/counter-jejak.html", "카운터 제작")]),
 ("pub", "주점·이자카야", "술집", "어두운 톤 벽·천장, 룸 칸막이, 바 테이블",
  ["hapan", "gypsum", "film", "molding", "sound"],
  ["룸 칸막이는 흡음재를 넣으면 옆 자리 소리가 줄어듭니다.", "어두운 톤 벽은 합판 도장·필름으로 연출합니다."],
  [("/gonggan/cafe-black-grain-wall.html", "검은 나뭇결 벽 사진"), ("/qna/bangeum-gabyeok.html", "방음 가벽")]),
 ("convenience", "편의점", "무인 편의점", "매장 벽·창고 칸막이, 계산대, 진열 뒤 벽",
  ["gypsum", "gujo", "hapan", "hardware"],
  ["창고 칸막이는 각재(또는 경량 스터드)+석고보드로 빠르게 세웁니다.", "진열대가 붙는 벽은 바탕에 합판을 덧대 고정력을 높입니다."],
  [("/qna/seokgo-myeotjang.html", "석고보드 몇 장"), ("/qna/sigma-stud.html", "경량 스터드")]),
 ("unmanned", "무인 매장", "무인 아이스크림·무인 카페·무인 문구", "벽 진열 선반, 결제 키오스크 자리, 조명 천장",
  ["mdf", "film", "jipseong", "hardware"],
  ["벽 진열 선반은 숨은 브라켓으로 깔끔하게 답니다.", "키오스크·CCTV 배선 자리를 목공 단계에서 미리 냅니다."],
  [("/qna/seonban-bracket.html", "선반 브라켓"), ("/qna/mutagong-seonban.html", "무타공 선반")]),
 ("salon", "미용실", "헤어숍", "거울 벽·경대, 샴푸실 칸막이, 대기석, 수납장",
  ["mdf", "film", "gypsum", "tile", "molding"],
  ["샴푸실 쪽은 물이 튀니 방수 석고보드·타일로 마감합니다.", "경대·수납장은 MDF+필름이 색 맞추기 쉽습니다."],
  [("/qna/bangsu-seokgo.html", "방수 석고보드"), ("/qna/geoul-dalgi.html", "거울 달기")]),
 ("nail", "네일·뷰티샵", "네일샵·속눈썹샵·피부관리실", "시술 테이블, 벽 수납, 관리실 칸막이",
  ["mdf", "film", "gypsum", "sound"],
  ["관리실 칸막이는 천장까지 막고 문을 달면 소리가 덜 샙니다.", "밝은 색 필름·도장으로 깔끔하게 마감합니다."],
  [("/qna/mutagong-gabyeok.html", "무타공 가벽"), ("/qna/film-sunseo.html", "필름 시공 순서")]),
 ("academy", "학원·교습소", "입시·영어·수학 학원", "강의실 칸막이, 방음 벽, 상담실, 사물함",
  ["gypsum", "gujo", "sound", "insul", "door"],
  ["강의실 사이 벽은 차음 석고보드·흡음재를 겹쳐 소리를 줄입니다.", "강의실 문은 방음 문이나 틈막이를 함께 생각합니다."],
  [("/qna/bangeum-gabyeok.html", "방음 가벽"), ("/qna/chaeum-seokgo.html", "차음 석고보드"), ("/qna/bangeum-mun.html", "방음 문")]),
 ("studycafe", "스터디카페·독서실", "독서실", "1인 좌석 칸막이, 룸, 흡음 천장, 사물함",
  ["mdf", "sound", "gypsum", "jipseong"],
  ["좌석 칸막이는 MDF·집성판으로 같은 크기를 반복 재단하면 빠릅니다.", "천장·벽 흡음재로 울림을 줄입니다."],
  [("/qna/studycafe-interior.html", "스터디카페 인테리어"), ("/bigyo/heupeum-board.html", "흡음보드 비교")]),
 ("music", "음악·피아노 학원", "실용음악 학원·연습실", "방음 연습실, 이중 벽, 방음 문",
  ["sound", "gypsum", "insul", "door"],
  ["연습실은 벽을 이중으로 세우고 사이에 흡음재를 채웁니다.", "흡음(울림 줄이기)과 차음(소리 막기)을 나눠 생각합니다."],
  [("/qna/akgi-bangeum.html", "악기 방음"), ("/qna/heubeumje-heubeumjae.html", "흡음재 뜻")]),
 ("gym", "헬스장·필라테스", "PT샵·요가원", "거울 벽, 바닥, 탈의실 칸막이, 샤워실",
  ["gypsum", "tile", "maru", "mdf"],
  ["거울 벽 바탕은 합판을 덧대 거울 고정을 단단히 합니다.", "탈의실·샤워실 쪽은 방수 자재를 씁니다."],
  [("/qna/geoul-dalgi.html", "거울 달기"), ("/qna/bangsu-seokgo.html", "방수 석고보드")]),
 ("pcroom", "PC방·보드게임카페", "게임카페", "좌석 칸막이, 흡음 천장, 배선 정리 하부장",
  ["mdf", "sound", "film", "gypsum"],
  ["좌석 칸막이와 하부장은 같은 규격으로 반복 재단합니다.", "배선이 지나갈 구멍·통로를 목공 때 미리 냅니다."],
  [("/qna/consent-gumeong-ttagi.html", "콘센트 구멍 따기"), ("/qna/mdf-pis.html", "MDF 피스")]),
 ("kidscafe", "키즈카페", "실내 놀이터", "놀이 구조물 하지, 벽 보호, 바닥, 파티션",
  ["jipseong", "hapan", "maru", "sound"],
  ["아이 손이 닿는 모서리는 둥글게 다듬고 가시 없게 샌딩합니다.", "놀이 구조물은 전문 업체 기준과 안전 인증을 따릅니다."],
  [("/qna/namu-jangnangam-mandeulgi.html", "나무 장난감 안전"), ("/qna/aibang-gagu.html", "아이방 가구")]),
 ("clinic", "병원·의원", "치과·한의원·피부과", "진료실·상담실 칸막이, 대기실 벽, 천장",
  ["gypsum", "gujo", "door", "film", "sound"],
  ["상담실은 차음 벽과 문으로 대화가 새지 않게 합니다.", "다중이용시설은 방염·불연 기준이 적용될 수 있어 자재를 먼저 확인합니다."],
  [("/qna/chaeum-seokgo.html", "차음 석고보드"), ("/qna/bangyeom-hapan.html", "방염합판")]),
 ("pharmacy", "약국", "약국 리모델링", "진열장, 조제실 칸막이, 카운터",
  ["mdf", "film", "jipseong", "gypsum"],
  ["벽 진열장은 MDF 몸통+필름 마감으로 색을 맞춥니다.", "조제실 칸막이는 유리 상부+목공 하부로 많이 짭니다."],
  [("/qna/system-seonban.html", "시스템 선반"), ("/qna/counter-jejak.html", "카운터 제작")]),
 ("optical", "안경원", "안경점", "벽 진열장, 검안실, 카운터",
  ["mdf", "film", "molding", "jipseong"],
  ["벽 진열장 안쪽에 조명 자리를 목공 단계에서 미리 냅니다.", "검안실은 칸막이로 나누고 문을 답니다."],
  [("/qna/ganjeop-molding-self.html", "간접조명 몰딩"), ("/qna/tv-seon-sumgigi.html", "배선 숨기기")]),
 ("phone", "휴대폰 매장", "통신사 대리점", "진열 테이블, 벽 그래픽 바탕, 상담석",
  ["mdf", "film", "gypsum"],
  ["벽 그래픽을 붙일 면은 석고·MDF를 평평하게 잡고 퍼티합니다.", "진열 테이블은 같은 크기로 반복 재단합니다."],
  [("/qna/seokgo-putty.html", "석고 퍼티"), ("/qna/mdf-film.html", "MDF 필름")]),
 ("laundry", "세탁소·코인빨래방", "무인 세탁방", "기계 받침대, 대기석, 벽 마감",
  ["tile", "gypsum", "jipseong"],
  ["물과 습기가 많아 벽·바닥은 방수 자재로 마감합니다.", "기계 받침대는 무게를 견디게 단단히 짭니다."],
  [("/qna/setakgi-batchimdae.html", "세탁기 받침대"), ("/qna/bangsu-seokgo.html", "방수 석고보드")]),
 ("petshop", "반려동물 매장·동물병원", "펫샵·애견미용", "미용실 칸막이, 진열장, 바닥, 벽 보호",
  ["tile", "film", "gypsum", "mdf"],
  ["바닥·벽 하단은 물청소에 강한 자재로 마감합니다.", "긁힘이 잦은 벽 아래는 보호판을 덧댑니다."],
  [("/qna/bangsu-seokgo.html", "방수 석고보드"), ("/qna/tile-sigong-juui.html", "타일 시공 주의")]),
 ("office", "사무실·공유오피스", "사무실 인테리어", "회의실 칸막이, 탕비실, 천장, 바닥",
  ["gypsum", "gujo", "sound", "door", "maru"],
  ["회의실은 차음 벽·흡음 천장으로 소리를 줄입니다.", "임대 사무실은 원상복구를 생각해 철거 쉬운 방식을 고릅니다."],
  [("/qna/samusil-self-interior.html", "사무실 셀프 인테리어"), ("/qna/samusil-kanmagi.html", "사무실 칸막이")]),
 ("showroom", "쇼룸·의류 매장", "옷가게·편집숍", "행거·진열대, 탈의실, 벽 선반, 바닥",
  ["jipseong", "mdf", "film", "hardware", "maru"],
  ["행거·벽 선반은 숨은 브라켓과 각재 바탕으로 단단히 답니다.", "탈의실은 칸막이+커튼 또는 문으로 짭니다."],
  [("/qna/system-hanger.html", "시스템 행거"), ("/qna/wonmok-hanger-seonban.html", "원목 행거 선반")]),
 ("pension", "펜션·숙박", "게스트하우스·모텔 리모델링", "객실 벽·천장 루바, 욕실, 데크, 방음",
  ["hinoki", "gypsum", "bangbu", "hapdeck", "sound"],
  ["객실 천장·벽 루바는 편백·스프러스로 분위기를 냅니다.", "바깥 데크는 방부목·합성목 중 관리 방법을 보고 고릅니다."],
  [("/qna/pension-self-interior.html", "펜션 셀프 인테리어"), ("/gagyeok/deck-gagyeok.html", "데크 가격")]),
 ("burger", "버거·샌드위치", "수제버거·샌드위치 전문점", "오픈 주방 카운터, 홀 테이블, 벽 포인트 마감",
  ["mdf", "film", "tile", "gypsum"],
  ["오픈 주방 앞 카운터는 물·기름에 강한 상판으로 마감합니다.", "벽 포인트는 타일·필름으로 브랜드 색을 맞춥니다."],
  [("/qna/counter-jejak.html", "카운터 제작"), ("/qna/artwall-tile.html", "아트월 타일")]),
 ("salad", "샐러드·도시락", "샐러드 전문점·도시락 매장", "작은 홀, 진열 냉장고 주변 마감, 포장 카운터",
  ["mdf", "film", "jipseong", "gypsum"],
  ["진열 냉장고 주변은 열기가 빠질 틈을 두고 마감합니다.", "포장 카운터는 집성판 상판으로 깔끔하게 짭니다."],
  [("/qna/naengjangjang-size.html", "냉장고장 사이즈"), ("/qna/jipseong-sangpan-magam.html", "상판 마감")]),
 ("noodle", "국수·라멘·마라탕", "면 요리 전문점", "바 좌석, 주방 벽 방수, 셀프 코너 선반",
  ["jipseong", "tile", "gypsum", "film"],
  ["바 좌석 상판은 뜨거운 그릇을 생각해 마감재를 고릅니다.", "셀프 코너 선반은 물청소가 쉬운 재질로 만듭니다."],
  [("/qna/bar-table.html", "바 테이블"), ("/qna/bangsu-seokgo.html", "방수 석고보드")]),
 ("icecream", "아이스크림·디저트", "아이스크림 할인점·디저트 매장", "냉동고 진열 벽, 밝은 벽·천장, 계산대",
  ["mdf", "film", "gypsum", "hardware"],
  ["냉동고가 많은 매장은 벽 콘센트 위치를 목공 단계에서 맞춥니다.", "밝은 색 필름·도장으로 깨끗한 느낌을 냅니다."],
  [("/qna/consent-gumeong-ttagi.html", "콘센트 구멍 따기"), ("/qna/film-sunseo.html", "필름 시공 순서")]),
 ("flower", "꽃집·플라워카페", "꽃집", "작업대, 물 쓰는 구역, 진열 선반, 원목 느낌 벽",
  ["jipseong", "bangbu", "tile", "stain"],
  ["물을 많이 쓰는 작업대는 상판 마감을 꼼꼼히 하고 바닥은 물에 강하게 합니다.", "원목 선반은 오일 마감으로 물 얼룩을 줄입니다."],
  [("/qna/wonmok-seonban-jejak.html", "원목 선반 제작"), ("/qna/jakeopdae-nopi.html", "작업대 높이")]),
 ("butcher", "정육점·반찬가게", "축산물 판매점·반찬 전문점", "진열 쇼케이스 주변, 작업실 칸막이, 위생 벽 마감",
  ["tile", "gypsum", "mdf"],
  ["작업실 벽·바닥은 물청소에 강한 타일·방수 자재로 마감합니다.", "위생 관련 시설 기준은 관할 기관 안내를 따릅니다."],
  [("/qna/bangsu-seokgo.html", "방수 석고보드"), ("/qna/tile-sigong-juui.html", "타일 시공 주의")]),
 ("stationery", "문구·생활용품점", "문구점·잡화점", "벽 진열 선반, 곤도라 뒤 벽, 계산대",
  ["mdf", "gypsum", "hardware", "film"],
  ["선반 레일을 달 벽은 바탕에 합판을 덧대 하중을 받게 합니다.", "같은 크기 선반판은 한 번에 반복 재단합니다."],
  [("/qna/system-seonban.html", "시스템 선반"), ("/qna/seonban-bracket.html", "선반 브라켓")]),
 ("bookcafe", "북카페·만화카페", "만화카페·도서 공간", "벽 책장, 다락형 좌석, 칸막이, 흡음",
  ["jipseong", "hapan", "sound", "gujo"],
  ["벽 책장은 처지지 않게 선반 두께와 받침 간격을 정합니다.", "다락형 좌석은 구조재로 튼튼하게 짜고 난간을 둡니다."],
  [("/qna/chaekjang-size.html", "책장 사이즈"), ("/qna/nangan-nopi.html", "난간 높이")]),
 ("photo", "셀프사진관·스튜디오", "포토부스·사진관", "부스 칸막이, 배경 벽, 조명 천장",
  ["mdf", "gypsum", "film", "sound"],
  ["부스 칸막이는 같은 규격으로 반복 제작해 빠르게 세웁니다.", "배경 벽은 평평하게 퍼티·도장하거나 필름으로 마감합니다."],
  [("/qna/seokgo-putty.html", "석고 퍼티"), ("/qna/mutagong-gabyeok.html", "무타공 가벽")]),
 ("dental", "치과·한의원", "치과의원·한의원", "진료 체어 구역, 소독실, 대기실 벽·천장, 상담실",
  ["gypsum", "gujo", "door", "film", "sound"],
  ["상담실·원장실은 차음 벽과 문으로 대화가 새지 않게 합니다.", "의료기관 시설 기준은 관할 기관 안내를 먼저 확인합니다."],
  [("/qna/chaeum-seokgo.html", "차음 석고보드"), ("/qna/bangeum-mun.html", "방음 문")]),
 ("realestate", "공인중개사·보험 사무소", "부동산·상담 사무소", "상담 테이블, 벽 게시판·선반, 칸막이",
  ["mdf", "gypsum", "film", "jipseong"],
  ["상담석 칸막이는 반벽·간살로 하면 답답하지 않습니다.", "유리면 시트지·간판 바탕을 함께 정리합니다."],
  [("/qna/gansal-partition.html", "간살 파티션"), ("/qna/yurichang-sheetji.html", "유리창 시트지")]),
 ("carwash", "세차장·카센터 대기실", "자동차 관련 매장", "고객 대기실, 사무실 칸막이, 창고 선반",
  ["gypsum", "gujo", "hardware", "tile"],
  ["작업장 쪽 벽은 충격·습기에 강한 자재를 씁니다.", "창고 선반은 각재·합판으로 튼튼하게 짭니다."],
  [("/qna/changgo-seonban.html", "창고 선반"), ("/qna/samusil-kanmagi.html", "사무실 칸막이")]),
 ("brunch", "브런치카페", "브런치 레스토랑", "큰 창가 좌석, 오픈 주방 카운터, 원목 테이블, 밝은 벽",
  ["jipseong", "film", "gypsum", "tile"],
  ["원목 테이블 상판은 오일·우레탄 중 관리 방식을 정해 마감합니다.", "오픈 주방 앞 벽은 물·기름에 강한 타일로 마감합니다."],
  [("/qna/wonmok-sangpan-coating.html", "원목 상판 코팅"), ("/qna/bar-table.html", "바 테이블")]),
 ("winebar", "와인바·칵테일바", "바·라운지", "어두운 톤 벽, 바 카운터, 진열 선반, 간접조명",
  ["jipseong", "hapan", "molding", "film"],
  ["바 카운터 상판은 두꺼운 집성판으로 무게감을 냅니다.", "진열 선반 뒤에 간접조명 자리를 목공 단계에서 냅니다."],
  [("/qna/ganjeop-molding-self.html", "간접조명 몰딩"), ("/qna/bar-table.html", "바 테이블")]),
 ("karaoke", "노래방·코인노래방", "노래연습장", "방음 룸, 복도, 룸 문, 흡음 벽",
  ["sound", "gypsum", "insul", "door"],
  ["룸 벽은 이중 벽과 흡음재로 옆 방 소리를 줄입니다.", "다중이용업소는 방염·피난 관련 기준이 있으니 관할 기관에 먼저 확인합니다."],
  [("/qna/bangeum-gabyeok.html", "방음 가벽"), ("/qna/maejang-bangyeom.html", "매장 방염")]),
 ("screengolf", "스크린골프·골프연습장", "실내 골프장", "타석 룸 칸막이, 바닥 단, 천장 흡음, 대기 공간",
  ["gypsum", "gujo", "sound", "hapan"],
  ["타석 바닥 단은 구조재로 튼튼하게 짜고 합판으로 덮습니다.", "공 맞는 벽·천장은 충격과 소리를 생각해 마감합니다."],
  [("/qna/bangeum-gabyeok.html", "방음 가벽"), ("/qna/osb-12t-15t.html", "판 두께 고르기")]),
 ("billiard", "당구장·볼링·탁구장", "실내 스포츠 시설", "넓은 홀 천장·조명, 벽 마감, 대기석",
  ["gypsum", "maru", "film"],
  ["넓은 홀 천장은 조명 위치를 먼저 정하고 천장틀을 짭니다.", "바닥은 시설 종류에 맞는 바닥재를 고릅니다."],
  [("/qna/seokgo-cheonjang-jomyeong.html", "석고 천장 조명"), ("/qna/badakjae-goreugi.html", "바닥재 고르기")]),
 ("taekwondo", "태권도·주짓수·체육관", "도장·체육관", "넓은 운동 공간 바닥, 거울 벽, 탈의실, 사무실",
  ["gypsum", "maru", "gujo", "sound"],
  ["운동 공간 바닥은 충격을 흡수하는 매트·바닥재를 씁니다.", "아래층 소음이 걱정되면 바닥 방음을 같이 생각합니다."],
  [("/qna/cheunggan-mat-sigong.html", "층간소음 매트"), ("/qna/geoul-dalgi.html", "거울 달기")]),
 ("gongbubang", "공부방·교습소", "소규모 공부방", "작은 강의실 칸막이, 책장, 방음",
  ["gypsum", "jipseong", "sound"],
  ["작은 공간은 벽 책장으로 수납을 늘립니다.", "옆 교실 소리는 차음 석고보드와 흡음재로 줄입니다."],
  [("/qna/chaekjang-size.html", "책장 사이즈"), ("/qna/chaeum-seokgo.html", "차음 석고보드")]),
 ("daycare", "어린이집·유치원", "보육시설 리모델링", "교실 벽·바닥, 수납장, 화장실, 안전 마감",
  ["jipseong", "maru", "film", "gypsum"],
  ["아이 손이 닿는 모서리는 둥글게, 가시 없게 마감합니다.", "보육시설 기준은 관할 기관 안내를 먼저 확인합니다."],
  [("/qna/aibang-gagu.html", "아이방 가구"), ("/qna/wonmok-gyogu-sedok.html", "원목 교구 관리")]),
 ("carehome", "요양원·주간보호센터", "노인 돌봄 시설", "복도 손잡이 바탕, 문턱 없애기, 미끄럼 방지 바닥",
  ["gypsum", "door", "maru", "hardware"],
  ["복도 손잡이를 달 벽은 바탕에 합판을 덧대 단단히 고정합니다.", "문턱을 낮추거나 없애 휠체어가 다니기 쉽게 합니다."],
  [("/qna/munteok-jegeo.html", "문턱 제거"), ("/qna/munteok-gyeongsaro.html", "문턱 경사로")]),
 ("vethospital", "동물병원", "반려동물 병원", "진료실 칸막이, 입원장 주변 마감, 대기실",
  ["gypsum", "tile", "film", "sound"],
  ["진료·입원 공간 벽은 물청소에 강한 마감을 씁니다.", "동물 소리가 새지 않게 칸막이에 흡음재를 넣습니다."],
  [("/qna/bangsu-seokgo.html", "방수 석고보드"), ("/qna/bangeum-gabyeok.html", "방음 가벽")]),
 ("chinese", "중식·일식·아시안 식당", "중국집·일식당·쌀국수", "홀 칸막이, 좌식 단, 주방 벽, 천장 루바",
  ["gujo", "hapan", "hinoki", "gypsum", "tile"],
  ["좌식 단은 각재 틀에 합판·마루를 덮고 모서리를 몰딩으로 마감합니다.", "일식 콘셉트 천장·벽은 루바로 분위기를 냅니다."],
  [("/qna/jwasik-pyeongsang.html", "좌식 평상"), ("/qna/ruba-sigong.html", "루바 시공")]),
 ("coffeetakeout", "테이크아웃 커피 전문점", "소형 커피 매장", "작은 카운터, 대기 공간, 벽 메뉴판 바탕",
  ["mdf", "film", "jipseong", "gypsum"],
  ["좁은 매장은 카운터와 상부장을 한 번에 짜서 공간을 아낍니다.", "메뉴판·간판 바탕은 각재·합판으로 단단히 잡습니다."],
  [("/qna/counter-jejak.html", "카운터 제작"), ("/qna/mujiju-byeokseonban.html", "무지주 벽선반")]),
 ("church", "교회·공방·소규모 공간", "작업실·공방", "강단·단상, 벽 흡음, 작업대",
  ["jipseong", "hapan", "sound", "gujo"],
  ["단상은 각재로 틀을 짜고 합판·마루로 덮습니다.", "울림이 큰 공간은 흡음재로 소리를 정리합니다."],
  [("/gonggan/cafe-wood-stage.html", "단상 공간 사진"), ("/mandeul/jakeopdae.html", "작업대 만들기")]),
 ("teahouse", "전통찻집·한방카페", "찻집·티카페·한옥 콘셉트 카페", "좌식 마루·평상, 루바·한지 느낌 벽, 격자 칸막이, 천장 루바",
  ["gujo", "hapan", "hinoki", "maru", "molding", "stain"],
  ["좌식 마루는 각재로 틀을 짜고 합판 위에 마루를 덮어 걸터앉기 좋은 높이로 맞춥니다.", "루바·원목 마감은 차와 물이 튀는 곳이라 오일·스테인으로 표면을 보호합니다."],
  [("/qna/jwasik-pyeongsang.html", "좌식 평상"), ("/qna/gansal-partition.html", "간살 파티션"), ("/qna/ruba-oil.html", "루바 오일 마감")]),
 ("arcade", "오락실·인형뽑기방", "코인오락실·게임장·뽑기방", "기계 배치 벽·바닥 마감, 배선 정리 몰딩, 천장 조명, 카운터",
  ["gypsum", "sound", "film", "molding", "maru"],
  ["기계 무게와 전기 용량·콘센트 위치는 전기 업체와 먼저 정하고 목공을 합니다.", "기계 소리가 울리는 홀은 벽·천장에 흡음재를 넣어 소음을 줄입니다."],
  [("/qna/tv-seon-sumgigi.html", "배선 숨기기"), ("/qna/seokgo-cheonjang-jomyeong.html", "석고 천장 조명"), ("/qna/heubeumjae-jongryu.html", "흡음재 종류")]),
]

PX = [("석고보드 일반 9.5T 3×6", r"석고-일반 3\*6 @ 9\.5T$"), ("방수 석고보드 9.5T 3×6", r"석고-방수 3\*6 @ 9\.5T"), ("방화 석고보드 12.5T 3×6", r"석고-방화 3\*6 @12\.5T"),
      ("MDF 9mm 4×8", r"MDF 4\*8 @ 9mm$"), ("MDF 18mm 4×8", r"MDF 4\*8 @18mm"), ("합판 12mm 내수 4×8", r"4\*8 @12mm\(내수/A급\)"),
      ("구조재 2×4 12자", r"Ⅱ 2\* 4\*12ft"), ("흡음보드 오크 라인 9T 1200×2400", r"흡음 오크 라인@9T\*1200\*2400")]

INFO = [("/qna/daejeon-sangga-interior-jajae.html", "대전 상가 인테리어 자재"), ("/qna/sejong-sangga-interior-jajae.html", "세종 상가 인테리어 자재"), ("/qna/mokgong-domyeon.html", "목공 도면 그리기"), ("/qna/interior-magam-checklist.html", "마감 점검 체크리스트"), ("/qna/bangyeom-tteut.html", "방염 뜻·대상 확인"), ("/franchise/balju.html", "자재 발주서(무료 양식)"), ("/qna/maejang-banbok-jaedan.html", "여러 매장 같은 규격 재단"), ("/qna/maejang-bangyeom.html", "매장 방염 자재 확인"), ("/qna/sangga-interior-jajae-list.html", "상가 인테리어 자재 목록"), ("/qna/franchise-interior-biyong-gusung.html", "인테리어 견적 항목"), ("/qna/franchise-interior-jugi.html", "프랜차이즈 리뉴얼 주기"), ("/qna/sangga-wonsang-bokgu.html", "상가 원상복구"), ("/qna/maejang-interior-sunseo.html", "매장 인테리어 순서"), ("/qna/maejang-interior-gigan.html", "공사 기간 줄이기"), ("/qna/gage-interior-gyeonjeok-bogi.html", "견적 보는 법"), ("/qna/mokgong-jajae-ssage.html", "목공 자재 아끼기"), ("/qna/interior-jajae-showroom.html", "자재 쇼룸"), ("/qna/interior-gongjeongpyo.html", "인테리어 공정표"), ("/qna/interior-silcheuk-checklist.html", "실측 체크리스트"), ("/qna/interior-gyeonjeokseo-yangsik.html", "견적서 양식"), ("/qna/interior-gyeyakseo-teugyak.html", "계약서 특약"), ("/qna/sangga-gabyeok-jongryu.html", "상가 가벽 종류")]

VRX = {"gypsum": "석고|가벽|천장", "mdf": "MDF|수납|선반", "film": "필름|시트", "jipseong": "집성|상판|테이블|카운터", "hapan": "합판", "molding": "몰딩|걸레받이",
       "tile": "타일", "sound": "방음|흡음", "maru": "마루|데코타일", "hinoki": "루바|편백|히노끼", "gujo": "각재|구조목|다루끼|가벽", "door": "중문|방문|도어|문틀",
       "hardware": "철물|브라켓|앙카", "insul": "단열", "bangbu": "방부|데크", "hapdeck": "합성|데크", "stain": "스테인|오일", "siding": "사이딩"}

JN = {"osb": "OSB", "hapan": "합판", "jipseong": "집성판", "gypsum": "석고보드", "molding": "몰딩", "film": "인테리어 필름", "hinoki": "편백·루바", "mdf": "MDF", "tile": "타일",
      "gujo": "구조재·각재", "maru": "마루", "sound": "흡음·방음재", "hardware": "철물·부속", "insul": "단열재", "door": "도어·문틀", "bangbu": "방부목", "hapdeck": "합성목 데크", "stain": "스테인·오일", "siding": "사이딩"}


def gen(page, E, CTA, faqslide, TEL, EMAIL, ADDR, HOURS, top, vsplit, P):
    import os
    OUTCHK = lambda u: True
    rows = []
    for nm, rx in PX:
        hit = sorted([p for p in P if re.search(rx, p["name"])], key=lambda p: p["price"])
        if hit: rows.append((nm, hit[0]["price"]))
    ptab = ('<table class="rt"><thead><tr><th>자재</th><th>소매 기준가(부가세 별도)</th></tr></thead><tbody>' + "".join(f'<tr><td>{E(n)}</td><td>{p:,}원~</td></tr>' for n, p in rows) + '</tbody></table>') if rows else ""
    try:
        import nation as _N
        REG = _N.REG
    except Exception:
        REG = []
    tel = TEL.replace("-", "")
    common_fq = [
        ("인테리어 업체인데 현장으로 바로 받을 수 있나요?", "네. 품목·규격·수량·재단 크기·현장 주소를 보내 주시면 자재값과 운임을 먼저 알려 드리고, 입금 확인 후 재단·상차해 용달로 현장에 보내 드립니다. 운임은 거리·차량·수량에 따라 달라 견적으로 안내합니다."),
        ("여러 매장에 같은 규격으로 반복 납품할 수 있나요?", "같은 도면·같은 재단표면 매장마다 같은 크기로 재단해 보낼 수 있습니다. 재단표(cut.html에서 만든 그림)를 한 번 보내 두시면 다음 매장부터 품목만 말씀하셔도 됩니다."),
        ("사업자 회원가가 있나요?", "사업자등록증·명함 확인 후 도매회원(wwood.kr)으로 가입하시면 회원가로 주문하실 수 있습니다."),
        ("방염·불연 자재가 필요한데 있나요?", "다중이용업소 등은 방염·불연 기준이 적용될 수 있습니다. 필요한 성능(방염 합판, 방화 석고보드 등)과 성적서가 필요한지 먼저 말씀해 주시면 해당 품목 재고와 서류를 확인해 드립니다."),
        ("매장에서 실물을 볼 수 있나요?", f"대전 유성 매장(3000평)에 합판·MDF·석고보드·몰딩·도어·필름·루바를 쌓아 두고 있습니다. 영업시간: {HOURS}."),
    ]
    QX = {'arcade': 'arcade-interior', 'teahouse': 'chatjip-interior', 'coffeetakeout': 'takeout-coffee-interior', 'chinese': 'junsik-ilsik-interior', 'gongbubang': 'gongbubang-interior', 'carwash': 'carwash-daegisil', 'stationery': 'munggu-interior', 'noodle': 'noodle-interior', 'pizza': 'pizza-baedal-interior', 'pension': 'pension-self-interior', 'salon': 'small-salon-interior', 'cafe': 'cafe-byeok-interior', 'music': 'eumak-hagwon-interior', 'billiard': 'danggujang-interior', 'brunch': 'brunch-cafe-interior', 'icecream': 'dessert-cafe-interior', 'burger': 'burger-interior', 'salad': 'salad-dosirak-interior', 'bookcafe': 'manhwa-cafe-interior', 'studycafe': 'doksil-interior', 'convenience': 'pyeonuijeom-interior', 'screengolf': 'screengolf-interior', 'carehome': 'yoyangwon-interior', 'daycare': 'eorinijip-interior', 'taekwondo': 'taekwondo-interior', 'laundry': 'coin-laundry-interior', 'pcroom': 'pcbang-interior', 'church': 'gyohoe-interior', 'vethospital': 'dongmul-byeongwon-interior', 'winebar': 'winebar-interior', 'realestate': 'budongsan-interior', 'petshop': 'aegyeonshop-interior', 'phone': 'phone-maejang-interior', 'optical': 'angyeongwon-interior', 'clinic': 'byeongwon-interior-jajae', 'photo': 'selfphoto-interior', 'kidscafe': 'kidscafe-interior', 'unmanned': 'musin-maejang-interior', 'academy': 'hagwon-interior-jajae', 'showroom': 'otgage-interior', 'restaurant': 'sikdang-kanmagi', 'bbq': 'gogitjip-interior', 'pub': 'suljip-interior', 'gym': 'pilates-interior-badak', 'karaoke': 'noraebang-interior', 'flower': 'kkotjip-interior', 'snack': 'bunsik-interior', 'butcher': 'jeongyuk-interior', 'dental': 'hanuiwon-interior', 'nail': 'nailshop-interior', 'office': 'shared-office-interior', 'bakery': 'bakery-interior', 'pharmacy': 'yakguk-interior', 'chicken': 'chikin-interior'}
    out = []
    for slug, nm, alias, work, mats, tips, links in BIZ:
        if slug in QX: links = list(links) + [(f'/qna/{QX[slug]}.html', f'{nm} 인테리어 자재·공정')]
        mlinks = "".join(f'<a href="/jajae/{m}.html">{E(JN.get(m, m))}</a>' for m in mats)
        ilinks = "".join(f'<a href="{u}">{E(t)}</a>' for u, t in links)
        mail = "mailto:" + EMAIL + "?subject=" + quote(f"{nm} 매장 인테리어 자재 견적 요청") + "&body=" + quote("업체명·담당자:\n현장 주소:\n품목·규격·수량:\n재단 크기(있으면):\n희망 입고일:\n")
        fq = [(f"{nm} 인테리어에 많이 쓰는 자재는 무엇인가요?", f"{nm} 매장은 주로 {work} 공사를 합니다. 그래서 {', '.join(JN.get(m, m) for m in mats)}를 많이 씁니다.")] + common_fq
        _rx = re.compile('|'.join(VRX[m] for m in mats if m in VRX) or '자재')
        _vs = top(lambda v: v.get('type') != 'S' and _rx.search(v['title']), 6)
        _grx = {"cafe": "^cafe-", "brunch": "^cafe-", "bakery": "^cafe-", "coffeetakeout": "^cafe-", "bookcafe": "^cafe-", "winebar": "^cafe-", "pub": "^cafe-", "restaurant": "^cafe-",
                "showroom": "^store-", "stationery": "^store-", "unmanned": "^store-", "phone": "^store-", "optical": "^store-", "pharmacy": "^store-", "flower": "^store-",
                "office": "office", "realestate": "office", "church": "^cafe-wood-stage"}.get(slug)
        _gs = ""
        if _grx:
            try:
                import gonggan_data as _GD
                _sc = [x for x in _GD.SCENES if re.search(_grx, x[0])][:4]
                if _sc: _gs = '<section class="wrap sec"><h2>' + E(nm) + ' 공간 사진 — 자재 눌러 보기</h2><div class="gig">' + "".join(f'<a class="gi" href="/gonggan/{x[0]}.html"><img src="{x[2]}" alt="{E(x[1])}" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:10px"><small>{E(x[1].split(" — ")[0])}</small></a>' for x in _sc) + '</div></section>'
            except Exception:
                _gs = ""
        _vsec = (f'<section class="wrap sec"><h2>{E(nm)} 공사에 도움 되는 시공 영상</h2>{vsplit(_vs, "h3")}</section>') if _vs else ''
        body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/franchise/">체인점 인테리어 자재</a> › {E(nm)}</p>'
                f'<h1>{E(nm)} 인테리어 자재 — 프랜차이즈·체인점 매장 공사 업체용 재단·현장 배송</h1>'
                f'<p class="glead">{E(nm)}({E(alias)}) 매장 인테리어 공사에 들어가는 합판·MDF·석고보드·각재·몰딩·필름·루바·흡음재를 대전 유성 영진종합목재(월드건축자재) 3000평 매장에서 원하는 크기로 재단해 전국 현장으로 보내 드립니다. 같은 규격 매장을 여러 곳 하는 체인점 공사는 재단표 하나로 반복 납품하기 좋습니다.</p>'
                f'<div class="row"><a class="b r" href="{mail}">메일로 자재 견적 요청</a><a class="b d" href="tel:{tel}">전화 {TEL}</a><a class="b o" href="/cut.html">재단표 만들기</a></div>'
                f'<h2 class="gt">{E(nm)} 매장에서 주로 하는 공사</h2><p>{E(work)}</p>'
                f'<h2 class="gt">많이 쓰는 자재</h2><div class="qk">{mlinks}</div>'
                f'<h2 class="gt">공사할 때 챙길 것</h2><ul class="gtip">' + "".join(f"<li>{E(t)}</li>" for t in tips) + '<li>다중이용시설은 방염·불연 기준이 적용될 수 있으니 자재 성능을 미리 확인합니다.</li></ul>'
                f'<h2 class="gt">자주 쓰는 자재 기준가</h2>{ptab}<p class="gs">매장 소매 기준가(부가세 별도) · 운임 별도 · 사업자는 도매회원(wwood.kr) 가입 후 회원가. <a href="/price.html">전체 기준가</a></p>'
                f'<h2 class="gt">납품 순서</h2><ol class="gtip"><li>도면·재단표나 품목·규격·수량을 전화·메일로 보내 주세요.</li><li>자재값과 현장까지 운임을 먼저 알려 드립니다.</li><li>입금 확인 후 재단·상차해 현장으로 출고합니다.</li><li>같은 매장 규격이면 다음 현장부터 재단표를 그대로 씁니다.</li></ol>'
                '<h2 class="gt">공정별 자재</h2><div class="qk">' + "".join(f'<a href="/franchise/g-{g[0]}.html">{E(g[1])}</a>' for g in GJ) + '</div>'
                f'<h2 class="gt">관련 정보</h2><div class="qk">{ilinks}' + "".join(f'<a href="{u}">{E(t)}</a>' for u, t in INFO) + '<a href="/gonggan/">공간 사진</a><a href="/sigongbeop/">자재 시공법</a><a href="/calc.html">자재 계산기</a></div></section>'
                + _gs + _vsec
                + f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{faqslide(fq)}</section>'
                + f'<section class="wrap sec"><p class="small">다른 업종: ' + " · ".join(f'<a href="/franchise/{b[0]}.html">{E(b[1])}</a>' for b in BIZ if b[0] != slug) + '</p>'
                + (f'<p class="small">지역별 현장 배송: ' + " · ".join(f'<a href="/franchise/r-{r[0]}.html">{E(r[1])}</a>' for r in REG) + '</p>' if REG else "") + f'</section>{CTA}')
        ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}
        page(f"franchise/{slug}.html", f"{nm} 인테리어 자재 납품 — 체인점 매장 공사 재단·전국 현장 배송 | 영진목재",
             f"{nm}({alias}) 매장 인테리어 업체용 합판·MDF·석고보드·몰딩·필름 재단 납품. 같은 규격 체인점 반복 재단, 전국 현장 용달 배송(운임 견적). {TEL}", body, "", ld)
        out.append((slug, nm, alias))
    # 지역별
    for rslug, rnm, cities, uses, _ in REG:
        jeju = rslug == "jeju"
        fq = [(f"{rnm} 매장 공사 현장으로 자재를 보내 주나요?", ("제주는 화물 배편을 이용하며 운임·일정은 따로 상담합니다." if jeju else f"네. {rnm}({cities[:30]}) 현장까지 용달로 보내 드립니다. 운임은 거리·차량·수량에 따라 달라 주문 전 먼저 알려 드립니다."))] + common_fq[1:]
        body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/franchise/">체인점 인테리어 자재</a> › {E(rnm)}</p>'
                f'<h1>{E(rnm)} 체인점·프랜차이즈 매장 인테리어 자재 — 재단해서 현장으로</h1>'
                f'<p class="glead">{E(rnm)}({E(cities)})에서 카페·음식점·학원·병원·편의점 등 체인점 매장 인테리어 공사를 하는 업체에 합판·MDF·석고보드·각재·몰딩·필름·흡음재를 대전 3000평 매장에서 재단해 {"배편" if jeju else "용달"}로 보내 드립니다.</p>'
                f'<div class="row"><a class="b d" href="tel:{tel}">전화 {TEL}</a><a class="b o" href="/cut.html">재단표 만들기</a><a class="b o" href="/jeonguk/{rslug}.html">{E(rnm)} 배송 안내</a></div>'
                f'<h2 class="gt">업종별 자재 안내</h2><div class="qk">' + "".join(f'<a href="/franchise/{b[0]}.html">{E(b[1])}</a>' for b in BIZ) + '</div>'
                + ('<h2 class="gt">' + E(rnm) + ' 도시별 안내</h2><div class="qk">' + "".join(f'<a href="/franchise/c-{c[0]}.html">{E(c[1])} 인테리어 자재</a>' for c in CITY if c[2] == rslug) + '</div>' if any(c[2] == rslug for c in CITY) else '')
                + '<h2 class="gt">공정별 자재</h2><div class="qk">' + "".join(f'<a href="/franchise/g-{g[0]}.html">{E(g[1])}</a>' for g in GJ) + '</div>'
                + f'<h2 class="gt">자주 쓰는 자재 기준가</h2>{ptab}<p class="gs">소매 기준가(부가세 별도) · 운임 별도</p></section>'
                + f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{faqslide(fq)}</section>'
                + f'<section class="wrap sec"><p class="small">다른 지역: ' + " · ".join(f'<a href="/franchise/r-{r[0]}.html">{E(r[1])}</a>' for r in REG if r[0] != rslug) + f'</p></section>{CTA}')
        ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}
        page(f"franchise/r-{rslug}.html", f"{rnm} 체인점 인테리어 자재 납품 — 매장 공사 현장 재단 배송 | 영진목재",
             f"{rnm} 프랜차이즈·체인점 매장 인테리어 업체용 합판·MDF·석고보드·몰딩·필름. 대전 3000평 매장에서 재단해 현장 배송(운임 견적). {TEL}", body, "", ld)
    cards = "".join(f'<a class="gi" href="/franchise/{s}.html"><b>{E(n)}</b><small>{E(a)}</small></a>' for s, n, a in out)
    fq = common_fq
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}
    page("franchise/index.html", "프랜차이즈·체인점 인테리어 자재 납품 — 매장 공사 업체용 재단·전국 현장 배송 | 영진목재",
         f"프랜차이즈·체인점 매장 인테리어 업체를 위한 합판·MDF·석고보드·각재·몰딩·필름·흡음재 재단 납품. 같은 규격 반복 재단, 전국 현장 용달 배송, 사업자 도매회원. {TEL}",
         f'<section class="wrap sec gg"><h1>프랜차이즈·체인점 인테리어 자재 납품</h1>'
         f'<p class="glead">카페·음식점·학원·병원·편의점처럼 같은 디자인 매장을 전국에 여러 곳 공사하는 인테리어 업체라면, 대전 유성 영진종합목재(월드건축자재) 3000평 매장에서 자재를 재단해 현장으로 바로 받아 보세요. 재단표 하나로 매장마다 같은 크기를 반복해 보낼 수 있습니다.</p>'
         f'<div class="row"><a class="b d" href="tel:{tel}">전화 {TEL}</a><a class="b o" href="/cut.html">재단표 만들기</a><a class="b o" href="https://wwood.kr/">도매회원 쇼핑몰</a></div>'
         f'<h2 class="gt">업종별 자재 안내</h2><div class="gig">{cards}</div>'
         + (f'<h2 class="gt">지역별 현장 배송</h2><div class="qk">' + "".join(f'<a href="/franchise/r-{r[0]}.html">{E(r[1])}</a>' for r in REG) + '</div>' if REG else "")
         + '<h2 class="gt">공정별 자재</h2><div class="qk">' + "".join(f'<a href="/franchise/g-{g[0]}.html">{E(g[1])}</a>' for g in GJ) + '</div>'
         + '<h2 class="gt">도시별 현장 배송</h2><div class="qk">' + "".join(f'<a href="/franchise/c-{c[0]}.html">{E(c[1])}</a>' for c in CITY) + '</div>'
         + '<h2 class="gt">업체가 자주 찾는 정보</h2><div class="qk">' + "".join(f'<a href="{u}">{E(t)}</a>' for u, t in INFO) + '</div>'
         + f'<h2 class="gt">자주 쓰는 자재 기준가</h2>{ptab}<p class="gs">매장 소매 기준가(부가세 별도) · 운임 별도 · 사업자는 도매회원 가입 후 회원가</p></section>'
         f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{faqslide(fq)}</section>{CTA}', "", ld)
    gen_gj(page, E, CTA, faqslide, TEL, top, vsplit)
    gen_balju(page, E, CTA, TEL, EMAIL)
    gen_city(page, E, CTA, faqslide, TEL, ptab, top, vsplit)
    return out


# 상가·매장 공정별 자재 안내(인테리어 업체용) — /franchise/g-<slug>.html
GJ = [
 ("bangeum-room", "방음 룸", "상담실·연습실·노래방 방음 룸", ["벽을 이중으로 세우고 사이에 흡음재를 채웁니다.", "차음 석고보드를 겹쳐 붙이고 틈은 실리콘으로 막습니다.", "문은 방음 문이나 틈막이를 달고, 환기 덕트는 소음기를 생각합니다."],
  ["sound", "gypsum", "insul"], [("/qna/bangeum-gabyeok.html", "방음 가벽"), ("/qna/chaeum-seokgo.html", "차음 석고보드"), ("/qna/bangeum-mun.html", "방음 문"), ('/qna/cafe-soeum-julgi.html', '카페 소음 줄이기')]),
 ("hwajangsil", "화장실", "매장 화장실 리모델링", ["방수층을 먼저 확인·보수합니다.", "벽은 방수 석고보드·타일, 천장은 물에 강한 자재로 마감합니다.", "문은 습기에 강한 도어로 하고 문턱 높이를 맞춥니다."],
  ["tile", "gypsum", "door"], [("/qna/yoksil-cheonjang.html", "욕실 천장"), ("/qna/hwajangsil-munteul-gyoche.html", "화장실 문틀 교체"), ("/qna/hwajangsil-bangeum.html", "화장실 방음"), ('/qna/sangga-hwajangsil-naemsae.html', '상가 화장실 냄새')]),
 ("dancha", "단차·계단", "매장 입구 단차·내부 계단·단상", ["단차 높이와 쓰는 사람 동선을 확인합니다.", "구조재로 틀을 짜고 합판·마루로 덮습니다.", "모서리는 미끄럼 방지 마감과 몰딩으로 정리합니다."],
  ["gujo", "hapan", "maru", "molding"], [("/qna/hyeongwan-dancha.html", "단차 만들기"), ("/qna/gyedan-nonseulip.html", "계단 미끄럼 방지"), ("/qna/munteok-gyeongsaro.html", "경사로"), ('/qna/maejang-badak-mulmagi.html', '출입구 물막이턱'), ('/qna/sangga-gyedan-ripom.html', '상가 계단 리폼'), ('/qna/mudae-dansang-jejak.html', '무대·단상 제작'), ('/qna/sangga-ipgu-kkumigi.html', '상가 입구 꾸미기'), ('/qna/badak-dancha-magam.html', '단차 마감')]),
 ("facade", "쇼윈도·파사드", "매장 전면 파사드·쇼윈도", ["전면 바탕(각파이프·합판)을 단단히 잡습니다.", "외부 마감은 사이딩·방부목·외부용 패널 중 고릅니다.", "유리면 시트지·간판 위치를 함께 정합니다."],
  ["siding", "bangbu", "hardware"], [("/qna/yurichang-sheetji.html", "유리창 시트지"), ("/qna/ganpan-sigong.html", "간판 시공"), ('/qna/pasade-tteut.html', '파사드 뜻'), ('/qna/sangga-changmun-upung.html', '상가 창문 우풍'), ('/qna/sangga-oebyeok-kkumigi.html', '상가 외벽 꾸미기'), ('/qna/oebyeok-remodeling.html', '외벽 리모델링'), ('/qna/cafe-terrace.html', '카페 테라스'), ('/qna/sangga-folding-door.html', '상가 폴딩도어')]),
 ("baekroom", "창고·백룸", "매장 창고·직원 공간", ["창고 칸막이를 각재+석고나 합판으로 세웁니다.", "선반은 하중을 보고 각재·합판으로 짭니다.", "습기 찬 창고는 환기와 바닥 띄움을 생각합니다."],
  ["gujo", "hapan", "gypsum"], [("/qna/changgo-seonban.html", "창고 선반"), ("/qna/changgo-rack.html", "창고 랙")]),
 ("cheolgeo", "철거", "기존 매장 인테리어 철거", ["가벽·천장·바닥재·간판을 어디까지 뜯을지 임대 계약·원상복구 조건으로 정합니다.", "철거 전 전기·설비를 차단하고 남길 배관·배선을 표시합니다.", "폐기물은 성상별로 나눠 처리 업체를 미리 잡습니다."],
  [], [("/geuncheo.html", "현장 근처 폐기물·용달 찾기"), ("/qna/sangga-wonsang-bokgu.html", "상가 원상복구"), ('/qna/mokjae-pegimul.html', '목재 폐기물 버리기'), ('/qna/sangga-naemsae-ppaegi.html', '전 업종 냄새 빼기')]),
 ("gabyeok", "가벽·칸막이", "목공 가벽·경량 칸막이", ["바닥·천장에 런너(또는 각재)를 고정하고 스터드를 세웁니다.", "소리를 막을 벽은 사이에 흡음재를 채웁니다.", "석고보드를 한 겹 또는 두 겹 붙이고 이음부를 퍼티로 잡습니다."],
  ["gypsum", "gujo", "sound"], [("/gabyeok-gyesan.html", "가벽 자재 계산기"), ("/qna/sigma-stud.html", "경량 스터드"), ("/qna/seokgo-myeotjang.html", "석고보드 몇 장"), ('/qna/samusil-gabyeok-self.html', '사무실 가벽 셀프'), ('/qna/samusil-gabyeok-vs-partition.html', '가벽 vs 파티션'), ('/qna/sikdang-kanmagi.html', '식당 칸막이'), ('/qna/hagwon-interior-jajae.html', '학원 강의실 나누기'), ('/qna/gyeongryang-kanmagi.html', '경량칸막이'), ('/qna/seokgo-kanmagi.html', '석고 칸막이'), ('/qna/corner-bead.html', '코너비드'), ('/qna/gansal-tteut.html', '간살 뜻'), ('/qna/gabyeok-munteul.html', '가벽 문틀'), ('/qna/gabyeok-cheolgeo-heoga.html', '가벽 철거 허가 확인')]),
 ("cheonjang", "천장", "석고 천장·루바 천장·흡음 천장", ["천장 각재(또는 경량 천장틀)로 틀을 짜고 조명·에어컨 자리를 미리 냅니다.", "석고보드·루바·흡음재 중 매장 콘셉트에 맞는 마감을 붙입니다.", "노출 천장은 기존 구조물을 정리하고 도장합니다."],
  ["gypsum", "hinoki", "sound"], [("/qna/cheonjang-mokgong-bangbeop.html", "천장 목공 방법"), ("/sigongbeop/rubaa-cheonjang.html", "루바 천장 시공법"), ("/bigyo/heupeum-board.html", "흡음보드 비교"), ('/qna/sangga-cheonjang-mokgong.html', '상가 천장 목공'), ('/qna/sangga-cheonjang-tex.html', '상가 천장 텍스 교체'), ('/qna/nochul-cheonjang.html', '노출천장'), ('/qna/cafe-cheonjang-magam.html', '카페 천장 마감'), ('/qna/cheonjang-heubeumjae-self.html', '천장 흡음재 셀프'), ('/qna/sangga-nusu.html', '상가 누수 찾기'), ('/qna/cheonjang-magamjae-jongryu.html', '천장 마감재 종류'), ('/qna/cheonjang-seokgo-anka.html', '천장 앙카')]),
 ("counter", "카운터·바", "카운터·바 테이블·진열대 제작", ["카운터 몸통은 각재·합판으로 짜고 겉은 MDF·필름이나 타일로 마감합니다.", "상판은 물·열을 생각해 집성판·인조석 등으로 고릅니다.", "포스·전원 배선 구멍을 제작 단계에서 냅니다."],
  ["jipseong", "mdf", "hapan"], [("/qna/counter-jejak.html", "카운터 제작"), ("/qna/bar-table.html", "바 테이블"), ("/cut.html", "재단표 만들기"), ('/qna/cafe-bar-table-nopi.html', '카페 바테이블 높이'), ('/qna/maejang-counter-nopi.html', '매장 카운터 높이'), ('/qna/wonmok-counter.html', '원목 카운터 제작'), ('/qna/bar-uija-nopi.html', '바 의자 높이')]),
 ("byeok", "벽 마감", "필름·도장·템바보드·타일 벽", ["벽 바탕을 평평하게 퍼티하고 샌딩합니다.", "필름은 프라이머 후 붙이고, 도장은 하도·상도 순서로 칠합니다.", "템바보드·패널은 본드와 타카로 고정하고 모서리를 몰딩으로 마감합니다."],
  ["film", "molding", "tile"], [("/qna/film-sunseo.html", "필름 시공 순서"), ("/qna/tempa-myeotjang.html", "템바보드 몇 장"), ("/qna/seokgo-putty.html", "석고 퍼티"), ('/qna/gage-byeok-kkumigi.html', '가게 벽면 꾸미기'), ('/qna/gage-byeok-hapan.html', '가게 벽 합판 작업'), ('/qna/cafe-byeok-interior.html', '카페 벽면'), ('/qna/sikdang-byeok-kkumigi.html', '식당 벽 꾸미기'), ('/qna/seokgo-putty.html', '석고 퍼티 작업'), ('/qna/dojang-sunseo.html', '도장 순서'), ('/qna/wood-louver.html', '우드 루버'), ('/qna/hapan-interior-cafe.html', '합판 인테리어'), ('/qna/byeok-magam-bangbeop.html', '벽 마감 방법'), ('/qna/byeok-film-sigong.html', '벽 필름 시공')]),
 ("badak", "바닥", "데코타일·타일·마루 바닥", ["기존 바닥 수평과 들뜸을 확인하고 필요하면 레벨링합니다.", "데코타일은 기준선을 잡고 본드로 붙이며, 타일은 접착제·줄눈까지 마감합니다.", "주방·물 쓰는 구역은 물에 강한 바닥재를 씁니다."],
  ["tile", "maru"], [("/qna/decotile-sijakjeom.html", "데코타일 시작점"), ("/qna/tile-jeopchakje.html", "타일 접착제"), ("/dobae-jangpan.html", "바닥재 계산기"), ('/qna/maejang-badak-bigyo.html', '매장 바닥 비교'), ('/qna/maejang-badak-sigong.html', '매장 바닥 시공'), ('/qna/maejang-badak-mulmagi.html', '매장 바닥 물 막기'), ('/qna/samusil-badakjae-jongryu.html', '사무실 바닥재'), ('/qna/sangga-badak-jangpan-vs-decotile.html', '장판 vs 데코타일'), ('/qna/maejang-badak-deultteum.html', '매장 바닥 들뜸 보수'), ('/qna/badak-supyeong-moltal.html', '바닥 수평 몰탈'), ('/qna/badak-hapan-jongryu.html', '바닥 합판 종류')]),
 ("mun", "문·도어", "매장 출입문·방화문·실내 도어", ["문틀 크기와 열림 방향을 실측합니다.", "방화구획·피난 관련 문은 정해진 성능의 문을 씁니다.", "도어클로저·손잡이·잠금장치를 함께 맞춥니다."],
  ["door", "hardware"], [("/qna/door-silcheuk.html", "문 실측"), ("/qna/banghwamun.html", "방화문"), ("/qna/door-closer.html", "도어클로저"), ('/qna/sikdang-kanmagi-mun.html', '식당 칸막이 문'), ('/qna/sangga-munteum.html', '상가 문틈 막기'), ('/qna/sangga-chulipmun-gyoche.html', '상가 출입문 교체'), ('/qna/maejang-ipgu-baram.html', '매장 입구 바람 막기'), ('/qna/gangwha-door-suri.html', '강화도어 수리'), ('/qna/munteul-seolchi.html', '문틀 설치'), ('/qna/yeodaji-mun-seolchi.html', '여닫이문 설치'), ('/qna/sliding-door-suri.html', '슬라이딩도어 수리'), ('/qna/jungmun-jongryu.html', '중문 종류')]),
 ("jubang", "주방", "매장 주방 벽·천장", ["주방 벽은 방수·불연 성능을 보고 석고보드·타일을 고릅니다.", "후드·덕트 자리와 배관 위치를 목공 전에 확정합니다.", "벽과 바닥이 만나는 곳은 실리콘으로 막아 물이 스며들지 않게 합니다."],
  ["gypsum", "tile"], [("/qna/jubang-byeok.html", "주방 벽"), ("/qna/bangsu-seokgo.html", "방수 석고보드"), ("/qna/banghwa-seokgo.html", "방화 석고보드"), ('/qna/cafe-jubang-seonban.html', '카페 주방 선반·동선'), ('/qna/samusil-hyugesil.html', '휴게실·탕비실')]),
 ("ganpan", "간판·외부", "간판 바탕·외부 마감", ["간판을 달 외벽 바탕(각파이프·합판)을 단단히 고정합니다.", "외부 목재는 방부목·외부용 마감으로 비를 막습니다.", "어닝·캐노피 등 외부 구조물은 건물 관리 규정을 먼저 확인합니다."],
  ["bangbu", "hardware", "siding"], [("/qna/ganpan-sigong.html", "간판 시공"), ("/qna/oebyeok-paint.html", "외벽 페인트"), ('/qna/ganpan-frame.html', '간판 프레임'), ('/qna/namu-ganpan-jaeryo.html', '나무 간판 재료')]),
 ("jomyeong", "조명 바탕 목공", "간접조명 홈·라인조명·커튼박스 목공", ["조명 위치·종류(라인·매입·간접)와 전선 자리를 전기 업체와 먼저 정합니다.", "천장·벽에 각재로 간접조명 턱이나 라인조명 홈 바탕을 짭니다.", "석고보드·몰딩으로 덮어 빛이 새는 선을 정리하고 도장·필름으로 마감합니다."],
  ["gujo", "gypsum", "molding"], [("/qna/line-jomyeong.html", "라인조명"), ("/qna/ganjeop-molding-self.html", "간접조명 몰딩"), ("/qna/uomul-cheonjang-ganjeop.html", "우물천장 간접조명"), ("/qna/curtainbox-ganjeop.html", "커튼박스 간접조명"), ("/qna/jomyeong-baechi.html", "조명 배치")]),
 ("seonban", "선반·집기", "벽 선반·진열 집기", ["벽 진열은 바탕 합판이나 각재에 브라켓을 고정합니다.", "같은 크기 선반판은 재단표로 반복 재단합니다.", "무거운 진열은 선반 두께와 받침 간격을 넉넉히 잡습니다."],
  ["jipseong", "mdf", "hardware"], [("/qna/seonban-bracket.html", "선반 브라켓"), ("/qna/system-seonban.html", "시스템 선반"), ("/qna/maejang-banbok-jaedan.html", "같은 규격 반복 재단"), ('/qna/mujiju-byeokseonban.html', '무지주 벽선반'), ('/qna/seonban-seolchi-bupum.html', '선반 설치 부품'), ('/qna/pantry-sunapjang.html', '펜트리 수납장')]),
]

# 사장님 지시(2026-11-28 "야금야금 말고 대량"): 업종 20개·공정 5개 한꺼번에 추가
BIZ += [
 ("gukbap", "국밥·해장국집", "순대국·감자탕·설렁탕·해장국 식당", "주방 벽·바닥 물청소 마감, 좌석 칸막이, 카운터, 신발장(좌식)", ["tile", "jipseong", "gypsum", "molding"], ["국물·김이 많은 주방은 벽·천장을 물과 습기에 강한 마감으로 합니다.", "좌식 자리는 단을 올려 합판·마루로 덮고 모서리를 몰딩으로 정리합니다."], [("/qna/sikdang-table-sangpan.html", "식당 테이블 상판"), ("/qna/sikdang-kanmagi.html", "식당 칸막이"), ("/qna/mudae-dansang-jejak.html", "좌식 단 올리기")]),
 ("cafeteria", "구내식당·급식소", "회사 구내식당·단체 급식소", "배식대 주변 벽·바닥, 퇴식구 칸막이, 식탁 상판, 대기 동선", ["tile", "jipseong", "gypsum"], ["배식·퇴식 동선이 엇갈리지 않게 칸막이 위치를 먼저 정합니다.", "식탁 상판은 같은 규격으로 한 번에 재단하면 공사가 빠릅니다."], [("/qna/maejang-banbok-jaedan.html", "같은 규격 반복 재단"), ("/qna/sikdang-table-sangpan.html", "식당 테이블 상판"), ("/qna/maejang-badak-bigyo.html", "매장 바닥 비교")]),
 ("juice", "생과일주스·스무디 전문점", "주스 바·스무디·테이크아웃 음료", "카운터·바 목공, 벽 메뉴판, 냉장 쇼케이스 주변 마감", ["jipseong", "film", "tile", "hinoki"], ["과일즙·물이 튀는 카운터는 상판과 앞면을 물에 강하게 마감합니다.", "메뉴판 벽은 하지를 보강해 무거운 메뉴판도 걸 수 있게 합니다."], [("/qna/takeout-coffee-interior.html", "테이크아웃 매장 인테리어"), ("/qna/maejang-counter-nopi.html", "카운터 높이"), ("/qna/urethane-coating.html", "우레탄 코팅")]),
 ("mart", "동네 마트·식자재 마트", "슈퍼마켓·식자재 마트", "바닥 마감, 벽면 진열 하지, 창고 선반, 계산대", ["tile", "hapan", "gujo", "hardware"], ["카트·지게차가 다니는 바닥은 단단한 바닥재로 합니다.", "창고 선반은 무게를 버티게 구조목·합판으로 짜고 벽에 고정합니다."], [("/qna/munggu-interior.html", "진열 선반·통로"), ("/qna/changgo-seonban.html", "창고 선반"), ("/qna/maejang-badak-bigyo.html", "매장 바닥 비교")]),
 ("fruit", "과일가게·청과", "과일·채소 가게", "진열 단(계단식 진열대), 바닥 물청소 마감, 차양·입구", ["jipseong", "bangbu", "stain", "tile"], ["계단식 과일 진열대는 집성판·방부목으로 짜고 물에 강하게 마감합니다.", "입구 쪽 진열대는 비·햇빛을 가릴 차양과 함께 계획합니다."], [("/qna/maejang-jinyeoldae-jejak.html", "매장 진열대 제작"), ("/qna/sangga-ipgu-kkumigi.html", "상가 입구 꾸미기"), ("/qna/awning.html", "어닝")]),
 ("tteokjip", "떡집·한과점", "떡집·방앗간·한과·디저트 떡", "작업장 벽·바닥 위생 마감, 진열장, 카운터", ["tile", "jipseong", "gypsum"], ["찜기·김이 많은 작업장은 습기에 강한 마감과 환기를 함께 챙깁니다.", "진열장은 높이를 낮게 해 상품이 잘 보이게 합니다."], [("/qna/jinyeoljang.html", "진열장 만들기"), ("/qna/salad-dosirak-interior.html", "위생 주방 마감"), ("/qna/maejang-counter-nopi.html", "카운터 높이")]),
 ("cosmetics", "화장품·뷰티 편집숍", "화장품 매장·뷰티 편집숍", "벽면 진열장·간접조명, 테스터 테이블, 거울", ["jipseong", "mdf", "film", "molding"], ["진열 선반마다 간접 조명 자리를 미리 내면 상품이 돋보입니다.", "테스터 테이블은 화장품이 묻어도 닦기 쉬운 마감으로 합니다."], [("/qna/jinyeoljang-led.html", "진열장 LED"), ("/qna/maejang-jinyeoldae-jejak.html", "매장 진열대 제작"), ("/qna/geoul-dalgi.html", "거울 달기")]),
 ("barbershop", "바버샵·남성 미용실", "바버샵·남성 커트 전문점", "벽 우드·타일 포인트, 거울·선반, 대기 벤치", ["jipseong", "tile", "hinoki", "stain"], ["거울·선반이 많은 벽은 하지를 보강하고 배선 위치를 먼저 정합니다.", "머리카락 청소가 잦은 바닥은 이음새가 적은 마감으로 합니다."], [("/qna/small-salon-interior.html", "작은 미용실 인테리어"), ("/qna/geoul-dalgi.html", "거울 달기"), ("/qna/wood-louver.html", "우드 루버")]),
 ("massage", "마사지·스파", "마사지숍·스파·타이마사지", "관리룸 가벽·방음, 간접 조명, 샤워실 방수", ["gypsum", "sound", "door", "tile"], ["관리룸 사이 가벽에 흡음재를 채워 대화가 새지 않게 합니다.", "샤워실이 있으면 방수 석고·타일로 마감합니다."], [("/qna/pibu-gwanrisil-interior.html", "관리룸 가벽·방음"), ("/qna/seokgo-kanmagi.html", "석고 칸막이"), ("/qna/bangsu-seokgo.html", "방수 석고보드")]),
 ("sauna", "찜질방·사우나", "찜질방·사우나·한증막", "휴게 공간 목재 마감, 히노끼·편백 벽, 습기·온도 관리", ["hinoki", "gujo", "insul", "tile"], ["열과 습기가 많은 공간은 수종과 마감을 신중히 고릅니다.", "휴게실 벽·천장은 편백·히노끼 루바로 분위기를 냅니다."], [("/qna/hinoki-yokjo.html", "히노끼 욕조·습기"), ("/qna/cheonjang-ruba-tteut.html", "루바 천장"), ("/qna/samnamu-vs-pyeonbaek.html", "삼나무 vs 편백")]),
 ("seminar", "강의장·세미나실", "교육장·세미나룸·대관 강의실", "단상, 흡음 벽·천장, 가변 칸막이, 수납장", ["gujo", "hapan", "sound", "gypsum"], ["말소리가 또렷하게 들리게 벽·천장 일부에 흡음재를 넣습니다.", "단상은 구조목 틀 + 두꺼운 합판으로 튼튼하게 만듭니다."], [("/qna/mudae-dansang-jejak.html", "무대·단상 제작"), ("/qna/hoeuisil-interior.html", "회의실 인테리어"), ("/qna/cafe-soeum-julgi.html", "울림 줄이기")]),
 ("library", "작은도서관·북스테이", "작은도서관·마을 서재", "벽면 책장, 좌식 열람 공간, 조명", ["jipseong", "hapan", "maru"], ["책 무게로 선반이 처지지 않게 두께와 받침 간격을 넉넉히 잡습니다.", "아이 열람 공간은 모서리를 둥글게 하고 책장을 벽에 고정합니다."], [("/qna/manhwa-cafe-interior.html", "책장·좌식 룸"), ("/qna/seonban-cheojim.html", "선반 처짐"), ("/qna/geosil-byeok-sunapjang.html", "벽면 수납장")]),
 ("senior", "경로당·노인정", "경로당·마을회관·쉼터", "문턱 제거, 안전 손잡이, 좌식·입식 공간, 미끄럼 방지 바닥", ["hardware", "maru", "tile"], ["어르신이 걸려 넘어지지 않게 문턱을 없애고 손잡이를 답니다.", "바닥은 미끄럼이 적고 따뜻한 마감으로 합니다."], [("/qna/yoyangwon-interior.html", "안전 손잡이·미끄럼 방지"), ("/qna/munteok-jegeo.html", "문턱 제거"), ("/qna/badak-dancha-magam.html", "단차 마감")]),
 ("gallery", "갤러리·전시장", "갤러리·전시 공간·팝업 스토어", "전시 가벽, 흰 벽 마감, 레일 조명·작품 걸이", ["gypsum", "gujo", "hapan"], ["작품을 거는 가벽은 합판 바탕을 넣어 어디든 걸 수 있게 합니다.", "흰 벽은 퍼티·도장을 꼼꼼히 해 얼룩 없이 마감합니다."], [("/qna/samusil-gabyeok-self.html", "가벽 세우기"), ("/qna/dojang-sunseo.html", "도장 순서"), ("/qna/gage-byeok-hapan.html", "벽 합판 바탕")]),
 ("climbing", "클라이밍장", "실내 암벽·볼더링짐", "인공 암벽 바탕 합판·구조, 바닥 매트 영역, 대기 공간", ["hapan", "gujo", "hardware"], ["암벽 구조와 홀드 고정은 전문 업체 기준을 따르고, 목재는 그 기준에 맞춰 준비합니다.", "대기·탈의 공간은 가벽으로 나눕니다."], [("/qna/climbing-byeok.html", "클라이밍 벽"), ("/qna/hapan-dukke-t-tteut.html", "합판 두께"), ("/qna/samusil-gabyeok-self.html", "가벽 세우기")]),
 ("escape", "방탈출 카페", "방탈출·체험형 테마 카페", "테마 룸 가벽·방음, 소품 목공, 비밀문·장치 틀", ["gypsum", "gujo", "hapan", "sound"], ["테마 룸 사이 가벽에 흡음재를 넣어 다른 방 소리가 들리지 않게 합니다.", "소품·장치 틀은 합판·각재로 튼튼하게 만들고 모서리를 다듬습니다."], [("/qna/seokgo-kanmagi.html", "석고 칸막이"), ("/qna/bangyeom-tteut.html", "방염 뜻"), ("/qna/gabyeok-munteul.html", "가벽 문틀")]),
 ("bikeshop", "자전거·킥보드 매장", "자전거 판매·수리점", "벽걸이 거치대 하지, 작업대, 바닥 마감", ["hapan", "gujo", "hardware", "tile"], ["자전거를 벽에 거는 거치대는 벽 하지·합판 바탕에 단단히 고정합니다.", "수리 작업대는 두꺼운 상판으로 만듭니다."], [("/qna/gabyeok-tagongpan.html", "타공판 벽"), ("/qna/byeok-seonban-gojeong.html", "벽 고정"), ("/qna/table-sangpan-jejak.html", "작업대 상판")]),
 ("dogcafe", "애견카페·고양이카페", "반려동물 동반 카페", "바닥 미끄럼 방지, 벽 하부 보호, 분리 펜스, 캣워크·선반", ["tile", "jipseong", "gujo", "stain"], ["동물 발이 미끄러지지 않고 청소가 쉬운 바닥을 고릅니다.", "캣워크·선반은 벽에 단단히 고정하고 모서리를 다듬습니다."], [("/qna/aegyeonshop-interior.html", "애견샵 인테리어"), ("/qna/banryeo-badak.html", "반려동물 바닥"), ("/qna/byeok-seonban-gojeong.html", "벽 선반 고정")]),
 ("artacademy", "미술학원·화실", "미술학원·입시미술·화실", "작품 걸이 벽, 수납장, 개수대 주변 마감, 조명", ["hapan", "jipseong", "tile"], ["작품을 거는 벽은 합판 바탕을 대 어디든 걸 수 있게 합니다.", "물감을 씻는 개수대 주변은 물에 강한 마감으로 합니다."], [("/qna/gallery-byeok.html", "작품 거는 벽"), ("/qna/hagwon-interior-jajae.html", "학원 인테리어"), ("/qna/gage-byeok-hapan.html", "벽 합판 바탕")]),
 ("dance", "댄스·발레 학원", "댄스 스튜디오·발레·방송댄스", "마루 바닥, 전면 거울, 바(발레바), 방음", ["maru", "gypsum", "sound", "hardware"], ["점프·회전이 많아 충격을 덜어 주는 마루 바닥을 씁니다.", "전면 거울과 발레바는 벽 하지에 단단히 고정합니다."], [("/qna/taekwondo-interior.html", "거울·매트 바닥"), ("/qna/eumak-hagwon-interior.html", "연습실 방음"), ("/qna/geoul-dalgi.html", "거울 달기")]),
]
GJ += [
 ("jinyeol", "진열대·진열장", "벽면 진열장·가운데 진열대·쇼케이스 주변", ["상품 크기에 맞춰 칸 높이·깊이를 정합니다.", "집성판·MDF로 몸체를 짜고 조명 자리를 미리 냅니다.", "무거운 진열장은 벽 하지에 단단히 고정합니다."], ["jipseong", "mdf", "hardware"], [("/qna/maejang-jinyeoldae-jejak.html", "매장 진열대 제작"), ("/qna/jinyeoljang-led.html", "진열장 LED"), ("/qna/munggu-interior.html", "진열 선반·통로")]),
 ("fitting", "탈의실·피팅룸", "옷가게·헬스장·병원 탈의실", ["각재 틀에 합판·석고보드를 붙여 칸을 나눕니다.", "앞쪽에 커튼 레일이나 문을 답니다.", "안쪽 벽에 거울·옷걸이를 하지에 고정합니다."], ["gujo", "hapan", "hardware"], [("/qna/fitting-room-jejak.html", "피팅룸 제작"), ("/qna/curtain-rail.html", "커튼 레일"), ("/qna/geoul-dalgi.html", "거울 달기")]),
 ("terrace", "테라스·외부 데크", "매장 앞 테라스·옥상 데크", ["바닥 상태(콘크리트·흙·방수층)를 확인하고 기초를 정합니다.", "방부목·합성데크로 바닥을 깔고 난간·화분대를 세웁니다.", "외부용 오일스테인으로 마감하고 어닝·차양을 더합니다."], ["bangbu", "hapdeck", "stain"], [("/qna/cafe-terrace.html", "카페 테라스"), ("/qna/oksang-deck-sigong.html", "옥상 데크 시공"), ("/qna/deck-nangan-nopi.html", "데크 난간 높이·간격")]),
 ("yuri", "유리 칸막이·회의실", "사무실 유리 파티션·회의실", ["유리 칸막이 위치와 문 위치를 정합니다.", "하부·상부 틀을 바닥·천장(슬래브까지)에 고정합니다.", "시트지로 시선을 적당히 가리고 문을 답니다."], ["gujo", "gypsum", "film"], [("/qna/hoeuisil-interior.html", "회의실 인테리어"), ("/qna/yuri-gabyeok.html", "유리 가벽"), ("/qna/yurichang-sheetji.html", "유리창 시트지")]),
 ("sunap", "붙박이 수납·벽장", "매장 창고장·직원 수납·벽면 수납", ["넣을 물건과 무게에 맞춰 칸을 나눕니다.", "집성판·합판을 재단해 몸체를 짜고 벽에 고정합니다.", "문짝·손잡이를 달고 마감합니다."], ["jipseong", "hapan", "hardware"], [("/qna/geosil-byeok-sunapjang.html", "벽면 수납장"), ("/qna/pantry-sunapjang.html", "펜트리 수납장"), ("/qna/seonban-seolchi-bupum.html", "선반 설치 부품")]),
]



def gen_gj(page, E, CTA, faqslide, TEL, top=None, vsplit=None):
    tel = TEL.replace("-", "")
    order = " → ".join(g[1] for g in GJ)
    for slug, nm, full, steps, mats, links in GJ:
        mlinks = "".join(f'<a href="/jajae/{m}.html">{E(JN.get(m, m))}</a>' for m in mats)
        ilinks = "".join(f'<a href="{u}">{E(t)}</a>' for u, t in links)
        _kw = {"cheolgeo": "철거", "gabyeok": "가벽|칸막이", "cheonjang": "천장|루바|텍스", "counter": "카운터|상판|싱크대", "byeok": "필름|템바|도장|페인트|아트월", "badak": "데코타일|타일|마루|장판",
               "mun": "중문|방문|도어|문틀", "jubang": "주방|싱크대|타일", "ganpan": "간판|외벽|사이딩", "seonban": "선반|수납|진열", "bangeum-room": "방음|흡음", "hwajangsil": "욕실|화장실",
               "dancha": "계단|단차|단상", "jomyeong": "조명|간접", "facade": "외벽|사이딩|파사드", "baekroom": "창고|선반"}.get(slug, nm)
        _vs = top(lambda v: v.get("type") != "S" and re.search(_kw, v["title"]), 6) if top else []
        _vsec = (f'<section class="wrap sec"><h2>{E(nm)} 시공 영상</h2>{vsplit(_vs, "h3")}</section>') if (_vs and vsplit) else ""
        fq = [(f"매장 {nm} 공사 자재를 현장으로 받을 수 있나요?", "네. 품목·규격·수량·재단 크기·현장 주소를 보내 주시면 자재값과 운임을 먼저 알려 드리고, 입금 확인 후 재단·상차해 용달로 보냅니다."),
              ("여러 매장 같은 공사를 반복하는데요?", "같은 재단표로 매장마다 같은 크기로 재단해 보낼 수 있습니다. 매장마다 달라지는 치수만 실측해 알려 주세요."),
              ("사업자 회원가가 있나요?", "사업자등록증·명함 확인 후 도매회원(wwood.kr)으로 가입하시면 회원가로 주문하실 수 있습니다.")]
        body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/franchise/">체인점 인테리어 자재</a> › 공정별 › {E(nm)}</p>'
                f'<h1>상가·매장 {E(nm)} 공사 자재 — {E(full)}</h1>'
                f'<p class="glead">카페·음식점·학원·병원 같은 체인점 매장 인테리어에서 {E(full)} 공정에 들어가는 자재와 순서를 정리했습니다. 자재는 대전 유성 영진종합목재(월드건축자재) 3000평 매장에서 재단해 전국 현장으로 보냅니다.</p>'
                f'<div class="row"><a class="b d" href="tel:{tel}">전화 {TEL}</a><a class="b o" href="/cut.html">재단표 만들기</a><a class="b o" href="/calc.html">자재 계산기</a></div>'
                f'<h2 class="gt">공정 순서</h2><ol class="gtip">' + "".join(f"<li>{E(s)}</li>" for s in steps) + '</ol>'
                + (f'<h2 class="gt">이 공정 자재</h2><div class="qk">{mlinks}</div>' if mats else "")
                + f'<h2 class="gt">관련 정보</h2><div class="qk">{ilinks}</div>'
                f'<h2 class="gt">매장 공사 전체 순서</h2><p>{E(order)}</p><div class="qk">' + "".join(f'<a href="/franchise/g-{g[0]}.html">{E(g[1])}</a>' for g in GJ if g[0] != slug) + '</div></section>'
                + _vsec
                + f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{faqslide(fq)}</section>'
                + '<section class="wrap sec"><p class="small">업종별 자재: ' + " · ".join(f'<a href="/franchise/{b[0]}.html">{E(b[1])}</a>' for b in BIZ[:20]) + ' · <a href="/franchise/">전체</a></p></section>' + CTA)
        ld = {"@context": "https://schema.org", "@type": "HowTo", "name": f"상가·매장 {nm} 공사 순서", "step": [{"@type": "HowToStep", "text": s} for s in steps]}
        page(f"franchise/g-{slug}.html", f"상가 {nm} 공사 자재 — 매장 인테리어 {full} 순서·재단 납품 | 영진목재",
             f"체인점·상가 매장 인테리어 {full} 공정의 순서와 필요한 자재. 대전 3000평 매장에서 재단해 전국 현장 배송(운임 견적). {TEL}", body, "", ld)


def gen_balju(page, E, CTA, TEL, EMAIL):
    """업체용 자재 발주서 — 품목 줄을 넣고 메일 보내기·인쇄(서버 없이 이 화면에서만)."""
    tel = TEL.replace("-", "")
    body = ('<section class="wrap sec gg"><p class="crumb"><a href="/franchise/">체인점 인테리어 자재</a> › 자재 발주서</p>'
            '<h1>인테리어 자재 발주서 — 업체용 무료 양식(메일 보내기·인쇄)</h1>'
            '<p class="glead">매장·상가 인테리어 현장에 필요한 자재를 줄마다 적고 <b>메일로 보내기</b>를 누르면 영진종합목재(월드건축자재)로 견적 요청 메일이 만들어집니다. 인쇄해서 현장 발주서로 써도 됩니다. 적은 내용은 이 화면에만 있고 어디에도 저장되지 않습니다.</p>'
            '<div class="bj"><div class="bjh"><label>업체명·담당자 <input id="bjc" placeholder="예: ○○인테리어 홍길동"></label><label>현장 주소 <input id="bja" placeholder="예: 서울 ○○구 ○○로"></label><label>희망 입고일 <input id="bjd" placeholder="예: 12월 5일 오전"></label></div>'
            '<table class="rt" id="bjt"><thead><tr><th>품목</th><th>규격(두께·크기)</th><th>수량</th><th>재단 크기(있으면)</th></tr></thead><tbody></tbody></table>'
            '<div class="row"><button class="b o" type="button" id="bjadd">줄 추가</button><button class="b r" type="button" id="bjmail">메일로 보내기</button><button class="b o" type="button" onclick="print()">인쇄</button>'
            f'<a class="b d" href="tel:{tel}">전화 {TEL}</a></div>'
            '<p class="gs">메일을 보낸 뒤 꼭 매장(' + TEL + ')에 전화해 주세요. 자재값과 운임을 먼저 알려 드리고, 입금 확인 후 재단·출고합니다. 사업자는 도매회원(wwood.kr) 가입 후 회원가로 거래합니다.</p></div>'
            '<h2 class="gt">자주 쓰는 품목 예시</h2><p>석고보드 일반 9.5T 3×6 · 방수 석고보드 9.5T · 다루끼 1.0×1.0 12자 · 구조재 2×4 12자 · MDF 9·18mm 4×8 · 내수합판 12mm 4×8 · 인테리어 필름 · 몰딩 · 템바보드 · 흡음보드</p>'
            '<div class="qk"><a href="/cut.html">재단표 만들기</a><a href="/calc.html">자재 계산기</a><a href="/price.html">기준가</a><a href="/franchise/">업종별 자재</a><a href="/dome.html">도매회원</a></div></section>'
            '<style>.bjh{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:10px 0}.bjh label{display:flex;flex-direction:column;font-weight:700;gap:4px}.bj input{font-size:17px;padding:10px;border:1px solid #ccc;border-radius:8px;width:100%;box-sizing:border-box}#bjt td{padding:4px}@media print{header,footer,.row,.qk,nav{display:none!important}}</style>'
            '<script>(function(){var tb=document.querySelector("#bjt tbody");function add(){var tr=document.createElement("tr");for(var i=0;i<4;i++){var td=document.createElement("td"),inp=document.createElement("input");inp.placeholder=["석고보드","9.5T 3×6","20장","—"][i];td.appendChild(inp);tr.appendChild(td)}tb.appendChild(tr)}for(var k=0;k<6;k++)add();document.getElementById("bjadd").onclick=add;'
            'document.getElementById("bjmail").onclick=function(){var v=function(id){return document.getElementById(id).value.trim()};var L=[];[].forEach.call(tb.rows,function(r){var c=[].map.call(r.querySelectorAll("input"),function(x){return x.value.trim()});if(c.join(""))L.push("- "+c[0]+" / "+c[1]+" / "+c[2]+(c[3]?" / 재단 "+c[3]:""))});'
            'var b="업체·담당: "+v("bjc")+"\\n현장 주소: "+v("bja")+"\\n희망 입고일: "+v("bjd")+"\\n\\n[품목 / 규격 / 수량 / 재단]\\n"+L.join("\\n")+"\\n\\n자재값·운임 견적 부탁드립니다.";'
            'location.href="mailto:' + EMAIL + '?subject="+encodeURIComponent("[자재 발주] "+(v("bjc")||"인테리어 현장"))+"&body="+encodeURIComponent(b)}})();</script>'
            + CTA)
    ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "인테리어 자재 발주서", "applicationCategory": "BusinessApplication", "operatingSystem": "Web", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"}}
    page("franchise/balju.html", "인테리어 자재 발주서 양식 — 업체용 무료, 메일로 바로 견적 요청 | 영진목재",
         "매장·상가 인테리어 현장 자재를 줄마다 적고 메일로 보내기·인쇄. 석고보드·각재·합판·MDF·필름 견적 요청과 재단·전국 현장 배송. 업체용 무료 자재 발주서.", body, "", ld)


# 도시별 '○○ 인테리어 자재' — 대전 매장에서 재단해 그 도시 현장으로(현지 매장인 척 하지 않음)
CITY = [("seoul", "서울", "seoul"), ("busan", "부산", "busan-gyeongnam"), ("incheon", "인천", "incheon"), ("daegu", "대구", "daegu-gyeongbuk"),
        ("gwangju", "광주", "gwangju-jeonnam"), ("ulsan", "울산", "busan-gyeongnam"), ("suwon", "수원", "gyeonggi-south"), ("seongnam", "성남", "gyeonggi-south"),
        ("yongin", "용인", "gyeonggi-south"), ("hwaseong", "화성", "gyeonggi-south"), ("pyeongtaek", "평택", "gyeonggi-south"), ("goyang", "고양", "gyeonggi-north"),
        ("paju", "파주", "gyeonggi-north"), ("gimpo", "김포", "gyeonggi-north"), ("changwon", "창원", "busan-gyeongnam"), ("gimhae", "김해", "busan-gyeongnam"),
        ("jeonju", "전주", "jeonbuk"), ("pohang", "포항", "daegu-gyeongbuk"), ("gumi", "구미", "daegu-gyeongbuk"), ("wonju", "원주", "gangwon"),
        ("chuncheon", "춘천", "gangwon"), ("gangneung", "강릉", "gangwon"), ("chungju", "충주", "chungbuk"), ("seosan", "서산", "chungnam"),
        ("dangjin", "당진", "chungnam"), ("asan", "아산", "chungnam"), ("jeju", "제주", "jeju"), ("yeosu", "여수", "gwangju-jeonnam"),
        ("suncheon", "순천", "gwangju-jeonnam"), ("gunsan", "군산", "jeonbuk")]


def gen_city(page, E, CTA, faqslide, TEL, ptab, top=None, vsplit=None):
    tel = TEL.replace("-", "")
    try:
        import nation as _N
        RN = {r[0]: r[1] for r in _N.REG}
    except Exception:
        RN = {}
    for slug, nm, rg in CITY:
        jeju = rg == "jeju"
        how = "화물 배편" if jeju else "용달(화물차)"
        import os as _os, glob as _gl
        from urllib.parse import quote as _q
        _ad = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "apt")
        _ap = []
        for _f in sorted(_gl.glob(_os.path.join(_ad, "*", "*.html"))):
            _b = _os.path.basename(_f)[:-5]
            if "-" in _b or _b == "index": continue
            if _b.startswith(nm): _ap.append((_b, "/apt/" + _os.path.basename(_os.path.dirname(_f)) + "/" + _q(_b) + ".html"))
        _sd = {"서울": "seoul", "부산": "busan", "인천": "incheon", "대구": "daegu", "광주": "gwangju", "울산": "ulsan", "제주": "jeju"}.get(nm)
        _aps = ""
        if _ap or _sd:
            _aps = '<h2 class="gt">' + E(nm) + ' 아파트별 인테리어 자재</h2><div class="qk">' + (f'<a href="/apt/{_sd}/">{E(nm)} 전체 아파트</a>' if _sd else "") + "".join(f'<a href="{u}">{E(t)}</a>' for t, u in _ap[:12]) + '</div>'
        _vs = top(lambda v: nm in v["title"], 4) if top else []
        _vsec = (f'<section class="wrap sec"><h2>{E(nm)} 현장 영상</h2>{vsplit(_vs, "h3")}</section>') if (_vs and vsplit) else ""
        fq = [(f"{nm}에 매장이 있나요?", f"매장은 대전 유성대로 44 한 곳(3000평)입니다. {nm} 현장에는 대전에서 원하는 크기로 재단해 {how}로 보내 드립니다."),
              (f"{nm} 현장까지 운임은 얼마인가요?", "정해진 금액이 없고 거리·차량·수량에 따라 달라 주문 전에 먼저 견적을 드립니다. 품목을 한 번에 모으면 운임 부담이 줄어듭니다."),
              ("실물을 보고 고를 수 있나요?", "대전 매장에 오시면 큰 판 실물을 보실 수 있고, 유튜브 '월드건축자재DIY'와 홈페이지 공간 사진·쇼룸 사진으로 미리 보실 수 있습니다. 필요하면 사진으로 실물 상태를 보내 드립니다."),
              ("업체 회원가가 있나요?", "사업자등록증·명함 확인 후 도매회원(wwood.kr)으로 가입하시면 회원가로 거래합니다.")]
        body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/franchise/">체인점 인테리어 자재</a> › 도시별 › {E(nm)}</p>'
                f'<h1>{E(nm)} 인테리어 자재 — 대전 3000평 매장에서 재단해 {E(nm)} 현장으로</h1>'
                f'<p class="glead">{E(nm)}에서 상가·매장·사무실 인테리어 공사를 하는 업체와 현장에, 석고보드·각재·합판·MDF·몰딩·필름·흡음재를 대전 유성 영진종합목재(월드건축자재) 3000평 매장에서 원하는 크기로 재단해 {how}로 보내 드립니다. {E(nm)} 현지 매장은 없고, 대전 한 곳에서 출고합니다.</p>'
                f'<div class="row"><a class="b r" href="/franchise/balju.html">자재 발주서 쓰기</a><a class="b d" href="tel:{tel}">전화 {TEL}</a><a class="b o" href="/cut.html">재단표 만들기</a></div>'
                f'<h2 class="gt">이렇게 받습니다</h2><ol class="gtip"><li>발주서나 전화로 품목·규격·수량·재단 크기·{E(nm)} 현장 주소를 알려 주세요.</li><li>자재값과 {E(nm)}까지 운임을 먼저 알려 드립니다.</li><li>입금 확인 후 재단·상차해 출고합니다.</li></ol>'
                f'<h2 class="gt">자주 쓰는 자재 기준가</h2>{ptab}<p class="gs">매장 소매 기준가(부가세 별도) · 운임 별도</p>'
                f'<h2 class="gt">업종별·공정별 자재</h2><div class="qk">' + "".join(f'<a href="/franchise/{b[0]}.html">{E(b[1])}</a>' for b in BIZ[:16]) + "".join(f'<a href="/franchise/g-{g[0]}.html">{E(g[1])}</a>' for g in GJ[:6]) + '<a href="/qna/interior-jajae-bolsu-inneun-got.html">자재 실물 볼 수 있는 곳</a><a href="/qna/interior-jajae-hoesa.html">자재 거래처 고르기</a></div>'
                + _aps
                + (f'<p class="small"><a href="/franchise/r-{rg}.html">{E(RN.get(rg, ""))} 체인점 자재 배송</a> · <a href="/jeonguk/{rg}.html">{E(RN.get(rg, ""))} 목재 배송 안내</a></p>' if rg in RN else "") + '</section>'
                + f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{faqslide(fq)}</section>'
                + _vsec
                + '<section class="wrap sec"><p class="small">다른 도시: ' + " · ".join(f'<a href="/franchise/c-{c[0]}.html">{E(c[1])}</a>' for c in CITY if c[0] != slug) + '</p></section>' + CTA)
        ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}
        page(f"franchise/c-{slug}.html", f"{nm} 인테리어 자재 — 석고보드·각재·합판 재단해 {nm} 현장 배송 | 대전 영진목재",
             f"{nm} 상가·매장 인테리어 업체용 석고보드·각재·합판·MDF·몰딩·필름. 대전 3000평 매장에서 재단해 {nm} 현장까지 {how} 배송(운임 견적). {TEL}", body, "", ld)

# 사장님 지시(2026-11-28 19:00 "많이 대량"): 업종 26개·공정 4개·도시 40개 추가
def _b(slug, nm, alias, work, mats, tips, links): return (slug, nm, alias, work, mats, tips, links)
BIZ += [
 _b("sashimi", "횟집·수산물 식당", "횟집·해산물·수산 식당", "수족관 주변 방수·배수 마감, 주방 벽·바닥, 좌식·룸 칸막이", ["tile", "jipseong", "gypsum"], ["수족관·물청소 구역은 바닥 경사와 배수, 방수 마감을 먼저 잡습니다.", "좌식 룸은 단을 올려 합판·마루로 덮고 미닫이로 나눕니다."], [("/qna/maejang-badak-mulmagi.html", "매장 바닥 물 막기"), ("/qna/junsik-ilsik-interior.html", "룸·칸막이"), ("/qna/bangsu-seokgo.html", "방수 석고보드")]),
 _b("jokbal", "족발·보쌈", "족발·보쌈·배달 겸 매장", "주방 위생 마감, 포장대, 홀 테이블·칸막이", ["tile", "jipseong", "stain"], ["배달 비중이 크면 포장대와 픽업 동선을 입구 쪽에 둡니다.", "홀 테이블은 우레탄 코팅으로 기름 자국을 막습니다."], [("/qna/pizza-baedal-interior.html", "배달 위주 매장"), ("/qna/sikdang-table-sangpan.html", "식당 테이블 상판"), ("/qna/urethane-coating.html", "우레탄 코팅")]),
 _b("shabu", "샤브샤브·뷔페", "샤브샤브·한식뷔페·샐러드바", "샐러드바·배식대 목공, 테이블 인덕션 배선, 칸막이", ["jipseong", "tile", "gypsum"], ["테이블마다 인덕션이 들어가면 배선 경로를 바닥·벽으로 먼저 잡습니다.", "샐러드바 앞면은 오염에 강한 마감으로 합니다."], [("/qna/sikdang-table-sangpan.html", "식당 테이블 상판"), ("/qna/sikdang-kanmagi.html", "식당 칸막이"), ("/qna/maejang-banbok-jaedan.html", "같은 규격 반복 재단")]),
 _b("roastery", "로스터리 카페", "원두 로스팅 카페·원두 판매", "로스터 주변 환기·내열 마감, 원두 진열 선반, 바 카운터", ["jipseong", "tile", "gypsum"], ["로스터 주변은 열과 연기 배출을 먼저 계획하고 내열 마감을 씁니다.", "원두 진열 선반은 벽 하지에 단단히 고정합니다."], [("/qna/takeout-coffee-interior.html", "카운터 중심 커피 매장"), ("/qna/cafe-byeok-interior.html", "카페 벽면"), ("/qna/byeok-seonban-gojeong.html", "벽 선반 고정")]),
 _b("gift", "소품샵·선물가게", "소품샵·문구 소품·편집숍", "벽면 진열 선반, 가운데 진열 테이블, 포토존 벽", ["jipseong", "mdf", "film"], ["작은 상품이 많으니 칸이 촘촘한 벽면 선반을 짭니다.", "사진 찍기 좋은 벽 한 면을 만들면 손님이 늘어납니다."], [("/qna/munggu-interior.html", "진열 선반·통로"), ("/qna/dessert-cafe-interior.html", "포토존 벽"), ("/qna/maejang-jinyeoldae-jejak.html", "진열대 제작")]),
 _b("bookstore", "서점·독립서점", "동네 서점·독립서점·북카페", "벽면 책장, 평대(진열 테이블), 열람 공간", ["jipseong", "hapan"], ["책 무게로 선반이 처지지 않게 두께와 받침 간격을 넉넉히 잡습니다.", "평대는 낮고 넓게 만들어 표지가 잘 보이게 합니다."], [("/qna/manhwa-cafe-interior.html", "책장·좌식 공간"), ("/qna/seonban-cheojim.html", "선반 처짐"), ("/qna/geosil-byeok-sunapjang.html", "벽면 책장")]),
 _b("toy", "장난감·완구점", "완구점·키덜트 숍·피규어 매장", "진열장·쇼케이스, 벽면 선반, 체험 테이블", ["jipseong", "mdf", "molding"], ["아이 손이 닿는 진열대는 모서리를 둥글게 다듬습니다.", "유리 쇼케이스 주변은 조명 자리를 미리 냅니다."], [("/qna/jinyeoljang-led.html", "진열장 LED"), ("/qna/kidscafe-interior.html", "아이 안전 자재"), ("/qna/maejang-jinyeoldae-jejak.html", "진열대 제작")]),
 _b("yoga", "요가원", "요가·명상 스튜디오", "마루 바닥, 벽 루바·간접 조명, 매트 수납장, 탈의실", ["maru", "hinoki", "gypsum", "jipseong"], ["맨발로 쓰는 공간이라 따뜻하고 미끄럽지 않은 바닥을 씁니다.", "매트·소도구 수납장을 벽면에 짜 넣으면 공간이 넓어 보입니다."], [("/qna/taekwondo-interior.html", "운동 공간 바닥"), ("/qna/fitting-room-jejak.html", "탈의실 만들기"), ("/qna/wood-louver.html", "우드 루버")]),
 _b("tattoo", "타투샵", "타투·반영구 스튜디오", "시술 룸 가벽, 위생 마감 벽·바닥, 조명", ["gypsum", "tile", "film"], ["시술 공간은 소독제로 닦아도 상하지 않는 마감을 씁니다.", "룸 사이는 가벽으로 나눠 사생활을 지킵니다."], [("/qna/pibu-gwanrisil-interior.html", "관리룸 가벽"), ("/qna/seokgo-kanmagi.html", "석고 칸막이"), ("/qna/samusil-badakjae-jongryu.html", "닦기 쉬운 바닥재")]),
 _b("partyroom", "파티룸", "파티룸·공간 대여·홈파티 스튜디오", "포토존 벽, 바 테이블, 소파 단, 방음", ["jipseong", "sound", "film", "hinoki"], ["밤 늦게까지 쓰는 공간이라 벽·천장 방음을 챙깁니다.", "사진이 잘 나오는 포토존 벽과 조명을 함께 계획합니다."], [("/qna/cafe-byeok-interior.html", "포인트 벽"), ("/qna/cafe-soeum-julgi.html", "울림 줄이기"), ("/qna/bar-uija-nopi.html", "바 의자 높이")]),
 _b("practiceroom", "합주실·연습실", "밴드 합주실·개인 연습실 대여", "룸 이중 벽 방음, 흡음 마감, 방음문", ["gypsum", "sound", "insul", "door"], ["룸마다 벽을 이중으로 세우고 사이에 흡음재를 채웁니다.", "문·환기구 틈이 소리 새는 주 원인이니 꼼꼼히 막습니다."], [("/qna/eumak-hagwon-interior.html", "연습실 방음"), ("/qna/bangeum-gabyeok.html", "방음 가벽"), ("/qna/bangeum-mun.html", "방음 문")]),
 _b("recording", "녹음실·스튜디오", "녹음실·보컬 부스·음향 스튜디오", "부스 방음 벽, 흡음·확산 패널, 문·창 차음", ["gypsum", "sound", "insul"], ["녹음 부스는 벽·바닥·천장을 띄워 진동이 덜 전해지게 계획합니다.", "흡음재 배치는 장비·용도에 맞춰 음향 업체와 상의합니다."], [("/qna/bangeum-booth.html", "방음부스"), ("/qna/chaeum-seokgo.html", "차음 석고보드"), ("/qna/heubeumjae-jongryu.html", "흡음재 종류")]),
 _b("studio1", "1인 방송 스튜디오", "유튜브·라이브커머스 촬영 스튜디오", "배경 벽, 흡음 처리, 조명·배선 정리, 가벽", ["gypsum", "sound", "film", "hinoki"], ["말소리 울림을 줄이려면 벽 일부에 흡음 패널을 붙입니다.", "배경 벽은 조명에 얼룩이 보이지 않게 고르게 마감합니다."], [("/qna/selfphoto-interior.html", "촬영 배경벽"), ("/qna/cafe-soeum-julgi.html", "울림 줄이기"), ("/qna/wood-louver.html", "우드 루버 배경")]),
 _b("lighting", "조명·가구 매장", "조명 매장·가구 쇼룸·리빙숍", "천장 조명 걸이 하지, 쇼룸 가벽·연출 공간, 진열대", ["gypsum", "gujo", "jipseong"], ["천장에 조명을 많이 다니 천장 하지를 보강합니다.", "가벽으로 거실·방처럼 연출 공간을 나눕니다."], [("/qna/cheonjang-seokgo-anka.html", "천장 앙카"), ("/qna/samusil-gabyeok-self.html", "가벽 세우기"), ("/qna/otgage-interior.html", "쇼룸 진열")]),
 _b("cooking", "쿠킹클래스", "쿠킹 스튜디오·베이킹 클래스", "작업대(아일랜드) 상판, 주방 벽·바닥, 수납장", ["jipseong", "tile", "hardware"], ["여러 명이 함께 쓰는 아일랜드 작업대는 넓고 튼튼하게 만듭니다.", "주방 벽·바닥은 물·기름에 강한 마감으로 합니다."], [("/qna/island-siktak-jejak.html", "아일랜드 작업대"), ("/qna/jubang-sangpan-gyoche.html", "주방 상판"), ("/qna/jubang-byeok-sunapjang.html", "주방 벽 수납")]),
 _b("pottery", "도자기 공방", "도예 공방·물레 클래스", "작업대, 선반(작품 건조대), 물 쓰는 구역 마감", ["jipseong", "gujo", "tile"], ["작품 건조 선반은 무게를 버티게 두껍게 짜고 벽에 고정합니다.", "흙물을 씻는 구역은 물에 강한 마감과 배수를 챙깁니다."], [("/qna/changgo-seonban.html", "튼튼한 선반"), ("/qna/table-sangpan-jejak.html", "작업대 상판"), ("/qna/maejang-badak-mulmagi.html", "바닥 물 막기")]),
 _b("woodshop", "목공방", "목공 공방·DIY 공방·가구 공방", "작업대, 공구 벽(타공판), 집진·전기, 자재 랙", ["gujo", "hapan", "hardware"], ["공구 소음·먼지가 많아 집진과 방음, 전기 용량을 먼저 챙깁니다.", "자재 랙은 구조목으로 튼튼하게 짜서 긴 자재를 눕혀 둡니다."], [("/qna/gabyeok-tagongpan.html", "타공판 공구 벽"), ("/qna/mokgong-gongu-gicho.html", "목공 기초 도구"), ("/qna/sanding-meonji.html", "샌딩 먼지")]),
 _b("eyelash", "속눈썹·왁싱샵", "속눈썹 연장·왁싱·반영구", "시술 베드 룸 가벽, 위생 마감, 간접 조명", ["gypsum", "film", "door"], ["시술 룸은 작아도 가벽과 미닫이로 사생활을 지킵니다.", "조명은 시술 부위가 잘 보이게 밝게, 대기 공간은 은은하게 합니다."], [("/qna/pibu-gwanrisil-interior.html", "관리룸 가벽"), ("/qna/sikdang-kanmagi-mun.html", "미닫이문 달기"), ("/qna/nailshop-interior.html", "네일샵 인테리어")]),
 _b("gosiwon", "고시원·원룸텔", "고시원·원룸텔·미니룸", "방 칸막이 가벽 방음, 붙박이 책상·수납, 문", ["gypsum", "sound", "jipseong", "door"], ["방이 붙어 있어 칸막이 벽 방음이 가장 중요합니다.", "작은 방은 붙박이 책상·선반으로 공간을 아낍니다."], [("/qna/seokgo-kanmagi.html", "석고 칸막이"), ("/qna/bangeum-gabyeok.html", "방음 가벽"), ("/qna/jobeun-aibang.html", "좁은 방 가구 배치")]),
 _b("sharehouse", "셰어하우스", "셰어하우스·코리빙", "공용 주방·거실 마감, 방 문·잠금, 개인 수납", ["jipseong", "door", "tile"], ["공용 주방 상판·벽은 여러 명이 써도 상하지 않게 마감합니다.", "방마다 잠금 장치와 개인 수납을 넣습니다."], [("/qna/jubang-sangpan-gyoche.html", "주방 상판"), ("/qna/anbang-butbakijang-gusung.html", "붙박이 수납"), ("/qna/bangmun-doorlock.html", "방문 잠금")]),
 _b("motel", "모텔·호텔 객실", "모텔·호텔·비즈니스호텔 객실 리모델링", "객실 벽·천장 마감, 붙박이 가구, 욕실, 방음", ["gypsum", "film", "jipseong", "sound"], ["객실 사이 벽은 흡음재를 채워 옆방 소리를 줄입니다.", "여러 객실을 같은 규격으로 하면 자재를 한 번에 재단해 공사가 빠릅니다."], [("/qna/pension-self-interior.html", "숙박 공간 셀프 인테리어"), ("/qna/maejang-banbok-jaedan.html", "같은 규격 반복 재단"), ("/qna/bangyeom-tteut.html", "방염 뜻")]),
 _b("storage", "셀프 스토리지", "창고 대여·보관 공간", "칸막이 벽, 선반 랙, 문·잠금", ["gujo", "hapan", "osb", "hardware"], ["칸막이는 구조목 틀 + 합판·OSB로 튼튼하게 만듭니다.", "습기가 차지 않게 환기와 바닥 방습을 챙깁니다."], [("/qna/changgo-seonban.html", "창고 선반"), ("/qna/changgo-seupgi.html", "창고 습기"), ("/qna/osb-magam.html", "OSB 마감")]),
 _b("kidshair", "키즈 미용실", "어린이 미용실·키즈 헤어", "놀이형 의자 주변 목공, 대기 놀이 공간, 안전 마감", ["jipseong", "molding", "stain"], ["아이가 기다리는 공간은 모서리를 둥글게 하고 가구를 벽에 고정합니다.", "머리카락 청소가 쉬운 바닥을 씁니다."], [("/qna/kidscafe-interior.html", "아이 안전 자재"), ("/qna/small-salon-interior.html", "작은 미용실"), ("/qna/eorinijip-interior.html", "안전한 마감재")]),
 _b("bridal", "웨딩·드레스샵", "웨딩드레스·턱시도·한복 대여", "피팅룸·무대, 드레스 진열 행거, 거울 벽, 조명", ["gypsum", "jipseong", "hardware", "molding"], ["드레스 피팅 무대는 구조목 틀 + 합판으로 튼튼하게 만듭니다.", "큰 거울과 행거는 벽 하지에 단단히 고정합니다."], [("/qna/fitting-room-jejak.html", "피팅룸 제작"), ("/qna/mudae-dansang-jejak.html", "무대·단상 제작"), ("/qna/geoul-dalgi.html", "거울 달기")]),
 _b("repairshop", "휴대폰·컴퓨터 수리점", "전자기기 수리점·사설 수리", "작업대, 부품 수납장, 상담 카운터, 배선", ["jipseong", "hardware", "film"], ["수리 작업대는 콘센트·조명을 넉넉히 두고 정전기·먼지를 관리합니다.", "작은 부품 수납은 서랍·칸을 촘촘히 짭니다."], [("/qna/phone-maejang-interior.html", "휴대폰 매장"), ("/qna/table-sangpan-jejak.html", "작업대 상판"), ("/qna/maejang-counter-nopi.html", "상담 카운터")]),
 _b("refill", "리필·제로웨이스트 매장", "리필 스테이션·친환경 생활용품점", "원목 진열 선반, 리필 디스펜서 받침대, 카운터", ["jipseong", "stain", "hapan"], ["무게가 있는 리필 용기는 튼튼한 받침대와 선반에 둡니다.", "원목 마감은 오일로 자연스럽게 하고 물 자국을 관리합니다."], [("/qna/munggu-interior.html", "진열 선반"), ("/qna/sangpan-oil-vs-urethane.html", "오일 vs 우레탄"), ("/qna/hapan-interior-cafe.html", "합판 인테리어")]),
]
GJ += [
 ("bangsu", "물 쓰는 공간 방수", "주방·화장실·세척 구역 방수 마감", ["물이 닿는 벽은 방수 석고·타일로, 바닥은 배수 경사를 먼저 잡습니다.", "바닥과 벽 모서리는 방수 처리 후 마감합니다.", "이음새와 기구 둘레는 실리콘으로 막습니다."], ["tile", "gypsum", "hardware"], [("/qna/bangsu-seokgo.html", "방수 석고보드"), ("/qna/maejang-badak-mulmagi.html", "매장 바닥 물 막기"), ("/qna/sangga-hwajangsil-naemsae.html", "배수구 트랩")]),
 ("heupeum", "흡음·소음 줄이기", "카페·식당·학원 울림 줄이기", ["소리가 오래 울리는 곳(넓은 천장·유리 맞은편 벽)을 찾습니다.", "천장 흡음판·배플, 벽 흡음 패널을 붙입니다.", "옆 공간으로 새는 소리는 가벽 속 흡음재·틈막이로 줄입니다."], ["sound", "gypsum"], [("/qna/cafe-soeum-julgi.html", "카페 소음 줄이기"), ("/qna/cheonjang-heubeumjae-self.html", "천장 흡음재"), ("/qna/heubeumjae-jongryu.html", "흡음재 종류")]),
 ("danyeol", "단열 보강", "통유리·외벽 쪽 벽·천장 단열", ["바람 새는 틈부터 막습니다.", "외벽 쪽 벽은 각재 틀 사이에 단열재를 넣고 석고보드로 덮습니다.", "천장 속·바닥 단열을 보강합니다."], ["insul", "gypsum"], [("/qna/sangga-danyeol.html", "상가 단열 방법"), ("/qna/danyeoljae-sigong-sunseo.html", "단열재 시공 순서"), ("/qna/sangga-changmun-upung.html", "창문 우풍")]),
 ("baeseon", "배선 정리·몰딩", "콘센트·전선·인터넷선 정리", ["전기 업체와 콘센트·배선 위치를 먼저 정합니다.", "벽 속·천장 속으로 넣지 못하는 선은 몰딩·덕트로 정리합니다.", "카운터·진열대에는 배선 구멍을 미리 냅니다."], ["molding", "hardware"], [("/qna/tv-seon-sumgigi.html", "배선 숨기기"), ("/qna/pcbang-interior.html", "좌석 배선"), ("/qna/arcade-interior.html", "기계 배선")]),
]
CITY += [("anyang","안양","gyeonggi-south"),("bucheon","부천","gyeonggi-south"),("ansan","안산","gyeonggi-south"),("gwangmyeong","광명","gyeonggi-south"),("siheung","시흥","gyeonggi-south"),("hanam","하남","gyeonggi-south"),("osan","오산","gyeonggi-south"),("icheon","이천","gyeonggi-south"),("anseong","안성","gyeonggi-south"),("gyeonggi-gwangju","경기 광주","gyeonggi-south"),("gunpo","군포","gyeonggi-south"),("uiwang","의왕","gyeonggi-south"),
 ("uijeongbu","의정부","gyeonggi-north"),("namyangju","남양주","gyeonggi-north"),("guri","구리","gyeonggi-north"),("yangju","양주","gyeonggi-north"),("pocheon","포천","gyeonggi-north"),
 ("jecheon","제천","chungbuk"),("eumseong","음성","chungbuk"),("jincheon","진천","chungbuk"),
 ("boryeong","보령","chungnam"),("hongseong","홍성","chungnam"),("buyeo","부여","chungnam"),("nonsan","논산","chungnam"),
 ("gyeongju","경주","daegu-gyeongbuk"),("andong","안동","daegu-gyeongbuk"),("gyeongsan","경산","daegu-gyeongbuk"),("gimcheon","김천","daegu-gyeongbuk"),
 ("jinju","진주","busan-gyeongnam"),("yangsan","양산","busan-gyeongnam"),("geoje","거제","busan-gyeongnam"),("tongyeong","통영","busan-gyeongnam"),
 ("iksan","익산","jeonbuk"),("jeongeup","정읍","jeonbuk"),
 ("mokpo","목포","gwangju-jeonnam"),("gwangyang","광양","gwangju-jeonnam"),("naju","나주","gwangju-jeonnam"),
 ("sokcho","속초","gangwon"),("donghae","동해","gangwon"),("seogwipo","서귀포","jeju")]
