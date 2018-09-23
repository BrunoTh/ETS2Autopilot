from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5 import QtCore
from UI.ui_main import Ui_MainWindow
from UI.settings import SettingsUI
from UI.updater import UpdaterUI
from database import Settings, Data
from thread_controller import ControllerThread
from thread_autopilot_cv import AutopilotThread  # Using cv mode
import sys


class MainUI(object):
    def __init__(self):
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)

        # Register other windows
        self.settings_ui = SettingsUI()
        self.updater_ui = UpdaterUI()

        # Define thread variables
        self.thread_controller = None
        self.thread_training = None
        self.thread_autopilot = None
        self.thread_recording = None

        # Register buttons and stuff
        self.ui.actionSettings.triggered.connect(self.settings_ui.show)
        self.ui.actionExit.triggered.connect(sys.exit)
        self.ui.actionUpdater.triggered.connect(self.updater_ui.show)
        self.ui.actionAbout.triggered.connect(self.show_info)

        self.ui.b_ets2_vjoy.clicked.connect(self.clicked_ets2_vjoy)
        self.ui.b_autopilot.clicked.connect(self.clicked_autopilot)

        # Try to start controller thread
        if Settings().get_value(Settings.CONTROLLER) is not None and Settings().get_value(Settings.VJOY_DEVICE) is not None:
            self.thread_controller = ControllerThread()
            self.thread_controller.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.thread_controller is not None and self.thread_controller.is_alive():
            print(self.thread_controller.is_alive())
            self.thread_controller.stop()
        if self.thread_autopilot is not None and self.thread_autopilot.is_alive():
            self.thread_autopilot.stop()
        if self.thread_recording is not None and self.thread_recording.is_alive():
            self.thread_recording.stop()
        if self.thread_training is not None and self.thread_training.is_alive():
            self.thread_training.stop()

    def show(self):
        self.window.show()

    def hide(self):
        pass

    def show_info(self):
        """
        actionAbout:
        Show window with program info.
        """
        pass

    def clicked_ets2_vjoy(self):
        """
        Vjoy detection button was clicked.
        """
        mode = self.ui.b_ets2_vjoy.text()

        if mode == "Start Joystick detection":
            self.ui.b_ets2_vjoy.setText("Stop Joystick detection")
        else:
            self.ui.b_ets2_vjoy.setText("Start Joystick detection")

    def clicked_autopilot(self):
        """
        Autopilot button was clicked.
        """
        mode = self.ui.b_autopilot.text()

        if mode == "Start Autopilot":
            self.ui.b_autopilot.setText("Stop Autopilot")

            # Start autopilot thread
            self.thread_autopilot = AutopilotThread(self.ui.statusbar, self.thread_controller, self.ui.image_front)
            self.thread_autopilot.start()

        else:
            self.ui.b_autopilot.setText("Start Autopilot")

            # Stop autopilot thread
            self.thread_autopilot.stop()
            self.thread_autopilot = None
