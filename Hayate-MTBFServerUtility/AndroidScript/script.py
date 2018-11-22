__author__ = 'thundersoft'

class Script():

    def __init__(self):
        self.scriptName=None
        self.scriptPath=None
        self.scriptLoopCount=None
        self.scriptLessLoopCount=None
        self.scriptReliantDevice = None;

    def setScriptName(self,name=None):
        self.scriptName=name

    def setScriptPath(self,path=None):
        self.scriptPath = path

    def setScriptLoop(self,loop=None):
        self.scriptLoopCount=loop

    def setReliantDevice(self,reliantDevice=None):
        self.scriptReliantDevice = reliantDevice

    def resetLessLoopCount(self):
        self.scriptLessLoopCount = self.scriptLoopCount



