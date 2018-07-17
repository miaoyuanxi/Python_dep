#!/usr/bin/env python
#encoding:utf-8
# -*- coding: utf-8 -*-

import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import os,sys,re
print "+++++++++++++++++++++++++++++++++the prerender strat++++++++++++++++++++++++++++++++++++++++++++++++"
maya_proj_paht = cmds.workspace(q=True, fullName=True)
source_path = "%s/sourceimages" % (maya_proj_paht)
scenes_path = "%s/scenes" % (maya_proj_paht)
render_node = pm.PyNode("defaultRenderGlobals")
yeti_load = cmds.pluginInfo("pgYetiMaya", query=True, loaded=True )
yeti_vray_load = cmds.pluginInfo("pgYetiVRayMaya", query=True, loaded=True )
shave_load = cmds.pluginInfo("shaveNode", query=True, loaded=True )
# if not cmds.pluginInfo( 'xgenToolkit', query=True, loaded=True ):
    # cmds.loadPlugin('xgenToolkit')
    # print ("Load xgenToolkit ")
rep_path = ""
search = ""
dicts = {}



def rd_path():
    
    rd_path = pm.PyNode("defaultRenderGlobals").imageFilePrefix.get()
    render_node=pm.PyNode("defaultRenderGlobals")
    render_name = render_node.currentRenderer.get()
    if render_name == "vray":
        rd_path = pm.PyNode("vraySettings").fnprx.get()
    print rd_path
    if rd_path is not None:
        print "change output path"
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
        print rd_path
        rd_path = re.sub(p1,"",rd_path)
        print rd_path
        rd_path = re.sub(p2,"",rd_path)
        print rd_path
        rd_path = re.sub(p3,"",rd_path)
        rd_path = re.sub(" ","_",rd_path)
        print rd_path
        sceneName = os.path.splitext(os.path.basename(pm.system.sceneName()))[0].strip()
        if '<Scene>' in rd_path:
            rd_path = rd_path.replace('<Scene>', sceneName)
        if '%s' in rd_path:
            rd_path = rd_path.replace('%s', sceneName)
        print "the output is %s " % rd_path
        pm.PyNode("defaultRenderGlobals").imageFilePrefix.set(rd_path)
        if render_name == "vray":
            rd_path = pm.PyNode("vraySettings").fnprx.set(rd_path)
    else:
        pass

def change_path(node_type, attr_name, mapping, rep_path,dicts):
    print "the  node type  is %s" % (node_type)    
    maya_proj_paht = cmds.workspace(q=True, fullName=True)
    source_path = "%s/sourceimages" % (maya_proj_paht)
    scenes_path = "%s/scenes" % (maya_proj_paht)
    data_path = "%s/data" % (maya_proj_paht)
    all_node = pm.ls(type=node_type)
    if len(all_node) != 0:
        for node in all_node:
            if node.hasAttr(attr_name):
                #file_path = cmds.getAttr(node + "."+attr_name)
                refcheck = pm.referenceQuery(node, inr = True)
                #print "refcheck %s " % (refcheck)
                if (refcheck == False):
                    try:              
                        node.attr(attr_name).set(l=0)
                    except Exception,error:
                        print Exception,":",error
                        pass
                file_path = node.attr(attr_name).get()
                if file_path != None and file_path.strip() !="" :
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
                        if os.path.exists(file_path_new) == 0 and dicts :
                            if asset_name in dicts:
                                file_path_new = dicts[asset_name]
                        
                        if os.path.exists(file_path_new) == 0:
                            print "the %s node %s  %s is not find ::: %s " % (node_type,node,attr_name,file_path)
                        else:
                            cmds.setAttr((node + "." + attr_name), file_path_new, type="string")
def change_path_mapping(node_type, attr_name, mapping):
    print "the  node type  is %s" % (node_type)    
    maya_proj_paht = cmds.workspace(q=True, fullName=True)
    source_path = "%s/sourceimages" % (maya_proj_paht)
    scenes_path = "%s/scenes" % (maya_proj_paht)
    data_path = "%s/data" % (maya_proj_paht)
    all_node = pm.ls(type=node_type)
    if len(all_node) != 0:
        for node in all_node:
            if node.hasAttr(attr_name):
                #file_path = cmds.getAttr(node + "."+attr_name)
                refcheck = pm.referenceQuery(node, inr = True)
                
                if (refcheck == False):
                    try:              
                        node.attr(attr_name).set(l=0)
                    except Exception,error:
                        print Exception,":",error
                        pass
                file_path = node.attr(attr_name).get()
                if file_path != None and file_path.strip() !="" :
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
def replace_path(node_type, attr_name,rep_path,repath_new):
    maya_proj_paht = cmds.workspace(q=True, fullName=True)
    source_path = "%s/sourceimages" % (maya_proj_paht)
    scenes_path = "%s/scenes" % (maya_proj_paht)
    data_path = "%s/data" % (maya_proj_paht)
    all_node = pm.ls(type=node_type)
    if all_node:
        for node in all_node:
            #file_path = cmds.getAttr(node + "."+attr_name)
            refcheck = pm.referenceQuery(node, inr = True)
            if (refcheck == False):                
                node.attr(attr_name).set(l=0)
            file_path = node.attr(attr_name).get()
            print file_path
            if file_path != None and file_path.strip() !="" :
                file_path_new = file_path.replace(rep_path, repath_new)
                print file_path_new
                cmds.setAttr((node + "." + attr_name), file_path_new, type="string")
                print "%s %s %s " % (node,attr_name,file_path_new)
                
def file_dicts(search):
    dicts = {}
    for parents, dirnames, filenames in os.walk(search):
        for filename in filenames:
            dicts[filename] = os.path.join(parents, filename)
    return dicts

def rep_path_def(mapping,old_path):
    if mapping:
        file_path_new=old_path
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
def get_graph_path(node):
    return cmds.getAttr(node+'.cacheFileName')
def set_graph_path(node, path):
    cmds.setAttr(node+'.cacheFileName', path)
def get_texture_node(graph_node):
    mel_cmd = 'pgYetiGraph -listNodes -type "texture" %s' % str(graph_node)
    texture_nodes = mel.eval(mel_cmd)
    return texture_nodes

def get_texture_path(texture, graph):
    mel_cmd = 'pgYetiGraph -node "%s" -param "file_name" -getParamValue %s' %(str(texture), str(graph))
    path = mel.eval(mel_cmd)
    return path
    
def set_texture_path(path, node, graph):
    mel_cmd = 'pgYetiGraph -node "{node_name}" -param "file_name" -setParamValueString {path}  {graph}'\
    .format(node_name=str(node), path=str(path), graph=str(graph))
    print mel_cmd

