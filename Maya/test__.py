
import os
import math


idex1 = 6.5
idex2 = 6.8
idex3 = 8.5
idex4 = 11.5
idex5 = 14
idex6 = 36
idex7 = 21
idex8 = 26
idex9 = 66
idex10 = 211
idex11 = 12.5
idex12 = 8.3
idex13 = 21
idex14 = 121
idex15 = 351
idex16 = 17
idex17 = 46
idex18 = 21
idex19 = 161
idex20 = 81
idex21 = 81
idex22 = 351
idex23 = 351
idex24 = 351
idex25 = 351

count_money = 0

count_index = 0


for i in range(1,25):
    i_index = 'title' + i
    i_index = 1
    idex_name = 'idex'+i
    globals()[idex_name]
    count_money += idex_name*i_index

for i in range(1, 25):

    idex_name = 'idex'+i
    globals()[idex_name]


    idex_name * i_index > count_money

import pymel.core as pm
import maya.cmds as cmds
import os
import random

te_path = r'c:/maps'
te_names = os.listdir(te_path)

objs = cmds.ls(sl=1)
for obj in objs:
    print obj
    sdnode = cmds.shadingNode("blinn", asShader=1)
    filenode = cmds.shadingNode('file', asTexture=1)
    ptnode = cmds.shadingNode('place2dTexture', asUtility=1)
    cmds.select(obj)
    cmds.hyperShade(assign=sdnode)
    pm.connectAttr(ptnode + ".coverage", filenode + ".coverage")

    pm.connectAttr(ptnode + ".translateFrame", filenode + ".translateFrame")

    pm.connectAttr(ptnode + ".rotateFrame", filenode + ".rotateFrame")

    pm.connectAttr(ptnode + ".mirrorU", filenode + ".mirrorU")

    pm.connectAttr(ptnode + ".mirrorV", filenode + ".mirrorV")

    pm.connectAttr(ptnode + ".stagger", filenode + ".stagger")

    pm.connectAttr(ptnode + ".wrapU", filenode + ".wrapU")

    pm.connectAttr(ptnode + ".wrapV", filenode + ".wrapV")

    pm.connectAttr(ptnode + ".repeatUV", filenode + ".repeatUV")

    pm.connectAttr(ptnode + ".offset", filenode + ".offset")

    pm.connectAttr(ptnode + ".rotateUV", filenode + ".rotateUV")

    pm.connectAttr(ptnode + ".noiseUV", filenode + ".noiseUV")

    pm.connectAttr(ptnode + ".vertexUvOne", filenode + ".vertexUvOne")

    pm.connectAttr(ptnode + ".vertexUvTwo", filenode + ".vertexUvTwo")

    pm.connectAttr(ptnode + ".vertexUvThree", filenode + ".vertexUvThree")
    pm.connectAttr(ptnode + ".vertexCameraOne", filenode + ".vertexCameraOne")
    pm.connectAttr(ptnode + ".outUV", filenode + ".uv")
    pm.connectAttr(ptnode + ".outUvFilterSize", filenode + ".uvFilterSize")
    pm.connectAttr(filenode + ".outColor", sdnode + ".color")

    path = te_path + te_names[int(random.uniform(1, len(te_names)))]
    cmds.setAttr((filenode + ".fileTextureName"), path, type="string")

