import os, sys
import py_compile


if len(sys.argv) == 1:
	Py_file= raw_input("py_file: ")	
	
else:
	Py_file = sys.argv[1]
	
print Py_file


py_compile.compile(Py_file)


