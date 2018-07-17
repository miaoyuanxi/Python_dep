@echo off

echo ========================convert py to EXE start========================
set curentpath=%~dp0
echo curentpath=%curentpath%
set exename=submit_batch_max

set project_path=%~1

set build_project_path=%project_path%\Max\submit_batch_max\
set update_project_path=%project_path%\max_build\
set zip_path=%update_project_path%\submit_batch_max\

mkdir "%zip_path%"
echo build_project_path=%build_project_path%
echo temp_project_path=%temp_project_path%



echo .
echo .
echo .
echo .
echo  ======================start.xcopy file===========================

xcopy /y /v /f "%build_project_path%_ctypes.pyd" "%zip_path%"
xcopy /y /v /f "%build_project_path%msvcr100.dll" "%zip_path%"
xcopy /y /v /f "%build_project_path%submit_batch_max.dll" "%zip_path%"

xcopy /y /v /f "%build_project_path%submita.mse" "%zip_path%"
xcopy /y /v /f "%build_project_path%submitu.mse" "%zip_path%"
xcopy /y /v /f "%build_project_path%submit_batch_max.exe" "%zip_path%"
echo .
echo .
echo  ======================start.submit_batch_max.zip===========================
echo del /F /Q "%update_project_path%%exename%.zip"
del /F /Q "%update_project_path%%exename%.zip"

echo C:/7-Zip/7z.exe a "%update_project_path%%exename%.zip" "%update_project_path%%exename%"
C:/7-Zip/7z.exe a "%update_project_path%%exename%.zip" "%update_project_path%%exename%"