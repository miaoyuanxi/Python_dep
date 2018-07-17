#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os,sys,subprocess,string,logging,time,shutil
import glob
import logging
import codecs
import configparser
import json
import gc
import xml.etree.ElementTree as ET
import re

from MayaPlugin import MayaPlugin
from Maya import Maya
from CommonUtil import RBCommon as CLASS_COMMON_UTIL
from MayaUtil import RBMayaUtil as CLASS_MAYA_UTIL
from imp import reload
reload(sys)

class AnalyzeMaya(Maya):
    def __init__(self,**paramDict):
        Maya.__init__(self,**paramDict)
        self.format_log('AnalyzeMaya.init','start')
        for key,value in self.__dict__.items():
            self.G_DEBUG_LOG.info(key+'='+str(value))
        self.format_log('done','end')
        self.CG_VERSION =self.G_CG_CONFIG_DICT['cg_version']
        self.G_CUSTOM_CONFIG_NAME ='CustomConfig.py'
        self.tips_info_dict = {}

    def maya_cmd_callback(self, my_popen, my_log):
        index = 0
        while my_popen.poll() is None:
            result_line = my_popen.stdout.readline().strip()
            result_line = result_line.decode(sys.getfilesystemencoding())
            # result_line = result_line.decode('utf-8')
            if result_line == '':
                continue
            CLASS_COMMON_UTIL.log_print(my_log, result_line)

            if "Reference file not found" in result_line:
                index += 1
                self.writing_error(25009, result_line)

            # if "open maya file ok." in result_line and index != 0:
            #     if "mayabatch.exe" in sys.executable.lower():
            #         sys.stdout.flush()
            #         time.sleep(0.2)
            #         CLASS_MAYA_UTIL.killMayabatch(self.G_DEBUG_LOG)
            #         return 0
            #     else:
            #         CLASS_MAYA_UTIL.kill_children()
            #     sys.stdout.flush()
            #     time.sleep(0.2)
            #     sys.exit(55555)
            #     CLASS_COMMON_UTIL.log_print(my_log,'\n\n-------------------------------------------End maya program-------------------------------------------\n\n')
            #     break

    def writing_error(self, error_code, info=""):
        error_code = str(error_code)
        r = re.findall(r"Reference file not found.+?: +(.+)", info, re.I)
        if error_code in self.tips_info_dict:
            if isinstance(self.tips_info_dict[error_code], list) and len(self.tips_info_dict[error_code]) > 0 and \
                            self.tips_info_dict[error_code][0] != info:
                if r:
                    info = r[0]
                error_list = self.tips_info_dict[error_code]
                error_list.append(info)
                self.tips_info_dict[error_code] = error_list
        else:
            if type(info) == str and info != "":
                if r:
                    self.tips_info_dict["25009"] = [r[0]]
                else:
                    self.tips_info_dict[error_code] = [info]
            else:
                self.tips_info_dict[error_code] = []


    def write_tips_info(self):
        info_file_path = os.path.dirname(self.G_TIPS_JSON)
        print ("write info_2 to tips.json")
        if not os.path.exists(info_file_path):
            os.makedirs(info_file_path)
        try:
            info_file = self.G_TIPS_JSON
            if os.path.exists(self.G_TIPS_JSON):
                with open(info_file, 'r') as f:
                    json_src = json.load(f)
                    for i in self.tips_info_dict:
                        json_src[i] = self.tips_info_dict[i]
            else:
                json_src = self.tips_info_dict
            print (json_src)
            with open(info_file, 'w+') as f:
                f.write(json.dumps(json_src,indent=2))
        except Exception as err:
            print  (err)
            pass


    def RB_CONFIG(self):
        self.G_DEBUG_LOG.info('[Maya.RBconfig.start.....]')
        print("----------------------------------------config start ------------------------------------------")
        #kill maya       
        CLASS_MAYA_UTIL.killMayabatch(self.G_DEBUG_LOG)  #kill mayabatch.exe
        # ----------------set env  -------------------
        os.environ["MAYA_UI_LANGUAGE"] = "en_US"
        os.environ['MAYA_DISABLE_CIP'] = '1'
        os.environ['MAYA_DISABLE_CLIC_IPM'] = '1'
        os.environ['MAYA_DISABLE_CER'] = '1'
        if float(self.CG_VERSION)>=2016:
            os.environ['MAYA_OPENCL_IGNORE_DRIVER_VERSION'] = '1'
            os.environ['MAYA_VP2_DEVICE_OVERRIDE'] = 'VirtualDeviceDx11'
        if int(self.RENDER_LAYER_TYPE):
            os.environ['MAYA_ENABLE_LEGACY_RENDER_LAYERS'] = "0"
        else:
            os.environ['MAYA_ENABLE_LEGACY_RENDER_LAYERS'] = "1"
        # ----------------load maya plugin-------------------
        self.G_DEBUG_LOG.info('插件配置')
        if self.G_CG_CONFIG_DICT:           
            sys.stdout.flush()
            custom_config=os.path.join(self.G_NODE_MAYAFUNCTION,self.G_CUSTOM_CONFIG_NAME).replace('\\','/') 
            if self.G_NODE_MAYAFUNCTION:                 
                if os.path.exists(custom_config): 
                    sys.stdout.flush()
                    print("custom_config is: " + custom_config )               
                    sys.stdout.flush()
                else:
                    print("Can not find the CustomConfig file: %s." % custom_config)
            print("plugin path:")
            print(self.G_CG_CONFIG_DICT)
            sys.stdout.flush()
            maya_plugin=MayaPlugin(self.G_CG_CONFIG_DICT,[custom_config],self.G_USER_ID,self.G_TASK_ID,self.G_DEBUG_LOG)
            maya_plugin.config()           
            sys.stdout.flush()      
        print("----------------------------------------config end ------------------------------------------")
        self.G_DEBUG_LOG.info('[Maya.RBconfig.end.....]')
        
    def RB_RENDER(self):
        self.G_DEBUG_LOG.info('[maya.RBanalyse.start.....]')
        options = {}
        options["user_id"] = self.G_USER_ID
        options["task_id"] = self.G_TASK_ID
        options["cg_project"] = self.G_INPUT_PROJECT_PATH
        options["cg_file"] = self.G_INPUT_CG_FILE
        options["task_json"] = self.G_TASK_JSON
        options["asset_json"] = self.G_ASSET_JSON
        options["tips_json"] = self.G_TIPS_JSON
        options["cg_version"] = self.CG_VERSION
        options["cg_plugins"] = self.G_CG_CONFIG_DICT["plugins"]
        print("99999999999")
        self.G_DEBUG_LOG.info(options)
        mayabatch = ["C:/Program Files/Autodesk/Maya%s/bin/mayabatch.exe" % \
                     (options["cg_version"]),
                     "D:/Program Files/Autodesk/Maya%s/bin/mayabatch.exe" % \
                     (options["cg_version"]),
                     "E:/Program Files/Autodesk/Maya%s/bin/mayabatch.exe" % \
                     (options["cg_version"]),
                     "F:/Program Files/Autodesk/Maya%s/bin/mayabatch.exe" % \
                     (options["cg_version"]),
                     "D:/Alias/Maya%sx64/bin/mayabatch.exe" % (options["cg_version"])]

        mayabatch = [i for i in mayabatch if os.path.isfile(i)]
        if mayabatch:
            mayabatch = mayabatch[0]
        else:
            print("there no Maya%s" % options["cg_version"])
            sys.exit(555)

        if self.G_RENDER_OS== '0':
            mayabatch='/usr/autodesk/'+self.G_CG_VERSION+'-x64/bin/mayabatch.exe'
            if not os.path.exists(mayabatch):
                mayabatch='/usr/autodesk/'+self.G_CG_VERSION+'/bin/mayabatch.exe'

        mayabatch=mayabatch.replace('\\','/')
        # self.G_AN_MAYA_FILE=os.path.join(self.G_NODE_MAYASCRIPT,'Analyze.py').replace('\\','/')
        # analyse_cmd = "%s %s --ui %s --ti %s --proj %s --cgfile %s --taskjson %s --assetjson %s --tipsjson %s" %(mayaExePath,self.G_AN_MAYA_FILE,self.G_USER_ID,self.G_TASK_ID,self.G_INPUT_PROJECT_PATH,self.G_INPUT_CG_FILE,self.G_TASK_JSON,self.G_ASSET_JSON,self.G_TIPS_JSON)
        # print analyse_cmd
        str_options = re.sub(r"\\\\", r"/", repr(options))
        str_dir = self.G_NODE_MAYASCRIPT.replace("\\", "/")
        analyse_cmd = "\"%s\" -command \"python \\\"options=%s;" \
              "import sys;sys.path.insert(0, '%s');import Analyze;reload(Analyze);" \
              "Analyze.analyze_maya(options)\\\"" % \
              (mayabatch, str_options, str_dir)

        print(analyse_cmd)
        self.G_FEE_PARSER.set('render','start_time',str(int(time.time())))
        self.G_DEBUG_LOG.info("\n\n-------------------------------------------Start maya program-------------------------------------\n\n")
        # analyse_cmd = analyse_cmd.encode(sys.getfilesystemencoding())
        print("analyse cmd info:\n")
        self.G_DEBUG_LOG.info(analyse_cmd)
        analyze_code,analyze_result=CLASS_COMMON_UTIL.cmd(analyse_cmd,my_log=self.G_DEBUG_LOG,continue_on_error=True,my_shell=True,callback_func=self.maya_cmd_callback)
        print(analyze_code,analyze_result)
        print(self.tips_info_dict)
        if self.tips_info_dict:
            self.write_tips_info()
            self.G_DEBUG_LOG.info("write tips info_2 ok.")
        CLASS_MAYA_UTIL.kill_lic_all(my_log=self.G_DEBUG_LOG)        
        self.G_FEE_PARSER.set('render','end_time',str(int(time.time())))
        self.G_DEBUG_LOG.info('[maya.RBanalyse.end.....]')

