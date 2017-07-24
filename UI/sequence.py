from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5 import QtCore, QtGui
from UI.ui_sequence import Ui_MainWindow
from database import Data
import functions
import os


class SequenceUI(object):
    def __init__(self):
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)

        self.sequence_id = None

        # Register actions
        self.ui.list_images.clicked.connect(self.show_image)
        self.ui.b_noIndicator.clicked.connect(self.set_no_indicator)
        self.ui.b_leftIndicator.clicked.connect(self.set_left_indicator)
        self.ui.b_rightIndicator.clicked.connect(self.set_right_indicator)
        self.ui.b_delete.clicked.connect(self.delete_selection)


    def show(self):
        self.fill_image_list()
        self.window.show()

    def hide(self):
        self.window.close()

    def set_sequence_id(self, sid):
        self.sequence_id = sid

    def _get_selected_image(self):
        selection_list = self.ui.list_images.selectedIndexes()
        if len(selection_list) > 0:
            return selection_list[0].data(QtCore.Qt.UserRole)
        else:
            return None

    def fill_image_list(self):
        """
        Fill list_image with data.
        """
        data = Data()
        list_images = self.ui.list_images

        model = QStandardItemModel(list_images)
        images = data.get_image_list(self.sequence_id)
        if len(images) > 0:
            for image in images:
                item = QStandardItem("%s - %s" % (image[1], functions.get_indicator(image[5])))
                item.setEditable(False)
                item.setData(str(image[0]), QtCore.Qt.UserRole)
                model.appendRow(item)
        list_images.setModel(model)

    def show_image(self):
        img_id = self._get_selected_image()
        img_data = Data().get_image_data(img_id)
        pixmap = QtGui.QPixmap(os.path.join("captured", img_data[1]))
        self.ui.captured_image.setPixmap(pixmap)

    def _update_maneuver(self, maneuver):
        img_id = self._get_selected_image()
        img_data = Data().get_image_data(img_id)
        if img_data is not None:
            Data().set_image_maneuver(img_data[1], maneuver)
        self.fill_image_list()

    def set_no_indicator(self):
        self._update_maneuver(0)

    def set_left_indicator(self):
        self._update_maneuver(1)

    def set_right_indicator(self):
        self._update_maneuver(2)

    def delete_selection(self):
        img_id = self._get_selected_image()
        if not img_id:
            return

        filename = Data().get_image_data(img_id)[1]
        Data().delete_image(filename)
        if os.path.exists(os.path.join("captured", filename)):
            os.remove(os.path.join("captured", filename))
        self.fill_image_list()
