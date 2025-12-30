from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List
import webbrowser

from PyQt5 import QtCore, QtGui, QtWidgets

from overlay.logging_func import catch_exceptions, get_logger
from overlay.settings import settings

logger = get_logger(__name__)


class MatchTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._matches: List[Dict[str, Any]] = []
        self._headers = ["Team 1", "Team 2", "Map", "Started", "Mode", "Result", "Rating diff", "AoE4World"]

    def rowCount(self, parent=QtCore.QModelIndex()) -> int:
        return len(self._matches)

    def columnCount(self, parent=QtCore.QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        match_data = self._matches[index.row()]
        col = index.column()

        # Identify main player and teams (cached logic could be better, but this is fast enough)
        main_player_data = None
        main_team_idx = 0
        for team_idx, team in enumerate(match_data['teams']):
            for player in team:
                if player['player']['profile_id'] == settings.profile_id:
                    main_team_idx = team_idx
                    main_player_data = player['player']
                    break
        
        if role == QtCore.Qt.DisplayRole:
            if col == 0: # Team 1 (Main Team)
                return self._format_team(match_data, main_team_idx)
            elif col == 1: # Team 2 (Opponent)
                other_team_idx = 1 if main_team_idx == 0 else 0
                return self._format_team(match_data, other_team_idx)
            elif col == 2: # Map
                return match_data.get('map', "Unknown map")
            elif col == 3: # Started
                try:
                    started = datetime.strptime(match_data['started_at'], "%Y-%m-%dT%H:%M:%S.000Z")
                    return started.strftime("%b %d, %H:%M:%S")
                except ValueError:
                    return match_data['started_at']
            elif col == 4: # Mode
                return match_data.get('kind', '')
            elif col == 5: # Result
                if main_player_data and main_player_data.get('result'):
                    return main_player_data['result'].capitalize()
                return "?"
            elif col == 6: # Rating diff
                if main_player_data and main_player_data.get('rating_diff'):
                    return str(main_player_data['rating_diff'])
                return "?"
            elif col == 7: # Link text
                return "Game Link"

        elif role == QtCore.Qt.TextAlignmentRole:
            if col in [0, 1]:
                return QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
            return QtCore.Qt.AlignCenter

        elif role == QtCore.Qt.ForegroundRole:
            if col == 5: # Result color
                result = main_player_data.get('result') if main_player_data else None
                if result == 'win':
                    return QtGui.QColor("#48bd21")
                elif result == 'loss':
                    return QtGui.QColor("red")
            elif col == 7: # Link color
                return QtGui.QColor("#7ab6ff")
        
        elif role == QtCore.Qt.FontRole:
            if col == 7:
                font = QtGui.QFont()
                font.setUnderline(True)
                return font
            if col in [0, 1]: # Teams
                font = QtGui.QFont()
                # font.setPointSize(9) 
                return font

        return None

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole) -> Any:
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._headers[section]
        return None

    def _format_team(self, match_data, team_idx):
        if team_idx >= len(match_data['teams']):
            return "-"
        
        lines = []
        for player in match_data['teams'][team_idx]:
            name = player['player']['name']
            civ = player['player']['civilization'].replace("_", " ").capitalize()
            lines.append(f"{name} ({civ})")
        return "\n".join(lines)

    def set_matches(self, matches: List[Dict[str, Any]]):
        self.beginResetModel()
        self._matches = matches
        self.endResetModel()

    def add_matches(self, new_matches: List[Dict[str, Any]]):
        if not new_matches:
            return
        # Filter duplicates
        current_ids = {m['game_id'] for m in self._matches}
        unique_matches = [m for m in new_matches if m['game_id'] not in current_ids]
        
        if not unique_matches:
            return

        self.beginInsertRows(QtCore.QModelIndex(), len(self._matches), len(self._matches) + len(unique_matches) - 1)
        self._matches.extend(unique_matches)
        self.endInsertRows()

    def get_match_at(self, row):
        if 0 <= row < len(self._matches):
            return self._matches[row]
        return None


class MatchHistoryTab(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.model = MatchTableModel(self)
        self.view = QtWidgets.QTableView(self)
        self.view.setModel(self.model)
        
        # Appearance
        self.view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.view.alternatingRowColors()
        self.view.verticalHeader().setVisible(False)
        self.view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.view.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.view.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.view.setShowGrid(True)
        self.view.setWordWrap(True)

        # Connect click for links
        self.view.clicked.connect(self.on_click)

        self.layout.addWidget(self.view)

    def clear_games(self):
        self.model.set_matches([])

    def on_click(self, index: QtCore.QModelIndex):
        if index.column() == 7: # Link column
            match = self.model.get_match_at(index.row())
            if match:
                game_id = match.get("game_id")
                url = f"https://aoe4world.com/players/{settings.profile_id}/games/{game_id}"
                webbrowser.open(url)

    @catch_exceptions(logger)
    def update_widgets(self, match_history: List[Any]):
        """ 
        Updates the table with new matches.
        """
        # Filter out ongoing matches to match legacy behavior
        filtered_history = [m for m in match_history if not m.get('ongoing')]
        
        self.model.set_matches(filtered_history)
        self.view.resizeRowsToContents()