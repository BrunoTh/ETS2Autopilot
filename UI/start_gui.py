import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from ui_main import Ui_MainWindow
import ui_settings
import ui_sequence

"""
Function list:
- get_sequence_list() - list
- append_sequence_changes(id, country, road_type)
- delete_sequence(id)
- show_sequence_details(id)

- show_front_image()
- show_steering_wheel()

- enter_mode()
- leave_mode()

- show_settings()
- exit()
- show_info()
"""


def show_settings():
    window_settings.show()


app = QApplication(sys.argv)
window = QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(window)

window_settings = QMainWindow()
ui_settings = ui_settings.Ui_MainWindow()
ui_settings.setupUi(window_settings)


window.show()
ui.actionSettings.triggered.connect(show_settings)
sys.exit(app.exec_())
