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
	if  dialogName!=undefined and dialogName!="" and dialogName=="About Hot4MAX" then (

		format "Dialog Name: %\n" (UIAccessor.GetWindowText WindowHandle)
		 
		
		local hwnd_children = uiAccessor.getChildWindows WindowHandle
		for i = 1 to hwnd_children.count do (
			format "% = \"%\"\n" i (uiAccessor.getWindowText hwnd_children[i])
		)
		UIAccessor.pressButtonByName WindowHandle "OK"
	)



	if  dialogName!=undefined and dialogName!="" and dialogName=="Proxy System" then (

		format "Dialog Name: %\n" (UIAccessor.GetWindowText WindowHandle)
		 
		
		local hwnd_children = uiAccessor.getChildWindows WindowHandle
		for i = 1 to hwnd_children.count do (
			format "% = \"%\"\n" i (uiAccessor.getWindowText hwnd_children[i])
		)
		UIAccessor.pressButtonByName WindowHandle "&No"
	)
    
    if  dialogName!=undefined and dialogName!="" and (matchpattern dialogName pattern:"vue xstream*" ignoreCase:true) then (

		format "Dialog Name: %\n" (UIAccessor.GetWindowText WindowHandle)
		 
		
		UIAccessor.PressDefaultButton()
		UIAccessor.CloseDialog WindowHandle
		UIAccessor.pressButtonByName WindowHandle "&No"
		UIAccessor.pressButtonByName WindowHandle "&Cancel"
		UIAccessor.SendMessageID WindowHandle #IDOK
        format "Dialog NameXXXXXXX\n" 
		
	)
	true
)

-----------------------------------------------------
struct STUtil(
	fn dotnetLog logStr=(
		if (maxversion())[1] < 18000 then(--2015,2014,2013,2012,2011,2010
			dotnetOut = DotNetClass "System.Console"
			dotnetOut.WriteLine ((localTime as string)+logStr)
		
		)else(
			G_STDOUT.print logStr
		)
		
		format "% %\n"localTime logStr
	),
	fn cmdLog logStr = (
		format "%\n" logStr
		DOSCommand ("echo "+logStr)
	),
	

	fn fillLeftZero sourceStr count= (
		if sourceStr ==undefined or sourceStr =="" then return sourceStr
		
		local str =sourceStr as string
		
		if  (matchPattern  str pattern:"-*" ) then(
			str=substring str 2 -1
			format "line......%\n" str
			while str.count<(count-1) do (
				str = "0" + str
			)
			str = "-"+str
		)else(
			while str.count<count do (
				str = "0" + str
			)
		)
		
		str
	),

	fn getFileNameFN file= (
		local ext = getFilenameType file
		local bname = getFileNameFile file
		local result = bname + ext
		result
	),
	
	
	fn replaceFN sourceStr oldStr newStr  = (
		
		if sourceStr ==undefined then return sourceStr
		local resultArr = #()
		for i=1 to sourceStr.count do (
			local index = findString sourceStr oldStr
			if index!=undefined then (
				local startStr = substring sourceStr 1 (index-1) 
				sourceStr = substring sourceStr (index+oldStr.count) sourceStr.count				
				append resultArr (startStr + newStr)
				
			)
		)
		append resultArr sourceStr
		local result = ""	
		for  rr in resultArr do (			
			append result rr
			
		)
		
		result
	),
	
	fn isStandardName myName= (
		allowed = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_-. "
		if myName==undefined or myName=="" then (
			return false
		)
		for i = 1 to myName.count do(
			if (findstring allowed myName[i]) == undefined then(			
				return false
			)
		)
		true
	),
	
	fn toStanderName myName=(
		local allowed = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_-. "
		local result = ""
		if myName==undefined or myName=="" then (
			
			result=undefined 
		)else(
			for i = 1 to myName.count do(
				if (findstring allowed myName[i]) != undefined then(
					result = result+myName[i]
				)
			)
			
			
			--check  all is space
			myName=result
			local spaceStr=" "
			local spaceCount=0
			format "myName....%\n" myName
			for i = 1 to myName.count do(
				if (findstring spaceStr myName[i]) != undefined then(
					spaceCount=spaceCount+1
				)
			)
			
			if spaceCount==myName.count then (
				result =undefined
			)
			
			if result=="" then (
				result=undefined
			)
		)
		
		result
	
	),
	fn get_json_val json_parser key_list value_type:"string" =(
		--local my_val = (((json_parser.GetValue  "system_info").GetValue "common").GetValue "channel").Value
		local json_temp =undefined
		for key in key_list do (
			if json_temp==undefined then (
				json_temp=(json_parser.GetValue  key)
			)else(
				json_temp=(json_temp.GetValue  key)
			)
			
		)
        if value_type=="list" then (
            json_temp
        )else(
            json_temp.Value
        )
		
	)
)
G_OBJ_UTIL = STUtil()

