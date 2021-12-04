from typing import Any, Dict, Optional

from PyQt5 import QtCore, QtGui, QtWidgets

from overlay.logging_func import get_logger
from overlay.plotting import Figure
from overlay.settings import settings
from overlay.worker import Worker

logger = get_logger(__name__)


class GraphTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        # Graph
        self.graph = QtWidgets.QLabel(self)

        # Refresh button
        refresh = QtWidgets.QPushButton("Rescale", self)
        refresh.clicked.connect(self.plot_data)
        refresh.move(QtCore.QPoint(10, 10))

        # ** get data somewhere
        # cache data for rescaling
        self.data = self.get_rating_debug_3v3()

        # Demo plotting
        self.plot_data()

    def plot_data(self):
        # Update size
        new_width = self.parent().parent().width()
        new_height = self.parent().parent().height()
        self.graph.setGeometry(0, 0, new_width, new_height)

        # Demo of plotting
        y = [i['rating'] for i in self.data]
        x = list(range(len(y)))

        fig = Figure("Basic chart", new_width, new_height)
        fig.plot(x, y, label="3v3 rating")
        self.graph.setPixmap(fig.get_pixmap())

    def get_rating_debug_3v3(self):
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
