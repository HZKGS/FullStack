param(
    [string]$MongoDb = "locallens",
    [switch]$Drop
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$BusinessFile = Join-Path $ProjectRoot "data\businesses.json"
$ReviewFile = Join-Path $ProjectRoot "data\reviews.json"

foreach ($file in @($BusinessFile, $ReviewFile)) {
    $resolved = (Resolve-Path $file).Path
    if (-not $resolved.StartsWith($ProjectRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Input file must stay inside $ProjectRoot"
    }
}

$common = @("--db", $MongoDb, "--jsonArray")
if ($Drop) {
    $common += "--drop"
}

mongoimport @common --collection businesses --file $BusinessFile
if ($LASTEXITCODE -ne 0) { throw "mongoimport failed for businesses" }

mongoimport @common --collection reviews --file $ReviewFile
if ($LASTEXITCODE -ne 0) { throw "mongoimport failed for reviews" }

Write-Host "Imported businesses.json and reviews.json into database $MongoDb"