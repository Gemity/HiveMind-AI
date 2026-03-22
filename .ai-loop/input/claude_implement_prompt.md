# Claude Implement Prompt Package

## Role

You are Claude Code acting in the `implementing` phase of a local AI orchestrator runtime.

Your responsibility in this phase is to implement Python code that realizes the approved design. You are not the design authority, and you are not the review authority. You must treat the approved design artifact as binding unless you encounter a genuine need for a design amendment.

## Runtime Metadata

- run_id: `run-20260323-000003-be751c2f`
- iteration: `1`
- target_phase: `implementing`
- expected_phase_attempt: `1`
- producer: `claude`
- artifact_version: `1`
- approved_design_version: `1`
- requirement_sha256: `a030d8d8f7b021f3fbb3f89529bfd66b880b2a0bc8b0d43f39f84c78601ddeb8`
- design_sha256: `bf6e57351f802136a275530dd37af5825499fd25ad30fa88f4affe4480c82e3b`
- review_target_commit: `null`

## Objective

Implement the first working Python skeleton of the orchestrator described in the approved design. The output should establish the project structure and core runtime foundations so later iterations can validate artifacts, manage state, and drive phase transitions predictably.

## Canonical Inputs

Read these files as the source of truth for this phase:

- `.ai-loop/input/requirement.md`
- `.ai-loop/state/workflow_state.json`
- `.ai-loop/artifacts/current/design.md`
- `.ai-loop/artifacts/current/summary.md`
- `.ai-loop/artifacts/current/design_amendments.md`
- `orchestrator_runtime_spec.md`

Priority order when there is tension:

1. `.ai-loop/artifacts/current/design.md`
2. `.ai-loop/state/workflow_state.json`
3. `.ai-loop/input/requirement.md`
4. `orchestrator_runtime_spec.md`
5. `.ai-loop/artifacts/current/summary.md`

## Implementation Scope

Implement the initial Python runtime skeleton described by the approved design.

The first implementation pass should prioritize these areas:

- create the `orchestrator/` package structure
- define shared models for workflow state, lock records, and artifact metadata
- implement atomic read and write helpers where needed
- implement `state_manager` for loading, validating, and saving workflow state
- implement `lock_manager` for acquiring, releasing, and recovering `lock.json`
- implement artifact parsing and validation foundations for markdown front matter and JSON artifacts
- implement a pure `transition_engine` skeleton that can resolve legal next phases from state and validated artifacts
- implement a minimal CLI entrypoint that can at least load state and report the active phase or run a dry phase check

It is acceptable if some modules are partial, but the code should form a coherent base that future iterations can extend without rework.

## Constraints

- Implement Python code only.
- Do not edit `.ai-loop/artifacts/current/design.md` directly.
- Do not change workflow phase or claim implementation success without producing the required report artifact.
- If you discover a design issue that blocks correct implementation, append a new proposed amendment to `.ai-loop/artifacts/current/design_amendments.md` instead of informally changing the design.
- Keep the code local-first and file-based.
- Prefer clear, testable modules over premature abstraction.
- Follow the approved module boundaries unless there is a compelling reason to adapt names slightly for Python ergonomics.

## Expected Code Targets

The approved design suggests a package layout similar to:

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

You may add small helper modules if they reduce complexity, but keep the structure aligned with the design.

## Required Output Artifact

Write or replace `.ai-loop/artifacts/current/implementation_report.md`.

The file must begin with this metadata block, with `created_at` filled to the actual current timestamp:

```yaml
---
artifact_type: implementation_report
artifact_version: 1
run_id: run-20260323-000003-be751c2f
iteration: 1
phase: implementing
phase_attempt: 1
producer: claude
created_at: <ISO 8601 timestamp with timezone>
mode: implement
result: success
---
```

Then produce these required sections exactly:

```markdown
# Summary
# Files Changed
# Tests Run
# Known Risks
# Amendment Requests
```

Rules for the report:

- `Files Changed` must list concrete file paths.
- `Tests Run` must list commands and outcomes, or explicitly state that no tests were run.
- `Amendment Requests` must be `none` or list amendment IDs already appended to `design_amendments.md`.
- If implementation is incomplete or blocked, set `result` accordingly and explain the gap honestly.

## Quality Bar

- Create code that is directly useful, not placeholder-only scaffolding.
- Make the modules readable and easy for later review by Codex.
- Keep orchestration logic deterministic and explicit.
- Prefer simple, composable Python over clever abstractions.
- Leave the repo in a state where the next phase can review concrete code and artifacts.

## Completion Condition

You are done only when both conditions are true:

1. The Python codebase contains the initial orchestrator implementation aligned with the approved design.
2. `.ai-loop/artifacts/current/implementation_report.md` accurately reports what was implemented for this run and phase.
