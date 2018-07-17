# ! /usr/bin/env python
# coding=utf-8
import os
import re
import sys
import subprocess
import _subprocess
import time
import logging
import uuid
import pprint
import shutil
import gzip
import traceback
import json
import locale
import cPickle
import glob
import codecs

if os.path.basename(sys.executable.lower()) in ["mayabatch.exe", "maya.exe"]:
    import pymel.core as pm
    import maya.cmds as cmds

    import ctypes
    print ctypes.cdll.msvcr100._getmaxstdio()
    ctypes.cdll.msvcr100._setmaxstdio(2048)
    print ctypes.cdll.msvcr100._getmaxstdio()

dir_dict={}
server_config = {"variables": {},
                 "spare_drives": "AEFGHIJKLMNOPQRSTUVWXYZ",
                 "upload_drive": None,
                 "project_drive": None,
                 "used_drives": None,
                 "forbidden_drives": ["B:", "C:", "D:"],
                 "mappings": {},
                 "mounts": {},
                 "maya_file": None,
                 "maya_version": None,
                 "client_version": None,
                 "project": None,
                 "project_custom": None,
                 "project_in_maya": None,
                 "project_in_ass": None,
                 "project_in_network": 0,
                 "project_get": None,
                 "user_id": None,
                 "father_id": None,
                 "seperate_account": 0,
                 "task_id": None,
                 "renderlayer": None,
                 "mac": "%012X" % uuid.getnode()}


def about():
    print 'Liu Qiang || MMmaomao'


def get_submit_options(ui_settings):
    options = {}
    app_config = RvOs.get_app_config()
    projects = RvOs.get_projects()
    options["project_symbol"] = ui_settings["project"]
    options["project_id"] = list(projects.keys())[list(projects.values()).index(ui_settings["project"])]
    options["user_id"] = app_config["userid"]
    options["platform"] = app_config["platform"]
    options["zone"] = app_config["zone"]
    options["cg_file_name"] = pm.sceneName()
    options["plugin_file"] = os.path.join(app_config["plugindir"], "maya_" + str(options["project_symbol"]) + ".pl")
    options["cg_version"] = "maya " + pm.about(v=1).split()[0]
    options["maya_version"] = pm.about(v=1).split()[0]
    options["cg_install"] = sys.executable
    options["custom_frames"] = ""
    options["client_version"] = app_config["guyversion"]
    options["language"] = "chinese"
    options["client_root"] = app_config["installdir"]
    options["temp_dir"] = ""
    options["project_path"] = ""
    options["analyze_mode"] = "normal"
    options["ini"] = os.path.join(os.environ["appdata"], r"RenderBus\%s\Module\script\submit_batch_maya\default.ini" % (options["platform"]))
    options["enable_maya_check"] = 0

    options["father_id"] = 0
    options["submit_mode"] = 2
    options["ignore_texture"] = 0
    options["only_scene"] = 0
    options["dependency"] = 0
    options["dont_analyze_mi"] = 0
    options["dont_analyze_ass"] = 0
    options["task_mode"] = 0
    options["seperate_account"] = 0
    options["task_level"] = ""
    options["all_proxy"] = 0

    server_config["temp_dir"] = options["temp_dir"].replace("\\", "/")
    server_config["user_id"] = options["user_id"]
    server_config["father_id"] = None
    server_config["seperate_account"] = options["seperate_account"]
    if options["father_id"]:
        if int(options["father_id"]) != 0:
            server_config["father_id"] = int(options["father_id"])

    home_id = server_config["father_id"] if server_config["father_id"] else \
        server_config["user_id"]

    if options["platform"] in ["1007"]:
        home_id = server_config["user_id"]

    home_id = int(home_id)
    if options["platform"] in ["1007"]:
        options["server_home"] = ""
    elif options["platform"] == "1099":
        options["server_home"] = "//172.31.19.49/d/inputdata"
    elif options["platform"] == "1005":
        options["server_home"] = ""
    elif options["platform"] == "1002":
        options["server_home"] = ""
    else:
        options["server_home"] = ""

    if options["platform"] in ["1007"]:
        options["user_home"] = "/%s/%s" % (home_id, options["project_symbol"])
        options["project_home"] = "/maya"
    else:
        options["user_home"] = "/%s/%s" % ((home_id/500)*500, home_id)
        options["project_home"] = ""

    server_config["client_version"] = options["client_version"]

    server_config["maya_version"] = options["maya_version"]
    server_config["project_custom"] = options["project_path"]
    server_config["project_in_maya"] = ""
    server_config["project"] = ""

    options["submit_mode"] = int(options["submit_mode"])
    server_config["submit_mode"] = options["submit_mode"]
    server_config["task_mode"] = options["task_mode"]

    return options


def get_maya_version(maya_file, default):
    if default:
        if default.lower().startswith("maya"):
            version = default.split()[1]
            print_info2("get default maya %s" % (version))
            return version
    else:
        writing_error(217, default)

    # TODO 1. we need config the maya version from the client app

    result = None
    if maya_file.endswith(".ma"):
        infos = []
        with open(maya_file, "r") as f:
            while 1:
                line = f.readline()
                if line.startswith("createNode"):
                    break
                elif line.strip() and not line.startswith("//"):
                    infos.append(line.strip())

        file_infos = [i for i in infos if i.startswith("fileInfo")]
        for i in file_infos:
            if "product" in i:
                r = re.findall(r'Maya.* (\d+\.?\d+)', i, re.I)
                if r:
                    result = int(r[0].split(".")[0])

    elif maya_file.endswith(".mb"):
        with open(maya_file, "r") as f:
            info = f.readline()

        file_infos = re.findall(r'FINF\x00+\x11?\x12?K?\r?(.+?)\x00(.+?)\x00',
                                info, re.I)
        for i in file_infos:
            if i[0] == "product":
                result = int(i[1].split()[1])

    if result:
        print_info2("get maya file version %s" % (result))
        return result
    else:
        version = default.split()[1]
        print_info2("get default maya %s" % (version))
        return version


def get_maya_batch(maya_file, maya_install, maya_version):
    # TODO 3. we need config the maya install path from the client app
    if maya_install:
        if os.path.exists(maya_install):
            return maya_install

    mayabatch = ["C:/Program Files/Autodesk/Maya%s/bin/mayabatch.exe" % \
                 (maya_version),
                 "D:/Program Files/Autodesk/Maya%s/bin/mayabatch.exe" % \
                 (maya_version),
                 "E:/Program Files/Autodesk/Maya%s/bin/mayabatch.exe" % \
                 (maya_version),
                 "F:/Program Files/Autodesk/Maya%s/bin/mayabatch.exe" % \
                 (maya_version),
                 "D:/Alias/Maya%sx64/bin/mayabatch.exe" % (maya_version)]

    mayabatch = [i for i in mayabatch if os.path.isfile(i)]

    if mayabatch:
        return mayabatch[0]


def get_user_level_cfg(level_file):
    try:
        info = eval(open(level_file, "r").read().replace("\r", "").replace("\n", ""))
        base = 50
        level = {}

        for project in info:
            for project_name in project:
                level[project_name] = {}
                for episode in project[project_name]:
                    level[project_name][str(episode)] = base
                    base -= 1

        return level
    except:
        return None


def get_level(level_file, maya_file, project_name):
    project_name = project_name.lower()
    level = get_user_level_cfg(level_file)
    if level:
        split_info = os.path.basename(maya_file).split("_")

        if len(split_info) > 2:
            episode = split_info[1]
        else:
            episode = None

        if project_name in level:
            if episode and episode in level[project_name]:
                return level[project_name][episode]
            else:
                return level[project_name]["default"]
        else:
            return level["default"]["default"]
    else:
        return 1


def analyze_maya(options, using_multi_task=0):
    print_info2("start maya ok.")
    print_info2("open maya file: " + options["maya_file"])
    if int(options["father_id"]) in  [1849749]:
        if 'scenes' in options["maya_file"]:
            options["project_path"] = options["maya_file"].split("scenes")[0]
    
    if options["project_path"]:
        if os.path.exists(options["project_path"]):
            workspacemel = os.path.join(options["project_path"],
                                        "workspace.mel")
            if not os.path.exists(workspacemel):
                try:
                    with open(workspacemel, "w"):
                        ''
                except:
                    pass
                    # raise Exception("Can't create empty workspace.mel file "
                    #                 "in project folder")

            if os.path.exists(workspacemel):
                pm.mel.eval('setProject "%s"' % (options["project_path"]))

    # ignore some open maya errors.
    if os.path.exists(options["maya_file"]) and os.path.isfile(options["maya_file"]):
        try:
            if options["user_id"] == 1873017 or options["user_id"] == 1880735  :
                pm.openFile(options["maya_file"], force=1, ignoreVersion=1, prompt=0, loadReferenceDepth="all")
            else:
                pm.openFile(options["maya_file"], force=1, ignoreVersion=1, prompt=0)
        except:
            pass
    else:
        raise Exception("Dont Found the maya files error.")

    

    print_info2("open maya file ok.")

    render_settings = pm.PyNode("defaultRenderGlobals")
    start = int(render_settings.startFrame.get())
    end = int(render_settings.endFrame.get())
    if not int(start) < int(pm.getCurrentTime()) < int(end):
        pm.setCurrentTime(int(start))

    if int(options["user_id"]) == 1818936:
        pre_mel = os.path.splitext(options["maya_file"])[0] + ".mel"
        pm.mel.source(pre_mel.replace("\\", "/"))

    server_config["temp_dir"] = options["temp_dir"].replace("\\", "/")

    server_config["user_id"] = options["user_id"]
    server_config["father_id"] = None
    server_config["seperate_account"] = options["seperate_account"]
    if options["father_id"]:
        if int(options["father_id"]) != 0:
            server_config["father_id"] = int(options["father_id"])

    home_id = server_config["father_id"] if server_config["father_id"] else \
        server_config["user_id"]

    if options["platform"] in ["1007"]:
        home_id = server_config["user_id"]

    if options["platform"] in ["1007"]:
        options["server_home"] = ""
    elif options["platform"] == "1099":
        options["server_home"] = "//172.31.19.49/d/inputdata"
    elif options["platform"] == "1005":
        options["server_home"] = ""
    elif options["platform"] == "1002":
        options["server_home"] = ""
    else:
        options["server_home"] = ""

    if options["platform"] in ["1007"]:
        options["user_home"] = "/%s/%s" % (home_id, options["project_symbol"])
        options["project_home"] = "/maya"
    else:
        options["user_home"] = "/%s/%s" % ((home_id/500)*500,
        home_id)
        options["project_home"] = ""

    server_config["client_version"] = options["client_version"]

    server_config["maya_version"] = options["maya_version"]
    server_config["project_custom"] = options["project_path"]
    server_config["project_in_maya"] = pm.workspace.path.encode("gb18030")
    # server_config["project_in_maya"] = str(pm.workspace.path)
    if server_config["project_in_maya"].endswith(":"):
        #maya2015 change c:/ to c:, we nedd add /
        server_config["project_in_maya"] += "/"

    if server_config["project_custom"]:
        server_config["project"] = "/share_project"
    else:
        server_config["project"] = "".join(["/uploads/",
            server_config["mac"], "/project"])

#    pprint.pprint(options)
#    pprint.pprint(server_config)

    options["submit_mode"] = int(options["submit_mode"])
    server_config["submit_mode"] = options["submit_mode"]

    print_info2("start analyze maya file.")
    task = MayaTask(options)

    server_config["task_mode"] = options["task_mode"]
    if options["task_mode"] == 1:
        task.get_layer_settings()
        task.set_project_info(options["project_id"], options["project_symbol"])
        task.set_task_level(options["task_level"])
        task["common"]["chunk_size"] = 99999
        task["common"]["name"] = "Miarmycache " + os.path.basename(task["common"]["cgFile"])
        task["common"]["no_output"] = 1
        task.submit()

        task["common"]["parent_id"] = task["common"]["taskId"]
        task["common"]["chunk_size"] = 1
        task["common"]["name"] = "Render " + os.path.basename(task["common"]["cgFile"])
        task["common"]["no_output"] = 0
        task.submit(no_upload=1)
        print task

    elif home_id in [] and server_config["submit_mode"] == 1:
        render_layers = [i.name()
                         for i in pm.PyNode("renderLayerManager").outputs()
                         if i.type() == "renderLayer"
                         if i.renderable.get()]
        for i in render_layers:
            print "get layer setting "
            task.get_layer_settings(i)
            task.set_project_info(options["project_id"], options["project_symbol"])
            task.set_task_level(options["task_level"])
            task.submit()
    else:
        # task.get_task_id()
        task.get_layer_settings()
        task.set_project_info(options["project_id"], options["project_symbol"])
        task.set_task_level(options["task_level"])
        task["common"]["name"] = ""
        task.submit()

    print "rayvision: get maya info ok."
    pm.runtime.Quit()

def auto_load_plu(maya_v, plug_name):

    if int(maya_v[:4]) <= 2015:
        maya_v = "%s-x64" % (maya_v)
    print maya_v
    curUserPath = os.environ.get('userprofile')
    pluginPrefsFile = r"%s/Documents/maya/%s/prefs/pluginPrefs.mel" % (curUserPath, maya_v)
    pluginPrefsFile = pluginPrefsFile.replace('\\', '/')
    hasPlugPrefs = False
    plug_load = (r'evalDeferred("autoLoadPlugin(\"\", \"%s\", \"%s\")");' + '\n') % (plug_name, plug_name)
    if os.path.exists(pluginPrefsFile):
        print pluginPrefsFile
        mode = "a+"
        with open(pluginPrefsFile, mode) as f:
            lines = f.readlines()
            for line in lines:
                if plug_load.strip() == line.strip():
                    print ("auto load  %s " % (plug_name))
                    hasPlugPrefs = True
                    break
            if not hasPlugPrefs:
                print ("write %s for auto load" % (plug_name))
                f.write(plug_load)


    else:
        file_dir = os.path.split(pluginPrefsFile)[0]
        if os.path.exists(file_dir) == 0:
            os.makedirs(file_dir)
        print ("makedir %s " % (file_dir))
        mode = "w"
        with open(pluginPrefsFile, mode) as f:
            print ("write %s for auto load" % (plug_name))
            f.write(plug_load)
def get_munu_time():
    try:
        file_path = os.path.realpath(__file__)
        print "the munu.pyd time"
        print time.ctime(os.stat(file_path).st_mtime)
    except:
        pass
    
def start_maya(options):
    get_munu_time()
    # type: (object) -> object
    options.temp_dir = options.temp_dir.replace("\\", "/")
    server_config["temp_dir"] = options.temp_dir

    if int(options.user_id) in [961404]:
        scene_name = os.path.splitext(os.path.basename(options.cg_file_name))[0]
        if not re.findall("^[A-Z][^-]+[0-9]$", scene_name):
            writing_error(222)
            print_info2("", 101)

    error_list = []
    munu_path = os.path.dirname(sys.argv[0].replace("\\", "/"))
    maya_file = options.maya_list.strip()

    options.maya_list = options.maya_list.replace("\\", "/")
    if not options.maya_file:
        options.maya_file = options.maya_list

    #for chinese character
    options.maya_file = repr(options.maya_file)[1:-1]

    if options.plugin_file:
        options.plugin_file = options.plugin_file.replace("\\", "/")

    options.maya_version = get_maya_version(maya_file, options.maya_version)

    options.user_id = int(options.user_id)

    mayabatch = ""
    if options.maya_install:
        if os.path.exists(options.maya_install):
            mayabatch = options.maya_install

    if options.maya_version < 2011:
        print_info2("Maya %s doesn't support" % (options.maya_version), 101)
    if options.maya_version > 2016:
        os.environ['MAYA_VP2_DEVICE_OVERRIDE'] = 'VirtualDeviceDx11'
        os.environ['MAYA_OPENCL_IGNORE_DRIVER_VERSION'] = '1'
        
    if int(options.user_id) in [964309, 1819310, 1821185, 1860665] or int(options.father_id) in [964309, 1819310, 1821185, 1860665]:
        mayabatch = r"%MAYAROOT%\bin\mayabatch.exe"
    if int(options.user_id) in [1878628]:
        mayabatch = r"C:\\Program Files\\Autodesk\\Maya2017\\bin\\mayabatch.exe"
    if int(options.user_id) in [1880735]:
        mayabatch = r"C:\\Program Files\\Autodesk\\Maya2016.5\\bin\\mayabatch.exe"
    if not mayabatch:
        if not options.maya_install:
            options.maya_install = "None"
        writing_error(213, options.maya_install)
        print_info2("", 101)

    options2 = vars(options)
    str_options = re.sub(r"\\", r"\\\\", repr(options2))
    os.environ["MAYA_UI_LANGUAGE"] = "en_US"
    cmd = "\"%s\" -command \"python \\\"options=%s;" \
          "import sys;sys.path.insert(0, '%s');import munu;" \
          "munu.analyze_maya(options)\\\"" % \
          (mayabatch, str_options, munu_path)

    shell = 0
    if int(options.user_id) == 1811213 or int(options.father_id) == 1811213:
        cmd = "call D:\\lg\\LG_Nuke\\launch_env.bat && " + cmd
        shell = 1

    if int(options.user_id) == 964309 or int(options.father_id) == 964309:
        cmd_bat = "@echo off"
        cmd_bat += "\r\n"
        cmd_bat += "call \"%s\"" % (r"\\storage1.of3d.com\centralizedTools\launcher\jueji_movie_02\maya\config\setenv_jueji_movie_02_2016.bat")
        cmd_bat += "\r\n"
        cmd_bat += cmd
        bat_tmp = os.path.join(os.environ["tmp"], "rayvision.bat")
        with open(bat_tmp, "w") as f:
            f.write(cmd_bat)
        cmd = bat_tmp

    if int(options.user_id) == 1878628 or int(options.father_id) == 1878628:
        pprint.pprint("of3d_3Below")
        cmd_bat = "@echo off"
        cmd_bat += "\r\n"
        cmd_bat += "call \"%s\"" % (r"\\storage1.of3d.com\centralizedTools\launcher\dreamworks_3below_cg\maya\config\setenv_dreamworks_3below_cg_2017.bat")
        cmd_bat += "\r\n"
        cmd_bat += cmd
        bat_tmp = os.path.join(os.environ["tmp"], "rayvision.bat")
        with open(bat_tmp, "w") as f:
            f.write(cmd_bat)
        cmd = bat_tmp
        
    if int(options.user_id) == 1860665 or int(options.father_id) == 1860665:
        cmd_bat = "@echo off"
        cmd_bat += "\r\n"
        cmd_bat += "call \"%s\"" % (r"\\storage1.of3d.com\centralizedTools\launcher\monsterhunt_02_movie\maya\config\setenv_monsterhunt_02_movie_2016.bat")
        cmd_bat += "\r\n"
        cmd_bat += cmd
        bat_tmp = os.path.join(os.environ["tmp"], "rayvision.bat")
        with open(bat_tmp, "w") as f:
            f.write(cmd_bat)
        cmd = bat_tmp
    if int(options.user_id) == 1819310 or int(options.father_id) == 1819310:
        cmd_bat = "@echo off"
        cmd_bat += "\r\n"
        cmd_bat += "call \"%s\"" % (r"\\storage1.of3d.com\centralizedTools\launcher\env\setenv_OF_DDG_CG_2015.bat")
        cmd_bat += "\r\n"
        cmd_bat += cmd
        bat_tmp = os.path.join(os.environ["tmp"], "rayvision.bat")
        with open(bat_tmp, "w") as f:
            f.write(cmd_bat)
        cmd = bat_tmp
    if int(options.user_id) == 1821185 or int(options.father_id) == 1821185:
        cmd_bat = "@echo off"
        cmd_bat += "\r\n"
        cmd_bat += "call \"%s\"" % (r"\\storage1.of3d.com\centralizedTools\launcher\render_Dreamworks_TrollHunters_CG_mtoa1.2.2.0.bat")
        cmd_bat += "\r\n"
        cmd_bat += cmd
        bat_tmp = os.path.join(os.environ["tmp"], "rayvision.bat")
        with open(bat_tmp, "w") as f:
            f.write(cmd_bat)
        cmd = bat_tmp
    if int(options.user_id) == 1818936 or int(options.father_id) == 1818936:
        RvOs.which("eco")
        env_root = r"\\10.50.1.22\td\clientFiles\1818936\tools_new"
        env_bat = os.path.join(env_root, "env.bat")

        cmd = "mayabatch.exe -command \\\"python \\\\\\\"options=%s;" \
              "import sys;sys.path.insert(0, '%s');import munu;" \
              "munu.analyze_maya(options)\\\\\\\"\\\"" % \
              (re.findall(r'{.+}', repr(options), re.I)[0], munu_path)

        # cmd = "\"%s\" && eco -t rayvision_maya -r \"%s\"" % (env_bat, cmd)
        cmd = "eco -t rayvision_maya -r \"%s\"" % (cmd)
        shell = 1
        # print cmd

        # cmd_bat = "@echo off"
        # cmd_bat += "\r\n"
        # cmd_bat += "call \"%s\"" % (env_bat)
        # cmd_bat += "\r\n"
        # cmd_bat += "eco -t rayvision_maya -r \"%s\"" % (cmd)
        # bat_tmp = os.path.join(os.environ["tmp"], "rayvision.bat")
        # with open(bat_tmp, "w") as f:
        #     f.write(cmd_bat)
        # cmd = bat_tmp
    if int(options.user_id) in [1812148, 1830380]:
        os.environ["CG_PROJECT"] = options.project_symbol
        if os.environ["CG_PROJECT"] == "DRGN":
            os.environ["CG_PROJECT"] = "DRAGON"
        if options.maya_version == "2017":
            os.environ["CG_PROJECT"] = "3BL"
        os.environ["MAYA_ENV_ROOT"] = "C:/CGCG/projects/%s/maya/%s/x64" % (os.environ["CG_PROJECT"], options.maya_version)
        os.environ["MAYA_PLUG_IN_PATH"] = "%s/plug-ins" % (os.environ["MAYA_ENV_ROOT"])
        os.environ["MAYA_SCRIPT_PATH"] = "%s/scripts" % (os.environ["MAYA_ENV_ROOT"])
        os.environ["PYTHONPATH"] = "%s/scripts" % (os.environ["MAYA_ENV_ROOT"])
        os.environ["MAYA_MODULE_PATH"] = "%s/modules" % (os.environ["MAYA_ENV_ROOT"])
        os.environ["MI_CUSTOM_SHADER_PATH"] = "%s/mentalray" % (os.environ["MAYA_ENV_ROOT"])
        os.environ["MI_LIBRARY_PATH"] = "%s/mentalray" % (os.environ["MAYA_ENV_ROOT"])
    
    if int(options.user_id) in [1860293]:
        os.environ["CG_PROJECT"] = "MH"
        os.environ["MAYA_ENV_ROOT"] = "C:/CGCG/projects/%s/maya/%s/x64" % (os.environ["CG_PROJECT"], options.maya_version)
        os.environ["MAYA_PLUG_IN_PATH"] = "%s/plug-ins" % (os.environ["MAYA_ENV_ROOT"])
        os.environ["MAYA_SCRIPT_PATH"] = "%s/scripts" % (os.environ["MAYA_ENV_ROOT"])
        os.environ["PYTHONPATH"] = "%s/scripts" % (os.environ["MAYA_ENV_ROOT"])
        os.environ["MAYA_MODULE_PATH"] = "%s/modules" % (os.environ["MAYA_ENV_ROOT"])
        
    if int(options.user_id) in [1871175]:
        os.environ["CG_PROJECT"] = "3BL"
        os.environ["MAYA_ENV_ROOT"] = "C:/CGCG/projects/%s/maya/%s/x64" % (os.environ["CG_PROJECT"], options.maya_version)
        os.environ["MAYA_PLUG_IN_PATH"] = "%s/plug-ins" % (os.environ["MAYA_ENV_ROOT"])
        os.environ["MAYA_SCRIPT_PATH"] = "%s/scripts" % (os.environ["MAYA_ENV_ROOT"])
        os.environ["PYTHONPATH"] = "%s/scripts" % (os.environ["MAYA_ENV_ROOT"])
        os.environ["MAYA_MODULE_PATH"] = "%s/modules" % (os.environ["MAYA_ENV_ROOT"])
    
    if int(options.user_id) in [1873017,1880735]:
        os.environ["CG_PROJECT"] = "CGBB"
        os.environ["CG_MAYA_DIR"] = "c:/CGCG/projects/BB_Rayvision/maya/2016.5/x64"
        os.environ["MAYA_SCRIPT_PATH"] = "%s/scripts" % (os.environ["CG_MAYA_DIR"])
        os.environ["MAYA_PLUG_IN_PATH"] = "%s/plug-ins" % (os.environ["CG_MAYA_DIR"])
        os.environ["MAYA_MODULE_PATH"] = "%s/modules" % (os.environ["CG_MAYA_DIR"])
        os.environ["XBMLANGPATH"] = "%s/icons" % (os.environ["CG_MAYA_DIR"])
        os.environ["PYTHONPATH"] = "%s/scripts" % (os.environ["CG_MAYA_DIR"])
        os.environ["STUDIOROOT"] ="Y:/BB/BB_sync"
        os.environ["PIPEROOT"] = "%s/huhuPipe" % (os.environ["STUDIOROOT"])
        os.environ["PROJECTROOT"] = "%s/projects" % (os.environ["STUDIOROOT"])
        os.environ["PROJECT_CODE"] = "BOFB_FILM"
        os.environ["MAYA_ENABLE_LEGACY_HYPERSHADE"] = "1"
    if int(options.user_id) in [1873149]:
        print "holyanimation"
        # os.environ["upServerPath"] = "//nas/data/PipePrj"
        # os.environ["upLocalCachePath"] = "//nas/data/PipePrj"
        
    
    if int(options.user_id) in [1844854,119768]:
        auto_load_plu(options.maya_version,"AbcImport")

    elif int(options.user_id) == 1813119:
        # launcher = r"\\px\app_config\release\maya\modulesLauncher\versions\v200\maya_launcher.py"
        # profile = r"\\px\app_config\release\settings\projects\icefantasy_icf-3595\maya\profiles\icf_maya2016-yeti_oldpipe"
        launcher = os.environ["px_launcher"]
        profile = os.environ["px_profile"]
        cmd = "python \"%s\" -xp \"%s\" %s" % (launcher, profile, cmd)
        shell = 1

    print "cmd info >>>> %s" % cmd

    print_info2("start Maya %s" % (options.maya_version))

