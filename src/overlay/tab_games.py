from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

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
        self.game_id = match_data['game_id']

        # Try to find the main player team first
        main_player_data = None
        main_team = 0
        for team_idx, team in enumerate(match_data['teams']):
            for player in team:
                if player['player']['profile_id'] == settings.profile_id:
                    main_team = team_idx
                    main_player_data = player['player']
                    break

        # Teams
        teams = defaultdict(list)
        for team_idx, team in enumerate(match_data['teams']):
            for player in team:
                civ = player['player']['civilization'].replace(
                    "_", " ").capitalize()
                teams[team_idx].append(
                    f"{player['player']['name']} ({civ})   ")

        other_team = 1 if main_team == 0 else 0
        team_widgets = []
        for team in (main_team, other_team):
            team_string = "\n".join(teams[team])
            team_widgets.append(QtWidgets.QLabel(team_string))

        # Map
        map_name = QtWidgets.QLabel(match_data.get('map', "Unknown map"))

        # Date
        started = datetime.strptime(match_data['started_at'],
                                    "%Y-%m-%dT%H:%M:%S.000Z")

        date = QtWidgets.QLabel(started.strftime("%b %d, %H:%M:%S"))

        # Mode
        mode = QtWidgets.QLabel(match_data['kind'])

        # Result
        result = QtWidgets.QLabel(main_player_data['result'].capitalize(
        ) if main_player_data and main_player_data['result'] else "?")

        # ELO change
        diff = main_player_data[
            'rating_diff'] if main_player_data and main_player_data[
                'rating_diff'] else "?"
        elo_change = QtWidgets.QLabel(str(diff))

        # aoe4world Link
        game_id = match_data["game_id"]
        link = QtWidgets.QLabel(
            f'<a href="https://aoe4world.com/players/{settings.profile_id}/games/{game_id}"> game link</a>'
        )
        link.setOpenExternalLinks(True)

        self.widgets = (*team_widgets, map_name, date, mode, result,
                        elo_change, link)

        for item in self.widgets:
            if item != link:
                item.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            if item not in team_widgets:
                item.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Line
        self.line = Line()

    def add_to_layout(self, row: int):
        """ Adds widgets back to the layout"""
        self.in_layout = True
        for column, widget in enumerate(self.widgets):
            self.main_layout.addWidget(widget, row, column)
        self.main_layout.addWidget(self.line, row + 1, 0, 1, len(self.widgets))

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
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_content.setLayout(self.scroll_layout)

        # Scroll area
        scroll = QtWidgets.QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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
        self.scroll_layout.addWidget(QtWidgets.QLabel("Rating diff"), 0, 6)
        self.scroll_layout.addWidget(QtWidgets.QLabel("AoE4World"), 0, 7)

        self.header_widgets = set()
        for i in range(self.scroll_layout.count()):
            self.scroll_layout.itemAt(i).widget().setAlignment(
                Qt.AlignmentFlag.AlignHCenter)
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
        present_game_ids = {i.game_id for i in self.matches}

        for match in reversed(match_history):
            if match['ongoing']:
                continue
            if match['game_id'] in present_game_ids:
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
