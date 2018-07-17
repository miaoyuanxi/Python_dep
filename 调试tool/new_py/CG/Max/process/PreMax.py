#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import time
import subprocess
import configparser
import codecs
import sys
import shutil
from distutils.version import LooseVersion, StrictVersion
# from RenderBase import RenderBase
from Max import Max
from MaxPlugin import MaxPlugin 
#update20151013\\10.50.8.15\p5\script\py\newpy\962712

import json
from CommonUtil import RBCommon as CLASS_COMMON_UTIL
from MaxUtil import RBMaxUtil as CLASS_MAX_UTIL

class RenderbusPath():
    def __init__(self,user_path):
        self.G_INPUT_USER_PATH=user_path
        

        
        

    
    def inter_path(self,p):
        first_two = p[0:2]
        if first_two == '//' or first_two == '\\\\':
            normPath = p.replace('\\', '/')
            index = normPath.find('/', 2)
            if index <= 2:
                return False
            return True
        
    def parse_inter_path(self,p):
        first_two = p[0:2]
        if first_two == '//' or first_two == '\\\\':
            normPath = p.replace('\\', '/')
            index = normPath.find('/', 2)
            if index <= 2:
                return ''
            
            return p[:index],p[index:]

    def convert_to_renderbus_path(self,item_path):

        absPath=[['a:/','/a/'],
            ['b:/','/b/'],
            ['c:/','/c/'],
            ['d:/','/d/']]
            
        result_max_file = item_path
        src_max_lowercase = os.path.normpath(item_path.lower()).replace('\\', '/')
        is_abcd_path = False
        is_inter_path = False
        
        if self.inter_path(src_max_lowercase):
            start,rest = self.parse_inter_path(src_max_lowercase)
            result_max_file= self.G_INPUT_USER_PATH + '/net' + start.replace('//', '/') + rest.replace('\\', '/') 
        else:
            result_max_file= self.G_INPUT_USER_PATH + '\\' + item_path.replace('\\', '/').replace(':','')

        return os.path.normpath(result_max_file)
        
        
    def convert_to_user_path(self,source_file):
        result_file = source_file
        user_input=self.G_INPUT_USER_PATH
        user_input=user_input.replace('/','\\')
        source_file=source_file.replace('/','\\').replace(user_input,'')
        
        if source_file.startswith('net'):
            result_file = '\\\\'+source_file[3:]
        elif source_file.startswith('a\\') or source_file.startswith('b\\') or source_file.startswith('c\\') or source_file.startswith('d\\'):
            result_file = source_file[0]+':'+source_file[1:]
        else:
            result_file=source_file[0]+':'+source_file[1:]
        
        result_file=result_file.replace('\\','/')
        return result_file
        
        
        
