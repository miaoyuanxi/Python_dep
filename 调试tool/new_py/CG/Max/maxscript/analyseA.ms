









dotnetcode = "
using System;
 
class StdOutPrinter {
    static public bool print(string txt) {
        Console.WriteLine(txt);
        return true;
    }
}
 
class StdErrPrinter {
    static public bool print(string txt) {
        Console.Error.WriteLine(txt);
        return true;
    }
}
class WriteToFile{
	static public bool write(string txt) {
        Console.Error.WriteLine(txt);
        return true;
    }

}
"
 
fn createAssembly dotnetcode className = (
    provider = dotNetObject "Microsoft.CSharp.CSharpCodeProvider"
    param = dotNetObject "System.CodeDom.Compiler.CompilerParameters"
    param.GenerateInMemory = on
    compiled = provider.CompileAssemblyFromSource param #(dotnetcode)
    compiled.CompiledAssembly.CreateInstance className
)
G_STDOUT = createAssembly dotnetcode "StdOutPrinter"


fn RB_MontiorDialog =
(


	local WindowHandle = DialogMonitorOPS.GetWindowHandle()

	local dialogName = UIAccessor.GetWindowText WindowHandle
--DOSCommand ("echo dialogName... " +dialogName+">>c:/dialogName.txt") 
	if  dialogName!=undefined and dialogName!="" and dialogName=="About Hot4MAX" then (

		format "Dialog Name: %\n" (UIAccessor.GetWindowText WindowHandle)
		 
		
		local hwnd_children = uiAccessor.getChildWindows WindowHandle
		for i = 1 to hwnd_children.count do (
			format "% = \"%\"\n" i (uiAccessor.getWindowText hwnd_children[i])
		)
		UIAccessor.pressButtonByName WindowHandle "OK"
	--UIAccessor.PressDefaultButton()
	--UIAccessor.CloseDialog WindowHandle
	--UIAccessor.SendMessageID WindowHandle #IDOK
	)



	if  dialogName!=undefined and dialogName!="" and dialogName=="Proxy System" then (

		format "Dialog Name: %\n" (UIAccessor.GetWindowText WindowHandle)
		 
		
		local hwnd_children = uiAccessor.getChildWindows WindowHandle
		for i = 1 to hwnd_children.count do (
			format "% = \"%\"\n" i (uiAccessor.getWindowText hwnd_children[i])
		)

		--UIAccessor.PressDefaultButton()
		
		--UIAccessor.CloseDialog WindowHandle
		UIAccessor.pressButtonByName WindowHandle "&No"
		--UIAccessor.SendMessageID WindowHandle #IDOK
	)
	true
)

-----------------------------------------------------

struct STConfig (
    ckey,
    cval,
    ctype
)
    
/*
信息封装
level，信息类型，error＝错误信息，warn＝警告信息
msg,信息内容
helperStr,信息对应的操作方案，如果是链接需要写成这种形式<a href="www.renderbus.com">more</a>
*/
struct STInfo(
    level,--0=info, 1=error, 2=warn
    msgList=#(),
	code
    
)
    
/*
检查结果的封装
resultName,结果名称，例如这个函数的目的是检查vrmesh没后缀名的，可以写成resultName="vrmeshWithoutExt"
infoList,信息列表，里面装的都是STInfo结构对象，对应的是各种错误，警告信息
configlist,配置信息列表，里面装的都是STConfig结构对旬，对应的是各种配置信息，最终会写到render.cfg的
*/
struct STResult (
    resultName,
    infoList=#(),
    configlist=#()
    
    
)




	
/*
信息提示总定义
多国语言版本
规范
都是大写，单词间用下划线连起，
警告信息以WARN_开头
错误信息以ERROR_开头
帮助信息以HELP_开头
*/

	
struct STLang (
    WARN_REALFLOW_VERSIONERR="Please upgrade your realflow version to at least 5.0.4",
    WARN_REALFLOW_VERSIONERR_CODE=10001,
	
	WARN_FUMEFX_NULL="FumeFX缓存丢失",
    WARN_FUMEFX_NULL_CODE=10001,
    
    
    ERROR_CAMERA_NULL="Missing camera",
    ERROR_CAMERA_NULL_CODE=10002,
    
	
	ERROR_VRMESH_NULL="Missing vrmesh suffix",
    ERROR_VRMESH_NULL_CODE=10003,
	
	
	ERROR_ELEMENTS_NULL="通道重名:",
    ERROR_ELEMENTS_NULL_CODE=10004,
	
	ERROR_CAMERAINFO_NULL="相机重名:",
    ERROR_CAMERAINFO_NULL_CODE=10005,
	
	ERROR_PROPERTIES_NULL="文件查不到信息:",
    ERROR_PROPERTIES_NULL_CODE=10006,
	
	ERROR_XREFS_NULL="代理文件路不能放在C、D盘和网络路径:",
    ERROR_XREFS_NULL_CODE=10007,
	
	ERROR_IESINFO_NULL="IES文件路径为空:",
    ERROR_IESINFO_NULL_CODE=10008,
	
    fn enVersion=(

		WARN_REALFLOW_VERSIONERR="Please upgrade your realflow version to at least 5.0.4"

    
		ERROR_CAMERA_NULL="Missing camera"
    
    )
    
)
global G_OBJ_LANG = STLang()




struct STConstanst(
	
	myMaxVersionInt=((maxversion())[1])/1000,
	myMaxVersionStr,
	myRenderVersion,
	myMaxFile=maxfilePath +maxFileName,
	myRender,
	myTaskId,
	myFrames,
	oAnalyseTxt,
	debugCount=1,
	--kg="0",
	fn init analyseTxt=(
		oAnalyseTxt=analyseTxt
		
	)
	
	
)
global G_CON=STConstanst()
	
struct STFileUtil(
	
		fn writeFileFN myFilePath msgList=(
			if doesFileExist myFilePath then (
				deleteFile myFilePath
				
			)
			
			local myfile=undefined 
			if G_CON.myMaxVersionInt >= 15 then(
				myfile = createFile myFilePath encoding:#utf8
			)else(
				myfile = createFile myFilePath
			)
			
			for msg in msgList do (
				
				print msg to:myfile
			)
			flush myfile
			close myfile
			
		)
	
)

global G_FILE_UTIL=STFileUtil()