def set_yeti_imageSearchPath(mapping):   
    all_yeti_nodes = cmds.ls(type='pgYetiMaya')
    if len(all_yeti_nodes) != 0:
        for node_name in all_yeti_nodes:
            #cache = get_graph_path(node_name)
            tnodes = get_texture_node(node_name)
            yeti_dict={}
            yeti_texs=[] 
            #print node_name
            if tnodes != None:
                if len(tnodes) != 0:
                    for tx_node in tnodes:
                        texs = get_texture_path(tx_node, node_name)
                        texs = texs.replace('\\', '/')
                        texs = texs.replace('<udim>', '1001')
                        texs = texs.replace('<UDIM>', '1001')
                        if os.path.exists(texs) == 0 and texs != "" and texs != None :
                            tex_new_path = rep_path_def(mapping,texs)
                            #print tex_new_path
                            if os.path.exists(tex_new_path) == 0:
                                print "the %s node %s   is not find :: %s" % (node_name,tx_node,texs)

                            
                            yeti_texs.append(os.path.dirname(tex_new_path) )
                             
                    cmds.setAttr(node_name+".imageSearchPath",l=0)
                    yeti_searchpath = ";".join(yeti_texs)
                    cmds.setAttr(node_name+".imageSearchPath",yeti_searchpath ,type='string')
   
    
def pre_layer_mel():
    print '++++++++++++++++++pre_layer_mel +++++++++++++++++++++++++++++'
    # if "pgYetiMaya" in plugins and "vrayformaya" in plugins:
        # cmds.loadPlugin( "vrayformaya")
        # cmds.loadPlugin( "pgYetiVRayMaya")   
    render_node=pm.PyNode("defaultRenderGlobals")
    render_name = render_node.currentRenderer.get()
    yeti_load=cmds.pluginInfo("pgYetiMaya", query=True, loaded=True )
    print "the yeti load is %s " % yeti_load
    yeti_vray_load=cmds.pluginInfo("pgYetiVRayMaya", query=True, loaded=True )
    print "the yeti_vray_load load is %s " % yeti_vray_load
    shave_load=cmds.pluginInfo("shaveNode", query=True, loaded=True )
    print "the shave_load load is %s " % shave_load
    pm.lockNode( 'defaultRenderGlobals', lock=False )
    render_node.postMel.set(l=0)
    render_node.preRenderLayerMel.set(l=0)
    render_node.postRenderLayerMel.set(l=0)
    render_node.preRenderMel.set(l=0)
    render_node.postRenderMel.set(l=0)
    
    if render_name=="vray":
        print "++++++++++++++++ the renderer is vray+++++++++++++++++++++"
        if yeti_load and  yeti_vray_load and shave_load==False:
            mel.eval('pgYetiVRayPreRender;')
            #render_node.postMel.set("pgYetiVRayPostRende;")
            print render_node.postMel.get()
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
        print "++++++++++++++++ the renderer is mentalRay++++++++++++++++++"
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
        print "++++++++++++++++ the renderer isnot vray mentalRay+++++++++++++++++++++++++"
        render_node.postMel.set("")
        render_node.preRenderLayerMel.set("")
        render_node.postRenderLayerMel.set("")
        render_node.preRenderMel.set("")
        render_node.postRenderMel.set("")
def del_node(node_name):     
    if pm.objExists(node_name):
        try:
            
            tran = pm.listTransforms(node_name)
             
            for a in tran:
                
                pm.delete(a) 
                print "the %s is del " % (a) 
        except:
            print "the %s dont del " % (node_name) 
            pass 

def set_cam_render(cams):
    print "multiple cams to cmd"
    cams_list = cams.split(',')
    
    cams_all = pm.ls(type='camera')
    for cam in cams_all:
        mel.eval('removeRenderLayerAdjustmentAndUnlock("%s.renderable")' % cam)
        if cam not in cams_list:
            cmds.setAttr(cam + ".renderable", 0)
        else:
            cmds.setAttr(cam + ".renderable", 1)

def del_cam(cams):
    print "multiple cams to cmd"
    cams_all = pm.ls(type='camera')
    if cams:
        cams_list = cams.split(',')    
    
        for cam in cams_all:
            mel.eval('removeRenderLayerAdjustmentAndUnlock("%s.renderable")' % cam)
            if cam not in cams_list:
                try:                    
                    del_node(cam)
                    
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
                    del_node(cam)
                    
                except:
                    print "the %s dont del " % (cam) 
                    pass 
            else:
                print "the cam %s is render" % (cam)
def set_layer_render(layers):
    print "multiple render layer to cmd"
    layers_list = layers.split(',')
    
    layers_all = cmds.listConnections("renderLayerManager.renderLayerId")
    for layer in layers_all:
        mel.eval('removeRenderLayerAdjustmentAndUnlock("%s.renderable")' % layer)
        if layer not in layers_list:
            cmds.setAttr(layer + ".renderable", 0)
        else:
            cmds.setAttr(layer + ".renderable", 1)
if user_id not in  [964309]:         
    pre_layer_mel()
if rendersetting:
    if 'renderableLayer' in rendersetting :
        if "," in rendersetting['renderableLayer']:
            set_layer_render(rendersetting['renderableLayer'])

attr_list = [{"VRayMesh": "fileName"}, {"AlembicNode": "abc_File"},{"pgYetiMaya": "groomFileName"},{"pgYetiMaya": "cacheFileName"},\
            {"aiImage": "filename"},{"RMSGeoLightBlocker": "Map"},{"PxrStdEnvMapLight": "Map"},{"VRaySettingsNode": "imap_fileName2"},\
            {"VRaySettingsNode": "pmap_file2"},{"VRaySettingsNode": "lc_fileName"},{"VRaySettingsNode": "shr_file_name"},{"VRaySettingsNode": "causticsFile2"},\
            {"VRaySettingsNode": "shr_file_name"},{"VRaySettingsNode": "imap_fileName"},{"VRaySettingsNode": "pmap_file"},{"VRaySettingsNode": "fileName"},\
            {"VRaySettingsNode": "shr_file_name"},{"VRayLightIESShape": "iesFile"},{"diskCache": "cacheName"},{"miDefaultOptions": "finalGatherFilename"},\
            {"RealflowMesh": "Path"},{"aiStandIn": "dso"},{"mip_binaryproxy": "object_filename"},{"mentalrayLightProfile": "fileName"},{"aiPhotometricLight": "ai_filename"},\
            {"VRayVolumeGrid": "inFile"},{"file":"fileTextureName"},{"RedshiftDomeLight":"tex0"},{"RedshiftSprite":"tex0"},{"ExocortexAlembicXform":"fileName"},{"ffxDyna":"output_path"},\
            {"ffxDyna":"wavelet_output_path"},{"ffxDyna":"postprocess_output_path"},{"RedshiftIESLight":"profile"},{"RedshiftDomeLight":"tex1"},\
            {"RedshiftEnvironment":"tex0"},{"RedshiftEnvironment":"tex1"},{"RedshiftEnvironment":"tex2"},{"RedshiftEnvironment":"tex3"},{"RedshiftEnvironment":"tex4"},{"RedshiftLensDistortion":"LDimage"},\
            {"RedshiftLightGobo":"tex0"},{"RedshiftNormalMap":"tex0"},{"RedshiftOptions":"irradianceCacheFilename"},{"RedshiftOptions":"photonFilename"}, {"RedshiftOptions":"irradiancePointCloudFilename"},{"RedshiftOptions":"subsurfaceScatteringFilename"},\
            {"RedshiftProxyMesh":"fileName"},{"RedshiftVolumeShape":"fileName"},{"RedshiftBokeh":"dofBokehImage"},{"RedshiftCameraMap":"tex0"},{"RedshiftDisplacement":"texMap"}]
            #,{"houdiniAsset":"otlFilePath"}]    

           
