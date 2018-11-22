# -*- coding: utf-8 -*-
__author__ = '赵嘉俊'

REPORT_FOLDER_NAME_STR = 'report.[0-9]+_[0-9]+'
REPORT_CASE_LOGCAT_FOLDER_NAME_STR = '\[StartTime\]([0-9]+_[0-9]+)_\[Script\]([\S\s]+)'
REPORT_CASE_LOGCAT_LOOP_FOLDER_NAME_STR = 'Time\[([0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+)\]_ID\[([\S\s]+)\]_Loop\[([0-9]+)\]'

LOGCAT_FILE = 'Time\[([0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+)\]_ID\[([\S\s]+)\]_Type\[([\S\s]+)\]_Loop\[([0-9]+)\]'

DEVICE_ID_STR = '([\S\s]+)\tdevice'

DROPBOX_WTF_STR = '[\S\s]+_wtf@([0-9]+)'
DROPBOX_STRICT_STR = '[\S\s]+_strictmode@([0-9]+)'
DROPBOX_APP_CRASH_STR = '[\S\s]+_app_crash@([0-9]+)'
DROPBOX_ANR_STR = '[\S\s]+_app_anr@([0-9]+)'
DROPBOX_LOWMEM = '[\S\s]+_lowmem@([0-9]+)'
DROPBOX_TOMBSTONES = '[\S\s]+_TOMBSTONE@([0-9]+)'
DROPBOX_WATCHDOG = '[\S\s]+_watchdog@([0-9]+)'
DROPBOX_SYSTEM_RESTART = 'SYSTEM_RESTART@([0-9]+)'
DROPBOX_SYSTEM_BOOT = 'SYSTEM_BOOT@([0-9]+)'

DROPBOX_DETAIL_PROCESS_STR = 'Process: ([\S\s]+.[\S\s]+.[\S\s]+)'
DROPBOX_DETAIL_PACKAGES_STR = 'Package: ([\S\s]+.[\S\s]+.[\S\s]+)'
DROPBOX_DETAIL_BRIEF_STR = '\tat [\S\s]+'
