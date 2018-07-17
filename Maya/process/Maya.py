#!/usr/bin/env python
#encoding:utf-8
# -*- coding: utf-8 -*-
import os
import sys
from RenderBase import *
from CommonUtil import RBCommon as CLASS_COMMON_UTIL
from imp import reload
reload(sys)
# sys.setdefaultencoding('utf-8')


class Maya(RenderBase):
    def __init__(self,**param_dict):
        RenderBase.__init__(self,**param_dict)
        self.format_log('Maya.init','start')
        
        
        #global variable
        
        self.G_CG_VERSION=self.G_TASK_JSON_DICT['software_config']['cg_name']+self.G_TASK_JSON_DICT['software_config']['cg_version']
        self.RENDER_LAYER_TYPE = self.G_SYSTEM_JSON_DICT['system_info']['common']['render_layer_type']

        self.G_NODE_MAYASCRIPT=os.path.normpath(os.path.join(self.G_NODE_PY,'CG/Maya/script'))
        self.G_NODE_MAYAFUNCTION=os.path.normpath(os.path.join(self.G_NODE_PY,'CG/Maya/function'))


        self.G_INPUT_CG_FILE = self.G_INPUT_CG_FILE.replace("\\","/")
        self.G_INPUT_PROJECT_PATH = self.G_INPUT_PROJECT_PATH.replace("\\","/")

        if 'mnt_map' in self.G_TASK_JSON_DICT:
            index = 0
            map_dict = self.G_TASK_JSON_DICT['mnt_map']
            for key, value in list(map_dict.items()):
                if value in self.G_INPUT_PROJECT_PATH:
                    index +=1
                    self.G_INPUT_PROJECT_PATH = re.sub(value, key, self.G_INPUT_PROJECT_PATH)
                if value in self.G_INPUT_CG_FILE:
                    index +=1
                    self.G_INPUT_CG_FILE = re.sub(value, key, self.G_INPUT_CG_FILE)
                if index == 2:
                    break

        self.G_INPUT_PROJECT_PATH = os.path.normpath(self.G_INPUT_PROJECT_PATH)
        self.G_INPUT_CG_FILE = os.path.normpath(self.G_INPUT_CG_FILE)
        self.format_log('done','end')
        
        
        
        
        
        