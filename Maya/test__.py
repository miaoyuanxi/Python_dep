#!/usr/bin/env python
# encoding:utf-8
# -*- coding: utf-8 -*-

import os
import time
import socket
import re
import math

class A(object):
	def __init__(self):
		self.aa = 1111111222
		self.bb = "3333"
		dd = B()
		dd.b_print()
	def a_print(self):
		print("a")
	def b_print(self):
		pass
	def run(self):
		dd = B()
		dd.b_print()
		ff = dd.b_print()
		print ff
		# child_method = getattr(self, 'b_print')  # 获取子类的run()方法
		# child_method()  # 执行子类的run()方法
class B(A):
	def __init__(self,cc = None,jj= None):
		A.__init__(self)
		self.jj = jj
	def b_print(self):
		self.a_print()
		print("b")
		print self.aa
		return self.jj
	def dd(self):
		self.run()
		
		


# if __name__ == '__main__':
# 	import json
# 	import codecs
# 	path = 'd:/test.json'
# 	dic = {u'file2_computedFileTextureNamePattern': {'local_path': [], 'source_path': [u'E:\\Etudes & Tutos\\File\\Houdini project\\HDRI - HDRI - HDRI - Bought\\Sky up with clouds.exr'], 'env': {}, 'missing': [u'E:\\Etudes & Tutos\\File\\Houdini project\\HDRI - HDRI - HDRI - Bought\\Sky up with clouds.exr']}, u'globule:file3_fileTextureName': {'local_path': [], 'source_path': [u'G:\\BOUROUISSA\\textures\\Gravel-2408b-bump-map.jpg'], 'env': {}, 'missing': [u'G:\\BOUROUISSA\\textures\\Gravel-2408b-bump-map.jpg']}, u'globuleobj:file3_computedFileTextureNamePattern': {'local_path': [], 'source_path': [u'G:\\BOUROUISSA\\textures\\Gravel-2408b-bump-map.jpg'], 'env': {}, 'missing': [u'G:\\BOUROUISSA\\textures\\Gravel-2408b-bump-map.jpg']}, u'globule:file2_fileTextureName': {'local_path': [], 'source_path': [u'C:\\Users\\Fay\u93f0l Hiba\\Downloads\\Documents\\01\\Blood Stone CH16.jpg'], 'env': {}, 'missing': [u'C:\\Users\\Fay\u93f0l Hiba\\Downloads\\Documents\\01\\Blood Stone CH16.jpg']}, u'globule:file2_computedFileTextureNamePattern': {'local_path': [], 'source_path': [u'C:\\Users\\Fay\u93f0l Hiba\\Downloads\\Documents\\01\\Blood Stone CH16.jpg'], 'env': {}, 'missing': [u'C:\\Users\\Fay\u93f0l Hiba\\Downloads\\Documents\\01\\Blood Stone CH16.jpg']}, u'file1_computedFileTextureNamePattern': {'local_path': [], 'source_path': [u'W:\\3D VFX Project\\VIZPARK - HDRI Skydome 01\\VP Skydome 09\\02 HDRI skydome\\VP_hdri_skydome_09.exr'], 'env': {}, 'missing': [u'W:\\3D VFX Project\\VIZPARK - HDRI Skydome 01\\VP Skydome 09\\02 HDRI skydome\\VP_hdri_skydome_09.exr']}, u'globuleobj:file2_computedFileTextureNamePattern': {'local_path': [], 'source_path': [u'G:\\BOUROUISSA\\textures\\seamless_human_skin_by_hhh316-d4nh537.jpg'], 'env': {}, 'missing': [u'G:\\BOUROUISSA\\textures\\seamless_human_skin_by_hhh316-d4nh537.jpg']}, u'globule:file3_computedFileTextureNamePattern': {'local_path': [], 'source_path': [u'G:\\BOUROUISSA\\textures\\Gravel-2408b-bump-map.jpg'], 'env': {}, 'missing': [u'G:\\BOUROUISSA\\textures\\Gravel-2408b-bump-map.jpg']}, u'globuleobj:file2_fileTextureName': {'local_path': [], 'source_path': [u'G:\\BOUROUISSA\\textures\\seamless_human_skin_by_hhh316-d4nh537.jpg'], 'env': {}, 'missing': [u'G:\\BOUROUISSA\\textures\\seamless_human_skin_by_hhh316-d4nh537.jpg']}, u'file2_fileTextureName': {'local_path': [], 'source_path': [u'E:\\Etudes & Tutos\\File\\Houdini project\\HDRI - HDRI - HDRI - Bought\\Sky up with clouds.exr'], 'env': {}, 'missing': [u'E:\\Etudes & Tutos\\File\\Houdini project\\HDRI - HDRI - HDRI - Bought\\Sky up with clouds.exr']}, u'file1_fileTextureName': {'local_path': [], 'source_path': [u'W:\\3D VFX Project\\VIZPARK - HDRI Skydome 01\\VP Skydome 09\\02 HDRI skydome\\VP_hdri_skydome_09.exr'], 'env': {}, 'missing': [u'W:\\3D VFX Project\\VIZPARK - HDRI Skydome 01\\VP Skydome 09\\02 HDRI skydome\\VP_hdri_skydome_09.exr']}, u'globuleobj:file3_fileTextureName': {'local_path': [], 'source_path': [u'G:\\BOUROUISSA\\textures\\Gravel-2408b-bump-map.jpg'], 'env': {}, 'missing': [u'G:\\BOUROUISSA\\textures\\Gravel-2408b-bump-map.jpg']}}
#
#
# 	with codecs.open(path, 'w', 'utf-8') as f:
# 		json.dump(dic, f, ensure_ascii=False, indent=4)
# def print_trilateral(rows=4, mode=1):
# 	'''
# 	:param rows: rows counts
# 	:param mode: up  or  down
# 	:return: a trilateral
# 	'''
# 	for i in range(0, rows):
# 		for k in range(0, i+1 if mode == 1 else rows - i):
# 			print " * ",  # 注意这里的","，一定不能省略，可以起到不换行的作用
# 			k += 1
# 		i += 1
# 		print "\n"
#
# print_trilateral(4,1)

