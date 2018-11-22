# -*- coding: utf-8 -*-
import socket
import time
import os
import threading
import Config
from scriptClient import Client

class TcpServer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self);
        self.device=None
        self.serverSocket=None;
        self.reportPath=None;

    def run(self):
        self.listen()

    def setDevice(self,device=None):
        self.device = device

    def setReportPath(self,path=None):
        self.reportPath = path

    def listen(self):
        # 启动Tcp 服务器监听
        self.serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.serverSocket.bind(('',self.device.tcpPort))
        self.serverSocket.listen(10000)
        while True:
            connect,address = self.serverSocket.accept()
            client = Client();
            client.setDevice(self.device)
            client.setConnectSocket(socket=connect)
            client.setReportPath(reportPath=self.reportPath)
            client.start();
        self.serverSocket.close()


