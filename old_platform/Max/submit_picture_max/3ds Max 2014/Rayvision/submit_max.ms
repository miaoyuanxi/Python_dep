
--G_RENDERBUS_DOT.ParentUserId  G_RENDERBUS_DOT.UserId G_RENDERBUS_DOT.UserName G_RENDERBUS_DOT.installDir G_RENDERBUS_DOT.PluginDir,G_RENDERBUS_DOT.ProjectDir


global Main_rollout
try(destroyDialog Main_rollout )catch()
global Render_setting_rollout,Help_rollout
global localtime_ini = "C:\\ProgramData\\localtime"+((((maxversion())[1])/1000-2)as string) +".cfg"
global R_Activecam = ""
global Activecam = #()
global Blocks = 1
global ThreadCount = 1
global Vray_Hight = false
global GIval = 1
global Distributeonoff = false

global with_Cam = "http://www.renderbus.com/support/post-id-1720"	--重名相机
global with_Elm = "http://www.renderbus.com/support/post-id-1718"	--重名通道
global with_All = "http://www.renderbus.com/support"	--帮助主页
global with_Ies = "http://www.renderbus.com/support/post-id-1913"	--ies丢失
global with_vfb = "http://www.renderbus.com/support/post-id-1716"
global with_ElP = "http://www.renderbus.com/support/post-id-1903" --通道路径

global MainName = G_RAYVISION_CON.AGENT_ROLLOUT_NAME --"直线云渲染 - LINECG.COM"
global AgentOutput = G_RAYVISION_CON.AGENT_OUTPUT --代理商输出名字"LinecgRender"
global AgentTitle = G_RAYVISION_CON.AGENT_TIPS --代理商提示
global AgenthelpLink = "true"

global progress_count="7" 

------------------------bakerender--str------------------
global SelectedCtrlLVItems=#()
global objID = #()
global bakeRenderonoff = 0
global allmyItem = ""

fn initListView lv =
   (
	   lv.gridLines = true 
	   lv.ForeColor = lv.ForeColor.black
	   lv.showitemtooltips = true
	   lv.View = (dotNetClass "System.Windows.Forms.View").Details
	   lv.fullRowSelect = true
	   lv.CheckBoxes = false
	   layout_def = #("物体ID","物体名称", "烘培元素数量","烘培尺寸")
   
		for i = 1 to layout_def.count do
		   (
			case i of
				(
				   1: lv.Columns.add layout_def[1] 55
				   2: lv.Columns.add layout_def[2] 80
				   3: lv.Columns.add layout_def[3] 85
				   4: lv.Columns.add layout_def[4] 75
				)
			)
    )
fn getObjectList  =
(
	local eleObjList = #()

	for obj in objects do
		(
			
			local bakeElemNum=obj.INodeBakeProperties.numBakeElements()
			if bakeElemNum>0 then 
				(
					append eleObjList obj
					append objID obj.inode.handle
				)
		)
	eleObjList
)
fn fillInSpreadSheet lv lists =
(
	theRange = #()
	for obj in lists do 
		(
		
			local bakeElemNum=obj.INodeBakeProperties.numBakeElements()
			
			local li = dotNetObject "System.Windows.Forms.ListViewItem" (obj.inode.handle as string)
			li.SubItems.add (obj.name)
			li.SubItems.add (bakeElemNum as string)
			
			local objBakElem =obj.INodeBakeProperties.getBakeElement 1
			local objBakElemWidth = objBakElem.outputSzX as string 
			local objBakElemHeight = objBakElem.outputSzY as string 
			li.SubItems.add (objBakElemWidth+"*" +objBakElemHeight)
			
			append theRange li
		)
	
	lv.Items.AddRange theRange

)
------------------------bakerender--end----------------


--___________________________________________________________________________________________________________
initResult = G_RAYVISION_DOT.initCon()

fn getMaxvStr = (
	local myMaxVersionInt=((maxversion())[1])/1000
	if myMaxVersionInt<=9 then (
		return "3ds Max "+(myMaxVersionInt as string)
	)else(
		return "3ds Max "+((2008+myMaxVersionInt-10) as string)
	)
	
	
)

fn getFormatRenderer =(
	local rendStr = ( classof renderers.production ) as string
	rendStr=toLower rendStr
	rendStr	=substituteString rendStr "v-ray " "vray"
	rendStr	=substituteString rendStr "v_ray_" "vray"
	rendStr	=substituteString rendStr "adv_" ""
	rendStr	=substituteString rendStr "demo_" ""
	rendStr	=substituteString rendStr " " ""
	rendStr	=substituteString rendStr "_" "."
	rendStr
)

fn getProjectInfo project=(
	--local maxv = "3ds Max " +project.MaxVersion
	local plugList = project.PluginArray
	local str = "" 
	for plu in plugList do (
		str = str +(substituteString plu "|" "")+" "
	)
	str
)

fn setIni myPath myType myKey myVal= (
	
	SetINISetting myPath myType myKey myVal
)
--___________________________________________________________________________________________________________







fn autoCamera = (
	if viewport.getType () == #view_camera then (
		local activeCamera = getActiveCamera()
		if ((classof activeCamera) as string )!="Targetobject" then(
			format "ftttt........%\n" (viewport.getType () as string)
			Render_setting_rollout.Re_cam_list.items = #(activeCamera.name as string)
			free R_Activecam
			append R_Activecam activeCamera.name as string
		)
	)
)


	
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

struct STTips(
	tipsCode,
	tipsType,
	tipsList=#(),
	tipsLink
	
    
)
    
/*
检查结果的封装
resultName,结果名称，例如这个函数的目的是检查vrmesh没后缀名的，可以写成resultName="vrmeshWithoutExt"
infoList,信息列表，里面装的都是STInfo结构对象，对应的是各种错误，警告信息
configlist,配置信息列表，里面装的都是STConfig结构对旬，对应的是各种配置信息，最终会写到render.cfg的
*/
struct STResult (
    resultName,
    tipsList=#(),
    configlist=#()
    
    
)