class PreMax(Max):

    '''
        初始化构造函数
    '''
    def __init__(self,**paramDict):
        Max.__init__(self,**paramDict)
        print('PreMax init')
        
        # self.fileCount=0

        self.MAX_PREPROCESS=False
        self.NOT_RUN_MAX=False
        self.ASSET_PROJECT_DICT={}
        
        self.MAX_ZIP_LIST=[]
  
        if os.path.exists(self.G_WORK_RENDER_TASK_MAX):
            shutil.rmtree(self.G_WORK_RENDER_TASK_MAX,onerror = CLASS_COMMON_UTIL.remove_readonly)
        # self.make_dir()
        
    def RB_CONFIG(self):#4
        self.G_DEBUG_LOG.info('[PreMax.RB_CONFIG.start.....]')
        
        # DogUtil.killMaxVray(self.G_DEBUG_LOG)  #kill 3dsmax.exe,3dsmaxcmd.exe,vrayspawner*.exe
        #self.copy_py_site_packages()        
        self.set_max_preprocess()
        self.set_vray0000()
        
        not_run_max_txt=os.path.join(self.G_MAX_SCRIPT,'user',self.G_USER_ID,'notrunmax.txt')
        if os.path.exists(not_run_max_txt):
            self.NOT_RUN_MAX = True
        print('NOT_RUN_MAX=' + str(self.NOT_RUN_MAX))
        
        # zip=os.path.join(self.G_PLUGIN_PATH,'tools','7-Zip')
        # copy_7z_cmd=r'c:\fcopy\FastCopy.exe /speed=full /force_close /no_confirm_stop /force_start "'+zip.replace('/','\\')+'" /to="c:\\"'
        # CLASS_COMMON_UTIL.cmd(copy_7z_cmd,my_log=self.G_DEBUG_LOG)   
        
        self.G_DEBUG_LOG.info('[PreMax.RB_CONFIG.end.....]')
           
    '''
        预处理任务，根据配置文件的文件，添加预处理的压缩max文件
    '''
    def RB_RENDER(self):#5
        #self.G_START_TIME = str(int(time.time()))
        #self.G_END_TIME = str(int(time.time()))
        #self.G_RENDER_LOG.info('startTime='+self.G_START_TIME)
        #self.G_RENDER_LOG.info('endTime='+self.G_END_TIME)
        # self.G_KAFKA_MESSAGE_DICT['start_time']=str(int(time.time()))
        self.G_FEE_PARSER.set('render','start_time',str(int(time.time())))
        
        net_render_txt=os.path.join(self.G_MAX_SCRIPT,'user',self.G_USER_ID,'netrender.txt').replace('\\','/')
        self.G_DEBUG_LOG.info('net_render_txt-------'+net_render_txt)
        if os.path.exists(net_render_txt):
            self.G_DEBUG_LOG.info('------Net render process--------')
            if self.G_CHANNEL == '1' or self.G_CHANNEL == '2':
                if 'max' in self.G_ASSET_JSON_DICT:                    
                    for max_file in self.G_ASSET_JSON_DICT['max']:
                        max_file = CLASS_COMMON_UTIL.bytes_to_str(max_file)
                        if os.path.exists(max_file):
                            target_path = self.G_WORK_RENDER_TASK_MAX
                            # self.G_DEBUG_LOG.info('unicode')
                            cmd_max='c:\\fcopy\\FastCopy.exe  /speed=full /force_close  /no_confirm_stop /force_start "'+max_file+'" /to="'+target_path+'"'
                            # self.G_DEBUG_LOG.info('[PreMax.copyFile.cmd_max.....]'+cmd_max.encode(sys.getfilesystemencoding()))
                            self.G_DEBUG_LOG.info('[PreMax.copyFile.cmd_max.....]'+cmd_max)
                            # CLASS_COMMON_UTIL.cmd_python3(cmd_max,my_log=self.G_DEBUG_LOG)
                            CLASS_COMMON_UTIL.cmd(cmd_max,my_log=self.G_DEBUG_LOG)
                            ##try:
                            ##    CLASS_COMMON_UTIL.cmd(cmd_max.encode(sys.getfilesystemencoding()),my_log=self.G_DEBUG_LOG)
                            ##except:
                            ##    if not os.path.exists(target_path):
                            ##        os.makedirs(target_path)
                            ##    # targetPath2=self.G_WORK_RENDER_TASK_MAX+file1[file1.rfind("\\"):]
                            ##    shutil.copy2(max_file,target_path)
                            ##    self.G_DEBUG_LOG.info('[success]retry copy:from ...... %s ...... to ...... %s ......' % (max_file,target_path))
                            self.run_max()
                            #cmd='c:/exdupe.exe -t16f '+self.G_WORK_RENDER_TASK_MAX+' '+self.G_WORK_RENDER_TASK_MAX+'.full'
                            cmd_pack=r'"'+self.G_DRIVERC_7Z+'" a -t7z "'+self.G_WORK_RENDER_TASK_MAX+'.7z" "'+self.G_WORK_RENDER_TASK_MAX+'\*"  -mmt -r'
                            self.G_DEBUG_LOG.info(cmd_pack)
                            #print cmd_max
                            CLASS_COMMON_UTIL.cmd(cmd_pack,my_log=self.G_DEBUG_LOG)
            else:
                self.G_DEBUG_LOG.info('submit from Client')
                #if self.RENDER_CFG_PARSER.has_section('texture'):
                #    texture_list=self.RENDER_CFG_PARSER.options('texture')
                #    for textureKey in texture_list:
                #        
                #        files=self.RENDER_CFG_PARSER.get('texture',textureKey)
                #        file1=(files.split('>>')[1]).replace('/','\\')
                #        if file1.endswith('.max') or file1.endswith('.max.7z'):
                #            file_dir=file1[file1.find(propath)+len(propath):file1.rfind("\\")]
                #            file_path=(self.G_INPUT_USER_PATH+file1[1:len(file1)]).replace('/','\\')
                #            self.G_DEBUG_LOG.info(file_path)
                #            if os.path.exists(file_path):
                #                target_path=self.G_WORK_RENDER_TASK_MAX.replace('/','\\')#+file_dir
                #                self.G_DEBUG_LOG.info('unicode')
                #                cmd_max=u'c:\\fcopy\\FastCopy.exe  /speed=full /force_close  /no_confirm_stop /force_start "'+file_path+'" /to="'+target_path+'"'
                #                self.G_DEBUG_LOG.info('[PreMax.copyFile.cmd_max.....]'+cmd_max.encode(sys.getfilesystemencoding()))
                #                self.RBcmd(cmd_max.encode(sys.getfilesystemencoding()))
                #                
                #                #file_path=\\10.50.241.9\d\inputdata5\1015500\1015735\d\work\HS\max\Volcano_03max_001_fumefx02_gai02_06_08.max.7z
                #                #self.G_WORK_RENDER_TASK_MAX
                #                filePath2=os.path.join(self.G_WORK_RENDER_TASK_MAX,file_path.split("\\")[-1])
                #                print self.G_WORK_RENDER_TASK_MAX
                #                print filePath2
                #                #if file1.endswith('.max.7z'):
                #                if filePath2.endswith('.max.7z'):
                #                    #max_zip_path,max_zip_name=os.path.split(file1)
                #                    max_zip_path,max_zip_name=os.path.split(filePath2)
                #                    #unpack_max_cmd=self.G_DRIVERC_7Z+' e "'+file1+'" -o"'+max_zip_path+'/" -y ' 
                #                    unpack_max_cmd=self.G_DRIVERC_7Z+' e "'+filePath2+'" -o"'+max_zip_path+'/" -y ' 
                #                    unpack_max_cmd=unpack_max_cmd.encode(sys.getfilesystemencoding())
                #                    self.RBcmd(unpack_max_cmd)
                #                    
                #                    move_to_maxbak_cmd='c:\\fcopy\\FastCopy.exe /cmd=move /speed=full /force_close  /no_confirm_stop /force_start "'+filePath2.replace('/','\\')+'" /to="'+self.G_WORK_RENDER_TASK_MAXBAK.replace('/','\\')+'"'
                #                    move_to_maxbak_cmd=move_to_maxbak_cmd.encode(sys.getfilesystemencoding())
                #                    self.RBcmd(move_to_maxbak_cmd)
                #                self.run_max()
                #                cmd_pack=r'"'+self.G_DRIVERC_7Z+'" a -t7z "'+self.G_WORK_RENDER_TASK_MAX+'.7z" "'+self.G_WORK_RENDER_TASK_MAX+'\*"  -mmt -r'
                #                self.G_DEBUG_LOG.info(cmd_pack)
                #                #print cmd_max
                #                self.RBcmd(cmd_pack)
        #                        
        #                        
        else:
            self.ifl_list=[]
            #if self.RENDER_CFG_PARSER.has_section('asset_input'):
            # if self.argsmap.has_key('from') and self.argsmap['from']=='web':
            #if self.G_TASK_JSON_DICT['miscellaneous'].has_key('sub_from') and self.G_TASK_JSON_DICT['miscellaneous']['sub_from'] == 'web':
            if self.G_CHANNEL == '1' or self.G_CHANNEL == '2':
                self.copy_file_web()
            else:
                self.copy_file2()
            self.unpack_max7z()
            self.handle_ifl()
            self.run_max()
            self.pack_file2()
            
        # self.G_KAFKA_MESSAGE_DICT['end_time']=str(int(time.time()))
        self.G_FEE_PARSER.set('render','end_time',str(int(time.time())))
           
    def check_file_code(self,my_file):
        # print(my_file)
        if os.path.exists(my_file):
            f = open(my_file,'r')
            f_encoding=self.chardet.detect(f.read())
            f.close()
            print(f_encoding)
            print(f_encoding['encoding'])
            return f_encoding['encoding']
    
    def get_max_file(self,source_max_file):
        if self.G_CHANNEL == '1' or self.G_CHANNEL == '2':
            return self.get_max_file_web(source_max_file)
        else:
            return self.get_max_file_client(source_max_file)
            
        
    def inter_path(self,p):
        first_two = p[0:2]
        if first_two == '//' or first_two == '\\\\':
            normPath = p.replace('\\', '/')
            index = normPath.find('/', 2)
            if index <= 2:
                return False
            return True
            
    def get_max_file_web(self,source_max_file):
        self.G_DEBUG_LOG.info('\r\n\r\n\r\n-----------[-get_max_file_web-]--------------\r\n\r\n\r\n')
        
        if self.ASSET_WEB_COOLECT_BY_PATH:
            result_max_file = source_max_file
            user_input=self.G_INPUT_USER_PATH
            user_input=user_input.replace('/','\\')
            source_max_file=source_max_file.replace('/','\\').replace(user_input,'')
            
            self.G_DEBUG_LOG.info(source_max_file)
            if source_max_file.startswith('__'):
                result_max_file = self.G_WORK_RENDER_TASK_MAX+'/'+source_max_file
            elif source_max_file.startswith('a') or source_max_file.startswith('b') or source_max_file.startswith('c') or source_max_file.startswith('d'):
                result_max_file = self.G_WORK_RENDER_TASK_MAX+'/'+source_max_file
            else:
                result_max_file=source_max_file[0]+':'+source_max_file[1:]
            
            result_max_file=result_max_file.replace('\\','/')
            self.G_DEBUG_LOG.info(result_max_file)
            return result_max_file
        else:
            result_max_file = self.G_WORK_RENDER_TASK_MAX+'/'+os.path.basename(source_max_file)
            return result_max_file
        
    def get_max_file_client(self,source_max_file):
        self.G_DEBUG_LOG.info('-----get_max_file_client-----')
        self.G_DEBUG_LOG.info(source_max_file)
        net_render_txt=os.path.join(self.G_MAX_SCRIPT,'user',self.G_USER_ID,'netrender.txt').replace('\\','/')
        self.G_DEBUG_LOG.info(net_render_txt)
        if  os.path.exists(net_render_txt):
            self.G_DEBUG_LOG.info('net render')
            cgFileName=os.path.basename(source_max_file)
            cg_file=os.path.join(self.G_WORK_RENDER_TASK_MAX,cgFileName).replace('\\','/')
            self.G_DEBUG_LOG.info(cg_file)
            return cg_file
        return source_max_file
        
    def getMaxFileClient_bak20170719(self,source_max_file):
        self.G_DEBUG_LOG.info('-----get_max_file_client-----')
        self.G_DEBUG_LOG.info(source_max_file)
        net_render_txt=os.path.join(self.G_MAX_SCRIPT,'user',self.G_USER_ID,'netrender.txt').replace('\\','/')
        self.G_DEBUG_LOG.info(net_render_txt)
        if  os.path.exists(net_render_txt):
            self.G_DEBUG_LOG.info('net render')
            cgFileName=os.path.basename(source_max_file)
            cg_file=os.path.join(self.G_WORK_RENDER_TASK_MAX,cgFileName).replace('\\','/')
            self.G_DEBUG_LOG.info(cg_file)
            return cg_file
            
        absPath=[['a:/','/a/'],
            ['b:/','/b/'],
            ['c:/','/c/'],
            ['d:/','/d/']]
            
        result_max_file = source_max_file
        src_max_lowercase = os.path.normpath(source_max_file.lower()).replace('\\', '/')
        is_abcd_path = False
        is_inter_path = False
       
        for prefix in absPath:
            if src_max_lowercase.startswith(prefix[0]):
                is_abcd_path = True
                result_max_file = self.G_WORK_RENDER_TASK_MAX + src_max_lowercase.replace(prefix[0], prefix[1])
                break
            
        if not is_abcd_path:
            if self.inter_path(src_max_lowercase):
                start,rest = self.parse_inter_path(src_max_lowercase)
                result_max_file= self.G_WORK_RENDER_TASK_MAX + '/net' + start.replace('//', '/') + rest.replace('\\', '/') 
            else:
                result_max_file= source_max_file.replace('\\', '/') 

        return os.path.normpath(result_max_file)

        
    def writeMsFile(self,msFile,sceneFile):

        msFileObject=codecs.open(msFile,'w',"utf-8")
        scriptMsName='processU.ms'
        json_file = self.G_TASK_JSON
        if self.G_CG_VERSION=='3ds Max 2012' or self.G_CG_VERSION=='3ds Max 2011' or self.G_CG_VERSION=='3ds Max 2010' or self.G_CG_VERSION=='3ds Max 2009':
            #msFileObject=codecs.open(msFile,'w',"gbk")
            msFileObject=codecs.open(msFile,'w',sys.getfilesystemencoding())
            scriptMsName='processA.ms'
            json_file = self.G_TASK_JSON_A
            
            
        msScript=self.G_NODE_MAXSCRIPT+'/'+scriptMsName
        msFileObject.write('(DotNetClass "System.Windows.Forms.Application").CurrentCulture = dotnetObject "System.Globalization.CultureInfo" "zh-cn"\r\n')
        msFileObject.write('filein @"'+msScript+'"\r\n')
        
        subFrom='client'
        # if self.argsmap.has_key('from') and self.argsmap['from']=='web':
        #if self.G_TASK_JSON_DICT['miscellaneous'].has_key('sub_from') and self.G_TASK_JSON_DICT['miscellaneous']['sub_from'] == 'web':
        if self.G_CHANNEL == '1' or self.G_CHANNEL == '2':
            # myCamera= self.RENDER_CFG_PARSER.get('common','renderablecamera')
            # myCamera = self.G_TASK_JSON_DICT['scene_info_render']['common']['renderable_camera']
            subFrom='web'
        else:
            subFrom='client'
            # myCamera=myCamera = self.G_TASK_JSON_DICT['scene_info_render']['common']['renderable_camera']
            # myCamera= self.RENDER_CFG_PARSER.get('renderSettings','renderablecamera')
            # if self.RENDER_CFG_PARSER.has_option('renderSettings','renderablecameras'):
                # renderableCameraStr = self.RENDER_CFG_PARSER.get('renderSettings','renderablecameras')
                # myCamera=self.G_CG_OPTION
        clientArrayStr= '#("'+self.G_USER_ID+'","'+self.G_USER_ID_PARENT+'","'+self.G_TASK_ID+'","'
        clientArrayStr=clientArrayStr+self.G_ACTION_ID+'","'+sceneFile+'","'+self.G_PLATFORM+'","'+self.G_CG_OPTION+'","'+subFrom+'","'+json_file.replace('\\','/')+'","'+self.G_KG+'")\r\n'
        mystr='doFN '+clientArrayStr#+self.G_USER_ID+'" "'+self.G_TASK_ID+'" "'+notRender+'" "'+renderFrame+'" "'+self.G_CG_TILE+'" "'+self.G_CG_TILE_COUNT+'" "'+self.G_KG+'" "'+self.G_ACTION_ID+'"  "'+renderOutput+'/" '+arrayStr+' "'+self.CURRENT_TASK+'"\r\n'

        msFileObject.write(mystr)
        msFileObject.close()
        self.G_DEBUG_LOG.info('[Max.writeMsFile.end.....]')
        return msFile
        
    def run_max(self):
        if self.MAX_PREPROCESS:
            if not self.NOT_RUN_MAX:
                #self.subst_path()      
                self.G_DEBUG_LOG.info(self.G_CG_VERSION)
                max_plugin=MaxPlugin(self.G_CG_CONFIG_DICT,self.G_DEBUG_LOG)
                max_plugin.config()
                
                self.customer_3dsmax_ini()
                
                ms_file=os.path.join(self.G_WORK_RENDER_TASK_CFG,'preproces.ms').replace('\\','/')
                cg_file = self.G_INPUT_CG_FILE
                self.MAX_FILE=self.get_max_file(cg_file)
                
                #max2File=os.path.join(self.G_WORK_RENDER_TASK_MAX2,os.path.basename(self.MAX_FILE))
                #max2File2=os.path.join(self.G_WORK_RENDER_TASK_MAX2,(self.G_TASK_ID+'.max'))
                #self.G_DEBUG_LOG.info(max2File)
                #self.G_DEBUG_LOG.info(max2File2)
                self.G_DEBUG_LOG.info(cg_file)
                self.G_DEBUG_LOG.info(self.MAX_FILE)
                #os.rename(max2File,max2File2)
                #self.writeMsFile(ms_file,max2File2.replace('\\','/'))
                self.writeMsFile(ms_file,self.MAX_FILE.replace('\\','/'))
                # self.writeMsFile(ms_file,cg_file.replace('\\','/'))
                
                maxExe =  'C:/Program Files/Autodesk/'+self.G_CG_VERSION+'/3dsmax.exe'
                preCmd = '"'+maxExe +'" -silent  -U MAXScript "'+ms_file+'"'
                # preCmd = preCmd.encode(sys.getfilesystemencoding())
                # print(preCmd)
                #DogUtil.maxCmd(preCmd,self.G_DEBUG_LOG)
                CLASS_COMMON_UTIL.cmd(preCmd,my_log=self.G_DEBUG_LOG,continue_on_error=True,my_shell=True,callback_func=CLASS_MAX_UTIL.max_cmd_callback)
                #DogUtil.runCmd(preCmd)
            else:
                cg_file = self.G_INPUT_CG_FILE               
                cg_file_dirname = os.path.dirname(cg_file)
                cg_file_basename = os.path.basename(cg_file)
                if self.G_CHANNEL == '1' or self.G_CHANNEL == '2':
                    max_file_node = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK_MAX,cg_file_basename))
                    max_file_node_new = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK_MAX,(self.G_TASK_ID+'.max')))
                # else:
                    # max_file_node = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK_MAX,cg_file.replace(':','')))
                    # max_file_node_new = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK_MAX,cg_file_dirname.replace(':',''),(self.G_TASK_ID+'.max')))
                #rename max file
                os.rename(max_file_node,max_file_node_new)

            
    '''
        读文件
    '''
    def readFile(self,path):
        if os.path.exists(path):
            fileObject=open(path)
            line=fileObject.readlines()
            # for r in line:
                # print(r)
            fileObject.close()
            return line
        pass

    '''
        读文件
    '''
    def readFileByCode(self,path,code):
        if os.path.exists(path):
                    
            fileObj=codecs.open(path,'r',code)
            lines=fileObj.readlines()
            fileObj.close()
            return lines
        pass

    
    def writeFile(self,file_path,list,code):
        fileObject=codecs.open(file_path,'w',code)
        for line in list :
            fileObject.write(line)
        fileObject.close()
        
    def convertStr2Unicode(self,str):
        if not isinstance(str, str):
            str=str.decode(sys.getfilesystemencoding())
        return str
        
            
    def convertIfl(self,sourceIfl,targetIfl):

        # print('targetIfl=',targetIfl)
        # print('sourceIfl=',sourceIfl)
        
        if os.path.exists(targetIfl):
            os.remove(targetIfl)
        
        #read_cfg_fleObj=codecs.open(v,'r',encoding=sys.getfilesystemencoding())

        sourceObj=codecs.open(sourceIfl,'r')
        sourceResult=sourceObj.read()
        targetObj=codecs.open(targetIfl,'a','UTF-8')
        try:
            sourceResult2=sourceResult.decode('gbk')#.decode('utf-8')
        except Exception as e:
            try:
                sourceResult2=sourceResult.decode('utf-8')
            except Exception as e:
                print('exception...')
        targetObj.write(sourceResult2)
        sourceObj.close()
        
        targetObj.close()
        
    def handle_ifl(self):
        self.G_DEBUG_LOG.info('[[PreMax.handle_ifl.start.....]')
        for ifl in self.ifl_list:
            self.G_DEBUG_LOG.info(ifl)
            fileCode=self.check_file_code(ifl)
            iflbak=ifl+'.bak'
            os.rename(ifl,iflbak)
            
            if fileCode=='EUC-TW':
                fileCode='gb2312'
            try:
                imgList=self.readFileByCode(iflbak,fileCode)
            except Exception as e:
                print('exception...'+fileCode)
                fileCode='gb2312'
                imgList=self.readFileByCode(iflbak,fileCode)
                          
            imgBasenameList=[]
            if imgList:
                for img in imgList:
                    imgBasename=os.path.basename(img)
                    self.G_DEBUG_LOG.info(img+'......'+imgBasename)
                    imgBasenameList.append(imgBasename)
                    self.writeFile(ifl,imgBasenameList,fileCode)
        self.G_DEBUG_LOG.info('[[PreMax.handle_ifl.end.....]')
        
    def handle_ifl_bakutf(self):
        self.G_DEBUG_LOG.info('[[PreMax.IFL.start.....]')
        for ifl in self.ifl_list:
        
            self.G_DEBUG_LOG.info(ifl)
            ifl2=ifl+'.utf'
            if os.path.exists(ifl):
            
                self.convertIfl(ifl,ifl2)
                os.rename(ifl,ifl+'.bak')
                
                self.G_DEBUG_LOG.info(ifl2)
                #shutil.copyfile(ifl,ifl+'.bak')
                
                imgList=self.readFile2(ifl2)
                imgBasenameList=[]
                for img in imgList:
                    
                    imgBasename=os.path.basename(img)
                    self.G_DEBUG_LOG.info(img+'......'+imgBasename)
                    imgBasenameList.append(imgBasename)
                    self.writeFile(ifl,imgBasenameList,'utf-8')
                
    def unpack_max7z(self):
        self.G_DEBUG_LOG.info('[[PreMax.unpack_max7z.start.....]')
        if self.MAX_ZIP_LIST:
            for max_zip in self.MAX_ZIP_LIST:
                self.G_DEBUG_LOG.info(max_zip)
                if os.path.exists(max_zip):
                    max_zip_path,max_zip_name=os.path.split(max_zip)
                    unpack_max_cmd=self.G_DRIVERC_7Z+' e "'+max_zip+'" -o"'+max_zip_path+'/" -y ' 
                    # if self.MAX_PREPROCESS:
                        # if not os.path.exists(self.G_WORK_RENDER_TASK_MAX2):
                            # os.makedirs(self.G_WORK_RENDER_TASK_MAX2)
                        #unpack_max_cmd=self.G_DRIVERC_7Z+' e "'+max_zip+'" -o"'+self.G_WORK_RENDER_TASK_MAX2+'/" -y ' 
                    #unpack_max_cmd=unpack_max_cmd.encode(sys.getfilesystemencoding())
                    CLASS_COMMON_UTIL.cmd(unpack_max_cmd,my_log=self.G_DEBUG_LOG)
                    # CLASS_COMMON_UTIL.cmd_python3(unpack_max_cmd,my_log=self.G_DEBUG_LOG)
                    
                    
                    
                    move_to_maxbak_cmd='c:\\fcopy\\FastCopy.exe /cmd=move /speed=full /force_close  /no_confirm_stop /force_start "'+max_zip.replace('/','\\')+'" /to="'+self.G_WORK_RENDER_TASK_MAXBAK.replace('/','\\')+'"'
                    # move_to_maxbak_cmd=move_to_maxbak_cmd.encode(sys.getfilesystemencoding())
                    CLASS_COMMON_UTIL.cmd(move_to_maxbak_cmd,my_log=self.G_DEBUG_LOG)
                    # CLASS_COMMON_UTIL.cmd_python3(move_to_maxbak_cmd,my_log=self.G_DEBUG_LOG)
                else:
                    self.G_DEBUG_LOG.info('max.7z missing!!!')
                
        self.G_DEBUG_LOG.info('[[PreMax.unpack_max7z.end.....]')
        
        
    def pack_file2(self):
        self.G_DEBUG_LOG.info('[[PreMax.pack_file2.start.....]')
        
        pack_max_folder=self.G_WORK_RENDER_TASK_MAX
        self.G_DEBUG_LOG.info(pack_max_folder)
        if os.path.exists(pack_max_folder):            
            #cmd_max='c:/exdupe.exe -t16f '+self.G_WORK_RENDER_TASK_MAX+' '+self.G_WORK_RENDER_TASK_MAX+'.full'
            cmd_7z=r'"'+self.G_DRIVERC_7Z+'" a -t7z "'+self.G_WORK_RENDER_TASK_MAX+'.7z" "'+pack_max_folder+'\*"  -mmt -r'
            CLASS_COMMON_UTIL.cmd(cmd_7z,my_log=self.G_DEBUG_LOG)
            
        self.G_DEBUG_LOG.info('[PreMax.pack_file2.end....]')

    #def GetFileList(self,file_list,propath):
    #    projectPath=(self.G_INPUT_USER_PATH+propath).replace('/','\\')
    #    self.G_DEBUG_LOG.info('[[--------project file list------]')
    #    self.G_DEBUG_LOG.info('[[PreMax.projectPath.....]'+projectPath)
    #    sample_list=[]
    #    for parent,dirnames,filenames in os.walk(projectPath):    #三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
    #        for filename in filenames:                        #输出文件信息
    #            ff=os.path.join(parent,filename).decode('gbk')
    #            sample_list.append(ff)
    #            self.G_DEBUG_LOG.info(ff)
    #            #self.G_DEBUG_LOG.info(type(ff))
    #            
    #    # pretxt=self.G_HELPER+self.G_TASK_ID
    #    pretxt=self.G_WORK_RENDER_TASK
    #
    #    if os.path.exists(pretxt):
    #        pass
    #    else:
    #        os.makedirs(pretxt)
    #    fh = open(pretxt+"\\pretxt.txt", 'w')
    #    notExistFileList=[]
    #    for files in file_list:
    #        #self.G_DEBUG_LOG.info(type(files))
    #        file1=(files.split('>>')[1]).replace('/','\\')
    #        if file1=="":
    #            self.G_DEBUG_LOG.info('files----'+files+"---false")
    #            sys.exit(-1)                  
    #        file_path=(self.G_INPUT_USER_PATH+file1[1:len(file1)]).replace('/','\\')
    #        isExists=0
    #        if self.is_out_file(file_path):
    #            self.G_DEBUG_LOG.info('[PreMax.isRENDER_OUTPUT_FILENAME]'+file_path.encode(sys.getfilesystemencoding())+"--pass")
    #            continue
    #        if os.path.exists(file_path):
    #            #self.G_DEBUG_LOG.info('[[PreMax.packFile.renderFilePath.....]'+file1.encode('gbk'))
    #            fh.write(file_path+"\r\n") 
    #            self.fileCount=self.fileCount+1
    #            isExists=1
    #        else:
    #            #self.G_DEBUG_LOG.info('[[PreMax.packFile.checkProFileName-----]'+file1.encode('gbk'))
    #            filename=file_path[file_path.rfind("\\")+1:len(file_path)]
    #            for profilepath in sample_list:
    #                #self.G_DEBUG_LOG.info('[[PreMax.packFile.file_name.....]'+profilepath)
    #                profilename=profilepath[profilepath.rfind("\\")+1:len(profilepath)]
    #                if profilename.lower()==filename.lower():
    #                    fh.write(profilepath+"\r\n")
    #                    self.fileCount=self.fileCount+1
    #                    isExists=1
    #        if isExists==0:
    #            notExistFileList.append(file1.encode('gbk'))
    #            #self.G_DEBUG_LOG.info('[[PreMax.packFile.file.....]'+file_path.encode('utf-8')+'...[not  exists]')
    #        else:
    #            self.G_DEBUG_LOG.info('[[PreMax.packFile.file.....]'+file1.encode('gbk')+'...[exists]')
    #    if len(notExistFileList)>0:
    #        for f in notExistFileList:
    #            self.G_DEBUG_LOG.info('[[PreMax.packFile.file.....]'+f+'...[not  exists]')
    #        return '-1'
    #
    #    fh.close()
    #    return pretxt+"\\pretxt.txt"

    #RENDER_OUTPUT_FILENAME
    #def RB_GET_OUT_FILE_NAME(self):
    #    self.RENDER_OUTPUT_FILENAME = ''
    #    # if self.RENDER_CFG_PARSER.has_option('renderSettings','RENDER_OUTPUT_FILENAME'):
    #        # self.RENDER_OUTPUT_FILENAME = self.RENDER_CFG_PARSER.get('renderSettings','RENDER_OUTPUT_FILENAME')
    #    if self.G_TASK_JSON_DICT['scene_info_render']['common'].has_key('output_file'):
    #        self.RENDER_OUTPUT_FILENAME = os.path.normpath(self.G_TASK_JSON_DICT['scene_info_render']['common']["output_file"])
    #        self.G_DEBUG_LOG.info('[PreMax.RENDER_OUTPUT_FILENAME......]'+self.RENDER_OUTPUT_FILENAME)
        

    def is_out_file(self,file_path):
        
        if 'output_file' in self.G_TASK_JSON_DICT['scene_info_render']['common']:
            render_output_filename = os.path.normpath(self.G_TASK_JSON_DICT['scene_info_render']['common']["output_file"])
            self.G_DEBUG_LOG.info('[PreMax.render_output_filename......]'+self.render_output_filename)
            
        if render_output_filename=='':
            return False
        if file_path.endswith(render_output_filename):
            return True
        return False

        
    
    def getAnimationVrmap(self,file_list,animation_file):
        # print(animation_file)
        animation_path=os.path.dirname(animation_file)
        # print(animation_path)
        if os.path.exists(animation_path):
            animation_filename=os.path.basename(animation_file)
            animation_basename,animationType=os.path.splitext(animation_filename)
            # print(animation_basename)
            animation_list=os.listdir(animation_path)
            for animation_file2 in animation_list:
                if animation_file2.endswith('.vrmap'):
                    animation_basename2=os.path.basename(animation_file2)
                    if animation_basename2.startswith(animation_basename):
                        # print(animation_file2)
                        file_list.append(os.path.join(animation_path,animation_file2))
            
    
    def copy_file_web(self):
        if self.ASSET_WEB_COOLECT_BY_PATH:
            self.copy_file_web_by_path()
        else:
            self.copy_file_web_by_name()
        
    def copy_file_web_by_path(self):
        self.G_DEBUG_LOG.info('[PreMax.copy_file_web_by_path.start.....]')
        file_list=[]
        
        # propath= self.G_USER_ID_PARENT+"\\"+self.G_USER_ID
        user_input=self.G_INPUT_USER_PATH.replace('/','\\')
        self.G_DEBUG_LOG.info('[[PreMax.copy_file_web_by_path.user_input.....]'+user_input)
        
        if 'asset_input_server' in self.G_ASSET_JSON_DICT:
            for asset in self.G_ASSET_JSON_DICT['asset_input_server']:
                asset = CLASS_COMMON_UTIL.bytes_to_str(asset)
                if os.path.exists(asset):
                    file_list.append(asset)
                else:
                    CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG,'[err]PreMax.copy_file_web_by_path: %s is not exist!!!' % asset)
                    
        #if self.G_ASSET_JSON_DICT.has_key('asset_input'):
        #    asset_list=self.G_ASSET_JSON_DICT['asset_input']
        #    for asset_file in asset_list:
        #        if asset_file.endswith('.vrmap') or  asset_file.endswith('.vrlmap'):
        #            continue
        #        file_list.append(asset_file)
                
        if 'max' in self.G_ASSET_JSON_DICT:
            max_list=self.G_ASSET_JSON_DICT['max']
            for max_path in max_list:
                max_path = CLASS_COMMON_UTIL.bytes_to_str(max_path)
                if os.path.exists(max_path):
                    file_list.append(max_path)
                else:
                    CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG,'[err]PreMax.copy_file_web_by_path: %s is not exist!!!' % max_path)        
        
        #---------------------------render.cfg vrmap vrlmap-------------
        if 'gi' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['gi']=='1':
            if 'primary_gi_engine' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['primary_gi_engine']=='0':
                #--------------------------Irradiance map_____from file--------------------------
                if 'irradiance_map_mode' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['irradiance_map_mode']=='2':
                    print('irrmapmode from file')
                    irrmapFile = self.G_TASK_JSON_DICT['scene_info_render']['renderer']['irrmap_file']
                    irrmapFile = self.relative_to_absolute(irrmapFile)
                    # file_list.append(self.RENDERBUS_PATH.convert_to_renderbus_path(irrmapFile))
                    file_list.append(irrmapFile)
                #--------------------------Irradiance map_____Animation(rendering)--------------------------
                if 'irradiance_map_mode' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['irradiance_map_mode']=='7':
                    print('irrmapmode animation (rendering)')
                    animation_file=self.G_TASK_JSON_DICT['scene_info_render']['renderer']['irrmap_file']
                    animation_file = self.relative_to_absolute(animation_file)
                    # animation_file=self.RENDERBUS_PATH.convert_to_renderbus_path(animation_file)
                    self.getAnimationVrmap(file_list,animation_file)
                    
            elif 'primary_gi_engine' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['primary_gi_engine']=='3':
            
                #--------------------------Light cache_____from file--------------------------
                if 'light_cache_mode' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['light_cache_mode']=='2':
                    print('light cache from file')
                    light_cache_file = self.G_TASK_JSON_DICT['scene_info_render']['renderer']['light_cache_file']
                    light_cache_file = self.relative_to_absolute(light_cache_file)
                    # file_list.append(self.RENDERBUS_PATH.convert_to_renderbus_path(light_cache_file))
                    file_list.append(light_cache_file)
            
            #--------------------------Light cache_____from file--------------------------        
            if 'secondary_gi_engine' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['secondary_gi_engine']=='3':
                if 'light_cache_mode' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['light_cache_mode']=='2':
                    print('light cache from file')
                    light_cache_file = self.G_TASK_JSON_DICT['scene_info_render']['renderer']['light_cache_file']
                    light_cache_file = self.relative_to_absolute(light_cache_file)
                    # file_list.append(self.RENDERBUS_PATH.convert_to_renderbus_path(light_cache_file))
                    file_list.append(light_cache_file)
        
        if file_list:            
            for files in file_list:                
                if self.is_out_file(files):
                    # self.G_DEBUG_LOG.info('[PreMax.copy_file_web_by_path.is_out_file]'+files.encode(sys.getfilesystemencoding())+"--pass")
                    self.G_DEBUG_LOG.info('[PreMax.copy_file_web_by_path.is_out_file]'+files+"--pass")
                    continue                    
                files=files.replace('/','\\')                
                if os.path.exists(files):
                    target_path=self.G_WORK_RENDER_TASK_MAX.replace('/','\\')+os.path.dirname(files).replace(user_input,'')
                    # self.G_DEBUG_LOG.info('unicode')
                    cmd_copy='c:\\fcopy\\FastCopy.exe  /speed=full /force_close  /no_confirm_stop /force_start "'+files+'" /to="'+target_path+'"'
                    # self.G_DEBUG_LOG.info('[PreMax.copy_file_web_by_path.cmd.....]'+cmd_copy.encode(sys.getfilesystemencoding()))
                    self.G_DEBUG_LOG.info('[PreMax.copy_file_web_by_path.cmd.....]'+cmd_copy)
                    # CLASS_COMMON_UTIL.cmd_python3(cmd_copy,my_log=self.G_DEBUG_LOG)
                    CLASS_COMMON_UTIL.cmd(cmd_copy,my_log=self.G_DEBUG_LOG)
                    ##try:
                    ##    CLASS_COMMON_UTIL.cmd(cmd_copy.encode(sys.getfilesystemencoding()),my_log=self.G_DEBUG_LOG)
                    ##except:
                    ##    if not os.path.exists(target_path):
                    ##        os.makedirs(target_path)
                    ##    # target_path2=target_path+files[files.rfind("\\"):]
                    ##    shutil.copy2(files,target_path)
                    ##    self.G_DEBUG_LOG.info('[success]retry copy:from ...... %s ...... to ...... %s ......' % (files,target_path))
                        
                    if files.endswith('.max.7z'):
                        max_zip_name=os.path.basename(files)
                        max_zip=os.path.join(target_path,max_zip_name)
                        self.MAX_ZIP_LIST.append(max_zip.replace('\\','/'))
                        
                else:
                    # self.G_DEBUG_LOG.info('[PreMax.copy_file_web_by_path.files.....]'+files.encode(sys.getfilesystemencoding())+"[not exists]")
                    self.G_DEBUG_LOG.info('[PreMax.copy_file_web_by_path.files.....]'+files+"[not exists]")
                    #sys.exit(-1)
                    #break                
                    
        self.G_DEBUG_LOG.info('[PreMax.copy_file_web_by_path.end.....]')
        
    def loop_input_asset(self):
        print('\r\n\r\n\r\n----------loop user input--------')
        #listDirs = os.walk(os.path.dirname(self.G_INPUT_CG_FILE))
        list_dirs = os.walk(self.G_INPUT_PROJECT_PATH) 
        for root, dirs, files in list_dirs: 
            for f in files: 
                # print(f,os.path.join(root, f))
                self.ASSET_PROJECT_DICT[f]=os.path.join(root,f)
                    
    def copy_file_web_by_name(self):
        self.G_DEBUG_LOG.info('[PreMax.copy_file_web_by_name.start.....]')
        file_list=[]
        
        # propath= self.G_USER_ID_PARENT+"\\"+self.G_USER_ID
        # user_input=self.G_INPUT_USER_PATH.replace('/','\\')+propath
        user_input = self.G_INPUT_USER_PATH
        self.G_DEBUG_LOG.info('[[PreMax.copy_file_web_by_name.user_input.....]'+user_input)
        
        #---------------------------------asset_input---------------------------------
        asset_input_list=[]
        if 'asset_input_server' in self.G_ASSET_JSON_DICT:
            for asset in self.G_ASSET_JSON_DICT['asset_input_server']:
                asset = CLASS_COMMON_UTIL.bytes_to_str(asset)
                if os.path.exists(asset):
                    asset_input_list.append(asset)
                else:
                    CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG,'[err]PreMax.copy_file_web_by_name: %s is not exist!!!' % asset)
        
        # self.loop_input_asset()
        # input_dir_list=self.ASSET_PROJECT_DICT.keys()
        # if self.G_ASSET_JSON_DICT.has_key('asset_input'):
            # loop_input_key_list=self.G_ASSET_JSON_DICT['asset_input']
            # for asset_file in loop_input_key_list:
                # if asset_file.endswith('.vrmap') or  asset_file.endswith('.vrlmap'):
                    # continue
                # if self.is_out_file(asset_file):
                    # self.G_DEBUG_LOG.info('[PreMax.copy_file_web_by_name.is_out_file]'+asset_file.encode(sys.getfilesystemencoding())+"--pass")
                    # continue
                
                # asset_file_name=os.path.basename(asset_file)
                # if asset_file_name in input_dir_list:
                    # asset_input_file=self.ASSET_PROJECT_DICT[asset_file_name]
                    # asset_input_list.append(asset_input_file)
                # else:
                    # self.G_DEBUG_LOG.info('[PreMax.copy_file_web_by_name.files.....]'+asset_file.encode(sys.getfilesystemencoding())+"[not exists]")
                    
        #---------------------------------max---------------------------------
        if 'max' in self.G_ASSET_JSON_DICT:
            max_list=self.G_ASSET_JSON_DICT['max']
            for max_path in max_list:
                max_path = CLASS_COMMON_UTIL.bytes_to_str(max_path)
                if os.path.exists(max_path):
                    file_list.append(max_path)
                else:
                    CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG,'[err]PreMax.copy_file_web_by_name: %s is not exist!!!' % max_path)
        
        ##---------------------------------realflow---------------------------------
        ## if self.RENDER_CFG_PARSER.has_section('realflow'):
        #if self.G_ASSET_JSON_DICT.has_key('realflow'):
        #   self.G_DEBUG_LOG.info('............realflow..............')
        #   realflow_list=self.G_ASSET_JSON_DICT['realflow']
        #   for realflow_str in realflow_list:
        #       splited_array = realflow_str.split('|')
        #       start_frame  = splited_array[0]
        #       end_frame    = splited_array[1]
        #       padding_size = splited_array[2] 
        #       format      = splited_array[3]
        #       base_dir     = splited_array[4]
        #       prefix      = splited_array[5]
        #       # build sequence number
        #       start = int(start_frame);
        #       end   = int(end_frame);
        #       file_name =  format.replace('#', '').replace('name', prefix).replace('ext', '') .replace('.', '') 
        #       self.G_DEBUG_LOG.info(file_name)
        #       for input_file in input_dir_list:
        #           if input_file.endswith('.bin') and file_name in input_file:
        #               self.G_DEBUG_LOG.info(input_file)
        #               asset_input_file=self.ASSET_PROJECT_DICT[input_file]
        #               asset_input_list.append(asset_input_file)
        #       file_list.append(realflow_str)
                
        
        #---------------------------render.cfg vrmap vrlmap-------------
        if 'gi' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['gi']=='1':
            if 'primary_gi_engine' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['primary_gi_engine']=='0':
                #--------------------------Irradiance map_____from file--------------------------
                if 'irradiance_map_mode' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['irradiance_map_mode']=='2':
                    print('irrmapmode from file')
                    irrmapFile = self.G_TASK_JSON_DICT['scene_info_render']['renderer']['irrmap_file']
                    irrmapFile = self.relative_to_absolute(irrmapFile)
                    # file_list.append(self.RENDERBUS_PATH.convert_to_renderbus_path(irrmapFile))
                    file_list.append(irrmapFile)
                #--------------------------Irradiance map_____Animation(rendering)--------------------------
                elif 'irradiance_map_mode' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['irradiance_map_mode']=='7':
                    print('irrmapmode animation (rendering)')
                    animation_file = self.G_TASK_JSON_DICT['scene_info_render']['renderer']['irrmap_file']
                    animation_file = self.relative_to_absolute(animation_file)
                    # animation_file=self.RENDERBUS_PATH.convert_to_renderbus_path(animation_file)
                    self.getAnimationVrmap(file_list,animation_file)
                    
            elif 'primary_gi_engine' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['primary_gi_engine']=='3':
            
                #--------------------------Light cache_____from file--------------------------
                if 'light_cache_mode' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['light_cache_mode']=='2':
                    print('light cache from file')
                    light_cache_file = self.G_TASK_JSON_DICT['scene_info_render']['renderer']['light_cache_file']
                    light_cache_file = self.relative_to_absolute(light_cache_file)
                    # file_list.append(self.RENDERBUS_PATH.convert_to_renderbus_path(light_cache_file))
                    file_list.append(light_cache_file)
            
            #--------------------------Light cache_____from file--------------------------        
            if 'secondary_gi_engine' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['secondary_gi_engine']=='3':
                if 'light_cache_mode' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['light_cache_mode']=='2':
                    print('light cache from file')
                    light_cache_file = self.G_TASK_JSON_DICT['scene_info_render']['renderer']['light_cache_file']
                    light_cache_file = self.relative_to_absolute(light_cache_file)
                    # file_list.append(self.RENDERBUS_PATH.convert_to_renderbus_path(light_cache_file))
                    file_list.append(light_cache_file)
        
        
        for files in asset_input_list:
            files=files.replace('/','\\')
            target_path=self.G_WORK_RENDER_TASK_MAX.replace('/','\\')
            # self.G_DEBUG_LOG.info('unicode')
            cmd_copy='c:\\fcopy\\FastCopy.exe  /speed=full /force_close  /no_confirm_stop /force_start "'+files+'" /to="'+target_path+'"'
            # self.G_DEBUG_LOG.info('[PreMax.copy_file_web_by_name.cmd.....]'+cmd_copy.encode(sys.getfilesystemencoding()))
            self.G_DEBUG_LOG.info('[PreMax.copy_file_web_by_name.cmd.....]'+cmd_copy)
            # CLASS_COMMON_UTIL.cmd_python3(cmd_copy,my_log=self.G_DEBUG_LOG)
            CLASS_COMMON_UTIL.cmd(cmd_copy,my_log=self.G_DEBUG_LOG)
            ##try:
            ##    CLASS_COMMON_UTIL.cmd(cmd_copy.encode(sys.getfilesystemencoding()),my_log=self.G_DEBUG_LOG)
            ##except:
            ##    if not os.path.exists(target_path):
            ##        os.makedirs(target_path)
            ##    # target_path2=target_path+files[files.rfind("\\"):]
            ##    shutil.copy2(files,target_path)
            ##    self.G_DEBUG_LOG.info('[success]retry copy:from ...... %s ...... to ...... %s ......' % (files,target_path))
            
                
        for files in file_list:                
            files=files.replace('/','\\')            
            if os.path.exists(files):
                target_path=self.G_WORK_RENDER_TASK_MAX.replace('/','\\')
                # self.G_DEBUG_LOG.info('unicode')
                cmd_copy='c:\\fcopy\\FastCopy.exe  /speed=full /force_close  /no_confirm_stop /force_start "'+files+'" /to="'+target_path+'"'
                self.G_DEBUG_LOG.info('[PreMax.copy_file_web_by_name.cmd.....]'+cmd_copy)
                # CLASS_COMMON_UTIL.cmd_python3(cmd_copy,my_log=self.G_DEBUG_LOG)
                CLASS_COMMON_UTIL.cmd(cmd_copy,my_log=self.G_DEBUG_LOG)
                ##try:
                ##    CLASS_COMMON_UTIL.cmd(cmd_copy.encode(sys.getfilesystemencoding()),my_log=self.G_DEBUG_LOG)
                ##except:
                ##    if not os.path.exists(target_path):
                ##        os.makedirs(target_path)
                ##    # target_path2=target_path+files[files.rfind("\\"):]
                ##    shutil.copy2(files,target_path)
                ##    self.G_DEBUG_LOG.info('[success]retry copy:from ...... %s ...... to ...... %s ......' % (files,target_path))
                
                if files.endswith('.max.7z'):
                    max_zip_name=os.path.basename(files)
                    max_zip=os.path.join(target_path,max_zip_name)
                    self.MAX_ZIP_LIST.append(max_zip.replace('\\','/'))
                    
            else:
                # self.G_DEBUG_LOG.info('[PreMax.copy_file_web_by_name.files.....]'+files.encode(sys.getfilesystemencoding())+"[not exists]")
                self.G_DEBUG_LOG.info('[PreMax.copy_file_web_by_name.files.....]'+files+"[not exists]")
                #sys.exit(-1)
                #break
                
        self.G_DEBUG_LOG.info('[PreMax.copy_file_web_by_name.end.....]')
        
    def copy_file2(self):
        self.G_DEBUG_LOG.info('[PreMax.copy_file2.start.....]')
        file_list=[]
        
        # propath= self.G_USER_ID_PARENT+"\\"+self.G_USER_ID
        # self.G_DEBUG_LOG.info('[[PreMax.packFile.propath.....]'+propath)
        #self.G_DEBUG_LOG.info('[PreMax.copyFile.texture_list]')
        if 'max' in self.G_ASSET_JSON_DICT:
            for asset_str in self.G_ASSET_JSON_DICT['max']:
                asset_str = CLASS_COMMON_UTIL.bytes_to_str(asset_str)
                if os.path.exists(asset_str):
                    file_list.append(asset_str)
                else:
                    self.G_DEBUG_LOG.info('[err]%s is not exist!!!' % asset_str)
                    sys.exit(-1)
                
        if 'asset_input_server' in self.G_ASSET_JSON_DICT:
            for asset_str in self.G_ASSET_JSON_DICT['asset_input_server']:
                asset_str = CLASS_COMMON_UTIL.bytes_to_str(asset_str)
                if os.path.exists(asset_str):
                    file_list.append(asset_str)
                else:
                    self.G_DEBUG_LOG.info('[err]%s is not exist!!!' % asset_str)
                    sys.exit(-1)
        # guyVersion=self.RENDER_CFG_PARSER.get('common','guyversion')
        
        
        # if LooseVersion(guyVersion)>LooseVersion('4.0.2.10'):
            # if self.RENDER_CFG_PARSER.has_section('vrmap'):
                # self.G_DEBUG_LOG.info('---vrmap---')
                # vrmapfileList=self.RENDER_CFG_PARSER.options('vrmap')
                # for vrmapfileKey in vrmapfileList:
                    # file_list.append(self.RENDER_CFG_PARSER.get('vrmap',vrmapfileKey))
            # if self.RENDER_CFG_PARSER.has_section('vrlmap'):
                # self.G_DEBUG_LOG.info('---vrlmap---')
                # vrlmapfileList=self.RENDER_CFG_PARSER.options('vrlmap')
                # for vrlmapfileKey in vrlmapfileList:
                    # file_list.append(self.RENDER_CFG_PARSER.get('vrlmap',vrlmapfileKey))
                    
        # else:
            # if self.RENDER_CFG_PARSER.has_section('customfile'):
                # self.G_DEBUG_LOG.info('---pre4.0.2.10.customfile---')
                # customfileList=self.RENDER_CFG_PARSER.options('customfile')
                # for customfileKey in customfileList:
                    # file_list.append(self.RENDER_CFG_PARSER.get('customfile',customfileKey))
                    
                
        #self.G_DEBUG_LOG.info('[PreMax.copyFile.start.file_list.....]'+self.G_INPUT_USER_PATH)
        if file_list:
            # commonCfg=self.RENDER_CFG_PARSER.options('common')#skipUpload
            # skipUpload="0"
            # if self.RENDER_CFG_PARSER.has_option('common','skipUpload'):
                # skipUpload=self.RENDER_CFG_PARSER.get('common','skipUpload')
            # self.G_DEBUG_LOG.info('[[PreMax.packFile.skipUpload.....]'+skipUpload)
            # if skipUpload=="1":
                # preFileTxt=self.GetFileList(file_list,propath)
                # self.G_DEBUG_LOG.info('[[PreMax.packFile.preFileTxt.....]'+preFileTxt)
                # if preFileTxt=="-1":
                    # sys.exit(-1)
                # else:
                    # self.G_DEBUG_LOG.info('[PreMax.copyFile.fileCount.....]'+str(self.fileCount))
                    # cmd=u'c:\\fcopy\\FastCopy.exe  /speed=full /force_close  /no_confirm_stop /force_start /srcfile="'+preFileTxt+'" /to="'+self.G_WORK_RENDER_TASK_MAX.replace('/','\\')+'"'
                    # self.G_DEBUG_LOG.info('[PreMax.copyFile.cmd.....]'+cmd)
                    # if isinstance(cmd,unicode):
                        # cmd.encode('utf-8')
                    # else:
                        # cmd.decode('gbk').encode('utf-8')
                    # self.RBcmd(cmd)
            # else:
            for files in file_list:
                #if files.endswith('.fxd')
                file_path_server=(files.split('>>')[1]).replace('/','\\') 
                if file_path_server=="":
                    self.G_DEBUG_LOG.info('files----'+files+"---false")
                    sys.exit(-1)   
                # file_path=(self.G_INPUT_USER_PATH+file1[1:len(file1)]).replace('/','\\')
                # file_path=os.path.normpath(os.path.join(G_INPUT_USER_PATH,files)).replace(':','')
                #self.G_DEBUG_LOG.info('[[PreMax.packFile.file_path.....]'+file_path)
                # file_dir=file1[file1.find(propath)+len(propath):file1.rfind("\\")]
                # file_dir=os.path.dirname(files).replace(':','')
                #self.G_DEBUG_LOG.info('[[PreMax.packFile.file_path.....]'+file_dir)
                #print os.path.exists(file_path)
                #file_path=self.GetFileList(propath,file_path)
                if self.is_out_file(file_path):
                    # self.G_DEBUG_LOG.info('[PreMax.isRENDER_OUTPUT_FILENAME]'+file_path.encode(sys.getfilesystemencoding())+"--pass")
                    self.G_DEBUG_LOG.info('[PreMax.isRENDER_OUTPUT_FILENAME]'+file_path+"--pass")
                    continue
                if os.path.exists(file_path):
                    target_path=os.path.join(self.G_WORK_RENDER_TASK_MAX,file_dir)
                    # self.G_DEBUG_LOG.info('unicode')
                    cmd_copy='c:\\fcopy\\FastCopy.exe  /speed=full /force_close  /no_confirm_stop /force_start "'+file_path+'" /to="'+target_path+'"'
                    # self.G_DEBUG_LOG.info('[PreMax.copyFile.cmd.....]'+cmd_copy.encode(sys.getfilesystemencoding()))
                    self.G_DEBUG_LOG.info('[PreMax.copyFile.cmd.....]'+cmd_copy)
                    # CLASS_COMMON_UTIL.cmd_python3(cmd_copy,my_log=self.G_DEBUG_LOG)
                    CLASS_COMMON_UTIL.cmd(cmd_copy,my_log=self.G_DEBUG_LOG)
                    ##try:
                    ##    CLASS_COMMON_UTIL.cmd(cmd_copy.encode(sys.getfilesystemencoding()),my_log=self.G_DEBUG_LOG)
                    ##except:
                    ##    if not os.path.exists(target_path):
                    ##        os.makedirs(target_path)
                    ##    target_path2=target_path+files[files.rfind("\\"):]
                    ##    shutil.copy2(file_path,target_path2)
                    ##    self.G_DEBUG_LOG.info('[success]retry copy:from ...... %s ...... to ...... %s ......' % (file_path,target_path2))
                        
                    if file_path.endswith('.max.7z'):
                        max_zip_name=os.path.basename(file_path)
                        max_zip=os.path.join(target_path,max_zip_name)
                        self.MAX_ZIP_LIST.append(max_zip.replace('\\','/'))
                        
                    elif file_path.endswith('.ifl'):
                        ifl_name=os.path.basename(file_path)
                        ifl=os.path.join(target_path,ifl_name)
                        self.ifl_list.append(ifl.replace('\\','/'))
                else:
                    # self.G_DEBUG_LOG.info('[PreMax.copyFile.file_path.....]'+file_path.encode(sys.getfilesystemencoding())+"not exists")
                    self.G_DEBUG_LOG.info('[PreMax.copyFile.file_path.....]'+file_path+"not exists")
                    sys.exit(-1)
                    #break
                
                    
        self.G_DEBUG_LOG.info('[PreMax.copyFile.end.....]')

    def RB_HAN_RESULT(self):
        self.G_DEBUG_LOG.info('[PreMax.RB_HAN_RESULT.start.....]')
        # output_dir = os.path.join(self.G_TEMP_PATH,self.G_TASK_ID)
        if not os.path.exists(self.G_TEMP_PATH):
            os.makedirs(self.G_TEMP_PATH)
        copy_cmd='c:\\fcopy\\FastCopy.exe  /speed=full /force_close  /no_confirm_stop /force_start "'+self.G_WORK_RENDER_TASK_MAX+'.7z" /to="'+self.G_TEMP_PATH+'"'
        
        # net_render_txt=os.path.join(self.G_PLUGINS_MAX_SCRIPT,'user',self.G_USERID,'netrender.txt').replace('\\','/')
        #if not os.path.exists(net_render_txt):
        CLASS_COMMON_UTIL.cmd(copy_cmd,my_log=self.G_DEBUG_LOG)
        self.G_DEBUG_LOG.info('[PreMax.RB_HAN_RESULT.end.....]')
        
    def read_by_code(self,code):
        print('read by code')
        

    def subst_path(self):
        self.G_DEBUG_LOG.info('[Max.subst_path start]')
        bat_str='net use * /del /y \r\n'
        # self.G_PLUGIN_PATH=self.argsmap['pluginPath']
        bat_str=bat_str+'net use B: '+self.G_PLUGIN_PATH.replace('/','\\').replace("10.60.100.151","10.60.100.152")+' \r\n'
        subst_driver='efghijklmnopqrstuvwxyz'
        for dd in subst_driver:
            bat_str=bat_str+'subst '+dd+': /d\r\n'
        for file_name in os.listdir(self.G_WORK_RENDER_TASK_MAX):
            self.G_DEBUG_LOG.info(file_name)
            if os.path.isfile(os.path.join(self.G_WORK_RENDER_TASK_MAX,file_name)):
                continue
            dir_name=file_name.lower()
            dir_path=os.path.join(self.G_WORK_RENDER_TASK_MAX,file_name).lower()
            # print(dir_name)        
            if dir_name=='net':
                continue
            if dir_name=='default':
                continue
            
            if dir_name=='b' or dir_name=='c' or dir_name=='d':
                continue
            
            #e,f,g...
            if len(dir_name)==1:
                # subst_cmd='subst '+dir_name+': '+dir_path
                subst_cmd='subst '+dir_name+': "'+dir_path+'"'
                self.G_DEBUG_LOG.info(subst_cmd)
                self.G_DEBUG_LOG.info(subst_cmd)
                os.system(subst_cmd)
                bat_str=bat_str+subst_cmd+'\r\n'
        bat_file=os.path.join(self.G_WORK_RENDER_TASK_CFG,('substDriver.bat')).replace('\\','/')
        self.write_bat(bat_file,bat_str)
        self.G_DEBUG_LOG.info('[Max.subst_path end]')
            
    def write_bat(self,bat_file,cmd_str):
        #subst
        #bat_file=os.path.join(self.G_RENDER_WORK_TASK_CFG,('render'+renderFrame+'_notrender.bat')).replace('\\','/')
        bat_file_object=codecs.open(bat_file,'w',"utf-8")
        bat_file_object.write(cmd_str+'\r\n')
        bat_file_object.close()
        
    #copy pySitePackages
    def copy_py_site_packages(self):
        py_site_packages_pool=os.path.normpath('B:/tools/pySitePackages')
        c_script=os.path.normpath('c:/script')
        py_site_packages_node=os.path.join(c_script,'pySitePackages')
        copy_py_site_packages_cmd=r'c:\fcopy\FastCopy.exe /speed=full /force_close /no_confirm_stop /force_start "'+py_site_packages_pool+'" /to="'+py_site_packages_node+'"'
        CLASS_COMMON_UTIL.cmd(copy_py_site_packages_cmd,my_log=self.G_DEBUG_LOG)
        sys.path.append(py_site_packages_node)
        self.chardet = __import__('chardet')
        
    #set self.MAX_PREPROCESS=True
    def set_max_preprocess(self):
        max_cmd_txt=os.path.join(self.G_MAX_SCRIPT,'user',self.G_USER_ID,'maxcmd.txt')
        if os.path.exists(max_cmd_txt):
            self.MAX_PREPROCESS=True
        if 'render_type' in self.G_TASK_JSON_DICT['miscellaneous'] and self.G_TASK_JSON_DICT['miscellaneous']['render_type'] == 'maxcmd':
            self.MAX_PREPROCESS=True
        if 'G_SCHEDULER_CLUSTER_NODES' in self.__dict__ and len(self.G_SCHEDULER_CLUSTER_NODES) > 0:
            self.MAX_PREPROCESS=True
        print('MAX_PREPROCESS=' + str(self.MAX_PREPROCESS))
    
    #set vray0000
    def set_vray0000(self):
        if 'G_SCHEDULER_CLUSTER_NODES' in self.__dict__ and len(self.G_SCHEDULER_CLUSTER_NODES) > 0:
            if 'plugins' in self.G_CG_CONFIG_DICT and 'vray' in self.G_CG_CONFIG_DICT['plugins']:
                if self.G_CG_CONFIG_DICT['plugins']['vray'].startswith('1') or self.G_CG_CONFIG_DICT['plugins']['vray'].startswith('2'):
                    print('set vray to vray0000 start')
                    software_config_plugins_old = {}
                    software_config_plugins = {}
                    vray_new = '0000'
                    for k1,v1 in list(self.G_CG_CONFIG_DICT['plugins'].items()):
                        software_config_plugins[k1] = v1
                    software_config_plugins_old = software_config_plugins
                    self.G_CG_CONFIG_DICT['plugins']['vray'] = vray_new  
                    if 'old_plugins' not in self.G_CG_CONFIG_DICT:
                        self.G_CG_CONFIG_DICT['old_plugins'] = software_config_plugins_old
                    #write task.json
                    CLASS_COMMON_UTIL.write_file(self.G_TASK_JSON_DICT,self.G_TASK_JSON)
                    print('set vray to vray0000 done')

    #Customer 3dsmax.ini (e.g. from B:\plugins\max\ini\distributed\3ds Max 2014\3dsmax.ini to C:\Users\admin\AppData\Local\Autodesk\3dsMax\2014 - 64bit\ENU\3dsmax.ini)
    def customer_3dsmax_ini(self):
        max_ini=os.path.join(self.G_MAX_B,'ini/distributed',self.G_CG_VERSION,'3dsmax.ini').replace('\\','/')
        max_user_ini=os.path.join(self.G_MAX_B,'ini/distributed',self.G_USER_ID,self.G_CG_VERSION,'3dsmax.ini').replace('\\','/')
        user_profile=os.environ["userprofile"]
        max_enu=user_profile+'\\AppData\\Local\\Autodesk\\3dsMax\\'+self.G_CG_VERSION.replace('3ds Max ','')+' - 64bit\\enu'
        #----------Customer 3dsmax.ini----------
        try:
            
            if os.path.exists(max_ini) and os.path.exists(max_enu) :
                copy_max_ini_cmd='xcopy /y /v /f "'+max_ini +'" "'+max_enu.replace('\\','/')+'/"' 
                self.G_DEBUG_LOG.info(copy_max_ini_cmd)
                # self.RBcmd(copy_max_ini_cmd,myLog=True)
                CLASS_COMMON_UTIL.cmd(copy_max_ini_cmd,my_log=self.G_DEBUG_LOG)
            
            if os.path.exists(max_user_ini) and os.path.exists(max_enu) :
                copy_max_ini_cmd='xcopy /y /v /f "'+max_user_ini +'" "'+max_enu.replace('\\','/')+'/"' 
                self.G_DEBUG_LOG.info(copy_max_ini_cmd)
                # self.RBcmd(copy_max_ini_cmd,myLog=True)
                CLASS_COMMON_UTIL.cmd(copy_max_ini_cmd,my_log=self.G_DEBUG_LOG)
        except Exception as e:
            self.G_DEBUG_LOG.info('[err].3dsmaxIni Exception')
            self.G_DEBUG_LOG.info(e)

    def relative_to_absolute(self,relative_path):
        return os.path.normpath(os.path.join(self.G_INPUT_USER_PATH,relative_path))
            
    #def RB_EXECUTE(self):#total    
    #
    #    self.G_DEBUG_LOG.info('[BASE.RB_EXECUTE.start.....]')        
    #    self.RB_PRE_PY()
    #    self.RB_MAP_DRIVE()
    #    self.RB_HAN_FILE()
    #    self.RB_CONFIG()
    #    self.RB_RENDER()
    #    # self.RB_CONVERT_SMALL_PIC()
    #    self.RB_HAN_RESULT()
    #    self.RB_POST_PY()
    #    self.RB_KAFKA_NOTIFY()
    #    self.G_DEBUG_LOG.info('[BASE.RB_EXECUTE.end.....]')
        

        
        