# This is a temporary solution for notifying the AWS Portal File Transfer system about the start and end of a job.
# It is overwriting the callbacks that are defined in the plugin to do this and then calls the old callback.

import os
import subprocess
import sys
import types
import traceback

from Deadline.Scripting import *
from FranticX.Diagnostics import *

from Deadline.Plugins import *

def getFileTransferControllerPath( plugin ):
    if sys.platform == 'linux' or sys.platform == 'linux2':
        return '/opt/Thinkbox/S3BackedCache/bin/task.py'
    elif sys.platform == 'win32':
        return 'C:/Program Files/Thinkbox/S3BackedCache/bin/task.py'
    elif sys.platform == 'darwin':
        pass

    plugin.LogInfo( 'No File Transfer controller is available for this platform ({}).'.format(sys.platform) )
    return None

def isFileTransferInstalled( plugin ):
    plugin.LogInfo( 'Looking for AWS Portal File Transfer...' )

    controller_path = getFileTransferControllerPath( plugin )

    installed = False

    if controller_path is not None:
        plugin.LogInfo( 'Looking for File Transfer controller in {}...'.format( controller_path ) )
        installed = os.path.exists( controller_path )

    if installed:
        plugin.LogInfo( 'Found AWS Portal File Transfer.' )
    else:
        plugin.LogInfo( 'Could not find AWS Portal File Transfer.' )

    return installed

def runFileTransferCommand( self, args ):
    self.LogInfo( 'Executing file transfer command: {}'.format( ' '.join( args ) ) )
    try:
        r = subprocess.check_output( args )
        self.LogInfo( 'Result: {}'.format( r ) )
    except subprocess.CalledProcessError as e:
        self.LogInfo( 'Error executing file transfer command (error code {})'.format( e.returncode ) )
        raise

def fileTransferStart( self ):
    self.LogInfo( 'AWS Portal File Transfer start...' )

    job = self.GetJob()

    controller_path = self.getFileTransferControllerPath()

    args = [
            'python', controller_path,
            'start', str( job.JobId ),
        ]

    if len( job.JobOutputFileNames ) > 0:
        args.append( '--upload_whitelist' )
        for outputFileName in job.JobOutputFileNames:
            args.append( str( outputFileName ) )
    else:
        self.LogWarning( 'No OutputFilename entries found in Job Info, so no output files will be downloaded.' )

    self.runFileTransferCommand( args )

    self.LogInfo( 'Done AWS Portal File Transfer start.' )

def fileTransferEnd( self ):
    self.LogInfo( 'AWS Portal File Transfer end...' )

    job = self.GetJob()

    controller_path = self.getFileTransferControllerPath()

    args = [
            'python', controller_path,
            'end', str( job.JobId ),
        ]

    self.runFileTransferCommand( args )

    self.LogInfo( 'Done AWS Portal File Transfer end.' )
    
def fileTransferPreRenderTasksCallback( self ):
    self.LogInfo( 'Notifying AWS Portal File Transfer about task start.' )
    self.fileTransferStart()

    # There is always a PreRenderTasks defined.  We must determine if it is a callback that has been set or the built in C# code that runs the callback.
    # TODO: this assumes that the old callback had this exact name.  Is there some way we can get the old callback programmatically instead?
    if 'DeadlineRepository.Plugins' in str( self.PreRenderTasks ):
        self.PreRenderTasks()

def fileTransferPostRenderTasksCallback( self ):
    try:
        # There is always a PostRenderTasks defined.  We must determine if it is a callback that has been set or the built in C# code that runs the callback.
        # TODO: this assumes that the old callback had this exact name.  Is there some way we can get the old callback programmatically instead?
        if 'DeadlineRepository.Plugins' in str( self.PostRenderTasks ):
            self.PostRenderTasks()
    finally:
        self.LogInfo( 'Notifying AWS Portal File Transfer about task end.' )
        self.fileTransferEnd()

def fileTransferStartJobCallback( self ):
    self.LogInfo( 'Notifying AWS Portal File Transfer about job start.' )
    self.fileTransferStart()

    # There is always a StartJob defined.  We must determine if it is a callback that has been set or the built in C# code that runs the callback.
    # TODO: this assumes that the old callback had this exact name.  Is there some way we can get the old callback programmatically instead?
    if 'DeadlineRepository.Plugins' in str( self.StartJob ):
        self.StartJob()

