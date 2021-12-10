from typing import Any, Dict, List

from PyQt5 import QtCore, QtWidgets

from overlay.aoe4_data import civ_data, map_data, mode_data
from overlay.api_checking import get_leaderboard_data
from overlay.logging_func import get_logger
from overlay.settings import settings
from overlay.worker import scheldule

logger = get_logger(__name__)


class StatsTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.leaderboard_data: Dict[int, Dict[str, Any]] = {}
        self.match_history_data: List[Dict[str, Any]] = []
        self.initUI()

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(10, 20, 10, 10)
        main_layout.setSpacing(20)
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(main_layout)

        ### Mode stats
        mode_frame = QtWidgets.QGroupBox("Mode")
        main_layout.addWidget(mode_frame)
        layout = QtWidgets.QGridLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setContentsMargins(10, 10, 10, 10)
        mode_frame.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                 QtWidgets.QSizePolicy.Minimum)
        mode_frame.setLayout(layout)
        mode_frame.setMaximumSize(900, 500)

        row = 0
        layout.addWidget(QtWidgets.QLabel("Mode"), row, 0)
        layout.addWidget(QtWidgets.QLabel("Wins"), row, 1)
        layout.addWidget(QtWidgets.QLabel("Losses"), row, 2)
        layout.addWidget(QtWidgets.QLabel("Drops"), row, 3)
        layout.addWidget(QtWidgets.QLabel("Winrate"), row, 4)
        layout.addWidget(QtWidgets.QLabel("Rating"), row, 5)
        layout.addWidget(QtWidgets.QLabel("Streak"), row, 6)

        for i in range(layout.count()):
            layout.itemAt(i).widget().setStyleSheet("font-weight: bold")

        self.mode_stats: Dict[int, Dict[str, QtWidgets.QLabel]] = dict()
        for m in mode_data:
            row += 1
            layout.addWidget(QtWidgets.QLabel(f"{m-16}v{m-16}"), row, 0)
            wins = QtWidgets.QLabel("–")
            losses = QtWidgets.QLabel("–")
            drops = QtWidgets.QLabel("–")
            winrate = QtWidgets.QLabel("–")
            rating = QtWidgets.QLabel("–")
            streak = QtWidgets.QLabel("–")

            self.mode_stats[m] = {
                "wins": wins,
                "losses": losses,
                "drops": drops,
                "winrate": winrate,
                "rating": rating,
                "streak": streak
            }
            for i, item in enumerate(self.mode_stats[m].values()):
                layout.addWidget(item, row, i + 1)

        ### Filtering
        slayout = QtWidgets.QHBoxLayout()
        slayout.setAlignment(QtCore.Qt.AlignLeft)
        main_layout.addLayout(slayout)

        # Note
        note = QtWidgets.QLabel("Filter civilization:")
        note.setStyleSheet("font-weight: bold")
        slayout.addWidget(note)

        # Civ combobox
        self.civ_box = QtWidgets.QComboBox()
        self.civ_box.setMaximumWidth(200)
        self.civ_box.setToolTip("Filter data for a civilization")
        slayout.addWidget(self.civ_box)
        self.civ_box.addItem("All")
        for civ in civ_data.values():
            self.civ_box.addItem(civ)
        self.civ_box.currentIndexChanged.connect(self.calculate_other_stats)

        # Games found
        self.games_found = QtWidgets.QLabel("→ Valid games: 0")
        self.games_found.setStyleSheet("font-weight: bold")
        slayout.addWidget(self.games_found)

        ### Results
        result_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(result_layout)

        ### Civ stats
        civ_group = QtWidgets.QGroupBox("Civilizations")
        result_layout.addWidget(civ_group)
        civg_layout = QtWidgets.QGridLayout()
        civg_layout.setAlignment(QtCore.Qt.AlignTop)
        civ_group.setLayout(civg_layout)

        # Civ headers
        civ_headers = []
        civ_headers.append(QtWidgets.QLabel("Civilization"))
        civ_headers.append(QtWidgets.QLabel("Wins"))
        civ_headers.append(QtWidgets.QLabel("Losses"))
        civ_headers.append(QtWidgets.QLabel("Winrate"))

        for column, widget in enumerate(civ_headers):
            civg_layout.addWidget(widget, 0, column)
            widget.setStyleSheet("font-weight: bold")

        # Add civs
        self.civ_widgets = {}
        for row, civ in enumerate(civ_data.values()):
            row += 1
            self.civ_widgets[civ] = dict()
            self.civ_widgets[civ]['name'] = QtWidgets.QLabel(civ)
            civg_layout.addWidget(self.civ_widgets[civ]['name'], row, 0)
            self.civ_widgets[civ]['wins'] = QtWidgets.QLabel("–")
            civg_layout.addWidget(self.civ_widgets[civ]['wins'], row, 1)
            self.civ_widgets[civ]['losses'] = QtWidgets.QLabel("–")
            civg_layout.addWidget(self.civ_widgets[civ]['losses'], row, 2)
            self.civ_widgets[civ]['winrate'] = QtWidgets.QLabel("–")
            civg_layout.addWidget(self.civ_widgets[civ]['winrate'], row, 3)

        # Map stats
        map_group = QtWidgets.QGroupBox("Maps")
        result_layout.addWidget(map_group)
        map_layout = QtWidgets.QGridLayout()
        map_group.setLayout(map_layout)

        # Map headers
        map_headers = []
        map_headers.append(QtWidgets.QLabel("Map"))
        map_headers.append(QtWidgets.QLabel("Wins"))
        map_headers.append(QtWidgets.QLabel("Losses"))
        map_headers.append(QtWidgets.QLabel("Winrate"))

        for column, widget in enumerate(map_headers):
            map_layout.addWidget(widget, 0, column)
            widget.setStyleSheet("font-weight: bold")

        # Add maps
        self.map_widgets = {}
        for row, m in enumerate(map_data.values()):
            row += 1
            self.map_widgets[m] = dict()
            self.map_widgets[m]['name'] = QtWidgets.QLabel(m)
            map_layout.addWidget(self.map_widgets[m]['name'], row, 0)
            self.map_widgets[m]['wins'] = QtWidgets.QLabel("–")
            map_layout.addWidget(self.map_widgets[m]['wins'], row, 1)
            self.map_widgets[m]['losses'] = QtWidgets.QLabel("–")
            map_layout.addWidget(self.map_widgets[m]['losses'], row, 2)
            self.map_widgets[m]['winrate'] = QtWidgets.QLabel("–")
            map_layout.addWidget(self.map_widgets[m]['winrate'], row, 3)

    def run_mode_update(self):
        """ Runs update for mode stats"""
        scheldule(self.update_leaderboard_data, self.get_all_leaderboard_data)

    def get_all_leaderboard_data(self):
        result = dict()
        for leaderboard_id in mode_data:
            result[leaderboard_id] = get_leaderboard_data(leaderboard_id)
        return result

    def update_leaderboard_data(self, leaderboard: Dict[int, Dict[str, Any]]):
        """ Update data and widgets"""
        self.leaderboard_data = leaderboard
        self.update_leaderboard_widgets()

    def update_leaderboard_widgets(self):
        for m, data in self.leaderboard_data.items():
            if not data.get('leaderboard', False):
                for widget in self.mode_stats[m].values():
                    widget.setText("–")
                continue

            data = data['leaderboard'][0]
            self.mode_stats[m]['wins'].setText(str(data['wins']))
            self.mode_stats[m]['losses'].setText(str(data['losses']))
            self.mode_stats[m]['drops'].setText(str(data['drops']))
            self.mode_stats[m]['rating'].setText(str(data['rating']))
            self.mode_stats[m]['streak'].setText(str(data['streak']))
            games = data['wins'] + data['losses'] + data['drops']
            winrate = data['wins'] / games if games else 0
            self.mode_stats[m]['winrate'].setText(f"{winrate:.2%}")

    def update_other_stats(self, match_history: List[Any]):
        # Add to our match history data
        present_match_ids = {i['match_id'] for i in self.match_history_data}
        for match in reversed(match_history):
            if match['match_id'] not in present_match_ids:
                self.match_history_data.append(match)
        self.calculate_other_stats()

    def calculate_other_stats(self):
        """ Calculates and updates other stats"""

        # Get the useful information from matches
        data = []
        for match in self.match_history_data:
            game = {"map": None, "win": None, "mode": None, "civ": None}
            if match['result'] not in {"Loss", "Win"}:
                continue
            game['map'] = match['map_type']
            game['win'] = match['result'] == "Win"
            game['mode'] = match['rating_type_id'] + 2
            for player in match['players']:
                if player['profile_id'] == settings.profile_id:
                    game['civ'] = player['civ']
                    break
            data.append(game)

        # Filter games based on the selected civilization
        filter_civ = self.civ_box.currentIndex() - 1
        if filter_civ != -1:
            filtered_games = [g for g in data if g['civ'] == filter_civ]
        else:
            filtered_games = data

        print(
            f"Filtering {len(self.match_history_data)} → {len(data)} → {len(filtered_games)}"
        )
        self.games_found.setText(f"→ Valid games: {len(filtered_games)}")

        ### !!! Update map and civ data
