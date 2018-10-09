
if self.user_id in [1850226]:
    print self.start
    if self.start:
        cmds.currentTime(int(self.start) ,edit=True)
if self.user_id in [1864685]:
    mel.eval("delete `ls -type unknown`")
if self.user_id in [1852657]:
    mel.eval('source "C:/Program Files/Domemaster3D/maya/common/scripts/domeRender.mel"; domemaster3DPreRenderMEL();')
if self.user_id in [962413 ,1844068]:
    for i in pm.ls(type="aiStandIn"):
        i.deferStandinLoad.set(0)
        print "set %s to 0" % (i.deferStandinLoad)

print self.user_id
if self.user_id in [1818411]:
    for i in pm.ls(type="aiStandIn"):
        i.deferStandinLoad.set(0)
        print "set %s to 0" % (i.deferStandinLoad)
if self.user_id in [963567]:
    print self.plugins
    print "+++++++++++++++++++++++mapping+++++++++++++++++++++++"
    print self.mapping
    print "rendersetting"
    print self.rendersetting
    print "+++++++++++++++++++++++mapping+++++++++++++++++++++++"
    print self.user_id

    rep_path =""
    search = ""
    dicts = {}
    if search:
        dicts = file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            self.change_path(node_type, attr_name, self.mapping, rep_path, dicts)
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
        dicts = file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            self.change_path(node_type, attr_name, self.mapping, rep_path, dicts)

    if "pgYetiMaya" not in self.plugins or "vrayformaya" not in self.plugins:
        self.render_node.postMel.set("")

    self.del_node('SGFC_sc05_sh01_ly_yong:SGFC_ch010001SwimsuitGirl_l_msAnim:Facial_PanelShape')
    self.del_node("SGFC_ch008001Policeman1_h_msAnim:Facial_PanelShape")
    self.del_node("aiAreaLightShape1309")
    self.del_node("Facial_PanelShape")

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
                i.width.set(self.rendersetting['width'])
            if 'height' in self.rendersetting and i.hasAttr("height"):
                i.height.set(self.rendersetting['height'])

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
        # setAttr "defaultArnoldRenderOptions.absoluteProceduralPaths" 0;
        # i.procedural_searchpath.set(r"N:\cg_custom_setup\network\arnold\htoa-1.11.1_r1692_houdini-15.0.393_windows\arnold\procedurals")

        i.shader_searchpath.set(source_path)
        i.texture_searchpath.set(source_path)
        # setAttr -type "string" defaultArnoldRenderOptions.procedural_searchpath ;
        # if self.user_id in [1873149]:
        # refs = pm.listReferences()
        # for ref in refs:
        # if ref.isLoaded():
        # print ref
        # ref.importContents()
        # else:
        # print ref
        # self.change_path_mapping("AlembicNode", "abc_File",self.mapping)
        # cmds.refresh()



        # if self.user_id in [1840038]:
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
if self.user_id in [1840793]:
    for i in pm.ls(type="VRaySettingsNode"):
        if self.rendersetting:
            if 'width' in self.rendersetting and i.hasAttr("width"):
                i.width.set(self.rendersetting['width'])
            if 'height' in self.rendersetting and i.hasAttr("height"):
                i.height.set(self.rendersetting['height'])
                # if i.hasAttr("srdml"):
                # if self.task_id in [9277600,9277601]:
                # dml = 2500
                # i.srdml.set(dml)
                # print "set vray srdml %s MB" %(dml)
    if self.task_id in [9289969]:
        mel.eval("putenv(\"MAYA_DISABLE_BATCH_RUNUP\",\"1\"); global proc dynRunupForBatchRender() {}; ")
if self.user_id in [1846319]:
    for i in pm.ls(type="resolution"):
        if self.rendersetting:
            if 'width' in self.rendersetting and i.hasAttr("width"):
                i.width.set(int(self.rendersetting['width']))
            if 'height' in self.rendersetting and i.hasAttr("height"):
                i.height.set(int(self.rendersetting['height']))

if self.user_id in [1848725]:
    for i in pm.ls(type="VRaySettingsNode"):
        if self.rendersetting:
            if 'width' in self.rendersetting and i.hasAttr("width"):
                i.width.set(self.rendersetting['width'])
            if 'height' in self.rendersetting and i.hasAttr("height"):
                i.height.set(self.rendersetting['height'])

