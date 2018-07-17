# !/usr/bin/env python
# encoding:utf-8
# -*- coding: utf-8 -*-
from __future__ import with_statement
import argparse
import copy
import os
import subprocess
import _subprocess
import pprint
import sys
import shutil
import filecmp
import time
import re
import math
import multiprocessing
import json
import types

reload(sys)
sys.setdefaultencoding('utf-8')

currentPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')
currentPath = currentPath.lower()
if "user" in currentPath:
    function_path = os.path.join(currentPath.split('user')[0],"function")
    script_path = os.path.join(currentPath.split('user')[0], "script")
    os.chdir(script_path)
    sys.path.append(function_path)
    sys.path.append(script_path)
    import RayvisionPluginsLoader
else:
    function_path = os.path.join(currentPath,"function")
    script_path = os.path.join(currentPath, "script")
    os.chdir(script_path)
    sys.path.append(function_path)
    sys.path.append(script_path)
    import RayvisionPluginsLoader



class Maya(object):
    def __init__(self):
		
        self.current_path = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')
        self.current_path = self.current_path.lower()
        if "user" in self.current_path:
            self.current_path = self.current_path.split('user')[0]
        self.info_json = os.path.join(self.current_path,'info.json')
        print "json_path : %s" %self.info_json

    def get_platfom(self,platform):
        platform = str(platform)
        info_dict = {}
        with open(self.info_json ,'r') as fn:
            fn_dict = json.load(fn)
            info_dict = fn_dict[platform]
        info_dict["auto_plugins"] = info_dict["auto_plugins"].replace("/", "\\")
        return info_dict


    def get_json(self,**kwargs):
        options = {"common": {},
                   "renderSettings": {},
                   "mappings": {},
                   "mount": {},
                   "variables": {},
                   "platform": {},
                   "server" :{}}

        options["common"]["debug"] = kwargs["debug"]
        options["common"]["tmp"] = "%s/%s" % (os.environ["tmp"], kwargs["task_id"])
        if not os.path.exists(options["common"]["tmp"]):
            os.makedirs(options["common"]["tmp"])

        if kwargs["json"]:
            if os.path.exists(kwargs["json"]):
                options_json = eval(open(kwargs["json"]).read())
                for i in options_json:
                    options[i] = options_json[i]

                options["renderSettings"]["start"] = kwargs["start"]
                options["renderSettings"]["end"] = kwargs["end"]
                options["renderSettings"]["by"] = kwargs["by"]

                options["common"]["debug"] = kwargs["debug"]
                options["common"]["tmp"] = "%s/%s" % (os.environ["tmp"],
                                                      options["common"]["taskId"])
                if not os.path.exists(options["common"]["tmp"]):
                    os.makedirs(options["common"]["tmp"])

                options["common"]["plugin_file"] = kwargs["plugin_file"]

                options["platform"] = self.get_platfom(kwargs["platform"])
                return options
            else:
                raise Exception("Can not find the json file: %s." % kwargs["json"])

        if kwargs["task_id"]:
            options["platform"] = self.get_platfom(kwargs["platform"])
            if kwargs["storage_path"]:
                kwargs["storage_path"] = kwargs["storage_path"].replace("\\", "/")
                options["platform"]["storage_path"] = kwargs["storage_path"]
                options["platform"]["home_path"] = re.findall(r'(.+?)/\d+/' ,kwargs["storage_path"], re.I)[0]

            options["renderSettings"]["start"] = kwargs["start"]
            options["renderSettings"]["end"] = kwargs["end"]
            options["renderSettings"]["by"] = kwargs["by"]

            cfg_path = "%s/%s/%s" % (options["platform"]["cfg_path"],
                                     kwargs["task_id"], "temp")

            options["platform"]["cfg_path"] = cfg_path

            cfg_file = "%s/%s" % (cfg_path, "render.cfg")

            print os.path.join(cfg_path, "server.cfg")
            server_info = eval(open(os.path.join(cfg_path, "server.cfg")).read())
            server_info.setdefault("task_mode", 0)

            options["plugins"] = eval(open(os.path.join(cfg_path,
                                                        "plugins.cfg")).read())

            result = {}
            with open(os.path.join(cfg_path, "render.cfg"), "r") as f:
                while 1:
                    line = f.readline()
                    if "=" in line:
                        line_split = line.split("=")
                        result[line_split[0].strip()] = line_split[1].strip()
                    if ">>" in line:
                        break
                    if "[delete]" in line:
                        break

                cfg_info = result

            options["common"]["submitFrom"] = "client"
            options["common"]["render_file"] = cfg_info['cgFile']
            options["common"]["cgv"] = str(server_info["maya_version"])
            options["common"]["cgFile"] = server_info["maya_file"]
            options["common"]["cgSoftName"] = cfg_info["cgSoftName"]
            options["common"]["userId"] = int(server_info["user_id"])
            # options["common"]["taskId"] = int(server_info["task_id"])
            options["common"]["taskId"] = int(cfg_info["taskId"])
            options["common"]["projectId"] = int(cfg_info["projectId"])
            options["common"]["projectSymbol"] = cfg_info["projectSymbol"]
            options["common"]["parent_id"] = cfg_info.setdefault("parent_id", 0)
            options["common"]["chunk_size"] = cfg_info.setdefault("chunk_size", 1)

            options["renderSettings"]["renderType"] = "render.exe"
            options["renderSettings"]["renderableCamera"] = cfg_info["renderableCamera"]
            options["renderSettings"]["renderableLayer"] = cfg_info["renderableLayer"]
            options["renderSettings"]["projectPath"] = server_info["project"]
            options["renderSettings"]["tiles"] = kwargs.setdefault("tiles", 1)
            options["renderSettings"]["tile_index"] = kwargs.setdefault("tile_index", 0)
            options["renderSettings"]["width"] = int(cfg_info["width"])
            options["renderSettings"]["height"] = int(cfg_info["height"])

            options["server"] = server_info
            for i in options["server"]["variables"]:
                options["variables"][i] = options["server"]["variables"][i]

            cfg_info["mountFrom"] = eval(cfg_info["mountFrom"])

            sys.stdout.flush()
            print "storage path is: " + options["platform"]["home_path"]
            sys.stdout.flush()

            for i in cfg_info["mountFrom"]:
                if ":" not in i:
                    options["mount"][cfg_info["mountFrom"][i]] = options["platform"]["home_path"] + i

            options["mappings"] = server_info["mappings"]

            options["common"]["plugin_file"] = os.path.join(cfg_path,
                                                            "plugins.cfg")

            if options["common"]["userId"] in [963493, 963494,
                                               963495, 963496]:
                options["common"]["plugin_file"] = None

            options["common"]["father_id"] = None
            if options["common"]["userId"] == 964309:
                options["common"]["father_id"] = 964309

            if options["common"]["father_id"] == 964309:
                options["mount"]["K:"] = options["platform"]["home_path"] + \
                                         "/964000/964309/%s/maya/K" % (options["common"]["projectSymbol"])

            if options["common"]["userId"] == 1821185:
                options["common"]["father_id"] = 1821185

            if options["common"]["father_id"] == 1821185:
                options["mount"]["K:"] = options["platform"]["home_path"] + \
                                         "/1821000/1821185/%s/maya/K" % (options["common"]["projectSymbol"])

            for i in options["mount"]:
                if "/maya" in options["mount"][i]:
                    options["mount"][i] = re.sub(r'[0-9a-zA-Z_]+/maya/', "", options["mount"][i], re.I)
            return options


