import glob
import os
import signal
import socket
import struct
import subprocess
import sys 
import threading
import xmlrpclib
import inspect
import urllib2
import re
import copy

import hqrop
import hutil.file
import hutil.json
import rendertracker
import simtracker

# The RPC connection to the render tracker.
gRenderTrackerRPC = None

# This constant is needed since we cannot access the default tile infix
# if the user has not added the vm_tile_filename_suffix parameter to
# the mantra node
DEFAULT_UNEXAPANDED_TILE_INFIX = "_tile%02d_"

# The kwargs on the functions are to consume extra arguments caused by
# updates adding parameters

def makeIFDs(
    hip_file, project_name, output_driver, ifd_path, delete_ifds, 
    frames_per_job, cross_platform_ifd, min_hosts_per_job, max_hosts_per_job, dirs_to_create, 
    load_hip=True, set_tile_callback=True, use_render_tracker=True, 
    render_frame_order=True, enable_checkpoints=True, **kwargs):
    """Generate IFDs from a hip file and then submit render jobs to HQueue.

    This function is called from hq_make_ifds.py.
    """
    global gRenderTrackerRPC

    import hou
    
    if use_render_tracker:
        gRenderTrackerRPC = getRenderTrackerRPC()
    else:
        gRenderTrackerRPC = None

    # Load the hip file and get the rop node ready.
    if load_hip:
        expanded_hip_file = hou.expandString(hip_file)
        rop, tile_callback_parm = _loadHipFileAndGetRopAndTileCallbackParm(
            expanded_hip_file, output_driver, project_name, enable_checkpoints, set_tile_callback)
    else:
        rop = hou.node(output_driver)
        if rop is not None and gRenderTrackerRPC is not None:
            gRenderTrackerRPC.setProjectError(project_name, 
                "Output driver '%s' does not exist." % output_driver)
        if set_tile_callback:
            tile_callback_parm = _getTileCallbackParm(rop)

    commandline_arg = rop.parm('soho_pipecmd').eval()

    # Extract the target frames from the output driver.
    frames = _getTargetFramesFromRop(rop)
    if render_frame_order == "subdivision_order":
        frames = createBinaryPartitionOrder(frames)
    if frames_per_job < 0:
        frames_per_job = len(frames)

    # Log that we've started to render this project.
    if gRenderTrackerRPC is not None:
        gRenderTrackerRPC.startedRenderProject(
            project_name, frames, True, os.environ["JOBID"])

    _createDirectories(dirs_to_create) 

    ifd_dir = os.path.dirname(hou.expandString(ifd_path))
    if not os.path.exists(ifd_dir):
        try:
            os.makedirs(ifd_dir)
        except OSError, e:
            error_message = (
                "ERROR: Cannot create output ifd directory: %s\n%s" % (
                    ifd_dir, e))
            if gRenderTrackerRPC is not None:
                gRenderTrackerRPC.setProjectError(project_name, error_message)
            print error_message
            sys.exit(1)
    
    # Generate the base name of the IFD jobs
    hip_name = os.path.basename(hip_file)
    ifd_name = os.path.basename(ifd_path)
    base_name = "Render -> HIP: %s IFD: %s " % (hip_name, ifd_name)

    # Generate the IFD for each frame and submit jobs to render those IFDs.
    frames_to_render, ifds, image_paths = [], [], []
    print "PROGRESS: 0/%d" % len(frames)
    for i, frame in enumerate(frames):
        # Turn on IFD generation and set IFD parameters in ROP node.
        # The expanded IFD path is returned.
        ifd_path_for_frame = _setIFDParmsAndGetExpandedPath(ifd_path, frame, rop)

        # Set the frame range and the tile callback parameter.
        _setParmInROPChain(rop, "f", (frame, frame, 1))

        if set_tile_callback:
            _setTileCallbackParm(tile_callback_parm, 0, frame, 1, 
                project_name, use_render_tracker)

        # Generate the ifd, logging to the render tracker.
        if gRenderTrackerRPC is not None:
            gRenderTrackerRPC.startedGeneratingFrameIFD(project_name, frame)
        _invokeRopAndCatchErrors(rop, project_name, frame, False)
        if gRenderTrackerRPC is not None:
            gRenderTrackerRPC.endedGeneratingFrameIFD(project_name, frame)

        # Now that this ifd has been generated, submit a job to render it.
        frames_to_render.append(frame)
        ifds.append(ifd_path_for_frame)
        image_paths.append(hqrop.getOutputParm(rop).evalAtFrame(frame))
        
        if len(frames_to_render) >= frames_per_job:
            _submitRenderFromIFDsJob(base_name, ifd_path, frames_to_render, 
                ifds, image_paths, commandline_arg,  min_hosts_per_job, 
                max_hosts_per_job, project_name, delete_ifds, 
                use_render_tracker, cross_platform_ifd)
            frames_to_render = []
            ifds = []
            image_paths = []

        print "PROGRESS: %d/%d" % (i + 1, len(frames))

    if len(frames_to_render) > 0:
        _submitRenderFromIFDsJob(base_name, ifd_path, frames_to_render, 
            ifds, image_paths, commandline_arg, min_hosts_per_job, 
            max_hosts_per_job, project_name, delete_ifds, use_render_tracker, cross_platform_ifd)
        frames_to_render = []
        ifds = []


def prepareIFDRender(
    project_name, ifd_path, start_frame, end_frame, frame_skip, 
    frames_per_job, cross_platform_ifd, min_hosts_per_job, max_hosts_per_job, dirs_to_create, 
    load_hip=True, set_tile_callback=True, use_render_tracker=True, 
    render_frame_order=True, **kwargs):
    
    global gRenderTrackerRPC

    start_frame = int(start_frame)
    end_frame = int(end_frame)
    frame_skip = int(frame_skip)

    frames = range(start_frame, end_frame + 1, frame_skip)
    if render_frame_order == "subdivision_order":
        frames = createBinaryPartitionOrder(frames)
    if frames_per_job < 0:
        frames_per_job = len(frames)
    
    # Log that we've started to render this project.
    if gRenderTrackerRPC is not None:
        gRenderTrackerRPC.startedRenderProject(
            project_name, frames, True, os.environ["JOBID"])
   
    _createDirectories(dirs_to_create, False)

    # Generate the render jobs basename
    ifd_name = os.path.basename(ifd_path)
    base_name = "Render -> IFD: %s " % (ifd_name)


    frame_render_groupings = _chunk(frames, frames_per_job)

    print "PROGRESS: 0/%d" % len(frames)
    total_progress = 0

    for group in frame_render_groupings:
        ifd_frame_paths = [
            _substituteWithHQROOT(_expandFrameVarsInString(ifd_path, frame))
            for frame in group]
        
        for ifd in ifd_frame_paths:
            if not os.path.exists(os.path.expandvars(ifd)):
                error_message = ("ERROR: No such file: %s" % (ifd))
                if gRenderTrackerRPC is not None:
                    gRenderTrackerRPC.setProjectError(project_name, 
                                                      error_message)
                print error_message
                sys.exit(1)

        total_progress += len(group)
        print "PROGRESS: %d/%d" % (total_progress, len(frames))

        _submitRenderFromIFDsJob(
            base_name, ifd_path, group, ifd_frame_paths, None, "mantra", 
            min_hosts_per_job, max_hosts_per_job, project_name, 
            False, use_render_tracker, cross_platform_ifd)


# This was an answer to the question from:
# http://stackoverflow.com/questions/434287/what-is-the-most-pythonic-way-to-iterate-over-a-list-in-chunks
def _chunk(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))


def _addMantraSpecificArguments(cmd_args):
    """Add Mantra-specific arguments to the given command and return
    the command with the added arguments."""
    # TODO: We should check if any of the options already exist
    #       before appending them.

    # Add -j option if the job has a cpu restriction.
    job_info = _getJobCpuAndTagInfo()
    if not "single" in job_info["tags"]:
        cmd_args += " -j" + str(job_info["cpus"])

    # Add -V option to make the render verbose.
    if " -V" not in cmd_args:
         cmd_args += " -V1";

    # Add -H option if the job has a list of client machines
    # that should run the job.
    str_clients = os.environ["HQHOSTS"]
    if len(str_clients.split(",")) > 1:
        cmd_args += " -H " + str_clients

    return cmd_args


def _submitRenderFromIFDsJob(
    base_name, ifd_path, frames, ifds, image_paths, commandline_args, 
    min_hosts_per_job, max_hosts_per_job, project_name, delete_ifds, 
    use_render_tracker, cross_platform_ifd):
    """Submit a new job to HQueue to render an IFD using Mantra.

    Note that job invokes hq_mantra.py with a standard Python interpreter.
    """
    frames_str = " ".join(str(f) for f in frames)

    name = _generateRenderJobName(base_name, frames, ifd_path)

    hq_cmds = _getHQueueCommands()
    commands = hqrop.getJobCommands(hq_cmds, "mantraCommands")
    job = {
        "name": name,
        "environment": {
            "HQCOMMANDS" : hutil.json.utf8Dumps(hq_cmds),
            "HQPARMS": hutil.json.utf8Dumps({
                "ifds": ifds,
                "frames": frames,
                "image_paths": image_paths,
                "delete_ifds": delete_ifds,
                "project_name": project_name,
                "commandline_args": commandline_args,
                "use_render_tracker": use_render_tracker,
            }),
        },
        "minHosts": str(min_hosts_per_job),
        "maxHosts": str(max_hosts_per_job),
        "command": commands
    }

    # Restrict the render job to machines that have the same
    # operating system as the machine generating the IFDs.
    # We have to place this restriction because IFDs embed hard-coded
    # file paths which differ between OS's.
    hq_client_arch = os.environ["HQCLIENTARCH"]
    operating_system = hq_client_arch.split("-")[0]
    if cross_platform_ifd:
        job["conditions"] = []
    else :    
        job["conditions"] = [ 
            { "type" : "client", "name" : "os", 
            "op" : "==", "value" : operating_system } ]

    # Set the number of cpus that the render job will have.
    job_info = _getJobCpuAndTagInfo()
    if "single" in job_info["tags"]:
        job["tags"] = ["single"]
    else:
        job["cpus"] = job_info["cpus"]

    hq_server = _newHQServerConnection()
    parent_job_id = _getParentJobID()

    if parent_job_id is not None:
        # Make the new job a child of this job's parent.
        job["parentIds"] = [parent_job_id,]

        # Also add any conditions coming from the parent job.
        parent_job = hq_server.getinfo(parent_job_id)
        job["conditions"].extend(parent_job["conditions"])

    _submitHQJobs(hq_server, job)