struct STUtil(
	
	fn setIni  oType oKey oVal   = (	
		format "configfile...%\n" G_CON.oAnalyseTxt
		format "type.%..key.%...val...%\n"  oType oKey oVal
		
		if G_CON.myMaxVersionInt >= 15 then(
			SetINISetting G_CON.oAnalyseTxt oType oKey oVal forceUTF16:true
		)else(
			SetINISetting G_CON.oAnalyseTxt oType oKey oVal
		)
	),
		
	
	fn dotnetLog logStr=(
		if (maxversion())[1] < 18000 then(--2015,2014,2013,2012,2011,2010
			dotnetOut = DotNetClass "System.Console"
			dotnetOut.WriteLine ((localTime as string)+logStr)
		
		)else(
			G_STDOUT.print logStr
		)
		
		format "% %\n"localTime logStr
		--setIni "log" (G_CON.debugCount as string) logStr
		--G_CON.debugCount=G_CON.debugCount+1
	),
		

	fn convertPythonList msList=(
		local pythonListStr="["
		if msList.count>0 then (
			for itemCount=1 to msList.count do (
				item = msList[itemCount]
				if itemCount==msList.count then (
					pythonListStr=pythonListStr+"\""+item+"\""
				)else(
					pythonListStr=pythonListStr+"\""+item+"\","
				)
				
			)
		)
		pythonListStr=pythonListStr+"]"
		pythonListStr
	),
	
	fn convertToStr str=(
		str = str as string
		if str=="undefined" then (
			str=""
		)
		str
	)
)
global G_UTIL=STUtil()


/*
分析普通信息
分辨率，相机，输出名等
*/
struct STCommon(
	fn checkGamma = (
		G_UTIL.dotnetLog "---------checkGamma----------"
			local myResult=STResult()
			myResult.resultName="fileGamma"
			local File_Gamma = IDisplayGamma.colorCorrectionMode as string
			append myResult.configlist (STConfig ckey:"gamma" cval:File_Gamma ctype:"common")
		--if IDisplayGamma.colorCorrectionMode == #gamma then
		--(
			append myResult.configlist (STConfig ckey:"gamma_val" cval:(IDisplayGamma.gamma as string) ctype:"common")
			append myResult.configlist (STConfig ckey:"in_gamma" cval:(fileInGamma as string) ctype:"common")
			append myResult.configlist (STConfig ckey:"out_gamma" cval:(fileOutGamma as string) ctype:"common")
		--)
		myResult
	),
			
	fn  checkMaxVersion =(
		G_UTIL.dotnetLog "---------checkMaxVersion----------"
		local myResult=STResult()
        myResult.resultName="Version"
		local myMaxVersionInt=(2008+(((maxversion())[1])/1000 )-10) as string 
		append myResult.configlist (STConfig ckey:"cgv" cval:("3ds Max " + myMaxVersionInt) ctype:"common")
		myResult
	),
	
	fn checkrenders = (
		G_UTIL.dotnetLog "---------checkrenders----------"
		local myResult=STResult()
        myResult.resultName="renders"
		local myRender = renderers.production
		renderType=classOf myRender as string
		--append myResult.configlist (STConfig ckey:"render" cval:renderType ctype:"common")
		myResult
	),
	
	fn checkkg = (
		G_UTIL.dotnetLog "---------checkkg----------"
		local myResult=STResult()
		myResult.resultName="kg"
		local rend = renderers.production		
		case rend.adv_irradmap_mode of(
			0:( --single frame
				format "single frame\n"
			)
			1:( --multiframe incremental
				format "multiframe incremental\n"
			)
			2: --from file
			( 
				format "from file\n"				
			)
			3: --add to current map
			(
				format "add to current map\n"
			)
			4: --incremental add to current map
			(
				format "incremental add to current map\n"
				G_CON.kg="100"				
			)
			5: --bucket mode
			(
				format "bucket mode\n"
			)
			6: --animation (prepass) rend map
			(
				format "animation (prepass) rend map\n"
				G_CON.kg="101"
			)
			7: --animation (rendering) rend pic
			(
				format "animation (rendering) rend pic\n"
			)
		)
		append myResult.configlist (STConfig ckey:"kg" cval:G_CON.kg ctype:"common")
		myResult
	),
	
	fn getFrames=(
		if rendTimeType == 1 then
		(
			G_CON.myFrames=((sliderTime as string) as integer) as string
		)
		if rendTimeType == 2 then
		(
			G_CON.myFrames=(((animationRange.Start as string)as integer) as string +"-"+((animationRange.End  as string)as integer)as string)	
		)			
		if rendTimeType == 3 then 
		(
			G_CON.myFrames=(((rendStart as string)as integer) as string +"-"+((rendEnd  as string)as integer)as string)
		)
		if rendTimeType == 4 then 
		(
			G_CON.myFrames=rendPickupFrames  as string
		)
	),
	
	fn checkrendertype = (
		G_UTIL.dotnetLog "---------checkrendertype----------"
		local myResult=STResult()
        myResult.resultName="rendertype"
		--append myResult.configlist (STConfig ckey:"rendTimeType" cval:(rendTimeType as string) ctype:"common")
		
		getFrames()
		append myResult.configlist (STConfig ckey:"frames" cval:G_CON.myFrames ctype:"common")
        
        local animationRangeStart=((animationRange.Start as string)as integer) as string
        local animationRangeEnd=((animationRange.End as string)as integer) as string
        append myResult.configlist (STConfig ckey:"animation_range" cval:(animationRangeStart+"-"+animationRangeEnd) ctype:"common")
        
		myResult
	),
	
	fn checkcameras =(
		G_UTIL.dotnetLog "---------checkcameras----------"
		local myResult=STResult()
        myResult.resultName="cameras"	
		local allCamera=""
		for ii=1 to cameras.count do
		(
		local c=cameras[ii]
			if ((classof c) as string )!="Targetobject" then (
					format "c>>>>%____%\n" (classof c) c.name
				if ii==cameras.count then (
					allCamera= allCamera+ c.name
				)else(
					allCamera= allCamera+ c.name+"[,]"
				)		
			)
		)
		--allcamera	
		append myResult.configlist (STConfig ckey:"all_camera" cval:allCamera ctype:"common")
			
			
		local came =#()
		for u in cameras do 
		(
			if (getfilenametype u.name) != ".Target" then 
			(
				format "u.name....%\n" u.name
				append came u.name
			)	
		)
		local duplicateCamaerasList=#()
		for a in came do 
		(
			
			local eqcount = 0
			for aa in came do 
			(
				if a == aa then 
				(
					eqcount =eqcount+1
				)
			)
			if eqcount >1 then 
			(
				format "_____======______%\n" a
				append duplicateCamaerasList a
			)
		)
			
		if duplicateCamaerasList.count>0 then (	
			append myResult.infoList (STInfo level:"error" msgList:duplicateCamaerasList code:G_OBJ_LANG.ERROR_CAMERAINFO_NULL_CODE)
		)
		
		
		myResult
	),
	
		----------------------------------------------------------------------------------------------------------------Camera
	fn checkCamerainfo = (
		G_UTIL.dotnetLog "---------checkCamerainfo----------"
		local myResult=STResult()
		myResult.resultName="Camerainfo"
		local ActiveCamera = getActiveCamera()
		local ActiveVie = viewport.getType()
		if ActiveCamera != undefined then 
			(
			append myResult.configlist (STConfig ckey:"renderable_camera" cval:(ActiveCamera.name as string) ctype:"common")
			)	
		else 
			(
				local actcamera = #()
				for i in cameras do 
				(
					if (getfilenametype i.name) != ".Target" then 
					(
						append actcamera i.name
					)	
				)
				if actcamera.count >0 then
				(
				append myResult.configlist (STConfig ckey:"renderable_camera" cval:actcamera[1] ctype:"common")
				)
				else
				(
			----append myResult.configlist (STConfig ckey:"renderable_camera" cval:(ActiveVie as string) ctype:"common")	
				append myResult.infoList (STInfo level:"error" msgList:"Missing Camera" code:G_OBJ_LANG.ERROR_CAMERAINFO_NULL_CODE)
				)
			)			
		myResult
	),
	
	fn checkrendersize=(
		local myResult=STResult()
        myResult.resultName="rendersize"	
		local Width = renderWidth as string
		local Height = renderHeight as string 
		append myResult.configlist (STConfig ckey:"width" cval:Width ctype:"common")
		append myResult.configlist (STConfig ckey:"height" cval:Height ctype:"common")
		myResult
		),
		
	fn checkoutputname = (
		try(
		local myResult=STResult()
        myResult.resultName="rendersize"	
		local savepath = rendOutputFilename
		outputname = getfilenamefile savepath
		outputtype = getfilenametype savepath
		
		-- 20180319 added:set default outputname and outputtype
		if outputname == undefined or outputname == "" then (
			outputname = "rayvision"
		)
		if outputtype == undefined or outputtype == "" then (
			outputtype = ".tga"
		)
		
		savefilename = outputname + outputtype
		append myResult.configlist (STConfig ckey:"output_file" cval:savefilename ctype:"common")
		append myResult.configlist (STConfig ckey:"output_file_basename" cval:outputname ctype:"common")
		append myResult.configlist (STConfig ckey:"output_file_type" cval:outputtype ctype:"common")
		)catch()
		myResult
	),
	----------------------------------------------------------------------------------------------------------------Elements
	fn checkElements = (
		local myResult=STResult()
        myResult.resultName="Elements"
		
			local renderElementsMgr = maxOps.GetRenderElementMgr #Production
			local elementActive=renderElementsMgr.GetElementsActive()
			append myResult.configList (STConfig ckey:"element_active" cval:(G_UTIL.convertToStr elementActive) ctype:"common")
			
			
			
			
			
			local allElements = ""
			elem =#()
			for n = 0 to (renderElementsMgr.numrenderelements()- 1) do
			(
				local el =classof( renderElementsMgr.GetRenderElement n)
				local elemPath = renderElementsMgr.getRenderElementFilename n
				format "elemPath elem___________%\n" elemPath
				append elem elemPath
				allElements= (allElements+(el as string +"[,]"))	
			)
			append myResult.configlist (STConfig ckey:"element_list" cval:(allElements as string) ctype:"common")
			append myResult.configlist (STConfig ckey:"element_type" cval:"tga" ctype:"common")
			
				
		myResult
	),
	fn checkCommon=(
		local myResult=STResult()
        myResult.resultName="common"
		append myResult.configlist (STConfig ckey:"global_proxy" cval:(BitmapProxyMgr.globalProxyEnable as string) ctype:"common")
        
		myResult
	),
    fn check=(
		local assetList = #()
        local myMaxVersion=checkMaxVersion()
		local myfilegamma =checkGamma()
		local myrenders = checkrenders()
		--local mykg = checkkg()
		local mycameras = checkcameras()
		local mycamerainfo = checkCamerainfo()
		local myrendersize = checkrendersize()
		local myoutputname = checkoutputname()
		local elementscheck = checkElements()
		local myrendertype = checkrendertype()
		local commonCheck=checkCommon()
		append assetList myfilegamma
        append assetList myMaxVersion 
		append assetList myrenders 
		--append assetList mykg 
		append assetList mycameras 
		append assetList mycamerainfo 
		append assetList myrendertype
		append assetList myrendersize
		append assetList myoutputname
		append assetList elementscheck
		append assetList commonCheck
        assetList
		
		)
)

