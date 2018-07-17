#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os,sys,subprocess,string,logging,time,shutil
import logging
import codecs
import time
import datetime



class NodeHelper:

    def __init__(self,log):
        print('init')
        self.LOG=log
        
        
    def getSubFolderList(self,folder):
    
        pass
        
    def formatTime(self,timestamp):
        timeArray = time.localtime(timestamp)
        date = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        
        #date = datetime.datetime.fromtimestamp(timestamp)  
        return str(date)
        
        
    def getDiskSpace(self,disk):
        self.LOG.info('')
        self.LOG.info('Check disk '+disk)
        cmd = 'fsutil volume diskfree '+disk+':'
        p = subprocess.Popen(cmd, shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        (child_stdin, child_stdout) = (p.stdin, p.stdout)
        linesList = child_stdout.readlines()
        child_stdin.close()
        child_stdout.close()
        try:
            if len(linesList)>0:
                freeSpace=float( linesList[0].strip().partition(":")[2] )/1024/1024/1024
                totalSpace=float( linesList[1].strip().partition(":")[2] )/1024/1024/1024
                
                self.LOG.info('Free space : '+str(freeSpace)+'G')
                self.LOG.info('Total space : '+str(totalSpace)+'G')
                return freeSpace
        except:
            print( "RV_Error: Cannot get the disk info correctly by executing \"%s\", please check if the disk is exist or not." % cmd )

        
    def checkDiskSpace(self):
        freeSpace=self.getDiskSpace('C')
        freeSpace=self.getDiskSpace('D')
        
        
    def cleanFolderByStayTime(self,cleanFolder,keepHour=72):
        if os.path.exists(cleanFolder) and os.path.isdir(cleanFolder):
            curretnTime=time.time()
            subFileList=os.listdir(cleanFolder)
            for sub in subFileList:
                subFile=os.path.join(cleanFolder,sub).replace('\\','/')
                #self.LOG.info('')
                #self.LOG.info(subFile)
                
                subFileMtime=os.path.getmtime(subFile)
                subFileCtime=os.path.getctime(subFile)
                subFileMtimeFormater=self.formatTime(subFileMtime)#modify time
                subFileCtimeFormater=self.formatTime(subFileCtime)#create time
                #self.LOG.info('Create time : '+subFileCtimeFormater)
                #self.LOG.info('Modify time : '+subFileMtimeFormater)
                
                stayHour=(curretnTime-subFileMtime)/ 3600 
                
                if 'd:/work' in cleanFolder:
                    fileStr=subFile+'|CreateTime|'+subFileCtimeFormater+'|ModifyTime|'+subFileMtimeFormater+'|StayHours|'+str(stayHour)
                    #self.LOG.info(fileStr)
                if stayHour>keepHour:
                    self.LOG.info('[remove]')
                    try:
                        if os.path.isdir(subFile):
                            shutil.rmtree(subFile)
                            pass
                        else:
                            pass
                            os.remove(subFile)
                    except Exception as e:
                        print(e)
                    
    
    def cleanFolder(self):
        self.cleanFolderByStayTime('d:/work/helper',168)
        self.cleanFolderByStayTime('d:/work/render',168)
        self.cleanFolderByStayTime('d:/log/helper',2160)
        self.cleanFolderByStayTime('d:/log/render',2160)
        
    def run(self):
        
        self.cleanFolder()
        self.checkDiskSpace()
        
        


def test():

    myLog=logging.getLogger('renderlog')
    fm=logging.Formatter("%(asctime)s  %(levelname)s - %(message)s","%Y-%m-%d %H:%M:%S")
    processLogPath='d:/test.log'
    processLogHandler=logging.FileHandler(processLogPath)
    processLogHandler.setFormatter(fm)
    console = logging.StreamHandler()  
    console.setLevel(logging.INFO) 

    myLog.setLevel(logging.DEBUG)
    myLog.addHandler(processLogHandler)
    myLog.addHandler(console)

    NH=NodeHelper(myLog)
    NH.run()


    