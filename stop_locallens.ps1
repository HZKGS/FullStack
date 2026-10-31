$ErrorActionPreference = "Stop"
$Runtime = Join-Path $PSScriptRoot ".runtime"

foreach ($name in @("ui", "api")) {
    $pidFile = Join-Path $Runtime "$name.pid"
    if (-not (Test-Path -LiteralPath $pidFile)) {
        Write-Host "$name is not tracked by this project."
        continue
    }
    $processId = [int](Get-Content -LiteralPath $pidFile -Raw)
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $processId
        Write-Host "Stopped $name (PID $processId)."
    }
    Remove-Item -LiteralPath $pidFile -Force
}

Write-Host "MongoDB was left running. Data remains in G:\FullStack\.mongo\data."