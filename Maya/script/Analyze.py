#!/usr/bin/env python
# encoding:utf-8
# -*- coding: utf-8 -*-
# -----M20180321-----
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

reload(sys)
sys.setdefaultencoding('utf8')
if os.path.basename(sys.executable.lower()) in ["mayabatch.exe", "maya.exe"]:
    import pymel.core as pm
    import maya.cmds as cmds
    import maya.mel as mel


class Maya(object):
    def __init__(self):

        self.scene_info_dict = collections.OrderedDict()
        self.asset_info_dict = collections.OrderedDict()
        self.tips_info_dict = collections.OrderedDict()
        self.asset_dict = collections.OrderedDict()


    def print_info(self, info, exit_code='', sleep=0.2):
        print ("%s" % (self.unicode_to_str(info)))

    def mylog(self,message):
        print("[Analyze] %s"%message)

    def writing_error(self, error_code, info=None):
        error_code = str(error_code)
        if type(info) == list:
            pass
        else:
            info = self.unicode_to_str(info)

        if error_code in self.tips_info_dict:
            if isinstance(self.tips_info_dict[error_code], list) and len(self.tips_info_dict[error_code]) > 0 and \
                            self.tips_info_dict[error_code][0] != info:
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

            elif type(info) == list:
                self.tips_info_dict[error_code] = info
            else:
                self.tips_info_dict[error_code] = []

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

    def to_unicode(self, string):
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

    def get_encode(self, encode_str):
        if isinstance(encode_str, unicode):
            return "unicode"
        else:
            for code in ["utf-8", sys.getfilesystemencoding(), "gb18030", "ascii", "gbk", "gb2312"]:
                try:
                    encode_str.decode(code)
                    return code
                except:
                    pass

    def str_to_unicode(self, encode_str):
        if isinstance(encode_str, unicode):
            return encode_str
        else:
            code = self.get_encode(encode_str)
            return encode_str.decode(code)

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
        if str1 == None or str1 == "" or str1 == 'Null' or str1 == 'null':
            str1 = ""
            return str1
        elif isinstance(str1, unicode):
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

    def check_contain_chinese(self, check_str):
        '''
        check  this string  contain  chinese
        :param check_str: sting
        :return: True or  False
        '''
        # for ch in check_str.decode('utf-8'):
        #     if u'\u4e00' <= ch <= u'\u9fff':
        #         return True
        # return False
        zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
        check_str = self.str_to_unicode(check_str)
        match = zh_pattern.search(check_str)
        if match:
            return True
        else:
            return False


