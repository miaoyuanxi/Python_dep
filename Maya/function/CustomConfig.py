#!/usr/bin/env python
#encoding:utf-8
# -*- coding: utf-8 -*-

import sys
import os
import shutil
import subprocess
from imp import reload
reload(sys)
# sys.setdefaultencoding('utf-8')
from MayaPlugin import PluginBase

#要习惯兼容python 3 


def main(*args):
    clientInfo = args[0]
    cgName = clientInfo['cgName'] #str
    cgVersion = clientInfo['cgVersion']#str
    plugins = clientInfo['plugins'] #dict
    userId = clientInfo['userId']#str
    taskId = clientInfo['taskId']#str
    
    #调用主的插件配置流程脚本 MayaPlugin.py，获取  插件在D盘的位置。
    Base = PluginBase()
    mtoa_ver = plugins["mtoa"]    
    mtoa_plugin_dir = os.path.join(Base.get_json_ini('Node_D'),"mtoa",'software',cgName + cgVersion + '_' + "mtoa" + mtoa_ver).replace('\\','/')


    #定制mklink
    if os.path.exists('D:/METRO'):
        os.system(r'rd /s/q "%s"' % "D:/METRO")
    os.system(r"mklink /d  D:\METRO \\10.60.100.101\d\inputdata5\100016000\100016371\D\METRO")
    print("mklink   \\10.60.100.101\d\inputdata5\100016000\100016371\D\METRO ---> D:\METRO ")
    
    
    #根据软件版本定制渲染层方式
    if cgVersion=='2017':
        os.environ['MAYA_ENABLE_LEGACY_RENDER_LAYERS'] = '0' #定制rendersetup  方式  ，1 为renderlayer方式
        print ("ENABLE_LEGACY_RENDER_LAYERS finis !!!")

    


    if cgVersion=='2015':
        srcDir=r"B:/custom_config/1840132/2015-x64/prefs" 
        dstDir=r"C:/Users/enfuzion/Documents/maya/2015-x64/prefs"
        os.system ("robocopy /s  %s %s" % (srcDir, dstDir))  #拷贝预设
        print("set mentalRay batch option")


    if cgVersion=='2016.5':
        os.environ['MAYA_APP_DIR'] = r"B:/custom_config/1840132/MAYA_Home"   #定制首选项
        print ("Set maya 2016.5 prefer to B:/custom_config/1840132/MAYA_Home")
        print (os.environ.get('MAYA_APP_DIR'))
        
        #定制自定义插件  alshader 
        if plugins:
            if 'alshader' not in plugins:
                _ARNOLD_PLUGIN_PATH=os.environ.get('ARNOLD_PLUGIN_PATH')
                _MTOA_TEMPLATES_PATH=os.environ.get('MTOA_TEMPLATES_PATH')
                _MAYA_CUSTOM_TEMPLATE_PATH=os.environ.get('MAYA_CUSTOM_TEMPLATE_PATH') 
                
                os.environ['MAYA_CUSTOM_TEMPLATE_PATH'] = (_MAYA_CUSTOM_TEMPLATE_PATH if _MAYA_CUSTOM_TEMPLATE_PATH else "") + r";" + r"B:/custom_config/1840132/alShaders-win-1.0.0rc17-ai4.2.12.2/aexml"
                os.environ['ARNOLD_PLUGIN_PATH'] = (_ARNOLD_PLUGIN_PATH if _ARNOLD_PLUGIN_PATH else "") + r";"  + r"B:/custom_config/1840132/alShaders-win-1.0.0rc17-ai4.2.12.2/bin"
                os.environ['MTOA_TEMPLATES_PATH'] = (_MTOA_TEMPLATES_PATH if _MTOA_TEMPLATES_PATH else "") + r";" + r"B:/custom_config/1840132/alShaders-win-1.0.0rc17-ai4.2.12.2/ae"
                print("SET custom  alshader(rc17) env finish!!!")

                
                
    #定制自定义环境变量，做mklink，及映射
    os.environ['upServerPath'] = "//nas/data/PipePrj"
    os.environ['cocoN'] = "//nas/outsource/nezha_out"
    os.environ['upLocalCachePath'] = "//10.60.200.102/d/inputdata5/1908000/1908106/d/PipePrjCache/"
    hostFile = r"C:/Windows/System32/drivers/etc/hosts"
    ip = "10.60.200.102"
    net = "nas"
    f= open(hostFile,'r')
    lines = f.readlines()
    f.close()
    for line in lines[:]:
        if line.strip():
            if ip in  line.strip() or net in  line.strip() :
                lines.remove(line)
        else:
            lines.remove(line)    
    lines.append("\n%s %s\n" %(ip, net))
    print ("\nhost  %s == %s\n" %(ip, net))
    f= open(hostFile,'w')
    for line in lines:
        f.write(line)
    f.close()
    print ("maklin finished!!")
    print ("you can access \\nas")
    if not os.path.exists('N:'):
        os.system(r'net use N:  \\10.60.200.102\d\inputdata5\1908000\1908106\N')
        print("maping N")
    if not os.path.exists('Y:'):
        os.system(r'net use Y:  \\10.60.200.102\d\inputdata5\1908000\1908106\Y')
        print("mapping Y")