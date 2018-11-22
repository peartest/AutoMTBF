# -*- coding: utf-8 -*-

class AndroidProcess():

    cmdline = None
    memory = []

    def __init__(self):
        pass

    def setCmdLine(self,cmdline=None):
        self.cmdline=cmdline

    def addMemInfo(self,data):
        self.memory.append(data)

