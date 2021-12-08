import time
from typing import Any, Dict, List

from PyQt5 import QtCore, QtWidgets

from overlay.aoe4_data import map_data
from overlay.api_checking import get_full_match_history
from overlay.worker import scheldule


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

        teams = dict()
        for player in match_data["players"]:
            team = player["team"]
            if team not in teams:
                teams[team] = []
            teams[team].append(f"{player['name']}")

        # Teams
        team_widgets = []
        for i, team in enumerate(teams):
            if i > 1:  # Keep it to two teams
                break
            team_string = "\n".join(teams[team])
            team_widgets.append(QtWidgets.QLabel(team_string))

        # Map
        map_name = QtWidgets.QLabel(
            map_data.get(match_data["map_type"], "Unknown map"))

        # Date
        date = QtWidgets.QLabel(
            time.strftime("%b %d, %H:%M:%S",
                          time.localtime(match_data['started'])))
        date.setStatusTip("year/month/day HH:MM:SS")

        # Mode
        mode = QtWidgets.QLabel()
        if len(teams) == 2:
            player_number = [len(teams[i]) for i in teams]
            mode.setText(f"{player_number[0]}v{player_number[1]}")

        # Result
        result = QtWidgets.QLabel(match_data["result"])

        # ELO change
        plus = not isinstance(match_data['my_rating_diff'],
                              str) and match_data['my_rating_diff'] > 0
        rating_string = f"{'+' if plus else ''}{match_data['my_rating_diff']} → {match_data['my_rating']}"
        elo_change = QtWidgets.QLabel(rating_string)

        self.widgets = (*team_widgets, map_name, date, mode, result,
                        elo_change)

        for item in self.widgets:
            item.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            item.setAlignment(QtCore.Qt.AlignCenter)

    def add_to_layout(self, row: int):
        """ Adds widgets back to the layout"""
        self.in_layout = True
        for column, widget in enumerate(self.widgets):
            self.main_layout.addWidget(widget, row, column)

    def remove_from_layout(self):
        """ Removes its widgets from the layout"""
        self.in_layout = False
        for widget in self.widgets:
            self.main_layout.removeWidget(widget)


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
        self.scroll_layout.addWidget(QtWidgets.QLabel("Date"), 0, 3)
        self.scroll_layout.addWidget(QtWidgets.QLabel("Mode"), 0, 4)
        self.scroll_layout.addWidget(QtWidgets.QLabel("Result"), 0, 5)
        self.scroll_layout.addWidget(QtWidgets.QLabel("Rating change"), 0, 6)

        for i in range(self.scroll_layout.count()):
            self.scroll_layout.itemAt(i).widget().setAlignment(
                QtCore.Qt.AlignHCenter)
            self.scroll_layout.itemAt(i).widget().setStyleSheet(
                "font-weight: bold")

        self.scroll_layout.addWidget(Line(), 1, 0, 1, 7)

    def clear_games(self):
        """ Removes all games from the game tab"""
        for item in self.matches:
            item.remove_from_layout()
        self.matches = []

    def run_update(self, amount: int):
        scheldule(self.update_widgets, get_full_match_history, amount)

    def update_widgets(self, match_history: List[Any]):
        # Remove widgets from the layout
        for item in self.matches:
            item.remove_from_layout()

        # Add new matches to our list
        present_match_ids = {i.match_id for i in self.matches}
        for match in reversed(match_history):
            if match['my_rating'] == -1:
                continue
            if match['match_id'] in present_match_ids:
                continue
            self.matches.append(MatchEntry(self.scroll_layout, match))

        # Re-add widgets to the layout
        added_rows = 2  # With header and line
        for match_entry in reversed(self.matches):
            if match_entry.in_layout:
                continue
            match_entry.add_to_layout(added_rows)
            self.scroll_layout.addWidget(Line(), added_rows + 1, 0, 1, 7)
            added_rows += 2
