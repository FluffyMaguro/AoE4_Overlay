import subprocess
import sys
import webbrowser
from functools import partial

from PyQt5 import QtCore, QtGui, QtWidgets

from overlay.helper_func import file_path, pyqt_wait
from overlay.settings import CONFIG_FOLDER, settings
from overlay.tab_widget import TabWidget

VERSION = "1.0.0"


class MainApp(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(f"AoE IV: Overlay ({VERSION})")
        self.setWindowIcon(QtGui.QIcon(file_path('src/img/icon.ico')))
        self.setGeometry(0, 0, 800, 500)
        self.move(QtWidgets.QDesktopWidget().availableGeometry().center() -
                  QtCore.QPoint(int(self.width() / 2), self.height()))

        # Create central widget
        self.setCentralWidget(TabWidget())

        ### Create menu bar items
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        link_menu = menubar.addMenu('Links')

        # Html
        icon = self.style().standardIcon(
            getattr(QtWidgets.QStyle, 'SP_DirLinkIcon'))
        htmlAction = QtWidgets.QAction(icon, 'Html files', self)
        htmlAction.setStatusTip('Open the folder with HTML layout files')
        htmlAction.triggered.connect(lambda: subprocess.run(
            ['explorer', file_path("src/html")]))
        file_menu.addAction(htmlAction)

        # Config
        icon = self.style().standardIcon(
            getattr(QtWidgets.QStyle, 'SP_DirLinkIcon'))
        htmlAction = QtWidgets.QAction(icon, 'Config file', self)
        htmlAction.setStatusTip('Open the folder with config files')
        htmlAction.triggered.connect(
            lambda: subprocess.run(['explorer', CONFIG_FOLDER]))
        file_menu.addAction(htmlAction)

        # Exit
        icon = self.style().standardIcon(
            getattr(QtWidgets.QStyle, 'SP_DialogCloseButton'))
        exitAction = QtWidgets.QAction(icon, 'Exit', self)
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtWidgets.qApp.quit)
        file_menu.addAction(exitAction)

        # Github
        icon = QtGui.QIcon(file_path("src/img/github.png"))
        githubAction = QtWidgets.QAction(icon, 'Overlay on Github', self)
        githubAction.triggered.connect(
            partial(webbrowser.open,
                    "https://github.com/FluffyMaguro/AoE4_Overlay"))
        link_menu.addAction(githubAction)

        # Discord
        icon = QtGui.QIcon(file_path("src/img/discord.png"))
        mdiscordAction = QtWidgets.QAction(icon, 'My discord', self)
        mdiscordAction.triggered.connect(
            partial(webbrowser.open, "https://discord.gg/FtGdhqD"))
        link_menu.addAction(mdiscordAction)

        # Maguro
        icon = QtGui.QIcon(file_path("src/img/maguro.jpg"))
        maguroAction = QtWidgets.QAction(icon, 'Maguro.one', self)
        maguroAction.triggered.connect(
            partial(webbrowser.open, "https://www.maguro.one/"))
        link_menu.addAction(maguroAction)

        # AoEIV.net
        icon = QtGui.QIcon(file_path("src/img/aoeivnet.png"))
        maguroAction = QtWidgets.QAction(icon, 'AoEIV.net', self)
        maguroAction.triggered.connect(
            partial(webbrowser.open, "https://aoeiv.net/"))
        link_menu.addAction(maguroAction)

        self.statusBar()
        self.show()
        self.centralWidget().check_for_new_version(VERSION)

    def finish(self):
        """ Give it some time to stop everything correctly"""
        settings.save()
        self.centralWidget().main_tab.stop_checking_api()
        pyqt_wait(1000)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Main = MainApp()
    exit_event = app.exec_()
    Main.finish()
    sys.exit(exit_event)
