#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import time
import subprocess
import sys
import codecs
import configparser
import shutil
from Max import Max

from CommonUtil import RBCommon as CLASS_COMMON_UTIL

class MergeMax(Max):

    '''
        初始化构造函数
    '''
    def __init__(self,**param_dict):
        Max.__init__(self,**param_dict)
        self.temp_mark=0
        
        ## clear directory
        if os.path.exists(self.G_WORK_RENDER_TASK_OUTPUT):
            try:
                shutil.rmtree(self.G_WORK_RENDER_TASK_OUTPUT)
            except Exception as e:
                print('[err]delete directory failed : %s' % self.G_WORK_RENDER_TASK_OUTPUT)
                print(e)
        
        photon_directory = os.path.join(self.G_WORK_RENDER_TASK,'photon')
        if os.path.exists(photon_directory):
            try:
                shutil.rmtree(photon_directory)
            except Exception as e:
                print('[err]delete directory failed : %s' % photon_directory)
                print(e)
            
        if not os.path.exists(self.G_WORK_RENDER_TASK_OUTPUT):
            os.makedirs(self.G_WORK_RENDER_TASK_OUTPUT)
        if not os.path.exists(photon_directory):
            os.makedirs(photon_directory)
                
        print('Merge init')        
                
    '''
        合并光子入口
    '''
    def RB_RENDER(self):
        self.format_log('拷贝小光子开始','start')
        
        # outputFiles=False
        # if self.G_TASK_JSON_DICT['miscellaneous'].has_key('only_photon'):
            # if self.G_TASK_JSON_DICT['miscellaneous']['only_photon'] == '1':
                # pass
                # self.G_OSS_OUTPUT_DIR=self.RvOssOutputRoot()+'d/output/'+self.RvUnionUserIdAndTaskId()
        # self.G_FEE_LOG.info('startTime='+str(int(time.time())))
        # self.G_FEE_LOG.info('endTime='+str(int(time.time())))
        # self.G_DEBUG_LOG.info('startTime='+str(int(time.time())))
        # self.G_DEBUG_LOG.info('endTime='+str(int(time.time())))
        # self.G_KAFKA_MESSAGE_DICT['start_time']=str(int(time.time()))
        self.G_FEE_PARSER.set('render','start_time',str(int(time.time())))
        
        # 调用合并光子方法
        #photon_path='A:/photon/'+self.G_TASK_ID+'/'
        photon_path=os.path.join(self.G_WORK_RENDER_TASK,'photon','source')
        photon_user_path=os.path.join(self.G_TEMP_PATH,'photon')
        if self.G_MULTI_CAMERA:
            # photon_path=os.path.join(self.G_WORK_RENDER_TASK,'photon','source',self.G_CG_OPTION)
            photon_user_path=os.path.join(self.G_TEMP_PATH,'photon',self.G_SMALL_TASK_ID)
        # photon_user_path2=os.path.join(self.G_INPUT_PROJECT_PATH,'photon',self.G_TASK_ID)        
        
        self.G_DEBUG_LOG.info(photon_path)
        self.G_DEBUG_LOG.info(photon_user_path)
        # self.G_DEBUG_LOG.info(photon_user_path2)
        
        # if os.path.exists(photon_user_path2):
            # copy_vrmap_cmd=r'c:\fcopy\FastCopy.exe /speed=full /force_close /no_confirm_stop /force_start "'+os.path.join(photon_user_path2,r'*.vrmap')+'" /to="'+photon_path+'"'
            # CLASS_COMMON_UTIL.cmd(copy_vrmap_cmd,my_log=self.G_DEBUG_LOG)
            
        if os.path.exists(photon_user_path):            
            #photon_user_path=self.argsmap['inputDataPath']+self.G_USERID_PARENT+"/"+self.G_USERID+"/photon/"+self.G_TASK_ID+"/*.vrmap"
            copy_vrmap_cmd=r'c:\fcopy\FastCopy.exe /speed=full /force_close /no_confirm_stop /force_start "'+photon_user_path+'\\*.vrmap" /to="'+photon_path+'"'
            CLASS_COMMON_UTIL.cmd(copy_vrmap_cmd,my_log=self.G_DEBUG_LOG)
            # CLASS_COMMON_UTIL.cmd_python3(copy_vrmap_cmd,my_log=self.G_DEBUG_LOG)
            
        self.G_DEBUG_LOG.info('photon_path ='+str(photon_path))
        self.show_path_file(photon_path)
        
        self.format_log('拷贝小光子结束','end')
        
        #-----------------------------------------merge photon-----------------------------------------------
        self.G_DEBUG_LOG.info('[Merge.RB_RENDER start]')
        self.merge_photon(photon_path)
        # self.G_KAFKA_MESSAGE_DICT['end_time']=str(int(time.time()))
        self.G_FEE_PARSER.set('render','end_time',str(int(time.time())))
        # self.G_DEBUG_LOG.info.info(framenum['status'])
        # outputFiles=self.getDirFileSize(self.G_WORK_RENDER_TASK_OUTPUT)
        # self.G_DEBUG_LOG.info.info('outputFiles ='+str(outputFiles))
        # if outputFiles == True:
        # 	if framenum['status'] != '':
        # 		self.G_FEE_LOG.info('status='+framenum['status'])
        # 		self.G_RENDER_STATUS=False
        # 	else:
        # 		self.G_FEE_LOG.info('status=Success')
        # 		self.G_RENDER_STATUS=True
        # else:
        # 	self.G_DEBUG_LOG.info.info('Render Failed ,Begin writeFee to mark Failed')
        # 	self.G_FEE_LOG.info('status=Failed')
        # 	self.G_RENDER_STATUS=False
        # self.G_DEBUG_LOG.info.info('Merge.RB_RENDER end')
        
    #def RBrenderConfig(self):
    #    self.G_DEBUG_LOG.info('[Merge.RBrenderConfig.start.....]')
    #    self.G_PLATFORM=self.argsmap['platform']
    #    self.G_KG=self.argsmap['kg']
    #    self.G_PATH_SMALL=self.argsmap['smallPath']
    #    self.G_SINGLE_FRAME_CHECK=self.argsmap['singleFrameCheck']
    #    self.G_PATH_COST=self.argsmap['pathCost']
    #    self.G_FIRST_FRAME=self.argsmap['firstFrame']
    #
    #    self.G_ZONE=self.argsmap['zone']
    #    self.G_PATH_USER_OUTPUT=self.argsmap['output']
    #    self.G_CG_VERSION=self.argsmap['cgv']
    #    self.G_CG_RENDER_VERSION=self.argsmap['renderVersion']
    #    self.G_DEBUG_LOG.info('[Merge.RBrenderConfig.end.....]')
    
    #'''
    #    调用子进程合成光子
    #'''
    #def RVCmd(self,cmd):
    #    self.G_DEBUG_LOG.info('cmd='+cmd)
    #    # self.G_RENDERCMD_LOGGER.info('cmd='+cmd)
    #    cmdp=subprocess.Popen(cmd,shell = True,stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    #    while True:
    #        buff = cmdp.stdout.readline()
    #        if buff == '' and cmdp.poll() != None:
    #            break
    #        # self.G_RENDERCMD_LOGGER.info(buff)
    #        # self.G_DEBUG_LOG.info.info(buff)
    #    resultCode = cmdp.returncode
    #    self.G_DEBUG_LOG.info('resultCode='+str(resultCode))
        
    '''	
        合成光子函数，参数说明：path光子所在路径
    '''
    def merge_photon(self,path):
        self.temp_mark=self.temp_mark+1
        # self.G_DEBUG_LOG.info('photon path tempMark='+str(self.temp_mark))
        # self.temp=os.path.join(self.G_WORK_RENDER_TASK,'photon','temp')
        # self.G_DEBUG_LOG.info('photon path temp='+self.temp)
        # self.RvMakeDirs(self.temp)
        # if not os.path.exists(self.temp):
            # os.makedirs(self.temp)
        # self.output=self.RvMakeDirs(self.temp+str(self.temp_mark))
        # self.RvMakeDirs(self.output)
        photon_output = os.path.join(self.G_WORK_RENDER_TASK,'photon','temp'+str(self.temp_mark))
        # if self.G_MULTI_CAMERA:
            # photon_output = os.path.join(self.G_WORK_RENDER_TASK,'photon',self.G_CG_OPTION,'temp'+str(self.temp_mark))
        if not os.path.exists(photon_output):
            os.makedirs(photon_output)
        self.G_DEBUG_LOG.info('photon output path='+photon_output)
        
        render_output=self.G_WORK_RENDER_TASK_OUTPUT
        self.G_DEBUG_LOG.info('render output path='+render_output)
        
        # oldRenderer=self.argsmap['render']
        # self.G_DEBUG_LOG.info('oldRenderer='+oldRenderer)
        # standRender=oldRenderer.lower().replace("v-ray", "vray").replace("v_ray", "vray").replace("_adv__", "").replace("_adv_", "").replace("_",".").replace("demo ", "").replace(" ", "")
        # self.G_DEBUG_LOG.info('standRender='+standRender)
        if 'plugins' in self.G_CG_CONFIG_DICT and 'vray' in self.G_CG_CONFIG_DICT['plugins']:
            stand_render = 'vray'+self.G_CG_CONFIG_DICT['plugins']['vray']        
            # vray='b:/plugins/max/imv/'+stand_render+'/imapviewer.exe'
            vray = os.path.join(self.G_MAX_B,'imv',stand_render,'imapviewer.exe')
            self.G_DEBUG_LOG.info('vray='+vray)
        
            file_array=self.filter_photon_file(path)
            file_array.sort()
            self.G_DEBUG_LOG.info(file_array)
            number=len(file_array)
            self.G_DEBUG_LOG.info('number='+str(number))
            # print 'number='+str(number)
            if number<=10:
                cmd='"'+vray+'"'
                for p in file_array:
                    cmd=cmd+' -load '+path+'/'+p
                    pass
                cmd=cmd+' -save '+render_output+'/'+self.G_SMALL_TASK_ID+'_irrmap.vrmap -nodisplay '
                # self.RVCmd(cmd)	
                CLASS_COMMON_UTIL.cmd(cmd,my_log=self.G_DEBUG_LOG)
                # CLASS_COMMON_UTIL.cmd_python3(cmd,my_log=self.G_DEBUG_LOG)
                self.show_path_file(render_output)
                pass
            elif number>10:
                j=0
                k=0
                while j<number:
                    k=k+1
                    i=0
                    cmd='"'+vray+'"'
                    while i<10:
                        
                        if j==number:
                            break
                        # print 'file_array['+str(j)+']='+file_array[j]
                        self.G_DEBUG_LOG.info('file_array['+str(j)+']='+file_array[j])
                        cmd=cmd+' -load '+path+'/'+file_array[j]
                        i=i+1
                        j=j+1
                        pass
                    cmd=cmd+' -save '+photon_output+'/'+str(k)+'.vrmap '+' -nodisplay'
                    # self.RVCmd(cmd)
                    CLASS_COMMON_UTIL.cmd(cmd,my_log=self.G_DEBUG_LOG)
                    # CLASS_COMMON_UTIL.cmd_python3(cmd,my_log=self.G_DEBUG_LOG)
                # print 'j='+str(j)
                self.G_DEBUG_LOG.info('j='+str(j))
                self.show_path_file(photon_output)
                self.merge_photon(photon_output)
            pass
    '''
        过滤tga vrlmap扩展名的文件，这些文件不进行合并光子
    '''
    def filter_photon_file(self,path):
        file_array=os.listdir(path)
        tempArray=[]
        for nameStr in file_array:
            
            if nameStr.endswith('.vrmap'):
                self.G_DEBUG_LOG.info('nameStr='+nameStr)
                tempArray.append(nameStr)
        return tempArray
    def show_path_file(self,path):
        for p in os.listdir(path):
            self.G_DEBUG_LOG.info('file='+path+'/'+p)
            # self.G_RENDERCMD_LOGGER.info('file='+path+'/'+p)
    #'''
    #    上传渲染结果和日志
    #'''
    #def RBresultAction(self):
    #    self.G_DEBUG_LOG.info('[BASE.RBresultAction.start.....]')
    #    #RB_small
    #    if not os.path.exists(self.G_PATH_SMALL):
    #        os.makedirs(self.G_PATH_SMALL)
    #    frameCheck = os.path.join(self.G_POOL,'tools',self.G_SINGLE_FRAME_CHECK)
    #    cmd1='c:\\fcopy\\FastCopy.exe  /speed=full /force_close  /no_confirm_stop /force_start "' +self.G_WORK_RENDER_TASK_OUTPUT.replace('/','\\') +'" /to="'+self.G_OUTPUT_USER_PATH+'"'
    #    cmd2='"' +frameCheck + '" "' + self.G_WORK_RENDER_TASK_OUTPUT + '" "'+ self.G_OUTPUT_USER_PATH+'"'
    #    cmd3='c:\\fcopy\\FastCopy.exe /cmd=move /speed=full /force_close  /no_confirm_stop /force_start "' +self.G_WORK_RENDER_TASK_OUTPUT.replace('/','\\')+'\\*.*" /to="'+self.G_RENDER_WORK_OUTPUTBAK.replace('/','\\')+'"'
    #
    #    feeLogFile=self.G_USERID+'-'+self.G_TASK_ID+'-'+self.G_JOB_NAME+'.txt'
    #    feeTxt=os.path.join(self.G_WORK_RENDER_TASK,feeLogFile)
    #    cmd4='xcopy /y /f "'+feeTxt+'" "'+self.G_PATH_COST+'/" '
    #    cmd1=cmd1.encode(sys.getfilesystemencoding())
    #    cmd2=cmd2.encode(sys.getfilesystemencoding())
    #    self.RBcmd(cmd1)
    #    self.RBcmd(cmd2)
    #    self.RBcmd(cmd3)
    #    self.RBcmd(cmd4)
    #    self.G_DEBUG_LOG.info('[BASE.RBresultAction.end.....]')
    '''
        上传渲染结果和日志
    ''' 
    def RB_HAN_RESULT(self):#8
        self.G_DEBUG_LOG.info('[BASE.RB_HAN_RESULT.start.....]')
        # 只渲染光子
        if self.G_ONLY_PHOTON == 'true':
            self.result_action()
        else:
            self.result_action_photon()
        self.G_DEBUG_LOG.info('[BASE.RB_HAN_RESULT.end.....]')
            
            
        #if self.argsmap.has_key('onlyphoton'):
        #    if self.argsmap['onlyphoton'] in 'true':
        #        self.result_action()
        #        pass
        #    else:
        #        if self.argsmap['currentTask'] in 'photon':
        #            # uploadPath='A:/photon/'+self.G_TASK_ID+'/'
        #            uploadPath=self.argsmap['inputDataPath']+self.G_USERID_PARENT+"/"+self.G_USERID+'/'+self.RENDER_CFG_PARSER.get('common','projectSymbol')+"/max/photon/"+self.G_TASK_ID+"/"
        #            if self.isScriptUpdateOk(20160900):
        #                uploadPath=self.argsmap['inputDataPath']+self.G_USERID_PARENT+"/"+self.G_USERID+"/photon/"+self.G_TASK_ID+"/"
        #            self.G_DEBUG_LOG.info(uploadPath.replace('/','\\'))
        #            uploadCmd='c:\\fcopy\\FastCopy.exe /cmd=move /speed=full /force_close  /no_confirm_stop /force_start "' +self.G_WORK_RENDER_TASK_OUTPUT.replace('/','\\')+'\*.*" /to="'+uploadPath.replace('/','\\')+'"'
        #            self.G_DEBUG_LOG.info(uploadCmd)
        #            feeLogFile=self.G_USERID+'-'+self.G_TASK_ID+'-'+self.G_JOB_NAME+'.txt'
        #            feeTxt=os.path.join(self.G_WORK_RENDER_TASK,feeLogFile)
        #            cmd4='xcopy /y /f "'+feeTxt+'" "'+self.G_PATH_COST+'/" '
        #            self.RvMakeDirs(uploadPath)
        #            self.RBcmd(uploadCmd)
        #            self.RBcmd(cmd4)
        #            pass
        #        else:
        #            self.result_action()
        #            pass
        #        pass
        #else:
        #    self.result_action()
        #    pass
        #self.G_DEBUG_LOG.info('[BASE.RB_HAN_RESULT.end.....]')
        
    def result_action_photon(self):
        # if self.G_ONLY_PHOTON == '1':
            # upload_path = self.G_OUTPUT_USER_PATH
        # else:
        upload_path = os.path.join(self.G_INPUT_PROJECT_PATH,'photon',self.G_SMALL_TASK_ID)     
        # if self.G_MULTI_CAMERA:
            # upload_path = os.path.join(self.G_INPUT_PROJECT_PATH,'photon',self.G_SMALL_TASK_ID)
            # if self.G_KG == '102':#fast inc map
                # upload_path = os.path.join(self.G_TEMP_PATH,'photon')
        cmd1='c:\\fcopy\\FastCopy.exe  /speed=full /force_close  /no_confirm_stop /force_start "' +self.G_WORK_RENDER_TASK_OUTPUT.replace('/','\\') +'" /to="'+upload_path+'"'
        # cmd2='"' +frame_check + '" "' + self.G_WORK_RENDER_TASK_OUTPUT + '" "'+ upload_path.rstrip()+'"'
        cmd3='c:\\fcopy\\FastCopy.exe /cmd=move /speed=full /force_close  /no_confirm_stop /force_start "' +self.G_WORK_RENDER_TASK_OUTPUT.replace('/','\\')+'\\*.*" /to="'+self.G_WORK_RENDER_TASK_OUTPUTBAK.replace('/','\\')+'"'
        
        CLASS_COMMON_UTIL.cmd(cmd1,my_log=self.G_DEBUG_LOG,try_count=3)
        # CLASS_COMMON_UTIL.cmd_python3(cmd1,my_log = self.G_DEBUG_LOG)
        # try:
            # self.check_result()
        # except Exception, e:
            # print '[check_result.err]'
            # print e
        # CLASS_COMMON_UTIL.cmd(cmd2,my_log=self.G_DEBUG_LOG)
        CLASS_COMMON_UTIL.cmd(cmd3,my_log=self.G_DEBUG_LOG,try_count=3,continue_on_error=True)
        
    #def readRenderCfg(self):
    #    self.G_DEBUG_LOG.info('[Max.readRenderCfg.start.....]')
    #    renderCfg=os.path.join(self.G_WORK_RENDER_TASK_CFG,'render.cfg')
    #    self.RENDER_CFG_PARSER = ConfigParser.ConfigParser()
    #    #self.RENDER_CFG_PARSER.read(renderCfg)
    #    try:
    #        self.G_DEBUG_LOG.info('read render cfg utf16')
    #        self.RENDER_CFG_PARSER.readfp(codecs.open(renderCfg, "r", "UTF-16"))
    #    except Exception, e:
    #        try:
    #            self.G_DEBUG_LOG.info('read render cfg utf8')
    #            self.RENDER_CFG_PARSER.readfp(codecs.open(renderCfg, "r", "UTF-8"))
    #        except Exception, e:
    #            self.G_DEBUG_LOG.info(e)
    #            self.G_DEBUG_LOG.info('read render cfg default')
    #            self.RENDER_CFG_PARSER.readfp(codecs.open(renderCfg, "r"))
    #    
    #    
    #    
    #    
    #    self.G_DEBUG_LOG.info('[Max.readRenderCfg.end.....]')
        
    #def netPath(self):
    #    # mountFrom='{"Z:":"//192.168.0.94/d"}'
    #    print '----------------net----------------'
    #    self.G_DEBUG_LOG.info('[path config]') 
    #    inputDataPath=self.argsmap['inputDataPath']
    #    
    #    cleanMountFrom='try3 net use * /del /y'
    #    self.G_DEBUG_LOG.info(cleanMountFrom)
    #    self.RBcmd(cleanMountFrom)
    #    
    #    self.delSubst()
    #    
    #    pluginPath=self.argsmap['pluginPath']
    #    if not os.path.exists(r'B:\plugins'):
    #        cmd='try3 net use B: '+pluginPath.replace('/','\\').replace("10.60.100.151","10.60.100.152")
    #        self.G_DEBUG_LOG.info(cmd) 
    #        self.RBcmd(cmd)
    #    
    #    projectPath=os.path.join(inputDataPath,self.G_USERID_PARENT,self.G_USERID,self.RENDER_CFG_PARSER.get('common','projectSymbol'),'max')
    #    projectPath=projectPath.replace('/','\\')
    #    self.G_DEBUG_LOG.info(projectPath)
    #    if not os.path.exists(projectPath):
    #        os.makedirs(projectPath)
    #        
    #    if not self.isScriptUpdateOk(20160900):
    #        cmd='try3 net use A: '+projectPath
    #        #nono_20160906___________self.G_DEBUG_LOG.info(cmd) 
    #        #nono_20160906___________self.RBcmd(cmd)
    #    
    #    
    '''
        get dir size
    '''
    def getDirFileSize(self,path):
        list_dirs = os.walk(path)
        fileNum=len(os.listdir(path))
        fileSizeSum=0
        fileSizeArray=[]
        flag=True
        for root, dirs, files in list_dirs:   
            for name in files:
                absolutePathFiles=os.path.join(root,name)
                size=os.path.getsize(absolutePathFiles)
                fileSizeSum=fileSizeSum+size
                fileSizeArray.append(size)
                self.G_DEBUG_LOG.info("filename="+absolutePathFiles)
                self.G_DEBUG_LOG.info("filesize="+str(size)) 
        self.G_DEBUG_LOG.info("fileNum="+str(fileNum))
        self.G_DEBUG_LOG.info("fileSizeSum="+str(fileSizeSum))
        if len(fileSizeArray)<=0:
            flag=False
        else:
            for f in fileSizeArray:
                if float(f) <=0:
                    flag=False
                    break
                pass
        self.G_DEBUG_LOG.info("flag="+str(flag))
        return flag
    #def RBexecute(self):#total    
    #    self.RBBackupPy()
    #    self.RBinitLog()
    #    self.G_DEBUG_LOG.info('[BASE.RBexecute.start.....]')        
    #    self.RBprePy()
    #    self.RBmakeDir()
    #    self.RBcopyTempFile()
    #    self.readPyCfg()
    #    self.readRenderCfg()
    #    self.netPath()        
    #    self.CheckDisk()
    #    # self.RBreadCfg()
    #    #self.RBhanFile()
    #    self.RBrenderConfig()
    #    self.RBwriteConsumeTxt()
    #    self.RBrender()
    #    # self.RBconvertSmallPic()
    #    self.RBhanResult()
    #    self.RBpostPy()
    #    self.G_DEBUG_LOG.info('[BASE.RBexecute.end.....]')