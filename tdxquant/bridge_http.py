from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from typing import Any
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from .subscription_watch_background import (
    SubscriptionWatchBackgroundController,
    build_background_paths,
)

BRIDGE_VERSION = "v1"
WATCH_EVENT_STREAM_SCHEMA_VERSION = "tdx.bridge.watch.event_stream.v1"
WATCH_EVENT_STREAM_TRANSPORT = "sse"
WATCH_TERMINAL_STATES = {"completed", "interrupted", "failed", "stopped"}
WATCH_STATUS_REASON_SAMPLE_LIMIT = 3
WATCH_STATUS_ACTION_SAMPLE_LIMIT = 3


@dataclass(frozen=True)
class BridgeConfig:
    worker_id: str
    bind_host: str
    port: int
    token: str
    master_allowlist: list[str]
    run_root_dir: str
    log_dir: str | None = None
    start_timeout_seconds: int = 10
    stop_grace_period_seconds: int = 5
    stop_force_kill_timeout_seconds: int = 2

    def __post_init__(self) -> None:
        if not self.token.strip():
            raise ValueError("bridge token is required")


def build_bridge_success(*, worker_id: str, request_id: str, result: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "result": result,
        "error": None,
        "meta": {
            "bridge_version": BRIDGE_VERSION,
            "worker_id": worker_id,
            "request_id": request_id,
        },
    }


def build_bridge_failure(
    *,
    worker_id: str,
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
            "bridge_version": BRIDGE_VERSION,
            "worker_id": worker_id,
            "request_id": request_id,
        },
    }


def build_bridge_watch_status_summary_result(result: dict[str, Any], *, worker_id: str) -> dict[str, Any]:
    status_summary = result.get("status_summary")
    status_summary = status_summary if isinstance(status_summary, dict) else {}
    governance = status_summary.get("governance")
    governance = governance if isinstance(governance, dict) else {}

    summary_view: dict[str, Any] = {
        "mode": "summary",
        "worker": worker_id,
        "status": status_summary.get("overall_status", result.get("status")),
    }

    runtime_view = build_bridge_watch_status_runtime_view(result)
    if runtime_view:
        summary_view["runtime"] = runtime_view

    if status_summary:
        status_view: dict[str, Any] = {}
        for key in ("schema_version", "overall_status", "heartbeat", "watermark", "reconnect"):
            if key in status_summary:
                status_view[key] = copy.deepcopy(status_summary[key])
        summary_view["status_summary"] = status_view

    if governance:
        governance_view: dict[str, Any] = {}
        for key in (
            "decision",
            "requires_manual_review",
            "staleness_evaluated",
            "boundary",
            "reason_source_counts",
            "reason_summary",
            "action_summary",
            "evaluation_summary",
        ):
            if key in governance:
                governance_view[key] = copy.deepcopy(governance[key])
        reasons = governance.get("reasons")
        if isinstance(reasons, list):
            governance_view["reason_count"] = len(reasons)
            reason_samples = [reason for reason in reasons if isinstance(reason, str)][
                :WATCH_STATUS_REASON_SAMPLE_LIMIT
            ]
            governance_view["reason_samples"] = reason_samples
            governance_view["reason_sample_limit"] = WATCH_STATUS_REASON_SAMPLE_LIMIT
            governance_view["reason_sample_truncated"] = len(reasons) > len(reason_samples)
        actions = governance.get("actions")
        if isinstance(actions, list):
            governance_view["action_count"] = len(actions)
            action_samples = build_bridge_watch_status_action_samples(actions)
            governance_view["action_samples"] = action_samples
            governance_view["action_sample_limit"] = WATCH_STATUS_ACTION_SAMPLE_LIMIT
            governance_view["action_sample_truncated"] = len(actions) > len(action_samples)
        summary_view["governance"] = governance_view

    return summary_view


def build_bridge_watch_status_action_samples(actions: list[object]) -> list[dict[str, str]]:
    samples: list[dict[str, str]] = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        sample: dict[str, str] = {}
        for key in ("action", "reason", "severity"):
            value = action.get(key)
            if isinstance(value, str) and value:
                sample[key] = value
        if sample:
            samples.append(sample)
        if len(samples) >= WATCH_STATUS_ACTION_SAMPLE_LIMIT:
            break
    return samples