class RvOs(object):
    is_win = 0
    is_linux = 0
    is_mac = 0

    if sys.platform.startswith("win"):
        os_type = "win"
        is_win = 1
        # add search path for wmic.exe
        os.environ["path"] += ";C:/WINDOWS/system32/wbem"
    elif sys.platform.startswith("linux"):
        os_type = "linux"
        is_linux = 1
    else:
        os_type = "mac"
        is_mac = 1

    @staticmethod
    def get_windows_mapping():
        if RvOs.is_win:
            networks = {}
            locals = []
            for i in RvOs.run_command('wmic logicaldisk get deviceid,drivetype,providername'):
                if i.strip():
                    info = i.split()
                    if info[1] == "4":
                        networks[info[0]] = info[2].replace("\\", "/")
                    elif info[1] == "3":
                        locals.append(info[0])

        return (locals, networks)

    @staticmethod
    def get_virtual_drive():
        if RvOs.is_win:
            return dict([i.strip().split("\\: =>")
                         for i in RvOs.run_command('subst') if i.strip()])

    @staticmethod
    def run_command(cmd):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = _subprocess.SW_HIDE

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, startupinfo=startupinfo)

        while 1:
            # returns None while subprocess is running
            return_code = p.poll()
            if return_code == 0:
                break
            # elif return_code == 1:
            #     raise Exception(cmd + " was terminated for some reason.")
            elif return_code != None:
                print "exit return code is: " + str(return_code)
                break
                # raise Exception(cmd + " was crashed for some reason.")
            line = p.stdout.readline()
            yield line

    @staticmethod
    def get_process_list(name):
        process_list = []
        for i in RvOs.run_command("wmic process where Caption=\"%s\" get processid" % (name)):
            if i.strip() and i.strip().isdigit():
                process_list.append(int(i.strip()))

        return process_list

    @staticmethod
    def get_all_child():
        parent_id = str(os.getpid())
        child = {}
        for i in RvOs.run_command('wmic process get Caption,ParentProcessId,ProcessId'):
            if i.strip():
                info = i.split()
                if info[1] == parent_id:
                    if info[0] != "WMIC.exe":
                        child[info[0]] = int(info[2])

        return child

    @staticmethod
    def kill_children():
        print "start kill all child task"
        for i in RvOs.get_all_child().values():
            # os.kill is Available from python2.7, need another method.
            #            os.kill(i, 9)
            if RvOs.is_win:
                print "taskkill /f /t /pid %s" % (i)
                os.system("taskkill /f /t /pid %s" % (i))

    @staticmethod
    def timeout_command(command, timeout):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = _subprocess.SW_HIDE

        start = time.time()
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        while process.poll() is None:
            #            print "return: " + str(process.poll())
            time.sleep(0.1)
            now = time.time()
            if (now - start) > timeout:
                #                os.kill(process.pid, 9)
                if RvOs.is_win:
                    os.system("taskkill /f /t /pid %s" % (process.pid))

                return None
        return process.poll()

    @staticmethod
    def call_command(cmd, shell=0):
        return subprocess.call(cmd, shell=shell)


class Zip7(object):

    def __init__(self, exe):
        self.exe = exe

    def get_zip_info(self, zip_file):
        {'Attributes': 'A',
         'Block': '0',
         'Blocks': '1',
         'CRC': '836CB95D',
         'Encrypted': '-',
         'Headers Size': '138',
         'Method': 'LZMA2:20',
         'Modified': '2015-03-28 15:59:26',
         'Packed Size': '29191866',
         'Path': 'M02_P04_S046.mb',
         'Physical Size': '29192004',
         'Size': '138382876',
         'Solid': '-',
         'Type': '7z'}

        cmd = "\"%s\" l -slt \"%s\"" % (self.exe, zip_file)
        print cmd
        result = {}
        for line in RvOs.run_command(cmd):
            if "=" in line:
                line_split = [i.strip() for i in line.strip().split("=")]
                result[line_split[0]] = line_split[1]

        return result


    def is_same(self, zip_file, src):
        if os.path.exists(zip_file) and os.path.exists(src):
            zip_info = self.get_zip_info(zip_file)

            z_time = zip_info["Modified"]
            z_size = zip_info["Size"]

            f_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                   time.localtime(os.path.getmtime(src)))
            f_size = str(os.path.getsize(src))

            if z_time == f_time and z_size == f_size:
                return 1


