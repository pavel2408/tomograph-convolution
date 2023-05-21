from PyQt5.QtCore import pyqtSlot

from uis.please_wait import Ui_Form
from PyQt5 import QtCore, QtGui, QtWidgets


class PleaseWaitWin(QtWidgets.QWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.setupUi(self)

    @pyqtSlot(int)
    def switch_task_count(self, task_num):
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(task_num)

    @pyqtSlot(str, int)
    def update_progress(self, status_string, part):
        self.label.setText(status_string)
        self.progressBar.setValue(part)
