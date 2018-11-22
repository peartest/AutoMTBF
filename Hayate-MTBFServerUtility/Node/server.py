# -*- coding: utf-8 -*-

import threading
import subprocess
import Config

class Server(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.device=None
        self.nodeServerProcessID=None

    def setDevice(self,device):
        self.device = device

    def run(self):
        command = '{node} {appium} -p {port} -U {id} -bp {bpPort} --session-override'\
            .format(node=Config.CONFIG_NODE_EXE,
                    appium=Config.CONFIG_NODE_APPIUM,
                    port=self.device.serverPort,
                    id=self.device.deviceID,
                    bpPort=self.device.bootstrapPort)
        popen = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        # 设置当前Node Server的PID
        self.nodeServerProcessID = popen.pid
        while True:
            next_line = popen.stdout.readline()
            if next_line == '' and popen.poll() != None:
                break
            else:
                # 打印日志的标准输出
                print next_line
