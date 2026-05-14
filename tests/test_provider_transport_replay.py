from __future__ import annotations

import json
import threading
import unittest
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from tdxquant.provider_transport_replay import (
    ProviderTransportReplayConfig,
    ProviderTransportReplayHTTPServer,
)
from tdxquant.replay_fixtures import list_provider_replay_fixtures, load_provider_replay_fixture


class ProviderTransportReplayHTTPTests(unittest.TestCase):
    def _start_server(
        self,
        *,
        master_allowlist: list[str] | None = None,
    ) -> tuple[ProviderTransportReplayHTTPServer, str, threading.Thread]:
        config = ProviderTransportReplayConfig(
            provider_id="provider-replay-a",
            bind_host="127.0.0.1",
            port=0,
            token="secret-token",
            master_allowlist=master_allowlist if master_allowlist is not None else ["127.0.0.1"],
        )
        server = ProviderTransportReplayHTTPServer(config)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server, f"http://127.0.0.1:{server.server_address[1]}", thread

    def _request_json(
        self,
        url: str,
        *,
        token: str | None = "secret-token",
    ) -> dict[str, object]:
        headers: dict[str, str] = {}
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        request = Request(url, headers=headers, method="GET")
        with urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

    def _request_text(
        self,
        url: str,
        *,
        token: str | None = "secret-token",
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
        server, base_url, thread = self._start_server()
        try:
            with self.assertRaises(HTTPError) as ctx:
                self._request_json(f"{base_url}/provider/v1/replay/health", token=None)
            payload = json.loads(ctx.exception.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertEqual(ctx.exception.code, 401)
        self.assertEqual(payload["error"]["code"], "UNAUTHORIZED")

    def test_health_rejects_disallowed_source_ip(self) -> None:
        server, base_url, thread = self._start_server(master_allowlist=["10.0.0.10"])
        try:
            with self.assertRaises(HTTPError) as ctx:
                self._request_json(f"{base_url}/provider/v1/replay/health")
            payload = json.loads(ctx.exception.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertEqual(ctx.exception.code, 403)
        self.assertEqual(payload["error"]["code"], "FORBIDDEN_SOURCE")

    def test_health_and_fixture_catalog_report_replay_only_transport(self) -> None:
        server, base_url, thread = self._start_server()
        try:
            health = self._request_json(f"{base_url}/provider/v1/replay/health")
            catalog = self._request_json(f"{base_url}/provider/v1/replay/fixtures")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertTrue(health["ok"])
        self.assertEqual(health["meta"]["provider_mode"], "replay")
        self.assertEqual(health["result"]["status"], "ok")
        self.assertEqual(health["result"]["service"], "provider-transport-replay")

        names = {item["name"] for item in catalog["result"]["fixtures"]}
        self.assertIn("runtime-capabilities-success", names)
        delayed = next(item for item in catalog["result"]["fixtures"] if item["name"] == "subscription-watch-event-stream-delayed-playback")
        self.assertEqual(delayed["transport"], "sse")
        self.assertEqual(delayed["playback_mode"], "delayed")

    def test_sync_replay_result_endpoint_preserves_provider_contract(self) -> None:
        server, base_url, thread = self._start_server()
        try:
            payload = self._request_json(f"{base_url}/provider/v1/replay/result?capability=runtime.capabilities")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        provider_result = payload["result"]["provider_result"]
        self.assertTrue(payload["ok"])
        self.assertEqual(provider_result["capability"], "runtime.capabilities")
        self.assertEqual(provider_result["runtime"]["mode"], "replay")
        self.assertEqual(provider_result["runtime"]["replay_source"]["mode"], "replay")
        self.assertIn("capabilities", provider_result["data"])

    def test_watch_status_and_events_are_served_from_replay_fixtures(self) -> None:
        server, base_url, thread = self._start_server()
        try:
            status = self._request_json(f"{base_url}/provider/v1/replay/watch/status")
            events = self._request_json(f"{base_url}/provider/v1/replay/watch/events?tail=1")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertEqual(status["result"]["control"]["state"], "completed")
        self.assertFalse(status["result"]["control"]["active"])
        self.assertEqual(status["result"]["watch_status"]["state"], "completed")
        self.assertEqual(status["result"]["replay_source"]["mode"], "replay")

        self.assertEqual(events["result"]["run_id"], "20260501T080000000000Z")
        self.assertEqual(len(events["result"]["events"]), 1)
        self.assertEqual(events["result"]["events"][0]["sequence"], 2)
        self.assertEqual(events["result"]["events"][0]["symbol"], "000001.SZ")

    def test_watch_stream_serves_immediate_sse_frames_from_replay_fixtures(self) -> None:
        server, base_url, thread = self._start_server()
        try:
            content_type, raw = self._request_text(f"{base_url}/provider/v1/replay/watch/events/stream")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertEqual(content_type, "text/event-stream")
        payloads = self._parse_sse_payloads(raw)
        frame_types = [item["frame_type"] for item in payloads]
        self.assertIn("status", frame_types)
        self.assertIn("quote", frame_types)
        self.assertEqual(payloads[0]["provider_mode"], "replay")
        self.assertEqual(payloads[0]["playback"]["mode"], "immediate")

    def test_watch_stream_delayed_playback_adds_deterministic_offsets(self) -> None:
        server, base_url, thread = self._start_server()
        try:
            _content_type, raw = self._request_text(
                f"{base_url}/provider/v1/replay/watch/events/stream?playback=delayed&delay_ms=250"
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        payloads = self._parse_sse_payloads(raw)
        quote_frames = [item for item in payloads if item["frame_type"] == "quote"]
        self.assertGreaterEqual(len(quote_frames), 2)
        self.assertEqual(quote_frames[0]["playback"]["mode"], "delayed")
        self.assertEqual(quote_frames[0]["playback"]["delay_ms"], 250)
        self.assertEqual(quote_frames[0]["playback"]["planned_emit_after_ms"], 250)
        self.assertEqual(quote_frames[1]["playback"]["planned_emit_after_ms"], 500)


class ProviderTransportReplayFixtureTests(unittest.TestCase):
    def test_delayed_playback_fixture_is_cataloged_and_loadable(self) -> None:
        fixtures = list_provider_replay_fixtures()
        delayed = next(item for item in fixtures if item["name"] == "subscription-watch-event-stream-delayed-playback")

        payload = load_provider_replay_fixture("subscription-watch-event-stream-delayed-playback")

        self.assertEqual(delayed["transport"], "sse")
        self.assertEqual(delayed["playback_mode"], "delayed")
        self.assertIsInstance(payload, list)
        quote_frames = [item for item in payload if item["frame_type"] == "quote"]
        self.assertGreaterEqual(len(quote_frames), 2)
        self.assertEqual(quote_frames[0]["playback"]["planned_emit_after_ms"], 250)
