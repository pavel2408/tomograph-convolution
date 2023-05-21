import pydicom
import numpy as np
import matplotlib.pyplot as plt
from PIL import ImageQt, Image
import os

def transform_to_hu(medical_image, image):
    intercept = medical_image.RescaleIntercept
    slope = medical_image.RescaleSlope
    print(intercept, slope)
    hu_image = image * slope + intercept

    return hu_image

def get_max_value(images):
    max_value = images[0].max()
    for i in range(1, len(images)):
        value = images[i].max()
        if value > max_value:
            max_value = value
    return max_value


def save_to_file(images, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    # max_value = get_max_value(images)
    print(images)
    img_num = 0
    for im in images:
        image = convert_to_rgb(im)
        # image.save(directory + os.sep + str(img_num) + '.jpg')
        # img_num += 1


def convert_to_rgb(im):
    rescaled_image = (np.maximum(im, 0) / im.max()) * 255  # float pixels
    final_image = np.uint8(rescaled_image)  # integers pixels

    final_image = ImageQt.toqpixmap(Image.fromarray(final_image))
    return final_image


def get_names_of_imgs_inside_folder(directory: str):
    names = []
    for filename in os.listdir(directory):
        _, ext = os.path.splitext(filename)
        if ext in [".dcm"]:
            names.append(filename)
    return names


def load_images_from_dicom(source_dir: str):
    # source_dir = 'C:\\Users\\Pavel\\Downloads\\1548. Mouse 21 (tumor). 100 mkl LaF3 RT. 2 w. DICOM'
    o1 = 'o1'
    o2 = 'o2'
    o3 = 'o3'

    # load the DICOM files
    files = []

    print('dir: {}'.format(source_dir))
    fnames = get_names_of_imgs_inside_folder(source_dir)
    for fname in fnames:
        print("loading: {}".format(fname))
        files.append(pydicom.dcmread(source_dir + os.sep + fname))

    print("file count: {}".format(len(files)))

    # skip files with no SliceLocation (eg scout views)
    slices = []
    skipcount = 0
    for f in files:
        if hasattr(f, 'SliceLocation'):
            slices.append(f)
        else:
            skipcount = skipcount + 1

    print("skipped, no SliceLocation: {}".format(skipcount))

    # ensure they are in the correct order
    slices = sorted(slices, key=lambda s: s.SliceLocation)

    # pixel aspects, assuming all slices are the same
    ps = slices[0].PixelSpacing
    ss = slices[0].SliceThickness
    ax_aspect = ps[1] / ps[0]
    sag_aspect = ps[1] / ss
    cor_aspect = ss / ps[0]

    # create 3D array
    img_shape = list(slices[0].pixel_array.shape)
    img_shape.append(len(slices))
    img3d = np.zeros(img_shape)

    # fill 3D array with the images from the files
    for i, s in enumerate(slices):
        img2d = s.pixel_array
        img3d[:, :, i] = img2d

    images_o1 = list()
    for i in range(0, img_shape[2]):
        image = convert_to_rgb(img3d[:, :, i])
        images_o1.append(image)
    images_o2 = list()
    for i in range(0, img_shape[1]):
        image = convert_to_rgb(img3d[:, i, :])
        images_o2.append(image)
    images_o3 = list()
    for i in range(0, img_shape[0]):
        image = convert_to_rgb(img3d[i, :, :])
        images_o3.append(image)

    return images_o1, images_o2, images_o3