if user_id in [1850226]:
    print start
    if start:
        cmds.currentTime(int(start),edit=True)
if user_id in [1864685]:
    mel.eval("delete `ls -type unknown`")
if user_id in [1852657]:
    mel.eval('source "C:/Program Files/Domemaster3D/maya/common/scripts/domeRender.mel"; domemaster3DPreRenderMEL();')
if user_id in [962413,1844068]:
    for i in pm.ls(type="aiStandIn"):
        i.deferStandinLoad.set(0)
        print "set %s to 0" % (i.deferStandinLoad) 

print user_id
if user_id in [1818411]:
    for i in pm.ls(type="aiStandIn"):
        i.deferStandinLoad.set(0)
        print "set %s to 0" % (i.deferStandinLoad)
if user_id in [963567]:
    print plugins
    print "+++++++++++++++++++++++mapping+++++++++++++++++++++++"
    print mapping
    print "rendersetting"
    print rendersetting
    print "+++++++++++++++++++++++mapping+++++++++++++++++++++++"
    print user_id

    rep_path =""
    search=""
    dicts={}
    if search:
        dicts=file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            change_path(node_type, attr_name, mapping, rep_path,dicts)
if user_id in [1017637]:

    print plugins
    print "+++++++++++++++++++++++mapping+++++++++++++++++++++++"
    print mapping
    print "rendersetting"
    print rendersetting
    print "+++++++++++++++++++++++mapping+++++++++++++++++++++++"
    print user_id

    rep_path =""
    search=""
    dicts={}
    if search:
        dicts=file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            change_path(node_type, attr_name, mapping, rep_path,dicts)
                            
    if "pgYetiMaya" not in plugins or "vrayformaya" not in plugins:
        render_node.postMel.set("")

    del_node('SGFC_sc05_sh01_ly_yong:SGFC_ch010001SwimsuitGirl_l_msAnim:Facial_PanelShape')
    del_node("SGFC_ch008001Policeman1_h_msAnim:Facial_PanelShape")
    del_node("aiAreaLightShape1309")
    del_node("Facial_PanelShape")
    
    del_node("aiAreaLightShape1309")
    for i in pm.ls(type="aiStandIn"):
        i.deferStandinLoad.set(0)
        print "set %s to 0" % (i.deferStandinLoad)  

    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("imap_multipass"):
            if taskid in [9350799]:
                i.attr('imap_multipass').set(0)
                print "set imap_multipass to false" 

                
        
        if i.hasAttr("srdml"):
            #dml = 48000
            dml =i.srdml.get()
            print "the scene vray srdml %s MB" %(dml)
            if taskid in [9350799]:
                print taskid
                i.srdml.set(20000)
                print "change vray srdml to  %s MB" %(i.srdml.get())
        if rendersetting:
            if 'width' in rendersetting and i.hasAttr("width") :
                i.width.set(rendersetting['width'])
            if 'height' in rendersetting and i.hasAttr("height") :
                i.height.set(rendersetting['height'])            

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
        print "defaultArnoldRenderOptions.abortOnError 0"
        i.abortOnError.set(1)
        i.log_verbosity.set(0)
        if i.hasAttr("autotx"):
            i.autotx.set(False)
        if i.hasAttr("textureMaxMemoryMB"):
            i.textureMaxMemoryMB.set(10240)
        i.absoluteTexturePaths.set(0)
        i.absoluteProceduralPaths.set(0)
        
        print 'setAttr "defaultArnoldRenderOptions.absoluteTexturePaths" 0;'
        #setAttr "defaultArnoldRenderOptions.absoluteProceduralPaths" 0;
        #i.procedural_searchpath.set(r"N:\cg_custom_setup\network\arnold\htoa-1.11.1_r1692_houdini-15.0.393_windows\arnold\procedurals")
        
        i.shader_searchpath.set(source_path)
        i.texture_searchpath.set(source_path)
        #setAttr -type "string" defaultArnoldRenderOptions.procedural_searchpath ;
# if user_id in [1873149]:
    # refs = pm.listReferences()
    # for ref in refs:
        # if ref.isLoaded():
            # print ref
            # ref.importContents()
        # else:
            # print ref
    # change_path_mapping("AlembicNode", "abc_File",mapping)
    # cmds.refresh()
    
        
        
# if user_id in [1840038]:
    # for i in pm.ls(type="aiOptions"):
        # print "defaultArnoldRenderOptions.abortOnError 0"
        # i.abortOnError.set(1)
        # i.log_verbosity.set(1)
        # if i.hasAttr("autotx"):
            # i.autotx.set(False)
        # if i.hasAttr("textureMaxMemoryMB"):
            # i.textureMaxMemoryMB.set(40960)
        # i.absoluteTexturePaths.set(0)
        # i.absoluteProceduralPaths.set(0)
        # print 'setAttr "defaultArnoldRenderOptions.absoluteTexturePaths" 0;'
    # mel.eval("putenv(\"MAYA_DISABLE_BATCH_RUNUP\",\"1\"); global proc dynRunupForBatchRender() {}; ") 
if user_id in [1840793]:
    for i in pm.ls(type="VRaySettingsNode"):
        if rendersetting:
            if 'width' in rendersetting and i.hasAttr("width") :
                i.width.set(rendersetting['width'])
            if 'height' in rendersetting and i.hasAttr("height") :
                i.height.set(rendersetting['height'])     
    # if i.hasAttr("srdml"):
        # if taskid in [9277600,9277601]:
            # dml = 2500
        # i.srdml.set(dml)
        # print "set vray srdml %s MB" %(dml)
    if taskid in [9289969]:
        mel.eval("putenv(\"MAYA_DISABLE_BATCH_RUNUP\",\"1\"); global proc dynRunupForBatchRender() {}; ")                
