#!/usr/bin/env python

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os


class DeviceManager(QWidget):
    usb_table = list()

    def __init__(self, parent=None):
        super(DeviceManager, self).__init__(parent)

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

        self.usb_table = self.get_usb_table()
        self.reload_device_table()

    def reload_device_table(self):
        # in ms
        call_interval = 1000
        new_usb_table = self.get_usb_table()

        for device in self.usb_table:
            found = False
            for new_table_device in new_usb_table:
                if device[0] == new_table_device[0]:
                    found = True
                    break
            if not found:
                print(device[1] + " was removed")

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

    def find_dev_mount_point(self, usb_table):
        mounts = open("/proc/mounts")
        mount_points = mounts.readlines()
        table = usb_table
        i = 0
        for device in table:
            for point in mount_points:
                arguments = point.split(" ")
                if arguments[0] == device[0]:
                    usb_table[i].append(arguments[1])
                    break
            i += 1
        return usb_table

    def get_usb_table(self):
        usb_set = self.get_device_list_by_path()
        block_device_list = self.get_device_list_by_label()

        usb_set = sorted(usb_set)
        usb_table = list()
        for device in usb_set:
            for element in block_device_list:
                if device == element[0]:
                    usb_table.append(element)
                    break
        usb_table = self.find_dev_mount_point(usb_table)
        return usb_table

    def get_device_list_by_label(self):
        by_label_dir = "/dev/disk/by-label/"
        block_devices = os.listdir(by_label_dir)
        block_device_list = list()
        for device in block_devices:
            block_device_list.append([os.path.abspath(by_label_dir + os.readlink(by_label_dir + device)),
                                      device])
        return block_device_list

    def get_device_list_by_path(self):
        by_path_dir = "/dev/disk/by-path/"
        disk_list = os.listdir(by_path_dir)
        usb_set = set()
        for device in disk_list:
            if device.find("usb") != -1:
                path = os.readlink(by_path_dir + device)
                abs_path = os.path.abspath(by_path_dir + path)
                usb_set.add(abs_path)
        return usb_set

if __name__ == '__main__':
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    dev_manager = DeviceManager()
    dev_manager.show()

    sys.exit(app.exec_())
