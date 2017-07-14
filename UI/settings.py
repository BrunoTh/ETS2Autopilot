from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtGui
from PIL import ImageGrab
import numpy as np
import cv2
from UI.ui_settings import Ui_MainWindow
from database import Settings

import sys


class SettingsUI(object):
    def __init__(self):
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)

        # Register actions
        self.ui.b_refreshImage.clicked.connect(self.fill_screen_cap)
        self.ui.b_save.clicked.connect(self.save_settings)
        self.ui.b_refreshDevices.clicked.connect(self.fill_device_list)

        self.ui.slider_left.valueChanged.connect(self.modify_border)
        self.ui.slider_right.valueChanged.connect(self.modify_border)
        self.ui.slider_top.valueChanged.connect(self.modify_border)
        self.ui.slider_bottom.valueChanged.connect(self.modify_border)

    def show(self):
        self._load_settings()
        self.window.show()

    def hide(self):
        self.window.close()

    def _load_settings(self):
        settings = Settings()

        # Screen data
        image_front_border_left = settings.get_value(settings.IMAGE_FRONT_BORDER_LEFT)
        image_front_border_right = settings.get_value(settings.IMAGE_FRONT_BORDER_RIGHT)
        image_front_border_top = settings.get_value(settings.IMAGE_FRONT_BORDER_TOP)
        image_front_border_bottom = settings.get_value(settings.IMAGE_FRONT_BORDER_BOTTOM)

        # Controller binding
        autopilot = settings.get_value(settings.AUTOPILOT)
        left_indicator = settings.get_value(settings.LEFT_INDICATOR)
        right_indicator = settings.get_value(settings.RIGHT_INDICATOR)
        steering_axis = settings.get_value(settings.STEERING_AXIS)
        throttle_axis = settings.get_value(settings.THROTTLE_AXIS)

        if autopilot:
            self.ui.e_autopilot.setText(str(autopilot))
        if left_indicator:
            self.ui.e_leftIndicator.setText(str(left_indicator))
        if right_indicator:
            self.ui.e_rightIndicator.setText(str(right_indicator))
        if steering_axis:
            self.ui.e_steering.setText(str(steering_axis))
        if throttle_axis:
            self.ui.e_throttle.setText(str(throttle_axis))

    def save_settings(self):
        pass

    def fill_screen_cap(self):
        frame_raw = ImageGrab.grab(bbox=(0, 0, 1920, 1080))
        frame = cv2.cvtColor(np.array(frame_raw), cv2.COLOR_RGB2BGR)
        qimg = QtGui.QImage(frame, frame.shape[1], frame.shape[0], frame.shape[1]*3, QtGui.Qimage.Format_RGB888)
        pixmap = QtGui.QPixmap(qimg)
        self.ui.screen_cap.setPixmap(pixmap)

    def fill_screen_list(self):
        pass

    def fill_device_list(self):
        pass

    def modify_border(self):
        slider_left = self.ui.slider_left.value()
        slider_right = self.ui.slider_right.value()
        slider_top = self.ui.slider_top.value()
        slider_bottom = self.ui.slider_bottom.value()

        if slider_left > slider_right:
            self.ui.slider_left.setValue(slider_right)
        if slider_top > slider_bottom:
            self.ui.slider_top.setValue(slider_bottom)
