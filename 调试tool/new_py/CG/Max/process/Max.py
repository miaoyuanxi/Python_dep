#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import codecs
import json

from RenderBase import *
from CommonUtil import RBCommon as CLASS_COMMON_UTIL


class Max(RenderBase):
    def __init__(self,**param_dict):
        RenderBase.__init__(self,**param_dict)
        
        #global variable
        if self.G_ACTION != 'Analyze':
            ## kg
            self.G_KG='0'
            if ('gi' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['gi'] == '1') and ('primary_gi_engine' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['primary_gi_engine'] == '0'):
                if 'irradiance_map_mode' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['irradiance_map_mode'] == '4':
                    self.G_KG='100'
                    if 'photonnode' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['photonnode'] == '1':
                        self.G_KG='102'
                if 'irradiance_map_mode' in self.G_TASK_JSON_DICT['scene_info_render']['renderer'] and self.G_TASK_JSON_DICT['scene_info_render']['renderer']['irradiance_map_mode'] == '6':
                    self.G_KG='101'        
            
            ## only_photon
            if 'onlyphoton' in self.G_TASK_JSON_DICT['scene_info_render']['renderer']:
                self.G_ONLY_PHOTON = self.G_TASK_JSON_DICT['scene_info_render']['renderer']['onlyphoton']
        
            ## multi camera
            self.G_MULTI_CAMERA = False
            self.G_WORK_RENDER_TASK_OUTPUT_XXX = self.G_WORK_RENDER_TASK_OUTPUT.replace('\\','/')
            if 'renderable_camera' in self.G_TASK_JSON_DICT['scene_info_render']['common']:
                renderable_camera = self.G_TASK_JSON_DICT['scene_info_render']['common']['renderable_camera']  #list
                if len(renderable_camera) > 1:
                   self.G_MULTI_CAMERA = True
                   self.G_WORK_RENDER_TASK_OUTPUT_XXX = self.G_WORK_RENDER_TASK_OUTPUT_XXX + '/' + self.G_SMALL_TASK_ID
                   
            ## task.json(ascii)
            self.G_TASK_JSON_A = os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK_CFG,'task_a.json'))
            if self.G_CG_VERSION=='3ds Max 2012' or self.G_CG_VERSION=='3ds Max 2011' or self.G_CG_VERSION=='3ds Max 2010' or self.G_CG_VERSION=='3ds Max 2009':
                with codecs.open(self.G_TASK_JSON,'rb','utf-8') as fp1:
                    with codecs.open(self.G_TASK_JSON_A,'wb',sys.getfilesystemencoding()) as fp2:
                        content = fp1.read()
                        fp2.write(content)
                
                
        self.G_WORK_RENDER_TASK_BLOCK=os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK,'block'))
        self.G_WORK_RENDER_TASK_GRAB=os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK,'grab'))
        self.G_WORK_RENDER_TASK_MAX=os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK,'max'))
        self.G_WORK_RENDER_TASK_MAXBAK=os.path.normpath(os.path.join(self.G_WORK_RENDER_TASK,'maxbak'))
        self.G_CG_VERSION=self.G_TASK_JSON_DICT['software_config']['cg_name']+' '+self.G_TASK_JSON_DICT['software_config']['cg_version']
        dir_list=[]
        dir_list.append(self.G_WORK_RENDER_TASK_BLOCK)
        dir_list.append(self.G_WORK_RENDER_TASK_GRAB)
        dir_list.append(self.G_WORK_RENDER_TASK_MAX)
        dir_list.append(self.G_WORK_RENDER_TASK_MAXBAK)
        CLASS_COMMON_UTIL.make_dirs(dir_list)
        
        self.G_MAX_B=os.path.normpath('B:/plugins/max')
        self.G_MAX_SCRIPT=os.path.join(self.G_MAX_B,'script')
        
        self.G_NODE_MAXSCRIPT=os.path.normpath(os.path.join(self.G_NODE_PY,'CG/Max/maxscript'))
        # self.G_NODE_PY_CUSTOM=os.path.normpath(os.path.join(self.G_NODE_PY,'custom'))
        self.ASSET_WEB_COOLECT_BY_PATH=False
        
        
