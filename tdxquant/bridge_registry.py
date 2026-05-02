from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
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
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        error_payload = _try_read_json_error_body(exc)
        if error_payload is not None:
            return error_payload
        raise RuntimeError(f"bridge worker request failed with HTTP {exc.code}: {exc.reason}") from exc
    except URLError as exc:
        raise RuntimeError(f"bridge worker request failed: {exc.reason}") from exc


def run_bridge_watch_status(*, registry_path: str | Path, worker_id: str) -> dict[str, Any]:
    worker = _resolve_worker(registry_path=registry_path, worker_id=worker_id)
    return call_worker(
        worker,
        method="GET",
        route="/bridge/v1/watch/status",
        token=resolve_worker_token(worker),
    )


def run_bridge_watch_start(
    *,
    registry_path: str | Path,
    worker_id: str,
    stock_list: list[str],
    max_events: int | None = None,
    max_seconds: float | None = None,
) -> dict[str, Any]:
    worker = _resolve_worker(registry_path=registry_path, worker_id=worker_id)
    body: dict[str, Any] = {"stock_list": list(stock_list)}
    if max_events is not None:
        body["max_events"] = max_events
    if max_seconds is not None:
        body["max_seconds"] = max_seconds
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
    payload = json.loads(body.decode("utf-8"))
    if isinstance(payload, dict):
        return payload
    return None
