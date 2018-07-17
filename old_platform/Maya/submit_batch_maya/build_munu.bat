cd E:\gdc\workaround
e:
call workon py26
if EXIST munu.c del /F /S /Q munu.c
python setup.py build_ext --inplace
move  /y munu.pyd munu\py26\munu.pyd
echo "py26 munu.py  to munu.pyd is ok"
call workon py27
if EXIST munu.c del /F /S /Q munu.c
python setup.py build_ext --inplace
move /y munu.pyd munu\py27\munu.pyd
echo "py27 munu.py  to munu.pyd is ok"
xcopy /y /e munu submit_batch_maya\munu\


del *.obj *.c *.exp *.lib
set data_=%date:~0,10%
set data_=%data_:/=_%
echo %data_%
set time_=%time:~0,8%
set time_=%time_::=_%
set date_time=%data_%_%time_%
echo %date_time%
if EXIST submit_batch_maya.zip ren submit_batch_maya.zip submit_batch_maya_%date_time%.zip
::del submit_batch_maya.zip
"C:\Program Files\WinRAR\winrar.exe" a -afzip submit_batch_maya.zip submit_batch_maya


::xcopy /y /e submit_batch_maya C:\Users\admin\AppData\Roaming\RenderBus\1008\Module\script\submit_batch_maya
::xcopy /y /e submit_batch_maya C:\Users\admin\AppData\Roaming\RenderBus\1002\Module\script\submit_batch_maya