class Analyze(dict, Maya):
    def __init__(self, options):
        Maya.__init__(self)
        dict.__init__(self)
        for i in options:
            self[i] = options[i]

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
        scene_info_common_dict['frames'] = scene_info_common_dict['start'] + '-' + scene_info_common_dict['end'] + '[' + scene_info_common_dict['by_frame'] + ']'
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

        if len(scene_info_common_dict['render_camera']) > 1:
            self.writing_error(20006, "render layer: %s  has %s  cameras: %s  " % (layer,len(scene_info_common_dict['render_camera']),scene_info_common_dict['render_camera']))

        scene_info_common_dict["renumber_frames"] = str(default_globals.modifyExtension.get())
        if default_globals.modifyExtension.get():
            self.writing_error(25001)
        scene_info_common_dict['width'] = str(int(cmds.getAttr("defaultResolution.width")))
        scene_info_common_dict['height'] = str(int(cmds.getAttr("defaultResolution.height")))
        scene_info_common_dict["image_format"] = str(self.get_image_format())
        if scene_info_common_dict["image_format"] not in ['png', 'iff', 'exr', 'tga', 'jpg', 'tif', 'jpeg', 'deepexr']:
            self.writing_error(20004, "render layer\'s imageformat is %s " % (scene_info_common_dict["image_format"]))
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
        if arnold_driver_node.hasAttr("append"):
            scene_info_option_dict["append"] = str(arnold_driver_node.append.get())
        scene_info_option_dict["aov_output_mode"] = str(arnold_driver_node.outputMode.get())
        scene_info_option_dict["motion_blur_enable"] = str(arnold_options_node.motion_blur_enable.get())
        scene_info_option_dict["merge_aovs"] = str(arnold_driver_node.mergeAOVs.get())
        scene_info_option_dict["abort_on_error"] = str(arnold_options_node.abortOnError.get())
        scene_info_option_dict["log_verbosity"] = str(arnold_options_node.log_verbosity.get())
        #sampling---------------
        AASamples = str(arnold_options_node.AASamples.get())
        GIDiffuseSamples = str(arnold_options_node.GIDiffuseSamples.get())
        if arnold_options_node.hasAttr("GISpecularSamples"):
            sampling_3 = str(arnold_options_node.GISpecularSamples.get())
        elif arnold_options_node.hasAttr("GIGlossySamples"):
            sampling_3 = str(arnold_options_node.GIGlossySamples.get())
        if arnold_options_node.hasAttr("GITransmissionSamples"):
            sampling_4 = str(arnold_options_node.GITransmissionSamples.get())
        elif arnold_options_node.hasAttr("GIRefractionSamples"):
            sampling_4 = str(arnold_options_node.GIRefractionSamples.get())

        if arnold_options_node.hasAttr("GISssSamples"):
            sampling_5 = str(arnold_options_node.GISssSamples.get())
        elif arnold_options_node.hasAttr("sssBssrdfSamples"):
            sampling_5 = str(arnold_options_node.sssBssrdfSamples.get())

        if arnold_options_node.hasAttr("GIVolumeSamples"):
            sampling_6 = str(arnold_options_node.GIVolumeSamples.get())
        elif arnold_options_node.hasAttr("volumeIndirectSamples"):
            sampling_6 = str(arnold_options_node.volumeIndirectSamples.get())


        scene_info_option_dict["sampling"] = [AASamples,GIDiffuseSamples,sampling_3,sampling_4,sampling_5, sampling_6]

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
        if vraySettings_node.hasAttr("animType"):
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
            scene_info_option_dict["absolute_procedural_paths"] = self.unicode_to_str(redshift_options.motionBlurEnable.get())
        if redshift_options.hasAttr("motionBlurDeformationEnable"):
            scene_info_option_dict[
                "motion_blur_deformation_enable"] = self.unicode_to_str(redshift_options.motionBlurDeformationEnable.get())

        if redshift_options.hasAttr("aovEnableDeepOutput"):
            scene_info_option_dict["aov_enable_deepOutput"] = self.unicode_to_str(redshift_options.aovEnableDeepOutput.get())

        if redshift_options.hasAttr("primaryGIEngine"):
            giengine_dict = {0: "None", 1: "Photon Map", 3: "Irradiance Cache", 4: "Brute Force"}
            gi_idex = redshift_options.primaryGIEngine.get()
            scene_info_option_dict["primary_gi_engine"] = giengine_dict[gi_idex]
            mode_ic = {0:"Rebuild",1:"Load",2:"Rebuild(prepass only)",3:"Rebuild(don`t save)"}
            if gi_idex == 3:
                if redshift_options.hasAttr("irradianceCacheMode"):
                    scene_info_option_dict["irradiance_cache_mode"] = mode_ic[redshift_options.irradianceCacheMode.get()]

        if redshift_options.hasAttr("secondaryGIEngine"):
            s_giengine_dict = {0: "None", 1: "Photon Map", 2: "Irradiance Point Cloud", 4: "Brute Force"}
            s_gi_idex = redshift_options.secondaryGIEngine.get()
            scene_info_option_dict["secondary_gi_engine"] = s_giengine_dict[s_gi_idex]

            mode_ip = {0:"Rebuild",1:"Load",2:"Rebuild(prepass only)",3:"Rebuild(don`t save)"}
            if s_gi_idex == 2:
                if redshift_options.hasAttr("irradiancePointCloudMode"):
                    scene_info_option_dict["irradiance_pointCloud_mode"] = mode_ip[redshift_options.irradiancePointCloudMode.get()]

        if redshift_options.hasAttr("bruteForceGINumRays"):
            GINumRays = redshift_options.bruteForceGINumRays.get()
            scene_info_option_dict["aov_enable_deepOutput"] = self.unicode_to_str(GINumRays)

        scene_info_option_dict['pre_render_mel'] = self.unicode_to_str(redshift_options.preRenderMel.get())
        scene_info_option_dict['post_render_mel'] = self.unicode_to_str(redshift_options.postRenderMel.get())
        scene_info_option_dict['pre_render_layer_mel'] = self.unicode_to_str(redshift_options.preRenderLayerMel.get())
        scene_info_option_dict['post_render_layer_mel'] = self.unicode_to_str(redshift_options.postRenderLayerMel.get())
        scene_info_option_dict['pre_render_frame_mel'] = self.unicode_to_str(redshift_options.preRenderFrameMel.get())
        scene_info_option_dict['post_render_frame_mel'] = self.unicode_to_str(redshift_options.postRenderFrameMel.get())
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
        self.has_renderable_layer()
        all_render_layer = cmds.listConnections("renderLayerManager.renderLayerId")
        if "defaultRenderLayer" not in all_render_layer:
            self.print_info(all_render_layer)
            self.writing_error(25019,all_render_layer)
        render_layer_list = render_layer if render_layer else all_render_layer
        if isinstance(render_layer_list, str):
            render_layer_list = [render_layer_list]
        for layer in render_layer_list:
            try:
                if layer:
                    self.mylog(layer)
                    layer_dict = layer
                    layer_dict = collections.OrderedDict()
                    pm.PyNode(layer).setCurrent()
                    self.get_image_namespace()
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
            except Exception as err:
                self.print_info(err)
                print (traceback.format_exc())
                self.writing_error(25018)
                raise Exception("Can't switch renderlayer :  " + layer)
        return self.scene_info_dict,self.tips_info_dict

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

    def get_image_format(self):
        render_engine = str(self.GetCurrentRenderer())
        if render_engine == 'arnold':
            return cmds.getAttr('defaultArnoldDriver.aiTranslator')
        if render_engine == 'redshift':
            redshift_format_number = cmds.getAttr('redshiftOptions.imageFormat')
            redshift_Image_format = {
                0: 'iff',
                1: 'exr',
                2: 'png',
                3: 'tga',
                4: 'jpg',
                5: 'tif'}
            return redshift_Image_format.get(redshift_format_number)
        if render_engine == 'vray':
            vray_format = pm.getAttr('vraySettings.imageFormatStr')
            if vray_format == None:
                return 'png'
            return vray_format
        if render_engine == 'mentalRay' or render_engine == 'mayaSoftware' or render_engine == 'mayaHardware' or render_engine == 'mayaHardware2' or render_engine == 'turtle':
            Image_format_number = cmds.getAttr("defaultRenderGlobals.imageFormat")
            Image_Format = {
                0: 'gif',
                1: 'pic',
                2: 'rla',
                3: 'tif',
                4: 'tif16',
                5: 'sgi',
                6: 'als',
                7: 'iff',
                8: 'jpg',
                9: 'eps',
                10: 'iff16',
                11: 'cin',
                12: 'yuv',
                13: 'sgi16',
                16: 'sgi16',
                19: 'tga',
                20: 'bmp',
                23: 'avi',
                31: 'psd',
                32: 'png',
                35: 'dds',
                36: 'Layered(psd)',
                51: 'exr'}
            return Image_Format.get(Image_format_number)

    def get_image_namespace(self):
        index = 0
        render_engine = str(self.GetCurrentRenderer())
        name_space = {
            1: 'name',
            2: 'name.ext',
            3: 'name.#.ext',
            4: 'name.ext.#',
            5: 'name.#',
            6: 'name#.ext',
            7: 'name_#.ext',
            8: 'namec',
            9: 'namec.ext'}
        if render_engine != 'vray':
            if cmds.getAttr("defaultRenderGlobals.animation") == False and cmds.getAttr(
                    "defaultRenderGlobals.outFormatControl") == 1 and cmds.getAttr(
                    "defaultRenderGlobals.periodInExt") == 1:
                index = 1
            elif cmds.getAttr("defaultRenderGlobals.animation") == False and cmds.getAttr(
                    "defaultRenderGlobals.outFormatControl") == 0 and cmds.getAttr(
                    "defaultRenderGlobals.periodInExt") == 1:
                index = 2
            elif cmds.getAttr("defaultRenderGlobals.animation") == True and cmds.getAttr(
                    "defaultRenderGlobals.outFormatControl") == 0 and cmds.getAttr(
                    "defaultRenderGlobals.periodInExt") == 1 and cmds.getAttr(
                    "defaultRenderGlobals.putFrameBeforeExt") == 1:
                index = 3
            elif cmds.getAttr("defaultRenderGlobals.animation") == True and cmds.getAttr(
                    "defaultRenderGlobals.outFormatControl") == 0 and cmds.getAttr(
                    "defaultRenderGlobals.periodInExt") == 1 and cmds.getAttr(
                    "defaultRenderGlobals.putFrameBeforeExt") == 0:
                index = 4
            elif cmds.getAttr("defaultRenderGlobals.animation") == True and cmds.getAttr(
                    "defaultRenderGlobals.outFormatControl") == 1 and cmds.getAttr(
                    "defaultRenderGlobals.periodInExt") == 1:
                index = 5
            elif cmds.getAttr("defaultRenderGlobals.animation") == True and cmds.getAttr(
                    "defaultRenderGlobals.outFormatControl") == 0 and cmds.getAttr(
                    "defaultRenderGlobals.periodInExt") == 0 and cmds.getAttr(
                    "defaultRenderGlobals.putFrameBeforeExt") == 1:
                index = 6
            elif cmds.getAttr("defaultRenderGlobals.animation") == True and cmds.getAttr(
                    "defaultRenderGlobals.outFormatControl") == 0 and cmds.getAttr(
                    "defaultRenderGlobals.periodInExt") == 2 and cmds.getAttr(
                    "defaultRenderGlobals.putFrameBeforeExt") == 1:
                index = 7
            elif cmds.getAttr("defaultRenderGlobals.animation") == True and cmds.getAttr(
                    "defaultRenderGlobals.outFormatControl") == 1 and cmds.getAttr(
                    "defaultRenderGlobals.periodInExt") == 1:
                index = 8
            elif cmds.getAttr("defaultRenderGlobals.animation") == True and cmds.getAttr(
                    "defaultRenderGlobals.outFormatControl") == 0 and cmds.getAttr(
                    "defaultRenderGlobals.periodInExt") == 1:
                index = 9
        else:
            pass
        if index not in [0, 3, 6, 7]:
            self.writing_error(20002, "current namespace is %s ," % (name_space.get(index)))

    def has_renderable_layer(self):
        render_layer = [i.name() for i in pm.PyNode("renderLayerManager.renderLayerId").outputs() if
                        i.type() == "renderLayer" if i.renderable.get()]
        if len(render_layer) == 0:
            self.writing_error(20003)

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
            prefix = pm.getAttr('defaultRenderGlobals.imageFilePrefix')
        else:
            prefix = pm.getAttr('vraySettings.fileNamePrefix')

        if prefix == "" or prefix == None:
            prefix = self.GetStrippedSceneFileName()

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
                           "redshift": "redshift",
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






