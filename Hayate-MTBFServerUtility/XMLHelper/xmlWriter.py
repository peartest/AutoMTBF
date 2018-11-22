# -*- coding: utf-8 -*-

import xml.dom.minidom as xml
import Config
import os

class XMLWriter():

    def __init__(self,isAppend=False,udid=None,mappingudid=None,recordFilePath=None):
        if not isAppend:
            self.implementation = xml.getDOMImplementation()
            self.document = self.implementation.createDocument(None,'Record',None)
            self.rootElement = self.document.documentElement
            self.deviceElement = self.document.createElement(Config.RECORD_XML_TAG_DEVICE)
            self.deviceElement.setAttribute(Config.RECORD_XML_DEVICE_ATTRIBUTE_ID,udid)
            self.deviceElement.setAttribute(Config.RECORD_XML_DEVICE_ATTRUBUTE_MAPPINGID,mappingudid)
            self.setps = [];
        else:
            self.recordFilePath = recordFilePath
            self.document = xml.parse(recordFilePath)
            self.rootElement = self.document.documentElement


    def handleScriptStart(self,scriptName=None,scriptStartTime=None,scriptCurrentLoop=None,scriptRoundFolder=None):
        self.scriptElement = self.document.createElement(Config.RECORD_XML_TAG_SCRIPT)
        self.scriptElement.setAttribute(Config.RECORD_XML_SCRIPT_ATTRIBUTE_NAME,scriptName)
        self.scriptElement.setAttribute(Config.RECORD_XML_SCRIPT_ATTRIBUTE_STARTTIME,scriptStartTime)
        self.scriptElement.setAttribute(Config.RECORD_XML_SCRIPT_ATTRIBUTE_LOOP,scriptCurrentLoop)
        self.scriptElement.setAttribute(Config.RECORD_XML_SCRIPT_ATTRIBUTE_ROUND,scriptRoundFolder)
        self.scriptResultElement = self.document.createElement(Config.RECORD_XML_TAG_SCRIPTRESULT)
        self.scriptLogElement = self.document.createElement(Config.RECORD_XML_TAG_LOG)
        self.scriptLogElement.setAttribute(Config.RECORD_XML_LOG_ATTRIBUTE_FOLDER,'Time[' + scriptStartTime + ']_Loop[' + scriptCurrentLoop + ']')
        self.scriptOKInfoElement = self.document.createElement(Config.RECORD_XML_TAG_OKINFO)
        self.scriptErrorInfoElement = self.document.createElement(Config.RECORD_XML_TAG_ERROR_INFO)

    def handleScriptEnd(self,scriptResult=None,scriptEndTime=None):
        self.scriptElement.setAttribute(Config.RECORD_XML_SCRIPT_ATTRIBUTE_ENDTIME,scriptEndTime)
        self.scriptResultElement.setAttribute(Config.RECORD_XML_SCRIPTRESULT_ATTRIBUTE_VALUE,scriptResult)

    def handleAppendScriptEnd(self,scriptResult=None,scriptEndTime=None):
        scriptElements = self.document.getElementsByTagName(Config.RECORD_XML_TAG_SCRIPT)
        scriptElements[0].setAttribute(Config.RECORD_XML_SCRIPT_ATTRIBUTE_ENDTIME,scriptEndTime)
        resultElemens = self.document.getElementsByTagName(Config.RECORD_XML_TAG_SCRIPTRESULT)
        resultElemens[0].setAttribute(Config.RECORD_XML_SCRIPTRESULT_ATTRIBUTE_VALUE,scriptResult)

    def handleScriptExecute(self,stepContent=None,stepResult=None,relatedDevice=None):
        stepElement = self.document.createElement(Config.RECORD_XML_TAG_SCRIPTSTEP)
        stepElement.setAttribute(Config.RECORD_XML_SCRIPTSTEP_ATTRIBUTE_CONTENT,stepContent)
        stepElement.setAttribute(Config.RECORD_XML_SCRIPTSTEP_ATTRIBUTE_RESULT,str(stepResult))
        stepElement.setAttribute(Config.RECORD_XML_SCRIPTSTEP_ATTRIBUTE_DEVICE,str(relatedDevice))
        self.setps.append(stepElement)

    def handleAppendScriptExecute(self,stepContent=None,stepResult=None,relatedDevice=None):
        scriptElements = self.rootElement.getElementsByTagName(Config.RECORD_XML_TAG_SCRIPT)
        stepElement = self.document.createElement(Config.RECORD_XML_TAG_SCRIPTSTEP)
        stepElement.setAttribute(Config.RECORD_XML_SCRIPTSTEP_ATTRIBUTE_CONTENT,stepContent)
        stepElement.setAttribute(Config.RECORD_XML_SCRIPTSTEP_ATTRIBUTE_RESULT,str(stepResult))
        stepElement.setAttribute(Config.RECORD_XML_SCRIPTSTEP_ATTRIBUTE_DEVICE,str(relatedDevice))
        scriptElements[0].appendChild(stepElement)

    def handleErrorInfo(self,error=None):
        errorInfoNode = self.document.createTextNode(error)
        self.scriptErrorInfoElement.appendChild(errorInfoNode)

    def handleAppendedErrorInfo(self,error=None):
        errorInfoElements = self.rootElement.getElementsByTagName(Config.RECORD_XML_TAG_ERROR_INFO)
        errorInfoNode = self.document.createTextNode(error)
        errorInfoElements[0].appendChild(errorInfoNode)

    def handleOKInfo(self,ok=None):
        okInfoNode = self.document.createTextNode(ok)
        self.scriptOKInfoElement.appendChild(okInfoNode)

    def generateRecord(self,recordPath=None):
        self.scriptElement.appendChild(self.scriptResultElement)
        self.scriptElement.appendChild(self.scriptLogElement)
        self.scriptElement.appendChild(self.scriptOKInfoElement)
        self.scriptElement.appendChild(self.scriptErrorInfoElement)
        for verStep in self.setps:
            self.scriptElement.appendChild(verStep)
        self.deviceElement.appendChild(self.scriptElement)
        self.rootElement.appendChild(self.deviceElement)
        file = open(os.path.join(recordPath,Config.RECORD_XML_NAME),'a')
        self.document.writexml(file)
        file.close()

    def saveRecord(self):
        file = open(self.recordFilePath,'w')
        self.document.writexml(file)
        file.close()

