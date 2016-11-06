from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QAbstractItemView, QVBoxLayout
from PyQt5.QtWidgets import QWidget, QLabel, QTextBrowser, QTableWidget, QGridLayout, QTableWidgetItem, QPushButton
from device_finder import DeviceFinder
from PyQt5.Qt import Qt
import os


class DeviceManager(QWidget):

    """Widget for device management"""

    usb_table = list()
    # in ms
    table_update_interval = 1000
    dev_finder = DeviceFinder()

    def __init__(self, parent=None):
        """Adds elements to widget"""
        super(DeviceManager, self).__init__(parent)

        block_device_table_label = QLabel("Block devices:")
        mtp_device_table_label = QLabel("MTP devices:")
        connection_log_label = QLabel("Device connection log:")

        self.unmount_button = QPushButton("Unmount selected drives")
        self.reload_mtp_list_button = QPushButton("Reload MTP list")
        self.connection_log = QTextBrowser()

        self.block_device_table_widget = QTableWidget()
        self.block_device_table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.mtp_device_table_widget = QTableWidget()
        self.mtp_device_table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.main_layout_init(block_device_table_label, connection_log_label, mtp_device_table_label)
        self.setWindowTitle("USB Manager")

        self.block_header = ["Device", "Label", "Mount point", "Total", "Used", "Free"]
        self.block_device_table_widget.setColumnCount(len(self.block_header))
        self.block_device_table_widget.setHorizontalHeaderLabels(self.block_header)
        self.block_device_table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.mtp_header = ["Manufacturer", "Model", "Total", "Free", "Used", "Storage Description"]
        self.mtp_device_table_widget.setColumnCount(len(self.mtp_header))
        self.mtp_device_table_widget.setHorizontalHeaderLabels(self.mtp_header)
        self.mtp_device_table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.usb_table = self.dev_finder.get_usb_table()
        self.update_table_widget(self.usb_table)
        self.reload_device_table()
        self.unmount_button.pressed.connect(self.unmount_button_handler)
        self.reload_mtp_list_button.pressed.connect(self.reload_mtp_handler)

    def reload_mtp_handler(self):
        mtp_list = self.dev_finder.get_mtp_devices()
        self.mtp_device_table_widget.clear()
        self.mtp_device_table_widget.setHorizontalHeaderLabels(self.mtp_header)
        self.mtp_device_table_widget.setRowCount(len(mtp_list))
        i = 0
        for device in mtp_list:
            j = 0
            for field in device:
                self.mtp_device_table_widget.setItem(i, j, QTableWidgetItem(field))
                j += 1
            i += 1

    def main_layout_init(self, block_device_table_label, connection_log_label, mtp_device_table_label):
        grid_layout = self.grid_layout_init(block_device_table_label, mtp_device_table_label)
        vbox_layout = self.vbox_layout_init(connection_log_label)
        main_layout = QGridLayout()
        main_layout.addLayout(grid_layout, 0, 0)
        main_layout.addLayout(vbox_layout, 1, 0)
        self.setLayout(main_layout)

    def vbox_layout_init(self, connection_log_label):
        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(connection_log_label)
        vbox_layout.addWidget(self.connection_log)
        return vbox_layout

    def grid_layout_init(self, block_device_table_label, mtp_device_table_label):
        grid_layout = QGridLayout()
        grid_layout.addWidget(block_device_table_label, 0, 0, Qt.AlignCenter)
        grid_layout.addWidget(mtp_device_table_label, 0, 1, Qt.AlignCenter)
        grid_layout.addWidget(self.block_device_table_widget, 1, 0)
        grid_layout.addWidget(self.mtp_device_table_widget, 1, 1)
        grid_layout.addWidget(self.unmount_button, 2, 0)
        grid_layout.addWidget(self.reload_mtp_list_button, 2, 1)
        return grid_layout

    def unmount_button_handler(self):
        """Unmount selected devices if they are not busy"""
        selected_fields = self.block_device_table_widget.selectedItems()
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
        self.block_device_table_widget.clear()
        self.block_device_table_widget.setHorizontalHeaderLabels(self.block_header)
        self.block_device_table_widget.setRowCount(len(new_usb_table))
        i = 0
        for device in new_usb_table:
            j = 0
            for field in device:
                self.block_device_table_widget.setItem(i, j, QTableWidgetItem(field))
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