#    print "INFO: get info from " + maya_file
#    print "INFO: " + cmd

    maya_exception = 1
    maya_warning = []

    re_task_id = re.compile(r'<cmd><code>777</code><des>(\d+)</des></cmd>',
                            re.I)
    task_id = None

    for line in RvOs.run_command(cmd, ignore_error=1, shell=shell):
        line_str = line.strip()
        if line_str:
            if options.is_debug:
                print line_str

            if "<cmd>" in line_str:
                print line_str
                sys.stdout.flush()
                time.sleep(0.1)
                r = re_task_id.findall(line_str)
                if r:
                    task_id = r[0]

            if "Error" in line_str:
                error_list.append(line_str)

            if "rayvision: get maya info ok." in line_str:
                maya_exception = 0
                RvOs.kill_children()
            elif "Reference file not found" in line_str:
                if not options.only_scene:
                    writing_error(101, line_str)
                    print_info2(line_str, 101)
            elif "Found missing texure files error" in line_str:
                if not options.ignore_texture:
                    print_info2(line_str, 201)

#            elif "Maya binary file parse error" in line_str:
#                print_info2(line_str, 102)
#            elif "Error: RuntimeError" in line_str:
#                if not options.only_scene:
#                    print_info2(line_str, 103)
#            elif "Error reading file" in line_str:
#                print_info2(line_str, 104)

    if int(options.user_id) == 964309 or int(options.father_id) == 964309:
        try:
            os.remove(bat_tmp)
        except:
            pass
        
        

    if maya_exception:
        if error_list:
            if "Found missing texure files error" in error_list[-1]:
                print_info2(error_list[-1], 201)
            else:
                print_info2(error_list[-1], 101)
        else:
            print_info2("Unknown error", 101)

    print "\n"

    if maya_warning:
        print_info2("Success", 201)
    else:
        writing_error(0)


def start_arnold(options):
    options2 = {}
    for i in options.__dict__:
        options2[i] = options.__dict__[i]

    options = options2
    options["ass_path"] = options["ass_path"].replace("\\", "/")

#    pprint.pprint(options)

    sequences, others = FileSequence.find(options["ass_path"], "ass")
    if sequences:
        for i in sequences:
            analyze_arnold(options, i)
    else:
        print_info2("Can't find the ass files in the drag directory.", 101)

    print "\n"
    print_info2("Success", 0)


def start_txt(options):
    options2 = {}
    for i in options.__dict__:
        options2[i] = options.__dict__[i]

    options = options2

    today = "%04d_%02d_%02d" % (time.localtime()[:3])
    yesterday = "%04d_%02d_%02d" % time.localtime(time.time() - 3600*24)[:3]
    the_day_before_yesterday = "%04d_%02d_%02d" % time.localtime(time.time() - 3600*48)[:3]

    txt_files = []
    for day in [the_day_before_yesterday, yesterday, today]:
        day_path = os.path.join(options["txt_path"], day, "_txtIndex")
        if os.path.exists(day_path):
            for i in os.listdir(day_path):
                if i.lower().endswith(".txt"):
                    if i != "error.txt":
                        txt_files.append(os.path.join(day_path, i))

    if options["enable_multi_task"]:
        for i in txt_files:
            try:
                analyze_txt(options, i)
            except:
                save_error_txt(os.path.join(day_path, "error.txt"), i)
    else:
        pt_path = sys.argv[0].lower().split("module")[0].rstrip("\\").rstrip("/")
        options["platform"] = os.path.basename(pt_path)
        db_path = r'%s\Profiles\users\%s\%s\tasklist.dat' % (pt_path,
            options["user_name"], os.environ["username"])
        db = SqliteDB(db_path)
        upload_history = db.get_table_list("upload_history")
        db.close()

        if upload_history:
            print "This computer is uploading, so skip."
        else:
            for i in txt_files:
                try:
                    if analyze_txt(options, i):
                        break
                except:
                    save_error_txt(os.path.join(day_path, "error.txt"), i)


def save_error_txt(save_path, txt):
    if os.path.exists(save_path):
        write_mode = "a"
    else:
        write_mode = "w"
    with open(save_path, write_mode) as f:
        f.write(txt)
        f.write("\n")


def analyze_txt(options, txt):
    print "found txt file: " + txt
    ok_mark = txt + ".ok"
    start_mark = txt + ".start"

    if os.path.exists(ok_mark):
        print "This txt file had been submited, so skip."
    elif os.path.exists(start_mark):
        print "This txt file is submiting, so skip."
    else:
        with open(start_mark, "w"):
            ''

        print "Start to analyze this txt file."

        server_config["user_id"] = options["user_id"]
        server_config["father_id"] = None
        if options["father_id"]:
            if int(options["father_id"]) != 0:
                server_config["father_id"] = int(options["father_id"])

        home_id = server_config["father_id"] if server_config["father_id"] else \
            server_config["user_id"]

        home_id = int(home_id)

#        if home_id == 961900:
#            options["server_home"] = "//10.50.24.11"
#
#        options["user_home"] = ""
#        options["project_home"] = ""

        if options["platform"] == "1002":
            options["server_home"] = "//10.60.100.102/d/inputdata5"
        else:
            options["server_home"] = "//10.50.24.11/d/inputdata5"

        if home_id == 963697:
            home_id = 961900

        options["user_home"] = "/%s/%s" % ((home_id/500)*500, home_id)

        options["project_home"] = "/hosts"

#        pprint.pprint(options)

        server_config["client_version"] = options["client_version"]

        if options["cg_software"] == "houdini":
            task = HoudiniTxtTask(options, txt)
        else:
            task = TxtTask(options, txt)

        task.set_project_info(options["project_id"], options["project_symbol"])
        task.set_task_level(options["task_level"])
        task.submit()

        with open("%s.%s" % (ok_mark,
            "%04d_%02d_%02d_%02d_%02d_%02d" % (time.localtime()[:6])), "w"):
            ''

        with open(ok_mark, "w"):
            ''

        return 1


def analyze_arnold(options, ass):
    # print_info2("start maya ok.")
    # print_info2("open maya file: " + options["maya_file"])
    #
    # pm.openFile(options["maya_file"], force=1, ignoreVersion=1, prompt=0)
    #
    # print_info2("open maya file ok.")

    server_config["user_id"] = options["user_id"]
    server_config["father_id"] = None
    if options["father_id"]:
        if int(options["father_id"]) != 0:
            server_config["father_id"] = int(options["father_id"])

    home_id = server_config["father_id"] if server_config["father_id"] else \
        server_config["user_id"]

    home_id = int(home_id)

    options["server_home"] = "//10.50.24.10/d/inputdata5"
    if home_id in [961900, 961577, 961580, 961581, 962152, 120151]:
        options["server_home"] = "//10.50.24.11/d/inputdata5"

    options["user_home"] = "/%s/%s" % ((home_id/500)*500, home_id)

    options["project_home"] = "/" + options["project_symbol"] + "/arnold"

#    pprint.pprint(options)

    server_config["client_version"] = options["client_version"]

    task = ArnoldTask(options, ass)
    task.set_project_info(options["project_id"], options["project_symbol"])
    task.set_task_level(options["task_level"])
    task.submit()


def print_info(info, exit_code=666, sleep=0.1, task_id=None):
    if exit_code in [666, 777]:
        print "<cmd><code>%s</code><des>%s</des></cmd>" % (exit_code, info)
#        sys.stdout.write("<cmd><code>666</code><des>%s</des></cmd>" % (info))
#        sys.stdout.write("\n")
        sys.stdout.flush()
        time.sleep(sleep)
    else:
        if exit_code != 0:
            if "mayabatch.exe" in sys.executable.lower():
#                sys.stdout.flush()
                print "<cmd><code>%s</code><des>%s</des></cmd>" % (exit_code, info)
#                sys.stdout.write("<cmd><code>%s</code><des>%s</des></cmd>" % \
#                    (exit_code, info))
#                sys.stdout.write("\n")
                sys.stdout.flush()
                time.sleep(sleep)
                pm.runtime.Quit()
                return 0
            else:
                RvOs.kill_children()

        if exit_code == 333:
            print "<cmd><code>%s</code><tid>%s</tid><des>%s</des></cmd>" % (exit_code, task_id, info)
        else:
            print "<cmd><code>%s</code><des>%s</des></cmd>" % (exit_code, info)
#        sys.stdout.write("<cmd><code>%s</code><des>%s</des></cmd>" % \
#            (exit_code, info))
#        sys.stdout.write("\n")
        sys.stdout.flush()
        time.sleep(sleep)
        exit(exit_code)


def print_info2(info, exit_code=200, sleep=0.2, task_id=None):
    if exit_code in [100, 200, 300]:
        if exit_code == 300:
            print "<cmd><code>%s</code><des>%s</des><tid>%s</tid></cmd>" % \
                        (exit_code, info, task_id)
        else:
            print "<cmd><code>%s</code><des>%s</des></cmd>" % (exit_code, info)

        sys.stdout.flush()
        time.sleep(sleep)
    else:
        if exit_code == 0:
            print "<cmd><code>100</code><des>%s</des></cmd>" % (info)
        else:
            if "mayabatch.exe" in sys.executable.lower():
                sys.stdout.flush()
                time.sleep(sleep)
                pm.runtime.Quit()
                return 0
            else:
                RvOs.kill_children()

        sys.stdout.flush()
        time.sleep(sleep)
        exit(exit_code)


def writing_error(error_code, info=""):
    json_file = os.path.join(server_config["temp_dir"], "result.json")
    error_code = str(error_code)
    error_json = ErrorJson(json_file)

    if error_code == "0":
        if error_json:
            return 0

    if type(info) == str:
        r = re.findall(r"Reference file not found.+?: +(.+)", info, re.I)
        if r:
            error_json["212"] = [r[0]]
        else:
            error_json[error_code] = [info]
    else:
        error_json[error_code] = info

    error_json.save()


def to_unicode(string):
    locale_encoding = locale.getpreferredencoding()
    if locale_encoding == "cp936":
        locale_encoding = "gb18030"

    if type(string) == unicode:
        return string
    elif type(string) == str:
        try:
            return string.decode("utf-8")
        except:
            return string.decode(locale_encoding)
    elif type(string) == pm.Path:
        return unicode(string)


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
    def get_encode(encode_str):
        if isinstance(encode_str, unicode):
            return "unicode"
        else:
            for code in ["utf-8",sys.getfilesystemencoding(), "gb18030","ascii","gbk","gb2312"]:
                try:
                    encode_str.decode(code)
                    return code
                except:
                    pass

    @staticmethod
    def str_to_unicode(encode_str):
        if isinstance(encode_str, unicode):
            return encode_str
        else:
            code = RvOs.get_encode(encode_str)
            return encode_str.decode(code)

    @staticmethod
    def get_windows_mapping():
        if RvOs.is_win:
            networks = {}
            locals = []
            all = []

            net_use = dict([re.findall(r'.+ ([a-z]:) +(.+)', i.strip(), re.I)[0]
                            for i in RvOs.run_command('net use')
                            if i.strip() if re.findall(r'.+ ([a-z]:) +(.+)',
                                                       i.strip(), re.I)])
            for i in net_use:
                net_use[i] = net_use[i].replace("Microsoft Windows Network",
                                                "").strip()

            for i in RvOs.run_command('wmic logicaldisk get deviceid,drivetype,providername'):
                if i.strip():
                    # a = re.findall(r'([a-z]:) +(\d) +(.+)?', i.strip(), re.I)
                    # print a
                    info = i.split()
                    if info[1] == "4":
                        if len(info) == 3:
                            if re.findall(r'^[\w _\-.:()\\/$]+$', info[2], re.I):
                                networks[info[0]] = info[2].replace("\\", "/")
                            else:
                                networks[info[0]] = None
                            all.append(info[0])
                        else:
                            if info[0] in net_use:
                                if os.path.exists(net_use[info[0]]):
                                    if re.findall(r'^[\w _\-.:()\\/$]+$', net_use[info[0]], re.I):
                                        networks[info[0]] = net_use[info[0]].replace("\\", "/")
                                    else:
                                        networks[info[0]] = None
                                    all.append(info[0])
                                else:
                                    # Don't know why the drive is not exists when using python to check.
                                    # Is this a network issue?
                                    # Can not reproduce this issue manually.
                                    print "%s is not exists" % (info[0])
                                    networks[info[0]] = None
                                    all.append(info[0])
                            else:
                                networks[info[0]] = None
                                all.append(info[0])

                    elif info[1] in ["3", "2"]:
                        if info[0] in server_config["forbidden_drives"]:
                            locals.append(info[0])
                        else:
                            networks[info[0]] = None
                        all.append(info[0])

        return (locals, networks, all)

    @staticmethod
    def run_command(cmd, ignore_error=None, shell=0):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = _subprocess.SW_HIDE
        
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
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
                    print "exit return code is: " + str(return_code)
                    raise Exception(cmd + " was crashed for some reason.")
            line = p.stdout.readline()
            if not line:
                break
            yield line

    @staticmethod
    def get_process_list(name):
        process_list = []
        for i in RvOs.run_command("wmic process where Caption=\"%s\" get processid" % (name)):
            if i.strip() and i.strip() not in ["ProcessId", "No Instance(s) Available."]:
                process_list.append(int(i.strip()))

        return process_list

    @staticmethod
    def get_desktop_app():
        app_names = ["qrenderbus.exe"]
        for i in app_names:
            process = RvOs.get_process_path(i)
            if process:
                return process[0]

    @staticmethod
    def get_rendercmd_exe():
        return os.path.join(RvOs.get_app_config()["installdir"], "rendercmd.exe")

    @staticmethod
    def get_app_config():
        env_ini = os.path.join(os.environ["appdata"], r"RenderBus\local\env.ini")

        config = open(env_ini).readlines()
        config = dict([[j.strip() for j in i.split("=")] for i in config if "=" in i])
        return config

    @staticmethod
    def get_projects():
        cmd = RvOs.get_rendercmd_exe()
        for i in RvOs.run_command("\"%s\" -getproject" % (cmd)):
            return eval(i)

    @staticmethod
    def get_process_path(name):
        process_list = []
        for i in RvOs.run_command("wmic process where name=\"%s\" get ExecutablePath" % (name)):
            if i.strip() and i.strip() not in ["ExecutablePath", "No Instance(s) Available."]:
                process_list.append(i.strip())

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
        for i in RvOs.get_all_child().values():
            # os.kill is Available from python2.7, need another method.
            # os.kill(i, 9)
            if RvOs.is_win:
                os.system("taskkill /f /t /pid %s" % (i))
                # task_kill_exe=os.path.join(RvOs.get_app_config()["installdir"], "taskkill.exe")
                # subprocess.Popen(r'"'+task_kill_exe+'" /f /t /pid %s' % (i))

    @staticmethod
    def timeout_command(command, timeout):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = _subprocess.SW_HIDE

        start = time.time()
        process = subprocess.Popen(command, stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,startupinfo = startupinfo,shell=False)
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

    @staticmethod
    def which(exe):
        if RvOs.is_win:
            cmd = "where " + exe
            print "execute: " + cmd
            for i in RvOs.run_command(cmd):
                print i


class Zip7(object):

    def __init__(self, exe):
        self.exe = exe

    def compress(self, src):
        zip_file = os.path.splitext(src)[0] + ".rayvision"

        if os.path.exists(zip_file):
            try:
                if zip_file.endswith(".rayvision"):
                    os.remove(zip_file)
            except:
                raise Exception("Can't delete %s before generate new "
                                "compressed file, please check." % (zip_file))
#        if self.is_same(zip_file, src):
#            print_info2("compressed file %s exists, skip compress" % (zip_file))
#            result = 1
#        else:

        print_info2("compressing %s to %s" % (src, zip_file))

        cmd = "\"%s\" a \"%s\" \"%s\" -mx3 -ssw" % (self.exe,
            zip_file, src)

        result = 0
        for line in RvOs.run_command(cmd):
            if line.strip() == "Everything is Ok":
                result = 1

        print_info2("compress finished.")

        if result:
            return zip_file
        else:
            return src

    def decompress(self, zip_file):
        zip_info = self.get_zip_info(zip_file)

        out = os.path.dirname(zip_file)
        src = os.path.join(out, zip_info["Path"])

        if self.is_same(zip_file, src):
            print "%s is already exists, skip decopress" % (src)
            return src
        else:
            print "decopress %s from %s" % (src, zip_file)
            cmd = "\"%s\" e \"%s\" -o\"%s\" -y" % (self.exe, zip_file, out)
            result = 0
            for line in RvOs.run_command(cmd):
                if line.strip() == "Everything is Ok":
                    result = 1

            if result:
                return src

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


class RvPathTxt(dict, RvOs):

    re_variable = re.compile(r'^//.+?(/.+)', re.I)

    def __init__(self, path, exists=0):
        dict.__init__(self)
        RvOs.__init__(self)
        self["source"] = path.replace("\\", "/")
        self["client"] = self["source"]
        self["server"] = "/uploads/error"
        self["mappings"] = {}
        self["variables"] = {}
        self["exists"] = exists

        r = self.re_variable.findall(self["client"])
        if r:
            self["server"] = r[0]

        if not self["exists"]:
            if self.is_exists():
                self["exists"] = 1

        if self.is_win:
            #Must encode to gb18030 to save the path in cfg file on Windows.
            if isinstance(self["client"], unicode):
                self["client"] = self["client"].encode("utf-8")

            if isinstance(self["server"], unicode):
                self["server"] = self["server"].encode("utf-8")

    @property
    def server_long_path(self):
        path = "".join([self.options["server_home"],
            self.options["user_home"], self.options["project_home"],
            self["server"]])

        if self.is_win:
            if isinstance(path, unicode):
                path.encode("utf-8")
        return path

    def is_exists(self):
        return os.path.exists(self["client"])


class RvPath(dict, RvOs):
    # TODO 2. we need config the maya project path from the client app
    locals, networks, all = RvOs.get_windows_mapping()

    for key in networks.keys():
        if networks[key]:
            networks[networks[key]] = key

    # assume the drive name not used in system is spare, so I can use.
    server_config["used_drives"] = all

    server_config["spare_drives"] = [i+":" for i in server_config["spare_drives"]
                                     if i not in [j.rstrip(":") for j in all]]

    re_variable = re.compile(r'^\${?(\w+)}?', re.I)

    def __init__(self, path, exists=0, in_ass=0):
        dict.__init__(self)
        RvOs.__init__(self)
        self["source"] = path.replace("\\", "/")
        self["client"] = self["source"]
        self["server"] = "/uploads/error"
        self["mappings"] = {}
        self["mounts"] = {}
        self["variables"] = {}
        self["exists"] = exists

        if not self["exists"]:
            if self.is_exists():
                self["exists"] = 1

        if in_ass:
            if server_config["project_custom"]:
                server_config["project_in_ass"] = server_config["project_custom"] + "/sourceimages"
            elif server_config["project_in_maya"]:
                server_config["project_in_ass"] = server_config["project_in_maya"] + "/sourceimages"
        else:
            server_config["project_in_ass"] = None

        self.get_server_project()

        if self["exists"]:
            if not server_config["project_in_network"] and \
                re.findall(r"^%s" % (server_config["project_in_maya"]), self["client"], re.I):
                self.fix_project_path()
#            self.fix_prefound_path()
            self.fix_variable_path()
            self.fix_local_path()
            self.fix_network_path()
            self.fix_unc_path()
        else:
            self.fix_variable_path()
            self.fix_project_path()

        #TODO this is some specific codes for ktcartoon
        if "/lfx_s_kuaichandian/" in self["source"].lower():
            self["server"] = self["server"].lower().replace("/lfx_s_kuaicandian/",
                "/lfx_s_kuaichandian/")

        self["server"] = self["server"].replace(":", "")
        if self["server"] == "/uploads/error":
            self["server"] = "/uploads/" + self["client"].lstrip("/")
        else:
            if not self["server"].startswith("/"):
                self["server"] = "/" + self["server"]

        if self.is_win:
            #Must encode to gb18030 to save the path in cfg file on Windows.
            if isinstance(self["client"], unicode):
                self["client"] = self["client"]
            
            if isinstance(self["server"], unicode):
                self["server"] = self["server"]
        
        self.update_server_config()

    def __eq__(self, other):
        return self["client"] == other["client"]

    def __hash__(self):
        return hash(self["client"])

    def __contains__(self, other):
        if isinstance(other, self.__class__):
            return other["client"] in self["client"]
        else:
            return other in self["client"]

    def __len__(self):
        return len(self["client"])

    def get_server_project(self):
        if server_config["project_in_maya"]:
            if not server_config["project_get"]:
                for i in self.networks:
                    re_project = re.compile(r'^%s' % (i), re.I)

                    if re_project.findall(server_config["project_in_maya"]):
                        project_match = i
                        project_drive = i

                        if project_match.startswith("//"):
                            project_drive = self.networks[i]

                        server_config["project"] = re_project.sub(
                            project_drive,
                            server_config["project_in_maya"])
                        server_config["project_get"] = 1
                        server_config["project_in_network"] = 1
                        server_config["project_drive"] = project_drive.rstrip("/")

                        break

    def fix_unc_path(self):
        if self["server"] == "/uploads/error":
            if self["client"].startswith("//"):
                mapping_object = re.findall(r'^(//.+?)/.+',
                                            self["client"], re.I)[0]
                drive = self.get_drive(mapping_object)
                self["mappings"][mapping_object] = drive
                self["mounts"][drive] = "/" + drive.rstrip(":")

                self["server"] = self["client"].replace(mapping_object, drive)

    def get_drive(self, mapping_object):
        for i in server_config["mappings"]:
            if self["client"].startswith(i):
                return server_config["mappings"][i]
        if not self["mappings"]:
            return self.get_new_spare_drives()

    def get_new_spare_drives(self):
        spare_drive = server_config["spare_drives"][-1]
        server_config["used_drives"].append(spare_drive)
        server_config["spare_drives"] = server_config["spare_drives"][:-1]

        return spare_drive

    def get_project_drive(self):
        if server_config["project_drive"]:
            return server_config["project_drive"]
        else:
            project_drive = self.get_new_spare_drives()
            server_config["project_drive"] = project_drive
