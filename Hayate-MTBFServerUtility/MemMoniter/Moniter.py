# -*- coding: utf-8 -*-

import MatchingString as ms
from AndroidProcess import AndroidProcess
import subprocess
import re

class Moniter:

    command_procrank = 'adb -s {id} shell procrank'
    # pattern = re.compile(ms.procrank)

    def __init__(self,device=None):
        self.device = device

    def procrank(self):
        # command = self.command_procrank.format(id = self.device.deviceID)
        command = self.command_procrank.format(id='1d469132')
        print command
        procrank = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        procrankId = procrank.pid
        while True:
            line = procrank.stdout.readline()
            if line == '' and procrank.poll() != None:
                break
            else:
                self.__parserMessage(message=line)


    def dumpMeminfo(self):
        pass

    def dumpHprof(self):
        pass

    def __parserMessage(self,message=None):
        valid = ms.pattern.match(message)
        data = {}
        if valid:
            print '********************'
            print valid.group()
            print '********************'
            data['pid'] = str(valid.group(1))
            data['vss'] = int(valid.group(2))
            data['rss'] = int(valid.group(3))
            data['pss'] = int(valid.group(4))
            data['uss'] = int(valid.group(5))
            data['cml'] = str(valid.group(10))
            cml = str(valid.group(10))
            exist,process = self.__checkProcessExist(cml)
            if not exist:
                self.__newAndroidProcess(data,cml)
            else:
                self.__addAndroidProcessInfo(process,data)
        else:
            pass

        print '================'
        print data
        print '================'

    def __newAndroidProcess(self,data,cml):
        process = AndroidProcess()
        process.setCmdLine(cmdline=cml)
        process.addMemInfo(data)
        print process
        print '============='
        self.device.append(process)

    def __addAndroidProcessInfo(self,process,data):
        process.addMemInfo(data)

    def __checkProcessExist(self,cmdline=None):
        isExist = False
        processExisted = None
        print self.device
        for process in self.device.process:
            if process.cmdline == cmdline:
                isExist = True
                processExisted = process
                break
        return isExist,processExisted
if __name__ == '__main__':
    a=Moniter()
    a.procrank()