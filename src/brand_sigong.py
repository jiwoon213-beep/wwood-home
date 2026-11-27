# 회사별 자재 시공법 — /sigongbeop/brand.html, /sigongbeop/brand-<key>.html, /sigongbeop/b-<slug>.html
# 제품 사진·이름은 각 제조사 데이터(회사 허락)로 만든 우리 제품 페이지에서 가져옴. 시공 순서는 일반적인 순서(제조사 공식 지침 아님).
import os, re, json, html as _h

DATE = "2026-11-27"
BR = [  # key, 화면 이름, 제품 폴더, 한 줄
    ("younglim", "영림", "younglim", "중문·방문·문틀·인테리어 필름·몰딩·마루·월패널"),
    ("yerim", "예림", "yerim", "슬라이딩·폴딩·간살 중문, ABS 도어, 문틀"),
    ("shenu", "쉐누", "shenu", "도어·중문·몰딩"),
    ("bondex", "본덱스", "bondex", "오일스테인·수성 페인트·스프레이"),
    ("nichiha", "니치하", "nichiha", "세라믹 사이딩 외벽"),
    ("taka", "제일타카", "taka", "실타카·프레이밍 타카·콘크리트 타카"),
]
# slug, brand key, 이름, 제품 고를 페이지들, 이름 거르기(정규식), 일반 시공법 slug, 리드, 순서, 준비물, 주의, FAQ
G = [
 ("yl-jungmun-3yeondong", "younglim", "영림 3연동 중문 설치 순서", ["younglim/jungmun-system.html", "younglim/jungmun-slim.html", "younglim/jungmun-all.html"], r"연동", "jungmun",
  "영림 3연동 중문처럼 문 세 짝이 한쪽으로 겹쳐 열리는 슬라이딩 중문을 다는 일반적인 순서입니다. 실측이 가장 중요하고, 상부 레일이 수평이어야 문이 저절로 밀리지 않습니다.",
  ["현관 폭·높이를 위·가운데·아래 세 곳씩 재고 가장 작은 값을 기준으로 주문합니다.", "바닥·벽·천장의 수평·수직을 확인하고 틀어진 만큼 문틀 쪽에 보정 여유를 둡니다.", "문틀(상부 레일·측면 틀)을 세우고 수평기로 맞춘 뒤 피스·앙카로 고정합니다.", "문짝을 레일에 걸고 연동 줄(벨트)과 롤러 높이를 조절해 세 짝이 같이 움직이게 맞춥니다.", "하부 가이드·스토퍼를 달고 여닫기를 여러 번 해 보며 걸리는 곳을 조절합니다.", "틈은 실리콘·몰딩으로 마감합니다."],
  ["줄자·수평기", "전동드릴·콘크리트 날", "앙카·피스", "실리콘·실리콘건"], ["유리 문짝은 무거워 두 사람이 다룹니다.", "주문 전 제품별 설치 공간(옆 벽 폭·천장 높이)을 꼭 확인합니다."],
  [("3연동 중문 셀프 설치 되나요?", "실측과 수평 잡기가 정확하면 가능하지만, 문짝이 무겁고 조절이 까다로워 처음이면 시공을 맡기는 경우가 많습니다."), ("3연동은 몇 cm 폭부터 되나요?", "제품마다 달라 해당 제품의 규격표를 확인합니다. 매장에서 실측 치수를 알려 주시면 맞는 제품을 찾아 드립니다.")]),
 ("yl-jungmun-yanggae", "younglim", "영림 양개 중문 설치 순서", ["younglim/jungmun-yanggae.html"], r"", "jungmun",
  "가운데서 양쪽으로 여는 양개 중문을 다는 일반적인 순서입니다. 두 짝이 가운데서 딱 맞아야 해서 문틀 수직이 특히 중요합니다.",
  ["현관 폭·높이와 문이 열리는 쪽 공간(신발장·벽과의 거리)을 잽니다.", "문틀을 세워 수직·수평을 맞추고 고정합니다.", "경첩으로 문짝 두 짝을 달고 가운데 틈이 위아래 같게 조절합니다.", "도어 클로저·자석·잠금 장치를 달고 여닫기를 확인합니다.", "틈을 실리콘·몰딩으로 마감합니다."],
  ["줄자·수평기", "전동드릴", "앙카·피스", "실리콘"], ["문이 열리는 반경 안에 신발장 문·센서등이 걸리지 않는지 먼저 봅니다."],
  [("양개 중문과 3연동 차이는?", "양개는 가운데서 양쪽으로 여닫고, 3연동은 세 짝이 옆으로 밀립니다(/bigyo/yanggae-vs-3yeondong.html).")]),
 ("yl-bangmun-gyoche", "younglim", "영림 ABS 방문 교체 순서", ["younglim/door-abs.html", "younglim/door-membrane.html"], r"", "munteul-gyoche",
  "기존 문틀은 두고 영림 ABS·멤브레인 방문처럼 문짝만 바꾸는 일반적인 순서입니다. 문틀 안쪽 치수와 경첩 위치를 맞추는 것이 핵심입니다.",
  ["기존 문틀 안쪽 폭·높이와 문 두께, 경첩 위치·개수를 잽니다.", "치수에 맞는 문짝을 주문합니다(손잡이 방향·타공 여부 확인).", "기존 문짝의 경첩 핀이나 피스를 풀어 떼어 냅니다.", "새 문짝에 경첩 자리를 맞춰 달고, 문틀과의 틈을 위아래 같게 조절합니다.", "손잡이·도어락을 달고 걸쇠 자리를 맞춥니다."],
  ["줄자", "전동드릴·드라이버", "경첩·피스", "끌(경첩 자리 조정용)"], ["ABS 문은 물에 강한 편이지만 욕실 안쪽처럼 물이 직접 닿는 곳은 제품 용도를 확인합니다."],
  [("문틀은 두고 문만 바꿀 수 있나요?", "네. 문틀 상태가 괜찮으면 문짝만 교체할 수 있습니다. 문틀 안쪽 치수를 정확히 재세요(/qna/door-silcheuk.html).")]),
 ("yl-munteul", "younglim", "영림 문틀 교체 순서", ["younglim/door-frame.html"], r"", "munteul-gyoche",
  "영림 문틀처럼 문틀째 새로 바꾸는 일반적인 순서입니다. 벽 구멍 크기에 맞춰 문틀을 고르고, 수직을 잡은 뒤 폼으로 고정합니다.",
  ["기존 문선·문틀을 떼어 내고 벽 구멍(개구부) 크기를 잽니다.", "벽 두께에 맞는 문틀 폭을 고릅니다.", "문틀을 세우고 쐐기로 수평·수직을 맞춥니다.", "피스로 고정하고 틈을 우레탄폼으로 채웁니다.", "폼이 굳으면 튀어나온 부분을 자르고 문선을 붙입니다.", "문짝을 달고 틈을 조절합니다."],
  ["수평기·직각자", "전동드릴", "쐐기·피스", "우레탄폼·폼건", "실타카(문선)"], ["폼을 많이 쏘면 부풀며 문틀이 휘니 틈의 절반 정도만 채웁니다."],
  [("문틀 교체 후 벽 마감은?", "문선으로 틈을 덮고, 벽이 깨진 곳은 퍼티로 메워 칠·도배합니다.")]),
 ("yl-film", "younglim", "영림 인테리어 필름 붙이는 순서", ["younglim/film.html"], r"", "film-sigong",
  "영림 인테리어 필름을 문·문틀·몰딩·가구에 붙이는 일반적인 순서입니다. 바탕 정리와 프라이머가 오래가는 비결입니다.",
  ["붙일 면의 먼지·기름을 닦고 찍힌 곳은 퍼티로 메웁니다.", "사포로 가볍게 갈아 면을 고르고 먼지를 닦습니다.", "프라이머를 얇게 바르고 마를 때까지 기다립니다.", "필름을 넉넉히 자르고 이형지를 조금씩 떼며 밀대로 가운데서 밖으로 밀어 붙입니다.", "모서리는 열(드라이기)을 살짝 주며 감싸고 남는 부분은 칼로 잘라 냅니다."],
  ["사포·퍼티", "프라이머·붓", "밀대(스퀴지)", "커터칼", "드라이기"], ["바탕이 젖었거나 추운 곳에서는 접착이 약해 들뜰 수 있습니다."],
  [("필름 기포는 어떻게 빼나요?", "바늘로 아주 작게 구멍을 내고 밀대로 공기를 밀어냅니다(/qna/film-gipo.html).")]),
 ("yl-molding", "younglim", "영림 몰딩·걸레받이 시공 순서", ["younglim/molding.html"], r"", "molding-georebatgi",
  "영림 천장 몰딩·걸레받이를 다는 일반적인 순서입니다. 모서리를 45도로 정확히 자르는 것이 깔끔한 마감의 비결입니다.",
  ["벽 길이를 재고 이음이 눈에 덜 띄는 곳으로 나눕니다.", "안쪽·바깥쪽 모서리는 각도절단기로 45도(실제 각도의 절반)로 자릅니다.", "뒷면에 본드를 바르고 실타카로 고정합니다.", "이음·모서리 틈은 몰딩용 실리콘·퍼티로 메웁니다."],
  ["각도절단기·톱", "실타카·실핀", "몰딩 본드", "실리콘"], ["벽 모서리가 직각이 아닌 경우가 많아 실제 각도를 재서 반으로 나눠 자릅니다."],
  [("걸레받이 떼는 법은?", "헤라를 틈에 넣어 살살 벌리며 뗍니다(/qna/georebatgi-ppaegi.html).")]),
 ("yl-maru", "younglim", "영림 마루 시공 순서", ["younglim/maru.html"], r"", "gangmaru",
  "영림 마루를 까는 일반적인 순서입니다. 접착식(강마루류)과 끼움식(강화마루·SPC류)은 방법이 달라 제품 종류를 먼저 확인합니다.",
  ["바닥의 높낮이를 보고 튀어나온 곳은 갈고 꺼진 곳은 메워 평평하게 합니다.", "바닥을 깨끗이 청소하고 습기를 확인합니다.", "빛이 들어오는 방향으로 첫 줄을 정하고 벽과 신축 여유를 둡니다.", "접착식은 본드를 펴 바르고, 끼움식은 판을 끼워 맞추며 깝니다.", "걸레받이로 가장자리를 덮어 마감합니다."],
  ["수평 몰탈·그라인더(평탄)", "마루 본드·빗살 헤라(접착식)", "고무망치·당김쇠", "톱"], ["바탕 습기가 많으면 들뜸이 생깁니다."],
  [("강마루와 강화마루 차이는?", "강마루는 접착해 깔고, 강화마루는 끼워 띄워 깝니다(/bigyo/kangmaru-vs-kanghwa.html).")]),
 ("yl-wall", "younglim", "영림 월패널 붙이는 순서", ["younglim/wall.html"], r"", "tempa-byeok",
  "영림 월패널(벽 마감 판)을 벽에 붙이는 일반적인 순서입니다. 벽이 고르지 않으면 각재 하지를 먼저 대고 붙입니다.",
  ["벽의 수직·평탄을 확인하고, 고르지 않으면 각재로 하지틀을 댑니다.", "콘센트·스위치 위치를 표시하고 판에 구멍을 따 둡니다.", "첫 장을 수직으로 맞춰 본드와 실타카(또는 피스)로 고정합니다.", "판을 끼워 맞추며 이어 붙입니다.", "끝과 모서리는 마감재(몰딩)로 덮습니다."],
  ["수평기·레이저 레벨", "실타카", "패널 본드", "직소·톱"], ["실크 벽지 위에는 접착이 약해 벽지를 뜯거나 하지틀에 고정합니다."],
  [("벽지 위에 패널 붙여도 되나요?", "합지는 붙기도 하지만 실크 벽지는 접착이 약해 뜯고 붙이거나 하지틀에 고정합니다.")]),
 ("yr-jungmun-sliding", "yerim", "예림 슬라이딩 중문 설치 순서", ["yerim/jungmun-sliding.html", "yerim/jungmun-slim.html"], r"", "jungmun",
  "예림 슬라이딩 중문(원슬라이딩·연동)을 다는 일반적인 순서입니다. 상부 레일 수평과 문이 밀려 들어갈 옆 벽 공간이 핵심입니다.",
  ["현관 폭·높이를 세 곳씩 재고 문이 밀려 들어갈 옆 벽 폭을 확인합니다.", "상부 레일(틀)을 수평기로 맞춰 고정합니다.", "문짝을 걸고 롤러 높이를 조절해 수직을 맞춥니다.", "하부 가이드와 스토퍼를 달고 여닫기를 확인합니다.", "틈을 실리콘·몰딩으로 마감합니다."],
  ["줄자·수평기", "전동드릴", "앙카·피스", "실리콘"], ["레일이 조금만 기울어도 문이 저절로 밀립니다."],
  [("원슬라이딩과 3연동 차이는?", "원슬라이딩은 큰 문 한 짝이, 3연동은 세 짝이 겹쳐 밀립니다(/bigyo/3yeondong-vs-one-sliding.html).")]),
 ("yr-jungmun-folding", "yerim", "예림 폴딩 중문 설치 순서", ["yerim/jungmun-folding.html"], r"", "jungmun",
  "예림 폴딩(접이식) 중문을 다는 일반적인 순서입니다. 문짝이 접혀 한쪽에 모이므로 접힌 두께만큼 공간을 남깁니다.",
  ["폭·높이를 재고 문이 접혀 모일 쪽 공간을 확인합니다.", "상부 레일을 수평으로 고정합니다.", "문짝을 레일에 걸고 경첩으로 연결합니다.", "피벗(회전축)과 하부 가이드를 맞춰 여닫기를 조절합니다."],
  ["줄자·수평기", "전동드릴", "앙카·피스"], ["접히는 쪽에 손가락이 끼지 않게 아이가 있는 집은 주의합니다."], []),
 ("yr-ganssal", "yerim", "예림 간살 중문 설치 순서", ["yerim/jungmun-ganssal.html"], r"", "jungmun",
  "예림 간살 중문처럼 가는 살이 들어간 중문을 다는 일반적인 순서입니다. 설치 순서는 슬라이딩·여닫이 방식에 따라 같고, 살이 상하지 않게 다루는 것이 중요합니다.",
  ["설치 방식(슬라이딩·여닫이)과 치수를 확인합니다.", "틀·레일을 수평·수직으로 고정합니다.", "문짝을 달고 틈과 움직임을 조절합니다.", "마감 후 살 사이 먼지는 부드러운 솔로 털어 냅니다."],
  ["줄자·수평기", "전동드릴", "앙카·피스"], ["살에 힘을 주어 들지 말고 문짝 틀을 잡고 옮깁니다."], []),
 ("yr-door-abs", "yerim", "예림 ABS 도어 교체 순서", ["yerim/door-abs.html", "yerim/door-ez.html"], r"", "munteul-gyoche",
  "예림 ABS 도어로 방문을 바꾸는 일반적인 순서입니다. 문틀째 바꿀지, 문짝만 바꿀지 먼저 정합니다.",
  ["문틀 안쪽 치수(문짝만) 또는 벽 구멍 치수(문틀째)를 잽니다.", "손잡이 방향·타공·문 두께를 정해 주문합니다.", "기존 문을 떼고 새 문을 경첩으로 답니다.", "틈을 조절하고 손잡이를 답니다."],
  ["줄자", "전동드릴·드라이버", "경첩·피스"], [], []),
 ("yr-door-frame", "yerim", "예림 문틀 설치 순서", ["yerim/door-frame.html"], r"", "munteul-gyoche",
  "예림 문틀을 새로 세우는 일반적인 순서입니다. 벽 두께에 맞는 폭을 고르고 쐐기로 수직을 잡은 뒤 폼으로 고정합니다.",
  ["벽 구멍 크기와 벽 두께를 잽니다.", "문틀을 세워 쐐기로 수평·수직을 맞춥니다.", "피스로 고정하고 우레탄폼으로 틈을 채웁니다.", "문선을 붙이고 문짝을 답니다."],
  ["수평기", "전동드릴", "쐐기·피스", "우레탄폼"], ["폼은 틈의 절반 정도만 채웁니다."], []),
 ("sh-door", "shenu", "쉐누 도어 교체 순서", ["shenu/door-abs.html", "shenu/door-glass.html"], r"", "munteul-gyoche",
  "쉐누 도어로 방문을 바꾸는 일반적인 순서입니다. 문틀 안쪽 치수와 경첩 위치를 맞추는 것이 핵심입니다.",
  ["문틀 안쪽 폭·높이와 경첩 위치를 잽니다.", "치수·손잡이 방향에 맞게 주문합니다.", "기존 문을 떼고 새 문을 경첩으로 답니다.", "틈과 걸쇠 자리를 조절합니다."],
  ["줄자", "전동드릴·드라이버", "경첩·피스"], ["유리가 들어간 문은 무거워 경첩 수를 확인합니다."], []),
 ("sh-jungmun", "shenu", "쉐누 중문 설치 순서", ["shenu/jungmun.html"], r"", "jungmun",
  "쉐누 중문을 다는 일반적인 순서입니다. 실측과 레일 수평이 가장 중요합니다.",
  ["현관 폭·높이를 세 곳씩 잽니다.", "틀·레일을 수평으로 고정합니다.", "문짝을 달고 움직임을 조절합니다.", "틈을 마감합니다."],
  ["줄자·수평기", "전동드릴", "앙카·피스", "실리콘"], [], []),
 ("sh-molding", "shenu", "쉐누 몰딩 시공 순서", ["shenu/molding.html"], r"", "molding-georebatgi",
  "쉐누 몰딩을 천장·벽에 다는 일반적인 순서입니다.",
  ["길이를 재서 이음 위치를 정합니다.", "모서리를 45도로 자릅니다.", "본드와 실타카로 고정합니다.", "틈을 메워 마감합니다."],
  ["각도절단기", "실타카", "몰딩 본드", "실리콘"], [], []),
 ("bd-deck-oil", "bondex", "본덱스 데크 오일스테인 칠하는 순서", ["bondex/stain.html", "bondex/oil.html"], r"", "oilstain",
  "본덱스 오일스테인·데크 오일로 방부목·데크를 칠하는 일반적인 순서입니다. 마른 날, 깨끗한 바탕에 얇게 두 번 바르는 것이 오래가는 요령입니다.",
  ["비 소식이 없는 마른 날을 고릅니다.", "먼지·곰팡이·옛 칠을 솔·사포로 벗기고 물기를 말립니다.", "잘 저어 색을 고르게 하고 자투리에 먼저 발라 색을 봅니다.", "결 방향으로 얇게 바르고 남는 것은 닦아 냅니다.", "마르면 한 번 더 바르고, 마구리(자른 면)는 꼼꼼히 먹입니다."],
  ["솔·롤러", "사포", "천(닦기용)", "장갑"], ["칠 묻은 천은 펼쳐 말려 버립니다(뭉쳐 두면 열이 날 수 있음)."],
  [("오일스테인 몇 번 바르나요?", "보통 두 번 바릅니다. 마르는 시간은 제품 설명을 따릅니다.")]),
 ("bd-paint", "bondex", "본덱스 수성 페인트 벽 칠하는 순서", ["bondex/paint.html"], r"", "seokgo-peinteu",
  "본덱스 수성 페인트로 벽·가구를 칠하는 일반적인 순서입니다. 마스킹과 젯소(바탕칠)가 결과를 좌우합니다.",
  ["바닥·몰딩·콘센트를 마스킹하고 덮습니다.", "구멍·금은 퍼티로 메우고 사포로 갑니다.", "필요하면 젯소(바탕칠)를 바릅니다.", "모서리는 붓, 넓은 면은 롤러로 얇게 칠합니다.", "마르면 두 번째 칠을 하고 마스킹은 살짝 마를 때 뗍니다."],
  ["롤러·붓·트레이", "마스킹테이프·커버링 테이프", "퍼티·사포"], ["추운 날은 잘 마르지 않으니 기온을 확인합니다."], []),
 ("bd-spray", "bondex", "본덱스 스프레이 칠하는 순서", ["bondex/spray.html"], r"", "seokgo-peinteu",
  "본덱스 스프레이(락카)로 작은 가구·철물을 칠하는 일반적인 순서입니다. 얇게 여러 번 뿌리는 것이 흘러내림을 막는 요령입니다.",
  ["바람이 잘 통하는 곳에서 바닥을 덮습니다.", "면의 기름·녹을 닦고 사포로 갑니다.", "캔을 충분히 흔들고 20~30cm 거리에서 얇게 뿌립니다.", "마르면 두세 번 더 뿌립니다."],
  ["사포", "마스킹테이프", "보호 비닐", "마스크·장갑"], ["불 가까이에서 쓰지 않습니다."], []),
 ("nc-siding", "nichiha", "니치하 세라믹 사이딩 외벽 시공 순서", ["nichiha/index.html"], r"", "ceramic-siding",
  "니치하 세라믹 사이딩으로 외벽을 마감하는 일반적인 순서입니다. 바탕 방수와 통기층 띠장, 전용 철물로 거는 방식이 핵심입니다.",
  ["외벽 바탕에 투습방수지를 아래에서 위로 겹쳐 붙입니다.", "통기층을 만들 세로 띠장을 일정 간격으로 댑니다.", "맨 아래 시작 철물을 수평으로 답니다.", "사이딩을 철물에 걸고 위 철물로 눌러 고정하며 올라갑니다.", "모서리·창 둘레는 전용 부재와 실링으로 마감합니다."],
  ["레이저 레벨", "원형톱(사이딩용 날)", "전용 철물·피스", "실링재"], ["자를 때 먼지가 많아 마스크·보안경을 쓰고, 제품별 시공 설명서를 꼭 따릅니다."],
  [("세라믹 사이딩 셀프 시공 되나요?", "무겁고 높은 곳 작업이 많아 보통 시공을 맡깁니다(/yeongyeol/).")]),
 ("tk-pin", "taka", "실타카로 몰딩·문선 박는 순서", ["taka/interior.html", "taka/battery.html"], r"", "molding-georebatgi",
  "제일타카 실타카(핀 타카)로 몰딩·문선·걸레받이를 고정하는 일반적인 순서입니다. 핀 길이를 자재 두께에 맞추는 것이 중요합니다.",
  ["자재 두께에 맞는 핀 길이를 고릅니다(뒤 바탕에 충분히 박히게).", "몰딩 뒤에 본드를 바르고 자리를 잡습니다.", "타카를 면에 수직으로 대고 일정 간격으로 쏩니다.", "핀 자국은 퍼티·몰딩 실리콘으로 메웁니다."],
  ["실타카·실핀", "콤프레샤(에어식) 또는 충전식", "몰딩 본드", "보안경"], ["손으로 받친 자리 가까이 쏘지 않습니다."],
  [("실타카와 일반 타카 차이는?", "실타카는 머리 없는 가는 핀이라 자국이 작고, 일반 타카는 ㄷ자 심으로 잡는 힘이 큽니다(/qna/taka-vs-siltaka.html).")]),
 ("tk-framing", "taka", "프레이밍 타카로 구조목 박는 순서", ["taka/framing.html"], r"", "gabyeok-sigong",
  "제일타카 프레이밍(못) 타카로 구조목·각재 틀을 짜는 일반적인 순서입니다.",
  ["부재 두께에 맞는 못 길이를 고릅니다.", "부재를 클램프·손으로 단단히 맞춥니다.", "타카를 면에 대고 정해진 간격으로 박습니다.", "못이 덜 박히면 압력·깊이 조절을 맞춥니다."],
  ["프레이밍 타카·못", "콤프레샤", "보안경·귀마개"], ["반동이 커서 두 손으로 잡고, 사람 쪽으로 겨누지 않습니다."], []),
 ("tk-concrete", "taka", "콘크리트 타카로 각재 고정하는 순서", ["taka/concrete.html"], r"", "gabyeok-sigong",
  "제일타카 콘크리트 타카로 콘크리트 바닥·벽에 각재·런너를 고정하는 일반적인 순서입니다.",
  ["콘크리트 상태(너무 단단하거나 부서지는지)를 확인합니다.", "각재·런너를 먹줄에 맞춰 놓습니다.", "타카를 수직으로 대고 일정 간격으로 박습니다.", "덜 박힌 핀은 망치로 마무리합니다."],
  ["콘크리트 타카·핀", "콤프레샤", "보안경·귀마개"], ["핀이 튈 수 있어 보안경을 꼭 씁니다. 무거운 물건은 앙카로 고정합니다."], []),
]


