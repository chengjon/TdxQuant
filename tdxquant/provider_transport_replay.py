from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse
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
