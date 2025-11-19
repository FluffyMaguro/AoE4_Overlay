from typing import Any, Callable, Dict

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from overlay.aoe4_data import civ_data
from overlay.helper_func import file_path, zeroed
from overlay.logging_func import get_logger
from overlay.overlay_widget import AoEOverlay, PlayerWidget
from overlay.settings import settings

logger = get_logger(__name__)
ICON_CACHE = {}


def get_icon(civ: str) -> QtGui.QIcon:
    """ Gets icon for a civilization. Handles caching."""
    if civ in ICON_CACHE:
        return ICON_CACHE[civ]
    path = file_path(f"img/flags/{civ}.webp")
    icon = QtGui.QIcon(path)
    ICON_CACHE[civ] = icon
    return icon


class InnerPlayer(PlayerWidget):
    """ Overriding player widget and making fields editable"""
    def __init__(self, row: int, toplayout: QtWidgets.QGridLayout):
        super().__init__(row, toplayout)
        self.hiding_civ_stats = False
        self.change_style()
        self.update_name_color()
        self.callable: Callable = print
        toplayout.addWidget(self.team_cb, row, 10)
        self.team_cb.currentIndexChanged.connect(self.update_team)

    def create_widgets(self):
        self.flag = QtWidgets.QComboBox()
        for i, civ in enumerate(civ_data.values()):
            self.flag.addItem(civ)
            self.flag.setItemIcon(i, get_icon(civ))

        self.name = QtWidgets.QLineEdit()
        self.team_cb = QtWidgets.QComboBox()
        self.team_cb.addItem("No team")
        for i in range(1, 3):
            self.team_cb.addItem(f"Team {i}")
        self.rating = QtWidgets.QLineEdit()
        self.country = QtWidgets.QLabel()
        self.rank = QtWidgets.QLineEdit()
        self.winrate = QtWidgets.QLineEdit()
        self.wins = QtWidgets.QLineEdit()
        self.losses = QtWidgets.QLineEdit()
        self.civ_games = QtWidgets.QLineEdit()
        self.civ_winrate = QtWidgets.QLineEdit()
        self.civ_median_wins = QtWidgets.QLineEdit()

    def show(self, show: bool = True):
        super().show(show)
        self.team_cb.show() if show else self.team_cb.hide()

    def update_team(self, index: int):
        self.team = zeroed(index)
        self.update_name_color()
        self.callable()

    def change_style(self):
        for item in (self.rating, self.rank, self.winrate, self.wins,
                     self.losses, self.civ_games, self.civ_winrate,
                     self.civ_median_wins):
            style = item.styleSheet()
            item.setStyleSheet(
                f"{style}; border: 1px solid #444; font-size: 11pt")

    def connect_to_function(self, function: Callable):
        self.callable = function
        self.flag.currentIndexChanged.connect(function)
        for item in (self.name, self.rating, self.rank, self.winrate,
                     self.wins, self.losses, self.civ_games, self.civ_winrate,
                     self.civ_median_wins):
            item.textChanged.connect(function)

    def disconnect_changes(self):
        self.flag.currentIndexChanged.disconnect()
        for item in (self.name, self.rating, self.rank, self.winrate,
                     self.wins, self.losses, self.civ_games, self.civ_winrate,
                     self.civ_median_wins):
            item.textChanged.disconnect()

    def update_name_color(self):
        color = settings.team_colors[(self.team - 1) %
                                     len(settings.team_colors)]
        color = tuple(color)
        self.name.setStyleSheet(
            f"background-color: rgba{color};font-weight: bold;"
            "border: 1px solid #444; font-size: 11pt")

    def update_flag(self):
        self.flag.setCurrentText(self.civ)

    def update_player(self, player_data: Dict[str, Any]):
        # We don't want the automatic update to look like the user made the change
        self.disconnect_changes()
        super().update_player(player_data)
        self.team_cb.setCurrentIndex(self.team)
        self.connect_to_function(self.callable)

    def get_data(self) -> Dict[str, Any]:
        # Override to get civ from flag
        return {
            'civ': self.flag.currentText(),
            'name': self.name.text(),
            'team': self.team,
            'rating': self.rating.text(),
            'rank': self.rank.text(),
            'wins': self.wins.text(),
            'losses': self.losses.text(),
            'winrate': self.winrate.text(),
            'civ_games': self.civ_games.text(),
            'civ_winrate': self.civ_winrate.text(),
            'civ_win_length_median': self.civ_median_wins.text(),
        }


