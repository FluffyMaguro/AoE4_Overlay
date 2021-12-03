import os

from PyQt5 import QtCore, QtGui, QtWidgets

from overlay.game_checking import API_checker, validate_steam_id
from overlay.helper_func import load_config, save_config
from overlay.logging_func import get_logger
from overlay.worker import Worker

logger = get_logger(__name__)


class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.threadpool = QtCore.QThreadPool()
        self.api_checker = API_checker()
        self.force_stop = False

        # Layout
        main_layout = QtWidgets.QGridLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(main_layout)

        # Current steam_id
        self.current_steam_id = QtWidgets.QLabel("Current steam id: None")
        self.current_steam_id.setStyleSheet("font-weight: bold")
        main_layout.addWidget(self.current_steam_id)

        # Edit steam_id
        self.steam_id_edit = QtWidgets.QLineEdit()
        self.steam_id_edit.setPlaceholderText("Your steam id")
        self.steam_id_edit.setStatusTip(
            'Steam ID can be found in "Account Details" at the top left')
        self.steam_id_edit.setMaximumWidth(200)
        main_layout.addWidget(self.steam_id_edit, 1, 0)

        # Set steam_id
        set_steam_id_btn = QtWidgets.QPushButton("Set steam id")
        set_steam_id_btn.setStatusTip("aaaaaaaaa")
        set_steam_id_btn.setMaximumWidth(100)
        set_steam_id_btn.clicked.connect(self.set_steam_id)
        main_layout.addWidget(set_steam_id_btn, 1, 1)

        # Load config and initialize
        config = load_config()
        if "steam_id" in config and validate_steam_id(config['steam_id']):
            logger.info("steam_id is valid")
            self.api_checker.steam_id = config['steam_id']
            self.steam_id_edit.setText(str(config['steam_id']))
            self.update_labels(valid=True, steam_id=config['steam_id'])

        self.run_check()

    def run_check(self, delayed_seconds: int = 0):
        thread_check = Worker(self.api_checker.check_for_new_game,
                              delayed_seconds)
        thread_check.signals.result.connect(self.got_new_game)
        self.threadpool.start(thread_check)

    def stop_check(self):
        self.force_stop = True
        self.api_checker.force_stop = True

    def got_new_game(self, *args):
        print("RESULT:", args)
        if not self.force_stop:
            self.run_check(delayed_seconds=30)

    def update_labels(self, valid, steam_id="None"):
        self.current_steam_id.setText(f"Current steam id: {steam_id}")
        if valid:
            self.current_steam_id.setStyleSheet(
                "color: green; font-weight: bold")
        else:
            self.current_steam_id.setStyleSheet("")
            self.steam_id_edit.setPlaceholderText("Invalid steam id!")
            self.steam_id_edit.setText("")

    def set_steam_id(self):
        try:
            steam_id = int(self.steam_id_edit.text())
        except ValueError:
            logger.warning(f"Invalid steam_id: {self.steam_id_edit.text()}")
            self.update_labels(valid=False)
            return

        # Validate steam_id
        if not validate_steam_id(steam_id):
            logger.warning(f"Invalid steam id: {self.steam_id_edit.text()}")
            self.update_labels(valid=False)
            return

        # Save to config
        save_config({"steam_id": steam_id})

        # Update label
        self.update_labels(valid=True, steam_id=steam_id)

        # Update/run search
        self.api_checker.steam_id = steam_id
