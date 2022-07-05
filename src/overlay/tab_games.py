import time
from collections import defaultdict
from typing import Any, Dict, List

from PyQt5 import QtCore, QtWidgets

from overlay.aoe4_data import map_data
from overlay.helper_func import quickmatch_game
from overlay.logging_func import catch_exceptions, get_logger
from overlay.settings import settings

logger = get_logger(__name__)


class Line(QtWidgets.QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #bbb")
        self.setMinimumHeight(1)
        self.setMaximumHeight(1)


class MatchEntry:

    def __init__(self, layout: QtWidgets.QGridLayout, match_data: Dict[str,
                                                                       Any]):
        self.main_layout: QtWidgets.QGridLayout = layout
        self.in_layout: bool = False
        self.match_id = match_data['match_id']

        # Try to find the main player team first
        main_team = 1
        for player in match_data["players"]:
            if player['profile_id'] == settings.profile_id:
                main_team = player['team']
                break

        # Teams
        teams = defaultdict(list)
        for player in match_data["players"]:
            team = player["team"]
            teams[team].append(f"{player['name']}")

        other_team = 1 if main_team == 2 else 2
        team_widgets = []
        for team in (main_team, other_team):
            team_string = "\n".join(teams[team])
            team_widgets.append(QtWidgets.QLabel(team_string))

        # Map
        map_name = QtWidgets.QLabel(
            map_data.get(match_data.get("map_type", -1), "Unknown map"))

        # Date
        date = QtWidgets.QLabel(
            time.strftime("%b %d, %H:%M:%S",
                          time.localtime(match_data['started'])))

        # Mode
        mode = QtWidgets.QLabel()
        if len(teams) == 2:
            player_number = [len(teams[i]) for i in teams]
            mode.setText(f"{player_number[0]}v{player_number[1]}")

        # Result
        result = QtWidgets.QLabel(match_data["result"])

        # ELO change
        if quickmatch_game(match_data):
            plus = not isinstance(match_data['my_rating_diff'],
                                  str) and match_data['my_rating_diff'] > 0
            rating_string = f"{'+' if plus else ''}{match_data['my_rating_diff']} → {match_data['my_rating']}"
        else:
            rating_string = "Custom game"

        elo_change = QtWidgets.QLabel(rating_string)

        # APM
        apm =  QtWidgets.QLabel(map_data.get(match_data.get("apm", "?"), "?"))


        self.widgets = (*team_widgets, map_name, date, mode, result, elo_change, apm)

        for item in self.widgets:
            item.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            item.setAlignment(QtCore.Qt.AlignCenter)

        # Line
        self.line = Line()

    def add_to_layout(self, row: int):
        """ Adds widgets back to the layout"""
        self.in_layout = True
        for column, widget in enumerate(self.widgets):
            self.main_layout.addWidget(widget, row, column)
        self.main_layout.addWidget(self.line, row + 1, 0, 1, 7)

    def remove_from_layout(self):
        """ Removes its widgets from the layout"""
        self.in_layout = False
        for widget in self.widgets:
            self.main_layout.removeWidget(widget)
        self.main_layout.removeWidget(self.line)


class MatchHistoryTab(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        # List of added matches. New ones at the end.
        self.matches: List[MatchEntry] = []

        # Scroll content
        scroll_content = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QGridLayout(self)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setAlignment(QtCore.Qt.AlignTop)
        scroll_content.setLayout(self.scroll_layout)

        # Scroll area
        scroll = QtWidgets.QScrollArea()
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_content)

        # Add scroll are to layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(scroll)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Header
        self.scroll_layout.addWidget(QtWidgets.QLabel("Team 1"), 0, 0)
        self.scroll_layout.addWidget(QtWidgets.QLabel("Team 2"), 0, 1)
        self.scroll_layout.addWidget(QtWidgets.QLabel("Map"), 0, 2)
        self.scroll_layout.addWidget(QtWidgets.QLabel("Started"), 0, 3)
        self.scroll_layout.addWidget(QtWidgets.QLabel("Mode"), 0, 4)
        self.scroll_layout.addWidget(QtWidgets.QLabel("Result"), 0, 5)
        self.scroll_layout.addWidget(QtWidgets.QLabel("Rating"), 0, 6)
        self.scroll_layout.addWidget(QtWidgets.QLabel("APM"), 0, 7)

        self.header_widgets = set()
        for i in range(self.scroll_layout.count()):
            self.scroll_layout.itemAt(i).widget().setAlignment(
                QtCore.Qt.AlignHCenter)
            self.scroll_layout.itemAt(i).widget().setStyleSheet(
                "font-weight: bold")
            self.header_widgets.add(self.scroll_layout.itemAt(i).widget())

    def clear_scroll_layout(self):
        """ Removes all widgets from the scroll layout
        All except the header widgets"""
        for match in self.matches:
            match.remove_from_layout()

    def clear_games(self):
        """ Removes all games from the game tab"""
        self.clear_scroll_layout()
        self.matches = []

    @catch_exceptions(logger)
    def update_widgets(self, match_history: List[Any]):
        # Remove widgets from the layout
        self.clear_scroll_layout()

        # Add new matches to our list
        present_match_ids = {i.match_id for i in self.matches}
        for match in reversed(match_history):
            if match['my_rating'] == -1 and quickmatch_game(match):
                continue
            if match['match_id'] in present_match_ids:
                continue
            self.matches.append(MatchEntry(self.scroll_layout, match))

        # Re-add widgets to the layout
        added_rows = 1  # With header
        for match_entry in reversed(self.matches):
            if match_entry.in_layout:
                continue
            if added_rows > settings.max_games_history * 2:
                continue
            match_entry.add_to_layout(added_rows)
            added_rows += 2
