import sys
from PIL import ImageQt
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QPixmap
import uis.mainwindow as mainwindow
from load_dicom import load_images_from_dicom
from functools import partial


class MainWindow(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.first_view_images: list[QPixmap] = None
        self.second_view_images: list[QPixmap] = None
        self.third_view_images: list[QPixmap] = None

        self.first_view.description_label = self.first_view_description
        self.second_view.description_label = self.second_view_description
        self.third_view.description_label = self.third_view_description

        self.first_view_pointer = 0
        self.second_view_pointer = 0
        self.third_view_pointer = 0
        self.action_open_dicom.triggered.connect(self.load_dicom)
        self.action_reset_slices.triggered.connect(self.reset_pointers)
        # self.action_sync_with_first.triggered.connect(partial(self.sync_pointers, self.first_view))
        # self.action_sync_with_second.triggered.connect(partial(self.sync_pointers, self.second_view))
        # self.action_sync_with_third.triggered.connect(partial(self.sync_pointers, self.third_view))
        self.view_menu.menuAction().setVisible(False)

    def reset_pointers(self):
        self.first_view.sync_slices(0)
        self.second_view.sync_slices(0)
        self.third_view.sync_slices(0)

    def sync_pointers(self, sync_view):
        pointer = sync_view.slice_pointer
        self.first_view.sync_slices(pointer)
        self.second_view.sync_slices(pointer)
        self.third_view.sync_slices(pointer)

    def first_view_scroll_slices(self, e):
        print(self, self.parent())

    def move_pointer(self):
        print(self.width(), self.height())
        if self.first_view_pointer < len(self.first_view_images):
            self.first_view_pointer += 1
        if self.second_view_pointer < len(self.second_view_images):
            self.second_view_pointer += 1
        if self.third_view_pointer < len(self.third_view_images):
            self.third_view_pointer += 1
        self.first_view.setPixmap(self.first_view_images[self.first_view_pointer].scaled(self.first_view.size()))
        self.second_view.setPixmap(self.second_view_images[self.second_view_pointer].scaled(self.second_view.size()))
        self.third_view.setPixmap(self.third_view_images[self.third_view_pointer].scaled(self.third_view.size()))

    def load_dicom(self):
        dicom_file_name = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку с DICOM-файлами...")
        if not dicom_file_name:
            return
        print(dicom_file_name)
        self.first_view_images, self.second_view_images, self.third_view_images = load_images_from_dicom(dicom_file_name)
        self.first_view_pointer = 0
        self.second_view_pointer = 0
        self.third_view_pointer = 0
        # print(self.second_view_images[self.second_view_pointer].size())

        self.first_view.slices = self.first_view_images
        self.second_view.slices = self.second_view_images
        self.third_view.slices = self.third_view_images

        self.first_view.slice_pointer = 0
        self.second_view.slice_pointer = 0
        self.third_view_pointer = 0

        print("hello")
        self.first_view.set_slice()
        self.second_view.set_slice()
        self.third_view.set_slice()
        self.view_menu.menuAction().setVisible(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec()

