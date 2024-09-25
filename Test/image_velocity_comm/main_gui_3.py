# from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog
from PyQt5.QtCore import QSocketNotifier, QObject
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import cv2
import mysql

import sys 
import socket
import struct
import pickle

from inference_2_2 import Inference
from judge_2 import Judge

import login_gui

'''
TODO
- 소켓, DB 재연결 버튼 만들기
- illegalJudge 만들기
- log 기록용 json형식 반환하기
- 어보 빨간색 도로 처리하기
- 
'''

from_class = uic.loadUiType('/home/jh/dev_ws/temp/dl_gui.ui')[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self, isAdmin, name):
        super().__init__()
        self.setupUi(self)

        self.username = name
        self.user_name.setText(name)

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
        self.btn_robot.clicked.connect(self.socket_configuration)
        self.btn_DB.clicked.connect(self.db_configuration)

        # 점수 차감
        self.judge = Judge()

        self.score = 100
        self.LCD_score.display(self.score)

        self.penalty = 0
        self.speed = 0

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
        self.port = 1155

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
#============================================

        frame_data = self.data[:msg_size]
        self.data = self.data[msg_size:]

        count = struct.unpack("I", frame_data[:4])[0]
        frame_data = frame_data[4:]

        # 프레임을 역직렬화
        frame, velocity = pickle.loads(frame_data)

        # 프레임 크기 조정
        frame = cv2.resize(frame, (640, 480))

        # 수신한 count 값 출력
        print("Received count:", count)

        self.show_frame(frame)
        print(count,velocity)
        return count, frame, velocity
    
    def show_frame(self, frame):
        frame, detects, cls_set = self.model.predict(frame)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, c = frame.shape
        qimage = QImage(frame.data, w, h, w*c, QImage.Format_RGB888)
        self.pixmap_monitor = QPixmap.fromImage(qimage)
        self.pixmap_monitor = self.pixmap_monitor.scaled(self.label.width(), self.label.height())
        self.label.setPixmap(self.pixmap_monitor)

        # 점수 차감
        self.charge, self.penalty = self.judge.verdict(detects, cls_set)

        if self.penalty:
            self.score -= self.penalty
            self.LCD_score.display(self.score)
            self.label_lastPenalty.setText("-" + str(self.penalty))


    
    def end_session(self):
        self.close()
        self.show_login()
    
    def show_login(self):
        login_dialog = login_gui.LoginDialog()
        if login_dialog.exec_() == QDialog.Accepted:
            self.show()


