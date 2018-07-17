#!/usr/bin/env python
#encoding:utf-8
# -*- coding: utf-8 -*-

import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import os,sys,re
import logging
import datetime
import time
import shutil
import collections
from pymel import versions


currentPath = r"\\10.80.100.101\o5\py\model"
script_path = os.path.join(currentPath, "script")
sys.path.append(script_path)



class PreRenderBase(object):
    def __init__(self):
        pass


    def str_to_unicode(self, encode_str):
        if isinstance(encode_str, unicode):
            return encode_str
        else:
            code = self.get_encode(encode_str)
            return encode_str.decode(code)


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
            pass
        return str(str1)


    def GetCurrentRenderer(self):
        """Returns the current renderer."""
        renderer = str(pm.mel.currentRenderer())
        if renderer == "_3delight":
            renderer = "3delight"

        return renderer


    def change_path(self,node_type, attr_name, mapping, rep_path, dicts):
        maya_proj_paht = cmds.workspace(q=True, fullName=True)
        source_path = "%s/sourceimages" % (maya_proj_paht)
        scenes_path = "%s/scenes" % (maya_proj_paht)
        data_path = "%s/data" % (maya_proj_paht)
        register_node_types = pm.ls(nodeTypes=1)
        if node_type in register_node_types:
            all_node = pm.ls(type=node_type)
            if len(all_node) != 0:
                print "the  node type  is %s" % (node_type)
                for node in all_node:
                    if node.hasAttr(attr_name):
                        # file_path = cmds.getAttr(node + "."+attr_name)
                        refcheck = pm.referenceQuery(node, inr=True)
                        # print "refcheck %s " % (refcheck)
                        if (refcheck == False):
                            try:
                                node.attr(attr_name).set(l=0)
                            except Exception, error:
                                print Exception, ":", error
                                pass
                        file_path = node.attr(attr_name).get()
                        if file_path != None and file_path.strip() != "":
                            file_path = file_path.replace('\\', '/')
                            file_path = file_path.replace('<udim>', '1001')
                            file_path = file_path.replace('<UDIM>', '1001')
                            if os.path.exists(file_path) == 0:
                                asset_name = os.path.split(file_path)[1]
                                file_path_new = file_path
                                if rep_path:
                                    file_path_new = "%s/%s" % (rep_path, asset_name)
                                if os.path.exists(file_path_new) == 0 and mapping:
                                    for repath in mapping:
                                        if mapping[repath] != repath:
                                            if file_path.find(repath) >= 0:
                                                file_path_new = file_path.replace(repath, mapping[repath])

                                if os.path.exists(file_path_new) == 0:
                                    file_path_new = "%s/%s" % (source_path, asset_name)
                                if os.path.exists(file_path_new) == 0:
                                    file_path_new = "%s/%s" % (scenes_path, asset_name)
                                if os.path.exists(file_path_new) == 0 and dicts:
                                    if asset_name in dicts:
                                        file_path_new = dicts[asset_name]

                                if os.path.exists(file_path_new) == 0:
                                    print "the %s node %s  %s is not find ::: %s " % (node_type, node, attr_name, file_path)
                                else:
                                    cmds.setAttr((node + "." + attr_name), file_path_new, type="string")

    def change_path_mapping(self,node_type, attr_name, mapping):
        print "the  node type  is %s" % (node_type)
        maya_proj_paht = cmds.workspace(q=True, fullName=True)
        source_path = "%s/sourceimages" % (maya_proj_paht)
        scenes_path = "%s/scenes" % (maya_proj_paht)
        data_path = "%s/data" % (maya_proj_paht)
        all_node = pm.ls(type=node_type)
        if len(all_node) != 0:
            for node in all_node:
                if node.hasAttr(attr_name):
                    # file_path = cmds.getAttr(node + "."+attr_name)
                    refcheck = pm.referenceQuery(node, inr=True)

                    if (refcheck == False):
                        try:
                            node.attr(attr_name).set(l=0)
                        except Exception, error:
                            print Exception, ":", error
                            pass
                    file_path = node.attr(attr_name).get()
                    if file_path != None and file_path.strip() != "":
                        file_path = file_path.replace('\\', '/')
                        if os.path.exists(file_path) == 0:
                            asset_name = os.path.split(file_path)[1]
                            file_path_new = file_path
                            print file_path_new
                            if os.path.exists(file_path_new) == 0 and mapping:
                                for repath in mapping:
                                    if mapping[repath] != repath:
                                        if file_path.find(repath) >= 0:
                                            file_path_new = file_path.replace(repath, mapping[repath])
                                            print file_path_new
                                            cmds.setAttr((node + "." + attr_name), file_path_new, type="string")


    def replace_path(self,node_type, attr_name, rep_path, repath_new):
        maya_proj_paht = cmds.workspace(q=True, fullName=True)
        source_path = "%s/sourceimages" % (maya_proj_paht)
        scenes_path = "%s/scenes" % (maya_proj_paht)
        data_path = "%s/data" % (maya_proj_paht)
        all_node = pm.ls(type=node_type)
        if all_node:
            for node in all_node:
                # file_path = cmds.getAttr(node + "."+attr_name)
                refcheck = pm.referenceQuery(node, inr=True)
                if (refcheck == False):
                    node.attr(attr_name).set(l=0)
                file_path = node.attr(attr_name).get()
                print file_path
                if file_path != None and file_path.strip() != "":
                    file_path_new = file_path.replace(rep_path, repath_new)
                    print file_path_new
                    cmds.setAttr((node + "." + attr_name), file_path_new, type="string")
                    print "%s %s %s " % (node, attr_name, file_path_new)


    def set_cam_render(self,cams):
        print "multiple cams to cmd"
        cams_list = cams.split(',')

        cams_all = pm.ls(type='camera')
        for cam in cams_all:
            mel.eval('removeRenderLayerAdjustmentAndUnlock("%s.renderable")' % cam)
            if cam not in cams_list:
                cmds.setAttr(cam + ".renderable", 0)
            else:
                cmds.setAttr(cam + ".renderable", 1)


    def del_cam(self,cams):
        print "multiple cams to cmd"
        cams_all = pm.ls(type='camera')
        if cams:
            cams_list = cams.split(',')

            for cam in cams_all:
                mel.eval('removeRenderLayerAdjustmentAndUnlock("%s.renderable")' % cam)
                if cam not in cams_list:
                    try:
                        self.del_node(cam)

                    except:
                        print "the %s dont del " % (cam)
                        pass
                else:
                    print "the cam %s is render" % (cam)
        else:
            for cam in cams_all:
                mel.eval('removeRenderLayerAdjustmentAndUnlock("%s.renderable")' % cam)
                if cmds.getAttr(cam + ".renderable")==0:
                    try:
                        self.del_node(cam)

                    except:
                        print "the %s dont del " % (cam)
                        pass
                else:
                    print "the cam %s is render" % (cam)


    def set_layer_render(self,layers):
        print "multiple render layer to cmd"
        layers_list = layers.split(',')

        layers_all = cmds.listConnections("renderLayerManager.renderLayerId")
        for layer in layers_all:
            mel.eval('removeRenderLayerAdjustmentAndUnlock("%s.renderable")' % layer)
            if layer not in layers_list:
                cmds.setAttr(layer + ".renderable", 0)
            else:
                cmds.setAttr(layer + ".renderable", 1)


    def file_dicts(self,search):
        dicts = {}
        for parents, dirnames, filenames in os.walk(search):
            for filename in filenames:
                dicts[filename] = os.path.join(parents, filename)
        return dicts


    def rep_path_def(self,mapping, old_path):
        if mapping:
            file_path_new = old_path
            for repath in mapping:
                if mapping[repath] != repath:
                    if old_path.find(repath) >= 0:
                        file_path_new = old_path.replace(repath, mapping[repath])
            if os.path.exists(file_path_new):
                return file_path_new
            else:
                return old_path
        else:
            return old_path


    def get_graph_path(self,node):
        return cmds.getAttr(node + '.cacheFileName')


    def set_graph_path(self,node, path):
        cmds.setAttr(node + '.cacheFileName', path)


    def get_texture_node(self,graph_node):
        mel_cmd = 'pgYetiGraph -listNodes -type "texture" %s' % str(graph_node)
        texture_nodes = mel.eval(mel_cmd)
        return texture_nodes


    def get_texture_path(self,texture, graph):
        mel_cmd = 'pgYetiGraph -node "%s" -param "file_name" -getParamValue %s' % (str(texture), str(graph))
        path = mel.eval(mel_cmd)
        return path


    def set_texture_path(self,path, node, graph):
        mel_cmd = 'pgYetiGraph -node "{node_name}" -param "file_name" -setParamValueString {path}  {graph}' \
            .format(node_name=str(node), path=str(path), graph=str(graph))
        print mel_cmd


    def set_yeti_imageSearchPath(self,mapping):

        maya_proj_paht = cmds.workspace(q=True, fullName=True)
        source_path = "%s/sourceimages" % (maya_proj_paht)
        scenes_path = "%s/scenes" % (maya_proj_paht)

        all_yeti_nodes = cmds.ls(type='pgYetiMaya')
        if len(all_yeti_nodes) != 0:
            for node_name in all_yeti_nodes:
                # cache = get_graph_path(node_name)
                tnodes = self.get_texture_node(node_name)
                yeti_dict = {}
                yeti_texs = []
                # print node_name
                if tnodes != None:
                    if len(tnodes) != 0:
                        for tx_node in tnodes:
                            texs = self.get_texture_path(tx_node, node_name)
                            texs = texs.replace('\\', '/')
                            texs = texs.replace('<udim>', '1001')
                            texs = texs.replace('<UDIM>', '1001')
                            if os.path.exists(texs) == 0 and texs != "" and texs != None:
                                tex_new_path = self.rep_path_def(mapping, texs)
                                # print tex_new_path
                                if os.path.exists(tex_new_path) == 0:
                                    print "the %s node %s   is not find :: %s" % (node_name, tx_node, texs)

                                yeti_texs.append(os.path.dirname(tex_new_path))

                        cmds.setAttr(node_name + ".imageSearchPath", l=0)
                        yeti_searchpath = ";".join(yeti_texs)
                        if cmds.getAttr(node_name + ".imageSearchPath"):
                            yeti_searchpath += ";" + cmds.getAttr(node_name + ".imageSearchPath")
                        if source_path:
                            yeti_searchpath += ";" + source_path
                        if scenes_path:
                            yeti_searchpath += ";" + scenes_path

                        cmds.setAttr(node_name + ".imageSearchPath", yeti_searchpath, type='string')


    def del_node(self,node_name):
        if pm.objExists(node_name):
            try:
                tran = pm.listTransforms(node_name)

                for a in tran:
                    pm.delete(a)
                    print "the %s is del " % (a)
            except:
                print "the %s dont del " % (node_name)
                pass


    def delete_unknown(self):
        unknownNodes = cmds.ls(type='unknown')
        if unknownNodes:
            try:
                for node in unknownNodes:
                    print 'deleting: ' + node
                    cmds.lockNode(node, lock=False)
                    cmds.delete(node)
            except Exception as err:
                print('=== Error(delete unknown node) Msg : %s ===' % (err))


    def CheckSlashes(self, filename):
        """Ensures that all slashes are consistent throughout the filename."""
        result = filename
        # string $result = substituteAllString( $filename, "\\", "/" ); // switch from '\' to '/'
        # $result = substituteAllString( $result, "//", "/" ); // replace double '/' where paths may have been combined
        # if( startsWith( $result, "/" ) )
        #	$result = "/" + $result;
        # return $result;
        newResult = ""
        newResult = result.replace("\\\\", "/")
        while newResult != result:
            result = newResult
            newResult = result.replace("\\\\", "/")

        result = newResult
        newResult = result.replace("//", "/")
        while newResult != result:
            result = newResult
            newResult = result.replace("//", "/")

        if pm.about(ntOS=1):
            if newResult.startswith("/"):
                newResult = "/" + newResult

        return newResult


    def GetStrippedSceneFileName(self):

        fileName = str(cmds.file(q=1, sceneName=1))
        fileName = str(pm.mel.basename(fileName, ".mb"))
        fileName = str(pm.mel.basename(fileName, ".ma"))
        return fileName


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


    def Test_prerender(self):
        print "do  custome prerender success!!!!!!!!!!!!!!!!!!!!"


    def get_image_namespace(self):
        index = 0
        RenderNode = pm.PyNode("defaultRenderGlobals")
        Renderer_name = RenderNode.currentRenderer.get()
        render_engine = str(Renderer_name)
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
            print "Current namespace is %s ," % (name_space.get(index))
            mel.eval("setMayaSoftwareFrameExt(3,0);")

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


    def log_scene(self,attr,value):
        print("[PreRender] Scene %s is :: %s" %(attr,str(value)))

    def log_scene_set(self,attr,value):
        print("[PreRender] Set %s >>> %s" %(attr,str(value)))



