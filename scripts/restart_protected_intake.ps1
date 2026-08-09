param(
    [string]$StorageRoot = "C:\private\pia-participant-store-v3",
    [int]$Port = 8789
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$listeners = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
foreach ($listener in $listeners) {
    $process = Get-Process -Id $listener.OwningProcess -ErrorAction SilentlyContinue
    if ($null -ne $process -and $process.ProcessName -match "^(python|pythonw)$") {
        Write-Host "Stopping Python listener $($process.Id) on port $Port"
        Stop-Process -Id $process.Id -Force
    } else {
        throw "Port $Port is owned by a non-Python process. Resolve it manually before continuing."
    }
}

Write-Host "Starting protected intake from $repoRoot"
Write-Host "Open a new browser tab at http://127.0.0.1:$Port/ after the server starts."
& python -m software.intake.protected_intake_server `
    --storage-root $StorageRoot `
    --port $Port
