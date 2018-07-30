from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5 import QtCore
from UI.ui_main import Ui_MainWindow
from UI.settings import SettingsUI
from UI.sequence import SequenceUI
from UI.updater import UpdaterUI
from database import Settings, Data
from thread_controller import ControllerThread
from thread_autopilot_cv import AutopilotThread  # Using cv mode
from thread_recording import RecordingThread
from thread_training import TrainingThread
import sys


class MainUI(object):
    def __init__(self):
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)

        # Register other windows
        self.settings_ui = SettingsUI()
        self.sequence_ui = SequenceUI()
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

        self.ui.b_sequenceApply.clicked.connect(self.append_sequence_changes)
        self.ui.b_sequenceDetails.clicked.connect(self.show_sequence_details)
        self.ui.b_sequenceDelete.clicked.connect(self.delete_selected_sequence)
        self.ui.sequence_list.clicked.connect(self.fill_sequence_data_fields)

        self.ui.b_mode.clicked.connect(self.enter_mode)

        self.fill_sequence_list()

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

    def _get_selected_sequence(self):
        selection_list = self.ui.sequence_list.selectedIndexes()
        if len(selection_list) > 0:
            return selection_list[0].data(QtCore.Qt.UserRole)
        else:
            return None

    def fill_sequence_list(self):
        """
        Fill sequence_list with data.
        """
        data = Data()
        sequence_list = self.ui.sequence_list

        model = QStandardItemModel(sequence_list)
        sequences = data.get_sequence_list()
        if len(sequences) > 0:
            for sequence in sequences:
                note = ""
                if sequence[4] is not None:
                    note = " - %s" % sequence[4]
                item = QStandardItem("%s%s" % (sequence[1], note))
                item.setEditable(False)
                item.setData(str(sequence[0]), QtCore.Qt.UserRole)
                model.insertRow(0, item)
        sequence_list.setModel(model)

    def fill_sequence_data_fields(self):
        """
        Set text of e_country and choose right cb_roadtype.
        """
        sid = self._get_selected_sequence()
        if sid:
            sequence_data = Data().get_sequence_data(sid)
            if sequence_data:
                code = Data().get_country_code(sequence_data[1])
                self.ui.e_country.setText(code)
                self.ui.cb_roadtype.setCurrentIndex(sequence_data[2]+1)

    def append_sequence_changes(self):
        """
        b_sequenceApply:
        Update data of selected sequence.
        """
        sid = self._get_selected_sequence()
        code = self.ui.e_country.text()
        road_type = self.ui.cb_roadtype.currentIndex()-1
        Data().update_sequence(sid, code, road_type)

    def delete_selected_sequence(self):
        """
        b_sequenceDelete:
        Delete the selected sequence.
        """
        sid = self._get_selected_sequence()
        Data().delete_sequence(sid)
        self.fill_sequence_list()

    def show_sequence_details(self):
        """
        b_sequenceDetails:
        Show window with all images of the selected sequence.
        """
        sid = self._get_selected_sequence()
        if sid:
            self.sequence_ui.set_sequence_id(sid)
            self.sequence_ui.show()

    def enter_mode(self):
        """
        b_mode:
        Starts the autopilot, recording or training.
        """
        rb_autopilot = self.ui.mode_autopilot.isChecked()
        rb_recording = self.ui.mode_recording.isChecked()
        rb_training = self.ui.mode_training.isChecked()

        # Start the controller thread
        if self.thread_controller is not None:
            self.thread_controller.stop()
        self.thread_controller = None
        self.thread_controller = ControllerThread()
        self.thread_controller.start()

        # Start mode specific thread
        if rb_autopilot:
            self.thread_autopilot = AutopilotThread(self.ui.statusbar, self.thread_controller, self.ui.steering_wheel, self.ui.image_front)
            self.thread_autopilot.start()
        elif rb_recording:
            self.thread_recording = RecordingThread(self.ui.statusbar, self.ui.image_front, self.fill_sequence_list)
            self.thread_recording.start()
        elif rb_training:
            self.thread_training = TrainingThread(self.ui.statusbar)
            self.thread_training.start()

        # Deactivate radio boxes while on mode is active
        self.ui.mode_autopilot.setEnabled(False)
        self.ui.mode_training.setEnabled(False)
        self.ui.mode_recording.setEnabled(False)

        self.ui.b_mode.clicked.disconnect()
        self.ui.b_mode.clicked.connect(self.leave_mode)
        self.ui.b_mode.setText("Stop")

    def leave_mode(self):
        """
        b_mode:
        Stops the autopilot, recording or training.
        """
        rb_autopilot = self.ui.mode_autopilot.isChecked()
        rb_recording = self.ui.mode_recording.isChecked()
        rb_training = self.ui.mode_training.isChecked()

        # Stop mode specific thread
        if rb_autopilot:
            self.thread_autopilot.stop()
            self.thread_autopilot = None
        elif rb_recording:
            self.thread_recording.stop()
            self.thread_recording = None
        elif rb_training:
            self.thread_training.stop()
            self.thread_training = None

        # Show recorded corrections
        self.fill_sequence_list()
            
        self.ui.mode_autopilot.setEnabled(True)
        self.ui.mode_training.setEnabled(True)
        self.ui.mode_recording.setEnabled(True)

        self.ui.b_mode.clicked.disconnect()
        self.ui.b_mode.clicked.connect(self.enter_mode)
        self.ui.b_mode.setText("Start")
