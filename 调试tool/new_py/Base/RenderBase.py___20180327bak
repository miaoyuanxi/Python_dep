#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
import subprocess
import string
import time,datetime
import shutil
import ctypes
import json
import re
import configparser
import codecs
#import math
import threading
import urllib.request
from atexit import register


from CommonUtil import RBCommon as CLASS_COMMON_UTIL
# from CommonUtil import RBKafka as CLASS_KAFKA
from FrameChecker import RBFrameChecker as CLASS_FRAME_CHECKER


class RenderBase():

    def __init__(self,**param_dict):
        print('[BASE.init.start.....]')
        # print(param_dict)        
        
        # define global variables
        # G_JOB_NAME,G_JOB_ID,G_CG_FRAMES,G_CG_LAYER_NAME,G_CG_OPTION,G_CG_TILE,G_CG_TILECOUNT
        # G_CG_NAME,G_ACTION,G_USER_ID,G_TASK_ID,G_TASK_JSON,G_USER_ID_PARENT,G_SCRIPT_POOL,G_RENDER_OS,G_SYS_ARGVS,G_NODE_PY  &&  G_SCHEDULER_CLUSTER_ID,G_SCHEDULER_CLUSTER_NODES
        for key in list(param_dict.keys()):
            if key.startswith('G'):
                exec('self.'+key+'=param_dict["'+key+'"]')
        
        self.G_MUNU_ID=self.G_SYS_ARGVS[1]  #munu_task_id
        self.G_JOB_ID=self.G_SYS_ARGVS[2]  #munu_job_id
        self.G_JOB_NAME=self.G_SYS_ARGVS[3]  #munu_job_name
        self.G_NODE_ID=self.G_SYS_ARGVS[4]  #11338764789520
        self.G_NODE_NAME=self.G_SYS_ARGVS[5]  #GD232
        self.G_RECOMMIT_FLAG=self.G_SYS_ARGVS[6]  #recommit_flag,default is "0"
            
        self.G_ACTION_ID=self.G_ACTION+'_'+self.G_MUNU_ID+'_'+self.G_JOB_ID
        
        # self.G_CG_PROCESS_FLAG = 0  # use with B:\config\cg_process.json
        
        self.G_WORK='c:/work'
        self.G_LOG_WORK='C:/log/render'
        if self.G_RENDER_OS=='0':  #G_RENDER_OS:0 linux ,1 windows
            self.G_LOG_WORK='/tmp/nzs-data/log/render'
            self.G_WORK='/tmp/nzs-data/work'

        #-----------------------------------------log-----------------------------------------------
        self.G_DEBUG_LOG=logging.getLogger('debug_log')
        self.G_RENDER_LOG=logging.getLogger('render_log')
        self.init_log()
        
        #-----------------------------------------analyse frame-----------------------------------------------
        if 'G_CG_FRAMES' in param_dict:
            self.G_CG_START_FRAME = None
            self.G_CG_END_FRAME = None
            self.G_CG_BY_FRAME = None
            patt = '(-?\d+)(?:-?(-?\d+)(?:\[(-?\d+)\])?)?'
            m = re.match(patt,self.G_CG_FRAMES)
            if m != None:
                self.G_CG_START_FRAME = m.group(1)
                self.G_CG_END_FRAME = m.group(2)
                self.G_CG_BY_FRAME = m.group(3)
                if self.G_CG_END_FRAME == None:
                    self.G_CG_END_FRAME = self.G_CG_START_FRAME
                if self.G_CG_BY_FRAME == None:
                    self.G_CG_BY_FRAME = '1'
            else:
                print('frames is not match')
        
        if 'G_CG_TILE' not in param_dict or ('G_CG_TILE' in param_dict and (self.G_CG_TILE == None or self.G_CG_TILE == '')):
            self.G_CG_TILE='0'
        if 'G_CG_TILE_COUNT' not in param_dict or ('G_CG_TILE_COUNT' in param_dict and (self.G_CG_TILE_COUNT == None or self.G_CG_TILE_COUNT == '')):
            self.G_CG_TILE_COUNT='1'
            
               
        
        #-----------------------------------------work directory-----------------------------------------------
        self.G_WORK_RENDER=os.path.normpath(os.path.join(self.G_WORK,'render'))
        self.G_WORK_RENDER_TASK=os.path.normpath(os.path.join(self.G_WORK_RENDER,self.G_TASK_ID))
        self.G_WORK_RENDER_TASK_CFG=os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK,'cfg'))
        self.G_WORK_RENDER_TASK_OUTPUT=os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK,'output'))
        self.G_WORK_RENDER_TASK_OUTPUTBAK=os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK,'outputbak'))
        self.G_WORK_RENDER_TASK_SMALL=os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK,'small'))
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
        #self.G_START_TIME=''
        #self.G_SMALL_PIC=''
        #self.G_END_TIME=''
        
        
        #-----------------------------------------task.json-----------------------------------------------
        self.G_DEBUG_LOG.info(self.G_TASK_JSON)
        if not os.path.exists(self.G_TASK_JSON):
            CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG,'task.json not exists')
        CLASS_COMMON_UTIL.python_copy(os.path.normpath(self.G_TASK_JSON),os.path.normpath(self.G_WORK_RENDER_TASK_CFG))    
        self.G_TASK_JSON=os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK_CFG,'task.json'))
        self.G_TASK_JSON_DICT=eval(codecs.open(self.G_TASK_JSON, 'r', 'utf-8').read())
        self.G_DEBUG_LOG.info(str(self.G_TASK_JSON_DICT))
        
        
        self.G_CG_CONFIG_DICT=self.G_TASK_JSON_DICT['software_config']
        self.G_CG_VERSION=self.G_TASK_JSON_DICT['software_config']['cg_name']+' '+self.G_TASK_JSON_DICT['software_config']['cg_version']
        self.G_ZONE=self.G_TASK_JSON_DICT['system_info']['common']['zone']
        self.G_PLATFORM=self.G_TASK_JSON_DICT['system_info']['common']['platform']
        self.G_AUTO_COMMIT=str(self.G_TASK_JSON_DICT['system_info']['common']['auto_commit'])
        self.G_TILES_PATH=os.path.normpath(os.path.join(self.G_TASK_JSON_DICT['system_info']['common']['tiles_path'], self.G_TASK_ID))
        self.G_INPUT_CG_FILE=os.path.normpath(self.G_TASK_JSON_DICT['system_info']['common']['input_cg_file'])
        self.G_CHANNEL=self.G_TASK_JSON_DICT['system_info']['common']['channel']
        self.G_INPUT_PROJECT_PATH=os.path.normpath(self.G_TASK_JSON_DICT['system_info']['common']['input_project_path'])
        self.G_CONFIG_PATH=os.path.normpath(os.path.join(self.G_TASK_JSON_DICT['system_info']['common']['config_path'], self.G_TASK_ID, 'cfg'))
        self.G_SMALL_PATH=os.path.normpath(os.path.join(self.G_TASK_JSON_DICT['system_info']['common']['small_path'], self.G_TASK_ID))
        self.G_INPUT_USER_PATH=os.path.normpath(self.G_TASK_JSON_DICT['system_info']['common']['input_user_path'])
        self.G_PLUGIN_PATH=os.path.normpath(self.G_TASK_JSON_DICT['system_info']['common']['plugin_path'])
        self.G_TEMP_PATH=os.path.normpath(os.path.join(self.G_TASK_JSON_DICT['system_info']['common']['temp_path'], self.G_TASK_ID))
        self.G_GRAB_PATH=os.path.normpath(os.path.join(self.G_TASK_JSON_DICT['system_info']['common']['grab_path'], self.G_TASK_ID))
        self.G_OUTPUT_USER_PATH=os.path.normpath(self.G_TASK_JSON_DICT['system_info']['common']['output_user_path'])
        self.G_OUTPUT_USER_PATH=os.path.join(self.G_OUTPUT_USER_PATH, '%s_%s' % (self.G_SMALL_TASK_ID, os.path.splitext(os.path.basename(self.G_INPUT_CG_FILE))[0]))
        # self.G_OUTPUT_USER_PATH = os.path.join(self.G_OUTPUT_USER_PATH,self.G_SMALL_TASK_ID+self.G_OUTPUT_USER_PATH.split(os.sep)[-1][len(self.G_TASK_ID):])
        self.G_API_PATH=os.path.normpath(self.G_TASK_JSON_DICT['system_info']['common']['api_path'])
        self.G_FEE_PATH=os.path.normpath(self.G_TASK_JSON_DICT['system_info']['common']['fee_path'])
        ##KAFKA
        # self.G_KAFKA_SERVER=self.G_TASK_JSON_DICT['system_info']['common']['kafka_server']
        # self.G_KAFKA_TOPIC=self.G_TASK_JSON_DICT['system_info']['common']['kafka_topic']
        ##cpu/gpu
        self.G_RENDER_CORE_TYPE = 'cpu'
        if 'render_core_type' in self.G_TASK_JSON_DICT['system_info']['common']:
            self.G_RENDER_CORE_TYPE=self.G_TASK_JSON_DICT['system_info']['common']['render_core_type']
        
        self.G_TIPS_JSON=os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK_CFG,'tips.json'))
        self.G_DRIVERC_7Z=os.path.normpath('d:/7-Zip/7z.exe')
        
        
        #-----------------------------------------assert.json-----------------------------------------------
        self.G_ASSET_JSON=os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK_CFG,'asset.json'))
        asset_json=os.path.join(self.G_CONFIG_PATH,'asset.json')
        if os.path.exists(asset_json):
            CLASS_COMMON_UTIL.python_copy(asset_json,self.G_WORK_RENDER_TASK_CFG)    
            self.G_ASSET_JSON_DICT=eval(codecs.open(asset_json, 'r', 'utf-8').read())
            
        
        # -----------------------------------------fee-----------------------------------------------
        self.G_FEE_PARSER = configparser.ConfigParser()
        if not self.G_FEE_PARSER.has_section('render'):
            self.G_FEE_PARSER.add_section('render')
            
        fee_dir = os.path.normpath(os.path.join(self.G_WORK,'fee',self.G_PLATFORM,self.G_MUNU_ID))
        if not os.path.exists(fee_dir):
            os.makedirs(fee_dir)
        fee_filename = r'%s_%s.ini' % (self.G_JOB_ID,self.G_RECOMMIT_FLAG)
        self.G_FEE_FILE = os.path.join(fee_dir,fee_filename)    #c:/work/fee/<platform>/<munu_task_id>/<munu_job_id>_<resubmit>.ini
            
            
            
        #----------------------------------------------turn global param to str---------------------------------------------------
        global_param_dict= self.__dict__
        for key,value in list(global_param_dict.items()):
            if isinstance(value,bytes):
                exec('self.' + key + ' = CLASS_COMMON_UTIL.bytes_to_str(self.' + key + ')')
        
        # global_param_dict= self.__dict__
        # for key,value in global_param_dict.items():
            # print type(value)
            # print (key+'='+str(value))
        
        print('[BASE.init.end.....]')
        
    def RB_SYSTEM_INFO(self):
        self.G_DEBUG_LOG.info("-"*20 + "  SysTemInfo  " + "-"*20)
        self.G_DEBUG_LOG.info("\r\nComputer Platform: %s" %CLASS_COMMON_UTIL.get_system_version())
        self.G_DEBUG_LOG.info("Computer HostName: %s" %CLASS_COMMON_UTIL.get_computer_hostname())
        
        self.G_DEBUG_LOG.info("Computer System: %s" %CLASS_COMMON_UTIL.get_system())
        self.G_DEBUG_LOG.info("Computer Ip: %s" %CLASS_COMMON_UTIL.get_computer_ip())
        self.G_DEBUG_LOG.info("Computer MAC: %s\r\n" %CLASS_COMMON_UTIL.get_computer_mac())
        
        if self.G_RENDER_OS != '0':
            lp_buffer = ctypes.create_string_buffer(78)
            ctypes.windll.kernel32.GetLogicalDriveStringsA(ctypes.sizeof(lp_buffer), lp_buffer)
            vol = lp_buffer.raw.split(b'\x00')
            for i in vol:
                if i:                             
                    self.G_DEBUG_LOG.info('Disk='+str(i))
                    
    
    '''
        pre custom
    '''
    def RB_PRE_PY(self):#1
    
    
        self.format_log('执行自定义PY脚本','start')
        self.G_DEBUG_LOG.info('[BASE.RB_PRE_PY.start.....]')
        self.G_DEBUG_LOG.info('如果以下自定义PY脚本存在，会执行此脚本')
        pre_py=os.path.join(self.G_NODE_PY,'CG',self.G_CG_NAME,'function','pre.py')
        self.G_DEBUG_LOG.info(pre_py)
        if os.path.exists(pre_py):
            import pre as PRE_PY_MODEL
            self.PRE_DICT=PRE_PY_MODEL.main()
        self.G_DEBUG_LOG.info('[BASE.RB_PRE_PY.end.....]')
        self.format_log('done','end')
    
    def RB_PRE_RESET_NODE(self):
        pass
    '''
        映射盘符
    '''
    def RB_MAP_DRIVE(self):#2
        self.format_log('映射盘符','start')
        self.G_DEBUG_LOG.info('[BASE.RB_MAP_DRIVE.start.....]')
        
        if self.G_RENDER_OS != '0':
            #delete all mappings
            CLASS_COMMON_UTIL.del_net_use()
            CLASS_COMMON_UTIL.del_subst()
            
            #net use
            b_flag = False
            if self.G_CG_NAME != 'Max' and 'mnt_map' in self.G_TASK_JSON_DICT['system_info']:
                map_dict = self.G_TASK_JSON_DICT['system_info']['mnt_map']
                for key,value in list(map_dict.items()):
                    value = os.path.normpath(value)
                    map_cmd = 'net use "%s" "%s"' % (key,value)
                    # CLASS_COMMON_UTIL.cmd_python3(map_cmd,my_log=self.G_DEBUG_LOG)
                    CLASS_COMMON_UTIL.cmd(map_cmd,my_log=self.G_DEBUG_LOG)
                    if key.lower() == 'b:':
                        b_flag = True
            if not b_flag:
                map_cmd_b = 'net use B: "%s"' % (os.path.normpath(self.G_PLUGIN_PATH))
                CLASS_COMMON_UTIL.cmd(map_cmd_b,my_log=self.G_DEBUG_LOG,try_count=3)
                
        self.G_DEBUG_LOG.info('[BASE.RB_MAP_DRIVE.end.....]')
        self.format_log('done','end')
        
    '''
        拷贝脚本文件
    '''
    def RB_HAN_FILE(self):#3  copy max.7z and so on
        self.format_log('拷贝脚本文件','start')
        self.G_DEBUG_LOG.info('[BASE.RB_HAN_FILE.start.....]'+self.G_RENDER_CORE_TYPE)
        
        CLASS_COMMON_UTIL.python_move(self.G_WORK_RENDER_TASK_OUTPUT,self.G_WORK_RENDER_TASK_OUTPUTBAK)
      
        self.G_DEBUG_LOG.info('[BASE.RB_HAN_FILE.end.....]')
        self.format_log('done','end')
        
    '''
        渲染基本配置
    '''
    def RB_CONFIG_BASE(self):#4
        self.format_log('渲染基本配置','start')
        self.G_DEBUG_LOG.info('[BASE.RB_CONFIG_BASE.start.....]')
        
        if self.G_RENDER_OS != '0':
            #DogUtil.killMaxVray(self.G_DEBUG_LOG)  #kill 3dsmax.exe,3dsmaxcmd.exe,vrayspawner*.exe
            self.copy_7z()  #copy 7-Zip
        self.copy_black()  #copy black.xml
        
        self.G_DEBUG_LOG.info('[BASE.RB_CONFIG_BASE.end.....]') 
        self.format_log('done','end')
        
    '''
        渲染配置
    '''
    def RB_CONFIG(self):#4
        self.format_log('渲染配置','start')
        self.G_DEBUG_LOG.info('[BASE.RB_CONFIG.start.....]')
        self.G_DEBUG_LOG.info('[BASE.RB_CONFIG.end.....]') 
        self.format_log('done','end')
        
    '''
        渲染
    '''
    def RB_RENDER(self):#5
        self.format_log('渲染','start')
        self.G_DEBUG_LOG.info('[BASE.RB_RENDER.start.....]')
        self.G_DEBUG_LOG.info('[BASE.RB_RENDER.end.....]')
        self.format_log('done','end')
        
    '''
        转换缩略图
    '''
    def RB_CONVERT_SMALL_PIC(self):#6
        if self.G_ACTION not in ['Analyze','Pre']:
            self.format_log('转换缩略图','start')
            self.G_DEBUG_LOG.info('[BASE.RB_CONVERT_SMALL_PIC.start.....]')
            
            #kafka--big_pic
            big_pic_list=[]
            list_dirs = os.walk(self.G_WORK_RENDER_TASK_OUTPUT)
            for root, dirs, files in list_dirs:
                for name in files:
                    work_big_pic = os.path.join(root,name)
                    big_pic_list.append(work_big_pic.replace(self.G_WORK_RENDER_TASK_OUTPUT+os.sep,'').replace('\\','/'))  #kafka message must use '/' , No '\'
            # self.G_KAFKA_MESSAGE_DICT['big_pic']=big_pic_list
            big_pic_str = '|'.join(big_pic_list)
            if self.G_ACTION in ['RenderPhoton','MergePhoton']:
                self.G_FEE_PARSER.set('render','big_pic','')
            else:
                self.G_FEE_PARSER.set('render','big_pic',big_pic_str)
            
            #convert small pic
            #kafka--small_pic
            if self.G_RENDER_OS != '0':
                self.G_DEBUG_LOG.info(self.G_WORK_RENDER_TASK_SMALL)
                self.G_DEBUG_LOG.info(self.G_SMALL_PATH)
                if not os.path.exists(self.G_WORK_RENDER_TASK_SMALL):
                    os.makedirs(self.G_WORK_RENDER_TASK_SMALL)
                    
                exr_to_jpg=os.path.join(self.G_WORK_RENDER_TASK,'exr2jpg')
                exr_to_jpg_bak=os.path.join(self.G_WORK_RENDER_TASK,'exr2jpgbak')
                self.convert_dir(self.G_WORK_RENDER_TASK_OUTPUT,self.G_WORK_RENDER_TASK_SMALL)
                self.convert_dir(exr_to_jpg,self.G_WORK_RENDER_TASK_SMALL)
                
                move_cmd='c:\\fcopy\\FastCopy.exe /cmd=move /speed=full /force_close  /no_confirm_stop /force_start "' +self.G_WORK_RENDER_TASK_SMALL.replace('/','\\')+'\*.*" /to="'+self.G_SMALL_PATH.replace('/','\\')+'"'
                CLASS_COMMON_UTIL.cmd(move_cmd,my_log=self.G_DEBUG_LOG,continue_on_error=True)

                if  os.path.exists(exr_to_jpg):
                    exr_to_jpg_bak_move='c:\\fcopy\\FastCopy.exe /cmd=move /speed=full /force_close  /no_confirm_stop /force_start "' +exr_to_jpg.replace('/','\\')+'\\*.*" /to="'+exr_to_jpg_bak.replace('/','\\')+'"'
                    CLASS_COMMON_UTIL.cmd(exr_to_jpg_bak_move,my_log=self.G_DEBUG_LOG)          
                    
            self.G_DEBUG_LOG.info('[BASE.RB_CONVERT_SMALL_PIC.end.....]')
            self.format_log('done','end')
        
    '''
        上传渲染结果和日志
    ''' 
    def RB_HAN_RESULT(self):#7
        self.format_log('.结果处理...','start')
        self.G_DEBUG_LOG.info('[BASE.RB_HAN_RESULT.start.....]')    
        
        if self.G_ACTION in ['Analyze']:
            task_json_name='task.json'
            asset_json_name='asset.json'
            tips_json_name='tips.json'
            node_task_json = os.path.join(self.G_WORK_RENDER_TASK_CFG,task_json_name)
            node_asset_json = os.path.join(self.G_WORK_RENDER_TASK_CFG,asset_json_name)
            node_tips_json = os.path.join(self.G_WORK_RENDER_TASK_CFG,tips_json_name)
            if not os.path.exists(node_task_json):
                CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG,'Analyze  file failed . task.json not exists')
                
            self.copy_cfg_to_server(node_task_json,node_asset_json,node_tips_json)
        else:
            self.result_action()

        self.G_DEBUG_LOG.info('[BASE.RB_HAN_RESULT.end.....]')
        self.format_log('done','end')
        
    def RB_POST_RESET_NODE(self):
        pass
        
    def RB_POST_PY(self):#8 pre custom
        self.format_log('渲染完毕执行自定义脚本','start')
        self.G_DEBUG_LOG.info('[BASE.RB_POST_PY.start.....]')
        self.G_DEBUG_LOG.info('如果以下路径的脚本存在，则会被执行')
        post_py=os.path.join(self.G_NODE_PY,'CG',self.G_CG_NAME,'function','post.py')
        self.G_DEBUG_LOG.info(post_py)
        if os.path.exists(post_py):
            import post as POST_PY_MODEL
            self.POST_DICT=POST_PY_MODEL.main()
        
        self.G_DEBUG_LOG.info('[BASE.RB_POST_PY.end.....]')
        self.format_log('done','end')
        
    '''
        kafka发送消息给平台
    '''

    def RB_KAFKA_NOTIFY(self):#9
        if self.G_ACTION not in ['Analyze','Pre']:
            self.format_log('kafka发送消息给平台','start')
            self.G_DEBUG_LOG.info('[BASE.RB_KAFKA_NOTIFY.start.....]')
            
            send_time = str(int(time.time()))
            self.G_KAFKA_MESSAGE_DICT["munu_task_id"] = self.G_MUNU_ID
            self.G_KAFKA_MESSAGE_DICT["munu_job_id"] = self.G_JOB_ID
            self.G_KAFKA_MESSAGE_DICT["recommit_flag"] = self.G_RECOMMIT_FLAG
            self.G_KAFKA_MESSAGE_DICT["action"] = self.G_ACTION
            self.G_KAFKA_MESSAGE_DICT['platform']=self.G_PLATFORM
            self.G_KAFKA_MESSAGE_DICT['send_time']=send_time
            self.G_KAFKA_MESSAGE_DICT['zone']=self.G_ZONE
            self.G_KAFKA_MESSAGE_DICT['node_name']=self.G_NODE_ID
            self.G_KAFKA_MESSAGE_DICT['task_id']=self.G_TASK_ID
            self.G_KAFKA_MESSAGE_DICT['render_type']=self.G_RENDER_CORE_TYPE
            #self.G_KAFKA_MESSAGE_DICT['start_time']=self.G_START_TIME
            #self.G_KAFKA_MESSAGE_DICT['big_pic']=[]
            #self.G_KAFKA_MESSAGE_DICT['small_pic']=[]
            #self.G_KAFKA_MESSAGE_DICT['end_time']=self.G_END_TIME
            #self.G_KAFKA_MESSAGE_DICT['distribute_node'] = '1'
            
            self.G_DEBUG_LOG.info('G_KAFKA_MESSAGE_DICT='+str(self.G_KAFKA_MESSAGE_DICT))
            
            # write kafka message json file(e.g. C:\work\render\10002736\2017120500004_0_1.json)
            # kafka_message_filename = self.G_MUNU_ID+'_'+self.G_JOB_ID+'.json'
            kafka_message_filename = self.G_MUNU_ID+'_'+self.G_JOB_ID+'_'+self.G_RECOMMIT_FLAG+'.json'
            kafka_message_json = os.path.join(self.G_WORK_RENDER_TASK,kafka_message_filename)
            kafka_message_json_str = json.dumps(self.G_KAFKA_MESSAGE_DICT,ensure_ascii=False)
            CLASS_COMMON_UTIL.write_file(kafka_message_json_str,kafka_message_json)
            CLASS_COMMON_UTIL.python_copy(kafka_message_json,self.G_CONFIG_PATH)
            
            try:
                kafka_result=CLASS_KAFKA.produce(self.G_KAFKA_MESSAGE_DICT,self.G_KAFKA_SERVER,self.G_KAFKA_TOPIC)
                self.G_DEBUG_LOG.info('kafka_result='+str(kafka_result))
            except:
                CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG,'Send Kafka Message Failed',is_exit=False)
            
            self.G_DEBUG_LOG.info('[BASE.RB_KAFKA_NOTIFY.end.....]')
            self.format_log('done','end')
    
    
    def RB_FEE(self):
    
        # if not self.G_RENDER_CORE_TYPE=="gpu":
        if self.G_RENDER_OS != '0':
            CLASS_COMMON_UTIL.del_net_use()
            CLASS_COMMON_UTIL.del_subst()
    
        if self.G_ACTION not in ['Analyze','Pre']:
            self.format_log('write fee','start')
            self.G_DEBUG_LOG.info('[BASE.RB_FEE.start.....]')
            
            self.G_FEE_PARSER.set('render','type',self.G_RENDER_CORE_TYPE)
            # self.G_FEE_PARSER.set('render','start_time','')
            # self.G_FEE_PARSER.set('render','end_time','')
            # self.G_FEE_PARSER.set('render','big_pic','')
            # self.G_FEE_PARSER.set('render','small_pic','')
            
            try:
                with codecs.open(self.G_FEE_FILE, 'w', 'utf-8') as fee_file:
                    self.G_FEE_PARSER.write(fee_file)
            except Exception as e:
                CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG,'Write Fee File Failed',is_exit=False)
            
            self.G_DEBUG_LOG.info('[BASE.RB_FEE.end.....]')
            self.format_log('done','end')
            
    def RB_RESOURCE_MONITOR(self):
        self.G_DEBUG_LOG.info('[BASE.RB_RESOURCE_MONITOR start]')
        #parse B:\config\cg_process.json
        cg_process_path = r'B:\config\cg_process.json'
        resource_monitor = r'C:\work\munu_client\resource_monitor\resource_monitor.exe'  # resource_monitor  #1
        if self.G_RENDER_OS == '0':
            resource_monitor = r'/home/tools/munu_client/resource_monitor/resource_monitor'
            cg_process_path = r'/B/config/cg_process_linux.json'
            
        if not os.path.exists(cg_process_path):
            self.G_DEBUG_LOG.info('[warn]%s is not exists!!!' % cg_process_path)
        else:
            cg_process_dict = eval(codecs.open(cg_process_path, 'r', 'utf-8').read())
    
            #xxx.exe "3dsmax.exe" "1-5|19126418|1868556|3dsmax|vray,multiscatter"
            if not os.path.exists(resource_monitor):
                self.G_DEBUG_LOG.info('[warn]%s is not exists!!!' % resource_monitor)
            else:
                if self.G_ACTION not in ['Analyze','Pre'] and self.G_CG_NAME in cg_process_dict:
                    process_name_list = cg_process_dict[self.G_CG_NAME]
                    if len(process_name_list) <= 0:
                        self.G_DEBUG_LOG.info('[warn]The list of key %s in the %s is empty!!!' % (self.G_CG_NAME, cg_process_path))
                    else:
                        # process_name = process_name_list[self.G_CG_PROCESS_FLAG]  #2
                        process_name = '|'.join(process_name_list)  #2
                        # render_frame = self.G_CG_START_FRAME  #3
                        # if self.G_CG_START_FRAME != self.G_CG_END_FRAME:
                            # render_frame = self.G_CG_START_FRAME + '-' + self.G_CG_END_FRAME + '[' + self.G_CG_BY_FRAME + ']'
                        # self.G_JOB_ID  #3
                        # self.G_TASKID  #4
                        # self.G_USERID  #5
                        cg_flag = self.G_CG_VERSION  #6
                        plugin_string = r'' #7
                        if 'plugins' in self.G_CG_CONFIG_DICT:
                            for key,value in list(self.G_CG_CONFIG_DICT['plugins'].items()):
                                plugin_string += key+value+','
                            plugin_string = plugin_string.strip(',')
                        
                        if not plugin_string:
                            plugin_string = r'None'
                        
                        # command = resource_monitor + ' "' + process_name + '" "' + render_frame + '\t' + self.G_TASK_ID + '\t' + self.G_USER_ID + '\t' + cg_flag + '\t' + plugin_string + '"'
                        command = r'%s "%s" "%s|%s|%s|%s|%s"' % (resource_monitor, process_name, self.G_JOB_ID, self.G_TASK_ID, self.G_USER_ID, cg_flag, plugin_string)
                        
                        t = threading.Thread(target=self.monitor_cmd,args=(command, resource_monitor, ))
                        t.daemon = True
                        t.start()
                            
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
            
            
    '''
        初始化日志
    '''
    def init_log(self):
        log_dir=os.path.join(self.G_LOG_WORK,self.G_TASK_ID)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)        
        fm=logging.Formatter("%(asctime)s  %(levelname)s - %(message)s","%Y-%m-%d %H:%M:%S")
        # debug_log 不能开放给客户查看
        debug_log_path=os.path.join(log_dir,(self.G_ACTION_ID+'_debug.log'))
        self.G_DEBUG_LOG.setLevel(logging.DEBUG)
        debug_log_handler=logging.FileHandler(debug_log_path, encoding='utf-8')
        debug_log_handler.setFormatter(fm)
        self.G_DEBUG_LOG.addHandler(debug_log_handler)
        console = logging.StreamHandler()  
        console.setLevel(logging.INFO)  
        self.G_DEBUG_LOG.addHandler(console)
        
        # render_log 可开放给客户查看
        render_log_path=os.path.join(log_dir,(self.G_ACTION_ID+'_render.log'))
        self.G_RENDER_LOG.setLevel(logging.DEBUG)
        render_log_handler=logging.FileHandler(render_log_path, encoding='utf-8')
        render_log_handler.setFormatter(fm)
        self.G_RENDER_LOG.addHandler(render_log_handler)
        console = logging.StreamHandler()  
        console.setLevel(logging.INFO)  
        self.G_RENDER_LOG.addHandler(console)
    
    '''
        创建目录
    '''       
    def make_dir(self):
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
        #render
        if not os.path.exists(self.G_WORK_RENDER):
            os.makedirs(self.G_WORK_RENDER)
        #renderwork
        if not os.path.exists(self.G_WORK_RENDER_TASK):
            os.makedirs(self.G_WORK_RENDER_TASK)        
        #renderwork/cfg
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
        #renderwork/output
        if not os.path.exists(self.G_WORK_RENDER_TASK_OUTPUT):
            os.makedirs(self.G_WORK_RENDER_TASK_OUTPUT)            
        #renderwork/outputbak
        if not os.path.exists(self.G_WORK_RENDER_TASK_OUTPUTBAK):
            os.makedirs(self.G_WORK_RENDER_TASK_OUTPUTBAK)
        #renderwork/small
        if not os.path.exists(self.G_WORK_RENDER_TASK_SMALL):
            os.makedirs(self.G_WORK_RENDER_TASK_SMALL)
        self.G_DEBUG_LOG.info('[BASE.make_dir.end.....]')
        
    '''
        格式化日志
    '''
    def format_log(self,log_str,log_type='common'):
        if log_str==None:
            log_str=''
        if log_type!='system':
            log_str=CLASS_COMMON_UTIL.bytes_to_str(log_str)
            
        if log_type=='start':
            self.G_DEBUG_LOG.info('----------------------------['+log_str+']----------------------------\r\n')
        elif log_type=='end':
            self.G_DEBUG_LOG.info('['+log_str+']\r\n')
        else:
            self.G_DEBUG_LOG.info(log_str+'\r\n')

    
    '''
        拷贝弹窗黑名单 black.xml
    '''
    def copy_black(self):
        self.G_DEBUG_LOG.info('[BASE.copy_black.start.....]')
        block_path = 'B:\\tools\\sweeper\\black.xml'
        base_path='c:\\work\\munu_client\\sweeper\\'
        if self.G_RENDER_OS=='0':
            block_path="\\B\\tools\\sweeper\\black.xml"
            base_path="/root/rayvision/work/munu_client/sweeper/"
        self.G_DEBUG_LOG.info(block_path+'>'+base_path)
        if os.path.exists(block_path):
            CLASS_COMMON_UTIL.python_copy(block_path,base_path)
        self.G_DEBUG_LOG.info('[BASE.copy_black.end.....]')
        
        
    def sort_pic_list(self, pic_list):
        """ Returns list.
            功能：将缩略图列表重新排序。
            这将影响平台展示给客户的缩略图顺序，
            默认对列表不做任何修改操作，如需则在各自软件的脚本中重写该方法
            如：max重写该方法实现了将主图缩略图排在列表最前面，方便平台展示给客户（第一张即为主图）
        """
        return pic_list
    
        
    def convert_dir(self,dir,work_small_path):
        self.G_DEBUG_LOG.info('[BASE.convert_dir.start.....]')
        
        if os.path.exists(dir):
            small_size='200'
            # if self.G_KG=='1':
                # small_size='40'
            small_pic_list=[]
            # big_pic_list=[]
            list_dirs = os.walk(dir) 
            for root, dirs, files in list_dirs: 
                for name in files:
                    ext=os.path.splitext(name)[1]
                    self.G_DEBUG_LOG.info('name='+name)
                    if ext == '.vrmap' or   ext == '.vrlmap' or ext=='.exr':
                        continue    
                    work_big_pic =os.path.join(root, name)
                    # big_pic_list.append(work_big_pic.replace(dir+'\\','').replace('\\','/'))
                    small_pic=work_big_pic.replace(dir+'\\','')
                    small_pic=self.G_ACTION_ID+"_"+small_pic.replace('\\','[_]').replace('/','[_]').replace('.','[-]')+'.jpg'
                    small_pic_list.append(small_pic.replace('\\','/'))
                    small_tmp_name = self.G_ACTION_ID+'_tmp.jpg'
                    work_small_pic=os.path.join(work_small_path,small_pic)
                    work_small_tmp_pic=os.path.join(work_small_path,small_tmp_name)

                    work_big_pic_tmp=os.path.join(root, 'tmp'+os.path.splitext(work_big_pic)[1] )
                    try:
                        os.rename(work_big_pic,work_big_pic_tmp);
                    except Exception as e:
                        self.G_DEBUG_LOG.info('rename failed-----')
                        pass
                    if not os.path.exists(work_big_pic_tmp):
                        work_big_pic_tmp = work_big_pic
                        work_small_tmp_pic = work_small_pic

                    oiio_path='c:\\oiio\\OpenImageIO-1.5.18-bin-vc9-x64\\oiiotool.exe'
                    convert_cmd='c:/ImageMagick/nconvert.exe  -out jpeg -ratio -resize '+small_size+' 0 -overwrite -o "'+work_small_tmp_pic +'" "'+work_big_pic_tmp+'"'
                    if ext=='.exr' and os.path.exists(oiio_path):
                        self.G_DEBUG_LOG.info('exr parse----'+name)
                        convert_cmd=oiio_path+' "'+work_big_pic_tmp+'" -resize '+self.get_convert_r(work_big_pic_tmp,oiio_path)+' -o "'+work_small_tmp_pic+'"'
                    #print work_big_pic
                    try:
                        # CLASS_COMMON_UTIL.cmd(convert_cmd,my_log=self.G_DEBUG_LOG,continue_on_error=True)
                        # CLASS_COMMON_UTIL.cmd_python3(convert_cmd,my_log=self.G_DEBUG_LOG)
                        CLASS_COMMON_UTIL.cmd(convert_cmd,my_log=self.G_DEBUG_LOG)
                    except Exception as e:
                        self.G_DEBUG_LOG.info('parse smallPic failed-----')
                        pass
                    if not work_big_pic_tmp==work_big_pic:
                        os.rename(work_big_pic_tmp,work_big_pic)
                        if os.path.exists(work_small_tmp_pic):
                            os.rename(work_small_tmp_pic,work_small_pic)
                    self.G_DEBUG_LOG.info('work_small_tmp_pic---'+work_small_tmp_pic+'---work_small_pic---'+work_small_pic+'---work_big_pic_tmp---'+work_big_pic_tmp+'---work_big_pic---'+work_big_pic)
            # self.G_KAFKA_MESSAGE_DICT['small_pic']=small_pic_list
            # self.G_KAFKA_MESSAGE_DICT['big_pic']=big_pic_list
            
            small_pic_list = self.sort_pic_list(small_pic_list)
            
            small_pic_str = '|'.join(small_pic_list)
            self.G_FEE_PARSER.set('render','small_pic',small_pic_str)
        self.G_DEBUG_LOG.info('[BASE.convert_dir.end.....]')
    
    def check_result(self):
        self.G_DEBUG_LOG.info( '================[check_result]===============')
        # server_output=self.G_OUTPUT_USER_PATH.encode(sys.getfilesystemencoding())
        server_output=self.G_OUTPUT_USER_PATH
        node_output=self.G_WORK_RENDER_TASK_OUTPUT.replace('\\','/')
        self.G_DEBUG_LOG.info('')
        self.G_DEBUG_LOG.info(node_output)
        self.G_DEBUG_LOG.info(server_output)
        self.G_DEBUG_LOG.info('')
        node_img_dict={}
        server_img_dict={}
        output_list = os.listdir(node_output)
        if not output_list:
            CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG,'output is empty!')
        for root, dirs, files in os.walk(node_output) : 
            for name in files:
                #------------node output file----------------
                node_img_file =os.path.join(root, name).replace('\\','/')
                img_file=node_img_file.replace(node_output,'')
                
                img_file_stat=os.stat(node_img_file)
                img_file_size=str(os.path.getsize(node_img_file))
                node_img_dict[img_file]=img_file_size
                date = datetime.datetime.fromtimestamp(img_file_stat.st_ctime)  
                img_file_ctime= date.strftime('%Y%m%d%H%M%S')  
                #img_file_ctime=str(img_file_stat.st_ctime)
                img_file_info='[node]'+img_file+' ['+img_file_size+'] ['+img_file_ctime+']'
                
                self.G_DEBUG_LOG.info(img_file_info)
                #------------server output file----------------
                server_img_file=(server_output+img_file).replace('/','\\')
                server_img_file_info=''
                if os.path.exists(server_img_file):
                    img_file_stat=os.stat(server_img_file)
                    img_file_size=str(os.path.getsize(server_img_file))
                    
                    date = datetime.datetime.fromtimestamp(img_file_stat.st_ctime)  
                    img_file_ctime= date.strftime('%Y%m%d%H%M%S')
                    server_img_file_info='[server]'+img_file+' ['+img_file_size+'] ['+img_file_ctime+']'
                    server_img_dict[img_file]=img_file_size
                else:
                    server_img_file_info='[server]'+img_file+' [missing]'
                
                self.G_DEBUG_LOG.info(server_img_file_info)
                self.G_DEBUG_LOG.info('')
                
        self.G_DEBUG_LOG.info('')
    
    '''
        上传渲染结果和日志
    '''    
    def result_action(self):
        self.G_DEBUG_LOG.info('[BASE.result_action.start.....]')
        #RB_small
        if not os.path.exists(self.G_SMALL_PATH):
            os.makedirs(self.G_SMALL_PATH)
        if self.G_RENDER_OS=='0':
            output_path="/output"
            outputbak_path="/outputbak"
            # sp_path = 'outputdata5'
            sp_path = 'render_data'
            output_folder=self.G_OUTPUT_USER_PATH[self.G_OUTPUT_USER_PATH.rfind(sp_path)+len(sp_path):len(self.G_OUTPUT_USER_PATH)]
            output_mnt_path = self.G_OUTPUT_USER_PATH.replace(output_folder,'').replace('\\','/')
            output_mnt='mount -t cifs -o username=administrator,password=Rayvision@2016,codepage=936,iocharset=gb2312 '+output_mnt_path+' '+output_path
            
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            CLASS_COMMON_UTIL.cmd(output_mnt,my_shell=True)
            
            output_path=output_path+output_folder.replace("\\","/")
            if not os.path.exists(output_path):
                os.makedirs(output_path)
                
            self.rendering_copy_notify()
            
            CLASS_COMMON_UTIL.python_copy(self.G_WORK_RENDER_TASK_OUTPUT,output_path)
            CLASS_COMMON_UTIL.python_copy(self.G_WORK_RENDER_TASK_OUTPUT,self.G_WORK_RENDER_TASK_OUTPUTBAK)
        else:
            # output=self.G_OUTPUT_USER_PATH.encode(sys.getfilesystemencoding())
            output=self.G_OUTPUT_USER_PATH
            if self.G_CG_TILE_COUNT !='1' and self.G_CG_TILE_COUNT!=self.G_CG_TILE:
                output=self.G_TILES_PATH

            cmd1='c:\\fcopy\\FastCopy.exe  /speed=full /force_close  /no_confirm_stop /force_start "' +self.G_WORK_RENDER_TASK_OUTPUT.replace('/','\\') +'" /to="'+output+'"'
            # cmd2='"' +frame_check + '" "' + self.G_WORK_RENDER_TASK_OUTPUT + '" "'+ output.rstrip()+'"'
            cmd3='c:\\fcopy\\FastCopy.exe /cmd=move /speed=full /force_close  /no_confirm_stop /force_start "' +self.G_WORK_RENDER_TASK_OUTPUT.replace('/','\\')+'\\*.*" /to="'+self.G_WORK_RENDER_TASK_OUTPUTBAK.replace('/','\\')+'"'
            
            self.rendering_copy_notify()
            
            CLASS_COMMON_UTIL.cmd(cmd1,my_log=self.G_DEBUG_LOG,try_count=3)
            # CLASS_COMMON_UTIL.cmd_python3(cmd1,my_log=self.G_DEBUG_LOG)
            try:
                self.check_result()
            except Exception as e:
                print('[check_result.err]')
                print(e)
            CLASS_FRAME_CHECKER.main(self.G_WORK_RENDER_TASK_OUTPUT,output,my_log=self.G_DEBUG_LOG)
            # CLASS_COMMON_UTIL.cmd(cmd2,my_log=self.G_DEBUG_LOG)
            CLASS_COMMON_UTIL.cmd(cmd3,my_log=self.G_DEBUG_LOG,try_count=3,continue_on_error=True)
        self.G_DEBUG_LOG.info('[BASE.result_action.end.....]')

    def get_convert_r(self,path,oiio_path):
        try:
            cmd=oiio_path+' -info "'+path+'"'
            small_size = '200x0'
            cmdp = subprocess.Popen(cmd,shell = True,stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            while cmdp.poll()==None:
                result_line = cmdp.stdout.readline().strip()
                result_line = result_line.decode(sys.getfilesystemencoding())
                if result_line!='':
                    # print("-"+result_line)
                    info_array = result_line[result_line.rfind(':')+1:result_line.find(',')].split("x")
                    # print(info_array)
                    if int(info_array[0])<int(info_array[0]):
                        small_size = '0x200'
        except Exception as e:
            print('[getoiiosize.err]')
            print(e)
        return small_size  
    
    def copy_7z(self):
        zip=os.path.join(self.G_PLUGIN_PATH,'tools','7-Zip')
        copy_7z_cmd=r'c:\fcopy\FastCopy.exe /speed=full /force_close /no_confirm_stop /force_start "'+zip.replace('/','\\')+'" /to="d:\\"'
        CLASS_COMMON_UTIL.cmd(copy_7z_cmd,my_log=self.G_DEBUG_LOG)  
        
    def copy_cfg_to_server(self,node_task_json,node_asset_json,node_tips_json):
        self.G_DEBUG_LOG.info('[BASE.RBhanResult.node_task_json.....]'+node_task_json)
        self.G_DEBUG_LOG.info('[BASE.RBhanResult.node_asset_json.....]'+node_asset_json)
        self.G_DEBUG_LOG.info('[BASE.RBhanResult.node_tips_json.....]'+node_tips_json)
        CLASS_COMMON_UTIL.python_copy(node_task_json,self.G_CONFIG_PATH)
        CLASS_COMMON_UTIL.python_copy(node_asset_json,self.G_CONFIG_PATH)
        CLASS_COMMON_UTIL.python_copy(node_tips_json,self.G_CONFIG_PATH)
        
    def rendering_copy_notify(self, start_or_end='0'):
        """Notify platform the script executing a copy action, the user can't stop the task at this time."""
        
        # url = r'http://172.16.4.27:8980/api/rendering/task/common/renderingCopyInterface'
        # api_json_dir = r'\\10.60.100.104\new_render_data\input\p\api'  # from task.json
        api_json_dir = self.G_API_PATH
        api_json_path = os.path.join(api_json_dir, 'rendering_interface.json')
        api_json_dict = eval(codecs.open(api_json_path, 'r', 'utf-8').read())
        rendering_copy_interface = api_json_dict['rendering_copy_interface']
        
        data = {
            "munuTaskId":self.G_MUNU_ID,
            "munuJobId":self.G_JOB_ID,
            "platform":self.G_PLATFORM,
            "reCommitFlag":self.G_RECOMMIT_FLAG,
            "startOrEnd":start_or_end     #  0:start copy, 1:end copy
        }
        headers = {'Content-Type': 'application/json'}
        request = urllib.request.Request(url=rendering_copy_interface, headers=headers, data=json.dumps(data).encode('utf-8'))
        try:
            response = urllib.request.urlopen(request)
            self.G_DEBUG_LOG.info(response.read())
        except Exception as e:
            self.G_DEBUG_LOG.info('[err]url can\'t open:%s' % rendering_copy_interface)
    
    
    
        
    '''
        渲染流程控制函数，子类可以覆盖方法
    '''   
    def RB_EXECUTE(self):#total
    
        self.format_log('\r\n--------------------------------------------小任务开始--------------------------------------------\r\n')        
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
        self.format_log('\r\n--------------------------------------------小任务结束--------------------------------------------\r\n')
        self.G_DEBUG_LOG.info('[BASE.RB_EXECUTE.end.....]')
        sys.exit(0)