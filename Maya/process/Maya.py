#!/usr/bin/env python
#encoding:utf-8
# -*- coding: utf-8 -*-
import os
import sys
import re
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
        self.G_NODE_MAYACONFIG = os.path.normpath(os.path.join(self.G_NODE_PY, 'CG/Maya/config'))

        self.G_INPUT_CG_FILE = self.G_INPUT_CG_FILE.replace("\\","/")
        self.G_INPUT_PROJECT_PATH = self.G_INPUT_PROJECT_PATH.replace("\\","/")
        if self.G_RENDER_OS != '0':
            if 'mnt_map' in self.G_TASK_JSON_DICT:
                index = 0
                map_dict = self.G_TASK_JSON_DICT['mnt_map']
                for key, value in list(map_dict.items()):
                    project_str = self.G_INPUT_PROJECT_PATH
                    temp_str_p = project_str.split(self.G_USER_ID, 1)[0] + self.G_USER_ID + "/" + project_str.split(self.G_USER_ID, 1)[1].split("/")[1]
                    if value == temp_str_p:
                        index +=1
                        self.G_INPUT_PROJECT_PATH = re.sub(value, key, self.G_INPUT_PROJECT_PATH)
                    cg_file_str = self.G_INPUT_CG_FILE
                    temp_str_c = cg_file_str.split(self.G_USER_ID, 1)[0] + self.G_USER_ID + "/" + project_str.split(self.G_USER_ID, 1)[1].split("/")[1]
                    if value == temp_str_c:
                        index +=1
                        self.G_INPUT_CG_FILE = re.sub(value, key, self.G_INPUT_CG_FILE)
                    if index == 2:
                        break
    
        self.G_INPUT_PROJECT_PATH = os.path.normpath(self.G_INPUT_PROJECT_PATH)
        self.G_INPUT_CG_FILE = os.path.normpath(self.G_INPUT_CG_FILE)
        self.format_log('done','end')
        
        
        
        
        
        