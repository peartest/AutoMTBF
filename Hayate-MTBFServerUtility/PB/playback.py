# -*- coding: utf-8 -*-

import time
import os
import subprocess
import threading
import json

class PlaybackScript(threading.Thread):

    def __init__(self,device=None):
        threading.Thread.__init__(self);
        self.device = device
        self.scripts = device.scripts;
        self.model = device.pbModel
        self.id = device.deviceID;
        self.mappingid = device.deviceMappingID
        self.serverPort = device.serverPort
        self.isDriverByTime = device.isDriverByTime
        # 将时间单位转换成秒
        self.testTime = device.value * 60 * 60
        self.startTime = None;

    def run(self):
        currentRound = 1;
        # 完整测试开始时间
        self.startTime = time.localtime()
        # 获取此次测试的完整测试文件夹名称
        # wholeTestFolderName = self.__getWholeTestFolerName(value=self.startTime);
        wholeTestFolderName = time.strftime('%Y%m%d%H%M%S',self.startTime)
        if self.model == 'unit':
            if self.isDriverByTime:
                while True:
                    # 获取当前测试Round的文件夹名称
                    currentRoundFolderName = self.__getRoundTestFolderName(round=currentRound)
                    if self.__unit_loop(wholeTestFolderName=wholeTestFolderName,roundFolderName=currentRoundFolderName):
                        break
                    currentRound = currentRound + 1;
            else:
                # 获取当前测试Round的文件夹名称
                currentRoundFolderName = self.__getRoundTestFolderName(round=currentRound)
                self.__unit_loop(wholeTestFolderName=wholeTestFolderName,roundFolderName=currentRoundFolderName)
        else:
            if self.isDriverByTime:
                while True:
                    # 获取当前测试Round的文件夹名称
                    currentRoundFolderName = self.__getRoundTestFolderName(round=currentRound)
                    if self.__suit_loop(wholeTestFolderName=wholeTestFolderName,roundFolderName=currentRoundFolderName):
                        break
                    currentRound = currentRound + 1;
            else:
                # 获取当前测试Round的文件夹名称
                currentRoundFolderName = self.__getRoundTestFolderName(round=currentRound)
                self.__suit_loop(wholeTestFolderName=wholeTestFolderName,roundFolderName=currentRoundFolderName)

    def playbackScript(self):
        self.startTime = time.time()
        print 'start time {startTime}'.format(startTime=self.startTime)
        if self.model == 'unit':
            if self.isDriverByTime:
                while True:
                    if self.__unit_loop():
                        break
            else:
                self.__unit_loop()
        else:
            if self.isDriverByTime:
                while True:
                    if self.__suit_loop():
                        break
            else:
                self.__suit_loop()

    def exe_commmand(self,command):
        os.system(command)

    def __unit_loop(self,wholeTestFolderName=None,roundFolderName=None):
        print 'Unit loop start'
        # 重置所有脚本的测试次数
        self.resetAllScriptsLessLoop()
        # 依次回放每个脚本
        for script in self.scripts:
            currentScriptLoop = script.scriptLessLoopCount
            # 依次将当前脚本的所有执行次数执行完毕
            for i in xrange(1,currentScriptLoop+1):
                # 每个脚本开始时，都需要检查测试时间
                if self.isDriverByTime and self.__checkOverTime():return True
                self.__playbackScript(currentScript=script,
                                      currentScriptLoop=i,
                                      currentWholeTestFolder=wholeTestFolderName,
                                      currentRoundFolder=roundFolderName)
                print 'Device {device} playback script {script} loop {loop} finish'.format(device=self.id if script.scriptReliantDevice == "MASTER" else script.scriptReliantDevice,
                                                                                           script=script.scriptPath,
                                                                                           loop=i)
        # 当所有脚本都执行完后，进行时间判断，如果时间没有达到返回False，又继续从头开始
        # 如果时间满足了总测试时间，则停止测试
        return True if self.isDriverByTime and self.__checkOverTime() else False

    def __suit_loop(self,wholeTestFolderName=None,roundFolderName=None):
        print 'Suit loop start'
        # 重置所有脚本的次数
        self.resetAllScriptsLessLoop()
        maxLoop = self.__getMaxLoop()
        # 在Suit模式下，以所有脚本中的最大Loop次数为上限进行循环。
        for i in xrange(1,maxLoop+1):
            for script in self.scripts:
                # 当前脚本在当前这一轮中的次数是否已经为0，如果为0就不进行回放，如果大于0就继续回放
                if script.scriptLessLoopCount > 0:
                    # 检测是否达到总测试时间
                    if self.isDriverByTime and self.__checkOverTime():return True
                    # 当前脚本开启测试的时间
                    self.__playbackScript(currentScript=script,
                                          currentScriptLoop=i,
                                          currentWholeTestFolder=wholeTestFolderName,
                                          currentRoundFolder=roundFolderName)
                    # 当前脚本剩余测试次数减1
                    script.scriptLessLoopCount = script.scriptLessLoopCount - 1
                    print 'Playback script {script} loop {loop} finish'.format(script=script.scriptPath,loop=i)
                else:
                    print '{script} loop count is 0.Do not need to test again in current suit'

        # 当前suit中所有脚本的所有测试次数都测试完成后，进行时间判断，如果时间没有达到返回Fasle,达到返回True
        return True if self.isDriverByTime and self.__checkOverTime() else False

    def __playbackScript(self,currentScript=None,currentScriptLoop=None,currentWholeTestFolder=None,currentRoundFolder=None):
        """
        回放特定脚本,只负责执行，不进行流程控制和脚本对象相关属性的改变
        :return:
        """
        runParams = {}
        runParams['scriptPath'] = currentScript.scriptPath;
        runParams['currentLoop'] = currentScriptLoop
        runParams['serverPort'] = self.serverPort
        runParams['tcp'] = self.device.tcpPort
        runParams['roundFolder'] = currentRoundFolder
        runParams['scriptName'] = currentScript.scriptName
        runParams['wholeTestFolderSuffix'] = currentWholeTestFolder

        deviceParams = {}
        deviceParams['udid'] = self.device.deviceID
        deviceParams['mappingid']=self.device.deviceMappingID
        deviceParams['logStorePath']=self.device.mtbfLogStorePath

        supportDeviceParams = self.__getSupportDevicesDict()

        command = 'python {scriptPath} {runParams} {deviceParams} {supportDeviceParams}'.format(scriptPath = currentScript.scriptPath,
                                                                                   runParams=json.dumps(runParams,separators=(',',':')),
                                                                                   deviceParams=json.dumps(deviceParams,separators=(',',':')),
                                                                                   supportDeviceParams=json.dumps(supportDeviceParams,separators=(',',':')))

        # command = 'python {scriptPath} {currentLoop} {wholeTestFolder} {deviceId} {serverPort} {supportDeviceID} {tcp} {roundFolder} {scriptName} {deviceMappingId} {logStorePath} {supportDevices}'\
        #                 .format(scriptPath=currentScript.scriptPath,
        #                         currentLoop=currentScriptLoop,
        #                         wholeTestFolder=currentWholeTestFolder,
        #                         deviceId=self.id,
        #                         serverPort=self.serverPort,
        #                         supportDeviceID='X',
        #                         tcp=self.device.tcpPort,
        #                         roundFolder=currentRoundFolder,
        #                         scriptName=currentScript.scriptName,
        #                         deviceMappingId = self.mappingid,
        #                         logStorePath = self.device.mtbfLogStorePath,
        #                         supportDevices = json.dumps(self.__getSupportDevicesDict(),separators=(',',':')))
        print 'Playback command {command}'.format(command=command)
        popen = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        while True:
            out_line = popen.stdout.readline()
            if out_line == '' and popen.poll() != None:
                break
            else:
                print out_line

    def __checkOverTime(self):
        """
        检查是否超时，如果超时返回True，测试停止，如果不超时测试继续.
        :return:
        """
        currentTime = time.time()
        if currentTime - time.mktime(self.startTime) >= self.testTime:
            print 'Test Finish.Time reach'
            return True
        else:
            print 'Test continue.Time not reach'
            return False

    def __getMaxLoop(self):
        differentlLoop = []
        for script in self.scripts:
            if not (script.scriptLoopCount in differentlLoop):
                differentlLoop.append(script.scriptLoopCount)
        return max(differentlLoop)

    def resetAllScriptsLessLoop(self):
        for script in self.scripts:
            script.resetLessLoopCount();

    # def makeTestReportFolderForSingleLoop(self):
    #     reportName = 'report.{time}'.format(time=time.strftime('%Y%m%d_%H%M%S',time.localtime()))
    #     reportFolderPath = os.path.join(os.path.dirname(self.scripts[0].scriptPath),reportName);
    #     if not os.path.exists(reportFolderPath):
    #         os.makedirs(reportFolderPath)
    #     return reportFolderPath

    def __getWholeTestFolerName(self,value=None):
        if not self.mappingid == "None":
            folderName = '{id}.{time}'.format(id= self.mappingid,time=time.strftime('%Y%m%d%H%M%S',value))
        else:
            folderName = '{id}.{time}'.format(id= self.id,time=time.strftime('%Y%m%d%H%M%S',value))
        return folderName

    def __getRoundTestFolderName(self,round=0):
        folderName = 'Round_{round}'.format(round=round)
        return folderName;

    def __getSupportDevicesDict(self):
        supportDevices = []
        for supportDevice in self.device.supportDevices:
            supportDevices.append({'udid':supportDevice.udid,
                                   'mappingid':supportDevice.mappingid,
                                   'logStorePath':supportDevice.logStorePath})

        return supportDevices;


