# HiveMind Template

This folder is now a self-contained portable bundle for a new project or feature workspace.

If you want to bring HiveMind into another project, carry this folder only.

Contents included inside this folder:

- `orchestrator/`
- `tests/`
- `skills/`
- `scripts/`
- `prompts/`
- `.ai-loop/`
- `pyproject.toml`
- `.gitignore`
- `orchestrator_runtime_spec.md`
- `run`
- `embed_checklist.md`

## Recommended Use

Option 1: copy this whole folder to a new location and rename it as the new workspace root.

Option 2: run the bootstrap script from inside this folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_template.ps1 -TargetPath <TARGET_WORKSPACE>
```

Optional:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_template.ps1 -TargetPath <TARGET_WORKSPACE> -RequirementTitle "Build feature X"
```

## What To Edit First

1. `.ai-loop/input/requirement.md`
2. `.ai-loop/state/workflow_state.json`
3. agent command settings if your local Codex or Claude CLI differs

## Philosophy

- This folder should be portable by itself.
- It should not depend on files outside the folder.
- The `.ai-loop/` inside this folder is a clean starter workspace, not the historical live workspace of the current repository.
