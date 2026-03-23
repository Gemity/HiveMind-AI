# HiveMind AI

HiveMind AI is a local-first orchestrator for coordinating multiple coding agents through deterministic runtime state, file-based artifacts, and explicit review loops.

Current operating model:

- Codex: design and review
- Claude Code: implementation and fix
- Orchestrator: state, validation, transitions, locks, and audit trail
- Human: initializes runs and resolves blocked decisions

The repository is currently used in a manual human-in-the-loop workflow, while the codebase moves toward more autonomous orchestration.

## Project Goals

- coordinate multiple AI workers without relying on hidden conversational memory
- make artifacts the source of truth
- preserve deterministic phase transitions
- validate outputs before advancing the workflow
- keep an audit trail through files, logs, tests, and git checkpoints

## Repository Layout

Key directories and files:

- `orchestrator/`: Python runtime package
- `tests/`: test suite
- `.ai-loop/`: live coordination workspace
- `orchestrator_runtime_spec.md`: runtime contract and artifact/state schema
- `document.md`: usage guide for the current workflow

Inside `.ai-loop/`:

- `input/`: requirements, human queue, and prompt packages
- `artifacts/current/`: active design, implementation, and review artifacts
- `artifacts/history/`: reserved for archived snapshots
- `state/`: workflow state and lock files
- `logs/`: audit log

## Requirements

- Windows environment with `py`
- Python 3.10+
- `pytest` available through `py -m pytest`

## Install / Run

Run tests:

```powershell
py -m pytest -q
```

Run the CLI:

```powershell
py -m orchestrator --help
```

Common commands:

```powershell
py -m orchestrator status
py -m orchestrator validate
py -m orchestrator check-transition
py -m orchestrator run
py -m orchestrator init --requirement .ai-loop/input/requirement.md --force
```

Or from Git Bash:

```bash
bash run
```

By default, `run` invokes:

- `codex exec -` for `designing` and `reviewing`
- `claude -p` for `implementing` and `fixing`

If your local CLI uses different arguments, override them with:

```powershell
$env:HIVEMIND_CODEX_COMMAND = 'codex exec --cwd {cwd} {prompt_path}'
$env:HIVEMIND_CLAUDE_COMMAND = 'claude -p'
```

Available placeholders inside these command templates:

- `{prompt_path}`
- `{cwd}`
- `{phase}`
- `{run_id}`
- `{iteration}`
- `{phase_attempt}`
- `{agent}`

## Workflow

1. Define the requirement in `.ai-loop/input/requirement.md`.
2. Initialize or inspect run state in `.ai-loop/state/workflow_state.json`.
3. Run `bash run` to generate the prompt package and invoke the responsible agent.
4. Codex produces `design.md`.
5. Claude implements code and updates `implementation_report.md`.
6. Codex reviews and updates `review.md` and `review.json`.
7. Claude fixes review findings until the review result becomes `PASS`.

Important rule:

- If implementation requires a design change, Claude should propose it in `design_amendments.md` instead of directly editing `design.md`.

## Current Status

The runtime already includes:

- workflow state models and persistence
- lock management
- artifact parsing and validation
- transition logic
- CLI commands
- test coverage for the reviewed behaviors

## Docs

- See `document.md` for the practical operator guide.
- See `orchestrator_runtime_spec.md` for the detailed runtime contract.
