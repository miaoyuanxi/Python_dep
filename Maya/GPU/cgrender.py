# ! /usr/bin/env python
# coding=utf-8
import argparse
import os
import subprocess
import _subprocess
import pprint
import sys
import shutil
import filecmp
import time
import re
import json
import math

currentPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')
currentPath = currentPath.lower()
if "user" in currentPath:
    function_path = os.path.join(currentPath.split('user')[0],"function")
    script_path = os.path.join(currentPath.split('user')[0], "script")
    sys.path.append(function_path)
    sys.path.append(script_path)
    import RayvisionPluginsLoader
else:
    function_path = currentPath.replace("process","function")
    script_path = currentPath.replace("process","script")
    sys.path.append(function_path)
    sys.path.append(script_path)
    import RayvisionPluginsLoader


class Maya(object):
    def __init__(self):

        currentPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')
        currentPath = currentPath.lower()
        if "user" in currentPath:
            process_path = os.path.join(currentPath.split('user')[0], "process")
            function_path = os.path.join(currentPath.split('user')[0], "function")
            script_path = os.path.join(currentPath.split('user')[0], "script")

        else:
            process_path = currentPath
            function_path = currentPath.replace("process", "function")
            script_path = currentPath.replace("process", "script")

        self.info_json = os.path.join(process_path, 'info.json')
        print "json_path : %s" % self.info_json



    def get_platfom(self, platform):
        platform = str(platform)
        info_dict = {}
        with open(self.info_json, 'r') as fn:
            fn_dict = json.load(fn)
            info_dict = fn_dict[platform]
        info_dict["auto_plugins"] = info_dict["auto_plugins"].replace("/", "\\")
        return info_dict

    def get_json(self,**kwargs):
        options = {"common": {},
                   "renderSettings": {},
                   "mappings": {},
                   "mount": {},
                   "variables": {},
                   "platform": {},
                   "server": {}}

        options["common"]["debug"] = kwargs["debug"]
        options["common"]["tmp"] = "%s/%s" % (os.environ["tmp"], kwargs["task_id"])
        if not os.path.exists(options["common"]["tmp"]):
            os.makedirs(options["common"]["tmp"])

        if kwargs["json"]:
            if os.path.exists(kwargs["json"]):
                options_json = eval(open(kwargs["json"]).read())
                for i in options_json:
                    options[i] = options_json[i]

                options["renderSettings"]["cg_file"] = options["common"]["cgFile"]

                options["renderSettings"]["start"] = kwargs["start"]
                options["renderSettings"]["end"] = kwargs["end"]
                options["renderSettings"]["by"] = kwargs["by"]

                options["renderSettings"]["tiles"] = kwargs.setdefault("tiles", 1)
                options["renderSettings"]["tile_index"] = kwargs.setdefault("tile_index", 0)

                options["common"]["debug"] = kwargs["debug"]
                options["common"]["tmp"] = "%s/%s" % (os.environ["tmp"],
                                                      options["common"]["taskId"])
                if not os.path.exists(options["common"]["tmp"]):
                    os.makedirs(options["common"]["tmp"])

                options["common"]["plugin_file"] = kwargs["plugin_file"]

                if os.path.exists(options["common"]["plugin_file"]):
                    options["plugins"] = eval(open(options["common"]["plugin_file"]).read())
                else:
                    options["plugins"] = {}

                options["platform"] = self.get_platfom(kwargs["platform"])
                if kwargs["storage_path"]:
                    options["platform"]["storage_path"] = kwargs["storage_path"]

                if options["common"]["userId"] in [1811926]:
                    options["common"]["plugin_file"] = None

                return options
            else:
                raise Exception("Can not find the json file: %s." % kwargs["json"])

        if kwargs["task_id"]:
            options["platform"] = self.get_platfom(kwargs["platform"])
            options["renderSettings"]["start"] = kwargs["start"]
            options["renderSettings"]["end"] = kwargs["end"]
            options["renderSettings"]["by"] = kwargs["by"]

            cfg_path = "%s/%s/%s" % (options["platform"]["cfg_path"],
                                     kwargs["task_id"], "temp")

            options["platform"]["cfg_path"] = cfg_path

            cfg_file = "%s/%s" % (cfg_path, "render.cfg")

            server_info = eval(open(os.path.join(cfg_path, "server.cfg")).read())

            result = {}
            with open(os.path.join(cfg_path, "render.cfg"), "r") as f:
                while 1:
                    line = f.readline()
                    if "=" in line:
                        line_split = line.split("=")
                        result[line_split[0].strip()] = line_split[1].strip()
                    if ">>" in line:
                        break
                cfg_info = result

            options["common"]["submitFrom"] = "client"
            options["common"]["cgv"] = int(server_info["maya_version"])
            options["common"]["cgFile"] = server_info["maya_file"]
            options["common"]["cgSoftName"] = cfg_info["cgSoftName"]
            options["common"]["userId"] = int(server_info["user_id"])
            options["common"]["taskId"] = int(server_info["task_id"])
            options["common"]["projectId"] = int(cfg_info["projectId"])
            options["common"]["projectSymbol"] = cfg_info["projectSymbol"]

            options["renderSettings"]["renderType"] = "render.exe"
            options["renderSettings"]["renderableCamera"] = cfg_info["renderableCamera"]
            options["renderSettings"]["projectPath"] = server_info["project"]

            options["server"] = server_info
            for i in options["server"]["variables"]:
                options["variables"][i] = options["server"]["variables"][i]

            cfg_info["mountFrom"] = eval(cfg_info["mountFrom"])

            if kwargs["storage_path"]:
                kwargs["storage_path"] = kwargs["storage_path"].replace("\\", "/")
                options["platform"]["home_path"] = re.findall(r'(.+?)/\d+/',
                                                              kwargs["storage_path"], re.I)[0]

            sys.stdout.flush()
            print "storage path is: " + options["platform"]["home_path"]
            sys.stdout.flush()

            for i in cfg_info["mountFrom"]:
                options["mount"][cfg_info["mountFrom"][i]] = options["platform"]["home_path"] + i

            options["mappings"] = server_info["mappings"]

            options["common"]["plugin_file"] = os.path.join(cfg_path,
                "plugins.cfg")

            if options["common"]["userId"] in [100001, 963493, 963494,
                963495, 963336, 962796,  963496, 120151, 963433, 1811926]:
                options["common"]["plugin_file"] = None

            return options



class RvOs(object):
    is_win = 0
    is_linux = 0
    is_mac = 0

    if sys.platform.startswith("win"):
        os_type = "win"
        is_win = 1
        #add search path for wmic.exe
        os.environ["path"] += ";C:/WINDOWS/system32/wbem"
    elif sys.platform.startswith("linux"):
        os_type = "linux"
        is_linux = 1
    else:
        os_type = "mac"
        is_mac = 1

    @staticmethod
    def get_windows_mapping():
        if RvOs.is_win:
            networks = {}
            locals = []
            for i in RvOs.run_command('wmic logicaldisk get deviceid,drivetype,providername'):
                if i.strip():
                    info = i.split()
                    if info[1] == "4":
                        networks[info[0]] = info[2].replace("\\", "/")
                    elif info[1] == "3":
                        locals.append(info[0])

        return (locals, networks)

    @staticmethod
    def get_virtual_drive():
        if RvOs.is_win:
            return dict([i.strip().split("\\: =>")
                for i in RvOs.run_command('subst') if i.strip()])

    @staticmethod
    def run_command(cmd):
        if RvOs.is_win:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = _subprocess.SW_HIDE
            shell = 0
        else:
            startupinfo = None
            shell = 1

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, startupinfo=startupinfo,
                             shell=shell)

        while 1:
            # returns None while subprocess is running
            return_code = p.poll()
            if return_code == 0:
                break
            # elif return_code == 1:
            #     raise Exception(cmd + " was terminated for some reason.")
            elif return_code is not None:
                print "exit return code is: " + str(return_code)
                break
                # raise Exception(cmd + " was crashed for some reason.")
            line = p.stdout.readline()
            yield line

    @staticmethod
    def get_process_list(name):
        process_list = []
        for i in RvOs.run_command("wmic process where Caption=\"%s\" get processid" % (name)):
            if i.strip() and i.strip().isdigit():
                process_list.append(int(i.strip()))

        return process_list

    @staticmethod
    def get_all_child():
        parent_id = str(os.getpid())
        child = {}
        for i in RvOs.run_command('wmic process get Caption,ParentProcessId,ProcessId'):
            if i.strip():
                info = i.split()
                if info[1] == parent_id:
                    if info[0] != "WMIC.exe":
                        child[info[0]] = int(info[2])

        return child

    @staticmethod
    def kill_children():
        for i in RvOs.get_all_child().values():
            #os.kill is Available from python2.7, need another method.
