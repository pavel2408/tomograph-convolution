from uis.dicom_win import Ui_Form
from PyQt5 import QtCore, QtGui, QtWidgets


class DicomWin(QtWidgets.QWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.setupUi(self)
