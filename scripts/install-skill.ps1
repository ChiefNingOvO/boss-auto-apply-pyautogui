param(
    [string]$CodexHome = "$env:USERPROFILE\.codex"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$source = Join-Path $repoRoot "skills\boss-auto-apply"
$targetRoot = Join-Path $CodexHome "skills"
$target = Join-Path $targetRoot "boss-auto-apply"

if (-not (Test-Path -LiteralPath $source)) {
    throw "Skill source not found: $source"
}

New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null
if (Test-Path -LiteralPath $target) {
    Remove-Item -LiteralPath $target -Recurse -Force
}
Copy-Item -Recurse -Force -LiteralPath $source -Destination $targetRoot

Write-Host "Installed boss-auto-apply skill to $target"
Write-Host "Restart Codex or open a new session to refresh the skill list."
