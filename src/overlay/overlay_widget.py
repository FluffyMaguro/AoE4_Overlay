from typing import Any, Dict

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from overlay.custom_widgets import OverlayWidget, VerticalLabel
from overlay.helper_func import file_path, zeroed
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

def set_country_flag(country_code: str, widget: QtWidgets.QLabel):
    """ Sets country flag to a widget. Handles caching."""
    if country_code in PIXMAP_CACHE:
        widget.setPixmap(PIXMAP_CACHE[country_code])
        return
    path = file_path(f"img/countries/{country_code}.png")  # PNG format
    pixmap = QtGui.QPixmap(path)
    pixmap = pixmap.scaled(widget.width(), widget.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    PIXMAP_CACHE[country_code] = pixmap
    widget.setPixmap(pixmap)


class PlayerWidget:
    """ Player widget shown on the overlay"""

    def __init__(self, row: int, toplayout: QtWidgets.QGridLayout):
        self.hiding_civ_stats: bool = True
        self.team: int = 0
        self.civ: str = ""
        self.visible = True
        self.create_widgets()
        self.name.setStyleSheet("font-weight: bold")
        self.name.setContentsMargins(5, 0, 10, 0)
        self.rating.setStyleSheet("color: #7ab6ff; font-weight: bold")
        self.winrate.setStyleSheet("color: #fffb78")
        self.wins.setStyleSheet("color: #48bd21")
        self.losses.setStyleSheet("color: red")
        for widget in (self.civ_games, self.civ_winrate, self.civ_median_wins):
            widget.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            widget.setStyleSheet(f"color: {settings.civ_stats_color}")

        offset = 0
        for column, widget in enumerate(
            (self.flag, self.name, self.country, self.rating, self.rank, self.winrate,
             self.wins, self.losses, self.civ_games, self.civ_winrate,
             self.civ_median_wins)):

            if widget == self.civ_games:
                offset = 1
            toplayout.addWidget(widget, row, column + offset)

    def create_widgets(self):
        # Separated so this can be changed in a child inner overlay for editing
        self.flag = QtWidgets.QLabel()
        self.flag.setFixedSize(QtCore.QSize(60, 30))
        self.country = QtWidgets.QLabel()
        self.country.setFixedSize(QtCore.QSize(25,14))
        self.country.setScaledContents(True)  

        self.name = QtWidgets.QLabel()
        self.rating = QtWidgets.QLabel()
        self.rank = QtWidgets.QLabel()
        self.winrate = QtWidgets.QLabel()
        self.wins = QtWidgets.QLabel()
        self.losses = QtWidgets.QLabel()
        self.civ_games = QtWidgets.QLabel()
        self.civ_winrate = QtWidgets.QLabel()
        self.civ_median_wins = QtWidgets.QLabel()
         

    def show(self, show: bool = True):
        self.visible = show
        """ Shows or hides all widgets in this class """
        for widget in (self.flag, self.name, self.country, self.rating, self.rank,
                       self.winrate, self.wins, self.losses, self.civ_games,
                       self.civ_winrate, self.civ_median_wins):
            widget.show() if show else widget.hide()

    def update_name_color(self):
        color = settings.team_colors[(self.team - 1) %
                                     len(settings.team_colors)]
        color = tuple(color)
        self.name.setStyleSheet("font-weight: bold; "
                                "background: QLinearGradient("
                                "x1: 0, y1: 0,"
                                "x2: 1, y2: 0,"
                                f"stop: 0 rgba{color},"
                                f"stop: 0.8 rgba{color},"
                                "stop: 1 rgba(0,0,0,0))")

    def update_flag(self, ):
        set_pixmap(self.civ, self.flag)

    def update_country_flag(self, country_code: str):
        set_country_flag(country_code, self.country)

    def update_player(self, player_data: Dict[str, Any]):
        # Flag
        self.civ = player_data['civ']
        self.update_flag()

        self.update_country_flag(player_data['country']) 
        # Indicate team with background color
        self.team = zeroed(player_data['team'])
        self.update_name_color()

        # Fill the rest
        self.name.setText(player_data['name'])
        self.rating.setText(player_data['rating'])
        self.rank.setText(player_data['rank'])
        self.winrate.setText(player_data['winrate'])
        self.wins.setText(str(player_data['wins']))
        self.losses.setText(player_data['losses'])
        self.civ_games.setText(player_data['civ_games'])
        self.civ_winrate.setText(player_data['civ_winrate'])
        self.civ_median_wins.setText(player_data['civ_win_length_median'])
        self.show(show=bool(player_data['name']))

        # Hide civ specific data when there are none
        if not player_data['civ_games'] and self.hiding_civ_stats:
            for widget in (self.civ_games, self.civ_winrate,
                           self.civ_median_wins):
                widget.hide()

    def get_data(self) -> Dict[str, Any]:
        return {
            'civ': self.civ,
            'name': self.name.text(),
            'team': self.team,
            'country': self.country.text(),
            'rating': self.rating.text(),
            'rank': self.rank.text(),
            'wins': self.wins.text(),
            'losses': self.losses.text(),
            'winrate': self.winrate.text(),
            'civ_games': self.civ_games.text(),
            'civ_winrate': self.civ_winrate.text(),
            'civ_win_length_median': self.civ_median_wins.text(),
        }


class AoEOverlay(OverlayWidget):
    """Overlay widget showing AOE4 information """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hiding_civ_stats: bool = True
        self.players = []
        self.setup_as_overlay()
        self.initUI()

    def setup_as_overlay(self):
        if settings.overlay_geometry is None:
            self.setGeometry(0, 0, 700, 400)
            sg = QtWidgets.QApplication.primaryScreen().availableGeometry()
            self.move(sg.width() - self.width() + 15, sg.top() - 20)
        else:
            self.setGeometry(*settings.overlay_geometry)

        self.setWindowTitle('AoE IV: Overlay')

    def initUI(self):
        # Layouts & inner frame
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

        self.inner_frame = QtWidgets.QFrame()
        self.inner_frame.setObjectName("inner_frame")
        layout.addWidget(self.inner_frame)
        self.playerlayout = QtWidgets.QGridLayout()
        self.playerlayout.setContentsMargins(10, 20, 20, 10)
        self.playerlayout.setHorizontalSpacing(10)
        self.playerlayout.setAlignment(Qt.AlignmentFlag.AlignRight
                                       | Qt.AlignmentFlag.AlignTop)
        self.inner_frame.setLayout(self.playerlayout)
        self.update_style(settings.font_size)

        # Map
        self.map = QtWidgets.QLabel()
        self.map.setStyleSheet(
            "font-weight: bold; font-style: italic; color: #f2ea54")
        self.map.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.playerlayout.addWidget(self.map, 0, 0, 1, 2)
        # Header
        country = QtWidgets.QLabel("Country")
        rating = QtWidgets.QLabel("Elo")
        rating.setStyleSheet("color: #7ab6ff; font-weight: bold")
        rank = QtWidgets.QLabel("Rank")
        winrate = QtWidgets.QLabel("Winrate")
        winrate.setStyleSheet("color: #fffb78")
        wins = QtWidgets.QLabel("Wins")
        wins.setStyleSheet("color: #48bd21")
        losses = QtWidgets.QLabel("Losses")
        losses.setStyleSheet("color: red")

        self.civ_games = QtWidgets.QLabel("Games")
        self.civ_winrate = QtWidgets.QLabel("Winrate")
        self.civ_med_wins = QtWidgets.QLabel("Wintime")

        for widget in (self.civ_games, self.civ_winrate, self.civ_med_wins):
            widget.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            widget.setStyleSheet(f"color: {settings.civ_stats_color}")

        offset = 0
        for column, widget in enumerate(
            (country, rating, rank, winrate, wins, losses, self.civ_games,
             self.civ_winrate, self.civ_med_wins)):
            if widget == self.civ_games:
                offset = 1
                self.civ_stats_label = VerticalLabel(
                    "CIV STATS", QtGui.QColor(settings.civ_stats_color))
                self.playerlayout.addWidget(self.civ_stats_label, 0,
                                            column + 2, 10, 1)

            self.playerlayout.addWidget(widget, 0, column + offset + 2)

        # Add players
        self.init_players()

    def init_players(self):
        for i in range(8):
            self.players.append(PlayerWidget(i + 1, self.playerlayout))

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

        if self.isVisible():
            self.show()

    def update_data(self, game_data: Dict[str, Any]):
        self.map.setText(game_data['map'])
        [p.show(False) for p in self.players]

        show_civ_stats = False
        for i, player in enumerate(game_data['players']):
            if i >= len(self.players):
                break

            self.players[i].update_player(player)

            if player['civ_games']:
                show_civ_stats = True

        # Show or hide civilization stats
        for widget in (self.civ_games, self.civ_winrate, self.civ_med_wins,
                       self.civ_stats_label):
            if self.hiding_civ_stats and not show_civ_stats:
                widget.hide()
            else:
                widget.show()

        if settings.open_overlay_on_new_game:
            self.show()

    def save_geometry(self):
        """ Saves overlay geometry into settings"""
        pos = self.pos()
        settings.overlay_geometry = [
            pos.x(), pos.y(), self.width(),
            self.height()
        ]

    def get_data(self) -> Dict[str, Any]:
        result = {"map": self.map.text(), "players": []}
        for player in self.players:
            if player.visible:
                result["players"].append(player.get_data())
        return result
