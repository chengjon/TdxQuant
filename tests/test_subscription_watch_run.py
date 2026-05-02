from __future__ import annotations

from pathlib import Path

from tdxquant.subscription_watch_run import (
    SUBSCRIPTION_WATCH_CAPABILITY,
    SUBSCRIPTION_WATCH_SCHEMA_VERSION,
    build_subscription_watch_manifest,
    build_subscription_watch_run_paths,
    build_subscription_watch_status_payload,
    build_subscription_watch_summary_payload,
)


def test_build_subscription_watch_run_paths_uses_run_id_directory(tmp_path: Path) -> None:
    paths = build_subscription_watch_run_paths(tmp_path, run_id="run-001")

    assert paths.run_id == "run-001"
    assert paths.run_dir == tmp_path / "run-001"
    assert paths.events_jsonl_path == tmp_path / "run-001" / "events.jsonl"
    assert paths.runner_log_path == tmp_path / "run-001" / "runner.log"
    assert paths.status_path == tmp_path / "run-001" / "status.json"
    assert paths.summary_path == tmp_path / "run-001" / "summary.json"
    assert paths.manifest_path == tmp_path / "run-001" / "manifest.json"


def test_build_subscription_watch_payloads_use_stable_contract_fields(tmp_path: Path) -> None:
    paths = build_subscription_watch_run_paths(tmp_path, run_id="run-001")
    manifest = build_subscription_watch_manifest(
        paths=paths,
        provider="tongdaxin",
        provider_mode="runtime_session",
        requested_symbols=["600519.SH"],
    )
    status = build_subscription_watch_status_payload(
        paths=paths,
        state="running",
        started_at="2026-05-01T08:00:00+00:00",
        updated_at="2026-05-01T08:00:01+00:00",
        session_id="session-001",
        event_count=2,
        last_sequence=2,
        last_event_ts="2026-05-01T08:00:01+00:00",
        last_symbol="600519.SH",
        warnings=[],
    )
    summary = build_subscription_watch_summary_payload(
        paths=paths,
        final_state="completed",
        started_at="2026-05-01T08:00:00+00:00",
        finished_at="2026-05-01T08:00:05+00:00",
        elapsed_ms=5000.0,
        session_id="session-001",
        event_count=2,
        symbol_count=1,
        stop_reason="completed",
        warning_count=0,
    )

    assert manifest["schema_version"] == SUBSCRIPTION_WATCH_SCHEMA_VERSION
    assert manifest["capability"] == SUBSCRIPTION_WATCH_CAPABILITY
    assert manifest["artifacts"]["events_jsonl_path"].endswith("events.jsonl")
    assert status["output_paths"]["summary_path"].endswith("summary.json")
    assert summary["final_state"] == "completed"
    assert summary["stop_reason"] == "completed"
