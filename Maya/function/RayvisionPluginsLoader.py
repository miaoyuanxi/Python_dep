# -*- coding: utf-8 -*-
import sys
import time
import re
import os
import copy
import shutil
import xml.etree.ElementTree as et
from optparse import OptionParser
from lib2to3.fixer_util import String



class RayvisionPluginsLoader(object):
    
    def __init__(self, log=None):
        
        self.log = log
        #self.pluginsInfoXml = r'\\10.50.1.22\td\plugins\maya\mayaPlugins.xml'
        #self.pluginsInfoXml = r'C:\Users\sanchan\workspace\mayaApp\src\RayvisionPluginsLoader\mayaPlugins.xml'
        self.pluginsInfoXml = r'B:\plugins\maya\mayaPlugins.xml'
        self.plginInfoFromXML = None
        self.validPlginInfo = None
        self.cPlgInfo = {}
        self.renderSW = None
        self.swVer = None
        self.docXml_software = None
        self.docXml_3rdPartyShader = None
        self.list_pluginsConfigPath = []
        self.list_3rdPtyShdPath = []
        
        self.errReturn = 0
        
    #output text message to the log
    def print_log(self, msg):
        
        if self.log:
            self.log.info(msg)
            
        else:
            print msg
        
    #Entry
    def RayvisionPluginsLoader(self, *args):
        
        clientInfo = args[0]
        extraInfo = args[1]
        
        self.doGetClientInfo(clientInfo)
        print "*"*30
        print self.doGetClientInfo(clientInfo)
        print type(self.doGetClientInfo(clientInfo))
        print clientInfo
        print self.plginInfoFromXML
        
        if self.plginInfoFromXML:
            self.setRenderSoftware([self.plginInfoFromXML['renderSoftware'], self.plginInfoFromXML['softwareVer']])
            # soft_name = self.plginInfoFromXML['renderSoftware']
            # soft_ver = self.plginInfoFromXML['softwareVer']
            # print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
            # print soft_name
            # print soft_ver
            print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++="
            if "gpuid" in os.environ:
                self.print_log("this gpu dont clear")
            else:
                self.print_log("+++++++++++++clear maya per start ++++++++++++++++++++++++")
                
                self.do_clear_render_pre([self.plginInfoFromXML['renderSoftware'], self.plginInfoFromXML['softwareVer']])
                self.print_log("+++++++++++++clear maya per end++++++++++++++++++++++++")
            
            if self.plginInfoFromXML.has_key('plugins'):
                self.print_log("+++++++++++++add auto_load_plu start ++++++++++++++++++++++++")
                plugin_list = self.plginInfoFromXML['plugins']
                print plugin_list
                self.do_auto_load_plu(self.plginInfoFromXML['softwareVer'],plugin_list)
                self.print_log("+++++++++++++add auto_load_plu end ++++++++++++++++++++++++")
                self.getPluginsConfig(self.plginInfoFromXML['plugins'])
                
            if self.plginInfoFromXML.has_key('3rdPartyShaders'):
                self.get3rdPartyShaderConfig(self.plginInfoFromXML['3rdPartyShaders'])
                
            self.doLoadPluginsCfg()
            self.doLoad3rdPartyShaderCfg()
            
        if extraInfo:
            self.doLoadExtraCfg(extraInfo)
        
        return self.errReturn
    def do_auto_load_plu(self,maya_v,plugin_list,*args):
        #self.auto_load_plu(maya_v,"tiffFloatReader") 
        #self.auto_load_plu(maya_v,"OpenEXRLoader") 
        if int(maya_v[:4])>=2014:
            self.auto_load_plu(maya_v,"AbcImport")
        if int(maya_v[:4])>=2015 and int(maya_v[:4])< 2017:
            self.auto_load_plu(maya_v,"xgenToolkit")
        if "miarmy" in plugin_list:
            miarmy_v = maya_v.replace(".","")
            print ("MiarmyProForMaya"+miarmy_v)
            self.auto_load_plu(maya_v,("MiarmyProForMaya"+miarmy_v)) 
        if "vrayformaya" in plugin_list:
            self.auto_load_plu(maya_v,"vrayformaya")
            self.auto_load_plu(maya_v,"xgenVRay")
        if "mtoa" in plugin_list:
            self.auto_load_plu(maya_v,"mtoa")  
        if "realflow" in plugin_list:
            self.auto_load_plu(maya_v,"realflow")  
        if "shaveNode" in plugin_list:
            self.auto_load_plu(maya_v,"shaveNode")             
            # if "pgYetiMaya" in plugin_list:
                # self.auto_load_plu(maya_v,"pgYetiVRayMaya")            

    
    def do_clear_render_pre(self, *args):
        input_SW = args[0][0]
        _V_APP = args[0][1]
        
        if input_SW=="maya":
            self.print_log("time is 2017 07 06 21:36")

   
            #print "set env is  none"
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

            
            
    def do_del_path(self,file_path):
        if os.path.isfile(file_path) and os.path.exists(file_path):
            try:
                os.remove(file_path)
                self.print_log("del file  %s" % file_path)
            except Exception,error:  
                print( Exception,":",error )
                self.print_log("dont del file %s" % file_path)
        if os.path.isdir(file_path) and os.path.exists(file_path):            
            try:                
                shutil.rmtree(file_path)
                self.print_log("del path %s" % file_path)
            except Exception,error:              
                print( Exception,":",error )
                self.print_log("dont del path %s" % file_path)
    def auto_load_plu(self,maya_v,plug_name):
        
        if int(maya_v[:4]) <= 2015:
            maya_v = "%s-x64" % (maya_v)
        print maya_v
        curUserPath = os.environ.get('userprofile')
        pluginPrefsFile = r"%s/Documents/maya/%s/prefs/pluginPrefs.mel" % (curUserPath, maya_v)
        pluginPrefsFile = pluginPrefsFile.replace('\\','/')
        hasPlugPrefs = False
        plug_load = (r'evalDeferred("autoLoadPlugin(\"\", \"%s\", \"%s\")");' + '\n') % (plug_name, plug_name)
        if os.path.exists(pluginPrefsFile):
            print pluginPrefsFile
            mode = "a+"
            with open(pluginPrefsFile, mode) as f:
                lines = f.readlines()
                for line in lines:
                    if plug_load.strip() == line.strip():
                        print ("auto load  %s " % (plug_name))
                        hasPlugPrefs = True
                        break
                if not hasPlugPrefs:
                    print ("write %s for auto load" % (plug_name))
                    f.write(plug_load)
            
            
        else:
            file_dir = os.path.split(pluginPrefsFile)[0]
            if os.path.exists(file_dir)==0:            
                os.makedirs(file_dir)
            print ("makedir %s " % (file_dir))
            mode = "w"
            with open(pluginPrefsFile, mode) as f:
                print ("write %s for auto load" % (plug_name))
                f.write(plug_load)


    def doGetClientInfo(self, *args):
        
        try:
            fp = open(args[0])
    
            if fp:
                try:
                    listOfplgCfg = fp.readlines()
                    removeNL = [(i.rstrip('\n')) for i in listOfplgCfg]
                    combinedText = ''.join(removeNL)
                    #self.plginInfoFromXML = eval('dict(%s)' % combinedText)
                    self.plginInfoFromXML = eval('dict(%s)' % combinedText)
                    self.validPlginInfo = copy.deepcopy(self.plginInfoFromXML)
                    
                except SyntaxError:
                    self.print_log('SyntaxError : error of convert info from plugin.cfg to clientinfo')
                    self.errReturn = 1
            '''
            #for test
            self.plginInfoFromXML = {'renderSoftware':'maya', \
                               'softwareVer':'2012', \
                               'plugins':{'shave':'8.0v01', 'testPlugin':'1.32'}, \
                               '3rdPartyShaders':{'mtoa':{'alshader':'0.3.3'}}}
            '''
        except:
            self.print_log('Read client info error!')
            self.errReturn = 1
    
    
    def setRenderSoftware(self, *args):
        
        inputSW = args[0][0]
        inputVer = args[0][1]
        
        try:
            self.renderSW = inputSW
        except:
            self.print_log('self.renderSW : %s' % self.renderSW)
            self.print_log('Error! Render software invalid!')
            self.errReturn = 1
            
        try:
            self.swVer = inputVer
        except:
            self.print_log('self.swVer : %s' % self.swVer)
            self.print_log('Error! Software version invalid!')
            self.errReturn = 1
            
        self.doParseXml()
            

    def doParseXml(self):
        
        #keywords of element and tag in XML
        eleNamingList = {'attrRenderSWVer':'version', \
                         'tag3rdPtyShdList':'thirdPartyShaderList'}
        
        if self.renderSW and self.swVer:
            #num = re.search('[0-9]+', str(self.swVer))
            #version = num.group()
            version = str(self.swVer)
            doc = et.parse(self.pluginsInfoXml)
            # find all element "maya" --------------------------------------------------
            allRederSW = doc.findall(self.renderSW)
            
            #print 'allRederSW : ', allRederSW
            
            for docSW in allRederSW:
                # if attr "version" 's value is match-----------------------------------
                if version in docSW.get(eleNamingList['attrRenderSWVer']):
                    self.docXml_software = docSW
                    break
                
                else:
                    self.print_log('Software version not found in the XML!')
                    self.errReturn = 1
                
            list_ele3rdPartyShader = doc.findall(eleNamingList['tag3rdPtyShdList'])
            
            #Check if only one element "thirdPartyShaderList" exists ----------
            if len(list_ele3rdPartyShader) == 1:
                self.docXml_3rdPartyShader = list_ele3rdPartyShader[0]
                
            else:
                self.print_log('Number of element 3rdPartyShader error!')
                self.errReturn = 1
            
        else:
            self.print_log('Please execute "setRenderSoftware" first!')
            self.errReturn = 1

            
    
    def getPluginsConfig(self, *args):
        
        pluginInfoInput = args[0]
        #keywords of element and tag in XML
        eleNamingList = {'tagPlginList':'pluginList', \
                         'attrPlginName':'name', \
                         'tagPlginVer':'version', \
                         'attrPlgVer':'pv', \
                         'tagCfgFile':'configFile'}

        
        plginList = self.docXml_software.find(eleNamingList['tagPlginList'])
        
        # check pluginlist is not empty ------------------------------------
        if plginList != None:
            
            dict_xmlPlgins = {}
            
            for p in plginList:
                
                # get attr "name" 's value' --------------------------------
                plginName = p.get(eleNamingList['attrPlginName'])

                # if attr "name" exist -------------------------------------
                if plginName:
                    dict_xmlPlgins.setdefault(plginName, p)
                    
            for k in pluginInfoInput.keys():
                plginNotFound = 1
                
                if k in dict_xmlPlgins.keys():
                    
                    plg = dict_xmlPlgins[k]
                    # find element "version" ---------------------------
                    plgVerList = plg.findall(eleNamingList['tagPlginVer'])
                    
                    for plgver in plgVerList:
                        # get attr "pv" 's value' ----------------------
                        pv = plgver.get(eleNamingList['attrPlgVer'])
                        # if plugin version is match -------------------
                        print 'pluginInfoInput[k]:%s, pv:%s' % (pluginInfoInput[k], pv)
                        if pluginInfoInput[k] == pv:
                            # find element "configPath" ----------------
                            configFileEle = plgver.find(eleNamingList['tagCfgFile'])
                            # check Element "configPath" exists' 
                            if configFileEle != None:
                                # get configPath 's text' --------------
                                configPath = configFileEle.text
                                
                                # check configPath 's text is not empty' 
                                if configPath != None:
                                    # config path append in to the output list 
                                    self.list_pluginsConfigPath.append(configPath)
                                    
                                    plginNotFound = 0
                                    
                                else:
                                    self.print_log('Error !! Element "configFile" is empty ...')
                                    self.errReturn = 1
                            else:
                                self.print_log('Error !! Element "configFile" not found ...')
                                self.errReturn = 1
                
                if plginNotFound:
                    self.print_log('Plugin "%s" configPath not found, please confirm the plugin name and version is correct!' % k)
                    del self.validPlginInfo['plugins'][k]
                    
        else:
            self.print_log('Error !! PluginList not found ...t')
            self.errReturn = 1
    
    
    
    def get3rdPartyShaderConfig(self, *args):
        
        thirdPartyShaderInput = args[0]
        #keywords of element and tag in XML
        eleNamingList = {'tagRenderer':'renderer', \
                         'attrRendererName':'name', \
                         'tagShader':'shader', \
                         'attrShaderName':'name', \
                         'tagShaderVer':'version', \
                         'attrShaderVer':'sv', \
                         'tagCfgFile':'configFile'}
        # Get 3rdPartyShader information when the 3 argument is not None -------
        if thirdPartyShaderInput != None:
            
            rdrInput = thirdPartyShaderInput.keys()
            noOfRdrInput = len(rdrInput)
            #Check only got one renderer is input
            if noOfRdrInput == 1:
                shdListInput = thirdPartyShaderInput[rdrInput[0]].keys()
                noOfShdInput = len(shdListInput)
                # Check any shader is input ------------------------------------
                if noOfShdInput:
                    rdrs = self.docXml_3rdPartyShader.findall(eleNamingList['tagRenderer'])
                    
                    dict_xml3rdShaders = {}
                    
                    for rdr in rdrs:
                        rdrName = rdr.get(eleNamingList['attrRendererName'])
                        
                        if rdrName:
                            dict_xml3rdShaders.setdefault(rdrName, rdr)
                        
                    # if the element of the renderer exists -------------------------------
                    if rdrInput[0] in dict_xml3rdShaders:
                        eleShd = dict_xml3rdShaders[rdrInput[0]]
                        
                        shds = eleShd.findall(eleNamingList['tagShader'])
                        
                        dictOfAllShds = {}
                        # Create a dictionary to compare with the input shader 
                        for shd in shds:
                            shdName = shd.get(eleNamingList['attrShaderName'])
                            
                            if shdName:
                                dictOfAllShds.setdefault(shdName, shd)
                        
                        for shdInput in shdListInput:
                            
                            shdNotFound = 1
                            
                            # if input shader exists -----------------------
                            if shdInput in dictOfAllShds:
                                shdEle = dictOfAllShds[shdInput]
                                shdVerList = shdEle.findall(eleNamingList['tagShaderVer'])
                            
                                for shdVer in shdVerList:
                                    sv = shdVer.get(eleNamingList['attrShaderVer'])
                                    # if the input shader version match ----
                                    if sv == thirdPartyShaderInput[rdrInput[0]][shdInput]:
                                        configFileEle = shdVer.find(eleNamingList['tagCfgFile'])
                                        # check if the element "configFile" exists 
                                        if configFileEle != None:
                                            configFilePath = configFileEle.text
                                            # if the config path is not empty
                                            if configFilePath != None:
                                                self.list_3rdPtyShdPath.append(configFilePath)
                                                
                                                shdNotFound = 0
                                                
                            if shdNotFound:
                                self.print_log('3rdShader "%s" configPath not found, please confirm this shader name and version is correct!' % shdInput)
                                del self.validPlginInfo['3rdPartyShaders'][rdrInput[0]][shdInput]
                                
                                if self.validPlginInfo['3rdPartyShaders'][rdrInput[0]] == {}:
                                    del self.validPlginInfo['3rdPartyShaders'][rdrInput[0]]
                     
                else:
                    self.print_log('%i shader input!' % noOfShdInput)
                    self.errReturn = 1
                                    
            else:
                self.print_log('%i renderer input!' % noOfRdrInput)
                self.errReturn = 1
    
    
    def doLoadPluginsCfg(self):
        self.print_log('plugins \'s config path : %s' % self.list_pluginsConfigPath)
        
        for cfgFile in self.list_pluginsConfigPath:
            
            # Check is the config file exists ----------------------------------
            if os.path.exists(cfgFile):
                # get the directory of config.py ---------------------------------------
                cfgFileDir = os.path.dirname(cfgFile)
                # add the path ---------------------------------------------------------
                sys.path.append(cfgFileDir)
                # Check is the path add success ----------------------------------------
                #print 'sys.path after append :', sys.path
                try:
                    # import the config module from ----------------------------------------
                    cfg = __import__('config')
                    # confirm the module is the most update --------------------------------
                    reload(cfg)
                    # excute the doConfigSetup ---------------------------------------------
                    #cfg.doConfigSetup(self.plginInfoFromXML)
                    print 'a', clientRenderInfo(self.validPlginInfo)
                    cfg.doConfigSetup(clientRenderInfo(self.validPlginInfo))
                                
                except Exception as err:
                    self.print_log('=== Error occur import/execute "%s"! ===\n=== Error Msg : %s ===' % (cfgFile, err))
                    self.errReturn = 1
                
                
                
                # remove the config file path ------------------------------------------
                try:
                    while True:
                        sys.path.remove(cfgFileDir)
                        
                except:
                    pass
                #confirm the config file path removed
                #print 'sys.path after import :', sys.path
            else:
                self.print_log('Config file "%s" is not exists!' % cfgFile)
                self.errReturn = 1
                            
    
    def doLoad3rdPartyShaderCfg(self):
        self.print_log('3rdPartyShaders \'s config path : %s' % self.list_3rdPtyShdPath)
        
        for cfgFile in self.list_3rdPtyShdPath:
            # get the directory of config.py ---------------------------------------
            cfgFileDir = os.path.dirname(cfgFile)
            # add the path ---------------------------------------------------------
            sys.path.append(cfgFileDir)
            # Check is the path add success ----------------------------------------
            #print 'sys.path after append :', sys.path

            # //--------------------------------
            ## edit by shen 2018.1.18
            load_time=1
            while load_time<3:
                try:
                    # import the config module from ----------------------------------------
                    cfg = __import__('config')
                    # confirm the module is the most update --------------------------------
                    reload(cfg)
                    # excute the doConfigSetup ---------------------------------------------
                    #cfg.doConfigSetup(self.plginInfoFromXML)
                    cfg.doConfigSetup(clientRenderInfo(self.validPlginInfo))

                except Exception as err:
                    ## delet config.pyc
                    pyc_file = os.path.join(cfgFileDir,"config.pyc")
                    try:
                        self.print_log("Try to remove the config.pyc file.")
                        os.remove(pyc_file)
                    except:
                        pass
                    load_time +=1
                    if load_time >=3:
                        self.print_log('=== Error occur import/execute "%s"! ===\n=== Error Msg : %s ===' % (cfgFile, err))
                        self.errReturn = 1

            # remove the config file path ------------------------------------------
            try:
                while True:
                    sys.path.remove(cfgFileDir)
                    
            except:
                pass


    def doLoadExtraCfg(self, *args):
        
        extraCfgs = args[0]
        
        for cfgFile in extraCfgs:
            # Check is the file exists -----------------------------------------
            if os.path.exists(cfgFile):
                # get the directory of config.py ---------------------------------------
                cfgFileDir = os.path.dirname(cfgFile)
                cfgFileName = os.path.splitext(os.path.split(cfgFile)[-1])[0]
                # add the path ---------------------------------------------------------
                sys.path.append(cfgFileDir)
                # Check is the path add success ----------------------------------------
                #print 'sys.path after append :', sys.path
                try:
                    # import the config module from ----------------------------------------
                    cfg = __import__(cfgFileName)
                    # confirm the module is the most update --------------------------------
                    reload(cfg)
                    # excute the doConfigSetup ---------------------------------------------
                    #cfg.doConfigSetup(self.plginInfoFromXML)
        
                    cfg.doConfigSetup(clientRenderInfo(self.validPlginInfo))
                    
                except Exception as err:
                    self.print_log('=== Error occur import/execute "%s"! ===\n=== Error Msg : %s ===' % (cfgFile, err))
                    self.errReturn = 1
                    
                    
                # remove the config file path ------------------------------------------
                try:
                    while True:
                        sys.path.remove(cfgFileDir)
                        
                except:
                    pass
                
            else:
                self.print_log('extrainfo file %s is not exists!' % cfgFile)
            


