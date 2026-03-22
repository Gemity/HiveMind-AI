# Requirement

Build a local AI orchestrator that enables multiple coding agents to work independently on the same problem while remaining aligned through deterministic runtime control.

## Context

- Project: HiveMind AI
- Goal: Create an orchestrator runtime that coordinates Codex and Claude Code as independent workers through artifacts, workflow state, locks, and explicit transition rules.
- Constraints: Local-first execution, no API dependency, file-based coordination, deterministic state machine, human-in-the-loop during the current project phase, Git-based auditability, crash recovery, and protection against stale or malformed agent outputs.

## Problem Statement

Current agent collaboration is manual and conversational. That makes the system fragile:

- agents can rely on terminal memory instead of shared runtime state
- stale artifacts can be mistaken for fresh outputs
- design, implementation, and review responsibilities can overlap
- the workflow can get stuck without a clear recovery path
- human intervention is required but not yet structured by the runtime

The project must replace this fragile coordination model with a concrete orchestrator that lets agents operate independently while the orchestrator enforces order, validation, and recovery.

## Core Requirements

- The orchestrator must act as the single authority for workflow phase transitions.
- Codex and Claude must behave as stateless workers that read declared inputs and emit declared outputs.
- All inter-agent coordination must happen through filesystem artifacts and workflow state, not hidden conversational context.
- Every artifact must be attributable to a specific run, iteration, phase, and input fingerprint.
- The orchestrator must validate artifacts before advancing the workflow.
- The orchestrator must support the phases `designing`, `implementing`, `reviewing`, `fixing`, `needs_human`, and `done`.
- The orchestrator must support design governance where implementation agents cannot directly mutate the approved design.
- The orchestrator must detect repeated failures, malformed artifacts, stale outputs, and no-progress loops.
- The orchestrator must support crash-safe resume from persisted state.
- The orchestrator must preserve an audit trail through logs, archived artifacts, and Git checkpoints.

## Target Roles

- Codex: design generation, design amendment review, implementation review
- Claude Code: implementation, critical issue fixing, design amendment proposals
- Orchestrator: prompt assembly, state transitions, artifact validation, lock handling, loop protection, audit logging
- Human: approve or reject blocked decisions, initialize runs, resolve ambiguous design tradeoffs during this manual phase

## Scope

- Define the runtime contract for agent collaboration.
- Define artifact schemas and validation rules.
- Define `workflow_state.json`, lock behavior, and transition rules.
- Create the local folder structure and bootstrap files used by the runtime.
- Implement the orchestrator code needed to run the workflow locally.
- Support the current manual workflow first, with a path toward more autonomous execution later.

## Out Of Scope For Initial Version

- Full autonomous operation without any human oversight
- Cloud orchestration or remote distributed execution
- General multi-agent marketplace or dynamic agent discovery
- Rich web UI beyond basic local runtime operation
- Automatic merge to protected branches without explicit approval

## Success Criteria

- A run can be initialized from a requirement and persisted into workflow state.
- Codex and Claude can work in separate steps using only the files under `.ai-loop/`.
- The orchestrator can reject stale or malformed artifacts instead of silently advancing.
- The orchestrator can move deterministically between design, implementation, review, and fix phases.
- Blocking conditions are routed into a structured human decision queue.
- The runtime can resume safely after interruption without losing run identity or phase context.
- Each iteration leaves behind enough logs, artifacts, and Git metadata to audit what happened.

## Notes For Agents

- This project exists to reduce dependency on conversational memory and manual orchestration.
- Treat `.ai-loop/state/workflow_state.json` and validated artifacts as the source of truth.
- Do not infer authority from who spoke last in the terminal.
- When design changes are needed, propose or review amendments instead of mutating approved design informally.
- During the current project stage, assume a human may initialize, unblock, or redirect the run between phases.
