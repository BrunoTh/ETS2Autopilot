from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5 import QtCore, QtGui
from UI.ui_sequence import Ui_MainWindow
from database import Data
import os


class SequenceUI(object):
    def __init__(self):
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)

        self.sequence_id = None

        # Register actions
        self.ui.list_images.clicked.connect(self.show_image)

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
                item = QStandardItem(image[1])
                item.setEditable(False)
                item.setData(str(image[0]), QtCore.Qt.UserRole)
                model.appendRow(item)
        list_images.setModel(model)

    def show_image(self):
        img_id = self._get_selected_image()
        img_data = Data().get_image_data(img_id)
        pixmap = QtGui.QPixmap(os.path.join("captured", img_data[1]))
        self.ui.captured_image.setPixmap(pixmap)
