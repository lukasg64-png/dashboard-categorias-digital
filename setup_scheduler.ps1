# setup_scheduler.ps1 — Registra a tarefa agendada no Windows Task Scheduler
# para atualizar diariamente o Acompanhamento Categorias Digital às 07:30.

$TaskName = "AcompanhamentoDigitalDailySync"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BatPath = Join-Path $ScriptDir "atualizar_digital.bat"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  CONFIGURAÇÃO DE AGENDAMENTO AUTOMÁTICO (WINDOWS TASK SCHEDULER)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Diretório do Projeto: $ScriptDir"
Write-Host "Script Executor:      $BatPath"
Write-Host "Horário de Execução:  07:30 da manhã (Diariamente)"

if (-not (Test-Path $BatPath)) {
    Write-Error "Arquivo atualizar_digital.bat não encontrado em $ScriptDir"
    exit 1
}

$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$BatPath`"" -WorkingDirectory $ScriptDir
$Trigger = New-ScheduledTaskTrigger -Daily -At "07:30"
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew

try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Atualizacao automatica diaria do Dashboard Acompanhamento Categorias Digital" -Force | Out-Null
    Write-Host "`n✅ Tarefa '$TaskName' agendada com sucesso para rodar todos os dias às 07:30!" -ForegroundColor Green
    Write-Host "Para executar manualmente agora: Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Yellow
} catch {
    Write-Warning "Não foi possível registrar com privilégios de Administrador direto: $_"
    Write-Host "Você pode executar o script atualizar_digital.bat manualmente ou executar o PowerShell como Administrador." -ForegroundColor Yellow
}
