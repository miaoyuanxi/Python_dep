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
from MaxPlugin import MaxPlugin
    
class DistributedRender():
    def __init__(self):
        self.PLUGIN_B_PATH=sys.argv[1]#"\\10.50.1.22\td_new\td"
        self.R_TASKID=sys.argv[2]#"5250767"
        self.R_RENDER_WORK='D:/work/render'
        self.R_MAX_VERSION=["2010","2011","2012","2013","2014","2015","2016","2017","2018","2019"]
        self.R_RENDER_WORK_TASK=os.path.join(self.R_RENDER_WORK,self.R_TASKID)
        if not os.path.exists(self.R_RENDER_WORK_TASK):
            os.makedirs(self.R_RENDER_WORK_TASK)
        self.R_RENDER_NODE_MAX=os.path.join(self.R_RENDER_WORK_TASK,'max')#.replace('\\','/')
        if not os.path.exists(self.R_RENDER_NODE_MAX):
            os.makedirs(self.R_RENDER_NODE_MAX)
        self.R_RENDER_NODE_CFG=os.path.join(self.R_RENDER_WORK_TASK,'cfg')
        if not os.path.exists(self.R_RENDER_NODE_CFG):
            os.makedirs(self.R_RENDER_NODE_CFG)
        
        self.R_MASTERIP=r'\\'+ sys.argv[3]#"10.50.7.80"
        self.R_MASTER_WORK='D$/work/render'
        self.R_MASTER_WORK_TASK=os.path.join(self.R_MASTERIP,self.R_MASTER_WORK,self.R_TASKID)
        self.R_MASTER_WORK_TASK_MAX=os.path.join(self.R_MASTERIP,self.R_MASTER_WORK,self.R_TASKID,'max')
        self.R_MASTER_WORK_TASK_CFG=os.path.join(self.R_MASTERIP,self.R_MASTER_WORK,self.R_TASKID,'cfg')
        self.R_MASTER_WORK_TASK_MAX_PACK=os.path.join(self.R_MASTER_WORK_TASK_MAX,'max.7z').replace('/','\\')
        
        if os.path.exists(self.R_MASTER_WORK_TASK_CFG):
            copyCfg='robocopy /e /ns /nc /nfl /ndl /np "%s" "%s"' % (self.R_MASTER_WORK_TASK_CFG,self.R_RENDER_NODE_CFG)
            self.runcmd(copyCfg)
            
        self.G_MAX_B='B:/plugins/max'
        self.G_PROGRAMFILES='C:/Program Files'
        
        self.G_LOG_WORK=sys.argv[4]#"c:/log"
        if not os.path.exists(self.G_LOG_WORK):
            os.makedirs(self.G_LOG_WORK)     
        self.G_PROCESS_LOG=logging.getLogger('processlog')
        self.PLUGIN_DICT=self.RBgetPluginDict()
        self.G_CG_VERSION=self.PLUGIN_DICT['renderSoftware']+' '+self.PLUGIN_DICT['softwareVer']
        
    def outPutLogger (self):
        self.G_PROCESS_LOG.info("\n\n-----------------------[VDR- set log path]-----------------------\n\n")
        processLogDir=os.path.join(self.G_LOG_WORK,self.R_TASKID)
        if not os.path.exists(processLogDir):
            os.makedirs(processLogDir)
            
        fm=logging.Formatter("%(asctime)s  %(levelname)s - %(message)s","%Y-%m-%d %H:%M:%S")
        processLogPath=os.path.join(processLogDir,"vray_distribute_log.txt")
        self.G_PROCESS_LOG.info(processLogPath)
        self.G_PROCESS_LOG.setLevel(logging.DEBUG)
        processLogHandler=logging.FileHandler(processLogPath)
        processLogHandler.setFormatter(fm)
        self.G_PROCESS_LOG.addHandler(processLogHandler)
        console = logging.StreamHandler()  
        console.setLevel(logging.INFO)  
        self.G_PROCESS_LOG.addHandler(console)
        self.G_PROCESS_LOG.info("[done]")
    
    def cleanMaxAndVrayExe(self):
        self.G_PROCESS_LOG.info("\n\n-----------------------[VDR- taskkill max and vray]-----------------------\n\n")
        maxExe='taskkill /im 3dsmax.exe /f'
        for G_version in self.R_MAX_VERSION:
            vrayExe='taskkill /im vrayspawner'+G_version+'.exe /f'
            self.runcmd(vrayExe)
        self.runcmd(maxExe)
        self.G_PROCESS_LOG.info("[done]")
        
    def cleanSubstAndNetDisk (self):
        self.G_PROCESS_LOG.info("\n\n-----------------------[VDR- del net path]-----------------------\n\n")
        self.G_PROCESS_LOG.info("del subst disk")
        existSubstDisk=['e:','f:','g:','h:','i:','j:','k:','l:','m:','n:','o:','p:','q:','r:','s:','t:','u:','v:','w:','x:','y:','z:']
        for substLocalDisk in existSubstDisk:
            delsubstDisk="subst %s /D" % (substLocalDisk)
            self.runcmd(delsubstDisk)
        delBDisk='try3 net use * /del /y'
        self.G_PROCESS_LOG.info(delBDisk)
        self.runcmd(delBDisk)
        self.G_PROCESS_LOG.info("[done]")

    def copyFilesToNode(self):
        self.G_PROCESS_LOG.info("\n\n-----------------------[VDR- copy renderFiles to node]-----------------------\n\n")
        max7z=self.R_RENDER_NODE_MAX+"/max.7z"
        if os.path.exists(self.R_MASTER_WORK_TASK_MAX_PACK):
            copyRenderPack=r'c:\fcopy\FastCopy.exe /cmd=diff /speed=full /force_close /no_confirm_stop /force_start '+'"'+self.R_MASTER_WORK_TASK_MAX_PACK+'"'+' /to='+'"'+self.R_RENDER_NODE_MAX.replace("/",'\\')+'"'
            self.G_PROCESS_LOG.info(copyRenderPack)
            self.runcmd(copyRenderPack)
            self.G_PROCESS_LOG.info("copy max.7z finshed")
            self.G_PROCESS_LOG.info("[done]")
        else:
            self.G_PROCESS_LOG.info(max7z+' is not existed')
            self.G_PROCESS_LOG.info('------------over----------------')
        if os.path.exists(max7z):
            unpack7z='d:/7-Zip/7z.exe x '+'"'+self.R_RENDER_NODE_MAX+'/max.7z" -y -aos -o"'+self.R_RENDER_NODE_MAX+'"'
            self.G_PROCESS_LOG.info(unpack7z)
            self.runcmd(unpack7z)
            self.G_PROCESS_LOG.info("unpack max.7z is OK")
            self.G_PROCESS_LOG.info("[done]")
            self.substPath()
            self.cfgPlugin()
        self.G_PROCESS_LOG.info("[done]")
            
    def substPath(self):
        self.G_PROCESS_LOG.info("\n\n-----------------------[VDR- net or subst path]-----------------------\n\n")
        diskList=os.listdir(self.R_RENDER_NODE_MAX)
        self.G_PROCESS_LOG.info(diskList)
        for disk in diskList: 
            if len(disk)==1 and disk !="a" and disk !="b" and disk !="c" and disk !="d":
                self.R_RENDER_NODE_MAX_DISK=os.path.join(self.R_RENDER_NODE_MAX,disk)
                substDisk="subst %s: \"%s\"" % (disk,self.R_RENDER_NODE_MAX_DISK)
                self.runcmd(substDisk)
                self.G_PROCESS_LOG.info(substDisk)
        netBDisk='try3 net use B: "'+self.PLUGIN_B_PATH+'"'
        self.runcmd(netBDisk)
        self.G_PROCESS_LOG.info("[done]")
        
    def cfgPlugin(self):
        self.G_PROCESS_LOG.info("\n\n-----------------------[VDR- config plugin]-----------------------\n\n")
        #maxPlugin=MaxPlugin(self.G_PROCESS_LOG,self.G_CG_VERSION,self.PLUGIN_DICT)
        maxPlugin=MaxPlugin(self.G_RAYVISION_PLUGINSCFG,self.G_PROCESS_LOG)
        maxPlugin.config()
        for G_version in self.R_MAX_VERSION:
            vraySpawnerVer='vrayspawner'+G_version+'.exe'
            vraySpawnerPath=os.path.join(self.G_PROGRAMFILES,"Autodesk",self.G_CG_VERSION,vraySpawnerVer).replace('\\','/')
            if  os.path.exists(vraySpawnerPath):
                self.G_PROCESS_LOG.info(vraySpawnerPath)
                os.system('start "" "%s"' % (vraySpawnerPath))
                self.G_PROCESS_LOG.info('running- '+vraySpawnerVer+"...")
                self.G_PROCESS_LOG.info("Set up total time: 120 s")
                delayTimes=["2","4"]
                self.G_PROCESS_LOG.info("Running time consuming: 0s ;  finished-- 0%")
                for delayTime in delayTimes: 
                    time.sleep(2)
                    self.G_PROCESS_LOG.info("Running time consuming: "+delayTime+"s ;  finished-- "+delayTime+"%")
        self.G_PROCESS_LOG.info("[done]")
        
    def RBgetPluginDict(self):
        self.G_PROCESS_LOG.info('[Max.RVgetPluginDict start]')
        self.G_RAYVISION_PLUGINSCFG=os.path.join(self.R_RENDER_NODE_CFG,'plugins.cfg')
        self.G_PROCESS_LOG.info(self.G_RAYVISION_PLUGINSCFG)
        # print(self.G_RAYVISION_PLUGINSCFG)
        plginInfoDict=None
        if  os.path.exists(self.G_RAYVISION_PLUGINSCFG):
            # fp = open(self.G_RAYVISION_PLUGINSCFG)

            # if fp:
            with open(self.G_RAYVISION_PLUGINSCFG) as fp:
                self.G_PROCESS_LOG.info('plugins file is exists')
                listOfplgCfg = fp.readlines()
                removeNL = [(i.rstrip('\n')) for i in listOfplgCfg]
                combinedText = ''.join(removeNL)
                plginInfoDict = eval('dict(%s)' % combinedText)
                # print(plginInfoDict)
                self.G_PROCESS_LOG.info(plginInfoDict)
                for i in list(plginInfoDict.keys()):
                    print(i)
                    print(plginInfoDict[i])
        self.G_PROCESS_LOG.info('[Max.RVgetPluginDict end]')
        return plginInfoDict

    def runcmd(self,cmdStr):
        cmdp=subprocess.Popen(cmdStr,stdin = subprocess.PIPE,stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = True)
        while True:
            buff=cmdp.stdout.readline()
            buff = buff.decode(sys.getfilesystemencoding())
            if buff=='' and cmdp.poll() !=None:
                break
        resultCode=cmdp.returncode

    def runAllConfig(self):
        self.outPutLogger()
        self.cleanMaxAndVrayExe()
        self.cleanSubstAndNetDisk()
        self.copyFilesToNode()

runconfig=DistributedRender()
runconfig.runAllConfig()