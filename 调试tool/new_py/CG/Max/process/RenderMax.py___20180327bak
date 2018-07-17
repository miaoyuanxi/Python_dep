#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
import subprocess
import string
import time
import shutil
import codecs
import configparser
import threading
import time
import json
import socket
import re

from Max import Max
from NodeHelper import NodeHelper

from MaxUtil import RBMonitorMaxThread
from MaxUtil import RBMonitorLMU
from MaxUtil import RBMonitorLog
from MaxUtil import RBMaxLog
# from MaxUtil import RBDogUtil
from MaxPlugin import MaxPlugin                               

# from CommonUtil import Common
from CommonUtil import RBCommon as CLASS_COMMON_UTIL
from MaxUtil import RBMaxUtil as CLASS_MAX_UTIL
from FrameChecker import RBFrameChecker as CLASS_FRAME_CHECKER

pySitePackagesNode=r'c:\script\pySitePackages'
if os.path.exists(pySitePackagesNode):
    sys.path.append(pySitePackagesNode)
    from MaxThread import MaxThread
     
#---------------------calss maxclient--------------------
class RenderMax(Max):
    def __init__(self,**param_dict):
        Max.__init__(self,**param_dict)
        self.format_log('RenderMax.init','start')
        for key,value in list(self.__dict__.items()):
            self.G_DEBUG_LOG.info(key+'='+str(value))
        self.format_log('done','end')       

        
        #self.G_CG_CONFIG_DICT=self.G_TASK_JSON_DICT['software_config']
        
        # self.G_RENDER_CAMERA=param_dict['G_CG_OPTION']                
        #self.PLUGINS_MAX_SCRIPT='B:/plugins/max/script/user'        
        # if param_dict.has_key('G_JOB_ID'):
            # self.G_JOB_NAME=param_dict['G_JOB_ID']            
        # if param_dict.has_key('G_SCHEDULER_CLUSTER_NODES'):
            # self.G_SCHEDULER_CLUSTER_NODES = param_dict['G_SCHEDULER_CLUSTER_NODES']   
        # self.G_MUNU_ID=self.G_SYS_ARGVS[1]
        # self.G_JOB_ID=self.G_SYS_ARGVS[2]        
        # print '--------------jobid-------------'
        # print type(self.G_JOB_NAME)
        # self.G_JOB_NAME_STR=self.G_JOB_NAME
        # self.G_JOB_NAME=self.G_JOB_NAME.encode(sys.getfilesystemencoding())
        # print type(self.G_JOB_NAME)        
        
        #grab server
        self.HOST='127.0.0.1'#'192.168.0.49'
        self.PORT=10100 
        self.BUFSIZ=1024
        self.ADDR=(self.HOST, self.PORT)        
        
        # self.G_ONLY_PHOTON = self.G_TASK_JSON_DICT['miscellaneous']['only_photon']
        
        #----------------------qsy20160712-----------------------
        self.G_MAX_SCRIPT_NAME='renderu.ms'#max2013,max204,max2015
        self.G_CUSTOM_BAT_NAME='custom.bat'
        self.G_USER_HOST_NAME='hosts.txt'
        #self.G_PROGRAMFILES='C:/Program Files'

        #____________________custom________________________
        self.MAX_CMD_RENDER=False
        self.MAX_VRAY_DISTRIBUTE=False
        if 'G_SCHEDULER_CLUSTER_NODES' in param_dict and len(self.G_SCHEDULER_CLUSTER_NODES) > 0:
            self.MAX_VRAY_DISTRIBUTE=True
        #self.RENDER_MODE='location'
        
        #----------------------get render frames-----------------------
        self.G_CG_FRAMES = self.get_render_frame()
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
    
    
        #------------------------------------------------        
        self.G_RAYVISION_MAX_MS = ''
        
        
    '''
        拷贝脚本文件
    '''
    def RB_HAN_FILE(self):#3  copy max.7z and so on
        self.format_log('拷贝脚本文件','start')
        self.G_DEBUG_LOG.info('[RenderMax.RB_HAN_FILE.start.....]'+self.G_RENDER_CORE_TYPE)
        
        CLASS_COMMON_UTIL.python_move(self.G_WORK_RENDER_TASK_OUTPUT,self.G_WORK_RENDER_TASK_OUTPUTBAK)
        
        if int(self.G_CG_TILE_COUNT)>1 and self.G_CG_TILE_COUNT==self.G_CG_TILE:#merge Pic
            self.G_RENDER_WORK_TASK_BLOCK=os.path.join(self.G_RENDER_WORK_TASK,'block').replace('/','\\')
            
            block_path1=os.path.join(self.G_TEMP_PATH,self.G_TASK_ID,'block').replace('/','\\')
            self.G_DEBUG_LOG.info(block_path1)
            if not os.path.exists(block_path1):
                CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG,'block not exists in temp folder')
            copy_block_cmd='c:\\fcopy\\FastCopy.exe   /speed=full /force_close  /no_confirm_stop /force_start "'+block_path1+'\\*.*" /to="'+self.G_RENDER_WORK_TASK_BLOCK.replace('/','\\')+'"'
            # copy_block_cmd=copy_block_cmd.encode(sys.getfilesystemencoding())
            CLASS_COMMON_UTIL.cmd(copy_block_cmd,my_log=self.G_DEBUG_LOG)
        else:
        
            #----------------copy max 7z-------------------
            max_7z=os.path.join(self.G_TEMP_PATH,'max.7z')
            if not os.path.exists(max_7z):
                CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG,'max.7z not exists in temp folder')
            copy_max_7z_cmd='c:\\fcopy\\FastCopy.exe /cmd=diff /speed=full /force_close  /no_confirm_stop /force_start "'+max_7z.replace('/','\\')+'" /to="'+self.G_WORK_RENDER_TASK_MAX.replace('/','\\')+'"'
            self.G_DEBUG_LOG.info(copy_max_7z_cmd)
            # CLASS_COMMON_UTIL.cmd(copy_max_7z_cmd.encode(sys.getfilesystemencoding()),my_log=self.G_DEBUG_LOG,my_shell=True)
            CLASS_COMMON_UTIL.cmd(copy_max_7z_cmd,my_log=self.G_DEBUG_LOG,my_shell=True)
            node_max_7z=os.path.join(self.G_WORK_RENDER_TASK_MAX,'max.7z')
            if not os.path.exists(node_max_7z):
                CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG,('max.7z not exists in '+self.G_WORK_RENDER_TASK_MAX))
            
            #----------------send cmd to node-------------------
            self.vray_distribute_node()
            
            #------------------unpack max.7z----------------
            self.G_DEBUG_LOG.info('unpack 7z...')
            unpack_cmd=self.G_DRIVERC_7Z+' x "'+node_max_7z+'" -y -aos -o"'+self.G_WORK_RENDER_TASK_MAX+'"' 
            self.G_DEBUG_LOG.info(unpack_cmd)
            # CLASS_COMMON_UTIL.cmd(unpack_cmd.encode(sys.getfilesystemencoding()),my_log=self.G_DEBUG_LOG,my_shell=True)
            CLASS_COMMON_UTIL.cmd(unpack_cmd,my_log=self.G_DEBUG_LOG,my_shell=True)
            
            #----------------copy photon-------------------
            self.copy_photon()
            
        self.G_DEBUG_LOG.info('[RenderMax.RB_HAN_FILE.end.....]')
        self.format_log('done','end')
        
        
    def RB_CONFIG(self):
        self.format_log('渲染配置','start')
        self.G_DEBUG_LOG.info('[RenderMax.RB_CONFIG.start.....]')
        
        CLASS_MAX_UTIL.killMaxVray(self.G_DEBUG_LOG)  #kill 3dsmax.exe,3dsmaxcmd.exe,vrayspawner*.exe
        
        #----------------start grab_service-------------------
        grabServer=r'C:/work/munu_client/grab_service/grab_service.exe'
        self.G_DEBUG_LOG.info(grabServer)        
        if os.path.exists(grabServer) and CLASS_MAX_UTIL.checkProcess('grab_service'):
            self.G_DEBUG_LOG.info('start grab_service')
            os.system('start '+grabServer)

        #----------------check config file-------------------
        if self.G_CG_VERSION=='3ds Max 2012' or self.G_CG_VERSION=='3ds Max 2011' or self.G_CG_VERSION=='3ds Max 2010' or self.G_CG_VERSION=='3ds Max 2009':
            self.G_MAX_SCRIPT_NAME='rendera1.3.ms'
        else:
            self.G_MAX_SCRIPT_NAME='renderu1.3.ms'            
        self.G_DEBUG_LOG.info('maxscriptName------'+self.G_MAX_SCRIPT_NAME)        
        custom_script_path=os.path.join(self.G_MAX_SCRIPT,'user',self.G_USER_ID)
        custom_ms=os.path.join(custom_script_path,self.G_MAX_SCRIPT_NAME)
        custom_bat=os.path.join(custom_script_path,self.G_CUSTOM_BAT_NAME)
        max_ini=os.path.join(self.G_MAX_B,'ini','3dsmax',self.G_CG_VERSION,'3dsmax.ini')
        max_user_ini=os.path.join(self.G_MAX_B,'ini','3dsmax',self.G_USER_ID,self.G_CG_VERSION,'3dsmax.ini')
        user_host_file=os.path.join(custom_script_path,self.G_USER_HOST_NAME)
        net_render_txt=os.path.join(self.G_MAX_SCRIPT,'user',self.G_USER_ID,'netrender.txt')        
        config_file_list=[custom_script_path,custom_ms,custom_bat,max_ini,max_user_ini,user_host_file,net_render_txt]
        self.check_config_file(config_file_list)
        
        #----------------load max plugin-------------------
        self.G_DEBUG_LOG.info('插件配置')
        max_plugin=MaxPlugin(self.G_CG_CONFIG_DICT,self.G_DEBUG_LOG)
        max_plugin.config()
        
        #----------------write vray_dr.cfg-------------------
        self.vray_distribute_root()        
        
        #----------------subst path------------------
        if not os.path.exists(net_render_txt):
            self.subst_path()
            
        #-----------render.ms--------
        self.G_RAYVISION_MAX_MS=os.path.join(self.G_MAX_SCRIPT,self.G_MAX_SCRIPT_NAME).replace('\\','/')
        if os.path.exists(custom_ms):
            self.G_RAYVISION_MAX_MS=custom_ms
            
        #----------delete max log----------
        user_profile=os.environ["userprofile"]
        max_enu=user_profile+'\\AppData\\Local\\Autodesk\\3dsMax\\'+self.G_CG_VERSION.replace('3ds Max ','')+' - 64bit\\enu'
        max_log=max_enu+'\\Network\\Max.log'        
        self.G_DEBUG_LOG.info(max_log)
        if os.path.exists(max_log):
            try:
                os.remove(max_log)
            except Exception as e:
                self.G_DEBUG_LOG.info(e)
        
        #----------delete vary log----------
        user_temp_file=os.environ["temp"]
        my_temp_vray_log=os.path.join(user_temp_file,'vraylog.txt').replace('\\','/')
        self.G_DEBUG_LOG.info(my_temp_vray_log)
        if os.path.exists(my_temp_vray_log):
            try:
                os.remove(my_temp_vray_log)
            except Exception as e:
                self.G_DEBUG_LOG.info(e)
                
        #----------Customer 3dsmax.ini----------
        try:            
            if os.path.exists(max_ini) and os.path.exists(max_enu) :
                copy_max_ini_cmd='xcopy /y /v /f "'+max_ini +'" "'+max_enu.replace('\\','/')+'/"'             
            if os.path.exists(max_user_ini) and os.path.exists(max_enu) :
                copy_max_ini_cmd='xcopy /y /v /f "'+max_user_ini +'" "'+max_enu.replace('\\','/')+'/"' 
            self.G_DEBUG_LOG.info(copy_max_ini_cmd)
            CLASS_COMMON_UTIL.cmd(copy_max_ini_cmd,my_log=self.G_DEBUG_LOG)
        except Exception as e:
            self.G_DEBUG_LOG.info('[err].3dsmaxIni Exception')
            self.G_DEBUG_LOG.info(e)            
        
        #------------CurrentDefaults.ini----------
        default_max=os.path.join(max_enu,'en-US/defaults/MAX').replace('\\','/')+'/'
        if self.G_CG_VERSION=='3ds Max 2010' or self.G_CG_VERSION=='3ds Max 2011' or self.G_CG_VERSION=='3ds Max 2012':
            default_max=os.path.join(max_enu,'defaults/MAX').replace('\\','/')+'/'
        if 'gamma' in self.G_TASK_JSON_DICT['scene_info_render']['common']:
            current_default_ini_gamma=os.path.join(self.G_MAX_B,'ini/3dsmaxDefault/gammaOn',self.G_CG_VERSION,'CurrentDefaults.ini').replace('\\','/')
            if self.G_TASK_JSON_DICT['scene_info_render']['common']['gamma'] == 'off':
                current_default_ini_gamma=os.path.join(self.G_MAX_B,'ini/3dsmaxDefault/gammaOff',self.G_CG_VERSION,'CurrentDefaults.ini').replace('\\','/')
            
            self.G_DEBUG_LOG.info('---current_default_ini_gamma---')
            self.G_DEBUG_LOG.info(current_default_ini_gamma)
            if os.path.exists(current_default_ini_gamma):
                copy_default_max_ini_cmd='xcopy /y /v /f "'+current_default_ini_gamma +'" "'+default_max+'"' 
                self.G_DEBUG_LOG.info(copy_default_max_ini_cmd)
                CLASS_COMMON_UTIL.cmd(copy_default_max_ini_cmd,my_log=self.G_DEBUG_LOG)

        #------------custom.bat----------
        if os.path.exists(custom_bat):
            custom_cmd=custom_bat+' "'+self.G_USER_ID+'" "'+self.G_TASK_ID+'" '
            self.G_DEBUG_LOG.info('执行custom.bat定制脚本')
            CLASS_COMMON_UTIL.cmd(custom_cmd,my_log=self.G_DEBUG_LOG)
            
        #------------host----------
        self.config_host(user_host_file)
        
        #------------red shift license----------
        try:
            # self.G_DEBUG_LOG.info('environ redshift_license 5053@10.50.10.231')
            # os.environ['redshift_license']='5053@10.50.10.231'
            self.G_DEBUG_LOG.info('environ redshift_license')
            license_env_path = os.path.join(self.G_MAX_B,'ini','config','license_env.json')
            with open(license_env_path,'r') as pl:
                pl_dict = json.load(pl)
                self.G_DEBUG_LOG.info(pl_dict)
                if 'plugins' in self.G_CG_CONFIG_DICT:
                    for plugins_key in list(self.G_CG_CONFIG_DICT['plugins'].keys()):
                        plugin_str = plugins_key + self.G_CG_CONFIG_DICT['plugins'][plugins_key]
                        if plugin_str in pl_dict:
                            env_name = pl_dict[plugin_str]["env_name"]
                            env_value = pl_dict[plugin_str]["env_value"]
                            os.environ[env_name]=env_value
        except Exception as e:
            self.G_DEBUG_LOG.info('[err].red shift license env')
            self.G_DEBUG_LOG.info(e)
        
        #------------max cmd render----------
        # maxCmdTxt=os.path.join(self.G_MAXSCRIPT,'user',self.G_USERID,'maxcmd.txt').replace('\\','/')
        max_cmd_txt=os.path.join(self.G_MAX_SCRIPT,'user',self.G_USER_ID,'maxcmd.txt')
        if os.path.exists(max_cmd_txt):
            self.MAX_CMD_RENDER=True
        if 'render_type' in self.G_TASK_JSON_DICT['miscellaneous'] and self.G_TASK_JSON_DICT['miscellaneous']['render_type'] == 'maxcmd':
            self.MAX_CMD_RENDER=True
        # if self.MAX_CMD_RENDER:
            # self.G_CG_PROCESS_FLAG = 1
        self.G_DEBUG_LOG.info('MAX_CMD_RENDER=' + str(self.MAX_CMD_RENDER))
                
        #----------------------get max file-----------------------
        self.MAX_FILE = self.get_max_file(self.G_INPUT_CG_FILE)
        
        #maxlog.txt,vray.log
        #max plugin
        #host
        #3dsmax.ini,CurrentDefaults
        #red shift license
        #custom.bat
        
        self.G_DEBUG_LOG.info('[RenderMax.RB_CONFIG.end.....]')
        self.format_log('done','end')
    '''
        渲染
    '''
    def RB_RENDER(self):#5
        self.format_log('渲染','start')
        self.G_DEBUG_LOG.info('[RenderMax.RB_RENDER.start.....]')
        
        #------------wtite ms file----------
        task_ms_file = self.write_ms_file()
        
        #------------get render cmd----------
        render_cmd = self.get_render_cmd(task_ms_file)
        self.G_DEBUG_LOG.info(render_cmd)
        
        #------------show desktop----------
        self.G_DEBUG_LOG.info('showdesktop.start')
        try:
            os.system('B:/tools/showDesktop.exe')
        except Exception as e:
            print('exception in showDesktop')
            print(e)
        self.G_DEBUG_LOG.info('showdesktop.end')  
        
        #------------start grab----------
        self.start_grab()
        
        # max_exe='"C:/Program Files/Autodesk/'+ self.G_CG_VERSION+'/3dsmax.exe"'
        # render_cmd = max_exe+' -silent  -ma -mxs "filein \\"'+task_ms_file+'\\";renderRun() "'
        
        #------------render----------
        # render_cmd=render_cmd.encode(sys.getfilesystemencoding())
        # self.G_KAFKA_MESSAGE_DICT['start_time']=str(int(time.time()))
        self.G_FEE_PARSER.set('render','start_time',str(int(time.time())))
        # CLASS_MAX_UTIL.max_cmd(render_cmd,self.G_DEBUG_LOG,True,True)
        self.G_DEBUG_LOG.info("\n\n-------------------------------------------Start max program-------------------------------------\n\n")
        CLASS_COMMON_UTIL.cmd(render_cmd,my_log=self.G_DEBUG_LOG,continue_on_error=True,my_shell=True,callback_func=CLASS_MAX_UTIL.max_cmd_callback)
        # self.G_KAFKA_MESSAGE_DICT['end_time']=str(int(time.time()))
        self.G_FEE_PARSER.set('render','end_time',str(int(time.time())))
        
        #------------rename photon file,add serial number----------
        self.rename_photon_file()      
        
        #------------stop PrintScreen----------
        self.stop_grab()
        
        #------------write renderLog----------
        max_log = RBMaxLog(self.G_TASK_ID,self.G_CG_VERSION,self.G_DEBUG_LOG,self.G_LOG_WORK,self.G_ACTION_ID)
        max_log.do()
        
        #------------from node copy Max.log and vraylog.txt to master host----------
        self.get_max_vray_log()
        
        self.G_DEBUG_LOG.info('[RenderMax.RB_RENDER.end.....]')
        self.format_log('done','end')
        
    def RB_HAN_RESULT(self):
        if self.G_ACTION == 'RenderPhoton':
            if self.G_KG=='100' or self.G_KG=='101' or self.G_KG=='102':#inc
                self.result_action_photon()
        else:
            self.result_action()
        
    def RB_POST_RESET_NODE(self):
        CLASS_MAX_UTIL.killMaxVray(self.G_DEBUG_LOG)
        
        # time.sleep(3)
        self.G_DEBUG_LOG.info('DEBUG_TASKKILL_MAXADAPTER')
        try:
            os.system('taskkill /F /IM maxadapter.adp.exe /T')
        except Exception as e:
            self.G_DEBUG_LOG.info('taskkill maxadapter.adp.exe exeception')  
            self.G_DEBUG_LOG.info(e) 
        
    def make_dir_max(self):
        
        self.G_DEBUG_LOG.info(self.G_WORK_RENDER_TASK_BLOCK)
        self.G_DEBUG_LOG.info(self.G_WORK_RENDER_TASK_GRAB)
        self.G_DEBUG_LOG.info(self.G_WORK_RENDER_TASK_MAX)
        self.G_DEBUG_LOG.info(self.G_WORK_RENDER_TASK_MAXBAK)
                
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
    
    def write_ms_file(self):
        
        not_render='false'
        if self.G_CG_VERSION=='3ds Max 2012' or self.G_CG_VERSION=='3ds Max 2011' or self.G_CG_VERSION=='3ds Max 2010' or self.G_CG_VERSION=='3ds Max 2009':
            render_ms_name='rendera2.0.ms'
            json_file = self.G_TASK_JSON_A
        else:
            render_ms_name='renderu2.0.ms'            
            json_file = self.G_TASK_JSON
        
        # render_frame = get_render_frame()
            
        render_ms=os.path.join(self.G_NODE_MAXSCRIPT,render_ms_name).replace('\\','/')
        task_ms_file=os.path.join(self.G_WORK_RENDER_TASK_CFG,('render'+self.G_CG_FRAMES+'.ms')).replace('\\','/')
        
        # self.MAX_FILE=self.get_max_file(self.G_INPUT_CG_FILE)
        ms_str='(DotNetClass "System.Windows.Forms.Application").CurrentCulture = dotnetObject "System.Globalization.CultureInfo" "zh-cn"\r\n'
        ms_str=ms_str+'filein @"'+render_ms+'"\r\n'
        ms_str=ms_str+'fn renderRun = (\r\n'
        ms_str=ms_str+'web_render #("'+self.G_USER_ID+'","'+self.G_TASK_ID+'","'+not_render+'","'+self.G_CG_FRAMES+'","'
        ms_str=ms_str+self.G_ACTION_ID+'","'+self.G_CG_OPTION+'","'+self.G_ACTION+'","'+self.G_WORK_RENDER_TASK_OUTPUT_XXX+'/'+'","'+self.MAX_FILE+'", @"'
        ms_str=ms_str+json_file.replace('\\','/')+'"'
        ms_str=ms_str+',"'+self.G_KG+'"'
        ms_str=ms_str+') \r\n)'
        if self.G_CG_VERSION=='3ds Max 2012' or self.G_CG_VERSION=='3ds Max 2011' or self.G_CG_VERSION=='3ds Max 2010' or self.G_CG_VERSION=='3ds Max 2009':
            CLASS_COMMON_UTIL.write_file(ms_str,task_ms_file,my_code='gbk')
        else:
            CLASS_COMMON_UTIL.write_file(ms_str,task_ms_file,my_code='utf-8')
        
        self.G_DEBUG_LOG.info('[RenderMax.write_ms_file.end.....]')
        return task_ms_file   
        
    def get_max_file(self,source_max_file):
        if self.G_CHANNEL == '1' or self.G_CHANNEL=='2':#WEB
            return self.get_max_file_web(source_max_file)
        else:
            pass
            #return self.get_max_file_client(source_max_file)
            
            
    def get_max_file_web(self,source_max_file):
        self.G_DEBUG_LOG.info('\r\n\r\n\r\n-----------[-getMaxFileWeb-]--------------\r\n\r\n\r\n')
        if self.MAX_CMD_RENDER:
            self.G_DEBUG_LOG.info('cmd render web')
            max_file_path_web=os.path.join(self.G_WORK_RENDER_TASK_MAX,(self.G_TASK_ID+r'.max'))
            self.G_DEBUG_LOG.info(max_file_path_web)
            return max_file_path_web
        result_max_file = self.G_WORK_RENDER_TASK_MAX+'/'+os.path.basename(source_max_file)
        result_max_file=result_max_file.replace('\\','/')
        return result_max_file
        
    def get_max_file_client(self,source_max_file):
        self.G_DEBUG_LOG.info('-----getMaxFileClient-----')
        
        return os.path.normpath(source_max_file)

    def rename_photon_taskid(self, photon_work_path, id_from, id_to):
        if os.path.exists(photon_work_path):
            for root, dirs , files in os.walk(photon_work_path):
                for name in files:
                    if name.endswith('vrmap') or name.endswith('vrlmap'):
                        photon_file = os.path.join(root,name)
                        name_new = id_to + name[len(id_from):]
                        photon_file_new = os.path.join(root,name_new)
                        if not os.path.exists(photon_file_new):
                            os.rename(photon_file,photon_file_new)
        
    def copy_photon(self):        
        if  self.G_KG=='100' or self.G_KG=='101' or self.G_KG=='102':#inc
            if self.G_ACTION == 'Render':
                photon_project_path=os.path.join(self.G_INPUT_PROJECT_PATH,'photon',self.G_PHOTON_SMALL_TASK_ID)
                photon_work_path=os.path.join(self.G_WORK_RENDER_TASK_MAX,'photon')
                # if self.G_MULTI_CAMERA:
                    # photon_project_path=os.path.join(self.G_INPUT_PROJECT_PATH,'photon',self.G_PHOTON_SMALL_TASK_ID)
                    # photon_work_path=os.path.join(self.G_WORK_RENDER_TASK_MAX,'photon')
                # photon_project_path = photon_project_path.decode('utf-8')
                
                if os.path.exists(photon_work_path) and os.path.isdir(photon_work_path):
                    try:
                        shutil.rmtree(photon_work_path)
                    except:
                        self.G_DEBUG_LOG.info('[warn]error delete directory:%s' % photon_work_path) 
                
                if os.path.exists(photon_project_path):
                    copy_photon_cmd=r'c:\fcopy\FastCopy.exe /speed=full /force_close /no_confirm_stop /force_start "'+photon_project_path.replace('/','\\')+'\\*.*" /to="'+photon_work_path.replace('/','\\')+'"'
                    CLASS_COMMON_UTIL.cmd(copy_photon_cmd,my_log=self.G_DEBUG_LOG)
                    # CLASS_COMMON_UTIL.cmd_python3(copy_photon_cmd,my_log=self.G_DEBUG_LOG)
                    
                    self.rename_photon_taskid(photon_work_path, self.G_PHOTON_SMALL_TASK_ID, self.G_TASK_ID)
    
    def result_action_photon(self):
        if self.G_ONLY_PHOTON == 'true':
            upload_path = self.G_OUTPUT_USER_PATH
            self.rename_photon_taskid(self.G_WORK_RENDER_TASK_OUTPUT, self.G_TASK_ID, self.G_SMALL_TASK_ID)
        else:
            if self.G_KG == '102':#fast inc map
                upload_path = os.path.join(self.G_TEMP_PATH,'photon')
                if self.G_MULTI_CAMERA:
                    upload_path = os.path.join(self.G_TEMP_PATH,'photon',self.G_SMALL_TASK_ID)
            else:
                upload_path = os.path.join(self.G_INPUT_PROJECT_PATH,'photon',self.G_SMALL_TASK_ID)     
                self.rename_photon_taskid(self.G_WORK_RENDER_TASK_OUTPUT, self.G_TASK_ID, self.G_SMALL_TASK_ID)
        
        cmd1='c:\\fcopy\\FastCopy.exe  /speed=full /force_close  /no_confirm_stop /force_start "' +self.G_WORK_RENDER_TASK_OUTPUT_XXX.replace('/','\\') +'" /to="'+upload_path+'"'
        # cmd2='c:\\fcopy\\FastCopy.exe  /speed=full /force_close  /no_confirm_stop /force_start "' +self.G_WORK_RENDER_TASK_OUTPUT.replace('/','\\') +'" /to="'+self.G_OUTPUT_USER_PATH+'"'
        # cmd2='"' +frame_check + '" "' + self.G_WORK_RENDER_TASK_OUTPUT + '" "'+ upload_path.rstrip()+'"'
        cmd3='c:\\fcopy\\FastCopy.exe /cmd=move /speed=full /force_close  /no_confirm_stop /force_start "' +self.G_WORK_RENDER_TASK_OUTPUT.replace('/','\\')+'\\*.*" /to="'+self.G_WORK_RENDER_TASK_OUTPUTBAK.replace('/','\\')+'"'
        
        self.rendering_copy_notify()
        
        CLASS_COMMON_UTIL.cmd(cmd1,my_log=self.G_DEBUG_LOG,try_count=3)
        # CLASS_COMMON_UTIL.cmd_python3(cmd1,my_log=self.G_DEBUG_LOG)
        # if upload_path != self.G_OUTPUT_USER_PATH:
            ##CLASS_COMMON_UTIL.cmd(cmd2.decode('utf-8').encode(sys.getfilesystemencoding()),my_log=self.G_DEBUG_LOG,try_count=3)
            # CLASS_COMMON_UTIL.cmd_python3(cmd2,my_log=self.G_DEBUG_LOG)
            
        # try:
            # self.check_result()
        # except Exception, e:
            # print '[check_result.err]'
            # print e
        CLASS_FRAME_CHECKER.main(self.G_WORK_RENDER_TASK_OUTPUT_XXX,upload_path,my_log=self.G_DEBUG_LOG)
        # CLASS_COMMON_UTIL.cmd(cmd2,my_log=self.G_DEBUG_LOG)
        CLASS_COMMON_UTIL.cmd(cmd3,my_log=self.G_DEBUG_LOG,try_count=3,continue_on_error=True)
    
    def result_action(self):
        self.G_DEBUG_LOG.info('[Max.result_action.start.....]')
        output=self.G_OUTPUT_USER_PATH
        if self.G_CG_TILE_COUNT !='1' and self.G_CG_TILE_COUNT!=self.G_CG_TILE:
            output=self.G_TILES_PATH

        cmd1='c:\\fcopy\\FastCopy.exe  /speed=full /force_close  /no_confirm_stop /force_start "' +self.G_WORK_RENDER_TASK_OUTPUT_XXX.replace('/','\\') +'" /to="'+output+'"'
        cmd3='c:\\fcopy\\FastCopy.exe /cmd=move /speed=full /force_close  /no_confirm_stop /force_start "' +self.G_WORK_RENDER_TASK_OUTPUT.replace('/','\\')+'\\*.*" /to="'+self.G_WORK_RENDER_TASK_OUTPUTBAK.replace('/','\\')+'"'
        
        self.rendering_copy_notify()
        
        # CLASS_COMMON_UTIL.cmd_python3(cmd1,my_log=self.G_DEBUG_LOG)
        CLASS_COMMON_UTIL.cmd(cmd1,my_log=self.G_DEBUG_LOG)
        try:
            self.check_result()
        except Exception as e:
            print('[check_result.err]')
            print(e)
        CLASS_FRAME_CHECKER.main(self.G_WORK_RENDER_TASK_OUTPUT_XXX,output,my_log=self.G_DEBUG_LOG)
        CLASS_COMMON_UTIL.cmd(cmd3,my_log=self.G_DEBUG_LOG,try_count=3,continue_on_error=True)
        self.G_DEBUG_LOG.info('[Max.result_action.end.....]')
    
    
    def check_config_file(self,config_file_list):
        self.G_DEBUG_LOG.info('相关配置文件') 
        for config_file in config_file_list:
            if os.path.exists(config_file):
                self.G_DEBUG_LOG.info(config_file+'[exists]') 
            else:
                self.G_DEBUG_LOG.info(config_file+'[missing]')
                
    def subst_path(self):        
        self.G_DEBUG_LOG.info('[RenderMax.subst_path.start.....]')
        bat_str = ''
        for file_name in os.listdir(self.G_WORK_RENDER_TASK_MAX):
            self.G_DEBUG_LOG.info(file_name)
            if os.path.isfile(os.path.join(self.G_WORK_RENDER_TASK_MAX,file_name)):
                continue
            dir_name=file_name.lower()
            dir_path=os.path.join(self.G_WORK_RENDER_TASK_MAX,file_name).lower()
            self.G_DEBUG_LOG.info(dir_name)            
            if dir_name=='net':
                continue
            if dir_name=='default':
                continue            
            if dir_name=='b' or dir_name=='c' or dir_name=='d':
                continue
            #e,f,g...
            if len(dir_name)==1:
                subst_cmd='subst '+dir_name+': "'+dir_path+'"'
                self.G_DEBUG_LOG.info(subst_cmd)     
                os.system(subst_cmd)
                bat_str=bat_str+subst_cmd+'\r\n'
        bat_file=os.path.join(self.G_WORK_RENDER_TASK_CFG,'substDriver.bat')
        CLASS_COMMON_UTIL.write_file(bat_str,bat_file)
        self.G_DEBUG_LOG.info('[RenderMax.subst_path.end.....]')
        
    def config_host(self,user_host_file):
        self.G_DEBUG_LOG.info('用户自定制HOSTS操作：如果用户自定制的hosts文件存在，则会在渲染前把hosts配置文件的内容追加写到节点机hosts文件中')
        self.G_DEBUG_LOG.info('用户自定制的hosts文件路径：')
        self.G_DEBUG_LOG.info(user_host_file)
        self.G_DEBUG_LOG.info('[RenderMax.config_host.start.....]')
        
        if os.path.exists(user_host_file):
            user_host_obj=open(user_host_file)
            user_host_list=user_host_obj.readlines()
            user_host_obj.close()
            
            win_host_file=r'C:\Windows\system32\drivers\etc\hosts'
            self.G_DEBUG_LOG.info('节点机的hosts文件路径：')
            self.G_DEBUG_LOG.info(win_host_file)
            win_host_obj=open(win_host_file,'a+')
            win_host_list=win_host_obj.readlines()
            for lines in user_host_list:
                if lines not in win_host_list:
                    win_host_obj.writelines('\n'+lines)
                    self.G_DEBUG_LOG.info('Add mapPath Success!')

            win_host_obj.close()
        self.G_DEBUG_LOG.info('[RenderMax.config_host.end.....]')        
        
    def get_light_cache_frame(self):
        self.G_DEBUG_LOG.info('[RenderMax.get_light_cache_frame.start....]')
        light_cache_frame=None
        if 'gi' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['gi']=='1':
            self.G_DEBUG_LOG.info('[RenderMax.get_light_cache_frame.start1....]')
            if 'light_cache_mode' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['light_cache_mode']=='1':
                if 'gi_frames' in self.G_TASK_JSON_DICT['scene_info_render']['renderer']:
                    self.G_DEBUG_LOG.info('[RenderMax.get_light_cache_frame.start2....]')
                    light_cache_frame=self.G_TASK_JSON_DICT['scene_info_render']['renderer']['gi_frames']
                else:
                    self.G_DEBUG_LOG.info('[RenderMax.get_light_cache_frame.start3....]')
                    light_cache_frame=self.G_TASK_JSON_DICT['scene_info_render']['common']['frames']
        self.G_DEBUG_LOG.info('[RenderMax.get_light_cache_frame.end....]')
        self.G_DEBUG_LOG.info('light_cache_frame:')    
        self.G_DEBUG_LOG.info(light_cache_frame)   
        return light_cache_frame        

    def get_render_frame(self):
        render_frame=self.G_CG_FRAMES
        if self.G_KG=='100':#inc
            if self.G_ACTION == 'RenderPhoton':
                if 'gi_frames' in self.G_TASK_JSON_DICT['scene_info_render']['renderer']:
                    render_frame=self.G_TASK_JSON_DICT['scene_info_render']['renderer']['gi_frames']
                else:
                    render_frame=self.G_TASK_JSON_DICT['scene_info_render']['common']['frames']
        elif self.G_KG=='101':#animation
            if self.G_ACTION == 'RenderPhoton':
                light_cache_frame=self.get_light_cache_frame()
                if light_cache_frame!=None:
                    render_frame=light_cache_frame
        elif self.G_KG=='102':#fast inc
            if self.G_ACTION == 'RenderPhoton':
                light_cache_frame=self.get_light_cache_frame()
                if light_cache_frame!=None:
                    render_frame=light_cache_frame
        # else:
            # light_cache_frame=self.get_light_cache_frame()
            # if light_cache_frame!=None:
                # render_frame=light_cache_frame
        return render_frame
    
    def get_render_cmd(self,task_ms_file):
    
        max_exe='"C:/Program Files/Autodesk/'+ self.G_CG_VERSION+'/3dsmax.exe"'
        render_cmd = max_exe+' -silent  -ma -mxs "filein \\"'+task_ms_file+'\\";renderRun() "'
        
        plugin_dict = self.G_CG_CONFIG_DICT['plugins']
        stand_vray_list=[]
        stand_vray_list.append('3ds Max 2016_vray3.30.05')
        stand_vray_list.append('3ds Max 2015_vray3.30.05')
        stand_vray_list.append('3ds Max 2014_vray3.30.05')
        stand_vray_list.append('3ds Max 2016_vray3.40.01')
        stand_vray_list.append('3ds Max 2015_vray3.40.01')
        stand_vray_list.append('3ds Max 2014_vray3.40.01')
        stand_vray_list.append('3ds Max 2017_vray3.40.01')
        stand_vray_list.append('3ds Max 2014_vray0000')
        stand_vray_list.append('3ds Max 2015_vray0000')
        stand_vray_list.append('3ds Max 2017_vray0000')
        renderer=''
        if 'vray' in plugin_dict:
            renderer='vray'+plugin_dict['vray']
        stand_vray_str=self.G_CG_VERSION+'_'+renderer
        if stand_vray_str in stand_vray_list:
            render_cmd = max_exe+' -ma -mxs "filein \\"'+task_ms_file+'\\";renderRun() "'
            
        if self.MAX_CMD_RENDER==True:
            if self.G_CHANNEL == '1' or self.G_CHANNEL == '2':  #web
                obase = self.G_TASK_JSON_DICT['scene_info_render']['common']['output_file_basename']
                otype = self.G_TASK_JSON_DICT['scene_info_render']['common']['output_file_type']
                cmd_render_output=obase+'.'+otype
                # if self.G_TASK_JSON_DICT['scene_info_render']['common'].has_key('renderable_camera'):
                    # cmd_render_cam = self.G_TASK_JSON_DICT['scene_info_render']['common']['renderable_camera']  #list
                if 'width' in self.G_TASK_JSON_DICT['scene_info']['common']:
                    cmd_render_width = self.G_TASK_JSON_DICT['scene_info']['common']['width']
                if 'height' in self.G_TASK_JSON_DICT['scene_info']['common']:
                    cmd_render_height = self.G_TASK_JSON_DICT['scene_info']['common']['height']
            # else:
                # if self.RENDER_CFG_PARSER.has_option('renderSettings','output'):
                    # cmd_render_output = self.RENDER_CFG_PARSER.get('renderSettings','output')
                # if self.RENDER_CFG_PARSER.has_option('renderSettings','renderableCamera'):
                    # cmd_render_cam = self.RENDER_CFG_PARSER.get('renderSettings','renderableCamera')
                # if self.RENDER_CFG_PARSER.has_option('renderSettings','width'):
                    # cmd_render_width = self.RENDER_CFG_PARSER.get('renderSettings','width')
                # if self.RENDER_CFG_PARSER.has_option('renderSettings','height'):
                    # cmdRenderheight = self.RENDER_CFG_PARSER.get('renderSettings','height')
            if self.G_ACTION == 'RenderPhoton':
                if 'gi_width' in self.G_TASK_JSON_DICT['scene_info_render']['renderer']:
                    cmd_render_height = self.G_TASK_JSON_DICT['scene_info_render']['renderer']['gi_width']
                if 'gi_height' in self.G_TASK_JSON_DICT['scene_info_render']['renderer']:
                    cmd_render_height = self.G_TASK_JSON_DICT['scene_info_render']['renderer']['gi_height']
            
            max_exe='"C:/Program Files/Autodesk/'+ self.G_CG_VERSION+'/3dsmaxcmd.exe"'
            render_cmd=max_exe+' -start:'+self.G_CG_START_FRAME+' -end:'+self.G_CG_END_FRAME+' -nthFrame:'+self.G_CG_BY_FRAME+' -o:"'+self.G_WORK_RENDER_TASK_OUTPUT_XXX+'/'+cmd_render_output+'" -camera:"'+self.G_CG_OPTION+'" -w:'+cmd_render_width+' -h:'+cmd_render_height+' -continueOnError '
            
            if self.G_ACTION == 'RenderPhoton':
                max_file_photon = self.MAX_FILE[:-4] + '_photon' + self.MAX_FILE[-4:]
                render_cmd=render_cmd+' "'+max_file_photon.replace('\\','/')+'"'
            else:            
                render_cmd=render_cmd+' "'+self.MAX_FILE.replace('\\','/')+'"'
        
        return render_cmd
    

    def rename_photon_file(self):
        #rename photon file,add serial number
        if self.MAX_CMD_RENDER==True:
            if self.G_ACTION == 'RenderPhoton':
                if self.G_KG=='102':  #fast inc
                    render_output = self.G_WORK_RENDER_TASK_OUTPUT_XXX
                    if os.path.exists(render_output):
                        render_output_list = os.listdir(render_output)
                        for file_basename in render_output_list:
                            if file_basename.endswith(r'irrmap.vrmap'):
                                # serial = self.G_JOB_NAME[6:]  #photon0000
                                length = len(self.G_CG_START_FRAME)
                                if length >= 4:
                                    serial = self.G_CG_START_FRAME
                                else:
                                    serial = '0'*(4-length) + self.G_CG_START_FRAME
                                file_newname = file_basename[:-6] + serial + file_basename[-6:]
                                try:
                                    os.rename(os.path.join(render_output,file_basename),os.path.join(render_output,file_newname))
                                except Exception as e:
                                    print('rename failed')
                                    print(e)
    
    def socket_send(self,final_data):
        try:
            self.client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(self.ADDR)
            self.client.send(final_data.encode('utf8'))
            recv_data=self.client.recv(self.BUFSIZ)
            self.G_DEBUG_LOG.info('socket send result '+self.HOST+'_____'+recv_data.decode('utf8'))
            if recv_data!=None and recv_data.endswith(b'success'):
                return True
            else:
                return False
        except Exception as e:
            self.G_DEBUG_LOG.info ('[err] connect socket exeception')
            self.G_DEBUG_LOG.info (e)
            return False
            
        
    def start_grab(self):
    
        self.G_DEBUG_LOG.info ('-------start grab------')
        
        grab_rate='300'
        grab_folder_local=os.path.join(self.G_WORK_RENDER_TASK,'grab').replace('\\','/')
        grab_folder_server=self.G_GRAB_PATH
        
        start_socket='rdf1grab|'+grab_rate+'|'+grab_folder_local+'|'+grab_folder_server+'|'+self.G_MUNU_ID+'_'+self.G_JOB_ID+'|'+self.G_NODE_NAME
        
        self.G_DEBUG_LOG.info ('SOCKET_DATA___'+start_socket)
        start_socket_len=len(start_socket)
        start_socket_len_hex=hex(start_socket_len)
        print(str(start_socket_len)+'>>'+str(start_socket_len_hex))
        start_socket_len_hex_str=str(start_socket_len_hex)[2:].zfill(8)
        final_data=start_socket_len_hex_str+start_socket
        self.G_DEBUG_LOG.info('MSG______'+self.HOST+':'+str(self.PORT)+'____'+final_data)
        self.socket_send(final_data)
        
    def stop_grab(self):
        stop_socket='rdf1stop'
        stop_socket_len=len(stop_socket)
        stop_socket_len_hex=hex(stop_socket_len)
        print(str(stop_socket_len)+'>>'+str(stop_socket_len_hex))
        stop_socket_len_hex_str=str(stop_socket_len_hex)[2:].zfill(8)
        final_data=stop_socket_len_hex_str+stop_socket
        self.G_DEBUG_LOG.info('MSG______'+self.HOST+':'+str(self.PORT)+'____'+final_data)
        self.socket_send(final_data)
    
    def get_max_vray_log(self):
        if self.MAX_VRAY_DISTRIBUTE:
            user_profile=os.environ["userprofile"]
            user_temp_file=os.environ["temp"]
            max_log_dir = user_profile+'\\AppData\\Local\\Autodesk\\3dsMax\\'+self.G_CG_VERSION.replace('3ds Max ','')+' - 64bit\\enu\\Network'
            max_log_dir = max_log_dir.replace('/','\\')
            max_log_path = os.path.join(max_log_dir,'Max.log').replace('/','\\')
            vray_log_dir = user_temp_file.replace('/','\\')
            vray_log_path = os.path.join(vray_log_dir,'vraylog.txt').replace('/','\\')
            
            node_ip_list = []
            for node_ip in self.G_SCHEDULER_CLUSTER_NODES.split(','):
                node_ip_list.append(node_ip)
            self.G_DEBUG_LOG.info(node_ip_list)   
            # nodeIP_num = len(node_ip_list)  #numbers of node ip
            if node_ip_list:
                for node_ip in node_ip_list:
                    max_log_node_remote = '\\\\' + node_ip + '\\' + max_log_path.replace(':','$')
                    vray_log_node_remote = '\\\\' + node_ip + '\\' + vray_log_path.replace(':','$')
                    max_log_to_master = os.path.join(self.G_LOG_WORK,self.G_TASK_ID,node_ip).replace('/','\\')
                    vray_log_to_master = os.path.join(self.G_LOG_WORK,self.G_TASK_ID,node_ip).replace('/','\\')
                    max_log_cmd=r'c:\fcopy\FastCopy.exe /cmd=force_copy /speed=full /force_close /no_confirm_stop /force_start "'+max_log_node_remote+'" /to="'+max_log_to_master+'"'
                    vray_log_cmd=r'c:\fcopy\FastCopy.exe /cmd=force_copy /speed=full /force_close /no_confirm_stop /force_start "'+vray_log_node_remote+'" /to="'+vray_log_to_master+'"'
                    CLASS_COMMON_UTIL.cmd(max_log_cmd,my_log=self.G_DEBUG_LOG,continue_on_error=True)
                    CLASS_COMMON_UTIL.cmd(vray_log_cmd,my_log=self.G_DEBUG_LOG,continue_on_error=True)
    
    def send_cmd_to_node(self,thread_name,local_ip,node_ip):
        self.G_DEBUG_LOG.info("%s begin: %s\n" % (thread_name,time.ctime(time.time())))
        
        from_addr = os.path.join(self.G_SCRIPT_POOL,'CG','Max','function','MaxDistribute.py')
        from_addr2 = os.path.join(self.G_SCRIPT_POOL,'CG','Max','function','MaxPlugin.py')
        to_addr = os.path.normpath('\\\\' + node_ip + '\\' + self.G_NODE_PY.replace(':','$'))
        
        copy_node_script_path='xcopy /Y /V /F "%s" "%s"' % (from_addr,to_addr)
        copy_node_script_path2='xcopy /Y /V /F "%s" "%s"' % (from_addr2,to_addr)
        if not os.path.exists(to_addr):
            os.makedirs(to_addr)
        CLASS_COMMON_UTIL.cmd(copy_node_script_path,my_log=self.G_DEBUG_LOG)
        CLASS_COMMON_UTIL.cmd(copy_node_script_path2,my_log=self.G_DEBUG_LOG)
        
        node_script_path = os.path.join(self.G_NODE_PY,'MaxDistribute.py')
        run_node_py_cmd='B:/tools/munu_agent_controller.exe %s 10001 "C:\\Python27\\python.exe %s "%s" "%s" "%s" "c:\\log""' % (node_ip,node_script_path,self.PLUGIN_PATH,self.G_TASK_ID,local_ip)
        CLASS_COMMON_UTIL.cmd(run_node_py_cmd,my_log=self.G_DEBUG_LOG)
        
        self.G_DEBUG_LOG.info("%s over: %s\n" % (thread_name,time.ctime(time.time())))
        
    def vray_distribute_node(self):
        if self.MAX_VRAY_DISTRIBUTE:
            self.G_DEBUG_LOG.info('---------TODO Vray dist---------') 
            ##get IP
            #local_ip = gethostbyname(gethostname())  #169.254.41.243
            ip_list = socket.gethostbyname_ex(socket.gethostname())  #('GA010', [], ['10.60.1.10', '169.254.41.243'])
            local_ip = ip_list[2][0]  #get localhost IP：10.60.1.10
            self.G_DEBUG_LOG.info('LOCAL IP:%s' % local_ip) 
                
            node_ip_list = []
            for node_ip in self.G_SCHEDULER_CLUSTER_NODES.split(','):
                node_ip_list.append(node_ip)
            self.G_DEBUG_LOG.info('NODE IP LIST:%s' % node_ip_list) 
            thread_list = []  #thread list
            ##send command with multi thread
            if node_ip_list:
                for node_ip in node_ip_list:
                    #thread.start_new_thread(send_cmd,("Thread-%s" % (node_ip),local_ip,node_ip))
                    t = threading.Thread(target=self.send_cmd_to_node,args=("Thread-%s" % (node_ip),local_ip,node_ip))
                    thread_list.append(t)
                for t in thread_list:
                    t.start()
                for t in thread_list:
                    t.join()
            else:
                self.G_DEBUG_LOG.info('node_ip_list is empty\n' ) 
            time.sleep(120)
    
    def vray_distribute_root(self):
        if self.MAX_VRAY_DISTRIBUTE:
            self.G_DEBUG_LOG.info('---------TODO Vray dist---------')
            content = ""  
            content_top_list = []  
            content_top = ""  
            content_bottom = ""  
            
            ##get IP
            #local_ip = gethostbyname(gethostname())  #169.254.41.243
            ip_list = gethostbyname_ex(gethostname())  #('GA010', [], ['10.60.1.10', '169.254.41.243'])
            local_ip = ip_list[2][0]  #get localhost IP：10.60.1.10
            self.G_DEBUG_LOG.info('LOCAL IP:%s' % local_ip) 
            
            node_ip_list = []
            for node_ip in self.G_SCHEDULER_CLUSTER_NODES.split(','):
                node_ip_list.append(node_ip)
            self.G_DEBUG_LOG.info('NODE IP LIST:%s' % node_ip_list) 
            node_ip_num = len(node_ip_list)  #numbers of node ip
            if node_ip_list:
                for node_ip in node_ip_list:
                    if self.G_CG_CONFIG_DICT['plugins']['vray'].startswith('3'):
                        content_top_list.append('%s 1 20204\n' % (node_ip))
                    else:
                        content_top_list.append('%s 1\n' % (node_ip))
                ####write cfg####
                for i in range(len(content_top_list)):
                    content_top = content_top + content_top_list[i]
                    
                if self.G_CG_CONFIG_DICT['plugins']['vray'].startswith('1'):
                    self.G_DEBUG_LOG.info('vray1\n') 
                    content_bottom = """restart_slaves 1
list_in_scene 1
"""
                elif self.G_CG_CONFIG_DICT['plugins']['vray'].startswith('2'):
                    self.G_DEBUG_LOG.info('vray2\n') 
                    content_bottom = """restart_slaves 1
list_in_scene 1
max_servers %s
""" % (node_ip_num)
                elif self.G_CG_CONFIG_DICT['plugins']['vray'].startswith('3'):
                    self.G_DEBUG_LOG.info('vray3\n') 
                    content_bottom = """restart_slaves 1
list_in_scene 1
max_servers %s
use_local_machine 1
transfer_missing_assets 1
use_cached_assets 1
cache_limit_type 2
cache_limit 100.000000
""" % (node_ip_num)
                elif self.G_CG_CONFIG_DICT['plugins']['vray'].startswith('0'):
                    self.G_DEBUG_LOG.info('vray0000\n') 
                    content_bottom = """restart_slaves 1
list_in_scene 1
max_servers %s
use_local_machine 1
transfer_missing_assets 1
use_cached_assets 1
cache_limit_type 2
cache_limit 100.000000
""" % (node_ip_num)
                else:
                    CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG,'vray version error\n')
                content = content_top.strip() + '\n' + content_bottom.strip()
                self.G_DEBUG_LOG.info(content)
                configure_tmp_path = 'D:\\work\\render\\%s\\cfg\\vray_dr.cfg' % (self.G_TASK_ID)  #tmp path
                with open(configure_tmp_path, 'w') as f:
                    f.write(content)
                version_year = self.G_CG_VERSION[-4:]
                if int(version_year) < 2013:
                    configure_path = 'C:\\users\\enfuzion\\AppData\\Local\\Autodesk\\3dsmax\\%s - 64bit\\ENU\\plugcfg' % (version_year)
                else:
                    configure_path = 'C:\\Users\\enfuzion\\AppData\\Local\\Autodesk\\3dsMax\\%s - 64bit\\ENU\\en-US\\plugcfg' % (version_year)
                self.G_DEBUG_LOG.info(configure_path)
                file_path = os.path.join(configure_path,"vray_dr.cfg")
                self.G_DEBUG_LOG.info(file_path)
                if not os.path.exists(configure_path):
                    os.makedirs(configure_path)
                shutil.copy(configure_tmp_path,file_path)                    
                #os.system("copy %s %s" % (configure_tmp_path,file_path))
                #cmdcp=subprocess.Popen("copy %s %s" % (configure_tmp_path,configure_path),stdin = subprocess.PIPE,stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = True)
                if os.path.isfile(file_path):
                    self.G_DEBUG_LOG.info('Success\n')
            else:
                self.G_DEBUG_LOG.info('node_ip_list is empty\n')
            time.sleep(120)
    

    def sort_pic_list(self, pic_list):
        """ Returns list.
            功能：将缩略图列表重新排序。
            这将影响平台展示给客户的缩略图顺序，
            默认对列表不做任何修改操作，如需则在各自软件的脚本中重写该方法
            如：max重写该方法实现了将主图缩略图排在列表最前面，方便平台展示给客户（第一张即为主图）
        """
        self.G_DEBUG_LOG.info('[RenderMax.sort_pic_list.start.....]')  # test chen
        output_file_basename=self.G_TASK_JSON_DICT['scene_info_render']['common']['output_file_basename']
        for index, element in enumerate(pic_list):
            if output_file_basename in element:
                pic_list.insert(0, pic_list.pop(index))
        return pic_list
        
        
        
        
        
        
        