from PyQt5.QtWidgets import QApplication
import time
from database import Settings


def get_screen_bbox(self):
    screen_id = Settings().get_value(Settings.SCREEN)
    if screen_id is None:
        screen_id = 0
    screen_res = QApplication.desktop().screenGeometry(int(screen_id))
    return screen_res.left(), screen_res.top(), screen_res.right(), screen_res.bottom()


def current_milli_time():
    return int(round(time.time() * 1000))