def _loadHipFileAndGetRopAndTileCallbackParm(
        hip_file, rop_path, project_name, enable_checkpoints, get_tile_callback=True):
    import hou

    # Load the hip file and get the rop, logging any errors to the render
    # tracker as project errors.
    def _logProjectError(error_message):
        if gRenderTrackerRPC is not None:
            gRenderTrackerRPC.setProjectError(project_name, error_message)
    rop = _loadHipFileAndGetNode(hip_file, rop_path, _logProjectError)

    # Enable/disable Mantra checkpoint files.
    # This must be done before we retrieve the tile callback parm because
    # enabling checkpointing could add spare parameters to the ROP node which
    # changes the parameter interface. 
    if rop.type().name() == "ifd":
        _enableMantraCheckpoints(rop, enable_checkpoints)

    # Add a tile callback spare parm so mantra can notify us of the render's
    # status.
    if get_tile_callback:
        tile_callback_parm = _getTileCallbackParm(rop)
    else:
        tile_callback_parm = None

    return rop, tile_callback_parm


def _loadHipFileAndGetNode(hip_file, node_path, error_logger=None):
    import hou

    _loadHipFile(hip_file, error_logger)

    # Make sure the node exists.
    node = hou.node(node_path)
    if node is None:
        _failWithProjectError("ERROR: Cannot find node: %s" % node_path,
                              error_logger)

    return node


def _loadHipFile(hip_file, error_logger = None):
    import hou

    # We need to switch our backslashes to forward slashes for UNC paths to
    # work correctly
    hip_file = hip_file.replace("\\", "/")

    if not os.path.exists(hip_file):
        _failWithProjectError("ERROR: Cannot find file %s" % hip_file,
                              error_logger)

    # We want to allow the JOB environment variable to override the value
    # saved in the hip file, before we load it (so that we can load otl files
    # based off $JOB).
    if hasattr(hou, "allowEnvironmentToOverwriteVariable"):
        if "JOB" in os.environ:
            hou.allowEnvironmentToOverwriteVariable("JOB", True)

    # Note that we ignore all load warnings.
    try:
        hou.hipFile.load(hip_file)
    except hou.LoadWarning:
        pass


def _failWithProjectError(error_message, error_logger):
    if error_logger is not None:
        error_logger(error_message)
        print error_message
        sys.exit(1)



def _getTileCallbackParm(rop):
    """Return the tile callback parameter for the given Mantra ROP.

    If the parameter does not exist, then create it.
    Return None if `rop` is not a Mantra ROP.
    """
    import hou
    tile_callback_parm = None
    if rop.type().name() in ("ifd", "baketexture"):
        tile_callback_parm = rop.parm("vm_tilecallback")
        if tile_callback_parm is None:
            tile_callback_parm_tuple = rop.addSpareParmTuple(
                hou.StringParmTemplate("vm_tilecallback", "tile callback", 1))
            tile_callback_parm = tile_callback_parm_tuple[0]
    return tile_callback_parm

def _createDirectories(dirs_to_create, expand_vars_with_hou=True):
    """Attempt to create given list of directories.  

    Raise an exception if the user doesn't have proper permissions to create
    the directory.
    """

    for dir_path in dirs_to_create:
        if expand_vars_with_hou:
            import hou
            dir_path = hou.expandString(dir_path)
        else:
            dir_path = os.path.expandvars(dir_path)

        if os.path.exists(dir_path):
            continue

        try:
            # Attempt to create the directory.
            os.makedirs(dir_path)
        except OSError, e:
            err_msg = e.strerror.upper().strip()
            if err_msg == "FILE EXISTS":
                # Directory already exists.  That's fine.
                pass
            elif err_msg == "PERMISSION DENIED":
                # Print a nicer looking message.
                print "ERROR: Cannot create " + dir_path \
                    + ".  Permission denied."
                sys.exit(1)
            else:
                # Raise all other exceptions.
                raise

def _setTileCallbackParm(
        parm, frame_index, frame_number, num_frames, project_name,
        use_render_tracker):
    try:
        no_tile_callback = bool(int(os.environ["NO_TILE_CALLBACK"]))
    except:
        no_tile_callback = False
    if no_tile_callback:
        return

    parm.set("%s/hq_mantracallback.py %d %d %d \"%s\" %d" % (
        (hqrop.hqScriptsDirectory(), frame_index, frame_number, num_frames,
        project_name, use_render_tracker)))

def _invokeRopAndCatchErrors(rop, project_name, frame, ignore_inputs):
    import hou

    try:
        _renderRop(rop, ignore_inputs=ignore_inputs)
    except hou.OperationFailed, e:
        # Log that the ifd generation failed and reraise the exception.
        if gRenderTrackerRPC is not None:
            gRenderTrackerRPC.setFrameError(project_name, frame, str(e))

        # Output ROP errors and fail.
        sys.stderr.write(str(e))
        sys.stderr.flush()
        sys.exit(1)

def _substituteWithHQROOT(file_path):
    """Replace the beginning of the given path with $HQROOT.
    
    if the path is not under HQ's shared network file system return the
    original path.  Return None if an error occurs.
    """
    # Get the HQ root.  It should have been set in the environment
    # by the server.
    hq_root = os.environ["HQROOT"]
    hq_root = os.path.normpath(hq_root)
    hq_root = hq_root.replace("\\", "/")

    # Normalize file path.
    # Stick with forward slashes instead of backward slashes.
    file_path = os.path.normpath(file_path)
    file_path = file_path.replace("\\", "/")

    # Compare the HQ root with the given file path.
    # Substitute the raw HQ root path with the HQROOT environment
    # variable.
    if file_path.startswith(hq_root):
        file_path = file_path[len(hq_root):]
        if not file_path.startswith("/"):
            file_path = "/" + file_path
        file_path = "$HQROOT" + file_path

    return file_path


def _getJobCpuAndTagInfo(job_id=None):
    """Return the cpu info and tag info for the currently running job."""
    job_info = _getJobInfo(job_id, ["cpus", "tags"])
    if not job_info.has_key("tags"):
        job_info["tags"] = []
    if not job_info.has_key("cpus"):
        job_info["cpus"] = 0
    return job_info


def _getJobInfo(job_id, attribs=None):
    if job_id is None:
        job_id = int(os.environ["JOBID"]) 
    hq_server = _newHQServerConnection()
    job_info = hq_server.getJob(job_id, attribs)
    if not job_info:
        return {}
    return job_info


def _getParentJobID(hq_server=None):
    if hq_server is None:
        hq_server = _newHQServerConnection()

    job_info = hq_server.getinfo(os.environ["JOBID"])
    if not job_info:
        return None

    parent_job_ids = job_info.get('parents', [])
    if len(parent_job_ids) == 0:
        return None

    return parent_job_ids[0]


def _submitHQJobs(hq_server, job_specs):
    """Submit a new job to the HQueue server.
    
    Return a sequence of job ids for the new job(s), or None if the submission
    failed.

    `job_specs` can either be a dictionary representing a single job
    specification or a tuple/list of dictionary objects representing
    multiple job specifications.
    """
    if type(job_specs) != list and type(job_specs) != tuple:
        job_specs = [job_specs,]

    # Make sure we apply the same conditions to the new jobs that
    # our current job is restricted to.
    job_id = os.environ['JOBID']
    job_info = hq_server.getinfo(job_id)
    for job in job_specs:
        _modifyJobForSubmittal(job, job_info)

    # Submit the jobs to HQueue.
    new_job_ids = hq_server.newjob(job_specs)
    if len(new_job_ids) == 0:
        job_names = [job["name"] for job in job_specs]
        print "Failed to submit jobs: %s" % job_names.join(", ")
        return None

    return new_job_ids

def _modifyJobForSubmittal(job, job_info):
    if not job.has_key("conditions"):
        job["conditions"] = job_info["conditions"]

    job["priority"] = job_info["priority"]
    hqrop.setEnvironmentVariablesInJobSpec(job)

    for child in job.get("children", []):
        _modifyJobForSubmittal(child, job)

def _getHQueueCommands():
    """Returns a dictionary of commands.
    
    These commands are used to execute the render and simulation scripts on
    the farm, and contain instructions on how to run hython, Mantra, and
    Python.
    """
    return hutil.json.utf8Loads(os.environ["HQCOMMANDS"])

def _newHQServerConnection():
    return xmlrpclib.ServerProxy(os.environ['HQSERVER'], allow_none=True)

