fn loadRayvision = (

	--Loading Assemblies:
	
	local rayvisionDll = (getDir #scripts)+"\\Rayvision\\Rayvision.dll"
	
	
	format "rayvisionDll...%\n" rayvisionDll
	local assembly = dotNetClass "System.Reflection.Assembly"
	assembly.loadfrom rayvisionDll
	global G_RAYVISION_DOT = dotnetobject "Rayvision.SubmitMax"
	global G_RAYVISION_CON = dotNetClass "Rayvision.Constant"
	print (G_RAYVISION_DOT.print "line-------line------mmmmm__________")
	print (G_RAYVISION_DOT.print "11111111111111")
	
	G_RAYVISION_CON.init()
	
	format "%\n" G_RAYVISION_CON.USER_ID
	format "%\n" G_RAYVISION_CON.AGENT
	format "%\n"  G_RAYVISION_CON.AGENT_ROLLOUT_NAME
)

loadRayvision()

