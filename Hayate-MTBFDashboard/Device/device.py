# -*- coding: utf-8 -*-
from __future__ import division
__author__ = '赵嘉俊'

import os
import re
from XML.xmlHelper import XmlParse
import sys
from Device.Script.Script import AndroidScript
from Device.Script.TestCase import AndroidTestCase
import Regular.Regular as DropboxRegular
import Device.Error.ErrorType as DropboxType
from Device.Error.Wtf import AndroidWtf
from Device.Error.StrictModeViolation import AndroidStrictModeViolation
from Device.Error.Crash import AndroidCrash
from Device.Error.Anr import AndroidANR
from Device.Error.Lowmem import AndroidLowmem
from Device.Error.SystemRestart import AndroidSystemRestart
from Device.Error.Tombstones import AndroidTombstones
from Device.Error.Watchdog import AndroidWatchdog
import time

class AndroidDevice():

    def __init__(self):
        # 设备属性
        self.id = None
        self.mappingid = None
        self.logStorePath = None
        self.supportDevices = None

        # 测试数据
        self.local_dropbox_path = None
        self.local_logcat_path = None
        self.local_record_path = None
        self.testcaseHtmlPath = None
        self.testcase = []
        self.passTestcase = []
        self.failTestcase = []
        self.testcaseCount = 0;
        self.crash = []
        self.crashCount = 0
        self.anr = []
        self.anrCount = 0
        self.lowmem = []
        self.lowmemCount = 0
        self.smv = []
        self.smvCount = 0
        self.systemRestart = []
        self.systemRestartCount = 0
        self.tombstones = []
        self.tombstonesCount = 0
        self.watchdog = []
        self.watchdogCount = 0
        self.wtf = []
        self.wtfCount = 0
        self.totalTestTime = 0
        self.totalTestTimes = 0
        self.passrate = None
        self.testStartTime = None
        self.passTestCaseCount = 0;
        self.failTestCaseCount = 0;
        self.xmlParse = XmlParse()

    def setUdid(self,value):
        self.id = value

    def setMappingId(self,value):
        self.mappingid = value

    def setLogStorePath(self,value):
        self.logStorePath = value

    def setSupportDevices(self,value):
        self.supportDevices = value

    def setTestcaseHtmlPath(self,path):
        self.testcaseHtmlPath = os.path.basename(path)

    def setTestcaseListHtmlPath(self,path):
        self.testcaseListHtmlPath = os.path.basename(path)

    def setAnrHtmlPath(self,value):
        self.anrHtmlPath = os.path.basename(value)

    def setCrashHtmlPath(self,value):
        self.crashHtmlPath = os.path.basename(value)

    def setLowMemHtmlPath(self,value):
        self.lowmemHtmlPath = os.path.basename(value)

    def setSMVHtmlPath(self,value):
        self.smvHtmlPath = os.path.basename(value)

    def setSystemRestartHtmlPath(self,value):
        self.systemRestartHtmlPath = os.path.basename(value)

    def setTombstonesHtmlPath(self,value):
        self.tombstonesHtmlPath = os.path.basename(value)

    def setWatchdogHtmlPath(self,value):
        self.watchdogHtmlPath = os.path.basename(value)

    def setWtfHtmlPath(self,value):
        self.wtfHtmlPath = os.path.basename(value)

    def setLocalDropboxPath(self,path):
        self.local_dropbox_path = path

    def setLocalLogcatPath(self,path):
        self.local_logcat_path = path

    def setLocalRecordPath(self,path):
        self.local_record_path = path

    def parseData(self):
        # 解析测试用例,生成AndroidScript,AndroidTestcase对象
        self.__parseTestcase()
        self.testcaseCount = len(self.testcase)
        # 计算AndroidTestcase数据
        for testcase in self.testcase:
            testcase.calculateData()
        for testcase in self.testcase:
            # 计算当前设备总测试时间
            self.totalTestTime = self.totalTestTime + testcase.totleExecuteTime
            # 计算当前设备的总pass rate
            self.totalTestTimes = self.totalTestTimes + testcase.totalExecuteTimes
            if testcase.isPass:
                self.passTestCaseCount = self.passTestCaseCount + 1
                self.passTestcase.append(testcase)
            else:
                self.failTestCaseCount = self.failTestCaseCount + 1
                self.failTestcase.append(testcase)
        self.passrate = '%.2f%%'%(self.passTestCaseCount/len(self.testcase)*100)

    def parseError(self):
        # 检索Dropbox中的所有错误
        dropboxFiles = os.listdir(self.local_dropbox_path)
        for file in dropboxFiles:
            self.__parseDroboxFile(file,self.local_dropbox_path)
        self.crashCount = len(self.crash)
        self.anrCount = len(self.anr)
        self.lowmemCount = len(self.lowmem)
        self.smvCount = len(self.smv)
        self.systemRestartCount = len(self.systemRestart)
        self.tombstonesCount = len(self.tombstones)
        self.watchdogCount = len(self.watchdog)
        self.wtfCount = len(self.wtf)

    def __transferTime(self,value):
        happen_time = int(value)
        happen_time = time.strftime('%Y%m%d%H%M%S',time.localtime(float('%.3f'%(happen_time/1000))))
        return happen_time

    def __findLogcatForError(self,happenTime):
        if len(self.testcase) <= 0:
            print 'Device {id} find logcat for error fail, because of device has no testcase record.'.format(id=self.id)
            sys.exit()
        for tc in self.testcase:
            for script in tc.scripts:
                isTargetScript = self.__checkIsTargetScript(script.startTime,script.endTime,happenTime)
                if isTargetScript:
                    return os.path.join('logcat',
                                        self.mappingid if not self.mappingid == "None" else self.id,
                                        script.round,
                                        script.name,
                                        script.logFolder)
        return None

    def __checkIsTargetScript(self,scriptStartTime,scriptEndTime,errorHappenTime):
        start = time.strptime(scriptStartTime,"%Y%m%d%H%M%S")
        end = time.strptime(scriptEndTime,"%Y%m%d%H%M%S")
        errorTime = time.strptime(errorHappenTime,"%Y%m%d%H%M%S")
        if (float(time.mktime(errorTime)) >= float(time.mktime(start))) \
                and (float(time.mktime(errorTime)) <= float(time.mktime(end))):
            return True
        return False

    def __parseDroboxFile(self,file,dropboxFolder):
        # 匹配 wtf
        find = re.search(DropboxRegular.DROPBOX_WTF_STR,file)
        if find:
            wtfError = AndroidWtf()
            wtfError.setType(DropboxType.DROPBOX_WTF)
            # wtfError.setDropboxFilePath(os.path.join(dropboxFolder,file))
            wtfError.setDropboxFilePath(os.path.join('dropbox',self.mappingid if not self.mappingid == "None" else self.id,file))
            happenTime = self.__transferTime(find.group(1))
            wtfError.setHappenTime(happenTime)
            logcat = self.__findLogcatForError(happenTime)
            if logcat:
                wtfError.setLogcat(logcat)
            else:
                wtfError.setLogcat('N/A')
            self.wtf.append(wtfError)
        # 匹配 strictmode
        find = re.search(DropboxRegular.DROPBOX_STRICT_STR,file)
        if find:
            smvError = AndroidStrictModeViolation()
            smvError.setType(DropboxType.DROPBOX_STRICT)
            # smvError.setDropboxFilePath(os.path.join(dropboxFolder,file))
            smvError.setDropboxFilePath(os.path.join('dropbox',self.mappingid if not self.mappingid == "None" else self.id,file))
            happenTime = self.__transferTime(find.group(1))
            print happenTime
            smvError.setHappenTime(happenTime)
            logcat = self.__findLogcatForError(happenTime)
            if logcat:
                smvError.setLogcat(logcat)
            else:
                smvError.setLogcat('N/A')
            self.smv.append(smvError)
        # 匹配 app crash
        find = re.search(DropboxRegular.DROPBOX_APP_CRASH_STR,file)
        if find:
            crashError = AndroidCrash()
            crashError.setType(DropboxType.DROPBOX_APP_CRASH)
            # crashError.setDropboxFilePath(os.path.join(dropboxFolder,file))
            crashError.setDropboxFilePath(os.path.join('dropbox',self.mappingid if not self.mappingid == "None" else self.id,file))
            happenTime = self.__transferTime(find.group(1))
            print happenTime
            crashError.setHappenTime(happenTime)
            logcat = self.__findLogcatForError(happenTime)
            if logcat:
                crashError.setLogcat(logcat)
            else:
                crashError.setLogcat('N/A')
            self.crash.append(crashError)
        # 匹配 anr
        find = re.search(DropboxRegular.DROPBOX_ANR_STR,file)
        if find:
            anrError = AndroidANR()
            anrError.setType(DropboxType.DROPBOX_ANR)
            # anrError.setDropboxFilePath(os.path.join(dropboxFolder,file))
            anrError.setDropboxFilePath(os.path.join('dropbox',self.mappingid if not self.mappingid == "None" else self.id,file))
            happenTime = self.__transferTime(find.group(1))
            print happenTime
            anrError.setHappenTime(happenTime)
            logcat = self.__findLogcatForError(happenTime)
            if logcat:
                anrError.setLogcat(logcat)
            else:
                anrError.setLogcat('N/A')
            self.anr.append(anrError)
        # 匹配 lowmen
        find = re.search(DropboxRegular.DROPBOX_LOWMEM,file)
        if find:
            lowmemError = AndroidLowmem()
            lowmemError.setType(DropboxType.DROPBOX_LOWMEM)
            # lowmemError.setDropboxFilePath(os.path.join(dropboxFolder,file))
            lowmemError.setDropboxFilePath(os.path.join('dropbox',self.mappingid if not self.mappingid == "None" else self.id,file))
            happenTime = self.__transferTime(find.group(1))
            print happenTime
            lowmemError.setHappenTime(happenTime)
            logcat = self.__findLogcatForError(happenTime)
            if logcat:
                lowmemError.setLogcat(logcat)
            else:
                lowmemError.setLogcat('N/A')
            self.lowmem.append(lowmemError)
        # 匹配 tombstones
        find = re.search(DropboxRegular.DROPBOX_TOMBSTONES,file)
        if find:
            tombstonesError = AndroidTombstones()
            tombstonesError.setType(DropboxType.DROPBOX_TOMBSTONES)
            # tombstonesError.setDropboxFilePath(os.path.join(dropboxFolder,file))
            tombstonesError.setDropboxFilePath(os.path.join('dropbox',self.mappingid if not self.mappingid == "None" else self.id,file))
            happenTime = self.__transferTime(find.group(1))
            print happenTime
            tombstonesError.setHappenTime(happenTime)
            logcat = self.__findLogcatForError(happenTime)
            if logcat:
                tombstonesError.setLogcat(logcat)
            else:
                tombstonesError.setLogcat('N/A')
            self.tombstones.append(tombstonesError)
        # 匹配 Watchdog
        find = re.search(DropboxRegular.DROPBOX_WATCHDOG,file)
        if find:
            watchdogError = AndroidWatchdog()
            watchdogError.setType(DropboxType.DROPBOX_WATCHDOG)
            # watchdogError.setDropboxFilePath(os.path.join(dropboxFolder,file))
            watchdogError.setDropboxFilePath(os.path.join('dropbox',self.mappingid if not self.mappingid == "None" else self.id,file))
            happenTime = self.__transferTime(find.group(1))
            print happenTime
            watchdogError.setHappenTime(happenTime)
            logcat = self.__findLogcatForError(happenTime)
            if logcat:
                watchdogError.setLogcat(logcat)
            else:
                watchdogError.setLogcat('N/A')
            self.watchdog.append(watchdogError)
        # 匹配 System restart
        find = re.search(DropboxRegular.DROPBOX_SYSTEM_RESTART,file)
        if find:
            systemServerRestartError = AndroidSystemRestart()
            systemServerRestartError.setType(DropboxType.DROPBOX_SYSTEM_RESTART)
            # systemServerRestartError.setDropboxFilePath(os.path.join(dropboxFolder,file))
            systemServerRestartError.setDropboxFilePath(os.path.join('dropbox',self.mappingid if not self.mappingid == "None" else self.id,file))
            happenTime = self.__transferTime(find.group(1))
            print happenTime
            systemServerRestartError.setHappenTime(happenTime)
            logcat = self.__findLogcatForError(happenTime)
            if logcat:
                systemServerRestartError.setLogcat(logcat)
            else:
                systemServerRestartError.setLogcat('N/A')
            self.systemRestart.append(systemServerRestartError)

    def __parseTestcase(self):
        roundFolders = os.listdir(self.local_record_path)
        for roundFolder in roundFolders:
            roundFolderPath = os.path.join(self.local_record_path,roundFolder)
            testCaseFolders = os.listdir(roundFolderPath)
            for testCaseFolder in testCaseFolders:
                testCaseFolderPath = os.path.join(roundFolderPath,testCaseFolder)
                loopFolders = os.listdir(testCaseFolderPath)
                for loopFolder in loopFolders:
                    loopFolderPath = os.path.join(testCaseFolderPath,loopFolder);
                    self.__parseRecordXml(loopFolderPath)

    def __parseRecordXml(self,path):
        recordXmlPath = os.path.join(path,'Record.xml')
        # 注意处理当Record.xml 不存在时应该如何处理，目前方式直接掉过
        # 此处需要详细设计再做修改
        if not os.path.exists(recordXmlPath):
            print 'Record file {path} did not exist.'.format(path=recordXmlPath)
            # sys.exit()
        else:
            self.xmlParse.refresh(recordXmlPath)
            script = self.__createAndroidScript(recordXmlPath)
            # 对比每个脚本的开始时间，得到最早的一个时间做为当前设备的开始时间
            if self.testStartTime == None:
                self.testStartTime = script.startTime
            else:
                tmp_time1 = time.mktime(time.strptime(self.testStartTime,"%Y%m%d%H%M%S"))
                tmp_time2 = time.mktime(time.strptime(script.startTime,"%Y%m%d%H%M%S"))
                if float(tmp_time2) < float(tmp_time1):
                    self.testStartTime = script.startTime
            self.__createAndroidTestcase(script)

    def __createAndroidScript(self,recordFilePath):
        currentScript = AndroidScript();
        currentScript.setRelatedDevice(self.xmlParse.getDeviceID())
        currentScript.setRelatedDeviceMappingId(self.xmlParse.getDeviceMappingId())
        currentScript.setStartTime(self.xmlParse.getScriptStartTime())
        currentScript.setEndTime(self.xmlParse.getScriptEndTime())
        currentScript.setName(self.xmlParse.getCurrentScriptName())
        currentScript.setLoop(self.xmlParse.getCurrentScriptLoop())
        currentScript.setRound(self.xmlParse.getCurrentScriptRound())
        currentScript.setResult(self.xmlParse.getCurrentScriptResult())
        currentScript.setLogFolder(self.xmlParse.getCurrentScriptLogFolderName())
        currentScript.setOKInfo(self.xmlParse.getCurrentScriptOKInfo())
        currentScript.setErrorInfo(self.xmlParse.getCurrentScriptErrorInfo())
        currentScript.setSteps(self.xmlParse.getCurrentScriptSteps())
        currentScript.generateRecordFilePath()
        currentScript.generateLogcatPath()
        return currentScript

    def __createAndroidTestcase(self,script):
        testcaseExist = False
        scriptName = script.name
        for tc in self.testcase:
            if tc.name == scriptName:
                testcaseExist = True
                tc.addScript(script)
                break
        if not testcaseExist:
            testcase = AndroidTestCase()
            testcase.addScript(script)
            testcase.setName(script.name)
            self.testcase.append(testcase)


