# HiveMind AI Usage Guide

## Overview

This project is a local AI orchestrator for coordinating multiple coding agents through files, workflow state, and explicit review artifacts.

Current role split:

- Codex: design and review
- Claude Code: implementation and fix
- Orchestrator: runtime logic, validation, transitions, and audit trail
- Human: initializes runs, moves work between agents, and resolves blocked decisions

This repository is still operated in a manual human-in-the-loop mode, but the codebase and `.ai-loop/` structure are designed to evolve toward more autonomous execution.

## Repository Structure

Important paths:

- [orchestrator](D:\AI Project\HiveMind AI\orchestrator): Python package for the runtime
- [tests](D:\AI Project\HiveMind AI\tests): test suite
- [orchestrator_runtime_spec.md](D:\AI Project\HiveMind AI\orchestrator_runtime_spec.md): executable runtime contract
- [orchestrator_runtime_design.md](D:\AI Project\HiveMind AI\orchestrator_runtime_design.md): earlier design draft
- [.ai-loop](D:\AI Project\HiveMind AI\.ai-loop): live coordination workspace for agents

The `.ai-loop` directory is the operational center:

- [.ai-loop/input](D:\AI Project\HiveMind AI\.ai-loop\input): requirements, human queue, and prompt packages
- [.ai-loop/artifacts/current](D:\AI Project\HiveMind AI\.ai-loop\artifacts\current): live artifacts for the current run
- [.ai-loop/artifacts/history](D:\AI Project\HiveMind AI\.ai-loop\artifacts\history): reserved for archived run snapshots
- [.ai-loop/state](D:\AI Project\HiveMind AI\.ai-loop\state): workflow state and lock files
- [.ai-loop/logs](D:\AI Project\HiveMind AI\.ai-loop\logs): audit log

## Main Runtime Files

These are the files most often touched during manual orchestration:

- [requirement.md](D:\AI Project\HiveMind AI\.ai-loop\input\requirement.md): problem statement and success criteria
- [workflow_state.json](D:\AI Project\HiveMind AI\.ai-loop\state\workflow_state.json): canonical current state
- [design.md](D:\AI Project\HiveMind AI\.ai-loop\artifacts\current\design.md): approved design artifact
- [design_amendments.md](D:\AI Project\HiveMind AI\.ai-loop\artifacts\current\design_amendments.md): proposed design changes
- [implementation_report.md](D:\AI Project\HiveMind AI\.ai-loop\artifacts\current\implementation_report.md): implementation/fix report from Claude
- [review.md](D:\AI Project\HiveMind AI\.ai-loop\artifacts\current\review.md): human-readable review result from Codex
- [review.json](D:\AI Project\HiveMind AI\.ai-loop\artifacts\current\review.json): machine-readable review result
- [summary.md](D:\AI Project\HiveMind AI\.ai-loop\artifacts\current\summary.md): condensed status summary
- [human_queue.md](D:\AI Project\HiveMind AI\.ai-loop\input\human_queue.md): manual decision log

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
py -m orchestrator init --requirement .ai-loop/input/requirement.md --force
```

## Manual Workflow

### 1. Prepare the requirement

Edit [requirement.md](D:\AI Project\HiveMind AI\.ai-loop\input\requirement.md) so it clearly states:

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

### 3. Design phase

Codex produces or updates:

- [design.md](D:\AI Project\HiveMind AI\.ai-loop\artifacts\current\design.md)

Prompt package used for this phase:

- [codex_design_prompt.md](D:\AI Project\HiveMind AI\.ai-loop\input\codex_design_prompt.md)

### 4. Implement phase

Claude implements code based on the approved design and produces:

- code changes in [orchestrator](D:\AI Project\HiveMind AI\orchestrator)
- [implementation_report.md](D:\AI Project\HiveMind AI\.ai-loop\artifacts\current\implementation_report.md)

Prompt package used for this phase:

- [claude_implement_prompt.md](D:\AI Project\HiveMind AI\.ai-loop\input\claude_implement_prompt.md)

### 5. Review phase

Codex reviews the implementation and updates:

- [review.md](D:\AI Project\HiveMind AI\.ai-loop\artifacts\current\review.md)
- [review.json](D:\AI Project\HiveMind AI\.ai-loop\artifacts\current\review.json)

Interpretation:

- `PASS`: implementation is accepted
- `FAIL`: Claude should fix the listed issues
- `BLOCKED`: human intervention is required

### 6. Fix phase

Claude reads the latest review artifacts and fixes only the unresolved review findings.

After fixes:

- rerun tests
- update [implementation_report.md](D:\AI Project\HiveMind AI\.ai-loop\artifacts\current\implementation_report.md)
- send the code back for another review

## Review Discipline

The expected loop is:

1. Claude changes code and updates `implementation_report.md`
2. Codex reviews code and updates `review.md` and `review.json`
3. Claude fixes only what review calls out
4. Repeat until review returns `PASS`

Important rule:

- If a design change is required, Claude should not edit [design.md](D:\AI Project\HiveMind AI\.ai-loop\artifacts\current\design.md) directly. Claude should append a proposal to [design_amendments.md](D:\AI Project\HiveMind AI\.ai-loop\artifacts\current\design_amendments.md).

## Testing

Run the full suite:

```powershell
py -m pytest -q
```

Current expectation in this repo is that tests stay green after each fix and each review round should mention the observed test result.

## Git Workflow

Recommended pattern:

1. implement or review
2. update artifacts in `.ai-loop/artifacts/current/`
3. commit the code or artifact checkpoint

Examples of checkpoints already used in this repo:

- implementation/spec setup commits
- review artifact commits
- re-review commits

This keeps the audit trail aligned with the orchestrator concept.

## Practical Notes

- The source of truth for runtime state is [workflow_state.json](D:\AI Project\HiveMind AI\.ai-loop\state\workflow_state.json), not terminal memory.
- Tests may pass while artifacts are outdated; keep [implementation_report.md](D:\AI Project\HiveMind AI\.ai-loop\artifacts\current\implementation_report.md), [review.md](D:\AI Project\HiveMind AI\.ai-loop\artifacts\current\review.md), and [review.json](D:\AI Project\HiveMind AI\.ai-loop\artifacts\current\review.json) in sync with the actual code state.
- [orchestrator_runtime_spec.md](D:\AI Project\HiveMind AI\orchestrator_runtime_spec.md) is the best reference when code behavior and artifact behavior disagree.

## Suggested Daily Routine

```powershell
git status --short
py -m pytest -q
py -m orchestrator status
py -m orchestrator validate
py -m orchestrator check-transition
```

Then:

- if implementation changed, update `implementation_report.md`
- if review changed, update `review.md` and `review.json`
- commit the resulting checkpoint