/*
分析资源信息，
贴图，缓存等
*/
struct STAsset(
    
    fn checkExample =(
        local myResult=STResult()
        myResult.resultName="example"
        --append myResult.infoList (STInfo level:"2" msg:G_OBJ_LANG.WARN_REALFLOW_VERSIONERR helperStr:G_OBJ_LANG.HELP_REALFLOW_VERSIONERR)
        --append myResult.infoList (STInfo level:"1" msg:G_OBJ_LANG.ERROR_CAMERA_NULL helperStr:G_OBJ_LANG.HELP_CAMERA_NULL)
        
        --append myResult.configlist (STConfig ckey:"gi" cval:"on" ctype:"vray")
        --append myResult.configlist (STConfig ckey:"width" cval:"1024" ctype:"common")
        
        myResult
    ),
	----------------------------------------------------------------------------------------------------------------Texture
	fn checkTexture = (
		local myResult=STResult()
        myResult.resultName="Texture"
			texList = #()
			Atsops.Refresh()
			Atsops.getFiles &texList
		
			for tex in texList do(
				if  (matchPattern tex pattern:"*.fxd") then(
				)else if (matchPattern tex pattern:"*.xmesh") then(
				)else if (matchPattern tex pattern:"*.vrmesh") then(
				)else if (matchPattern tex pattern:"*.bin") then(
				)else if (matchPattern tex pattern:"*.aur") then(
				)else if tex==(maxfilepath+maxfilename) then(
				)else if  (ATSOps.IsInputFile tex)  then(
					append myResult.configlist (STConfig ckey:"path" cval:tex ctype:"texture")
				)
					

			)
		myResult
		),
	----------------------------------------------------------------------------------------------------------------Krakatoa
	fn KrakatoaPRTLoaderFN = (
        local myResult=STResult()
        myResult.resultName="Krakatoa"
		try(
			local krakatoaPRTLoaderList = getclassinstances KrakatoaPRTLoader
			for myKrakatora in krakatoaPRTLoaderList do 
				(
				for ii = 1 to myKrakatora.fileList.count do 
					(
					format "a1...%\n" myKrakatora.fileList[ii]
					local PRTLoaderFile = myKrakatora.fileList[ii]
					local resultPRTLoaderName=G_OBJ_FILEUTIL.analysePath PRTLoaderFile
					if resultPRTLoaderName!=undefined then 
						(
						myKrakatora.fileList[ii]=resultPRTLoaderName
						format "a2...%\n" myKrakatora.fileList[ii]
						append myResult.configlist (STConfig ckey:"path" cval:myKrakatora.fileList[ii] ctype:"krakatoa")
						)
					)
				)
		)catch()
		myResult
	),
	
	----------------------------------------------------------------------------------------------------------------XMeshLoader
	fn checkXMeshLoader = (
        local myResult=STResult()
        myResult.resultName="xmesh"
		try(
			
				
			local xmeshList = getclassinstances XMeshLoader
			for theXMeshLoader in xmeshList do(
				format "\r\n\r\n\r\n-------------------\r\n"
				--local xmeshName=theXMeshLoader.name 
				local firstFrame=G_UTIL.convertToStr theXMeshLoader.rangeFirstFrame  
				local lastFrame=G_UTIL.convertToStr theXMeshLoader.rangeLastFrame  
				local limitToRange=G_UTIL.convertToStr theXMeshLoader.limitToRange  
				local renderSequence=G_UTIL.convertToStr theXMeshLoader.RenderSequence  
				local ProxySequence=G_UTIL.convertToStr theXMeshLoader.ProxySequence  
				
				--format "xmeshName....%\n" xmeshName
				format "firstFrame....%\n" firstFrame
				format "lastFrame....%\n" lastFrame
				format "limitToRange....%\n" limitToRange
				format "renderSequence....%\n" renderSequence
				format "ProxySequence....%\n" ProxySequence
				local str=firstFrame+"|"+lastFrame+"|"+limitToRange+"|"+renderSequence+"|"+ProxySequence
				
				append myResult.configlist (STConfig ckey:"path" cval:(str ) ctype:"xmesh")
			)
		)catch()
		myResult
	),
	
	----------------------------------------------------------------------------------------------------------------xrefs
	fn checkXrefs = (
		local myResult=STResult()
        myResult.resultName="Xrefs"
		try(
		local xrefscount = xrefs.getXRefFileCount()
		if xrefscount>0 then 
			(
				for i = 1 to xrefscount do 
				(
				local xrefsfile = xrefs.getXRefFile i
				append myResult.configlist (STConfig ckey:"path" cval:(xrefsfile.filename as string) ctype:"xrefs")
				local xrefspath =  xrefsfile.filename [1]+xrefsfile.filename [2]
				if xrefspath =="C:"or xrefspath =="D:" or xrefspath =="\\" then
					(
					print xrefsfile.filename
					append myResult.infoList (STInfo level:"error" code:G_OBJ_LANG.ERROR_XREFS_NULL_CODE)
					)
				)	
			)
		)catch()
		try(
		local xrefobj = getclassinstances XRefObject
		if  xrefobj.count>0 then 
			(
				for i = 1 to  xrefobj.count do 
				(
				local xrefsobjfile = xrefobj[i].filename
				append myResult.configlist (STConfig ckey:"path" cval:(xrefsobjfile as string) ctype:"xrefsobj")
				local xrefsobjpath =  xrefsobjfile[1]+xrefsobjfile[2]
				print xrefsobjpath
				if xrefsobjpath =="C:"or xrefsobjpath =="D:" or xrefsobjpath =="\\" then
					(
					append myResult.infoList (STInfo level:"error"  code:G_OBJ_LANG.ERROR_XREFS_NULL_CODE)
					)
				)	
			)	
		)catch()	
	myResult
	),
	
	----------------------------------------------------------------------------------------------------------------Realflow
	fn checkRealflow = (
		local myResult=STResult()
        myResult.resultName="Realflow"
		try(
				
				local rfMeshList = getClassInstances RFMeshLoader				
				for rfMesh in rfMeshList do(	
					local meshPath = rfMesh.path	
					
					if meshPath!=undefined and meshPath!="" then (
						print meshPath
						local formatStr = "name.#.ext"
						local prefix = rfMesh.prefix						
						local rfFormat = rfMesh.Format						
						if rfFormat==0 then (--name.#.ext
							formatStr ="name.#.ext"
						)else if rfFormat==1 then (--name.ext.#
							formatStr = "name.ext.#"
						)else if rfFormat==2 then (--name#.ext
							formatStr = "name#.ext"
						)else if rfFormat==3 then (--name_#.ext
							formatStr ="name_#.ext"
						)else(
							formatStr = "name.#.ext"
						)	
						
						local rfMeshStart= rfMesh.start as string
						local rfMeshStop=rfMesh.stop as string
						local rfMeshPad=rfMesh.padding as string
						format "%_%_%\n" (rfMeshStart as string ) (rfMeshStop  as string ) (rfMeshPad as string )
						
						local mymeshResult = rfMeshStart+"|"+rfMeshStop+"|"+rfMeshPad+"|"+formatStr+"|"+meshPath+"|"+prefix
						
						format "mymesh...%\n" mymeshResult
						append myResult.configlist (STConfig ckey:"path" cval:mymeshResult ctype:"realflow")
					)
					
				)
				
		)catch()
		myResult
		),
	----------------------------------------------------------------------------------------------------------------Alembic
	fn checkAlembic = (
		local myResult=STResult()
        myResult.resultName="Alembic"
			try(
			abc_file = getclassinstances Alembic_Mesh_Geometry 
			for i = 1 to abc_file.count do 
				(
					local AlembicFolder = abc_file[i].path
					append myResult.configlist (STConfig ckey:"path" cval:AlembicFolder ctype:"alembic")
				)
				)catch()
			try (
				abc_file = getclassinstances AlembicObject
			for i = 1 to abc_file.count do 
				(
					local AlembicFolder =  abc_file[i].source
					append myResult.configlist (STConfig ckey:"path" cval:AlembicFolder ctype:"alembic")
				)
			)catch()
			myResult
		),	
    --------------------------------------------------------------------------------------------------------------PointCache
	fn checkPointCache=(
		local myResult=STResult()
        myResult.resultName="PointCache"
			local pcArr = #()
			try(
				pcArr = getClassInstances  Point_Cache
				local pcwsmArr =  getClassInstances Point_CacheSpacewarpModifier
				join pcArr pcwsmArr
			)catch()
			try(			
			for pc in pcArr do (
				Filepath = getfilenamepath pc.fileName as string
				Filename = getfilenamefile pc.fileName as string
				Filetype = getfilenametype pc.fileName as string
				append myResult.configlist (STConfig ckey:"path" cval:(Filepath+Filename+Filetype) ctype:"pointcache")
				)
		)catch()
		myResult
		),	
	---------------------------------------------------------------------------------------------------------------FumeFX
	fn checkFumeFX = (
		local myResult=STResult()
        myResult.resultName="fumefx"
			local cacheList=#()
			try(
				local arr = getclassinstances FumeFX
				for a in arr do(
					local defaultPath = a.GetPath "default"
					local waveletPath = a.GetPath "wavelet"
					local retimerPath = a.GetPath "retimer"
					
					format "defaultPath...%\n" defaultPath
					format "waveletPath...%\n" waveletPath
					format "retimerPath...%\n" retimerPath
					
					local frameStr=(a.startframe as string)+"|"+(a.endframe as string)+"|"
					
					
					if not (matchPattern defaultPath pattern:"*.fxd") then (
						defaultPath=defaultPath+".fxd"
					)
					if not (matchPattern waveletPath pattern:"*.fxd") then (
						waveletPath=waveletPath+".fxd"
					)
					if not (matchPattern retimerPath pattern:"*.fxd") then (
						retimerPath=retimerPath+".fxd"
					)
					
					append myResult.configlist (STConfig ckey:"path" cval:(frameStr+"default|"+defaultPath) ctype:"fumefx")
					append myResult.configlist (STConfig ckey:"path" cval:(frameStr+"wavlet|"+waveletPath) ctype:"fumefx")
					append myResult.configlist (STConfig ckey:"path" cval:(frameStr+"post|"+retimerPath) ctype:"fumefx")
					
					
				)
			)catch()
		myResult
	),
	
	---------------------------------------------------------------------------------------------------------------Phoenix
	fn checkPhoenix = (
	
		local myResult=STResult()
		myResult.resultName="Phoenix"
		try(
			--D:\cq\catch\Liquids
			local arr = getclassinstances PHXSimulator
			for a in arr do(
				local phoenixNode=refs.dependentNodes a firstOnly:true baseObjectOnly:true
				local phoenixNodeName=phoenixNode.name as string
				format "p......%____%\n" a.rendinput a.simoutput
				frameStr=a.startframe as string +"|"+a.stopframe as string
				append myResult.configlist (STConfig ckey:"path" cval:(frameStr+"|phxsimulator|"+phoenixNodeName+"|"+(a.rendinput as string)+"|"+(a.simoutput)) ctype:"phoenix")	
			)
		)catch()
		
		try(
			--D:\work\scene\phoenixfd\fd_####.aur
			local arr = getclassinstances FireSmokeSim
			for a in arr do(
				local phoenixNode=refs.dependentNodes a firstOnly:true baseObjectOnly:true
				local phoenixNodeName=phoenixNode.name as string
				format "f......%____%\n" a.rendinput a.simoutput
				frameStr=a.startframe as string +"|"+a.stopframe as string
				append myResult.configlist (STConfig ckey:"path" cval:(frameStr+"|firesmokesim|"+phoenixNodeName+"|"+(a.rendinput as string)+"|"+(a.simoutput)) ctype:"phoenix")	
			)
		)catch()
		
		try(
			local arr = getclassinstances LiquidSim
			
			for a in arr do(
				local phoenixNode=refs.dependentNodes a firstOnly:true baseObjectOnly:true
				local phoenixNodeName=phoenixNode.name as string
				format "s......%____%\n" a.rendinput a.simoutput
				--if hasProperty a simoutput then 
				frameStr=a.startframe as string +"|"+a.stopframe as string
				
				append myResult.configlist (STConfig ckey:"path" cval:(frameStr+"|liquidsim|"+phoenixNodeName+"|"+(a.rendinput as string)+"|"+(a.simoutput)) ctype:"phoenix")	
			)
		)catch()
		myResult
	),
	
		---------------------------------------------------------------------------------------------------------------Phoenix
	fn checkVrayVolume = (
	
		local myResult=STResult()
		myResult.resultName="vrayVolume"
		try(
			vvList = getclassinstances VRayVolumeGrid
			for v in vvList do (
				format "v........%\n" v.rendinput
				append myResult.configlist (STConfig ckey:"path" cval:v.rendinput ctype:"vrayvolume")	
			)
			
		)catch()
		
		myResult
	),
	
	
	----------------------------------------------------------------------------------------------------------------Vrmesh
	fn checkVrmesh = (
        local myResult=STResult()
        myResult.resultName="vrmesh"
		try(
			local vrMeshArr=getclassinstances vrayproxy
			for i = 1 to  vrMeshArr.count do 
			(
				aax = getfilenametype vrMeshArr[i].Filename
				---vrmeshpath = 
				append myResult.configlist (STConfig ckey:"path" cval:vrMeshArr[i].Filename ctype:"vrmesh")	
				if aax != ".vrmesh" then 
				(	
				append myResult.infoList (STInfo level:"error"  code:G_OBJ_LANG.ERROR_VRMESH_NULL_CODE)
				)
				--else
				--(					
				--append myResult.configlist (STConfig ckey:"path" cval:vrMeshArr[i].Filename ctype:"vrmesh")	
				--)
			)
		)catch()
        myResult	
	),
	
			

	fn getObjectByMaterial  materialList myResult=(--get refrence object by materail or texture
		local materialCount=1
		for myMaterial in materialList do (
			
			local objectList=refs.dependents myMaterial
			local refObjStr="("
			for myObj in objectList where superclassof myObj == geometryclass do (
				refObjStr=refObjStr+myObj.name +","
			)
			refObjStr=refObjStr+")"
			local mKey="BAD."+((classof myMaterial as string)+(materialCount as string))
			local mValue=myMaterial.name+refObjStr
			format "%=%\n"  mKey mValue
			
			append myResult.configlist (STConfig ckey:mKey cval:mValue ctype:"badmaterial")	
		)
		
		
	),


	fn getBadMaterailAndTexture=(
		local myResult=STResult()
		myResult.resultName="BadMaterial"	
		try(
			local raytraceMaterialList=getclassinstances RaytraceMaterial 
			getObjectByMaterial  raytraceMaterialList myResult
		)catch()
		
		try(
			local raytracelList=getclassinstances Raytrace 
			getObjectByMaterial  raytracelList myResult
		)catch()
		
		try(
			local flatMirrorList =getclassinstances FlatMirror
			getObjectByMaterial   flatMirrorList myResult
		)catch()
		
		try(
			local reflectRefractList =getclassinstances ReflectRefract
			getObjectByMaterial  reflectRefractList myResult
		)catch()
		
		try(
			local autodeskMaterialList =getclassinstances Autodesk_Material
			getObjectByMaterial   autodeskMaterialList myResult
		)catch()
		
		try(
			local architecturalList =getclassinstances Architectural
			getObjectByMaterial   architecturalList myResult
		)catch()
		
		myResult
	),

	----------------------------------------------------------------------------------------------------------------Fileinfo
	fn checkfileProperties = (
		local myResult=STResult()
		myResult.resultName="Fileinfo"	
		if fileProperties.getItems "Objects" == undefined and fileProperties.getItems "对象" == undefined then 
		(
		append myResult.infoList (STInfo level:"error"  code:G_OBJ_LANG.ERROR_PROPERTIES_NULL_CODE)	
		)
		myResult
		),
		
	----------------------------------------------------------------------------------------------------------------IES
	fn checkIES = (
		local myResult=STResult()
		myResult.resultName="IES"	
			try(
				local Targetlight=getclassinstances Target_Light 
				local Freelight= getclassinstances Free_Light
				local allies = Targetlight+Freelight
				for i = 1 to  allies.count do 
				(
					webfilepath = getfilenamepath allies[i].webfile
					webfilefile = getfilenamefile allies[i].webfile
					webfiletype = getfilenametype allies[i].webfile
					--print aaxx
					if webfilepath == ""or webfilepath ==undefined then 
					(
					--	messagebox ""
					append myResult.infoList (STInfo level:"error"  code:G_OBJ_LANG.ERROR_IESINFO_NULL_CODE)	
					)
					else
					(
					append myResult.configlist (STConfig ckey:"path" cval:(webfilepath+webfilefile+webfiletype) ctype:"ies")	
					)
				)
				)catch()
		myResult
		),


		
    fn check=(
        local assetList = #()
        local exampleResult=checkExample()
		local myvrmesh=checkVrmesh()
		local myVrayVolume=checkVrayVolume()
		local Propertiescheck =checkfileProperties()
		local Mytexture = checkTexture()
		local MyAlembic = checkAlembic()
		local MyPointcache = checkPointCache()
		local MyfumeFx = checkFumeFX()
		local MyPhoenix = checkPhoenix()
		local MyKrakatoa = KrakatoaPRTLoaderFN()
		local Myiesfile = checkIES()
		local MyRealflow = checkRealflow()
		local MyXrefs = checkXrefs()
		local MyXMeshLoader = checkXMeshLoader()
		local badMaterial=getBadMaterailAndTexture()
		
		append assetList Mytexture
        append assetList exampleResult 
		append assetList myvrmesh
		append assetList myVrayVolume
		append assetList Propertiescheck
		append assetList MyAlembic
		append assetList MyPointcache
		append assetList MyfumeFx
		append assetList MyPhoenix
		append assetList MyKrakatoa
		append assetList Myiesfile
		append assetList MyRealflow
		append assetList MyXrefs
		append assetList MyXMeshLoader
		
		
		
		append assetList badMaterial
        assetList
    )
    
)

