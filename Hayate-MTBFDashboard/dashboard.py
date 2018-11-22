# -*- coding: utf-8 -*-
import os
import sys
import time
from shutil import copy, move, copytree
from xml.dom.minidom import  parse
import django
from django.template.loader import get_template
from django.template import Context
from Config import DashboardConfig
from ADB.adbHelper import ADB as AndroidADB
from HTML.htmlHelper import html
import json
sys.path.append("..")
from Sagittarium.Log.LogHelper import Logger
from Sagittarium.CustomException.DashboardException import TargetRecordFolderNotExistException
from Device.device import AndroidDevice
from Device.supportDevice import SupportDevice
from Sagittarium.CustomException.ConfigErrorException import ConfigFileNotExistException
from Sagittarium.CustomException.ConfigErrorException import DeviceTagNotExistException
from Sagittarium.CustomException.ConfigErrorException import DeviceAttributeIsNotValid
from Sagittarium.CustomException.ConfigErrorException import SupportDeviceAtrributeIsNotValid
reload(sys)
sys.setdefaultencoding('utf8')

PARENT_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PARENT_PROJECT_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'Hayate-MTBFDashboard.settings'

def getDeviceUnderTest():
    devices = []
    xml = str(__file__).replace('Hayate-MTBFDashboard\dashboard.py',
                                'Hayate-MTBFServerUtility\ParserConfig\MultDevicesPBConfig.xml')
    Logger.debug(xml)
    if not os.path.exists(xml):
        raise ConfigFileNotExistException(xml)
    document = parse(xml)
    rootElement = document.documentElement
    # 获取测试设备
    deviceElements = rootElement.getElementsByTagName(DashboardConfig.CONFIG_XML_ELEMENT_DEVICE)
    if len(deviceElements) == 0:
        raise DeviceTagNotExistException()
    for deviceElement in deviceElements:
        supportDevices = []
        device = AndroidDevice()
        # 获取udid
        udid = deviceElement.getAttribute(DashboardConfig.CONFIG_XML_ATTRIBUTE_UDID)
        if udid == "":
            raise DeviceAttributeIsNotValid('udid')
        device.setUdid(udid)
        # 获取mappingid
        mappingid = deviceElement.getAttribute(DashboardConfig.CONFIG_XML_ATTRIBUTE_MAPPINGID)
        if mappingid == "":
            raise DeviceAttributeIsNotValid('mappingid')
        device.setMappingId(mappingid)
        # 获取log存储路径
        logStorePath = deviceElement.getAttribute(DashboardConfig.CONFIG_XML_ATTRIBUTE_LOGSTOREPATH)
        if logStorePath == "":
            raise DeviceAttributeIsNotValid("logStorePath")
        device.setLogStorePath(logStorePath)
        # 辅助设备
        supportDeviceElements = deviceElement.getElementsByTagName(
            deviceElement.getAttribute(DashboardConfig.CONFIG_XML_ELEMENT_SUPPORTDEVICE))
        if len(supportDeviceElements) > 0:
            for supportDeviceElement in supportDeviceElements:
                supportDevice = SupportDevice()
                # 辅助设备id
                supportDeviceUdid = supportDeviceElement.getAttribute(DashboardConfig.CONFIG_XML_ATTRIBUTE_UDID)
                if supportDeviceUdid == "":
                    raise SupportDeviceAtrributeIsNotValid("udid")
                supportDevice.setUdid(supportDeviceUdid)
                # 辅助设备映射id
                supportDeviceMappingId = supportDeviceElement.getAttribute(
                    DashboardConfig.CONFIG_XML_ATTRIBUTE_MAPPINGID)
                if supportDeviceMappingId == "":
                    raise SupportDeviceAtrributeIsNotValid("mappingid")
                supportDevice.setMappingUdid(supportDeviceMappingId)
                # 辅助设备存储Log路径
                supportDeviceLogStorePath = supportDeviceElement.getAttribute(
                    DashboardConfig.CONFIG_XML_ATTRIBUTE_LOGSTOREPATH)
                if supportDeviceLogStorePath == "":
                    raise SupportDeviceAtrributeIsNotValid("logStorePath")
                supportDevice.setLogStorePath(supportDeviceLogStorePath)
                supportDevices.append(supportDevice)
        device.setSupportDevices(supportDevices)
        devices.append(device)
    return devices

