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
# import math
import random
import threading
import urllib.request
import urllib.error
from atexit import register

from CommonUtil import RBCommon as CLASS_COMMON_UTIL
# from CommonUtil import RBKafka as CLASS_KAFKA
from FrameChecker import RBFrameChecker as CLASS_FRAME_CHECKER


class RenderBase(object):

    def __init__(self, **param_dict):
        print('[BASE.init.start.....]')
        # print(param_dict)

        # define global variables
        # G_JOB_NAME,G_JOB_ID,G_CG_FRAMES,G_CG_LAYER_NAME,G_CG_OPTION,G_CG_TILE,G_CG_TILECOUNT
        # G_CG_NAME,G_ACTION,G_USER_ID,G_TASK_ID,G_TASK_JSON,G_USER_ID_PARENT,G_SCRIPT_POOL,G_RENDER_OS,G_SYS_ARGVS,G_NODE_PY  &&  G_SCHEDULER_CLUSTER_ID,G_SCHEDULER_CLUSTER_NODES
        for key in list(param_dict.keys()):
            if key.startswith('G'):
                assign = 'self.{0} = param_dict["{0}"]'.format(key)
                exec (assign)
                # exec('self.'+key+'=param_dict["'+key+'"]')

        argvs = self.G_SYS_ARGVS
        self.G_MUNU_ID = argvs[1]  # munu_task_id
        self.G_JOB_ID = argvs[2]  # munu_job_id
        self.G_JOB_NAME = argvs[3]  # munu_job_name
        self.G_NODE_ID = argvs[4]  # 11338764789520
        self.G_NODE_NAME = argvs[5]  # GD232
        self.G_RECOMMIT_FLAG = argvs[6]  # recommit_flag,default is "0"
        self.G_RENDER_CONTINUE = argvs[7]  # 是否继续渲染, 目前用于一机多帧中, 值: "true"(继续, 原来是渲到第几帧就从第几帧开始)/"false"(重来, 从第一帧开始)

        self.G_ACTION_ID = self.G_ACTION + '_' + self.G_MUNU_ID + '_' + self.G_JOB_ID

        # self.G_CG_PROCESS_FLAG = 0  # use with B:\config\cg_process.json
        self.G_WORK = 'c:/work'
        self.G_LOG_WORK = 'C:/log/render'
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

        if 'G_CG_TILE' not in param_dict or (
                'G_CG_TILE' in param_dict and (self.G_CG_TILE is None or self.G_CG_TILE == '')):
            self.G_CG_TILE = '0'
        if 'G_CG_TILE_COUNT' not in param_dict or (
                'G_CG_TILE_COUNT' in param_dict and (self.G_CG_TILE_COUNT is None or self.G_CG_TILE_COUNT == '')):
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

        # -----------------------------------------kafka-----------------------------------------------
        # self.G_KAFKA_MESSAGE_DICT={}
        # self.G_KAFKA_MESSAGE_DICT['start_time']=str(int(time.time()))
        # self.G_KAFKA_MESSAGE_DICT['end_time']=str(int(time.time()))
        # self.G_KAFKA_MESSAGE_DICT['big_pic']=[]
        # self.G_KAFKA_MESSAGE_DICT['small_pic']=[]
        # self.G_KAFKA_MESSAGE_DICT['distribute_node'] = '1'

        # self.G_KAFKA_HOST='10.60.96.142'
        # self.G_KAFKA_PORT=9092
        # self.G_KAFKA_TOPIC= 'dev-munu-topic'
        # self.G_KAFKA_MESSAGE_BODY_DICT={}
        # self.G_KAFKA_MESSAGE_BODY_DICT['startTime']=str(int(time.time()))
        # self.G_KAFKA_MESSAGE_BODY_DICT['endTime']=str(int(time.time()))
        # self.G_START_TIME=''
        # self.G_SMALL_PIC=''
        # self.G_END_TIME=''

        # -----------------------------------------task.json+system.json-----------------------------------------------
        self.G_DEBUG_LOG.info(self.G_TASK_JSON)
        if not os.path.exists(self.G_TASK_JSON):
            CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG, 'task.json not exists')
        CLASS_COMMON_UTIL.python_copy(os.path.normpath(self.G_TASK_JSON), os.path.normpath(self.G_WORK_RENDER_TASK_CFG))
        self.G_REMOTE_TASK_CFG = os.path.split(self.G_TASK_JSON)[0]
        self.G_TASK_JSON = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK_CFG, 'task.json'))
        self.G_TASK_JSON_DICT = eval(codecs.open(self.G_TASK_JSON, 'r', 'utf-8').read())
        self.G_DEBUG_LOG.info(str(self.G_TASK_JSON_DICT))

        self.G_DEBUG_LOG.info(self.G_SYSTEM_JSON)
        if not os.path.exists(self.G_SYSTEM_JSON):
            CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG, 'system.json not exists')
        CLASS_COMMON_UTIL.python_copy(os.path.normpath(self.G_SYSTEM_JSON), os.path.normpath(self.G_WORK_RENDER_TASK_CFG))
        self.G_REMOTE_TASK_SYS_CFG = os.path.split(self.G_SYSTEM_JSON)[0]
        self.G_SYSTEM_JSON = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK_CFG, 'system.json'))
        self.G_SYSTEM_JSON_DICT = eval(codecs.open(self.G_SYSTEM_JSON, 'r', 'utf-8').read())
        self.G_DEBUG_LOG.info(str(self.G_SYSTEM_JSON_DICT))

        software_config = self.G_TASK_JSON_DICT['software_config']
        self.G_CG_CONFIG_DICT = software_config
        self.G_CG_VERSION = software_config['cg_name'] + ' ' + software_config['cg_version']

        common = self.G_SYSTEM_JSON_DICT['system_info']['common']
        self.G_ZONE = common['zone']
        self.G_PLATFORM = common['platform']
        self.G_AUTO_COMMIT = str(common['auto_commit'])
        self.G_TILES_PATH = os.path.normpath(os.path.join(common['tiles_path'], self.G_TASK_ID))
        self.G_INPUT_CG_FILE = os.path.normpath(common['input_cg_file'])
        self.G_CHANNEL = common['channel']
        self.G_INPUT_PROJECT_PATH = os.path.normpath(common['input_project_path'])
        self.G_CONFIG_PATH = os.path.normpath(os.path.join(common['config_path'], self.G_TASK_ID, 'cfg'))
        self.G_SMALL_PATH = os.path.normpath(os.path.join(common['small_path'], self.G_TASK_ID))
        self.G_INPUT_USER_PATH = os.path.normpath(common['input_user_path'])

        # 账号的类型 1，主账号，2，子账号
        account_type = str(common["account_type"])
        print("account_type={}".format(account_type))
        print("account_type={}".format(account_type))
        if account_type == "2":
            # 父账号id
            parent_id = str(common["parent_id"])
            # 是否共享父账号的资产存储  0，不共用，1，共用
            share_storage = str(common["share_storage"])
            print("parent_id={}".format(parent_id))
            print("share_storage={}".format(share_storage))

            if share_storage == "1":
                # 主子账号重新赋值
                old_user_path = int(self.G_USER_ID) // 500 * 500
                new_user_path = int(parent_id) // 500 * 500
                self.G_INPUT_CG_FILE = self.G_INPUT_CG_FILE.replace(self.G_USER_ID, parent_id).replace(str(old_user_path), str(new_user_path))
                self.G_INPUT_PROJECT_PATH = self.G_INPUT_PROJECT_PATH.replace(self.G_USER_ID, parent_id).replace(str(old_user_path), str(new_user_path))
                self.G_INPUT_USER_PATH = self.G_INPUT_USER_PATH.replace(self.G_USER_ID, parent_id).replace(str(old_user_path), str(new_user_path))
                print("self.G_INPUT_CG_FILE={}".format(self.G_INPUT_CG_FILE))
                print("self.G_INPUT_PROJECT_PATH={}".format(self.G_INPUT_PROJECT_PATH))
                print("self.G_INPUT_USER_PATH={}".format(self.G_INPUT_USER_PATH))

        self.G_PLUGIN_PATH = os.path.normpath(common['plugin_path'])
        self.G_TEMP_PATH = os.path.normpath(os.path.join(common['temp_path'], self.G_TASK_ID))
        self.G_GRAB_PATH = os.path.normpath(os.path.join(common['grab_path'], self.G_TASK_ID))
        user_path = os.path.normpath(common['output_user_path'])
        self.G_OUTPUT_USER_PATH = os.path.join(user_path, '{}_{}'.format(self.G_SMALL_TASK_ID, os.path.splitext(os.path.basename(self.G_INPUT_CG_FILE))[0]))
        self.G_API_PATH = os.path.normpath(common['api_path'])
        self.G_FEE_PATH = os.path.normpath(common['fee_path'])

        ##KAFKA
        # self.G_KAFKA_SERVER=common['kafka_server']
        # self.G_KAFKA_TOPIC=common['kafka_topic']
        ##cpu/gpu
        self.G_RENDER_CORE_TYPE = 'cpu'
        if 'render_core_type' in common:
            self.G_RENDER_CORE_TYPE = common['render_core_type']

        self.G_TIPS_JSON = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK_CFG, 'tips.json'))
        self.G_DRIVERC_7Z = os.path.normpath('d:/7-Zip/7z.exe')

        # -----------------------------------------assert.json-----------------------------------------------
        self.G_ASSET_JSON = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK_CFG, 'asset.json'))
        asset_json = os.path.join(self.G_CONFIG_PATH, 'asset.json')
        if os.path.exists(asset_json):
            CLASS_COMMON_UTIL.python_copy(asset_json, self.G_WORK_RENDER_TASK_CFG)
            self.G_ASSET_JSON_DICT = eval(codecs.open(asset_json, 'r', 'utf-8').read())

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
        elif self.G_PLATFORM == '5':
            platform_alias = 'pic'
        elif self.G_PLATFORM == '8':
            platform_alias = 'www8'
        elif self.G_PLATFORM == '9':
            platform_alias = 'www9'
        elif self.G_PLATFORM == '10':
            platform_alias = 'gpu'

        fee_dir = os.path.normpath(os.path.join(self.G_WORK, 'fee', platform_alias, self.G_MUNU_ID))
        if not os.path.exists(fee_dir):
            os.makedirs(fee_dir)
        fee_filename = r'%s_%s.ini' % (self.G_JOB_ID, self.G_RECOMMIT_FLAG)
        self.G_FEE_FILE = os.path.join(fee_dir,
                                       fee_filename)  # c:/work/fee/<platform>/<munu_task_id>/<munu_job_id>_<resubmit>.ini

        # ----------------------------------------------turn global param to str---------------------------------------------------
        global_param_dict = self.__dict__
        for key, value in list(global_param_dict.items()):
            if isinstance(value, bytes):
                assign = 'self.{0} = CLASS_COMMON_UTIL.bytes_to_str(self.{0})'.format(key)
                exec (assign)
                # exec('self.' + key + ' = CLASS_COMMON_UTIL.bytes_to_str(self.' + key + ')')

        # global_param_dict= self.__dict__
        # for key,value in global_param_dict.items():
        # print type(value)
        # print (key+'='+str(value))

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
        if self.g_one_machine_multiframe is True:
            self.pre_multiframe()

        # --------------------------------------------
        print('[BASE.init.end.....]')

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
                    map_cmd = 'net use "%s" "%s"' % (key, value)
                    # CLASS_COMMON_UTIL.cmd_python3(map_cmd,my_log=self.G_DEBUG_LOG)
                    CLASS_COMMON_UTIL.cmd(map_cmd, my_log=self.G_DEBUG_LOG)
                    if key.lower() == 'b:':
                        b_flag = True
            if not b_flag:
                map_cmd_b = 'net use B: "%s"' % (os.path.normpath(self.G_PLUGIN_PATH))
                CLASS_COMMON_UTIL.cmd(map_cmd_b, my_log=self.G_DEBUG_LOG, try_count=3)

        self.G_DEBUG_LOG.info('[BASE.RB_MAP_DRIVE.end.....]')
        self.format_log('done', 'end')

    def RB_HAN_FILE(self):  # 3  copy max.7z and so on
        '''
            拷贝脚本文件
        '''
        self.format_log('拷贝脚本文件', 'start')
        self.G_DEBUG_LOG.info('[BASE.RB_HAN_FILE.start.....]' + self.G_RENDER_CORE_TYPE)

        CLASS_COMMON_UTIL.python_move(self.G_WORK_RENDER_TASK_OUTPUT, self.G_WORK_RENDER_TASK_OUTPUTBAK)

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

    def RB_CONVERT_SMALL_PIC(self):  # 6
        '''
            转换缩略图
        '''
        if self.G_ACTION not in ['Analyze', 'Pre']:
            self.format_log('转换缩略图', 'start')
            self.G_DEBUG_LOG.info('[BASE.RB_CONVERT_SMALL_PIC.start.....]')

            # kafka--big_pic
            big_pic_list = []
            list_dirs = os.walk(self.G_WORK_RENDER_TASK_OUTPUT)
            for root, dirs, files in list_dirs:
                for name in files:
                    work_big_pic = os.path.join(root, name)
                    big_pic_list.append(work_big_pic.replace(self.G_WORK_RENDER_TASK_OUTPUT + os.sep, '').replace('\\',
                                                                                                                  '/'))  # kafka message must use '/' , No '\'
            # self.G_KAFKA_MESSAGE_DICT['big_pic']=big_pic_list
            big_pic_str = '|'.join(big_pic_list)
            if self.G_ACTION in ['RenderPhoton', 'MergePhoton']:
                self.G_FEE_PARSER.set('render', 'big_pic', '')
            else:
                self.G_FEE_PARSER.set('render', 'big_pic', big_pic_str)

            # convert small pic
            # kafka--small_pic
            if self.G_RENDER_OS != '0':
                self.G_DEBUG_LOG.info(self.G_WORK_RENDER_TASK_SMALL)
                self.G_DEBUG_LOG.info(self.G_SMALL_PATH)
                if not os.path.exists(self.G_WORK_RENDER_TASK_SMALL):
                    os.makedirs(self.G_WORK_RENDER_TASK_SMALL)

                exr_to_jpg = os.path.join(self.G_WORK_RENDER_TASK, 'exr2jpg')
                exr_to_jpg_bak = os.path.join(self.G_WORK_RENDER_TASK, 'exr2jpgbak')
                self.convert_dir(self.G_WORK_RENDER_TASK_OUTPUT, self.G_WORK_RENDER_TASK_SMALL)
                self.convert_dir(exr_to_jpg, self.G_WORK_RENDER_TASK_SMALL)

                move_cmd = 'c:\\fcopy\\FastCopy.exe /cmd=move /speed=full /force_close  /no_confirm_stop /force_start "' + self.G_WORK_RENDER_TASK_SMALL.replace(
                    '/', '\\') + '\*.*" /to="' + self.G_SMALL_PATH.replace('/', '\\') + '"'
                CLASS_COMMON_UTIL.cmd(move_cmd, my_log=self.G_DEBUG_LOG, continue_on_error=True)

                if os.path.exists(exr_to_jpg):
                    exr_to_jpg_bak_move = 'c:\\fcopy\\FastCopy.exe /cmd=move /speed=full /force_close  /no_confirm_stop /force_start "' + exr_to_jpg.replace(
                        '/', '\\') + '\\*.*" /to="' + exr_to_jpg_bak.replace('/', '\\') + '"'
                    CLASS_COMMON_UTIL.cmd(exr_to_jpg_bak_move, my_log=self.G_DEBUG_LOG)

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
            cg_process_path = r'/B/config/cg_process_linux.json'

        if not os.path.exists(cg_process_path):
            self.G_DEBUG_LOG.info('[warn]%s is not exists!!!' % cg_process_path)
        else:
            cg_process_dict = eval(codecs.open(cg_process_path, 'r', 'utf-8').read())

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

                        t = threading.Thread(target=self.monitor_cmd, args=(command, resource_monitor,))
                        t.daemon = True
                        t.start()
        if self.g_one_machine_multiframe is True:
            self.monitor_complete_thread.start()

        self.G_DEBUG_LOG.info('[BASE.RB_RESOURCE_MONITOR end]')

    def monitor_cmd(self, command, resource_monitor):
        self.G_DEBUG_LOG.info(command)
        register(self.monitor_exit, resource_monitor)
        os.system(command)

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
        render_log_path = os.path.join(log_dir, (self.G_ACTION_ID + '_render.log'))
        self.G_RENDER_LOG.setLevel(logging.DEBUG)
        render_log_handler = logging.FileHandler(render_log_path, encoding='utf-8')
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
            CLASS_COMMON_UTIL.python_copy(block_path, base_path)
        self.G_DEBUG_LOG.info('[BASE.copy_black.end.....]')

    def sort_pic_list(self, pic_list):
        """ Returns list.
            功能：将缩略图列表重新排序。
            这将影响平台展示给客户的缩略图顺序，
            默认对列表不做任何修改操作，如需则在各自软件的脚本中重写该方法
            如：max重写该方法实现了将主图缩略图排在列表最前面，方便平台展示给客户（第一张即为主图）
        """
        return pic_list

    def convert_dir(self, dir, work_small_path):
        self.G_DEBUG_LOG.info('[BASE.convert_dir.start.....]')

        if os.path.exists(dir):
            small_width = '425'
            small_height = '260'
            small_pic_list = []

            list_dirs = os.walk(dir)
            for root, dirs, files in list_dirs:
                for name in files:
                    ext = os.path.splitext(name)[1]
                    self.G_DEBUG_LOG.info('name=' + name)
                    if ext in ['.vrmap', '.vrlmap', '.vrimg']:
                        continue
                    work_big_pic = os.path.join(root, name)
                    # big_pic_list.append(work_big_pic.replace(dir+'\\','').replace('\\','/'))
                    small_pic = work_big_pic.replace(dir + '\\', '')
                    small_pic = self.G_ACTION_ID + "_" + small_pic.replace('\\', '[_]').replace('/', '[_]').replace('.',
                                                                                                                    '[-]') + '.jpg'
                    small_pic_list.append(small_pic.replace('\\', '/'))
                    small_tmp_name = self.G_ACTION_ID + '_tmp.jpg'
                    work_small_pic = os.path.join(work_small_path, small_pic)
                    work_small_tmp_pic = os.path.join(work_small_path, small_tmp_name)

                    work_big_pic_tmp = os.path.join(root, 'tmp' + os.path.splitext(work_big_pic)[1])
                    try:
                        os.rename(work_big_pic, work_big_pic_tmp)
                    except Exception as e:
                        self.G_DEBUG_LOG.info('rename failed-----')
                        pass
                    if not os.path.exists(work_big_pic_tmp):
                        work_big_pic_tmp = work_big_pic
                        work_small_tmp_pic = work_small_pic

                    oiio_path = r'c:\oiio\OpenImageIO-1.5.18-bin-vc9-x64\oiiotool.exe'
                    nconvert_path = r'c:/ImageMagick/nconvert.exe'
                    # convert_cmd = 'c:/ImageMagick/nconvert.exe  -out jpeg -ratio -resize ' + small_size + ' 0 -overwrite -o "' + work_small_tmp_pic + '" "' + work_big_pic_tmp + '"'
                    convert_cmd = '{exe_path} -out jpeg -ratio -resize {w} {h} -overwrite -o "{output_file}" "{converted_file}"'.format(
                        exe_path=nconvert_path,
                        w=small_width,
                        h=small_height,
                        output_file=work_small_tmp_pic,
                        converted_file=work_big_pic_tmp
                    )
                    if ext == '.exr' and os.path.exists(oiio_path):
                        self.G_DEBUG_LOG.info('exr parse----' + name)

                        # convert_cmd = oiio_path + ' "' + work_big_pic_tmp + '" -resize ' + self.get_convert_r(work_big_pic_tmp, oiio_path) + ' -o "' + work_small_tmp_pic + '"'
                        convert_cmd = '{exe_path} "{converted_file}" -resize {width_x_height} -o "{output_file}"'.format(
                            exe_path=oiio_path,
                            output_file=work_small_tmp_pic,
                            converted_file=work_big_pic_tmp,
                            width_x_height=self.get_convert_r(work_big_pic_tmp, oiio_path, small_width, small_height),
                        )
                    # print work_big_pic
                    try:
                        # CLASS_COMMON_UTIL.cmd(convert_cmd,my_log=self.G_DEBUG_LOG,continue_on_error=True)
                        # CLASS_COMMON_UTIL.cmd_python3(convert_cmd,my_log=self.G_DEBUG_LOG)
                        CLASS_COMMON_UTIL.cmd(convert_cmd, my_log=self.G_DEBUG_LOG, continue_on_error=True)
                    except Exception as e:
                        self.G_DEBUG_LOG.info('parse smallPic failed-----')
                        pass
                    if not work_big_pic_tmp == work_big_pic:
                        os.rename(work_big_pic_tmp, work_big_pic)
                        if os.path.exists(work_small_tmp_pic):
                            try:
                                os.rename(work_small_tmp_pic, work_small_pic)
                            except FileExistsError as e:
                                pass
                    self.G_DEBUG_LOG.info(
                        'work_small_tmp_pic---' + work_small_tmp_pic + '---work_small_pic---' + work_small_pic + '---work_big_pic_tmp---' + work_big_pic_tmp + '---work_big_pic---' + work_big_pic)
            # self.G_KAFKA_MESSAGE_DICT['small_pic']=small_pic_list
            # self.G_KAFKA_MESSAGE_DICT['big_pic']=big_pic_list

            small_pic_list = self.sort_pic_list(small_pic_list)

            small_pic_str = '|'.join(small_pic_list)
            self.G_FEE_PARSER.set('render', 'small_pic', small_pic_str)
            return small_pic_str
        self.G_DEBUG_LOG.info('[BASE.convert_dir.end.....]')
        return ''

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
        output_list = os.listdir(node_output)
        if not output_list:
            CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG, 'output is empty!')
        for root, dirs, files in os.walk(node_output):
            for name in files:
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

        self.G_DEBUG_LOG.info('')

    def result_action(self):
        '''
            上传渲染结果和日志
        '''
        self.G_DEBUG_LOG.info('[BASE.result_action.start.....]')
        # RB_small
        if not os.path.exists(self.G_SMALL_PATH):
            os.makedirs(self.G_SMALL_PATH)
        if self.G_RENDER_OS == '0':
            output_path = "/output"
            outputbak_path = "/outputbak"
            sp_path = 'render_data'
            output_folder = self.G_OUTPUT_USER_PATH[
                            self.G_OUTPUT_USER_PATH.rfind(sp_path) + len(sp_path):len(self.G_OUTPUT_USER_PATH)]
            output_mnt_path = self.G_OUTPUT_USER_PATH.replace(output_folder, '').replace('\\', '/')
            output_mnt = 'mount -t cifs -o username=administrator,password=Rayvision@2016,codepage=936,iocharset=gb2312 ' + output_mnt_path + ' ' + output_path

            if not os.path.exists(output_path):
                os.makedirs(output_path)

            self.rendering_copy_notify()

            CLASS_COMMON_UTIL.cmd(output_mnt, my_shell=True)

            output_path = output_path + output_folder.replace("\\", "/")
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            CLASS_COMMON_UTIL.python_copy(self.G_WORK_RENDER_TASK_OUTPUT, output_path)
            CLASS_COMMON_UTIL.python_copy(self.G_WORK_RENDER_TASK_OUTPUT, self.G_WORK_RENDER_TASK_OUTPUTBAK)
        else:
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
        CLASS_COMMON_UTIL.python_copy(node_task_json, self.G_CONFIG_PATH)
        CLASS_COMMON_UTIL.python_copy(node_asset_json, self.G_CONFIG_PATH)
        CLASS_COMMON_UTIL.python_copy(node_tips_json, self.G_CONFIG_PATH)

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
                cmd = r'c:\fcopy\FastCopy.exe /cmd=force_copy /speed=full /force_close /no_confirm_stop /force_start "{}" /to="{}"'.format(
                    remote_render_record_json,
                    self.G_WORK_RENDER_TASK_MULTIFRAME,
                )
                CLASS_COMMON_UTIL.cmd(cmd, my_log=self.G_DEBUG_LOG, try_count=3, continue_on_error=True)
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
        path = self.render_record_json
        common_util = CLASS_COMMON_UTIL
        if os.path.isfile(path):
            obj = common_util.json_load(path)
            frame_list = obj['completed']
            frame_list.append(frame)
            common_util.json_save(path, obj)
        else:
            frame_list = [frame]
            obj = {
                "completed": frame_list,  # ['1', '3']
            }
            common_util.json_save(path, obj)
        # 上传
        cmd = r'c:\fcopy\FastCopy.exe /cmd=force_copy /speed=full /force_close /no_confirm_stop /force_start "{}" /to="{}"'.format(
            path,
            self.G_REMOTE_TASK_CFG,
        )
        CLASS_COMMON_UTIL.cmd(cmd, my_log=self.G_DEBUG_LOG)
        # 复制到 multiframe_bak
        cmd = r'c:\fcopy\FastCopy.exe /cmd=force_copy /speed=full /force_close /no_confirm_stop /force_start "{}" /to="{}"'.format(
            path,
            self.G_WORK_RENDER_TASK_MULTIFRAME_BAK,
        )
        CLASS_COMMON_UTIL.cmd(cmd, my_log=self.G_DEBUG_LOG, continue_on_error=True)

    def handle_file(self, frame):
        '''
            上传渲染结果和日志
        '''
        self.G_DEBUG_LOG.info('[Base.handle_file.start.....]')
        # RB_small
        if not os.path.exists(self.G_SMALL_PATH):
            os.makedirs(self.G_SMALL_PATH)
        if self.G_RENDER_OS == '0':
            output_path = "/output"
            outputbak_path = "/outputbak"
            sp_path = 'render_data'
            output_folder = self.G_OUTPUT_USER_PATH[
                            self.G_OUTPUT_USER_PATH.rfind(sp_path) + len(sp_path):len(self.G_OUTPUT_USER_PATH)]
            output_mnt_path = self.G_OUTPUT_USER_PATH.replace(output_folder, '').replace('\\', '/')
            output_mnt = 'mount -t cifs -o username=administrator,password=Rayvision@2016,codepage=936,iocharset=gb2312 ' + output_mnt_path + ' ' + output_path

            if not os.path.exists(output_path):
                os.makedirs(output_path)

            CLASS_COMMON_UTIL.cmd(output_mnt, my_shell=True)

            output_path = output_path + output_folder.replace("\\", "/")
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            CLASS_COMMON_UTIL.python_copy(self.G_WORK_RENDER_TASK_OUTPUT, output_path)
            CLASS_COMMON_UTIL.python_copy(self.G_WORK_RENDER_TASK_OUTPUT, self.G_WORK_RENDER_TASK_OUTPUTBAK)
        else:
            # output=self.G_OUTPUT_USER_PATH.encode(sys.getfilesystemencoding())
            output = self.G_OUTPUT_USER_PATH
            frame = frame.zfill(4)
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
        commom_util = CLASS_COMMON_UTIL
        log = self.G_DEBUG_LOG.info
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
        log(self.render_record)
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
            commom_util.json_save(full_path, j)
            cmd = r'c:\fcopy\FastCopy.exe /speed=full /force_close /no_confirm_stop /force_start "{}" /to="{}"'.format(
                full_path,
                temp_path,
            )
            CLASS_COMMON_UTIL.cmd(cmd, my_log=self.G_DEBUG_LOG)
        except Exception as e:
            log("[write_deduct_fee_text] error: {}, frame: {}".format(e, frame))
            return False
        # 移动到 multiframe_bak
        cmd = r'c:\fcopy\FastCopy.exe /cmd=move /speed=full /force_close /no_confirm_stop /force_start "{}" /to="{}"'.format(
            full_path,
            self.G_WORK_RENDER_TASK_MULTIFRAME_BAK,
        )
        CLASS_COMMON_UTIL.cmd(cmd, my_log=self.G_DEBUG_LOG, try_count=3, continue_on_error=True)

        return True

    def copy_small_pic(self):
        self.G_DEBUG_LOG.info("copy small picture: {}->{}".format(self.G_WORK_RENDER_TASK_SMALL, self.G_SMALL_PATH))
        cmd = r'c:\fcopy\FastCopy.exe /cmd=force_copy /speed=full /force_close /no_confirm_stop /force_start "{}" /to="{}"'.format(
            self.G_WORK_RENDER_TASK_SMALL,
            self.G_SMALL_PATH,
        )
        CLASS_COMMON_UTIL.cmd(cmd, my_log=self.G_DEBUG_LOG, continue_on_error=True)

    def loop_handle_complete(self, render_list):
        common_util = CLASS_COMMON_UTIL
        log = self.G_DEBUG_LOG.info
        l = self.multiframe_complete_list
        log("render_list: {}".format(render_list))
        count = 0
        frame_count = len(render_list)
        while True:
            if len(l) == 0:
                if self.cg_return_code != 'custom' and self.cg_return_code is not None:
                    break
                log("sleep 5, list: {}".format(render_list))
                time.sleep(5)
                continue
            # 拿到当前帧
            frame = l[0]
            count += 1
            # 发请求
            success = self.rendering_copy_notify('0')
            if success is False:
                log("[loop] send 0 fail")
                pass
            # 转缩略图
            big_pic_str = self.big_picture_string(frame)
            small_pic_str = self.convert_dir(os.path.join(self.G_WORK_RENDER_TASK_OUTPUT, frame.zfill(4)),
                                             self.G_WORK_RENDER_TASK_SMALL)
            # 拷贝
            log("copy, result_action1")
            self.handle_file(frame)
            # 拷贝缩略图
            self.copy_small_pic()
            # 写扣费文本
            success = self.write_deduct_fee_text(frame, big_pic_str, small_pic_str)
            log("write_deduct_fee_text")
            if success is False:
                log("[loop] write_deduct_fee_text fail")
                pass
            # 发请求
            success = self.rendering_copy_notify('1')
            if success is False:
                log("[loop] send 1 fail")
                pass
            # 当前帧出队
            # frame = l.pop(0)
            # 渲染完一帧之后记录到文件
            l.pop(0)
            log("write render info json, frame: {}".format(frame))
            self.save_render_info(frame)
            self.delete_frame_folder(frame)
            log(self.render_record)
            # 移除帧数量 == 这台机需要渲染的帧数量
            log("******** compare==={}==={}===={}".format(frame_count, len(render_list), l))
            if count == frame_count:
                break
        if count != frame_count:
            log("渲染过程异常!!!count={}\nframe_count={}".format(count, frame_count))

    def delete_frame_folder(self, frame):
        f = frame.zfill(4)
        full_path = os.path.join(self.G_WORK_RENDER_TASK_OUTPUT, f)
        try:
            shutil.rmtree(full_path, ignore_errors=True)
        except WindowsError as e:
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
        log = self.G_DEBUG_LOG.info
        commom_util = CLASS_COMMON_UTIL
        f = self.render_record_json
        json_path = os.path.join(self.G_WORK_RENDER_TASK_MULTIFRAME, f)
        if self.G_RENDER_CONTINUE == "true" and os.path.isfile(json_path):
            j = commom_util.json_load(json_path)
            completed = j['completed']
            now_frames = commom_util.need_render_from_frame(self.G_CG_FRAMES)
            unfinished = list(set(now_frames) - set(completed))
            unfinished.sort(key=int)
            log("completed={}\nnow_frames={}".format(completed, now_frames))
            log("unfinished={}\nself.G_CG_FRAMES={}\nself.G_CG_END_FRAME={}\nself.G_CG_BY_FRAME={}".format(unfinished, self.G_CG_FRAMES, self.G_CG_END_FRAME, self.G_CG_BY_FRAME))
            if len(unfinished) == 0:
                frames = self.G_CG_FRAMES
            else:
                start = unfinished[0]
                frames = "{start}-{end}[{by}]".format(
                    start=start,
                    end=self.G_CG_END_FRAME,
                    by=self.G_CG_BY_FRAME,
                )
                log("***重组帧: {}".format(frames))
        else:
            frames = self.G_CG_FRAMES
        return frames

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
