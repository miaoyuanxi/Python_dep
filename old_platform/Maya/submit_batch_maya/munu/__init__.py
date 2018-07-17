#! /usr/bin/env python
#coding=utf-8
import sys
import os

munu_version = "py" + "".join([str(i) for i in sys.version_info[:3]])
munu_path = os.path.join(os.path.dirname(__file__), munu_version)

if not os.path.exists(munu_path):
    munu_version = "py" + "".join([str(i) for i in sys.version_info[:2]])
    munu_path = os.path.join(os.path.dirname(__file__), munu_version)

sys.path.append(munu_path)

print "python executable is: " + sys.executable
print "python version is: " + sys.version
print "import munu path: " + munu_path
sys.stdout.flush()

exec("from " + munu_version + ".munu import *")
