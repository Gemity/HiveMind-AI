# HiveMind Template

This folder defines the reusable template that should be embedded into a new project or feature workspace.

The goal of the template is:

- carry over the orchestrator runtime
- carry over the test suite
- create a clean `.ai-loop` workspace
- avoid copying the historical artifacts of this repository

## What To Embed

Copy these items into the target workspace:

- `orchestrator/`
- `tests/`
- `skills/`
- `pyproject.toml`
- `.gitignore`
- `orchestrator_runtime_spec.md`
- `template/bootstrap/.ai-loop/`
- `template/prompts/`

Do not copy the live `.ai-loop/` folder from the root of this repository into a new project, because it contains the history of this project creating itself.

## Bootstrap Script

You can bootstrap a new workspace with:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_template.ps1 -TargetPath <TARGET_WORKSPACE>
```

Optional:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_template.ps1 -TargetPath <TARGET_WORKSPACE> -RequirementTitle "Build feature X"
```

## Bootstrap Flow

1. Copy the reusable files into the target project.
2. Copy `template/bootstrap/.ai-loop/` to `.ai-loop/` in the target project.
3. Keep `skills/` available so future agents can re-read the embedded package through the onboarding skill.
4. Rewrite `.ai-loop/input/requirement.md` for the new project or feature.
5. Initialize or update `.ai-loop/state/workflow_state.json`.
6. Generate phase-specific prompt files from `template/prompts/`.
7. Start the design phase with Codex.
8. Continue with implement, review, and fix loops.

## Template Philosophy

- Template content should be generic and reusable.
- Runtime code belongs in the target project.
- Live artifacts belong only to the target project's own `.ai-loop`.
- Prompt templates should use placeholders instead of hard-coded run data.
