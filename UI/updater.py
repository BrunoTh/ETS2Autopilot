from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtGui
from UI.ui_updater import Ui_MainWindow
from database import Settings


class UpdaterUI(object):
    def __init__(self):
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)

    def show(self):
        self.window.show()

    def hide(self):
        self.window.close()

    def check_for_update(self):
        pass

    def run_update(self):
        pass

    def restart_app(self):
        pass
