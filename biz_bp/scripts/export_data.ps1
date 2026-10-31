param(
    [string]$MongoDb = "locallens",
    [string]$OutputDirectory = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Join-Path $ProjectRoot "data\export"
}
$ResolvedOutput = [System.IO.Path]::GetFullPath($OutputDirectory)
if (-not $ResolvedOutput.StartsWith($ProjectRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Output directory must stay inside $ProjectRoot"
}

New-Item -ItemType Directory -Force -Path $ResolvedOutput | Out-Null

mongoexport --db $MongoDb --collection businesses --jsonArray --out (Join-Path $ResolvedOutput "businesses.json")
if ($LASTEXITCODE -ne 0) { throw "mongoexport failed for businesses" }

mongoexport --db $MongoDb --collection reviews --jsonArray --out (Join-Path $ResolvedOutput "reviews.json")
if ($LASTEXITCODE -ne 0) { throw "mongoexport failed for reviews" }

Write-Host "Exported collections to $ResolvedOutput"