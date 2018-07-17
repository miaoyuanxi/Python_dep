struct STLoadMax(
	
	fn loadMaxFN=(
		G_OBJ_UTIL.dotnetLog (" [loadMaxFN].Start ")
		
		DialogMonitorOPS.unRegisterNotification id:#RB_Monitor_Dialog 
		DialogMonitorOPS.RegisterNotification RB_MontiorDialog id:#RB_Monitor_Dialog
		DialogMonitorOPS.Enabled = true
		
		G_OBJ_UTIL.dotnetLog G_STCON.MAXFILE
		local loadResult = loadMaxFile G_STCON.MAXFILE useFileUnits:true quiet:true 
        try(callbacks.removeScripts #preRender id:#ID_CRP_preRenderP )catch() 
        try(callbacks.removeScripts #filePostOpen id:#ID_CRP_filePostOpenP )catch()
        try(callbacks.removeScripts #viewportChange id:#ID_CRP_viewportChangeP )catch() 
        try(callbacks.removeScripts #filePostOpen id:#ID_CRP_filePostOpen )catch() 
        try(callbacks.removeScripts #filePostMerge id:#ID_CRP_filePostMerge )catch()
        try(callbacks.removeScripts #postImport id:#ID_CRP_postImport )catch()
		G_OBJ_UTIL.dotnetLog (" [loadMaxFN].End\n")
		
		G_STCON.RENDERER_OBJECT=renderers.production 
		G_STCON.RENDERER_STR = ( classof G_STCON.RENDERER_OBJECT ) as string
		
		
		
		G_OBJ_UTIL.dotnetLog(" [loadMaxFN].G_STCON.RENDERER_STR="+G_STCON.RENDERER_STR)
		
		try(
			local gammaFu=IDisplayGamma.colorCorrectionMode as string
			G_OBJ_UTIL.dotnetLog ("------Gamma after load max is"+gammaFu+"--------")
		)catch()
		
		try(
			rendUseNet=false
		)catch()
		
		loadResult
		if  loadResult == true then
		(
			G_OBJ_UTIL.dotnetLog(" [loadMaxFN].True ")
		)
		else
		(
			G_OBJ_UTIL.dotnetLog(" [loadMaxFN].Failure ")
			quitMax #noPrompt
		)
		
	),
	
	fn runFN = (
		
		loadMaxFN()
		
	)

)
G_STLoadMax = STLoadMax()
