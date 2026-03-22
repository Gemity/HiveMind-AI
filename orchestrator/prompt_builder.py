"""Prompt assembly for each phase. Stub for first implementation pass."""

from orchestrator.models import WorkflowState


def build_prompt(state: WorkflowState, phase: str) -> str:
    """Build the prompt package for a given phase.

    Not yet implemented - will assemble deterministic prompts from canonical inputs.
    """
    raise NotImplementedError("prompt_builder.build_prompt is not yet implemented")
