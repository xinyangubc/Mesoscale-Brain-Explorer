#!/usr/bin/env python3

import ast
import os

import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from .fileloader import load_reference_frame
from .mse_ui_elements import CheckableComboBox, PlayerDialog
from . import fileloader
from . import constants

def save_project(video_path, project, frames, manip, file_type):
    name_before, ext = os.path.splitext(os.path.basename(video_path))
    file_before = [files for files in project.files if files['name'] == name_before]
    assert(len(file_before) == 1)
    file_before = file_before[0]

    name_after = fileloader.get_name_after_no_overwrite(name_before, manip, project)
    # check if one with same name already exists and don't overwrite if it does
    # name_after = str(name_before + '_' + manip + '.')
    # name_after_copy = str(name_before + '_' + manip + '(')
    # file_after = [files for files in project.files if name_after in files['path'] or name_after_copy in files['name']]
    #
    # if len(file_after) > 0:
    #     name_after = str(name_before + '_' + manip) + '(' + str(len(file_after)) + ')'
    # else:
    #     name_after = str(name_before + '_' + manip)

    path = str(os.path.normpath(os.path.join(project.path, name_after) + '.npy'))
    if frames is not None:
        if os.path.isfile(path):
            progress = QProgressDialog('Deleting ' + path, 'Abort', 0, 100)
            progress.setAutoClose(True)
            progress.setMinimumDuration(0)
            def callback_del(x):
                progress.setValue(x * 100)
                QApplication.processEvents()
            callback_del(0)
            os.remove(path)
            callback_del(1)
        progress = QProgressDialog('Saving ' + path + ' to file. This could take a few minutes.', 'Abort', 0, 100)
        progress.setAutoClose(True)
        progress.setMinimumDuration(0)
        def callback_save(x):
            progress.setValue(x * 100)
            QApplication.processEvents()
        callback_save(0)
        np.save(path, frames)
        callback_save(1)
    if not file_before['manipulations'] == []:
        project.files.append({
            'path': os.path.normpath(path),
            'type': file_type,
            'source_video': video_path,
            'manipulations': str(ast.literal_eval(file_before['manipulations']) + [manip]),
            'name': name_after
        })
    else:
        project.files.append({
            'path': os.path.normpath(path),
            'type': file_type,
            'source_video': video_path,
            'manipulations': str([manip]),
            'name': name_after
        })
    file_after_test = [files for files in project.files if files['name'] == name_after]
    assert (len(file_after_test) == 1)
    project.save()
    return path

def change_origin(project, video_path, origin):
    file = [files for files in project.files if os.path.normpath(files['path']) == os.path.normpath(video_path)]
    assert(len(file) == 1)
    file = file[0]
    index_of_file = project.files.index(file)
    project.files[index_of_file]['origin'] = str(origin)
    project.save()

# Always ensure all reference_frames come first in the list
# def refresh_all_list(project, video_list, indices, last_manips_to_display=['All']):
#     video_list.model().clear()
#     for f in project.files:
#         item = QStandardItem(f['name'])
#         item.setDropEnabled(False)
#         if f['type'] != 'ref_frame':
#             continue
#         video_list.model().appendRow(item)
#     for f in project.files:
#         item = QStandardItem(f['name'])
#         item.setDropEnabled(False)
#         if f['type'] != 'video':
#             continue
#         if 'All' in last_manips_to_display:
#             video_list.model().appendRow(item)
#         elif f['manipulations'] != []:
#             if ast.literal_eval(f['manipulations'])[-1] in last_manips_to_display:
#                 video_list.model().appendRow(item)
#
#     if len(indices) > 1:
#         theQIndexObjects = [video_list.model().createIndex(rowIndex, 0) for rowIndex in
#                             indices]
#         for Qindex in theQIndexObjects:
#             video_list.selectionModel().select(Qindex, QItemSelectionModel.Select)
#     else:
#         video_list.setCurrentIndex(video_list.model().index(indices[0], 0))


