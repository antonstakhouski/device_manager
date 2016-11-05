#!/usr/bin/env python

from device_manager import DeviceManager

if __name__ == '__main__':
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    dev_manager = DeviceManager()
    dev_manager.show()

    sys.exit(app.exec_())