#            os.kill(i, 9)
            if RvOs.is_win:
                os.system("taskkill /f /t /pid %s" % (i))

    @staticmethod
    def timeout_command(command, timeout):
        if RvOs.is_win:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = _subprocess.SW_HIDE

        start = time.time()
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        while process.poll() is None:
#            print "return: " + str(process.poll())
            time.sleep(0.1)
            now = time.time()
            if (now - start) > timeout:
#                os.kill(process.pid, 9)
                if RvOs.is_win:
                    os.system("taskkill /f /t /pid %s" % (process.pid))

                return None
        return process.poll()

    @staticmethod
    def call_command(cmd, shell=0):
        return subprocess.call(cmd, shell=shell)


class Zip7(object):

    def __init__(self, exe):
        self.exe = exe

    def compress(self, src):
        zip_file = os.path.splitext(src)[0] + ".7z"

        if self.is_same(zip_file, src):
            print_info("compressed file %s exists, skip compress" % (zip_file))
            result = 1
        else:
            print_info("compressing %s to %s" % (src, zip_file))

            cmd = "\"%s\" a \"%s\" \"%s\" -mx3 -ssw" % (self.exe,
                zip_file, src)

            result = 0
            for line in RvOs.run_command(cmd):
                if line.strip() == "Everything is Ok":
                    result = 1

        if result:
            return zip_file
        else:
            return src

    def decompress(self, zip_file, mark_path):
        zip_info = self.get_zip_info(zip_file)

        out = os.path.dirname(zip_file)
        src = os.path.join(out, zip_info["Path"])

        decompress_ok = "%s/%s" % (mark_path, "decompress_ok")
        start_decompress = "%s/%s" % (mark_path, "start_decompress")

        if os.path.exists(start_decompress):
            while 1:
                if os.path.exists(decompress_ok):
                    print "%s is already exists, skip decopress" % (src)
                    return src

                print "Waiting for decompress..."
                time.sleep(1)
        else:
            with open(start_decompress, "w") as f:
                ''

            try:
                print "decopress %s from %s" % (src, zip_file)
                cmd = "\"%s\" e \"%s\" -o\"%s\" -y" % (self.exe, zip_file, out)
                print cmd
                result = 0
                for line in RvOs.run_command(cmd):
                    if line.strip() == "Everything is Ok":
                        result = 1

                if result:
                    with open(decompress_ok, "w") as f:
                        ''
                    return src
                else:
                    os.remove(start_decompress)

            except:
                print "Catch except when decompress, delete %s" % (start_decompress)
                os.remove(start_decompress)

    def try_decompress(self, zip_file, retry=3):
        if retry == 0:
            return None
        else:
            try:
                print "try decompress %s time" % (4-retry)
                return self.decompress(zip_file)
            except:
                return self.try_decompress(zip_file, retry-1)

    def get_zip_info(self, zip_file):
        {'Attributes': 'A',
         'Block': '0',
         'Blocks': '1',
         'CRC': '836CB95D',
         'Encrypted': '-',
         'Headers Size': '138',
         'Method': 'LZMA2:20',
         'Modified': '2015-03-28 15:59:26',
         'Packed Size': '29191866',
         'Path': 'M02_P04_S046.mb',
         'Physical Size': '29192004',
         'Size': '138382876',
         'Solid': '-',
         'Type': '7z'}

        cmd = "\"%s\" l -slt \"%s\"" % (self.exe, zip_file)
        result = {}
        for line in RvOs.run_command(cmd):
            if "=" in line:
                line_split = [i.strip() for i in line.strip().split("=")]
                result[line_split[0]] = line_split[1]

        return result


    def is_same(self, zip_file, src):
        if os.path.exists(zip_file) and os.path.exists(src):
            zip_info = self.get_zip_info(zip_file)

            z_time = zip_info["Modified"]
            z_size = zip_info["Size"]

            f_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                   time.localtime(os.path.getmtime(src)))
            f_size = str(os.path.getsize(src))

            if z_time == f_time and z_size == f_size:
                return 1


class FileSequence():

    NUMBER_PATTERN = re.compile("([0-9]+)")
    PADDING_PATTERN = re.compile("(#+)")

    def __init__(self, path = "", head = "", tail = "", start = 0,
                        end = 0, padding = 0, missing=[]):
        self.path = path.replace("\\", "/")
        self.head = head
        self.tail = tail
        self.start = start
        self.end = end
        self.padding = padding
        self.missing = missing

    def __repr__(self):
        if not self.missing:
#            bb.###.jpg 1-6
            return self.path + "/" + "".join([self.head, self.padding*"#",
                self.tail, " ", str(self.start), "-", str(self.end)])
        else:
#            bb.###.jpg 1-6 (1-3 5-6 mising 4)
            return self.path + "/" + "".join([self.head, self.padding*"#",
                self.tail, " ", str(self.start), "-", str(self.end),
                " ( missing ",
                ",".join([str(i) for i in self.missing]),
                " ) "])

    def __iter__(self):
        def filesequence_iter_generator():
            for frame in range(self.start, self.end+1):
                if frame not in self.missing:
                    yield "".join([self.head, str(frame).zfill(self.padding),
                                   self.tail])
        return filesequence_iter_generator()

    def get_frame_file(self, frame):
        return "".join([self.path, "/", self.head,
                        str(frame).zfill(self.padding), self.tail])

    @classmethod
    def get_from_string(cls, string):
        print string
        re_missing = re.findall("\(missing (.+)\)", string, re.I)
        missing = []
        if re_missing:
            missing = [int(i) for i in re_missing[0].split(",")]

        re_sequence = re.findall("(.+) (\d+-\d+)", string, re.I)
        start, end = [int(i) for i in re_sequence[0][1].split("-")]
        base, tail = os.path.splitext(re_sequence[0][0])
        padding = base.count("#")
        head = os.path.basename(base).split("#")[0]
        path = os.path.dirname(base)
        return FileSequence(path, head, tail, start, end, padding, missing)

    @property
    def name(self):
        return str(self)

    @property
    def fileName(self):
        return os.path.join(self.path, str(self))

    @property
    def readName(self):
        return os.path.join(self.path, "".join([self.head, self.padding*"#", self.tail]))

    @property
    def startFileName(self):
        baseName = "".join([self.head, str(self.start).zfill(self.padding),
                                   self.tail])
        return os.path.join(self.path, baseName)

    @property
    def frames(self):
        return self.end - self.start + 1 - len(self.missing)

    @property
    def frameinfo(self):
        return [frame for frame in range(self.start, self.end+1)
                if frame not in self.missing]

    @property
    def ext(self):
        return self.tail.split('.')[-1].lower()

    @property
    def files(self):
        for filename in iter(self):
            yield os.path.join(self.path, filename)

    @property
    def badframes(self):
        return [frame for frame in range(self.start, self.end+1)
                if frame not in self.missing
                if os.path.getsize(os.path.join(self.path,
                 "".join([self.head, str(frame).zfill(self.padding),
                self.tail]))) < 2000]

    @property
    def blackFrames(self):
        if self.ext in ["tif", "tiff"]:
            blackSize = 129852L
        elif self.ext == "exr":
            blackSize = 320811L
        else:
            blackSize = 0

        if blackSize:
            black = [   frame
                        for frame in range(self.start, self.end+1)
                        if frame not in self.missing
                        if os.path.getsize(os.path.join(self.path,
                         "".join([self.head, str(frame).zfill(self.padding),
                                self.tail]))) == blackSize
                    ]

            if len(black) == self.frames:
                return black
            else:
                if self.start in black:
                    mark = self.start
                    for i in range(self.start, self.end+1):
                        if mark in black:
                            black.remove(mark)
                            mark += 1

                if self.end in black:
                    mark = self.end
                    for i in range(self.start, self.end+1):
                        if mark in black:
                            black.remove(mark)
                            mark -= 1

                return black
        else:
            return []

    @classmethod
    def single_frame_format(cls, single_frame):
        base = os.path.basename(single_frame)
        number = re.findall(r'(0+\d+)', base, re.I)[0]

        single_frame2 = single_frame.replace(number, str(int(number)+1).zfill(len(number)))
        seq, others = FileSequence.find([single_frame, single_frame2])

        return FileSequence(seq[0].path, seq[0].head, seq[0].tail,
                            seq[0].start, seq[0].end-1, seq[0].padding,
                            seq[0].missing)

    @classmethod
    def recursive_find(cls, search_path, sequence=[], ext=None,
        actual_frange=None):
        if os.path.isdir(search_path):
            sequences, others = cls.find(search_path, ext, actual_frange)
            for i in others:
                if os.path.isdir(os.path.join(search_path, i)):
                    sequences += cls.recursive_find(os.path.join(search_path,
                        i), sequences, ext, actual_frange)

        return sequences

    @classmethod
    def find(cls, search_path, ext=None, actual_frange=None):
        mySequence, others = [], []
        if isinstance(search_path, list):
            files = sorted([os.path.basename(i) for i in search_path])
            path = None

        elif os.path.isdir(search_path):
            files = sorted([i for i in os.listdir(search_path)])
            path = search_path

        if files:
#direcotiry add to others, one call of isfile spend 0.001s.
#                            if os.path.isfile(os.path.join(search_path, i))])
            sequences, others = cls.find_in_list(files)
            for i in sequences:
                padding = len(cls.PADDING_PATTERN.findall(i)[0])
                head, tail = i.split(padding*"#")
                start = sequences[i][0]
                end = sequences[i][-1]

                if actual_frange:
                    missing = [frame for frame in Frames(actual_frange)
                                if frame not in sequences[i]]
                else:
                    missing = [frame for frame in range(start, end+1)
                                if frame not in sequences[i]]

                missing = sorted([i for i in set(missing)])

                start_file = head + str(start).zfill(padding) + tail
                if not path:
                    for path_i in search_path:
                        if start_file in path_i:
                            path = os.path.dirname(path_i)
                            break

                if not path:
                    path = os.path.dirname(search_path[0])

                mySequence.append(FileSequence(path, head, tail, start,
                                    end, padding, missing))

        if ext:
            return [i for i in mySequence if i.ext==ext], others
        else:
            return mySequence, others

    @classmethod
    def find_in_list(cls, files):
        sequence = {}
        others = []
        temp = []

        for index, file in enumerate(files):
            if index != len(files)-1:
                isSequence = cls.getSequences(file, files[index+1])
                if isSequence:
                    sequence[isSequence[0]] = sequence.setdefault(isSequence[0],
                                                        []) + isSequence[1:3]

                    temp += [file, files[index+1]]
                else:
                    others.append(file)
            else:
                others.append(file)


        for i in sequence:
            sequence[i] = sorted(list(set(sequence[i])))
        others = [i for i in others if i not in temp if i.lower() != "thumbs.db"]

        return sequence, others

    @classmethod
    def getSequences(cls, file1, file2):
        components = [i for i in cls.NUMBER_PATTERN.split(file1) if i]
        numberIndex = dict([(index, i) for index, i in enumerate(components)
                            if cls.NUMBER_PATTERN.findall(i)])

        for i in sorted(numberIndex.keys(), reverse=1):
            r = re.findall(r'^(%s)(\d{%s})(%s)$' % ("".join(components[:i]),
                            len(numberIndex[i]), "".join(components[i+1:])),
                            file2)
            if r:
                return ["".join([r[0][0], len(r[0][1])*"#", r[0][2]]),
                        int(numberIndex[i]), int(r[0][1])]


class Render(dict, Zip7, RvOs):

    def __init__(self, options):
        for i in options:
            self[i] = options[i]

        self.check_mapping()
        self.check_7z()
        # self.check_sweeper()

    def check_sweeper(self):
        processes = RvOs.get_process_list("sweeper.exe")
        if processes:
            print "sweeper is running."
            sys.stdout.flush()
            print processes
            sys.stdout.flush()
        else:
            print "start sweeper."
            cmd = "start %s" % (r"C:\sweeper\sweeper.exe")
            print "cmd: " + cmd
            RvOs.call_command(cmd, shell=1)
            processes = RvOs.get_process_list("sweeper.exe")
            sys.stdout.flush()
            print processes
            sys.stdout.flush()

    def check_mapping(self):
        if self["common"]["submitFrom"] == "client":
            self.clean_network()
            self.mapping_network()
            self.mapping_plugins()

    def check_7z(self):
        if self["common"]["cgFile"].endswith(".rayvision"):
            print "Found 7z file: %s" % (self["common"]["cgFile"])
            Zip7.__init__(self, self["platform"]["7z.exe"])

            result = self.decompress(self["common"]["cgFile"],
                self["platform"]["cfg_path"])
            if result:
                self["common"]["cgFile"] = result
            else:
                raise Exception("decompress error %s" % \
                (self["common"]["cgFile"]))

    def run_command(self, command):
        #weird bug, don't know why