#            server_config["mounts"][project_drive] = "/" + project_drive.rstrip(":")
            server_config["mounts"][project_drive] = server_config["project"]
            return project_drive

    def get_upload_drive(self):
        if server_config["upload_drive"]:
            return server_config["upload_drive"]
        else:
            upload_drive = self.get_new_spare_drives()
            server_config["upload_drive"] = upload_drive
            server_config["mounts"][upload_drive] = "/" + upload_drive.rstrip(":")
            return upload_drive

    def fix_prefound_path(self):
        for i in server_config["variables"]:
            re_found = re.compile(r'^\${%s}' % (i), re.I)
            r = re_found.findall(self["client"])
            if r:
                self["variables"][i] = server_config["variables"][i]
                self["client"] = self["client"].replace(r[0], os.environ[i])
                self["server"] = self["client"].replace(os.environ[i],
                    server_config["variables"][i])

                return 0

        if self["server"] == "/uploads/error":
            for i in server_config["mappings"]:
                re_found = re.compile(r'^%s' % (i), re.I)
                r = re_found.findall(self["client"])
                if r:
                    self["mappings"][r[0]] = server_config["mappings"][i]
                    self["server"] = re_found.sub(server_config["mappings"][i],
                        self["client"])

                    return 0

        if self["server"] == "/uploads/error":
            for match_project in ["project_custom", "project_in_maya", "project_in_ass"]:
                if server_config[match_project]:
                    print match_project, server_config[match_project]
                    r = re.findall(r'^%s' % server_config[match_project],
                        self["client"], re.I)
                    if r:
                        project_drive = self.get_project_drive()
                        #print_info2(project_drive)

                        self["server"] = self["client"].replace(r[0],
                            server_config["project"])

                    return 0

    def fix_variable_path(self):
        if self["server"] == "/uploads/error":
            r = self.re_variable.findall(self["client"])
            if r:
                if r[0] in os.environ:
                    print "variable %s is %s" % (r[0] ,os.environ[r[0]])
                else:
                    os.environ.setdefault(r[0], default="")
                    print "variable  %s is dont find ,change %s" % (r[0], os.environ[r[0]])
                os.environ[r[0]].replace("\\", "/")

                if len(os.environ[r[0]].strip()) == 3:
                    self["variables"][r[0]] = os.environ[r[0]]
                    proj = "/" + os.environ[r[0]][0]
                else:
                    if ":" in os.environ[r[0]]:
                        # self["variables"][r[0]] = "/" + os.environ[r[0]].replace(":", "")
                        self["variables"][r[0]] = os.environ[r[0]]
                    else:
                        proj = os.path.basename(os.environ[r[0]])
                        self["variables"][r[0]] = "/" + proj

                self["mappings"][os.environ[r[0]]] = self["variables"][r[0]]

                if len(os.environ[r[0]].strip()) == 3:
                    self["client"] = self["client"].replace("${" + r[0] + "}",
                        os.environ[r[0]][:2]).replace("$" + r[0] + "",
                        os.environ[r[0]][:2])
                else:
                    self["client"] = self["client"].replace("${" + r[0] + "}",
                        os.environ[r[0]]).replace("$" + r[0] + "",
                        os.environ[r[0]])

                if self.is_exists():
                    self["exists"] = 1

                if len(os.environ[r[0]].strip()) == 3:
                    self["server"] = self["client"].replace(os.environ[r[0]][:2],
                                                            proj)
                else:
                    self["server"] = self["client"].replace(os.environ[r[0]],
                        self["variables"][r[0]])

    def fix_project_path(self):
        if self["server"] == "/uploads/error":
            for match_project in ["project_custom", "project_in_maya", "project_in_ass"]:
                if server_config[match_project]:
                    #TODO this is some specific codes for ktcartoon
                    if "/lfx_s_kuaichandian/" in self["client"].lower():
                        self["client"] = self["client"].lower().replace("/lfx_s_kuaichandian/",
                            "/lfx_s_kuaicandian/")

                    path_split = self["client"].split("/")
                    for i in range(len(path_split)):
                        if server_config[match_project].endswith(":"):
                            server_config[match_project] += "/"
                        project_file = os.path.join(server_config[match_project],
                            *path_split[i:])
                        if os.path.exists(project_file):
                            self["client"] = project_file.replace("\\", "/")
                            self["exists"] = 1

                            r = re.findall(r'^%s' % server_config[match_project].replace("(", "\(").replace(")", "\)"),
                                self["client"], re.I)

                            if r:
                                project_drive = self.get_project_drive()
                                #print_info2(project_drive)

                                self["mappings"]["/".join(path_split[:i])] = project_drive
                                self["server"] = self["client"].replace(r[0].rstrip("/"), server_config["project"])
                                self["mounts"][project_drive] = "/" + project_drive.strip(":")

                            return 0

    def fix_local_path(self):
        if self["server"] == "/uploads/error":
            for i in self.locals:
                r = re.findall(r'^%s' % i, self["client"], re.I)
                if r:
                    upload_drive = self.get_upload_drive()
                    self["mappings"][r[0]] = upload_drive + \
                        "/uploads/" + server_config["mac"] + "/" + i.rstrip(":")
                    self["server"] = self["client"].replace(r[0],
                        self["mappings"][r[0]])

                    return 0

    def fix_network_path(self):
        if self["server"] == "/uploads/error":
            #print "the path is %s " % self["client"]
            #print type(self["client"])
            for i in self.networks:
                #print "the netwokr is %s" % i
                r = re.findall(r'^%s' % i, self["client"], re.I)
                if r:
                    if re.findall(r'\w:', self["client"], re.I):
                        drive = r[0]
                        path = self.networks[i]
                    else:
                        path = r[0]
                        drive = self.networks[i]

                    if drive.upper() in server_config["forbidden_drives"]:
                        drive_server = self.get_drive(drive)
                    else:
                        drive_server = drive

                    self["mounts"][drive_server] = "/" + drive_server.strip(":")
                    if path:
                        self["mappings"][path] = drive_server

                    self["mappings"][drive] = drive_server
                    #print "the mappings is %s" % self["mappings"]
                    
                    for i in self["mappings"]:
                        #print type(i)
                        #print "the mappings is  %s" % i
                        new_i = i
                        if not re.findall(r'^[a-z0-9 _.:()]+$', i, re.I):
                            #new_i = i.decode("gb18030")
                            if not isinstance(i, unicode):
                                try:
                                    new_i = RvOs.str_to_unicode(i)
                                except:
                                    pass
                            else:
                                new_i=i
                        else:
                            #new_i = i.encode("gb18030")
                            if not isinstance(i, unicode):
                                try:
                                    new_i = RvOs.str_to_unicode(i)
                                except:
                                    pass
                            else:
                                new_i=i
                        if not isinstance(self["client"], unicode):
                            if i in self["client"]:
    
                                #print type(new_i)
                                #print type(i)
                                self["server"] = self["client"].replace(i, self["mappings"][i])
                                return 0
                        else:
                            if new_i in self["client"]:
                                #print type(new_i)
                                #print type(i)
                                self["server"] = self["client"].replace(i, self["mappings"][i])
                                return 0

                    for i in self["mounts"]:
                        if i in self["client"]:
                            self["server"] = self["client"].replace(i, self["mounts"][i])

                            return 0

    def update_server_config(self):
        for type_i in ["variables", "mappings", "mounts"]:
            for i in self[type_i]:
                if i:
                    if i not in server_config[type_i]:
                        server_config[type_i][i] = self[type_i][i]

        server_config["mounts"] = dict([(self.encode(i[0]), self.encode(i[1]))
                                        for i in server_config["mounts"].items()])
    
    def encode(self, string, code="utf-8"):
        if isinstance(string, unicode):
            return string.encode(code)
        else:
            return string

    @property
    def server_long_path(self):
        path = self["client"]

        if self["exists"]:
            if self.is_win:
                for i in self["mappings"].keys():
                    if isinstance(i, unicode):
                        self["mappings"][i.encode("utf-8")] = self["mappings"].pop(i)
                        
                        #        path = "".join([self.options["server_home"],
                        #            self.options["user_home"], self.options["project_home"],
                        #            self["server"]])
                
                for i in self["mappings"]:
                    if RvOs.str_to_unicode(self["client"]).encode("utf-8").startswith(i):
                        path = RvOs.str_to_unicode(self["client"]).encode("utf-8").replace(i,
                                                                                           self["mappings"][i])
                        break

#            key = self["mappings"].keys()[0]
#            path = self["client"].replace(key, self["mappings"][key])

            if self.is_win:
                if isinstance(path, unicode):
                    return path.encode("utf-8")
            return path

    def is_file(self):
        return os.path.isfile(self["client"])

    def is_exists(self):
        if ":" in os.path.basename(self["client"]):
            return not os.system("dir %s" % self["client"].replace("/", "\\"))
        else:
            return os.path.exists(self["client"])

    def is_dir(self):
        return os.path.isdir(self["client"])


class RvLogger(RvOs):

    def __init__(self, log_name, log_file):
        self._logger = logging.getLogger(log_name)
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(levelname)-8s: %(asctime)s %(message)s')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)

    def info(self, msg):
        if self._logger is not None:
            if self.is_win:
                self._logger.info(msg + "\r")
            else:
                self._logger.info(msg)

    def warning(self, msg):
        if self._logger is not None:
            if self.is_win:
                self._logger.warning(msg + "\r")
            else:
                self._logger.warning(msg)

    def error(self, msg):
        if self._logger is not None:
            if self.is_win:
                self._logger.error(msg + "\r")
            else:
                self._logger.error(msg)


class ErrorJson(dict):

    def __init__(self, json_file):
        dict.__init__(self)
        self.json_file = json_file
        if os.path.exists(self.json_file):
            self.update(json.load(open(self.json_file, "r")))

    def save(self):
        json.dump(self, open(self.json_file, 'w'))


class RvTask(dict, RvOs):

    def __init__(self, options):
        dict.__init__(self)
        RvOs.__init__(self)

        RvPath.options = options
        RvPathTxt.options = options

        self.options = options

        self.custom = {"ini": None,
                       "user": None,
                       "renderfarm_path": None,
                       "renderbus_exe": None}

        self.get_preference()
        self["renderSettings"] = {}
        self["common"] = {}

    def get_preference(self):
        self.custom["ini"] = self.options["ini"]

        info = [i.strip() for i in open(self.custom["ini"], "r")]
        self.custom["user"] = info[0]
        self.custom["renderfarm_path"] = info[1]
        self.custom["renderbus_exe"] = info[2]

    def get_id(self):
        id = self.timeout_command("\"%s\" -task %s" % \
            (self.custom["renderbus_exe"], self.options["project_id"]), 60)

        if id == None:
            print_info2("get id spended too many time.", 101)
        elif id == 0:
            print_info2("returned task id number is 0.", 101)
        elif type(id) == type(0):
            print_info2("get task id %s" % (id), 300, task_id=id)
            return str(id)
        else:
            print_info2("returned id number is not right.", 101)

    def get_task_id(self):
        self["common"]["taskId"] = self.get_id()

        self.cfg_path = os.path.join(self.custom["renderfarm_path"],
            self["common"]["taskId"])

        if not os.path.exists(self.cfg_path):
            os.makedirs(self.cfg_path)

    def submit(self):
        self.get_task_id()

        print_info2("get file path info ok.")
        self.write_cfg()
        print_info2("write render.cfg ok.")
        self.write_server_cfg()
        print_info2("write server.cfg ok.")
        self.write_plugins_cfg()
        print_info2("write plugins.cfg ok.")
        self.write_missing_cfg()
        print_info2("write missings.cfg ok.")

        cmd = "\"%s\" -subtask %s" % (self.custom["renderbus_exe"],
            self["common"]["taskId"])

        return_code = self.timeout_command(cmd, 60)

        if return_code == None:
            print_info2("submit task spended too many times.", 101)
        elif return_code == 0:
            print_info2("submit task ok.")
        else:
            print_info2("submit task encounted error.", 101)

    def set_task_level(self, task_level):
        if task_level and task_level != "None":
            task_level = str(task_level)

            if os.path.isfile(task_level):
                self["common"]["level"] = get_level(task_level,
                    self["common"]["cgFile"],
                    self["common"]["projectSymbol"])
            else:
                self["common"]["level"] = task_level

    def set_project_info(self, project_id, project_symbol):
        self["common"]["project_id"] = project_id
        self["common"]["projectId"] = project_id
        self["common"]["projectSymbol"] = project_symbol

    def get_reference(self):
        self.references = []

    def get_cache(self):
        self.caches = []

    def get_texture(self):
        try:
            self.textures
        except:
            self.textures = []

    def write_cfg(self):
        with open(os.path.join(self.cfg_path, "render.cfg"), "w") as cfg_file:
            ''

    def write_server_cfg(self):
        with open(os.path.join(self.cfg_path, "server.cfg"), "w") as cfg_file:
            ''

    def write_plugins_cfg(self):
        with open(os.path.join(self.cfg_path, "plugins.cfg"), "w") as cfg_file:
            ''

    def write_missing_cfg(self):
        with open(os.path.join(self.cfg_path, "missings.cfg"), "w") as cfg_file:
            ''


class ArnoldTask(RvTask):

    def __init__(self, options, ass, path_type="RvPath"):
        RvTask.__init__(self, options)
        self.RvPath = eval(path_type)

        self.ass = ass

        self["common"] = {"taskId": None,
                          "project": "arnold",
                          "kg": 32,
                          "projectSymbol": "default",
                          "cgv": "arnold",
                          "cgSoftName": "maya",
                          "cgFile": self.ass.readName.replace("/", "\\"),
                          "render_file": self.RvPath(self.ass.path).server_long_path,
#                          "render_file": RvPath(self.ass.startFileName).server_long_path,
                          "renderer": None,
                          "output": None,
                          "level": None,
                          "zone": options["zone"],
                          "project_id": None,
                          "projectId": None}

        self["renderSettings"] = {"renderableLayer": None,
                                  "renderableCamera": None,
                                  "width": 640,
                                  "height": 480,
                                  "usedRenderer": None}

        if self.ass.missing:
            self["renderSettings"]["frames"] = ",".join([str(i)
                for i in self.ass.frameinfo])
        else:
            self["renderSettings"]["frames"] = "%s-%s[1]" % (self.ass.start,
                                                       self.ass.end)

        self["texture"] = []
        self["zp"] = []

        self.missings = []

        self.get_reference()
        self.get_cache()
        self.get_texture()

    def write_cfg(self):
        self["texture"] += [self.RvPath(i) for i in self.ass.files]

        if server_config["seperate_account"] in [0, 2]:
            self["texture"] += self.references

        self["texture"] += self.caches

        if server_config["seperate_account"] in [0, 2]:
            self["texture"] += self.textures

        with open(os.path.join(self.cfg_path, "render.cfg"), "w") as cfg_file:
            for step in ["common", "renderSettings"]:
                cfg_file.write("[" + step + "]\n")

                for info in self[step]:
                    cfg_file.write("%s=%s\n" % (info, self[step][info]))

                cfg_file.write("\n")

            for step in ["texture", "zp"]:
                cfg_file.write("[" + step + "]\n")
                i = 0
                for index, path in enumerate(self[step]):
                    print path["client"]
                    if re.findall(r'ddg', path["client"], re.I):
                        print "the path %s  is ddg ,dont up it" % path["client"]
                    else:
                        cfg_file.write("path%d=%s>>%s\n" % (i+1,
                                path["client"], "".join([self.options["user_home"],
                                    self.options["project_home"],
                                    path["server"]])))
                        i = i+1

                    if not path["exists"]:
                        self.missings.append(path["source"].encode("utf-8"))

                cfg_file.write("\n")


    def write_server_cfg(self):
        for type in ["variables", "mappings"]:
            for i in server_config[type]:
                 server_config[type][i] = "".join([self.options["server_home"],
                    self.options["user_home"], self.options["project_home"],
                    server_config[type][i]])

#        pprint.pprint(server_config)

        server_config["task_id"] = self["common"]["taskId"]
        server_config["ass_path"] = self["common"]["render_file"]
        server_config["ass_head"] = self.ass.head
        server_config["ass_tail"] = self.ass.tail
        server_config["ass_padding"] = self.ass.readName.count("#")

        with open(os.path.join(self.cfg_path, "server.cfg"), "w") as cfg_file:
            str = pprint.pformat(server_config)
            # if RvOs.is_win:
            #     str = str.replace("\n", "\r\n")
            cfg_file.write(str)


class TxtTask(ArnoldTask):

    def __init__(self, options, txt):
        self.get_ass_and_texture(txt)

        ArnoldTask.__init__(self, options, self.ass, path_type="RvPathTxt")

        output = os.path.dirname(self["common"]["cgFile"].replace("\\", "/"))
        output = output.lower().replace("render_cache", "render_image")
        self["common"]["output"] = output

    def get_ass_and_texture(self, txt):
        asses = []
        textures = []

        for i in open(txt, "r"):
            file = i.strip()
            if file.lower().endswith(".ass"):
                asses.append(file)
            else:
                textures.append(file)

        self.textures = [RvPathTxt(txt)]
        self.textures += [RvPathTxt(i) for i in set(textures) if i]

        asses = [i for i in set(asses) if i]

        if len(asses) > 1:
            sequences, others = FileSequence.find(asses)
            if len(sequences) == 1:
                self.ass = sequences[0]
            else:
                for ass_i in sequences:
                    txt2 = os.path.basename(txt).replace(".",
                                                         "").replace("_",
                                                                     "").lower()
                    ass2 = ass_i.head.replace(".", "").replace("_", "").lower()
                    if txt2.startswith(ass2):
                        self.ass = ass_i
                    else:
                        self.textures += [RvPathTxt(i) for i in ass_i.files]

            self.textures += [RvPathTxt(i) for i in asses
                              for j in others if j in i]
        else:
            self.ass = FileSequence.single_frame_format(asses[0])


class HoudiniTxtTask(RvTask):

    def __init__(self, options, txt):
        RvTask.__init__(self, options)
        self["common"] = {"taskId": None,
                          "project": "houdini",
                          "kg": 32,
                          "projectSymbol": "default",
                          "cgv": "houdini",
                          "cgSoftName": "maya",
                          "cgFile": None,
                          "render_file": None,
                          "renderer": None,
                          "output": None,
                          "level": None,
                          "zone": options["zone"],
                          "project_id": None,
                          "projectId": None}

        self["renderSettings"] = {"renderableLayer": None,
                                  "renderableCamera": None,
                                  "width": 640,
                                  "height": 480,
                                  "usedRenderer": None}

        self.get_houdini(txt)

        self["texture"] = []
        self["zp"] = []
        self.missings = []

        output = os.path.dirname(self["common"]["cgFile"].replace("\\", "/"))
        output = output.lower().replace("houdini", "render_image")
        self["common"]["output"] = output

    def get_houdini(self, txt):
        self.hip = ""
        self.textures = []

        for i in open(txt, "r"):
            line = i.strip()
            if line:
                if line.lower().endswith(".hip"):
                    if not self.hip:
                        if "bak" not in line.lower():
                            self.hip = line
                            self["common"]["cgFile"] = self.hip.replace("/", "\\")
                            self["common"]["render_file"] = RvPathTxt(self.hip).server_long_path
                        else:
                            self.textures.append(line)
                    else:
                        self.textures.append(line)
                elif "," in line:
                    settings = dict([i.strip().split("=") for i in line.split(",")])
                    self["renderSettings"]["rop"] = settings["rop"]
                    self["renderSettings"]["frames"] = "%s-%s[%s]" % \
                        (settings["start"], settings["end"], settings["by"])
                else:
                    self.textures.append(line)

        self.textures.append(self.hip)
        self.textures = [RvPathTxt(i) for i in set(self.textures) if i]

    def write_cfg(self):
        self["texture"] = self.textures

        with open(os.path.join(self.cfg_path, "render.cfg"), "w") as cfg_file:
            for step in ["common", "renderSettings"]:
                cfg_file.write("[" + step + "]\n")

                for info in self[step]:
                    cfg_file.write("%s=%s\n" % (info, self[step][info]))

                cfg_file.write("\n")

            for step in ["texture", "zp"]:
                cfg_file.write("[" + step + "]\n")

                for index, path in enumerate(self[step]):
                    cfg_file.write("path%d=%s>>%s\n" % (index+1,
                            path["client"], "".join([self.options["user_home"],
                                self.options["project_home"],
                                path["server"]])))

                    if not path["exists"]:
                        self.missings.append(path["source"].encode("utf-8"))

                cfg_file.write("\n")


    def write_server_cfg(self):
        for type in ["variables", "mappings"]:
            for i in server_config[type]:
                 server_config[type][i] = "".join([self.options["server_home"],
                    self.options["user_home"], self.options["project_home"],
                    server_config[type][i]])

#        pprint.pprint(server_config)
        server_config["rop"] = self["renderSettings"]["rop"]
        server_config["task_id"] = self["common"]["taskId"]

        with open(os.path.join(self.cfg_path, "server.cfg"), "w") as cfg_file:
            str_ = pprint.pformat(server_config)
            # if RvOs.is_win:
            #     str_ = str_.replace("\n", "\r\n")
            cfg_file.write(str_)


