def setupSysPath():
    """Add Houdini's script paths to sys.path."""
    import sys, os

    python_version = "%d.%d" % sys.version_info[:2]
    python_version_no_dot = "%d%d" % sys.version_info[:2]
    paths = ["%s/houdini/python%slibs" % (os.environ['HFS'], python_version),]
    if sys.platform == "win32":
        paths.append("%s/python%s/lib/site-packages" 
            % (os.environ['HFS'], python_version_no_dot))
    else:
        paths.append("%s/python/lib/python%s/site-packages" 
            % (os.environ['HFS'], python_version))

    for path in paths:
        if path not in sys.path:
            sys.path.append(path)

# This script is invoked from a regular Python shell, not hython, so we need
# to add Houdini's script paths to sys.path before we can import hqlib (and
# the modules it depends on).
setupSysPath()
import hqlib

if __name__ == '__main__':
    hqlib.callFunctionWithHQParms(hqlib.startSimulation)

