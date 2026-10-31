$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Mongod = Join-Path $ProjectRoot "..\.mongo\server\MongoDB\Server\9.0\bin\mongod.exe"
$DataPath = Join-Path $ProjectRoot "..\.mongo\data"
$LogPath = Join-Path $ProjectRoot "..\.mongo\mongod.log"
$PidPath = Join-Path $ProjectRoot "..\.mongo\mongod.pid"

function Test-MongoPort {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $async = $client.BeginConnect("127.0.0.1", 27017, $null, $null)
        if (-not $async.AsyncWaitHandle.WaitOne(1000)) { return $false }
        $client.EndConnect($async)
        return $true
    }
    catch {
        return $false
    }
    finally {
        $client.Close()
    }
}

if (-not (Test-Path -LiteralPath $Mongod)) {
    throw "Project-local mongod.exe not found. Install/extract MongoDB under G:\FullStack\.mongo\server first."
}
New-Item -ItemType Directory -Force -Path $DataPath | Out-Null

if (Test-MongoPort) {
    Write-Host "MongoDB is already listening on 127.0.0.1:27017."
    return
}

$arguments = @(
    "--dbpath", $DataPath,
    "--bind_ip", "127.0.0.1",
    "--port", "27017",
    "--logpath", $LogPath,
    "--logappend"
)
$process = Start-Process -FilePath $Mongod -ArgumentList $arguments -PassThru -WindowStyle Hidden
Set-Content -LiteralPath $PidPath -Value $process.Id -Encoding ascii
Start-Sleep -Seconds 3
if ($process.HasExited) {
    throw "mongod exited during startup. See $LogPath"
}
Write-Host "MongoDB started on 127.0.0.1:27017 (PID $($process.Id))."