def build_bridge_watch_status_runtime_view(result: dict[str, Any]) -> dict[str, Any]:
    control = result.get("control")
    control = control if isinstance(control, dict) else {}
    watch_status = result.get("watch_status")
    watch_status = watch_status if isinstance(watch_status, dict) else {}

    runtime_view: dict[str, Any] = {}
    if "state" in control:
        runtime_view["control_state"] = control["state"]
    if "active" in control:
        runtime_view["active"] = control["active"]
    if "state" in watch_status:
        runtime_view["watch_state"] = watch_status["state"]

    run_id = watch_status.get("run_id", control.get("run_id"))
    if run_id is not None:
        runtime_view["run_id"] = run_id
    if "pid" in control:
        runtime_view["pid"] = control["pid"]
    return runtime_view


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_watch_event_stream_frame(
    *,
    run_id: str | None,
    frame_type: str,
    cursor: str,
    event: dict[str, Any] | None = None,
    status: dict[str, Any] | None = None,
    reconnect: dict[str, Any] | None = None,
) -> dict[str, Any]:
    frame: dict[str, Any] = {
        "schema_version": WATCH_EVENT_STREAM_SCHEMA_VERSION,
        "transport": WATCH_EVENT_STREAM_TRANSPORT,
        "run_id": run_id,
        "cursor": cursor,
        "frame_type": frame_type,
        "emitted_at": _now_utc_iso(),
    }
    if event is not None:
        frame["event"] = event
    if status is not None:
        frame["status"] = status
    if reconnect is not None:
        frame["reconnect"] = reconnect
    return frame


def _encode_sse_frame(frame: dict[str, Any]) -> str:
    payload = json.dumps(frame, ensure_ascii=False, separators=(",", ":"))
    cursor = str(frame.get("cursor") or "")
    frame_type = str(frame.get("frame_type") or "message")
    return f"id: {cursor}\nevent: {frame_type}\ndata: {payload}\n\n"