if self.user_id in [1818014]:
    for i in pm.ls(type="VRaySettingsNode"):
        if self.rendersetting:
            if 'width' in self.rendersetting and i.hasAttr("width"):
                i.width.set(self.rendersetting['width'])
            if 'height' in self.rendersetting and i.hasAttr("height"):
                i.height.set(self.rendersetting['height'])

if self.user_id in [1855835]:
    for i in pm.ls(type="VRaySettingsNode"):
        if self.rendersetting:
            if 'width' in self.rendersetting and i.hasAttr("width"):
                i.width.set(self.rendersetting['width'])
            if 'height' in self.rendersetting and i.hasAttr("height"):
                i.height.set(self.rendersetting['height'])
if self.user_id in [1833080]:
    for i in pm.ls(type="aiStandIn"):
        i.deferStandinLoad.set(0)
        print "set %s to 0" % (i.deferStandinLoad)
if self.user_id in [1833042]:
    for i in pm.ls(type="aiStandIn"):
        i.deferStandinLoad.set(0)
        print "set %s to 0" % (i.deferStandinLoad)
if self.user_id in [1833047]:
    for i in pm.ls(type="aiStandIn"):
        i.deferStandinLoad.set(0)
        print "set %s to 0" % (i.deferStandinLoad)

        # if self.user_id in [1820999]:
        # print "set vray srdml "
        # print self.task_id
        # for i in pm.ls(type="VRaySettingsNode"):
        # if i.hasAttr("srdml"):
        # dml = 20000            
        # if self.task_id in [9183335,9183346,9183337,9183224]:
        # dml = 32000
        # i.srdml.set(dml)
        # print "set vray srdml %s MB" %(dml)

if self.user_id in [1832764]:
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
if self.user_id in [1843589]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(0)
if self.user_id in [1867173]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(30000)
if self.user_id in [1852550]:
    for i in pm.ls(type="pgYetiMaya"):
        print "%s .aiLoadAtInit 1" % (i)
        i.aiLoadAtInit.set(1)
    for i in pm.ls(type="aiOptions"):
        print "defaultArnoldRenderOptions.abortOnError 0"
        i.abortOnError.set(0)
        print "abortOnError off"
if self.user_id in [1844577, 1857698, 1853469]:
    for i in pm.ls(type="pgYetiMaya"):
        print "%s .aiLoadAtInit 1" % (i)
        i.aiLoadAtInit.set(1)
if self.user_id in [1300061]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(30000)
            print "set vray srdml 30000"
            # if i.hasAttr("sys_distributed_rendering_on"):
            # i.sys_distributed_rendering_on.set(False)
            # if i.hasAttr("globopt_gi_dontRenderImage"):
            # i.globopt_gi_dontRenderImage.set(False)

if self.user_id in [1805679]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(30000)
            print "set vray srdml 30000"

if self.user_id in [1843088]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(30000)
            print "set vray srdml 30000"
            # if self.user_id in [1843589]:
            # print "set vray srdml "
            # for i in pm.ls(type="VRaySettingsNode"):
            # if i.hasAttr("srdml"):
            # i.srdml.set(0)
            # print "set vray srdml 0"
if self.user_id in [1814431]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(0)
            print "set vray srdml 0"
if self.user_id in [1820999]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(0)
            print "set vray srdml 0"
if self.user_id in [1840038]:
    print self.start
    if self.start:
        cmds.currentTime(int(self.start), edit=True)
        print "update frame"
    mel.eval("putenv(\"MAYA_DISABLE_BATCH_RUNUP\",\"1\"); global proc dynRunupForBatchRender() {}; ")
if self.user_id in [1863884, 1839312]:
    print self.start
    if self.start:
        cmds.currentTime(int(self.start - 1), edit=True)
    mel.eval("putenv(\"MAYA_DISABLE_BATCH_RUNUP\",\"1\"); global proc dynRunupForBatchRender() {}; ")

