#! /usr/bin/env python
# coding=utf-8
import argparse
import os
import munu
import pprint
import json


def check_path(**kwargs):
    # python E:\gdc\workaround\framechecker.py -p "C:\RenderFarm\Download\测试\52157_ball_mb" -j "C:/RenderFarm/framechecker.json" -f " -1-10"
    if os.path.exists(kwargs["json"]):
        os.remove(kwargs["json"])

    sequences = munu.FileSequence.recursive_find(kwargs["path"],
                                                 actual_frange=kwargs["frange"].lstrip())

    error_sequences = [i for i in sequences if i.missing]

    pprint.pprint(sequences)
    print "="*50
    pprint.pprint(error_sequences)

    for i in error_sequences:
        print i.__repr__(), type(i.__repr__())

    if error_sequences:
        data = {"errorkey": [i.__repr__() for i in error_sequences]}

        print data
        with open(kwargs["json"], "w") as json_file:
            try:
                json.dump(data, json_file)
            except:
                json_file.seek(0)
                json.dump(data, json_file, encoding="gb18030")

        exit(1)

    exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Liu Qiang || MMmaomao')
    parser.add_argument("-p", dest="path",
                        help="path include image sequences",
                        type=str, required=1)
    parser.add_argument("-j", dest="json",
                        help="temp path to save check results",
                        type=str, required=1)
    parser.add_argument("-f", dest="frange",
                        help="frame range",
                        type=str, required=1)

    kwargs = parser.parse_args().__dict__
    check_path(**kwargs)
