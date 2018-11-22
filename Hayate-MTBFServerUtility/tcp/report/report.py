__author__ = 'thundersoft'

import xlwt
import xlrd
from xlutils.copy import copy
import os

class Report():

    def __init__(self,path=None,name=None,deviceId =None):
        self.id = deviceId;
        self.reportPath = path;
        self.reportName = name;
        self.sheetName = '{id}_Details'.format(id=self.id)
        self.sheetName_passrate = '{id}_PassRate'.format(id=self.id)
        self.report = os.path.join(self.reportPath,self.reportName)
        self.__checkPath()
        self.reportExist = self.__checkReportExist()
        self.__createReport()
        pass

    def __checkPath(self):
        if not os.path.exists(self.reportPath):
            os.makedirs(self.reportPath)

    def __checkReportExist(self):
        return os.path.exists(self.report)

    def __createReport(self):
        if not self.reportExist:
            self.workbook = xlwt.Workbook();
            self.worksheet = self.workbook.add_sheet(self.sheetName)
            self.worksheet_passrate = self.workbook.add_sheet(self.sheetName_passrate)
            self.__write_title()
            self.__write_title_pr()
            self.workbook.save(self.report)

    # def __title_font(self):
    #     title_font = xlwt.Font();
    #     title_font.name = 'Times New Roman';
    #     title_font.bold = True;
    #     title_font.colour_index = 0;
    #     return title_font

    # def getUserStyle(self,forColor=0,backColor=1):
    #     pattern = xlwt.Pattern
    #     pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    #     pattern.pattern_fore_colour=forColor
    #     pattern.pattern_back_colour=backColor
    #     style = xlwt.XFStyle();
    #     style.pattern = pattern
    #     return style
    def __write_title_pr(self):
        self.worksheet_passrate.write(0,0,'Script name')
        self.worksheet.col(0).width = 20000;

        self.worksheet_passrate.write(0,1,'Total count')
        self.worksheet.col(1).width = 5000;

        self.worksheet_passrate.write(0,2,'Pass count')
        self.worksheet.col(2).width = 5000;

        self.worksheet_passrate.write(0,3,'Fail count')
        self.worksheet.col(3).width = 5000;

        self.worksheet_passrate.write(0,4,'Pass rate')
        self.worksheet.col(4).width = 5000;


    def __write_title(self):
        self.worksheet.write(0,0,'Script name');
        self.worksheet.col(0).width = 5000;

        self.worksheet.write(0,1,'Device ID');
        self.worksheet.col(1).width = 5000;

        self.worksheet.write(0,2,'Result');
        self.worksheet.col(2).width = 5000;

        self.worksheet.write(0,3,'Error Info');
        self.worksheet.col(3).width = 5000;

        self.worksheet.write(0,4,'OK Info');
        self.worksheet.col(4).width = 5000;

        self.worksheet.write(0,5,'Execute detail');
        self.worksheet.col(5).width = 5000;

        self.worksheet.write(0,6,'Start time');
        self.worksheet.col(6).width = 5000;

        self.worksheet.write(0,7,'End time');
        self.worksheet.col(7).width = 5000;

        self.worksheet.write(0,8,'Role');
        self.worksheet.col(8).width = 5000;

    def __open_report(self,isPassRate=False):
        if not isPassRate:
            excel = xlrd.open_workbook(self.report,formatting_info=True)
            sheet = excel.sheet_by_name(self.sheetName)
            return excel,sheet
        else:
            excel = xlrd.open_workbook(self.report,formatting_info=True)
            sheet = excel.sheet_by_name(self.sheetName_passrate)
            return excel,sheet


    """
    Write pass rate data
    """
    def writePRInfo(self,data=None):
        excel,sheet = self.__open_report(isPassRate=True)
        tmpReport = copy(excel)
        rows = sheet.nrows
        tmpSheet = tmpReport.get_sheet(1)
        isFound = False
        targetRow = 1;
        for currentRow in xrange(0,rows):
            if str(sheet.cell(currentRow,0).value) == data['script']:
                isFound = True
                targetRow = currentRow
                break
        if not isFound:
            tmpSheet.write(rows,0,data['script'])
            tmpSheet.write(rows,1,1);
            tmpSheet.write(rows,2,float(1) if data['result'] else float(0));
            tmpSheet.write(rows,3,float(0) if data['result'] else float(1));
            tmpSheet.write(rows,4,float(1) if data['result'] else float(0));
        else:
            oldTotalCount = int(sheet.cell(targetRow,1).value)
            newTotalCount = oldTotalCount + 1
            oldPassCount = int(sheet.cell(targetRow,2).value)
            newPassCount = oldPassCount + 1 if data['result'] else oldPassCount
            oldFailCount = int(sheet.cell(targetRow,3).value)
            newFailCount = oldFailCount if data['result'] else oldFailCount + 1
            tmpSheet.write(targetRow,1,newTotalCount)
            tmpSheet.write(targetRow,2,newPassCount)
            tmpSheet.write(targetRow,3,newFailCount)
            tmpSheet.write(targetRow,4,"%.3f" %(float(newPassCount)/float(newTotalCount)));
        tmpReport.save(self.report)


    def writeStartInfo(self,scriptName=None,deviceID=None,startTime=None,step=None,deviceRole=None):
        excel,sheet=self.__open_report()
        currentRows= sheet.nrows
        tmpReport = copy(excel)
        tmpSheet = tmpReport.get_sheet(0)
        tmpSheet.write(currentRows,0,scriptName);
        tmpSheet.write(currentRows,1,deviceID)
        tmpSheet.write(currentRows,6,startTime)
        newStep = '{old}\n{new}'.format(old="",new=step)
        tmpSheet.write(currentRows,5,newStep)
        tmpSheet.write(currentRows,8,deviceRole)
        tmpReport.save(self.report)

    def writeEndInfo(self,endTime=None,step=None):
        excel,sheet=self.__open_report()
        currentRows= sheet.nrows
        tmpReport = copy(excel)
        tmpSheet = tmpReport.get_sheet(0)
        tmpSheet.write(currentRows-1,7,endTime);
        oldStep = sheet.cell(currentRows-1,5).value
        newStep = '{old}\n{new}'.format(old=oldStep,new=step)
        tmpSheet.write(currentRows-1,5,newStep.decode('utf-8'))
        tmpReport.save(self.report)

    def writeErrorInfo(self,error=None):
        excel,sheet=self.__open_report()
        currentRows= sheet.nrows
        tmpReport = copy(excel)
        tmpSheet = tmpReport.get_sheet(0)
        oldError = sheet.cell(currentRows-1,3).value
        newStep = '{old}\n{new}'.format(old=oldError,new=error)
        tmpSheet.write(currentRows-1,3,newStep.decode('utf-8'))
        tmpReport.save(self.report)

    def writeResultInfo(self,result=None):
        excel,sheet=self.__open_report()
        currentRows= sheet.nrows
        tmpReport = copy(excel)
        tmpSheet = tmpReport.get_sheet(0)
        if not result:
            tmpSheet.write(currentRows-1,2,result)
        else:
            tmpSheet.write(currentRows-1,2,result)
        tmpReport.save(self.report)

    def writeStepInfo(self,step=None):
        excel,sheet=self.__open_report()
        currentRows= sheet.nrows
        tmpReport = copy(excel)
        tmpSheet = tmpReport.get_sheet(0)
        oldStep = sheet.cell(currentRows-1,5).value
        newStep = '{old}\n{new}'.format(old=oldStep,new=step)
        tmpSheet.write(currentRows-1,5,newStep.decode('utf-8'))
        tmpReport.save(self.report)

    def writeOKInfo(self,ok=None):
        excel,sheet=self.__open_report()
        currentRows= sheet.nrows
        tmpReport = copy(excel)
        tmpSheet = tmpReport.get_sheet(0)
        tmpSheet.write(currentRows-1,4,ok)
        tmpReport.save(self.report)