struct STConst (
	
	WORK_PATH="d:/work/render/",
	USER_ID,
	TASK_ID,
	MY_ACTION,
	
	SCRIPT_UPDATE,
	DEFAULT_DRIVER="A:",
	RENDER_FRAME,
	RENDER_FRAME_START,
	RENDER_FRAME_END,
	RENDER_FRAME_BY,
	RENDER_FRAME_SERIAL, 
	BLOCK_NUMBER,
	TOTAL_BLOCK,
	OVER_LAP=5,
	REGION_ARR,
	MAXFILE,
	NOT_RENDER,
	MYKG,
	MYPLATFORM,
	STEP_COUNT="7",
	PROJECT_SYMBOL="default",
	GUY_VERSION,
	OUTPUT_NAME="renderbus.jpg",
	ELEMENT_ACTIVE,
	RENDER_ELEMENT,
	ELEM_TYPE,
	VRAY_GI,
	VRAY_PRIMARY_GIENGINE,
	VRAY_SECONDARY_GIENGINE,
	VRAY_IRRADIANCEMAP_MODE,
	VRAY_IRRMAP_FILE,
	VRAY_LIGHTCACHE_MODE,
	VRAY_LIGHTCACHE_FILE,
	VRAY_IMAGE_SAMPLE_TYPE,
	VRAY_FILTER_ON,
	VRAY_FILTER_KERNEL,
	VRAY_DISTRIBUTE,
	JOB_ID,
	OUTPUT_PATH,
	OUTPUT_FILE,
	OUTPUT_SERIAL_FILE,
	RENDER_WORK="",
	LOG_PATH="c:/log/render/",
	CACHE_PATH,
	TEXTURE_PATH,
	PHOTON_PATH,
    MERGE_PATH,
	RENDERER_OBJECT,
	RENDERER_STR,
	RENDER_CFG_FILE="c:/rayvision/render/render.cfg",
	MAX_GAMMA,
	MAX_GAMMAVAL,
	MAX_INGAMMA,
	MAX_OUTGAMMA,
	ACTIVE_CAMERA,
	RENDERABLE_CAMERA,
	SKIP_UPLOAD="0",
	MYWIDTH,
	MYHEIGHT,
	MYCURRENTTASK,--picture/photon
	PLUGINS_MAX="B:/plugins/max/script/user/",
	SUB_FROM,
	IS_PICTURE="false",
	IS_BAKERENDER="false",		
	BAKERENDERID,
	CUSTOM_CLIENT="",
    MAX_QUICK_RENDER=true,
	PARAM_ARRAY=#(),
	ASSET_WEB_COOLECT_BY_PATH=false,
	PHOTON_DISPLACEMENT,
	PHOTON_REFLE_REFRA,
	MAX_USER_PATH=#(),
	MAX_XREF_PATH=#(),
	JSON_PARSER,
	
	fn bcdPath myDriver myPath=(
		local pathArr = filterString myPath ":"
		myDriver = pathArr[1]
		mySubPath= pathArr[2]
		
		local resultPath = (RENDER_WORK+myDriver+mySubPath)
		G_OBJ_UTIL.dotnetLog (" [bcdPath.resultPath]="+resultPath)
		resultPath
		
	),
	
	fn analyseRenderFrame =(
		local myStartFrame = undefined 
		local myEndFrame=undefined 
		local myByFrame=undefined
		
		if RENDER_FRAME !=undefined then (
			local frameArr1 = filterString RENDER_FRAME  "-"
			if frameArr1!=undefined and frameArr1.count==2 then (--11-113[6]
				myStartFrame = ""
				myEndFrame = ""
				if RENDER_FRAME[1] == "-" then(
					myStartFrame = "-"
				)
				if (findString RENDER_FRAME "--") != undefined then(
					myEndFrame = "-"
				)
			
				myStartFrame=myStartFrame+frameArr1[1]
				
				local frameArr2 = filterString frameArr1[2] "["
				
				if frameArr2!=undefined and frameArr2.count==2 then (
					myEndFrame=myEndFrame+frameArr2[1]
					
					myByFrame=G_OBJ_UTIL.replaceFN frameArr2[2] "]" ""
					
				)else if frameArr2!=undefined and frameArr2.count==1 then (--11-113
					myEndFrame=myEndFrame+frameArr2[1]
					
					myByFrame="1"
				)
				
			)
		)
		if myStartFrame!=undefined and myEndFrame!=undefined and myByFrame!=undefined then(--kg=100
			RENDER_FRAME_START= myStartFrame
			RENDER_FRAME_END=myEndFrame
			RENDER_FRAME_BY=myByFrame
		)
		if MYKG == "100" then(
			RENDER_FRAME_START= RENDER_FRAME
			RENDER_FRAME_END=RENDER_FRAME
			RENDER_FRAME_BY="1"
		)
		
	),
	
	fn getMaxFile=(
		--local maxFile=getINISetting RENDER_CFG_FILE "max" "max"
        local maxFile = (((json_parser.GetValue  "system_info").GetValue "common").GetValue "input_cg_file").Value
		maxFile=substituteString maxFile "\\" "/"
		format "maxfile............%\n" maxFile
		
		if VRAY_DISTRIBUTE!=undefined and VRAY_DISTRIBUTE=="true" then (
			
			local resultPath =RENDER_WORK+TASK_ID+".max"
			G_OBJ_UTIL.dotnetLog (" [getMaxFile.resultPath]="+resultPath)
			return resultPath
			
		)else(
			local netRenderTxt=PLUGINS_MAX+USER_ID+"/netrender.txt"
			if  doesFileExist netRenderTxt  then (-- net render
				local resultPath =(RENDER_WORK+(getfilenamefile maxFile)+(getfilenametype maxFile))
				G_OBJ_UTIL.dotnetLog (" [getMaxFile.resultPath]="+resultPath)
				return resultPath
			)
			
			if SKIP_UPLOAD=="1" then (
				local resultPath =(RENDER_WORK+(getfilenamefile maxFile)+(getfilenametype maxFile))
				G_OBJ_UTIL.dotnetLog (" [getMaxFile.resultPath]="+resultPath)
				return resultPath
			)else(
				if (findstring maxFile "/")==1 then (--\\serverA\bbgg\gg\abdd.pic>>/neta/bbgg/gg/abdd.pic
					local pathArr = filterString maxFile "/"
					mySubPath=""
					for i=1 to pathArr.count do (
						if i==pathArr.count then (
							mySubPath=mySubPath+pathArr[i]
						)else(
							mySubPath=mySubPath+pathArr[i]+"/"
						)
					)
					local resultPath = (RENDER_WORK+"net/"+mySubPath)
					if SUB_FROM=="1" or SUB_FROM=="2" then (
						resultPath = (RENDER_WORK+"__"+mySubPath)
					)
					G_OBJ_UTIL.dotnetLog (" [getMaxFile.resultPath]="+resultPath)
					return resultPath
				)
				
				local lowerMaxFile = toLower maxFile
				
				if (findstring lowerMaxFile "b:")==1 then (--c:/img/feee.jpg>>e/img/feee.jpg
					return bcdPath "b" maxFile
				)
				if (findstring lowerMaxFile "c:")==1 then (--c:/img/feee.jpg>>e/img/feee.jpg
					return bcdPath "c" maxFile
				)
				
				if (findstring lowerMaxFile "d:")==1 then (--c:/img/feee.jpg>>e/img/feee.jpg
					return bcdPath "d" maxFile
				)
				
				if (findstring maxFile ":")==2 then (--e:/img/feee.jpg>>e/img/feee.jpg
					G_OBJ_UTIL.dotnetLog (" [getMaxFile.resultPath]=undefined2")
					
					return maxFile 
				)
				
				local resultPath =("/default/"+maxFile)
				G_OBJ_UTIL.dotnetLog (" [getMaxFile.resultPath]="+resultPath)
				return resultPath
			)
			
		)
	),
	

	fn myLoadAssembly dllFile =(
		local assemblyStr=((dotnetClass "System.IO.File").ReadAllBytes dllFile)
		(dotnetClass "System.Reflection.Assembly").Load assemblyStr
	),
	
	fn get_json_parser task_json=(
		
		format "task_json-------------------%\n" task_json
		local json_dll=@"B:\plugins\max\newtonsoftJson\3.5\Newtonsoft.Json.dll" 
		myLoadAssembly json_dll
		local json_str = ""  
		local json_file = openFile task_json  
		while not eof json_file do(  
			json_str += readchar json_file  
		)  
		close json_file
	
		JSON_PARSER = (dotNetObject "Newtonsoft.Json.Linq.JObject").parse json_str  
	),
    
	fn readTaskJson task_json=(
		
		if doesFileExist task_json then (
            u8 = dotNetObject "System.Text.UTF8Encoding"
			
			if SUB_FROM=="1" or SUB_FROM=="2" then (

				--local outputBaseName=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","common", "output_file_basename")
				local outputBaseName = u8.GetString (u8.GetBytes (G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","common", "output_file_basename")))
                
				
                
                
				local outputType=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","common", "output_file_type")
				if (findString outputType ".")==undefined then(
					OUTPUT_NAME=outputBaseName+"."+outputType
				)else(
					OUTPUT_NAME=outputBaseName+outputType
				)
			)else()
			

			MAX_GAMMA = G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","common", "gamma")
			MAX_GAMMAVAL = G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","common", "gamma_val")
			MAX_INGAMMA = G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","common", "in_gamma")
			MAX_OUTGAMMA = G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","common", "out_gamma")

			
			ELEMENT_ACTIVE=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","common", "element_active")
			RENDER_ELEMENT=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","common", "element_list")
			ELEM_TYPE=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","common", "element_type")
			
			local renderer_name_yes = true
			try
			(
				local renderer_name = G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","renderer", "name")
				format "renderer_name:%\n" renderer_name
			)
			catch
			(
					print "json file have no scene_info_render.renderer.name"
					renderer_name_yes = false
			)
			
			if renderer_name_yes == true and (G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","renderer", "name")) == "vray" then
			(
				VRAY_GI=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","renderer", "gi")
				VRAY_PRIMARY_GIENGINE=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","renderer", "primary_gi_engine")
				VRAY_SECONDARY_GIENGINE=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","renderer", "secondary_gi_engine")
				VRAY_IRRADIANCEMAP_MODE=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","renderer", "irradiance_map_mode")
				--VRAY_IRRMAP_FILE=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","renderer", "irrmap_file")
                VRAY_IRRMAP_FILE = u8.GetString (u8.GetBytes (G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","renderer", "irrmap_file")))
				VRAY_LIGHTCACHE_MODE=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","renderer", "light_cache_mode")
				--VRAY_LIGHTCACHE_FILE=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","renderer", "light_cache_file")
                VRAY_LIGHTCACHE_FILE = u8.GetString (u8.GetBytes (G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","renderer", "light_cache_file")))
				VRAY_IMAGE_SAMPLE_TYPE=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","renderer", "image_sampler_type")
				VRAY_FILTER_ON=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","renderer", "filter_on")
				VRAY_FILTER_KERNEL=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","renderer", "filter_kernel")
				VRAY_DISTRIBUTE=G_OBJ_UTIL.get_json_val JSON_PARSER #("system_info","common", "distribute_node")

				PHOTON_DISPLACEMENT= G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","renderer", "displacement")
				PHOTON_REFLE_REFRA= G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","renderer", "reflection_refraction")

			)

			if MY_ACTION!=undefined and MY_ACTION=="RenderPhoton" then (
				MYWIDTH=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","renderer", "gi_width")
				MYHEIGHT=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","renderer", "gi_height")

				renderWidth=MYWIDTH as integer
				renderHeight=MYHEIGHT  as integer
			)else(
				MYWIDTH=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","common", "width")
				MYHEIGHT=G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","common", "height")
				renderWidth=MYWIDTH as integer
				renderHeight=MYHEIGHT  as integer
			)
			

            local myRenderCameras= G_OBJ_UTIL.get_json_val JSON_PARSER #("scene_info_render","common", "renderable_camera") value_type:"list"

            if myRenderCameras!=undefined and myRenderCameras.count > 1 then(
				local myCameraFolder=substituteString RENDERABLE_CAMERA "/" "_"
				myCameraFolder=substituteString RENDERABLE_CAMERA "\\" "_"

                --20180122--PHOTON_PATH=PHOTON_PATH+myCameraFolder+"/"
                MERGE_PATH=MERGE_PATH+myCameraFolder+"/"
               
			)

			format "*****[%].....\n" OUTPUT_NAME
			if OUTPUT_NAME!=undefined then (
				if OUTPUT_NAME=="" then (
					OUTPUT_NAME="rayvision.tga"
				)
				local baseName=getfilenamefile OUTPUT_NAME
				if baseName!=undefined and (not matchPattern  baseName pattern:"*_" ) then(
					OUTPUT_NAME=baseName+"_"+(getfilenametype OUTPUT_NAME)
				)
			)
			
		)
		
	),    
    
    

	fn init paramArray=(
		PARAM_ARRAY=paramArray
		USER_ID = PARAM_ARRAY[1]
		TASK_ID = PARAM_ARRAY[2]
		NOT_RENDER=PARAM_ARRAY[3]
		RENDER_FRAME = PARAM_ARRAY[4]
		RENDER_FRAME_START= PARAM_ARRAY[4]
		RENDER_FRAME_END =PARAM_ARRAY[4]
		JOB_ID=PARAM_ARRAY[5]
		
        RENDERABLE_CAMERA=PARAM_ARRAY[6]
		MY_ACTION=PARAM_ARRAY[7]
		OUTPUT_PATH=PARAM_ARRAY[8]
		MAXFILE =PARAM_ARRAY[9]
		
		
		
        task_json=PARAM_ARRAY[10]
		MYKG = PARAM_ARRAY[11]
        
		LOG_PATH=LOG_PATH+USER_ID+"/"+TASK_ID+"/"
		
		analyseRenderFrame()
		RENDER_FRAME_SERIAL  = ""
		if RENDER_FRAME_START==RENDER_FRAME_END then(
			RENDER_FRAME_SERIAL  = G_OBJ_UTIL.fillLeftZero RENDER_FRAME 4
		)
		
		RENDER_WORK =WORK_PATH+TASK_ID+"/max/"
		
		PHOTON_PATH=RENDER_WORK+"/photon/"
        MERGE_PATH=WORK_PATH+TASK_ID+"/block/frame_"+RENDER_FRAME+"/"

		CACHE_PATH=RENDER_WORK
		TEXTURE_PATH=RENDER_WORK
		
		MYWIDTH=renderWidth as string
		MYHEIGHT=renderHeight as string
		
		get_json_parser(task_json)

		SUB_FROM=G_OBJ_UTIL.get_json_val JSON_PARSER #("system_info","common", "channel")
		MYPLATFORM=G_OBJ_UTIL.get_json_val JSON_PARSER #("system_info","common", "platform")
		readTaskJson(task_json)
		
		
		
		G_OBJ_UTIL.dotnetLog (" [init]MYPLATFORM="+MYPLATFORM)
		G_OBJ_UTIL.dotnetLog (" [init]RENDER_CFG_FILE="+RENDER_CFG_FILE)
		G_OBJ_UTIL.dotnetLog (" [init]USER_ID="+USER_ID)
		G_OBJ_UTIL.dotnetLog (" [init]TASK_ID="+TASK_ID)
		G_OBJ_UTIL.dotnetLog (" [init]NOT_RENDER="+NOT_RENDER)
		G_OBJ_UTIL.dotnetLog (" [init]BLOCK_NUMBER="+(BLOCK_NUMBER as string))
		G_OBJ_UTIL.dotnetLog (" [init]TOTAL_BLOCK="+(TOTAL_BLOCK as string))
		G_OBJ_UTIL.dotnetLog (" [init]RENDER_FRAME="+RENDER_FRAME)
		G_OBJ_UTIL.dotnetLog (" [init]RENDER_FRAME_START="+RENDER_FRAME_START)
		G_OBJ_UTIL.dotnetLog (" [init]RENDER_FRAME_END="+RENDER_FRAME_END)
		G_OBJ_UTIL.dotnetLog (" [init]RENDER_FRAME_BY="+(RENDER_FRAME_BY as string))
		G_OBJ_UTIL.dotnetLog (" [init]MY_ACTION="+MY_ACTION)
		G_OBJ_UTIL.dotnetLog (" [init]SUB_FROM="+SUB_FROM)
		G_OBJ_UTIL.dotnetLog (" [init]CUSTOM_CLIENT="+CUSTOM_CLIENT)	
		G_OBJ_UTIL.dotnetLog (" [init]MAX_QUICK_RENDER="+(MAX_QUICK_RENDER as string))	
			
			
		G_OBJ_UTIL.dotnetLog (" [init]JOB_ID="+JOB_ID)
		G_OBJ_UTIL.dotnetLog (" [init]MAXFILE="+MAXFILE)
		G_OBJ_UTIL.dotnetLog (" [init]OUTPUT_PATH="+OUTPUT_PATH)
		G_OBJ_UTIL.dotnetLog (" [init]MYWIDTH="+MYWIDTH)
		G_OBJ_UTIL.dotnetLog (" [init]MYHEIGHT="+MYHEIGHT)
		
		G_OBJ_UTIL.dotnetLog (" [init]RENDER_WORK="+RENDER_WORK)
		G_OBJ_UTIL.dotnetLog (" [init]RENDER_FRAME_SERIAL="+RENDER_FRAME_SERIAL)
		
		G_OBJ_UTIL.dotnetLog (" [init]RENDERABLE_CAMERA="+(RENDERABLE_CAMERA as string))
			
			
		G_OBJ_UTIL.dotnetLog (" [init]OUTPUT_NAME="+(OUTPUT_NAME as string))
			
			
		makeDir OUTPUT_PATH all:true
			
	)
	
)
G_STCON=STConst()

struct STConfigMax(
	
	fn delAllUserPath = (
		
		local cc =mapPaths.count()
		for i in cc to 1 by -1 do (
			try(
				mapPaths.delete i
			)catch()
		)
		
	),

	fn getAllUserPath=(
		
		local userPathArr = #()
		for i=1 to mapPaths.count() do (
			local myPath = mapPaths.get i
			append userPathArr myPath
		)
		userPathArr
	),

	fn addUserPath userPathArr = (
		
		for i=1 to userPathArr.count do (
			local mpath = userPathArr[i]
			if mpath!=undefined then (
				mapPaths.add mpath
			)
			
		)
		
		
	),

	
	fn delAllXrefPath = (
		
		local cc =xrefPaths.count()
		for i in cc to 1 by -1 do (
			try(
				xrefPaths.delete i
			)catch()
		)
		
	),

	fn getAllXrefPath=(
		
		local xrefPathArr = #()
		for i=1 to xrefPaths.count() do (
			local myPath = xrefPaths.get i
			append xrefPathArr myPath
		)
		xrefPathArr
	),

	fn addXrefPath xrefPathArr = (
		
		for i=1 to xrefPathArr.count do (
			local mpath = xrefPathArr[i]
			if mpath!=undefined then (
				xrefPaths.add mpath
			)
			
		)
		
		
	),
	
	
	fn initMaxFN = (
		G_OBJ_UTIL.dotnetLog (" [initMaxFN].Start ")

		try(
			useFileUnits=true 
			quiet=true 
		)catch()
		try(setVRaySilentMode() )catch()
	
		local pathArr = getAllUserPath()
		G_STCON.MAX_USER_PATH=pathArr
		local userPathArr=#(G_STCON.RENDER_WORK,G_STCON.TEXTURE_PATH,G_STCON.CACHE_PATH)
		addUserPath userPathArr
		
		local xrefPathArr =getAllXrefPath()
		G_STCON.MAX_XREF_PATH=xrefPathArr
		local xrefPathArr=#(G_STCON.RENDER_WORK,G_STCON.TEXTURE_PATH,G_STCON.CACHE_PATH)
		addUserPath xrefPathArr
		G_OBJ_UTIL.dotnetLog (" [initMaxFN].End \n")
		
	),
	
	
	fn resetMaxFN =(
		G_OBJ_UTIL.dotnetLog (" [resetMaxFN].Start ")
		try(
			delAllUserPath()
			addUserPath G_STCON.MAX_USER_PATH
		)catch()
		
		try(
			delAllXrefPath()
			addXrefPath G_STCON.MAX_XREF_PATH
		)catch()
			
		G_OBJ_UTIL.dotnetLog (" [resetMaxFN].End \n")
		
	)
	
	
)
G_STMethods_STConfigMax = STConfigMax()

struct STFileUtil (
	
	fn abcdPath myDriver myPath=(
		local pathArr = filterString myPath ":"
		myDriver = pathArr[1]
		mySubPath= pathArr[2]
		
		local resultPath = (G_STCON.RENDER_WORK+myDriver+mySubPath)
		G_OBJ_UTIL.dotnetLog (" [NEW] "+resultPath)
		resultPath
		
	),
	
	

	fn analysePath myPath=(
		
		G_OBJ_UTIL.dotnetLog (" [OLD] "+(myPath as string))
			
		if G_STCON.VRAY_DISTRIBUTE!=undefined and G_STCON.VRAY_DISTRIBUTE=="true" then (
			G_OBJ_UTIL.dotnetLog ("vray distribute")
			return undefined
		)else(
			local netRenderTxt=G_STCON.PLUGINS_MAX+G_STCON.USER_ID+"/netrender.txt"
			if  doesFileExist netRenderTxt  then (-- net render
				return undefined
			)

			if G_STCON.MYPLATFORM=="1007"  then (
				local myFile=undefined 
				if myPath!=undefined and  myPath !="" then (
					local myFilename =getfilenamefile myPath+getfilenametype myPath
					local myFile = G_STCON.TEXTURE_PATH+myFilename
				)
				G_OBJ_UTIL.dotnetLog (" [NEW] "+(myFile as string))
				return myFile
				
			)else(
				if myPath==undefined or myPath=="" then (
					G_OBJ_UTIL.dotnetLog (" [NEW] "+(myPath as string))--("undefined")
					return undefined
				)
				myPath=G_OBJ_UTIL.replaceFN myPath "\\" "/"
				
				local myName =getfilenamefile myPath
				local myType= getfilenametype myPath
				local myFile = myName+myType
				if G_STCON.SUB_FROM=="1" or G_STCON.SUB_FROM=="2" then(
					------------------------by path-----------------------
					if G_STCON.ASSET_WEB_COOLECT_BY_PATH then (
						
						if myType==".max" then (
							local resultPath = (G_STCON.RENDER_WORK+myFile)
							return resultPath
						)
						------------net path
						if (findstring myPath "/")==1 then (--\\serverA\bbgg\gg\abdd.pic>>/neta/bbgg/gg/abdd.pic
							local pathArr = filterString myPath "/"
							mySubPath=""
							for i=1 to pathArr.count do (
								if i==pathArr.count then (
									mySubPath=mySubPath+pathArr[i]
								)else(
									mySubPath=mySubPath+pathArr[i]+"/"
								)
							)
							local resultPath = (G_STCON.RENDER_WORK+"__"+mySubPath)
							
							G_OBJ_UTIL.dotnetLog ("NEW="+(resultPath as string))
							return resultPath
						)
						
						lowerMyPath = toLower myPath
						if (findstring lowerMyPath "a:")==1 then (--c:/img/feee.jpg>>e/img/feee.jpg
							return abcdPath "a" myPath
						)
						if (findstring lowerMyPath "b:")==1 then (--c:/img/feee.jpg>>e/img/feee.jpg
							return abcdPath "b" myPath
						)
						if (findstring lowerMyPath "c:")==1 then (--c:/img/feee.jpg>>e/img/feee.jpg
							return abcdPath "c" myPath
						)
						
						if (findstring lowerMyPath "d:")==1 then (--c:/img/feee.jpg>>e/img/feee.jpg
							return abcdPath "d" myPath
						)
						
						if (findstring myPath ":")==2 then (--e:/img/feee.jpg>>e/img/feee.jpg
							G_OBJ_UTIL.dotnetLog (" [NEW] "+(myPath as string))--(" undefined2")
							
							local resultPath=undefined
							--G_OBJ_UTIL.dotnetLog (" [analysePath.type]="+ (myType as string))
							if myType==".vrmap" or myType==".vrlmap" then (
								resultPath= myPath 
							)
							
							return resultPath 
						)
						
						local resultPath =(G_STCON.RENDER_WORK+"/default/"+myFile)
						G_OBJ_UTIL.dotnetLog (" [NEW] "+(resultPath as string))
						return resultPath
						
					)else(-----------------------------------------------by name----------------------
						local resultPath =(G_STCON.RENDER_WORK+myFile)
						G_OBJ_UTIL.dotnetLog (" [NEW] "+(resultPath as string))
						return resultPath
						
					)
					
				)else(
					---------------------------------client-------------------------------------------
					if G_STCON.SKIP_UPLOAD=="1" then (
						local resultPath =(G_STCON.RENDER_WORK+myFile)
						G_OBJ_UTIL.dotnetLog (" [NEW] "+(resultPath as string))
						return resultPath
					)else(
						--max file
						if myType==".max" then (
							local resultPath = (G_STCON.RENDER_WORK+myFile)
							return resultPath
						)
						------------net path
						if (findstring myPath "/")==1 then (--\\serverA\bbgg\gg\abdd.pic>>/neta/bbgg/gg/abdd.pic
							local pathArr = filterString myPath "/"
							mySubPath=""
							for i=1 to pathArr.count do (
								if i==pathArr.count then (
									mySubPath=mySubPath+pathArr[i]
								)else(
									mySubPath=mySubPath+pathArr[i]+"/"
								)
							)
							local resultPath = (G_STCON.RENDER_WORK+"net/"+mySubPath)
							
							G_OBJ_UTIL.dotnetLog (" [NEW] "+(resultPath as string))
							return resultPath
						)
						
						lowerMyPath = toLower myPath
						if (findstring lowerMyPath "a:")==1 then (--c:/img/feee.jpg>>e/img/feee.jpg
							return abcdPath "a" myPath
						)
						if (findstring lowerMyPath "b:")==1 then (--c:/img/feee.jpg>>e/img/feee.jpg
							return abcdPath "b" myPath
						)
						if (findstring lowerMyPath "c:")==1 then (--c:/img/feee.jpg>>e/img/feee.jpg
							return abcdPath "c" myPath
						)
						
						if (findstring lowerMyPath "d:")==1 then (--c:/img/feee.jpg>>e/img/feee.jpg
							return abcdPath "d" myPath
						)
						
						if (findstring myPath ":")==2 then (--e:/img/feee.jpg>>e/img/feee.jpg
							
							local resultPath=undefined

							if myType==".vrmap" or myType==".vrlmap" then (
								resultPath= myPath 
							)
							G_OBJ_UTIL.dotnetLog (" [NEW] "+(myPath as string))
							return resultPath 
						)
						
						if not pathConfig.isAbsolutePath myPath then (
								
							local resultPath =(maxfilepath+myPath)

							G_OBJ_UTIL.dotnetLog (" [NEW] "+(resultPath as string))
							return resultPath
						)
						
						local resultPath =(G_STCON.RENDER_WORK+"default/"+myFile)

						G_OBJ_UTIL.dotnetLog (" [NEW] "+(resultPath as string))
						return resultPath
					
					)
				)
			)
		)
	)
)
G_OBJ_FILEUTIL=STFileUtil()

