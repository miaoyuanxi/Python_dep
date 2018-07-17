#!/usr/bin/env python
# encoding:utf-8
# -*- coding: utf-8 -*-
# -----M20180321-----
# 2017/9/21-16:27-2017
# "C:\Program Files\Autodesk\Maya2014\bin\mayapy.exe" E:\PycharmProjects\work\test_del\an_maya.py --ui "123" --ti "456" --proj "E:\fang\fagng" --cgfile "E:\fang\fagng\scenes\pre_test_2014.mb" --taskjson "d:\task.json"
# "C:/Program Files/Autodesk/maya2014/bin/mayabatch.exe" -command "python \"options={'cg_file': 'E:/fang/fagng/scenes/pre_test_2014.mb', 'user_id': 123, 'cg_project': 'E:/fang/fagng', 'task_id': 456, 'task_json': 'd:/task.json'};import sys;sys.path.insert(0, 'E:/PycharmProjects/work/test_del');from an_maya import *;analyze = maya_an(options);analyze.run();analyze.write_info_file();\""


import os
import re
import sys
import json
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
import argparse
import collections

if os.path.basename(sys.executable.lower()) in ["mayabatch.exe", "maya.exe"]:
    import pymel.core as pm
    import maya.cmds as cmds
    import maya.mel as mel


class Maya(object):
    def __init__(self):
        pass

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

    def write_file(self, file_content, my_file, my_code='UTF-8', my_mode='w'):

        if isinstance(file_content, str):
            file_content_u = self.bytes_to_str(file_content)
            fl = codecs.open(my_file, my_mode, my_code)
            fl.write(file_content_u)
            fl.close()
            return True
        elif isinstance(file_content, (list, tuple)):
            fl = codecs.open(my_file, my_mode, my_code)
            for line in file_content:
                fl.write(line + '\r\n')
            fl.close()
            return True
        else:
            return False

    def encode_str(self, my_str):
        if my_str:
            my_str = my_str.encode('unicode-escape').decode('string_escape')
        else:
            my_str = str(None)
        print (my_str)
        return my_str

    def unicode_to_str(self, str1, str_encode='system'):
        if isinstance(str1, unicode):
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
                print ('[err]unicode_to_str:encode %s to %s failed' % (str1, str_encode))
                print (e)
        else:
            print ('%s is not unicode ' % (str1))
        return str(str1)