struct STAnalyse(
	myResult=STResult(),
	
	fn getStrFromList tipsList = (
		local str = ""
		for tipStr in tipsList do (
			str = str + tipStr +"\r\n"
		)
		
		str
	),
	
	fn commonInfo =(
		format "-------commonINFO------\n"
		
		local frameStr = "0"
		if rendtimetype==1 then (--single
			frameStr= (currentTime.Frame as integer) as string --sliderTime.Frame
		)else if rendtimetype==2 then (--Active Time segment
			local anStart = (animationRange.start.frame as integer) as string
			local anEnd =  (animationRange.end.frame as integer) as string 
			local nth = (rendNThFrame as integer) as string
			frameStr=anStart+"-"+anEnd +"["+nth+"]"
		)else if rendtimetype==3 then (--Ranage
			local nth =(rendNThFrame as integer) as string
			local start = (rendStart.frame as integer) as string
			local end = (rendEnd.frame as integer) as string
			frameStr=start+"-"+end +"["+nth+"]"				
			
		)else if rendtimetype==4 then(--Frames
			local frames = rendPickupFrames 
			if frames!=undefined and frames!="" then (			
				frameStr=frames
			)			
		)
		
		append myResult.configlist (STConfig ckey:"filegamma" cval:(IDisplayGamma.colorCorrectionMode as string) ctype:"common")	
		append myResult.configlist (STConfig ckey:"kg" cval:"0" ctype:"common")
		append myResult.configlist (STConfig ckey:"from" cval:"3dsmax" ctype:"common")
		append myResult.configlist (STConfig ckey:"update" cval:"20170610" ctype:"common")
		append myResult.configlist (STConfig ckey:"sceneproject" cval:maxfilepath ctype:"common")
		append myResult.configlist (STConfig ckey:"scenefile" cval:(maxfilepath+maxfilename) ctype:"common")
		append myResult.configlist (STConfig ckey:"cgfile" cval:(maxfilepath+maxfilename) ctype:"common")
		append myResult.configlist (STConfig ckey:"alloutputtype" cval:"tga,tif,jpg,png,rla,rpf,exr" ctype:"client")
		append myResult.configlist (STConfig ckey:"allelemtype" cval:"tga,tif,jpg,png,rla,rpf,exr" ctype:"client")
		append myResult.configlist (STConfig ckey:"cameradelimiter" cval:"[,]" ctype:"renderSettings")
		
		if Render_setting_rollout.rendertype.state == 2 and Render_setting_rollout.lv_objects.Items.Count != 0 then
		(
			Activecam.count = 1
			append myResult.configlist (STConfig ckey:"renderablecamera" cval:"BAKERENDERCAMERA" ctype:"renderSettings")
			append myResult.configlist (STConfig ckey:"isbakerender" cval:"true" ctype:"common")
			append myResult.configlist (STConfig ckey:"isPicture" cval:"false" ctype:"common")
			append myResult.configlist (STConfig ckey:"tiles" cval:"1" ctype:"renderSettings")
			append myResult.configlist (STConfig ckey:"frames" cval:("1-"+ Render_setting_rollout.lv_objects.Items.Count as string+"[1]") ctype:"renderSettings")
			append myResult.configlist (STConfig ckey:"bakeobjectids" cval:(allmyItem as string) ctype:"renderSettings")			
		)
		else
		(
			append myResult.configlist (STConfig ckey:"isBakerender" cval:"false" ctype:"common")
			if (classof renderers.production) == vray then
			(
			append myResult.configlist (STConfig ckey:"distribute" cval:(Distributeonoff as string) ctype:"vray")
			)
			else
			(
			append myResult.configlist (STConfig ckey:"distribute" cval:"false" ctype:"vray")
			Render_setting_rollout.distribute_switch.checked = false	
			)
			append myResult.configlist (STConfig ckey:"isPicture" cval:"true" ctype:"common")
			append myResult.configlist (STConfig ckey:"tiles" cval:(Blocks as string) ctype:"renderSettings")
			append myResult.configlist (STConfig ckey:"distributenode" cval:(ThreadCount as string) ctype:"vray")
			append myResult.configlist (STConfig ckey:"frames" cval:(((sliderTime as string ) as integer) as string) ctype:"renderSettings")
			--append myResult.configlist (STConfig ckey:"renderablecamera" cval:(Activecam[1] as string) ctype:"renderSettings")
				if Activecam.count >0 then
				(
					APPcam=""
					if Activecam.count>=2 then 
					(
						for iii =1 to  Activecam.count-1 do 
						(
							append APPcam (Activecam[iii]+"[,]")
						)
					append myResult.configlist (STConfig ckey:"renderablecamera" cval:((APPcam+Activecam[Activecam.count]) as string) ctype:"renderSettings")
					)
					else 
					(
					append 	APPcam Activecam[1]
					append myResult.configlist (STConfig ckey:"renderablecamera" cval:(APPcam as string) ctype:"renderSettings")	
					)
				)
		)		
		append myResult.configlist (STConfig ckey:"width" cval:(renderWidth as string) ctype:"renderSettings")	
		append myResult.configlist (STConfig ckey:"height" cval:(renderheight as string) ctype:"renderSettings")
		append myResult.configlist (STConfig ckey:"RenderType" cval:(getRenderType() as string) ctype:"TD")

		append myResult.configlist (STConfig ckey:"giframes" cval:(((sliderTime as string ) as integer) as string) ctype:"vray")
		append myResult.configlist (STConfig ckey:"giwidth" cval:((renderWidth/Render_setting_rollout.GI_w.value) as string) ctype:"vray")	
		append myResult.configlist (STConfig ckey:"giheight" cval:((renderheight/Render_setting_rollout.GI_w.value) as string) ctype:"vray")
		
		local animationRangeStart=((animationRange.Start as string)as integer) as string
		local animationRangeEnd=((animationRange.End as string)as integer) as string
		--append myResult.configlist (STConfig ckey:"animationRange" cval:(animationRangeStart+"-"+animationRangeEnd) ctype:"renderSettings")

		append myResult.configList (STConfig ckey:"rendSaveFile" cval:(rendSaveFile as string) ctype:"renderSettings")
		append myResult.configList (STConfig ckey:"locationoutput" cval:(getfilenamepath rendOutputFilename) ctype:"common")
		append myResult.configList (STConfig ckey:"rendOutputFilename" cval:(rendOutputFilename as string) ctype:"renderSettings")
		--append myResult.configList (STConfig ckey:"output" cval:rendOutputFilename ctype:"renderSettings")
		
		local outBaseName=getfilenamefile rendOutputFilename
		local outBaseType=getfilenametype rendOutputFilename
		local ltime = getlocaltime()
		local hz = ""
		for i = ltime.count-4 to ltime.count-2 do (append hz (ltime[i] as string))
		append myResult.configList (STConfig ckey:"output" cval:(outBaseName+"_"+hz+outBaseType) ctype:"renderSettings")
			
		--append myResult.configlist (STConfig ckey:"output" cval:(rendOutputFilename as string) ctype:"renderSettings")

		--append myResult.configlist (STConfig ckey:"renderablecamera" cval:(Activecam[1] as string) ctype:"renderSettings")
		append myResult.configlist (STConfig ckey:"cgv" cval:("3ds Max "+(1998+(((maxversion())[1])/1000 )) as string) ctype:"common")
		
		append myResult.configlist (STConfig ckey:"max" cval:((maxFilePath+maxFileName) as string)  ctype:"max")
		
		if IDisplayGamma.colorCorrectionMode == #gamma then(
			append myResult.configlist (STConfig ckey:"gamma" cval: "on" ctype:"renderSettings")
			append myResult.configlist (STConfig ckey:"gammaval" cval: (IDisplayGamma.gamma as string) ctype:"renderSettings")
			append myResult.configlist (STConfig ckey:"ingamma" cval: (fileInGamma as string) ctype:"renderSettings")
			append myResult.configlist (STConfig ckey:"outgamma" cval: (fileOutGamma as string) ctype:"renderSettings")
		)else(
			append myResult.configlist (STConfig ckey:"gamma" cval: "off" ctype:"renderSettings")
		)
	),
	
	fn textureInfo =(
		local maxFileScene = G_RAYVISION_DOT.analysePath (maxfilepath+maxfilename)
		texList = #() 
		ATSOps.Refresh()
		Atsops.getFiles &texList
		for tex in texList do(
			if tex==undefined or tex=="" then(
				continue
			)
			if tex!=(maxfilepath+maxfilename) and  (ATSOps.IsInputFile tex) then(
				local txtScene = G_RAYVISION_DOT.analysePath tex
				local Truepath = mapPaths.getFullFilePath  tex
				if doesFileExist Truepath then (
					append myResult.configlist (STConfig ckey:"path" cval:(Truepath+">>"+txtScene) ctype:"texture")
				)else(
					local pathReally = mapPaths.getFullFilePath (filenamefrompath  tex)
					if doesFileExist pathReally then (
						append myResult.configlist (STConfig ckey:"path" cval:(pathReally+">>"+txtScene) ctype:"texture")
					)else(
						append myResult.configlist (STConfig ckey:"warn" cval:tex ctype:"warn")
					)
					
				)
				--append myResult.configlist (STConfig ckey:"Asset" cval:tex ctype:"TD")	
			)
		)
		
	),

	fn vrayInfo =(
		
		format "vray.....\n"
		local myRender = renderers.production
		local renderType=classOf myRender as string
		if Vray_Hight == true then
		(
			append myResult.configlist (STConfig ckey:"render" cval:"V_Ray_Adv_3_40_01" ctype:"common")
		)
		else
		(
			append myResult.configlist (STConfig ckey:"render" cval:(renderType as string) ctype:"common")	
		)
		if classof myRender == vray   then(
			myRender.system_frameStamp_on = false 
			if myrender.output_on == on then (----------- VFB
				append myResult.configlist (STConfig ckey:"vfb" cval:"on" ctype:"vray")
				append myResult.configlist (STConfig ckey:"vrwidth " cval:(myrender.output_width as string) ctype:"vray")
				append myResult.configlist (STConfig ckey:"vrheight " cval:(myrender.output_height as string) ctype:"vray")
				if myrender.output_splitgbuffer == off then 
				(
				myrender.output_splitgbuffer = on
				append myResult.configlist (STConfig ckey:"VFB_Elements_out" cval:"off" ctype:"vray")
				)
				else
				(
				append myResult.configlist (STConfig ckey:"VFB_Elements_out" cval:(myrender.output_splitgbuffer as string) ctype:"vray")	
				)
				if myrender.output_splitfilename ==undefined or myrender.output_splitfilename == "" then (
					local tipsStr = "勾选了VFB 未设置输出路径"
					append myResult.tipsList (STTips tipsType:"error" tipsList:#(tipsStr) tipsLink:with_vfb) 
				)else (
					append myResult.configlist (STConfig ckey:"vfbsavepath" cval:(myrender.output_splitfilename as string) ctype:"vray")
					local vfbname = (getfilenamefile myrender.output_splitfilename)
					local vfbtype = (getfilenametype myrender.output_splitfilename)
					append myResult.configlist (STConfig ckey:"vfbsavename" cval:((vfbname+vfbtype)as string) ctype:"vray")
				)
			)else(
				append myResult.configlist (STConfig ckey:"vfb " cval:" off" ctype:"vray")						
			)
			
			append myResult.configlist (STConfig ckey:"imageSampler_type" cval:(myRender.imageSampler_type as string) ctype:"vray")
			if myrender.options_displacement == true then
			(
				append myResult.configlist (STConfig ckey:"displacement" cval:"1" ctype:"vray")
			)else(append myResult.configlist (STConfig ckey:"displacement" cval:"0" ctype:"vray"))
			if myrender.options_reflectionRefraction == true then
			(
				append myResult.configlist (STConfig ckey:"reflectionRefraction" cval:"1" ctype:"vray")	
			)else(append myResult.configlist (STConfig ckey:"reflectionRefraction" cval:"0" ctype:"vray"))			
			if myRender.gi_on == true then (-------------GI
				
				append myResult.configlist (STConfig ckey:"gi" cval:"on" ctype:"vray")	
				append myResult.configlist (STConfig ckey:"primarygiengine" cval:(myRender.gi_primary_type as string) ctype:"vray")
				append myResult.configlist (STConfig ckey:"secondarygiengine" cval:(myRender.gi_secondary_type as string) ctype:"vray")	
				append myResult.configlist (STConfig ckey:"irradiancemapmode" cval:(myRender.adv_irradmap_mode as string) ctype:"vray")
				append myResult.configlist (STConfig ckey:"lightcachemode" cval:(myRender.lightcache_mode as string) ctype:"vray")	
				
				--append myResult.configlist (STConfig ckey:"lightcachefile" cval:(myRender.lightcache_loadFileName as string) ctype:"vray")
				append myResult.configlist (STConfig ckey:"memLimit" cval:(myRender.system_raycaster_memLimit as string) ctype:"vray")
				append myResult.configlist (STConfig ckey:"Default geometry" cval:(myRender.system_instancedObjects as string) ctype:"vray")
				
				
				if myRender.gi_primary_type == 0 then (
					if (myRender.adv_irradmap_mode == 2 )or (myRender.adv_irradmap_mode == 7) then (
						local vrmap=myRender.adv_irradmap_loadFileName 
						if vrmap==undefined or vrmap=="" then (
							local tipsStr = "发光贴图文件路径未设置"
							append myResult.tipsList (STTips tipsType:"error" tipsList:#(tipsStr) tipsLink:with_All) 
						)else(
							if  doesFileExist vrmap  then(
								local vrmapScene = G_RAYVISION_DOT.analysePath vrmap
								append myResult.configlist (STConfig ckey:"irrmapfile" cval:vrmap ctype:"vray")
								append myResult.configlist (STConfig ckey:"path" cval:(vrmap+">>"+vrmapScene as string) ctype:"customfile")
							)else(
								local vrmap2 = (mapPaths.getFullFilePath vrmap)
								if   doesFileExist vrmap2  then(
									local vrmapScene = G_RAYVISION_DOT.analysePath vrmap
									append myResult.configlist (STConfig ckey:"irrmapfile" cval:(vrmap as string) ctype:"vray")
									append myResult.configlist (STConfig ckey:"path" cval:(vrmap2+">>"+vrmapScene as string) ctype:"customfile")
								)else(
									local tipsStr="发光贴图文件丢失" +vrmap
									append myResult.tipsList (STTips tipsType:"error" tipsList:#(tipsStr) tipsLink:with_All)
								)
							)
							
						)
						
					)						
				)
				
				
				if myRender.gi_secondary_type == 3 then (
					if myRender.lightcache_mode == 2 then (
						local vrlmap =  myRender.lightcache_loadFileName 
						if vrlmap==undefined or vrlmap=="" then (
							local tipsStr = "灯光缓存文件路径未设置"
							append myResult.tipsList (STTips tipsType:"error" tipsList:#(tipsStr) tipsLink:with_All) 
						)else(
							if  doesFileExist vrlmap  then(
								local vrlmapScene = G_RAYVISION_DOT.analysePath vrlmap
								append myResult.configlist (STConfig ckey:"lightcachefile" cval:(vrlmap as string) ctype:"vray")
								append myResult.configlist (STConfig ckey:"path" cval:(vrlmap+">>"+vrlmapScene as string) ctype:"customfile")
							)else(
								local vrlmap2 = (mapPaths.getFullFilePath vrlmap)
								if   doesFileExist vrlmap2  then(
									local vrlmapScene = G_RAYVISION_DOT.analysePath vrlmap
									append myResult.configlist (STConfig ckey:"lightcachefile" cval:vrlmap ctype:"vray")
									append myResult.configlist (STConfig ckey:"path" cval:(vrlmap2+">>"+vrlmapScene as string) ctype:"customfile")
								)else(
									local tipsStr="灯光缓存文件丢失" +vrlmap
									append myResult.tipsList (STTips tipsType:"error" tipsList:#(tipsStr) tipsLink:with_All)
								)
							)
						)
						
					)
					else(print "1")
				)			
			)else (
				append myResult.configlist (STConfig ckey:"gi" cval:"off" ctype:"vray")
			)
			
			if  myRender.gi_on then (
				if myRender.gi_primary_type == 0 and ((myRender.adv_irradmap_mode == 2 ) or  (myRender.adv_irradmap_mode == 7) )then (--irradiance map 
				)else(
					if Blocks>1 and (Render_setting_rollout.rendertype.state == 1)  then (
						append myResult.configlist (STConfig ckey:"kg" cval:"100" ctype:"common")
					)
				)
				
				if myRender.gi_secondary_type == 3 or myRender.lightcache_mode == 2 then (
				)else(
					if Blocks>1 and (Render_setting_rollout.rendertype.state == 1) then (
						append myResult.configlist (STConfig ckey:"kg" cval:"100" ctype:"common")
					)
				)
			)else(
				if Blocks>1 and (Render_setting_rollout.rendertype.state == 1) then (
					append myResult.configlist (STConfig ckey:"kg" cval:"100" ctype:"common")
				)
			)
		/*
		local VrayMS = (GetDir #scripts) + "\Startup\vrayutils.ms"
		if doesFileExist VrayMS then 
		(
			VrayMSfile = openFile VrayMS 
			if	(skipToString VrayMSfile "材质") == ok or (matchPattern (myRender.system_frameStamp_string) pattern:"*文件*") ==true then
				(
					append myResult.configlist (STConfig ckey:"Vraylanguage" cval:"中文版Vray" ctype:"TD")	
				)
			close VrayMSfile
		)
		*/	
		)
		else
		(
			append myResult.configlist (STConfig ckey:"ABC" cval:"CBA"  ctype:"vray")
		)		
	
	),

	fn elementsInfo =(
		local re = maxOps.GetCurRenderElementMgr()
		local renderElementsMgr = maxOps.GetRenderElementMgr #Production
		local elementActive=renderElementsMgr.GetElementsActive()
		local allElements = ""
		local elem =#()
		local errElm = #()
		local dupElements=#()
		--elementStr=""
		local unpathelm =#()
		local elemCount = 1
		if elementActive==true then (
		append myResult.configlist (STConfig ckey:"elementactive" cval:"on" ctype:"renderSettings")	
		)
		else (
		append myResult.configlist (STConfig ckey:"elementactive" cval:"off" ctype:"renderSettings")		
		)
		if renderElementsMgr.numrenderelements()>0 then 
		(
			for n = 0 to (renderElementsMgr.numrenderelements()- 1) do
			(
				local el =( re.GetRenderElement n)
				append elem (el.elementName  as string)
				allElements= (allElements+(el.elementname as string +"[,]"))
				local selemPath = (renderElementsMgr.getRenderElementFilename n)as string
				--local selemnames = (renderElementsMgr.GetRenderElementFilename n)as string
					if (getfilenamepath selemPath) != "" then 
					(
					append myResult.configlist (STConfig ckey:("renderelement"+elemCount as string) cval:(el.elementName as string +"|"+selemPath as string) ctype:"renderSettings")
					elemCount = elemCount+1	
					)
					else
					(
					append unpathelm (el.elementName as string)
					)					
			)
			if unpathelm.count >0 then 
			(
			local elempathstr = ""
				for unelm in unpathelm do (
					elempathstr = elempathstr + (unelm as string)+","
				)
				local tipsList = #("有通道未指定输出路径:"+elempathstr)
				append myResult.tipsList (STTips tipsType:"error" tipsList:tipsList tipsLink:with_ElP)
			)
			local elemPath = renderElementsMgr.getRenderElementFilename 0
			local elemType=undefined
			if elemPath!=undefined then 
			(
				elemType=getfilenametype elemPath
			)
			if elemType==undefined or elemType=="" then 
			(
				if  rendOutputFilename!=undefined then 
				(
					local outputType = getfilenametype rendOutputFilename
					elemType=outputType
				)
				
			)
			if elemType==undefined or elemType=="" then (
				elemType="tga"
			)
			elemType = (filterString elemType ".")[1]
			append myResult.configlist (STConfig ckey:"elemtype" cval:elemType ctype:"renderSettings")
		)
		print allElements
		append myResult.configlist (STConfig ckey:"render element" cval:allElements ctype:"renderSettings")	
		for G_elm in elem do 
			(
			local eqcount = 0
			for GG_elm in elem do 
				(
				if G_elm == GG_elm then 
					(
					eqcount =eqcount+1
					)
				)
				if eqcount >1 then 
				(
				format "当前有重名的通道________%\n" G_elm
				--free errElm
				append errElm G_elm
				append dupElements G_elm
				)
			)
		if dupElements.count>0 then (
			local elemStr = ""
			for dupElem in dupElements do (
				elemStr = elemStr + (dupElem as string)+","
			)
			local tipsList = #("有同名通道:"+elemStr)
			append myResult.tipsList (STTips tipsType:"error" tipsList:tipsList tipsLink:with_Elm) 
		)

			
	),
	
	fn cameraInfo =(
		
		format "-------checkCameraInfo--------\n"
		
		local allcamList = ""
		local errCam = ""
		local inicamList = #()
		local dupCameraList=#()
		for  Allcam in cameras do 
		(
			if ((classof Allcam) as string )!="Targetobject" then
				(
				append  allcamList (Allcam.name as string +"[,]")
				append  inicamList Allcam.name as string
				)
		)
		append myResult.configlist (STConfig ckey:"allcamera" cval:(allcamList as string) ctype:"renderSettings")	
		if inicamList.count <=0 then
		(
		append tipsList "场景中没有相机"
		)
		for G_cam in inicamList do 
		(
			local eqcount = 0
			for GG_cam in inicamList do 
			(
				if G_cam == GG_cam then 
				(
					eqcount =eqcount+1
				)
			)
			if eqcount >1 then 
			(
				format "当前有重名的相机________%\n" G_cam
				append errCam G_cam
				--append tipsList G_cam
				append dupCameraList G_cam
			)
		)
		
		if dupCameraList.count>0 then (
			local camStr = ""
			for dupCam in dupCameraList do (
				camStr = camStr + dupCam+","
			)
			local tipsList = #("有同名相机:"+camStr)
			append myResult.tipsList (STTips tipsType:"error" tipsList:tipsList tipsLink:with_Cam) 
		)
		
	),
	
	fn iesInfo =(
		try(
			local dupIes=#()
			for i in lights do 
			(
				if (classof i) == Target_Light or (classof i) == Free_Light then
				(
				 if i.Distribution == 3 and (i.webfile =="" or i.webfile == undefined) then
					(
					print i.name
					append dupIes (i.name+",")
					)
				)
			)
			if dupIes.count>0 then (
				local iesStr = getStrFromList dupIes
				local tipsList = #("IES文件丢失::"+(iesStr as string))
				append myResult.tipsList (STTips tipsType:"error" tipsList:tipsList tipsLink:with_Ies) 
			
			)
		)catch("IES_error_____") 
	myResult
	),
	

	
	fn check = (
		commonInfo()
		cameraInfo()
		elementsInfo()
		iesInfo()
		textureInfo()
		vrayInfo()
		myResult
		
	)
	
)




rollout Render_setting_rollout "Render_setting" width:368 height:520
(
	spinner G_width "宽度：" pos:[40,220] width:70 height:16 range:[1,32768,renderWidth] type:#integer scale:1
	spinner G_Height "高度：" pos:[145,220] width:70 height:16 range:[1,32768,renderheight] type:#integer scale:1
	spinner G_Aspect "图像比例：" pos:[265,220] width:70 height:16 range:[0.001,32768.000,getRendImageAspect()] type:#float scale:0.01
	checkbutton G_lock "L" pos:[340,220] width:16 height:16 enabled:true checked:false
	GroupBox Pro_box "项目列表：" pos:[8,7] width:352 height:136
	dropdownList Pro_list "" pos:[16,28] width:336 height:22 items:#("Project", "默认项目1", "默认项目2", "默认项目3")
	label Pro_info "软件配置：空" pos:[19,55] width:330 height:48
	multiListBox Sc_cam_list "场景相机列表:" pos:[16,274] width:168 height:4 enabled:true selection:0
	HyperLink sj "(双击添加)" pos:[92,274] width:70 height:24 enabled:false color:(color 255 0 0)
	label PRO_TS1 "如需修改配置信息请先登录客户端，并打开右上角“设置”>“项目设置”>“添加渲染软件配置”，进行配置" pos:[16,105] width:336 height:30 enabled:false color:(color 240 100 100)
	multiListBox Re_cam_list "渲染相机列表：" pos:[192,275] width:160 height:4
	checkbox Block_switch "启用分块" pos:[1117,394] width:76 height:16 enabled:false checked:false
	radiobuttons Block_Count "" pos:[1196,396] width:72 height:48 enabled:true labels:#("2x2    ", "3x3    ", "4x4") default:1
	spinner GI_w "光子比例：1/" pos:[11311,396] width:45 height:16 range:[1,8,3] type:#integer scale:1
	GroupBox bl_box "极急速渲染：" pos:[8,375] width:352 height:124 
	label Block_help "注意:勾选使用vray3.0渲染速度会有所提升,但效果可能会产\n生差异." pos:[35,460] width:320 height:30 enabled:false --color:(color 220 200 0)
	edittext Save_path "" pos:[8,524] width:288 height:20 fieldwidth:2 readOnly:true
	button Save_but "文件..." pos:[304,524] width:50 height:20
	GroupBox grp14 "分辨率设置:" pos:[8,203] width:352 height:40
	GroupBox grp15 "相机:" pos:[8,252] width:352 height:113
	label lbl20 "》" pos:[184,314] width:8 height:14
	GroupBox grp20 "保存路径:" pos:[8,506] width:352 height:47
	--*****************************************************
	checkbox Vray_switch "使用vray3.0以上版本渲染" pos:[17,440] width:320 height:16 enabled:true checked:false
	checkbox distribute_switch "开启极急速渲染" pos:[17,400] width:110 height:16 enabled:true checked:false toolTip:"开启后，所选核数越多渲染时间越短，另外所选核数不同，根据渲染时间长短计费标准也不同，详情请查阅官网上面的计费标准"
	radiobuttons distribute_Count "" pos:[35,420] width:72 height:48 enabled:false labels:#("48核     ", "80核     ", "96核     ","192核") default:1
	--*****************************************************
	--dotNetControl bq_neirong "System.Windows.Forms.Label" pos:[0,33] width:218 height:1
-------------------------------
	groupBox grp16 "渲染方式:" pos:[8,155] width:352 height:40
	radiobuttons rendertype "" pos:[60,172] width:373 height:32 enabled:true labels:#("效果图渲染                                ", "烘培渲染") default:1 
	
 	dotNetControl lv_objects "System.Windows.Forms.ListView" BackColor:(dotnetClass "System.Drawing.Color").gray  pos:[1113,56] width:352 height:230
	button btn_delement "删除通道并移除列表" pos:[11119,377] width:120 height:20 
	button btn_Remove "从渲染列表移除" pos:[1117,377] width:90 height:20 toolTip:"Select objects Removed in the list." enabled:false
	button btn_refresh "重新读取" pos:[1280,376] width:80 height:24 toolTip:"All objects in the scene with the uvwunwrap modifier are displayed in the list." enabled:false
	GroupBox delele "" pos:[1113,366] width:230 height:35
	HyperLink abt "注意:“烘培渲染” 为特殊渲染方式如不需要请不要选择此选项" pos:[1113,32] width:368 height:24 enabled:false color:(color 0 180 180)
	local rendercamList = #()
	
---------------------------------	
	on Render_setting_rollout open do ----------------界面打开
	(
		--********************************bake
		local objList = getObjectList()
		initListView lv_objects
		fillInSpreadSheet lv_objects objList
		lv_objects.enabled = false
		--********************************
		renderSceneDialog.close()
		rendertype.state = 1
		global camList = #()
		for  Allcam in cameras do 
		(
			if ((classof Allcam) as string )!="Targetobject" then
			(
				append  camList Allcam.name as string
			)
		)
		format "camlist____%\n" camList
		Sc_cam_list.items = camList
		Save_path.text = rendOutputFilename
		if viewport.getType () == #view_camera then 
		(
			local Accam = getActiveCamera()
			if ((classof Accam) as string )!="Targetobject" then
			(
				append Activecam Accam.name as string
				append R_Activecam Accam.name as string
			)
			Re_cam_list.items = Activecam
			for re = 1 to camList.count do
			(		
				if camList[re] == Accam.name as string then
				(
					deleteItem camList re
					Sc_cam_list.items = camList
				)
			)
		)
		if (classof renderers.production) == vray then
		(
		Blocks=1
		ThreadCount=3
		Block_Count.enabled =false 
		GI_w.enabled =false
		Distributeonoff = true
		distribute_switch.checked = true 
		distribute_Count.enabled =true			
		)
		if rendOutputFilename == "" then
		(	
			Save_path.text = rendOutputFilename ="C:\\"+AgentOutput+"_Download\\"+AgentOutput+".tga"
		)
		else
		(
			local types = ""
			local rendertypess = #(".tga",".tif",".jpg",".png",".rla",".rpf",".exr",".bmp")
			for is = 1 to rendertypess.count do
			(
				if (getfilenametype rendOutputFilename) == rendertypess[is] then
				(
					types = is 
				)
			)
			if types != "" then 
			(
				rendOutputFilename = (getfilenamepath rendOutputFilename)+(getfilenamefile rendOutputFilename)+rendertypess[types]
				Save_path.text = rendOutputFilename
			)
			else
			(
				rendOutputFilename = (getfilenamepath rendOutputFilename)+(getfilenamefile rendOutputFilename)+".tga"
				Save_path.text = rendOutputFilename
			)
		)		
	callbacks.removeScripts id:#testCallback
	callbacks.addScript #filePreOpenProcess "DestroyDialog Main_rollout" id:#testCallback	
	)
	on G_width changed val do  ---渲染宽度
	(
		if G_lock.checked == true then
		(
			G_Height.value = ((G_width.value)/(G_Aspect.value)) as integer
			renderWidth = G_width.value
			renderheight = G_Height.value
		)
		else
		(
			G_Aspect.value = ((G_width.value as float)/(G_Height.value as float))
			renderWidth = G_width.value
		)
	)
	on G_Height changed val do  -- 渲染高度
	(
		if G_lock.checked == true then
		(
			G_width.value = ((G_Height.value)*(G_Aspect.value))as integer
			renderheight = G_Height.value
			renderWidth = G_width.value
		)
		else
		(
			G_Aspect.value = ((G_width.value as float)/(G_Height.value as float))
			renderheight = G_Height.value	
		)
	)
	on G_Aspect changed val do
	(
		if G_lock.checked != true then
		(
			G_Height.value = ((G_width.value as float)/(G_Aspect.value as float))
			renderheight = G_Height.value
		)
		else
		()	
	)
	on G_lock changed state do
	(
		if G_lock.checked == true then
		(
		G_Aspect.enabled = false
		)
		else
		(
		G_Aspect.enabled = true
		)
	)
	on Pro_list selected i do
	(

		local currentProjectName = Pro_list.items[i]
		format "You selected '%'!\n" currentProjectName
		
		local maxV=(getMaxvStr())
		local rendStr = getFormatRenderer()
		local projectCfg = G_RAYVISION_DOT.getProjectCfg    (i-1) maxV rendStr
		format "project........%\n" (projectCfg as string)
		Pro_info.text=""
			
			
		local cfgStr = maxV+"\r\n"+rendStr
		
		if projectCfg==undefined then (
			Pro_info.text=cfgStr
			
		)else(
			
			local str =getProjectInfo projectCfg
			Pro_info.text=cfgStr+"\r\n"+str
		)
		if Pro_list.selected != 1 then 
		(
			PRO_TS1.enabled =true 
		)
	)
	on Sc_cam_list doubleClicked sel do ---------------场景相机
	(
		try(

		if sel != 0 then 
			( 
			append Activecam Sc_cam_list.items[sel]
			)

		Re_cam_list.items = Activecam
		deleteItem camList sel
		sort camList
		Sc_cam_list.items = camList
		append R_Activecam (Sc_cam_list.items[sel] as string)
			if Re_cam_list.items.count >1 then 
			(	
			--messagebox "不能分块"
			Block_switch.enabled =false
			Block_switch.checked =false
			Block_help.enabled =false
			Block_Count.enabled =false 
			GI_w.enabled =false
			Blocks=1
			)
			else
			(
			--Block_switch.enabled =true
			)
		)catch()			
	)
	on Re_cam_list doubleClicked sel do ---------------渲染相机
	(
		if sel != 0 then 
			( 
			append camList Re_cam_list.items[sel]
			)
		Sc_cam_list.items = camList
		deleteItem Activecam sel
		sort Activecam
		Re_cam_list.items = Activecam
		if Re_cam_list.items.count >1 then 
			(	
			--messagebox "不能分块"
			--Block_switch.enabled =false
			--Block_switch.checked =false
		--	Blocks=1	
			)
			else
			(
			--Block_switch.enabled =true
			)
	)
	on Block_switch changed stat do ------------分块渲染开关
	(
		if Block_switch.checked == true then
		(
			Block_help.enabled =true 
			Block_Count.enabled =true 
			GI_w.enabled =true 
			Block_Count.state = 1
			Blocks=4
		)
		else
		(
			Block_help.enabled =false
			Block_Count.enabled =false 
			GI_w.enabled =false
			Blocks=1
		)
	)
	/*
	on Block_Count changed stat do  -------- 分块块数选择
	(
	
		if Block_Count.state == 2 then 
		(
			Blocks=9
			
		)
		if Block_Count.state == 3 then 
		(
			Blocks=16
		)
		if Block_Count.state == 1 then
		(
			Blocks=4
		)
	)
	*/
	on distribute_switch changed stat do ------------分布渲染开关
	(
		if distribute_switch.checked == true then
		(
			local locrender = (classof renderers.production)
			if locrender == vray then
			(
			distribute_Count.enabled =true
			ThreadCount=3
			Distributeonoff = true
			)
			else
			(
			messagebox ("分布式只支持Vray渲染器 当前为："+locrender as string+" 请切换") title:AgentTitle beep:off
			distribute_switch.checked = false 	
			)
		)
		else
		(
			distribute_Count.enabled =false 
			ThreadCount=1
			Distributeonoff = false
		)

	)
	
	on Vray_switch changed stat do ------------使用vray3.0开关
	(
		if Vray_switch.checked == true then
		(
			local locrender = (classof renderers.production)
			if locrender == vray and (locrender as string)[11] != "3" then
			(
			Vray_switch.enabled =true
			Vray_Hight=true
			)
			else
			(
			messagebox ("只限3.0以下版本的vray使用") title:AgentTitle beep:off
			Vray_switch.checked = false 	
			)
		)
		else
		(
			Vray_switch.enabled =false
		)

	)
	--/*
	on distribute_Count changed stat do  -------- 分布线程选择
	(
	
		if distribute_Count.state == 2 then 
		(
			ThreadCount=5
			
		)
		if distribute_Count.state == 3 then 
		(
			ThreadCount=6
		)
		if distribute_Count.state == 4 then 
		(
			ThreadCount=12
		)
		if distribute_Count.state == 1 then
		(
			ThreadCount=3
		)
	)
	--*/
	on Save_but pressed do    ------输出路径选择
	(
		thePath = getSaveFileName filename:(getfilenamefile rendOutputFilename) types:"Targa Image File (*.tga, *.vda, *.icb, *.vst)|*.tga|JPEG File (*.jpg,*.jpe, *.jpeg)|*.jpg|BMP Image File (*.bmp)|*.bmp|OpenEXRImage File (*.exr, *.fxr)|*.exr|PNG Image File (*.png)|*.png|TIF Image File (*tif, *tiff)|*.tif|RLA Image File (*.rla)|*.rla|"		--format "**%\n" thePath.types
		if thePath != undefined then 
			(
				if rendertype.state != 2 then
				(
				Save_path.text = thePath
				rendOutputFilename = thePath
				)
				else
				(
				Save_path.text = (getfilenamepath thePath)
				rendOutputFilename = thePath
				)
			)
			
	)
	on sle_Cam changed stat do
	(
		if sle_Cam.checked == true then
			(
			if viewport.getType () == #view_camera then 
			(
			local G_Acam = getActiveCamera()
		
			if ((classof G_Acam) as string )!="Targetobject" then
				(
				Re_cam_list.items = #(G_Acam.name as string)
				free R_Activecam
				append R_Activecam (G_Acam.name as string)
				)
	
			)	
			callbacks.removeScripts id:#autoCam
			callbacks.addScript #viewportChange "autoCamera()" id:#autoCam	
			)
		else
			(			
			callbacks.removeScripts id:#autoCam
			)
	)
--==========================================================================================
	on rendertype changed stat do  -------- 渲染模式选择
	(
		if rendertype.state == 2 then
		(
		Save_but.text = "目录..."
		Save_path.text = (getfilenamepath rendOutputFilename)
		grp14.pos = [1118,203] --分辨率设置
		G_width.pos = [1140,220] --宽度
		G_Height.pos = [1145,220] --高度
		G_Aspect.pos = [1265,220] --图像比例
		G_lock.pos = [1340,220] --L
			
		grp15.pos = [1118,252] --相机
		Sc_cam_list.pos = [1116,274] --"场景相机列表 = "
		sj.pos = [1192,274] --"(双击添加)"
		Re_cam_list.pos = [1192,275] --渲染相机列表：
			
		bl_box.pos = [1118,375] --"分块渲染："
		Block_switch.pos = [1117,394] --"启用分块"
		Block_Count.pos = [1196,396] --2*2 3*3
		GI_w.pos = [1311,396] --"光子比例：1/"
		Block_help.pos = [1135,460] ---帮助
		lbl20.pos = [1184,314]
			
		distribute_switch.pos = [1196,450]  --分布式
		distribute_Count.pos = [1135,420]  --分布式线程
		Vray_switch.pos = [1117,440]
		--------------------------------------------
		lv_objects.pos = [8,230]
		btn_delement.pos = [110,475] -- "移除后不再添加" 
		btn_Remove.pos = [13,475] -- "从渲染列表移除" 
		btn_refresh.pos = [280,475] -- "重新读取" 
		delele.pos = [8,465] -- "" 
		abt.pos = [8,210] --注意
		
		
		bakeRenderonoff = 1
		lv_objects.enabled = true
		btn_Remove.enabled = true
		--delelement.enabled = true
		btn_refresh.enabled = true
			
		)
		if rendertype.state == 1 then
		(
		Save_but.text = "文件..."
		Save_path.text =  rendOutputFilename
		grp14.pos = [8,203] --分辨率设置
		G_width.pos = [98,220] --宽度
		G_Height.pos = [203,220] --高度
		G_Aspect.pos = [323,220] --图像比例
		G_lock.pos = [340,220] --L
			
		grp15.pos = [8,252] --相机
		Sc_cam_list.pos = [16,290] 
		sj.pos = [92,274] --"(双击添加)"
		Re_cam_list.pos = [192,291] --渲染相机列表：
			
		bl_box.pos = [8,375] --"分块渲染："
		Block_switch.pos = [1117,394] --"启用分块"
		Block_Count.pos = [1196,396] --2*2 3*3
		GI_w.pos = [11344,396] --"光子比例：1/"
		Block_help.pos = [35,460] ---帮助
		lbl20.pos = [184,314]
			
		distribute_switch.pos = [17,400]
		distribute_Count.pos = [35,420]
		Vray_switch.pos = [17,440]
		---------------------------------
		lv_objects.pos = [1113,56]
		btn_delement.pos = [1119,377] -- "移除后不再添加" 
		btn_Remove.pos = [1117,377] -- "从渲染列表移除" 
		btn_refresh.pos = [1280,376] -- "重新读取" 
		delele.pos = [11113,366] -- "" 
		abt.pos = [1113,32] --注意
		
		bakeRenderonoff = 0
		lv_objects.enabled = false
		btn_Remove.enabled = false
		--delelement.enabled = false
		btn_refresh.enabled = false
		

		)		
	)
    local oldObj =undefined
    fn getList=(
		
		local LV_ITEMS = #()
		for li=0 to (lv_objects.Items.Count - 1) do (append LV_ITEMS (lv_objects.Items.Item li))
		LV_ITEMS
	)
	fn listerfresh=(
		local temps = #()
		for i=0 to lv_objects.Items.Count-1 do
			(	
				local objs= lv_objects.items.item[i].text
				local myObj = maxOps.getNodeByHandle (objs as number)
				append temps myObj			
			)
		temps
		)
	on lv_objects Click do
		(
        deleteAllChangeHandlers id:#foo
		)
	on lv_objects DoubleClick do
	(   
		if oldObj!=undefined then 
			(
				deselect oldObj
			)
				local objID= lv_objects.SelectedItems.item[0].text
				try ( DestroyDialog gTextureBakeDialog) catch()
				local myObj = maxOps.getNodeByHandle  (objID as integer)
				oldObj=myObj
				select myObj
				macros.run "Render" "BakeDialog"
		when parameters myObj changes id:#foo handleAt:#redrawViews do
			(
				temp=#()
				for i=0 to lv_objects.Items.Count-1 do
					(
						local objs= lv_objects.items.item[i].text
						local myObj = maxOps.getNodeByHandle (objs as number)
						append temp	myObj
					)
				lv_objects.items.clear()
				fillInSpreadSheet lv_objects temp
			)
	)
	on btn_delement pressed do
	(
	local selectItems = lv_objects.SelectedItems
		for i=selectItems.count-1 to 0 by -1 do 
			(
				
				try destroydialog texelement catch ()
				rollout texelement "Remove Texture Elements"
					(  
						label texturelist "勾选“ 删除通道并移除列表 ”选项，将删除元素的烘焙通道，点击“ 确认移除 ”后，移除列表的元素不再刷新 到列表中。" style_sunkenedge:false pos:[12,6] width:280 height:45 
						button btn_addele "确认移除" pos:[80,60] width:60 height:25 
						button btn_cancel "取消移除" pos:[155,60] width:60 height:25
						--local selectItems = lv_objects.SelectedItems
						on btn_addele pressed do
						(
							local selectItems = lv_objects.SelectedItems
							for i=selectItems.count-1 to 0 by -1 do 
								(
									local objName = selectItems.item[i].text
									local myObj = maxOps.getNodeByHandle (objName as number)
									myObj.iNodeBakeProperties.removeAllBakeElements()
									lv_objects.items.removeat selectItems.item[i].index	
								)
							local temp2 = listerfresh()		
	                        lv_objects.items.clear()
	                        fillInSpreadSheet lv_objects temp2
							
								
							destroyDialog texelement
						)
						
						on btn_cancel pressed do
								(
									destroyDialog texelement 
								)
					)
			createDialog texelement 300 100
			)
		deleteAllChangeHandlers id:#foo	
	)
	on btn_Remove pressed do
	(
	local selectItems = lv_objects.SelectedItems
	for i=selectItems.count-1 to 0 by -1 do 
		
		(	
			lv_objects.items.removeat selectItems.item[i].index
		)
		
	local temp2 = listerfresh()		
	lv_objects.items.clear()
	fillInSpreadSheet lv_objects temp2
	deleteAllChangeHandlers id:#foo
	
	)
	on btn_refresh pressed do
	(
	 
		lv_objects.items.clear()
	    local objList = getObjectList()
		fillInSpreadSheet lv_objects objList
	    deleteAllChangeHandlers id:#foo
		
	)
	on btn_add pressed do
    (
		add_modifier()
		maps=fillInSpreadSheet lv_objects selection
		
	
    )
	fn bake_Submit =
	(
		if lv_objects.Items.Count >0 then 
		(
		for i=0 to lv_objects.Items.Count-1 do 
			(
				local myItem=lv_objects.items.item[i].text
				append allmyItem (myItem + ",")
			)
		bakecounts = lv_objects.Items.Count
		deleteAllChangeHandlers id:#foo
		)
	)
)

rollout Help_rollout "Help" width:480 height:550
(
	HyperLink err_info1 ""  width:350 height:24 enabled:false color:(color 255 0 0) address:"http://www.renderbus.com/" hovercolor:(color 0 255 255)
	HyperLink err_info2 ""  width:350 height:24 enabled:false color:(color 255 0 0) address:"http://www.renderbus.com/" hovercolor:(color 0 255 255)
	HyperLink err_info3 ""  width:350 height:24 enabled:false color:(color 255 0 0) address:"http://www.renderbus.com/" hovercolor:(color 0 255 255)
	HyperLink err_info4 ""  width:350 height:24 enabled:false color:(color 255 0 0) address:"http://www.renderbus.com/" hovercolor:(color 0 255 255)
	HyperLink err_info5 ""  width:350 height:24 enabled:false color:(color 255 0 0) address:"http://www.renderbus.com/" hovercolor:(color 0 255 255)
	HyperLink err_info6 ""  width:350 height:24 enabled:false color:(color 255 0 0) address:"http://www.renderbus.com/" hovercolor:(color 0 255 255)
	HyperLink err_info7 ""  width:350 height:24 enabled:false color:(color 255 0 0) address:"http://www.renderbus.com/" hovercolor:(color 0 255 255)
	HyperLink err_info8 ""  pos:[10,480] width:450 height:24 enabled:false color:(color 255 0 0) address:"http://www.renderbus.com/" hovercolor:(color 0 255 255)
)

rollout Main_rollout MainName width:392 height:750
(
	
	
	--______________________________________________________________________________________________
	dotNetControl tabs "System.Windows.Forms.TabControl" pos:[5,12] width:380 height:25
	subRollout commonSubRollout "" pos:[5,40] width:380 height:590
	subRollout tipSubRollout "" pos:[5,40] width:380 height:590 visible:false
	local tabSetting
	local tabTips
	
	--_______________________________________________________________________________________________
	
	
	button submitBtn "提交" pos:[288,646] width:96 height:46
	label Sub_prompt "" pos:[160,716] width:220 height:16 enabled:false
	HyperLink qq "联系客服" pos:[30,714] width:75 height:16 address:"http://www.renderbus.com/" color:(color 150 150 150)
	progressBar Pb_info "ProgressBar" pos:[8,676] width:264 height:16 value:1 color:(color 55 165 0)
	HyperLink Sc_prompt "" pos:[8,644] width:280 height:16 enabled:false color:(color 55 165 0)
	HyperLink Sc_prompt_ER "提交之前请先保存文件!" pos:[140,644] width:125 height:16 enabled:false color:(color 255 0 0)
	
	
	fn localTimeinfo = (
		try(
			InfoTxt = openFile localtime_ini
			skipToString InfoTxt "localTime="
			L_time = readLine InfoTxt
			Sub_prompt.caption =("上次提交时间:"+ L_time as string )		
			close InfoTxt 
		)catch()
	)
	
	--_______________________________________________________________________________________________
	fn initTab   =(
		
		tabs.tabPages.clear()
		--Set the size mode so that we can control their width. 
		--tabs.sizeMode=tabs.sizeMode.fixed
		--Set the width of every tab.
		--tabs.itemSize=dotnetObject "System.Drawing.Size" 60 25
		tabSetting = dotNetObject "System.Windows.Forms.TabPage" " 渲染设置 "
		tabTips = dotNetObject "System.Windows.Forms.TabPage" " 分析结果 "
		tabs.controls.add tabSetting
		tabs.controls.add tabTips
		tabTips.parent = undefined
		
		addSubRollout commonSubRollout Render_setting_rollout
		addSubRollout tipSubRollout Help_rollout
		
		tipSubRollout.visible=false
		
		
	)
	--_______________________________________________________________________________________________
	
	

	fn submitWork  theSender theEvent=(
		
		Sc_prompt.caption =("分析场景信息...")
		Pb_info.value =100.*1/7
		submitBtn.enabled = false				
		local analyse = STAnalyse()
		local analyseResult = analyse.check()
		format "tipList..count=======%\n" analyseResult.tipsList.count
		if analyseResult.tipsList.count >0 then(
			
			
			local linkH=10
			local linkCount=1
			for tips in analyseResult.tipsList do (
				local linkCountStr = linkCount as string
				local str = analyse.getStrFromList tips.tipsList
				local linkStr = tips.tipsLink as string
				execute("Help_rollout.err_info"+linkCountStr+".caption = \""+str+"\"")
				execute("Help_rollout.err_info"+linkCountStr+".address = \""+linkStr+"\"")
				execute("Help_rollout.err_info"+linkCountStr+".pos = [10,("+(linkH as string)+")]")
				execute("Help_rollout.err_info"+linkCountStr+".enabled = true")
				linkCount=linkCount+1
				linkH=linkH+20
			)
			
			
			
			tipSubRollout.visible=true
			commonSubRollout.visible=false
			tabTips.parent = tabs
			
			Main_rollout.tabs.SelectedIndex=1
			format "....end=======\n" 
			
			
		)else(
				
				
				
				
			Sc_prompt.caption =("(5/"+progress_count+")正在校验素材信息...")
			Sc_prompt_ER.caption =("<请勿关闭此界面!>")
			Pb_info.value =100.*5/7
			
			
			local textureCount=1
			local warnCount=1
			local vrmapcount=1
			local TdCount=1
			--local logPath=analyseTxt
			
			local timeArr = getLocalTime()
			local timeStr = timeArr[1] as string 
			timeStr=timeStr +(timeArr[2] as string )
			timeStr=timeStr +(timeArr[3] as string )
			timeStr=timeStr +(timeArr[4] as string )
			timeStr=timeStr +(timeArr[5] as string )
			timeStr=timeStr +(timeArr[6] as string )
			
			local projectTemp=G_RAYVISION_CON.PROJECT_DIR+"\\temp\\"
			local logPath=projectTemp+timeStr+".ini"
			
			if projectTemp !=undefined and (not doesFileExist projectTemp) then (
				makeDir projectTemp  all:true
			)
			
			for myConfig in analyseResult.configlist do (	
				format "%___%____%\n" myConfig.ctype myConfig.ckey myConfig.cval
				
				if myConfig.ctype=="texture" then (
					setIni logPath myConfig.ctype (myConfig.ckey+(textureCount as string)) myConfig.cval
					textureCount=textureCount+1
				)else if myConfig.ctype=="warn" then (
					setIni logPath myConfig.ctype (myConfig.ckey+(warnCount as string)) myConfig.cval
					warnCount=warnCount+1
				)else if myConfig.ctype=="TD" then (
					setIni logPath myConfig.ctype (myConfig.ckey+(TdCount as string)) myConfig.cval
					TdCount=TdCount+1
				)else if myConfig.ctype=="customfile" then (
					setIni logPath myConfig.ctype (myConfig.ckey+(vrmapcount as string)) myConfig.cval
					vrmapcount=vrmapcount+1
				)else(
					setIni logPath myConfig.ctype myConfig.ckey myConfig.cval
				)
			)
			

			
			--__________________________________________________________________________________________
			
			local subResult = G_RAYVISION_DOT.subTask  (maxfilepath + maxfilename) (getMaxvStr()) (getFormatRenderer()) logPath
			format "_%\n" subResult
			if (matchPattern subResult pattern:"OK_*") == true then
			(				
				Sc_prompt_ER.caption =("")
				Sc_prompt_ER.pos = [570,600]
				Sc_prompt.caption = (substituteString subResult "OK_" "")
				makedir ((getfilenamepath rendoutputfilename)+(substituteString subResult "OK_提交任务成功！ 任务号：" "")+"_"+(getfilenamefile maxFileName))
				--__________________________________________________________________________________________

				SetINISetting localtime_ini "Time" "localTime" localTime	
				Sub_prompt.caption = "上次提交时间："+localTime
				Pb_info.value =100
			)
			else
			(
				Sc_prompt_ER.caption =("")
				Sc_prompt_ER.pos = [570,600]
				Sc_prompt.color = (color 255 0 0)
				Sc_prompt.caption = subResult
	
			)
		)
		
		
		
	)
	
	fn getProjectWork  theSender theEvent=(
		format "getProjectWork....\r\n"
		G_RAYVISION_DOT.initProject()
		
		
		local projectNameList = G_RAYVISION_DOT.projectNameList
		
		
		if projectNameList!=undefined and projectNameList.count>0 then (
			Render_setting_rollout.Pro_list.items=projectNameList
			
			local currentProjectName = projectNameList[1]
			
			
			local maxV=(getMaxvStr())
			local rendStr = getFormatRenderer()
			local projectCfg = G_RAYVISION_DOT.getProjectCfg    0 maxV rendStr
			local rendStr = getFormatRenderer()
				
			local cfgStr = maxV+"\r\n"+rendStr
			if projectCfg==undefined then (
				Render_setting_rollout.Pro_info.text=cfgStr
				
			)else(
				
				local str =getProjectInfo projectCfg
				Render_setting_rollout.Pro_info.text=cfgStr+"\r\n"+str
			)
			submitBtn.enabled = true
			--format "projectCfgList....%....%\n" currentProjectName (project.PluginArray as string)
		)else(
			Render_setting_rollout.Pro_list.items=#()
			messagebox("获取项目列表失败!") title:AgentTitle beep:off
		)
		format "getProjectWork2....\r\n"
	)
	
	fn creatWorker methodName methodParam:#()=
	(
		BackgroundWorker = DotNetObject "System.ComponentModel.BackgroundWorker"
		if methodName=="getProjectWork" then (
			DotNet.AddEventHandler BackgroundWorker "DoWork"  getProjectWork
		)else if methodName=="submitWork"  then (
			DotNet.AddEventHandler BackgroundWorker "DoWork"  submitWork
		)
		BackgroundWorker.WorkerSupportsCancellation = true
		BackgroundWorker.RunWorkerAsync methodParam
		
		
	)
	
	
	
	on Main_rollout open do
	(
		format "--------\n"
		submitBtn.enabled = false
		autosave.Enable = false
		initTab() 
		localTimeinfo()
		G_RAYVISION_DOT.MaxFile=maxfilepath + maxfilename
		creatWorker "getProjectWork" methodParam:#("test1","test2")
		
	)
	
	--____________________________________________________________________________________________________________________
	on tabs mousedown arg do(
		--format "tabs.SelectedTab.TabIndex.....%\n" tabs.SelectedTab.TabIndex
		--try(
			--for x in commonSubRollout.rollouts do removeSubRollout commonSubRollout x
		--)catch()
		case tabs.SelectedTab.TabIndex of(
			default:(
				--addSubRollout commonSubRollout Render_setting_rollout
				commonSubRollout.visible=true
				tipSubRollout.visible=false
				
			)
			1:(
				--addSubRollout commonSubRollout Help_rollout
				commonSubRollout.visible=false
				tipSubRollout.visible=true
			)

		)
	)
	--____________________________________________________________________________________________________________________
	
	
	on Main_rollout close do
	(
		callbacks.removeScripts id:#autoCam
		autosave.Enable = true
	)

	on submitBtn pressed do
	(
		renderSceneDialog.close()
		if maxfilepath != "" then
		(
			if G_RAYVISION_DOT.isClient()=="0" then (
				if (Render_setting_rollout.Re_cam_list.items.count != 0) then
				(
					if makeDir (getfilenamepath rendoutputfilename) == true then
					(
						if Render_setting_rollout.rendertype.state == 2  then 
						(
							if Render_setting_rollout.lv_objects.Items.Count != 0 then
							(
							Sc_prompt_ER.caption =("")
							Render_setting_rollout.bake_Submit()
							Sc_prompt.caption = "正在保存场景..."
							max file save
							creatWorker "submitWork" methodParam:#("test1","test2")
							)
							else
							(
							messagebox "当前选择了“烘培渲染”场景中未发现可烘培物体，请切换成”效果图渲染“模式" title:AgentTitle beep:off
							)
						)
						else
						(
							Sc_prompt_ER.caption =("")
							Sc_prompt.caption = "正在保存场景..."
							max file save
							creatWorker "submitWork" methodParam:#("test1","test2")	
							--clearlistener()
						)
					)
					else
					(
						messagebox "输出路径不存在或无法写入,请更改为其他路径" title:AgentTitle beep:off
					)
				)
				else
				(
					if (Render_setting_rollout.rendertype.state == 1) then
					(
					messagebox "请添加相机至渲染相机列表"	 title:AgentTitle beep:off
					)
					else
					(
					if makeDir (getfilenamepath rendoutputfilename) == true then
					(
						if Render_setting_rollout.lv_objects.Items.Count != 0 then
						(
						Sc_prompt_ER.caption =("")
						Render_setting_rollout.bake_Submit()
						Sc_prompt.caption = "正在保存场景..."
						max file save
						creatWorker "submitWork" methodParam:#("test1","test2")
						)
						else
						(
						messagebox "当前选择了“烘培渲染”场景中未发现可烘培物体，请切换成”效果图渲染“模式" title:AgentTitle beep:off
						)
					)
					else
					(
						messagebox "输出路径不存在或无法写入,请更改为其他路径" title:AgentTitle beep:off
					)	
						
						
					)
				)
			)else(
				messagebox "请登录客户端!"  title:AgentTitle beep:off
			)
		)
		else 
		(
		messagebox "请先保存场景" title:AgentTitle beep:off
		)
	)
)

if G_RAYVISION_DOT.isClient()=="0" then (
createDialog Main_rollout lockheight:true lockwidth:true style:#(#style_titlebar, #style_border, #style_sysmenu, #style_resizing,#style_minimizebox)
)else (messagebox "请先登录客户端!" title:AgentTitle beep:off )