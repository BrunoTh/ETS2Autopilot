from PyQt5.QtWidgets import QMainWindow
from UI.ui_sequence import Ui_MainWindow
from database import Data
import sys


class SequenceUI(object):
    def __init__(self):
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)

        self.sequence_id = None

        # Register actions

    def show(self):
        self.window.show()

    def hide(self):
        self.window.close()

    def set_sequence_id(self, sid):
        self.sequence_id = sid
