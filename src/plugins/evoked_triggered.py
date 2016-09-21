#!/usr/bin/env python

import os
import numpy as np
import uuid

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from util import fileloader
from util.qt import FileTable, FileTableModel, qtutil


class Widget(QWidget):
    def __init__(self, project, parent=None):
        super(Widget, self).__init__(parent)
        if not project:
            return
        self.project = project
        self.setup_ui()
        self.update_tables()

    def setup_ui(self):
        vbox = QVBoxLayout()
        self.table1 = FileTable()
        self.table1.setSelectionMode(QAbstractItemView.MultiSelection)
        vbox.addWidget(self.table1)
        pb = QPushButton('Generate Triggered Average')
        pb.clicked.connect(self.trigger_average)
        vbox.addWidget(pb)
        self.table2 = FileTable()
        vbox.addWidget(self.table2)
        self.setLayout(vbox)

    def update_tables(self):
        videos = [f for f in self.project.files if f['type'] == 'video']
        self.table1.setModel(FileTableModel(videos))
        videos = [
            f for f in self.project.files
            if 'manipulations' in f and 'trigger-avg' in f['manipulations']
            ]
        self.table2.setModel(FileTableModel(videos))

    def trigger_average(self):
        filenames = self.table1.selected_paths()
        if len(filenames) < 2:
            qtutil.warning('Select multiple files to average.')
            return
        frames = [fileloader.load_file(f) for f in filenames]
        lens = [len(frames[x]) for x in range(len(frames))]
        min_lens = np.min(lens)

        trig_avg = []
        for frame_set_index in range(min_lens):
            frames_to_avg = [frames[frame_index][frame_set_index]
                             for frame_index in range(len(frames))]
            frames_to_avg = np.concatenate(frames_to_avg)
            avg = np.mean(frames_to_avg, axis=0)
            trig_avg.append(avg)
        #frames = np.concatenate(frames)

        path = os.path.join(self.project.path, str(uuid.uuid4()) + 'trigger-avg.npy')
        np.save(path, trig_avg)
        self.project.files.append({
            'path': path,
            'type': 'video',
            'manipulations': 'trigger-avg',
            'source': filenames
        })
        self.project.save()
        self.update_tables()


class MyPlugin:
    def __init__(self, project):
        self.name = 'Concat videos'
        self.widget = Widget(project)

    def run(self):
        pass