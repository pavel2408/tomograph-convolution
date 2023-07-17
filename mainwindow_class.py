import sys
import numpy as np
from pathlib import Path
from copy import deepcopy
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QThread, QWaitCondition, QMutex, QObject
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QFileDialog

import load_dicom
import uis.mainwindow as mainwindow
from load_dicom import load_images_from_dicom
from uis.history_class import HistoryWin
from recognizer import Recognizer
from scan_history import ScanHistory
from uis.dicom_win_class import DicomWin
from uis.organs_info_class import OrgansWin
from uis.please_wait_class import PleaseWaitWin


class MainWindow(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.scan_history = None
        self.image_files = ""
        self.subject_name = ""
        self.cur_file = ""
        self.multiple_file_load_mutex = QMutex()
        self.history_save_is_finished = QWaitCondition()
        self.autosave_history = False
        self.class_properties = []
        self.analyze_file_name = ""
        self.dicom_file_name = ""
        self.thread = None
        self.recognizer = None
        self.properties = ""
        self.setupUi(self)
        self.dicom_win = DicomWin()
        self.organs_win = OrgansWin()
        self.please_wait_win = PleaseWaitWin(self)
        self.meta_string = ""
        self.first_view_images: list[QPixmap] = []
        self.second_view_images: list[QPixmap] = []
        self.third_view_images: list[QPixmap] = []

        self.first_view.description_label = self.first_view_description
        self.second_view.description_label = self.second_view_description
        self.third_view.description_label = self.third_view_description

        self.first_view_pointer = 0
        self.second_view_pointer = 0
        self.third_view_pointer = 0
        self.action_open_dicom.triggered.connect(self.load_tomography_image)
        self.action_reset_slices.triggered.connect(self.reset_pointers)
        # self.action_sync_with_first.triggered.connect(partial(self.sync_pointers, self.first_view))
        # self.action_sync_with_second.triggered.connect(partial(self.sync_pointers, self.second_view))
        # self.action_sync_with_third.triggered.connect(partial(self.sync_pointers, self.third_view))
        self.action_Analyze.triggered.connect(self.load_analyze)
        self.action_DICOM.triggered.connect(self.show_metadata)
        self.action_organs_info.triggered.connect(self.show_organ_info)
        self.action_check_cuda.triggered.connect(self.check_for_videocard)
        self.open_history_action.triggered.connect(self.open_history)
        self.save_history_action.triggered.connect(self.save_class_properties)
        self.view_menu.menuAction().setVisible(False)
        self.load_history_from_images_action.triggered.connect(self.load_history_from_folders)

    def load_history_from_folders(self):
        img_files, _ = QFileDialog.getOpenFileNames(
            None,
            caption="Выберите Analyze HDR файлы...",
            filter="Analyze files(*.hdr)",
        )
        if not img_files:
            return
        self.autosave_history = True
        img_files.sort()
        self.image_files = img_files
        self.load_analyze(self.image_files[0])

    def save_class_properties(self):
        if not self.class_properties:
            msg_box = QMessageBox(QtWidgets.QMessageBox.Icon.Critical, "Ошибка",
                                  "Откройте томографический снимок для анализа", parent=self)
            msg_box.show()
            return

        patient_name, ok = QInputDialog.getText(self, 'Введите значение', 'Введите имя пациента', text=self.subject_name)
        if not ok:
            return
        hours, ok = QInputDialog.getDouble(self, 'Введите значение', f'Введите количество часов с момента введения '
                                                                     f'вещества({Path(self.cur_file).name})', decimals=2)
        if not ok:
            return
        self.subject_name = patient_name
        print(hours)
        val = [patient_name, hours]
        for i in self.class_properties:
            val.append(i.intensity)
        self.scan_history = ScanHistory()
        self.scan_history.save_values(val)
        self.scan_history.close()

    def open_history(self):
        self.history_win = HistoryWin(self)
        if not self.history_win.is_err:
            self.history_win.show()

    def check_for_videocard(self):
        msg = QMessageBox(QMessageBox.Icon.Information, "Статус", "", parent=self)
        try:
            import torch.cuda as cuda
        except Exception as e:
            msg.setText("Отсутствует модуль pytorch")
            msg.show()
            return
        if not cuda.is_available():
            result_text = "Отсутствуют библиотеки CUDA"
        elif cuda.device_count() < 1:
            result_text = "Отсутствует видеокарта"
        else:
            result_text = f"Используемая видеокарта: {cuda.get_device_name(0)}"
        msg.setText(result_text)
        msg.show()

    def show_metadata(self):
        if self.meta_string != "":
            self.dicom_win.show()
        else:
            msg_box = QMessageBox(QtWidgets.QMessageBox.Icon.Critical, "Ошибка",
                                  "Не найдены данные для DICOM-файла", parent=self)
            msg_box.show()

    def show_organ_info(self):
        self.organs_win.show()

    def reset_pointers(self):
        self.first_view.sync_slices(0)
        self.second_view.sync_slices(0)
        self.third_view.sync_slices(0)

    def sync_pointers(self, sync_view):
        pointer = sync_view.slice_pointer
        self.first_view.sync_slices(pointer)
        self.second_view.sync_slices(pointer)
        self.third_view.sync_slices(pointer)

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

    def load_analyze(self, filename=""):
        if filename == "":
            self.analyze_file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Выберите Analyze HDR файл...",
                                                                              filter="Analyze files(*.hdr)")
            if not self.analyze_file_name:
                return
        else:
            self.analyze_file_name = filename
        self.cur_file = self.analyze_file_name
        self.action_DICOM.setEnabled(False)
        self.meta_string = ""
        self.recognizer = Recognizer(self.analyze_file_name, "analyze")
        self.first_view_pointer = 0
        self.second_view_pointer = 0
        self.third_view_pointer = 0
        self.first_view_images = []
        self.second_view_images = []
        self.third_view_images = []
        self.thread = QThread()
        self.recognizer.moveToThread(self.thread)
        self.thread.started.connect(self.recognizer.run_recognition)
        self.recognizer.progress.connect(self.please_wait_win.update_progress)
        self.recognizer.switch_task_count.connect(self.please_wait_win.switch_task_count)
        self.recognizer.finished.connect(self.thread.quit)
        self.recognizer.finished.connect(self.load_analyze_finished)
        self.recognizer.finished.connect(self.recognizer.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Step 6: Start the thread
        self.thread.start()
        self.please_wait_win.show()

    def load_analyze_finished(self):
        self.please_wait_win.hide()
        self.properties = self.recognizer.property_string
        # print(self.second_view_images[self.second_view_pointer].size())
        self.first_view.slices = self.recognizer.ax_images
        self.second_view.slices = self.recognizer.cor_images
        self.third_view.slices = self.recognizer.cag_images
        self.class_properties = deepcopy(self.recognizer.class_properties)

        self.first_view.slice_pointer = 0
        self.second_view.slice_pointer = 0
        self.third_view.slice_pointer = 0

        self.first_view.set_slice()
        self.second_view.set_slice()
        self.third_view.set_slice()
        self.view_menu.menuAction().setVisible(True)
        self.organs_win.textEdit.setText(self.properties)
        if self.autosave_history:
            self.save_class_properties()
            if not self.image_files:
                self.autosave_history = False
            else:
                self.image_files.pop(0)
                self.load_analyze(self.image_files[0])

    def load_tomography_image(self):
        self.dicom_file_name = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку с DICOM-файлами...")
        if not self.dicom_file_name:
            return
        self.meta_string = ""
        self.recognizer = Recognizer(self.dicom_file_name, "dicom")
        self.first_view_pointer = 0
        self.second_view_pointer = 0
        self.third_view_pointer = 0
        self.first_view_images = []
        self.second_view_images = []
        self.third_view_images = []
        self.thread = QThread()
        self.recognizer.moveToThread(self.thread)
        self.thread.started.connect(self.recognizer.run_recognition)
        self.recognizer.progress.connect(self.please_wait_win.update_progress)
        self.recognizer.switch_task_count.connect(self.please_wait_win.switch_task_count)
        self.recognizer.finished.connect(self.thread.quit)
        self.recognizer.finished.connect(self.load_tomography_image_finished)
        self.recognizer.finished.connect(self.recognizer.deleteLater)
        self.thread.finished.connect(self.recognizer.deleteLater)
        # Step 6: Start the thread
        self.thread.start()
        self.please_wait_win.show()
        # print(self.second_view_images[self.second_view_pointer].size())

    def load_tomography_image_finished(self):
        self.please_wait_win.hide()
        self.properties = self.recognizer.property_string
        self.first_view.slices = self.recognizer.ax_images
        self.second_view.slices = self.recognizer.cor_images
        self.third_view.slices = self.recognizer.cag_images
        self.class_properties = deepcopy(self.recognizer.class_properties)

        self.first_view.slice_pointer = 0
        self.second_view.slice_pointer = 0
        self.third_view.slice_pointer = 0

        print("hello")
        self.first_view.set_slice()
        self.second_view.set_slice()
        self.third_view.set_slice()
        self.view_menu.menuAction().setVisible(True)
        self.meta_string = load_dicom.get_metadata(self.dicom_file_name)
        self.dicom_win.textEdit.setText(self.meta_string)
        self.action_DICOM.setEnabled(True)
        self.organs_win.textEdit.setText(self.properties)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec()