def fileTransferEndJobCallback( self ):
    try:
        # There is always a EndJob defined.  We must determine if it is a callback that has been set or the built in C# code that runs the callback.
        # TODO: this assumes that the old callback had this exact name.  Is there some way we can get the old callback programmatically instead?
        if 'DeadlineRepository.Plugins' in str( self.EndJob ):
            self.EndJob()
    finally:
        self.LogInfo( 'Notifying AWS Portal File Transfer about job end.' )
        self.fileTransferEnd()

def fileTransferRenderTasksCallback( self ):
    self.LogInfo( 'Notifying AWS Portal File Transfer pre-task.' )
    self.fileTransferStart()

    try:
        # There is always a RenderTasks defined.  We must determine if it is a callback that has been set or the built in C# code that runs the callback.
        # TODO: this assumes that the old callback had this exact name.  Is there some way we can get the old callback programmatically instead?
        if 'DeadlineRepository.Plugins' in str( self.RenderTasks ):
            self.RenderTasks()
    finally:
        self.LogInfo( 'Notifying AWS Portal File Transfer post-task.' )
        self.fileTransferEnd()


def __main__( deadlinePlugin ):
    if isFileTransferInstalled( deadlinePlugin ):
        deadlinePlugin.LogInfo( 'AWS Portal File Transfer is installed on the system.  Adding file sync callbacks.' )

        # Add new functions to the Deadline Plugin
        deadlinePlugin.getFileTransferControllerPath = types.MethodType( getFileTransferControllerPath, deadlinePlugin )
        deadlinePlugin.runFileTransferCommand = types.MethodType( runFileTransferCommand, deadlinePlugin )

        deadlinePlugin.fileTransferStart = types.MethodType( fileTransferStart, deadlinePlugin )
        deadlinePlugin.fileTransferEnd = types.MethodType( fileTransferEnd, deadlinePlugin )

        if deadlinePlugin.PluginType == 1: # Advanced
            deadlinePlugin.LogInfo( 'Adding callbacks for Advanced plugin.' )

            # Remove the callback from StartJobCallback if one already exists
            if deadlinePlugin.StartJobCallback is not None:
                del deadlinePlugin.StartJobCallback

            # Add a new callback to the plugin to so that File Transfer is notified when the job starts.
            deadlinePlugin.StartJobCallback += types.MethodType( fileTransferStartJobCallback, deadlinePlugin )

            # Remove the callback from EndJobCallback if one already exists
            if deadlinePlugin.EndJobCallback is not None:
                del deadlinePlugin.EndJobCallback

            # Add a new callback to the plugin to so that File Transfer is notified when the job ends.
            deadlinePlugin.EndJobCallback += types.MethodType( fileTransferEndJobCallback, deadlinePlugin )

            # Remove the callback from RenderTasksCallback if one already exists
            if deadlinePlugin.RenderTasksCallback is not None:
                del deadlinePlugin.RenderTasksCallback

            # Add a new callback to the plugin to so that File Transfer is notified for each task.
            deadlinePlugin.RenderTasksCallback += types.MethodType( fileTransferRenderTasksCallback, deadlinePlugin )

        else: # Simple
            deadlinePlugin.LogInfo( 'Adding callbacks for Simple plugin.' )

            # Remove the callback from PostRenderTasks if one already exists
            if deadlinePlugin.PreRenderTasksCallback is not None:
                del deadlinePlugin.PreRenderTasksCallback

            # Add a new callback to the plugin to so that File Transfer is notified when the job starts.
            deadlinePlugin.PreRenderTasksCallback += types.MethodType( fileTransferPreRenderTasksCallback, deadlinePlugin )

            # Remove the callback from PostRenderTasks if one already exists
            if deadlinePlugin.PostRenderTasksCallback is not None:
                del deadlinePlugin.PostRenderTasksCallback

            # Add a new callback to the plugin to so that File Transfer is notified when the job ends.
            deadlinePlugin.PostRenderTasksCallback += types.MethodType( fileTransferPostRenderTasksCallback, deadlinePlugin )
    else:
        deadlinePlugin.LogInfo( 'AWS Portal File Transfer is not installed on the system.' )
