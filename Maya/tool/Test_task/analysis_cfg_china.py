# -*- coding: utf-8 -*-
import json
import os
import re
class analysisCfg():
    def __init__(self,platform,taskID,userID):
        self.platform = platform
        self.taskID =taskID
        self.userID = userID

        self.render_mode = ''
        self.server_info = ''

        # delfix = re.findall('^\d?\D', taskID)
        # if delfix:
        #     taskID = taskID.replace(delfix[0], '')
        self.taskID = re.sub('^\d?\D','',self.taskID)

        self.k_jsonerror = False

        self.platform_address = {'c_W2rb':r'\\10.60.100.101','c_W3rb':r'\\10.30.100.102',\
                            'c_W4rb':r'\\10.40.100.101','c_W9rb':r'\\10.80.100.101',\
                            'c_GPUrb':r'\\10.90.100.101'}




        self.userID_up =''
        try:
            if int(userID[-3:]) >= 500:
                self.userID_up = str(int(userID) - int(userID[-3:]) + 500)
            else:
                self.userID_up = str(int(userID) - int(userID[-3:]))
        except Exception as e:
            print (e)

        #客户端
        #// 10.60.100.101 / d / ninputdata5 / 10572267 / temp\server.cfg
        #\\10.60.100.101\p5\temp\10572267_render\cfg

        #网页端
        #\\10.60.100.101\p5\config\1163000\1163153\10583609
        #\\10.60.100.101\p5\temp\10583609_render\cfg

        py_cfg_Path = os.path.join(self.platform_address[platform],'p5','temp','%s_render'%self.taskID,'cfg' )
        print('client cfg path is %s' %py_cfg_Path)
        ninputdata5_temp = os.path.join(self.platform_address[platform],'d','ninputdata5',self.taskID,'temp' )
        print('client cfg path is %s' %ninputdata5_temp)

        web_cfg_Path = os.path.join(self.platform_address[platform],'p5','config',self.userID_up,self.userID,self.taskID)
        print('web cfg path is %s' %web_cfg_Path)
        #py_cfg_Path = r'D:\Work\china_client\cfg'
        # py_cfg_Path = r'D:\Work\china_web\cfg'
        # web_cfg_Path = r'D:\Work\china_web\10583609'

        py_cfg_p      = os.path.join(py_cfg_Path,'py.cfg')
        #客户端配置文件路径
        plugins_cfg_p = os.path.join(ninputdata5_temp,'plugins.cfg')
        server_cfg_p  = os.path.join(ninputdata5_temp,'server.cfg')
        render_cfg_p = os.path.join(ninputdata5_temp, 'render.cfg')
        #网页端配置文件路径
        web_plugins_json_p = os.path.join(web_cfg_Path,'plugins.json')
        web_render_json_p = os.path.join(web_cfg_Path, 'render.json')

        if os.path.exists(py_cfg_p) and os.path.exists(plugins_cfg_p) and os.path.exists(server_cfg_p) and os.path.exists(render_cfg_p):
            #客户端
            self.render_mode = 'client'
            # 读取配置文件
            self.server_info  = eval(open(server_cfg_p).read())
            self.plugins_info = eval(open(plugins_cfg_p).read())

            result = {}
            with open(py_cfg_p,"r") as f:
                while 1:
                    line = f.readline()
                    if "=" in line:
                        line_split = line.split("=")
                        result[line_split[0].strip()] = line_split[1].strip()
                    else:
                        break
                self.py_info = result

            render_result = {}
            with open(render_cfg_p,"r") as f:
                while 1:
                    line = f.readline()
                    if "=" in line:
                        line_split = line.split("=")
                        render_result[line_split[0].strip()] = line_split[1].strip()
                    if ">>" in line:
                        break
                    if "[delete]" in line:
                        break
                self.render_info = render_result



        elif os.path.exists(py_cfg_p) and os.path.exists(web_plugins_json_p) and os.path.exists(web_render_json_p):
            #网页端
            self.render_mode = 'web'
            #读取配置文件
            self.plugins_info = json.loads(open(web_plugins_json_p).read())
            self.web_render_info  = json.loads(open(web_render_json_p).read())

            result = {}
            with open(py_cfg_p,"r") as f:
                while 1:
                    line = f.readline()
                    if "=" in line:
                        line_split = line.split("=")
                        result[line_split[0].strip()] = line_split[1].strip()
                    else:
                        break
                self.py_info = result



        else:self.k_jsonerror = True


        self.function_path = os.path.join(self.platform_address[platform],'o5','py','model','function')



    def analysisPlugins(self):
        """return maya插件 (字典格式)"""
        k_plugins = {}
        k_plugins = (self.plugins_info['plugins'] if self.plugins_info['plugins'] else '')
        return k_plugins

    def analysisSoft(self):
        """return maya版本"""
        k_mayaver = ''
        if self.plugins_info['renderSoftware'].lower() == 'maya':
            k_mayaver = self.plugins_info['softwareVer']
        else : k_mayaver = 'It is not maya task!!!'
        return k_mayaver

    def analysisMapping(self):
        """renturn 映射盘符"""
        k_path = self.analysisPath()

        k_mapping = {}
        #客户端
        if self.render_mode == 'client':
            print('client mapping analysis')
            if 'mountFrom' in self.render_info:
                k_mountFrom = eval(self.render_info['mountFrom'])
                for diver_path,key_diver in k_mountFrom.items():
                    print(diver_path,key_diver)
                    kexp = r'^(\w:)'
                    #匹配字母开头
                    if re.findall(kexp,str(key_diver)):
                        #替换掉开头的字符
                        kstart = r'^(/)'
                        k_mountsp = re.sub(kstart, '',diver_path)
                        print('k_mountsp =%s' %k_mountsp)
                        netpath = os.path.join(self.storage_path,k_mountsp)
                        print('netpath =%s' %netpath)
                        netdict = {key_diver:os.path.normpath(netpath)}

                        k_mapping.update(netdict)

            B_plugin_path = {'B:':self.B_plugin_path}
            k_mapping.update(B_plugin_path)

        #网页端
        elif self.render_mode == 'web':
            if 'mntMap' in self.web_render_info:
                for key_diver in self.web_render_info['mntMap']:
                    kexp = r'^(\w:)'
                    if re.findall(kexp, str(key_diver)):
                        netpath = os.path.normpath(self.web_render_info['mntMap'][key_diver])
                        netdict = {key_diver:netpath}
                        k_mapping.update(netdict)


        return k_mapping

    def analysisPath(self):
        """return 数据为 1 = maya文件地址, 2=图片输出地址,3=用户自定义文件夹,4=prerender文件夹,5=B盘路径"""

        # B盘插件路径
        self.B_plugin_path = ''
        if 'PLUGINPATHLIST' in self.py_info:
            B_plugin_paths = eval(self.py_info['PLUGINPATHLIST'])
            self.B_plugin_path = os.path.normpath(B_plugin_paths[0])
        elif 'PLUGINPATH' in self.py_info:
            self.B_plugin_path = os.path.normpath(eval(self.py_info['PLUGINPATH']))
        else:
            print('B plugins path error ----!!!!')

        # RayvisionCustomConfig 路径
        customfile_Path = os.path.join(self.B_plugin_path, 'custom_config', self.userID)
        # prerender路径
        C_prerender_path = os.path.join(self.platform_address[self.platform], 'o5', 'py', 'model', 'user', self.userID)



        if self.render_mode == 'client':

            #图片输出路径
            k_user_outputPath = eval(self.py_info['G_PATH_USER_OUTPUT'])

            #客户的存储路径
            k_input_proj = eval(self.py_info['G_PATH_INPUTPROJECT'])
            #获取存储路径 d\inputdata5
            self.storage_path = ''
            if self.userID_up in k_input_proj and self.userID in k_input_proj:
                self.storage_path = os.path.normpath(k_input_proj.split(self.userID_up)[0])
            else: print('Get storage path error ----!!!!')

            k_input_file = eval(self.py_info['G_PATH_INPUTFILE'])


            #组合出 input的 maya文件路径
            k_filePath = os.path.normpath(os.path.dirname(k_input_file))
            k_exp = r"^\w(:)"
            if re.findall(k_exp,k_filePath):
                g_input_file = re.sub(k_exp,k_filePath[0],k_filePath)
                k_input_filePath = os.path.join(k_input_proj,g_input_file)

        elif self.render_mode == 'web':

            #获取 k_input_filePath
            if 'common' in self.web_render_info:
                k_input_file = ''
                if 'inputCgFile' in self.web_render_info['common']:
                    k_input_file = self.web_render_info['common']['inputCgFile']
                elif 'cgFile' in self.web_render_info['common']:
                    k_input_file = self.web_render_info['common']['cgFile']
                else:print('Get input file path error ----!!!!')

                k_input_filePath = os.path.dirname(k_input_file)

            #获取k_user_outputPath
            if 'common' in self.web_render_info:
                if 'userOutputPath' in self.web_render_info['common']:
                    k_output_file = self.web_render_info['common']['userOutputPath']
                    k_user_outputPath = os.path.dirname(k_output_file)
                else:print('Get output file path error ----!!!!')



        return (k_input_filePath,k_user_outputPath,customfile_Path,C_prerender_path,self.B_plugin_path)


if __name__ == '__main__':
    a=analysisCfg('c_W2rb','111','1863567')
    a.analysisMapping()
