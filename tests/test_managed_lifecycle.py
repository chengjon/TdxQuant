from __future__ import annotations

from datetime import datetime, timezone

from tdxquant.managed_lifecycle import (
    acquire_lifecycle_file_lock,
    build_managed_lifecycle_provenance,
    build_process_liveness,
    build_process_ownership_diagnostics,
    build_restart_backoff_projection,
    coerce_process_pid,
    release_lifecycle_file_lock,
)


def test_process_liveness_rejects_invalid_pid_without_probe() -> None:
    calls: list[int] = []

    result = build_process_liveness("not-a-pid", pid_is_alive=lambda pid: calls.append(pid) or True)

    assert result == {
        "schema_version": "tdx.managed_process_lifecycle.process_liveness.v1",
        "pid": None,
        "pid_valid": False,
        "pid_live": False,
        "boundary": "read_only_process_liveness_probe; no_process_control",
    }
    assert calls == []
    assert coerce_process_pid("not-a-pid") == 0


def test_process_liveness_uses_injected_probe_for_valid_pid() -> None:
    result = build_process_liveness("4321", pid_is_alive=lambda pid: pid == 4321)

    assert result["pid"] == 4321
    assert result["pid_valid"] is True
    assert result["pid_live"] is True


def test_process_ownership_diagnostics_reports_owned_process_with_provenance() -> None:
    diagnostics = build_process_ownership_diagnostics(
        {
            "configured": True,
            "check_status": "valid",
            "pid": 4321,
            "owner_token": "owner-token-a",
            "config_hash_matches": True,
        },
        expected_owner_token="owner-token-a",
        process_running=lambda pid: pid == 4321,
        expected_command=["python", "-m", "tdxquant.cli"],
        process_identity_matches=lambda pid, command: pid == 4321
        and command == ["python", "-m", "tdxquant.cli"],
        adapter="unit_test_adapter",
    )

    assert diagnostics["schema_version"] == "tdx.managed_process_lifecycle.process_ownership.v1"
    assert diagnostics["ownership_status"] == "owned"
    assert diagnostics["owned_process"] is True
    assert diagnostics["pid"] == 4321
    assert diagnostics["pid_live"] is True
    assert diagnostics["owner_token_present"] is True
    assert diagnostics["owner_token_matches"] is True
    assert diagnostics["process_identity_checked"] is True
    assert diagnostics["process_identity_matches"] is True
    assert diagnostics["control_allowed"] is True
    assert diagnostics["managed_lifecycle"] == build_managed_lifecycle_provenance(
        adapter="unit_test_adapter",
        primitives=["process_liveness", "process_ownership"],
    )


def test_process_ownership_diagnostics_rejects_non_running_pid() -> None:
    diagnostics = build_process_ownership_diagnostics(
        {
            "configured": True,
            "check_status": "valid",
            "pid": 4321,
            "owner_token": "owner-token-a",
            "config_hash_matches": True,
        },
        expected_owner_token="owner-token-a",
        process_running=lambda _pid: False,
        expected_command=["python", "-m", "tdxquant.cli"],
        process_identity_matches=lambda _pid, _command: True,
        adapter="unit_test_adapter",
    )

    assert diagnostics["ownership_status"] == "process_not_running"
    assert diagnostics["owned_process"] is False
    assert diagnostics["pid_live"] is False
    assert diagnostics["process_identity_checked"] is False
    assert diagnostics["control_allowed"] is False


def test_restart_backoff_projection_is_pure_metadata() -> None:
    created_at = datetime(2026, 6, 1, 1, 2, 3, tzinfo=timezone.utc)

    projection = build_restart_backoff_projection(
        reason="operator_restart",
        created_at=created_at,
        backoff_seconds=30.0,
        boundary="unit_test_backoff_projection_only",
    )

    assert projection == {
        "schema_version": "tdx.managed_process_lifecycle.restart_backoff_projection.v1",
        "status": "active",
        "reason_codes": ["BACKOFF_ACTIVE"],
        "reason": "operator_restart",
        "created_at": "2026-06-01T01:02:03+00:00",
        "retry_after_at": "2026-06-01T01:02:33+00:00",
        "backoff_seconds": 30.0,
        "boundary": "unit_test_backoff_projection_only",
    }


def test_lifecycle_file_lock_reports_acquire_block_and_release_with_provenance(tmp_path) -> None:
    lock_path = tmp_path / "control.lock"

    first = acquire_lifecycle_file_lock(lock_path, adapter="unit_test_adapter")
    second = acquire_lifecycle_file_lock(lock_path, adapter="unit_test_adapter")

    try:
        assert first.lock_acquired is True
        assert first.reason_code == "LOCK_ACQUIRED"
        assert first.to_diagnostics() == {
            "schema_version": "tdx.managed_process_lifecycle.file_lock.v1",
            "path": str(lock_path),
            "strategy": "advisory_flock",
            "lock_attempted": True,
            "lock_acquired": True,
            "reason_code": "LOCK_ACQUIRED",
            "managed_lifecycle": build_managed_lifecycle_provenance(
                adapter="unit_test_adapter",
                primitives=["file_lock"],
            ),
        }
        assert second.lock_acquired is False
        assert second.reason_code == "LOCK_HELD"
        assert second.to_diagnostics()["lock_acquired"] is False
        assert second.to_diagnostics()["managed_lifecycle"]["primitives"] == ["file_lock"]
    finally:
        second_release = release_lifecycle_file_lock(second)
        first_release = release_lifecycle_file_lock(first)

    assert second_release == {
        "schema_version": "tdx.managed_process_lifecycle.file_lock_release.v1",
        "path": str(lock_path),
        "strategy": "advisory_flock",
        "lock_released": False,
        "reason_code": "LOCK_NOT_ACQUIRED",
        "managed_lifecycle": build_managed_lifecycle_provenance(
            adapter="unit_test_adapter",
            primitives=["file_lock"],
        ),
    }
    assert first_release == {
        "schema_version": "tdx.managed_process_lifecycle.file_lock_release.v1",
        "path": str(lock_path),
        "strategy": "advisory_flock",
        "lock_released": True,
        "reason_code": "LOCK_RELEASED",
        "managed_lifecycle": build_managed_lifecycle_provenance(
            adapter="unit_test_adapter",
            primitives=["file_lock"],
        ),
    }
