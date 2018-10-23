# !/usr/bin/env python
# encoding:utf-8
# -*- coding: utf-8 -*-

import os, sys
import subprocess
import time
Platform= raw_input("Platform: ")
Platform = str(Platform)
platform_num = "w" + str(Platform)
if Platform == "gpu":
    platform_num = "gpu"

B_ini_dict = {"w2":"//10.60.100.151/td",
              "w2-1":"//10.60.200.150/td",
              "w3":"//10.30.100.151/td01",
              "w3-1":"//10.30.100.151/td02",
              "w4":"//10.40.100.151/td01",
              "w4-1":"//10.40.100.151/td02",
              "w9":"//10.80.243.50/td",
              "gpu":"//10.90.96.51/td1"
              }

print("platform is %s"%(platform_num))


def bytes_to_str(str1, str_decode='default'):
    if not isinstance(str1, str):
        try:
            if str_decode != 'default':
                str1 = str1.decode(str_decode.lower())
            else:
                try:
                    str1 = str1.decode('utf-8')
                except:
                    try:
                        str1 = str1.decode('gbk')
                    except:
                        str1 = str1.decode(sys.getfilesystemencoding())
        except Exception as e:
            print('[err]bytes_to_str:decode %s to str failed' % (str1))
            print(e)
    return str1
def run_cmd(cmd_str,try_count=1, continue_on_error=False, my_shell=False,callback_func=None):  # continue_on_error=true-->not exit ; continue_on_error=false--> exit
    # print(str(continue_on_error) + '--->>>' + str(my_shell))
    cmd_str = bytes_to_str(cmd_str)
    print('cmd...' + cmd_str)
    # self.G_PROCESS_LOG.info('try3...')
    l = 0
    resultStr = ''
    resultCode = 0
    while l < try_count:
        l = l + 1
        my_popen = subprocess.Popen(cmd_str, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, shell=my_shell)
        my_popen.stdin.write(b'3/n')
        my_popen.stdin.write(b'4/n')

        while my_popen.poll() == None:
            result_line = my_popen.stdout.readline().strip()
            result_line = result_line.decode(sys.getfilesystemencoding())
            if result_line != '':
                print(result_line)

        resultStr = my_popen.stdout.read()
        resultStr = resultStr.decode(sys.getfilesystemencoding())
        resultCode = my_popen.returncode
        if resultCode == 0:
            break
        else:
            time.sleep(1)

    print('resultStr...' + resultStr)
    print('resultCode...' + str(resultCode))

    if not continue_on_error:
        if resultCode != 0:
            sys.exit(resultCode)
    return resultCode, resultStr

B_ini_dict[platform_num] = B_ini_dict[platform_num].replace("/","\\")
cmd1 = "net use b: /del /y"    
cmd2 = "net use b: \"%s\" \"Ray@td852\" /user:\"tdadmin\""%(B_ini_dict[platform_num])  
# cmd2 = "net use b: \"%s\" \"Ruiyun@2016\" /user:\"administrator\""%(B_ini_dict[platform_num])  
cmd3 = "net use /delete %s" %("\\\\" + B_ini_dict[platform_num].replace("\\","/").split("/")[2] + "\\IPC$")  
try:
    run_cmd(cmd3,try_count=3, continue_on_error=True)
    b = os.listdir("b:")
    if b:
        result_code,_  = run_cmd(cmd1,try_count=3, continue_on_error=False)
        if result_code == 0:
            result_code1= run_cmd(cmd2,try_count=3, continue_on_error=False)

        
except Exception as e:
    result_code1= run_cmd(cmd2,try_count=3, continue_on_error=False)

# 双击运行 py脚本
# 输入平台号  如   2 或 2-1 （表示你要映射W2的两个B盘）
#                  3 或 3-1 （表示你要映射W3的两个B盘）
#                  4 或 4-1 （表示你要映射W4的两个B盘）
#                  9      （表示你要映射W9的B盘）
#                  gpu    （表示你要映射gpu的B盘）