#        return subprocess.call(command, shell=1)
        if self.is_win:
            return subprocess.call(command)
        if self.is_linux:
            return subprocess.call(command, shell=1)

    def clean_network(self):
        # if self.run_command("net use * /delete /y"):
            # print "clean mapping network failed."
        if self.is_win:
            # print "clean mapping network successfully."
            for j in range(3):
                if self.run_command("net use * /delete /y"):
                    print "clean mapping network failed."
                    time.sleep(5)
                    print "Wait 5 seconds..."
                else:
                    print "clean mapping network successfully."
                    break
        
        
            sys.stdout.flush()

            self.clean_virtual_drive()

        if self.is_linux:
            if self.run_command("mount | grep -v '/mnt_rayvision' | awk '/cifs/ {print $3} ' | xargs umount"):
                print "clean mapping network failed."
                time.sleep(5)
                print "Wait 5 seconds..."
            else:
                print "clean mapping network successfully."

        sys.stdout.flush()

        # if self["platform"]["platform"] == 1005:
        #     self.clean_vcfs()

    def clean_vcfs(self):
        print "clean vcfs"
        cmd = r"c:\vcfsclient\vcfstask stop"
        print cmd
        sys.stdout.flush()
        self.run_command(cmd)
        sys.stdout.flush()

    def clean_virtual_drive(self, max=60):
        virtual_drive = RvOs.get_virtual_drive()
        if max == 0:
            print "clean virtual_drive failed"
            pprint.pprint(virtual_drive)
            sys.stdout.flush()
            return 0
        else:
            for i in virtual_drive:
                if self.run_command("subst %s /d" % (i)):
                    print "clean virtual drive failed: %s => %s" % (i,
                        virtual_drive[i])
                    sys.stdout.flush()
                else:
                    print "clean virtual drive successfully: %s => %s" % (i,
                        virtual_drive[i])
                    sys.stdout.flush()

            virtual_drive = RvOs.get_virtual_drive()
            if virtual_drive:
                time.sleep(1)
                print "wait 1 second and try remove subst again"
                sys.stdout.flush()
                self.clean_virtual_drive(max - 1)
            else:
                print "clean virtual_drive success"
                sys.stdout.flush()

    def create_virtua_drive(self, virtual_drive, path, max=60):
        if max == 0:
            print "can not create virutal drive: %s => %s" % (virtual_drive,
                path)
            sys.stdout.flush()
            return 0
        else:
            self.run_command("subst %s %s" % (virtual_drive, path))
            sys.stdout.flush()
            if os.path.exists(virtual_drive + "/"):
                print "create virutal drive: %s => %s" % (virtual_drive,
                    path)
                print virtual_drive + "/" + " is exists"
                sys.stdout.flush()
            else:
                time.sleep(1)
                print "wait 1 second and try subst again"
                sys.stdout.flush()
                self.create_virtua_drive(virtual_drive, path, max-1)

    def mapping_network(self):
        for i in self["mount"]:
            if i == "vcfs":
                cmd = r"c:\vcfsclient\vcfstask start /path=c:\vcfsclient " \
                    "/conf=vcfs.conf /log=opt_result.log " \
                    "/letter=%s" % (self["mount"][i].strip(":").lower())
                print cmd

                sys.stdout.flush()
                if self.run_command(cmd):
                    sys.stdout.flush()
                    print "can not start vcfs %s" % (self["mount"][i])
                    sys.stdout.flush()
                # else:
                #     mark = 120
                #     while 1:
                #         if os.path.exists(self["mount"][i]):
                #             print self["mount"][i] + " is exist"
                #             print "start vcfs %s" % (self["mount"][i])
                #             sys.stdout.flush()
                #             break
                #         else:
                #             if mark == 0:
                #                 break
                #             else:
                #                 print self["mount"][i] + " is not exist"
                #                 mark -= 1
                #                 time.sleep(1)
                #                 print "waiting 1 second for vcfs"
                #                 sys.stdout.flush()

            else:
                #on windows, we must use '\' slash when mount, not '/'
                path = self["mount"][i].replace("/", "\\")
                if path.startswith("\\"):
                    if self.run_command("net use %s %s" % (i, path)):
                        print "can not mapping %s to %s" % (i, path)
                    else:
                        print "Mapping %s to %s" % (i, path)
                else:
                    self.create_virtua_drive(i, path)

                sys.stdout.flush()

        self.run_command("net use")
        self.run_command("subst")

    def mapping_plugins(self):
        drive = "B:"
        auto_plugins = self["platform"]["auto_plugins"]
        if self.run_command("net use %s %s" % (drive, auto_plugins)):
            print "can not mapping %s to %s" % (drive, auto_plugins)
        else:
            print "Mapping %s to %s" % (drive, auto_plugins)

    def copytree(self, src, dst):
        if not os.path.exists(dst):
            os.makedirs(dst)

        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)

            if os.path.isdir(s):
                self.copytree(s, d)
            else:
                if os.path.exists(d):
                    if filecmp.cmp(s, d):
                        print "%s already exists, skip" % (d)
                    else:
                        print "copy %s to %s" % (s, d)
                        shutil.copy2(s, d)

                else:
                    print "copy %s to %s" % (s, d)
                    shutil.copy2(s, d)

    def copytree2(self, src, dst):
        if not os.path.exists(dst):
            os.makedirs(dst)

        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)

            if os.path.isdir(s):
                self.copytree2(s, d)
            else:
                print "copy %s to %s" % (s, d)
                shutil.copy2(s, d)


class MayaBatch(Render):

    def __init__(self, options):
        ''


class MayaGui(Render):

    def __init__(self, options):
        ''


class ArnoldClass(Render):

    def __init__(self, options):
        super(ArnoldClass, self).__init__(options)
        self.get_arnold_info()
        self.set_plugins()
        # self.get_arnold_version(self["common"]["cgFile"].startFileName)

    def get_arnold_info(self):
        self["renderSettings"]["output"] = "c:/work/render/%s/output/" % \
                                            (self["common"]["taskId"])
        if not os.path.exists(self["renderSettings"]["output"]):
            os.makedirs(self["renderSettings"]["output"])

        self["common"]["cgFile"] = FileSequence.get_from_string(self["common"]["cgFile"])

    def set_plugins(self):
        sys.stdout.flush()
        custom_file = None
        if self["platform"]["custom_config"]:
            custom_file = self["platform"]["custom_config"] + "/" + \
                str(self["common"]["userId"]) + "/ass.json"
            print "custom_config is: " + custom_file
        if os.path.exists(custom_file):
            print "custom_config is: " + custom_file
            plugin_info = json.load(open(custom_file, "r"))
        if self["common"]["userId"] in [119768,1841236]:
            os.system(r'wmic process where name="JGS_mtoa_licserver.exe" delete')
            os.system(r'wmic process where name="rlm.exe" delete')
            srcDir=r"B:\plugins\maya\mtoa\maya2017\mtoa_1.3.0.0\AMPED"
            dstDir=r'"C:\AMPED"'
            os.system ("robocopy /s  %s %s" % (srcDir, dstDir))
            os.environ['solidangle_LICENSE'] = r'5053@localhost'
            os.system(r'start C:\AMPED\rlm.exe')
            plugin_info = {"kick.exe": "B:/custom_config/1841236/mtoa_1.3.0.0/maya_mtoa/bin/kick.exe",
                           "args": {"-l": "B:/custom_config/1841236/mtoa_1.3.0.0/maya_mtoa/shaders",
                                    "-g": 2.2,
                                    "-v": 6,
                                    "-t": 0
                                    }
                           }
        else:
            print "custom_config is not exists, use default settings."
            plugin_info = {"kick.exe": "//10.50.1.22/td/custom_config/1811805/1.2.3.1/2014/bin/kick.exe",
                           "args": {"-l": "//10.50.1.22/td/custom_config/1811805/1.2.3.1/2014/shaders",
                                    "-g": 2.2,
                                    "-v": 2,
                                    "-t": 0
                                    }
                           }
        self["renderSettings"]["kick.exe"] = plugin_info["kick.exe"]
        self["renderSettings"]["args"] = plugin_info["args"]

        sys.stdout.flush()

    def get_arnold_version(self, ass):
        result = {"arnold_version": None,
                  "sys": None,
                  "host_app": None,
                  "host_version": None,
                  "software": None,
                  "software_version": None}

        if os.path.exists(ass):
            with open(ass, "r") as f:
                while 1:
                    line = f.readline()
                    if line.startswith("### from"):
                        result["arnold_version"], result["sys"] = line.split()[3:5]
                        continue
                    if line.startswith("### host app"):
                        line_split = line.split()
                        result["host_app"] = line_split[3]
                        result["host_version"] = line_split[4]
                        result["software"] = line_split[-3]
                        result["software_version"] = " ".join(line_split[-2:])
                        break

        return result

    def get_ass_file(self, frame):
        return self["common"]["cgFile"].get_frame_file(frame)


