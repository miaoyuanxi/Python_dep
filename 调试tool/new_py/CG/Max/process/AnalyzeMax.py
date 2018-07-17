#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os,sys,subprocess,string,logging,time,shutil
import glob
import logging
import codecs
import configparser
import json
import gc
import xml.etree.ElementTree as ET
import re
import operator


from Max import Max
from MaxPlugin import MaxPlugin
# from MaxDog import DogUtil

from CommonUtil import RBCommon as CLASS_COMMON_UTIL
from MaxUtil import RBMaxUtil as CLASS_MAX_UTIL



class ConflictPlugin:
    def __init__(self): 
        self.VRAY_MULTISCATTER=["2010_2.00.01_1.0.18a","2010_2.00.02_1.0.18a","2010_2.10.01_1.0.18a","2010_2.20.02_1.0.18a",
        "2010_2.40.03_1.0.18a","2010_2.00.01_1.1.05","2010_2.00.02_1.1.05","2010_2.10.01_1.1.05",
        "2010_2.20.02_1.1.05","2010_2.40.03_1.1.05","2010_2.00.01_1.1.05a","2010_2.00.02_1.1.05a",
        "2010_2.10.01_1.1.05a","2010_2.20.02_1.1.05a","2010_2.40.03_1.1.05a","2010_2.00.01_1.1.07a",
        "2010_2.00.02_1.1.07a","2010_2.10.01_1.1.07a","2010_2.20.02_1.1.07a","2010_2.40.03_1.1.07a",
        "2010_2.00.01_1.1.08b","2010_2.00.02_1.1.08b","2010_2.10.01_1.1.08b","2010_2.20.02_1.1.08b",
        "2010_2.40.03_1.1.08b","2010_2.00.01_1.1.09","2010_2.00.02_1.1.09","2010_2.10.01_1.1.09",
        "2010_2.20.02_1.1.09","2010_2.40.03_1.1.09","2010_2.00.01_1.1.09a","2010_2.00.02_1.1.09a",
        "2010_2.10.01_1.1.09a","2010_2.20.02_1.1.09a","2010_2.40.03_1.1.09a","2010_2.00.01_1.1.09c",
        "2010_2.00.02_1.1.09c","2010_2.10.01_1.1.09c","2010_2.20.02_1.1.09c","2010_2.40.03_1.1.09c",
        "2010_2.00.01_1.1.09d","2010_2.00.02_1.1.09d","2010_2.10.01_1.1.09d","2010_2.20.02_1.1.09d",
        "2010_2.40.03_1.1.09d","2010_2.00.01_1.2.0.3","2010_2.00.02_1.2.0.3","2010_2.10.01_1.2.0.3",
        "2010_2.20.02_1.2.0.3","2010_2.40.03_1.2.0.3","2010_2.00.01_1.2.0.123.0","2010_2.00.02_1.2.0.123.0",
        "2010_2.10.01_1.2.0.123.0","2010_2.20.02_1.2.0.123.0","2010_2.40.03_1.2.0.123.0","2010_2.00.01_1.3.1.3a",
        "2010_2.00.02_1.3.1.3a","2010_2.10.01_1.3.1.3a","2010_2.20.02_1.3.1.3a","2010_2.40.03_1.3.1.3a",
        "2011_2.00.01_1.0.18a","2011_2.00.02_1.0.18a","2011_2.10.01_1.0.18a","2011_2.20.02_1.0.18a",
        "2011_2.20.03_1.0.18a","2011_2.40.03_1.0.18a","2011_3.30.04_1.0.18a","2011_3.30.05_1.0.18a",
        "2011_2.00.01_1.1.05","2011_2.00.02_1.1.05","2011_2.10.01_1.1.05","2011_2.20.02_1.1.05",
        "2011_2.20.03_1.1.05","2011_2.40.03_1.1.05","2011_3.30.04_1.1.05","2011_3.30.05_1.1.05",
        "2011_2.00.01_1.1.05a","2011_2.00.02_1.1.05a","2011_2.10.01_1.1.05a","2011_2.20.02_1.1.05a",
        "2011_2.20.03_1.1.05a","2011_2.40.03_1.1.05a","2011_3.30.04_1.1.05a","2011_3.30.05_1.1.05a",
        "2011_2.00.01_1.1.07a","2011_2.00.02_1.1.07a","2011_2.10.01_1.1.07a","2011_2.20.02_1.1.07a",
        "2011_2.20.03_1.1.07a","2011_2.40.03_1.1.07a","2011_3.30.04_1.1.07a","2011_3.30.05_1.1.07a",
        "2011_2.00.01_1.1.08b","2011_2.00.02_1.1.08b","2011_2.10.01_1.1.08b","2011_2.20.02_1.1.08b",
        "2011_2.20.03_1.1.08b","2011_2.40.03_1.1.08b","2011_3.30.04_1.1.08b","2011_3.30.05_1.1.08b",
        "2011_2.00.01_1.1.09","2011_2.00.02_1.1.09","2011_2.10.01_1.1.09","2011_2.20.02_1.1.09",
        "2011_2.20.03_1.1.09","2011_2.40.03_1.1.09","2011_3.30.04_1.1.09","2011_3.30.05_1.1.09",
        "2011_2.00.01_1.1.09a","2011_2.00.02_1.1.09a","2011_2.10.01_1.1.09a","2011_2.20.02_1.1.09a",
        "2011_2.20.03_1.1.09a","2011_2.40.03_1.1.09a","2011_3.30.04_1.1.09a","2011_3.30.05_1.1.09a",
        "2011_2.00.01_1.1.09c","2011_2.00.02_1.1.09c","2011_2.10.01_1.1.09c","2011_2.20.02_1.1.09c",
        "2011_2.20.03_1.1.09c","2011_2.40.03_1.1.09c","2011_3.30.04_1.1.09c","2011_3.30.05_1.1.09c",
        "2011_2.00.01_1.1.09d","2011_2.00.02_1.1.09d","2011_2.10.01_1.1.09d","2011_2.20.02_1.1.09d",
        "2011_2.20.03_1.1.09d","2011_2.40.03_1.1.09d","2011_3.30.04_1.1.09d","2011_3.30.05_1.1.09d",
        "2011_2.00.01_1.2.0.3","2011_2.00.02_1.2.0.3","2011_2.10.01_1.2.0.3","2011_2.20.02_1.2.0.3",
        "2011_2.20.03_1.2.0.3","2011_2.40.03_1.2.0.3","2011_3.30.04_1.2.0.3","2011_3.30.05_1.2.0.3",
        "2011_2.00.01_1.2.0.123.0","2011_2.00.02_1.2.0.123.0","2011_2.10.01_1.2.0.123.0",
        "2011_2.20.02_1.2.0.123.0","2011_2.20.03_1.2.0.123.0","2011_2.40.03_1.2.0.123.0","2011_3.30.04_1.2.0.123.0",
        "2011_3.30.05_1.2.0.123.0","2011_2.00.01_1.3.1.3a","2011_2.00.02_1.3.1.3a","2011_2.10.01_1.3.1.3a","2011_2.20.02_1.3.1.3a",
        "2011_2.20.03_1.3.1.3a","2011_2.40.03_1.3.1.3a","2011_3.30.04_1.3.1.3a","2011_3.30.05_1.3.1.3a","2012_2.00.03_1.1.07a",
        "2012_2.10.01_1.1.07a","2012_2.20.02_1.1.07a","2012_2.20.03_1.1.07a","2012_2.30.01_1.1.07a","2012_2.40.03_1.1.07a",
        "2012_3.30.04_1.1.07a","2012_3.30.05_1.1.07a","2012_3.40.01_1.1.07a","2012_2.00.03_1.1.08b","2012_2.10.01_1.1.08b",
        "2012_2.20.02_1.1.08b","2012_2.20.03_1.1.08b","2012_2.30.01_1.1.08b","2012_2.40.03_1.1.08b","2012_3.30.04_1.1.08b",
        "2012_3.30.05_1.1.08b","2012_3.40.01_1.1.08b","2012_2.00.03_1.1.09","2012_2.10.01_1.1.09","2012_2.20.02_1.1.09",
        "2012_2.20.03_1.1.09","2012_2.30.01_1.1.09","2012_2.40.03_1.1.09","2012_3.30.04_1.1.09","2012_3.30.05_1.1.09",
        "2012_3.40.01_1.1.09","2012_2.00.03_1.1.09a","2012_2.10.01_1.1.09a","2012_2.20.02_1.1.09a","2012_2.20.03_1.1.09a",
        "2012_2.30.01_1.1.09a","2012_2.40.03_1.1.09a","2012_3.30.04_1.1.09a","2012_3.30.05_1.1.09a","2012_3.40.01_1.1.09a",
        "2012_2.00.03_1.1.09c","2012_2.10.01_1.1.09c","2012_2.20.02_1.1.09c","2012_2.20.03_1.1.09c","2012_2.30.01_1.1.09c",
        "2012_2.40.03_1.1.09c","2012_3.30.04_1.1.09c","2012_3.30.05_1.1.09c","2012_3.40.01_1.1.09c","2012_2.00.03_1.1.09d",
        "2012_2.10.01_1.1.09d","2012_2.20.02_1.1.09d","2012_2.20.03_1.1.09d","2012_2.30.01_1.1.09d","2012_2.40.03_1.1.09d",
        "2012_3.30.04_1.1.09d","2012_3.30.05_1.1.09d","2012_3.40.01_1.1.09d","2012_2.00.03_1.2.0.3","2012_2.10.01_1.2.0.3",
        "2012_2.20.02_1.2.0.3","2012_2.20.03_1.2.0.3","2012_2.30.01_1.2.0.3","2012_2.40.03_1.2.0.3","2012_3.30.04_1.2.0.3",
        "2012_3.30.05_1.2.0.3","2012_3.40.01_1.2.0.3","2012_2.00.03_1.2.0.123.0","2012_2.10.01_1.2.0.123.0","2012_2.20.02_1.2.0.123.0",
        "2012_2.20.03_1.2.0.123.0","2012_2.30.01_1.2.0.123.0","2012_2.40.03_1.2.0.123.0","2012_3.30.04_1.2.0.123.0","2012_3.30.05_1.2.0.123.0",
        "2012_3.40.01_1.2.0.123.0","2012_2.00.03_1.3.1.3a","2012_2.10.01_1.3.1.3a","2012_2.20.02_1.3.1.3a","2012_2.20.03_1.3.1.3a",
        "2012_2.30.01_1.3.1.3a","2012_2.40.03_1.3.1.3a","2012_3.30.04_1.3.1.3a","2012_3.30.05_1.3.1.3a","2012_3.40.01_1.3.1.3a",
        "2013_2.30.01_1.1.09c","2013_2.40.03_1.1.09c","2013_2.40.04_1.1.09c","2013_3.30.04_1.1.09c","2013_3.30.05_1.1.09c","2013_3.40.01_1.1.09c",
        "2013_2.30.01_1.1.09d","2013_2.40.03_1.1.09d","2013_2.40.04_1.1.09d","2013_3.30.04_1.1.09d","2013_3.30.05_1.1.09d","2013_3.40.01_1.1.09d",
        "2013_2.30.01_1.2.0.12","2013_2.40.03_1.2.0.12","2013_2.40.04_1.2.0.12","2013_3.30.04_1.2.0.12","2013_3.30.05_1.2.0.12",
        "2013_3.40.01_1.2.0.12","2013_2.30.01_1.2.0.3","2013_2.40.03_1.2.0.3","2013_2.40.04_1.2.0.3","2013_3.30.04_1.2.0.3",
        "2013_3.30.05_1.2.0.3","2013_3.40.01_1.2.0.3","2013_2.30.01_1.2.0.123.0","2013_2.40.03_1.2.0.123.0","2013_2.40.04_1.2.0.123.0",
        "2013_3.30.04_1.2.0.123.0","2013_3.30.05_1.2.0.123.0","2013_3.40.01_1.2.0.123.0","2013_2.30.01_1.3.1.3a","2013_2.40.03_1.3.1.3a",
        "2013_2.40.04_1.3.1.3a","2013_3.30.04_1.3.1.3a","2013_3.30.05_1.3.1.3a","2013_3.40.01_1.3.1.3a","2014_2.30.01_1.1.09c",
        "2014_2.40.03_1.1.09c","2014_2.40.04_1.1.09c","2014_3.30.04_1.1.09c","2014_3.30.05_1.1.09c","2014_3.40.01_1.1.09c",
        "2014_2.30.01_1.1.09d","2014_2.40.03_1.1.09d","2014_2.40.04_1.1.09d","2014_3.30.04_1.1.09d","2014_3.30.05_1.1.09d",
        "2014_3.40.01_1.1.09d","2014_2.30.01_1.2.0.12","2014_2.40.03_1.2.0.12","2014_2.40.04_1.2.0.12","2014_3.30.04_1.2.0.12",
        "2014_3.30.05_1.2.0.12","2014_3.40.01_1.2.0.12","2014_2.30.01_1.2.0.3","2014_2.40.03_1.2.0.3","2014_2.40.04_1.2.0.3",
        "2014_3.30.04_1.2.0.3","2014_3.30.05_1.2.0.3","2014_3.40.01_1.2.0.3","2014_2.30.01_1.2.0.123.0","2014_2.40.03_1.2.0.123.0",
        "2014_2.40.04_1.2.0.123.0","2014_3.30.04_1.2.0.123.0","2014_3.30.05_1.2.0.123.0","2014_3.40.01_1.2.0.123.0","2014_2.30.01_1.3.1.3a",
        "2014_2.40.03_1.3.1.3a","2014_2.40.04_1.3.1.3a_","2014_3.30.04_1.3.1.3a","2014_3.30.05_1.3.1.3a","2014_3.40.01_1.3.1.3a"]
        
    def max_plugin_conflict(self,max='',plugin1='',plugin2=''):
        
        print('-----conflict Plugin--------')
        print(max)
        print(plugin1)
        print(plugin2)
        str_a=max+"_"+plugin1+"_"+plugin2
       
        if str_a  in self.VRAY_MULTISCATTER: 
            print("True!")
            return True
        else:
            print("False")
            return False

