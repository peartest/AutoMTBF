# -*- coding: utf-8 -*-

class SupportDevice:

    def __init__(self):
        self.udid = None
        self.mappingid = None
        self.logStorePath = None

    def setUdid(self,value=None):
        self.udid = value;

    def setMappingId(self,value=None):
        self.mappingid = value;

    def setLogStorePath(self,value=None):
        self.logStorePath = value