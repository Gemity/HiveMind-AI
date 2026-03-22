---
artifact_type: design
artifact_version: 1
run_id: run-20260323-000003-be751c2f
iteration: 1
phase: designing
phase_attempt: 1
producer: codex
created_at: 2026-03-23T00:07:21+07:00
design_version: 1
status: approved
---

# Objective

Design a local-first orchestrator runtime that coordinates Codex and Claude Code as independent, stateless workers through deterministic phase control, file-based artifacts, persisted workflow state, and human-gated recovery paths. The design must be specific enough for Claude to implement the Python runtime without relying on hidden conversational context.

# Scope

This design covers the first implementable version of the orchestrator runtime for HiveMind AI.

Included in scope:

- a Python orchestrator process that owns workflow transitions
- persisted runtime state in `.ai-loop/state/workflow_state.json`
- lock acquisition and stale lock recovery through `.ai-loop/state/lock.json`
- artifact production and validation for design, implementation, review, summary, and tech debt files
- prompt package assembly for Codex and Claude in each phase
- manual-first execution where a human can trigger each phase and resolve blocked states
- git checkpoint hooks sufficient for audit and resume support
- loop protection for stale outputs, repeated failures, malformed artifacts, and no-progress cycles

Explicitly not in scope for this version:

- background daemonization or service deployment
- remote agent execution or cloud orchestration
- automatic branch merging without approval
- dynamic discovery of arbitrary new agents
- a rich UI beyond filesystem artifacts and terminal commands

# Constraints

- The system must run locally and not depend on hosted APIs.
- The orchestrator must be the only authority that changes workflow phase.
- Agents must be treated as stateless workers that consume declared inputs and emit declared outputs.
- Cross-agent communication must happen through files under `.ai-loop/`, not through terminal memory.
- Approved design cannot be edited directly by the implementation agent.
- Artifact acceptance must depend on metadata and validation, not only file presence.
- The current delivery stage is human-in-the-loop, so the runtime must support partial manual operation without losing determinism.
- The design should minimize ambiguity so Claude can implement Python modules directly from it.

# Architecture

## Runtime Model

The orchestrator is a single Python entrypoint that executes one phase at a time. It reads `workflow_state.json`, validates preconditions for the current phase, builds a phase-specific prompt package, invokes the appropriate worker, validates produced artifacts, archives outputs, updates state, and then stops or advances to the next phase.

The orchestrator is intentionally centralized. Codex and Claude do not decide the next phase, do not mutate workflow state directly, and do not infer authority from terminal conversation. They only read canonical inputs and write their assigned artifacts.

## Core Modules

### 1. `state_manager`

Responsibilities:

- load and validate `workflow_state.json`
- save state atomically through temporary file plus rename
- expose helpers for updating phase, iteration, loop guards, human gate, and git metadata
- reject unknown schema versions early

Expected functions:

- `load_state() -> WorkflowState`
- `save_state(state) -> None`
- `set_phase(state, phase, phase_attempt)`
- `record_phase_success(state, phase)`
- `open_human_gate(state, reason, details)`

### 2. `lock_manager`

Responsibilities:

- acquire `lock.json` atomically before phase execution
- fail fast when a valid lock exists
- detect stale locks via expiry and process liveness checks
- refresh lock during long agent invocations
- release lock after state commit or controlled failure

Expected functions:

- `acquire_lock(state, ttl_seconds)`
- `refresh_lock(lock)`
- `release_lock()`
- `recover_stale_lock()`

### 3. `artifact_models`

Responsibilities:

- define schemas for markdown front matter and JSON artifacts
- normalize metadata across artifact types
- parse and validate front matter in markdown artifacts

Data models should exist for at least:

- `DesignArtifact`
- `ImplementationReportArtifact`
- `ReviewArtifact`
- `WorkflowState`
- `LockRecord`

### 4. `artifact_validator`

Responsibilities:

- validate presence, parseability, metadata match, required sections, and cross-file consistency
- reject stale outputs using `run_id`, `iteration`, `phase`, `phase_attempt`, and input fingerprint
- classify malformed artifact failures for loop guard accounting

Expected functions:

- `validate_design(path, expected_state)`
- `validate_implementation_report(path, expected_state)`
- `validate_review_pair(review_md_path, review_json_path, expected_state)`
- `compute_file_sha256(path)`

### 5. `prompt_builder`

Responsibilities:

- assemble deterministic prompt packages for each phase from canonical inputs
- inject runtime metadata and expected output contract
- keep prompt content phase-specific so workers do not overstep role boundaries

Outputs should be text files under `.ai-loop/input/` such as:

- `codex_design_prompt.md`
- `claude_implement_prompt.md`
- `codex_review_prompt.md`
- `claude_fix_prompt.md`

### 6. `agent_runner`

Responsibilities:

- run the configured worker command for the current phase
- enforce timeout per phase
- capture exit code and stderr/stdout summary for audit logging
- return control to orchestrator without deciding success on its own

The module should abstract worker invocation so current manual execution can later be swapped with semi-automated CLI execution.

### 7. `transition_engine`

Responsibilities:

- evaluate entry conditions for each phase
- compute next phase from validated artifacts and current state
- enforce human gate and loop protection thresholds
- centralize all transition logic so it is testable without invoking agents

### 8. `history_manager`

Responsibilities:

- copy accepted artifacts from `artifacts/current/` into `artifacts/history/<run_id>/iter-xxxx/`
- preserve immutable snapshots for audit and replay
- generate or update `summary.md`
- append normalized minor issues to `tech_debt.md` when configured

### 9. `git_manager`

Responsibilities:

- record current branch and HEAD when available
- create checkpoint commits after successful phases that changed code or canonical artifacts
- update `last_reviewed_commit` and `last_good_commit`
- degrade gracefully when git access is unavailable or blocked

