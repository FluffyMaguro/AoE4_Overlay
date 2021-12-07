import time
from typing import Any, Dict, List, Optional

from PyQt5 import QtCore, QtGui, QtWidgets

from overlay.graph_widget import GraphWidget
from overlay.logging_func import get_logger
from overlay.settings import settings
from overlay.worker import scheldule

logger = get_logger(__name__)



class GraphTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # self.setAutoFillBackground(True)
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # Graph
        self.test_graph = GraphWidget()
        layout.addWidget(self.test_graph)

        # self.test_graph2 = GraphWidget()
        # layout.addWidget(self.test_graph2)

        # Get data
        scheldule(self.get_data_finished, self.get_rating_debug_3v3)


    def get_data_finished(self, data: List[Any]):
        self.data = data
        self.plot_data()

    def plot_data(self):
        # Demo of plotting
        y = [i['rating'] for i in self.data]
        x = list(range(len(y)))

        self.test_graph.title="3v3 Rating history"
        self.test_graph.x_label = "Games"
        self.test_graph.y_label = "Rating"
        self.test_graph.plot(x, y, label="3v3 rating")
        self.test_graph.plot(x, [i+100 for i in y], label="3v3 rating2")
        self.test_graph.text("Some text", 2, 1100)

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
