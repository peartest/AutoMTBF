# -*- coding: utf-8 -*-

import xml.dom.minidom
import os
import sys
sys.path.append('../')
import Config
from AndroidDevice.device import Device
from AndroidScript.script import Script
from AndroidDevice.supportDevice import SupportDevice
from CustomException.ConfigErrorException import DeviceTagNotExistException
from CustomException.ConfigErrorException import DeviceAttributeIsNotValid
from CustomException.ConfigErrorException import SupportDeviceAtrributeIsNotValid
class Parser():

    def __init__(self):
        pass

    def getDevice(self,deviceID=None):
        device = None
        dom = xml.dom.minidom.parse(Config.CONFIG_XML_FILE)
        root = dom.documentElement
        deviceNodes = root.getElementsByTagName(Config.CONFIG_XML_TAG_DEVICE)
        for i in xrange(0,len(deviceNodes)):
            id = deviceNodes[i].getAttribute(Config.CONFIG_XML_TAG_UDID)
            if id == deviceID:
                port = int(deviceNodes[i].getAttribute(Config.CONFIG_XML_TAG_PORT))
                tcpPort = int(deviceNodes[i].getAttribute(Config.CONFIG_XML_TAG_TCP))
                device = Device()
                driverByTime = False
                if deviceNodes[i].getAttribute(Config.CONFIG_XML_TAG_DRIVER) == 'true':
                    driverByTime = True
                model = deviceNodes[i].getAttribute(Config.CONFIG_XML_TAG_MODEL)
                time = float(deviceNodes[i].getAttribute(Config.CONFIG_XML_TAG_TIME))
                bootstrapPort = int(deviceNodes[i].getAttribute(Config.CONFIG_XML_TAG_BOOTSTRAPPORT))
                # Get scripts and values
                scriptsList = self.__getScripts(node=deviceNodes[i])
                device.setDeviceScripts(scriptsList=scriptsList)
                # device.setDeviceValues(id=id,port=port,driverByTime=driverByTime,model=model,time=time,bootstrapPort=bootstrapPort)
                device.setTcpPort(tcp=tcpPort)
                break
        return device

    def getDevices(self):
        devices = []
        dom = xml.dom.minidom.parse(Config.CONFIG_XML_FILE)
        root = dom.documentElement
        deviceNodes = root.getElementsByTagName(Config.CONFIG_XML_TAG_DEVICE)
        if len(deviceNodes) == 0:
            raise DeviceTagNotExistException()
        # 遍历所有设备节点
        for i in xrange(0,len(deviceNodes)):
            # 获取设备id
            id = deviceNodes[i].getAttribute(Config.CONFIG_XML_TAG_UDID)
            if id == "" or id == None:
                raise DeviceAttributeIsNotValid("id")
            # 获取设备映射id,如果没有对应属性，这自动设置为""
            mappingid = deviceNodes[i].getAttribute(Config.CONFIG_XML_TAG_MAPPINGID)
            if mappingid == "" or mappingid == None:
                raise DeviceAttributeIsNotValid("mappingid")
            # 获取设备存储log的路径，设备上面的路径,如果没有自动设置为""
            logStorePath = deviceNodes[i].getAttribute(Config.CONFIG_XML_TAG_LOGSTOREPATH)
            if logStorePath == "" or logStorePath == None:
                raise DeviceAttributeIsNotValid("logStorePath")
            # 获取需要连接的Server 端口
            port = int(deviceNodes[i].getAttribute(Config.CONFIG_XML_TAG_PORT))
            # 获取TCP 端口
            tcpPort = int(deviceNodes[i].getAttribute(Config.CONFIG_XML_TAG_TCP))
            # 获取测试是否被时间驱动
            driverByTime = False
            if deviceNodes[i].getAttribute(Config.CONFIG_XML_TAG_DRIVER) == 'true':
                driverByTime = True
            # 获取测试模式
            model = deviceNodes[i].getAttribute(Config.CONFIG_XML_TAG_MODEL)
            # 获取测试时间
            time = float(deviceNodes[i].getAttribute(Config.CONFIG_XML_TAG_TIME))
            # 获取连接bootstrap的端口
            bootstrapPort = int(deviceNodes[i].getAttribute(Config.CONFIG_XML_TAG_BOOTSTRAPPORT))
            # 获取当前设备所对应的所有脚本
            scriptsList = self.__getScripts(node=deviceNodes[i])
            # 获取当前设备依赖的所有辅助设备（可理解为与当前设备会发生交互的设备）,并定义设备的角色
            # reliantDevices = self.__getCurrentReliantDevices(scriptsList,masterDeviceID=id)
            # 获取当前设备依赖的设备
            supportDevices = self.__getSupportDevice(node=deviceNodes[i])

            device = Device()
            # 设置设备编号
            device.setDeviceID(id=id)
            # 设置设备映射编号
            device.setDeviceMappingID(mappingid=mappingid)
            # 设置log在设备上面的存储位置
            device.setMtbfLogStorePath(path=logStorePath)
            # 设置服务器端口
            device.setServerPort(port=port)
            # 设置Tcp端口
            device.setTcpPort(tcp=tcpPort)
            # 设置是否测试以时间驱动
            device.setDriverByTime(driverByTime=driverByTime)
            # 设置回放模式
            device.setPlaybackModel(model=model)
            # 设置测试时间
            device.setTestTime(time=time)
            # 设置设备端的Bootstrap 端口
            device.setBootstrapPort(bootstrapPort=bootstrapPort)
            # 设置当前设备的所有脚本（包括会在辅助机上面执行的脚本）
            device.setDeviceScripts(scriptsList=scriptsList)
            # 设置当前设备需要的辅助机列表
            # device.setReliantDevices(reliantDevices=reliantDevices)
            # 设置当前设备需要依赖的设备
            device.setSupportDevices(supportDevices=supportDevices)
            devices.append(device)
        return devices

    def __getCurrentReliantDevices(self,scripts=None,masterDeviceID=None):
        reliantDevices=[]
        for script in scripts:
            if not (script.scriptReliantDevice in reliantDevices):
                reliantDevices.append({'udid':masterDeviceID if script.scriptReliantDevice == 'MASTER' else script.scriptReliantDevice
                                      ,'role':'master' if script.scriptReliantDevice == 'MASTER' else 'slave'})
        return reliantDevices

    def __getSupportDevice(self,node=None):
        supportDevices=[]
        supportDevicesNode = node.getElementsByTagName(Config.CONFIG_XML_TAG_SUPPORTDEVICES)
        if len(supportDevicesNode) == 0:
            return supportDevices
        else:
            supportDeviceNodes = supportDevicesNode[0].getElementsByTagName(Config.CONFIG_XML_TAG_SUPPORTDEVICE)
            if len(supportDeviceNodes) == 0:
                return supportDevices
            for supportDevice in supportDeviceNodes:
                id = supportDevice.getAttribute(Config.CONFIG_XML_TAG_UDID)
                if id == "" or id == None:
                    raise SupportDeviceAtrributeIsNotValid("id")
                mappingid = supportDevice.getAttribute(Config.CONFIG_XML_TAG_MAPPINGID)
                if mappingid == "" or mappingid == None:
                    raise SupportDeviceAtrributeIsNotValid("mappingid")
                logStorePath = supportDevice.getAttribute(Config.CONFIG_XML_TAG_LOGSTOREPATH)
                if logStorePath == "" or logStorePath == None:
                    raise SupportDeviceAtrributeIsNotValid("logStorePath")
                currentSupportDevice = SupportDevice()
                # 设置依赖设备的id
                currentSupportDevice.setUdid(value=id)
                currentSupportDevice.setMappingId(value=mappingid)
                currentSupportDevice.setLogStorePath(value=logStorePath)
                supportDevices.append(currentSupportDevice)
            return supportDevices


    def __getScripts(self,node=None):
        scripts = []
        scriptsNode = node.getElementsByTagName(Config.CONFIG_XML_TAG_SCRIPTS)
        scriptNodes = scriptsNode[0].getElementsByTagName(Config.CONFIG_XML_TAG_SCRIPT)
        for script in scriptNodes:
            scriptPath = script.getAttribute(Config.CONFIG_XML_TAG_PATH)
            scriptName = os.path.basename(scriptPath)
            scriptLoop = script.getAttribute(Config.CONFIG_XML_TAG_LOOP)
            scriptReliantDevice = script.getAttribute(Config.CONFIG_XML_TAG_RELIANTDEVICE)
            currentScript = Script()
            # 设置脚本的名字
            currentScript.setScriptName(name=scriptName)
            # 设置脚本的路径
            currentScript.setScriptPath(path=scriptPath)
            # 设置脚本的循环次数
            currentScript.setScriptLoop(loop=int(scriptLoop))
            # 设置脚本所依赖的设备
            currentScript.setReliantDevice(reliantDevice=scriptReliantDevice)
            scripts.append(currentScript)
        return scripts

if __name__ == '__main__':
    parser = Parser()
    devices = parser.getDevices()
    for i in xrange(0,len(devices)):
        print devices[i].deviceID
        print devices[i].serverPort
        print devices[i].isDriverByTime
        print devices[i].pbModel
        print devices[i].value