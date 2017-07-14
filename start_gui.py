import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from UI.main import MainUI


app = QApplication(sys.argv)
main = MainUI()
main.show()
sys.exit(app.exec_())
