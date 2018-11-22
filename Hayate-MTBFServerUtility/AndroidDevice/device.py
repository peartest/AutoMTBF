# -*- coding: utf-8 -*-

from Repeater import Log

class Device:

    def __init__(self):
        self.deviceID = None
        self.deviceMappingID = None
        self.mtbfLogStorePath = None
        self.serverPort = None
        self.tcpPort = None
        self.isDriverByTime = None
        self.pbModel = None
        self.value = None
        self.scripts=[];
        self.bootstrapPort=None
        self.reliantDevices=[]
        self.supportDevices=[]
        self.process = []

    def setDeviceID(self,id=None):
        self.deviceID = id

    def setDeviceMappingID(self,mappingid=None):
        self.deviceMappingID = mappingid;

    def setMtbfLogStorePath(self,path=None):
        self.mtbfLogStorePath = path

    def setServerPort(self,port=None):
        self.serverPort = port

    def setTcpPort(self,tcp=None):
        self.tcpPort = tcp

    def setDriverByTime(self,driverByTime=None):
        self.isDriverByTime = driverByTime

    def setPlaybackModel(self,model=None):
        self.pbModel = model

    def setTestTime(self,time):
        self.value = time

    def setBootstrapPort(self,bootstrapPort=None):
        self.bootstrapPort = bootstrapPort

    def setDeviceScripts(self,scriptsList=None):
        self.scripts=scriptsList

    def setReliantDevices(self,reliantDevices=[]):
        self.reliantDevices = reliantDevices

    def setSupportDevices(self,supportDevices=[]):
        self.supportDevices = supportDevices

    def getMasterDeviceID(self):
        """
        获取主设备
        :return:
        """
        master = None
        for device in self.reliantDevices:
            if device['role'] == 'master':
                master = device['udid']
                break
        return master

    def getSlaveDeviceID(self):
        """
        获取奴隶设备
        :return:
        """
        slaves = []
        for device in self.reliantDevices:
            if device['role'] == 'slave':
                slaves.append(device['udid'])
        return slaves

    def addProcess(self,process):
        self.process.append(process)

    def isOOM(self):
        for process in self.process:
            Log.show(process.cmdline)

