"""
生成训练集和测试集及其名称
"""
import xml.etree.ElementTree as ET
import pickle
import os
import shutil
from os import listdir, getcwd
from os.path import join

sets = ['train', 'val']
classes = ['ws', 'sps', 'ds', 'brs', 'wsrs', 'Agaricus', 'Amanita', 'Boletus', 'Cortinarius', 'Entoloma',
           'Hygrocybe', 'Lactarius', 'Russula', 'Suillus', 'Chicory', 'Harebell', 'Knapweed', 'Mallow',
           'Mayapple', 'Boerner', 'Leconte', 'Linnaeus', 'acuminatus', 'armandi',
           'coleoptera', 'linnaeus']


def convert(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


def convert_annotation(image_id):
    in_file = open('data/all_xml/%s.xml' % (image_id), encoding='utf-8')
    out_file = open('data/all_labels/%s.txt' % (image_id), 'w', encoding='utf-8')
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult) == 1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        """b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text),
             float(xmlbox.find('ymax').text))"""

        """
        防止xml文件中min值比max值大，导致txt文件中标记数据出现负值的情况
        """
        b = [float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text),
             float(xmlbox.find('ymax').text)]
        if b[0] > b[1]:
            b[0], b[1] = b[1], b[0]
        if b[2] > b[3]:
            b[2], b[3] = b[3], b[2]
        b = tuple(b)

        bb = convert((w, h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')


wd = getcwd()
print(wd)
for image_set in sets:
    if not os.path.exists('data/all_labels/'):
        os.makedirs('data/all_labels/')
    image_ids = open('data/ImageSets/%s.txt' % (image_set), encoding='utf-8').read().strip().split()
    image_list_file = open('data/images_%s.txt' % (image_set), 'w', encoding='utf-8')
    labels_list_file = open('data/labels_%s.txt' % (image_set), 'w', encoding='utf-8')
    for image_id in image_ids:
        image_list_file.write('%s.jpg\n' % (image_id))
        labels_list_file.write('%s.txt\n' % (image_id))
        convert_annotation(image_id)  # 如果标签已经是txt格式，将此行注释掉，所有的txt存放到all_labels文件夹。
    image_list_file.close()
    labels_list_file.close()


def copy_file(new_path, path_txt, search_path):  # 参数1：存放新文件的位置  参数2：为上一步建立好的train,val训练数据的路径txt文件  参数3：为搜索的文件位置
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    with open(path_txt, 'r') as lines:
        filenames_to_copy = set(line.rstrip() for line in lines)
        # print('filenames_to_copy:',filenames_to_copy)
        # print(len(filenames_to_copy))
    for root, _, filenames in os.walk(search_path):
        # print('root',root)
        # print(_)
        # print(filenames)
        for filename in filenames:
            if filename in filenames_to_copy:
                shutil.copy(os.path.join(root, filename), new_path)


# 按照划分好的训练文件的路径搜索目标，并将其复制到yolo格式下的新路径
copy_file('./data/images/train/', './data/images_train.txt', './data/all_images')
copy_file('./data/images/val/', './data/images_val.txt', './data/all_images')
copy_file('./data/labels/train/', './data/labels_train.txt', './data/all_labels')
copy_file('./data/labels/val/', './data/labels_val.txt', './data/all_labels')
