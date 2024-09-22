from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog
from PyQt5.QtCore import QSocketNotifier, QObject
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

        # 버튼
        self.btn_logout.clicked.connect(self.end_session)
        self.btn_search_1.clicked.connect(self.load_user_db)
        self.btn_search_2.clicked.connect(self.load_admin_db)

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
        self.host = '172.30.1.33'
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
    
    def socket_configuration_sectionSpeedReader(self, timeout=1):
        self.host_2 = '172.30.1.76'
        self.port_2 = 3333

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
            QMessageBox.critical(self, "Error", f"Error: {err}")

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
                self.file_name = self.car_number + '_' + self.now + '_' + str(count)
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
                print(f"Received data: {self.section_speed}")
            else:
                pass

        except ConnectionError as e:
            print(f"Connection error: {e}")
            
    def show_frame(self, frame):
        try:
            frame, detects, cls_set = self.model.predict(frame)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, c = frame.shape
            qimage = QImage(frame.data, w, h, w*c, QImage.Format_RGB888)
            self.pixmap_monitor = QPixmap.fromImage(qimage)
            self.pixmap_monitor = self.pixmap_monitor.scaled(self.label.width(), self.label.height())
            self.label.setPixmap(self.pixmap_monitor)

            # 점수 차감
            self.charge_id, self.penalty, detected_classes, self.is_new_object, self.new_object  = self.judge.verdict(detects, cls_set, self.velocity, self.section_speed)
            self.update_label(detected_classes)

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
                self.upload_new_object_data(e)
                cv2.imwrite(self.path_admin+self.file_name, frame)

        except Exception as e:
            print(f"Error in show_frame: {e}")
    
    def upload_penalty_data(self):
        insert = f"insert into PenaltyLog values ({self.now}, {self.user_id}, {self.charge_id}, {self.velocity})"
        self.cursor.execute(insert)
    
    def upload_new_object_data(self, _object):
        insert = f"insert into ObjectLog values ({self.now}, {_object}, {self.car_number}, {self.path_admin}, {self._json}, {self.file_name})"
        self.cursor.execute(insert)

    def update_label(self, detected_classes):
        # set 데이터를 문자열로 변환하여 표시 (콤마로 구분)
        label_text = ",\n".join(detected_classes)
        self.label_status_desc.setText(f"Detected Classes: {label_text}")
    
    def load_user_db(self):
        query = f"select "
    
    def load_admin_db(self):
        pass

    def end_session(self):
        self.close()
        self.show_login()
    
    def show_login(self):
        login_dialog = login_gui.LoginDialog()
        if login_dialog.exec_() == QDialog.Accepted:
            self.show()


