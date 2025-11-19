from typing import Any, Dict, List

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

from overlay.aoe4_data import civ_data, map_data, mode_data
from overlay.api_checking import get_leaderboard_data
from overlay.helper_func import match_mode
from overlay.logging_func import catch_exceptions, get_logger
from overlay.settings import settings
from overlay.worker import scheldule

logger = get_logger(__name__)


class StatsTab(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.leaderboard_data: Dict[int, Dict[str, Any]] = {}
        self.match_data: List[Dict[str, Any]] = []
        self.initUI()

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 5)
        main_layout.setSpacing(10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(main_layout)

        ### Mode stats
        mode_frame = QtWidgets.QGroupBox("Mode stats")
        main_layout.addWidget(mode_frame)
        layout = QtWidgets.QGridLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        mode_frame.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum,
                                 QtWidgets.QSizePolicy.Policy.Minimum)
        mode_frame.setLayout(layout)
        mode_frame.setMaximumSize(900, 500)

        row = 0
        layout.addWidget(QtWidgets.QLabel("Mode"), row, 0)
        layout.addWidget(QtWidgets.QLabel("Wins"), row, 1)
        layout.addWidget(QtWidgets.QLabel("Losses"), row, 2)
        layout.addWidget(QtWidgets.QLabel("Drops"), row, 3)
        layout.addWidget(QtWidgets.QLabel("Games"), row, 4)
        layout.addWidget(QtWidgets.QLabel("Winrate"), row, 5)
        layout.addWidget(QtWidgets.QLabel("Rank"), row, 6)
        layout.addWidget(QtWidgets.QLabel("Rating"), row, 7)
        layout.addWidget(QtWidgets.QLabel("Max rating"), row, 8)
        layout.addWidget(QtWidgets.QLabel("Max streak"), row, 9)

        for i in range(layout.count()):
            layout.itemAt(i).widget().setStyleSheet("font-weight: bold")

        self.mode_stats: Dict[int, Dict[str, QtWidgets.QLabel]] = dict()
        for m in mode_data:
            row += 1
            layout.addWidget(QtWidgets.QLabel(f"{m-16}v{m-16}"), row, 0)
            wins = QtWidgets.QLabel("–")
            losses = QtWidgets.QLabel("–")
            drops = QtWidgets.QLabel("–")
            games = QtWidgets.QLabel("–")
            winrate = QtWidgets.QLabel("–")
            rank = QtWidgets.QLabel("–")
            rating = QtWidgets.QLabel("–")
            hrating = QtWidgets.QLabel("–")
            streak = QtWidgets.QLabel("–")

            self.mode_stats[m] = {
                "wins": wins,
                "losses": losses,
                "drops": drops,
                "games": games,
                "winrate": winrate,
                "rank": rank,
                "rating": rating,
                "hrating": hrating,
                "streak": streak
            }
            for i, item in enumerate(self.mode_stats[m].values()):
                layout.addWidget(item, row, i + 1)

        ### Filtering
        slayout = QtWidgets.QHBoxLayout()
        slayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        slayout.setSpacing(5)
        main_layout.addLayout(slayout)

        # Games found
        self.games_found = QtWidgets.QLabel("Recent games analyzed: 0 (?)")
        self.games_found.setToolTip(
            "The number of analyzed games might be lower due to API not providing all data"
        )
        self.games_found.setMinimumWidth(200)
        self.games_found.setStyleSheet("QLabel {font-weight: bold}")
        slayout.addWidget(self.games_found)
        slayout.addItem(QtWidgets.QSpacerItem(40, 0))

        # Filtering mode label
        mode = QtWidgets.QLabel("Filter mode:")
        mode.setStyleSheet("font-weight: bold")
        slayout.addWidget(mode)

        # Filtering mode combobox
        self.mode_box = QtWidgets.QComboBox()
        self.mode_box.setMaximumWidth(200)
        self.mode_box.setToolTip("Filter data for a mode")
        slayout.addWidget(self.mode_box)
        self.mode_box.addItem("All")
        for mode in mode_data.values():
            self.mode_box.addItem(mode)
        self.mode_box.currentIndexChanged.connect(self.update_civ_map_stats)
        slayout.addItem(QtWidgets.QSpacerItem(20, 0))

        # Filtering civ label
        note = QtWidgets.QLabel("Filter civilization:")
        note.setStyleSheet("font-weight: bold")
        slayout.addWidget(note)

        # Filtering civ combobox
        self.civ_box = QtWidgets.QComboBox()
        self.civ_box.setMaximumWidth(200)
        self.civ_box.setToolTip("Filter data for a civilization")
        slayout.addWidget(self.civ_box)
        self.civ_box.addItem("All")
        for civ in civ_data.values():
            self.civ_box.addItem(civ)
        self.civ_box.currentIndexChanged.connect(self.update_civ_map_stats)

        ### Results
        result_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(result_layout)

        ### Civ stats
        civ_group = QtWidgets.QGroupBox("Civilization stats")
        result_layout.addWidget(civ_group)
        civg_layout = QtWidgets.QGridLayout()
        civg_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
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
            self.civ_widgets[civ]['name'].setMinimumWidth(130)
            civg_layout.addWidget(self.civ_widgets[civ]['name'], row, 0)
            self.civ_widgets[civ]['wins'] = QtWidgets.QLabel("–")
            civg_layout.addWidget(self.civ_widgets[civ]['wins'], row, 1)
            self.civ_widgets[civ]['losses'] = QtWidgets.QLabel("–")
            civg_layout.addWidget(self.civ_widgets[civ]['losses'], row, 2)
            self.civ_widgets[civ]['winrate'] = QtWidgets.QLabel("–")
            civg_layout.addWidget(self.civ_widgets[civ]['winrate'], row, 3)

        # Map stats
        map_group = QtWidgets.QGroupBox("Map stats")
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
            self.map_widgets[m]['name'].setMinimumWidth(130)
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
        if leaderboard is None:
            logger.warning("No leaderboard data")
            return
        self.leaderboard_data = leaderboard
        self.update_leaderboard_widgets()

    @catch_exceptions(logger)
    def update_leaderboard_widgets(self):
        for m, data in self.leaderboard_data.items():
            if not data.get('leaderboard', False):
                for widget in self.mode_stats[m].values():
                    widget.setText("–")
                continue

            data = data['leaderboard'][0]
            self.mode_stats[m]['wins'].setText(str(data['wins']))
            self.mode_stats[m]['losses'].setText(str(data['losses']))
            self.mode_stats[m]['games'].setText(str(data['games']))
            self.mode_stats[m]['drops'].setText(str(data['drops']))
            self.mode_stats[m]['rank'].setText(str(data['rank']))
            self.mode_stats[m]['rating'].setText(str(data['rating']))
            self.mode_stats[m]['hrating'].setText(str(data['highest_rating']))
            self.mode_stats[m]['streak'].setText(str(data['highest_streak']))
            games = data['wins'] + data['losses']
            winrate = data['wins'] / games if games else 0
            self.mode_stats[m]['winrate'].setText(f"{winrate:.2%}")

    @catch_exceptions(logger)
    def update_other_stats(self, match_history: List[Any]):
        # Add to our match history data
        present_match_ids = {m['match_id'] for m in self.match_data}
        for match in reversed(match_history):
            if match['match_id'] not in present_match_ids:
                self.add_match_data(match)
        self.update_civ_map_stats()
        logger.info(
            f'Received {len(match_history)} | Saved {len(self.match_data)} games'
        )

    @catch_exceptions(logger)
    def add_match_data(self, match: Dict[str, Any]):
        """ Saves only specific data from the match history data"""
        game = dict()  # includes: win, mode, map, civ
        if match['result'] not in {"Loss", "Win"}:
            return
        game['map'] = match.get('map_type', -1)
        game['win'] = match['result'] == "Win"
        game['mode'] = match_mode(match)
        game['match_id'] = match['match_id']
        for player in match['players']:
            if player['profile_id'] == settings.profile_id:
                game['civ'] = player['civ']
                break
        if 'civ' not in game:
            return
        self.match_data.append(game)

    def clear_match_data(self):
        self.match_data = []
        self.update_civ_map_stats()

    @catch_exceptions(logger)
    def update_civ_map_stats(self):
        # Filter games based on the selected civilization
        fdata = self.match_data
        if self.civ_box.currentIndex() != 0:
            filter_civ = self.civ_box.currentIndex() - 1
            fdata = [g for g in self.match_data if g['civ'] == filter_civ]

        # Filter games based on the selected mode
        if self.mode_box.currentIndex() != 0:
            filter_mode = self.mode_box.currentIndex() + 16
            fdata = [g for g in fdata if g['mode'] == filter_mode]

        # Update the number of analyzed games
        self.games_found.setText(f"Recent games analyzed: {len(fdata)} (?)")

        # Get specific civ and map data from filtered games
        civ_stats = {c_index: {"wins": 0, "losses": 0} for c_index in civ_data}
        map_stats = {m_index: {"wins": 0, "losses": 0} for m_index in map_data}
        # game = {"map": None, "win": None, "mode": None, "civ": None}
        for game in fdata:
            c = game['civ']
            m = game['map']
            if game['win']:
                civ_stats[c]['wins'] += 1
                map_stats[m]['wins'] += 1
            else:
                civ_stats[c]['losses'] += 1
                map_stats[m]['losses'] += 1

        # Update civ widgets
        for civ_index, c_data in civ_stats.items():
            civ_name = civ_data[civ_index]
            swins = str(c_data['wins']) if c_data['wins'] else "–"
            self.civ_widgets[civ_name]['wins'].setText(swins)
            slosses = str(c_data['losses']) if c_data['losses'] else "–"
            self.civ_widgets[civ_name]['losses'].setText(slosses)
            games = c_data['wins'] + c_data['losses']
            swinrate = f"{c_data['wins']/games:.1%}" if games else "–"
            self.civ_widgets[civ_name]['winrate'].setText(swinrate)

        # Update map widgets
        for map_index, m_data in map_stats.items():
            map_name = map_data[map_index]
            swins = str(m_data['wins']) if m_data['wins'] else "–"
            self.map_widgets[map_name]['wins'].setText(swins)
            slosses = str(m_data['losses']) if m_data['losses'] else "–"
            self.map_widgets[map_name]['losses'].setText(slosses)
            games = m_data['wins'] + m_data['losses']
            swinrate = f"{m_data['wins']/games:.1%}" if games else "–"
            self.map_widgets[map_name]['winrate'].setText(swinrate)
