==================MTBF============================
如果你要使用TSRunner 进行MTBF测试，并获取相应的测试数据，请安装MTBF脚本编写规则进行编写

----------------------------------------------MTBF脚本模板---------------------------------------------------
# -*- coding: utf-8 -*-

# Import actions library
from Sagittarium.basicaction import BasicAction
import sys

def script():
    # Xpath:绝对路径标注控件
    # 对于xpath来说，节点索引是从1开始！
    basicAction.click_element_by_xpath({'xpath': "/hierarchy/"
                                                 "android.widget.FrameLayout[1]/"
                                                 "android.widget.LinearLayout[1]/"
                                                 "android.widget.FrameLayout[1]/"
                                                 "android.widget.LinearLayout[1]/"
                                                 "android.widget.LinearLayout[2]/"
                                                 "android.widget.FrameLayout[1]/"
                                                 "android.widget.Button"})

    # Xpath:相对路径标注控件
    # 控件所有属性均可标注控件，例如bounds
    basicAction.click_element_by_xpath({'xpath': "//*[contains(@bounds,'[540,284][720,401]')]"})

# actions end from here

if __name__ == '__main__':
    '''
    操作设备1（主设备）
    '''
    try:
        basicAction = BasicAction(__file__,isMTBFTestCase=True,systemArgs=sys.argv)
        basicAction.script_start(targetDevice=basicAction.current_udid)
        logStorePath = basicAction.log_start()
        script()
    except BaseException, e:
        basicAction.feedback.feedback_action_fail('', str(e))
    finally:
        basicAction.log_end();
        basicAction.script_end();
    '''
    操作设备2（辅助设备）
    '''
    try:
        basicAction.script_start(targetDevice=basicAction.supportDevice('SupportDevice1'))
        logStorePath = basicAction.log_start()
        script()
    except BaseException,e:
        basicAction.feedback.feedback_action_fail('',str(e))
    finally:
        basicAction.script_end()
    '''
    操作设备3（辅助设备）
    '''
    try:
        basicAction.script_start(targetDevice=basicAction.supportDevice('SupportDevice2'))
        logStorePath = basicAction.log_start()
        script()
    except BaseException, e:
        basicAction.feedback.feedback_action_fail('', str(e))
    finally:
        basicAction.log_end();
        basicAction.script_end();
----------------------------------------------MTBF脚本模板---------------------------------------------------

===============================启动MTBF测试============================================
1.脚本按照MTBF要求的格式进行编写。
2.在MultDevicesPBConfig.xml中进行配置。
3.打开Server1.bat
4.打开Server2.bat
5.打开PlaybackScript.bat

==============================获取MTBF测试报告=========================================
测试完成后，使用以下命令生成测试报告。（命令中的绝对路径请替换成你安装路径下的对应路径）
python E:\TSRunner\MTBF\Hayate-MTBFDashboard\dashboard.py E:\TSRunner\MTBF\Hayate-MTBFServerUtility\RecordMTBFTestCaseResult.20160526165648

"E:\TSRunner\MTBF\Hayate-MTBFServerUtility\RecordMTBFTestCaseResult.20160526165648" 此文件夹下保存有测试过程中的数据，每此开启MTBF测试都会生成这种文件夹。

