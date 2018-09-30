#!/usr/bin/env python
#encoding:utf-8
# -*- coding: utf-8 -*-
import sys
import os
import shutil
import subprocess
from imp import reload
reload(sys)
# sys.setdefaultencoding('utf-8')
from MayaPlugin import PluginBase


class MtoaConfig():
    def __init__(self,clientInfo):
        self.MyLog(clientInfo)        
        self.cgName = clientInfo['cgName']
        self.cgVersion = clientInfo['cgVersion']
        self.pluginName = clientInfo['pluginName']
        self.pluginVersion = clientInfo['pluginVersion']
        self.plugins = clientInfo['plugins'] #dict
        self.userId = clientInfo['userId']
        self.taskId = clientInfo['taskId']
        self.pluginsPath = clientInfo['pluginsPath'] 
        self.configPath = clientInfo['configPath'] 
        self.messUpPath = clientInfo['messUpPath'] 
        self.json_path = os.path.join(self.pluginsPath,"envInfo.json")
        self.Base = PluginBase()

        self._PluginDir = os.path.join(self.Base.get_json_ini('Node_D',self.json_path),self.pluginName,'software',self.cgName + self.cgVersion + '_' + self.pluginName + self.pluginVersion).replace('\\','/')
        self.solidangle_LICENSE = self.Base.get_json_ini('solidangle_LICENSE',self.json_path)
        self.MyLog(self._PluginDir)
                
    def MyLog(self,message,extr="MtoaSetup"):      
        if str(message).strip() != "":
            print("[%s] %s"%(extr,str(message)))

    def reCreateMod(self):
        MODULES_LOCAL =  self._PluginDir  + r"/maya_root/modules"
        if not os.path.exists(MODULES_LOCAL):
            os.makedirs(MODULES_LOCAL)
        module_file = self._PluginDir  + r"/maya_root/modules/mtoa.mod"
        NEW_MAYAM_MTOA_PATH = self._PluginDir  +r"/maya_mtoa"
        NEW_MAYAM_MTOA_PATH = NEW_MAYAM_MTOA_PATH.replace("\\","/")
        ModulePathList = []
        line1 = "+ mtoa any " + NEW_MAYAM_MTOA_PATH
        line2 = "PATH +:= bin"
        line3 = "MAYA_CUSTOM_TEMPLATE_PATH +:= scripts/mtoa/ui/templates"
        line4 = "MAYA_SCRIPT_PATH +:= scripts/mtoa/mel"
        ModulePathList = [line1,line2,line3,line4]
        if os.path.exists(module_file):
            fp = open(module_file,'w')
            for line in ModulePathList:
                fp.writelines(line)  
                fp.write('\n')  
            fp.close() 
        ORG_DESCRIPT_FILE = NEW_MAYAM_MTOA_PATH + r"/arnoldRenderer.xml"
        NEW_DESCRIPT_DIR = self._PluginDir  + r"/maya_root/bin/rendererDesc"
        if not os.path.exists(NEW_DESCRIPT_DIR):
            os.makedirs(NEW_DESCRIPT_DIR)
        if os.path.exists(ORG_DESCRIPT_FILE):
            shutil.copy(ORG_DESCRIPT_FILE,NEW_DESCRIPT_DIR) 

    def setEnv(self):
        os.environ['solidangle_LICENSE'] = self.solidangle_LICENSE
        self.MyLog("arnold license local :" + os.environ['solidangle_LICENSE'] )
        _PATH_env=os.environ.get('PATH')
        _MAYA_RENDER_DESC_PATH=os.environ.get('MAYA_RENDER_DESC_PATH')
        _MAYA_MODULE_PATH=os.environ.get('MAYA_MODULE_PATH')
        _MAYA_SCRIPT_PATH=os.environ.get('MAYA_SCRIPT_PATH')
        os.environ['PATH'] = (_PATH_env + r";" if _PATH_env else "") + self._PluginDir  + r'/maya_mtoa/bin' 
        os.environ['MAYA_RENDER_DESC_PATH'] = (_MAYA_RENDER_DESC_PATH + r";" if _MAYA_RENDER_DESC_PATH else "") + self._PluginDir + r"/maya_root/bin/rendererDesc"
        os.environ['MAYA_MODULE_PATH'] = (_MAYA_MODULE_PATH + r";" if _MAYA_MODULE_PATH else "") + self._PluginDir + r"/maya_root/modules"
        os.environ['MAYA_SCRIPT_PATH'] = (_MAYA_SCRIPT_PATH + r";" if _MAYA_SCRIPT_PATH else "") + self._PluginDir + r"/maya_mtoa/scripts"    


def main(*args):
    infoDict = args[0]
    configPlugin = MtoaConfig(infoDict)
    configPlugin.reCreateMod()
    configPlugin.setEnv()
    configPlugin.MyLog( "set mtoa env finish")


if __name__ == '__main__':
    main()
    # os.system ("\""+MAYA_ROOT + "/bin/maya.exe"+"\"")