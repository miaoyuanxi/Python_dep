#! /usr/bin/env python
# coding=utf-8
# Author: Liu Qiang
# Tel:    13811571784
# QQ:     386939142

import pymel.core as pm
import pymel.all as pa


def install_rayvision():
    if "MayaWindow|Rayvision" not in pm.lsUI(type="menu"):
        pm.menu("Rayvision", parent='MayaWindow')
        pm.menuItem("SubmitMayaRenderTask",
                    command="import Rayvision.submit_maya;Rayvision.submit_maya.submit_maya()")

pa.mayautils.executeDeferred(install_rayvision)
