from typing import Any, Dict, List, Tuple

from PyQt5 import QtCore, QtGui, QtWidgets

from overlay.aoe4_data import civ_data, map_data
from overlay.helper_func import file_path
from overlay.settings import settings

PIXMAP_CACHE = {}


def set_pixmap(civ: str, widget: QtWidgets.QWidget):
    """ Sets civ pixmap to a widget. Handles caching."""
    if civ in PIXMAP_CACHE:
        widget.setPixmap(PIXMAP_CACHE[civ])
        return
    path = file_path(f"img/flags/{civ}.webp")
    pixmap = QtGui.QPixmap(path)
    pixmap = pixmap.scaled(widget.width(), widget.height())
    PIXMAP_CACHE[civ] = pixmap
    widget.setPixmap(pixmap)


class PlayerWidget:
    """ Player widget shown on the overlay"""
    def __init__(self, row: int, toplayout: QtWidgets.QGridLayout):
        self.create_widgets()
        self.name.setStyleSheet("font-weight: bold")
        self.name.setContentsMargins(5, 0, 10, 0)
        self.rating.setStyleSheet("color: #7ab6ff; font-weight: bold")
        self.winrate.setStyleSheet("color: #fffb78")
        self.wins.setStyleSheet("color: #48bd21")
        self.losses.setStyleSheet("color: red")

        for column, widget in enumerate(
            (self.flag, self.name, self.rating, self.rank, self.winrate,
             self.wins, self.losses)):
            toplayout.addWidget(widget, row, column)

    def create_widgets(self):
        # Separated so this can be changed in a child inner overlay for editing
        self.flag = QtWidgets.QLabel()
        self.flag.setFixedSize(QtCore.QSize(60, 30))
        self.name = QtWidgets.QLabel()
        self.rating = QtWidgets.QLabel()
        self.rank = QtWidgets.QLabel()
        self.winrate = QtWidgets.QLabel()
        self.wins = QtWidgets.QLabel()
        self.losses = QtWidgets.QLabel()

    def show(self, show: bool = True):
        """ Shows or hides all widgets in this class """
        for widget in (self.flag, self.name, self.rating, self.rank,
                       self.winrate, self.wins, self.losses):
            widget.show() if show else widget.hide()

    def update_name_color(self, color: Tuple[int, int, int, float]):
        self.name.setStyleSheet("font-weight: bold; "
                                "background: QLinearGradient("
                                "x1: 0, y1: 0,"
                                "x2: 1, y2: 0,"
                                f"stop: 0 rgba{color},"
                                f"stop: 0.8 rgba{color},"
                                "stop: 1 rgba(0,0,0,0))")

    def update_flag(self, civ_name: str):
        set_pixmap(civ_name, self.flag)

    def update_player(self, player_data: Dict[str, Any]):
        self.show()
        civ_name = civ_data.get(player_data['civ'], "Unknown civ")
        self.name.setText(player_data['name'])

        # Flag
        self.update_flag(civ_name)

        # Indicate team with background color
        color = settings.team_colors[(player_data['team'] - 1) %
                                     len(settings.team_colors)]
        self.update_name_color(color)

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

    def override(self, data: List[str]):
        for i, item in enumerate((self.name, self.rating, self.rank,
                                  self.winrate, self.wins, self.losses)):
            item.setText(data[i])
        set_pixmap(data[-1], self.flag)
        self.show() if self.name.text() else self.show(False)


