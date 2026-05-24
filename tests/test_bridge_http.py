from __future__ import annotations

import json
import os
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from tdxquant.bridge_http import BridgeConfig, BridgeHTTPServer, build_bridge_failure, build_bridge_success, load_bridge_config


class _FakeController:
    def __init__(self) -> None:
        self.start_calls: list[dict[str, object]] = []
        self.stop_calls: list[dict[str, object]] = []
        self.status_calls: list[dict[str, object]] = []
        self.control_status_calls = 0
        self.status_handler = None
        self.list_calls = 0
        self.artifact_calls: list[dict[str, object]] = []
        self.event_calls: list[dict[str, object]] = []
        self.log_calls: list[dict[str, object]] = []
        self.start_result: dict[str, object] = {"ok": True, "result": {"run_id": "run-001", "state": "starting"}}
        self.stop_result: dict[str, object] = {"ok": True, "result": {"run_id": "run-001", "state": "stopped"}}
        self.status_result: dict[str, object] = {
            "control": {"state": "running", "active": True, "run_id": "run-001", "pid": 1234, "reason": None},
            "watch_status": {"run_id": "run-001", "event_count": 3},
        }
        self.list_result: dict[str, object] = {"active": None, "last_completed": None, "last_failed": None}
        self.artifact_result: dict[str, object] = {"run_id": "run-001", "artifacts": {"run_dir": "/tmp/run-001"}}
        self.events_result: dict[str, object] = {"run_id": "run-001", "events": []}
        self.logs_result: dict[str, object] = {"run_id": "run-001", "lines": []}

    def start(self, **kwargs: object) -> dict[str, object]:
        self.start_calls.append(dict(kwargs))
        return dict(self.start_result)

    def stop(self, **kwargs: object) -> dict[str, object]:
        self.stop_calls.append(dict(kwargs))
        return dict(self.stop_result)

    def status(self, **kwargs: object) -> dict[str, object]:
        self.status_calls.append(dict(kwargs))
        if self.status_handler is not None:
            return dict(self.status_handler(**kwargs))
        return dict(self.status_result)

    def control_status(self) -> dict[str, object]:
        self.control_status_calls += 1
        payload = self.status()
        return dict(payload.get("control") or {})

    def list_runs(self) -> dict[str, object]:
        self.list_calls += 1
        return dict(self.list_result)

    def artifacts(self, **kwargs: object) -> dict[str, object]:
        self.artifact_calls.append(dict(kwargs))
        return dict(self.artifact_result)

    def events(self, **kwargs: object) -> dict[str, object]:
        self.event_calls.append(dict(kwargs))
        return dict(self.events_result)

    def logs(self, **kwargs: object) -> dict[str, object]:
        self.log_calls.append(dict(kwargs))
        return dict(self.logs_result)