if __name__ == '__main__':
    # from shutil import copytree
    # copytree(os.path.join(os.path.dirname(os.path.dirname(__file__)),
    #                       'mtbf_report_templates',
    #                       'css'),'F:\\Git-Local-Automatic-Tools\\Hayate-MTBFDashboard\\20160504173905\\')
    # os.makedirs(r'F:\Git-Local-Automatic-Tools\Hayate-MTBFDashboard\20160504173905')
    # a = [1,2,3]
    # print len(a)
    # device = AndroidDevice()
    # device.setLocalRecordPath(r'F:\Git-Local-Automatic-Tools\Hayate-MTBFDashboard\20160428141329\record\990005270007595')
    # device.parseData()
    # for testcase in device.testcase:
    #     print testcase.name
    #     print testcase.passRate
    #     print testcase.totalExecuteTimes
    #     print testcase.totleExecuteTime
    #     print testcase.passTimes
    #     print testcase.failTimes
    # device.setLocalDropboxPath(r'F:\Git-Local-Automatic-Tools\Hayate-MTBFDashboard\20160428141329\dropbox\990005270007595')
    # device.parseError()
    # import time
    # happen_time = int('1461810667045')
    # happen_time = time.strftime('%Y_%m_%d_%H_%M_%S',time.localtime(float('%.3f'%(happen_time/1000))))
    # print happen_time
    print __file__