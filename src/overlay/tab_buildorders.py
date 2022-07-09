import os
import json
import pathlib

import keyboard
from PyQt5 import QtCore, QtGui, QtWidgets

from overlay.custom_widgets import CustomKeySequenceEdit
from overlay.logging_func import get_logger
from overlay.settings import settings

from overlay.build_order_tools import check_valid_aoe4_build_order_from_string, MultiQLabelDisplay, QLabelSettings

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

        file_path = str(pathlib.Path(__file__).parent.resolve())  # path of the folder containing this file
        self.directory_game_pictures = os.path.join(file_path, '..', 'img', 'build_order')  # build order pictures

        # build order display
        self.build_order_notes = MultiQLabelDisplay(
            font_police=settings.bo_font_police, font_size=settings.bo_font_size, image_height=settings.bo_image_height,
            border_size=settings.bo_border_size, vertical_spacing=settings.bo_vertical_spacing,
            color_default=settings.bo_text_color, game_pictures_folder=self.directory_game_pictures)

        self.fixed = True  # True if overlay position is fixed

        # window is transparent to mouse events, except for the configuration when not hidden
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)

        # remove the window title and stay always on top
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        # color and opacity
        color_background = settings.bo_color_background
        self.setStyleSheet(
            f'background-color: rgb({color_background[0]}, {color_background[1]}, {color_background[2]})')
        self.setWindowOpacity(settings.bo_opacity)

        # check that the upper right corner is inside the screen
        screen_size = QtWidgets.QDesktopWidget().screenGeometry(-1)

        if settings.bo_upper_right_position[0] >= screen_size.width():
            print(f'Upper right corner X position set to {(screen_size.width() - 20)} (to stay inside screen).')
            settings.bo_upper_right_position[0] = screen_size.width() - 20

        if settings.bo_upper_right_position[1] >= screen_size.height():
            print(f'Upper right corner Y position set to {(screen_size.height() - 40)} (to stay inside screen).')
            settings.bo_upper_right_position[1] = screen_size.height() - 40

        self.update_position()  # update the position

    def update_settings(self):
        """Update the overlay settings"""
        self.build_order_notes.update_settings(
            font_police=settings.bo_font_police, font_size=settings.bo_font_size,
            border_size=settings.bo_border_size, vertical_spacing=settings.bo_vertical_spacing,
            color_default=settings.bo_text_color, image_height=settings.bo_image_height)

    def update_build_order_display(self, title: str, data: dict):
        """Update the display of the build order

        Parameters
        ----------
        title    title of this build order step
        data     data from the build order in dictionary form
        """
        self.build_order_notes.clear()  # clear previous build order display

        if (settings.bo_show_title) and (title != ''):
            self.build_order_notes.add_row_from_picture_line(
                parent=self, line=title,
                labels_settings=[QLabelSettings(text_color=settings.bo_title_color, text_bold=True)])

        if 'notes' in data:  # build order with pictures
            notes = data['notes']
            for note in notes:
                self.build_order_notes.add_row_from_picture_line(parent=self, line=note)
        elif 'txt' in data:  # simple TXT file for build order:
            self.build_order_notes.add_row_from_picture_line(parent=self, line=str(data['txt']))

        self.build_order_notes.update_size_position()  # update the size and position of the build order

        # resize the window to the size of the build order
        self.resize(self.build_order_notes.row_max_width + 2 * settings.bo_border_size,
                    self.build_order_notes.row_total_height + 2 * settings.bo_border_size)

        self.build_order_notes.show()  # show the new notes
        self.update_position()  # update the position to keep the correct upper right corner position

    def show_hide(self):
        """Switch from hidden to shown (and opposite)"""
        self.hide() if self.isVisible() else self.show()
        if self.isVisible():
            self.update_position()

    def change_position_state(self):
        """Change the state from fixed position to window with moving position (and opposite)"""
        if self.fixed:  # fixed to moving
            self.fixed = False
            self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
            self.setWindowFlags(QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowStaysOnTopHint)
        else:  # moving to fixed
            self.fixed = True
            # offset added to take into account the difference of the window size with titlebar
            self.save_upper_right_position(offset_x=8, offset_y=31)
            self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def save_upper_right_position(self, offset_x: int = 0, offset_y: int = 0):
        """Save of the upper right corner position

        Parameters
        ----------
        offset_x    pixels offset to add on the X axis
        offset_y    pixels offset to add on the Y axis
        """
        settings.bo_upper_right_position = [self.x() + self.width() + offset_x, self.y() + offset_y]

    def update_position(self):
        """Update the position to stick to the saved upper right corner"""
        self.move(settings.bo_upper_right_position[0] - self.width(), settings.bo_upper_right_position[1])


