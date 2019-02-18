import mvexportutils
import os
import threading

def isSupported():
    return os.path.exists(os.environ['HFS'] + '/bin/mcp32.exe')

def updateFrameCB(line, data):
    l = line.lstrip()
    if l.startswith("Writing"):
        tokens = l.rsplit(None, 1)
        if tokens[-1].isdigit():
            data.setFrame(int(tokens[-1]))

def encode(kwargs):
    args = []
    args.append(os.environ['HFS'] + '/bin/mcp32')

    def convertFormatStringToFrameVar(format_string):
        import re	
        p = re.compile('%0?[1-9]?d')
        def replace(match):
            if len(match.group()) == 4:
                return '$F' + match.group()[2]
            elif len(match.group()) == 2:
                return '$F'
            else:
                return match.group()

        new_string = p.sub(replace, format_string, 1)
        if new_string == format_string:
            return None
        else:
            return new_string

    n_frames = len(kwargs['imagefiles'])
    format_string = convertFormatStringToFrameVar(
                                          kwargs['imagefilesstringformat'])
    if format_string != None:
        args.extend(['-f', '1', "%d" % n_frames, format_string])
    else:
        args.extend(kwargs['imagefiles'])

    if kwargs.has_key('audiofile') and len(kwargs['audiofile']) > 0:
        if kwargs.has_key('audiocopy') and kwargs['audiocopy']:
            args.extend(['-a', '-x', kwargs['audiofile']])
        else:
            args.extend(['-a', kwargs['audiofile']])
    
    if kwargs['outputformat'] == 'mov':
        args.extend(['-o', '-v', '-l', 'QT:QuickTime',
                     '-w', "%d" % kwargs['xres'],
                     '-h', "%d" % kwargs['yres'],
                     '-r', "%g" % kwargs['framerate'],
                     kwargs['outputfile']])
    elif kwargs['outputformat'] == 'avi':
        args.extend(['-o', '-v', '-l', 'VFW:AVI',
                     '-w', "%d" % kwargs['xres'],
                     '-h', "%d" % kwargs['yres'],
                     '-r', "%g" % kwargs['framerate'],
                     kwargs['outputfile']])

    # A 32 bit executable cannot load the 64 bit image DSOs.
    os.environ['HOUDINI_DISABLE_IMAGE_DSO'] = '1'

    # We can only update the progress via the main thread so we need to run the
    # subprocess in another thread (RunThread).  We will use an instance of the
    # FrameData class to notify the main thread whenever the frame progress has
    # been updated.  Moreover, the FrameData's condition synchronization object
    # is also used by RunThread to wake up the main thread when it finishes.
    class FrameData():
        def __init__(self):
            self._frame = 0
            self.condition = threading.Condition()

        def setFrame(self, frame):
            self.condition.acquire()
            self._frame = frame
            self.condition.notify()
            self.condition.release()

        def getFrame(self):
            self.condition.acquire()
            f = self._frame
            self.condition.release()
            return f

    class RunThread ( threading.Thread ):
        def __init__(self, args, stderrcallback, condition):
            self.args = args
            self.stderrcallback = stderrcallback
            self.condition = condition
            # We need a flag to indicate the thread is done that's protected by
            # the condition's lock to avoid the situation where the main thread
            # checks this thread's status immediately after we release the lock
            # at the end of run(), but before run() exits, causing it to wait
            # on a signal that will never come.
            self.finished = False
            threading.Thread.__init__(self)
        def run(self):
            # Suppressing the console window seems to prevent QuickTime from
            # displaying the compression component dialogs, causing it to hang.
            self.retval = mvexportutils.runAsynchronous(
                               self.args, suppresswindow=False,
                               stderrcallback=self.stderrcallback)
            self.condition.acquire()
            self.finished = True
            self.condition.notify()
            self.condition.release()

    frame_data = FrameData()
    run_thread = RunThread(args, (updateFrameCB, frame_data),
                           frame_data.condition)
    frame_data.condition.acquire()
    run_thread.start()
    while not run_thread.finished:
        frame_data.condition.wait()
        hou.updateProgressAndCheckForInterrupt(
                                      frame_data.getFrame() * 100 / n_frames)
    frame_data.condition.release()
    return run_thread.retval
