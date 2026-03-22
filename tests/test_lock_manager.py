"""Tests for orchestrator.lock_manager."""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from orchestrator.lock_manager import (
    acquire_lock,
    is_lock_expired,
    read_lock,
    recover_stale_lock,
    refresh_lock,
    release_lock,
)
from orchestrator.models import LockRecord, WorkflowState, RequirementRef


def _make_state() -> WorkflowState:
    return WorkflowState(
        run_id="run-20260323-120000-abcdef12",
        phase="designing",
        phase_attempt=1,
        requirement=RequirementRef(sha256="abc"),
    )


class TestAcquireLock:
    def test_creates_lock(self, tmp_path: Path):
        lock_path = tmp_path / "lock.json"
        state = _make_state()
        lock = acquire_lock(state, path=lock_path)
        assert lock.run_id == state.run_id
        assert lock.pid == os.getpid()
        assert lock_path.exists()

    def test_fails_if_locked(self, tmp_path: Path):
        lock_path = tmp_path / "lock.json"
        state = _make_state()
        acquire_lock(state, path=lock_path)
        with pytest.raises(RuntimeError, match="Lock already held"):
            acquire_lock(state, path=lock_path)


class TestReleaseLock:
    def test_removes_file(self, tmp_path: Path):
        lock_path = tmp_path / "lock.json"
        state = _make_state()
        acquire_lock(state, path=lock_path)
        release_lock(lock_path)
        assert not lock_path.exists()

    def test_no_error_if_missing(self, tmp_path: Path):
        release_lock(tmp_path / "missing.json")  # should not raise


class TestIsLockExpired:
    def test_expired(self):
        lock = LockRecord(
            expires_at=(datetime.now(timezone.utc) - timedelta(seconds=10)).isoformat(),
        )
        assert is_lock_expired(lock) is True

    def test_not_expired(self):
        lock = LockRecord(
            expires_at=(datetime.now(timezone.utc) + timedelta(seconds=600)).isoformat(),
        )
        assert is_lock_expired(lock) is False

    def test_no_expires_at(self):
        lock = LockRecord(expires_at=None)
        assert is_lock_expired(lock) is True


class TestReadLock:
    def test_returns_none_if_missing(self, tmp_path: Path):
        assert read_lock(tmp_path / "lock.json") is None

    def test_returns_none_for_null_lock(self, tmp_path: Path):
        lock_path = tmp_path / "lock.json"
        lock_path.write_text(json.dumps({"lock_version": 1, "run_id": None}))
        assert read_lock(lock_path) is None

    def test_reads_valid_lock(self, tmp_path: Path):
        lock_path = tmp_path / "lock.json"
        state = _make_state()
        acquire_lock(state, path=lock_path)
        lock = read_lock(lock_path)
        assert lock is not None
        assert lock.run_id == state.run_id


class TestRefreshLock:
    def test_updates_expires_at(self, tmp_path: Path):
        lock_path = tmp_path / "lock.json"
        state = _make_state()
        lock = acquire_lock(state, ttl_seconds=60, path=lock_path)
        old_expires = lock.expires_at
        new_lock = refresh_lock(lock, ttl_seconds=600, path=lock_path)
        assert new_lock.expires_at != old_expires


class TestRecoverStaleLock:
    def test_recovers_expired_dead_pid(self, tmp_path: Path):
        import socket
        lock_path = tmp_path / "lock.json"
        # Write an expired lock with a dead PID on this host
        lock_data = {
            "lock_version": 1,
            "run_id": "run-old",
            "owner": "orch",
            "pid": 99999999,  # almost certainly dead
            "hostname": socket.gethostname(),
            "phase": "designing",
            "phase_attempt": 1,
            "acquired_at": "2020-01-01T00:00:00Z",
            "expires_at": "2020-01-01T00:01:00Z",
        }
        lock_path.write_text(json.dumps(lock_data))
        assert recover_stale_lock(lock_path) is True
        assert not lock_path.exists()

    def test_no_recovery_if_no_lock(self, tmp_path: Path):
        assert recover_stale_lock(tmp_path / "lock.json") is False
