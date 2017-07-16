# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sequence.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(462, 431)
        self.list_images = QtWidgets.QListView(MainWindow)
        self.list_images.setGeometry(QtCore.QRect(10, 10, 180, 371))
        self.list_images.setObjectName("list_images")
        self.b_delete = QtWidgets.QPushButton(MainWindow)
        self.b_delete.setGeometry(QtCore.QRect(10, 390, 180, 30))
        self.b_delete.setObjectName("b_delete")
        self.captured_image = QtWidgets.QLabel(MainWindow)
        self.captured_image.setGeometry(QtCore.QRect(200, 10, 250, 100))
        self.captured_image.setFrameShape(QtWidgets.QFrame.Box)
        self.captured_image.setText("")
        self.captured_image.setObjectName("captured_image")
        self.b_save = QtWidgets.QPushButton(MainWindow)
        self.b_save.setGeometry(QtCore.QRect(360, 390, 95, 30))
        self.b_save.setObjectName("b_save")
        self.groupBox = QtWidgets.QGroupBox(MainWindow)
        self.groupBox.setGeometry(QtCore.QRect(200, 180, 141, 151))
        self.groupBox.setObjectName("groupBox")
        self.b_noIndicator = QtWidgets.QPushButton(self.groupBox)
        self.b_noIndicator.setGeometry(QtCore.QRect(10, 30, 121, 30))
        self.b_noIndicator.setObjectName("b_noIndicator")
        self.b_leftIndicator = QtWidgets.QPushButton(self.groupBox)
        self.b_leftIndicator.setGeometry(QtCore.QRect(10, 70, 121, 30))
        self.b_leftIndicator.setObjectName("b_leftIndicator")
        self.b_rightIndicator = QtWidgets.QPushButton(self.groupBox)
        self.b_rightIndicator.setGeometry(QtCore.QRect(10, 110, 121, 30))
        self.b_rightIndicator.setObjectName("b_rightIndicator")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Sequence"))
        self.b_delete.setText(_translate("MainWindow", "Delete entry and image"))
        self.b_save.setText(_translate("MainWindow", "Save"))
        self.groupBox.setTitle(_translate("MainWindow", "Set Indicator"))
        self.b_noIndicator.setText(_translate("MainWindow", "No Indicator"))
        self.b_leftIndicator.setText(_translate("MainWindow", "Left Indicator"))
        self.b_rightIndicator.setText(_translate("MainWindow", "Right Indicator"))
