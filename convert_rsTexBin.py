# -*- coding: utf-8 -*-
# by rongjie


def convertTexturesToRedshift(forced):
    import maya.cmds as cmds
    import os

    redshitTextureProcessor = os.getenv("REDSHIFT_COREDATAPATH") + "/bin/redshiftTextureProcessor"

    # find the files
    all_material_list = cmds.ls(materials=True)
    textures_list = cmds.ls(type="file")
    domeLights_list = cmds.ls(type="RedshiftDomeLight")
    normalMaps_list = cmds.ls(type="RedshiftNormalMap")
    environments_list = cmds.ls(type="RedshiftEnvironment")
    lensDistortions_list = cmds.ls(type="RedshiftLensDistortion")
    sprites_list = cmds.ls(type="RedshiftSprite")
    numberOfNodes = len(textures_list) + len(domeLights_list) + len(normalMaps_list) + len(environments_list) # + len(sprites_list) + len(lensDistortions_list)

    if forced == 1:
        print "Forced Conversion of " + str(numberOfNodes) + " nodes\n"
    else:
        print "Skipped Conversion of " + str(numberOfNodes) + " nodes\n"

    # file textures
    for each in textures_list:
        if not each:
            continue
        fileName = cmds.getAttr(each + ".ftn")
        colorSpace = cmds.getAttr(each + ".colorProfile")
        if cmds.listConnections(each + '.repeatUV', s=True, d=False):
            place2d = cmds.listConnections(each + '.repeatUV', s=True, d=False)[0]
            repeatU = cmds.getAttr(place2d + '.repeatU')
            repeatV = cmds.getAttr(place2d + '.repeatV')
        else:
            repeatU = 1
            repeatV = 1

        if repeatU != 1:
            repeatU_str = " -wx"
        else:
            repeatU_str = ""

        if repeatV != 1:
            repeatV_str = " -wy"
        else:
            repeatV_str = ""

        # about color and weight
        if cmds.listConnections(each, s=False, d=True, c=True):
            des_node_list = zip(cmds.listConnections(each, s=False, d=True, c=True)[::2],
                                cmds.listConnections(each, s=False, d=True, c=True)[1::2])
            for des_node in des_node_list:

                if des_node[1] in all_material_list or (cmds.nodeType(des_node[1]) == 'multiplyDivide'):
                    if des_node[0].rsplit('.', 1)[1] == 'outColor':
                        # force_str = " -s"
                        if colorSpace not in [2, 4]:
                            if forced == 1:
                                print "Converting " + fileName + " to sRGB space\n"
                                os.system(
                                    redshitTextureProcessor + " " + fileName + " -s -noskip" + repeatU_str + repeatV_str + "\n")
                            else:
                                print "Converting " + fileName + " to sRGB space\n"
                                os.system(
                                    redshitTextureProcessor + " " + fileName + " -s" + repeatU_str + repeatV_str + " \n")
                        else:
                            if forced == 1:
                                print "Converting " + fileName + " to linear space\n"
                                os.system(
                                    redshitTextureProcessor + " " + fileName + " -l -noskip" + repeatU_str + repeatV_str + "\n")
                            else:
                                print "Converting " + fileName + " to linear space\n"
                                os.system(
                                    redshitTextureProcessor + " " + fileName + " -l" + repeatU_str + repeatV_str + " \n")
                    else:
                        if colorSpace not in [3]:
                            # force_str = " -l"
                            if forced == 1:
                                print "Converting " + fileName + " to linear space\n"
                                os.system(
                                    redshitTextureProcessor + " " + fileName + " -l -noskip" + repeatU_str + repeatV_str + "\n")
                            else:
                                print "Converting " + fileName + " to linear space\n"
                                os.system(
                                    redshitTextureProcessor + " " + fileName + " -l" + repeatU_str + repeatV_str + " \n")
                        else:
                            # force_str = " -l"
                            if forced == 1:
                                print "Converting " + fileName + " to sRGB space\n"
                                os.system(
                                    redshitTextureProcessor + " " + fileName + " -s -noskip" + repeatU_str + repeatV_str + "\n")
                            else:
                                print "Converting " + fileName + " to sRGB space\n"
                                os.system(
                                    redshitTextureProcessor + " " + fileName + " -s" + repeatU_str + repeatV_str + " \n")

    # domelight maps are always linear
    for domeLight in domeLights_list:
        domeLightName = cmds.getAttr(domeLight + ".tex0")
        backPlateName = cmds.getAttr(domeLight + ".tex1")
        if os.path.exists(domeLightName):
            domeLight_srgb = cmds.getAttr(domeLight + ".srgbToLinear0")
            if domeLight_srgb == 0:
                if forced == 1:
                    print ("Converting " + domeLightName + " to original space\n")
                    os.system(redshitTextureProcessor + " " + domeLightName + " -isphere -l -noskip\n")
                else:
                    print ("Converting " + domeLightName + " to original space\n")
                    os.system(redshitTextureProcessor + " " + domeLightName + " -isphere -l\n")
            else:
                if forced == 1:
                    print ("Converting " + domeLightName + " to original space\n")
                    os.system(redshitTextureProcessor + " " + domeLightName + " -isphere -s -noskip\n")
                else:
                    print ("Converting " + domeLightName + " to original space\n")
                    os.system(redshitTextureProcessor + " " + domeLightName + " -isphere -s\n")
        if backPlateName and os.path.exists(backPlateName):
            backPlate_srgb = cmds.getAttr(domeLight + ".srgbToLinear1")
            if backPlate_srgb == 0:
                if forced == 1:
                    print ("Converting " + backPlateName + " to original space\n")
                    os.system(redshitTextureProcessor + " " + backPlateName + " -isphere -l -noskip\n")
                else:
                    print ("Converting " + backPlateName + " to original space\n")
                    os.system(redshitTextureProcessor + " " + backPlateName + " -isphere -l\n")
            else:
                if forced == 1:
                    print ("Converting " + backPlateName + " to original space\n")
                    os.system(redshitTextureProcessor + " " + backPlateName + " -isphere -s -noskip\n")
                else:
                    print ("Converting " + backPlateName + " to original space\n")
                    os.system(redshitTextureProcessor + " " + backPlateName + " -isphere -s\n")

    # environments are usually linear
    for environment in environments_list:
        environmentMapName = cmds.getAttr(environment + ".tex0")
        environmentBackPlateName = cmds.getAttr(environment + ".tex1")
        if os.path.exists(environmentMapName):
            env_srgb = cmds.getAttr(environment + ".srgbToLinear0")
            if env_srgb == 0:
                if forced == 1:
                    print ("Converting " + environmentMapName + " to original space\n")
                    os.system(redshitTextureProcessor + " " + environmentMapName + " -l -noskip\n")
                else:
                    print ("Converting " + environmentMapName + " to original space\n")
                    os.system(redshitTextureProcessor + " " + environmentMapName + " -l\n")
            else:
                if forced == 1:
                    print ("Converting " + environmentMapName + " to original space\n")
                    os.system(redshitTextureProcessor + " " + environmentMapName + " -s -noskip\n")
                else:
                    print ("Converting " + environmentMapName + " to original space\n")
                    os.system(redshitTextureProcessor + " " + environmentMapName + " -s\n")

        if environmentBackPlateName and os.path.exists(environmentBackPlateName):
            env_srgb = cmds.getAttr(environment + ".srgbToLinear1")
            if env_srgb == 0:
                if forced == 1:
                    print ("Converting " + environmentBackPlateName + " to original space\n")
                    os.system(redshitTextureProcessor + " " + environmentBackPlateName + " -l -noskip\n")
                else:
                    print ("Converting " + environmentBackPlateName + " to original space\n")
                    os.system(redshitTextureProcessor + " " + environmentBackPlateName + " -l\n")
            else:
                if forced == 1:
                    print ("Converting " + environmentBackPlateName + " to original space\n")
                    os.system(redshitTextureProcessor + " " + environmentBackPlateName + " -s -noskip\n")
                else:
                    print ("Converting " + environmentBackPlateName + " to original space\n")
                    os.system(redshitTextureProcessor + " " + environmentBackPlateName + " -s\n")

    # normal maps are always linear
    for normalMap in normalMaps_list:
        normalMapName = cmds.getAttr(normalMap + ".tex0")
        if os.path.exists(normalMapName):
            if forced == 1:
                print ("Converting " + normalMapName + " to linear space\n")
                os.system(redshitTextureProcessor + " " + normalMapName + " -l -noskip\n")
            else:
                print ("Converting " + normalMapName + " to linear space\n")
                os.system(redshitTextureProcessor + " " + normalMapName + " -l\n")

    # # sprite textures as original color space otherwise it interferes with the sprite color settings
    # for sprite in sprites_list:
    #     spriteName = cmds.getAttr(sprite + ".tex0")
    #     if os.path.exists(spriteName):
    #         if forced == 1:
    #             print ("Converting " + spriteName + " using its original space\n")
    #             os.system(redshitTextureProcessor + " " + spriteName + " -ocolor -l -noskip\n")
    #         else:
    #             print ("Converting " + spriteName + " using it's original space\n")
    #             os.system(redshitTextureProcessor + " " + spriteName + " -ocolor -l\n")

    # # lens distortion images as original color space otherwise it interferes with the distortion image color settings
    # for lensDistortion in lensDistortions_list:
    #     lensDistortionName = cmds.getAttr(lensDistortion + ".LDimage")
    #     if os.path.exists(lensDistortionName):
    #         if forced == 1:
    #             print ("Converting " + lensDistortionName + " using it's original space\n")
    #             os.system(redshitTextureProcessor + " " + lensDistortionName + " -ocolor -l -noskip\n")
    #         else:
    #             print ("Converting " + lensDistortionName + " using it's original space\n")
    #             os.system(redshitTextureProcessor + " " + lensDistortionName + " -ocolor -l\n")

    print 'final!'

convertTexturesToRedshift(1)