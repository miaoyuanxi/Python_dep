#!/usr/bin/env python
#encoding:utf-8
# -*- coding: utf-8 -*-
import os
import re
import shutil
def change():
    rsmap_list = []
    output = 'c:/work/render/16061768/output/107_109_1/'

    projectPath = 'Q:/Feature_projects/ali/3D/scenes/Render/Seq101/Seq101_Sc005/Final/irradiance_map'
    if projectPath == None or projectPath == '':
        projectPath = r'C:/Users/enfuzion/Documents/maya/projects/default'
    print projectPath
    render_log = r'D:\test.txt'
    if os.path.exists(render_log):
        print "77777777"
    with open(render_log, "r") as l:
        for line in l:
            line = line.encode("utf-8")
            print line
            aa = line.strip()
            print aa
            if line.strip() and "Saving to disk" in line:
                print line
                print "6666666"
                projectPath = projectPath.replace('/', '\\\\')
                p1 = re.compile(r"%s.+\.rsmap" % projectPath, re.I)
                rsmap_file = p1.findall(line)
                print rsmap_file

                if rsmap_file:
                    rsmap_list.append(rsmap_file[0])
    if rsmap_list:
        print rsmap_list
        for rsmap_file in rsmap_list:
            if os.path.exists(rsmap_file):
                print rsmap_file
                new_file_path = output + '/' + rsmap_file.rsplit(projectPath)[1].rsplit('/', 1)[1]
                print new_file_path
                new_file_path = new_file_path.replace('/', '\\')
                print new_file_path
                copy_path = os.path.dirname(new_file_path)
                if not os.path.exists(copy_path):
                    os.makedirs(copy_path)
                print "the rsamp copy path is %s " % copy_path

                shutil.copy(rsmap_file, copy_path)