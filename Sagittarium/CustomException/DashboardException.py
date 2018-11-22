# -*- coding: utf-8 -*-
__author__ = '赵嘉俊'

class TargetRecordFolderNotExistException(Exception):

    def __init__(self,value=None):
        self.value = 'Target record folder with {value} is not exist'.format(value=value)

    def __str__(self):
        return repr(self.value)
