# Embed Checklist

Use this checklist when creating a new project or feature workspace from this template.

1. Copy `orchestrator/`, `tests/`, `skills/`, `pyproject.toml`, `.gitignore`, and `orchestrator_runtime_spec.md` into the target workspace.
2. Copy `template/bootstrap/.ai-loop/` into the target workspace as `.ai-loop/`.
3. Copy `template/prompts/` into the target workspace or generate prompt files from them.
4. Rewrite `.ai-loop/input/requirement.md` for the target project or feature.
5. Initialize run metadata in `.ai-loop/state/workflow_state.json`.
6. Run `py -m pytest -q` in the target workspace.
7. Load `skills/hivemind-embed-onboarding/SKILL.md` when an agent needs to reconstruct the embedded package.
8. Start the design phase.

Do not copy the root `.ai-loop/` from this repository into a target project.