if self.user_id in [1853812]:
    if self.task_id in [16078054]:
        for i in pm.ls(type="RedshiftOptions"):
            if i.hasAttr("motionBlurEnable"):
                i.motionBlurEnable.set(0)
                print "set  motionBlurEnable   0"

    print self.start
    if self.start:
        cmds.currentTime(int(self.start), edit=True)
    mel.eval("putenv(\"MAYA_DISABLE_BATCH_RUNUP\",\"1\"); global proc dynRunupForBatchRender() {}; ")
    try:
        mel.eval("delete DT_C_BXXZ:frameCounterUpdate;")
    except:
        pass

if self.user_id in [830123]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(50000)
            print "set vray srdml 0"
if self.user_id in [1844577]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(55000)
            print "set vray srdml 55000"

if self.user_id in [963260]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(0)
            print "set vray srdml 0"

if self.user_id in [1843698]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(32000)
        if i.hasAttr("sys_distributed_rendering_on"):
            i.sys_distributed_rendering_on.set(False)
        if i.hasAttr("globopt_gi_dontRenderImage"):
            i.globopt_gi_dontRenderImage.set(False)
    rep_path = ""
    search = ""
    dicts = {}
    if search:
        dicts = file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            self.change_path(node_type, attr_name, self.mapping, rep_path, dicts)

if self.user_id in [1859047]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(48000)
    mel.eval("putenv(\"MAYA_DISABLE_BATCH_RUNUP\",\"1\"); global proc dynRunupForBatchRender() {}; ")
if self.user_id in [964311]:
    rep_path = ""
    search = ""
    dicts = {}
    if search:
        dicts = self.file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            self.change_path(node_type, attr_name, self.mapping, rep_path, dicts)

if self.user_id in [1816685]:
    rep_path = ""
    search = ""
    dicts = {}
    if search:
        dicts = self.file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            self.change_path(node_type, attr_name, self.mapping, rep_path, dicts)

if self.user_id in [1832581]:
    print self.mapping
    rep_path = ""
    search = ""
    dicts = {}
    if search:
        dicts = self.file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            self.change_path(node_type, attr_name, self.mapping, rep_path, dicts)
if self.user_id in [1848484]:
    rep_path = ""
    search = ""
    dicts = {}
    if search:
        dicts = self.file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            self.change_path(node_type, attr_name, self.mapping, rep_path, dicts)

if self.user_id in [1848680]:
    rep_path = ""
    search = ""
    dicts = {}
    if search:
        dicts = self.file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            self.change_path(node_type, attr_name, self.mapping, rep_path, dicts)
if self.user_id in [962539]:
    rep_path = ""
    search = ""
    dicts = {}
    if search:
        dicts = self.file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            self.change_path(node_type, attr_name, self.mapping, rep_path, dicts)
    for i in pm.ls(type="aiOptions"):
        # print "defaultArnoldRenderOptions.abortOnError 0"
        # i.abortOnError.set(1)
        i.log_verbosity.set(0)
        if i.hasAttr("autotx"):
            i.autotx.set(False)
        i.absoluteTexturePaths.set(0)
        i.absoluteProceduralPaths.set(0)
        source_path = "%s/sourceimages" % (maya_proj_paht)
        i.shader_searchpath.set(source_path)
        i.texture_searchpath.set(source_path)

if self.user_id in [965281]:
    print self.start
    if self.start:
        cmds.currentTime(int(self.start), edit=True)
if self.user_id in [1822731]:
    print self.start
    if self.start:
        cmds.currentTime(int(self.start - 1), edit=True)
        print "update to pre frame"
if self.user_id in [1834714]:
    mel.eval('setUpAxis \"Y\";')
    print self.start
    if self.start:
        cmds.currentTime(int(self.start), edit=True)
if self.user_id in [963909]:
    mel.eval('setUpAxis \"Z\";')
    print self.start
    if self.start:
        cmds.currentTime(int(self.start), edit=True)
if self.user_id in [963447]:
    print self.start
    if self.start:
        cmds.currentTime(int(self.start), edit=True)
    for i in pm.ls(type="pgYetiMaya"):
        print "%s .aiLoadAtInit 1" % (i)
        i.aiLoadAtInit.set(1)
        # for i in pm.ls(type="aiOptions"):
        # i.motion_blur_enable.set(0)
        # print "defaultArnoldRenderOptions.motion_blur_enable 0"
print "step01"
if self.user_id in [1833038]:
    print "666666666666666666666666666666666666666"

if self.user_id in [1835213, 1881622, 1859026, 1863099, 1883450, 1877965, 1879546, 1833958]:
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

