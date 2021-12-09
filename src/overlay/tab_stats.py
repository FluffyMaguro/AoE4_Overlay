from typing import Any, Dict, List

from PyQt5 import QtCore, QtWidgets

from overlay.aoe4_data import mode_data
from overlay.api_checking import get_leaderboard_data
from overlay.logging_func import get_logger
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
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(main_layout)

        ### Mode stats
        mode_frame = QtWidgets.QFrame()
        main_layout.addWidget(mode_frame)
        layout = QtWidgets.QGridLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setContentsMargins(10, 10, 10, 10)
        mode_frame.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                 QtWidgets.QSizePolicy.Minimum)
        mode_frame.setLayout(layout)
        mode_frame.setMaximumSize(900, 500)
        mode_frame.setAutoFillBackground(True)

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

        ### Other stats
        

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

        print("We have now", len(self.match_history_data),
              "matches for stats!")
