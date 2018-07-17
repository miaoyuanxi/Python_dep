
--(dotnetClass "Application").CurrentCulture = dotnetObject "System.Globalization.CultureInfo" "zh-cn"

	
	
fn UpdateMsFile = (
	try(
		env_file = "\""+(@"%appdata%\RenderBus\local\env.ini")+"\""
		env_folder = "C:\\ProgramData\\"
		HiddenDOSCommand ("xcopy /y /v /e " + env_file + " " + env_folder)
		InfoTxt = openFile (env_folder+"env.ini")
		skipToString InfoTxt "platform = "
		L_time = readLine InfoTxt
		close InfoTxt 
		Scpath = GetDir #scripts
		VS = (filterString Scpath "\\")
		MaxV = VS[VS.count-1]
		source_file = "\""+(@"%appdata%\RenderBus\"+L_time+"\\Module\\script\\submit_picture_max\\"+MaxV+"\\scripts\\Rayvision")+"\""
		dest_folder = ("\""+(Scpath +"\\Rayvision")+"\"")
		if doesFileExist  (Scpath +"\Rayvision\Rayvision.dll") then
		(
		HiddenDOSCommand ("xcopy /y /v /e " + source_file + " " + dest_folder)
		)
		else()
	)catch()
)
--UpdateMsFile()

Fn SetDefaultLanguageToChinese = 
(
    if (MaxVersion() )[1] >= 15000 do
    if "2052" != GetINISetting (GetMAXIniFile()) "File Language Options" "LanguageToUseForFileIO" do 
    (
        DialogMonitorOPS.UnRegisterNotification id:#SetDefaultLanguageToChinese
        Fn DialogMonitorCallBackSetDefaultLanguageToChinese = 
        (
            currentHandle = DialogMonitorOPS.GetWindowHandle()
            if "Preference Settings" == UIAccessor.GetWindowText currentHandle do
            (
                languageNames = #("Chinese","English","German","French","japanese","Korean","Current")
                childrens = Windows.getChildrenHWND currentHandle
                
                languageLabel = undefined 
                for tempControl in childrens where tempControl[5] == "Default Language:" do 
                (
                    languageLabel = tempControl
                )
                if languageLabel != undefined do
                for tempControl in childrens where 
                (
                    tempControl[2]==languageLabel[2] and \
                    tempControl[3]==languageLabel[3]  and \
                    "ComboBox" == tempControl[4] and \
                    FindItem languageNames tempControl[5] != 0
                )
                do
                (
                    UIAccessor.SendMessage tempControl[1] 0x014E 6 0
                )
                UIAccessor.SendMessageID currentHandle #IDOK
            )
            true
        )
        DialogMonitorOPS.RegisterNotification DialogMonitorCallBackSetDefaultLanguageToChinese id:#SetDefaultLanguageToChinese
        DialogMonitorOPS.Enabled = true
        DialogMonitorOPS.ShowNotification()
        max file preferences
        DialogMonitorOPS.UnRegisterNotification id:#SetDefaultLanguageToChinese
        DialogMonitorOPS.Enabled = false
    )
)
SetDefaultLanguageToChinese()

	
fn myLoadAssembly dllFile =(
	local assemblyStr=((dotnetClass "System.IO.File").ReadAllBytes dllFile)
	(dotnetClass "System.Reflection.Assembly").Load assemblyStr
)
	

	
fn createMenu =(
		local rayvisionDll = (getDir #scripts)+"\\Rayvision\\Rayvision.dll"
		--myLoadAssembly rayvisionDll
		dotNet.loadAssembly rayvisionDll
		global G_RAYVISION_DOT = dotnetobject "Rayvision.SubmitMax"
		global G_RAYVISION_CON = dotNetClass "Rayvision.Constant"
		G_RAYVISION_DOT.initCon()
		format "agent_label___%______%\n" G_RAYVISION_CON.AGENT_LABEL G_RAYVISION_DOT.isClient()
		global AgentName = G_RAYVISION_CON.AGENT_LABEL
		global RVInstall = G_RAYVISION_CON.INSTALL_DIR + "/QRenderBus.exe"
		format "INS_________%\n" RVInstall
		try (menuMan.unRegisterMenu (menuMan.findMenu AgentName))catch()
		renderbusmainMenu = menuMan.getMainMenuBar() 
		
		/*
		macroScript subTask category:"RenderBus" buttonText:"发布任务1" tooltip:"发布任务2" (
			try filein (getDir #scripts + @"\Rayvision\submit_max.mse") catch messagebox "加载失败，请重新安装插件！" title:"Rayvision" 
			
		)
			
		*/
		macroStr1 = "macroScript subTask category:\"RenderBus\" buttonText:\"发布任务\" (\n try filein (getDir #scripts + @\"\Rayvision\submit_max.mse\") catch messagebox \"加载失败，请重新安装客户端！\" title:\"瑞云渲染\" \n)"
		macroStr2 = "macroScript runBus category:\"RenderBus\" buttonText:\"运行客户端\" (\n shellLaunch RVInstall \"\" \n)"
		--format "%\n" macroStr1
		execute macroStr1
		execute macroStr2
		local bigMenu = menuMan.createMenu AgentName 
		renderbusmainMenu.addItem (menuMan.createSubMenuItem "bigMenu" bigMenu) (10) 
		for i = 1 to bigMenu.numItems() do bigMenu.removeItem (bigMenu.getItem i)
		bigMenu.addItem (menuMan.createActionItem "subTask" "RenderBus") 1
		bigMenu.addItem (menuMan.createSeparatorItem()) 2
		bigMenu.addItem (menuMan.createActionItem "runBus" "RenderBus") 3
		menuMan.updateMenuBar()
)

createMenu()