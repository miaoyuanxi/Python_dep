#!/usr/bin/env python
#encoding:utf-8
# -*- coding: utf-8 -*-

# 2017/9/21-16:27-2017
#"C:\Program Files\Autodesk\Maya2014\bin\mayapy.exe" E:\PycharmProjects\work\test_del\an_maya.py --ui "123" --ti "456" --proj "E:\fang\fagng" --cgfile "E:\fang\fagng\scenes\pre_test_2014.mb" --taskjson "d:\task.json"
#"C:/Program Files/Autodesk/maya2014/bin/mayabatch.exe" -command "python \"options={'cg_file': 'E:/fang/fagng/scenes/pre_test_2014.mb', 'user_id': 123, 'cg_project': 'E:/fang/fagng', 'task_id': 456, 'task_json': 'd:/task.json'};import sys;sys.path.insert(0, 'E:/PycharmProjects/work/test_del');from an_maya import *;analyze = maya_an(options);analyze.run();analyze.write_info_file();\""


import os
import sys
import re
import subprocess
import json
import argparse
import collections




# if "maya" in sys.executable.lower():
    # if "mayapy" in sys.executable.lower() or \
            # "python-bin" in sys.executable.lower():
        # import maya.standalone as standalone
        # standalone.initialize()
    # import maya.cmds as cmds
    # import maya.mel as mel
    # import pymel.core as pm

import maya.standalone
try:
    maya.standalone.initialize(name='python')
except:
    sys.stderr.write( "Failed in initialize standalone application" )
    raise

import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel

