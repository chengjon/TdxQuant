from __future__ import annotations

import copy
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .models import ErrorCode, Result
from .replay_fixtures import list_provider_replay_fixtures, load_provider_replay_fixture
from .result_contract import build_runtime_metadata
from .subscription_watch_run import SubscriptionWatchRunPaths

PROVIDER_MODE_LIVE = "live"
PROVIDER_MODE_REPLAY = "replay"

_SYNC_REPLAY_DEFAULT_FIXTURES: dict[str, str] = {
    "formula.screen": "formula-screen-success",
    "runtime.capabilities": "runtime-capabilities-success",
    "runtime.health": "runtime-health-degraded",
    "runtime.doctor": "runtime-doctor-degraded",
    "market.snapshot": "market-snapshot-success",
    "market.market_snapshot": "market-market-snapshot-success",
    "market.full_tick": "market-full-tick-success",
    "market.stock_info": "market-stock-info-success",
    "market.more_info": "market-more-info-success",
    "market.cb_info": "market-cb-info-success",
    "meta.gb_info": "meta-gb-info-success",
    "meta.ipo_info": "meta-ipo-info-success",
    "meta.gp_one_data": "meta-gp-one-success",
    "meta.divid_factors": "meta-divid-factors-success",
    "market.kline": "market-kline-success",
    "meta.stock_list": "meta-stock-list-success",
    "meta.sector_list": "meta-sector-list-success",
    "meta.sector_stocks": "meta-sector-stocks-success",
    "financial.financial_data": "financial-financial-data-success",
    "financial.financial_data_by_date": "financial-financial-data-by-date-success",
    "transaction.stock_transaction_data": "transaction-stock-transaction-data-success",
    "transaction.stock_transaction_data_by_date": "transaction-stock-transaction-data-by-date-success",
    "transaction.market_transaction_data": "transaction-market-transaction-data-success",
    "transaction.market_transaction_data_by_date": "transaction-market-transaction-data-by-date-success",
    "transaction.sector_transaction_data": "transaction-sector-transaction-data-success",
    "transaction.sector_transaction_data_by_date": "transaction-sector-transaction-data-by-date-success",
    "block.send_user_block": "block-send-user-block-applied",
    "block.read_watchlist_snapshot": "block-read-watchlist-success",
    "block.sync_watchlist": "block-sync-replace-applied",
    "subscription.subscribe_hq": "subscription-subscribe-success",
    "subscription.unsubscribe_hq": "subscription-unsubscribe-success",
    "subscription.get_subscribe_hq_stock_list": "subscription-list-success",
}

_SUBSCRIPTION_WATCH_BUNDLE_DEFAULTS: dict[str, str] = {
    "manifest": "subscription-watch-manifest",
    "status": "subscription-watch-status-completed",
    "summary": "subscription-watch-summary-completed",
    "events": "subscription-watch-events",
}


@dataclass(frozen=True)
class ReplayFixtureSource:
    capability: str
    source_kind: str
    fixture_name: str | None = None
    path: Path | None = None


@dataclass(frozen=True)
class SubscriptionWatchReplaySource:
    source_kind: str
    manifest: dict[str, Any]
    status: dict[str, Any]
    summary: dict[str, Any]
    events: list[dict[str, Any]]
    fixture_name: str | None = None
    path: Path | None = None


@dataclass(frozen=True)
class MaterializedSubscriptionWatchReplay:
    source: SubscriptionWatchReplaySource
    manifest: dict[str, Any]
    status: dict[str, Any]
    summary: dict[str, Any]
    events: list[dict[str, Any]]


def normalize_provider_mode(provider_mode: str | None) -> str:
    normalized = (provider_mode or PROVIDER_MODE_LIVE).strip().lower()
    if normalized in {PROVIDER_MODE_LIVE, PROVIDER_MODE_REPLAY}:
        return normalized
    raise ValueError(f"unsupported provider mode: {provider_mode}")


def is_replay_mode(provider_mode: str | None) -> bool:
    return normalize_provider_mode(provider_mode) == PROVIDER_MODE_REPLAY


def _fixture_registry() -> dict[str, dict[str, str]]:
    return {item["name"]: item for item in list_provider_replay_fixtures()}