class ArnoldKick(ArnoldClass):

    def __init__(self, options):
        super(ArnoldKick, self).__init__(options)

    def render(self):
        print "start Arnold kick process..."
        sys.stdout.flush()

        for i in range(int(self["renderSettings"]["start"]),
                       int(self["renderSettings"]["end"]) + 1):
            print "start to render frame: " + str(i)
            sys.stdout.flush()
            self.render_frame(i)

    def render_frame(self, frame):
        input = self.get_ass_file(frame)
        output = os.path.join(self["renderSettings"]["output"],
                              os.path.basename(input.replace(".ass", ".exr")))

        cmd = "\"%s\" -nstdin -dw -dp -nocrashpopup %s -i \"%s\" -o \"%s\"" % \
              (self["renderSettings"]["kick.exe"],
               " ".join([i + " " + str(self["renderSettings"]["args"][i])
                         for i in self["renderSettings"]["args"]]),

               input, output)

        print "Info: Run render ass file command:"
        print cmd
        sys.stdout.flush()

        images = []
        RE_ALL = re.compile(r'writing.+file `?(.+?)[ \']')
        for line in RvOs.run_command(cmd):
            if line.strip():
                print line.strip()
                sys.stdout.flush()
                if "Arnold shutdown" in line:
                    break
                elif RE_ALL.findall(line, re.I):
                    images.append(RE_ALL.findall(line, re.I)[0])
                elif re.findall(r'.+driver_exr.+Cannot open image file',
                                line, re.I):
                    RvOs.kill_children()
                    raise Exception("Can't find output image path")
                elif "[kick] Can't read input file" in line:
                    RvOs.kill_children()
                    raise Exception("Can't read input ass file")
                elif "[ass] can't open" in line:
                    RvOs.kill_children()
                    raise Exception("Can't open input ass file")
                elif re.findall(r'node \".+\" is not installed', line, re.I):
                    RvOs.kill_children()
                    raise Exception("Node not installed error")

#                elif "[texturesys] Could not open file" in line:
#                    kill_all()
#                    raise Exception("Can't read sourceimage file")

#        for i in images:
#            self.copy_file(i)

class Nuke(Render):

    def __init__(self, options):
        Render.__init__(self, options)


class NukeMerge(Nuke):

    def __init__(self, options):
        Nuke.__init__(self, options)
        self.get_input_output()

    def get_input_output(self):
        tile_path = "%s/tiles/%s/%s" % (self["platform"]["storage_path"],
                                        self["common"]["taskId"],
                                        self["renderSettings"]["start"])
        tile_path = tile_path.replace("\\", "/")

        all_files = []
        for root, dirs, files in os.walk(tile_path+"/0"):
            for i_file in files:
                ignore = 0
                for ignore_file in [".db"]:
                    if i_file.lower().endswith(ignore_file):
                        ignore = 1
                if not ignore:
                    all_files.append(os.path.join(root, i_file))

        self.tile_files = [[re.sub(r'(.+/tiles/\d+/\d+)(/0/)(.+)', r"\1/%s/\3" % (index), i.replace("\\", "/"))
                            for index in range(self["renderSettings"]["tiles"])]
                           for i in all_files]

        self.tile_files = [[self.get_right_file_name(j) for j in i]
                           for i in self.tile_files]

        self["renderSettings"]["output"] = "c:/work/render/%s/output/" % \
            (self["common"]["taskId"])

    def render(self):
        if self["common"]["debug"]:
            print "json info:"
            pprint.pprint(self)
        print self.tile_files
        for i in self.tile_files:
            if self["common"]["debug"]:
                print i
            print i
            tile_output = self["renderSettings"]["output"] + re.sub(r'(.+/tiles/\d+/\d+)(/0/)(.+)', r"\3", i[0])
                     
            
         
            tile_folder = os.path.dirname(tile_output)
            tile_output = tile_folder + '/' + os.path.basename(tile_output)
            print tile_output
            # print "9999999999999999999"
            if not os.path.exists(tile_folder):
                os.makedirs(tile_folder)

            
            self.merge_files(self["renderSettings"]["tiles"], i, tile_output)

    def merge_files(self, tiles, input_files, tile_output):
        #nuke_exe = r"B:\nuke\Nuke5.1v5\Nuke5.1.exe"
        os.environ['foundry_LICENSE'] = r'4101@10.60.5.248'
        nuke_exe = r"B:\nuke\Nuke10.5v5\Nuke10.5.exe"
        merge_images = os.path.join(os.path.dirname(__file__), "merge_images_new.py")
        cmd = "\"%s\" -t \"%s\" -tiles %s -width %s -height %s" \
              " -tile_files \"%s\" -tile_output \"%s\" " % (nuke_exe, merge_images,
                                                    tiles,
                                                    self["renderSettings"]["width"],
                                                    self["renderSettings"]["height"],
                                                    input_files, tile_output)

        print cmd

        #is_complete = 0
        #re_complete = re.compile(r'Scene.+completed\.$', re.I)
        for line in RvOs.run_command(cmd):
            line_str = line.strip()
            if line_str:
                print line_str

                # if re_complete.findall(line_str):
                    # is_complete = 1

                    # if not is_complete:
                        # exit(1)

    def get_right_file_name(self, file_name):
        r = re.findall(r'.+(\.\d+$)', file_name, re.I)
        if r:
            dirname = os.path.dirname(file_name)
            basename = os.path.basename(file_name)
            basename = r[0].lstrip(".") + "." + basename.replace(r[0], "")
            right_file_name = os.path.join(dirname, basename)
            shutil.copy2(file_name, right_file_name)
            return right_file_name
        else:
            return file_name


