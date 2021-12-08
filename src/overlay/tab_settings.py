import keyboard
from PyQt5 import QtCore, QtGui, QtWidgets

from overlay.api_checking import find_player
from overlay.logging_func import get_logger
from overlay.overlay_widget import AoEOverlay
from overlay.settings import settings
from overlay.worker import scheldule

logger = get_logger(__name__)


class CustomKeySequenceEdit(QtWidgets.QKeySequenceEdit):
    key_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(CustomKeySequenceEdit, self).__init__(parent)

    def keyPressEvent(self, QKeyEvent):
        super(CustomKeySequenceEdit, self).keyPressEvent(QKeyEvent)
        value = self.keySequence()
        self.setKeySequence(QtGui.QKeySequence(value))
        self.key_changed.emit(value.toString())


class SettingsTab(QtWidgets.QWidget):
    new_profile = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.overlay_widget = AoEOverlay()
        self.init_UI()

    def init_UI(self):
        # Layout
        self.main_layout = QtWidgets.QGridLayout()
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.main_layout)

        # Profile info
        self.profile_info = QtWidgets.QLabel("No player identified")
        self.profile_info.setStyleSheet("font-weight: bold")
        self.profile_info.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse)
        self.main_layout.addWidget(self.profile_info)

        # Notification
        self.notification_label = QtWidgets.QLabel()
        self.notification_label.hide()
        self.main_layout.addWidget(self.notification_label, 1, 0)

        # Multi search
        self.multi_search = QtWidgets.QLineEdit()
        self.multi_search.setPlaceholderText("Steam ID / Profile ID / Name")
        self.multi_search.setStatusTip(
            'Search for your account with one of these (Steam ID / Profile ID / Name).'
            ' Searching by name might not find the correct player.')
        self.multi_search.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.multi_search.setMaximumWidth(220)
        self.main_layout.addWidget(self.multi_search, 2, 0)

        # Multi search button
        self.multi_search_btn = QtWidgets.QPushButton("Search")
        self.multi_search_btn.clicked.connect(self.find_profile)
        self.multi_search_btn.setShortcut("Return")
        self.multi_search_btn.setStatusTip(
            'Search for your account with one of these (Steam ID / Profile ID / Name).'
            ' Searching by name might not find the correct player.')
        self.main_layout.addWidget(self.multi_search_btn, 2, 1)

        self.main_layout.addItem(QtWidgets.QSpacerItem(0, 20), 3, 0)

        # Hotkey for overlay
        key_label = QtWidgets.QLabel(
            "Add a hotkey for showing or hiding overlay:")
        self.main_layout.addWidget(key_label, 4, 0)

        self.key_showhide = CustomKeySequenceEdit(self)
        self.key_showhide.setMaximumWidth(100)
        self.key_showhide.setStatusTip("Hotkey hiding and showing the overlay")
        self.main_layout.addWidget(self.key_showhide, 4, 1)
        self.key_showhide.key_changed.connect(self.hotkey_changed)

        # Position change button
        self.btn_change_position = QtWidgets.QPushButton(
            "Change/fix overlay position")
        self.btn_change_position.setStatusTip(
            "Click to change overlay position. Click again to fix its position."
        )
        self.btn_change_position.clicked.connect(
            self.overlay_widget.change_state)
        self.main_layout.addWidget(self.btn_change_position, 5, 0)

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
        self.main_layout.addWidget(self.font_size_combo, 5, 1)

        # Create update button
        self.update_button = QtWidgets.QPushButton("New update!")
        self.update_button.setStatusTip(
            "Click here to download new app version")
        self.update_button.setStyleSheet(
            'background-color: #3bb825; color: black')
        self.update_button.hide()
        self.main_layout.addWidget(self.update_button, 6, 0)

    def start(self):
        # Initialize
        self.update_profile_info()

        # Hotkey
        if settings.overlay_hotkey:
            self.key_showhide.setKeySequence(
                QtGui.QKeySequence.fromString(settings.overlay_hotkey))
            keyboard.add_hotkey(settings.overlay_hotkey,
                                self.overlay_widget.show_hide)

        if settings.steam_id or settings.profile_id:
            self.new_profile.emit()

    def update_profile_info(self):
        """ Updates profile information based on found steam_id and profile_id"""
        s = []
        if settings.player_name:
            s.append(settings.player_name)
        if settings.steam_id:
            s.append(f"Steam_id: {settings.steam_id}")
        if settings.profile_id:
            s.append(f"Profile_id: {settings.profile_id}")

        if s:
            self.profile_info.setText('\n'.join(s))
            self.profile_info.setStyleSheet(
                "color: #359c20; font-weight: bold")

    def notification(self, text: str, color: str = "black"):
        """ Shows a notification"""
        self.notification_label.show()
        self.notification_label.setText(text)
        self.notification_label.setStyleSheet(f"color: {color}")

    def find_profile(self):
        """ Attempts to find player ids based on provided text (name, either id)"""
        self.notification_label.hide()
        text = self.multi_search.text().strip()
        if not text:
            return
        logger.info(f"Finding a player with key: {text}")

        scheldule(self.find_profile_finish, find_player, text)

    def find_profile_finish(self, result: bool):
        if result:
            self.new_profile.emit()
            self.update_profile_info()
            self.notification("Player found!", "#359c20")
        else:
            self.notification("Failed to find such player!", "red")

    def font_size_changed(self):
        font_size = self.font_size_combo.currentIndex() + 1
        settings.font_size = font_size
        self.overlay_widget.update_font_size(font_size)

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
