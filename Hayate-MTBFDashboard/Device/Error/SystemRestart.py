# -*- coding: utf-8 -*-
__author__ = '赵嘉俊'

from  Device.Error.Error import AndroidError

class AndroidSystemRestart(AndroidError):

    def __init__(self):
        AndroidError.__init__(self)