def _resolve_fixture_map_selectors(
    capability: str,
    replay_fixture_map: Mapping[str, Any] | None,
) -> tuple[str | None, str | None]:
    if replay_fixture_map is None:
        return None, None
    selector = replay_fixture_map.get(capability)
    if selector is None:
        return None, None
    if isinstance(selector, str):
        return selector, None
    if isinstance(selector, Path):
        return None, str(selector)
    if isinstance(selector, Mapping):
        fixture_name = selector.get("fixture")
        fixture_path = selector.get("fixture_path")
        return (
            str(fixture_name) if fixture_name is not None else None,
            str(fixture_path) if fixture_path is not None else None,
        )
    raise ValueError(f"unsupported replay fixture selector for capability: {capability}")


def resolve_sync_replay_source(
    capability: str,
    *,
    replay_fixture: str | None = None,
    replay_fixture_path: str | None = None,
    replay_fixture_map: Mapping[str, Any] | None = None,
) -> ReplayFixtureSource:
    if capability not in _SYNC_REPLAY_DEFAULT_FIXTURES:
        raise ValueError(f"unsupported replay capability: {capability}")
    mapped_fixture, mapped_path = _resolve_fixture_map_selectors(capability, replay_fixture_map)
    selected_fixture = replay_fixture if replay_fixture is not None else mapped_fixture
    selected_path = replay_fixture_path if replay_fixture_path is not None else mapped_path
    if selected_fixture is not None and selected_path is not None:
        raise ValueError("fixture and fixture_path cannot be used together")
    if selected_path is not None:
        path = Path(selected_path)
        if not path.exists():
            raise ValueError(f"replay fixture path does not exist: {path}")
        return ReplayFixtureSource(capability=capability, source_kind="path", path=path)
    resolved_fixture = selected_fixture or _SYNC_REPLAY_DEFAULT_FIXTURES.get(capability)
    if not resolved_fixture:
        raise ValueError(f"unable to resolve replay fixture for capability: {capability}")
    registry = _fixture_registry()
    descriptor = registry.get(resolved_fixture)
    if descriptor is None:
        raise ValueError(f"unsupported provider replay fixture: {resolved_fixture}")
    if descriptor.get("capability") != capability:
        raise ValueError(
            f"replay fixture {resolved_fixture} does not match capability {capability}"
        )
    return ReplayFixtureSource(capability=capability, source_kind="builtin", fixture_name=resolved_fixture)


def _load_json_fixture_path(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed replay fixture JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"replay fixture must contain a JSON object: {path}")
    return payload


def _load_jsonl_fixture_path(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(f"unable to read replay fixture path: {path}") from exc
    rows: list[dict[str, Any]] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed replay fixture JSONL: {path}") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"replay JSONL fixture must contain object rows: {path}")
        rows.append(payload)
    return rows


def build_replay_result(
    capability: str,
    payload: Mapping[str, Any],
    *,
    source: ReplayFixtureSource,
) -> Result:
    fixture_capability = payload.get("capability")
    if not isinstance(fixture_capability, str) or fixture_capability != capability:
        raise ValueError(f"replay fixture capability mismatch for {capability}")
    raw_code = payload.get("code", ErrorCode.OK.value)
    try:
        code = ErrorCode(str(raw_code))
    except ValueError as exc:
        raise ValueError(f"unsupported replay fixture error code: {raw_code}") from exc
    raw_data = payload.get("data", {})
    if not isinstance(raw_data, Mapping):
        raise ValueError("replay fixture data payload must be a JSON object")
    warnings = payload.get("warnings", [])
    if not isinstance(warnings, list):
        raise ValueError("replay fixture warnings must be a JSON array")
    artifacts = payload.get("artifacts", [])
    if not isinstance(artifacts, list):
        raise ValueError("replay fixture artifacts must be a JSON array")
    runtime = payload.get("runtime")
    if runtime is None:
        runtime_payload = build_runtime_metadata(mode="replay")
    elif isinstance(runtime, Mapping):
        runtime_payload = dict(runtime)
    else:
        raise ValueError("replay fixture runtime must be a JSON object")
    runtime_payload.setdefault("provider_mode", "replay")
    runtime_payload["mode"] = "replay"
    replay_source = {
        "mode": "replay",
        "capability": capability,
        "source_kind": source.source_kind,
    }
    if source.fixture_name is not None:
        replay_source["fixture"] = source.fixture_name
    if source.path is not None:
        replay_source["path"] = str(source.path)
    runtime_payload["replay_source"] = copy.deepcopy(replay_source)

    data = copy.deepcopy(dict(raw_data))
    data.setdefault("replay_source", copy.deepcopy(replay_source))
    next_action = data.get("next_action")
    result = Result(
        ok=bool(payload.get("success", payload.get("ok", False))),
        code=code,
        message=str(payload.get("message", "")),
        data=data,
        warnings=[str(item) for item in warnings],
        next_action=str(next_action) if isinstance(next_action, str) else None,
    )
    result._provider_contract = {
        "capability": capability,
        "capability_version": payload.get("capability_version"),
        "schema_version": payload.get("schema_version"),
        "request_id": payload.get("request_id"),
        "started_at": payload.get("started_at"),
        "finished_at": payload.get("finished_at"),
        "elapsed_ms": payload.get("elapsed_ms"),
        "runtime": runtime_payload,
        "warnings": list(result.warnings),
        "artifacts": copy.deepcopy(list(artifacts)),
    }
    result._provider_artifacts = copy.deepcopy(list(artifacts))
    return result


def execute_sync_replay(
    capability: str,
    *,
    replay_fixture: str | None = None,
    replay_fixture_path: str | None = None,
    replay_fixture_map: Mapping[str, Any] | None = None,
) -> Result:
    try:
        source = resolve_sync_replay_source(
            capability,
            replay_fixture=replay_fixture,
            replay_fixture_path=replay_fixture_path,
            replay_fixture_map=replay_fixture_map,
        )
        if source.source_kind == "builtin":
            payload = load_provider_replay_fixture(str(source.fixture_name))
        else:
            payload = _load_json_fixture_path(Path(source.path))
        if not isinstance(payload, Mapping):
            raise ValueError("replay fixture must resolve to a JSON object")
        return build_replay_result(capability, payload, source=source)
    except ValueError as exc:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message=str(exc),
            data={
                "replay_source": {
                    "mode": "replay",
                    "capability": capability,
                }
            },
        )