class MayaTask(dict, RvOs, Zip7):

    def __init__(self, options):
        MayaTask.options = options
        RvPath.options = options

        self.get_preference()

        dict.__init__(self)
        RvOs.__init__(self)
        Zip7.__init__(self, self.custom["7z_exe"])
        self.scene_path = RvPath(pm.sceneName())
        # if not self.scene_path["source"]:
        #     raise Exception("Maya file version is different from the maya "
        #                     "version you had selected in project settings")

        # if self.options["platform"] in ["1005", "1002", "1006", "1008"]:
        self.scene_compress = RvPath(self.compress(self.scene_path["client"]))
        # else:
            # self.scene_compress = None

        self["common"] = {"taskId": None,
                          "project": "maya",
                          "cgSoftName": "maya",
                          "kg": 32,
                          "projectSymbol": "default",
                          "cgv": "maya" + pm.about(v=1).split()[0],
                        #   "cgv": "maya" + "%s.%s".rstrip(".0") % (str(pm.about(api=1))[:4], str(pm.about(api=1))[4]),
                          "cgFile": self.scene_path["client"],
#                          "renderfile": self.scene_path.server_long_path,
                          "renderer": None,
                          "output": None,
                          "level": None,
                          "projectId": None,
                          "project_id": None,
                          "zone": options["zone"],
                          "mountFrom": {},
                          "render_file": self.scene_path.server_long_path,
                          "sceneFile": self.scene_path.server_long_path,
                          "dependency": self.options["dependency"],
                          "sceneProject": None}

        # self["common"]["cgv"] = self["common"]["cgv"].rstrip(".0")
        self["common"]["name"] = os.path.basename(self["common"]["cgFile"])
        self["common"]["original_cg_file"] = self["common"]["cgFile"]
        try:
            self["common"]["munu_pyd_time"] = time.ctime(os.stat(os.path.realpath(__file__)).st_mtime)
        except:
            pass
        
        if self.scene_compress:
            self["common"]["render_file"] = self.scene_compress.server_long_path
            self["common"]["sceneFile"] = self.scene_compress.server_long_path

        self["renderSettings"] = {"renderableLayer": None,
                                  "renderableCamera": [],
                                  "allCamera": None,
                                  "frames": None,
                                  "width": None,
                                  "height": None,
                                  "usedRenderer": None}

        self["texture"] = []
        self["zp"] = []
        self["delete"] = [self.scene_compress]
        

        self.missings = []
        self.references = []
        self.textures = []
        self.caches = []

        options.setdefault("enable_maya_check", 1)
        if options["enable_maya_check"]:
            self.check_maya_settings()

        if options["analyze_mode"] != "fast":
            self.get_reference()
            print_info2("get reference info ok.")

            self.get_cache()
            print_info2("get cache info ok.")

            self.get_texture()
            print_info2("get texture info ok.")

        print_info2("Analyze maya file ok.")

    def check_maya_settings(self):
        print_info2("Start check maya settings.")
        render_global = pm.PyNode("defaultRenderGlobals")
        renderer = render_global.currentRenderer.get()
        plugins = eval(open(self.options["plugin_file"], "r").read().replace("\r", "").replace("\n", ""))
        if "vrayformaya_hybrid_GPU" in plugins["plugins"]:
            if "vrayformaya" not in plugins["plugins"]:
                plugins["plugins"]["vrayformaya"] = plugins["plugins"]["vrayformaya_hybrid_GPU"]

        plugins_rederer = {"arnold": "mtoa",
                           "vray": "vrayformaya",
                           "redshift": "redshift_GPU",
                           "renderman": "RenderMan_for_Maya"}
        plugins_rederer.setdefault(renderer)

        if render_global.modifyExtension.get():
            writing_error(202)

        if int(server_config["user_id"]) not in [1844854]:
            if self.is_absolute_path(render_global.imageFilePrefix.get()):
                writing_error(203)

        if renderer == "vray":
            for i in pm.ls(type="VRaySettingsNode"):
                if self.is_absolute_path(i.fnprx.get()):
                    writing_error(203)
                if i.sys_distributed_rendering_on.get():
                    writing_error(204)
                try:
                    if i.animType.get() == 2:
                        writing_error(205)
                except:
                    pass
                if i.vrscene_on.get():
                    writing_error(208)

        if renderer == "arnold":
            try:
                if pm.PyNode("defaultArnoldRenderOptions").renderType.get() in [1, 2]:
                    writing_error(206)
            except:
                pass

        if render_global.preMel.get() == "pgYetiVRayPreRender":
            if "vrayformaya" not in plugins["plugins"] or "pgYetiMaya" not in plugins["plugins"]:
                writing_error(207)
        #szy dont check renderer
        if plugins_rederer[renderer]:
            if plugins_rederer[renderer] not in plugins["plugins"]:
                if plugins_rederer[renderer] != "mtoa" or int(server_config["maya_version"]) < 2017:
                    writing_error(209)

        if len(str(int(render_global.endFrame.get()))) > render_global.extensionPadding.get():
            writing_error(214)

        if pm.ls(type="xgmPalette"):
            ''

        if pm.optionVar.get("renderSetupEnable", 1):
            ''

        renderable_camera = [i.name() for i in pm.ls(type="camera") if i.renderable.get()]
        if not renderable_camera:
            writing_error(216)

        print_info2("Check maya settings ok.")

    def is_absolute_path(self, path):
        if path:
            path = path.replace("\\", "/")
            if ":" in path:
                return 1
            if path.startswith("//"):
                return 1

    def get_preference(self):
        self.custom = {"ini": None,
                       "user": None,
                       "renderfarm_path": None,
                       "renderbus_exe": None}

        self.custom["ini"] = self.options["ini"]

        if not os.path.exists(self.custom["ini"]):
            raise Exception("Can't find default.ini for maya.")

        info = [i.strip() for i in open(self.custom["ini"], "r")]
        self.custom["user"] = info[0]
        self.custom["renderfarm_path"] = info[1]
        self.custom["renderbus_exe"] = info[2]
        self.custom["7z_exe"] = os.path.join(os.path.dirname(self.custom["renderbus_exe"]),
                                             "module", "bin",
                                             "windows-32-msvc2012",
                                             "7z.exe")

    def get_id(self):
        id = self.timeout_command("\"%s\" -task %s" % \
            (self.custom["renderbus_exe"], self.options["project_id"]), 120)

        if id == None:
            writing_error(220, ["get task id spending 120 seconds."])
            print_info2("get id spended too many times.", 101)
        elif id < 2:
            writing_error(220, ["get task id %s" % id])
            raise Exception("returned task id number is %s" % id)
        elif type(id) == type(0):
            print_info2("get task id %s" % (id), 300, task_id=id)
            return str(id)
        else:
            writing_error(220, ["get task id %s" % id])
            print_info2("returned task id number is not right.", 101)

    def get_task_id(self):
        self["common"]["taskId"] = self.get_id()

        self.cfg_path = os.path.join(self.custom["renderfarm_path"],
            self["common"]["taskId"])

        if not os.path.exists(self.cfg_path):
            os.makedirs(self.cfg_path)

    def get_output(self):
        #TODO 4. we need config the output path from the client app
        if self.preference["output_style"] == "gdc":
            #        "cl_149_081_l4AllLayer_lr_c001.mb"
            infos = os.path.basename(self["common"]["cgFile"]).split(".")[0].split("_")[1:3]
            if len(infos) == 2:
                episode, shot = infos

                if int(episode)/2:
                    type = "odd"
                else:
                    type = "even"

                output = r"z:/netrender/scenes/%s/%s/ep_%03d/sc_%03d" % (self["common"]["projectSymbol"],
                    type, int(episode), int(shot))

    #            self["common"]["output"] = RvPath(output)["client"]
                self["common"]["output"] = output.encode("gb18030")

    def check_render_settings(self):
        all_camera = [i.name() for i in pm.ls(type="camera")]
        render_camera = self["renderSettings"]["renderableCamera"]

        self["renderSettings"]["allCamera"] = ",".join(all_camera)
        self["renderSettings"]["renderableCamera"] = ",".join(set(render_camera))

        if not self["renderSettings"]["renderableCamera"]:
            raise Exception("Can't find camera in render settings.")

        if not self["renderSettings"]["renderableLayer"]:
            raise Exception("Can't find render layer in render settings.")

    def get_auto_create_folder_list(self):
        self["common"]["create_folder"] = []
        mentalray = ["finalgMap", "lightMap", "photonMap", "shadowMap"]
        if not server_config["project_in_network"]:
            project_path = server_config["project_drive"]
        else:
            project_path = server_config["project"]

        if project_path:
            for i in mentalray:
                self["common"]["create_folder"].append(project_path + "/renderData/mentalray/" + i)

    def write_cfg(self, no_upload=0):
        for type in ["mounts"]:
            for i in server_config[type]:
                root = "".join([self.options["server_home"],
                                self.options["user_home"],
                                self.options["project_home"]])

                if server_config[type][i]:
                    if not server_config[type][i].startswith(root):
                        server_config[type][i] = "".join([self.options["server_home"],
                                                          self.options["user_home"],
                                                          self.options["project_home"],
                                                          server_config[type][i]])

        for key in server_config["mounts"].keys():
            if key:
                if server_config["mounts"][key]:
                    self["common"]["mountFrom"][server_config["mounts"][key]] = key

        if self.scene_compress:
            self["texture"] += [self.scene_compress]
        else:
            self["texture"] += [self.scene_path]

        if int(server_config["user_id"]) == 1818936:
            self["texture"] += [RvPath(os.path.splitext(self.scene_path["client"])[0] + ".mel")]

        if server_config["seperate_account"] in [0, 2]:
            self["texture"] += self.references

        self["texture"] += self.caches

        if server_config["seperate_account"] in [0, 2]:
            self["texture"] += self.textures

        if no_upload:
            self["texture"] = []
            self["zp"] = []
            self["delete"] = []

        self["texture"] = list(set(self["texture"]))
        self["texture"] = self.ignore_out_images_for_of3d(self["texture"])
        
        if int(server_config["user_id"]) == 1859047:
            self["delete"] = []
        if int(server_config["user_id"]) == 1865216:
            self["delete"] = []

        with codecs.open(os.path.join(self.cfg_path, "render.cfg"), "w","utf-8") as cfg_file:
        #with open(os.path.join(self.cfg_path, "render.cfg"), "w") as cfg_file:
            for step in ["common", "renderSettings"]:
                cfg_file.write("[" + step + "]\r\n")

                for info in self[step]:
                    cfg_file.write("%s=%s\r\n" % (info, self[step][info]))

                cfg_file.write("\r\n")

            for step in ["texture", "zp"]:
                cfg_file.write("[" + step + "]\r\n")

                if not self.options["only_scene"]:
                    index = 1
                    for path in self[step]:
                        if self.options["platform"] in ["1007"]:
                            write_str = "path%d=%s>>%s\r\n" % (
                                index, path["client"], "".join([self.options["project_home"], path["server"]]))
                        else:
                            write_str = "path%d=%s>>%s\r\n" % (index, path["client"], "".join(
                                [self.options["user_home"], self.options["project_home"], path["server"]]))

                        write_str = RvOs.str_to_unicode(write_str)
                        if path["exists"] and not re.findall(r'ddg', path["client"], re.I):
                            scene_name_ = os.path.splitext(os.path.basename(self.scene_path["client"]))[0]
                            file_name__, file_ext__ = os.path.splitext(os.path.basename(path["client"]))
                            
                            if ":" in path["server"]:
                                pprint.pprint(path)
                                raise Exception("Get drive mappings info error,"
                                                " please reanlayze this file.")
                            else:
                                if file_ext__ != ".rayvision":
                                    cfg_file.write(write_str)
                                    index += 1
                                else:
                                    if file_name__ == scene_name_:
                                        cfg_file.write(write_str)
                                        index += 1

                        else:
                            self.missings.append(RvOs.str_to_unicode(path["source"]).encode("utf-8"))
                else:
                    if step == "texture":
                        if self.scene_compress:
                            cfg_file.write("path1=%s>>%s\r\n" % (self.scene_compress["client"],
                            "".join([self.options["user_home"],
                            self.options["project_home"],
                            self.scene_compress["server"]])))
                        else:
                            cfg_file.write("path1=%s>>%s\r\n" % (self.scene_path["client"],
                            "".join([self.options["project_home"],
                            self.scene_path["server"]])))

            if self.scene_compress:
                for step in ["delete"]:
                    cfg_file.write("[" + step + "]\r\n")
                    index=1
                    for  path in self[step]:
                        file_name__, file_ext__ = os.path.splitext(os.path.basename(path["client"]))
                        if file_ext__ == ".rayvision":
                            cfg_file.write("path%d=%s\r\n" % (index, path["client"]))
                            index = index+1

                cfg_file.write("\r\n")

#            for step in ["texture", "zp"]:
#                cfg_file.write("[" + step + "]\r\n")
#
#                for index, path in enumerate(self[step]):
#                    cfg_file.write("path%d=%s\r\n" % (index+1, path["client"]))
#                    if not path["using_env_variable"]:
#                        self.logger.warning("absolute path: " + path["source"])
#
#                cfg_file.write("\r\n")

    # @staticmethod
    # def ignore_child_path(path_list):
    def ignore_child_path(self, path_list):
        # cPickle.dump(path_list, open("c:/test/original", "wb"))
        path_list = sorted(path_list, key=lambda x: len(x), reverse=1)
        # cPickle.dump(path_list, open("c:/test/sort", "wb"))
        result_list = []
        for index, child_i in enumerate(path_list):
            is_child = 0
            sys.stdout.flush()
            for parent_i in path_list[index+1:]:
                if re.findall(r'%s/' % (parent_i["client"].replace("+", "\+")),
                              child_i["client"].replace("+", "\+"),
                              re.I):
                    is_child = 1
                    break
            if not is_child:
                result_list.append(child_i)

        # if not os.path.exists("c:/test"):
        #     os.makedirs("c:/test")
        # cPickle.dump(result_list, open("c:/test/ignore", "wb"))
        # cPickle.dump(list(set(result_list)), open("c:/test/ignore2", "wb"))
        return list(set(result_list))

    def ignore_out_images_for_of3d(self, path_list):
        result_list = []
        for i in path_list:
            r = re.findall(r'^M:/storage_10/projectFiles/of_ddg_cg/files/publish/sequences.+Lighting/work.+/maya/?$', i["client"], re.I)
            #r = re.findall(r'of_ddg_cg', i["client"], re.I)
            if not r:
                result_list.append(i)
            else:
                maya_path = i["client"].strip("/")
                for i_path in os.listdir(maya_path):
                    if i_path.lower() != "images":
                        result_list.append(RvPath(i["client"] + "/" + i_path))

        return list(set(result_list))

    def set_task_level(self, task_level):
        if task_level and task_level != "None":
            task_level = str(task_level)

            if os.path.isfile(task_level):
                self["common"]["level"] = get_level(task_level,
                                                    self["common"]["cgFile"],
                                                    self["common"]["projectSymbol"])
            else:
                self["common"]["level"] = task_level

    def set_project_info(self, project_id, project_symbol):
        self["common"]["project_id"] = project_id
        self["common"]["projectId"] = project_id
        self["common"]["projectSymbol"] = project_symbol

    def write_server_cfg(self):
        # server_config["project"] = "".join([self.options["server_home"],
        #    self.options["user_home"], self.options["project_home"],
        #    server_config["project"]])

        server_config["mounts"][server_config["project_drive"]] = server_config["project"]
        if not server_config["project_in_network"]:
            server_config["project"] = server_config["project_drive"]

        server_config["task_id"] = self["common"]["taskId"]
        server_config["maya_file"] = self["common"]["sceneFile"]
        server_config["maya_file"] = self["common"]["render_file"]

        for i in server_config["mappings"].keys():
            if not isinstance(i, unicode):
                server_config["mappings"][RvOs.str_to_unicode(i)] = server_config["mappings"].pop(i)

        # print server_config
        # pprint.pprint(server_config)

        with open(os.path.join(self.cfg_path, "server.cfg"), "w") as cfg_file:
            str_ = pprint.pformat(server_config)
            if RvOs.is_win:
                str_ = str_.replace("\n", "\r\n")
            cfg_file.write(str_)

    def write_plugins_cfg(self):
        if self.options["plugin_file"]:
            shutil.copy2(self.options["plugin_file"],
                         os.path.join(self.cfg_path, "plugins.cfg"))
            return 0

        builtin_plugins = [u'AbcExport', u'AbcImport', u'ArubaTessellator',
                           u'Substance', u'modelingToolkit']

        builtin_plugins += [u'Unfold3D', u'modelingToolkitExt',
                            u'modelingToolkit', u'modelingToolkitStd']

        plugin_list = pm.pluginInfo(query=True, listPlugins=True)
        plugins = {}
        if plugin_list:
            plugins = dict([(i, pm.pluginInfo(i, query=1, version=1))
                            for i in pm.pluginInfo(query=True, listPlugins=True)
                            if "autodesk" not in pm.pluginInfo(i, query=1,
                            vendor=1).lower() if i not in builtin_plugins])

        if "shaveNode" in plugins:
            plugins["shaveNode"] = pm.mel.eval('shaveVersion')

        all_infos = {}
        all_infos[u'renderSoftware'] = u'maya'
        all_infos[u'softwareVer'] = server_config["maya_version"]
        all_infos[u'plugins'] = plugins
        all_infos[u'3rdPartyShaders'] = {}

        with open(os.path.join(self.cfg_path, "plugins.cfg"), "w") as cfg_file:
            str = pprint.pformat(all_infos)
            if RvOs.is_win:
                str = str.replace("\n", "\r\n")
            cfg_file.write(str)

    def write_missing_cfg(self):
        if int(server_config["user_id"]) in [961743, 1812689]:
            self.missings = [i for i in self.missings if i.lower() != "redshift"]

        with open(os.path.join(self.cfg_path, "missings.cfg"), "w") as cfg_file:
            for i in self.missings:
                # cfg_file.write(pprint.pformat(self.missings))
                cfg_file.write(i)
                cfg_file.write("\r\n")

        if not int(self.options["ignore_texture"]):
            if self.missings:
                writing_error(201, [to_unicode(i) for i in self.missings])
                raise Exception("Found missing texure files error.")
            else:
                if self.options["user_id"] in [961577]:
                    r = re.compile(r'^z:|sourceimages', re.I)
                    error_file = []
                    for i in self.textures:
                        if not r.findall(i["client"]):
                            error_file.append(i["client"])

                    with open(os.path.join(self.cfg_path, "missings.cfg"),
                              "a") as cfg_file:
                        for i in error_file:
                            cfg_file.write(i)
                            cfg_file.write("\r\n")

                    if error_file:
                        raise Exception("Found error texure files path.")

    def submit(self, no_upload=0):
        self["renderSettings"]["allCamera"] = ",".join([i.name() for i in pm.ls(type="camera")])
        self["renderSettings"]["renderableCamera"] = ",".join(set(self["renderSettings"]["renderableCamera"]))

        self.get_task_id()

#        self.get_output()

        #maya file must be submit.mb
        #put reference mb file in texture block.
#        submit_mb = self.cfg_path + "/submit.mb"

#        self["zp"] = [RvPath(submit_mb)]

#        pm.saveAs(submit_mb)

#        shutil.copy2(self["common"]["cgFile"], submit_mb)

        self.get_auto_create_folder_list()
        print_info2("get file path info ok.")
        self.write_cfg(no_upload)

        print_info2("write render.cfg ok.")
        self.write_server_cfg()

        print_info2("write server.cfg ok.")
        self.write_plugins_cfg()
        print_info2("write plugins.cfg ok.")
        self.write_missing_cfg()
        print_info2("write missings.cfg ok.")

    def set_custom_settings(self, ui_settings):
        self.get_layer_settings()
        self.set_project_info(self.options["project_id"], self.options["project_symbol"])
        self["common"]["name"] = ""

        self["renderSettings"]["allCamera"] = ",".join([i.name() for i in pm.ls(type="camera")])
        if ui_settings["enable_custom_camera"]:
            self["renderSettings"]["renderableCamera"] = [ui_settings["camera"]]
        self["renderSettings"]["renderableCamera"] = ",".join(set(self["renderSettings"]["renderableCamera"]))

        self["renderSettings"]["width"] = ui_settings["width"]
        self["renderSettings"]["height"] = ui_settings["height"]

        self["renderSettings"]["frames"] = ui_settings["frames"]
        self["renderSettings"]["tiles"] = ui_settings["tiles"]

        self["renderSettings"]["firstFrames"] = ui_settings["test_frames"]
        self["renderSettings"]["afterFirstRender"] = ui_settings["after_test_frames"]

        self["renderSettings"]["nodememories"] = ui_settings["memory_requirement"]

    def download_plugin_file(self):
        cmd = "\"%s\" -pluginconfig %s \"maya %s\"" % (self.custom["renderbus_exe"],
                                                       self.options["project_id"],
                                                       server_config["maya_version"])
        return_code = self.timeout_command(cmd, 60)

        if return_code is None:
            print_info2("download plugin file process spended too many times.")
        elif return_code == 0:
            print_info2("download plugin file ok.")
        else:
            print_info2("download plugin file encounted error.")

    def submit2(self, no_upload=0):
        
        self.get_task_id()

        self.get_auto_create_folder_list()
        print_info2("get file path info ok.")
        self.write_cfg(no_upload)

        print_info2("write render.cfg ok.")
        self.write_server_cfg()

        print_info2("write server.cfg ok.")
        self.download_plugin_file()
        self.write_plugins_cfg()
        print_info2("write plugins.cfg ok.")
        self.write_missing_cfg()
        print_info2("write missings.cfg ok.")

        cmd = "\"%s\" -subtask %s 2" % (self.custom["renderbus_exe"],
                                        self["common"]["taskId"])

        return self.timeout_command(cmd, 60)

    def get_all_sub_references(self, reference_node, result=[]):
        if reference_node.subReferences():
            for i in reference_node.subReferences().values():
                result += self.get_all_sub_references(i, result + [i])
            return result
        else:
            return [reference_node]

    def get_reference(self):
        # all_reference = set(pm.listReferences() + [j for i in pm.listReferences()
        #             for j in self.get_all_sub_references(i, result=[])])
        #
        # all_reference = [pm.FileReference(i) for i in pm.ls(type="reference")
        #    if "sharedreferencenode" not in i.name().lower()
        #    and "unknown" not in i.name().lower()]
        #
        # references_path = set([i.path
        #                        for i in all_reference
        #                        if i.isLoaded()])
        #
        # this is for get variables
        # references_path = set([i.unresolvedPath()
        #                        for i in all_reference
        #                        if i.isLoaded()])
        #
        # In some maya files using arnold render, if the reference not exist,
        # even it's not loaded, the render woulbe be failed,
        # so we upload all the reference even it's not loaded.

        all_reference = pm.listReferences(recursive=1)
        # references_path = set([i.unresolvedPath() for i in all_reference])
        # references_path = set([i.path for i in all_reference])
        # I don't remember why i use path or unresolvedPath() before
        # I use path just for a temp workaround.
        # I use unresolvedPath to get path with enviroment variable just now.
        references_path = []
        for i in all_reference:
            if i.unresolvedPath().startswith("$"):
                references_path.append(i.unresolvedPath())
            else:
                references_path.append(i.path)

#        for i in reference:
#            if not i["is_network"]:
#                raise Exception("Found reference file in the local machine.")

        self.references = [RvPath(i) for i in set(references_path)
                           if i if i.strip()]

    def find_cache_files(self, cache_path, cache_name):
        return [os.path.join(cache_path, i) for i in os.listdir(cache_path)   if i.lower().startswith(cache_name.lower())]

    def get_cache(self):
        self.caches = []