class MayaClass(Render):

    def __init__(self, options):
        Render.__init__(self, options)
        self.get_maya_info()
        self.create_setup_file()
        self.set_variables()
        self.set_plugins()

    def get_maya_info(self):
        self["renderSettings"]["maya_file"] = self["common"]["cgFile"]

        if self.is_win:
            self["renderSettings"]["render.exe"] = "C:/Program Files/Autodesk/" \
                "maya%s/bin/render.exe" % (self["common"]["cgv"])
            self["renderSettings"]["mayabatch.exe"] = "C:/Program Files/Autodesk/" \
                "maya%s/bin/mayabatch.exe" % (self["common"]["cgv"])
            self["renderSettings"]["output"] = "c:/work/render/%s/output/" % \
                (self["common"]["taskId"])
        if self.is_linux:
            if float(self["common"]["cgv"]) < 2016:
                version_name = "%s-x64" % (self["common"]["cgv"])
            else:
                version_name = self["common"]["cgv"]

            self["renderSettings"]["render.exe"] = "/usr/autodesk/" \
                "maya%s/bin/Render" % (version_name)
            self["renderSettings"]["mayabatch.exe"] = "/usr/autodesk/" \
                "maya%s/bin/maya -batch" % (version_name)
            self["renderSettings"]["output"] = "/tmp/nzs-data/work/render/%s/output/" % \
                (self["common"]["taskId"])
            self["common"]["tmp"] = "%s/%s" % ("/tmp",
                                                  self["common"]["taskId"])
            if not os.path.exists(self["common"]["tmp"]):
                os.makedirs(self["common"]["tmp"])

        if not os.path.exists(self["renderSettings"]["output"]):
            os.makedirs(self["renderSettings"]["output"])

    def get_region(self, tiles, tile_index, width, height):
        tiles = int(tiles)
        tile_index = int(tile_index)
        width = int(width)
        height = int(height)
        
        n = int(math.sqrt(tiles))
        for i in sorted(range(2, n + 1), reverse=1):
            if tiles % i != 0:
                continue
            else:
                n = i
                break

        n3 = tiles / n
        n1 = tile_index / n3
        n2 = tile_index % n3

        top = height / n * (n1 + 1)
        # top = height / n * (n1 + 1) - 1
        left = width / n3 * n2
        bottom = height / n * n1
        right = width / n3 * (n2 + 1)
        # right = width / n3 * (n2 + 1) -1

        if right == width:
            right -= 1
        if top == height:
            top -= 1

        return left, right, bottom, top
            
    def create_setup_file(self):
        if self["mappings"]:
            self["renderSettings"]["setup_file"] = "%s/usersetup.mel" % \
                (self["common"]["tmp"])

            with open(self["renderSettings"]["setup_file"], "w") as f:
                f.write("dirmap -en true;\n")
                for i in self["mappings"]:
                    if not i.startswith("$"):
                        old_path = i
                        if isinstance(old_path, unicode):
                            old_path = i.encode("gb18030")
                        f.write("dirmap -m \"%s\" \"%s\";\n" % (old_path,
                                self["mappings"][i]))

    def set_variables(self):
        if self["common"]["userId"] in [963130]:
            os.environ["IDMT_PROJECTS"] = "Z:/Projects"
        else:
            for i in self["variables"]:
                os.environ[i] = self["variables"][i]

        if self["mappings"]:
            os.environ.setdefault("MAYA_SCRIPT_PATH", "")
            if os.environ["MAYA_SCRIPT_PATH"]:
                os.environ["MAYA_SCRIPT_PATH"] += ";"
            os.environ["MAYA_SCRIPT_PATH"] += self["common"]["tmp"]

        for i in self["mappings"]:
            if i.startswith("$"):
                try:
                    variable = re.findall(r'\$\{(.+)\}', i, re.I)[0]
                    os.environ[variable] = self["mappings"][i]
                except:
                    pass

    def set_plugins(self):
        if self["common"]["plugin_file"]:
            sys.stdout.flush()
            plginLd = RayvisionPluginsLoader.RayvisionPluginsLoader()
            sys.stdout.flush()
            if self["platform"]["custom_config"]:
                custom_file = self["platform"]["custom_config"] + "/" + \
                    str(self["common"]["userId"]) + "/RayvisionCustomConfig.py"
                sys.stdout.flush()
                print "custom_config is: " + custom_file
                sys.stdout.flush()
            plginLd.RayvisionPluginsLoader(self["common"]["plugin_file"], [custom_file])
            sys.stdout.flush()