def init_hotkey(hotkey_str: str, hotkey_edit: CustomKeySequenceEdit, hotkey_signal: QtCore.pyqtSignal):
    """Initialize one hotkey

    Parameters
    ----------
    hotkey_str       string containing the hotkey sequence
    hotkey_edit      field to edit the hotkey
    hotkey_signal    signal linked to this hotkey

    Returns
    -------
    updated 'hotkey_str'
    """
    if hotkey_str:
        try:
            hotkey_edit.setKeySequence(QtGui.QKeySequence.fromString(hotkey_str))
            keyboard.add_hotkey(hotkey_str, hotkey_signal.emit)
        except Exception:
            logger.exception("Failed to set hotkey.")
            hotkey_str = ""
            hotkey_edit.setKeySequence(QtGui.QKeySequence.fromString(""))
    return hotkey_str


def hotkey_changed(new_hotkey: str, hotkey_str: str,
                   hotkey_edit: CustomKeySequenceEdit, hotkey_signal: QtCore.pyqtSignal):
    """Update hotkey when changed

    Parameters
    ----------
    new_hotkey       new hotkey value
    hotkey_str       string containing the hotkey sequence
    hotkey_edit      field to edit the hotkey
    hotkey_signal    signal linked to this hotkey

    Returns
    -------
    updated 'hotkey_str'
    """
    new_hotkey = CustomKeySequenceEdit.convert_hotkey(new_hotkey)

    if new_hotkey == "Del":
        hotkey_edit.setKeySequence(QtGui.QKeySequence.fromString(""))
        return ""
    elif not new_hotkey or (new_hotkey == hotkey_str):
        return hotkey_str

    try:
        keyboard.add_hotkey(new_hotkey, hotkey_signal.emit)
        if hotkey_str:
            keyboard.remove_hotkey(hotkey_str)
        logger.info(f"Setting new build order hotkey to: {new_hotkey}")
        return new_hotkey
    except Exception:
        logger.exception(f"Failed to set hotkey: {new_hotkey}")
        hotkey_edit.setKeySequence(QtGui.QKeySequence.fromString(hotkey_str))
        return hotkey_str


