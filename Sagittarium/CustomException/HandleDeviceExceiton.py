# -*- coding: utf-8 -*-
__author__ = '赵嘉俊'

class RootDeviceException(Exception):

    def __init__(self,id=None,error=None):
        self.value = "Root device {id} fail.{error}".format(id=id,error=error)

    def __str__(self):
        return repr(self.value)

class PullDropboxFilesException(Exception):

    def __init__(self,id=None,error=None):
        self.value = "Device {id} pull dropbox fail.{error}".format(id=id,error=error)

    def __str__(self):
        return repr(self.value)

class PullLogcatFilesException(Exception):

    def __init__(self,id=None,error=None):
        self.value = "Device {id} pull logcat fail.{error}".format(id=id,error=error)

    def __str__(self):
        return repr(self.value)