if self.user_id in [1813649, 1857270, 1888315]:
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

if self.user_id in [1868563]:
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

if self.user_id in [1844817, 961743, 1844765, 963567, 1860992, 962371, 1854466, 1811755, 1863576, 1878285, 1877869, 1864856,
               1876209, 1876088, 1903427]:
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
    if rd_path == None:
        rd_path = ''
        print "pre.fix is default"
    if "<RenderLayer>" not in rd_path:
        rel = "<RenderLayer>"
        if rd_path == "":
            rd_path = rel
            print "change_path :: %s " % rd_path
            pm.PyNode("defaultRenderGlobals").imageFilePrefix.set(rd_path)
        else:
            rd_path_split = rd_path.replace("\\", '/').rsplit('/', 1)
            if len(rd_path_split) == 2:
                rd_path = "/".join([rd_path_split[0], rel, rd_path_split[1]])
            elif len(rd_path_split) == 1:
                rd_path = "/".join([rel, rd_path_split[0]])
            print "change_path :: %s " % rd_path
            pm.PyNode("defaultRenderGlobals").imageFilePrefix.set(rd_path)
if self.user_id in [18448171111111]:
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
        if self.task_id in [16127821]:
            if i.hasAttr("primaryGIEngine"):
                giengine_dict = {0: "None", 1: "Photon Map", 3: "Irradiance Cache", 4: "Brute Force"}
                gi_idex = i.primaryGIEngine.get()
                print "Scene primaryGIEngine is %s" % giengine_dict[gi_idex]
                i.primaryGIEngine.set(0)
                gi_idex_new = i.primaryGIEngine.get()
                print "set primaryGIEngine is %s" % giengine_dict[gi_idex_new]

            if i.hasAttr("secondaryGIEngine"):
                s_giengine_dict = {0: "None", 1: "Photon Map", 2: "Irradiance Point Cloud", 4: "Brute Force"}
                s_gi_idex = i.secondaryGIEngine.get()
                print "Scene secondaryGIEngine is %s" % s_giengine_dict[s_gi_idex]
                i.secondaryGIEngine.set(4)
                s_gi_idex_new = i.secondaryGIEngine.get()
                print "set secondaryGIEngine is %s" % s_giengine_dict[s_gi_idex_new]

            if i.hasAttr("bruteForceGINumRays"):
                GINumRays = i.bruteForceGINumRays.get()
                print "Scene bruteForceGINumRays is %s" % str(GINumRays)
                i.bruteForceGINumRays.set(256)
                print "set bruteForceGINumRays is 256"

    rd_path = pm.PyNode("defaultRenderGlobals").imageFilePrefix.get()
    print "old rd_path :: %s " % rd_path
    if rd_path == None:
        rd_path = ''
        print "pre.fix is default"
    if "<RenderLayer>" not in rd_path:
        rel = "<RenderLayer>"
        if rd_path == "":
            rd_path = rel
            print "change_path :: %s " % rd_path
            pm.PyNode("defaultRenderGlobals").imageFilePrefix.set(rd_path)
        else:
            rd_path_split = rd_path.replace("\\", '/').rsplit('/', 1)
            if len(rd_path_split) == 2:
                rd_path = "/".join([rd_path_split[0], rel, rd_path_split[1]])
            elif len(rd_path_split) == 1:
                rd_path = "/".join([rel, rd_path_split[0]])
            print "change_path :: %s " % rd_path
            pm.PyNode("defaultRenderGlobals").imageFilePrefix.set(rd_path)
    mel.eval("putenv(\"MAYA_DISABLE_BATCH_RUNUP\",\"1\"); global proc dynRunupForBatchRender() {}; ")

if self.user_id in [1844953, 1847323, 1831205]:
    for i in pm.ls(type='aiOptions'):
        if i.hasAttr("autotx"):
            print "autotx is false"
            i.autotx.set(False)
if self.user_id in [1848099]:
    for i in pm.ls(type='aiOptions'):
        if i.hasAttr("autotx"):
            i.autotx.set(False)
        print "autotx is OFF"
if self.user_id in [1819610]:
    print "  "
    self.rd_path()

    cmds.setAttr("redshiftOptions.maxNumGPUMBForForICPHierarchy", 256)
