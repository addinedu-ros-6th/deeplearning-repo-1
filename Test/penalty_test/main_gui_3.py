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
'''

from_class = uic.loadUiType('/home/sh/dev_ws/test22/dl_gui.ui')[0]

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

        # # 소켓 설정 (기능이 없다면 주석 처리)
        # self.socket_configuration()

        # self.data = b""
        # self.payload_size = struct.calcsize("Q")

        # QSocketNotifier 설정 (읽기 가능할 때 알림 받음)
        # self.socket_notifier = QSocketNotifier(self.client_socket.fileno(), QSocketNotifier.Read)
        # self.socket_notifier.activated.connect(self.read_data)

        # DB 설정
        self.db_configuration()

        # 추론 객체
        self.model = Inference()

        # 버튼
        self.btn_logout.clicked.connect(self.end_session)
        
        # self.btn_robot.clicked.connect(self.socket_configuration)  # 주석 처리
        self.btn_DB.clicked.connect(self.db_configuration)

        self.btn_logout_2.clicked.connect(self.process_next_frame)

        # 점수 차감
        self.judge = Judge()

        self.score = 100
        self.LCD_score.display(self.score)

        self.penalty = 0
        self.speed = 30
        self.LCD_speed.display(self.speed)

        self.video_path = '/home/sh/dev_ws/test/validation_video/test_06.mp4'  # 여기에 실제 비디오 파일 경로를 입력하세요
        self.cap = cv2.VideoCapture(self.video_path)

        # 타이머 설정
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_frame)
        # self.timer.start(100)  # 40ms마다 프레임 업데이트 (약 25 FPS)

    def __del__(self):
        try:
            if hasattr(self, 'cap'):
                self.cap.release()
            if hasattr(self, 'client_socket'):
                self.client_socket.close()
            if hasattr(self, 'cursor'):
                self.cursor.close()
            if hasattr(self, 'conn'):
                self.conn.close()
        except Exception as e:
           pass # print(f"Error in __del__: {e}")

    def show_admin_tab(self):
        self.Controll.insertTab(self.admin_tab_index, self.admin_tab_widget, "Object_Log")

    def hide_admin_tab(self):
        self.Controll.removeTab(self.admin_tab_index)



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

    
    def process_next_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (640, 480))
            self.show_frame(frame)
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 비디오가 끝나면 처음으로 돌아감

    def show_frame(self, frame):
        try:
            frame, detects, cls_set = self.model.predict(frame)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, c = frame.shape
            qimage = QImage(frame.data, w, h, w * c, QImage.Format_RGB888)
            self.pixmap_monitor = QPixmap.fromImage(qimage)
            self.pixmap_monitor = self.pixmap_monitor.scaled(self.label.width(), self.label.height())
            self.label.setPixmap(self.pixmap_monitor)

            # 점수 차감
            self.charge, self.penalty = self.judge.verdict(detects, cls_set)
            if self.penalty:
                self.score -= self.penalty
                self.LCD_score.display(self.score)
                self.label_lastPenalty.setText("-" + str(self.penalty))
        except Exception as e:
            print(f"Error in show_frame: {e}")

    def end_session(self):
        self.close()
        self.show_login()

    def show_login(self):
        login_dialog = login_gui.LoginDialog()
        if login_dialog.exec_() == QDialog.Accepted:
            self.show()
