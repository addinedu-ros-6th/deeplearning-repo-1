# from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog
from PyQt5.QtCore import QSocketNotifier, QObject
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *

import serial
import time


from_class = uic.loadUiType('./speed_control.ui')[0]

class SpeedControl(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.connect_serial()

        self.btn_apply.clicked.connect(self.apply_speed)
    
    def __del__(self):
        self.ser.close()
    

    def connect_serial(self):
        try:
            self.ser = serial.Serial('/dev/ttyArduino', 9600, timeout=1)
            time.sleep(5)
            
        except:
            pass

    def apply_speed(self):
        speed = self.line_speed.text()
        command = f'F{speed}'.encode()
        self.ser.write(command)