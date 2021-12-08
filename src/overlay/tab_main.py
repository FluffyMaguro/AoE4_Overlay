import webbrowser
from functools import partial

from PyQt5 import QtWidgets

from overlay.helper_func import version_check
from overlay.logging_func import get_logger
from overlay.tab_games import MatchHistoryTab
from overlay.tab_graphs import GraphTab
from overlay.tab_random import RandomTab
from overlay.tab_settings import SettingsTab
from overlay.tab_stats import StatsTab

logger = get_logger(__name__)


class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.match_history_tab = MatchHistoryTab(self)
        self.graph_tab = GraphTab(self)
        self.random_tab = RandomTab(self)
        self.stats_tab = StatsTab(self)
        # Need this one defined the last
        self.main_tab = SettingsTab(self)

        self.addTab(self.main_tab, "Settings")
        self.addTab(self.graph_tab, "Rating")
        self.addTab(self.stats_tab, "Stats")
        self.addTab(self.match_history_tab, "Games")
        self.addTab(self.random_tab, "Randomize")

    def check_for_new_version(self, version: str):
        """ Checks for a new version, creates a button if there is one """
        link = version_check(version)
        if not link:
            return
        logger.info("New version available!")
        self.update_button.clicked.connect(partial(webbrowser.open, link))
        self.update_button.show()
