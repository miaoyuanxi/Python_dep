#!/usr/bin/env python
#encoding:utf-8
# -*- coding: utf-8 -*-
import os
import time
import subprocess
import re
import sys
import shutil
from CommonUtil import RBCommon as CLASS_COMMON_UTIL

class RBMayaUtil(object):
    def __init__(self):
        self.is_win = 0
        self.is_linux = 0
        self.is_mac = 0
        if sys.platform.startswith("win"):
            os_type = "win"
            self.is_win = 1
            #add search path for wmic.exe
            os.environ["path"] += ";C:/WINDOWS/system32/wbem"
        elif sys.platform.startswith("linux"):
            os_type = "linux"
            self.is_linux = 1
        else:
            os_type = "mac"
            self.is_mac = 1


    @classmethod
    def cmd(self, cmd_str, my_log=None, try_count=1, continue_on_error=False, my_shell=False,
            callback_func=None):  # continue_on_error=true-->not exit ; continue_on_error=false--> exit
        print(str(continue_on_error) + '--->>>' + str(my_shell))
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
    def killMayabatch(self,progressLog):
        progressLog.info('MayaLogDEBUG_TASKKILL_mayabatch')            
        try:
            os.system('taskkill /F /IM mayabatch.exe /T')
        except  Exception as e:
            progressLog.info('MayaLog2taskkill mayabatch.exe exeception')  
            progressLog.info(e)

    @classmethod      
    def kill_lic_all(self,my_log = None): 
        print ("+++++++++++++++++++++++kill lic starting +++++++++++++++++++++")
        # print "Rendering Completed!"

        # if not %errorlevel%==0 goto fail
        # echo "exit rlm "
        # wmic process where name="rlm.exe" delete
        # wmic process where name="JGS_mtoa_licserver.exe" delete
        # wmic process where name="rlm_redshift.exe" delete
        # wmic process where name="rlm_Golaem.exe" delete
        # wmic process where ExecutablePath="C:\\AMPED_mili\\rlm.exe" delete
        # ::wmic process where ExecutablePath="C:\\Golaem\\rlm_Golaem.exe" delete
        # %b_path%\tools\cmdow\cmdow.exe "C:\Golaem\rlm.exe" /cls
        # %b_path%\tools\cmdow\cmdow.exe "C:\Golaem\rlm_Golaem.exe" /cls
        # %b_path%\tools\cmdow\cmdow.exe "C:\AMPED\rlm.exe" /cls

        kill_win_cmd_list = []
        pid_name_list = []
        lic_process_list = []        
        cmdow_path = "B:" + r"/tools/cmdow/cmdow.exe"
        lic_path_list = [r"C:\Golaem\rlm.exe",r"C:\Golaem\rlm_Golaem.exe",r"C:\AMPED\rlm.exe"] 
        lic_list = ["rlm.exe","JGS_mtoa_licserver.exe","rlm_redshift.exe","rlm_Golaem.exe"]

        for i in lic_path_list:
            lic_path_list_cmd = cmdow_path + " " + i
            kill_win_cmd_list.append(lic_path_list_cmd)     

        if kill_win_cmd_list:
            print (kill_win_cmd_list)
            for i in kill_win_cmd_list:            
                try:
                    a = os.system(i)
                    print ('Have been killed the %s,return :%s' % (i, a))
                except OSError as e:
                    print ('There is not lic windows!!!')

        else:
            print ("the kill_win_cmd_list is none")


        RunningProcessList=[]
        KillList=[]

        f=os.popen('tasklist').readlines()

        for i in f:
            try:
                thisone=i.split()[0]
                if '.exe' not in thisone:
                    continue
                if thisone in RunningProcessList:
                    continue
                RunningProcessList.append(thisone)
                if thisone in lic_list:
                    KillList.append(thisone)
            except:
                pass

            
        if KillList:
            print (KillList)
            for name in KillList:  
                try:                              
                    a = os.system('taskkill /f /im '+name)
                    # command = 'taskkill /F /IM %s' %name
                    # a = os.system(command)
                    print ('Have been killed the %s,return :%s' % (name, a))
                except OSError as e:
                    print ('there is no process!!!')
                    
        print ("+++++++++++++++++++++++kill lic ending +++++++++++++++++++++")

    @classmethod
    def do_del_path(self,file_path,my_log = None):
        if os.path.isfile(file_path) and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print ("del file  %s" % file_path)
            except Exception as error:
                print( Exception,":",error )
                print ("dont del file %s" % file_path)
        if os.path.isdir(file_path) and os.path.exists(file_path):
            try:
                shutil.rmtree(file_path)
                print ("del path %s" % file_path)
            except Exception as error:
                print( Exception,":",error )
                print ("dont del path %s" % file_path)

    @classmethod
    def clean_dir(self,Dir):
        if os.path.isdir(Dir) and os.path.exists(Dir):
            try:
                for root, dirs, files in os.walk(Dir, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                print ("del path %s" % Dir)
            except Exception as error:
                print(Exception, ":", error)
                print ("dont del path %s" % Dir)

    @classmethod
    def run_command(self,cmd, ignore_error=None, shell=0):
        startupinfo = subprocess.STARTUPINFO()
        # startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
        # startupinfo.wShowWindow = _subprocess.SW_HIDE

        p = subprocess.Popen(cmd, stdin=subprocess.PIPE,stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, startupinfo=startupinfo,
            shell=shell)

        while 1:
            #returns None while subprocess is running
            return_code = p.poll()
            # if return_code == 0:
            #     break
            if return_code == 1:
                if ignore_error == 1:
                    break
                else:
                    raise Exception(cmd + " was terminated for some reason.")
            elif return_code != None and return_code != 0:
                if ignore_error == 1:
                    break
                else:
                    print ("exit return code is: " + str(return_code))
                    raise Exception(cmd + " was crashed for some reason.")
            line = p.stdout.readline()
            if not line:
                break
            yield line

    @staticmethod
    def get_process_list(self,name):
        process_list = []
        for i in self.run_command("wmic process where Caption=\"%s\" get processid" % (name)):
            if i.strip() and i.strip().isdigit():
                process_list.append(int(i.strip()))

        return process_list

    @staticmethod
    def get_all_child(self):
        parent_id = str(os.getpid())
        child = {}
        for i in self.run_command('wmic process get Caption,ParentProcessId,ProcessId'):
            if i.strip():
                info = i.split()
                if info[1] == parent_id:
                    if info[0] != "WMIC.exe":
                        child[info[0]] = int(info[2])

        return child

    @staticmethod
    def kill_children(self):
        print ("start kill all child task")
        for i in self.get_all_child().values():
            #os.kill is Available from python2.7, need another method.
#            os.kill(i, 9)
            
            if self.is_win:
                print ("taskkill /f /t /pid %s" % (i))
                os.system("taskkill /f /t /pid %s" % (i))

#     @staticmethod
#     def timeout_command(self,command, timeout):
#         startupinfo = subprocess.STARTUPINFO()
#         startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
#         startupinfo.wShowWindow = _subprocess.SW_HIDE
#
#         start = time.time()
#         process = subprocess.Popen(command, stdout=subprocess.PIPE,
#                                    stderr=subprocess.PIPE)
#         while process.poll() is None:
# #            print "return: " + str(process.poll())
#             time.sleep(0.1)
#             now = time.time()
#             if (now - start) > timeout:
# #                os.kill(process.pid, 9)
#                 if self.is_win:
#                     os.system("taskkill /f /t /pid %s" % (process.pid))
#
#                 return None
#         return process.poll()

    @classmethod
    def dict_get(self,tmp_dict,objkey,value_list = []):
        for k,v in list(tmp_dict.items()):
            if k == objkey:
                if v not in value_list:
                    value_list.append(v)
            else:
                if isinstance(v,dict):
                    self.dict_get(v,objkey,value_list)
        return value_list


class NukeMerge(dict):
    def __init__(self,options):
        dict.__init__(self)
        for i in options:
            self[i] = options[i]
        self.get_input_output()

    def get_input_output(self):
        tile_path = "%s/%s" % (self["g_tiles_path"],
                               self["g_cg_start_frame"])
        tile_path = tile_path.replace("\\", "/")
        all_files = []
        for root, dirs, files in os.walk(tile_path + "/0"):
            for i_file in files:
                ignore = 0
                for ignore_file in [".db"]:
                    if i_file.lower().endswith(ignore_file):
                        ignore = 1
                if not ignore:
                    all_files.append(os.path.join(root, i_file))

        self.tile_files = [[re.sub(r'(.+/temp_title/\d+/\d+)(/0/)(.+)', r"\1/%s/\3" % (index), i.replace("\\", "/"))
                            for index in range(self["tiles"])]
                           for i in all_files]

        self.tile_files = [[self.get_right_file_name(j) for j in i]
                           for i in self.tile_files]


    def render(self,mylog = None):
        self.mylog = mylog
        print (self.tile_files)
        for i in self.tile_files:
            tile_output = self["output"] + '/'+ re.sub(r'(.+/temp_title/\d+/\d+)(/0/)(.+)', r"\3", i[0])
            tile_output = tile_output.replace("\\","/")
            tile_folder = os.path.dirname(tile_output)
            if not os.path.exists(tile_folder):
                os.makedirs(tile_folder)

            self.merge_files(self["tiles"], i, tile_output)

    def merge_files(self, tiles, input_files, tile_output):
        # nuke_exe = r"B:\nuke\Nuke5.1v5\Nuke5.1.exe"
        os.environ['foundry_LICENSE'] = r'4101@10.60.5.248'
        nuke_exe = r"B:\nuke\Nuke10.5v5\Nuke10.5.exe"
        merge_images = os.path.join(self["func_path"], "NukeMerge.py")
        cmd = "\"%s\" -t \"%s\" -tiles %s -width %s -height %s" \
              " -tile_files \"%s\" -tile_output \"%s\" " % (nuke_exe, merge_images,
                                                            tiles,
                                                            self["width"],
                                                            self["height"],
                                                            input_files, tile_output)

        print (cmd)
        CLASS_COMMON_UTIL.cmd(cmd, my_log = self.mylog, continue_on_error=True, my_shell=True)

    def get_right_file_name(self, file_name):
        r = re.findall(r'.+(\.\d+$)', file_name, re.I)
        if r:
            dirname = os.path.dirname(file_name)
            basename = os.path.basename(file_name)
            basename = r[0].lstrip(".") + "." + basename.replace(r[0], "")
            right_file_name = os.path.join(dirname, basename)
            shutil.copy2(file_name, right_file_name)
            return right_file_name
        else:
            return file_name

