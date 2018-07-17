# ! /usr/bin/env python
# coding=utf-8
import argparse
import os
import re


def get_cfg_info(cfg_file):
    result = {}
    for line in open(cfg_file, "r"):
        if "=" in line:
            line_split = line.split("=")
            result[line_split[0].strip()] = line_split[1].strip()
        if ">>" in line:
            break
    return result


def get_output(**kwargs):
    kwargs["root_path"] = kwargs["root_path"].rstrip("/").rstrip("\\").rstrip("\"")
    kwargs["root_path"] = kwargs["root_path"].replace("\\", "/")
    kwargs["scene_path"] = kwargs["scene_path"].replace("\\", "/")

    base, ext = os.path.splitext(os.path.basename(kwargs["scene_path"]))
    ext = ext.lstrip(".")

    kwargs["root_path"] = kwargs["root_path"].replace("/", "\\")

    # if kwargs["user_id"] == 964309:
    #     kwargs["father_id"] = 964309
    # if kwargs["father_id"] == 964309:
    #     sequence, shot = re.findall(r'.*?(\d+).*?(\d+).+?',
    #                                 os.path.basename(kwargs["scene_path"]), re.I)[0]
    #     sequence = sequence.zfill(4)
    #     shot = shot.zfill(4)
    #     path = "Y:\\JUEJI_movie\\renders\SEQ%s\\S%s_%s\\temp\\renderbus\\" % (sequence, sequence, shot)
    #     return path

    if kwargs["user_id"] == 1819310:
        kwargs["father_id"] = 1819310
    if kwargs["father_id"] == 1819310:
        path = "%s\\images\\" % (os.path.dirname(kwargs["scene_path"]))
        return path.replace("/", "\\")

    if kwargs["user_id"] == 962413:
        kwargs["father_id"] = 962413
    if kwargs["father_id"] == 962413:
        return "%s\\%s\\" % (kwargs["root_path"], base)

    if kwargs["user_id"] == 961743:
        kwargs["father_id"] = 961743
    if kwargs["father_id"] == 961743:
        return "%s\\" % (kwargs["root_path"])

    if kwargs["user_id"] == 1813491:
        return "%s\\" % (kwargs["root_path"])

    if kwargs["user_id"] in [961900, 963697]:
        if kwargs["scene_path"].lower().endswith(".hip"):
            cfg_file = r"C:\RenderFarm\Project\%s\render.cfg" % (kwargs["task_id"])
            mantra_name = get_cfg_info(cfg_file)["rop"].split("/")[-1]
            shot = re.findall(r'(CUT\w+?_\w+?)[_\.].+',
                              os.path.basename(kwargs["scene_path"]), re.I)[0]
            sequence = shot.split("_")[0]

            path = os.path.dirname(kwargs["scene_path"]).lower()
            path = path.replace("/", '\\')
            r = re.findall(r'.+houdini\\(.+)\\dragon.+', path, re.I)
            path = path.replace(r[0], "farm1_image")
            path = os.path.join(path.split("dragonnest2")[0], "dragonnest2",
                                sequence, shot, shot + "_" + mantra_name)

            path += "\\"
        else:
            path = os.path.dirname(kwargs["scene_path"]).lower()
            path = path.replace("render_cache", "render_image")
            path = path.replace("/", '\\') + "\\"
        return path

    if kwargs["user_id"] in [1813119]:
        output_py = os.environ["px_output_py"]
        os.environ["scene_path"] = kwargs["scene_path"]
        render_out_path = ""
        # print output_py, os.path.exists(output_py)
        if os.path.exists(output_py):
            execfile(output_py, globals(), locals())
            return render_out_path

        r = re.findall(r'\w+_(\w+)_(\d+)_(\w+)_v\d+.+',
                       os.path.basename(kwargs["scene_path"]), re.I)
        if r:
            sc, shot, task = r[0]
            return "%s\\%s\\%s\\elements\\3d\\%s\\" % (kwargs["root_path"],
                                                       sc, shot, task)

    if kwargs["user_id"] == 1821185:
        kwargs["father_id"] = 1821185
    if kwargs["father_id"] == 1821185:
        episode, sequence, shot = re.findall(r'.*(ths_\d+)_(\w+?)_(\w+?)_',
                                             os.path.basename(kwargs["scene_path"]),
                                             re.I)[0]

        path = "S:\\DW_TrollHunter_TV\\Renders\\%s\\%s\\%s\\temp\\renderbus\\" % (episode, sequence, shot)
        return path

    if kwargs["user_id"] == 1830380:
        kwargs["father_id"] = 1830380
    if kwargs["father_id"] == 1830380:
        episode, sequence, shot = re.findall(r'.*(ths_\d+)_(\w+?)_(\w+?)_',
                                             os.path.basename(kwargs["scene_path"]),
                                             re.I)[0]

        return "%s\\%s_%s_%s\\" % (kwargs["root_path"], episode, sequence, shot)

    return "%s\\%s_%s\\" % (kwargs["root_path"], kwargs["task_id"],
                            base.strip("."))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Liu Qiang || MMmaomao')
    parser.add_argument("--ui", dest="user_id", type=int, required=1)
    parser.add_argument("--fi", dest="father_id", type=int, default=0)
    parser.add_argument("--ti", dest="task_id", type=int, required=1)
    parser.add_argument("-s", dest="scene_path", help="full path of scene file",
                        type=str, required=1)
    parser.add_argument("-r", dest="root_path", help="download root path",
                        type=str, required=1)

    kwargs = parser.parse_known_args()[0].__dict__
    print get_output(**kwargs)
