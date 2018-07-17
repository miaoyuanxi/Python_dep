#! /usr/bin/env python
#encoding:utf-8
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import time
import optparse
import ctypes
import getpass
import codecs
import ConfigParser
import string
import datetime
import _winreg
import platform
import re
import argparse

from collections import Counter


reload(sys)
sys.setdefaultencoding('utf-8')

class RenderbusPath():
    def __init__(self,userPath,assetCollectAbsolutePath):
        self.G_INPUT_USER=userPath
        self.ASSET_CLIENT_COOLECT_BY_PATH=assetCollectAbsolutePath
    def InterPath(self,p):
        firstTwo = p[0:2]
        if firstTwo == '//' or firstTwo == '\\\\':
            normPath = p.replace('\\', '/')
            index = normPath.find('/', 2)
            if index <= 2:
                return False
            return True
        
    def parseInterPath(self,p):
        firstTwo = p[0:2]
        if firstTwo == '//' or firstTwo == '\\\\':
            normPath = p.replace('\\', '/')
            index = normPath.find('/', 2)
            if index <= 2:
                return ''
            
            return p[:index],p[index:]

    def convertPath(self,itemPath):
        if self.ASSET_CLIENT_COOLECT_BY_PATH:
            absPath=[['a:/','/a/'],
                ['b:/','/b/'],
                ['c:/','/c/'],
                ['d:/','/d/']]
                
            resultFile = itemPath
            lowerFile = os.path.normpath(itemPath.lower()).replace('\\', '/')
            is_abcd_path = False;
            is_InterPath = False;
            fileDir=os.path.dirname(lowerFile)
            if fileDir==None or fileDir.strip()=='':
                return os.path.normpath(resultFile)
            else:
                if self.InterPath(lowerFile):
                    start,rest = self.parseInterPath(lowerFile)
                    #resultFile= self.G_INPUT_USER + '/net' + start.replace('//', '/') + rest.replace('\\', '/') 
                    # resultFile= self.G_INPUT_USER + '/__'+ start.replace('//', '')+ rest.replace('\\', '/') 
                    resultFile= self.G_INPUT_USER + '/net/'+ start.replace('//', '')+ rest.replace('\\', '/') 
                else:
                    resultFile= self.G_INPUT_USER + '\\' + itemPath.replace('\\', '/').replace(':','')

                return os.path.normpath(resultFile)
        else:
            return itemPath
            
    def convertToUserPath(self,sourceFile):
        resultFile = sourceFile
        userInput=self.G_INPUT_USER
        userInput=userInput.replace('/','\\')
        sourceFile=sourceFile.replace('/','\\').replace(userInput,'')
        
        #if sourceFile.startswith('net'):
        if sourceFile.startswith('__'):
            resultFile = '\\\\'+sourceFile[2:]
            #resultFile=resultFile.replace('\\','/')
        elif sourceFile.startswith('a\\') or sourceFile.startswith('b\\') or sourceFile.startswith('c\\') or sourceFile.startswith('d\\'):
            resultFile = sourceFile[0]+':'+sourceFile[1:]
            resultFile=resultFile.replace('\\','/')
        else:
            resultFile=sourceFile[0]+':'+sourceFile[1:]
            resultFile=resultFile.replace('\\','/')
        
        return resultFile
        
class ConflictPlugin:

    #'2012_2.40.03_1.1.09d',
    def __init__(self): 
        self.VRAY_MULTISCATTER=['2010_2.00.01_1.0.18a','2010_2.00.02_1.0.18a','2010_2.10.01_1.0.18a','2010_2.20.02_1.0.18a','2010_2.40.03_1.0.18a',
        '2010_2.00.01_1.1.05','2010_2.00.02_1.1.05','2010_2.10.01_1.1.05','2010_2.20.02_1.1.05','2010_2.40.03_1.1.05',
        '2010_2.00.01_1.1.05a','2010_2.10.01_1.1.05a','2010_2.20.02_1.1.05a','2010_2.40.03_1.1.05a','2010_2.00.01_1.1.07a',
        '2010_2.20.02_1.1.07a','2010_2.40.03_1.1.07a','2010_2.00.01_1.1.08b','2010_2.20.02_1.1.08b','2010_2.40.03_1.1.08b',
        '2010_2.00.01_1.1.09','2010_2.00.02_1.1.09','2010_2.10.01_1.1.09','2010_2.20.02_1.1.09','2010_2.40.03_1.1.09',
        '2010_2.00.01_1.1.09a','2010_2.40.03_1.1.09a','2010_2.00.01_1.1.09c','2010_2.40.03_1.1.09c','2010_2.00.01_1.1.09d',
        '2010_2.40.03_1.1.09d','2010_2.00.01_1.2.0.3','2010_2.00.02_1.2.0.3','2010_2.10.01_1.2.0.3','2010_2.20.02_1.2.0.3',
        '2010_2.40.03_1.2.0.3','2010_2.00.01_1.3.1.3a','2010_2.00.02_1.3.1.3a',
        '2010_2.10.01_1.3.1.3a','2010_2.20.02_1.3.1.3a','2010_2.40.03_1.3.1.3a','2011_2.00.01_1.0.18a','2011_2.00.02_1.0.18a',
        '2011_2.10.01_1.0.18a','2011_2.20.02_1.0.18a','2011_2.20.03_1.0.18a','2011_2.40.03_1.0.18a','2011_3.30.04_1.0.18a',
        '2011_3.30.05_1.0.18a','2011_2.00.02_1.1.05','2011_2.10.01_1.1.05','2011_2.20.02_1.1.05','2011_2.20.03_1.1.05',
        '2011_2.40.03_1.1.05','2011_3.30.04_1.1.05','2011_3.30.05_1.1.05','2011_2.10.01_1.1.05a','2011_2.20.02_1.1.05a',
        '2011_2.20.03_1.1.05a','2011_2.40.03_1.1.05a','2011_3.30.04_1.1.05a','2011_3.30.05_1.1.05a','2011_2.20.02_1.1.07a',
        '2011_2.20.03_1.1.07a','2011_2.40.03_1.1.07a','2011_3.30.04_1.1.07a','2011_3.30.05_1.1.07a','2011_2.20.02_1.1.08b',
        '2011_2.20.03_1.1.08b','2011_2.40.03_1.1.08b','2011_3.30.04_1.1.08b','2011_3.30.05_1.1.08b','2011_3.30.04_1.1.09',
        '2011_3.30.05_1.1.09','2011_2.40.03_1.1.09a','2011_3.30.04_1.1.09a','2011_3.30.05_1.1.09a','2011_2.40.03_1.1.09c',
        '2011_3.30.04_1.1.09c','2011_3.30.05_1.1.09c','2011_2.40.03_1.1.09d','2011_3.30.04_1.1.09d','2011_3.30.05_1.1.09d',
        '2011_3.30.04_1.2.0.3','2011_3.30.05_1.2.0.3','2011_2.00.01_1.3.1.3a','2011_2.00.02_1.3.1.3a',
        '2011_2.10.01_1.3.1.3a','2011_2.20.02_1.3.1.3a','2011_2.20.03_1.3.1.3a','2011_2.40.03_1.3.1.3a','2011_3.30.04_1.3.1.3a',
        '2011_3.30.05_1.3.1.3a','2012_2.20.02_1.1.07a','2012_2.20.03_1.1.07a','2012_2.30.01_1.1.07a','2012_2.40.03_1.1.07a',
        '2012_3.30.04_1.1.07a','2012_3.30.05_1.1.07a','2012_3.40.01_1.1.07a','2012_2.20.02_1.1.08b','2012_2.20.03_1.1.08b',
        '2012_2.30.01_1.1.08b','2012_2.40.03_1.1.08b','2012_3.30.04_1.1.08b','2012_3.30.05_1.1.08b','2012_3.40.01_1.1.08b',
        '2012_2.30.01_1.1.09','2012_2.40.03_1.1.09','2012_3.30.04_1.1.09','2012_3.30.05_1.1.09','2012_3.40.01_1.1.09',
        '2012_2.30.01_1.1.09a','2012_2.40.03_1.1.09a','2012_3.30.04_1.1.09a','2012_3.30.05_1.1.09a','2012_3.40.01_1.1.09a',
        '2012_2.40.03_1.1.09c','2012_3.30.04_1.1.09c','2012_3.30.05_1.1.09c','2012_3.40.01_1.1.09c',
        '2012_3.30.04_1.1.09d','2012_3.30.05_1.1.09d','2012_3.40.01_1.1.09d','2012_3.30.04_1.2.0.3','2012_3.30.05_1.2.0.3',
        '2012_3.40.01_1.2.0.3','2012_2.00.03_1.3.1.3a','2012_2.10.01_1.3.1.3a',
        '2012_2.20.02_1.3.1.3a','2012_2.20.03_1.3.1.3a','2012_2.30.01_1.3.1.3a','2012_2.40.03_1.3.1.3a','2012_3.30.04_1.3.1.3a',
        '2012_3.30.05_1.3.1.3a','2012_3.40.01_1.3.1.3a','2013_2.40.03_1.1.09c','2013_2.40.04_1.1.09c','2013_3.30.04_1.1.09c',
        '2013_3.30.05_1.1.09c','2013_3.40.01_1.1.09c','2013_2.40.03_1.1.09d','2013_2.40.04_1.1.09d','2013_3.30.04_1.1.09d',
        '2013_3.30.05_1.1.09d','2013_3.40.01_1.1.09d',
        '2013_3.30.04_1.2.0.3','2013_3.30.05_1.2.0.3','2013_3.40.01_1.2.0.3',
        '2013_2.30.01_1.3.1.3a','2013_2.40.03_1.3.1.3a','2013_2.40.04_1.3.1.3a','2013_3.30.04_1.3.1.3a','2013_3.30.05_1.3.1.3a',
        '2013_3.40.01_1.3.1.3a','2014_2.40.03_1.1.09c','2014_2.40.04_1.1.09c','2014_3.30.04_1.1.09c','2014_3.30.05_1.1.09c',
        '2014_3.40.01_1.1.09c','2014_2.40.03_1.1.09d','2014_2.40.04_1.1.09d','2014_3.30.04_1.1.09d','2014_3.30.05_1.1.09d',
        '2014_3.40.01_1.1.09d','2014_3.30.04_1.2.0.3',
        '2014_3.30.05_1.2.0.3','2014_3.40.01_1.2.0.3','2014_2.30.01_1.3.1.3a','2014_2.40.03_1.3.1.3a','2014_2.40.04_1.3.1.3a',
        '2012_3.40.02_1.1.09c','2012_3.40.02_1.1.09d','2012_3.40.02_1.2.0.3',
        '2012_3.50.03_1.1.09c','2012_3.50.03_1.1.09d','2012_3.50.03_1.2.0.3',
        '2012_2.30.01_1.1.09d']
    
    



    def maxPluginConflict(self,max='',plugin1='',plugin2=''):
        
        print '-----conflict Plugin--------'
        print max
        print plugin1
        print plugin2
        str_a=max+"_"+plugin1+"_"+plugin2
       
        if str_a  in self.VRAY_MULTISCATTER: 
            print("True!")
            return True
        else:
            print("False")
            return False
            
class TipsCode:
    def __init__(self):
    
        self.MAX_NOTEXISTS='15019'
        self.MAX_ZIP_FAILED='15009'
        self.VRAY_NOTMATCH='15020'
        
        
        self.MAXINFO_FAILED='15002'
        self.CONFLICT_MULTISCATTER_VRAY='15021'
        self.MAX_NOTMATCH='15013'
        self.CAMERA_DUPLICAT='15015'
        self.ELEMENT_DUPLICAT='15016'
        
        self.VRMESH_EXT_NULL="15018"
        self.PROXY_ENABLE="15010"
        self.RENDERER_NOTSUPPORT="15004"
        #-----------self.OUTPUTNAME_NULL="15007"
        self.CAMERA_NULL="15006"
        self.TASK_FOLDER_FAILED="15011"
        self.TASK_CREATE_FAILED="15012"
        self.MULTIFRAME_NOTSUPPORT="10015"#Irradiance map mode :  \"Multiframe incremental\" not supported
        self.ADDTOCMAP_NOTSUPPORT="10014"#Irradiance map mode : Add to current map not supported
        self.PPT_NOTSUPPORT="10016"#"Light cache mode : \"Progressive path tracing\" not supported "
        self.VRAY_HDRI_NOTSUPPORT="999"
        self.GAMMA_ON="10013"
        self.XREFFILES="10025"
        self.XREFOBJ="10026"
        self.VDB_MISSING="10028"
        self.REALFLOW_VERSION="15022"
        self.MISSING_FILE="10012"
        self.VRMESH_MISSING='10030'
        self.HDRI_MISSING="10012"
        self.VRMAP_MISSING="10023"
        self.VRLMAP_MISSING="10024"
        self.FUMEFX_MISSING="10011"
        self.PHOENIFX_MISSING="10022"
        self.FIRESMOKESIM_MISSING="10022"
        self.LIQUIDSIM_MISSING="10022"
        self.KK_MISSING="10019"
        self.ABC_MISSING="10018"
        self.XMESH_MISSING="10020"
        self.ANIMATION_MAP_MISSING="10027"
        self.REALFLOW_MISSING="10021"
        self.BAD_MATERIAL="10010"
        self.VRIMG_UNDEFINED="10017"#--"\"Render to V-Ray raw image file\" Checked but *.vrimg is undefined "
        self.CHANNEL_FILE_UNDEFINED="15017"#--"Save separate render channels Checked but channels file is error"
        
        self.NOT_ENGLISH_MAX='10033'
        
        self.DUP_TEXTURE='15023'
        self.UNKNOW_ERR='999'
        
        self.HAIR_MISSING='10032'
        
        self.RENDERER_MISSING='15005'
        
        self.PL_OPEN_FAILED="15028"
        self.PL_CONTENT_EXCEPTION="15029"
        self.MAX_PRIVILEGE_HIGH="15030"
        self.TASK_GET_FAILED="15031"
        self.MATERIAL_PATH_LONG="15032"        
        self.MAX_NAME_ILLEGAL = "15033"
        