class Analyze(dict):
    def __init__(self, options):
        for i in options:
            self[i] = options[i]            
        self.scene_info_dict={}
        
    
    def write_info_file(self):
        info_file_path = os.path.dirname(self["task_json"])
        print "write info to task.json"
        if not os.path.exists(info_file_path):
            os.makedirs(info_file_path)
        try:
            info_file = self["task_json"]
            with open(info_file, 'r') as f:
                print "read info file"
                json_src = json.load(f)
            print type(json_src)
            json_src["scene_info"] = self.scene_info_dict
            # json_src.setdefault("scene_info",[]).append(self.scene_info_dict)
            print json_src
            with open(info_file, 'w') as f:
                print "write info file"
                f.write(json.dumps(json_src))
                # f.close()
        except Exception as err:
            print  err
            pass

    def run(self):
        self.analyze_list = ["Start", "End", 'userRenderer', 'imageFilePrefix', "Ext", "dynMemLimit", \
                             'camera', 'render_camera', "render_layer", 'renderable_layer', 'width', \
                             'height', 'preMel', 'postMel', 'preRenderLayerMel', 'postRenderLayerMel', 'preRenderMel','postRenderMel']

        self.assets_node_dict = {'file': 'fileTextureName', 'aiImage': 'filename', 'alTriplanar': 'texture',\
                                 'AlembicNode': 'abc_File', 'pgYetiMaya': 'cacheFileName', 'aiStandIn': 'dso', \
                                'RMSGeoLightBlocker': 'Map', 'VRayMesh': 'fileName', 'VRayLightIESShape': 'iesFile', \
                                'diskCache': 'cacheName', 'RealflowMesh': 'Path', 'mip_binaryproxy': 'object_filename', \
                                'mentalrayLightProfile': 'fileName', 'aiPhotometricLight': 'ai_filename',\
                                'cacheFile': 'cachePath', 'VRayVolumeGrid': 'inFile'}

        self.assets_node_list = [{"file": "fileTextureName"},{"VRayMesh": "fileName"},{"AlembicNode": "abc_File"},\
                                 {"pgYetiMaya": "groomFileName"},{"pgYetiMaya": "cacheFileName"},{"aiImage": "filename"},\
                                 {"RMSGeoLightBlocker": "Map"},{"PxrStdEnvMapLight": "Map"},{"VRaySettingsNode": "imap_fileName2"}, \
                                 {"VRaySettingsNode": "pmap_file2"}, {"VRaySettingsNode": "lc_fileName"},\
                                 {"VRaySettingsNode": "shr_file_name"}, {"VRaySettingsNode": "causticsFile2"}, \
                                 {"VRaySettingsNode": "imap_fileName"},{"VRaySettingsNode": "pmap_file"}, {"VRaySettingsNode": "fileName"}, \
                                 {"VRayLightIESShape": "iesFile"},{"diskCache": "cacheName"}, {"miDefaultOptions": "finalGatherFilename"}, \
                                 {"RealflowMesh": "Path"}, {"aiStandIn": "dso"}, {"mip_binaryproxy": "object_filename"},\
                                 {"mentalrayLightProfile": "fileName"}, {"aiPhotometricLight": "ai_filename"}, \
                                 {"VRayVolumeGrid": "inFile"}, {"file": "fileTextureName"}, {"RedshiftDomeLight": "tex0"},\
                                 {"RedshiftSprite": "tex0"}, {"ExocortexAlembicXform": "fileName"}, {"ffxDyna": "output_path"}, \
                                 {"ffxDyna": "wavelet_output_path"}, {"ffxDyna": "postprocess_output_path"},\
                                 {"RedshiftIESLight": "profile"}, {"RedshiftDomeLight": "tex1"}, \
                                 {"RedshiftEnvironment": "tex0"}, {"RedshiftEnvironment": "tex1"}, {"RedshiftEnvironment": "tex2"},\
                                 {"RedshiftEnvironment": "tex3"}, {"RedshiftEnvironment": "tex4"},\
                                 {"RedshiftLensDistortion": "LDimage"},{"RedshiftLightGobo": "tex0"}, {"RedshiftNormalMap": "tex0"},\
                                 {"RedshiftOptions": "irradianceCacheFilename"}, {"RedshiftOptions": "photonFilename"},\
                                 {"RedshiftOptions": "irradiancePointCloudFilename"},{"RedshiftOptions": "subsurfaceScatteringFilename"}, \
                                 {"RedshiftProxyMesh": "fileName"}, {"RedshiftVolumeShape": "fileName"},\
                                 {"RedshiftBokeh": "dofBokehImage"}, {"RedshiftCameraMap": "tex0"},{"RedshiftDisplacement": "texMap"},\
                                 {"alTriplanar": "texture"},{"cacheFile": "cachePath"},{"gpuCache": "cacheFileNam"}]
        
        print "[Rayvision]: open maya file " + self["cg_file"]
        self.set_env()
        # self.set_project()
        try:
            cmds.file(self["cg_file"], o=1, force=1, ignoreVersion=1, prompt=0)
        except:
            pass
        print "[Rayvision]: open maya ok."        
        pm.lockNode( 'defaultRenderGlobals', lock=False )
        # self.set_env()
        self.get_rendersetting()

    #------------get rendersetting   return  a  dict -------------

    def set_project(self):
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
                        # raise Exception("Can't create empty workspace.mel file "
                        #                 "in project folder")

                if os.path.exists(workspacemel):
                    pm.mel.eval('setProject "%s"' % (self["cg_project"]))   

    def set_env(self):
        try:
            import maya.standalone
            maya.standalone.initialize(name="python")
        except:
            sys.stderr.write("Failed in initialize standalone application")
            raise
        for value in ["MAYA_PLUG_IN_PATH", "PYTHONPATH", "MAYA_MODULE_PATH"]:
            os.environ[value] = mel.eval('getenv "%s"' % value)
            print os.environ[value]

        for i in os.environ["PYTHONPATH"].split(";"):
            i = i.replace('/', '\\')
            if os.path.exists(i) and i not in sys.path:
                sys.path.append(i)

        for plugin in ["AbcExport.mll", "AbcImport.mll", "mtoa.mll"]:
            try:
                print(plugin)
                cmds.loadPlugin(plugin)
            except:
                print('----------%s not load' % plugin)    
    
        # try:
            # pm.loadPlugin("mtoa")
            # pm.pluginInfo("mtoa", e=1, a=1)
        # except:
            # print "mtoa has been loaded!!!"   
    
    
    def is_renderable_layer(self,render_layer):  
        for layer in pm.PyNode("renderLayerManager.renderLayerId").outputs():
            if layer == render_layer:
                if layer.type() == "renderLayer":
                    if layer.renderable.get():
                        return '1'
                    else:
                        return '0'

    # def get_layer_settings(self, render_layer=None):
        # render_settings = pm.PyNode("defaultRenderGlobals")

        # if render_layer:
            # try:
                # pm.PyNode(render_layer).setCurrent()
                # self["renderSettings"]["renderableLayer"] = render_layer
                # self["renderSettings"]["allLayer"] = ",".join([i.name()
                    # for i in pm.PyNode("renderLayerManager").outputs()
                    # if i.type() == "renderLayer"])
                # self["renderSettings"]["renderableCamera"] = [i.name()
                     # for i in pm.ls(type="camera") if i.renderable.get()]
                # server_config["renderlayer"] = render_layer
                # start = int(render_settings.startFrame.get())
                # end = int(render_settings.endFrame.get())
                # frange = str(start) + "-" + str(end)
                # step = render_settings.byFrameStep.get()
                # self["renderSettings"]["frames"] = frange + "[" + str(int(step)) + "]"
                # self["common"]["name"] = os.path.basename(self["common"]["cgFile"])
                # self["common"]["name"] += " " + render_layer
                # self["delete"] = []
            # except:
                # print traceback.format_exc()
                # raise Exception("Can't switch renderlayer " + render_layer)
        # else:
            # all_layers = [i for i in pm.PyNode("renderLayerManager").outputs()
                          # if i.type() == "renderLayer"]
            # render_layers = [i for i in all_layers if i.renderable.get()]
            # if not render_layers:
                # raise Exception("Can't find render layer in render settings.")

            # self["renderSettings"]["renderableLayer"] = ",".join([i.name()
                # for i in render_layers])
            # self["renderSettings"]["allLayer"] = ",".join([i.name()
                # for i in all_layers])
