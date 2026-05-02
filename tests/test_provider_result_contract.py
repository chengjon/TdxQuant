import json
import unittest
from pathlib import Path

from tdxquant.models import ErrorCode, Result
from tdxquant.result_contract import build_runtime_metadata


class ProviderResultContractTests(unittest.TestCase):
    def _load_fixture(self, name: str) -> dict:
        path = Path(__file__).parent / "fixtures" / name
        return json.loads(path.read_text(encoding="utf-8"))

    def test_success_fixture_matches_provider_contract(self) -> None:
        expected = self._load_fixture("provider_result_success.json")
        result = Result(ok=True, code=ErrorCode.OK, message="ok", data={"rows": [{"symbol": "000001.SZ"}]})
        payload = result.to_provider_dict(
            capability="formula.screen",
            capability_version="v1",
            schema_version="2026-04-28",
            request_id="req-success",
            started_at="2026-04-28T12:00:00Z",
            finished_at="2026-04-28T12:00:01Z",
            elapsed_ms=1000.0,
            runtime=build_runtime_metadata(mode="bridge"),
        )
        self.assertEqual(payload, expected)
        self.assertTrue(payload["success"])
        self.assertTrue(payload["ok"])
        self.assertIsInstance(payload["warnings"], list)
        self.assertIsInstance(payload["artifacts"], list)
        self.assertIsInstance(payload["data"], dict)

    def test_failure_fixture_matches_provider_contract(self) -> None:
        expected = self._load_fixture("provider_result_failure.json")
        result = Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="invalid formula input",
            data={},
            warnings=["formula warning"],
            next_action="fix-input",
        )
        payload = result.to_provider_dict(
            capability="formula.screen",
            capability_version="v1",
            schema_version="2026-04-28",
            request_id="req-failure",
            started_at="2026-04-28T12:00:00Z",
            finished_at="2026-04-28T12:00:01Z",
            elapsed_ms=1000.0,
            runtime=build_runtime_metadata(mode="bridge"),
        )
        self.assertEqual(payload, expected)
        self.assertFalse(payload["success"])
        self.assertFalse(payload["ok"])
        self.assertIsInstance(payload["warnings"], list)
        self.assertIsInstance(payload["artifacts"], list)
        self.assertIsInstance(payload["data"], dict)
