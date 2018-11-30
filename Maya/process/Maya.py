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

        # 将self.G_INPUT_PROJECT_PATH和self.G_INPUT_CG_FILE替换成本地路径
        self.G_INPUT_CG_FILE = self.G_INPUT_CG_FILE.replace("\\", "/")
        self.G_INPUT_PROJECT_PATH = self.G_INPUT_PROJECT_PATH.replace("\\", "/")
        if self.G_RENDER_OS != '0':
            map_dict = self.G_TASK_JSON_DICT.get('mnt_map', {})
            for local_path, ip_path in map_dict.items():
                local_path = local_path.replace('\\', '/')
                ip_path = ip_path.replace('\\', '/')
                self.G_DEBUG_LOG.info("[ip_path   ] {}".format(ip_path))
                self.G_DEBUG_LOG.info("[local_path] {}".format(local_path))
                if self.G_INPUT_PROJECT_PATH.startswith(ip_path):
                    self.G_INPUT_PROJECT_PATH = self.G_INPUT_PROJECT_PATH.replace(ip_path, local_path)
                    self.G_DEBUG_LOG.info("*****[G_INPUT_PROJECT_PATH] {}****".format(self.G_INPUT_PROJECT_PATH))
        
                if self.G_INPUT_CG_FILE.startswith(ip_path):
                    self.G_INPUT_CG_FILE = self.G_INPUT_CG_FILE.replace(ip_path, local_path)
                    self.G_DEBUG_LOG.info("*****[G_INPUT_CG_FILE] {}****".format(self.G_INPUT_CG_FILE))

        self.G_INPUT_PROJECT_PATH = os.path.normpath(self.G_INPUT_PROJECT_PATH)
        self.G_INPUT_CG_FILE = os.path.normpath(self.G_INPUT_CG_FILE)
        self.format_log('done','end')
        
        
        
        
        
        