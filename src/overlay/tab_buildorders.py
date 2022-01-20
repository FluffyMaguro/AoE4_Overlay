import keyboard
from PyQt5 import QtCore, QtGui, QtWidgets

from overlay.custom_widgets import CustomKeySequenceEdit, OverlayWidget
from overlay.logging_func import get_logger
from overlay.settings import settings

logger = get_logger(__name__)


class Buildorder_overlay(OverlayWidget):
    """Overlay widget showing buildorders """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_overlay()
        self.initUI()

    def setup_overlay(self):
        if settings.bo_overlay_geometry is None:
            self.setGeometry(0, 0, 300, 200)
            sg = QtWidgets.QDesktopWidget().screenGeometry(0)
            self.move(sg.width() - self.width() + 15, sg.top() + 400)
        else:
            self.setGeometry(*settings.bo_overlay_geometry)
        self.setWindowTitle('AoE IV: Buildorder Overlay')

    def initUI(self):
        mlayout = QtWidgets.QHBoxLayout()
        mlayout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(mlayout)

        # Frame for background and resizing
        frame = QtWidgets.QFrame()
        mlayout.addWidget(frame)
        frame.setObjectName("inner_frame")
        flayout = QtWidgets.QVBoxLayout()
        flayout.setAlignment(QtCore.Qt.AlignTop)
        flayout.setContentsMargins(15, 5, 5, 5)
        frame.setLayout(flayout)

        # Set size policy so frame uses minimum height
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Maximum)
        frame.setSizePolicy(sizePolicy)

        self.title = QtWidgets.QLabel()
        self.title.setObjectName("botitle")
        self.title.setWordWrap(True)
        if not settings.bo_showtitle:
            self.title.hide()

        flayout.addWidget(self.title)

        self.text = QtWidgets.QLabel()
        self.text.setWordWrap(True)
        flayout.addWidget(self.text)

        self.update_style(settings.bo_font_size)

    def update_data(self, title: str, text: str):
        self.title.setText(title)
        self.text.setText(text)

    def update_style(self, font_size: int):
        self.setStyleSheet(
            f"QLabel {{font-size: {font_size}pt; color: white }}"
            f"QLabel#botitle {{font-size: {font_size + 2}pt;"
            f"font-weight: bold; color: {settings.bo_title_color}}}"
            "QFrame#inner_frame {"
            "background: QLinearGradient("
            "x1: 0, y1: 0,"
            "x2: 1, y2: 0,"
            "stop: 0 rgba(0,0,0,0),"
            f"stop: 0.1 rgba(0,0,0,{max(settings.bo_bg_opacity - 0.1, 0)}),"
            f"stop: 0.98 rgba(0,0,0,{settings.bo_bg_opacity}),"
            "stop: 1 rgba(0,0,0,0))}")

        # Updates style (prevents ghosting)
        if self.isVisible():
            self.show()

    def save_geometry(self):
        """ Saves overlay geometry into settings"""
        pos = self.pos()
        settings.bo_overlay_geometry = [
            pos.x(), pos.y(), self.width(),
            self.height()
        ]


