# Quick Start

## Option 1

Copy this whole `template/` folder to a new location and rename it as the new workspace root.

## Option 2

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_template.ps1 -TargetPath <TARGET_WORKSPACE>
```

## First Steps

1. Edit `.ai-loop/input/requirement.md`
2. Initialize state if needed:

```powershell
py -m orchestrator init --requirement .ai-loop/input/requirement.md --force
```

3. Run tests:

```powershell
py -m pytest -q
```

4. Start the first loop:

```bash
bash run
```

## Rule

Treat the `.ai-loop/` inside this folder as a clean starter workspace for the new project, not as the live history of the current repository.
