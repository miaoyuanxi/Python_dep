#!/usr/bin/env python
# encoding:utf-8
# -*- coding: utf-8 -*-
import logging
import os
import sys
import re



class father():
    def call_children(self):
        child_method = getattr(self, 'out')# 获取子类的out()方法
        child_method() # 执行子类的out()方法

class children(father):
    def out(self):
        print "hehe"

#
# child = children()
# child.call_children()

aa  = 'dfsgsdfsdfsdfsdrf'


def get_encode(encode_str):
    if isinstance(encode_str, unicode):
        return "unicode"
    else:
        for code in ["utf-8", sys.getfilesystemencoding(), "gb18030", "ascii", "gbk", "gb2312"]:
            try:
                encode_str.decode(code)
                return code
            except:
                pass

def str_to_unicode(encode_str):
    if isinstance(encode_str, unicode):
        return encode_str
    else:
        code = get_encode(encode_str)
        return encode_str.decode(code)

def check_contain_chinese(check_str):
    '''
    check  this string  contain  chinese
    :param check_str: sting
    :return: True or  False
    '''
    # for ch in check_str.decode('utf-8'):
    #     if u'\u4e00' <= ch <= u'\u9fff':
    #         return True
    # return False
    zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
    check_str = str_to_unicode(check_str)
    match = zh_pattern.search(check_str)
    if match:
        return check_str
    else:
        return False

bb = "D:/dflsjf/多萨洛夫姐啊斯拉夫/dsff是独立房间数量.ma"

def check_scene_name():
    scene_name = os.path.splitext(os.path.basename(bb))[0]
    if not re.findall("^[A-Z][^-]+[0-9]$", scene_name):
        print "555555"
        return False
    return True
    print "6666"
    
    
def unicode_to_str(str1, str_encode='system'):
    if str1 == None or str1 == "" or str1 == 'Null' or str1 == 'null':
        str1 = ""
        return str1
    elif isinstance(str1, unicode):
        try:
            if str_encode.lower() == 'system':
                str1 = str1.encode(sys.getfilesystemencoding())
            elif str_encode.lower() == 'utf-8':
                str1 = str1.encode('utf-8')
            elif str_encode.lower() == 'gbk':
                str1 = str1.encode('gbk')
            else:
                str1 = str1.encode(str_encode)
        except Exception as e:
            print ('[err]unicode_to_str:encode %s to %s failed' % (str1, str_encode))
            print (e)
    else:
        print ('%s is not unicode ' % (str1))
    return str(str1)
    
def check_maya_version(maya_file):
    result = None
    maya_file = unicode_to_str(maya_file)
    if maya_file.endswith(".ma"):
        infos = []
        with open(maya_file, "r") as f:
            while 1:
                line = f.readline()
                if line.startswith("createNode"):
                    break
                elif line.strip() and not line.startswith("//"):
                    infos.append(line.strip())

        file_infos = [i for i in infos if i.startswith("fileInfo")]
        for i in file_infos:
            if "product" in i:
                r = re.findall(r'Maya.* (\d+\.?\d+)', i, re.I)
                if r:
                    result = int(r[0].split(".")[0])
            if result == 2016 and "version" in i:
                if "2016 Extension" in i:
                    result = 2016.5
        file_info_2013 = [i for i in infos if i.startswith("requires")]
        if result == 2013:
            for j in file_info_2013:
                if "maya \"2013\";" in j:
                    result = 2013
                else:
                    result = 2013.5

    elif maya_file.endswith(".mb"):
        with open(maya_file, "r") as f:
            info = f.readline()

        file_infos = re.findall(r'FINF\x00+\x11?\x12?K?\r?(.+?)\x00(.+?)\x00',
                                info, re.I)
        for i in file_infos:
            if i[0] == "product":
                result = int(i[1].split()[1])
                
            if result == 2016 and "version" in i[0]:
                if "2016 Extension" in i[1]:
                    result = 2016.5

        file_info_2013 = re.findall(r'2013ff10',
                                info, re.I)

        if result == 2013:
            print file_info_2013
            for j in file_info_2013:
                if j[0]:
                    result = 2013.5
                else:
                    result = 2013

    if result:
        print("get maya file version %s" % (result))

aa = r"D:/test/2016.5.mb"

check_maya_version(aa)