class BoTab(QtWidgets.QWidget):
    """Tab used to configure the build order (BO) overlay"""
    show_hide_overlay = QtCore.pyqtSignal()  # show/hide the BO
    cycle_build_order = QtCore.pyqtSignal()  # cycle between the different BO available
    previous_step_build_order = QtCore.pyqtSignal()  # go to the previous step of the build order
    next_step_build_order = QtCore.pyqtSignal()  # go to the next step of the build order

    def __init__(self, parent):
        """Constructor

        Parameters
        ----------
        parent    parent of the widget
        """
        super().__init__(parent)

        self.build_order_step = -1  # step of the build order, negative if not valid
        self.build_order_step_count = -1  # number of steps in the build order, negative if not valid

        self.overlay = BuildOrderOverlay()  # overlay to display the build order

        # user interface
        self.bo_edit = QtWidgets.QTextEdit()  # text/json edit field
        self.naming_widget = QtWidgets.QLineEdit()  # BO name edition
        self.bo_list = QtWidgets.QListWidget()  # list of build orders
        self.font_size_combo = QtWidgets.QComboBox()  # overlay font
        self.button_change_position = QtWidgets.QPushButton("Change overlay position")  # change overlay position

        # hotkeys
        self.key_show_hide = CustomKeySequenceEdit(self)
        self.key_cycle = CustomKeySequenceEdit(self)
        self.key_previous_step = CustomKeySequenceEdit(self)
        self.key_next_step = CustomKeySequenceEdit(self)

        # connect signals
        self.show_hide_overlay.connect(self.overlay.show_hide)
        self.cycle_build_order.connect(self.cycle_overlay)
        self.previous_step_build_order.connect(self.select_previous_build_order_step)
        self.next_step_build_order.connect(self.select_next_build_order_step)

        # initialization
        self.init_ui()
        self.init_hotkeys()

        self.update_overlay()  # update the BO overlay

    def closeEvent(self, _):
        """Function called when closing the widget."""
        self.overlay.close()

    def init_hotkeys(self):
        """Initialize all the hotkeys"""
        settings.bo_overlay_hotkey_show = init_hotkey(
            hotkey_str=settings.bo_overlay_hotkey_show,
            hotkey_edit=self.key_show_hide,
            hotkey_signal=self.show_hide_overlay)

        settings.bo_overlay_hotkey_cycle = init_hotkey(
            hotkey_str=settings.bo_overlay_hotkey_cycle,
            hotkey_edit=self.key_cycle,
            hotkey_signal=self.cycle_build_order)

        settings.bo_overlay_hotkey_previous_step = init_hotkey(
            hotkey_str=settings.bo_overlay_hotkey_previous_step,
            hotkey_edit=self.key_previous_step,
            hotkey_signal=self.previous_step_build_order)

        settings.bo_overlay_hotkey_next_step = init_hotkey(
            hotkey_str=settings.bo_overlay_hotkey_next_step,
            hotkey_edit=self.key_next_step,
            hotkey_signal=self.next_step_build_order)

    def init_ui(self):
        """Initialize the user interface for the BO configuration"""
        horizontal_layout = QtWidgets.QHBoxLayout()
        self.setLayout(horizontal_layout)

        # text/json edit field
        horizontal_layout.addWidget(self.bo_edit)

        # BO control frame
        control_frame = QtWidgets.QFrame()
        control_frame.setMaximumWidth(350)
        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.setContentsMargins(0, 0, 0, 0)
        control_frame.setLayout(vertical_layout)
        horizontal_layout.addWidget(control_frame)

        # renaming build orders
        self.naming_widget.setToolTip("Adapt the build order name here")
        self.naming_widget.setTextMargins(3, 0, 0, 0)
        vertical_layout.addWidget(self.naming_widget)

        # list of build orders
        vertical_layout.addWidget(self.bo_list)
        for name in settings.build_orders:
            self.bo_list.addItem(name)
        self.bo_list.currentItemChanged.connect(self.bo_selected)
        self.bo_list.setCurrentRow(0)

        # add build order
        add_bo_button = QtWidgets.QPushButton("Add build order")
        add_bo_button.clicked.connect(self.add_build_order)
        vertical_layout.addWidget(add_bo_button)

        # remove build order
        remove_bo_btn = QtWidgets.QPushButton("Remove build order")
        remove_bo_btn.clicked.connect(self.remove_build_order)
        vertical_layout.addWidget(remove_bo_btn)

        vertical_layout.addSpacing(30)
        age4builder = QtWidgets.QLabel(
            'Find & copy build orders from <a href="https://age4builder.com/">age4builder.com</a>'
        )
        age4builder.setOpenExternalLinks(True)
        vertical_layout.addWidget(age4builder)

        # overlay control (hotkeys...)
        vertical_layout.addSpacing(10)
        overlay_box = QtWidgets.QGroupBox("Overlay")
        overlay_layout = QtWidgets.QGridLayout()
        overlay_box.setLayout(overlay_layout)
        vertical_layout.addWidget(overlay_box)

        # show/hide hotkey
        key_label = QtWidgets.QLabel("Hotkey for showing and hiding overlay:")
        overlay_layout.addWidget(key_label, 0, 0)
        self.key_show_hide.setMaximumWidth(100)
        self.key_show_hide.setToolTip("Hotkey for showing and hiding overlay.")
        overlay_layout.addWidget(self.key_show_hide, 0, 1)
        self.key_show_hide.key_changed.connect(self.show_hotkey_changed)

        # cycle hotkey
        key_label = QtWidgets.QLabel("Hotkey for cycling build orders:")
        overlay_layout.addWidget(key_label, 1, 0)
        self.key_cycle.setMaximumWidth(100)
        self.key_cycle.setToolTip("Hotkey for cycling build orders.")
        overlay_layout.addWidget(self.key_cycle, 1, 1)
        self.key_cycle.key_changed.connect(self.cycle_hotkey_changed)

        # previous build order step hotkey
        key_label = QtWidgets.QLabel("Hotkey to go to previous step:")
        overlay_layout.addWidget(key_label, 2, 0)
        self.key_previous_step.setMaximumWidth(100)
        self.key_previous_step.setToolTip("Hotkey to go to the previous step of the build order.")
        overlay_layout.addWidget(self.key_previous_step, 2, 1)
        self.key_previous_step.key_changed.connect(self.previous_step_hotkey_changed)

        # next build order step hotkey
        key_label = QtWidgets.QLabel("Hotkey to go to next step:")
        overlay_layout.addWidget(key_label, 3, 0)
        self.key_next_step.setMaximumWidth(100)
        self.key_next_step.setToolTip("Hotkey to go to the next step of the build order.")
        overlay_layout.addWidget(self.key_next_step, 3, 1)
        self.key_next_step.key_changed.connect(self.next_step_hotkey_changed)

        # overlay font
        font_label = QtWidgets.QLabel("Overlay font size:")
        overlay_layout.addWidget(font_label, 4, 0)
        for i in range(1, 50):
            self.font_size_combo.addItem(f"{i} pt")
        self.font_size_combo.setCurrentIndex(settings.bo_font_size - 1)
        self.font_size_combo.currentIndexChanged.connect(self.font_size_changed)
        overlay_layout.addWidget(self.font_size_combo, 4, 1)

        # Position change button
        self.button_change_position.setToolTip("Click to change overlay position. Click again to fix its position.")
        self.button_change_position.clicked.connect(self.overlay.change_position_state)
        overlay_layout.addWidget(self.button_change_position, 5, 0, 1, 2)

    def save_current_bo(self):
        """Save the current build order"""
        bo_name = self.bo_list.currentItem().text()
        bo_text = self.bo_edit.toPlainText()
        settings.build_orders[bo_name] = bo_text
        self.update_overlay()

    def bo_selected(self, item: QtWidgets.QListWidgetItem):
        """Actions related to selected BO

        Parameters
        ----------
        item    holds the BO content
        """

        try:  # try disconnecting signals (throws an error when nothing connected)
            self.bo_edit.disconnect()
        except TypeError:
            pass
        try:
            self.naming_widget.disconnect()
        except TypeError:
            pass

        # change values
        self.naming_widget.setText(item.text())
        self.bo_edit.setText(settings.build_orders.get(item.text(), ""))
        self.update_overlay()

        # reconnect signals
        self.bo_edit.textChanged.connect(self.save_current_bo)
        self.naming_widget.textChanged.connect(self.name_changed)

    def name_changed(self, text: str):
        """Change the name of the BO

        Parameters
        ----------
        text    new name for the BO
        """
        self.bo_list.currentItem().setText(text)

        # remove the old build order
        rows = self.bo_list.count()
        bo_names = {self.bo_list.item(i).text() for i in range(rows)}
        for name in settings.build_orders:
            if name not in bo_names:
                del settings.build_orders[name]
                break

        # add the new build order
        self.save_current_bo()

    def add_build_order(self):
        """Add a new build order"""
        self.bo_list.addItem(f"Build order {self.bo_list.count() + 1}")
        self.bo_list.setCurrentRow(self.bo_list.count() - 1)
        self.save_current_bo()

    def remove_build_order(self):
        """Remove the currently selected build order"""
        if self.bo_list.count() == 1:
            return
        del settings.build_orders[self.bo_list.currentItem().text()]
        self.bo_list.takeItem(self.bo_list.currentRow())

    def font_size_changed(self, font_index: int):
        """Adapt the overlay for a font size change

        Parameters
        ----------
        font_index
        """
        settings.bo_font_size = font_index + 1
        self.overlay.update_settings()
        self.update_overlay()

    def show_hotkey_changed(self, new_hotkey: str):
        """Update the show/hide hotkey when changed

        Parameters
        ----------
        new_hotkey    string containing the new hotkey sequence
        """
        settings.bo_overlay_hotkey_show = hotkey_changed(
            new_hotkey=new_hotkey, hotkey_str=settings.bo_overlay_hotkey_show,
            hotkey_edit=self.key_show_hide, hotkey_signal=self.show_hide_overlay)

    def cycle_hotkey_changed(self, new_hotkey: str):
        """Update the cycle BO hotkey when changed

        Parameters
        ----------
        new_hotkey    string containing the new hotkey sequence
        """
        settings.bo_overlay_hotkey_cycle = hotkey_changed(
            new_hotkey=new_hotkey, hotkey_str=settings.bo_overlay_hotkey_cycle,
            hotkey_edit=self.key_cycle, hotkey_signal=self.cycle_build_order)

    def previous_step_hotkey_changed(self, new_hotkey: str):
        """Update the previous step hotkey when changed

        Parameters
        ----------
        new_hotkey    string containing the new hotkey sequence
        """
        settings.bo_overlay_hotkey_previous_step = hotkey_changed(
            new_hotkey=new_hotkey, hotkey_str=settings.bo_overlay_hotkey_previous_step,
            hotkey_edit=self.key_previous_step, hotkey_signal=self.previous_step_build_order)

    def next_step_hotkey_changed(self, new_hotkey: str):
        """Update the next step hotkey when changed

        Parameters
        ----------
        new_hotkey    string containing the new hotkey sequence
        """
        settings.bo_overlay_hotkey_next_step = hotkey_changed(
            new_hotkey=new_hotkey, hotkey_str=settings.bo_overlay_hotkey_next_step,
            hotkey_edit=self.key_next_step, hotkey_signal=self.next_step_build_order)

    def limit_build_order_step(self):
        """Limit the step of the build order"""
        if self.build_order_step_count < 1:  # invalid build order for step selection
            self.build_order_step = -1
            self.build_order_step_count = -1
        elif self.build_order_step < 0:
            self.build_order_step = 0
        elif self.build_order_step >= self.build_order_step_count:
            self.build_order_step = self.build_order_step_count - 1

    def select_previous_build_order_step(self):
        """Select the previous build order step"""
        init_build_order_step = self.build_order_step
        self.build_order_step -= 1
        self.limit_build_order_step()
        if (init_build_order_step != self.build_order_step) and (self.build_order_step >= 0):
            self.update_overlay()

    def select_next_build_order_step(self):
        """Select the next build order"""
        init_build_order_step = self.build_order_step
        self.build_order_step += 1
        self.limit_build_order_step()
        if (init_build_order_step != self.build_order_step) and (self.build_order_step >= 0):
            self.update_overlay()

    def cycle_overlay(self):
        """ Cycles through build orders and sends data to the overlay"""
        self.bo_list.setCurrentRow((self.bo_list.currentRow() + 1) % self.bo_list.count())
        self.build_order_step = -1
        self.update_overlay()

    def update_overlay(self):
        """Send new data to the overlay"""
        if self.bo_list.count():
            # get data from the selected build order
            bo_name = self.bo_list.currentItem().text()
            bo_text = self.bo_edit.toPlainText()
            # check if valid JSON format for CraftySalamander overlay
            if check_valid_aoe4_build_order_from_string(bo_text):
                data = json.loads(bo_text)
                self.build_order_step_count = len(data['build_order'])
                self.limit_build_order_step()
                self.overlay.update_build_order_display(
                    title=f'{bo_name} - {self.build_order_step + 1}/{self.build_order_step_count}',
                    data=data['build_order'][self.build_order_step])
            else:
                self.build_order_step = -1
                self.build_order_step_count = -1
                self.overlay.update_build_order_display(title=bo_name, data={'txt': bo_text})