def _load_subscription_watch_builtin_bundle(fixture_name: str | None = None) -> SubscriptionWatchReplaySource:
    if fixture_name is not None:
        descriptor = _fixture_registry().get(fixture_name)
        if descriptor is None:
            raise ValueError(f"unsupported provider replay fixture: {fixture_name}")
        if descriptor.get("capability") != "subscription.watch":
            raise ValueError(
                f"replay fixture {fixture_name} does not match capability subscription.watch"
            )
    manifest = load_provider_replay_fixture(_SUBSCRIPTION_WATCH_BUNDLE_DEFAULTS["manifest"])
    status = load_provider_replay_fixture(_SUBSCRIPTION_WATCH_BUNDLE_DEFAULTS["status"])
    summary = load_provider_replay_fixture(_SUBSCRIPTION_WATCH_BUNDLE_DEFAULTS["summary"])
    events = load_provider_replay_fixture(_SUBSCRIPTION_WATCH_BUNDLE_DEFAULTS["events"])
    if not isinstance(manifest, Mapping) or not isinstance(status, Mapping) or not isinstance(summary, Mapping):
        raise ValueError("subscription.watch replay bundle is malformed")
    if not isinstance(events, list):
        raise ValueError("subscription.watch replay events bundle is malformed")
    return SubscriptionWatchReplaySource(
        source_kind="builtin",
        fixture_name=fixture_name or _SUBSCRIPTION_WATCH_BUNDLE_DEFAULTS["manifest"],
        manifest=copy.deepcopy(dict(manifest)),
        status=copy.deepcopy(dict(status)),
        summary=copy.deepcopy(dict(summary)),
        events=[copy.deepcopy(dict(item)) for item in events if isinstance(item, Mapping)],
    )


def _load_subscription_watch_path_bundle(path: Path) -> SubscriptionWatchReplaySource:
    if path.is_dir():
        bundle_dir = path
        manifest_path = bundle_dir / "manifest.json"
    else:
        bundle_dir = path.parent
        manifest_path = path
    status_path = bundle_dir / "status.json"
    summary_path = bundle_dir / "summary.json"
    events_path = bundle_dir / "events.jsonl"
    for required_path in (manifest_path, status_path, summary_path, events_path):
        if not required_path.exists():
            raise ValueError(f"subscription.watch replay artifact does not exist: {required_path}")
    manifest = _load_json_fixture_path(manifest_path)
    status = _load_json_fixture_path(status_path)
    summary = _load_json_fixture_path(summary_path)
    events = _load_jsonl_fixture_path(events_path)
    return SubscriptionWatchReplaySource(
        source_kind="path",
        path=path,
        manifest=manifest,
        status=status,
        summary=summary,
        events=events,
    )