#        caches = [(i.cachePath.get(), i.cacheName.get())
#                    for i in pm.ls(type="cacheFile")]
#
#        for i in caches:
#            self["texture"] += [RvPath(i) for i in self.find_cache_files(i[0], i[1])]

        #get all files in the cache directorys.
        cache_paths = set([i.cachePath.get().strip() for i in pm.ls(type="cacheFile") if i.cachePath.get() if i.cachePath.get().strip()])
        cache_paths = [RvPath(i) for i in cache_paths if i if i.strip()]

        for path_i in cache_paths:
            if path_i["exists"]:
                self.caches += [RvPath(os.path.join(root, file))
                                for root, dirs, files in os.walk(path_i["client"])
                                for file in files
                                if re.findall(r'^[\w _\-.:()\\/${}]+$',
                                              os.path.join(root, file), re.I)]

    def get_xgen2(self):
        maya_file_list = self.references[:]
        maya_file_list.append(self.scene_path)
        return [j for i in maya_file_list
                for j in self.get_xgen_with_maya_file(i["client"])]

    def get_xgen(self):
        xgen = [i.xgFileName.get() for i in pm.ls(type="xgmPalette") if i.xgFileName.get() if i.xgFileName.get().strip()]
        xgen_format = []
        files1 = []
        files2 = []
        files3 = []
        files4 = []
        data_path = []
        data_path2 = []
        file_str2 = []
        xgen_bb=[]
        for i in xgen:
            xgen_i = RvPath(os.path.join(os.path.dirname(self["common"]["cgFile"]), i))
            if xgen_i["exists"]:
                xgen_format.append(xgen_i)
                data_path.append(self.get_data_path_from_xgen(xgen_i["client"]))
                xgen_abc = RvPath(xgen_i["client"].lower().replace(".xgen",".abc"))
                xgen_format += self.get_files_from_xgen_1832205(xgen_i["client"])
                if xgen_abc["exists"]:
                    xgen_format.append(xgen_abc)
            else:
                xgen_format.append(RvPath(i))

        if xgen:
            import xgenm as xg
            import xgenm.xgGlobal as xgg
            import xgenm.XgExternalAPI as xge
            
            file_str = [xg.getAttr("files", i_pale, i_desc, "ArchivePrimitive")
                        for i_pale in xg.palettes()
                        for i_desc in xg.descriptions(i_pale)
                        if "ArchivePrimitive" in xg.objects(i_pale, i_desc)]

            file_str2 = [xg.getAttr("cacheFileName", i_pale, i_desc, "SplinePrimitive")
                         for i_pale in xg.palettes()
                         for i_desc in xg.descriptions(i_pale)
                         if "SplinePrimitive" in xg.objects(i_pale, i_desc)]

            file_str2 += [xg.getAttr("custom__arnold_auxRenderPatch", i_pale, i_desc, "RendermanRenderer")
                          for i_pale in xg.palettes()
                          for i_desc in xg.descriptions(i_pale)
                          if "RendermanRenderer" in xg.objects(i_pale, i_desc)]
            file_str2 += [xg.getAttr("custom__vray_CacheFile", i_pale, i_desc, "RendermanRenderer")
                          for i_pale in xg.palettes()
                          for i_desc in xg.descriptions(i_pale)
                          if "RendermanRenderer" in xg.objects(i_pale, i_desc)]
            
            file_str2 = [RvPath(i) for i in file_str2 if not i.startswith("$") and i and i != "0"]
            print file_str2
            print "+++++++++++++++++++++++++++++"
            xgen_bb = self.get_xgen_cgcgbb()
            print xgen_bb
            #xgen_bb = [RvPath(i) for i in xgen_bb if os.path.exists(i) ]
            xgen_bb = [RvPath(i) for i in xgen_bb]
            print xgen_bb
            print "+++++++++++++++++++++++++++++"
            # of3d using xgDataPath and xgProjectPath with absolute path in xgen file
            # xgDataPath		M:/storage_10/projectFiles/of_ddg_cg/files/publish/assets/Environment/flaenv01_a/Xgen/maya/v018/xgen/collections/leaf_roof_left
            # xgProjectPath		K:/rendertmp/users/liaoyanchen/maya_project/ddg_outsource/
            # but from xgen api, only get ${PROJECT}Xgen/maya/v018/xgen/collections/leaf_roof_left
            # so we get info from xgen file directly instead of api
            # data_path = list(set([RvPath(xg.getAttr("xgDataPath", i_pale))
            #                  for i_pale in xg.palettes()]))

            # data_path = []
            # for i_pale in xg.palettes():
            #     xg_data = xg.getAttr("xgDataPath", i_pale)
            #     print xg_data
            #     data_path.append(RvPath(xg_data))

            files = set()
            folders = set()
            #
            for file_i in file_str:
                r = re.findall(r'"[a-z0-9:/_. ]+/[a-z0-9:/_. {}$]+"', file_i, re.I)
                #files_p = re.compile(r'(?<=")(?:[a-z][:][\\/]|[\\\\]|[\${?])(?:[\w _\-.:()\\/$/+{}\'])+(?=")', re.I)
                #r = files_p.findall(file_i)
                if r:
                    for i in r:
                        file = eval(i).lower()
                        files.add(file)
                        if file.endswith(".ass.gz"):
                            asstoc = file.replace(".ass.gz", ".asstoc")
                            if os.path.exists(asstoc):
                                files.add(asstoc)

            for i in list(files):
                r = re.findall(r'\$\{frame\}', i, re.I)
                if r:
                    folders.add(os.path.dirname(i))
                    files.remove(i)
            
            files1 = [RvPath(i) for i in files if i ]
            files2 = [RvPath(i.split("/archives")[0])
                      for i in files if "xgen/archives" in i]
            files4 = [RvPath(i.split("/xarchive")[0])
                      for i in files if "/xarchive" in i]

            data_path2 = [RvPath(i) for i in folders if i]

        files3 = set()
        abc_folder = os.path.dirname(self["common"]["cgFile"])
        abc_base = os.path.splitext(os.path.basename(self["common"]["cgFile"]))[0].lower()

        for i in os.listdir(abc_folder):
            if i.lower().startswith(abc_base):
                if i.lower().endswith(".abc"):
                    files3.add(os.path.join(abc_folder, i))
        
        
        files3 = [RvPath(i) for i in files3 if i]
        #print files3
        print "get xgen files ok."
        result = xgen_format + files1 + files2 + files3 + files4 + data_path + data_path2 + file_str2 + xgen_bb
        #print result
        abc_folder2 = []
        for i in result:
            # if i["client"].lower().endswith(".abc"):
            #     abc_folder2.append(RvPath(os.path.dirname(os.path.dirname(i["client"]))))
            if os.path.basename(i["client"]).lower() == ".abc":
                abc_folder2.append(RvPath((i["client"])))
            if os.path.basename(i["client"]).lower() == ".xgen":
                abc_folder2.append(RvPath((i["client"])))
        
       
        return result + abc_folder2

    def get_xgen_cgcgbb(self):
        import xgenm as xg
        import xgenm.xgGlobal as xgg
        if xgg.Maya:
            xgen_path = []
            palettes = xg.palettes()
            #print xg.rootDir()
            for palette in palettes:
                p1 = re.compile(r"(?<=map\(\')[\w _\-.:()\\/$/+{}']+(?=\'\))", re.I)
                p2 = re.compile(r"^\${.*", re.I)
                #p3 = re.compile(r'[a-z][:][\\/][\w _\-.:()\\/$+]+\.[\w]+',re.I)
                p3 = re.compile(r'[a-z][:][\\/][\w _\-.:()\\/$+]+',re.I)
                files_p = re.compile(r'(?<=")(?:[a-z][:][\\/]|[\\\\]|[\${?])(?:[\w _\-.:()\\/$/+{}\'])+(?=")', re.I)
                attrs = xg.allAttrs(palette)
                palette_attr_list = []
                for attr in attrs:
                    palette_attr = xg.getAttr(attr, palette).strip()
                    if attr == "xgDataPath":
                        xgDataPath_path = palette_attr
                        xgen_path.append(xg.expandFilepath(xgDataPath_path, palette))
                
                    if attr == "xgProjectPath":
                        xgProjectPath_path = palette_attr
                        continue
                    if "$" in palette_attr:
                        r1 = p1.findall(palette_attr)
                        r2 = p2.findall(palette_attr)
                        if r1:
                            for rr in r1:
                                palette_attr_list.append(rr)
                        if r2:
                            for rr in r2:
                                palette_attr_list.append(rr)
                    else:
                        r3 = p3.findall(palette_attr)
                        if r3:
                            for rr in r3:
                                palette_attr_list.append(rr)
            
                descriptions = xg.descriptions(palette)
                for description in descriptions:
                    # print xgDataPath_path,xgProjectPath_path
                    desc = xg.expandFilepath("${DESC}", description)
                
                    for attr in palette_attr_list:
                        xgen_path.append(xg.expandFilepath(attr, description))
                
                    objects = xg.objects(palette, description, True)
                    for object in objects:
                        print " Object:" + object
                        attrs = xg.allAttrs(palette, description, object)
                        
                        for attr in attrs:
                            attr_Value = xg.getAttr(attr, palette, description, object)
                            print "attr :" + attr
                            print "attr_Value : " +attr_Value
                            if attr == "files":
                                file_rs = files_p.findall(attr_Value)
                                if file_rs:
                                    for file_r in file_rs:
                                        file_r = os.path.normpath(xg.expandFilepath(file_r, description))
                                        if file_r:
                                            archives = ["\\ass\\","\\abc\\","\\materials\\","\\mi\\","\\rib\\"]
                                            xgen_path += [file_r.split(i)[0]  for i in archives if i in file_r]
                            if attr == "cacheFileName":
                                print attr_Value
                            r1 = p1.findall(attr_Value)
                            r2 = p2.findall(attr_Value)
                            r3 = p3.findall(attr_Value)
                            if r1:
                                for rr in r1:
                                    rr = xg.expandFilepath(rr, description)
                                    if rr:
                                        xgen_path.append(rr)
                            if r2:
                                for rr in r2:
                                    rr = xg.expandFilepath(rr, description)
                                    if rr:
                                        xgen_path.append(rr)
                            
                            if r3:
                                for rr in r3:
                                    if rr:
                                        xgen_path.append(rr)
                    fxModules = xg.fxModules(palette, description)
                    for fxModule in fxModules:
                        # print " fxModule:" + fxModule
                        attrs = xg.allAttrs(palette, description, fxModule)
                        for attr in attrs:
                            attr_Value = xg.getAttr(attr, palette, description, fxModule)
                        
                            r1 = p1.findall(attr_Value)
                            r2 = p2.findall(attr_Value)
                            r3 = p3.findall(attr_Value)
                            if r1:
                                for rr in r1:
                                    #rr = xg.expandFilepath(rr.replace("${FXMODULE}", fxModule).replace("${DESC}", desc),description)
                                    rr = rr.replace("${FXMODULE}", fxModule).replace("${DESC}", desc)
                                    if rr:
                                        xgen_path.append(rr)
                            if r2:
                                for rr in r2:
                                    #rr = xg.expandFilepath(rr.replace("${FXMODULE}", fxModule).replace("${DESC}", desc), description)
                                    rr = rr.replace("${FXMODULE}", fxModule).replace("${DESC}", desc)
                                    if rr:
                                        xgen_path.append(rr)
                            if r3:
                                for rr in r3:
                                    #rr = xg.expandFilepath(rr.replace("${FXMODULE}", fxModule).replace("${DESC}", desc),description)
                                    rr = rr.replace("${FXMODULE}", fxModule).replace("${DESC}", desc)
                                    if rr:
                                        xgen_path.append(rr)
            print xgen_path
            xgen_path = [os.path.normpath(i.rstrip("/")) for i in set(xgen_path)]
            return set(xgen_path)

    def get_file_vrscene(self,vrscene):
        path_list = []
        path_list_old = []
        textures = []
    
        path_list.append(vrscene)
        TYPE_PATTERN = re.compile("^[a-zA-Z].+")
        vrscene_PATTERN = re.compile(r'(?:[a-z][:][\\/]|[\\\\]|[/]|(?:\.\./)|(?:\.\.\\))[\w _\-.:()\\/$+]+\.vrscene',
                                     re.I)
    
        for p in path_list:
            current_node = {}
            node = []
            #print p
            with open(p, 'r') as f:
                while True:
                    line = f.readline()
                    if line:
                        line = line.strip()
                        if line.startswith("//"):
                            pass
                        elif line.startswith("#include"):
                            vrscene_file = vrscene_PATTERN.findall(line)
                            if vrscene_file:
                                # print vrscene_file[0]
                                if vrscene_file[0] not in path_list_old and vrscene_file[
                                    0] not in path_list and os.path.exists(vrscene_file[0]):
                                    path_list.append(vrscene_file[0])
                            else:
                                pass
                    
                        elif TYPE_PATTERN.findall(line):
                            if current_node:
                                group = line.strip().replace(';', '').split('=')
                                if len(group) == 2:
                                    current_node[group[0]] = group[1]
                                else:
                                    print ""
                            else:
                                line = [i for i in line.split() if i not in ["{", "}"]]
                                if len(line) == 2:
                                    # print line
                                    current_node['nodeType'] = line[0]
                                    current_node['nodeName'] = line[1]
                        if "}" in line:
                            node.append(current_node)
                        
                            current_node = {}
                        else:
                            pass
                    else:
                        break
            path_list_old.append(p)
            for a in node:
                print a['nodeType']
                if a['nodeType'] == 'BitmapBuffer':
                    #print a['nodeName']
                    #print a['file']
                    textures.append(a['file'])
        #print path_list_old
        #print textures
        textures += path_list_old
        return list(set(textures))
    def get_data_path_from_xgen(self, xgen_file):
        xgDataPath = ""
        xgProjectPath = ""
        for line in open(xgen_file, "r"):
            if "xgDataPath" in line:
                r = re.findall(r'\s*xgDataPath\s*(.+?)\s*$', line, re.I)
                if r:
                    xgDataPath = r[0]

            elif "xgProjectPath" in line:
                r = re.findall(r'\s*xgProjectPath\s*(.+?)\s*$', line, re.I)
                if r:
                    xgProjectPath = r[0]
                    break

        xgDataPath = xgDataPath.replace("${PROJECT}", xgProjectPath)
        return RvPath(xgDataPath)

    def get_files_from_xgen(self, xgen_file):
        file_str = [i for i in open(xgen_file, "r") if "files" in i]
        files = set()

        for file_i in file_str:
            r = re.findall(r'".+?"', file_i, re.I)
            if r:
                for i in r[3:]:
                    file = eval(i).lower()
                    files.add(file)
                    if file.endswith(".ass.gz"):
                        asstoc = file.replace(".ass.gz", ".asstoc")
                        if os.path.exists(asstoc):
                            files.add(asstoc)

        return [RvPath(i) for i in files]

    def get_files_from_xgen_1832205(self, xgen_file):
        file_str = [i for i in open(xgen_file, "r")]
        files = set()
        p = re.compile(r'[a-z][:][\\/][\w _\-.:()\\/$+]+\.[\w]+', re.I)
        for file_i in file_str:
            r = p.findall(file_i)
            if r:
                for ii in r:
                    files.add(ii)
        return [RvPath(i) for i in files]



    def get_xgen_with_maya_file(self, maya_file):
        result = []
        maya_path = os.path.dirname(maya_file)
        xgen_data = os.path.join(maya_path, "xgen")
        if os.path.exists(xgen_data):
            result.append(RvPath(xgen_data))

        xgen_file_type = ["json", "xgen"]
        for i in os.listdir(maya_path):
            for j in xgen_file_type:
                if i.lower().endswith(j):
                    result.append(RvPath(os.path.join(maya_path, i)))
        return result

    def get_yeti(self):
        yeti_node = pm.ls(type="pgYetiMaya")
        texture = []
        for i in yeti_node:
            texture_in_yeti = None
            try:
                texture_in_yeti = pm.mel.pgYetiGraph("-listNodes", "-type",
                                                     "texture", i)
            except:
                pass

            if texture_in_yeti:
                if i.hasAttr("isp"):
                    search_path = i.isp.get()
                else:
                    search_path = None

                for j in texture_in_yeti:
                    image = pm.mel.pgYetiGraph("-node", j, "-param",
                                               "file_name", "-getParamValue", i)
                    if not os.path.exists(image):
                        if search_path:
                            image = os.path.join(search_path, image)
                    texture.append(image)

        for i in yeti_node:
            texture_in_yeti = None
            try:
                texture_in_yeti = pm.mel.pgYetiGraph("-listNodes", "-type",
                                                     "reference", i)
            except:
                pass

            if texture_in_yeti:
                for j in texture_in_yeti:
                    texture.append(pm.mel.pgYetiGraph("-node", j, "-param",
                                   "reference_file", "-getParamValue", i))

        texture += [i.outputCacheFileName.get()
                    for i in yeti_node
                    if i if i.strip()  if i.outputCacheFileName.get() if i.outputCacheFileName.get().strip()]

        texture += [i.cacheFileName.get()
                    for i in yeti_node
                    if i if i.strip() if i.cacheFileName.get() if i.cacheFileName.get().strip()]

        texture += [i.groomFileName.get() for i in yeti_node    if i.hasAttr("groomFileName") if i.groomFileName.get()  if i.groomFileName.get().strip()]

        texture += [j for i in yeti_node
                    if i.hasAttr("imageSearchPath")
                    if i.imageSearchPath.get()
                    for j in i.imageSearchPath.get().strip().split(";")]
        # texture2 = set()
        # for i in texture:
        #     if re.findall(r'<udim>', i, re.I):
        #         for path in self.get_udim_files(i):
        #             texture2.add(path)
        #     elif "%04d" in i:
        #         path = os.path.dirname(i)
        #         if os.path.exists(path):
        #             texture2.add(RvPath(path))
        #     else:
        #         texture2.add(RvPath(i))
        texture2 = []
        for i in texture:
            if os.path.isdir(i):
                texture2.append(RvPath(i))
            else:
                texture2 += [RvPath(ii) for ii in self.file_images(i.strip())]

        texture2 = list(set(texture2))
        print "get yeti files ok."
        
        return texture2

    def get_single_ass_from_sequence(self, seq, frame):
        # P:/CAS_NEC3/Asset/Publish/PRO/Itm/Grass/Ass/Grass_One/Grass_One.####.ass 19
        frame = str(frame).zfill(seq.count("#"))
        seq_split = seq.split("#")
        single_ass = "".join([seq_split[0], frame, seq_split[-1]])
        if os.path.exists(single_ass):
            return single_ass
        elif os.path.exists(single_ass + ".gz"):
            return single_ass + ".gz"
        else:
            return single_ass

    def get_ass(self):
        texture = []
        ass_node = pm.ls(type="aiStandIn")
        print "get ass node: " + str(len(ass_node))
        all_standin_ass = set([i.dso.get() for i in ass_node])
        all_ass = [i for i in all_standin_ass if i if i.strip()]
        #print all_ass
        ass = [RvPath(i) for i in all_ass if "#" not in i]
        print "get single ass files: " + str(len(ass))

        seq_ass = [RvPath(os.path.join(os.path.dirname(i), j))
                   for i in all_ass
                   if "#" in i
                   if os.path.exists(os.path.dirname(i))
                   for j in os.listdir(os.path.dirname(i))
                   if j.lower().endswith(".ass") or
                   j.lower().endswith(".gz")]
        
        texture += ass
        texture += seq_ass
        #print ass
        #print seq_ass
        #print "get  ### ass files: " + str(len(seq_ass))
        analyze_ass = ass
        
        if self.options["all_proxy"]:
            
            analyze_ass += seq_ass
        else:
            
            sequences, others = FileSequence.find([i["client"] for i in seq_ass])
            
            for i in sequences:
                print "sequesn is %s " % i
                analyze_ass.append(RvPath(i.startFileName))
            for i in others:
                analyze_ass.append(RvPath(i))

        print "Analyze ass files: " + str(len(analyze_ass))
        
        for i in analyze_ass:
            if i["exists"]:
                if i["client"].lower().endswith("arcadia_school_landscape_fursystemnodebshape_standin_v11.ass"):
                    continue

                print "Analyze ass file: " + i["client"]
                texture += AssFile(i["client"]).get_files_from_ass()
                print "get ass file: " + i["client"] + " ok."

        print "get all ass files ok."
        return texture

    def get_ass_pixomon(self):
        texture = []
        a_ass = []
        ass = []
        for i in pm.ls(type='mesh'):
            print i
        
        all_ass = set([i.dso.get() for i in pm.ls(type='mesh') if i.hasAttr('dso') if i.ai_translator.get() == "procedural" if i.dso.get() if i.dso.get().strip()])
        all_ass = [i for i in all_ass if i if i.strip()]
        
        for i in all_ass:
            print i
            old_nub = i.split('.')[1]
            try:
                if int(old_nub):
                    num_ass = glob.glob(i.replace(".%s." % old_nub, ".*."))
                    for a in num_ass:
                        a_ass.append(a)
            except:
                a_ass.append(i)

        print a_ass
        print "get ass files: " + str(len(a_ass))
        ass += [RvPath(i.replace('\\','/'))  for i in a_ass if i  if i.strip()]
        
        texture += ass
     
        
     
        if self.options["all_proxy"]:
            analyze_ass = ass
        else:
            sequences, others = FileSequence.find([i["client"] for i in ass])
            analyze_ass = []
            for i in sequences:
                analyze_ass.append(RvPath(i.startFileName))
            for i in others:
                analyze_ass.append(RvPath(i))
    
        print "Analyze  ass files: " + str(len(analyze_ass))
    
        for i in analyze_ass:
            if i["exists"]:
                if i["client"].lower().endswith("arcadia_school_landscape_fursystemnodebshape_standin_v11.ass"):
                    continue
            
                print "Analyze ass file: " + i["client"]
                texture += AssFile(i["client"]).get_files_from_ass()
                print "get ass file: " + i["client"] + " ok."
    
        print "get all ass files ok."
        return texture
       
    def get_assembly(self):
        texture = []
        p1 = re.compile(r"^[a-zA-Z]:/?")
        p2 = re.compile(r"^/+")
        maya_proj_paht = pm.workspace(q=True, fullName=True)
        definition_node = pm.ls(type="assemblyDefinition")
        definition_node += pm.ls(type="assemblyReference")
        for i_node in definition_node:
            for i in i_node.representations:
                #print i.definition.get()
                if i.rty.get() in ["Scene", "Cache"]:
                    path = i.rda.get()
                    if path and path.strip():
                        path = path.replace('\\', '/')
                        if p1.findall(path) or p2.findall(path):
                            texture.append(RvPath(path.strip()))
                        else:
                            path = "%s/%s" % (maya_proj_paht, path)
                            texture.append(RvPath(path.strip()))


            if i_node.type() == "assemblyReference":
                path = i_node.definition.get()
                if path and path.strip():
                    path = path.replace('\\', '/')
                    if p1.findall(path) or p2.findall(path):
                        texture.append(RvPath(path.strip()))
                    else:
                        path = "%s/%s" % (maya_proj_paht, path)
                        texture.append(RvPath(path.strip()))

        print "get scene assemly files ok."
        return texture

    def get_mi(self):
        texture = []
        mi = list(set([RvPath(i.miProxyFile.get()) for i in pm.ls(type="mesh")
                       if i.hasAttr("miProxyFile")
                       if i.miProxyFile.get() if i.miProxyFile.get().strip()]))

        texture += mi

        sequences, others = FileSequence.find([i["client"] for i in mi])
        analyze_mi = []
        for i in sequences:
            analyze_mi.append(RvPath(i.startFileName))
        for i in others:
            analyze_mi.append(RvPath(i))

        for i in analyze_mi:
            if i["exists"]:
                for line in open(i["client"]):
                    if len(line) < 500:
                        r = re.findall(r'.+\"([a-z]:/.+)\"$', line, re.I)
                        if r:
                            texture.append(RvPath(r[0]))
        mi2 = []
        if "cgGeoReplace" in pm.ls(nodeTypes=1):
            
            mi2 = list(set([RvPath(i.fileName.get() + ".mi.gz")
                            for i in pm.ls(type="cgGeoReplace")
                            if i.fileName.get() if i.fileName.get().strip()]))
        
            texture += mi2

        sequences, others = FileSequence.find([i["client"] for i in mi2])
        analyze_mi2 = []
        for i in sequences:
            analyze_mi2.append(RvPath(i.startFileName))
        for i in others:
            analyze_mi2.append(RvPath(i))

        for i in analyze_mi2:
            if i["exists"]:
                for line in gzip.open(i["client"]):
                    if len(line) < 500:
                        r = re.findall(r'.+\"([a-z]:/.+)\"$', line, re.I)
                        if r:
                            texture.append(RvPath(r[0]))

        return texture

    def get_redshift(self):
        texture = []
        print "get RedshiftDomeLight"
        texture += [RvPath(ii) for i in pm.ls(type="RedshiftDomeLight")
                    if i.tex0.get() if i.tex0.get().strip()
                    for ii in self.file_images(i.tex0.get().strip(), i.useFrameExtension.get())]
    
        texture += [RvPath(ii) for i in pm.ls(type="RedshiftDomeLight")
                    if i.tex1.get() if i.tex1.get().strip()
                    for ii in self.file_images(i.tex1.get().strip(), i.useFrameExtension1.get())]
    

        print "get RedshiftSprite "
        texture += [RvPath(ii) for i in pm.ls(type="RedshiftSprite")
                    if i.tex0.get() if i.tex0.get().strip()
                    for ii in self.file_images(i.tex0.get().strip(), i.useFrameExtension.get())]
    
        print "get RedshiftNormalMap "
        texture += [RvPath(ii) for i in pm.ls(type="RedshiftNormalMap")
                    if i.tex0.get() if i.tex0.get().strip()
                    for ii in self.file_images(i.tex0.get().strip(), i.useFrameExtension.get())]
    
        print "get RedshiftEnvironment  "
        texture += [RvPath(ii) for i in pm.ls(type="RedshiftEnvironment")
                    if i.tex0.get() if i.tex0.get().strip()
                    for ii in self.file_images(i.tex0.get().strip(), i.useFrameExtension.get())]
    
        texture += [RvPath(ii) for i in pm.ls(type="RedshiftEnvironment")
                    if i.tex1.get() if i.tex1.get().strip()
                    for ii in self.file_images(i.tex1.get().strip(), i.useFrameExtension1.get())]
    
        texture += [RvPath(ii) for i in pm.ls(type="RedshiftEnvironment")
                    if i.tex2.get() if i.tex2.get().strip()
                    for ii in self.file_images(i.tex2.get().strip(), i.useFrameExtension2.get())]
    
        texture += [RvPath(ii) for i in pm.ls(type="RedshiftEnvironment")
                    if i.tex3.get() if i.tex3.get().strip()
                    for ii in self.file_images(i.tex3.get().strip(), i.useFrameExtension3.get())]
    
        texture += [RvPath(ii) for i in pm.ls(type="RedshiftEnvironment")
                    if i.tex4.get() if i.tex4.get().strip()
                    for ii in self.file_images(i.tex4.get().strip(), i.useFrameExtension4.get())]
    
        print "get RedshiftVolumeShape"
        texture += [RvPath(ii) for i in pm.ls(type="RedshiftVolumeShape")
                    if i.fileName.get() if i.fileName.get().strip()
                    for ii in self.file_images(i.fileName.get().strip(), i.useFrameExtension.get())]
        
        
        print "get RedshiftIESLight"
        texture += [RvPath(i.profile.get().strip())
                    for i in pm.ls(type="RedshiftIESLight")
                    if i.profile.get() if i.profile.get().strip()]
        
        
        print "get dofBokehImage"
        texture += [RvPath(i.dofBokehImage.get().strip())
                    for i in pm.ls(type="RedshiftIESLight")
                    if i.hasAttr("dofBokehImage")
                    if i.dofBokehImage.get() if i.dofBokehImage.get().strip()]
        
        print "get RedshiftBokeh"
        texture += [RvPath(i.dofBokehImage.get().strip())
                    for i in pm.ls(type="RedshiftBokeh")
                    if i.hasAttr("dofBokehImage")
                    if i.dofBokehImage.get() if i.dofBokehImage.get().strip()]
        
        
        print "get irradianceCacheFilename"
        texture += [RvPath(ii) for i in pm.ls(type="RedshiftOptions")
                    if i.irradianceCacheMode.get() ==1
                    if i.irradianceCacheFilename.get() if i.irradianceCacheFilename.get().strip()
                    for ii in self.file_images(i.irradiancePointCloudFilename.get().strip(), 0)]
        print "get irradiancePointCloudFilename "
        texture += [RvPath(ii) for i in pm.ls(type="RedshiftOptions")
                    if i.irradianceCacheMode.get() ==1
                    if i.irradiancePointCloudFilename.get() if i.irradiancePointCloudFilename.get().strip()
                    for ii in self.file_images(i.irradiancePointCloudFilename.get().strip(), 0)]
        print "get photonFilename "
        texture += [RvPath(ii) for i in pm.ls(type="RedshiftOptions")
                    if i.photonFilename.get() ==1
                    if i.photonFilename.get() if i.photonFilename.get().strip()
                    for ii in self.file_images(i.photonFilename.get().strip(), 0)]
       
        

        texture2 = []
        print "get #file"
        for i in set(texture):
            if "#" in i["client"]:
                path = RvPath(os.path.dirname(i["client"]))
                if os.path.exists(path["client"]):
                    texture2.append(path)
            else:
                texture2.append(i)
        print "get dont exists  file "
        p = re.compile(r'^(?:[a-z][:][\\/]|[\\\\]|(?:\${?))',re.I)
        for i in texture2:
            if i["exists"]==0:
                if not p.findall(i["client"]):
                    for ii in self.file_images(i["client"], 1):
                        if RvPath(ii)["exists"]:
                            texture2.append(RvPath(ii))
        
        
        
        
        
        
        texture2 +=self.get_rs_ProxyMesh()
            # for i in rs_proxy:
            #     print "Anlyze %s" % (i["client"])
            #     if i["exists"]:
            #         texture2 += self.get_files_from_rs(i["client"])
            #     elif "#" in i["client"]:
            #         single_file = self.get_single_file_from_sequence(i["client"])
            #         if single_file:
            #             texture2 += self.get_files_from_rs(single_file)
            #     else:
            #         print "Not exists, skip %s" % (i["client"])
        print "get redshift end"
        return list(set(texture2))
    
    def get_rs_ProxyMesh(self):
        rs_old = []
        print "get RedshiftProxyMesh"
        texture = []
        for i in pm.ls(type="RedshiftProxyMesh"):
            rs_seq = []
            if i.fileName.get():
                if i.fileName.get().strip():
                    if i.useFrameExtension.get():
                        for ii in self.file_images(i.fileName.get().strip(),1):
                            rs_seq.append(ii)
                            texture.append(RvPath(ii))
                        if not int(self.options["dont_analyze_ass"]):
                            if rs_seq[0] not in rs_old and os.path.exists(rs_seq[0]):
                                print "get file   form seq rs"
                                texture += self.get_files_from_rs(rs_seq[0])
                                rs_old.append(rs_seq[0])
                    else:
                        texture.append(RvPath(i.fileName.get().strip()))
                        if not int(self.options["dont_analyze_ass"]):
                            for ii in self.file_images(i.fileName.get().strip(), 0):
                                if ii not in rs_old  and os.path.exists(ii):
                                    print "get file  form rs"
                                    texture += self.get_files_from_rs(ii )
                                    rs_old.append(i.fileName.get().strip())
        return list(set(texture))
    def get_xgmSplineCache(self):
        texture = []
        texture += [RvPath(i.fileName.get().strip()) for i in pm.ls(type="xgmSplineCache") if i.fileName.get() if
                    i.fileName.get().strip()]
        texture2 = []
        p = re.compile(r'^(?:[a-z][:][\\/]|[\\\\]|(?:\${?))', re.I)
        for i in set(texture):
            if i["exists"] == 0:
                if not p.findall(i["client"]):
                    i2 = RvPath(os.path.dirname(os.path.join(pm.workspace(q=1, fullName=1), i["client"])))
                    if i2["exists"]:
                        texture2.append(i2)

            else:
                texture2.append(i)
    
        return list(set(texture2))
    def get_xgmCurveToSpline(self):
        texture = []
        texture += [RvPath(i.fileName.get().strip()) for i in pm.ls(type="xgmCurveToSpline") if i.fileName.get() if
                    i.fileName.get().strip()]
        texture2 = []
        p = re.compile(r'^(?:[a-z][:][\\/]|[\\\\]|(?:\${?))', re.I)
        for i in set(texture):
            if i["exists"] == 0:
                if not p.findall(i["client"]):
                    i2 = RvPath(os.path.dirname(os.path.join(pm.workspace(q=1, fullName=1), i["client"])))
                    if i2["exists"]:
                        texture2.append(i2)
            else:
                texture2.append(i)
    
        return list(set(texture2))

    def get_single_file_from_sequence(self, sequence):
        files = [i for i in os.listdir(os.path.dirname(sequence))]
        name_pattern = re.findall(r'^(.+?)#+(.+?)$', os.path.basename(sequence), re.I)[0]
        single_file = None
        for i in files:
            if re.findall(r'%s\d+%s' % name_pattern, i, re.I):
                single_file = i
                break

        if single_file:
            return os.path.join(os.path.dirname(sequence), single_file)

    def get_files_from_rs(self,rs_file):
        texture = []
        for line in open(rs_file, "rb"):
            p = re.compile(r'(?:[a-z][:][\\/]|[\\\\]|(?:\.\./)|(?:\.\.\\)){1}[\w _\-.:()\\/$+]+\.[\w]+', re.I)
            r = p.findall(line)
            rs_image = (
            ".rstxbin", ".tga", ".dds", ".jpg", ".png", ".rsmap", ".iff", ".rs", ".exr", ".tiff", ".jpeg", ".hdr",
            ".bmp",".als", ".cin", ".pic", ".rat", ".psd", ".psb", ".ies", ".gif", ".qtl", ".rla", ".rlb", ".pix", ".sgi",
            ".rgb", ".rgba", ".si",".rs",".tif",".tif23",
            ".tif16", ".tx", ".vst", ".yuv", ".ptex", ".tex", ".dpx")
            if r:
                for i in r:
                    if i.lower().endswith(rs_image):
                        if i.startswith(("../", "/../", "\\..\\", "..\\")):
                            
                            i = os.path.normpath(os.path.abspath(os.path.dirname(os.path.abspath(rs_file)) + "\\" + i))
                            
                        texture.append(RvPath(i))
        return texture

    def get_of3d_cache(self):
        texture = []
        texture += [RvPath(i.cachePath.get().strip())
                    for i in pm.ls(type="h5AttribCache")
                    if i.cachePath.get() if i.cachePath.get().strip()]
        texture += [RvPath(i.hesPath.get().strip())
                    for i in pm.ls(type="hesMesh")
                    if i.hesPath.get() if i.hesPath.get().strip()]
        texture += [RvPath(i.cachePath.get().strip())
                    for i in pm.ls(type="opiumBakeP")
                    if i.cachePath.get() if i.cachePath.get().strip()]

        texture2 = []
        for i in set(texture):
            for j in [".m", ".hes", ".h5", ".bm"]:
                texture2.append(RvPath(os.path.splitext(i["client"])[0] + j))

        texture = [RvPath(i.cachePath.get().strip())
                   for i in pm.ls(type="opiumMesh")
                   if i.cachePath.get() if i.cachePath.get().strip()]

        for i in set(texture):
            for j in [".m", ".bm", ".json"]:
                texture2.append(RvPath(os.path.splitext(i["client"])[0] + j))

        return list(set(texture2))

    def get_renderman(self):
        texture = [RvPath(i.Map.get().strip())
                   for i in pm.ls(type="RMSGeoLightBlocker")
                   if i.Map.get() if i.Map.get().strip()]
        texture += [RvPath(i.filename.get().strip())
                    for i in pm.ls(type="PxrTexture")
                    if i.filename.get() if i.filename.get().strip()]
        texture += [RvPath(i.filename.get().strip())
                    for i in pm.ls(type="PxrBump")
                    if i.filename.get() if i.filename.get().strip()]
        texture += [RvPath(i.rman__EnvMap.get().strip())
                    for i in pm.ls(type="PxrStdEnvMapLight")
                    if i.rman__EnvMap.get() if i.rman__EnvMap.get().strip()]
        texture += [RvPath(i.lightColorMap.get().strip())
                    for i in pm.ls(type="PxrDomeLight")
                    if i.lightColorMap.get() if i.lightColorMap.get().strip()]
        texture += [RvPath(i.filename.get().strip())
                    for i in pm.ls(type="PxrNormalMap")
                    if i.filename.get() if i.filename.get().strip()]

        return list(set(texture))

    def get_fur(self):
        texture = [RvPath(i_value)
                   for i_node in pm.ls(type="FurDescription")
                   for i_attr in [u'BaseColorMap',
                                  u'TipColorMap',
                                  u'BaseAmbientColorMap',
                                  u'TipAmbientColorMap',
                                  u'SpecularColorMap',
                                  u'LengthMap',
                                  u'SpecularSharpnessMap',
                                  u'BaldnessMap',
                                  u'BaseOpacityMap',
                                  u'TipOpacityMap',
                                  u'BaseWidthMap',
                                  u'TipWidthMap',
                                  u'SegmentsMap',
                                  u'BaseCurlMap',
                                  u'TipCurlMap',
                                  u'ScraggleMap',
                                  u'ScraggleFrequencyMap',
                                  u'ScraggleCorrelationMap',
                                  u'ClumpingMap',
                                  u'ClumpingFrequencyMap',
                                  u'ClumpShapeMap',
                                  u'InclinationMap',
                                  u'RollMap',
                                  u'PolarMap',
                                  u'AttractionMap',
                                  u'OffsetMap',
                                  u'CustomEqualizerMap']
                   for i_value in i_node.attr(i_attr).get()
                   if i_value if i_value.strip()]

        return list(set(texture))

    def get_particle_cache(self):
        texture = [RvPath(os.path.join(pm.workspace.fileRules.get("particles", "cache/particles"),
                   i.cacheDirectory.get().strip()))
                   for i in pm.ls(type="dynGlobals")
                   if i.cacheDirectory.get() if i.cacheDirectory.get().strip()]

        startup = [RvPath(os.path.join(pm.workspace.fileRules.get("particles", "cache/particles"),
                   i.cacheDirectory.get()+"_startup"))
                   for i in pm.ls(type="dynGlobals")
                   if i.cacheDirectory.get() if i.cacheDirectory.get().strip()]

        for i in startup:
            if i["exists"]:
                texture.append(i)

        return list(set(texture))

    def get_disk_cache(self):
        texture = [RvPath(i.cacheName.get().strip())
                   for i in pm.ls(type="diskCache")
                   if i.cacheName.get() if i.cacheName.get().strip()]

        texture2 = []
        if texture:
            if "diskCache" not in pm.workspace.fileRules.keys():
                writing_error(215)

        for i in texture:
            if i["exists"]:
                texture2.append(i)
            else:
                i2 = RvPath(os.path.join(pm.workspace.fileRules["diskCache"], i["client"]))
                if i2["exists"]:
                    texture2.append(i2)
                else:
                    texture2.append(i)

        return list(set(texture2))

    def get_realflow(self):
        texture = [RvPath(ii) for i in pm.ls(type="SDMeshModifier") if i.path.get() if i.path.get().strip() for ii in
                   self.file_images(i.path.get().strip(), 1)]
        texture += [RvPath(ii) for i in pm.ls(type="RealflowMesh") if i.Path.get() if i.Path.get().strip() for ii in
                    self.file_images(i.Path.get().strip(), 1)]
        return list(set(texture))

    def get_miarmy(self):
        texture = set()
        if pm.ls(type="McdMeshDriveIM"):
            for i in pm.ls(type="McdGlobal"):
                if i.outMD2Folder.get() and i.outMD2Folder.get().strip():
                    if i.outMD2Name.get() and i.outMD2Name.get().strip():
                        if os.path.isdir(i.outMD2Folder.get()):
                            for j in os.listdir(i.outMD2Folder.get()):
                                if j.lower().startswith(i.outMD2Name.get().lower()):
                                    if j.lower().endswith(".mbc") or j.lower().endswith(".mid"):
                                        texture.add(RvPath(os.path.join(i.outMD2Folder.get(), j)))
        elif pm.ls(type="aiStandIn"):
            for i in pm.ls(type="McdGlobal"):
                if i.arProc.get() and os.path.exists(i.arProc.get()):
                    texture.add(RvPath(i.arProc.get()))
                
                if i.outARNm.get() and i.outARFd.get():
                    arnold_files = os.path.join(i.outARFd.get(), i.outARNm.get())
                    if os.path.exists(arnold_files):
                        texture.add(RvPath(arnold_files))

        for i in pm.ls(type="McdGlobal"):
            if i.hasAttr("outputVRFolder"):
                if i.outputVRFolder.get():
                    if i.outputVRName.get():
                        if os.path.isdir(i.outputVRFolder.get()):
                            for files in glob.glob(os.path.join(i.outputVRFolder.get(), i.outputVRName.get() + "*")):
                                texture.add(RvPath(files))
            if i.hasAttr("outputFolder"):
                if i.outputFolder.get():
                    if i.outputRibs.get():
                        if os.path.isdir(i.outputFolder.get()):
                            for files in glob.glob(os.path.join(i.outputFolder.get(), i.outputRibs.get() + "*")):
                                texture.add(RvPath(files))
            
            if i.hasAttr("outputFolder"):
                if i.outputFolder.get():
                    if i.outputPics.get():
                        if os.path.isdir(i.outputFolder.get()):
                            for files in glob.glob(os.path.join(i.outputFolder.get(), i.outputPics.get() + "*")):
                                texture.add(RvPath(files))

            if i.hasAttr("outMD2Folder"):
                if i.outMD2Folder.get() and i.outMD2Folder.get().strip():
                    if i.outMD2Name.get() and i.outMD2Name.get().strip():
                        if os.path.isdir(i.outMD2Folder.get()):
                            for files in glob.glob(os.path.join(i.outMD2Folder.get(), i.outMD2Name.get() +"*")):
                                texture.add(RvPath(files))
          
            
            if i.hasAttr("outputRSFolder"):
                if i.outputRSFolder.get():
                    if i.outputRSName.get():
                        if os.path.isdir(i.outputRSFolder.get()):
                            for files in glob.glob(os.path.join(i.outputRSFolder.get(), i.outputRSName.get() + "*")):
                                texture.add(RvPath(files))

            if i.hasAttr("cacheFolder"):
                if i.cacheFolder.get():
                    if i.cacheName.get():
                        if os.path.isdir(i.cacheFolder.get()):
                            for files in glob.glob(os.path.join(i.cacheFolder.get(), i.cacheName.get() + "*")):
                                texture.add(RvPath(files))

        return list(texture)

    def get_vray(self):
        
        texture = [RvPath(i.fileName.get().strip())
                   for i in pm.ls(type="VRayMtlOSL")
                   if i.fileName.get() if i.fileName.get().strip()]
        
        texture += [RvPath(i.file.get().strip())
                   for i in pm.ls(type="VRayScannedMtl")
                   if i.file.get() if i.file.get().strip()]
        
        texture += [RvPath(i.fileName.get().strip())
                    for i in pm.ls(type="VRayMesh")
                    if i.fileName.get() if i.fileName.get().strip()]

        texture += [RvPath(i.iesFile.get().strip())
                    for i in pm.ls(type="VRayLightIESShape")
                    if i.iesFile.get() if i.iesFile.get().strip()]
        texture += [RvPath(i.iesFile.get().strip())
                    for i in pm.ls(type="VRayLightIESShape")
                    if i.iesFile.get() if i.iesFile.get().strip()]

        vray_settings_attr = ["imap_fileName2",
                              "imap_autoSaveFile2",
                              "pmap_file2",
                              "pmap_autoSaveFile2",
                              "lc_fileName",
                              "lc_autoSaveFile",
                              "shr_file_name",
                              "causticsFile2",
                              "imap_fileName",
                              "imap_autoSaveFile",
                              "pmap_file",
                              "pmap_autoSaveFile",
                              "autoSaveFile",
                              "fileName",
                              "causticsAutoSaveFile",
                              "causticsFile",
                              "shr_file_name"]

        for i in pm.ls(type="VRaySettingsNode"):
            for i_attr in vray_settings_attr:
                if i.hasAttr(i_attr):
                    for i_path in self._get_layer_overrides("%s.%s" % (i, i_attr)):
                        if i_path:
                            if i_path.strip():
                                folder = os.path.dirname(i_path.strip())
                                if os.path.exists(folder):
                                    for ii in os.listdir(folder):
                                        if os.path.isfile(os.path.join(folder, ii)):
                                            if ii.lower().endswith(".vrmap") or ii.lower().endswith(".vrlmap") or ii.lower().endswith(".vrpmap") or ii.lower().endswith(".vrsh"):
                                                texture.append(RvPath(os.path.join(folder, ii)))
        
        
        for i in pm.ls(type="VRayVolumeGrid"):
            path = i.inFile.get()
            if path:
                if path.strip():
                    if "#" in path:
                        texture.append(RvPath(os.path.dirname(path)))
                    else:
                        texture.append(RvPath(path))

        for i in pm.ls(type="VRaySettingsNode"):
            if i.vfbOn.get():
                ''

        return list(set(texture))

    def get_fumefx(self):
        texture = []
        for i in pm.ls(type="ffxDyna"):
            texture.append(i.postprocess_output_path.get())
            texture.append(i.wavelet_output_path.get())
            texture.append(i.output_path.get())
            texture.append(i.illumination_output_path.get())

            # fumeFXShape1.postprocess_output_path E:/fumefx/st-15/sl-15/feipan_pp_.fxd
            # fumeFXShape1.wavelet_output_path E:/fumefx/st-15/sl-15/feipan_wt_.fxd
            # fumeFXShape1.output_path E:/fumefx/st-15/feipan_.fxd
            # fumeFXShape1.illumination_output_path F:/simulation/fumefx/sl-15/feipan_.fim
            # fumeFXShape1.pathIM F:/simulation/fumefx/sl-15/feipan_0200.fim
            # fumeFXShape1.initial_state_path
            # fumeFXShape1.render_output_path E:/fumefx/st-15/feipan_0200.fxd
            # fumeFXShape1.preview_path C:/Users/Administrator/Documents/maya/projects/default/data/fumePreview.avi

        fumefx_path = [i.strip()
                       for i in set([os.path.dirname(j) for j in texture])
                       if i if i.strip()]

        return [RvPath(os.path.join(i_path, i_file))
                for i_path in fumefx_path
                if os.path.exists(i_path)
                for i_file in os.listdir(i_path)]

    def get_fracture(self):
        texture = []
        for i in pm.ls(type="fxWorld"):
            for j in i.take:
                texture.append(j.takeFile.get())

        return [RvPath(i) for i in set(texture) if i if i.strip()]

    def get_marza(self):
        texture = []
        texture += [RvPath(i.abc_File.get().strip())
                    for i in pm.ls(type="mzAlembicNode")
                    if i.abc_File.get() if i.abc_File.get().strip()]

        texture += [RvPath(i.filePath.get().strip())
                    for i in pm.ls(type="mzAbcShape")
                    if i.filePath.get() if i.filePath.get().strip()]

        return list(set(texture))

    def get_golaemcrowd(self):
        texture = []
        if "CrowdEntityTypeNode" in pm.ls(nodeTypes=1):
            texture += [RvPath(i.characterFile.get().strip())
                        for i in pm.ls(type="CrowdEntityTypeNode")
                        if i.characterFile.get() if i.characterFile.get().strip()]

        return list(set(texture))

    def get_alshader(self):
        print "get get_alshader"
        texture = []
        if "alTriplanar" in pm.ls(nodeTypes=1):
            texture += [RvPath(i.texture.get().strip())
                        for i in pm.ls(type="alTriplanar")
                        if i.texture.get() if i.texture.get().strip()]

        return list(set(texture))

    def get_houdini(self):
        texture = []
        for i in pm.ls(type="houdiniAsset"):
            for attr in ["houdiniAssetParm_pointfile",
                         "houdiniAssetParm_file",
                         "otlFilePath","houdiniAssetParm.houdiniAssetParm_Bgeo_Maya_file"]:
                if i.hasAttr(attr):
                    texture.append(RvPath(i.attr(attr).get()))

        texture2 = []
        for i in texture:
            if re.findall(r'.+\$f\d?.+', i["client"], re.I):
                texture2.append(RvPath(os.path.dirname(i["client"])))
            else:
                texture2.append(i)

        return list(set(texture2))

    def get_BossSpectralWave(self):
        self.caches = []
        for i in pm.ls(type="BossSpectralWave"):
            cache_path = []
            object = i.name()
            project = pm.workspace(q=1, fullName=1)
            scene = os.path.basename(pm.system.sceneName()).strip()
            if i.useCache.get():
                cache_folder = i.cacheFolder.get()
                if cache_folder:
                    cache_folder = cache_folder.replace("<project>", project).replace("<scene>", scene).replace("<object>", object)
                self.caches += RvPath(cache_folder)
                
                # cache_name = i.cacheName.get()
                # cache_path.append(os.path.join(cache_folder, cache_name))
                # if i.enableFoam.get():
                #     foamCacheName = i.foamCacheName.get()
                #     cache_path.append(os.path.join(cache_folder, foamCacheName))
                # if i.cacheVelocity.get():
                #     velocityCacheName = i.velocityCacheName.get()
                #     cache_path.append(os.path.join(cache_folder, velocityCacheName))
                # for cp in cache_path:
                #     cp = cp.replace("<project>", project).replace("<scene>", scene).replace("<object>", object)
                #     self.caches += [RvPath(i) for i in self.file_images(cp, 0)]
        return self.caches

    def get_BossWaveSolver(self):
        self.caches = []
        for i in pm.ls(type="BossWaveSolver"):
            cache_path = []
            object = i.name()
            project = pm.workspace(q=1, fullName=1)
            scene = os.path.basename(pm.system.sceneName()).strip()
            if i.useCache.get():
                cache_folder = i.cacheFolder.get()
                if cache_folder:
                    cache_folder = cache_folder.replace("<project>", project).replace("<scene>", scene).replace(
                        "<object>", object)
                self.caches += RvPath(cache_folder)
        return self.caches
    def get_BossGeoProperties(self):
        self.caches = []
        for i in pm.ls(type="BossGeoProperties"):
            cache_path = []
            object = i.name()
            project = pm.workspace(q=1, fullName=1)
            scene = os.path.basename(pm.system.sceneName()).strip()
            if i.useCache.get():
                cache_folder = i.cacheFolder.get()
                if cache_folder:
                    cache_folder = cache_folder.replace("<project>", project).replace("<scene>", scene).replace(
                        "<object>", object)
                self.caches += RvPath(cache_folder)
        return self.caches
    
    
    
    def get_file_form_json(self):
        file_path = os.path.realpath(__file__)
        #print "__file__"
        #print file_path
        currentPath = os.path.dirname(file_path.replace("\\", "/")).split("munu")[0]
        #print currentPath
        node_json_file = r"%s/node_ext.json" % (currentPath)
        
        node_json_dict = json.load(open(node_json_file))
        print node_json_dict

    def get_texture(self):
        print "Getting texture files..."
        node_types = ["mentalrayIblShape", "psdFileTex", "imagePlane",
                      "mentalrayTexture", "aiStandIn",
                      "aiImage", "aiPhotometricLight",
                      "AlembicNode", "mip_binaryproxy", "shaveGlobals",
                      "NBuddyEMPLoader", "ExocortexAlembicXform",
                      "RealflowEmitter",
                      "ExocortexAlembicPolyMeshDeform",
                      "ExocortexAlembicFile", "VRaySettingsNode",
                      "AlembicNodeAB", "vraySettings", "aiVolume",
                      "colorManagementGlobals"]

        register_node_types = pm.ls(nodeTypes=1)
        
        node_types = [i for i in node_types if i in register_node_types]

        attr_names = ["imageName", "filename",
                      "texture", "fileName", "Path", "dso", "aiFilename",
                      "abc_File", "object_filename", "tmpDir", "empInputPath",
                      "Paths[0]",
                      "cacheName", "cfp"]

        nodes = [node_i for type_i in node_types
                 for node_i in pm.ls(type=type_i)]

        textures = []
        for node_i in nodes:
            pprint.pprint(node_i)
            
            for attr_i in attr_names:
                
                if node_i.hasAttr(attr_i):
                    amin_attr = 0
                    if node_i.hasAttr("useFrameExtension") and node_i.useFrameExtension.get():
                        amin_attr =1
                    elif node_i.hasAttr("uvTilingMode") and node_i.uvTilingMode.get():
                        amin_attr = 1
                    else:
                        amin_attr = 0

                    try:
                        file = node_i.attr(attr_i).get().strip()
                        
                    except:
                        file = None
                    
                    if file:
                        pprint.pprint(file)
                        textures += [RvPath(i)["client"] for i in self.file_images(file, amin_attr)]

        print 0
        self.textures = []
        for i in set(textures):
            if i:
                if i.strip():
                    if RvPath(i.strip())["exists"]:
                        self.textures.append(RvPath(i.strip()))
                    elif "." in os.path.basename(RvPath(i.strip())["client"]):
                        self.textures.append(RvPath(i.strip()))

        print "Getting default files..."
        self.textures += self.get_maya_files()
        print_info2("Getting default files...")

        
        

        
        if "McdMeshDriveIM" in register_node_types or "McdGlobal" in register_node_types:
            print_info2("Getting Miarmy files...")
            #print "Getting Miarmy files..."
            self.textures += self.get_miarmy()

        if set(["SDMeshModifier"]) & set(register_node_types):
            print "Getting realflow files..."
            self.textures += self.get_realflow()

        if "dynGlobals" in register_node_types:
            print "Getting particles files..."
            self.textures += self.get_particle_cache()

        
        if "xgmPalette" in register_node_types:
            print_info2("Getting xgen files...")
            self.textures += self.get_xgen()
            print "Getting extra xgen files..."
            self.textures += self.get_xgen2()

        if "pgYetiMaya" in register_node_types:
            print_info2("Getting yeti files...")
            self.textures += self.get_yeti()

        if "ffxDyna" in register_node_types:
            print "Getting fumefx files..."
            self.textures += self.get_fumefx()

        if "aiStandIn" in register_node_types:
            if not int(self.options["dont_analyze_ass"]):
                print "Getting arnold .ass files..."
                self.textures += self.get_ass()

        renderer = pm.PyNode("defaultRenderGlobals").currentRenderer.get()
        if renderer == "redshift":
            print_info2("Getting redshift files...")
            self.textures += self.get_redshift()

        if renderer == "mentalRay":
            print "Getting mentalray files..."
            if not int(self.options["dont_analyze_mi"]):
                print "Getting mentalray .mi files..."
                self.textures += self.get_mi()

            miDefaultOptions = pm.PyNode("miDefaultOptions")
            all_layers = [i for i in pm.PyNode("renderLayerManager").outputs()
                          if i.type() == "renderLayer"
                          if i.renderable.get()]
            for layer in all_layers:
                if layer != layer.currentLayer():
                    layer.setCurrent()
                if miDefaultOptions.hasAttr('photonMapFilename'):
                    photon_map = miDefaultOptions.photonMapFilename.get()
                    if photon_map:
                        self.textures.append(RvPath(photon_map))
                if miDefaultOptions.hasAttr('finalGatherFilename'):
                    final_gather_map = miDefaultOptions.finalGatherFilename.get()
                    if final_gather_map:
                        self.textures.append(RvPath(final_gather_map))
                if miDefaultOptions.hasAttr('finalGatherMergeFiles'):
                    final_merge_maps = miDefaultOptions.finalGatherMergeFiles.get()
                    print final_merge_maps, miDefaultOptions.finalGatherMergeFiles.get()
                    for i in final_merge_maps:
                        if i:
                            self.textures.append(RvPath(i))

        if "h5AttribCache" in register_node_types or \
                "hesMesh" in register_node_types:
            print "Getting h5Cache and hesMesh files..."
            self.textures += self.get_of3d_cache()

        if "taBodyShape" in register_node_types:
            print "Getting glowing files..."
            self.textures += self.get_glowing_files()

        if renderer in ["renderMan", "renderManRIS"]:
            print "Getting renderman files..."
            self.textures += self.get_renderman()

        if "FurDescription" in register_node_types:
            print "Getting maya fur files..."
            self.textures += self.get_fur()

        if "assemblyDefinition" in register_node_types or \
                "assemblyReference" in register_node_types:
            print "Getting maya assembly files..."
            self.textures += self.get_assembly()

        if renderer == "vray":
            print_info2("Getting vray files...")
            self.textures += self.get_vray()

        if "fxWorld" in register_node_types:
            print "Getting fracture files..."
            self.textures += self.get_fracture()

        if "diskCache" in register_node_types:
            print "Getting diskCache files..."
            self.textures += self.get_disk_cache()

        if "houdiniAsset" in register_node_types:
            print "Getting houdini asset..."
            self.textures += self.get_houdini()

        if "xgmSplineCache" in register_node_types:
            print "Getting xgmSplineCache ..."
            self.textures += self.get_xgmSplineCache()

        if "xgmCurveToSpline" in register_node_types:
            print "Getting xgmCurveToSpline ..."
            self.textures += self.get_xgmCurveToSpline()
        
        
        if "BossGeoProperties" in register_node_types:
            print "Getting BossGeoProperties ..."
            self.textures += self.get_BossGeoProperties()
        
        if "BossWaveSolver" in register_node_types:
            print "Getting BossWaveSolver ..."
            self.textures += self.get_BossWaveSolver()
        
        if "BossSpectralWave" in register_node_types:
            print "Getting BossSpectralWave ..."
            self.textures += self.get_BossSpectralWave()

        if int(server_config["user_id"]) == 1818936:
            print "Getting Marza files..."
            self.textures += self.get_marza()
        if int(server_config["user_id"]) == 1813119:
            if "mesh" in register_node_types:
                
                print "Getting mesh ass  files..."
                self.textures += self.get_ass_pixomon()
        

        #print "get_file_form_json ..."
        #self.get_file_form_json()
        #self.textures += self.get_file_form_json()
        self.textures += self.get_alshader()
        self.textures += self.get_golaemcrowd()
        file = []
        folder = []
        print 8
        print 8888
        file = [i for i in self.textures if not i.is_dir()]
        
        folder = [i for i in self.textures if i.is_dir()]

        folder += [RvPath(os.path.dirname(i["client"]))
                   for i in file if "%03d" in i["client"]]

        file = [i for i in file if "%03d" not in i["client"]]

        print 9
        file2 = []
        for i in file:
           

            if re.findall(r'<udim>', i["client"], re.I):
                file2 += self.get_udim_files(i["client"])
            elif re.findall(r'MAPID', i["client"], re.I):
                path = os.path.dirname(i["client"])
                if os.path.exists(path):
                    folder.append(RvPath(path))
            else:
                file2.append(i)
        print 999

        self.textures = file2
        self.textures += [RvPath(os.path.join(root, file))
                          for path in set(folder)
                          for root, dirs, files in os.walk(path["client"])
                          for file in files
                          if re.findall(r'^[\w _\-.:()\\/${}]+$', os.path.join(root, file), re.I)]

        self.textures = [i for i in set(self.textures)  if ".mayaSwatches" not in i["client"]]
        if int(server_config["user_id"]) not in [100001,1840038]:
            print "Getting extra files..."
            self.textures += self.get_extra_postfix_files(".tx")
            self.textures += self.get_extra_postfix_files(".map")
            self.textures += self.get_extra_postfix_files(".rstexbin")
        
        
        
        
        
        print 9999
        if int(server_config["user_id"]) == 1873017:
            print "Getting file form vrscene files..."
            vrscene_list = [i["client"] for i in self.textures if os.path.splitext(i["client"])[1].lower() == ".vrscene" and i["exists"]]
            vrscene_list += [ii for i in vrscene_list if "masterLayer" in i for ii in self.get_file_vrscene(i)]
            vrscene_folder = set([os.path.dirname(i) for i in vrscene_list])
            #vrscene_list += list(set([os.path.join(i, file) for i in vrscene_folder for file in os.listdir(i) if os.path.splitext(file)[1].lower() == ".vrscene"]))
            vrscene_list += list(set([ files for files  in glob.glob(os.path.join(vrscene_folder, "*.vrscene"))]))
            
            
            self.textures += [RvPath(i) for i in vrscene_list]
        if int(server_config["user_id"]) == 1880735:
            print "Getting file form vrscene files..."
            vrscene_list = [i["client"] for i in self.textures if os.path.splitext(i["client"])[1].lower() == ".vrscene" and i["exists"]]
            vrscene_folder = set([os.path.dirname(i) for i in vrscene_list])
            vrscene_list += list(set([ files for files in glob.glob(os.path.join(vrscene_folder, "*.vrscene"))]))
            vrscene_list += [ii for i in vrscene_list for ii in  self.get_file_vrscene(i) ]
            
            self.textures += [RvPath(i) for i in vrscene_list]
       
        #print self.textures
        if int(server_config["user_id"]) in [1840038]:
            print "1840038 dont up tx";
            self.textures = [i for i in self.textures if os.path.splitext(i["client"])[1].lower() != ".tx"]
        
        if int(server_config["user_id"]) in [1865216]:
            dont_up_exr = ['.avi']
            print "1865216 dont up avi"
            
            self.textures = [i for i in self.textures if os.path.splitext(i["client"])[1].lower() not in dont_up_exr ]
        
        print 10

    def get_maya_files(self):
        pprint.pprint("Get file node ...")
        textures = []
        #texture2 = []
        nodes = [node_i for node_i in pm.ls(type="file")]
        for node_i in nodes:
            pprint.pprint("the file node is " + node_i)
            if node_i.hasAttr("useFrameExtension") and node_i.useFrameExtension.get():
                amin_attr = 1
            elif node_i.hasAttr("uvTilingMode") and node_i.uvTilingMode.get():
                amin_attr = 1
            else:
                amin_attr = 0
            if node_i.hasAttr("computedFileTextureNamePattern"):
                file_paths = self._get_layer_overrides("%s.%s" % (node_i, "computedFileTextureNamePattern"))
                for file_path in file_paths:
                    if file_path:
                        textures += [RvPath(i) for i in self.file_images(file_path, amin_attr)]
            if node_i.hasAttr("fileTextureName"):
                file_paths = self._get_layer_overrides("%s.%s" % (node_i, "fileTextureName"))
                for file_path in file_paths:
                    if file_path:
                        textures += [RvPath(i) for i in self.file_images(file_path, amin_attr)]
            
        pprint.pprint("End file node ...")
        return list(set(textures))

    def get_extra_postfix_files(self, postfix):
        return [RvPath(os.path.splitext(i["client"])[0] + postfix)
                for i in self.textures
                if os.path.exists(os.path.splitext(i["client"])[0] + postfix)]

    def get_udim_files(self, udim_path):
    
        p = re.compile(r"<UDIM>", re.I)
        if re.findall(p, udim_path):
            dirName, baseName = os.path.split(udim_path)
            if os.path.exists(dirName) == 1:
                separator = udim_path.replace(dirName, "").replace(baseName, "")
                regex = re.sub(p, "1(?:[0-9][0-9][1-9]|[1-9][1-9]0|0[1-9]0|[1-9]00)", baseName)
                result = [''.join((dirName, separator, f)) for f in os.listdir(dirName) if
                          os.path.isfile(os.path.join(dirName, f)) and re.match(regex, f, flags=re.IGNORECASE)]
                return [RvPath(i) for i in result]
            else:
                return []
        
        
        
        # udim_path = RvPath(udim_path)
        # result = glob.glob('%s.*%s' % (udim_path["client"].split('.')[0],udim_path["client"].split('.')[-1]))

        # result = []
        # if float(pm.about(v=1).split()[0]) >= 2016:
        #     import maya.app.general.fileTexturePathResolver
        #     result = maya.app.general.fileTexturePathResolver.findAllFilesForPattern(udim_path["client"], None)
        #
        # if not result:
        #     folder = RvPath(os.path.dirname(udim_path["client"]))
        #     if os.path.exists(folder["client"]):
        #         for root, dirs, files in os.walk(folder["client"]):
        #             for file_i in files:
        #                 path_i = os.path.join(root, file_i)
        #                 if re.findall(r'^[\w _\-.:()\\/${}]+$', path_i, re.I):
        #                     result.append(path_i)

    def file_images2(self, udim_str, amin_attr=0):
        if os.path.exists(udim_str) == 1 and amin_attr==0:
            yield udim_str
        else:
            p = re.compile(r'^(?:[a-z][:][\\/]|[\\\\]|(?:\${?))', re.I)
            if not p.findall(udim_str):
                udim_str = os.path.join(pm.workspace(q=1, fullName=1), udim_str)
            udim_str = udim_str.replace('\\', '/')
            dir_path, file_name_src = os.path.split(udim_str)
            if os.path.exists(dir_path) == 1:
                separator = udim_str.replace(dir_path, "").replace(file_name_src, "")
                file_name = file_name_src.replace('(', "\(").replace(")", "\)").replace(".", "\.").replace("+", "\+")
                # \%[\d]+[d]   "%05d"
                coms = {'<UDIM>': r"1(?:[0-9][0-9][1-9]|[1-9][1-9]0|0[1-9]0|[1-9]00)", '<F>': r"[\d]+",
                        '\%[\d]+[d]+': r"[\d]+", 'MAPID': r'[\d]+', "<tile>": r"[\d]+", "<uvtile>": r"[\d]+",
                        "\#": r"[\d]+", "<meshitem>": r"[\d]+", "<u>": r"[\d]+", "<v>": r"[\d]+", "<Frame>": r"[\d]+"}
                for comp in coms:
                    file_name = re.sub(re.compile(comp, re.I), coms[comp], file_name)
                if amin_attr:
                    sep_num_re = re.compile(r"[0-9]+(?=[^0-9]*$)", re.I)
                    sep_num = sep_num_re.findall(file_name)
                    if sep_num:
                        file_name = re.sub(sep_num[0], r"[\d]+", file_name)
            
                if file_name == file_name_src:
                    yield udim_str
                else:
                    p2 = re.compile(file_name, re.I)
                    if dir_path in dir_dict:
                        dir_path_file = dir_dict[dir_path]
                    else:
                        dir_path_file = [i for i in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, i))]
                        dir_dict[dir_path] = dir_path_file
                
                    dir_path_file = os.listdir(dir_path)
                    for file_n in dir_path_file:
                        file_path = os.path.join(dir_path, file_n).replace('\\', separator)
                        a = re.findall(p2, file_n)
                        if a:
                            yield os.path.join(dir_path, a[0]).replace('\\', separator)
            else:
                pprint.pprint(udim_str)
                yield udim_str

    def file_images(self, udim_str, amin_attr=0):
        if os.path.exists(udim_str) == 1 and amin_attr == 0:
            yield udim_str
        else:
            p = re.compile(r'^(?:[a-z][:][\\/]|[\\\\]|(?:\${?))', re.I)
            if not p.findall(udim_str):
                udim_str = os.path.join(pm.workspace(q=1, fullName=1), udim_str)
            udim_str = udim_str.replace('\\', '/')
            dir_path, file_name_src = os.path.split(udim_str)
            # print file_name_src
            if os.path.exists(dir_path) == 1:
                separator = udim_str.replace(dir_path, "").replace(file_name_src, "")
                file_name = file_name_src.replace('(', "\(").replace(")", "\)").replace(".", "\.").replace("+", "\+")
                # file_name = file_name_src
                # \%[\d]+[d]   "%05d"
                coms = {'<UDIM>': r"[\d]+", '<F>': r"[\d]+",
                        '\%[\d]+[d]+': r"[\d]+", 'MAPID': r'[\d]+', "<tile>": r"[\d]+", "<uvtile>": r"[\d]+",
                        "\#": r"[\d]+", "<meshitem>": r"[\d]+", "<u>": r"[\d]+", "<v>": r"[\d]+", "<Frame>": r"[\d]+"}
                for comp in coms:
                    file_name = re.sub(re.compile(comp, re.I), coms[comp], file_name)
                if amin_attr:
                    sep_num_re = re.compile(r"[0-9]+(?=[^0-9]*$)", re.I)
                    sep_num = sep_num_re.findall(file_name)
                    if sep_num:
                        file_name = re.sub(sep_num[0], r"[\d]+", file_name)
            
                if file_name == file_name_src:
                    yield udim_str
                else:
                    #print file_name
                    file_name_glob = file_name.replace(r"[\d]+", "[0-9]*").replace("\\", "")
                    #print file_name_glob
                    p2 = re.compile(file_name, re.I)
                    # print glob.glob(os.path.join(dir_path,file_name_glob).replace('\\', separator))
                    for i in glob.glob(os.path.join(dir_path, file_name_glob)):
                        file_name_g = os.path.split(i)[1]
                        # print file_name_g
                        if p2.match(file_name_g):
                            yield i.replace('\\', separator)
                            # yield os.path.join(dir_path, a[0]).replace('\\', separator)
            else:
                pprint.pprint(udim_str)
                yield udim_str

    def _get_layer_overrides(self, attr):
        connections = cmds.listConnections(attr, plugs=True)
        if connections:
            for connection in connections:
                if connection:
                    node_name = connection.split('.')[0]
                    if cmds.nodeType(node_name) == 'renderLayer':
                        attr_name = '%s.value' % '.'.join(connection.split('.')[:-1])
                        yield cmds.getAttr(attr_name)
        else:
            yield cmds.getAttr(attr)

   
    def get_glowing_files(self):
        texture = []
        for i in pm.ls(type="taBodyShape"):
            if i.displayAbc.get():
                if i.displayAbc.get().strip():
                    texture.append(RvPath(i.displayAbc.get().strip()))

            if i.renderAbc.get():
                if i.renderAbc.get().strip():
                    texture.append(RvPath(i.renderAbc.get().strip()))

            if i.materialAbc.get():
                if i.materialAbc.get().strip():
                    mat_file = i.materialAbc.get().strip()
                    texture.append(RvPath(mat_file))

                    texture_folder = os.path.join(os.path.dirname(os.path.dirname(mat_file)), "textures")
                    texture.append(RvPath(texture_folder))

                    if os.path.exists(mat_file):
                        texture += self.get_files_from_mat(mat_file)

        return list(set(texture))

    def get_files_from_mat(self, mat_file):
        texture = []
        for line in open(mat_file, "rb"):
            r = re.findall(r'[a-z][:][\\/][\w _\-.:()\\/$]+\.[\w]+', line, re.I)
            if r:
                for i in r:
                    texture.append(RvPath(i))
        return texture

    def log(self):
        raise Exception(" was terminated for some reason.")

    def get_layer_settings(self, render_layer=None):
        render_settings = pm.PyNode("defaultRenderGlobals")

        if render_layer:
            try:
                pm.PyNode(render_layer).setCurrent()
                self["renderSettings"]["renderableLayer"] = render_layer
                self["renderSettings"]["allLayer"] = ",".join([i.name()
                    for i in pm.PyNode("renderLayerManager").outputs()
                    if i.type() == "renderLayer"])
                self["renderSettings"]["renderableCamera"] = [i.name()
                     for i in pm.ls(type="camera") if i.renderable.get()]
                server_config["renderlayer"] = render_layer
                
                start = int(render_settings.startFrame.get())
                end = int(render_settings.endFrame.get())
                frange = str(start) + "-" + str(end)
                step = render_settings.byFrameStep.get()
                
                self["renderSettings"]["frames"] = frange + "[" + str(int(step)) + "]"
                self["common"]["name"] = os.path.basename(self["common"]["cgFile"])
                self["common"]["name"] += " " + render_layer
                if int(server_config["user_id"]) == 1873017 or int(server_config["user_id"]) == 1880735 :
                    print "the %s delete scene rayvision file" % (server_config["user_id"])
                else:
                    print "dont delete scene rayvision file"
                    self["delete"] = []
            except:
                print traceback.format_exc()
                raise Exception("Can't switch renderlayer " + render_layer)
        else:
            all_layers = [i for i in pm.PyNode("renderLayerManager").outputs()
                          if i.type() == "renderLayer"]
            render_layers = [i for i in all_layers if i.renderable.get()]
            if not render_layers:
                raise Exception("Can't find render layer in render settings.")

            self["renderSettings"]["renderableLayer"] = ",".join([i.name()
                for i in render_layers])
            self["renderSettings"]["allLayer"] = ",".join([i.name()
                for i in all_layers])
