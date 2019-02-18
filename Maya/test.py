class O(object):
    def __init__(self):
        self.l = {"a":1}

    def __add__(self, other):
        l = self.l
        l.update(other)
        return l





class B(O):
    def __init__(self):
        self.l = {"b":2}

    def __add__(self, other):
        l = self.l
        l.update(other)
        return l


class C(O):
    def __init__(self):
        self.l = {"c":3}

    def __add__(self, other):
        l = self.l
        l.update(other)
        return l
a = O()
b = B()
c = C()

d = a + {"b": 2}
print d


# print a
# print b
# print c

# a = O()
#
# b = a + {"b": 2}
#
# print(b)
# !/usr/bin/env python
# encoding:utf-8
# -*- coding: utf-8 -*-
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import os, sys, re
import time

