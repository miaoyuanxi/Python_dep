struct STRender(
	
	fn cpuSet=(
        try(
            local cpuCount = SysInfo.CPUCount
            G_OBJ_UTIL.dotnetLog ( "cpuCount="+(cpuCount as string))
            local TargetAffinity=0
            local targetAffinity = 0
            for coreID = 2 to SysInfo.CPUCount do(
                targetAffinity = (Bit.Set targetAffinity coreID true)
            )
            SysInfo.ProcessAffinity = targetAffinity
        )catch()
		
		try(
			sysInfo.MAXPriority=#low
		)catch()
	),
	
	fn renderExecuteFN=(
		
		G_OBJ_UTIL.dotnetLog (" [renderExecuteFN].Start ")

		local elemArr=#()
		
		
		global myRenderCamera=undefined
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
                myRenderCamera=c
			)
			
		)
		G_OBJ_UTIL.dotnetLog (" [renderExecuteFN].myRenderCamera... "+(myRenderCamera as string))
		
		local renderCmd="render quiet:true    outputwidth:(G_STCON.MYWIDTH as number) outputheight:(G_STCON.MYHEIGHT as number) outputfile:G_STCON.OUTPUT_SERIAL_FILE "
		
		-----------frame
		if G_STCON.RENDER_FRAME_START==G_STCON.RENDER_FRAME_END then
		(
			renderCmd=renderCmd+" frame:(G_STCON.RENDER_FRAME as time) "
			try(-----------sliderTime
				sliderTime=(G_STCON.RENDER_FRAME as time)
			)catch()
		)
		else
		(
			renderCmd=renderCmd+" fromframe:(G_STCON.RENDER_FRAME_START as time)  toframe:(G_STCON.RENDER_FRAME_END as time)  nthframe:(G_STCON.RENDER_FRAME_BY as time) "
		)

		-----------camera
		if myRenderCamera!=undefined then (
			renderCmd=renderCmd+" camera:myRenderCamera"
		)
		
		G_OBJ_UTIL.dotnetLog (" [renderExecuteFN].RenderType... "+(getRenderType() as string))
		local myRenderType=toLower (getRenderType() as string)
		----------------block
		if G_STCON.TOTAL_BLOCK>1 then(
			calcRegion()
			renderCmd=renderCmd+" renderType:#regionCrop region:G_STCON.REGION_ARR "
		)else(
			
			if myRenderType=="region" then (
				renderCmd=renderCmd+" renderType:#region "
			)else if myRenderType =="selected" then(
				renderCmd=renderCmd+" renderType:#selected "
			)
			else if myRenderType =="selection" then (
				renderCmd=renderCmd+" renderType:#selection "
			)else if myRenderType =="blowup" then (
				renderCmd=renderCmd+" renderType:#blowup "
			)else if myRenderType =="crop" then (
				renderCmd=renderCmd+" renderType:#crop "
			)
		)
		-----------elements
		--if (G_STCON.MYKG=="100" or G_STCON.MYKG=="101" or G_STCON.MYKG=="102" ) and G_STCON.MYCURRENTTASK=="photon" then (--incremental add to current map
		if (G_STCON.MYKG=="100" or G_STCON.MYKG=="101" or G_STCON.MYKG=="102" ) and G_STCON.MY_ACTION=="RenderPhoton" then (--incremental add to current map
			
		)else()
		
		
		if G_STCON.USER_ID=="961404"  then (
			renderCmd=renderCmd+" outputHDRbitmap:true "
		)

		G_OBJ_UTIL.dotnetLog (" [renderExecuteFN].rendercmd___"+renderCmd)
		if G_STCON.NOT_RENDER=="true" then (
			
		)else(
			execute(renderCmd)
		)
		
		G_OBJ_UTIL.dotnetLog (" [renderExecuteFN].End\n")
		
		if (maxversion())[1] < 16000 then(--2013,2012,2011,2010

			if not (matchPattern G_STCON.OUTPUT_NAME pattern:"*.tif" ignoreCase:true) then (
			
				if G_STCON.MAX_GAMMA!=undefined and G_STCON.MAX_GAMMA=="on" and G_STCON.MAX_OUTGAMMA!=undefined then (
					G_OBJ_UTIL.dotnetLog (" [renderExecuteFN].gammaStart ")
					try(
						G_OBJ_UTIL.dotnetLog (" [renderExecuteFN].setgamma")
						local bm=openBitMap G_STCON.OUTPUT_SERIAL_FILE
						local bmm = copy bm
						bmm.filename=G_STCON.OUTPUT_SERIAL_FILE
						bmm.gamma=G_STCON.MAX_OUTGAMMA as float
						save bmm
					)catch(
						G_OBJ_UTIL.dotnetLog (getcurrentException() as string)	
					)
					G_OBJ_UTIL.dotnetLog (" [renderExecuteFN].GammaEnd ")
				)
			)
		)		
	),
	
	fn maxQuickRenderFn=(
		
		G_OBJ_UTIL.dotnetLog (" [maxQuickRenderFn].Start ")

		
		----------------------camera----------------------
		global myRenderCamera=undefined
		G_OBJ_UTIL.dotnetLog (" [maxQuickRenderFn].myRenderCamera__ ")
		for c in cameras do (
			local cameraNameStr=trimright (trimleft c.name)
			G_OBJ_UTIL.dotnetLog (" [maxQuickRenderFn].cameraNameStr__ "+cameraNameStr)
			if (classof c)!=Targetobject and cameraNameStr==G_STCON.RENDERABLE_CAMERA then (
				try(
                    --viewport.ResetAllViews() 
                    viewport.setCamera c
					
					
					local viewId=viewport.activeViewport
	
					local viewType =viewport.getType index:viewId --viewport.getType()
					G_OBJ_UTIL.dotnetLog ("ViewPort="+(viewId as string)+"..."+(viewType as string))
                )catch()
                myRenderCamera=c
			)
			
		)
		G_OBJ_UTIL.dotnetLog (" [maxQuickRenderFn].myRenderCamera... "+(myRenderCamera as string))
		
		----------------------frame----------------------
		if (findString G_STCON.RENDER_FRAME ",") != undefined then(
			rendTimeType = 4
			rendSaveFile=true
			--rendOutputFilename = ""
			rendPickupFrames=G_STCON.RENDER_FRAME as string
		)else(
			if G_STCON.RENDER_FRAME_START==G_STCON.RENDER_FRAME_END then(
				rendTimeType = 1 
				try(-----------sliderTime
					sliderTime=(G_STCON.RENDER_FRAME as time)
				)catch()
			)else(
				rendTimeType = 3 
				rendSaveFile=true
				rendNThFrame=G_STCON.RENDER_FRAME_BY as integer
				rendStart=G_STCON.RENDER_FRAME_START as integer
				rendEnd=G_STCON.RENDER_FRAME_END as integer
			)
		)
		sleep 1
        if G_STCON.NOT_RENDER=="true" then (
			
		)else(
            renderSceneDialog.open()
            renderSceneDialog.commit()
            if (maxversion())[1] < 17000 then(
                try(
                    renderSceneDialog.update()
                )catch()
            )
            renderSceneDialog.close()
			
			
			
		
			rendTimeType = 1
			rendSaveFile=true
			rendStart=G_STCON.RENDER_FRAME_START as integer
			rendEnd=G_STCON.RENDER_FRAME_END as integer
			for renderNowFrame = (G_STCON.RENDER_FRAME_START as integer) to (G_STCON.RENDER_FRAME_END as integer) by (G_STCON.RENDER_FRAME_BY as integer) do(
				G_OBJ_UTIL.dotnetLog ("[maxQuickRenderFn].renderNowFrame... "+(renderNowFrame as string))
				local now_frame_serial = G_OBJ_UTIL.fillLeftZero renderNowFrame 4
				local output_frame_path = G_STCON.OUTPUT_PATH+now_frame_serial+"/"
                if not doesFileExist output_frame_path then (
                    makeDir output_frame_path all:true
                )
				local now_serial_file=output_frame_path +(getfilenamefile G_STCON.OUTPUT_NAME)+now_frame_serial+(getfilenametype G_STCON.OUTPUT_NAME)
				--local imageInfoArr=getImageInfo()
				rendSaveFile=true
				
				if   G_STCON.MAX_QUICK_RENDER  then(
					
					rendOutputFilename=now_serial_file
				)else(
					rendOutputFilename=G_STCON.OUTPUT_FILE
				)
		
		
		
				try(
					sliderTime = renderNowFrame as time
				)catch()
				max quick render
				G_OBJ_UTIL.dotnetLog ("[_____render end_____][" + (renderNowFrame as string) + "]")
			)
		)
	),
	
    fn bakeRenders=(
		G_OBJ_UTIL.dotnetLog ("\n\n-------------------[Render to Texture]-------------------\n")
		local Allgeo =  filterString G_STCON.BAKERENDERID "," 
		select (maxOps.getNodeByHandle (Allgeo[G_STCON.RENDER_FRAME_START as integer] as integer))
		G_OBJ_UTIL.dotnetLog ("___Geoname::"+($.name as string) +"    Modcount::"+ ($.modifiers.count as string))
			for  i = 1 to $.NumBakeElements() do 
				(
					local enname = $.GetBakeElement i
					format "%__%\n" enname (classof enmame as string)
					local newPath=G_STCON.OUTPUT_PATH +(getfilenamefile enname.filename)+(getfilenametype G_STCON.OUTPUT_NAME)
					local filetype= G_STCON.OUTPUT_PATH +(getfilenamefile enname.filename)+(getfilenametype G_STCON.OUTPUT_NAME)
					format "newPath.....%\n" newPath
					enname.filename = (getfilenamefile enname.filename)+(getfilenametype G_STCON.OUTPUT_NAME)
					enname.filetype = newPath
					renderWidth  = enname.outputSzX as integer
					renderHeight = enname.outputSzY as integer
				)
			render rendertype:#bakeselected
    ),
	
	fn custombakeRenders=(
		G_OBJ_UTIL.dotnetLog ("\n\n-------------------[Custom_Render to Texture]-------------------\n")
		max select all
		G_OBJ_UTIL.dotnetLog ("___ALLselectGeo::"+$.count as string)		
		select selection[G_STCON.RENDER_FRAME_START as integer]
		G_OBJ_UTIL.dotnetLog ("___Geoname::"+($.name as string) +"    Modcount::"+ ($.modifiers.count as string))
		for  i = 1 to $.NumBakeElements() do 
			(
				local enname = $.GetBakeElement i
				format "%__%\n" enname (classof enmame as string)
				local newPath=G_STCON.OUTPUT_PATH +(getfilenamefile enname.filename)+(getfilenametype G_STCON.OUTPUT_NAME)
				local filetype= G_STCON.OUTPUT_PATH +(getfilenamefile enname.filename)+(getfilenametype G_STCON.OUTPUT_NAME)
				format "newPath.....%\n" newPath
				enname.filename = (getfilenamefile enname.filename)+(getfilenametype G_STCON.OUTPUT_NAME)
				enname.filetype = newPath
				renderWidth  = enname.outputSzX as integer
				renderHeight = enname.outputSzY as integer
			)
		render rendertype:#bakeselected
    ),	
	
	fn runFN=(
		
		G_OBJ_UTIL.dotnetLog (" [runFN].Start ")
		
			cpuSet()
			
			if G_STCON.IS_BAKERENDER == "true" then
			(
				bakeRenders()
			)
			else
			(
				if (G_STCON.USER_ID=="1821496" or G_STCON.USER_ID=="1819964" or G_STCON.USER_ID=="1840720" or G_STCON.USER_ID=="1844686") and (getRenderType() == #selected) then
				(
				   custombakeRenders()
				)
				else
				(
					if  G_STCON.MAX_QUICK_RENDER  then 
					(
						G_OBJ_UTIL.dotnetLog ("\n\n-------------------[[Start Max Quick Render]-------------------\n")
						renderSceneDialog.open()
						renderSceneDialog.commit()
						if (maxversion())[1] < 17000 then(
							try(
								renderSceneDialog.update()
							)catch()
						)
						
						renderSceneDialog.close()
						maxQuickRenderFn()
					)
					else
					(
						renderExecuteFN()
					)
				)
			)	

		
		G_OBJ_UTIL.dotnetLog (" [runFN].End \n")
	)

)
G_STRender = STRender()
