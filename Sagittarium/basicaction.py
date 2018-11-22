# -*- coding: utf-8 -*-

import os
import socket
import subprocess
import time
import json
from PIL import Image
from selenium.webdriver.common.by import By
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction
from appium.webdriver.connectiontype import ConnectionType
from message.feedback import Feedback
import validation.imageValidation
from SagittariumException.sagittariumException import NoSuchSupportDeviceException
from SagittariumException.sagittariumException import TargetDeviceNoneValueException
from SagittariumException.sagittariumException import InexistentDeviceIDException
from Log.LogHelper import Logger

class BasicAction:

    def __init__(self,script,systemArgs=None,isMTBFTestCase=False):
        """init socket,scriptName,webdriver,cpas
        :param script:
        :param udid:
        :param port:
        :return:
        """
        if isMTBFTestCase:
            # 实例回放参数
            self.runParams = self.__instanceParams(systemArgs[1])
            # 实例设备参数
            self.deviceParams = self.__instanceParams(systemArgs[2])
            # 实例辅助设备参数
            self.supportDevices = self.__instanceParams(systemArgs[3])

            self.targetDevice = None
            self.scriptname = script;
            self.current_udid = self.deviceParams['udid'];
            self.current_mapping_udid = self.deviceParams['mappingid'];
            self.logStorePath = self.deviceParams['logStorePath']
            self.serverPort = self.runParams['serverPort'];
            self.tcp=self.runParams['tcp']
            self.desired_caps = {};
            self.desired_caps['platformName'] = 'Android';
            self.desired_caps['platformVersion'] = '4.2';
            self.desired_caps['deviceName'] = 'Android Device';
            self.desired_caps['udid'] = self.current_udid;
            self.desired_caps['autoLaunch'] = False;
            self.desired_caps['appPackage'] = '';
            self.desired_caps['appActivity'] = '';
            self.desired_caps['newCommandTimeout'] = 60 * 60 * 24
            self.driver = None;
            # MTBF 相关变量
            self.mtbf_isMTBFTestCase = True;
            self.mtbf_WholeTestFolder = self.runParams['wholeTestFolderSuffix'];
            self.mtbf_WholeTestFolder_Record = self.__getWholeTestFolderForRecordFiles();
            self.mtbf_WholeTestFolder_Logcat = None
            self.mtbf_RoundFolder = self.runParams['roundFolder'];
            self.mtbf_TestCaseStartTime = time.strftime('%Y%m%d%H%M%S',time.localtime());
            self.mtbf_TestCaseEndTime = None;
            self.mtbf_TestCaseCurrentLoop = self.runParams['currentLoop'];
            self.mtbf_TestCaseName = self.runParams['scriptName']
        else:
            self.scriptname = script;
            self.current_udid = None;
            self.serverPort = 4723;
            self.tcp=8998
            self.desired_caps = {};
            self.desired_caps['platformName'] = 'Android';
            self.desired_caps['platformVersion'] = '4.2';
            self.desired_caps['deviceName'] = 'Android Device';
            self.desired_caps['udid'] = self.current_udid;
            self.desired_caps['autoLaunch'] = False;
            self.desired_caps['appPackage'] = '';
            self.desired_caps['appActivity'] = '';
            self.desired_caps['newCommandTimeout'] = 60 * 60 * 24
            self.driver = None;
            # MTBF 相关变量
            self.mtbf_isMTBFTestCase = False;

    def __instanceParams(self,value):
        tmp = value
        tmp = tmp.replace("{","{\"")
        tmp = tmp.replace(":","\":\"")
        tmp = tmp.replace(",","\",\"")
        tmp = tmp.replace("}","\"}")
        tmp = tmp.replace("}\",\"{","},{")
        tmp = tmp.replace("\":\"\\",":\\")
        return json.loads(tmp)

    def __initMessage(self,ignore_error=False):
        """
        init message
        :return:
        """
        message = {};
        message['ignore_error'] = ignore_error;
        return message;

    def assert_script_error(self,step = None,error = None):
        """
        Edit Time:2015/6/3
        For version:v2003
        Assertion script error.
        :param step:
        :param error:
        :return:
        """
        self.feedback.feedback_action_fail(str(step),str(error),False);

    def assert_script_ok(self,ok_step = None,ok_info = None):
        self.feedback.feedback_script_ok(step=ok_step,info=ok_info);

    def supportDevice(self,name):
        isFindDevice = False
        for item in self.supportDevices:
            if item['mappingid'] == name:
                return item['udid']
        if not isFindDevice:
            raise NoSuchSupportDeviceException(name)

    def __getDeviceLogStorePath(self,udid):
        isFindDevice = False
        if self.deviceParams['udid'] == udid:
            return self.deviceParams['logStorePath']
        else:
            for item in self.supportDevices:
                if item['udid'] == udid:
                    return item['logStorePath']
        if not isFindDevice:
            raise NoSuchSupportDeviceException(udid)

    def __getWholeTestFolderForRecordFiles(self):
        if self.deviceParams['mappingid'] == "None":
            return self.deviceParams['udid'] + '.' + self.mtbf_WholeTestFolder
        else:
            return self.deviceParams['mappingid'] + '.' + self.mtbf_WholeTestFolder

    def __getWholeTestFolderForLogcatFiles(self,targetDevice):
        if targetDevice == None:
            if self.deviceParams['mappingid'] == "None":
                self.mtbf_WholeTestFolder_Logcat = self.deviceParams['udid'] + '.' + self.mtbf_WholeTestFolder
            else:
                self.mtbf_WholeTestFolder_Logcat = self.deviceParams['mappingid'] + '.' + self.mtbf_WholeTestFolder
        else:
            # 检查是主设备还是辅助设备
            if (self.deviceParams['udid'] == targetDevice) and (not self.deviceParams['mappingid'] == "None"):
                self.mtbf_WholeTestFolder_Logcat = self.deviceParams['mappingid'] + '.' + self.mtbf_WholeTestFolder
            elif self.deviceParams['udid'] == targetDevice and self.deviceParams['mappingid'] == "None":
                self.mtbf_WholeTestFolder_Logcat = self.deviceParams['udid'] + '.' + self.mtbf_WholeTestFolder
            elif not self.deviceParams['udid'] == targetDevice:
                for item in self.supportDevices:
                    if (item['udid'] == targetDevice) and (not item['mappingid'] == "None"):
                        self.mtbf_WholeTestFolder_Logcat = item['mappingid'] + '.' + self.mtbf_WholeTestFolder
                        break
                    elif (item['udid'] == targetDevice) and (item['mappingid'] == "None"):
                        self.mtbf_WholeTestFolder_Logcat = item['udid'] + '.' + self.mtbf_WholeTestFolder
                        break

    def script_start(self,targetDevice=None):
        """connect http server and get webdriver instance
        :return:
        """
        if targetDevice == None:
                raise TargetDeviceNoneValueException(value='123')

        # 设置在哪台设备上面执行：
        if self.mtbf_isMTBFTestCase:
            self.targetDevice = targetDevice
            self.desired_caps['udid'] = self.targetDevice
        else:
            self.current_udid = targetDevice
            self.desired_caps['udid'] = self.current_udid

        # 设置wholeTestFolder
        if self.mtbf_isMTBFTestCase:
            self.__getWholeTestFolderForLogcatFiles(self.targetDevice)

        # 连接 Webdriver server
        currentServerPort = str(self.serverPort);
        self.driver = webdriver.Remote('http://localhost:' + currentServerPort + '/wd/hub',self.desired_caps);
        # 连接TCP server
        self.scriptsocket = socket.socket();
        host = socket.gethostname();
        self.scriptsocket.connect((host,int(self.tcp)));

        if self.mtbf_isMTBFTestCase:
            self.feedback = Feedback(self.scriptsocket, self.scriptname,
                                     udid=self.current_udid if self.targetDevice == None else self.targetDevice,
                                     mappingudid=self.current_mapping_udid);
            self.feedback.feedback_script_start(isMTBFTestCase=True,
                                                mtbfWholeTestFolder=self.mtbf_WholeTestFolder_Record,
                                                mtbfRoundFolder=self.mtbf_RoundFolder,
                                                mtbfTestCaseStartTime=self.mtbf_TestCaseStartTime,
                                                mtbfTestCaseCurrentLoop=self.mtbf_TestCaseCurrentLoop,
                                                mtbfTestCaseName=self.mtbf_TestCaseName);
        else:
            self.feedback = Feedback(self.scriptsocket, self.scriptname,
                                     udid=self.current_udid);
            self.feedback.feedback_script_start(isMTBFTestCase=False)

    def script_set_device(self,udid=None):
        """
        Set the device which current device run on
        :param udid:
        :return:
        """
        self.desired_caps['udid'] = udid;

    def script_end(self):
        # script end,send message to java server, let the current script connection close
        if self.mtbf_isMTBFTestCase:
            self.mtbf_WholeTestFolder = self.runParams['wholeTestFolderSuffix']
            self.mtbf_TestCaseEndTime = time.strftime('%Y%m%d%H%M%S',time.localtime());
        self.driver.quit();
        self.feedback.feedback_script_end(endTime=self.mtbf_TestCaseEndTime if self.mtbf_isMTBFTestCase else None);
        self.scriptsocket.close();

    def click_element_by_point(self,param,ignore_error_handle = False):
        """click the element on screen by the point of it.
        :param param:
        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'click element by point x:' + str(param['x']) + ' y:' + str(param['y']);
        try:
            point_x = param['x'];
            point_y = param['y'];
            click_count = param['count'];
            touch_action = TouchAction(self.driver);
            touch_action.tap(x=point_x,y=point_y,count=click_count).release().perform();
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            print 'catch exception:'+ str(e);
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def long_click_element_by_point(self,param,ignore_error_handle = False):
        """long click the element on screen by the point of it.
        :param param:{'x':1,'y':2,'duration'=1000}
        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'long click element by point x:' + str(param['x']) + ' y:' + str(param['y']);
        try:
            point_x = param['x'];
            point_y = param['y'];
            click_duration = param['duration'];
            touch_action = TouchAction(self.driver);
            touch_action.long_press(x=point_x,y=point_y,duration=click_duration).perform();
            message = self.feedback.feedback_action_ok(step);
        except BasicAction,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def click_element_by_id(self,param,ignore_error_handle = False):
        """click the element on screen by resource id of it.
        :param param:{'resourceid':'xxx',}
        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'click element by resourceid:' + param['resourceid'];
        try:
            id = param['resourceid'];
            element = self.driver.find_element_by_id(id);
            element.click();
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def click_element_by_xpath(self,param,ignore_error_handle=False):
        """
        Click the element by it's xpath
        :return:
        """
        message = {};
        step = 'Click element by it\'s xpath {xpath}'.format(xpath=param['xpath'])
        try:
            xpath = param['xpath'];
            element = self.driver.find_element_by_xpath(xpath);
            element.click()
            message = self.feedback.feedback_action_ok(step)
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle)
        finally:
            return message

    def find_element_by_xpath(self,param,ignore_error_handle=False):
        """find element by xpath"""
        message = {}
        step = 'Find element by xpath {value}'.format(value=str(param['xpath']))
        try:
            xpath = param['xpath']
            element = self.driver.find_element_by_xpath(xpath)
            message = self.feedback.feedback_action_ok(step)
            message['element'] = element
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle)
        finally:
            return message

    # def click_element_by_ID(self,id=None,ignore_error_handle=False):
    #     message = {}
    #     step = 'Click element by id:{elementId}'.format(elementId=str(id))
    #     try:
    #         self.driver.clickElementWithId(id);
    #         message = self.feedback.feedback_action_ok(step)
    #     except BaseException,e:
    #         message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle)
    #     finally:
    #         return message

    def long_click_element_by_id(self,param,ignore_error_handle = False):
        """long click the element on screen by resource id of it.
        :param param:{'resourceid':'xxx','duration':1000}
        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'long click element by resourceid:' + param['resourceid'];
        try:
            id = param['resourceid'];
            click_duration = param['duration'];
            element = self.driver.find_element_by_id(id);
            touch_action = TouchAction(self.driver);
            touch_action.long_press(element,click_duration).perform();
            message = self.feedback.feedback_action_ok(step)
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def click_element_by_text(self,param,ignore_error_handle = False):
        """
        Edit Time:2015/6/3
        For version:v2003
        click element by text
        :param param:
        :return:
        """
        message = {};
        text = str(param.get('text',None));
        step = 'click element by text \'' + text + '\''
        try:
            element = self.driver.find_element_by_name(text);
            element.click();
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def long_click_element_by_text(self,param,ignore_error_handle = False):
        """
        Edit Time:2015/6/3
        For version:v2003
        long click element by text
        :param param:
        :return:
        """
        message = {};
        text = str(param.get('text',None));
        click_duration = param.get('duration',None);
        step = 'long click element by text \'' + text + '\'';
        try:
            element = self.driver.find_element_by_name(text);
            touch_action = TouchAction(self.driver);
            touch_action.long_press(element,click_duration).perform();
            message = self.feedback.feedback_action_ok(step)
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle)
        finally:
            return message;

    def select_listitem_by_id(self,param,ignore_error_handle = False):
        """
        Edit Time:2015/6/3
        For version:v2003
        select the listitem in list
        :param param:
        :return:
        """
        message = {};
        list_id = str(param.get('list_id',None));
        listitem_id = str(param.get('listitem_id',None));
        listitem_index = param.get('listitem_index',None);
        step = 'select listitem ' + str(listitem_index) + ' in list \'' + list_id + '\'';
        try:
            list_element = self.driver.find_element_by_id(list_id);
            listitems = list_element.find_elements_by_id(listitem_id);
            listitem = listitems[listitem_index];
            listitem.click();
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def get_text_by_id(self,param,ignore_error_handle = False):
        """
        Edit Time:2015/6/5
        For version:v2003
        get text of element,locate the element by id
        :param param:
        :return:
        """
        message = {};
        resource_id = str(param.get('resource_id',None));
        step = 'get text from the element which id is \'' + resource_id + '\'';
        try:
            element = self.driver.find_element_by_id(resource_id);
            text = element.text;
            message = self.feedback.feedback_action_ok(step);
            message['text'] = text;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
            message['text'] = None;
        finally:
            return message;

    def get_checked_state_by_id(self,param,ignore_error_handle = False):
        """
        Edit Time:2015/6/5
        For version:v2003
        get check state of element,locate the element by id
        :param param:
        :return:
        """
        message = {};
        resource_id = str(param.get('resource_id',None));
        step = 'check if the checkbox is checked by id \'' + resource_id + '\'';
        try:
            element = self.driver.find_element_by_id(resource_id);
            checked = element.is_selected();
            message = self.feedback.feedback_action_ok(step);
            message['checked'] = checked;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
            message['checked'] = None;
        finally:
            return message;

    def find_child_element_by_id(self,param,ignore_error_handle = False):
        """
        Edit Time:2015/6/8
        For version:v2003
        find child element in parent element
        :param param:
        :return:
        """
        message = {};
        parent_element = param.get('parent',None);
        child_resource_id = str(param.get('child_resource_id',None));
        step = 'find child element \'' + child_resource_id + '\' in parent element';
        try:
            child_element = parent_element.find_element_by_id(child_resource_id);
            message = self.feedback.feedback_action_ok(step);
            message['child_element'] = child_element;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
            message['child_element'] = None;
        finally:
            return message;

    def find_child_elements_by_id(self,param,ignore_error_handle = False):
        """
        Edit Time:2015/6/8
        For version:v2003
        find child elements in parent element
        :param param:
        :return:
        """
        message = {};
        parent_element = param.get('parent',None);
        child_resource_id = str(param.get('child_resource_id',None));
        step = 'find child elements \'' + child_resource_id + '\' in parent element'
        try:
            child_elements = parent_element.find_elements_by_id(child_resource_id);
            message = self.feedback.feedback_action_ok(step);
            message['child_elements'] = child_elements;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
            message['child_elements'] = None;
        finally:
            return message;

    def find_child_elements_by_class(self,param,ignore_error_handle = False):
        """
        Edit Time:2015/6/8
        For version:v2003
        find child elements in parent element
        :param param:
        :return:
        """
        message = {};
        parent_element = param.get('parent',None);
        child_class = str(param.get('child_class',None));
        step = 'find child elements by class \'' + child_class + '\' in parent elements'
        try:
            child_elements = parent_element.find_elements(by=By.CLASS_NAME,value=child_class);
            message = self.feedback.feedback_action_ok(step);
            message['child_elements'] = child_elements;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
            message['child_elements'] = None;
        finally:
            return message;

    def sleep(self,param,ignore_error_handle = False):
        """sleep some time.
        :param param:{'timeout':1000}
        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'sleep some time:' + str(param['timeout']);
        try:
            sleep_time = param['timeout'];
            touch_action = TouchAction(self.driver);
            touch_action.wait(ms=sleep_time).perform();
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def find_element_by_resource_id(self,param,ignore_error_handle = False):
        """find element by it's resource id.
        :param param::{'resourceid':'xxxx'}
        :param ignore_error_handle:
        :return:the result of the action.It contains element object.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'find element by resource id:' + param['resourceid'];
        try:
            id = param['resourceid'];
            element = self.driver.find_element_by_id(id);
            message = self.feedback.feedback_action_ok(step);
            message['element'] = element;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def find_element_by_text(self,param,ignore_error_handle = False):
        """find element by it's text .
        :param param:{'text':'xxxx'}
        :param ignore_error_handle:
        :return:the result of the action.It contains element object.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'find element by text:' + param['text'];
        try:
            text = param['text'];
            element = self.driver.find_element_by_name(text);
            message = self.feedback.feedback_action_ok(step);
            message['element'] = element;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def find_element_by_partial_text(self,param,ignore_error_handle = False):
        """
        for Sagittarius version 2005
        find element by partial text
        :param param:
        :param ignore_error_handle:
        :return:
        """
        message = {}
        step = 'find element by partial text:' + param['partial_text'];
        partial_text = param.get('partial_text',None);
        try:
            element = self.driver.find_element_by_partial_text(partial_text);
            message = self.feedback.feedback_action_ok(step);
            message['element'] = element;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def find_elements_by_partial_text(self,param,ignore_error_handle = False):
        """
        for Sagittarius version 2005
        find elements by partial text
        :param param:
        :param ignore_error_handle:
        :return:
        """
        message = {};
        step = 'find elements by partial text:' + str(param.get('partial_text',None));
        partial_text = str(param.get('partial_text',None));
        try:
            elements = self.driver.find_elements_by_partial_text(partial_text);
            message = self.feedback.feedback_action_ok(step);
            message['elements'] = elements;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle)
        finally:
            return message;

    def find_element_by_class(self,param={},ignore_error_handle = False):
        """
        find element by class name on cuurent page.
        :param param:{'class':'xxx'}
        :return:the result of the action.
        """
        message = {};
        step = 'find element by class ' + str(param.get('class',None)) + ' on current page';
        class_name = str(param.get('class',None));
        try:
            element = self.driver.find_element(by=By.CLASS_NAME,value=class_name);
            message = self.feedback.feedback_action_ok(step);
            message['element'] = element;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def find_elements_by_class(self,param={},ignore_error_handle = False):
        """
        find all elements by class name on current view
        :param param:{'class':''}
        :return:result of the action .If it is ok, it will contain the elements
        """
        message = {};
        step = 'find all elements by class name ' + str(param.get('class',None)) + ' on current page';
        class_name = str(param.get('class',None));
        try:
            elements = self.driver.find_elements(by=By.CLASS_NAME,value=class_name);
            message = self.feedback.feedback_action_ok(step);
            message['elements'] = elements;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def find_elements_by_resource_id(self,param = {},ignore_error_handle = False):
        """
        find all elements buy resource id on current page
        :param param:{'resourceid':'xxxx'}
        :return:the result of the action. If the action is ok,the result will contain the elements object;
        """
        message = {};
        step = 'find all elements by resource id ' + param['resourceid'] + ' on current page';
        try:
            id = param['resourceid'];
            all_elements = self.driver.find_elements_by_id(id);
            message = self.feedback.feedback_action_ok(step);
            message['elements'] = all_elements;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def find_elements_by_text(self,param={},ignore_error_handle = False):
        """
        find all elements by text on current page
        :param param:{'text':'xxx'}
        :return:the result of the action.If it is ok,the result will contain elements
        """
        message = {};
        step = 'find all elements by text ' + param.get('text',None) + ' on current page';
        text = param.get('text',None);
        try:
            elements = self.driver.find_elements(by=By.NAME,value=text);
            message = self.feedback.feedback_action_ok(step);
            message['elements'] = elements;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def find_element_by_description(self,param={},ignore_error_handle=False):
        message = {};
        description = param.get('description')
        type = param.get('type')
        step = 'find element by description \'%s\' and type \'%d\''%(description,type)
        try:
            element = self.driver.find_element(by=By.DESC,value=description,type=type)
            message = self.feedback.feedback_action_ok(step)
            message['element'] = element
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message

    def scroll_from_element_to_element(self,param,ignore_error_handle = False):
        """scroll view from a element to another element.
        :param param:{'element_from':'xxxx','element_to':'xxxx'};
        :param ignore_error_handle:
        :return:the result of the action.It contains element object.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'scroll view from a element \'' +  param['resourceid_from'] + '\' to another element \'' + param['resourceid_to'];
        try:
            id_from = param['resourceid_from'];
            id_to = param['resourceid_to'];
            element_from = self.driver.find_element_by_id(id_from);
            element_to = self.driver.find_element_by_id(id_to);
            self.driver.scroll(element_from,element_to);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def drag_from_element_to_element(self,param,ignore_error_handle = False):
        """drag and drop view from a element to another element.
        :param param:{'resourceid_from':'xxxx','resourceid_to':'xxxx'};
        :param ignore_error_handle:
        :return:the result of the action.It contains element object.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'drag and drop from a element \'' + param['resourceid_from'] + '\' to another element \'' + param['resourceid_to'];
        try:
            id_from = param['resourceid_from'];
            id_to = param['resourceid_to'];
            element_from = self.driver.find_element_by_id(id_from);
            element_to = self.driver.find_element_by_id(id_to);
            self.driver.drag_and_drop(element_from,element_to);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def swipe_on_screen(self,param,ignore_error_handle=False):
        """swipe screen from one point to another point.
        :param param:{start_x:111,start_y:111,end_x:111,end_y:111};
        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'swipe from one point [' + str(param['start_x']) + ',' + str(param['start_y']) + '] to another point [' + str(param['end_x']) + ',' + str(param['end_y']) + ']' ;
        try:
            start_x = param['start_x'];
            start_y = param['start_y'];
            end_x = param['end_x'];
            end_y = param['end_y'];
            swipe_duration = param['duration'];
            self.driver.swipe(start_x,start_y,end_x,end_y,swipe_duration);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def flick_on_screen(self,param,ignore_error_handle=False):
        """
        flick on screen
        :param param:
        :param ignore_error_handle:
        :return:
        """
        message = {};
        start_x = param['start_x'];
        start_y = param['start_y'];
        end_x = param['end_x'];
        end_y = param['end_y'];
        step = 'flick from one point [' + str(param['start_x']) + ',' + str(param['start_y']) + '] to another point [' + str(param['end_x']) + ',' + str(param['end_y']) + ']' ;
        try:
            self.driver.flick(start_x,start_y,end_x,end_y);
            message = self.feedback.feedback_action_ok(step);
        except BasicAction,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def pinch_on_screen(self, param = {},ignore_error_handle = False):
        """pinch screen.
        :param param:{resourceid:xxx,percent:200,steps:50};
        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        id = param.get('resourceid');
        percent = param.get('percent',200);
        steps = param.get('steps',50);
        step = 'pinch on an element \'' + str(id) + '\' with percent \'' + str(percent) + '\' and steps \'' + str(steps) + '\'';
        try:
            element = self.driver.find_element_by_id(id);
            self.driver.pinch(element,percent,steps);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def zoom_on_screen(self,param = {},ignore_error_handle = False):
        """zoom screen.
        :param param:{resourceid:xxx,percent:200,steps:50};
        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        id = param.get('resourceid');
        percent = param.get('percent',200);
        steps = param.get('steps',50);
        step = 'zoom on an element \'' + str(id) + '\' with percent \'' + str(percent) + '\' and steps \'' + str(steps) + '\'';
        try:
            element = self.driver.find_element_by_id(id);
            self.driver.zoom(element,percent,steps);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def hide_keyboard(self,ignore_error_handle = False):
        """hide keybord.
        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'hide keyboard';
        try:
            if self.driver.is_ime_active():
                self.driver.hide_keyboard();
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def is_ime_popup(self,ignore_error_handle =False):
        """
        check if the ime popup
        :return:
        """
        message = {};
        step = 'is ime popup'
        try:
            isPopup = self.driver.is_ime_active();
            message = self.feedback.feedback_action_ok(step);
            message['is_popup'] = isPopup;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def press_keyevent(self,param = {},ignore_error_handle = False):
        """Press key.
        :param param:{'keycode':123};
        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'press key code \'' + str(param.get('keycode')) + '\'';
        keycode = param.get('keycode');
        try:
            self.driver.press_keycode(keycode);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def press_home(self,ignore_error_handle = False):
        """
        press home hardkey
        :return:
        """
        message = {};
        step = 'press HOME key'
        try:
            self.driver.press_keycode(3);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def press_power(self,ignore_error_handle = False):
        """
        press power hardkey
        :return:
        """
        message = {};
        step = 'press POWER key'
        try:
            self.driver.press_keycode(26);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def press_volume_up(self,ignore_error_handle = False):
        """
        press volume up hardkey
        :return:
        """
        message = {};
        step = 'press VOLUME UP key'
        try:
            self.driver.press_keycode(24);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def press_volume_down(self,ignore_error_handle = False):
        """
        press volume down hardkey
        :return:
        """
        message = {};
        step = 'press VOLUME DOWN key';
        try:
            self.driver.press_keycode(25);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def press_back(self,ignore_error_handle = False):
        """
        press back hardkey
        :return:
        """
        message = {};
        step = 'press BACK key';
        try:
            self.driver.press_keycode(4);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def press_menu(self,ignore_error_handle = False):
        """
        press menu key
        :return:
        """
        message = {};
        step = 'press MENU key';
        try:
            self.driver.press_keycode(82);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def press_recent(self,ignore_error_handle = False):
        """
        press recent hardkey
        :return:
        """
        message = {};
        step = 'press RECENT key';
        try:
            self.driver.press_keycode(187);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def long_press_keyevent(self,param = {},ignore_error_handle = False):
        """long press key.
        :param param:{'keycode':123};
        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'long press key code \'' + str(param.get('keycode')) + '\''
        keycode = param.get('keycode');
        try:
            self.driver.long_press_keycode(keycode);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    @property
    def get_current_activity_name(self,ignore_error_handle = False):
        """get current activity name on device
        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'get current activity name';
        try:
            activity_name = self.driver.current_activity;
            message = self.feedback.feedback_action_ok(step);
            message['activity'] = activity_name;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(self,str(e),ignore_error_handle);
        finally:
            return message;

    def start_activity(self,param={},ignore_error_handle = False):
        """start activity by package and activity name
        :param param:{'package':'xxx','activity':'xxxx'}
        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'start activity by app package \'' + param.get('package') + '\' and activity name \'' +  param.get('activity') + '\'';
        package = param.get('package');
        activity = param.get('activity');
        try:
            self.driver.start_activity(package,activity);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return  message;

    def open_notification(self,ignore_error_handle = False):
        """open notification

        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'open notification';
        try:
            self.driver.open_notifications();
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    @property
    def get_network_connection_type(self,ignore_error_handle = False):
        """get current network connection type of device
        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'get network connection type';
        try:
            type = self.driver.network_connection;
            message = self.feedback.feedback_action_ok(step);
            message['network_type'] = type;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def set_network_connection_type(self,param={},ignore_error_handle = False):
        """set network connection type
        :param param:
        network type:
        0 (None)           | 0    | 0    | 0
        1 (Airplane Mode)  | 0    | 0    | 1
        2 (Wifi only)      | 0    | 1    | 0
        4 (Data only)      | 1    | 0    | 0
        6 (All network on) | 1    | 1    | 0
        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'set network connection type \'' + str(param.get('network_type',0)) + '\'';
        network_type = param.get('network_type',0);
        try:
            if network_type == 0:
                self.driver.set_network_connection(ConnectionType.NO_CONNECTION);
            elif network_type == 1:
                self.driver.set_network_connection(ConnectionType.AIRPLANE_MODE);
            elif network_type == 2:
                self.driver.set_network_connection(ConnectionType.WIFI_ONLY);
            elif network_type == 4:
                self.driver.set_network_connection(ConnectionType.DATA_ONLY);
            elif network_type == 6:
                self.driver.set_network_connection(ConnectionType.ALL_NETWORK_ON);
            else:
                self.driver.set_network_connection(ConnectionType.NO_CONNECTION);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def shake_device(self,ignore_error_handle = False):
        """shake device
        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'shake device';
        try:
            self.driver.shake();
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def set_orientation(self,param={},ignore_error_handle = False):
        """rotate device to PORTRAIT or LANDSCAPE mode;
        :param param:
        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'set device orientation to \'' + param.get('rotate','PORTRAIT') + '\'';
        rotate = param.get('rotate','PORTRAIT');
        try:
            self.driver.orientation = rotate;
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    @property
    def get_orientation(self,ignore_error_handle = False):
        """get orientation of the device;
        :param ignore_error_handle:
        :return:the result of the action.If it fail, it will return error message by "dict"
        """
        message = {};
        step = 'get device orientation';
        try:
            rotate = self.driver.orientation;
            message = self.feedback.feedback_action_ok(step);
            message['rotate'] = rotate;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def snake_move(self,param=(),duration = None,ignore_error_handle = False):
        """
        move on screen like a snake
        :param param:joints of snake
        :param duration:every step wait time of snake move
        :return: the result of the action
        """
        message = {};
        step = 'draw a snake on device with ' + str(len(param)) + ' joint';
        try:
            touch_action = TouchAction(self.driver);
            touch_action.snake_move(param,duration).release().perform();
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def snakes_move(self,param=(),duration = 1000,ignore_error_handle = False):
        """
        move on screen like some snake
        :param param:((({'x':1,'y':1},{'x':1,'y':1}),({'x':'1'},{'y':1}),({'x':1,'y':1},{'x':1,'y':1})),duration=1000)
        :param duration: the wait time of ver steps
        :return:the result of the action
        """
        message = {};
        step = 'draw ' + str(len(param)) + ' snakes on screen';
        multi_action = MultiAction(self.driver);
        try:
            snakes_count = len(param);# the count of the snakes
            for snakes_index in range(0,snakes_count):
                current_snake = param[snakes_index];
                current_snake_joints_count = len(current_snake);
                touch_action = TouchAction(self.driver);
                touch_action._add_action('press',touch_action._get_opts(None,current_snake[0]['x'],current_snake[0]['y'],duration));
                for current_snake_joints_index in range(1,current_snake_joints_count):
                    current_joint = current_snake[current_snake_joints_index];
                    touch_action._add_action('moveTo',touch_action._get_opts(None,current_joint['x'],current_joint['y'],duration));
                    touch_action._add_action('wait',{'ms':duration});
                touch_action.release();
                multi_action.add(touch_action)
            multi_action.perform();
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def wake_up(self,ignore_error_handle = False):
        """
        wake up android device
        :return:
        """
        message = {};
        step = 'wake up android device';
        try:
            self.driver.wake_up_android_device();
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def lock(self,ignore_error_handle = False):
        """
        lock android device
        :return:
        """
        message = {};
        step = 'lock android device'
        try:
            self.driver.lock_android_device();
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def is_screen_on(self,ignore_error_handle = False):
        """
        check if screen on
        :return:
        """
        message = {};
        step = 'check screen on';
        try:
            isScreenOn = self.driver.is_android_screen_on;
            message = self.feedback.feedback_action_ok(step);
            message['screen_on'] = isScreenOn;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def set_text_by_resource_id(self,param={},ignore_error_handle = False):
        """
        set text on textbox of device
        :param param:{'resoutceid':'xxx','text':'xxxx'}
        :return:the result of the action
        """
        message = {};
        step = 'set text \'' + str(param.get('text',None)) + '\' in textbox \'' + str(param.get('resourceid',None)) + '\' in current view';
        resource_id = str(param.get('resourceid',None));
        text = str(param.get('text',None));
        try:
            element = self.driver.find_element_by_id(resource_id);
            element.set_text(text);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def set_text_by_element(self,param={},ignore_error_handle = False):
        """
        set text by element
        :param param:
        :return:
        """
        message = {}
        step = 'set text with element'
        element = param.get('element',None);
        text = str(param.get('text',None));
        try:
            element.send_keys(text);
            message = self.feedback.feedback_action_ok(step)
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def clear_text_by_resource_id(self,param,ignore_error_handle = False):
        """
        clear the text on the element
        :return:
        """
        message = {};
        step = 'clear text of element which resource id is \'' +  str(param.get('resourceid',None));
        resource_id = str(param.get('resourceid',None));
        try:
           # element = self.driver.find_element_by_id(resource_id);
           # element.clear();
            self.driver.clear_text(resource_id);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def go_back_to_home(self,ignore_error_handle = False):
        """
        Go back to home
        :return:
        """
        message = {};
        step = 'go back to home';
        try:
            for step_index in range(1,10):
                self.driver.press_keycode(4);
            self.driver.press_keycode(3);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def install_app(self,param,ignore_error_handle = False):
        """
        install app
        :param param:
        :return:
        """
        message = {};
        app_path = str(param.get('app_path',None));
        step = 'install app \'' + app_path;
        try:
            self.driver.install_app(app_path);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def uninstall_app(self,param,ignore_error_handle = False):
        """
        uninstall app
        :param param:
        :return:
        """
        message = {};
        app_package = param.get('app_package');
        step = 'uninstall app \'' + app_package + '\'';
        try:
            self.driver.remove_app(app_package);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def isAppInstall(self,param,ignore_error_handle = False):
        """
        check if the app install
        :param param:
        :return:
        """
        message = {};
        app_package = str(param.get('app_package',None));
        step = 'check if the app \'' + app_package + '\' install';
        try:
            is_install = self.driver.is_app_installed(app_package);
            message = self.feedback.feedback_action_ok(step)
            message['is_install'] = is_install;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def take_android_screen_shoot(self,param,ignore_error_handle = False):
        """
        take screenshot
        :param param:
        :return:
        """
        message = {};
        store_path = str(param.get('path',None));
        store_name = str(param.get('name',None));
        step = ('take android screenshot and store it to \'%s\' with name \'%s\'')%(store_path,store_name);
        try:
            self.driver.screen_capture(store_path,store_name);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def pull_files_to_local(self,param,ignore_error_handle = False):
        """
        pull file or folder to local path,
        if the local path not exist ,it will create automatically.
        :param param:
        :return:
        """
        message = {};
        device_path = str(param.get('device_path',None));
        local_path = str(param.get('local_path',None));
        step = ('pull the file or folder on device \'%s\' to local \'%s\'')%(device_path,local_path);
        try:
           if os.path.isfile(local_path):
               dir = os.path.dirname(local_path);
               if not os.path.exists(dir):
                   os.mkdir(dir);
           else:
               if not os.path.exists(local_path):
                   os.mkdir(local_path)
           self.driver.pull_file_to_local(device_path,local_path);
           message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
           message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message

    def android_monkey(self,param,ignore_error_handle = False):
        """
        execute monkey test
        :param param:
        :return:
        """
        message = {};
        monkey_package = str(param.get('package',None));
        step = 'monkey test for package \'' + monkey_package + '\'';
        try:
            #self.driver.monkey_test(monkey_package);
            self.driver.android_monkey_test(monkey_package);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message

    def monkey(self,param,ignore_error_handle = False):
        """
        execute monkey test
        NOW IT IS FOR TOP3000 TEST
        :param param:
        :return:
        """
        message = {};
        monkey_package = str(param.get('package',None));
        monkey_ignore_crash = param.get('ignore_crash',None);
        monkey_ignore_anr = param.get('ignore_anr',None);
        monkey_ignore_security_exception = param.get('ignore_security_exception',None);
        monkey_kill_process_after_error = param.get('kill_process_after_error',None);
        monkey_throttle = param.get('throttle',None);
        monkey_step = param.get('step',None);
        monkey_log_folder_path = param.get('logFolderPath',None)
        monkey_app_label = param.get('app_label',None);
        step = 'execute monkey test for package \'' + monkey_package \
               + '\' with params \'--ignore-crashes\':' + str(monkey_ignore_crash) \
               + ',\'--ignore-timeouts\':' + str(monkey_ignore_anr) \
               + ',\'--ignore-security-exceptions\':' + str(monkey_ignore_security_exception) \
               + ',\'--kill-process-after-error\':' + str(monkey_kill_process_after_error) \
               + ',\'--throttle\':' + str(monkey_throttle) \
               + ',\'steps:\'' + str(monkey_step)
        # get monkey command
        monkey_command = 'adb shell monkey -p ' + monkey_package + ' --pct-anyevent 0';
        if monkey_ignore_crash:
            monkey_command = monkey_command + ' --ignore-crashes';
        if monkey_ignore_anr:
            monkey_command = monkey_command + ' --ignore-timeouts';
        if monkey_ignore_security_exception:
            monkey_command = monkey_command + ' --ignore-security-exceptions';
        monkey_command = monkey_command + ' --throttle ' + str(monkey_throttle) + ' -v -v -v ' + str(monkey_step);

        popen = subprocess.Popen(monkey_command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        crash_happen = False;
        anr_happen = False;
        while True:
            next_line = popen.stdout.readline()
            if next_line == '' and popen.poll() != None:
                break;
            else:
                if next_line.find('CRASH') != -1:
                    crash_happen = True
                    crash_popen = subprocess.Popen('adb logcat -d -v threadtime *:V',stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    crash_log_file = open(os.path.join(monkey_log_folder_path,monkey_app_label + ' CRASH.log'),'w')
                    while True:
                        next_line = crash_popen.stdout.readline()
                        if next_line == '' and crash_popen.poll() != None:
                            break;
                        else:
                            crash_log_file.write(next_line + '\n');
                    crash_log_file.close();
                if next_line.find('NOT RESPONDING') != -1:
                    anr_happen = True
                    anr_popen = subprocess.Popen('adb logcat -d -v threadtime *:V',stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    anr_log_file = open(os.path.join(monkey_log_folder_path,monkey_app_label + ' ANR.log'),'w')
                    while True:
                        next_line = anr_popen.stdout.readline()
                        if next_line == '' and anr_popen.poll() != None:
                            break;
                        else:
                            anr_log_file.write(next_line + '\n');
                    anr_log_file.close();
        if (not crash_happen) and (not anr_happen):
            message = self.feedback.feedback_action_ok(step);
        else:
            if crash_happen and anr_happen:
                message = self.feedback.feedback_action_fail(step,'CRASH and ANR happen',ignore_error_handle)
            if crash_happen and (not anr_happen):
                message = self.feedback.feedback_action_fail(step,'CRASH happen',ignore_error_handle)
            if (not crash_happen) and anr_happen:
                message = self.feedback.feedback_action_fail(step,'ANR happen',ignore_error_handle)

        return message;

    def android_logcat(self,param ,ignore_error_handle = False):
        """
        get android log
        :param param:
        :param ignore_error_handle:
        :return:
        """
        message = {};
        logType = str(param.get('log_type',None));
        logFileFolder = str(param.get('logFolder',None));
        logFileName = str(param.get('logName',None));
        step = 'get android log by type \'' + logType + '\'';
        try:
            if logType == 'default':
                if self.current_udid == None:
                    logcatCommand = 'adb logcat -d -v threadtime *:V';
                else:
                    logcatCommand = 'adb -s ' + self.current_udid + ' logcat -d -v threadtime *:V';
            elif logType == 'kernel':
                if self.current_udid == None:
                    logcatCommand = 'adb logcat -b kernel -d -v threadtime *:V';
                else:
                    logcatCommand = 'adb -s ' + self.current_udid + ' logcat -b kernel -d -v threadtime *:V';
            elif logType == 'radio':
                if self.current_udid == None:
                    logcatCommand = 'adb logcat -b radio -d -v threadtime *:V';
                else:
                    logcatCommand = 'adb -s ' + self.current_udid + ' logcat -b radio -d -v threadtime *:V';
            elif logType == 'events':
                if self.current_udid == None:
                    logcatCommand = 'adb logcat -d -v threadtime *:V';
                else:
                    logcatCommand = 'adb -s ' + self.current_udid +' logcat -d -v threadtime *:V';

            if not os.path.exists(logFileFolder):
                os.makedirs(logFileFolder)

            log_file_path = os.path.join(logFileFolder,logFileName);
            log_file = open(log_file_path,'w');
            log_popen = subprocess.Popen(logcatCommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            while True:
                next_line = log_popen.stdout.readline();
                if next_line == '' and log_popen.poll() != None:
                    break;
                else:
                    log_file.write(next_line);
            log_file.close();
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return  message;

    def image_validation(self,param,ignore_error_handle = False):
        """
        image_validation
        :param param:
        :return:
        """
        message = {};
        target_picture = param.get('target_picture',None);
        source_picture = param.get('source_picture',None);
        step = 'image validation source picture ' + str(source_picture) + ' with target picture ' + str(target_picture);
        try:
            value = validation.imageValidation.calc_similar_by_path(target_picture,source_picture);
            message = self.feedback.feedback_action_ok(step);
            message['similarity'] = value;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
            message['similarity'] = None
        finally:
            return message;

    def get_current_package(self,ignore_error_handle = False):
        """
        For Sagittatius version 2006
        get current package
        :param ignore_error_handle:
        :return:
        """
        message = {}
        step = 'get current package'
        try:
            package = self.driver.get_current_package();
            message = self.feedback.feedback_action_ok(step);
            message['package'] = package;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
            message['package'] = None
        finally:
            return message;

    def force_stop_app(self,param,ignore_error_handle = False):
        """
        For Sagittatius version 2006
        force stop app
        :param param:
        :param ignore_error_handle:
        :return:
        """
        message = {}
        package = str(param.get('package',None));
        step = 'force stop app ' + package;
        try:
            self.driver.force_stop_app(package);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def drag_and_drop(self,param,ignore_error_handle = False):
        """
        For Sagittatius version 2006
        drag a element to another element
        :param param:
        :param ignore_error_handle:
        :return:
        """
        message = {}
        origin_element = param.get('origin',None);
        destination_element = param.get('destination',None);
        step = 'drag a element to another element'
        try:
            self.driver.drag_and_drop(origin_element,destination_element);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def drag_and_drop_by_point(self,param,ignore_error_handle = False):
        """
        For Sagittatius version 2006
        drag from point to point
        :param param:
        :param ignore_error_handle:
        :return:
        """
        message = {}
        startX = param.get('startX');
        startY = param.get('startY');
        endX = param.get('endX');
        endY = param.get('endY');
        print 'start x:' + str(startX);
        print 'start y:' + str(startY);
        step = ('drag from point (\'%d\',\'%d\') to point (\'%s\',\'%s\')')%(startX,startY,endX,endY);
        try:
            self.driver.drag_and_drop_by_point(startX,startY,endX,endY);
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
        finally:
            return message;

    def wait_element_exist(self,param,ignore_error_handle = False):
        """
        Waits a specified length of time for a UI element to become visible.
        This method waits until the UI element becomes visible on the display, or until the timeout has elapsed.
        You can use this method in situations where the content that you want to select is not immediately displayed.
        For Sagittatius version 3000
        :param param:timeout the amount of time to wait (in milliseconds)
        :param ignore_error_handle:
        :return:true if the UI element is displayed, else false if timeout elapsed while waiting
        """
        message = {};
        timeout = param.get('timeout')
        resourceId = param.get('resourceid')
        step = ('waits \'%d\' sec for UI element \'%s\' to become visible')%(timeout,resourceId)
        try:
            exist = self.driver.wait_element_exist(resourceId,timeout)
            message = self.feedback.feedback_action_ok(step)
            message['exist'] = exist
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle)
            message['exist'] = False
        finally:
            return message

    def scroll_to_text(self,param,ignore_error_handle = False):
        """
        Performs a swipe up on the UI element until the requested text is visible or until swipe attempts have been exhausted.
        :param param:text	to look for
                     resourceid  the scroll UI element
        :param ignore_error_handle:
        :return:true if item us found else false
        """
        message = {};
        text = param.get('text')
        resourceid = param.get('resourceid')
        instance = param.get('instance')
        if instance is None:
            instance = 0
        step  = ('scroll UI element \'%s\' to \'%s\' with instance \'%s\'')%(text,resourceid,instance);
        try:
            scrollResult = self.driver.scroll_element_to_text(resourceid,text,instance);
            message = self.feedback.feedback_action_ok(step)
            message['scroll'] = scrollResult;
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle);
            message['scroll'] = False

        finally:
            return message

    def click_element_by_description(self,param,ignore_error_handle=False):
        """
        Click the element by description within different type
        :param param:DEFAULT = 0;START_WITH = 1;CONTAINS = 2;
        :param ignore_error_handle:
        :return:
        """
        message = {};
        description = param.get('description');
        type = param.get('type')
        step = ('click element by description \'%s\' with type \'%d\'')%(description,type);
        try:
            self.driver.clickElementWithDescription(description,type)
            message = self.feedback.feedback_action_ok(step);
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle)
        finally:
            return message

    def log_start(self):
        """
        Start logcat.
        :return:
        """
        logStorePath = self.driver.log_start(wholeTestFolder=self.mtbf_WholeTestFolder_Logcat,
                                             roundFolder=self.mtbf_RoundFolder,
                                             deviceID=self.current_udid if self.targetDevice==None else self.targetDevice,
                                             startTime=self.mtbf_TestCaseStartTime,
                                             currentLoop=self.mtbf_TestCaseCurrentLoop,
                                             scriptName=self.mtbf_TestCaseName,
                                             logStorePath=self.__getDeviceLogStorePath(self.targetDevice))
        return logStorePath

    def log_end(self):
        """
        End logcat
        :return:
        """
        self.driver.log_end()

    def take_screenshot_by_uiautomator(self,screenshotPath=None,screenshotName=None,ignore_error_handle=False):
        """
        take screenshot by uiautomator
        :return:
        """
        message = {}
        path = screenshotPath
        name = screenshotName
        step = 'Take screenshot {pic_name} and store it to {pic_path}'.format(pic_name=name,pic_path=path)
        try:
            self.driver.cap_screen_by_uiautomator(storePath=path,storeName=name)
            message = self.feedback.feedback_action_ok(step)
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle)
        finally:
            return message


    '''
    以下函数对应简易录制所需要的操作
    '''
    def click_pixel_on_screen(self,x=0,y=0,ignore_error_handle=False):
        """
        此API针对简易录制，对应动作不经过Appium server和通过Bootstrap实现。
        由adb 命令直接实现
        :param x:
        :param y:
        :return:
        """
        message = {}
        step = 'Click pixel {pixelX} {pixelY} on screen.'.format(pixelX=str(x),pixelY=str(y))
        try:
            adb_click_command = 'adb shell input tap {pixelX} {pixelY}'.format(pixelX = str(x),pixelY = str(y))
            result = os.system(adb_click_command)
            if result == 0:
                message = self.feedback.feedback_action_ok(step)
            else:
                message = self.feedback.feedback_action_fail(step,'Command return code is {code}'.format(code = str(result)),ignore_error_handle)
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle)
        finally:
            return message;

    def action_wait(self,millisecond=0,ignore_error_handle=False):
        """
        此方法对应简易录制，动作与动作之间的间隔时间
        :param millisecond:
        :param ignore_error_handle:
        :return:
        """
        message = {}
        step = 'Wait {time} millisecond'.format(time=millisecond)
        try:
            second = float(millisecond)/1000
            time.sleep(second)
            message = self.feedback.feedback_action_ok(step)
        except BaseException,e:
            message = self.feedback.feedback_action_fail(step,str(e),ignore_error_handle)
        finally:
            return message

    '''
    以上函数对应简易录制
    '''

    '''
    以下函数针对获取辅助设备相关操作
    '''
    def getSupportDevicesCount(self):
        return len(self.supportDevices)

    def getSupportDeviceId(self):
        pass;

    '''
    以上函数针对获取辅助设备相关操作
    '''




