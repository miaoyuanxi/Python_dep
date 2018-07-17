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
import time
import platform
import json
import types
import datetime
from imp import reload
reload(sys)
# sys.setdefaultencoding('utf-8')


class PluginBase(object):
    def __init__(self):
        self.JSON_PATH = r'B:/plugins/maya_new/envInfo.json'
        self.G_PLUGIN_PY_NAME = 'config.py'
        self.G_PLUGIN_FUNCTION_NAME = 'main'
        self.ZIP_TYPE = '.7z'
        self.CURRENT_OS = platform.system().lower() 
        self.TOOL_DIR = self.get_json_ini('toolDir')
        self.ZIPEXE = "%s/7z.exe"%self.TOOL_DIR
        self.TEMP_PATH = os.getenv('temp').replace('\\','/')

    def get_json_ini(self,objkey,default = None,idex=0):
        info_path = self.JSON_PATH
        with open(info_path,'r') as fn:
            fn_dict = json.load(fn)
            tmp_dict = fn_dict[self.CURRENT_OS]
            def get_dict(tmp_dict,objkey,default = None,idex=0):
                for k,v in list(tmp_dict.items()):
                    if k == objkey:
                        if isinstance(v,list):
                            v = v[idex]
                        elif v == None:
                            v = default
                        else:
                            v = v
                        return v
                    else:
                        # if type(v) is types.DictType:
                        if isinstance(v,dict):
                            re = get_dict(v,objkey,default,idex)
                            if re is not default:
                                if isinstance(re,list):
                                    re = re[idex]
                                elif re == None:
                                    re = default
                                else:
                                    re = re
                                # print re
                                return re
                return default
            key_v = get_dict(tmp_dict,objkey,default,idex)
        return key_v
                

    def clean_dir(self,Dir):
        for root, dirs, files in os.walk(Dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    def do_del_path(self,file_path):
        if os.path.isfile(file_path) and os.path.exists(file_path):
            try:
                os.remove(file_path)
                self.MyLog("del file  %s" % file_path)
            except Exception as error:  
                print( Exception,":",error )
                self.MyLog("dont del file %s" % file_path)
        if os.path.isdir(file_path) and os.path.exists(file_path):            
            try:                
                shutil.rmtree(file_path)
                self.MyLog("del path %s" % file_path)
            except Exception as error:              
                print( Exception,":",error )
                self.MyLog("dont del path %s" % file_path)                 
                
                
                

    def make_dirs(self,dir_list=[]):
        if len(dir_list)>0:
            for dir in dir_list:
                if not os.path.exists(dir):
                    os.makedirs(dir)
        

    def find_7z(self,_7z, folder):
        _7z_name = os.path.basename(_7z)
        if os.path.exists(_7z):
            info_file = os.path.splitext(_7z)[0] + ".info"
            if os.path.isfile(info_file):
                with open(info_file, 'r') as f:
                    dict_info = eval(f.read())
                    if 'mtime' in dict_info:
                        src_7z_mtime = dict_info['mtime']
                    if 'size' in dict_info:
                        src_7z_size = dict_info['size']
            else:
                src_7z_mtime = time.ctime(os.stat(_7z).st_mtime)
                src_7z_size = os.path.getsize(_7z)
            for des_7z in os.listdir(folder):
                if des_7z.startswith(_7z_name):
                    des_7z_file = os.path.join(folder, des_7z)
                    if os.path.isfile(des_7z_file):
                        des_7z_mtime = time.ctime(os.stat(des_7z_file).st_mtime)
                        des_7z_size = os.path.getsize(des_7z_file)
                        # print src_7z_mtime, des_7z_mtime
                        # print len(src_7z_mtime), len(des_7z_mtime)
                        # print src_7z_size, des_7z_size
                        if src_7z_mtime == des_7z_mtime and src_7z_size == des_7z_size:
                            return des_7z_file
                            self.MyLog('%s  is  same ' % _7z)
                        else:
                            return 0
        else:
            self.Mylog( "the %s is not exists" % _7z)
            return 0
            
            

    def un_7z(self,zip_file,to,my_log=None):
        if my_log == None:
            my_log = self.TEMP_PATH + '/' + 'plugin.txt'
        un_times = 1
        while un_times<3:
            cmd = r'"%s" x -y -aos "%s" -o"%s"' % (self.ZIPEXE, zip_file, to)
            un_log = open(my_log,"wt")
            source_unzip = subprocess.Popen(cmd,stdout=un_log,shell=True)
            source_unzip.wait()
            if not source_unzip.returncode == 0:
                un_times +=1
            else:
                un_times = 3
            un_log.close()


    def copy_7z(self,zip_file,to,my_log=None):
        if my_log == None:
            my_log = self.TEMP_PATH + '/' + 'plugin.txt'
        cp_times = 0
        while cp_times < 3:
            cp_log = open(my_log,"wt")
            cmds_copy = "copy %s %s" % (os.path.abspath(zip_file),
                        os.path.abspath(to))
            source_copy = subprocess.Popen(cmds_copy,stdout=cp_log,shell=True)
            source_copy.wait()
            cp_times =(cp_times+1) if not source_copy.returncode == 0 else 5
            cp_log.close()
            
    def cmd_copy(self,copy_source,to,my_log=None):
        if os.path.exists(copy_source):
            if my_log == None:
                my_log = self.TEMP_PATH + '/' + 'plugin.txt'
            cp_times = 0
            while cp_times < 3:
                cp_log = open(my_log,"wt")
                if os.path.isdir(copy_source):                
                    cmds_copy = r'xcopy /y /f /e /v "%s" "%s"' % (os.path.abspath(copy_source),os.path.abspath(to))
                else:
                    cmds_copy = "copy %s %s" % (os.path.abspath(source),os.path.abspath(to))
                source_copy = subprocess.Popen(cmds_copy,stdout=cp_log,shell=True)
                source_copy.wait()
                cp_times =(cp_times+1) if not source_copy.returncode == 0 else 5
                cp_log.close()
        else:
            self.MyLog('canot exist  %s' % copy_source)

    #python copy
    def CopyFiles(self,copy_source,copy_target):
        copy_source=os.path.normpath(copy_source)
        copy_target=os.path.normpath(copy_target)
        copy_source = self.str_to_unicode(copy_source)
        copy_target = self.str_to_unicode(copy_target)
        try:
            if not os.path.exists(copy_target):
                os.makedirs(copy_target)
            if  os.path.isdir(copy_source):
                self.copy_folder(copy_source,copy_target)
            else:
                shutil.copy(copy_source,copy_target)
            return True
        except Exception as e:
            print (e)
            return False


    def copy_folder(self,pyFolder,to):
        if not os.path.exists(to):
            os.makedirs(to)
        if os.path.exists(pyFolder):
            for root, dirs, files in os.walk(pyFolder):
                for dirname in  dirs:
                    tdir=os.path.join(root,dirname)
                    if not os.path.exists(tdir):
                        os.makedirs(tdir)
                for i in xrange (0, files.__len__()):
                    sf = os.path.join(root, files[i])
                    folder=to+root[len(pyFolder):len(root)]+"/"
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    shutil.copy(sf,folder)


    def str_to_unicode(self,str,str_decode = 'default'):
        if not isinstance(str,unicode):
            try:
                if str_decode != 'default':
                    str = str.decode(str_decode.lower())
                else:
                    try:
                        str = str.decode('utf-8')                        
                    except:
                        try:
                            str = str.decode('gbk')
                        except:                            
                            str = str.decode(sys.getfilesystemencoding())
            except Exception as e:
                print ('[err]str_to_unicode:decode %s to unicode failed' % (str))
                print (e)
        return str


    def unicode_to_str(self,str,str_encode = 'system'):
        if isinstance(str,unicode):
            try:
                if str_encode.lower() == 'system':
                    str=str.encode(sys.getfilesystemencoding())
                elif str_encode.lower() == 'utf-8':
                    str = str.encode('utf-8')
                elif str_encode.lower() == 'gbk':
                    str = str.encode('gbk')
                else:
                    str = str.encode(str_encode)
            except Exception as e:
                print ('[err]unicode_to_str:encode %s to %s failed' % (str,str_encode))
                print (e)
        else:
            print ('%s is not unicode ' % (str))
        return str


  
    def CalcMD5(self,filepath):
        with open(filepath,'rb') as f:
            md5obj = hashlib.md5()
            md5obj.update(f.read())
            hash = md5obj.hexdigest()
            print(hash)
            return hash  

    def check_file(self,file1,file2):   #校验文件函数  
        hashfile1 = self.CalcMD5(file1)
        hashfile2 = self.CalcMD5(file2)
        if hashfile1 == hashfile2:
            return 1
        else:
            return 0
            



class MayaPlugin(PluginBase):
    def __init__(self,pluginCfg = None,custom_config = None,userId = '000',taskId = '000',myLog=None):
        PluginBase.__init__(self)
        self.USERID = userId
        self.TASKID = taskId        
        self.MY_LOGER= myLog
        self.Nodefolders = ["source","software","logs"]        
        self.MAYA_Plugin_Dir = self.get_json_ini('MAYA_Plugin_Dir')
        self.Node_D = self.get_json_ini('Node_D')
        self.TEMP_PATH = os.getenv('temp').replace('\\','/')      
        self.custom_config = custom_config
        
        if isinstance(pluginCfg,dict):
            self.G_PLUGIN_DICT=pluginCfg
        else:
            self.G_PLUGIN_DICT=self.get_plugin_dict(pluginCfg)

        if 'renderSoftware' in self.G_PLUGIN_DICT or 'softwareVer' in self.G_PLUGIN_DICT:
            # self.G_CG_VERSION=self.G_PLUGIN_DICT['renderSoftware']+' '+self.G_PLUGIN_DICT['softwareVer']
            self.G_CG_NAME =self.G_PLUGIN_DICT['renderSoftware']
            self.G_CG_VERSION =self.G_PLUGIN_DICT['softwareVer']
        else:
            # self.G_CG_VERSION=self.G_PLUGIN_DICT['cg_name']+' '+self.G_PLUGIN_DICT['cg_version']
            self.G_CG_NAME =self.G_PLUGIN_DICT['cg_name']
            self.G_CG_VERSION =self.G_PLUGIN_DICT['cg_version']

    def MyLog(self,message,extr="MayaPlugin"):
        if self.MY_LOGER:
            self.MY_LOGER.info("[%s] %s"%(extr,str(message)))
        else:
            if str(message).strip() != "":
                print("[%s] %s"%(extr,str(message)))



    def get_plugin_dict(self,pluginCfg):
        plginInfoDict=None
        if  os.path.exists(pluginCfg):
            fp = open(pluginCfg)
            if fp:
                listOfplgCfg = fp.readlines()
                removeNL = [(i.rstrip('\n')) for i in listOfplgCfg]
                combinedText = ''.join(removeNL)
                plginInfoDict = eval('dict(%s)' % combinedText)
                # print plginInfoDict
                # for i in plginInfoDict.keys():
                    # self.MyLog(i)
                    # self.MyLog(plginInfoDict[i])

        return plginInfoDict

    def do_clear_render_pre(self, *args):
        input_SW = args[0]
        _V_APP = args[1]
        
        if input_SW=="maya": 

            os.environ['MAYA_RENDER_DESC_PATH'] = ""
            os.environ['MAYA_MODULE_PATH'] =""
            #os.environ['MAYA_SCRIPT_PATH'] = ""
            os.environ['MAYA_PLUG_IN_PATH'] = ""            
            _MAYA_ROOT = r"C:/Program Files/Autodesk/Maya" + _V_APP
            
            curUserPath = os.environ.get('userprofile')
            _MAYA_HOME = r"%s/Documents/maya/%s" % (curUserPath, _V_APP)
            if int(_V_APP[:4])<=2015:
                _MAYA_HOME = r"%s/Documents/maya/%s-x64" % (curUserPath,_V_APP)
            _MAYA_HOME = _MAYA_HOME.replace('\\',"/")
            del_list_mod=['mtoa.mod',"VRayForMaya.module",\
            "shaveHaircut.mod","3delight_for_maya2013.mod","pgYetiMaya.mod",\
            "Maya2012ExocortexAlembic.mod",'3delight_for_maya2012.mod','3delight_for_maya2013.5.mod','3delight_for_maya2014.mod',\
            "FumeFX.mod",'MiarmyForMaya.txt','Pixelux Digital Molecular Matter 64-bit.txt','ArnoldDomemaster3D.mod','Domemaster3D.mod',\
            'glmCrowd.mod','KrakatoaForMaya.module','maya2016.mod',"ArnoldDomemaster3D.mod",'Domemaster3D.mod','Maya2015ExocortexAlembic.mod','houdiniEngine-maya2015']
            mode_path =  r"%s\modules" % (_MAYA_ROOT)
            if os.path.exists(mode_path):
                mode_list = os.listdir(mode_path)
            else:
                mode_list=[]
            del_mod_list=[val for val in del_list_mod if val in mode_list]
            #del_list = list(set(del_list).intersection(set(listdir_path)))    
            for del_path in del_mod_list:
                del_file_path="%s\%s" % (mode_path,del_path)
                self.do_del_path(del_file_path)
            
            del_list_plug=['maxwell.mll','poseDeformer.mll','poseReader.mll','realflow.mll',"faceMachine.mll",'faceMachine','anzovin',\
            'wbDeltaMushDeformer.bundle','wbDeltaMushDeformer.mll','wbDeltaMushDeformer.so','anzovinRigNodes.mll','hotOceanDeformer.mll',\
            'nPowerTrans.mll','nPowerSoftware','resetSkinJoint.mll','AWutils.dll','VoxelFlow.dll']
            plug_path =  r"%s\bin\plug-ins" % (_MAYA_ROOT)
            if os.path.exists(plug_path):
                plug_list = os.listdir(plug_path)
            else:
                plug_list=[]
            
            del_plug_list=[val for val in del_list_plug if val in plug_list]
            #del_list = list(set(del_list).intersection(set(listdir_path)))    
            for del_path in del_plug_list:
                del_file_path="%s\%s" % (plug_path,del_path)
                self.do_del_path(del_file_path)
            #print "claer arnold "
            del_mode_path_one= r"%s\modules\mtoa.mod" % (_MAYA_HOME)            
            del_DESC_path_one= r"%s\bin\rendererDesc\arnoldRenderer.xml" % (_MAYA_ROOT)
            self.do_del_path(del_mode_path_one)
            self.do_del_path(del_DESC_path_one)            
            #print "clear vray "
            del_vray_one=r"%s\vray" % (_MAYA_ROOT)
            self.do_del_path(del_vray_one) 
            vray_lic=r"C:\Program Files\Common Files\ChaosGroup\vrlclient.xml"
            self.do_del_path(vray_lic)
            maya_scripts=r"C:\Users\enfuzion\Documents\maya\scripts"
            self.do_del_path(maya_scripts)
            #print del fumefx for mr
            
            fumefx_dll=r"C:\Program Files\Autodesk\mentalrayForMaya%s\shaders\ffxDyna.dll" % (_V_APP) 

            self.do_del_path(fumefx_dll) 
            fume_mi=r"C:\Program Files\Autodesk\mentalrayForMaya%s\shaders\include\ffxDyna.mi" % (_V_APP)

            self.do_del_path(fume_mi)
            mr_2017=r"C:\Program Files\Common Files\Autodesk Shared\Modules\Maya\2017\mentalray.mod"

            self.do_del_path(mr_2017)    

    def do_auto_load_plu(self,maya_v,plugin_list,*args):
        if int(maya_v[:4])>=2014:
            self.auto_load_plu(maya_v,"AbcImport")
            self.auto_load_plu(maya_v,"realflow")
        if int(maya_v[:4])>=2015 and int(maya_v[:4])< 2017:
            self.auto_load_plu(maya_v,"xgenToolkit")
        if "miarmy" in plugin_list:
            miarmy_v = maya_v.replace(".","")
            self.MyLog("MiarmyProForMaya"+miarmy_v)
            self.auto_load_plu(maya_v,("MiarmyProForMaya"+miarmy_v)) 
        if "vrayformaya" in plugin_list:
            self.auto_load_plu(maya_v,"vrayformaya")
            self.auto_load_plu(maya_v,"xgenVRay")             
        if "mtoa" in plugin_list:
            self.auto_load_plu(maya_v,"mtoa")
        if "realflow" in plugin_list:
            self.auto_load_plu(maya_v,"realflow")   
            
            
    def do_load_plugins_cfg(self, *args):        
        pluginsConfigPathList = args[0] 
        validInfoDict = args[1]
        # print pluginsConfigPathList
        # print validInfoDict
        # print type(validInfoDict)                
        for cfgFile in pluginsConfigPathList:
            if os.path.exists(cfgFile):
                self.MyLog('plugins \'s config path : %s' % cfgFile)
                cfgFileDir = os.path.dirname(cfgFile)
                cfgFileName = os.path.splitext(os.path.split(cfgFile)[-1])[0]
                # print cfgFileName
                sys.path.append(cfgFileDir)
                # self.MyLog( 'sys.path after append : %s' % sys.path)
                try:
                    cfg = __import__(cfgFileName)
                    reload(cfg)        
                    cfg.main(clientRenderInfo(validInfoDict))
                except Exception as err:
                    self.MyLog('=== Error occur import/execute "%s"! ===\n=== Error Msg : %s ===' % (cfgFile, err))
                try:
                    while True:
                        sys.path.remove(cfgFileDir)
                except:
                    pass                
            else:
                self.MyLog('cfgFile file %s is not exists!' % cfgFile)


    def do_load_plugins_cfg_cus(self, *args):
        pluginsConfigPathList = args[0]
        validInfoDict = args[1]
        # print pluginsConfigPathList
        # print validInfoDict
        # print type(validInfoDict)
        for cfgFile in pluginsConfigPathList:
            if os.path.exists(cfgFile):
                self.MyLog('plugins \'s config path : %s' % cfgFile)
                cfgFileDir = os.path.dirname(cfgFile)
                cfgFileName = os.path.splitext(os.path.split(cfgFile)[-1])[0]
                # print cfgFileName
                sys.path.append(cfgFileDir)
                # self.MyLog( 'sys.path after append : %s' % sys.path)
                try:
                    cfg = __import__(cfgFileName)
                    reload(cfg)
                    cfg.doConfigSetup(clientRenderInfo(validInfoDict))
                except Exception as err:
                    self.MyLog('=== Error occur import/execute "%s"! ===\n=== Error Msg : %s ===' % (cfgFile, err))
                try:
                    while True:
                        sys.path.remove(cfgFileDir)
                except:
                    pass
            else:
                self.MyLog('cfgFile file %s is not exists!' % cfgFile)

    def auto_load_plu(self,maya_v,plug_name):
        
        if int(maya_v[:4]) <= 2015:
            maya_v = "%s-x64" % (maya_v)
        curUserPath = os.environ.get('userprofile')
        pluginPrefsFile = r"%s/Documents/maya/%s/prefs/pluginPrefs.mel" % (curUserPath, maya_v)
        pluginPrefsFile = pluginPrefsFile.replace('\\','/')
        hasPlugPrefs = False
        plug_load = (r'evalDeferred("autoLoadPlugin(\"\", \"%s\", \"%s\")");' + '\n') % (plug_name, plug_name)
        if os.path.exists(pluginPrefsFile):
            mode = "a+"
            with open(pluginPrefsFile, mode) as f:
                lines = f.readlines()
                for line in lines:
                    if plug_load.strip() == line.strip():
                        self.MyLog("auto load  %s " % (plug_name))
                        hasPlugPrefs = True
                        break
                if not hasPlugPrefs:
                    self.MyLog("write %s for auto load" % (plug_name))
                    f.write(plug_load)
            
            
        else:
            file_dir = os.path.split(pluginPrefsFile)[0]
            if os.path.exists(file_dir)==0:            
                os.makedirs(file_dir)
            # print ("makedir %s " % (file_dir))
            mode = "w"
            with open(pluginPrefsFile, mode) as f:
                # print ("write %s for auto load" % (plug_name))
                f.write(plug_load)
                
                
              


    def get_plugin_ini(self):
        # print('--------------------------------Start config ini--------------------------------\n\n')       
        pluginValidList = []  
        # pluginValidDict = {} 
        pluginPyPath = ''        
        allPlugDict=self.G_PLUGIN_DICT
        index = 0
        if allPlugDict and 'plugins' in allPlugDict:
            pluginDict=allPlugDict['plugins']
            self.MyLog(pluginDict)
            if pluginDict:
                for pluginName in pluginDict:  
                    pluginVersion=pluginDict[pluginName]                 
                    pluginZipName = self.G_CG_NAME + self.G_CG_VERSION + '_' + pluginName + pluginVersion + self.ZIP_TYPE
                    if pluginName in  ['redshift','alShader','Cryptomatte','Domemaster3D','miarmy']:
                        if pluginName == 'miarmy':
                            ver_list = []
                            ZipSourceDir = os.path.join(self.MAYA_Plugin_Dir,pluginName,'source').replace('\\','/')
                            for zipfile in os.listdir(ZipSourceDir):                               
                                zipfile = zipfile.lower()
                                if zipfile.startswith(pluginName) and zipfile.endswith(self.ZIP_TYPE):
                                    ver_list.append(int(os.path.splitext(zipfile)[0].split(pluginName)[1].replace(".","")))  
                            if len(ver_list) == 0:
                                self.MyLog("Miarmy plugin is not exist! please check ")
                                sys.exit(555)                               
                            max_ver = str(max(ver_list))
                            pluginVersion = ".".join([max_ver[0],max_ver[1],max_ver[-2:]])
                            self.MyLog("lastest miarmy ver : " + pluginVersion)
                        pluginZipName = pluginName + pluginVersion + self.ZIP_TYPE            
                    pluginZipName_pro = self.G_CG_NAME + self.G_CG_VERSION + '_' + pluginName + pluginVersion + '_' + 'pro' + self.ZIP_TYPE
                    pluginZipName_clientM = self.G_CG_NAME + self.G_CG_VERSION + '_' + pluginName + pluginVersion + '_' + 'clientM' + self.ZIP_TYPE
                    pluginPyPath01=os.path.join(self.MAYA_Plugin_Dir,pluginName,'script',self.G_PLUGIN_PY_NAME).replace('\\','/')
                    pluginPyPath02=os.path.join(self.MAYA_Plugin_Dir,pluginName,'script',self.G_CG_NAME+self.G_CG_VERSION + '_' + pluginName + pluginVersion,self.G_PLUGIN_PY_NAME).replace('\\','/')
                    pluginZipSource = os.path.join(self.MAYA_Plugin_Dir,pluginName,'source',pluginZipName).replace('\\','/')
                    pluginZipSource_pro = os.path.join(self.MAYA_Plugin_Dir,pluginName,'source',pluginZipName_pro).replace('\\','/')
                    pluginZipSource_clientM = os.path.join(self.MAYA_Plugin_Dir,pluginName,'source',pluginZipName_clientM).replace('\\','/')                        
                    pluginZipNode = os.path.join(self.Node_D,pluginName,'source',pluginZipName).replace('\\','/')
                    if os.path.exists(pluginPyPath02):
                        pluginPyPath = pluginPyPath02
                    else:
                        pluginPyPath = pluginPyPath01
                    pluginConfigFile = pluginPyPath
                    messages = os.path.join(self.MAYA_Plugin_Dir,pluginName,'source').replace('\\','/')
                    if os.path.exists(pluginConfigFile):
                        if os.path.exists(pluginZipSource) or os.path.exists(pluginZipSource_pro) or os.path.exists(pluginZipSource_clientM):                        
                            pluginValidDict = pluginName + 'ValidDict' 
                            pluginValidDict = {}
                            # pluginValidDict = dict([('pluginName',pluginName),('pluginVersion',pluginVersion),('pluginPy',pluginConfigFile),('plugins',self.G_PLUGIN_DICT['plugins']),('cgName',self.G_CG_NAME),('cgVersion',self.G_CG_VERSION),('pluginZipSource',pluginZipSource),('pluginZipNode',pluginZipNode)])   
                            pluginValidDict['pluginName'] = pluginName
                            pluginValidDict['pluginVersion'] = pluginVersion
                            pluginValidDict['pluginPy'] = pluginConfigFile
                            pluginValidDict['plugins'] = self.G_PLUGIN_DICT['plugins']
                            pluginValidDict['cgName'] = self.G_CG_NAME
                            pluginValidDict['cgVersion'] = self.G_CG_VERSION
                            pluginValidDict['pluginZipSource'] = pluginZipSource
                            pluginValidDict['pluginZipNode'] = pluginZipNode
                            pluginValidList.append(pluginValidDict)                        
                            # self.MyLog(pluginValidList)    
                        else:
                            index += 1
                            self.MyLog('[Error]----The  plugin %s version  %s  is not exists!' % (pluginName,pluginVersion))
                    else:
                        if not os.path.exists(pluginConfigFile): 
                            index += 1
                            self.MyLog('[Error]----The  %s  is not exists!' % pluginConfigFile)                      
                if index > 0:
                    self.MyLog('Plugin  configPath not found, please confirm the plugin name and version is correct!')
                    sys.exit(55)                    
            else:
                self.MyLog('[Waring]----The customer did not configure plugins!')
                # sys.exit(555)
        print (pluginValidList)
        return pluginValidList
        

        
    def config_plugin(self, *args):
        # self.MyLog(self.G_PLUGIN_DICT) 
        validInfo = {} 
        validInfoPost = {}  
        if "gpuid" in os.environ:
            self.MyLog("this gpu dont clear")
        else:
            # self.MyLog("+++++++++++++clear maya per start ++++++++++++++++++++++++")
            self.do_clear_render_pre(self.G_CG_NAME,self.G_CG_VERSION)
            # self.MyLog("+++++++++++++clear maya per end++++++++++++++++++++++++")
        if self.G_PLUGIN_DICT and 'plugins' in self.G_PLUGIN_DICT: 

            # self.MyLog("+++++++++++++add auto_load_plu start ++++++++++++++++++++++++")
            pluginDict=self.G_PLUGIN_DICT['plugins']
            plugin_list = pluginDict.keys()
            # print plugin_list
            self.do_auto_load_plu(self.G_CG_VERSION,plugin_list)
            # self.MyLog("+++++++++++++add auto_load_plu end ++++++++++++++++++++++++")

        pluginValidList = self.get_plugin_ini()
        # print pluginValidList
        if len(pluginValidList) > 0:
            for plugindict in pluginValidList:
                if plugindict:
                    pluginPy = plugindict['pluginPy']
                    validInfo['cgName'] =  self.G_CG_NAME
                    validInfo['cgVersion'] =  self.G_CG_VERSION 
                    validInfo['pluginName'] =  plugindict['pluginName']
                    validInfo['pluginVersion'] =  plugindict['pluginVersion']    
                    validInfo['plugins'] =  self.G_PLUGIN_DICT['plugins']
                    validInfo['userId'] =  self.USERID
                    validInfo['taskId'] =  self.TASKID                    
                    pluginZipSource = plugindict['pluginZipSource'] 
                    pluginZipNode = plugindict['pluginZipNode']                        
                    for elm in self.Nodefolders:
                        if not os.path.exists("%s/%s/%s"%(self.Node_D,plugindict['pluginName'],elm)):
                            os.makedirs("%s/%s/%s"%(self.Node_D,plugindict['pluginName'],elm))
                    NodeSoftware = os.path.join(self.Node_D,plugindict['pluginName'],'software').replace('\\','/')
                    NodeSourcePath = os.path.join(self.Node_D,plugindict['pluginName'],'source').replace('\\','/')
                    PluginDir = os.path.join(self.Node_D,plugindict['pluginName'],'software',self.G_CG_NAME +self.G_CG_VERSION + '_' + plugindict['pluginName'] + plugindict['pluginVersion'] ).replace('\\','/')
                    self.make_dirs([PluginDir])
                    # try:                        
                        # PluginDir_del = os.path.join(PluginDir + 'del').replace('\\','/')
                        # os.renames(PluginDir,PluginDir_del)
                        # p = multiprocessing.Process(target=self.clean_dir, args=(os.path.abspath(PluginDir_del),))
                        # p.start()
                        # # self.clean_dir(os.path.abspath(PluginDir_del)) 
                    # except Exception as err:
                        # self.MyLog('=== Error : %s ===' % (err))                       
                    
                    un_log = os.path.join(self.Node_D,plugindict['pluginName'],'logs','un_log.txt').replace('\\','/')
                    cp_log = os.path.join(self.Node_D,plugindict['pluginName'],'logs','cp_log.txt').replace('\\','/')
                    if plugindict['pluginName'] == 'vrayformaya':
                        pass
                    else:
                        if self.find_7z(pluginZipSource,NodeSourcePath):
                            self.un_7z(pluginZipNode,PluginDir,un_log)
                        else:
                            self.copy_7z(pluginZipSource,NodeSourcePath,cp_log)
                            self.un_7z(pluginZipNode,PluginDir,un_log)
                    self.do_load_plugins_cfg([pluginPy],validInfo)                    
        validInfoPost['cgName'] =  self.G_CG_NAME
        validInfoPost['cgVersion'] =  self.G_CG_VERSION    
        validInfoPost['plugins'] =  self.G_PLUGIN_DICT['plugins']
        validInfoPost['userId'] =  self.USERID
        validInfoPost['taskId'] =  self.TASKID       
        if self.custom_config:
            self.do_load_plugins_cfg_cus(self.custom_config,validInfoPost)

    def return_info(self):

        cg_name = self.G_CG_NAME
        cg_vervison = self.G_CG_VERSION
        plugins = self.G_PLUGIN_DICT['plugins']
        user_id =  self.USERID
        task_id = self.TASKID
        return cg_name,cg_vervison,plugins,user_id,task_id


    def config(self):
        print ('\n\n-------------------------------------------------------[MayaPlugin]start----------------------------------------------------------\n\n')
        beginTime = datetime.datetime.now()
        self.config_plugin()
        endTime = datetime.datetime.now()
        timeOut = endTime - beginTime
        self.MyLog( "RunningTime----%s" % (str(timeOut)))
        print ('\n\n-------------------------------------------------------[MayaPlugin]end----------------------------------------------------------\n\n')


class clientRenderInfo(dict):
    def __init__(self, *args):
        dict.__init__(self)
        self.plginInfo = args[0]

        self['cgName'] = self.plginInfo['cgName']
        self['cgVersion'] = self.plginInfo['cgVersion']
        self['plugins'] = self.plginInfo['plugins']
        self['userId'] = self.plginInfo['userId']
        self['taskId'] = self.plginInfo['taskId']

        if self.plginInfo.has_key('pluginName'):
            self['pluginName'] = self.plginInfo['pluginName']
        if self.plginInfo.has_key('pluginVersion'):
            self['pluginVersion'] = self.plginInfo['pluginVersion']

    def rdrSW(self, *args):
        if self.plginInfo.has_key('cgName'):
            return self.plginInfo['cgName']
        else:
            return None

    def swVer(self, *args):
        if self.plginInfo.has_key('cgVersion'):
            return self.plginInfo['cgVersion']
        else:
            return None

    def plgins(self, *args):
        if self.plginInfo.has_key('plugins'):
            return self.plginInfo['plugins']
        else:
            return None

    def shders(self, *args):
        if self.plginInfo.has_key('3rdPartyShaders'):
            return self.plginInfo['3rdPartyShaders']
        else:
            return None



if __name__ == '__main__':

    pluginCfg=sys.argv[0]
    pluginPost=sys.argv[1]
    userId=sys.argv[2]
    taskId=sys.argv[3]
    mayaPlugin=MayaPlugin(pluginCfg,pluginPost,userId,taskId)
    mayaPlugin.config()