class Render(dict, Zip7):

    def __init__(self, options):
        for i in options:
            self[i] = options[i]
        print "dont " *20
        # self.check_mapping()119768
        self.check_mapping()
        ma = self["common"]["cgFile"].replace(".rayvision", ".ma")
        if os.path.exists(ma):
            self["common"]["cgFile"] = ma
        else:
            self["common"]["cgFile"] = self["common"]["cgFile"].replace(".rayvision", ".mb")

    def get_cpu_cores(self, renderer=None):
        if renderer in ["arnold", "vray"]:
            return multiprocessing.cpu_count() - 1
        else:
            return multiprocessing.cpu_count()


    def check_mapping(self):
        if self["common"]["submitFrom"] == "client":
            self.clean_network()
            self.mapping_network()
            self.mapping_plugins()


    def run_command(self, command):
        # weird bug, don't know why
        #        return subprocess.call(command, shell=1)
        return subprocess.call(command)

    def clean_network(self):
        # return 0
        if self["server"]["user_id"] in []:
            return 0

        # if self.run_command("net use * /delete /y"):
        # print "clean mapping network failed."
        # else:
        # print "clean mapping network successfully."
        for j in range(3):
            if self.run_command("net use * /delete /y"):
                print "clean mapping network failed."
                time.sleep(5)
                print "Wait 5 seconds..."
            else:
                print "clean mapping network successfully."
                break
        sys.stdout.flush()

        self.clean_virtual_drive()
        sys.stdout.flush()

    def clean_vcfs(self):
        print "clean vcfs"
        cmd = r"c:\vcfsclient\vcfstask stop"
        print cmd
        sys.stdout.flush()
        self.run_command(cmd)
        sys.stdout.flush()

    def clean_virtual_drive(self, max=60):
        virtual_drive = RvOs.get_virtual_drive()
        if max == 0:
            print "clean virtual_drive failed"
            pprint.pprint(virtual_drive)
            sys.stdout.flush()
            return 0
        else:
            for i in virtual_drive:
                if self.run_command("subst %s /d" % (i)):
                    print "clean virtual drive failed: %s => %s" % (i,
                                                                    virtual_drive[i])
                    sys.stdout.flush()
                else:
                    print "clean virtual drive successfully: %s => %s" % (i,
                                                                          virtual_drive[i])
                    sys.stdout.flush()

            virtual_drive = RvOs.get_virtual_drive()
            if virtual_drive:
                time.sleep(1)
                print "wait 1 second and try remove subst again"
                sys.stdout.flush()
                self.clean_virtual_drive(max - 1)
            else:
                print "clean virtual_drive success"
                sys.stdout.flush()

    def create_virtua_drive(self, virtual_drive, path, max=60):
        if max == 0:
            print "can not create virutal drive: %s => %s" % (virtual_drive,
                                                              path)
            sys.stdout.flush()
            return 0
        else:
            self.run_command("subst %s %s" % (virtual_drive, path))
            sys.stdout.flush()
            if os.path.exists(virtual_drive + "/"):
                print "create virutal drive: %s => %s" % (virtual_drive,
                                                          path)
                print virtual_drive + "/" + " is exists"
                sys.stdout.flush()
            else:
                time.sleep(1)
                print "wait 1 second and try subst again"
                sys.stdout.flush()
                self.create_virtua_drive(virtual_drive, path, max-1)

    def mapping_network(self):
        for i in self["mount"]:
            if i == "vcfs":
                cmd = r"c:\vcfsclient\vcfstask start /path=c:\vcfsclient " \
                      "/conf=vcfs.conf /log=opt_result.log " \
                      "/letter=%s" % (self["mount"][i].strip(":").lower())
                print cmd

                sys.stdout.flush()
                if self.run_command(cmd):
                    sys.stdout.flush()
                    print "can not start vcfs %s" % (self["mount"][i])
                    sys.stdout.flush()

            else:
                # on windows, we must use '\' slash when mount, not '/'
                path = self["mount"][i].replace("/", "\\")
                if os.path.exists(path):
                    if path.startswith("\\"):
                        for j in range(3):
                            if self.run_command("net use %s %s" % (i, path)):
                                print "can not mapping %s to %s" % (i, path)
                                time.sleep(5)
                                print "Wait 5 seconds..."
                            else:
                                print "Mapping %s to %s" % (i, path)
                                break

                    elif path.lower().startswith("c:"):
                        path = r"\\127.0.0.1\c$" + path.split(":")[1]
                        if self.run_command("net use %s %s" % (i, path)):
                            print "can not mapping %s to %s" % (i, path)
                        else:
                            print "Mapping %s to %s" % (i, path)
                    else:
                        self.create_virtua_drive(i, path)
                else:
                    print '[warn]The path is not exist:%s' % path

                sys.stdout.flush()

        self.run_command("net use")
        self.run_command("subst")

    def mapping_plugins(self):
        drive = "B:"
        auto_plugins = self["platform"]["auto_plugins"]

        if self.run_command("net use %s %s" % (drive, auto_plugins)):
            print "can not mapping %s to %s" % (drive, auto_plugins)
        else:
            print "Mapping %s to %s" % (drive, auto_plugins)

    def copytree(self, src, dst):
        if not os.path.exists(dst):
            os.makedirs(dst)

        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)

            if os.path.isdir(s):
                self.copytree(s, d)
            else:
                if os.path.exists(d):
                    if filecmp.cmp(s, d):
                        print "%s already exists, skip" % (d)
                    else:
                        print "copy %s to %s" % (s, d)
                        shutil.copy2(s, d)

                else:
                    print "copy %s to %s" % (s, d)
                    shutil.copy2(s, d)

    def copytree2(self, src, dst):
        if not os.path.exists(dst):
            os.makedirs(dst)

        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)

            if os.path.isdir(s):
                self.copytree2(s, d)
            else:
                print "copy %s to %s" % (s, d)
                shutil.copy2(s, d)





class Nuke(Render):

    def __init__(self, options):
        Render.__init__(self, options)


class NukeMerge(Nuke):

    def __init__(self, options):
        Nuke.__init__(self, options)
        self.get_input_output()

    def get_input_output(self):
        tile_path = "%s/tiles/%s/%s" % (self["platform"]["storage_path"],
                                        self["common"]["taskId"],
                                        self["renderSettings"]["start"])
        tile_path = tile_path.replace("\\", "/")

        all_files = []
        for root, dirs, files in os.walk(tile_path):
            for i_file in files:
                ignore = 0
                for ignore_file in [".db"]:
                    if i_file.lower().endswith(ignore_file):
                        ignore = 1
                if not ignore:
                    all_files.append(os.path.join(root, i_file))

        self.tile_files_list = \
            [[re.sub(r'(.+/tiles/\d+/[-]?\d+)/(\d+)/(.+)', r"\1/%s/\3" % (index), i.replace("\\", "/"))
             for index in range(self["renderSettings"]["tiles"])]
            for i in all_files]
        self.tile_files = []
        for i in self.tile_files_list:
            if i not in self.tile_files:
                self.tile_files.append(i)

        # self.tile_files = [[self.get_right_file_name(j) for j in i]  for i in self.tile_files]

        self["renderSettings"]["output"] = "c:/work/render/%s/output/" % \
                                           (self["common"]["taskId"])

    def render(self):
        if self["common"]["debug"]:
            print "json info:"
            pprint.pprint(self)
        print self.tile_files
        for i in self.tile_files:
            if self["common"]["debug"]:
                print i
            print i
            tile_output = self["renderSettings"]["output"] + re.sub(r'(.+/tiles/[-]?\d+/[-]?\d+)(/0/)(.+)', r"\3", i[0])
            print   tile_output

            tile_folder = os.path.dirname(tile_output)
            print tile_folder
            tile_output = tile_folder + '/' + os.path.basename(tile_output)
            print tile_output
            if not os.path.exists(tile_folder):
                os.makedirs(tile_folder)

            self.merge_files(self["renderSettings"]["tiles"], i, tile_output)

    def merge_files(self, tiles, input_files, tile_output):
        # nuke_exe = r"B:\nuke\Nuke5.1v5\Nuke5.1.exe"
        os.environ['foundry_LICENSE'] = r'4101@10.60.5.248'
        nuke_exe = r"B:\nuke\Nuke10.5v5\Nuke10.5.exe"
        merge_images = os.path.join(self["platform"]["py_path"],"function", "NukeMerge.py")
        cmd = "\"%s\" -t \"%s\" -tiles %s -width %s -height %s" \
              " -tile_files \"%s\" -tile_output \"%s\" " % (nuke_exe, merge_images,
                                                            tiles,
                                                            self["renderSettings"]["width"],
                                                            self["renderSettings"]["height"],
                                                            input_files, tile_output)

        print cmd

        # is_complete = 0
        # re_complete = re.compile(r'Scene.+completed\.$', re.I)
        for line in RvOs.run_command(cmd):
            line_str = line.strip()
            if line_str:
                print line_str

                # if re_complete.findall(line_str):
                # is_complete = 1

                # if not is_complete:
                # exit(1)

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


