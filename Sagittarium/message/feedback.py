# -*- coding: utf-8 -*-
__author__ = '赵嘉俊'

import json;
import time;

class Feedback:

    def __init__(self,currentSocket,script,udid='',mappingudid=None):
        self.current_script_name = script;
        self.current_socket = currentSocket;
        # 主设备id
        self.current_udid = udid;
        # 主设备映射id
        self.current_mapping_udid = mappingudid;

    def feedback_script_start(self,
                              isMTBFTestCase=False,
                              mtbfWholeTestFolder=None,
                              mtbfRoundFolder=None,
                              mtbfTestCaseStartTime=None,
                              mtbfTestCaseCurrentLoop=None,
                              mtbfTestCaseName=None):
        if isMTBFTestCase:
            message = {'type':'step',
                       'step':'script_start',
                       'script':self.current_script_name,
                       'udid':self.current_udid,
                       'mappingudid':self.current_mapping_udid,
                       'mtbfWholeTestFolder':mtbfWholeTestFolder,
                       'mtbfRoundFolder':mtbfRoundFolder,
                       'mtbfTestCaseStartTime':mtbfTestCaseStartTime,
                       'mtbfTestCaseCurrentLoop':mtbfTestCaseCurrentLoop,
                       'mtbfTestCaseName':mtbfTestCaseName};
        else:
            message = {'type':'step',
                       'step':'script_start',
                       'script':self.current_script_name,
                       'udid':self.current_udid
                       };
        message_to_send = json.dumps(message) + '\n';
        self.current_socket.send(str(message_to_send));

    def feedback_script_end(self,endTime=None):
        message = {'type':'step',
                   'step':'script_end',
                   'script':self.current_script_name,
                   'udid':self.current_udid,
                   'endTime':endTime};
        message_to_send = json.dumps(message) + '\n';
        self.current_socket.send(str(message_to_send));

    def feedback_action_fail(self,step,error,ignore_error=False):
        message = {'type':'result','result':False,'step':step,'error':error,'script':self.current_script_name,'udid':self.current_udid,'ignore_error':ignore_error};
        message_to_send = json.dumps(message) + '\n';
        self.current_socket.send(str(message_to_send));
        return message;

    def feedback_action_ok(self,step):
        message = {'type':'result','result':True,'step':step,'error':None,'script':self.current_script_name,'udid':self.current_udid};
        message_to_send = json.dumps(message) + '\n';
        self.current_socket.send(str(message_to_send));
        return message;

    def feedback_show_message(self,message = None,step = None):
        message = {'type':'debug','message':message,'step':step,'script':self.current_script_name,'udid':self.current_udid}
        message_to_send = json.dumps(message) + '\n'
        self.current_socket.send(str(message_to_send));
        return message;

    def feedback_script_ok(self,step = None,info = None):
        message = {'type':'scriptOKResult','result':True,'step':step,'info':info,'script':self.current_script_name,'udid':self.current_udid};
        message_to_send = json.dumps(message) + '\n';
        self.current_socket.send(str(message_to_send));
        return message;

    def feedback_top_3000_debug(self,info):
        message = {'type':'top3000_debug','info':info,'result':None,'step':None,'error':None,'script':self.current_script_name};
        message_to_send = json.dumps(message) + '\n';
        self.current_socket.send(str(message_to_send));
        return message;