class clientRenderInfo():
    
    def __init__(self, *args):
        self.plginInfo = args[0]
    
    def rdrSW(self, *args):
        if self.plginInfo.has_key('renderSoftware'):
            return self.plginInfo['renderSoftware']
        else:
            return None
    
    def swVer(self, *args):
        if self.plginInfo.has_key('softwareVer'):
            return self.plginInfo['softwareVer']
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
    
    #===========================================================================
    # Step of using PluginLoader:
    # 1. run setRenderSoftware with the input software and version
    # 2. run getPluginsConfig to get the configure path of shader (result is "list_pluginsConfigPath")
    # 3. run get3rdPartyShaderConfig to get the configure path of the 3rdPartyShader (result is "list_3rdPtyShdPath")
    # 4. run doLoadPluginsCfg/doLoad3rdPartyShaderCfg to import and run!
    #===========================================================================
    
    plginsLd = RayvisionPluginsLoader()
    rtn = plginsLd.RayvisionPluginsLoader('C:\Users\sanchan\workspace\mayaApp\src\mayaConfig\plugins.cfg', [])
    print 'rtn', rtn
    
    '''
    optParser = OptionParser()
    optParser.add_option('-c', '--ci', type='string', dest='clientInfo')
    optParser.add_option('-e', '--ei', type='string', dest='extraInfo')
    
    options,args = optParser.parse_args(sys.argv[1:])
    
    if len(sys.argv) > 1:
        
        plginsLd = RayvisionPluginsLoader()
        plginsLd.doGetClientInfo(options.clientInfo)
        
        if plginsLd.plginInfoFromXML:
            plginsLd.setRenderSoftware([plginsLd.plginInfoFromXML['renderSoftware'], plginsLd.plginInfoFromXML['softwareVer']])
        
            if plginsLd.plginInfoFromXML.has_key('plugins'):
                plginsLd.getPluginsConfig(plginsLd.plginInfoFromXML['plugins'])
                
            if plginsLd.plginInfoFromXML.has_key('3rdPartyShaders'):
                plginsLd.get3rdPartyShaderConfig(plginsLd.plginInfoFromXML['3rdPartyShaders'])
                
            plginsLd.doLoadPluginsCfg()
            plginsLd.doLoad3rdPartyShaderCfg()
            
        if options.extraInfo:
            plginsLd.doLoadExtraCfg(options.extraInfo)
        
    else:
        print 'Argument not found!'
    
    '''

