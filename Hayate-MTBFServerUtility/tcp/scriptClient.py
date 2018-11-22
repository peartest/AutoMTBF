# -*- coding: utf-8 -*-

import os
import threading
import json
import time
from XMLHelper.xmlWriter import XMLWriter
import Config
import yaml


class Client(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self);
        self.connect = None
        self.reportPath = None;
        self.report = None
        self.device = None
        self.isScriptPass = True
        self.isAppend = False;
        self.currentRecordPath = None

    def setDevice(self, device=None):
        self.device = device

    def setConnectSocket(self, socket=None):
        self.connect = socket

    def setReportPath(self, reportPath=None):
        self.reportPath = reportPath

    def run(self):
        self.master = self.device.getMasterDeviceID()
        self.slaves = self.device.getSlaveDeviceID()
        # try:
        while True:
            data = self.connect.recv(1024)
            if data == '' or data == None:
                pass
            else:
                # print data
                # data = json.dumps(data)
                print data
                message_from_client = json.loads(data)
                print 'Get json data from script:{data}'.format(data=message_from_client)
                isScriptEnd = self.handleMessage(message=message_from_client)
                if isScriptEnd:
                    # 生成记录文件
                    if self.isAppend:
                        self.xmlHandler.saveRecord()
                    else:
                        self.xmlHandler.generateRecord(recordPath=self.currentRecordPath)
                        break
                        # if isScriptEnd :
                        # # Write Pass rate
                        # if self.isScriptPass:
                        # self.report.writePRInfo(data={'script':message_from_client['script'],'result':True})
                        #     else:
                        #         self.report.writePRInfo(data={'script':message_from_client['script'],'result':False})
                        #     break;
                        # except BaseException,e:
                        #     print 'Error:{error}'.format(error=str(e))
                        # finally:
                        #     print 'Close socket connecting'
                        #     self.connect.close()

    def __handleScriptStart(self, scriptStartMessage):
        self.currentRecordPath = os.path.join(self.reportPath,
                                              scriptStartMessage['mtbfWholeTestFolder'],
                                              scriptStartMessage['mtbfRoundFolder'],
                                              scriptStartMessage['mtbfTestCaseName'],
                                              'Time[{time}]_Loop[{loop}]'.format(
                                                  time=scriptStartMessage['mtbfTestCaseStartTime'],
                                                  loop=scriptStartMessage['mtbfTestCaseCurrentLoop']))
        print 'Current RecordPath:' + str(self.currentRecordPath)
        # 判断Record文件是否存在，如果存在追加记录，如果不存在创建目录，重新添加记录
        if not os.path.exists(self.currentRecordPath):
            # 不存在
            self.isAppend = False
            os.makedirs(self.currentRecordPath);
            self.xmlHandler = XMLWriter(isAppend=self.isAppend, udid=str(scriptStartMessage['udid']),
                                        mappingudid=str(scriptStartMessage['mappingudid']));
            self.xmlHandler.handleScriptStart(scriptName=scriptStartMessage['mtbfTestCaseName'],
                                              scriptStartTime=scriptStartMessage['mtbfTestCaseStartTime'],
                                              scriptCurrentLoop=scriptStartMessage['mtbfTestCaseCurrentLoop'],
                                              scriptRoundFolder=scriptStartMessage['mtbfRoundFolder'])
        else:
            # 存在
            self.isAppend = True
            self.xmlHandler = XMLWriter(isAppend=self.isAppend,
                                        recordFilePath=os.path.join(self.currentRecordPath, 'Record.xml'))

    def __handleScriptEnd(self, message):
        if self.isAppend:
            self.xmlHandler.handleAppendScriptEnd(scriptEndTime=str(message['endTime']),
                                                  scriptResult='OK' if self.isScriptPass else 'Fail')
        else:
            self.xmlHandler.handleScriptEnd(scriptEndTime=str(message['endTime']),
                                            scriptResult='OK' if self.isScriptPass else 'Fail')

    def __handleScriptExecute(self, message):
        stepContent = message['step'];
        stepResult = message['result'];
        relatedDevice = message['udid']
        if not stepResult:
            if 'ignore_error' in message:
                if not message['ignore_error']:
                    self.isScriptPass = False
                    self.xmlHandler.handleAppendedErrorInfo(error=str(message['error'])) if self.isAppend else self.xmlHandler.handleErrorInfo(error=str(message['error']))

        if self.isAppend:
            self.xmlHandler.handleAppendScriptExecute(stepContent=stepContent, stepResult=stepResult,relatedDevice=relatedDevice)
        else:
            self.xmlHandler.handleScriptExecute(stepContent=stepContent, stepResult=stepResult,relatedDevice=relatedDevice)


    def handleMessage(self, message=None):
        type = message['type']
        deviceID = message['udid']
        if type == 'step':
            step = message['step']
            if step == 'script_start':
                # 处理脚本开始测试相关信息
                self.__handleScriptStart(message)
            elif step == 'script_end':
                # 写入当前脚本结束测试相关信息
                self.__handleScriptEnd(message)
                return True
        elif type == 'result':
            # 处理脚本执行过程
            self.__handleScriptExecute(message)
        elif type == 'scriptOKResult':
            # 写入脚本当前测试结果正确信息
            self.isScriptPass = True
            self.xmlHandler.handleOKInfo(ok=str(message['info']))
        return False

    def __closeClient(self):
        self.connect.close();