class Asset(dict, Maya):

    def __init__(self):
        Maya.__init__(self)
        dict.__init__(self)
        self.func_list = {
            'reference': self.get_reference,
            'file': self.get_file,
            'dynGlobals': self.get_legacy_particle,
        }

    def my_log(self, info, exit_code='', sleep=0.2):
        print ("%s" % (info))

    def get_all_render_layers(self):
        return [i.name() for i in pm.PyNode("renderLayerManager.renderLayerId").outputs() if
                i.type() == "renderLayer"]

    def get_renderable_layer(self):
        return [i.name() for i in self.get_all_render_layers() if i.renderable.get()]

    def get_assets_from_name(self, node_name):
        if pm.objExists(node_name):
            node_type = pm.PyNode(node_name).type()
            return self.func_list[node_type](node_name)

    def get_all_assets(self):
        for i in self.func_list:
            self.asset_dict[i] = self.func_list[i]()
        return self.asset_dict

    def get_assets_from_type(self, node_type):
        # print node_type
        if node_type in self.func_list:
            return self.func_list[node_type]()

    def get_layer_overrides(self, node, attr):
        if node.hasAttr(attr):
            connections = cmds.listConnections(node + "." + attr, plugs=True)
            if connections:
                return True
            else:
                return False
        else:
            return False

    def get_node_attr_over(self, node, attr, layer):
        if node.hasAttr(attr):
            connections = cmds.listConnections(node + "." + attr, plugs=True)
            if connections:
                for connection in connections:
                    if connection:

                        node_name = connection.split('.')[0]
                        if node_name == layer and cmds.nodeType(node_name) == 'renderLayer':
                            attr_name = '%s.value' % '.'.join(connection.split('.')[:-1])
                            return cmds.getAttr(attr_name)
                        else:
                            return cmds.getAttr(node + "." + attr)

            else:
                return node.attr(attr).get()
        else:
            return 0

    def get_node_attr_val(self, node, attr):
        if node.hasAttr(attr):
            return node.attr(attr).get()
        else:
            return 0

    def get_env_val(self, path):
        pass

    def from_path_to_dict(self, source_path, dict_key, amin_attr=0):
        textures = {}
        env_re = re.compile(r'^\${?(\w+)}?', re.I)
        textures[dict_key] = {}
        textures[dict_key]["missing"] = []
        textures[dict_key]["local_path"] = []
        textures[dict_key]["env"] = {}
        textures[dict_key]["source_path"] = []
        if source_path:
            source_path = os.path.normpath(source_path)
            textures[dict_key]["source_path"].append(source_path)
            r = env_re.findall(source_path)
            if r:
                if os.environ.setdefault(r[0], ""):
                    env_val = os.path.normpath(os.getenv(r[0]))
                    textures[dict_key]["env"][r[0]] = env_val
                    source_path = source_path.replace("${" + r[0] + "}", env_val)
                    # print source_path

            local_path = [i for i in self.file_images(source_path, amin_attr)]
            if local_path:
                textures[dict_key]["local_path"] += local_path
            else:
                textures[dict_key]["missing"].append(source_path)
        return textures

    def get_file_from_folder(self, folder, prefix="*", ext="*"):
        files = []
        p = re.compile(r'^(?:[a-z][:][\\/]|[\\\\]|(?:\${?))', re.I)
        if not p.findall(folder):
            folder = os.path.join(pm.workspace(q=1, fullName=1), folder)
        if os.path.exists(folder) and os.path.isdir(folder):

            file_glob = os.path.normpath(os.path.join(folder, prefix + "*" + ext))
            print file_glob
            for i in glob.glob(file_glob):
                yield i
        elif os.path.exists(folder) and os.path.isfile(folder):

            yield folder

    def get_node_paths(self, node, attr, amin_attr, layer=None):
        if layer:
            source_path = self.get_node_attr_over(node, attr, layer)
            layer = "_" + layer
        else:
            source_path = self.get_node_attr_val(node, attr)
            layer = ""
        attr = "_" + attr
        dict_key = node + attr + layer
        textures = self.from_path_to_dict(source_path, dict_key, amin_attr)
        return textures

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
                    if os.path.exists(udim_str):
                        yield udim_str

                else:

                    file_name_glob = file_name.replace(r"[\d]+", "*").replace("\\", "")

                    p2 = re.compile(file_name, re.I)
                    # print glob.glob(os.path.join(dir_path,file_name_glob).replace('\\', separator))
                    for i in glob.glob(os.path.join(dir_path, file_name_glob)):
                        file_name_g = os.path.split(i)[1]
                        # print file_name_g
                        yield i.replace('\\', separator)
                        # if p2.match(file_name_g):
                        # yield i.replace('\\', separator)

    def get_legacy_particle(self, node_name=None):
        # if "particles" not in pm.workspace.fileRules.keys():
        #     self.writing_error(100000)
        textures = {}

        def_name = sys._getframe().f_code.co_name
        pprint.pprint("start %s ..." % def_name)
        nodes = []
        if node_name:
            nodes.append(pm.PyNode(node_name))
        else:
            nodes = pm.ls(type="dynGlobals")
            cache_folder_list = []
            for i in nodes:
                dict_key = i.name() + "_cacheDirectory"
                textures[dict_key] = {}
                textures[dict_key]["missing"] = []
                textures[dict_key]["local_path"] = []
                textures[dict_key]["env"] = {}
                textures[dict_key]["source_path"] = []
                if i.cacheDirectory.get():
                    if i.cacheDirectory.get().strip():
                        cache_folder = os.path.normpath(
                            os.path.join(pm.workspace.fileRules.get("particles", "cache/particles"),
                                         i.cacheDirectory.get().strip()))
                        cache_folder_strartup = cache_folder + "_startup"
                        cache_folder_list += [i for i in self.get_file_from_folder(cache_folder)]
                        cache_folder_list += [i for i in self.get_file_from_folder(cache_folder_strartup)]
                        textures[dict_key]["source_path"].append(cache_folder)
                        if cache_folder_list:
                            textures[dict_key]["local_path"] += cache_folder_list
                        else:
                            textures[dict_key]["missing"].append(cache_folder)

        pprint.pprint("end %s ..." % def_name)
        return textures

    def get_reference(self):
        def_name = sys._getframe().f_code.co_name
        pprint.pprint("start %s ..." % def_name)
        textures = {}
        env_re = re.compile(r'^\${?(\w+)}?', re.I)
        all_reference = pm.listReferences(recursive=1)

        for i in all_reference:
            dict_key_unresolvedPath = i.refNode.name() + "_unresolvedPath"
            unresolvedPath_source_path = str(i.unresolvedPath())
            textures.update(self.from_path_to_dict(unresolvedPath_source_path, dict_key_unresolvedPath))

            dict_key_unresolvedPath = i.refNode.name() + "_path"
            unresolvedPath_source_path = str(i.path)
            textures.update(self.from_path_to_dict(unresolvedPath_source_path, dict_key_unresolvedPath))
        pprint.pprint("end %s ..." % def_name)
        return textures

    def get_file(self, node_name=None):
        def_name = sys._getframe().f_code.co_name
        pprint.pprint("start %s ..." % def_name)
        files = {}
        textures = {}
        nodes = []
        if node_name:
            nodes.append(pm.PyNode(node_name))
        else:
            nodes = pm.ls(type="file")
        for node_i in nodes:
            # print node_i.name()
            amin_attr = 0
            # pprint.pprint("the file node is " + node_i)
            overrides = 0
            for attr in ["useFrameExtension", "uvTilingMode", "computedFileTextureNamePattern", "fileTextureName"]:
                if self.get_layer_overrides(node_i, attr):
                    overrides = 1
                    print "the %s is have layer overrides " % node_i
                    break
            if overrides:
                for layer in self.get_all_render_layers():
                    if self.get_node_attr_over(node_i, "useFrameExtension", layer) or self.get_node_attr_over(node_i,
                                                                                                              "uvTilingMode",
                                                                                                              layer):
                        amin_attr = 1
                    files.update(self.get_node_paths(node_i, "computedFileTextureNamePattern", amin_attr, layer))
                    files.update(self.get_node_paths(node_i, "fileTextureName", amin_attr, layer))
            else:
                if self.get_node_attr_val(node_i, "useFrameExtension") or self.get_node_attr_val(node_i,
                                                                                                 "uvTilingMode"):
                    amin_attr = 1
                files.update(self.get_node_paths(node_i, "computedFileTextureNamePattern", amin_attr))
                files.update(self.get_node_paths(node_i, "fileTextureName", amin_attr))

        pprint.pprint("end %s ..." % def_name)

        return files

    def func_filter_dict(self):
        pass

    def get_asset_dict(self):
        asset = []
        missing_file = []
        env_dict = {}
        tips_missing_file = []
        self.get_all_assets()
        if self.asset_dict:
            for i in self.asset_dict:
                for j in self.asset_dict[i]:
                    if len(self.asset_dict[i][j]["local_path"]) > 0:
                        asset.append({"node":j,"path":self.asset_dict[i][j]["local_path"]})
                    if len(self.asset_dict[i][j]["missing"]) > 0:
                        missing_file.append({"node":j,"path":self.asset_dict[i][j]["missing"]})
                    for env_i in self.asset_dict[i][j]["env"]:
                        if env_i not in env_dict:
                            env_dict[env_i] = self.asset_dict[i][j]["env"][env_i]
        self.asset_info_dict["asset"] = asset
        self.asset_info_dict["missing_file"] = missing_file

        for m_file_i in self.asset_info_dict["missing_file"]:
            for m_file_j in m_file_i["path"]:
                if m_file_j not in tips_missing_file:
                    tips_missing_file.append(m_file_j)

        if len(self.asset_info_dict["missing_file"])>0:
            self.writing_error(20001,tips_missing_file)
        return self.asset_info_dict,self.tips_info_dict,env_dict



