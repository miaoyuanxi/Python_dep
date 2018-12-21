#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import sys
import subprocess
import string
import time
import datetime
import shutil
import ctypes
import json
import re
import configparser
import codecs
import random
import threading
import copy
import collections
import urllib.request
import urllib.error
import FrameCheckerLinux
import os
import subprocess
import shutil
import sys
import time
import codecs
import json
import stat
import socket
import re
import platform
import uuid
from atexit import register


class MyxLib(object):
    def __init__(self):
    
        self.G_DEBUG_LOG = logging.getLogger('debug_log')
        self.G_RENDER_LOG = logging.getLogger('render_log')
        self.MY_LOGER = None
        
        
        
    def MyLog(self, message, extr="MyxLib"):
        if self.MY_LOGER:
            self.MY_LOGER.info("[%s] %s" % (extr, str(message)))
        else:
            if str(message).strip() != "":
                print("[%s] %s" % (extr, str(message)))
                
                
        
    def monitor_exit(self, resource_monitor):
        self.G_DEBUG_LOG.info('[monitor_exit]start...')
        software_name = os.path.basename(resource_monitor)

        kill_cmd = r'taskkill /F /IM %s /T' % software_name
        if self.G_RENDER_OS == '0':
            kill_cmd = r"ps -ef | grep -i %s | grep -v grep | awk '{print $2}' | xargs kill -9" % software_name

        os.system(kill_cmd)
        self.G_DEBUG_LOG.info('[monitor_exit]end...')
        
        
    def monitor_cmd(self, command):
        self.G_DEBUG_LOG.info(command)
        # register(self.monitor_exit, resource_monitor)
        # os.system(command)
        
        if self.G_RENDER_OS == '0':  # G_RENDER_OS:0 linux ,1 windows
            cmdp = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        else:
            # 子进程会随着父进程退出而退出，且会显示子进程的控制台窗口
            cmdp = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, creationflags=subprocess.CREATE_NEW_CONSOLE)

            
            
            
    def get_json_ini(self,json_path,objkey, default=None, idex=0):
        with open(json_path, 'r') as fn:
            fn_dict = json.load(fn)
            tmp_dict = fn_dict[self.CURRENT_OS]
            def get_dict(tmp_dict, objkey, default=None, idex=0):
                for k, v in list(tmp_dict.items()):
                    if k == objkey:
                        if isinstance(v, list):
                            v = v[idex]
                        elif v == None:
                            v = default
                        else:
                            v = v
                        return v
                    else:
                        # if type(v) is types.DictType:
                        if isinstance(v, dict):
                            re = get_dict(v, objkey, default, idex)
                            if re is not default:
                                if isinstance(re, list):
                                    re = re[idex]
                                elif re == None:
                                    re = default
                                else:
                                    re = re
                                # print re
                                return re
                return default
            
            key_v = get_dict(tmp_dict, objkey, default, idex)
        return key_v
            
            
    def clean_dir(self, Dir):
        for root, dirs, files in os.walk(Dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
    
    def do_del_path(self, file_path):
        if os.path.isfile(file_path) and os.path.exists(file_path):
            try:
                os.remove(file_path)
                self.MyLog("del file  %s" % file_path)
            except Exception as error:
                print(Exception, ":", error)
                self.MyLog("dont del file %s" % file_path)
        if os.path.isdir(file_path) and os.path.exists(file_path):
            try:
                shutil.rmtree(file_path)
                self.MyLog("del path %s" % file_path)
            except Exception as error:
                print(Exception, ":", error)
                self.MyLog("dont del path %s" % file_path)
    
    def make_dirs(self, dir_list=[]):
        if len(dir_list) > 0:
            for dir in dir_list:
                if not os.path.exists(dir):
                    os.makedirs(dir)
    
    def find_7z(self, _7z, folder):
        _7z_name = os.path.basename(_7z)
        if os.path.exists(_7z):
            info_file = os.path.splitext(_7z)[0] + ".info"
            if os.path.isfile(info_file):
                with open(info_file, 'r') as f:
                    dict_info = eval(f.read())
                    if 'mtime' in dict_info:
                        src_7z_mtime = dict_info['mtime']
                    if 'size' in dict_info:
                        src_7z_size = dict_info['size']
            else:
                src_7z_mtime = time.ctime(os.stat(_7z).st_mtime)
                src_7z_size = os.path.getsize(_7z)
            for des_7z in os.listdir(folder):
                if des_7z.startswith(_7z_name):
                    des_7z_file = os.path.join(folder, des_7z)
                    if os.path.isfile(des_7z_file):
                        des_7z_mtime = time.ctime(os.stat(des_7z_file).st_mtime)
                        des_7z_size = os.path.getsize(des_7z_file)
                        # print src_7z_mtime, des_7z_mtime
                        # print len(src_7z_mtime), len(des_7z_mtime)
                        # print src_7z_size, des_7z_size
                        if src_7z_mtime == des_7z_mtime and src_7z_size == des_7z_size:
                            return des_7z_file
                            self.MyLog('%s  is  same ' % _7z)
                        else:
                            return 0
        else:
            self.Mylog("the %s is not exists" % _7z)
            return 0
    
    def un_7z(self, zip_file, to, my_log=None):
        if my_log == None:
            my_log = self.TEMP_PATH + '/' + 'plugin.txt'
        un_times = 1
        while un_times < 3:
            if self.CURRENT_OS == "linux":
                cmd = 'unzip -o -d "%s" "%s"' % (to, zip_file)
            elif self.CURRENT_OS == "windows":
                self.TOOL_DIR = self.get_json_ini('toolDir')
                if not os.path.exists(self.TOOL_DIR):
                    self.TOOL_DIR = self.get_json_ini('toolDir', idex=1)
                self.ZIPEXE = "%s/7z.exe" % self.TOOL_DIR
                cmd = r'"%s" x -y "%s" -o"%s"' % (self.ZIPEXE, zip_file, to)
            else:
                self.my_log("Current OS is %s" % self.CURRENT_OS)
                sys.exit(555)
            un_log = open(my_log, "wt")
            source_unzip = subprocess.Popen(cmd, stdout=un_log, shell=True)
            source_unzip.wait()
            if not source_unzip.returncode == 0:
                un_times += 1
            else:
                un_times = 3
            un_log.close()
    
    def copy_7z(self, zip_file, to, my_log=None):
        if my_log == None:
            my_log = self.TEMP_PATH + '/' + 'plugin.txt'
        cp_times = 0
        while cp_times < 3:
            cp_log = open(my_log, "wt")
            cmds_copy = "copy \"%s\" \"%s\"" % (os.path.abspath(zip_file), os.path.abspath(to))
            if self.CURRENT_OS == "linux":
                cmds_copy = "cp \"%s\" \"%s\"" % (os.path.abspath(zip_file), os.path.abspath(to))
            source_copy = subprocess.Popen(cmds_copy, stdout=cp_log, shell=True)
            source_copy.wait()
            cp_times = (cp_times + 1) if not source_copy.returncode == 0 else 5
            cp_log.close()
    
    def cmd_copy(self, copy_source, to, my_log=None):
        if os.path.exists(copy_source):
            if my_log == None:
                my_log = self.TEMP_PATH + '/' + 'plugin.txt'
            cp_times = 0
            while cp_times < 3:
                cp_log = open(my_log, "wt")
                if os.path.isdir(copy_source):
                    cmds_copy = r'xcopy /y /f /e /v "%s" "%s"' % (os.path.abspath(copy_source), os.path.abspath(to))
                else:
                    cmds_copy = "copy %s %s" % (os.path.abspath(copy_source), os.path.abspath(to))
                source_copy = subprocess.Popen(cmds_copy, stdout=cp_log, shell=True)
                source_copy.wait()
                cp_times = (cp_times + 1) if not source_copy.returncode == 0 else 5
                cp_log.close()
        else:
            self.MyLog('canot exist  %s' % copy_source)
    
    # python copy
    def CopyFiles(self, copy_source, copy_target):
        copy_source = os.path.normpath(copy_source)
        copy_target = os.path.normpath(copy_target)
        copy_source = self.str_to_unicode(copy_source)
        copy_target = self.str_to_unicode(copy_target)
        try:
            if not os.path.exists(copy_target):
                os.makedirs(copy_target)
            if os.path.isdir(copy_source):
                self.copy_folder(copy_source, copy_target)
            else:
                shutil.copy(copy_source, copy_target)
            return True
        except Exception as e:
            print (e)
            return False
    
    def copy_folder(self, pyFolder, to):
        if not os.path.exists(to):
            os.makedirs(to)
        if os.path.exists(pyFolder):
            for root, dirs, files in os.walk(pyFolder):
                for dirname in dirs:
                    tdir = os.path.join(root, dirname)
                    if not os.path.exists(tdir):
                        os.makedirs(tdir)
                for i in xrange(0, files.__len__()):
                    sf = os.path.join(root, files[i])
                    folder = to + root[len(pyFolder):len(root)] + "/"
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    shutil.copy(sf, folder)
    
    def str_to_unicode(self, str, str_decode='default'):
        if not isinstance(str, unicode):
            try:
                if str_decode != 'default':
                    str = str.decode(str_decode.lower())
                else:
                    try:
                        str = str.decode('utf-8')
                    except:
                        try:
                            str = str.decode('gbk')
                        except:
                            str = str.decode(sys.getfilesystemencoding())
            except Exception as e:
                print ('[err]str_to_unicode:decode %s to unicode failed' % (str))
                print (e)
        return str
    
    def unicode_to_str(self, str, str_encode='system'):
        if isinstance(str, unicode):
            try:
                if str_encode.lower() == 'system':
                    str = str.encode(sys.getfilesystemencoding())
                elif str_encode.lower() == 'utf-8':
                    str = str.encode('utf-8')
                elif str_encode.lower() == 'gbk':
                    str = str.encode('gbk')
                else:
                    str = str.encode(str_encode)
            except Exception as e:
                print ('[err]unicode_to_str:encode %s to %s failed' % (str, str_encode))
                print (e)
        else:
            print ('%s is not unicode ' % (str))
        return str
    
    def CalcMD5(self, filepath):
        with open(filepath, 'rb') as f:
            md5obj = hashlib.md5()
            md5obj.update(f.read())
            hash = md5obj.hexdigest()
            print(hash)
            return hash
    
    def check_file(self, file1, file2):  # 校验文件函数
        hashfile1 = self.CalcMD5(file1)
        hashfile2 = self.CalcMD5(file2)
        if hashfile1 == hashfile2:
            return 1
        else:
            return 0
            
            
    def print_trilateral(self,rows=4,mode=1):
        '''
        :param rows: rows counts
        :param mode: up  or  down
        :return: a trilateral
        '''
        for i in range(0, rows):
            for k in range(0, i + 1 if mode == 1 else rows - i):
                print " * ",  # 注意这里的","，一定不能省略，可以起到不换行的作用
                k += 1
            i += 1
            print "\n"
            
            
            
            
            
            
            
            
def decorator_use_in_class(f):
    def wrapper(self, *args, **kwargs):
        log_info_start = r'[{}.{}.start.....]'.format(self.__class__.__name__, f.__name__)
        log_info_end = r'[{}.{}.end.....]'.format(self.__class__.__name__, f.__name__)
        self.G_DEBUG_LOG.info(log_info_start)
        out = f(self, *args, **kwargs)
        self.G_DEBUG_LOG.info(log_info_end)
        return out
    return wrapper
    
    
    
    
    
class RBCommon(object):

    @classmethod
    def log_print(self, my_log, log_str):
        if my_log == None:
            print(log_str)
        else:
            my_log.info(log_str)

    @classmethod
    def del_net_use(self):

        try:
            self.cmd("net use * /del /y", my_shell=True)
        except:
            pass

    @classmethod
    def del_subst(self):
        def del_subst_callback(my_popen, my_log):
            while my_popen.poll() == None:
                result_line = my_popen.stdout.readline().strip()
                result_line = result_line.decode(sys.getfilesystemencoding())
                print(result_line)
                if result_line != '' and (':\:' in result_line):
                    substDriver = result_line[0:2]
                    substDriverList.append(substDriver)

            for substDriver in substDriverList:
                print(substDriver)
                delSubstCmd = 'subst ' + substDriver + ' /d'
                print(delSubstCmd)
                try:
                    os.system(delSubstCmd)
                except:
                    pass

        substDriverList = []
        self.cmd('subst', my_log=None, continue_on_error=False, my_shell=False, callback_func=del_subst_callback)
        # cmdp=subprocess.Popen('subst',stdin = subprocess.PIPE,stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = False)
        # cmdp.stdin.write('3/n')
        # cmdp.stdin.write('4/n')

    @classmethod
    def cmd____abort(self, cmd_str, my_log=None, try_count=1, continue_on_error=False,
                     my_shell=False):  # continue_on_error=true-->not exit ; continue_on_error=false--> exit
        print(str(continue_on_error) + '--->>>' + str(my_shell))
        if my_log != None:
            my_log.info('cmd...' + cmd_str)
        # self.G_PROCESS_LOG.info('try3...')
        l = 0
        resultStr = ''
        resultCode = 0
        while l < try_count:
            l = l + 1
            cmdp = subprocess.Popen(cmd_str, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    shell=my_shell)
            cmdp.stdin.write('3/n')
            cmdp.stdin.write('4/n')
            while cmdp.poll() == None:
                resultLine = cmdp.stdout.readline().strip()
                resultLine = resultLine.decode(sys.getfilesystemencoding())
                if resultLine != '' and my_log != None:
                    my_log.info(resultLine)

            resultStr = cmdp.stdout.read()
            resultStr = resultStr.decode(sys.getfilesystemencoding())
            resultCode = cmdp.returncode
            if resultCode == 0:
                break
            else:
                time.sleep(1)
        if my_log != None:
            my_log.info('resultStr...' + resultStr)
            my_log.info('resultCode...' + str(resultCode))

        if not continue_on_error:
            if resultCode != 0:
                sys.exit(resultCode)
        return resultCode, resultStr

    @classmethod
    def cmd(self, cmd_str, my_log=None, try_count=1, continue_on_error=False, my_shell=False,
            callback_func=None):  # continue_on_error=true-->not exit ; continue_on_error=false--> exit
        print("continue_on_error={}, my_shell={}".format(continue_on_error, my_shell))
        cmd_str = self.bytes_to_str(cmd_str)
        if my_log != None:
            my_log.info('cmd...' + cmd_str)
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

            if callback_func == None:
                while my_popen.poll() == None:
                    result_line = my_popen.stdout.readline().strip()
                    result_line = result_line.decode(sys.getfilesystemencoding())
                    if result_line != '' and my_log != None:
                        my_log.info(result_line)
            else:
                callback_func(my_popen, my_log)

            resultStr = my_popen.stdout.read()
            resultStr = resultStr.decode(sys.getfilesystemencoding())
            resultCode = my_popen.returncode
            if resultCode == 0:
                break
            else:
                time.sleep(1)
        if my_log != None:
            my_log.info('resultStr...' + resultStr)
            my_log.info('resultCode...' + str(resultCode))

        if not continue_on_error:
            if resultCode != 0:
                sys.exit(resultCode)
        return resultCode, resultStr

    @classmethod
    def cmd_python3(self, cmd_str, my_log=None):
        # if callback_func == None and my_shell == False
        python_path = r'c:\python34\python.exe'
        script_path = 'C:\\script\\new_py\\Util\\RunCmd.py'
        run_cmd_txt = 'C:\\script\\new_py\\RunCmd.txt'

        cmd_str_u = self.bytes_to_str(cmd_str)
        if my_log != None:
            my_log.info(cmd_str_u)

        # write cmd to RunCmd.txt
        f1 = codecs.open(run_cmd_txt, 'w', 'utf-8')
        f1.write(cmd_str_u)
        f1.close()

        cmd_p3 = r'%s "%s" "%s"' % (python_path, script_path, run_cmd_txt)
        self.cmd(cmd_p3, my_log=my_log)
        
    @classmethod
    def python_copy(self, copy_source, copy_target, mode='copy', my_log=None, try_count=1, continue_on_error=True):
        """
        拷贝或移动文件、文件夹（移动会将源文件夹删除）
        :param str copy_source: 源文件（夹）
        :param str copy_target: 目标文件夹
        :param str mode: "copy": 拷贝；"move"：移动
        :param str my_log: 日志对象
        :param str try_count: 总尝试次数
        :param str continue_on_error: True则忽略失败，False则失败退出
        """
        copy_source = os.path.normpath(copy_source)
        copy_target = os.path.normpath(copy_target)
        copy_source = self.bytes_to_str(copy_source)
        copy_target = self.bytes_to_str(copy_target)
        if my_log:
            my_log.info('[{0}]{1} --> {2}'.format(mode, copy_source, copy_target))
        
        current_count = 0
        is_error = False
        while current_count < try_count:
            current_count += 1
            try:
                if not os.path.exists(copy_target):
                    os.makedirs(copy_target)
                if os.path.isdir(copy_source):
                    self.copy_folder(copy_source, copy_target, mode=mode, my_log=my_log)
                    if mode == 'move':
                        shutil.rmtree(copy_source, ignore_errors=True)
                    if not os.path.exists(copy_source):
                        os.makedirs(copy_source)
                else:
                    # if mode == 'move':
                        # shutil.move(copy_source, copy_target)
                    # else:
                    shutil.copy2(copy_source, copy_target)
                    if mode == 'move':
                        os.remove(copy_source)
                is_error = False
                break
            except Exception as e:
                is_error = True
                print(e)
                if my_log:
                    my_log.info('[{0} error]{1}'.format(mode, e))
                
        if (not continue_on_error) and is_error:
            sys.exit(-1)
            

    @classmethod
    def copy_folder(self, pyFolder, to, mode='copy', my_log=None):
        if not os.path.exists(to):
            os.makedirs(to)
        if os.path.exists(pyFolder):
            for root, dirs, files in os.walk(pyFolder):
                for dirname in dirs:
                    tdir = os.path.join(root, dirname)
                    if not os.path.exists(tdir):
                        os.makedirs(tdir)
                for i in range(0, files.__len__()):
                    sf = os.path.join(root, files[i])
                    folder = to + root[len(pyFolder):len(root)] + "/"
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                        
                    # if mode == 'move':
                        # shutil.move(sf, folder)  # src: file; dest: dir
                    # else:
                    shutil.copy2(sf, folder)  # src: file; dest: dir

    @classmethod
    def error_exit_log(self, my_log, log_str, exit_code=-1, is_exit=True):
        my_log.info('\r\n\r\n---------------------------------[error]---------------------------------')
        my_log.info(log_str)
        my_log.info('-------------------------------------------------------------------------\r\n')
        if is_exit:
            sys.exit(exit_code)

    @classmethod
    def read_random_file(self, file):
        code_list = ['utf-8', 'gbk', sys.getfilesystemencoding(), 'utf-16']
        file_list = []
        for code in code_list:
            try:
                with open(file, 'r', encoding=code) as file_obj:
                    file_list = file_obj.readlines()
                break
            except:
                pass
        return file_list

    @classmethod
    def read_file(self, path1, my_code='UTF-8', my_mode='r'):
        if os.path.exists(path1):
            file_object = codecs.open(path1, my_mode, my_code)
            line = file_object.readlines()
            file_object.close()
            for r in line:
                print(r)
            return line
        pass

    @classmethod
    def write_file(self, file_content, my_file, my_code='UTF-8', my_mode='w'):

        if isinstance(file_content, (str, bytes)):
            file_content_u = self.bytes_to_str(file_content)
            with codecs.open(my_file, my_mode, my_code) as fl:
                fl.write(file_content_u)


        elif isinstance(file_content, (list, tuple)):
            with codecs.open(my_file, my_mode, my_code) as fl:
                for line in file_content:



                    fl.write(line)
        else:
            return False
        return True

    @classmethod
    def exit_tips(self, tips_str, tips_file, config_path, my_log):
        self.write_file(tips_str, tips_file)
        self.python_copy(os.path.normpath(tips_file), os.path.normpath(config_path))
        if my_log != None:
            self.error_exit_log(my_log, tips_str, is_exit=False)

        sys.exit(0)

    @classmethod
    def bytes_to_str(self, str1, str_decode='default'):
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

    @classmethod
    def str_to_bytes(self, str1, str_encode='system'):
        if isinstance(str1, str):
            try:
                if str_encode.lower() == 'system':
                    str1 = str1.encode(sys.getfilesystemencoding())
                elif str_encode.lower() == 'utf-8':
                    str1 = str1.encode('utf-8')
                elif str_encode.lower() == 'gbk':
                    str1 = str1.encode('gbk')
                else:
                    str1 = str1.encode(str_encode)
            except Exception as e:
                print('[err]str_to_bytes:encode %s to %s failed' % (str1, str_encode))
                print(e)
        else:
            print('%s is not str ' % (str1))
        return str1

    '''
        mount路径函数:
        {
            "/output":{
                "path":"//10.60.100.102/d/inputdata5/962500/962712",
                "username":"",
                "password":""
            }
        }
    '''

    @classmethod
    def mount_path(self, dict={}):
        print('mount paths :')
        for key in list(dict.keys()):
            key = os.path.normpath(key)
            if not os.path.exists(key):
                os.makedirs(key)
            path = dict[key]['path']
            if 'username' in dict[key] and 'password' in dict[key]:
                username = dict[key]['username']
                password = dict[key]['password']
                mount_cmd = 'mount -t auto -o username=%s,password=%s,codepage=936,iocharset=gb2312 "%s" "%s" ' % (
                username, password, path, key)
            else:
                mount_cmd = 'mount -t auto -o codepage=936,iocharset=gb2312 "%s" "%s"' % (path, key)
            try:
                self.cmd(mount_cmd)
            except Exception as e:
                print('mount path failed "%s" --> "%s"' % (path, key))
                print(e)

    @classmethod
    def make_dirs(self, dir_list=[]):
        if len(dir_list) > 0:
            for dir in dir_list:
                if os.path.exists(dir):
                    shutil.rmtree(dir, ignore_errors=True)
                os.makedirs(dir)

    # use when shutil.rmtree can't delete file
    @classmethod
    def remove_readonly(self, func, path, excinfo):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
            print('file can\'t remove:%s' % (path))
            print(e)

    @classmethod
    def get_system_version(self):
        return platform.platform()

    @classmethod
    def get_system(self):
        return platform.system()

    @classmethod
    def get_computer_mac(self):

        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])

    @classmethod
    def get_computer_hostname(self):
        return socket.gethostname()

    @classmethod
    def get_computer_ip(self):
        host_name = self.get_computer_hostname()
        ip_str = socket.gethostbyname_ex(host_name)[2][0]
        return ip_str

    @classmethod
    def write_hosts(self, server_dict):
        '''
        example
        {"192.168.0.88":["server1","storage.renderbus.com"],"10.60.100.1.102":["storage.renderbus.com"]}
        '''
        ip_list = []
        server_list = []
        for key_ip, value_server in list(server_dict.items()):
            print(key_ip)
            ip_list.append(key_ip)
            server_list.extend(value_server)

        host_file = r'C:\WINDOWS\system32\drivers\etc\hosts'
        hosts_list_old = self.read_file(host_file)

        hosts_list_new = []
        for host_line in hosts_list_old:
            if not host_line:
                continue
            host_line = host_line.strip()
            if host_line.startswith('#'):
                hosts_list_new.append(host_line)
                continue

            host_line_arr = host_line.split()

            if len(host_line_arr) == 2:
                print(host_line_arr[0] + '---------->' + host_line_arr[1])
                if host_line_arr[0].strip() in ip_list or host_line_arr[1].strip() in server_list:
                    pass
                else:
                    hosts_list_new.append(host_line)
            else:
                hosts_list_new.append(host_line)

        for key_ip, value_server in list(server_dict.items()):
            for server in value_server:
                hosts_list_new.append(key_ip + '      ' + server)
        for line in hosts_list_new:
            print(line)
        self.write_file(hosts_list_new, host_file)

    @classmethod
    def kill_app_list(self, app_list=[]):
        my_os = self.get_system()
        for app in app_list:
            if my_os == 'Windows':
                cmd_str = r'c:\windows\system32\cmd.exe /c c:\windows\system32\TASKKILL.exe /F /IM %s' % app
            elif my_os == 'Linux':
                cmd_str = ''
            self.cmd(cmd_str)

    @classmethod
    def start_server(self, server_name):
        cmd_str = 'C:\Windows\System32\sc.exe start "' + server_name + '"'
        return self.cmd(cmd_str)

    @classmethod
    def stop_server(self, server_name):
        cmd_str = 'C:\Windows\System32\sc.exe stop "' + server_name + '"'
        return self.cmd(cmd_str)

    @classmethod
    def query_server(self, server_name):
        find_str = r'C:\Windows\System32\findstr.exe'
        cmd_str = 'C:\Windows\System32\sc.exe query ' + server_name + '|' + find_str + ' "STATE"'
        self.cmd(cmd_str)

        '''
        check_info = check_popen.stdout.readlines()
        for elm in check_info:
            if "STOPPED" in elm.strip():
                to_install = False
                print elm.strip()

            if "RUNNING" in elm.strip():
                predone +=1
                print elm.strip()

        '''

    @staticmethod
    def json_load(json_path, encoding='utf-8'):
        p = json_path
        mode = 'r'
        with open(p, mode, encoding=encoding) as fp:
            d = json.load(fp)
        return d

    @staticmethod
    def json_save(json_path, obj, encoding='utf-8'):
        p = json_path
        mode = 'w'
        with open(p, mode, encoding=encoding) as fp:
            json.dump(obj, fp, indent=2)

    @staticmethod
    def find_frame(string):
        """
        :param string: eg. '1-10' '5' '1-10[2]'
        :return: (1, 10, 1) / (5, 5, 1) / (1, 10, 2)
        """
        start_frame = None
        end_frame = None
        by_frame = None
        pattern = '(-?\d+)(?:-?(-?\d+)(?:\[(-?\d+)\])?)?'
        m = re.match(pattern, string)

        if m is not None:
            start_frame = m.group(1)
            end_frame = m.group(2)
            by_frame = m.group(3)
            if end_frame is None:
                end_frame = start_frame
            if by_frame is None:
                by_frame = '1'
        else:
            print('[find_frame]frames is not match')
        return (start_frame, end_frame, by_frame)

    @classmethod
    def need_render_from_frame(cls, string):
        """
        根据 frames 字符串得到需要渲染的帧
        :param string: eg. '1-10' '5' '1-10[2]'
        :return: ['1', '2', '3', '4', '5', ...] / ['5'] / ['1', '3', '5', '7', '9']
        """
        l = []
        start_frame, end_frame, by_frame = cls.find_frame(string)
        if start_frame is not None:
            start_frame = int(start_frame)
            end_frame = int(end_frame)
            by_frame = int(by_frame)
            for i in range(start_frame, end_frame + 1, by_frame):
                l.append(str(i))
        return l

    @staticmethod
    def write_file1(path, content, encoding='utf-8', mode='w'):
        with open(path, mode, encoding=encoding) as fp:
            print(content, file=fp)

    
    @classmethod
    def make_dir(self, path):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except Exception as e:
                print(e)
                if not os.path.exists(path):
                    os.makedirs(path)
            
            
    @classmethod
    def generate_frame_serial(self, frame, count=4, mode='static'):
        """
        Generate the frame serial(e.g.0000, 10000, -001, -11111)
        :param str frame: current render frame
        :param int count: frame serial standard length
        :param str mode: 
            1.static: 静态帧类型，如count为4，则大于4位的帧数就保持原样，小于4位帧数则在最高位填充0；
            2.dynamic: 动态帧类型，count失效，帧数一直保持原样
        :return: The frame serial
        :rtype: str
        """
        frame = str(frame)
        if mode == 'static':
            frame_serial = frame.zfill(count)
        else:
            frame_serial = frame
        return frame_serial
        
    @classmethod
    def get_father_user_id(cls, user_id):
        return str((int(user_id)//500)*500)
            

class RBKafka():
    '''
    使用kafka的生产模块
    '''

    def __init__(self):
        print('init............')

    @classmethod
    def send_json_data(self, params, kafka_topic):
        try:
            parmas_message = json.dumps(params)  # <type 'str'>
            producer = self.producer
            # producer.send(self.kafkatopic, parmas_message.encode('utf-8'))
            print(parmas_message)
            future = producer.send(kafka_topic, parmas_message.encode('utf-8'))
            try:
                record_metadata = future.get(timeout=10)
                print(record_metadata.topic)
                print(record_metadata.partition)
                print(record_metadata.offset)
            except KafkaError as e:
                print('get data failed')
                print(e)
            # Successful result returns assigned partition and offset
            producer.flush()
        except KafkaError as e:
            print(e)

    @classmethod
    def produce(self, json_data, my_kafka_server, my_kafka_topic):
        flag = False
        j = 0
        self.producer = KafkaProducer(bootstrap_servers=my_kafka_server)
        while (not flag) and (j < 3):
            try:
                self.send_json_data(json_data, my_kafka_topic)
                # print params
                flag = True
                print('send info success')
            except Exception as e:
                print(e)
                j += 1
        return flag            
            
            
            
class FrameCheckerLinux(object):
    def __init__(self, src_directory, dest_directory, my_log=None):
        self.my_log = my_log
        self.log_print('[FrameCheckerLinux.start...]')
        self.system_sep = os.sep
        self.src_directory = CLASS_COMMON_UTIL.bytes_to_str(os.path.normpath(src_directory).rstrip(self.system_sep))
        self.dest_directory = CLASS_COMMON_UTIL.bytes_to_str(os.path.normpath(dest_directory).rstrip(self.system_sep))
    
    def log_print(self, log_str):
        """
        Write log to file or just print log.
        :param str log_str: The log that needs to be printed.
        """
        if self.my_log == None:
            print(log_str)
        else:
            self.my_log.info(log_str)
    
    def error_exit_log(self, log_str, exit_code=-1, is_exit=True):
        """
        Format the error/warning log.
        :param str log_str: The error/warning information that needs to be printed.
        :param int exit_code: The exit code.
        :param bool is_exit: Whether or not to exit directly.
        """
        big_info = '[error]' if is_exit else '[warning]'
        self.log_print('---------------------------------%s---------------------------------' % big_info)
        self.log_print(log_str)
        self.log_print('-------------------------------------------------------------------------\r\n')
        if is_exit:
            sys.exit(exit_code)
    
    def check_path_exist(self, path, retry_times=3, sleep_time=5):
        """
        Check whether the path exists, and reduce the impact of network factors by retrying.
        :param str path: The path to be checked.
        :param int retry_times: If the path does not exist, the number of retries.default is 3 times.
        :param int sleep_time: Sleep time before each retrial.default is 5 seconds.
        """
        current_times = 1
        while current_times <= retry_times:
            if os.path.exists(path):
                break
            else:
                current_times += 1
                if current_times == retry_times:
                    self.error_exit_log('The path is not exist:%s' % path)
                time.sleep(sleep_time)
    
    def check_output_empty(self):
        """
        1.Check whether the output directory of the node machine is empty.
        """
        # src_directory_list = os.listdir(self.src_directory)
        is_empty_output = True
        for root, dirs, files in os.walk(self.src_directory):
            if len(files) > 0:
                is_empty_output = False
                break
        if is_empty_output:
            self.error_exit_log('The output is empty:%s' % self.src_directory)
        
    def check_correctly_copy(self):
        """
        2.Check whether the pictures in the output directory of node machine are correctly copied to user storage.
        """
        for root, dirs, files in os.walk(self.src_directory):
            for file_name in files:
                src_file_path = os.path.join(root, file_name)
                src_file_size = os.path.getsize(src_file_path)
                file_relative_path = src_file_path.replace(self.src_directory, '').lstrip(self.system_sep)
                dest_file_path = os.path.join(self.dest_directory, file_relative_path)
                
                if src_file_size > 0:
                    if os.path.exists(dest_file_path):
                        dest_file_size = os.path.getsize(dest_file_path)
                        if src_file_size == dest_file_size:
                            self.log_print('{}==size:{}'.format(src_file_path, src_file_size))
                            continue
                        else:
                            self.error_exit_log('Size Different:\nsrc:    %s - %sB\ndest:   %s - %sB' % (src_file_path, str(src_file_size), dest_file_path, str(dest_file_size)), is_exit=False)
                    else:
                        self.error_exit_log('The path is not exist:%s' % dest_file_path, is_exit=False)
                else:
                    self.error_exit_log('The size of file is abnormal:%s : %sB' % (src_file_path, str(src_file_size)), is_exit=False)
    
    def run(self):
        self.check_path_exist(self.src_directory)
        self.check_output_empty()
        self.check_path_exist(self.dest_directory)
        self.check_correctly_copy()
        self.log_print('[FrameCheckerLinux.end...]')
            
class RBFrameChecker(object):
    
    @classmethod
    def get_file_size(self,local_path,server_path,my_log=None):
        local_path = local_path.replace('\\','/')
        server_path = server_path.replace('\\','/')
        local_path = CLASS_COMMON_UTIL.bytes_to_str(local_path)
        server_path = CLASS_COMMON_UTIL.bytes_to_str(server_path)
        check_file = []
        if os.path.exists(server_path):
            for root, dirs, files in os.walk(local_path):
                for file_name in files:
                    if file_name.split('.')[-1]!='db':
                        local_files = os.path.join(root, file_name).replace('\\', '/')
                        local_file_size = os.path.getsize(local_files)
                        server_files = server_path+local_files.split(local_path)[-1].replace('\\','/')
                        if os.path.exists(server_files):
                            server_file_size = os.path.getsize(server_files)
                            if float(local_file_size)/1024>0:
                                if local_file_size != server_file_size:
                                    CLASS_COMMON_UTIL.log_print(my_log,'Not the same as the file size：\n'+'    local: \"'+str(local_files)+'\"      size:'+str(local_file_size)+'\n    server: \"'+str(server_files)+'\"      size:'+str(server_file_size)+'\n')
                                else:
                                    #print 'nuke____',local_files
                                    check_file.append(local_files)
                            else:
                                CLASS_COMMON_UTIL.log_print(my_log,'This file \"' + local_files + '\" size abnormal !\n')
                        else:
                            CLASS_COMMON_UTIL.log_print(my_log,'This file \"'+local_files+'\" not in server path !\n')
        return check_file
        # self.check_texture(nuke_path, check_file)
    
    @classmethod
    def check_texture(self,nuke_path,texture_file,my_log=None):
        run_path = nuke_path
        run_path = CLASS_COMMON_UTIL.bytes_to_str(run_path)
        #print texture_file
        #print  '________',run_path
        os.environ['HFS'] = run_path
        _PATH_ORG = os.environ.get('PATH')
        os.environ['PATH'] = (_PATH_ORG if _PATH_ORG else '') + r';' + run_path
        #print os.environ['PATH']
        lib_path = '%s/lib' % (run_path)
        # _PATH_New = os.environ.get('PATH')
        # print '_PATH_New = ' + _PATH_New
        site_path = '%s/lib/site-packages' % (run_path)
        if lib_path not in sys.path:
            sys.path.append(lib_path)
        if site_path not in sys.path:
            sys.path.append(site_path)

        import nuke

        for i in texture_file :
            i = i.replace('\\','/')
            texture_type = ['avi', 'eps', 'dds', 'bmp', 'vrimg']
            if i.split('.')[-1] not in texture_type:
                #print i
                readtex = nuke.nodes.Read(file=i.encode('utf-8'))
                if readtex.metadata() == {}:
                    CLASS_COMMON_UTIL.log_print(my_log,'File is damaged'+i)
                else:
                    # print u'ok__________'+i
                    pass
            else:
                CLASS_COMMON_UTIL.log_print(my_log,' This file does not support Nuke do check'+i)
                
    @classmethod
    def main(self,local_path,server_path,my_log=None):
        nuke_path = r'C:/Program Files/Nuke10.0v4'
        check_file = self.get_file_size(local_path,server_path,my_log)
        if not check_file:
            CLASS_COMMON_UTIL.error_exit_log(my_log,'output have no file!')
        if platform.system() == 'Linux':
            pass
        else:
            if os.path.exists(nuke_path):
                try:
                    self.check_texture(nuke_path,check_file,my_log)
                except Exception as e:
                    CLASS_COMMON_UTIL.log_print(my_log,e)





#python 监测内存和cpu的使用率
import paramiko
import pymysql
import time

linux = ['192.168.0.179']

def connectHost(ip, uname='shenyuming', passwd='ajiongqqq'):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=uname, password=passwd, port=22)
    return ssh

def MainCheck():
    try:
        while True:
            time.sleep(1)
            for a in range(len(linux)):
                ssh = connectHost(linux[a])
                # 查询主机名称
                cmd = 'hostname'
                stdin, stdout, stderr = ssh.exec_command(cmd)
                host_name = stdout.readlines()
                host_name = host_name[0]
                # 查看当前时间
                csj = 'date +%T'
                stdin, stdout, stderr = ssh.exec_command(csj)
                curr_time = stdout.readlines()
                curr_time = curr_time[0]
            
                # 查看cpu使用率，并将信息写入到数据库中(取三次平均值)
                cpu = "vmstat 1 3|sed  '1d'|sed  '1d'|awk '{print $15}'"
                stdin, stdout, stderr = ssh.exec_command(cpu)
                cpu = stdout.readlines()
                cpu_usage = str(round((100 - (int(cpu[0]) + int(cpu[1]) + int(cpu[2])) / 3), 2)) + '%'
            
                # 查看内存使用率，并将信息写入到数据库中
            
                mem = "cat /proc/meminfo|sed -n '1,4p'|awk '{print $2}'"
                stdin, stdout, stderr = ssh.exec_command(mem)
                mem = stdout.readlines()
                mem_total = round(int(mem[0]) / 1024)
                mem_total_free = round(int(mem[1]) / 1024) + round(int(mem[2]) / 1024) + round(int(mem[3]) / 1024)
                mem_usage = str(round(((mem_total - mem_total_free) / mem_total) * 100, 2)) + "%"
            
                sql = "insert into memory_and_cpu values('%s','%s','%s','%s')" % (
                    host_name, curr_time, cpu_usage, mem_usage)
                db = connectDB()
                sqlDML(sql, db)
    except:
        print("连接服务器 %s 异常" % (linux[a]))

def connectDB(dbname='test11'):
    if dbname == 'test11':
        db = pymysql.connect("localhost", "root", "shen123", "test11")
        return db

def sqlDML(sql, db):
    cr = db.cursor()
    cr.execute(sql)
    db.commit()
    cr.close()

    #

if __name__ == '__main__':
    MainCheck()
##########################################################


# 先下载psutil库:pip install psutil
import psutil
import os, datetime, time

def getMemCpu():
    data = psutil.virtual_memory()
    total = data.total  # 总内存,单位为byte
    free = data.available  # 可以内存
    memory = "Memory usage:%d" % (int(round(data.percent))) + "%" + " "
    cpu = "CPU:%0.2f" % psutil.cpu_percent(interval=1) + "%"
    return memory + cpu

def main():

    while (True):
        info = getMemCpu()
        time.sleep(0.2)
        print info + "\b" * (len(info) + 1),

if __name__ == "__main__":
    main()

if __name__ == '__main__':
    print (            '\n\n-------------------------------------------------------[MayaPlugin]start----------------------------------------------------------\n\n')
    beginTime = datetime.datetime.now()

    endTime = datetime.datetime.now()
    timeOut = endTime - beginTime
    self.MyLog("RunningTime----%s" % (str(timeOut)))
    print (            '\n\n-------------------------------------------------------[MayaPlugin]end----------------------------------------------------------\n\n')


            
            
            
            
            
            
            
            
            
            
            