if user_id in [1846319]:
    for i in pm.ls(type="resolution"):
        if rendersetting:
            if 'width' in rendersetting and i.hasAttr("width") :
                i.width.set(int(rendersetting['width']))
            if 'height' in rendersetting and i.hasAttr("height") :
                i.height.set(int(rendersetting['height']))  

if user_id in [1848725]:
    for i in pm.ls(type="VRaySettingsNode"):
        if rendersetting:
            if 'width' in rendersetting and i.hasAttr("width") :
                i.width.set(rendersetting['width'])
            if 'height' in rendersetting and i.hasAttr("height") :
                i.height.set(rendersetting['height'])    

                
if user_id in [1818014]:
    for i in pm.ls(type="VRaySettingsNode"):
        if rendersetting:
            if 'width' in rendersetting and i.hasAttr("width") :
                i.width.set(rendersetting['width'])
            if 'height' in rendersetting and i.hasAttr("height") :
                i.height.set(rendersetting['height'])
                
if user_id in [1855835]:
    for i in pm.ls(type="VRaySettingsNode"):
        if rendersetting:
            if 'width' in rendersetting and i.hasAttr("width") :
                i.width.set(rendersetting['width'])
            if 'height' in rendersetting and i.hasAttr("height") :
                i.height.set(rendersetting['height'])
if user_id in [1833080]:
    for i in pm.ls(type="aiStandIn"):
        i.deferStandinLoad.set(0)
        print "set %s to 0" % (i.deferStandinLoad)  
if user_id in [1833042]:
    for i in pm.ls(type="aiStandIn"):
        i.deferStandinLoad.set(0)
        print "set %s to 0" % (i.deferStandinLoad)         
if user_id in [1833047]:
    for i in pm.ls(type="aiStandIn"):
        i.deferStandinLoad.set(0)
        print "set %s to 0" % (i.deferStandinLoad)

# if user_id in [1820999]:
    # print "set vray srdml "
    # print taskid
    # for i in pm.ls(type="VRaySettingsNode"):
        # if i.hasAttr("srdml"):
            # dml = 20000            
            # if taskid in [9183335,9183346,9183337,9183224]:
                # dml = 32000
            # i.srdml.set(dml)
            # print "set vray srdml %s MB" %(dml)

if user_id in [1832764]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(48000)
        if i.hasAttr("sys_distributed_rendering_on"):
            i.sys_distributed_rendering_on.set(False)
        if i.hasAttr("globopt_gi_dontRenderImage"):
            i.globopt_gi_dontRenderImage.set(False)
    for i in pm.ls(type="aiStandIn"):
        i.deferStandinLoad.set(0)
        print "set %s to 0" % (i.deferStandinLoad)
        
    for i in pm.ls(type="aiOptions"):
        print "defaultArnoldRenderOptions.abortOnError 0"
        i.abortOnError.set(1)
        i.log_verbosity.set(1)
    for i in pm.ls(type="pgYetiMaya"):
        print "%s .aiLoadAtInit 1" % (i)
        i.aiLoadAtInit.set(1)
if user_id in [1843589]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(0)
if user_id in [1867173]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(30000)
if user_id in [1852550]:
    for i in pm.ls(type="pgYetiMaya"):
        print "%s .aiLoadAtInit 1" % (i)
        i.aiLoadAtInit.set(1)
    for i in pm.ls(type="aiOptions"):
        print "defaultArnoldRenderOptions.abortOnError 0"
        i.abortOnError.set(0)
        print "abortOnError off"
if user_id in [1844577,1857698,1853469]:
    for i in pm.ls(type="pgYetiMaya"):
        print "%s .aiLoadAtInit 1" % (i)
        i.aiLoadAtInit.set(1)        
if user_id in [1300061]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(30000)
            print "set vray srdml 30000"
        # if i.hasAttr("sys_distributed_rendering_on"):
            # i.sys_distributed_rendering_on.set(False)
        # if i.hasAttr("globopt_gi_dontRenderImage"):
            # i.globopt_gi_dontRenderImage.set(False)
            
if user_id in [1805679]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(30000)
            print "set vray srdml 30000"
            
if user_id in [1843088]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(30000)
            print "set vray srdml 30000"
# if user_id in [1843589]:
    # print "set vray srdml "
    # for i in pm.ls(type="VRaySettingsNode"):
        # if i.hasAttr("srdml"):
            # i.srdml.set(0)
            # print "set vray srdml 0"
if user_id in [1814431]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(0)
            print "set vray srdml 0"
if user_id in [1820999]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(0)
            print "set vray srdml 0"
if user_id in [1840038]:
    print start
    if start:
        cmds.currentTime(int(start),edit=True)
        print "update frame"
    mel.eval("putenv(\"MAYA_DISABLE_BATCH_RUNUP\",\"1\"); global proc dynRunupForBatchRender() {}; ") 
if user_id in [1863884,1839312]:
    print start
    if start:
        cmds.currentTime(int(start-1),edit=True)
    mel.eval("putenv(\"MAYA_DISABLE_BATCH_RUNUP\",\"1\"); global proc dynRunupForBatchRender() {}; ") 
    
if user_id in [1853812]:
    if taskid in [16078054]:
        for i in pm.ls(type="RedshiftOptions"):          
            if i.hasAttr("motionBlurEnable"):
                i.motionBlurEnable.set(0)
                print "set  motionBlurEnable   0"

    print start
    if start:
        cmds.currentTime(int(start),edit=True)
    mel.eval("putenv(\"MAYA_DISABLE_BATCH_RUNUP\",\"1\"); global proc dynRunupForBatchRender() {}; ")
    try:
        mel.eval("delete DT_C_BXXZ:frameCounterUpdate;")
    except:
        pass
        
    
    
if user_id in [830123]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(50000)
            print "set vray srdml 0"            
if user_id in [1844577]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(55000)
            print "set vray srdml 55000"

if user_id in [963260]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(0)
            print "set vray srdml 0"
            
if user_id in [1843698]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(32000)
        if i.hasAttr("sys_distributed_rendering_on"):
            i.sys_distributed_rendering_on.set(False)
        if i.hasAttr("globopt_gi_dontRenderImage"):
            i.globopt_gi_dontRenderImage.set(False)
    rep_path =""
    search=""
    dicts={}
    if search:
        dicts=file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            change_path(node_type, attr_name, mapping, rep_path,dicts) 
            
if user_id in [1859047]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(48000)
    mel.eval("putenv(\"MAYA_DISABLE_BATCH_RUNUP\",\"1\"); global proc dynRunupForBatchRender() {}; ")                          
if user_id in [964311]:
    rep_path =""
    search=""
    dicts={}
    if search:
        dicts=file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            change_path(node_type, attr_name, mapping, rep_path,dicts)  
                          
if user_id in [1816685]:
    rep_path =""
    search=""
    dicts={}
    if search:
        dicts=file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            change_path(node_type, attr_name, mapping, rep_path,dicts)  