class Config(dict,Maya):
    def __init__(self,options):
        dict.__init__(self)
        Maya.__init__(self)
        self.options = options
        for i in options:
            self[i] = options[i]

    def start_open_maya(self):
        self.print_info("start maya ok.")
        self.print_info("open maya file: " + self["cg_file"])
        self["cg_project"] = os.path.normpath(self["cg_project"]).replace('\\', '/')
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

    def check_maya_version(self, maya_file, cg_version):
        result = None
        maya_file = self.unicode_to_str(maya_file)
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
            if float(result) == float(cg_version):
                pass
            else:
                self.writing_error(25013, "maya file version Maya%s" % result)

    def gather_task_dict(self):
        analyze_render_setting = Analyze(self.options)
        info_dict = analyze_render_setting.get_layer_settings()
        for i in info_dict[0]:
            self.scene_info_dict[i] = info_dict[0][i]
        for i in info_dict[1]:
            self.tips_info_dict[i] = info_dict[1][i]

    def gather_asset_dict(self):
        analyze_Asset = Asset()
        info_dict_2 = analyze_Asset.get_asset_dict()
        for i in info_dict_2[0]:
            self.asset_info_dict[i] = info_dict_2[0][i]
        for i in info_dict_2[1]:
            self.tips_info_dict[i] = info_dict_2[1][i]
        if "defaultRenderLayer" in self.scene_info_dict:
            self.scene_info_dict["defaultRenderLayer"]["env"] = info_dict_2[2]


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
            with open(info_file, 'w+') as f:
                f.write(json.dumps(json_src,indent=2))
        except Exception as err:
            print  err
            pass

    def write_asset_info(self):
        info_file_path = os.path.dirname(self["asset_json"])
        print "write info to asset.json"
        if not os.path.exists(info_file_path):
            os.makedirs(info_file_path)
        try:
            info_file = self["asset_json"]
            self.asset_info_dict['scene_file'] = [self.str_to_unicode(self["cg_file"])]
            json_src = self.asset_info_dict
            print json_src
            with open(info_file, 'w+') as f:
                f.write(json.dumps(json_src,ensure_ascii=False,indent=2).decode('utf8'))
        except Exception as err:
            print  err
            pass

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
                f.write(json.dumps(json_src,indent=2))
        except Exception as err:
            print  err
            pass






