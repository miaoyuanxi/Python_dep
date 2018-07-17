#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
#import imghdr
import sys
import platform

from CommonUtil import RBCommon as CLASS_COMMON_UTIL


class RBFrameChecker(object):
    
    @classmethod
    def get_file_size(self,local_path,server_path,my_log=None):
        local_path = local_path.replace('\\','/')
        server_path = server_path.replace('\\','/')
        local_path = CLASS_COMMON_UTIL.bytes_to_str(local_path)
        server_path = CLASS_COMMON_UTIL.bytes_to_str(server_path)
        check_file = []
        if os.path.exists(server_path):
            for root, dirs, files in os.walk(local_path):
                for file_name in files:
                    if file_name.split('.')[-1]!='db':
                        local_files = os.path.join(root, file_name).replace('\\', '/')
                        local_file_size = os.path.getsize(local_files)
                        server_files = server_path+local_files.split(local_path)[-1].replace('\\','/')
                        if os.path.exists(server_files):
                            server_file_size = os.path.getsize(server_files)
                            if float(local_file_size)/1024>0:
                                if local_file_size != server_file_size:
                                    CLASS_COMMON_UTIL.log_print(my_log,'Not the same as the file size：\n'+'    local: \"'+str(local_files)+'\"      size:'+str(local_file_size)+'\n    server: \"'+str(server_files)+'\"      size:'+str(server_file_size)+'\n')
                                else:
                                    #print 'nuke____',local_files
                                    check_file.append(local_files)
                            else:
                                CLASS_COMMON_UTIL.log_print(my_log,'This file \"' + local_files + '\" size abnormal !\n')
                        else:
                            CLASS_COMMON_UTIL.log_print(my_log,'This file \"'+local_files+'\" not in server path !\n')
        return check_file
        # self.check_texture(nuke_path, check_file)
    
    @classmethod
    def check_texture(self,nuke_path,texture_file,my_log=None):
        run_path = nuke_path
        run_path = CLASS_COMMON_UTIL.bytes_to_str(run_path)
        #print texture_file
        #print  '________',run_path
        os.environ['HFS'] = run_path
        _PATH_ORG = os.environ.get('PATH')
        os.environ['PATH'] = (_PATH_ORG if _PATH_ORG else '') + r';' + run_path
        #print os.environ['PATH']
        lib_path = '%s/lib' % (run_path)
        # _PATH_New = os.environ.get('PATH')
        # print '_PATH_New = ' + _PATH_New
        site_path = '%s/lib/site-packages' % (run_path)
        if lib_path not in sys.path:
            sys.path.append(lib_path)
        if site_path not in sys.path:
            sys.path.append(site_path)

        import nuke

        for i in texture_file :
            i = i.replace('\\','/')
            texture_type = ['avi', 'eps', 'dds', 'bmp', 'vrimg']
            if i.split('.')[-1] not in texture_type:
                #print i
                readtex = nuke.nodes.Read(file=i.encode('utf-8'))
                if readtex.metadata() == {}:
                    CLASS_COMMON_UTIL.log_print(my_log,'File is damaged'+i)
                else:
                    # print u'ok__________'+i
                    pass
            else:
                CLASS_COMMON_UTIL.log_print(my_log,' This file does not support Nuke do check'+i)
                
    @classmethod
    def main(self,local_path,server_path,my_log=None):
        nuke_path = r'C:/Program Files/Nuke10.0v4'
        check_file = self.get_file_size(local_path,server_path,my_log)
        if not check_file:
            CLASS_COMMON_UTIL.error_exit_log(my_log,'output have no file!')
        if platform.system() == 'Linux':
            pass
        else:
            if os.path.exists(nuke_path):
                try:
                    self.check_texture(nuke_path,check_file,my_log)
                except Exception as e:
                    CLASS_COMMON_UTIL.log_print(my_log,e)

if __name__ == '__main__':
    # nuke_path =r'C:/Program Files/Nuke10.0v4'
    # CLASS_FRAME_CHECKER = RBFrameChecker()
    # CLASS_FRAME_CHECKER.get_file_size(r'G:\\BitmapCheck',r'//172.16.10.88/test/WF/BitmapCheck')
    RBFrameChecker.main(r'G:\\BitmapCheck',r'//172.16.10.88/test/WF/BitmapCheck')
