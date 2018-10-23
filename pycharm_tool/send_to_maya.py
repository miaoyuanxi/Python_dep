"""
PyCharm python script by Yann Schmidt.
Version: 1.0
---
Send whole file to Maya via commandPort.
http://www.yannschmidt.com/blog/create-send-maya-command-pycharm
---
Inspired from MayaSublime plugin for Sublime Text 2/3.
https://github.com/justinfx/MayaSublime
"""

import sys
import textwrap
import time
from telnetlib import Telnet

# Sync Settings for Maya
# -----
# You should verify and modify it if needed.

# Maya commandPort HOSTNAME
maya_hostname = "127.0.0.1"

# Maya commandPort to communicate via Python
python_command_port = 7002

# Maya commandPort to communicate via MEL
mel_command_port = 7001

# -----------------------


class SendToMaya(object):
    """
    Send to Maya command for PyCharm.
    ---
    Send the current script by Telnet to Maya for executing it.
    """

    # A template wrapper for sending Python source safely
    # over the socket.
    # Executes in a private namespace to avoid collisions
    # with the main environment in Maya.
    # Also handles catches and printing exceptions so that
    # they are not masked.
    PY_CMD_TEMPLATE = textwrap.dedent('''
        import traceback
        import __main__
        namespace = __main__.__dict__.get('_pycharm_SendToMaya_command')
        if not namespace:
            namespace = __main__.__dict__.copy()
            __main__.__dict__['_pycharm_SendToMaya_command'] = namespace
        namespace['__file__'] = {2!r}
        try:
            {0}({1!r}, namespace, namespace)
        except:
            traceback.print_exc()
    ''')

    def __init__(self):
        self.execType = 'execfile'
        self.fileType = 'python'
        self.file = str(sys.argv[1])
        self.sep = None

        # Set the fileType
        self.is_python()

        # Set settings
        self._settings = dict()
        self.init_settings()

    def init_settings(self):
        self._settings['host'] = maya_hostname

        if self.fileType == 'python':
            self._settings['port'] = python_command_port
            self.sep = '\n'
        else:
            self._settings['port'] = mel_command_port
            self.sep = '\r'

    def is_python(self):
        """
        Test if a file a in python syntax else, mel
        """
        if sys.argv[1].endswith('.py'):
            self.fileType = 'python'
        elif sys.argv[1].endswith('.mel'):
            self.fileType = 'mel'
        else:
            self.fileType = None

    def run(self):
        """
        Send the data.
        """
        if self.fileType is None:
            print("No Maya-Recognized language found.")
            return

        snips = []

        if self.fileType == 'python':
            snips.append(self.file)
        else:
            snips.append('rehash; source "{0}";'.format(self.file))

        mCmd = str(self.sep.join(snips))
        if not mCmd:
            return

        print("Sending {0} file {1!r} to Maya...".format(self.fileType, mCmd[:200]))

        if self.fileType == 'python':
            # We need to wrap our source string into a template
            # so that it gets executed properly on the Maya side
            mCmd = self.PY_CMD_TEMPLATE.format(self.execType, mCmd, self.file)
            print mCmd
        c = None

        try:
            c = Telnet(
                self._settings.get('host'),
                int(self._settings.get('port')),
                timeout=3)

            c.write(mCmd.encode(encoding='UTF-8'))
        except Exception:
            e = sys.exc_info()[1]
            err = str(e)
            print("Failed to communicate with Maya (%(host)s:%(port)s)):\n%(err)s" % locals())
            raise
        else:
            time.sleep(.1)
        finally:
            if c is not None:
                c.close()

s = SendToMaya()
s.run()
