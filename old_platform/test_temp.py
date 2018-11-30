#coding=utf-8
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


class RvOs(object):
	is_win = 0
	is_linux = 0
	is_mac = 0
	
	if sys.platform.startswith("win"):
		os_type = "win"
		is_win = 1
		# add search path for wmic.exe
		os.environ["path"] += ";C:/WINDOWS/system32/wbem"
	elif sys.platform.startswith("linux"):
		os_type = "linux"
		is_linux = 1
	else:
		os_type = "mac"
		is_mac = 1
	
	@staticmethod
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
	
	@staticmethod
	def str_to_unicode(encode_str):
		if isinstance(encode_str, unicode):
			return encode_str
		else:
			code = RvOs.get_encode(encode_str)
			return encode_str.decode(code)
	
	@staticmethod
	def get_windows_mapping():
		if RvOs.is_win:
			networks = {}
			locals = []
			all = []
			
			net_use = dict([re.findall(r'.+ ([a-z]:) +(.+)', i.strip(), re.I)[0]
							for i in RvOs.run_command('net use')
							if i.strip() if re.findall(r'.+ ([a-z]:) +(.+)',
													   i.strip(), re.I)])
			for i in net_use:
				net_use[i] = net_use[i].replace("Microsoft Windows Network",
												"").strip()
			
			for i in RvOs.run_command('wmic logicaldisk get deviceid,drivetype,providername'):
				if i.strip():
					# a = re.findall(r'([a-z]:) +(\d) +(.+)?', i.strip(), re.I)
					# print a
					info = i.split()
					if info[1] == "4":
						if len(info) == 3:
							if re.findall(r'^[\w _\-.:()\\/$]+$', info[2], re.I):
								networks[info[0]] = info[2].replace("\\", "/")
							else:
								networks[info[0]] = None
							all.append(info[0])
						else:
							if info[0] in net_use:
								if os.path.exists(net_use[info[0]]):
									if re.findall(r'^[\w _\-.:()\\/$]+$', net_use[info[0]], re.I):
										networks[info[0]] = net_use[info[0]].replace("\\", "/")
									else:
										networks[info[0]] = None
									all.append(info[0])
								else:
									# Don't know why the drive is not exists when using python to check.
									# Is this a network issue?
									# Can not reproduce this issue manually.
									print "%s is not exists" % (info[0])
									networks[info[0]] = None
									all.append(info[0])
							else:
								networks[info[0]] = None
								all.append(info[0])
					
					elif info[1] in ["3", "2"]:
						if info[0] in server_config["forbidden_drives"]:
							locals.append(info[0])
						else:
							networks[info[0]] = None
						all.append(info[0])
		
		return (locals, networks, all)
	
	@staticmethod
	def run_command(cmd, ignore_error=None, shell=0):
		startupinfo = subprocess.STARTUPINFO()
		startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
		startupinfo.wShowWindow = _subprocess.SW_HIDE
		
		p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
							 stderr=subprocess.STDOUT, startupinfo=startupinfo,
							 shell=shell)
		
		while 1:
			# returns None while subprocess is running
			return_code = p.poll()
			# if return_code == 0:
			#     break
			if return_code == 1:
				if ignore_error == 1:
					break
				else:
					raise Exception(cmd + " was terminated for some reason.")
			elif return_code != None and return_code != 0:
				if ignore_error == 1:
					break
				else:
					print "exit return code is: " + str(return_code)
					raise Exception(cmd + " was crashed for some reason.")
			line = p.stdout.readline()
			if not line:
				break
			yield line
	
	@staticmethod
	def get_process_list(name):
		process_list = []
		for i in RvOs.run_command("wmic process where Caption=\"%s\" get processid" % (name)):
			if i.strip() and i.strip() not in ["ProcessId", "No Instance(s) Available."]:
				process_list.append(int(i.strip()))
		
		return process_list
	
	@staticmethod
	def get_desktop_app():
		app_names = ["qrenderbus.exe"]
		for i in app_names:
			process = RvOs.get_process_path(i)
			if process:
				return process[0]
	
	@staticmethod
	def get_rendercmd_exe():
		return os.path.join(RvOs.get_app_config()["installdir"], "rendercmd.exe")
	
	@staticmethod
	def get_app_config():
		env_ini = os.path.join(os.environ["appdata"], r"RenderBus\local\env.ini")
		
		config = open(env_ini).readlines()
		config = dict([[j.strip() for j in i.split("=")] for i in config if "=" in i])
		return config
	
	@staticmethod
	def get_projects():
		cmd = RvOs.get_rendercmd_exe()
		for i in RvOs.run_command("\"%s\" -getproject" % (cmd)):
			return eval(i)
	
	@staticmethod
	def get_process_path(name):
		process_list = []
		for i in RvOs.run_command("wmic process where name=\"%s\" get ExecutablePath" % (name)):
			if i.strip() and i.strip() not in ["ExecutablePath", "No Instance(s) Available."]:
				process_list.append(i.strip())
		
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
			# os.kill is Available from python2.7, need another method.
			# os.kill(i, 9)
			if RvOs.is_win:
				os.system("taskkill /f /t /pid %s" % (i))
			# task_kill_exe=os.path.join(RvOs.get_app_config()["installdir"], "taskkill.exe")
			# subprocess.Popen(r'"'+task_kill_exe+'" /f /t /pid %s' % (i))
	
	@staticmethod
	def timeout_command(command, timeout):
		startupinfo = subprocess.STARTUPINFO()
		startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
		startupinfo.wShowWindow = _subprocess.SW_HIDE
		
		start = time.time()
		process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
								   stderr=subprocess.PIPE, startupinfo=startupinfo, shell=False)
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
	
	@staticmethod
	def which(exe):
		if RvOs.is_win:
			cmd = "where " + exe
			print "execute: " + cmd
			for i in RvOs.run_command(cmd):
				print i


locals, networks, all = RvOs.get_windows_mapping()
print networks