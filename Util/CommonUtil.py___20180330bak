#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import shutil
import sys
import time
import codecs
import json
import stat
import socket
import re
import platform
import uuid
# from kafka import KafkaProducer
# from kafka.errors import KafkaError

# class FileHandle

class RBCommon(object):
    
    @classmethod 
    def log_print(self,my_log,log_str):
        if my_log==None:
            print(log_str)
        else:
            my_log.info(log_str)
            
    @classmethod    
    def del_net_use(self):
    
        try:
            self.cmd("net use * /del /y",my_shell = True)
        except:
            pass
            
    @classmethod        
    def del_subst(self):
        def del_subst_callback(my_popen,my_log):
            while my_popen.poll()==None:
                result_line = my_popen.stdout.readline().strip()
                result_line = result_line.decode(sys.getfilesystemencoding())
                print(result_line)
                if result_line!='' and (':\:' in result_line):
                    substDriver= result_line[0:2]
                    substDriverList.append(substDriver)
            
            for substDriver in substDriverList:
                print(substDriver)
                delSubstCmd='subst '+substDriver+ ' /d'
                print(delSubstCmd)
                try:
                    os.system(delSubstCmd)
                except:
                    pass
        
        substDriverList=[]
        self.cmd('subst',my_log=None,continue_on_error=False,my_shell=False,callback_func=del_subst_callback)
        #cmdp=subprocess.Popen('subst',stdin = subprocess.PIPE,stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = False)
        #cmdp.stdin.write('3/n')
        #cmdp.stdin.write('4/n')
        
                
    @classmethod            
    def cmd____abort(self,cmd_str,my_log=None,try_count=1,continue_on_error=False,my_shell=False):#continue_on_error=true-->not exit ; continue_on_error=false--> exit 
        print(str(continue_on_error)+'--->>>'+str(my_shell))
        if my_log!=None:
            my_log.info('cmd...'+cmd_str)
        #self.G_PROCESS_LOG.info('try3...')
        l=0
        resultStr=''
        resultCode=0
        while l < try_count:
            l=l+1
            cmdp=subprocess.Popen(cmd_str,stdin = subprocess.PIPE,stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = my_shell)
            cmdp.stdin.write('3/n')
            cmdp.stdin.write('4/n')
            while cmdp.poll()==None:
                resultLine = cmdp.stdout.readline().strip()
                resultLine = resultLine.decode(sys.getfilesystemencoding())
                if resultLine!='' and my_log!=None:
                    my_log.info(resultLine)
                
            resultStr = cmdp.stdout.read()
            resultStr = resultStr.decode(sys.getfilesystemencoding())
            resultCode = cmdp.returncode
            if resultCode==0:
                break
            else:
                time.sleep(1)
        if my_log!=None:
            my_log.info('resultStr...'+resultStr)
            my_log.info('resultCode...'+str(resultCode))
        
        if not continue_on_error:
            if resultCode!=0:
                sys.exit(resultCode)
        return resultCode,resultStr
        
        
    @classmethod            
    def cmd(self,cmd_str,my_log=None,try_count=1,continue_on_error=False,my_shell=False,callback_func=None):#continue_on_error=true-->not exit ; continue_on_error=false--> exit 
        print(str(continue_on_error)+'--->>>'+str(my_shell))
        cmd_str = self.bytes_to_str(cmd_str)
        if my_log!=None:
            my_log.info('cmd...'+cmd_str)
        #self.G_PROCESS_LOG.info('try3...')
        l=0
        resultStr=''
        resultCode=0
        while l < try_count:
            l=l+1
            my_popen=subprocess.Popen(cmd_str,stdin = subprocess.PIPE,stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = my_shell)
            my_popen.stdin.write(b'3/n')
            my_popen.stdin.write(b'4/n')
            
            if callback_func==None:
                while my_popen.poll()==None:
                    result_line = my_popen.stdout.readline().strip()
                    result_line = result_line.decode(sys.getfilesystemencoding())
                    if result_line!='' and my_log!=None:
                        my_log.info(result_line)
            else:
                callback_func(my_popen,my_log)
                    
                
            resultStr = my_popen.stdout.read()
            resultStr = resultStr.decode(sys.getfilesystemencoding())
            resultCode = my_popen.returncode
            if resultCode==0:
                break
            else:
                time.sleep(1)
        if my_log!=None:
            my_log.info('resultStr...'+resultStr)
            my_log.info('resultCode...'+str(resultCode))
        
        if not continue_on_error:         
            if resultCode!=0:
                sys.exit(resultCode)
        return resultCode,resultStr
        
    @classmethod
    def cmd_python3(self,cmd_str,my_log=None):
        #if callback_func == None and my_shell == False
        python_path = r'c:\python34\python.exe'
        script_path = 'C:\\script\\new_py\\Util\\RunCmd.py'
        run_cmd_txt = 'C:\\script\\new_py\\RunCmd.txt'
        
        cmd_str_u = self.bytes_to_str(cmd_str)
        if my_log != None:
            my_log.info(cmd_str_u)
            
        #write cmd to RunCmd.txt
        f1 = codecs.open(run_cmd_txt,'w','utf-8')
        f1.write(cmd_str_u)
        f1.close()
        
        cmd_p3=r'%s "%s" "%s"' % (python_path,script_path,run_cmd_txt)
        self.cmd(cmd_p3,my_log=my_log)
         
    @classmethod
    def python_copy(self,copy_source,copy_target):
        copy_source=os.path.normpath(copy_source)
        copy_target=os.path.normpath(copy_target)
        copy_source = self.bytes_to_str(copy_source)
        copy_target = self.bytes_to_str(copy_target)
        try:
            if not os.path.exists(copy_target):
                os.makedirs(copy_target)
            if  os.path.isdir(copy_source):
                self.copy_folder(copy_source,copy_target)
            else:
                shutil.copy(copy_source,copy_target)
            return True
        except Exception as e:
            print(e)
            return False

    @classmethod
    def copy_folder(self,pyFolder,to):
        if not os.path.exists(to):
            os.makedirs(to)
        if os.path.exists(pyFolder):
            for root, dirs, files in os.walk(pyFolder):
                for dirname in  dirs:
                    tdir=os.path.join(root,dirname)
                    if not os.path.exists(tdir):
                        os.makedirs(tdir)
                for i in range (0, files.__len__()):
                    sf = os.path.join(root, files[i])
                    folder=to+root[len(pyFolder):len(root)]+"/"
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    shutil.copy(sf,folder)
    
    @classmethod
    def python_move(self, move_source, move_target, continue_on_error=False, my_shell=False):
        move_source = os.path.normpath(move_source)
        move_target = os.path.normpath(move_target)
        move_source = self.bytes_to_str(move_source)
        move_target = self.bytes_to_str(move_target)
        try:
            if not os.path.exists(move_target):
                os.makedirs(move_target)
            if os.path.isdir(move_source):
                self.move_folder(move_source, move_target)
            else:
                shutil.move(move_source, move_target)
            return True
        except Exception as e:
            print(e)
            return False

    @classmethod
    def move_folder(self, src_folder, to):
        if not os.path.exists(to):
            os.makedirs(to)
        if os.path.exists(src_folder):
            name_list = os.listdir(src_folder)
            print(name_list)
            for name in name_list:
                src = os.path.join(src_folder,name)
                shutil.move(src, to)
    
    @classmethod                
    def error_exit_log(self,my_log,log_str,exit_code=-1,is_exit=True):
        my_log.info('\r\n\r\n---------------------------------[error]---------------------------------')
        my_log.info(log_str)
        my_log.info('-------------------------------------------------------------------------\r\n')
        if is_exit:
            sys.exit(exit_code)
    
    @classmethod   
    def read_random_file(self,file):
        code_list=['utf-8','gbk',sys.getfilesystemencoding(),'utf-16']
        file_list=[]
        for code in code_list:
            try:
                with open(file, 'r', encoding=code) as file_obj:
                    file_list=file_obj.readlines()
                break
            except:
                pass
        return file_list
    
    @classmethod
    def read_file(self,path1,my_code='UTF-8',my_mode='r'):
        if os.path.exists(path1):
            file_object=codecs.open(path1, my_mode, my_code)
            line=file_object.readlines()
            file_object.close()
            for r in line:
                print(r)
            return line
        pass
        
    @classmethod     
    def write_file(self,file_content,my_file,my_code='UTF-8',my_mode='w'):
        
        if isinstance(file_content,str):
            file_content_u = self.bytes_to_str(file_content)
            fl=codecs.open(my_file, my_mode, my_code)
            fl.write(file_content_u)
            fl.close()
            return True
        elif isinstance(file_content,(list,tuple)):
            fl=codecs.open(my_file, my_mode, my_code)
            for line in file_content:
                fl.write(line+'\r\n')
            fl.close()
            return True
        else:
            return False

    @classmethod 
    def exit_tips(self,tips_str,tips_file,config_path,my_log):
        self.write_file(tips_str,tips_file)
        self.python_copy(os.path.normpath(tips_file),os.path.normpath(config_path))
        if my_log!=None:
            self.error_exit_log(my_log,tips_str,is_exit=False)
            
        sys.exit(0)
    
    @classmethod
    def bytes_to_str(self,str1,str_decode = 'default'):  
        if not isinstance(str1,str):
            try:
                if str_decode != 'default':
                    str1 = str1.decode(str_decode.lower())
                else:
                    try:
                        str1 = str1.decode('utf-8')                        
                    except:
                        try:
                            str1 = str1.decode('gbk')
                        except:                            
                            str1 = str1.decode(sys.getfilesystemencoding())
            except Exception as e:
                print('[err]bytes_to_str:decode %s to str failed' % (str1))
                print(e)
        return str1
    
    @classmethod
    def str_to_bytes(self,str1,str_encode = 'system'):  
        if isinstance(str1,str):
            try:
                if str_encode.lower() == 'system':
                    str1=str1.encode(sys.getfilesystemencoding())
                elif str_encode.lower() == 'utf-8':
                    str1 = str1.encode('utf-8')
                elif str_encode.lower() == 'gbk':
                    str1 = str1.encode('gbk')
                else:
                    str1 = str1.encode(str_encode)
            except Exception as e:
                print('[err]str_to_bytes:encode %s to %s failed' % (str1,str_encode))
                print(e)
        else:
            print('%s is not str ' % (str1))
        return str1
    

 
    '''
        mount路径函数:
        {
            "/output":{
                "path":"//10.60.100.102/d/inputdata5/962500/962712",
                "username":"",
                "password":""
            }
        }
    '''
    @classmethod
    def mount_path(self,dict={}):
        print('mount paths :')
        for key in list(dict.keys()):
            key = os.path.normpath(key)
            if not os.path.exists(key):
                os.makedirs(key)
            path = dict[key]['path']
            if 'username' in dict[key] and 'password' in dict[key]:
                username = dict[key]['username']
                password = dict[key]['password']
                mount_cmd='mount -t auto -o username=%s,password=%s,codepage=936,iocharset=gb2312 "%s" "%s" ' % (username,password,path,key)
            else:
                mount_cmd='mount -t auto -o codepage=936,iocharset=gb2312 "%s" "%s"' % (path,key)
            try:
                self.cmd(mount_cmd)  
            except Exception as e:
                print('mount path failed "%s" --> "%s"' % (path,key))
                print(e)
    
    @classmethod
    def make_dirs(self,dir_list=[]):
        if len(dir_list)>0:
            for dir in dir_list:
                if not os.path.exists(dir):
                    os.makedirs(dir)
    
    #use when shutil.rmtree can't delete file
    @classmethod                
    def remove_readonly(self,func, path, excinfo):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
            print('file can\'t remove:%s' % (path))
            print(e)
        
    @classmethod    
    def get_system_version(self):
        return platform.platform()
        
    @classmethod    
    def get_system(self):
        return platform.system()
    
    @classmethod    
    def get_computer_mac(self):
    
        mac=uuid.UUID(int = uuid.getnode()).hex[-12:] 
        return ":".join([mac[e:e+2] for e in range(0,11,2)])
    
    @classmethod    
    def get_computer_hostname(self):
         return socket.gethostname()
         
    @classmethod      
    def get_computer_ip(self):
        host_name = self.get_computer_hostname()
        ip_str = socket.gethostbyname(host_name)
        return ip_str
    
    @classmethod      
    def write_hosts(self,server_dict):
        '''
        example
        {"192.168.0.88":["server1","storage.renderbus.com"],"10.60.100.1.102":["storage.renderbus.com"]}
        '''
        ip_list=[]
        server_list=[]
        for key_ip,value_server in list(server_dict.items()):
            print(key_ip)
            ip_list.append(key_ip)
            server_list.extend(value_server)
        
        host_file=r'C:\WINDOWS\system32\drivers\etc\hosts'
        hosts_list_old=self.read_file(host_file)
        
        hosts_list_new=[]
        for host_line in hosts_list_old:
            if not host_line:
                continue
            host_line=host_line.strip()
            if host_line.startswith('#'):
                hosts_list_new.append(host_line)
                continue
                
            host_line_arr = host_line.split()
            
            if len(host_line_arr)==2:
                print(host_line_arr[0]+'---------->'+host_line_arr[1])
                if host_line_arr[0].strip() in ip_list or host_line_arr[1].strip() in server_list:
                    pass
                else:
                    hosts_list_new.append(host_line)
            else:
                hosts_list_new.append(host_line)
        
        for key_ip,value_server in list(server_dict.items()):        
            for server in value_server:
                hosts_list_new.append(key_ip+'      '+server)
        for line in hosts_list_new:
            print(line)  
        self.write_file(hosts_list_new,host_file)
          
        
        
    @classmethod
    def kill_app_list(self,app_list=[]):
        my_os=self.get_system()
        for app in app_list:
            if  my_os=='Windows':
                cmd_str = r'c:\windows\system32\cmd.exe /c c:\windows\system32\TASKKILL.exe /F /IM %s'%app
            elif my_os=='Linux':
                cmd_str = ''
            self.cmd(cmd_str)
            
            
    @classmethod
    def start_server(self,server_name):
        cmd_str = 'C:\Windows\System32\sc.exe start "'+server_name+'"'
        return self.cmd(cmd_str)
        
    @classmethod
    def stop_server(self,server_name):
        cmd_str = 'C:\Windows\System32\sc.exe stop "'+server_name+'"'
        return self.cmd(cmd_str)
        
    @classmethod
    def query_server(self,server_name):
        find_str= r'C:\Windows\System32\findstr.exe'
        cmd_str = 'C:\Windows\System32\sc.exe query '+server_name+'|'+find_str+' "STATE"' 
        self.cmd(cmd_str)
        
        '''
        check_info = check_popen.stdout.readlines()
        for elm in check_info:
            if "STOPPED" in elm.strip():
                to_install = False
                print elm.strip()
                
            if "RUNNING" in elm.strip():
                predone +=1
                print elm.strip()
                
        '''
         
    