if self.user_id in [119768]:
    print "test rs tile ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    # if self.rendersetting:
    # reg = self.rendersetting['tile_region'].split(' ')
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

if self.user_id in [964309]:
    print " SET Redshift Render attribute"
    self.rd_path()
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
    if self.task_id in [16011090]:
        cmds.setAttr("redshiftOptions.maxNumGPUMBForForICPHierarchy", 256)
        cmds.setAttr("redshiftOptions.percentageOfGPUMemoryToUse", 100)
        cmds.setAttr("redshiftOptions.numGPUMBToReserveForRays", 4096)
        cmds.setAttr("redshiftOptions.maxNumCPUMBForTextureCache", 10240)
        cmds.setAttr("redshiftOptions.maxNumGPUMBForTextureCache", 1024)

    if self.task_id in [16038460]:
        cmds.setAttr("redshiftOptions.maxNumGPUMBForForICPHierarchy", 256)
        cmds.setAttr("redshiftOptions.percentageOfGPUMemoryToUse", 90)
        cmds.setAttr("redshiftOptions.numGPUMBToReserveForRays", 4096)
        cmds.setAttr("redshiftOptions.maxNumCPUMBForTextureCache", 4096)
        cmds.setAttr("redshiftOptions.maxNumGPUMBForTextureCache", 2048)
        print "gpu   test  "
if self.user_id in [1861699]:
    print " SET Redshift Render attribute"
    self.rd_path()
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
if self.user_id in [1814856]:
    print self.user_id
    print self.plugins
    print "+++++++++++++++++++++++self.mapping+++++++++++++++++++++++"
    print self.mapping
    print "+++++++++++++++++++++++self.mapping+++++++++++++++++++++++"
    self.render_node.postMel.set(l=0)
    self.render_node.postMel.set("")
    self.render_node.preRenderLayerMel.set(l=0)
    self.render_node.preRenderLayerMel.set("")
    self.render_node.postRenderLayerMel.set(l=0)
    self.render_node.postRenderLayerMel.set("")
    self.render_node.preRenderMel.set(l=0)
    self.render_node.preRenderMel.set("")
    self.render_node.postRenderMel.set(l=0)
    self.render_node.postRenderMel.set("")
    rep_path = ""
    search = ""
    dicts = {}
    if search:
        dicts = self.file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            self.change_path(node_type, attr_name, self.mapping, rep_path, dicts)
    self.set_yeti_imageSearchPath(self.mapping)


if self.user_id in [1886200, 1846192]:
    print " SET Redshift Render attribute"
    self.rd_path()
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

if self.user_id in [1016752]:
    self.rd_path()
    self.conduct_mel()

if self.user_id in [1866194, 1873149, 1903427, 1905390, 964549]:
    self.rd_path()
    mel.eval("putenv(\"MAYA_DISABLE_BATCH_RUNUP\",\"1\"); global proc dynRunupForBatchRender() {}; ")
    print "Set MAYA_DISABLE_BATCH_RUNUP = 1"
    # self.conduct_mel()

if self.user_id in [1848903]:
    rep_path = ""
    search = ""
    dicts = {}
    if search:
        dicts = self.file_dicts(search)
    for attr_dict in attr_list:
        for node_type in attr_dict:
            attr_name = attr_dict[node_type]
            self.change_path(node_type, attr_name, self.mapping, rep_path, dicts)
if self.user_id in [1852464]:
    if self.task_id in [5347743]:
        for i in pm.ls(type="aiOptions"):
            i.abortOnError.set(0)
            print "abort On Error turn off"
if self.user_id in [9271787]:
    mel.eval("optionVar  -iv \"miUseMayaAlphaDetection\" 1; ")
if self.user_id in [1814593, 119602]:
    mel.eval("optionVar  -iv \"renderSetupEnable\" 0;")
if self.user_id in [1813119]:
    self.render_node.preRenderLayerMel.set("")
    self.render_node.postRenderLayerMel.set("")
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(0)
            print "set vray srdml 0"
if self.user_id in [1859072, 1859047]:
    print "set vray srdml "
    for i in pm.ls(type="VRaySettingsNode"):
        if i.hasAttr("srdml"):
            i.srdml.set(0)
            print "set vray srdml 0"