/*
分析渲染器信息
vray渲染器的设置等
*/
struct STRenderer(
	
	fn checkVFB myResult=(
		local myRender = renderers.production
		
		local vfbOn=myrender.output_on as string
		append myResult.configlist (STConfig ckey:"vfb" cval:vfbOn ctype:"renderer")
			
		local renderToRwFile = myRender.output_saveRawFile as string
		local rawImgName = myRender.output_rawFileName
		append myResult.configList (STConfig ckey:"rend_raw_img_Name" cval:renderToRwFile ctype:"renderer")
		append myResult.configList (STConfig ckey:"raw_img_name" cval:(G_UTIL.convertToStr rawImgName) ctype:"renderer")
		
		
		local splitBuffer = myRender.output_splitgbuffer as string
		append myResult.configList (STConfig ckey:"save_sep_channel" cval:splitBuffer ctype:"renderer")
		local splitFileName = myRender.output_splitfilename as string			
		append myResult.configList (STConfig ckey:"channel_file" cval:(G_UTIL.convertToStr splitFileName) ctype:"renderer")
		
		local displacement=myRender.options_displacement as string
		append myResult.configList (STConfig ckey:"displacement" cval:displacement ctype:"renderer")
		
		local rr=myRender.options_reflectionRefraction as string
		append myResult.configList (STConfig ckey:"reflection_refraction" cval:rr ctype:"renderer")
			
		local filterOnBoolean=myRender.filter_on as string
		append myResult.configList (STConfig ckey:"filter_on" cval:filterOnBoolean ctype:"renderer")
		
		
		local imageSamplerType=myRender.imageSampler_type as string
		append myResult.configList (STConfig ckey:"image_sampler_type" cval:imageSamplerType ctype:"renderer")
		
		local filterKernel=(classof myRender.filter_kernel as string)
		local filterKernelStandard=""
		if filterKernel ==	"Area"	then(	
			filterKernelStandard =	"Area"
		)else if filterKernel ==	"Sharp_Quadratic" 	then(	
			filterKernelStandard =	"Sharp Quadratic" 
		)else if filterKernel ==	"Catmull_Rom"	then(	
			filterKernelStandard =	"Catmull-Rom"
		)else if filterKernel ==	"Plate_Match_MAX_R2"	then(	
			filterKernelStandard =	"Plate Match/MAX R2"
		)else if filterKernel ==	"Quadratic"	then(	
			filterKernelStandard =	"Quadratic"
		)else if filterKernel ==	"cubic"	then(	
			filterKernelStandard =	"cubic"
		)else if filterKernel ==	"Video"	then(	
			filterKernelStandard =	"Video"
		)else if filterKernel ==	"Soften"	then(	
			filterKernelStandard =	"Soften"
		)else if filterKernel ==	"Cook_Variable"	then(	
			filterKernelStandard =	"Cook Variable"
		)else if filterKernel ==	"Blendfilter"	then(	
			filterKernelStandard =	"Blend"
		)else if filterKernel ==	"Blackman"	then(	
			filterKernelStandard =	"Blackman"
		)else if filterKernel ==	"Mitchell_Netravali"	then(	
			filterKernelStandard =	"Mitchell-Netravali"
		)else if filterKernel ==	"VRayLanczosFilter"	then(	
			filterKernelStandard =	"VRayLanczosFilter"
		)else if filterKernel ==	"VRaySincFilter"	then(	
			filterKernelStandard =	"VRaySincFilter"
		)else if filterKernel ==	"VRayBoxFilter"	then(	
			filterKernelStandard =	"VRayBoxFilter"
		)else if filterKernel ==	"VRayTriangleFilter"	then(	
			filterKernelStandard =	"VRayTriangleFilter"
		)
		append myResult.configList (STConfig ckey:"filter_kernel" cval:filterKernelStandard ctype:"renderer")
		
	),
	
	fn checkGI myResult=(
		local myRender = renderers.production
			
		if myRender.gi_on==true then(
			append myResult.configlist (STConfig ckey:"gi" cval:"1" ctype:"renderer")
		)else(
			append myResult.configlist (STConfig ckey:"gi" cval:"0" ctype:"renderer")
		)
		
		append myResult.configlist (STConfig ckey:"primary_gi_engine" cval:(myRender.gi_primary_type as string) ctype:"renderer")
		append myResult.configlist (STConfig ckey:"irradiance_map_mode" cval:(myRender.adv_irradmap_mode as string) ctype:"renderer")
		append myResult.configlist (STConfig ckey:"irrmap_file" cval:(G_UTIL.convertToStr myRender.adv_irradmap_loadFileName ) ctype:"renderer")
		
		
		append myResult.configlist (STConfig ckey:"secondary_gi_engine" cval:(myRender.gi_secondary_type as string) ctype:"renderer")	
		append myResult.configlist (STConfig ckey:"light_cache_mode" cval:(myRender.lightcache_mode as string) ctype:"renderer")
		append myResult.configlist (STConfig ckey:"light_cache_file" cval:(G_UTIL.convertToStr  myRender.lightcache_loadFileName ) ctype:"renderer")
		
		
		memLimit_USER = myRender.system_raycaster_memLimit as string 
		append myResult.configlist (STConfig ckey:"mem_limit" cval:memLimit_USER ctype:"renderer")
		append myResult.configlist (STConfig ckey:"default_geometry" cval:(myRender.system_instancedObjects as string) ctype:"renderer")
		
		append myResult.configlist (STConfig ckey:"gi_frames" cval:G_CON.myFrames ctype:"renderer")
		append myResult.configlist (STConfig ckey:"gi_width" cval:(renderWidth as string) ctype:"renderer")
		append myResult.configlist (STConfig ckey:"gi_height" cval:(renderHeight as string) ctype:"renderer")
		
		
		local subdivs =""
		local secbounce=""
		if hasProperty myRender "dmcgi_subdivs" then (
			subdivs=myRender.dmcgi_subdivs as string
		)
		if hasProperty myRender "qmcgi_subdivs" then (
			subdivs=myRender.qmcgi_subdivs as string
		)
		local secbounce=""
		if hasProperty myRender "dmcgi_depth" then (
			secbounce=myRender.dmcgi_depth as string
		)
		if hasProperty myRender "qmcgi_depth" then (
			secbounce=myRender.qmcgi_depth as string
		)
		
		append myResult.configList (STConfig ckey:"subdivs" cval:subdivs ctype:"renderer")
		append myResult.configList (STConfig ckey:"secbounce" cval:secbounce ctype:"renderer")
		append myResult.configList (STConfig ckey:"displacement" cval:(myRender.options_displacement as string) ctype:"renderer")
		append myResult.configList (STConfig ckey:"reflection_refraction" cval:(myRender.options_reflectionRefraction as string) ctype:"renderer")
		
	),
	
	fn checkVray= (
		local myResult=STResult()
		myResult.resultName="Vray"
		append myResult.configList (STConfig ckey:"name" cval:"vray" ctype:"renderer")
		
		checkGI myResult
		checkVFB myResult

		append myResult.configlist (STConfig ckey:"onlyphoton" cval:"false" ctype:"renderer")
		myResult
	),	
	
	fn checkRender rend = (
		local myResult=STResult()
		myResult.resultName=rend
		append myResult.configList (STConfig ckey:"name" cval:rend ctype:"renderer")
		myResult
	),	
	
    fn check=(
		local rendererList=#()
		local rend=""
		local rendStr = ( classof renderers.production ) as string
		if (rendStr == (vray as string)) then (
			rend="vray"
			local myResult=checkVray()
			append rendererList myResult
		) else if (rendStr == (default_scanline_renderer as string)) then (
			rend = "scanline"
			local myResult=checkRender(rend)
			append rendererList myResult
		) else if rendStr == (finalRender_stage_1 as string) then (
			rend = "finalrender"
			local myResult=checkRender(rend)
			append rendererList myResult
		) else if (rendStr == (MaxwellRenderer as string)) then (
			rend = "maxwell"
			local myResult=checkRender(rend)
			append rendererList myResult
		) else if (rendStr == (mental_ray_renderer as string)) then (
			rend = "mentalray"
			local myResult=checkRender(rend)
			append rendererList myResult
		) else if (rendStr == (mental_ray_iray_Renderer as string)) then (
			rend = "mentalray_iray"
			local myResult=checkRender(rend)
			append rendererList myResult
		) else if (rendStr == (Quicksilver_Hardware_Renderer as string)) then (
			rend = "hardware"
			local myResult=checkRender(rend)
			append rendererList myResult
		) else (
			rend = ""
			local myResult=checkRender(rend)
			append rendererList myResult
		)
		
        rendererList
	)

)

