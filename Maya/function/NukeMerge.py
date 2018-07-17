#! /usr/bin/env python
# coding=utf-8
import sys
import os
import nuke
import pprint
if sys.version_info[:2] == (2, 5):
    if sys.platform.startswith("win"):
        sys.path.append(os.path.join(os.path.dirname(__file__), "tim", "py25"))

import argparse

def set_format(width,height ):
    newFormat = nuke.addFormat('%s %s 1 new' % (width,height))
    nuke.Root()['format'].setValue(newFormat)

def create_read(file_path):
    node = nuke.createNode('Read')
    node['file'].fromUserText(file_path)
    return node

def merge_image(images,tile_output):
 
    read_nodes = []
    for i in images:
        read_nodes.append(create_read(i))
    
    merge = nuke.createNode('Merge2')
    x = 0
    for i in read_nodes:
        if x == 2:
            x += 1
            # print i.name()
            merge.setInput(x, i)
            x += 1
        else:
            merge.setInput(x, i)
            x += 1
    merge["operation"].setValue("max")
    merge["also_merge"].setValue("all")
    
    tile_output_folder = os.path.dirname(tile_output)
    if not os.path.exists(tile_output_folder):
        os.makedirs(tile_output_folder)
    
    write = nuke.nodes.Write(inputs=[merge], file=tile_output)
    write["channels"].setValue("all")
    nuke.execute(write.name(), 1, 1, 1)
    nuke.scriptClear()

def merge(kwargs):
    tile_nums = 8
    tile_output_folder= kwargs["tile_output"]
    print tile_output_folder
    if tile_output_folder.endswith(".iff"):
        print "iff"
        tile_output_folder = tile_output_folder.replace(".iff",".exr")
    print tile_output_folder
    
    if len(kwargs["tile_files"]) <= tile_nums:
        print "xiao yu 8 tile"
        print tile_output_folder
        merge_image(kwargs["tile_files"],tile_output_folder)  
    else:
        print "da yu 8 tile"
        tile_output_list=[]
        temp_dir =  os.environ.get('TEMP').replace("\\",'/')   
        name_ext = tile_output_folder.replace("\\",'/').rsplit('/',1)[1].rsplit('.',1)
        name = name_ext[0]
        ext = name_ext[1]
        print "++++++++++++++++++++++++++++++"
        print ext
        print "++++++++++++++++++++++++++++++"
        if ext=="iff":
            ext ="exr"
        a = 0
        for images in  [kwargs["tile_files"][i:i+tile_nums] for i in xrange(0,len(kwargs["tile_files"]),tile_nums)]:
            a += 1
            temp_output_dir= "%s/tile/%s_%s.%s" % (temp_dir,name,a,ext)        
            merge_image(images,temp_output_dir)
            tile_output_list.append(temp_output_dir)
        merge_image(tile_output_list,tile_output_folder)

    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='--------------')
    parser.add_argument("-tiles", dest="tiles", type=int)
    parser.add_argument("-tile_files", dest="tile_files", type=str)
    parser.add_argument("-tile_output", dest="tile_output", type=str)
    parser.add_argument("-width", dest="width", type=int)
    parser.add_argument("-height", dest="height", type=int)

    kwargs = parser.parse_args().__dict__

    kwargs["tile_files"] = eval(kwargs["tile_files"])
    merge(kwargs)
