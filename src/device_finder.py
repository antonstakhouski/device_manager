import os


class DeviceFinder:
    def __init__(self):
        pass

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