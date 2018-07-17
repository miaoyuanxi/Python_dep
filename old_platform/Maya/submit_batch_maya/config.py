'''
Creat 
'''
import os,sys
import subprocess
import re,time

class VrayPlugins():
    
    def __init__(self,list):
        self._server_trop = "106096162"
        self._maya_ver = list[0]
        self._vray_ver = list[1]
        self._trop = list[3]
        self._license = list[2] if not list[2]=="" else ("client" if self._trop else "pro")
        self.BaseData()
        self.MakeClientDir()

    def BaseData(self):
        self._plugin_name = 'vray'
        self._b_dir = "B:"
        self._b_dist_path = "%s/plugins/maya" % self._b_dir
        self._plugin_software = "D:/plugins/maya/%s"%self._plugin_name 

    def MakeClientDir(self):
        folders = ["source","software","logs"]
        if os.path.exists("%s/%s"%(self._plugin_software,"software")):
            try:
                subprocess.call("rd /s /q %s"%os.path.abspath("%s/%s"%(self._plugin_software,"software")),shell=True)
            except:
                self.PrintVr("Canot remove the software folder")
        for elm in folders:
            if not os.path.exists("%s/%s"%(self._plugin_software,elm)):
                os.makedirs("%s/%s"%(self._plugin_software,elm))


    def SourceCheck(self,b_path,client_path,disk="client",change=0):
        client_exist = [False,self._license]
        b_exist = [False,self._license]
        ## 1\M & Pro in D disk
        if self._license == "pro":
            pro_source = "vrayformaya_%s_%s_pro.7z" % (self._maya_ver,self._vray_ver) ## goto D serch pro
            if not os.path.exists("%s/%s"%(client_path,pro_source)):                  ## goto b serch pro
                if not os.path.exists("%s/%s"%(b_path,pro_source)):                   ## change type 
                    self._license = "client"
                    client_exist,b_exist,plugM_software = self.SourceCheck(b_path,client_path,disk,change)
                else:
                    plugM_software = pro_source
                    b_exist = [True,self._license]
            else:
                plugM_software = pro_source
                client_exist = [True,self._license]
        elif self._license == "client":
            exprot = "%sM"%self._license if change == 0 else self._license
            plugM_software = "vrayformaya_%s_%s_%s.7z" % (self._maya_ver,self._vray_ver,exprot)
            if not os.path.exists("%s/%s"%(client_path,plugM_software)):              ## goto D serch clientM
                if not os.path.exists("%s/%s"%(b_path,plugM_software)):                   ## change type
                    change +=1
                    if change<2:
                        client_exist,b_exist,plugM_software = self.SourceCheck(b_path,client_path,disk,change)
                else:
                    b_exist = [True,self._license]
            else:
                client_exist = [True,self._license]

        return client_exist,b_exist,plugM_software
        
    def ConfigPlugin(self):
        self.PrintVr("ConfigPlugin proc")
        unztool = "C:/7-Zip"
        unzexe = "%s/7z.exe"%unztool
        if not os.path.exists(unzexe):
            b_unzip = "%s/tools/7-Zip"%self._b_dir
            os.system ("robocopy /e /ns /nc /nfl /ndl /np  %s %s" % (os.path.abspath(b_unzip), os.path.abspath(unztool)))
        
        vray_source = "%s/vrayformaya/source/maya%s" % (self._b_dist_path,self._maya_ver)
        vray_aim = "%s/source" % self._plugin_software
        vray_software_info = self.SourceCheck(vray_source,vray_aim)
        self.PrintVr(vray_software_info)
        copy_source = True if (not vray_software_info[0][0] and vray_software_info[0][1]) else False
        ## whether if it is the same file by getmtime
        if os.path.exists(vray_source):
            if os.path.exists("%s/%s"%(vray_source,vray_software_info[2])):
                if vray_software_info[0][0]:
                    t1 = os.path.getmtime("%s/%s"%(vray_aim,vray_software_info[2]))
                    t2 = os.path.getmtime("%s/%s"%(vray_source,vray_software_info[2]))
                    if t1 !=t2:copy_source = True
                    self.PrintVr("difference source, cp it...")
            else:
                self.PrintVr("This version is not in the source disk,redo the setup.")
                os.system("del /s /q %s"%os.path.abspath("%s/%s"%(vray_aim,vray_software_info[2])))
                vray_software_info = self.SourceCheck(vray_source,vray_aim)
                self.PrintVr(vray_software_info)
                copy_source = True if (not vray_software_info[0][0] and vray_software_info[0][1]) else False

        if self._trop and not self._license=="client":
            self.PrintVr("Cant found this version(cli) ,to check the source for more informations. ")
            sys.exit(001)
        if not vray_software_info[0][0] and not vray_software_info[1][0]:
            self.PrintVr("Cant found this version(All) ,to check the source for more informations. ")
            sys.exit(002)
        if copy_source:
            cp = 0
            while cp < 3:
                self.PrintVr("GET: %s"%vray_software_info[2])
                if os.path.exists("%s/%s"%(vray_source,vray_software_info[2])):
                    copy_log = open("%s/logs/copy_source.txt"%self._plugin_software,"wt")
                    cmds_copy = "copy %s %s" % (os.path.abspath("%s/%s"%(vray_source,vray_software_info[2])),
                                os.path.abspath("%s/%s"%(vray_aim,vray_software_info[2])))
                    #print(cmds_copy)
                    source_copy = subprocess.Popen(cmds_copy,stdout=copy_log,shell=True)
                    source_copy.wait()
                    cp =(cp+1) if not source_copy.returncode == 0 else 5
                    if source_copy.returncode == 0: copy_source = False
                    copy_log.close()
                else:
                    cp = 6
            if cp == 6:
                self.PrintVr('This plugin "%s" version %s is not exist.' % (self._plugin_name,self._vray_ver))
                sys.exit(55)
            elif cp == 3:
                self.PrintVr("Cant cp the source from the B dist.")
                sys.exit(555)
        
        if not copy_source:
            self.PrintVr("Finally: %s/%s"%(vray_aim,vray_software_info[2]))
            unzip_times = 1
            while unzip_times<3:
                cmd_un7z_source = unzexe + " x -y -aos "
                cmd_un7z_source += "%s/%s"%(vray_aim,vray_software_info[2])
                cmd_un7z_source += " -o%s" % ("%s/software/%s_%s"%(self._plugin_software,self._maya_ver,self._vray_ver.replace("","")))
                # print(cmd_un7z_source)
                unzip_log = open("%s/logs/unzip.txt"%self._plugin_software,"wt")
                source_unzip = subprocess.Popen(cmd_un7z_source,stdout=unzip_log,shell=True)
                source_unzip.wait()
                if not source_unzip.returncode == 0:
                    unzip_times +=1
                    os.system("copy %s %s /y" % (os.path.abspath("%s/%s"%(vray_source,vray_software_info[2])),
                                os.path.abspath("%s/%s"%(vray_aim,vray_software_info[2]))))
                elif not os.path.exists("%s/software/%s_%s/maya_root/modules/VRayForMaya.module"%(self._plugin_software,self._maya_ver,self._vray_ver.replace("",""))):
                    unzip_times = 1
                    time.sleep(1)
                else:
                    unzip_times = 3
                unzip_log.close()


    def LicenseMapping(self,app_path):
        server_folder = ''
        if os.path.exists("%s/license/vrlclient.xml"%app_path):
            with open("%s/license/vrlclient.xml"%app_path,"r") as f:
                infos = f.readlines()
                f.close()
            if len(infos):
                hostline = ''
                for elm in infos:
                    if "<Host>" in elm:
                        hostline = elm
                        break
                for elm in re.findall("\d+",hostline):
                    server_folder += elm.strip()
                self.PrintVr("Server check resulte: %s"%server_folder)
        return server_folder
    
    def CopyAllFiles(self,app_folder,lic=0):
        dstDir=r'"C:\Program Files\Autodesk\Maya%s"'%  self._maya_ver
        cmds_maya = "robocopy /e /ns /nc /nfl /ndl /np %s %s" % (os.path.abspath("%s/maya_root"%app_folder), dstDir)
        #print(cmds_maya)
        if not lic:
            maya_root = open("%s/logs/maya_root.txt"%self._plugin_software,"wt")
            source_unzip = subprocess.Popen(cmds_maya,stdout=maya_root,shell=True)
            source_unzip.wait()
            maya_root.close()
        if self._license == "client":
            license_folder = self._server_trop if self._trop else self.LicenseMapping(app_folder)
            if not len(license_folder):license_folder = self._server_trop
            self.PrintVr("Final server used: %s"%license_folder)
            if license_folder=="127001":license_folder="127000001"
            srcDir="%s/vrayformaya/license/%s/vrlclient.xml"%(self._b_dist_path,license_folder)
            dstDir=r'"C:\Program Files\Common Files\ChaosGroup\vrlclient.xml"'
            cmds_xml = "copy %s %s /y" % (os.path.abspath(srcDir),dstDir)
            #print(cmds_xml)
            subprocess.call(cmds_xml,stdout = subprocess.PIPE,shell =1)
        elif self._license == "pro":
            dstDir=r'"C:\Program Files\Common Files\ChaosGroup\vrlclient.xml"'
            license_folder = "127000001"
            srcDir="%s/vrayformaya/license/%s/vrlclient.xml"%(self._b_dist_path,license_folder)
            cmds_xml = "copy %s %s /y" % (os.path.abspath(srcDir),dstDir)
            #print(cmds_xml)
            subprocess.call(cmds_xml,stdout = subprocess.PIPE,shell =1)
        time.sleep(1)
        dstDir="C:/Program Files/Common Files/ChaosGroup/vrlclient.xml"
        cp_t = 1
        cp_check = False
        while cp_check == False:
            if os.path.exists(dstDir):
                self.PrintVr("License file check: Trune")
                cp_check = True
            else:
                time.sleep(2)
                self.PrintVr("License file check: False/ Try to cp %s"%str(cp_t))
                if cp_t>=4:cp_check = True
                cp_t += 1

    def MappingEVN(self):
        app_folder = "%s/software/%s_%s"%(self._plugin_software,self._maya_ver,self._vray_ver.replace("",""))
        modules = "// Module file for Maya. Helps Maya find resources for VRayForMaya."
        modules += "\n+ VRayForMaya%sx64 0.9 %s\maya_vray"%(self._maya_ver,app_folder.replace("/","\\"))
        #print(modules)
        with open("%s\maya_root\modules\VRayForMaya.module"%app_folder.replace("/","\\"),"w") as f:
            f.write(modules)
            f.close()
        
        self.CopyAllFiles(app_folder)
        app_folder = os.path.abspath(app_folder)
        
        ### ---------------------------------------------------
        ### envs
        ### ---------------------------------------------------
        _maya_ver="2016_5" if self._maya_ver=='2016.5' else self._maya_ver
        VRAY_MAIN    = "VRAY_FOR_Maya%s_MAIN_x64"%_maya_ver
        VRAY_PLUGINS = "VRAY_FOR_Maya%s_PLUGINS_x64"%_maya_ver
        VRAY_TOOLS   = "VRAY_TOOLS_Maya%s_x64"%_maya_ver
        VRAY_OSL     = "VRAY_OSL_PATH_Maya%s_x64"%_maya_ver
        VRAY_CLIENT  = "VRAY_AUTH_CLIENT_FILE_PATH"

        os.environ[VRAY_MAIN] = r'%s\maya_vray'%app_folder if not os.environ.get(VRAY_MAIN) else os.environ.get(VRAY_MAIN)+r';%s\maya_vray'%app_folder
        os.environ[VRAY_PLUGINS] = r"%s\maya_vray\vrayplugins"%app_folder if not os.environ.get(VRAY_PLUGINS) else os.environ.get(VRAY_PLUGINS)+r";%s\maya_vray\vrayplugins"%app_folder
        os.environ[VRAY_TOOLS] = r"%s\vray\bin"%app_folder if not os.environ.get(VRAY_TOOLS)else os.environ.get(VRAY_TOOLS)+r";%s\vray\bin"%app_folder
        os.environ[VRAY_OSL] = r"%s\vray\opensl"%app_folder if not os.environ.get(VRAY_OSL)else os.environ.get(VRAY_OSL)+r";%s\vray\opensl"%app_folder
        os.environ[VRAY_CLIENT] = r"C:\Program Files\Common Files\ChaosGroup"
        #os.system("set")
        
    def PrintVr(self,info,extr="VraySetup"):
        if str(info).strip() != "":
            print("[%s] %s"%(extr,str(info)))


