#!/usr/bin/env python
#encoding:utf-8
# -*- coding: utf-8 -*-

import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import os,sys,re
import logging
import datetime
import subprocess
import time


def bytes_to_str(str1, str_decode='default'):
    if not isinstance(str1, str):
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

def run_cmd(cmd_str, my_log=None, try_count=1, continue_on_error=False, my_shell=False,
        callback_func=None):  # continue_on_error=true-->not exit ; continue_on_error=false--> exit
    print(str(continue_on_error) + '--->>>' + str(my_shell))
    cmd_str = bytes_to_str(cmd_str)
    if my_log != None:
        my_log.info('cmd...' + cmd_str)
    # self.G_PROCESS_LOG.info('try3...')
    l = 0
    resultStr = ''
    resultCode = 0
    while l < try_count:
        l = l + 1
        my_popen = subprocess.Popen(cmd_str, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, shell=my_shell)
        my_popen.stdin.write(b'3/n')
        my_popen.stdin.write(b'4/n')

        if callback_func == None:
            while my_popen.poll() == None:
                result_line = my_popen.stdout.readline().strip()
                result_line = result_line.decode(sys.getfilesystemencoding())
                if result_line != '' and my_log != None:
                    my_log.info(result_line)
        else:
            callback_func(my_popen, my_log)

        resultStr = my_popen.stdout.read()
        resultStr = resultStr.decode(sys.getfilesystemencoding())
        resultCode = my_popen.returncode
        if resultCode == 0:
            break
        else:
            time.sleep(1)
    if my_log != None:
        my_log.info('resultStr...' + resultStr)
        my_log.info('resultCode...' + str(resultCode))

    if not continue_on_error:
        if resultCode != 0:
            sys.exit(resultCode)
    return resultCode, resultStr



def set_rendered_frame(save_path = "", task_id="", rd="", use_id=""):
    print ("the cfg path ++++++++++> %s " % save_path)
    print ("the task id is ============> %s" % task_id)
    print ("the rd_path is ============> %s" % rd)
    save_path = rendersetting["output"]
    out_temp = os.path.abspath(os.path.join(os.path.dirname(save_path),os.path.pardir)).replace("\\","/")
    current_frame = int(pm.currentTime())
    if len(str(current_frame)) >= 4:
        serial = current_frame
    else:
        serial = '0' * (5 - current_frame) + str(current_frame)
    output_frame = os.path.join(save_path,serial).replace("\\","/")

    if not os.path.exists(output_frame):
        os.makedirs(output_frame)

    cmd1 = '{fcopy_path} /speed=full /cmd=move /force_close /no_confirm_stop /force_start "{source}" /to="{destination}"'.format(
        fcopy_path='c:\\fcopy\\FastCopy.exe',
        source=os.path.join(save_path.replace('/', '\\')),
        destination=out_temp.replace('/', '\\'),
    )

    cmd2 = '{fcopy_path} /speed=full /cmd=move /force_close /no_confirm_stop /force_start "{source}" /to="{destination}"'.format(
        fcopy_path='c:\\fcopy\\FastCopy.exe',
        source=os.path.join(out_temp.replace('/', '\\')),
        destination=output_frame.replace('/', '\\'),
    )
    cmd(cmd1,my_log=None, try_count=3, continue_on_error=True)
    cmd(cmd2,my_log=None, try_count=3, continue_on_error=True)


def write_post_frame_ini():
    pm.lockNode('defaultRenderGlobals', lock=False)

    render_node = pm.PyNode("defaultRenderGlobals")
    render_name = render_node.currentRenderer.get()

    render_node.postMel.set(l=0)
    render_node.preRenderLayerMel.set(l=0)
    render_node.postRenderLayerMel.set(l=0)
    render_node.preRenderMel.set(l=0)
    render_node.postRenderMel.set(l=0)

    preMel = render_node.preMel.get()
    postMel = render_node.postMel.get()
    preRenderLayerMel = render_node.preRenderLayerMel.get()
    postRenderLayerMel = render_node.postRenderLayerMel.get()
    preRenderMel = render_node.preRenderMel.get()
    postRenderMel = render_node.postRenderMel.get()

    current_frame = int(cmds.currentTime( query=True ))
    frame_out_ini = "[_____render end_____]"+ "[" + str(current_frame) + "]" + "\n"
    print frame_out_ini


def copy_texture_to():
    current_frame = int(pm.currentTime())
    if len(str(current_frame)) >= 4:
        serial = str(current_frame)
    else:
        serial = '0' * (4 - len(str(current_frame))) + str(current_frame)
    output_frame = os.path.join(options["output_frame"],serial).replace("\\","/")
    print output_frame
    if not os.path.exists(output_frame):
        os.makedirs(output_frame)

    cmd = '{fcopy_path} /speed=full /cmd=move /force_close /no_confirm_stop /force_start "{source}" /to="{destination}"'.format(
        fcopy_path='c:\\fcopy\\FastCopy.exe',
        source=os.path.join(options["output"]).replace('/', '\\'),
        destination=output_frame.replace("/","\\"),
    )

    result_code,_  = run_cmd(cmd,my_log=None, try_count=3, continue_on_error=True)
    if result_code == 0:
        print "copy temp out to  frame  out  success!"
    # os.system(cmd)





if __name__ == '__main__':
    print '\n\n-------------------------------------------------------[PostRender]start----------------------------------------------------------\n\n'
    post_start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print "[PostRender start]----%s \n" % post_start_time
    beginTime = datetime.datetime.now()
    if options["g_one_machine_multiframe"] is True:
        write_post_frame_ini()
        copy_texture_to()

    endTime = datetime.datetime.now()
    timeOut = endTime - beginTime
    print "[Prerender time]----%s" % (str(timeOut))
    print '\n\n-------------------------------------------------------[PostRender]end----------------------------------------------------------\n\n'