def getRenderTrackerRPC():
    """Return a connection to the render tracker on the HQueue server machine.
    
    If the render tracker is not running, return a dummy render tracker that
    does nothing.  This approach is simpler than returning None, since code
    that wants to log events with the render tracker can simply call the
    logging methods, without checking if it's None.  You can differentiate
    between a real render tracker connection and a dummy one by the return
    value of isRunning.
    """
    class _DummyRenderTracker(object):
        def isRunning(self):
            return False

        def __getattr__(self, name):
            def dummy_func(*args, **kwargs):
                pass
            return dummy_func

    class _ConnectionFailureTolerantRenderTracker(object):
        """A rendertracker RPC connection that handles connection failures
        and then turns into a dummy render tracker.  We can get a connection
        failure if the HQserver (and thus the render tracker) is restarted
        while jobs are still running.
        """
        def __init__(self, real_render_tracker_rpc):
            # Fallback to the "dummy" render tracker if we can't connect to
            # the real one.  Note that you may pass in None for
            # real_render_tracker_rpc.
            self.real_render_tracker_rpc = real_render_tracker_rpc
            self.dummy_render_tracker_rpc = _DummyRenderTracker()

        def __getattr__(self, name):
            # If we couldn't connect to the real render tracker earlier, return
            # the attribute on the dummy one.
            if self.real_render_tracker_rpc is None:
                return getattr(self.dummy_render_tracker_rpc, name)

            # Return a function that calls the method on the real render
            # tracker.
            attr = getattr(self.real_render_tracker_rpc, name)
            def wrapper(*args, **kwargs):
                try:
                    return attr(*args, **kwargs)
                except urllib2.URLError:
                    # Handle a connection failure and fall back to the dummy
                    # version.
                    self.real_render_tracker_rpc = None
                    return (False if name == "isRunning" else None)
            return wrapper

    hq_server_machine = os.environ['HQSERVER'][7:].split(":")[0]
    return _ConnectionFailureTolerantRenderTracker(
        rendertracker.getConnection(hq_server_machine))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def submitMultipleRenderJobs(
    hip_file, project_name, output_driver, frames_per_job,
    min_hosts_per_job, max_hosts_per_job, dirs_to_create,  
    render_single_tile=False, use_render_tracker=True, 
    render_frame_order=True, enable_checkpoints=True, **kwargs):
    """Submit a number of HQueue jobs to render directly from a hip file.
    
    Each job will render a batch of `frames_per_job` using
    hq_render_from_hip.py.  This function is called by hq_submit_renders.py.
    """
    global gRenderTrackerRPC
    import hou

    if use_render_tracker:
        gRenderTrackerRPC = getRenderTrackerRPC()
    else:
        gRenderTrackerRPC = None

    # Load the .hip file and get the output driver.
    expanded_hip_file = hou.expandString(hip_file)
    def _logProjectError(error_message):
        if gRenderTrackerRPC is not None:
            gRenderTrackerRPC.setProjectError(project_name, error_message)
    rop = _loadHipFileAndGetNode(expanded_hip_file, output_driver, 
        _logProjectError)

    # Extract the target frames from the output driver.
    frames = _getTargetFramesFromRop(rop)
    if render_frame_order == "subdivision_order":
        frames = createBinaryPartitionOrder(frames)
    if frames_per_job < 0:
        frames_per_job = len(frames)

    # Log that we've started to render this project.
    if gRenderTrackerRPC is not None:
        gRenderTrackerRPC.startedRenderProject(
            project_name, frames, False, os.environ["JOBID"])

    hq_server = _newHQServerConnection()

    # Create several child job specs for rendering batches of frames.
    frame_job_range = range(0, len(frames), frames_per_job)
    i = 0
    print "PROGRESS: 0/%d" % len(frame_job_range)
    for f in frame_job_range:
        job_frames = frames[f:f + frames_per_job]
        job_specs = _createSpecsForRenderJob(hq_server, hip_file, 
            project_name, rop, job_frames, min_hosts_per_job,
            max_hosts_per_job, render_single_tile, enable_checkpoints, 
            dirs_to_create, use_render_tracker)
        _submitHQJobs(hq_server, job_specs)

        i = i + 1
        print "PROGRESS: %d/%d" % (i, len(frame_job_range))


def _createSpecsForRenderJob(
    hq_server, hip_file, project_name, rop, frames, 
    min_hosts_per_job, max_hosts_per_job, render_single_tile, enable_checkpoints,
    dirs_to_create, use_render_tracker):
    """Create HQueue specifications for the render job described 
    by the input arguments.

    A spec is created for each sub-task in the job.
    Task dependencies are set up as parent-child relationships.
    """
    job_specs = {}
    
    # Get commands for job specs.
    hq_cmds = _getHQueueCommands()
    commands = hqrop.getJobCommands(
        hq_cmds, "hythonCommands", "hq_render_from_hip.py")

    rops = [rop]
    index = 0

    while index < len(rops):
        cur_rop = rops[index]
        index = index + 1

        if job_specs.has_key(cur_rop.path()):
            continue

        # We need to keep track of our input nodes
        # because we will need to submit render jobs for them as well.
        inputs = cur_rop.inputs()

        # Handle Fetch ROPs.
        if cur_rop.type().name() == "fetch":
            cur_rop, fetched_inputs = _getFetchedROP(cur_rop, True)
            inputs = inputs + fetched_inputs
        
        child_stub_ids = []
        # Get the ROP's input nodes so that they are processed later.
        for input_rop in inputs:
            if input_rop is None:
                continue

            # Skip nodes that are not ROPs.
            if input_rop.parm("execute") is None \
                or input_rop.parm("renderdialog") is None:
                continue

            input_rop_path = input_rop.path()

            # If the input node is a Fetch ROP, then we need to link
            # the fetched ROP job with the current job.
            if input_rop.type().name() == "fetch":
                source_rop = _getFetchedROP(input_rop)
                input_rop_path = source_rop.path()

            rops.append(input_rop)
            child_stub_ids.append(input_rop_path)

        # Create a job spec for the current ROP.
        cur_spec = _createSpecForRop(commands, hq_cmds, hip_file, 
            project_name, cur_rop, frames, child_stub_ids, min_hosts_per_job, 
            max_hosts_per_job, render_single_tile, enable_checkpoints, dirs_to_create, 
            use_render_tracker)

        # The first ROP should be parented to this job's parent.
        if index == 1:
            parent_job_id = _getParentJobID(hq_server)
            if parent_job_id is not None:
                cur_spec["parentIds"] = [parent_job_id,]

        job_specs[cur_rop.path()] = cur_spec

    return job_specs.values()


def _createSpecForRop(
    commands, hq_cmds, hip_file, project_name, rop, frames, child_stub_ids, 
    min_hosts_per_job, max_hosts_per_job, render_single_tile, enable_checkpoints, 
    dirs_to_create, use_render_tracker):
    """Create an HQueue job specification for the output driver and frames."""
    if (rop.type().name() == "ifd" and rop.parm("vm_tile_render") is not None
            and rop.parm("vm_tile_render").evalAsInt() == 1
            and not render_single_tile):
        tile_jobs = _createSpecsForTileJobs(
            commands, hq_cmds, hip_file, project_name, rop, frames, 
            child_stub_ids, min_hosts_per_job, max_hosts_per_job,
            enable_checkpoints, dirs_to_create, use_render_tracker)
        return _createContainerJobForTiledRop(
            hq_cmds, hip_file, project_name, rop, frames, tile_jobs)
    else:
        return _createSpecForUntiledRop(
            commands, hq_cmds, hip_file, project_name, rop, frames, 
            child_stub_ids, min_hosts_per_job, max_hosts_per_job, 
            enable_checkpoints, dirs_to_create, use_render_tracker)

def _createContainerJobForTiledRop(hq_cmds, hip_file, project_name, rop, 
                                    frames, tile_jobs):
    name = _generateNameForHipRender(hip_file, rop, frames)

    commands = hqrop.getJobCommands(
        hq_cmds, "hythonCommands", "hq_stitch_tiles.py")
   
    hq_parms = {
        "hip_file": hip_file,
        "project_name": project_name,
        "output_driver": rop.path(),
        "frames": frames,
    }

    job_spec = {
        "name": name,
        "stubId": rop.path(),
        "command": commands,
        "environment": {
            "HQCOMMANDS": hutil.json.utf8Dumps(hq_cmds),
            "HQPARMS": hutil.json.utf8Dumps(hq_parms),
        },
        "children": tile_jobs,
    }

    return job_spec

def _createSpecsForTileJobs(
    commands, hq_cmds, hip_file, project_name, rop, frames, child_stub_ids, 
    min_hosts_per_job, max_hosts_per_job, enable_checkpoints, dirs_to_create,
    use_render_tracker):
    number_of_tiles = _getNumberOfTiles(rop)
    
    tile_job_specs = []

    for tile_number in xrange(number_of_tiles):
        job_spec = _createSpecForSingleTileJob(
            commands, hq_cmds, hip_file, project_name, rop, frames, 
            child_stub_ids, min_hosts_per_job, max_hosts_per_job, 
            enable_checkpoints, dirs_to_create, use_render_tracker, tile_number)
        tile_job_specs.append(job_spec)
    
    return tile_job_specs

def _getNumberOfTiles(rop):
    columns = rop.parm("vm_tile_count_x").evalAsInt()
    rows = rop.parm("vm_tile_count_y").evalAsInt()

    return columns * rows


def _createSpecForSingleTileJob(
    commands, hq_cmds, hip_file, project_name, rop, frames, child_stub_ids, 
    min_hosts_per_job, max_hosts_per_job, enable_checkpoints,
    dirs_to_create, use_render_tracker, tile_number):
    hip_name = os.path.basename(hip_file)

    base_name = "Render Tile -> HIP: %s ROP: %s" % (hip_name, rop.name())
    frame_word = _getFrameWord(frames)

    output_path = rop.parm("vm_picture").unexpandedString()
    padding = _determineFramePadding(output_path)

    frames_string = _frameListAsString(frames, padding)
    tile_string = _determineTileString(rop, tile_number)

    name = ("%s (%s: %s; %s)" % (base_name, frame_word, frames_string,
                                        tile_string))


    hq_parms = { 
        "hip_file" : hip_file,
        "project_name" : project_name,
        "output_driver" : rop.path(),
        "frames" : frames,
        "tile" : tile_number,
        "enable_checkpoints" : enable_checkpoints,
        "dirs_to_create" : dirs_to_create,
        "use_render_tracker" : use_render_tracker,
    }

    job_spec = {"name": name,
                "command": commands,
                "environment": {
                        "HQCOMMANDS": hutil.json.utf8Dumps(hq_cmds),
                        "HQPARMS": hutil.json.utf8Dumps(hq_parms),
                    },
                "minHosts": str(min_hosts_per_job),
                "maxHosts": str(max_hosts_per_job),
                }
    
    job_spec["childStubIds"] = child_stub_ids

    job_info = _getJobCpuAndTagInfo()
    if "single" in job_info["tags"]:
        job_spec["tags"] = ["single"]
    else:
        job_spec["cpus"] = job_info["cpus"]

    return job_spec

