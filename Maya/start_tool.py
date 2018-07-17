# ! /usr/bin/env python
# coding=utf-8


import os
import subprocess
import _subprocess
import pprint
import sys
import shutil
import filecmp
import time
import RayvisionPluginsLoader
import re
import json
import math






class StartTool():
    def __init__(self,user_id = '100000',task_id = '100000'):
        self.user_id = user_id
        self.task_id = task_id




    def run_command(self,cmd):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = _subprocess.SW_HIDE
        shell = 0
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, startupinfo=startupinfo,
                             shell=shell)
        while 1:
            # returns None while subprocess is running
            return_code = p.poll()
            if return_code == 0:
                break
            # elif return_code == 1:
            #     raise Exception(cmd + " was terminated for some reason.")
            elif return_code is not None:
                print "exit return code is: " + str(return_code)
                break
                # raise Exception(cmd + " was crashed for some reason.")
            line = p.stdout.readline()
            yield line


    def get_virtual_drive(self):
        return dict([i.strip().split("\\: =>")
            for i in self.run_command('subst') if i.strip()])



    def clean_network(self):
        # if self.run_command("net use * /delete /y"):
        # print "clean mapping network failed."
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
        virtual_drive = self.get_virtual_drive()
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

            virtual_drive = self.get_virtual_drive()
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
                self.create_virtua_drive(virtual_drive, path, max - 1)

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
                if path.startswith("\\"):
                    if self.run_command("net use %s %s" % (i, path)):
                        print "can not mapping %s to %s" % (i, path)
                    else:
                        print "Mapping %s to %s" % (i, path)
                else:
                    self.create_virtua_drive(i, path)

                sys.stdout.flush()

        self.run_command("net use")
        self.run_command("subst")

    def mapping_plugins(self):
        drive = "B:"
        if self.submitFrom == "client":
            auto_plugins = self.b_ip_dict[self.get_platform()]
            if self.run_command("net use %s %s" % (drive, auto_plugins)):
                print "can not mapping %s to %s" % (drive, auto_plugins)
            else:
                print "Mapping %s to %s" % (drive, auto_plugins)

    def get_platform(self):
        if self.task_id[:2] == "10":
            return "2"
        if self.task_id[:2] == "19":
            return "9"
        if self.task_id[0] == "8":
            return "8"
        if self.task_id[:2] == "16":
            return "gpu"



    def get_info(self):
        index = 0

        if int(self.user_id[-3:]) >= 500:
            fileId = str(int(self.user_id) - int(self.user_id[-3:]) + 500)
        else:
            fileId = str(int(self.user_id) - int(self.user_id[-3:]))

        data_ip_dict = {"2":"10.60.100.101","8":"10.70.242.102","9":"10.80.100.101","gpu":"10.90.100.101"}
        self.b_ip_dict = {"2":r"\\10.60.100.151\td","8":r"\\10.70.242.50\td","9":r"\\10.80.243.50\td","gpu":r"\\10.90.96.51\td1"}
        #网页端
        plugin_config1 = r"//%s/p5/config/%s/%s/%s/plugins.json" % (data_ip_dict[self.get_platform()],fileId, self.user_id, self.task_id)
        render_info1 = r"//%s/p5/config/%s/%s/%s/render.json" % (data_ip_dict[self.get_platform()],fileId, self.user_id, self.task_id)
        #客户端
        plugin_config2 = r"//%s/d/ninputdata5/%s/temp/plugins.cfg" % (data_ip_dict[self.get_platform()],self.task_id)
        render_info2 = r"//%s/d/ninputdata5/%s/temp/render.cfg" % (data_ip_dict[self.get_platform()],self.task_id)
        self.server_info = r"//%s/d/ninputdata5/%s/temp/server.cfg" % (data_ip_dict[self.get_platform()],self.task_id)

        self.custom_config = r"%s\custom_config" %(self.b_ip_dict[self.get_platform()])
        self.model = r"\\%s\o5\py\model" %(data_ip_dict[self.get_platform()])

        if os.path.exists(plugin_config1):
            index += 1
            self.submitFrom = "web"
            self.plugin_cfg_file = plugin_config1
            self.render_info = render_info1
        elif os.path.exists(plugin_config2):
            self.submitFrom = "client"
            index += 1
            self.plugin_cfg_file = plugin_config2
            self.render_info = render_info2
        if index == 0:
            print "this task id  is not exist!!!!!"
            return 0



    def get_mount(self):
        mountFrom = None
        if os.path.basename(self.render_info).endswith(".cfg"):
            with open(self.render_info, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if "mountFrom" in line:
                        exec(line)
                        print mountFrom
                        self.mount = mountFrom
                        break
        elif os.path.basename(self.render_info).endswith(".json"):
            with open(self.render_info, 'r') as file:
                file_str = file.read()
                render_info_dict = dict(eval(file_str))
                self.mount = render_info_dict["mntMap"]





    def get_plugins(self):
        pass



    def get_cmd(self):
        pass




    def config(self):

        self.clean_network()
        self.mapping_network()
        self.mapping_plugins()


        pass






    # model=r"D:\temp"









sys.path.append(model)
import RayvisionPluginsLoader

if os.path.exists(plugin_config1):
    plugin_cfg_file = plugin_config1
elif os.path.exists(plugin_config2):
    plugin_cfg_file = plugin_config2

if custom_plugin_cfg == "":
    plugin_cfg_file = plugin_cfg_file
else:
    plugin_cfg_file = custom_plugin_cfg
print "plugin_cfg_file"
print plugin_cfg_file
custom_file = custom_config + "/" + cusId + "/RayvisionCustomConfig.py"
print plugin_cfg_file
plginLd = RayvisionPluginsLoader.RayvisionPluginsLoader()
plginLd.RayvisionPluginsLoader(plugin_cfg_file, [custom_file])
with open(plugin_cfg_file, 'r') as file:
    file_str = file.read()
    plugis_dict = dict(eval(file_str))

    if plugis_dict:
        renderSoftware = plugis_dict['renderSoftware']
        softwareVer = plugis_dict['softwareVer']
        plugis_list_dict = plugis_dict['plugins']
        print plugis_list_dict
cmd1 = r"C:\Program Files\Autodesk\Maya%s\bin\maya.exe" % (softwareVer)
print '"' + cmd1 + '"'
cmd2 = 'cmd'
if cmd == "":
    cmd_str = cmd1
elif cmd == "2":
    cmd_str = cmd2
print cmd

os.system('"' + cmd_str + '"')


if __name__ == '__main__':
    cusId = raw_input("cusid: ")
    taskId = raw_input("taskId: ")
    custom_plugin_cfg = raw_input('custom_plugin_cfg: ')
    cmd = raw_input("cmd: ")
    print "custom_plugin_cfg"
    print custom_plugin_cfg
    print type(custom_plugin_cfg)
    if cusId == "":
        cusId = "1234567"
        fileId = "1234567"
    else:
        if int(cusId[-3:]) >= 500:
            fileId = str(int(cusId) - int(cusId[-3:]) + 500)
        else:
            fileId = str(int(cusId) - int(cusId[-3:]))
    if taskId == "":
        taskId = "1600000"