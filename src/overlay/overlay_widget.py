import os
from typing import Any, Dict, List, Optional

from PyQt5 import QtCore, QtGui, QtWidgets

from overlay.aoe4_data import civ_data, map_data
from overlay.helper_func import file_path
from overlay.settings import settings


class PlayerWidget(QtWidgets.QWidget):
    """ Player widget shown on the overlay"""
    def __init__(self):
        super().__init__()
        self.hide()
        playout = QtWidgets.QHBoxLayout()
        self.setLayout(playout)

        self.flag = QtWidgets.QLabel()
        self.flag.setFixedSize(QtCore.QSize(60, 30))
        self.name = QtWidgets.QLabel()
        self.name.setStyleSheet("font-weight: bold")
        self.civ = QtWidgets.QLabel()
        self.rating = QtWidgets.QLabel()
        self.rating.setStyleSheet("color: blue")
        self.rank = QtWidgets.QLabel()
        self.winrate = QtWidgets.QLabel()
        self.wins = QtWidgets.QLabel()
        self.wins.setStyleSheet("color: green")
        self.losses = QtWidgets.QLabel()
        self.losses.setStyleSheet("color: red")

        for item in (self.flag, self.name, self.civ, self.rating, self.rank,
                     self.winrate, self.wins, self.losses):
            playout.addWidget(item)

    def update_player(self, player_data: Dict[str, Any]):
        self.show()
        civ_name = civ_data.get(player_data['civ'], "Unknown civ")
        self.name.setText(player_data['name'])
        self.civ.setText(f"({civ_name})")

        # Flag
        image_file = file_path(f'src/img/flags/{civ_name}.webp')
        if os.path.isfile(image_file):
            pixmap = QtGui.QPixmap(image_file)
            pixmap = pixmap.scaled(self.flag.width(), self.flag.height())
            self.flag.setPixmap(pixmap)

        # Check whether we have ranked data
        if not 'rank' in player_data:
            self.rank.setText("")
            self.winrate.setText("")
            self.wins.setText("")
            self.losses.setText("")
            self.rating.setText("")
            return

        self.rating.setText(str(player_data['rating']))
        self.rank.setText(f"#{player_data['rank']}")
        self.winrate.setText(
            f"{player_data['wins']/(player_data['wins']+player_data['losses']):.1%}"
        )
        self.wins.setText(str(player_data['wins']))
        self.losses.setText(str(player_data['losses']))


class AoEOverlay(QtWidgets.QWidget):
    """Overlay widget showing AOE4 information """
    def __init__(self):
        super().__init__()
        self.fixed = True

        if settings.overlay_geometry is None:
            self.setGeometry(0, 0, 600, 600)
            sg = QtWidgets.QDesktopWidget().screenGeometry(0)
            self.move(sg.width() - self.width() - 10, sg.top() + 10)
        else:
            self.setGeometry(*settings.overlay_geometry)

        self.setWindowTitle('AoE IV: Overlay')
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint
                            | QtCore.Qt.WindowTransparentForInput
                            | QtCore.Qt.WindowStaysOnTopHint
                            | QtCore.Qt.CoverWindow
                            | QtCore.Qt.NoDropShadowWindowHint
                            | QtCore.Qt.WindowDoesNotAcceptFocus)
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self.playerlayout = QtWidgets.QVBoxLayout()
        self.playerlayout.setAlignment(QtCore.Qt.AlignRight
                                       | QtCore.Qt.AlignTop)
        self.setLayout(self.playerlayout)
        self.update_font_size(settings.font_size)

        # Add UI elements
        self.map = QtWidgets.QLabel("MAP_NAME")
        self.playerlayout.addWidget(self.map)

        self.players = []
        for _ in range(8):
            self.players.append(PlayerWidget())
            self.playerlayout.addWidget(self.players[-1])

        self.show()

    def update_font_size(self, font_size):
        self.setStyleSheet(f"QLabel {{font-size: {font_size}pt }}")

    def update_data(self, game_data: Dict[str, Any]):
        self.map.setText(map_data.get(game_data['map_type'], "Unknown map"))

        [p.hide() for p in self.players]
        for i, player in enumerate(game_data['players']):
            self.players[i].update_player(player)

        if not self.isVisible():
            self.show()

    def show_hide(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def save_geometry(self):
        """ Saves overlay geometry into settings"""
        pos = self.pos()
        settings.overlay_geometry = [
            pos.x(), pos.y(), self.width(),
            self.height()
        ]

    def change_state(self):
        """ Changes the widget to be movable or not"""
        pos = self.pos()

        if self.fixed:
            self.fixed = False
            self.setWindowFlags(QtCore.Qt.Window
                                | QtCore.Qt.CustomizeWindowHint
                                | QtCore.Qt.WindowTitleHint)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground, False)
            self.move(pos.x() - 8, pos.y() - 31)
        else:
            self.fixed = True
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint
                                | QtCore.Qt.WindowTransparentForInput
                                | QtCore.Qt.WindowStaysOnTopHint
                                | QtCore.Qt.CoverWindow
                                | QtCore.Qt.NoDropShadowWindowHint
                                | QtCore.Qt.WindowDoesNotAcceptFocus)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
            self.move(pos.x() + 8, pos.y() + 31)
            self.save_geometry()
        self.show()
