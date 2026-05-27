from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen
from uuid import uuid4

from .models import ErrorCode
from .replay_fixtures import list_provider_replay_fixtures
from .replay_provider import (
    execute_sync_replay,
    load_subscription_watch_replay_source,
)

REPLAY_TRANSPORT_VERSION = "provider-transport-replay.v1"
WATCH_EVENT_STREAM_SCHEMA_VERSION = "tdx.bridge.watch.event_stream.v1"
WATCH_TERMINAL_STATES = {"completed", "failed", "stopped", "stopping", "cancelled"}
REPLAY_READ_ONLY_ENDPOINTS = [
    "/provider/v1/replay/health",
    "/provider/v1/replay/fixtures",
    "/provider/v1/replay/result",
    "/provider/v1/replay/watch/status",
    "/provider/v1/replay/watch/events",
    "/provider/v1/replay/watch/events/stream",
]
PROVIDER_REPLAY_STATUS_PROBE_KEYS = (
    "health_probe",
    "watch_status_probe",
    "watch_events_probe",
    "watch_stream_probe",
)
PROVIDER_REPLAY_PROBE_ERROR_SAMPLE_LIMIT = 3


@dataclass(frozen=True)
class ProviderTransportReplayConfig:
    provider_id: str
    bind_host: str
    port: int
    token: str
    master_allowlist: list[str]
    replay_fixture: str | None = None
    replay_fixture_path: str | None = None

    def __post_init__(self) -> None:
        if not self.provider_id.strip():
            raise ValueError("provider_id is required")
        if not self.bind_host.strip():
            raise ValueError("bind_host is required")
        if not self.token:
            raise ValueError("token is required")


