'''
180308
Author : ESENS
네이버 플레이스 검색을 도와주는 스크래핑 모듈
'''

import xlrd
import xlwt
import requests
import json
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import *
from xlutils.copy import copy
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QFileInfo

import random
import time
import sys
import os

id_dict = []
myList = []
alt_path = ""
excel_id_dict = []

#TODO: 다중 키워드 검색, 검색 기록 , 검색 중 정지, 결과 사용자에게 보여줌,

#네이버 지도에 ?로 표시되는 항목은(주소가 부정확 한경우??) 스크래핑이 안됨
#실제 네이버 결과와 비교하여 확인 결과 100% 취합이 가능한 것으로 보이며
#개수의 차이가 있는 경우는 네이버 지도상 표시되는 경계와 실제 지역으로 잡히는 바운더리가 달라서 인듯 함
#실제로 테스트 해본 경우는 1000개가 있다고 나왔는데 스크래핑 결과가 800개 정도일 때, 한 페이지당 20개의 가게가 노출되므로 499페이지에는
#점포가 전부 노출이 되어야 하지만 , 페이지를 이동 해 본 결과 데이터가 없고,  399페이지까지 데이터가 있는걸로 확인되므로
#스크래핑이 정확함


class mydata:

    global item_list
    item_list = []

    def __init__(self):
        self.id = str()
        self.name = str()
        self.roadAddr = str()
        self.commAddr = str()
        self.category = str()

    def setData(self,id,name,roadAddr,commAddr,addr,category):
        global id_dict
        if(id not in id_dict):
            id_dict.append(id)
            self.id = id
            self.name = name
            self.roadAddr = roadAddr
            self.commAddr = commAddr+" "+addr
            self.category = category
            return self
        else:
            return -1

    def show_data(self):
        return " " + self.name + " " + self.roadAddr + " " + self.commAddr + self.category


def get_html(url):
    _html = ""
    resp = requests.get(url)
    if resp.status_code == 200:
        _html = resp.text
    return _html

def get_parse(pagenum,query):
    if pagenum < 0:
        print("pagenum err")
        return -1
    print("get_parse : " + str(pagenum) + " ," +query)
    URL = "https://store.naver.com/restaurants/list?&page=" + str(pagenum) + "&query=" + query
    html = get_html(URL)
    if not html:
        print("is not html")
        return -1
    html = html.replace('\" \"' , "")
    html = html.replace(",null", "")
    html = html.replace('\"none\"', '\" \"')
    html = html.replace('\"None\"', '\" \"')
    html = html.replace("null,", '\" \",')
    #180404 추가, (오류 키워드 서초 맛집, promotionTitle 이 있는 가게에서 발생 )
    html = html.replace(':,', ':\" \",')
    #print(html)
    try:
        soup = BeautifulSoup(html, 'html.parser')
        # 3번째 script에 필요한 정보가 있으므로
        filter_area = soup.find_all('script')

        dataString = str(filter_area[2])
        #print("---- html parsing start ----")
        #print(dataString)
        print("---- html parsing end ----")
    except IndexError :
        #해당 script가 비어있음. pass
        return -1

    start_idx = dataString.find("\"searchCondition\"") - 1
    end_idx = dataString.rfind("}") + 1

    try:

        myjson = json.loads(dataString[start_idx: end_idx])

    except json.decoder.JSONDecodeError:
        print("해당 페이지에 오류가 있습니다(Json)")
        return -2
    arr_json = myjson['businesses']
    query = arr_json.get('queue')
    id_str = 'id'
    list_values = [id_str for id_str in arr_json.values()]

    # dict의 pair를 list로 받아올 수 없어서 list로 만든 다음 필요한 item만 slice
    itemjson = list_values[2]

    id_list = list()
    id_list = list(itemjson['items'])

    save_data = mydata()
    #save_data.__init__()
    #mydata를 저장할 list
    myData_list = []
    if(len(id_list) < 3):
        print("id_list size is under 3")
        return -1
    my_dict = dict()

    # 각 점포별로 iteration하면서 필요한 데이터 뽑아옴
    for i in range(0, len(id_list)+1):
        id = ""
        roadAddr = ""
        commonAddr = ""
        addr = ""
        category = ""

        id_chk = True
        name_chk = True
        roadAddr_chk = True
        commonAddr_chk = True
        addr_chk = True
        category_chk = True

        try:
            my_dict = id_list[i]
            #print(my_dict)
            if ('id' not in my_dict):
                id = "id 없음"
                id_chk = False
            else:
                id = my_dict['id']
            if ('name' not in my_dict):
                name = "상호명 없음"
                name_chk = False
            else:
                name = my_dict['name']
            if ('roadAddr' not in my_dict):
                roadAddr = "도로명 주소 없음"
                roadAddr_chk = False
            else:
                roadAddr = my_dict['roadAddr']
            if('commonAddr' not in my_dict):
                commonAddr = "일반주소 없음"
                commonAddr_chk = False
            else:
                commonAddr = my_dict['commonAddr']
            if ('addr' not in my_dict):
                addr = "상세주소 없음"
                addr_chk = False
            else:
                addr = my_dict['addr']

            if ('category' not in my_dict):
                category = "카테고리 없음"
                category_chk = False
            else:
                category = my_dict['category']

            if(not (id_chk or name_chk or roadAddr_chk or commonAddr_chk or addr_chk or category_chk)):
                print("전부 없는 경우 garbage 값이므로 pass")

            else:
                ret_save = save_data.setData(id,name,roadAddr,commonAddr,addr,category)
                if type(ret_save) is mydata:
                    myData_list.append(save_data)
                save_data = mydata()

        except TypeError as e:
            print("typeError!" + str(e))
            continue
        except IndexError as e1:
            print("Scrapping End")
            continue
        except:
            print("exception!")
            return -1
        #print(my_dict)
    return myData_list

