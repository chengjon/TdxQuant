from __future__ import annotations

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

    def test_call_worker_preserves_json_error_body_on_non_2xx_response(self) -> None:
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
            "error": {
                "code": "UNAUTHORIZED",
                "message": "missing or invalid bearer token",
                "details": {},
            },
            "meta": {"worker_id": "worker-a", "request_id": "req-1"},
        }
        http_error = HTTPError(
            url="http://127.0.0.1:8787/bridge/v1/watch/status",
            code=401,
            msg="Unauthorized",
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

    def test_call_worker_normalizes_url_error(self) -> None:
        worker = BridgeWorker(
            worker_id="worker-a",
            label="A",
            host="127.0.0.1",
            port=8787,
            token_env="BRIDGE_TOKEN_A",
            role_tags=["watch"],
            enabled=True,
        )

        with patch("tdxquant.bridge_registry.urlopen", side_effect=URLError("connection refused")):
            with self.assertRaisesRegex(RuntimeError, "bridge worker request failed: connection refused"):
                call_worker(
                    worker,
                    method="GET",
                    route="/bridge/v1/watch/status",
                    token="secret-token",
                )
