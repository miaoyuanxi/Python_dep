#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
import subprocess
import string
import time
import datetime
import shutil
import ctypes
import json
import re
import configparser
import codecs
import random
import threading
import copy
import collections
import urllib.request
import urllib.error
import FrameCheckerLinux
from atexit import register

from CommonUtil import RBCommon as CLASS_COMMON_UTIL
from FrameChecker import RBFrameChecker as CLASS_FRAME_CHECKER


class RenderBase(object):

    def __init__(self, **param_dict):
        """
        1.入口脚本中以G开头的变量都会定义为成员变量
        2.JOB_NAME与JOB_ID：
            平台和munu都有各自代表不同含义的JOB_NAME与JOB_ID，脚本JOB_NAME与JOB_ID采用的是munu通过入口脚本命令行传过来的值
            平台侧：JOB_NAME，一串数字，没有具体含义；JOB_ID，只有在通道任务时有意义，通道传值为"channel"。两个值可从脚本入口脚本获取
            munu侧：JOB_NAME与平台侧JOB_ID一致；JOB_ID代表munu_job_id。两个值可从入口脚本命令行获取
        """
    
        print('[BASE.init.start.....]')

        # define variables
        # G_JOB_NAME,G_JOB_ID,G_CG_FRAMES,G_CG_LAYER_NAME,G_CG_OPTION,G_CG_TILE,G_CG_TILE_COUNT
        # G_CG_NAME,G_ACTION,G_USER_ID,G_TASK_ID,G_TASK_JSON,G_USER_ID_PARENT,G_SCRIPT_POOL,G_RENDER_OS,G_SYS_ARGVS,G_NODE_PY  &&  G_SCHEDULER_CLUSTER_ID,G_SCHEDULER_CLUSTER_NODES
        for key in list(param_dict.keys()):
            if key.startswith('G'):
                assign = 'self.{0} = param_dict["{0}"]'.format(key)
                exec (assign)
                # exec('self.'+key+'=param_dict["'+key+'"]')

        # max通道任务，平台那边传的G_ACTION过来仍然是Render，入口脚本的G_JOB_ID传channel过来以便区分
        # 脚本会将"channel"赋值给self.G_JOB_NAME以便后续使用
        is_channel = True if self.G_JOB_ID == 'channel' else False
        argvs = self.G_SYS_ARGVS
        self.G_MUNU_ID = argvs[1].replace("\"","")  # munu_task_id
        self.G_JOB_ID = argvs[2].replace("\"","")  # munu_job_id
        self.G_JOB_NAME = argvs[3].replace("\"","") if not is_channel else 'channel'  # munu_job_name
        self.G_NODE_ID = argvs[4].replace("\"","")  # 11338764789520
        self.G_NODE_NAME = argvs[5].replace("\"","")  # GD232
        self.G_RECOMMIT_FLAG = argvs[6].replace("\"","")  # recommit_flag,default is "0"
        self.G_RENDER_CONTINUE = argvs[7].replace("\"","")  # 是否继续渲染, 目前用于一机多帧中, 值: "true"(继续, 原来是渲到第几帧就从第几帧开始)/"false"(重来, 从第一帧开始)

        self.G_ACTION_ID = self.G_ACTION + '_' + self.G_MUNU_ID + '_' + self.G_JOB_ID

        # self.G_CG_PROCESS_FLAG = 0  # use with B:\config\cg_process.json
        self.G_WORK = 'c:/work'
        self.G_LOG_WORK = 'C:/log/render'
        # TODO 新平台路径改变
        if self.G_RENDER_OS == '0':  # G_RENDER_OS:0 linux ,1 windows
            self.G_LOG_WORK = '/tmp/nzs-data/log/render'
            self.G_WORK = '/tmp/nzs-data/work'

        # -----------------------------------------log-----------------------------------------------
        self.G_DEBUG_LOG = logging.getLogger('debug_log')
        self.G_RENDER_LOG = logging.getLogger('render_log')
        self.init_log()

        # -----------------------------------------analyse frame-----------------------------------------------
        if 'G_CG_FRAMES' in param_dict:
            start_frame, end_frame, by_frame = CLASS_COMMON_UTIL.find_frame(self.G_CG_FRAMES)
            self.G_CG_START_FRAME = start_frame
            self.G_CG_END_FRAME = end_frame
            self.G_CG_BY_FRAME = by_frame
            
        # 分块
        if 'G_CG_TILE' not in param_dict or ('G_CG_TILE' in param_dict and (self.G_CG_TILE is None or self.G_CG_TILE == '')):
            self.G_CG_TILE = '0'
        if 'G_CG_TILE_COUNT' not in param_dict or ('G_CG_TILE_COUNT' in param_dict and (self.G_CG_TILE_COUNT is None or self.G_CG_TILE_COUNT == '')):
            self.G_CG_TILE_COUNT = '1'

        # 是否一机多帧
        if "G_RENDER_MUL_NUM" in param_dict:  # 主图有此键
            if self.G_RENDER_MUL_NUM == "1":
                self.g_one_machine_multiframe = True
            elif self.G_RENDER_MUL_NUM == "0":
                self.g_one_machine_multiframe = False
        else:
            self.g_one_machine_multiframe = None

        # -----------------------------------------work directory-----------------------------------------------
        self.G_WORK_RENDER = os.path.normpath(os.path.join(self.G_WORK, 'render'))
        self.G_WORK_RENDER_TASK = os.path.normpath(os.path.join(self.G_WORK_RENDER, self.G_TASK_ID))
        self.G_WORK_RENDER_TASK_CFG = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK, 'cfg'))
        self.G_WORK_RENDER_TASK_OUTPUT = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK, 'output'))
        self.G_WORK_RENDER_TASK_OUTPUTBAK = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK, 'outputbak'))
        self.G_WORK_RENDER_TASK_SMALL = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK, 'small'))

        # 一机多帧才创建此文件夹
        self.G_WORK_RENDER_TASK_MULTIFRAME = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK, 'multiframe'))
        self.G_WORK_RENDER_TASK_MULTIFRAME_BAK = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK, 'multiframe_bak'))

        self.make_dir()

        # -----------------------------------------task.json+system.json-----------------------------------------------
        self.G_DEBUG_LOG.info(self.G_TASK_JSON)
        if not os.path.exists(self.G_TASK_JSON):
            CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG, 'task.json not exists')
        
        CLASS_COMMON_UTIL.python_copy(os.path.normpath(self.G_TASK_JSON), os.path.normpath(self.G_WORK_RENDER_TASK_CFG), my_log=self.G_DEBUG_LOG)
        self.G_REMOTE_TASK_CFG = os.path.split(self.G_TASK_JSON)[0]
        self.G_TASK_JSON = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK_CFG, 'task.json'))
        # self.G_TASK_JSON_DICT = eval(codecs.open(self.G_TASK_JSON, 'r', 'utf-8').read())
        with codecs.open(self.G_TASK_JSON, 'r', 'utf-8') as f_task_json:
            self.G_TASK_JSON_DICT = json.load(f_task_json)
        try:
            print(str(self.G_TASK_JSON_DICT))  # print默认是gbk编码，如果是非中英文则会报错
        except:
            pass
        

        # system.json
        self.G_DEBUG_LOG.info(self.G_SYSTEM_JSON)
        if not os.path.exists(self.G_SYSTEM_JSON):
            CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG, 'system.json not exists')
        
        CLASS_COMMON_UTIL.python_copy(os.path.normpath(self.G_SYSTEM_JSON), os.path.normpath(self.G_WORK_RENDER_TASK_CFG), my_log=self.G_DEBUG_LOG)
        self.G_REMOTE_TASK_SYS_CFG = os.path.split(self.G_SYSTEM_JSON)[0]
        self.G_SYSTEM_JSON = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK_CFG, 'system.json'))
        # self.G_SYSTEM_JSON_DICT = eval(codecs.open(self.G_SYSTEM_JSON, 'r', 'utf-8').read())
        with codecs.open(self.G_SYSTEM_JSON, 'r', 'utf-8') as f_system_json:
            self.G_SYSTEM_JSON_DICT = json.load(f_system_json)
        try:
            print(str(self.G_SYSTEM_JSON_DICT))  # print默认是gbk编码，如果是非中英文则会报错
        except:
            pass
            
        # system_linux.json
        self.G_LINUX_MAP_DICT2 = {}#G_LINUX_MAP_DICT2是从system.json里取来的映射关系，G_LINUX_MAP_DICT是入口脚本里的脚本P目录的映射关系
        # TODO 新平台路径改变
        if self.G_RENDER_OS == '0':  # G_RENDER_OS:0 linux ,1 windows
            self.G_LINUX_MAP_DICT2 = self.G_SYSTEM_JSON_DICT['system_info']['mnt_map_linux']
            
        self.G_SYSTEM_LINUX_JSON = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK_CFG, 'system_linux.json'))
        if self.G_RENDER_OS == '0':  # G_RENDER_OS:0 linux ,1 windows
            print('__________linux json---------')
            print(str(self.G_LINUX_MAP_DICT))
            print(str(self.G_LINUX_MAP_DICT2))
            system_json_linux_dict = copy.deepcopy(self.G_SYSTEM_JSON_DICT)
            common = system_json_linux_dict['system_info']['common']
            for key, value in common.items():
                new_value = self.to_linux_path(value)
                system_json_linux_dict['system_info']['common'][key] = new_value
                
            system_json_linux_dict['system_info']['common']['plugin_path_list'] = ['/tmp/nzs-data/renderbuswork/cg']
            
            self.G_SYSTEM_LINUX_JSON_DICT = system_json_linux_dict
            
            with codecs.open(self.G_SYSTEM_LINUX_JSON, 'w', 'utf-8') as f_system_linux_json:
                json.dump(system_json_linux_dict, f_system_linux_json, ensure_ascii=False, indent=4)

        software_config = self.G_TASK_JSON_DICT['software_config']
        self.G_CG_CONFIG_DICT = software_config
        self.G_CG_VERSION = software_config['cg_name'] + ' ' + software_config['cg_version']

        common = self.G_SYSTEM_JSON_DICT['system_info']['common']
        self.G_ZONE = common['zone']
        self.G_PLATFORM = common['platform']
        self.G_AUTO_COMMIT = str(common['auto_commit'])
        self.G_TILES_PATH = os.path.normpath(os.path.join(common['tiles_path'], self.G_SMALL_TASK_ID))
        self.G_INPUT_CG_FILE = os.path.normpath(common['input_cg_file'])
        self.G_CHANNEL = common['channel']  # 1:from client  2:from web  3:from plugin  4.from sdk

        self.G_INPUT_PROJECT_PATH = os.path.normpath(common['input_project_path'])
        self.G_CONFIG_PATH = os.path.normpath(os.path.join(common['config_path'], self.G_TASK_ID, 'cfg'))
        self.G_SMALL_PATH = os.path.normpath(os.path.join(common['small_path'], self.G_TASK_ID))
        self.G_INPUT_USER_PATH = os.path.normpath(common['input_user_path'])
        
        self.G_TEMP_PATH = os.path.normpath(os.path.join(common['temp_path'], self.G_TASK_ID))
        self.G_GRAB_PATH = os.path.normpath(os.path.join(common['grab_path'], self.G_TASK_ID))
        user_path = os.path.normpath(common['output_user_path'])
        self.G_OUTPUT_USER_PATH = os.path.join(user_path, '{}_{}'.format(self.G_SMALL_TASK_ID, os.path.splitext(os.path.basename(self.G_INPUT_CG_FILE))[0]))
        self.G_API_PATH = os.path.normpath(common['api_path'])
        self.G_FEE_PATH = os.path.normpath(common['fee_path'])
        
        if 'plugin_path' in common:
            self.G_PLUGIN_PATH = os.path.normpath(common['plugin_path'])
        else:
            self.G_PLUGIN_PATH = os.path.normpath(common['plugin_path_list'][0])
            
        # 20181017，td转cg过渡
        if self.G_CG_NAME == 'Maya' and self.G_RENDER_OS == '0':
            self.G_PLUGIN_PATH = self.G_PLUGIN_PATH.replace('td', 'cg')
        

        ##KAFKA
        # self.G_KAFKA_SERVER=common['kafka_server']
        # self.G_KAFKA_TOPIC=common['kafka_topic']
        ##cpu/gpu
        self.G_RENDER_CORE_TYPE = 'cpu'
        if 'render_core_type' in common:
            self.G_RENDER_CORE_TYPE = common['render_core_type']

        self.G_TIPS_JSON = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK_CFG, 'tips.json'))
        self.G_DRIVERC_7Z = os.path.normpath('d:/7-Zip/7z.exe')

        # -----------------------------------------asset.json-----------------------------------------------
        self.G_ASSET_JSON = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK_CFG, 'asset.json'))
        asset_json = os.path.join(self.G_CONFIG_PATH, 'asset.json')
        if os.path.exists(asset_json):
            
            CLASS_COMMON_UTIL.python_copy(asset_json, self.G_WORK_RENDER_TASK_CFG, my_log=self.G_DEBUG_LOG)
            # self.G_ASSET_JSON_DICT = eval(codecs.open(asset_json, 'r', 'utf-8').read())
            with codecs.open(asset_json, 'r', 'utf-8') as f_asset_json:
                self.G_ASSET_JSON_DICT = json.load(f_asset_json)
                
                
        # -----------------------------------------upload.json-----------------------------------------------
        if self.G_CHANNEL != '2': # not web
            self.G_UPLOAD_JSON = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK_CFG, 'upload.json'))
            upload_json = os.path.join(self.G_CONFIG_PATH, 'upload.json')
            if os.path.exists(upload_json):
                
                CLASS_COMMON_UTIL.python_copy(upload_json, self.G_WORK_RENDER_TASK_CFG, my_log=self.G_DEBUG_LOG)
                with codecs.open(upload_json, 'r', 'utf-8') as f_upload_json:
                    self.G_UPLOAD_JSON_DICT = json.load(f_upload_json)
                

        # -----------------------------------------fee-----------------------------------------------
        self.G_FEE_PARSER = configparser.ConfigParser()
        if not self.G_FEE_PARSER.has_section('render'):
            self.G_FEE_PARSER.add_section('render')

        # 新平台和munu不兼容平台号,最快的方法是脚本帮忙翻译平台号
        # 2 5 8 9 10--->>www2 pic www8 www9 gpu
        platform_alias = 'www2'
        if self.G_PLATFORM == '0':
            platform_alias = 'www0'
        elif self.G_PLATFORM == '1':
            platform_alias = 'www1'
        elif self.G_PLATFORM == '2':
            platform_alias = 'www2'
        elif self.G_PLATFORM == '3':
            platform_alias = 'www3'
        elif self.G_PLATFORM == '4':
            platform_alias = 'www4'
        elif self.G_PLATFORM == '20':
            platform_alias = 'pic'
        # elif self.G_PLATFORM == '8':
            # platform_alias = 'www8'
        elif self.G_PLATFORM == '9':
            platform_alias = 'www9'

        elif self.G_PLATFORM == '21':
            platform_alias = 'gpu'

        fee_dir = os.path.normpath(os.path.join(self.G_WORK, 'fee', platform_alias, self.G_MUNU_ID))
        if not os.path.exists(fee_dir):
            os.makedirs(fee_dir)
        fee_filename = r'%s_%s.ini' % (self.G_JOB_ID, self.G_RECOMMIT_FLAG)
        self.G_FEE_FILE = os.path.join(fee_dir,
                                       fee_filename)  # c:/work/fee/<platform>/<munu_task_id>/<munu_job_id>_<resubmit>.ini

        # ----------------------------------------------对全局变量进行处理---------------------------------------------------
        global_param_dict = self.__dict__
        for key, value in list(global_param_dict.items()):
            if isinstance(value, bytes):
                assign = 'self.{0} = CLASS_COMMON_UTIL.bytes_to_str(self.{0})'.format(key)
                exec (assign)
                
            # ip path to linux path
            if isinstance(value, (bytes, str)):
                exec('self.'+key+' = self.to_linux_path(self.'+key+')')
                
                # ip path to linux path
                # for linux_path, ip_path in self.G_LINUX_MAP_DICT.items():
                    # linux_path = os.path.normpath(linux_path)
                    # ip_path = os.path.normpath(ip_path)
                    # exec('self.'+key+' = os.path.normpath(self.'+key+')')
                    # exec('self.'+key+' = self.'+key+'.replace(ip_path, linux_path)')



        # --------------一机多帧----------------------

        # 记录文件
        self.render_record_json = os.path.join(self.G_WORK_RENDER_TASK_MULTIFRAME, "{task_id}_{munu_task_id}_{munu_job_id}_{frames}".format(
            munu_task_id=self.G_MUNU_ID,
            munu_job_id=self.G_JOB_ID,
            task_id=self.G_TASK_ID,
            frames=self.G_CG_FRAMES,
        ))
        self.render_record = {}
        # 完成队列
        self.multiframe_complete_list = []
        # cg 进程返回码
        self.cg_return_code = 'custom'
        #
        
        if self.G_CHANNEL == '3':  # 效果图插件提交
            self.g_one_machine_multiframe = False
        
        if self.g_one_machine_multiframe is True:
            self.pre_multiframe()

        # resolve scriptconfig.json
        script_config_json_path = os.path.join(self.G_NODE_PY, 'Base', 'scriptconfig.json')
        with codecs.open(script_config_json_path, 'r', 'utf-8') as f:
            self.SCRIPT_CONFIG_DICT = json.load(f)
            
        # --------------------------------------------
        print('[BASE.init.end.....]')
        #sys.exit(-1)

    def RB_SYSTEM_INFO(self):
        self.G_DEBUG_LOG.info("-" * 20 + "  SysTemInfo  " + "-" * 20)
        self.G_DEBUG_LOG.info("\r\nComputer Platform: %s" % CLASS_COMMON_UTIL.get_system_version())
        self.G_DEBUG_LOG.info("Computer HostName: %s" % CLASS_COMMON_UTIL.get_computer_hostname())

        self.G_DEBUG_LOG.info("Computer System: %s" % CLASS_COMMON_UTIL.get_system())
        self.G_DEBUG_LOG.info("Computer Ip: %s" % CLASS_COMMON_UTIL.get_computer_ip())
        self.G_DEBUG_LOG.info("Computer MAC: %s\r\n" % CLASS_COMMON_UTIL.get_computer_mac())

        if self.G_RENDER_OS != '0':
            lp_buffer = ctypes.create_string_buffer(78)
            ctypes.windll.kernel32.GetLogicalDriveStringsA(ctypes.sizeof(lp_buffer), lp_buffer)
            vol = lp_buffer.raw.split(b'\x00')
            for i in vol:
                if i:
                    self.G_DEBUG_LOG.info('Disk=' + str(i))

    def RB_PRE_PY(self):  # 1
        '''
            pre custom
        '''

        self.format_log('执行自定义PY脚本', 'start')
        self.G_DEBUG_LOG.info('[BASE.RB_PRE_PY.start.....]')
        self.G_DEBUG_LOG.info('如果以下自定义PY脚本存在，会执行此脚本')
        pre_py = os.path.join(self.G_NODE_PY, 'CG', self.G_CG_NAME, 'function', 'Pre.py')
        self.G_DEBUG_LOG.info(pre_py)
        if os.path.exists(pre_py):
            import Pre as PRE_PY_MODEL
            self.PRE_DICT = PRE_PY_MODEL.main()
        self.G_DEBUG_LOG.info('[BASE.RB_PRE_PY.end.....]')
        self.format_log('done', 'end')

    def RB_PRE_RESET_NODE(self):
        pass

    def RB_MAP_DRIVE(self):  # 2
        '''
            映射盘符
        '''
        self.format_log('映射盘符', 'start')
        self.G_DEBUG_LOG.info('[BASE.RB_MAP_DRIVE.start.....]')

        if self.G_RENDER_OS != '0':
            # delete all mappings
            CLASS_COMMON_UTIL.del_net_use()
            CLASS_COMMON_UTIL.del_subst()

            # net use
            b_flag = False
            if self.G_CG_NAME != 'Max' and 'mnt_map' in self.G_TASK_JSON_DICT:
                map_dict = self.G_TASK_JSON_DICT['mnt_map']
                for key, value in list(map_dict.items()):
                    value = os.path.normpath(value)

                    if os.path.exists(value):
                        map_cmd = 'net use "%s" "%s"' % (key, value)
                        # CLASS_COMMON_UTIL.cmd_python3(map_cmd,my_log=self.G_DEBUG_LOG)
                        CLASS_COMMON_UTIL.cmd(map_cmd, my_log=self.G_DEBUG_LOG)
                        if key.lower() == 'b:':
                            b_flag = True
            if not b_flag:
                b_path = os.path.normpath(self.G_PLUGIN_PATH)
                if os.path.exists(b_path):
                    map_cmd_b = 'net use B: "%s"' % (b_path)
                    CLASS_COMMON_UTIL.cmd(map_cmd_b, my_log=self.G_DEBUG_LOG, try_count=3)
        else:

            # 删除mount
            umount_cmd_list = []
            umount_cmd_list.append("mount")
            for linux_path in self.G_LINUX_MAP_DICT.keys():
                umount_cmd_list.append("grep -v '{}'".format(linux_path))
                
            # 兼容老平台
            umount_cmd_list.append("grep -v '{}'".format(r'/mnt_rayvision/p5'))
            umount_cmd_list.append("grep -v '{}'".format(r'/mnt_rayvision/o5'))
            
            umount_cmd_list.append("awk '/cifs/ {print $3} '")
            umount_cmd_list.append("xargs umount")
            
            umount_cmd = '|'.join(umount_cmd_list)
            
            exitcode = subprocess.call(umount_cmd, shell=1)
            # if exitcode not in(0,123):
                # sys.exit(exitcode)

            user = self.SCRIPT_CONFIG_DICT["common"]["common_mount_user_name"]
            pswd = self.SCRIPT_CONFIG_DICT["common"]["common_mount_password"]
            
            
            map_dict = self.G_TASK_JSON_DICT.get('mnt_map', {})
            map_dict.update(self.G_LINUX_MAP_DICT2)#mount server path
            for key, value in list(map_dict.items()):
                value = os.path.normpath(value)
                mount_str = 'mount -t cifs -o username=' + user + ',password='+ pswd +',codepage=936,iocharset=gb2312 "'+value+'" "' + key  + '"'
                if not os.path.exists(key):
                    os.makedirs(key)

                print_mount_str = re.sub(user, "******", mount_str)
                print_mount_str = re.sub(pswd, "******", print_mount_str)
                self.G_DEBUG_LOG.info("mount   : " + print_mount_str)

                CLASS_COMMON_UTIL.cmd(mount_str, try_count=3, my_shell=True)
                
            # 挂载B        
            b_path = os.path.normpath(self.G_PLUGIN_PATH)
            b_path_linux = r'/tmp/nzs-data/renderbuswork/cg'
            if not os.path.exists(b_path_linux):
                os.makedirs(b_path_linux)
            map_cmd_b = 'mount -t cifs -o username=' + user + ',password='+ pswd +',codepage=936,iocharset=gb2312 "' + b_path + '" "' + b_path_linux + '"'
            print_mount_str = re.sub(user, "******", map_cmd_b)
            print_mount_str = re.sub(pswd, "******", print_mount_str)
            self.G_DEBUG_LOG.info("mount   : " + print_mount_str)
            CLASS_COMMON_UTIL.cmd(map_cmd_b, try_count=3, my_shell=True)

        self.G_DEBUG_LOG.info('[BASE.RB_MAP_DRIVE.end.....]')
        self.format_log('done', 'end')

    def RB_HAN_FILE(self):  # 3  copy max.7z and so on
        '''
            拷贝脚本文件
        '''
        self.format_log('拷贝脚本文件', 'start')
        self.G_DEBUG_LOG.info('[BASE.RB_HAN_FILE.start.....]' + self.G_RENDER_CORE_TYPE)

        CLASS_COMMON_UTIL.python_copy(self.G_WORK_RENDER_TASK_OUTPUT, self.G_WORK_RENDER_TASK_OUTPUTBAK, mode='move', my_log=self.G_DEBUG_LOG)

        self.G_DEBUG_LOG.info('[BASE.RB_HAN_FILE.end.....]')
        self.format_log('done', 'end')

    '''
        渲染基本配置
    '''

    def RB_CONFIG_BASE(self):  # 4
        self.format_log('渲染基本配置', 'start')
        self.G_DEBUG_LOG.info('[BASE.RB_CONFIG_BASE.start.....]')

        if self.G_RENDER_OS != '0':
            # DogUtil.killMaxVray(self.G_DEBUG_LOG)  #kill 3dsmax.exe,3dsmaxcmd.exe,vrayspawner*.exe
            self.copy_7z()  # copy 7-Zip
        self.copy_black()  # copy black.xml

        self.G_DEBUG_LOG.info('[BASE.RB_CONFIG_BASE.end.....]')
        self.format_log('done', 'end')

    def RB_CONFIG(self):  # 4
        '''
            渲染配置
        '''
        self.format_log('渲染配置', 'start')
        self.G_DEBUG_LOG.info('[BASE.RB_CONFIG.start.....]')
        self.G_DEBUG_LOG.info('[BASE.RB_CONFIG.end.....]')
        self.format_log('done', 'end')

    def RB_RENDER(self):  # 5
        '''
            渲染
        '''
        self.format_log('渲染', 'start')
        self.G_DEBUG_LOG.info('[BASE.RB_RENDER.start.....]')
        self.G_DEBUG_LOG.info('[BASE.RB_RENDER.end.....]')
        self.format_log('done', 'end')

    def convert_small(self, src=None, dest=None):
        """convert small pic"""
        if self.G_RENDER_OS == '0':  #  linux
            small_pic_str = self.convert_small_linux(src, dest)
        else:
            small_pic_str = self.convert_small_windows(src, dest)
            
        return small_pic_str
        
    def convert_small_windows(self, src=None, dest=None):
        if src is None:
            src = self.G_WORK_RENDER_TASK_OUTPUT
        if dest is None:
            dest = self.G_WORK_RENDER_TASK_SMALL
            
        self.G_DEBUG_LOG.info(src)  # local small path
        self.G_DEBUG_LOG.info(dest)  # local small path
        self.G_DEBUG_LOG.info(self.G_SMALL_PATH)  # server small path
        self.G_DEBUG_LOG.info('')
        
        # exr_to_jpg = os.path.join(self.G_WORK_RENDER_TASK, 'exr2jpg')
        # exr_to_jpg_bak = os.path.join(self.G_WORK_RENDER_TASK, 'exr2jpgbak')
        
        if not os.path.exists(dest):
            os.makedirs(dest)

        small_pic_str = self.convert_dir(src, dest)
        
        # exr_to_jpg
        # if os.path.exists(exr_to_jpg):
            # self.convert_dir(exr_to_jpg, dest)
            
            # exr_to_jpg_bak_move = 'c:\\fcopy\\FastCopy.exe /cmd=move /speed=full /force_close  /no_confirm_stop /force_start "' + exr_to_jpg.replace(
                # '/', '\\') + '\\*.*" /to="' + exr_to_jpg_bak.replace('/', '\\') + '"'
            # CLASS_COMMON_UTIL.cmd(exr_to_jpg_bak_move, my_log=self.G_DEBUG_LOG)

        # move local_small_path to server_small_path
        move_cmd = 'c:\\fcopy\\FastCopy.exe /cmd=move /speed=full /force_close  /no_confirm_stop /force_start "' + dest.replace(
            '/', '\\') + '\*.*" /to="' + self.G_SMALL_PATH.replace('/', '\\') + '"'
        CLASS_COMMON_UTIL.cmd(move_cmd, my_log=self.G_DEBUG_LOG, continue_on_error=True)
        
        return small_pic_str
    
    def convert_small_linux(self, src=None, dest=None):
        """Linux 下转换缩略图, RBconvertSmallPic 的 Linux 版."""
        self.format_log('Linux 转换缩略图', 'start')
        
        if src is None:
            src = self.G_WORK_RENDER_TASK_OUTPUT
        if dest is None:
            dest = self.G_WORK_RENDER_TASK_SMALL
        
        self.G_DEBUG_LOG.info('[BASE.convert_small_pic_linux.start.....]')
        self.G_DEBUG_LOG.info('work_small_path={}'.format(dest))
        if not os.path.exists(dest):
            os.makedirs(dest)
        
        # exr_to_jpg = os.path.join(self.G_WORK_RENDER_TASK, 'exr2jpg')
        # exr_to_jpg_bak = os.path.join(self.G_WORK_RENDER_TASK, 'exr2jpgbak')
        #
        small_pic_str = self.convert_by_magick(src, dest)
        # self.convert_by_magick(exr_to_jpg, dest)
        # copy
        
        CLASS_COMMON_UTIL.python_copy(dest.replace('\\','/'), self.G_SMALL_PATH, my_log=self.G_DEBUG_LOG)

        # if os.path.exists(exr_to_jpg):
            
            # CLASS_COMMON_UTIL.python_copy(exr_to_jpg.replace('\\','/'), exr_to_jpg_bak, my_log=self.G_DEBUG_LOG)

        self.G_DEBUG_LOG.info('[BASE.convert_small_pic_linux.end.....]')
        self.format_log('done', 'end')
        
        return small_pic_str

    def convert_by_magick(self, output_path, small_path):
        if not os.path.exists(output_path):
            return ''
        size = "200"
        
        small_pic_file_name_list=[]
        for root, dirs, files in os.walk(output_path):
            for f in files:
                ext = os.path.splitext(f)[-1]

                big_pic = os.path.join(root, f)
                base_name = os.path.basename(f)  # smallName=workBigPic.replace(dir+'\\','') ???
                small_name = self.G_JOB_NAME + "_" + base_name.replace('\\', '[_]').replace('.', '[-]') + '.jpg'
                small_temp_name = self.G_JOB_NAME + "_tmp.jpg"

                small_pic_file_name_list.append(small_name.replace('\\', '/'))
                small_pic = os.path.join(small_path, small_name)
                small_tmp_pic = os.path.join(small_path, small_temp_name)

                big_pic_tmp = os.path.join(root, "tmp" + os.path.splitext(big_pic)[-1])
                self.G_DEBUG_LOG.info('-------====------')
                self.G_DEBUG_LOG.info('big_pic={}'.format(big_pic))
                self.G_DEBUG_LOG.info('big_pic_tmp={}'.format(big_pic_tmp))
                self.G_DEBUG_LOG.info('base_name={}'.format(base_name))
                self.G_DEBUG_LOG.info('small_name={}'.format(small_name))
                self.G_DEBUG_LOG.info('small_temp_name={}'.format(small_temp_name))
                self.G_DEBUG_LOG.info('small_pic={}'.format(small_pic))
                self.G_DEBUG_LOG.info('small_tmp_pic={}'.format(small_tmp_pic))
                
                
                #try:
                os.rename(big_pic, big_pic_tmp)
                #except Exception as e:
                #traceback.print_exc()
                if not os.path.exists(big_pic_tmp):
                    self.G_DEBUG_LOG.info('not exists....')
                    big_pic_tmp = big_pic
                    small_tmp_pic = small_pic
                self.G_DEBUG_LOG.info('big_pic={}'.format(big_pic))
                self.G_DEBUG_LOG.info('big_pic_tmp={}'.format(big_pic_tmp))
                self.G_DEBUG_LOG.info('--------------------------====---------------------')
                # cmd0 = '/usr/bin/identify -ping -format "%w %h" "{}"'.format(big_pic_tmp)
                # self.G_PROCESS_LOG.info("\n{}\n".format(cmd0))
                # convert_size = "200x0"
                # try:
                #     p = subprocess.Popen(cmd0, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                #     stdout, stderr = p.communicate()
                #     pattern = '(\d+) (\d+)'
                #     q = re.search(pattern, stdout)
                #     if q:
                #         width, height = q.groups()
                #         if int(height) > int(width):
                #             convert_size = "0x200"
                # except Exception as e:
                #     import traceback
                #     traceback.print_exc()
                #
                cmd = '{convert_path}  -resize {convert_size} {big_pic_tmp} {small_tmp_pic}'.format(
                    convert_path="/usr/bin/convert",
                    big_pic_tmp=big_pic_tmp,
                    small_tmp_pic=small_tmp_pic,
                    convert_size="425x260",
                )
                self.G_DEBUG_LOG.info("\n{}\n".format(cmd))
                try:
                    # os.system(cmd)
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    stdout, stderr = p.communicate()
                    self.G_DEBUG_LOG.info("[convert pic linux]result: {}, returncode: {}".format(stdout, p.returncode))
                except Exception as e:
                    import traceback
                    traceback.print_exc()

                if not big_pic_tmp == big_pic:
                    os.rename(big_pic_tmp, big_pic)
                    if os.path.exists(small_tmp_pic):
                        try:
                            os.rename(small_tmp_pic, small_pic)
                        except Exception as e:
                            traceback.print_exc()
                self.G_DEBUG_LOG.info("\nsmall_tmp_pic='{}'\nsmall_pic='{}'\nbig_pic_tmp='{}'\nbig_pic='{}'\nsmall_name='{}'".format(
                    small_tmp_pic,
                    small_pic,
                    big_pic_tmp,
                    big_pic,
                    small_name,
                ))
                #self.G_FEE_LOG.info('smallPic=' + small_name.decode(sys.getfilesystemencoding()))
        
        small_pic_file_name_list = self.sort_pic_list(small_pic_file_name_list)
        small_pic_str = '|'.join(small_pic_file_name_list)
        self.G_FEE_PARSER.set('render', 'small_pic', small_pic_str)
            
        return small_pic_str
        
    def RB_CONVERT_SMALL_PIC(self):  # 6
        '''
            转换缩略图
        '''
        if self.G_ACTION not in ['Analyze', 'Pre']:
            self.format_log('转换缩略图', 'start')
            self.G_DEBUG_LOG.info('[BASE.RB_CONVERT_SMALL_PIC.start.....]')

            big_pic_list = []
            
            for root, dirs, files in os.walk(self.G_WORK_RENDER_TASK_OUTPUT):  # generator
                for name in files:
                    work_big_pic = os.path.join(root, name)
                    big_pic_list.append(work_big_pic.replace(self.G_WORK_RENDER_TASK_OUTPUT + os.sep, '').replace('\\',
                                                                                                                  '/'))  # kafka message must use '/' , No '\'
            big_pic_str = '|'.join(big_pic_list)
            if self.G_ACTION in ['RenderPhoton', 'MergePhoton']:
                self.G_FEE_PARSER.set('render', 'big_pic', '')
            else:
                self.G_FEE_PARSER.set('render', 'big_pic', big_pic_str)

            # convert small pic
            self.convert_small()


            self.G_DEBUG_LOG.info('[BASE.RB_CONVERT_SMALL_PIC.end.....]')
            self.format_log('done', 'end')

            
    def RB_HAN_RESULT(self):  # 7
        '''
            上传渲染结果和日志
        '''
        self.format_log('.结果处理...', 'start')
        self.G_DEBUG_LOG.info('[BASE.RB_HAN_RESULT.start.....]')

        if self.G_ACTION in ['Analyze']:
            task_json_name = 'task.json'
            asset_json_name = 'asset.json'
            tips_json_name = 'tips.json'
            node_task_json = os.path.join(self.G_WORK_RENDER_TASK_CFG, task_json_name)
            node_asset_json = os.path.join(self.G_WORK_RENDER_TASK_CFG, asset_json_name)
            node_tips_json = os.path.join(self.G_WORK_RENDER_TASK_CFG, tips_json_name)

            
            if not os.path.exists(node_task_json):
                CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG, 'Analyze  file failed . task.json not exists')
                
            # if not os.path.exists(node_asset_json):
                # CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG, 'Analyze  file failed . asset.json not exists')
                
            if not os.path.exists(node_tips_json):
                CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG, 'Analyze  file failed . tips.json not exists')

            self.copy_cfg_to_server(node_task_json, node_asset_json, node_tips_json)
        else:
            self.result_action()

        self.G_DEBUG_LOG.info('[BASE.RB_HAN_RESULT.end.....]')
        self.format_log('done', 'end')

    def RB_POST_RESET_NODE(self):
        pass

    def RB_POST_PY(self):  # 8 pre custom
        self.format_log('渲染完毕执行自定义脚本', 'start')
        self.G_DEBUG_LOG.info('[BASE.RB_POST_PY.start.....]')
        self.G_DEBUG_LOG.info('如果以下路径的脚本存在，则会被执行')
        post_py = os.path.join(self.G_NODE_PY, 'CG', self.G_CG_NAME, 'function', 'Post.py')
        self.G_DEBUG_LOG.info(post_py)
        if os.path.exists(post_py):
            import Post as POST_PY_MODEL
            self.POST_DICT = POST_PY_MODEL.main()

        self.G_DEBUG_LOG.info('[BASE.RB_POST_PY.end.....]')
        self.format_log('done', 'end')

    def RB_KAFKA_NOTIFY(self):  # 9
        '''
            kafka发送消息给平台
        '''
        if self.G_ACTION not in ['Analyze', 'Pre']:
            self.format_log('kafka发送消息给平台', 'start')
            self.G_DEBUG_LOG.info('[BASE.RB_KAFKA_NOTIFY.start.....]')

            send_time = str(int(time.time()))
            self.G_KAFKA_MESSAGE_DICT["munu_task_id"] = self.G_MUNU_ID
            self.G_KAFKA_MESSAGE_DICT["munu_job_id"] = self.G_JOB_ID
            self.G_KAFKA_MESSAGE_DICT["recommit_flag"] = self.G_RECOMMIT_FLAG
            self.G_KAFKA_MESSAGE_DICT["action"] = self.G_ACTION
            self.G_KAFKA_MESSAGE_DICT['platform'] = self.G_PLATFORM
            self.G_KAFKA_MESSAGE_DICT['send_time'] = send_time
            self.G_KAFKA_MESSAGE_DICT['zone'] = self.G_ZONE
            self.G_KAFKA_MESSAGE_DICT['node_name'] = self.G_NODE_ID
            self.G_KAFKA_MESSAGE_DICT['task_id'] = self.G_TASK_ID
            self.G_KAFKA_MESSAGE_DICT['render_type'] = self.G_RENDER_CORE_TYPE
            # self.G_KAFKA_MESSAGE_DICT['start_time']=self.G_START_TIME
            # self.G_KAFKA_MESSAGE_DICT['big_pic']=[]
            # self.G_KAFKA_MESSAGE_DICT['small_pic']=[]
            # self.G_KAFKA_MESSAGE_DICT['end_time']=self.G_END_TIME
            # self.G_KAFKA_MESSAGE_DICT['distribute_node'] = '1'

            self.G_DEBUG_LOG.info('G_KAFKA_MESSAGE_DICT=' + str(self.G_KAFKA_MESSAGE_DICT))

            # write kafka message json file(e.g. C:\work\render\10002736\2017120500004_0_1.json)
            # kafka_message_filename = self.G_MUNU_ID+'_'+self.G_JOB_ID+'.json'
            kafka_message_filename = self.G_MUNU_ID + '_' + self.G_JOB_ID + '_' + self.G_RECOMMIT_FLAG + '.json'
            kafka_message_json = os.path.join(self.G_WORK_RENDER_TASK, kafka_message_filename)
            kafka_message_json_str = json.dumps(self.G_KAFKA_MESSAGE_DICT, ensure_ascii=False)
            CLASS_COMMON_UTIL.write_file(kafka_message_json_str, kafka_message_json)
            CLASS_COMMON_UTIL.python_copy(kafka_message_json, self.G_CONFIG_PATH)

            try:
                kafka_result = CLASS_KAFKA.produce(self.G_KAFKA_MESSAGE_DICT, self.G_KAFKA_SERVER, self.G_KAFKA_TOPIC)
                self.G_DEBUG_LOG.info('kafka_result=' + str(kafka_result))
            except:
                CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG, 'Send Kafka Message Failed', is_exit=False)

            self.G_DEBUG_LOG.info('[BASE.RB_KAFKA_NOTIFY.end.....]')
            self.format_log('done', 'end')

    def RB_FEE(self):

        # if not self.G_RENDER_CORE_TYPE=="gpu":
        if self.G_RENDER_OS != '0':
            CLASS_COMMON_UTIL.del_net_use()
            CLASS_COMMON_UTIL.del_subst()

        if self.G_ACTION not in ['Analyze', 'Pre']:
            self.format_log('write fee', 'start')
            self.G_DEBUG_LOG.info('[BASE.RB_FEE.start.....]')

            self.G_FEE_PARSER.set('render', 'type', self.G_RENDER_CORE_TYPE)
            # self.G_FEE_PARSER.set('render','start_time','')
            # self.G_FEE_PARSER.set('render','end_time','')
            # self.G_FEE_PARSER.set('render','big_pic','')
            # self.G_FEE_PARSER.set('render','small_pic','')
            if self.g_one_machine_multiframe is True:
                self.G_FEE_PARSER.set('render', 'big_pic', '')
                self.G_FEE_PARSER.set('render', 'small_pic', '')

            try:
                with codecs.open(self.G_FEE_FILE, 'w', 'utf-8') as fee_file:
                    self.G_FEE_PARSER.write(fee_file)
            except Exception as e:
                CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG, 'Write Fee File Failed', is_exit=False)

            self.G_DEBUG_LOG.info('[BASE.RB_FEE.end.....]')
            self.format_log('done', 'end')

    def RB_RESOURCE_MONITOR(self):
        self.G_DEBUG_LOG.info('[BASE.RB_RESOURCE_MONITOR start]')
        # parse B:\config\cg_process.json
        cg_process_path = r'B:\config\cg_process.json'
        resource_monitor = r'C:\work\munu_client\resource_monitor\resource_monitor.exe'  # resource_monitor  #1
        if self.G_RENDER_OS == '0':
            resource_monitor = r'/home/tools/munu_client/resource_monitor/resource_monitor'
            cg_process_path = r'/tmp/nzs-data/renderbuswork/cg/config/cg_process_linux.json'

        if not os.path.exists(cg_process_path):
            self.G_DEBUG_LOG.info('[warn]%s is not exists!!!' % cg_process_path)
        else:
            # cg_process_dict = eval(codecs.open(cg_process_path, 'r', 'utf-8').read())
            with codecs.open(cg_process_path, 'r', 'utf-8') as f_cg_process:
                cg_process_dict = json.load(f_cg_process)

            # xxx.exe "3dsmax.exe" "1-5|19126418|1868556|3dsmax|vray,multiscatter"
            if not os.path.exists(resource_monitor):
                self.G_DEBUG_LOG.info('[warn]%s is not exists!!!' % resource_monitor)
            else:
                if self.G_ACTION not in ['Analyze', 'Pre'] and self.G_CG_NAME in cg_process_dict:
                    process_name_list = cg_process_dict[self.G_CG_NAME]
                    if len(process_name_list) <= 0:
                        self.G_DEBUG_LOG.info(
                            '[warn]The list of key %s in the %s is empty!!!' % (self.G_CG_NAME, cg_process_path))
                    else:
                        # process_name = process_name_list[self.G_CG_PROCESS_FLAG]  #2
                        process_name = '|'.join(process_name_list)  # 2
                        # render_frame = self.G_CG_START_FRAME  #3
                        # if self.G_CG_START_FRAME != self.G_CG_END_FRAME:
                        # render_frame = self.G_CG_START_FRAME + '-' + self.G_CG_END_FRAME + '[' + self.G_CG_BY_FRAME + ']'
                        # self.G_JOB_ID  #3
                        # self.G_TASKID  #4
                        # self.G_USERID  #5
                        cg_flag = self.G_CG_VERSION  # 6
                        plugin_string = r''  # 7
                        if 'plugins' in self.G_CG_CONFIG_DICT:
                            for key, value in list(self.G_CG_CONFIG_DICT['plugins'].items()):
                                plugin_string += key + value + ','
                            plugin_string = plugin_string.strip(',')

                        if not plugin_string:
                            plugin_string = r'None'

                        command = r'{} "{}" "{}|{}|{}|{}|{}"'.format(
                            resource_monitor,
                            process_name,
                            self.G_JOB_ID,
                            self.G_TASK_ID,
                            self.G_USER_ID,
                            cg_flag,
                            plugin_string,
                        )

                        self.monitor_cmd(command)
                        # t = threading.Thread(target=self.monitor_cmd, args=(command, resource_monitor,))
                        # t.daemon = True
                        # t.start()
                        
                        
        if self.g_one_machine_multiframe is True:
            self.monitor_complete_thread.start()

        self.G_DEBUG_LOG.info('[BASE.RB_RESOURCE_MONITOR end]')

    def monitor_cmd(self, command):
        self.G_DEBUG_LOG.info(command)
        # register(self.monitor_exit, resource_monitor)
        # os.system(command)
        
        if self.G_RENDER_OS == '0':  # G_RENDER_OS:0 linux ,1 windows
            cmdp = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        else:
            # 子进程会随着父进程退出而退出，且会显示子进程的控制台窗口
            cmdp = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, creationflags=subprocess.CREATE_NEW_CONSOLE)

            
    def monitor_exit(self, resource_monitor):
        self.G_DEBUG_LOG.info('[monitor_exit]start...')
        software_name = os.path.basename(resource_monitor)

        kill_cmd = r'taskkill /F /IM %s /T' % software_name
        if self.G_RENDER_OS == '0':
            kill_cmd = r"ps -ef | grep -i %s | grep -v grep | awk '{print $2}' | xargs kill -9" % software_name

        os.system(kill_cmd)
        self.G_DEBUG_LOG.info('[monitor_exit]end...')

    def init_log(self):
        '''
            初始化日志
        '''
        log_dir = os.path.join(self.G_LOG_WORK, self.G_TASK_ID)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        fm = logging.Formatter("%(asctime)s  %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
        # debug_log 不能开放给客户查看
        debug_log_path = os.path.join(log_dir, (self.G_ACTION_ID + '_debug.log'))
        self.G_DEBUG_LOG.setLevel(logging.DEBUG)
        debug_log_handler = logging.FileHandler(debug_log_path, encoding='utf-8')
        debug_log_handler.setFormatter(fm)
        self.G_DEBUG_LOG.addHandler(debug_log_handler)
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        self.G_DEBUG_LOG.addHandler(console)

        # render_log 可开放给客户查看
        self.render_log_path = os.path.join(log_dir, (self.G_ACTION_ID + '_render.log'))
        self.G_RENDER_LOG.setLevel(logging.DEBUG)
        render_log_handler = logging.FileHandler(self.render_log_path, encoding='utf-8')
        render_log_handler.setFormatter(fm)
        self.G_RENDER_LOG.addHandler(render_log_handler)
        self.G_RENDER_LOG.addHandler(debug_log_handler)
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        self.G_RENDER_LOG.addHandler(console)

    def make_dir(self):
        '''
            创建目录
        '''
        self.G_DEBUG_LOG.info('[BASE.make_dir.start.....]')
        self.G_DEBUG_LOG.info('创建以下路径的目录：')
        self.G_DEBUG_LOG.info(self.G_WORK_RENDER)
        self.G_DEBUG_LOG.info(self.G_WORK_RENDER_TASK)
        self.G_DEBUG_LOG.info(self.G_WORK_RENDER_TASK_CFG)
        '''
        self.G_DEBUG_LOG.info(self.G_WORK_RENDER_TASK_BLOCK)
        self.G_DEBUG_LOG.info(self.G_WORK_RENDER_TASK_GRAB)
        self.G_DEBUG_LOG.info(self.G_WORK_RENDER_TASK_MAX)
        self.G_DEBUG_LOG.info(self.G_WORK_RENDER_TASK_MAXBAK)
        '''
        self.G_DEBUG_LOG.info(self.G_WORK_RENDER_TASK_OUTPUT)
        self.G_DEBUG_LOG.info(self.G_WORK_RENDER_TASK_OUTPUTBAK)
        self.G_DEBUG_LOG.info(self.G_WORK_RENDER_TASK_SMALL)
        # render
        if not os.path.exists(self.G_WORK_RENDER):
            os.makedirs(self.G_WORK_RENDER)
        # renderwork
        if not os.path.exists(self.G_WORK_RENDER_TASK):
            os.makedirs(self.G_WORK_RENDER_TASK)
            # renderwork/cfg
        if not os.path.exists(self.G_WORK_RENDER_TASK_CFG):
            os.makedirs(self.G_WORK_RENDER_TASK_CFG)
        '''
        #renderwork/block
        if not os.path.exists(self.G_WORK_RENDER_TASK_BLOCK):
            os.makedirs(self.G_WORK_RENDER_TASK_BLOCK)
        #renderwork/grab
        if not os.path.exists(self.G_WORK_RENDER_TASK_GRAB):
            os.makedirs(self.G_WORK_RENDER_TASK_GRAB)
        #renderwork/max
        if not os.path.exists(self.G_WORK_RENDER_TASK_MAX):
            os.makedirs(self.G_WORK_RENDER_TASK_MAX)
        #renderwork/maxbak
        if not os.path.exists(self.G_WORK_RENDER_TASK_MAXBAK):
            os.makedirs(self.G_WORK_RENDER_TASK_MAXBAK)
        '''
        # renderwork/output
        if not os.path.exists(self.G_WORK_RENDER_TASK_OUTPUT):
            os.makedirs(self.G_WORK_RENDER_TASK_OUTPUT)
            # renderwork/outputbak
        if not os.path.exists(self.G_WORK_RENDER_TASK_OUTPUTBAK):
            os.makedirs(self.G_WORK_RENDER_TASK_OUTPUTBAK)
        # renderwork/small
        if not os.path.exists(self.G_WORK_RENDER_TASK_SMALL):
            os.makedirs(self.G_WORK_RENDER_TASK_SMALL)
        if self.g_one_machine_multiframe is True:
            if not os.path.exists(self.G_WORK_RENDER_TASK_MULTIFRAME):
                os.makedirs(self.G_WORK_RENDER_TASK_MULTIFRAME)
            if not os.path.exists(self.G_WORK_RENDER_TASK_MULTIFRAME_BAK):
                os.makedirs(self.G_WORK_RENDER_TASK_MULTIFRAME_BAK)
        self.G_DEBUG_LOG.info('[BASE.make_dir.end.....]')

    def format_log(self, log_str, log_type='common'):
        '''
            格式化日志
        '''
        if log_str is None:
            log_str = ''
        if log_type != 'system':
            log_str = CLASS_COMMON_UTIL.bytes_to_str(log_str)

        if log_type == 'start':
            self.G_DEBUG_LOG.info('----------------------------[' + log_str + ']----------------------------\r\n')
        elif log_type == 'end':
            self.G_DEBUG_LOG.info('[' + log_str + ']\r\n')
        else:
            self.G_DEBUG_LOG.info(log_str + '\r\n')

    def copy_black(self):
        '''
            拷贝弹窗黑名单 black.xml
        '''
        self.G_DEBUG_LOG.info('[BASE.copy_black.start.....]')
        block_path = 'B:\\tools\\sweeper\\black.xml'
        base_path = 'c:\\work\\munu_client\\sweeper\\'
        if self.G_RENDER_OS == '0':
            block_path = "\\B\\tools\\sweeper\\black.xml"
            base_path = "/root/rayvision/work/munu_client/sweeper/"
        self.G_DEBUG_LOG.info(block_path + '>' + base_path)
        if os.path.exists(block_path):
            
            CLASS_COMMON_UTIL.python_copy(block_path, base_path, my_log=self.G_DEBUG_LOG)
        self.G_DEBUG_LOG.info('[BASE.copy_black.end.....]')

    def sort_pic_list(self, pic_list):
        """ Returns list.
            功能：将缩略图列表重新排序。
            这将影响平台展示给客户的缩略图顺序，
            默认对列表不做任何修改操作，如需则在各自软件的脚本中重写该方法
            如：max重写该方法实现了将主图缩略图排在列表最前面，方便平台展示给客户（第一张即为主图）
        """
        return pic_list

    def convert_dir(self, big_pic_dir, small_pic_dir):
        """
        转换缩略图
            1.大图源文件 重命名为 大图临时文件（排除编码的影响）
            2.将 大图临时文件 转缩略图为 缩略图临时文件
            3.将 缩略图临时文件 重命名为 缩略图目标文件
        :param str big_pic_dir: 大图存放路径
        :param str small_pic_dir: 缩略图存放路径
        :rerurn: small_pic_str or ''
        :rtype: str
        """
        self.G_DEBUG_LOG.info('[BASE.convert_dir.start.....]')

        big_pic_dir = os.path.normpath(big_pic_dir)
        small_pic_dir = os.path.normpath(small_pic_dir)
        small_pic_str = ''
        
        if os.path.exists(big_pic_dir):
            if self.G_CHANNEL == '3':  # 效果图插件提交
                small_width = '640'
                small_height = '640'
            else:
                small_width = '425'
                small_height = '260'
            small_pic_file_name_list = []

            for root, dirs, files in os.walk(big_pic_dir):  # generator
                for big_pic_file_name in files:
                    self.G_DEBUG_LOG.info('')  # 分隔日志
                    self.G_DEBUG_LOG.info('big_pic_file_name=' + big_pic_file_name)
                    
                    big_pic_file_path = os.path.join(root, big_pic_file_name)
                    big_pic_file_name_tuple = os.path.splitext(big_pic_file_name)  # ('demo', '.jpg')
                    big_pic_file_name_root = big_pic_file_name_tuple[0]  # 'demo'
                    big_pic_file_name_ext = big_pic_file_name_tuple[1]  # '.jpg'
                    
                    if big_pic_file_name_ext in ['.vrmap', '.vrlmap', '.vrimg']:
                        continue
                        
                    big_pic_relative_file_path = big_pic_file_path[len(big_pic_dir) + 1:]  # 相对路径，不以（反）斜杠开头
                    
                    small_pic_file_name = '{action_id}_{path_str}.jpg'.format(
                        action_id=self.G_ACTION_ID,
                        path_str=big_pic_relative_file_path.replace('\\', '[_]').replace('/', '[_]').replace('.', '[-]'),
                    )
                    small_pic_file_path = os.path.join(small_pic_dir, small_pic_file_name)

                    small_pic_file_name_list.append(small_pic_file_name.replace('\\', '/'))
                    
                    small_pic_file_path_tmp = os.path.join(small_pic_dir, self.G_ACTION_ID + '_tmp.jpg')
                    big_pic_file_path_tmp = os.path.join(root, 'tmp{}'.format(big_pic_file_name_ext))
                    
                    # 1.大图源文件 重命名为 大图临时文件
                    # 如果重命名失败，保持原子性
                    try:
                        os.rename(big_pic_file_path, big_pic_file_path_tmp)
                    except Exception as e:
                        self.G_DEBUG_LOG.info('[warn]rename big_pic_file_path to big_pic_file_path_tmp failed-----')
                        big_pic_file_path_tmp = big_pic_file_path
                        small_pic_file_path_tmp = small_pic_file_path
                    
                    self.G_DEBUG_LOG.info('big_pic_file_path---{}'.format(big_pic_file_path))
                    self.G_DEBUG_LOG.info('big_pic_file_path_tmp---{}'.format(big_pic_file_path_tmp))
                    self.G_DEBUG_LOG.info('small_pic_file_path_tmp---{}'.format(small_pic_file_path_tmp))
                    self.G_DEBUG_LOG.info('small_pic_file_path---{}'.format(small_pic_file_path))
                    
                    # 确定转换命令行
                    # 不判断工具是否存在，不存在则会在执行时报错跳过；如果判断的话需要保持原子性则修改动作较大
                    if big_pic_file_name_ext in ['.exr']:
                        # 用oiiotool转换exr
                        # 201809 oiiotool转换 包含通道的exr图 时会崩溃，可用nuke
                        
                        # oiio_path = r'c:\oiio\OpenImageIO-1.5.18-bin-vc9-x64\oiiotool.exe'
                        # convert_cmd = '{exe_path} "{converted_file}" -resize {width_x_height} -o "{output_file}"'.format(
                            # exe_path=oiio_path,
                            # output_file=small_pic_file_path_tmp,
                            # converted_file=big_pic_file_path_tmp,
                            # width_x_height=self.get_convert_r(big_pic_file_path_tmp, oiio_path, small_width, small_height),
                        # )
                        
                        py_path = os.path.join(r'C:\script\new_py\Util', "nuke_convert_small_pic.py")
                        nuke_path = ''
                        nuke_path1 = os.path.join(r'C:\Program Files\Nuke10.0v4', 'Nuke10.0.exe')
                        nuke_path2 = os.path.join(r'C:\Program Files\Nuke9.0v9', 'Nuke9.0.exe')
                        nuke_path3 = os.path.join(r'C:\Program Files\Nuke10.0v6', 'Nuke10.0.exe')
                        nuke_path4 = os.path.join(r'C:\Program Files\Nuke9.0v6', 'Nuke9.0.exe')
                        nuke_path5 = os.path.join(r'C:\Program Files\Nuke10.5v5', 'Nuke10.5.exe')
                        nuke_path6 = os.path.join(r'C:\Program Files\Nuke8.0v3', 'Nuke8.0.exe')
                        nuke_path7 = os.path.join(r'C:\Program Files\Nuke10.0v6', 'Nuke.exe')
                        nuke_path8 = os.path.join(r'B:\nuke\Nuke10.5v5', 'Nuke10.5.exe')
                        if os.path.isfile(nuke_path1):
                            nuke_path = nuke_path1
                        elif os.path.isfile(nuke_path2):
                            nuke_path = nuke_path2
                        elif os.path.isfile(nuke_path3):
                            nuke_path = nuke_path3
                        elif os.path.isfile(nuke_path4):
                            nuke_path = nuke_path4
                        elif os.path.isfile(nuke_path5):
                            nuke_path = nuke_path5
                        elif os.path.isfile(nuke_path6):
                            nuke_path = nuke_path6
                        elif os.path.isfile(nuke_path7):
                            nuke_path = nuke_path7
                        elif os.path.isfile(nuke_path8):
                            nuke_path = nuke_path8
                        else:
                            self.G_DEBUG_LOG.info("[warn]nuke is not exists!")
                            
                        if not os.path.isfile(py_path):
                            self.G_DEBUG_LOG.info("[warn]nuke_convert_small_pic.py is not exists!")
                            
                        try:
                            os.environ['foundry_LICENSE'] = "4101@127.0.0.1;4101@10.60.1.108;4101@10.60.5.248;4101@10.30.96.203"
                        except Exception as e:
                            self.G_DEBUG_LOG.info("set environ for nuke error:\n{}".format(e))
                            
                        convert_cmd = r'"{nuke_path}" -t "{py_path}" "{width}" "{height}" "{input_file}" "{output_file}"'.format(
                            nuke_path=nuke_path,
                            py_path=py_path,
                            width=small_width,
                            height=small_height,
                            input_file=big_pic_file_path_tmp,
                            output_file=small_pic_file_path_tmp,
                        ).replace("\\", '/')
                    else:
                        # 用nconvert转换缩略图
                        nconvert_path = r'c:/ImageMagick/nconvert.exe'
                        # convert_cmd = '{exe_path} -out jpeg -ratio -resize {w} {h} -overwrite -o "{output_file}" "{converted_file}"'.format(
                        convert_cmd = '{exe_path} -out jpeg -ratio -resize {w} {h} -overwrite -o "{output_file}" "{converted_file}"'.format(
                            exe_path=nconvert_path,
                            w=small_width,
                            h=small_height,
                            output_file=small_pic_file_path_tmp,
                            converted_file=big_pic_file_path_tmp
                        )
                        
                    # 2.将 大图临时文件 转缩略图为 缩略图临时文件
                    CLASS_COMMON_UTIL.cmd(convert_cmd, my_log=self.G_DEBUG_LOG, continue_on_error=True)
                        
                    # 3.将 缩略图临时文件 重命名为 缩略图目标文件
                    if big_pic_file_path_tmp != big_pic_file_path:
                        os.rename(big_pic_file_path_tmp, big_pic_file_path)
                        if os.path.exists(small_pic_file_path_tmp):
                            try:
                                os.rename(small_pic_file_path_tmp, small_pic_file_path)
                            except Exception as e:
                                pass
                        
                    self.G_DEBUG_LOG.info('')  # 分隔日志

            small_pic_file_name_list = self.sort_pic_list(small_pic_file_name_list)

            small_pic_str = '|'.join(small_pic_file_name_list)
            self.G_FEE_PARSER.set('render', 'small_pic', small_pic_str)

        self.G_DEBUG_LOG.info('[BASE.convert_dir.end.....]')
        return small_pic_str

    def check_result(self):
        self.G_DEBUG_LOG.info('================[check_result]===============')
        # server_output=self.G_OUTPUT_USER_PATH.encode(sys.getfilesystemencoding())
        server_output = self.G_OUTPUT_USER_PATH
        node_output = self.G_WORK_RENDER_TASK_OUTPUT.replace('\\', '/')
        self.G_DEBUG_LOG.info('')
        self.G_DEBUG_LOG.info(node_output)
        self.G_DEBUG_LOG.info(server_output)
        self.G_DEBUG_LOG.info('')
        node_img_dict = {}
        server_img_dict = {}
        # output_list = os.listdir(node_output)
        # if not output_list:
            # CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG, 'output is empty!')
            
        is_empty = True
        
        for root, dirs, files in os.walk(node_output):
            for name in files:
                is_empty = False
                # ------------node output file----------------
                node_img_file = os.path.join(root, name).replace('\\', '/')
                img_file = node_img_file.replace(node_output, '')

                img_file_stat = os.stat(node_img_file)
                img_file_size = str(os.path.getsize(node_img_file))
                node_img_dict[img_file] = img_file_size
                date = datetime.datetime.fromtimestamp(img_file_stat.st_ctime)
                img_file_ctime = date.strftime('%Y%m%d%H%M%S')
                # img_file_ctime=str(img_file_stat.st_ctime)
                img_file_info = '[node]' + img_file + ' [' + img_file_size + '] [' + img_file_ctime + ']'

                self.G_DEBUG_LOG.info(img_file_info)
                # ------------server output file----------------
                server_img_file = (server_output + img_file).replace('/', '\\')
                server_img_file_info = ''
                if os.path.exists(server_img_file):
                    img_file_stat = os.stat(server_img_file)
                    img_file_size = str(os.path.getsize(server_img_file))

                    date = datetime.datetime.fromtimestamp(img_file_stat.st_ctime)
                    img_file_ctime = date.strftime('%Y%m%d%H%M%S')
                    server_img_file_info = '[server]' + img_file + ' [' + img_file_size + '] [' + img_file_ctime + ']'
                    server_img_dict[img_file] = img_file_size
                else:
                    server_img_file_info = '[server]' + img_file + ' [missing]'

                self.G_DEBUG_LOG.info(server_img_file_info)
                self.G_DEBUG_LOG.info('')

        if is_empty:
            CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG, 'output is empty!')
                
        self.G_DEBUG_LOG.info('')

    def result_action(self):
        '''
            上传渲染结果和日志
        '''
        self.G_DEBUG_LOG.info('[BASE.result_action.start.....]')
        # RB_small
        if self.G_RENDER_OS == '0':
            output_path = self.G_OUTPUT_USER_PATH
            if self.G_CG_TILE_COUNT != '1' and self.G_CG_TILE_COUNT != self.G_CG_TILE:
                output_path = self.G_TILES_PATH
            
            if not os.path.exists(output_path):
                CLASS_COMMON_UTIL.make_dir(output_path)

            self.rendering_copy_notify()

            
            CLASS_COMMON_UTIL.python_copy(self.G_WORK_RENDER_TASK_OUTPUT, output_path, my_log=self.G_DEBUG_LOG)
            
            FrameCheckerLinux.main(self.G_WORK_RENDER_TASK_OUTPUT, output_path, my_log=self.G_DEBUG_LOG)
            
            
            CLASS_COMMON_UTIL.python_copy(self.G_WORK_RENDER_TASK_OUTPUT, self.G_WORK_RENDER_TASK_OUTPUTBAK, mode='move', my_log=self.G_DEBUG_LOG)
            self.copy_log()  # copy render log to output(linux only)
        else:
            if not os.path.exists(self.G_SMALL_PATH):
                CLASS_COMMON_UTIL.make_dir(self.G_SMALL_PATH)
        
            # output=self.G_OUTPUT_USER_PATH.encode(sys.getfilesystemencoding())
            output = self.G_OUTPUT_USER_PATH
            if self.G_CG_TILE_COUNT != '1' and self.G_CG_TILE_COUNT != self.G_CG_TILE:
                output = self.G_TILES_PATH

            cmd1 = 'c:\\fcopy\\FastCopy.exe  /speed=full /force_close  /no_confirm_stop /force_start "' + self.G_WORK_RENDER_TASK_OUTPUT.replace(
                '/', '\\') + '" /to="' + output + '"'
            # cmd2='"' +frame_check + '" "' + self.G_WORK_RENDER_TASK_OUTPUT + '" "'+ output.rstrip()+'"'
            cmd3 = 'c:\\fcopy\\FastCopy.exe /cmd=move /speed=full /force_close  /no_confirm_stop /force_start "' + self.G_WORK_RENDER_TASK_OUTPUT.replace(
                '/', '\\') + '\\*.*" /to="' + self.G_WORK_RENDER_TASK_OUTPUTBAK.replace('/', '\\') + '"'

            self.rendering_copy_notify()

            CLASS_COMMON_UTIL.cmd(cmd1, my_log=self.G_DEBUG_LOG, try_count=3)
            # CLASS_COMMON_UTIL.cmd_python3(cmd1,my_log=self.G_DEBUG_LOG)
            try:
                self.check_result()
            except Exception as e:
                print('[check_result.err]')
                print(e)
            # CLASS_FRAME_CHECKER.main(self.G_WORK_RENDER_TASK_OUTPUT, output, my_log=self.G_DEBUG_LOG)
            # CLASS_COMMON_UTIL.cmd(cmd2,my_log=self.G_DEBUG_LOG)
            CLASS_COMMON_UTIL.cmd(cmd3, my_log=self.G_DEBUG_LOG, try_count=3, continue_on_error=True)
        
        self.G_DEBUG_LOG.info('[BASE.result_action.end.....]')

    def get_convert_r(self, path, oiio_path, width, height):
        small_size = '{}x{}'.format(width, height)
        try:
            width = int(width)
            height = int(height)

            cmd = oiio_path + ' -info "' + path + '"'
            ratio = width / (height * 1.0)

            self.G_DEBUG_LOG.info(cmd)
            cmdp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout, stderr = cmdp.communicate()
            stdout = stdout.decode()
            self.G_DEBUG_LOG.info("[get_convert_r] stdout: \n{}".format(stdout))
            info_array = stdout[stdout.rfind(':') + 1:stdout.find(',')].split("x")
            src_width = int(info_array[0])
            src_height = int(info_array[1])
            src_ratio = src_width / (src_height * 1.0)

            if src_ratio > ratio:
                small_size = '{}x0'.format(width)
            else:
                small_size = '0x{}'.format(height)
            # while cmdp.poll() is None:
                # result_line = cmdp.stdout.readline()
                # self.G_DEBUG_LOG.info(result_line)
                # if result_line:
                    # if result_line.strip():
                        # result_line = result_line.decode(sys.getfilesystemencoding())
                        # info_array = result_line[result_line.rfind(':') + 1:result_line.find(',')].split("x")
                        # src_width = int(info_array[0])
                        # src_height = int(info_array[1])
                        # src_ratio = src_width / (src_height * 1.0)

                        # if src_ratio > ratio:
                            # small_size = '{}x0'.format(width)
                        # else:
                            # small_size = '0x{}'.format(height)
                # else:
                    # break
        except Exception as e:
            print('[getoiiosize.err]')
            print(e)
        return small_size

    def copy_7z(self):
        zip = os.path.join(self.G_PLUGIN_PATH, 'tools', '7-Zip')
        copy_7z_cmd = r'c:\fcopy\FastCopy.exe /speed=full /force_close /no_confirm_stop /force_start "' + zip.replace(
            '/', '\\') + '" /to="d:\\"'
        CLASS_COMMON_UTIL.cmd(copy_7z_cmd, my_log=self.G_DEBUG_LOG)

    def copy_cfg_to_server(self, node_task_json, node_asset_json, node_tips_json):
        self.G_DEBUG_LOG.info('[BASE.RBhanResult.node_task_json.....]' + node_task_json)
        self.G_DEBUG_LOG.info('[BASE.RBhanResult.node_asset_json.....]' + node_asset_json)
        self.G_DEBUG_LOG.info('[BASE.RBhanResult.node_tips_json.....]' + node_tips_json)
        
        
        CLASS_COMMON_UTIL.python_copy(node_task_json, self.G_CONFIG_PATH, my_log=self.G_DEBUG_LOG)
        
        
        CLASS_COMMON_UTIL.python_copy(node_asset_json, self.G_CONFIG_PATH, my_log=self.G_DEBUG_LOG)
        
        
        CLASS_COMMON_UTIL.python_copy(node_tips_json, self.G_CONFIG_PATH, my_log=self.G_DEBUG_LOG)

    def rendering_copy_notify(self, start_or_end='0'):
        """Notify platform the script executing a copy action, the user can't stop the task at this time."""

        # url = r'http://172.16.4.27:8980/api/rendering/task/common/renderingCopyInterface'
        # api_json_dir = r'\\10.60.100.104\new_render_data\input\p\api'  # from task.json
        api_json_dir = self.G_API_PATH
        api_json_path = os.path.join(api_json_dir, 'rendering_interface.json')
        success = False
        if os.path.exists(api_json_path):
            rendering_copy_interface_list = []  # select API randomly in this list
            api_json_dict = CLASS_COMMON_UTIL.json_load(api_json_path)
            rendering_copy_interfaces = api_json_dict['rendering_copy_interface']  # list or string
            if isinstance(rendering_copy_interfaces, list):
                rendering_copy_interface_list.extend(rendering_copy_interfaces)
            else:
                rendering_copy_interface_list.append(rendering_copy_interfaces)

            random.shuffle(rendering_copy_interface_list)  # random list

            data = {
                "munuTaskId": self.G_MUNU_ID,
                "munuJobId": self.G_JOB_ID,
                "platform": self.G_PLATFORM,
                "reCommitFlag": self.G_RECOMMIT_FLAG,
                "startOrEnd": start_or_end  # 0:start copy, 1:end copy
            }
            headers = {'Content-Type': 'application/json'}

            for rendering_copy_interface in rendering_copy_interface_list:
                self.G_DEBUG_LOG.info('rendering_copy_interface: {}'.format(rendering_copy_interface))
                request = urllib.request.Request(
                    url=rendering_copy_interface,
                    headers=headers,
                    data=json.dumps(data).encode('utf-8'),  # TODO test param: ensure_ascii=True
                )
                try:
                    response = urllib.request.urlopen(request)
                    self.G_DEBUG_LOG.info("[send]: {}\n[response] {}".format(start_or_end, response.read().decode("utf-8")))
                    success = True
                    break
                except urllib.error.HTTPError as e:
                    self.G_DEBUG_LOG.info('[err]HTTP error: {}\n{}'.format(rendering_copy_interface, e))
                    continue
                except urllib.error.URLError as e:
                    self.G_DEBUG_LOG.info('[err]url can\'t open: {}\n{}'.format(rendering_copy_interface, e))
                    continue
                except Exception as e:
                    self.G_DEBUG_LOG.info('[err] Exception: {}'.format(e))
                    continue
        else:
            self.G_DEBUG_LOG.info('[warn]file not found:%s' % api_json_path)
        self.G_DEBUG_LOG.info('[BASE.rendering_copy_notify.end.....]')
        return success

    def pre_multiframe(self):
        if self.G_RENDER_CONTINUE == "true":
            # 继续渲染, 先拷贝 渲染记录.json 到本地
            remote_render_record_json = os.path.join(self.G_REMOTE_TASK_CFG, os.path.basename(self.render_record_json))
            if os.path.exists(remote_render_record_json):
                CLASS_COMMON_UTIL.python_copy(remote_render_record_json, self.G_WORK_RENDER_TASK_MULTIFRAME, my_log=self.G_DEBUG_LOG, try_count=3)

            frames = self.remain_frames()
        else:
            # 重新渲染
            print("self.G_RECOMMIT_FLAG == {} and self.G_RENDER_CONTINUE == {}".format(self.G_RECOMMIT_FLAG, self.G_RENDER_CONTINUE))
            frames = self.G_CG_FRAMES

        render_list = CLASS_COMMON_UTIL.need_render_from_frame(frames)
        # 监控线程
        t = threading.Thread(target=self.loop_handle_complete, args=(render_list,))
        self.monitor_complete_thread = t

        start_frame, end_frame, by_frame = CLASS_COMMON_UTIL.find_frame(frames)
        self.G_CG_FRAMES = frames
        self.G_CG_START_FRAME = start_frame
        self.G_CG_END_FRAME = end_frame
        self.G_CG_BY_FRAME = by_frame

    def save_render_info(self, frame):
        """
        把一机多帧渲染完成的帧记录到json
        :param frame:
        :return:
        """
        if os.path.isfile(self.render_record_json):
            obj = CLASS_COMMON_UTIL.json_load(self.render_record_json)
            frame_list = obj['completed']
            frame_list.append(frame)
            CLASS_COMMON_UTIL.json_save(self.render_record_json, obj)
        else:
            frame_list = [frame]
            obj = {
                "completed": frame_list,  # ['1', '3']
            }
            CLASS_COMMON_UTIL.json_save(self.render_record_json, obj)
        # 上传
        CLASS_COMMON_UTIL.python_copy(self.render_record_json, self.G_REMOTE_TASK_CFG, my_log=self.G_DEBUG_LOG)
        
        # 复制到 multiframe_bak
        CLASS_COMMON_UTIL.python_copy(self.render_record_json, self.G_WORK_RENDER_TASK_MULTIFRAME_BAK, my_log=self.G_DEBUG_LOG)
        

    def handle_file(self, frame):
        '''
            上传渲染结果和日志
        '''
        self.G_DEBUG_LOG.info('[Base.handle_file.start.....]')
        frame = frame.zfill(4)
        
        if self.G_RENDER_OS == '0':
            output_path = self.G_OUTPUT_USER_PATH
            local_output = os.path.join(self.G_WORK_RENDER_TASK_OUTPUT, frame)
            local_outputbak = os.path.join(self.G_WORK_RENDER_TASK_OUTPUTBAK, frame)

            if not os.path.exists(output_path):
                CLASS_COMMON_UTIL.make_dir(output_path)

            self.rendering_copy_notify()
            
            CLASS_COMMON_UTIL.python_copy(local_output, output_path, my_log=self.G_DEBUG_LOG)
            
            FrameCheckerLinux.main(local_output, output_path, my_log=self.G_DEBUG_LOG)
            
            CLASS_COMMON_UTIL.python_copy(local_output, local_outputbak, mode='move', my_log=self.G_DEBUG_LOG)
            shutil.rmtree(local_output)  # delete empty directory
        else:
            # RB_small
            if not os.path.exists(self.G_SMALL_PATH):
                CLASS_COMMON_UTIL.make_dir(self.G_SMALL_PATH)
        
            # output=self.G_OUTPUT_USER_PATH.encode(sys.getfilesystemencoding())
            output = self.G_OUTPUT_USER_PATH
            
            if self.G_CG_TILE_COUNT != '1' and self.G_CG_TILE_COUNT != self.G_CG_TILE:
                output = self.G_TILES_PATH

            if not os.path.exists(output):
                os.makedirs(output)

            cmd1 = '{fcopy_path} /speed=full /force_close /no_confirm_stop /force_start "{source}" /to="{destination}"'.format(
                fcopy_path='c:\\fcopy\\FastCopy.exe',
                source=os.path.join(self.G_WORK_RENDER_TASK_OUTPUT.replace('/', '\\'), frame),
                destination=output.replace('/', '\\'),
            )

            cmd3 = '{fcopy_path} /speed=full /cmd=move /force_close /no_confirm_stop /force_start "{source}" /to="{destination}"'.format(
                fcopy_path='c:\\fcopy\\FastCopy.exe',
                source=os.path.join(self.G_WORK_RENDER_TASK_OUTPUT.replace('/', '\\'), frame),
                destination=self.G_WORK_RENDER_TASK_OUTPUTBAK.replace('/', '\\'),
            )

            CLASS_COMMON_UTIL.cmd(cmd1, my_log=self.G_DEBUG_LOG, try_count=3)
            # CLASS_COMMON_UTIL.cmd_python3(cmd1,my_log=self.G_DEBUG_LOG)
            try:
                self.check_result()
            except Exception as e:
                print('[check_result.err]')
                print(e)
            # CLASS_FRAME_CHECKER.main(self.G_WORK_RENDER_TASK_OUTPUT, output, my_log=self.G_DEBUG_LOG)
            # CLASS_COMMON_UTIL.cmd(cmd2,my_log=self.G_DEBUG_LOG)
            CLASS_COMMON_UTIL.cmd(cmd3, my_log=self.G_DEBUG_LOG, try_count=3, continue_on_error=True)
        self.G_DEBUG_LOG.info('[Base.handle_file.end.....]')

    def big_picture_string(self, frame):
        big_pic_list = []
        path = os.path.join(self.G_WORK_RENDER_TASK_OUTPUT, frame.zfill(4))
        for root, dirs, files in os.walk(path):
            for name in files:
                work_big_pic = os.path.join(root, name)
                self.G_DEBUG_LOG.info("[big_picture_string] {}".format(work_big_pic))
                big_pic_list.append(work_big_pic.replace(path + os.sep, '').replace('\\', '/'))
        big_pic_str = '|'.join(big_pic_list)
        return big_pic_str

    def write_deduct_fee_text(self, frame, big_pic_str, small_pic_str):
        """
        参数: 帧, 开始时间, 结束时间,
        \\10.60.100.104\new_render_data\input\o\fee\<munu_task_id>_<munu_job_id>_<frame>_<resubmit>_<timestamp>.json
        :return:
        """
        # 本地 fee 路径
        fee_path = self.G_WORK_RENDER_TASK_MULTIFRAME
        # 存储的 fee 路径
        temp_path = self.G_FEE_PATH
        timestamp = int(time.time())
        name = "{munu_task_id}_{munu_job_id}_{frame}_{resubmit}_{timestamp}.json".format(
            munu_task_id=self.G_MUNU_ID,
            munu_job_id=self.G_JOB_ID,
            frame=frame,
            resubmit=self.G_RECOMMIT_FLAG,  # 重提次数
            timestamp=timestamp,
        )
        full_path = os.path.join(fee_path, name)
        self.G_DEBUG_LOG.info(self.render_record)
        render_record = self.render_record[frame]
        start_time = render_record['start_time']
        end_time = render_record['end_time']
        j = dict(
            platform=self.G_PLATFORM,
            munuTaskId=self.G_MUNU_ID,
            munuJobId=self.G_JOB_ID,
            reCommitFlag=self.G_RECOMMIT_FLAG,
            renderStartTime=str(start_time),
            renderEndTime=str(end_time),
            renderBigPic=big_pic_str,
            renderSmallPic=small_pic_str,
        )
        try:
            # 先存本地, 另外上传到 temp_path 路径
            CLASS_COMMON_UTIL.json_save(full_path, j)
            CLASS_COMMON_UTIL.python_copy(full_path, temp_path, my_log=self.G_DEBUG_LOG)
            
        except Exception as e:
            self.G_DEBUG_LOG.info("[write_deduct_fee_text] error: {}, frame: {}".format(e, frame))
            return False
        # 移动到 multiframe_bak
        CLASS_COMMON_UTIL.python_copy(full_path, self.G_WORK_RENDER_TASK_MULTIFRAME_BAK, mode='move', my_log=self.G_DEBUG_LOG)
        
        return True


    def loop_handle_complete(self, render_list):
        """
        :param list render_list: ['0', '1', '2']
        """
        self.G_DEBUG_LOG.info("render_list: {}".format(render_list))
        count = 0
        frame_count = len(render_list)
        while True:
            self.G_DEBUG_LOG.info("multiframe_complete_list: {}".format(self.multiframe_complete_list))
            self.G_DEBUG_LOG.info("cg_return_code: {}".format(self.cg_return_code))
        
            if len(self.multiframe_complete_list) == 0:
                if self.cg_return_code != 'custom' and self.cg_return_code is not None:
                    break
                time.sleep(5)
                continue
            # 拿到当前帧
            frame = self.multiframe_complete_list[0]
            count += 1
            # 发请求
            success = self.rendering_copy_notify('0')
            if success is False:
                self.G_DEBUG_LOG.info("[loop] send 0 fail")
            # 转缩略图
            big_pic_str = self.big_picture_string(frame)
            small_pic_str = self.convert_small(os.path.join(self.G_WORK_RENDER_TASK_OUTPUT, frame.zfill(4)),
                                             self.G_WORK_RENDER_TASK_SMALL)
            # 拷贝
            self.G_DEBUG_LOG.info("copy, result_action1")
            self.handle_file(frame)
            # 写扣费文本
            success = self.write_deduct_fee_text(frame, big_pic_str, small_pic_str)
            self.G_DEBUG_LOG.info("write_deduct_fee_text")
            if success is False:
                self.G_DEBUG_LOG.info("[loop] write_deduct_fee_text fail")
                
            # 发请求
            success = self.rendering_copy_notify('1')
            if success is False:
                self.G_DEBUG_LOG.info("[loop] send 1 fail")
                pass
            # 当前帧出队
            # frame = self.multiframe_complete_list.pop(0)
            # 渲染完一帧之后记录到文件
            self.multiframe_complete_list.pop(0)
            self.G_DEBUG_LOG.info("write render info json, frame: {}".format(frame))
            self.save_render_info(frame)
            self.delete_frame_folder(frame)
            self.G_DEBUG_LOG.info(self.render_record)
            # 移除帧数量 == 这台机需要渲染的帧数量
            self.G_DEBUG_LOG.info("******** compare==={}==={}===={}".format(frame_count, len(render_list), self.multiframe_complete_list))
            if count == frame_count:
                self.copy_log()  # copy render log to output(linux only)
                break
        if count != frame_count:
            self.G_DEBUG_LOG.info("渲染过程异常!!!count={}\nframe_count={}".format(count, frame_count))

    def delete_frame_folder(self, frame):
        f = frame.zfill(4)
        full_path = os.path.join(self.G_WORK_RENDER_TASK_OUTPUT, f)
        try:
            shutil.rmtree(full_path, ignore_errors=True)
        except Exception as e:
            self.G_DEBUG_LOG.info("delete frame folder error: {}".format(e))

    def remain_frames(self):
        """
        如果是继续渲并且存在一个json文件(有且只有一个):
            计算未完成的有哪些
            如果已经全部渲染完成:
                使用入口脚本的 frames
            否则:
                得到应该从第几帧渲起
                重组需要渲染的帧
        不存在:
            使用入口脚本的 frames
        :return: frames
        """
        json_path = os.path.join(self.G_WORK_RENDER_TASK_MULTIFRAME, self.render_record_json)
        if self.G_RENDER_CONTINUE == "true" and os.path.isfile(json_path):
            j = CLASS_COMMON_UTIL.json_load(json_path)
            completed = j['completed']
            now_frames = CLASS_COMMON_UTIL.need_render_from_frame(self.G_CG_FRAMES)
            unfinished = list(set(now_frames) - set(completed))
            unfinished.sort(key=int)
            self.G_DEBUG_LOG.info("completed={}\nnow_frames={}".format(completed, now_frames))
            self.G_DEBUG_LOG.info("unfinished={}\nself.G_CG_FRAMES={}\nself.G_CG_END_FRAME={}\nself.G_CG_BY_FRAME={}".format(unfinished, self.G_CG_FRAMES, self.G_CG_END_FRAME, self.G_CG_BY_FRAME))
            if len(unfinished) == 0:
                frames = self.G_CG_FRAMES
            else:
                start = unfinished[0]
                frames = "{start}-{end}[{by}]".format(
                    start=start,
                    end=self.G_CG_END_FRAME,
                    by=self.G_CG_BY_FRAME,
                )
                self.G_DEBUG_LOG.info("***重组帧: {}".format(frames))
        else:
            frames = self.G_CG_FRAMES
        return frames

    def to_linux_path(self, path1):
        """
        ip path to linux path.
        :param str path1: ip path, 不能是相对路径
        谨慎使用os.path.normpath, 如空字符串会变成.
        """
        if self.G_RENDER_OS == '0':  # G_RENDER_OS:0 linux ,1 windows
            system_map_dict = collections.OrderedDict()  # 有序字典：保证先替换map_dict的内容，用来正确处理input_project_path和input_cg_file
            
            map_dict = self.G_TASK_JSON_DICT.get('mnt_map', {})
            
            system_map_dict.update(map_dict)
            system_map_dict.update(self.G_LINUX_MAP_DICT)
            system_map_dict.update(self.G_LINUX_MAP_DICT2)
            if isinstance(path1, (bytes, str)):
                path1 = path1.replace('\\', '/')
                for linux_path, ip_path in system_map_dict.items():
                    linux_path = linux_path.replace('\\', '/')
                    ip_path = ip_path.replace('\\', '/')
                    if path1.startswith(ip_path+'/'):#互斥过滤
                        path1 = path1.replace(ip_path, linux_path)
                
        return path1
        
    def copy_log(self):
        """copy renderLog to user output"""
        if self.G_RENDER_OS == '0':  # G_RENDER_OS:0 linux ,1 windows
            user_render_log_dir = os.path.join(os.path.dirname(self.G_OUTPUT_USER_PATH), 'render_log', self.G_SMALL_TASK_ID)
            CLASS_COMMON_UTIL.make_dir(user_render_log_dir)
            CLASS_COMMON_UTIL.python_copy(self.render_log_path, user_render_log_dir, my_log=self.G_DEBUG_LOG)
        
        
    def RB_EXECUTE(self):  # total
        '''
            渲染流程控制函数，子类可以覆盖方法
        '''

        self.format_log(
            '\r\n--------------------------------------------小任务开始--------------------------------------------\r\n')
        if self.g_one_machine_multiframe is True:
            self.RB_SYSTEM_INFO()
            self.RB_PRE_RESET_NODE()
            self.RB_MAP_DRIVE()
            self.RB_CONFIG_BASE()
            self.RB_HAN_FILE()
            self.RB_CONFIG()
            self.RB_PRE_PY()
            self.RB_RESOURCE_MONITOR()
            self.RB_RENDER()  # 一机多帧: (起一个)线程做了: 转缩略图,拷贝文件, 生成扣费文本
            self.RB_POST_PY()
            self.RB_POST_RESET_NODE()
            self.RB_FEE()

        else:
            self.RB_SYSTEM_INFO()
            self.RB_PRE_RESET_NODE()
            self.RB_MAP_DRIVE()
            self.RB_CONFIG_BASE()
            self.RB_HAN_FILE()
            self.RB_CONFIG()
            self.RB_PRE_PY()
            self.RB_RESOURCE_MONITOR()
            self.RB_RENDER()
            self.RB_CONVERT_SMALL_PIC()
            self.RB_POST_PY()
            self.RB_POST_RESET_NODE()
            self.RB_HAN_RESULT()
            self.RB_FEE()
        self.format_log(
            '\r\n--------------------------------------------小任务结束--------------------------------------------\r\n')
        self.G_DEBUG_LOG.info('[BASE.RB_EXECUTE.end.....]')
        sys.exit(0)
