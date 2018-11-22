# -*- coding: utf-8 -*-
from __future__ import division
__author__ = '赵嘉俊'

import time
import datetime

class AndroidTestCase():

    def __init__(self):
        self.totalExecuteTimes = None
        self.passRate = None
        self.passTimes = 0
        self.failTimes = 0
        self.name = None
        self.totleExecuteTime=0;
        self.scripts = []
        self.passScripts = []
        self.failScripts = []
        self.isPass = False;
        self.executeDetailHtmlPath = None

    def setExecuteDetailHtmlPath(self,path):
        self.executeDetailHtmlPath = path

    def addScript(self,script):
        self.scripts.append(script)

    def setName(self,value):
        self.name = value

    def calculateData(self):
        self.totalExecuteTimes = len(self.scripts)

        for script in self.scripts:
            # 处理当前脚本执行结果
            if script.result == 'OK':
                self.passTimes = self.passTimes + 1
                self.passScripts.append(script)
            elif script.result == 'Fail':
                self.failTimes = self.failTimes + 1
                self.failScripts.append(script)
            # 记录当前脚本执行时间，单位秒
            self.totleExecuteTime = self.totleExecuteTime + self.__calculateScriptExcuteTime(script)
        self.passRate = float('%.2f'%(self.passTimes/self.totalExecuteTimes))
        if self.passRate >= 0.90 :
            self.isPass = True
        else:
            self.isPass = False

    def __calculateScriptExcuteTime(self,currentScript):
        start = time.strptime(currentScript.startTime,"%Y%m%d%H%M%S")
        end = time.strptime(currentScript.endTime,"%Y%m%d%H%M%S")
        start_date = datetime.datetime(start.tm_year,
                                       start.tm_mon,
                                       start.tm_mday,
                                       start.tm_hour,
                                       start.tm_min,
                                       start.tm_sec)
        end_date = datetime.datetime(end.tm_year,
                                     end.tm_mon,
                                     end.tm_mday,
                                     end.tm_hour,
                                     end.tm_min,
                                     end.tm_sec)
        return (end_date-start_date).seconds


if __name__ == "__main__":
    # start = time.strptime('20160428103155',"%Y%m%d%H%M%S")
    # end = time.strptime('20160428103226',"%Y%m%d%H%M%S")
    # print start
    # print end
    # start_date = datetime.datetime(start.tm_year,
    #                                start.tm_mon,
    #                                start.tm_mday,
    #                                start.tm_hour,
    #                                start.tm_min,
    #                                start.tm_sec)
    # end_date = datetime.datetime(end.tm_year,
    #                              end.tm_mon,
    #                              end.tm_mday,
    #                              end.tm_hour,
    #                              end.tm_min,
    #                              end.tm_sec)
    # print '相差:%s'%(end_date-start_date).seconds
    # print type((end_date-start_date).seconds)

    passRate = float('%.2f'%(70/71))
    print passRate
