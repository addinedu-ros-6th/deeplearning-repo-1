from PyQt5 import QtWidgets, uic
import mysql.connector
from PyQt5.QtWidgets import QMessageBox

import os

# MySQL 연결 정보
db_config = {
    'host': 'database-1.cpog6osggiv3.ap-northeast-2.rds.amazonaws.com',
    'user': 'arduino_PJT',
    'password': '1234',
    'database': 'ardumension'
}

# 로그인 창 클래스
class LoginDialog(QtWidgets.QDialog):
    def __init__(self):
        super(LoginDialog, self).__init__()
        uic.loadUi("./ui/login_gui.ui", self)
        self.login_button.clicked.connect(self.handle_login)

        self.isAdmin = False
        self.name = ""

        self.path_user = "./pictures/user_log/"
        self.path_admin = "./pictures/admin_log/"

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # MySQL 연결
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            query = "SELECT * FROM UserData WHERE login_id=%s AND password=%s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()

            if result:
                self.id, _, self.isAdmin, self.number, _ = result

                # 유저마다 다른 폴더 만들어서 사진 저장
                admin_pic_dir = self.path_admin + self.number
                user_pic_dir = self.path_user + self.number
                if not os.path.exists(admin_pic_dir):
                    os.makedirs(admin_pic_dir)
                if not os.path.exists(user_pic_dir):
                    os.makedirs(user_pic_dir)

                QMessageBox.information(self, "Success", "Login successful!")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Invalid username or password!")

            cursor.close()
            conn.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Error: {err}")
