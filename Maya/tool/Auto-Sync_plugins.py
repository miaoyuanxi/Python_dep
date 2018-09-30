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



class AutoBase():
    def __init__(self,mode = "1",auto_file = None):
        self.mode = mode
        self.auto_file = auto_file
    
        self.w2 = {"ip_path":["//10.60.100.151/td","//10.60.200.150/td"],"user_name":"enfuzion","passwords":"ruiyun2016"}
        self.w3 = {"ip_path":["//10.30.100.151/td01","/10.30.100.151/td02"], "user_name": "enfuzion",
              "passwords": "Raywing@host8"}
        self.w4 = {"ip_path": ["//10.40.100.151/td01","//10.40.100.151/td02"], "user_name": "enfuzion",
              "passwords": "Raywing@host8"}
        self.w9 = {"ip_path": ["//10.80.243.50/td"], "user_name": "enfuzion",
              "passwords": "ruiyun2017"}
        self.GPU = {"ip_path": ["//10.90.96.51/td1"], "user_name": "enfuzion",
              "passwords": "ruiyun2016"}
    

            
    def copy_files(self,source,destination,my_log=None):
        self.TEMP_PATH = os.getenv('temp').replace('\\', '/')
        if my_log == None:
            my_log = self.TEMP_PATH + '/' + 'plugin.txt'
        cp_times = 0
        while cp_times < 3:
            cp_log = open(my_log, "wt")
            cmds_copy = '{fcopy_path} /cmd=diff /speed=full /force_close /no_confirm_stop /force_start  "{source}" /to="{destination}"'.format(
                fcopy_path='c:\\fcopy\\FastCopy.exe',
                source=os.path.join(source.replace('/', '\\')),
                destination=destination.replace("/","\\"),
            )
            source_copy = subprocess.Popen(cmds_copy, stdout=cp_log, shell=True)
            source_copy.wait()
            cp_times = (cp_times + 1) if not source_copy.returncode == 0 else 5
            cp_log.close()
            
    def cteate_voucher(self):
        do_cmd = "cmdkey / add: % b_path_ip % / user: % user_name % /pass: % password %"

    def get_auto_ini(self):
        platform_list = ["w2","w3","w4","w9","GPU"]
        for i in platform_list:
            platform_name = eval("self." + i)
            ip_path_list = platform_name["platform_name"]
            user_name = platform_name["user_name"]
            passwords = platform_name["passwords"]
            for ip_path in ip_path_list:
                cmd_voucher = "cmdkey / add: % %s % / user: % %s % /pass: % %s %" %(ip_path,user_name,passwords)
                subprocess.Popen(cmd_voucher, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, shell=False)

                if self.mode == "1":
                    source = self.auto_file
                    destination = ip_path + ""
        
if __name__ == '__main__':
    print(u"请选择同步方式，默认方式请填1，单个文件，同步到其他平台\n,高级方式请填2，从W2平台同步所有插件到其他平台，请慎重。。。")
    while True:
        mode = raw_input("mode: ")
        if mode == "1":
            print (u"请拖入要同步的文件，不能是文件夹，只能是单个文件")
            auto_file = raw_input('auto_file: ')
            break
        elif mode == "2":
            print(u"你想好了吗，你确定吗，你ok吗？确定请再输入2")
            while True:
                mode = raw_input("mode: ")
                if mode != "2":
                    print(u"别找抽啊")
                else:
                    break
        else:
            print(u"瞎搞，请重新输入")
            mode = raw_input("mode: ")
    if mode == "1":
        auto_file = auto_file
    else:
        auto_file = None
    AutoBase(mode,AutoBase)
    