if user_id in [1832581]:
    print mapping
    rep_path =""
    search=""
    dicts={}
    if search:
        dicts=file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            change_path(node_type, attr_name, mapping, rep_path,dicts)
if user_id in [1848484]:
    rep_path =""
    search=""
    dicts={}
    if search:
        dicts=file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            change_path(node_type, attr_name, mapping, rep_path,dicts)  
            
if user_id in [1848680]:
    rep_path =""
    search=""
    dicts={}
    if search:
        dicts=file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            change_path(node_type, attr_name, mapping, rep_path,dicts)
if user_id in [962539]:
    rep_path =""
    search=""
    dicts={}
    if search:
        dicts=file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            change_path(node_type, attr_name, mapping, rep_path,dicts)
    for i in pm.ls(type="aiOptions"):
        #print "defaultArnoldRenderOptions.abortOnError 0"
        #i.abortOnError.set(1)
        i.log_verbosity.set(0)
        if i.hasAttr("autotx"):
            i.autotx.set(False)
        i.absoluteTexturePaths.set(0)
        i.absoluteProceduralPaths.set(0)
        source_path="%s/sourceimages" % (maya_proj_paht)
        i.shader_searchpath.set(source_path)
        i.texture_searchpath.set(source_path)
        
        
if user_id in [965281]:
    print start
    if start:
        cmds.currentTime(int(start),edit=True)
if user_id in [1822731]:
    print start
    if start:
        cmds.currentTime(int(start-1),edit=True)
        print "update to pre frame"
if user_id in [1834714]:
    mel.eval('setUpAxis \"Y\";')
    print start
    if start:
        cmds.currentTime(int(start),edit=True)
if user_id in [963909]:
    mel.eval('setUpAxis \"Z\";')
    print start
    if start:
        cmds.currentTime(int(start),edit=True)
if user_id in [963447]:
    print start
    if start:
        cmds.currentTime(int(start),edit=True)
    for i in pm.ls(type="pgYetiMaya"):
        print "%s .aiLoadAtInit 1" % (i)
        i.aiLoadAtInit.set(1)
    # for i in pm.ls(type="aiOptions"):
        # i.motion_blur_enable.set(0)
        # print "defaultArnoldRenderOptions.motion_blur_enable 0"
print "step01"
if user_id in [1833038]:
    print "666666666666666666666666666666666666666"

if user_id in [1835213,1881622,1859026,1863099,1883450,1877965,1879546,1833958]:
    print "set Redshift VRAM"
    for i in pm.ls(type='RedshiftOptions'):
        if i.hasAttr("automaticMemoryManagement"):
            print "automaticMemoryManagement is 0"
            i.automaticMemoryManagement.set(0)
        if i.hasAttr("maxNumGPUMBForIrradiancePointCloudHierarchy"):
            print "Irradiance Point Cloud is 256"
            i.maxNumGPUMBForIrradiancePointCloudHierarchy.set(256)
        if i.hasAttr("percentageOfGPUMemoryToUse"):
            print "percentageOfGPUMemoryToUse is 95"
            i.percentageOfGPUMemoryToUse.set(95)
        if i.hasAttr("maxNumGPUMBForForICPHierarchy"):
            print "maxNumGPUMBForForICPHierarchy is 512"
            i.maxNumGPUMBForForICPHierarchy.set(512)
        if i.hasAttr("percentageOfFreeMemoryUsedForTextureCache"):
            print "percentageOfFreeMemoryUsedForTextureCache is 15"
            i.percentageOfFreeMemoryUsedForTextureCache.set(15)
        if i.hasAttr("maxNumCPUMBForTextureCache"):
            print "maxNumCPUMBForTextureCache is 5120"
            i.maxNumCPUMBForTextureCache.set(5120)
        # if i.hasAttr("enableDebugCapture"):
            # print "redshiftOptions.enableDebugCapture"
            # print "once you get the crash , the message (log file html and bin files) will save in  D:\temp\REDSHIFT\CACHE\G0\Log/Log.Latest.0. "
            # i.enableDebugCapture.set(1)    
    
if user_id in [1813649,1857270,1888315]:
    print "set Redshift VRAM"
    for i in pm.ls(type='RedshiftOptions'):
        if i.hasAttr("automaticMemoryManagement"):
            print "automaticMemoryManagement is 0"
            i.automaticMemoryManagement.set(0)
        if i.hasAttr("maxNumGPUMBForIrradiancePointCloudHierarchy"):
            print "Irradiance Point Cloud is 512"
            i.maxNumGPUMBForIrradiancePointCloudHierarchy.set(512)
        if i.hasAttr("percentageOfGPUMemoryToUse"):
            print "percentageOfGPUMemoryToUse is 95"
            i.percentageOfGPUMemoryToUse.set(95)
        if i.hasAttr("maxNumGPUMBForForICPHierarchy"):
            print "maxNumGPUMBForForICPHierarchy is 512"
            i.maxNumGPUMBForForICPHierarchy.set(512)
        if i.hasAttr("percentageOfFreeMemoryUsedForTextureCache"):
            print "percentageOfFreeMemoryUsedForTextureCache is 15"
            i.percentageOfFreeMemoryUsedForTextureCache.set(15)
        if i.hasAttr("maxNumCPUMBForTextureCache"):
            print "maxNumCPUMBForTextureCache is 10240"
            i.maxNumCPUMBForTextureCache.set(10240)
        # if i.hasAttr("enableDebugCapture"):
            # print "redshiftOptions.enableDebugCapture"
            # print "once you get the crash , the message (log file html and bin files) will save in  D:\temp\REDSHIFT\CACHE\G0\Log/Log.Latest.0. "
            # i.enableDebugCapture.set(1)   
            
if user_id in [1868563]:
    print "set Redshift VRAM"
    for i in pm.ls(type='RedshiftOptions'):
        # if i.hasAttr("automaticMemoryManagement"):
            # print "automaticMemoryManagement is 0"
            # i.automaticMemoryManagement.set(0)
        # if i.hasAttr("maxNumGPUMBForIrradiancePointCloudHierarchy"):
            # print "Irradiance Point Cloud is 1024"
            # i.maxNumGPUMBForIrradiancePointCloudHierarchy.set(1024)
        # if i.hasAttr("percentageOfGPUMemoryToUse"):
            # print "percentageOfGPUMemoryToUse is 95"
            # i.percentageOfGPUMemoryToUse.set(95)
        # if i.hasAttr("maxNumGPUMBForForICPHierarchy"):
            # print "maxNumGPUMBForForICPHierarchy is 1024"
            # i.maxNumGPUMBForForICPHierarchy.set(1024)
        # if i.hasAttr("percentageOfFreeMemoryUsedForTextureCache"):
            # print "percentageOfFreeMemoryUsedForTextureCache is 15"
            # i.percentageOfFreeMemoryUsedForTextureCache.set(15)
        # if i.hasAttr("maxNumCPUMBForTextureCache"):
            # print "maxNumCPUMBForTextureCache is 10240"
            # i.maxNumCPUMBForTextureCache.set(10240)
        if i.hasAttr("enableDebugCapture"):
            print "redshiftOptions.enableDebugCapture"
            print "once you get the crash , the message (log file html and bin files) will save in  D:\temp\REDSHIFT\CACHE\G0\Log/Log.Latest.0. "
            i.enableDebugCapture.set(1)   
            