class MayaRender(MayaClass):

    def __init__(self, options):
        MayaClass.__init__(self, options)


        self.cmd_json = os.path.join(self["platform"]["py_path"],'user',str(self["common"]["userId"]),'cmd','cmd.json')
        if os.path.exists(self.cmd_json):
            print "custome cmd.json path : %s" % self.cmd_json
            self.get_cmd_json()
            for i in self.cmd_dict:
                self["renderSettings"][i] = self.cmd_dict[i]


    def get_cmd_json(self):
        with open(self.cmd_json ,'r') as fn:
            cmd_dict = json.load(fn)
        self.cmd_dict = cmd_dict
        return self.cmd_dict




    def RBcmd(self,cmdStr,continueOnErr=False,myShell=False,myLog=False):#continueOnErr=true-->not exit ; continueOnErr=false--> exit 
        print str(continueOnErr)+'--->>>'+str(myShell)
        cmdp=subprocess.Popen(cmdStr,stdin = subprocess.PIPE,stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = myShell)
        cmdp.stdin.write('3/n')
        cmdp.stdin.write('4/n')
        exitcode = 0
        while cmdp.poll()==None:
            resultLine = cmdp.stdout.readline().strip()
            if resultLine!='':
                if "License error" in resultLine or "[mtoa] Failed batch render" in resultLine or "error checking out license for arnold" in resultLine or "No license for product (-1)" in resultLine:
                    exitcode = -1
            
        resultStr = cmdp.stdout.read()
        resultCode = cmdp.returncode

        if exitcode==-1:
            sys.exit(-1)

        if not continueOnErr:
            if resultCode!=0:
                sys.exit(resultCode)
        return resultStr        
        
        
        
        
        
    def render(self):
        currentPath = os.path.split(os.path.realpath(__file__))[0].replace('\\','/')
        self["common"]['pre_render'] = currentPath 
        
        self["renderSettings"]["tile_region"] = ""
        if self["renderSettings"]["tiles"] > 1:
            tile_region = self.get_region(self["renderSettings"]["tiles"],
                                          self["renderSettings"]["tile_index"],
                                          self["renderSettings"]["width"],
                                          self["renderSettings"]["height"])
            self["renderSettings"]["tile_region"] = " ".join([str(i) for i in tile_region])
        if os.environ.has_key('gpuid'):
            self["renderSettings"]["output"] = "c:/work/render/%s/" \
            "output/%s_%s_%s/" % (self["common"]["taskId"],
                                  self["renderSettings"]["start"],
                                  self["renderSettings"]["end"],
                                  self["renderSettings"]["by"])
            
            gid = int(os.environ.get('gpuid')) - 1
            d_log = r"D:/Temp/REDSHIFT/CACHE/G{}/Log/Log.Latest.0/log.html".format(gid)
            if not os.path.exists(d_log):
                os.makedirs(os.path.dirname(d_log))
                with open(d_log,"w"):
                    ""            
                print "Creat empty Redshift log file: {}".format(d_log)
            if not os.path.exists(r"C:/ProgramData/Redshift/Log/Log.Latest.0/log.html"):
                os.makedirs(r"C:/ProgramData/Redshift/Log/Log.Latest.0")

                with open(r"C:/ProgramData/Redshift//Log/Log.Latest.0/log.html","w"):
                    "" 
        else:
            self["renderSettings"]["output"] = "c:/work/render/%s/output/%s/%s/" % \
                (self["common"]["taskId"], self["renderSettings"]["start"],
                 self["renderSettings"]["tile_index"])
    
    
        if self["common"]["debug"]:
            print "json info:"
            pprint.pprint(self)

        if float(self["common"]["cgv"])==2017:
            print "copy mayaBatchRenderProcedure.mel for maya2017 updata3 "
            os.system ("robocopy /e /ns /nc /nfl /ndl /np  \"//10.90.100.101/o5/py/model/2017updata3\"  \"C:/Program Files/Autodesk/Maya2017/scripts/others\"" )



        print "start maya render process..."
        if self["renderSettings"]["projectPath"]:
            if os.path.exists(self["renderSettings"]["projectPath"]):
                os.chdir(self["renderSettings"]["projectPath"])
                
        if self["common"]["userId"] in [1857270]:
            if float(self["common"]["cgv"])==2015:
                self["renderSettings"]["render.exe"] = "C:/Program Files/Autodesk/" \
                    "Maya2015_sp6/bin/render.exe"
                self["renderSettings"]["mayabatch.exe"] = "C:/Program Files/Autodesk/" \
                    "Maya2015_sp6/bin/mayabatch.exe"
                
        cmd = "\"%(render.exe)s\" -s %(start)s -e %(end)s -b %(by)s " \
            "-proj \"%(projectPath)s\" -rd \"%(output)s\"" \
            % self["renderSettings"]

        if self["renderSettings"]["renderableCamera"]:
            if not "," in self["renderSettings"]["renderableCamera"] and \
                not "{rayvision}" in self["renderSettings"]["renderableCamera"]:
                cmd += " -cam \"%(renderableCamera)s\"" % self["renderSettings"]

        if self["renderSettings"].get("renderableLayer"):
            if not "," in self["renderSettings"]["renderableLayer"] and \
                not "{rayvision}" in self["renderSettings"]["renderableLayer"]:
                cmd += " -rl \"%(renderableLayer)s\"" % self["renderSettings"]


        if self["common"]["userId"] in [1879546,1857270,1903427,1903427]:
            cmd += " -preRender \"python \\\"user_id=%s;mapping=%s;plugins=%s;taskid=%s;rendersetting=%s;start=%s;execfile(\\\\\\\"//10.90.100.101/o5/py/model/prerender.py\\\\\\\")\\\"\"" % (self["common"]["userId"],self["mappings"],self["plugins"]["plugins"],self["common"]["taskId"],self["renderSettings"],self["renderSettings"]["start"])
                

            
        if "redshift_GPU" in self["plugins"]["plugins"]:

            PreRender = os.path.join(self["platform"]["py_path"], 'script', 'PreRender.py').replace("\\", "/")
            pre_render_dict = {}
            pre_render_dict["mapping"] = self["mappings"]
            pre_render_dict["user_id"] = self["common"]["userId"]
            pre_render_dict["task_id"] = self["common"]["taskId"]
            pre_render_dict["start"] = self["renderSettings"]["start"]
            pre_render_dict["end"] = self["renderSettings"]["end"]
            pre_render_dict["rendersetting"] = self["renderSettings"]
            pre_render_dict["plugins"] = self["plugins"]["plugins"]
            pre_render_dict["c_prerender"] = os.path.join(self["platform"]["py_path"], 'user',
                                                          str(self["common"]["userId"]), 'prerender',
                                                          'C_PreRender.py').replace("\\", "/")

            if self["common"]["userId"] in [1866194, 1835213, 1888315, 1833958, 1844817, 1873149, 1886200, 1868563,
                                            1813649, 1859026, 961743, 1833038, 964311, 1819610, 1814856, 1848484,
                                            1848680, 963567, 1820265, 964309, 1864685, 1860992, 119768, 962371, 1821671,
                                            1854466, 1811755, 1863576, 1863884, 1863099, 1877869, 1864856, 1883450,
                                            1877965, 1846192, 1876209, 1876088, 1905390, 1909924, 1839312]:
                if self["common"]["userId"] in [961743]:
                    cmd += " -preRender \"python \\\"execfile(\\\\\\\"//10.90.100.101/o5/py/model/961743.py\\\\\\\")\\\"\" -r redshift -logLevel 1"
            else:
                # cmd += " -r redshift -logLevel 1"
                cmd += " -preRender \"python \\\"pre_render_dict=%s;execfile(\\\\\\\"%s\\\\\\\")\\\"\" -r redshift -logLevel 1 " % (pre_render_dict, PreRender)













        
            if self["common"]["userId"] in [1903427,1822731]:
                cmd += " -r redshift -logLevel 2"
            else:
                cmd += " -r redshift -logLevel 1"        

                
            if "gpuid" in os.environ:
                gpu_n= int(os.environ["gpuid"]) - 1
            else :
                gpu_n="0"             
            if self["common"]["userId"] in [1868564]:
                print "shuang ka gpu"
                gpu_n="0,1"
            gpu_n="0,1"
            if self["common"]["taskId"] in [16096461,16096462,16096463]:
                print "dan ka gpu"
                gpu_n="0"            

            # if self["common"]["userId"] in [1868563]:
                # print "dan ka gpu"
                # gpu_n="0"
            if self["common"]["taskId"] in [16076108]:
                print "dan ka gpu"
            

            
            if self["common"]["userId"] in [1840038,1846192]:
                print "dan ka gpu"
                gpu_n="0"
            cmd += " -gpu {%s}" % (gpu_n)            
        
        
            # if self["common"]["taskId"] in [16095888]:
                # print "dan ka gpu"
                # gpu_n="0"
            # cmd += " -gpu {%s}" % (gpu_n)                
            # cmd += " -gpu {0,1}"
        if self["common"]["userId"] in [1820446]:
            self["renderSettings"]["output"] += "<pass>/<scene>_<pass>" \
                                                "_<aov>_#.<ext>"
            cmd = "\"%(render.exe)s\" -r 3delight -rp all -an 1" \
                  " -s %(start)s -e %(end)s -inc %(by)s " \
                  " -proj \"%(projectPath)s\" -img \"%(output)s\"" \
                  % self["renderSettings"]

        # if int(self["common"]["taskId"]) in [5041988]:
            # cmd += " -x 10 -y 10"

            
        if "redshift_GPU" in self["plugins"]["plugins"]:        
            if self["common"]["userId"] in [1868564]:            
                if int(self.renderSettings["end"]) > int(self.renderSettings["start"]):
                    cmd += " -postFrame \"python \\\"rendersetting=%s;execfile(\\\\\\\"//10.90.100.101/o5/py/model/PostRender.py\\\\\\\")\\\";\"" % (self["renderSettings"])
                    
        if self["renderSettings"]["tile_region"]:

           if "redshift_GPU" in self["plugins"]["plugins"]:
                
                cmd += "  -reg %(tile_region)s" % self["renderSettings"]


        elif " -r " not in cmd and float(self["common"]["cgv"]) < 2017:
            cmd += " -mr:art -mr:aml"
            
            
        cmd += " \"%(maya_file)s\"" % self["renderSettings"]

        if self["common"]["userId"] == 1818936:
            pre_bat = r"\\10.50.1.22\td\clientFiles\1818936\tools_new\env.bat"
            pre_mel = os.path.splitext(self["renderSettings"]["maya_file"])[0] + ".mel"
            self["renderSettings"]["pre_mel"] = pre_mel.replace("\\", "/")
            os.environ["path"] += r";C:\Python27"
            os.environ["DONOT_OVERWRITE_FRAMERANGE"] = "1"
            print os.environ["path"]
            sys.stdout.flush()
            cmd = "eco -t rayvision_maya -r \"render.exe -s %(start)s" \
                  " -e %(end)s -b %(by)s -proj \\\"%(projectPath)s\\\"" \
                  " -rd \\\"%(output)s\\\"" \
                  " \\\"%(maya_file)s\\\"" \
                  % self["renderSettings"]

            cmd = "\"%s\" && %s" % (pre_bat, cmd)

        # if self["common"]["userId"] in [1818936]:
        #     self["renderSettings"]["ass_dir"] = r"d:\temp"
        #     if not os.path.exists(self["renderSettings"]["ass_dir"]):
        #         os.makedirs(self["renderSettings"]["ass_dir"])
        #
        #     maya_base = os.path.basename(self["renderSettings"]["maya_file"])
        #     split_ext = [os.path.splitext(maya_base)[0]]
        #     split_ext.append(str(self["renderSettings"]["start"]).zfill(4))
        #     split_ext.append("ass")
        #     self["renderSettings"]["ass_path"] = os.path.join(self["renderSettings"]["ass_dir"], ".".join(split_ext))
        #     self["renderSettings"]["image_name"] = maya_base
        #
        #     cmd1 = "Render.exe -r arnoldExport -s %(start)s -e %(end)s" \
        #            " -b %(by)s -pad 4 -x 1920 -y 1080" \
        #            " -proj \"%(projectPath)s\" -rd \"%(output)s\"" \
        #            " -im %(image_name)s" \
        #            " -assDir \"%(ass_dir)s\"" \
        #            " \"%(maya_file)s\"" % self["renderSettings"]
        #
        #     cmd2 = "kick.exe -dw -dp -t 0 -v 5" \
        #            " -set options.abort_on_license_fail true" \
        #            " -i \"%(ass_path)s\"" % self["renderSettings"]
        #
        #     cmd = [cmd1, cmd2]
        if "redshift_GPU" in self["plugins"]["plugins"]:        
            if self["common"]["userId"] in [1868564]:
                self["renderSettings"]["bat"] = r"B:\scripts\Maya\redshift_cmd\Erender_RS_new.bat"
                self["renderSettings"]["task_id"] = self["common"]["taskId"]
                self["renderSettings"]["user_id"] = self["common"]["userId"]
                self["renderSettings"]["cmdexe"] = r"C:\Windows\System32\cmd.exe"
                
                # cmd = "\"%(cmdexe)s\" \"%(bat)s\" %(user_id)s %(task_id)s \"%(render.exe)s\" "\
                    # "\"%(renderableLayer)s\" %(start)s %(end)s %(by)s " \
                    # "\"%(projectPath)s\" \"%(maya_file)s\" \"%(output)s\"" \
                    # % self["renderSettings"]        
                # cmd=self["renderSettings"]["bat"]
                # +' "'+self["renderSettings"]["user_id"]+\
                # '"  "'+self["renderSettings"]["task_id"]+'"  "'+self["renderSettings"]["render.exe"]+\
                # '" "'+self["renderSettings"]["renderableLayer"]+'" "' + self["renderSettings"]["start"] +\
                # '" "'+self["renderSettings"]["end"] +'" "'+ self["renderSettings"]["by"] +'" "'+ self["renderSettings"]["projectPath"]+\
                # '" "'+ self["renderSettings"]["maya_file"]+'" "'+ self["renderSettings"]["output"]+'" '
        print "render cmd info:"
        print cmd
        sys.stdout.flush()
        G_JOB_NAME=os.environ.get('G_JOB_NAME')
        render_log_path = "d:/log/render"
        render_log = "%s/%s/%s_render.log" % (render_log_path,self["common"]["taskId"],G_JOB_NAME)
        print render_log
        with open(render_log,"ab+") as l:
            l.write('render cmd info: \n')
            #l.write(cmd)
            l.flush()
            if isinstance(cmd, list):
                for i in cmd:

                    print "render cmd info:"
                    print i
                    sys.stdout.flush()

                    for line in RvOs.run_command(i):
                        l.write(line)
                        l.flush()
                        line_str = line.strip()
                        if line_str:
                            print line_str

                if self["common"]["debug"]:
                    ''
                else:
                    if self["common"]["userId"] in [1818936]:
                        try:
                            os.remove(self["renderSettings"]["ass_path"])
                        except:
                            pass
            else:
                # subprocess.call(cmd)
                is_complete = 0
                re_complete = re.compile(r'^Scene.+completed\.$', re.I)
                if self["common"]["userId"] in [1868564]:
                    os.system(r"B:\scripts\Maya\redshift_cmd\Erender_RS_new.bat")
                    # for line in os.system(r"B:\scripts\Maya\redshift_cmd\Erender_RS_new.bat"):
                    # for line in self.RBcmd(r"B:\scripts\Maya\redshift_cmd\Erender_RS_new.bat",False,True):
                        # line_str = line.strip()
                        # if line_str:
                            # l.write(line)
                            # l.flush()
                            # print line_str
                            # if re_complete.findall(line_str):
                                # RvOs.kill_children()
                                # is_complete = 1
                                # break                            
                    # if not is_complete:
                        # exit(1)                
                
                
                else:                
                    for line in RvOs.run_command(cmd):
                        line_str = line.strip()
                        if line_str:
                            l.write(line)
                            l.flush()
                            print line_str
                            if "ASSERT FAILED" in line_str:
                                RvOs.kill_children()
                                is_complete = 0
                                break
                            if "failed to render" in line_str:
                                RvOs.kill_children()
                                is_complete = 0
                                break
                            if "DL inf loop detected" in line_str:
                                RvOs.kill_children()
                                is_complete = 0
                                break
                                
                            if self["common"]["userId"] in [963287]:
                                if "Maya exited with status -1073741818" in line_str:
                                    exit(-1073741818)
                                if "Maya exited with status -1073741819" in line_str:
                                    exit(-1073741819)

                            if re_complete.findall(line_str):
                                RvOs.kill_children()
                                is_complete = 1
                                break

                    if not is_complete:
                        exit(1)


