import sys
from PyQt5 import QtWidgets, uic
import mysql.connector
from PyQt5.QtWidgets import QMessageBox

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
        uic.loadUi("./Vehicle_Gui/login_gui.ui", self)  # login.ui 파일을 로드합니다.
        self.login_button.clicked.connect(self.handle_login)

        self.isAdmin = False
        self.name = ""

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # MySQL 연결
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            query = "SELECT * FROM login_info WHERE username=%s AND password=%s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()

            if result:
                _, _, _, self.isAdmin, self.name = result
                QMessageBox.information(self, "Success", "Login successful!")
                self.accept()  # 로그인 성공 시 창을 닫음
            else:
                QMessageBox.warning(self, "Error", "Invalid username or password!")

            cursor.close()
            conn.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Error: {err}")
