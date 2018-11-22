# -*- coding: utf-8 -*-
__author__ = '赵嘉俊'

DASHBOARD_FOLDER_NAME = 'MTBF_DASHBOARD'

ANDROID_COMMAND_DEVICES = 'adb devices'
ANDROID_COMMNAD_PULL_DROPBOX_LOGS = 'adb -s {id} pull {remote} {local}'
ANDROID_COMMNAD_ROOT_DEVICE = 'adb -s {id} root'
ANDROID_COMMAND_REMOUNT_DEVICE = 'adb -s {id} remount'
ANDROID_COMMAND_PULL_MTBF_LOGS = 'adb -s {id} pull /sdcard/MTBF/Logs {local}'

FOLDER_NAME = '{time}'
FOLDER_NAME_DROPBOX = 'dropbox'
FOLDER_NAME_TOMBSTONES = 'tombstones'
FOLDER_NAME_ANR = 'anr'

RECORD_XML_DEVICE_TAG = 'Device'
RECORD_XML_UDID_ATTRIBUTE = 'udid'
RECORD_XML_MAPPINGID_ATTRIBUTE = 'mappingudid'
RECORD_XML_SCRIPT_TAG = 'Script'
RECORD_XML_ENDTIME_ATTRIBUTE = 'endTime'
RECORD_XML_LOOP_ATTRIBUTE = 'loop'
RECORD_XML_ROUND_ATTRIBUTE = 'round'
RECORD_XML_STARTTIME_ATTRIBUTE = 'startTime'
RECORD_XML_SCRIPTNAME_ATTRIBUTE = 'name'
RECORD_XML_SCRIPTRESULT_TAG = 'Result'
RECORD_XML_VALUE_ATTRIBUTE = 'value'
RECORD_XML_OKINFO_TAG = 'OKInfo'
RECORD_XML_ERRORINFO_TAG = 'ErrorInfo'
RECORD_XML_STEP_TAG = 'Step'
RECORD_XML_CONTENT_ATTRIBUTE = 'content'
RECORD_XML_STEPRESULT_ATTRIBUTE = 'stepResult'
RECORD_XML_LOG_TAG = 'Log'
RECORD_XML_FOLDER_ATTRIBUTE = 'folder'

CONFIG_XML_ELEMENT_DEVICE = 'Device'
CONFIG_XML_ELEMENT_SUPPORTDEVICE = 'SupportDevice '
CONFIG_XML_ATTRIBUTE_UDID = 'udid'
CONFIG_XML_ATTRIBUTE_MAPPINGID = 'mappingid'
CONFIG_XML_ATTRIBUTE_LOGSTOREPATH = 'logStorePath'