class LightWaveClass(Render):

    def __init__(self, options):
        Render.__init__(self, options)
        self.get_info()
        self.crack_lightwave()

    def get_info(self):
        self["renderSettings"]["exe"] = r"B:\NewTek\LightWave_%s\bin\lwsn.exe" \
            % (self["common"]["cgv"])
        self["renderSettings"]["config"] = r"C:\users\enfuzion\.NewTek\LightWave\2015.3"

        self["renderSettings"]["lwsn.exe"] = "C:/Program Files/Autodesk/" \
            "maya%s/bin/mayabatch.exe" % (self["common"]["cgv"])
        self["renderSettings"]["output"] = "c:/work/render/%s/output/" % \
            (self["common"]["taskId"])
        if not os.path.exists(self["renderSettings"]["output"]):
            os.makedirs(self["renderSettings"]["output"])

        self["renderSettings"]["cg_file"] = os.path.splitext(self["renderSettings"]["cg_file"])[0] + "_rayvision.lws"

    def crack_lightwave(self):
        self.copytree2(r"B:\NewTek\LWK\LightWave_%s\.NewTek" % (self["common"]["cgv"]),
                       r"C:\users\enfuzion\.NewTek")


class LightWaveLwsn(LightWaveClass):

    def __init__(self, options):
        LightWaveClass.__init__(self, options)

    def render(self):
        pprint.pprint(self)

        cmd = "\"%(exe)s\" -3 -c\"%(config)s\" -d\"%(projectPath)s\" \
               -q \"%(cg_file)s\" %(start)s %(end)s %(by)s" \
               % self["renderSettings"]

        print "Info: Run render lightwave file command:"
        print cmd
        sys.stdout.flush()

        for line in RvOs.run_command(cmd):
            line_str = line.strip()
            if line_str:
                print line_str


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Liu Qiang || MMmaomao')
    parser.add_argument("--js", dest="json", type=str)
    parser.add_argument("--ti", dest="task_id", type=int)
    parser.add_argument("--pt", dest="platform", type=int)
    parser.add_argument("--sf", dest="start", type=int, required=1)
    parser.add_argument("--ef", dest="end", type=int, required=1)
    parser.add_argument("--by", dest="by", type=int, required=1)
    parser.add_argument("--lg", dest="log_object", type=str)
    parser.add_argument("--pl", dest="plugin_file", type=str)
    parser.add_argument("--sp", dest="storage_path", type=str)
    parser.add_argument("--tiles", dest="tiles", type=int, default=1)
    parser.add_argument("--tile_index", dest="tile_index", type=int, default=0)
    parser.add_argument("-d", dest="debug", default=False, action="store_true")

    kwargs = parser.parse_args().__dict__
    maya_info = Maya()
    options = maya_info.get_json(**kwargs)

    render = None
    if str(options["renderSettings"]["tiles"]) != '1' and options["renderSettings"]["tiles"] == options["renderSettings"]["tile_index"]:
        render = NukeMerge(options)
    else:
        if options["common"]["cgSoftName"] == "maya":
            if options["renderSettings"]["renderType"] == "render.exe":
                render = MayaRender(options)
            elif options["renderSettings"]["renderType"] == "mayabatch.exe":
                render = MayaBatch(options)
            elif options["renderSettings"]["renderType"] == "maya.exe":
                render = MayaGui(options)
        elif options["common"]["cgSoftName"] == "arnold":
            if options["renderSettings"]["renderType"] == "kick.exe":
                render = ArnoldKick(options)
        elif options["common"]["cgSoftName"] == "lightwave":
            if options["renderSettings"]["renderType"] == "lwsn.exe":
                render = LightWaveLwsn(options)
    if render:
        render.render()
        if not options["common"]["debug"]:
            render.clean_network()
    else:
        raise Exception("Can not find the match render class.")
