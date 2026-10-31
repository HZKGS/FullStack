$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $ProjectRoot
$Python = Join-Path $ProjectRoot "venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    throw "Virtual-environment Python not found at $Python"
}
& (Join-Path $PSScriptRoot "start_mongo.ps1")
& $Python -m unittest -v tests.test_api_smoke
exit $LASTEXITCODE