class Analyze(dict, Maya):
    def __init__(self, options):
        Maya.__init__(self)
        dict.__init__(self)
        for i in options:
            self[i] = options[i]
        self.scene_info_dict = collections.OrderedDict()
        self.asset_info_dict = collections.OrderedDict()
        self.tips_info_dict = collections.OrderedDict()

        # self.asset_info_dict = {
        #
        # }
        # self.tips_info_dict = {
        #
        # }

    def print_info(self, info, exit_code='', sleep=0.2):
        print ("%s" % (info))

    def writing_error(self, error_code, info=""):
        info = self.unicode_to_str(info)
        error_code = str(error_code)
        if error_code in self.tips_info_dict:
            if isinstance(self.tips_info_dict[error_code], list) and len(self.tips_info_dict[error_code]) > 0:
                error_list = self.tips_info_dict[error_code]
                error_list.append(info)
                self.tips_info_dict[error_code] = error_list
        else:
            if type(info) == str and info != "":
                r = re.findall(r"Reference file not found.+?: +(.+)", info, re.I)
                if r:
                    self.tips_info_dict["25009"] = [r[0]]
                else:
                    self.tips_info_dict[error_code] = [info]
            else:
                self.tips_info_dict[error_code] = []

    def show_hide_node(self):
        mel.eval("outlinerEditor -edit -showDagOnly false outlinerPanel1;showMinorNodes true;")

    def is_renderable_layer(self, render_layer):
        for layer in pm.PyNode("renderLayerManager.renderLayerId").outputs():
            if layer == render_layer:
                if layer.type() == "renderLayer":
                    if layer.renderable.get():
                        return '1'
                    else:
                        return '0'

    def get_default_render_globals(self, layer):
        scene_info_common_dict = collections.OrderedDict()
        default_globals = pm.PyNode("defaultRenderGlobals")
        scene_info_common_dict['renderer'] = str(self.GetCurrentRenderer())
        scene_info_common_dict['image_file_prefix'] = str(self.GetMayaOutputPrefix(layer))
        if self.is_absolute_path(scene_info_common_dict['image_file_prefix']):
            self.writing_error(25002, "renderlayer: %s --- %s" % (layer, scene_info_common_dict['image_file_prefix']))
        scene_info_common_dict['start'] = str(int(cmds.getAttr("defaultRenderGlobals.startFrame")))
        scene_info_common_dict['end'] = str(int(cmds.getAttr("defaultRenderGlobals.endFrame")))
        scene_info_common_dict['by_frame'] = str(int(cmds.getAttr("defaultRenderGlobals.byFrame")))
        if layer == "defaultRenderLayer":
            pass
        else:
            if pm.mel.eval('editRenderLayerAdjustment -remove "defaultRenderGlobals.endFrame";') or pm.mel.eval(
                    'editRenderLayerAdjustment -remove "defaultRenderGlobals.startFrame";') or pm.mel.eval(
                    'editRenderLayerAdjustment -remove "defaultRenderGlobals.byFrame";'):
                self.writing_error(25015,
                                   "render layer: %s \'s startFrame/endFrame/byFrame has Layer Override attribute ,advice Layered submitting" % (
                                   layer))
        scene_info_common_dict['all_camera'] = self.GetRenderableCameras(False)
        scene_info_common_dict['render_camera'] = [i.name() for i in pm.ls(type="camera") if i.renderable.get()]
        if not scene_info_common_dict['render_camera']:
            self.writing_error(25011, "render layer: %s  there is  no camera  " % (layer))
        scene_info_common_dict["renumber_frames"] = str(default_globals.modifyExtension.get())
        if default_globals.modifyExtension.get():
            self.writing_error(25001)
        scene_info_common_dict['width'] = str(int(cmds.getAttr("defaultResolution.width")))
        scene_info_common_dict['height'] = str(int(cmds.getAttr("defaultResolution.height")))
        scene_info_common_dict["image_format"] = str(self.GetOutputExt())
        scene_info_common_dict["animation"] = str(default_globals.animation.get())
        scene_info_common_dict["file_name"] = str(pm.renderSettings(fin=1, cam='', lyr=layer))
        if len(str(int(default_globals.endFrame.get()))) > default_globals.extensionPadding.get():
            self.writing_error(25010)
        # self["renderSettings"]['all_layer'] = ",".join([i.name() for i in pm.PyNode("renderLayerManager.renderLayerId").outputs() if i.type() == "renderLayer"])
        # self["renderSettings"]['render_layer'] = ",".join([i.name() for i in pm.PyNode("renderLayerManager.renderLayerId").outputs() if i.type() == "renderLayer" if i.renderable.get()])
        # self.scene_info_dict[layer]["common"] = scene_info_common_dict
        return scene_info_common_dict

    def get_arnold_setting(self, layer):
        try:
            arnold_options_node = pm.PyNode('defaultArnoldRenderOptions')
        except:
            arnold_options_node = pm.createNode('aiOptions', name='defaultArnoldRenderOptions', skipSelect=True,
                                                shared=True)
        try:
            arnold_filter_node = pm.PyNode('defaultArnoldFilter')
        except:
            arnold_filter_node = pm.createNode('aiAOVFilter', name='defaultArnoldFilter', skipSelect=True, shared=True)
        try:
            arnold_driver_node = pm.PyNode('defaultArnoldDriver')
        except:
            arnold_driver_node = pm.createNode('aiAOVDriver', name='defaultArnoldDriver', skipSelect=True, shared=True)
        try:
            arnold_display_driver_node = pm.PyNode('defaultArnoldDisplayDriver')
        except:
            arnold_display_driver_node = pm.createNode('aiAOVDriver', name='defaultArnoldDisplayDriver',
                                                       skipSelect=True, shared=True)
        try:
            resolution_node = pm.PyNode('defaultResolution')
        except:
            resolution_node = pm.createNode('resolution', name='defaultResolution', skipSelect=True, shared=True)
        scene_info_option_dict = collections.OrderedDict()
        scene_info_option_dict["append"] = str(arnold_driver_node.append.get())
        scene_info_option_dict["aov_output_mode"] = str(arnold_driver_node.outputMode.get())
        scene_info_option_dict["motion_blur_enable"] = str(arnold_options_node.motion_blur_enable.get())
        scene_info_option_dict["merge_aovs"] = str(arnold_driver_node.mergeAOVs.get())
        scene_info_option_dict["abort_on_error"] = str(arnold_options_node.abortOnError.get())
        scene_info_option_dict["log_verbosity"] = str(arnold_options_node.log_verbosity.get())
        AASamples = str(arnold_options_node.AASamples.get())
        GIDiffuseSamples = str(arnold_options_node.GIDiffuseSamples.get())
        GISpecularSamples = str(arnold_options_node.GISpecularSamples.get())
        GITransmissionSamples = str(arnold_options_node.GITransmissionSamples.get())
        GISssSamples = str(arnold_options_node.GISssSamples.get())
        GIVolumeSamples = str(arnold_options_node.GIVolumeSamples.get())
        scene_info_option_dict["sampling"] = [AASamples, GIDiffuseSamples, GISpecularSamples, GITransmissionSamples,
                                              GISssSamples, GIVolumeSamples]
        if arnold_options_node.hasAttr("autotx"):
            scene_info_option_dict["auto_tx"] = str(arnold_options_node.autotx.get())
            if scene_info_option_dict["auto_tx"] == '0':
                scene_info_option_dict["use_existing_tiled_textures"] = str(
                    arnold_options_node.use_existing_tiled_textures.get())
        if arnold_options_node.hasAttr("textureMaxMemoryMB"):
            scene_info_option_dict["texture_max_memory_mb"] = str(arnold_options_node.textureMaxMemoryMB.get())
        if arnold_options_node.hasAttr("threads_autodetect"):
            scene_info_option_dict["threads_autodetect"] = str(arnold_options_node.threads_autodetect.get())
        if arnold_options_node.hasAttr("renderType"):
            scene_info_option_dict["render_type"] = str(arnold_options_node.renderType.get())
            if arnold_options_node.renderType.get() in [1, 2]:
                self.writing_error(25005)
        if arnold_options_node.hasAttr("absoluteTexturePaths"):
            scene_info_option_dict["absolute_texture_paths"] = str(arnold_options_node.absoluteTexturePaths.get())
        if arnold_options_node.hasAttr("absoluteProceduralPaths"):
            scene_info_option_dict["absolute_procedural_paths"] = str(arnold_options_node.absoluteProceduralPaths.get())
        scene_info_option_dict['pre_render_mel'] = self.unicode_to_str(self.defaultRG.preMel.get())
        scene_info_option_dict['post_render_mel'] = self.unicode_to_str(self.defaultRG.postMel.get())
        scene_info_option_dict['pre_render_layer_mel'] = self.unicode_to_str(self.defaultRG.preRenderLayerMel.get())
        scene_info_option_dict['post_render_layer_mel'] = self.unicode_to_str(self.defaultRG.postRenderLayerMel.get())
        scene_info_option_dict['pre_render_frame_mel'] = self.unicode_to_str(self.defaultRG.preRenderMel.get())
        scene_info_option_dict['post_render_frame_mel'] = self.unicode_to_str(self.defaultRG.postRenderMel.get())
        # self.scene_info_dict[layer]["option"] = scene_info_option_dict
        return scene_info_option_dict

    def get_vray_setting(self, layer):
        try:
            vraySettings_node = pm.PyNode('vraySettings')
        except:
            vraySettings_node = pm.createNode('VRaySettingsNode', name='vraySettings', skipSelect=True, shared=True)
        scene_info_option_dict = collections.OrderedDict()
        scene_info_option_dict["dynMemLimit"] = str(vraySettings_node.sys_rayc_dynMemLimit.get())
        scene_info_option_dict["animType"] = str(vraySettings_node.animType.get())
        if vraySettings_node.animType.get() == 2:
            self.writing_error(25004)
        scene_info_option_dict["sys_distributed_rendering_on"] = str(
            vraySettings_node.sys_distributed_rendering_on.get())
        if vraySettings_node.sys_distributed_rendering_on.get():
            self.writing_error(25003)
        scene_info_option_dict["vrscene_on"] = str(vraySettings_node.vrscene_on.get())
        if vraySettings_node.vrscene_on.get():
            self.writing_error(25007)
        scene_info_option_dict['pre_render_mel'] = self.unicode_to_str(self.defaultRG.preMel.get())
        scene_info_option_dict['post_render_mel'] = self.unicode_to_str(self.defaultRG.postMel.get())
        scene_info_option_dict['pre_render_layer_mel'] = self.unicode_to_str(self.defaultRG.preRenderLayerMel.get())
        scene_info_option_dict['post_render_layer_mel'] = self.unicode_to_str(self.defaultRG.postRenderLayerMel.get())
        scene_info_option_dict['pre_render_frame_mel'] = self.unicode_to_str(self.defaultRG.preRenderMel.get())
        scene_info_option_dict['post_render_frame_mel'] = self.unicode_to_str(self.defaultRG.postRenderMel.get())
        scene_info_option_dict['pre_key_frame_mel'] = self.unicode_to_str(vraySettings_node.preKeyframeMel.get())
        scene_info_option_dict['rt_image_ready_mel'] = self.unicode_to_str(vraySettings_node.rtImageReadyMel.get())
        # self.scene_info_dict[layer]["option"] = scene_info_option_dict
        return scene_info_option_dict

    def get_redshift_setting(self, layer):
        scene_info_option_dict = collections.OrderedDict()
        redshift_options = pm.PyNode("redshiftOptions")
        if redshift_options.hasAttr("motionBlurEnable"):
            scene_info_option_dict["absolute_procedural_paths"] = redshift_options.motionBlurEnable.get()
        if redshift_options.hasAttr("motionBlurDeformationEnable"):
            scene_info_option_dict[
                "motion_blur_deformation_enable"] = redshift_options.motionBlurDeformationEnable.get()
        scene_info_option_dict['pre_render_mel'] = redshift_options.preRenderMel.get()
        scene_info_option_dict['post_render_mel'] = redshift_options.postRenderMel.get()
        scene_info_option_dict['pre_render_layer_mel'] = redshift_options.preRenderLayerMel.get()
        scene_info_option_dict['post_render_layer_mel'] = redshift_options.postRenderLayerMel.get()
        scene_info_option_dict['pre_render_frame_mel'] = redshift_options.preRenderFrameMel.get()
        scene_info_option_dict['post_render_frame_mel'] = redshift_options.postRenderFrameMel.get()
        # self.scene_info_dict[layer]["option"] = scene_info_option_dict
        return scene_info_option_dict

    def get_renderman_setting(self, layer):
        scene_info_option_dict = collections.OrderedDict()
        # self.scene_info_dict[layer]["option"] = scene_info_option_dict
        return scene_info_option_dict

    def get_krakatoa_setting(self, layer):
        scene_info_option_dict = collections.OrderedDict()
        # self.scene_info_dict[layer]["option"] = scene_info_option_dict
        return scene_info_option_dict

    def get_layer_settings(self, render_layer=None):
        self.defaultRG = pm.PyNode("defaultRenderGlobals")
        self.show_hide_node()
        all_render_layer = cmds.listConnections("renderLayerManager.renderLayerId")
        render_layer_list = render_layer if render_layer else all_render_layer
        if isinstance(render_layer_list, str):
            render_layer_list = [render_layer_list]
        for layer in render_layer_list:
            if layer:
                layer_dict = layer
                layer_dict = collections.OrderedDict()
                pm.PyNode(layer).setCurrent()
                if self.check_layer_renderer(layer):
                    layer_dict['renderable'] = self.is_renderable_layer(layer)
                    renderer = str(self.GetCurrentRenderer())
                    layer_dict['is_default_camera'] = '1'
                    layer_dict['common'] = self.get_default_render_globals(layer)
                    if renderer == "vray":
                        layer_dict['option'] = self.get_vray_setting(layer)
                    elif renderer == "arnold":
                        layer_dict['option'] = self.get_arnold_setting(layer)
                    elif renderer == "redshift":
                        layer_dict['option'] = self.get_redshift_setting(layer)
                    elif renderer == "renderman":
                        layer_dict['option'] = self.get_renderman_setting(layer)
                    elif renderer == "MayaKrakatoa":
                        layer_dict['option'] = self.get_krakatoa_setting(layer)
                    else:
                        layer_dict['option'] = ''
                    self.scene_info_dict[layer] = layer_dict
                else:
                    pass
            else:
                print (traceback.format_exc())
                self.writing_error(25018)
                raise Exception("Can't switch renderlayer :  " + layer)

    def getArnoldElementNames(self):
        elementNames = [""]
        arnold_options_node = pm.PyNode("defaultArnoldRenderOptions")
        aovMode = int(arnold_options_node.aovMode.get())
        # aovMode = int(pm.getAttr("defaultArnoldRenderOptions.aovMode"))
        mergeAOV = int(pm.getAttr("defaultArnoldDriver.mergeAOVs"))
        imfType = str(pm.mel.getImfImageType())
        if aovMode:
            if not mergeAOV:
                elementNames = []
                AOVnames = pm.ls(type='aiAOV')
                for aovName in AOVnames:
                    enabled = int(pm.getAttr(str(aovName) + ".enabled"))
                    if enabled == 1:
                        elementNames.insert(0, pm.getAttr(str(aovName) + ".name"))
                elementNames.insert(0, "beauty")
        return elementNames

    def getArnoldElements(self):
        elementNames = [""]
        aovMode = int(pm.getAttr("defaultArnoldRenderOptions.aovMode"))
        mergeAOV = int(pm.getAttr("defaultArnoldDriver.mergeAOVs"))
        imfType = str(pm.mel.getImfImageType())
        if aovMode:
            if not mergeAOV:
                elementNames = []
                AOVnames = pm.ls(type='aiAOV')
                for aovName in AOVnames:
                    enabled = int(pm.getAttr(str(aovName) + ".enabled"))
                    if enabled == 1:
                        elementNames.insert(0, aovName)

        return elementNames

    def getRedshiftElements(self):

        elementNames = [""]
        REs = pm.ls(type='RedshiftAOV')
        for RE in REs:
            enabled = int(pm.getAttr(str(RE) + ".enabled"))
            if enabled == 1:
                elementNames.insert(0, RE)

        return elementNames

    def getMentalRayElementNames(self, currentRenderLayer):

        elementNames = [""]
        # Format's in Maya are stored as integers.  For Mental ray EXR is stored as 51.
        exrFormat = 51
        if currentRenderLayer != "":
            format = int(pm.getAttr('defaultRenderGlobals.imageFormat'))
            prefix = str(pm.getAttr('defaultRenderGlobals.imageFilePrefix'))
            # If the format is exr and there is not a renderPass token in the output prefix then the output is rendered as a single multichannel exr so we do not have to handle the elements separately.
            if format != exrFormat or pm.mel.match("<RenderPass>", prefix) != "":
                renderLayers = []
                renderLayers = pm.ls(type='renderLayer')
                if currentRenderLayer in renderLayers:
                    connectedPasses = pm.listConnections(currentRenderLayer + ".rps")
                    if len(connectedPasses) > 0:
                        elementNames = []
                        elementNames.insert(0, "MasterBeauty")
                        for pass_ in connectedPasses:
                            elementNames.insert(0, pass_)

        return elementNames

    def getVRayElementNames(self):
        elementNames = [""]
        isMultichannelExr = int(False)
        multichannel = " (multichannel)"
        ext = ""
        REs = pm.ls(type=['VRayRenderElement', 'VRayRenderElementSet'])
        if pm.optionMenuGrp('vrayImageFormatMenu', exists=1):
            ext = str(pm.optionMenuGrp('vrayImageFormatMenu', q=1, v=1))
        else:
            ext = str(pm.getAttr('vraySettings.imageFormatStr'))
        if ext == "":
            ext = "png"
        # for some reason this happens if you have not changed the format
        if ext.endswith(multichannel):
            ext = ext[0:-len(multichannel)]
            isMultichannelExr = int(True)
        enableAll = int(pm.getAttr("vraySettings.relements_enableall"))
        useReferenced = int(pm.getAttr("vraySettings.relements_usereferenced"))
        if not isMultichannelExr and enableAll:
            for RE in REs:
                enabled = int(pm.getAttr(str(RE) + ".enabled"))
                isReferenced = int(pm.referenceQuery(RE, isNodeReferenced=1))
                if isReferenced == 1 and useReferenced == 0:
                    continue
                if enabled == 1:
                    reType = str(pm.getAttr(str(RE) + ".vrayClassType"))
                    REName = ""
                    if reType == "ExtraTexElement" or reType == "MaterialSelectElement":
                        RENameFunction = pm.listAttr(RE, st="vray_explicit_name_*")
                        REName = str(pm.getAttr(str(RE) + "." + RENameFunction[0]))
                        if REName == "":
                            RENameFunction = pm.listAttr(RE, st="vray_name_*")
                            REName = str(pm.getAttr(str(RE) + "." + RENameFunction[0]))
                            if reType == "ExtraTexElement":
                                textures = pm.listConnections(str(RE) + ".vray_texture_extratex")
                                if len(textures) > 0:
                                    if REName != "":
                                        REName += "_"

                                    REName += textures[0]
                            elif reType == "MaterialSelectElement":
                                materials = pm.listConnections(str(RE) + ".vray_mtl_mtlselect")
                                if len(materials) > 0:
                                    if REName != "":
                                        REName += "_"

                                    REName += materials[0]

                    else:
                        RENameFunction = pm.listAttr(RE, st="vray_name_*")
                        if len(RENameFunction) == 0:
                            RENameFunction = pm.listAttr(RE, st="vray_filename_*")

                        REName = str(pm.getAttr(str(RE) + "." + RENameFunction[0]))

                    REName = str(pm.mel.substituteAllString(REName, " ", "_"))
                    elementNames.insert(0, REName)

            separateAlpha = int(pm.getAttr("vraySettings.separateAlpha"))
            if separateAlpha == 1:
                elementNames.insert(0, "Alpha")

        return elementNames

    # ------------get assets   return  a  list -------------

    def get_assets(self, assets_node_list):
        asset_dict = {}
        for asset_node_dict in assets_node_list:
            for node_type in asset_node_dict:
                attr_name = asset_node_dict[node_type]
                # node_type='ExocortexAlembicXform'
                # attr_name='fileName'
                all_node = pm.ls(type=node_type)
                if all_node:
                    print all_node
                    for node in all_node:
                        if node_type == 'cacheFile':
                            b = cmds.getAttr(node + ".cacheName")
                            c = cmds.getAttr(node + ".cachePath")
                            if c.endswith("/"):
                                c = c.strip()
                                c = c[:-1]
                            print (c + "/" + b + ".xml")
                            file_path = c + "/" + b + ".xml"
                        else:
                            file_path = cmds.getAttr(node + "." + attr_name)
                        # node.attr(attr_name).set(l=0)
                        # file_path = node.attr(attr_name).get()
                        asset_dict_keys = node_type + '::' + attr_name
                        asset_dict_value = node + '::' + file_path
                        asset_dict[asset_dict_keys] = asset_dict_value

        print '+' * 40
        print asset_dict
        return asset_dict

    def gather_asset(self, asset_type, asset_list, asset_dict):
        self.G_DEBUG_LOG.info('\r\n\r\n[-----------------maya.RBanalyse.gather_asset_by_file_path]')
        self.G_DEBUG_LOG.info(asset_type)
        asset_input_server_str = 'asset_input_server'
        asset_input_str = 'asset_input'
        asset_input_missing_str = 'asset_input_missing'
        asset_item_missing_str = asset_type + '_missing'
        asset_input_list = []
        asset_input_missing_list = []
        asset_input_server_list = []

        for asset in asset_list:
            asset_input_list.append(asset)
            if self.ASSET_WEB_COOLECT_BY_PATH:
                if not os.path.exists(asset):
                    asset_input_missing_list.append(asset)
            else:
                asset_item_server = self.get_file_from_project_by_name(asset)
                if asset_item_server:
                    asset_input_server_list.append(asset_item_server)
                else:
                    asset_input_missing_list.append(asset)
                '''
                asset_name=os.path.basename(asset)
                #if  asset_name   in self.ASSET_INPUT_KEY_LIST:
                if self.G_INPUT_PROJECT_ASSET_DICT.has_key(asset_name):    
                    self.get_file_from_project_by_name()
                    asset_input_server_list.append(self.G_INPUT_PROJECT_ASSET_DICT[asset_name])
                else:
                    asset_input_missing_list.append(asset)
                '''
        if asset_input_server_list:
            if asset_dict.has_key(asset_input_server_str):
                # asset_dict[asset_input_server_str].extend(asset_input_server_list)  # notice yinyong
                asset_dict[asset_input_server_str] = asset_dict[asset_input_server_str] + asset_input_server_list
            else:
                asset_dict[asset_input_server_str] = asset_input_server_list

        if asset_input_list:
            if asset_dict.has_key(asset_input_str):
                # asset_dict[asset_input_str].extend(asset_input_list)  # notice yinyong
                asset_dict[asset_input_str] = asset_dict[asset_input_str] + asset_input_list
            else:
                asset_dict[asset_input_str] = asset_input_list
        if asset_input_missing_list:
            if asset_dict.has_key(asset_input_missing_str):
                # asset_dict[asset_input_missing_str].extend(asset_input_missing_list)  # notice yinyong
                asset_dict[asset_input_missing_str] = asset_dict[asset_input_missing_str] + asset_input_missing_list
            else:
                asset_dict[asset_input_missing_str] = asset_input_missing_list

            asset_dict[asset_item_missing_str] = asset_input_missing_list

    def GetCurrentRenderer(self):
        """Returns the current renderer."""
        renderer = str(pm.mel.currentRenderer())
        if renderer == "_3delight":
            renderer = "3delight"

        return renderer

    def GetOutputExt(self):

        renderer = str(self.GetCurrentRenderer())
        if renderer == "vray":
            pm.melGlobals.initVar('string[]', 'g_vrayImgExt')
            # Need to special case vray, because they like to do things differently.
            ext = ""
            if pm.optionMenuGrp('vrayImageFormatMenu', exists=1):
                ext = str(pm.optionMenuGrp('vrayImageFormatMenu', q=1, v=1))
            else:
                ext = str(pm.getAttr('vraySettings.imageFormatStr'))
            if ext == "":
                ext = "png"
                # for some reason this happens if you have not changed the format
                # VRay can append this to the end of the render settings display, but we don't want it in the file name.

            isMultichannelExr = int(False)
            multichannel = " (multichannel)"
            if ext.endswith(multichannel):
                ext = ext[0:-len(multichannel)]
                isMultichannelExr = int(True)

        else:

            if renderer == "renderMan" or renderer == "renderManRIS":
                pat = str(pm.mel.rmanGetImagenamePattern(1))
                # $prefixString = `rmanGetImageName 1`;
                ext = str(pm.mel.rmanGetImageExt(""))

            elif renderer == "mentalRay":
                ext = str(cmds.getAttr("defaultRenderGlobals.imfkey"))

            else:
                ext = str(cmds.getAttr("defaultRenderGlobals.imageFormat"))

        return ext

    def GetMotionBlur(self):
        """Returns if motion blur is enabled."""

        renderer = str(self.GetCurrentRenderer())
        mb = int(False)
        if renderer == "mentalRay":
            mb = int(pm.getAttr('miDefaultOptions.motionBlur'))


        elif renderer == "mayaHardware" or renderer == "mayaHardware2":
            mb = int(pm.getAttr('hardwareRenderGlobals.enableMotionBlur'))


        elif renderer == "mayaVector":
            mb = int(False)


        elif renderer == "turtle":
            mb = int(pm.getAttr('TurtleRenderOptions.motionBlur'))


        elif renderer == "renderMan" or renderer == "renderManRIS":
            mb = int(pm.getAttr('renderManGlobals.rman__torattr___motionBlur'))


        elif renderer == "finalRender":
            mb = int(pm.getAttr('defaultFinalRenderSettings.motionBlur'))


        elif renderer == "vray":
            mb = int(pm.getAttr('vraySettings.cam_mbOn'))


        else:
            mb = int(pm.getAttr('defaultRenderGlobals.motionBlur'))

        return mb

    def GetStrippedSceneFileName(self):

        fileName = str(cmds.file(q=1, sceneName=1))
        fileName = str(pm.mel.basename(fileName, ".mb"))
        fileName = str(pm.mel.basename(fileName, ".ma"))
        return fileName

    def GetMayaOutputPrefix(self, layer):

        prefix = ""
        renderer = str(self.GetCurrentRenderer())

        if renderer != "vray":
            prefix = str(pm.getAttr('defaultRenderGlobals.imageFilePrefix'))
        else:
            prefix = str(pm.getAttr('vraySettings.fileNamePrefix'))

        if prefix == "":
            prefix = str(self.GetStrippedSceneFileName())

            # if renderer == "arnold" and pm.mel.match("<RenderPass>", prefix) == "":
            # elements = self.getArnoldElementNames()
            # if elements[0] != "":
            # prefix = "<RenderPass>/" + prefix
            # if renderer == "mentalRay" and pm.mel.match("<RenderPass>", prefix) == "":
            # elements = self.getMentalRayElementNames(layer)
            # if elements[0] != "":
            # prefix = "<RenderPass>/" + prefix
            # renderableCameras = self.GetRenderableCameras(False)
            # multipleRenderableCams = (len(renderableCameras) > 1)
            # # Redshift does not work with multiple renderable cameras so we need to node add <camera>
            # if multipleRenderableCams:
            # if (pm.mel.match("<Camera>", prefix) == "") and (
            # pm.mel.match("%c", prefix) == "") and renderer != "redshift" and (
            # renderer != "vray" or pm.mel.match("<camera>", prefix) == ""):
            # prefix = "<Camera>/" + prefix
            # # vray accepts <camera> as a token, whereas no one else does

            # if self.IsRenderLayersOn():
            # if renderer == "vray" and (pm.mel.match("<Layer>", prefix) == "") and (
            # pm.mel.match("<layer>", prefix) == "") and (pm.mel.match("%l", prefix) == ""):
            # prefix = "<Layer>/" + prefix
            # elif renderer != "vray" and (pm.mel.match("<RenderLayer>", prefix) == "") and (
            # pm.mel.match("<Layer>", prefix) == "") and (pm.mel.match("%l", prefix) == ""):
            # prefix = "<RenderLayer>/" + prefix

        return prefix

    def GetRenderableCameras_bak(self, ignoreDefaultCameras):

        cameraNames = pm.mel.listTransforms('-cameras')
        renderableCameras = []
        for cameraName in cameraNames:
            if self.IsCameraRenderable(cameraName):
                relatives = pm.listRelatives(cameraName, s=1)
                cameraShape = relatives[0]
                # Only submit default cameras if the setting to ignore them is disabled.
                if not ignoreDefaultCameras or not self.IsDefaultCamera(cameraShape):
                    renderableCameras.insert(0, cameraName)

        return renderableCameras

    def GetRenderableCameras(self, ignoreDefaultCameras):

        cameraNames = cmds.ls(type="camera")
        renderableCameras = []
        for cameraName in cameraNames:
            # Only submit default cameras if the setting to ignore them is disabled.
            if not ignoreDefaultCameras and not self.IsDefaultCamera(cameraName):
                renderableCameras.insert(0, cameraName)

        return renderableCameras

    def IsCameraRenderable(self, cameraName):

        relatives = pm.listRelatives(cameraName, s=1)
        # print( "Checking if camera is renderable: " + $cameraName + "\n" );
        cameraShape = relatives[0]
        cameraRenderable = 0
        # Getting the renderable attribute can throw an error if there are duplicate camera shape names.
        # The catch blocks are to prevent these erros so that the submission can continue.
        if not pm.catch(lambda: pm.mel.attributeExists("renderable", cameraShape)):
            cameraRenderable = int(pm.getAttr(cameraShape + ".renderable"))
            pm.catch(lambda: cameraRenderable)

        return cameraRenderable

    def IsDefaultCamera_bak(self, cameraName):
        if cameraName == "frontShape" or cameraName == "perspShape" or cameraName == "sideShape" or cameraName == "topShape":
            return True
        elif cameraName == "front" or cameraName == "persp" or cameraName == "side" or cameraName == "top":
            return True
        else:
            return False

    def IsDefaultCamera(self, cameraName):
        if cameraName == "frontShape" or cameraName == "sideShape" or cameraName == "topShape":
            return True
        elif cameraName == "front" or cameraName == "side" or cameraName == "top":
            return True
        else:
            return False

    def IsRenderLayersOn(self):
        """Returns if render layers is on."""

        renderLayers = pm.ls(exactType="renderLayer")
        referenceLayers = pm.ls(exactType="renderLayer", rn=1)
        return ((len(renderLayers) - len(referenceLayers)) > 1)

    def check_maya_version(self, maya_file, cg_version):
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
            self.print_info("get maya file version %s" % (result))
            if int(result) == int(cg_version):
                pass
            else:
                self.writing_error(25013, "maya file version Maya%s" % result)

    def is_absolute_path(self, path):
        if path:
            path = path.replace("\\", "/")
            if ":" in path:
                return 1
            if path.startswith("//"):
                return 1

    def check_layer_renderer(self, layer):
        renderer = str(self.GetCurrentRenderer())
        self.print_info("current renderer is : %s " % renderer)
        plugins_rederer = {"arnold": "mtoa",
                           "vray": "vrayformaya",
                           "redshift": "redshift_GPU",
                           "renderman": "RenderMan_for_Maya",
                           "MayaKrakatoa": "krakatoa"
                           }
        plugins_rederer.setdefault(renderer)
        if plugins_rederer[renderer]:
            if plugins_rederer[renderer] not in self["cg_plugins"]:
                self.writing_error(25008, "render layer: %s \'s renderer is %s ,please confirm configure plugins" % (
                layer, renderer))
                return False
        elif renderer == "mentalRay" and int(self["cg_version"]) > 2016.5 and renderer not in self["cg_plugins"]:
            self.writing_error(25008,
                               "render layer: %s \'s renderer is %s ,above version of maya2017(contain),  please confirm configure mentalRay" % (
                               layer, renderer))
            return False
        elif renderer in ["mayaHardware", "mayaHardware2", "mayaVector"]:
            self.writing_error(25014, "render layer: %s \'s renderer is %s   please change" % (layer, renderer))
            return False
        return True

    def check_scene_name(self):
        scene_name = os.path.splitext(os.path.basename(self["cg_file"]))[0]
        if not re.findall("^[A-Z][^-]+[0-9]$", scene_name):
            self.writing_error(25017)
            return False
        return True

    def start_open_maya(self):
        self.print_info("start maya ok.")
        self.print_info("open maya file: " + self["cg_file"])
        if self["cg_project"]:
            if os.path.exists(self["cg_project"]):
                workspacemel = os.path.join(self["cg_project"],
                                            "workspace.mel")
                if not os.path.exists(workspacemel):
                    try:
                        with open(workspacemel, "w"):
                            ''
                    except:
                        pass
                if os.path.exists(workspacemel):
                    pm.mel.eval('setProject "%s"' % (self["cg_project"]))
        # ignore some open maya errors.
        if os.path.exists(self["cg_file"]) and os.path.isfile(self["cg_file"]):
            try:
                # pm.openFile(options["cg_file"], force=1, ignoreVersion=1, prompt=0, loadReferenceDepth="all")
                pm.openFile(self["cg_file"], force=1, ignoreVersion=1, prompt=0)
                self.print_info("open maya file ok.")
            except:
                pass
        else:
            raise Exception("Dont Found the maya files error.")

    def write_task_info(self):
        info_file_path = os.path.dirname(self["task_json"])
        print "write info to task.json"
        if not os.path.exists(info_file_path):
            os.makedirs(info_file_path)
        try:
            info_file = self["task_json"]
            with open(info_file, 'r') as f:
                json_src = json.load(f)
            json_src["scene_info"] = self.scene_info_dict
            # json_src.setdefault("scene_info",[]).append(self.scene_info_dict)
            with open(info_file, 'w') as f:
                f.write(json.dumps(json_src))
        except Exception as err:
            print  err
            pass

    def write_task_json(self):
        json_file_path = os.path.dirname(self["task_json"])
        print "write info to %s" % self["task_json"]
        if not os.path.exists(json_file_path):
            os.makedirs(json_file_path)
        try:
            info_file = self["task_json"]
            with open(info_file, 'r') as f:
                json_src = json.load(f)
            print type(json_src)
            json_src["scene_info"] = self.scene_info_dict

            task_json_str = json.dumps(json_src, ensure_ascii=False)
            self.write_file(task_json_str, self["task_json"])
        except Exception as err:
            print  err
            pass

    def write_asset_json(self):
        json_file_path = os.path.dirname(self["asset_json"])
        if not os.path.exists(json_file_path):
            os.makedirs(json_file_path)
        # self.asset_info_dict['maya'] = [self["cg_file"]]
        print "write info to asset.json"
        try:
            info_file = self["asset_json"]
            json_src = self.asset_info_dict
            print json_src
            with open(info_file, 'w+') as f:
                f.write(json.dumps(json_src))
        except Exception as err:
            print  err
            pass

    def write_tips_json(self):
        tips_file_path = os.path.dirname(self["tips_json"])
        print "write info to %s" % self["tips_json"]
        if not os.path.exists(tips_file_path):
            os.makedirs(tips_file_path)
        tips_json_str = json.dumps(self.tips_info_dict, ensure_ascii=False)
        self.write_file(tips_json_str, self["tips_json"])

    def write_tips_info(self):
        info_file_path = os.path.dirname(self["tips_json"])
        print "write info to tips.json"
        if not os.path.exists(info_file_path):
            os.makedirs(info_file_path)
        try:
            info_file = self["tips_json"]
            json_src = self.tips_info_dict
            print json_src
            with open(info_file, 'w+') as f:
                f.write(json.dumps(json_src))
        except Exception as err:
            print  err
            pass


def analyze_maya(options):
    print "88888888888888"
    print options
    analyze = Analyze(options)

    analyze.check_maya_version(options["cg_file"], options["cg_version"])
    analyze.start_open_maya()
    analyze.get_layer_settings()
    analyze.print_info("get layer setting info ok.")

    analyze.write_task_info()
    analyze.print_info("write task info ok.")

    analyze.write_asset_json()
    analyze.print_info("write asset info ok.")

    analyze.write_tips_info()
    analyze.print_info("write tips info ok.")