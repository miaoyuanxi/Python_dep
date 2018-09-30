#!/usr/bin/env python
#encoding:utf-8
# -*- coding: utf-8 -*-
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import os,sys,re
import time

from PreRender import PreRenderBase as CLASS_PRE_BASE



def main(*args):
    print ("custome prerender  start ----------- ")
    info_dict = args[0]
    print (info_dict) #prerender  info   dict
    print (info_dict["user_id"]) #int
    print (info_dict["start"])   #int
    print (info_dict["mapping"]) #dict
    print (info_dict["task_id"])  #int
    print (info_dict["plugins"])  #dict
   
    
    PRE_BASE = CLASS_PRE_BASE()
    
    PRE_BASE.Test_prerender()
    PRE_BASE.get_image_namespace()
    
    
    
    print ("custome prerender  end ----------- ")
    
    
    
    




