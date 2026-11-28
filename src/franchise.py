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
 ("church", "교회·공방·소규모 공간", "작업실·공방", "강단·단상, 벽 흡음, 작업대",
  ["jipseong", "hapan", "sound", "gujo"],
  ["단상은 각재로 틀을 짜고 합판·마루로 덮습니다.", "울림이 큰 공간은 흡음재로 소리를 정리합니다."],
  [("/gonggan/cafe-wood-stage.html", "단상 공간 사진"), ("/mandeul/jakeopdae.html", "작업대 만들기")]),
]

PX = [("석고보드 일반 9.5T 3×6", r"석고-일반 3\*6 @ 9\.5T$"), ("방수 석고보드 9.5T 3×6", r"석고-방수 3\*6 @ 9\.5T"), ("방화 석고보드 12.5T 3×6", r"석고-방화 3\*6 @12\.5T"),
      ("MDF 9mm 4×8", r"MDF 4\*8 @ 9mm$"), ("MDF 18mm 4×8", r"MDF 4\*8 @18mm"), ("합판 12mm 내수 4×8", r"4\*8 @12mm\(내수/A급\)"),
      ("구조재 2×4 12자", r"Ⅱ 2\* 4\*12ft"), ("흡음보드 오크 라인 9T 1200×2400", r"흡음 오크 라인@9T\*1200\*2400")]

INFO = [("/qna/maejang-banbok-jaedan.html", "여러 매장 같은 규격 재단"), ("/qna/maejang-bangyeom.html", "매장 방염 자재 확인"), ("/qna/sangga-interior-jajae-list.html", "상가 인테리어 자재 목록"), ("/qna/franchise-interior-biyong-gusung.html", "인테리어 견적 항목"), ("/qna/franchise-interior-jugi.html", "프랜차이즈 리뉴얼 주기"), ("/qna/sangga-wonsang-bokgu.html", "상가 원상복구")]

JN = {"hapan": "합판", "jipseong": "집성판", "gypsum": "석고보드", "molding": "몰딩", "film": "인테리어 필름", "hinoki": "편백·루바", "mdf": "MDF", "tile": "타일",
      "gujo": "구조재·각재", "maru": "마루", "sound": "흡음·방음재", "hardware": "철물·부속", "insul": "단열재", "door": "도어·문틀", "bangbu": "방부목", "hapdeck": "합성목 데크", "stain": "스테인·오일"}


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
    out = []
    for slug, nm, alias, work, mats, tips, links in BIZ:
        mlinks = "".join(f'<a href="/jajae/{m}.html">{E(JN.get(m, m))}</a>' for m in mats)
        ilinks = "".join(f'<a href="{u}">{E(t)}</a>' for u, t in links)
        mail = "mailto:" + EMAIL + "?subject=" + quote(f"{nm} 매장 인테리어 자재 견적 요청") + "&body=" + quote("업체명·담당자:\n현장 주소:\n품목·규격·수량:\n재단 크기(있으면):\n희망 입고일:\n")
        fq = [(f"{nm} 인테리어에 많이 쓰는 자재는 무엇인가요?", f"{nm} 매장은 주로 {work} 공사를 합니다. 그래서 {', '.join(JN.get(m, m) for m in mats)}를 많이 씁니다.")] + common_fq
        body = (f'<section class="wrap sec gg"><p class="crumb"><a href="/franchise/">체인점 인테리어 자재</a> › {E(nm)}</p>'
                f'<h1>{E(nm)} 인테리어 자재 — 프랜차이즈·체인점 매장 공사 업체용 재단·현장 배송</h1>'
                f'<p class="glead">{E(nm)}({E(alias)}) 매장 인테리어 공사에 들어가는 합판·MDF·석고보드·각재·몰딩·필름·루바·흡음재를 대전 유성 영진종합목재(월드건축자재) 3000평 매장에서 원하는 크기로 재단해 전국 현장으로 보내 드립니다. 같은 규격 매장을 여러 곳 하는 체인점 공사는 재단표 하나로 반복 납품하기 좋습니다.</p>'
                f'<div class="row"><a class="b r" href="{mail}">메일로 자재 견적 요청</a><a class="b d" href="tel:{tel}">전화 {TEL}</a><a class="b o" href="/cut.html">재단표 만들기</a></div>'
                f'<h2 class="gt">{E(nm)} 매장에서 주로 하는 공사</h2><p>{E(work)}</p>'
                f'<h2 class="gt">많이 쓰는 자재</h2><div class="qk">{mlinks}</div>'
                f'<h2 class="gt">공사할 때 챙길 것</h2><ul class="gtip">' + "".join(f"<li>{E(t)}</li>" for t in tips) + '<li>다중이용시설은 방염·불연 기준이 적용될 수 있으니 자재 성능을 미리 확인합니다.</li></ul>'
                f'<h2 class="gt">자주 쓰는 자재 기준가</h2>{ptab}<p class="gs">매장 소매 기준가(부가세 별도) · 운임 별도 · 사업자는 도매회원(wwood.kr) 가입 후 회원가. <a href="/price.html">전체 기준가</a></p>'
                f'<h2 class="gt">납품 순서</h2><ol class="gtip"><li>도면·재단표나 품목·규격·수량을 전화·메일로 보내 주세요.</li><li>자재값과 현장까지 운임을 먼저 알려 드립니다.</li><li>입금 확인 후 재단·상차해 현장으로 출고합니다.</li><li>같은 매장 규격이면 다음 현장부터 재단표를 그대로 씁니다.</li></ol>'
                f'<h2 class="gt">관련 정보</h2><div class="qk">{ilinks}' + "".join(f'<a href="{u}">{E(t)}</a>' for u, t in INFO) + '<a href="/gonggan/">공간 사진</a><a href="/sigongbeop/">자재 시공법</a><a href="/calc.html">자재 계산기</a></div></section>'
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
                f'<h2 class="gt">자주 쓰는 자재 기준가</h2>{ptab}<p class="gs">소매 기준가(부가세 별도) · 운임 별도</p></section>'
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
         + '<h2 class="gt">업체가 자주 찾는 정보</h2><div class="qk">' + "".join(f'<a href="{u}">{E(t)}</a>' for u, t in INFO) + '</div>'
         + f'<h2 class="gt">자주 쓰는 자재 기준가</h2>{ptab}<p class="gs">매장 소매 기준가(부가세 별도) · 운임 별도 · 사업자는 도매회원 가입 후 회원가</p></section>'
         f'<section class="wrap sec gg"><h2 class="gt">자주 묻는 질문</h2>{faqslide(fq)}</section>{CTA}', "", ld)
    return out
