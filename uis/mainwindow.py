# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(988, 849)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.first_view_description = QtWidgets.QLabel(self.centralwidget)
        self.first_view_description.setMinimumSize(QtCore.QSize(400, 20))
        self.first_view_description.setMaximumSize(QtCore.QSize(16777215, 20))
        self.first_view_description.setAlignment(QtCore.Qt.AlignCenter)
        self.first_view_description.setObjectName("first_view_description")
        self.verticalLayout_2.addWidget(self.first_view_description)
        self.first_view = SliceLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.first_view.sizePolicy().hasHeightForWidth())
        self.first_view.setSizePolicy(sizePolicy)
        self.first_view.setMinimumSize(QtCore.QSize(400, 300))
        self.first_view.setText("")
        self.first_view.setScaledContents(True)
        self.first_view.setObjectName("first_view")
        self.verticalLayout_2.addWidget(self.first_view)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.third_view_description = QtWidgets.QLabel(self.centralwidget)
        self.third_view_description.setMinimumSize(QtCore.QSize(400, 20))
        self.third_view_description.setMaximumSize(QtCore.QSize(16777215, 20))
        self.third_view_description.setAlignment(QtCore.Qt.AlignCenter)
        self.third_view_description.setObjectName("third_view_description")
        self.verticalLayout_3.addWidget(self.third_view_description)
        self.third_view = SliceLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.third_view.sizePolicy().hasHeightForWidth())
        self.third_view.setSizePolicy(sizePolicy)
        self.third_view.setMinimumSize(QtCore.QSize(400, 300))
        self.third_view.setText("")
        self.third_view.setScaledContents(True)
        self.third_view.setObjectName("third_view")
        self.verticalLayout_3.addWidget(self.third_view)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.second_view_description = QtWidgets.QLabel(self.centralwidget)
        self.second_view_description.setMinimumSize(QtCore.QSize(400, 20))
        self.second_view_description.setMaximumSize(QtCore.QSize(16777215, 20))
        self.second_view_description.setAlignment(QtCore.Qt.AlignCenter)
        self.second_view_description.setObjectName("second_view_description")
        self.verticalLayout_4.addWidget(self.second_view_description)
        self.second_view = SliceLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.second_view.sizePolicy().hasHeightForWidth())
        self.second_view.setSizePolicy(sizePolicy)
        self.second_view.setMinimumSize(QtCore.QSize(400, 300))
        self.second_view.setText("")
        self.second_view.setScaledContents(True)
        self.second_view.setObjectName("second_view")
        self.verticalLayout_4.addWidget(self.second_view)
        self.horizontalLayout_2.addLayout(self.verticalLayout_4)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 988, 21))
        self.menubar.setObjectName("menubar")
        self.main_menu = QtWidgets.QMenu(self.menubar)
        self.main_menu.setObjectName("main_menu")
        self.view_menu = QtWidgets.QMenu(self.menubar)
        self.view_menu.setObjectName("view_menu")
        MainWindow.setMenuBar(self.menubar)
        self.action_open_dicom = QtWidgets.QAction(MainWindow)
        self.action_open_dicom.setObjectName("action_open_dicom")
        self.action_sync_with_first = QtWidgets.QAction(MainWindow)
        self.action_sync_with_first.setObjectName("action_sync_with_first")
        self.action_sync_with_second = QtWidgets.QAction(MainWindow)
        self.action_sync_with_second.setObjectName("action_sync_with_second")
        self.action_sync_with_third = QtWidgets.QAction(MainWindow)
        self.action_sync_with_third.setObjectName("action_sync_with_third")
        self.action_reset_slices = QtWidgets.QAction(MainWindow)
        self.action_reset_slices.setObjectName("action_reset_slices")
        self.main_menu.addAction(self.action_open_dicom)
        self.view_menu.addAction(self.action_reset_slices)
        self.view_menu.addAction(self.action_sync_with_first)
        self.view_menu.addAction(self.action_sync_with_second)
        self.view_menu.addAction(self.action_sync_with_third)
        self.menubar.addAction(self.main_menu.menuAction())
        self.menubar.addAction(self.view_menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.first_view_description.setText(_translate("MainWindow", "Фронтальный срез"))
        self.third_view_description.setText(_translate("MainWindow", "Корональный срез"))
        self.second_view_description.setText(_translate("MainWindow", "Сагиттальный срез"))
        self.main_menu.setTitle(_translate("MainWindow", "Меню"))
        self.view_menu.setTitle(_translate("MainWindow", "Вид"))
        self.action_open_dicom.setText(_translate("MainWindow", "Открыть папку DICOM-файлами"))
        self.action_sync_with_first.setText(_translate("MainWindow", "Синхронизировать с первым срезом"))
        self.action_sync_with_second.setText(_translate("MainWindow", "Синхронизировать со вторым срезом"))
        self.action_sync_with_third.setText(_translate("MainWindow", "Синхронизировать с третьим срезом"))
        self.action_reset_slices.setText(_translate("MainWindow", "Сбросить срезы"))
from uis.custom_widgets import SliceLabel