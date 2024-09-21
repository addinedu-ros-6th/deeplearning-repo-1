from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QDialog
from PyQt5.QtCore import QSocketNotifier
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import cv2
import mysql

import socket
import struct
import pickle
import datetime
import json

from inference import Inference
from judge import Judge

import login_gui

'''
TODO
- log 기록용 json형식 반환하기
    - json 뭐 들어갈지 정하기
- Object_Log에서 로그 더블클릭/조회 버튼 누르면 사진 띄우기
- 어보 빨간색 도로 처리하기
- 로그 쿼리 작성하기
- 로그 검색기능 완성하기
- sql 파일 만들기
    - sql 테이블 생성하는 코드 작성하기. 
- 트랙이랑 통신 뚫기
- 활성화 되어있는 탭만 작동하게 하기
- 
'''

from_class = uic.loadUiType('./dl_gui.ui')[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self, id, isAdmin, number):
        super().__init__()
        self.setupUi(self)

        self.user_id = id
        self.car_number = number
        self.label_car_number.setText(number)

        # 어드민 여부
        self.admin_tab_index = 2
        self.admin_tab_widget = self.Controll.widget(self.admin_tab_index)
        
        if isAdmin:
            self.show_admin_tab()
            print("Logged in as admin")
        else:
            self.hide_admin_tab()
            print("Logged in as regular user")

        # 소켓 설정
        self.socket_configuration()

        self.data = b""
        self.payload_size = struct.calcsize("Q")

        # QSocketNotifier 설정 (읽기 가능할 때 알림 받음)
        self.socket_notifier = QSocketNotifier(self.client_socket.fileno(), QSocketNotifier.Read)
        self.socket_notifier.activated.connect(self.read_data)

        # DB 설정
        self.db_configuration()

        # 추론 객체
        self.model = Inference()

        # 버튼
        self.btn_logout.clicked.connect(self.end_session)
        self.btn_search_1.clicked.connect(self.load_user_db)
        self.btn_search_2.clicked.connect(self.load_admin_db)

        self.tableWidget_1.cellDoubleClicked.connect(self.table1_dclicked)
        self.tableWidget_2.cellDoubleClicked.connect(self.table2_dclicked)

        # 시간 설정
        self.dateTime_start_1.setDateTime(QDateTime.currentDateTime())
        self.dateTime_end_1.setDateTime(QDateTime.currentDateTime())
        self.dateTime_start_2.setDateTime(QDateTime.currentDateTime())
        self.dateTime_end_2.setDateTime(QDateTime.currentDateTime())

        # 표 설정
        self.tableWidget_1.setColumnHidden(6, True)
        self.tableWidget_1.setColumnHidden(7, True)
        self.tableWidget_1.setColumnHidden(8, True)

        self.tableWidget_2.setColumnHidden(3, True)
        self.tableWidget_2.setColumnHidden(4, True)
        self.tableWidget_2.setColumnHidden(5, True)

        # 점수 차감
        self.judge = Judge()

        self.score = 0
        self.LCD_score.display(self.score)
        self.penalty = 0

        self.path_user = '../pictures/user_log/' + self.car_number + '/'
        self.path_admin = '../pictures/admin_log/' + self.car_number + '/'

    def __del__(self):
        self.client_socket.close()
        self.cursor.close()
        self.conn.close()


    def show_admin_tab(self):
        self.Controll.insertTab(self.admin_tab_index, self.admin_tab_widget, "Object_Log")

    def hide_admin_tab(self):
        self.Controll.removeTab(self.admin_tab_index)

    def socket_configuration(self, timeout=1):
        self.host = '192.168.0.15'
        self.port = 9999

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_socket.settimeout(timeout)

        try:
            # 서버에 연결 시도
            print(f"Trying to connect to {self.host}:{self.port}...")
            self.client_socket.connect((self.host, self.port))
            print(f"Connected to {self.host}:{self.port}")

        except socket.timeout:
            print(f"Connection timed out after {timeout} seconds")

        except socket.error as e:
            print(f"Socket error: {e}")

        # print(f"Listening on {self.host}:{self.port}...")
    
    def db_configuration(self):
        db_config = {
            'host': 'database-1.cpog6osggiv3.ap-northeast-2.rds.amazonaws.com',
            'user': 'arduino_PJT',
            'password': '1234',
            'database': 'ardumension'
        }

        print("connecting to database...")

        try:
            self.conn = mysql.connector.connect(**db_config)
            self.cursor = self.conn.cursor()
            print("Connected to DB")
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Error: {err}")


    def read_data(self):
        while len(self.data) < self.payload_size:
            self.data += self.client_socket.recv(4096)

        packed_msg_size = self.data[:self.payload_size]
        self.data = self.data[self.payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]

        while len(self.data) < msg_size:
            self.data += self.client_socket.recv(4096)

        frame_data = self.data[:msg_size]
        self.data = self.data[msg_size:]

        count = struct.unpack("I", frame_data[:4])[0]
        frame_data = frame_data[4:]

        # 프레임을 역직렬화
        frame, self.velocity = pickle.loads(frame_data)
        self.velocity = int(self.velocity)
        self.LCD_speed.display(self.velocity)

        # 프레임 크기 조정
        frame = cv2.resize(frame, (640, 480))

        # 수신한 count 값 출력
        # print("Received count:", count)

        self.show_frame(frame)
        # print(count, self.velocity)

        # 파일 저장을 위한 시간 저장
        self.now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.file_name = self.car_number + '_' + self.now + '_' + str(count)

    def show_frame(self, frame):
        try:
            frame_boxed, detects, cls_set, _json = self.model.predict(frame)

            frame_boxed = cv2.cvtColor(frame_boxed, cv2.COLOR_BGR2RGB)
            h, w, c = frame_boxed.shape
            qimage = QImage(frame_boxed.data, w, h, w * c, QImage.Format_RGB888)
            self.pixmap_monitor = QPixmap.fromImage(qimage)
            self.pixmap_monitor = self.pixmap_monitor.scaled(self.label.width(), self.label.height())
            self.label.setPixmap(self.pixmap_monitor)

            # 점수 차감
            self.charge_id, self.penalty, detected_classes, self.is_new_object, self.new_object = self.judge.verdict(detects, cls_set, self.velocity, frame)
            # self.update_label(detected_classes)
            
            if self.penalty:
                self.score += self.penalty
                print(self.score, self.penalty)
                self.LCD_score.display(self.score)
                self.label_lastPenalty.setText("-" + str(self.penalty))

                # 감점사항 있을 시 DB 업로드
                self.upload_penalty_data()
                cv2.imwrite(self.path_user+self.file_name, frame)
            
            # 새로운 객체 감지 시 DB 업로드
            for e in self.new_object:
                self.upload_new_object_data(e, _json)
                cv2.imwrite(self.path_admin+self.file_name, frame)

        except Exception as e:
            print(f"Error in show_frame: {e}")
    
    def upload_penalty_data(self):
        insert = f"insert into PenaltyLog values ({self.now}, {self.user_id}, {self.charge_id}, {self.velocity})"
        self.cursor.execute(insert)
    
    def upload_new_object_data(self, _object, _json):
        # json 파일 처리
        # list[list[dict[]]]
        # json_new = []
        # for json_list in _json:
        #     json_indi_new = []
        #     for dict in json_list:
        #         json_indi_new.append({key: dict[key] for key in ['name', 'class', 'confidence', 'box']})
        #     json_new.append(json_indi_new)

        json_new = []
        for json_list in _json:
            for dict in json_list:
                json_new.append({key: dict[key] for key in ['name', 'class', 'confidence', 'box']})
            
        insert = f"insert into ObjectLog values ({self.now}, {_object}, {self.car_number}, {self.path_admin}, {json_new}, {self.file_name})"
        self.cursor.execute(insert)

    def update_label(self, detected_classes):
        # set 데이터를 문자열로 변환하여 표시 (콤마로 구분)
        label_text = ", ".join(detected_classes)
        self.label_status_desc.setText(f"Detected Classes: {label_text}")
    
    def load_user_db(self):
        query = f"select pl.time, pl.user_id, pl.speed, pd.penalty_type, pd.penalty_score, \
                    pl.score, pl.image_path, pl.image_name, pl.json_data \
                    from PenaltyLog pl, PenaltyData pd \
                    where (pl.user_id = {self.user_id}) and (pl.penalty_id = pd.id);"
        self.cursor.execute(query)
        results = self.cursor.fetchall()

        self.tableWidget_1.setRowCount(len(results))

        for i, result in enumerate(results):
            
            date_time, user_id, speed, penalty_type, penalty_score, score, image_path, image_name, json_data = result
            date_time_str = date_time.strftime("%Y-%m-%d %H:%M")
            self.tableWidget_1.setItem(i, 0, QTableWidgetItem(date_time_str))
            self.tableWidget_1.setItem(i, 1, QTableWidgetItem(self.car_number))
            self.tableWidget_1.setItem(i, 2, QTableWidgetItem(str(score)))
            self.tableWidget_1.setItem(i, 3, QTableWidgetItem(penalty_type))
            self.tableWidget_1.setItem(i, 4, QTableWidgetItem(str(penalty_score)))
            self.tableWidget_1.setItem(i, 5, QTableWidgetItem(str(speed)))
            self.tableWidget_1.setItem(i, 6, QTableWidgetItem(image_path))
            self.tableWidget_1.setItem(i, 7, QTableWidgetItem(image_name))
            self.tableWidget_1.setItem(i, 8, QTableWidgetItem(json_data))

    def load_admin_db(self):
        query = f"select ol.time, ud.car_number, od.objects, ol.image_path, ol.image_name, ol.json_data\
                    from ObjectLog ol, ObjectData od, UserData ud \
                    where (ol.user_id = ud.id) and (ol.object_id = od.id);"
        self.cursor.execute(query)
        results = self.cursor.fetchall()

        self.tableWidget_2.setRowCount(len(results))

        for i, result in enumerate(results):
            date_time, car_number, _object, image_path, image_name, json_data = result
            date_time_str = date_time.strftime("%Y-%m-%d %H:%M")
            self.tableWidget_2.setItem(i, 0, QTableWidgetItem(date_time_str))
            self.tableWidget_2.setItem(i, 1, QTableWidgetItem(car_number))
            self.tableWidget_2.setItem(i, 2, QTableWidgetItem(_object))
            self.tableWidget_2.setItem(i, 3, QTableWidgetItem(image_path))
            self.tableWidget_2.setItem(i, 4, QTableWidgetItem(image_name))
            self.tableWidget_2.setItem(i, 5, QTableWidgetItem(json_data))
    
    def table1_dclicked(self, row, col):
        image_path = self.tableWidget_1.item(row, 6).text()
        image_name = self.tableWidget_1.item(row, 7).text()
        json_data = json.loads(self.tableWidget_1.item(row, 8).text())

        # 이미지에 박스 그리고 보여주기
        image = cv2.imread(image_path+image_name)
        for data in json_data:
            cls = data['name']
            conf = data['confidence']
            x1, x2, y1, y2 = data['box'].values()
            x1 = int(x1)
            x2 = int(x2)
            y1 = int(y1)
            y2 = int(y2)

            # 바운딩 박스 그리기
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)

            # 점수 텍스트 표시
            label = f'{conf:.2f}'
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 2)

            # 클래스 표시
            cv2.putText(image, cls, (x1 + 40, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 2)
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, c = image.shape
        qimage = QImage(image, w, h, w * c, QImage.Format_RGB888)
        self.pixmap_monitor_userlog = QPixmap.fromImage(qimage)
        self.pixmap_monitor_userlog = self.pixmap_monitor_userlog.scaled(self.label_preview_1.width(), self.label_preview_1.height())
        self.label_preview_1.setPixmap(self.pixmap_monitor_userlog)

    def table2_dclicked(self, row, col):
        image_path = self.tableWidget_2.item(row, 3).text()
        image_name = self.tableWidget_2.item(row, 4).text()
        json_data = json.loads(self.tableWidget_2.item(row, 5).text())
        print("image_path:", image_path)
        print("image_name:", image_name)

        image = cv2.imread(image_path+image_name)
        for data in json_data:
            cls = data['name']
            conf = data['confidence']
            x1, x2, y1, y2 = data['box'].values()
            x1 = int(x1)
            x2 = int(x2)
            y1 = int(y1)
            y2 = int(y2)

            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)

            label = f'{conf:.2f}'
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 2)

            cv2.putText(image, cls, (x1 + 40, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 2)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, c = image.shape
        qimage = QImage(image, w, h, w * c, QImage.Format_RGB888)
        self.pixmap_monitor_adminlog = QPixmap.fromImage(qimage)
        self.pixmap_monitor_adminlog = self.pixmap_monitor_adminlog.scaled(self.label_preview_2.width(), self.label_preview_2.height())
        self.label_preview_2.setPixmap(self.pixmap_monitor_adminlog)

    def end_session(self):
        self.close()
        self.show_login()
    
    def show_login(self):
        login_dialog = login_gui.LoginDialog()
        if login_dialog.exec_() == QDialog.Accepted:
            self.show()