/*
分析插件信息
*/
struct STPlugin(
    fn check=()
    
)

fn setIniCfg assetRs=(
	local count=1
	local infoList=assetRs.infoList
	local configList=assetRs.configlist
	
	
	for config in configList do (
		if config.ctype=="common" or config.ctype=="renderer" then (
			G_UTIL.setIni  config.ctype (config.ckey) config.cval
		)else(
			G_UTIL.setIni  config.ctype (config.ckey+(count as string)) config.cval
			count=count+1
		)
		
	)
	--------------------warn or error--------------------
	for info in infoList do (
		
		G_UTIL.setIni  "tips" (info.code as string)  (G_UTIL.convertPythonList info.msgList)
			
	)
	
)

fn  analyseRun userId taskId maxFile analyseTxt  pythonPid=(
	deletefile analyseTxt
	
	windows.sendMessage (pythonPid as integer) 11 0 0
	
	G_CON.init analyseTxt
	
	DialogMonitorOPS.unRegisterNotification id:#RB_Monitor_Dialog 
	DialogMonitorOPS.RegisterNotification RB_MontiorDialog id:#RB_Monitor_Dialog
	DialogMonitorOPS.Enabled = true
	
	G_UTIL.dotnetLog "---------loadmaxfile start----------"
	local loadResult = loadMaxFile maxFile useFileUnits:true quiet:true
	G_UTIL.dotnetLog ("---------loadmaxfile end----------"+loadResult as string)
	
	local totalResult = #()
	
	
    local asset = STAsset()
    local assetResultList = asset.check()
	
	
	local mycommon = STCommon()
	local mycommonStList = mycommon.check()
	
	
	local rendererSt=STRenderer()
	local rendererStList =rendererSt.check()
	
	join totalResult mycommonStList
	join totalResult rendererStList
	join totalResult assetResultList

/*
	local count=1
	local fumefxCount=1
	local phoenixCount=1
	local pointcacheCount=1
	local krakatoaCount=1
	local alembicCount=1
	local realflowCount=1
	local vrmeshCount=1
	local iesCount=1
	local xrefsCount=1
	local xmeshCount=1
	local errCount=1
	local warnCount=1
	local badMaterialCount=1
	*/
	local logPath=analyseTxt
	--local logPath="G:/render.cfg"
	
	for assetRS in totalResult do (
		setIniCfg assetRS
		format "assetRS...%\n" (assetRS as string)
	)
	
	/*
    for assetRS in totalResult do (
		format "%\n" assetRS
		--local infoList=assetRs.infoList
		setIniCfg assetRS
		
		local exampleInfoList=assetRs.infoList
		local exampleConfigList=assetRs.configlist
		for exampleConfig in exampleConfigList do (
			
			if exampleConfig.ctype=="texture" then (
			G_UTIL.setIni  exampleConfig.ctype (exampleConfig.ckey+(count as string)) exampleConfig.cval
			
			count=count+1
			)
			else if exampleConfig.ctype=="fumefx" then 
			(
			G_UTIL.setIni  exampleConfig.ctype (exampleConfig.ckey+(fumefxCount as string)) exampleConfig.cval
			fumefxCount=fumefxCount+1
			)
			else if exampleConfig.ctype=="phoenix" then 
			(
			G_UTIL.setIni  exampleConfig.ctype (exampleConfig.ckey+(phoenixCount as string)) exampleConfig.cval
			phoenixCount=phoenixCount+1
			)
			else if exampleConfig.ctype=="pointcache" then 
			(
			G_UTIL.setIni  exampleConfig.ctype (exampleConfig.ckey+(pointcacheCount as string)) exampleConfig.cval
			pointcacheCount=pointcacheCount+1
			)
			else if exampleConfig.ctype=="krakatoa" then 
			(
			G_UTIL.setIni  exampleConfig.ctype (exampleConfig.ckey+(krakatoaCount as string)) exampleConfig.cval
			krakatoaCount=krakatoaCount+1
			)
			else if exampleConfig.ctype=="vrmesh" then 
			(
			G_UTIL.setIni  exampleConfig.ctype (exampleConfig.ckey+(vrmeshCount as string)) exampleConfig.cval
			vrmeshCount=vrmeshCount+1
			)
			else if exampleConfig.ctype=="alembic" then 
			(
			G_UTIL.setIni  exampleConfig.ctype (exampleConfig.ckey+(alembicCount as string)) exampleConfig.cval
			alembicCount=alembicCount+1
			)
			else if exampleConfig.ctype=="realflow" then 
			(
			G_UTIL.setIni  exampleConfig.ctype (exampleConfig.ckey+(realflowCount as string)) exampleConfig.cval
			realflowCount=realflowCount+1
			)
			else if exampleConfig.ctype=="ies" then 
			(
			G_UTIL.setIni  exampleConfig.ctype (exampleConfig.ckey+(iesCount as string)) exampleConfig.cval
			iesCount=iesCount+1
			)
			else if exampleConfig.ctype=="xrefs" then 
			(
			G_UTIL.setIni  exampleConfig.ctype (exampleConfig.ckey+(xrefsCount as string)) exampleConfig.cval
			xrefsCount=xrefsCount+1
			)
			else if exampleConfig.ctype=="xmesh" then 
			(
			G_UTIL.setIni  exampleConfig.ctype (exampleConfig.ckey+(xmeshCount as string)) exampleConfig.cval
			xmeshCount=xmeshCount+1
			)
			else if exampleConfig.ctype=="BadMaterial" then 
			(
			G_UTIL.setIni  exampleConfig.ctype (exampleConfig.ckey+(badMaterialCount as string)) exampleConfig.cval
			badMaterialCount=badMaterialCount+1
			)
			
			
			else
			(
				
				G_UTIL.setIni  exampleConfig.ctype exampleConfig.ckey (exampleConfig.cval as string)
			)
			)
			
		--------------------warn or error--------------------
		for info in exampleInfoList do (
			
			G_UTIL.setIni  "tips" (info.code as string)  (G_UTIL.convertPythonList info.msgList)
			
				
		)
	)
	
	*/
	format "------------------end--------------------\r\n"
	windows.sendMessage (pythonPid as integer) 999 0 0
	G_UTIL.dotnetLog "\n\n------------------------------------------------------------[End maxscript analyse]--------------------------------------------------------\n\n"
	G_UTIL.dotnetLog "\n\n------------------------------------------------------------[_____KILL MAX_____]--------------------------------------------------------\n\n"
	--DOSCommand ("b:/tools/maxkill.exe " +(windows.getMAXHWND() as string)) 
)

clearlistener()
--test "962712" "11111" "c:/work/helper/11111/max/test.max"
--analyseRun "962712" "21740" @"D:\work\helper\5108979\max\vrmeh.max" @"d:\work\helper\21740\cfg\analyse_net.txt"
--analyseRun "962712" "5140547" @"D:\work\helper\5140547\max\要命要命不是人.max" "d:/analyse_net.txt"

--analyseRun "962712" "5145962" "C:/work/helper/5145962/max/wangyeduantest01.max" "C:/work/helper/5145962/cfg/analyse_net.txt" "0"

