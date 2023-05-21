from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from copy import deepcopy


class SliceLabel(QtWidgets.QLabel):
    def __init__(self, parent):
        super(SliceLabel, self).__init__(parent=parent)
        self.__slices = []
        self.slice_pointer = 0
        self.__description_label: QLabel = None
        self.description_text = ""

    @property
    def description_label(self):
        return self.__description_label

    @description_label.setter
    def description_label(self, new_label: QLabel):
        self.__description_label = new_label
        self.description_text = new_label.text()

    @property
    def slices(self):
        return self.__slices

    @slices.setter
    def slices(self, new_slices):
        self.__slices = new_slices

    def sync_slices(self, new_pointer):
        if new_pointer >= len(self.__slices) - 1:
            print('?')
            return
        self.slice_pointer = new_pointer
        self.set_slice()

    def set_slice(self):
        self.__slices[self.slice_pointer] = self.__slices[self.slice_pointer].scaled(self.width()/1.25, self.height()/1.25, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.setPixmap(self.__slices[self.slice_pointer])
        self.__description_label.setText(self.description_text + f" ({self.slice_pointer+1} из {len(self.__slices)})")

    def wheelEvent(self, e: QtGui.QWheelEvent) -> None:
        if not self.__slices:
            return super(SliceLabel, self).wheelEvent(e)
        # wheel up
        if e.angleDelta().y() > 0:
            if self.slice_pointer <= 0:
                return super(SliceLabel, self).wheelEvent(e)
            self.slice_pointer -= 1
        # wheel down
        else:
            if self.slice_pointer >= len(self.__slices) - 1:
                return super(SliceLabel, self).wheelEvent(e)
            self.slice_pointer += 1
        print(self.slice_pointer, len(self.__slices))
        self.set_slice()
        return super(SliceLabel, self).wheelEvent(e)