class AoEOverlay(QtWidgets.QWidget):
    """Overlay widget showing AOE4 information """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fixed = True
        self.players = []
        self.setup_as_overlay()
        self.initUI()

    def setup_as_overlay(self):
        if settings.overlay_geometry is None:
            self.setGeometry(0, 0, 700, 400)
            sg = QtWidgets.QDesktopWidget().screenGeometry(0)
            self.move(sg.width() - self.width() + 15, sg.top() - 20)
        else:
            self.setGeometry(*settings.overlay_geometry)

        self.setWindowTitle('AoE IV: Overlay')
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint
                            | QtCore.Qt.WindowTransparentForInput
                            | QtCore.Qt.WindowStaysOnTopHint
                            | QtCore.Qt.CoverWindow
                            | QtCore.Qt.NoDropShadowWindowHint
                            | QtCore.Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

    def initUI(self):
        # Layouts & inner frame
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        self.setLayout(layout)

        self.inner_frame = QtWidgets.QFrame()
        self.inner_frame.setObjectName("inner_frame")
        layout.addWidget(self.inner_frame)
        self.playerlayout = QtWidgets.QGridLayout()
        self.playerlayout.setContentsMargins(10, 20, 20, 10)
        self.playerlayout.setHorizontalSpacing(10)
        self.playerlayout.setAlignment(QtCore.Qt.AlignRight
                                       | QtCore.Qt.AlignTop)
        self.inner_frame.setLayout(self.playerlayout)
        self.update_style(settings.font_size)

        # Map
        self.map = QtWidgets.QLabel()
        self.map.setStyleSheet(
            "font-weight: bold; font-style: italic; color: #f2ea54")
        self.map.setAlignment(QtCore.Qt.AlignCenter)
        self.playerlayout.addWidget(self.map, 0, 0, 1, 2)

        # Header
        rating = QtWidgets.QLabel("Elo")
        rating.setStyleSheet("color: #7ab6ff; font-weight: bold")
        rank = QtWidgets.QLabel("Rank")
        winrate = QtWidgets.QLabel("Winrate")
        winrate.setStyleSheet("color: #fffb78")
        wins = QtWidgets.QLabel("Wins")
        wins.setStyleSheet("color: #48bd21")
        losses = QtWidgets.QLabel("Losses")
        losses.setStyleSheet("color: red")

        for column, widget in enumerate((rating, rank, winrate, wins, losses)):
            self.playerlayout.addWidget(widget, 0, column + 2)

        # Add players
        self.init_players()

        # Save position
        self.old_pos = self.pos()

    def init_players(self):
        for i in range(8):
            self.players.append(PlayerWidget(i + 1, self.playerlayout))

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        """ Override used for window dragging"""
        self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        """ Override used for window dragging"""
        delta = QtCore.QPoint(event.globalPos() - self.old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPos()

    def update_style(self, font_size: int):
        self.setStyleSheet(
            f"QLabel {{font-size: {font_size}pt; color: white }}"
            "QFrame#inner_frame"
            "{"
            "background: QLinearGradient("
            "x1: 0, y1: 0,"
            "x2: 1, y2: 0,"
            "stop: 0 rgba(0,0,0,0),"
            "stop: 0.1 rgba(0,0,0,0.5),"
            "stop: 1 rgba(0,0,0,1))"
            "}")

    def update_data(self, game_data: Dict[str, Any]):
        self.map.setText(
            f'{map_data.get(game_data["map_type"], "Unknown map")} ')

        [p.show(False) for p in self.players]
        player_data = self.sort_game_data(game_data['players'])
        for i, player in enumerate(player_data):
            self.players[i].update_player(player)

        self.show()

    def sort_game_data(
            self, player_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """ Sorts player data so the main player team is always on top"""
        # Find main player team
        team = None
        for player in player_data:
            if player['profile_id'] == settings.profile_id:
                team = player['team']
                break
        if team is None:
            return player_data

        def sortingf(player: Dict[str, Any]) -> int:
            if player['team'] == team:
                return -1
            return player['team']

        return sorted(player_data, key=sortingf)

    def show_hide(self):
        self.hide() if self.isVisible() else self.show()

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
            self.move(pos.x() - 1, pos.y() - 31)
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

    def override(self, data: Dict[str, Any]):
        self.map.setText(data['map'])
        for i, player in enumerate(data['players']):
            self.players[i].override(player)
        self.show()