class InnerOverlay(AoEOverlay):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.change_to_editable()
        self.setStyleSheet(
            "background-color: #222; color: white; font-size: 11pt")
        self.hiding_civ_stats = False

    def change_to_editable(self):
        self.map = QtWidgets.QLineEdit("Map")
        self.map.textChanged.connect(self.changed)
        self.map.setStyleSheet(
            "font-weight: bold; font-style: italic; color: #f2ea54; border: 1px solid #444"
        )
        self.map.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.playerlayout.addWidget(self.map, 0, 0, 1, 2)

    def setup_as_overlay(self):
        ...

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        ...

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        ...

    def update_style(self, font_size: int):
        ...

    def init_players(self):
        for i in range(8):
            self.players.append(InnerPlayer(i + 1, self.playerlayout))
            self.players[-1].connect_to_function(self.changed)

    def update_data(self, player_data: Dict[str, Any]):
        self.map.textChanged.disconnect()
        super().update_data(player_data)
        self.map.textChanged.connect(self.changed)

    def changed(self):
        self.parent().overlay_changed(self.get_data())


class OverrideTab(QtWidgets.QWidget):
    data_override = QtCore.pyqtSignal(object)
    update_override = QtCore.pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__(parent)
        self.live_data = {}
        self.changed_data = {}
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(15)
        self.setLayout(layout)

        top_layout = QtWidgets.QVBoxLayout()
        top_layout.setContentsMargins(10, 10, 0, 0)
        layout.addLayout(top_layout)

        # Description
        desc = QtWidgets.QLabel(
            """Here you can override what is being shown on the overlay.<br><br>\
             <b>Override</b> will apply these values.<br>\
             <b>Reset</b> will reset the overlay and this to current live values.<br>\
             <b>Prevent automatic update</b> will prevent automatic updating with new games."""
        )

        top_layout.addWidget(desc)

        # Button
        hlayout = QtWidgets.QHBoxLayout()
        top_layout.addLayout(hlayout)

        # Override overlay
        override_btn = QtWidgets.QPushButton("Override")
        override_btn.clicked.connect(self.override_overlay)
        override_btn.setMaximumWidth(150)
        override_btn.setShortcut("Return")
        hlayout.addWidget(override_btn)

        # Reset overlay
        reset_btn = QtWidgets.QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_overlay)
        reset_btn.setMaximumWidth(150)
        hlayout.addWidget(reset_btn)

        self.prevent_ck = QtWidgets.QCheckBox("Prevent automatic update")
        self.prevent_ck.stateChanged.connect(
            lambda: self.update_override.emit(self.prevent_ck.isChecked()))
        hlayout.addWidget(self.prevent_ck)

        # Inner overlay
        self.overlay_widget = InnerOverlay()
        layout.addWidget(self.overlay_widget)
        self.overlay_widget.show()

    def update_data(self, player_data: Dict[str, Any]):
        self.live_data = player_data
        if not self.prevent_ck.isChecked():
            self.overlay_widget.update_data(player_data)
            self.changed_data = player_data

    def overlay_changed(self, data: Dict[str, Any]):
        self.changed_data = data

    def override_overlay(self):
        if not self.changed_data:
            return
        self.data_override.emit(self.changed_data)

    def reset_overlay(self):
        if not self.live_data:
            return
        self.overlay_widget.update_data(self.live_data)
        self.changed_data = self.overlay_widget.get_data()
        self.data_override.emit(self.changed_data)
        self.prevent_ck.setChecked(False)
