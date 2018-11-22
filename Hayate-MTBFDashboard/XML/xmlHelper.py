# -*- coding: utf-8 -*-
__author__ = '赵嘉俊'

from xml.dom.minidom import  parse
from Config import DashboardConfig

class XmlParse():

    def __init__(self):
        self.xmlPath = None

    def __setXMLPath(self,value):
        self.xmlPath = value

    def __initParse(self):
        self.document = parse(self.xmlPath)
        self.rootElement = self.document.documentElement

    def refresh(self,path):
        self.__setXMLPath(path)
        self.__initParse()

    def getDeviceID(self):
        deviceElements = self.rootElement.getElementsByTagName(DashboardConfig.RECORD_XML_DEVICE_TAG)
        udid = deviceElements[0].getAttribute(DashboardConfig.RECORD_XML_UDID_ATTRIBUTE)
        return udid

    def getDeviceMappingId(self):
        deviceElements = self.rootElement.getElementsByTagName(DashboardConfig.RECORD_XML_DEVICE_TAG)
        mappingid = deviceElements[0].getAttribute(DashboardConfig.RECORD_XML_MAPPINGID_ATTRIBUTE)
        return mappingid

    def getScriptStartTime(self):
        scriptElements = self.rootElement.getElementsByTagName(DashboardConfig.RECORD_XML_SCRIPT_TAG)
        scriptStartTime = scriptElements[0].getAttribute(DashboardConfig.RECORD_XML_STARTTIME_ATTRIBUTE)
        return scriptStartTime

    def getScriptEndTime(self):
        scriptElements = self.rootElement.getElementsByTagName(DashboardConfig.RECORD_XML_SCRIPT_TAG)
        scriptEndTime = scriptElements[0].getAttribute(DashboardConfig.RECORD_XML_ENDTIME_ATTRIBUTE)
        return scriptEndTime

    def getCurrentScriptLoop(self):
        scriptElements = self.rootElement.getElementsByTagName(DashboardConfig.RECORD_XML_SCRIPT_TAG)
        loop = scriptElements[0].getAttribute(DashboardConfig.RECORD_XML_LOOP_ATTRIBUTE)
        return loop

    def getCurrentScriptRound(self):
        scriptElements = self.rootElement.getElementsByTagName(DashboardConfig.RECORD_XML_SCRIPT_TAG)
        round = scriptElements[0].getAttribute(DashboardConfig.RECORD_XML_ROUND_ATTRIBUTE)
        return round

    def getCurrentScriptName(self):
        scriptElements = self.rootElement.getElementsByTagName(DashboardConfig.RECORD_XML_SCRIPT_TAG)
        name = scriptElements[0].getAttribute(DashboardConfig.RECORD_XML_SCRIPTNAME_ATTRIBUTE)
        return name

    def getCurrentScriptResult(self):
        resultElements =self.rootElement.getElementsByTagName(DashboardConfig.RECORD_XML_SCRIPTRESULT_TAG)
        result = resultElements[0].getAttribute(DashboardConfig.RECORD_XML_VALUE_ATTRIBUTE)
        return result

    def getCurrentScriptLogFolderName(self):
        logFolderElements = self.rootElement.getElementsByTagName(DashboardConfig.RECORD_XML_LOG_TAG)
        folder = logFolderElements[0].getAttribute(DashboardConfig.RECORD_XML_FOLDER_ATTRIBUTE);
        return folder

    def getCurrentScriptOKInfo(self):
        okInfoElements = self.rootElement.getElementsByTagName(DashboardConfig.RECORD_XML_OKINFO_TAG)
        if okInfoElements[0].firstChild == None:
            info = 'N/A'
        else:
            info = okInfoElements[0].firstChild.data
        return info

    def getCurrentScriptErrorInfo(self):
        errorInfoElements = self.rootElement.getElementsByTagName(DashboardConfig.RECORD_XML_ERRORINFO_TAG)
        if errorInfoElements[0].firstChild == None:
            info = 'N/A'
        else:
            info = errorInfoElements[0].firstChild.data
        return info

    def getCurrentScriptSteps(self):
        steps = []
        stepElements = self.rootElement.getElementsByTagName(DashboardConfig.RECORD_XML_STEP_TAG)
        for step in stepElements:
            currentStep = {}
            currentStep['content'] = step.getAttribute(DashboardConfig.RECORD_XML_CONTENT_ATTRIBUTE)
            currentStep['result'] = step.getAttribute(DashboardConfig.RECORD_XML_STEPRESULT_ATTRIBUTE)
            steps.append(currentStep)
        return steps



if __name__ == '__main__':

    print str(__file__).replace('Hayate-MTBFDashboard/XML/xmlHelper.py','Hayate-MTBFServerUtility/ParserConfig/MultDevicesPBConfig.xml')

    # xml = XmlParse()
    # xml.setXMLPath(r'F:\Git-Local-Automatic-Tools\Hayate-MTBFDashboard\20160428141329\record\990005270007595\Round_1\Demo.py\Time[20160428103155]_Loop[1]\Record.xml')
    # xml.initParse()
    # print xml.getDeviceID();
    # print xml.getScriptStartTime()
    # print xml.getScriptEndTime()
    # print xml.getCurrentScriptLoop()
    # print xml.getCurrentScriptName()
    # print xml.getCurrentScriptResult()
    # print xml.getCurrentScriptLogFolderName()
    # print xml.getCurrentScriptOKInfo()
    # print xml.getCurrentScriptErrorInfo()
    # print xml.getCurrentScriptSteps()