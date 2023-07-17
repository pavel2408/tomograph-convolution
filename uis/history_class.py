import sys
import numpy as np
from uis.history_win import Ui_Form
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMessageBox
sys.path.append("..")
from scan_history import ScanHistory
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class HistoryWin(QtWidgets.QWidget, Ui_Form):
    def __init__(self, parent):
        super().__init__(parent, QtCore.Qt.Window)
        self.setupUi(self)
        self.class_names = ['Heart', 'Spleen', 'Liver', 'Kidneys', 'Bladder', 'Tumor']
        self.is_err = False
        self.scan_history = ScanHistory()
        patient_names = self.scan_history.load_patients()
        if not patient_names:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Ошибка!")
            msg_box.setText("Отсутствуют данные о пациентах!")
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.exec()
            self.is_err = True
        else:
            for i in patient_names:
                self.comboBox.addItem(i[0])
        self.pushButton.clicked.connect(self.draw_history)

    def draw_history(self):
        patient_name = self.comboBox.currentText()
        data = self.scan_history.load_patient_data(patient_name)
        data_by_class = {i: {} for i in self.class_names}
        for i in data:
            data_by_class["Heart"][i[1]] = i[2]
            data_by_class["Spleen"][i[1]] = i[3]
            data_by_class["Liver"][i[1]] = i[4]
            data_by_class["Kidneys"][i[1]] = i[5]
            data_by_class["Bladder"][i[1]] = i[6]
            data_by_class["Tumor"][i[1]] = i[7]
        print(data_by_class)

        self.sc = MplCanvas(self, dpi=100)
        for i in data_by_class:
            self.sc.axes.plot(list(data_by_class[i].keys()), list(data_by_class[i].values()), label=i)
        self.sc.axes.legend(loc='upper right')

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(self.sc, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)

        self.matplotlib_widget.setLayout(layout)