#            layer = pm.PyNode(all_layers[0])
#            if layer.currentLayer() not in all_layers:
#                layer.setCurrent()

            
            start, end = None, None
            try:
                # add switch renderlayers check.
                for layer in all_layers:
                    if layer != layer.currentLayer():
                        layer.setCurrent()

                    temp_start = int(render_settings.startFrame.get())
                    temp_end = int(render_settings.endFrame.get())

                    if start:
                        if start > temp_start:
                            start = temp_start
                    else:
                        start = temp_start

                    if end:
                        if end < temp_end:
                            end = temp_end
                    else:
                        end = temp_end
                        
                    if self.options["user_id"] in [964309]:
                        print "user id is 964309 ,the start end is playbackOptions min max"
                        start = int (pm.playbackOptions(q=1,min=1))
                        end = int (pm.playbackOptions(q=1,max=1))
                        
                        
                    self["renderSettings"]["renderableCamera"] += [i.name()
                         for i in pm.ls(type="camera") if i.renderable.get()]

                frange = str(start) + "-" + str(end)
                step = render_settings.byFrameStep.get()
                self["renderSettings"]["frames"] = frange + "[" + str(int(step)) + "]"

            except:
                print traceback.format_exc()
                writing_error(218)
                raise Exception("Can't switch renderlayers.")

            print_info2("switch renderlayer check ok")

        self["common"]["renderer"] = render_settings.currentRenderer.get()
        self["renderSettings"]["usedRenderer"] = render_settings.currentRenderer.get()

        resolution_settings = pm.PyNode("defaultResolution")
        self["renderSettings"]["width"] = resolution_settings.width.get()
        self["renderSettings"]["height"] = resolution_settings.height.get()

        # if render_layer:
        #     start = render_settings.startFrame.get()
        #     end = render_settings.endFrame.get()
        #     frange = str(int(start)) + "-" + str(int(end))
        #     step = render_settings.byFrameStep.get()
        #     self["renderSettings"]["frames"] = frange + "[" + str(int(step)) + "]"


