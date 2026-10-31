param(
    [switch]$OpenBrowser
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$Biz = Join-Path $Root "biz_bp"
$Ui = Join-Path $Root "locallens-ui"
$Runtime = Join-Path $Root ".runtime"
New-Item -ItemType Directory -Force -Path $Runtime | Out-Null

function Test-Port([int]$Port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $async = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
        return $async.AsyncWaitHandle.WaitOne(700) -and $client.Connected
    }
    catch {
        return $false
    }
    finally {
        $client.Close()
    }
}

& (Join-Path $Biz "scripts\start_mongo.ps1")

if (-not (Test-Port 5000)) {
    $Python = Join-Path $Biz "venv\Scripts\python.exe"
    $ApiOut = Join-Path $Runtime "api.out.log"
    $ApiErr = Join-Path $Runtime "api.err.log"
    $Api = Start-Process -FilePath $Python -ArgumentList "app.py" -WorkingDirectory $Biz -PassThru -WindowStyle Hidden -RedirectStandardOutput $ApiOut -RedirectStandardError $ApiErr
    Set-Content -LiteralPath (Join-Path $Runtime "api.pid") -Value $Api.Id -Encoding ascii
}

if (-not (Test-Port 4200)) {
    $Ng = Join-Path $Ui "node_modules\.bin\ng.cmd"
    $UiOut = Join-Path $Runtime "ui.out.log"
    $UiErr = Join-Path $Runtime "ui.err.log"
    $UiProcess = Start-Process -FilePath $Ng -ArgumentList "serve", "--host", "127.0.0.1", "--port", "4200" -WorkingDirectory $Ui -PassThru -WindowStyle Hidden -RedirectStandardOutput $UiOut -RedirectStandardError $UiErr
    Set-Content -LiteralPath (Join-Path $Runtime "ui.pid") -Value $UiProcess.Id -Encoding ascii
}

$apiReady = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Milliseconds 500
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:5000/health" -TimeoutSec 2
        if ($health.status -eq "ok") { $apiReady = $true; break }
    }
    catch {}
}
if (-not $apiReady) {
    throw "Flask API did not become ready. Check $Runtime\api.err.log"
}

$uiReady = $false
for ($i = 0; $i -lt 40; $i++) {
    if (Test-Port 4200) { $uiReady = $true; break }
    Start-Sleep -Milliseconds 500
}
if (-not $uiReady) {
    throw "Angular UI did not become ready. Check $Runtime\ui.err.log"
}

Write-Host ""
Write-Host "LocalLens is running:" -ForegroundColor Green
Write-Host "  Angular UI: http://127.0.0.1:4200/"
Write-Host "  Flask API:  http://127.0.0.1:5000/"
Write-Host "  API data:   http://127.0.0.1:5000/api/v1.0/businesses?pn=1&ps=5"
Write-Host ""
Write-Host "Stop API/UI with: $Root\stop_locallens.ps1"

if ($OpenBrowser) {
    Start-Process "http://127.0.0.1:4200/"
}