def build_provider_transport_replay_status(
    config: ProviderTransportReplayConfig,
    *,
    health_probe: dict[str, Any] | None = None,
    watch_status_probe: dict[str, Any] | None = None,
    watch_events_probe: dict[str, Any] | None = None,
    watch_stream_probe: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_kind = "default_fixture_resolution"
    if config.replay_fixture_path:
        source_kind = "fixture_path"
    elif config.replay_fixture:
        source_kind = "built_in_fixture"

    master_allowlist = list(config.master_allowlist or [])
    resolved_health_probe = _normalize_provider_replay_health_probe(health_probe)
    resolved_watch_status_probe = _normalize_provider_replay_watch_status_probe(watch_status_probe)
    resolved_watch_events_probe = _normalize_provider_replay_watch_events_probe(watch_events_probe)
    resolved_watch_stream_probe = _normalize_provider_replay_watch_stream_probe(watch_stream_probe)
    resolved_probes = {
        "health_probe": resolved_health_probe,
        "watch_status_probe": resolved_watch_status_probe,
        "watch_events_probe": resolved_watch_events_probe,
        "watch_stream_probe": resolved_watch_stream_probe,
    }
    return {
        "provider_id": config.provider_id,
        "service": "provider-transport-replay",
        "provider_mode": "replay",
        "transport": "http",
        "transport_mode": "replay_only",
        "schema_version": REPLAY_TRANSPORT_VERSION,
        "bind": {
            "host": config.bind_host,
            "port": config.port,
        },
        "security": {
            "bearer_token_required": True,
            "source_allowlist_enabled": bool(master_allowlist),
            "master_allowlist_count": len(master_allowlist),
        },
        "replay_source": {
            "source_kind": source_kind,
            "fixture": config.replay_fixture,
            "fixture_path": config.replay_fixture_path,
        },
        "capabilities": {
            "read_only": True,
            "writes_supported": False,
            "endpoints": list(REPLAY_READ_ONLY_ENDPOINTS),
        },
        "runtime": {
            "runtime_observed": bool(
                resolved_health_probe.get("enabled")
                or resolved_watch_status_probe.get("enabled")
                or resolved_watch_events_probe.get("enabled")
                or resolved_watch_stream_probe.get("enabled")
            ),
            "live_runtime_required": False,
            "live_market_session_supported": False,
            "health_probe": resolved_health_probe,
            "watch_status_probe": resolved_watch_status_probe,
            "watch_events_probe": resolved_watch_events_probe,
            "watch_stream_probe": resolved_watch_stream_probe,
            "probe_summary": _build_provider_replay_probe_summary(resolved_probes),
        },
        "lifecycle": {
            "mode": "foreground_process",
            "start_stop_managed": False,
            "daemon_managed": False,
            "scheduler_managed": False,
            "restart_policy": "not_managed",
        },
        "boundaries": [
            "fixture-backed replay only",
            "read-only provider surface",
            "no daemon start/stop lifecycle management",
            "no scheduler or restart governance",
            "no live market session",
        ],
    }


def probe_provider_transport_replay_health(
    config: ProviderTransportReplayConfig,
    *,
    timeout_seconds: float | int = 1.0,
) -> dict[str, Any]:
    try:
        resolved_timeout = float(timeout_seconds)
    except (TypeError, ValueError):
        return _build_probe_result(
            status="invalid_timeout",
            reachable=False,
            timeout_seconds=None,
            error="timeout_seconds must be numeric",
            url=_provider_replay_health_probe_url(config),
        )
    if resolved_timeout <= 0:
        return _build_probe_result(
            status="invalid_timeout",
            reachable=False,
            timeout_seconds=resolved_timeout,
            error="timeout_seconds must be positive",
            url=_provider_replay_health_probe_url(config),
        )

    url = _provider_replay_health_probe_url(config)
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {config.token}",
            "X-Request-Id": uuid4().hex,
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=resolved_timeout) as response:
            http_status = int(response.getcode())
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        details = _decode_probe_http_error(exc)
        return _build_probe_result(
            status="http_error",
            reachable=True,
            timeout_seconds=resolved_timeout,
            http_status=exc.code,
            error=details.get("message"),
            error_code=details.get("code"),
            url=url,
        )
    except (URLError, TimeoutError, OSError) as exc:
        return _build_probe_result(
            status="unreachable",
            reachable=False,
            timeout_seconds=resolved_timeout,
            error=_probe_error_message(exc),
            url=url,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return _build_probe_result(
            status="invalid_response",
            reachable=True,
            timeout_seconds=resolved_timeout,
            http_status=None,
            error=str(exc),
            url=url,
        )

    result = payload.get("result") if isinstance(payload, dict) else None
    result = result if isinstance(result, dict) else {}
    healthy = bool(payload.get("ok")) and http_status == 200 and result.get("status") == "ok"
    return _build_probe_result(
        status="healthy" if healthy else "unexpected_response",
        reachable=True,
        timeout_seconds=resolved_timeout,
        http_status=http_status,
        service=str(result.get("service") or "") or None,
        provider_id=str(result.get("provider_id") or "") or None,
        provider_mode=str(result.get("provider_mode") or "") or None,
        url=url,
    )


def probe_provider_transport_replay_watch_status(
    config: ProviderTransportReplayConfig,
    *,
    timeout_seconds: float | int = 1.0,
) -> dict[str, Any]:
    endpoint = "/provider/v1/replay/watch/status"
    try:
        resolved_timeout = float(timeout_seconds)
    except (TypeError, ValueError):
        return _build_probe_result(
            status="invalid_timeout",
            reachable=False,
            timeout_seconds=None,
            error="timeout_seconds must be numeric",
            url=_provider_replay_watch_status_probe_url(config),
            target="watch_status",
            endpoint=endpoint,
        )
    if resolved_timeout <= 0:
        return _build_probe_result(
            status="invalid_timeout",
            reachable=False,
            timeout_seconds=resolved_timeout,
            error="timeout_seconds must be positive",
            url=_provider_replay_watch_status_probe_url(config),
            target="watch_status",
            endpoint=endpoint,
        )

    url = _provider_replay_watch_status_probe_url(config)
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {config.token}",
            "X-Request-Id": uuid4().hex,
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=resolved_timeout) as response:
            http_status = int(response.getcode())
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        details = _decode_probe_http_error(exc)
        return _build_probe_result(
            status="http_error",
            reachable=True,
            timeout_seconds=resolved_timeout,
            http_status=exc.code,
            error=details.get("message"),
            error_code=details.get("code"),
            url=url,
            target="watch_status",
            endpoint=endpoint,
        )
    except (URLError, TimeoutError, OSError) as exc:
        return _build_probe_result(
            status="unreachable",
            reachable=False,
            timeout_seconds=resolved_timeout,
            error=_probe_error_message(exc),
            url=url,
            target="watch_status",
            endpoint=endpoint,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return _build_probe_result(
            status="invalid_response",
            reachable=True,
            timeout_seconds=resolved_timeout,
            http_status=None,
            error=str(exc),
            url=url,
            target="watch_status",
            endpoint=endpoint,
        )

    result = payload.get("result") if isinstance(payload, dict) else None
    result = result if isinstance(result, dict) else {}
    watch_status = result.get("watch_status") if isinstance(result.get("watch_status"), dict) else {}
    control = result.get("control") if isinstance(result.get("control"), dict) else {}
    state = str(watch_status.get("state") or control.get("state") or "") or None
    healthy = bool(payload.get("ok")) and http_status == 200 and state in {
        "completed",
        "running",
        "reconnecting",
        "degraded",
        "stopped",
    }
    return _build_probe_result(
        status="healthy" if healthy else "unexpected_response",
        reachable=True,
        timeout_seconds=resolved_timeout,
        http_status=http_status,
        service="provider-transport-replay",
        provider_id=config.provider_id,
        provider_mode="replay",
        url=url,
        target="watch_status",
        endpoint=endpoint,
        state=state,
    )


def probe_provider_transport_replay_watch_events(
    config: ProviderTransportReplayConfig,
    *,
    timeout_seconds: float | int = 1.0,
) -> dict[str, Any]:
    endpoint = "/provider/v1/replay/watch/events"
    try:
        resolved_timeout = float(timeout_seconds)
    except (TypeError, ValueError):
        return _build_probe_result(
            status="invalid_timeout",
            reachable=False,
            timeout_seconds=None,
            error="timeout_seconds must be numeric",
            url=_provider_replay_watch_events_probe_url(config),
            target="watch_events",
            endpoint=endpoint,
        )
    if resolved_timeout <= 0:
        return _build_probe_result(
            status="invalid_timeout",
            reachable=False,
            timeout_seconds=resolved_timeout,
            error="timeout_seconds must be positive",
            url=_provider_replay_watch_events_probe_url(config),
            target="watch_events",
            endpoint=endpoint,
        )

    url = _provider_replay_watch_events_probe_url(config)
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {config.token}",
            "X-Request-Id": uuid4().hex,
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=resolved_timeout) as response:
            http_status = int(response.getcode())
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        details = _decode_probe_http_error(exc)
        return _build_probe_result(
            status="http_error",
            reachable=True,
            timeout_seconds=resolved_timeout,
            http_status=exc.code,
            error=details.get("message"),
            error_code=details.get("code"),
            url=url,
            target="watch_events",
            endpoint=endpoint,
        )
    except (URLError, TimeoutError, OSError) as exc:
        return _build_probe_result(
            status="unreachable",
            reachable=False,
            timeout_seconds=resolved_timeout,
            error=_probe_error_message(exc),
            url=url,
            target="watch_events",
            endpoint=endpoint,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return _build_probe_result(
            status="invalid_response",
            reachable=True,
            timeout_seconds=resolved_timeout,
            http_status=None,
            error=str(exc),
            url=url,
            target="watch_events",
            endpoint=endpoint,
        )

    result = payload.get("result") if isinstance(payload, dict) else None
    result = result if isinstance(result, dict) else {}
    events = result.get("events")
    healthy = bool(payload.get("ok")) and http_status == 200 and isinstance(events, list)
    return _build_probe_result(
        status="healthy" if healthy else "unexpected_response",
        reachable=True,
        timeout_seconds=resolved_timeout,
        http_status=http_status,
        service="provider-transport-replay",
        provider_id=config.provider_id,
        provider_mode="replay",
        url=url,
        target="watch_events",
        endpoint=endpoint,
        event_count=len(events) if isinstance(events, list) else None,
    )


def probe_provider_transport_replay_watch_stream(
    config: ProviderTransportReplayConfig,
    *,
    timeout_seconds: float | int = 1.0,
) -> dict[str, Any]:
    endpoint = "/provider/v1/replay/watch/events/stream"
    try:
        resolved_timeout = float(timeout_seconds)
    except (TypeError, ValueError):
        return _build_probe_result(
            status="invalid_timeout",
            reachable=False,
            timeout_seconds=None,
            error="timeout_seconds must be numeric",
            url=_provider_replay_watch_stream_probe_url(config),
            target="watch_stream",
            endpoint=endpoint,
        )
    if resolved_timeout <= 0:
        return _build_probe_result(
            status="invalid_timeout",
            reachable=False,
            timeout_seconds=resolved_timeout,
            error="timeout_seconds must be positive",
            url=_provider_replay_watch_stream_probe_url(config),
            target="watch_stream",
            endpoint=endpoint,
        )

    url = _provider_replay_watch_stream_probe_url(config)
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {config.token}",
            "X-Request-Id": uuid4().hex,
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=resolved_timeout) as response:
            http_status = int(response.getcode())
            content_type = str(response.headers.get("Content-Type") or "")
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        details = _decode_probe_http_error(exc)
        return _build_probe_result(
            status="http_error",
            reachable=True,
            timeout_seconds=resolved_timeout,
            http_status=exc.code,
            error=details.get("message"),
            error_code=details.get("code"),
            url=url,
            target="watch_stream",
            endpoint=endpoint,
        )
    except (URLError, TimeoutError, OSError) as exc:
        return _build_probe_result(
            status="unreachable",
            reachable=False,
            timeout_seconds=resolved_timeout,
            error=_probe_error_message(exc),
            url=url,
            target="watch_stream",
            endpoint=endpoint,
        )
    except UnicodeDecodeError as exc:
        return _build_probe_result(
            status="invalid_response",
            reachable=True,
            timeout_seconds=resolved_timeout,
            http_status=None,
            error=str(exc),
            url=url,
            target="watch_stream",
            endpoint=endpoint,
        )

    frame_count = sum(1 for line in body.splitlines() if line.startswith("data: "))
    healthy = bool(http_status == 200 and "text/event-stream" in content_type and frame_count > 0)
    return _build_probe_result(
        status="healthy" if healthy else "unexpected_response",
        reachable=True,
        timeout_seconds=resolved_timeout,
        http_status=http_status,
        service="provider-transport-replay",
        provider_id=config.provider_id,
        provider_mode="replay",
        url=url,
        target="watch_stream",
        endpoint=endpoint,
        frame_count=frame_count,
    )


