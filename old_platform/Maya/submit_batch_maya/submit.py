# ! /usr/bin/env python
# coding=utf-8
# Author: Liu Qiang
# Tel:    13811571784
# QQ:     386939142
import munu
import argparse
import time
import os
import sys


def get_desktop_app():
    app_names = ["qrenderbus.exe", "foxrenderfarm.exe"]
    for i in app_names:
        process = munu.RvOs.get_process_path(i)
        if process:
            return process[0]


def submit_to_app(file_path):
    if os.path.exists(file_path):
        app = get_desktop_app()
        submit_exe = os.path.join(os.path.dirname(app), "rendercmd.exe")
        if app:
            cmd = "\"%s\" -submittask \"%s\"" % (submit_exe, file_path)
            exit_code = munu.RvOs.call_command(cmd)
            if exit_code == 1:
                raise Exception("You must select a default project in desktop "
                                "APP")
            if exit_code == 2:
                raise Exception("We don't support this file type: %s"
                                % (os.path.splitext(file_path)[1]))
        else:
            raise Exception("Rayvison desktop APP is not running")
    else:
        raise Exception("%s is not exists" % (file_path))


def scan_txt(options):
    today = "%04d_%02d_%02d" % (time.localtime()[:3])
    yesterday = "%04d_%02d_%02d" % time.localtime(time.time() - 3600*24)[:3]
    the_day_before_yesterday = "%04d_%02d_%02d" % time.localtime(time.time() -
                                                                 3600*48)[:3]

    txt_files = []
    for day in [the_day_before_yesterday, yesterday, today]:
        day_path = os.path.join(options["txt_path"], day)
        if os.path.exists(day_path):
            for f in os.listdir(day_path):
                if f.lower().endswith(".txt"):
                    txt_files.append(os.path.join(day_path, f))

    for i in txt_files:
        analyze_txt(i)


def analyze_txt(txt):
    print "found txt file: " + txt
    ok_mark = txt + ".ok"
    start_mark = txt + ".start"

    if os.path.exists(ok_mark):
        print "This txt file had been submited, so skip."
    elif os.path.exists(start_mark):
        print "This txt file is submiting, so skip."
    else:
        with open(start_mark, "w"):
            ''

        print "Start to analyze this txt file."

        submit_to_app(open(txt).read().strip())

        with open("%s.%s" % (ok_mark, "%04d_%02d_%02d_%02d_%02d_%02d" %
                  (time.localtime()[:6])), "w"):
            ''

        with open(ok_mark, "w"):
            ''


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Liu Qiang || MMmaomao")
    parser.add_argument("-p", dest="txt_path",
                        help="A path contain txt files placed in date folders.",
                        type=str)
    parser.add_argument("-f", dest="file_path",
                        help="Submit file directly using absolute file path "
                             "such as: E:/test/test.mb",
                        type=str)

    parser.add_argument("-i", dest="interval", default=1,
                        help="Search txt files time interval, default is 1 "
                             "minutes.",
                        type=int)

    # parser.add_argument("-mt",
    #                     action="store_true", dest="enable_multi_task",
    #                     default=False, help="Enable multi task submiting.")

    kwargs = parser.parse_args().__dict__

    if len(munu.RvOs.get_process_list("submit.exe")) > 1:
        print "already has a submit.exe process running"
        exit(0)

    if kwargs["file_path"]:
        print "Submit %s to desktop app." % (kwargs["file_path"])
        submit_to_app(kwargs["file_path"])
    elif kwargs["txt_path"]:
        print "Start scan the txt path: %s" % (kwargs["txt_path"])

        while 1:
            scan_txt(kwargs)
            print "Finish submit txt process, waiting for next time..."
            print "\n"
            time.sleep(kwargs["interval"]*60)

    else:
        print "Examples: %appdata%/renderbus/1005/module/script/submit_batch_maya" \
              "/submit.exe -p \"E:/test_files/txt\""
        print "Examples: %appdata%/renderbus/1005/module/script/submit_batch_maya" \
              "/submit.exe -f \"E:/test_files/test.mb\""
        parser.print_help()
