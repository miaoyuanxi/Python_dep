# ! /usr/bin/env python
# coding=utf-8
# Author: Liu Qiang
# Tel:    13811571784
# QQ:     386939142
import munu
import optparse
import time
import os
import sys

if __name__ == '__main__':
    parser = optparse.OptionParser()

    parser.add_option("-p", dest="txt_path",
                      help="A path contain txt files placed in date folders.",
                      metavar="string")

    parser.add_option("-i", dest="interval", default=1,
                      help="Search txt files time interval, default is 1 "
                           "minutes.",
                      metavar="int")

    parser.add_option("--lv", dest="task_level",
                      help="submit task with this level",
                      metavar="string")

    parser.add_option("--pi", dest="project_id",
                      help="submit task with this project id",
                      metavar="string")

    parser.add_option("--ui", dest="user_id", default=961900,
                      help="submit task with this user id",
                      metavar="int")

    parser.add_option("--un", dest="user_name",
                      help="submit task with this user name",
                      metavar="string")

    parser.add_option("--fi", dest="father_id",
                      help="submit task with this father id",
                      metavar="string")

    parser.add_option("--ps", dest="project_symbol",
                      help="submit task with this project symbol",
                      metavar="string")

    parser.add_option("--ver", dest="client_version",
                      help="client version",
                      metavar="string")

    parser.add_option("--zo", dest="zone",
                      help="zone arg",
                      metavar="string")

    parser.add_option("--it", dest="ignore_texture",
                      help="ignore missing texture",
                      metavar="int", default=1)

    parser.add_option("--fr", dest="custom_frames",
                      help="set custom frames",
                      metavar="string")

    parser.add_option("--pt", dest="platform",
                      help="set which platform to store files",
                      metavar="string")

    parser.add_option("--mt",
                      action="store_true", dest="enable_multi_task",
                      default=False, help="Enable multi task submiting.")

    parser.add_option("--cs", dest="cg_software",
                      help="cg software", default="arnold",
                      metavar="string")

    (options, args) = parser.parse_args()

    if len(munu.RvOs.get_process_list("submit_batch_txt.exe")) > 1:
        print "already has a submit_batch_txt.exe process running"
        exit(0)

    if all((options.txt_path, options.project_id, options.project_symbol)):
        options.ini = os.path.dirname(sys.executable.lower().replace("\\",
                                              "/")) + "/default.ini"

        # print options.ini

        while 1:
            munu.start_txt(options)

            print "Finish submit txt process, waiting for next time..."
            print "\n"
            time.sleep(options.interval*60)

    else:
        print "CMD: %appdata%/renderbus/1005/module/script/submit_batch_maya/submit_batch_txt.exe " \
              "--un \"mijia\"--pi 1083 " \
              "--ps \"PPR\" -p \"F:/mili/txt_files\""
        parser.print_help()
