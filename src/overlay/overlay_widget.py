from PyQt5 import QtCore, QtGui, QtWidgets


class PlayerWidget(QtWidgets.QWidget):
    """ Player widget shown on the overlay"""
    def __init__(self):
        super().__init__()

        self.name = QtWidgets.QLabel("sfsdfdsfd", self)


class AoEOverlay(QtWidgets.QWidget):
    """Overlay widget showing AOE4 information """
    def __init__(self):
        super().__init__()

        self.setGeometry(0, 0, 600, 600)
        sg = QtWidgets.QDesktopWidget().screenGeometry(0)
        self.move(sg.width() - self.width() - 10, sg.top() + 10)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint
                            | QtCore.Qt.WindowTransparentForInput
                            | QtCore.Qt.WindowStaysOnTopHint
                            | QtCore.Qt.CoverWindow
                            | QtCore.Qt.NoDropShadowWindowHint
                            | QtCore.Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self.playerlayout = QtWidgets.QVBoxLayout()
        self.playerlayout.setAlignment(QtCore.Qt.AlignTop)
        self.playerlayout.setVerticalSpacing(2)
        self.setLayout(self.playerlayout)

        self.test = QtWidgets.QLabel("sfsdfdsfd", self)

    def add_players(self):
        ...
