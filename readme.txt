==================MTBF============================
�����Ҫʹ��TSRunner ����MTBF���ԣ�����ȡ��Ӧ�Ĳ������ݣ��밲װMTBF�ű���д������б�д

----------------------------------------------MTBF�ű�ģ��---------------------------------------------------
# -*- coding: utf-8 -*-
__author__ = '�Լο�'

# Import actions library
from Sagittarium.basicaction import BasicAction
import sys

def script():
    # Xpath:����·����ע�ؼ�
    # ����xpath��˵���ڵ������Ǵ�1��ʼ��
    basicAction.click_element_by_xpath({'xpath': "/hierarchy/"
                                                 "android.widget.FrameLayout[1]/"
                                                 "android.widget.LinearLayout[1]/"
                                                 "android.widget.FrameLayout[1]/"
                                                 "android.widget.LinearLayout[1]/"
                                                 "android.widget.LinearLayout[2]/"
                                                 "android.widget.FrameLayout[1]/"
                                                 "android.widget.Button"})

    # Xpath:���·����ע�ؼ�
    # �ؼ��������Ծ��ɱ�ע�ؼ�������bounds
    basicAction.click_element_by_xpath({'xpath': "//*[contains(@bounds,'[540,284][720,401]')]"})

# actions end from here

if __name__ == '__main__':
    '''
    �����豸1�����豸��
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
    �����豸2�������豸��
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
    �����豸3�������豸��
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
----------------------------------------------MTBF�ű�ģ��---------------------------------------------------

===============================����MTBF����============================================
1.�ű�����MTBFҪ��ĸ�ʽ���б�д��
2.��MultDevicesPBConfig.xml�н������á�
3.��Server1.bat
4.��Server2.bat
5.��PlaybackScript.bat

==============================��ȡMTBF���Ա���=========================================
������ɺ�ʹ�������������ɲ��Ա��档�������еľ���·�����滻���㰲װ·���µĶ�Ӧ·����
python E:\TSRunner\MTBF\Hayate-MTBFDashboard\dashboard.py E:\TSRunner\MTBF\Hayate-MTBFServerUtility\RecordMTBFTestCaseResult.20160526165648

"E:\TSRunner\MTBF\Hayate-MTBFServerUtility\RecordMTBFTestCaseResult.20160526165648" ���ļ����±����в��Թ����е����ݣ�ÿ�˿���MTBF���Զ������������ļ��С�

