#!/usr/bin/env python
# encoding:utf-8
# -*- coding: utf-8 -*-
import logging
import os
import sys
import subprocess
import string
import time
import datetime
import shutil
import codecs
import configparser
import json
import socket
import re
import math
import multiprocessing
from imp import reload
import platform
reload(sys)
# sys.setdefaultencoding('utf-8')
from Maya import Maya
from MayaPlugin import MayaPlugin

from CommonUtil import RBCommon as CLASS_COMMON_UTIL
from MayaUtil import RBMayaUtil as CLASS_MAYA_UTIL
from MayaUtil import NukeMerge
from FrameChecker import RBFrameChecker as CLASS_FRAME_CHECKER
import threading

class RenderMaya(Maya):
    def __init__(self, **paramDict):
        Maya.__init__(self, **paramDict)
        self.format_log('RenderMaya.init', 'start')
        for key, value in self.__dict__.items():
            self.G_DEBUG_LOG.info(key + '=' + str(value))
        self.format_log('done', 'end')
        self.CURRENT_OS = platform.system().lower()
        self.G_CUSTOME_CONFIG_NAME = 'CustomConfig.py'
        self.G_PRE_NAME = 'Pre.py'
        self.G_POST_NAME = 'Post.py'
        self.G_PRERENDER_NAME = 'PreRender.py'
        self.G_POSTRENDER_NAME = 'PostRender.py'
        self.G_CUSTOME_PRERENDER_NAME = 'C_PreRender.py'
        self.G_CUSTOME_INFO_CMD_NAME = 'info.json'
        self.CG_PLUGINS_DICT = self.G_CG_CONFIG_DICT['plugins']
        self.CG_NAME = self.G_CG_CONFIG_DICT['cg_name']
        self.CG_VERSION = self.G_CG_CONFIG_DICT['cg_version']
        self.ENABLE_LAYERED = self.G_TASK_JSON_DICT['scene_info_render']['enable_layered']
        self.TEMP_PATH = self.G_SYSTEM_JSON_DICT['system_info']['common']['temp_path']
        
        self.G_RN_MAYA_PRERENDER = os.path.join(self.G_NODE_MAYASCRIPT, self.G_PRERENDER_NAME).replace('\\', '/')
        self.G_RN_MAYA_POSTRENDER = os.path.join(self.G_NODE_MAYASCRIPT, self.G_POSTRENDER_NAME).replace('\\', '/')
        self.G_RN_MAYA_CUSTOME_PRERENDER = os.path.join(self.G_NODE_MAYASCRIPT, self.G_CUSTOME_PRERENDER_NAME).replace(
            '\\', '/')
        self.G_RN_MAYA_CUSTOME_CONFIG_CMD = os.path.join(self.G_NODE_MAYACONFIG, self.G_CUSTOME_INFO_CMD_NAME).replace('\\', '/')
        
        if self.G_CG_TILE_COUNT == self.G_CG_TILE:
            self.IMAGE_MERGE_FRAME = "1"
        else:
            self.IMAGE_MERGE_FRAME = "0"
        self.PLUGINS_PATH = self.get_plugin_dir() + "/plugins"
        self.CONFIG_PATH = self.get_plugin_dir() + "/config"
        self.MESS_UP_PATH = self.get_plugin_dir() + "/mess_up"
        
        self.ERROR_LIST = []
        

    def my_print(self,message):
        self.G_DEBUG_LOG.info('[MonitorLog] %s' % message)

    
    def maya_cmd_callback(self, my_popen, my_log):
        while my_popen.poll() is None:
            result_line = my_popen.stdout.readline().strip()
            result_line = result_line.decode(sys.getfilesystemencoding())
            # result_line = result_line.decode('utf-8')
            result_line = self.bytes_to_str(result_line)
            result_line = self.to_gbk(result_line)
            if result_line == '':
                continue
            CLASS_COMMON_UTIL.log_print(my_log, result_line)
            
            if self.g_one_machine_multiframe is True:
                if '[_____render end_____]' in result_line:  # [_____render end_____][1]
                    frame = re.search('\[(-?\d+)\]', result_line).group(1)
                    self.multiframe_complete_list.append(frame)
                    end_time = int(time.time())
                    print('[self.render_record]: {}'.format(self.render_record))
                    self.render_record[frame]['end_time'] = end_time
                    self.render_record[str(int(frame) + int(self.G_CG_BY_FRAME))] = {'start_time': end_time,
                                                                                     'end_time': -1}


            #任务渲染完，强制退出maya

            completed_key = "Scene %s completed" % (self.renderSettings["maya_file"])
            if completed_key in result_line:
                print("log_key: {%s}" % completed_key)
                print("maya batch end !!!")
                # my_popen.kill() #杀不掉子进程的子进程，所以有问题
                CLASS_MAYA_UTIL.killMayabatch(my_log)  # kill mayabatch.exe
                break


    def bytes_to_str(self, str1, str_decode='default'):
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

    def get_encode(self, encode_str):
        for code in ["utf-8", sys.getfilesystemencoding(), "gb18030", "ascii", "gbk", "gb2312"]:
            try:
                encode_str.decode(code)
                return code
            except:
                pass

    def to_gbk(self, encode_str):
        if isinstance(encode_str, str):
            return encode_str
        else:
            code = self.get_encode(encode_str)
            return encode_str.decode(code).encode('GBK')

    def get_plugin_dir(self):
        if self.CURRENT_OS == "windows":
            plugin_path_ip = self.G_PLUGIN_PATH
            plugin_path = "c:/renderbuswork/cg/maya/windows"
            if os.path.exists(plugin_path):
                return plugin_path
            elif self.G_PLUGIN_PATH:
                self.my_print(self.G_PLUGIN_PATH)
                plugin_path_ip = plugin_path_ip.replace("\\","/")
                # self.MyLog("plugins server path is :: %s" % plugin_path_ip)
                plugin_path_ip = plugin_path_ip.split("/")[2]
                plugin_path = "//" + plugin_path_ip + "/cg/maya/windows"
                return plugin_path
            else:
                self.my_print("Plugins path is not exists.............")
                sys.exit(555)
    
        elif self.CURRENT_OS == "linux":
            plugin_path = "/tmp/nzs-data/renderbuswork/cg/maya/linux"
            if os.path.exists(plugin_path):
                return plugin_path
            else:
                self.my_print("Plugins path is not exists.............")
                sys.exit(555)
        
    def RB_CONFIG(self):
        self.G_DEBUG_LOG.info('[Maya.RBconfig.start.....]')
        try:
            if self.CURRENT_OS == "windows":
                if self.CG_VERSION == '2017':
                    copy_cmd = '{fcopy_path} /speed=full /force_close /no_confirm_stop /force_start "{source}" /to="{destination}"'.format(
                        fcopy_path='c:\\fcopy\\FastCopy.exe',
                        source=os.path.join(self.PLUGINS_PATH,"maya_Documents","2017updata3").replace(
                            '/', '\\'),
                        destination=os.path.join(r"C:/Program Files/Autodesk/Maya2017/scripts/others").replace("/", "\\"),
                    )
    
                    CLASS_COMMON_UTIL.cmd(copy_cmd, my_log=self.G_DEBUG_LOG, try_count=3, continue_on_error=False)

        except Exception as err:
            self.G_DEBUG_LOG.infor(err)
        
        if self.G_CG_TILE_COUNT != self.G_CG_TILE:
            print(
            "----------------------------------------loading plugins start ------------------------------------------")
            # kill maya
            CLASS_MAYA_UTIL.killMayabatch(self.G_DEBUG_LOG)  # kill mayabatch.exe
            # ----------------set env  -------------------
            os.environ["MAYA_UI_LANGUAGE"] = "en_US"
            os.environ['MAYA_DISABLE_CIP'] = '1'
            os.environ['MAYA_DISABLE_CLIC_IPM'] = '1'
            os.environ['MAYA_DISABLE_CER'] = '1'
            if float(self.CG_VERSION) >= 2016:
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
                custom_config = os.path.join(self.G_NODE_MAYAFUNCTION, self.G_CUSTOME_CONFIG_NAME).replace('\\', '/')
                if self.G_NODE_MAYAFUNCTION:
                    if os.path.exists(custom_config):
                        sys.stdout.flush()
                        print("custom_config is: " + custom_config)
                        sys.stdout.flush()
                    else:
                        print("Can not find the CustomConfig file: %s." % custom_config)
                print("plugin path:")
                print(self.G_CG_CONFIG_DICT)
                sys.stdout.flush()
                maya_plugin = MayaPlugin(self.G_CG_CONFIG_DICT, [custom_config], self.G_USER_ID, self.G_TASK_ID,
                                         self.G_DEBUG_LOG,self.G_PLUGIN_PATH)
                maya_plugin.config()
                sys.stdout.flush()
            print(
            "----------------------------------------loading plugins end ------------------------------------------")
            self.G_DEBUG_LOG.info('[Maya.RBconfig.end.....]')
            
        else:
            self.G_DEBUG_LOG.info("[RenderNuke  Comp...........................]")
        self.G_DEBUG_LOG.info('[RenderMaya.RB_CONFIG.end.....]')
        self.format_log('done', 'end')

    '''
        渲染
    '''
    
    def RB_RENDER(self):  # 5
        
        self.format_log('渲染', 'start')
        if int(self.G_CG_TILE_COUNT) != int(self.G_CG_TILE):
            self.G_DEBUG_LOG.info('[RenderMaya.RB_RENDER.start.....]')

            # ------------get render cmd----------
            
            # #------------get render cmd----------
            self.MAYA_FINAL_RENDER_CMD = self.get_render_cmd()

            render_cmd = self.MAYA_FINAL_RENDER_CMD
            sys.stdout.flush()
            print ("render cmd info:")
            self.G_DEBUG_LOG.info(render_cmd)
            
            start_time = int(time.time())
            if self.g_one_machine_multiframe is True:
                render_list = CLASS_COMMON_UTIL.need_render_from_frame(self.G_CG_FRAMES)
                self.render_record.update({render_list[0]: {'start_time': start_time, 'end_time': 0}})
                pass
            self.G_FEE_PARSER.set('render', 'start_time', str(start_time))
            
            self.G_DEBUG_LOG.info(
                "\n\n-------------------------------------------Start maya program-------------------------------------\n\n")
            result_code, _ = CLASS_COMMON_UTIL.cmd(render_cmd, my_log=self.G_RENDER_LOG, continue_on_error=False,
                                                   my_shell=True,
                                                   callback_func=self.maya_cmd_callback)
            
            self.cg_return_code = result_code
            end_time = int(time.time())
            self.G_FEE_PARSER.set('render', 'end_time', str(end_time))
            
            # if self.g_one_machine_multiframe is True:
            #     CLASS_MAYA_UTIL.clean_dir(self.G_WORK_RENDER_TASK_OUTPUT, my_log=self.G_DEBUG_LOG)
            
            CLASS_MAYA_UTIL.kill_lic_all(my_log=self.G_DEBUG_LOG)
            self.G_FEE_PARSER.set('render', 'end_time', str(end_time))
            self.G_DEBUG_LOG.info('[RenderMaya.RB_RENDER.end.....]')
        
        else:
            self.G_DEBUG_LOG.info('[RenderNuke.RB_RENDER.start.....]')
            self.G_FEE_PARSER.set('render', 'start_time', str(int(time.time())))
            options = {}
            options["func_path"] = self.G_NODE_MAYAFUNCTION
            options["tiles"] = int(self.G_CG_TILE_COUNT)
            options["tile_index"] = int(self.G_CG_TILE)
            options["width"] = int(self.G_TASK_JSON_DICT['scene_info_render'][self.G_CG_LAYER_NAME]['common']['width'])
            options["height"] = int(
                self.G_TASK_JSON_DICT['scene_info_render'][self.G_CG_LAYER_NAME]['common']['height'])
            options["output"] = self.G_WORK_RENDER_TASK_OUTPUT
            options["g_tiles_path"] = self.G_TILES_PATH
            options["g_task_id"] = self.G_TASK_ID
            options["g_cg_start_frame"] = self.G_CG_START_FRAME
            print (options)
            nuke_merge = NukeMerge(options)
            nuke_merge.render(self.G_DEBUG_LOG)
            CLASS_MAYA_UTIL.kill_lic_all(my_log=self.G_DEBUG_LOG)
            self.G_FEE_PARSER.set('render', 'end_time', str(int(time.time())))
            self.G_DEBUG_LOG.info('[RenderNuke.RB_RENDER.end.....]')

        # 日志过滤调用errorbase类
        monitor_ini_dict = {}
        monitor_ini_dict["G_INPUT_CG_FILE"] = self.G_INPUT_CG_FILE
        monitor_ini_dict["CG_NAME"] = self.CG_NAME
        monitor_ini_dict["CG_VERSION"] = self.CG_VERSION
        monitor_ini_dict["CG_PLUGINS_DICT"] = self.CG_PLUGINS_DICT
        monitor_ini_dict["G_INPUT_USER_PATH"] = self.G_INPUT_USER_PATH
        monitor_ini_dict["G_OUTPUT_USER_PATH"] = self.G_OUTPUT_USER_PATH
        monitor_ini_dict["G_NODE_NAME"] = self.G_NODE_NAME
        monitor_ini_dict["G_NODE_ID"] = self.G_NODE_ID
        monitor_ini_dict["G_WORK_RENDER_TASK_OUTPUT"] = self.G_WORK_RENDER_TASK_OUTPUT
        monitor_ini_dict["G_DEBUG_LOG"] = self.G_DEBUG_LOG

        monitor_log = ErrorBase(monitor_ini_dict)
        monitor_log.run()

        self.format_log('done', 'end')
    
    def get_region(self, tiles, tile_index, width, height):
        n = int(math.sqrt(tiles))
        for i in sorted(range(2, n + 1), reverse=1):
            if tiles % i != 0:
                continue
            else:
                n = i
                break
        n3 = tiles / n
        n1 = tile_index / n3
        n2 = tile_index % n3
        top = height / n * (n1 + 1)
        left = width / n3 * n2
        bottom = height / n * n1
        right = width / n3 * (n2 + 1)
        if right == width:
            right -= 1
        if top == height:
            top -= 1
        return int(left), int(right), int(bottom), int(top)
    
    def get_render_cmd(self):
        self.renderSettings = {}
        self.mappings = {}
        render_cmd = ''

        if os.path.exists(self.G_RN_MAYA_CUSTOME_CONFIG_CMD):
            print ("handle custome cmd.json")
            with open(self.G_RN_MAYA_CUSTOME_CONFIG_CMD, 'r') as fn:
                cmd_dict = json.load(fn)
            print (cmd_dict)
            # for i in cmd_dict:
            #     self.renderSettings[i] = cmd_dict[i]
    
        if self.G_RENDER_OS == '0':
            if float(self.CG_VERSION) < 2016:
                version_name = "%s-x64" % (self.CG_VERSION)
            else:
                version_name = self.CG_VERSION
            self.renderSettings["render.exe"] = "/usr/autodesk/" \
                                                "maya%s/bin/Render" % (version_name)
            self.renderSettings["mayabatch.exe"] = "/usr/autodesk/" \
                                                   "maya%s/bin/maya -batch" % (version_name)
        self.renderSettings["render.exe"] = "C:/Program Files/Autodesk/" \
                                            "maya%s/bin/render.exe" % (self.CG_VERSION)
        self.renderSettings["output"] = os.path.normpath(self.G_WORK_RENDER_TASK_OUTPUT).replace("\\", "/")
        
        # 一机多帧
        self.renderSettings["g_one_machine_multiframe"] = self.g_one_machine_multiframe
        if self.g_one_machine_multiframe is True:
            self.renderSettings["output"] = os.path.join(os.path.normpath(self.G_WORK_RENDER_TASK_OUTPUT),
                                                         "temp_out").replace("\\", "/")
        self.renderSettings["output_frame"] = os.path.normpath(self.G_WORK_RENDER_TASK_OUTPUT).replace("\\", "/")
        
        if not os.path.exists(self.renderSettings["output"]):
            os.makedirs(self.renderSettings["output"])
        
        self.renderSettings["tile_region"] = ""
        self.renderSettings["tiles"] = int(self.G_CG_TILE_COUNT)
        self.renderSettings["tile_index"] = int(self.G_CG_TILE)
        # -----------render tiles------------
        if self.renderSettings["tiles"] > 1:
            tile_region = self.get_region(int(self.G_CG_TILE_COUNT),
                                          int(self.G_CG_TILE),
                                          int(self.G_TASK_JSON_DICT['scene_info_render'][self.G_CG_LAYER_NAME][
                                                  'common']['width']),
                                          int(self.G_TASK_JSON_DICT['scene_info_render'][self.G_CG_LAYER_NAME][
                                                  'common']['height']))
            self.renderSettings["tile_region"] = " ".join([str(i) for i in tile_region])
            
            self.renderSettings["output"] = "%s/%s/%s/" % \
                                            (os.path.normpath(self.G_WORK_RENDER_TASK_OUTPUT).replace("\\", "/"),
                                             self.G_CG_START_FRAME,
                                             self.renderSettings["tile_index"])
            self.renderSettings["output"] = os.path.normpath(self.renderSettings["output"])
            if not os.path.exists(self.renderSettings["output"]):
                os.makedirs(self.renderSettings["output"])
        
        if self.G_INPUT_PROJECT_PATH:
            if os.path.exists(self.G_INPUT_PROJECT_PATH):
                os.chdir(self.G_INPUT_PROJECT_PATH)
        
        self.renderSettings["maya_file"] = os.path.normpath(self.G_INPUT_CG_FILE).replace("\\","/")
        self.renderSettings["start"] = self.G_CG_START_FRAME
        self.renderSettings["end"] = self.G_CG_END_FRAME
        self.renderSettings["by"] = self.G_CG_BY_FRAME
        self.renderSettings["renderableCamera"] = self.G_CG_OPTION
        self.renderSettings["renderableLayer"] = self.G_CG_LAYER_NAME
        self.renderSettings["projectPath"] = os.path.normpath(self.G_INPUT_PROJECT_PATH).replace("\\","/")
        self.renderSettings["renderType"] = "render.exe"
        if self.ENABLE_LAYERED == "1":
            self.renderSettings["width"] = int(
                self.G_TASK_JSON_DICT['scene_info_render'][self.G_CG_LAYER_NAME]['common']['width'])
            self.renderSettings["height"] = int(
                self.G_TASK_JSON_DICT['scene_info_render'][self.G_CG_LAYER_NAME]['common']['height'])
        else:
            self.renderSettings["width"] = int(
                self.G_TASK_JSON_DICT['scene_info_render']['defaultRenderLayer']['common']['width'])
            self.renderSettings["height"] = int(
                self.G_TASK_JSON_DICT['scene_info_render']['defaultRenderLayer']['common']['height'])
        
        # "-----------------------------cmd--------------------------------"
        cmd = "\"%(render.exe)s\" -s %(start)s -e %(end)s -b %(by)s " \
              "-proj \"%(projectPath)s\" -rd \"%(output)s\"" \
              % self.renderSettings
        if self.G_CG_OPTION:
            cmd += " -cam \"%(renderableCamera)s\"" % self.renderSettings
        if self.G_CG_LAYER_NAME:
            cmd += " -rl \"%(renderableLayer)s\"" % self.renderSettings
        
        pre_render_dict = {}
        pre_render_dict["enable_layered"] = self.ENABLE_LAYERED
        pre_render_dict["projectPath"] = os.path.normpath(self.G_INPUT_PROJECT_PATH)
        pre_render_dict["mapping"] = self.mappings
        pre_render_dict["renderableCamera"] = self.G_CG_OPTION
        pre_render_dict["renderableLayer"] = self.G_CG_LAYER_NAME
        pre_render_dict["task_json"] = self.G_TASK_JSON
        pre_render_dict["start"] = self.G_CG_START_FRAME
        pre_render_dict["c_prerender"] = self.G_RN_MAYA_CUSTOME_PRERENDER
        pre_render_dict["user_id"] = self.G_USER_ID
        pre_render_dict["task_id"] = self.G_TASK_ID
        pre_render_dict["plugins"] = self.G_CG_CONFIG_DICT["plugins"]
        
        
        # cmd += " -preRender \"python \\\"pre_render_dict=%s;execfile(\\\\\\\"%s\\\\\\\")\\\"\"" % (pre_render_dict, self.G_RN_MAYA_PRERENDER)
        #
        # ---------------render cmd-------------------------
        
        
        # ----------render tile------------
        if self.ENABLE_LAYERED == "1":
            self.renderer = self.G_TASK_JSON_DICT['scene_info_render'][self.G_CG_LAYER_NAME]['common']['renderer']
            if self.renderSettings["tile_region"]:
                if self.renderer in ["mentalRay", "arnold", "vray"]:
                    if self.renderer == "mentalRay" and float(self.CG_VERSION) < 2017:
                        cmd += " -r mr -reg %(tile_region)s" % self.renderSettings
                    elif self.renderer == "mentalRay" and float(
                            self.CG_VERSION) > 2016.5 and "mentalray" in self.CG_PLUGINS_DICT:
                        cmd += " -r mr -reg %(tile_region)s" % self.renderSettings
                    
                    elif self.renderer == "arnold" and "mtoa" in self.CG_PLUGINS_DICT:
                        cmd += " -r arnold -reg %(tile_region)s" % self.renderSettings
                    
                    elif self.renderer == "vray" and "vrayformaya" in self.CG_PLUGINS_DICT:
                        cmd += " -r vray -reg %(tile_region)s" % self.renderSettings
                    
                    else:
                        print("please confirm the renderer is correct!")
                        print("current render layer \'s render is %s ,not in [mentalRay,arnold,vray]" % (self.renderer))
                        sys.exit(555)
                elif self.renderer in ["mayaSoftware"]:
                    cmd += " -r sw -reg %(tile_region)s" % self.renderSettings
                
                elif self.renderer in ["redshift"]:
                    cmd += " -r redshift -logLevel 1 -gpu {0,1} -reg %(tile_region)s" % self.renderSettings
                    
                else:
                    print("please confirm the renderer is correct!")
                    print("current render layer \'s render is %s " % (self.renderer))
                    sys.exit(555)
            
            else:
                if self.renderer == "renderManRIS" or self.renderer == "renderMan" and "RenderMan_for_Maya" in self.CG_PLUGINS_DICT:
                    cmd += " -r rman"
                elif self.renderer == "vray" and "vrayformaya" in self.CG_PLUGINS_DICT:
                    cmd += " -r vray"
                elif self.renderer == "redshift" and "redshift" in self.CG_PLUGINS_DICT:
                    cmd += " -r redshift -logLevel 1"
                    gpu_n = "0,1"
                    cmd += " -gpu {%s}" % (gpu_n)
                elif self.renderer == "mayaSoftware":
                    cmd += " -r sw"
                else:
                    pass
        
        else:
            
            scene_info_render_dict = self.G_TASK_JSON_DICT['scene_info_render']
            renderer_list = CLASS_MAYA_UTIL.dict_get(scene_info_render_dict, "renderer")
            self.G_DEBUG_LOG.info(renderer_list)
            
            if "redshift" in self.CG_PLUGINS_DICT and "redshift" in renderer_list:
                cmd += " -r redshift -logLevel 1"
                gpu_n = "0,1"
                cmd += " -gpu {%s}" % (gpu_n)
            
            elif "RenderMan_for_Maya" in self.CG_PLUGINS_DICT and "renderManRIS" in renderer_list or "renderMan" in renderer_list:
                cmd += " -r rman"
            else:
                pass

        if "-r rman" in cmd:
            cmd += " -setAttr Format:resolution \"%(width)s %(height)s\"" % self.renderSettings
        else:
            cmd += " -x %(width)s -y %(height)s" % self.renderSettings

        post_render_dict = {}
        post_render_dict["output"] = self.renderSettings["output"]
        post_render_dict["output_frame"] = self.renderSettings["output_frame"]
        post_render_dict["g_one_machine_multiframe"] = self.g_one_machine_multiframe
        
        # -------------get custom render cmd-------------
        
        
        # -------------add post render cmd-------------
        if self.g_one_machine_multiframe is True:
            cmd += " -postFrame \"python \\\"post_render_dict=%s;execfile(\\\\\\\"%s\\\\\\\")\\\";\"" % (
                post_render_dict, self.G_RN_MAYA_POSTRENDER)
        
        max_threads_number = int(multiprocessing.cpu_count())
        if " -r " not in cmd and float(self.CG_VERSION) < 2017:
            # cmd += " -mr:art -mr:aml"
            cmd += " -mr:rt %s -mr:aml" % max_threads_number
        
        cmd += " \"%(maya_file)s\"" % self.renderSettings
            
        sys.stdout.flush()
        return cmd


class ErrorBase():
    def __init__(self,ini_dict):
        print(ini_dict)
        for key in list(ini_dict.keys()):
            assign = 'self.{0} = ini_dict["{0}"]'.format(key)
            exec (assign)
    
    def run(self):
        self.print_trilateral(mode=1)
        self.G_DEBUG_LOG.info('------------------------- start MonitorLog-------------------------')
        self.get_ini()
        self.G_DEBUG_LOG.info('-------------------------  end  MonitorLog-------------------------')
        self.print_trilateral(mode=2)
    
    def my_log(self, message):
        self.G_DEBUG_LOG.info('[MonitorLog] %s' % message)
    
    def print_trilateral(self,rows=4,mode=1):
        '''
        :param rows: rows counts
        :param mode: up  or  down
        :return: a trilateral
        '''
        for i in range(0, rows):
            for k in range(0, i + 1 if mode == 1 else rows - i):
                self.my_log(" * ",)
                k += 1
            i += 1
            self.my_log("\n")
    
    def get_ini(self):
        self.G_DEBUG_LOG.info('[MonitorLog].start...')
        self.my_log('软件::%s' % (self.CG_NAME + self.CG_VERSION))
        self.my_log('插件::%s' % (self.CG_PLUGINS_DICT))
        self.my_log('内存使用::%s' % ('None'))
        self.my_log('INPUT  目录::%s' % (self.G_INPUT_USER_PATH.replace('/', '\\')))
        self.my_log('OUTPUT 目录::%s' % (self.G_OUTPUT_USER_PATH.replace('/', '\\')))
        self.my_log('节点机器IP::%s--%s' % (self.G_NODE_NAME, CLASS_COMMON_UTIL.get_computer_ip()))
        self.my_log('节点机器OUTPUT目录::%s' % (self.G_WORK_RENDER_TASK_OUTPUT.replace('/', '\\')))
        self.my_log('MAYA文件::%s' % (self.G_INPUT_CG_FILE.replace('/', '\\')))
        self.my_log('MAYA文件的大小::%s MB' % (self.get_FileSize(self.G_INPUT_CG_FILE)))
        self.my_log('MAYA文件的时间::%s' % (self.get_FileModifyTime(self.G_INPUT_CG_FILE)))
        

    def TimeStampToTime(self,timestamp):
        '''把时间戳转化为时间: 1479264792 to 2016-11-16 10:53:12'''
        timeStruct = time.localtime(timestamp)
        return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)
        
    def get_FileSize(self,filePath):
        '''获取文件的大小,结果保留两位小数，单位为MB'''
        filePath = unicode(filePath,'utf8')
        fsize = os.path.getsize(filePath)
        fsize = fsize/float(1024*1024)
        return str(round(fsize,2))
    
    def get_FileModifyTime(self,filePath):
        '''获取文件的修改时间'''
        filePath = unicode(filePath,'utf8')
        t = os.path.getmtime(filePath)
        return self.TimeStampToTime(t)
    
    def get_FileCreateTime(self,filePath):
        '''获取文件的创建时间'''
        filePath = unicode(filePath,'utf8')
        t = os.path.getctime(filePath)
        return self.TimeStampToTime(t)

    def get_FileAccessTime(self,filePath):
        '''获取文件的访问时间'''
        filePath = unicode(filePath,'utf8')
        t = os.path.getatime(filePath)
        return self.TimeStampToTime(t)