class Frames(list):

    def __init__(self, franges):
        list.__init__(self)
        self.get_frames(franges)

    def get_frames(self, franges):
        if franges:
            for i in [j.replace(" ", "") for j in franges.split(",")]:
                if re.findall("\d+-\d+", i, re.I):
                    self += self.get_frames_from_frange(i)
                else:
                    self.append(int(i.strip()))

            self.sort()

    def get_frames_from_frange(self, frange):
        frange = frange.strip()
        by = 1
        if "[" in frange:
            by = int(re.findall(r'\[(\d+)\]', frange, re.I)[0])
            start, end = [int(i) for i in frange.split("[")[0].split("-")]
        else:
            start, end = re.findall("(-?\d+)-(\d+)", frange, re.I)[0]

        return range(int(start), int(end) + 1, by)


class FileSequence():

    NUMBER_PATTERN = re.compile("([0-9]+)")
    # NUMBER_PATTERN2 = re.compile("([0-9]+)")
    # NUMBER_PATTERN2 = re.compile("(?<=\.)([0-9]+)(?=\.)")
    # NUMBER_PATTERN2 = re.compile("([0-9]+)(?=[\._])")
    NUMBER_PATTERN2 = re.compile("(-?[0-9]+)(?![a-zA-Z\d])")
    PADDING_PATTERN = re.compile("(#+)")

    def __init__(self, path="", head="", tail="", start=0, end=0, padding=0,
                 missing=[]):
        self.path = path.replace("\\", "/")
        self.head = head
        self.tail = tail
        self.start = start
        self.end = end
        self.padding = padding
        self.missing = missing

    def __repr__(self):
        if not self.missing:
#            bb.###.jpg 1-6
            return self.path + "/" + "".join([self.head, self.padding*"#",
                self.tail, " ", str(self.start), "-", str(self.end)])
        else:
#            bb.###.jpg 1-6 (1-3 5-6 mising 4)
            return self.path + "/" + "".join([self.head, self.padding*"#",
                self.tail, " ", str(self.start), "-", str(self.end),
                " ( missing ",
                ",".join([str(i) for i in self.missing]),
                " ) "])

    def __iter__(self):
        def filesequence_iter_generator():
            for frame in range(self.start, self.end+1):
                if frame not in self.missing:
                    yield "".join([self.head, str(frame).zfill(self.padding),
                                   self.tail])
        return filesequence_iter_generator()

    def get_frame_file(self, frame):
        return "".join([self.path, "/", self.head,
                        str(frame).zfill(self.padding), self.tail])

    @classmethod
    def get_from_string(cls, string):
        print string
        re_missing = re.findall("\(missing (.+)\)", string, re.I)
        missing = []
        if re_missing:
            missing = [int(i) for i in re_missing[0].split(",")]

        re_sequence = re.findall("(.+) (\d+-\d+)", string, re.I)
        start, end = [int(i) for i in re_sequence[0][1].split("-")]
        base, tail = os.path.splitext(re_sequence[0][0])
        padding = base.count("#")
        head = os.path.basename(base).split("#")[0]
        path = os.path.dirname(base)
        return FileSequence(path, head, tail, start, end, padding, missing)

    @property
    def name(self):
        return str(self)

    @property
    def fileName(self):
        return os.path.join(self.path, str(self))

    @property
    def readName(self):
        return os.path.join(self.path, "".join([self.head, self.padding*"#", self.tail]))

    @property
    def startFileName(self):
        baseName = "".join([self.head, str(self.start).zfill(self.padding),
                                   self.tail])
        return os.path.join(self.path, baseName)

    @property
    def frames(self):
        return self.end - self.start + 1 - len(self.missing)

    @property
    def frameinfo(self):
        return [frame for frame in range(self.start, self.end+1)
                if frame not in self.missing]

    @property
    def ext(self):
        return self.tail.split('.')[-1].lower()

    @property
    def files(self):
        for filename in iter(self):
            yield os.path.join(self.path, filename)

    @property
    def badframes(self):
        return [frame for frame in range(self.start, self.end+1)
                if frame not in self.missing
                if os.path.getsize(os.path.join(self.path,
                 "".join([self.head, str(frame).zfill(self.padding),
                self.tail]))) < 2000]

    @property
    def blackFrames(self):
        if self.ext in ["tif", "tiff"]:
            blackSize = 129852L
        elif self.ext == "exr":
            blackSize = 320811L
        else:
            blackSize = 0

        if blackSize:
            black = [   frame
                        for frame in range(self.start, self.end+1)
                        if frame not in self.missing
                        if os.path.getsize(os.path.join(self.path,
                         "".join([self.head, str(frame).zfill(self.padding),
                                self.tail]))) == blackSize
                    ]

            if len(black) == self.frames:
                return black
            else:
                if self.start in black:
                    mark = self.start
                    for i in range(self.start, self.end+1):
                        if mark in black:
                            black.remove(mark)
                            mark += 1

                if self.end in black:
                    mark = self.end
                    for i in range(self.start, self.end+1):
                        if mark in black:
                            black.remove(mark)
                            mark -= 1

                return black
        else:
            return []

    @classmethod
    def single_frame_format(cls, single_frame):
        base = os.path.basename(single_frame)
        number = re.findall(r'(0+\d+)', base, re.I)[0]

        single_frame2 = single_frame.replace(number, str(int(number)+1).zfill(len(number)))
        seq, others = FileSequence.find([single_frame, single_frame2])

        return FileSequence(seq[0].path, seq[0].head, seq[0].tail,
                            seq[0].start, seq[0].end-1, seq[0].padding,
                            seq[0].missing)

    @classmethod
    def recursive_find(cls, search_path, sequence=[], ext=None,
                       actual_frange=None):
        if os.path.isdir(search_path):
            sequences, others = cls.find(search_path, ext, actual_frange)
            for i in others:
                if os.path.isdir(os.path.join(search_path, i)):
                    sequences += cls.recursive_find(os.path.join(search_path,
                        i), sequences, ext, actual_frange)

        return sequences

    @classmethod
    def find(cls, search_path, ext=None, actual_frange=None):
        my_sequences, my_others = [], []
        path_group = {}
        if isinstance(search_path, list):
            for i in search_path:
                folder = os.path.dirname(i).replace("\\", "/")
                path_group.setdefault(folder, [])
                path_group[folder].append(os.path.basename(i))

        elif os.path.isdir(search_path):
            path_group = {search_path.replace("\\", "/"): os.listdir(search_path)}

        for i in path_group:
            path_group[i].sort()

        for folder in path_group:
            # directory also add to others, one call of isfile spend 0.001s.
            #                            if os.path.isfile(os.path.join(search_path, i))])
            ext_group = {}
            for i in path_group[folder]:
                ext_group[os.path.splitext(i)[1]] = ext_group.setdefault(os.path.splitext(i)[1], []) + [i]

            sequences, others = {}, []
            for i in ext_group:
                if i:
                    sequences_i, others_i = cls.find_in_list(ext_group[i])
                    sequences.update(sequences_i)
                    others += others_i
                else:
                    others += ext_group[i]

            for i in sequences:
                padding = len(cls.PADDING_PATTERN.findall(i)[0])
                head, tail = i.split(padding*"#")
                start = sequences[i][0]
                end = sequences[i][-1]

                if actual_frange:
                    missing = [frame for frame in Frames(actual_frange)
                               if frame not in sequences[i]]
                else:
                    missing = [frame for frame in range(start, end+1)
                               if frame not in sequences[i]]

                missing = sorted([i for i in set(missing)])

                my_sequences.append(FileSequence(folder, head, tail, start,
                                    end, padding, missing))
            for i in others:
                my_others.append(folder + "/" + i)

        if ext:
            my_sequences = [i for i in my_sequences if i.ext == ext]

        return my_sequences, my_others

    @classmethod
    def find_in_list(cls, files):
        sequence = {}
        others = []
        temp = []

        for index, file in enumerate(files):
            if index != len(files) - 1:
                isSequence = cls.getSequences(file, files[index + 1])
                if isSequence:
                    sequence[isSequence[0]] = sequence.setdefault(isSequence[0],
                                                                  []) + isSequence[1:3]

                    temp += [file, files[index+1]]
                else:
                    others.append(file)
            else:
                others.append(file)

        for i in sequence:
            sequence[i] = sorted(list(set(sequence[i])))
        others = [i for i in others if i not in temp if i.lower() != "thumbs.db"]

        return sequence, others

    @classmethod
    def getSequences(cls, file1, file2):
        # components = [i for i in cls.NUMBER_PATTERN.split(file1) if i]
        components = [i for i in cls.NUMBER_PATTERN2.split(file1) if i]
        numberIndex = dict([(index, i) for index, i in enumerate(components)
                            if cls.NUMBER_PATTERN.findall(i)])
        
        print components, numberIndex
        for i in sorted(numberIndex.keys(), reverse=1):
            r1 = re.findall(r'^(%s)(\d{%s})(%s)$' % ("".join(components[:i]),
                            len(numberIndex[i]), "".join(components[i+1:])),
                            file2)
            r2 = re.findall(r'^(%s)(-{1}\d{%s})(%s)$' % ("".join(components[:i]),
                            len(numberIndex[i]) - 1, "".join(components[i+1:])),
                            file2)
            

            if r1:
                # print r1
                r = r1
            elif r2:
                # print r2
                r = r2
            else:
                r = None

            if r:
                # return ["".join([r[0][0], len(r[0][1])*"#", r[0][2]]),
                #         int(numberIndex[i]), int(r[0][1])]
                return ["".join([r[0][0], len(r[0][1]) * "#", r[0][2]]), int(numberIndex[i]), int(r[0][1])]