if self.user_id in [1821671]:
    current_renderer=pm.PyNode("defaultRenderGlobals").currentRenderer.get()
    print "currentRenderer is %s" % (current_renderer)
    output_prefix = pm.PyNode("defaultRenderGlobals").imageFilePrefix.get()
    if output_prefix=="":
        print "output_prefix is Defaults"
        sceneName = os.path.splitext(os.path.basename(pm.system.sceneName()))[0].strip()
        pm.PyNode("defaultRenderGlobals").imageFilePrefix.set(sceneName)
        Newoutput_prefix=pm.PyNode("defaultRenderGlobals").imageFilePrefix.get()
        print "New output_prefix is %s" % (Newoutput_prefix)
    if self.start and self.end:
        scenes_start = pm.PyNode("defaultRenderGlobals").startFrame.get()
        scenes_end = pm.PyNode("defaultRenderGlobals").endFrame.get()
        print "scenes_start frame is %s" % (scenes_start)
        print "scenes_end frame is %s" % (scenes_end)
        startFrame = self.start
        endFrame = self.end
        pm.PyNode("defaultRenderGlobals").startFrame.set(startFrame)
        pm.PyNode("defaultRenderGlobals").endFrame.set(endFrame)
        print "set current render startFrame is %s" % (startFrame)
        print "set current render endFrame is %s" % (endFrame)

        # if self.user_id in [1861699]:
        # mel.eval('colorManagementPrefs -e -cmEnabled 1;')
        # print "Enable color manger"
if self.user_id in [1854466]:
    for i in pm.ls(type="RedshiftOptions"):
        if i.hasAttr("logLevel"):
            i.logLevel.set(2)
            print "Set Redshift log level to 2"

if self.user_id in [1909924]:
    cmds.cycleCheck(evaluation=False)
    print "cycleCheck OFF "
    mel.eval("putenv(\"MAYA_DISABLE_BATCH_RUNUP\",\"1\"); global proc dynRunupForBatchRender() {}; ")
    print "MAYA_DISABLE_BATCH_RUNUP =>1"


    def CopyExtfile(self):
        D_ROOT = self.Base.get_json_ini('Node_D')
        EXT_ROOT = self.Base.get_json_ini('MAYA_Plugin_Dir')
        if self.plugins:
            if "mtoa" in self.plugins:
                self.MyLog("<<<<<<Set arnold for shaveNode Extension file>>>>>>>")
                ARNOLD_VERSION = self.plugins['mtoa']
                ARNOLD_PATH = D_ROOT + r"/mtoa/software/maya%s_mtoa%s" % (self.cgVersion, ARNOLD_VERSION)
            
                if not os.path.exists(ARNOLD_PATH + r"/maya_mtoa/shaders/shave_shaders.dll") and not os.path.exists(
                                ARNOLD_PATH + r"/maya_mtoa/extensions/shave.dll") and not os.path.exists(
                                ARNOLD_PATH + r"/maya_mtoa/extensions/shave.py"):
                    extlist = ["1.4.2.2", "2.0.1"]
                    if ARNOLD_VERSION in extlist:
                        EXT_SHADERS = EXT_ROOT + r"/shaveNode/extensions_for_Mtoa/maya%s_mtoa%s/shaders" % (
                        self.cgVersion, ARNOLD_VERSION)
                        EXT_FILE = EXT_ROOT + r"/shaveNode/extensions_for_Mtoa/maya%s_mtoa%s/extensions" % (
                        self.cgVersion, ARNOLD_VERSION)
                    
                        Shaders_srcDir = EXT_SHADERS
                        Shaders_dstDir = ARNOLD_PATH + r"/maya_mtoa/shaders"
                        os.system("robocopy /s  %s %s" % (Shaders_srcDir, Shaders_dstDir))
                    
                        Ext_srcDir = EXT_FILE
                        Ext_dstDir = ARNOLD_PATH + r"/maya_mtoa/extensions"
                        os.system("robocopy /s  %s %s" % (Ext_srcDir, Ext_dstDir))
                    else:
                        self.MyLog(
                            "Current this arnold or maya version don't have shave extsiontion file in B disk,please offer your own file....")
            
            
                else:
                    self.MyLog("This arnold vesion already has the shave extension file ")
            
                self.MyLog("<<<<<<<Set arnold for shaveNode Extension file env finsh!!!>>>>>>>")