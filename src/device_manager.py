from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QWidget, QLabel, QTextBrowser, QTableWidget, QGridLayout, QTableWidgetItem, QPushButton
from device_finder import DeviceFinder
import libmount
import subprocess
import os


class DeviceManager(QWidget):

    """Widget for device management"""

    usb_table = list()
    # in ms
    table_update_interval = 1000

    def __init__(self, parent=None):
        """Adds elements to widget"""
        super(DeviceManager, self).__init__(parent)
        self.dev_finder = DeviceFinder()

        device_table_label = QLabel("Connected devices:")
        connection_log_label = QLabel("Device connection log:")

        self.unmount_button = QPushButton("Unmount selected drives")
        self.connection_log = QTextBrowser()
        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(device_table_label, 0, 0)
        self.grid_layout.addWidget(self.table_widget, 1, 0)
        self.grid_layout.addWidget(self.unmount_button, 2, 0)
        self.grid_layout.addWidget(connection_log_label, 3, 0)
        self.grid_layout.addWidget(self.connection_log, 4, 0)

        self.setWindowTitle("USB Manager")
        self.setLayout(self.grid_layout)

        column_count = 6
        self.table_widget.setColumnCount(column_count)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_widget.setHorizontalHeaderLabels(
            ["Device", "Label", "Mount point", "Total", "Used", "Free"])

        self.usb_table = self.dev_finder.get_usb_table()
        self.update_table_widget(self.usb_table)
        self.reload_device_table()
        self.unmount_button.pressed.connect(self.unmount_button_handler)

    def unmount_button_handler(self):
        """Unmount selected devices if they are not busy"""
        selected_fields = self.table_widget.selectedItems()
        for item in selected_fields:
            for device in self.usb_table:
                if item.text() == device[0] and len(device) > 2:
                    res = os.system("umount " + device[2])
                    if res:
                        self.connection_log.append(device[2] + "is busy")
                    else:
                        self.connection_log.append(device[2] + " is unmounted")
        self.usb_table = self.dev_finder.get_usb_table()
        self.update_table_widget(self.usb_table)

    def reload_device_table(self):
        """Gather info about connected devices"""
        new_usb_table = self.dev_finder.get_usb_table()

        self.remove_event_check(new_usb_table)
        self.connect_event_check(new_usb_table)

        if self.usb_table != new_usb_table:
            self.update_table_widget(new_usb_table)
            self.usb_table = new_usb_table

        QTimer.singleShot(self.table_update_interval, self.reload_device_table)

    def update_table_widget(self, new_usb_table):
        """Update connected devices table"""
        self.table_widget.clear()
        self.table_widget.setRowCount(len(new_usb_table))
        i = 0
        for device in new_usb_table:
            j = 0
            for field in device:
                self.table_widget.setItem(i, j, QTableWidgetItem(field))
                j += 1
            i += 1

    def connect_event_check(self, new_usb_table):
        """Show message on device connection"""
        for new_table_device in new_usb_table:
            found = False
            for device in self.usb_table:
                if new_table_device[0] == device[0]:
                    found = True
                    break
            if not found:
                self.connection_log.append(new_table_device[1] + " was connected")

    def remove_event_check(self, new_usb_table):
        """Show message on device remove"""
        for device in self.usb_table:
            found = False
            for new_table_device in new_usb_table:
                if device[0] == new_table_device[0]:
                    found = True
                    break
            if not found:
                self.connection_log.append(device[1] + " was removed")
