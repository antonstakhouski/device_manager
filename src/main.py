#!/usr/bin/env python

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os
from device_finder import *


class DeviceManager(QWidget):
    usb_table = list()

    def __init__(self, parent=None):
        super(DeviceManager, self).__init__(parent)
        self.dev_finder = DeviceFinder()

        device_table_label = QLabel("Connected devices:")
        connection_log_label = QLabel("Device connection log:")

        self.connection_log = QTextBrowser()
        self.table_widget = QTableWidget()

        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(device_table_label, 0, 0)
        self.grid_layout.addWidget(self.table_widget, 1, 0)
        self.grid_layout.addWidget(connection_log_label, 2, 0)
        self.grid_layout.addWidget(self.connection_log, 3, 0)

        self.setWindowTitle("USB Manager")
        self.setLayout(self.grid_layout)

        column_count = 3
        self.table_widget.setColumnCount(column_count)
        self.table_widget.setHorizontalHeaderLabels(["Device", "Label", "Mount point"])

        self.usb_table = self.dev_finder.get_usb_table()
        self.reload_device_table()

    def reload_device_table(self):
        # in ms
        call_interval = 1000
        new_usb_table = self.dev_finder.get_usb_table()

        self.remove_event_check(new_usb_table)
        self.connect_event_check(new_usb_table)

        self.table_widget.setRowCount(len(new_usb_table))
        i = 0
        for device in new_usb_table:
            j = 0
            for field in device:
                self.table_widget.setItem(i, j, QTableWidgetItem(field))
                j += 1
            i += 1
        self.usb_table = new_usb_table
        QTimer.singleShot(call_interval, self.reload_device_table)

    def connect_event_check(self, new_usb_table):
        for new_table_device in new_usb_table:
            found = False
            for device in self.usb_table:
                if new_table_device[0] == device[0]:
                    found = True
                    break
            if not found:
                self.connection_log.append(new_table_device[1] + " was connected")

    def remove_event_check(self, new_usb_table):
        for device in self.usb_table:
            found = False
            for new_table_device in new_usb_table:
                if device[0] == new_table_device[0]:
                    found = True
                    break
            if not found:
                self.connection_log.append(device[1] + " was removed")


if __name__ == '__main__':
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    dev_manager = DeviceManager()
    dev_manager.show()

    sys.exit(app.exec_())