class myTest(QMainWindow):
    #def __init__(self, parent=None):
        #super(myTest, self).__init__(parent)
    def __init__(self):
        super().__init__()
        alt_path = path
        print('alt_path is ..' + alt_path)
        '''
        #TODO alt path 수정해야함....(그래도 혹시 모르니 , 윈도우 기반 바탕화면 path 입력해둘것)
        global alt_path
        alt_path = ".../example.xls"
        if not path:
            alt_path = ".../pathSample.xls"
        else:
            alt_path = path+".xls"
        '''
        # 검색어
        self.textlabel = QLabel("검색어 :", self)
        self.textlabel.move(20, 30)
        self.textlabel.resize(60, 30)

        # 검색어 텍스트박스
        self.textedit = QTextEdit("", self)
        self.textedit.move(80,30)
        self.textedit.resize(260,30)

        btn_select = QPushButton("조회", self)
        btn_select.move(365, 30) #x, y
        btn_select.resize(80, 35) #width, height
        btn_select.clicked.connect(self.search_clicked)

        self.statusbar = self.statusBar()
        #x,y,width,height
        self.setGeometry(300, 200, 480, 240)
        self.setWindowTitle('Scrapping Module')

        #self.show_loading(True)
        self.show()

    def open(self):
        global path
        fileName, _ = QFileDialog.getSaveFileName(self, "Save as", path)

        if fileName:
            self.openFile(fileName)

    def openFile(self, fileName):

        if fileName:
            global alt_path
            alt_path = fileName
            if ".xls" not in fileName:
                alt_path += ".xls"

    def show_loading(self,tag):
        if tag:
            #self.movielabel.hide()
            self.movielabel.show()
            print("show!")
        else:
            self.movielabel.hide()
            print("not show!")

    def search_clicked(self):

        #lod = loading()
        #lod.show()

        textboxValue = self.textedit.toPlainText()
        # 해당 페이지에서 점포 정보가 없으면 -1을 리턴한다.
        global myList
        #myList = []
        chk_ret = check_space(self, str(textboxValue))
        #공백 체크 통과
        if chk_ret > 0 :
            for i in range(1, 500, 3):
                print("---------------" + str(i) + "--------------")
                ret = get_parse(i, str(textboxValue))
                if type(ret) is list:
                    myList.append(ret)
                    time.sleep(random.uniform(0.25, 1.8))
                    continue
                #json error catch
                elif ret == -2:
                    continue
                else:
                    print("ret is not list ")
                    break

        str_print = ""
        #movielabel.hide()
        if len(myList) < 1:
        #if ( type(ret) is not list ):
            QMessageBox.critical(self, 'Error!!', "검색결과가 없습니다. : " + textboxValue, QMessageBox.Ok)

        else: # data가 있는 경우에만 버튼 show 및 데이터 파싱
            QMessageBox.information(self, 'Success', "검색을 완료하였습니다 : " + textboxValue, QMessageBox.Ok)
            btn_save = QPushButton("저장", self)
            btn_save.move(100, 70)
            btn_save.clicked.connect(self.save_clicked)
            btn_save.show()

            btn_cancel = QPushButton("취소", self)
            btn_cancel.move(240, 70)
            btn_cancel.clicked.connect(self.cancel_clicked)
            btn_cancel.show()
            #전체 아이템의 개수
            cnt_idx = 0
            for i in range(0,len(myList)):
                for j in range(0, len(myList[i])):
                    cnt_idx += 1

            #데이터 label에 보여주기
            #self.label.setText(str_print)
            global parse_data
            parse_data = myList
    def cancel_clicked(self):
        self.close()

    def save_clicked(self):

        self.open()
        try:
            r_workbook = get_excel_data(alt_path)
            r_worksheet = r_workbook.sheet_by_index(0)
            num_rows = r_worksheet.nrows
            #print("num_rows : "+num_rows)
            #이어쓰기
            wb = copy(r_workbook)
            worksheet = wb.get_sheet(0)

            if(num_rows > 1): #이미 엑셀 데이터가 있는 경우
                ret = QMessageBox.question(self, '엑셀 데이터 존재', "이미 엑셀 파일이 존재합니다. 이어서 쓰시겠습니까?" , QMessageBox.Ok,
                                     QMessageBox.Cancel)
                #print(str(ret))
                if ret == 1024:
                    get_excel_id(alt_path)
                else:
                    QMessageBox.information(self, '저장 취소!', "저장이 취소되었습니다. : ", QMessageBox.Ok)
                    return


            #전체 아이템의 개수
            cnt_idx = 0
            global excel_id_dict
            global parse_data
            global myList
            for i in range(0, len(parse_data)):
                for j in range(0, len(parse_data[i])):
                    if (parse_data[i][j].id not in excel_id_dict):
                        worksheet.write(num_rows + cnt_idx, 0, num_rows + cnt_idx)    #번호
                        worksheet.write(num_rows + cnt_idx, 1, parse_data[i][j].id) #점포 id
                        worksheet.write(num_rows + cnt_idx, 2, parse_data[i][j].category)
                        worksheet.write(num_rows + cnt_idx, 3, parse_data[i][j].name)  #상호명
                        worksheet.write(num_rows + cnt_idx, 4, parse_data[i][j].roadAddr)  #도로명 주소
                        worksheet.write(num_rows + cnt_idx, 5, parse_data[i][j].commAddr)  #구주소1
                        cnt_idx += 1
                    else:
                        print("엑셀 데이터와 중복 발생! 패스함, ")
                    #worksheet.write(i+1, 5, parse_data[i].addr)  #구주소2(상세주소)
            wb.save(alt_path)
            QMessageBox.information(self, '저장완료!', "저장을 완료하였습니다. : ", QMessageBox.Ok)
            parse_data = list()
            myList = list()
        except:
            QMessageBox.critical(self, 'Error!!', "저장을 실패하였습니다. : ", QMessageBox.Ok)


