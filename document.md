# HiveMind AI Usage Guide

## Overview

This project is a local AI orchestrator for coordinating multiple coding agents through files, workflow state, and explicit review artifacts.

Current role split:

- Codex: design and review
- Claude Code: implementation and fix
- Orchestrator: runtime logic, validation, transitions, and audit trail
- Human: initializes runs, moves work between agents, and resolves blocked decisions

This repository is still operated in a manual human-in-the-loop mode, but the codebase and `.ai-loop` structure are designed to evolve toward more autonomous execution.

## Repository Structure

Important paths:

- `orchestrator/`: Python package for the runtime
- `tests/`: test suite
- `skills/`: reusable helper skill content
- `scripts/`: bootstrap and utility scripts
- `template/`: portable bundle that can be copied into another project by itself
- `.ai-loop/`: live coordination workspace for this repository
- `orchestrator_runtime_spec.md`: executable runtime contract

The `.ai-loop` directory is the operational center of the current repo:

- `.ai-loop/input`: requirements, human queue, and prompt packages
- `.ai-loop/artifacts/current`: live artifacts for the current run
- `.ai-loop/artifacts/history`: reserved for archived run snapshots
- `.ai-loop/state`: workflow state and lock files
- `.ai-loop/logs`: audit log

## Portable Template

The recommended reusable package is now the `template/` folder itself.

That means when you want to bring HiveMind into another project, you should only need to carry:

- `template/`

Inside `template/` there is already a self-contained bundle with:

- runtime code
- tests
- scripts
- skills
- clean `.ai-loop`
- prompt templates
- `run`
- `.gitignore`
- `pyproject.toml`
- runtime spec

You have two ways to use it:

1. Copy the whole `template/` folder somewhere else and rename it into the new workspace root.
2. Run `template/scripts/bootstrap_template.ps1` to materialize a fresh workspace elsewhere.

## Python Commands

Use the Python launcher on Windows:

```powershell
py -m pytest -q
```

Run the orchestrator CLI:

```powershell
py -m orchestrator --help
```

Common CLI commands:

```powershell
py -m orchestrator status
py -m orchestrator validate
py -m orchestrator check-transition
py -m orchestrator run
py -m orchestrator init --requirement .ai-loop/input/requirement.md --force
```

Git Bash shortcut:

```bash
bash run
```

Default agent commands:

- `codex exec -` for `designing` and `reviewing`
- `claude -p` for `implementing` and `fixing`

Override them when your local CLI needs different flags:

```powershell
$env:HIVEMIND_CODEX_COMMAND = 'codex exec --cwd {cwd} {prompt_path}'
$env:HIVEMIND_CLAUDE_COMMAND = 'claude -p'
```

Supported template placeholders:

- `{prompt_path}`
- `{cwd}`
- `{phase}`
- `{run_id}`
- `{iteration}`
- `{phase_attempt}`
- `{agent}`

## Manual Workflow

### 1. Prepare the requirement

Edit `.ai-loop/input/requirement.md` so it clearly states:

- project goal
- constraints
- success criteria
- current human-in-the-loop assumptions

### 2. Initialize or inspect state

Check the current runtime state:

```powershell
py -m orchestrator status
```

If you need to initialize a fresh run:

```powershell
py -m orchestrator init --requirement .ai-loop/input/requirement.md --force
```

Then generate the prompt package and invoke the assigned agent:

```bash
bash run
```

### 3. Design phase

Codex produces or updates:

- `.ai-loop/artifacts/current/design.md`

### 4. Implement phase

Claude implements code and produces:

- code changes in `orchestrator/`
- `.ai-loop/artifacts/current/implementation_report.md`

### 5. Review phase

Codex reviews the implementation and updates:

- `.ai-loop/artifacts/current/review.md`
- `.ai-loop/artifacts/current/review.json`

Interpretation:

- `PASS`: implementation is accepted
- `FAIL`: Claude should fix the listed issues
- `BLOCKED`: human intervention is required

### 6. Fix phase

Claude reads the latest review artifacts and fixes only unresolved review findings.

After fixes:

- rerun tests
- update `.ai-loop/artifacts/current/implementation_report.md`
- send the code back for another review

## Review Discipline

The expected loop is:

1. Claude changes code and updates `implementation_report.md`
2. Codex reviews code and updates `review.md` and `review.json`
3. Claude fixes only what review calls out
4. Repeat until review returns `PASS`

Important rule:

- If a design change is required, Claude should not edit `.ai-loop/artifacts/current/design.md` directly. Claude should append a proposal to `.ai-loop/artifacts/current/design_amendments.md`.

## Testing

Run the full suite:

```powershell
py -m pytest -q
```

Current expectation in this repo is that tests stay green after each fix and each review round should mention the observed test result.

## Practical Notes

- The source of truth for runtime state is `.ai-loop/state/workflow_state.json`, not terminal memory.
- Tests may pass while artifacts are outdated; keep implementation and review artifacts in sync with the actual code state.
- `orchestrator_runtime_spec.md` is the best reference when code behavior and artifact behavior disagree.
- The root `.ai-loop/` in this repo is the live workspace for this repo itself. The `.ai-loop/` inside `template/` is the clean portable starter version.
