# Codex Design Prompt Package

## Role

You are Codex acting in the `designing` phase of a local AI orchestrator runtime.

Your responsibility in this phase is limited to design work. You are not implementing Python code in this step. You must produce a complete and approved design artifact that the implementation agent can follow without relying on conversational memory.

## Runtime Metadata

- run_id: `run-20260323-000003-be751c2f`
- iteration: `1`
- phase: `designing`
- phase_attempt: `1`
- producer: `codex`
- artifact_version: `1`
- target_design_version: `1`
- requirement_sha256: `a030d8d8f7b021f3fbb3f89529bfd66b880b2a0bc8b0d43f39f84c78601ddeb8`

## Objective

Design a local AI orchestrator that allows multiple coding agents to work independently on the same problem while staying aligned through deterministic runtime control.

The immediate goal of this phase is to create the first approved `design.md` for the project.

## Canonical Inputs

Read these files as the source of truth for this phase:

- `.ai-loop/input/requirement.md`
- `.ai-loop/state/workflow_state.json`
- `.ai-loop/artifacts/current/summary.md`
- `.ai-loop/artifacts/current/design_amendments.md`
- `orchestrator_runtime_design.md`
- `orchestrator_runtime_spec.md`

Priority order when there is tension:

1. `workflow_state.json`
2. `requirement.md`
3. `orchestrator_runtime_spec.md`
4. `orchestrator_runtime_design.md`
5. `summary.md`

## Design Goals

Your design should make the orchestrator practical to implement and robust in real use.

At minimum, it should cover:

- runtime architecture and module boundaries
- responsibilities of orchestrator, Codex, Claude, and human gate
- artifact lifecycle and validation flow
- workflow execution model and transition handling
- lock handling and recovery strategy
- state persistence and resume behavior
- prompt assembly strategy for each phase
- git checkpoint strategy
- malformed artifact handling
- loop protection and human escalation
- manual-first operation now, with a path to more automation later

## Constraints

- Local-first execution only
- No API dependency
- File-based coordination only
- Deterministic state machine
- Agents must behave as stateless workers
- Design governance must prevent implementation agents from mutating approved design directly
- The current project phase still includes human intervention between steps
- The design should be specific enough that Claude can later implement Python modules from it

## Required Output

Write or replace `.ai-loop/artifacts/current/design.md`.

The file must begin with this metadata block, with `created_at` filled to the actual current timestamp:

```yaml
---
artifact_type: design
artifact_version: 1
run_id: run-20260323-000003-be751c2f
iteration: 1
phase: designing
phase_attempt: 1
producer: codex
created_at: <ISO 8601 timestamp with timezone>
design_version: 1
status: approved
---
```

Then produce these required sections exactly:

```markdown
# Objective
# Scope
# Constraints
# Architecture
# Execution Plan
# Acceptance Criteria
# Non-Goals
```

## Quality Bar

- Make the design implementation-ready, not high-level only.
- Prefer explicit responsibilities and contracts over broad advice.
- Call out module boundaries and data flow clearly.
- Make sure Claude could implement Python code from this design without needing hidden context.
- If you identify unresolved decisions, list them explicitly and mark whether they block implementation.

## Amendment Rules

- Do not treat yourself as the implementation agent.
- Do not write `implementation_report.md` or review artifacts in this phase.
- If you think the current requirement is insufficient, note assumptions inside the design instead of changing the workflow state.
- If a design amendment is needed in the future, it must go through `design_amendments.md`, but for this first design pass you should produce the best complete design possible.

## Completion Condition

You are done only when `.ai-loop/artifacts/current/design.md` contains a complete approved design artifact for this run and phase.
