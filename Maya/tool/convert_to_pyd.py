import os, sys
import py_compile
from distutils.core import setup
from Cython.Build import cythonize

if len(sys.argv) == 1:
	Py_file= raw_input("py_file: ")	
	
else:
	Py_file = sys.argv[1]
	
print Py_file

# py_compile.compile(Py_file)

Py_file = "E:/NewPlatform/Maya/tool/Map_B.py"
setup(name = 'Hello world',ext_modules = cythonize(Py_file))
