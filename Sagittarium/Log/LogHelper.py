# -*- coding: utf-8 -*-
__author__ = '赵嘉俊'

class Logger():

    def __init__(self):
        pass

    @staticmethod
    def debug(value):
        print '[Debug]{value}'.format(value=str(value))

    @staticmethod
    def info(value):
        print '[Info]{value}'.format(value=str(value))

    @staticmethod
    def error(value):
        print '[Error]{value}'.format(value=str(value))

    @staticmethod
    def warning(value):
        print '[Warning]{value}'.format(value=str(value))