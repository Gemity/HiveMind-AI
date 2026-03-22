"""Worker invocation adapter. Stub for first implementation pass."""

from orchestrator.models import WorkflowState


def run_agent(state: WorkflowState, phase: str, prompt_path: str) -> dict:
    """Invoke the worker for a given phase.

    Not yet implemented - currently supports manual execution only.
    Will later support CLI-based agent invocation.
    """
    raise NotImplementedError("agent_runner.run_agent is not yet implemented")
