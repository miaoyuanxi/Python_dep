set "FUSION=C:\Program Files\Blackmagic Design\Fusion"

set "PATH=%FUSION%;%PATH%

fusion "%CD%\Composition1.comp" /render /start 1 /end 10 /step 1 /verbose /quiet /quietlicense /clean /quit
