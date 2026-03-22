param(
    [Parameter(Mandatory = $true)]
    [string]$TargetPath,

    [string]$RequirementTitle = "Describe the new project or feature here.",

    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Copy-PathSafe {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Source,

        [Parameter(Mandatory = $true)]
        [string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        throw "Source path not found: $Source"
    }

    $parent = Split-Path -Parent $Destination
    if ($parent) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }

    Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$targetRoot = [System.IO.Path]::GetFullPath($TargetPath)

if ((Test-Path -LiteralPath $targetRoot) -and -not $Force) {
    $existing = Get-ChildItem -Force -ErrorAction SilentlyContinue $targetRoot
    if ($existing) {
        throw "Target path is not empty. Re-run with -Force if you want to copy into it: $targetRoot"
    }
}

New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null

$copyMap = @(
    @{ Source = (Join-Path $repoRoot "orchestrator"); Destination = (Join-Path $targetRoot "orchestrator") },
    @{ Source = (Join-Path $repoRoot "tests"); Destination = (Join-Path $targetRoot "tests") },
    @{ Source = (Join-Path $repoRoot "pyproject.toml"); Destination = (Join-Path $targetRoot "pyproject.toml") },
    @{ Source = (Join-Path $repoRoot ".gitignore"); Destination = (Join-Path $targetRoot ".gitignore") },
    @{ Source = (Join-Path $repoRoot "orchestrator_runtime_spec.md"); Destination = (Join-Path $targetRoot "orchestrator_runtime_spec.md") },
    @{ Source = (Join-Path $repoRoot "template\bootstrap\.ai-loop"); Destination = (Join-Path $targetRoot ".ai-loop") },
    @{ Source = (Join-Path $repoRoot "template\prompts"); Destination = (Join-Path $targetRoot "template_prompts") }
)

foreach ($entry in $copyMap) {
    Copy-PathSafe -Source $entry.Source -Destination $entry.Destination
}

$requirementPath = Join-Path $targetRoot ".ai-loop\input\requirement.md"
if (Test-Path -LiteralPath $requirementPath) {
    $content = Get-Content -LiteralPath $requirementPath -Raw
    $content = $content.Replace("Describe the new project or feature here.", $RequirementTitle)
    Set-Content -LiteralPath $requirementPath -Value $content
}

$readmePath = Join-Path $targetRoot "HIVEMIND_TEMPLATE_README.md"
$readme = @"
# Embedded HiveMind Template

This workspace was bootstrapped from the HiveMind AI template.

Copied assets:

- orchestrator runtime package
- test suite
- runtime spec
- clean .ai-loop workspace
- prompt templates

Next steps:

1. Edit `.ai-loop/input/requirement.md`
2. Initialize `.ai-loop/state/workflow_state.json`
3. Run `py -m pytest -q`
4. Start the design phase with Codex
"@
Set-Content -LiteralPath $readmePath -Value $readme

Write-Host "Template embedded successfully at: $targetRoot"
Write-Host "Next: edit .ai-loop/input/requirement.md and initialize workflow state."
