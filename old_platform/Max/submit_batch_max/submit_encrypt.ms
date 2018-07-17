

fn run_encrypt=(
	
	
	
	local thisScriptPath = getFilenamePath (getSourceFileName())
	
	local submita_ms = pathConfig.appendPath   thisScriptPath "submita.ms"
	local submitu_ms = pathConfig.appendPath   thisScriptPath "submitu.ms"
	encryptScript submita_ms
	encryptScript submitu_ms
)
---run_encrypt()



--encryptScript @"D:\RenderBus\Script\gitLab\Client\Max\submit_batch_max\submita.ms"

--encryptScript @"D:\RenderBus\Script\gitLab\Client\Max\submit_batch_max\submitu.ms"




