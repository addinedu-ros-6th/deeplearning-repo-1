from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys

from DrivingScoreSystem.login_gui import LoginDialog
from DrivingScoreSystem.main_gui import WindowClass


def main():
    app = QApplication(sys.argv)
 
    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        print("login success") 
        main_window = WindowClass(login_dialog.id, login_dialog.isAdmin, login_dialog.number)
        main_window.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()
