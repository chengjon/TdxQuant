from __future__ import annotations

from dataclasses import dataclass
import errno
import json
import os
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class BridgeWorker:
    worker_id: str
    label: str
    host: str
    port: int
    token_env: str
    role_tags: list[str]
    enabled: bool = True


def load_worker_registry(path: str | Path) -> list[BridgeWorker]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("worker registry must be a JSON array")
    workers: list[BridgeWorker] = []
    seen_worker_ids: set[str] = set()
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("worker registry entries must be JSON objects")
        worker = BridgeWorker(
            worker_id=str(item.get("worker_id") or "").strip(),
            label=str(item.get("label") or "").strip(),
            host=str(item.get("host") or "").strip(),
            port=int(item.get("port") or 0),
            token_env=str(item.get("token_env") or "").strip(),
            role_tags=[str(tag) for tag in item.get("role_tags") or []],
            enabled=bool(item.get("enabled", True)),
        )
        _validate_worker(worker)
        if worker.worker_id in seen_worker_ids:
            raise ValueError(f"duplicate worker_id in registry: {worker.worker_id}")
        seen_worker_ids.add(worker.worker_id)
        if worker.enabled:
            workers.append(worker)
    return workers


def select_worker(workers: list[BridgeWorker], *, worker_id: str) -> BridgeWorker:
    for worker in workers:
        if worker.worker_id == worker_id:
            return worker
    raise ValueError(f"unknown worker: {worker_id}")


def resolve_worker_token(worker: BridgeWorker) -> str:
    token = os.environ.get(worker.token_env, "").strip()
    if not token:
        raise ValueError(f"missing bridge token in environment: {worker.token_env}")
    return token


