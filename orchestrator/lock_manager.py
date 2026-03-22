"""Lock management for exclusive phase execution.

Maps to design section 'lock_manager' and runtime spec section 8.
Uses OS-level atomic file creation to prevent TOCTOU races.
"""

from __future__ import annotations

import json
import os
import socket
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from orchestrator.constants import DEFAULT_LOCK_TTL_SECONDS, LOCK_PATH, LOCK_VERSION
from orchestrator.fileutil import atomic_write
from orchestrator.models import LockRecord, WorkflowState


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now_utc().isoformat()


def _parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s)


def acquire_lock(
    state: WorkflowState,
    ttl_seconds: int = DEFAULT_LOCK_TTL_SECONDS,
    path: Path = LOCK_PATH,
) -> LockRecord:
    """Atomically create lock.json. Raises if a valid lock exists."""
    path = Path(path)

    # Check existing lock
    existing = read_lock(path)
    if existing and not is_lock_expired(existing):
        raise RuntimeError(
            f"Lock already held by owner={existing.owner} pid={existing.pid} "
            f"until {existing.expires_at}"
        )

    # If expired lock exists, try recovery first
    if existing and is_lock_expired(existing):
        recover_stale_lock(path)

    now = _now_utc()
    lock = LockRecord(
        lock_version=LOCK_VERSION,
        run_id=state.run_id,
        owner="orchestrator",
        pid=os.getpid(),
        hostname=socket.gethostname(),
        phase=state.phase,
        phase_attempt=state.phase_attempt,
        acquired_at=now.isoformat(),
        expires_at=(now + timedelta(seconds=ttl_seconds)).isoformat(),
    )

    data = json.dumps(lock.to_dict(), indent=2, ensure_ascii=False) + "\n"
    atomic_write(path, data)
    return lock


def release_lock(path: Path = LOCK_PATH) -> None:
    """Remove lock.json."""
    path = Path(path)
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def refresh_lock(
    lock: LockRecord,
    ttl_seconds: int = DEFAULT_LOCK_TTL_SECONDS,
    path: Path = LOCK_PATH,
) -> LockRecord:
    """Update expires_at in lock file."""
    now = _now_utc()
    new_lock = LockRecord(
        lock_version=lock.lock_version,
        run_id=lock.run_id,
        owner=lock.owner,
        pid=lock.pid,
        hostname=lock.hostname,
        phase=lock.phase,
        phase_attempt=lock.phase_attempt,
        acquired_at=lock.acquired_at,
        expires_at=(now + timedelta(seconds=ttl_seconds)).isoformat(),
    )
    data = json.dumps(new_lock.to_dict(), indent=2, ensure_ascii=False) + "\n"
    atomic_write(path, data)
    return new_lock


def read_lock(path: Path = LOCK_PATH) -> Optional[LockRecord]:
    """Read current lock. Returns None if file doesn't exist or is empty/null."""
    path = Path(path)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # An empty/null lock means no active lock
        if not data or not data.get("run_id"):
            return None
        return LockRecord.from_dict(data)
    except (json.JSONDecodeError, KeyError):
        return None


def is_lock_expired(lock: LockRecord) -> bool:
    """Check if lock has passed expires_at."""
    if not lock.expires_at:
        return True
    try:
        expires = _parse_iso(lock.expires_at)
        return _now_utc() > expires
    except ValueError:
        return True


def is_lock_owner_alive(lock: LockRecord) -> bool:
    """Check if the PID in the lock is still running (best-effort).

    Also checks hostname match - if different host, assume alive (can't check).
    """
    if not lock.pid:
        return False

    # If different hostname, we can't check - assume alive for safety
    if lock.hostname and lock.hostname != socket.gethostname():
        return True

    try:
        os.kill(lock.pid, 0)
        return True
    except OSError:
        return False


def recover_stale_lock(path: Path = LOCK_PATH) -> bool:
    """If lock is expired and owner is dead, remove it. Returns True if recovered."""
    lock = read_lock(path)
    if lock is None:
        return False

    if is_lock_expired(lock) and not is_lock_owner_alive(lock):
        release_lock(path)
        return True

    return False
