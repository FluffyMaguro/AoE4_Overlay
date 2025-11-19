from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt


class CustomKeySequenceEdit(QtWidgets.QKeySequenceEdit):
    key_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(CustomKeySequenceEdit, self).__init__(parent)

    def keyPressEvent(self, QKeyEvent):
        super(CustomKeySequenceEdit, self).keyPressEvent(QKeyEvent)
        value = self.keySequence()
        self.setKeySequence(QtGui.QKeySequence(value))
        self.key_changed.emit(value.toString())

    @staticmethod
    def convert_hotkey(hotkey: str) -> str:
        """ Converts hotkey to the format usable by the keyboard module"""
        replace_dict = {
            "Num+": "",
            "scrolllock": 'scroll lock',
            "ScrollLock": 'scroll lock'
        }
        for item, nitem in replace_dict.items():
            hotkey = hotkey.replace(item, nitem)
        return hotkey

    def get_hotkey_string(self) -> str:
        """ Returns the hotkey string usable by the keyboard module"""
        return self.convert_hotkey(self.keySequence().toString())


class VerticalLabel(QtWidgets.QLabel):
    def __init__(self, text: str, color: QtGui.QColor, min_width: int = 20):
        super().__init__()
        self.setMinimumWidth(min_width)
        self.textlabel = text
        self.color = color

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(self.color)
        painter.rotate(-90)
        rect = QtCore.QRect(-self.height(), 0, self.height(), self.width())
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                         self.textlabel)
        painter.end()


class OverlayWidget(QtWidgets.QWidget):
    """Custom overlay widget"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fixed: bool = True
        self.set_state(translucent=True)

    def __post_init__(self):
        self.old_pos: QtCore.QPoint = self.pos()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        """ Override used for window dragging"""
        self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        """ Override used for window dragging"""
        delta = QtCore.QPoint(event.globalPosition().toPoint() - self.old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPosition().toPoint()

    def show_hide(self):
        self.hide() if self.isVisible() else self.show()

    def save_geometry(self):
        ...

    def set_state(self, translucent: bool):
        if translucent:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                                | Qt.WindowType.WindowTransparentForInput
                                | Qt.WindowType.WindowStaysOnTopHint
                                | Qt.WindowType.CoverWindow
                                | Qt.WindowType.NoDropShadowWindowHint
                                | Qt.WindowType.WindowDoesNotAcceptFocus)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        else:
            self.setWindowFlags(Qt.WindowType.Window
                                | Qt.WindowType.CustomizeWindowHint
                                | Qt.WindowType.WindowTitleHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

    def change_state(self):
        """ Changes the widget to be movable or not"""
        self.show()
        pos = self.pos()
        if self.fixed:
            self.fixed = False
            self.set_state(translucent=False)
            self.move(pos.x() - 8, pos.y() - 31)
        else:
            self.fixed = True
            self.set_state(translucent=True)
            self.move(pos.x() + 8, pos.y() + 31)
            self.save_geometry()
        self.show()
