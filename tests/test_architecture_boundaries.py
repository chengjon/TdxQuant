from __future__ import annotations

import tempfile
import unittest
import argparse
from pathlib import Path
from unittest.mock import patch

from tdxquant.architecture import CapabilityRisk, build_capability_risk_metadata, classify_capability_risk
from tdxquant.cli import _handle_api_subcommand as handle_root_api_subcommand
from tdxquant.cli import build_parser as build_root_parser
from tdxquant.cli_api import build_api_parser, handle_api_subcommand
from tdxquant.models import ErrorCode, Result
from tdxquant.runtime_config import get_runtime_config_path, list_runtime_config_names, load_runtime_config_object


class CapabilityRiskTests(unittest.TestCase):
    def test_classifies_read_only_query_capability(self) -> None:
        self.assertEqual(classify_capability_risk("market.snapshot"), CapabilityRisk.READ_ONLY_QUERY)
        self.assertEqual(classify_capability_risk("block.read_watchlist_snapshot"), CapabilityRisk.READ_ONLY_QUERY)

    def test_classifies_provider_and_trade_mutations(self) -> None:
        self.assertEqual(classify_capability_risk("block.send_user_block"), CapabilityRisk.PROVIDER_MUTATION)
        self.assertEqual(classify_capability_risk("trade.order_stock"), CapabilityRisk.NATIVE_TRADE_MUTATION)
        self.assertEqual(classify_capability_risk("pingan.buy_submit_once"), CapabilityRisk.DESKTOP_TRADE_MUTATION)

    def test_builds_machine_readable_metadata(self) -> None:
        metadata = build_capability_risk_metadata("block.sync_watchlist")

        self.assertEqual(metadata["risk"], "provider_mutation")
        self.assertFalse(metadata["read_only"])
        self.assertTrue(metadata["mutation"])


class RuntimeConfigRegistryTests(unittest.TestCase):
    def test_resolves_registered_runtime_config_from_project_root(self) -> None:
        path = get_runtime_config_path("api_profiles")

        self.assertTrue(path.is_absolute())
        self.assertEqual(path.name, "api-profiles.json")

    def test_lists_known_runtime_configs(self) -> None:
        names = list_runtime_config_names()

        self.assertIn("api_profiles", names)
        self.assertIn("command_catalog", names)
        self.assertEqual(names, sorted(names))

    def test_loads_json_object_without_changing_contents(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "config.json"
            path.write_text('{"default": {"field": "value"}}', encoding="utf-8")

            payload = load_runtime_config_object("api_profiles", path=path)

        self.assertEqual(payload, {"default": {"field": "value"}})

    def test_rejects_non_object_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "config.json"
            path.write_text("[]", encoding="utf-8")

            with self.assertRaises(ValueError):
                load_runtime_config_object("api_profiles", path=path)


class ApiCliModuleBoundaryTests(unittest.TestCase):
    def test_api_cli_module_registers_nested_api_parser(self) -> None:
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command", required=True)

        build_api_parser(subparsers)
        args = parser.parse_args(["api", "capabilities", "--provider-mode", "replay"])

        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "capabilities")
        self.assertEqual(args.provider_mode, "replay")

    def test_root_cli_registers_nested_api_parser_through_api_module(self) -> None:
        parser = build_root_parser()

        args = parser.parse_args(["api", "snapshot", "--code", "000001.SZ", "--field", "Now"])

        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "snapshot")
        self.assertEqual(args.code, "000001.SZ")
        self.assertEqual(args.field, ["Now"])

    def test_root_cli_delegates_nested_api_dispatch_to_api_module(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="delegated")
        parser = build_root_parser()
        args = parser.parse_args(["api", "capabilities"])

        with patch("tdxquant.cli._handle_api_subcommand_impl", return_value=expected) as delegated:
            result = handle_root_api_subcommand(args)

        self.assertIs(result, expected)
        delegated.assert_called_once()

    def test_api_cli_module_dispatch_accepts_manager_factory(self) -> None:
        captured_kwargs: dict[str, object] = {}

        class FakeRuntime:
            def capabilities(self) -> Result:
                return Result(ok=True, code=ErrorCode.OK, message="ok", data={"source": "fake"})

        class FakeManager:
            def __init__(self, **kwargs: object) -> None:
                captured_kwargs.update(kwargs)
                self.runtime = FakeRuntime()

        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command", required=True)
        build_api_parser(subparsers)
        args = parser.parse_args(["api", "capabilities", "--profile", "brief", "--provider-mode", "replay"])

        result = handle_api_subcommand(args, manager_factory=FakeManager)

        self.assertTrue(result.ok)
        self.assertEqual(captured_kwargs["profile"], "brief")
        self.assertEqual(captured_kwargs["provider_mode"], "replay")


if __name__ == "__main__":
    unittest.main()
