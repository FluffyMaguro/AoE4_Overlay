from turtle import onclick
import pynput
import time

from typing import Any, Dict, List

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QThread

from overlay.aoe4_data import civ_data, map_data, mode_data
from overlay.api_checking import get_leaderboard_data
from overlay.logging_func import get_logger, catch_exceptions
from overlay.settings import settings
from pynput.keyboard import Key, Listener
from pynput.mouse import Listener as MouseListener

logger = get_logger(__name__)


class ApmTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.leaderboard_data: Dict[int, Dict[str, Any]] = {}
        self.match_data: List[Dict[str, Any]] = []
        self.initUI()

    def initUI(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 5)
        self.main_layout.setSpacing(10)
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.main_layout)

        ### Profile box
        profile_box = QtWidgets.QGroupBox("Current APM")
        profile_box.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
            )
        )
        profile_box.setMinimumSize(300, 100)
        profile_box_layout = QtWidgets.QGridLayout()
        profile_box.setLayout(profile_box_layout)
        self.main_layout.addWidget(profile_box)

        self.profile_info = QtWidgets.QLabel("0")
        self.profile_info.setStyleSheet("font-weight: bold")
        self.profile_info.setAlignment(QtCore.Qt.AlignCenter)
        self.profile_info.setFont(QtGui.QFont("Arial", 24))
        self.profile_info.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        profile_box_layout.addWidget(self.profile_info)

        self.start_btn = QtWidgets.QPushButton("Start")
        self.start_btn.clicked.connect(self.start_apm_recording)
        self.start_btn.setShortcut("Enter")
        self.start_btn.setToolTip(
            'Start recording apm')
        profile_box_layout.addWidget(self.start_btn, 2, 1)


        self.stop_btn = QtWidgets.QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_apm_recording)
        self.stop_btn.setShortcut("Esc")
        self.stop_btn.setToolTip(
            'Stop recording apm')
        profile_box_layout.addWidget(self.stop_btn, 2, 2)


    def start_apm_recording(self):
        self.keys = Keys(self.profile_info)
        self.keys.start()

    def stop_apm_recording(self):
        self.keys.stop()

class Keys(QThread):
    def __init__(self, label: QtWidgets.QLabel):
        super().__init__()
        self.action_count = 0
        self.keys = []
        self.label = label
        self.finished = False

    def on_key_press(self, key):
        if self.finished:
            return
        try: 
            print('Key Pressed : ',key)    #Print pressed key   
        except Exception as ex:
            print('There was an error : ',ex)
        self.keys.append(key)    #Store the Keys
        self.action_count += 1      #Count keys pressed
        minutes = (time.time_ns()-self.start)/60000000000
        self.label.setText(str(self.action_count/minutes))

    def on_click(self, x, y, button, pressed):
        if self.finished or not pressed:
            return
        try: 
            print('Mouse click : ', x, y, button, pressed)    #Print pressed key   
        except Exception as ex:
            print('There was an error : ',ex)
        self.keys.append('click')    #Store the Keys
        self.action_count += 1      #Count keys pressed
        minutes = (time.time_ns()-self.start)/60000000000
        self.label.setText(str(self.action_count/minutes))

    def write_to_file(self):
        with open('log.txt','a') as file:
            for key in self.keys:
                key = str(key).replace("'","")   #Replace ' with space
                if 'key'.upper() not in key.upper():
                    file.write(key)
            file.write("\n")    #Insert new line

    def run(self):
        self.start = time.time_ns()
        self.finished = False
        with MouseListener(on_click=self.on_click) as mouse_listener, Listener(on_press=self.on_key_press) as listener:
             mouse_listener.join()
             listener.join()

    def stop(self):
        self.finished = True
        minutes = (time.time_ns()-self.start)/60000000000
        self.label.setText(str(self.action_count/minutes))
        self.write_to_file()
        self.action_count = 0
        self.keys = []
        self.terminate() # TODO this does no actually stop the threads ...
 