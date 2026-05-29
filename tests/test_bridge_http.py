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
        self.restart_calls: list[dict[str, object]] = []
        self.supervisor_tick_calls: list[dict[str, object]] = []
        self.supervisor_run_calls: list[dict[str, object]] = []
        self.supervisor_daemon_start_calls: list[dict[str, object]] = []
        self.supervisor_daemon_stop_calls: list[dict[str, object]] = []
        self.supervisor_daemon_status_calls = 0
        self.restart_preflight_calls = 0
        self.status_calls: list[dict[str, object]] = []
        self.control_status_calls = 0
        self.status_handler = None
        self.list_calls = 0
        self.artifact_calls: list[dict[str, object]] = []
        self.event_calls: list[dict[str, object]] = []
        self.log_calls: list[dict[str, object]] = []
        self.start_result: dict[str, object] = {"ok": True, "result": {"run_id": "run-001", "state": "starting"}}
        self.stop_result: dict[str, object] = {"ok": True, "result": {"run_id": "run-001", "state": "stopped"}}
        self.restart_result: dict[str, object] = {
            "ok": True,
            "result": {
                "status": "restarted",
                "previous_run_id": "run-001",
                "new_run_id": "run-002",
            },
        }
        self.restart_preflight_result: dict[str, object] = {
            "ok": True,
            "result": {
                "schema_version": "tdx.subscription_watch.restart_preflight.v1",
                "ready": True,
                "decision": "ready",
                "reason_codes": [],
            },
        }
        self.supervisor_tick_result: dict[str, object] = {
            "ok": True,
            "result": {
                "schema_version": "tdx.subscription_watch.supervisor_tick.v1",
                "status": "noop",
                "decision": "no_action",
            },
        }
        self.supervisor_run_result: dict[str, object] = {
            "ok": True,
            "result": {
                "schema_version": "tdx.subscription_watch.supervisor_run.v1",
                "status": "waiting",
                "tick_count": 3,
            },
        }
        self.supervisor_daemon_status_result: dict[str, object] = {
            "ok": True,
            "result": {
                "schema_version": "tdx.subscription_watch.supervisor_daemon.v1",
                "state": "running",
                "pid": 1234,
            },
        }
        self.supervisor_daemon_start_result: dict[str, object] = {
            "ok": True,
            "result": {
                "schema_version": "tdx.subscription_watch.supervisor_daemon.v1",
                "state": "starting",
                "pid": 1234,
            },
        }
        self.supervisor_daemon_stop_result: dict[str, object] = {
            "ok": True,
            "result": {
                "schema_version": "tdx.subscription_watch.supervisor_daemon.v1",
                "state": "stopping",
                "pid": 1234,
            },
        }
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

    def restart(self, **kwargs: object) -> dict[str, object]:
        self.restart_calls.append(dict(kwargs))
        return dict(self.restart_result)

    def restart_preflight(self) -> dict[str, object]:
        self.restart_preflight_calls += 1
        return dict(self.restart_preflight_result)

    def supervisor_tick(self, **kwargs: object) -> dict[str, object]:
        self.supervisor_tick_calls.append(dict(kwargs))
        return dict(self.supervisor_tick_result)

    def supervisor_run(self, **kwargs: object) -> dict[str, object]:
        self.supervisor_run_calls.append(dict(kwargs))
        return dict(self.supervisor_run_result)

    def supervisor_daemon_status(self) -> dict[str, object]:
        self.supervisor_daemon_status_calls += 1
        return dict(self.supervisor_daemon_status_result)

    def start_supervisor_daemon(self, **kwargs: object) -> dict[str, object]:
        self.supervisor_daemon_start_calls.append(dict(kwargs))
        return dict(self.supervisor_daemon_start_result)

    def stop_supervisor_daemon(self, **kwargs: object) -> dict[str, object]:
        self.supervisor_daemon_stop_calls.append(dict(kwargs))
        return dict(self.supervisor_daemon_stop_result)

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

    def test_watch_restart_dispatches_to_controller(self) -> None:
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
                    f"{base_url}/bridge/v1/watch/restart",
                    method="POST",
                    token="secret-token",
                    payload={"reason": "operator_restart", "grace_period_seconds": 2},
                )
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["status"], "restarted")
                self.assertEqual(payload["result"]["previous_run_id"], "run-001")
                self.assertEqual(payload["result"]["new_run_id"], "run-002")
                self.assertEqual(
                    controller.restart_calls[0],
                    {"reason": "operator_restart", "grace_period_seconds": 2},
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_restart_preflight_dispatches_to_controller(self) -> None:
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
                    f"{base_url}/bridge/v1/watch/restart-preflight",
                    token="secret-token",
                )
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["schema_version"], "tdx.subscription_watch.restart_preflight.v1")
                self.assertTrue(payload["result"]["ready"])
                self.assertEqual(controller.restart_preflight_calls, 1)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_supervisor_tick_dispatches_to_controller(self) -> None:
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
                    f"{base_url}/bridge/v1/watch/supervisor-tick",
                    method="POST",
                    token="secret-token",
                    payload={"reason": "manual_tick"},
                )
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["schema_version"], "tdx.subscription_watch.supervisor_tick.v1")
                self.assertEqual(controller.supervisor_tick_calls, [{"reason": "manual_tick"}])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_supervisor_run_dispatches_to_controller(self) -> None:
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
                    f"{base_url}/bridge/v1/watch/supervisor-run",
                    method="POST",
                    token="secret-token",
                    payload={"max_ticks": 3, "interval_seconds": 0.25, "reason": "manual_supervise"},
                )
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["schema_version"], "tdx.subscription_watch.supervisor_run.v1")
                self.assertEqual(
                    controller.supervisor_run_calls,
                    [{"max_ticks": 3, "interval_seconds": 0.25, "reason": "manual_supervise"}],
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_supervisor_daemon_status_dispatches_to_controller(self) -> None:
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
                    f"{base_url}/bridge/v1/watch/supervisor-daemon/status",
                    token="secret-token",
                )
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["schema_version"], "tdx.subscription_watch.supervisor_daemon.v1")
                self.assertEqual(controller.supervisor_daemon_status_calls, 1)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_supervisor_daemon_start_dispatches_to_controller(self) -> None:
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
                    f"{base_url}/bridge/v1/watch/supervisor-daemon/start",
                    method="POST",
                    token="secret-token",
                    payload={
                        "max_ticks": 3,
                        "interval_seconds": 0.25,
                        "loop_sleep_seconds": 1.5,
                        "reason": "manual_daemon_start",
                        "owner_token": "owner-1",
                    },
                )
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["schema_version"], "tdx.subscription_watch.supervisor_daemon.v1")
                self.assertEqual(
                    controller.supervisor_daemon_start_calls,
                    [
                        {
                            "max_ticks": 3,
                            "interval_seconds": 0.25,
                            "loop_sleep_seconds": 1.5,
                            "reason": "manual_daemon_start",
                            "owner_token": "owner-1",
                        }
                    ],
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_watch_supervisor_daemon_stop_dispatches_to_controller(self) -> None:
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
                    f"{base_url}/bridge/v1/watch/supervisor-daemon/stop",
                    method="POST",
                    token="secret-token",
                    payload={"owner_token": "owner-1", "reason": "manual_daemon_stop"},
                )
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["result"]["schema_version"], "tdx.subscription_watch.supervisor_daemon.v1")
                self.assertEqual(
                    controller.supervisor_daemon_stop_calls,
                    [{"owner_token": "owner-1", "reason": "manual_daemon_stop"}],
                )
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
                "control": {
                    "state": "running",
                    "active": True,
                    "run_id": "run-001",
                    "pid": 1234,
                    "start_request": {
                        "stock_list": ["600519.SH", "000001.SZ"],
                        "max_events": 10,
                        "max_seconds": 30.0,
                        "poll_interval": 0.5,
                    },
                },
                "watch_status": {"state": "running", "run_id": "run-001", "event_count": 3},
                "status_summary": {
                    "schema_version": "tdx.subscription_watch.status_summary.v1",
                    "overall_status": "degraded",
                    "boundary": "summary_projection_only; optional heartbeat/watermark/reconnect staleness evaluation only; does not change reconnect/backoff behavior",
                    "control_rollup": {
                        "control_state": "running",
                        "control_active": True,
                        "has_control_run_id": True,
                        "has_control_pid": True,
                        "control_reason": None,
                        "has_control_reason": False,
                        "stale_process_state": False,
                        "startup_persistence_failed": False,
                    },
                    "consistency_rollup": {
                        "control_state": "running",
                        "watch_state": "running",
                        "has_watch_status": True,
                        "has_control_run_id": True,
                        "has_watch_run_id": True,
                        "run_id_match": True,
                        "state_match": True,
                        "has_control_pid": True,
                        "has_mismatch": False,
                    },
                    "statefile_ownership": {
                        "schema_version": "tdx.subscription_watch.statefile_ownership.v1",
                        "status": "owned_active",
                        "reason_codes": ["OWNED_ACTIVE"],
                        "statefile_exists": True,
                        "pidfile_exists": True,
                        "lockfile_exists": True,
                        "active": True,
                        "control_state": "running",
                        "payload_pid": 1234,
                        "owned_pid": 1234,
                        "pid_matches_owned_state": True,
                        "process_alive": True,
                        "boundary": "local_statefile_pidfile_only;does_not_claim_provider_readiness_or_lifecycle_control",
                    },
                    "supervisor_daemon": {
                        "schema_version": "tdx.subscription_watch.supervisor_daemon.v1",
                        "daemon_status": "running",
                        "state": "running",
                        "statefile_exists": True,
                        "statefile_valid": True,
                        "pidfile_exists": True,
                        "pid": 5678,
                        "process_running": True,
                        "has_owner_token": True,
                        "generation": 2,
                        "control_allowed": True,
                        "boundary": "read_only_supervisor_daemon_status;does_not_execute_lifecycle",
                    },
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
                        "reason_source_key_count": 4,
                        "reason_summary": {
                            "count": 4,
                            "primary_reason": "heartbeat:stale",
                            "primary_source": "heartbeat",
                            "primary_reason_source": "heartbeat",
                            "source_counts": {
                                "heartbeat": 1,
                                "overall_status": 1,
                                "reconnect": 1,
                                "watermark": 1,
                            },
                            "source_key_count": 4,
                            "reason_code_counts": {
                                "heartbeat:stale": 1,
                                "overall_status:degraded": 1,
                                "reconnect:stale": 1,
                                "watermark:stale": 1,
                            },
                            "reason_code_key_count": 4,
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
                            "primary_reason": "heartbeat_stale",
                            "primary_reason_source": "unknown",
                            "primary_severity": "review",
                            "actions": ["inspect_worker"],
                            "severity_key_count": 1,
                            "action_name_counts": {
                                "inspect_process": 1,
                                "inspect_reconnect": 1,
                                "inspect_watermark": 1,
                                "inspect_worker": 1,
                            },
                            "action_name_key_count": 4,
                            "reason_source_counts": {"overall_status": 1, "unknown": 3},
                            "reason_source_key_count": 2,
                            "reason_code_counts": {
                                "heartbeat_stale": 1,
                                "overall_status:degraded": 1,
                                "reconnect_stale": 1,
                                "watermark_stale": 1,
                            },
                            "reason_code_key_count": 4,
                        },
                        "reconnect_rollup": {
                            "staleness": "stale",
                            "reconnect_count": 2,
                            "consecutive_reconnect_failures": 1,
                            "has_reconnects": True,
                            "has_reconnect_failures": True,
                            "has_last_error": True,
                            "has_next_reconnect_at": True,
                            "age_source": "last_disconnect_at",
                            "stale_after_seconds": 60.0,
                        },
                        "evaluation_summary": {
                            "evaluated_components": ["heartbeat", "watermark"],
                            "primary_evaluated_component": "heartbeat",
                            "stale_components": ["heartbeat"],
                            "primary_stale_component": "heartbeat",
                            "has_stale_component": True,
                            "primary_fresh_component": "watermark",
                            "has_fresh_component": True,
                            "not_evaluated_components": ["reconnect"],
                            "primary_not_evaluated_component": "reconnect",
                            "has_not_evaluated_component": True,
                            "all_components_evaluated": False,
                            "evaluated_count": 2,
                            "stale_count": 1,
                            "fresh_count": 1,
                            "not_evaluated_count": 1,
                            "component_status_counts": {"fresh": 1, "not_evaluated": 1, "stale": 1},
                            "component_status_key_count": 3,
                            "evaluated_status_counts": {"fresh": 1, "stale": 1},
                            "evaluated_status_key_count": 2,
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
                "state_match": True,
                "run_id": "run-001",
                "run_id_source": "watch_status",
                "run_id_match": True,
                "pid": 1234,
                "pid_source": "control",
                "identity_summary": {
                    "control_state": "running",
                    "watch_state": "running",
                    "state_match": True,
                    "has_run_id": True,
                    "run_id_source": "watch_status",
                    "run_id_match": True,
                    "has_pid": True,
                    "pid_source": "control",
                },
            },
        )
        self.assertEqual(
            payload["result"]["status_summary"]["schema_version"],
            "tdx.subscription_watch.status_summary.v1",
        )
        self.assertEqual(
            payload["result"]["status_summary"]["boundary"],
            "summary_projection_only; optional heartbeat/watermark/reconnect staleness evaluation only; does not change reconnect/backoff behavior",
        )
        self.assertEqual(
            payload["result"]["status_summary"]["control_rollup"],
            {
                "control_state": "running",
                "control_active": True,
                "has_control_run_id": True,
                "has_control_pid": True,
                "control_reason": None,
                "has_control_reason": False,
                "stale_process_state": False,
                "startup_persistence_failed": False,
            },
        )
        self.assertEqual(
            payload["result"]["status_summary"]["consistency_rollup"],
            {
                "control_state": "running",
                "watch_state": "running",
                "has_watch_status": True,
                "has_control_run_id": True,
                "has_watch_run_id": True,
                "run_id_match": True,
                "state_match": True,
                "has_control_pid": True,
                "has_mismatch": False,
            },
        )
        self.assertEqual(payload["result"]["status_summary"]["heartbeat"]["status"], "stale")
        self.assertEqual(payload["result"]["status_summary"]["watermark"]["status"], "fresh")
        self.assertEqual(payload["result"]["status_summary"]["reconnect"]["reconnect_count"], 2)
        self.assertEqual(payload["result"]["status_summary"]["statefile_ownership"]["status"], "owned_active")
        self.assertEqual(
            payload["result"]["status_summary"]["statefile_ownership"]["boundary"],
            "local_statefile_pidfile_only;does_not_claim_provider_readiness_or_lifecycle_control",
        )
        self.assertEqual(payload["result"]["status_summary"]["supervisor_daemon"]["daemon_status"], "running")
        self.assertEqual(
            payload["result"]["status_summary"]["supervisor_daemon"]["boundary"],
            "read_only_supervisor_daemon_status;does_not_execute_lifecycle",
        )
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
        self.assertEqual(payload["result"]["governance"]["reason_source_key_count"], 4)
        self.assertEqual(
            payload["result"]["governance"]["reason_summary"],
            {
                "count": 4,
                "primary_reason": "heartbeat:stale",
                "primary_source": "heartbeat",
                "primary_reason_source": "heartbeat",
                "source_counts": {"heartbeat": 1, "overall_status": 1, "reconnect": 1, "watermark": 1},
                "source_key_count": 4,
                "reason_code_counts": {
                    "heartbeat:stale": 1,
                    "overall_status:degraded": 1,
                    "reconnect:stale": 1,
                    "watermark:stale": 1,
                },
                "reason_code_key_count": 4,
            },
        )
        self.assertEqual(
            payload["result"]["governance"]["reason_samples"],
            ["heartbeat:stale", "overall_status:degraded", "watermark:stale"],
        )
        self.assertEqual(payload["result"]["governance"]["reason_sample_count"], 3)
        self.assertEqual(payload["result"]["governance"]["reason_sample_hidden_count"], 1)
        self.assertEqual(payload["result"]["governance"]["reason_sample_limit"], 3)
        self.assertEqual(payload["result"]["governance"]["reason_sample_truncated"], True)
        self.assertEqual(payload["result"]["governance"]["action_count"], 4)
        self.assertEqual(payload["result"]["governance"]["action_summary"]["primary_action"], "inspect_worker")
        self.assertEqual(payload["result"]["governance"]["action_summary"]["primary_reason"], "heartbeat_stale")
        self.assertEqual(payload["result"]["governance"]["action_summary"]["primary_reason_source"], "unknown")
        self.assertEqual(payload["result"]["governance"]["action_summary"]["primary_severity"], "review")
        self.assertEqual(payload["result"]["governance"]["action_summary"]["severity_key_count"], 1)
        self.assertEqual(
            payload["result"]["governance"]["action_summary"]["action_name_counts"],
            {
                "inspect_process": 1,
                "inspect_reconnect": 1,
                "inspect_watermark": 1,
                "inspect_worker": 1,
            },
        )
        self.assertEqual(payload["result"]["governance"]["action_summary"]["action_name_key_count"], 4)
        self.assertEqual(
            payload["result"]["governance"]["action_summary"]["reason_source_counts"],
            {"overall_status": 1, "unknown": 3},
        )
        self.assertEqual(payload["result"]["governance"]["action_summary"]["reason_source_key_count"], 2)
        self.assertEqual(
            payload["result"]["governance"]["action_summary"]["reason_code_counts"],
            {
                "heartbeat_stale": 1,
                "overall_status:degraded": 1,
                "reconnect_stale": 1,
                "watermark_stale": 1,
            },
        )
        self.assertEqual(payload["result"]["governance"]["action_summary"]["reason_code_key_count"], 4)
        self.assertEqual(
            payload["result"]["governance"]["reconnect_rollup"],
            {
                "staleness": "stale",
                "reconnect_count": 2,
                "consecutive_reconnect_failures": 1,
                "has_reconnects": True,
                "has_reconnect_failures": True,
                "has_last_error": True,
                "has_next_reconnect_at": True,
                "age_source": "last_disconnect_at",
                "stale_after_seconds": 60.0,
            },
        )
        self.assertEqual(
            payload["result"]["governance"]["decision_summary"],
            {
                "decision": "manual_review",
                "requires_manual_review": True,
                "staleness_evaluated": True,
                "reason_count": 4,
                "action_count": 4,
                "reason_source_key_count": 4,
                "reason_code_key_count": 4,
                "primary_reason": "heartbeat:stale",
                "primary_reason_source": "heartbeat",
                "primary_severity": "review",
                "primary_action": "inspect_worker",
                "primary_action_reason": "heartbeat_stale",
                "primary_action_reason_source": "unknown",
                "has_reasons": True,
                "has_actions": True,
            },
        )
        self.assertEqual(
            payload["result"]["governance"]["evaluation_rollup"],
            {
                "staleness_evaluated": True,
                "evaluated_count": 2,
                "stale_count": 1,
                "fresh_count": 1,
                "not_evaluated_count": 1,
                "primary_evaluated_component": "heartbeat",
                "primary_stale_component": "heartbeat",
                "primary_fresh_component": "watermark",
                "primary_not_evaluated_component": "reconnect",
                "has_evaluated_component": True,
                "has_stale_component": True,
                "has_fresh_component": True,
                "has_not_evaluated_component": True,
                "all_components_evaluated": False,
                "component_status_key_count": 3,
                "evaluated_status_key_count": 2,
            },
        )
        self.assertEqual(
            payload["result"]["governance"]["action_samples"],
            [
                {"action": "inspect_worker", "reason": "heartbeat_stale", "severity": "review"},
                {"action": "inspect_watermark", "reason": "watermark_stale", "severity": "review"},
                {"action": "inspect_reconnect", "reason": "reconnect_stale", "severity": "review"},
            ],
        )
        self.assertEqual(payload["result"]["governance"]["action_sample_count"], 3)
        self.assertEqual(payload["result"]["governance"]["action_sample_hidden_count"], 1)
        self.assertEqual(payload["result"]["governance"]["action_sample_limit"], 3)
        self.assertEqual(payload["result"]["governance"]["action_sample_truncated"], True)
        self.assertEqual(
            payload["result"]["governance"]["sample_summary"],
            {
                "reason_count": 4,
                "reason_sample_count": 3,
                "reason_sample_hidden_count": 1,
                "reason_sample_limit": 3,
                "reason_sample_truncated": True,
                "action_count": 4,
                "action_sample_count": 3,
                "action_sample_hidden_count": 1,
                "action_sample_limit": 3,
                "action_sample_truncated": True,
            },
        )
        self.assertEqual(
            payload["result"]["governance"]["evaluation_summary"],
            {
                "evaluated_components": ["heartbeat", "watermark"],
                "primary_evaluated_component": "heartbeat",
                "stale_components": ["heartbeat"],
                "primary_stale_component": "heartbeat",
                "has_stale_component": True,
                "primary_fresh_component": "watermark",
                "has_fresh_component": True,
                "not_evaluated_components": ["reconnect"],
                "primary_not_evaluated_component": "reconnect",
                "has_not_evaluated_component": True,
                "all_components_evaluated": False,
                "evaluated_count": 2,
                "stale_count": 1,
                "fresh_count": 1,
                "not_evaluated_count": 1,
                "component_status_counts": {"fresh": 1, "not_evaluated": 1, "stale": 1},
                "component_status_key_count": 3,
                "evaluated_status_counts": {"fresh": 1, "stale": 1},
                "evaluated_status_key_count": 2,
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

    def test_watch_status_diagnostics_view_projects_rollup_flags(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            controller.status_result = {
                "control": {
                    "state": "running",
                    "active": True,
                    "run_id": "run-001",
                    "pid": 1234,
                    "start_request": {
                        "stock_list": ["600519.SH", "000001.SZ"],
                        "max_events": 10,
                        "max_seconds": 30.0,
                        "poll_interval": 0.5,
                    },
                    "last_restart_observation": {
                        "schema_version": "tdx.subscription_watch.restart_observation.v1",
                        "status": "succeeded",
                        "previous_run_id": "run-000",
                        "new_run_id": "run-001",
                        "reason": "operator_restart",
                        "stop_state": "stopped",
                        "start_state": "running",
                        "start_request_summary": {
                            "stock_count": 2,
                            "has_max_events": True,
                            "has_max_seconds": True,
                            "has_poll_interval": True,
                        },
                        "boundary": "observation_only;does_not_schedule_restart_backoff_or_supervisor",
                    },
                    "restart_backoff": {
                        "schema_version": "tdx.subscription_watch.restart_backoff.v1",
                        "status": "active",
                        "reason_codes": ["BACKOFF_ACTIVE"],
                        "previous_run_id": "run-001",
                        "reason": "operator_restart",
                        "created_at": "2026-05-29T00:00:00+00:00",
                        "retry_after_at": "2999-01-01T00:00:00+00:00",
                        "backoff_seconds": 30.0,
                        "start_error_code": "START_FAILED",
                        "start_request_summary": {
                            "stock_count": 2,
                            "has_max_events": True,
                            "has_max_seconds": True,
                            "has_poll_interval": True,
                        },
                        "boundary": "explicit_restart_guard_only;does_not_schedule_restart_or_supervisor",
                    },
                },
                "watch_status": {"state": "degraded", "run_id": "run-002", "event_count": 3},
                "status_summary": {
                    "schema_version": "tdx.subscription_watch.status_summary.v1",
                    "overall_status": "manual_review",
                    "control_rollup": {
                        "control_state": "running",
                        "control_active": True,
                        "has_control_run_id": True,
                        "has_control_pid": True,
                        "control_reason": None,
                        "has_control_reason": False,
                        "stale_process_state": False,
                        "startup_persistence_failed": False,
                    },
                    "consistency_rollup": {
                        "control_state": "running",
                        "watch_state": "degraded",
                        "has_watch_status": True,
                        "has_control_run_id": True,
                        "has_watch_run_id": True,
                        "run_id_match": False,
                        "state_match": False,
                        "has_control_pid": True,
                        "has_mismatch": True,
                    },
                    "governance": {
                        "decision": "manual_review",
                        "requires_manual_review": True,
                        "staleness_evaluated": True,
                        "boundary": "advisory_only; does_not_trigger_reconnect_backoff_restart_or_lifecycle_changes",
                        "reasons": ["watch_status:mismatch", "reconnect:stale"],
                        "actions": [{"action": "inspect_worker", "reason": "watch_status:mismatch"}],
                        "reconnect_rollup": {
                            "staleness": "stale",
                            "reconnect_count": 2,
                            "consecutive_reconnect_failures": 1,
                            "has_reconnects": True,
                            "has_reconnect_failures": True,
                            "has_last_error": True,
                            "has_next_reconnect_at": True,
                            "age_source": "last_disconnect_at",
                            "stale_after_seconds": 60.0,
                        },
                        "evaluation_summary": {
                            "evaluated_components": ["heartbeat", "watermark"],
                            "stale_components": ["heartbeat"],
                            "fresh_components": ["watermark"],
                            "not_evaluated_components": ["reconnect"],
                            "has_stale_component": True,
                            "has_not_evaluated_component": True,
                            "all_components_evaluated": False,
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
                payload = self._request(f"{base_url}/bridge/v1/watch/status?view=diagnostics", token="secret-token")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["result"]["mode"], "diagnostics")
        self.assertEqual(payload["result"]["worker"], "worker-a")
        self.assertEqual(
            payload["result"]["diagnostics"],
            {
                "has_control_rollup": True,
                "has_consistency_rollup": True,
                "has_reconnect_rollup": True,
                "has_evaluation_rollup": True,
                "has_mismatch": True,
                "requires_manual_review": True,
                "staleness_evaluated": True,
                "has_reconnect_failures": True,
                "has_reconnect_last_error": True,
                "has_stale_component": True,
                "has_not_evaluated_component": True,
                "all_components_evaluated": False,
                "restartability": {
                    "ready": False,
                    "decision": "blocked",
                    "reason_codes": ["BACKOFF_ACTIVE"],
                    "has_start_request": True,
                    "start_request_summary": {
                        "stock_count": 2,
                        "has_max_events": True,
                        "has_max_seconds": True,
                        "has_poll_interval": True,
                    },
                    "boundary": "read_only;does_not_stop_start_or_schedule_restart",
                },
                "restart_observation": {
                    "has_observation": True,
                    "status": "succeeded",
                    "previous_run_id": "run-000",
                    "new_run_id": "run-001",
                    "reason": "operator_restart",
                    "stop_state": "stopped",
                    "start_state": "running",
                    "start_request_summary": {
                        "stock_count": 2,
                        "has_max_events": True,
                        "has_max_seconds": True,
                        "has_poll_interval": True,
                    },
                    "boundary": "observation_only;does_not_schedule_restart_backoff_or_supervisor",
                },
                "restart_backoff": {
                    "active": True,
                    "status": "active",
                    "reason_codes": ["BACKOFF_ACTIVE"],
                    "previous_run_id": "run-001",
                    "reason": "operator_restart",
                    "created_at": "2026-05-29T00:00:00+00:00",
                    "retry_after_at": "2999-01-01T00:00:00+00:00",
                    "backoff_seconds": 30.0,
                    "start_error_code": "START_FAILED",
                    "start_request_summary": {
                        "stock_count": 2,
                        "has_max_events": True,
                        "has_max_seconds": True,
                        "has_poll_interval": True,
                    },
                    "boundary": "explicit_restart_guard_only;does_not_schedule_restart_or_supervisor",
                },
                "boundary": "advisory_only; does_not_trigger_reconnect_backoff_restart_or_lifecycle_changes",
            },
        )
        self.assertNotIn("control", payload["result"])
        self.assertNotIn("watch_status", payload["result"])
        self.assertNotIn("reasons", payload["result"]["governance"])
        self.assertNotIn("actions", payload["result"]["governance"])
        self.assertEqual(
            controller.status_calls,
            [
                {
                    "heartbeat_stale_after_seconds": None,
                    "watermark_stale_after_seconds": None,
                    "reconnect_stale_after_seconds": None,
                }
            ],
        )

    def test_watch_status_diagnostics_view_projects_blocked_restartability_reason(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            controller.status_result = {
                "control": {"state": "running", "active": True, "run_id": "run-001", "pid": 1234},
                "watch_status": {"state": "running", "run_id": "run-001"},
                "status_summary": {
                    "schema_version": "tdx.subscription_watch.status_summary.v1",
                    "control_rollup": {"control_state": "running", "control_active": True},
                    "consistency_rollup": {"has_mismatch": False},
                    "governance": {
                        "requires_manual_review": False,
                        "staleness_evaluated": False,
                        "boundary": "advisory_only; does_not_trigger_reconnect_backoff_restart_or_lifecycle_changes",
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
                payload = self._request(f"{base_url}/bridge/v1/watch/status?view=diagnostics", token="secret-token")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(
            payload["result"]["diagnostics"]["restartability"],
            {
                "ready": False,
                "decision": "blocked",
                "reason_codes": ["MISSING_START_REQUEST"],
                "has_start_request": False,
                "start_request_summary": None,
                "boundary": "read_only;does_not_stop_start_or_schedule_restart",
            },
        )

    def test_watch_status_diagnostics_view_projects_statefile_ownership(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            controller.status_result = {
                "control": {"state": "running", "active": True, "run_id": "run-001", "pid": 1234},
                "watch_status": {"state": "running", "run_id": "run-001"},
                "statefile_ownership": {
                    "schema_version": "tdx.subscription_watch.statefile_ownership.v1",
                    "status": "owned_active",
                    "reason_codes": ["OWNED_ACTIVE"],
                    "statefile_exists": True,
                    "pidfile_exists": True,
                    "lockfile_exists": True,
                    "active": True,
                    "control_state": "running",
                    "payload_pid": 1234,
                    "owned_pid": 1234,
                    "pid_matches_owned_state": True,
                    "process_alive": True,
                    "boundary": "local_statefile_pidfile_only;does_not_claim_provider_readiness_or_lifecycle_control",
                },
                "status_summary": {
                    "schema_version": "tdx.subscription_watch.status_summary.v1",
                    "control_rollup": {"control_state": "running", "control_active": True},
                    "consistency_rollup": {"has_mismatch": False},
                    "governance": {
                        "requires_manual_review": False,
                        "staleness_evaluated": False,
                        "boundary": "advisory_only; does_not_trigger_reconnect_backoff_restart_or_lifecycle_changes",
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
                payload = self._request(f"{base_url}/bridge/v1/watch/status?view=diagnostics", token="secret-token")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(
            payload["result"]["diagnostics"]["statefile_ownership"],
            {
                "schema_version": "tdx.subscription_watch.statefile_ownership.v1",
                "status": "owned_active",
                "reason_codes": ["OWNED_ACTIVE"],
                "statefile_exists": True,
                "pidfile_exists": True,
                "lockfile_exists": True,
                "active": True,
                "control_state": "running",
                "payload_pid": 1234,
                "owned_pid": 1234,
                "pid_matches_owned_state": True,
                "process_alive": True,
                "boundary": "local_statefile_pidfile_only;does_not_claim_provider_readiness_or_lifecycle_control",
            },
        )
        self.assertNotIn("control", payload["result"])
        self.assertNotIn("watch_status", payload["result"])

    def test_watch_status_summary_view_projects_supervisor_daemon_status(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            controller.status_result = {
                "control": {"state": "running", "active": True, "run_id": "run-001", "pid": 1234},
                "watch_status": {"state": "running", "run_id": "run-001"},
                "supervisor_daemon": {
                    "schema_version": "tdx.subscription_watch.supervisor_daemon.v1",
                    "daemon_status": "running",
                    "state": "running",
                    "statefile_exists": True,
                    "statefile_valid": True,
                    "pidfile_exists": True,
                    "pid": 4321,
                    "process_running": True,
                    "owner_token": "owner-1",
                    "generation": 1,
                    "settings": {"max_ticks": 2, "interval_seconds": 0.5, "loop_sleep_seconds": 3.0},
                    "control_allowed": True,
                    "boundary": "read_only_supervisor_daemon_status;does_not_execute_lifecycle",
                },
                "status_summary": {
                    "schema_version": "tdx.subscription_watch.status_summary.v1",
                    "overall_status": "running",
                    "control_rollup": {"control_state": "running", "control_active": True},
                    "consistency_rollup": {"has_mismatch": False},
                    "governance": {
                        "requires_manual_review": False,
                        "staleness_evaluated": False,
                        "boundary": "advisory_only; does_not_trigger_reconnect_backoff_restart_or_lifecycle_changes",
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
                payload = self._request(f"{base_url}/bridge/v1/watch/status?view=summary", token="secret-token")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(
            payload["result"]["supervisor_daemon"],
            {
                "schema_version": "tdx.subscription_watch.supervisor_daemon.v1",
                "daemon_status": "running",
                "state": "running",
                "statefile_exists": True,
                "statefile_valid": True,
                "pidfile_exists": True,
                "pid": 4321,
                "process_running": True,
                "has_owner_token": True,
                "generation": 1,
                "control_allowed": True,
                "boundary": "read_only_supervisor_daemon_status;does_not_execute_lifecycle",
            },
        )
        self.assertNotIn("owner_token", payload["result"]["supervisor_daemon"])
        self.assertNotIn("settings", payload["result"]["supervisor_daemon"])
        self.assertNotIn("control", payload["result"])
        self.assertNotIn("watch_status", payload["result"])

    def test_watch_status_diagnostics_view_projects_supervisor_daemon_status(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            controller.status_result = {
                "control": {"state": "running", "active": True, "run_id": "run-001", "pid": 1234},
                "watch_status": {"state": "running", "run_id": "run-001"},
                "supervisor_daemon": {
                    "schema_version": "tdx.subscription_watch.supervisor_daemon.v1",
                    "daemon_status": "not_running",
                    "state": "running",
                    "statefile_exists": True,
                    "statefile_valid": True,
                    "pidfile_exists": True,
                    "pid": 4321,
                    "process_running": False,
                    "owner_token": "owner-1",
                    "generation": 2,
                    "settings": {"max_ticks": 2},
                    "control_allowed": False,
                    "boundary": "read_only_supervisor_daemon_status;does_not_execute_lifecycle",
                },
                "status_summary": {
                    "schema_version": "tdx.subscription_watch.status_summary.v1",
                    "control_rollup": {"control_state": "running", "control_active": True},
                    "consistency_rollup": {"has_mismatch": False},
                    "governance": {
                        "requires_manual_review": False,
                        "staleness_evaluated": False,
                        "boundary": "advisory_only; does_not_trigger_reconnect_backoff_restart_or_lifecycle_changes",
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
                payload = self._request(f"{base_url}/bridge/v1/watch/status?view=diagnostics", token="secret-token")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        expected = {
            "schema_version": "tdx.subscription_watch.supervisor_daemon.v1",
            "daemon_status": "not_running",
            "state": "running",
            "statefile_exists": True,
            "statefile_valid": True,
            "pidfile_exists": True,
            "pid": 4321,
            "process_running": False,
            "has_owner_token": True,
            "generation": 2,
            "control_allowed": False,
            "boundary": "read_only_supervisor_daemon_status;does_not_execute_lifecycle",
        }
        self.assertEqual(payload["result"]["supervisor_daemon"], expected)
        self.assertEqual(payload["result"]["diagnostics"]["supervisor_daemon"], expected)
        self.assertNotIn("owner_token", payload["result"]["diagnostics"]["supervisor_daemon"])
        self.assertNotIn("settings", payload["result"]["diagnostics"]["supervisor_daemon"])

    def test_watch_status_diagnostics_view_projects_supervisor_run_observation(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            controller.status_result = {
                "control": {
                    "state": "restart_backoff",
                    "active": False,
                    "run_id": "run-001",
                    "pid": None,
                    "last_supervisor_run_observation": {
                        "schema_version": "tdx.subscription_watch.supervisor_run_observation.v1",
                        "status": "waiting",
                        "final_status": "waiting",
                        "final_decision": "wait",
                        "tick_count": 2,
                        "max_ticks": 2,
                        "interval_seconds": 0.0,
                        "reason": "manual_supervise",
                        "action_taken": False,
                        "tick_status_counts": {"waiting": 2},
                        "tick_decision_counts": {"wait": 2},
                        "boundary": "observation_only;does_not_schedule_supervisor_or_background_retry",
                    },
                },
                "watch_status": None,
                "status_summary": {
                    "schema_version": "tdx.subscription_watch.status_summary.v1",
                    "control_rollup": {"control_state": "restart_backoff", "control_active": False},
                    "consistency_rollup": {"has_mismatch": False},
                    "governance": {
                        "requires_manual_review": False,
                        "staleness_evaluated": False,
                        "boundary": "advisory_only; does_not_trigger_reconnect_backoff_restart_or_lifecycle_changes",
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
                payload = self._request(f"{base_url}/bridge/v1/watch/status?view=diagnostics", token="secret-token")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(
            payload["result"]["diagnostics"]["supervisor_run_observation"],
            {
                "schema_version": "tdx.subscription_watch.supervisor_run_observation.v1",
                "status": "waiting",
                "final_status": "waiting",
                "final_decision": "wait",
                "tick_count": 2,
                "max_ticks": 2,
                "interval_seconds": 0.0,
                "reason": "manual_supervise",
                "action_taken": False,
                "tick_status_counts": {"waiting": 2},
                "tick_decision_counts": {"wait": 2},
                "boundary": "observation_only;does_not_schedule_supervisor_or_background_retry",
            },
        )
        self.assertNotIn("tick_summaries", payload["result"]["diagnostics"]["supervisor_run_observation"])
        self.assertNotIn("control", payload["result"])
        self.assertNotIn("watch_status", payload["result"])

    def test_watch_status_diagnostics_view_projects_supervisor_tick_observation(self) -> None:
        with TemporaryDirectory() as temp_dir:
            controller = _FakeController()
            controller.status_result = {
                "control": {
                    "state": "restart_backoff",
                    "active": False,
                    "run_id": "run-001",
                    "pid": None,
                    "last_supervisor_tick_observation": {
                        "schema_version": "tdx.subscription_watch.supervisor_tick_observation.v1",
                        "status": "recovered",
                        "decision": "recovered",
                        "action_taken": True,
                        "reason_codes": [],
                        "previous_run_id": "run-001",
                        "new_run_id": "run-002",
                        "reason": "manual_tick",
                        "start_request_summary": {
                            "stock_count": 2,
                            "has_max_events": True,
                            "has_max_seconds": True,
                            "has_poll_interval": True,
                        },
                        "boundary": "observation_only;does_not_schedule_supervisor_or_background_retry",
                        "start_result": {"run_id": "run-002"},
                        "restart_backoff": {"status": "expired"},
                    },
                },
                "watch_status": None,
                "status_summary": {
                    "schema_version": "tdx.subscription_watch.status_summary.v1",
                    "control_rollup": {"control_state": "restart_backoff", "control_active": False},
                    "consistency_rollup": {"has_mismatch": False},
                    "governance": {
                        "requires_manual_review": False,
                        "staleness_evaluated": False,
                        "boundary": "advisory_only; does_not_trigger_reconnect_backoff_restart_or_lifecycle_changes",
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
                payload = self._request(f"{base_url}/bridge/v1/watch/status?view=diagnostics", token="secret-token")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(
            payload["result"]["diagnostics"]["supervisor_tick_observation"],
            {
                "schema_version": "tdx.subscription_watch.supervisor_tick_observation.v1",
                "status": "recovered",
                "decision": "recovered",
                "action_taken": True,
                "reason_codes": [],
                "previous_run_id": "run-001",
                "new_run_id": "run-002",
                "reason": "manual_tick",
                "start_request_summary": {
                    "stock_count": 2,
                    "has_max_events": True,
                    "has_max_seconds": True,
                    "has_poll_interval": True,
                },
                "boundary": "observation_only;does_not_schedule_supervisor_or_background_retry",
            },
        )
        self.assertNotIn("start_result", payload["result"]["diagnostics"]["supervisor_tick_observation"])
        self.assertNotIn("restart_backoff", payload["result"]["diagnostics"]["supervisor_tick_observation"])
        self.assertNotIn("control", payload["result"])
        self.assertNotIn("watch_status", payload["result"])

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
        self.assertEqual(payload["error"]["message"], "query parameter view must be one of: detailed, diagnostics, summary")
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
