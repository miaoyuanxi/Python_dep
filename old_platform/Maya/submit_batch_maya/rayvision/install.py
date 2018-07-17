#! /usr/bin/env python
# coding=utf-8
import os
import sys


def get_documents():
    import ctypes
    from ctypes.wintypes import MAX_PATH

    dll = ctypes.windll.shell32
    buf = ctypes.create_unicode_buffer(MAX_PATH + 1)
    if dll.SHGetSpecialFolderPathW(None, buf, 0x0005, False):
        return buf.value
    else:
        return os.path.join(os.environ["userprofile"], "Documents")


def get_maya_mod_path():
    mod_path = os.path.join(get_documents(), "maya", "modules")
    if not os.path.exists(mod_path):
        os.makedirs(mod_path)
    return mod_path


def get_maya_documents():
    documet_path = os.path.join(get_documents(), "maya", "scripts")
    rayvision_path = os.path.join(documet_path, "Rayvision")
    if not os.path.exists(documet_path):
        os.makedirs(documet_path)
    if not os.path.exists(rayvision_path):
        os.makedirs(rayvision_path)
    return documet_path


def get_app_config():
    env_ini = os.path.join(os.environ["appdata"], r"RenderBus\local\env.ini")
    config = open(env_ini).readlines()
    config = dict([[j.strip() for j in i.split("=")] for i in config if "=" in i])
    return config


def get_app_platform_number():
    return get_app_config()["platform"]


def write_mod_file():
    info = "+ rayvision any %sappdata%s\\RenderBus\\%s\\Module\\script\\submit_batch_maya\\rayvision" % ("%", "%", get_app_platform_number())
    mod_path = get_maya_mod_path()
    with open(os.path.join(mod_path, "rayvision.mod"), "w") as f:
        f.write(info)

if __name__ == '__main__':
    write_mod_file()
    sys.exit(0)
