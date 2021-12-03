import webbrowser
from functools import partial
from typing import Any, Dict, Optional

import keyboard
from PyQt5 import QtCore, QtGui, QtWidgets

from overlay.game_checking import API_checker, find_player, validate_steam_id
from overlay.helper_func import version_check
from overlay.logging_func import get_logger
from overlay.overlay_widget import AoEOverlay
from overlay.settings import settings
from overlay.worker import Worker

logger = get_logger(__name__)


def pyqt_wait(miliseconds: int):
    """ Pause executing for `time` in miliseconds"""
    loop = QtCore.QEventLoop()
    QtCore.QTimer.singleShot(miliseconds, loop.quit)
    loop.exec_()


class CustomKeySequenceEdit(QtWidgets.QKeySequenceEdit):
    key_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(CustomKeySequenceEdit, self).__init__(parent)

    def keyPressEvent(self, QKeyEvent):
        super(CustomKeySequenceEdit, self).keyPressEvent(QKeyEvent)
        value = self.keySequence()
        self.setKeySequence(QtGui.QKeySequence(value))
        self.key_changed.emit(value.toString())


class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.threadpool = QtCore.QThreadPool()
        self.api_checker = API_checker()
        self.force_stop = False
        self.overlay_widget = AoEOverlay()
        self.init_UI()
        self.start()

    def init_UI(self):
        # Layout
        self.main_layout = QtWidgets.QGridLayout()
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.main_layout)

        # Current steam_id
        self.profile_info = QtWidgets.QLabel("Current steam ID: None")
        self.profile_info.setStyleSheet("font-weight: bold")
        self.main_layout.addWidget(self.profile_info)

        # Edit steam_id
        self.steam_id_edit = QtWidgets.QLineEdit()
        self.steam_id_edit.setPlaceholderText("Your steam ID")
        self.steam_id_edit.setStatusTip(
            'Steam ID can be found in "Account Details" at the top left')
        self.steam_id_edit.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.steam_id_edit.setMaximumWidth(220)
        self.main_layout.addWidget(self.steam_id_edit, 1, 0)

        # Set steam_id
        set_steam_id_btn = QtWidgets.QPushButton("Set steam ID")
        set_steam_id_btn.setStatusTip("Sets and validates the filled steam ID")
        set_steam_id_btn.setMaximumWidth(100)
        set_steam_id_btn.clicked.connect(self.set_steam_id)
        self.main_layout.addWidget(set_steam_id_btn, 1, 1)

        spacer = QtWidgets.QLabel()
        self.main_layout.addWidget(spacer, 2, 0)

        # Hotkey for overlay
        key_label = QtWidgets.QLabel(
            "Add a hotkey for showing or hiding overlay:")
        self.main_layout.addWidget(key_label, 3, 0)

        self.key_showhide = CustomKeySequenceEdit(self)
        self.key_showhide.setMaximumWidth(100)
        self.main_layout.addWidget(self.key_showhide, 3, 1)
        self.key_showhide.key_changed.connect(self.hotkey_changed)

        # Position change button
        self.btn_change_position = QtWidgets.QPushButton(
            "Change/fix overlay position")
        self.btn_change_position.clicked.connect(
            self.overlay_widget.change_state)
        self.main_layout.addWidget(self.btn_change_position, 4, 0)

        # Overlay font
        font_label = QtWidgets.QLabel("Change overlay font")
        self.main_layout.addWidget(font_label)

        self.font_size_combo = QtWidgets.QComboBox()
        self.font_size_combo.setStatusTip("Overlay font size")
        for i in range(1, 50):
            self.font_size_combo.addItem(f"{i} pt")
        self.font_size_combo.setCurrentIndex(settings.font_size - 1)
        self.font_size_combo.currentIndexChanged.connect(
            self.font_size_changed)
        self.main_layout.addWidget(self.font_size_combo, 4, 1)

        # Create update button
        self.update_button = QtWidgets.QPushButton("New update!")
        self.update_button.setStatusTip(
            "Click here to download new app version")
        self.update_button.setStyleSheet(
            'background-color: #3bb825; color: black')
        self.update_button.hide()
        self.main_layout.addWidget(self.update_button, 5, 0)

        # Multi search
        self.multi_search = QtWidgets.QLineEdit()
        self.multi_search.setPlaceholderText("Steam ID / profile ID / Name")
        self.multi_search.setStatusTip(
            'Search for your account with one option')
        self.multi_search.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.multi_search.setMaximumWidth(220)
        self.main_layout.addWidget(self.multi_search, 6, 0)

        # Multi search button
        self.multi_search_btn = QtWidgets.QPushButton("Search")
        self.multi_search_btn.clicked.connect(self.find_profile)
        self.main_layout.addWidget(self.multi_search_btn, 6, 1)

    def find_profile(self):
        text = self.multi_search.text()
        find_player(text)
        print("finding with", text)

    def font_size_changed(self):
        font_size = self.font_size_combo.currentIndex() + 1
        settings.font_size = font_size
        self.overlay_widget.update_font_size(font_size)

    def start(self):
        # Load config and initialize
        if validate_steam_id(settings.steam_id):
            logger.info("steam_id loaded and is valid")
            self.api_checker.steam_id = settings.steam_id
            self.steam_id_edit.setText(str(settings.steam_id))
            self.update_profile_info(valid=True, steam_id=settings.steam_id)

        # Hotkey
        if settings.overlay_hotkey:
            self.key_showhide.setKeySequence(
                QtGui.QKeySequence.fromString(settings.overlay_hotkey))
            keyboard.add_hotkey(settings.overlay_hotkey,
                                self.overlay_widget.show_hide)

        # self.run_check()
        # DEBUG FOR VISUAL CHANGES
        self.overlay_widget.update_data({
            'lobby_id':
            '109775240919138141',
            'map_size':
            3,
            'map_type':
            9,
            'match_id':
            '12595190',
            'name':
            'AUTOMATCH',
            'num_players':
            6,
            'num_slots':
            6,
            'players': [{
                'civ': 4,
                'clan': None,
                'color': None,
                'country': None,
                'losses': 5,
                'name': 'Mini-Negan',
                'profile_id': 5636932,
                'rank': 12570,
                'rating': 1105,
                'rating_change': None,
                'slot': 1,
                'slot_type': 1,
                'streak': -1,
                'team': 1,
                'wins': 8,
                'won': None
            }, {
                'civ': 5,
                'clan': None,
                'color': None,
                'country': None,
                'name': 'Iotawolf101',
                'profile_id': 181552,
                'rating': None,
                'rating_change': None,
                'slot': 3,
                'slot_type': 1,
                'team': 1,
                'won': None
            }, {
                'civ': 1,
                'clan': None,
                'color': None,
                'country': None,
                'losses': 8,
                'name': 'Maguro',
                'profile_id': 5233600,
                'rank': 17708,
                'rating': 1063,
                'rating_change': None,
                'slot': 2,
                'slot_type': 1,
                'streak': 1,
                'team': 1,
                'wins': 9,
                'won': None
            }, {
                'civ': 3,
                'clan': None,
                'color': None,
                'country': None,
                'losses': 5,
                'name': 'Kanax',
                'profile_id': 6703549,
                'rank': 27902,
                'rating': 990,
                'rating_change': None,
                'slot': 4,
                'slot_type': 1,
                'streak': -2,
                'team': 2,
                'wins': 5,
                'won': None
            }, {
                'civ': 5,
                'clan': None,
                'color': None,
                'country': None,
                'losses': 62,
                'name': 'lebowskiiiiiiiii',
                'profile_id': 684531,
                'rank': 29512,
                'rating': 979,
                'rating_change': None,
                'slot': 5,
                'slot_type': 1,
                'streak': -1,
                'team': 2,
                'wins': 54,
                'won': None
            }, {
                'civ': 6,
                'clan': None,
                'color': None,
                'country': None,
                'name': 'gcdomi7872',
                'profile_id': 5971541,
                'rating': None,
                'rating_change': None,
                'slot': 6,
                'slot_type': 1,
                'team': 2,
                'won': None
            }],
            'ranked':
            False,
            'rating_type_id':
            17,
            'server':
            'ukwest',
            'started':
            1638493446,
            'version':
            '8324'
        })
        # DEBUG END

    def hotkey_changed(self, new_hotkey: str):
        """ Checks whether the hotkey is actually new and valid.
        Updates keyboard threads"""
        if new_hotkey == "Del":
            self.key_showhide.setKeySequence(
                QtGui.QKeySequence.fromString(None))
            return
        elif not new_hotkey or new_hotkey == settings.overlay_hotkey:
            return

        logger.info(f"Setting new hotkey to: {new_hotkey}")
        if settings.overlay_hotkey:
            keyboard.remove_hotkey(settings.overlay_hotkey)
        settings.overlay_hotkey = new_hotkey
        keyboard.add_hotkey(settings.overlay_hotkey,
                            self.overlay_widget.show_hide)

    def stop_checking_api(self):
        """ The app is closing, we need to start shuttings things down"""
        self.force_stop = True
        self.api_checker.force_stop = True

    def got_new_game(self, game_data: Optional[Dict[str, Any]]):
        """Received new data from api check, passes data along and reruns the check"""
        if self.force_stop:
            return

        if game_data is not None:
            self.overlay_widget.update_data(game_data)

        self.run_check(delayed_seconds=30)

    def run_check(self, delayed_seconds: int = 0):
        """ Creates a new thread for a new api check"""
        thread_check = Worker(self.api_checker.check_for_new_game,
                              delayed_seconds)
        thread_check.signals.result.connect(self.got_new_game)
        self.threadpool.start(thread_check)

    def update_profile_info(self, valid: bool, steam_id="None"):
        """ Update labels for steam id label"""
        self.profile_info.setText(f"Valid steam ID: {steam_id}")
        if valid:
            self.profile_info.setStyleSheet(
                "color: #359c20; font-weight: bold")
        else:
            self.profile_info.setStyleSheet("")
            self.steam_id_edit.setPlaceholderText("Invalid steam ID!")
            self.steam_id_edit.setText("")

    def set_steam_id(self):
        """ Checks whether the steam_id is valid, updates config, labels and api checker"""
        try:
            steam_id = int(self.steam_id_edit.text())
        except ValueError:
            logger.warning(f"Invalid steam_id: {self.steam_id_edit.text()}")
            self.update_profile_info(valid=False)
            return

        # Validate steam_id
        if not validate_steam_id(steam_id):
            logger.warning(f"Invalid steam ID: {self.steam_id_edit.text()}")
            self.update_profile_info(valid=False)
            return

        # Save to config
        settings.steam_id = steam_id

        # Update label
        self.update_profile_info(valid=True, steam_id=steam_id)

        # Update/run search
        self.api_checker.steam_id = steam_id

    def check_for_new_version(self, version: str):
        """ Checks for a new version, creates a button if there is one """
        link = version_check(version)
        if not link:
            return
        logger.info("New version available!")
        self.update_button.clicked.connect(partial(webbrowser.open, link))
        self.update_button.show()
