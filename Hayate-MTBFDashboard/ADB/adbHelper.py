# -*- coding: utf-8 -*-
import sys,os
import time
from subprocess import Popen,PIPE
print os.getcwd()
print sys.argv[0]
print os.path.split( os.path.realpath( sys.argv[0] ) )[0]
sys.path.append(os.path.join(os.path.split( os.path.realpath( sys.argv[0] ) )[0], '..'))
from Sagittarium.CustomException.HandleDeviceExceiton import RootDeviceException
from Sagittarium.CustomException.HandleDeviceExceiton import PullDropboxFilesException
from Sagittarium.CustomException.HandleDeviceExceiton import PullLogcatFilesException
from Sagittarium.Log.LogHelper import Logger

class ADB():

    def __init__(self):
        pass

    def __executeCommand(self,command):
        process = Popen(command,stdout=PIPE,stderr=PIPE)
        (stdoutPut,stderrPut) = process.communicate()
        if process.returncode == 1:
            return (False,stderrPut)
        elif process.returncode == 0:
            return (True,stdoutPut)
        else:
            return (False,'Unknown status')

    def pullDropboxFiles(self,devices,mtbfDashboardPath):
        Logger.info('Start pull dropbox files on devices')
        for device in devices:
            Logger.info("Start pull dropbox files on device {id}".format(id=device.id))
            if not device.mappingid == "None":
                Logger.debug("Device {id} has mappingid {mappingid}.So use mappingid name folder".format(id=device.id,mappingid=device.mappingid))
                deviceDropboxPath = os.path.join(mtbfDashboardPath,'dropbox',device.mappingid)
            else:
                Logger.debug("Device {id} has no mappingid {mappingid}.So use id name folder".format(id=device.id,mappingid=device.mappingid))
                deviceDropboxPath = os.path.join(mtbfDashboardPath,'dropbox',device.id)
            if not os.path.exists(deviceDropboxPath):
                os.makedirs(deviceDropboxPath)
            device.setLocalDropboxPath(deviceDropboxPath)
            self.__pullDropboxFiles(device,deviceDropboxPath)

    def pullLogcatFiles(self,devices,mtbfDashboardPathd):
        Logger.info("Start pull logcat on devices")
        for device in devices:
            if not device.mappingid == "None":
                deviceLogcatPath = os.path.join(mtbfDashboardPathd,'logcat',device.mappingid)
            else:
                deviceLogcatPath = os.path.join(mtbfDashboardPathd,'logcat',device.id)

            if not os.path.exists(deviceLogcatPath):
                os.makedirs(deviceLogcatPath)
            device.setLocalLogcatPath(deviceLogcatPath)
            self.__pullLogcatFiles(device,deviceLogcatPath)

    def rootDevices(self,devices):
        for device in devices:
            self.__rootDevice(device)
            self.__remountDevice(device)

    def __pullLogcatFiles(self,device,path):
        useMappingId = False
        if not device.mappingid == "None":
            useMappingId = True
        else:
            useMappingId = False
        targetLogcatPathOnDevice = '/sdcard/MTBF' if device.logStorePath == "Default" else device.logStorePath + "/MTBF"
        remotePath = None
        lsCommand = ('adb','-s',device.id,'ls',targetLogcatPathOnDevice)
        response = self.__executeCommand(lsCommand)
        if not response[0]:
            raise PullLogcatFilesException(id=device.id,error=str(response[1]))
        lines = response[1].split('\r\n')
        while '' in lines:
            lines.remove('')
        for line in lines:
            Logger.debug(line)
            if (device.mappingid if useMappingId else device.id) in line:
                items = line.split(' ')
                for item in items:
                    if (device.mappingid if useMappingId else device.id) in item:
                        remotePath = targetLogcatPathOnDevice + '/' + item.replace('\r\n','')
        if remotePath == None:
            raise  PullLogcatFilesException(id=device.id,error='Find device {id} logcat folder on device fail.'.format(id=device.id))
        pullCommand = ('adb','-s',device.id,'pull',remotePath,path)
        response = self.__executeCommand(pullCommand)
        if not response[0]:
            raise PullLogcatFilesException(id=device.id,error=str(response[1]))
        else:
            Logger.info('Pull logcat to device {id} OK.'.format(id=device.id))

    def __pullDropboxFiles(self,device,path):
        command = ('adb','-s',device.id,'pull','/data/system/dropbox/',path)
        response = self.__executeCommand(command)
        if not response[0]:
            raise PullDropboxFilesException(id=device.id,error=str(response[1]))
        else:
            Logger.info('Pull dropbox files to local on device {id} OK'.format(id=device.id))

    def __rootDevice(self,device):
        command = ('adb','-s' ,device.id ,'root')
        response = self.__executeCommand(command)
        if not response[0]:
            raise RootDeviceException(id=device.id,error=str(response[1]))
        else:
            Logger.info('Root device {id} OK'.format(id=device.id))

    def __remountDevice(self,device):
        time.sleep(5)
        command = ('adb','-s',device.id,'remount')
        response = self.__executeCommand(command)
        if not response[0]:
            print 'Remount device {id} fail.\n{error}'.format(id=device.id,error=str(response[1]))
            sys.exit()
        else:
            print 'Remount device {id} OK.'.format(id=device.id)

    # def getConnectedDevices(self):
    #     devices = []
    #     command = ('adb','devices')
    #     response = self.__executeCommand(command)
    #     if not response[0]:
    #         print 'Get connected android devices fail.\n{error}'.format(error=response[1])
    #         sys.exit()
    #     else:
    #         lines = response[1].split('\r\n')
    #         while '' in lines:
    #             lines.remove('')
    #         for eachLine in lines:
    #             temp_pattern = re.compile(RegularString.DEVICE_ID_STR)
    #             match = temp_pattern.match(eachLine)
    #             if match:
    #                 deviceID = match.group(1)
    #                 temp_device = AndroidDevice(udid=deviceID)
    #                 devices.append(temp_device)
    #     if len(devices) == 0:
    #         print 'No android device connected to PC.'
    #         sys.exit();
    #     else:
    #         for device in devices:
    #             print 'Find connected device:{id}'.format(id=device.id)
    #     return devices


if __name__ == '__main__':
    pass





