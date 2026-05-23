from __future__ import annotations

import errno
import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from tdxquant.bridge_registry import (
    BridgeWorker,
    call_worker,
    load_worker_registry,
    resolve_worker_token,
    run_bridge_health,
    run_bridge_watch_artifacts,
    run_bridge_watch_events,
    run_bridge_watch_event_stream,
    run_bridge_watch_list,
    run_bridge_watch_logs,
    run_bridge_watch_start,
    run_bridge_watch_status,
    select_worker,
)


class BridgeRegistryTests(unittest.TestCase):
    def test_load_worker_registry_reads_enabled_workers(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "master-workers.json"
            path.write_text(
                json.dumps(
                    [
                        {
                            "worker_id": "worker-a",
                            "label": "A",
                            "host": "127.0.0.1",
                            "port": 8080,
                            "token_env": "BRIDGE_TOKEN_A",
                            "role_tags": ["watch"],
                            "enabled": True,
                        },
                        {
                            "worker_id": "worker-b",
                            "label": "B",
                            "host": "127.0.0.1",
                            "port": 8081,
                            "token_env": "BRIDGE_TOKEN_B",
                            "role_tags": ["watch"],
                            "enabled": False,
                        },
                    ]
                ),
                encoding="utf-8",
            )

            workers = load_worker_registry(path)

        self.assertEqual(len(workers), 1)
        self.assertEqual(workers[0].worker_id, "worker-a")
        self.assertEqual(workers[0].host, "127.0.0.1")

    def test_select_worker_requires_known_enabled_worker(self) -> None:
        workers = [
            BridgeWorker(
                worker_id="worker-a",
                label="A",
                host="127.0.0.1",
                port=8080,
                token_env="BRIDGE_TOKEN_A",
                role_tags=["watch"],
                enabled=True,
            )
        ]

        selected = select_worker(workers, worker_id="worker-a")

        self.assertEqual(selected.worker_id, "worker-a")
        with self.assertRaisesRegex(ValueError, "unknown worker"):
            select_worker(workers, worker_id="worker-missing")

    def test_load_worker_registry_rejects_duplicate_worker_ids(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "master-workers.json"
            path.write_text(
                json.dumps(
                    [
                        {
                            "worker_id": "worker-a",
                            "label": "A1",
                            "host": "127.0.0.1",
                            "port": 8080,
                            "token_env": "BRIDGE_TOKEN_A1",
                            "role_tags": ["watch"],
                            "enabled": True,
                        },
                        {
                            "worker_id": "worker-a",
                            "label": "A2",
                            "host": "127.0.0.1",
                            "port": 8081,
                            "token_env": "BRIDGE_TOKEN_A2",
                            "role_tags": ["watch"],
                            "enabled": True,
                        },
                    ]
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "duplicate worker_id"):
                load_worker_registry(path)

    def test_resolve_worker_token_reads_token_env(self) -> None:
        worker = BridgeWorker(
            worker_id="worker-a",
            label="A",
            host="127.0.0.1",
            port=8080,
            token_env="BRIDGE_TOKEN_A",
            role_tags=["watch"],
            enabled=True,
        )

        with patch.dict("os.environ", {"BRIDGE_TOKEN_A": "secret-token"}, clear=True):
            token = resolve_worker_token(worker)

        self.assertEqual(token, "secret-token")

    def test_call_worker_sends_json_with_bearer_token(self) -> None:
        worker = BridgeWorker(
            worker_id="worker-a",
            label="A",
            host="127.0.0.1",
            port=8787,
            token_env="BRIDGE_TOKEN_A",
            role_tags=["watch"],
            enabled=True,
        )

        response_payload = {"ok": True, "result": {"status": "running"}}

        class _FakeResponse:
            def __enter__(self) -> "_FakeResponse":
                return self

            def __exit__(self, exc_type, exc, tb) -> None:
                del exc_type, exc, tb

            def read(self) -> bytes:
                return json.dumps(response_payload).encode("utf-8")

        with patch("tdxquant.bridge_registry.urlopen", return_value=_FakeResponse()) as mocked:
            payload = call_worker(
                worker,
                method="POST",
                route="/bridge/v1/watch/start",
                token="secret-token",
                body={"stock_list": ["000001.SZ"]},
            )

        self.assertEqual(payload, response_payload)
        request = mocked.call_args.args[0]
        self.assertEqual(request.full_url, "http://127.0.0.1:8787/bridge/v1/watch/start")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Authorization"), "Bearer secret-token")
        self.assertEqual(json.loads(request.data.decode("utf-8")), {"stock_list": ["000001.SZ"]})

    def test_run_bridge_watch_start_includes_poll_interval_and_idempotency_key(self) -> None:
        worker = BridgeWorker(
            worker_id="worker-a",
            label="A",
            host="127.0.0.1",
            port=8787,
            token_env="BRIDGE_TOKEN_A",
            role_tags=["watch"],
            enabled=True,
        )

        with (
            patch("tdxquant.bridge_registry.load_worker_registry", return_value=[worker]),
            patch("tdxquant.bridge_registry.resolve_worker_token", return_value="secret-token"),
            patch("tdxquant.bridge_registry.call_worker", return_value={"ok": True, "result": {"run_id": "run-001"}}) as mocked_call,
        ):
            payload = run_bridge_watch_start(
                registry_path="runtime/bridge/master-workers.json",
                worker_id="worker-a",
                stock_list=["000001.SZ"],
                max_events=5,
                max_seconds=30.0,
                poll_interval=0.5,
                idempotency_key="idem-001",
            )

        self.assertEqual(payload, {"ok": True, "result": {"run_id": "run-001"}})
        self.assertEqual(
            mocked_call.call_args.kwargs["body"],
            {
                "stock_list": ["000001.SZ"],
                "max_events": 5,
                "max_seconds": 30.0,
                "poll_interval": 0.5,
                "idempotency_key": "idem-001",
            },
        )

    def test_run_bridge_health_uses_health_route(self) -> None:
        worker = BridgeWorker(
            worker_id="worker-a",
            label="A",
            host="127.0.0.1",
            port=8787,
            token_env="BRIDGE_TOKEN_A",
            role_tags=["watch"],
            enabled=True,
        )

        with (
            patch("tdxquant.bridge_registry.load_worker_registry", return_value=[worker]),
            patch("tdxquant.bridge_registry.resolve_worker_token", return_value="secret-token"),
            patch("tdxquant.bridge_registry.call_worker", return_value={"ok": True, "result": {"status": "ok"}}) as mocked_call,
        ):
            payload = run_bridge_health(
                registry_path="runtime/bridge/master-workers.json",
                worker_id="worker-a",
            )

        self.assertEqual(payload, {"ok": True, "result": {"status": "ok"}})
        self.assertEqual(mocked_call.call_args.kwargs["route"], "/bridge/v1/health")

    def test_run_bridge_watch_list_uses_list_route(self) -> None:
        worker = BridgeWorker(
            worker_id="worker-a",
            label="A",
            host="127.0.0.1",
            port=8787,
            token_env="BRIDGE_TOKEN_A",
            role_tags=["watch"],
            enabled=True,
        )

        with (
            patch("tdxquant.bridge_registry.load_worker_registry", return_value=[worker]),
            patch("tdxquant.bridge_registry.resolve_worker_token", return_value="secret-token"),
            patch("tdxquant.bridge_registry.call_worker", return_value={"ok": True, "result": {"active": None}}) as mocked_call,
        ):
            payload = run_bridge_watch_list(
                registry_path="runtime/bridge/master-workers.json",
                worker_id="worker-a",
            )

        self.assertEqual(payload, {"ok": True, "result": {"active": None}})
        self.assertEqual(mocked_call.call_args.kwargs["route"], "/bridge/v1/watch/list")

    def test_run_bridge_watch_artifacts_uses_artifacts_route(self) -> None:
        worker = BridgeWorker(
            worker_id="worker-a",
            label="A",
            host="127.0.0.1",
            port=8787,
            token_env="BRIDGE_TOKEN_A",
            role_tags=["watch"],
            enabled=True,
        )

        with (
            patch("tdxquant.bridge_registry.load_worker_registry", return_value=[worker]),
            patch("tdxquant.bridge_registry.resolve_worker_token", return_value="secret-token"),
            patch("tdxquant.bridge_registry.call_worker", return_value={"ok": True, "result": {"run_id": "run-001"}}) as mocked_call,
        ):
            payload = run_bridge_watch_artifacts(
                registry_path="runtime/bridge/master-workers.json",
                worker_id="worker-a",
            )

        self.assertEqual(payload, {"ok": True, "result": {"run_id": "run-001"}})
        self.assertEqual(mocked_call.call_args.kwargs["route"], "/bridge/v1/watch/artifacts")

    def test_run_bridge_watch_events_uses_tail_query_parameter(self) -> None:
        worker = BridgeWorker(
            worker_id="worker-a",
            label="A",
            host="127.0.0.1",
            port=8787,
            token_env="BRIDGE_TOKEN_A",
            role_tags=["watch"],
            enabled=True,
        )

        with (
            patch("tdxquant.bridge_registry.load_worker_registry", return_value=[worker]),
            patch("tdxquant.bridge_registry.resolve_worker_token", return_value="secret-token"),
            patch("tdxquant.bridge_registry.call_worker", return_value={"ok": True, "result": {"events": []}}) as mocked_call,
        ):
            payload = run_bridge_watch_events(
                registry_path="runtime/bridge/master-workers.json",
                worker_id="worker-a",
                tail=25,
            )

        self.assertEqual(payload, {"ok": True, "result": {"events": []}})
        self.assertEqual(mocked_call.call_args.kwargs["route"], "/bridge/v1/watch/events?tail=25")

    def test_run_bridge_watch_status_uses_heartbeat_stale_query_parameter(self) -> None:
        worker = BridgeWorker(
            worker_id="worker-a",
            label="A",
            host="127.0.0.1",
            port=8787,
            token_env="BRIDGE_TOKEN_A",
            role_tags=["watch"],
            enabled=True,
        )

        with (
            patch("tdxquant.bridge_registry.load_worker_registry", return_value=[worker]),
            patch("tdxquant.bridge_registry.resolve_worker_token", return_value="secret-token"),
            patch("tdxquant.bridge_registry.call_worker", return_value={"ok": True, "result": {"status": "running"}}) as mocked_call,
        ):
            payload = run_bridge_watch_status(
                registry_path="runtime/bridge/master-workers.json",
                worker_id="worker-a",
                heartbeat_stale_after_seconds=60,
                watermark_stale_after_seconds=120,
                reconnect_stale_after_seconds=180,
            )

        self.assertEqual(payload, {"ok": True, "result": {"status": "running"}})
        self.assertEqual(
            mocked_call.call_args.kwargs["route"],
            "/bridge/v1/watch/status?heartbeat_stale_after_seconds=60&watermark_stale_after_seconds=120&reconnect_stale_after_seconds=180",
        )

    def test_run_bridge_watch_event_stream_uses_stream_route_and_cursor_query(self) -> None:
        worker = BridgeWorker(
            worker_id="worker-a",
            label="A",
            host="127.0.0.1",
            port=8787,
            token_env="BRIDGE_TOKEN_A",
            role_tags=["watch"],
            enabled=True,
        )

        with (
            patch("tdxquant.bridge_registry.load_worker_registry", return_value=[worker]),
            patch("tdxquant.bridge_registry.resolve_worker_token", return_value="secret-token"),
            patch("tdxquant.bridge_registry.call_worker_text", return_value="event: heartbeat\n\n") as mocked_call,
        ):
            payload = run_bridge_watch_event_stream(
                registry_path="runtime/bridge/master-workers.json",
                worker_id="worker-a",
                run_id="run-001",
                from_cursor="run-001:event:7",
                follow=False,
                heartbeat_seconds=5,
            )

        self.assertEqual(payload, "event: heartbeat\n\n")
        self.assertEqual(
            mocked_call.call_args.kwargs["route"],
            "/bridge/v1/watch/events/stream?run_id=run-001&from=run-001%3Aevent%3A7&follow=false&heartbeat_seconds=5",
        )

    def test_run_bridge_watch_logs_uses_tail_query_parameter(self) -> None:
        worker = BridgeWorker(
            worker_id="worker-a",
            label="A",
            host="127.0.0.1",
            port=8787,
            token_env="BRIDGE_TOKEN_A",
            role_tags=["watch"],
            enabled=True,
        )

        with (
            patch("tdxquant.bridge_registry.load_worker_registry", return_value=[worker]),
            patch("tdxquant.bridge_registry.resolve_worker_token", return_value="secret-token"),
            patch("tdxquant.bridge_registry.call_worker", return_value={"ok": True, "result": {"lines": []}}) as mocked_call,
        ):
            payload = run_bridge_watch_logs(
                registry_path="runtime/bridge/master-workers.json",
                worker_id="worker-a",
                tail=50,
            )

        self.assertEqual(payload, {"ok": True, "result": {"lines": []}})
        self.assertEqual(mocked_call.call_args.kwargs["route"], "/bridge/v1/watch/logs?tail=50")

    def test_call_worker_returns_bridge_json_error_body_for_http_failures(self) -> None:
        worker = BridgeWorker(
            worker_id="worker-a",
            label="A",
            host="127.0.0.1",
            port=8787,
            token_env="BRIDGE_TOKEN_A",
            role_tags=["watch"],
            enabled=True,
        )
        error_payload = {
            "ok": False,
            "result": None,
            "error": {
                "code": "FORBIDDEN_SOURCE",
                "message": "source ip is not allowed",
                "details": {},
            },
            "meta": {"worker_id": "worker-a", "request_id": "req-1"},
        }
        http_error = HTTPError(
            url="http://127.0.0.1:8787/bridge/v1/watch/status",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(json.dumps(error_payload).encode("utf-8")),
        )

        with patch("tdxquant.bridge_registry.urlopen", side_effect=http_error):
            payload = call_worker(
                worker,
                method="GET",
                route="/bridge/v1/watch/status",
                token="secret-token",
            )

        self.assertEqual(payload, error_payload)

    def test_call_worker_raises_runtime_error_for_invalid_json_success_body(self) -> None:
        worker = BridgeWorker(
            worker_id="worker-a",
            label="A",
            host="127.0.0.1",
            port=8787,
            token_env="BRIDGE_TOKEN_A",
            role_tags=["watch"],
            enabled=True,
        )

        class _InvalidJsonResponse:
            def __enter__(self) -> "_InvalidJsonResponse":
                return self

            def __exit__(self, exc_type, exc, tb) -> None:
                del exc_type, exc, tb

            def read(self) -> bytes:
                return b"{not valid json"

        with patch("tdxquant.bridge_registry.urlopen", return_value=_InvalidJsonResponse()):
            with self.assertRaisesRegex(RuntimeError, "bridge worker returned invalid JSON payload"):
                call_worker(
                    worker,
                    method="GET",
                    route="/bridge/v1/watch/status",
                    token="secret-token",
                )

    def test_call_worker_raises_runtime_error_for_invalid_utf8_success_body(self) -> None:
        worker = BridgeWorker(
            worker_id="worker-a",
            label="A",
            host="127.0.0.1",
            port=8787,
            token_env="BRIDGE_TOKEN_A",
            role_tags=["watch"],
            enabled=True,
        )

        class _InvalidUtf8Response:
            def __enter__(self) -> "_InvalidUtf8Response":
                return self

            def __exit__(self, exc_type, exc, tb) -> None:
                del exc_type, exc, tb

            def read(self) -> bytes:
                return b"\xff"

        with patch("tdxquant.bridge_registry.urlopen", return_value=_InvalidUtf8Response()):
            with self.assertRaisesRegex(RuntimeError, "bridge worker returned invalid JSON payload"):
                call_worker(
                    worker,
                    method="GET",
                    route="/bridge/v1/watch/status",
                    token="secret-token",
                )

    def test_call_worker_raises_runtime_error_for_non_object_json_success_body(self) -> None:
        worker = BridgeWorker(
            worker_id="worker-a",
            label="A",
            host="127.0.0.1",
            port=8787,
            token_env="BRIDGE_TOKEN_A",
            role_tags=["watch"],
            enabled=True,
        )

        class _ArrayPayloadResponse:
            def __enter__(self) -> "_ArrayPayloadResponse":
                return self

            def __exit__(self, exc_type, exc, tb) -> None:
                del exc_type, exc, tb

            def read(self) -> bytes:
                return b"[]"

        with patch("tdxquant.bridge_registry.urlopen", return_value=_ArrayPayloadResponse()):
            with self.assertRaisesRegex(RuntimeError, "bridge worker returned non-object JSON payload"):
                call_worker(
                    worker,
                    method="GET",
                    route="/bridge/v1/watch/status",
                    token="secret-token",
                )

    def test_call_worker_normalizes_non_json_http_error_body(self) -> None:
        worker = BridgeWorker(
            worker_id="worker-a",
            label="A",
            host="127.0.0.1",
            port=8787,
            token_env="BRIDGE_TOKEN_A",
            role_tags=["watch"],
            enabled=True,
        )
        http_error = HTTPError(
            url="http://127.0.0.1:8787/bridge/v1/watch/status",
            code=502,
            msg="Bad Gateway",
            hdrs=None,
            fp=io.BytesIO(b"upstream gateway failure"),
        )

        with patch("tdxquant.bridge_registry.urlopen", side_effect=http_error):
            with self.assertRaisesRegex(RuntimeError, "bridge worker request failed with HTTP 502: Bad Gateway"):
                call_worker(
                    worker,
                    method="GET",
                    route="/bridge/v1/watch/status",
                    token="secret-token",
                )

    def test_call_worker_raises_runtime_error_for_connection_refused(self) -> None:
        worker = BridgeWorker(
            worker_id="worker-a",
            label="A",
            host="127.0.0.1",
            port=8787,
            token_env="BRIDGE_TOKEN_A",
            role_tags=["watch"],
            enabled=True,
        )

        transport_error = URLError(ConnectionRefusedError(errno.ECONNREFUSED, "Connection refused"))

        with patch("tdxquant.bridge_registry.urlopen", side_effect=transport_error):
            with self.assertRaisesRegex(RuntimeError, "bridge worker request failed: connection refused"):
                call_worker(
                    worker,
                    method="GET",
                    route="/bridge/v1/watch/status",
                    token="secret-token",
                )
