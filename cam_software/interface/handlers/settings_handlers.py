import win32api
import os
import shutil


def get_driveLabels():
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    return drives


def get_presetFiles():
    return os.listdir(path='accuracy_presets/')


def image_shower(drive_letter):
    source_dir = drive_letter
    target_dir = 'images/'
    file_list = os.listdir(source_dir)
    image_list = []
    for i in file_list:
        buff = os.path.splitext(i)
        if buff[1] == '.bmp':
            image_list.append(drive_letter + i)
            #shutil.move(os.path.join(source_dir, i), target_dir)
    return image_list

def image_remover(drive_letter):
    source_dir = drive_letter
    target_dir = 'images/'
    file_list = os.listdir(source_dir)
    image_list = []
    for i in file_list:
        buff = os.path.splitext(i)
        if buff[1] == '.bmp':
            os.remove(drive_letter + i)
    return image_list
