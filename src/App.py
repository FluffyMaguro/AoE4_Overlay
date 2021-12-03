import subprocess
import sys
import webbrowser
from functools import partial

from PyQt5 import QtCore, QtGui, QtWidgets

from overlay.helper_func import file_path, get_config_folder
from overlay.main_widget import MainWidget

VERSION = "1.0.0"


class MainApp(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(f"AoE IV: Overlay ({VERSION})")
        self.setWindowIcon(QtGui.QIcon(file_path('src/img/icon.ico')))
        self.setGeometry(0, 0, 530, 150)
        self.move(QtWidgets.QDesktopWidget().availableGeometry().center() -
                  QtCore.QPoint(int(self.width() / 2), self.height()))

        # Create central widget
        self.setCentralWidget(MainWidget())

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
        htmlAction.triggered.connect(lambda: subprocess.run(
            ['explorer', get_config_folder()]))
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
        githubAction = QtWidgets.QAction(icon, 'Github page', self)
        githubAction.triggered.connect(
            partial(webbrowser.open,
                    "https://github.com/FluffyMaguro/AoE4_Overlay"))
        link_menu.addAction(githubAction)

        # Maguro
        icon = QtGui.QIcon(file_path("src/img/maguro.jpg"))
        maguroAction = QtWidgets.QAction(icon, 'Maguro.one', self)
        maguroAction.triggered.connect(
            partial(webbrowser.open, "https://www.maguro.one/"))
        link_menu.addAction(maguroAction)

        self.statusBar()
        self.show()

    def wait_ms(self, time):
        """ Pause executing for `time` in miliseconds"""
        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(time, loop.quit)
        loop.exec_()

    def stop_all(self):
        """ Give it some time to stop everything correctly"""
        self.centralWidget().stop_check()
        self.wait_ms(1000)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Main = MainApp()
    exit_event = app.exec_()
    Main.stop_all()
    sys.exit(exit_event)