class BoTab(QtWidgets.QWidget):
    show_hide_overlay = QtCore.pyqtSignal()
    cycle_buildorder = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.overlay = Buildorder_overlay()
        self.initUI()
        self.init_hotkeys()

        # Connect signals
        self.show_hide_overlay.connect(self.overlay.show_hide)
        self.cycle_buildorder.connect(self.cycle_overlay)

        self.update_overlay()

    def init_hotkeys(self):
        if settings.bo_overlay_hotkey_show:
            self.key_showhide.setKeySequence(
                QtGui.QKeySequence.fromString(settings.bo_overlay_hotkey_show))
            keyboard.add_hotkey(settings.bo_overlay_hotkey_show,
                                self.show_hide_overlay.emit)

        if settings.bo_overlay_hotkey_cycle:
            self.key_cycle.setKeySequence(
                QtGui.QKeySequence.fromString(
                    settings.bo_overlay_hotkey_cycle))
            keyboard.add_hotkey(settings.bo_overlay_hotkey_cycle,
                                self.cycle_buildorder.emit)

    def initUI(self):
        hlayout = QtWidgets.QHBoxLayout()
        self.setLayout(hlayout)

        # Text edit field
        self.edit = QtWidgets.QTextEdit()
        hlayout.addWidget(self.edit)

        ### Buildorder controls
        controls = QtWidgets.QFrame()
        controls.setMaximumWidth(350)
        clayout = QtWidgets.QVBoxLayout()
        clayout.setContentsMargins(0, 0, 0, 0)
        controls.setLayout(clayout)
        hlayout.addWidget(controls)

        # Renaming buildorders
        self.rename_widget = QtWidgets.QLineEdit()
        self.rename_widget.setToolTip("Rename buildorder here")
        self.rename_widget.setTextMargins(3, 0, 0, 0)
        clayout.addWidget(self.rename_widget)

        # Buildorder list
        self.bo_list = QtWidgets.QListWidget()
        clayout.addWidget(self.bo_list)
        for name in settings.buildorders:
            self.bo_list.addItem(name)
        self.bo_list.currentItemChanged.connect(self.bo_selected)
        self.bo_list.setCurrentRow(0)

        # Add buildorders
        add_bo_btn = QtWidgets.QPushButton("Add build order")
        add_bo_btn.clicked.connect(self.add_buildorder)
        clayout.addWidget(add_bo_btn)

        # Remove buildorder
        remove_bo_btn = QtWidgets.QPushButton("Remove build order")
        remove_bo_btn.clicked.connect(self.remove_buildorder)
        clayout.addWidget(remove_bo_btn)

        clayout.addSpacing(40)

        ### Overlay controls
        overlay_box = QtWidgets.QGroupBox("Overlay")
        overlay_layout = QtWidgets.QGridLayout()
        overlay_box.setLayout(overlay_layout)
        clayout.addWidget(overlay_box)

        # Show/hide hotkey
        key_label = QtWidgets.QLabel("Hotkey for showing and hiding overlay:")
        overlay_layout.addWidget(key_label, 0, 0)

        self.key_showhide = CustomKeySequenceEdit(self)
        self.key_showhide.setMaximumWidth(100)
        self.key_showhide.setToolTip("Hotkey for showing and hiding overlay")
        overlay_layout.addWidget(self.key_showhide, 0, 1)
        self.key_showhide.key_changed.connect(self.show_hotkey_changed)

        # Cycle hotkey
        key_label = QtWidgets.QLabel("Hotkey for cycling buildorders:")
        overlay_layout.addWidget(key_label, 1, 0)

        self.key_cycle = CustomKeySequenceEdit(self)
        self.key_cycle.setMaximumWidth(100)
        self.key_cycle.setToolTip("Hotkey for cycling buildorders")
        overlay_layout.addWidget(self.key_cycle, 1, 1)
        self.key_cycle.key_changed.connect(self.cycle_hotkey_changed)

        # Overlay font
        font_label = QtWidgets.QLabel("Overlay font size:")
        overlay_layout.addWidget(font_label, 2, 0)

        self.font_size_combo = QtWidgets.QComboBox()
        for i in range(1, 50):
            self.font_size_combo.addItem(f"{i} pt")
        self.font_size_combo.setCurrentIndex(settings.bo_font_size - 1)
        self.font_size_combo.currentIndexChanged.connect(
            self.font_size_changed)
        overlay_layout.addWidget(self.font_size_combo, 2, 1)

        # Position change button
        self.btn_change_position = QtWidgets.QPushButton(
            "Change/fix overlay position")
        self.btn_change_position.setToolTip(
            "Click to change overlay position. Click again to fix its position."
        )
        self.btn_change_position.clicked.connect(self.overlay.change_state)
        overlay_layout.addWidget(self.btn_change_position, 3, 0, 1, 2)

    def save_current_bo(self):
        bo_name = self.bo_list.currentItem().text()
        bo_text = self.edit.toPlainText()
        settings.buildorders[bo_name] = bo_text
        self.update_overlay()

    def bo_selected(self, item: QtWidgets.QListWidgetItem):
        # Try disconnecting signals (throws an error when nothing connected)
        try:
            self.edit.disconnect()
        except TypeError:
            pass
        try:
            self.rename_widget.disconnect()
        except TypeError:
            pass

        # Change values
        self.rename_widget.setText(item.text())
        self.edit.setText(settings.buildorders.get(item.text(), ""))
        self.update_overlay()

        # Reconnect signals
        self.edit.textChanged.connect(self.save_current_bo)
        self.rename_widget.textChanged.connect(self.name_changed)

    def name_changed(self, text: str):
        self.bo_list.currentItem().setText(text)

        # Remove the old buildorder
        rows = self.bo_list.count()
        bo_names = {self.bo_list.item(i).text() for i in range(rows)}
        for name in settings.buildorders:
            if name not in bo_names:
                del settings.buildorders[name]
                break

        # Add the new buildorder
        self.save_current_bo()

    def add_buildorder(self):
        self.bo_list.addItem(f"Buildorder {self.bo_list.count() + 1}")
        self.bo_list.setCurrentRow(self.bo_list.count() - 1)
        self.save_current_bo()

    def remove_buildorder(self):
        if self.bo_list.count() == 1:
            return
        del settings.buildorders[self.bo_list.currentItem().text()]
        self.bo_list.takeItem(self.bo_list.currentRow())

    def font_size_changed(self, font_index: int):
        settings.bo_font_size = font_index + 1
        self.overlay.update_style(font_index + 1)

    def show_hotkey_changed(self, new_hotkey: str):
        """ Checks whether the hotkey is actually new and valid.
        Updates keyboard threads"""
        new_hotkey = new_hotkey.replace("Num+", "")

        if new_hotkey == "Del":
            self.key_showhide.setKeySequence(QtGui.QKeySequence.fromString(""))
            settings.bo_overlay_hotkey_show = ""
            return
        elif not new_hotkey or new_hotkey == settings.bo_overlay_hotkey_show:
            return

        if settings.bo_overlay_hotkey_show:
            keyboard.remove_hotkey(settings.bo_overlay_hotkey_show)
        logger.info(f"Setting new buildorder show hotkey to: {new_hotkey}")
        settings.bo_overlay_hotkey_show = new_hotkey
        keyboard.add_hotkey(new_hotkey, self.show_hide_overlay.emit)

    def cycle_hotkey_changed(self, new_hotkey: str):
        """ Checks whether the hotkey is actually new and valid.
        Updates keyboard threads"""
        new_hotkey = new_hotkey.replace("Num+", "")

        if new_hotkey == "Del":
            self.key_cycle.setKeySequence(QtGui.QKeySequence.fromString(""))
            settings.bo_overlay_hotkey_cycle = ""
            return
        elif not new_hotkey or new_hotkey == settings.bo_overlay_hotkey_cycle:
            return

        if settings.bo_overlay_hotkey_cycle:
            keyboard.remove_hotkey(settings.bo_overlay_hotkey_cycle)
        logger.info(f"Setting new buildorder cycle hotkey to: {new_hotkey}")
        settings.bo_overlay_hotkey_cycle = new_hotkey
        keyboard.add_hotkey(new_hotkey, self.cycle_buildorder.emit)

    def update_overlay(self):
        """Send new data to the overlay"""
        if self.bo_list.count():
            bo_name = self.bo_list.currentItem().text()
            bo_text = self.edit.toPlainText()
            self.overlay.update_data(bo_name, bo_text)

    def cycle_overlay(self):
        """ Cycles through buildorders and sends data to the overlay"""
        # Update widget (move to higher row)
        count = self.bo_list.count()
        # This also automatically update overlay
        self.bo_list.setCurrentRow((self.bo_list.currentRow() + 1) % count)
        self.overlay.show()
