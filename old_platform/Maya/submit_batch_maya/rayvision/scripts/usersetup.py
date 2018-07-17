#! /usr/bin/env python
# coding=utf-8
import pymel.core as pm
import pymel.all as pa
import os
import sys


def get_app_config():
    env_ini = os.path.join(os.environ["appdata"], r"RenderBus\local\env.ini")
    config = open(env_ini).readlines()
    config = dict([[j.strip() for j in i.split("=")] for i in config if "=" in i])
    return config


def get_app_platform_number():
    return get_app_config()["platform"]


def install_rayvision_menu():
    if "MayaWindow|Rayvision" not in pm.lsUI(type="menu"):
        pm.menu("Rayvision", parent='MayaWindow')
        pm.menuItem("SubmitMayaRenderTask",
                    command="execfile(r\"%s\")" % (submit_maya_py))

munu_path = os.path.join(os.environ["appdata"], r"RenderBus\%s\Module\script\submit_batch_maya" % (get_app_platform_number()))
sys.path.append(munu_path)
submit_maya_py = os.path.join(munu_path, r"rayvision\submit_maya.py")
pa.mayautils.executeDeferred(install_rayvision_menu)
