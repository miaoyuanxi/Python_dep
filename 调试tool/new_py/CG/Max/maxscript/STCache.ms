struct STCache (

	fn pointCacheFN=(
		G_OBJ_UTIL.dotnetLog (" [STAsset.pointCacheFN.start].... ")
		local pcArr = #()
		
		try(
			pcArr = getClassInstances  Point_Cache
		)catch(G_OBJ_UTIL.dotnetLog ("NO_Point_Cache"))
		
		try(
			
			local pcwsmArr =  getClassInstances Point_CacheSpacewarpModifier
			join pcArr pcwsmArr
		)catch(G_OBJ_UTIL.dotnetLog ("NO_Point_CacheSpacewarpModifier"))			
		
		for myFile in pcArr do (
			local resultFile=G_OBJ_FILEUTIL.analysePath myFile.filename
			if resultFile!=undefined then (
				local oldPlaybackType=undefined
				local oldPlaybackStart=undefined
				local oldPlaybackEnd=undefined
				try(
					oldPlaybackType=myFile.playbackType
					oldPlaybackStart=myFile.playbackStart
					oldPlaybackEnd=myFile.playbackEnd
				)catch()
				
				myFile.filename=resultFile
				
				try(
					myFile.playbackType=oldPlaybackType
					myFile.playbackStart=oldPlaybackStart
					myFile.playbackEnd=oldPlaybackEnd
				)catch()
				
			)
		)
		G_OBJ_UTIL.dotnetLog (" [STAsset.pointCacheFN.end]\n")
	),

-------------------------------------------------------------Alembic-------------------------------------------------st
	fn AlembicFN = (
		G_OBJ_UTIL.dotnetLog (" [Alembic_Mesh_Geometry].Start ")
		try(
			local arr = getclassinstances Alembic_Mesh_Geometry 
			for a in arr do (
				local AlembicFile = a.path
				local resultAlembicName=G_OBJ_FILEUTIL.analysePath AlembicFile
				if resultAlembicName!=undefined then (
					a.path=resultAlembicName
				)
				
			)
		)catch(G_OBJ_UTIL.dotnetLog ("NO_Alembic_Mesh_Geometry"))
			
		G_OBJ_UTIL.dotnetLog (" [AlembicFN_Alembic_Mesh_Geometry].End\n")
		
		G_OBJ_UTIL.dotnetLog (" [AlembicFN_Alembiccam].Start ")   -----------------------------------20170824
		try(
			local arr = getclassinstances AlembicCamera
			for a in arr do (
				local Alembiccam = a.source
				local resultAlembiccam=G_OBJ_FILEUTIL.analysePath Alembiccam
				if resultAlembiccam!=undefined then (
					a.source=resultAlembiccam
				)
				
			)
		)catch(G_OBJ_UTIL.dotnetLog ("NO_Alembiccam"))
			
		G_OBJ_UTIL.dotnetLog (" [Alembiccam].End\n")
		
		G_OBJ_UTIL.dotnetLog (" [AlembicMeshNormals].Start ")    -----------------------------------20171123
		try(
			local arr = getclassinstances Alembic_Mesh_Normals
			for a in arr do (
				if a.path != undefined then (
					local resultAlembicMeshNormalsPath=G_OBJ_FILEUTIL.analysePath a.path
					a.path = resultAlembicMeshNormalsPath
				)
			)
		)catch(G_OBJ_UTIL.dotnetLog ("NO_AlembicMeshNormals"))

		G_OBJ_UTIL.dotnetLog (" [AlembicMeshNormals].End\n")
			
		G_OBJ_UTIL.dotnetLog (" [AlembicMeshGeometry].Start ")    -----------------------------------20171123
		try(
			local arr = getclassinstances Alembic_Mesh_Geometry
			for a in arr do (
				if a.path != undefined then (
					local resultAlembicMeshGeometryPath=G_OBJ_FILEUTIL.analysePath a.path
					a.path = resultAlembicMeshGeometryPath
				)
			)
		)catch(G_OBJ_UTIL.dotnetLog ("NO_AlembicMeshGeometry"))

		G_OBJ_UTIL.dotnetLog (" [AlembicMeshGeometry].End\n")
			
		G_OBJ_UTIL.dotnetLog (" [AlembicMeshTopology].Start ")    -----------------------------------20171123
		try(
			local arr = getclassinstances Alembic_Mesh_Topology
			for a in arr do (
				if a.path != undefined then (
					local resultAlembicMeshTopologyPath=G_OBJ_FILEUTIL.analysePath a.path
					a.path = resultAlembicMeshTopologyPath
				)
			)
		)catch(G_OBJ_UTIL.dotnetLog ("NO_AlembicMeshTopology"))

		G_OBJ_UTIL.dotnetLog (" [AlembicMeshTopology].End\n")
		
		G_OBJ_UTIL.dotnetLog (" [AlembicFN_AlembicObject].Start ")
		try(
			local arr = getclassinstances AlembicObject
			for a in arr do (
				local AlembicFile = a.source
				local resultAlembicName=G_OBJ_FILEUTIL.analysePath AlembicFile
				if resultAlembicName!=undefined then (
					a.source=resultAlembicName
				)
				
			)
		)catch(G_OBJ_UTIL.dotnetLog ("NO_AlembicObject"))
		G_OBJ_UTIL.dotnetLog (" [AlembicObject].End\n")
	),
-------------------------------------------------------------Alembic-------------------------------------------------end

-------------------------------------------------------------KrakatoaPRTLoader---------------------------------------st
	fn KrakatoaPRTLoaderFN = (
		G_OBJ_UTIL.dotnetLog (" [KrakatoaPRTLoader].Start ")
		try(
			local krakatoaPRTLoaderList = getclassinstances KrakatoaPRTLoader
			for myKrakatora in krakatoaPRTLoaderList do 
				(
				for ii = 1 to myKrakatora.fileList.count do 
					(
						format "a1...%\n" myKrakatora.fileList[ii]
				local PRTLoaderFile = myKrakatora.fileList[ii]
				local resultPRTLoaderName=G_OBJ_FILEUTIL.analysePath PRTLoaderFile
				if resultPRTLoaderName!=undefined then (
					myKrakatora.fileList[ii]=resultPRTLoaderName
					format "a2...%\n" myKrakatora.fileList[ii]
				)
					)
				)
		)catch(G_OBJ_UTIL.dotnetLog ("NO_KrakatoaPRTLoader"))
				
		G_OBJ_UTIL.dotnetLog (" [KrakatoaPRTLoader].End\n")
		
	),
-------------------------------------------------------------KrakatoaPRTLoader---------------------------------------end
-------------------------------------------------------------phoenixFN-----------------------------------------------st
	fn phoenixFN = (
		
		-------------------------PHXSimulator-------------------------
		G_OBJ_UTIL.dotnetLog (" [phoenixFN_PHXSimulator].Start ")
		try(
			
			local arra = getclassinstances PHXSimulator
			for aa in arra do (
				-------------------------input
				local phoenixFile = aa.rendinput
				if  phoenixFile!=undefined and not (matchPattern  phoenixFile pattern:"$*" ) then(
					local resultPhoenixName=G_OBJ_FILEUTIL.analysePath phoenixFile
					if resultPhoenixName!=undefined then (
						aa.rendinput=resultPhoenixName
					)
				)
				-------------------------output
				local phoenixFileOut = aa.simoutput
				if  phoenixFileOut!=undefined and not (matchPattern  phoenixFileOut pattern:"$*" ) then(
					local resultPhoenixFileOut=G_OBJ_FILEUTIL.analysePath phoenixFileOut
					if resultPhoenixFileOut!=undefined then (
						aa.simoutput=resultPhoenixFileOut
					)
				)
				
			)
		)catch(G_OBJ_UTIL.dotnetLog ("NO_PHXSimulator"))
			
		G_OBJ_UTIL.dotnetLog (" [phoenixFN_PHXSimulator].End\n")
		
		
		-------------------------FireSmokeSim-------------------------
		G_OBJ_UTIL.dotnetLog (" [phoenixFN_FireSmokeSim].Start ")
		try(
			local arrb = getclassinstances FireSmokeSim
			for ab in arrb do (
				-------------------------input
				local phoenixFile = ab.rendinput
				if  phoenixFile!=undefined and not (matchPattern  phoenixFile pattern:"$*" ) then(
					local resultPhoenixName=G_OBJ_FILEUTIL.analysePath phoenixFile
					if resultPhoenixName!=undefined then (
						ab.rendinput=resultPhoenixName
					)
				)
				
				-------------------------output
				local phoenixFileOutput = ab.simoutput
				if  phoenixFileOutput!=undefined and not (matchPattern  phoenixFileOutput pattern:"$*" ) then(
					local resultPhoenixFileOutput=G_OBJ_FILEUTIL.analysePath phoenixFileOutput
					if resultPhoenixFileOutput!=undefined then (
						ab.simoutput=resultPhoenixFileOutput
					)
				)
			)
		)catch(G_OBJ_UTIL.dotnetLog ("NO_FireSmokeSim"))
		G_OBJ_UTIL.dotnetLog (" [phoenixFN_FireSmokeSim].End\n")
		
		
		-------------------------LiquidSim-------------------------
		G_OBJ_UTIL.dotnetLog (" [phoenixFN_LiquidSim].Start ")
		try(
			local arrc = getclassinstances LiquidSim
			for ac in arrc do (
				-------------------------input
				local LiquidSiminFile = ac.rendinput
				if  LiquidSiminFile!=undefined and not (matchPattern  LiquidSiminFile pattern:"$*" ) then(
					local LiquidSimName=G_OBJ_FILEUTIL.analysePath LiquidSiminFile
					if LiquidSimName!=undefined then (
						ac.rendinput=LiquidSimName
					)
				)
				-------------------------output
				local phoenixFileOutput = ac.simoutput
				if  phoenixFileOutput!=undefined and not (matchPattern  phoenixFileOutput pattern:"$*" ) then(
					local resultPhoenixFileOutput=G_OBJ_FILEUTIL.analysePath phoenixFileOutput
					if resultPhoenixFileOutput!=undefined then (
						ac.simoutput=resultPhoenixFileOutput
					)
				)
			)
		)catch(G_OBJ_UTIL.dotnetLog ("NO_LiquidSim"))
		G_OBJ_UTIL.dotnetLog (" [phoenixFN_LiquidSim].End\n")
	),
-------------------------------------------------------------phoenixFN-----------------------------------------------end

    fn fumefxFN=(
		G_OBJ_UTIL.dotnetLog (" [fumefxFN].Start ")
		try(
			local arr = getclassinstances FumeFX
			for a in arr do(
				local defaultPath = a.GetPath "default"
				local waveletPath = a.GetPath "wavelet"
				local retimerPath = a.GetPath "retimer"
				G_OBJ_UTIL.dotnetLog (G_STCON.OUTPUT_PATH +"preview.avi")
				local previewPath=a.GetPath "preview"
				G_OBJ_UTIL.dotnetLog (previewPath)
				
				if previewPath!=undefined and previewPath!="" then (
					a.SetPath (G_STCON.OUTPUT_PATH +"preview.avi") #("preview")
				)
				
				local resultDefaultFile=G_OBJ_FILEUTIL.analysePath defaultPath
				local resultDefaultFileFolder=getFilenamePath resultDefaultFile
				if doesfileexist resultDefaultFileFolder and  resultDefaultFile!=undefined then (
					a.SetPath (resultDefaultFile+".fxd") #("default")
				)
				
				local resultWaveletFile=G_OBJ_FILEUTIL.analysePath waveletPath
				local resultWaveletFileFolder=getFilenamePath resultWaveletFile
				if doesfileexist resultWaveletFileFolder and resultWaveletFile!=undefined then(
					a.SetPath (resultWaveletFile+".fxd") #("wavelet")
					
				)
				
				local resultRetimerFile=G_OBJ_FILEUTIL.analysePath retimerPath
				local resultRetimerFileFolder=getFilenamePath resultRetimerFile
				if doesfileexist resultRetimerFileFolder and resultRetimerFile!=undefined then (
					a.SetPath (resultRetimerFile+".fxd") #("retimer")
				)
			)
			
		)catch()
		G_OBJ_UTIL.dotnetLog (" [fumefxFN].end\n")
		
	),	
	
	fn realflowFN = (
		G_OBJ_UTIL.dotnetLog (" [realflowFN].Start ")
		
		
		try(
			local rfMeshes = getClassInstances RFMeshLoader		
			for rfMesh in rfMeshes do(
				local meshPath = rfMesh.path
				local oldstart = rfMesh.start
				local oldoffset = rfMesh.offset
				local resultMeshPath=G_OBJ_FILEUTIL.analysePath meshPath
				if resultMeshPath!=undefined then (
					if not (matchpattern resultMeshPath pattern:"*/" ignoreCase:true) then (
						resultMeshPath=resultMeshPath+"/"
					)
					G_OBJ_UTIL.dotnetLog (" [realflowFN].resultMeshPath="+resultMeshPath)
					rfMesh.path=resultMeshPath
					rfMesh.start = oldstart
					rfMesh.offset = oldoffset

				)
				
			)
		)catch	(G_OBJ_UTIL.dotnetLog ("NO_RFMeshLoader"))
			
			
		try(
			local rfParticles = getClassInstances ParticleLoader
			if rfParticles.count > 0 and  hasProperty rfParticles[1] "binPath" then(
				for rfp in rfParticles do (
					
					local myBinPath= rfp.binPath
					local resultBinPath=G_OBJ_FILEUTIL.analysePath myBinPath
					if resultBinPath!=undefined then (
						if not (matchpattern resultBinPath pattern:"*/" ignoreCase:true) then (
							resultBinPath=resultBinPath+"/"
						)
						G_OBJ_UTIL.dotnetLog (" [NEW] "+resultBinPath)
						rfp.binPath=resultBinPath
						
					)
				)
			)
			
		)catch(G_OBJ_UTIL.dotnetLog ("NO_ParticleLoader"))
			
			
		try(
			
			local rfEditableMeshPaths = getClassInstances RFSoftBody
			if rfEditableMeshPaths.count>0  and  hasProperty rfEditableMeshPaths[1] "SD_Filename" then (
						
				for rfMesh in rfEditableMeshPaths do(
					local rfMeshPath = rfMesh.SD_Filename
					local resultRfMeshPath=G_OBJ_FILEUTIL.analysePath rfMeshPath
					if resultRfMeshPath!=undefined  then (
						if not (matchpattern resultRfMeshPath pattern:"*/" ignoreCase:true) then (
							resultRfMeshPath=resultRfMeshPath+"/"
						)
						G_OBJ_UTIL.dotnetLog (" [NEW] "+resultRfMeshPath)
						rfMesh.SD_Filename =resultRfMeshPath						
					)
				)
			)
		)catch(G_OBJ_UTIL.dotnetLog ("NO_RFSoftBody"))
		
		G_OBJ_UTIL.dotnetLog (" [realflowFN].End\n")
	),
-------------------------------------------------------------RF_Cache-----------------------------------------------st	--20170824
	fn refilecacheFN=(
		G_OBJ_UTIL.dotnetLog (" [refileCacheFN].Start ")
		try(
			local rfCache = getclassinstances RF_Cache
			for a in rfCache do (

			try(
				local oldrfrecStart = a.recStart
				local oldrfrecEnd = a.recEnd
				local oldrfrecStep = a.recStep
			)catch()
				
				local resultreFileName=G_OBJ_FILEUTIL.analysePath a.Filename
				if resultreFileName!=undefined  then 
				(
					a.Filename = resultreFileName
				)
				
			try(
				a.recStart = oldrfrecStart
				a.recEnd = oldrfrecEnd
				a.recStep = oldrfrecStep
			)catch()
			
			)
		)catch()
		G_OBJ_UTIL.dotnetLog (" [refileCacheFN].End\n")
	),	
-------------------------------------------------------------RF_Cache-----------------------------------------------end	

-------------------------------------------------------------VRayScannedMtl-----------------------------------------------st	--20170824
	fn vrscannedFN=(
		G_OBJ_UTIL.dotnetLog (" [vrscannedFN].Start ")
		try(
			local vrscan = getclassinstances VRayScannedMtl
			for a in vrscan do (
			
				local resultvrscanFileName=G_OBJ_FILEUTIL.analysePath a.Filename
				if resultvrscanFileName!=undefined  then 
				(
					a.Filename = resultvrscanFileName
				)
			
			)
		)catch()
		G_OBJ_UTIL.dotnetLog (" [vrscannedFN].End\n")
	),	
-------------------------------------------------------------VRayScannedMtl-----------------------------------------------end	

	fn xmeshFN=(
		G_OBJ_UTIL.dotnetLog (" [xmeshFN].Start ")
		try(
			local cacheArr = getclassinstances XMeshLoader
			for mycache in cacheArr do (

				local renderSequencePath = mycache.renderSequence
				local proxySequencePath = mycache.proxySequence
				
				local resultRenderSequencePath=G_OBJ_FILEUTIL.analysePath renderSequencePath
				if resultRenderSequencePath!=undefined  then (
					mycache.renderSequence = resultRenderSequencePath
					
				)
				local resultProxySequencePath=G_OBJ_FILEUTIL.analysePath proxySequencePath
				if resultProxySequencePath!=undefined  then (
					mycache.proxySequence = resultProxySequencePath
					
				)
			)
		)catch()
		G_OBJ_UTIL.dotnetLog (" [xmeshFN].End\n")
	),
	

	fn runFN =(
		
		if G_STCON.VRAY_DISTRIBUTE!=undefined and G_STCON.VRAY_DISTRIBUTE=="true" then (
			
		)else(
			
			pointCacheFN()
			KrakatoaPRTLoaderFN()
			AlembicFN()
			phoenixFN()
			fumefxFN()
			realflowFN()
			refilecacheFN()
			vrscannedFN()
			xmeshFN()
		)
	)

)

G_STCache = STCache()
