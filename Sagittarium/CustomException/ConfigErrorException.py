# -*- coding: utf-8 -*-
__author__ = '赵嘉俊'


class ConfigFileNotExistException(Exception):

    def __init__(self,value):
        self.value = "Config file {value} not exist".format(value=value)

    def __str__(self):
        return repr(self.value)

class DeviceTagNotExistException(Exception):

    def __init__(self):
        self.value = "Device tag not exist in config file"

    def __str__(self):
        return repr(self.value)

class DeviceAttributeIsNotValid(Exception):

    def __init__(self,value):
        self.value = "Attribute {value} of device master device is not valid".format(value=value)

    def __str__(self):
        return repr(self.value)

class SupportDeviceAtrributeIsNotValid(Exception):

    def __init__(self,value):
        self.value = "Attribute {value} of support device is not valid".format(value=value)

    def __str__(self):
        return repr(self.value)


