# -*- coding: utf-8 -*-
__author__ = '赵嘉俊'

class AndroidScript():

    def __init__(self):
        self.relatedDevice = None;
        self.relatedDeviceMappingid = None;
        self.startTime = None;
        self.endTime = None;
        self.name = None;
        self.round = None
        self.loop = None;
        self.result = None;
        self.logFolder = None;
        self.OKInfo = None;
        self.ErrorInfo = None;
        self.steps = None
        self.recordFile = None
        self.logcatPath = None

    def setRelatedDevice(self,value):self.relatedDevice = value

    def setRelatedDeviceMappingId(self,value):self.relatedDeviceMappingid = value

    def setStartTime(self,value):self.startTime = value

    def setEndTime(self,value):self.endTime = value

    def setName(self,value):self.name = value

    def setLoop(self,value):self.loop = value

    def setRound(self,value):self.round = value

    def setResult(self,value): self.result = value

    def setLogFolder(self,value):self.logFolder = value

    def setOKInfo(self,value):self.OKInfo = value

    def setErrorInfo(self,value):self.ErrorInfo = value

    def setSteps(self,value):self.steps = value

    def generateRecordFilePath(self):
        self.recordFile = 'record\\{device}\\{round}\\{name}\\{logFolder}\\Record.xml'.format(
            device=self.relatedDeviceMappingid if not self.relatedDeviceMappingid == "None" else self.relatedDevice,
            round=self.round,
            name=self.name,
            logFolder=self.logFolder)

    def generateLogcatPath(self):
        self.logcatPath = 'logcat\\{device}\\{round}\\{name}\\{logFolder}'.format(
            device=self.relatedDeviceMappingid if not self.relatedDeviceMappingid == "None" else self.relatedDevice,
            round=self.round,
            name=self.name,
            logFolder=self.logFolder)