class SubmitMax:
    def __init__(self):
        print 'init...'
        self.MAX_CMD = ["multiscatter1.3.5.6","multiscatter1.3.6.3","multiscatter1.3.6.9","multiscatter1.0.5.5",
        "forestpack4.2.2","forestpack4.2.5","forestpack4.3.6","forestpack4.3.7","forestpack4.4.0","forestpack4.4.1","forestpack5.0.5","forestpack5.2.0","forestpack5.3.2","forestpack5.4.0",
        "railclone2.3.4","railclone2.4.7","railclone2.5.0","railclone2.6.0","railclone2.7.0","railclone2.7.4","railclone 2.7.5","railclone 3.0.7","railclone 3.0.8"]
        
        self.error9900_max_damage='Scene has damged or been compressed' #场景文件已损坏或者被压缩
        self.error9899_maxexe_notexist='3ds Max software of scene has not been found'  #未找到场景使用的3ds Max 软件版本
        self.error9898_project_maxversion='3ds Max version of scene is different from the version you configured for the project'#场景文件用的3dsmax版本和项目配置的3dsmax版本不一致
        self.error_getcgversion_exception='Getting 3ds Max software version failed' #获取3ds Max 软件版本失败
        self.error_getrenderer_exception='Missing renderer'   #渲染器丢失
        self.error_getcglocation_exception='Getting 3ds Max software version failed'  #获取3ds Max 软件版本失败
        self.error_multiscatterandvray_confilict=' is not compatible with '
        
        self.msg_getmaxinfo_failed='Get max file info failed,Scene maybe has damged or been compressed'#获取场景信息失败，可能场景文件已损坏或者被压缩，或者使用了非英文版本制作。
        self.error_getmaxinfo_failed=self.msg_getmaxinfo_failed
        self.progress_getmaxinfo='get max file info start'
        self.progress_getmaxversion='Get 3ds Max version start...'
        
        
        self.error_zip_failed='Failed to compress 3dsmax scene into 7zip file'
        self.progress_startmax='Start 3ds Max'
        self.progress_endmax='Close 3ds Max'
        self.progress_startpackmax='Compressing 3dsmax scene to 7zip'
        self.progress_endpackmax='Compress 3dsmax scene to 7zip successfully'
        self.progress_subSuccessed='Submit task successfully'
        self.progress_subFailed='Submit task failed'
        self.errorList=[]
        
        self.CURRENT_PATH_STR=sys.path[0]
        self.CURRENT_PATH=self.convertStr2Unicode(self.CURRENT_PATH_STR)
        self.WINDOWS_USER_NAME=getpass.getuser()
        self.WINDOWS_USER_NAME = self.convertStr2Unicode(self.WINDOWS_USER_NAME)
        self.USER_PRO_FILE_STR=os.environ['userprofile']
        self.USER_PRO_FILE=self.convertStr2Unicode(self.USER_PRO_FILE_STR)
        self.PLUGIN_DICT={}
        
        self.TIPS_DICT={}
        
        self.TIPS_CODE=TipsCode()
        
        self.CONFLICT_PLUGIN=ConflictPlugin()
        '''
        self.CG_VERSION
        self.CG_VERSION_STR
        self.CG_WORK_PATH
        self.CG_FILE
        self.USER_NAME
        self.RENDERER
        self.MS_FILE
        self.USER_ID
        self.PROJECT_ID
        self.PROJECT_NAME
        self.PLUGIN_FILE
        self.RENDERFARM
        self.LANG
        self.PLATFORM
        self.TEMPPATH
        '''
        self.initOption()
        self.readIni()
        self.ERROR_TXT=self.TEMPPATH+'/error.txt'
        
        self.assetiInputCount=1
        
        self.USER_PARENT_ID=str((int(self.USER_ID)/500)*500)
        self.FATHER_PARENT_ID=str((int(self.FATHER_ID)/500)*500)
        userInput='/'+self.USER_PARENT_ID+'/'+self.USER_ID
        if self.SEPERATE_ACCOUNT == '2':
            userInput='/'+self.FATHER_PARENT_ID+'/'+self.FATHER_ID
            
        self.renderbusPathObj   = RenderbusPath(userInput,True)
        
        print '----------------------------------------'
        print 'CURRENT_PATH='+self.CURRENT_PATH_STR
        print 'WINDOWS_USER_NAME='+self.WINDOWS_USER_NAME
        print 'USER_PRO_FILE='+self.USER_PRO_FILE_STR
        print 'USER_ID='+self.USER_ID
        print 'FATHER_ID='+self.FATHER_ID
        print 'PROJECT_ID='+self.PROJECT_ID
        print 'PROJECT_NAME='+self.PROJECT_NAME
        print 'CG_FILE='+self.CG_FILE_S
        print 'PLUGIN_FILE='+self.PLUGIN_FILE
        print 'USER_NAME='+self.USER_NAME
        print 'TEMPPATH='+self.TEMPPATH_S
        print 'RENDERFARM='+self.RENDERFARM_S
        print 'LANG='+self.LANG
        print 'PLATFORM='+self.PLATFORM
        print 'TEMP_PROJECT_PATH='+self.TEMP_PROJECT_PATH
        print 'GUYVERSION='+self.GUYVERSION
        print 'INGORE_TEXTURE='+self.INGORE_TEXTURE
        print 'ENABLE_PARAM='+self.ENABLE_PARAM
        print 'SKIP_UPLOAD='+self.SKIP_UPLOAD
        print 'CLIENT_ZONE='+self.CLIENT_ZONE
        print 'CUSTOM_CLIENT='+self.CUSTOM_CLIENT
        print 'SEPERATE_ACCOUNT='+self.SEPERATE_ACCOUNT
        
        print type(self.RENDERFARM_S)
        print '----------------------------------------'

        
    def readIni(self):
        iniPath=os.path.join(self.CURRENT_PATH,'default.ini')
        print iniPath
        if os.path.exists(iniPath):
            fileHandle=open(iniPath)
            fileList = fileHandle.readlines()
            self.USER_NAME=fileList[0].strip('\r').lstrip().rstrip()
            self.TEMP_PROJECT_PATH=fileList[1].strip('\r').lstrip().rstrip()
            self.TEMP_PROJECT_PATH=self.TEMP_PROJECT_PATH.replace('\\','/')
            if not isinstance(str, unicode):
                try:
                    print 'utf-8 >> unicode'
                    self.USER_NAME=self.USER_NAME.decode('utf-8')
                    self.TEMP_PROJECT_PATH=self.TEMP_PROJECT_PATH.decode('utf-8')
                except:
                    try:
                        print 'filesystemencoding >> unicode'
                        self.USER_NAME=self.USER_NAME.decode(sys.getfilesystemencoding())
                        self.TEMP_PROJECT_PATH=self.TEMP_PROJECT_PATH.decode(sys.getfilesystemencoding())
                    except:
                        print 'failed to convert str to unicode'
            fileHandle.close()

    def initOption(self):
        parser = argparse.ArgumentParser()
        '''
        parser.add_argument("--userid", dest="userid",help="userid", metavar="string")
        parser.add_argument("--projectid", dest="projectid",help="projectid",metavar="string")
        parser.add_argument("--projectname", dest="projectname",help="projectname",metavar="string")
        parser.add_argument("--cgfile", dest="cgfile",help="cgfile",metavar="string")
        parser.add_argument("--pluginfile", dest="pluginfile",help="pluginfile",metavar="string")
        parser.add_argument("--renderfarm", dest="renderfarm",help="renderfarm",metavar="string")
        parser.add_argument("--lang", dest="lang",help="lang",metavar="string")
        '''

        parser.add_argument("--pi", dest="projectid", help="project id", metavar="int")
        parser.add_argument("--ps", dest="projectname", help="project symbol", metavar="string")
        parser.add_argument("--lv", dest="lv", help="level", metavar="string")
        parser.add_argument("--cgfl", dest="cgfile", help="submit cg file", metavar="string")
        parser.add_argument("--ui", dest="userid", help="userid", metavar="int")
        parser.add_argument("--fi", dest="fi", help="father id", metavar="int")
        parser.add_argument("--zo", dest="zo", help="zone", metavar="int")
        parser.add_argument("--sm", dest="enableParam", help="enable Param", metavar="int")
        parser.add_argument("--it", dest="ingoreTexture", help="ingore missing texture", metavar="int")
        parser.add_argument("--os", dest="skipUpload", help="skip upload texture", metavar="int")
        parser.add_argument("--pl", dest="pluginfile", help="pluginfile", metavar="string")
        parser.add_argument("--cgv", dest="cgv", help="cg version", metavar="string")
        parser.add_argument("--cginst", dest="cginst", help="cg install location", metavar="string")
        parser.add_argument("--fr", dest="fr", help="custom frames", metavar="string")
        parser.add_argument("--ver", dest="guyversion", help="version", metavar="string")
        parser.add_argument("--pt", dest="pt", help="platform", metavar="int")
        parser.add_argument("--lang", dest="lang", help="lang", metavar="string")
        parser.add_argument("--from", dest="renderfarm", help="renderfarm", metavar="string")
        parser.add_argument("--td", dest="temppath", help="assigned temporary dir", metavar="string")
        parser.add_argument("--de", dest="dependTaskId", help="Depend Task Id", metavar="int")
        parser.add_argument("--pp", dest="projectDir", help="Project Dir", metavar="string")
        parser.add_argument("-d", "--debug", dest="debug", help="debug", metavar="string")
        parser.add_argument("--cli", dest="clientZone", help="foxrenderfarm or renderbus", metavar="string")
        parser.add_argument("--cc", dest="customClient", help="custom client", metavar="string")
        parser.add_argument("--sa", dest="SeparateAccount", help="separate account", metavar="int")
        parser.add_argument("--mode", dest="mode", help="mode", metavar="string")

        (args, other_arg_list) = parser.parse_known_args()

        self.CG_FILE_S = args.cgfile.replace('\\', '/')
        self.RENDERFARM_S = args.renderfarm.replace('\\', '/')
        self.TEMPPATH_S = args.temppath.replace('\\', '/')

        if args.clientZone == None:
            self.CLIENT_ZONE = 'renderbus'
        else:
            self.CLIENT_ZONE = self.convertStr2Unicode(str(args.clientZone))
        if args.customClient == None:
            self.CUSTOM_CLIENT = ''
        else:
            self.CUSTOM_CLIENT = self.convertStr2Unicode(str(args.customClient))
        if args.SeparateAccount == None:
            self.SEPERATE_ACCOUNT = '0'
        else:
            self.SEPERATE_ACCOUNT = self.convertStr2Unicode(args.SeparateAccount)

        self.USER_ID = self.convertStr2Unicode(str(args.userid))
        self.FATHER_ID = self.convertStr2Unicode(str(args.fi))
        self.PROJECT_ID = self.convertStr2Unicode(str(args.projectid))
        self.PROJECT_NAME = self.convertStr2Unicode(args.projectname)
        self.CG_FILE = self.convertStr2Unicode(self.CG_FILE_S)
        self.PLUGIN_FILE = self.convertStr2Unicode(args.pluginfile.replace('\\', '/'))
        self.RENDERFARM = self.convertStr2Unicode(self.RENDERFARM_S)
        self.LANG = self.convertStr2Unicode(args.lang)
        self.PLATFORM = self.convertStr2Unicode(args.pt)
        self.TEMPPATH = self.convertStr2Unicode(self.TEMPPATH_S)
        self.GUYVERSION = self.convertStr2Unicode(args.guyversion)
        self.INGORE_TEXTURE = self.convertStr2Unicode(args.ingoreTexture)
        self.ENABLE_PARAM = self.convertStr2Unicode(args.enableParam)
        self.SKIP_UPLOAD = self.convertStr2Unicode(args.skipUpload)
        

    def initOption_abort20171117(self):
        parser = optparse.OptionParser()
        '''
        parser.add_option("--userid", dest="userid",help="userid", metavar="string")
        parser.add_option("--projectid", dest="projectid",help="projectid",metavar="string")
        parser.add_option("--projectname", dest="projectname",help="projectname",metavar="string")
        parser.add_option("--cgfile", dest="cgfile",help="cgfile",metavar="string")
        parser.add_option("--pluginfile", dest="pluginfile",help="pluginfile",metavar="string")
        parser.add_option("--renderfarm", dest="renderfarm",help="renderfarm",metavar="string")
        parser.add_option("--lang", dest="lang",help="lang",metavar="string")
        '''
        
        
        parser.add_option("--pi", dest="projectid",help="project id",metavar="int")
        parser.add_option("--ps", dest="projectname",help="project symbol",metavar="string")
        parser.add_option("--lv", dest="lv",help="level",metavar="string")
        parser.add_option("--cgfl", dest="cgfile",help="submit cg file",metavar="string")
        parser.add_option("--ui", dest="userid",help="userid", metavar="int")
        parser.add_option("--fi", dest="fi",help="father id",metavar="int")
        parser.add_option("--zo", dest="zo",help="zone",metavar="int")
        parser.add_option("--sm", dest="enableParam",help="enable Param",metavar="int")
        parser.add_option("--it", dest="ingoreTexture",help="ingore missing texture",metavar="int")
        parser.add_option("--os", dest="skipUpload",help="skip upload texture",metavar="int")
        parser.add_option("--pl", dest="pluginfile",help="pluginfile",metavar="string")
        parser.add_option("--cgv", dest="cgv",help="cg version",metavar="string")
        parser.add_option("--cginst", dest="cginst",help="cg install location",metavar="string")
        parser.add_option("--fr", dest="fr",help="custom frames",metavar="string")
        parser.add_option("--ver", dest="guyversion",help="version",metavar="string")
        parser.add_option("--pt", dest="pt",help="platform",metavar="int")
        parser.add_option("--lang", dest="lang",help="lang",metavar="string")
        parser.add_option("--from", dest="renderfarm",help="renderfarm",metavar="string")
        parser.add_option("--td", dest="temppath",help="assigned temporary dir",metavar="string")
        parser.add_option("--de", dest="dependTaskId",help="Depend Task Id",metavar="int")
        parser.add_option("--pp", dest="projectDir",help="Project Dir",metavar="string")
        parser.add_option("-d","--debug", dest="debug",help="debug",metavar="string")
        parser.add_option("--cli", dest="clientZone",help="foxrenderfarm or renderbus",metavar="string")
        parser.add_option("--cc", dest="customClient",help="custom client",metavar="string")
        
        
        (options, args) = parser.parse_args()
        
        self.CG_FILE_S=options.cgfile.replace('\\','/')
        self.RENDERFARM_S=options.renderfarm.replace('\\','/')
        self.TEMPPATH_S=options.temppath.replace('\\','/')
        
        if options.clientZone==None:
            self.CLIENT_ZONE='renderbus'
        else:
            self.CLIENT_ZONE=self.convertStr2Unicode(str(options.clientZone))
        if options.customClient==None:
            self.CUSTOM_CLIENT=''
        else:
            self.CUSTOM_CLIENT=self.convertStr2Unicode(str(options.customClient))    
        
            
        self.USER_ID=self.convertStr2Unicode(str(options.userid))
        self.PROJECT_ID=self.convertStr2Unicode(str(options.projectid))
        self.PROJECT_NAME=self.convertStr2Unicode(options.projectname)
        self.CG_FILE=self.convertStr2Unicode(self.CG_FILE_S)
        self.PLUGIN_FILE=self.convertStr2Unicode(options.pluginfile.replace('\\','/'))
        self.RENDERFARM=self.convertStr2Unicode(self.RENDERFARM_S)
        self.LANG=self.convertStr2Unicode(options.lang)
        self.PLATFORM=self.convertStr2Unicode(options.pt)
        self.TEMPPATH=self.convertStr2Unicode(self.TEMPPATH_S)
        self.GUYVERSION=self.convertStr2Unicode(options.guyversion)
        self.INGORE_TEXTURE=self.convertStr2Unicode(options.ingoreTexture)
        self.ENABLE_PARAM=self.convertStr2Unicode(options.enableParam)
        self.SKIP_UPLOAD=self.convertStr2Unicode(options.skipUpload)
        

    def convertStr2Unicode(self,str):
        if not isinstance(str, unicode):
            str=str.decode(sys.getfilesystemencoding())
        return str
        
    def convertUnicode2Str(self,uStr):
        print type(uStr)
        uStr=uStr.encode(sys.getfilesystemencoding())
        print type(uStr)
        return uStr
        
    def errorExit(self,exitCode,exitMsg):
    
            print '[err]',exitMsg
            self.writeLogFile()
            self.printCmd(exitCode,exitMsg)
            exit(exitCode)
            
            
    def getMaxVersionByNumber(self,maxNumber):
        maxVersion=None
        if cmp(maxNumber,float(20))==1 or cmp(maxNumber,float(20))==0:
            maxVersion='3ds Max 2018'
        elif cmp(maxNumber,float(19))==1 or cmp(maxNumber,float(19))==0:
            maxVersion='3ds Max 2017'
        elif cmp(maxNumber,float(18))==1 or cmp(maxNumber,float(18))==0:
            maxVersion='3ds Max 2016'
        elif cmp(maxNumber,float(17))==1 or cmp(maxNumber,float(17))==0:
            maxVersion='3ds Max 2015'
        elif cmp(maxNumber,float(16))==1 or cmp(maxNumber,float(16))==0:
            maxVersion='3ds Max 2014'
        elif cmp(maxNumber,float(15))==1 or cmp(maxNumber,float(15))==0:
            maxVersion='3ds Max 2013'
        elif cmp(maxNumber,float(14))==1 or cmp(maxNumber,float(14))==0:
            maxVersion='3ds Max 2012'
        elif cmp(maxNumber,float(13))==1 or cmp(maxNumber,float(13))==0:
            maxVersion='3ds Max 2011'
        elif cmp(maxNumber,float(12))==1 or cmp(maxNumber,float(12))==0:
            maxVersion='3ds Max 2010'
        return maxVersion
        

    def tryLoadDll(self):
        try:
            print 'load dll by system encode'
            self.loadDll(sys.getfilesystemencoding())
        except:
            pass
        if self.MAX_VERSION_INT_DLL==None or self.MAX_VERSION_STR_DLL==None or self.MAX_RENDERER_DLL==None:
            print 'load dll by  utf-8'
            try:
                self.loadDll('utf-8')
            except:
                pass
        if self.MAX_VERSION_INT_DLL==None or self.MAX_VERSION_STR_DLL==None or self.MAX_RENDERER_DLL==None:
            print 'load dll by  gbk'
            try:
                self.loadDll('gbk')
            except:
                pass
        if self.MAX_VERSION_INT_DLL==None or self.MAX_VERSION_STR_DLL==None or self.MAX_RENDERER_DLL==None:
            print '[err]failed to load submit_batch_max.dll'
            # self.writeExitsTips(self.TIPS_CODE.MAXINFO_FAILED)
        
    def loadDll(self,myCode):
    
        self.MAX_VERSION_INT_DLL=None
        self.MAX_VERSION_STR_DLL=None
        self.MAX_RENDERER_DLL=None
        self.MAX_OUTPUT_GAMMA_DLL=None
        
        dllPath=os.path.join(self.CURRENT_PATH,'submit_batch_max.dll')
        print dllPath
        if os.path.exists(dllPath):
            print '----load dll-----'
            # dll = ctypes.CDLL(dllPath)
            dll = ctypes.CDLL(dllPath.encode(sys.getfilesystemencoding()))
            contentPoint= dll.GetProperties(self.CG_FILE_S)
            content = ctypes.string_at(contentPoint, -1)
            print type(content)
            #print content
            '''
            maxInfo=codecs.open('c:/kkk.txt','a','UTF-8')
            maxInfo.write(content)
            maxInfo.close()
            '''
            
            maxInfoArr = content.split('\r\n')
            #print maxInfoArr
            if maxInfoArr!=None  and len(maxInfoArr)>1  :
                #for maxInfoLine in maxInfoArr:
                    #print maxInfoLine
                print '-------line-------'
                for maxInfoLine in maxInfoArr:
                    if not isinstance(maxInfoLine, unicode):
                        maxInfoLine=maxInfoLine.decode(myCode)
                    if maxInfoLine.startswith('\t3ds Max Version:') or maxInfoLine.startswith('\t3ds max Version:') or maxInfoLine.startswith('\t3ds Max 版本:') or maxInfoLine.startswith('\t3ds Max バージョン :'):
                        maxVersion=maxInfoLine.replace('\t3ds Max Version:','').replace('\t3ds max Version:','').replace('\t3ds Max 版本:','').replace('\t3ds Max バージョン :','')
                        maxVersion=maxVersion.replace(',','.')
                        maxVersionFloat=string.atof(maxVersion)
                        maxVersionStr = self.getMaxVersionByNumber(maxVersionFloat)
                        self.MAX_VERSION_INT_DLL=int(maxVersionFloat)
                        self.MAX_VERSION_STR_DLL=maxVersionStr
                        print '3ds max  version...',self.MAX_VERSION_INT_DLL,'___',self.MAX_VERSION_STR_DLL
                        
                    elif maxInfoLine.startswith('\tSaved As Version:') or maxInfoLine.startswith('\t另存为版本:')  or maxInfoLine.startswith('\tバージョンとして保存:'):
                        maxVersion=maxInfoLine.replace('\tSaved As Version:','').replace('\t另存为版本:','').replace('\tバージョンとして保存:','')
                        maxVersion=maxVersion.replace(',','.')
                        maxVersionFloat=string.atof(maxVersion)
                        maxVersionStr = self.getMaxVersionByNumber(maxVersionFloat)
                        self.MAX_VERSION_INT_DLL=int(maxVersionFloat)
                        self.MAX_VERSION_STR_DLL=maxVersionStr
                        print '3ds max save as version...',self.MAX_VERSION_INT_DLL,'___',self.MAX_VERSION_STR_DLL
                        
                    elif maxInfoLine.startswith('\tRenderer Name='):
                        renderer=maxInfoLine.replace('\tRenderer Name=','')
                        renderer = renderer.lower().replace('v-ray ', 'vray').replace('v_ray ', 'vray').replace('adv ', '').replace('edu ', '').replace('demo ', '').replace(' ', '')
                        self.MAX_RENDERER_DLL=renderer
                        print '3ds max  renderer...',self.MAX_RENDERER_DLL
                        
                    elif maxInfoLine.startswith('\tRender Output Gamma='):#default is 0.00
                        outputGamma=maxInfoLine.replace('\tRender Output Gamma=','')
                        self.MAX_OUTPUT_GAMMA_DLL=outputGamma
                        print '3ds max  output gamma...',self.MAX_OUTPUT_GAMMA_DLL

                        

    def getProjectMaxVersion(self):
        self.printLineInfo('Get Project info')
        projectMaxVersion=None
        if  os.path.exists(self.PLUGIN_FILE):
            try:
                fp = open(self.PLUGIN_FILE)
            except Exception as e:
                print '[err]can\'t open file:' + self.PLUGIN_FILE
                print '[err]',e
                self.writeExitsTips(self.TIPS_CODE.PL_OPEN_FAILED,[self.PLUGIN_FILE])
            if fp:
                listOfplgCfg = fp.readlines()
                removeNL = [(i.rstrip('\n')) for i in listOfplgCfg]
                combinedText = ''.join(removeNL)
                try:
                    plginInfoDict = eval('dict(%s)' % combinedText)
                    print plginInfoDict
                except Exception as e:
                    print '[err]failed to translate pl file into dictionary'
                    print '[err]',e
                    self.writeExitsTips(self.TIPS_CODE.PL_CONTENT_EXCEPTION)
                pl_key_list = plginInfoDict.keys()
                if not ('3rdPartyShaders' in pl_key_list and 'plugins' in pl_key_list and 'renderSoftware' in pl_key_list and 'softwareVer' in pl_key_list):
                    print '[err]pl file write incomplete'
                    self.writeExitsTips(self.TIPS_CODE.PL_CONTENT_EXCEPTION)
                if plginInfoDict!=None and plginInfoDict.has_key('renderSoftware') and plginInfoDict.has_key('softwareVer'):
                    projectMaxVersion=plginInfoDict['renderSoftware']+' ' +plginInfoDict['softwareVer']
                    print 'projectMaxVersion===='+projectMaxVersion
        else:
            print '[err]pl file does not exist:' + self.PLUGIN_FILE
            self.writeExitsTips(self.TIPS_CODE.PL_CONTENT_EXCEPTION)
        return projectMaxVersion
        
    def readRenderCfg(self):
        self.printLineInfo('Read render cfg')
        
        if self.CG_VERSION<15:
            renderTempCfgFile=os.path.join(self.TASK_TEMP_PROJECT_PATH,'renderTemp.cfg')
            if not os.path.exists(renderTempCfgFile):
                self.printLineInfo('renderTemp.cfg not exists')
                exit()
            self.convertCode()
                    
        renderCfg=os.path.join(self.TASK_TEMP_PROJECT_PATH,'render.cfg')
        if not os.path.exists(renderCfg):
            self.printLineInfo('render.cfg not exists')
            exit()
        self.RENDER_CFG_PARSER =None
        self.RENDER_CFG_PARSER = ConfigParser.ConfigParser()
        #self.RENDER_CFG_PARSER.read(renderCfg)
        try:
            print('read render cfg utf16')
            self.RENDER_CFG_PARSER.readfp(codecs.open(renderCfg, "r", "UTF-16"))
        except Exception, e:
            try:
                print('read render cfg utf8')
                self.RENDER_CFG_PARSER.readfp(codecs.open(renderCfg, "r", "UTF-8"))
            except Exception, e:
                print(e)
                print('read render cfg default')
                self.RENDER_CFG_PARSER.readfp(codecs.open(renderCfg, "r"))
        
        if self.RENDER_CFG_PARSER.has_option('renderSettings', 'frames'):
            self.FRAMES=self.RENDER_CFG_PARSER.get('renderSettings', 'frames')
        if self.RENDER_CFG_PARSER.has_option('renderSettings', 'animationRange'):
            self.ANIMATION_RANGE=self.RENDER_CFG_PARSER.get('renderSettings', 'animationRange') 
        
    def writeMsFile(self):
        #C:\users\enfuzion\AppData\Roaming\RenderBus\Profiles\users\cust\enfuzion\maxscript
        self.printLineInfo('Prepare ms file')
        #msPathArr=[self.USER_PRO_FILE,'appdata\\roaming\\renderbus','profiles\\users',self.USER_NAME,self.WINDOWS_USER_NAME,'maxscript']
        # msPathArr=[self.USER_PRO_FILE,'appdata\\roaming\\renderbus','profiles\\users',self.USER_NAME,'maxscript']
        msPathArr=[self.USER_PRO_FILE,'appdata\\roaming\\renderbus','profiles\\users','maxscript']
        msPath=os.path.join(*msPathArr).replace('\\','/')
        print msPath
        if not os.path.exists(msPath):
            os.makedirs(msPath)
        timeFormat='%Y%m%d%H%M%S'
        timeStr=time.strftime(timeFormat,time.localtime())
        msName='Analyse'+timeStr+'.ms'
        msFile=os.path.join(msPath,msName).replace('\\','/')
        msFileObject=codecs.open(msFile,'a',sys.getfilesystemencoding())
        if self.CG_VERSION>14:
            msFileObject=codecs.open(msFile,'a','UTF-8')
            
        msFileObject.write('(DotNetClass "System.Windows.Forms.Application").CurrentCulture = dotnetObject "System.Globalization.CultureInfo" "zh-cn"\r\n')
        msFileObject.write('filein @"'+self.MS_FILE+'"\r\n')
        msFileObject.write('fn analyse = (\r\n')
        mystr='rayvision "'+self.USER_ID+'" "'+self.PROJECT_ID+'" "'+self.PROJECT_NAME+'" "'+self.CG_FILE+'" "'+self.PLUGIN_FILE+'" "'+self.RENDERER+'" "'+self.PLATFORM+'" "'+self.RENDERFARM+'" "'+self.TEMPPATH+'" "'+self.GUYVERSION+'" "'+self.TEMP_PROJECT_PATH+'" "'+self.INGORE_TEXTURE+'" "'+self.ENABLE_PARAM+'" "'+self.SKIP_UPLOAD+'" "'+self.CLIENT_ZONE+'" "'+self.CUSTOM_CLIENT+'" "'+self.FATHER_ID+'" "'+self.SEPERATE_ACCOUNT+'"\r\n'
        
        msFileObject.write(mystr)
        msFileObject.write(')\r\n')
        msFileObject.close()
        return msFile
        

            
    def cmd(self,cmdStr):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        
        cmdp=subprocess.Popen(cmdStr,shell = True,stdout = subprocess.PIPE, stderr = subprocess.STDOUT,startupinfo=startupinfo)
        print '-------[cmd start]--------'
        print cmdStr
        result=''
        while cmdp.poll()==None:
            resultLine = cmdp.stdout.readline().strip()
            if resultLine!='':
                print resultLine
                result = result+resultLine
        print '-------[cmd end]--------'
        resultCode = cmdp.returncode
        resultStr = cmdp.stdout.read()
        print 'cmd_resultCode...'+str(resultCode)
        print 'cmd_resultStr...'+resultStr
        #print 'result...'+result
        return resultCode
        
    def subTask(self):
        self.printLineInfo('Submit task')
        renderCmd=os.path.join(self.RENDERFARM,'rendercmd.exe').replace('\\','/')
        renderCmdStr='"'+renderCmd+'" -subtask ' + self.TASK_ID
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        #kwargs['startupinfo'] = myStartupinfo
        #myStartupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
        #myStartupinfo.wShowWindow = _subprocess.SW_HIDE
        
        cmdp=subprocess.Popen(renderCmdStr,shell = True,stdout = subprocess.PIPE, stderr = subprocess.STDOUT,startupinfo=startupinfo)
        print '-------[subTask start]--------'
        while True:
            buff = cmdp.stdout.readline()
            if buff == '' and cmdp.poll() != None:
                #print cmdp.poll()
                break
            
        print '-------[subTask end]--------'
        resultCode = cmdp.returncode
        resultStr = cmdp.stdout.read()
        print 'subTask_resultCode...'+str(resultCode)
        print 'subTask_resultStr...'+resultStr
        
    
    def loadMaxInfo(self):
        self.printLineInfo('Load max info start')
        self.printCmd(200, 'Load max info ')
        try:
            mydll=os.path.join(self.RENDERFARM,'PropertyInfo.dll').replace('\\','/')
            print type(mydll)
            print mydll
            
            self.MAX_INFO = ctypes.CDLL(self.convertUnicode2Str(mydll))
            print '[Load max info successed ]'
        except Exception,e:
            print '[err] Load max info failed'
            print '[err]',e
            self.errorList.append(self.msg_getmaxinfo_failed)
            self.writeExitsTips(self.TIPS_CODE.MAXINFO_FAILED)
            #20170609[remove exit code]self.errorExit(108,self.error_getmaxinfo_failed)
        
    def getMaxVersion(self):
        #-----3ds max version
        self.printLineInfo('Get Max Version start')
        myCgVersion=None
        self.printCmd(200, 'Get Max Version')
        try:
            #self.CG_FILE_S=self.convertUnicode2Str(self.CG_FILE)
            myCgVersion = ctypes.c_char_p(self.MAX_INFO.GetCgsoftSavedVer(self.CG_FILE_S)).value
            print '3ds Max Save Version='+str(myCgVersion)
            if myCgVersion==None or myCgVersion=='':
                myCgVersion = ctypes.c_char_p(self.MAX_INFO.GetCgsoftVer(self.CG_FILE_S)).value
                print '3ds Max Version='+str(myCgVersion)
            
        except Exception,e:
            print '[err]Get Max Version failed'
            print '[err]',e
        #----------3ds max location
        if myCgVersion==None or myCgVersion=='':
            self.errorList.append(self.msg_getmaxinfo_failed)
            self.writeExitsTips(self.TIPS_CODE.MAXINFO_FAILED)
            #20170609[remove exit code]self.errorExit(108,self.error_getmaxinfo_failed)
        else:
            myCgVersion=myCgVersion.lstrip().rstrip()[0:2]
            
            self.CG_VERSION=int(myCgVersion)
            print 'CG_VERSION_INT:'+str(self.CG_VERSION)
            if self.CG_VERSION<=9:
                self.CG_VERSION_STR='3ds Max '+str(self.CG_VERSION)
            else:
                self.CG_VERSION_STR='3ds Max '+str(self.CG_VERSION+1998)
            print ('---'+self.CG_VERSION_STR+'---')
            self.printCmd(200, self.CG_VERSION_STR)
            
                
                
               
           
    def getMaxLocationReg(self,bit):
            
        maxLocation=None
        maxLanguageCode=''
        
        softwareStr=r'Software\Autodesk\\'
        if bit=='32':
            softwareStr='SOFTWARE\Wow6432Node\Autodesk\\'
        #---------------------get max locaction from regedit---------------------
        maxTypeList=['3dsMax','3dsMaxDesign']
        if self.CG_VERSION<15:
            maxLanguageCodeList=['409','40C','407','411','412','804']#English,French,German,Japanese,Korean,Chinese
            #HKEY_LOCAL_MACHINE\SOFTWARE\Autodesk\3dsMax\12.0\MAX-1:409
            for maxType in maxTypeList:
                for code in maxLanguageCodeList:
                    print maxType,code
                    try:
                        maxVersionStr=softwareStr+maxType+'\\'+str(self.CG_VERSION)+'.0\MAX-1:'+code
                        print maxVersionStr
                        key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,maxVersionStr)
                        maxLocation, type = _winreg.QueryValueEx(key, "Installdir")
                        maxLanguageCode=code
                        
                    except Exception, e:
                        print e
                        
        else:
        
            for maxType in maxTypeList:
                print maxType
                try:
                    maxVersionStr=softwareStr+maxType+'\\'+str(self.CG_VERSION)+'.0'#Software\Autodesk\3dsMax\15.0
                    key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,maxVersionStr)
                    maxLocation, type = _winreg.QueryValueEx(key, "Installdir")
                    print maxLocation
                except Exception, e:
                        print e
        return maxLocation,maxLanguageCode
        
    def getMaxLocationEnv(self,bit):
        #ADSK_3DSMAX_x64_2012    C:\Program Files\Autodesk\3ds Max 2012\
        #ADSK_3DSMAX_x64_2014    C:\Program Files\Autodesk\3ds Max 2014\
        maxLocation=None
        envKey='ADSK_3DSMAX_x'+bit+'_'+self.CG_VERSION_STR.replace('3ds Max ','')
        print envKey
        try:
            maxLocation=os.environ[envKey]
        except Exception, e:
            print e
        return maxLocation
        
        
    def getMaxLocation(self):
        self.printLineInfo('Get Max Location start...')

        maxLanguageCode=''
        maxLocation,maxLanguageCode=self.getMaxLocationReg('64')
            
        if maxLocation==None:
            maxLocation,maxLanguageCode=self.getMaxLocationReg('32')
            
        if maxLocation==None:
            maxLocation=self.getMaxLocationEnv('64')
            
        if maxLocation==None:
            maxLocation=self.getMaxLocationEnv('32')
        
        
        #---------------------max locaction  exists or not---------------------
        self.CG_WORK_PATH=None
        if maxLocation!=None:
            maxLocation=os.path.join(maxLocation,'3dsmax.exe').replace('\\','/')
            if os.path.exists(maxLocation):
                self.CG_WORK_PATH=maxLocation
                
        if self.CG_WORK_PATH ==None or self.CG_WORK_PATH =='':
            driverMaxList=['c','d','e','f']
            for driver in driverMaxList:
                maxLoc=driver+':\Program Files\Autodesk\\'+self.CG_VERSION_STR+'\3dsmax.exe'
                if os.path.exists(maxLoc):
                    self.CG_WORK_PATH=maxLoc
                    break
        
        #-----------ftype 3dsmax---------
        if self.CG_WORK_PATH ==None or self.CG_WORK_PATH =='':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            ftypeCmd='ftype 3dsmax'
            cmdp=subprocess.Popen(ftypeCmd,shell = True,stdout = subprocess.PIPE, stderr = subprocess.STDOUT,startupinfo=startupinfo)
            result=''
            while cmdp.poll()==None:
                resultLine = cmdp.stdout.readline().strip()
                if resultLine!='':
                    print resultLine
                    result = result+resultLine
            #3dsmax="C:\Program Files\Autodesk\3ds Max 2017\\3dsmax.exe" "%1"
            if result.startswith('3dsmax="') and self.CG_VERSION_STR in result:
                maxLoc=result.replace('3dsmax="','').replace('"%1"','').replace('"','').strip()
                if os.path.exists(maxLoc):
                    self.CG_WORK_PATH=maxLoc
            print '-------[cmd end]--------'
            
            
        if self.CG_WORK_PATH ==None or self.CG_WORK_PATH =='':
            maxLoc2=ctypes.c_char_p(self.MAX_INFO.GetCgsoftWorkpath(self.CG_FILE_S,str(self.CG_VERSION))).value
            if os.path.exists(maxLoc2):
                self.CG_WORK_PATH=maxLoc2
                
                
        if self.CG_WORK_PATH ==None or self.CG_WORK_PATH =='':           
            self.writeExitsTips(self.TIPS_CODE.MAX_NOTEXISTS,[self.CG_VERSION_STR])
            #20170609[remove exit code]self.errorExit(108,self.error_getmaxinfo_failed)
        else:
            if self.CG_VERSION<15 and maxLanguageCode in ['40C','407','411','412','804']:
                self.TIPS_DICT[self.TIPS_CODE.NOT_ENGLISH_MAX]=[self.CG_WORK_PATH]
                
    def getMaxLocation__abort(self):
        self.printLineInfo('Get Max Location start')
        try:
            
            self.CG_WORK_PATH=ctypes.c_char_p(self.MAX_INFO.GetCgsoftWorkpath(self.CG_FILE_S,str(self.CG_VERSION))).value
            print '3ds Max location:',self.CG_WORK_PATH
            if self.CG_WORK_PATH==None or self.CG_WORK_PATH=='':
                self.errorList.append(self.CG_VERSION_STR)
                self.errorList.append(self.error9899_maxexe_notexist)
                self.writeExitsTips(self.TIPS_CODE.MAXINFO_FAILED)
                #20170609[remove exit code]self.errorExit(108,self.error_getmaxinfo_failed)
            else:
                print 'CG_WORK_PATH=',self.CG_WORK_PATH
                print 'type=',type(self.CG_WORK_PATH)
                self.CG_WORK_PATH=self.CG_WORK_PATH.decode(sys.getfilesystemencoding())
                print 'after--->'
                print 'type=',type(self.CG_WORK_PATH)
                print 'CG_WORK_PATH=',self.CG_WORK_PATH
        except Exception,e:
            print '[err]Get 3ds Max program exception'
            print '[err]',e
            self.errorList.append(self.error_getcglocation_exception)
            self.writeExitsTips(self.TIPS_CODE.MAXINFO_FAILED)
            #20170609[remove exit code]self.errorExit(108,self.error_getmaxinfo_failed)
        if not os.path.exists(self.CG_WORK_PATH):
            self.writeExitsTips(self.TIPS_CODE.MAX_NOTEXISTS,[self.CG_WORK_PATH])
            #20170609[remove exit code]self.errorExit(108,self.error_getmaxinfo_failed)

    def getMaxRenderer(self):
        #------renderer version
        self.printLineInfo('Get Max Renderer start')
        try:
            self.RENDERER=ctypes.c_char_p(self.MAX_INFO.GetRendererName(self.CG_FILE_S)).value
            print 'renderer='+self.RENDERER
            self.RENDERER=self.convertStr2Unicode(self.RENDERER)
            self.RENDERER_STANDARD=self.RENDERER.lower().replace('v-ray ', 'vray').replace('v_ray ', 'vray').replace('adv ', '').replace('edu ', '').replace('demo ', '').replace(' ', '')
            if 'missing' in self.RENDERER.lower():
                print 'missing renderer'
                self.errorList.append(self.error_getrenderer_exception)
                self.writeExitsTips(self.TIPS_CODE.RENDERER_MISSING)
                #20170609[remove exit code]self.errorExit(108,self.error_getmaxinfo_failed)
        except Exception,e:
            print 'get renderer version exception'
            self.errorList.append(self.error_getrenderer_exception)
            self.writeExitsTips(self.TIPS_CODE.MAXINFO_FAILED)
            #20170609[remove exit code]self.errorExit(108,self.error_getmaxinfo_failed)
        
    def writeLogFile(self):
        if  os.path.exists(self.ERROR_TXT):
            os.remove(self.ERROR_TXT)
        logFileObject=codecs.open(self.ERROR_TXT,'a')
        for msg in self.errorList:
            logFileObject.write(msg+'\r\n')
        logFileObject.close()
        return logFileObject
    
    def askClient(self):
        print 'askclient'
        
    def maxInfo(self):
        self.loadMaxInfo()
        self.getMaxVersion()
        self.getMaxLocation()
        self.getMaxRenderer()
        
        
    def getTaskPluginCfg(self):
        self.printLineInfo('Get plugin info')
        
        projectMaxVersion=None
        if  os.path.exists(self.PLUGIN_FILE):
            try:
                fp = open(self.PLUGIN_FILE)
            except Exception as e:
                print '[err]can\'t open file:' + self.PLUGIN_FILE
                print '[err]',e
                self.writeExitsTips(self.TIPS_CODE.PL_OPEN_FAILED,[self.PLUGIN_FILE])
            if fp:
                listOfplgCfg = fp.readlines()
                removeNL = [(i.rstrip('\n')) for i in listOfplgCfg]
                combinedText = ''.join(removeNL)
                try:
                    self.PLUGIN_DICT = eval('dict(%s)' % combinedText)
                    print self.PLUGIN_DICT
                except Exception as e:
                    print '[err]failed to translate pl file into dictionary'
                    print '[err]',e
                    self.writeExitsTips(self.TIPS_CODE.PL_CONTENT_EXCEPTION)
                pl_key_list = self.PLUGIN_DICT.keys()
                if not ('3rdPartyShaders' in pl_key_list and 'plugins' in pl_key_list and 'renderSoftware' in pl_key_list and 'softwareVer' in pl_key_list):
                    print '[err]pl file write incomplete'
                    self.writeExitsTips(self.TIPS_CODE.PL_CONTENT_EXCEPTION)
        else:
            print '[err]pl file does not exist:' + self.PLUGIN_FILE
            self.writeExitsTips(self.TIPS_CODE.PL_CONTENT_EXCEPTION)
                
    def maxKill(self,parentId):
        print 'maxend...'
        cmdStr='wmic process where name="3dsmax.exe" get Caption,ParentProcessId,ProcessId'
        cmdp=subprocess.Popen(cmdStr,shell = True,stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        while True:
            buff = cmdp.stdout.readline().strip()
            if buff == '' and cmdp.poll() != None:
                #print cmdp.poll()
                break
            #self.G_PROCESS_LOGGER.info(buff)
            if buff!=None and buff!='' :
                try:
                    buffArr=buff.split()
                    #print buff
                    if int(buffArr[1])==parentId:
                        #print 'kill...'+buff
                        os.system("taskkill /f /pid %s" % (buffArr[2]))
                except:
                    pass
    
    def printLineInfo(self,info):
        print ''
        print '----------------------------------------------'
        print info
        print '----------------------------------------------'
    def printCmd(self,exitCode, exitInfo,sleep=0.3):
        sys.stdout.flush()
        if exitCode==300:
            print '<cmd><code>%s</code><des>%s</des><tid>%s</tid></cmd>' % (exitCode, exitInfo, exitInfo)
        else:
            print '<cmd><code>%s</code><des>%s</des></cmd>' % (exitCode, exitInfo)
        sys.stdout.flush()
        time.sleep(sleep)
        
    def handleBuffStr(self,buff,cmdp,sleep=0.3):
        buff=buff.strip('\n').strip('\r').lstrip().rstrip()
        #print 'msg...'+buff
        if buff.startswith('[maxscript]'):
            buffArr=buff.split('=')
            
            exitCode=int(buffArr[1])
            exitInfo=''
            
            for index in range(len(buffArr)):
                if index>1:
                    exitInfo=exitInfo+buffArr[index]
            self.EXIT_CODE=exitCode
            #running max
            
            
            if exitCode==200:#process
                self.printCmd(exitCode, exitInfo)
                self.process_info=exitInfo
            elif exitCode==300:#taskid
                
                if exitInfo=='-1':
                    try:
                        cmdp.terminate()
                        cmdp.kill()
                    except:
                        pass
                    try:
                        self.maxKill(cmdp.pid)
                    except:
                        pass
                    self.errorList.append(self.TIPS_CODE.TASK_CREATE_FAILED)
                    self.writeExitsTips(self.TIPS_CODE.TASK_CREATE_FAILED,[])
                    
                    
                else:
                    self.TASK_ID=exitInfo
                    self.TASK_TEMP_PROJECT_PATH=os.path.join(self.TEMP_PROJECT_PATH,self.TASK_ID)
                    self.printCmd(exitCode, exitInfo)
                    self.process_info=exitInfo
                
            elif exitCode==100:#success
                try:
                    self.maxKill(cmdp.pid)
                except:
                    pass
                    
                try:
                    cmdp.terminate()
                    cmdp.kill()
                except:
                    pass
                
            else:
                try:
                    self.maxKill(cmdp.pid)
                except:
                    pass
                    
                try:
                    cmdp.terminate()
                    cmdp.kill()
                except:
                    pass

            
            '''
            if exitCode==100:#success
                self.maxKill(cmdp.pid)
                self.printCmd(exitCode, exitInfo)
                cmdp.terminate()
                cmdp.kill()

            elif exitCode==201 or exitCode==202:#warn
                self.maxKill(cmdp.pid)
                self.printCmd(exitCode, exitInfo)
                cmdp.terminate()
                cmdp.kill()

                
            elif (exitCode>101 and exitCode<200) or exitCode==301:#error
                self.maxKill(cmdp.pid)
                self.printCmd(exitCode, exitInfo)
                cmdp.terminate()
                cmdp.kill()
                exit(exitCode)
            elif exitCode==300:#taskid
                self.TASK_ID=exitInfo
                self.TASK_TEMP_PROJECT_PATH=os.path.join(self.TEMP_PROJECT_PATH,self.TASK_ID)
                self.printCmd(exitCode, exitInfo)
            else:#process
                self.printCmd(exitCode, exitInfo)
            '''
        else:
            print buff
        
        
    def maxCmd(self,continueOnErr=False,myShell=False):#continueOnErr=true-->not exit ; continueOnErr=false--> exit 
        self.printLineInfo('3ds Max ready')
        
        maxscriptName='submitu.mse'
        if self.CG_VERSION>14:
            maxscriptName='submitu.mse'
        else:
            maxscriptName='submita.mse'
        self.MS_FILE=os.path.join(self.CURRENT_PATH,maxscriptName).replace('\\','/')
        '''
        print type(self.CG_FILE)
        cmdStr=u'"'+self.CG_WORK_PATH+'" -silent -mip  -mxs "filein \\"'+self.MS_FILE+'\\";rayvision \\"'+self.USER_ID+'\\" \\"'+self.PROJECT_ID+'\\" \\"'+self.PROJECT_NAME+'\\" \\"'+self.CG_FILE+'\\" \\"'+self.PLUGIN_FILE+'\\" \\"'
        print cmdStr
        print '****************************'
        '''
        maxTxt=os.path.join(self.TEMP_PROJECT_PATH,'max.txt')
        maxTxtTxt=os.path.join(self.TEMP_PROJECT_PATH,'max.txt.txt')
        mipParm='-mip'
        if  os.path.exists(maxTxt) or os.path.exists(maxTxtTxt):
            mipParm=' '
        if self.USER_ID=='962677' or self.USER_ID=='1811843' :
            mipParm=' '
        #cmdStr = '"'+self.CG_WORK_PATH+'" -silent '+mipParm+'  -mxs "filein \\"'+self.MS_FILE+'\\";rayvision \\"'+self.USER_ID+'\\" \\"'+self.PROJECT_ID+'\\" \\"'+self.PROJECT_NAME+'\\" \\"'+self.CG_FILE+'\\" \\"'+self.PLUGIN_FILE+'\\" \\"'+self.RENDERER+'\\" \\"'+self.PLATFORM+'\\" \\"'+self.RENDERFARM+'\\" \\"'+self.TEMPPATH+'\\" \\"'+self.GUYVERSION+'\\" \\"'+self.TEMP_PROJECT_PATH+'\\" \\"'+self.INGORE_TEXTURE+'\\" \\"'+self.ENABLE_PARAM+'\\" \\"'+self.SKIP_UPLOAD+'\\""'
        #if self.USER_ID=='962677' or self.USER_ID=='1811843':
        #cmdStr = '"'+self.CG_WORK_PATH+'" -silent  -mxs "filein \\"'+self.MS_FILE+'\\";rayvision \\"'+self.USER_ID+'\\" \\"'+self.PROJECT_ID+'\\" \\"'+self.PROJECT_NAME+'\\" \\"'+self.CG_FILE+'\\" \\"'+self.PLUGIN_FILE+'\\" \\"'+self.RENDERER+'\\" \\"'+self.PLATFORM+'\\" \\"'+self.RENDERFARM+'\\" \\"'+self.TEMPPATH+'\\" \\"'+self.GUYVERSION+'\\" \\"'+self.TEMP_PROJECT_PATH+'\\" \\"'+self.INGORE_TEXTURE+'\\" \\"'+self.ENABLE_PARAM+'\\" \\"'+self.SKIP_UPLOAD+'\\""'

        #if self.CG_VERSION==12:#2010
        msFile=self.writeMsFile()
        cmdStr='"'+self.CG_WORK_PATH.replace('\\','/')+'" -silent  '+mipParm+'   -mxs "filein \\"'+msFile+'\\";analyse()"'

        print '================================='
        print cmdStr
        print '================================='
        cmdStr=cmdStr.encode(sys.getfilesystemencoding())
        self.printCmd(200,self.progress_startmax)
        
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        #kwargs['startupinfo'] = myStartupinfo
        #myStartupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
        #myStartupinfo.wShowWindow = _subprocess.SW_HIDE
        
        cmdp=subprocess.Popen(cmdStr,shell = True,stdout = subprocess.PIPE, stderr = subprocess.STDOUT,startupinfo=startupinfo)
        
        self.printLineInfo('analyse max file start')
        while True:
            buff = cmdp.stdout.readline()
            if buff == '' and cmdp.poll() != None:
                #print cmdp.poll()
                break
            self.handleBuffStr(buff,cmdp)
        try:
            print self.TASK_ID
        except Exception as e:
            print '[err]failed to get task id'
            print '[err]',e
            self.writeExitsTips(self.TIPS_CODE.TASK_GET_FAILED)
        if not os.path.exists(self.TASK_TEMP_PROJECT_PATH):
            print '[err]failed to create task folder'
            self.writeExitsTips(self.TIPS_CODE.TASK_FOLDER_FAILED)
        self.printLineInfo('analyse max file end')
        resultCode = cmdp.returncode
        resultStr = cmdp.stdout.read()
        print 'resultCode...'+str(resultCode)
        print 'resultStr...'+resultStr
        print '3ds max end...'
        self.printCmd(200,self.progress_endmax)
        
    def convertCode(self):
        self.printLineInfo('Ready render cfg')
        print self.TASK_ID
        print sys.getdefaultencoding()
        print sys.getfilesystemencoding()
        
        
        renderCfgFile=os.path.join(self.TASK_TEMP_PROJECT_PATH,'render.cfg')
        renderTempCfgFile=os.path.join(self.TASK_TEMP_PROJECT_PATH,'renderTemp.cfg')
        print 'renderCfgFile=',renderCfgFile
        print 'renderTempCfgFile=',renderTempCfgFile
        
        #renderCfgFileObj=codecs.open(renderCfgFile,'r',encoding=sys.getfilesystemencoding())

        renderTempCfgFileObj=codecs.open(renderTempCfgFile,'r')
        renderCfgFileResult=renderTempCfgFileObj.read()
        renderCfgFileResult=renderCfgFileResult.decode(sys.getfilesystemencoding())
        renderTempCfgFileObj.close()
        
        print type(renderCfgFileResult)
        #print renderCfgFileResult
        
        #print renderCfgFileResult
        renderCfgFileObj=codecs.open(renderCfgFile,'a','UTF-16')
        renderCfgFileObj.write(renderCfgFileResult)
        renderCfgFileObj.close()
    

    def isUpload(self,cgfile):
    
        #self.TEMPPATH=r'C:\Users\Administrator\AppData\Local\Temp\RenderBus\Project\3_1469083485'
        #self.TEMP_PROJECT_PATH=r'C:\RenderFarm\Project'
        #self.TASK_TEMP_PROJECT_PATH=r'C:\RenderFarm\Project\5041113'
        #self.TASK_ID='1111111'
        result=False
        try:
            print type(cgfile),'----',cgfile
            cgfileSize=os.path.getsize(cgfile)
            cgfileMtime=os.path.getmtime(cgfile)
            cgfileMtime2 = datetime.datetime.fromtimestamp(cgfileMtime).strftime('%Y%m%d%H%M%S')

            cgfileU=self.convertStr2Unicode(cgfile)
            
            maxListPath = os.path.split(self.TEMPPATH)
            print maxListPath[0]
            maxListFile=os.path.join(maxListPath[0],'max.list')
            
            
            if os.path.exists(maxListFile):
                f  =codecs.open(maxListFile,'r','utf-8')
                uploadMaxList=f.readlines()
                f.close()
                
                for uploadMaxLine in uploadMaxList:
                    uploadMaxInfo=uploadMaxLine.split('|')

                    if cgfileU==uploadMaxInfo[2] and unicode(cgfileSize)==uploadMaxInfo[3] and unicode(cgfileMtime2)==uploadMaxInfo[4].strip():
                        print 'match record'
                        cgFilePath,cgFileName=os.path.split(cgfile)
                        taskPath = os.path.join(self.TEMP_PROJECT_PATH,uploadMaxInfo[0])
                        uploadCgfile=os.path.join(taskPath,(cgFileName+'.7z'))
                        if os.path.exists(taskPath) and  not os.path.exists(uploadCgfile):
                            result=True
                            break
                        
            f  =codecs.open(maxListFile,'a','utf-8')
            nowStr=time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
            maxInfoLine= self.TASK_ID+'|'+nowStr+'|'+cgfileU+'|'+str(cgfileSize)+'|'+cgfileMtime2+'\r\n'
            f.write(maxInfoLine)
            f.close()
        except:
            print 'is pack err'
        print 'isUpload result',result
        return result
        
    def packMax(self):
        self.printLineInfo('Zip file')
        if self.SKIP_UPLOAD=='0':
            self.printCmd(200,self.progress_startpackmax)
            
            if self.RENDER_CFG_PARSER.has_section('max'):
                zipExe=os.path.join(self.RENDERFARM,ur'module\bin\windows-32-msvc2012\7z.exe')
                
                zipfileKeyList=self.RENDER_CFG_PARSER.options('max')
                for zipfileKey in zipfileKeyList:
                    cgFile=(self.RENDER_CFG_PARSER.get('max',zipfileKey))
                            
                    #isUpload=self.isUpload(cgFile)
                    isUpload=False
                    if not isUpload:
                        cgFilePath,cgFileName=os.path.split(cgFile)
                
                        maxZip=os.path.join(self.TASK_TEMP_PROJECT_PATH,(cgFileName+'.7z'))
                        #cmdStr='"'+zipExe+'" a -t7z "'+maxZip+'" "'+cgFile+'"  -mmt -r'
                        #cmd = "\"%s\" a \"%s\" \"%s\" -mx3 -ssw" % (self.exe,zip_file, src)
                        
                        print '---------------------type---------------------------'
                        print type(self.RENDERFARM)
                        print type(zipExe)
                        print type(maxZip)
                        print type(cgFile)
                        print type(self.PLATFORM)
                        cmdStr=u'"'+zipExe+'" a "'+maxZip+'" "'+cgFile+'"   -mx3 -ssw'
                        cmdStr=cmdStr.encode(sys.getfilesystemencoding())
                        exitCode=self.cmd(cmdStr)
                        if exitCode==0 and  os.path.exists(maxZip):
                            print 'zip OK'
                        else:
                            self.writeExitsTips(self.TIPS_CODE.MAX_ZIP_FAILED)
                            self.errorList.append(self.error_zip_failed)
                            self.writeLogFile()
                            #20170609[remove exit code]
                            #self.printCmd(108,self.progress_subFailed)
                            #exit(108)

    def writeTaskPluginCfg(self):
        self.printLineInfo('writeTaskPluginCfg.Get plugin info')
        
        if self.PLUGIN_DICT!=None:
            
            if self.RENDERER!=None:
                #myRender=self.RENDERER.lower().replace('v-ray ', 'vray').replace('v_ray ', 'vray').replace('adv ', '').replace('demo ', '').replace(' ', '')
                myRender=self.RENDERER_STANDARD
                if 'vray' in myRender:
                    myRenderVersion=myRender.replace('vray','')
                    if self.PLUGIN_DICT.has_key('plugins'):
                        pluginDict=self.PLUGIN_DICT['plugins']
                        pluginDict['vray']=myRenderVersion
                    else:
                        pluginDict={}
                        pluginDict['vray']=myRenderVersion
                        self.PLUGIN_DICT['plugins']=pluginDict
                        
            newPlugins={}
            
            if self.MAX_VERSION_INT_DLL==None:
                self.MAX_VERSION_INT_DLL=''
            if self.MAX_VERSION_STR_DLL==None:
                self.MAX_VERSION_STR_DLL=''
            if self.MAX_RENDERER_DLL==None:
                self.MAX_RENDERER_DLL=''
            if self.MAX_OUTPUT_GAMMA_DLL==None:
                self.MAX_OUTPUT_GAMMA_DLL=''
            newPlugins[u'maxVersionInt']=self.MAX_VERSION_INT_DLL
            newPlugins[u'maxVersion']=self.MAX_VERSION_STR_DLL
            newPlugins[u'renderer']=self.MAX_RENDERER_DLL
            newPlugins[u'outputGamma']=self.MAX_OUTPUT_GAMMA_DLL
            self.PLUGIN_DICT[u'others']=newPlugins

            
            pluginCfgFile=os.path.join(self.TASK_TEMP_PROJECT_PATH,'plugins.cfg')
            #pluginCfgFile=os.path.join('d:/nono','pluginssss.cfg')
            pluginCfgFileObj=codecs.open(pluginCfgFile,'a','UTF-8')
            pluginCfgFileObj.write(str(self.PLUGIN_DICT))
            pluginCfgFileObj.close()
        
            
    def writeTips(self,str):
        tipsJson=os.path.join(self.TEMPPATH,'result.json')
        if os.path.exists(tipsJson):
            try:
                os.remove(tipsJson)
            except Exception, e:
                print 'remove result.json failed'
                
        
        fl=codecs.open(tipsJson, 'w', "UTF-8")
        fl.write(str)
        fl.close()
        

    def writeExitsTips(self,code,msgList=[]):
        str='{\r\n'
        str=str+'"'+code+'":['
        if msgList.count>0:
            for index,itemVal in enumerate(msgList):
                itemVal = itemVal.strip().replace('/','\\').replace('\\','\\\\').replace('"','\\"')
                if index==(len(msgList)-1):
                    str=str+'"'+itemVal+'"'
                else:
                    str=str+'"'+itemVal+'",'
                
        str=str+']\r\n}'
        self.writeTips(str)
        exit()

        
    # support only '[,]' format    
    def isListDuplicate(self, list):
        #items = self.RENDER_CFG_PARSER.get(section, option).strip(splitStr).split(splitStr) 
        mySet=set(list)
        if len(list)==len(mySet):
            return False
        else:
            return True
            
    def listToStr(self,msgList):
        if isinstance(msgList,list):
            str=''
            for item in msgList:
                str=str+'"'+item+'",'
            str=str.strip(',')
            str=str.replace('[','\[').replace(']','\]').replace('{','\{').replace('}','\}').replace('"','\"')
            str='['+str+']'
            
            return str
        else:
        
            return msgList


    def hanMSTips(self):#-----------abort
        #self.RENDER_CFG_PARSER=parseAnalyseTxt()
        print '----------tips-----------'
        itemList=[]
        if self.RENDER_CFG_PARSER.has_section('tips'):
            dataDict={}
            itemKeyList = self.RENDER_CFG_PARSER.options('tips')
            if len(itemKeyList)>0:
                
                for index,itemKey in enumerate(itemKeyList):
                #for itemKey in itemKeyList:
                    itemVal = self.RENDER_CFG_PARSER.get('tips', itemKey)
                    if itemVal==None or itemVal=='':
                        continue
                        
                    itemVal = itemVal.strip().replace('/','\\').replace('\\','\\\\')
                    msTipStr=itemKey+':'+itemVal
                    itemList.append(msTipStr)
                    self.TIPS_DICT[itemKey.strip().strip('"')]=itemVal
                    
        
        #self.checkTwoVray(itemList)
        #self.checkDuplictCamera(itemList)
        #self.checkDuplicatElem(itemList)
        
        
        if len(itemList)>0:
            tipStr='{\r\n'
            for  index,item in enumerate(itemList):
                if index==(len(itemList)-1):
                    tipStr=tipStr+item+'\r\n'
                else:
                    tipStr=tipStr+item+',\r\n'
                            
            tipStr=tipStr+'\r\n}'
            #self.writeTips(tipStr)
                #resultStr=resultStr.encode(sys.getfilesystemencoding())
                #resultStr=resultStr.decode(sys.getfilesystemencoding(), 'utf-8')
                #resultStr=resultStr.decode('gbk', 'utf-8')
                #resultStr=resultStr.decode(sys.getfilesystemencoding())
                #print resultStr
                
            return True
            
        else:
            return False
                
        
            
            

            
    def multiscatterAndVray(self):
        self.printLineInfo('-----multiscatter-----')
        
        pluginStr=''
        myRender=''
        if self.RENDERER!=None:
            myRender=self.RENDERER_STANDARD
            myRender=myRender.replace('vray', '')
        if self.PLUGIN_DICT!=None and self.PLUGIN_DICT.has_key('plugins'):
                 
            pluginDict=self.PLUGIN_DICT['plugins']
            if pluginDict.has_key('multiscatter'):
                pluginStr=pluginDict['multiscatter']
                
        if self.CONFLICT_PLUGIN.maxPluginConflict(self.CG_VERSION_STR.replace('3ds Max ',''),myRender,pluginStr):
        
            self.errorList.append((myRender+' '+pluginStr))
            self.writeExitsTips(self.TIPS_CODE.CONFLICT_MULTISCATTER_VRAY,[self.RENDERER_STANDARD,('Multiscatter'+pluginStr)])
            #20170609[remove exit code]
            #self.printCmd(108,self.progress_subFailed)
            #exit(108)
            exit()
            

    def validMaxProperties(self):
        self.errorList.append(self.TIPS_CODE.MAXINFO_FAILED)
        self.writeExitsTips(self.TIPS_CODE.MAXINFO_FAILED,[])
         
        #20170609[remove exit code]
        #self.printCmd(108,self.progress_subFailed)
        #exit(108)
        exit()
        
    #if WINDOWS_USER_NAME!=Administrator and the Privilege Level of 3dsmax is higher than RenderBus,the task will analyse failed
    def PrivilegeLevel(self):
        self.printLineInfo('-----PrivilegeLevel-----')
        print self.WINDOWS_USER_NAME
        windows_platform = platform.platform()  #Windows-7-6.1.7600,Windows-10-10.0.15063,Windows-8-6.2.9200
        print windows_platform
        if windows_platform.startswith("Windows-10") or windows_platform.startswith("Windows-8") or self.WINDOWS_USER_NAME.lower() != 'administrator':
            max_flag = False
            renderbus_flag = False
            key_user = None
            key_machine = None
            try:
                reg_user = _winreg.ConnectRegistry(None,_winreg.HKEY_CURRENT_USER)
                key_user = _winreg.OpenKey(reg_user,r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers")
            except WindowsError:
                print 'key_user maybe not exsits'
            try:
                reg_machine = _winreg.ConnectRegistry(None,_winreg.HKEY_LOCAL_MACHINE)
                key_machine = _winreg.OpenKey(reg_machine,r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers")
            except WindowsError:
                print 'key_machine maybe not exsits'
            if key_user != None or key_machine != None: #key exsits
                print self.CG_WORK_PATH.replace('/','\\')  #unicode
                exe_name = r"QRenderBus.exe"
                if self.CLIENT_ZONE == "renderbus":
                    exe_name = r"QRenderBus.exe"
                if self.CLIENT_ZONE == "foxrenderfarm":
                    exe_name = r"QFoxRenderfarm.exe"
                renderbus_path = os.path.join(self.RENDERFARM,exe_name).replace('/','\\')
                print renderbus_path  #unicode
                if key_user != None:
                    try:
                        i = 0
                        while i < 100:
                            name, value, tp = _winreg.EnumValue(key_user, i)  #str,unicode,int
                            try:
                                name = name.decode(sys.getfilesystemencoding())
                            except:
                                try:
                                    print 'utf-8'
                                    name = name.decode('utf-8')
                                except:
                                    try:
                                        print 'gbk'
                                        name = name.decode('gbk')
                                    except:
                                        print 'name decode failed'
                            # print name,':',value
                            name_lower = name.lower()
                            value_lower = value.lower()
                            value_lower_list = value_lower.split()
                            if name_lower == self.CG_WORK_PATH.replace('/','\\').lower() and 'runasadmin' in value_lower_list:
                                max_flag = True
                            if name_lower == renderbus_path.lower() and 'runasadmin' in value_lower_list:
                                renderbus_flag = True
                            i += 1
                    except WindowsError:
                        print 'key_user loop end'
                    _winreg.CloseKey(key_user)
                    print 'key_user end'
                if key_machine != None:
                    try:
                        i = 0
                        while i < 100:
                            name, value, tp = _winreg.EnumValue(key_machine, i)  #str,unicode,int
                            try:
                                name = name.decode(sys.getfilesystemencoding())
                            except:
                                try:
                                    print 'utf-8'
                                    name = name.decode('utf-8')
                                except:
                                    try:
                                        print 'gbk'
                                        name = name.decode('gbk')
                                    except:
                                        print 'name decode failed'
                            # print name,':',value
                            name_lower = name.lower()
                            value_lower = value.lower()
                            value_lower_list = value_lower.split()
                            if name_lower == self.CG_WORK_PATH.replace('/','\\').lower() and 'runasadmin' in value_lower_list:
                                max_flag = True
                            if name_lower == renderbus_path.lower() and 'runasadmin' in value_lower_list:
                                renderbus_flag = True
                            i += 1
                    except WindowsError:
                        print 'key_machine loop end'
                    _winreg.CloseKey(key_machine)
                    print 'key_machine end'
                print max_flag,renderbus_flag
                if windows_platform.startswith("Windows-10") or windows_platform.startswith("Windows-8"):
                    if max_flag == True:
                        print 'The Privilege Level of 3dsmax is higher than RenderBus'
                        self.writeExitsTips(self.TIPS_CODE.MAX_PRIVILEGE_HIGH)
                else:
                    if max_flag == True and renderbus_flag == False:
                        print 'The Privilege Level of 3dsmax is higher than RenderBus'
                        self.writeExitsTips(self.TIPS_CODE.MAX_PRIVILEGE_HIGH)
    
    #check max file length
    def checkLengthMax(self):
        #self.CG_FILE_S  self.CG_FILE
        max_file_name_maxlength = 222
        max_file_path_maxlength = 279
        max_file_name = self.CG_FILE_S.split('/')[-1]  #str
        max_file_name_length = len(max_file_name)
        max_file_path = self.CG_FILE_S[:-max_file_name_length]  #str
        max_file_path_length = len(max_file_path)
        print max_file_path
        print max_file_path_length
        print max_file_name
        print max_file_name_length
        if max_file_name_length > max_file_name_maxlength or max_file_path_length > max_file_path_maxlength:
            self.writeExitsTips(self.TIPS_CODE.MATERIAL_PATH_LONG,[self.CG_FILE])
    
    '''
        check max name
        Demand comes from bitone:
        1.Only '_' not allowed '-'
        2.The ending is only numeric
        3.start with an uppercase letter
        and so on
    '''
    def checkNameMax(self):
        max_file_name = self.CG_FILE_S.split('/')[-1]  #str
        (short_name,extension) = os.path.splitext(max_file_name)
        patt = r'^[A-Z][^-]*?\d$'
        m = re.match(patt,short_name)
        if m == None:
            self.writeExitsTips(self.TIPS_CODE.MAX_NAME_ILLEGAL,[self.CG_FILE])        
        
    def valid(self):
        self.multiscatterAndVray()
        # self.PrivilegeLevel()
        if self.USER_ID == '961404':
            self.checkNameMax()
        self.checkLengthMax()


        
    def run(self):
        #myInfo=Info()
        #self.convertCode()
        try:
            if not os.path.exists(self.TEMPPATH):
                os.makedirs(self.TEMPPATH)
        except Exception as e:
            print '[err]Create directory failed'
            print '[err]',e
        try:
            if not os.path.exists(self.TEMP_PROJECT_PATH):
                os.makedirs(self.TEMP_PROJECT_PATH)
        except Exception as e:
            print '[err]Create directory failed'
            print '[err]',e
        if not os.path.exists(self.TEMPPATH):
            self.writeExitsTips(self.TIPS_CODE.TASK_FOLDER_FAILED,[self.TEMPPATH])
        if not os.path.exists(self.TEMP_PROJECT_PATH):
            self.writeExitsTips(self.TIPS_CODE.TASK_FOLDER_FAILED,[self.TEMP_PROJECT_PATH])
            
        #-------------------remove result.json-------------------
        tipsJson=os.path.join(self.TEMPPATH,'result.json')
        if os.path.exists(tipsJson):
            try:
                os.remove(tipsJson)
            except Exception, e:
                print 'remove result.json failed'
            
        self.tryLoadDll()

        
        self.maxInfo()
        self.getTaskPluginCfg()
        self.valid()
        print sys.getdefaultencoding()
        print self.errorList
        
        
        if self.getProjectMaxVersion()!=self.CG_VERSION_STR:
            self.errorList.append(self.error9898_project_maxversion)
            self.writeLogFile()
            self.writeExitsTips(self.TIPS_CODE.MAX_NOTMATCH,[self.CG_VERSION_STR,self.getProjectMaxVersion()])
            exit()
        self.maxCmd()
        self.readRenderCfg()    
        self.hanTips()
        self.doAsset()
        self.packMax()
        self.writeTaskPluginCfg()
        self.writeLogFile()
        self.writeSeperateAccount()
        self.writeDistribute()
        self.writeRenderType()
        self.printLineInfo('analyse success')
        
    #------------------------analyse helper------------------
        
    def countCharInStr(self,str,char):
        start = str.find(char)
        end = str.rfind(char)
        if start==-1 and end==-1:
            return 0
        else:
            clen=end-start+1
            return clen
            
    def getSerial(self,number,numberCount):
        numberStr=str(number)
        while len(numberStr)<numberCount:
            numberStr='0'+numberStr
        return numberStr
        
    def endsWithNumber(self,myStr):
        for i in range(0,9) :
            if myStr.endswith(str(i)):
                return True
        return False
        
        
    def getFileMultiTimes(self,file):#cgfile=k:/test/mmmmm.max,file=F:/eeee/iiioo/nono.jpg
        if file==None or file.strip()=='':
            return None
            
        #print 'get file-------------------------'
        #---------------------F:/eeee/iiioo/nono.jpg---------------------
        #print file
        if os.path.exists(file):
            return file
            
        #---------------------k:/test/nono.jpg---------------------
        maxFileFolder=os.path.dirname(self.CG_FILE)
        fileName=os.path.basename(file)
        file2= os.path.join(maxFileFolder,fileName).replace('/','\\')
        #print file2
        if os.path.exists(file2):
            return file2
        
        #---------------------k:/test/iiioo/nono.jpg---------------------
        fileDirName=os.path.basename(os.path.dirname(file))
        file3=os.path.join(maxFileFolder,fileDirName,fileName).replace('/','\\')
        #print file3
        if os.path.exists(file3):
            return file3
        return None
        
    def handleAsset(self,assetsDict):
        resultDict={}
        for assetType,assetList in assetsDict.items():
            if assetType=='hair':
                resultList=[]
                missingResultList=[]
                for asset in assetList:
                    splitedArray=asset.split('|')
                    startFrame=splitedArray[0]
                    endFrame=splitedArray[1]
                    statFile=splitedArray[2] 
                    if statFile==None or statFile.strip()=='':
                        continue
                        
                    statFileBaseName=os.path.basename(statFile)
                    statFileFolder=os.path.dirname(statFile)
                    # build sequence number
                    start = int(startFrame);
                    end   = int(endFrame);
                    
                    statFile2=statFile[:-5]
                    for i in range(start , end+1, -1 if start > end else 1):
                        if i >= 0 :
                            file = statFile2  + self.getSerial(i,4) + '.stat'
                        else:
                            file = statFile2 + str(i) + '.stat'
                            
                        
                        resultFile=self.getFileMultiTimes(file)
                        if resultFile==None:
                            if file.strip()!='':
                                missingResultList.append(file.replace('/','\\').replace('\\','\\\\').replace('"','\\"'))
                        else:
                            inSceneFile=self.renderbusPathObj.convertPath(file)
                            resultList.append(resultFile+'>>'+inSceneFile) 
                        
                resultDict[assetType]=resultList
                #resultDict[assetType+'_missing']=missingResultList
                if len(missingResultList):
                    self.TIPS_DICT[self.TIPS_CODE.HAIR_MISSING]=missingResultList
            elif assetType=='texture':
                pass
            elif assetType=='common':
                pass
            elif assetType=='vray':
                pass
            elif assetType=='phoenix':
                print '--------phoenix---------'
                resultList=[]
                missingResultList=[]
                for asset in assetList:
                    splitedArray = asset.split('|')
                    startFrame  = splitedArray[0]
                    endFrame    = splitedArray[1]
                    type        = splitedArray[2] # PHXSimulator | FireSmokeSim | LiquidSim
                    nodeName    =splitedArray[3]
                    inputFile    = splitedArray[4]
                    outputFile    = splitedArray[5]
                    start = int(startFrame);
                    end   = int(endFrame);
                    if start==0 and end==0:
                        # frameArr=self.ANIMATION_RANGE.split('-')
                        patt = '(-?\d+)(?:-(-?\d+))?'
                        m = re.match(patt,self.ANIMATION_RANGE)
                        if m != None:
                            start = m.group(1)
                            end = m.group(2)
                            if end == None:
                                end = start
                            start = int(start)
                            end = int(end)
                        else:
                            print '[err]frameArr is not match'
                        # if len(frameArr)==1:
                            # start=end=int(frameArr[0])
                        # elif len(frameArr)==2:
                            # start=int(frameArr[0])
                            # end=int(frameArr[1])
                        
                    if inputFile.startswith('$'):
                        inputFile=outputFile
                    if inputFile.startswith('$'):
                        #resultList.append(nodeName) 
                        missingResultList.append(nodeName.replace('/','\\').replace('\\','\\\\'))
                        continue
                        
                    file = ''
                    #pos=inputFile.rfind('####.aur')
                    inputFile=inputFile.strip('.aur')
                    inputFileBaseName=os.path.basename(inputFile)
                    charCount=self.countCharInStr(inputFileBaseName,'#')
                    inputFile=inputFile.strip('#').strip('_')
                    
                    for i in range(start , end+1, -1 if start > end else 1):
                    
                        if i >= 0 :
                            file = inputFile  +'_'+ self.getSerial(i,charCount)  + '.aur'
                        else:
                            file = inputFile  +'_'+ str(i) + '.aur'
                        resultFile=self.getFileMultiTimes(file)
                        print file
                        print resultFile
                        if resultFile==None:
                            if file.strip()!='':
                                missingResultList.append(file.replace('/','\\').replace('\\','\\\\').replace('"','\\"'))
                        else:
                            inSceneFile=self.renderbusPathObj.convertPath(file)
                            resultList.append(resultFile+'>>'+inSceneFile)  
                resultDict[assetType]=resultList
                if len(missingResultList):
                    self.TIPS_DICT[self.TIPS_CODE.PHOENIFX_MISSING]=missingResultList
        return resultDict    
    
    def getItem(self, section):
        
        if self.RENDER_CFG_PARSER.has_section(section):
            itemList = []
            itemKeyList = self.RENDER_CFG_PARSER.options(section)
            print itemKeyList
            for itemKey in itemKeyList:
                itemPath = self.RENDER_CFG_PARSER.get(section, itemKey).strip()
                
                itemList.append(itemPath)
            
            return itemList
            
        
        
    def hanTips(self):
        self.printLineInfo('MS tips')
        #-----------------------MS TIPS-----------
        
        itemList=[]
        if self.RENDER_CFG_PARSER.has_section('tips'):
            dataDict={}
            itemKeyList = self.RENDER_CFG_PARSER.options('tips')
            if len(itemKeyList)>0:
                
                for index,itemKey in enumerate(itemKeyList):
                #for itemKey in itemKeyList:
                    itemVal = self.RENDER_CFG_PARSER.get('tips', itemKey)
                    if itemVal==None or itemVal=='':
                        continue
                        
                    itemVal = itemVal.strip().replace('/','\\').replace('\\','\\\\')
                    msTipStr=itemKey+':'+itemVal
                    itemList.append(msTipStr)
                    self.TIPS_DICT[itemKey.strip().strip('"')]=itemVal
        
        #------------CHECK two vray-----------
        if self.RENDERER_STANDARD.startswith('vray'):
            if self.RENDER_CFG_PARSER.has_option('common', 'render'):
                rendererMS = self.RENDER_CFG_PARSER.get('common', 'render')
                rendererMS=rendererMS.lower().replace('v-ray ', 'vray').replace('v_ray ', 'vray').replace('adv ', '').replace('edu ', '').replace('demo ', '').replace(' ', '')
                rendererMS=rendererMS.lower().replace('v_ray_', 'vray').replace('adv_', '').replace('edu_', '').replace('_', '.')
                if self.RENDERER_STANDARD!=rendererMS:
                    myList=[self.RENDERER_STANDARD.replace('/','\\').replace('\\','\\\\').replace('"','\\"'),rendererMS.replace('/','\\').replace('\\','\\\\').replace('"','\\"')]
                    self.TIPS_DICT[self.TIPS_CODE.VRAY_NOTMATCH]=myList
                    
        #------------gamma-----------
        if self.RENDER_CFG_PARSER.has_option('common','filegamma'):
            gamma= self.RENDER_CFG_PARSER.get('common', 'filegamma')
            if gamma!=None and gamma.strip()=='gamma':
                self.TIPS_DICT[self.TIPS_CODE.GAMMA_ON]=[]
        
        #------------global proxy-----------
        if self.RENDER_CFG_PARSER.has_option('renderSettings','globalproxy'):
            globalproxy= self.RENDER_CFG_PARSER.get('renderSettings', 'globalproxy')
            if globalproxy!=None and globalproxy.strip()=='true':
                self.TIPS_DICT[self.TIPS_CODE.PROXY_ENABLE]=[]
                
        #------------check duplicate camera-----------  
        if self.RENDER_CFG_PARSER.has_option('renderSettings', 'allCamera'):
            cameraItem=self.RENDER_CFG_PARSER.get('renderSettings', 'allCamera')
            # cameraList=cameraItem.strip().strip('[,]').split('[,]')
            cameraItem = cameraItem.strip()
            if cameraItem.startswith('[,]'):
                cameraItem = cameraItem[3:]
            if cameraItem.endswith('[,]'):
                cameraItem = cameraItem[:-3]
            cameraList=cameraItem.split('[,]')
            if self.isListDuplicate(cameraList ):
                cameraList2 = []
                for cl in cameraList:
                    cameraList2.append(cl.strip().replace('/','\\').replace('\\','\\\\').replace('"','\\"'))
                self.TIPS_DICT[self.TIPS_CODE.CAMERA_DUPLICAT]=cameraList2
                
        #------------check duplicate elements----------- 
        print 'check elem---------'
        if self.RENDER_CFG_PARSER.has_section('renderSettings'):
            renderSettingsList=self.getItem('renderSettings')
            elemList=[]
            elemTipList=[]
            itemKeyList = self.RENDER_CFG_PARSER.options('renderSettings')
            for itemKey in itemKeyList:
                if itemKey.startswith('renderelement') :
                    
                    itemVal = self.RENDER_CFG_PARSER.get('renderSettings', itemKey)
                    elemTipList.append(itemVal.replace('/','\\').replace('\\','\\\\').replace('"','\\"'))
                    pos=itemVal.rfind('|')+1
                    elemPath=itemVal[pos:]
                    
                    if elemPath!='':
                        elemList.append(os.path.basename(elemPath))
            
            if len(elemList)>0 and self.isListDuplicate(elemList):
                self.TIPS_DICT[self.TIPS_CODE.ELEMENT_DUPLICAT]=elemTipList
                        
        self.checkDuplicateTexture()
        self.checkLengthTexture()
        
        #------------vrmesh with null type-----------
        if self.RENDER_CFG_PARSER.has_section('vrmesh'):
            badVrmeshList=[]
            itemKeyList = self.RENDER_CFG_PARSER.options('vrmesh')
            for index,itemKey in enumerate(itemKeyList):
                itemVal = self.RENDER_CFG_PARSER.get('vrmesh', itemKey)
                if itemVal==None or itemVal=='':
                    continue
                itemVal = itemVal.strip()
                if os.path.splitext(itemVal)[1] ==None or  os.path.splitext(itemVal)[1] =='' :
                    badVrmeshList.append(itemVal.strip().replace('/','\\').replace('\\','\\\\').replace('"','\\"'))
            if len(badVrmeshList)>0:
                self.TIPS_DICT[self.TIPS_CODE.VRMESH_EXT_NULL]=badVrmeshList
                
                
    def checkDuplicateTexture(self):
    
        if self.RENDER_CFG_PARSER.has_section('texture'):
            dupTextureDict={}
            textureList=[]
            itemKeyList = self.RENDER_CFG_PARSER.options('texture')
            for index,itemKey in enumerate(itemKeyList):
                itemVal = self.RENDER_CFG_PARSER.get('texture', itemKey)
                if itemVal==None or itemVal=='':
                    continue
                itemVal = itemVal.strip()
                textureList.append(itemVal)
            
            for item1 in textureList:
                if item1==None or item1.strip()=='':
                    continue
                itemName1=item1.split('>>')[0]
                dupList=[]
                for item2 in textureList:
                    if item2==None or item2.strip()=='':
                        continue
                    itemName2=item2.split('>>')[0]
                    if itemName1==itemName2:
                        dupList.append(item2.split('>>')[1])
                if len(dupList)>1:
                    dupTextureDict[itemName1]=dupList
                    
            if len(dupTextureDict)>0 :
                dupTextureList=dupTextureDict.values()
                dupStr=''
                totalDupList=[]
                for dupList in dupTextureList:
                    totalDupList.extend(dupList)
                    
                self.TIPS_DICT[self.TIPS_CODE.DUP_TEXTURE]=totalDupList
                
    def checkLengthTexture(self):
        inputDataPath_len = 29  #inputDataPath=\\10.60.100.102/d/inputdata5/
        textureList=[]
        textureList_long = []
        if self.RENDER_CFG_PARSER.has_section('texture'):
            itemKeyList = self.RENDER_CFG_PARSER.options('texture')
            for index,itemKey in enumerate(itemKeyList):
                itemVal = self.RENDER_CFG_PARSER.get('texture', itemKey)
                if itemVal==None or itemVal=='':
                    continue
                itemVal = itemVal.strip()
                textureList.append(itemVal)
                
            for item in textureList:
                if item==None or item.strip()=='':
                    continue
                itemName1=item.split('>>')[0]
                itemName2=item.split('>>')[1]  #because filename can't contain '>>'
                item_length = inputDataPath_len + len(itemName2) - 1  #remove the length of '/'
                print 'item_length:%d' % (item_length)
                if item_length > 259:  #max length of filename in windows is 259 bytes
                    if itemName1.endswith(r'.7z'):
                        max_name = self.RENDER_CFG_PARSER.get('max','max')
                        textureList_long.append(max_name.strip().replace('/','\\').replace('\\','\\\\').replace('"','\\"'))
                    else:
                        textureList_long.append(itemName1.strip().replace('/','\\').replace('\\','\\\\').replace('"','\\"'))
            if len(textureList_long) > 0:
                self.TIPS_DICT[self.TIPS_CODE.MATERIAL_PATH_LONG] = textureList_long
                # self.writeExitsTips(self.TIPS_CODE.MATERIAL_PATH_LONG,textureList_long)
        #else:
        #    # self.TIPS_DICT[self.TIPS_CODE.MATERIAL_PATH_LONG] = []
        #    self.writeExitsTips(self.TIPS_CODE.MATERIAL_PATH_LONG,textureList_long)
            
    def doAsset(self):
    
        self.printLineInfo('doAsset')
        
        assetDict = {}
        sectionNameList=['phoenix','hair']
        for sectionName in sectionNameList:
            sectionList=self.getItem(sectionName)
            if sectionList!=None:
                assetDict[sectionName]= sectionList
        resultAssetDict=self.handleAsset(assetDict)
        
        assetInputSctionName='texture'
        if len(resultAssetDict):
            if self.RENDER_CFG_PARSER.has_section(assetInputSctionName):
                itemKeyList = self.RENDER_CFG_PARSER.options(assetInputSctionName)
                textureCount=len(itemKeyList)+1
            else:
                self.RENDER_CFG_PARSER.add_section(assetInputSctionName)
                textureCount=1
                
            for assetType,assetList in resultAssetDict.items():
                for asset in assetList:
                    self.RENDER_CFG_PARSER.set(assetInputSctionName, ('path' + str(textureCount)), asset)
                    textureCount = textureCount + 1 
                
        # renderCfg=os.path.join(self.TASK_TEMP_PROJECT_PATH,'render.cfg')
        if len(self.TIPS_DICT)>0:
            cfgTips='alltips'
            if not self.RENDER_CFG_PARSER.has_section(cfgTips):
                self.RENDER_CFG_PARSER.add_section(cfgTips)
            
            tipStr='{\r\n'
            
            for tipCode ,tipMsgList in self.TIPS_DICT.items():
                tipStr=tipStr+'"'+tipCode+'":'+self.listToStr(tipMsgList)+',\r\n'
                
                tipStr2=self.listToStr(tipMsgList)
                self.RENDER_CFG_PARSER.set(cfgTips, (str(tipCode)), tipStr2)
            tipStr=tipStr.strip('\r\n').strip(',')+'\r\n}'
            self.writeTips(tipStr)
            #itemList.append(cameraDuplictStr)
        else:
            tipStr='{"0":[""]}'
            self.writeTips(tipStr)
        
        #self.RENDER_CFG_PARSER.write(codecs.open(renderCfg, "w", "UTF-16-LE"))
        # self.RENDER_CFG_PARSER.write(codecs.open(renderCfg, "w", "UTF-16"))

    def writeSeperateAccount(self):
        self.printLineInfo('Write separate accout')
        #self.SEPERATE_ACCOUNT
        cfgCommon = 'common'
        if not self.RENDER_CFG_PARSER.has_section(cfgCommon):
            self.RENDER_CFG_PARSER.add_section(cfgCommon)
        self.RENDER_CFG_PARSER.set(cfgCommon, 'separateaccount', self.SEPERATE_ACCOUNT)
        
    def writeDistribute(self):
        # if self.USER_ID == '961404' and self.USER_ID == '1852991':
        self.printLineInfo('Write distribute')
        if self.PLUGIN_DICT.has_key('plugins'):
            pluginDict = self.PLUGIN_DICT['plugins']
            #if renderer is vray
            if pluginDict.has_key('vray'):
                cfgVray = 'vray'
                if not self.RENDER_CFG_PARSER.has_section(cfgVray):
                    self.RENDER_CFG_PARSER.add_section(cfgVray)
                self.RENDER_CFG_PARSER.set(cfgVray, 'distribute', 'false')
                self.RENDER_CFG_PARSER.set(cfgVray, 'distributenodecore', '48')
                # self.RENDER_CFG_PARSER.set(cfgVray, 'distributenodelist', '3:48,5:80,6:96,12:192')
                self.RENDER_CFG_PARSER.set(cfgVray, 'distributenodelist', '3:48,6:96')
        
    '''
        Write rendertype to render.cfg(e.g. rendertype=maxcmd)
    '''
    def writeRenderType(self):
    
        
        self.printLineInfo('Write rendertype')
        renderCfg = os.path.join(self.TASK_TEMP_PROJECT_PATH, 'render.cfg')
        if self.USER_ID=='1857815':
            pass
        else:
            
            if self.PLUGIN_DICT.has_key('plugins'):
                pluginDict = self.PLUGIN_DICT['plugins']
                for pluginsKey in pluginDict.keys():
                    pluginStr = pluginsKey + pluginDict[pluginsKey]
                    if pluginStr in self.MAX_CMD:
                        cfgCommon = 'common'
                        if not self.RENDER_CFG_PARSER.has_section(cfgCommon):
                            self.RENDER_CFG_PARSER.add_section(cfgCommon)
                        self.RENDER_CFG_PARSER.set(cfgCommon, 'rendertype', 'maxcmd')
                        break
                    
        self.RENDER_CFG_PARSER.write(codecs.open(renderCfg, "w", "UTF-16"))

if __name__ == '__main__':
    SubmitMax().run()


    '''
        
submit_batch_max.exe --userid="100001" --projectid="68" --projectname="worker_ljw" --cgfile="D:/NONO/rar_scene/max2012-2014复杂贴图打包/fuza.max" --pluginfile="C:/Users/Administrator/AppData/Roaming/RenderBus/Profiles/users/cust/enfuzion/pluginconf/max_worker_ljw.pl" 
if __name__ == '__main__': 
    cmdStr = '"C:/Program Files/Autodesk/3ds Max 2014/3dsmax.exe" -silent -mip  -mxs "filein \\"D:/temp/max/submit_batch_max/renderfarm_u_test.ms\\";rayvision \\"100001\\" \\"68\\" \\"worker_ljw\\" \\"D:/NONO/rar_scene/max2012-2014复杂贴图打包/fuza.max\\" \\"C:/Users/Administrator/AppData/Roaming/RenderBus/Profiles/users/cust/enfuzion/pluginconf/max_worker_ljw.pl\\" \\"default scanline renderer\\""'
    cmdStr=cmdStr.decode('utf-8').encode('gbk')
    print cmdStr
    maxCmd(cmdStr)
    '''