# -*- coding: utf-8 -*-

from Node.server import Server
from  ParserConfig.parser import Parser
import time

if __name__ == '__main__':
    parser = Parser()
    devices = parser.getDevices()
    nodeServerList=[]
    try:
        for device in devices:
            nodeServer = Server()
            # 设置当前Node Server关联的设备集中的主设备
            nodeServer.setDevice(device=device)
            nodeServerList.append(nodeServer)

        # 开始所有Node Server
        for server in nodeServerList:
            server.start()
            time.sleep(2)
        print 'Start Appium Server finish.Waiting Appium Client to connect'
        for server in nodeServerList:
            server.join()
    except BaseException,e:
        print str(e)




