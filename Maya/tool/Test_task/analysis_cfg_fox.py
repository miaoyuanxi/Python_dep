# -*- coding: utf-8 -*-
import json
import os
import re
class analysisCfg():
    def __init__(self,platform,taskID,userID):
        self.platform = platform
        self.taskID =taskID
        self.userID = userID
        # delfix = re.findall('^\d?\D', taskID)
        # if delfix:
        #     taskID = taskID.replace(delfix[0], '')
        self.taskID = re.sub('^\d?\D', '', taskID)

        self.k_jsonerror = False

        self.platform_address = {'W2rb':r'\\10.60.100.101','W9rb':r'\\10.80.100.101','GPUrb':r'\\10.90.100.101'}

        # cfg_jsonPath = r'D:\Work\fox\cfg\task.json'
        # sys_jsonPath = r'D:\Work\fox\sys_cfg\system.json'
        #
        # self.k_cfg_json = json.loads(open(cfg_jsonPath).read())
        # self.k_sys_json = json.loads(open(sys_jsonPath).read())


        userID_up =''
        try:
            if int(userID[-3:]) >= 500:
                userID_up = str(int(userID) - int(userID[-3:]) + 500)
            else:
                userID_up = str(int(userID) - int(userID[-3:]))
        except Exception as e:
            print (e)

        cfg_jsonPath = os.path.join(self.platform_address[platform],'render_p','config',userID_up,userID,taskID,'cfg','task.json')
        sys_jsonPath = os.path.join(self.platform_address[platform],'render_p','config',userID_up,userID,taskID,'sys_cfg','system.json')
        cfg_jsonPath = os.path.normpath(cfg_jsonPath)
        sys_jsonPath = os.path.normpath(sys_jsonPath)
        print (cfg_jsonPath)

        if os.path.exists(cfg_jsonPath) and os.path.exists(sys_jsonPath):

            self.k_cfg_json = json.loads(open(cfg_jsonPath).read())
            self.k_sys_json = json.loads(open(sys_jsonPath).read())

        else:self.k_jsonerror = True

        self.function_path = os.path.join(self.platform_address[platform],'render_p','script','CG','Maya','function')
        self.script_path   = os.path.join(self.platform_address[platform],'render_p','script','CG','Maya','script')

        self.C_function_path = os.path.join(self.platform_address[platform], 'render_p', 'script', 'User', userID,'CG','Maya','function')
        self.C_script_path   = os.path.join(self.platform_address[platform], 'render_p', 'script', 'User', userID, 'CG', 'Maya', 'function')


    def analysisPlugins(self):
        """return maya插件 (字典格式)"""
        k_plugins = {}
        k_plugins = (self.k_cfg_json['software_config']['plugins'] if self.k_cfg_json['software_config']['plugins'] else '')
        return k_plugins

    def analysisSoft(self):
        """return maya版本"""
        k_mayaver = ''
        if self.k_cfg_json['software_config']['cg_name'].lower() == 'maya':
            k_mayaver = self.k_cfg_json['software_config']['cg_version']
        else : k_mayaver = 'It is not maya task!!!'
        return k_mayaver

    def analysisMapping(self):
        """renturn 映射盘符"""
        k_mapping = {}
        k_mapping = (self.k_cfg_json['mnt_map'] if self.k_cfg_json['mnt_map'] else '')
        #B盘路径

        if 'plugin_path' in self.k_sys_json['system_info']['common']:
            k_Bpath = self.k_sys_json['system_info']['common']['plugin_path']
        elif 'plugin_path_list' in self.k_sys_json['system_info']['common']:
            k_Bpath = self.k_sys_json['system_info']['common']['plugin_path_list'][0]

        k_pluginPath = {'B:':k_Bpath}
        k_mapping.update(k_pluginPath)
        return k_mapping

    def analysisPath(self):
        """return 数据为 1 = maya文件地址, 2=图片输出地址,3=用户自定义文件夹,4=prerender文件夹,5=B盘路径"""

        if 'common' in self.k_sys_json['system_info']:
            k_path = self.k_sys_json['system_info']['common']
        else:print('system.josn hasnot common key')
        #maya文件夹路径
        if 'input_cg_file' in self.k_sys_json['system_info']['common']:
            k_input_file = self.k_sys_json['system_info']['common']['input_cg_file']
            k_input_filePath = os.path.normpath(os.path.dirname(k_input_file))
        #输出文件夹路径
        if 'output_user_path' in self.k_sys_json['system_info']['common']:
            k_user_outputPath = self.k_sys_json['system_info']['common']['output_user_path']
            k_user_outputPath = os.path.normpath(k_user_outputPath)

        #B盘路径
        if 'plugin_path' in self.k_sys_json['system_info']['common']:
            self.B_plugin_path = self.k_sys_json['system_info']['common']['plugin_path']
            self.B_plugin_path = os.path.normpath(self.B_plugin_path)
        elif 'plugin_path_list' in self.k_sys_json['system_info']['common']:
            self.B_plugin_path = self.k_sys_json['system_info']['common']['plugin_path_list'][0]
            self.B_plugin_path = os.path.normpath(self.B_plugin_path)
        #自定义路径
        customfile_Path = os.path.normpath(os.path.join(self.B_plugin_path, 'config_files',self.userID))

        #prerender路径
        C_prerender_path = self.C_script_path


        return (k_input_filePath,k_user_outputPath,customfile_Path,C_prerender_path,self.B_plugin_path)




if __name__ == '__main__':
    a = analysisCfg('W2rb', '111', '1863567')
    print(a.analysisPath())