class OiiO(Render):

    def __init__(self, options):
        Render.__init__(self, options)
        self.get_input_output()

    def get_input_output(self):
        tile_path = "%s/tiles/%s/%s" % (self["platform"]["storage_path"],
                                        self["common"]["taskId"],
                                        self["renderSettings"]["start"])
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

        self.tile_files = [[i.replace("\\", "/").replace("/0/", "/%s/" % (index))
                            for index in range(self["renderSettings"]["tiles"])]
                           for i in all_files]

        print self.tile_files
        self.tile_files = [[self.get_right_file_name(j) for j in i]
                           for i in self.tile_files]
        print self.tile_files
        # self.tile_files.replace("\\", "/")
        self["renderSettings"]["output"] = "c:/work/render/%s/output/" % \
                                           (self["common"]["taskId"])

    def merge_files(self, read1, read2, output):
        oiio_exe = r"B:\OpenImageIO\oiio_1.5.18\oiiotool.exe"
        cmd = "\"%s\" --over \"%s\" \"%s\" -o \"%s\"" % (oiio_exe, read1, read2, output)

        print cmd

        for line in RvOs.run_command(cmd):
            line_str = line.strip()
            if line_str:
                print line_str

    def render(self):
        if self["common"]["debug"]:
            print "json info:"
            pprint.pprint(self)

        for i_tile_files in self.tile_files:
            for index, i in enumerate(i_tile_files):
                if not index:
                    tile_output = self["renderSettings"]["output"] + i.split("/0/")[1]
                    if not os.path.exists(os.path.dirname(tile_output)):
                        os.makedirs(os.path.dirname(tile_output))
                    read1 = i
                else:
                    self.merge_files(read1, i, tile_output)
                    read1 = tile_output

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


class MayaClass(Render):

    def __init__(self, options):
        Render.__init__(self, options)
        self.get_maya_info()
        if self["common"]["userId"] in [1872633]:
            self.add_dirmap_val()
        self.create_setup_file()
        self.set_variables()
        if self["common"]["userId"] in [1868564]:
            self.set_plugins_myx()
        else:
            self.set_plugins()

    def get_maya_info(self):
        if os.path.exists(self["common"]["render_file"]):

            self["renderSettings"]["maya_file"] = self["common"]["render_file"]
        else:
            self["renderSettings"]["maya_file"] = os.path.split(self["common"]["cgFile"])[0] + "/" + \
                                                  os.path.split(self["common"]["render_file"])[1]

        self["renderSettings"]["render.exe"] = "C:/Program Files/Autodesk/" \
                                               "maya%s/bin/render.exe" % (self["common"]["cgv"])
        self["renderSettings"]["mayabatch.exe"] = "C:/Program Files/Autodesk/" \
                                                  "maya%s/bin/mayabatch.exe" % (self["common"]["cgv"])
        self["renderSettings"]["output"] = "c:/work/render/%s/output/" % \
                                           (self["common"]["taskId"])
        self["renderSettings"]["cache"] = self["renderSettings"]["output"]

        self["renderSettings"]["user_id"] = self["server"]["user_id"]
        if "gpuid" in os.environ:
            # if self["server"]["user_id"] in [1841567]:
            # self["renderSettings"]["output"] = "c:/work/render/%s/" \
            # "output/" % (self["common"]["taskId"])
            # else:
            self["renderSettings"]["output"] = "c:/work/render/%s/" \
                                               "output/%s_%s_%s/" % (self["common"]["taskId"],
                                                                     self["renderSettings"]["start"],
                                                                     self["renderSettings"]["end"],
                                                                     self["renderSettings"]["by"])
            self["renderSettings"]["cache"] = self["renderSettings"]["output"].replace("output", "cache")
            os.environ["REDSHIFT_LOCALDATAPATH"] = self["renderSettings"]["cache"]

        for i in ["output", "cache"]:
            if not os.path.exists(self["renderSettings"][i]):
                os.makedirs(self["renderSettings"][i])

        self["renderSettings"]["user_id"] = self["server"]["user_id"]

        if self["renderSettings"]["projectPath"]:
            default_workspace = os.path.join(r'\\10.50.5.29\o5\py\model\tim\maya_default_workspace', "workspace.mel")
            workspacemel = os.path.join(self["renderSettings"]["projectPath"],
                                        "workspace.mel")
            print workspacemel
            try:
                if not os.path.exists(workspacemel):
                    shutil.copy2(default_workspace, workspacemel)
            except Exception:
                pass

    def get_region(self, tiles, tile_index, width, height):
        n = int(math.sqrt(tiles))
        for i in sorted(range(2, n + 1), reverse=1):
            if tiles % i != 0:
                continue
            else:
                n = i
                break

        n3 = tiles / n
        n1 = tile_index / n3
        n2 = tile_index % n3

        top = height / n * (n1 + 1)
        # top = height / n * (n1 + 1) - 1
        left = width / n3 * n2
        bottom = height / n * n1
        right = width / n3 * (n2 + 1)
        # right = width / n3 * (n2 + 1) -1

        if right == width:
            right -= 1
        if top == height:
            top -= 1

        return left, right, bottom, top

    def create_setup_file(self):
        if self["mappings"]:
            self["renderSettings"]["setup_file"] = "%s/usersetup.mel" % \
                                                   (self["common"]["tmp"])

            with open(self["renderSettings"]["setup_file"], "w") as f:
                f.write("dirmap -en true;\n")
                for i in self["mappings"]:
                    if i != "None":

                        if not i.startswith("$") and not i.endswith(".abc"):
                            old_path = i
                            if isinstance(old_path, unicode):
                                old_path = i.encode("gb18030")
                            new_path = self["mappings"][i]
                            if isinstance(new_path, unicode):
                                new_path = self["mappings"][i].encode("gb18030")
                            f.write("dirmap -m \"%s\" \"%s\";\n" % (old_path,
                                                                    new_path))

    def add_dirmap_val(self):
        if self["common"]["userId"] in [1872633]:
            print("ADD MAPPINGS : prod/cgserver-02")
            adict = self["mappings"]
            adict["/prod/cgserver-02"] = "T:"
            print adict
            self["mappings"] = {}

    def set_variables(self):
        if self["common"]["userId"] in [963130]:
            os.environ["IDMT_PROJECTS"] = "Z:/Projects"
        else:
            for i in self["variables"]:
                if len(self["variables"][i]) == 3:
                    os.environ[i] = self["variables"][i]
                else:
                    os.environ[i] = os.path.join(self["platform"]["storage_path"],
                                                 "maya" + self["variables"][i])

        if self["mappings"]:
            os.environ.setdefault("MAYA_SCRIPT_PATH", "")
            if os.environ["MAYA_SCRIPT_PATH"]:
                os.environ["MAYA_SCRIPT_PATH"] += ";"
            os.environ["MAYA_SCRIPT_PATH"] += self["common"]["tmp"]
        else:
            os.environ.setdefault("MAYA_SCRIPT_PATH", "")
        for i in self["mappings"]:
            if i.startswith("$"):
                try:
                    variable = re.findall(r'\$\{(.+)\}', i, re.I)[0]
                    os.environ[variable] = self["mappings"][i]
                except:
                    pass

    def set_plugins(self):
        print "strat set plugins +++++++++++++++++++ "
        print self["common"]["plugin_file"]
        if self["common"]["plugin_file"]:
            sys.stdout.flush()

            if "gpu_card_no" in os.environ:
                print "gpu_card_no: " + os.environ["gpu_card_no"]
            else:
                print "gpu_card_no variable is not exists."
            sys.stdout.flush()

            print "MAYA_SCRIPT_PATH: " + os.environ["MAYA_SCRIPT_PATH"]
            plginLd = RayvisionPluginsLoader.RayvisionPluginsLoader()
            sys.stdout.flush()
            if self["platform"]["custom_config"]:
                custom_file = self["platform"]["custom_config"] + "/" + \
                              str(self["common"]["userId"]) + "/RayvisionCustomConfig.py"
                sys.stdout.flush()
                print "custom_config is: " + custom_file
                sys.stdout.flush()
            print "plugin path:"
            print self["common"]["plugin_file"]
            sys.stdout.flush()
            plginLd.RayvisionPluginsLoader(self["common"]["plugin_file"], [custom_file])
            print "MAYA_SCRIPT_PATH: " + os.environ["MAYA_SCRIPT_PATH"]
            sys.stdout.flush()
        print "end set plugins +++++++++++++++++++++++"

    def set_plugins_myx(self):
        print "--------------------Set Plugins start---------------------------"

        if self["common"]["userId"] in [1868564]:
            from MayaPlugin import MayaPlugin

        print self["common"]["plugin_file"]
        if self["common"]["plugin_file"]:
            sys.stdout.flush()

            if "gpu_card_no" in os.environ:
                print "gpu_card_no: " + os.environ["gpu_card_no"]
            else:
                print "gpu_card_no variable is not exists."
            sys.stdout.flush()

            print "MAYA_SCRIPT_PATH: " + os.environ["MAYA_SCRIPT_PATH"]

            sys.stdout.flush()
            if self["platform"]["custom_config"]:
                custom_file = self["platform"]["custom_config"] + "/" + \
                              str(self["common"]["userId"]) + "/RayvisionCustomConfig.py"
                sys.stdout.flush()
                print "[Custom_config] is: " + custom_file
                sys.stdout.flush()
            print "[Plugin path]:"
            print self["common"]["plugin_file"]
            sys.stdout.flush()

            maya_plugin = MayaPlugin(self["common"]["plugin_file"], [custom_file], self["common"]["userId"],
                                     self["common"]["taskId"])
            maya_plugin.config()
            sys.stdout.flush()

            print "MAYA_SCRIPT_PATH: " + os.environ["MAYA_SCRIPT_PATH"]
            sys.stdout.flush()
        print "--------------------Set Plugins  end---------------------------"


