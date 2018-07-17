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

struct STConst (
	
	WORK_HELPER="d:/work/helper/",
    WORK_RENDER="d:/work/render/",
	USER_ID,
	USER_ID_PARENT,
	TASK_ID,
    MAX_FILE,
	MAX_FROM,
	PARAM_ARRAY,
	WORK_HELPER_TASK,
	WORK_HELPER_TASK_MAX,
	WORK_HELPER_TASK_MAX2,
	WORK_HELPER_TASK_CFG,
    WORK_RENDER_TASK_MAX,
	WORK_RENDER_TASK_OUTPUT,
	
	task_json,
	RENDER_CFG_FILE,
	
	MYKG,
	MYWIDTH,
	MYHEIGHT,
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
	PHOTON_DISPLACEMENT,
	PHOTON_REFLE_REFRA,
	LinqJsonObj,



    
	fn get_json_parser task_json=(
		
		format "task_json-------------------%\n" task_json
		local JsonDllPath=@"B:\plugins\max\newtonsoftJson\3.5\Newtonsoft.Json.dll" 


		-- 读取本地Json文件到字符变量  
		JsonString = ""  
		JsonFile = openFile task_json  
		while not eof JsonFile do  
		(  
			JsonString += readchar JsonFile  
		)  
		close JsonFile  
		  
		  
		-- 加载模块  
		(dotnetClass "System.Reflection.assembly").Load ((dotnetClass "System.IO.File").ReadAllBytes(JsonDllPath))  
		-- 解析Json格式的字符  
		LinqJsonObj = (dotNetObject "Newtonsoft.Json.Linq.JObject").parse JsonString  
	),
    
    fn get_json_val LinqJsonObj key_list value_type:"string" =(
		local json_temp =undefined
		for key in key_list do (
			if json_temp==undefined then (
				json_temp=(LinqJsonObj.GetValue  key)
			)else(
				json_temp=(json_temp.GetValue  key)
			)
			
		)
		if value_type=="list" then (
			json_temp
		)else(
			json_temp.Value
		)
		
	),
	
	fn readTaskJson task_json=(
		if doesFileExist task_json then (

			VRAY_GI=get_json_val LinqJsonObj #("scene_info_render","renderer", "gi")
			VRAY_PRIMARY_GIENGINE=get_json_val LinqJsonObj #("scene_info_render","renderer", "primary_gi_engine")
			VRAY_SECONDARY_GIENGINE=get_json_val LinqJsonObj #("scene_info_render","renderer", "secondary_gi_engine")
			VRAY_IRRADIANCEMAP_MODE=get_json_val LinqJsonObj #("scene_info_render","renderer", "irradiance_map_mode")
			VRAY_IRRMAP_FILE=get_json_val LinqJsonObj #("scene_info_render","renderer", "irrmap_file")
			VRAY_LIGHTCACHE_MODE=get_json_val LinqJsonObj #("scene_info_render","renderer", "light_cache_mode")
			VRAY_LIGHTCACHE_FILE=get_json_val LinqJsonObj #("scene_info_render","renderer", "light_cache_file")
			VRAY_IMAGE_SAMPLE_TYPE=get_json_val LinqJsonObj #("scene_info_render","renderer", "image_sampler_type")
			VRAY_FILTER_ON=get_json_val LinqJsonObj #("scene_info_render","renderer", "filter_on")
			VRAY_FILTER_KERNEL=get_json_val LinqJsonObj #("scene_info_render","renderer", "filter_kernel")
			VRAY_DISTRIBUTE=get_json_val LinqJsonObj #("system_info","common", "distribute_node")
			--VRAY_DISTRIBUTE="3"
			PHOTON_DISPLACEMENT= get_json_val LinqJsonObj #("scene_info_render","renderer", "displacement")
			PHOTON_REFLE_REFRA= get_json_val LinqJsonObj #("scene_info_render","renderer", "reflection_refraction")
			MYWIDTH=get_json_val LinqJsonObj #("scene_info_render","renderer", "gi_width")
			MYHEIGHT=get_json_val LinqJsonObj #("scene_info_render","renderer", "gi_height")
		
			
		)
	),
	
	fn init paramArray=(
		PARAM_ARRAY=paramArray
		USER_ID = PARAM_ARRAY[1]
		USER_ID_PARENT= PARAM_ARRAY[2]
		TASK_ID = PARAM_ARRAY[3]
		MAX_FILE=PARAM_ARRAY[5]
		MAX_FROM=PARAM_ARRAY[8]
		task_json = PARAM_ARRAY[9]
		MYKG = PARAM_ARRAY[10]
		
		WORK_HELPER_TASK=WORK_HELPER+TASK_ID+"/"
		WORK_HELPER_TASK_MAX=WORK_HELPER_TASK+"max/"
        WORK_HELPER_TASK_MAX2=WORK_HELPER_TASK+"/max2/"
		WORK_HELPER_TASK_CFG=WORK_HELPER+TASK_ID+"/cfg/"
		RENDER_CFG_FILE = WORK_HELPER_TASK+"cfg/render.cfg"
		WORK_RENDER_TASK_MAX=WORK_RENDER+TASK_ID+"/max/"
		WORK_RENDER_TASK_OUTPUT=WORK_RENDER+TASK_ID+"/output/"
		--readRenderCfg()
        get_json_parser(task_json)
		readTaskJson(task_json)
        if not doesfileexist WORK_RENDER_TASK_MAX then(
            makeDir WORK_RENDER_TASK_MAX all:true
        )
	)
	
)
G_STCON=STConst()

