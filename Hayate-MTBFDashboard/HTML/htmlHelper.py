# -*- coding: utf-8 -*-
__author__ = '赵嘉俊'

class html():

    def __init__(self):
        pass

    def getTestcasesInfo(self,device):
        testcasesName = []
        testcasesPassrate = []
        for testcase in device.testcase:
            testcasesName.append(testcase.name)
            testcasesPassrate.append(float(testcase.passRate))
        return testcasesName,testcasesPassrate

    def getConsumptionOfTestcases(self,device):
        consumption = []
        testcases = device.testcase
        for testcase in testcases:
            consumption.append([testcase.name,testcase.totleExecuteTime])
        return consumption

    def getTestcasePassFailTimes(self,device):
        passTimes = []
        failTimes = []
        for testcase in device.testcase:
            passTimes.append(testcase.passTimes)
            failTimes.append(testcase.failTimes)
        return passTimes,failTimes


