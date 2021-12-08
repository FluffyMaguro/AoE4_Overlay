import webbrowser
from functools import partial
from typing import Any, Dict, Optional

from PyQt5 import QtWidgets

from overlay.api_checking import API_checker
from overlay.helper_func import version_check
from overlay.logging_func import get_logger
from overlay.settings import settings
from overlay.tab_games import MatchHistoryTab
from overlay.tab_graphs import GraphTab
from overlay.tab_random import RandomTab
from overlay.tab_settings import SettingsTab
from overlay.tab_stats import StatsTab
from overlay.worker import scheldule

logger = get_logger(__name__)


class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.api_checker = API_checker()
        self.force_stop = False

        self.games_tab = MatchHistoryTab(self)
        self.graph_tab = GraphTab(self)
        self.random_tab = RandomTab(self)
        self.stats_tab = StatsTab(self)
        self.settigns_tab = SettingsTab(self)
        self.settigns_tab.new_profile.connect(self.new_profile_found)

        self.addTab(self.settigns_tab, "Settings")
        self.addTab(self.graph_tab, "Rating")
        self.addTab(self.stats_tab, "Stats")
        self.addTab(self.games_tab, "Games")
        self.addTab(self.random_tab, "Randomize")

    def start(self):
        self.settigns_tab.start()

        # DEBUG START
        self.debug()  # Remove later
        self.settigns_tab.overlay_widget.hide()
        # DEBUG END

        # self.run_new_game_check()

    def new_profile_found(self):
        self.graph_tab.run_update()
        self.stats_tab.run_update()
        self.games_tab.clear_games()
        self.games_tab.run_update(100)
        self.parent().update_title(settings.player_name)

    def check_for_new_version(self, version: str):
        """ Checks for a new version, creates a button if there is one """
        link = version_check(version)
        if not link:
            return
        logger.info("New version available!")
        self.update_button.clicked.connect(partial(webbrowser.open, link))
        self.update_button.show()

    def stop_checking_api(self):
        """ The app is closing, we need to start shuttings things down"""
        self.force_stop = True
        self.api_checker.force_stop = True

    def run_new_game_check(self, delayed_seconds: int = 0):
        """ Creates a new thread for a new api check"""
        scheldule(self.got_new_game, self.api_checker.check_for_new_game,
                  delayed_seconds)

    def got_new_game(self, game_data: Optional[Dict[str, Any]]):
        """Received new data from api check, passes data along and reruns the check"""
        if self.force_stop:
            return

        if game_data is not None:
            logger.info("New game. Updating...")
            self.settigns_tab.overlay_widget.update_data(game_data)
            self.graph_tab.run_update()
            self.stats_tab.run_update()
            self.games_tab.run_update(3)

        self.run_new_game_check(delayed_seconds=30)

    def debug(self):
        self.settigns_tab.overlay_widget.update_data({
            'lobby_id':
            '109775240919138141',
            'map_size':
            3,
            'map_type':
            9,
            'match_id':
            '12595190',
            'name':
            'AUTOMATCH',
            'num_players':
            6,
            'num_slots':
            6,
            'players': [{
                'civ': 4,
                'clan': None,
                'color': None,
                'country': None,
                'losses': 5,
                'name': 'Mini-Negan',
                'profile_id': 5636932,
                'rank': 12570,
                'rating': 1105,
                'rating_change': None,
                'slot': 1,
                'slot_type': 1,
                'streak': -1,
                'team': 1,
                'wins': 8,
                'won': None
            }, {
                'civ': 5,
                'clan': None,
                'color': None,
                'country': None,
                'name': 'Iotawolf101',
                'profile_id': 181552,
                'rating': None,
                'rating_change': None,
                'slot': 3,
                'slot_type': 1,
                'team': 1,
                'won': None
            }, {
                'civ': 1,
                'clan': None,
                'color': None,
                'country': None,
                'losses': 8,
                'name': 'Maguro',
                'profile_id': 5233600,
                'rank': 17708,
                'rating': 1063,
                'rating_change': None,
                'slot': 2,
                'slot_type': 1,
                'streak': 1,
                'team': 1,
                'wins': 9,
                'won': None
            }, {
                'civ': 3,
                'clan': None,
                'color': None,
                'country': None,
                'losses': 5,
                'name': 'Kanax',
                'profile_id': 6703549,
                'rank': 27902,
                'rating': 990,
                'rating_change': None,
                'slot': 4,
                'slot_type': 1,
                'streak': -2,
                'team': 2,
                'wins': 5,
                'won': None
            }, {
                'civ': 5,
                'clan': None,
                'color': None,
                'country': None,
                'losses': 62,
                'name': 'lebowskiiiiiiiii',
                'profile_id': 684531,
                'rank': 29512,
                'rating': 979,
                'rating_change': None,
                'slot': 5,
                'slot_type': 1,
                'streak': -1,
                'team': 2,
                'wins': 54,
                'won': None
            }, {
                'civ': 6,
                'clan': None,
                'color': None,
                'country': None,
                'name': 'gcdomi7872',
                'profile_id': 5971541,
                'rating': None,
                'rating_change': None,
                'slot': 6,
                'slot_type': 1,
                'team': 2,
                'won': None
            }],
            'ranked':
            False,
            'rating_type_id':
            17,
            'server':
            'ukwest',
            'started':
            1638493446,
            'version':
            '8324'
        })
