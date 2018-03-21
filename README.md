# NaverPlaceScrapper
Naver Place Scrapping Project
# 프로젝트 개요
- 네이버 플레이스에 등록되어 있는 상점 정보 조회하기
- pyqt5를 활용하여 GUI로 구성
- 검색어(e.g 강남 맛집)를 넣으면 모든 점포의 카테고리(업종),점포명,주소를 긁어온다.
- 각 점포 ID를 고유값으로 하므로 중복 없이(검색어가 중복되어도 e.g 강남 맛집, 서초역 맛집) 엑셀에 저장된다.

# 사용 기술
-Python(3.4)
-Pyqt5(for GUI)
-xlrd,xlwt(for excel)
-json,requests(for Scarpping and Parsing)
