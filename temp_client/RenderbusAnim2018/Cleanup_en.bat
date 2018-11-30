@echo off & setlocal enabledelayedexpansion
set process=QRenderBus.exe QFoxRenderfarm.exe rayvision_update.exe rendercmd.exe output.exe framechecker.exe submit_batch_maya.exe submit_batch_max.exe
for %%a in (%process%) do (
taskkill /F /IM %%a
)

start QFoxRenderfarm.exe