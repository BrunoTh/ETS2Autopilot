from PyQt5.QtWidgets import QApplication
from PyQt5 import QtGui
import time
from database import Settings


def get_screen_bbox():
    screen_id = Settings().get_value(Settings.SCREEN)
    if screen_id is None:
        screen_id = 0
    screen_res = QApplication.desktop().screenGeometry(int(screen_id))
    return screen_res.left(), screen_res.top(), screen_res.right(), screen_res.bottom()


def current_milli_time():
    return int(round(time.time() * 1000))


def set_image(cv_image, ui_element):
    qimg = QtGui.QImage(cv_image, cv_image.shape[1], cv_image.shape[0], cv_image.strides[0], QtGui.QImage.Format_RGB888)
    pixmap = QtGui.QPixmap(qimg)
    pixmap = pixmap.scaledToHeight(ui_element.height())
    ui_element.setPixmap(pixmap)
