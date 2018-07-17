struct STVray(
		
	fn vrayFileFN = (
		G_OBJ_UTIL.dotnetLog (" [STAsset.vrayFileFN.start].... ")	
		
		try
		(
			local hdris = getClassInstances VRayHDRI
			for hd in hdris do	(
				local resultHDRIMapName=G_OBJ_FILEUTIL.analysePath hd.HDRIMapName
				if resultHDRIMapName!=undefined then (
					hd.HDRIMapName=resultHDRIMapName
					
				)
			)
		)catch(G_OBJ_UTIL.dotnetLog (" NO_VRayHDRI"))
		
			
		try
		(
			local cams = getClassInstances VRayStereoscopic
			for cam in cams do(
				
				if  cam.enabled == true and cam.shademap_mode == 2 then(
					local resultShademapfile=G_OBJ_FILEUTIL.analysePath  cam.shademap_file
					if resultShademapfile!=undefined then (
						cam.shademap_file=resultShademapfile
					)
				)
			)
		)catch(G_OBJ_UTIL.dotnetLog ("NO_VRayStereoscopic"))
			
		try(
			local cams = getClassInstances VRayPhysicalCamera
			for cam in cams do(
				if cam.distortion_type == 2 then(
					local resultLensfile=G_OBJ_FILEUTIL.analysePath  cam.lens_file
					if resultLensfile!=undefined then (
						cam.lens_file=resultLensfile
					)
				)
			)
		)catch()

		try(
			local ies = getClassInstances VRayIES
			for i in ies do(
				local resultIesfile=G_OBJ_FILEUTIL.analysePath i.ies_file
				if resultIesfile!=undefined then (
					i.ies_file=resultIesfile
				)
				
			)
		)catch(G_OBJ_UTIL.dotnetLog ("NO_VRayIES"))
			
			
		try(
			local vrayBmpArr = getClassInstances VRayBmpFilter
			for myObj in vrayBmpArr do (
				local resultBitmapName=G_OBJ_FILEUTIL.analysePath myObj.filename
				if resultBitmapName!=undefined then (
					myObj.filename=resultBitmapName
					
				)
			)
		)catch(
			G_OBJ_UTIL.dotnetLog ("NO_VRayBmpFilter"))
		
		try(
			local allproxys = #()
			
			local vrMeshArr1=getclassinstances vrayproxy
			join allproxys vrMeshArr1
			
			try(
				local vrMeshArr2=getclassinstances CProxy
				join allproxys vrMeshArr2
			
			)catch(G_OBJ_UTIL.dotnetLog ("NO_CProxy"))
			
			for myMesh in allproxys do (
				local resultBitmapName=G_OBJ_FILEUTIL.analysePath myMesh.filename
				if resultBitmapName!=undefined then (
					myMesh.filename=resultBitmapName
					
				)
			)
		)catch(G_OBJ_UTIL.dotnetLog ("NO_vrayproxy"))
		
		try(
			local vRayVolumeGridArr=getclassinstances VRayVolumeGrid
			for volumeGrid in vRayVolumeGridArr do (
				local resultVRayVolumeGrid=G_OBJ_FILEUTIL.analysePath volumeGrid.rendinput
				if resultVRayVolumeGrid!=undefined then (
					volumeGrid.rendinput=resultVRayVolumeGrid
					volumeGrid.prv_dwnsmp = 0
					volumeGrid.usrchmap = "2,density;"
				)
				
			)
		)catch(G_OBJ_UTIL.dotnetLog ("NO_VRayVolumeGrid"))
			
		G_OBJ_UTIL.dotnetLog (" [STAsset.vrayFileFN.end]\n")
	),
	
	fn photonOption=(

        rendSaveFile=true
		G_STCON.RENDERER_OBJECT.options_dontRenderImage=true
		G_STCON.RENDERER_OBJECT.gi_irradmap_showCalcPhase=true
		
		G_STCON.RENDERER_OBJECT.gi_primary_type=G_STCON.VRAY_PRIMARY_GIENGINE as integer
		G_STCON.RENDERER_OBJECT.gi_secondary_type=G_STCON.VRAY_SECONDARY_GIENGINE as integer
		
	
				
		if G_STCON.PHOTON_DISPLACEMENT=="1" then (
			G_STCON.RENDERER_OBJECT.options_displacement=true
		)else(
			G_STCON.RENDERER_OBJECT.options_displacement=false
		)
		if G_STCON.PHOTON_REFLE_REFRA=="1" then (
			G_STCON.RENDERER_OBJECT.options_reflectionRefraction=true
		)else(
			G_STCON.RENDERER_OBJECT.options_reflectionRefraction=false
		)
		--20151001
		G_STCON.RENDERER_OBJECT.imageSampler_type=G_STCON.VRAY_IMAGE_SAMPLE_TYPE as integer
		if G_STCON.VRAY_FILTER_ON=="true" then (
			G_STCON.RENDERER_OBJECT.filter_on=true
		)else(
			G_STCON.RENDERER_OBJECT.filter_on=false
		)
		
		if G_STCON.VRAY_FILTER_KERNEL!=undefined and G_STCON.VRAY_FILTER_KERNEL!="" then (
			
			G_OBJ_UTIL.dotnetLog (" filter_kernel= "+G_STCON.VRAY_FILTER_KERNEL)
			local clientfilter=G_STCON.VRAY_FILTER_KERNEL
			if clientfilter ==	"Area"	then(	
				renderers.production.filter_kernel =	Area()
			)else if clientfilter ==	"Sharp Quadratic" 	then(	
				renderers.production.filter_kernel =	Sharp_Quadratic()
			)else if clientfilter ==	"Catmull-Rom"	then(	
				renderers.production.filter_kernel =	Catmull_Rom()
			)else if clientfilter ==	"Plate Match/MAX R2"	then(	
				renderers.production.filter_kernel =	Plate_Match_MAX_R2()
			)else if clientfilter ==	"Quadratic"	then(	
				renderers.production.filter_kernel =	Quadratic()
			)else if clientfilter ==	"cubic"	then(	
				renderers.production.filter_kernel =	cubic()
			)else if clientfilter ==	"Video"	then(	
				renderers.production.filter_kernel =	Video()
			)else if clientfilter ==	"Soften"	then(	
				renderers.production.filter_kernel =	Soften()
			)else if clientfilter ==	"Cook Variable"	then(	
				renderers.production.filter_kernel =	Cook_Variable()
			)else if clientfilter ==	"Blend"	then(	
				renderers.production.filter_kernel =	Blendfilter()
			)else if clientfilter ==	"Blackman"	then(	
				renderers.production.filter_kernel =	Blackman()
			)else if clientfilter ==	"Mitchell-Netravali"	then(	
				renderers.production.filter_kernel =	Mitchell_Netravali()
			)else if clientfilter ==	"VRayLanczosFilter" 	then(	
				renderers.production.filter_kernel =	VRayLanczosFilter()
			)else if clientfilter ==	"VRaySincFilter"	then(	
				renderers.production.filter_kernel =	VRaySincFilter()
			)else if clientfilter ==	"VRayBoxFilter"	then(	
				renderers.production.filter_kernel =	VRayBoxFilter()
			)else if clientfilter ==	"VRayTriangleFilter"	then(	
				renderers.production.filter_kernel =	VRayTriangleFilter()

			)
		)
	),
	
	fn flyThrough=(
		if G_STCON.VRAY_LIGHTCACHE_MODE=="1" or G_STCON.IS_PICTURE=="true" then (--Fly-through
			G_OBJ_UTIL.dotnetLog (" lightcache_flyThrough ")
			G_STCON.RENDERER_OBJECT.lightcache_mode=1
			G_STCON.RENDERER_OBJECT.lightcache_autoSave=true
			G_STCON.RENDERER_OBJECT.lightcache_autoSaveFileName=G_STCON.OUTPUT_PATH+G_STCON.TASK_ID+"_lightcache.vrlmap"
		)
		
	),
	
	fn flyThroughFromFile=(
		if G_STCON.VRAY_LIGHTCACHE_MODE=="1"  or G_STCON.IS_PICTURE=="true" then (--Fly-through convert to from file
			G_OBJ_UTIL.dotnetLog (" lightcache_from file ")
			G_STCON.RENDERER_OBJECT.lightcache_mode=2
			G_STCON.RENDERER_OBJECT.lightcache_loadFileName=G_STCON.PHOTON_PATH+G_STCON.TASK_ID+"_lightcache.vrlmap"
		)
		
	),
	
	fn vrayDistributeFN=(

		local oldWidth=renderWidth
		local oldHeight=renderHeight
		
		
		renderers.production.output_width = renderWidth/4
		renderers.production.output_height = renderHeight/4
		renderWidth=renderWidth/4
		renderHeight=renderHeight/4
		
		renderers.production.gi_on=True 
		renderers.production.gi_primary_type = 0
		

		G_OBJ_UTIL.dotnetLog (" [renderExecuteFN].myRenderCamera__ ")
		for c in cameras do (
			local cameraNameStr=trimright (trimleft c.name)
			G_OBJ_UTIL.dotnetLog (" [renderExecuteFN].cameraNameStr__ "+cameraNameStr)
			if (classof c)!=Targetobject and cameraNameStr==G_STCON.RENDERABLE_CAMERA then (
				try(
                    --viewport.ResetAllViews() 
                    viewport.setCamera c
					
					
					local viewId=viewport.activeViewport
	
					local viewType =viewport.getType index:viewId --viewport.getType()
					G_OBJ_UTIL.dotnetLog ("ViewPort="+(viewId as string)+"..."+(viewType as string))
                )catch()
			)
			
		)
		G_OBJ_UTIL.dotnetLog (" [renderExecuteFN].myRenderCamera... ")
		
				if DoesFileExist (renderers.production.adv_irradmap_loadFileName  as string) then
				(
					G_OBJ_UTIL.dotnetLog "irrmap is exist "
					renderers.production.adv_irradmap_mode=2
					renderers.production.adv_irradmap_autoSave=false
				)
				else
				(
					renderers.production.adv_irradmap_mode=0
					renderers.production.adv_irradmap_autoSave=true
					renderers.production.adv_irradmap_autoSaveFileName="Z:/max/"+G_STCON.TASK_ID+"_irrmap.vrmap"
				)


				if DoesFileExist (renderers.production.lightcache_loadFileName as string) then
				(
					G_OBJ_UTIL.dotnetLog "Lightcache is exist "
					renderers.production.lightcache_mode=2
					renderers.production.lightcache_autoSave=false
				)
				else
				(
					renderers.production.lightcache_mode=0
					renderers.production.lightcache_autoSave=true
					renderers.production.lightcache_autoSaveFileName="Z:/max/"+G_STCON.TASK_ID+"_lightcache.vrlmap"
				)
				
				if (DoesFileExist (renderers.production.adv_irradmap_loadFileName  as string)) and (DoesFileExist (renderers.production.lightcache_loadFileName as string)) then
				(
					G_OBJ_UTIL.dotnetLog "Not render vrmap"
				)
				else
				(
					renderers.production.options_dontRenderImage = true
						
					max quick render 
						
					for f in getFiles ((substituteString (getfilenamepath rendoutputfilename)"\\" "/")+"*.*") do deleteFile f
					
					renderers.production.options_dontRenderImage = false
				
			--renderers.production.adv_irradmap_mode=2
			--renderers.production.adv_irradmap_autoSave=false
			--renderers.production.adv_irradmap_loadFileName=G_STCON.WORK_RENDER_TASK_MAX+G_STCON.TASK_ID+"_irrmap.vrmap"		
			
			--renderers.production.lightcache_mode=2
			--renderers.production.lightcache_autoSave=false
			--renderers.production.lightcache_loadFileName=G_STCON.WORK_RENDER_TASK_MAX+G_STCON.TASK_ID+"_lightcache.vrmap"
			
					if renderers.production.adv_irradmap_autoSave==true then
					(
						renderers.production.adv_irradmap_mode=2
						renderers.production.adv_irradmap_autoSave=false
						renderers.production.adv_irradmap_loadFileName="Z:/max/"+G_STCON.TASK_ID+"_irrmap.vrmap"	
					)
					if renderers.production.lightcache_autoSave==true then
					(
						renderers.production.lightcache_mode=2
						renderers.production.lightcache_autoSave=false
						renderers.production.lightcache_loadFileName="Z:/max/"+G_STCON.TASK_ID+"_lightcache.vrlmap"
					)
				)
			renderWidth = oldWidth
			renderHeight = oldHeight
			renderers.production.output_width = oldWidth
			renderers.production.output_height = oldHeight
			
	),
	
	fn vrayFN = (
		
		G_OBJ_UTIL.dotnetLog (" [vrayFN].Start ")
		
		if G_STCON.VRAY_DISTRIBUTE!=undefined and G_STCON.VRAY_DISTRIBUTE=="true" then 
		(
			--if G_STCON.MYCURRENTTASK!=undefined and G_STCON.MYCURRENTTASK=="picture" then 
			if G_STCON.MY_ACTION!=undefined and G_STCON.MY_ACTION=="Render" then
			(
				G_STCON.RENDERER_OBJECT.system_distributedRender=true
			)
		)
		
		
		try(
				memLimit_USER = G_STCON.RENDERER_OBJECT.system_raycaster_memLimit
				if memLimit_USER<16000 then 
				(
						sysIN=sysinfo.getSystemMemoryInfo()
						s_N =((sysIN[3] /= (1024.*1024.)) as integer) as string
						sysout=(replace s_N 2 4 "0000") as integer
						if sysout > 30000 then
						(	
						G_STCON.RENDERER_OBJECT.system_raycaster_memLimit = sysout-18000
						NEW_NCs=G_STCON.RENDERER_OBJECT.system_raycaster_memLimit
						G_OBJ_UTIL.dotnetLog ("------"+"New_dynamic memory limit:"+NEW_NCs as string +"MB------")			
						)
						else
						(
						G_STCON.RENDERER_OBJECT.system_raycaster_memLimit =16000
						NEW_NC=G_STCON.RENDERER_OBJECT.system_raycaster_memLimit
						G_OBJ_UTIL.dotnetLog ("------"+"New_dynamic memory limit:"+NEW_NC as string +"MB------")

						)
				)	
				else()	
			RaytraceGlobalSettings.showMessages = false
		)catch()

		try(
			
			if G_STCON.RENDERER_OBJECT.system_region_x <= 32 then (
				G_OBJ_UTIL.dotnetLog ("------System region------48")
				G_STCON.RENDERER_OBJECT.system_region_x = G_STCON.RENDERER_OBJECT.system_region_y = 48
				G_STCON.RENDERER_OBJECT.system_region_sequence = 0
				G_STCON.RENDERER_OBJECT.system_region_meaning = 0	
			)
			
		)catch()

		G_STCON.RENDERER_OBJECT.output_width = G_STCON.MYWIDTH as integer
		G_STCON.RENDERER_OBJECT.output_height = G_STCON.MYHEIGHT as integer
		
		G_STCON.RENDERER_OBJECT.options_dontRenderImage=false
		
		if G_STCON.CUSTOM_CLIENT!=undefined and G_STCON.CUSTOM_CLIENT=="yunwu" then (
			try(
				G_STCON.RENDERER_OBJECT.camera_type=1
				G_STCON.RENDERER_OBJECT.camera_overrideFOV=true
				G_STCON.RENDERER_OBJECT.camera_fov=360.0
				
				G_STCON.RENDERER_OBJECT.camera_cyl_height=400.0
				G_STCON.RENDERER_OBJECT.camera_fish_autoDistance=true
				G_STCON.RENDERER_OBJECT.camera_fish_distance=2.0
				G_STCON.RENDERER_OBJECT.camera_fish_curve=1.0
			)catch()
		)
		
		--------------------------------vfb-----------------------------
		local enableFrameBuffer = G_STCON.RENDERER_OBJECT.output_on
		local renderToRwFile = G_STCON.RENDERER_OBJECT.output_saveRawFile			
		local splitBuffer = G_STCON.RENDERER_OBJECT.output_splitgbuffer
		if(enableFrameBuffer==true) then (--vray frame buffer
			local outputRawFile = G_STCON.RENDERER_OBJECT.output_rawFileName
			if renderToRwFile==true and outputRawFile!=undefined and outputRawFile!=""  then (					
				local outputRawFileT = getFilenameType outputRawFile
				local outputRawFileN = getFileNameFile outputRawFile
				G_STCON.RENDERER_OBJECT.output_rawFileName =G_STCON.OUTPUT_PATH + outputRawFileN + outputRawFileT
			)
				
			local splitFileName = G_STCON.RENDERER_OBJECT.output_splitfilename
			if splitBuffer==true and splitFileName!=undefined and splitFileName != "" then (					
				local splitFileT = getFilenameType splitFileName
				local splitFileN = getFileNameFile splitFileName					
				G_STCON.RENDERER_OBJECT.output_splitfilename = G_STCON.OUTPUT_PATH + splitFileN + splitFileT
				
			)
            try(
				rendShowVFB=FALSE
			)catch()
            
		)else(
			try(
				G_STCON.RENDERER_OBJECT.output_saveRawFile=false		
				G_STCON.RENDERER_OBJECT.output_splitgbuffer=false
			)catch()
            try(
				rendShowVFB=TRUE
			)catch()
		)
		
		

		if G_STCON.MYKG=="0"  then (
			
			if G_STCON.VRAY_GI=="on" or G_STCON.VRAY_GI=="true" or G_STCON.VRAY_GI=="1" then (
				G_STCON.RENDERER_OBJECT.gi_primary_type=G_STCON.VRAY_PRIMARY_GIENGINE as integer
				G_STCON.RENDERER_OBJECT.gi_secondary_type=G_STCON.VRAY_SECONDARY_GIENGINE as integer
				
				if G_STCON.VRAY_IRRADIANCEMAP_MODE!=undefined and G_STCON.VRAY_IRRADIANCEMAP_MODE!="" then (
					G_STCON.RENDERER_OBJECT.adv_irradmap_mode=G_STCON.VRAY_IRRADIANCEMAP_MODE as integer
				)
				if G_STCON.VRAY_LIGHTCACHE_MODE!=undefined and G_STCON.VRAY_LIGHTCACHE_MODE!="" then (
					G_STCON.RENDERER_OBJECT.lightcache_mode=G_STCON.VRAY_LIGHTCACHE_MODE as integer
				)
				
				if G_STCON.RENDERER_OBJECT.lightcache_mode==1 then (
					G_STCON.RENDERER_OBJECT.lightcache_autoSave=true
					G_STCON.RENDERER_OBJECT.lightcache_autoSaveFileName=G_STCON.OUTPUT_PATH+G_STCON.TASK_ID+"_lightcache.vrlmap"
				)
				
				local irrLoadFileInscenePath=G_OBJ_FILEUTIL.analysePath G_STCON.VRAY_IRRMAP_FILE
				if G_STCON.RENDER_WORK!=undefined and irrLoadFileInscenePath!=undefined then (
					G_STCON.RENDERER_OBJECT.adv_irradmap_loadFileName=G_STCON.RENDER_WORK+(filenameFromPath irrLoadFileInscenePath)
					
				)
				local ligLoadFileInscenePath=G_OBJ_FILEUTIL.analysePath G_STCON.VRAY_LIGHTCACHE_FILE
				if G_STCON.RENDER_WORK!=undefined and ligLoadFileInscenePath!=undefined then (
					G_STCON.RENDERER_OBJECT.lightcache_loadFileName=G_STCON.RENDER_WORK+(filenameFromPath ligLoadFileInscenePath)
					
				)
				
			)
			else if G_STCON.VRAY_GI=="off" or G_STCON.VRAY_GI=="false" or G_STCON.VRAY_GI=="0" then(
				G_STCON.RENDERER_OBJECT.gi_on = false
			)
			
		)else if G_STCON.MYKG=="100" then (--incremental add to current map
			G_STCON.RENDERER_OBJECT.gi_on=True 
			--if  G_STCON.MYCURRENTTASK=="photon"  then (
			if  G_STCON.MY_ACTION=="RenderPhoton"  then (
			
				G_STCON.RENDERER_OBJECT.options_dontRenderImage = true
				G_STCON.RENDERER_OBJECT.gi_irradmap_showSamples = true
				G_STCON.RENDERER_OBJECT.lightcache_showCalcPhase = 1 
				
				G_STCON.RENDERER_OBJECT.adv_irradmap_mode=4
				G_STCON.RENDERER_OBJECT.adv_irradmap_autoSave=true
				G_STCON.RENDERER_OBJECT.adv_irradmap_autoSaveFileName=G_STCON.OUTPUT_PATH+G_STCON.TASK_ID+"_irrmap.vrmap"
				
				photonOption()
				flyThrough()
				
			)else(
				G_STCON.RENDERER_OBJECT.adv_irradmap_mode=2
				G_STCON.RENDERER_OBJECT.adv_irradmap_loadFileName=G_STCON.PHOTON_PATH+G_STCON.TASK_ID+"_irrmap.vrmap"
				flyThroughFromFile()
				
			)
			
		) else if G_STCON.MYKG=="101" then (--animation (prepass) rend map
			G_STCON.RENDERER_OBJECT.gi_on=True 
			--if  G_STCON.MYCURRENTTASK=="photon"  then (
			if  G_STCON.MY_ACTION=="RenderPhoton"  then (
			
				G_STCON.RENDERER_OBJECT.options_dontRenderImage = true
				G_STCON.RENDERER_OBJECT.gi_irradmap_showSamples = true
				G_STCON.RENDERER_OBJECT.lightcache_showCalcPhase = 1 
			
				G_STCON.RENDERER_OBJECT.adv_irradmap_mode=6
				G_STCON.RENDERER_OBJECT.adv_irradmap_autoSave=true
				G_STCON.RENDERER_OBJECT.adv_irradmap_autoSaveFileName=G_STCON.OUTPUT_PATH+G_STCON.TASK_ID+"_animation.vrmap"
				
				photonOption()
				flyThrough()
			)else(
				G_STCON.RENDERER_OBJECT.adv_irradmap_mode=7
				G_STCON.RENDERER_OBJECT.adv_irradmap_loadFileName=G_STCON.PHOTON_PATH+G_STCON.TASK_ID+"_animation.vrmap"
				flyThroughFromFile()
			)
		
			
		) else if  G_STCON.MYKG=="102" then (--fast rend map
			G_STCON.RENDERER_OBJECT.gi_on=True 
			--if  G_STCON.MYCURRENTTASK=="photon"  then (
			if  G_STCON.MY_ACTION=="RenderPhoton"  then (
			
				G_STCON.RENDERER_OBJECT.options_dontRenderImage = true
				G_STCON.RENDERER_OBJECT.gi_irradmap_showSamples = true
				G_STCON.RENDERER_OBJECT.lightcache_showCalcPhase = 1 
			
				G_STCON.RENDERER_OBJECT.adv_irradmap_autoSave=true
				G_STCON.RENDERER_OBJECT.adv_irradmap_mode=4
				G_STCON.RENDERER_OBJECT.adv_irradmap_autoSaveFileName=G_STCON.OUTPUT_PATH+G_STCON.TASK_ID+"_irrmap"+ G_STCON.RENDER_FRAME_SERIAL+".vrmap"
				photonOption()
				flyThrough()
			)else(
				G_STCON.RENDERER_OBJECT.adv_irradmap_mode=2
				G_STCON.RENDERER_OBJECT.adv_irradmap_loadFileName=G_STCON.PHOTON_PATH+G_STCON.TASK_ID+"_irrmap.vrmap"
				flyThroughFromFile()
			)
		)			
		G_OBJ_UTIL.dotnetLog (" [vrayFN].End\n")
	),
	
	fn runFN = (
	
		if (G_STCON.RENDERER_STR == (vray as string)) then 
			(
				--if G_STCON.VRAY_DISTRIBUTE != undefined and G_STCON.VRAY_DISTRIBUTE =="true" and G_STCON.MYCURRENTTASK!=undefined and G_STCON.MYCURRENTTASK=="picture" then
				if G_STCON.VRAY_DISTRIBUTE != undefined and G_STCON.VRAY_DISTRIBUTE =="true" and G_STCON.MY_ACTION!=undefined and G_STCON.MY_ACTION=="Render" then
				(	
					vrayDistributeFN()
					renderers.current.system_distributedRender = true
				)
				else
				(
					vrayFileFN()
					vrayFN()
				)
			) 
		else if (G_STCON.RENDERER_STR == (default_scanline_renderer as string)) then (
			
		) else if G_STCON.RENDERER_STR == (finalRender_stage_1 as string) then (
			--finalRenderFN()
		) else if (G_STCON.RENDERER_STR == (MaxwellRenderer as string)) then (
			
		) else if (G_STCON.RENDERER_STR == (mental_ray_renderer as string)) then (
			
		) else if (G_STCON.RENDERER_STR == (mental_ray_iray_Renderer as string)) then (
			
		) else if (G_STCON.RENDERER_STR == (Quicksilver_Hardware_Renderer as string)) then (
			
		) 
	)
)
G_Vray = STVray()


struct STRedshift(
	
	fn rspRoxyFN=(
		G_OBJ_UTIL.dotnetLog (" [RsproxyFN].Start ")
		try(
			local rsproxy = getclassinstances proxy
			for a in rsproxy do (
				
				local oldissequence = a.issequence
				local oldstartframe = a.startframe
				local oldendframe = a.endframe
				
				local resultrsproxy=G_OBJ_FILEUTIL.analysePath a.file
				if resultrsproxy!=undefined  then 
				(
					a.file = resultrsproxy
				)
				
				a.issequence = oldissequence
				a.startframe = oldstartframe
				a.endframe = oldendframe
			
			)
		)catch()
		G_OBJ_UTIL.dotnetLog (" [RsproxyFN].End\n")
	),
	
	fn runFN =(
		
		rspRoxyFN()
	)

)
G_Redshift = STRedshift()


struct STRenderer(

	fn setRenderer =(
		
		if (classof renderers.production) == vray then
		(
			G_Vray.runFN()
		)
		else if (classof renderers.production) == Redshift_Renderer then
		(
			G_Redshift.runFN()
		)
		else()
	),
	
	fn runFN = (
		
		setRenderer()
		
	)
)
G_STRenderer = STRenderer()