def _determineTileString(rop, tile):
    # We do not care about what frame we expand part of the string at as
    # we only want the number of digits used in the tile number expansion
    unexpanded_tile_infix = _getUnexpandedTileInfix(rop, 1)
    search_result = re.search("(?P<padding>%\d+d)", unexpanded_tile_infix)

    if search_result:
        padding = search_result.group("padding")
        return "".join(["Tile: ", padding]) % tile
    else:
        return "Tile: %d" % tile

def _createSpecForUntiledRop(
    commands, hq_cmds, hip_file, project_name, rop, frames, child_stub_ids, 
    min_hosts_per_job, max_hosts_per_job, enable_checkpoints, dirs_to_create, 
    use_render_tracker):
    """Create an HQueue job specification when not doing tiling.

    This also handles the case where the the user specified tiling but wants
    HQueue to render only the single, specified tile.
    """
    name = _generateNameForHipRender(hip_file, rop, frames)

    job_spec = {
        "name": name,
        "stubId": rop.path(),
        "environment": { 
            "HQCOMMANDS" : hutil.json.utf8Dumps(hq_cmds),
        },
    }

    if child_stub_ids:
        job_spec["childStubIds"] = child_stub_ids

    # Add commands to only ROP nodes that actually do real work.
    if rop.type().name() not in ("batch", "merge", "null"):
        job_spec["command"] = commands

    hq_parms = { 
        "hip_file" : hip_file,
        "project_name" : project_name,
        "output_driver" : rop.path(),
        "frames" : frames,
        "enable_checkpoints" : enable_checkpoints,
        "dirs_to_create" : dirs_to_create,
        "use_render_tracker" : use_render_tracker,
    }

    # Set the number of cpus that the job will use.
    job_info = _getJobCpuAndTagInfo()
    if "single" in job_info["tags"]:
        job_spec["tags"] = ["single"]
    else:
        job_spec["cpus"] = job_info["cpus"]

    # Add mantra specific options and parameters
    if rop.type().name() in ("ifd", "baketexture"):
        job_spec["minHosts"] = str(min_hosts_per_job)
        job_spec["maxHosts"] = str(max_hosts_per_job)

    job_spec["environment"]["HQPARMS"] = hutil.json.utf8Dumps(hq_parms)

    return job_spec

def _generateNameForHipRender(hip_file, rop, frames):
    hip_name = os.path.basename(hip_file)
    output_path = _getOutputPath(rop)
    base_name = "Render -> HIP: %s ROP: %s" % (hip_name, rop.name())
    return _generateRenderJobName(base_name, frames, output_path)

def _getOutputPath(rop):
    """Returns an empty string if it cannot be determined."""
    output_parm = hqrop.getOutputParm(rop)
    if output_parm is not None:
        output_path = output_parm.getReferencedParm().unexpandedString()
    else:
        output_path = ""
    
    return output_path

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def renderFromHip(
    hip_file, project_name, output_driver, frames, dirs_to_create,
    use_render_tracker=True, tile = None, enable_checkpoints=True):
    """Render a set of frames from the given .hip file and output driver.

    This function is called by hq_render_from_hip.py.
    """
    global gRenderTrackerRPC

    import hou

    if use_render_tracker:
        gRenderTrackerRPC = getRenderTrackerRPC()
    else:
        gRenderTrackerRPC = None

    expanded_hip_file = hou.expandString(hip_file)
    rop, tile_callback_parm = _loadHipFileAndGetRopAndTileCallbackParm(
        expanded_hip_file, output_driver, project_name, enable_checkpoints)

    _createDirectories(dirs_to_create)

    # Make sure the output driver is set to render the given frame range
    # instead of any frame.
    if rop.parm('trange') is not None:
        rop.parm("trange").set(1)

    # Turn on mantra-specific options.  Tell mantra to at least split out the
    # version and output file path, and set its -H option.
    # TODO: We should check if -H is already specified.
    rop_type = rop.type().name()
    cmd_parm = rop.parm("soho_pipecmd")
    if rop_type in ("ifd", "baketexture") and cmd_parm is not None:
        cmd = cmd_parm.unexpandedString()
        cmd = _addMantraSpecificArguments(cmd)
        cmd_parm.set(cmd.strip())
    
    if rop_type == "ifd" and tile is not None:
        rop.parm("vm_tile_index").setExpression(str(tile))

    if rop_type in ("alembic", "rop_alembic") and rop.parm("filename"):
        # Evaluate the filename parameter to get the latest time-dependent flag
        # value.
        rop.parm("filename").eval()

        if not rop.parm("filename").isTimeDependent():
            # Special case the Alembic ROP when it is outputting to a single
            # .abc file.  We let the ROP render all frames in one go.
            frame_start = frames[0]
            frame_end = frames[-1]
            frame_incr = 1 if len(frames) == 1 else frames[1] - frames[0]
            _setParm(rop.parmTuple("f"), (frame_start, frame_end, frame_incr))
            _renderRop(rop, ignore_inputs=True)
            return

    print "PROGRESS: 0/%d" % len(frames)
    for i, frame in enumerate(frames):
        # Tell the render tracker about the job id and output file name for
        # this frame.
        output_parm = hqrop.getOutputParm(rop)
        if output_parm is not None and gRenderTrackerRPC is not None:
            gRenderTrackerRPC.startedFrameRender(
                project_name, frame, os.environ["JOBID"],
                output_parm.evalAtFrame(frame))
        
        _setParm(rop.parmTuple("f"), (frame, frame, 1))

        # Make sure Houdini blocks until the render is complete.
        fg_parm = rop.parm("soho_foreground")
        if fg_parm is not None:
            fg_parm.set(1)

        # Set the Mantra tile callback.
        if tile_callback_parm is not None:
            _setTileCallbackParm(
                tile_callback_parm, i, frame, len(frames), project_name,
                use_render_tracker)

        # For non-Mantra rops, print the output file path.
        if rop_type not in ("ifd", "baketexture") and output_parm is not None:
            print "Generating Output File:", output_parm.evalAtFrame(frame)

        _invokeRopAndCatchErrors(rop, project_name, frame, True)
        print "PROGRESS: %d/%d" % (i + 1, len(frames))

        # Let the render tracker know that the frame is finished.
        if gRenderTrackerRPC is not None:
            gRenderTrackerRPC.setFrameRenderFraction(
                project_name, frame, 100.0)


def stitchTiles(hip_file, project_name, output_driver, frames):
    """Merges the tiles together into a single image.

    The outputted image is the path specified on the rop node.
    """
    import hou
    
    expanded_hip_file = hou.expandString(hip_file)
    rop = _loadHipFileAndGetNode(expanded_hip_file, output_driver)
    
    has_failed = False

    print "PROGRESS: 0/%s" % len(frames)
    for frame in frames:
        return_code = _stitchSingleFrame(rop, frame)
        if return_code != 0:
            has_failed = True
            print "Stitching frame %s failed" % frame
        print "PROGRESS: %s/%s " % (frame, len(frames))
    
    if has_failed:
        sys.exit(1)

