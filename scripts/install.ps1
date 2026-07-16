param(
    [string]$Target,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

if (-not $Target) {
    $codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
    $Target = Join-Path $codexHome "skills"
}

$sourceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\skills")).Path
$targetRoot = [System.IO.Path]::GetFullPath($Target)
New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null
$timestamp = Get-Date -Format "yyyyMMddHHmmss"

foreach ($skill in Get-ChildItem -LiteralPath $sourceRoot -Directory) {
    $destination = [System.IO.Path]::GetFullPath((Join-Path $targetRoot $skill.Name))
    if (-not $destination.StartsWith($targetRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing destination outside target root: $destination"
    }

    if (Test-Path -LiteralPath $destination) {
        if (-not $Force) {
            throw "Skill already exists: $destination. Re-run with -Force to back it up and replace it."
        }
        $backup = "$destination.bak.$timestamp"
        Move-Item -LiteralPath $destination -Destination $backup
        Write-Host "Backed up $destination to $backup"
    }

    Copy-Item -LiteralPath $skill.FullName -Destination $destination -Recurse
    Write-Host "Installed $($skill.Name) -> $destination"
}

Write-Host "Agent Preflight installation complete. Restart or reload the agent if required."
