#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import string
import time
import shutil
import glob
import logging
import codecs
import pprint
import json
import re
import _winreg
import traceback
import platform
client_script= os.path.abspath(sys.path[0]+'/../submit/')
print(client_script)
sys.path.append(client_script)
from submitutil import *



class Maya():
    def __init__(self,options):
        self.PY_VERSION = sys.version_info[0]
        self.tips_info_dict = {}
        self.asset_info_dict = {}
        task_json_dict = options
        argument_json_dict = task_json_dict["argument_info"]
      
        self.argument_json_dict = argument_json_dict
        self.cg_file = argument_json_dict["cg_file"]
        self.plugins_dict = argument_json_dict['plugin_setting']['software_config']
        self.cg_version = self.plugins_dict["cg_version"]

        client_project_dir = argument_json_dict['client_setting']['client_project_dir']
        client_project_dir = client_project_dir.replace("\\", "/")

        self.task_json = client_project_dir + "/" + "task.json"
        if not os.path.exists(self.task_json):
            print("%s is not exists......."% self.task_json)
            sys.exit(555)
        self.asset_json = client_project_dir + "/" + "asset.json"
        self.tips_json = client_project_dir + "/" + "tips.json"
        self.upload_json = client_project_dir + "/" + "upload.json"
        
        self.my_log = None
        self.current_os = platform.system().lower()

        argument_json_path = argument_json_dict['argument_json']
        self.argument_json_path = argument_json_path.replace("\\", "/")

        analyze_script = os.path.abspath(sys.path[0] + '/../maya/')
        self.analyze_script_path = analyze_script.replace("\\", "/")

        client_script = os.path.abspath(sys.path[0] + '/../submit/')
        self.client_script = client_script.replace("\\", "/")


    def print_info(self, info):
        if self.PY_VERSION == 3:
            print(info)
        else:
            print("%s" % (self.unicode_to_str(info)))

    def print_info_error(self, info):
        if self.PY_VERSION == 3:
            print ("[Analyze Error]%s" % (info))
        else:
            print ("[Analyze Error]%s" % (self.unicode_to_str(info)))
     
    def writing_error(self, error_code, info=None):
        error_code = str(error_code)
        if type(info) == list:
            pass
        else:
            info = self.str_to_unicode(info)
        if error_code in self.tips_info_dict:
            if isinstance(self.tips_info_dict[error_code], list) and len(self.tips_info_dict[error_code]) > 0 and \
                            self.tips_info_dict[error_code][0] != info:
                error_list = self.tips_info_dict[error_code]
                error_list.append(info)
                self.tips_info_dict[error_code] = error_list
        else:
            if type(info) == unicode and info != "":
                r = re.findall(r"Reference file not found.+?: +(.+)", info, re.I)
                if r:
                    self.tips_info_dict["25009"] = [r[0]]
                else:
                    self.tips_info_dict[error_code] = [info]

            elif type(info) == list:
                self.tips_info_dict[error_code] = info
            else:
                self.tips_info_dict[error_code] = []
     
    def str_to_unicode(self, encode_str):
        if encode_str == None or encode_str == "" or encode_str == 'Null' or encode_str == 'null':
            encode_str = ""
            return encode_str
        elif isinstance(encode_str, unicode):
            return encode_str
        else:
            code = self.get_encode(encode_str)
            return encode_str.decode(code)
        
    def get_encode(self, encode_str):
        if isinstance(encode_str, unicode):
            return "unicode"
        else:
            for code in ["utf-8", sys.getfilesystemencoding(), "gb18030", "ascii", "gbk", "gb2312"]:
                try:
                    encode_str.decode(code)
                    return code
                except:
                    pass
  
    def unicode_to_str(self, str1, str_encode='system'):
        if str1 == None or str1 == "" or str1 == 'Null' or str1 == 'null':
            str1 = ""
            return str1
        elif isinstance(str1, unicode):
            try:
                if str_encode.lower() == 'system':
                    str1 = str1.encode(sys.getfilesystemencoding())
                elif str_encode.lower() == 'utf-8':
                    str1 = str1.encode('utf-8')
                elif str_encode.lower() == 'gbk':
                    str1 = str1.encode('gbk')
                else:
                    str1 = str1.encode(str_encode)
            except Exception as e:
                print ('[err]unicode_to_str:encode %s to %s failed' % (str1, str_encode))
                print (e)
        elif isinstance(str1, str):
            return str1
        else:
            print ('%s is not unicode ' % (str1))
        return str(str1)


    def bytes_to_str(self,str1, str_decode='default'):
        if not isinstance(str1, str):
            try:
                if str_decode != 'default':
                    str1 = str1.decode(str_decode.lower())
                else:
                    try:
                        str1 = str1.decode('utf-8')
                    except:
                        try:
                            str1 = str1.decode('gbk')
                        except:
                            str1 = str1.decode(sys.getfilesystemencoding())
            except Exception as e:
                print('[err]bytes_to_str:decode %s to str failed' % (str1))
                print(e)
        return str1

    def to_gbk(self, encode_str):
        if isinstance(encode_str, str):
            return encode_str
        else:
            code = self.get_encode(encode_str)
            return encode_str.decode(code).encode('GBK')


    def log_print(self, my_log, log_str):
        if my_log == None:
            print(log_str)
        else:
            my_log.info(log_str)


    def maya_cmd_callback(self, my_popen, my_log):
        index = 0
        while my_popen.poll() is None:
            result_line = my_popen.stdout.readline().strip()
            # result_line = result_line.decode(sys.getfilesystemencoding())
            result_line = self.bytes_to_str(result_line)
            result_line = self.to_gbk(result_line)
            if result_line == '':
                continue
            self.log_print(my_log, result_line)
            if "Reference file not found" in result_line:
                index += 1
                self.writing_error(25009, result_line)


    def check_maya_version(self, maya_file, cg_version):
        """Python2 version of check_version"""
        result = None
        maya_file = self.unicode_to_str(maya_file)
        if maya_file.endswith(".ma"):
            infos = []
            with open(maya_file, "r") as f:
                while 1:
                    line = f.readline()
                    if line.startswith("createNode"):
                        break
                    elif line.strip() and not line.startswith("//"):
                        infos.append(line.strip())
            file_infos = [i for i in infos if i.startswith("fileInfo")]
            for i in file_infos:
                if "product" in i:
                    r = re.findall(r'Maya.* (\d+\.?\d+)', i, re.I)
                    if r:
                        result = int(r[0].split(".")[0])
                if result == 2016 and "version" in i:
                    if "2016 Extension" in i:
                        result = 2016.5
            file_info_2013 = [i for i in infos if i.startswith("requires")]
            if result == 2013:
                for j in file_info_2013:
                    if "maya \"2013\";" in j:
                        result = 2013
                    else:
                        result = 2013.5
        elif maya_file.endswith(".mb"):
            with open(maya_file, "r") as f:
                info = f.readline()
            file_infos = re.findall(r'FINF\x00+\x11?\x12?K?\r?(.+?)\x00(.+?)\x00', info, re.I)
            for i in file_infos:
                if i[0] == "product":
                    result = int(i[1].split()[1])
            
                if result == 2016 and "version" in i[0]:
                    if "2016 Extension" in i[1]:
                        result = 2016.5
            file_info_2013 = re.findall(r'2013ff10', info, re.I)
            if result == 2013:
                print file_info_2013
                for j in file_info_2013:
                    if j[0]:
                        result = 2013.5
                    else:
                        result = 2013
        if result:
            self.print_info("get maya file version %s" % (result))
            if float(result) == float(cg_version):
                pass
            else:
                self.writing_error(25013, "maya file version Maya%s" % result)
        return result

    def check_maya_version1(self, maya_file, cg_version):
        """Python3 version of check_version"""
        result = None
        maya_file = self.unicode_to_str(maya_file)
        if maya_file.endswith(".ma"):
            infos = []
            with open(maya_file, "r") as f:
                while 1:
                    line = f.readline()
                    if line.startswith(b"createNode"):
                        break
                    elif line.strip() and not line.startswith(b"//"):
                        infos.append(line.strip())
            file_infos = [i for i in infos if i.startswith(b"fileInfo")]
            for i in file_infos:
                if b"product" in i:
                    r = re.findall(br'Maya.* (\d+\.?\d+)', i, re.I)
                    if r:
                        result = int(r[0].split(".")[0])
                if result == 2016 and b"version" in i:
                    if b"2016 Extension" in i:
                        result = 2016.5
            file_info_2013 = [i for i in infos if i.startswith(b"requires")]
            if result == 2013:
                for j in file_info_2013:
                    if b"maya \"2013\";" in j:
                        result = 2013
                    else:
                        result = 2013.5
        elif maya_file.endswith(".mb"):
            with open(maya_file, "r") as f:
                info = f.readline()
            file_infos = re.findall(br'FINF\x00+\x11?\x12?K?\r?(.+?)\x00(.+?)\x00', info, re.I)
            for i in file_infos:
                if i[0] == b"product":
                    result = int(i[1].split()[1])
            
                if result == 2016 and b"version" in i[0]:
                    if b"2016 Extension" in i[1]:
                        result = 2016.5
            file_info_2013 = re.findall(br'2013ff10', info, re.I)
            if result == 2013:
                print file_info_2013
                for j in file_info_2013:
                    if j[0]:
                        result = 2013.5
                    else:
                        result = 2013
        if result:
            self.print_info("get maya file version %s" % (result))
            if float(result) == float(cg_version):
                pass
            else:
                self.writing_error(25013, "maya file version Maya%s" % result)
        return result


    def write_tips_info(self):
        info_file_path = os.path.dirname(self.tips_json)
        print ("write info_2 to tips.json")
        if not os.path.exists(info_file_path):
            os.makedirs(info_file_path)
        try:
            info_file = self.tips_json
            if os.path.exists(self.tips_json):
                with open(info_file, 'r') as f:
                    json_src = json.load(f)
                    for i in self.tips_info_dict:
                        json_src[i] = self.tips_info_dict[i]
            else:
                json_src = self.tips_info_dict
            # print (json_src)
            with codecs.open(info_file, 'w', 'utf-8') as f:
                json.dump(json_src, f, ensure_ascii=False, indent=4)
        except Exception as err:
            print(err)


    def location_from_reg(self, version):
        # for 2013/2013.5, 2016/2016.5
        versions = (version, "{0}.5".format(version))
        location = None
        mayabatch = None
        for v in versions:
            _string = 'SOFTWARE\Autodesk\Maya\{0}\Setup\InstallPath'.format(v)
            self.print_info(_string)
            try:
                handle = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, _string)
                location, type = _winreg.QueryValueEx(handle, "MAYA_INSTALL_LOCATION")
                mayabatch = os.path.join(location, "bin", "mayabatch.exe")
                mayabatch = mayabatch.replace("\\","/")
                self.print_info('localtion:{0}, type:{1}'.format(location, type))
                break
            except (WindowsError) as e:
                self.print_info_error(traceback.format_exc())

        if not mayabatch:
            if self.current_os == 'windows':
                mayabatch = ["C:/Program Files/Autodesk/Maya%s/bin/mayabatch.exe" %(str(version)),
                             "D:/Program Files/Autodesk/Maya%s/bin/mayabatch.exe" %(str(version)),
                             "E:/Program Files/Autodesk/Maya%s/bin/mayabatch.exe" %(str(version)),
                             "F:/Program Files/Autodesk/Maya%s/bin/mayabatch.exe" %(str(version)),
                             "D:/Alias/Maya%sx64/bin/mayabatch.exe" % (str(version))]
    
                mayabatch = [i for i in mayabatch if os.path.isfile(i)]
                if mayabatch:
                    mayabatch = mayabatch[0]
                else:
                    self.print_info_error("there no Maya%s" % str(version))
                    sys.exit(555)

            elif self.current_os == 'linux':
                mayabatch = '/usr/autodesk/maya' + str(version) + '-x64/bin/maya'
                if not os.path.exists(mayabatch):
                    mayabatch = '/usr/autodesk/maya' + str(version) + '/bin/maya'
            else:
                self.print_info_error("Current OS is %s" % str(version))
                sys.exit(555)
        if not os.path.exists(mayabatch):
            self.writing_error(25025)
            return False

        return mayabatch


    def set_env(self):
        os.environ["MAYA_UI_LANGUAGE"] = "en_US"
        os.environ['MAYA_DISABLE_CIP'] = '1'
        os.environ['MAYA_DISABLE_CLIC_IPM'] = '1'
        os.environ['MAYA_DISABLE_CER'] = '1'
        if float(self.cg_version) >= 2016:
            os.environ['MAYA_OPENCL_IGNORE_DRIVER_VERSION'] = '1'
            os.environ['MAYA_VP2_DEVICE_OVERRIDE'] = 'VirtualDeviceDx11'
        if int(self.argument_json_dict["plugin_setting"]["render_layer_type"]):
            os.environ['MAYA_ENABLE_LEGACY_RENDER_LAYERS'] = "0"
        else:
            os.environ['MAYA_ENABLE_LEGACY_RENDER_LAYERS'] = "1"


    def analyse_cg_file(self):
        self.set_env()
        if self.PY_VERSION == 3:
            version = self.check_maya_version1(self.cg_file,self.cg_version)
        else:
            version = self.check_maya_version(self.cg_file,self.cg_version)
        version = str(version)
        mayabatch_path = self.location_from_reg(version)
        if mayabatch_path:
            options = {}
            options["task_json"] = self.task_json
            options["client_script"] = self.client_script
          
            if self.current_os == 'windows':
                analyse_cmd = "\"%s\" -command \"python \\\"options=%s;import sys;sys.path.insert(0, '%s');import Analyze;reload(Analyze);Analyze.analyze_maya(options)\\\"\"" % (
                    mayabatch_path,options,self.analyze_script_path)
            else:
                analyse_cmd = "\"%s\" -batch -command \"python \\\"argument_json_path=\\\\\\\"%s\\\\\\\";execfile(\\\\\\\"%s\\\\\\\")\\\"\"" % (
                    mayabatch_path, self.argument_json_path, self.analyze_script_path)
        
            self.print_info("\n\n-------------------------------------------Start maya program-------------------------------------\n\n")
            self.print_info("analyse cmd info:\n")
            analyze_code, analyze_result = RBCommonUtil.cmd(analyse_cmd, my_log=self.my_log, continue_on_error=True,my_shell=True,callback_func=self.maya_cmd_callback)
    
            self.print_info(analyze_code)
            self.print_info(analyze_result)
        else:
            pass
        self.print_info(self.tips_info_dict)
        if self.tips_info_dict:
            self.write_tips_info()
            self.print_info("write tips info_2 ok.")



