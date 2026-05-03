import json
from pathlib import Path

from tdxquant.provider_discovery import list_provider_capabilities
from tdxquant.replay_fixtures import load_provider_replay_fixture
from tdxquant.replay_provider import execute_sync_replay, materialize_subscription_watch_replay
from tdxquant.subscription_watch_run import build_subscription_watch_run_paths


def test_execute_sync_replay_uses_default_runtime_capabilities_fixture() -> None:
    result = execute_sync_replay("runtime.capabilities")

    assert result.ok is True
    assert result.message == "listed provider capabilities"
    assert result.data["summary"]["total"] == 5
    capability_names = {item["name"] for item in result.data["capabilities"]}
    assert "block.read_watchlist_snapshot" in capability_names
    assert result.data["replay_source"]["fixture"] == "runtime-capabilities-success"
    assert result._provider_contract["runtime"]["mode"] == "replay"


def test_execute_sync_replay_uses_default_block_read_watchlist_fixture() -> None:
    result = execute_sync_replay("block.read_watchlist_snapshot")

    assert result.ok is True
    assert result.data["snapshot"]["block_code"] == "ZXG"
    assert result.data["snapshot"]["symbols"] == ["600519.SH", "000001.SZ"]
    assert result.data["replay_source"]["fixture"] == "block-read-watchlist-success"


def test_block_read_watchlist_discovery_metadata_is_exposed() -> None:
    capability = next(
        item for item in list_provider_capabilities() if item["name"] == "block.read_watchlist_snapshot"
    )

    assert capability["query_metadata"] == {
        "query_shapes": [
            {
                "query_kind": "block.read_watchlist_snapshot",
                "selectors": ["block_code"],
                "query_params": [],
            }
        ],
        "supports_empty_results": True,
        "returns_ordered_symbols": True,
        "deduplicates_members": True,
        "normalizes_symbols": True,
    }


def test_execute_sync_replay_rejects_malformed_custom_fixture_path(tmp_path: Path) -> None:
    fixture_path = tmp_path / "bad-runtime-capabilities.json"
    fixture_path.write_text(json.dumps(["bad"]), encoding="utf-8")

    result = execute_sync_replay(
        "runtime.capabilities",
        replay_fixture_path=str(fixture_path),
    )

    assert result.ok is False
    assert result.code.value == "invalid_request"
    assert "JSON object" in result.message


def test_materialize_subscription_watch_replay_rewrites_run_identity_for_directory_source(tmp_path: Path) -> None:
    source_dir = tmp_path / "source-run"
    source_dir.mkdir()
    source_manifest = load_provider_replay_fixture("subscription-watch-manifest")
    source_status = load_provider_replay_fixture("subscription-watch-status-completed")
    source_summary = load_provider_replay_fixture("subscription-watch-summary-completed")
    source_events = load_provider_replay_fixture("subscription-watch-events")

    (source_dir / "manifest.json").write_text(json.dumps(source_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (source_dir / "status.json").write_text(json.dumps(source_status, ensure_ascii=False, indent=2), encoding="utf-8")
    (source_dir / "summary.json").write_text(json.dumps(source_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (source_dir / "events.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in source_events) + "\n",
        encoding="utf-8",
    )

    paths = build_subscription_watch_run_paths(tmp_path / "materialized", run_id="run-002")
    materialized = materialize_subscription_watch_replay(
        paths=paths,
        replay_fixture_path=str(source_dir),
    )

    assert materialized.manifest["run_id"] == "run-002"
    assert materialized.manifest["provider_mode"] == "replay"
    assert materialized.status["run_id"] == "run-002"
    assert materialized.summary["run_id"] == "run-002"
    assert materialized.events[0]["run_id"] == "run-002"
    assert materialized.status["output_paths"]["run_dir"].endswith("run-002")
    assert materialized.summary["artifacts"]["events_jsonl_path"].endswith("run-002/events.jsonl")
    assert paths.manifest_path.exists()
    assert paths.status_path.exists()
    assert paths.summary_path.exists()
    assert paths.events_jsonl_path.exists()
    assert paths.events_csv_path.exists()
