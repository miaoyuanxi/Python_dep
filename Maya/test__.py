#!/usr/bin/env python
# encoding:utf-8
# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
# from __future__ import print_function
import os
import time
import socket
import re
import math
import _winreg
import os
import re
import sys
import math
import traceback
import psutil
import threading
import os,datetime,time



# try:
#     import _winreg
# except ImportError:
#     import winreg as _winreg


#
# class A(object):
# 	def __init__(self):
# 		self.aa = 1111111222
# 		self.bb = "3333"
# 		dd = B()
# 		dd.b_print()
# 	def a_print(self):
# 		print("a")
# 	def b_print(self):
# 		pass
# 	def run(self):
# 		dd = B()
# 		dd.b_print()
# 		ff = dd.b_print()
# 		print (ff)
# 		# child_method = getattr(self, 'b_print')  # 获取子类的run()方法
# 		# child_method()  # 执行子类的run()方法
# class B(A):
# 	def __init__(self,cc = None,jj= None):
# 		A.__init__(self)
# 		self.jj = jj
# 	def b_print(self):
# 		self.a_print()
# 		print("b")
# 		print (self.aa)
# 		return self.jj
# 	def dd(self):
# 		self.run()
#
		


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
#
# def TimeStampToTime(timestamp):
# 	'''把时间戳转化为时间: 1479264792 to 2016-11-16 10:53:12'''
# 	timeStruct = time.localtime(timestamp)
# 	return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)
#
# def get_FileSize(filePath):
# 	'''获取文件的大小,结果保留两位小数，单位为MB'''
# 	filePath = unicode(filePath, 'utf8')
# 	fsize = os.path.getsize(filePath)
# 	fsize = fsize / float(1024 * 1024)
# 	return round(fsize, 2)
#
#
# def get_FileModifyTime(filePath):
# 	'''获取文件的修改时间'''
# 	filePath = unicode(filePath, 'utf8')
# 	t = os.path.getmtime(filePath)
# 	return TimeStampToTime(t)


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



# def get_region(tiles, tile_index, width, height):
# 	print(tiles, tile_index, width, height)
# 	print("999999999999999999999999999")
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
# 	print(int(left), int(right), int(bottom), int(top))
# tiles = 8
# width = 1024
# height = 1024
#
# # print get_region(8,7, width, height)
# #
# #
# # dict_t = {"a":"aa","b":"bb","c":"cc"}
# # str_ =""
# # for i in dict_t:
# # 	str_ += "%s = '%s'; " % (i ,dict_t[i])
# # # print str_
# # # exec(str_)
# # # print a
# #
# # print "%"
# d={'age': '3', 'boyfriend': 'czt', 'name': {"aa":"aaaa"}, 'sex': 'women'}
# s1=d.items()
# lst=[]
# for key,value in s1:
# 	s3="%s=%s"%(key,value)
# 	lst.append(s3)
# print lst
# print ",".join(lst)
# def location_from_reg(version):
# 	# for 2013/2013.5, 2016/2016.5
# 	versions = (version, "{0}.5".format(version))
# 	location = None
# 	for v in versions:
# 		_string = r'SOFTWARE\Autodesk\Maya\{0}\Setup\InstallPath'.format(v)
# 		print(_string)
# 		try:
# 			handle = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, _string)
# 			location, type = _winreg.QueryValueEx(handle, "MAYA_INSTALL_LOCATION")
# 			print('localtion:{0}, type:{1}'.format(location, type))
# 			break
# 		except (WindowsError) as e:
# 			print(traceback.format_exc())
# 			pass
#
# 	return location
#
#
# print (location_from_reg(2017))


# coding=utf-8
# 2018/11/15-9:47-2018