class RenderbusPath():
    def __init__(self,user_path,asset_collect_absolute_path):
        self.G_INPUT_USER=user_path
        self.ASSET_WEB_COOLECT_BY_PATH=asset_collect_absolute_path
    def inter_path(self,p):
        first_two = p[0:2]
        if first_two == '//' or first_two == '\\\\':
            norm_path = p.replace('\\', '/')
            index = norm_path.find('/', 2)
            if index <= 2:
                return False
            return True
        
    def parse_inter_path(self,p):
        first_two = p[0:2]
        if first_two == '//' or first_two == '\\\\':
            norm_path = p.replace('\\', '/')
            index = norm_path.find('/', 2)
            if index <= 2:
                return ''
            
            return p[:index],p[index:]

    def convert_path(self,item_path):
        if self.ASSET_WEB_COOLECT_BY_PATH:
            abs_path=[['a:/','/a/'],
                ['b:/','/b/'],
                ['c:/','/c/'],
                ['d:/','/d/']]
                
            result_file = item_path
            lower_file = os.path.normpath(item_path.lower()).replace('\\', '/')
            is_abcd_path = False;
            is_inter_path = False;
            file_dir=os.path.dirname(lower_file)
            if file_dir==None or file_dir.strip()=='':
                return os.path.normpath(result_file)
            else:
                if self.inter_path(lower_file):
                    start,rest = self.parse_inter_path(lower_file)
                    #result_file= self.G_INPUT_USER + '/net' + start.replace('//', '/') + rest.replace('\\', '/') 
                    result_file= self.G_INPUT_USER + '/__'+ start.replace('//', '')+ rest.replace('\\', '/') 
                else:
                    result_file= self.G_INPUT_USER + '\\' + item_path.replace('\\', '/').replace(':','')

                return os.path.normpath(result_file)
        else:
            return item_path
            
    def convert_to_user_path(self,source_file):
        result_file = source_file
        user_input=self.G_INPUT_USER
        user_input=user_input.replace('/','\\')
        source_file=source_file.replace('/','\\').replace(user_input,'')
        
        #if source_file.startswith('net'):
        if source_file.startswith('__'):
            result_file = '\\\\'+source_file[2:]
            #result_file=result_file.replace('\\','/')
        elif source_file.startswith('a\\') or source_file.startswith('b\\') or source_file.startswith('c\\') or source_file.startswith('d\\'):
            result_file = source_file[0]+':'+source_file[1:]
            result_file=result_file.replace('\\','/')
        else:
            result_file=source_file[0]+':'+source_file[1:]
            result_file=result_file.replace('\\','/')
        
        return result_file
        

        
        
        
class MaxResult():
    def __init__(self):
        pass
        
