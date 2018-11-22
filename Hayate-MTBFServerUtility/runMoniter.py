# -*- coding: utf-8 -*-
__author__ = '赵嘉俊'

from ParserConfig.parser import Parser
from MemMoniter.Moniter import Moniter

if __name__ == '__main__':

        parser = Parser();
        devices = parser.getDevices()

        for device in devices:
            memoryMoniter = Moniter(device=device);
            memoryMoniter.procrank()
            device.isOOM()