import os
import re
import sys
import subprocess
import _subprocess
import time
import logging
import uuid
import pprint
import shutil
import gzip
import traceback
import json
import locale
import cPickle
import glob
import codecs
# server_config = {}
# server_config["forbidden_drives"] = ['B:', 'C:', 'D:']
#
#
# def run_command(cmd, ignore_error=None, shell=0):
# 	startupinfo = subprocess.STARTUPINFO()
# 	startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
# 	startupinfo.wShowWindow = _subprocess.SW_HIDE
# 	p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
# 						 stderr=subprocess.STDOUT, startupinfo=startupinfo,
# 						 shell=shell)
#
# 	while 1:
# 		# returns None while subprocess is running
# 		return_code = p.poll()
# 		# if return_code == 0:
# 		#     break
# 		if return_code == 1:
# 			if ignore_error == 1:
# 				break
# 			else:
# 				raise Exception(cmd + " was terminated for some reason.")
# 		elif return_code != None and return_code != 0:
# 			if ignore_error == 1:
# 				break
# 			else:
# 				print "exit return code is: " + str(return_code)
# 				raise Exception(cmd + " was crashed for some reason.")
# 		line = p.stdout.readline()
# 		if not line:
# 			break
# 		yield line
#
#
#
# def get_windows_mapping():
#
# 	networks = {}
# 	locals = []
# 	all = []
# 	net_use = dict([re.findall(r'.+ ([a-z]:) +(.+)', i.strip(), re.I)[0]
# 					for i in run_command('net use')
# 					if i.strip() if re.findall(r'.+ ([a-z]:) +(.+)',
# 											   i.strip(), re.I)])
# 	for i in net_use:
# 		net_use[i] = net_use[i].replace("Microsoft Windows Network", "").strip()
#
# 	for i in run_command('wmic logicaldisk get deviceid,drivetype,providername'):
# 		if i.strip():
# 			# a = re.findall(r'([a-z]:) +(\d) +(.+)?', i.strip(), re.I)
# 			# print a
# 			info = i.split()
# 			if info[1] == "4":
# 				if len(info) == 3:
# 					if re.findall(r'^[\w _\-.:()\\/$]+$', info[2], re.I):
# 						networks[info[0]] = info[2].replace("\\", "/")
# 					else:
# 						networks[info[0]] = None
# 					all.append(info[0])
# 				else:
# 					if info[0] in net_use:
# 						if os.path.exists(net_use[info[0]]):
# 							if re.findall(r'^[\w _\-.:()\\/$]+$', net_use[info[0]], re.I):
# 								networks[info[0]] = net_use[info[0]].replace("\\", "/")
# 							else:
# 								networks[info[0]] = None
# 							all.append(info[0])
# 						else:
# 							# Don't know why the drive is not exists when using python to check.
# 							# Is this a network issue?
# 							# Can not reproduce this issue manually.
# 							print "%s is not exists" % (info[0])
# 							networks[info[0]] = None
# 							all.append(info[0])
# 					else:
# 						networks[info[0]] = None
# 						all.append(info[0])
#
# 			elif info[1] in ["3", "2"]:
# 				if info[0] in server_config["forbidden_drives"]:
# 					locals.append(info[0])
# 				else:
# 					networks[info[0]] = None
# 				all.append(info[0])
#
# 	return (locals, networks, all)
#
#
# def get_computer_mac():
# 	mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
# 	# return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])
# 	return mac
#
#
#
# print type(get_computer_mac())

#
# def inter_path(path):
# 	first_two = path[0:2]
# 	if first_two in ('//', '\\\\'):
# 		norm_path = path.replace('\\', '/')
# 		index = norm_path.find('/', 2)
# 		if index <= 2:
# 			return False
# 		return True
#
#
# def parse_inter_path(path):
# 	first_two = path[0:2]
# 	if first_two in ('//', '\\\\'):
# 		norm_path = path.replace('\\', '/')
# 		index = norm_path.find('/', 2)
# 		if index <= 2:
# 			return ''
# 		return path[:index], path[index:]
#
#
# def convert_path(user_input, path):
# 	"""
# 	:param user_input: e.g. "/1021000/1021394"
# 	:param path: e.g. "D:/work/render/19183793/max/d/Work/c05/111409-021212132P-embedayry.jpg"
# 	:return: \1021000\1021394\D\work\render\19183793\max\d\Work\c05\111409-021212132P-embedayry.jpg
# 	"""
# 	result_file = path
# 	lower_file = os.path.normpath(path.lower()).replace('\\', '/')
# 	file_dir = os.path.dirname(lower_file)
# 	if file_dir is None or file_dir.strip() == '':
# 		pass
# 	else:
# 		if inter_path(lower_file) is True:
# 			start, rest = parse_inter_path(lower_file)
# 			# result_file = user_input + '/net/' + start.replace('//', '') + rest.replace('\\', '/')
# 			result_file = user_input + start + rest.replace('\\', '/')
# 		else:
# 			result_file = user_input + '\\' + path.replace('\\', '/').replace(':', '')
#
# 	result = os.path.normpath(result_file)
# 	result = result.replace("\\", "/")
# 	return result
# aa = "D:/work/render/19183793/max/d/Work/c05/111409-021212132P-embedayry.jpg"
#
# print convert_path("",aa)


