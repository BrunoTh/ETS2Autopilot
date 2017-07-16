from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtGui
from PIL import ImageGrab
import numpy as np
import cv2
import pygame
from UI.ui_settings import Ui_MainWindow
from database import Settings

import sys


class SettingsUI(object):
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

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

        self.ui.cb_screen.currentIndexChanged.connect(self.select_screen)

        self.ui.b_refreshDevices.clicked.connect(self.fill_device_list)

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
        vjoy = settings.get_value(settings.VJOY_DEVICE)
        autopilot = settings.get_value(settings.AUTOPILOT)
        left_indicator = settings.get_value(settings.LEFT_INDICATOR)
        right_indicator = settings.get_value(settings.RIGHT_INDICATOR)
        steering_axis = settings.get_value(settings.STEERING_AXIS)
        throttle_axis = settings.get_value(settings.THROTTLE_AXIS)

        self.fill_screen_list()
        self.fill_device_list()
        self.select_screen()

        # Set scrollbar values
        if image_front_border_right is not None:
            self.ui.slider_right.setValue(int(image_front_border_right))
        else:
            self.ui.slider_right.setValue(self.ui.slider_right.maximum())

        if image_front_border_left is not None:
            self.ui.slider_left.setValue(int(image_front_border_left))
        else:
            self.ui.slider_left.setValue(self.ui.slider_left.minimum())

        if image_front_border_bottom is not None:
            self.ui.slider_bottom.setValue(int(image_front_border_bottom))
        else:
            self.ui.slider_bottom.setValue(self.ui.slider_bottom.maximum())

        if image_front_border_top is not None:
            self.ui.slider_top.setValue(int(image_front_border_top))
        else:
            self.ui.slider_top.setValue(self.ui.slider_top.minimum())

        # Display key bindings
        if vjoy:
            self.ui.e_vjoy.setText(str(vjoy))
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

        self.fill_screen_cap()

    def fill_device_list(self):
        if pygame.joystick.get_init():
            pygame.joystick.quit()
        pygame.joystick.init()
        self.ui.cb_devices.clear()

        joystick_count = pygame.joystick.get_count()
        if joystick_count > 0:
            for i in range(joystick_count):
                self.ui.cb_devices.addItem(pygame.joystick.Joystick(i).get_name())
            device = Settings().get_value(Settings.CONTROLLER)
            if device is not None and int(device) < joystick_count:
                self.ui.cb_devices.setCurrentIndex(int(device))

    def fill_screen_list(self):
        # TODO: SCREEN settings value gets overwritten
        self.ui.cb_screen.clear()
        for i in range(len(QApplication.screens())):
            self.ui.cb_screen.addItem("Screen %d" % (i+1))
        screen = Settings().get_value(Settings.SCREEN)

        if screen is not None:
            self.ui.cb_screen.setCurrentIndex(int(screen))

    def select_screen(self):
        screen_id = self.ui.cb_screen.currentIndex()
        screen_res = QApplication.desktop().screenGeometry(screen_id)

        Settings().set_value(Settings.SCREEN, screen_id)

        self.ui.slider_left.setMaximum(screen_res.width())
        self.ui.slider_right.setMaximum(screen_res.width())
        self.ui.slider_top.setMaximum(screen_res.height())
        self.ui.slider_bottom.setMaximum(screen_res.height())

    def get_screen_bbox(self):
        screen_id = Settings().get_value(Settings.SCREEN)
        if screen_id is None:
            screen_id = 0
        screen_res = QApplication.desktop().screenGeometry(int(screen_id))
        return screen_res.left(), screen_res.top(), screen_res.right(), screen_res.bottom()

    def save_settings(self):
        settings = Settings()
        settings.set_value(settings.IMAGE_FRONT_BORDER_LEFT, self.ui.slider_left.value())
        settings.set_value(settings.IMAGE_FRONT_BORDER_RIGHT, self.ui.slider_right.value())
        settings.set_value(settings.IMAGE_FRONT_BORDER_TOP, self.ui.slider_top.value())
        settings.set_value(settings.IMAGE_FRONT_BORDER_BOTTOM, self.ui.slider_bottom.value())

        settings.set_value(settings.SCREEN, self.ui.cb_screen.currentIndex())
        settings.set_value(settings.CONTROLLER, self.ui.cb_devices.currentIndex())

        settings.set_value(settings.VJOY_DEVICE, self.ui.e_vjoy.text())
        settings.set_value(settings.AUTOPILOT, self.ui.e_autopilot.text())
        settings.set_value(settings.LEFT_INDICATOR, self.ui.e_leftIndicator.text())
        settings.set_value(settings.RIGHT_INDICATOR, self.ui.e_rightIndicator.text())
        settings.set_value(settings.STEERING_AXIS, self.ui.e_steering.text())
        settings.set_value(settings.THROTTLE_AXIS, self.ui.e_throttle.text())

        self.hide()

    def fill_screen_cap(self):
        # TODO: Screen 2 shows black image
        slider_left = self.ui.slider_left.value()
        slider_right = self.ui.slider_right.value()
        slider_top = self.ui.slider_top.value()
        slider_bottom = self.ui.slider_bottom.value()

        frame_raw = ImageGrab.grab(bbox=self.get_screen_bbox())
        frame = np.uint8(frame_raw)
        frame = cv2.rectangle(frame, (slider_left, slider_top), (slider_right, slider_bottom), (255, 0, 0), 4)
        qimg = QtGui.QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap(qimg)
        pixmap = pixmap.scaledToHeight(self.ui.screen_cap.height())
        self.ui.screen_cap.setPixmap(pixmap)

    def modify_border(self):
        slider_left = self.ui.slider_left.value()
        slider_right = self.ui.slider_right.value()
        slider_top = self.ui.slider_top.value()
        slider_bottom = self.ui.slider_bottom.value()

        if slider_left > slider_right:
            self.ui.slider_left.setValue(slider_right)
        if slider_top > slider_bottom:
            self.ui.slider_top.setValue(slider_bottom)

        self.fill_screen_cap()
