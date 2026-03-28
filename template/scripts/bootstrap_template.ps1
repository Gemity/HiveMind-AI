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

$templateRoot = Split-Path -Parent $PSScriptRoot
$targetRoot = [System.IO.Path]::GetFullPath($TargetPath)

if ((Test-Path -LiteralPath $targetRoot) -and -not $Force) {
    $existing = Get-ChildItem -Force -ErrorAction SilentlyContinue $targetRoot
    if ($existing) {
        throw "Target path is not empty. Re-run with -Force if you want to copy into it: $targetRoot"
    }
}

New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null

$copyMap = @(
    @{ Source = (Join-Path $templateRoot "orchestrator"); Destination = (Join-Path $targetRoot "orchestrator") },
    @{ Source = (Join-Path $templateRoot "tests"); Destination = (Join-Path $targetRoot "tests") },
    @{ Source = (Join-Path $templateRoot "skills"); Destination = (Join-Path $targetRoot "skills") },
    @{ Source = (Join-Path $templateRoot "scripts"); Destination = (Join-Path $targetRoot "scripts") },
    @{ Source = (Join-Path $templateRoot "prompts"); Destination = (Join-Path $targetRoot "prompts") },
    @{ Source = (Join-Path $templateRoot ".ai-loop"); Destination = (Join-Path $targetRoot ".ai-loop") },
    @{ Source = (Join-Path $templateRoot "pyproject.toml"); Destination = (Join-Path $targetRoot "pyproject.toml") },
    @{ Source = (Join-Path $templateRoot ".gitignore"); Destination = (Join-Path $targetRoot ".gitignore") },
    @{ Source = (Join-Path $templateRoot "orchestrator_runtime_spec.md"); Destination = (Join-Path $targetRoot "orchestrator_runtime_spec.md") },
    @{ Source = (Join-Path $templateRoot "run"); Destination = (Join-Path $targetRoot "run") },
    @{ Source = (Join-Path $templateRoot "README.md"); Destination = (Join-Path $targetRoot "README.md") },
    @{ Source = (Join-Path $templateRoot "embed_checklist.md"); Destination = (Join-Path $targetRoot "embed_checklist.md") }
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

Write-Host "Template embedded successfully at: $targetRoot"
Write-Host "Next: edit .ai-loop/input/requirement.md and initialize workflow state."