if user_id in [1844817,961743,1844765,963567,1860992,962371,1854466,1811755,1863576,1878285,1877869,1864856,1876209,1876088,1903427]:
    print "set Redshift VRAM"
    for i in pm.ls(type='RedshiftOptions'):
        if i.hasAttr("maxNumGPUMBForIrradiancePointCloudHierarchy"):
            print "Irradiance Point Cloud is 512"
            i.maxNumGPUMBForIrradiancePointCloudHierarchy.set(512)
        if i.hasAttr("maxNumGPUMBForForICPHierarchy"):
            print "Irradiance cache is 512"
            i.maxNumGPUMBForForICPHierarchy.set(512)
        if i.hasAttr("maxNumCPUMBForTextureCache"):
            print "maxNumCPUMBForTextureCache is 512"
            i.maxNumCPUMBForTextureCache.set(10240)
        # if i.hasAttr("enableDebugCapture"):
            # print "redshiftOptions.enableDebugCapture"
            # print "once you get the crash , the message (log file html and bin files) will save in  D:\temp\REDSHIFT\CACHE\G0\Log/Log.Latest.0. "
            # i.enableDebugCapture.set(1)
    rd_path = pm.PyNode("defaultRenderGlobals").imageFilePrefix.get()
    print "old rd_path :: %s " % rd_path
    if rd_path == None :
        rd_path =''
        print "pre.fix is default"
    if "<RenderLayer>" not in  rd_path:
        rel = "<RenderLayer>"
        if rd_path == "":
            rd_path = rel
            print "change_path :: %s " %  rd_path
            pm.PyNode("defaultRenderGlobals").imageFilePrefix.set(rd_path)
        else:
            rd_path_split  = rd_path.replace("\\",'/').rsplit('/',1)
            if  len(rd_path_split) == 2:
                rd_path = "/".join([rd_path_split[0],rel,rd_path_split[1]])
            elif len(rd_path_split) == 1:
                rd_path = "/".join([rel, rd_path_split[0]])
            print "change_path :: %s " %  rd_path
            pm.PyNode("defaultRenderGlobals").imageFilePrefix.set(rd_path)
if user_id in [18448171111111]:
    print "set Redshift VRAM"
    for i in pm.ls(type='RedshiftOptions'):
        if i.hasAttr("automaticMemoryManagement"):
            print "automaticMemoryManagement is OFF"
            i.automaticMemoryManagement.set(0)
        if i.hasAttr("maxNumGPUMBForIrradiancePointCloudHierarchy"):
            print "Irradiance Point Cloud is 128"
            i.maxNumGPUMBForIrradiancePointCloudHierarchy.set(128)
        if i.hasAttr("percentageOfGPUMemoryToUse"):
            print "percentageOfGPUMemoryToUse is 90"
            i.percentageOfGPUMemoryToUse.set(90)
        if i.hasAttr("maxNumGPUMBForForICPHierarchy"):
            print "maxNumGPUMBForForICPHierarchy is 128"
            i.maxNumGPUMBForForICPHierarchy.set(128)
        if i.hasAttr("percentageOfFreeMemoryUsedForTextureCache"):
            print "percentageOfFreeMemoryUsedForTextureCache is 15"
            i.percentageOfFreeMemoryUsedForTextureCache.set(15)
        if i.hasAttr("maxNumCPUMBForTextureCache"):
            print "maxNumCPUMBForTextureCache is 4096"
            i.maxNumCPUMBForTextureCache.set(4096)
        if taskid in [16127821]:    
            if i.hasAttr("primaryGIEngine"):
                giengine_dict = {0:"None",1:"Photon Map",3:"Irradiance Cache",4:"Brute Force"}
                gi_idex = i.primaryGIEngine.get()
                print "Scene primaryGIEngine is %s" % giengine_dict[gi_idex]                
                i.primaryGIEngine.set(0)  
                gi_idex_new = i.primaryGIEngine.get()
                print "set primaryGIEngine is %s"  % giengine_dict[gi_idex_new]    

            if i.hasAttr("secondaryGIEngine"):
                s_giengine_dict = {0:"None",1:"Photon Map",2:"Irradiance Point Cloud",4:"Brute Force"}
                s_gi_idex = i.secondaryGIEngine.get()
                print "Scene secondaryGIEngine is %s" % s_giengine_dict[s_gi_idex]                
                i.secondaryGIEngine.set(4)  
                s_gi_idex_new = i.secondaryGIEngine.get()
                print "set secondaryGIEngine is %s"  % s_giengine_dict[s_gi_idex_new]  
                
            if i.hasAttr("bruteForceGINumRays"):
                GINumRays = i.bruteForceGINumRays.get()
                print "Scene bruteForceGINumRays is %s" %str(GINumRays)
                i.bruteForceGINumRays.set(256)
                print "set bruteForceGINumRays is 256"
                
    rd_path = pm.PyNode("defaultRenderGlobals").imageFilePrefix.get()
    print "old rd_path :: %s " % rd_path
    if rd_path == None :
        rd_path =''
        print "pre.fix is default"
    if "<RenderLayer>" not in  rd_path:
        rel = "<RenderLayer>"
        if rd_path == "":
            rd_path = rel
            print "change_path :: %s " %  rd_path
            pm.PyNode("defaultRenderGlobals").imageFilePrefix.set(rd_path)
        else:
            rd_path_split  = rd_path.replace("\\",'/').rsplit('/',1)
            if  len(rd_path_split) == 2:
                rd_path = "/".join([rd_path_split[0],rel,rd_path_split[1]])
            elif len(rd_path_split) == 1:
                rd_path = "/".join([rel, rd_path_split[0]])
            print "change_path :: %s " %  rd_path
            pm.PyNode("defaultRenderGlobals").imageFilePrefix.set(rd_path)  
    mel.eval("putenv(\"MAYA_DISABLE_BATCH_RUNUP\",\"1\"); global proc dynRunupForBatchRender() {}; ")              

if user_id in [1844953,1847323,1831205]:
    for i in pm.ls(type='aiOptions'):
        if i.hasAttr("autotx"):
            print "autotx is false"
            i.autotx.set(False)
if user_id in [1848099]:
    for i in pm.ls(type='aiOptions'):
        if i.hasAttr("autotx"):
            i.autotx.set(False)
        print "autotx is OFF"
