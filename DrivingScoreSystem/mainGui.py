from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import PyQt5

import sys

import main_gui
import login_gui


def main():
    app = QApplication(sys.argv)

    login_dialog = login_gui.LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        print("login success") 
        main_window = main_gui.WindowClass(login_dialog.isAdmin, login_dialog.name)
        main_window.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()
