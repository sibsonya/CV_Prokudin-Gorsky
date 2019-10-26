#! /usr/bin/python3

import numpy as np
from skimage import io
import math

CUTTING_PERSENT = 5 # %
MAX_SIZE = 500 # pixels


def load_image(path):
    return io.imread(path, plugin='matplotlib')


def height(img):
    return len(img)


def width(img):
    if height(img) == 0:
        return 0
    return len(img[0])


def vertical_split(img, parts_count):
    new_height = height(img) // parts_count
    return [img[new_height * i : new_height * (i + 1)] for i in range(parts_count)]


def cut_edge(img, persent):
    deleted_rows_count = height(img) * persent // 100
    deleted_columns_count = width(img) * persent // 100
    return img[deleted_rows_count : height(img) - deleted_rows_count, 
            deleted_columns_count : width(img) - deleted_columns_count]


def calculate_overlap_intervals(moving_img, dx, dy):
    start_x = max(0, dx)
    start_y = max(0, dy)
    end_x = min(width(moving_img), width(moving_img) + dx)
    end_y = min(height(moving_img), height(moving_img) + dy)
    return [start_x, start_y, end_x, end_y]


def mse(static_img, moving_img, dx, dy):
    start_x, start_y, end_x, end_y = calculate_overlap_intervals(moving_img, dx, dy)
    return -np.sum(np.square(static_img[start_y : end_y, start_x : end_x] - 
            moving_img[start_y - dy : end_y - dy, start_x - dx : end_x - dx])) / (end_x - start_x) * (end_y - start_y)


def cross_correlation(static_img, moving_img, dx, dy):
    start_x, start_y, end_x, end_y = calculate_overlap_intervals(moving_img, dx, dy)
    new_static_img = static_img[start_y : end_y, start_x : end_x]
    new_moving_img = moving_img[start_y - dy : end_y - dy, start_x - dx : end_x - dx]
    return np.sum(new_static_img * new_moving_img) / math.sqrt(float(np.sum(np.square(new_moving_img))) * float(np.sum(np.square(new_static_img))))


def basic_superposition(static_img, moving_img, metric_function, y_range, x_range):
    result_align = (0, 0)
    max_correlation = 0
    initialized = False
    for dx in range(x_range[0], x_range[1] + 1):
        for dy in range(y_range[0], y_range[1] + 1):
            correlation = metric_function(static_img, moving_img, dx, dy)
            if not initialized or max_correlation < correlation:
                max_correlation = correlation
                initialized = True
                result_align = (dy, dx)
    return result_align


def press2(img):
    if img.shape[0] % 2 != 0:
        img = img[:img.shape[0] - 1, ::]
    if img.shape[1] % 2 != 0:
        img = img[::, :img.shape[1] - 1]
    return (img[::2, ::2] + img[1::2, ::2] + img[::2, 1::2] + img[1::2, 1::2]) / 4


def align(img, g_coord):
    img1, img2, img3 = vertical_split(img, 3)
    height_ = height(img1)
    img1 = np.array(cut_edge(img1, CUTTING_PERSENT))
    img2 = np.array(cut_edge(img2, CUTTING_PERSENT))
    img3 = np.array(cut_edge(img3, CUTTING_PERSENT))
    imgs = list([[img1, img2, img3]])
    while max(height(imgs[-1][0]), width(imgs[-1][0])) > MAX_SIZE:
        imgs.append([
            press2(imgs[-1][0]),
            press2(imgs[-1][1]),
            press2(imgs[-1][2])])
    dy1, dx1 = basic_superposition(imgs[-1][1], imgs[-1][0], mse, (-15,15), (-15, 15))
    dy3, dx3 = basic_superposition(imgs[-1][1], imgs[-1][2], mse, (-15,15), (-15, 15))
    res = np.array([dy1, dx1, dy3, dx3]) # dy1 dx1 dy3 dx3

    for i in range(len(imgs) - 2, -1, -1):
        res = 2 * res
        dy1, dx1 = basic_superposition(imgs[i][1], imgs[i][0], mse, (res[0], res[0] + 1), (res[1], res[1] + 1))
        dy3, dx3 = basic_superposition(imgs[i][1], imgs[i][2], mse, (res[2], res[2] + 1), (res[3], res[3] + 1))
        res = np.array([dy1, dx1, dy3, dx3])

    imgs[0][0] = np.roll(imgs[0][0], (res[0], res[1]), axis = (0, 1))
    imgs[0][2] = np.roll(imgs[0][2], (res[2], res[3]), axis = (0, 1))
    aligned_img = np.vstack((imgs[0][0], imgs[0][1], imgs[0][2]))

    return aligned_img, (g_coord[0] - res[0] - height_, g_coord[1] - res[1]), (g_coord[0] - res[2] + height_, g_coord[1] - res[3])