if user_id in [1819610]:
    print "  "
    rd_path()
    
    cmds.setAttr("redshiftOptions.maxNumGPUMBForForICPHierarchy",256)
if user_id in [119768]:
    print "test rs tile ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    # if rendersetting:
        # reg = rendersetting['tile_region'].split(' ')
        # print reg 
        # # mel.eval("setAttr defaultRenderGlobals.leftRegion %s" % (reg[0]))
        # # mel.eval("setAttr defaultRenderGlobals.rightRegion %s" % (reg[1]))
        # # mel.eval("setAttr defaultRenderGlobals.bottomRegion %s" % (reg[2]))
        # # mel.eval("setAttr defaultRenderGlobals.topRegion %s" % (reg[3]))
        # # mel.eval("setAttr defaultRenderGlobals.useRenderRegion true")

        # mel.eval("setAttr defaultRenderGlobals.left %s" % (reg[0]))
        # mel.eval("setAttr defaultRenderGlobals.rght %s" % (reg[1]))
        # mel.eval("setAttr defaultRenderGlobals.bot %s" % (reg[2]))
        # mel.eval("setAttr defaultRenderGlobals.top %s" % (reg[3]))
        
        # print mel.eval("getAttr defaultRenderGlobals.leftRegion")
        # print mel.eval("getAttr defaultRenderGlobals.rightRegion")
        # print mel.eval("getAttr defaultRenderGlobals.bottomRegion")
        # print mel.eval("getAttr defaultRenderGlobals.topRegion")
        # print mel.eval("getAttr defaultRenderGlobals.useRenderRegion")
    print "test rs tile ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"

if user_id in [964309]:
    print " SET Redshift Render attribute"
    rd_path()
    for i in pm.ls(type='RedshiftOptions'):
        if i.hasAttr("copyToTextureCache"):
            print "copyToTextureCache is on"
            i.copyToTextureCache.set(1)
        if i.hasAttr("percentageOfGPUMemoryToUse"):
            print "percentageOfGPUMemoryToUse is 90%"
            i.percentageOfGPUMemoryToUse.set(90)
        if i.hasAttr("maxNumGPUMBForIrradiancePointCloudHierarchy"):
            print "Irradiance Point Cloud is 256"
            i.maxNumGPUMBForIrradiancePointCloudHierarchy.set(256)
        if i.hasAttr("maxNumGPUMBForForICPHierarchy"):
            print "Irradiance cache is 256"
            i.maxNumGPUMBForForICPHierarchy.set(256)
        if i.hasAttr("percentageOfFreeMemoryUsedForTextureCache"):
            print "percentageOfFreeMemoryUsedForTextureCache is 15%"
            i.percentageOfFreeMemoryUsedForTextureCache.set(15)
        if i.hasAttr("maxNumGPUMBForTextureCache"):
            print "maxNumGPUMBForTextureCache is 256"
            i.maxNumGPUMBForTextureCache.set(256)
        if i.hasAttr("maxNumCPUMBForTextureCache"):
            print "maxNumCPUMBForTextureCache is 4096"
            i.maxNumCPUMBForTextureCache.set(4096)
        if i.hasAttr("numGPUMBToReserveForRays"):
            print "numGPUMBToReserveForRays is 0"
            i.numGPUMBToReserveForRays.set(0)
        # if i.hasAttr("automaticMemoryManagement"):
            # print "This Redshift version has automaticMemoryManagement attribute "
            # print "automaticMemoryManagement is ON"
            # i.automaticMemoryManagement.set(1)
    if taskid in [16011090]: 
    
        cmds.setAttr("redshiftOptions.maxNumGPUMBForForICPHierarchy",256)  
        cmds.setAttr("redshiftOptions.percentageOfGPUMemoryToUse",100)  
        cmds.setAttr("redshiftOptions.numGPUMBToReserveForRays",4096)  
        cmds.setAttr("redshiftOptions.maxNumCPUMBForTextureCache",10240)  
        cmds.setAttr("redshiftOptions.maxNumGPUMBForTextureCache",1024)

    if taskid in [16038460]: 
    
        cmds.setAttr("redshiftOptions.maxNumGPUMBForForICPHierarchy",256)  
        cmds.setAttr("redshiftOptions.percentageOfGPUMemoryToUse",90)  
        cmds.setAttr("redshiftOptions.numGPUMBToReserveForRays",4096)  
        cmds.setAttr("redshiftOptions.maxNumCPUMBForTextureCache",4096)  
        cmds.setAttr("redshiftOptions.maxNumGPUMBForTextureCache",2048)
        print "gpu   test  "
if user_id in [1861699]:
    print " SET Redshift Render attribute"
    rd_path()
    for i in pm.ls(type='RedshiftOptions'):
        if i.hasAttr("copyToTextureCache"):
            print "copyToTextureCache is on"
            i.copyToTextureCache.set(1)
        if i.hasAttr("percentageOfGPUMemoryToUse"):
            print "percentageOfGPUMemoryToUse is 90%"
            i.percentageOfGPUMemoryToUse.set(90)
        if i.hasAttr("maxNumGPUMBForIrradiancePointCloudHierarchy"):
            print "Irradiance Point Cloud is 256"
            i.maxNumGPUMBForIrradiancePointCloudHierarchy.set(256)
        if i.hasAttr("maxNumGPUMBForForICPHierarchy"):
            print "Irradiance cache is 256"
            i.maxNumGPUMBForForICPHierarchy.set(256)
        if i.hasAttr("percentageOfFreeMemoryUsedForTextureCache"):
            print "percentageOfFreeMemoryUsedForTextureCache is 15%"
            i.percentageOfFreeMemoryUsedForTextureCache.set(15)
        if i.hasAttr("maxNumGPUMBForTextureCache"):
            print "maxNumGPUMBForTextureCache is 256"
            i.maxNumGPUMBForTextureCache.set(256)
        if i.hasAttr("maxNumCPUMBForTextureCache"):
            print "maxNumCPUMBForTextureCache is 4096"
            i.maxNumCPUMBForTextureCache.set(4096)
        if i.hasAttr("numGPUMBToReserveForRays"):
            print "numGPUMBToReserveForRays is 0"
            i.numGPUMBToReserveForRays.set(0)
        # if i.hasAttr("automaticMemoryManagement"):
            # print "This Redshift version has automaticMemoryManagement attribute "
            # print "automaticMemoryManagement is ON"
            # i.automaticMemoryManagement.set(1)  
    # cmds.setAttr("redshiftOptions.maxNumGPUMBForForICPHierarchy",256)  
    # cmds.setAttr("redshiftOptions.percentageOfGPUMemoryToUse",90)  
    # cmds.setAttr("redshiftOptions.numGPUMBToReserveForRays",4096)  
    # cmds.setAttr("redshiftOptions.maxNumCPUMBForTextureCache",4096)  
    # cmds.setAttr("redshiftOptions.maxNumGPUMBForTextureCache",2048)                