def print_script_version():
    print('----------maya script version--------------')
    print('cg:            maya')
    print('author:        admin')
    print('build:         2018-10-31 10:36')
    print('version:       1.0.1')
    print('hash:          e10adc3949ba59abbe56e057f20f883e')
    
    
def analyse(param_dict):
    RBCommonUtil.debug_log('----------rayvision--submit----------analyse.maya--------------',param_dict["argument_info"]['is_debug'])
    #pprint.pprint(param_dict)
    RBCommonUtil.debug_log(param_dict,param_dict["argument_info"]['is_debug'])
    #print(param_dict['is_debug'])
    #print('__________________________________________________________')
    #argument_json_dict=RBFileUtil.parser_argument_json(param_dict['argument_json'])
    #RBCommonUtil.debug_log(argument_json_dict,param_dict['is_debug'])
    '''
    a_json=sys.path[0]+'\\argument.json'
    with codecs.open(a_json, 'r', 'utf-8') as a_json_obj:
        json_dict = json.load(a_json_obj)
        #pprint.pprint(json_dict)
    '''

    #argument_json_path = argument_json_dict['argument_json']
    #argument_json_path = argument_json_path.replace("\\", "/")
    #analyze_script= os.path.abspath(sys.path[0]+'/../maya/Analyze/')
    #analyze_script_path = analyze_script.replace("\\", "/")

    analyse_maya = Maya(param_dict)
    analyse_maya.analyse_cg_file()





if __name__ == '__main__':
    print('----------rayvision--submit----------maya--------------')
    '''
    a_json=sys.path[0]+'\\..\\argument.json'
    with codecs.open(a_json, 'r', 'utf-8') as a_json_obj:
        json_dict = json.load(a_json_obj)
        #pprint.pprint(json_dict)
    '''
    