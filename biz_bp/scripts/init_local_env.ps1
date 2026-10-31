$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$EnvPath = Join-Path $ProjectRoot ".env.local"

if (Test-Path -LiteralPath $EnvPath) {
    Write-Host "Local environment already exists: $EnvPath"
    return
}

$jwtSecret = [System.Guid]::NewGuid().ToString("N") + [System.Guid]::NewGuid().ToString("N")
$adminPassword = [System.Guid]::NewGuid().ToString("N")
$userPassword = [System.Guid]::NewGuid().ToString("N")
$content = @"
MONGO_URI=mongodb://127.0.0.1:27017
MONGO_DB_NAME=locallens
JWT_SECRET=$jwtSecret
JWT_EXPIRY_SECONDS=28800
ADMIN_PASSWORD=$adminPassword
USER_PASSWORD=$userPassword
HOST=127.0.0.1
PORT=5000
FLASK_DEBUG=0
"@
[System.IO.File]::WriteAllText($EnvPath, $content, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "Created gitignored local environment: $EnvPath"
Write-Host "Secret values were not printed."