def _pick(ROOT, d, pages, rx, n=6):
    R = os.path.dirname(ROOT); out = []; seen = set()
    for pg in pages:
        p = os.path.join(R, pg)
        if not os.path.exists(p): continue
        for href, nm in re.findall(r'<a href="(/' + d + r'/p/[^"]+\.html)">([^<]{2,120})</a>', open(p, encoding="utf-8").read()):
            if href in seen or (rx and not re.search(rx, nm)): continue
            pp = os.path.join(R, href.lstrip("/"))
            if not os.path.exists(pp): continue
            t = open(pp, encoding="utf-8").read()
            m = re.search(r'<h1>.*?</h1>.*?<img[^>]*? src="([^"]+)"', t, re.S)
            if not m: continue
            seen.add(href); out.append((href, _h.unescape(nm.strip()), m.group(1)))
            if len(out) >= n: return out
    return out


RP = ' referrerpolicy="no-referrer"'


def gen(page, E, CTA, ROOT, SG):
    sgn = {x[0]: x[1] for x in SG}
    bn = {k: (nm, d, one) for k, nm, d, one in BR}
    cards = {k: [] for k, *_ in BR}
    for slug, bk, nm, pages, rx, gs, lead, steps, tools, warn, fq in G:
        bnm, d, _ = bn[bk]
        if d is None:
            img = _IMG.get(slug); rp = ""
            cards[bk].append(f'<a class="mc" href="/sigongbeop/b-{slug}.html">' + (f'<img loading="lazy" src="{img}" alt="" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;margin-bottom:6px">' if img else "") + f'<b>{E(nm)}</b><small>{E(lead[:42])}…</small></a>')
            continue
        prods = _pick(ROOT, d, pages, rx)
        img = prods[0][2] if prods else None
        rp = ' referrerpolicy="no-referrer"' if img and img.startswith("http") else ""
        hero = f'<figure class="mkfig"><img src="{E(img)}"{rp} alt="{E(prods[0][1])}" style="width:100%;max-height:440px;object-fit:contain;background:#fff;border-radius:14px"><figcaption class="small muted">{E(prods[0][1])} (제품 사진: {E(bnm)})</figcaption></figure>' if img else ""
        pg = "".join(f'<a class="mc" href="{h}"><img loading="lazy" src="{E(i)}"{RP if i.startswith("http") else ""} alt="{E(n)}" style="width:100%;aspect-ratio:1/1;object-fit:contain;background:#fff;border-radius:8px;margin-bottom:6px"><b>{E(n[:40])}</b><small>사진·규격 보기</small></a>' for h, n, i in prods)
        fqa = [(f"{nm.replace(' 순서', '')}은 어떻게 하나요?", " ".join(steps[:3]))] + list(fq) + [("이 순서가 제조사 공식 시공법인가요?", f"아니요. 영진종합목재가 정리한 일반적인 시공 순서입니다. 제품마다 방법이 다를 수 있으니 {bnm} 제품의 시공 설명서를 우선 따르세요."), ("자재는 어디서 사나요?", "대전 유성 영진종합목재(월드건축자재) 매장에서 상담·주문하실 수 있고 전국 배송도 됩니다.")]
        _lk = lambda t: re.sub(r"\((/[A-Za-z0-9_/.\-#=%]+)\)", r'(<a href="\1">바로 보기</a>)', E(t))
        body = (f'<section class="wrap sec"><p class="crumb"><a href="/sigongbeop/">자재 시공법</a> › <a href="/sigongbeop/brand.html">회사별 시공법</a> › <a href="/sigongbeop/brand-{bk}.html">{E(bnm)}</a></p>'
                f'<h1>{E(nm)}</h1><p class="lead">{E(lead)}</p>{hero}' + plan_html(slug, E, _CSS[0], ROOT, gs) +
                f'<h2>시공 순서</h2><ol>' + "".join(f"<li>{E(s)}</li>" for s in steps) + '</ol>'
                f'<h2>준비할 자재·공구</h2><ul>' + "".join(f"<li>{E(s)}</li>" for s in tools) + '</ul>'
                + (f'<h2>주의할 점</h2><ul>' + "".join(f"<li>{E(s)}</li>" for s in warn) + '</ul>' if warn else "")
                + (f'<h2>{E(bnm)} 관련 제품</h2><div class="mg m2">{pg}</div>' if pg else "")
                + (f'<p>같은 공정의 자세한 그림 설명서: <a href="/sigongbeop/{gs}.html">{E(sgn.get(gs, "자재 시공법"))} ›</a></p>' if gs in sgn else "")
                + f'<p class="small muted">이 페이지는 영진종합목재가 정리한 일반적인 시공 순서이며 {E(bnm)}의 공식 시공 지침이 아닙니다. 제품마다 방법이 다를 수 있으니 제품 시공 설명서를 우선 따르세요. 제품 사진·이름은 {E(bnm)} 제공 자료입니다. (정리 {DATE})</p>'
                + '<h2>자주 묻는 질문</h2>' + "".join(f'<details><summary>{E(q)}</summary><p>{_lk(a)}</p></details>' for q, a in fqa)
                + f'<h2>{E(bnm)} 다른 시공법</h2><div class="olk">' + "".join(f'<a href="/sigongbeop/{x[0]}.html">{E(x[2])}</a>' for x in G if x[1] == bk and x[0] != slug) + f'<a class="ac" href="/sigongbeop/brand.html">회사별 시공법 전체</a></div></section>{CTA}')
        _st = lambda t: re.sub(r"\(/[^)]*\)", "", t)
        ld = [{"@context": "https://schema.org", "@type": "HowTo", "name": nm, "description": lead, **({"image": img} if img else {}),
               "tool": [{"@type": "HowToTool", "name": t} for t in tools], "step": [{"@type": "HowToStep", "position": i + 1, "text": s} for i, s in enumerate(steps)]},
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": _st(a)}} for q, a in fqa]}]
        page(f"sigongbeop/b-{slug}.html", f"{nm} — 준비물·주의점·관련 제품 | 영진목재", f"{nm}: {lead[:110]}", body, "/sigongbeop/", ld, img)
        cards[bk].append(f'<a class="mc" href="/sigongbeop/b-{slug}.html">' + (f'<img loading="lazy" src="{E(img)}"{rp} alt="" style="width:100%;aspect-ratio:4/3;object-fit:contain;background:#fff;border-radius:8px;margin-bottom:6px">' if img else "") + f'<b>{E(nm)}</b><small>{E(lead[:42])}…</small></a>')
    # 회사별 허브
    jump = "".join(f'<a href="#b-{k}">{E(nm)} {len(cards[k])}</a>' for k, nm, d, one in BR if cards[k])
    secs = ""
    for k, nm, d, one in BR:
        if not cards[k]: continue
        page(f"sigongbeop/brand-{k}.html", f"{nm} 시공법 모음 — {one} | 영진목재", f"{nm} 제품({one}) 시공 순서·준비물·주의점을 한곳에. 제품 사진과 함께 보는 일반 시공 순서.",
             f'<section class="wrap sec"><p class="crumb"><a href="/sigongbeop/">자재 시공법</a> › <a href="/sigongbeop/brand.html">회사별 시공법</a> › {E(nm)}</p><h1>{E(nm)} 시공법 모음</h1><p class="lead">{E(nm)} {E(one)} 제품을 시공하는 일반적인 순서를 모았습니다. 제품 사진·이름은 {E(nm)} 제공 자료이며, 순서는 공식 지침이 아니니 제품 설명서를 함께 확인하세요.</p><div class="mg m2">{"".join(cards[k])}</div>{f'<p><a href="/{d}/">{E(nm)} 제품 전체 보기 ›</a></p>' if d else '<p class="small muted">해당 회사 제품·서비스가 아니며 관계없습니다. 비슷한 분위기를 우리 매장 자재로 시공하는 일반 순서입니다.</p>'}</section>{CTA}', "/sigongbeop/")
        secs += f'<h2 id="b-{k}">{E(nm)} <small class="muted">{E(one)}</small></h2><div class="mg m2">{"".join(cards[k][:4])}</div><p><a href="/sigongbeop/brand-{k}.html">{E(nm)} 시공법 전체 보기 ›</a></p>'
    page("sigongbeop/brand.html", "회사별 자재 시공법 — 영림·예림·쉐누·본덱스·니치하·제일타카, 한샘·리바트·KCC·LX·현대L&C·까사미아 스타일 | 영진목재", "영림 중문·방문·필름, 예림 중문, 쉐누 도어, 본덱스 오일스테인, 니치하 사이딩, 제일타카 사용 순서를 회사별로 정리했습니다.",
         f'<section class="wrap sec"><p class="crumb"><a href="/sigongbeop/">자재 시공법</a> › 회사별</p><h1>회사별 자재 시공법</h1><p class="lead">우리 매장에서 다루는 회사 제품별로 시공 순서·준비물·주의점을 정리했습니다. 제품 사진과 함께 보고, 같은 공정의 그림 설명서로 이어집니다.</p><div class="olk">{jump}</div>{secs}</section>{CTA}', "/sigongbeop/")
    return f'<section class="wrap sec"><h2>회사별 시공법</h2><p>영림·예림·쉐누·본덱스·니치하·제일타카 제품과, 한샘·리바트·KCC·LX 지인·현대L&C·까사미아 스타일 인테리어를 회사별로 나눠 시공 순서를 정리했습니다.</p><div class="olk">' + "".join(f'<a href="/sigongbeop/brand-{k}.html">{E(nm)} {len(cards[k])}</a>' for k, nm, d, one in BR if cards[k]) + '<a class="ac" href="/sigongbeop/brand.html">전체 보기</a></div>' + "".join(f'<h3>{E(nm)}</h3><div class="mg m2">{"".join(cards[k][:4])}</div>' for k, nm, d, one in BR if cards[k]) + '</section>'


# 한샘·리바트 스타일 — 해당 회사 제품·서비스 아님(관계없음). 회사 사진·로고 안 씀, 그림은 우리 그림 설명서.
BR += [("hanssem", "한샘 스타일", None, "주방·붙박이장·욕실·중문·아트월 분위기를 우리 자재로"), ("livart", "리바트 스타일", None, "마루·무몰딩·커튼박스·드레스룸·문 필름 분위기를 우리 자재로")]
GS = [  # slug, key, 이름, 우리 시공법 slug, 리드, 순서, 준비물, 주의, FAQ, 자재 링크
 ("hs-sink-door", "hanssem", "한샘 스타일 싱크대 문짝 교체·리폼", "sinkdae-munjjak", "한샘 주방처럼 깔끔한 단색 무광 싱크대 느낌을, 몸통은 두고 문짝만 새로 달거나 필름으로 덮어 내는 방법입니다.",
  ["문짝 크기(폭·높이·두께)와 경첩 위치를 하나씩 잽니다.", "새 문짝을 맞추거나, 기존 문짝을 떼어 필름을 붙일지 정합니다.", "필름이면 기름때를 닦고 사포·프라이머 후 붙입니다.", "경첩을 달고 문 간격을 경첩 나사로 조절합니다.", "손잡이를 바꾸거나 푸시 방식으로 정리합니다."],
  ["줄자", "드라이버", "인테리어 필름·밀대(필름 리폼 시)", "경첩"], ["주방 기름때를 다 닦지 않으면 필름이 들뜹니다."],
  [("싱크대 문짝만 바꿀 수 있나요?", "네. 몸통이 멀쩡하면 문짝만 맞춰 달거나 필름으로 덮을 수 있습니다(/qna/sink-munjjak-jejak.html).")], [("/younglim/film.html", "인테리어 필름"), ("/bigyo/gyeongcheop-types.html", "경첩 종류")]),
 ("hs-butbakijang", "hanssem", "한샘 스타일 붙박이장 문 필름 리폼", "film-sigong", "오래된 붙박이장 문을 한샘 붙박이장처럼 밝은 단색·우드 톤으로 바꾸는 필름 리폼 순서입니다.",
  ["문을 떼거나 붙인 채로 손잡이를 풉니다.", "먼지·기름을 닦고 사포로 가볍게 간 뒤 프라이머를 바릅니다.", "필름을 넉넉히 잘라 가운데서 밖으로 밀어 붙입니다.", "모서리는 드라이기로 열을 살짝 주며 감싸고 남는 부분을 자릅니다.", "손잡이를 다시 달거나 새 손잡이로 바꿉니다."],
  ["인테리어 필름", "프라이머·붓", "밀대·커터칼", "드라이기"], ["문 가장자리(엣지)를 꼼꼼히 감싸야 오래갑니다."], [], [("/younglim/film.html", "인테리어 필름")]),
 ("hs-yoksil", "hanssem", "한샘 스타일 욕실 리모델링 순서", "yoksil-tile", "한샘 욕실처럼 큰 타일·젠다이·수납장으로 정리된 욕실 느낌을 내는 일반 순서입니다. 방수와 배관은 전문가에게 맡기는 경우가 많습니다.",
  ["철거할지 덧방할지 정하고 기존 타일 들뜸을 확인합니다.", "배관·전기(콘센트·환풍기)를 먼저 정리합니다.", "방수를 하고 벽·바닥 타일을 붙입니다.", "줄눈을 넣고 굳힙니다.", "천장재·수전·변기·세면대·수납장을 답니다.", "틈을 바이오 실리콘으로 마감합니다."],
  ["타일·접착제", "줄눈제", "바이오 실리콘", "수평기"], ["방수가 잘못되면 아래층 누수로 이어집니다."],
  [("욕실 타일 덧방 되나요?", "기존 타일이 단단히 붙어 있으면 덧방도 합니다. 들뜬 곳이 있으면 떼고 합니다.")], [("/bigyo/porcelain-vs-dogijil.html", "포세린 vs 도기질"), ("/bigyo/epoxy-vs-cement-julnun.html", "에폭시 줄눈")]),
 ("hs-jungmun", "hanssem", "한샘 스타일 현관 중문", "jungmun", "한샘 현관처럼 슬림한 프레임과 큰 유리로 깔끔한 중문 느낌을 내는 방법입니다. 우리 매장의 영림·예림·쉐누 중문으로 맞출 수 있습니다.",
  ["현관 폭·높이를 세 곳씩 잽니다.", "슬림 프레임·유리 종류·여는 방식을 고릅니다.", "틀을 수평으로 고정합니다.", "문짝을 달고 움직임을 조절합니다.", "틈을 마감합니다."],
  ["줄자·수평기", "전동드릴", "앙카·실리콘"], [], [], [("/younglim/jungmun-slim.html", "영림 슬림 중문"), ("/yerim/jungmun-slim.html", "예림 슬림 중문")]),
 ("hs-artwall", "hanssem", "한샘 스타일 거실 아트월(템바보드)", "tempa-byeok", "거실 TV 뒤를 세로 줄무늬 템바보드로 포인트 주는 방법입니다.",
  ["벽 폭·높이를 재고 콘센트·TV 위치를 정합니다.", "벽이 고르지 않으면 각재로 하지틀을 댑니다.", "첫 장을 수직으로 세워 본드·실타카로 고정합니다.", "이어 붙이고 끝은 마감재로 덮습니다."],
  ["템바보드", "실타카·본드", "레이저 레벨", "직소"], ["실크 벽지 위는 접착이 약합니다."], [], [("/gagyeok/tempa-board.html", "템바보드 가격")]),
 ("lv-maru", "livart", "리바트 스타일 마루 바꾸기", "gangmaru", "리바트 집꾸미기처럼 밝은 오크 톤 마루로 바닥 분위기를 바꾸는 일반 순서입니다.",
  ["바닥 평탄과 습기를 확인합니다.", "기존 바닥재를 걷을지 위에 덧깔지 정합니다.", "빛 방향으로 첫 줄을 정해 깝니다.", "걸레받이로 가장자리를 마감합니다."],
  ["마루", "본드·빗살 헤라(접착식)", "고무망치", "톱"], ["바탕 습기가 많으면 들뜹니다."], [], [("/younglim/maru.html", "영림 마루"), ("/bigyo/spc-vs-kangmaru.html", "SPC vs 강마루")]),
 ("lv-mumolding", "livart", "리바트 스타일 무몰딩·마이너스 몰딩", "minus-molding-sigong", "천장 몰딩이 안 보이는 깔끔한 무몰딩·마이너스 몰딩 느낌을 내는 방법입니다. 목공 단계에서 미리 계획해야 합니다.",
  ["천장과 벽이 만나는 선을 곧게 잡습니다.", "마이너스 몰딩(홈 몰딩)을 대거나 석고 끝을 띄워 홈을 만듭니다.", "퍼티로 이음을 정리하고 칠·도배합니다."],
  ["마이너스 몰딩", "석고보드", "퍼티·사포"], ["벽·천장이 곧지 않으면 선이 삐뚤어 보입니다."], [], [("/younglim/molding.html", "영림 몰딩")]),
 ("lv-curtainbox", "livart", "리바트 스타일 커튼박스 간접조명", "keoteun-box", "커튼 레일을 천장 속에 숨기고 간접등으로 은은하게 빛나게 하는 방법입니다.",
  ["창 위 천장 속 깊이와 커튼 레일 두 줄 폭을 정합니다.", "각재로 커튼박스 틀을 짭니다.", "석고보드로 덮고 간접등 전선 자리를 남깁니다.", "레일과 간접등을 답니다."],
  ["각재", "석고보드", "LED 간접등", "커튼 레일"], ["전기 연결은 차단기를 내리고 합니다."], [], [("/qna/curtainbox-ganjeop.html", "커튼박스 간접조명")]),
 ("lv-dressroom", "livart", "리바트 스타일 드레스룸 가벽·선반", "gabyeok-sigong", "작은방을 드레스룸으로 바꿀 때 가벽과 선반으로 공간을 나누는 방법입니다.",
  ["옷 길이에 맞춰 행거 높이·선반 위치를 정합니다.", "필요하면 각재·석고보드로 가벽을 세웁니다.", "벽 바탕(각재·앙카)에 선반 브라켓과 행거를 고정합니다.", "조명과 거울을 답니다."],
  ["각재·석고보드", "선반 브라켓·행거 봉", "앙카·피스"], ["무거운 옷 무게를 생각해 바탕에 단단히 고정합니다."], [], [("/qna/dressroom.html", "드레스룸 만들기")]),
 ("lv-munfilm", "livart", "리바트 스타일 방문·문틀 필름", "munteul-film", "누런 방문·문틀을 화이트·그레이 톤으로 바꿔 집 전체를 밝게 만드는 필름 리폼 순서입니다.",
  ["문과 문틀의 먼지·기름을 닦고 찍힌 곳을 메웁니다.", "사포로 갈고 프라이머를 바릅니다.", "문틀부터 필름을 붙이고 문짝을 붙입니다.", "손잡이·경첩 부위는 칼로 정리합니다."],
  ["인테리어 필름", "프라이머", "밀대·커터칼", "드라이기"], [], [], [("/younglim/film.html", "인테리어 필름")]),
]


CO = {"hanssem": "한샘", "livart": "현대리바트", "kcc": "KCC", "lxzin": "LX하우시스", "hlnc": "현대L&C", "casamia": "까사미아"}
BR += [("kcc", "KCC 스타일", None, "창호·욕실·마루 분위기를 우리 자재로"), ("lxzin", "LX 지인 스타일", None, "필름 벽·마루·단열 분위기를 우리 자재로"),
       ("hlnc", "현대L&C 스타일", None, "주방 리폼·아트월·바닥 분위기를 우리 자재로"), ("casamia", "까사미아 스타일", None, "웨인스코팅·호텔식 벽·간접조명 분위기를 우리 자재로")]
GS += [
 ("kcc-changho", "kcc", "KCC 스타일 베란다 창호 교체 준비", "uretan-foam", "큰 통유리 느낌의 이중창으로 바꿀 때, 창틀 둘레 틈을 폼·실리콘으로 막고 마감하는 준비 순서입니다. 창호 자체 설치는 전문 시공이 필요합니다.",
  ["기존 창틀 크기(폭·높이)를 여러 곳에서 재 둡니다.", "창을 떼어 낸 뒤 벽과 새 창틀 사이 틈을 확인합니다.", "새 창틀을 수평·수직으로 고정합니다.", "틈을 우레탄폼으로 절반 정도 채우고, 굳으면 잘라 냅니다.", "실내는 몰딩, 실외는 실리콘으로 마감합니다."],
  ["줄자·수평기", "우레탄폼·폼건", "실리콘", "몰딩"], ["폼을 너무 많이 쏘면 창틀이 휠 수 있습니다."], [("창호 교체 직접 되나요?", "창 설치는 무겁고 정밀해 보통 전문 시공을 맡기고, 둘레 마감은 직접 하기도 합니다.")], [("/bigyo/system-vs-ilban-changho.html", "시스템창 vs 일반 샷시"), ("/bigyo/bokcheung-vs-samjung-yuri.html", "복층 vs 삼중유리")]),
 ("kcc-yoksil", "kcc", "KCC 스타일 욕실 타일 덧방", "yoksil-tile", "큰 포세린 타일로 욕실을 밝게 바꾸는 덧방 순서입니다. 기존 타일이 단단할 때만 덧방합니다.",
  ["기존 타일을 두드려 들뜬 곳이 없는지 봅니다.", "기름때를 닦고 프라이머를 바릅니다.", "접착제를 빗살 흙손으로 펴고 타일을 붙입니다.", "줄눈을 넣고 수전·액세서리를 다시 답니다."],
  ["타일·접착제", "빗살 흙손", "레벨링 클립", "줄눈제"], ["덧방하면 벽이 두꺼워져 수전·문틀 쪽 마감을 챙깁니다."], [], [("/bigyo/porcelain-vs-dogijil.html", "포세린 vs 도기질")]),
 ("kcc-maru", "kcc", "KCC 스타일 거실 마루", "gangmaru", "밝은 우드 톤 마루로 거실 바닥을 바꾸는 일반 순서입니다.",
  ["바닥 평탄·습기를 확인합니다.", "빛 방향으로 첫 줄을 정합니다.", "본드를 펴고 마루를 깝니다(접착식).", "걸레받이로 마감합니다."], ["마루", "마루 본드·빗살 헤라", "고무망치"], [], [], [("/younglim/maru.html", "영림 마루")]),
 ("lx-filmwall", "lxzin", "LX 지인 스타일 필름 벽 리폼", "film-sigong", "벽지 대신 매끈한 필름으로 벽·문을 덮어 깔끔한 느낌을 내는 순서입니다.",
  ["벽 바탕의 요철을 퍼티로 메우고 사포로 갑니다.", "프라이머를 바르고 말립니다.", "필름을 위에서 아래로 밀대로 붙입니다.", "모서리·콘센트 둘레를 칼로 정리합니다."], ["인테리어 필름", "퍼티·사포", "프라이머", "밀대·칼"], ["바탕 요철이 그대로 비쳐 바탕 작업이 중요합니다."], [], [("/younglim/film.html", "인테리어 필름")]),
 ("lx-maru", "lxzin", "LX 지인 스타일 강마루", "gangmaru", "고른 무늬의 강마루로 집 전체 바닥을 바꾸는 일반 순서입니다.",
  ["기존 바닥재를 걷고 평탄을 잡습니다.", "본드를 펴고 강마루를 깝니다.", "문턱·이음은 몰딩으로 정리합니다."], ["강마루", "본드", "고무망치"], [], [], [("/bigyo/kangmaru-vs-kanghwa.html", "강마루 vs 강화마루")]),
 ("lx-danyeol", "lxzin", "LX 지인 스타일 결로 벽 단열", "isopink-byeok", "북쪽 방 벽의 결로·곰팡이를 줄이려고 단열재와 석고보드로 벽을 보강하는 순서입니다.",
  ["곰팡이 난 벽지를 떼고 벽을 말립니다.", "단열재를 벽에 붙이거나 각재 사이에 채웁니다.", "이음을 테이프로 막습니다.", "석고보드로 덮고 도배합니다."], ["단열재(아이소핑크 등)", "각재", "석고보드", "폼본드"], ["이음에 틈이 있으면 그 자리에 다시 결로가 생깁니다."], [], [("/bigyo/isopink-vs-eboard.html", "아이소핑크 vs 이보드")]),
 ("hl-sink", "hlnc", "현대L&C 스타일 주방 리폼", "sinkdae-munjjak", "주방 몸통은 두고 문짝·상판 느낌을 바꿔 새 주방처럼 보이게 하는 순서입니다.",
  ["문짝·서랍 앞판 크기를 잽니다.", "문짝을 새로 맞추거나 필름으로 덮습니다.", "손잡이·경첩을 바꿉니다.", "벽 백스플래시는 타일·판넬로 덧댑니다."], ["필름 또는 새 문짝", "경첩·손잡이", "실리콘"], [], [], [("/younglim/film.html", "인테리어 필름"), ("/bigyo/injo-vs-engineered-stone.html", "상판 비교")]),
 ("hl-artwall", "hlnc", "현대L&C 스타일 대리석 느낌 아트월", "tempa-byeok", "TV 뒤 벽을 대리석 무늬 판넬·필름으로 포인트 주는 순서입니다.",
  ["벽 크기와 TV·콘센트 위치를 정합니다.", "벽이 고르지 않으면 하지틀을 댑니다.", "판넬을 본드·실타카로 붙이거나 필름을 붙입니다.", "끝을 몰딩으로 마감합니다."], ["대리석 무늬 판넬 또는 필름", "실타카·본드", "레이저 레벨"], [], [], [("/younglim/wall.html", "영림 월패널")]),
 ("hl-decotile", "hlnc", "현대L&C 스타일 데코타일 바닥", "decotile", "상가·방 바닥을 데코타일로 바꾸는 순서입니다.",
  ["바닥을 평평하게 하고 청소합니다.", "가운데 기준선을 긋습니다.", "접착제를 펴고 기준선부터 붙입니다.", "롤러로 눌러 밀착합니다."], ["데코타일", "접착제·헤라", "칼", "롤러"], ["바탕 요철이 그대로 비칩니다."], [], [("/bigyo/jangpan-vs-decotile.html", "장판 vs 데코타일")]),
 ("cs-wainscoting", "casamia", "까사미아 스타일 웨인스코팅 벽", "molding-georebatgi", "벽에 몰딩으로 네모 틀을 만들어 클래식하고 고급스러운 느낌을 내는 순서입니다.",
  ["벽 폭을 칸 수로 나눠 틀 크기를 정하고 연필로 그립니다.", "몰딩을 45도로 잘라 네모 틀을 만듭니다.", "본드·실타카로 붙이고 틈을 메웁니다.", "벽과 몰딩을 같은 색으로 칠합니다."], ["평몰딩", "각도절단기", "실타카·본드", "페인트"], ["칸 간격이 고르지 않으면 어색해 보입니다."], [], [("/bigyo/wainscoting-vs-tempa.html", "웨인스코팅 vs 템바보드")]),
 ("cs-headwall", "casamia", "까사미아 스타일 호텔식 침대 헤드 벽", "tempa-byeok", "침대 뒤 벽을 템바보드·판넬로 감싸 호텔 같은 느낌을 내는 순서입니다.",
  ["침대 폭보다 넉넉하게 벽 마감 폭을 정합니다.", "콘센트·조명 자리를 먼저 정합니다.", "판을 붙이고 위쪽에 간접등 자리를 남깁니다.", "끝을 마감재로 덮습니다."], ["템바보드", "실타카·본드", "LED 간접등"], [], [], [("/qna/tempa-headboard.html", "템바보드 헤드보드")]),
 ("cs-ganjeop", "casamia", "까사미아 스타일 우물천장 간접조명", "seokgo-cheonjang", "거실 천장 둘레에 숨은 조명을 넣어 은은한 분위기를 내는 순서입니다.",
  ["천장 단 높이와 간접등 자리를 정합니다.", "각재로 단 틀을 짜고 석고보드로 덮습니다.", "턱 안쪽에 LED를 넣을 공간을 남깁니다.", "퍼티·도장 후 조명을 답니다."], ["각재", "석고보드", "LED 간접등"], ["전기는 차단기를 내리고 작업합니다."], [], [("/qna/curtainbox-ganjeop.html", "간접조명")]),
]

_gen0 = gen
_CSS = [""]


def gen(page, E, CTA, ROOT, SG, PL2CSS=""):
    _CSS[0] = PL2CSS
    sgn = {x[0]: x[1] for x in SG}
    for slug, bk, nm, gs, lead, steps, tools, warn, fq, links in GS:
        bnm = dict((k, n) for k, n, *_ in BR)[bk]; co = CO[bk]
        im = f"/assets/sigongbeop/{gs}.jpg" if os.path.exists(f"{ROOT}/assets/sigongbeop/{gs}.jpg") else None
        fqa = list(fq) + [(f"{co} 제품이나 시공인가요?", f"아니요. {co}와 관계없는 페이지로, 비슷한 분위기를 영진종합목재 매장 자재로 직접 시공하는 일반 순서를 정리했습니다."), ("자재는 어디서 사나요?", "대전 유성 영진종합목재(월드건축자재) 매장에서 상담·주문하실 수 있고 전국 배송도 됩니다.")]
        _lk = lambda t: re.sub(r"\((/[A-Za-z0-9_/.\-#=%]+)\)", r'(<a href="\1">바로 보기</a>)', E(t))
        body = (f'<section class="wrap sec"><p class="crumb"><a href="/sigongbeop/">자재 시공법</a> › <a href="/sigongbeop/brand.html">회사별 시공법</a> › <a href="/sigongbeop/brand-{bk}.html">{E(bnm)}</a></p>'
                f'<h1>{E(nm)}</h1><p class="lead">{E(lead)}</p><p class="small muted">{E(co)} 제품·서비스가 아니며 {E(co)}와 관계없습니다. 회사 사진·로고는 쓰지 않았고, 그림은 영진종합목재가 직접 그린 그림입니다.</p>'
                + (f'<figure class="mkfig"><img src="{im}" width="1200" height="800" alt="{E(nm)} 완성 그림" style="width:100%;height:auto;border-radius:14px"><figcaption class="small muted">완성 모습 그림(영진종합목재)</figcaption></figure>' if im else "")
                + plan_html(slug, E, _CSS[0], ROOT, gs) + '<h2>시공 순서</h2><ol>' + "".join(f"<li>{E(s)}</li>" for s in steps) + '</ol><h2>준비할 자재·공구</h2><ul>' + "".join(f"<li>{E(s)}</li>" for s in tools) + '</ul>'
                + (f'<h2>주의할 점</h2><ul>' + "".join(f"<li>{E(s)}</li>" for s in warn) + '</ul>' if warn else "")
                + '<h2>이 분위기에 쓰는 자재</h2><div class="olk">' + "".join(f'<a href="{h}">{E(n)}</a>' for h, n in links) + (f'<a class="ac" href="/sigongbeop/{gs}.html">{E(sgn.get(gs, "그림 설명서"))} 그림 설명서</a>' if gs in sgn else "") + '</div>'
                + '<h2>자주 묻는 질문</h2>' + "".join(f'<details><summary>{E(q)}</summary><p>{_lk(a)}</p></details>' for q, a in fqa)
                + f'<h2>{E(bnm)} 다른 시공법</h2><div class="olk">' + "".join(f'<a href="/sigongbeop/b-{x[0]}.html">{E(x[2])}</a>' for x in GS if x[1] == bk and x[0] != slug) + f'<a class="ac" href="/sigongbeop/brand.html">회사별 시공법 전체</a></div></section>{CTA}')
        _st = lambda t: re.sub(r"\(/[^)]*\)", "", t)
        ld = [{"@context": "https://schema.org", "@type": "HowTo", "name": nm, "description": lead, **({"image": "https://www.wwood.co.kr" + im} if im else {}), "step": [{"@type": "HowToStep", "position": i + 1, "text": s} for i, s in enumerate(steps)]},
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": _st(a)}} for q, a in fqa]}]
        page(f"sigongbeop/b-{slug}.html", f"{nm} — 직접 시공 순서·자재 | 영진목재", f"{nm}: {lead[:100]} ({co}와 관계없는 일반 시공 안내)", body, "/sigongbeop/", ld, im)
        G.append((slug, bk, nm, [], "", gs, lead, steps, tools, warn, fq))  # 목록용(제품 고르기 없음)
        _IMG[slug] = im
    return _gen0(page, E, CTA, ROOT, SG)


_IMG = {}


# 2D 도면 — 벽·바닥·데크는 PL2(plan2d.js, 치수 바꾸면 재단 목록까지), 문·중문은 아래 정면도·평면도 SVG
PLAN = {
 "yl-jungmun-3yeondong": ("door", "3yeon", 1400, 2300), "yl-jungmun-yanggae": ("door", "yanggae", 1400, 2300), "yl-bangmun-gyoche": ("door", "swing", 900, 2100),
 "yl-munteul": ("door", "frame", 900, 2100), "yl-wall": ("pl2", "whap", 3000, 0, 2400), "yl-maru": ("pl2", "fhap", 3600, 3000, 0),
 "yr-jungmun-sliding": ("door", "one", 1200, 2300), "yr-jungmun-folding": ("door", "fold", 1600, 2300), "yr-ganssal": ("door", "3yeon", 1400, 2300),
 "yr-door-abs": ("door", "swing", 900, 2100), "yr-door-frame": ("door", "frame", 900, 2100), "sh-door": ("door", "swing", 900, 2100), "sh-jungmun": ("door", "one", 1200, 2300),

 "bd-deck-oil": ("pl2", "deck", 3600, 2400, 0), "nc-siding": ("pl2", "whap", 6000, 0, 3000), "tk-framing": ("pl2", "wgyp", 3000, 0, 2400), "tk-concrete": ("pl2", "wgyp", 3000, 0, 2400),
 "hs-jungmun": ("door", "one", 1200, 2300), "hs-artwall": ("pl2", "whap", 3000, 0, 2400), "lv-maru": ("pl2", "fhap", 3600, 3000, 0), "lv-dressroom": ("pl2", "wgyp", 2400, 0, 2400),
}


def _dim(x1, y1, x2, y2, t, v=False):
    s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#c0392b" stroke-width="1.3" marker-start="url(#da)" marker-end="url(#da)"/>'
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    return s + (f'<text x="{cx - 8}" y="{cy}" transform="rotate(-90 {cx - 8} {cy})" text-anchor="middle" font-size="17" font-weight="700" fill="#c0392b">{t}</text>' if v else f'<text x="{cx}" y="{cy - 7}" text-anchor="middle" font-size="17" font-weight="700" fill="#c0392b">{t}</text>')


def door_svg(kind, W, H):
    """정면도(왼쪽)+평면도(오른쪽). 치수 mm."""
    k = min(300 / W, 420 / H); w, h = W * k, H * k; x0, y0 = 60, 40
    R = lambda x, y, a, b, f="#f3e3c6", sw=1.4: f'<rect x="{x:.1f}" y="{y:.1f}" width="{a:.1f}" height="{b:.1f}" fill="{f}" stroke="#3b3128" stroke-width="{sw}"/>'
    s = R(x0 - 8, y0 - 8, w + 16, h + 8, "#e9e2d6")  # 문틀
    lab = {"3yeon": "3연동 슬라이딩 중문", "one": "원슬라이딩 중문", "yanggae": "양개 중문", "fold": "폴딩(접이식) 중문", "swing": "방문(여닫이)", "frame": "문틀"}[kind]
    if kind in ("3yeon", "one", "fold", "yanggae"):
        s += R(x0 - 8, y0 - 18, w + 16, 10, "#b9ada0")  # 상부 레일
    n = {"3yeon": 3, "one": 1, "yanggae": 2, "fold": 4, "swing": 1, "frame": 0}[kind]
    if kind == "3yeon":
        pw = w / 3 + 6
        for i in range(3): s += R(x0 + i * (w - pw) / 2, y0, pw, h, "#fbf1df") + R(x0 + i * (w - pw) / 2 + 10, y0 + 14, pw - 20, h - 28, "#dfeaf0")
    elif kind == "one":
        s += R(x0, y0, w * .62, h, "#fbf1df") + R(x0 + 10, y0 + 14, w * .62 - 20, h - 28, "#dfeaf0") + f'<text x="{x0 + w * .8}" y="{y0 + h / 2}" text-anchor="middle" font-size="15" fill="#6b5f52">고정창</text>' + R(x0 + w * .62, y0, w * .38, h, "#eef3f5")
    elif kind == "yanggae":
        for i in range(2): s += R(x0 + i * w / 2, y0, w / 2, h, "#fbf1df") + R(x0 + i * w / 2 + 10, y0 + 14, w / 2 - 20, h - 28, "#dfeaf0")
    elif kind == "fold":
        for i in range(4): s += R(x0 + i * w / 4, y0, w / 4, h, "#fbf1df") + R(x0 + i * w / 4 + 7, y0 + 14, w / 4 - 14, h - 28, "#dfeaf0")
    elif kind == "swing":
        s += R(x0, y0, w, h, "#fbf1df") + f'<circle cx="{x0 + w - 18}" cy="{y0 + h * .48}" r="6" fill="#3b3128"/>' + "".join(f'<rect x="{x0 - 3}" y="{y0 + h * f:.1f}" width="6" height="22" fill="#3b3128"/>' for f in (.1, .5, .85))
    elif kind == "frame":
        s += R(x0, y0, w, h, "#f6f3ee") + f'<text x="{x0 + w / 2}" y="{y0 + h / 2}" text-anchor="middle" font-size="15" fill="#6b5f52">문틀 안쪽</text>'
    s += _dim(x0, y0 + h + 30, x0 + w, y0 + h + 30, f"폭 {W:,}") + _dim(x0 - 32, y0, x0 - 32, y0 + h, f"높이 {H:,}", True)
    s += f'<text x="{x0 + w / 2}" y="{y0 + h + 66}" text-anchor="middle" font-size="16" font-weight="700" fill="#3b3128">정면도 · {lab}</text>'
    # 평면도
    px, py, pw2 = 450, 120, 300; kk = pw2 / W; wt = 150 * kk * 1.6
    s += R(px - 40, py, 40, wt, "#cfc6b8") + R(px + pw2, py, 40, wt, "#cfc6b8") + f'<text x="{px - 20}" y="{py - 8}" text-anchor="middle" font-size="13" fill="#6b5f52">벽</text>'
    if kind in ("3yeon", "one", "fold"):
        for i in range(n if kind != "fold" else 1):
            s += R(px + i * 8, py + 6 + i * 9, pw2 * (.62 if kind == "one" else .36), 7, "#a98b5d")
        s += f'<path d="M{px + pw2 * .5} {py + wt + 26}h-90" stroke="#2d6a4f" stroke-width="2" marker-end="url(#da2)"/><text x="{px + pw2 * .5 - 45}" y="{py + wt + 48}" text-anchor="middle" font-size="14" fill="#2d6a4f">여는 방향</text>'
        if kind == "fold": s += "".join(f'<line x1="{px + i * 30}" y1="{py + 10 + (i % 2) * 22}" x2="{px + (i + 1) * 30}" y2="{py + 10 + ((i + 1) % 2) * 22}" stroke="#a98b5d" stroke-width="6"/>' for i in range(4))
    elif kind == "yanggae":
        r = pw2 / 2
        s += f'<path d="M{px} {py + wt} l0 {r} M{px} {py + wt} m0 {r} A{r} {r} 0 0 0 {px + r} {py + wt}" fill="none" stroke="#a98b5d" stroke-width="2" stroke-dasharray="5 4"/><path d="M{px + pw2} {py + wt} l0 {r} M{px + pw2} {py + wt} m0 {r} A{r} {r} 0 0 1 {px + r} {py + wt}" fill="none" stroke="#a98b5d" stroke-width="2" stroke-dasharray="5 4"/>'
        s += f'<line x1="{px}" y1="{py + wt}" x2="{px}" y2="{py + wt + r}" stroke="#a98b5d" stroke-width="6"/><line x1="{px + pw2}" y1="{py + wt}" x2="{px + pw2}" y2="{py + wt + r}" stroke="#a98b5d" stroke-width="6"/><text x="{px + r}" y="{py + wt + r + 24}" text-anchor="middle" font-size="13" fill="#6b5f52">문이 열리는 공간(반경 {W // 2:,})</text>'
    elif kind == "swing":
        r = pw2
        s += f'<line x1="{px}" y1="{py + wt}" x2="{px}" y2="{py + wt + r}" stroke="#a98b5d" stroke-width="6"/><path d="M{px} {py + wt + r} A{r} {r} 0 0 0 {px + r} {py + wt}" fill="none" stroke="#a98b5d" stroke-width="2" stroke-dasharray="5 4"/><text x="{px + r / 2}" y="{py + wt + r + 22}" text-anchor="middle" font-size="13" fill="#6b5f52">문이 열리는 공간</text>'
    elif kind == "frame":
        s += R(px - 6, py - 6, 12, wt + 12, "#a98b5d") + R(px + pw2 - 6, py - 6, 12, wt + 12, "#a98b5d") + _dim(px + pw2 + 52, py, px + pw2 + 52, py + wt, "벽 두께", True) + f'<text x="{px + pw2 / 2}" y="{py + wt + 30}" text-anchor="middle" font-size="13" fill="#6b5f52">문틀 폭 = 벽 두께 + 문선 여유</text>'
    s += _dim(px, py - 30, px + pw2, py - 30, f"{W:,}") + f'<text x="{px + pw2 / 2}" y="{y0 + h + 66}" text-anchor="middle" font-size="16" font-weight="700" fill="#3b3128">평면도(위에서 본 모습)</text>'
    return (f'<svg viewBox="0 0 820 {int(y0 + h + 84)}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;background:#fff;border:1px solid #e6e0d4;border-radius:14px" role="img" aria-label="{lab} 2D 도면 폭 {W} 높이 {H}mm">'
            '<defs><marker id="da" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#c0392b"/></marker><marker id="da2" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#2d6a4f"/></marker></defs>'
            f'{s}</svg>')


def plan_html(slug, E, PL2CSS, ROOT, gs):
    p = PLAN.get(slug)
    if p and p[0] == "door":
        _, kind, W, H = p
        return (f'<h2>2D 도면 (정면·평면)</h2>{door_svg(kind, W, H)}<p class="small muted">예시 치수(mm)입니다. 실제 주문은 현관·문틀을 위·가운데·아래 세 곳씩 재서 가장 작은 값으로 정합니다. 도면: 영진종합목재.</p>')
    if p and p[0] == "pl2":
        _, t, w, d, h = p
        return ('<div class="pl2" id="pl2"><h2>2D 도면 · 필요한 자재 수량</h2><div class="pl2in"><label>가로<input type="number" id="plw"></label><label id="pld0">세로<input type="number" id="pld"></label><label id="plh0">높이<input type="number" id="plh"></label><span>mm</span></div><div class="pl2d" id="pl2svg"></div><h3>재단 목록 · 필요한 자재</h3><div id="pl2tb"></div><h3>순서 그림</h3><div id="pl2iso"></div><div class="pl2b"><button type="button" class="pl2pdf" id="pl2pdf">PDF로 저장</button></div></div>'
                '<script src="/assets/plan2d.js"></script><script>(function(){var P=PL2,p=' + json.dumps({"t": t, "w": w, "d": d, "h": h}) + ',g=function(i){return document.getElementById(i)};function draw(){g("pld0").style.display=p.t.charAt(0)=="w"?"none":"";g("plh0").style.display=p.t.charAt(0)!="w"?"none":"";g("plw").value=p.w;g("pld").value=p.d;g("plh").value=p.h;g("pl2svg").innerHTML=P.svg(p);g("pl2tb").innerHTML=P.table(p);g("pl2iso").innerHTML=P.iso(p,0)}'
                '["plw","pld","plh"].forEach(function(id){g(id).addEventListener("input",function(){var v=+this.value;if(v>0){p[{plw:"w",pld:"d",plh:"h"}[id]]=v;draw()}})});g("pl2pdf").onclick=function(){window.print()};draw()})();</script><style>' + PL2CSS + '</style>')
    if os.path.exists(f"{ROOT}/assets/sigongbeop/{gs}-steps.jpg"):
        return f'<h2>순서 그림 설명서</h2><img class="mkfig" loading="lazy" src="/assets/sigongbeop/{gs}-steps.jpg" alt="순서 그림 설명서" style="width:100%;height:auto;border-radius:14px;border:1px solid #e6e0d4"><p class="small muted">그림: 영진종합목재</p>'
    return ""

PLAN.update({"kcc-maru": ("pl2", "fhap", 4200, 3600, 0), "kcc-yoksil": ("pl2", "wgyp", 2000, 0, 2300), "lx-maru": ("pl2", "fhap", 3600, 3000, 0), "lx-danyeol": ("pl2", "wgyp", 3000, 0, 2400),
             "hl-artwall": ("pl2", "whap", 3000, 0, 2400), "hl-decotile": ("pl2", "fhap", 3600, 3000, 0), "cs-headwall": ("pl2", "whap", 2400, 0, 2400)})
