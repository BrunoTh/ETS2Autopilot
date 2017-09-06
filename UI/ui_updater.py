# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer\updater.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 131)
        MainWindow.setLocale(QtCore.QLocale(QtCore.QLocale.German, QtCore.QLocale.Germany))
        self.pb_progress = QtWidgets.QProgressBar(MainWindow)
        self.pb_progress.setGeometry(QtCore.QRect(10, 60, 381, 23))
        self.pb_progress.setProperty("value", 0)
        self.pb_progress.setAlignment(QtCore.Qt.AlignCenter)
        self.pb_progress.setOrientation(QtCore.Qt.Horizontal)
        self.pb_progress.setObjectName("pb_progress")
        self.b_run = QtWidgets.QPushButton(MainWindow)
        self.b_run.setEnabled(False)
        self.b_run.setGeometry(QtCore.QRect(210, 90, 181, 30))
        self.b_run.setCheckable(False)
        self.b_run.setChecked(False)
        self.b_run.setObjectName("b_run")
        self.label = QtWidgets.QLabel(MainWindow)
        self.label.setGeometry(QtCore.QRect(10, 10, 81, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(MainWindow)
        self.label_2.setGeometry(QtCore.QRect(10, 30, 81, 16))
        self.label_2.setObjectName("label_2")
        self.b_check = QtWidgets.QPushButton(MainWindow)
        self.b_check.setGeometry(QtCore.QRect(10, 90, 181, 30))
        self.b_check.setObjectName("b_check")
        self.l_newVersion = QtWidgets.QLabel(MainWindow)
        self.l_newVersion.setGeometry(QtCore.QRect(100, 30, 81, 16))
        self.l_newVersion.setText("")
        self.l_newVersion.setObjectName("l_newVersion")
        self.l_currentVersion = QtWidgets.QLabel(MainWindow)
        self.l_currentVersion.setGeometry(QtCore.QRect(100, 10, 81, 16))
        self.l_currentVersion.setText("")
        self.l_currentVersion.setObjectName("l_currentVersion")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Updater"))
        self.pb_progress.setFormat(_translate("MainWindow", "%p%"))
        self.b_run.setText(_translate("MainWindow", "Run Update"))
        self.label.setText(_translate("MainWindow", "Current version:"))
        self.label_2.setText(_translate("MainWindow", "New version:"))
        self.b_check.setText(_translate("MainWindow", "Check for Update"))

