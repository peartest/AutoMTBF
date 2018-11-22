# -*- coding: utf-8 -*-

import time
import os

from tcp.tcpServer import TcpServer
from  ParserConfig.parser import Parser
import Config

if __name__ == '__main__':
    try:
        parser = Parser()
        devices = parser.getDevices()
        tcpServerList=[]
        reportPath = Config.CONFI_XML_TEST_REPORT_PATH.format(time=time.strftime('%Y%m%d%H%M%S',time.localtime()))
        # 创建报告目录
        if not os.path.exists(reportPath):
            os.makedirs(reportPath)
        # 创建以设备集数量为准的Tcp Server
        for device in devices:
            tcpServer = TcpServer()
            # 设置Tcp Server关联的设备
            tcpServer.setDevice(device=device)
            # 设置Tcp Server关联的报告路径
            tcpServer.setReportPath(path=reportPath)
            tcpServerList.append(tcpServer)
        for sever in tcpServerList:
            sever.start()
            time.sleep(1)
        print 'Start Tcp Sever finish.Wait script to connect.'
        for server in tcpServerList:
            server.join()
    except BaseException,e:
        print 'Error:{error}'.format(error=str(e))