def refresh_list(project, ui_list, indices, types, last_manips_to_display):
    ui_list.model().clear()
    for type in types:
        for f in project.files:
            item = QStandardItem(f['name'])
            item.setDropEnabled(False)
            if f['type'] != type:
                continue
            if 'All' in last_manips_to_display:
                ui_list.model().appendRow(QStandardItem(item))
            elif f['manipulations'] != []:
                if ast.literal_eval(f['manipulations'])[-1] in last_manips_to_display:
                    ui_list.model().appendRow(item)

    if len(indices) > 1:
        theQIndexObjects = [ui_list.model().createIndex(rowIndex, 0) for rowIndex in
                            indices]
        for Qindex in theQIndexObjects:
            ui_list.selectionModel().select(Qindex, QItemSelectionModel.Select)
    elif len(indices) == 1:
        ui_list.setCurrentIndex(ui_list.model().index(indices[0], 0))


def refresh_video_list_via_combo_box(widget, list_display_type, trigger_item=None):
    if trigger_item != 0:
        widget.toolbutton.model().item(0, 0).setCheckState(Qt.Unchecked)

    last_manips_to_display = []
    for i in range(widget.toolbutton.count()):
        if widget.toolbutton.model().item(i, 0).checkState() != 0:
            last_manips_to_display = last_manips_to_display + [widget.toolbutton.itemText(i)]
    refresh_list(widget.project, widget.video_list, [0], list_display_type, last_manips_to_display)

def get_project_file_from_key_item(project, key, item):
    file = [files for files in project.files if os.path.normpath(files[key]) == os.path.normpath(item)]
    if not file:
        return
    assert (len(file) == 1)
    return file[0]

def add_combo_dropdown(widget, items):
    widget.ComboBox = CheckableComboBox()
    widget.ComboBox.addItem('All')
    item = widget.ComboBox.model().item(0, 0)
    item.setCheckState(Qt.Checked)
    for i, text in enumerate(items):
        widget.ComboBox.addItem(text)
        item = widget.ComboBox.model().item(i+1, 0)
        item.setCheckState(Qt.Unchecked)
    return widget.ComboBox


def flatten(foo):
    for x in foo:
        if hasattr(x, '__iter__') and not isinstance(x, str):
            for y in flatten(x):
                yield y
        else:
            yield x

#todo: fix toolbutton...
def get_list_of_project_manips(project):
    vid_files = [f for f in project.files if f['type'] in constants.TOOLBUTTON_TYPES]
    list_of_manips = [x['manipulations'] for x in vid_files if x['manipulations'] != []]
    list_of_manips = [ast.literal_eval(l) for l in list_of_manips]
    list_of_manips = list(flatten(list_of_manips))
    return list(set(list_of_manips))


def selected_video_changed_multi(widget, selected, deselected):
    if not widget.video_list.selectedIndexes() or not widget.video_list.currentIndex().data(Qt.DisplayRole):
        return
    # for index in deselected.indexes():
    #     vidpath = str(os.path.join(widget.project.path,
    #                                index.data(Qt.DisplayRole))
    #                   + '.npy')
    #     widget.selected_videos = [x for x in widget.selected_videos if x != vidpath]
    widget.selected_videos = []
    for index in widget.video_list.selectedIndexes():
        vidpath = str(os.path.normpath(os.path.join(widget.project.path, index.data(Qt.DisplayRole)) + '.npy'))
        if vidpath not in widget.selected_videos and vidpath != 'None':
            widget.selected_videos = widget.selected_videos + [vidpath]
            widget.shown_video_path = str(os.path.normpath(os.path.join(widget.project.path,
                                                       widget.video_list.currentIndex().data(Qt.DisplayRole))
                                    + '.npy'))
    frame = load_reference_frame(widget.shown_video_path)
    widget.view.show(frame)


def video_triggered(widget, index):
    filename = str(os.path.join(widget.project.path, index.data(Qt.DisplayRole)) + '.npy')
    dialog = PlayerDialog(widget.project, filename, widget)
    dialog.show()
    # widget.open_dialogs.append(dialog)

def update_plugin_params(widget, key, val):
    widget.params[key] = val
    widget.project.pipeline[widget.plugin_position] = widget.params
    widget.project.save()