def load_subscription_watch_replay_source(
    *,
    replay_fixture: str | None = None,
    replay_fixture_path: str | None = None,
) -> SubscriptionWatchReplaySource:
    if replay_fixture is not None and replay_fixture_path is not None:
        raise ValueError("fixture and fixture_path cannot be used together")
    if replay_fixture_path is not None:
        path = Path(replay_fixture_path)
        if not path.exists():
            raise ValueError(f"replay fixture path does not exist: {path}")
        return _load_subscription_watch_path_bundle(path)
    return _load_subscription_watch_builtin_bundle(replay_fixture)


def _write_json_file(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_jsonl_file(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_event_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "sequence",
        "symbol",
        "event_type",
        "source_ts",
        "event_ts",
        "session_id",
        "provider_instance_id",
        "subscription_id",
        "payload_json",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "sequence": row.get("sequence"),
                    "symbol": row.get("symbol"),
                    "event_type": row.get("event_type"),
                    "source_ts": row.get("source_ts"),
                    "event_ts": row.get("event_ts"),
                    "session_id": row.get("session_id"),
                    "provider_instance_id": row.get("provider_instance_id"),
                    "subscription_id": row.get("subscription_id"),
                    "payload_json": json.dumps(row.get("payload", {}), ensure_ascii=False, sort_keys=True),
                }
            )


def materialize_subscription_watch_replay(
    *,
    paths: SubscriptionWatchRunPaths,
    replay_fixture: str | None = None,
    replay_fixture_path: str | None = None,
) -> MaterializedSubscriptionWatchReplay:
    def _path_value(path: Path) -> str:
        return path.as_posix()

    source = load_subscription_watch_replay_source(
        replay_fixture=replay_fixture,
        replay_fixture_path=replay_fixture_path,
    )

    manifest = copy.deepcopy(source.manifest)
    status = copy.deepcopy(source.status)
    summary = copy.deepcopy(source.summary)
    events = [copy.deepcopy(row) for row in source.events]

    manifest["run_id"] = paths.run_id
    manifest["provider_mode"] = "replay"
    manifest["output_dir"] = _path_value(paths.run_dir)
    manifest["artifacts"] = {
        "manifest_path": _path_value(paths.manifest_path),
        "status_path": _path_value(paths.status_path),
        "summary_path": _path_value(paths.summary_path),
        "events_jsonl_path": _path_value(paths.events_jsonl_path),
        "events_csv_path": _path_value(paths.events_csv_path),
    }

    status["run_id"] = paths.run_id
    status["state"] = "completed"
    status["output_paths"] = {
        "run_dir": _path_value(paths.run_dir),
        "manifest_path": _path_value(paths.manifest_path),
        "status_path": _path_value(paths.status_path),
        "summary_path": _path_value(paths.summary_path),
        "events_jsonl_path": _path_value(paths.events_jsonl_path),
        "events_csv_path": _path_value(paths.events_csv_path),
    }
    status["artifacts"] = {
        "run_dir": _path_value(paths.run_dir),
        "manifest_path": _path_value(paths.manifest_path),
        "status_path": _path_value(paths.status_path),
        "summary_path": _path_value(paths.summary_path),
        "events_jsonl_path": _path_value(paths.events_jsonl_path),
        "events_csv_path": _path_value(paths.events_csv_path),
        "jsonl_output_path": _path_value(paths.events_jsonl_path),
        "csv_output_path": _path_value(paths.events_csv_path),
        "status_output_path": _path_value(paths.status_path),
    }

    summary["run_id"] = paths.run_id
    summary["final_state"] = "completed"
    summary["artifacts"] = {
        "manifest_path": _path_value(paths.manifest_path),
        "status_path": _path_value(paths.status_path),
        "summary_path": _path_value(paths.summary_path),
        "events_jsonl_path": _path_value(paths.events_jsonl_path),
        "events_csv_path": _path_value(paths.events_csv_path),
    }

    for row in events:
        row["run_id"] = paths.run_id

    paths.run_dir.mkdir(parents=True, exist_ok=True)
    _write_json_file(paths.manifest_path, manifest)
    _write_json_file(paths.status_path, status)
    _write_json_file(paths.summary_path, summary)
    _write_jsonl_file(paths.events_jsonl_path, events)
    _write_event_csv(paths.events_csv_path, events)

    return MaterializedSubscriptionWatchReplay(
        source=source,
        manifest=manifest,
        status=status,
        summary=summary,
        events=events,
    )
