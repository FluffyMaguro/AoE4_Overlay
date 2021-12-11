import json
import os
import time
from typing import Any, Dict, List

from PyQt5 import QtCore, QtWidgets

from overlay.aoe4_data import map_data
from overlay.logging_func import CONFIG_FOLDER, get_logger
from overlay.settings import settings

logger = get_logger(__name__)
DATA_FILE = os.path.join(CONFIG_FOLDER, "match_data.json")


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
        teams = {1: [], 2: []}
        for player in match_data["players"]:
            team = player["team"]
            if team in teams:
                teams[team].append(f"{player['name']}")

        other_team = 1 if main_team == 2 else 2
        team_widgets = []
        for team in (main_team, other_team):
            team_string = "\n".join(teams[team])
            team_widgets.append(QtWidgets.QLabel(team_string))

        # Map
        map_name = QtWidgets.QLabel(
            map_data.get(match_data["map_type"], "Unknown map"))

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
        self.logging_matches = False
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
        self.scroll_layout.addWidget(QtWidgets.QLabel("Rating"), 0, 6)

        self.header_widgets = set()
        for i in range(self.scroll_layout.count()):
            self.scroll_layout.itemAt(i).widget().setAlignment(
                QtCore.Qt.AlignHCenter)
            self.scroll_layout.itemAt(i).widget().setStyleSheet(
                "font-weight: bold")
            self.header_widgets.add(self.scroll_layout.itemAt(i).widget())

        self.scroll_layout.addWidget(Line(), 1, 0, 1, 7)

    def clear_scroll_layout(self):
        """ Removes all widgets from the scroll layout
        All except the header widgets"""
        widgets_in_layout = {
            self.scroll_layout.itemAt(i).widget()
            for i in range(self.scroll_layout.count())
        }
        for widget in widgets_in_layout:
            if widget in self.header_widgets:
                continue
            self.scroll_layout.removeWidget(widget)

    def clear_games(self):
        """ Removes all games from the game tab"""
        self.clear_scroll_layout()
        self.matches = []

    def save_game_data(self, match_data: Dict[str, Any]):
        """ Saves match data into a data file for archivation"""
        if not self.logging_matches:
            return
        with open(DATA_FILE, 'a') as f:
            try:
                data = json.dumps(match_data, indent=2)
                f.write(data)
            except Exception:
                logger.exception(f"Failed to save match data")

    def update_widgets(self, match_history: List[Any]):
        # Remove widgets from the layout
        self.clear_scroll_layout()

        # Add new matches to our list
        present_match_ids = {i.match_id for i in self.matches}
        for match in reversed(match_history):
            if match['my_rating'] == -1:
                continue
            if match['match_id'] in present_match_ids:
                continue
            self.matches.append(MatchEntry(self.scroll_layout, match))
            self.save_game_data(match)

        # Re-add widgets to the layout
        added_rows = 2  # With header and line
        for match_entry in reversed(self.matches):
            if match_entry.in_layout:
                continue
            match_entry.add_to_layout(added_rows)
            self.scroll_layout.addWidget(Line(), added_rows + 1, 0, 1, 7)
            added_rows += 2