class MayaRender(MayaClass):

    def __init__(self, options):
        MayaClass.__init__(self, options)

        self.cmd_json = os.path.join(self["platform"]["py_path"],'user',str(self["common"]["userId"]),'cmd','cmd.json')
        if os.path.exists(self.cmd_json):
            print "custome cmd.json path : %s" % self.cmd_json
            self.get_cmd_json()
            for i in self.cmd_dict:
                self["renderSettings"][i] = self.cmd_dict[i]

    def get_cmd_json(self):
        with open(self.cmd_json ,'r') as fn:
            cmd_dict = json.load(fn)
        self.cmd_dict = cmd_dict
        return self.cmd_dict



    def render_progress(self, lin_str):

        if re.findall(r"log started", lin_str, re.I):
            return "\n\n render progress :: the scene  load end \r\n\n"

        elif re.findall(r"loaded [0-9] plugins from", lin_str, re.I):
            return "\n\n render progress :: arnold loading plugin \r\n\n"
        elif re.findall(r"rendering image at", lin_str, re.I):
            return "\n\n render progress :: arnold render is start \r\n\n"
        elif re.findall(r"Arnold shutdown", lin_str, re.I):
            return "\n\n render progress :: arnold render is end \r\n\n"
        elif re.findall(r"Scene.+completed\.$", lin_str, re.I):
            return "\n\n render progress :: maya render is end \r\n\n"
        else:
            render_progress = re.findall(r"(?<= | )(?:[0-9]+)(?=% done)", lin_str, re.I)
            if render_progress:
                render_progress = render_progress[0]
                return "\n\n render progress :: render  %s%% \r\n\n" % (render_progress)

    def render(self):

        self["renderSettings"]["tile_region"] = ""
        if self["renderSettings"]["tiles"] > 1:
            tile_region = self.get_region(self["renderSettings"]["tiles"],
                                          self["renderSettings"]["tile_index"],
                                          self["renderSettings"]["width"],
                                          self["renderSettings"]["height"])
            self["renderSettings"]["tile_region"] = " ".join([str(i) for i in tile_region])

            self["renderSettings"]["output"] = "c:/work/render/%s/output/%s/%s/" % \
                                               (self["common"]["taskId"], self["renderSettings"]["start"],
                                                self["renderSettings"]["tile_index"])

        if self["common"]["debug"]:
            print "json info:"
            pprint.pprint(self)
        print "*+" * 20
        print self["common"]["cgv"]

        if float(self["common"]["cgv"]) == 2017:
            # os.system(r'"xcopy /y /f \\10.60.100.101\o5\py\model\maya2017\prefs\pluginPrefs.mel C:\users\enfuzion\Documents\maya\2017\prefs\"')
            # shutil.copy("//10.60.100.101/o5/py/model/2017updata3/mayaBatchRenderProcedure.mel", "C:/Program Files/Autodesk/Maya2017/scripts/others/mayaBatchRenderProcedure.mel")
            os.system(
                "robocopy /e /ns /nc /nfl /ndl /np  \"//10.60.100.101/o5/py/model/2017updata3\"  \"C:/Program Files/Autodesk/Maya2017/scripts/others\"")

        if self["server"]["user_id"] in [119768, 962276]:
            if self["renderSettings"]["end"] > self["renderSettings"]["start"]:
                import rendered_frames
                frames_list = rendered_frames.get_retry_frames(self["renderSettings"]["start"],
                                                               self["renderSettings"]["end"],
                                                               self["platform"]["cfg_path"])
                if frames_list:
                    print '++++++++the frames %s is not render ,start render to cmd ++++++++++' % (frames_list)
                    self["renderSettings"]["start"] = frames_list[0]
                    self["renderSettings"]["end"] = frames_list[-1]
                else:
                    rendered_frames.del_frames(self["renderSettings"]["start"], self["renderSettings"]["end"],
                                               self["platform"]["cfg_path"])

        if self["common"]["userId"] in [962814, 1849749, 1858642, 1858237, 1858240, 1858241, 1858637, 1858638, 874812,
                                        1879925, 1879928, 1879929, 1879930, 1879931, 1879932, 1879934, 1879935, 1879936,
                                        1879937, 1879938, 1879963, 1879966, 1879967, 1879968, 1879969, 1879970, 1882048,
                                        1884724, 1886445, 1894815, 1894816, 1894817, 1894831, 1897697, 1897990, 1897991,
                                        1897992, 1897994, 1897996, 1897997, 1897998, 1897999, 1898000, 1898001, 1898002,
                                        1898003, 1898004, 1898006, 1898007, 1898008]:
            cgFile_path = self["renderSettings"]["maya_file"]
            if 'scenes' in cgFile_path:
                proj_path = cgFile_path.split("scenes")[0]
                self["renderSettings"]['projectPath'] = proj_path
                print self["renderSettings"]['projectPath']
        if self["renderSettings"]["projectPath"]:
            if os.path.exists(self["renderSettings"]["projectPath"]):
                os.chdir(self["renderSettings"]["projectPath"])

        if self["common"]["userId"] in [1897686]:
            if float(self["common"]["cgv"]) == 2015:
                self["renderSettings"]["render.exe"] = "C:/Program Files/Autodesk/" \
                                                       "Maya2015_base/bin/render.exe"
                self["renderSettings"]["mayabatch.exe"] = "C:/Program Files/Autodesk/" \
                                                          "Maya2015_base/bin/mayabatch.exe"
        if self["common"]["userId"] in [1894815]:
            if float(self["common"]["cgv"]) == 2017:
                if "mtoa" in self["plugins"]["plugins"] and self["plugins"]["plugins"]["mtoa"] == "1.3.0.0":
                    self["renderSettings"]["render.exe"] = "C:/Program Files/Autodesk/" \
                                                           "Maya2017_base/bin/render.exe"
                    self["renderSettings"]["mayabatch.exe"] = "C:/Program Files/Autodesk/" \
                                                              "Maya2017_base/bin/mayabatch.exe"

        cmd = "\"%(render.exe)s\" -s %(start)s -e %(end)s -b %(by)s " \
              "-proj \"%(projectPath)s\" -rd \"%(output)s\"" \
              % self["renderSettings"]

        if self["renderSettings"]["renderableCamera"]:
            if not "," in self["renderSettings"]["renderableCamera"] and \
                    not "{rayvision}" in self["renderSettings"]["renderableCamera"]:
                cmd += " -cam \"%(renderableCamera)s\"" % self["renderSettings"]

        if self["renderSettings"]["renderableLayer"]:
            if not "," in self["renderSettings"]["renderableLayer"]:
                cmd += " -rl \"%(renderableLayer)s\"" % self["renderSettings"]
        clearn_cmd = cmd

        if self["server"]["user_id"] == 962413:
            self["server"]["father_id"] = 962413




        PreRender = os.path.join(self["platform"]["py_path"],'script','PreRender.py').replace("\\","/")
        pre_render_dict = {}
        pre_render_dict["mapping"] = self["mappings"]
        pre_render_dict["user_id"] = self["common"]["userId"]
        pre_render_dict["task_id"] = self["common"]["taskId"]
        pre_render_dict["start"] = self["renderSettings"]["start"]
        pre_render_dict["rendersetting"] = self["renderSettings"]
        pre_render_dict["plugins"] = self["plugins"]["plugins"]
        pre_render_dict["c_prerender"] = os.path.join(self["platform"]["py_path"],'user',str(self["common"]["userId"]),'prerender','C_PreRender.py').replace("\\","/")



        # ------------------------------------------------------add preRender cmd---------------------------------------------------------------------
        # huaqiangfangte userid
        HQID = [1821228, 962413, 1821226, 1821229, 1821231, 1821234, 1821235, 1868236, 1868237, 1868238, 1868370,
                1868371, 1868372, 1868373, 1868374, 1868375, 1868376, 1868377, 1868379, 1868380, 1868382, 1868383,
                1868384]

        if self["common"]["userId"] not in [1818014, 1875231, 1846887, 1854355, 1814593, 963931, 1873017,
                                            1812148, 1812148, 1830380, 1871175, 1899488, 1820991] and self["common"]["userId"] not in HQID:
            cmd += " -preRender \"python \\\"pre_render_dict=%s;execfile(\\\\\\\"%s\\\\\\\")\\\"\"" % (pre_render_dict,PreRender)

        # if self["common"]["userId"] in [1844854]:
        #     cmd += " -preRender \"python \\\"user_id=%s;mapping=%s;plugins=%s;taskid=%s;rendersetting=%s;start=%s;execfile(\\\\\\\"//10.60.100.101/o5/py/model/prerender_1844854.py\\\\\\\")\\\"\"" % (
        #     self["common"]["userId"], self["mappings"], self["plugins"]["plugins"], self["common"]["taskId"],
        #     self["renderSettings"], self["renderSettings"]["start"])

        if self["server"]["user_id"] in HQID:
            cmd = "\"%(render.exe)s\" -s %(start)s -e %(end)s -b %(by)s " \
                  "-proj \"None\" -rd \"%(output)s\"" % self["renderSettings"]
            image_name = os.path.basename(self["renderSettings"]["maya_file"]).split("-")[0]
            # image_name = "<RenderPass>/" + image_name + "_<RenderPass>"
            # cmd += " -im \"%s\" -fnc 3" % image_name
            if "caml" in self["renderSettings"]["maya_file"].lower():
                camera = "CamL"
            elif "camr" in self["renderSettings"]["maya_file"].lower():
                camera = "CamR"
            else:
                raise Exception("Can not find the right camera in the maya file name.")

            # image_name = "<RenderPass>/" + image_name + "_" + camera + "_<RenderPass>"
            # cmd += " -im \"%s\" -fnc 3" % image_name
            cmd += " -preRender \"source \\\"//10.60.100.151/td/clientFiles/962413/render_command_light_new_2018DY_renderbus.mel\\\"\""
            # cmd += " -cam \"%s\"" % camera

        if self["server"]["user_id"] in [1875231]:
            cmd = "\"%(render.exe)s\" -s %(start)s -e %(end)s -b %(by)s " \
                  "-proj \"None\" -rd \"%(output)s\"" % self["renderSettings"]
            image_name = os.path.basename(self["renderSettings"]["maya_file"]).split("-")[0]
            # image_name = "<RenderPass>/" + image_name + "_<RenderPass>"
            # cmd += " -im \"%s\" -fnc 3" % image_name
            if "caml" in self["renderSettings"]["maya_file"].lower():
                camera = "CamL"
            elif "camr" in self["renderSettings"]["maya_file"].lower():
                camera = "CamR"
            else:
                raise Exception("Can not find the right camera in the maya file name.")

            # image_name = "<RenderPass>/" + image_name + "_" + camera + "_<RenderPass>"
            # cmd += " -im \"%s\" -fnc 3" % image_name
            cmd += " -preRender \"source \\\"//10.60.100.151/td/clientFiles/962413/render_command_light_new_2018DY_renderbus1875231.mel\\\"\""
            # cmd += " -cam \"%s\"" % camera

        if self["common"]["userId"] in [1873017]:
            cmd += " -preRender \"python \\\"user_id=%s;plugins=%s;taskid=%s;renderableCamera=\\\\\\\"%s\\\\\\\";maya_file=\\\\\\\"%s\\\\\\\";execfile(\\\\\\\"//10.60.100.101/o5/py/model/user/1873017/other/1873017.py\\\\\\\")\\\"\"" % (
            self["common"]["userId"], self["plugins"]["plugins"], self["common"]["taskId"],
            self["renderSettings"]["renderableCamera"], self['common']["render_file"])

        if self["common"]["userId"] in [1812148, 1830380, 1871175]:
            cmd += " -preRender \"python \\\"user_id=%s;mapping=%s;plugins=%s;taskid=%s;maya_ver=%s;rendersetting=%s;execfile(\\\\\\\"//10.60.100.101/o5/py/model/1812148.py\\\\\\\")\\\"\"" % (
            self["common"]["userId"], self["mappings"], self["plugins"]["plugins"], self["common"]["taskId"],
            self["common"]["cgv"], self["renderSettings"])
        if self["common"]["userId"] in [963931]:
            cmd += " -preRender \"source \\\"//10.60.100.101/o5/py/model/963931.mel\\\"\""

        if self["common"]["userId"] in [1814593]:
            cmd += " -preRender \" optionVar  -iv \\\"renderSetupEnable\\\" 0;source \\\"//10.60.100.101/o5/py/model/1814593.mel\\\";\""
        if self["common"]["userId"] in [1846887]:
            cmd += " -preRender \" optionVar  -iv \\\"renderSetupEnable\\\" 0;python \\\"user_id=%s;mapping=%s;plugins=%s;taskid=%s;execfile(\\\\\\\"//10.60.100.101/o5/py/model/prerender.py\\\\\\\")\\\"\"" % (
            self["common"]["userId"], self["mappings"], self["plugins"]["plugins"], self["common"]["taskId"])

        if self["common"]["userId"] in [1854355]:
            if self["common"]["taskId"] in [9373662, 9390999]:
                cmd += " -mr:v 5 -preRender \"source \\\"//10.60.100.101/o5/py/model/1854355.mel\\\"\""

        # ----------------------------------------------------------------------------------------------------------------------------------------------

        if "RenderMan_for_Maya" in self["plugins"]["plugins"]:
            cmd += " -r rman"
            if self["common"]["userId"] in [1814593]:
                cmd += " -ris "
        elif "3delight" in self["plugins"]["plugins"]:
            self["renderSettings"]["output"] += "<pass>/<scene>_<pass>" \
                                                "_<aov>_#.<ext>"
            cmd = "\"%(render.exe)s\" -r 3delight -rp all -an 1" \
                  " -s %(start)s -e %(end)s -inc %(by)s " \
                  " -proj \"%(projectPath)s\" -img \"%(output)s\"" \
                  % self["renderSettings"]


        # ----------------------redshift cmd -------------------------------------------------------------


        # ----------------------redshift cmd -------------------------------------------------------------
		



        if self["server"]["task_mode"] == 1 and self["common"]["parent_id"]:
            self["renderSettings"]["maya_file"] += "_rayvision.ma"

        if self["renderSettings"]["tile_region"]:
            if "mtoa" in self["plugins"]["plugins"] and "vrayformaya" in self["plugins"]["plugins"]:
                raise AssertionError("the tile render , only one renderer in the plug-in list")

            elif "mtoa" in self["plugins"]["plugins"]:
                cmd += " -r arnold -reg %(tile_region)s" % self["renderSettings"]
            elif "vrayformaya" in self["plugins"]["plugins"]:
                cmd += " -r vray -reg %(tile_region)s" % self["renderSettings"]
            else:
                cmd += " -r mr -reg %(tile_region)s" % self["renderSettings"]

        # if "mtoa" in self["plugins"]["plugins"]:
        #     if " -r " not in cmd:
        #         cmd += " -r arnold"
        #     cmd += " -ai:threads %s" % (self.get_cpu_cores("arnold"))
        #        if self["common"]["userId"] in [1832764]:
        #            cmd +=" -r file "
        if " -r " not in cmd and float(self["common"]["cgv"]) < 2017 and self["common"]["userId"] not in [1017637]:
            cmd += " -mr:art -mr:aml"

        # --------------------------------------------------------add postFrame cmd----------------------------------------------------------------
        if self["server"]["user_id"] in [119768]:
            if self["renderSettings"]["end"] > self["renderSettings"]["start"]:
                cmd += " -postFrame \"python \\\"execfile(\\\\\\\"//10.60.100.101/o5/py/model/rendered_frames.py\\\\\\\");set_rendered_frame(\\\\\\\"%s\\\\\\\")\\\";\"" % (
                self["platform"]["cfg_path"])

        if "-r rman" in cmd:
            cmd += " -setAttr Format:resolution \"%(width)s %(height)s\" \"%(maya_file)s\"" % self["renderSettings"]
        else:
            cmd += " -x %(width)s -y %(height)s \"%(maya_file)s\"" % self["renderSettings"]

        if self["server"]["user_id"] == 964309:
            self["server"]["father_id"] = 964309

        if self["server"]["user_id"] in [1811222, 1301816, 963685, 1816635]:
            if not os.path.exists(self["renderSettings"]["output_redshift"]):
                os.makedirs(self["renderSettings"]["output_redshift"])
            self["renderSettings"]["bat"] = r"B:\scripts\Maya\Erender_RS.bat"
            self["renderSettings"]["task_id"] = self["common"]["taskId"]
            cmd = "\"%(bat)s\" %(user_id)s %(task_id)s \"%(render.exe)s\" " \
                  "\"%(renderableLayer)s\" %(start)s %(end)s %(by)s " \
                  "\"%(projectPath)s\" \"%(maya_file)s\" \"%(output_redshift)s\"" \
                  % self["renderSettings"]
        if self["server"]["user_id"] in [11111]:
            if not os.path.exists(self["renderSettings"]["output_redshift"]):
                os.makedirs(self["renderSettings"]["output_redshift"])
            self["renderSettings"]["bat"] = r"B:\scripts\Maya\redshift_cmd\Erender_RS.bat"
            self["renderSettings"]["task_id"] = self["common"]["taskId"]
            cmd = "\"%(bat)s\" %(user_id)s %(task_id)s \"%(render.exe)s\" " \
                  "\"%(renderableLayer)s\" %(start)s %(end)s %(by)s " \
                  "\"%(projectPath)s\" \"%(maya_file)s\" \"%(output_redshift)s\"" \
                  % self["renderSettings"]

        if self["server"]["user_id"] == 1819310:
            self["server"]["father_id"] = 1819310
        if self["server"]["user_id"] == 1845831:
            self["server"]["father_id"] = 1845831
        if self["server"]["user_id"] == 1821185:
            self["server"]["father_id"] = 1821185
        if self["server"]["user_id"] == 1844227:
            self["server"]["father_id"] = 1844227

        if self["server"]["father_id"] in [1819310, 1821185, 1845831, 1844227]:
            if not os.path.exists(self["renderSettings"]["output_redshift"]):
                os.makedirs(self["renderSettings"]["output_redshift"])
            self["renderSettings"]["bat"] = r"B:\scripts\maya\of3d.bat"
            self["renderSettings"]["task_id"] = self["common"]["taskId"]
            """
            cmd = "\"%(bat)s\" %(user_id)s %(task_id)s \"%(render.exe)s\" "\
                "\"%(renderableLayer)s\" %(start)s %(end)s %(by)s " \
                "\"%(projectPath)s\" \"%(maya_file)s\" \"%(output_redshift)s\"" \
                % self["renderSettings"]
            """
            if self["renderSettings"]["renderableCamera"]:
                if "," in self["renderSettings"]["renderableCamera"] or \
                        "{rayvision}" in self["renderSettings"]["renderableCamera"]:
                    self["renderSettings"]["renderableCamera"] = ""
            else:
                self["renderSettings"]["renderableCamera"] = ""

            if self["renderSettings"]["renderableLayer"]:
                if "," in self["renderSettings"]["renderableLayer"]:
                    self["renderSettings"]["renderableLayer"] = ""
            else:
                self["renderSettings"]["renderableLayer"] = ""

            cmd = "\"%(bat)s\" %(user_id)s %(task_id)s \"%(render.exe)s\" \"%(renderableCamera)s\" " \
                  "\"%(renderableLayer)s\" %(start)s %(end)s %(by)s " \
                  "\"%(projectPath)s\" \"%(maya_file)s\" \"%(output_redshift)s\" %(width)s %(height)s" \
                  % self["renderSettings"]

        if self["server"]["task_mode"] == 1 and not self["common"]["parent_id"]:
            self["renderSettings"]["maya_file"] = self["renderSettings"]["maya_file"].replace("\\", "/")
            self["renderSettings"]["cache_path"] = r"//10.50.242.1/d/cache/%s/AgentCache" % (self["common"]["taskId"])
            self["renderSettings"]["cache_name"] = "testCache"
            self["renderSettings"]["ass_path"] = r"//10.50.242.1/d/cache/%s/ArnoldContents" % (self["common"]["taskId"])
            self["renderSettings"]["ass_name"] = "renderTest"
            self["renderSettings"]["mtoa_path"] = r"B:/plugins/maya/miarmy/" \
                                                  "maya%s/miarmy_%s/maya_miarmy/bin/arnold/mtoa%s" \
                                                  % (self["common"]["cgv"],
                                                     self["plugins"]["plugins"]["miarmy"],
                                                     re.findall(r'\w+\.\d\.', self["plugins"]["plugins"]["mtoa"])[
                                                         0] + "0")
            self["renderSettings"]["maya_file_rayvision"] = self["renderSettings"]["maya_file"] + "_rayvision.ma"
            if not os.path.exists(self["renderSettings"]["cache_path"]):
                os.makedirs(self["renderSettings"]["cache_path"])
            if not os.path.exists(self["renderSettings"]["ass_path"]):
                os.makedirs(self["renderSettings"]["ass_path"])

            cmd1 = "\"%(mayabatch.exe)s\" \"%(maya_file)s\"" \
                   " -command \"McdBatchAgentCache2 \\\"\'%(cache_path)s\'\\\"" \
                   " \\\"\'%(cache_name)s\'\\\"\"" % self["renderSettings"]

            cmd2 = "\"%(mayabatch.exe)s\" \"%(maya_file)s\"" \
                   " -command \"McdBatchArnoldExport2 \\\"\'%(cache_path)s\'\\\"" \
                   " \\\"\'%(cache_name)s\'\\\" \\\"\'%(ass_path)s\'\\\"" \
                   " \\\"\'%(ass_name)s\'\\\" \\\"\'%(mtoa_path)s\'\\\"" \
                   " \\\"\'%(maya_file_rayvision)s\'\\\"\"" \
                   % self["renderSettings"]

            cmd = [cmd1, cmd2]
        print(self["server"]["user_id"])
        if str(self["server"]["user_id"]) in ["1861989", "1874138"]:
            ## user: ID dp03
            print("clearn cmds")
            cmd = clearn_cmd
            cmd += " -x %(width)s -y %(height)s \"%(maya_file)s\"" % self["renderSettings"]
            print(os.system("set"))
        print "render cmd info:"
        print cmd
        sys.stdout.flush()

        G_JOB_NAME = os.environ.get('G_JOB_NAME')
        render_log_path = "d:/log/render"
        render_log = "%s/%s/%s_render.log" % (render_log_path, self["common"]["taskId"], G_JOB_NAME)
        print render_log
        with open(render_log, "ab+") as l:

            start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print "the render start time :: {} \n".format(start_time)
            l.write("the render start time :: {} \n".format(start_time))
            l.write('render cmd info: \n')
            # l.write(cmd)
            l.flush()
            if isinstance(cmd, list):
                for i in cmd:
                    print "render cmd info:"
                    print i
                    sys.stdout.flush()

                    for line in RvOs.run_command(i):
                        l.write(line)
                        l.flush()
                        line_str = line.strip()
                        if line_str:
                            pass
                            print line_str
                end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print "the render end time :: {} \n".format(end_time)
                l.write("the render end time :: {} \n".format(end_time))
                l.flush()
            else:
                # subprocess.call(cmd)
                is_complete = 0
                re_complete = re.compile(r'Scene.+completed\.$', re.I)
                for line in RvOs.run_command(cmd):
                    l.write(line + "\n")
                    if self["common"]["userId"] in [1813119]:
                        if self.render_progress(line):
                            print self.render_progress(line)
                            l.write(self.render_progress(line))
                    l.flush()
                    line_str = line.strip()
                    if line_str:
                        pass
                        print line_str
                        if "ASSERT FAILED" in line_str:
                            RvOs.kill_children()
                            is_complete = 0
                            break
                        if "failed to render" in line_str:
                            RvOs.kill_children()
                            is_complete = 0
                            break
                        if "DL inf loop detected" in line_str:
                            RvOs.kill_children()
                            is_complete = 0
                            break

                        if "Stack trace:" in line_str:
                            RvOs.kill_children()
                            is_complete = 0
                            break
                        if self["common"]["userId"] in [963287]:
                            if "Maya exited with status -1073741818" in line_str:
                                exit(-1073741818)
                            if "Maya exited with status -1073741819" in line_str:
                                exit(-1073741819)
                        if self["common"]["userId"] in [1849653, 1873851]:
                            if "Maya exited with status -1073741819" in line_str:
                                exit(0)

                        if re_complete.findall(line_str):
                            RvOs.kill_children()
                            is_complete = 1
                            break
                end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print "the render end time :: {} \n".format(end_time)
                l.write("the render end time :: {} \n".format(end_time))
                l.flush()
                if not is_complete:
                    exit(1)
        if self["common"]["userId"] in [1873017]:
            print "copy vrmap"
            copy_vrmap_cmd = "c:/python27/python.exe" + " " + r"//10.60.100.101/o5/py/model/copy_vrmap.py" + " --ti " + str(
                self["common"]["taskId"]) + " --ot " + self["renderSettings"]['output'] + " --rlog " + render_log
            print "copy_vrmap_cmd :: %s " % copy_vrmap_cmd
            for line in RvOs.run_command(copy_vrmap_cmd):
                line_str = line.strip()
                if line_str:
                    print line_str


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='----------')
    parser.add_argument("--js", dest="json", type=str)
    parser.add_argument("--ti", dest="task_id", type=int)
    parser.add_argument("--pt", dest="platform", type=int)
    parser.add_argument("--sf", dest="start", type=int, required=1)
    parser.add_argument("--ef", dest="end", type=int, required=1)
    parser.add_argument("--by", dest="by", type=int, required=1)
    parser.add_argument("--lg", dest="log_object", type=str)
    parser.add_argument("--pl", dest="plugin_file", type=str)
    parser.add_argument("--sp", dest="storage_path", type=str)
    parser.add_argument("--tiles", dest="tiles", type=int, default=1)
    parser.add_argument("--tile_index", dest="tile_index", type=int, default=0)
    parser.add_argument("-d", dest="debug", default=False, action="store_true")

    kwargs = parser.parse_args().__dict__
    maya_info = Maya()
    options = maya_info.get_json(**kwargs)

    render = None
    if options["renderSettings"]["tiles"] == options["renderSettings"]["tile_index"]:
        render = NukeMerge(options)
    elif options["common"]["cgSoftName"] == "maya":
        if options["renderSettings"]["renderType"] == "render.exe":
            render = MayaRender(options)

    if render:
        render.render()
        if not options["common"]["debug"]:
            render.clean_network()
    else:
        raise Exception("Can not find the match render class.")
