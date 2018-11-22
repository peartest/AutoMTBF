# -*- coding: utf-8 -*-
__author__ = '赵嘉俊'

class SupportDevice():

    def __init__(self):
        self.udid = None
        self.mappingid = None
        self.logStorePath = None

    def setUdid(self,value):
        self.udid = value

    def setMappingUdid(self,value):
        self.mappingid = value

    def setLogStorePath(self,value):
        self.logStorePath = value