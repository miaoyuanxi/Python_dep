
fn fileinMS = (
	filein @"STMethods.ms"	----加载共用模块（方法）
	
	filein @"STLoadMax.ms"	----打开max文件
	
	filein @"STCommon.ms"	----设置共用参数（宽，高，输出路径等）
	
	filein @"STTexture.ms"	----设置贴图路径
	
	filein @"STCache.ms"	----设置缓存
	
	filein @"STRenderer.ms"	----设置渲染器参数
	
	filein @"STRender.ms"	----开始渲染
)

fileinMS()





fn web_render paramArray deleteModel:#() rendModel:#()  = (

	
	G_OBJ_UTIL.dotnetLog "\n\n------------------------------------------------------------[Start maxscript render]--------------------------------------------------------\n\n"

	G_STCON.init  paramArray
	
	G_OBJ_UTIL.dotnetLog ("\n\n-------------------[1/"+G_STCON.STEP_COUNT+"][G_STMethods]-------------------\n")

	G_STMethods_STConfigMax.initMaxFN()
		
	
	
	G_OBJ_UTIL.dotnetLog ("\n\n-------------------[2/"+G_STCON.STEP_COUNT+"][G_STLoadMax]-------------------\n")
	G_STLoadMax.runFN() 
	
	G_OBJ_UTIL.dotnetLog ("\n\n-------------------[3/"+G_STCON.STEP_COUNT+"][G_STCommon]-------------------\n")
	G_STCommon.runFN()
	
	G_OBJ_UTIL.dotnetLog ("\n\n-------------------[4/"+G_STCON.STEP_COUNT+"][G_STTexture]-------------------\n")
	G_STTexture.runFN()
	
	G_OBJ_UTIL.dotnetLog ("\n\n-------------------[5/"+G_STCON.STEP_COUNT+"][G_STCache]-------------------\n")
	G_STCache.runFN()
	
	G_OBJ_UTIL.dotnetLog ("\n\n-------------------[6/"+G_STCON.STEP_COUNT+"][G_STRenderer]-------------------\n")
	G_STRenderer.runFN()
	
	G_OBJ_UTIL.dotnetLog ("\n\n-------------------[7/"+G_STCON.STEP_COUNT+"][G_STRender]-------------------\n")
	G_STRender.runFN()
	
			
	
	
	G_OBJ_UTIL.dotnetLog ("\n\n-------------------[8/"+G_STCON.STEP_COUNT+"][Reset 3ds Max And exit]-------------------\n")
	
	G_STMethods_STConfigMax.resetMaxFN()
	
	G_OBJ_UTIL.dotnetLog "\n\n------------------------------------------------------------[End maxscript render]--------------------------------------------------------\n\n"
	G_OBJ_UTIL.dotnetLog "\n\n------------------------------------------------------------[_____KILL MAX_____]--------------------------------------------------------\n\n"
	sleep 5

	G_OBJ_UTIL.dotnetLog " --------------rvRender.end---------------"
	
)
--rvRender #("100001","279","false","25","Render_765","Camera001","Render","c:/work/render/279/output","c:/work/render/279/max/hh2014max.max", @"c:/work/render/279/cfg/task.json","0") 
