cd E:\gdc\workaround
e:
call workon py26
python setup.py build_ext --inplace
move munu.pyd munu\py26\munu.pyd

call workon py27
python setup.py build_ext --inplace
move munu.pyd munu\py27\munu.pyd

xcopy /y /e munu submit_batch_maya\munu\

cython --embed -o build\submit_batch_maya.c submit_batch_maya.py
call "C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\vcvarsall.bat" amd64
cl /nologo /Ox /MD /W3 /GS- /DNDEBUG -IC:\Python270\include -IC:\Python270\PC /Tcbuild\submit_batch_maya.c /link /OUT:"build\submit_batch_maya.exe" /SUBSYSTEM:CONSOLE /MACHINE:amd64 /LIBPATH:c:\Python270\libs /LIBPATH:c:\Python270\PCbuild
copy /y build\submit_batch_maya.exe submit_batch_maya\submit_batch_maya.exe

cython --embed -o build\submit_batch_txt.c submit_batch_txt.py
call "C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\vcvarsall.bat" amd64
cl /nologo /Ox /MD /W3 /GS- /DNDEBUG -IC:\Python270\include -IC:\Python270\PC /Tcbuild\submit_batch_txt.c /link /OUT:"build\submit_batch_txt.exe" /SUBSYSTEM:CONSOLE /MACHINE:amd64 /LIBPATH:c:\Python270\libs /LIBPATH:c:\Python270\PCbuild
copy /y build\submit_batch_txt.exe submit_batch_maya\submit_batch_txt.exe

cython --embed -o build\output.c output.py
call "C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\vcvarsall.bat" amd64
cl /nologo /Ox /MD /W3 /GS- /DNDEBUG -IC:\Python270\include -IC:\Python270\PC /Tcbuild\output.c /link /OUT:"build\output.exe" /SUBSYSTEM:CONSOLE /MACHINE:amd64 /LIBPATH:c:\Python270\libs /LIBPATH:c:\Python270\PCbuild
copy /y build\output.exe submit_batch_maya\output.exe

cython --embed -o build\framechecker.c framechecker.py
call "C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\vcvarsall.bat" amd64
cl /nologo /Ox /MD /W3 /GS- /DNDEBUG -IC:\Python270\include -IC:\Python270\PC /Tcbuild\framechecker.c /link /OUT:"build\framechecker.exe" /SUBSYSTEM:CONSOLE /MACHINE:amd64 /LIBPATH:c:\Python270\libs /LIBPATH:c:\Python270\PCbuild
copy /y build\framechecker.exe submit_batch_maya\framechecker.exe

cython --embed -o build\submit.c submit.py
call "C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\vcvarsall.bat" amd64
cl /nologo /Ox /MD /W3 /GS- /DNDEBUG -IC:\Python270\include -IC:\Python270\PC /Tcbuild\submit.c /link /OUT:"build\submit.exe" /SUBSYSTEM:CONSOLE /MACHINE:amd64 /LIBPATH:c:\Python270\libs /LIBPATH:c:\Python270\PCbuild
copy /y build\submit.exe submit_batch_maya\submit.exe

del *.obj *.c *.exp *.lib
REM call workon py27x86
REM cython --embed -o build\output.c output.py
REM call "C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\vcvarsall.bat" x86
REM cl /nologo /Ox /MD /W3 /GS- /DNDEBUG -IC:\Python279x86\include -IC:\Python279x86\PC /Tcbuild\output.c /link /OUT:"build\output.exe" /SUBSYSTEM:CONSOLE /MACHINE:x86 /LIBPATH:c:\Python279x86\libs /LIBPATH:c:\Python279x86\PCbuild
REM copy /y build\output.exe submit_batch_maya\output.exe

REM cython --embed -o build\framechecker.c framechecker.py
REM call "C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\vcvarsall.bat" amd64
REM cl /nologo /Ox /MD /W3 /GS- /DNDEBUG -IC:\Python279x86\include -IC:\Python279x86\PC /Tcbuild\framechecker.c /link /OUT:"build\framechecker.exe" /SUBSYSTEM:CONSOLE /MACHINE:amd64 /LIBPATH:c:\Python279x86\libs /LIBPATH:c:\Python279x86\PCbuild
REM copy /y build\framechecker.exe submit_batch_maya\x86\framechecker.exe

del submit_batch_maya.zip
"C:\Program Files\WinRAR\winrar.exe" a -afzip submit_batch_maya.zip submit_batch_maya

xcopy /y /e submit_batch_maya C:\Users\admin\AppData\Roaming\RenderBus\1008\Module\script\submit_batch_maya
xcopy /y /e submit_batch_maya C:\Users\admin\AppData\Roaming\RenderBus\1002\Module\script\submit_batch_maya
