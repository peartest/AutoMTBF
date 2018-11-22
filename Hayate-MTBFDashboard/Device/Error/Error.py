# -*- coding: utf-8 -*-
__author__ = '赵嘉俊'

class AndroidError():

    def __init__(self):
        self.type = None;
        self.happenTime = None;
        self.logcat = None;
        self.dropboxFilePath = None

    def setType(self,value):
        self.type = value

    def setHappenTime(self,value):
        self.happenTime = value

    def setLogcat(self,value):
        self.logcat = value

    def setDropboxFilePath(self,value):
        self.dropboxFilePath = value