### 10. `audit_logger`

Responsibilities:

- append structured log events into `.ai-loop/logs/audit.log`
- record phase start, phase end, validation failures, human gate events, and git actions
- keep messages short, append-only, and easy to inspect manually

## Data Flow

1. Human initializes a run by filling `requirement.md` and starting state.
2. Orchestrator loads state and acquires lock.
3. Orchestrator builds the prompt package for the current phase.
4. Assigned worker produces artifacts only in `artifacts/current/`.
5. Orchestrator validates artifacts against state and fingerprints.
6. If valid, orchestrator archives artifacts, updates summary and state, optionally creates git checkpoint, and determines next phase.
7. If invalid or blocked, orchestrator retries, opens human gate, or routes back to designing or fixing depending on transition rules.

## Phase Responsibilities

### Designing

- Worker: Codex
- Inputs: `requirement.md`, `workflow_state.json`, prior `summary.md`, `design_amendments.md`, runtime spec
- Output: approved `design.md`
- Exit rule: move to `implementing` only after design metadata and required sections validate

### Implementing

- Worker: Claude
- Inputs: approved `design.md`, `requirement.md`, `workflow_state.json`, prior `summary.md`, open amendments
- Output: `implementation_report.md`, optional new amendment proposals appended to `design_amendments.md`
- Exit rule: move to `reviewing` only after implementation report validates

### Reviewing

- Worker: Codex
- Inputs: approved design, implementation report, code diff context, workflow state, open amendments
- Output: `review.md` and `review.json`
- Exit rule:
  - `pass` -> `done`
  - `fail` without design change -> `fixing`
  - `fail` with design change -> `designing`
  - `blocked` -> `needs_human`

### Fixing

- Worker: Claude
- Inputs: only unresolved critical issues from `review.json`, current design, workflow state
- Output: `implementation_report.md` with `mode: fix`
- Exit rule: move back to `reviewing` and increment iteration after accepted fix phase

### Needs Human

- Worker: human
- Inputs: human queue entry, latest state, blocking reason
- Output: decision recorded in `human_queue.md` and optionally state update
- Exit rule: continue to a concrete next phase or mark run failed or completed

## Design Governance

`design.md` is the canonical approved design. Claude must not modify it directly.

When Claude discovers a required design change, it may only append a new proposal to `design_amendments.md`. Codex reviews amendments during review or a redesign pass and marks them accepted or rejected. The orchestrator treats accepted blocking amendments as a reason to return to `designing`. Only after a new approved design is produced may the orchestrator mark an amendment as applied.

## Recovery Strategy

- Every state write is atomic.
- Every artifact must match the current run metadata.
- Any crash before state commit leaves the same phase active and allows retry with incremented `phase_attempt`.
- Expired lock recovery requires both expiry and failed liveness check.
- If artifacts are malformed repeatedly, the orchestrator opens the human gate instead of looping indefinitely.

## Assumptions

- The first runtime implementation can be a command-driven CLI script, not a daemon.
- Git integration should be optional at runtime because local permission issues may exist.
- Worker invocation adapters can start simple and manual, then be automated later without rewriting the transition engine.
- Markdown front matter parsing and JSON schema validation are sufficient for the first version.

# Execution Plan

1. Implement shared models and atomic file helpers.
2. Implement `state_manager` and `lock_manager` first because all other modules depend on them.
3. Implement artifact parsing and validation for `design.md`, `implementation_report.md`, `review.md`, and `review.json`.
4. Implement `transition_engine` as pure logic with tests for every allowed phase transition.
5. Implement `prompt_builder` to generate deterministic phase packages under `.ai-loop/input/`.
6. Implement `agent_runner` as a thin adapter that can support manual execution now and automated CLI execution later.
7. Implement `history_manager` and `audit_logger` for archiving and traceability.
8. Implement `git_manager` with graceful fallback when repository access is unavailable.
9. Add a top-level orchestrator CLI that performs one phase execution per command invocation.
10. After core orchestration works for the manual flow, add convenience commands for initializing runs, validating artifacts, and advancing to the next phase.

Suggested Python package layout:

- `orchestrator/__init__.py`
- `orchestrator/models.py`
- `orchestrator/state_manager.py`
- `orchestrator/lock_manager.py`
- `orchestrator/artifact_parser.py`
- `orchestrator/artifact_validator.py`
- `orchestrator/prompt_builder.py`
- `orchestrator/agent_runner.py`
- `orchestrator/transition_engine.py`
- `orchestrator/history_manager.py`
- `orchestrator/git_manager.py`
- `orchestrator/audit_logger.py`
- `orchestrator/cli.py`

# Acceptance Criteria

- A Python orchestrator can load the current run and determine the active phase from `workflow_state.json`.
- The orchestrator can acquire and release `lock.json` safely for one phase execution.
- The orchestrator can validate whether `design.md`, `implementation_report.md`, and the review pair belong to the current run and phase.
- Codex and Claude can exchange work exclusively through `.ai-loop/` artifacts without relying on terminal memory.
- A stale artifact from another phase attempt or iteration is rejected.
- A blocked or malformed phase can route deterministically to retry or `needs_human`.
- The design clearly separates what Claude may implement from what only the orchestrator may decide.
- The architecture can be implemented incrementally, starting with manual command execution and evolving toward greater automation.

# Non-Goals

- Building a fully autonomous multi-agent system in the first implementation.
- Supporting arbitrary third-party agents before the two-worker flow is stable.
- Solving distributed coordination across multiple machines.
- Building a production GUI before the runtime contract is proven locally.
- Hiding all human decisions; the system should surface blocked states instead of pretending to resolve them automatically.
