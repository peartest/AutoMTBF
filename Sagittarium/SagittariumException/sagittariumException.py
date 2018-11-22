# -*- coding: utf-8 -*-
__author__ = '赵嘉俊'

class NoSuchSupportDeviceException(Exception):

    def __init__(self,value):
        self.value = "Can not find the support device {name}".format(name=value)

    def __str__(self):
        return repr(self.value)

class TargetDeviceNoneValueException(Exception):

    def __init__(self,value):
        self.value = "The param targetDevice is None in script_start.You must specify a targetDevice id which you want " \
                     "playback script on"

    def __str__(self):
        return repr(self.value)

class InexistentDeviceIDException(Exception):
    def __init__(self,value):
        self.value = "The device {value} is inexistent".format(value=value)

    def __str__(self):
        return repr(self.value)