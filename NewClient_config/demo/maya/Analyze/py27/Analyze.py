#!/usr/bin/env python
# encoding:utf-8
# -*- coding: utf-8 -*-
# -----M20180321-----
import os
import re
import sys
import json
import subprocess
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

# defaultencoding = 'utf-8'
# if sys.getdefaultencoding() != defaultencoding:
#     reload(sys)
#     sys.setdefaultencoding(defaultencoding)

if "maya" in sys.executable.lower():
    import pymel.core as pm
    import maya.cmds as cmds
    import maya.mel as mel


def print_def_name(func):
    # fname = func.func_name
    
    def print_name(*args, **kw):
        print "strat %s " % func.__name__
        func(*args, **kw)
        print "end %s " % func.__name__
    
    return print_name


class Maya(object):
    def __init__(self):

        self.scene_info_dict = collections.OrderedDict()
        self.asset_info_dict = collections.OrderedDict()
        self.tips_info_dict = collections.OrderedDict()
        self.upload_info_dict = collections.OrderedDict()
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
            # info = self.unicode_to_str(info)
            info = self.str_to_unicode(info)
        if error_code in self.tips_info_dict:
            if isinstance(self.tips_info_dict[error_code], list) and len(self.tips_info_dict[error_code]) > 0 and \
                            self.tips_info_dict[error_code][0] != info:
                error_list = self.tips_info_dict[error_code]
                error_list.append(info)
                self.tips_info_dict[error_code] = error_list
        else:
            if type(info) == unicode and info != "":
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

    def inter_path(self,path):
        first_two = path[0:2]
        if first_two in ('//', '\\\\'):
            norm_path = path.replace('\\', '/')
            index = norm_path.find('/', 2)
            if index <= 2:
                return False
            return True

    def parse_inter_path(self,path):
        first_two = path[0:2]
        if first_two in ('//', '\\\\'):
            norm_path = path.replace('\\', '/')
            index = norm_path.find('/', 2)
            if index <= 2:
                return ''
            return path[:index], path[index:]

    def convert_path(self,user_input, path):
        """
        :param user_input: e.g. "/1021000/1021394"
        :param path: e.g. "D:/work/render/19183793/max/d/Work/c05/111409-021212132P-embedayry.jpg"
        :return: \1021000\1021394\D\work\render\19183793\max\d\Work\c05\111409-021212132P-embedayry.jpg
        """
        result_file = path
        lower_file = os.path.normpath(path.lower()).replace('\\', '/')
        file_dir = os.path.dirname(lower_file)
        if file_dir is None or file_dir.strip() == '':
            pass
        else:
            if self.inter_path(lower_file) is True:
                start, rest = self.parse_inter_path(lower_file)
                # result_file = user_input + '/net/' + start.replace('//', '') + rest.replace('\\', '/')
                result_file = user_input + start + rest.replace('\\', '/')
            else:
                result_file = user_input + '\\' + path.replace('\\', '/').replace(':', '')
    
        result = os.path.normpath(result_file)
        result = result.replace("\\", "/")
        return result



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
        if encode_str == None or encode_str == "" or encode_str == 'Null' or encode_str == 'null':
            encode_str = ""
            return encode_str
        elif isinstance(encode_str, unicode):
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
        elif isinstance(str1, str):
            return str1
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
            return check_str
        else:
            return False

    def check_file_size(self,file):
        file_mtime = time.ctime(os.stat(file).st_mtime)
        file_size = os.path.getsize(file)
        return file_mtime,file_size

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
        scene_info_common_dict['image_file_prefix'] = self.GetMayaOutputPrefix(layer)
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
        # scene_info_common_dict["file_name"] = str(pm.renderSettings(fin=1, cam='', lyr=layer))
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
        if arnold_options_node.hasAttr("skipLicenseCheck"):
            scene_info_option_dict["skipLicenseCheck"] = str(arnold_options_node.skipLicenseCheck.get())
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
            
        aovs_list = self.getArnoldElements()
        denoise_list = []
        if len(aovs_list) != 0:
            for aovName in aovs_list:
                aov_node = pm.PyNode(aovName)
                if aov_node.hasAttr("denoise"):
                    enabled = int(pm.getAttr(str(aovName) + ".denoise"))
                    if enabled == 1:
                        denoise_list.append(aovName)
        if len(denoise_list) != 0:
            self.writing_error(25023,"%s come into use Denoise with Optix,(Arnold) don\'t support  GPU denoise..."% (','.join(denoise_list)))
            
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
            
        if vraySettings_node.hasAttr("productionEngine"):
            productionEngine_dict = {0:"CPU",1:"OpenCL",2:"CUDA"}
            productionEngine = vraySettings_node.productionEngine.get()
            scene_info_option_dict["productionEngine"] = productionEngine_dict[productionEngine]
            if productionEngine != 0 and self["platform"] != "21":
                self.writing_error(25022,"Current Vray productionEngine is %s,Please modify" % scene_info_option_dict["productionEngine"])
    
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
        renderman_options = pm.PyNode("renderManRISGlobals")
        if renderman_options.hasAttr("rman__torattr___motionBlur"):
            scene_info_option_dict["rman__torattr___motionBlur"] = self.unicode_to_str(renderman_options.rman__torattr___motionBlur.get())
        return scene_info_option_dict

    def get_krakatoa_setting(self, layer):
        scene_info_option_dict = collections.OrderedDict()
        # self.scene_info_dict[layer]["option"] = scene_info_option_dict
        return scene_info_option_dict

    def get_layer_settings(self, render_layer=None):
        self.defaultRG = pm.PyNode("defaultRenderGlobals")
        # self.show_hide_node()
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
                        elif renderer == 'renderManRIS' or renderer == 'renderMan':
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
                self.print_info (traceback.format_exc())
                self.writing_error(25018)
                # raise Exception("Can't switch renderlayer :  " + layer)
        return self.scene_info_dict,self.tips_info_dict

    def getArnoldElementNames(self):
        elementNames = []
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
        elementNames = []
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

        elementNames = []
        REs = pm.ls(type='RedshiftAOV')
        for RE in REs:
            enabled = int(pm.getAttr(str(RE) + ".enabled"))
            if enabled == 1:
                elementNames.insert(0, RE)

        return elementNames

    def getMentalRayElementNames(self, currentRenderLayer):

        elementNames = []
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
        elementNames = []
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
                    self.print_info (all_node)
                    for node in all_node:
                        if node_type == 'cacheFile':
                            b = cmds.getAttr(node + ".cacheName")
                            c = cmds.getAttr(node + ".cachePath")
                            if c.endswith("/"):
                                c = c.strip()
                                c = c[:-1]
                            self.print_info(c + "/" + b + ".xml")
                            file_path = c + "/" + b + ".xml"
                        else:
                            file_path = cmds.getAttr(node + "." + attr_name)
                        # node.attr(attr_name).set(l=0)
                        # file_path = node.attr(attr_name).get()
                        asset_dict_keys = node_type + '::' + attr_name
                        asset_dict_value = node + '::' + file_path
                        asset_dict[asset_dict_keys] = asset_dict_value

        print '+' * 40
        self.print_info(asset_dict)
        return asset_dict

    def gather_asset(self, asset_type, asset_list, asset_dict):
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
        if render_engine == 'renderManRIS' or render_engine == 'renderMan':
            Image_format_number = cmds.getAttr("rmanFinalOutputGlobals0.rman__riopt__Display_type")
            return Image_format_number


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

    def get_motionblur(self):
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

        fileName = cmds.file(q=1, sceneName=1)
        fileName = pm.mel.basename(fileName, ".mb")
        fileName = pm.mel.basename(fileName, ".ma")
        return fileName

    def GetMayaOutputPrefix(self, layer):
        prefix = ""
        renderer = str(self.GetCurrentRenderer())
        if renderer != "vray":
            prefix = pm.getAttr('defaultRenderGlobals.imageFilePrefix')
        else:
            prefix = pm.getAttr('vraySettings.fileNamePrefix')

        if prefix == "" or prefix == None:
            prefix = ""
            # prefix = os.path.splitext(os.path.basename(pm.system.sceneName()))[0].strip()

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
        prefix = self.str_to_unicode(prefix)
        return prefix

    def GetRenderableCameras_bak1(self, ignoreDefaultCameras):

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
        '''
        判断一段字符串
        :param path:  is string
        :return: true or false
        '''
        if path:
            path = path.replace("\\", "/")
            if ":" in path:
                return 1
            if path.startswith("//"):
                return 1
            if self.check_contain_chinese(path):
                self.print_info(path)
                return 1

    def check_layer_renderer(self, layer):
        renderer = str(self.GetCurrentRenderer())
        self.print_info("current renderer is : %s " % renderer)
        plugins_rederer = {"arnold": "mtoa",
                           "vray": "vrayformaya",
                           "redshift": "redshift",
                           "renderManRIS": "RenderMan_for_Maya",
                           "renderMan": "RenderMan_for_Maya",
                           "renderman": "RenderMan_for_Maya",
                           "MayaKrakatoa": "krakatoa",
                           "mentalRay": "mentalray"
                           
                           }
        plugins_rederer.setdefault(renderer)
        if plugins_rederer[renderer]:
            if plugins_rederer[renderer] not in self["cg_plugins"]:
                self.writing_error(25008, "render layer: %s \'s renderer is %s ,please confirm configure plugins" % (
                layer, renderer))
                return False
        elif renderer == "mentalRay" and int(self["cg_version"]) > 2016.5 and plugins_rederer[renderer] not in self["cg_plugins"]:
            self.writing_error(25008,
                               "render layer: %s \'s renderer is %s ,above version of maya2017(contain),  please confirm configure mentalRay" % (
                               layer, renderer))
            return False
        elif renderer in ["mayaHardware", "mayaHardware2", "mayaVector"]:
            self.writing_error(25014, "render layer: %s \'s renderer is %s   please change" % (layer, renderer))
            return False
        
        elif "RenderMan_for_Maya" in self["cg_plugins"] and "mtoa" in self["cg_plugins"] or "vrayformaya" in self["cg_plugins"] or "redshift" in self["cg_plugins"] or "mentalray" in self["cg_plugins"]:
            self.writing_error(25024, "plugins list : %s   please change" % (self["cg_plugins"]))
            return False
        else:
            pass
        return True


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
            return self.path + "/" + "".join([self.head, self.padding * "#",
                                              self.tail, " ", str(self.start), "-", str(self.end)])
        else:
            #            bb.###.jpg 1-6 (1-3 5-6 mising 4)
            return self.path + "/" + "".join([self.head, self.padding * "#",
                                              self.tail, " ", str(self.start), "-", str(self.end),
                                              " ( missing ",
                                              ",".join([str(i) for i in self.missing]),
                                              " ) "])
    
    def __iter__(self):
        def filesequence_iter_generator():
            for frame in range(self.start, self.end + 1):
                if frame not in self.missing:
                    yield "".join([self.head, str(frame).zfill(self.padding),
                                   self.tail])
        
        return filesequence_iter_generator()
    
    def get_frame_file(self, frame):
        return "".join([self.path, "/", self.head,
                        str(frame).zfill(self.padding), self.tail])
    
    @classmethod
    def get_from_string(cls, string):
        # print string
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
        return os.path.normpath(os.path.join(self.path, "".join([self.head, self.padding * "#", self.tail])))
    
    @property
    def startFileName(self):
        baseName = "".join([self.head, str(self.start).zfill(self.padding),
                            self.tail])
        return os.path.normpath(os.path.join(self.path, baseName))
    
    @property
    def frames(self):
        return self.end - self.start + 1 - len(self.missing)
    
    @property
    def frameinfo(self):
        return [frame for frame in range(self.start, self.end + 1)
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
        return [frame for frame in range(self.start, self.end + 1)
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
            black = [frame
                     for frame in range(self.start, self.end + 1)
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
                    for i in range(self.start, self.end + 1):
                        if mark in black:
                            black.remove(mark)
                            mark += 1
                
                if self.end in black:
                    mark = self.end
                    for i in range(self.start, self.end + 1):
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
        
        single_frame2 = single_frame.replace(number, str(int(number) + 1).zfill(len(number)))
        seq, others = FileSequence.find([single_frame, single_frame2])
        
        return FileSequence(seq[0].path, seq[0].head, seq[0].tail,
                            seq[0].start, seq[0].end - 1, seq[0].padding,
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
                head, tail = i.split(padding * "#")
                start = sequences[i][0]
                end = sequences[i][-1]
                
                if actual_frange:
                    missing = [frame for frame in Frames(actual_frange)
                               if frame not in sequences[i]]
                else:
                    missing = [frame for frame in range(start, end + 1)
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
                    
                    temp += [file, files[index + 1]]
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
        
        # print components, numberIndex
        for i in sorted(numberIndex.keys(), reverse=1):
            r1 = re.findall(r'^(%s)(\d{%s})(%s)$' % ("".join(components[:i]),
                                                     len(numberIndex[i]), "".join(components[i + 1:])),
                            file2)
            r2 = re.findall(r'^(%s)(-{1}\d{%s})(%s)$' % ("".join(components[:i]),
                                                         len(numberIndex[i]) - 1, "".join(components[i + 1:])),
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


class Asset(dict, Maya):
    ASS_FILES = []
    ASS_FILES_AN = []
    
    RS_FILES = []
    RS_FILES_AN = []
    
    VRSCENE_FILES = []
    VRSCENE_FILES_AN = []
    
    MI_FILES = []
    MI_FILES_AN = []
    
    rib_files = []
    rib_files_an = []

    def __init__(self):
        Maya.__init__(self)
        dict.__init__(self)
        self.func_list = {
            'reference': self.get_reference,
            'file': self.get_file,
            'dynGlobals': self.get_legacy_particle,
            'AlembicNode': self.get_AlembicNode,
            
        }

    def my_log(self, info, exit_code='', sleep=0.2):
        print ("%s" % (info))

    def get_all_render_layers(self):
        '''
        :return: returns all render layers  of  the scene
        '''
        return [i.name() for i in pm.PyNode("renderLayerManager.renderLayerId").outputs() if
                i.type() == "renderLayer"]

    def get_renderable_layer(self):
        '''
        :return: returns all open renderable render  layers  of  the scene
        '''
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

    def get_path_env_val(self, source_path):
        '''

        :param source_path: path
        :return: the path is have env ,if have env ,return the env name and env val,if dont have return False
        '''
        env_re = re.compile(r'\${?(\w+)}?', re.I)
        r = env_re.findall(source_path)
        env_val = {}
        if r:
            for r_i in r:
                if os.environ.setdefault(r_i, ""):
                    val = os.path.normpath(os.getenv(r_i))
                    env_val[r_i] = val
                else:
                    env_val[r_i] = None
        return env_val

    def get_env_path_normpath(self, path):
        return os.path.normpath(os.path.expandvars(path))

    def get_node_overrides_able(self, node, attr):
        '''

        :param node: node name ,type str
        :param attr: node attr ,type str
        :return:is the attr on node have overrides,type  boolean,
        '''
        if node.hasAttr(attr):
            connections = cmds.listConnections(node + "." + attr, plugs=True)
            if connections:
                return True
            else:
                return False
        else:
            return False

    def get_node_attr_over(self, node, attr, layer=None):
        '''

        :param node:  node name
        :param attr: node attribute
        :param layer: render laye name
        :return: returns the value of node's attribute
        '''
    
        if node.hasAttr(attr):
            if layer:
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
                return node.attr(attr).get()
    
        else:
            self.print_info("the node %s dont has  %s " % (node, attr))
            return ("dont has attr :: the node %s dont has  %s " % (node, attr))

    def get_node_attr_val(self, node, attr):
        if node.hasAttr(attr):
            return node.attr(attr).get()
        else:
            return ""

    def get_dict_from_path(self, source_path, dict_key, amin_attr_val=0):
        '''

        :param source_path:
        :param dict_key:
        :param amin_attr_val:
        :return:
        '''
        textures = {}
    
        env_re = re.compile(r'^\${?(\w+)}?', re.I)
        textures[dict_key] = {}
        textures[dict_key]["source_path"] = []
        textures[dict_key]["missing"] = []
        textures[dict_key]["local_path"] = []
        textures[dict_key]["env"] = {}
    
        if source_path:
            source_path = os.path.normpath(source_path)
            textures[dict_key]["source_path"].append(source_path)
        
            if self.get_path_env_val(source_path):
            
                for env_key in self.get_path_env_val(source_path):
                    env_val = self.get_path_env_val(source_path)[env_key]
                    if env_val:
                        textures[dict_key]["env"][env_key] = env_val
                        source_path = source_path.replace("${" + env_key + "}", env_val).replace("$" + env_key, env_val)
                        self.print_info(source_path)
        
            local_path = [i for i in self.file_images(source_path, amin_attr_val)]
            # print local_path
            if local_path:
                textures[dict_key]["local_path"] += local_path
            else:
                textures[dict_key]["missing"].append(source_path)
        else:
        
            textures[dict_key]["source_path"].append(source_path)
            textures[dict_key]["missing"].append("the path is None")
    
        return textures

    def get_files_from_folder(self, folder, prefix="*", ext="*"):
        files = []
        p = re.compile(r'^(?:[a-z][:][\\/]|[\\\\]|(?:\${?))', re.I)
        if not p.findall(folder):
            folder = os.path.join(pm.workspace(q=1, fullName=1), folder)
        # if os.path.exists(folder) and os.path.isdir(folder):
        file_glob = os.path.normpath(os.path.join(folder, prefix + "*." + ext))
        # print file_glob
        for i in glob.glob(file_glob):
            yield i
        if os.path.exists(folder) and os.path.isfile(folder):
            yield folder

    def get_node_paths_to_dict(self, node, attr, amin_attr_val=None, layer=None):
        '''
        :param node: node name
        :param attr: attr name
        :param amin_attr_val: node's amin attr
        :param layer:  render layer name
        :return: dict
        '''
        textures = {}
        if layer:
            source_path = self.get_node_attr_over(node, attr, layer)
            layer = "_" + layer
        else:
            source_path = self.get_node_attr_over(node, attr)
            layer = ""
        attr = "_" + attr
        dict_key = node + attr + layer
        if source_path and (isinstance(source_path, unicode) or isinstance(source_path, str)):
            if source_path and not source_path.startswith("dont has attr"):
                self.print_info(source_path)
                textures.update(self.get_dict_from_path(source_path, dict_key, amin_attr_val))
    
        elif source_path and isinstance(source_path, list):
            for path in source_path:
                if path:
                    textures.update(self.get_dict_from_path(path, dict_key, amin_attr_val))
        return textures

    def file_images(self, udim_str, amin_attr_val=0):
        if os.path.exists(udim_str) == 1 and amin_attr_val == 0:
            yield os.path.normpath(udim_str)
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
                if amin_attr_val:
                    sep_num_re = re.compile(r"[0-9]+(?=[^0-9]*$)", re.I)
                    sep_num = sep_num_re.findall(file_name)
                    if sep_num:
                        file_name = re.sub(sep_num[0], r"[\d]+", file_name)
            
                if file_name == file_name_src:
                    if os.path.exists(udim_str):
                        yield os.path.normpath(udim_str)
            
                else:
                
                    file_name_glob = file_name.replace(r"[\d]+", "*").replace("\\", "")
                
                    p2 = re.compile(file_name, re.I)
                    # print glob.glob(os.path.join(dir_path,file_name_glob).replace('\\', separator))
                    for i in glob.glob(os.path.join(dir_path, file_name_glob)):
                        file_name_g = os.path.split(i)[1]
                        # print file_name_g
                        yield os.path.normpath(i.replace('\\', separator))
                        # if p2.match(file_name_g):
                        # yield i.replace('\\', separator)

    def get_node_asstes(self, node_name, assts_attr=[], seq_attr=[]):
        textures = {}
    
        amin_attr_val = 0
        overrides = 0
    
        for over_attr_i in list(set(assts_attr + seq_attr)):
        
            if self.get_node_overrides_able(node_name, over_attr_i):
                overrides = 1
                self.print_info ("the %s is have layer overrides " % node_name)
                break
        if overrides:
            for layer in self.get_all_render_layers():
                if seq_attr:
                    for seq_attr_i in seq_attr:
                        if self.get_node_attr_over(node_name, seq_attr_i, layer):
                            amin_attr_val = 1
                            break
                if assts_attr:
                    for assts_attr_i in assts_attr:
                        textures.update(self.get_node_paths_to_dict(node_name, assts_attr_i, amin_attr_val, layer))
    
        else:
            if seq_attr:
                for seq_attr_i in seq_attr:
                    if self.get_node_attr_over(node_name, seq_attr_i):
                        amin_attr_val = 1
                        break
            if assts_attr:
                for assts_attr_i in assts_attr:
                    textures.update(self.get_node_paths_to_dict(node_name, assts_attr_i, amin_attr_val))
    
        return textures

    def get_legacy_particle(self, node_name=None):
        textures = {}
        if "particles" not in pm.workspace.fileRules.keys():
            self.writing_error(25020)
        else:
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
                            cache_folder_list += [i for i in self.get_files_from_folder(cache_folder, ext=".pdc")]
                            cache_folder_list += [i for i in
                                                  self.get_files_from_folder(cache_folder_strartup, ext=".pdc")]
                            textures[dict_key]["source_path"].append(cache_folder)
                            if cache_folder_list:
                                textures[dict_key]["local_path"] += cache_folder_list
                            else:
                                textures[dict_key]["missing"].append(cache_folder)
    
        return textures

    def get_disk_cache(self, node_name=None):
        def_name = sys._getframe().f_code.co_name
        self.print_info("start %s ..." % def_name)
        textures = {}
        if "diskCache" not in pm.workspace.fileRules.keys():
            self.writing_error(2520)
        else:
            nodes = []
            if node_name:
                nodes.append(pm.PyNode(node_name))
            else:
                nodes = pm.ls(type="diskCache")
            for node_i in nodes:
                dict_key = node_i.name() + "_cacheName"
                source_path = self.get_node_attr_val(node_i, "cacheName")
                if source_path:
                    source_path = os.path.normpath(os.path.join(pm.workspace.fileRules.get("diskCache"), source_path))
                
                    textures.update(self.get_dict_from_path(source_path, dict_key))
        self.print_info("end %s ..." % def_name)
        return textures

    def get_cacheFile(self, node_name=None):
        def_name = sys._getframe().f_code.co_name
        self.print_info("start %s ..." % def_name)
        textures = {}
    
        nodes = []
        if node_name:
            nodes.append(pm.PyNode(node_name))
        else:
            nodes = pm.ls(type="cacheFile")
        for node_i in nodes:
            files = []
            dict_key = node_i.name() + "_cachePath"
            textures[dict_key] = {}
            textures[dict_key]["missing"] = []
            textures[dict_key]["local_path"] = []
            textures[dict_key]["env"] = {}
            textures[dict_key]["source_path"] = []
        
            source_path = self.get_node_attr_val(node_i, "cachePath")
            cache_name = self.get_node_attr_val(node_i, "cacheName")
            if source_path and cache_name:
                if self.get_path_env_val(source_path):
                    textures[dict_key]["env"].update(self.get_path_env_val(source_path))
                    for i in self.get_path_env_val(source_path):
                        if self.get_path_env_val(source_path)[i]:
                            source_path = source_path.replace("${" + i + "}", self.get_path_env_val(source_path)[i])
                if cache_name.lower().endswith(".bin"):
                    textures[dict_key]["source_path"].append(os.path.join(source_path, cache_name))
                    cache_name.rsplit(".", 2)
                else:
                    textures[dict_key]["source_path"].append(os.path.join(source_path, cache_name + ".xml"))
                for i in ["xml", "mcc", "mcx", "bin", "mc"]:
                    files += self.get_files_from_folder(source_path, cache_name, i)
                if files:
                    textures[dict_key]["local_path"] += files
                else:
                    textures[dict_key]["missing"] += textures[dict_key]["source_path"]
    
        self.print_info("end %s ..." % def_name)
        return textures

    def get_fur(self, node_name=None):
        def_name = sys._getframe().f_code.co_name
        self.print_info("start %s ..." % def_name)
        textures = {}
        nodes = []
        if node_name:
            nodes.append(pm.PyNode(node_name))
        else:
            nodes = pm.ls(type="FurDescription")
            for node_i in nodes:
                for attr in node_i.listAttr():
                
                    if attr.find("Map") != -1:
                    
                        try:
                            ii = 0
                            for i in attr.get():
                                dict_key = str(attr) + str(ii)
                            
                                if i:
                                    ii = ii + 1
                                    textures.update(self.get_dict_from_path(i, dict_key))
                        except:
                            pass
    
        self.print_info("end %s ..." % def_name)
        return textures

    def get_reference(self):
        def_name = sys._getframe().f_code.co_name
        self.print_info("start %s ..." % def_name)
        textures = {}
        env_re = re.compile(r'^\${?(\w+)}?', re.I)
        all_reference = pm.listReferences(recursive=1)
    
        for i in all_reference:
            dict_key_unresolvedPath = i.refNode.name() + "_unresolvedPath"
            unresolvedPath_source_path = str(i.unresolvedPath())
            textures.update(self.get_dict_from_path(unresolvedPath_source_path, dict_key_unresolvedPath))
        
            dict_key_unresolvedPath = i.refNode.name() + "_path"
            unresolvedPath_source_path = str(i.path)
            textures.update(self.get_dict_from_path(unresolvedPath_source_path, dict_key_unresolvedPath))
        self.print_info("end %s ..." % def_name)
        return textures

    def get_file(self, node_name=None):
        textures = {}
        nodes = []
        if node_name:
            nodes.append(pm.PyNode(node_name))
        else:
            nodes = pm.ls(type="file")
        for node_i in nodes:
            textures.update(self.get_node_asstes(node_i, assts_attr=["fileTextureName"],
                                                 seq_attr=["useFrameExtension", "uvTilingMode"]))
            textures.update(self.get_node_asstes(node_i, assts_attr=["computedFileTextureNamePattern"],
                                                 seq_attr=["useFrameExtension", "uvTilingMode"]))
        return textures

    def get_AlembicNode(self, node_name=None):
        textures = {}
        nodes = []
        if node_name:
            nodes.append(pm.PyNode(node_name))
        else:
            nodes = pm.ls(type="AlembicNode")
        for node_i in nodes:
            textures.update(self.get_node_asstes(node_i, assts_attr=["abc_File"]))
            textures.update(self.get_node_asstes(node_i, assts_attr=["fns"]))
        return textures

    def get_imagePlane(self, node_name=None):
    
        textures = {}
        nodes = []
        if node_name:
            nodes.append(pm.PyNode(node_name))
        else:
            nodes = pm.ls(type="imagePlane")
        for node_i in nodes:
            textures.update(self.get_node_asstes(node_i, assts_attr=["imageName"], seq_attr=["useFrameExtension"]))
        return textures

    def get_psdFileTex(self, node_name=None):
    
        textures = {}
        nodes = []
        if node_name:
            nodes.append(pm.PyNode(node_name))
        else:
            nodes = pm.ls(type="psdFileTex")
        for node_i in nodes:
            textures.update(
                self.get_node_asstes(node_i, assts_attr=["fileTextureName"], seq_attr=["useFrameExtension"]))
        return textures

    def get_mentalrayIblShape(self, node_name=None):
        textures = {}
        nodes = []
        if node_name:
            nodes.append(pm.PyNode(node_name))
        else:
            nodes = pm.ls(type="mentalrayIblShape")
        for node_i in nodes:
            textures.update(self.get_node_asstes(node_i, assts_attr=["texture"], seq_attr=["useFrameExtension"]))
        return textures

    def get_mentalrayTexture(self, node_name=None):
    
        textures = {}
        nodes = []
        if node_name:
            nodes.append(pm.PyNode(node_name))
        else:
            nodes = pm.ls(type="mentalrayTexture")
        for node_i in nodes:
            textures.update(self.get_node_asstes(node_i, assts_attr=["fileTextureName"]))
        return textures

    def get_mentalrayOptions(self, node_name=None):
    
        textures = {}
        nodes = []
        if node_name:
            nodes.append(pm.PyNode(node_name))
        else:
            nodes = pm.ls(type="mentalrayOptions")
        for node_i in nodes:
            textures.update(self.get_node_asstes(node_i, assts_attr=["photonMapFilename"]))
            textures.update(self.get_node_asstes(node_i, assts_attr=["finalGatherFilename"]))
            textures.update(self.get_node_asstes(node_i, assts_attr=["finalGatherMergeFiles"]))
        return textures

    def get_mesh(self, node_name=None):
        textures = {}
        nodes = []
        if node_name:
            nodes.append(pm.PyNode(node_name))
        else:
            nodes = pm.ls(type="mesh")
        for node_i in nodes:
            mi_files = {}
            mi_files.update(self.get_node_asstes(node_i, assts_attr=["miProxyFile"]))
            textures.update(mi_files)
            if mi_files:
                for mi_key in mi_files:
                    sequences, others = FileSequence.find(list(mi_files[mi_key]["local_path"]), "mi")
                    for mi_i_s in sequences:
                        mi_an = os.path.normpath(mi_i_s.startFileName)
                        if mi_an not in self.MI_FILES and mi_an not in self.MI_FILES_AN:
                            self.MI_FILES.append(mi_an)
                    for mi_an in others:
                        if mi_an not in self.MI_FILES and mi_an not in self.MI_FILES_AN:
                            self.MI_FILES.append(mi_an)
    
        for mi_file in self.MI_FILES:
            get_file_mi = self.get_file_from_mi(mi_file)
            textures[mi_file] = {}
            textures[mi_file]["local_path"] = []
            textures[mi_file]["local_path"] += get_file_mi
            sequences, others = FileSequence.find(list(get_file_mi), "mi")
            for mi_i_s in sequences:
                mi_an = os.path.normpath(mi_i_s.startFileName)
                if os.path.exists(mi_an) and mi_an not in self.MI_FILES and mi_an not in self.MI_FILES_AN:
                    self.MI_FILES.append(mi_an)
            for mi_an in others:
                mi_an = os.path.normpath(mi_an)
                if os.path.exists(mi_an) and mi_an not in self.MI_FILES and mi_an not in self.MI_FILES_AN:
                    self.MI_FILES.append(mi_an)
    
        return textures

    def get_file_from_mi(self, mi_file):
        texture = []
        # print mi_file
        with open(mi_file, "rb") as mi_fb:
            for line in mi_fb:
                p = re.compile(r'.+\"((?:[a-z][:][\\/]|[\\\\]|(?:\.\./)|(?:\.\.\\))?[\w _\-.:()\\/$+#<f>]+\.[\w]+)\"$',
                               re.I)
                r = p.findall(line)
                rs_image = (
                    ".rstxbin", ".tga", ".dds", ".jpg", ".png", ".rsmap", ".iff", ".rs", ".exr", ".tiff", ".jpeg",
                    ".hdr",
                    ".bmp", ".als", ".cin", ".pic", ".rat", ".psd", ".psb", ".ies", ".gif", ".qtl", ".rla", ".rlb",
                    ".pix", ".sgi",
                    ".rgb", ".rgba", ".si", ".rs", ".tif", ".tif23", ".mi",
                    ".tif16", ".tx", ".vst", ".yuv", ".ptex", ".tex", ".dpx")
                if r:
                    for i in r:
                        if i.lower().endswith(rs_image):
                            if i.startswith(("../", "/../", "\\..\\", "..\\")):
                                i = os.path.normpath(
                                    os.path.abspath(os.path.dirname(os.path.abspath(rs_file)) + "\\" + i))
                        
                            texture.append(i)
        return texture

    def get_xgmPalette(self, node_name=None):
        textures = {}
        nodes = []
        if node_name:
            nodes.append(pm.PyNode(node_name))
        else:
            nodes = pm.ls(type="xgmPalette")
        for node_i in nodes:
            source_path = os.path.join(os.path.dirname(pm.system.sceneName()),
                                       self.get_node_attr_over(node_i, "xgFileName"))
        
            dict_key = node_i + "_" + "xgFileName"
        
            textures.update(self.get_dict_from_path(source_path, dict_key))
        return textures

    def get_xgen_with_maya_file(self):
        maya_files = []
        refer_dict = self.get_reference()
    
        for key in refer_dict:
            maya_files.append(refer_dict[key]["local_path"])
    
        maya_files.append(pm.system.sceneName())
        files = []
        for maya_file in maya_files:
            maya_path = os.path.dirname(maya_file)
            file_name = os.path.splitext(os.path.basename(maya_file))[0]
            files += [i for i in self.get_files_from_folder(maya_path, file_name, "xgen")]
            files += [i for i in self.get_files_from_folder(maya_path, file_name, "abc")]
            files += [i for i in self.get_files_from_folder(maya_path, file_name, "json")]
        return files

    def get_xgen_re_allattrs(self):
        import xgenm as xg
        import xgenm.xgGlobal as xgg
    
        if xgg.Maya:
            xgen_path = []
            palettes = xg.palettes()
            # print xg.rootDir()
            for palette in palettes:
            
                p1 = re.compile(r"(?<=map\(\')[\w _\-.:()\\/$/+{}']+(?=\'\))", re.I)
                p2 = re.compile(r"^\${.*", re.I)
                # p3 = re.compile(r'[a-z][:][\\/][\w _\-.:()\\/$+]+\.[\w]+',re.I)
                p3 = re.compile(r'[a-z][:][\\/][\w _\-.:()\\/$+]+', re.I)
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
                        # print " Object:" + object
                        attrs = xg.allAttrs(palette, description, object)
                    
                        for attr in attrs:
                            attr_Value = xg.getAttr(attr, palette, description, object)
                            # print "attr :" + attr
                            # print "attr_Value : " +attr_Value
                            if attr == "files":
                                Archive_files = self.get_xgen_Archive_files(attr_Value, description)
                            
                                xgen_path += Archive_files
                        
                            if attr == "cacheFileName":
                                self.print_info(attr_Value)
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
                                    # rr = xg.expandFilepath(rr.replace("${FXMODULE}", fxModule).replace("${DESC}", desc),description)
                                    rr = rr.replace("${FXMODULE}", fxModule).replace("${DESC}", desc)
                                    if rr:
                                        xgen_path.append(rr)
                            if r2:
                                for rr in r2:
                                    # rr = xg.expandFilepath(rr.replace("${FXMODULE}", fxModule).replace("${DESC}", desc), description)
                                    rr = rr.replace("${FXMODULE}", fxModule).replace("${DESC}", desc)
                                    if rr:
                                        xgen_path.append(rr)
                            if r3:
                                for rr in r3:
                                    # rr = xg.expandFilepath(rr.replace("${FXMODULE}", fxModule).replace("${DESC}", desc),description)
                                    rr = rr.replace("${FXMODULE}", fxModule).replace("${DESC}", desc)
                                    if rr:
                                        xgen_path.append(rr)
        
            xgen_path = [os.path.normpath(i.rstrip("/")) for i in set(xgen_path)]
            return set(xgen_path)

    def get_files_from_xgen_file(self, xgen_file):
        os.environ["DESC"] = ""
        os.environ["PROJECT"] = ""
        xgen_files = []
        xgDataPath = ""
        xgProjectPath = ""
        #
        re_attrs = [re.compile('\\$\\w+\\s*=\\s*map\\([\"\']([\\w${}/:]+)[\"\']\\);\\s*#', re.I),
                    re.compile(r'^(?:[a-z][:][\\/]|[\\\\]|[\${?])(?:[\w_\-.:()\\/$/+{}])+(?![ \t\r\n=])', re.I)]
    
        with open(xgen_file, "r") as fp:
            for line in fp:
                line = line.strip(' \t\r\n')
                # print line
                if cmp(line, "Palette") == 0:
                    line = fp.next()
                    line = line.strip(' \t\r\n')
                    Palette_name = line.split('\t', 3)[3]
                    self.print_info("Palette_name     " + Palette_name)
                
                    while line and cmp(line, "endAttrs"):
                        line = fp.next()
                        line = line.strip(' \t\r\n')
                        if line.startswith("xgDataPath"):
                            xgDataPath = line.split("\t")[2]
                            self.print_info (xgDataPath)
                        elif line.startswith("xgProjectPath"):
                            xgProjectPath = line.split("\t")[2]
                            self.print_info (xgProjectPath)
                            os.environ["PROJECT"] = xgProjectPath
                        
                            xgen_files.append(self.get_env_path_normpath(xgDataPath))
            
            
                elif cmp(line, "Description") == 0:
                    line = fp.next()
                    line = line.strip(' \t\r\n')
                    Description_name = line.split('\t', 3)[3]
                    self.print_info ("Description_name     " + Description_name)
                    os.environ["DESC"] = self.get_env_path_normpath(xgDataPath + "\\" + Description_name)
                
                    while line and cmp(line, "endAttrs"):
                        # print line.split("\t", 1)
                        line = fp.next()
                        line = line.strip(' \t\r\n')
            
            
                elif cmp(line, "ArchivePrimitive") == 0:
                    line = fp.next()
                    line = line.strip(' \t\r\n')
                    while line and cmp(line, "endAttrs"):
                    
                        if cmp(line.split("\t", 1)[0].strip(' \t\r\n'), "files") == 0:
                            # print line.split("\t",1)[1].strip(' \t\r\n')
                            xgen_files += self.get_xgen_Archive_files(line.split("\t", 1)[1].strip(' \t\r\n'),
                                                                      Description_name)
                        # print line
                        line = fp.next()
                        line = line.strip(' \t\r\n')
                        try:
                            for re_attr in re_attrs:
                                if re_attr.findall(line.split("\t", 1)[1].strip(' \t\r\n')):
                                    for i in re_attr.findall(line.split("\t", 1)[1].strip(' \t\r\n')):
                                        xgen_files.append(self.get_env_path_normpath(i))
                        except:
                            pass
            
            
            
            
                elif "FXModule" in line and line.strip(' \t\r\n').endswith("FXModule"):
                
                    while line and cmp(line, "endAttrs"):
                        if cmp(line.split("\t", 1)[0].strip(' \t\r\n'), "name") == 0:
                            FXModule_name = line.split("\t", 1)[1].strip(' \t\r\n')
                            os.environ["FXMODULE"] = FXModule_name
                            # print "FXModule_name    " + FXModule_name
                        line = fp.next()
                        line = line.strip(' \t\r\n')
                        try:
                            for re_attr in re_attrs:
                                if re_attr.findall(line.split("\t", 1)[1].strip(' \t\r\n')):
                                    for i in re_attr.findall(line.split("\t", 1)[1].strip(' \t\r\n')):
                                        xgen_files.append(self.get_env_path_normpath(i))
                        except:
                            pass
                elif cmp(line, "MapTextures") == 0:
                
                    while line and cmp(line, "endAttrs"):
                        line = fp.next()
                        line = line.strip(' \t\r\n')
                    
                        try:
                            self.print_info (line.rsplit("\t", 1)[1].strip(' \t\r\n'))
                            for re_attr in re_attrs:
                                if re_attr.findall(line.rsplit("\t", 1)[1].strip(' \t\r\n')):
                                    for i in re_attr.findall(line.rsplit("\t", 1)[1].strip(' \t\r\n')):
                                        xgen_files.append(self.get_env_path_normpath(i))
                        except:
                            pass
                else:
                    try:
                        for re_attr in re_attrs:
                            if re_attr.findall(line.split("\t", 1)[1].strip(' \t\r\n')):
                                for i in re_attr.findall(line.split("\t", 1)[1].strip(' \t\r\n')):
                                    xgen_files.append(self.get_env_path_normpath(i))
                    except:
                        pass
        return xgen_files

    def get_xgen_Archive_files(self, Archive_attr, description):
        Archive_name_re = re.compile(r"(?<=name\=\")[\w _\-.:()\\/$/+{}']+(?=\")", re.I)
        Archive_file_re = re.compile(r'(?<=")(?:[a-z][:][\\/]|[\\\\]|[\${?])(?:[\w _\-.:()\\/$/+{}\'])+(?=\")', re.I)
        Archive_files = []
    
        if "#ArchiveGroup" in Archive_attr:
            line = Archive_attr.strip().strip("files").strip()
            for li in line.split("#ArchiveGroup "):
                if li:
                    if Archive_name_re.findall(li):
                        Archive_name = Archive_name_re.findall(li)[0]
                        # print Archive_name
                    if Archive_file_re.findall(li):
                        for file in Archive_file_re.findall(li):
                            # file_r = os.path.normpath(xg.expandFilepath(file, description))
                            file_r = self.get_env_path_normpath(file)
                        
                            if "\\mi\\" in file_r:
                                Archive_files += self.get_files_from_folder(os.path.split(file_r)[0],
                                                                            Archive_name + "*", "mi.gz")
                        
                            if "\\rib\\" in file_r or "ribarchives" in file_r:
                                Archive_files += self.get_files_from_folder(os.path.split(file_r)[0],
                                                                            Archive_name + "*", "zip")
                            
                                Archive_files += self.get_files_from_folder(os.path.join(os.path.split(file_r)[0],
                                                                                         Archive_name + "*"), "*")
                        
                            if "\\ass\\" in file_r:
                                Archive_files += self.get_files_from_folder(os.path.split(file_r)[0],
                                                                            Archive_name + "*", "gz")
                                Archive_files += self.get_files_from_folder(os.path.split(file_r)[0],
                                                                            Archive_name + "*", "asstoc")
                                Archive_files += self.get_files_from_folder(os.path.split(file_r)[0],
                                                                            Archive_name + "*", "ass")
                        
                            if "\\materials\\" in file_r:
                                Archive_files += self.get_files_from_folder(os.path.split(file_r)[0],
                                                                            Archive_name + "*", "ma")
                        
                            if "\\abc\\" in file_r:
                                Archive_files += self.get_files_from_folder(os.path.split(file_r)[0],
                                                                            Archive_name + "*", "abc")
                        
                            Archive_files += self.get_files_from_folder(os.path.split(os.path.split(file_r)[0])[0],
                                                                        Archive_name + "*", "xarc")
                            Archive_files += self.get_files_from_folder(os.path.split(os.path.split(file_r)[0])[0],
                                                                        Archive_name + "*", "log")
    
        return list(set(Archive_files))

    def get_xgen_ptex_lookup(self, node_name=None):
        textures = {}
        textures.update(self.get_node_asstes("xgen_ptex_lookup", assts_attr=["fileName"]))
        return textures

    def get_node_from_ass(self, ass_file, amin_attr=0):
        self.print_info("the ass file is %s" % ass_file)
        DATE_PATTERN = re.compile("^### exported: +(.+)")
        ARNOLD_PATTERN = re.compile("^### from: +(.+)")
        APP_PATTERN = re.compile("^### host app: +(.+)")
        TYPE_PATTERN = re.compile("^[a-zA-Z].+")
        node_list = []
        current_node = {}
    
        if ass_file.endswith(".gz"):
            fp = gzip.open(ass_file)
        else:
            fp = open(ass_file, "r")
        for line in fp:
            line = line.strip(' \t\r\n')
            if line:
            
                if line.startswith("#"):
                    pass
                elif TYPE_PATTERN.findall(line):
                
                    if current_node:
                        group = line.split()
                    
                        if len(group) == 1:
                            pass
                        elif len(group) > 1 and group[1].startswith("\""):
                            current_node[group[0]] = [" ".join(group[1:]).strip("\"")]
                        else:
                            current_node[group[0]] = " ".join(group[1:])
                    else:
                        line = [i for i in line.split() if i not in ["{", "}"]]
                        if len(line) == 1:
                            current_node["node_type"] = line[0]
                        
                            if cmp(line[0], "polymesh") == 0:
                                # print line
                                line = fp.next()
                                line = fp.next()
                                line = line.strip(' \t\r\n')
                            
                                current_node[line.split()[0]] = line.split()[1]
                                while line and cmp(line, "}"):
                                    line = fp.next()
                                    line = line.strip(' \t\r\n')
                        else:
                        
                            for index, i in enumerate(line):
                            
                                if index % 2:
                                
                                    if index < len(line):
                                        current_node["node_type"] = line[0]
                                        current_node[line[index - 1]] = [line[index].strip('"')]
                            node_list.append(current_node)
            
                if "}" in line:
                    node_list.append(current_node)
                
                    current_node = {}
    
        fp.close()
        return node_list

    def filter_assdicts(self, ass_file, amin_attr=0):
        node_list = self.get_node_from_ass(ass_file)
        ass_name = os.path.split(ass_file)[1]
        textures = {}
    
        node_types = {"MayaFile": ["filename"], "procedural": ["G_assetsPath", "G_middlePath"]}
        ass_types = {"procedural": ["dso", "filename"], "include": ["include"]}
        for nodes in node_list:
            node_name = nodes.get("name", None)
            if node_name:
                node_name = node_name.replace("/", "_")
            node_type = nodes.get("node_type", None)
        
            if node_type in node_types:
                for attr in node_types[node_type]:
                    if nodes.get(attr, None):
                        dict_key = "%s_%s_%s_%s" % (ass_name, node_type, node_name, attr)
                        textures.update(self.get_dict_from_path(nodes.get(attr, None)[0], dict_key, amin_attr_val=0))
        
            if node_type in ass_types:
                for attr in ass_types[node_type]:
                    self.print_info(ass_types[node_type])
                    if nodes.get(attr, None):
                        self.print_info(nodes.get(attr, None))
                        dict_key = "%s_%s_%s_%s" % (ass_name, node_type, node_name, attr)
                        ass_dicts = {}
                        ass_dicts.update(self.get_dict_from_path(nodes.get(attr, None)[0], dict_key, amin_attr_val=0))
                        textures.update(self.get_dict_from_path(nodes.get(attr, None)[0], dict_key, amin_attr_val=0))
                    
                        if ass_dicts:
                            for ass_key in ass_dicts:
                                sequences, others = FileSequence.find(list(ass_dicts[ass_key]["local_path"]), "rs")
                                for ass_i_s in sequences:
                                    ass_an = os.path.normpath(ass_i_s.startFileName)
                                    if ass_an not in self.ASS_FILES and ass_an not in self.ASS_FILES_AN:
                                        self.ASS_FILES.append(ass_an)
                                for ass_an in others:
                                    if ass_an not in self.ASS_FILES and ass_an not in self.ASS_FILES_AN:
                                        self.ASS_FILES.append(ass_an)
        
            if nodes.get("filename", None):
                dict_key = "%s_%s_%s" % (node_type, node_name, "filename")
                textures.update(self.get_dict_from_path(nodes.get("filename", None)[0], dict_key, amin_attr_val=0))
    
        return textures

    def get_file_from_ass(self, ass_file, amin_attr=0):
        textures = {}
        if os.path.exists(ass_file) and ass_file not in self.ASS_FILES and ass_file not in self.ASS_FILES_AN:
            self.ASS_FILES.append(ass_file)
        for ass_i in self.ASS_FILES:
            textures.update(self.filter_assdicts(ass_i))
    
        return textures

    def get_RedshiftProxyMesh(self, node_name=None):
    
        textures = {}
        nodes = []
        if node_name:
            nodes.append(pm.PyNode(node_name))
        else:
            nodes = pm.ls(type="RedshiftProxyMesh")
        for node_i in nodes:
            rs_files = {}
            rs_files.update(self.get_node_asstes(node_i, assts_attr=["fileName"], seq_attr=["useFrameExtension"]))
            textures.update(rs_files)
            if rs_files:
                for rs_key in rs_files:
                    sequences, others = FileSequence.find(list(rs_files[rs_key]["local_path"]), "rs")
                    for rs_i_s in sequences:
                        rs_an = os.path.normpath(rs_i_s.startFileName)
                        if rs_an not in self.RS_FILES and rs_an not in self.RS_FILES_AN:
                            self.RS_FILES.append(rs_an)
                    for rs_an in others:
                        if rs_an not in self.RS_FILES and rs_an not in self.RS_FILES_AN:
                            self.RS_FILES.append(rs_an)
    
        for rs_file in self.RS_FILES:
            get_file_rs = self.get_file_from_rs(rs_file, 1)
            textures[rs_file] = {}
            textures[rs_file]["local_path"] = []
            textures[rs_file]["local_path"] += get_file_rs
            sequences, others = FileSequence.find(list(get_file_rs), "rs")
            for rs_i_s in sequences:
                rs_an = os.path.normpath(rs_i_s.startFileName)
                if os.path.exists(rs_an) and rs_an not in self.RS_FILES and rs_an not in self.RS_FILES_AN:
                    self.RS_FILES.append(rs_an)
            for rs_an in others:
                rs_an = os.path.normpath(rs_an)
                if os.path.exists(rs_an) and rs_an not in self.RS_FILES and rs_an not in self.RS_FILES_AN:
                    self.RS_FILES.append(rs_an)
    
        return textures

    def get_file_from_rs(self, rs_file, amin_attr=0):
        texture = []
        for line in open(rs_file, "rb"):
            p = re.compile(r'(?:[a-z][:][\\/]|[\\\\]|(?:\.\./)|(?:\.\.\\)){1}[\w _\-.:()\\/$+]+\.[\w]+', re.I)
        
            r = p.findall(line)
            rs_image = (
                ".rstxbin", ".tga", ".dds", ".jpg", ".png", ".rsmap", ".iff", ".rs", ".exr", ".tiff", ".jpeg", ".hdr",
                ".bmp", ".als", ".cin", ".pic", ".rat", ".psd", ".psb", ".ies", ".gif", ".qtl", ".rla", ".rlb", ".pix",
                ".sgi",
                ".rgb", ".rgba", ".si", ".rs", ".tif", ".tif23",
                ".tif16", ".tx", ".vst", ".yuv", ".ptex", ".tex", ".dpx")
            if r:
                for i in r:
                    if i.lower().endswith(rs_image):
                        if i.startswith(("../", "/../", "\\..\\", "..\\")):
                            i = os.path.abspath(os.path.dirname(os.path.abspath(rs_file)) + "\\" + i)
                        i = os.path.normpath(i)
                        texture += self.file_images(i, amin_attr)
        return list(set(texture))

    def get_node_from_vrscene(self, vrscene_file, amin_attr=0):
        self.print_info("the vrscene file is %s" % vrscene_file)
        TYPE_PATTERN = re.compile("^[a-zA-Z].+")
        vrscene_PATTERN = re.compile(r'(?:[a-z][:][\\/]|[\\\\]|[/]|(?:\.\./)|(?:\.\.\\))[\w _\-.:()\\/$+]+\.vrscene',
                                     re.I)
        current_node = {}
        node_list = []
        with open(vrscene_file, 'r') as f:
            while True:
                line = f.readline()
                if line:
                    line = line.strip()
                    if line.startswith("//"):
                        pass
                    elif line.startswith("#include"):
                        vr_file = vrscene_PATTERN.findall(line)
                        if vr_file:
                            current_node['nodeType'] = "include"
                            current_node['nodeName'] = os.path.basename(vr_file[0])
                            current_node['include'] = vr_file[0]
                            node_list.append(current_node)
                            current_node = {}
                            # if vr_file:
                            #     if vr_file[0] not in self.VRSCENE_FILES and vr_file[0] not in self.VRSCENE_FILES_AN and os.path.exists(vr_file[0]):
                            #         self.VRSCENE_FILES.append(vr_file[0])
                            # else:
                            #     pass
                
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
                        node_list.append(current_node)
                    
                        current_node = {}
                    else:
                        pass
                else:
                    break
    
        return node_list

    def filter_vrscenedicts(self, vrscene_file, amin_attr=0):
        node_list = self.get_node_from_vrscene(vrscene_file)
    
        vrscene_name = os.path.split(vrscene_file)[1]
        textures = {}
    
        node_types = {"BitmapBuffer": ["file"], "TexOSL": ["shader_file"]}
        vrscene_types = {"include": ["include"], "VRayScene": ["filepath"]}
        for nodes in node_list:
            # print nodes
            node_name = nodes.get("nodeName", None)
            if node_name:
                node_name = node_name.replace("/", "_")
            node_type = nodes.get("nodeType", None)
            # print node_name
            # print node_type
            if node_type in node_types:
                for attr in node_types[node_type]:
                    if nodes.get(attr, None):
                        dict_key = "%s_%s_%s_%s" % (vrscene_name, node_type, node_name, attr)
                        textures.update(self.get_dict_from_path(nodes.get(attr, None), dict_key, amin_attr_val=0))
        
            if node_type in vrscene_types:
                for attr in vrscene_types[node_type]:
                
                    if nodes.get(attr, None):
                        self.print_info(nodes.get(attr, None))
                        dict_key = "%s_%s_%s_%s" % (vrscene_name, node_type, node_name, attr)
                        self.print_info(dict_key)
                        vrscene_dicts = {}
                        vrscene_dicts.update(
                            self.get_dict_from_path(os.path.normpath(nodes.get(attr, None)), dict_key, amin_attr_val=0))
                    
                        textures.update(
                            self.get_dict_from_path(os.path.normpath(nodes.get(attr, None)), dict_key, amin_attr_val=0))
                    
                        if vrscene_dicts:
                            for vrscene_key in vrscene_dicts:
                                sequences, others = FileSequence.find(list(vrscene_dicts[vrscene_key]["local_path"]),
                                                                      "vrscene")
                                for vrscene_i_s in sequences:
                                    vrscene_an = os.path.normpath(vrscene_i_s.startFileName)
                                    if vrscene_an not in self.VRSCENE_FILES and vrscene_an not in self.VRSCENE_FILES_AN:
                                        self.VRSCENE_FILES.append(vrscene_an)
                                for vrscene_an in others:
                                    if vrscene_an not in self.VRSCENE_FILES and vrscene_an not in self.VRSCENE_FILES_AN:
                                        self.VRSCENE_FILES.append(vrscene_an)
        
            if nodes.get("filename", None):
                dict_key = "%s_%s_%s" % (node_type, node_name, "filename")
                textures.update(self.get_dict_from_path(nodes.get("filename", None)[0], dict_key, amin_attr_val=0))
    
        return textures

    def get_file_from_vrscene(self, vrscene_file, amin_attr=0):
        textures = {}
        if os.path.exists(
                vrscene_file) and vrscene_file not in self.VRSCENE_FILES and vrscene_file not in self.VRSCENE_FILES_AN:
            self.VRSCENE_FILES.append(vrscene_file)
        for vrscene_i in self.VRSCENE_FILES:
            textures.update(self.filter_vrscenedicts(vrscene_i))
    
        return textures

    def get_node_from_rib(self, rib_file, amin_attr=0):
        pass

    def filter_ribdicts(self, rib_file, amin_attr=0):
        pass

    def get_file_from_rib(self, rib_file, amin_attr=0):
        pass

    def get_yeti(self, node_name=None):
        textures = {}
        nodes = []
        if node_name:
            nodes.append(pm.PyNode(node_name))
        else:
            nodes = pm.ls(type="pgYetiMaya")
        for node_i in nodes:
            textures.update(self.get_node_asstes(node_i, assts_attr=["groomFileName"]))
            textures.update(self.get_node_asstes(node_i, assts_attr=["imageSearchPath"]))
            textures.update(self.get_node_asstes(node_i, assts_attr=["cacheFileName"]))
            try:
                # mel_cmd = 'pgYetiGraph -listNodes -type "texture" %s' % str(node_i)
                # texture_in_yeti = [i for i in mel.eval(mel_cmd)]
                texture_in_yeti = [i for i in pm.mel.pgYetiGraph("-listNodes", "-type", "texture", node_i)]
                for texture in texture_in_yeti:
                    self.print_info(texture)
                    image = pm.mel.pgYetiGraph("-node", texture, "-param", "file_name", "-getParamValue", node_i)
                    if image:
                        # print image
                        dict_key = "%s_%s_file_name" % (node_i, texture)
                        # print dict_key
                        # print self.get_dict_from_path("C:/Yeti-v2.2.1_Maya2017-windows64/examples/test_texture.tif", dict_key)
                        textures.update(self.get_dict_from_path(image, dict_key))
            except:
                pass
        
            try:
                # mel_cmd = 'pgYetiGraph -listNodes -type "reference" %s' % str(node_i)
                # reference_in_yeti =  [i for i in mel.eval(mel_cmd)]
                reference_in_yeti = [i for i in pm.mel.pgYetiGraph("-listNodes", "-type", "reference", node_i)]
                for reference in reference_in_yeti:
                    # print reference
                    image = pm.mel.pgYetiGraph("-node", reference, "-param", "reference_file", "-getParamValue", node_i)
                    if image:
                        dict_key = "%s_%s_reference_file" % (node_i, reference)
                        textures.update(self.get_dict_from_path(image, dict_key))
            except:
                pass
    
        return textures

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
                        asset.append({"node":j,"path":[self.str_to_unicode(k) for k in self.asset_dict[i][j]["local_path"]]})
                    if len(self.asset_dict[i][j]["missing"]) > 0:
                        missing_file.append({"node":j,"path":[self.str_to_unicode(l) for l in self.asset_dict[i][j]["missing"]]})
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
        self.print_info("start open maya file: " + self["cg_file"])
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
                cmds.file(self["cg_file"], o=1, force=1, ignoreVersion=1, prompt=0)
                # pm.openFile(self["cg_file"], force=1, ignoreVersion=1, prompt=0)
                self.print_info("open maya file ok.")
            except:
                pass
        else:
            raise Exception("Dont Found the maya files error.")


    def check_scene_name(self):
        scene_name = os.path.splitext(os.path.basename(self["cg_file"]))[0]
        if scene_name.startswith(" "):
            self.writing_error(25017,"scene name begins with a space")
        if scene_name.endswith(" "):
            self.writing_error(25017, "scene name ends with a space")
        if self.check_contain_chinese(scene_name):
            self.writing_error(25017, "scene name contains chinese")

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
                if result == 2016 and "version" in i:
                    if "2016 Extension" in i:
                        result = 2016.5
            file_info_2013 = [i for i in infos if i.startswith("requires")]
            if result == 2013:
                for j in file_info_2013:
                    if "maya \"2013\";" in j:
                        result = 2013
                    else:
                        result = 2013.5
        elif maya_file.endswith(".mb"):
            with open(maya_file, "r") as f:
                info = f.readline()
            file_infos = re.findall(r'FINF\x00+\x11?\x12?K?\r?(.+?)\x00(.+?)\x00',info, re.I)
            for i in file_infos:
                if i[0] == "product":
                    result = int(i[1].split()[1])
            
                if result == 2016 and "version" in i[0]:
                    if "2016 Extension" in i[1]:
                        result = 2016.5
            file_info_2013 = re.findall(r'2013ff10',info, re.I)
            if result == 2013:
                print file_info_2013
                for j in file_info_2013:
                    if j[0]:
                        result = 2013.5
                    else:
                        result = 2013
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

    def gather_upload_dict(self):
        upload_json_dict = {}
        upload_asset = []
        upload_scene = []
    
        # Add the cg file to upload.json
        upload_scene.append({"local": self["cg_file"], "server": self.convert_path("", self["cg_file"])})
        # Add the assets to upload.json
        assets = self.asset_info_dict["asset"]
        for asset_dict in assets:
            path_list = asset_dict["path"]
            for path in path_list:
                d = {}
                local = path
                server = self.convert_path("", local)
                d["local"] = local.replace("\\", "/")
                d["server"] = server
                if d not in upload_asset:
                    upload_asset.append(d)
        # Add the cg file to upload.json
        upload_asset.append({
            "local": self["cg_file"],
            "server": self.convert_path("",self["cg_file"])
        })

    
        upload_json_dict["scene"] = upload_scene
        upload_json_dict["asset"] = upload_asset
        self.upload_info_dict = upload_json_dict
    
        return self.upload_info_dict



    def write_task_info(self):
        info_file_path = os.path.dirname(self["task_json"])
        print "write info to task.json"
        if not os.path.exists(info_file_path):
            os.makedirs(info_file_path)
        try:
            info_file = self["task_json"]
            
            if os.path.exists(self["task_json"]):
                with open(info_file, 'r') as f:
                    json_src = json.load(f)
            else:
                json_src = {}
            json_src["scene_info"] = self.scene_info_dict
            with codecs.open(info_file, 'w', 'utf-8') as f:
                json.dump(json_src, f, ensure_ascii=False, indent=4)
            # task_json_str = json.dumps(json_src, ensure_ascii=False, indent=4)
            # task_json_str = task_json_str.encode("utf-8")
            # self.write_file(task_json_str,info_file)
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
            with codecs.open(info_file, 'w', 'utf-8') as f:
                json.dump(self.asset_info_dict, f, ensure_ascii=False, indent=4)
        except Exception as err:
            print  err
            pass
        
    def write_upload_info(self):
        info_file_path = os.path.dirname(self["upload_json"])
        print "write info to upload.json"
        if not os.path.exists(info_file_path):
            os.makedirs(info_file_path)
        try:
            info_file = self["upload_json"]
            with codecs.open(info_file, 'w', 'utf-8') as f:
                json.dump(self.upload_info_dict, f, ensure_ascii=False, indent=4)
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
            with codecs.open(info_file, 'w', 'utf-8') as f:
                json.dump(self.tips_info_dict, f, ensure_ascii=False, indent=4)
        except Exception as err:
            print  err
            pass

def analyze_maya(options):
    submit_type = "client"
    if submit_type == "client":
        argument_json_path = options["argument_json_path"]
        client_script = options["client_script"]
        client_script = os.path.abspath(client_script)
        sys.path.append(client_script)
        from submitutil import *
        
        print("88888888888888")
        print(argument_json_path)
        print(type(argument_json_path))
        analyze_options = {}
        argument_json_dict = RBFileUtil.parser_argument_json(argument_json_path)
        client_project_dir = argument_json_dict['client_setting']['client_project_dir']
        client_project_dir = client_project_dir.replace("\\", "/") + "/" + argument_json_dict['job_id']

        analyze_options["cg_project"] = argument_json_dict["user_setting"]["project_dir"]
        analyze_options["cg_file"] = argument_json_dict["cg_file"]
        analyze_options["task_json"] = client_project_dir + "/" + "task.json"
        analyze_options["asset_json"] = client_project_dir + "/" + "asset.json"
        analyze_options["tips_json"] = client_project_dir + "/" + "tips.json"
        analyze_options["upload_json"] = client_project_dir + "/" + "upload.json"
        analyze_options["cg_version"] = argument_json_dict['plugin_setting']['software_config']['cg_version']
        analyze_options["cg_plugins"] = argument_json_dict["plugin_setting"]["software_config"]['plugins']
        analyze_options["platform"] = argument_json_dict["platform"]

        analyze = Config(analyze_options)

        analyze.check_scene_name()
        analyze.start_open_maya()

        analyze.gather_task_dict()
        analyze.print_info("get layer setting info ok.")

        analyze.gather_asset_dict()
        analyze.print_info("gather assets  info ok.")
        
        analyze.gather_upload_dict()
        analyze.print_info("gather upload  info ok.")

        analyze.print_info("gather tips  info ok.")

        analyze.write_task_info()
        analyze.print_info("write task info ok.")

        analyze.write_asset_info()
        analyze.print_info("write asset info ok.")
        
        analyze.write_upload_info()
        analyze.print_info("write upload info ok.")

        analyze.write_tips_info()
        analyze.print_info("write tips info ok.")

        analyze.print_info("analyze maya info ok.")
        
        
        
    else:
        print "88888888888888"
        info_dict = json.dumps(options, ensure_ascii=False, indent=4)
        print info_dict
        print type(options)
        analyze = Config(options)
        
        analyze.check_maya_version(options["cg_file"],options["cg_version"])
        analyze.check_scene_name()
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
    #linux
    options = {}
    options["cg_file"] = cg_file
    options["cg_project"] = cg_project
    options["task_json"] = task_json
    if os.path.exists(options["task_json"]):
        options["asset_json"] = os.path.join(os.path.dirname(options["task_json"]),"asset.json").replace("\\","/")
        options["tips_json"] = os.path.join(os.path.dirname(options["task_json"]),"tips.json").replace("\\","/")
        options["system_json"] = os.path.join(os.path.dirname(options["task_json"]),"system.json").replace("\\","/")
        with codecs.open(options["task_json"],'r', 'utf-8') as f_task_json:
            task_json_dict = json.load(f_task_json)
        options["cg_version"] = task_json_dict['software_config']['cg_version']
        options["cg_plugins"] = task_json_dict['software_config']['plugins']
        with codecs.open(options["system_json"], 'r', 'utf-8') as f_system_json:
            system_json_dict = json.load(f_system_json)
        options["platform"] = system_json_dict['system_info']['common']['platform']
        analyze_maya(options)
    else:
        print("task.json is not exists")
        sys.exit(555)