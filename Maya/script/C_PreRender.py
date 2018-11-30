#!/usr/bin/env python
#encoding:utf-8
# -*- coding: utf-8 -*-
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import os,sys,re
import time

from PreRender import PreRenderBase as CLASS_PRE_BASE   #调用主的Prerender里面的类方法



def main(*args):
    print ("custome prerender  start ----------- ")
    info_dict = args[0]
    print (info_dict) #prerender  info   dict
    print (info_dict["user_id"]) #int
    print (info_dict["start"])   #int
    print (info_dict["mapping"]) #dict
    print (info_dict["task_id"])  #int
    print (info_dict["plugins"])  #dict
   
   
   
   
    #调用主的Prerender里面的类方法，过滤场景信息
    PRE_BASE = CLASS_PRE_BASE()    
    PRE_BASE.Test_prerender()
    PRE_BASE.get_image_namespace()
    
    
    #关闭动力学，因为不关 会边解算边渲染，导致渲染时间异常
    mel.eval("putenv(\"MAYA_DISABLE_BATCH_RUNUP\",\"1\"); global proc dynRunupForBatchRender() {}; ")
    print ("Set MAYA_DISABLE_BATCH_RUNUP = 1 ")    
    
    #设置动画模式为  DG  ，设置DG模式，可以定制首选项 ，也可以这样定制。
    mel.eval("optionVar -iv \"evaluationMode\" 1;")
    print "set evaluationMode to dg"    
    
    
    #刷新当前帧的前一帧，因为有时候缓存读取有问题，或者绑定时候模型飞，刷新当前帧就可以了 
    if info_dict["start"]:
        cmds.currentTime(int(start)-1, edit=True)
        print "update frame"        
    
    
    
    #Aronld   相关定制 
    
    for i in pm.ls(type="aiOptions"):
        if i.hasAttr("use_existing_tiled_textures"):            
            i.use_existing_tiled_textures.set(0)  #不使用存在的tx贴图。
            print "Set use_existing_tiled_textures OFF "   
        i.motion_blur_enable.set(0)
        i.abortOnError.set(0)   #关掉报错警告             
        if i.hasAttr("log_verbosity"):
            i.log_verbosity.set(1)   #日志级别设置成1
        if i.hasAttr("autotx"):
            i.autotx.set(False)   #关掉自动转换贴图，因为多帧同时转换会转换出错
            
        if i.hasAttr("textureMaxMemoryMB"):
            ar_node = pm.PyNode("defaultArnoldRenderOptions")
            ar_node.textureMaxMemoryMB.set(l=0)  #解除锁定 ，因为有些客户会锁定某些参数，锁定了是修改不了参数了，解锁，再设值          
            i.textureMaxMemoryMB.set(20480)   #设置贴图缓存

    #vray  相关定制
    
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            org_srdml = i.srdml.get()
            print "Your scens originalvray srdml is %s " % (org_srdml)
            if "vrayformaya" in info_dict["plugins"]:
                print type(info_dict["plugins"]["vrayformaya"])
                if info_dict["plugins"]["vrayformaya"] >= "3.10":
                    print "Your task vray version >= 3.10,set srdml to 0 "
                    i.srdml.set(0)    #vray  版本 在3.10  以上，设置  vray的动态缓存为0，充分利用cpu
                else:
                    i.srdml.set(20480)
                    print "Your vray version lower than  3.10.01,set srdml to 20480MB"    
    
    
        if i.hasAttr("sys_max_threads"):
            i.sys_max_threads.set(30)   #设置线程使用数，有时候内存分配出错，设置这个可以试一下
            PRE_BASE.log_scene_set("sys_max_threads","30")
            
        if i.hasAttr("sys_message_level"):
            i.sys_message_level.set(4)   #设置vray的日志级别，有时候一些异常报错  改变日志级别  可能会跳过
            PRE_BASE.log_scene_set("sys_message_level","4")        
    
    
    
    print ("custome prerender  end ----------- ")
    
    
    
    