if user_id in [1814856]:
    print user_id
    print plugins
    print "+++++++++++++++++++++++mapping+++++++++++++++++++++++"
    print mapping
    print "+++++++++++++++++++++++mapping+++++++++++++++++++++++"
    render_node.postMel.set(l=0)
    render_node.postMel.set("")
    render_node.preRenderLayerMel.set(l=0)
    render_node.preRenderLayerMel.set("")
    render_node.postRenderLayerMel.set(l=0)
    render_node.postRenderLayerMel.set("")
    render_node.preRenderMel.set(l=0)
    render_node.preRenderMel.set("")
    render_node.postRenderMel.set(l=0)
    render_node.postRenderMel.set("")
    rep_path =""
    search=""
    dicts={}
    if search:
        dicts=file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            change_path(node_type, attr_name, mapping, rep_path,dicts)
    set_yeti_imageSearchPath(mapping)        
if user_id in [1815272]:
    rd_path()
    pre_layer_mel()
    # for i in pm.ls(type="aiOptions"):
        # i.abortOnError.set(0)
        # print 'abortOnError-off'
    for i in pm.ls(type="aiOptions"):
        i.abortOnError.set(0)
        print 'abortOnError-off'
        
if user_id in [1886200,1846192]:
    print " SET Redshift Render attribute"
    rd_path()
    for i in pm.ls(type='RedshiftOptions'):
        if i.hasAttr("copyToTextureCache"):
            print "copyToTextureCache is on"
            i.copyToTextureCache.set(1)
        if i.hasAttr("percentageOfGPUMemoryToUse"):
            print "percentageOfGPUMemoryToUse is 90%"
            i.percentageOfGPUMemoryToUse.set(90)
        if i.hasAttr("maxNumGPUMBForIrradiancePointCloudHierarchy"):
            print "Irradiance Point Cloud is 512"
            i.maxNumGPUMBForIrradiancePointCloudHierarchy.set(512)
        if i.hasAttr("maxNumGPUMBForForICPHierarchy"):
            print "Irradiance cache is 512"
            i.maxNumGPUMBForForICPHierarchy.set(512)
        if i.hasAttr("percentageOfFreeMemoryUsedForTextureCache"):
            print "percentageOfFreeMemoryUsedForTextureCache is 15%"
            i.percentageOfFreeMemoryUsedForTextureCache.set(15)
        if i.hasAttr("maxNumGPUMBForTextureCache"):
            print "maxNumGPUMBForTextureCache is 256"
            i.maxNumGPUMBForTextureCache.set(256)
        if i.hasAttr("maxNumCPUMBForTextureCache"):
            print "maxNumCPUMBForTextureCache is 4096"
            i.maxNumCPUMBForTextureCache.set(4096)
        if i.hasAttr("numGPUMBToReserveForRays"):
            print "numGPUMBToReserveForRays is 0"
            i.numGPUMBToReserveForRays.set(0)  

        if i.hasAttr("irradiancePointCloudScreenRadius"):
            print "irradiancePointCloudScreenRadius is 8"
            i.irradiancePointCloudScreenRadius.set(8) 

            
    for i in pm.ls(type="pgYetiMaya"):
        if i.hasAttr("aiLoadAtInit"):
            i.aiLoadAtInit.set(1)
            # print "%s .aiLoadAtInit 1" % (i)        
        
        
if user_id in [1016752]:
    rd_path()
    pre_layer_mel()
    
if user_id in [1866194,1873149,1903427,1905390,964549]:
    rd_path()
    mel.eval("putenv(\"MAYA_DISABLE_BATCH_RUNUP\",\"1\"); global proc dynRunupForBatchRender() {}; ")
    print "Set MAYA_DISABLE_BATCH_RUNUP = 1"
    # pre_layer_mel()

if user_id in [1848903]:
    rep_path =""
    search=""
    dicts={}
    if search:
        dicts=file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            change_path(node_type, attr_name, mapping, rep_path,dicts)
if user_id in [1852464]:
    if taskid in [5347743]:
        for i in pm.ls(type="aiOptions"):
            i.abortOnError.set(0)
            print "abort On Error turn off"
if user_id in [9271787]:
    mel.eval("optionVar  -iv \"miUseMayaAlphaDetection\" 1; ")
if user_id in [1814593,119602]:
    mel.eval("optionVar  -iv \"renderSetupEnable\" 0;")
if user_id in [1813119]:
    render_node.preRenderLayerMel.set("")
    render_node.postRenderLayerMel.set("")
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(0)
            print "set vray srdml 0"
if user_id in [1859072,1859047]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(0)
            print "set vray srdml 0"
            
if user_id in [1821671]:
    current_renderer=pm.PyNode("defaultRenderGlobals").currentRenderer.get()
    print "currentRenderer is %s" % (current_renderer)
    output_prefix = pm.PyNode("defaultRenderGlobals").imageFilePrefix.get()
    if output_prefix=="":
        print "output_prefix is Defaults"
        sceneName = os.path.splitext(os.path.basename(pm.system.sceneName()))[0].strip()
        pm.PyNode("defaultRenderGlobals").imageFilePrefix.set(sceneName)
        Newoutput_prefix=pm.PyNode("defaultRenderGlobals").imageFilePrefix.get()
        print "New output_prefix is %s" % (Newoutput_prefix)
    if start and end:
        scenes_start = pm.PyNode("defaultRenderGlobals").startFrame.get()
        scenes_end = pm.PyNode("defaultRenderGlobals").endFrame.get()
        print "scenes_start frame is %s" % (scenes_start)
        print "scenes_end frame is %s" % (scenes_end)
        startFrame = start
        endFrame = end
        pm.PyNode("defaultRenderGlobals").startFrame.set(startFrame)
        pm.PyNode("defaultRenderGlobals").endFrame.set(endFrame)
        print "set current render startFrame is %s" % (startFrame)
        print "set current render endFrame is %s" % (endFrame)
        
        
# if user_id in [1861699]:
    # mel.eval('colorManagementPrefs -e -cmEnabled 1;')
    # print "Enable color manger"
if user_id in [1854466]:
    for i in pm.ls(type="RedshiftOptions"):
        if i.hasAttr("logLevel") :
            i.logLevel.set(2)
            print "Set Redshift log level to 2"
            
if user_id in [1909924]:
    cmds.cycleCheck(evaluation=False)
    print "cycleCheck OFF "
    mel.eval("putenv(\"MAYA_DISABLE_BATCH_RUNUP\",\"1\"); global proc dynRunupForBatchRender() {}; ") 
    print "MAYA_DISABLE_BATCH_RUNUP =>1"
    
        
print "**********************************************the prerender end******************************************************"