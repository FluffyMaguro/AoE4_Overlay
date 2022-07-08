import json

import keyboard
from PyQt5 import QtCore, QtGui, QtWidgets

from overlay.custom_widgets import CustomKeySequenceEdit, OverlayWidget
from overlay.logging_func import catch_exceptions, get_logger
from overlay.settings import settings

from overlay.build_order_tools import check_valid_aoe4_build_order_from_string, MultiQLabelDisplay

logger = get_logger(__name__)


class BuildOrderOverlay(QtWidgets.QMainWindow):
    """Overlay widget showing the selected build order"""

    def __init__(self, parent=None):
        """Constructor

        Parameters
        ----------
        parent    parent of the widget
        """
        super().__init__(parent)
        self.show()

        # color and opacity
        self.setStyleSheet(
            f'background-color: rgb({settings.bo_color_background[0]}, {settings.bo_color_background[1]},'
            f'{settings.bo_color_background[2]})')
        self.setWindowOpacity(settings.bo_opacity)

        # window is transparent and stays on top
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint
                            | QtCore.Qt.WindowTransparentForInput
                            | QtCore.Qt.WindowStaysOnTopHint
                            | QtCore.Qt.CoverWindow
                            | QtCore.Qt.NoDropShadowWindowHint
                            | QtCore.Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        # build order display
        self.build_order_notes = MultiQLabelDisplay(
            font_police='Arial', font_size=settings.bo_font_size, image_height=30, border_size=15, vertical_spacing=10,
            color_default=[255, 255, 255], game_pictures_folder='.')

        self.show()

    def update_build_order_display(self, data: dict):
        self.build_order_notes.clear()
        self.build_order_notes.add_row_from_picture_line(parent=self,
                                                         line='First line is longer than the second line.')
        self.build_order_notes.add_row_from_picture_line(parent=self, line='Second line.')
        self.build_order_notes.add_row_from_picture_line(parent=self, line='Third line.')
        self.build_order_notes.add_row_from_picture_line(parent=self, line='Fourth line.')

        if 'notes' in data:
            notes = data['notes']
            for note in notes:
                self.build_order_notes.add_row_from_picture_line(parent=self, line=note)

        self.build_order_notes.update_size_position()

        self.resize(self.build_order_notes.row_max_width + 30, self.build_order_notes.row_total_height + 30)

        self.build_order_notes.show()


class BoTab(QtWidgets.QWidget):
    """Tab for build order configuration"""

    def __init__(self, parent):
        super().__init__(parent)
        self.overlay = BuildOrderOverlay()
        self.update_overlay()

    def update_overlay(self):
        data = json.loads(
            '{'
            '    "population_count": 10,'
            '    "villager_count": 8,'
            '    "age": 1,'
            '    "resources": {'
            '        "food": 8,'
            '        "wood": 0,'
            '        "gold": 0,'
            '        "stone": 0'
            '    },'
            '    "notes": ['
            '        "Send the first 6 @unit_worker/villager.png@ to @resource/sheep.png@. Make an additional @unit_cavalry/scout.png@.",'
            '       "Send the next 2 @unit_worker/villager.png@ to @resource/sheep.png@ (8 in total). Build a @building_economy/house.png@."'
            '    ]'
            '}')
        self.overlay.update_build_order_display(data=data)
