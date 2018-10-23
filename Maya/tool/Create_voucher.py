# !/usr/bin/env python
# encoding:utf-8
# -*- coding: utf-8 -*-

import os, sys
import subprocess
import time

voucher_list = ["10.60.100.151","10.60.200.150","10.60.200.151","10.60.100.152","10.80.243.50","10.80.243.51","10.30.100.151","10.30.100.152","10.40.100.151","10.40.100.152","10.90.96.51"]

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

try:
    for voucher_i in voucher_list:
        cmd_clean_voucher_1 = "net use /delete %s" %("\\\\" + voucher_i + "\\IPC$")
        cmd_clean_voucher_2 = "cmdkey /delete:%s" %(voucher_i)
        run_cmd(cmd_clean_voucher_1,try_count=1, continue_on_error=True)
        run_cmd(cmd_clean_voucher_2,try_count=1, continue_on_error=True)
    for voucher_i in voucher_list:
        cmd_create_voucher = "cmdkey /add:%s /user:%s /pass:%s" %(voucher_i,"tdadmin","Ray@td852")
        run_cmd(cmd_create_voucher,try_count=3, continue_on_error=True)
except Exception as e:
    print(Exception)
    print(e)



