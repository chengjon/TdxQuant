from __future__ import annotations

from dataclasses import dataclass
import errno
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

try:
    import fcntl
except ModuleNotFoundError:  # pragma: no cover - exercised on Windows
    fcntl = None  # type: ignore[assignment]

MANAGED_LIFECYCLE_MODULE = "tdxquant.managed_lifecycle"
MANAGED_LIFECYCLE_PROVENANCE_SCHEMA_VERSION = "tdx.managed_process_lifecycle.provenance.v1"
PROCESS_LIVENESS_SCHEMA_VERSION = "tdx.managed_process_lifecycle.process_liveness.v1"
PROCESS_OWNERSHIP_SCHEMA_VERSION = "tdx.managed_process_lifecycle.process_ownership.v1"
FILE_LOCK_SCHEMA_VERSION = "tdx.managed_process_lifecycle.file_lock.v1"
FILE_LOCK_RELEASE_SCHEMA_VERSION = "tdx.managed_process_lifecycle.file_lock_release.v1"
RESTART_BACKOFF_PROJECTION_SCHEMA_VERSION = (
    "tdx.managed_process_lifecycle.restart_backoff_projection.v1"
)
PROCESS_LIVENESS_BOUNDARY = "read_only_process_liveness_probe; no_process_control"
PROCESS_OWNERSHIP_BOUNDARY = "read_only_process_ownership_diagnostics; no_process_control"
MANAGED_LIFECYCLE_PROVENANCE_BOUNDARY = "diagnostic_provenance_only; no_lifecycle_control"


@dataclass
class ManagedLifecycleFileLock:
    path: Path
    strategy: str
    adapter: str
    handle: Any | None = None
    lock_acquired: bool = False
    reason_code: str = "LOCK_NOT_ATTEMPTED"

    def to_diagnostics(self) -> dict[str, Any]:
        return {
            "schema_version": FILE_LOCK_SCHEMA_VERSION,
            "path": str(self.path),
            "strategy": self.strategy,
            "lock_attempted": True,
            "lock_acquired": self.lock_acquired,
            "reason_code": self.reason_code,
            "managed_lifecycle": build_managed_lifecycle_provenance(
                adapter=self.adapter,
                primitives=["file_lock"],
            ),
        }

    def fileno(self) -> int:
        if self.handle is None:
            raise ValueError("lock is not acquired")
        return self.handle.fileno()

    def close(self) -> None:
        if self.handle is not None:
            self.handle.close()
            self.handle = None


def coerce_process_pid(raw_pid: Any) -> int:
    try:
        pid = int(raw_pid or 0)
    except (TypeError, ValueError):
        return 0
    return pid if pid > 0 else 0