def call_worker(
    worker: BridgeWorker,
    *,
    method: str,
    route: str,
    token: str,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    request = Request(
        f"http://{worker.host}:{worker.port}{route}",
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        data=None if body is None else json.dumps(body).encode("utf-8"),
    )
    try:
        with urlopen(request, timeout=5.0) as response:
            raw_bytes = response.read()
        try:
            raw = raw_bytes.decode("utf-8")
            payload = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("bridge worker returned invalid JSON payload") from exc
        if not isinstance(payload, dict):
            raise RuntimeError("bridge worker returned non-object JSON payload")
        return payload
    except HTTPError as exc:
        error_payload = _try_read_json_error_body(exc)
        if error_payload is not None:
            return error_payload
        raise RuntimeError(f"bridge worker request failed with HTTP {exc.code}: {exc.reason}") from exc
    except URLError as exc:
        raise RuntimeError(f"bridge worker request failed: {_normalize_url_error_reason(exc.reason)}") from exc


def call_worker_text(
    worker: BridgeWorker,
    *,
    method: str,
    route: str,
    token: str,
    body: dict[str, Any] | None = None,
) -> str:
    request = Request(
        f"http://{worker.host}:{worker.port}{route}",
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        data=None if body is None else json.dumps(body).encode("utf-8"),
    )
    try:
        with urlopen(request, timeout=5.0) as response:
            return response.read().decode("utf-8")
    except HTTPError as exc:
        error_payload = _try_read_json_error_body(exc)
        if error_payload is not None:
            return json.dumps(error_payload, ensure_ascii=False)
        raise RuntimeError(f"bridge worker request failed with HTTP {exc.code}: {exc.reason}") from exc
    except UnicodeDecodeError as exc:
        raise RuntimeError("bridge worker returned invalid text payload") from exc
    except URLError as exc:
        raise RuntimeError(f"bridge worker request failed: {_normalize_url_error_reason(exc.reason)}") from exc


def run_bridge_watch_status(
    *,
    registry_path: str | Path,
    worker_id: str,
    heartbeat_stale_after_seconds: float | int | None = None,
    watermark_stale_after_seconds: float | int | None = None,
    reconnect_stale_after_seconds: float | int | None = None,
) -> dict[str, Any]:
    worker = _resolve_worker(registry_path=registry_path, worker_id=worker_id)
    return call_worker(
        worker,
        method="GET",
        route=_build_route(
            "/bridge/v1/watch/status",
            heartbeat_stale_after_seconds=heartbeat_stale_after_seconds,
            watermark_stale_after_seconds=watermark_stale_after_seconds,
            reconnect_stale_after_seconds=reconnect_stale_after_seconds,
        ),
        token=resolve_worker_token(worker),
    )


def run_bridge_health(*, registry_path: str | Path, worker_id: str) -> dict[str, Any]:
    worker = _resolve_worker(registry_path=registry_path, worker_id=worker_id)
    return call_worker(
        worker,
        method="GET",
        route="/bridge/v1/health",
        token=resolve_worker_token(worker),
    )


def run_bridge_watch_list(*, registry_path: str | Path, worker_id: str) -> dict[str, Any]:
    worker = _resolve_worker(registry_path=registry_path, worker_id=worker_id)
    return call_worker(
        worker,
        method="GET",
        route="/bridge/v1/watch/list",
        token=resolve_worker_token(worker),
    )


def run_bridge_watch_artifacts(*, registry_path: str | Path, worker_id: str) -> dict[str, Any]:
    worker = _resolve_worker(registry_path=registry_path, worker_id=worker_id)
    return call_worker(
        worker,
        method="GET",
        route="/bridge/v1/watch/artifacts",
        token=resolve_worker_token(worker),
    )


def run_bridge_watch_events(*, registry_path: str | Path, worker_id: str, tail: int | None = None) -> dict[str, Any]:
    worker = _resolve_worker(registry_path=registry_path, worker_id=worker_id)
    return call_worker(
        worker,
        method="GET",
        route=_build_route("/bridge/v1/watch/events", tail=tail),
        token=resolve_worker_token(worker),
    )


def run_bridge_watch_event_stream(
    *,
    registry_path: str | Path,
    worker_id: str,
    run_id: str | None = None,
    from_cursor: str | None = None,
    follow: bool | None = None,
    heartbeat_seconds: int | None = None,
) -> str:
    worker = _resolve_worker(registry_path=registry_path, worker_id=worker_id)
    return call_worker_text(
        worker,
        method="GET",
        route=_build_route(
            "/bridge/v1/watch/events/stream",
            run_id=run_id,
            **{"from": from_cursor},
            follow=None if follow is None else str(follow).lower(),
            heartbeat_seconds=heartbeat_seconds,
        ),
        token=resolve_worker_token(worker),
    )


def run_bridge_watch_logs(*, registry_path: str | Path, worker_id: str, tail: int | None = None) -> dict[str, Any]:
    worker = _resolve_worker(registry_path=registry_path, worker_id=worker_id)
    return call_worker(
        worker,
        method="GET",
        route=_build_route("/bridge/v1/watch/logs", tail=tail),
        token=resolve_worker_token(worker),
    )


def run_bridge_watch_start(
    *,
    registry_path: str | Path,
    worker_id: str,
    stock_list: list[str],
    max_events: int | None = None,
    max_seconds: float | None = None,
    poll_interval: float | None = None,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    worker = _resolve_worker(registry_path=registry_path, worker_id=worker_id)
    body: dict[str, Any] = {"stock_list": list(stock_list)}
    if max_events is not None:
        body["max_events"] = max_events
    if max_seconds is not None:
        body["max_seconds"] = max_seconds
    if poll_interval is not None:
        body["poll_interval"] = poll_interval
    if idempotency_key is not None:
        body["idempotency_key"] = idempotency_key
    return call_worker(
        worker,
        method="POST",
        route="/bridge/v1/watch/start",
        token=resolve_worker_token(worker),
        body=body,
    )


def run_bridge_watch_stop(*, registry_path: str | Path, worker_id: str) -> dict[str, Any]:
    worker = _resolve_worker(registry_path=registry_path, worker_id=worker_id)
    return call_worker(
        worker,
        method="POST",
        route="/bridge/v1/watch/stop",
        token=resolve_worker_token(worker),
        body={},
    )


def _resolve_worker(*, registry_path: str | Path, worker_id: str) -> BridgeWorker:
    return select_worker(load_worker_registry(registry_path), worker_id=worker_id)


def _build_route(path: str, *, tail: int | None = None, **params: Any) -> str:
    query: dict[str, Any] = {}
    if tail is not None:
        query["tail"] = tail
    for key, value in params.items():
        if value is not None:
            query[key] = value
    if not query:
        return path
    return f"{path}?{urlencode(query)}"


def _validate_worker(worker: BridgeWorker) -> None:
    if not worker.worker_id:
        raise ValueError("worker registry entry requires worker_id")
    if not worker.label:
        raise ValueError(f"worker registry entry {worker.worker_id!r} requires label")
    if not worker.host:
        raise ValueError(f"worker registry entry {worker.worker_id!r} requires host")
    if worker.port <= 0:
        raise ValueError(f"worker registry entry {worker.worker_id!r} requires a positive port")
    if not worker.token_env:
        raise ValueError(f"worker registry entry {worker.worker_id!r} requires token_env")


def _try_read_json_error_body(error: HTTPError) -> dict[str, Any] | None:
    if error.fp is None:
        return None
    body = error.fp.read()
    if not body:
        return None
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if isinstance(payload, dict):
        return payload
    return None


def _normalize_url_error_reason(reason: object) -> str:
    if isinstance(reason, OSError) and getattr(reason, "errno", None) == errno.ECONNREFUSED:
        return "connection refused"
    return str(reason)