class ArnoldNode(dict):

    NUMBER_PATTERN = re.compile(r'[+-]?\d*.?\d*$')

    def __init__(self, type):
        dict.__init__(self)
        self["type"] = type

    def format(self, style="katana"):
        for i in self:
            if i == "type":
                pass
            elif i == "name":
                self[i] = self[i][0]
            else:
                if len(self[i]) == 1:
                    self[i] = self.covert_str_to_real_type(self[i][0])
                else:
                    self[i] = [self.covert_str_to_real_type(j)
                        for j in self[i]]

        if style == "katana":
            self.format_to_katana_type()

    def covert_str_to_real_type(self, s):
        if self.NUMBER_PATTERN.match(s):
            return eval(s)
        elif s == "on":
            return True
        elif s == "off":
            return False
        else:
            return s.strip("\"")

    def format_to_katana_type(self):
        if self["type"] == "MayaFile":
            self["type"] = "image"

        self["parameters"] = {}

        for i in self.keys():
            if i not in ["name", "type", "parameters"]:
                self["parameters"][i] = self[i]
                self.pop(i)

        self["connections"] = {}


class AssFile(list):

    DATE_PATTERN = re.compile("^### exported: +(.+)")
    ARNOLD_PATTERN = re.compile("^### from: +(.+)")
    APP_PATTERN = re.compile("^### host app: +(.+)")
    TYPE_PATTERN = re.compile("^[a-zA-Z].+")

    def __init__(self, ass_file=None, node_list=[]):
        self.is_gzip = 0
        if ass_file:
            if ass_file.endswith(".gz"):
                self.is_gzip = 1

        if node_list:
            self += node_list
            for i in self:
                if "filename" in i:
                    if not i["filename"][0].endswith('"'):
                        i["filename"] = [i["filename"][0] + '"']
        else:
            self.ass_file = ass_file
            self.current_node = {}

            self.get_nodes()

    def get_files_from_ass(self, ass_file=None):
        if ass_file:
            ass_nodes = AssFile(ass_file)
        else:
            ass_nodes = self

        texture = [RvPath(eval(i["filename"][0]), in_ass=1)
                   for i in ass_nodes.filter("MayaFile")]

        texture += [RvPath(eval(i["filename"][0]), in_ass=1)
                    for i in ass_nodes.filter("image")]

        texture += [RvPath(eval(i["filename"][0]), in_ass=1)
                    for i in ass_nodes.filter("procedural")
                    if "filename" in i if eval(i["filename"][0])]
        

        for i in ass_nodes.filter("procedural"):
            if "G_assetsPath" in i:
                if eval(i["G_assetsPath"][0]):
                    
                    texture += [RvPath(eval(i["G_assetsPath"][0]), in_ass=1)]
                    break
        for i in ass_nodes.filter("include"):
                texture += [RvPath(eval(i["include"][0]), in_ass=1)]
                
        ass = list(set([RvPath(eval(i["dso"][0]))
                   for i in ass_nodes.filter("procedural")
                   if "dso" in i if eval(i["dso"][0])]))
        ass += list(set([RvPath(eval(i["filename"][0]))
                   for i in ass_nodes.filter("procedural")
                   if "filename" in i if eval(i["filename"][0]) if eval(i["filename"][0]).lower().endswith(".ass")]))
        ass += list(set([RvPath(eval(i["include"][0]) )
                                for i in ass_nodes.filter("include") if eval(i["include"][0]).lower().endswith(".ass")]))
        
        
        sequences, others = FileSequence.find([i["client"] for i in ass])
        analyze_ass = []
        for i in sequences:
            analyze_ass.append(RvPath(i.startFileName))
        for i in others:
            analyze_ass.append(RvPath(i))

        for i in analyze_ass:
            if i["exists"]:
                texture += self.get_files_from_ass(i["client"])

        return [i for i in set(texture + ass)]

    def get_nodes(self):
        if self.is_gzip:
            open_obj = gzip.open(self.ass_file)
        else:
            open_obj = open(self.ass_file)
        for line in open_obj:
            line = line.strip()
            if line:
                if line.startswith("#"):
                    pass
                elif self.TYPE_PATTERN.findall(line):
                    
                    if self.current_node:
                        group = line.split()
                        
                        if len(group) == 1:
                            pass
                        elif len(group) > 1 and group[1].startswith("\""):
                            self.current_node[group[0]] = [" ".join(group[1:])]
                        else:
                            self.current_node[group[0]] = group[1:]
                    else:
                        line = [i for i in line.split() if i not in ["{", "}"]]
                        
                        if len(line) == 1:
                            
                            self.current_node = ArnoldNode(line[0])
                        else:
                            #print line
                            # procedural { name cube dso "R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCity/Model/Publish/JZZ_PalaceBridgeSETS_mod_LOD150.ass"
                            self.current_node = ArnoldNode(line[0])
                            
                            for index, i in enumerate(line):
                                
                                if index % 2:

                                    if index  < len(line):
                                        
                                        self.current_node[line[index-1]] = [line[index ]]
                            self.append(self.current_node)

                if "}" in line:
                    self.append(self.current_node)
                    #print self.current_node
                    self.current_node = {}

    def filter(self, type):
        #'MayaShadingEngine'
        if type == "shader":
            nodes = [i for i in self if
                i["type"] in ['MayaFile', 'MayaNormalDisplacement',
                'ginstance', 'lambert', 'mayaBump2D',
                'sky', 'standard',] or i["type"].startswith("of_")]
        else:
            nodes = [i for i in self if "type" in i if i["type"] == type]

        if nodes:
            return AssFile(node_list=nodes)
        else:
            return []

    def get_names(self):
        return set([i["name"][0] for i in self])

    def get_types(self):
        return set([i["type"] for i in self])

    def format(self, style="katana"):
        for i in self:
            i.format(style)

        for i in self:
            for j in i["parameters"].keys():
                if i["parameters"][j] in [k["name"] for k in self]:
                    i["connections"][j] = i["parameters"][j]
                    i["parameters"].pop(j)


class RvVersion(list):

    def __init__(self, version):
        list.__init__(self, [int(i) for i in version.split(".")])

    def __lt__(self, obj):
        for i in range(4):
            if self[i] > obj[i]:
                return 0
            elif self[i] < obj[i]:
                return 1
            else:
                pass

        return 0

    def __gt__(self, obj):
        for i in range(4):
            if self[i] > obj[i]:
                return 1
            elif self[i] < obj[i]:
                return 0
            else:
                pass

        return 0

    def __eq__(self, obj):
        if len(self) == len(obj):
            for i in range(len(self)):
                if self[i] != obj[i]:
                    return 0

            return 1
        else:
            return 0


class SqliteDB(object):

    def __init__(self, db_path):
        import sqlite3
        if os.path.exists(db_path):
            print "Found " + db_path
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
        else:
            raise Exception("Can not find: " + db_path.replace("/", "\\"))

    def get_table_list(self, table):
        sql = 'select * from ' + table
        self.execute_sql(sql)
        return self.cursor.fetchall()

    def execute_sql(self, sql):
        self.cursor.execute(sql)

    def close(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    locals, networks, all = RvOs.get_windows_mapping()
    print locals
    print networks
    print all
    #pprint.pprint(RvPath(r'//nas/data/PipePrj/XL/shots/seq007/seq007_shot007/CFX/hair/Main/hair/CHR_MC_LangMing_C019--LangMing_C019_rig_ani9/HairHeadF_hairSystemShape.nhair.abc'))
    #pprint.pprint(RvPath(r'E:\PycharmProjects\udim_test\keke_diffuseColor02_blood_mask.1001.jpg'))
    
    # txt = r"C:\Users\admin\Documents\Tencent Files\386936142\FileRecv\CUT017H_003A_SFGVer001__2016_04_08__00_33.txt"
    # asses = [r"\\hnas01\outrender\DragonNest2_Texture\DragonNest2\Materials\Scene\SSTT_tiejiangpuguangchang\default\s_SSTT_tiejiangpuguangchang._v2015_09_06__18_25_43.pci.mat1.Ass",
    #          "//hnas02/outrender/DragonNest2_farm1/render_cache/2015_09_29/SeqTEST/CUTTEST_TEST/DSORenderFarmTest/CUTTEST_TEST_DSORenderFarmTest_0001.ass",
    #          "//hnas02/outrender/DragonNest2_farm1/render_cache/2015_09_29/SeqTEST/CUTTEST_TEST/DSORenderFarmTest/CUTTEST_TEST_DSORenderFarmTest_0002.ass",
    #          "//hnas02/outrender/DragonNest2_farm1/render_cache/2015_09_29/SeqTEST/CUTTEST_TEST/DSORenderFarmTest/aa.01.ass",
    #          "//hnas02/outrender/DragonNest2_farm1/render_cache/2015_09_29/SeqTEST/CUTTEST_TEST/DSORenderFarmTest/aa.01.ass.gz",
    #          "//hnas02/outrender/DragonNest2_farm1/render_cache/2015_09_29/SeqTEST/CUTTEST_TEST/DSORenderFarmTest/aa.02.ass",
    #          "//hnas02/outrender/DragonNest2_farm1/render_cache/2015_09_29/SeqTEST/CUTTEST_TEST/DSORenderFarmTest/aa.02.ass.gz",
    #          "//hnas02/outrender/DragonNest2_farm1/render_cache/2015_09_29/SeqTEST/CUTTEST_TEST/DSORenderFarmTest/ccc.ass",
    #          r"\\hnas01\outrender\DragonNest2_Texture\DragonNest2\Materials\Scene\SSTT_tiejiangpuguangchang\default\s_SSTT_tiejiangpuguangchang._v2015_09_06__18_25_43.pci.mat.Ass",
    #          "//hnas02/outrender/aaa/render_cache/2015_09_29/SeqTEST/CUTTEST_TEST/DSORenderFarmTest/bbbb_0001.ass",
    #          "//hnas02/outrender/aaa/render_cache/2015_09_29/SeqTEST/CUTTEST_TEST/DSORenderFarmTest/asd.ass",
    #          "//hnas02/outrender/aaa/render_cache/2015_09_29/SeqTEST/CUTTEST_TEST/DSORenderFarmTest/aa",
    #          "//hnas02/outrender/aaa/render_cache/2015_09_29/SeqTEST/CUTTEST_TEST/DSORenderFarmTest/bbbb_0002.ass"]
    #
    # sequences, others = FileSequence.find(asses)
    # pprint.pprint(sequences)
    # pprint.pprint(others)
    # # print [i for i in asses for j in others if j in i]
    #
    # print FileSequence.get_from_string("Z:/ass_ball/ass_ball._####.ass 1-10 (missing 3,6,8)")
    # a = FileSequence.get_from_string("Z:/ass_ball/ass_ball._####.ass 1-10")
    # # RvPath.options = {}
    # print a.get_frame_file(5)
    # print a.startFileName
    # print RvOs.get_windows_mapping()
    #
    # print RvVersion("3.0.1.7") == RvVersion("3.0.1.7")
    # print RvVersion("3.0.1.7") >= RvVersion("3.0.2.8")
    # print RvVersion("3.0.1.7") <= RvVersion("3.0.1.8")

#    os.environ["idmt_projects"] = "//10.50.1.6/d/inputdata8/maya/18000/18445/file-cluster/GDC/Projects"

    # pprint.pprint(RvPath(r'${IDMT_PROJECTS}/ZoomWhiteDolphin/Project/scenes/Animation/episode_128/episode_camera/zm_128_011_cam.ma'))
    #pprint.pprint(RvPath(r'${aaa}/ZoomWhiteDolphin/Project/scenes/Animation/episode_128/episode_camera/zm_128_011_cam.ma'))


#    print "\n"
#    pprint.pprint(RvPath(r'//10.50.1.6/d/inputdata8/maya/18000/18445/file-cluster/GDC/Projects/ZoomWhiteDolphin/Project/scenes/Animation/episode_128/episode_camera/zm_128_011_cam.ma'))
#    print "\n"
#    pprint.pprint(RvPath(r'${IDMT_PROJECTS}/ZoomWhiteDolphin/Project/scenes/props/p576001DivingMaskRico/master/zm_p576001DivingMaskRico_h_ms_render.mb'))
#    print "\n"
#    pprint.pprint(RvPath(r'${IDMT_PROJECTS}/ZoomWhiteDolphin/Project/scenes/props/aaa/master/zm_p576001DivingMaskRico_h_ms_render.mb'))
#    print "\n"

#    server_config["project_custom"] = None
#    server_config["project_in_maya"] = '//10.50.1.6/d/inputdata8/maya/300000/300239/LFX'
#    server_config["project"] = '/uploads/admin/project'
#
    # server_config["project_in_maya"] = 'z:/aa/'
    # pprint.pprint(RvPath('/ve/aa.jpg'))
    # print "\n"

    # server_config["project_in_maya"] = 'z:/'
    # pprint.pprint(RvPath('/ve/aa.jpg'))
    # print "\n"

    # server_config["project_in_maya"] = 'z:'
    # pprint.pprint(RvPath('/ve/aa.jpg'))
    # print "\n"
#    pprint.pprint(RvPath(r'E:/test_files/kt_cartoon_sc002_001_render.mb'))
#    print "\n"
#    pprint.pprint(RvPath(r'E:/LFX//scenes/characters/ch_LFX_zhengyi_bd_final.ma'))
#    print "\n"
#    pprint.pprint(RvPath(r'scenes/characters/ch_LFX_zhengyi_bd_final.ma'))
#    print "\n"
#    pprint.pprint(RvPath(r'//10.50.1.6/d/inputdata8/maya/300000/300239/LFX/sourceimages/enviroments/LFX_s_kuaicandian/4096/LFX_S_CSJD_fanhuaqu_loufang3.tga'))
#    print "\n"
#
#    pprint.pprint(RvPath(r'//192.168.0.88/3dsoft/temp/aaa.mb'))
#    print "\n"
#
#    pprint.pprint(RvPath(r'z:/aaa.mb'))
#    print "\n"
#
#    pprint.pprint(RvPath(r'//10.50.1.6/d/inputdata8/maya/300000/300246/Z\zslm_local\boShiZhanYiCunFangChu_Tex_Light_v017.ma'))
#    print "\n"
#
#
#    pprint.pprint(RvPath(r'Z:\zslm_local\boShiZhanYiCunFangChu_Tex_Light_v017.ma'))
#    print "\n"
#
#    pprint.pprint(RvPath(r'Z:\zslm_local\boShiZhanYiCunFangChu_Tex_Light_v017.ma'))
#    print "\n"
#
#
#    pprint.pprint(RvPath(r'E:\test_files\boShiZhanYiCunFangChu_Tex_Light_v017.ma'))
#    print "\n"
#
#    pprint.pprint(RvPath(r'E:\test_files\ball.mb'))
#    print "\n"
#
#    pprint.pprint(RvPath(r'E:\work\test\shave8.0v06_mtoa1.0.0.1_maya2013.ma'))
#    print "\n"
#
#
#     server_config["project_in_maya"] = 'C:/google drive_first/Special/Special topic/maya/corridor(first)'
#     # a = RvPath(r'E:\test_files\ball.mb')
#     a = RvPath(r'corridor_first.fgmap')
#     pprint.pprint(a)
#     print a.server_long_path
#
#     a = RvPath(r'C:\Users\admin\Desktop\aaa')
#     pprint.pprint(a)
# #    print a.server_long_path
#
# #    a = RvPath(r'\\192.168.0.88\test\customer\2014_ball.ma')
# #    pprint.pprint(a)
# #    print a.server_long_path
#
#     print Frames(" 5, 7, 1 - 4, 10-20[2]")
#     print Frames(" 5, 7, 1 - 4wode, 10-20[2]")
#     print Frames("")
#     print Frames(None)
#
#     a = u"�ҵ�gb18030".encode("gb18030")
#     b = u"�ҵ�utf-8".encode("utf-8")
#     c = u"�ҵ�unicode"
#
#     print RvOs.str_to_unicode(a).encode("gb18030")
#     print RvOs.str_to_unicode(b).encode("gb18030")
#     print RvOs.str_to_unicode(c).encode("gb18030")
#
#     print RvOs.str_to_unicode(a).encode("utf-8")
#     print RvOs.str_to_unicode(b).encode("utf-8")
#     print RvOs.str_to_unicode(c).encode("utf-8")
#    a = RvPath(r'Z:\customer\test\2015_ball.mb')
#    pprint.pprint(a)
#    print a.server_long_path
#
#    pprint.pprint(server_config)
#
    # for i in FileSequence.find(r'D:\test\default\sourceimages'):
    #     print i

    # ass = AssFile(r'C:\Users\admin\Documents\Tencent Files\386936142\FileRecv\Agent58\Agent58\stdin.1001.ass.gz')
    # print ass
    # ass = AssFile(r'C:\Users\admin\Documents\Tencent Files\386936142\FileRecv\Agent58\Agent58\stdin.1001.ass2.gz')
    # print ass
    # ass = AssFile(r'C:\Users\admin\Documents\Tencent Files\386936142\FileRecv\Agent58\Agent58\stdin.1001.ass1.gz')
    # print ass
    # for i in ass:
    #     if "name" in i:
    #         print i["name"], i["type"]
    # pprint.pprint(ass.filter("MayaFile"))
    # pprint.pprint(ass.get_files_from_ass())

    # ass = AssFile(r'F:\of3d\aaa.ass')
    # for i in ass:
    #     print i

    # ass = AssFile(r'E:\\gdc\\test_del\\mk_sShuF_h_tx.ass')
    # for i in ass.filter("MayaFile"):
    #     print i
    # for i in ass.filter("mayaBump2D"):
    #     print i
    # print len(ass.get_files_from_ass())
    # pprint.pprint(ass.get_files_from_ass())
    # print ass.get_nodes()

    # a = RvPath(r'P:/Suvival/data/BG/Main/Shading/Road_type_a/proxy/_pr_tree_bb_sb_bt_pr_tree_bb_sb_bt.vrmesh')
    # b = RvPath(r'P:/Suvival/')
    # print b in a
    # # print len(a)
    # # print len(b)
    #
    # a = cPickle.load(open(r"D:\test\original", "rb"))
    # print len(a)
    
    # c = MayaTask.ignore_child_path(a)
    # print len(c)
    # for i in a:
    #     if i.is_dir():
    #         print i
    # b = cPickle.load(open(r"D:\test\sort", "rb"))
    # print len(b)
    # c = cPickle.load(open(r"D:\test\ignore", "rb"))
    # print len(c)
    # a1 = set([i["client"] for i in a if ".ma" in i["client"]])
    # c1 = set([i["client"] for i in c if ".ma" in i["client"]])
    #
    # for i in (a1 - c1):
    #     print i
    # for i in a:
    #     if ".ma" in i["client"]:
    #         print i["client"]
    # a = 'Z:/Projects/DH2/shot_work/Resolve/05/SHOT06/Cache/DH2_05_SHOT06_Ani_/'
    # b = 'Z:/Projects/DH2/shot_work/Resolve/05/SHOT06/Cache/DH2_05_SHOT06_Ani_/cloth/'
    # def length_cmp(a, b): return len(a) >= len(b)
    # def length_cmp(a, b): return cmp(len(a), len(b))
    # print sorted([b, a], key=lambda x: len(x), reverse=1)
    # print sorted([a, b], key=lambda x: len(x))
    # print length_cmp(a, b)
    # print length_cmp(b, a)
    # pprint.pprint(MayaTask.ignore_child_path(c))
    # ass = AssFile(r'F:\of3d\aa.ass')
    # for i in ass:
    #     print i

    #     if "name" in i:
    #         print i["name"], i["type"]
    # pprint.pprint(ass.filter("MayaFile"))
    # pprint.pprint(ass.get_files_from_ass())

    # ass = AssFile(r'F:\of3d\aa2.ass')
    # for i in ass:
    #     if "name" in i:
    #         print i["name"], i["type"]
    # pprint.pprint(ass.filter("MayaFile"))
    # pprint.pprint(ass.get_files_from_ass())

    # a = [u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCity/Model/Publish/JZZ_BingYingDanTi_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCity/Model/Publish/JZZ_HuangGongDanTi_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCity/Model/Publish/JZZ_JunPalace_mod_LOD250.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCity/Model/Publish/JZZ_PalaceBridgeSETS_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCity/Model/Publish/JZZ_SkyCityDoubleTower_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCity/Model/Publish/JZZ_SkyCityHuangCheng_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCity/Model/Publish/JZZ_SkyCityMainBuilding_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCity/Model/Publish/JZZ_SkyCtiyBridgeSupport_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCity/Model/Publish/JZZ_SkyCtiyHeroPillarsA_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCity/Model/Publish/JZZ_SkyCtiyHeroPillarsB_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityBlockA/Model/Publish/SkyCityBlockA_Night_mod_LOD250.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityBlockB/Model/Publish/SkyCityBlockB_Night_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityBlockE/Model/Publish/SkyCityBlockE_Night_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityBlockG/Model/Publish/SkyCityBlockG_Night_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityBlockK/Model/Publish/SkyCityBlockK_night_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityDownTownBlockA/Model/Publish/SkyCityDownTownBlockA_night_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityDownTownBlockB/Model/Publish/JZZ_SkyCityBlockB_night_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityDownTownBlockC/Model/Publish/JZZ_SkyCityBlockC_Night_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityDownTownBlockD/Model/Publish/JZZ_SkyCityBlockD_Night_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityDownTownBlockE/Model/Publish/SkyCityDownTownBlockE_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityShangChengQu/Model/Publish/JZZ_ShangChengQu1HaoLou_mod_LOD150.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityShangChengQu/Model/Publish/JZZ_ShangChengQu3HaoLou_mod_LOD150.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityShangChengQu/Model/Publish/JZZ_ShangChengQuDuZhuangDanTi4_mod_LOD150.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityTree/Model/Publish/JZZ_SkyCityTreeA_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityTree/Model/Publish/JZZ_SkyCityTreeC_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityTree/Model/Publish/JZZ_SkyCityTreeD_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityTree/Model/Publish/JZZ_SkyCityTreeE_mod_LOD050.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityXiaChengQu/Model/Publish/JZZ_XiaChengQu10HaoLou_mod_LOD150.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityXiaChengQu/Model/Publish/JZZ_XiaChengQu1HaoLou_mod_LOD150.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityXiaChengQu/Model/Publish/JZZ_XiaChengQuBj01_mod_LOD.150.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityXiaChengQu/Model/Publish/JZZ_XiaChengQuBj01_mod_LOD.151.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/assets/CGassets/Sets/SkyCityXiaChengQu/Model/Publish/JZZ_XiaChengQuBj04_mod_LOD150.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/sequences/SC036/XL_0036_0020/CG/effects/work/shijiu/cache/JZZ_XL0036_020_fx_crowd_adrew_v015/JZZ_XL0036_020_fx_crowd_adrew_v015/assStandin/assStandin.0993.ass',
    #     u'R:/filmServe/1019_JA_JZZ/VFX/sequences/SC036/XL_0036_0020/CG/effects/work/shijiu/cache/JZZ_XL0036_020_fx_crowd_adrew_v015/JZZ_XL0036_020_fx_crowd_adrew_v015/assStandin/assStandin.0994.ass']
    #
    # sequences, others = FileSequence.find([i for i in a])
    # print len(a)
    # print sequences
    # print len(others)
    #
    # a = ErrorJson(r"e:\result.json")
    # print a.keys()
    #
    # for line in open(r"C:\Users\admin\Desktop\stereoCameraLeft\aaa.mat", "rb"):
    #     r = re.findall(r'[a-z][:][\\/][\w _\-.:()\\/$]+\.[\w]+', line, re.I)
    #     if r:
    #         print r
    ass = AssFile(r'E:\\gdc\\test_del\\shu.ass')
    for i in ass.get_files_from_ass():
        print i