if __name__ == "__main__":
    try:
        # 通过解析xml文件获取设备对象
        connected_devices = getDeviceUnderTest()

        adb = AndroidADB()
        # Root 设备
        adb.rootDevices(connected_devices)

        # 创建MTBF测试数据总文件夹
        mtbfDashboardFolderPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                               DashboardConfig.FOLDER_NAME.format(
                                                   time=time.strftime('%Y%m%d%H%M%S', time.localtime())))
        if not os.path.exists(mtbfDashboardFolderPath):
            os.makedirs(mtbfDashboardFolderPath)
            Logger.info("Create dashboard folder {folder} ok".format(folder=mtbfDashboardFolderPath))

        # 导出Dropbox 日志
        adb.pullDropboxFiles(connected_devices, mtbfDashboardFolderPath)

        # 复制Record文件
        Logger.info('Start move record files.')
        wholeMTBFFolder = sys.argv[1]
        for device in connected_devices:
            useMappingId = False
            if not device.mappingid == "None":
                Logger.info("Deivce {id} has mappingid {mappingid}.So use mappingid name record folder".format(id=device.id,mappingid=device.mappingid))
                useMappingId = True
                recordPath = os.path.join(mtbfDashboardFolderPath, 'record',device.mappingid)
            else:
                Logger.info("Deivce {id} has no mappingid {mappingid}.So use id name record folder".format(id=device.id,mappingid=device.mappingid))
                useMappingId = False
                recordPath = os.path.join(mtbfDashboardFolderPath, 'record',device.id)
            if not os.path.exists(recordPath):
                os.makedirs(recordPath)
            folders = os.listdir(wholeMTBFFolder)
            targetPath = None
            # 检索record folders
            for folder in folders:
                if (device.mappingid if useMappingId else device.id) in folder:
                    targetPath = os.path.join(wholeMTBFFolder, folder)
                    break;
            if targetPath == None:
                raise TargetRecordFolderNotExistException(value=(device.mappingid if useMappingId else device.id))
            roundFolders = os.listdir(targetPath)
            for folder in roundFolders:
                move(os.path.join(targetPath, folder), recordPath)
            device.setLocalRecordPath(recordPath)
        Logger.info('Move record files OK.')

        # 导出Logcat
        adb.pullLogcatFiles(connected_devices, mtbfDashboardFolderPath)

        # 解析数据
        for device in connected_devices:
            Logger.info('Device {id} parse data.'.format(id=device.id))
            device.parseData()
            Logger.info('Deivce {id} parse error.'.format(id=device.id))
            device.parseError()
    except BaseException,e:
        Logger.error(str(e))
        sys.exit(1)


    # 测试数据生成
    # for device in connected_devices:
    #     print 'Device {id} data:'.format(id=device.id)
    #     print 'Crash:\n'
    #     print device.crash
    #     print 'Anr:\n'
    #     print device.anr
    #     print 'lowmem:\n'
    #     print device.lowmem
    #     print 'smv:\n'
    #     print device.smv
    #     print 'SystemRestart:\n'
    #     print device.systemRestart
    #     print 'Tombstones:\n'
    #     print device.tombstones
    #     print 'Watchdog:\n'
    #     print device.watchdog
    #     print 'Wtf:\n'
    #     print device.wtf
    #     print 'Total test time:' + str(device.totalTestTime)
    #     print 'Whole Pass rate:' + str(device.passrate)
    #     print 'Total test times:' + str(device.totalTestTimes)
    #     for case in device.testcase:
    #         print 'Testcase:' + str(case.name)
    #         print 'Total execute times:' + str(case.totalExecuteTimes)
    #         print 'Total pass times:' + str(case.passTimes)
    #         print 'Total fail times:' + str(case.failTimes)
    #         print 'Pass rate:' + str(case.passRate)
    #         print 'Total execute time:' + str(case.totleExecuteTime)

    htmlDataGenerator = html()
    try:
        django.setup()
        # 构建测试用例图标显示页面
        for device in connected_devices:
            useMappingId = True if not device.mappingid == "None" else False
            # 生成脚本测试明细
            for testcase in device.testcase:
                testcaseExecuteDetail_tamplate = get_template('basic_tables.html')
                testcaseExecuteDetail_html = testcaseExecuteDetail_tamplate.render(Context({'scripts':testcase.scripts,
                                                                                            'testcaseName':testcase.name}))
                testcaseExecuteDetail_html_path = os.path.join(mtbfDashboardFolderPath,
                                                               '{id}_{name}_detail.html'.format(id= device.mappingid if useMappingId else device.id,name=testcase.name))
                with open(testcaseExecuteDetail_html_path,'w') as testcaseDetailHtml:
                    testcaseDetailHtml.write(testcaseExecuteDetail_html)
                testcase.setExecuteDetailHtmlPath(testcaseExecuteDetail_html_path)

            # 生成错误明细
            # Crash
            crashDetail_tamplate = get_template('crash.html')
            crashDetail_html = crashDetail_tamplate.render(Context({'crash':device.crash,
                                                                    'udid':device.id,
                                                                    'errorCount':len(device.crash)}))
            crashDetail_html_path = os.path.join(mtbfDashboardFolderPath,'{id}_crash_detail.html'.format(id=device.mappingid if useMappingId else device.id))
            with open(crashDetail_html_path,'w') as errorDetailHtml:
                errorDetailHtml.write(crashDetail_html)
            device.setCrashHtmlPath(crashDetail_html_path)

            # Anr
            anrDetail_tamplate = get_template('anr.html')
            anrDetail_html = anrDetail_tamplate.render(Context({'anr':device.anr,
                                                                'udid':device.id,
                                                                'errorCount':len(device.anr)}))
            anrDetail_html_path = os.path.join(mtbfDashboardFolderPath,'{id}_anr_detail.html'.format(id=device.mappingid if useMappingId else device.id))
            with open(anrDetail_html_path,'w') as errorDetailHtml:
                errorDetailHtml.write(anrDetail_html)
            device.setAnrHtmlPath(anrDetail_html_path)

            # Lowmem
            lowmemDetail_tamplate = get_template('lowmem.html')
            lowmemDetail_html = lowmemDetail_tamplate.render(Context({'lowmem':device.lowmem,
                                                                      'udid':device.id,
                                                                      'errorCount':len(device.lowmem)}))
            lowmemDetail_html_path = os.path.join(mtbfDashboardFolderPath,'{id}_lowmem_detail.html'.format(id=device.mappingid if useMappingId else device.id))
            with open(lowmemDetail_html_path,'w') as errorDetailHtml:
                errorDetailHtml.write(lowmemDetail_html)
            device.setLowMemHtmlPath(lowmemDetail_html_path)

            # Smv
            smvDetail_tamplate = get_template('smv.html')
            smvDetail_html = smvDetail_tamplate.render(Context({'smv':device.smv,
                                                                'udid':device.id,
                                                                'errorCount':len(device.smv)}))
            smvDetail_html_path = os.path.join(mtbfDashboardFolderPath,'{id}_smv_detail.html'.format(id=device.mappingid if useMappingId else device.id))
            with open(smvDetail_html_path,'w') as errorDetailHtml:
                errorDetailHtml.write(smvDetail_html)
            device.setSMVHtmlPath(smvDetail_html_path)

            # System restart
            systemRestartDetail_tamplate = get_template('systemRestart.html')
            systemRestartDetail_html = systemRestartDetail_tamplate.render(Context({'systemRestart':device.systemRestart,
                                                                                    'udid':device.id,
                                                                                    'errorCount':len(device.systemRestart)}))
            systemRestartDetail_html_path = os.path.join(mtbfDashboardFolderPath,'{id}_SystemRestart_detail.html'.format(id=device.mappingid if useMappingId else device.id))
            with open(systemRestartDetail_html_path,'w') as errorDetailHtml:
                errorDetailHtml.write(systemRestartDetail_html)
            device.setSystemRestartHtmlPath(systemRestartDetail_html_path)

            # Tombstones
            tombstonesDetail_tamplate = get_template('tombstones.html')
            tombstonesDetail_html = tombstonesDetail_tamplate.render(Context({'tombstones':device.tombstones,
                                                                              'udid':device.id,
                                                                              'errorCount':len(device.tombstones)}))
            tombstonesDetail_html_path = os.path.join(mtbfDashboardFolderPath,'{id}_Tombstones_detail.html'.format(id=device.mappingid if useMappingId else device.id))
            with open(tombstonesDetail_html_path,'w') as errorDetailHtml:
                errorDetailHtml.write(tombstonesDetail_html)
            device.setTombstonesHtmlPath(tombstonesDetail_html_path)

            # Watchdog
            watchdogDetail_tamplate = get_template('watchdog.html')
            watchdogDetail_html = watchdogDetail_tamplate.render(Context({'watchdog':device.watchdog,
                                                                          'udid':device.id,
                                                                          'errorCount':len(device.watchdog)}))
            watchdogDetail_html_path = os.path.join(mtbfDashboardFolderPath,'{id}_Watchdog_detail.html'.format(id=device.mappingid if useMappingId else device.id))
            with open(watchdogDetail_html_path,'w') as errorDetailHtml:
                errorDetailHtml.write(watchdogDetail_html)
            device.setWatchdogHtmlPath(watchdogDetail_html_path)

            # Wtf
            wtfDetail_tamplate = get_template('wtf.html')
            wtfDetail_html = wtfDetail_tamplate.render(Context({'wtf':device.wtf,
                                                                'udid':device.id,
                                                                'errorCount':len(device.wtf)}))
            wtfDetail_html_path = os.path.join(mtbfDashboardFolderPath,'{id}_Wtf_detail.html'.format(id=device.mappingid if useMappingId else device.id))
            with open(wtfDetail_html_path,'w') as errorDetailHtml:
                errorDetailHtml.write(wtfDetail_html)
            device.setWtfHtmlPath(wtfDetail_html_path)

            # 生成测试用例执行明细
            testcaseList_tamplate = get_template('testcaseList.html')
            testcaseList_html = testcaseList_tamplate.render(Context({'device':device,
                                                                      'failTestcases':device.failTestcase}))
            testcaseList_html_path = os.path.join(mtbfDashboardFolderPath, '{id}_testcaseList.html'.format(id=device.mappingid if useMappingId else device.id))
            with open(testcaseList_html_path,'w') as testcaseHtml:
                testcaseHtml.write(testcaseList_html)
            device.setTestcaseListHtmlPath(testcaseList_html_path)

            # 生成图标界面
            testcase_tamplate = get_template('graphs.html')
            testcasesName,testcasesPassrate = htmlDataGenerator.getTestcasesInfo(device)
            testcasesConsumption = htmlDataGenerator.getConsumptionOfTestcases(device)
            testcasesPassTimes,testcasesFailTimes = htmlDataGenerator.getTestcasePassFailTimes(device)
            testcase_html = testcase_tamplate.render(Context({'TestcasesName':json.dumps(testcasesName),
                                                              'TestcasesPassrate':json.dumps(testcasesPassrate),
                                                              'TestcasesConsumption':json.dumps(testcasesConsumption),
                                                              'TestcasesPassTimes':json.dumps(testcasesPassTimes),
                                                              'TestcasesFailTimes':json.dumps(testcasesFailTimes),
                                                              'DeviceId':json.dumps({'id':device.id}),
                                                              'TestcasesNameNoJS':testcasesName,
                                                              'Testcases':device.testcase}))
            testcase_html_path = os.path.join(mtbfDashboardFolderPath,'{id}_testcase.html'.format(id=device.mappingid if useMappingId else device.id))
            with open(testcase_html_path,'w') as testcaseHtml:
                testcaseHtml.write(testcase_html)
            device.setTestcaseHtmlPath(testcase_html_path)

        # 构建测试数据概要界面
        index_tamplate = get_template('index.html')
        index_html = index_tamplate.render(Context({'devices': connected_devices,
                                                    'devicesCount':len(connected_devices)}))
        index_html_path = os.path.join(mtbfDashboardFolderPath, 'dashboard.html')
        with open(index_html_path, 'w') as mf:
            mf.write(index_html)

        # Copy css files
        cssFolder = os.path.join(mtbfDashboardFolderPath,'css')
        if not os.path.exists(cssFolder):
            os.makedirs(cssFolder)
        cssFiles = os.listdir(os.path.join(os.path.dirname(__file__),'mtbf_report_templates','css'))
        for file in cssFiles:
            copy(os.path.join(os.path.dirname(__file__),'mtbf_report_templates','css',file),cssFolder)

        # Copy fonts files
        fontsFolder = os.path.join(mtbfDashboardFolderPath,'fonts')
        if not os.path.exists(fontsFolder):
            os.makedirs(fontsFolder)
        fontsFiles = os.listdir(os.path.join(os.path.dirname(__file__),'mtbf_report_templates','fonts'))
        for file in fontsFiles:
            copy(os.path.join(os.path.dirname(__file__),'mtbf_report_templates','fonts',file),fontsFolder)

        # Copy image files
        imagesFolder = os.path.join(mtbfDashboardFolderPath,'images')
        if not os.path.exists(imagesFolder):
            os.makedirs(imagesFolder)
        imagesFiles = os.listdir(os.path.join(os.path.dirname(__file__),'mtbf_report_templates','images'))
        for file in imagesFiles:
            copy(os.path.join(os.path.dirname(__file__),'mtbf_report_templates','images',file),imagesFolder)


        # Copy js files
        jsFolder = os.path.join(mtbfDashboardFolderPath,'js')
        if not os.path.exists(jsFolder):
            os.makedirs(jsFolder)
        jsFiles = os.listdir(os.path.join(os.path.dirname(__file__),'mtbf_report_templates','js'))
        for file in jsFiles:
            copy(os.path.join(os.path.dirname(__file__),'mtbf_report_templates','js',file),jsFolder)

    except BaseException, e:
        print e