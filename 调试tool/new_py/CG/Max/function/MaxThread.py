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

class MaxThread(threading.Thread):

    def __init__(self,interval,taskId,jobName,nodeName,workTask,grabOutput,logObj):  
        threading.Thread.__init__(self)
        self.interval = interval  
        self.thread_stop = False
        self.RENDER_LOG=logObj
        self.TASK_ID=taskId
        self.JOB_NAME=jobName
        self.NODE_NAME=nodeName
        self.WORK_TASK=workTask
        self.GRAB_OUTPUT=grabOutput
        self.grabImgName='grabImg1.3.exe'
        #self.PLUGINS_MAX_SCRIPT='B:/plugins/max2'
        self.W=600
        self.H=600
    
    def run(self): #Overwrite run() method, put what you want the thread do here  
        time.sleep(200)
        
    def stop(self):  
        self.thread_stop = True
        self.RENDER_LOG.info('[Thread].stop...')
        try:
            print('end')
            #os.system('taskkill /F /IM '+self.grabImgName+' /T')
        except Exception as e:
            print('[Thread.err]')
            print(e)