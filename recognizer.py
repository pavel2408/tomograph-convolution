import numpy as np
from PyQt5.QtGui import QPixmap, QImage
from matplotlib.path import Path
import os
import nibabel as nib
import re
from ultralytics import YOLO
from PIL import Image
from scipy.ndimage import median_filter
from PyQt5.QtCore import QObject, pyqtSignal
import load_dicom
from PIL import ImageQt, Image
import cv2


class Label:
    def __init__(self, class_index):
        self.class_index = class_index
        self.points = list()


class ClassProperty:
    def __init__(self, class_name, volume, intensity):
        self.class_name = class_name
        self.volume = volume
        self.intensity = intensity

    def __repr__(self):
        return f"{self.class_name}: {self.volume}, {self.intensity}"


def convert_to_qt(img: np.array):
    h, w, ch = img.shape
    bytesPerLine = ch * w
    toQt = QPixmap(QImage(img.data, w, h, bytesPerLine, QImage.Format_RGB888))
    return toQt


class Recognizer(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str, int)
    switch_task_count = pyqtSignal(int)

    def __init__(self, ct_path, ct_type):
        super(Recognizer, self).__init__()
        self.class_properties = []
        self.cag_images = None
        self.cor_images = None
        self.property_string = None
        self.ax_images = None
        self.helper_text = ""
        self.ct_type = ct_type
        self.ax_labels = {}
        self.cag_labels = {}
        self.cor_labels = {}
        # аксиальная проекция
        self.dir_ax_labels = 'labels\\ax'
        # сагиттальная проекция
        self.dir_cag_labels = 'labels\\cag'
        # коронарная проекция
        self.dir_cor_labels = 'labels\\cor'
        self.ct_path = ct_path
        self.class_names = ['Heart', 'Spleen', 'Liver', 'Kidneys', 'Bladder', 'Tumor']
        self.vox_volume = 0.028 * 0.028 * 0.028

    def load_labels(self, txt_labels_list):
        labels = list()
        for line in txt_labels_list:
            match = re.search(r'([0-9]+) (.*)', line)
            if match is None:
                continue
            label = Label(int(match.group(1)))
            values = match.group(2).split()
            for i in range(1, len(values), 2):
                label.points.append((float(values[i - 1]), float(values[i])))
            labels.append(label)
        return labels

    def get_mask(self, tupVerts, shape):
        x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))  # make a canvas with coordinates
        x, y = x.flatten(), y.flatten()
        points = np.vstack((y, x)).T

        p = Path(tupVerts)  # make a polygon
        grid = p.contains_points(points)
        mask = grid.reshape(shape)  # now you have a mask with points inside a polygon
        return mask

    def apply_labels(self, data, txt_labels_dict):
        shape = data[0, 0, :, :].shape
        total_steps = len(list(txt_labels_dict.keys()))
        step_count = 1
        self.switch_task_count.emit(total_steps)
        for key in txt_labels_dict:
            self.progress.emit(f"{self.helper_text}: метка {key}", step_count)
            step_count += 1
            labels = self.load_labels(txt_labels_dict[key])
            labels_dict = {}
            for label in labels:
                if label.class_index not in labels_dict:
                    labels_dict[label.class_index] = list()
                labels_dict[label.class_index].append(label)

            for class_index in labels_dict:
                arr = data[class_index, key, :, :]
                polys = list()

                labels = labels_dict[class_index]
                label = labels[0]

                points = np.multiply(label.points, shape)
                polys.append(Path(points))
                min_x = int(min(points[:, 0]))
                max_x = int(max(points[:, 0])) + 1
                min_y = int(min(points[:, 1]))
                max_y = int(max(points[:, 1])) + 1

                for i in range(1, len(labels)):
                    label = labels[i]

                    points = np.multiply(label.points, shape)
                    polys.append(Path(points))
                    min_x_1 = int(min(points[:, 0]))
                    max_x_1 = int(max(points[:, 0])) + 1
                    min_y_1 = int(min(points[:, 1]))
                    max_y_1 = int(max(points[:, 1])) + 1
                    if min_x_1 < min_x:
                        min_x = min_x_1
                    if max_x_1 > max_x:
                        max_x = max_x_1
                    if min_y_1 < min_y:
                        min_y = min_y_1
                    if max_y_1 > max_y:
                        max_y = max_y_1

                for i in range(min_x, max_x):
                    for j in range(min_y, max_y):
                        for poly in polys:
                            if poly.contains_point((i, j)):
                                arr[i, j] += 1
                                break

    def get_image(self, im):
        min_val = -300
        max_val = 1000
        rescaled_image = np.maximum(im, min_val)
        rescaled_image = np.minimum(rescaled_image, max_val)
        rescaled_image = rescaled_image - min_val

        rescaled_image = (rescaled_image / (max_val - min_val)) * 255  # float pixels
        final_image = np.uint8(rescaled_image)  # integers pixels
        final_image = final_image.transpose()

        final_image = Image.fromarray(final_image)
        return final_image

    def get_image_dicom(self, im):
        rescaled_image = (np.maximum(im, 0) / im.max()) * 255  # float pixels
        final_image = np.uint8(rescaled_image)  # integers pixels
        final_image = Image.fromarray(final_image)
        return final_image

    def get_analyze_labels_from_cnn(self, data, mask_dict, weights_path, is_dicom):
        model = YOLO(
            model=weights_path,
            task='segment',
        )
        self.switch_task_count.emit(data.shape[0])
        image_list = []
        for i in range(0, data.shape[0]):
            self.progress.emit(f"{self.helper_text}: Изображение {i+1} из {data.shape[0]}", i)
            if is_dicom:
                image = self.get_image_dicom(data[i, :, :])
            else:
                image = self.get_image(data[i, :, :])
            print("starting recognition...")
            result = model.predict(image)[0]
            print("recognition end.")
            masks = result.masks
            if masks is None:
                image_list.append(ImageQt.toqpixmap(image))
                continue
            else:
                if is_dicom:
                    plotted_img = result.plot()
                else:
                    plotted_img = result.plot(line_width=1, font_size=15, pil=True)
                qt_pix = convert_to_qt(plotted_img)
                image_list.append(qt_pix)
            lines = list()
            for j in range(len(masks)):
                cls = result.boxes[j].cls.item()
                points = masks[j].xyn[0]
                points_str = ' '.join([f'{point[0]} {point[1]}' for point in points])
                line = f'{int(cls)} {points_str}\n'
                lines.append(line)
            mask_dict[i] = lines
        return image_list

    def run_recognition(self):
        self.ax_images = []
        self.ax_labels = {}
        self.cag_images = []
        self.cag_labels = {}
        self.cor_images = []
        self.cor_labels = {}
        self.switch_task_count.emit(1)
        if self.ct_type == "dicom":
            self.progress.emit("Загружаю данные из DICOM-файлов...", 0)
            ct_data = load_dicom.load_images_from_dicom(self.ct_path)
            ct_data1 = ct_data
            self.progress.emit("Распознаю изображения на фронтальной проекции...", 0)
            self.helper_text = "Фронтальная проекция"
            self.ax_images = self.get_analyze_labels_from_cnn(ct_data1.transpose(2, 0, 1), self.ax_labels, 'weights\\ax.pt',
                                                         self.ct_type == "dicom")
            self.progress.emit("Распознаю изображения на сагиттальной проекции...", 0)
            self.helper_text = "Сагиттальная проекция"
            self.cor_images = self.get_analyze_labels_from_cnn(ct_data1.transpose(1, 0, 2), self.cor_labels,
                                                          'weights\\cag.pt', self.ct_type == "dicom")
            self.progress.emit("Распознаю изображения на корональной проекции...", 0)
            self.helper_text = "Корональная проекция"
            self.cag_images = self.get_analyze_labels_from_cnn(ct_data1.transpose(0, 1, 2), self.cag_labels,
                                                          'weights\\cor.pt', self.ct_type == "dicom")
        elif self.ct_type == "analyze":
            self.progress.emit("Загружаю данные из Analyze-файла...", 0)
            ct_img = nib.load(self.ct_path)
            ct_data = ct_img.get_fdata()
            ct_data1 = median_filter(ct_data, 3)
            self.progress.emit("Распознаю изображения на фронтальной проекции...", 0)
            self.helper_text = "Фронтальная проекция"
            self.ax_images = self.get_analyze_labels_from_cnn(ct_data1.transpose(2, 0, 1), self.ax_labels, 'weights\\ax.pt',
                                                         self.ct_type == "dicom")
            self.progress.emit("Распознаю изображения на корональной проекции...", 0)
            self.helper_text = "Корональная проекция"
            self.cor_images = self.get_analyze_labels_from_cnn(ct_data1.transpose(1, 0, 2), self.cor_labels,
                                                          'weights\\cor.pt', self.ct_type == "dicom")
            self.progress.emit("Распознаю изображения на сагиттальной проекции...", 0)
            self.helper_text = "Сагиттальная проекция"
            self.cag_images = self.get_analyze_labels_from_cnn(ct_data1.transpose(0, 1, 2), self.cag_labels,
                                                          'weights\\cag.pt', self.ct_type == "dicom")
        else:
            raise ValueError("Unsupported data format")

        shape = ct_data.shape
        data = np.zeros(shape=(len(self.class_names), shape[0], shape[1], shape[2]))

        self.switch_task_count.emit(1)
        self.progress.emit("Обрабатываю полученные метки для фронтальной проекции...", 0)
        self.helper_text = "Фронтальная проекция"
        self.apply_labels(data.transpose(0, 3, 1, 2), self.ax_labels)

        self.progress.emit("Обрабатываю полученные метки для корональной проекции...", 0)
        self.helper_text = "Корональная проекция"
        self.apply_labels(data.transpose(0, 2, 1, 3), self.cor_labels)

        self.progress.emit("Обрабатываю полученные метки для сагиттальной проекции...", 0)
        self.helper_text = "Сагиттальная проекция"
        self.apply_labels(data.transpose(0, 1, 2, 3), self.cag_labels)
        self.property_string = ""
        self.switch_task_count.emit(len(self.class_names))
        self.class_properties = []
        for i in range(len(self.class_names)):
            self.progress.emit(f"Расчитываю объём для класса {self.class_names[i]}...", i+1)
            self.property_string += f'{self.class_names[i]}:\n'
            class_data = data[i, :, :, :]
            unique, counts = np.unique(class_data, return_counts=True)
            counts = dict(zip(unique, counts))

            # получаем маску, где есть детекции как минимум в двух проекциях
            mask = np.ma.getmask(np.ma.masked_where(class_data < 2, class_data))
            # накладываем маску на исходное КТ
            class_data = np.ma.masked_where(mask, ct_data)
            # сжимаем данные и переводим в одномерный массив
            class_data = np.ma.compressed(class_data)
            vox_count = class_data.shape[0]
            try:
                volume = vox_count * self.vox_volume
            except:
                volume = 0
            self.property_string += f'\tvolume = {round(volume, 2)}ml\n'
            try:
                intensity_avg = sum(class_data) / vox_count
            except:
                intensity_avg = 0
            self.property_string += f'\tintensity_avg = {round(intensity_avg, 2)}HU\n'
            self.class_properties.append(ClassProperty(self.class_names[i], volume, intensity_avg))
        print(self.class_properties)
        self.finished.emit()
