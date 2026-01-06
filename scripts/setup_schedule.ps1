
$TaskName = "JobFlowGenAI_Hourly"
$PythonPath = (Get-Command python).Source
$WorkDir = (Get-Location).Path
$ScriptArgs = "-m jobflow.run --once"

$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $ScriptArgs -WorkingDirectory $WorkDir
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -Action $Action -Trigger $Trigger -Settings $Settings -TaskName $TaskName -Description "Runs JobFlow GenAI Agent every hour to find new Data Engineer jobs."

Write-Host "✅ Task '$TaskName' has been scheduled to run every hour."
Write-Host "You can view it in 'Task Scheduler' app."
