struct STTexture(
	
	fn bitmapFN=(
		G_OBJ_UTIL.dotnetLog (" [STAsset.bitmapFN.start].... ")
		local allBitmaps = #()
		
		try(
			local allBitmaps1 = getClassInstances bitmapTex processChildren:True
			join allBitmaps allBitmaps1
			
		)catch(G_OBJ_UTIL.dotnetLog ("NO_bitmapTex"))
		
		try(
			local allBitmaps2 = getClassInstances bitmapHDR processChildren:True 
			join allBitmaps allBitmaps2
		)catch(G_OBJ_UTIL.dotnetLog ("NO_bitmapHDR"))
		
		try(		
			local allBitmaps3 = getClassInstances CoronaBitmap processChildren:True		
			join allBitmaps allBitmaps3		
		)catch(G_OBJ_UTIL.dotnetLog ("NO_CoronaBitmap"))

		for myObj in allBitmaps do (
			
			try(
				local oldplayBackRate = myObj.playBackRate
			)catch()
			
			local resultBitmapName=G_OBJ_FILEUTIL.analysePath myObj.filename
			if resultBitmapName!=undefined then (
				myObj.filename=resultBitmapName	
			)
			
			try(
				myObj.playBackRate = oldplayBackRate
			)catch()
		)
		
		try(
			
			local Subbitmaps = getclassinstances Substance processChildren:True 
			for o in Subbitmaps do
			(
				local beforePath = G_OBJ_FILEUTIL.analysePath o.SubstanceFilename
									
				if beforePath !=undefined then
				(
				o.SubstanceFilename = beforePath
				)
			)
			
			
		)catch(G_OBJ_UTIL.dotnetLog (" NO_SubstanceFile" ))
		
		try(
			G_OBJ_UTIL.dotnetLog (" \n\n")
			G_OBJ_UTIL.dotnetLog (" [ATSOps.bitmapFN.start]\n")
			ATSOps.Refresh()
			Atsops.getFiles &texList
			for tex in texList do
			(
				if tex==undefined or tex=="" then
				(
					continue
				)
				if tex!=(maxfilepath+maxfilename) and  (ATSOps.IsInputFile tex) then
				(
					if  (filterString tex "\\")[1] == "D:" or (filterString tex "\\")[1] == "d:" or (filterString tex "\\")[1] == "C:" or (filterString tex "\\")[1] == "c:" or tex[1] == "\\" then
					(
						if ((filterString tex "\\")[1]+"\\"+(filterString tex "\\")[2]) != "d:\work" then
						(
							print tex
							ATSOps.SelectFiles tex
							
							newtex = G_OBJ_FILEUTIL.analysePath tex
							
							ATSOps.SetPathOnSelection (getfilenamepath newtex)
							
							ATSOps.ClearSelection() 
						)
					)
				)
			)
			G_OBJ_UTIL.dotnetLog (" [ATSOps.bitmapFN.end]\n\n")
		)catch(G_OBJ_UTIL.dotnetLog (" NO_ATSOps" ))	
		
		
		G_OBJ_UTIL.dotnetLog (" [STAsset.bitmapFN.end]\n")
	),
	
	fn iesFN=(
		local allInstanceArr= #()
		for mylight in lights do (
			try(
				local tempArr=#()
				InstanceMgr.GetInstances mylight &tempArr
				if findItem allInstanceArr mylight==0 then (
					format "%[not found]...\n" mylight.name
					local resultIes = G_OBJ_FILEUTIL.analysePath mylight.webfile
					if resultIes!=undefined then (
						--InstanceMgr.MakeObjectsUnique mylight #individual
						local oldIntensity = mylight.intensity
						local oldtype = mylight.type
						local olduseMultiplier =mylight.useMultiplier
						local oldmultiplier = mylight.multiplier
						mylight.webfile=resultIes
						mylight.intensity=oldIntensity
						mylight.type=oldtype
						mylight.useMultiplier =olduseMultiplier
						mylight.multiplier=oldmultiplier
						
						
					)
				)else(
					format "% [found]\n" mylight.name
				)
				if tempArr.count>0 then (
					join allInstanceArr tempArr
					
				)
			)catch()
		)
	
		try(
			local Cories = getClassInstances CoronaLight
			for i in Cories do(
				local resultIesfile=G_OBJ_FILEUTIL.analysePath i.iesFile
				if resultIesfile!=undefined then (
					i.iesFile=resultIesfile
				)
				
			)
		)catch(G_OBJ_UTIL.dotnetLog ("NO_CoronaIES"))		
	
	),
	
	fn runFN=(
		
		bitmapFN()
		iesFN()
	)
	
)
G_STTexture = STTexture()