def load_bridge_config(config_path: str | Path) -> BridgeConfig:
    payload = json.loads(Path(config_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("bridge config must be a JSON object")
    bind_host = payload.get("bind_host")
    if not isinstance(bind_host, str) or not bind_host.strip():
        raise ValueError("bridge config requires a non-empty bind_host")
    return BridgeConfig(
        worker_id=str(payload.get("worker_id") or "").strip(),
        bind_host=bind_host.strip(),
        port=int(payload.get("port") or 0),
        token=str(payload.get("token") or ""),
        master_allowlist=[str(item) for item in payload.get("master_allowlist") or []],
        run_root_dir=str(payload.get("run_root_dir") or "runtime/subscription-watch"),
        log_dir=str(payload["log_dir"]) if payload.get("log_dir") is not None else None,
        start_timeout_seconds=int(10 if payload.get("start_timeout_seconds") is None else payload.get("start_timeout_seconds")),
        stop_grace_period_seconds=int(
            5 if payload.get("stop_grace_period_seconds") is None else payload.get("stop_grace_period_seconds")
        ),
        stop_force_kill_timeout_seconds=int(
            2
            if payload.get("stop_force_kill_timeout_seconds") is None
            else payload.get("stop_force_kill_timeout_seconds")
        ),
    )


class BridgeHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        config: BridgeConfig,
        *,
        controller: SubscriptionWatchBackgroundController | Any | None = None,
    ) -> None:
        super().__init__((config.bind_host, config.port), BridgeRequestHandler)
        self.bridge_config = config
        self.run_root_dir = Path(config.run_root_dir)
        self.background_paths = build_background_paths(self.run_root_dir)
        self.bridge_controller = controller or SubscriptionWatchBackgroundController(
            root_dir=self.run_root_dir,
            python_executable=sys.executable,
            start_timeout_seconds=config.start_timeout_seconds,
            default_stop_grace_period_seconds=config.stop_grace_period_seconds,
            stop_force_kill_timeout_seconds=config.stop_force_kill_timeout_seconds,
        )


class BridgeRequestHandler(BaseHTTPRequestHandler):
    server: BridgeHTTPServer

    def do_GET(self) -> None:  # noqa: N802
        self._handle_request("GET")

    def do_POST(self) -> None:  # noqa: N802
        self._handle_request("POST")

    def log_message(self, format: str, *args: object) -> None:
        del format, args

    def _handle_request(self, method: str) -> None:
        config = self.server.bridge_config
        request_id = self.headers.get("X-Request-Id") or uuid4().hex
        source_ip = self.client_address[0]
        parsed = urlparse(self.path)

        if config.master_allowlist and source_ip not in set(config.master_allowlist):
            self._write_json(
                403,
                build_bridge_failure(
                    worker_id=config.worker_id,
                    request_id=request_id,
                    code="FORBIDDEN_SOURCE",
                    message="source ip is not allowed",
                    details={"source_ip": source_ip},
                ),
            )
            return

        auth_header = self.headers.get("Authorization") or ""
        expected = f"Bearer {config.token}"
        if auth_header != expected:
            self._write_json(
                401,
                build_bridge_failure(
                    worker_id=config.worker_id,
                    request_id=request_id,
                    code="UNAUTHORIZED",
                    message="missing or invalid bearer token",
                ),
            )
            return

        try:
            if method == "GET" and parsed.path == "/bridge/v1/health":
                control = self.server.bridge_controller.control_status()
                self._write_json(
                    200,
                    build_bridge_success(
                        worker_id=config.worker_id,
                        request_id=request_id,
                        result={
                            "status": "ok",
                            "worker_id": config.worker_id,
                            "control": control,
                        },
                    ),
                )
                return
            if method == "POST" and parsed.path == "/bridge/v1/watch/start":
                self._handle_watch_start(request_id)
                return
            if method == "POST" and parsed.path == "/bridge/v1/watch/stop":
                self._handle_watch_stop(request_id)
                return
            if method == "GET" and parsed.path == "/bridge/v1/watch/status":
                self._handle_watch_status(request_id)
                return
            if method == "GET" and parsed.path == "/bridge/v1/watch/list":
                self._handle_watch_list(request_id)
                return
            if method == "GET" and parsed.path == "/bridge/v1/watch/artifacts":
                self._handle_watch_artifacts(request_id)
                return
            if method == "GET" and parsed.path == "/bridge/v1/watch/events/stream":
                self._handle_watch_event_stream(request_id)
                return
            if method == "GET" and parsed.path == "/bridge/v1/watch/events":
                self._handle_watch_events(request_id)
                return
            if method == "GET" and parsed.path == "/bridge/v1/watch/logs":
                self._handle_watch_logs(request_id)
                return
            self._write_json(
                404,
                build_bridge_failure(
                    worker_id=config.worker_id,
                    request_id=request_id,
                    code="NOT_FOUND",
                    message="unsupported bridge endpoint",
                    details={"path": parsed.path, "method": method},
                ),
            )
        except ValueError as exc:
            self._write_json(
                400,
                build_bridge_failure(
                    worker_id=config.worker_id,
                    request_id=request_id,
                    code="INVALID_REQUEST",
                    message=str(exc),
                ),
            )
        except Exception as exc:
            self._write_json(
                500,
                build_bridge_failure(
                    worker_id=config.worker_id,
                    request_id=request_id,
                    code="INTERNAL_ERROR",
                    message=str(exc),
                ),
            )

    def _handle_watch_start(self, request_id: str) -> None:
        body = self._read_json_body()
        stock_list = body.get("stock_list")
        if not isinstance(stock_list, list) or not all(isinstance(item, str) for item in stock_list):
            raise ValueError("watch start requires stock_list as a JSON string array")
        result = self.server.bridge_controller.start(
            stock_list=list(stock_list),
            max_events=self._optional_int(body.get("max_events")),
            max_seconds=self._optional_float(body.get("max_seconds")),
            poll_interval=self._optional_float(body.get("poll_interval")),
            idempotency_key=self._optional_str(body.get("idempotency_key")),
        )
        self._write_control_result(result, request_id=request_id)

    def _handle_watch_stop(self, request_id: str) -> None:
        body = self._read_json_body()
        grace_period = self.server.bridge_config.stop_grace_period_seconds
        if "grace_period_seconds" in body:
            grace_period = self._optional_int(body.get("grace_period_seconds"))
        result = self.server.bridge_controller.stop(
            reason=self._optional_str(body.get("reason")),
            grace_period_seconds=grace_period,
        )
        self._write_control_result(result, request_id=request_id)

    def _handle_watch_status(self, request_id: str) -> None:
        view = self._query_optional_str("view") or "detailed"
        if view not in {"detailed", "summary"}:
            raise ValueError("query parameter view must be one of: detailed, summary")
        result = self.server.bridge_controller.status(
            heartbeat_stale_after_seconds=self._query_optional_float("heartbeat_stale_after_seconds"),
            watermark_stale_after_seconds=self._query_optional_float("watermark_stale_after_seconds"),
            reconnect_stale_after_seconds=self._query_optional_float("reconnect_stale_after_seconds"),
        )
        if view == "summary":
            result = build_bridge_watch_status_summary_result(
                result,
                worker_id=self.server.bridge_config.worker_id,
            )
        self._write_json(
            200,
            build_bridge_success(
                worker_id=self.server.bridge_config.worker_id,
                request_id=request_id,
                result=result,
            ),
        )

    def _handle_watch_list(self, request_id: str) -> None:
        result = self.server.bridge_controller.list_runs()
        self._write_json(200, build_bridge_success(worker_id=self.server.bridge_config.worker_id, request_id=request_id, result=result))

    def _handle_watch_artifacts(self, request_id: str) -> None:
        run_id = self._resolve_run_id()
        result = self.server.bridge_controller.artifacts(run_id=run_id)
        self._write_json(
            200,
            build_bridge_success(
                worker_id=self.server.bridge_config.worker_id,
                request_id=request_id,
                result=result,
            ),
        )

    def _handle_watch_events(self, request_id: str) -> None:
        run_id = self._resolve_run_id()
        tail = self._query_int("tail", default=100)
        result = self.server.bridge_controller.events(run_id=run_id, tail=tail)
        self._write_json(
            200,
            build_bridge_success(
                worker_id=self.server.bridge_config.worker_id,
                request_id=request_id,
                result=result,
            ),
        )

    def _handle_watch_event_stream(self, request_id: str) -> None:
        run_id = self._resolve_run_id()
        tail = self._query_int("tail", default=100)
        heartbeat_seconds = self._query_int("heartbeat_seconds", default=15)
        status_result = self.server.bridge_controller.status()
        events_result = self.server.bridge_controller.events(run_id=run_id, tail=tail)
        frames = self._build_watch_event_stream_frames(
            request_id=request_id,
            run_id=run_id,
            status_result=status_result,
            events_result=events_result,
            from_cursor=self._stream_resume_cursor(),
            heartbeat_seconds=heartbeat_seconds,
        )
        self._write_sse(200, frames)

    def _handle_watch_logs(self, request_id: str) -> None:
        run_id = self._resolve_run_id()
        tail = self._query_int("tail", default=200)
        result = self.server.bridge_controller.logs(run_id=run_id, tail=tail)
        self._write_json(
            200,
            build_bridge_success(
                worker_id=self.server.bridge_config.worker_id,
                request_id=request_id,
                result=result,
            ),
        )

    def _write_control_result(self, result: dict[str, Any], *, request_id: str) -> None:
        if result.get("ok") is True:
            self._write_json(
                200,
                build_bridge_success(
                    worker_id=self.server.bridge_config.worker_id,
                    request_id=request_id,
                    result=dict(result.get("result") or {}),
                ),
            )
            return
        error = dict(result.get("error") or {})
        code = str(error.get("code") or "CONTROL_ERROR")
        if code == "INVALID_REQUEST":
            status = 400
        elif code in {"ALREADY_RUNNING", "CONTROL_LOCKED"}:
            status = 409
        else:
            status = 500
        self._write_json(
            status,
            build_bridge_failure(
                worker_id=self.server.bridge_config.worker_id,
                request_id=request_id,
                code=code,
                message=str(error.get("message") or "bridge control operation failed"),
                details=dict(error.get("details") or {}),
            ),
        )

    def _read_json_body(self) -> dict[str, Any]:
        raw_length = self.headers.get("Content-Length") or "0"
        length = int(raw_length)
        if length <= 0:
            return {}
        body = self.rfile.read(length).decode("utf-8")
        payload = json.loads(body)
        if not isinstance(payload, dict):
            raise ValueError("request body must be a JSON object")
        return payload

    def _resolve_run_id(self, *, default_run_id: Any = None) -> str | None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        explicit = self._optional_str(query.get("run_id", [None])[0])
        if explicit:
            return explicit
        fallback = self._optional_str(default_run_id)
        if fallback:
            return fallback
        active_payload = self.server.bridge_controller.control_status()
        active_run_id = self._optional_str(active_payload.get("run_id"))
        if active_run_id and bool(active_payload.get("active")):
            return active_run_id
        return None

    def _stream_resume_cursor(self) -> str | None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        explicit = self._optional_str(query.get("from", [None])[0])
        if explicit:
            return explicit
        return self._optional_str(self.headers.get("Last-Event-ID"))

    def _build_watch_event_stream_frames(
        self,
        *,
        request_id: str,
        run_id: str | None,
        status_result: dict[str, Any],
        events_result: dict[str, Any],
        from_cursor: str | None,
        heartbeat_seconds: int,
    ) -> list[dict[str, Any]]:
        control = status_result.get("control") if isinstance(status_result.get("control"), dict) else {}
        watch_status = (
            status_result.get("watch_status") if isinstance(status_result.get("watch_status"), dict) else {}
        )
        resolved_run_id = (
            run_id
            or self._optional_str(watch_status.get("run_id"))
            or self._optional_str(control.get("run_id"))
            or self._optional_str(events_result.get("run_id"))
        )
        status_projection = {
            "request_id": request_id,
            "control": control,
            "watch_status": watch_status,
        }
        reconnect_projection = self._build_reconnect_projection(watch_status)
        frames: list[dict[str, Any]] = [
            _build_watch_event_stream_frame(
                run_id=resolved_run_id,
                frame_type="status",
                cursor=f"{resolved_run_id or 'unknown'}:status",
                status=status_projection,
                reconnect=reconnect_projection,
            )
        ]

        raw_events = events_result.get("events") if isinstance(events_result.get("events"), list) else []
        requested_sequence = self._event_sequence_from_cursor(from_cursor)
        event_sequences = [
            int(item["sequence"])
            for item in raw_events
            if isinstance(item, dict) and isinstance(item.get("sequence"), int)
        ]
        if requested_sequence is not None and event_sequences and min(event_sequences) > requested_sequence + 1:
            raise ValueError("stream cursor is no longer available")

        emitted_quote = False
        for index, item in enumerate(raw_events, start=1):
            if not isinstance(item, dict):
                continue
            sequence = item.get("sequence")
            if isinstance(sequence, int):
                if requested_sequence is not None and sequence <= requested_sequence:
                    continue
                cursor = f"{resolved_run_id or item.get('run_id') or 'unknown'}:event:{sequence}"
            else:
                cursor = f"{resolved_run_id or item.get('run_id') or 'unknown'}:event:{index}"
            frames.append(
                _build_watch_event_stream_frame(
                    run_id=self._optional_str(item.get("run_id")) or resolved_run_id,
                    frame_type="quote",
                    cursor=cursor,
                    event=item,
                )
            )
            emitted_quote = True

        if not emitted_quote and heartbeat_seconds > 0:
            frames.append(
                _build_watch_event_stream_frame(
                    run_id=resolved_run_id,
                    frame_type="heartbeat",
                    cursor=f"{resolved_run_id or 'unknown'}:heartbeat",
                    status=status_projection,
                    reconnect=reconnect_projection,
                )
            )

        state = self._optional_str(watch_status.get("state")) or self._optional_str(control.get("state"))
        if state in WATCH_TERMINAL_STATES:
            frames.append(
                _build_watch_event_stream_frame(
                    run_id=resolved_run_id,
                    frame_type="terminal",
                    cursor=f"{resolved_run_id or 'unknown'}:terminal",
                    status=status_projection,
                    reconnect=reconnect_projection,
                )
            )
        return frames

    @staticmethod
    def _event_sequence_from_cursor(cursor: str | None) -> int | None:
        if not cursor or ":event:" not in cursor:
            return None
        raw_value = cursor.rsplit(":event:", 1)[-1]
        try:
            return int(raw_value)
        except ValueError:
            return None

    @staticmethod
    def _build_reconnect_projection(watch_status: dict[str, Any]) -> dict[str, Any]:
        keys = [
            "reconnect_count",
            "consecutive_reconnect_failures",
            "last_disconnect_at",
            "last_reconnect_at",
            "next_reconnect_at",
            "degraded_since",
            "last_error",
        ]
        return {key: watch_status.get(key) for key in keys if key in watch_status}

    def _query_int(self, name: str, *, default: int) -> int:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        raw_value = query.get(name, [default])[0]
        try:
            return int(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"query parameter {name} must be an integer") from exc

    def _query_optional_float(self, name: str) -> float | None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if name not in query:
            return None
        raw_value = query.get(name, [""])[0]
        try:
            value = float(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"query parameter {name} must be a number") from exc
        if value <= 0:
            raise ValueError(f"query parameter {name} must be positive")
        return value

    def _query_optional_str(self, name: str) -> str | None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if name not in query:
            return None
        raw_value = query.get(name, [""])[0]
        value = str(raw_value).strip()
        return value or None

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        if value is None or value == "":
            return None
        return int(value)

    @staticmethod
    def _optional_float(value: Any) -> float | None:
        if value is None or value == "":
            return None
        return float(value)

    @staticmethod
    def _optional_str(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

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


def serve_bridge_from_config(config_path: str | Path) -> int:
    config = load_bridge_config(config_path)
    server = BridgeHTTPServer(config)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0
