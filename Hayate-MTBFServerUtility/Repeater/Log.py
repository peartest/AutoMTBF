# -*- coding: utf-8 -*-

import ctypes,sys
import LogColor

std_out_handle = ctypes.windll.kernel32.GetStdHandle(LogColor.STD_OUTPUT_HANDLE)

def set_cmd_text_color(color, handle=std_out_handle):
    Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return Bool

def resetColor():
    set_cmd_text_color(LogColor.FOREGROUND_RED |LogColor.FOREGROUND_GREEN | LogColor.FOREGROUND_BLUE)

def show(info):
    set_cmd_text_color(LogColor.FOREGROUND_YELLOW)
    sys.stdout.write("Process Cmdline:")
    set_cmd_text_color(LogColor.FOREGROUND_PINK)
    sys.stdout.write(info + '\n')
    resetColor()