class RBKafka():
    '''
    使用kafka的生产模块
    '''
    def __init__(self):
        print('init............')
    
    @classmethod
    def send_json_data(self, params,kafka_topic):
        try:
            parmas_message = json.dumps(params)  #<type 'str'>
            producer = self.producer
            # producer.send(self.kafkatopic, parmas_message.encode('utf-8'))
            print(parmas_message)
            future = producer.send(kafka_topic, parmas_message.encode('utf-8'))
            try:
                record_metadata = future.get(timeout=10)
                print(record_metadata.topic)
                print(record_metadata.partition)
                print(record_metadata.offset)
            except KafkaError as e:
                print('get data failed')
                print(e)
            # Successful result returns assigned partition and offset
            producer.flush()
        except KafkaError as e:
            print(e)
            
    @classmethod        
    def produce(self,json_data, my_kafka_server, my_kafka_topic):
        flag = False
        j = 0
        self.producer = KafkaProducer(bootstrap_servers = my_kafka_server)
        while (not flag) and (j<3):
            try:
                self.send_json_data(json_data,my_kafka_topic)
                # print params
                flag = True
                print('send info success')
            except Exception as e:
                print(e)
                j += 1
        return flag

if __name__ == '__main__':

    params = {
        "platform":"2",
        "messageKey": "analyze",
        "messageBody": {
            "zone": "1",
            "nodeName": "D174",
            "firstFrame": "409",
            "startTime": "1501646131",
            "smallPic": "frame0663_gezi_0663[-]tga.jpg",
            "endTime": "1501646264",
            "taskId": "11111",
            "jobId": "chentestjob的标识"
        },
        "messageTime": "munu产生该消息的时间",
        "messageId": "11111_005_photon_rendering",
        "platform": "munu节点机标识",
        "restartNumber": "1",
        "customize": "自定义信息"
    }
    params["messageKey"] = "analyze"
    RBKafka.produce(params,"10.60.96.142", 9092, "dev-munu-topic-01")