def process_pid_alive(pid: int) -> bool:
    resolved_pid = coerce_process_pid(pid)
    if resolved_pid < 1:
        return False
    try:
        os.kill(resolved_pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def build_process_liveness(
    raw_pid: Any,
    *,
    pid_is_alive: Any | None = None,
) -> dict[str, Any]:
    pid = coerce_process_pid(raw_pid)
    if pid < 1:
        return {
            "schema_version": PROCESS_LIVENESS_SCHEMA_VERSION,
            "pid": None,
            "pid_valid": False,
            "pid_live": False,
            "boundary": PROCESS_LIVENESS_BOUNDARY,
        }
    probe = pid_is_alive or process_pid_alive
    return {
        "schema_version": PROCESS_LIVENESS_SCHEMA_VERSION,
        "pid": pid,
        "pid_valid": True,
        "pid_live": bool(probe(pid)),
        "boundary": PROCESS_LIVENESS_BOUNDARY,
    }


def build_managed_lifecycle_provenance(
    *,
    adapter: str,
    primitives: list[str] | tuple[str, ...],
) -> dict[str, Any]:
    return {
        "schema_version": MANAGED_LIFECYCLE_PROVENANCE_SCHEMA_VERSION,
        "module": MANAGED_LIFECYCLE_MODULE,
        "adapter": adapter,
        "primitives": list(primitives),
        "boundary": MANAGED_LIFECYCLE_PROVENANCE_BOUNDARY,
    }


def acquire_lifecycle_file_lock(
    lock_path: str | Path,
    *,
    adapter: str = "managed_process_lifecycle",
    strategy: str = "advisory_flock",
) -> ManagedLifecycleFileLock:
    path = Path(lock_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if strategy == "exclusive_lockfile":
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            return ManagedLifecycleFileLock(
                path=path,
                strategy=strategy,
                adapter=adapter,
                lock_acquired=False,
                reason_code="LOCK_HELD",
            )
        except OSError as exc:
            return ManagedLifecycleFileLock(
                path=path,
                strategy=strategy,
                adapter=adapter,
                lock_acquired=False,
                reason_code=f"LOCK_UNAVAILABLE:{exc.__class__.__name__}",
            )
        try:
            handle = os.fdopen(fd, "w", encoding="utf-8")
        except OSError as exc:
            os.close(fd)
            return ManagedLifecycleFileLock(
                path=path,
                strategy=strategy,
                adapter=adapter,
                lock_acquired=False,
                reason_code=f"LOCK_UNAVAILABLE:{exc.__class__.__name__}",
            )
        return ManagedLifecycleFileLock(
            path=path,
            strategy=strategy,
            adapter=adapter,
            handle=handle,
            lock_acquired=True,
            reason_code="LOCK_ACQUIRED",
        )

    if strategy != "advisory_flock":
        raise ValueError(f"unsupported lifecycle file lock strategy: {strategy}")

    if fcntl is None:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            return ManagedLifecycleFileLock(
                path=path,
                strategy=strategy,
                adapter=adapter,
                lock_acquired=False,
                reason_code="LOCK_HELD",
            )
        except OSError as exc:
            return ManagedLifecycleFileLock(
                path=path,
                strategy=strategy,
                adapter=adapter,
                lock_acquired=False,
                reason_code=f"LOCK_UNAVAILABLE:{exc.__class__.__name__}",
            )
        try:
            handle = os.fdopen(fd, "w", encoding="utf-8")
        except OSError as exc:
            os.close(fd)
            return ManagedLifecycleFileLock(
                path=path,
                strategy=strategy,
                adapter=adapter,
                lock_acquired=False,
                reason_code=f"LOCK_UNAVAILABLE:{exc.__class__.__name__}",
            )
        return ManagedLifecycleFileLock(
            path=path,
            strategy=strategy,
            adapter=adapter,
            handle=handle,
            lock_acquired=True,
            reason_code="LOCK_ACQUIRED",
        )

    handle = path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        handle.close()
        if exc.errno in {errno.EACCES, errno.EAGAIN}:
            return ManagedLifecycleFileLock(
                path=path,
                strategy=strategy,
                adapter=adapter,
                lock_acquired=False,
                reason_code="LOCK_HELD",
            )
        return ManagedLifecycleFileLock(
            path=path,
            strategy=strategy,
            adapter=adapter,
            lock_acquired=False,
            reason_code=f"LOCK_UNAVAILABLE:{exc.__class__.__name__}",
        )
    return ManagedLifecycleFileLock(
        path=path,
        strategy=strategy,
        adapter=adapter,
        handle=handle,
        lock_acquired=True,
        reason_code="LOCK_ACQUIRED",
    )


def release_lifecycle_file_lock(lock: ManagedLifecycleFileLock) -> dict[str, Any]:
    released = False
    reason_code = "LOCK_NOT_ACQUIRED"
    if lock.lock_acquired:
        try:
            if lock.strategy == "advisory_flock":
                if lock.handle is not None:
                    if fcntl is not None:
                        fcntl.flock(lock.handle.fileno(), fcntl.LOCK_UN)
                    released = True
            elif lock.strategy == "exclusive_lockfile":
                released = True
            else:
                reason_code = "LOCK_RELEASE_UNSUPPORTED"
        except OSError as exc:
            reason_code = f"LOCK_RELEASE_FAILED:{exc.__class__.__name__}"
            released = False
        finally:
            try:
                lock.close()
            except OSError as exc:
                reason_code = f"LOCK_RELEASE_FAILED:{exc.__class__.__name__}"
                released = False
            if lock.strategy == "exclusive_lockfile" or (lock.strategy == "advisory_flock" and fcntl is None):
                try:
                    lock.path.unlink()
                except FileNotFoundError:
                    released = released or lock.lock_acquired
                except OSError as exc:
                    reason_code = f"LOCK_RELEASE_FAILED:{exc.__class__.__name__}"
                    released = False
        if released and reason_code != "LOCK_RELEASE_UNSUPPORTED":
            reason_code = "LOCK_RELEASED"
    return {
        "schema_version": FILE_LOCK_RELEASE_SCHEMA_VERSION,
        "path": str(lock.path),
        "strategy": lock.strategy,
        "lock_released": released,
        "reason_code": reason_code,
        "managed_lifecycle": build_managed_lifecycle_provenance(
            adapter=lock.adapter,
            primitives=["file_lock"],
        ),
    }


def build_process_ownership_diagnostics(
    statefile_check: dict[str, Any] | None,
    *,
    expected_owner_token: str | None = None,
    process_running: Any | None = None,
    expected_command: list[str] | None = None,
    process_identity_matches: Any | None = None,
    adapter: str = "managed_process_lifecycle",
) -> dict[str, Any]:
    pid = statefile_check.get("pid") if isinstance(statefile_check, dict) else None
    owner_token = statefile_check.get("owner_token") if isinstance(statefile_check, dict) else None
    owner_token_present = isinstance(owner_token, str) and bool(owner_token)
    expected_owner_token_present = isinstance(expected_owner_token, str) and bool(expected_owner_token)
    owner_token_matches = None
    if expected_owner_token_present:
        owner_token_matches = owner_token == expected_owner_token

    diagnostics: dict[str, Any] = {
        "schema_version": PROCESS_OWNERSHIP_SCHEMA_VERSION,
        "ownership_status": "unknown_process_identity",
        "owned_process": False,
        "pid": pid if isinstance(pid, int) else None,
        "pid_live": None,
        "owner_token_present": owner_token_present,
        "owner_token_matches": owner_token_matches,
        "config_hash_matches": statefile_check.get("config_hash_matches")
        if isinstance(statefile_check, dict)
        else None,
        "process_identity_checked": False,
        "process_identity_matches": None,
        "control_allowed": False,
        "managed_lifecycle": build_managed_lifecycle_provenance(
            adapter=adapter,
            primitives=["process_liveness", "process_ownership"],
        ),
        "boundary": PROCESS_OWNERSHIP_BOUNDARY,
    }

    if not isinstance(statefile_check, dict):
        diagnostics["ownership_status"] = "invalid_statefile"
        return diagnostics
    if statefile_check.get("configured") is not True:
        diagnostics["ownership_status"] = "not_configured"
        return diagnostics
    if statefile_check.get("check_status") == "missing":
        diagnostics["ownership_status"] = "missing_statefile"
        return diagnostics
    if statefile_check.get("check_status") != "valid":
        diagnostics["ownership_status"] = "invalid_statefile"
        return diagnostics
    if statefile_check.get("stale") is True:
        diagnostics["ownership_status"] = "stale_statefile"
        return diagnostics
    if statefile_check.get("config_hash_matches") is not True:
        diagnostics["ownership_status"] = "config_hash_mismatch"
        return diagnostics
    if expected_owner_token_present and owner_token_matches is not True:
        diagnostics["ownership_status"] = "owner_token_mismatch"
        return diagnostics
    if not isinstance(pid, int):
        diagnostics["ownership_status"] = "invalid_statefile"
        return diagnostics

    if callable(process_running):
        try:
            diagnostics["pid_live"] = bool(process_running(pid))
        except OSError:
            diagnostics["pid_live"] = None
    if diagnostics["pid_live"] is False:
        diagnostics["ownership_status"] = "process_not_running"
        return diagnostics
    if diagnostics["pid_live"] is not True:
        diagnostics["ownership_status"] = "unknown_process_identity"
        return diagnostics

    if callable(process_identity_matches):
        diagnostics["process_identity_checked"] = True
        command = expected_command or []
        try:
            identity_matches = process_identity_matches(pid, command)
        except OSError:
            identity_matches = None
        if identity_matches is True:
            diagnostics["process_identity_matches"] = True
        elif identity_matches is False:
            diagnostics["process_identity_matches"] = False
            diagnostics["ownership_status"] = "process_identity_mismatch"
            return diagnostics
        else:
            diagnostics["process_identity_matches"] = None
            diagnostics["ownership_status"] = "unknown_process_identity"
            return diagnostics

    diagnostics["ownership_status"] = "owned"
    diagnostics["owned_process"] = True
    diagnostics["control_allowed"] = True
    return diagnostics


def build_restart_backoff_projection(
    *,
    reason: str,
    created_at: datetime,
    backoff_seconds: float | int,
    boundary: str,
) -> dict[str, Any]:
    resolved_backoff_seconds = max(float(backoff_seconds), 0.0)
    retry_after_at = created_at + timedelta(seconds=resolved_backoff_seconds)
    return {
        "schema_version": RESTART_BACKOFF_PROJECTION_SCHEMA_VERSION,
        "status": "active",
        "reason_codes": ["BACKOFF_ACTIVE"],
        "reason": reason,
        "created_at": created_at.isoformat(),
        "retry_after_at": retry_after_at.isoformat(),
        "backoff_seconds": resolved_backoff_seconds,
        "boundary": boundary,
    }