def TimeStampToTime(timestamp):
	'''把时间戳转化为时间: 1479264792 to 2016-11-16 10:53:12'''
	timeStruct = time.localtime(timestamp)
	return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)

def get_FileSize(filePath):
	'''获取文件的大小,结果保留两位小数，单位为MB'''
	filePath = unicode(filePath, 'utf8')
	fsize = os.path.getsize(filePath)
	fsize = fsize / float(1024 * 1024)
	return round(fsize, 2)


def get_FileModifyTime(filePath):
	'''获取文件的修改时间'''
	filePath = unicode(filePath, 'utf8')
	t = os.path.getmtime(filePath)
	return TimeStampToTime(t)


# aa = "D:/ccccc.mb"
#
# #
# # print type(get_FileSize(aa))
# # print type(get_FileModifyTime(aa))
# def get_computer_hostname():
# 	return socket.gethostname()
#
# def get_computer_ip():
# 	host_name = get_computer_hostname()
# 	ip_str = socket.gethostbyname(host_name)
# 	return ip_str
#
#
# print get_computer_ip()

# log_line = '2018-10-11 11:31:34 INFO - 00:00:26 2176MB ERROR | [texturesys] unspecified OIIO error (filename = "Y:/XCM_2019D"Y()/Asse"t/seq+-0打上了飞机拉萨00/character/xiongda/sourceimages/xiongda/xiongda_body_col08.jpg")'
#
#
# def get_log_ini(log_line):
# 	error_file_list = []
# 	if log_line.strip() and "ERROR | [texturesys] unspecified OIIO error" in log_line:
# 		p1 = re.compile(r"(?<=\().+(?=[\',\)])", re.I)
# 		p1 = re.compile(r"\"(.*)\"", re.I)
# 		error_file_path = p1.findall(log_line)
# 		if error_file_path:
# 			error_file_list.append(error_file_path[0])
# 	return error_file_list
#
#
# print get_log_ini(log_line)


#
# def print_trilateral(rows=4, mode=1):
# 	'''
# 	:param rows: rows counts
# 	:param mode: up  or  down
# 	:return: a trilateral
# 	'''
# 	for i in range(0, rows):
# 		print(" * " * (i + 1 if mode == 1 else rows - i))
# 		i += 1
# 		print("\n")
#
# print_trilateral(5,mode = 2)

#
# def get_region(tiles, tile_index, width, height):
# 	n = int(math.sqrt(tiles))
# 	for i in sorted(range(2, n + 1), reverse=1):
# 		if tiles % i != 0:
# 			continue
# 		else:
# 			n = i
# 			break
# 	n3 = tiles / n
# 	n1 = tile_index / n3
# 	n2 = tile_index % n3
# 	top = height / n * (n1 + 1)
# 	left = width / n3 * n2
# 	bottom = height / n * n1
# 	right = width / n3 * (n2 + 1)
# 	if right == width:
# 		right -= 1
# 	if top == height:
# 		top -= 1
# 	return int(left), int(right), int(bottom), int(top)



def get_region(tiles, tile_index, width, height):
	print(tiles, tile_index, width, height)
	print("999999999999999999999999999")
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
	left = width / n3 * n2
	bottom = height / n * n1
	right = width / n3 * (n2 + 1)
	if right == width:
		right -= 1
	if top == height:
		top -= 1
	print(int(left), int(right), int(bottom), int(top))
tiles = 8
width = 1024
height = 1024

# print get_region(8,7, width, height)
#
#
# dict_t = {"a":"aa","b":"bb","c":"cc"}
# str_ =""
# for i in dict_t:
# 	str_ += "%s = '%s'; " % (i ,dict_t[i])
# # print str_
# # exec(str_)
# # print a
#
# print "%"
d={'age': '3', 'boyfriend': 'czt', 'name': {"aa":"aaaa"}, 'sex': 'women'}
s1=d.items()
lst=[]
for key,value in s1:
	s3="%s=%s"%(key,value)
	lst.append(s3)
print lst
print ",".join(lst)