def _normalize_provider_replay_health_probe(health_probe: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(health_probe, dict):
        return {
            "enabled": False,
            "status": "not_requested",
            "reachable": None,
            "http_status": None,
        }
    resolved = dict(health_probe)
    resolved["enabled"] = True
    resolved.setdefault("status", "unknown")
    resolved.setdefault("reachable", None)
    resolved.setdefault("http_status", None)
    return resolved


def _normalize_provider_replay_watch_status_probe(watch_status_probe: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(watch_status_probe, dict):
        return {
            "enabled": False,
            "target": "watch_status",
            "endpoint": "/provider/v1/replay/watch/status",
            "status": "not_requested",
            "reachable": None,
            "http_status": None,
        }
    resolved = dict(watch_status_probe)
    resolved["enabled"] = True
    resolved.setdefault("target", "watch_status")
    resolved.setdefault("endpoint", "/provider/v1/replay/watch/status")
    resolved.setdefault("status", "unknown")
    resolved.setdefault("reachable", None)
    resolved.setdefault("http_status", None)
    return resolved


def _normalize_provider_replay_watch_events_probe(watch_events_probe: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(watch_events_probe, dict):
        return {
            "enabled": False,
            "target": "watch_events",
            "endpoint": "/provider/v1/replay/watch/events",
            "status": "not_requested",
            "reachable": None,
            "http_status": None,
        }
    resolved = dict(watch_events_probe)
    resolved["enabled"] = True
    resolved.setdefault("target", "watch_events")
    resolved.setdefault("endpoint", "/provider/v1/replay/watch/events")
    resolved.setdefault("status", "unknown")
    resolved.setdefault("reachable", None)
    resolved.setdefault("http_status", None)
    return resolved


def _normalize_provider_replay_watch_stream_probe(watch_stream_probe: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(watch_stream_probe, dict):
        return {
            "enabled": False,
            "target": "watch_stream",
            "endpoint": "/provider/v1/replay/watch/events/stream",
            "status": "not_requested",
            "reachable": None,
            "http_status": None,
        }
    resolved = dict(watch_stream_probe)
    resolved["enabled"] = True
    resolved.setdefault("target", "watch_stream")
    resolved.setdefault("endpoint", "/provider/v1/replay/watch/events/stream")
    resolved.setdefault("status", "unknown")
    resolved.setdefault("reachable", None)
    resolved.setdefault("http_status", None)
    return resolved


def _build_provider_replay_probe_summary(probes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    requested: list[str] = []
    healthy: list[str] = []
    failed: list[str] = []
    unhealthy: list[str] = []
    not_requested: list[str] = []
    healthy_count = 0
    status_counts: dict[str, int] = {}
    requested_status_counts: dict[str, int] = {}
    failed_status_counts: dict[str, int] = {}
    requested_reachability_counts: dict[str, int] = {}
    healthy_reachability_counts: dict[str, int] = {}
    failed_reachability_counts: dict[str, int] = {}
    requested_http_status_counts: dict[str, int] = {}
    healthy_http_status_counts: dict[str, int] = {}
    failed_http_status_counts: dict[str, int] = {}
    error_code_counts: dict[str, int] = {}
    failed_error_code_counts: dict[str, int] = {}
    error_samples: list[dict[str, Any]] = []
    error_sample_status_counts: dict[str, int] = {}
    error_sample_probe_counts: dict[str, int] = {}
    error_sample_http_status_counts: dict[str, int] = {}
    error_sample_reachability_counts: dict[str, int] = {}
    error_sample_count = 0
    primary_error_sample_reachability: str | None = None

    for key in PROVIDER_REPLAY_STATUS_PROBE_KEYS:
        probe = probes.get(key) or {}
        probe_status = probe.get("status") if isinstance(probe.get("status"), str) else "not_requested"
        status_counts[probe_status] = status_counts.get(probe_status, 0) + 1
        error_code = probe.get("error_code")
        if isinstance(error_code, str) and error_code:
            error_code_counts[error_code] = error_code_counts.get(error_code, 0) + 1
        if probe_status not in {"healthy", "not_requested"} or (isinstance(error_code, str) and error_code):
            error_sample_count += 1
            error_sample_status_counts[probe_status] = error_sample_status_counts.get(probe_status, 0) + 1
            error_sample_probe_counts[key] = error_sample_probe_counts.get(key, 0) + 1
            reachable = probe.get("reachable")
            if reachable is True:
                error_sample_reachability_status = "reachable"
            elif reachable is False:
                error_sample_reachability_status = "unreachable"
            else:
                error_sample_reachability_status = "unknown"
            error_sample_reachability_counts[error_sample_reachability_status] = (
                error_sample_reachability_counts.get(error_sample_reachability_status, 0) + 1
            )
            if primary_error_sample_reachability is None:
                primary_error_sample_reachability = error_sample_reachability_status
            http_status = probe.get("http_status")
            if isinstance(http_status, int) and not isinstance(http_status, bool):
                http_status_key = str(http_status)
                error_sample_http_status_counts[http_status_key] = (
                    error_sample_http_status_counts.get(http_status_key, 0) + 1
                )
            if len(error_samples) < PROVIDER_REPLAY_PROBE_ERROR_SAMPLE_LIMIT:
                sample: dict[str, Any] = {"probe": key, "status": probe_status}
                if isinstance(error_code, str) and error_code:
                    sample["error_code"] = error_code
                if isinstance(http_status, int):
                    sample["http_status"] = http_status
                error_samples.append(sample)
        if probe_status == "not_requested":
            not_requested.append(key)
            continue
        requested.append(key)
        requested_status_counts[probe_status] = requested_status_counts.get(probe_status, 0) + 1
        http_status = probe.get("http_status")
        if isinstance(http_status, int) and not isinstance(http_status, bool):
            http_status_key = str(http_status)
            requested_http_status_counts[http_status_key] = (
                requested_http_status_counts.get(http_status_key, 0) + 1
            )
        reachable = probe.get("reachable")
        if reachable is True:
            reachability_status = "reachable"
        elif reachable is False:
            reachability_status = "unreachable"
        else:
            reachability_status = "unknown"
        requested_reachability_counts[reachability_status] = (
            requested_reachability_counts.get(reachability_status, 0) + 1
        )
        if probe_status == "healthy":
            healthy.append(key)
            healthy_count += 1
            healthy_reachability_counts[reachability_status] = (
                healthy_reachability_counts.get(reachability_status, 0) + 1
            )
            if isinstance(http_status, int) and not isinstance(http_status, bool):
                http_status_key = str(http_status)
                healthy_http_status_counts[http_status_key] = (
                    healthy_http_status_counts.get(http_status_key, 0) + 1
                )
        else:
            failed.append(key)
            unhealthy.append(key)
            failed_status_counts[probe_status] = failed_status_counts.get(probe_status, 0) + 1
            failed_reachability_counts[reachability_status] = (
                failed_reachability_counts.get(reachability_status, 0) + 1
            )
            if isinstance(http_status, int) and not isinstance(http_status, bool):
                http_status_key = str(http_status)
                failed_http_status_counts[http_status_key] = (
                    failed_http_status_counts.get(http_status_key, 0) + 1
                )
            if isinstance(error_code, str) and error_code:
                failed_error_code_counts[error_code] = failed_error_code_counts.get(error_code, 0) + 1

    requested_count = len(requested)
    failed_count = len(unhealthy)
    total_count = len(PROVIDER_REPLAY_STATUS_PROBE_KEYS)
    primary_error_sample = error_samples[0] if error_samples else {}
    error_sample_visible_count = len(error_samples)
    error_sample_hidden_count = max(error_sample_count - len(error_samples), 0)
    error_sample_truncated = error_sample_count > error_sample_visible_count
    primary_error_sample_probe = (
        primary_error_sample.get("probe") if isinstance(primary_error_sample.get("probe"), str) else None
    )
    primary_error_sample_status = (
        primary_error_sample.get("status") if isinstance(primary_error_sample.get("status"), str) else None
    )
    primary_error_sample_error_code = (
        primary_error_sample.get("error_code")
        if isinstance(primary_error_sample.get("error_code"), str)
        else None
    )
    primary_error_sample_http_status = (
        primary_error_sample.get("http_status")
        if isinstance(primary_error_sample.get("http_status"), int)
        and not isinstance(primary_error_sample.get("http_status"), bool)
        else None
    )
    error_sample_summary = {
        "count": error_sample_count,
        "visible_count": error_sample_visible_count,
        "hidden_count": error_sample_hidden_count,
        "limit": PROVIDER_REPLAY_PROBE_ERROR_SAMPLE_LIMIT,
        "truncated": error_sample_truncated,
        "primary_probe": primary_error_sample_probe,
        "primary_status": primary_error_sample_status,
        "primary_error_code": primary_error_sample_error_code,
        "primary_http_status": primary_error_sample_http_status,
        "primary_reachability": primary_error_sample_reachability,
    }
    if requested_count == 0:
        summary_status = "not_requested"
        request_coverage_status = "none"
    elif failed_count:
        summary_status = "degraded"
        request_coverage_status = "complete" if requested_count == total_count else "partial"
    else:
        summary_status = "healthy"
        request_coverage_status = "complete" if requested_count == total_count else "partial"

    request_summary = {
        "status": request_coverage_status,
        "total_count": total_count,
        "requested_count": requested_count,
        "not_requested_count": total_count - requested_count,
        "healthy_count": healthy_count,
        "failed_count": failed_count,
        "unhealthy_count": len(unhealthy),
        "primary_requested_probe": requested[0] if requested else None,
        "primary_not_requested_probe": not_requested[0] if not_requested else None,
    }
    health_summary = {
        "status": summary_status,
        "healthy_count": healthy_count,
        "failed_count": failed_count,
        "unhealthy_count": len(unhealthy),
        "status_key_count": len(status_counts),
        "primary_healthy_probe": healthy[0] if healthy else None,
        "primary_failed_probe": failed[0] if failed else None,
        "primary_unhealthy_probe": unhealthy[0] if unhealthy else None,
    }
    primary_problem_probe = failed[0] if failed else unhealthy[0] if unhealthy else primary_error_sample_probe
    outcome_summary = {
        "status": summary_status,
        "request_coverage_status": request_coverage_status,
        "total_count": total_count,
        "requested_count": requested_count,
        "healthy_count": healthy_count,
        "failed_count": failed_count,
        "unhealthy_count": len(unhealthy),
        "not_requested_count": total_count - requested_count,
        "all_probes_requested": bool(total_count and requested_count == total_count),
        "has_failed_probe": bool(failed_count),
        "has_unhealthy_probe": bool(unhealthy),
        "primary_problem_probe": primary_problem_probe,
        "primary_error_sample_probe": primary_error_sample_probe,
        "primary_error_sample_status": primary_error_sample_status,
    }

    return {
        "status": summary_status,
        "request_coverage_status": request_coverage_status,
        "request_summary": request_summary,
        "health_summary": health_summary,
        "outcome_summary": outcome_summary,
        "total_count": total_count,
        "requested_count": requested_count,
        "has_requested_probe": bool(requested),
        "healthy_count": healthy_count,
        "has_healthy_probe": bool(healthy),
        "failed_count": failed_count,
        "has_failed_probe": bool(failed_count),
        "unhealthy_count": len(unhealthy),
        "not_requested_count": total_count - requested_count,
        "all_probes_requested": bool(total_count and requested_count == total_count),
        "has_not_requested_probe": bool(not_requested),
        "status_counts": {status: status_counts[status] for status in sorted(status_counts)},
        "status_key_count": len(status_counts),
        "requested_status_counts": {
            status: requested_status_counts[status] for status in sorted(requested_status_counts)
        },
        "requested_status_key_count": len(requested_status_counts),
        "failed_status_counts": {status: failed_status_counts[status] for status in sorted(failed_status_counts)},
        "failed_status_key_count": len(failed_status_counts),
        "requested_reachability_counts": {
            status: requested_reachability_counts[status] for status in sorted(requested_reachability_counts)
        },
        "requested_reachability_key_count": len(requested_reachability_counts),
        "healthy_reachability_counts": {
            status: healthy_reachability_counts[status] for status in sorted(healthy_reachability_counts)
        },
        "healthy_reachability_key_count": len(healthy_reachability_counts),
        "failed_reachability_counts": {
            status: failed_reachability_counts[status] for status in sorted(failed_reachability_counts)
        },
        "failed_reachability_key_count": len(failed_reachability_counts),
        "requested_http_status_counts": {
            status: requested_http_status_counts[status]
            for status in sorted(requested_http_status_counts, key=int)
        },
        "requested_http_status_key_count": len(requested_http_status_counts),
        "healthy_http_status_counts": {
            status: healthy_http_status_counts[status] for status in sorted(healthy_http_status_counts, key=int)
        },
        "healthy_http_status_key_count": len(healthy_http_status_counts),
        "failed_http_status_counts": {
            status: failed_http_status_counts[status] for status in sorted(failed_http_status_counts, key=int)
        },
        "failed_http_status_key_count": len(failed_http_status_counts),
        "error_code_counts": {code: error_code_counts[code] for code in sorted(error_code_counts)},
        "error_code_key_count": len(error_code_counts),
        "failed_error_code_counts": {
            code: failed_error_code_counts[code] for code in sorted(failed_error_code_counts)
        },
        "failed_error_code_key_count": len(failed_error_code_counts),
        "error_samples": error_samples,
        "primary_error_sample_probe": primary_error_sample_probe,
        "primary_error_sample_status": primary_error_sample_status,
        "primary_error_sample_error_code": primary_error_sample_error_code,
        "primary_error_sample_http_status": primary_error_sample_http_status,
        "primary_error_sample_reachability": primary_error_sample_reachability,
        "error_sample_count": error_sample_count,
        "has_error_sample": bool(error_sample_count),
        "error_sample_status_counts": {
            status: error_sample_status_counts[status] for status in sorted(error_sample_status_counts)
        },
        "error_sample_status_key_count": len(error_sample_status_counts),
        "error_sample_probe_counts": {
            probe: error_sample_probe_counts[probe] for probe in sorted(error_sample_probe_counts)
        },
        "error_sample_probe_key_count": len(error_sample_probe_counts),
        "error_sample_http_status_counts": {
            status: error_sample_http_status_counts[status]
            for status in sorted(error_sample_http_status_counts)
        },
        "error_sample_http_status_key_count": len(error_sample_http_status_counts),
        "error_sample_reachability_counts": {
            status: error_sample_reachability_counts[status]
            for status in sorted(error_sample_reachability_counts)
        },
        "error_sample_reachability_key_count": len(error_sample_reachability_counts),
        "error_sample_limit": PROVIDER_REPLAY_PROBE_ERROR_SAMPLE_LIMIT,
        "error_sample_visible_count": error_sample_visible_count,
        "has_visible_error_sample": bool(error_sample_visible_count),
        "error_sample_hidden_count": error_sample_hidden_count,
        "has_hidden_error_sample": bool(error_sample_hidden_count),
        "error_sample_truncated": error_sample_truncated,
        "error_sample_summary": error_sample_summary,
        "requested": requested,
        "primary_requested_probe": requested[0] if requested else None,
        "healthy": healthy,
        "primary_healthy_probe": healthy[0] if healthy else None,
        "failed": failed,
        "primary_failed_probe": failed[0] if failed else None,
        "unhealthy": unhealthy,
        "primary_unhealthy_probe": unhealthy[0] if unhealthy else None,
        "primary_problem_probe": primary_problem_probe,
        "not_requested": not_requested,
        "primary_not_requested_probe": not_requested[0] if not_requested else None,
        "boundary": "read_only_probe_rollup; does_not_start_socket_or_manage_daemon_lifecycle",
    }


def _provider_replay_health_probe_url(config: ProviderTransportReplayConfig) -> str:
    host = config.bind_host.strip()
    if host in {"0.0.0.0", "::"}:
        host = "127.0.0.1"
    elif ":" in host and not host.startswith("["):
        host = f"[{host}]"
    return f"http://{host}:{config.port}/provider/v1/replay/health"


def _provider_replay_watch_status_probe_url(config: ProviderTransportReplayConfig) -> str:
    host = config.bind_host.strip()
    if host in {"0.0.0.0", "::"}:
        host = "127.0.0.1"
    elif ":" in host and not host.startswith("["):
        host = f"[{host}]"
    return f"http://{host}:{config.port}/provider/v1/replay/watch/status"


def _provider_replay_watch_events_probe_url(config: ProviderTransportReplayConfig) -> str:
    host = config.bind_host.strip()
    if host in {"0.0.0.0", "::"}:
        host = "127.0.0.1"
    elif ":" in host and not host.startswith("["):
        host = f"[{host}]"
    return f"http://{host}:{config.port}/provider/v1/replay/watch/events"


def _provider_replay_watch_stream_probe_url(config: ProviderTransportReplayConfig) -> str:
    host = config.bind_host.strip()
    if host in {"0.0.0.0", "::"}:
        host = "127.0.0.1"
    elif ":" in host and not host.startswith("["):
        host = f"[{host}]"
    return f"http://{host}:{config.port}/provider/v1/replay/watch/events/stream?playback=immediate"


def _build_probe_result(
    *,
    status: str,
    reachable: bool,
    timeout_seconds: float | None,
    url: str,
    http_status: int | None = None,
    error: str | None = None,
    error_code: str | None = None,
    service: str | None = None,
    provider_id: str | None = None,
    provider_mode: str | None = None,
    target: str | None = None,
    endpoint: str | None = None,
    state: str | None = None,
    event_count: int | None = None,
    frame_count: int | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "enabled": True,
        "status": status,
        "reachable": reachable,
        "http_status": http_status,
        "timeout_seconds": timeout_seconds,
        "url": url,
    }
    if error:
        result["error"] = error
    if error_code:
        result["error_code"] = error_code
    if service:
        result["service"] = service
    if provider_id:
        result["provider_id"] = provider_id
    if provider_mode:
        result["provider_mode"] = provider_mode
    if target:
        result["target"] = target
    if endpoint:
        result["endpoint"] = endpoint
    if state:
        result["state"] = state
    if event_count is not None:
        result["event_count"] = event_count
    if frame_count is not None:
        result["frame_count"] = frame_count
    return result


def _decode_probe_http_error(exc: HTTPError) -> dict[str, str | None]:
    try:
        payload = json.loads(exc.read().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"code": None, "message": str(exc)}
    error = payload.get("error") if isinstance(payload, dict) else None
    if isinstance(error, dict):
        return {
            "code": str(error.get("code") or "") or None,
            "message": str(error.get("message") or "") or None,
        }
    return {"code": None, "message": str(exc)}


def _probe_error_message(exc: BaseException) -> str:
    reason = getattr(exc, "reason", None)
    if reason is not None:
        return str(reason)
    return str(exc)


def build_replay_transport_success(
    *,
    provider_id: str,
    request_id: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "ok": True,
        "result": result,
        "error": None,
        "meta": {
            "provider_id": provider_id,
            "provider_mode": "replay",
            "transport": "http",
            "schema_version": REPLAY_TRANSPORT_VERSION,
            "request_id": request_id,
        },
    }


def build_replay_transport_failure(
    *,
    provider_id: str,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "ok": False,
        "result": None,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
        "meta": {
            "provider_id": provider_id,
            "provider_mode": "replay",
            "transport": "http",
            "schema_version": REPLAY_TRANSPORT_VERSION,
            "request_id": request_id,
        },
    }


def _encode_sse_frame(frame: dict[str, Any]) -> str:
    payload = json.dumps(frame, ensure_ascii=False, separators=(",", ":"))
    cursor = str(frame.get("cursor") or "")
    frame_type = str(frame.get("frame_type") or "message")
    return f"id: {cursor}\nevent: {frame_type}\ndata: {payload}\n\n"


class ProviderTransportReplayHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, config: ProviderTransportReplayConfig) -> None:
        super().__init__((config.bind_host, config.port), ProviderTransportReplayRequestHandler)
        self.replay_config = config


class ProviderTransportReplayRequestHandler(BaseHTTPRequestHandler):
    server: ProviderTransportReplayHTTPServer

    def do_GET(self) -> None:  # noqa: N802
        self._handle_request()

    def log_message(self, format: str, *args: object) -> None:
        del format, args

    def _handle_request(self) -> None:
        config = self.server.replay_config
        request_id = self.headers.get("X-Request-Id") or uuid4().hex
        source_ip = self.client_address[0]
        parsed = urlparse(self.path)

        if config.master_allowlist and source_ip not in set(config.master_allowlist):
            self._write_json(
                403,
                build_replay_transport_failure(
                    provider_id=config.provider_id,
                    request_id=request_id,
                    code="FORBIDDEN_SOURCE",
                    message="source ip is not allowed",
                    details={"source_ip": source_ip},
                ),
            )
            return

        auth_header = self.headers.get("Authorization") or ""
        if auth_header != f"Bearer {config.token}":
            self._write_json(
                401,
                build_replay_transport_failure(
                    provider_id=config.provider_id,
                    request_id=request_id,
                    code="UNAUTHORIZED",
                    message="missing or invalid bearer token",
                ),
            )
            return

        try:
            if parsed.path == "/provider/v1/replay/health":
                self._handle_health(request_id)
                return
            if parsed.path == "/provider/v1/replay/fixtures":
                self._handle_fixtures(request_id)
                return
            if parsed.path == "/provider/v1/replay/result":
                self._handle_result(request_id)
                return
            if parsed.path == "/provider/v1/replay/watch/status":
                self._handle_watch_status(request_id)
                return
            if parsed.path == "/provider/v1/replay/watch/events":
                self._handle_watch_events(request_id)
                return
            if parsed.path == "/provider/v1/replay/watch/events/stream":
                self._handle_watch_event_stream(request_id)
                return
            self._write_json(
                404,
                build_replay_transport_failure(
                    provider_id=config.provider_id,
                    request_id=request_id,
                    code="NOT_FOUND",
                    message="unsupported replay endpoint",
                    details={"path": parsed.path},
                ),
            )
        except ValueError as exc:
            self._write_json(
                400,
                build_replay_transport_failure(
                    provider_id=config.provider_id,
                    request_id=request_id,
                    code="INVALID_REQUEST",
                    message=str(exc),
                ),
            )
        except Exception as exc:
            self._write_json(
                500,
                build_replay_transport_failure(
                    provider_id=config.provider_id,
                    request_id=request_id,
                    code="INTERNAL_ERROR",
                    message=str(exc),
                ),
            )

    def _handle_health(self, request_id: str) -> None:
        self._write_success(
            request_id,
            {
                "status": "ok",
                "service": "provider-transport-replay",
                "provider_id": self.server.replay_config.provider_id,
                "provider_mode": "replay",
                "live_runtime_required": False,
            },
        )

    def _handle_fixtures(self, request_id: str) -> None:
        self._write_success(
            request_id,
            {
                "fixtures": list_provider_replay_fixtures(),
                "provider_mode": "replay",
            },
        )

    def _handle_result(self, request_id: str) -> None:
        query = self._query()
        capability = self._optional_str(query.get("capability", [None])[0])
        if not capability:
            raise ValueError("query parameter capability is required")
        result = execute_sync_replay(
            capability,
            replay_fixture=self._optional_str(query.get("fixture", [None])[0]),
            replay_fixture_path=self._optional_str(query.get("fixture_path", [None])[0]),
        )
        provider_result = result.to_dict()
        if not result.ok and result.code == ErrorCode.INVALID_REQUEST:
            self._write_json(
                400,
                build_replay_transport_failure(
                    provider_id=self.server.replay_config.provider_id,
                    request_id=request_id,
                    code=result.code.value,
                    message=result.message,
                    details={"provider_result": provider_result},
                ),
            )
            return
        self._write_success(request_id, {"provider_result": provider_result})

    def _handle_watch_status(self, request_id: str) -> None:
        source = self._load_watch_source()
        watch_status = copy.deepcopy(source.status)
        state = self._optional_str(watch_status.get("state")) or "completed"
        run_id = self._optional_str(watch_status.get("run_id"))
        self._write_success(
            request_id,
            {
                "control": {
                    "state": state,
                    "active": False,
                    "run_id": run_id,
                    "provider_mode": "replay",
                },
                "watch_status": watch_status,
                "replay_source": self._replay_source_payload(source),
            },
        )

    def _handle_watch_events(self, request_id: str) -> None:
        source = self._load_watch_source()
        events = [copy.deepcopy(item) for item in source.events]
        tail = self._query_int("tail", default=len(events))
        if tail >= 0:
            events = events[-tail:] if tail else []
        self._write_success(
            request_id,
            {
                "run_id": self._optional_str(source.status.get("run_id")),
                "events": events,
                "replay_source": self._replay_source_payload(source),
            },
        )

    def _handle_watch_event_stream(self, request_id: str) -> None:
        source = self._load_watch_source()
        query = self._query()
        playback = self._optional_str(query.get("playback", [None])[0]) or "immediate"
        if playback not in {"immediate", "delayed"}:
            raise ValueError("query parameter playback must be immediate or delayed")
        delay_ms = self._query_int("delay_ms", default=0)
        if playback == "delayed" and delay_ms <= 0:
            delay_ms = 250
        frames = self._build_watch_event_stream_frames(
            request_id=request_id,
            source=source,
            playback=playback,
            delay_ms=delay_ms,
        )
        self._write_sse(200, frames)

    def _build_watch_event_stream_frames(
        self,
        *,
        request_id: str,
        source: Any,
        playback: str,
        delay_ms: int,
    ) -> list[dict[str, Any]]:
        watch_status = copy.deepcopy(source.status)
        events = [copy.deepcopy(item) for item in source.events]
        run_id = self._optional_str(watch_status.get("run_id")) or "replay-run"
        state = self._optional_str(watch_status.get("state")) or "completed"
        replay_source = self._replay_source_payload(source)

        frames: list[dict[str, Any]] = [
            self._build_stream_frame(
                run_id=run_id,
                frame_type="status",
                cursor=f"{run_id}:status",
                playback=self._playback_payload(playback, delay_ms, planned_emit_after_ms=0),
                replay_source=replay_source,
                status={
                    "request_id": request_id,
                    "control": {
                        "state": state,
                        "active": False,
                        "run_id": run_id,
                        "provider_mode": "replay",
                    },
                    "watch_status": watch_status,
                },
            )
        ]

        for index, event in enumerate(events, start=1):
            sequence = event.get("sequence")
            cursor_sequence = sequence if isinstance(sequence, int) else index
            planned = index * delay_ms if playback == "delayed" else 0
            frames.append(
                self._build_stream_frame(
                    run_id=self._optional_str(event.get("run_id")) or run_id,
                    frame_type="quote",
                    cursor=f"{run_id}:event:{cursor_sequence}",
                    playback=self._playback_payload(playback, delay_ms, planned_emit_after_ms=planned),
                    replay_source=replay_source,
                    event=event,
                )
            )

        if not events:
            frames.append(
                self._build_stream_frame(
                    run_id=run_id,
                    frame_type="heartbeat",
                    cursor=f"{run_id}:heartbeat",
                    playback=self._playback_payload(playback, delay_ms, planned_emit_after_ms=0),
                    replay_source=replay_source,
                    status={"request_id": request_id, "watch_status": watch_status},
                )
            )

        if state in WATCH_TERMINAL_STATES:
            planned = (len(events) + 1) * delay_ms if playback == "delayed" else 0
            frames.append(
                self._build_stream_frame(
                    run_id=run_id,
                    frame_type="terminal",
                    cursor=f"{run_id}:terminal",
                    playback=self._playback_payload(playback, delay_ms, planned_emit_after_ms=planned),
                    replay_source=replay_source,
                    status={"request_id": request_id, "watch_status": watch_status},
                )
            )
        return frames

    @staticmethod
    def _build_stream_frame(
        *,
        run_id: str,
        frame_type: str,
        cursor: str,
        playback: dict[str, Any],
        replay_source: dict[str, Any],
        status: dict[str, Any] | None = None,
        event: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        frame: dict[str, Any] = {
            "schema_version": WATCH_EVENT_STREAM_SCHEMA_VERSION,
            "transport": "sse",
            "provider_mode": "replay",
            "run_id": run_id,
            "cursor": cursor,
            "frame_type": frame_type,
            "playback": playback,
            "replay_source": replay_source,
        }
        if status is not None:
            frame["status"] = status
        if event is not None:
            frame["event"] = event
        return frame

    @staticmethod
    def _playback_payload(playback: str, delay_ms: int, *, planned_emit_after_ms: int) -> dict[str, Any]:
        return {
            "mode": playback,
            "delay_ms": delay_ms if playback == "delayed" else 0,
            "planned_emit_after_ms": planned_emit_after_ms,
        }

    def _load_watch_source(self) -> Any:
        query = self._query()
        fixture = self._optional_str(query.get("fixture", [None])[0]) or self.server.replay_config.replay_fixture
        fixture_path = self._optional_str(query.get("fixture_path", [None])[0]) or self.server.replay_config.replay_fixture_path
        return load_subscription_watch_replay_source(
            replay_fixture=fixture,
            replay_fixture_path=fixture_path,
        )

    @staticmethod
    def _replay_source_payload(source: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "mode": "replay",
            "source_kind": source.source_kind,
            "capability": "subscription.watch",
        }
        if source.fixture_name is not None:
            payload["fixture"] = source.fixture_name
        if source.path is not None:
            payload["path"] = str(source.path)
        return payload

    def _query(self) -> dict[str, list[str]]:
        return parse_qs(urlparse(self.path).query)

    def _query_int(self, name: str, *, default: int) -> int:
        raw_value = self._query().get(name, [default])[0]
        try:
            return int(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"query parameter {name} must be an integer") from exc

    @staticmethod
    def _optional_str(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _write_success(self, request_id: str, result: dict[str, Any]) -> None:
        self._write_json(
            200,
            build_replay_transport_success(
                provider_id=self.server.replay_config.provider_id,
                request_id=request_id,
                result=result,
            ),
        )

    def _write_json(self, status_code: int, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _write_sse(self, status_code: int, frames: list[dict[str, Any]]) -> None:
        encoded = "".join(_encode_sse_frame(frame) for frame in frames).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def serve_provider_transport_replay(config: ProviderTransportReplayConfig) -> int:
    server = ProviderTransportReplayHTTPServer(config)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


def load_provider_transport_replay_config(config_path: str | Path) -> ProviderTransportReplayConfig:
    payload = json.loads(Path(config_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("provider transport replay config must be a JSON object")
    return ProviderTransportReplayConfig(
        provider_id=str(payload.get("provider_id") or "").strip(),
        bind_host=str(payload.get("bind_host") or "").strip(),
        port=int(payload.get("port") or 0),
        token=str(payload.get("token") or ""),
        master_allowlist=[str(item) for item in payload.get("master_allowlist") or []],
        replay_fixture=str(payload["replay_fixture"]) if payload.get("replay_fixture") is not None else None,
        replay_fixture_path=str(payload["replay_fixture_path"]) if payload.get("replay_fixture_path") is not None else None,
    )
