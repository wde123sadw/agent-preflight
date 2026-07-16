param(
    [string]$Target,
    [switch]$Force,
    [switch]$DryRun,
    [switch]$Json
)

$ErrorActionPreference = "Stop"
$installer = Join-Path $PSScriptRoot "install.py"
$arguments = @($installer)

if ($Target) {
    $arguments += @("--target", $Target)
}
if ($Force) {
    $arguments += "--force"
}
if ($DryRun) {
    $arguments += "--dry-run"
}
if ($Json) {
    $arguments += "--json"
}

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 @arguments
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python @arguments
} else {
    throw "Python 3.8 or newer is required."
}

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
