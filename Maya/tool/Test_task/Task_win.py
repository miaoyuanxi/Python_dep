# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys
import os
import time
import Task
import analysis_cfg_fox
import analysis_cfg_china
#import QDesktopServices
import k_mapping
from CommonUtil import RBCommon as CLASS_COMMON_UTIL

class k_Taskwindow(Task.Ui_MainWindow,QWidget):
    def __init__(self,parent=None):
        super(k_Taskwindow,self).__init__()
        self.setupUi(MainWindow)

        #设置tabwidget的宽度

        self.Mapping_tableWidget.setColumnWidth(1,330)

        self.Plugins_tableWidget.setColumnWidth(1,130)

        self.TextCMD.hide()
        self.RBgroupBox_layoutWidget.hide()


        #按钮功能设置
        self.IPkey.clicked.connect(self.add_cmdkey)
        self.Get_Button.clicked.connect(self.kGetcfg)


        self.Mapping_netuse.clicked.connect(self.knetuse)
        self.Mapping_add.clicked.connect(self.setBlankToMappingQTable)
        self.Mapping_reduce.clicked.connect(self.clearMappingQTableItem)

        self.Plugins_add.clicked.connect(self.setBlankToPluginQTable)
        self.Plugins_reduce.clicked.connect(self.clearPluginQTableItem)

        self.Close_Button.clicked.connect(self.kclose)
        self.Input_Button.clicked.connect(self.OpenInput)
        self.Output_Button.clicked.connect(self.OpenOutput)
        self.Customfile_Button.clicked.connect(self.OpenCustom_files)
        self.PreRender_Button.clicked.connect(self.OpenPrerender)

        self.Maya_Button.clicked.connect(self.excuteMaya)
        self.CMD_Button.clicked.connect(self.excuteCMD)
        #self.k_inputPath = sysPath['tiles_path']

        self.PlatformMode_CB.currentIndexChanged.connect(self.kchangeModel)

        self.C_function_path = ''
        self.custom_file = ''

        self.k_one = True
        self.k_ip_on = True



    def kchangeModel(self):
        "转换平台模式"

        if self.PlatformMode_CB.currentText() in ['Fox']:
            self.RBgroupBox_layoutWidget2.hide()
            self.RBgroupBox_layoutWidget.show()
        elif self.PlatformMode_CB.currentText() in ['China']:
            self.RBgroupBox_layoutWidget2.show()
            self.RBgroupBox_layoutWidget.hide()

    def kGetcfg(self):
        """根据用户ID 任务ID分析数据 """

        k_platform = ''

        k_taskID = self.TaskID_lineEdit.text()
        k_useID  = self.UserID_lineEdit.text()

        if self.PlatformMode_CB.currentText() in ['Fox']:
            k_platform_group= [self.W2rb,self.W9rb,self.GPUrb]
            for i in k_platform_group:
                if i.isChecked():
                    k_platform = i.objectName()
        elif self.PlatformMode_CB.currentText() in ['China']:
            k_platform_group = [self.c_W2rb, self.c_W3rb, self.c_W4rb, self.c_W9rb, self.c_GPUrb]
            for i in k_platform_group:
                if i.isChecked():
                    k_platform = i.objectName()



        #没有设置好 盘符 任务ID 和 用户ID  弹出报错
        if not k_platform or not k_taskID or not k_useID:
            self.msg('No specified Platform or ID')

        else:
            if self.PlatformMode_CB.currentText() in ['Fox']:
                # 实例 配置json脚本
                cfg = analysis_cfg_fox.analysisCfg(k_platform,k_taskID,k_useID)

            elif self.PlatformMode_CB.currentText() in ['China']:

                cfg = analysis_cfg_china.analysisCfg(k_platform, k_taskID, k_useID)


            if cfg.k_jsonerror:
                self.msg('cannot find cfg.json')

            else:
                #填入plugins数据
                Plugins = cfg.analysisPlugins()
                self.setItemToQTableWidget(self.Plugins_tableWidget,Plugins)
                print('Finish get Plugins analysis')

                #填入maya版本号
                Mayaver = cfg.analysisSoft()
                self.Version_lineEdit.setText(Mayaver)
                print('Finish get Mayaver analysis')

                #填入Mapping数据
                Mapping = cfg.analysisMapping()
                self.setItemToQTableWidget(self.Mapping_tableWidget, Mapping)
                print('Finish get Mapping analysis')

                Aspath= cfg.analysisPath()
                #maya文件目录
                self.k_inputPath  = Aspath[0]
                #maya输出图片目录
                self.k_outputPath = Aspath[1]
                #自定义文件夹目录
                self.k_custompath = Aspath[2]
                #prerender文件夹目录
                self.C_script_path = Aspath[3]
                #B盘路径
                self.B_path = Aspath[4]
                print('Finish get Path analysis')

                if self.PlatformMode_CB.currentText() in ['Fox']:
                    #自定义function的路径 (mayaplugin路径,自定义py文件路径)
                    self.C_function_path = cfg.C_function_path
                    print(self.C_function_path)
                    self.function_path = cfg.function_path
                    print(self.function_path)

                    #自定义文件路径
                    self.custom_file = os.path.normpath(os.path.join(self.C_function_path,'CustomConfig.py'))
                    print('Finish get Fox customfile')

                elif self.PlatformMode_CB.currentText() in ['China']:
                    #自定义function的路径 (mayaplugin路径,自定义py文件路径)

                    self.function_path = cfg.function_path
                    print(self.function_path)

                    #自定义文件路径
                    self.custom_file = os.path.normpath(os.path.join(self.B_path,'custom_config',\
                                                                     k_useID,'RayvisionCustomConfig.py'))
                    print('Finish get China customfile')

                    #dirmap的字典
                    self.k_dirmap = ''
                    if 'mappings' in cfg.server_info:
                        self.k_dirmap = cfg.server_info['mappings']
                        print(self.k_dirmap)


    def OpenInput(self):
        """ Input按钮功能 """
        #QDesktopServices.openUrl(QUrl(self.k_inputPath))
        if os.path.exists(self.k_inputPath):
            os.startfile(self.k_inputPath)
        else:
            self.msg('%s path is not exists' %self.k_inputPath)

    def OpenOutput(self):
        """ Output按钮功能 """
        if os.path.exists(self.k_outputPath):
            os.startfile(self.k_outputPath)
        else:
            #不存在路径时 弹出窗口
            self.msg('%s path is not exists' %self.k_outputPath)


    def OpenCustom_files(self):
        """Preferences按钮功能"""
        if os.path.exists(self.k_custompath):
            os.startfile(self.k_custompath)
        else:
            self.msg('%s path is not exists' %self.k_custompath)

    def OpenPrerender(self):
        """prerender按钮功能"""
        if os.path.exists(self.C_script_path):
            os.startfile(self.C_script_path)
        else:
            self.msg('%s path is not exists' %self.C_script_path)

    def knetuse(self):
        """根据 mapping的内容 映射盘符"""
        self.getData()
        k_mapping.k_mapping(self.getMappingQtab)



    def kclose(self):
        """close按钮功能"""
        app.exit()


    def getData(self):
        """获取窗口内 Plugins Mapping maya版本 的数据"""

        #获取Plugins的数据
        self.getPluginsQtab = self.getItemfromQTableWidget(self.Plugins_tableWidget)
        print (self.getPluginsQtab)

        # 获取Mapping的数据
        self.getMappingQtab = self.getItemfromQTableWidget(self.Mapping_tableWidget)
        print (self.getMappingQtab)

        # 获取maya版本数据
        self.getMayaVer = self.Version_lineEdit.text()
        print (self.getMayaVer)

    def excuteBefore(self):
        #获取窗口内的信息
        self.getData()

        plugin_cfg_file = {u'cg_name':'Maya','cg_version':self.getMayaVer,'plugins':self.getPluginsQtab}


        if os.path.exists(self.C_function_path):
            print('import C_function_path')
            sys.path.append(self.C_function_path)
            #__import__('MayaPlugin')
            import MayaPlugin

        elif os.path.exists(self.function_path):
            print('import function_path')
            print (self.function_path)
            sys.path.append(self.function_path)
            #__import__('MayaPlugin')
            import MayaPlugin

        print('plugin_cfg_file is %s' % plugin_cfg_file)
        print('self.custom_file is %s' %self.custom_file)
        maya_plugin = MayaPlugin.MayaPlugin(plugin_cfg_file,[self.custom_file])
        maya_plugin.config()

    def excuteMaya(self):
        """执行maya按钮"""
        if self.k_one:
            self.excuteBefore()
            self.maya_dirmap()
            self.k_one = False

        cmd_str = r"C:\Program Files\Autodesk\Maya%s\bin\maya.exe" % (self.getMayaVer)
        #cmd_str = r"D:\Autodesk\Maya2017\bin\maya.exe"
        os.startfile('"' + cmd_str + '"')
        print ('startfile %s' %cmd_str)

    def excuteCMD(self):
        """执行cmd按钮"""
        self.TextCMD.show()

        CMDText = self.TextCMD.toPlainText()
        if CMDText:
            print ('excute %s' %CMDText)
            if self.k_one:
                self.excuteBefore()
                self.maya_dirmap()
                self.k_one = False

            CLASS_COMMON_UTIL.cmd(CMDText,continue_on_error=True, my_shell=True)


    def getItemfromQTableWidget(self,QTablename):
        """获取QTab内每个格子的数据，并组成字典，QTablename输入的数据为QTab的名字"""
        #获取行数与列数
        getRow=QTablename.rowCount()
        getcolumn = QTablename.columnCount()
        QTabData = {}
        for row in range(getRow):
            # 获取Qtab内的每个格子的数据
            for column in range(getcolumn):
                #先判断格子是否为空
                if QTablename.item(row, column):
                    getText = QTablename.item(row, column).text()
                    #print (getText)

                    #将数据放入字典
                    if not column and getText:
                        QTabData[getText] = ''
                    elif column == 1:
                        # 先判断格子是否为空
                        if QTablename.item(row, column-1):
                            getText_key = QTablename.item(row, column-1).text()
                            QTabData[getText_key] = getText

        return QTabData

    def setItemToQTableWidget(self,QTablename,cfg_dic):
        """为QTab的第一行加入数据，QTablename=QTab的名称，cfg_dic=数据字典 key=column 0 value=column 1"""
        for Plugin in cfg_dic:
            #将数据转成 QTableWidgetItem
            Plugins_Itemname    = QTableWidgetItem(Plugin)
            Plugins_Itemversion = QTableWidgetItem(cfg_dic[Plugin].replace('/','\\'))
            #将数据塞入第一行
            QTablename.insertRow(0)
            QTablename.setItem(0, 0, Plugins_Itemname)
            QTablename.setItem(0, 1, Plugins_Itemversion)
            #选择的时候 选择一整行
            QTablename.setSelectionBehavior(QAbstractItemView.SelectRows)

    def setBlankToMappingQTable(self):
        """加入空白行"""
        self.Mapping_tableWidget.insertRow(0)
        #选择的时候 选择一整行
        self.Mapping_tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)

    def clearMappingQTableItem(self):
        #self.k_tabWidget.clearContents()
        krow=self.Mapping_tableWidget.currentRow()
        self.Mapping_tableWidget.removeRow(krow)

    def setBlankToPluginQTable(self):
        """加入空白行"""
        self.Plugins_tableWidget.insertRow(0)
        #选择的时候 选择一整行
        self.Plugins_tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)

    def clearPluginQTableItem(self):
        #self.k_tabWidget.clearContents()
        krow=self.Plugins_tableWidget.currentRow()
        self.Plugins_tableWidget.removeRow(krow)

    def msg(self,message):
        kMessage = QMessageBox.information(self,  # 使用infomation信息框
                                        "出问题啦，请注意！！！",
                                        message,
                                        QMessageBox.Yes)

    def add_cmdkey(self):
        """添加IP 凭据"""
        keyplan1 = {'user': 'enfuzion', 'password': 'ruiyun2016'}
        keyplan2 = {'user': 'enfuzion', 'password': 'ruiyun2017'}
        keyplan3 = {'user': 'enfuzion', 'password': 'Raywing@host8'}

        keyplan4 = {'user': 'enfuzion', 'password': 'Raywing@host8-2'}
        keyplan5 = {'user': 'enfuzion', 'password': 'Raywing@host8-9'}
        keyplan6 = {'user': 'tdadmin', 'password': 'Ray@td852'}
        keyplan7 = {'user': 'administrator', 'password': 'Ruiyun@2016'}


        k_ipsort = {'w2': ['10.60.100.101','10.60.100.102','10.60.100.103','10.60.100.104','10.60.200.101', \
                           '10.60.200.102','10.60.200.103','10.60.200.104','10.60.100.201','10.60.100.202', \
                           '10.60.200.201','10.60.200.202'],\
                    'w3': ['10.30.100.101','10.30.100.102', '10.30.100.102', '10.30.100.201', '10.30.100.202'], \
                    'w4': ['10.40.100.101', '10.40.100.102', '10.40.100.103', '10.40.100.201', '10.40.100.202'], \
                    'w9': ['10.80.100.101','10.80.100.102', '10.80.100.103', '10.80.100.104', '10.70.242.101', '10.70.242.102', \
                           '10.80.100.201', '10.80.100.202', '10.80.100.203','10.70.242.201'],\
                    'gpu': ['10.90.100.101', '10.90.100.102', '10.90.100.103', '10.90.100.201', '10.90.100.202'],\
                    'B_plugins':['10.60.100.151','10.60.200.150','10.60.200.151','10.60.100.152','10.80.243.50','10.80.243.51',\
                                 '10.30.100.151','10.30.100.152','10.40.100.151','10.40.100.152','10.90.96.51']\
                    }

        self.k_cmdkey = {}

        for ip_key in k_ipsort:
            if ip_key in ['w2']:
                for ip_value in k_ipsort[ip_key]:
                    self.k_cmdkey.update({ip_value: keyplan4})
            if ip_key in ['gpu']:
                for ip_value in k_ipsort[ip_key]:
                    self.k_cmdkey.update({ip_value: keyplan1})
            if ip_key in ['w3', 'w4']:
                for ip_value in k_ipsort[ip_key]:
                    self.k_cmdkey.update({ip_value: keyplan3})
            if ip_key in ['w9']:
                for ip_value in k_ipsort[ip_key]:
                    self.k_cmdkey.update({ip_value: keyplan5})
            if ip_key in ['B_plugins']:
                for ip_value in k_ipsort[ip_key]:
                    self.k_cmdkey.update({ip_value: keyplan6})

        for k_ip in self.k_cmdkey:
            set_cmdkey = 'cmdkey /add:{0} /user:{1} /password:{2}'.format(k_ip,self.k_cmdkey[k_ip]['user'],self.k_cmdkey[k_ip]['password'])
            CLASS_COMMON_UTIL.cmd(set_cmdkey, continue_on_error=True, my_shell=True)

        print('添加全平台 地址凭据完毕!')

    def maya_dirmap(self):
        """在当前路径生成 usersetup.py文件"""
        current_file = os.path.realpath(__file__)
        current_path = os.path.dirname(current_file)
        k_usersetup_mel = os.path.normpath(os.path.join(current_path,'userSetup.py'))
        print(k_usersetup_mel)

        if self.k_dirmap:
            with open(k_usersetup_mel, "w") as f:
                f.write("import maya.cmds as cmds\n")
                f.write("cmds.dirmap( en=True )\n")
                for i in self.k_dirmap:
                    if not i.startswith("$"):
                        old_path = i
                        new_path = self.k_dirmap[i]
                        f.write("cmds.dirmap ( m=('%s' , '%s'))\n" % (old_path,
                                                                      new_path))
                f.write("print('Mapping successfully')\n")

            _MAYA_SCRIPT_PATH = os.environ.get('MAYA_SCRIPT_PATH')
            os.environ['MAYA_SCRIPT_PATH'] = (_MAYA_SCRIPT_PATH + r";" if _MAYA_SCRIPT_PATH else "") + current_path

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    kwin = k_Taskwindow()
    MainWindow.setWindowTitle(u'Maya 环境配置工具 v1.4')

    MainWindow.show()
    sys.exit(app.exec_())