def get_excel_data(path):
    #print('getExcelData path : ' + path)
    try:
        workbook = xlrd.open_workbook(path)
    except FileNotFoundError as e:
        #해당 경로에 excel 파일이 없으면 생성
        print("file not found! create new workbook")
        workbook = xlwt.Workbook(encoding='utf-8')
        workbook.default_style.font.height = 20 * 11
        worksheet = workbook.add_sheet(u'시트')

        font_style = xlwt.easyxf('font:height 280;')
        worksheet.row(0).set_style(font_style)

        # 세로인덱스, 가로 인덱스 , 들어갈 데이터
        worksheet.write(0, 0, u"번호")
        worksheet.write(0, 1, u"점포ID")
        worksheet.write(0, 2, u"카테고리")
        worksheet.write(0, 3, u"상호명")
        worksheet.write(0, 4, u"도로명 주소")
        worksheet.write(0, 5, u"지번 주소")
        workbook.save(path)
        return xlrd.open_workbook(path)
    except:
        print("another error!")
        return -1
    return workbook

def get_excel_id(path):
    global excel_id_dict
    workbook = xlrd.open_workbook(path)
    worksheet = workbook.sheet_by_index(0)
    num_rows = worksheet.nrows

    for row_num in range(num_rows):
        #print("excel:id"+str(worksheet.row_values(row_num)[1]))
        excel_id_dict.append(worksheet.row_values(row_num)[1])


#검색어 검증후 파싱하여 파싱데이터 반환
def check_space(self, testString):
    #문자열이 비어있는 경우는 false 이므로
    if not testString:
        print("검색어가 잘못 되었습니다.(공백이거나 검색 불가능한 특수문자 포함됨, \n \`~!@#$%^&*()-+=?/) \n" + testString)
        return -1
    else:
        my_str = "!@#$%^&*?=+-][)(`~}{"
        for i in range(0, len(my_str)):
            if my_str[i] in testString:
                #print("in!")
                print("검색어가 잘못 되었습니다.(공백이거나 검색 불가능한 특수문자 포함됨, \n \`~!@#$%^&*()-+=?/) \n" + testString)
                return -1
            else:
                continue
        return 1

if __name__ == '__main__':
    global path
    path = os.getcwd()
    print("main_func.. path : " + path)
    app = QApplication(sys.argv)
    ex = myTest()
    ex.show()
    sys.exit(app.exec_())

