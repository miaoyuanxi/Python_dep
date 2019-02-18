from System import *
from System.Diagnostics import *
from System.IO import *

from Deadline.Plugins import *
from Deadline.Scripting import *

import socket, traceback

def GetDeadlinePlugin():
    return HoudiniPlugin()
    
def CleanupDeadlinePlugin( deadlinePlugin ):
    deadlinePlugin.Cleanup()
    
class HoudiniPlugin (DeadlinePlugin):
    completedFrames = 0
    ropType = ""
    
    def __init__( self ):
        self.InitializeProcessCallback += self.InitializeProcess
        self.RenderExecutableCallback += self.RenderExecutable
        self.RenderArgumentCallback += self.RenderArgument
        self.PreRenderTasksCallback += self.PreRenderTasks
        self.PostRenderTasksCallback += self.PostRenderTasks
    
    def Cleanup(self):
        for stdoutHandler in self.StdoutHandlers:
            del stdoutHandler.HandleCallback
        
        del self.InitializeProcessCallback
        del self.RenderExecutableCallback
        del self.RenderArgumentCallback
        del self.PreRenderTasksCallback
        del self.PostRenderTasksCallback
    
    def InitializeProcess( self ):
        self.SingleFramesOnly = False
        self.StdoutHandling = True
        self.PopupHandling = True
        
        self.AddStdoutHandlerCallback( "(Couldn't find renderer.*)" ).HandleCallback += self.HandleStdoutRenderer
        self.AddStdoutHandlerCallback( "(Error: Unknown option:.*)" ).HandleCallback += self.HandleStdoutUnknown
        self.AddStdoutHandlerCallback( "(Error: .*)" ).HandleCallback += self.HandleStdoutError
        self.AddStdoutHandlerCallback( ".*(Redshift cannot operate with less than 128MB of free VRAM).*" ).HandleCallback += self.HandleStdoutError
        self.AddStdoutHandlerCallback( ".*(No licenses could be found to run this application).*" ).HandleCallback += self.HandleStdoutLicense
        self.AddStdoutHandlerCallback( ".*ALF_PROGRESS ([0-9]+)%.*" ).HandleCallback += self.HandleStdoutFrameProgress
        self.AddStdoutHandlerCallback( ".*Render Time:.*" ).HandleCallback += self.HandleStdoutFrameComplete
        self.AddStdoutHandlerCallback( ".*Finished Rendering.*" ).HandleCallback += self.HandleStdoutDoneRender
        self.AddStdoutHandlerCallback( ".*ROP type: (.*)" ).HandleCallback += self.SetRopType
        self.AddStdoutHandlerCallback( ".*?(\d+)% done.*" ).HandleCallback += self.HandleStdoutFrameProgress
        
        self.AddPopupHandler( ".*Streaming SIMD Extensions Not Enabled.*", "OK" )
        
    def RenderExecutable( self ):
        version = self.GetPluginInfoEntryWithDefault( "Version", "16.0" ).replace( ".", "_" )
        build = self.GetPluginInfoEntryWithDefault( "Build", "none" ).lower()
        houdiniExeList = self.GetConfigEntry( "Houdini" + version + "_Hython_Executable" )
        
        if SystemUtils.IsRunningOnLinux():
            houdiniExeList = houdiniExeList.replace( "hython", "hython-bin" )
        
        houdiniExe = ""
        if SystemUtils.IsRunningOnWindows():
            if build == "32bit":
                self.LogInfo( "Enforcing 32 bit build" )
                houdiniExe = FileUtils.SearchFileListFor32Bit( houdiniExeList )
                if houdiniExe == "":
                    self.LogWarning( "Houdini " + version + " hython 32 bit executable was not found in the semicolon separated list \"" + houdiniExeList + "\". Checking for any executable that exists instead." )
            elif build == "64bit":
                self.LogInfo( "Enforcing 64 bit build" )
                houdiniExe = FileUtils.SearchFileListFor64Bit( houdiniExeList )
                if houdiniExe == "":
                    self.LogWarning( "Houdini " + version + " hython 64 bit executable was not found in the semicolon separated list \"" + houdiniExeList + "\". Checking for any executable that exists instead." )
            
        if houdiniExe == "":
            houdiniExe = FileUtils.SearchFileList( houdiniExeList )
            if houdiniExe == "":
                self.FailRender( "Houdini " + version + " hython executable was not found in the semicolon separated list \"" + houdiniExeList + "\". The path to the render executable can be configured from the Plugin Configuration in the Deadline Monitor." )
        
        if SystemUtils.IsRunningOnLinux():
            houdiniExe = houdiniExe.replace( "hython-bin", "hython" )
        
        return houdiniExe
        
    def RenderArgument(self):
        ifdFilename = self.GetPluginInfoEntryWithDefault( "IFD", "" ) 
        ifdFilename = RepositoryUtils.CheckPathMapping( ifdFilename )
        
        outputFilename = self.GetPluginInfoEntryWithDefault( "Output", "" ) 
        outputFilename = RepositoryUtils.CheckPathMapping( outputFilename )
        
        scene = self.GetPluginInfoEntryWithDefault( "SceneFile", self.GetDataFilename() )
        scene = RepositoryUtils.CheckPathMapping( scene )
        
        regionRendering = self.GetBooleanPluginInfoEntryWithDefault( "RegionRendering", False )
        singleRegionJob = self.IsTileJob()
        singleRegionFrame = str(self.GetStartFrame())
        singleRegionIndex = self.GetCurrentTaskId()
        
        simJob = self.GetBooleanPluginInfoEntryWithDefault( "SimJob", False )
        
        wedgeNum = -1
        try:
            wedgeNum = self.GetIntegerPluginInfoEntryWithDefault("WedgeNum", "-1")
        except:
            pass
        
        scene = scene.replace("\\","/")
        outputFilename = outputFilename.replace("\\", "/")
        ifdFilename = ifdFilename.replace("\\", "/")

        if SystemUtils.IsRunningOnWindows():
            if scene.startswith( "/" ) and scene[0:2] != "//":
                scene = "/" + scene
            if outputFilename.startswith( "/" ) and outputFilename[0:2] != "//":
                outputFilename = "/" + outputFilename
            if ifdFilename.startswith( "/" ) and ifdFilename[0:2] != "//":
                ifdFilename = "/" + ifdFilename
        else:
            if scene.startswith( "/" ) and scene[0:2] == "//":
                scene = scene[1:len(scene)]
            if outputFilename.startswith( "/" ) and outputFilename[0:2] == "//":
                outputFilename = outputFilename[1:len(outputFilename)]
            if ifdFilename.startswith( "/" ) and ifdFilename[0:2] == "//":
                ifdFilename = ifdFilename[1:len(ifdFilename)]
        
        # Construct the command line options and return them.
        hrender = Path.Combine( self.GetPluginDirectory(),"hrender_dl.py" )
        arguments = "\"" + hrender + "\""
        
        if simJob:
            machineNameOrIpAddress = ""
            trackerPort = self.GetIntegerConfigEntry( "Houdini_SimTracker_Tracker_Port" )
            if self.GetBooleanPluginInfoEntryWithDefault( "SimRequiresTracking", True ):
                self.LogInfo( "Sim Job: Checking which machine is running the tracking process" )
                
                # Need to figure out which slave is rendering the first task for this job.
                currentJob = self.GetJob()
                tasks = RepositoryUtils.GetJobTasks( currentJob, True )
                
                if tasks.GetTask(0).TaskStatus != "Rendering":
                    self.FailRender( "Sim Job: Cannot determine which machine is running the tracking process because the first task for this job is not in the rendering state" )
                
                trackerMachineSlave = tasks.GetTask(0).TaskSlaveName
                if trackerMachineSlave == "":
                    self.FailRender( "Sim Job: Cannot determine which machine is running the tracking process because the first task for this job is not being rendered by another slave" )
                
                slaveInfo = RepositoryUtils.GetSlaveInfo( trackerMachineSlave, True )
                self.LogInfo( "Sim Job: Slave \"" + slaveInfo.SlaveName + "\" is running the tracking proccess" ) 
                
                
                if not self.GetConfigEntry( "Houdini_SimTracker_Use_IP_Address" ):
                    machineNameOrIpAddress = SlaveUtils.GetMachineNames([slaveInfo])[0]
                    self.LogInfo( "Sim Job: Connecting to slave machine using host name \"" + machineNameOrIpAddress + "\"" )
                else:
                    machineNameOrIpAddress = SlaveUtils.GetMachineIPAddresses([slaveInfo])[0]
                    self.LogInfo( "Sim Job: Connecting to slave machine using IP address \"" + machineNameOrIpAddress + "\"" )
                
            arguments += " -s " + str( singleRegionFrame ) + " \"" + machineNameOrIpAddress + "\" " + str(trackerPort)
        elif regionRendering and singleRegionJob:
            arguments += " -f " + str( singleRegionFrame ) + " " + str( singleRegionFrame ) + " 1"
        else:
            arguments += " -f " + str(self.GetStartFrame()) + " " + str(self.GetEndFrame()) + " 1"
        
        width = self.GetIntegerPluginInfoEntryWithDefault( "Width", 0 )
        height = self.GetIntegerPluginInfoEntryWithDefault( "Height", 0 )
        if( width > 0 and height > 0 ):
            arguments += " -r " + str(width) + " " + str(height)
        
        if( len(outputFilename) > 0 ):
            arguments += " -o \"" + outputFilename + "\""
        if( len(ifdFilename) > 0 ):
            arguments += " -i \"" + ifdFilename + "\""
        
        if self.GetBooleanPluginInfoEntryWithDefault( "IgnoreInputs", False ):
            arguments += " -g"
        
        arguments += " -d " + self.GetPluginInfoEntry( "OutputDriver" )
        if regionRendering:
            xStart = 0
            xEnd = 0
            yStart = 0
            yEnd = 0
            currTile = 0
            if singleRegionJob:
                currTile = singleRegionIndex
                xStart = self.GetFloatPluginInfoEntryWithDefault("RegionLeft"+str(singleRegionIndex),0)
                xEnd = self.GetFloatPluginInfoEntryWithDefault("RegionRight"+str(singleRegionIndex),0)
                yStart = self.GetFloatPluginInfoEntryWithDefault("RegionBottom"+str(singleRegionIndex),0)
                yEnd = self.GetFloatPluginInfoEntryWithDefault("RegionTop"+str(singleRegionIndex),0)
            else:
                currTile = self.GetIntegerPluginInfoEntryWithDefault( "CurrentTile", 1 )
                xStart = self.GetFloatPluginInfoEntryWithDefault( "RegionLeft", 0 )
                xEnd = self.GetFloatPluginInfoEntryWithDefault( "RegionRight", 0 )
                yStart = self.GetFloatPluginInfoEntryWithDefault( "RegionBottom", 0 )
                yEnd = self.GetFloatPluginInfoEntryWithDefault( "RegionTop", 0 )
                
            arguments += " -t %s %s %s %s %s" % ( currTile, xStart, xEnd, yStart, yEnd )
        
        if wedgeNum > -1:
            arguments += " -wedgenum " + str(wedgeNum)
        
        gpuList = self.GetGpuOverrides()
        if len( gpuList ) > 0:
            
            gpus = ",".join( gpuList )
            arguments += " -gpu " + gpus
            
            if self.GetBooleanPluginInfoEntryWithDefault( "OpenCLUseGPU", 1 ):
                self.SetProcessEnvironmentVariable( "HOUDINI_OCL_DEVICETYPE", "GPU" )
                self.SetProcessEnvironmentVariable( "HOUDINI_OCL_VENDOR", "" )
                self.SetProcessEnvironmentVariable( "HOUDINI_OCL_DEVICENUMBER", gpuList[ self.GetThreadNumber() % len( gpuList ) ] )
            
        arguments += " \"" + scene + "\""
        
        return arguments
    
    def GetGpuOverrides( self ):
        resultGPUs = []
        
        # If the number of gpus per task is set, then need to calculate the gpus to use.
        gpusPerTask = self.GetIntegerPluginInfoEntryWithDefault( "GPUsPerTask", 0 )
        gpusSelectDevices = self.GetPluginInfoEntryWithDefault( "GPUsSelectDevices", "" )

        if self.OverrideGpuAffinity():
            overrideGPUs = self.GpuAffinity()
            if gpusPerTask == 0 and gpusSelectDevices != "":
                gpus = gpusSelectDevices.split( "," )
                notFoundGPUs = []
                for gpu in gpus:
                    if int( gpu ) in overrideGPUs:
                        resultGPUs.append( gpu )
                    else:
                        notFoundGPUs.append( gpu )
                
                if len( notFoundGPUs ) > 0:
                    self.LogWarning( "The Slave is overriding its GPU affinity and the following GPUs do not match the Slaves affinity so they will not be used: " + ",".join( notFoundGPUs ) )
                if len( resultGPUs ) == 0:
                    self.FailRender( "The Slave does not have affinity for any of the GPUs specified in the job." )
            elif gpusPerTask > 0:
                if gpusPerTask > len( overrideGPUs ):
                    self.LogWarning( "The Slave is overriding its GPU affinity and the Slave only has affinity for " + str( len( overrideGPUs ) ) + " gpus of the " + str( gpusPerTask ) + " requested." )
                    resultGPUs =  [ str( gpu ) for gpu in overrideGPUs ]
                else:
                    resultGPUs = [ str( gpu ) for gpu in overrideGPUs if gpu < gpusPerTask ]
            else:
                resultGPUs = [ str( gpu ) for gpu in overrideGPUs ]
        elif gpusPerTask == 0 and gpusSelectDevices != "":
            resultGPUs = gpusSelectDevices.split( "," )

        elif gpusPerTask > 0:
            gpuList = []
            for i in range( ( self.GetThreadNumber() * gpusPerTask ), ( self.GetThreadNumber() * gpusPerTask ) + gpusPerTask ):
                gpuList.append( str( i ) )
            resultGPUs = gpuList
        
        resultGPUs = list( resultGPUs )
        
        return resultGPUs
    
    def PreRenderTasks(self):
        # Use Escape License if requested
        slave = self.GetSlaveName().lower()
        ELicSlaves = self.GetConfigEntryWithDefault( "ELicSlaves", "" ).lower().split( ',' )
        if slave in ELicSlaves:
            self.LogInfo( "This Slave will use a Houdini Escape license to render" )
            self.SetProcessEnvironmentVariable("HOUDINI_SCRIPT_LICENSE", "hescape")
            
        if self.GetBooleanConfigEntryWithDefault( "EnablePathMapping", True ):
            mappings = RepositoryUtils.GetPathMappings( )
            if len(mappings) >0:
                houdiniPathmap = ""
                if Environment.GetEnvironmentVariable( "HOUDINI_PATHMAP" ) != None:
                    houdiniPathmap = Environment.GetEnvironmentVariable( "HOUDINI_PATHMAP" )
                            
                if houdiniPathmap.endswith( "}" ):
                    houdiniPathmap = houdiniPathmap[:-1]
                
                for map in mappings:
                    if houdiniPathmap != "":
                        houdiniPathmap += ", "
                        
                    originalPath = map[0].replace("\\","/")
                    newPath = map[1].replace("\\","/")
                    if originalPath != "" and newPath != "":
                        if SystemUtils.IsRunningOnWindows():
                            if newPath.startswith( "/" ) and newPath[0:2] != "//":
                                newPath = "/" + newPath
                        else:
                            if newPath.startswith( "/" ) and newPath[0:2] == "//":
                                newPath = newPath[1:len(newPath)]
                            
                        houdiniPathmap += "\"" + originalPath + "\":\"" + newPath + "\""
                
                if not houdiniPathmap.startswith("{"):
                    houdiniPathmap = "{"+houdiniPathmap
                if not houdiniPathmap.endswith("}"):
                    houdiniPathmap = houdiniPathmap+"}"
                
                self.LogInfo("Set HOUDINI_PATHMAP to " + houdiniPathmap )
                self.SetProcessEnvironmentVariable( 'HOUDINI_PATHMAP', houdiniPathmap )
        
        if self.GetBooleanPluginInfoEntryWithDefault( "SimJob", False ) and self.GetBooleanPluginInfoEntryWithDefault( "SimRequiresTracking", True ) and self.GetCurrentTaskId() == "0":
            self.LogInfo( "Sim Job: Starting Sim Tracker process because this is the first task for this sim job" )
            
            if SystemUtils.IsRunningOnWindows():
                pythonExe = "dpython.exe"
            else:
                pythonExe = "dpython"
            
            pythonPath = Path.Combine( ClientUtils.GetBinDirectory(), pythonExe )
        
            version = self.GetPluginInfoEntryWithDefault( "Version", "16.0" ).replace( ".", "_" )
            simTrackerList = self.GetConfigEntry( "Houdini" + version + "_SimTracker" )
            simTracker = FileUtils.SearchFileList( simTrackerList )
            if simTracker == "":
                self.FailRender( "Sim Job: Houdini " + version + " sim tracker file was not found in the semicolon separated list \"" + simTrackerList + "\". The path to the sim tracker file can be configured from the Plugin Configuration in the Deadline Monitor." )
            
            trackerPort = self.GetIntegerConfigEntry( "Houdini_SimTracker_Tracker_Port" )
            webServicePort = self.GetIntegerConfigEntry( "Houdini_SimTracker_Web_Service_Port" )
            
            # Check if either of the ports are already in use.
            trackerPortInUse = False
            webServicePortInUse = False
            
            s = None
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('', trackerPort))
                s.close()
                s = None
            except:
                s.close()
                s = None
                self.LogWarning( traceback.format_exc() )
                trackerPortInUse = True
                
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('', webServicePort))
                s.close()
                s = None
            except:
                s.close()
                s = None
                self.LogWarning( traceback.format_exc() )
                webServicePortInUse = True
                
            if trackerPortInUse and webServicePortInUse:
                self.FailRender("Unable to start the Sim Tracker process because tracker port {0} and web service port {1} are in use.".format(trackerPort,webServicePort))
            elif trackerPortInUse:
                self.FailRender("Unable to start the Sim Tracker process because tracker port {0} is in use.".format(trackerPort))
            elif webServicePortInUse:
                self.FailRender("Unable to start the Sim Tracker process because web service port {0} is in use.".format(webServicePort))
            
            arguments = "\"" + simTracker + "\" " + str(trackerPort) + " " + str(webServicePort)
            self.LogInfo("Sim Job: Starting the Sim Tracker process")
            self.StartMonitoredProgram( "SimTracker",  pythonPath, arguments, Path.GetDirectoryName( simTracker )  ) # string name, string executable, string arguments, string startupDirectory
            
        self.LogInfo("Starting Houdini Job")
        self.SetProgress(0)
        
    def PostRenderTasks(self):
        if self.GetBooleanPluginInfoEntryWithDefault( "SimJob", False ) and self.GetBooleanPluginInfoEntryWithDefault( "SimRequiresTracking", True ) and self.GetCurrentTaskId() == "0":
            self.LogInfo("Sim Job: Waiting for all other tasks for this job to complete before stopping theSim Tracker process")
            
            incompleteTasks = []
            
            jobComplete = False
            while not jobComplete:
                if self.IsCanceled():
                    self.FailRender( "Task canceled" )
                
                SystemUtils.Sleep( 5000 )
                
                currentJob = self.GetJob()
                tasks = RepositoryUtils.GetJobTasks( currentJob, True )
                
                jobComplete = True
                for task in tasks:
                    if task.TaskID > 0:
                        if task.TaskStatus != "Completed":
                            taskIdStr = str(task.TaskID)
                            
                            # Don't want to log more than once for any incomplete task.
                            if taskIdStr not in incompleteTasks:
                                incompleteTasks.append( taskIdStr )
                                self.LogInfo("Sim Job, still waiting for task: "+str(task.TaskID))
                            
                            jobComplete = False
                            break
            
            self.LogInfo("Sim Job: Stopping the Sim Tracker process")
            self.ShutdownMonitoredProgram( "SimTracker" )
    
        self.LogInfo("Finished Houdini Job")
        
    def HandleStdoutRenderer(self):
        self.FailRender(self.GetRegexMatch(1))
    
    def HandleStdoutError(self):
        self.FailRender(self.GetRegexMatch(1))

    def HandleStdoutLicense(self):
        self.FailRender(self.GetRegexMatch(1))
        
    def HandleStdoutUnknown(self):
        self.FailRender( "Bad command line: " + self.RenderArgument() + "\nHoudini Error: " + self.GetRegexMatch(1) )
    
    def HandleStdoutFrameProgress(self):
        if self.ropType == "ifd" or self.ropType == "rop_ifd":
            frameCount = self.GetEndFrame() - self.GetStartFrame() + 1
            if frameCount != 0:
                completedFrameProgress = float(self.completedFrames) * 100.0
                currentFrameProgress = float(self.GetRegexMatch(1))
                overallProgress = (completedFrameProgress + currentFrameProgress) / float(frameCount)
                self.SetProgress(overallProgress)
                self.SetStatusMessage( "Progress: " + str(overallProgress) + " %" )
                
        elif self.ropType == "geometry" or self.ropType == "rop_geometry" or self.ropType == "arnold":
            overallProgress = float(self.GetRegexMatch(1))
            self.SetProgress(overallProgress)
            self.SetStatusMessage( "Progress: " + str(overallProgress) + " %" )
        
    def HandleStdoutFrameComplete(self):
        if self.ropType == "ifd" or self.ropType == "rop_ifd":
            self.completedFrames = self.completedFrames + 1
        
    def HandleStdoutDoneRender(self):
        self.SetStatusMessage("Finished Render")
        self.SetProgress(100)
        
    def SetRopType(self):
        self.ropType = self.GetRegexMatch(1)
           