def analyze_maya(options):
    print "88888888888888"
    print options
    print type(options)
    analyze = Config(options)

    analyze.check_maya_version(options["cg_file"],options["cg_version"])
    analyze.start_open_maya()

    analyze.gather_task_dict()
    analyze.print_info("get layer setting info ok.")

    analyze.gather_asset_dict()
    analyze.print_info("gather assets  info ok.")

    analyze.print_info("gather tips  info ok.")


    analyze.write_task_info()
    analyze.print_info("write task info ok.")

    analyze.write_asset_info()
    analyze.print_info("write asset info ok.")

    analyze.write_tips_info()
    analyze.print_info("write tips info ok.")

    analyze.print_info("analyze maya info ok.")



if __name__ == '__main__':
    options = {}
    '''
    import sys
    sys.path.append("E:\\PycharmProjects\\maya_analyze")
    import Analyze
    a = Analyze.Asset()
    for i in a.ceate_asset():
        print i, a.ceate_asset()[i]
    '''
    # analyze = Analyze(options)
    # print dir(analyze)
    # print analyze.get_default_render_globals("defaultRenderLayer")
    # asset = Asset()
    #a = Asset()
    # print a.get_reference()
    # print a.get_file()
    # for i in a.get_file_from_folder("E:\\fang\\fagng\\cache\\particles\\legacy_par_2014_startup","particleShape",ext=".*"):
    #     print i
    #print a.get_legacy_particle()
    #a.get_assets_from_name("file1")
    # for i in  a.ceate_asset():
    #     print i,a.ceate_asset()[i]
    analyze_asset = Asset()
    print analyze_asset.get_asset_dict()
    # for i in analyze_asset.get_all_assets():
    #     print analyze_asset.get_all_assets()[i]