#
# def get_mnt_map_dict():
# 	upload_info_dict =["D:/work/render/19183793/max/d/Work/c05/111409-021212132P-embedayry.jpg"]
# 	mnt_map_dict = {}
# 	mnt_map = {}
#
# 	for asset_dict in upload_info_dict:
# 		first_two = asset_dict[0:2]
#
# 		# norm_path = local_path.replace('\\', '/')
# 		# index = norm_path.find('/', 2)
# 		# if index <= 2:
# 		#     return ''
#
# 		if first_two not in ["B:","C","D"]:
# 			mnt_map_dict = mnt_map_dict.update({first_two: first_two[0:2].split(":")[0]})
#
#
# 	return mnt_map_dict
#
# print get_mnt_map_dict()
import platform
# reference_list = []
# invalid_abc = []
# error_list = []
# def convertUnicode2Str(uStr):
# 	CURRENT_OS = platform.system()
# 	if isinstance(uStr, unicode):
# 		if CURRENT_OS == 'Linux':
# 			uStr = uStr.encode('utf-8')
# 		else:
# 			uStr = uStr.encode(sys.getfilesystemencoding())
# 		return uStr
# 	else:
# 		return uStr
#
#
# def print_info_err(info):
# 	info = convertUnicode2Str(info)
# 	r = re.findall(r"Reference file not found.+?: +(.+)", info, re.I)
# 	r1 = re.findall(r"Error: line \d+:(.*) is not a valid Alembic file", info, re.I)
# 	if r:
# 		if r[0] not in reference_list:
# 			reference_list.append(r[0])
#
# 	if r1:
# 		if r1[0] not in invalid_abc:
# 			invalid_abc.append(r1[0])
#
# 	if info not in error_list:
# 		error_list.append(info)
# 	print ("[Analyze Error]%s" % (info))
#
# print_info_err(u"......二缺，场景中没有开渲染层，让客户开启要渲染的渲染层，再提交任务........")

# aa = "Warning: Reference file not found. : //10.70.242.101/d/inputdata5/100000000/100000056/maya_test/23.ma"
# print_info_err(aa)
# print reference_list




#
#
# def start_monitor(self):
#
# 	self.monitorMaya = MonitorThread(60, log_obj=self.G_DEBUG_LOG)
# 	self.monitorMaya.setDaemon(True)
# 	self.monitorMaya.start()
#
#
# def stop_monitor(self):
# 	if self.monitorMaya != None:
# 		self.monitorMaya.stop()
#
#
#
#
#
#
# class MonitorThread(threading.Thread):
# 	"""
# 	监控占用的CPU、Memory
# 	"""
#
# 	def __init__(self, interval, log_obj=None):
# 		"""
# 		:param interval: 间隔时间
# 		:param log_obj: 日志对象，用来打印执行过程日志信息，如self.G_DEBUG_LOG
# 		"""
# 		threading.Thread.__init__(self)
#
# 		self.interval = interval
# 		self.log_obj = log_obj
# 		self.thread_stop = False
#
# 	def log_print(self, my_log, log_str):
# 		if my_log == None:
# 			print(log_str)
# 		else:
# 			my_log.info(log_str)
#
# 	def get_mem_cpu(self):
# 		data = psutil.virtual_memory()
# 		total = data.total  # 总内存,单位为byte
# 		free = data.available  # 可用内存
# 		memory = "Memory usage:%d" % (int(round(data.percent))) + "%" + " "
# 		cpu = "CPU:%0.2f" % psutil.cpu_percent(interval=1) + "%"
# 		return cpu,memory
#
# 	def loop(self):
# 		print 'thread %s is running...' % threading.current_thread().name
# 		while (True):
# 			info = self.get_mem_cpu()
# 			print 'thread %s >>> ' % (threading.current_thread().name)
# 			time.sleep(0.2)
# 			print info + "\b" * (len(info) + 1),
# 		print 'thread %s ended.' % threading.current_thread().name
#
#
# 	def run(self):  # Overwrite run() method, put what you want the thread do here
# 		self.log_print(self.log_obj,'------------------------- Start MonitorThread -------------------------')
# 		while not self.thread_stop:
# 			try:
# 				self.log_print(self.log_obj, '[MonitorThread].___MonitorThread____')
# 				cpu_str, mem_str = self.get_mem_cpu()
# 				self.log_print(self.log_obj,'[MonitorThread].Cpu={0}% Memory={1}B'.format(cpu_str, mem_str))
# 				time.sleep(self.interval)
# 			except Exception as e:
# 				self.log_print(self.log_obj, e)
#
# 	def stop(self):
# 		self.thread_stop = True
# 		self.log_print(self.log_obj, '[MonitorThread].stop...')




plugins = [{u'is_default': u'', u'cg_soft_name': u'houdini 16', u'config_id': u'5962', u'plugin_name': u''},
		   {u'is_default': u'', u'cg_soft_name': u'houdini 17', u'config_id': u'58977', u'plugin_name': u''}]

print(type(plugins))
default_plugin = [i for i in plugins if "is_default" in i if i["is_default"] == '1']
print(default_plugin)