def main(maya_ver="2017",vray_ver="3.40.04"):
    ## ------------------------------------------------------------
    ## the license type use pro for default,if not 
    ## found, check the clientM or client type(use license). 
    ## eg. [maya_version,vray_version,license_type,use_new_license]
    ## create by shen 2018.01.230150
    ## ------------------------------------------------------------
    use_new_license = True if str(os.environ.get("G_VRAY_LICENSE"))=="2" else False
    print(use_new_license,str(os.environ.get("G_VRAY_LICNESE")))
    licentype = "client" if str(os.environ.get("VRAY_SETUP_TYPE"))=="1" else ""
    vray_ins = VrayPlugins([maya_ver,vray_ver,licentype,use_new_license])
    vray_ins.ConfigPlugin()
    vray_ins.MappingEVN()
    vray_ins.PrintVr("Pluging setup finished.")
    return vray_ins
    
def doConfigSetup(*args):
    clientInfo = args[0]
    maya_ver = clientInfo.swVer()
    all_plgins = clientInfo.plgins()
    vray_ver = all_plgins["vrayformaya"] if "vrayformaya" in all_plgins else False
    #print vray_ver
    if not vray_ver:
        print("PL set an vray version")
        sys.exit(003)
    if "st" in vray_ver:vray_ver=vray_ver.replace("st","")
    main(maya_ver,vray_ver)

if __name__=="__main__":
    
    os.system(r'"C:\Program Files\Autodesk\Maya%s\bin\maya.exe"'%main('2015','3.05.03')._maya_ver)
    
