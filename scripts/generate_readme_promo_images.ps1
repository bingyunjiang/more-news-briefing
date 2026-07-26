[CmdletBinding()]
param(
    [ValidateRange(1, 32)]
    [int]$Concurrency = 3
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$UserProfilePath = [Environment]::GetFolderPath('UserProfile')
$CodexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $UserProfilePath '.codex' }
$ImageGen = Join-Path $CodexRoot 'skills\.system\imagegen\scripts\image_gen.py'
$Prompts = Join-Path $RepoRoot 'tmp\imagegen\readme-promo-prompts.jsonl'
$OutDir = Join-Path $RepoRoot 'assets\readme-xiaohei-scenes'

if (-not (Test-Path -LiteralPath $ImageGen -PathType Leaf)) {
    throw "image_gen.py not found: $ImageGen"
}
if (-not (Test-Path -LiteralPath $Prompts -PathType Leaf)) {
    throw "Prompt file not found: $Prompts"
}
if ([string]::IsNullOrWhiteSpace($env:OPENAI_API_KEY)) {
    throw 'OPENAI_API_KEY is not set. Set it in this trusted PowerShell session, then rerun.'
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$PythonLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($PythonLauncher) {
    & $PythonLauncher.Source -3 $ImageGen generate-batch --input $Prompts --out-dir $OutDir --concurrency $Concurrency
} else {
    $Python = Get-Command python -ErrorAction Stop
    & $Python.Source $ImageGen generate-batch --input $Prompts --out-dir $OutDir --concurrency $Concurrency
}

if ($LASTEXITCODE -ne 0) {
    throw "Image generation failed with exit code $LASTEXITCODE"
}