class PreRender(dict,PreRenderBase):
    
    def __init__(self,pre_dict,mylog=None):

        PreRenderBase.__init__(self)
        dict.__init__(self)
        self.pre_dict = pre_dict
        self.log = mylog
        # self.enable_layered = pre_dict["enable_layered"]
        # self.projectPath = pre_dict["projectPath"]
        self.mapping = pre_dict["mapping"]
        # self.renderableCamera = pre_dict["renderableCamera"]
        # self.renderableLayer = pre_dict["renderableLayer"]
        # self.task_json = pre_dict["task_json"]
        self.start = pre_dict["start"]
        self.c_prerender = pre_dict["c_prerender"]
        self.user_id = pre_dict["user_id"]
        self.plugins = pre_dict["plugins"]
        self.rendersetting = pre_dict["rendersetting"]
        self.task_id = pre_dict["task_id"]



        #-----------------------------------------log-----------------------------------------------

        #-------------global vars-------------
        self.MAYA_PROJ_PATH = cmds.workspace(q=True, fullName=True)
        self.SOURCE_PATH = "%s/sourceimages" % (self.MAYA_PROJ_PATH)
        self.SCENES_PATH = "%s/scenes" % (self.MAYA_PROJ_PATH)
        self.RENDER_NODE = pm.PyNode("defaultRenderGlobals")
        yeti_load = cmds.pluginInfo("pgYetiMaya", query=True, loaded=True )
        yeti_vray_load = cmds.pluginInfo("pgYetiVRayMaya", query=True, loaded=True )
        shave_load = cmds.pluginInfo("shaveNode", query=True, loaded=True )

        rep_path = ""
        search = ""
        dicts = {}         
        #-----------unlock   node------
        pm.lockNode( 'defaultRenderGlobals', lock=False )




        #--------------------------------bak-----------------------------

        self.maya_proj_paht = cmds.workspace(q=True, fullName=True)
        self.source_path = "%s/sourceimages" % (self.maya_proj_paht)
        self.scenes_path = "%s/scenes" % (self.maya_proj_paht)
        self.render_node = pm.PyNode("defaultRenderGlobals")
        self.render_name = self.render_node.currentRenderer.get()
        yeti_load = cmds.pluginInfo("pgYetiMaya", query=True, loaded=True)
        yeti_vray_load = cmds.pluginInfo("pgYetiVRayMaya", query=True, loaded=True)
        shave_load = cmds.pluginInfo("shaveNode", query=True, loaded=True)

        rep_path = ""
        search = ""
        dicts = {}

    def mylog(self,message,extr="PreRender"):
        if self.log:
            self.log.info("[%s] %s"%(extr,str(message)))         
        else:        
            if str(message).strip() != "":
                print("[%s] %s"%(extr,str(message)))

    def get_scene_info(self):
        self.mtoa_dict = {}
        self.vray_dict = {}
        self.redshift_dict = {}
        self.mentalray_dict = {}

        renderer = str(self.GetCurrentRenderer())

        if renderer == "vray":
            pass

        elif renderer == "arnold":
            try:
                arnold_options_node = pm.PyNode('defaultArnoldRenderOptions')
            except:
                arnold_options_node = pm.createNode('aiOptions', name='defaultArnoldRenderOptions', skipSelect=True,
                                                    shared=True)
            try:
                arnold_filter_node = pm.PyNode('defaultArnoldFilter')
            except:
                arnold_filter_node = pm.createNode('aiAOVFilter', name='defaultArnoldFilter', skipSelect=True,
                                                   shared=True)
            try:
                arnold_driver_node = pm.PyNode('defaultArnoldDriver')
            except:
                arnold_driver_node = pm.createNode('aiAOVDriver', name='defaultArnoldDriver', skipSelect=True,
                                                   shared=True)
            try:
                arnold_display_driver_node = pm.PyNode('defaultArnoldDisplayDriver')
            except:
                arnold_display_driver_node = pm.createNode('aiAOVDriver', name='defaultArnoldDisplayDriver',
                                                           skipSelect=True, shared=True)
            try:
                resolution_node = pm.PyNode('defaultResolution')
            except:
                resolution_node = pm.createNode('resolution', name='defaultResolution', skipSelect=True, shared=True)

            if arnold_driver_node.hasAttr("append"):
                self.mtoa_dict["append"] = str(arnold_driver_node.append.get())

            if arnold_driver_node.hasAttr("tiled"):
                self.mtoa_dict["tiled"] = str(arnold_driver_node.tiled.get())

            self.mtoa_dict["aov_output_mode"] = str(arnold_driver_node.outputMode.get())
            self.mtoa_dict["motion_blur_enable"] = str(arnold_options_node.motion_blur_enable.get())
            self.mtoa_dict["merge_aovs"] = str(arnold_driver_node.mergeAOVs.get())
            self.mtoa_dict["abort_on_error"] = str(arnold_options_node.abortOnError.get())
            self.mtoa_dict["log_verbosity"] = str(arnold_options_node.log_verbosity.get())
            # sampling---------------
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

            self.mtoa_dict["sampling"] = [AASamples, GIDiffuseSamples, sampling_3, sampling_4, sampling_5,
                                          sampling_6]

            if arnold_options_node.hasAttr("autotx"):
                self.mtoa_dict["auto_tx"] = str(arnold_options_node.autotx.get())
                if self.mtoa_dict["auto_tx"] == 'False':
                    self.mtoa_dict["use_existing_tiled_textures"] = str(arnold_options_node.use_existing_tiled_textures.get())
            if arnold_options_node.hasAttr("textureMaxMemoryMB"):
                self.mtoa_dict["textureMaxMemoryMB"] = str(arnold_options_node.textureMaxMemoryMB.get())
            if arnold_options_node.hasAttr("threads_autodetect"):
                self.mtoa_dict["threads_autodetect"] = str(arnold_options_node.threads_autodetect.get())
            if arnold_options_node.hasAttr("renderType"):
                self.mtoa_dict["render_type"] = str(arnold_options_node.renderType.get())
            if arnold_options_node.hasAttr("absoluteTexturePaths"):
                self.mtoa_dict["absolute_texture_paths"] = str(arnold_options_node.absoluteTexturePaths.get())
            if arnold_options_node.hasAttr("absoluteProceduralPaths"):
                self.mtoa_dict["absolute_procedural_paths"] = str(arnold_options_node.absoluteProceduralPaths.get())

    def reset_scene_info(self):
        self.get_scene_info()
        default_globals = pm.PyNode("defaultRenderGlobals")
        render_node = pm.PyNode("defaultRenderGlobals")
        render_name = render_node.currentRenderer.get()
        w = cmds.getAttr("defaultResolution.width")
        h = cmds.getAttr("defaultResolution.height")
        self.log_scene("The Maya version with update",str(versions.current()))
        self.log_scene("renderner", str(render_name))
        self.log_scene("imageFilePrefix", self.unicode_to_str(self.GetMayaOutputPrefix()))
        self.log_scene("Outpu format", str(self.get_image_format()))
        self.log_scene("Resolution", str(str(w)+' '+str(h)))

        default_globals.modifyExtension.set(0)
        self.log_scene_set("Renumber frames","off")

        # renderable_cam = []
        # for i in pm.ls(type="camera"):
        #     if i.renderable.get(): renderable_cam.append(i)
        # if not len(renderable_cam):
        #     print("PL set an camera to render scene.")
        #     sys.exit(001)
        if render_name == "arnold":
            arnold_options_node = pm.PyNode('defaultArnoldRenderOptions')
            arnold_driver_node = pm.PyNode('defaultArnoldDriver')
            #-----------------log----------------------
            if "append" in self.mtoa_dict:
                self.log_scene("append", self.mtoa_dict["append"])
                if self.mtoa_dict["append"]:
                    arnold_driver_node.append.set(0)
                    self.log_scene_set("append",0)

            if "tiled" in self.mtoa_dict:
                self.log_scene("tiled", self.mtoa_dict["tiled"])
                if self.mtoa_dict["tiled"]:
                    arnold_driver_node.tiled.set(0)
                    self.log_scene_set("tiled",0)

            if arnold_driver_node.hasAttr("autocrop"):
                arnold_driver_node.autocrop.set(0)
                self.log_scene_set("autocrop", 0)


            if arnold_driver_node.hasAttr("outputPadded"):
                arnold_driver_node.outputPadded.set(1)
                self.log_scene_set("outputPadded",1)


            if "tiled" in self.mtoa_dict:
                self.log_scene("tiled", self.mtoa_dict["tiled"])
                if self.mtoa_dict["tiled"]:
                    arnold_driver_node.tiled.set(0)
                    self.log_scene_set("tiled",0)



            if "threads_autodetect" in self.mtoa_dict:
                self.log_scene("threads_autodetect", self.mtoa_dict["threads_autodetect"])
                if not self.mtoa_dict["threads_autodetect"]:
                    arnold_options_node.threads_autodetect.set(1)
                    self.log_scene_set("threads_autodetect",1)

            if "abort_on_error" in self.mtoa_dict:
                self.log_scene("abort_on_error", self.mtoa_dict["abort_on_error"])
                # if self.mtoa_dict["abort_on_error"]:
                #     arnold_options_node.abortOnError.set(0)
                #     self.log_scene_set("abort_on_error",0)

            if "log_verbosity" in self.mtoa_dict:
                self.log_scene("log_verbosity", self.mtoa_dict["log_verbosity"])

            if "motion_blur_enable" in self.mtoa_dict:
                self.log_scene("motion_blur_enable", self.mtoa_dict["motion_blur_enable"])
                if self.mtoa_dict["motion_blur_enable"] == "1":
                        if arnold_options_node.hasAttr("ignoreMotionBlur"):
                            ignoreMotionBlur = arnold_options_node.ignoreMotionBlur.get()
                            self.log_scene("ignoreMotionBlur",ignoreMotionBlur)

            if "merge_aovs" in self.mtoa_dict:
                self.log_scene("merge_aovs", self.mtoa_dict["merge_aovs"])

            if "aov_output_mode" in self.mtoa_dict:
                mode_dict ={0:"GUI Only",1:"Batch Only",2:"GUI and Batch"}
                self.log_scene("aov_output_mode", mode_dict[int(self.mtoa_dict["aov_output_mode"])])
                if not self.mtoa_dict["aov_output_mode"]:
                    arnold_driver_node.outputMode.set(2)
                    self.log_scene_set("aov_output_mode",mode_dict[2])

            if "textureMaxMemoryMB" in self.mtoa_dict:
                self.log_scene("textureMaxMemoryMB", self.mtoa_dict["textureMaxMemoryMB"])
                if float(self.mtoa_dict["textureMaxMemoryMB"]) < 20480:
                    arnold_options_node.textureMaxMemoryMB.set(20480)
                    self.log_scene_set("textureMaxMemoryMB",20480)

                elif float(self.mtoa_dict["textureMaxMemoryMB"]) > 40960:
                    arnold_options_node.textureMaxMemoryMB.set(40960)
                    self.log_scene_set("textureMaxMemoryMB", 40960)


            if "auto_tx" in self.mtoa_dict:
                self.log_scene("auto_tx", self.mtoa_dict["auto_tx"])
                if self.mtoa_dict["auto_tx"] == "True":
                    arnold_options_node.autotx.set(0)
                    self.log_scene_set("auto_tx",False)
                else:
                    self.log_scene("use_existing_tiled_textures", self.mtoa_dict["use_existing_tiled_textures"])

            for i in pm.ls(type="aiStandIn"):
                if i.hasAttr("deferStandinLoad"):
                    i.deferStandinLoad.set(0)

        elif render_name == "vray":
            vraySettings = pm.PyNode("vraySettings")
            dynMemLimit = vraySettings.sys_rayc_dynMemLimit.get()
            self.log_scene("dynMemLimit",dynMemLimit)

            if vraySettings.hasAttr("animType"):
                animType_dict = {0:"disable",1:"standard",2:"specific frames"}
                animType = vraySettings.animType.get()
                self.log_scene("animType",animType_dict[animType])
                if animType != 1:
                    vraySettings.animType.set(1)
                    self.log_scene_set("animType",animType_dict[1])

        yeti_load = cmds.pluginInfo("pgYetiMaya", query=True, loaded=True)
        if yeti_load:
            for i in pm.ls(type="pgYetiMaya"):
                if i.hasAttr("aiLoadAtInit"):
                    i.aiLoadAtInit.set(1)
        sys.stdout.flush()

    def han_custome_prerender(self):
        # Check is the config file exists ----------------------------------
        if os.path.exists(self.c_prerender):
            self.mylog('--------------Handle the C_PreRender.py-----------------')
            cfgFileDir = os.path.dirname(self.c_prerender)
            cfgFileName = os.path.splitext(os.path.split(self.c_prerender)[-1])[0]
            sys.path.append(cfgFileDir)
            try:
                cfg = __import__('C_PreRender')
                reload(cfg)
                cfg.main(self.pre_dict)
            except Exception as err:
                self.mylog('=== Error occur import/execute "%s"! ===\n=== Error Msg : %s ===' % (self.c_prerender, err))
            try:
                while True:
                    sys.path.remove(cfgFileDir)
            except:
                pass
        else:
            self.mylog('--------the C_PreRender.py is not exists!-----------')

    def get_image_namespace(self):
        index = 0
        RenderNode = pm.PyNode("defaultRenderGlobals")
        Renderer_name = RenderNode.currentRenderer.get()
        render_engine = str(Renderer_name)
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
            self.log_scene("Namespace",name_space.get(index))
            mel.eval("setMayaSoftwareFrameExt(3,0);")
            self.log_scene_set("Namespace","name.#.ext")

    def GetMayaOutputPrefix(self):
        prefix = ""
        renderer = str(self.GetCurrentRenderer())

        if renderer != "vray":
            prefix = pm.getAttr('defaultRenderGlobals.imageFilePrefix')
        else:
            prefix = pm.getAttr('vraySettings.fileNamePrefix')

        if prefix == "" or prefix == None:
            prefix = self.GetStrippedSceneFileName()
        return prefix

    def GetCurrentRenderer(self):
        """Returns the current renderer."""
        renderer=str(pm.mel.currentRenderer())
        if renderer == "_3delight":
            renderer="3delight"
            
        return renderer

    def GetOutputPrefix(self,replaceFrameNumber, newFrameNumber, layerName, cameraName, renderElement):
        """Returns the output prefix as is shown in the Render Globals, except that the frame
        number is replaced with '?' padding.
        lobal proc string GetOutputPrefix( int $replaceFrameNumber, int $newFrameNumber )"""
        

        outputPrefix=""
        paddingString=""
        renderer=str(self.GetCurrentRenderer())
        renderableCameras= ",".join([i.name() for i in pm.ls(type="camera") if i.renderable.get()]) 
        multipleRenderableCams=(len(renderableCameras)>1)
        if renderer == "vray":
            pm.melGlobals.initVar('string[]', 'g_vrayImgExt')
            # Need to special case vray, because they like to do things differently.
            ext=""
            if pm.optionMenuGrp('vrayImageFormatMenu', exists=1):
                ext=str(pm.optionMenuGrp('vrayImageFormatMenu', q=1, v=1))
                
            
            else:
                ext=str(pm.getAttr('vraySettings.imageFormatStr'))
                
            if ext == "":
                ext="png"
                #for some reason this happens if you have not changed the format
                # VRay can append this to the end of the render settings display, but we don't want it in the file name.
                
            isMultichannelExr=int(False)
            multichannel=" (multichannel)"
            if ext.endswith(multichannel):
                ext=ext[0:-len(multichannel)]
                isMultichannelExr=int(True)
                
            versionString=str(pm.mel.vray('version'))
            version=2
            minorVersion=0
            if versionString != "":
                buffer = []
                buffer=versionString.split(".")
                version=int(int(buffer[0]))
                minorVersion=int(int(buffer[1]))
                
            prefix=str(pm.getAttr('vraySettings.fileNamePrefix'))
            # We need to use eval because the definition of vrayTransformFilename is different for
            # different versions of vray, and this is the only way to get around the "incorrect
            # number of arguments" error.
            separateFolders=int(pm.getAttr("vraySettings.relements_separateFolders"))
            separateRGBA=0
            if not pm.catch(lambda: pm.getAttr("vraySettings.relements_separateRGBA")):
                separateRGBA=int(pm.getAttr("vraySettings.relements_separateRGBA"))
                
            if prefix == "":
                prefix=str(pm.mel.GetStrippedSceneFileName())
                '''
                if( IsOldVray() )
                    $prefix = eval( "vrayTransformFilename( \"" + $prefix + "\", \"\" )" );
                else
                    $prefix = eval( "vrayTransformFilename( \"" + $prefix + "\", \"\", \"\" )" );
                '''
                
            if renderElement != "" and separateFolders:
                tempPrefix=str(pm.mel.dirname(prefix))
                if tempPrefix != "":
                    tempPrefix=tempPrefix + "/"
                    
                prefix=tempPrefix + renderElement + "/" + str(pm.mel.basename(prefix, ""))
                
            
            elif renderElement == "" and separateFolders and separateRGBA:
                tempPrefix=str(pm.mel.dirname(prefix))
                if tempPrefix != "":
                    tempPrefix=tempPrefix + "/"
                    
                prefix=tempPrefix + "rgba/" + str(pm.mel.basename(prefix, ""))
                
            if multipleRenderableCams and (pm.mel.match("<Camera>", prefix) == "") and (pm.mel.match("<camera>", prefix) == "") and (pm.mel.match("%c", prefix) == ""):
                prefix="<Camera>/" + prefix
                
            if pm.mel.IsRenderLayersOn() and (pm.mel.match("<Layer>", prefix) == "") and (pm.mel.match("<layer>", prefix) == "") and (pm.mel.match("%l", prefix) == ""):
                prefix="<Layer>/" + prefix
                
            if prefix != "":
                if not pm.catch(lambda: pm.mel.eval("vrayTransformFilename( \"\", \"\", \"\", 0, 0 )")):
                    sceneName=str(pm.mel.GetStrippedSceneFileName())
                    # Don't transform if the prefix is blank, so we can just default to the scene file name.
                    # Vray strips off all extensions in the scene name when replacing the <Scene> tag.
                    if version<3 or (version == 3 and minorVersion == 0):
                        sceneName=str(pm.mel.basenameEx(sceneName))
                        
                    prefix=str(pm.mel.eval("vrayTransformFilename( \"" + prefix + "\", \"" + cameraName + "\", \"" + sceneName + "\", 0, 0 )"))
                    
                
                elif not pm.catch(lambda: pm.mel.eval("vrayTransformFilename( \"\", \"\", \"\", 0 )")):
                    sceneName=str(pm.mel.GetStrippedSceneFileName())
                    # Vray strips off all extensions in the scene name when replacing the <Scene> tag.
                    if version<3 or (version == 3 and minorVersion == 0):
                        sceneName=str(pm.mel.basenameEx(sceneName))
                        
                    prefix=str(pm.mel.eval("vrayTransformFilename( \"" + prefix + "\", \"" + cameraName + "\", \"" + sceneName + "\", 0 )"))
                    
                
                elif not pm.catch(lambda: pm.mel.eval("vrayTransformFilename( \"\", \"\", \"\" )")):
                    prefix=str(pm.mel.eval("vrayTransformFilename( \"" + prefix + "\", \"\", \"\" )"))
                    
                
                elif not pm.catch(lambda: pm.mel.eval("vrayTransformFilename( \"\", \"\" )")):
                    prefix=str(pm.mel.eval("vrayTransformFilename( \"" + prefix + "\", \"\" )"))
                    
                
                else:
                    print "Could not evaluate output path using vrayTransformFilename, please contact Deadline support and include the version of vray you are using\n"
                    
                
            if renderElement != "" and isMultichannelExr == 0:
                prefix=prefix + str((pm.getAttr("vraySettings.fileNameRenderElementSeparator"))) + renderElement
                #if( catchQuiet( eval( "vrayTransformFilename( \"" + $prefix + "\", \"\", \"\" )" ) ) )
                #{
                #	if( catchQuiet( eval( "vrayTransformFilename( \"" + $prefix + "\", \"\" )" ) ) )
                #		$prefix = `getAttr vraySettings.fileNamePrefix`;
                #}
                #if( $prefix == "" )
                #	$prefix = GetStrippedSceneFileName();
                
            
            elif renderElement == "" and separateFolders and separateRGBA and isMultichannelExr == 0:
                prefix=prefix + str((pm.getAttr("vraySettings.fileNameRenderElementSeparator"))) + "rgba"
                
            if pm.mel.IsAnimatedOn():
                padding=4
                # Seems to be a bug where no matter what, VRay will use 4 digits for padding.
                # If ever fixed, try using the value from the vray settings.
                #int $padding = `getAttr vraySettings.fileNamePadding`;
                if version>=3:
                    padding=int(pm.getAttr('vraySettings.fileNamePadding'))
                    
                for i in range(0,padding):
                    paddingString=paddingString + "#"
                    # When rendering to a non-raw format, vray places a period before the padding, even though it
                    # doesn't show up in the render globals filename.
                    
                if ext == "vrimg" or (isMultichannelExr and version<3):
                    outputPrefix=prefix + paddingString + "." + ext
                    
                
                else:
                    outputPrefix=prefix + "." + paddingString + "." + ext
                    
                
            
            elif ext == "vrimg" or (isMultichannelExr and version<3):
                outputPrefix=prefix + "." + ext
                # When rendering to a non-raw format, vray places a period before the padding, even though it
                # doesn't show up in the render globals filename.
                
            
            else:
                outputPrefix=prefix + "." + ext
                
            
        
        else:
            paddingFound=0
            # Get the first output prefix.
            prefixString=""
            if renderer == "renderMan" or renderer == "renderManRIS":
                if cameraName == "":
                    pat=str(pm.mel.rmanGetImagenamePattern(1))
                    #$prefixString = `rmanGetImageName 1`;
                    ftext=str(pm.mel.rmanGetImageExt(""))
                    prefixString=str(pm.mel.rman("assetref", "-cls", "Final", "-assetnmpat", pat, "-ref", "$ASSETNAME", "-LAYER", layerName, "-EXT", ftext, "-DSPYID", "", "-DSPYCHAN", ""))
                    
                
                else:
                    cameraRelatives=pm.listRelatives(cameraName, s=1)
                    camera=cameraRelatives[0]
                    pat=str(pm.mel.rmanGetImagenamePattern(1))
                    ftext=str(pm.mel.rmanGetImageExt(""))
                    prefixString=str(pm.mel.rman("assetref", "-cls", "Final", "-assetnmpat", pat, "-ref", "$ASSETNAME", "-LAYER", layerName, "-CAMERA", camera, "-EXT", ftext, "-DSPYID", "", "-DSPYCHAN", ""))
                    
                
            
            elif renderer == "MayaKrakatoa":
                prefixes=pm.renderSettings(fin=1, cam=cameraName, lyr=layerName)
                #string $prefixes[] = `renderSettings -fin`;
                prefixString=prefixes[0]
                forceEXROutput=int(pm.getAttr("MayaKrakatoaRenderSettings.forceEXROutput"))
                if forceEXROutput == 1:
                    tokens = []
                    tokens=prefixString.split(".")
                    result=""
                    i = 0
                    for i in range(0,len(tokens) - 1):
                        result+=tokens[i] + "."
                        
                    prefixString=result + "exr"
                    
                
            
            else:
                currentPrefix=str(pm.getAttr('defaultRenderGlobals.imageFilePrefix'))
                newPrefix=currentPrefix
                if newPrefix == "":
                    newPrefix=str(pm.mel.GetStrippedSceneFileName())
                    
                if renderer == "arnold" and pm.mel.match("<RenderPass>", newPrefix) == "":
                    elements=pm.mel.getArnoldElementNames()
                    if elements[0] != "":
                        newPrefix="<RenderPass>/" + newPrefix
                        
                    
                if renderer == "mentalRay" and pm.mel.match("<RenderPass>", newPrefix) == "":
                    elements=pm.mel.getMentalRayElementNames(layerName)
                    if elements[0] != "":
                        newPrefix="<RenderPass>/" + newPrefix
                        
                    
                if multipleRenderableCams and (pm.mel.match("<Camera>", newPrefix) == "") and (pm.mel.match("%c", newPrefix) == ""):
                    newPrefix="<Camera>/" + newPrefix
                    
                if pm.mel.IsRenderLayersOn() and (pm.mel.match("<RenderLayer>", newPrefix) == "") and (pm.mel.match("<Layer>", newPrefix) == "") and (pm.mel.match("%l", newPrefix) == ""):
                    newPrefix="<RenderLayer>/" + newPrefix
                    
                pm.setAttr("defaultRenderGlobals.imageFilePrefix", newPrefix, type="string")
                #string $prefixes[] = `renderSettings -fin`;
                prefixes=pm.renderSettings(fin=1, cam=cameraName, lyr=layerName, cts=("RenderPass=" + renderElement))
                prefixString=prefixes[0]
                pm.setAttr("defaultRenderGlobals.imageFilePrefix", currentPrefix, type="string")
                
            prefixWithColons=""
            # Go through each letter of the prefix and create a new prefix with each letter
            # separated by colons, ie: f:i:l:e:n:a:m:e:.:e:x:t:
            for i in range(1,len(prefixString)+1):
                prefixWithColons+=prefixString[i-1:i] + ":"
                # Now split up the new prefix into an array, which removes all the colons and
                # places one letter in each index. Then count backwards and replace the first
                # group of numbers with the padding characters.
                
            prefix=prefixWithColons.split(":")
            if pm.mel.IsAnimatedOn():
                for i in range(len(prefix),0,-1):
                    if pm.mel.match("[0-9]", prefix[i]) != "":
                        prefix[i]="#"
                        paddingString=paddingString + "#"
                        paddingFound=1
                        
                    
                    elif paddingFound:
                        if prefix[i] == "-":
                            prefix[i]="#"
                            paddingString=paddingString + "#"
                            
                        break
                        
                    
                
            outputPrefix="".join(prefix)
            # Finally, convert the prefix array back to a string.
            if renderer == "maxwell" and renderElement != "":
                prefixParts=outputPrefix.split(".")
                numParts=len(prefixParts)
                mainPart=numParts - 2
                if pm.mel.IsAnimatedOn():
                    mainPart-=1
                    
                prefixParts[mainPart]=prefixParts[mainPart] + "_" + renderElement
                extNumber=0
                if renderElement == "zbuffer":
                    extNumber=int(pm.getAttr('maxwellRenderOptions.depthChannelFormat'))
                    
                
                elif renderElement == "object":
                    extNumber=int(pm.getAttr('maxwellRenderOptions.objIDChannelFormat'))
                    
                
                elif renderElement == "material":
                    extNumber=int(pm.getAttr('maxwellRenderOptions.matIDChannelFormat'))
                    
                
                elif renderElement == "motion":
                    extNumber=int(pm.getAttr('maxwellRenderOptions.motionVectorChannelFormat'))
                    
                
                elif renderElement.startswith("customAlpha_"):
                    extNumber=int(pm.getAttr('maxwellRenderOptions.customAlphaChannelFormat'))
                    
                
                else:
                    extNumber=int(pm.getAttr("maxwellRenderOptions." + renderElement + "ChannelFormat"))
                    
                prefixParts[numParts - 1]=str(pm.mel.getMaxwellChannelExtension(extNumber, True))
                outputPrefix=".".join(prefixParts)
                
            
            elif renderer == "maxwell":
                format=int(pm.getAttr('defaultRenderGlobals.imageFormat'))
                outputPrefix=outputPrefix[0:-3]
                outputPrefix=outputPrefix + str(pm.mel.getMaxwellChannelExtension(format, False))
                
            
        if pm.mel.IsAnimatedOn() and replaceFrameNumber:
            paddedFrame="" + str(newFrameNumber)
            while len(paddedFrame)<len(paddingString):
                paddedFrame="0" + paddedFrame
                
            
            outputPrefix=str(pm.mel.substituteAllString(outputPrefix, paddingString, paddedFrame))
            
        return outputPrefix

    def IsRenderLayersOn(self):
        """Returns if render layers is on."""
        

        renderLayers=pm.ls(exactType="renderLayer")
        referenceLayers=pm.ls(exactType="renderLayer", rn=1)
        return ((len(renderLayers) - len(referenceLayers))>1)
        
    def getRenderableRenderLayers(self,onlyReferenced):
        
        renderLayerList=pm.ls(exactType="renderLayer")
        # Loop through the render layer if the checkbox is on
        renderableLayers=[]
        for layer in renderLayerList:
            renderable=int(pm.getAttr(str(layer) + ".renderable"))
            # Only get output if the renderable attribute is on
            if renderable:
                isReferenceLayer=int(pm.referenceQuery(layer, inr=1))
                if isReferenceLayer and onlyReferenced:
                    renderableLayers.insert(0,layer)
                elif not isReferenceLayer and not onlyReferenced:
                    renderableLayers.insert(0,layer)

        return renderableLayers


    def load_plugins(self):
        try:
            render_node = pm.PyNode("defaultRenderGlobals")
            render_name = render_node.currentRenderer.get()
            if "pgYetiMaya" in self.plugins and "vrayformaya" in self.plugins:
                if render_name == "vray":
                    cmds.loadPlugin("pgYetiVRayMaya")
        except:
            pass

    def conduct_mel(self):
        # if "pgYetiMaya" in self.plugins and "vrayformaya" in self.plugins:
            # cmds.loadPlugin( "vrayformaya")
            # cmds.loadPlugin( "pgYetiVRayMaya")   
        render_node=pm.PyNode("defaultRenderGlobals")
        render_name = render_node.currentRenderer.get()
        yeti_load=cmds.pluginInfo("pgYetiMaya", query=True, loaded=True )
        self.mylog("the yeti load is %s " % yeti_load)
        yeti_vray_load=cmds.pluginInfo("pgYetiVRayMaya", query=True, loaded=True )
        self.mylog("the yeti_vray_load load is %s " % yeti_vray_load)
        shave_load=cmds.pluginInfo("shaveNode", query=True, loaded=True )
        self.mylog("the shave_load load is %s " % shave_load)
        glmCrowd_load =cmds.pluginInfo("glmCrowd", query=True, loaded=True )
        self.mylog("the glmCrowd load is %s " % glmCrowd_load)
        render_node.postMel.set(l=0)
        render_node.preRenderLayerMel.set(l=0)
        render_node.postRenderLayerMel.set(l=0)
        render_node.preRenderMel.set(l=0)
        render_node.postRenderMel.set(l=0)
        preMel = render_node.preMel.get()
        postMel = render_node.postMel.get()
        preRenderLayerMel = render_node.preRenderLayerMel.get()
        postRenderLayerMel = render_node.postRenderLayerMel.get()
        preRenderMel = render_node.preRenderMel.get()
        postRenderMel = render_node.postRenderMel.get()

        if render_name=="vray":
            if yeti_load and  yeti_vray_load and shave_load==False:
                mel.eval('pgYetiVRayPreRender;')
            if shave_load and yeti_load==False :
                mel.eval('shaveVrayPreRender;')
            if yeti_load and  yeti_vray_load and shave_load:
                mel.eval('shaveVrayPreRender;pgYetiVRayPreRender;')
            else:
                render_node.postMel.set("")
                render_node.preRenderLayerMel.set("")
                render_node.postRenderLayerMel.set("")
                render_node.preRenderMel.set("")
                render_node.postRenderMel.set("")
        elif render_name=="mentalRay":
            if shave_load:
                #render_name = render_node.currentRenderer.get()
                render_node.preRenderMel.set("shave_MRFrameStart;")
                render_node.postRenderMel.set("shave_MRFrameEnd;")
                #mel.eval('shave_MRFrameStart')
                #render_node.preRenderLayerMel.set('python \"mel.eval(\\"pgYetiVRayPreRender\\")\"')
            else:
                render_node.preRenderMel.set("")
                render_node.postRenderMel.set("")
        else:
            render_node.postMel.set("")
            render_node.preRenderLayerMel.set("")
            render_node.postRenderLayerMel.set("")
            render_node.preRenderMel.set("")
            render_node.postRenderMel.set("")

        if glmCrowd_load:
            mel.eval('glmRenderCallback("PreRender");')
            render_node.postMel.set('glmRenderCallback("PostRender");')
            render_node.preRenderLayerMel.set('glmRenderCallback("PreRenderLayer");')
            render_node.postRenderLayerMel.set('glmRenderCallback("PostRenderLayer");')
            render_node.preRenderMel.set('glmRenderCallback("PreRenderFrame");')
            render_node.postRenderMel.set('glmRenderCallback("PostRenderFrame");')
        self.log_scene('postMel', render_node.postMel.get())
        self.log_scene('preRenderLayerMel', render_node.preRenderLayerMel.get())
        self.log_scene('postRenderLayerMel', render_node.postRenderLayerMel.get())
        self.log_scene('preRenderMel', render_node.preRenderMel.get())
        self.log_scene('postRenderMel', render_node.postRenderMel.get())

        # if preMel:
        #     print preMel
        #     pmel = preMel
        #     pmel_list = pmel.split(';')
        #     for mels in pmel_list:
        #         if not mels == '':
        #             try:
        #                 mel.eval(mels)
        #
        #             except Exception as err:
        #
        #                 self.mylog('=== Error occur execute "%s"! ===\n=== Error Msg : %s ===' % (mels, err))

    def rd_path(self):
        rd_path = pm.PyNode("defaultRenderGlobals").imageFilePrefix.get()
        render_node=pm.PyNode("defaultRenderGlobals")
        render_name = render_node.currentRenderer.get()
        if render_name == "vray":
            rd_path = pm.PyNode("vraySettings").fnprx.get()
        rd_path = self.unicode_to_str(rd_path)
        self.log_scene("Current Outpu setting ",self.unicode_to_str(rd_path))
        if rd_path:
            rd_path=rd_path.replace('\\','/').replace('//','/')
            p1=re.compile(r"^\w:/?")
            p2=re.compile(r"^/*")
            p3=re.compile(r"[^\w///<>.% :]")
            p4=re.compile(r"//*")
            #print re.findall(p,rd_path)
            #p=re.compile("[.~!@#$%\^\+\*&/ \? \|:\.{}()<>';=\\"]")
            #print p.search(rd_path).group()
            #m=p.match(rd_path)
            rd_path=re.sub(p4,"/",rd_path)
            rd_path = re.sub(p1,"",rd_path)
            rd_path = re.sub(p2,"",rd_path)
            rd_path = re.sub(p3,"",rd_path)
            rd_path = re.sub(" ","_",rd_path)
            sceneName = os.path.splitext(os.path.basename(pm.system.sceneName()))[0].strip()
            if '<Scene>' in rd_path:
                rd_path = rd_path.replace('<Scene>', sceneName)
            if '%s' in rd_path:
                rd_path = rd_path.replace('%s', sceneName)
            if render_name == "vray":
                if '<RenderLayer>' in rd_path:
                    rd_path = rd_path.replace('<RenderLayer>','<Layer>')
                rd_path = pm.PyNode("vraySettings").fnprx.set(rd_path)
            else:
                pm.PyNode("defaultRenderGlobals").imageFilePrefix.set(rd_path)

            self.log_scene_set("Current Output setting ",self.unicode_to_str(rd_path))
        else:
            pass

    def write_pre_frame_ini(self):
        pm.lockNode('defaultRenderGlobals', lock=False)
        render_node = pm.PyNode("defaultRenderGlobals")
        render_name = render_node.currentRenderer.get()
        render_node.postMel.set(l=0)
        render_node.preRenderLayerMel.set(l=0)
        render_node.postRenderLayerMel.set(l=0)
        render_node.preRenderMel.set(l=0)
        render_node.postRenderMel.set(l=0)
        rd_path_old =  self.GetMayaOutputPrefix()

        current_frame = int(pm.currentTime())
        if current_frame >= 4:
            serial = current_frame
        else:
            serial = '0' * (5 - current_frame) + str(current_frame)
            rd_path_new = serial + "/" + rd_path_old

        if render_name == "vray":
            pm.PyNode("vraySettings").fnprx.set(rd_path_new)
        else:
            pm.PyNode("defaultRenderGlobals").imageFilePrefix.set(rd_path_new)

        str_mel = 'int $currTime = `currentTime -query`; \
                  global proc string GetStrippedSceneFileName() \
                  { string $fileName = `file - q - sceneName`; \
                  $fileName = `basename $fileName ".mb"`;\
                  $fileName = `basename $fileName ".ma"`; \
                  return $fileName;}; \
                  string $currentPrefix = `getAttr defaultRenderGlobals.imageFilePrefix`; \
                  string $newPrefix = $currentPrefix; \
                  if( $newPrefix == "" ){$newPrefix = GetStrippedSceneFileName();} \
                  string $str_time = $currTime; \
                  int $len_num = size($str_time); \
                  if( $len_num >= 4 ){$serial = $currTime;}; \
                  else{$serial = "0" * (4 - $len_num ) + $str_time;}; \
                  $newPrefix = $serial + "/" + $newPrefix; \
                  setAttr "defaultRenderGlobals.imageFilePrefix" -type "string" $newPrefix;'

        render_node.preRenderMel.set(str_mel)

    def write_post_frame_ini(self):
        pm.lockNode('defaultRenderGlobals', lock=False)

        render_node = pm.PyNode("defaultRenderGlobals")
        render_name = render_node.currentRenderer.get()

        render_node.postMel.set(l=0)
        render_node.preRenderLayerMel.set(l=0)
        render_node.postRenderLayerMel.set(l=0)
        render_node.preRenderMel.set(l=0)
        render_node.postRenderMel.set(l=0)

        preMel = render_node.preMel.get()
        postMel = render_node.postMel.get()
        preRenderLayerMel = render_node.preRenderLayerMel.get()
        postRenderLayerMel = render_node.postRenderLayerMel.get()
        preRenderMel = render_node.preRenderMel.get()
        postRenderMel = render_node.postRenderMel.get()

        # current_frame = int(pm.currentTime())
        # frame_out_ini = "[_____render end_____]"+ "[" + str(current_frame) + "]"
        # str_mel = "print '%s'" %frame_out_ini
        # render_node.postRenderMel.set(str_mel)
        # render_node.postRenderMel.set(postRenderMel+"python \"import sys;sys.path.append('c:/scrrpic\')import postmel; postmle.coy(loacoupt="",soutp=""")\"")

        # mel.eval('int $currTime = `currentTime -query`;string $str_mel = "[_____render end_____]"+ "[" + $currTime + "]";setAttr  defaultRenderGlobals.postRenderMel -type "string" $str_mel;')

        # str_mel = 'python (current_frame = int(pm.currentTime()); \
        #           frame_out_ini = "[_____render end_____]"+ "[" + str(current_frame) + "]" + "\n" \
        #           print frame_out_ini; )'




        str_mel = '''
        import maya.cmds as cmds 
        current_frame = int(cmds.currentTime( query=True ))      
        frame_out_ini = "[_____render end_____]"+ "[" + str(current_frame) + "]" + "\\n" 
        print frame_out_ini
        if len(str(current_frame)) >= 4:
            serial = current_frame
        else:
            serial = '0' * (5 - current_frame) + str(current_frame)
        output_frame = os.path.join(renderSettings["output"],serial).replace("\\\\","/")
    
        if not os.path.exists(output_frame):
            os.makedirs(output_frame)
    
        cmd = '{fcopy_path} /speed=full /cmd=move /force_close /no_confirm_stop /force_start "{source}" /to="{destination}"'.format(
            fcopy_path='c:\\fcopy\\FastCopy.exe',
            source=os.path.join(renderSettings["output"].replace('/', '\\\\')),
            destination=output_frame.replace('/', '\\\\'),
        )
        os.system(cmd)
        '''
        str_mel = 'python (current_frame = int(pm.currentTime()); \
                  frame_out_ini = "[_____render end_____]"+ "[" + str(current_frame) + "]" + "\n" \
                  print frame_out_ini; )'

        str_mel = 'int $currTime = `currentTime -query`;string $str_mel = "[_____render end_____]"+ "[" + $currTime + "]";print ($str_mel + "\\n");'
        print str_mel
        render_node.postRenderMel.set(str_mel)

    def copy_texture_to_out(self):
        str_mel = '''
        current_frame = int(pm.currentTime())
        if len(str(current_frame)) >= 4:
            serial = current_frame
        else:
            serial = '0' * (5 - current_frame) + str(current_frame)
        output_frame = os.path.join(renderSettings["output"],serial).replace("\\","/")
    
        if not os.path.exists(output_frame):
            os.makedirs(output_frame)
    
        cmd = '{fcopy_path} /speed=full /cmd=move /force_close /no_confirm_stop /force_start "{source}" /to="{destination}"'.format(
            fcopy_path='c:\\fcopy\\FastCopy.exe',
            source=os.path.join(renderSettings["output"].replace('/', '\\')),
            destination=output_frame.replace('/', '\\'),
        )
        os.system(cmd)
        '''


    def han_custome_prerender_bak(self):
        ########################### custom   self.start   here ########################################
        attr_list = [{"VRayMesh": "fileName"}, {"AlembicNode": "abc_File"}, {"pgYetiMaya": "groomFileName"},
                     {"pgYetiMaya": "cacheFileName"}, \
                     {"aiImage": "filename"}, {"RMSGeoLightBlocker": "Map"}, {"PxrStdEnvMapLight": "Map"},
                     {"PxrTexture": "filename"}, {"VRaySettingsNode": "imap_fileName2"}, \
                     {"VRaySettingsNode": "pmap_file2"}, {"VRaySettingsNode": "lc_fileName"},
                     {"VRaySettingsNode": "shr_file_name"}, {"VRaySettingsNode": "causticsFile2"}, \
                     {"VRaySettingsNode": "shr_file_name"}, {"VRaySettingsNode": "imap_fileName"},
                     {"VRaySettingsNode": "pmap_file"}, {"VRaySettingsNode": "fileName"}, \
                     {"VRaySettingsNode": "shr_file_name"}, {"VRayLightIESShape": "iesFile"},
                     {"diskCache": "cacheName"},
                     {"miDefaultOptions": "finalGatherFilename"}, \
                     {"RealflowMesh": "Path"}, {"aiStandIn": "dso"}, {"mip_binaryproxy": "object_filename"},
                     {"mentalrayLightProfile": "fileName"}, {"aiPhotometricLight": "ai_filename"}, \
                     {"VRayVolumeGrid": "inFile"}, {"file": "fileTextureName"}, {"RedshiftDomeLight": "tex0"},
                     {"RedshiftSprite": "tex0"}, {"ExocortexAlembicXform": "fileName"}, {"ffxDyna": "output_path"}, \
                     {"ffxDyna": "wavelet_output_path"}, {"ffxDyna": "postprocess_output_path"},
                     {"RedshiftIESLight": "profile"}, {"RedshiftDomeLight": "tex1"}, \
                     {"RedshiftEnvironment": "tex0"}, {"RedshiftEnvironment": "tex1"}, {"RedshiftEnvironment": "tex2"},
                     {"RedshiftEnvironment": "tex3"}, {"RedshiftEnvironment": "tex4"},
                     {"RedshiftLensDistortion": "LDimage"}, \
                     {"RedshiftLightGobo": "tex0"}, {"RedshiftNormalMap": "tex0"},
                     {"RedshiftOptions": "irradianceCacheFilename"}, {"RedshiftOptions": "photonFilename"},
                     {"RedshiftOptions": "irradiancePointCloudFilename"},
                     {"RedshiftOptions": "subsurfaceScatteringFilename"}, \
                     {"RedshiftProxyMesh": "fileName"}, {"RedshiftVolumeShape": "fileName"},
                     {"RedshiftBokeh": "dofBokehImage"},
                     {"RedshiftCameraMap": "tex0"}, {"RedshiftDisplacement": "texMap"}]
        # ,{"houdiniAsset":"otlFilePath"}]

        if self.user_id in [962413]:
            for i in pm.ls(type="aiStandIn"):
                i.deferStandinLoad.set(0)
                print "set %s to 0" % (i.deferStandinLoad)

        if self.user_id in [1875817]:
            for i in pm.ls(type="aiAOVDriver"):
                if i.hasAttr("mergeAOVs"):
                    i.mergeAOVs.set(1)
                    print "set mergeAOVs to 1"

        if self.user_id in [1812756]:
            for i in pm.ls(type="aiStandIn"):
                i.deferStandinLoad.set(0)
                print "set %s to 0" % (i.deferStandinLoad)

        if self.user_id in [963909]:
            mel.eval('setUpAxis \"z\";')
            print self.start
            # if self.start:
            # cmds.currentTime(int(self.start),edit=True)
        if self.user_id in [1841452]:
            print "set vray srdml "
            for i in pm.ls(type="VRaySettingsNode"):
                if i.hasAttr("srdml"):
                    i.srdml.set(0)
                    print "set vray srdml 0"

        if self.user_id in [1857270]:
            print "set vray srdml "
            for i in pm.ls(type="VRaySettingsNode"):
                if i.hasAttr("srdml"):
                    i.srdml.set(10000)
                    print "set vray srdml 10000"

        if self.user_id in [1881384]:
            print "set vray srdml "
            for i in pm.ls(type="VRaySettingsNode"):
                if i.hasAttr("srdml"):
                    i.srdml.set(30000)
                    print "set vray srdml 30000"

        if self.user_id in [1017637]:
            print self.plugins
            print "+++++++++++++++++++++++mapping+++++++++++++++++++++++"
            print self.mapping
            print "rendersetting"
            print self.rendersetting
            print "+++++++++++++++++++++++mapping+++++++++++++++++++++++"
            print self.user_id
            maya_proj_path = cmds.workspace(q=True, fullName=True)
            source_path = "%s/sourceimages" % (maya_proj_path)
            rep_path = ""
            search = ""
            dicts = {}
            if search:
                dicts = self.file_dicts(search)
            for attr_dict in self.attr_list:
                for node_type in attr_dict:
                    attr_name = attr_dict[node_type]
                    self.change_path(node_type, attr_name, self.mapping, rep_path, dicts)
            # replace_path("pgYetiMaya", "cacheFileName","//192.168.80.223/MayaFiles/TYBL/SC01/sh06/xiecm/TYBL_SC01_sh06","X:")
            # replace_path("pgYetiMaya", "cacheFileName","E:/work/TYBL/Project","X:")
            self.change_path_mapping("pgYetiMaya", "cacheFileName", self.mapping)
            if "pgYetiMaya" not in self.plugins or "vrayformaya" not in self.plugins:
                self.render_node.postMel.set("")
            self.set_yeti_imageSearchPath(self.mapping)
            self.del_node('SGFC_sc05_sh01_ly_yong:SGFC_ch010001SwimsuitGirl_l_msAnim:Facial_PanelShape')
            self.del_node(
                'SGFC_sc08_sh01_0810:_1:che:SGFC_sc08_sh01_JingCha_037:SGFC_ch008001Policeman1_h_msAnim:Facial_PanelShape')
            self.del_node(
                'SGFC_sc08_sh01_0810:_1:che:SGFC_sc08_sh01_JingCha_038:SGFC_ch008001Policeman1_h_msAnim:Facial_PanelShape')
            self.del_node("SGFC_ch008001Policeman1_h_msAnim:Facial_PanelShape")
            self.del_node("ch:Facial_Panel_MD_19432Shape")
            self.del_node("ch:Facial_Panel_MD_19431Shape")
            self.del_node("aiAreaLightShape1309")
            self.del_node("Facial_PanelShape")
            self.del_node("ch:Facial_Panel_MD_19433")
            self.del_node("Policeman16:Facial_PanelShape")
            self.del_node("Policeman17:Facial_PanelShape")
            self.del_node("Policeman16:Facial_PanelShape")
            self.del_node("Policeman16:Facial_PanelShape")
            self.del_node("Policeman16:Facial_PanelShape")
            self.del_node("Policeman16:Facial_PanelShape")
            self.del_node("Policeman16:Facial_PanelShape")
            self.del_node("ch:Facial_Panel_MD_19433Shape")
            self.del_node(
                "SGFC_sc08_sh01_0810:_1:che:SGFC_sc08_sh01_JingCha_040:SGFC_ch008001Policeman1_h_msAnim:Facial_PanelShape")
            self.del_node(
                "SGFC_sc08_sh01_0810:_1:che:SGFC_sc08_sh01_JingCha_039:SGFC_ch008001Policeman1_h_msAnim:Facial_PanelShape")
            self.del_node("SGFC_sc08_sh01_0810:_1:dongbujuese_002:ch012001Policeman:Facial_PanelShape")
            self.del_node("SGFC_sc08_sh01_0810:_1:dongbujuese_002:ch012001Policeman3:Facial_PanelShape")
            self.del_node("SGFC_sc08_sh01_0810:_1:dongbujuese_002:jc1:ch012001Policeman6:Facial_PanelShape")
            self.del_node("SGFC_sc08_sh01_0810:_1:dongbujuese_002:jc1:ch012001Policeman7:Facial_PanelShape")
            self.del_node("SGFC_sc08_sh01_0810:_1:dongbujuese_002:jc3:ch012001Policeman9:Facial_PanelShape")
            self.del_node(
                "SGFC_sc08_sh01_0810:_1:dongbujuese_002:jincha:SGFC_sc028_sh01_an_DBjuese:ch008001Policeman1:Facial_PanelShape")
            self.del_node("SGFC_sc08_sh01_0810:_1:dongbujuese_002:jc3:ch012001Policeman9:Facial_PanelShape")
            self.del_node("SGFC_sc08_sh01_0810:_1:dongbujuese_002:jc3:ch012001Policeman9:Facial_PanelShape")
            self.del_node("SGFC_sc08_sh01_0810:_1:dongbujuese_002:jc3:ch012001Policeman9:Facial_PanelShape")
            self.del_node("SGFC_sc05_sh01_ly_yong5:SGFC_ch010001SwimsuitGirl_l_msAnim:Facial_PanelShape")
            self.del_node("Facial_Panel_MD_4771Shape")

            self.del_node("aiAreaLightShape1309")
            for i in pm.ls(type="aiStandIn"):
                i.deferStandinLoad.set(0)
                print "set %s to 0" % (i.deferStandinLoad)

            for i in pm.ls(type="VRaySettingsNode"):
                if i.hasAttr("imap_multipass"):
                    if self.task_id in [9350799]:
                        i.attr('imap_multipass').set(0)
                        print "set imap_multipass to false"

                if i.hasAttr("srdml"):
                    # dml = 48000
                    dml = i.srdml.get()
                    print "the scene vray srdml %s MB" % (dml)
                    if self.task_id in [9350799]:
                        print self.task_id
                        i.srdml.set(20000)
                        print "change vray srdml to  %s MB" % (i.srdml.get())
                if self.rendersetting:
                    if 'width' in self.rendersetting and i.hasAttr("width"):
                        i.width.set(int(self.rendersetting['width']))
                    if 'height' in self.rendersetting and i.hasAttr("height"):
                        i.height.set(int(self.rendersetting['height']))
                    cams = self.rendersetting['renderableCamera']
                    self.del_cam(cams)
                if i.hasAttr("sys_distributed_rendering_on"):
                    i.sys_distributed_rendering_on.set(False)
                if i.hasAttr("globopt_gi_dontRenderImage"):
                    i.globopt_gi_dontRenderImage.set(False)
                    # all_image = cmds.ls(exactType ="cacheFile")
                    # if len(all_image) != 0:
                    # for a in all_image:
                    # b = cmds.getAttr(a+".cacheName")
                    # c = cmds.getAttr(a+".cachePath")
                    # print (c+"/"+b+".xml")
                    # cmds.setAttr((a+".cachePath"),r"X:/data",type="string")

            for i in pm.ls(type="aiOptions"):
                # print "defaultArnoldRenderOptions.abortOnError 0"
                # i.abortOnError.set(1)
                i.log_verbosity.set(1)
                if i.hasAttr("autotx"):
                    i.autotx.set(False)
                if i.hasAttr("textureMaxMemoryMB"):
                    i.textureMaxMemoryMB.set(40960)
                i.absoluteTexturePaths.set(0)
                i.absoluteProceduralPaths.set(0)

                print 'setAttr "defaultArnoldRenderOptions.absoluteTexturePaths" 0;'
                # setAttr "defaultArnoldRenderOptions.absoluteProceduralPaths" 0;
                # i.procedural_searchpath.set(r"N:\cg_custom_setup\network\arnold\htoa-1.11.1_r1692_houdini-15.0.393_windows\arnold\procedurals")

                i.shader_searchpath.set(source_path)
                i.texture_searchpath.set(source_path)
                # setAttr -type "string" defaultArnoldRenderOptions.procedural_searchpath ;

            print("PRE Times move time slider")
            if self.start:
                cmds.currentTime(int(self.start + 1), edit=True)
                cmds.currentTime(int(self.start), edit=True)
                print "update frame"

        if self.user_id in [964137, 1868562]:
            print "set vray srdml "
            for i in pm.ls(type="VRaySettingsNode"):
                if i.hasAttr("srdml"):
                    i.srdml.set(0)
                    print "set vray srdml 0"
                if 'width' in self.rendersetting and i.hasAttr("width"):
                    i.width.set(self.rendersetting['width'])
                if 'height' in self.rendersetting and i.hasAttr("height"):
                    i.height.set(self.rendersetting['height'])
                print "Reset your Vray rendering resolution attribute according your setting on the client"
            for i in pm.ls(type="resolution"):
                if 'width' in self.rendersetting and i.hasAttr("width"):
                    i.width.set(int(self.rendersetting['width']))
                if 'height' in self.rendersetting and i.hasAttr("height"):
                    i.height.set(int(self.rendersetting['height']))
                print "Reset your scene resolution attribute according your setting on the client"
        if self.user_id in [1858676, 1858472]:
            for i in pm.ls(type="aiOptions"):
                print "defaultArnoldRenderOptions.abortOnError 0"
                i.abortOnError.set(0)
                if i.hasAttr("log_verbosity"):
                    i.log_verbosity.set(1)
                if i.hasAttr("autotx"):
                    i.autotx.set(False)
                if i.hasAttr("textureMaxMemoryMB"):
                    i.textureMaxMemoryMB.set(20480)
                    # i.absoluteTexturePaths.set(0)
                    # i.absoluteProceduralPaths.set(0)
                    # print 'setAttr "defaultArnoldRenderOptions.absoluteTexturePaths" 0;'
            for i in pm.ls(type="VRaySettingsNode"):
                if i.hasAttr("srdml"):
                    i.srdml.set(0)
                    print "set vray srdml 0"
        if self.user_id in [1872869]:
            for i in pm.ls(type="aiOptions"):
                # print "defaultArnoldRenderOptions.abortOnError 0"
                # i.abortOnError.set(1)
                if i.hasAttr("log_verbosity"):
                    i.log_verbosity.set(1)
                if i.hasAttr("autotx"):
                    i.autotx.set(False)
                if i.hasAttr("textureMaxMemoryMB"):
                    i.textureMaxMemoryMB.set(10240)
                    print "set textureMaxMemoryMB 1024MB"
        if self.user_id in [1852297]:
            for i in pm.ls(type="aiOptions"):
                print "defaultArnoldRenderOptions.abortOnError 0"
                i.abortOnError.set(0)
                if i.hasAttr("log_verbosity"):
                    i.log_verbosity.set(1)
                if i.hasAttr("autotx"):
                    i.autotx.set(False)
                if i.hasAttr("textureMaxMemoryMB"):
                    i.textureMaxMemoryMB.set(10240)
                    print "set textureMaxMemoryMB 1024MB"
            print "set vray srdml "
            for i in pm.ls(type="VRaySettingsNode"):
                if i.hasAttr("srdml"):
                    i.srdml.set(0)
                    print "set vray srdml 0"

        if self.user_id in [1844577]:
            for i in pm.ls(type="aiOptions"):
                print "defaultArnoldRenderOptions.abortOnError 0"
                i.abortOnError.set(0)
            for i in pm.ls(type="aiStandIn"):
                i.deferStandinLoad.set(0)
                print "set %s to 0" % (i.deferStandinLoad)
            for i in pm.ls(type="pgYetiMaya"):
                if i.hasAttr("aiLoadAtInit"):
                    i.aiLoadAtInit.set(1)

    def main(self):
        self.get_scene_info()
        self.reset_scene_info()
        self.get_image_namespace()
        self.rd_path()
        self.load_plugins()
        self.conduct_mel()
        self.han_custome_prerender_bak()
        self.han_custome_prerender()


if __name__ == '__main__':
    print '\n\n-------------------------------------------------------[PreRender]start----------------------------------------------------------\n\n'
    premel_start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print "[Prerender start]----%s \n" % premel_start_time
    beginTime = datetime.datetime.now()
    config = PreRender(pre_render_dict)
    config.main()
    endTime = datetime.datetime.now()
    timeOut = endTime - beginTime
    print "[Prerender time]----%s" % (str(timeOut))
    print '\n\n-------------------------------------------------------[PreRender]end----------------------------------------------------------\n\n'
