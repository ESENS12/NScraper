# NaverPlaceScraper
Scraping Project
# 프로젝트 개요
- 상점 정보 조회하기
- pyqt5를 활용하여 GUI로 구성
- 검색어(e.g 강남 맛집)를 넣으면 모든 점포의 카테고리(업종),점포명,주소,전화번호 수집
- 모든 결과 데이터는 N사 검색결과를 기준으로 함(place, map..etc)
- 각 점포 ID를 고유값으로 하므로 중복 없이(검색어가 중복되어도 e.g 강남 맛집, 서초역 맛집) 엑셀로 저장

# 사용 기술
- Python(3.4)
- Pyqt5(for GUI)
- xlrd,xlwt(for excel)
- json,requests,BeautifulSoup(for Scrap and Parse)
