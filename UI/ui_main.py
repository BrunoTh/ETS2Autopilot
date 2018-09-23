# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer\main.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(542, 255)
        MainWindow.setWindowOpacity(1.0)
        MainWindow.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        MainWindow.setAnimated(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.image_front = QtWidgets.QLabel(self.centralwidget)
        self.image_front.setGeometry(QtCore.QRect(170, 10, 360, 200))
        self.image_front.setMinimumSize(QtCore.QSize(360, 200))
        self.image_front.setMouseTracking(False)
        self.image_front.setFrameShape(QtWidgets.QFrame.Box)
        self.image_front.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.image_front.setText("")
        self.image_front.setObjectName("image_front")
        self.b_autopilot = QtWidgets.QPushButton(self.centralwidget)
        self.b_autopilot.setGeometry(QtCore.QRect(10, 50, 151, 30))
        self.b_autopilot.setObjectName("b_autopilot")
        self.b_ets2_vjoy = QtWidgets.QPushButton(self.centralwidget)
        self.b_ets2_vjoy.setGeometry(QtCore.QRect(10, 10, 151, 31))
        self.b_ets2_vjoy.setObjectName("b_ets2_vjoy")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 542, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuInfo = QtWidgets.QMenu(self.menubar)
        self.menuInfo.setObjectName("menuInfo")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setMinimumSize(QtCore.QSize(0, 20))
        self.statusbar.setBaseSize(QtCore.QSize(0, 20))
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionSettings = QtWidgets.QAction(MainWindow)
        self.actionSettings.setCheckable(False)
        self.actionSettings.setChecked(False)
        self.actionSettings.setObjectName("actionSettings")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionUpdater = QtWidgets.QAction(MainWindow)
        self.actionUpdater.setObjectName("actionUpdater")
        self.menuFile.addAction(self.actionSettings)
        self.menuFile.addAction(self.actionExit)
        self.menuInfo.addAction(self.actionUpdater)
        self.menuInfo.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuInfo.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ETS2 Autopilot"))
        self.b_autopilot.setText(_translate("MainWindow", "Start Autopilot"))
        self.b_ets2_vjoy.setText(_translate("MainWindow", "Start Joystick detection"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuInfo.setTitle(_translate("MainWindow", "Info"))
        self.actionSettings.setText(_translate("MainWindow", "Settings"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionUpdater.setText(_translate("MainWindow", "Updater"))

