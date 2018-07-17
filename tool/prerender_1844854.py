#!/usr/bin/env python
#encoding:utf-8
# -*- coding: utf-8 -*-
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import os,sys,re


for i in pm.ls(type="aiOptions"): 
	if i.hasAttr("log_verbosity"):
		log_verbosity = i.log_verbosity.get()
		i.log_verbosity.set(1)
for i in pm.ls(type="pgYetiMaya"):
	if i.hasAttr("aiLoadAtInit"):
		i.aiLoadAtInit.set(1)       

for i in pm.ls(type="aiStandIn"):
	if i.hasAttr("deferStandinLoad"):
		i.deferStandinLoad.set(0)



		

