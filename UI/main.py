from PyQt5.QtWidgets import QMainWindow
from ui_main import Ui_MainWindow


class Main(object):
    def __init__(self):
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)

    def show(self):
        self.window.show()

    def hide(self):
        pass


