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
import time
from CommonUtil import RBCommon as CLASS_COMMON_UTIL


class MaxPlugin():
    def __init__(self,pluginCfg,myLog=None):
        print('config plugin...')
        
        self.G_LOCAL_AUTODESK='C:/Program Files/Autodesk'
        self.G_MAX_B='B:/plugins/max'
        self.G_PLUGIN_INI=self.G_MAX_B+'/ini'
        self.G_PROGRAM_FILES='C:/Program Files'
        
        self.MY_LOGER=myLog
        self.myLog('---------------maxPlugin------------------')
        if isinstance(pluginCfg,dict):
            self.G_PLUGIN_DICT=pluginCfg
        else:
            self.G_PLUGIN_DICT=self.getPluginDict(pluginCfg)
            
        
        if self.G_PLUGIN_DICT and 'plugins' in self.G_PLUGIN_DICT:
            pluginDict=self.G_PLUGIN_DICT['plugins']
            pluginDict['rayvision']='1.0.0'
        if 'renderSoftware' in self.G_PLUGIN_DICT or 'softwareVer' in self.G_PLUGIN_DICT:
            self.G_CG_VERSION=self.G_PLUGIN_DICT['renderSoftware']+' '+self.G_PLUGIN_DICT['softwareVer']
        else:
            self.G_CG_VERSION=self.G_PLUGIN_DICT['cg_name']+' '+self.G_PLUGIN_DICT['cg_version']
        print("maxclient-----")
        
    
    def myLog(self,str):
        if self.MY_LOGER==None:
            print(str)
        else:
            self.MY_LOGER.info(str)
       
    def getPluginDict(self,pluginCfg):
        self.myLog(pluginCfg)
        plginInfoDict=None
        if  os.path.exists(pluginCfg):
            # fp = open(pluginCfg)
            # if fp:
            with open(pluginCfg) as fp:
                listOfplgCfg = fp.readlines()
                removeNL = [(i.rstrip('\n')) for i in listOfplgCfg]
                combinedText = ''.join(removeNL)
                plginInfoDict = eval('dict(%s)' % combinedText)
                # print(plginInfoDict)
                for i in list(plginInfoDict.keys()):
                    self.myLog(i)
                    self.myLog(plginInfoDict[i])
                    
                    
        return plginInfoDict
    
    def delete(self):
    
        self.myLog('--------------------------------[MaxPlugin]Start Config plugin.delete--------------------------------\n\n')
        defDelPath=self.G_MAX_B+ '/script/pluginBat/delFile.bat' 
        print('defDelPath...',defDelPath)
        print('del plugins\n')
        delCmd='"'+defDelPath+'"'+' '+'"'+self.G_CG_VERSION+'"'
        
        self.myLog(delCmd)
        if os.path.exists(defDelPath):
            print('pluginDelCmd------'+defDelPath)
            self.runcmd(delCmd)
            print('pluginDelCmd...finished\n')
            
    
    def getIncludeIni(self):
        print('--------------------------------Start config ini--------------------------------\n\n')
        print('getIncludeIni...start------\n')
        standIni=os.path.join(self.G_PLUGIN_INI,'standard',self.G_CG_VERSION,'plugin_include.ini').replace('\\','/')
        includeIniList=[]
        if os.path.exists(standIni):
            f=open(standIni)
            sourceinclude=f.read()
            f.close()
            includeIniList.append(sourceinclude)
            
        allPlugDict=self.G_PLUGIN_DICT
        if allPlugDict and 'plugins' in allPlugDict:
            pluginDict=allPlugDict['plugins']
            for pluginName in pluginDict:  
                pluginVersion=pluginDict[pluginName]
                pluginPath=os.path.join(self.G_PLUGIN_INI,pluginName,pluginName+pluginVersion,self.G_CG_VERSION,'plugin_include.ini').replace('\\','/')
                if os.path.exists(pluginPath):
                    f=open(pluginPath)
                    sourceinclude=f.read()
                    f.close()
                    includeIniList.append(sourceinclude) 
                
        return includeIniList
        
    def getDirectoryIni(self):
        print('getDirectoryIni...start------\n')
        standIni=os.path.join(self.G_PLUGIN_INI,'standard',self.G_CG_VERSION,'plugin_directory.ini')
        directoryIniList=[]
        if os.path.exists(standIni):
            f=open(standIni)
            sourcedirectory=f.read()
            f.close()
            directoryIniList.append(sourcedirectory)
            
        allPlugDict=self.G_PLUGIN_DICT
        if allPlugDict and 'plugins' in allPlugDict:
            pluginDict=allPlugDict['plugins']
            for pluginName in pluginDict:  
                pluginVersion=pluginDict[pluginName]
                pluginPath=os.path.join(self.G_PLUGIN_INI,pluginName,pluginName+pluginVersion,self.G_CG_VERSION,'plugin_directory.ini').replace('\\','/')
                if os.path.exists(pluginPath):
                    f=open(pluginPath)
                    sourcedirectory=f.read()
                    f.close()
                    directoryIniList.append(sourcedirectory)
        return directoryIniList
        
    def writeIni(self):
        self.myLog('--------------------------------[MaxPlugin]writeIni...start--------------------------------\n')
        includeIniList=self.getIncludeIni()
        directoryIniList=self.getDirectoryIni()
        targetPath=os.path.join(self.G_LOCAL_AUTODESK,self.G_CG_VERSION,'en-US','plugin.ini').replace('\\','/')
        if self.G_CG_VERSION=='3ds Max 2010' or self.G_CG_VERSION=='3ds Max 2011' or self.G_CG_VERSION=='3ds Max 2012':
            targetPath=os.path.join(self.G_LOCAL_AUTODESK,self.G_CG_VERSION,'plugin.ini').replace('\\','/') 
        if os.path.exists(targetPath):
            os.system('del /s /q "%s"' % (targetPath)) 
            self.myLog('del ini'+targetPath+'\n')
        self.myLog('write ini to '+targetPath+'\n')
        f=open(targetPath,'wb')
        if includeIniList: 
            f.write(b'[Include]'+b'\n')
            for includeIni in includeIniList:
                includeIni = CLASS_COMMON_UTIL.str_to_bytes(includeIni)
                f.write(includeIni+b'\n')
            
        if directoryIniList: 
            f.write(b'[Directory]'+b'\n')
            for directoryIni in directoryIniList:
                directoryIni = CLASS_COMMON_UTIL.str_to_bytes(directoryIni)
                f.write(directoryIni+b'\n')
        print('write ini finished\n')
        f.close()    
        print('writeIni...end\n')
        
        
    def copyConfigPlugin(self):
        self.myLog('--------------------------------[MaxPlugin]start copy plugin--------------------------------\n\n')
        allPlugDict=self.G_PLUGIN_DICT
        if allPlugDict and 'plugins' in allPlugDict:
            pluginDict=allPlugDict['plugins']
            for pluginName in pluginDict:
                if pluginName=="vray":
                    pluginName2='vray2'
                    pluginVersion=pluginDict[pluginName]
                    print('[Load Plugin]----'+pluginName+","+pluginName+pluginVersion)
                    print('[Load Plugin]----'+pluginName+","+pluginName+pluginVersion)
                    srcDir=os.path.join(self.G_MAX_B,pluginName2,pluginName+pluginVersion,self.G_CG_VERSION,'Program Files.7z').replace('/','\\')
                    dPluginMax=os.path.join(r'd:\plugins\max',pluginName2,pluginName+pluginVersion,self.G_CG_VERSION).replace('/','\\')
                    d7z=os.path.join(dPluginMax,'Program Files.7z').replace('/','\\')
                    
                    fcmd=r'c:\fcopy\FastCopy.exe /speed=full /force_close /no_confirm_stop /force_start "'+srcDir+'" /to="'+dPluginMax+'"'
                    self.myLog(fcmd)
                    self.runcmd(fcmd)
                    
                    #c:/7-Zip/7z.exe e "d:/plugins/vray2/vay" -o"c:/work/helper/9269244/max/E/Work/17.04-05/Benz NGCC/max/Cam23a/" -y
                    unpackCmd='d:/7-Zip/7z.exe x "'+d7z+'" -y -aoa -o"c:/Program Files" '
                    self.myLog(unpackCmd)
                    self.runcmd(unpackCmd)
                    #os.system('robocopy /e /ns /nc /nfl /ndl /np "%s" "%s"' % (srcDir,self.G_PROGRAM_FILES))
                    #pluginBatPath=os.path.join(self.G_MAX_B,pluginName,'script',pluginName + '.bat').replace('\\','/')
                    #cmdStr='"'+pluginBatPath+'" "'+self.G_CG_VERSION+'" "'+pluginName+'" "'+pluginName+pluginVersion+'" "'+self.G_MAX_B+'"'
                    #if os.path.exists(pluginBatPath):
                        #self.runcmd(cmdStr) 
            for pluginName in pluginDict:
                if pluginName=="vray":
                    pass
                else:
                    pluginVersion=pluginDict[pluginName]
                    if pluginName == "multiscatter":
                        if "vray" in pluginDict:
                            # if pluginDict["vray"].startswith("3") and not pluginVersion.endswith(r"vray3.0"):
                            if pluginDict["vray"].startswith("3") and pluginVersion == r"1.2.0.12":
                                pluginVersion = pluginVersion + r"vray3.0"
                            if not pluginDict["vray"].startswith("3") and pluginVersion.endswith(r"vray3.0"):
                                # pluginVersion = pluginVersion - r"vray3.0"
                                pluginVersion = pluginVersion[:-7]
                    print(pluginVersion)
                    print('[Load Plugin]----'+pluginName+","+pluginName+pluginVersion)
                    print('[Load Plugin]----'+pluginName+","+pluginName+pluginVersion)
                    pluginBatPath=os.path.join(self.G_MAX_B,'script','pluginBat',pluginName + '.bat').replace('\\','/')
                    pluginBatPathNotWait=os.path.join(self.G_MAX_B,'script','pluginBat',pluginName + '_notwait.bat').replace('\\','/')
                    cmdStr='"'+pluginBatPath+'" "'+self.G_CG_VERSION+'" "'+pluginName+'" "'+pluginName+pluginVersion+'" "'+self.G_MAX_B+'"'
                    cmdStrNotWait='"'+pluginBatPathNotWait+'" "'+self.G_CG_VERSION+'" "'+pluginName+'" "'+pluginName+pluginVersion+'" "'+self.G_MAX_B+'"'
                    if os.path.exists(pluginBatPath):
                        self.runcmd(cmdStr)
                    else:
                        srcDir=os.path.join(self.G_MAX_B,pluginName,pluginName+pluginVersion,self.G_CG_VERSION).replace('\\','/')
                        dstDir=os.path.join(self.G_LOCAL_AUTODESK,self.G_CG_VERSION).replace('\\','/')
                        os.system('robocopy /e /ns /nc /nfl /ndl /np "%s" "%s"' % (srcDir,dstDir))
                    if os.path.exists(pluginBatPathNotWait):
                        os.system(cmdStrNotWait)
        print('Config Plugin...finished\n')
        print('Config Plugin...finished\n')
        
    def runcmd(self,cmdStr):
        cmdp=subprocess.Popen(cmdStr,stdin = subprocess.PIPE,stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = True)
        while True:
            resultLine=cmdp.stdout.readline()
            resultLine = resultLine.decode(sys.getfilesystemencoding())
            if resultLine == '' and cmdp.poll()!=None:
                break
            self.myLog(resultLine)
        resultCode=cmdp.returncode
        
    def config(self):
        self.myLog('\n\n-------------------------------------------------------[MaxPlugin]start----------------------------------------------------------\n\n')
        self.delete()
        self.writeIni()
        self.copyConfigPlugin()
        self.myLog('\n\n-------------------------------------------------------[MaxPlugin]end----------------------------------------------------------\n\n')
        
        
if __name__ == '__main__':
    pluginCfg=sys.argv[1]
    maxPlugin=MaxPlugin(pluginCfg)
    maxPlugin.config()
