import os
import subprocess
def maketx_cmd(map_path,tx_option):
    maketx_path = r"C:/solidangle/mtoadeploy/2014_1.2.7.2"+"/bin/maketx"
    cmd = maketx_path + " "+tx_option+ " "+map_path
    if os.name == 'nt':
        proc = subprocess.Popen(cmd, creationflags=subprocess.SW_HIDE, shell=True)
    else:
        proc = subprocess.Popen(cmd, shell=True)
    return proc.wait()

def isImage(file_path):
    ext = os.path.splitext(file_path)[1]
    if (ext == '.jpeg' or ext == '.jpg' or ext == '.tiff' or ext == '.tif' or
        ext == '.png' or ext == '.exr' or ext == '.hdr' or ext == '.bmp' or
        ext == '.tga' ):
        return True
    return False

def exist_tx(file_path):
    ext = os.path.splitext(file_path)
    if os.path.exists(ext[0]+".tx"):
        return False
    return True


def file_path_sub(path):
    file_path = []
    for root,dirs,files in os.walk(path):
        for filespath in files:
            if isImage(os.path.join(root,filespath)) and os.path.exists(os.path.join(root,filespath)) and  exist_tx(os.path.join(root,filespath)) and os.path.getsize(os.path.join(root,filespath))>0:
                tx_option = "-u --oiio"
                maketx_cmd(os.path.join(root,filespath),tx_option)


