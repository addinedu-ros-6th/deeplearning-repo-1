from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QDialog, QApplication, QLabel, QVBoxLayout, QHeaderView
from PyQt5.QtCore import QSocketNotifier, Qt
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import cv2
import mysql
import numpy as np

import socket
import struct
import pickle
import datetime
import json
import sys

from DrivingScoreSystem.inference import Inference
from DrivingScoreSystem.judge import Judge

import DrivingScoreSystem.login_gui

'''
TODO
- 어보 빨간색 도로 처리하기
- 로그 검색기능 완성하기
- 활성화 되어있는 탭만 작동하게 하기
- LCD 색 바뀌는거 작동 확인 하기
- 
'''

app = QApplication(sys.argv)
window = QMainWindow()
with open("./ui/Toolery.qss", 'r') as file:
        qss = file.read()
        app.setStyleSheet(qss)

from_class = uic.loadUiType('./ui/dl_gui.ui')[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self, id, isAdmin, number):
        super().__init__()
        self.setupUi(self)

        self.user_id = id
        self.car_number = number
        self.label_car_number.setText(number)

        self.object_data = {"lane": 1, "yellow_lane": 2, "stop_line": 3, "kidzone": 4, "sectoin_start": 5, "section_end": 6, "limit_30": 7, "limit_50": 8, 
                           "limit_100": 9, "oneway": 10, "dotted_lane": 11, "traffic_light_red": 12, "traffic_light_yellow": 13, "traffic_light_green": 14, 
                           "person": 15}

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
        self.socket_configuration_sectionSpeedReader()

        self.data = b""
        self.payload_size = struct.calcsize("Q")

        # QSocketNotifier 설정 (읽기 가능할 때 알림 받음)
        self.socket_notifier = QSocketNotifier(self.client_socket.fileno(), QSocketNotifier.Read)
        self.socket_notifier.activated.connect(self.read_data)

        self.socket_notifier_2 = QSocketNotifier(self.client_socket_2.fileno(), QSocketNotifier.Read)
        self.socket_notifier_2.activated.connect(self.read_data_2)
        
        # DB 설정
        self.db_configuration()

        # 추론 객체
        self.model = Inference()

        # 첫번째 탭 열려있을 떄만 영상 받아오기
        self.Controll.currentChanged.connect(self.on_tab_change)
        if self.Controll.currentIndex() == 0:
            self.socket_notifier.setEnabled(True)
            self.socket_notifier_2.setEnabled(True)

        # 버튼
        self.btn_logout.clicked.connect(self.end_session)
        self.btn_search_1.clicked.connect(self.load_user_db)
        self.btn_search_2.clicked.connect(self.load_admin_db)

        self.tableWidget_1.cellDoubleClicked.connect(self.table1_dclicked)
        self.tableWidget_2.cellDoubleClicked.connect(self.table2_dclicked)

        # 시간 설정
        self.dateTime_start_1.setDateTime(QDateTime.currentDateTime().addMonths(-1))
        self.dateTime_end_1.setDateTime(QDateTime.currentDateTime())
        self.dateTime_start_2.setDateTime(QDateTime.currentDateTime().addMonths(-1))
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
        self.section_speed = 0
        self.score = 0
        self.LCD_score.display(self.score)
        self.penalty = 0

        self.path_user = './pictures/user_log/' + self.car_number + '/'
        self.path_admin = './pictures/admin_log/' + self.car_number + '/'

    def __del__(self):
        self.client_socket.close()
        self.cursor.close()
        self.conn.close()


    def show_admin_tab(self):
        self.Controll.insertTab(self.admin_tab_index, self.admin_tab_widget, "Object_Log")

    def hide_admin_tab(self):
        self.Controll.removeTab(self.admin_tab_index)
    
    def on_tab_change(self, index):
        if index == 0:
            self.socket_notifier.setEnabled(True)
            self.socket_notifier_2.setEnabled(True)
        
        if index == 1:
            self.socket_notifier.setEnabled(False)
            self.socket_notifier_2.setEnabled(False)

            self.load_user_db()
        
        if index == 2:
            self.socket_notifier.setEnabled(False)
            self.socket_notifier_2.setEnabled(False)

            self.load_admin_db()

    def socket_configuration(self, timeout=1):
        self.host = '192.168.0.16'
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

    def socket_configuration_sectionSpeedReader(self, timeout=1):
        self.host_2 = '192.168.0.27'
        self.port_2 = 5555

        self.client_socket_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_socket_2.settimeout(timeout)

        try:
            # 두 번째 서버에 연결 시도
            print(f"Trying to connect to {self.host_2}:{self.port_2}...")
            self.client_socket_2.connect((self.host_2, self.port_2))
            print(f"Connected to {self.host_2}:{self.port_2}")

        except socket.timeout:
            print(f"Connection to {self.host_2} timed out after {timeout} seconds")

        except socket.error as e:
            print(f"Socket error: {e}")

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
            QMessageBox.warning(self, "Error", f"Error: {err}")

    def read_data(self):
        try:
            while len(self.data) < self.payload_size:
                self.data += self.client_socket.recv(4096)

            packed_msg_size = self.data[:self.payload_size]
            self.data = self.data[self.payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(self.data) < msg_size:
                self.data += self.client_socket.recv(4096)

            # 나머지는 frame 데이터
            frame_data = self.data[:msg_size]
            self.data = self.data[msg_size:]

            count = struct.unpack("I", frame_data[:4])[0]
            frame_data = frame_data[4:]

            # 프레임을 역직렬화
            frame, self.velocity = pickle.loads(frame_data)

            # 만약 self.velocity가 문자열인 경우에만 처리
            if isinstance(self.velocity, str):
                self.velocity = self.velocity.replace('\n', '').strip()
            
            # 정수형으로 변환
            self.velocity = int(self.velocity)
            self.velocity_static = -20
            if self.velocity > 80:
                self.velocity =self.velocity_static + self.velocity
            self.LCD_speed.display(self.velocity)

            if isinstance(frame, tuple) and isinstance(frame[0], np.ndarray):
                frame = frame[0]  # 튜플의 첫 번째 요소만 사용

            # 프레임이 이미지 데이터인지 확인
            if isinstance(frame, (np.ndarray)):
                # 프레임 크기 조정
                frame = cv2.resize(frame, (640, 480))
                self.show_frame(frame)
                # 파일 저장을 위한 시간 저장
                self.now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.file_name = self.car_number + '_' + self.now + '_' + str(count) + '.jpg'
            else:
                print(f"Received non-image data: {frame}")

        except (pickle.UnpicklingError, struct.error, cv2.error) as e:
            print(f"Error processing received data: {e}")

    def read_data_2(self):
        try:
            # 1024바이트씩 데이터를 수신
            data_2 = self.client_socket_2.recv(1024)
            
            if data_2:
                self.section_speed = data_2.decode('utf-8').strip()
            else:
                pass

        except ConnectionError as e:
            print(f"Connection error: {e}")

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
            self.charge_id, self.penalty, detected_classes, self.is_new_object, self.new_object = self.judge.verdict(detects, cls_set, self.velocity, frame, self.section_speed)
            self.update_label(detected_classes) 
            
            if self.penalty:
                self.score += self.penalty
                print(self.score, self.penalty)
                self.LCD_score.display(self.score)
                self.label_lastPenalty.setText("-" + str(self.penalty))

                # 감점사항 있을 시 DB 업로드
                self.upload_penalty_data(_json)
                cv2.imwrite(self.path_user+self.file_name, frame)
            
            # 새로운 객체 감지 시 DB 업로드
            if self.is_new_object:
                for e in self.new_object:
                    object_id = self.object_data[e]
                    self.upload_new_object_data(object_id, _json)
                    cv2.imwrite(self.path_admin+self.file_name, frame)
            
            # 점수 색상 설정
            if (self.score > 0) and (self.score < 30):
                self.LCD_score.setStyleSheet('QLCDNumber{ color: rgb(220, 220, 0); }')
            elif (self.score >= 30) and (self.score < 60):
                self.LCD_score.setStyleSheet('QLCDNumber{ color: rgb(220, 135, 0); }')
            elif self.score >= 60:
                self.LCD_score.setStyleSheet('QLCDNumber{ color: rgb(220, 0, 0); }')
            
            # 속도 색상 설정
            for detect in detects:
                for k, i in detect.items():
                    if k[:5] == 'limit':
                        split = k.split('_')
                        limit = split[-1]
                        if self.velocity > int(limit):
                            self.LCD_speed.setStyleSheet('QLCDNumber{ color: rgb(220, 0, 0); }')
                        else:
                            self.LCD_speed.setStyleSheet('QLCDNumber{ color: rgb(0, 0, 0); }')
                    else:
                        self.LCD_speed.setStyleSheet('QLCDNumber{ color: rgb(0, 0, 0); }')

        except Exception as e:
            print(f"Error in show_frame: {e}")

    def update_label(self, detected_classes):
        label_text = ",\n".join(detected_classes)
        self.label_status_desc.setText(label_text)
    
    def upload_penalty_data(self, _json):
        json_new = []
        for json_list in _json:
            for _dict in json_list:
                json_new.append({key: _dict[key] for key in ['name', 'class', 'confidence', 'box']})
        
        json_new = json.dumps(json_new)
        insert = f'''insert into PenaltyLog values ('{self.now}', {self.user_id}, {self.charge_id}, {self.velocity}, '{self.file_name}', '{self.path_user}', '{json_new}', {self.score})'''
        self.cursor.execute(insert)
        self.conn.commit()
    
    def upload_new_object_data(self, object_id, _json):
        json_new = []
        for json_list in _json:
            for _dict in json_list:
                json_new.append({key: _dict[key] for key in ['name', 'class', 'confidence', 'box']})
        json_new = json.dumps(json_new)
        insert = f'''insert into ObjectLog values ('{self.now}', {self.user_id}, {object_id}, '{self.path_admin}', '{json_new}', '{self.file_name}')'''

        self.cursor.execute(insert)
        self.conn.commit()

    def update_label(self, detected_classes):
        label_text = ",\n".join(detected_classes)
        self.label_status_desc.setText(label_text)
    
    def load_user_db(self):
        start_date1 = self.dateTime_start_1.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end_date1 = self.dateTime_end_1.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        search_option = self.comboBox_1.currentText()
        search_text = self.lineEdit.text()
        base_query = """
            SELECT pl.time, pl.speed, pd.penalty_type, pd.penalty_score,
                pl.score, pl.image_path, pl.image_name, pl.json_data
            FROM PenaltyLog pl
            JOIN PenaltyData pd ON pl.penalty_id = pd.id
            WHERE pl.user_id = %s AND pl.time BETWEEN %s AND %s
            """
        params = [self.user_id, start_date1, end_date1]
        
        if search_text:
            if search_option == 'All':
                base_query += """
                AND (pd.penalty_type LIKE %s OR pd.penalty_score LIKE %s OR pl.speed LIKE %s)
                """
                params.extend([f"%{search_text}%"] * 3)
            elif search_option == 'penalty_type':
                base_query += "AND pd.penalty_type LIKE %s"
                params.append(f"%{search_text}%")
            elif search_option == 'pd.penalty_score':
                base_query += "AND pd.penalty_score LIKE %s"
                params.append(f"%{search_text}%")
            elif search_option == 'speed':
                base_query += "AND pl.speed LIKE %s"
                params.append(f"%{search_text}%")
            else:
                QMessageBox.warning(self, "경고", "올바르지 않은 검색 옵션입니다.")
                return
        
        try:
            self.cursor.execute(base_query, params)
            results = self.cursor.fetchall()

            if len(results) == 0:
                QMessageBox.warning(self, "검색 결과", "선택한 조건에 맞는 데이터가 없습니다.")
                return

            self.tableWidget_1.setRowCount(len(results))

            header = self.tableWidget_1.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)

            for i, result in enumerate(results):
                date_time, speed, penalty_type, penalty_score, score, image_path, image_name, json_data = result
                date_time_str = date_time.strftime("%Y-%m-%d %H:%M:%S")

                item_1 = QTableWidgetItem(date_time_str)
                item_2 = QTableWidgetItem(self.car_number)
                item_3 = QTableWidgetItem(str(score))
                item_4 = QTableWidgetItem(penalty_type)
                item_5 = QTableWidgetItem(str(penalty_score))
                item_6 = QTableWidgetItem(str(speed))
                item_1.setTextAlignment(Qt.AlignCenter)
                item_2.setTextAlignment(Qt.AlignCenter)
                item_3.setTextAlignment(Qt.AlignCenter)
                item_4.setTextAlignment(Qt.AlignCenter)
                item_5.setTextAlignment(Qt.AlignCenter)
                item_6.setTextAlignment(Qt.AlignCenter)

                self.tableWidget_1.setItem(i, 0, item_1)
                self.tableWidget_1.setItem(i, 1, item_2)
                self.tableWidget_1.setItem(i, 2, item_3)
                self.tableWidget_1.setItem(i, 3, item_4)
                self.tableWidget_1.setItem(i, 4, item_5)
                self.tableWidget_1.setItem(i, 5, item_6)
                self.tableWidget_1.setItem(i, 6, QTableWidgetItem(image_path))
                self.tableWidget_1.setItem(i, 7, QTableWidgetItem(image_name))
                self.tableWidget_1.setItem(i, 8, QTableWidgetItem(json_data))
            
            # self.tableWidget_1.sortItems(0, Qt.DescendingOrder)

            if len(results) == 0:
                QMessageBox.warning(self, "검색 결과", "선택한 조건에 맞는 데이터가 없습니다.")
        
        except Exception as e:
            print(f"Error details: {str(e)}")
            QMessageBox.warning(self, "오류", f"데이터를 불러오는 중 오류가 발생했습니다: {str(e)}")


    def load_admin_db(self):
        start_date2 = self.dateTime_start_2.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end_date2 = self.dateTime_end_2.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        
        search_option = self.comboBox_2.currentText()
        search_text = self.lineEdit_2.text()
        
        base_query = """
        SELECT ol.time, ud.car_number, od.objects, ol.image_path, ol.image_name, ol.json_data
        FROM ObjectLog ol, ObjectData od, UserData ud 
        WHERE (ol.user_id = ud.id) AND (ol.object_id = od.id) 
        AND (ol.time BETWEEN %s AND %s)
        """
        
        if search_text:
            if search_option == 'All':
                additional_condition = """
                AND (ud.car_number LIKE %s OR od.objects LIKE %s OR ol.time LIKE %s)
                """
                search_params = (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%")
            elif search_option == 'plate':
                additional_condition = "AND ud.car_number LIKE %s"
                search_params = (f"%{search_text}%",)
            elif search_option == 'object':
                additional_condition = "AND od.objects LIKE %s"
                search_params = (f"%{search_text}%",)
            
            query = base_query + additional_condition
            params = (start_date2, end_date2) + search_params
        else:
            query = base_query
            params = (start_date2, end_date2)

        try:
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            
            self.tableWidget_2.setRowCount(len(results))

            header = self.tableWidget_2.horizontalHeader()       
            header.setSectionResizeMode(QHeaderView.Stretch)

            for i, result in enumerate(results):
                date_time, car_number, _object, image_path, image_name, json_data = result
                date_time_str = date_time.strftime("%Y-%m-%d %H:%M:%S")

                item_1 = QTableWidgetItem(date_time_str)
                item_2 = QTableWidgetItem(car_number)
                item_3 = QTableWidgetItem(_object)
                item_1.setTextAlignment(Qt.AlignCenter)
                item_2.setTextAlignment(Qt.AlignCenter)
                item_3.setTextAlignment(Qt.AlignCenter)

                self.tableWidget_2.setItem(i, 0, item_1)
                self.tableWidget_2.setItem(i, 1, item_2)
                self.tableWidget_2.setItem(i, 2, item_3)
                self.tableWidget_2.setItem(i, 3, QTableWidgetItem(image_path))
                self.tableWidget_2.setItem(i, 4, QTableWidgetItem(image_name))
                self.tableWidget_2.setItem(i, 5, QTableWidgetItem(json_data))
            
            # self.tableWidget_2.sortItems(0, Qt.DescendingOrder)
            
            if len(results) == 0:
                QMessageBox.warning(self, "검색 결과", "선택한 조건에 맞는 데이터가 없습니다.")
        
        except Exception as e:  # 예외 처리 추가
            QMessageBox.warning(self, "오류", f"데이터를 불러오는 중 오류가 발생했습니다: {str(e)}")

    def open_new_window(self, image_path, image_name, json_data):
        try:
            image = cv2.imread(image_path + image_name)
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

            image_window = ImageWindow(image)
            image_window.show_image()
        
        except AttributeError:
            QMessageBox.warning(self, "오류", "사진이 존재하지 않습니다.")

    def table1_dclicked(self, row, col):
        image_path = self.tableWidget_1.item(row, 6).text()
        image_name = self.tableWidget_1.item(row, 7).text()
        json_data = json.loads(self.tableWidget_1.item(row, 8).text())

        self.open_new_window(image_path, image_name, json_data)

    def table2_dclicked(self, row, col):
        image_path = self.tableWidget_2.item(row, 3).text()
        image_name = self.tableWidget_2.item(row, 4).text()
        json_data = json.loads(self.tableWidget_2.item(row, 5).text())

        self.open_new_window(image_path, image_name, json_data)

    def end_session(self):
        self.close()
        self.show_login()
    
    def show_login(self):
        login_dialog = DrivingScoreSystem.login_gui.LoginDialog()
        if login_dialog.exec_() == QDialog.Accepted:
            self.show()


class ImageWindow(QDialog):
    def __init__(self, image, parent=None):
        super(ImageWindow, self).__init__(parent)
        self.setWindowTitle("Image Viewer")

        # 이미지 QLabel 생성
        label = QLabel(self)
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QPixmap(QPixmap.fromImage(QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()))

        # QLabel에 이미지 설정
        label.setPixmap(q_image)

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
        self.resize(width, height)

    def show_image(self):
        self.exec_()