class AnalyzeMax(Max):
    def __init__(self,**paramDict):
        Max.__init__(self,**paramDict)
        print("max.INIT")

        # self.G_MAX_B='B:/plugins/max'
        # self.G_NODE_MAXSCRIPT='C:/script/new_py/CG/Max/maxscript'
        self.G_MAXSCRIPT_NAME_U='analyseU.ms'#max2013,max2014,max2015
        self.G_MAXSCRIPT_NAME_A='analyseA.ms'#max2012,max2011,max2010
        
        self.G_ANALYZE_TXT_NODE=os.path.join(self.G_WORK_RENDER_TASK_CFG,'analyze.txt').replace('\\','/')
        self.G_PROPERTY_TXT_NODE=os.path.join(self.G_WORK_RENDER_TASK_CFG,'property.txt').replace('\\','/')
        self.G_TIPS_TXT_NODE=os.path.join(self.G_WORK_RENDER_TASK_CFG,'tips.json').replace('\\','/')
        
        
        self.G_INPUT_PROJECT_ASSET_DICT={}
        # self.ASSET_WEB_COOLECT_BY_PATH=False
        
        
        self.G_PROGRAMFILES='C:/Program Files/Autodesk'
        
        
        self.G_MAXFIND='B:/plugins/max/maxfind/GetMaxProperty.exe'
        self.G_MAXFIND_MAX_VERSION_STR=None
        self.G_MAXFIND_MAX_VERSION_INT=None
        self.G_MAXFIND_RENDERER=None
        self.G_MAXFIND_OUTPUT_GAMMA=None
        
        
        self.renderbus_path_obj   = RenderbusPath(self.G_INPUT_USER_PATH,self.ASSET_WEB_COOLECT_BY_PATH)
        self.check_if_l_items     = []
        #self.assetInputItems    = []
        self.asset_input_count   = 1
        self.input_missing_items  = []
        self.input_missing_count  = 1
        
        self.TIPS_DICT={}
        self.TIPS_LIST=[]
        self.CONFLICT_PLUGIN=ConflictPlugin()
        
        
        self.TIPS_CODE_DICT={}
        self.TIPS_CODE_DICT['vdb_missing']='10028'
        self.TIPS_CODE_DICT['realflow_missing']='15022'
        self.TIPS_CODE_DICT['vrmesh_missing']='10030'
        self.TIPS_CODE_DICT['hdri_missing']='10012'
        self.TIPS_CODE_DICT['vrmap_missing']='10023'
        self.TIPS_CODE_DICT['vrlmap_missing']='10024'
        self.TIPS_CODE_DICT['fumefx_missing']='10011'
        self.TIPS_CODE_DICT['phoenifx_missing']='10022'
        self.TIPS_CODE_DICT['firesmokesim_missing']='10022'
        self.TIPS_CODE_DICT['liquidsim_missing']='10022'
        self.TIPS_CODE_DICT['kk_missing']='10019'
        self.TIPS_CODE_DICT['xmesh_missing']='10020'
        self.TIPS_CODE_DICT['animation_map_missing']='10027'
        self.TIPS_CODE_DICT['realflow_missing']='10021'
        self.TIPS_CODE_DICT['texture_missing']='10012'
        self.TIPS_CODE_DICT['phoenix_missing']='10012'
        self.TIPS_CODE_DICT['pc_missing']='10029'
        self.TIPS_CODE_DICT['pointcache_missing']='10018'
        
        self.TIPS_CODE_DICT['max_version_not_match']='15008'
        self.TIPS_CODE_DICT['maxinfo_failed']='15002'
        
        self.TIPS_CODE_DICT['conflict_multiscatter_vray']='15021'
        self.TIPS_CODE_DICT['max_notmatch']='15013'
        self.TIPS_CODE_DICT['camera_duplicat']='15015'
        self.TIPS_CODE_DICT['element_duplicat']='15016'
        self.TIPS_CODE_DICT['vrmesh_ext_null']='15018'
        self.TIPS_CODE_DICT['proxy_enable']='15010'
        self.TIPS_CODE_DICT['renderer_notsupport']='15004'
        self.TIPS_CODE_DICT['camera_null']='15006'
        self.TIPS_CODE_DICT['task_folder_failed']='15011'
        self.TIPS_CODE_DICT['task_create_failed']='15012'
        self.TIPS_CODE_DICT['multiframe_notsupport']='10015'#irradiance map mode :  \'multiframe incremental\' not supported
        self.TIPS_CODE_DICT['addtocmap_notsupport']='10014'#irradiance map mode : add to current map not supported
        self.TIPS_CODE_DICT['ppt_notsupport']='10016'#'light cache mode : \'progressive path tracing\' not supported '
        self.TIPS_CODE_DICT['vray_hdri_notsupport']='999'
        self.TIPS_CODE_DICT['gamma_on']='10013'
        self.TIPS_CODE_DICT['xreffiles']='10025'
        self.TIPS_CODE_DICT['xrefobj']='10026'
        self.TIPS_CODE_DICT['bad_material']='10010'
        self.TIPS_CODE_DICT['vrimg_undefined']='10017'#--'\'render to v-ray raw image file\' checked but *.vrimg is undefined '
        self.TIPS_CODE_DICT['channel_file_undefined']='15017'#--'save separate render channels checked but channels file is error'
        
        self.TIPS_CODE_DICT['warn_renderable_camera_null']='10035'#--"When the switch on 'Enable scene parameter modification' is opened, if the renderable camera is not selected, a warning is required to prevent the batch submission"
        self.TIPS_CODE_DICT['warn_filename_filetype_null']='10036'#--"When the switch on 'Enable scene parameter modification' is opened, if the filename or filetype is null, a warning is required to prevent the batch submission"
        self.TIPS_CODE_DICT['error_renderable_camera_null']='15040'#--"When the switch on 'Enable scene parameter modification' is closed, if the renderable camera is not selected, a error is required to prevent the batch submission"
        self.TIPS_CODE_DICT['error_filename_filetype_null']='15041'#--"When the switch on 'Enable scene parameter modification' is closed, if the filename or filetype is null, a error is required to prevent the batch submission"
        
        self.TIPS_CODE_DICT['duplicate_texture']='10031'
        self.TIPS_CODE_DICT['unknow_err']='999'
        self.TIPS_CODE_DICT['unknow_warn']='888'
        self.TIPS_CODE_DICT['missing_file']='10012'
        
        print('\r\n==================================================\r\n')
        if not os.path.exists(self.G_WORK_RENDER_TASK_CFG):
            os.makedirs(self.G_WORK_RENDER_TASK_CFG)
        
        if  os.path.exists(self.G_ANALYZE_TXT_NODE):
            os.remove(self.G_ANALYZE_TXT_NODE)#debug______
            pass
        #----------------------------------------------print global param---------------------------------------------------
        # global_param_dict= self.__dict__
        # for key,value in list(global_param_dict.items()):
            # print(key+'='+str(value))
            
            
        
    def RB_HAN_FILE(self):#3copy max file
        self.G_DEBUG_LOG.info('[max.RBhanFile.start.....]')
        
        #-------------------------copy max file-------------------------------
        copy_cmd_str = r'C:\fcopy\FastCopy.exe /speed=full /force_close /no_confirm_stop /force_start "' + os.path.join(self.G_INPUT_CG_FILE.replace('/','\\'))+'" /to="'+self.G_WORK_RENDER_TASK.replace('/','\\')+'\\max\\"'
        # print(str(copy_cmd_str))
        # copy_cmd_str=copy_cmd_str.encode(sys.getfilesystemencoding())
        # cmd_result_code,cmd_result_str=CLASS_COMMON_UTIL.cmd(copy_cmd_str,my_log=self.G_DEBUG_LOG)
        # if cmd_result_code!=0:
            # CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG,'copy max file failed')
        # CLASS_COMMON_UTIL.cmd_python3(copy_cmd_str,my_log = self.G_DEBUG_LOG)
        CLASS_COMMON_UTIL.cmd(copy_cmd_str,my_log = self.G_DEBUG_LOG)
        self.G_DEBUG_LOG.info('[max.RBhanFile.end.....]')
        
    def RB_CONFIG(self):#5
        self.G_DEBUG_LOG.info('[Max.RBconfig.start.....]')
        
        '''
        clean_mount_from='net use * /del /y'
        CLASS_COMMON_UTIL.cmd(clean_mount_from,try_count=3)
        if not os.path.exists(r'B:\plugins'):
            cmd='net use B: '+self.G_PLUGIN_PATH.replace('/','\\').replace("10.60.100.151","10.60.100.152")
            CLASS_COMMON_UTIL.cmd(cmd,try_count=3)
        '''
        #kill 3dsmax.exe,3dsmaxcmd.exe,vrayspawner*.exe
        CLASS_MAX_UTIL.killMaxVray(self.G_DEBUG_LOG)
        
        self.maxfind()
        self.config_max_plugin()
        self.G_DEBUG_LOG.info('[Max.RBconfig.end.....]')
        
    def RB_RENDER(self):#7
        #return#
        self.G_DEBUG_LOG.info('[max.RBanalyse.start.....]')
        
        
       #"C:/Program Files/Autodesk/3ds Max 2014/3dsmax.exe" -silent -ma -mxs "filein \"B:/plugins/max/script/analyseU.ms";analyseRun \"962712\" \"20628\" \"C:\work\helper\20628\max\要命要命不是人.max\" \"C:\work\helper\20628\cfg\analyse_net.txt\" "
        max_exe = self.G_PROGRAMFILES+'/'+self.G_CG_VERSION+'/3dsmax.exe'
        
        #helper_max_file = self.G_WORK_RENDER_TASK + '\\max\\' + os.path.basename(self.G_INPUT_CG_FILE) 
        #analyze_cmd = max_exe + '" -silent -ma -mxs "filein \\"'+ms_script +'\\";analyseRun \\"' + self.G_USER_ID +'\\" \\"' + self.G_BIG_TASK_ID + '\\" \\"' + helper_max_file.replace('\\','/') + '\\" \\"' + self.G_ANALYZE_TXT_NODE.replace('\\','/') + '\\" "'
        ms_file=self.write_ms_file()
        
        plugin_dict=self.G_CG_CONFIG_DICT['plugins']
        stand_vray_list=[]
        stand_vray_list.append('3ds Max 2016_vray3.30.05')
        stand_vray_list.append('3ds Max 2015_vray3.30.05')
        stand_vray_list.append('3ds Max 2014_vray3.30.05')
        stand_vray_list.append('3ds Max 2016_vray3.40.01')
        stand_vray_list.append('3ds Max 2015_vray3.40.01')
        stand_vray_list.append('3ds Max 2014_vray3.40.01')
        
        renderer=''
        if 'vray' in plugin_dict:
            renderer='vray'+plugin_dict['vray']
        stand_vray_str=self.G_CG_VERSION+'_'+renderer
        
        self.G_DEBUG_LOG.info('\r\n\r\n==========================')
        self.G_DEBUG_LOG.info(stand_vray_str)
        
        
        analyze_cmd = '"'+max_exe +'" -silent  -U MAXScript "'+ms_file+'"'
        if stand_vray_str in stand_vray_list:
            analyze_cmd = '"'+max_exe +'"   -U MAXScript "'+ms_file+'"'
        # analyze_cmd = analyze_cmd.encode(sys.getfilesystemencoding())
        #CLASS_MAX_UTIL.max_cmd(analyze_cmd,self.G_DEBUG_LOG,True,True)#debug__________
        # self.G_KAFKA_MESSAGE_DICT['start_time']=str(int(time.time()))
        self.G_FEE_PARSER.set('render','start_time',str(int(time.time())))
        self.G_DEBUG_LOG.info("\n\n-------------------------------------------Start max program-------------------------------------\n\n")
        analyze_code,analyze_result=CLASS_COMMON_UTIL.cmd(analyze_cmd,my_log=self.G_DEBUG_LOG,continue_on_error=True,my_shell=True,callback_func=CLASS_MAX_UTIL.max_cmd_callback)
        
        # self.G_KAFKA_MESSAGE_DICT['end_time']=str(int(time.time()))
        self.G_FEE_PARSER.set('render','end_time',str(int(time.time())))
        self.G_DEBUG_LOG.info('[max.RBanalyse.end.....]')
        #sys.exit(-1)
        

    def RB_HAN_RESULT(self):#8
        self.format_log('结果处理','start')
        self.G_DEBUG_LOG.info('[AnalyzeMax.RB_HAN_RESULT.start.....]') 
        if not os.path.exists(self.G_ANALYZE_TXT_NODE):
            CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG,'Analyze max file failed . result file analyze.txt not exists')
        
        task_json_name='task.json'
        asset_json_name='asset.json'
        tips_json_name='tips.json'
        node_task_json = os.path.join(self.G_WORK_RENDER_TASK_CFG,task_json_name)
        node_asset_json = os.path.join(self.G_WORK_RENDER_TASK_CFG,asset_json_name)
        node_tips_json = os.path.join(self.G_WORK_RENDER_TASK_CFG,tips_json_name)
        
        
        self.parse_analyze_txt()
        scene_info_dict=self.han_task_json(node_task_json)
        asset_json_dict=self.han_asset_json(node_asset_json)
        self.han_tips_json(node_tips_json,scene_info_dict,asset_json_dict)
        CLASS_COMMON_UTIL.python_copy(os.path.normpath(self.G_ANALYZE_TXT_NODE),os.path.normpath(self.G_CONFIG_PATH))
        CLASS_COMMON_UTIL.python_copy(os.path.normpath(self.G_PROPERTY_TXT_NODE),os.path.normpath(self.G_CONFIG_PATH))
        self.G_DEBUG_LOG.info('[AnalyzeMax.RB_HAN_RESULT.end.....]') 
        
        
        Max.RB_HAN_RESULT(self)
        
        
        #self.G_DEBUG_LOG.info('[BASE.RBhanResult.node_task_json.....]'+node_task_json)
        #self.G_DEBUG_LOG.info('[BASE.RBhanResult.node_asset_json.....]'+node_asset_json)
        #self.G_DEBUG_LOG.info('[BASE.RBhanResult.server_task_json.....]'+self.G_TASK_JSON)
        #self.G_DEBUG_LOG.info('[BASE.RBhanResult.server_task_json.....]'+self.G_TIPS_TXT_NODE)
        #CLASS_COMMON_UTIL.python_copy(os.path.normpath(self.G_ANALYZE_TXT_NODE),os.path.normpath(self.G_CONFIG_PATH))
        #CLASS_COMMON_UTIL.python_copy(os.path.normpath(self.G_PROPERTY_TXT_NODE),os.path.normpath(self.G_CONFIG_PATH))
        #CLASS_COMMON_UTIL.python_copy(node_task_json,self.G_CONFIG_PATH)
        #CLASS_COMMON_UTIL.python_copy(node_asset_json,self.G_CONFIG_PATH)
        #CLASS_COMMON_UTIL.python_copy(node_tips_json,self.G_CONFIG_PATH)
        #CLASS_COMMON_UTIL.python_copy(self.G_TIPS_TXT_NODE,self.G_CONFIG_PATH)  
        #self.copy_cfg_to_server(node_task_json,node_asset_json,node_tips_json)
        
    
        
    #=================================================task.json===================================================   
    def han_task_json(self,node_task_json):
        scene_info_dict={}
        scene_info_common_dict={}
        scene_info_renderer_dict={}
        miscellaneous_dict={}
        
        #-----------------------------------------------------scene_info_common---------------------------------------------------
        common_section='common'
        if  self.ANALYZE_TXT_PARSER.has_section(common_section):
            for option in self.ANALYZE_TXT_PARSER.options(common_section):  
                value = self.ANALYZE_TXT_PARSER.get(common_section,option)
                value = CLASS_COMMON_UTIL.bytes_to_str(value)
                # print(" ",option,"=",value)
                if option=='all_camera':
                    all_camera_str=value
                    scene_info_common_dict['all_camera']=self.str_to_list(all_camera_str,'[,]')
                elif option=='renderable_camera':
                    renderable_camera_list=[]
                    renderable_camera_str=value
                    renderable_camera_list.append(renderable_camera_str)
                    scene_info_common_dict['renderable_camera']=renderable_camera_list
                elif option=='element_list':
                    all_element_str=value
                    scene_info_common_dict['element_list']=self.str_to_list(all_element_str,'[,]')
                else:
                    if value=='true':
                        scene_info_common_dict[option]='1'
                    elif value=='false':
                        scene_info_common_dict[option]='0'
                    else:
                        scene_info_common_dict[option]=value
        # scene_info_common_dict['kg']='0'
        ## add for test
        # scene_info_common_dict['gamma']='gamma'
        # scene_info_common_dict['gamma_val']='2.2'
        # scene_info_common_dict['in_gamma']='2.2'
        # scene_info_common_dict['out_gamma']='2.2'
                    
        #-----------------------------------------------------scene_info_renderer---------------------------------------------------
        renderer_section='renderer'
        if  self.ANALYZE_TXT_PARSER.has_section(renderer_section):
            for option in self.ANALYZE_TXT_PARSER.options(renderer_section):  
                value = self.ANALYZE_TXT_PARSER.get(renderer_section,option) 
                value = CLASS_COMMON_UTIL.bytes_to_str(value)
                # print(" ",option,"=",value)
                scene_info_renderer_dict[option]=value
        
        scene_info_dict['common']=scene_info_common_dict
        scene_info_dict['renderer']=scene_info_renderer_dict
        
        #-----------------------------------------------------miscellaneous---------------------------------------------------
        #miscellaneous_dict['sub_from']='web'
        # miscellaneous_dict['only_photon']='0'
        # if self.G_TASK_JSON_DICT.has_key('miscellaneous') and self.G_TASK_JSON_DICT['miscellaneous'].has_key('only_photon'):
            # miscellaneous_dict['only_photon']=self.G_TASK_JSON_DICT['miscellaneous']['only_photon']
        maxcmd_plugin_json = os.path.join(self.G_MAX_B,'ini','config','maxcmd_plugin.json')
        with open(maxcmd_plugin_json,'r') as pl:
            pl_dict = json.load(pl)
            pl_list = pl_dict["maxcmd_plugin"]
            # if self.G_TASK_JSON_DICT.has_key('software_config'):
                # self.G_CG_CONFIG_DICT=self.G_TASK_JSON_DICT['software_config']
            if 'plugins' in self.G_CG_CONFIG_DICT:
                plugin_dict = self.G_CG_CONFIG_DICT['plugins']
                for plugins_key in list(plugin_dict.keys()):
                    plugin_str = plugins_key + plugin_dict[plugins_key]
                    if plugin_str in pl_list:
                        miscellaneous_dict['render_type']='maxcmd'
                        break
            else:
                print('There is no key--plugins in the plugins.cfg')
                    
        
        self.G_TASK_JSON_DICT['scene_info']=scene_info_dict
        self.G_TASK_JSON_DICT['miscellaneous']=miscellaneous_dict
        task_json_str = json.dumps(self.G_TASK_JSON_DICT,ensure_ascii=False)
        CLASS_COMMON_UTIL.write_file(task_json_str,node_task_json)
        return scene_info_dict
    
    #=================================================asset.json===================================================
    def han_asset_json(self,node_asset_json):
        self.loop_project_asset()
        asset_json_dict=self.get_all_asset()
        asset_json_dict['max']=[self.G_INPUT_CG_FILE]
        asset_json_str = json.dumps(asset_json_dict,ensure_ascii=False)
        
        CLASS_COMMON_UTIL.write_file(asset_json_str,node_asset_json)
        return asset_json_dict
    
    #=================================================tips.json===================================================    
    def han_tips_json(self,node_tips_json,scene_info_dict,asset_json_dict):
        self.G_DEBUG_LOG.info('------------------------------ hand ms  tips---------------------------------') 
        tips_json_dict={}
        #------------ms tips-----------
        if self.ANALYZE_TXT_PARSER.has_section('tips'):
            dataDict={}
            item_key_list = self.ANALYZE_TXT_PARSER.options('tips')
            for index,item_key in enumerate(item_key_list):
            #for item_key in item_key_list:
                value = self.ANALYZE_TXT_PARSER.get('tips', item_key)
                value = CLASS_COMMON_UTIL.bytes_to_str(value)
                item_val = value
                if item_val==None or item_val=='':
                    continue
                item_val = item_val.strip()
                tips_json_dict[item_key]=item_val

        self.G_DEBUG_LOG.info('------------------------------ hand tips gamma---------------------------------') 
        #------------gamma-----------
        # if self.ANALYZE_TXT_PARSER.has_option('common','file_gamma'):
            # gamma= self.ANALYZE_TXT_PARSER.get('common', 'file_gamma')
        if self.ANALYZE_TXT_PARSER.has_option('common','gamma'):
            gamma= self.ANALYZE_TXT_PARSER.get('common', 'gamma')
            if gamma!=None and gamma.strip()=='gamma':
                tips_json_dict[self.TIPS_CODE_DICT['gamma_on']]=[]
        
        #------------global proxy-----------
        if self.ANALYZE_TXT_PARSER.has_option('common','global_proxy'):
            globalproxy= self.ANALYZE_TXT_PARSER.get('common', 'global_proxy')
            if globalproxy!=None and globalproxy.strip()=='1':
                tips_json_dict[self.TIPS_CODE_DICT['proxy_enable']]=[]
                
        #------------check duplicate camera-----------  
        if self.ANALYZE_TXT_PARSER.has_option('common', 'all_camera'):   
            value = self.ANALYZE_TXT_PARSER.get('common', 'all_camera')
            value = CLASS_COMMON_UTIL.bytes_to_str(value) 
            camera_list = self.str_to_list(value,'[,]')
            if self.isDuplicateList(camera_list):
                tips_json_dict[self.TIPS_CODE_DICT['camera_duplicat']]=camera_list
            
        #------------check duplicate elements-----------   
        if self.ANALYZE_TXT_PARSER.has_option('common', 'element_list'):
            value = self.ANALYZE_TXT_PARSER.get('common', 'element_list')
            value = CLASS_COMMON_UTIL.bytes_to_str(value) 
            elem_list = self.str_to_list(value,'[,]') 
            if self.isDuplicateList(elem_list):
                tips_json_dict[self.TIPS_CODE_DICT['element_duplicat']]=elem_list
            
        #------------vrmesh with null type-----------
        if self.ANALYZE_TXT_PARSER.has_section('vrmesh'):
            bad_vrmesh_list=[]
            item_key_list = self.ANALYZE_TXT_PARSER.options('vrmesh')
            for index,item_key in enumerate(item_key_list):
                value = self.ANALYZE_TXT_PARSER.get('vrmesh', item_key)
                value = CLASS_COMMON_UTIL.bytes_to_str(value)
                item_val = value
                if item_val==None or item_val=='':
                    continue
                item_val = item_val.strip()
                if os.path.splitext(item_val)[1] ==None or  os.path.splitext(item_val)[1] =='' :
                    bad_vrmesh_list.append(item_val)
            if len(bad_vrmesh_list)>0:
                tips_json_dict[self.TIPS_CODE_DICT['vrmesh_ext_null']]=bad_vrmesh_list
                
        #------------Missing camera-----------   
        if self.ANALYZE_TXT_PARSER.has_option('common', 'all_camera'):
            if self.ANALYZE_TXT_PARSER.get('common', 'all_camera')==None or self.ANALYZE_TXT_PARSER.get('common', 'all_camera')=='':
                tips_json_dict[self.TIPS_CODE_DICT['camera_null']]=[]
        else:
            tips_json_dict[self.TIPS_CODE_DICT['camera_null']]=[]
            
        #------------Missing renderable camera-----------   
        if self.ANALYZE_TXT_PARSER.has_option('common', 'renderable_camera'):
            renderable_camera = self.ANALYZE_TXT_PARSER.get('common', 'renderable_camera')
            if renderable_camera==None or renderable_camera=='':
                if self.G_AUTO_COMMIT == '1':  #auto commit
                    tips_json_dict[self.TIPS_CODE_DICT['error_renderable_camera_null']]=[]
                else:  #2
                    tips_json_dict[self.TIPS_CODE_DICT['warn_renderable_camera_null']]=[]
            else:
                if self.ANALYZE_TXT_PARSER.has_option('common', 'all_camera'):
                    all_camera = self.ANALYZE_TXT_PARSER.get('common', 'all_camera')
                    if renderable_camera not in all_camera:
                        if self.G_AUTO_COMMIT == '1':  #auto commit
                            tips_json_dict[self.TIPS_CODE_DICT['error_renderable_camera_null']]=[]
                        else:
                            tips_json_dict[self.TIPS_CODE_DICT['warn_renderable_camera_null']]=[]
        else:
            if self.G_AUTO_COMMIT == '1':  #auto commit
                tips_json_dict[self.TIPS_CODE_DICT['error_renderable_camera_null']]=[]
            else:
                tips_json_dict[self.TIPS_CODE_DICT['warn_renderable_camera_null']]=[]
            
        #------------Missing filename/filetype-----------   
        if self.ANALYZE_TXT_PARSER.has_option('common', 'output_file_basename'):
            if self.ANALYZE_TXT_PARSER.get('common', 'output_file_basename')==None or self.ANALYZE_TXT_PARSER.get('common', 'output_file_basename')=='':
                if self.G_AUTO_COMMIT == '1':  #auto commit
                    tips_json_dict[self.TIPS_CODE_DICT['error_filename_filetype_null']]=[]
                else:
                    tips_json_dict[self.TIPS_CODE_DICT['warn_filename_filetype_null']]=[]
        else:
            if self.G_AUTO_COMMIT == '1':  #auto commit
                tips_json_dict[self.TIPS_CODE_DICT['error_filename_filetype_null']]=[]
            else:
                tips_json_dict[self.TIPS_CODE_DICT['warn_filename_filetype_null']]=[]
            
        if self.ANALYZE_TXT_PARSER.has_option('common', 'output_file_type'):
            if self.ANALYZE_TXT_PARSER.get('common', 'output_file_type')==None or self.ANALYZE_TXT_PARSER.get('common', 'output_file_type')=='':
                if self.G_AUTO_COMMIT == '1':  #auto commit
                    tips_json_dict[self.TIPS_CODE_DICT['error_filename_filetype_null']]=[]
                else:
                    tips_json_dict[self.TIPS_CODE_DICT['warn_filename_filetype_null']]=[]
        else:
            if self.G_AUTO_COMMIT == '1':  #auto commit
                tips_json_dict[self.TIPS_CODE_DICT['error_filename_filetype_null']]=[]
            else:
                tips_json_dict[self.TIPS_CODE_DICT['warn_filename_filetype_null']]=[]
        
        #------------xref files-----------   
        if self.ANALYZE_TXT_PARSER.has_option('common', 'xrefs'):
            if self.ANALYZE_TXT_PARSER.get('common', 'xrefs')==None or self.ANALYZE_TXT_PARSER.get('common', 'xrefs')=='':
                tips_json_dict[self.TIPS_CODE_DICT['camera_null']]=[]
               
        self.G_DEBUG_LOG.info('------------------------------ han tips vfb---------------------------------') 
        #-----------VFB : \"Render to V-Ray raw image file\" Checked but *.vrimg is undefined " ------------ 
        if self.ANALYZE_TXT_PARSER.has_option('renderer', 'vfb') and self.ANALYZE_TXT_PARSER.get('renderer', 'vfb') =='true':
            if self.ANALYZE_TXT_PARSER.has_option('renderer', 'rend_raw_img_name') and self.ANALYZE_TXT_PARSER.get('renderer', 'rend_raw_img_name') =='true':
                if self.ANALYZE_TXT_PARSER.has_option('renderer', 'raw_img_name') and self.ANALYZE_TXT_PARSER.get('renderer', 'raw_img_name') =='':
                    tips_json_dict[self.TIPS_CODE_DICT['vrimg_undefined']]=[]
        
        #-----------\"Save separate render channels Checked but channels file is error"------------ 
        if self.ANALYZE_TXT_PARSER.has_option('renderer', 'save_sep_channel') and self.ANALYZE_TXT_PARSER.get('renderer', 'save_sep_channel') =='true':
            if self.ANALYZE_TXT_PARSER.has_option('renderer', 'channel_file') and self.ANALYZE_TXT_PARSER.get('renderer', 'channel_file') =='':
                tips_json_dict[self.TIPS_CODE_DICT['channel_file_undefined']]=[]
                
        self.G_DEBUG_LOG.info('------------------------------ han tips gi---------------------------------') 
        #--------------------check gi------------------- 
        if self.ANALYZE_TXT_PARSER.has_option('renderer', 'gi') and self.ANALYZE_TXT_PARSER.get('renderer', 'gi')=='1' :
            if self.ANALYZE_TXT_PARSER.has_option('renderer', 'primary_gi_engine') and self.ANALYZE_TXT_PARSER.get('renderer', 'primary_gi_engine') =='0':
                #-----------Irradiance map mode :  \"Multiframe incremental\" not supported------------
                if self.ANALYZE_TXT_PARSER.has_option('renderer', 'irradiance_map_mode') and self.ANALYZE_TXT_PARSER.get('renderer', 'irradiance_map_mode') =='1':
                    tips_json_dict[self.TIPS_CODE_DICT['multiframe_notsupport']]=[]
                    
                #-----------Irradiance map mode : Add to current map not supported------------
                if self.ANALYZE_TXT_PARSER.has_option('renderer', 'irradiance_map_mode') and self.ANALYZE_TXT_PARSER.get('renderer', 'irradiance_map_mode') =='3':
                    tips_json_dict[self.TIPS_CODE_DICT['addtocmap_notsupport']]=[]
            
            #-----------Light cache mode : \"Progressive path tracing\" not supported------------        
            elif self.ANALYZE_TXT_PARSER.has_option('renderer', 'primary_gi_engine') and self.ANALYZE_TXT_PARSER.get('renderer', 'primary_gi_engine') =='3':
                 if self.ANALYZE_TXT_PARSER.has_option('renderer', 'light_cache_mode') and self.ANALYZE_TXT_PARSER.get('renderer', 'light_cache_mode') =='3':
                    tips_json_dict[self.TIPS_CODE_DICT['ppt_notsupport']]=[]
                    
            #-----------Light cache mode : \"Progressive path tracing\" not supported------------ 
            if self.ANALYZE_TXT_PARSER.has_option('renderer', 'secondary_gi_engine') and self.ANALYZE_TXT_PARSER.get('renderer', 'secondary_gi_engine') =='3':
                if self.ANALYZE_TXT_PARSER.has_option('renderer', 'light_cache_mode') and self.ANALYZE_TXT_PARSER.get('renderer', 'light_cache_mode') =='3':
                    tips_json_dict[self.TIPS_CODE_DICT['ppt_notsupport']]=[]
                    
            #-----------Irradiance map mode : \"From file\" VRMAP_MISSING------------ 
            if self.ANALYZE_TXT_PARSER.has_option('renderer', 'primary_gi_engine') and self.ANALYZE_TXT_PARSER.get('renderer', 'primary_gi_engine') =='0':
                if self.ANALYZE_TXT_PARSER.has_option('renderer', 'irradiance_map_mode') and self.ANALYZE_TXT_PARSER.get('renderer', 'irradiance_map_mode') =='2':
                    if self.ANALYZE_TXT_PARSER.has_option('renderer', 'irrmap_file') and self.ANALYZE_TXT_PARSER.get('renderer', 'irrmap_file') =='':
                        tips_json_dict[self.TIPS_CODE_DICT['vrmap_missing']]=[]
            
            #-----------Irradiance map mode : \"Animation rendering\" ANIMATION_MAP_MISSING------------ 
            if self.ANALYZE_TXT_PARSER.has_option('renderer', 'primary_gi_engine') and self.ANALYZE_TXT_PARSER.get('renderer', 'primary_gi_engine') =='0':
                if self.ANALYZE_TXT_PARSER.has_option('renderer', 'irradiance_map_mode') and self.ANALYZE_TXT_PARSER.get('renderer', 'irradiance_map_mode') =='7':
                    if self.ANALYZE_TXT_PARSER.has_option('renderer', 'irrmap_file') and self.ANALYZE_TXT_PARSER.get('renderer', 'irrmap_file') =='':
                        # if self.ANALYZE_TXT_PARSER.has_option('renderer', 'irrmap_file') and self.ANALYZE_TXT_PARSER.get('renderer', 'irrmap_file') =='':
                        tips_json_dict[self.TIPS_CODE_DICT['animation_map_missing']]=[]
            
            #-----------light cache mode : \"From file\" VRLMAP_MISSING------------ 
            if self.ANALYZE_TXT_PARSER.has_option('renderer', 'secondary_gi_engine') and self.ANALYZE_TXT_PARSER.get('renderer', 'secondary_gi_engine') =='3':
                if self.ANALYZE_TXT_PARSER.has_option('renderer', 'light_cache_mode') and self.ANALYZE_TXT_PARSER.get('renderer', 'light_cache_mode') =='2':
                    if self.ANALYZE_TXT_PARSER.has_option('renderer', 'light_cache_file') and self.ANALYZE_TXT_PARSER.get('renderer', 'light_cache_file') =='':
                        tips_json_dict[self.TIPS_CODE_DICT['vrlmap_missing']]=[]
       
       
        
        
        #------------------------------------check duplicate texture--------------------------------------
        dup_texture_dict=self.checkDuplicateFile(asset_json_dict['texture'])
        if len(dup_texture_dict)>0 :
            dup_texture_list=list(dup_texture_dict.values())
            dup_str=''
            total_dup_list=[]
            for dup_list in dup_texture_list:
                total_dup_list.extend(dup_list)
            tips_json_dict[self.TIPS_CODE_DICT['duplicate_texture']]=total_dup_list
        
        #--------------------------------------------------------missing--------------------------------------------
        self.G_DEBUG_LOG.info('------------------------------ check missing---------------------------------') 
        
        for key,value in list(self.TIPS_CODE_DICT.items()):
            self.get_missing_code_info(value,key,asset_json_dict,tips_json_dict)
        
        '''
        self.get_missing_code_info(self.TIPS_CODE.PC_MISSING,'pointcache_missing',tips_json_dict)
        self.get_missing_code_info(self.TIPS_CODE.MISSING_FILE,'texture_missing',tips_json_dict)
        self.get_missing_code_info(self.TIPS_CODE.XREFFILES,'xrefs',tips_json_dict)
        self.get_missing_code_info(self.TIPS_CODE.XREFOBJ,'xrefsobj',tips_json_dict)
        self.get_missing_code_info(self.TIPS_CODE.VDB_MISSING,'vdb_missing',tips_json_dict)
        self.get_missing_code_info(self.TIPS_CODE.HDRI_MISSING,'hdri_missing',tips_json_dict)
        self.get_missing_code_info(self.TIPS_CODE.FUMEFX_MISSING,'fumefx_missing',tips_json_dict)
        self.get_missing_code_info(self.TIPS_CODE.PHOENIFX_MISSING,'phoenix_missing',tips_json_dict)
        self.get_missing_code_info(self.TIPS_CODE.VRMESH_MISSING,'vrmesh_missing',tips_json_dict)
        self.get_missing_code_info(self.TIPS_CODE.FIRESMOKESIM_MISSING,'firesmokesim_missing',tips_json_dict)
        self.get_missing_code_info(self.TIPS_CODE.LIQUIDSIM_MISSING,'liquidsim_missing',tips_json_dict)
        self.get_missing_code_info(self.TIPS_CODE.KK_MISSING,'kk_missing',tips_json_dict)
        self.get_missing_code_info(self.TIPS_CODE.ABC_MISSING,'alembic_missing',tips_json_dict)
        self.get_missing_code_info(self.TIPS_CODE.XMESH_MISSING,'xmesh_missing',tips_json_dict)
        self.get_missing_code_info(self.TIPS_CODE.REALFLOW_MISSING,'realflow_missing',tips_json_dict)
        
        self.get_missing_code_info(self.TIPS_CODE.BAD_MATERIAL,'badmaterial',asset_json_dict,tips_json_dict)
        self.get_missing_code_info(self.TIPS_CODE.XREFFILES,'xrefs',asset_json_dict,tips_json_dict)
        self.get_missing_code_info(self.TIPS_CODE.XREFOBJ,'xrefsobj',asset_json_dict,tips_json_dict)
        '''
        
        
        #------------write tips----------- 
        tips_json_str = json.dumps(tips_json_dict,ensure_ascii=False)
        CLASS_COMMON_UTIL.write_file(tips_json_str,node_tips_json)
        

        


            
    def str_to_list(self,list_str,split_symbol):
        list=[]
        if list_str==None or list_str=='' or list_str=='[,]':
            return list
        
        if list_str.endswith(split_symbol):
            list_str=list_str[:-len(split_symbol)]
        list=list_str.split(split_symbol)
        
        return list
    
    def RBBackupPy(self):
        print('[MAX.RBBackupPy.start.....]')

        print('[MAX.RBBackupPy.end.....]')
        
    def getSerial(self,number,number_count):
        number_str=str(number)
        while len(number_str)<number_count:
            number_str='0'+number_str
        return number_str
            
    def countCharInStr(self,str,char):
        start = str.find(char)
        end = str.rfind(char)
        if start==-1 and end==-1:
            return 0
        else:
            clen=end-start+1
            return clen
        
    def convertFileCode(self,source,target,source_code='utf-8',target_code='UTF-16'):
        if os.path.exists(target):
            os.remove(target)
        
        resource_file_obj=codecs.open(source,'r')
        resource_file_result=resource_file_obj.read()
        resource_file_result=resource_file_result.decode(source_code)
        resource_file_obj.close()
        
        
        render_cfg_file_obj=codecs.open(target,'a',target_code)
        render_cfg_file_obj.write(resource_file_result)
        render_cfg_file_obj.close()
        
        
    def testMode(self):
        test_file=r'D:/test.txt'
        if os.path.exists(test_file):
            return
    def RBreadCfg(self):#4
        self.G_DEBUG_LOG.info('[Max.RBreadCfg.start.....]')
        self.G_DEBUG_LOG.info('[Max.RBreadCfg.end.....]')
        
    def RBcopyTempFile(self):
        self.G_DEBUG_LOG.info('[MAX.RBcopyTempFile.start.....]')
        temp_file=os.path.join(self.G_POOL,'temp',(self.G_TASK_ID+'_analyse'))
        self.G_DEBUG_LOG.info(temp_file)
        self.G_DEBUG_LOG.info(self.G_WORK_RENDER_TASK)
        #self.pythonCopy(temp_file.replace('/','\\'),self.G_WORK_RENDER_TASK.replace('/','\\'))
        
        self.G_DEBUG_LOG.info('[MAX.RBcopyTempFile.end.....]')	
    

        
    def getMaxVersionByNumber(self,max_number):
        max_version=None
        if operator.ge(max_number,float(20))==True:
            max_version='3ds Max 2018'
        elif operator.ge(max_number,float(19))==True:
            max_version='3ds Max 2017'
        elif operator.ge(max_number,float(18))==True:
            max_version='3ds Max 2016'
        elif operator.ge(max_number,float(17))==True:
            max_version='3ds Max 2015'
        elif operator.ge(max_number,float(16))==True:
            max_version='3ds Max 2014'
        elif operator.ge(max_number,float(15))==True:
            max_version='3ds Max 2013'
        elif operator.ge(max_number,float(14))==True:
            max_version='3ds Max 2012'
        elif operator.ge(max_number,float(13))==True:
            max_version='3ds Max 2011'
        elif operator.ge(max_number,float(12))==True:
            max_version='3ds Max 2010'
        # if cmp(max_number,float(20))==1 or cmp(max_number,float(20))==0:
            # max_version='3ds Max 2018'
        # elif cmp(max_number,float(19))==1 or cmp(max_number,float(19))==0:
            # max_version='3ds Max 2017'
        # elif cmp(max_number,float(18))==1 or cmp(max_number,float(18))==0:
            # max_version='3ds Max 2016'
        # elif cmp(max_number,float(17))==1 or cmp(max_number,float(17))==0:
            # max_version='3ds Max 2015'
        # elif cmp(max_number,float(16))==1 or cmp(max_number,float(16))==0:
            # max_version='3ds Max 2014'
        # elif cmp(max_number,float(15))==1 or cmp(max_number,float(15))==0:
            # max_version='3ds Max 2013'
        # elif cmp(max_number,float(14))==1 or cmp(max_number,float(14))==0:
            # max_version='3ds Max 2012'
        # elif cmp(max_number,float(13))==1 or cmp(max_number,float(13))==0:
            # max_version='3ds Max 2011'
        # elif cmp(max_number,float(12))==1 or cmp(max_number,float(12))==0:
            # max_version='3ds Max 2010'
        return max_version

    def readFile(self,file):
        code_list=['utf-8','utf-16','gbk',sys.getfilesystemencoding(),'']
        file_list=[]
        for code in code_list:
            try:
                with codecs.open(file, 'r', code) as file_obj:
                    file_list=file_obj.readlines()
                break
            except:
                pass
        return file_list

    def maxfind(self):
        #return#
        print('----------maxfind----------')
        helper_max_file = self.G_WORK_RENDER_TASK + '\\max\\' + os.path.basename(self.G_INPUT_CG_FILE)
        if  os.path.exists(self.G_PROPERTY_TXT_NODE):
            os.remove(self.G_PROPERTY_TXT_NODE)
        max_find_cmd_str=self.G_MAXFIND+r' "' +helper_max_file.replace('\\','/')+'">>'+self.G_PROPERTY_TXT_NODE
        
        # CLASS_COMMON_UTIL.cmd(max_find_cmd_str.encode(sys.getfilesystemencoding()),my_log=self.G_DEBUG_LOG,my_shell=True)
        CLASS_COMMON_UTIL.cmd(max_find_cmd_str,my_log=self.G_DEBUG_LOG,my_shell=True)
        print('----------------------property-----------------')
        property_list=[]
        if not os.path.exists(self.G_PROPERTY_TXT_NODE):
            CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG,'maxfind read max file failed')
            
        try:
            self.G_DEBUG_LOG.info('--------------utf-8----------')
            property_obj=codecs.open(self.G_PROPERTY_TXT_NODE, "r", "UTF-8")
            property_list=property_obj.readlines()
        except:
            try:
                self.G_DEBUG_LOG.info('--------------sys----------')
                self.G_DEBUG_LOG.info(sys.getfilesystemencoding())
                property_obj=codecs.open(self.G_PROPERTY_TXT_NODE, "r", sys.getfilesystemencoding())
                property_list=property_obj.readlines()
            except:
                try:
                    self.G_DEBUG_LOG.info('--------------default----------')
                    property_obj=codecs.open(self.G_PROPERTY_TXT_NODE, "r")
                    property_list=property_obj.readlines()
                except:
                    pass
        try:
            property_obj.close()
        except:
            pass
            
        for max_info_line in property_list:
            self.G_DEBUG_LOG.info(max_info_line)
            if max_info_line.startswith('\t3ds Max Version:') or max_info_line.startswith('\t3ds max Version:') or max_info_line.startswith('\t3ds Max 版本:') or max_info_line.startswith('\t3ds Max バージョン :'):
                max_version=max_info_line.replace('\t3ds Max Version:','').replace('\t3ds max Version:','').replace('\t3ds Max 版本:','').replace('\t3ds Max バージョン :','')
                max_version=max_version.replace(',','.').replace('\r','').replace('\n','')
                # max_version_float=string.atof(max_version)
                max_version_float=float(max_version)
                max_version_str = self.getMaxVersionByNumber(max_version_float)
                self.G_MAXFIND_MAX_VERSION_INT=int(max_version_float)
                self.G_MAXFIND_MAX_VERSION_STR=max_version_str
                print('3ds max  version...',self.G_MAXFIND_MAX_VERSION_INT,'___',self.G_MAXFIND_MAX_VERSION_STR)
                
            elif max_info_line.startswith('\tSaved As Version:') or max_info_line.startswith('\t另存为版本:')  or max_info_line.startswith('\tバージョンとして保存:'):
                max_version=max_info_line.replace('\tSaved As Version:','').replace('\t另存为版本:','').replace('\tバージョンとして保存:','')
                max_version=max_version.replace(',','.').replace('\r','').replace('\n','')
                # max_version_float=string.atof(max_version)
                max_version_float=float(max_version)
                max_version_str = self.getMaxVersionByNumber(max_version_float)
                self.G_MAXFIND_MAX_VERSION_INT=int(max_version_float)
                self.G_MAXFIND_MAX_VERSION_STR=max_version_str
                print('3ds max save as version...',self.G_MAXFIND_MAX_VERSION_INT,'___',self.G_MAXFIND_MAX_VERSION_STR)
                
            elif max_info_line.startswith('\tRenderer Name='):
                renderer=max_info_line.replace('\tRenderer Name=','')
                renderer = renderer.lower().replace('v-ray ', 'vray').replace('v_ray ', 'vray').replace('adv ', '').replace('demo ', '').replace(' ', '')
                renderer = renderer.replace('edu ', '').replace('edu_', '').replace('\r','').replace('\n','')
                self.G_MAXFIND_RENDERER=renderer
                print('3ds max  renderer...',self.G_MAXFIND_RENDERER)
                
            elif max_info_line.startswith('\tRender Output Gamma='):#default is 0.00
                output_gamma=max_info_line.replace('\tRender Output Gamma=','').replace('\r','').replace('\n','')
                self.G_MAXFIND_OUTPUT_GAMMA=output_gamma
                print('3ds max  output gamma...',self.G_MAXFIND_OUTPUT_GAMMA)
        
        
        if self.G_MAXFIND_RENDERER==None or self.G_MAXFIND_MAX_VERSION_STR==None:
            tips_str='{"'+self.TIPS_CODE_DICT['maxinfo_failed']+'":[]}'
            # self.RB_KAFKA_NOTIFY()
            CLASS_COMMON_UTIL.exit_tips(tips_str,self.G_TIPS_TXT_NODE,self.G_CONFIG_PATH,self.G_DEBUG_LOG)
            
            
        if 'rt' in self.G_MAXFIND_RENDERER:
            tips_str='{"'+self.TIPS_CODE_DICT['renderer_notsupport']+'":[]}'
            # self.RB_KAFKA_NOTIFY()
            CLASS_COMMON_UTIL.exit_tips(tips_str,self.G_TIPS_TXT_NODE,self.G_CONFIG_PATH,self.G_DEBUG_LOG)
            
    def multiscatterAndVray(self):
    
        multiscatter_str=''
        if 'plugins' in self.G_CG_CONFIG_DICT:
            plugin_dict=self.G_CG_CONFIG_DICT['plugins']
            if 'multiscatter' in plugin_dict:
                multiscatter_str=plugin_dict['multiscatter']
                
        if self.CONFLICT_PLUGIN.max_plugin_conflict(self.G_CG_VERSION.replace('3ds Max ',''),self.G_MAXFIND_RENDERER.replace('vray',''),multiscatter_str):
            tips_str='{"'+self.TIPS_CODE_DICT['conflict_multiscatter_vray']+'":["'+self.G_CG_VERSION+'","'+self.G_MAXFIND_RENDERER+'","'+multiscatter_str+'"]}'
            # self.RB_KAFKA_NOTIFY()
            CLASS_COMMON_UTIL.exit_tips(tips_str,self.G_TIPS_TXT_NODE,self.G_CONFIG_PATH,self.G_DEBUG_LOG)
            # CLASS_COMMON_UTIL.write_file(tips_str,self.G_TIPS_TXT_NODE)
            # self.copyTipTxt()
            # exit(0)
        
    def config_max_plugin(self):#config 3ds Max ,vray,plugin...and so on
        
        self.G_DEBUG_LOG.info('[max.configMax.start.....]')
        
        # print(str(self.G_CG_CONFIG_DICT))
        # print(str(type(self.G_CG_CONFIG_DICT)))
        
        
        
        #-------------------------------max version of scene and max version of project config-------------------------------
        if self.G_CG_VERSION!=self.G_MAXFIND_MAX_VERSION_STR:
            tips_str='{"'+self.TIPS_CODE_DICT['max_version_not_match']+'":[]}'
            # self.RB_KAFKA_NOTIFY()
            CLASS_COMMON_UTIL.exit_tips(tips_str,self.G_TIPS_TXT_NODE,self.G_CONFIG_PATH,self.G_DEBUG_LOG)
            
        if self.G_MAXFIND_RENDERER.startswith('vray'):
            myRenderVersion=self.G_MAXFIND_RENDERER.replace('vray','').replace('edu','')
            if 'plugins' in self.G_CG_CONFIG_DICT:
                plugin_dict=self.G_CG_CONFIG_DICT['plugins']
                plugin_dict['vray']=myRenderVersion
            else:
                plugin_dict={}
                plugin_dict['vray']=myRenderVersion
                self.G_CG_CONFIG_DICT['plugins']=plugin_dict

        if 'cg_name' not in self.G_CG_CONFIG_DICT:
            self.G_CG_CONFIG_DICT['cg_name']='3ds Max'
            
        if 'cg_version' not in self.G_CG_CONFIG_DICT:
            self.G_CG_CONFIG_DICT['cg_version']=self.G_MAXFIND_MAX_VERSION_STR.replace('3ds Max ','')
            
        # print(self.G_CG_CONFIG_DICT)
        
           
        
        #-------------------------------conflict multiscatter and vray-------------------------------
        self.multiscatterAndVray() 
        
        
        self.G_DEBUG_LOG.info('---------------plugin--------')
        self.G_DEBUG_LOG.info(str(self.G_CG_CONFIG_DICT))
        
        max_plugin=MaxPlugin(self.G_CG_CONFIG_DICT,self.G_DEBUG_LOG)
        max_plugin.config()
        
        

        
    def write_ms_file(self):

        ms_file=os.path.join(self.G_WORK_RENDER_TASK_CFG,('helper.ms'))
        ms_file=ms_file.replace('\\','/')
        if os.path.exists(ms_file):
            os.remove(ms_file)
            
        ms_file_object=codecs.open(ms_file,'w',"utf-8")
        
        analyse_txt=self.G_ANALYZE_TXT_NODE.replace('\\','/')
        script_ms_name=self.G_MAXSCRIPT_NAME_U
        if self.G_CG_VERSION=='3ds Max 2012' or self.G_CG_VERSION=='3ds Max 2011' or self.G_CG_VERSION=='3ds Max 2010' or self.G_CG_VERSION=='3ds Max 2009':
            #ms_file_object=codecs.open(ms_file,'w',"gbk")
            ms_file_object=codecs.open(ms_file,'w',sys.getfilesystemencoding())
            script_ms_name=self.G_MAXSCRIPT_NAME_A
            
        user_ms_script=self.G_NODE_MAXSCRIPT+'/user/'+self.G_USER_ID+'/'+script_ms_name
        ms_script=self.G_NODE_MAXSCRIPT+'/'+script_ms_name
        if os.path.exists(user_ms_script):
            ms_script=user_ms_script
            
        ms_file_object.write('(DotNetClass "System.Windows.Forms.Application").CurrentCulture = dotnetObject "System.Globalization.CultureInfo" "zh-cn"\r\n')
        ms_file_object.write('filein @"'+ms_script+'"\r\n')
        
        #analyseRun "962712" "5140547" "C:/work/helper/5140547/max/要命要命不是人.max" "C:/work/helper/5140547/cfg/analyse_net.txt" 
        helper_max_file = self.G_WORK_RENDER_TASK + '\\max\\' + os.path.basename(self.G_INPUT_CG_FILE) 
        my_str='analyseRun "'+self.G_USER_ID+'" "'+self.G_TASK_ID+'" "'+helper_max_file.replace('\\','/')+'" "'+analyse_txt+'" "'+str(os.getpid())+'"\r\n'
        ms_file_object.write(my_str)
        
        ms_file_object.close()
        self.G_DEBUG_LOG.info('[Max.writeMsFile.end.....]')
        return ms_file
        
        

        

                    

        
    def listToStr(self,list):
        str='['
        for item in list:
            str=str+'"'+item+'",'
        str=str.strip(',')
        str=str+']'
        return str
        

        

    def get_missing_code_info(self,info_code,info_type,asset_json_dict,tips_json_dict):
        self.G_DEBUG_LOG.info('------------------------------ get_missing_code_info---------------------------------') 
        self.G_DEBUG_LOG.info(info_code)
        self.G_DEBUG_LOG.info(info_type)
        tip_info_list=[]
        #if self.G_TASK_JSON_DICT.has_key('software_config'):
        if info_type in asset_json_dict:
            item_key_list =asset_json_dict[info_type]
                 
            if len(item_key_list)>0:
                for item_val in item_key_list:
                    if item_val==None or item_val=='':
                        continue
                    item_val = item_val.strip()
                    if self.ASSET_WEB_COOLECT_BY_PATH:
                        item_val=self.renderbus_path_obj.convert_to_user_path(item_val)
                    tip_info_list.append(item_val)
        if tip_info_list:
            tips_json_dict[info_code]=tip_info_list
                
    def parse_analyze_txt(self):
        
        self.ANALYZE_TXT_PARSER = configparser.ConfigParser()
        try:
            self.ANALYZE_TXT_PARSER.readfp(codecs.open(self.G_ANALYZE_TXT_NODE, "r", "UTF-16"))
        except Exception as e:
            try:
                self.ANALYZE_TXT_PARSER.readfp(codecs.open(self.G_ANALYZE_TXT_NODE, "r", "UTF-8"))
            except Exception as e:
                self.ANALYZE_TXT_PARSER.readfp(codecs.open(self.G_ANALYZE_TXT_NODE, "r"))
        self.FRAMES=self.ANALYZE_TXT_PARSER.get('common', 'frames')
        self.ANIMATION_RANGE=self.ANALYZE_TXT_PARSER.get('common', 'animation_range') 
        return self.ANALYZE_TXT_PARSER
        
    def getItemFromSection(self, section):
        print('getItemFromSection.section='+section)
        item_list = []
        if self.ANALYZE_TXT_PARSER.has_section(section):
            item_key_list = self.ANALYZE_TXT_PARSER.options(section)
            # print(item_key_list)
            for item_key in item_key_list:
                # print item_key
                value = self.ANALYZE_TXT_PARSER.get(section, item_key).strip()
                value = CLASS_COMMON_UTIL.bytes_to_str(value)
                item_path = value
                # print item_path
                #if ignore:
                #    rbFile = item_path 
                #else:
                #    rbFile = self.renderbus_path_obj.convert_path(item_path)

                #print rbFile
                #item_list.append(rbFile)
                item_list.append(item_path)
            
        return item_list
    
    #true=duplicate,false=not duplicate
    def isDuplicateList(self, list):
        list_set = set(list)
        if len(list)==len(list_set):
            return False
        else:
            return True
            
    def get_file_from_project_by_name(self,file):
        file_from_input=None
        #assetInputList= self.G_INPUT_PROJECT_ASSET_DICT.keys()
        file_base_name=os.path.basename(file)
        #if file_base_name in self.ASSET_INPUT_KEY_LIST:
        if file_base_name in self.G_INPUT_PROJECT_ASSET_DICT:
            file_from_input=self.G_INPUT_PROJECT_ASSET_DICT[file_base_name]
        return file_from_input
        
    def get_point_cache_list(self,asset_file,result_list):
        wild_path=asset_file
        if self.ASSET_WEB_COOLECT_BY_PATH:
            wild_path2 = self.renderbus_path_obj.convert_path(asset_file)
            result_list.append(wild_path2)
        else:
            result_list.append(wild_path)
            wild_path2=self.get_file_from_project_by_name(asset_file)
            
        if wild_path.endswith('.xml') and wild_path2!=None and os.path.exists(wild_path2):
            
            root = ET.parse(wild_path2).getroot()
            
            cache_type           = root.find('cacheType').get('Type')    # OneFile | OneFilePerFrame
            format              = root.find('cacheType').get('Format')  # mcc | mcx
            time                = root.find('time').get('Range')
            cache_time_per_frame   = root.find('cacheTimePerFrame').get('TimePerFrame')
            
            if format!=None and format == 'mcx':
                suffix      = '.mcx' 
            else:
                suffix      = '.mc' 
            # cache_start = int(time.split('-')[0]) / int(cache_time_per_frame)
            # cache_end  = int(time.split('-')[1]) / int(cache_time_per_frame)
            # cache_start = int(time.split('-')[1]) / int(cache_time_per_frame)
            # cache_end  = int(time.split('-')[2]) / int(cache_time_per_frame)
            patt = '(-?\d+)-(-?\d+)'
            m = re.match(patt,time)
            if m != None:
                cache_start = int(m.group(1)) / int(cache_time_per_frame)
                cache_end  = int(m.group(2)) / int(cache_time_per_frame)
            else:
                print('[err]re match [%s] err' % (time))
            
            if cache_type == 'OneFilePerFrame':                        
                for i in range(cache_start, cache_end + 1):
                    cache_file = os.path.splitext(wild_path2)[0] + 'Frame' + str(i) + suffix
                    if self.ASSET_WEB_COOLECT_BY_PATH:
                        cache_file2 = self.renderbus_path_obj.convert_path(cache_file)
                    else:
                        cache_base_name=os.path.basename(cache_file)
                        cache_file2=os.path.join(os.path.dirname(wild_path),cache_base_name)
                    result_list.append(cache_file2) 
                    
            elif cache_type == 'OneFile':
                cache_file = wild_path2.replace('.xml', suffix)
                if self.ASSET_WEB_COOLECT_BY_PATH:
                    cache_file2 = self.renderbus_path_obj.convert_path(cache_file)
                else:
                    cache_file2=wild_path.replace('.xml', suffix)
                result_list.append(cache_file2)
        

                        
    
        
    def getIflList(self,if_l_file,result_list):
        
        really_if_l_file=if_l_file
        if self.ASSET_WEB_COOLECT_BY_PATH:
            really_if_l_file=self.renderbus_path_obj.convert_path(if_l_file)
            result_list.append(really_if_l_file)
        else:
            result_list.append(if_l_file)
            really_if_l_file=self.get_file_from_project_by_name(if_l_file)
        
        
        if really_if_l_file!=None and os.path.exists(really_if_l_file): 
            #print '[exists]'
            really_if_l_file_dir=os.path.dirname(really_if_l_file)
            if_l_file_list=self.readFile(really_if_l_file)
            asset_list = []
            for line in if_l_file_list:
                
                # remove bom tag 
                if line==None or line.strip('')=='':
                    continue
                if bytes(line)[:3] == codecs.BOM_UTF8:
                    line = bytes(line)[3:]
                #print line.decode('utf-8').strip()
                line=line.strip()
                pos =line.rfind(' ')
                img = line
                if pos!=-1:
                    number=line[pos:].strip()
                    #print 'number...',number
                    if number.isalnum():#mm.jpg 5
                        img = line[:pos]
                #print img.decode('utf-8').strip()
                img_dir=os.path.dirname(img)
                if img_dir==None or img_dir.strip()=='':
                    img = os.path.join(really_if_l_file_dir,img)
                else:
                    img = self.renderbus_path_obj.convert_path(img.decode('utf-8').strip())
                
                
                result_list.append(img)
                

    #-----------------get input asset and missing asset--------------------
    def gather_asset(self, asset_type, asset_list,asset_dict):
        
            
        self.G_DEBUG_LOG.info('\r\n\r\n[-----------------max.RBanalyse.gather_asset_by_file_path]')
        self.G_DEBUG_LOG.info(asset_type)
        
        asset_input_server_str='asset_input_server'
        asset_input_str='asset_input'
        asset_input_missing_str='asset_input_missing'
        asset_item_missing_str=asset_type+'_missing'
        asset_input_list=[]
        asset_input_missing_list=[]
        asset_input_server_list=[]
        
        for asset in asset_list:
            asset_input_list.append(asset)
            if self.ASSET_WEB_COOLECT_BY_PATH:
                if not os.path.exists(asset):
                    asset_input_missing_list.append(asset)
            else:
                asset_item_server=self.get_file_from_project_by_name(asset)
                if asset_item_server:
                    asset_input_server_list.append(asset_item_server)
                else:
                    asset_input_missing_list.append(asset)
                '''
                asset_name=os.path.basename(asset)
                #if  asset_name   in self.ASSET_INPUT_KEY_LIST:
                if self.G_INPUT_PROJECT_ASSET_DICT.has_key(asset_name):    
                    self.get_file_from_project_by_name()
                    asset_input_server_list.append(self.G_INPUT_PROJECT_ASSET_DICT[asset_name])
                else:
                    asset_input_missing_list.append(asset)
                '''
        if asset_input_server_list:
            if asset_input_server_str in asset_dict:
                # asset_dict[asset_input_server_str].extend(asset_input_server_list)  # notice yinyong
                asset_dict[asset_input_server_str] = asset_dict[asset_input_server_str] + asset_input_server_list
            else:
                asset_dict[asset_input_server_str]=asset_input_server_list
                
        if asset_input_list:
            if asset_input_str in asset_dict:
                # asset_dict[asset_input_str].extend(asset_input_list)  # notice yinyong
                asset_dict[asset_input_str] = asset_dict[asset_input_str] + asset_input_list
            else:
                asset_dict[asset_input_str]=asset_input_list
        if asset_input_missing_list:
            if asset_input_missing_str in asset_dict:
                # asset_dict[asset_input_missing_str].extend(asset_input_missing_list)  # notice yinyong
                asset_dict[asset_input_missing_str] = asset_dict[asset_input_missing_str] + asset_input_missing_list
            else:
                asset_dict[asset_input_missing_str]=asset_input_missing_list
            
            asset_dict[asset_item_missing_str]=asset_input_missing_list
        
    #-----------------get all asset list(found and missing)--------------------
    def handleAsset(self, dict):
        asset_dict = dict
        def handler(key):
            result_dict = {}
            result_list = []
            asset_list = asset_dict[key]
            
            # handle fumefx & realflow & pc2 & pointcache & vrmesh
            if key == 'fumefx':
                for asset in asset_list:
                    splited_array = asset.split('|')
                    start_frame  = splited_array[0]
                    end_frame    = splited_array[1]
                    type        = splited_array[2] # default | wavlet | post
                    wild_path    = splited_array[3]
                    pos         = wild_path.rfind('.fxd')

                    # build sequence number
                    start = int(start_frame);
                    end   = int(end_frame);
                    file = ''
                    for i in range(start , end+1, -1 if start > end else 1):
                        
                        if i >= 0:
                            file = wild_path[:pos] + '%04d' % i + '.fxd'
                        else:
                            file = wild_path[:pos] + str(i) + '.fxd'
                        
                        result_list.append(self.renderbus_path_obj.convert_path(file)) 
            elif key == 'xmesh':
                print('-----------------------xmesh--------------------------')
                for asset in asset_list:
                    # print(asset)
                    splited_array = asset.split('|')
                    start_frame  = splited_array[0]
                    end_frame    = splited_array[1]
                    limit        = splited_array[2] # PHXSimulator | FireSmokeSim | LiquidSim
                    render_sequence    =splited_array[3]
                    proxy_sequence    = splited_array[4]
                    
                    start = int(start_frame)
                    end   = int(end_frame)
                    
                    if limit!='true':
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
                            print('[err]%s is not match' % (self.ANIMATION_RANGE))
                        # frame_arr=self.ANIMATION_RANGE.split('-')
                        # if len(frame_arr)==1:
                            # start=end=int(frame_arr[0])
                        # elif len(frame_arr)==2:
                            # start=int(frame_arr[0])
                            # end=int(frame_arr[1])
                            
                    for i in range(start , end+1, -1 if start > end else 1):
                        if render_sequence!=None and render_sequence!='':
                            file = render_sequence[:-10] + '%04d' % i + '.xmesh'
                            result_list.append(self.renderbus_path_obj.convert_path(file))
                        if proxy_sequence!=None and proxy_sequence!='':
                            file = proxy_sequence[:-10] + '%04d' % i + '.xmesh'
                            result_list.append(self.renderbus_path_obj.convert_path(file))
                    if render_sequence!=None and render_sequence!='':
                        renderSequenceFolder=os.path.dirname(self.renderbus_path_obj.convert_path(render_sequence))
                        if os.path.exists(renderSequenceFolder):
                            renderSequenceList=os.listdir(renderSequenceFolder)
                            for rSeq in renderSequenceList:
                                if rSeq.endswith('.xmdat'):
                                    result_list.append(os.path.join(renderSequenceFolder,rSeq))
                    if proxy_sequence!=None and proxy_sequence!='':
                        proxySequenceFolder=os.path.dirname(self.renderbus_path_obj.convert_path(proxy_sequence))
                        if os.path.exists(proxySequenceFolder):
                            proxySequenceList=os.listdir(proxySequenceFolder)
                            for p_seq in proxySequenceList:
                                if p_seq.endswith('.xmdat'):
                                    result_list.append(os.path.join(proxySequenceFolder,p_seq))
            elif key == 'phoenix':
                print('-----------------------phoenix--------------------------')
                
                for asset in asset_list:
                    splited_array = asset.split('|')
                    start_frame  = splited_array[0]
                    end_frame    = splited_array[1]
                    type        = splited_array[2] # PHXSimulator | FireSmokeSim | LiquidSim
                    node_name    =splited_array[3]
                    input_file    = splited_array[4]
                    output_file    = splited_array[5]
                    start = int(start_frame);
                    end   = int(end_frame);
                    if start==0 and end==0:
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
                            print('[err]%s is not match' % (self.ANIMATION_RANGE))
                        # frame_arr=self.ANIMATION_RANGE.split('-')
                        # if len(frame_arr)==1:
                            # start=end=int(frame_arr[0])
                        # elif len(frame_arr)==2:
                            # start=int(frame_arr[0])
                            # end=int(frame_arr[1])
                        
                    if input_file.startswith('$'):
                        input_file=output_file
                    if input_file.startswith('$'):
                        result_list.append(node_name) 
                        continue
                        
                    file = ''
                    #pos=input_file.rfind('####.aur')
                    input_file=input_file.strip('.aur')
                    input_file_base_name=os.path.basename(input_file)
                    char_count=self.countCharInStr(input_file_base_name,'#')
                    input_file=input_file.strip('#').strip('_')
                    
                    if type=='firesmokesim':
                        for i in range(start , end+1, -1 if start > end else 1):
                            if i >= 0 :
                                
                                file = input_file +'_'+ self.getSerial(i,char_count) + '.aur'
                            else:
                                file = input_file+'_' + str(i) + '.aur'
                            result_list.append(self.renderbus_path_obj.convert_path(file)) 
                    else:
                        for i in range(start , end+1, -1 if start > end else 1):
                        
                            if i >= 0 :
                                file = input_file  +'_'+ self.getSerial(i,char_count)  + '.aur'
                            else:
                                file = input_file  +'_'+ str(i) + '.aur'
                            result_list.append(self.renderbus_path_obj.convert_path(file)) 
            
            elif key == 'realflow':
               for asset in asset_list:
                   splited_array = asset.split('|')
                   start_frame  = splited_array[0]
                   end_frame    = splited_array[1]
                   padding_size = splited_array[2] 
                   format      = splited_array[3]
                   base_dir     = splited_array[4]
                   prefix      = splited_array[5]
                   # build sequence number
                   start = int(start_frame);
                   end   = int(end_frame);
                   file = ''
                   
                   
                   file_name =  format.replace('#', '*').replace('name', prefix).replace('ext', 'bin')  
                   file = os.path.join(base_dir, file_name)      

                   for i in range(start , end+1, -1 if start > end else 1):
                        if i >= 0:
                            serial = str(i).zfill(int(padding_size))
                        else:
                            serial = str((sys.maxsize+1)*2+i)
                        result_list.append(self.renderbus_path_obj.convert_path(file.replace('*',serial))) 
                            
                              
                        
            elif key == 'vrmesh':
                 for asset in asset_list:
                    wild_path = asset
                    if wild_path.endswith('.vrmesh'):
                        file_path = self.renderbus_path_obj.convert_path(wild_path)
                        result_list.append(file_path) 
                    else:
                        print('#########################################################')
                        #self.G_DEBUG_LOG.error('[Max vrmesh invalid: %s]' % wild_path)

            elif key == 'pointcache':
                for asset in asset_list:
                    self.get_point_cache_list(asset,result_list)
                    
                
            else:
                for asset in asset_list:
                    if asset.endswith('.ifl'):
                        # print('resultIFL.....', asset)
                        self.getIflList(asset,result_list)
                    else:
                        result_list.append(self.renderbus_path_obj.convert_path(asset))
                    
            
                #result_list = map(self.renderbus_path_obj.convert_path, asset_list)    
               
            
            result_dict[key] = result_list
            return result_dict
            
        return handler
        
    def checkDuplicateFile(self,list):
        result_dict={}
        
        
        for item1 in list:
            if item1==None or item1.strip()=='':
                continue
            item_name1=os.path.basename(item1)
            dup_list=[]
            for item2 in list:
                if item2==None or item2.strip()=='':
                    continue
                item_name2=os.path.basename(item2)
                if item_name1==item_name2:
                    dup_list.append(item2)
            if len(dup_list)>1:
                result_dict[item_name1]=dup_list
                
        return result_dict
                    
            
        
    def get_all_asset(self):
        asset_dict = {}
        
        for key in self.TIPS_CODE_DICT:
            key=key.replace('_missing','')
            asset_dict[key]    = self.getItemFromSection(key)
        '''
        asset_dict['texture']    = self.getItemFromSection('texture')
        asset_dict['vrmesh']     = self.getItemFromSection('vrmesh')
        asset_dict['alembic']    = self.getItemFromSection('alembic')
        asset_dict['fumefx']     = self.getItemFromSection('fumefx')
        asset_dict['phoenix']    = self.getItemFromSection('phoenix')
        asset_dict['xmesh']      = self.getItemFromSection('xmesh')
        asset_dict['pc2']        = self.getItemFromSection('pc2')
        asset_dict['pointcache'] = self.getItemFromSection('pointcache')
        asset_dict['realflow']   = self.getItemFromSection('realflow')
        asset_dict['ies']        = self.getItemFromSection('ies')
        asset_dict['xrefs']      = self.getItemFromSection('xrefs')
        asset_dict['error']      = self.getItemFromSection('error')
        '''
        
        # all assets
        dict_list = list(map(self.handleAsset(asset_dict), asset_dict))
        
        for dict in dict_list:
            self.G_DEBUG_LOG.info('------------------------------ start---------------------------------') 
            for asset_type, asset_list in list(dict.items()):
                self.gather_asset(asset_type, asset_list,asset_dict)
            self.G_DEBUG_LOG.info('------------------------------ end---------------------------------') 
        #self.ANALYZE_TXT_PARSER.write(codecs.open(self.G_ANALYZE_TXT_NODE, "w", "UTF-16"))
        
        self.G_DEBUG_LOG.info('------------------------------ get all asset end---------------------------------')
        #print ('asset_dict='+str(asset_dict))
        return asset_dict
        

        
    def loop_project_asset(self):
        if not self.ASSET_WEB_COOLECT_BY_PATH:
            for root, dirs, files in os.walk(self.G_INPUT_PROJECT_PATH): 
                for f in files: 
                    # print f,os.path.join(root, f)
                    self.G_INPUT_PROJECT_ASSET_DICT[f]=os.path.join(root,f)
                    
        #self.ASSET_INPUT_KEY_LIST= self.G_INPUT_PROJECT_ASSET_DICT.keys()
    

        

        
    
escape_dict={'\a':r'\a',
           '\b':r'\b',
           '\c':r'\c',
           '\f':r'\f',
           '\n':r'\n',
           '\r':r'\r',
           '\t':r'\t',
           '\v':r'\v',
           '\'':r'\'',
           '\"':r'\"',
           '\0':r'\0',
           '\1':r'\1',
           '\2':r'\2',
           '\3':r'\3',
           '\4':r'\4',
           '\5':r'\5',
           '\6':r'\6',
           '\7':r'\7',
           '\8':r'\8',
           '\9':r'\9'}

def raw(text):
    """Returns a raw string representation of text"""
    new_string=''
    for char in text:
        try: new_string+=escape_dict[char]
        except KeyError: new_string+=char
    return new_string
    
