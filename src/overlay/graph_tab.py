import time
from typing import Any, Dict, List, Optional

from PyQt5 import QtCore, QtGui, QtWidgets

from overlay.logging_func import get_logger
from overlay.plotting import Figure
from overlay.settings import settings
from overlay.worker import scheldule

logger = get_logger(__name__)


class GraphTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        # Graph
        self.graph = QtWidgets.QLabel(self)

        # Refresh button
        refresh = QtWidgets.QPushButton("Rescale", self)
        refresh.setStatusTip("Rescales the graph based on new size")
        refresh.clicked.connect(self.plot_data)
        refresh.move(QtCore.QPoint(10, 10))

        # ** get data somewhere

        # ** PLOT Ratings, Ranks

        # Get data
        scheldule(self.get_data_finished, self.get_rating_debug_3v3)

    def get_data_finished(self, data: List[Any]):
        self.data = data
        self.plot_data()

    def plot_data(self):
        # Update size
        new_width = self.parent().parent().width()
        new_height = self.parent().parent().height() - 20
        self.graph.setGeometry(0, 0, new_width, new_height)

        # Demo of plotting
        y = [i['rating'] for i in self.data]
        x = list(range(len(y)))

        fig = Figure("3v3 Rating history", new_width, new_height)
        fig.x_label = "Games"
        fig.y_label = "Rating"
        fig.plot(x, y, label="3v3 rating")
        fig.text("Some text", 2, 1100)
        self.graph.setPixmap(fig.get_pixmap())

    def get_rating_debug_3v3(self):
        time.sleep(0.1)
        return [{
            'drops': 1,
            'num_losses': 8,
            'num_wins': 9,
            'rating': 1063,
            'streak': 1,
            'timestamp': 1638495697
        }, {
            'drops': 1,
            'num_losses': 8,
            'num_wins': 8,
            'rating': 1041,
            'streak': -4,
            'timestamp': 1638493070
        }, {
            'drops': 1,
            'num_losses': 7,
            'num_wins': 8,
            'rating': 1065,
            'streak': -3,
            'timestamp': 1638323154
        }, {
            'drops': 1,
            'num_losses': 6,
            'num_wins': 8,
            'rating': 1089,
            'streak': -2,
            'timestamp': 1638321772
        }, {
            'drops': 1,
            'num_losses': 4,
            'num_wins': 8,
            'rating': 1143,
            'streak': 4,
            'timestamp': 1638229105
        }, {
            'drops': 1,
            'num_losses': 4,
            'num_wins': 7,
            'rating': 1113,
            'streak': 3,
            'timestamp': 1638226738
        }, {
            'drops': 1,
            'num_losses': 4,
            'num_wins': 6,
            'rating': 1080,
            'streak': 2,
            'timestamp': 1637975368
        }]
