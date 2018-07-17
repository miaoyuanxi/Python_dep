struct STCommon(
	
	fn commonFN=(--run after load max file
		G_OBJ_UTIL.dotnetLog (" [commonFN].Start ")

		renderWidth = G_STCON.MYWIDTH as integer
		renderHeight= G_STCON.MYHEIGHT as integer
		
		try(
			G_OBJ_UTIL.dotnetLog (" [commonFN].BitmapProxyMgr.start ")
		
			BitmapProxyMgr.globalProxyEnable=false
			G_OBJ_UTIL.dotnetLog (" [commonFN].BitmapProxyMgr.end\n")
		
		)catch(
			G_OBJ_UTIL.dotnetLog (" [commonFN].BitmapProxyMgrexception ")
			G_OBJ_UTIL.dotnetLog (getcurrentexception() as string)
		)
		
		try(
			G_OBJ_UTIL.dotnetLog (" [commonFN].IBitmapPager.start ")
		
			IBitmapPager.enabled=false
			G_OBJ_UTIL.dotnetLog (" [commonFN].IBitmapPager.end\n")
		
		)catch(
			G_OBJ_UTIL.dotnetLog (" [commonFN].IBitmapPagerexception ")
			G_OBJ_UTIL.dotnetLog (getcurrentexception() as string)
		)
		
		G_OBJ_UTIL.dotnetLog (" [commonFN].End\n")
		

	),
			
	fn getMyCamera=(
		
		local myCamera = getActiveCamera()
		local renderView
		try(
			if (rendUseActiveView) then ( 
				renderView = viewport.activeViewport 
			)else ( 
				renderView = rendViewIndex 
			)
			myCamera =  (viewport.getCamera index:renderView)
			G_STCON.ACTIVE_CAMERA=myCamera
			G_OBJ_UTIL.dotnetLog (" [getMyCamera]G_STCON.ACTIVE_CAMERA="+G_STCON.ACTIVE_CAMERA)
		)catch()
		
		myCamera
	),
	
	fn getImageInfo=(
		local imageInfoArr = #()
		
		local rendOutputFilenameTemp=rendOutputFilename
		if rendOutputFilenameTemp!=undefined and rendOutputFilenameTemp!="" then(
			
			local outputTypeScene=getFilenametype rendOutputFilenameTemp
			local outputTypeRender=getFilenametype G_STCON.OUTPUT_NAME
			G_OBJ_UTIL.dotnetLog ("outputTypeScene="+outputTypeScene)
			G_OBJ_UTIL.dotnetLog ("outputTypeRender="+outputTypeRender)
			if outputTypeScene==outputTypeRender then (
				
				try(
					imageInfoArr=getBitmapInfoRayvision()
				
				)catch(G_OBJ_UTIL.dotnetLog (" [setImageInfo]_get output file info failed"))
				
				G_OBJ_UTIL.dotnetLog  ("imageInfoArr___"+ (imageInfoArr as string))
			)
		)
		imageInfoArr
	),

    fn setImageInfo imageInfoArr=(
		G_OBJ_UTIL.dotnetLog ("-----get output file info-----")
		

		
		G_OBJ_UTIL.dotnetLog ("-----set output file info-----")
		if imageInfoArr!=undefined and imageInfoArr.count>0 then (
			
			if imageInfoArr[1]=="type:jpg" then (
				for imageInfo in imageInfoArr do (
					if imageInfo!=undefined and matchPattern imageInfo pattern:"quality:*" ignoreCase:true then (
						local myQuality = (substring imageInfo 9 -1) as integer
						jpeg.setQuality myQuality
						G_OBJ_UTIL.dotnetLog  ("[setImageInfo]setQuality..."+myQuality as string)
					)else if imageInfo!=undefined and matchPattern imageInfo pattern:"smooth:*" ignoreCase:true then (
						local mySmooth = (substring imageInfo 8 -1) as integer
						jpeg.setSmoothing mySmooth
						G_OBJ_UTIL.dotnetLog  ("[setImageInfo]setSmoothing..."+mySmooth as string)
					)
				)
			)else if imageInfoArr[1]=="type:bmp" then (
				for imageInfo in imageInfoArr do (
					if imageInfo!=undefined and  imageInfo=="colors:2" then (
						bmp.setType #paletted
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]BMP_setTyp 8 Bit Optimized palette"
					)else if imageInfo!=undefined and  imageInfo=="colors:8" then (
						bmp.setType #true24
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]BMP_setTyp RGB 24 bit"
					)
				)
			)else if imageInfoArr[1]=="type:png" then (
				for imageInfo in imageInfoArr do (
					if imageInfo!=undefined and  imageInfo=="colors:2" then (
						pngio.setType #paletted
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]PNG_colors Optimized palette(256)"
					)else if imageInfo!=undefined and  imageInfo=="colors:8" then (
						pngio.setType #true24
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]PNG_colors RGB 24bit(16.7Million)"
					)else if imageInfo!=undefined and  imageInfo=="colors:9" then (
						pngio.setType #true48
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]PNG_colors RGB 48 bit(281 Trillion)"
					)else if imageInfo!=undefined and  imageInfo=="colors:3" then (
						pngio.setType #gray8
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]PNG_colors Grayscale 8 bit (256)"
					)else if imageInfo!=undefined and  imageInfo=="colors:4" then (
						pngio.setType #gray16
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]PNG_colors Grayscale 16 bit (65,536)"
					)else if imageInfo!=undefined and  imageInfo=="alphachannel:1" then (
						pngio.setAlpha true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]setAlpha_true..." 
					)else if imageInfo!=undefined and  imageInfo=="alphachannel:0" then (
						pngio.setAlpha false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]setAlpha_false..." 
					)else if imageInfo!=undefined and  imageInfo=="interlaced:1" then (
						pngio.setInterlaced true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]setInterlaced_true..." 
					)else if imageInfo!=undefined and  imageInfo=="interlaced:0" then (
						pngio.setInterlaced false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]setInterlaced_false..." 
					)
				)
			)else if imageInfoArr[1]=="type:rla" then (
				for imageInfo in imageInfoArr do (
					if imageInfo!=undefined and  imageInfo=="bitsperchannel:0" then (
						rla.colorDepth =8
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA.Bits per channel 8"
					)else if imageInfo!=undefined and  imageInfo=="bitsperchannel:1" then (
						rla.colorDepth =16
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA.Bits per channel 16"
					)else if imageInfo!=undefined and  imageInfo=="bitsperchannel:2" then (
						rla.colorDepth =32
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA.Bits per channel 32"
					)else if imageInfo!=undefined and  imageInfo=="storealphachannel:0" then (
						rla.alpha =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA.storealphachannel false"
					)else if imageInfo!=undefined and  imageInfo=="storealphachannel:1" then (
						rla.alpha =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA.storealphachannel true"
					)else if imageInfo!=undefined and  imageInfo=="premultalpha:0" then (
						rla.premultAlpha =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA_premultAlpha false"
					)else if imageInfo!=undefined and  imageInfo=="premultalpha:1" then (
						rla.premultAlpha =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA_premultAlpha true"
					)else if imageInfo!=undefined and  imageInfo=="zchannel:0" then (
						rla.zChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA_ZChannel false"
					)else if imageInfo!=undefined and  imageInfo=="zchannel:1" then (
						rla.zChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA_ZChannel true"
					)else if imageInfo!=undefined and  imageInfo=="mtlidchannel:0" then (
						rla.mtlIDChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA_MtlIDChannel false"
					)else if imageInfo!=undefined and  imageInfo=="mtlidchannel:1" then (
						rla.mtlIDChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA_MtlIDChannel true"
					)else if imageInfo!=undefined and  imageInfo=="objectidchannel:0" then (
						rla.nodeIDChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA_ObjectChannel false"
					)else if imageInfo!=undefined and  imageInfo=="objectidchannel:1" then (
						rla.nodeIDChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA_ObjectChannel true"
					)else if imageInfo!=undefined and  imageInfo=="uvchannel:0" then (
						rla.uvChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA.UVChannel false"
					)else if imageInfo!=undefined and  imageInfo=="uvchannel:1" then (
						rla.uvChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA.UVChannel true"
					)else if imageInfo!=undefined and  imageInfo=="normalchannel:0" then (
						rla.normalChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA.NormalChannel false"
					)else if imageInfo!=undefined and  imageInfo=="normalchannel:1" then (
						rla.normalChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA.NormalChannel true"
					)else if imageInfo!=undefined and  imageInfo=="non-clampedchannel:0" then (
						rla.realpixChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA.Non-ClampedChannel false"
					)else if imageInfo!=undefined and  imageInfo=="non-clampedchannel:1" then (
						rla.realpixChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA.Non-ClampedChannel true"
					)else if imageInfo!=undefined and  imageInfo=="coveragechannel:0" then (
						rla.coverageChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA.coveragechannel false"
					)else if imageInfo!=undefined and  imageInfo=="coveragechannel:1" then (
						rla.coverageChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RLA.coveragechannel true"
					)
				)
			)else if imageInfoArr[1]=="type:tga" then (
				for imageInfo in imageInfoArr do (
					if imageInfo!=undefined and  imageInfo=="bitsperpixel:0" then (
						Targa.setColorDepth 16
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]TGA.Image bitsperpixel 16"
					)else if imageInfo!=undefined and  imageInfo=="bitsperpixel:1" then (
						Targa.setColorDepth 24
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]TGA.Image bitsperpixel 24"
					)else if imageInfo!=undefined and  imageInfo=="bitsperpixel:2" then (
						Targa.setColorDepth 32
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]TGA.Image bitsperpixel 32"
					)else if imageInfo!=undefined and  imageInfo=="compressed:0" then (
						Targa.setCompressed false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]TGA.compressed false"
					)else if imageInfo!=undefined and  imageInfo=="compressed:1" then (
						Targa.setCompressed true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]TGA.compressed true"
					)else if imageInfo!=undefined and  imageInfo=="alphasplit:0" then (
						Targa.setAlphaSplit false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]TGA.alphaSplit false"
					)else if imageInfo!=undefined and  imageInfo=="alphasplit:1" then (
						Targa.setAlphaSplit true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]TGA.alphaSplit true"
					)else if imageInfo!=undefined and  imageInfo=="premultalpha:0" then (
						Targa.setPreMultAlpha false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]TGA.preMultAlpha false"
					)else if imageInfo!=undefined and  imageInfo=="premultalpha:1" then (
						Targa.setPreMultAlpha true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]TGA.preMultAlpha true"
					)
				)
			)else if imageInfoArr[1]=="type:tif" then (
				for imageInfo in imageInfoArr do (
					if imageInfo!=undefined and  imageInfo=="imagetype:0" then (
						TIF.setType #mono
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]TIF.imagetype 8-bit Greyscale"
					)else if imageInfo!=undefined and  imageInfo=="imagetype:1" then (
						TIF.setType #color
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]TIF.imagetype 8-bit Color"
					)else if imageInfo!=undefined and  imageInfo=="imagetype:2" then (
						TIF.setType #logL
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]TIF.imagetype 16-bit Color"
					)else if imageInfo!=undefined and  imageInfo=="imagetype:3" then (
						TIF.setType #logLUV
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]TIF.imagetype 16-bit SGI Logl"
					)else if imageInfo!=undefined and  imageInfo=="imagetype:4" then (
						TIF.setType #color16
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]TIF.imagetype 32-bit SGI LogLUV"
					)else if imageInfo!=undefined and  imageInfo=="compressiontype:0" then (
						TIF.setCompression #none
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]TIF.Compression Type No Compression"
					)else if imageInfo!=undefined and  imageInfo=="compressiontype:1" then (
						TIF.setCompression #packBits
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]TIF.Compression Type PackBits"
					)else if imageInfo!=undefined and  imageInfo=="storealphachannel:0" then (
						TIF.setAlpha #false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]TIF.storealphachannel 0"
					)else if imageInfo!=undefined and  imageInfo=="storealphachannel:1" then (
						TIF.setAlpha #true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]TIF.storealphachannel 1"
					)else if imageInfo!=undefined and  (matchpattern imageInfo pattern:"dotsperinch:*" ignoreCase:true) then (
						local dotsperinch = (substring imageInfo 13 -1) as float
						TIF.setDPI dotsperinch
						G_OBJ_UTIL.dotnetLog  ("[setImageInfo]TIF. "+ dotsperinch as string)
					)
				)
			)else if imageInfoArr[1]=="type:rpf" then (
				for imageInfo in imageInfoArr do (
					if imageInfo!=undefined and  imageInfo=="bitsperchannel:0" then (
						rpf.colorDepth =8
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]rpf.Bits per channel 8"
					)else if imageInfo!=undefined and  imageInfo=="bitsperchannel:1" then (
						rpf.colorDepth =16
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.Bits per channel 16"
					)else if imageInfo!=undefined and  imageInfo=="bitsperchannel:2" then (
						rpf.colorDepth =32
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.Bits per channel 32"
					)else if imageInfo!=undefined and  imageInfo=="storealphachannel:0" then (
						rpf.alpha =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.StoreAlphaChannel false"
					)else if imageInfo!=undefined and  imageInfo=="storealphachannel:1" then (
						rpf.alpha =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.StoreAlphaChannel true"
					)else if imageInfo!=undefined and  imageInfo=="premultalpha:0" then (
						rpf.premultAlpha =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.premultalpha false"
					)else if imageInfo!=undefined and  imageInfo=="premultalpha:1" then (
						rpf.premultAlpha =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.premultalpha true"
					)else if imageInfo!=undefined and  imageInfo=="zchannel:0" then (
						rpf.zChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.zchannel false"
					)else if imageInfo!=undefined and  imageInfo=="zchannel:1" then (
						rpf.zChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.zchannel true"
					)else if imageInfo!=undefined and  imageInfo=="mtlidchannel:0" then (
						rpf.mtlIDChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.mtlidchannel false"
					)else if imageInfo!=undefined and  imageInfo=="mtlidchannel:1" then (
						rpf.mtlIDChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.mtlidchannel true"
					)else if imageInfo!=undefined and  imageInfo=="objectidchannel:0" then (
						rpf.nodeIDChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.objectidchannel false"
					)else if imageInfo!=undefined and  imageInfo=="objectidchannel:1" then (
						rpf.nodeIDChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.objectidchannel true"
					)else if imageInfo!=undefined and  imageInfo=="uvchannel:0" then (
						rpf.uvChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.uvchannel false"
					)else if imageInfo!=undefined and  imageInfo=="uvchannel:1" then (
						rpf.uvChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.uvchannel true"
					)else if imageInfo!=undefined and  imageInfo=="normalchannel:0" then (
						rpf.normalChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.normalchannel false"
					)else if imageInfo!=undefined and  imageInfo=="normalchannel:1" then (
						rpf.normalChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.normalchannel true"
					)else if imageInfo!=undefined and  imageInfo=="non-clampedchannel:0" then (
						rpf.realpixChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.non-clampedchannel false"
					)else if imageInfo!=undefined and  imageInfo=="non-clampedchannel:1" then (
						rpf.realpixChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.non-clampedchannel true"
					)else if imageInfo!=undefined and  imageInfo=="coveragechannel:0" then (
						rpf.coverageChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.coveragechannel false"
					)else if imageInfo!=undefined and  imageInfo=="coveragechannel:1" then (
						rpf.coverageChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.coveragechannel true"
					)else if imageInfo!=undefined and  imageInfo=="noderenderidchannel:0" then (
						rpf.nodeRenderIDChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.noderenderidchannel false"
					)else if imageInfo!=undefined and  imageInfo=="noderenderidchannel:1" then (
						rpf.nodeRenderIDChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.noderenderidchannel true"
					)else if imageInfo!=undefined and  imageInfo=="colorchannel:0" then (
						rpf.colorChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.colorchannel false"
					)else if imageInfo!=undefined and  imageInfo=="colorchannel:1" then (
						rpf.colorChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.colorchannel true"
					)else if imageInfo!=undefined and  imageInfo=="transpchannel:0" then (
						rpf.transpChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.transpchannel false"
					)else if imageInfo!=undefined and  imageInfo=="transpchannel:1" then (
						rpf.transpChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.transpchannel true"
					)else if imageInfo!=undefined and  imageInfo=="velocchannel:0" then (
						rpf.velocChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.velocchannel false"
					)else if imageInfo!=undefined and  imageInfo=="velocchannel:1" then (
						rpf.velocChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.velocchannel true"
					)else if imageInfo!=undefined and  imageInfo=="weightchannel:0" then (
						rpf.weightChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.weightchannel false"
					)else if imageInfo!=undefined and  imageInfo=="weightchannel:1" then (
						rpf.weightChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.weightchannel true"
					)else if imageInfo!=undefined and  imageInfo=="maskchannel:0" then (
						rpf.maskChannel =false
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.maskchannel false"
					)else if imageInfo!=undefined and  imageInfo=="maskchannel:1" then (
						rpf.maskChannel =true
						G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.maskchannel true"
					)
				)
			)else if imageInfoArr[1]=="type:exr" then (
				
			)
		
		)
		
		
		
		
		if G_STCON.USER_ID=="1301008" then (
			try(
				G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.custom.1301008"
				rpf.colorDepth =16
				rpf.nodeIDChannel =true
				rpf.zChannel =true
			)catch(
				G_OBJ_UTIL.dotnetLog  "[setImageInfo]RPF.custom.1301008__exception"
			)
		)
		
		
	),
	
	fn setMaxOutputNameFN =(
		G_OBJ_UTIL.dotnetLog (" [setMaxOutputNameFN].Start ")
		

		G_STCON.OUTPUT_FILE = (G_STCON.OUTPUT_PATH +G_STCON.OUTPUT_NAME)
		
		G_STCON.OUTPUT_SERIAL_FILE=G_STCON.OUTPUT_PATH +(getfilenamefile G_STCON.OUTPUT_NAME)+G_STCON.RENDER_FRAME_SERIAL+(getfilenametype G_STCON.OUTPUT_NAME)
		
		
		local imageInfoArr=getImageInfo()
		
		rendSaveFile=true
        if   G_STCON.MAX_QUICK_RENDER  then(
			
			rendOutputFilename=G_STCON.OUTPUT_SERIAL_FILE
		)else(
            rendOutputFilename=G_STCON.OUTPUT_FILE
        )
		
		setImageInfo imageInfoArr
		
		
		if G_STCON.USER_ID=="964684" or G_STCON.USER_ID=="962712"  then 
			(
				G_OBJ_UTIL.dotnetLog (" [run].customScript ")
				if matchPattern G_STCON.OUTPUT_NAME pattern:"*.exr" then 
				(
					G_OBJ_UTIL.dotnetLog (" [runFN].Exr")
					fopenexr.setLayerOutputFormat 0 1
					fopenexr.setLayerOutputType 0 0 
					fopenexr.SetCompression 3
					fopenexr.setSaveScanline true
					fopenexr.setSaveRegion false

					fopenexr.delAllGBufferLayers()
					fopenexr.addGBufferChannelLayer 0 "zDepth" 2 1
					fopenexr.addGBufferChannelLayer 11 "Velocity" 3 1
				
				
					G_OBJ_UTIL.dotnetLog (" [runFN].Exr_setAutoAddRenderElements ")
					fopenexr.setAutoAddRenderElements true
				)
			) 
		else
			(
				if matchPattern G_STCON.OUTPUT_NAME pattern:"*.exr" and G_STCON.TOTAL_BLOCK==1 then
				(
					G_OBJ_UTIL.dotnetLog (" [run].customScript _Set up EXR to a file")
					fopenexr.setAutoAddRenderElements true
					rendOutputFilename = rendOutputFilename
				)
				
				if matchPattern G_STCON.OUTPUT_NAME pattern:"*.rpf" and G_STCON.TOTAL_BLOCK==1 then
				(
					G_OBJ_UTIL.dotnetLog (" [run].customScript _Set up RPF to a file")
					rpf.colorDepth =16
					rpf.nodeIDChannel =true
					rpf.zChannel =true
					rendOutputFilename = rendOutputFilename
				)
			)
		
		G_OBJ_UTIL.dotnetLog (" [setMaxOutputNameFN].G_STCON.OUTPUT_FILE="+G_STCON.OUTPUT_FILE)
		G_OBJ_UTIL.dotnetLog (" [setMaxOutputNameFN].End\n")
		outPath
	),
	
	fn elementFN =(
		G_OBJ_UTIL.dotnetLog (" [elementFN].Start ")
		
		if G_STCON.ELEM_TYPE==undefined or G_STCON.ELEM_TYPE=="" then (
			G_STCON.ELEM_TYPE="tga"
		)
		re = maxOps.GetCurRenderElementMgr() 
		theManager = maxOps.GetRenderElementMgr #Production
		theManager.SetDisplayElements false
		--20151001
		if G_STCON.MY_ACTION=="Render" then(
			if G_STCON.ELEMENT_ACTIVE=="on" or G_STCON.ELEMENT_ACTIVE=="true" or G_STCON.ELEMENT_ACTIVE=="1" then(
				re.SetElementsActive true
				for n = 0 to (theManager.numrenderelements()- 1) do(
				
					local el = re.getrenderelement n	
					if (classof el as string) != "Missing_Render_Element_Plug_in" then(
						el.enabled=true
						local elName = re.GetRenderElementFilename n
						local elType = el.elementname
						
						local resultName = ""
						if elName==undefined or elName=="" then(				
							resultName = elType+"_"+G_STCON.RENDER_FRAME_SERIAL+"."+G_STCON.ELEM_TYPE
						)else(	
							local elBasename = getFilenameFile elname
							resultName = elBasename +"_"+G_STCON.RENDER_FRAME_SERIAL+ "."+G_STCON.ELEM_TYPE
						)
						if (getfilenametype resultName) != ".png" then
						(
							re.SetRenderElementFilename n (G_STCON.OUTPUT_PATH + resultName )
						)
						else
						(
							re.SetRenderElementFilename n (G_STCON.OUTPUT_PATH + (getfilenamefile resultName)as string +".tga" )
							G_OBJ_UTIL.dotnetLog (" Convert PNG to TGA ")
						)
					)
				)
			)else(
				re.SetElementsActive false
			)
		)else(
			re.SetElementsActive false
			renderers.production.output_on = false
		)

		G_OBJ_UTIL.dotnetLog (" [elementFN].End\n")
	),
	
	fn runFN = (
		
		commonFN()
		getMyCamera()
		setMaxOutputNameFN()
		elementFN()
	)

)
G_STCommon = STCommon()