class BridgeEnvelopeTests(unittest.TestCase):
    def test_build_bridge_success_uses_required_envelope_fields(self) -> None:
        payload = build_bridge_success(worker_id="worker-a", request_id="req-001", result={"status": "running"})

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["result"]["status"], "running")
        self.assertIsNone(payload["error"])
        self.assertEqual(payload["meta"]["worker_id"], "worker-a")
        self.assertEqual(payload["meta"]["request_id"], "req-001")

    def test_build_bridge_failure_uses_required_envelope_fields(self) -> None:
        payload = build_bridge_failure(
            worker_id="worker-a",
            request_id="req-002",
            code="FORBIDDEN_SOURCE",
            message="source ip is not allowed",
            details={"source_ip": "127.0.0.1"},
        )

        self.assertFalse(payload["ok"])
        self.assertIsNone(payload["result"])
        self.assertEqual(payload["error"]["code"], "FORBIDDEN_SOURCE")
        self.assertEqual(payload["error"]["details"]["source_ip"], "127.0.0.1")
        self.assertEqual(payload["meta"]["worker_id"], "worker-a")

    def test_bridge_config_rejects_missing_token(self) -> None:
        with self.assertRaises(ValueError):
            BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=8080,
                token="",
                master_allowlist=["127.0.0.1"],
                run_root_dir="runtime/subscription-watch",
            )

    def test_load_bridge_config_requires_explicit_bind_host(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "bridge.json"
            config_path.write_text(
                json.dumps(
                    {
                        "worker_id": "worker-a",
                        "port": 8787,
                        "token": "secret-token",
                        "master_allowlist": ["127.0.0.1"],
                        "run_root_dir": "runtime/subscription-watch",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_bridge_config(config_path)

    def test_load_bridge_config_preserves_explicit_zero_timeout_values(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "bridge.json"
            config_path.write_text(
                json.dumps(
                    {
                        "worker_id": "worker-a",
                        "bind_host": "127.0.0.1",
                        "port": 8787,
                        "token": "secret-token",
                        "master_allowlist": ["127.0.0.1"],
                        "run_root_dir": "runtime/subscription-watch",
                        "start_timeout_seconds": 0,
                        "stop_grace_period_seconds": 0,
                        "stop_force_kill_timeout_seconds": 0,
                    }
                ),
                encoding="utf-8",
            )

            config = load_bridge_config(config_path)

        self.assertEqual(config.start_timeout_seconds, 0)
        self.assertEqual(config.stop_grace_period_seconds, 0)
        self.assertEqual(config.stop_force_kill_timeout_seconds, 0)


class BridgeRequestHandlerTests(unittest.TestCase):
    def _start_server(
        self,
        config: BridgeConfig,
        *,
        controller: _FakeController | None = None,
    ) -> tuple[BridgeHTTPServer, str, threading.Thread]:
        server = BridgeHTTPServer(config, controller=controller)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server, f"http://127.0.0.1:{server.server_address[1]}", thread

    def _request(
        self,
        url: str,
        *,
        method: str = "GET",
        token: str | None = None,
        payload: dict[str, object] | None = None,
    ) -> dict[str, object]:
        body = None
        headers: dict[str, str] = {}
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(url, data=body, headers=headers, method=method)
        with urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

    def _request_text(
        self,
        url: str,
        *,
        token: str | None = None,
    ) -> tuple[str, str]:
        headers: dict[str, str] = {}
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        request = Request(url, headers=headers, method="GET")
        with urlopen(request, timeout=5) as response:
            return response.headers.get_content_type(), response.read().decode("utf-8")

    @staticmethod
    def _parse_sse_payloads(raw: str) -> list[dict[str, object]]:
        payloads: list[dict[str, object]] = []
        for block in raw.strip().split("\n\n"):
            for line in block.splitlines():
                if line.startswith("data: "):
                    payloads.append(json.loads(line.removeprefix("data: ")))
        return payloads

    def test_health_requires_bearer_token(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                with self.assertRaises(HTTPError) as ctx:
                    self._request(f"{base_url}/bridge/v1/health")
                payload = json.loads(ctx.exception.read().decode("utf-8"))
                self.assertEqual(ctx.exception.code, 401)
                self.assertEqual(payload["error"]["code"], "UNAUTHORIZED")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_health_rejects_disallowed_source_ip(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["10.0.0.10"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                with self.assertRaises(HTTPError) as ctx:
                    self._request(f"{base_url}/bridge/v1/health", token="secret-token")
                payload = json.loads(ctx.exception.read().decode("utf-8"))
                self.assertEqual(ctx.exception.code, 403)
                self.assertEqual(payload["error"]["code"], "FORBIDDEN_SOURCE")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_health_returns_worker_metadata_when_authorized(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                payload = self._request(f"{base_url}/bridge/v1/health", token="secret-token")
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["status"], "ok")
                self.assertEqual(payload["meta"]["worker_id"], "worker-a")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_start_dispatches_to_controller(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config, controller=controller)
            try:
                payload = self._request(
                    f"{base_url}/bridge/v1/watch/start",
                    method="POST",
                    token="secret-token",
                    payload={
                        "stock_list": ["000001", "600519"],
                        "max_events": 2,
                        "poll_interval": 0.1,
                        "idempotency_key": "idem-001",
                    },
                )
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["run_id"], "run-001")
                self.assertEqual(controller.start_calls[0]["stock_list"], ["000001", "600519"])
                self.assertEqual(controller.start_calls[0]["max_events"], 2)
                self.assertEqual(controller.start_calls[0]["poll_interval"], 0.1)
                self.assertEqual(controller.start_calls[0]["idempotency_key"], "idem-001")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_status_reads_active_and_run_status_payloads(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            run_dir = root_dir / "run-001"
            run_dir.mkdir(parents=True)
            pid = os.getpid()
            (root_dir / "active.json").write_text(
                json.dumps({"state": "running", "active": True, "run_id": "run-001", "pid": pid, "reason": None}),
                encoding="utf-8",
            )
            (root_dir / "pid").write_text(f"{pid}\n", encoding="utf-8")
            (run_dir / "status.json").write_text(
                json.dumps({"run_id": "run-001", "state": "running", "event_count": 3}),
                encoding="utf-8",
            )
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                payload = self._request(f"{base_url}/bridge/v1/watch/status", token="secret-token")
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["control"]["run_id"], "run-001")
                self.assertEqual(payload["result"]["watch_status"]["event_count"], 3)
                self.assertNotIn("mode", payload["result"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_status_preserves_reconnecting_runtime_fields(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            live_result = {
                "control": {
                    "state": "reconnecting",
                    "active": True,
                    "run_id": "run-001",
                    "pid": 1234,
                    "reason": None,
                },
                "watch_status": {
                    "run_id": "run-001",
                    "state": "reconnecting",
                    "heartbeat_at": "2026-05-03T09:00:05+00:00",
                    "last_event_ts": "2026-05-03T09:00:02+00:00",
                    "reconnect_count": 1,
                    "consecutive_reconnect_failures": 1,
                    "last_error": {"code": "SESSION_LOST", "message": "session lost"},
                },
            }
            historical_result = {
                "control": dict(live_result["control"]),
                "watch_status": {
                    "run_id": "run-001",
                    "state": "running",
                    "event_count": 3,
                },
            }
            controller.status_handler = lambda **kwargs: historical_result if kwargs.get("run_id") else live_result
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config, controller=controller)
            try:
                payload = self._request(f"{base_url}/bridge/v1/watch/status", token="secret-token")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["result"]["watch_status"]["state"], "reconnecting")
        self.assertEqual(payload["result"]["watch_status"]["reconnect_count"], 1)
        self.assertEqual(payload["result"]["watch_status"]["last_error"]["code"], "SESSION_LOST")

    def test_watch_status_forwards_heartbeat_stale_threshold_to_controller(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config, controller=controller)
            try:
                payload = self._request(
                    f"{base_url}/bridge/v1/watch/status?heartbeat_stale_after_seconds=60&watermark_stale_after_seconds=120&reconnect_stale_after_seconds=180",
                    token="secret-token",
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertTrue(payload["ok"])
        self.assertEqual(
            controller.status_calls,
            [
                {
                    "heartbeat_stale_after_seconds": 60.0,
                    "watermark_stale_after_seconds": 120.0,
                    "reconnect_stale_after_seconds": 180.0,
                }
            ],
        )

    def test_watch_status_summary_view_projects_governance_rollup(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            controller.status_result = {
                "control": {"state": "running", "active": True, "run_id": "run-001", "pid": 1234},
                "watch_status": {"state": "running", "run_id": "run-001", "event_count": 3},
                "status_summary": {
                    "overall_status": "degraded",
                    "heartbeat": {"status": "stale", "age_seconds": 180.0},
                    "watermark": {"status": "fresh", "age_seconds": 15.0},
                    "reconnect": {"status": "degraded", "reconnect_count": 2},
                    "governance": {
                        "decision": "manual_review",
                        "requires_manual_review": True,
                        "staleness_evaluated": True,
                        "boundary": "advisory_only; does_not_trigger_reconnect_backoff_restart_or_lifecycle_changes",
                        "reasons": [
                            "heartbeat:stale",
                            "overall_status:degraded",
                            "watermark:stale",
                            "reconnect:stale",
                        ],
                        "reason_source_counts": {
                            "heartbeat": 1,
                            "overall_status": 1,
                            "reconnect": 1,
                            "watermark": 1,
                        },
                        "actions": [
                            {
                                "action": "inspect_worker",
                                "reason": "heartbeat_stale",
                                "severity": "review",
                                "description": "Inspect worker heartbeat.",
                            },
                            {
                                "action": "inspect_watermark",
                                "reason": "watermark_stale",
                                "severity": "review",
                                "description": "Inspect event watermark.",
                            },
                            {
                                "action": "inspect_reconnect",
                                "reason": "reconnect_stale",
                                "severity": "review",
                                "description": "Inspect reconnect duration.",
                            },
                            {
                                "action": "inspect_process",
                                "reason": "overall_status:degraded",
                                "severity": "review",
                                "description": "Inspect long-run process health.",
                            },
                        ],
                        "action_summary": {
                            "count": 4,
                            "primary_action": "inspect_worker",
                            "actions": ["inspect_worker"],
                        },
                        "evaluation_summary": {
                            "evaluated_components": ["heartbeat", "watermark"],
                            "stale_components": ["heartbeat"],
                            "not_evaluated_components": ["reconnect"],
                            "evaluated_count": 2,
                            "stale_count": 1,
                            "not_evaluated_count": 1,
                        },
                    },
                },
            }
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config, controller=controller)
            try:
                payload = self._request(
                    f"{base_url}/bridge/v1/watch/status?view=summary&heartbeat_stale_after_seconds=60&reconnect_stale_after_seconds=180",
                    token="secret-token",
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["result"]["mode"], "summary")
        self.assertEqual(payload["result"]["worker"], "worker-a")
        self.assertEqual(payload["result"]["status"], "degraded")
        self.assertEqual(
            payload["result"]["runtime"],
            {
                "control_state": "running",
                "active": True,
                "watch_state": "running",
                "run_id": "run-001",
                "pid": 1234,
            },
        )
        self.assertEqual(payload["result"]["status_summary"]["heartbeat"]["status"], "stale")
        self.assertEqual(payload["result"]["status_summary"]["watermark"]["status"], "fresh")
        self.assertEqual(payload["result"]["status_summary"]["reconnect"]["reconnect_count"], 2)
        self.assertEqual(payload["result"]["governance"]["decision"], "manual_review")
        self.assertEqual(payload["result"]["governance"]["requires_manual_review"], True)
        self.assertEqual(payload["result"]["governance"]["staleness_evaluated"], True)
        self.assertEqual(
            payload["result"]["governance"]["boundary"],
            "advisory_only; does_not_trigger_reconnect_backoff_restart_or_lifecycle_changes",
        )
        self.assertEqual(payload["result"]["governance"]["reason_count"], 4)
        self.assertEqual(
            payload["result"]["governance"]["reason_source_counts"],
            {"heartbeat": 1, "overall_status": 1, "reconnect": 1, "watermark": 1},
        )
        self.assertEqual(
            payload["result"]["governance"]["reason_samples"],
            ["heartbeat:stale", "overall_status:degraded", "watermark:stale"],
        )
        self.assertEqual(payload["result"]["governance"]["reason_sample_limit"], 3)
        self.assertEqual(payload["result"]["governance"]["reason_sample_truncated"], True)
        self.assertEqual(payload["result"]["governance"]["action_summary"]["primary_action"], "inspect_worker")
        self.assertEqual(
            payload["result"]["governance"]["action_samples"],
            [
                {"action": "inspect_worker", "reason": "heartbeat_stale", "severity": "review"},
                {"action": "inspect_watermark", "reason": "watermark_stale", "severity": "review"},
                {"action": "inspect_reconnect", "reason": "reconnect_stale", "severity": "review"},
            ],
        )
        self.assertEqual(payload["result"]["governance"]["action_sample_limit"], 3)
        self.assertEqual(payload["result"]["governance"]["action_sample_truncated"], True)
        self.assertEqual(
            payload["result"]["governance"]["evaluation_summary"],
            {
                "evaluated_components": ["heartbeat", "watermark"],
                "stale_components": ["heartbeat"],
                "not_evaluated_components": ["reconnect"],
                "evaluated_count": 2,
                "stale_count": 1,
                "not_evaluated_count": 1,
            },
        )
        self.assertNotIn("reasons", payload["result"]["governance"])
        self.assertNotIn("actions", payload["result"]["governance"])
        self.assertNotIn("control", payload["result"])
        self.assertNotIn("watch_status", payload["result"])
        self.assertEqual(
            controller.status_calls,
            [
                {
                    "heartbeat_stale_after_seconds": 60.0,
                    "watermark_stale_after_seconds": None,
                    "reconnect_stale_after_seconds": 180.0,
                }
            ],
        )

    def test_watch_status_summary_view_rejects_unknown_view(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config, controller=controller)
            try:
                with self.assertRaises(HTTPError) as ctx:
                    self._request(f"{base_url}/bridge/v1/watch/status?view=compact", token="secret-token")
                payload = json.loads(ctx.exception.read().decode("utf-8"))
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(ctx.exception.code, 400)
        self.assertEqual(payload["error"]["code"], "INVALID_REQUEST")
        self.assertEqual(payload["error"]["message"], "query parameter view must be one of: detailed, summary")
        self.assertEqual(controller.status_calls, [])

    def test_watch_event_stream_projects_status_and_event_rows_as_sse(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            controller.status_result = {
                "control": {"state": "reconnecting", "active": True, "run_id": "run-001", "pid": 1234},
                "watch_status": {
                    "run_id": "run-001",
                    "state": "reconnecting",
                    "reconnect_count": 1,
                    "last_disconnect_at": "2026-05-14T01:00:00+00:00",
                    "last_reconnect_at": None,
                    "next_reconnect_at": "2026-05-14T01:00:05+00:00",
                    "degraded_since": None,
                    "last_error": {"code": "SESSION_LOST", "message": "session lost"},
                },
            }
            controller.events_result = {
                "run_id": "run-001",
                "events": [
                    {
                        "schema_version": "subscription.event.v1",
                        "capability": "subscription.watch",
                        "run_id": "run-001",
                        "sequence": 7,
                        "event_type": "quote_update",
                        "symbol": "000001.SZ",
                        "reconnect_metadata": {"reconnect_count": 1},
                        "payload": {"Now": 10.01},
                    }
                ],
            }
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config, controller=controller)
            try:
                content_type, raw = self._request_text(
                    f"{base_url}/bridge/v1/watch/events/stream?run_id=run-001&follow=false",
                    token="secret-token",
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(content_type, "text/event-stream")
        payloads = self._parse_sse_payloads(raw)
        self.assertEqual(payloads[0]["frame_type"], "status")
        self.assertEqual(payloads[0]["reconnect"]["reconnect_count"], 1)
        self.assertEqual(payloads[1]["frame_type"], "quote")
        self.assertEqual(payloads[1]["event"]["sequence"], 7)
        self.assertEqual(payloads[1]["event"]["reconnect_metadata"]["reconnect_count"], 1)

    def test_watch_status_preserves_degraded_runtime_fields(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            live_result = {
                "control": {
                    "state": "degraded",
                    "active": True,
                    "run_id": "run-001",
                    "pid": 1234,
                    "reason": None,
                },
                "watch_status": {
                    "run_id": "run-001",
                    "state": "degraded",
                    "heartbeat_at": "2026-05-03T09:00:05+00:00",
                    "last_event_ts": "2026-05-03T09:00:02+00:00",
                    "degraded_since": "2026-05-03T09:00:03+00:00",
                    "last_disconnect_at": "2026-05-03T09:00:03+00:00",
                    "next_reconnect_at": "2026-05-03T09:00:08+00:00",
                    "last_error": {"code": "RECONNECT_BACKOFF", "message": "retrying"},
                },
            }
            historical_result = {
                "control": dict(live_result["control"]),
                "watch_status": {
                    "run_id": "run-001",
                    "state": "running",
                    "event_count": 3,
                },
            }
            controller.status_handler = lambda **kwargs: historical_result if kwargs.get("run_id") else live_result
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config, controller=controller)
            try:
                payload = self._request(f"{base_url}/bridge/v1/watch/status", token="secret-token")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["result"]["watch_status"]["state"], "degraded")
        self.assertEqual(payload["result"]["watch_status"]["degraded_since"], "2026-05-03T09:00:03+00:00")
        self.assertEqual(payload["result"]["watch_status"]["last_error"]["code"], "RECONNECT_BACKOFF")

    def test_watch_status_surfaces_stale_process_failure_projection(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            stale_result = {
                "control": {
                    "state": "failed",
                    "active": False,
                    "run_id": "run-001",
                    "pid": None,
                    "reason": "stale_process_state",
                },
                "watch_status": None,
            }
            status_reads = 0

            def status_handler(**kwargs: object) -> dict[str, object]:
                nonlocal status_reads
                status_reads += 1
                if status_reads == 1:
                    return stale_result
                return {
                    "control": {
                        "state": "running",
                        "active": True,
                        "run_id": "run-001",
                        "pid": 1234,
                        "reason": None,
                    },
                    "watch_status": {
                        "run_id": "run-001",
                        "state": "running",
                        "event_count": 99,
                    },
                }

            controller.status_handler = status_handler
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config, controller=controller)
            try:
                payload = self._request(f"{base_url}/bridge/v1/watch/status", token="secret-token")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["result"]["control"]["state"], "failed")
        self.assertFalse(payload["result"]["control"]["active"])
        self.assertEqual(payload["result"]["control"]["reason"], "stale_process_state")
        self.assertIsNone(payload["result"]["watch_status"])

    def test_watch_status_rejects_missing_or_invalid_token_before_controller_read(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config, controller=controller)
            try:
                with self.assertRaises(HTTPError) as missing_ctx:
                    self._request(f"{base_url}/bridge/v1/watch/status")
                missing_payload = json.loads(missing_ctx.exception.read().decode("utf-8"))
                self.assertEqual(missing_ctx.exception.code, 401)
                self.assertEqual(missing_payload["error"]["code"], "UNAUTHORIZED")

                with self.assertRaises(HTTPError) as invalid_ctx:
                    self._request(f"{base_url}/bridge/v1/watch/status", token="wrong-token")
                invalid_payload = json.loads(invalid_ctx.exception.read().decode("utf-8"))
                self.assertEqual(invalid_ctx.exception.code, 401)
                self.assertEqual(invalid_payload["error"]["code"], "UNAUTHORIZED")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(controller.status_calls, [])

    def test_health_uses_reconciled_stale_background_state(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            (root_dir / "active.json").write_text(
                json.dumps({"state": "running", "active": True, "run_id": "run-001", "pid": 1234, "reason": None}),
                encoding="utf-8",
            )
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                payload = self._request(f"{base_url}/bridge/v1/health", token="secret-token")
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["control"]["state"], "failed")
                self.assertFalse(payload["result"]["control"]["active"])
                self.assertEqual(payload["result"]["control"]["reason"], "stale_process_state")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_health_ignores_malformed_status_json_when_control_state_is_valid(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            run_dir = root_dir / "run-001"
            run_dir.mkdir(parents=True)
            pid = os.getpid()
            (root_dir / "active.json").write_text(
                json.dumps({"state": "running", "active": True, "run_id": "run-001", "pid": pid, "reason": None}),
                encoding="utf-8",
            )
            (root_dir / "pid").write_text(f"{pid}\n", encoding="utf-8")
            (run_dir / "status.json").write_text("{invalid json", encoding="utf-8")
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                payload = self._request(f"{base_url}/bridge/v1/health", token="secret-token")
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["control"]["state"], "running")
                self.assertEqual(payload["result"]["control"]["run_id"], "run-001")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_status_uses_reconciled_stale_background_state(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            (root_dir / "active.json").write_text(
                json.dumps({"state": "running", "active": True, "run_id": "run-001", "pid": 1234, "reason": None}),
                encoding="utf-8",
            )
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                payload = self._request(f"{base_url}/bridge/v1/watch/status", token="secret-token")
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["control"]["state"], "failed")
                self.assertFalse(payload["result"]["control"]["active"])
                self.assertIsNone(payload["result"]["watch_status"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_status_uses_reconciled_stale_reconnecting_background_state(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            (root_dir / "active.json").write_text(
                json.dumps({"state": "reconnecting", "active": True, "run_id": "run-001", "pid": 1234, "reason": None}),
                encoding="utf-8",
            )
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                payload = self._request(f"{base_url}/bridge/v1/watch/status", token="secret-token")
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["control"]["state"], "failed")
                self.assertFalse(payload["result"]["control"]["active"])
                self.assertEqual(payload["result"]["control"]["reason"], "stale_process_state")
                self.assertIsNone(payload["result"]["watch_status"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_status_does_not_fall_back_to_historical_status_without_explicit_run_id(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            run_dir = root_dir / "run-001"
            run_dir.mkdir(parents=True)
            (root_dir / "active.json").write_text(
                json.dumps({"state": "completed", "active": False, "run_id": "run-001", "pid": None, "reason": "completed"}),
                encoding="utf-8",
            )
            (run_dir / "status.json").write_text(
                json.dumps({"run_id": "run-001", "state": "completed", "event_count": 3}),
                encoding="utf-8",
            )
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                payload = self._request(f"{base_url}/bridge/v1/watch/status", token="secret-token")
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["control"]["run_id"], "run-001")
                self.assertFalse(payload["result"]["control"]["active"])
                self.assertIsNone(payload["result"]["watch_status"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_status_ignores_explicit_run_id_and_returns_controller_status_verbatim(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            run_dir = root_dir / "run-001"
            run_dir.mkdir(parents=True)
            (root_dir / "active.json").write_text(
                json.dumps({"state": "completed", "active": False, "run_id": "run-001", "pid": None, "reason": "completed"}),
                encoding="utf-8",
            )
            (run_dir / "status.json").write_text(
                json.dumps({"run_id": "run-001", "state": "completed", "event_count": 3}),
                encoding="utf-8",
            )
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                payload = self._request(f"{base_url}/bridge/v1/watch/status?run_id=run-001", token="secret-token")
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["control"]["run_id"], "run-001")
                self.assertFalse(payload["result"]["control"]["active"])
                self.assertIsNone(payload["result"]["watch_status"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_list_returns_only_active_last_completed_and_last_failed(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            active_run = root_dir / "run-003"
            completed_run = root_dir / "run-002"
            failed_run = root_dir / "run-001"
            active_run.mkdir(parents=True)
            completed_run.mkdir(parents=True)
            failed_run.mkdir(parents=True)
            (root_dir / "active.json").write_text(
                json.dumps({"state": "running", "active": True, "run_id": "run-003", "pid": os.getpid(), "reason": None}),
                encoding="utf-8",
            )
            (root_dir / "pid").write_text(f"{os.getpid()}\n", encoding="utf-8")
            (active_run / "status.json").write_text(
                json.dumps({"run_id": "run-003", "state": "running", "event_count": 5}),
                encoding="utf-8",
            )
            (completed_run / "summary.json").write_text(
                json.dumps({"run_id": "run-002", "final_state": "completed", "event_count": 8}),
                encoding="utf-8",
            )
            (failed_run / "summary.json").write_text(
                json.dumps({"run_id": "run-001", "final_state": "failed", "event_count": 2}),
                encoding="utf-8",
            )
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                payload = self._request(f"{base_url}/bridge/v1/watch/list", token="secret-token")
                self.assertTrue(payload["ok"])
                result = payload["result"]
                self.assertEqual(set(result), {"active", "last_completed", "last_failed"})
                self.assertEqual(result["active"]["run_id"], "run-003")
                self.assertEqual(result["last_completed"]["run_id"], "run-002")
                self.assertEqual(result["last_failed"]["run_id"], "run-001")
                self.assertNotIn("runs", result)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_list_uses_reconciled_stale_background_state(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            completed_run = root_dir / "run-002"
            failed_run = root_dir / "run-001"
            completed_run.mkdir(parents=True)
            failed_run.mkdir(parents=True)
            (root_dir / "active.json").write_text(
                json.dumps({"state": "running", "active": True, "run_id": "run-003", "pid": 1234, "reason": None}),
                encoding="utf-8",
            )
            (completed_run / "summary.json").write_text(
                json.dumps({"run_id": "run-002", "final_state": "completed"}),
                encoding="utf-8",
            )
            (failed_run / "summary.json").write_text(
                json.dumps({"run_id": "run-001", "final_state": "failed"}),
                encoding="utf-8",
            )
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                payload = self._request(f"{base_url}/bridge/v1/watch/list", token="secret-token")
                self.assertTrue(payload["ok"])
                self.assertIsNone(payload["result"]["active"])
                self.assertEqual(payload["result"]["last_completed"]["run_id"], "run-002")
                self.assertEqual(payload["result"]["last_failed"]["run_id"], "run-001")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_events_uses_tail_query_parameter(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            run_dir = root_dir / "run-001"
            run_dir.mkdir(parents=True)
            (run_dir / "events.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps({"sequence": 1, "symbol": "000001"}),
                        json.dumps({"sequence": 2, "symbol": "000002"}),
                        json.dumps({"sequence": 3, "symbol": "000003"}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                payload = self._request(
                    f"{base_url}/bridge/v1/watch/events?run_id=run-001&tail=2",
                    token="secret-token",
                )
                self.assertTrue(payload["ok"])
                self.assertEqual([row["sequence"] for row in payload["result"]["events"]], [2, 3])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_logs_uses_tail_query_parameter(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            run_dir = root_dir / "run-001"
            run_dir.mkdir(parents=True)
            (run_dir / "runner.log").write_text("line-1\nline-2\nline-3\n", encoding="utf-8")
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                payload = self._request(
                    f"{base_url}/bridge/v1/watch/logs?run_id=run-001&tail=2",
                    token="secret-token",
                )
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["lines"], ["line-2", "line-3"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_artifacts_requires_active_run_or_explicit_run_id(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            historical_run = root_dir / "run-001"
            historical_run.mkdir(parents=True)
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                with self.assertRaises(HTTPError) as ctx:
                    self._request(f"{base_url}/bridge/v1/watch/artifacts", token="secret-token")
                payload = json.loads(ctx.exception.read().decode("utf-8"))
                self.assertEqual(ctx.exception.code, 400)
                self.assertEqual(payload["error"]["code"], "INVALID_REQUEST")
                self.assertEqual(payload["error"]["message"], "watch artifacts require an active or explicit run_id")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_artifacts_uses_active_run_id_without_parsing_status_json(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            run_dir = root_dir / "run-001"
            run_dir.mkdir(parents=True)
            pid = os.getpid()
            (root_dir / "active.json").write_text(
                json.dumps({"state": "running", "active": True, "run_id": "run-001", "pid": pid, "reason": None}),
                encoding="utf-8",
            )
            (root_dir / "pid").write_text(f"{pid}\n", encoding="utf-8")
            (run_dir / "status.json").write_text("{invalid json", encoding="utf-8")
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                payload = self._request(f"{base_url}/bridge/v1/watch/artifacts", token="secret-token")
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["run_id"], "run-001")
                self.assertTrue(payload["result"]["artifacts"]["status_path"].endswith("run-001/status.json"))
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_events_requires_active_run_or_explicit_run_id(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            historical_run = root_dir / "run-001"
            historical_run.mkdir(parents=True)
            (historical_run / "events.jsonl").write_text(json.dumps({"sequence": 1}) + "\n", encoding="utf-8")
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                with self.assertRaises(HTTPError) as ctx:
                    self._request(f"{base_url}/bridge/v1/watch/events", token="secret-token")
                payload = json.loads(ctx.exception.read().decode("utf-8"))
                self.assertEqual(ctx.exception.code, 400)
                self.assertEqual(payload["error"]["message"], "watch events require an active or explicit run_id")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_events_uses_active_run_id_without_parsing_status_json(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            run_dir = root_dir / "run-001"
            run_dir.mkdir(parents=True)
            pid = os.getpid()
            (root_dir / "active.json").write_text(
                json.dumps({"state": "running", "active": True, "run_id": "run-001", "pid": pid, "reason": None}),
                encoding="utf-8",
            )
            (root_dir / "pid").write_text(f"{pid}\n", encoding="utf-8")
            (run_dir / "status.json").write_text("{invalid json", encoding="utf-8")
            (run_dir / "events.jsonl").write_text(json.dumps({"sequence": 1}) + "\n", encoding="utf-8")
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                payload = self._request(f"{base_url}/bridge/v1/watch/events", token="secret-token")
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["run_id"], "run-001")
                self.assertEqual(payload["result"]["events"][0]["sequence"], 1)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_logs_requires_active_run_or_explicit_run_id(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            historical_run = root_dir / "run-001"
            historical_run.mkdir(parents=True)
            (historical_run / "runner.log").write_text("line-1\n", encoding="utf-8")
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                with self.assertRaises(HTTPError) as ctx:
                    self._request(f"{base_url}/bridge/v1/watch/logs", token="secret-token")
                payload = json.loads(ctx.exception.read().decode("utf-8"))
                self.assertEqual(ctx.exception.code, 400)
                self.assertEqual(payload["error"]["message"], "watch logs require an active or explicit run_id")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_logs_uses_active_run_id_without_parsing_status_json(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            run_dir = root_dir / "run-001"
            run_dir.mkdir(parents=True)
            pid = os.getpid()
            (root_dir / "active.json").write_text(
                json.dumps({"state": "running", "active": True, "run_id": "run-001", "pid": pid, "reason": None}),
                encoding="utf-8",
            )
            (root_dir / "pid").write_text(f"{pid}\n", encoding="utf-8")
            (run_dir / "status.json").write_text("{invalid json", encoding="utf-8")
            (run_dir / "runner.log").write_text("line-1\n", encoding="utf-8")
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config)
            try:
                payload = self._request(f"{base_url}/bridge/v1/watch/logs", token="secret-token")
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["run_id"], "run-001")
                self.assertEqual(payload["result"]["lines"], ["line-1"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_stop_preserves_controller_failure_message_and_details(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            controller.stop_result = {
                "ok": False,
                "error": {
                    "code": "SIGNAL_FAILED",
                    "message": "failed to signal background watch process",
                    "details": {"run_id": "run-001", "pid": 4321},
                },
            }
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config, controller=controller)
            try:
                with self.assertRaises(HTTPError) as ctx:
                    self._request(
                        f"{base_url}/bridge/v1/watch/stop",
                        method="POST",
                        token="secret-token",
                        payload={"reason": "operator_stop"},
                    )
                payload = json.loads(ctx.exception.read().decode("utf-8"))
                self.assertEqual(ctx.exception.code, 500)
                self.assertEqual(payload["error"]["code"], "SIGNAL_FAILED")
                self.assertEqual(payload["error"]["message"], "failed to signal background watch process")
                self.assertEqual(payload["error"]["details"], {"run_id": "run-001", "pid": 4321})
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_start_maps_already_running_to_conflict_failure(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            controller.start_result = {
                "ok": False,
                "error": {
                    "code": "ALREADY_RUNNING",
                    "message": "subscription-watch background run is already active",
                    "details": {"run_id": "run-001"},
                },
            }
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config, controller=controller)
            try:
                with self.assertRaises(HTTPError) as ctx:
                    self._request(
                        f"{base_url}/bridge/v1/watch/start",
                        method="POST",
                        token="secret-token",
                        payload={"stock_list": ["000001.SZ"]},
                    )
                payload = json.loads(ctx.exception.read().decode("utf-8"))
                self.assertEqual(ctx.exception.code, 409)
                self.assertEqual(payload["error"]["code"], "ALREADY_RUNNING")
                self.assertEqual(payload["error"]["message"], "subscription-watch background run is already active")
                self.assertEqual(payload["error"]["details"], {"run_id": "run-001"})
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_start_maps_invalid_request_to_http_400(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            controller.start_result = {
                "ok": False,
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "subscription watch task requires max_events > 0",
                    "details": {},
                },
            }
            config = BridgeConfig(
                worker_id="worker-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
                run_root_dir=temp_dir,
            )
            server, base_url, thread = self._start_server(config, controller=controller)
            try:
                with self.assertRaises(HTTPError) as ctx:
                    self._request(
                        f"{base_url}/bridge/v1/watch/start",
                        method="POST",
                        token="secret-token",
                        payload={"stock_list": ["000001.SZ"], "max_events": 0},
                    )
                payload = json.loads(ctx.exception.read().decode("utf-8"))
                self.assertEqual(ctx.exception.code, 400)
                self.assertEqual(payload["error"]["code"], "INVALID_REQUEST")
                self.assertEqual(payload["error"]["message"], "subscription watch task requires max_events > 0")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)
