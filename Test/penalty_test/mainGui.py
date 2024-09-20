from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import PyQt5

import sys

# import login_gui
# import main_gui_2
from login_gui import LoginDialog
from main_gui_3 import WindowClass


def main():
    app = QApplication(sys.argv)

    # login_dialog = login_gui.LoginDialog()
    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        print("login success") 
        # main_window = main_gui_2.WindowClass(login_dialog.isAdmin, login_dialog.name)
        main_window = WindowClass(login_dialog.isAdmin, login_dialog.name)
        main_window.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()