def _stitchSingleFrame(rop, frame):
    output_path = rop.parm("vm_picture").evalAsStringAtFrame(frame)
    tile_file_pattern = _getTilePattern(rop, frame)
    tile_files = _getFiles(tile_file_pattern)

    pipe = subprocess.Popen("itilestitch %s %s" 
        % (output_path, " ".join(tile_files)), 
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    itilestich_output = _readFromPipeAndPrintOutput(pipe)
    
    if pipe.returncode == 0:
        print "Cleaning up tiles for frame %s." % frame
        _removeFiles(tile_files)
    
    return pipe.returncode

def _removeFiles(files):
    for single_file in files:
        try:
            os.remove(single_file)
        except OSError, exception:
            print exception

def _getTilePattern(rop, frame):
    """Get the glob pattern for the tile files for the specified frame."""
    unexpanded_tile_infix = _getUnexpandedTileInfix(rop, frame)
    output_path = rop.parm("vm_picture").evalAsStringAtFrame(frame)
    tile_infix = re.sub("%\d*d", "*", unexpanded_tile_infix)
    tile_pattern = hutil.file.insertFileSuffix(output_path, tile_infix)

    return tile_pattern

def _getUnexpandedTileInfix(rop, frame):
    """Gets the tile infix string for a specific frame but not a specific tile.
    """
    tile_infix_parm = rop.parm("vm_tile_filename_suffix")

    if tile_infix_parm is not None:
        unexpanded_tile_infix = tile_infix_parm.evalAsStringAtFrame(frame)
    else:
        # Unfortunately, there is no way to access the spare parameters that are
        # not set on the node by the user and so we just have to know what the 
        # tile infix is.
        unexpanded_tile_infix  = DEFAULT_UNEXAPANDED_TILE_INFIX
    
    return unexpanded_tile_infix

def _getFiles(pattern):
    """Uses the given glob pattern to find files but not directories."""
    listing = glob.iglob(pattern)

    return [file_path for file_path in listing if os.path.isfile(file_path)]
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def invokeMantra(ifds, frames, image_paths, delete_ifds, project_name,
    commandline_args, use_render_tracker=True):
    """Invoke mantra for each ifd passed in.

    Log any errors with the render tracker and delete the ifds if we're
    supposed to.  This function is called from hq_mantra.py and is run
    from Python, not hython.
    """
    global gRenderTrackerRPC

    if use_render_tracker:
        gRenderTrackerRPC = getRenderTrackerRPC()
    else:
        gRenderTrackerRPC = None
    
    if image_paths:
        for ifd, frame, image_path in zip(ifds, frames, image_paths):
            _invokeMantraForOneIFD(
                ifd, frame, delete_ifds, project_name, commandline_args,
                image_path)
    else:
        for ifd, frame in zip(ifds, frames):
            _invokeMantraForOneIFD(
                ifd, frame, delete_ifds, project_name, commandline_args)

def _invokeMantraForOneIFD(
    ifd, frame, delete_ifd, project_name, commandline_args, image_path = None):

    if gRenderTrackerRPC is not None and image_path is not None:
        gRenderTrackerRPC.startedFrameRender(
            project_name, frame, os.environ["JOBID"], image_path)

    # Note that it's important that we don't import hou here, since we don't
    # want to use a Houdini Batch license while rendering.
    mantra_bin = "$HFS/bin/mantra"
    if sys.platform == "win32":
        mantra_bin = hutil.file.convertToWinPath(mantra_bin)
        mantra_bin = mantra_bin + ".exe"
        mantra_bin = "\"" + mantra_bin + "\""
        ifd = hutil.file.convertToWinPath(ifd)
   
    # Build command-line arguments.
    split_cmd_args = commandline_args.split()
    split_cmd_args[0] = mantra_bin
    commandline_args = " ".join(split_cmd_args)
    commandline_args = _addMantraSpecificArguments(commandline_args)

    # Set final command.
    if sys.platform == "win32":
        cmd = "%s -f \"%s\"" % (commandline_args, ifd)
    else:
        cmd = "%s -f \"%s\"" % (commandline_args, ifd)

    # Note that on Windows we enclose the command in double quotes
    # to protect against whitespace.  We need to do this because
    # we set shell=True when calling subprocess.Popen().
    # Setting shell=True implicitly runs cmd.exe and passes `cmd`
    # as a an argument.  The enclosing double quotes ensures that `cmd`
    # is treated as a single argument instead of a list of arguments.
    if sys.platform == "win32":
        # The problem mentioned above only occurs for Python <= 2.6.
        py_version_info = sys.version_info
        if py_version_info[0] == 2 and py_version_info[1] <= 6:
            cmd = "\"" + cmd + "\""

    pipe = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # We want to print out information from mantra as it becomes available
    # but also remember it in case it fails with an error.
    mantra_output = _readFromPipeAndPrintOutput(pipe)

    # Note that we don't delete the ifd if the render failed, so the user can
    # more easily diagnose the problem.
    if pipe.returncode != 0:
        if gRenderTrackerRPC is not None:
            gRenderTrackerRPC.setFrameError(
                project_name, frame, "%s" % mantra_output)
        sys.exit(pipe.returncode)

    # Mark the frame as finished and delete the ifd if we're supposed to.
    if gRenderTrackerRPC is not None:
        gRenderTrackerRPC.setFrameRenderFraction(project_name, frame, 1.0)
    if delete_ifd:
        deleteFile(ifd)

def deleteFile(file_name):
    expanded_file_name = os.path.expandvars(file_name)

    if os.path.isfile(expanded_file_name):
        os.unlink(expanded_file_name)
        print "Deleted ifd file: ", expanded_file_name
    else:
        print "Could not find file to delete: ", expanded_file_name

def _readFromPipeAndPrintOutput(pipe):
    # We want to print out information as soon as it becomes available.
    output = ""
    try:
        while True:
            if pipe.poll() is not None:
                # The program has exited, so read the rest of the output.
                output_portion = pipe.stdout.read()
            else:
                # Wait for the program to write out a line of output.
                output_portion = pipe.stdout.readline()

            # Print the output and also remember it.
            sys.stdout.write(output_portion)
            sys.stdout.flush()
            output += output_portion

            if pipe.poll() is not None:
                break
    except KeyboardInterrupt:
        # We need to kill the Mantra subprocess and the subshell.
        # TODO: Need Windows equivalent.
        os.killpg(os.getpgid(pipe.pid), signal.SIGKILL)
        raise

    return output

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def startWedgeRender(hip_file, output_driver, enable_perf_mon, 
                        dirs_to_create, **kwargs):
    """Start a Wedge render.

    Jobs will be create for each wedge that the Wedge node can generate.
    """
    import hou 

    expanded_hip_file = hou.expandString(hip_file)

    _createDirectories(dirs_to_create)

    hq_server = _newHQServerConnection()

    wedge_node = _loadHipFileAndGetNode(expanded_hip_file, output_driver)

    wedge_names = wedge_node.hdaModule().getwedgenames(wedge_node)

    print "PROGRESS: 0/%i" % len(wedge_names)
    for wedge_number, wedge_name in enumerate(wedge_names):
        job_spec = _createWedgeRenderJobSpec(wedge_number, wedge_name, 
                                             hip_file, output_driver,
                                             enable_perf_mon, hq_server)
        _submitHQJobs(hq_server, job_spec)
        print "PROGRESS: %i/%i" % (wedge_number + 1, len(wedge_names))



def _createWedgeRenderJobSpec(wedge_number, wedge_name, hip_file, 
                              output_driver, enable_perf_mon, hq_server):
    """Creates the job spec for a wedge based render."""
    hip_name = os.path.basename(hip_file)
    rop_name = os.path.basename(output_driver)
    
    name = "Simulate -> HIP: %s ROP: %s (%s)" % (hip_name, rop_name, 
                                                 wedge_name)
    
    hq_commands = _getHQueueCommands()
    commands = hqrop.getJobCommands(hq_commands, "hythonCommands", 
                                    "hq_wedge_render.py")

    hq_parm = {"wedge_number": wedge_number,
               "hip_file": hip_file,
               "output_driver": output_driver,
               "enable_perf_mon": enable_perf_mon,}

    environment = {"HQCOMMANDS": hutil.json.utf8Dumps(hq_commands),
                   "HQPARMS": hutil.json.utf8Dumps(hq_parm)}
    
    job_spec = {"name": name,
                "environment": environment,
                "command": commands,}

    # Set the number of cpus that the job will use.
    job_info = _getJobCpuAndTagInfo()
    if "single" in job_info["tags"]:
        job_spec["tags"] = ["single"]
    else:
        job_spec["cpus"] = job_info["cpus"]

    parent_job_id = _getParentJobID(hq_server)
    if parent_job_id is not None:
        job_spec['parentIds'] = [parent_job_id,]

    return job_spec

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def renderWedge(wedge_number, hip_file, output_driver, enable_perf_mon):
    """Renders a specific wedge."""
    import hou

    expanded_hip_file = hou.expandString(hip_file)
    wedge_node = _loadHipFileAndGetNode(expanded_hip_file, output_driver)
    
    rop = hou.node(wedge_node.parm('driver').eval())

    if rop is None:
        print "ERROR: Cannot find output driver: ", output_driver
        sys.exit(1)

    turnOnAlfredStyleReporting(rop)
    
    wedge_node.parm('wrange').set('single')
    wedge_node.parm('wedgenum').set(wedge_number)

    # Turn on performance monitoring.
    if enable_perf_mon:
        hou.hscript("perfmon -o stdout -t ms")

    wedge_node.render()


def startSimulation(hip_file, output_driver, controls_node, slice_divs, 
    num_slices, slice_type, dirs_to_create, enable_perf_mon = False, **kwargs):
    """Start a new simulation.

    Start a tracker in a new thread and submit jobs that will process the
    slices.  This function is called from hq_start_sim.py and is run from
    Python, not hython.
    """
    # First spawn the tracker, turning off verbosity.
    simtracker.setVerbosity(False)
    tracker_thread = threading.Thread(target=lambda: simtracker.serve(0, 0))
    tracker_thread.start()

    # Wait for the tracker to be ready and get the host and ports.
    simtracker.waitForListener()
    tracker_host = socket.gethostname()
    tracker_port = simtracker.getListenPort()
    web_port = simtracker.getWebPort()

    # Output some useful information.
    print ""
    print "Tracker listening on port ", tracker_port
    print ("To view simulation statistics, "
            + "go to http://%(tracker_host)s:%(web_port)s") % locals()
    print ""

    # Connect to the HQ server and get the id of the parent job.  It will also
    # be the parent of the slice jobs and the 'stop tracker' job.
    hq_server = _newHQServerConnection()
    parent_job_id = _getParentJobID(hq_server);

    # Submit new child jobs to process the slices.
    # The child job processes will communicate with the tracker.
    child_ids = _submitSliceJobs(tracker_host, tracker_port, 
        parent_job_id, hq_server, hip_file, output_driver, controls_node,
        slice_divs, num_slices, slice_type, enable_perf_mon, dirs_to_create)

    # Submit a job to cleanup the tracker when the simulation
    # is finished.
    _submitSimCleanupJob(tracker_host, tracker_port, hq_server, 
        parent_job_id, child_ids)

    # Flush printed text to stdout out.  This function will be executed from
    # Python instead of hython which typically buffers its output.
    sys.stdout.flush()

    # Wait for the tracker to finish.
    simtracker.waitForCompletion()


def _submitSliceJobs(tracker_host, tracker_port, parent_job_id, 
    hq_server, hip_file, output_driver, controls_node, slice_divs,
    num_slices, slice_type, enable_perf_mon, dirs_to_create):
    """Submits child jobs that will process slices in the simulation.
    
    The slice information is obtained from the controls node.
    """
    # Figure out how many jobs we need to submit based on the
    # number of slices in the simulation.
    if slice_type == "volume":
        num_slices = slice_divs[0] * slice_divs[1] * slice_divs[2]

    # Set slice job name.
    hip_name = os.path.basename(hip_file)
    rop_name = os.path.basename(output_driver)

    # Submit a child job for each slice.
    child_ids = []
    hq_cmds = _getHQueueCommands()
    commands = hqrop.getJobCommands(
        hq_cmds, "hythonCommands", "hq_sim_slice.py")

    # Keep track of the parent job's cpu and tag info.
    # We need to pass them down to the children.
    job_info = _getJobCpuAndTagInfo(parent_job_id)

    for i in range(num_slices):
        # We subtract 1 because slices are zero-based
        slice_string = _getFormattedIndex(i, num_slices - 1)
        name = ("Simulate -> HIP: %s ROP: %s (Slice %s)" 
                    % (hip_name, rop_name, slice_string))
        child_job = {
            "name": name,
            "environment": { 
                "HQCOMMANDS": hutil.json.utf8Dumps(hq_cmds),
                "HQPARMS": hutil.json.utf8Dumps({
                    "tracker_host": tracker_host,
                    "tracker_port": tracker_port,
                    "hip_file": hip_file,
                    "output_driver": output_driver,
                    "controls_node": controls_node,
                    "slice_divs": slice_divs,
                    "slice_type": slice_type,
                    "enable_perf_mon": enable_perf_mon,
                    "slice_num": i,
                    "dirs_to_create": dirs_to_create 
                })
            },
            "command" : commands
        }

        # Set the number of cpus that the job will use.
        if "single" in job_info["tags"]:
            child_job["tags"] = ["single"]
        else:
            child_job["cpus"] = job_info["cpus"]

        if parent_job_id is not None:
            child_job["parentIds"] = [parent_job_id,]

        new_job_ids = _submitHQJobs(hq_server, child_job)
        if len(new_job_ids) != 0:
            print "Submitted job for slice ", i
            child_ids.append(new_job_ids[0])
    return child_ids

def _submitSimCleanupJob(tracker_host, tracker_port, hq_server, 
        parent_job_id, child_ids):
    """Submits a job to cleanup the simulation when it is complete.

    The new job will be a sibling of this job and will have the same children.
    """
    hq_cmds = _getHQueueCommands()
    commands = hqrop.getJobCommands(
        hq_cmds, "pythonCommands", "hq_stop_sim.py")

    cleanup_job = {
        "name": "Stop Tracker",
        "environment": { 
            "HQCOMMANDS": hutil.json.utf8Dumps(hq_cmds),
            "HQPARMS": hutil.json.utf8Dumps({
                "tracker_host": tracker_host,
                "tracker_port": tracker_port
            })
        },
        "tags": ["excludeProgress", "single"],
        "command": commands
    }

    if parent_job_id is not None:
        cleanup_job["parentIds"] = [parent_job_id,]

    cleanup_job["childrenIds"] = child_ids

    new_job_ids = _submitHQJobs(hq_server, cleanup_job)
    if len(new_job_ids) != 0:
        print "Submitted cleanup job"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def simulateSlice(tracker_host, tracker_port, hip_file, output_driver, 
    controls_node, slice_divs, slice_num, slice_type, enable_perf_mon, 
    dirs_to_create):
    """Simulate a slice of a simulation."""
    import hou

    # Load the hip file and get the controls dop.
    expanded_hip_file = hou.expandString(hip_file)
    controls_dop = _loadHipFileAndGetNode(expanded_hip_file, controls_node)

    _createDirectories(dirs_to_create) 

    # Set the tracker address.
    controls_dop.parm("address").deleteAllKeyframes()
    controls_dop.parm("address").set(tracker_host)
    controls_dop.parm("port").set(tracker_port)

    # Set slice division information.
    if slice_type == "volume":
        slice_div_parm = controls_dop.parmTuple("slicediv")
        vis_slice_div_parm = controls_dop.parmTuple("visslicediv")
        if slice_div_parm is not None:
            slice_div_parm.set(slice_divs)
        if vis_slice_div_parm is not None:
            vis_slice_div_parm.set(slice_divs)

    # Set the slice number.
    hou.hscript("setenv SLICE=" + str(slice_num))
    hou.hscript("varchange")

    # Make sure the rop exists.
    rop = hou.node(output_driver)
    if rop is None:
        print "ERROR: Cannot find output driver: ", output_driver
        sys.exit(1)

    # Turn on Alfred-style progress reporting on Geo ROP.
    alf_prog_parm = rop.parm("alfprogress")
    if alf_prog_parm is not None:
        alf_prog_parm.set(1)

    # Set the frame range.
    frame_range = _getFrameRangeFromRop(rop)
    _setParmInROPChain(rop, "trange", 1)
    _setParmInROPChain(rop, "f", frame_range)

    # Turn on performance monitoring.
    if enable_perf_mon:
        hou.hscript("perfmon -o stdout -t ms")

    # Simulate!
    _renderRop(rop)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def stopSimulation(tracker_host, tracker_port):
    """Stops the tracker process.

    This function is called from hq_stop_sim.py.
    """
    # Connect to the tracker.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((tracker_host, tracker_port))

    # Send the quit message.
    msg = "quit"
    msg_len = struct.pack("!L", len(msg))
    msg = msg_len + msg
    s.send(msg)

    # Read the ack from tracker and send back an empty message to indicate
    # success.
    s.recv(1)
    s.send('')

    s.close()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def runSimulationWithoutSlices(hip_file, output_driver, dirs_to_create, 
    enable_perf_mon=False, dependency_order="frame_by_frame", **kwargs):
    """Runs the simulation by rendering the given output driver.
    
    This function is called from hq_run_sim_without_slices.py.
    """
    import hou

    expanded_hip_file = hou.expandString(hip_file)
    rop = _loadHipFileAndGetNode(expanded_hip_file, output_driver)

    # Create output directories if requested to do so.
    _createDirectories(dirs_to_create) 

    # Turn on Alfred-style progress reporting on Geo ROPs.
    alf_prog_parm = rop.parm("alfprogress")
    if alf_prog_parm is not None:
        alf_prog_parm.set(1)

    # Set the frame range.
    frame_range = _getFrameRangeFromRop(rop)
    _setParmInROPChain(rop, "trange", 1)
    _setParmInROPChain(rop, "f", frame_range)

    # Turn on performance monitoring.
    if enable_perf_mon:
        hou.hscript("perfmon -o stdout -t ms")

    # Get the render method (frame-by-frame or node-by-node).
    render_method = _convertDependencyOrderToRenderMethod(dependency_order)
    
    # Simulate!
    _renderRop(rop, method=render_method)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def cloudRenderChooseHFS(
        project_name, hip_path, rop_node_path, desired_houdini_version,
        environment=None, project_path=None):
    """Chooses $HFS and submits a job that will submit the render job.

    This function is called from hq_cloud_render_choose_hfs.py.  It runs in
    the cloud and is part of the bootstrapping process of starting a render
    in the cloud.
    """
    # TODO: Remove the project_path parameter.  It only exists for temporary
    #       backward compatibility with a few versions of Houdini.

    # Note that $HQCOMMANDS isn't set because we don't know which $HFS to use.
    # Also note that we set $JOB to the project path, in case their hip file
    # uses $JOB references.  If it doesn't, then the hip file will be inside
    # the project path and $JOB will be the same as $HIP.
    hfs = _findClosestCloudHFS(desired_houdini_version)
    python_version = "%d.%d" % sys.version_info[:2]
    script = "$HFS/houdini/scripts/hqueue/hq_cloud_render_submit.py"
    job = {
        "name": "Render %(hip_path)s %(rop_node_path)s"
            " (submit cloud render)" % locals(),
        "shell": "bash",
        "priority": 10,
        "environment": {
            "HQPARMS": hutil.json.utf8Dumps({
                "hip_path": hip_path,
                "project_name": project_name,
                "rop_node_path": rop_node_path
            }),
        },
        "command": "export HOUDINI_PYTHON_VERSION=%(python_version)s &&"
            " export HFS=%(hfs)s && cd $HFS && source houdini_setup &&"
            " hython %(script)s" % locals()
    }

    # If given, environment contains a dictionary of values to preserve
    # in child jobs.
    if environment is not None:
        for name, value in environment.items():
            hqrop.setPreservedEnvironmentVariable(name, value)

    job["parentIds"] = [os.environ["JOBID"],]
    _submitHQJobs(_newHQServerConnection(), job)

def _findClosestCloudHFS(desired_houdini_version):
    # If the desired version could not be found, find the best match.
    desired_version_tuple = tuple(
        int(x) for x in desired_houdini_version.split("."))
    best_version_tuple = None

    hfs_prefix = "/opt/hfs"
    for hfs_dir in glob.glob(hfs_prefix + "*"):
        if not os.path.isdir(hfs_dir):
            continue

        version_string = hfs_dir[len(hfs_prefix):]
        version_tuple = tuple(int(x) for x in version_string.split("."))

        if _isBetterHFSVersion(
                version_tuple, desired_version_tuple, best_version_tuple):
            best_version_tuple = version_tuple

    if best_version_tuple is None:
        # We could not find a version of Houdini which
        # satisfies the desired version.
        print "ERROR: Houdini '%i.%i' is not supported on the Cloud." \
            % desired_version_tuple[:2]
        sys.exit(1)

    return hfs_prefix + ".".join(str(x) for x in best_version_tuple)

def _isBetterHFSVersion(version, desired_version, best_version):
    """Return whether a particular Houdini version is the best found so far.
    
    The versions are tuples containing the current one being considered, the
    desired version, and the best one found so far.  Return whether or not the
    current one is the new best one found.  Note that best_version may be None.
    """
    if version[:2] != desired_version[:2]:
        return False

    if best_version is None:
        return True

    if best_version < desired_version:
        # We haven't yet find a high enough version.  Take this one if
        # it's higher.
        return version > best_version

    # We had found a high enough version.  Take this one if it's also high
    # enough and it's lower than the best found.
    return version >= desired_version and version < best_version

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def cloudRenderSubmit(hip_path, project_name, rop_node_path):
    """Load the hip file, adjust the rop to use the HQServer running in the
    cloud instead of starting up the load, and invoke it to submit the job.

    This function is called from hq_cloud_render_submit.py.  It runs in
    the cloud and is part of the bootstrapping process of starting a render
    in the cloud.
    """
    import hou, cloud

    rop_node = _loadHipFileAndGetNode(hip_path, rop_node_path)

    # Set the project name in the rop's parameter holding the project parms.
    project_parms = cloud.getCachedProjectParmsFromRop(rop_node)
    if project_parms is not None:
        project_parms["project_name"] = project_name
        cloud.saveProjectParmsToRop(rop_node, project_parms)

    if rop_node.parm("hq_use_cloud1") is not None:
        rop_node.parm("hq_use_cloud1").set(0)
    rop_node.parm("hq_server").set(os.environ["HQSERVER"])
    rop_node.parm("hq_hfs").set(os.environ["HFS"])

    # Toggle HQueue Render parameters based on the output driver's type.
    output_driver = hqrop.getOutputDriver(rop_node)
    if output_driver.type().name() != "ifd":
        # Turn off Generate IFDs if the output driver is not a Mantra ROP.
        rop_node.parm("hq_makeifds").set(0)
    if output_driver.type().name() == "dop" \
        or output_driver.type().name() == "rop_dop":
        # Turn on Batch All Frames if the output driver is a Dynamics ROP.
        rop_node.parm("hq_batch_all_frames").set(1)

    # Make sure to use the render tracker when rendering.
    rop_node.parm("hq_use_render_tracker").set(1)

    rop_node.render()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def startClusterSimulation(hip_file, output_driver, cluster_node,
    dirs_to_create, enable_perf_mon = False, **kwargs):
    """ Start a new cluster simulation.
    """
    import hou
    
    expanded_hip_file = hou.expandString(hip_file)
    cluster_sop = _loadHipFileAndGetNode(expanded_hip_file, cluster_node)

    _createDirectories(dirs_to_create)

    number_of_clusters = cluster_sop.parm("num_clusters").eval()
    
    hq_server = _newHQServerConnection()

    print "PROGRESS: 0/%i" % number_of_clusters
    for cluster in range (number_of_clusters):
        job_spec = _createClusterJobSpec(cluster, number_of_clusters,
                                         hip_file, output_driver, cluster_node,
                                         enable_perf_mon, hq_server)
        _submitHQJobs(hq_server, job_spec)
        print "PROGRESS: %i/%i" % (cluster + 1, number_of_clusters)
       


def _createClusterJobSpec(cluster_number, number_of_clusters, hip_file, 
                          output_driver, cluster_node, enable_perf_mon, 
                          hq_server):
    """Creates the job spec for the cluster job.
    """
    
    hip_name = os.path.basename(hip_file)
    rop_name = os.path.basename(output_driver)
    cluster_string = _getFormattedIndex(cluster_number, number_of_clusters - 1)
    name = "Simulate -> HIP: %s ROP: %s (Cluster %s) " % (hip_name, rop_name,
                                                          cluster_string)
    
    hq_cmds = _getHQueueCommands()
    commands = hqrop.getJobCommands(
        hq_cmds, "hythonCommands", "hq_sim_cluster.py")

    hq_parms = {
        "cluster_number": cluster_number,
        "hip_file": hip_file,
        "output_driver": output_driver,
        "cluster_node": cluster_node,
        "enable_perf_mon": enable_perf_mon,
    }
    job_spec = {
        "name": name,
        "environment": {
            "HQCOMMANDS": hutil.json.utf8Dumps(hq_cmds),
            "HQPARMS": hutil.json.utf8Dumps(hq_parms),
        },
        "command": commands,
    }

    # Set the number of cpus that the job will use.
    job_info = _getJobCpuAndTagInfo()
    if "single" in job_info["tags"]:
        job_spec["tags"] = ["single"]
    else:
        job_spec["cpus"] = job_info["cpus"]
 
    # We set this jobs parent to be parent of the current job
    # This parent job will be the empty job that just contains the active jobs
    parent_job_id = _getParentJobID(hq_server);
    if parent_job_id is not None:
        job_spec["parentIds"] = [parent_job_id,]
    
    return job_spec

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def simulateCluster(cluster_number, hip_file, output_driver, cluster_node,
    enable_perf_mon):
    """Runs the cluster simulation on the client machine.
    """
    import hou

    expanded_hip_file = hou.expandString(hip_file)
    rop = _loadHipFileAndGetNode(expanded_hip_file, output_driver)
    cluster_sop = hou.node(cluster_node)

    turnOnAlfredStyleReporting(rop)

    if rop is None:
        print "ERROR: Cannot find output driver: ", output_driver
        sys.exit(1)

    cluster_sop.parm("cluster_filter").set("$CLUSTER")

    # The global variable still has to be set so that the files are named 
    # correctly
    hou.hscript("setenv CLUSTER=" + str(cluster_number))
    hou.hscript("varchange CLUSTER")

    # Turn on performance monitoring.
    if enable_perf_mon:
        hou.hscript("perfmon -o stdout -t ms")

    _renderRop(rop)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def callFunctionWithHQParms(function):
    """Call a particular function, passing the arguments in $HQPARMS.
    
    This function is used from the scripts that call into this module.
    It will make sure that required parameters are passed and ignore extra parameters.
    """
    # Determine which parameters have default values, and initialize the
    # keyword arguments with those values.
    argspec = inspect.getargspec(function)
    parm_names = argspec[0]
    default_values = argspec[3] or ()
    kwargs = dict(zip(
        parm_names[len(parm_names) - len(default_values):], default_values))

    # Update the dictionary of arguments with those passed via $HQPARMS.
    kwargs.update(hutil.json.utf8Loads(os.environ["HQPARMS"]))
    
    for parm_name in kwargs.keys():
        if parm_name not in parm_names:
            print ("Warning: %s() got an unexpected paramter '%s'." % (
                function.__name__, parm_name))

    for parm_name in parm_names:
        if parm_name not in kwargs:
            raise TypeError("%s() takes the parameter '%s' (not given)" % (
                function.__name__, parm_name))
    else:
        return function(**kwargs)


def _renderRop(rop, *args, **kwargs):
    if hasattr(rop, 'render'):
        rop.render(*args, **kwargs)
    elif rop.parm("execute"):
        rop.parm("execute").pressButton()
    else:
        raise TypeError("Could not render given node: " + rop.name())


def _convertDependencyOrderToRenderMethod(dependency_order):
    # Render frame-by-frame instead of node-by-node by default.
    import hou

    if dependency_order == "node_by_node":
        return hou.renderMethod.RopByRop
    else:
        return hou.renderMethod.FrameByFrame

    return render_method


def _setIFDParmsAndGetExpandedPath(ifd_path, frame, rop):
    """Turn on IFD generation on the specified ROP and set IFD parameters.

    Return the IFD path with variables expanded.
    """
    import hou

    # Turn on IFD generation.
    rop.parm("soho_outputmode").set(1)
    
    # Instruct the ROP to not return from a render() call until the IFD is
    # generated.
    rop.parm("soho_foreground").set(1)

    # Set the IFD path parameter to the unexpanded IFD path.
    rop.parm("soho_diskfile").set(ifd_path)

    # If the IFD path contains $ACTIVETAKE then we need to temporarily switch
    # takes so that $ACTIVETAKE expands to the correct take name.
    rop_take = None
    cur_take = None
    if ifd_path.find("$ACTIVETAKE") >= 0 \
        and rop.parm("take").eval() != "_current_":
        rop_take_name = rop.parm("take").eval()
        rop_take = hou.takes.findTake(rop_take_name)
        cur_take = hou.takes.currentTake()
        if rop_take != cur_take:
            hou.takes.setCurrentTake(rop_take)

    # Use the ROP IFD path parameter to expand the IFD path.
    expanded_ifd_path = rop.parm("soho_diskfile").evalAtFrame(frame)

    # Restore the previous current take.
    if rop_take != cur_take:
        hou.takes.setCurrentTake(cur_take)

    # Substitute the platform-dependent prefix in the IFD path
    # with $HQROOT to make the path platform-independent so the IFD file
    # can be located by any machine on the farm.
    expanded_ifd_path = _substituteWithHQROOT(expanded_ifd_path)

    return expanded_ifd_path


def _setParmInROPChain(rop, parm_name, vals):
    """Set the values for the given parameters in each node of the ROP chain.

    `rop` is the last node in the chain.
    `parm_name` is the name of the parameter or parameter tuple to be set.
    `val` is the parameter values.
    """
    import hou
    rop_stack = [rop, ]
    visited_rops = []

    while len(rop_stack) > 0:
        cur_rop = rop_stack.pop()

        if type(vals) == type([]) or type(vals) == type(()):
            parm = cur_rop.parmTuple(parm_name)
        else:
            parm = cur_rop.parm(parm_name)

        # Set the parameter if it exists.
        if parm is not None:
            _setParm(parm, vals)

        visited_rops.append(cur_rop)

        # Examine inputs.
        for input_node in cur_rop.inputs():
            if input_node is None:
                continue

            if input_node.type().category() == hou.ropNodeTypeCategory() \
                and input_node not in visited_rops:
                rop_stack.append(input_node)


def _setParm(parm, value):
    """Sets a parm with the given value.

    Will handle parmTuples and cases where the parm has an expression set.
    """
    try:    
        zipped_items = zip(parm, value)
    except TypeError:
        parm.getReferencedParm().deleteAllKeyframes()
        parm.getReferencedParm().set(value)
    else:
        for subparm, subvalue in zipped_items:
            subparm.getReferencedParm().deleteAllKeyframes()
            subparm.getReferencedParm().set(subvalue)


def _getTargetFramesFromRop(rop):
    """Return a tuple of frame numbers that the given output driver is 
    configured to render.
    """
    (start_frame, end_frame, frame_incr) = _getFrameRangeFromRop(rop)
    frames = range(start_frame, end_frame + 1, frame_incr)
    return frames


def _getFrameRangeFromRop(rop):
    """Return a 3-tuple of start_frame, end_frame and frame_increment 
    for the render frame range in the given ROP node."""
    start_frame, end_frame, frame_incr =  _getFrameRangeFromRopRecurse(rop)

    # If a frame range could not be found then just return the current frame
    # as the frame range.
    if start_frame is None or end_frame is None or frame_incr is None:
        print ("Warning: Could not determine frame range from '%s' node." \
              " Using current frame instead.") % rop.path()

        import hou
        start_frame = int(hou.frame())
        end_frame = int(hou.frame())
        frame_incr = 1

    return start_frame, end_frame, frame_incr


def _getFrameRangeFromRopRecurse(rop):
    """Helper function for _getFrameRangeFromRop().

    Recursively traverses nodes to find the desired frame range.
    """
    import hou

    start_frame = None
    end_frame = None
    frame_incr = None

    if rop.type().name() == "merge":

        # For Merge ROPs,
        # the start frame is the min. start frame of its inputs,
        # the end frame is the max. end frame of its inputs,
        # and the increment is the min. increment of its inputs.
        for input_rop in rop.inputs():
            in_start, in_end, in_inc = _getFrameRangeFromRopRecurse(input_rop)
            if start_frame is None or in_start < start_frame:
                start_frame = in_start
            if end_frame is None or in_end > end_frame:
                end_frame = in_end
            if frame_incr is None or in_inc < frame_incr:
                frame_incr = in_inc
    elif rop.type().name() == "fetch":
        # Get the frame range from the fetched ROP.
        source_rop = _getFetchedROP(rop)
        start_frame, end_frame, frame_incr = \
            _getFrameRangeFromRopRecurse(source_rop)
    else:
        # Get the start, end and increment frame values.
        # If trange absent, we assume the full range.
        if (rop.parm('trange') is not None) and (rop.evalParm("trange") == 0):
            start_frame = int(hou.frame())
            end_frame = int(hou.frame())
            frame_incr = 1
        elif rop.parmTuple("f") is not None:
            start_frame = int(rop.evalParm("f1"))
            end_frame = int(rop.evalParm("f2"))
            frame_incr = int(rop.evalParm("f3"))
        else:
            # The node does not have a frame range parameter set.
            # Try searching for the frame range on its input nodes.
            for input_node in rop.inputs():
                start_frame, end_frame, frame_incr = \
                    _getFrameRangeFromRopRecurse(input_node)
                if start_frame is not None:
                    break

    if frame_incr is not None and frame_incr <= 0:
        frame_incr = 1

    return (start_frame, end_frame, frame_incr)


def _getFetchedROP(fetch_rop, return_inputs=False):
    """Return the source ROP that is being fetched by the given Fetch ROP.

    Fetching is recursive until a non-Fetch ROP is found.
    If `return_inputs` is True, then also return a tuple of all the nodes
    that input into the fetched ROP and any intermediary Fetch ROPs.
    """
    source_rop_path = fetch_rop.parm("source").eval()
    source_rop = fetch_rop.node(source_rop_path)
    if source_rop is None:
        error_message = "ERROR: %s fetching ROP that does not exist." \
            % fetch_rop.path()
        print error_message
        sys.exit(1)

    inputs = source_rop.inputs()

    # Fetch again if our source ROP is a Fetch ROP.
    if source_rop.type().name() == "fetch":
        source_rop, fetched_inputs = _getFetchedROP(source_rop, True)
        inputs = inputs + fetched_inputs

    if return_inputs:
        return source_rop, inputs
    else:
        return source_rop

def createBinaryPartitionOrder(sequence):
    """Returns a new list ordered by doing a binary subdivision on the sequence.
    """
    if len(sequence) <= 2:
        return list(sequence)
    else:
        result = [sequence[0], sequence[-1]]
        subsequences = [sequence[1:-1]]

        while subsequences:
            extra_results, subsequences = _partitionSubsequences(subsequences)
            result.extend(extra_results)
        return result

def _partitionSubsequences(subsequences):
    new_subsequences = []
    result = []

    for subsequence in subsequences:
        mid_point, partitions = _partitionSingleSubsequence(subsequence)
        result.append(mid_point)
        new_subsequences.extend(partitions)

    return result, new_subsequences

def _partitionSingleSubsequence(subsequence):
    new_subsequences = []

    mid_index = (len(subsequence)) // 2
    
    first_half = subsequence[0:mid_index]
    if first_half:
        new_subsequences.append(first_half)

    second_half = subsequence[mid_index + 1: len(subsequence)]
    if second_half:
        new_subsequences.append(second_half)

    return subsequence[mid_index], new_subsequences

def _generateRenderJobName(base_name, frames, output_path = ""):
    frame_word = _getFrameWord(frames)
    padding = _determineFramePadding(output_path)
    frames_string = _frameListAsString(frames, padding)

    return ("%s (%s: %s)" % (base_name, frame_word, frames_string))

def _getFrameWord(frames):
    if len(frames) == 1:
        return "Frame"
    else:
        return "Frames"

def _frameListAsString(frames, padding):
    if len(frames) == 1 and padding > 0:
        return "".join(["%0", str(padding), "d"]) % frames[0]
    else:
        return ", ".join((str(frame) for frame in frames))

def _determineFramePadding(output_path):
    # Technically this pattern matches invalid patterns such as ${F3 ad $F3}.
    # I suspect that in practice that this should not be an issue
    result = re.search("\${?F(?P<padding>\d+)}?", output_path)
    if not result:
        # This is for the case where people have padzero hscript commands
        # left over from when $F# padding was not working
        result = re.search("padzero\(\s*(?P<padding>\d+)\s*,\s*\$F\s*\)",
                            output_path)

    if result:
        return int(result.group('padding'), 10)
    else:
        return 0

def _getFormattedIndex(index, total):
    digits = _determineNumberOfDigits(total)
    return "".join(["%0", str(digits), "i"]) % index

def _determineNumberOfDigits(number):
    """Gets the number of digits in a number.

    This is only meant to work with positive integers.
    """
    return len(str(number))

def _expandFrameVarsInString(source_str, frame):
    """Expands frame variables (i.e. $F) found in the given string with `frame`.
    """
    str_frame = str(frame)
    expanded_str = source_str

    # Replace $F[0-9]+ with the padded frame number.
    regex = "\$F[0-9]+"
    matches = re.findall(regex, expanded_str)
    for match in matches:
        num = int(match[2:])
        if num > 0:
            padded_frame = str_frame.zfill(num)
        else:
            padded_frame = ""
        expanded_str = expanded_str.replace(match, padded_frame)

    # Replace ${F[0-9]+} with the padded frame number.
    regex = "\${F[0-9]+}"
    matches = re.findall(regex, expanded_str)
    for match in matches:
        num = int(match[3:-1])
        if num > 0:
            padded_frame = str_frame.zfill(num)
        else:
            padded_frame = ""
        expanded_str = expanded_str.replace(match, padded_frame)

    # Replace $F with the frame number.
    expanded_str = expanded_str.replace("$F", str_frame)

    # Replace ${F} with the frame number.
    expanded_str = expanded_str.replace("${F}", str_frame)
    
    return expanded_str


def turnOnAlfredStyleReporting(rop):
    alf_prog_parm = rop.parm("alfprogress")
    if alf_prog_parm is not None:
        alf_prog_parm.set(1)


def _enableMantraCheckpoints(rop, enable):
    """Turn on or off checkpoint files in the given Mantra ROP."""
    OUTPUT_CHECKPOINTS_PARM_NAME = "vm_writecheckpoint"
    RESUME_CHECKPOINTS_PARM_NAME = "vm_readcheckpoint"
    OVERRIDE_CHECKPOINT_FILE_PARM_NAME = "vm_overridecheckpointname"
    CHECKPOINT_FILE_NAME_PARM_NAME = "vm_checkpointname" 

    if rop.parm(OUTPUT_CHECKPOINTS_PARM_NAME) is None:
        print "WARNING: Unable to set Mantra checkpointing due to an old " \
              "version of the Mantra ROP.  To enable checkpointing, " \
              "create a new Mantra ROP in a newer Houdini version."
        return


    if not enable:
        # Turn off checkpoint parameters.
        if rop.parm(OUTPUT_CHECKPOINTS_PARM_NAME).eval():
            rop.parm(OUTPUT_CHECKPOINTS_PARM_NAME).set(False)
        if rop.parm(RESUME_CHECKPOINTS_PARM_NAME).eval():
            rop.parm(RESUME_CHECKPOINTS_PARM_NAME).set(False)
        return

    # Turn on checkpoint parameters.
    rop.parm(OUTPUT_CHECKPOINTS_PARM_NAME).set(True)
    rop.parm(RESUME_CHECKPOINTS_PARM_NAME).set(True)

    # We need to override the checkpoint file name so that it includes the
    # HQueue root job id.  To do that, we have to ensure that the checkpoint
    # override parameters are added to the Mantra ROP.
    need_override_checkpoint_parm = False
    need_checkpoint_name_parm = False
    if rop.parm(OVERRIDE_CHECKPOINT_FILE_PARM_NAME) is None:
        need_override_checkpoint_parm = True
    if rop.parm(CHECKPOINT_FILE_NAME_PARM_NAME) is None:
        need_checkpoint_name_parm = True

    if need_override_checkpoint_parm or need_checkpoint_name_parm:
        import hou
        ptg = rop.parmTemplateGroup()
        if need_override_checkpoint_parm:
            ptg.addParmTemplate(
                hou.ToggleParmTemplate(
                    OVERRIDE_CHECKPOINT_FILE_PARM_NAME, 
                    "Override Checkpoint File Name"))
        if need_checkpoint_name_parm:
            ptg.addParmTemplate(
                hou.StringParmTemplate(
                    CHECKPOINT_FILE_NAME_PARM_NAME, "Checkpoint File Name", 1))

        rop.setParmTemplateGroup(ptg)

    # Turn on the checkpoint override and set the file name.
    # Include the HQueue root job id as a part of the checkpoint file name
    # so that we can distinguish which jobs have checkpointing turned on
    # and which do not.
    rop.parm(OVERRIDE_CHECKPOINT_FILE_PARM_NAME).set(True)
    root_job_id = os.environ.get("ROOTJOBID", None)
    if root_job_id is None:
        # It's possible that the job is running on an older HQueue farm
        # where ROOTJOBID does not exist.  In this case we just exclude
        # the job id from the checkpoint file name.
        root_job_id = ""
    checkpoint_file_name = \
        "`chs(\"vm_picture\")`.hq%s.mantra_checkpoint" % root_job_id
    rop.parm(CHECKPOINT_FILE_NAME_PARM_NAME).set(checkpoint_file_name)
