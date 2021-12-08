import random

from PyQt5 import QtCore, QtGui, QtWidgets

from overlay.aoe4_data import civ_data, map_data
from overlay.helper_func import file_path


class RandomTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.current_map = None
        self.current_civ = None

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(10, 40, 10, 10)
        self.setLayout(layout)

        # Civ layout
        civ_layout = QtWidgets.QVBoxLayout()
        civ_layout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        layout.addLayout(civ_layout)

        spacer = QtWidgets.QLabel()
        spacer.setMinimumHeight(50)
        civ_layout.addWidget(spacer)

        # Civ image
        self.civ_image = QtWidgets.QLabel()
        self.civ_image.setFixedSize(QtCore.QSize(270, 150))
        civ_layout.addWidget(self.civ_image)

        # Civ label
        self.civ_label = QtWidgets.QLabel()
        self.civ_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.civ_label.setStyleSheet("font-weight: bold; font-size: 20px")
        civ_layout.addWidget(self.civ_label)

        spacer = QtWidgets.QLabel()
        spacer.setMinimumHeight(84)
        civ_layout.addWidget(spacer)

        # Randomize civ
        rnd_civ = QtWidgets.QPushButton("Randomize civ")
        rnd_civ.clicked.connect(self.randomize_civ)
        rnd_civ.setMinimumHeight(30)
        civ_layout.addWidget(rnd_civ)

        # Map layout
        map_layout = QtWidgets.QVBoxLayout()
        map_layout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        layout.addLayout(map_layout)

        # Map image
        self.map_image = QtWidgets.QLabel()
        self.map_image.setFixedSize(QtCore.QSize(270, 270))
        map_layout.addWidget(self.map_image)

        # Map label
        self.map_label = QtWidgets.QLabel()
        self.map_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.map_label.setStyleSheet("font-weight: bold; font-size: 20px")
        map_layout.addWidget(self.map_label)

        spacer = QtWidgets.QLabel()
        spacer.setMinimumHeight(20)
        map_layout.addWidget(spacer)

        # Randomize map
        rnd_map = QtWidgets.QPushButton("Randomize map")
        rnd_map.clicked.connect(self.randomize_map)
        rnd_map.setMinimumHeight(30)
        map_layout.addWidget(rnd_map)

        # Initial randomize
        self.randomize_map()
        self.randomize_civ()

    def randomize_civ(self):
        civ_name = random.choice(tuple(civ_data.values()))
        if civ_name == self.current_civ:
            self.randomize_civ()
            return
        self.current_civ = civ_name

        img_path = file_path(f"src/img/flags/{civ_name}.webp")
        pixmap = QtGui.QPixmap(img_path)
        pixmap = pixmap.scaled(self.civ_image.width(), self.civ_image.height(),
                               QtCore.Qt.KeepAspectRatio,
                               QtCore.Qt.FastTransformation)
        self.civ_image.setPixmap(pixmap)
        self.civ_label.setText(civ_name)

    def randomize_map(self):
        map_name = random.choice(tuple(map_data.values()))
        if map_name == self.current_map:
            self.randomize_map()
            return
        self.current_map = map_name

        img_path = file_path(f"src/img/maps/{map_name.replace(' ','_')}.png")
        pixmap = QtGui.QPixmap(img_path)
        pixmap = pixmap.scaled(self.map_image.width(), self.map_image.height(),
                               QtCore.Qt.KeepAspectRatio,
                               QtCore.Qt.FastTransformation)
        self.map_image.setPixmap(pixmap)
        self.map_label.setText(map_name)
