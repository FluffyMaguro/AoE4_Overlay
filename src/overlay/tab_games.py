import time
from typing import Any, Dict, List

from PyQt5 import QtCore, QtWidgets

from overlay.aoe4_data import map_data


class MatchEntry(QtWidgets.QWidget):
    def __init__(self, parent, match_data: Dict[str, Any]):
        super().__init__(parent)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        teams = dict()
        for player in match_data["players"]:
            team = player["team"]
            if team not in teams:
                teams[team] = []
            teams[team].append(f"{player['name']}")

        # Teams
        team_widgets = []
        for team in teams:
            team_string = "\n".join(teams[team])
            team_widgets.append(QtWidgets.QLabel(team_string))

        # Map
        map_name = QtWidgets.QLabel(
            map_data.get(match_data["map_type"], "Unknown map"))
        # Ranked
        ranked = QtWidgets.QLabel(
            "ranked" if match_data["ranked"] else "unranked")

        # Date
        date = QtWidgets.QLabel(
            time.strftime("%Y/%m/%d %H:%M:%S",
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

        for item in (*team_widgets, map_name, ranked, date, mode, result,
                     elo_change):
            self.layout().addWidget(item)
            item.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.show()


class MatchHistoryTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.matches = dict()

        # Scroll content
        scroll_content = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QVBoxLayout(self)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
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

    def clear_games(self):
        """ Removes all games from the game tab"""
        for widget in self.matches.values():
            self.scroll_layout.removeWidget(widget)
        self.matches = dict()

    def update_match_history_widgets(self, match_history: List[Any]):
        for match in match_history:
            # Game already created or game doesn't have rating yet
            if match["match_id"] in self.matches or match['my_rating'] == -1:
                continue
            widget = MatchEntry(self, match)
            self.matches[match["match_id"]] = widget
            self.scroll_layout.addWidget(widget)