# #            layer = pm.PyNode(all_layers[0])
# #            if layer.currentLayer() not in all_layers:
# #                layer.setCurrent()

            # start, end = None, None
            # try:
                # # add switch renderlayers check.
                # for layer in all_layers:
                    # if layer != layer.currentLayer():
                        # layer.setCurrent()

                    # temp_start = int(render_settings.startFrame.get())
                    # temp_end = int(render_settings.endFrame.get())

                    # if start:
                        # if start > temp_start:
                            # start = temp_start
                    # else:
                        # start = temp_start

                    # if end:
                        # if end < temp_end:
                            # end = temp_end
                    # else:
                        # end = temp_end

                    # self["renderSettings"]["renderableCamera"] += [i.name()
                         # for i in pm.ls(type="camera") if i.renderable.get()]

                # frange = str(start) + "-" + str(end)
                # step = render_settings.byFrameStep.get()
                # self["renderSettings"]["frames"] = frange + "[" + str(int(step)) + "]"

            # except:
                # print traceback.format_exc()
                # writing_error(218)
                # raise Exception("Can't switch renderlayers.")

            # print_info2("switch renderlayer check ok")

        # self["common"]["renderer"] = render_settings.currentRenderer.get()
        # self["renderSettings"]["usedRenderer"] = render_settings.currentRenderer.get()

        # resolution_settings = pm.PyNode("defaultResolution")
        # self["renderSettings"]["width"] = resolution_settings.width.get()
        # self["renderSettings"]["height"] = resolution_settings.height.get()

        # if render_layer:
            # start = render_settings.startFrame.get()
            # end = render_settings.endFrame.get()
            # frange = str(int(start)) + "-" + str(int(end))
            # step = render_settings.byFrameStep.get()
            # self["renderSettings"]["frames"] = frange + "[" + str(int(step)) + "]"
    def show_hide_node(self):
        mel.eval("outlinerEditor -edit -showDagOnly false outlinerPanel1;showMinorNodes true;")



            
    def get_defaultrenderglobals(self,layer):
        scene_info_common_dict = collections.OrderedDict()
        default_globals = pm.PyNode("defaultRenderGlobals")
        scene_info_common_dict['renderer'] = str(self.GetCurrentRenderer())
        scene_info_common_dict['image_file_prefix'] = str(self.GetMayaOutputPrefix(layer))
        scene_info_common_dict['start'] = str(int(cmds.getAttr("defaultRenderGlobals.startFrame")))
        scene_info_common_dict['end'] = str(int(cmds.getAttr("defaultRenderGlobals.endFrame")))
        scene_info_common_dict['by_frame'] = str(int(cmds.getAttr("defaultRenderGlobals.byFrame")))
        scene_info_common_dict['all_camera'] = cmds.ls(type="camera")
        scene_info_common_dict['render_camera'] = [i.name() for i in pm.ls(type="camera") if i.renderable.get()]
        scene_info_common_dict["renumber_frames"] = str(default_globals.modifyExtension.get())
        scene_info_common_dict['width'] = str(int(cmds.getAttr("defaultResolution.width")))
        scene_info_common_dict['height'] = str(int(cmds.getAttr("defaultResolution.height")))      
        scene_info_common_dict["image_format"] = str(self.GetOutputExt())
        scene_info_common_dict["animation"] = str(default_globals.animation.get())
        scene_info_common_dict["file_name"] = str(pm.renderSettings(fin=1, cam='', lyr=layer))
        # self["renderSettings"]['all_layer'] = ",".join([i.name() for i in pm.PyNode("renderLayerManager.renderLayerId").outputs() if i.type() == "renderLayer"])
        # self["renderSettings"]['render_layer'] = ",".join([i.name() for i in pm.PyNode("renderLayerManager.renderLayerId").outputs() if i.type() == "renderLayer" if i.renderable.get()])
        self.getMel()
        return scene_info_common_dict


    def get_arnoldsetting(self): 
        try:
            arnold_options_node = pm.PyNode('defaultArnoldRenderOptions')
        except :
            arnold_options_node = pm.createNode('aiOptions', name='defaultArnoldRenderOptions', skipSelect=True, shared=True)
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
            arnold_display_driver_node = pm.createNode('aiAOVDriver', name='defaultArnoldDisplayDriver', skipSelect=True, shared=True)            
        try:
            resolution_node = pm.PyNode('defaultResolution')
        except :
            resolution_node = pm.createNode('resolution', name = 'defaultResolution', skipSelect=True, shared=True)
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
        scene_info_option_dict["sampling"] = [AASamples,GIDiffuseSamples,GISpecularSamples,GITransmissionSamples,GISssSamples, GIVolumeSamples]
        if arnold_options_node.hasAttr("autotx"):
            scene_info_option_dict["auto_tx"] = str(arnold_options_node.autotx.get())
            if scene_info_option_dict["auto_tx"] == '0':
                scene_info_option_dict["use_existing_tiled_textures"] = str(arnold_options_node.use_existing_tiled_textures.get())
        if arnold_options_node.hasAttr("textureMaxMemoryMB"):
            scene_info_option_dict["texture_max_memory_mb"] = str(arnold_options_node.textureMaxMemoryMB.get())
        if arnold_options_node.hasAttr("threads_autodetect"):
            scene_info_option_dict["threads_autodetect"] = str(arnold_options_node.threads_autodetect.get())            
        if arnold_options_node.hasAttr("renderType"):
            scene_info_option_dict["render_type"] = str(arnold_options_node.renderType.get())
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
        return scene_info_option_dict

    def encode_str(self,my_str):
        if my_str:        
            my_str=my_str.encode('unicode-escape').decode('string_escape')
        else:
            my_str = str(None)
        print my_str
        return my_str
        
    def unicode_to_str(self,str1,str_encode = 'system'):
        if isinstance(str1,unicode):
            try:
                if str_encode.lower() == 'system':
                    str1=str1.encode(sys.getfilesystemencoding())
                elif str_encode.lower() == 'utf-8':
                    str1 = str1.encode('utf-8')
                elif str_encode.lower() == 'gbk':
                    str1 = str1.encode('gbk')
                else:
                    str1 = str1.encode(str_encode)
            except Exception as e:
                print '[err]unicode_to_str:encode %s to %s failed' % (str1,str_encode)
                print e
        else:
            print '%s is not unicode ' % (str1)
        return str(str1)
        
       
        
    def get_vraysetting(self):
        try:
            vraySettings_node = pm.PyNode('defaultArnoldRenderOptions')
        except :
            vraySettings_node = pm.createNode('aiOptions', name='defaultArnoldRenderOptions', skipSelect=True, shared=True)
        scene_info_option_dict = collections.OrderedDict()
        vraySettings = pm.PyNode("vraySettings")
        scene_info_option_dict["dynMemLimit"] = str(vraySettings.sys_rayc_dynMemLimit.get())
        scene_info_option_dict["animType"] = str(vraySettings.animType.get())       
        scene_info_option_dict['pre_render_mel'] = self.defaultRG.preMel.get()
        scene_info_option_dict['post_render_mel'] = self.defaultRG.postMel.get()
        scene_info_option_dict['pre_render_layer_mel'] = self.defaultRG.preRenderLayerMel.get()
        scene_info_option_dict['post_render_layer_mel'] = self.defaultRG.postRenderLayerMel.get()
        scene_info_option_dict['pre_render_frame_mel'] = self.defaultRG.preRenderMel.get()
        scene_info_option_dict['post_render_frame_mel'] = self.defaultRG.postRenderMel.get()
        scene_info_option_dict['pre_key_frame_mel'] = vraySettings.preKeyframeMel.get()
        scene_info_option_dict['rt_image_ready_mel'] = vraySettings.rtImageReadyMel.get()
        return scene_info_option_dict


    def get_redshiftsetting(self):
        scene_info_option_dict = collections.OrderedDict()
        redshift_options = pm.PyNode("redshiftOptions")
        if redshift_options.hasAttr("motionBlurEnable"):
            scene_info_option_dict["absolute_procedural_paths"] = redshift_options.motionBlurEnable.get()
        if redshift_options.hasAttr("motionBlurDeformationEnable"):
            scene_info_option_dict["motion_blur_deformation_enable"] = redshift_options.motionBlurDeformationEnable.get()             

        scene_info_option_dict['pre_render_mel'] = redshift_options.preRenderMel.get()
        scene_info_option_dict['post_render_mel'] = redshift_options.postRenderMel.get()
        scene_info_option_dict['pre_render_layer_mel'] = redshift_options.preRenderLayerMel.get()
        scene_info_option_dict['post_render_layer_mel'] = redshift_options.postRenderLayerMel.get()
        scene_info_option_dict['pre_render_frame_mel'] = redshift_options.preRenderFrameMel.get()
        scene_info_option_dict['post_render_frame_mel'] = redshift_options.postRenderFrameMel.get()
        return scene_info_option_dict




    def get_rendermansetting(self):
        pass

    def get_mayakrakatoasetting(self):
        pass


    def get_rendersetting(self):    
        scene_info_dict = collections.OrderedDict()  
        layer_dict = collections.OrderedDict()
        self.defaultRG = pm.PyNode("defaultRenderGlobals")
        self.show_hide_node()
        all_render_layer = cmds.listConnections("renderLayerManager.renderLayerId")
        for layer in all_render_layer:
            if layer:
                pm.PyNode(layer).setCurrent()
                if self.is_renderable_layer(layer):               
                    layer_dict['renderable'] = '1'
                else:
                    layer_dict['renderable'] = '0'                    
                renderer = str(self.GetCurrentRenderer())
                layer_dict['common'] = self.get_defaultrenderglobals(layer)
                layer_dict['is_default_camera'] = '1'
                if renderer == "vray":
                    layer_dict['option'] = self.get_vraysetting()
                elif renderer == "arnold":
                    layer_dict['option'] = self.get_arnoldsetting()
                elif renderer == "redshift":
                    layer_dict['option'] = self.get_redshiftsetting()
                elif renderer == "renderman":
                    layer_dict['option'] = self.get_rendermansetting()
                elif renderer == "MayaKrakatoa":
                    layer_dict['option'] = self.get_rendermansetting()
                else:
                    pass
                self.scene_info_dict[layer] = layer_dict
            else:
                raise Exception("Can't switch renderlayer " + layer)        
        
        
        
            # try:
                # pm.PyNode(layer).setCurrent()
                # if layer.type() == "renderLayer":
                    # if layer.renderable.get():
                        # self.scene_info_dict[layer]['renderable'] = '1'
                    # else:
                        # self.scene_info_dict[layer]['renderable'] = '0'                
                # renderer = str(self.GetCurrentRenderer())
                # self.get_defaultrenderglobals(layer)
                # if renderer == "vray":
                    # self.get_vraysetting(layer)
                # elif renderer == "arnold":
                    # self.get_arnoldsetting(layer)
                # elif renderer == "redshift":
                    # self.get_redshiftsetting(layer)
                # elif renderer == "renderman":
                    # self.get_rendermansetting(layer)
                # elif renderer == "MayaKrakatoa":
                    # self.get_rendermansetting(layer)
                # else:
                    # pass
            # except:
                # raise Exception("Can't switch renderlayer " + layer)

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

    def getMentalRayElementNames(self,currentRenderLayer):

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


    #------------get assets   return  a  list -------------

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
        renderer=str(pm.mel.currentRenderer())
        if renderer == "_3delight":
            renderer="3delight"
            
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

    def GetMayaOutputPrefix(self,layer):

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


    def GetRenderableCameras(self,ignoreDefaultCameras):

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

    def IsCameraRenderable(self,cameraName):

        relatives = pm.listRelatives(cameraName, s=1)
        # print( "Checking if camera is renderable: " + $cameraName + "\n" );
        cameraShape = relatives[0]
        cameraRenderable = 0
        # Getting the renderable attribute can throw an error if there are duplicate camera shape names.
        # The catch blocks are to prevent these erros so that the submission can continue.
        if not pm.catch(lambda: pm.mel.attributeExists("renderable", cameraShape)):
            cameraRenderable = int(pm.getAttr(cameraShape + ".renderable"))
            pm.catch(lambda :cameraRenderable)

        return cameraRenderable

    def IsDefaultCamera(self,cameraName):
        if cameraName == "frontShape" or cameraName == "perspShape" or cameraName == "sideShape" or cameraName == "topShape":
            return True
        elif cameraName == "front" or cameraName == "persp" or cameraName == "side" or cameraName == "top":
            return True
        else:
            return False

    def IsRenderLayersOn(self):
        """Returns if render layers is on."""

        renderLayers = pm.ls(exactType="renderLayer")
        referenceLayers = pm.ls(exactType="renderLayer", rn=1)
        return ((len(renderLayers) - len(referenceLayers)) > 1)

    def getMel(self):
        scene_info_option_dict = {}
        renderer = str(self.GetCurrentRenderer())
        if renderer == "redshift":
            render_node = pm.PyNode("redshiftOptions")
            scene_info_option_dict['pre_render_mel'] = render_node.preRenderMel.get()
            scene_info_option_dict['post_render_mel'] = render_node.postRenderMel.get()
            scene_info_option_dict['pre_render_layer_mel'] = render_node.preRenderLayerMel.get()
            scene_info_option_dict['post_render_layer_mel'] = render_node.postRenderLayerMel.get()
            scene_info_option_dict['pre_render_frame_mel'] = render_node.preRenderFrameMel.get()
            scene_info_option_dict['post_render_frame_mel'] = render_node.postRenderFrameMel.get()
        elif renderer == "vray":
            vraySettings = pm.PyNode("vraySettings")
            render_node = pm.PyNode("defaultRenderGlobals")
            scene_info_option_dict['pre_render_mel'] = render_node.preMel.get()
            scene_info_option_dict['post_render_mel'] = render_node.postMel.get()
            scene_info_option_dict['pre_render_layer_mel'] = render_node.preRenderLayerMel.get()
            scene_info_option_dict['post_render_layer_mel'] = render_node.postRenderLayerMel.get()
            scene_info_option_dict['pre_render_frame_mel'] = render_node.preRenderMel.get()
            scene_info_option_dict['post_render_frame_mel'] = render_node.postRenderMel.get()
            scene_info_option_dict['pre_key_frame_mel'] = vraySettings.preKeyframeMel.get()
            scene_info_option_dict['rt_image_ready_mel'] = vraySettings.rtImageReadyMel.get()
        else:
            render_node = pm.PyNode("defaultRenderGlobals")
            scene_info_option_dict['pre_render_mel'] = render_node.preMel.get()
            scene_info_option_dict['post_render_mel'] = render_node.postMel.get()
            scene_info_option_dict['pre_render_layer_mel'] = render_node.preRenderLayerMel.get()
            scene_info_option_dict['post_render_layer_mel'] = render_node.postRenderLayerMel.get()
            scene_info_option_dict['pre_render_frame_mel'] = render_node.preRenderMel.get()
            scene_info_option_dict['post_render_frame_mel'] = render_node.postRenderMel.get()
            
        return scene_info_option_dict

    def RB_HAN_RESULT(self):#8
        self.format_log('结果处理','start')
        self.G_DEBUG_LOG.info('[AnalyzeMax.RB_HAN_RESULT.start.....]') 
        if not os.path.exists(self.G_ANALYZE_TXT_NODE):
            CLASS_COMMON_UTIL.error_exit_log(self.G_DEBUG_LOG,'Analyze max file failed . result file analyze.txt not exists')
        
        task_json_name='task.json'
        asset_json_name='asset.json'
        tips_json_name='tips.json'
        node_task_json = os.path.join(self.G_WORK_RENDER_TASK_CFG,task_json_name)
        node_asset_json = os.path.join(self.G_WORK_RENDER_TASK_CFG,asset_json_name)
        node_tips_json = os.path.join(self.G_WORK_RENDER_TASK_CFG,tips_json_name)
        
        
        self.parse_analyze_txt()
        scene_info_dict=self.han_task_json(node_task_json)
        asset_json_dict=self.han_asset_json(node_asset_json)
        self.han_tips_json(node_tips_json,scene_info_dict,asset_json_dict)            
            
            
            
            
        
    #=================================================task.json===================================================   
    def han_task_json(self,node_task_json):
        scene_info_dict={}
        scene_info_common_dict={}
        scene_info_renderer_dict={}
        miscellaneous_dict={}
        

        self.G_TASK_JSON_DICT['scene_info']=scene_info_dict
        self.G_TASK_JSON_DICT['miscellaneous']=miscellaneous_dict
        task_json_str = json.dumps(self.G_TASK_JSON_DICT,ensure_ascii=False)
        CLASS_COMMON_UTIL.write_file(task_json_str,node_task_json)
        return scene_info_dict

    #=================================================asset.json===================================================
    def han_asset_json(self,node_asset_json):
        self.loop_project_asset()
        asset_json_dict=self.get_all_asset()
        asset_json_dict['maya']=[self.G_INPUT_CG_FILE]
        asset_json_str = json.dumps(asset_json_dict,ensure_ascii=False)
        
        CLASS_COMMON_UTIL.write_file(asset_json_str,node_asset_json)
        return asset_json_dict
        
    
    #=================================================tips.json===================================================    
    def han_tips_json(self,node_tips_json,scene_info_dict,asset_json_dict):

        
        #------------write tips----------- 
        tips_json_str = json.dumps(tips_json_dict,ensure_ascii=False)
        CLASS_COMMON_UTIL.write_file(tips_json_str,node_tips_json)
                        
    def writing_error(self,error_code, info=""):
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
                        
class ErrorJson(dict):

    def __init__(self, json_file):
        dict.__init__(self)
        self.json_file = json_file
        if os.path.exists(self.json_file):
            self.update(json.load(open(self.json_file, "r")))

    def save(self):
        json.dump(self, open(self.json_file, 'w'))                        
                        
                        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='maya check python')
    parser.add_argument("--ui", dest="user_id", type=int)
    parser.add_argument("--ti", dest="task_id", type=int)
    parser.add_argument("--proj", dest="cg_project", type=str)
    parser.add_argument("--cgfile", dest="cg_file", type=str)
    parser.add_argument("--taskjson", dest="task_json", type=str)
    parser.add_argument("--assetjson", dest="asset_json", type=str)
    parser.add_argument("--tipsjson", dest="tips_json", type=str)
    options = parser.parse_args().__dict__
    print options
    analyze = Analyze(options)
    analyze.run()
    analyze.write_info_file()
    print "success\n"
    print "Analyse end.........................................."