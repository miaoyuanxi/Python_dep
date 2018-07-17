#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
import subprocess
import string
import time
import shutil
import threading
import time
import codecs
from CommonUtil import RBCommon as CLASS_COMMON_UTIL

class RBMaxUtil(object):

    @staticmethod
    def RBLog___abort(logStr,myLog=None):
        if myLog==None:
            print(logStr)
        else:
            myLog.info(logStr)
    
    @staticmethod
    def maxCmd___abort(cmdStr,myLog=None):#continueOnErr=true-->not exit ; continueOnErr=false--> exit 
        DogUtil.RBLog(cmdStr,myLog)
        cmdp=subprocess.Popen(cmdStr,shell = True,stdout = subprocess.PIPE, stderr = subprocess.STDOUT)        
        while True:
            buff = cmdp.stdout.readline()
            buff = buff.decode(sys.getfilesystemencoding())
            if buff == '' and cmdp.poll() != None:
                break   
            DogUtil.RBLog(buff,myLog)
            if '[End maxscript render]' in buff:
                try:
                    os.system('taskkill /F /IM 3dsmax.exe /T')
                except  Exception as e:
                    DogUtil.RBLog('taskkill 3dsmax.exe exeception')  
                    DogUtil.RBLog(e)  
                try:
                    os.system('taskkill /F /IM 3dsmaxcmd.exe /T')
                except  Exception as e:
                    DogUtil.RBLog('taskkill 3dsmaxcmd.exe exeception')  
                    DogUtil.RBLog(e)          
        resultCode = cmdp.returncode
        return resultCode
        
        
    @staticmethod
    def runCmd_______abort(cmd,myLog=None):
        # print('cmd='+cmd)
        cmdp=subprocess.Popen(cmd,shell = True,stdout = subprocess.PIPE, stderr = subprocess.STDOUT)        
        while True:
            buff = cmdp.stdout.readline()
            buff = buff.decode(sys.getfilesystemencoding())
            if buff == '' and cmdp.poll() != None:
                break   
            if myLog!=None :
                myLog.info(buff)
            # self.G_RENDERCMD_LOGGER.info(buff)
            # self.G_PROCESS_LOGGER.info(buff)          
        resultCode = cmdp.returncode
        return resultCode
        
        
        
        
    @staticmethod
    def restartWin(progressLog):
        progressLog.info('MaxLogDEBUG_restartWin')            
        try:
            os.system('shutdown /r /t 0')
        except  Exception as e:
            progressLog.info('MaxLogDEBUG_restartWin exeception')  
            progressLog.info(e)
            
    @staticmethod
    def killMax(progressLog):
        progressLog.info('MaxLogDEBUG_TASKKILL_3DSMAXCMD')            
        try:
            os.system('taskkill /F /IM 3dsmaxcmd.exe /T')
        except  Exception as e:
            progressLog.info('MaxLog2taskkill 3dsmaxcmd.exe exeception')  
            progressLog.info(e) 
        
        
        progressLog.info('MaxLogDEBUG_TASKKILL_3DSMAX')
        try:
            os.system('taskkill /F /IM 3dsmax.exe /T')
        except  Exception as e:
            progressLog.info('MaxLog2taskkill 3dsmax.exe exeception')  
            progressLog.info(e) 
            
    @staticmethod
    def checkProcess(procName):
        try:
            file_handle = os.popen('tasklist /FI "IMAGENAME eq ' + procName + '"')
            file_content = file_handle.read()
            if file_content.find(procName) > -1:
                return True
            else:
                return False
        except BaseException as e:
            print(str(e))
            return False  
        
    #kill 3dsmax.exe,3dsmaxcmd.exe,vrayspawner*.exe,powershell.exe
    @staticmethod
    def killMaxVray(progressLog):
        progressLog.info('[killMaxVray start]')
        try:
            os.system('taskkill /F /FI "IMAGENAME eq vrayspawner*" /T')
        except Exception as e:
            progressLog.info('kill vrayspawner*.exe exception')
            progressLog.info(e)
        try:
            os.system('taskkill /F /IM 3dsmaxcmd.exe /T')
        except Exception as e:
            progressLog.info('kill 3dsmaxcmd.exe exception') 
            progressLog.info(e)
        try:
            os.system('taskkill /F /IM 3dsmax.exe /T')
        except  Exception as e:
            progressLog.info('kill 3dsmax.exe exception') 
            progressLog.info(e)
        progressLog.info('[killMaxVray end]')
    
    @classmethod
    def kill_max(self,parent_id=None,my_log=None):
        CLASS_COMMON_UTIL.log_print(my_log,'parent_id='+str(parent_id))
        if parent_id==None:
            CLASS_COMMON_UTIL.log_print(my_log,'kill all 3dsmaxcmd')
            try:
                os.system('taskkill /F /IM 3dsmax.exe /T')
            except  Exception as e:
                CLASS_COMMON_UTIL.log_print(my_log,'taskkill 3dsmax.exe exeception')
                CLASS_COMMON_UTIL.log_print(my_log,e)
        else:
            cmd_str='wmic process where name="3dsmax.exe" get Caption,ParentProcessId,ProcessId'
            CLASS_COMMON_UTIL.log_print(my_log,cmd_str)
            cmdp=subprocess.Popen(cmd_str,shell = True,stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            while True:
                buff = cmdp.stdout.readline().strip()
                buff = buff.decode(sys.getfilesystemencoding())
                if buff == '' and cmdp.poll() != None:
                    break
                if buff!=None and buff!='' :
                    
                    CLASS_COMMON_UTIL.log_print(my_log,'max process info...')
                    CLASS_COMMON_UTIL.log_print(my_log,buff)
                        
                    try:
                        buffArr=buff.split()
                        CLASS_COMMON_UTIL.log_print(my_log,str(buffArr))
                        # if int(buffArr[1])==parent_id:
                        if buffArr[1]==str(parent_id):
                            CLASS_COMMON_UTIL.log_print(my_log,'kill...'+buff)
                            os.system("taskkill /f /pid %s" % (buffArr[2]))
                    except  Exception as e:
                        CLASS_COMMON_UTIL.log_print(my_log,'taskkill 3dsmax.exe exeception')
                        CLASS_COMMON_UTIL.log_print(my_log,e)
                
        try:
            os.system('taskkill /F /IM 3dsmaxcmd.exe /T')
        except  Exception as e:
            CLASS_COMMON_UTIL.log_print(my_log,'taskkill 3dsmaxcmd.exe exeception')
            CLASS_COMMON_UTIL.log_print(my_log,e)
        CLASS_COMMON_UTIL.log_print(my_log,'maxKill...end...\n')
        
    
    @classmethod
    def max_cmd_callback(self,my_popen,my_log):
    
        while my_popen.poll()==None:
            result_line = my_popen.stdout.readline().strip()
            result_line = result_line.decode(sys.getfilesystemencoding())
            if result_line=='' :
                continue
            CLASS_COMMON_UTIL.log_print(my_log,result_line)
            
            if '[_____KILL MAX_____]' in result_line:
                self.kill_max(my_popen.pid,my_log)
                CLASS_COMMON_UTIL.log_print(my_log,'\n\n-------------------------------------------End max program-------------------------------------------\n\n')
                break
            
    @classmethod
    def max_cmd____aobrt(self,cmd_str,my_log=None,continue_on_error=False,my_shell=False):#continueOnErr=true-->not exit ; continueOnErr=false--> exit 
        print(str(continue_on_error)+'--->>>'+str(my_shell))
        if my_log!=None:
            my_log.info(cmd_str)
            my_log.info("\n\n-------------------------------------------Start max program-------------------------------------\n\n")
        
        cmdp=subprocess.Popen(cmd_str,stdin = subprocess.PIPE,stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = my_shell)
        #cmdp.stdin.write('3/n')
        #cmdp.stdin.write('4/n')
        while True:
            resultLine = cmdp.stdout.readline().strip()
            resultLine = resultLine.decode(sys.getfilesystemencoding())
            if resultLine == '' and cmdp.poll()!=None:
                break
            if my_log!=None:    
                my_log.info(resultLine)
            
            if '[_____KILL MAX_____]' in resultLine:
                self.kill_max(cmdp.pid)
                if my_log!=None:
                    my_log.info("\n\n-------------------------------------------End max program-------------------------------------\n\n")
        resultStr = cmdp.stdout.read()
        resultStr = resultStr.decode(sys.getfilesystemencoding())
        resultCode = cmdp.returncode
        
        if my_log!=None:
            my_log.info('resultStr...'+resultStr)
            my_log.info('resultCode...'+str(resultCode))
        
        if not continue_on_error:
            if resultCode!=0:
                sys.exit(resultCode)
        return resultStr

    
class RBMaxLog(object):
    def __init__(self,task_id,cg_version,log_obj,log_work,action_id): 
              
            self.thread_stop = False
            self.RENDER_LOG=log_obj
            
            user_profile=os.environ["userprofile"]
            user_temp_file=os.environ["temp"]
            
            self.MAX_LOG=user_profile+'\\AppData\\Local\\Autodesk\\3dsMax\\'+cg_version.replace('3ds Max ','')+' - 64bit\\enu\\Network\\Max.log'
            self.VRAY_LOG=os.path.join(user_temp_file,'vraylog.txt').replace('\\','/')
            
            render_log_dir=os.path.join(log_work,task_id)
            # self.WORK_VRAY_LOG=os.path.join(render_log_dir,(action_id+'_vray2.txt'))
            # self.WORK_MAX_LOG=os.path.join(render_log_dir,(action_id+'_max2.txt'))
            self.WORK_NEW_RENDER_LOG=os.path.join(render_log_dir,(action_id+'_render.log'))
            
            self.RENDER_LOG.info('[MonitorLog]'+self.MAX_LOG)
            self.RENDER_LOG.info('[MonitorLog]'+self.VRAY_LOG)
        
    ##def readFile(self,path):
    ##    if os.path.exists(path):
    ##        file_object=open(path,'r',encoding='utf-8')
    ##        line=file_object.readlines()
    ##        
    ##        return line
    ##    pass
        
    def writeFile(self,file_path,list1,write_mode,encoding='utf-8'):
        with codecs.open(file_path,write_mode,encoding) as file_object:
            for line in list1 :
                file_object.write(line)
        # file_object.close()
        
    def do(self):
    
        max_log_list=[]
        vray_log_list=[]
        if os.path.exists(self.MAX_LOG):
            self.RENDER_LOG.info('[MonitorLog].handle maxlog...')
            # max_log_list=self.readFile(self.MAX_LOG)
            max_log_list = CLASS_COMMON_UTIL.read_random_file(self.MAX_LOG)
            # self.writeFile(self.WORK_MAX_LOG,max_log_list,'w')
            self.writeFile(self.WORK_NEW_RENDER_LOG,["\n\n======================================================================maxlog======================================================================\n\n"],'w')
            self.writeFile(self.WORK_NEW_RENDER_LOG,max_log_list,'a+')
            
        if os.path.exists(self.VRAY_LOG):
            self.RENDER_LOG.info('[MonitorLog].handle vraylog...')
            # vray_log_list=self.readFile(self.VRAY_LOG)
            vray_log_list = CLASS_COMMON_UTIL.read_random_file(self.VRAY_LOG)
            # self.writeFile(self.WORK_VRAY_LOG,vray_log_list,'w')
            self.writeFile(self.WORK_NEW_RENDER_LOG,["\n\n======================================================================vraylog======================================================================\n\n"],'a+')
            self.writeFile(self.WORK_NEW_RENDER_LOG,vray_log_list,'a+')
            
                    
        self.RENDER_LOG.info('[MonitorLog].sleep...')
        return max_log_list,vray_log_list
        
    
    
class RBMonitorLog(threading.Thread):
    def __init__(self,interval,taskId,cgVersion,logObj,feeLog,logWork,jobName): 
        threading.Thread.__init__(self)
        self.interval = interval  
        self.thread_stop = False
        self.RENDER_LOG=logObj
        self.FEE_LOG=feeLog
        
        self.maxLog = MaxLog(taskId,cgVersion,logObj,logWork,jobName)
            

            
    def run(self): #Overwrite run() method, put what you want the thread do here 
        self.RENDER_LOG.info('------------------------- start MonitorLog-------------------------')    
        
            
        
        while not self.thread_stop:
            self.RENDER_LOG.info('[MonitorLog].start...')
            maxLogList,vray_log_list=self.maxLog.do()
            
            error1='Error loading irradiance map: File format error'
            error2='error: Could not load irradiance map'
            # error3='warning: Could not connect to host'
            error4='warning: Error loading irradiance map: Error opening file'
            for vrayLogLine in vray_log_list:
                if error1 in vrayLogLine:
                    self.RENDER_LOG.info('')
                    self.RENDER_LOG.info('-------------------------------------------------------------------------------------------------')
                    self.RENDER_LOG.info('[error]'+error1)
                    self.RENDER_LOG.info('-------------------------------------------------------------------------------------------------\r\n')
                    self.FEE_LOG.info('jobStatus='+error1)
                    DogUtil.killMax(self.RENDER_LOG)
                    
                    sys.exit(-1)
                    
                # if error3 in vrayLogLine:
                    # self.RENDER_LOG.info('')
                    # self.RENDER_LOG.info('-------------------------------------------------------------------------------------------------')
                    # self.RENDER_LOG.info('[error]'+error3)
                    # self.RENDER_LOG.info('-------------------------------------------------------------------------------------------------\r\n')
                    # self.FEE_LOG.info('jobStatus='+error3)
                    # DogUtil.killMax(self.RENDER_LOG)
                    
                    # sys.exit(-1)
                
                if error4 in vrayLogLine:
                    self.RENDER_LOG.info('')
                    self.RENDER_LOG.info('-------------------------------------------------------------------------------------------------')
                    self.RENDER_LOG.info('[error]'+error4)
                    self.RENDER_LOG.info('-------------------------------------------------------------------------------------------------\r\n')
                    self.FEE_LOG.info('jobStatus='+error4)
                    DogUtil.killMax(self.RENDER_LOG)
                    
                    sys.exit(-1)
                
            time.sleep(self.interval)
        self.RENDER_LOG.info('------------------------- end MonitorLog-------------------------')   
    def stop(self):  
        self.thread_stop = True
        self.RENDER_LOG.info('[MonitorLog].stop...')
        try:
            print('end')
            
        except Exception as e:
            print('[MonitorLog.err]')
            print(e)
            
            
class RBMonitorLMU(threading.Thread):
    def __init__(self,interval,taskId,jobName,nodeName,logObj,workCfg): 
            threading.Thread.__init__(self)
            self.interval = interval  
            self.thread_stop = False
            self.RENDER_LOG=logObj
            self.TASK_ID=taskId
            self.JOB_NAME=jobName
            self.NODE_NAME=nodeName
            self.WORK_CFG=workCfg
            
    def checkProcess(self,procName):
        try:
            file_handle = os.popen('tasklist /FI "IMAGENAME eq ' + procName + '"')
            file_content = file_handle.read()
            if file_content.find(procName) > -1:
                self.RENDER_LOG.info('[MonitorLMU]....LMU EXISTS...')
                return True
                #sys.exit(-5)
            else:
                self.RENDER_LOG.info('[MonitorLMU]....LMU NOT EXISTS...')
                return False
                
        except BaseException as e:
            print(str(e))
            return False
            
    def run(self): #Overwrite run() method, put what you want the thread do here 
        self.RENDER_LOG.info('------------------------- start MonitorLMU-------------------------')    
        while not self.thread_stop:
            self.RENDER_LOG.info('[MonitorLMU].checkProcess...')
            lmuChecked=self.checkProcess('LMU.exe')
            if lmuChecked:
                DogUtil.killMax(self.RENDER_LOG)
                DogUtil.restartWin(self.RENDER_LOG)
                sys.exit(-1)
                
            self.RENDER_LOG.info('[MonitorLMU].sleep...')
            time.sleep(self.interval)
        self.RENDER_LOG.info('------------------------- end MonitorLMU-------------------------')   
    def stop(self):  
        self.thread_stop = True
        self.RENDER_LOG.info('[MonitorLMU].stop...')
        try:
            print('end')
            
        except Exception as e:
            print('[MonitorLMU.err]')
            print(e)
            
            
class RBMonitorMaxThread(threading.Thread):

    def __init__(self,interval,taskId,jobName,nodeName,logObj,workCfg):  
        threading.Thread.__init__(self)
        self.interval = interval  
        self.thread_stop = False
        self.RENDER_LOG=logObj
        self.TASK_ID=taskId
        self.JOB_NAME=jobName
        self.NODE_NAME=nodeName
        self.WORK_CFG=workCfg
        
    def getMaxInfo(self,cmd):
        print('cmd='+cmd)
        cpuStr=''
        memoryStr=''
        cmdp=subprocess.Popen(cmd,shell = True,stdout = subprocess.PIPE, stderr = subprocess.STDOUT)        
        while True:
            buff = cmdp.stdout.readline()
            buff = buff.decode(sys.getfilesystemencoding())
            if buff == '' and cmdp.poll() != None:
                break   
            if buff!=None  and ('|' in buff):
                cpuMem=buff.strip().strip('\r').strip('\n')
                cpuMemArr = cpuMem.split('|')
                cpuStr = cpuMemArr[0]
                memoryStr=cpuMemArr[1]
        return cpuStr,memoryStr
        
    def run(self): #Overwrite run() method, put what you want the thread do here  
        
        self.RENDER_LOG.info('------------------------- Start MonitorMax -------------------------')
        
        
        tempTxt=os.path.join(self.WORK_CFG,'temp.txt').replace('\\','/')
        tempBat=os.path.join(self.WORK_CFG,'temp.bat').replace('\\','/')
        
        processExe=r'b:/tools/process_utility.exe'
        processExe2=r'c:/process_utility.exe'
        shutil.copy(processExe,processExe2)
        checkProcessCmd=processExe2+' "3dsmax.exe"'
        
        while not self.thread_stop:
            try:
                
                self.RENDER_LOG.info('[MonitorMax].___MonitorMaxThread____')
                #os.system('echo fvok----------->>'+tempTxt)
                
                if os.path.exists(tempBat):
                    self.RENDER_LOG.info('run temp.bat')
                    os.system(tempBat+'>>'+tempTxt)
                
                cpuInfo,memoryInfo=self.getMaxInfo(checkProcessCmd)
                self.RENDER_LOG.info('[MonitorMax].Cpu='+cpuInfo+'% Memory='+memoryInfo)
                self.RENDER_LOG.info('[MonitorMax].sleep...')
                time.sleep(self.interval)
            except Exception as e:
                print('[MonitorMaxThread.err]')
                print(e)
                self.RENDER_LOG.info(e)
    def stop(self):  
        self.thread_stop = True
        self.RENDER_LOG.info('[MonitorMaxThread].stop...')
        try:
            print('end')
            
        except Exception as e:
            print('[MonitorMaxThread.err]')
            print(e)
            

            