struct STUtil(
	fn dotnetLog logStr=(
		if (maxversion())[1] < 18000 then(--2015,2014,2013,2012,2011,2010
			dotnetOut = DotNetClass "System.Console"
			--dotnetOut.WriteLine ((localTime as string)+logStr)
			dotnetOut.WriteLine ((" - - - ")+logStr)
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
	
	fn analysePath myPath=(
		if myPath != undefined then
		(
			if (findstring myPath ":")==2 then (
				myPath=substituteString myPath "\\" "/"
				myPaths=substituteString myPath ":/" "/"
				if G_STCON.MAX_FROM != "web" then 
				(
					myPath = G_STCON.WORK_HELPER_TASK_MAX + myPaths
				)
				else
				(
				myPath = maxfilepath+(filenamefrompath myPath)
				)
			)
			else if (findstring myPath "\\") == 1 then
			(
				myPath=substituteString myPath "\\" "/"
				myPaths=substituteString myPath "//" "/"
				if G_STCON.MAX_FROM != "web" then
				(
				myPath =G_STCON.WORK_HELPER_TASK_MAX + ("net"+myPaths)
				)
				else
				(
				myPath = maxfilepath+(filenamefrompath myPath)
				)
			)
			else
			(
				myPath = maxfilepath+(filenamefrompath myPath)
			)
		)else(print "replaceError")
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
	
	)

)
G_OBJ_UTIL = STUtil()

struct STAsset (
	
	fn commonFN = (
		G_OBJ_UTIL.dotnetLog (" [STAsset.commonFN.Start].... ")
		
		callbacks.removeScripts()
		
		try(
			rendSaveFile = true

			rendTimeType = 1
			
			rendUseNet=false
			
			rendShowVFB = true
		)catch()
		
		if rendoutputfilename != "" then
			(
				try(
				local imageInfoArr=getBitmapInfoRayvision()
				)catch(G_OBJ_UTIL.dotnetLog (" [getRayvisionDLL_Failure] "))
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
				rendoutputfilename = (G_STCON.WORK_RENDER_TASK_OUTPUT+(filenamefrompath rendoutputfilename)as string)	
			)
		else
			(
				rendoutputfilename = G_STCON.WORK_RENDER_TASK_OUTPUT+"Renderbus.tga"
			)
		
		try(
		re = maxOps.GetCurRenderElementMgr() 
		theManager = maxOps.GetRenderElementMgr #Production
		theManager.SetDisplayElements false
		for n = 0 to (theManager.numrenderelements()- 1) do
			(
				local el = re.getrenderelement n	
				el.enabled=true
				local elName = re.GetRenderElementFilename n
				
				if (filenamefrompath elName) != "" or (filenamefrompath elName) != undefined then
				(
					if (getfilenametype elName) != ".png" then
					(
						re.SetRenderElementFilename n ( G_STCON.WORK_RENDER_TASK_OUTPUT + (filenamefrompath elName) as string)
					)
					else
					(
						re.SetRenderElementFilename n ( G_STCON.WORK_RENDER_TASK_OUTPUT + (getfilenamefile elName) as string +".tga")
					)
				)
				else
				(
					re.SetRenderElementFilename n ( G_STCON.WORK_RENDER_TASK_OUTPUT + (classof el)+".tga")
				)
			)
		)catch(print "ERROR___")
		
		
		local myRender = renderers.production	
		if  (classof myRender) == vray then
		(
			
			if  (myRender.output_saveRawFile == true) and  (myRender.output_rawFileName != "") and (myRender.output_rawFileName != undefined)then
			(
				myRender.output_rawFileName = (G_STCON.WORK_RENDER_TASK_OUTPUT+(filenamefrompath myRender.output_rawFileName)as string)
			)
			--else(myrender.output_on = false)
			
			if  (myRender.output_on == true) and (myRender.output_splitfilename != "") and (myRender.output_splitfilename != undefined) then
			(
				myRender.output_splitgbuffer = true
				myRender.output_splitfilename = (G_STCON.WORK_RENDER_TASK_OUTPUT+(filenamefrompath myRender.output_splitfilename)as string)
			)
			else(myrender.output_on = false)
			
			
			try(
				myRender.system_vrayLog_level =4
				myRender.system_vrayLog_show = true
				RaytraceGlobalSettings.showMessages = false
				myRender.system_embree_on = true
				myRender.system_embree_moblur = true
				myRender.system_embree_highPrecision = true
			)catch()
			
			
		)
		try(
				G_OBJ_UTIL.dotnetLog (" [run].customScript  <<SetExr>> ")
				if matchPattern rendoutputfilename pattern:"*.exr" then 
				(
					fopenexr.setAutoAddRenderElements true
				
					rendoutputfilename = (G_STCON.WORK_RENDER_TASK_OUTPUT+(filenamefrompath rendoutputfilename)as string)	
				)
		)catch(G_OBJ_UTIL.dotnetLog (" [run].customScript____EXR__Error "))
		
		try(
				G_OBJ_UTIL.dotnetLog (" [run].customScript  <<SetRpf>> ")
				if matchPattern rendoutputfilename pattern:"*.rpf" then 
				(
					rpf.colorDepth =16
					rpf.nodeIDChannel =true
					rpf.zChannel =true
				
					rendoutputfilename = (G_STCON.WORK_RENDER_TASK_OUTPUT+(filenamefrompath rendoutputfilename)as string)	
				)
		)catch(G_OBJ_UTIL.dotnetLog (" [run].customScript____RPF__Error "))
				
		G_OBJ_UTIL.dotnetLog (" [STAsset.commonFN.End]\n ")
	),
	
	fn bitmapFN workMax workMax2=(--G_STCON.WORK_HELPER_TASK_MAX G_STCON.WORK_RENDER_TASK_MAX
		format "%\n" (" [STAsset.bitmapFN.start].... ")
		G_OBJ_UTIL.dotnetLog (" [STAsset.bitmapFN.start].... ")
		local allBitmaps = #()
		local arrbitmap = #()
		--local sceneMaps = usedMaps()
		local bitmapcount = 0

		try(
			local allBitmaps1 = getClassInstances bitmaptex processChildren:True
			join allBitmaps allBitmaps1
			
		)catch(
			format "%\n" ("NO_bitmapTex")
		)
		
		try(
			local allBitmaps2 = getClassInstances bitmapHDR processChildren:True 
			join allBitmaps allBitmaps2
		)catch(
			format "%\n"("NO_bitmapHDR")	
		)
--try(
		--for m in meditmaterials do join sceneMaps (usedMaps m)
		for i in allBitmaps do 
		(
				if i.filename != undefined then
				(
					if (getfilenametype i.filename)!= ".ifl" then 
					(
						bitNum = G_OBJ_UTIL.fillLeftZero bitmapcount 5
						beforePath = (G_OBJ_UTIL.analysePath i.filename)
						texfiletype = getfilenametype beforePath
						--afterPath = (workMax2 +"Map"+ bitNum as string +texfiletype)

						if (finditem arrbitmap beforePath) == 0 then
							(
								bitmapcount += 1
								append arrbitmap beforePath
								append arrbitmap (bitNum as string)
							)
						afterPath = (workMax2 +"Map"+ arrbitmap[(finditem arrbitmap beforePath)+1]as string +texfiletype)
							
						copyfile beforePath afterPath
						i.filename = afterPath
						
						G_OBJ_UTIL.dotnetLog (beforePath as string + "<<<=>>>" +afterPath as string )

						if (getfilenamepath i.filename ) != (getfilenamepath afterPath) and (getfilenamepath i.filename )!= undefined then 
						(
							G_OBJ_UTIL.dotnetLog ("Secondary changes  ::"+i.filename as string)
							i.filename = afterPath
						)
						--bitmapcount = bitmapcount+1	
					)
				
					else if (getfilenametype i.filename) == ".ifl" then
					(
						if DoesFileexist (G_OBJ_UTIL.analysePath i.filename) then
						(
							local iflArr = #()	
							local iflFile = openfile (G_OBJ_UTIL.analysePath i.filename)
							while not eof iflFile do append iflArr (readline iflFile)
							close iflFile
							for ii in iflArr do 
							(
								local ifiFilepath = (G_OBJ_UTIL.analysePath ii)
								if (getfilenamepath ii)!="" and (DoesFileExist ifiFilepath) then
								(
									ftstr = (getfilenamefile ii)
									texfiletype = (getfilenametype ii)
									---IflFilenumber = ftstr[ftstr.count-3]+ftstr[ftstr.count-2]+ftstr[ftstr.count-1]+ftstr[ftstr.count]
								copyfile ifiFilepath (workMax2 +(filenamefrompath ii))
								)
								else
								(
									ftstr = (getfilenamefile ii)
									texfiletype = (getfilenametype ii)
									---IflFilenumber = ftstr[ftstr.count-3]+ftstr[ftstr.count-2]+ftstr[ftstr.count-1]+ftstr[ftstr.count]
								copyfile ((getfilenamepath (G_OBJ_UTIL.analysePath i.filename)) + (filenamefrompath ii)) (workMax2 +(filenamefrompath ii))
								)
							)
							beforePath = (G_OBJ_UTIL.analysePath  i.filename)
							afterPath = (workMax2 +(filenamefrompath i.filename))					
							copyfile beforePath afterPath
							i.filename = afterPath		
						)else(G_OBJ_UTIL.dotnetLog "IFL File Missing")						
					)
				)
			
		)
		
	--)catch()
		format "%\n" (" [STAsset.bitmapFN.end].... ")
		G_OBJ_UTIL.dotnetLog (" [STAsset.bitmapFN.end]\n ")
	),
	
	fn iesFN workMax workMax2 =(
		G_OBJ_UTIL.dotnetLog (" [STAsset.iesFN.start].... ")
		local allInstanceArr= #()
		local arries = #()
		local iescount = 0
		for mylight in lights do (
			try(
						local tempArr=#()
						InstanceMgr.GetInstances mylight &tempArr
						if findItem allInstanceArr mylight==0 then 
							(
								--InstanceMgr.MakeObjectsUnique mylight #individual
								local oldIntensity = mylight.intensity
								local oldtype = mylight.type
								local olduseMultiplier =mylight.useMultiplier
								local oldmultiplier = mylight.multiplier
							
							bitNum = G_OBJ_UTIL.fillLeftZero iescount 5
							beforePath = (G_OBJ_UTIL.analysePath mylight.webfile)
							--afterPath = (workMax2 +"IES"+bitNum as string +".ies")
								
								if (finditem arries beforePath) == 0 then
								(
									iescount += 1
									append arries beforePath
									append arries (bitNum as string)
								)
								afterPath = (workMax2 +"IES"+arries[(finditem arries beforePath)+1]as string +".ies")
								copyfile beforePath afterPath
								mylight.webfile = afterPath
							

								G_OBJ_UTIL.dotnetLog (beforePath as string + "<<<=>>>" +afterPath as string )
								
								mylight.intensity=oldIntensity
								mylight.type=oldtype
								mylight.useMultiplier =olduseMultiplier
								mylight.multiplier=oldmultiplier
								--iescount = iescount +1
						)
			if tempArr.count>0 then 
				(
					join allInstanceArr tempArr
				)

			)catch()
		)
		G_OBJ_UTIL.dotnetLog (" [STAsset.iesFN.end]\n ")
	),
	
	fn vrmapFN workMax workMax2 =(
		G_OBJ_UTIL.dotnetLog (" [STAsset.vrmapFN.Start].... ")
		try(
			local Allvrmap = #()
			if G_STCON.VRAY_IRRMAP_FILE != undefined and G_STCON.VRAY_IRRMAP_FILE != "" then
			(
				myRender = renderers.production
				vrmappath = (G_OBJ_UTIL.analysePath G_STCON.VRAY_IRRMAP_FILE)
				join Allvrmap (getfiles ((getfilenamepath vrmappath)+(getfilenamefile vrmappath)+"*"))
				for i in Allvrmap do 
				(
					copyfile i (workMax2 +(filenamefrompath i))
					G_OBJ_UTIL.dotnetLog (i as string + "<<<=>>>" +(workMax2 +(filenamefrompath i)) as string )
				)
				
				try(
					if G_STCON.VRAY_IRRADIANCEMAP_MODE!=undefined and G_STCON.VRAY_IRRADIANCEMAP_MODE!="" then (
						myRender.adv_irradmap_mode=G_STCON.VRAY_IRRADIANCEMAP_MODE as integer
					)
				)catch(G_OBJ_UTIL.dotnetLog (" NO_irradmapFile" ))
				myRender.adv_irradmap_loadFileName = (workMax2 +(filenamefrompath vrmappath))
				
					
				vrlmappath = (G_OBJ_UTIL.analysePath G_STCON.VRAY_LIGHTCACHE_FILE)
				copyfile vrlmappath (workMax2 +(filenamefrompath vrlmappath))
				G_OBJ_UTIL.dotnetLog (vrlmappath as string + "<<<=>>>" +(workMax2 +(filenamefrompath vrlmappath)) as string )
					
				try(
					if G_STCON.VRAY_LIGHTCACHE_MODE!=undefined and G_STCON.VRAY_LIGHTCACHE_MODE!="" then (
						G_STCON.lightcache_mode=G_STCON.VRAY_LIGHTCACHE_MODE as integer
					)
				)catch(G_OBJ_UTIL.dotnetLog (" NO_LightCacheFile" ))
				myRender.lightcache_loadFileName = (workMax2 +(filenamefrompath vrlmappath))
				
			)else(G_OBJ_UTIL.dotnetLog (" NO_VRayMap" ))
		)catch(print "IES_error_____")
		G_OBJ_UTIL.dotnetLog (" [STAsset.vrmapFN.End]\n ")
	),
	
	fn vrayFileFN workMax workMax2 = (
		G_OBJ_UTIL.dotnetLog (" [STAsset.vrayFileFN.Start].... ")
		try
		(
			local hdris = getClassInstances VRayHDRI
			local VRayHDRIcount = 0
			for hd in hdris do	(
				if hd.HDRIMapName!=undefined then (
					if (getfilenametype hd.HDRIMapName)!=".ifl" then 
					(
						beforePath = (G_OBJ_UTIL.analysePath hd.HDRIMapName)
						texfiletype = getfilenametype beforePath
						bitNum = G_OBJ_UTIL.fillLeftZero VRayHDRIcount 5
						afterPath = (workMax2 +"VRayHDRI"+ bitNum as string +texfiletype)
						
						copyfile beforePath afterPath
						hd.HDRIMapName=afterPath
						VRayHDRIcount = VRayHDRIcount+1
					)
					else if (getfilenametype hd.HDRIMapName) == ".ifl" then
					(
						G_OBJ_UTIL.dotnetLog ("IFL ___ HDR::"+hd.HDRIMapName)
						if DoesFileexist (G_OBJ_UTIL.analysePath hd.HDRIMapName) then
						(
							local iflArr = #()	
							local iflFile = openfile (G_OBJ_UTIL.analysePath hd.HDRIMapName)
							while not eof iflFile do append iflArr (readline iflFile)
							close iflFile
							for ii in iflArr do 
							(
								local ifiFilepath = (G_OBJ_UTIL.analysePath ii)
								if (getfilenamepath ii)!="" and (DoesFileExist ifiFilepath) then
								(
									ftstr = (getfilenamefile ii)
									texfiletype = (getfilenametype ii)
									---IflFilenumber = ftstr[ftstr.count-3]+ftstr[ftstr.count-2]+ftstr[ftstr.count-1]+ftstr[ftstr.count]
								copyfile ifiFilepath (workMax2 +(filenamefrompath ii))
								)
								else
								(
									ftstr = (getfilenamefile ii)
									texfiletype = (getfilenametype ii)
									---IflFilenumber = ftstr[ftstr.count-3]+ftstr[ftstr.count-2]+ftstr[ftstr.count-1]+ftstr[ftstr.count]
								copyfile ((getfilenamepath (G_OBJ_UTIL.analysePath hd.HDRIMapName)) + (filenamefrompath ii)) (workMax2 +(filenamefrompath ii))
								)
							)
							beforePath = (G_OBJ_UTIL.analysePath  hd.HDRIMapName)
							afterPath = (workMax2 +(filenamefrompath hd.HDRIMapName))					
							copyfile beforePath afterPath
							hd.HDRIMapName = afterPath		
						)else(G_OBJ_UTIL.dotnetLog "IFL File Missing")						
					)
				)
			)
		)catch(
		G_OBJ_UTIL.dotnetLog (" NO_VRayHDRI")
		)
		
			
		try(
			local ies = getClassInstances VRayIES
			local VRayIEScount = 0
			local arrvrayies = #()
			for i in ies do(
				if i.ies_file!=undefined then (
					local oldpower = i.power
					bitNum = G_OBJ_UTIL.fillLeftZero VRayIEScount 5
					beforePath = G_OBJ_UTIL.analysePath i.ies_file
					texfiletype = getfilenametype beforePath
					--afterPath = (workMax2 +"VRayIES"+ bitNum as string +texfiletype)
					
					if (finditem arrvrayies beforePath) == 0 then
					(
						VRayIEScount += 1
						append arrvrayies beforePath
						append arrvrayies (bitNum as string)
					)
					afterPath = (workMax2 +"VRayIES"+arrvrayies[(finditem arrvrayies beforePath)+1]as string +".ies")
					
					copyfile beforePath afterPath
					i.ies_file=afterPath
					G_OBJ_UTIL.dotnetLog (beforePath as string + "<<<=>>>" +afterPath as string )
					
					i.power = oldpower
					
					--VRayIEScount =VRayIEScount +1
				)
				
			)
		)catch(
			G_OBJ_UTIL.dotnetLog ("NO_VRayIES")
			G_OBJ_UTIL.dotnetLog (getcurrentException() as string)		
		)
			
			
		try(
			local vrayBmpArr = getClassInstances VRayBmpFilter
			local VRayBmpFiltercount = 0
			for myObj in vrayBmpArr do (
				if myObj.filename!=undefined then (
					bitNum = G_OBJ_UTIL.fillLeftZero VRayBmpFiltercount 5
					Fnewnetpath = G_OBJ_UTIL.analysePath myObj.filename
					texfiletype = getfilenametype Fnewnetpath
					copyfile Fnewnetpath (workMax2 +"VRayBit"+ bitNum as string +texfiletype)
					myObj.filename=(workMax2 +"VRayBit"+ bitNum as string +texfiletype)
					VRayBmpFiltercount = VRayBmpFiltercount+1
				)
			)
		)catch(
			G_OBJ_UTIL.dotnetLog ("NO_VRayBmpFilter")
			G_OBJ_UTIL.dotnetLog (getcurrentException() as string)	
		)
		
		try(
			local vrMeshArr=getclassinstances vrayproxy
			local arrvrmesh = #()
			local proxyscount = 0
			for myMesh in vrMeshArr do (
				print myMesh.filename
				if  myMesh.filename!=undefined then (
					bitNum = G_OBJ_UTIL.fillLeftZero proxyscount 5
					beforePath = (G_OBJ_UTIL.analysePath myMesh.filename)
					
					--vrmeshfiletype = getfilenametype beforePath
					--afterPath = (workMax2 +"VRmesh"+ bitNum as string +".vrmesh")
					
					if (finditem arrvrmesh beforePath) == 0 then
					(
						proxyscount += 1
						append arrvrmesh beforePath
						append arrvrmesh (bitNum as string)
					)
					
					afterPath = (workMax2 +"VRmesh"+ arrvrmesh[(finditem arrvrmesh beforePath)+1] as string +".vrmesh")
					copyfile beforePath afterPath
					myMesh.filename=afterPath
					
					
					G_OBJ_UTIL.dotnetLog ( beforePath as string + "<<<=>>>" +afterPath as string )
					--proxyscount = proxyscount+1
				)
				
			)
		)catch(
			G_OBJ_UTIL.dotnetLog ("NO_vrayproxy")
		)
		G_OBJ_UTIL.dotnetLog (" [STAsset.vrayFileFN.End]\n ")
	),
	
	fn pointCacheFN workMax workMax2 =(
		G_OBJ_UTIL.dotnetLog (" [STAsset.pointCacheFN.start].... ")
		local pcArr = #()
		local AllpointFile = #()
		local pointCachecount = 0
		try(
			pcArr = getClassInstances  Point_Cache
		)catch(
			G_OBJ_UTIL.dotnetLog ("NO_Point_Cache")
		)
		try(
			
			local pcwsmArr =  getClassInstances Point_CacheSpacewarpModifier
			join pcArr pcwsmArr
		)catch(
			G_OBJ_UTIL.dotnetLog ("NO_Point_CacheSpacewarpModifier")
		)			
		for myFile in pcArr do (
			if myFile.filename!=undefined then (
				local oldPlaybackType=undefined
				local oldPlaybackStart=undefined
				local oldPlaybackEnd=undefined
				try(
					oldPlaybackType=myFile.playbackType
					oldPlaybackStart=myFile.playbackStart
					oldPlaybackEnd=myFile.playbackEnd
				)catch()
					bitNum = G_OBJ_UTIL.fillLeftZero pointCachecount 5
					Fnewnetpath = G_OBJ_UTIL.analysePath  myFile.filename
					texfiletype = getfilenametype Fnewnetpath
					join AllpointFile (getfiles ((getfilenamepath Fnewnetpath) + (getfilenamefile Fnewnetpath) +"*"))
					for i in AllpointFile do 
					(
						copyfile i (workMax2 + (filenamefrompath i))
						myFile.filename=(workMax2 + (filenamefrompath myFile.filename))
				--myFile.filename=resultFile
					)
					pointCachecount = pointCachecount+1
				try(
					myFile.playbackType=oldPlaybackType
					myFile.playbackStart=oldPlaybackStart
					myFile.playbackEnd=oldPlaybackEnd
				)catch()
				
			)
		)
		G_OBJ_UTIL.dotnetLog (" [STAsset.pointCacheFN.end]\n")
	),
	
	fn refileCacheFN workMax workMax2 =(
		G_OBJ_UTIL.dotnetLog (" [refileCacheFN].Start.... ")
		try(
			local arr = getclassinstances RF_Cache
			for a in arr do (
			
			try(
				local oldrfrecStart = a.recStart
				local oldrfrecEnd = a.recEnd
				local oldrfrecStep = a.recStep
			)catch()
			
				local resultreFileName=G_OBJ_UTIL.analysePath a.Filename
				if resultreFileName!=undefined then 
				(

					copyfile resultreFileName (workMax2 +(filenamefrompath resultreFileName))
					a.Filename=(workMax2 +(filenamefrompath resultreFileName))

					G_OBJ_UTIL.dotnetLog (resultreFileName+ "<<<=>>>"+a.Filename)
				
				
					try(
						a.recStart = oldrfrecStart
						a.recEnd = oldrfrecEnd
						a.recStep = oldrfrecStep
					)catch()
				)
			)
		)catch(
			G_OBJ_UTIL.dotnetLog ("NO_refileCache")	
		)
		G_OBJ_UTIL.dotnetLog (" [refileCacheFN].End\n")
	),
	
	fn vrayScannedFN workMax workMax2 =(
		G_OBJ_UTIL.dotnetLog (" [VRayScannedMtl].Start.... ")
		try(
			local vrscanned = getclassinstances VRayScannedMtl
			for a in vrscanned do (
			
				local resultscanFileName=G_OBJ_UTIL.analysePath a.Filename
				if resultscanFileName!=undefined and resultscanFileName!="" then 
				(

					copyfile resultscanFileName (workMax2 +(filenamefrompath resultscanFileName))
					a.Filename=(workMax2 +(filenamefrompath resultscanFileName))

					G_OBJ_UTIL.dotnetLog (resultscanFileName+ "<<<=>>>"+a.Filename)
				
				)
			)
		)catch(
			G_OBJ_UTIL.dotnetLog ("NO_vrayScanned")	
		)
		G_OBJ_UTIL.dotnetLog (" [VRayScannedMtl].End\n")
	),
-------------------------------------------------------------Alembic-------------------------------------------------st
	fn AlembicFN workMax workMax2 = (
		G_OBJ_UTIL.dotnetLog (" [Alembic_Mesh_Geometry].Start.... ")
		try(
			--local Alembiccount = 0
			local arr = getclassinstances Alembic_Mesh_Geometry 
			for a in arr do (
				local AlembicFile = a.path
				local resultAlembicName=G_OBJ_UTIL.analysePath AlembicFile
				
				if resultAlembicName!=undefined then (
					--bitNum = G_OBJ_UTIL.fillLeftZero Alembiccount 5

					copyfile resultAlembicName (workMax2 +(filenamefrompath resultAlembicName))
					a.path=(workMax2 +(filenamefrompath resultAlembicName))
					--Alembiccount = Alembiccount+1
					G_OBJ_UTIL.dotnetLog ("Alembic_Mesh    "+a.path)
				)
				
			)
		)catch(
			G_OBJ_UTIL.dotnetLog ("NO_Alembic_Mesh_Geometry")	
		)
		G_OBJ_UTIL.dotnetLog (" [Alembic_Mesh_Geometry].End\n")
		
		
		G_OBJ_UTIL.dotnetLog (" [Alembic_AlembicCamera].Start.... ")
		try(
			--local Alembiccount = 0
			local arr = getclassinstances AlembicCamera
			for a in arr do (
				local AlembicFile = a.source
				local resultAlembicName=G_OBJ_UTIL.analysePath AlembicFile
				
				if resultAlembicName!=undefined then (
					--bitNum = G_OBJ_UTIL.fillLeftZero Alembiccount 5

					copyfile resultAlembicName (workMax2 +(filenamefrompath resultAlembicName))
					a.source=(workMax2 +(filenamefrompath resultAlembicName))
					--Alembiccount = Alembiccount+1
					G_OBJ_UTIL.dotnetLog ("AlembicCamera    "+a.source)
				)
				
			)
		)catch(
			G_OBJ_UTIL.dotnetLog ("NO_AlembicCamera")	
		)
		G_OBJ_UTIL.dotnetLog (" [AlembicFN_AlembicCamera].End\n")
		
		
		G_OBJ_UTIL.dotnetLog (" [AlembicFN_AlembicObject].Start.... ")
		try(
			--local AlembicOBJcount = 0
			local arr = getclassinstances AlembicObject 
			for a in arr do (
				local AlembicFile = a.source
				local resultAlembicName=G_OBJ_UTIL.analysePath AlembicFile
				
				if resultAlembicName!=undefined then (
					--bitNum =  G_OBJ_UTIL.fillLeftZero AlembicOBJcount 5
					
					copyfile resultAlembicName (workMax2 +(filenamefrompath resultAlembicName))
					a.source=(workMax2 +(filenamefrompath resultAlembicName))
					--AlembicOBJcount = AlembicOBJcount+1
					G_OBJ_UTIL.dotnetLog ("AlembicObjectPath   "+a.source)
				)
				
			)
		)catch(
			G_OBJ_UTIL.dotnetLog ("NO_AlembicObject")
		)
		G_OBJ_UTIL.dotnetLog (" [AlembicFN_AlembicObject].End\n")
	),
-------------------------------------------------------------Alembic-------------------------------------------------end

-------------------------------------------------------------KrakatoaPRTLoader---------------------------------------st
	fn KrakatoaPRTLoaderFN workMax workMax2= (
		G_OBJ_UTIL.dotnetLog (" [KrakatoaPRTLoader].Start ")
		try(
			local AllallPRTLoaderfile = #()
			local krakatoaPRTLoaderList = getclassinstances KrakatoaPRTLoader
			for myKrakatora in krakatoaPRTLoaderList do 
				(
					if myKrakatora.fileList.count>0 then
					(
						for ii = 1 to myKrakatora.fileList.count do 
							(
								
								local PRTLoaderFile = myKrakatora.fileList[ii]
								local resultPRTLoaderName=G_OBJ_UTIL.analysePath PRTLoaderFile
										
								if resultPRTLoaderName!=undefined then 
								(
									local kkname=""
									if (getfilenamefile resultPRTLoaderName ).count>4 then
									(
										for str = 1 to (getfilenamefile resultPRTLoaderName).count-2 do
										(
											append kkname (getfilenamefile resultPRTLoaderName)[str]
										)
									)
					
									allPRTLoaders = getfiles (substituteString ((getfilenamepath resultPRTLoaderName)+kkname+"*")"\\" "/")
									join AllallPRTLoaderfile allPRTLoaders
									
									format "a1...%\n"  allPRTLoaders
									
									for i in AllallPRTLoaderfile do 
										(
											copyfile i (workMax2 + (filenamefrompath i))
											myKrakatora.fileList[ii]=(workMax2 + (filenamefrompath i))
										)
									
								)
							format "a2...%\n" myKrakatora.fileList[ii]
							)
					)
				)
		)catch(
			G_OBJ_UTIL.dotnetLog ("NO_KrakatoaPRTLoader")
		)
		G_OBJ_UTIL.dotnetLog (" [KrakatoaPRTLoader].End\n")
		
	),
-------------------------------------------------------------KrakatoaPRTLoader---------------------------------------end
	
-------------------------------------------------------------phoenixFN-----------------------------------------------st
	fn phoenixFN workMax workMax2= (
		
		-------------------------PHXSimulator-------------------------
		G_OBJ_UTIL.dotnetLog (" [phoenixFN_PHXSimulator].Start.... ")
		try(
			local AllSimulatorFile = #()
			local arr = getclassinstances PHXSimulator
			for a in arr do (
				-------------------------input
				local phoenixFileInput = a.rendinput
				if  phoenixFileInput!=undefined and not (matchPattern  phoenixFileInput pattern:"$*" ) then(
				
					Fnewnetpath = G_OBJ_UTIL.analysePath a.rendinput
					PHXinputfile = getfiles (substituteString Fnewnetpath "####" "*")
					
					join AllSimulatorFile PHXinputfile
					
					for i in AllSimulatorFile do 
					(
						copyfile i (workMax2 + (filenamefrompath i))
					)
					a.rendinput=(workMax2 + (filenamefrompath a.rendinput))
				)
				-------------------------output
				local phoenixFileOutput = a.simoutput
				if  phoenixFileOutput!=undefined and not (matchPattern  phoenixFileOutput pattern:"$*" ) then(
						
						Fnewnetpath = G_OBJ_UTIL.analysePath a.simoutput
						PHXoutputfile = getfiles (substituteString Fnewnetpath "####" "*")
					
						join AllLiquidSimFile PHXoutputfile
					
						for i in AllLiquidSimFile do 
						(
							copyfile i (workMax2 + (filenamefrompath i))
						)
						a.simoutput=(workMax2 + (filenamefrompath a.simoutput))
				)
			)
		)catch(
			G_OBJ_UTIL.dotnetLog ("NO_PHXSimulator")	
		)
		G_OBJ_UTIL.dotnetLog (" [phoenixFN_PHXSimulator].End\n")
		
		
		-------------------------FireSmokeSim-------------------------
		G_OBJ_UTIL.dotnetLog (" [phoenixFN_FireSmokeSim].Start.... ")
		try(
			local AllSmokeSimFile = #()
			local arr = getclassinstances FireSmokeSim
			for a in arr do (
				-------------------------input
				local phoenixFileInput = a.rendinput
				if  phoenixFileInput!=undefined and not (matchPattern  phoenixFileInput pattern:"$*" ) then(
				
					Fnewnetpath = G_OBJ_UTIL.analysePath a.rendinput
					Fireinputfile = getfiles (substituteString Fnewnetpath "####" "*")
					
					join AllSmokeSimFile Fireinputfile
					
					for i in AllSmokeSimFile do 
					(
						copyfile i (workMax2 + (filenamefrompath i))
					)
					a.rendinput=(workMax2 + (filenamefrompath a.rendinput))
				)
				-------------------------output
				local phoenixFileOutput = a.simoutput
				if  phoenixFileOutput!=undefined and not (matchPattern  phoenixFileOutput pattern:"$*" ) then(
						
						Fnewnetpath = G_OBJ_UTIL.analysePath a.simoutput
						Fireoutputfile = getfiles (substituteString Fnewnetpath "####" "*")
					
						join AllLiquidSimFile Fireoutputfile
					
						for i in AllLiquidSimFile do 
						(
							copyfile i (workMax2 + (filenamefrompath i))
						)
						a.simoutput=(workMax2 + (filenamefrompath a.simoutput))
				)
			)
		)catch(
			G_OBJ_UTIL.dotnetLog ("NO_FireSmokeSim")	
		)
		G_OBJ_UTIL.dotnetLog (" [phoenixFN_FireSmokeSim].End\n")
		
		
		-------------------------LiquidSim-------------------------
		G_OBJ_UTIL.dotnetLog (" [phoenixFN_LiquidSim].Start.... ")
		try(
			local AllLiquidSimFile = #()
			local arr = getclassinstances LiquidSim
			for a in arr do (
				-------------------------input
				local phoenixFileInput = a.rendinput
				if  phoenixFileInput!=undefined and not (matchPattern  phoenixFileInput pattern:"$*" ) then(
				
					Fnewnetpath = G_OBJ_UTIL.analysePath a.rendinput
					siminputfile = getfiles (substituteString Fnewnetpath "####" "*")
					
					join AllLiquidSimFile siminputfile
					
					for i in AllLiquidSimFile do 
					(
						copyfile i (workMax2 + (filenamefrompath i))
					)
					a.rendinput=(workMax2 + (filenamefrompath a.rendinput))
				)
				-------------------------output
				local phoenixFileOutput = a.simoutput
				if  phoenixFileOutput!=undefined and not (matchPattern  phoenixFileOutput pattern:"$*" ) then(
						
						Fnewnetpath = G_OBJ_UTIL.analysePath a.simoutput
						simoutputfile = getfiles (substituteString Fnewnetpath "####" "*")
					
						join AllLiquidSimFile simoutputfile
					
						for i in AllLiquidSimFile do 
						(
							copyfile i (workMax2 + (filenamefrompath i))
						)
						a.simoutput=(workMax2 + (filenamefrompath a.simoutput))
				)
			)
		)catch(
			G_OBJ_UTIL.dotnetLog ("NO_LiquidSim")	
		)
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
	
	
	fn realflowFN workMax workMax2 = (
		G_OBJ_UTIL.dotnetLog (" [realflowFN].Start ")
		
		
		try(
			local AllrefMesh = #()
			local allrefl = #()
			local rfMeshes1 = getClassInstances RFMeshLoader
			join allrefl rfMeshes1
			
			local rfMeshes2 = getClassInstances MeshLoader
			join allrefl rfMeshes2
			
			for rfMesh in allrefl do(
				local meshPath = rfMesh.path
				local meshprefix  = rfMesh.prefix
				local oldstart = rfMesh.start
				local oldoffset = rfMesh.offset
				local resultMeshPath=G_OBJ_UTIL.analysePath meshPath 
				
				if resultMeshPath!=undefined then (
			
					join AllrefMesh (getfiles (resultMeshPath + meshprefix + "*.bin"))
					
					for i in AllrefMesh do 
						(
							--print i
							copyfile i (workMax2 + (filenamefrompath i))
					
						)
					rfMesh.path=workMax2	
					
					G_OBJ_UTIL.dotnetLog (" [realflowFN].NewMeshPath="+rfMesh.path)
					--rfMesh.path=resultMeshPath
					rfMesh.start = oldstart
					rfMesh.offset = oldoffset

				)
				
			)
		)catch	(
			G_OBJ_UTIL.dotnetLog ("NO_RFMeshLoader")	
		)
			
			
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
			
			
		)catch(
				G_OBJ_UTIL.dotnetLog ("NO_ParticleLoader")
		)
			
			
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
			
			
		)catch(
			G_OBJ_UTIL.dotnetLog ("NO_RFSoftBody")
		)
		G_OBJ_UTIL.dotnetLog (" [realflowFN].End\n")
	),
	
	fn xmeshFN=(
		G_OBJ_UTIL.dotnetLog (" [xmeshFN].Start ")
		try(
			local cacheArr = getclassinstances XMeshLoader
			for mycache in cacheArr do (
				
				--showproperties mycache
				
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
		local netrendertxtfile = ("B:/plugins/max/script/user/"+G_STCON.USER_ID+"/netrender.txt")
		if doesFileExist  netrendertxtfile then
		(
			commonFN()
			G_OBJ_UTIL.dotnetLog (" [run].customScript <<NetRender>> ")
		)
		else
		(
			commonFN()
			bitmapFN G_STCON.WORK_HELPER_TASK_MAX G_STCON.WORK_RENDER_TASK_MAX
			iesFN G_STCON.WORK_HELPER_TASK_MAX G_STCON.WORK_RENDER_TASK_MAX
			vrayFileFN G_STCON.WORK_HELPER_TASK_MAX G_STCON.WORK_RENDER_TASK_MAX
			pointCacheFN G_STCON.WORK_HELPER_TASK_MAX G_STCON.WORK_RENDER_TASK_MAX
			vrmapFN G_STCON.WORK_HELPER_TASK_MAX G_STCON.WORK_RENDER_TASK_MAX
			KrakatoaPRTLoaderFN G_STCON.WORK_HELPER_TASK_MAX G_STCON.WORK_RENDER_TASK_MAX
			AlembicFN G_STCON.WORK_HELPER_TASK_MAX G_STCON.WORK_RENDER_TASK_MAX
			refileCacheFN G_STCON.WORK_HELPER_TASK_MAX G_STCON.WORK_RENDER_TASK_MAX
			vrayScannedFN G_STCON.WORK_HELPER_TASK_MAX G_STCON.WORK_RENDER_TASK_MAX
			phoenixFN G_STCON.WORK_HELPER_TASK_MAX G_STCON.WORK_RENDER_TASK_MAX
			--fumefxFN()
			realflowFN G_STCON.WORK_HELPER_TASK_MAX G_STCON.WORK_RENDER_TASK_MAX
			--xmeshFN()	
		)
	)
	
)

--fn rvRender userId taskId notRender renderFrame blockNumber totalBlock  kg jobName   outputPath optionArray currenttask  = (
fn doFN paramArray deleteModel:#() rendModel:#()  = (


	G_OBJ_UTIL.dotnetLog "\n\n------------------------------------------------------------[Start maxscript preprocess]--------------------------------------------------------\n\n"
	G_STCON.init  paramArray
	
	format "G_STCON.MAX_FROM=%\n" G_STCON.MAX_FROM
	IF G_STCON.MAX_FROM != "web" THEN
	(
		IF PATHISNETWORKPATH G_STCON.MAX_FILE THEN 
		(
			local MAXNETPATH = (substituteString G_STCON.MAX_FILE "//" "/")
			local LOCALMAXFILEPATH = G_STCON.WORK_HELPER_TASK_MAX + "net" + MAXNETPATH
			local loadResult = loadMaxFile localmaxfilepath useFileUnits:true quiet:true 
		)
		else
		(
			local MAXNETPATH = (substituteString G_STCON.MAX_FILE ":/" "/")
			local LOCALMAXFILEPATH = G_STCON.WORK_HELPER_TASK_MAX + MAXNETPATH
			format "MAXNETPATH=%\n" MAXNETPATH
			format "LOCALMAXFILEPATH=%\n" LOCALMAXFILEPATH
			local loadResult = loadMaxFile LOCALMAXFILEPATH useFileUnits:true quiet:true 
			
			
		)
	)
	else
	(
		format "MAXNETPATH=%\n" G_STCON.MAX_FILE
		
		local loadResult = loadMaxFile G_STCON.MAX_FILE useFileUnits:true quiet:true 
	)
	format "maxfileload%\n" loadResult
	if loadResult then
	(
		fn vrayPhotonRenderFN = (
			if G_STCON.MYKG!=undefined and G_STCON.MYKG!="0" then (




				renderWidth=G_STCON.MYWIDTH as integer
				renderHeight=G_STCON.MYHEIGHT  as integer
			)
			
			if G_STCON.VRAY_FILTER_KERNEL!=undefined and G_STCON.VRAY_FILTER_KERNEL!="" then (
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
		
			if G_STCON.MYKG=="100" then (--incremental add to current map
				renderers.production.gi_on=True 
					renderers.production.adv_irradmap_mode=4
					renderers.production.adv_irradmap_autoSave=true
					renderers.production.adv_irradmap_autoSaveFileName=G_STCON.WORK_RENDER_TASK_OUTPUT+G_STCON.TASK_ID+"_irrmap.vrmap"
			) else if G_STCON.MYKG=="101" then (--animation (prepass) rend map
				renderers.production.gi_on=True 
					renderers.production.adv_irradmap_mode=6
					renderers.production.adv_irradmap_autoSave=true
					renderers.production.adv_irradmap_autoSaveFileName=G_STCON.WORK_RENDER_TASK_OUTPUT+G_STCON.TASK_ID+"_animation.vrmap"
				
			) else if  G_STCON.MYKG=="102" then (--fast rend map
				renderers.production.gi_on=True 
					renderers.production.adv_irradmap_autoSave=true
					renderers.production.adv_irradmap_mode=4
					renderers.production.adv_irradmap_autoSaveFileName=G_STCON.WORK_RENDER_TASK_OUTPUT+G_STCON.TASK_ID+"_irrmap.vrmap"
			)
			
			if G_STCON.VRAY_SECONDARY_GIENGINE == "3" then (---lightcache 
				renderers.production.gi_on=True 
					if G_STCON.VRAY_LIGHTCACHE_MODE != undefined  and G_STCON.VRAY_LIGHTCACHE_MODE == "1" then
					(
						renderers.production.lightcache_mode=1
						renderers.production.lightcache_autoSave=true
						renderers.production.lightcache_autoSaveFileName=G_STCON.WORK_RENDER_TASK_OUTPUT+G_STCON.TASK_ID+"_lightcache.vrlmap"
					)
			)
		)
		
		fn vrayPhotonloadFN = (
			
			if G_STCON.MYKG=="100" then (--incremental add to current map
				renderers.production.gi_on=True 
					renderers.production.adv_irradmap_mode=2
					renderers.production.adv_irradmap_loadFileName=G_STCON.WORK_RENDER_TASK_MAX+"photon/"+G_STCON.TASK_ID+"_irrmap.vrmap"
		
			) else if G_STCON.MYKG=="101" then (--animation (prepass) rend map
				renderers.production.gi_on=True
					renderers.production.adv_irradmap_mode=7
					renderers.production.adv_irradmap_loadFileName=G_STCON.WORK_RENDER_TASK_MAX+"photon/"+G_STCON.TASK_ID+"_animation.vrmap"
		
			) else if  G_STCON.MYKG=="102" then (--fast rend map
				renderers.production.gi_on=True 
					renderers.production.adv_irradmap_mode=2
					renderers.production.adv_irradmap_loadFileName=G_STCON.WORK_RENDER_TASK_MAX+"photon/"+G_STCON.TASK_ID+"_irrmap.vrmap"
			)
			
			if G_STCON.VRAY_SECONDARY_GIENGINE == "3" then (---lightcache 
				renderers.production.gi_on=True 
					if G_STCON.VRAY_LIGHTCACHE_MODE != undefined  and G_STCON.VRAY_LIGHTCACHE_MODE == "1" then
					(
						renderers.production.lightcache_mode=2
						renderers.production.lightcache_loadFileName=G_STCON.WORK_RENDER_TASK_MAX+"photon/"+G_STCON.TASK_ID+"_lightcache.vrlmap"
					)
			)
			
		)
		
		if G_STCON.MYKG == "0" or G_STCON.MYKG == undefined then
		(
			local myAsset=STAsset()
			myAsset.runFN()
			saveMaxFile (G_STCON.WORK_RENDER_TASK_MAX+G_STCON.TASK_ID+".max")
		)
		else
		(
			local myAsset=STAsset()
			myAsset.runFN()
			vrayPhotonRenderFN()
			saveMaxFile (G_STCON.WORK_RENDER_TASK_MAX+G_STCON.TASK_ID+"_photon.max")
			
			vrayPhotonloadFN()
			saveMaxFile (G_STCON.WORK_RENDER_TASK_MAX+G_STCON.TASK_ID+".max")
			
		)
	)

    G_OBJ_UTIL.dotnetLog "\n\n------------------------------------------------------------[End maxscript preprocess]--------------------------------------------------------\n\n"
    G_OBJ_UTIL.dotnetLog "\n\n------------------------------------------------------------[_____KILL MAX_____]--------------------------------------------------------\n\n"
		

	
)


clearlistener()
--doFN #("1843589","1843500","9403082","pre-999","c:/work/helper/9403082/max/Quick Tix.max","1002","Cam_1","web")


