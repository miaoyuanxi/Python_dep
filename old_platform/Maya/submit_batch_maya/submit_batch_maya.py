# ! /usr/bin/env python
# coding=utf-8
import munu
import os
import sys
from optparse import (OptionParser, BadOptionError, AmbiguousOptionError)


class PassThroughOptionParser(OptionParser):
    """
    An unknown option pass-through implementation of OptionParser.

    When unknown arguments are encountered, bundle with largs and try again,
    until rargs is depleted.

    sys.exit(status) will still be called if a known argument is passed
    incorrectly (e.g. missing arguments or bad argument types, etc.)
    """
    def _process_args(self, largs, rargs, values):
        while rargs:
            try:
                OptionParser._process_args(self, largs, rargs, values)
            except (BadOptionError, AmbiguousOptionError), e:
                largs.append(e.opt_str)


if __name__ == '__main__':
    parser = PassThroughOptionParser()

    parser.add_option("--ml", dest="maya_list",
                      help="maya file path, use ',' "
                           "to seperate, such as: -ml test01.ma,"
                           "test02.ma,test03.mb",
                      type="string")

    parser.add_option("--mf", dest="maya_file",
                      help="single maya file path",
                      type="string")

    parser.add_option("--mp", dest="maya_project",
                      help="maya project path",
                      type="string")

    parser.add_option("--pp", dest="project_path",
                      help="project path",
                      type="string")

    parser.add_option("--mv", dest="maya_version",
                      help="maya version",
                      type="string")

    parser.add_option("--mayai", dest="maya_install",
                      help="maya install path",
                      type="string")

    parser.add_option("--lv", dest="task_level",
                      help="submit task with this level",
                      type="string")

    parser.add_option("--pi", dest="project_id",
                      help="submit task with this project id",
                      type="string")

    parser.add_option("--ps", dest="project_symbol",
                      help="submit task with this project symbol",
                      type="string")

    parser.add_option("--pl", dest="plugin_file",
                      help="submit task with this plugin_file",
                      type="string")

    parser.add_option("--ui", dest="user_id",
                      help="submit task with this user id",
                      type="string")

    parser.add_option("--fi", dest="father_id",
                      help="submit task with this father id",
                      type="int")

    parser.add_option("--ver", dest="client_version",
                      help="client version",
                      type="string")

    parser.add_option("--zo", dest="zone",
                      help="zone arg",
                      type="string")

    parser.add_option("--it", dest="ignore_texture",
                      help="ignore missing texture",
                      type="int", default=0)

    parser.add_option("--os", dest="only_scene",
                      help="only submit scene file. ignore the texture files.",
                      type="int", default=0)

    parser.add_option("--sm", dest="submit_mode",
                      help="submit with this mode",
                      type="int", default=1)

    parser.add_option("--fr", dest="custom_frames",
                      help="set custom frames",
                      type="string")

    parser.add_option("--pt", dest="platform",
                      help="set which platform to store files",
                      type="string")

    parser.add_option("--lang", dest="language",
                      help="set language to display info",
                      type="string")

    parser.add_option("--from", dest="client_root",
                      help="client software root path",
                      type="string")

    parser.add_option("-d", "--debug",
                      action="store_true", dest="is_debug", default=1,
                      help="show debug infos.")

    parser.add_option("--cgfl", dest="cg_file_name",
                      help="cg_file_name path, use ',' "
                           "to seperate, such as: -ml test01.ma,"
                           "test02.ma,test03.mb",
                      type="string")

    parser.add_option("--cgv", dest="cg_version",
                      help="maya version",
                      type="string")

    parser.add_option("--cginst", dest="cg_install",
                      help="maya install path",
                      type="string")

    parser.add_option("--td", dest="temp_dir",
                      help="Assigned temporary dir",
                      type="string")

    parser.add_option("--dd", dest="default_dir",
                      help="Setting deafault project dir",
                      type="string")

    parser.add_option("--tid", dest="task_id",
                      help="task id",
                      type="string")

    parser.add_option("--de", dest="dependency",
                      help="submit with dependency",
                      type="int", default=0)

    parser.add_option("--mi", dest="dont_analyze_mi",
                      help="whether ignore .mi files",
                      type="int", default=0)

    parser.add_option("--ass", dest="dont_analyze_ass",
                      help="whether ignore .ass files",
                      type="int", default=0)

    parser.add_option("--tm", dest="task_mode",
                      help="task mode",
                      type="int", default=0)

    parser.add_option("--sa", dest="seperate_account",
                      help="seperate user and father account mode",
                      type="int", default=0)

    parser.add_option("--mode", dest="analyze_mode",
                      help="select your analyze mode",
                      type="string", default="normal")

    parser.add_option("--ap", dest="all_proxy",
                      help="analyze all proxy files even proxy files is a sequence",
                      type="int", default=0)

    (options, args) = parser.parse_args()

    if options.maya_list or options.cg_file_name:
        if not options.seperate_account:
            options.father_id = 0
        if options.cg_file_name:
            options.cg_file_name = options.cg_file_name.replace("\\", "/")
            options.maya_list = options.cg_file_name
        if options.cg_version:
            options.maya_version = options.cg_version
        if options.cg_install:
            options.maya_install = options.cg_install.replace("\\", "/")

        if not os.path.exists(options.temp_dir):
            os.makedirs(options.temp_dir)

        if options.project_path:
            options.project_path = options.project_path.replace("\\", "/")

        options.maya_list = options.maya_list.replace("\\", "/")
        options.ini = os.path.dirname(sys.executable.lower().replace("\\",
                                      "/")) + "/default.ini"
        options.only_scene = int(options.only_scene)
        options.ignore_texture = int(options.ignore_texture)
        options.submit_mode = int(options.submit_mode)
        options.client_root = options.client_root.replace("\\", "/")

        if options.only_scene:
            options.ignore_texture = 1

        if options.user_id == "1852677":
            options.all_proxy = 1

        munu.start_maya(options)
    else:
        parser.print_help()
