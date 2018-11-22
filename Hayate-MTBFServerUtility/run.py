# -*- coding: utf-8 -*-

from ParserConfig.parser import Parser

def startTcp():
    pass

def startNodeServer():
    pass

def startPlaybackScripts():
    pass


if __name__ == '__main__':
    # 解析配置文件
    devices = []
    try:
        configParser = Parser()
        devices = configParser.getDevices()
    except BaseException,e:
        print 'Paser config file fail.Error:{error}'.format(error=str(e))

    # 开启TCP通信服务

