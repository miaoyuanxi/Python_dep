#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import codecs

print(sys.argv[0])
print('-------------------------start---------------------------')
path = sys.argv[1]

f1 = codecs.open(path,'r','utf-8')
cmd = f1.read()
f1.close()

ret = os.system(cmd)
if ret != 0:
    sys.exit(ret)
print('No message is best message!')
print('-------------------------end---------------------------')