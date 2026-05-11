import json
import unittest
from importlib import import_module
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from tdxquant.api import TdxApiManager, TdxTaskManager
from tdxquant.api.context import get_api_profile_path, load_api_profiles, resolve_api_profile
from tdxquant.api.task import get_task_profile_path, load_task_profiles, resolve_task_profile
from tdxquant.catalog import (
    get_command_bundle_path,
    get_command_catalog_path,
    load_command_bundles,
    load_command_catalog,
    resolve_command_bundle,
    resolve_command_catalog_entry,
)
from tdxquant.api.block import BlockApi
from tdxquant.api.financial import FinancialApi
from tdxquant.api.formula import FormulaApi
from tdxquant.api.market import MarketApi
from tdxquant.api.meta import MetaApi
from tdxquant.api.runtime import RuntimeApi
from tdxquant.models import ErrorCode, Result
from tdxquant.replay_fixtures import load_provider_replay_fixture
from tdxquant.reporting import get_report_preset_path, load_report_presets, resolve_report_preset
from tdxquant.tasking import get_task_preset_path, load_task_presets, resolve_task_preset


class ApiContextTests(unittest.TestCase):
    def test_get_api_profile_path_is_absolute(self) -> None:
        self.assertTrue(get_api_profile_path().is_absolute())
        self.assertEqual(get_api_profile_path().name, "api-profiles.json")

    def test_load_api_profiles_reads_json_object(self) -> None:
        with TemporaryDirectory() as temp_dir:
            profile_path = Path(temp_dir) / "api-profiles.json"
            profile_path.write_text('{"default": {"list_type": 0}}', encoding="utf-8")
            profiles = load_api_profiles(profile_path)
        self.assertEqual(profiles["default"]["list_type"], 0)

    def test_resolve_api_profile_prefers_explicit_overrides(self) -> None:
        profiles = {"default": {"list_type": 0, "include_timing": True}}
        resolved = resolve_api_profile("default", overrides={"list_type": 1}, profiles=profiles)
        self.assertEqual(resolved["list_type"], 1)
        self.assertTrue(resolved["include_timing"])

    def test_get_task_profile_path_is_absolute(self) -> None:
        self.assertTrue(get_task_profile_path().is_absolute())
        self.assertEqual(get_task_profile_path().name, "task-profiles.json")

    def test_load_task_profiles_reads_json_object(self) -> None:
        with TemporaryDirectory() as temp_dir:
            profile_path = Path(temp_dir) / "task-profiles.json"
            profile_path.write_text('{"default": {"api_profile": "default"}}', encoding="utf-8")
            profiles = load_task_profiles(profile_path)
        self.assertEqual(profiles["default"]["api_profile"], "default")

    def test_resolve_task_profile_prefers_explicit_overrides(self) -> None:
        profiles = {"default": {"api_profile": "default", "output_format": "json"}}
        resolved = resolve_task_profile("default", overrides={"output_format": "csv"}, profiles=profiles)
        self.assertEqual(resolved["output_format"], "csv")
        self.assertEqual(resolved["api_profile"], "default")

    def test_get_report_preset_path_is_absolute(self) -> None:
        self.assertTrue(get_report_preset_path().is_absolute())
        self.assertEqual(get_report_preset_path().name, "report-presets.json")

    def test_load_report_presets_reads_json_object(self) -> None:
        with TemporaryDirectory() as temp_dir:
            preset_path = Path(temp_dir) / "report-presets.json"
            preset_path.write_text('{"daily-review": {"command": "daily", "options": {"recent_limit": 20}}}', encoding="utf-8")
            presets = load_report_presets(preset_path)
        self.assertEqual(presets["daily-review"]["command"], "daily")

    def test_runtime_report_presets_include_trade_audit_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-daily-review", presets)
        self.assertIn("audit-daily-confirmed", presets)
        self.assertIn("audit-period-review", presets)
        self.assertEqual(presets["audit-daily-review"]["command"], "audit-daily")
        self.assertEqual(presets["audit-period-review"]["command"], "audit-period")

    def test_runtime_report_presets_include_pingan_trade_audit_review_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-daily-pingan-review", presets)
        self.assertIn("audit-period-pingan-review", presets)
        self.assertEqual(presets["audit-daily-pingan-review"]["command"], "audit-daily")
        self.assertEqual(presets["audit-daily-pingan-review"]["options"]["broker"], "pingan")
        self.assertEqual(presets["audit-period-pingan-review"]["command"], "audit-period")
        self.assertEqual(presets["audit-period-pingan-review"]["options"]["broker"], "pingan")

    def test_runtime_report_presets_include_rejected_trade_audit_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-daily-rejected", presets)
        self.assertIn("audit-period-rejected", presets)
        self.assertEqual(presets["audit-daily-rejected"]["options"]["status"], "rejected")
        self.assertEqual(presets["audit-period-rejected"]["options"]["status"], "rejected")

    def test_runtime_report_presets_include_confirmed_and_replayed_trade_audit_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-period-confirmed", presets)
        self.assertIn("audit-daily-replayed", presets)
        self.assertIn("audit-period-replayed", presets)
        self.assertEqual(presets["audit-period-confirmed"]["options"]["status"], "confirmed")
        self.assertEqual(presets["audit-daily-replayed"]["options"]["status"], "replayed")
        self.assertEqual(presets["audit-period-replayed"]["options"]["status"], "replayed")

    def test_runtime_report_presets_include_pingan_confirmed_and_replayed_trade_audit_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-daily-pingan-confirmed", presets)
        self.assertIn("audit-period-pingan-confirmed", presets)
        self.assertIn("audit-daily-pingan-replayed", presets)
        self.assertIn("audit-period-pingan-replayed", presets)
        self.assertEqual(presets["audit-daily-pingan-confirmed"]["options"]["broker"], "pingan")
        self.assertEqual(presets["audit-daily-pingan-confirmed"]["options"]["status"], "confirmed")
        self.assertEqual(presets["audit-period-pingan-replayed"]["options"]["broker"], "pingan")
        self.assertEqual(presets["audit-period-pingan-replayed"]["options"]["status"], "replayed")

    def test_runtime_report_presets_include_failed_trade_audit_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-daily-failed", presets)
        self.assertIn("audit-period-failed", presets)
        self.assertEqual(presets["audit-daily-failed"]["options"]["status"], "failed")
        self.assertEqual(presets["audit-period-failed"]["options"]["status"], "failed")

    def test_runtime_report_presets_include_trade_audit_exception_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-daily-exceptions", presets)
        self.assertIn("audit-period-exceptions", presets)
        self.assertEqual(presets["audit-daily-exceptions"]["options"]["statuses"], ["rejected", "failed"])
        self.assertEqual(presets["audit-period-exceptions"]["options"]["statuses"], ["rejected", "failed"])

    def test_runtime_report_presets_include_pingan_trade_audit_exception_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-daily-pingan-exceptions", presets)
        self.assertIn("audit-period-pingan-exceptions", presets)
        self.assertEqual(presets["audit-daily-pingan-exceptions"]["options"]["broker"], "pingan")
        self.assertEqual(
            presets["audit-daily-pingan-exceptions"]["options"]["statuses"],
            ["rejected", "failed"],
        )
        self.assertEqual(presets["audit-period-pingan-exceptions"]["options"]["broker"], "pingan")

    def test_runtime_report_presets_include_pingan_rejected_and_failed_trade_audit_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-daily-pingan-rejected", presets)
        self.assertIn("audit-period-pingan-rejected", presets)
        self.assertIn("audit-daily-pingan-failed", presets)
        self.assertIn("audit-period-pingan-failed", presets)
        self.assertEqual(presets["audit-daily-pingan-rejected"]["options"]["broker"], "pingan")
        self.assertEqual(presets["audit-daily-pingan-rejected"]["options"]["status"], "rejected")
        self.assertEqual(presets["audit-period-pingan-failed"]["options"]["broker"], "pingan")
        self.assertEqual(presets["audit-period-pingan-failed"]["options"]["status"], "failed")

    def test_runtime_report_presets_include_confirm_oriented_trade_audit_exception_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-daily-confirm-exceptions", presets)
        self.assertIn("audit-period-confirm-exceptions", presets)
        self.assertEqual(presets["audit-daily-confirm-exceptions"]["options"]["method"], "confirm_current")
        self.assertEqual(
            presets["audit-daily-confirm-exceptions"]["options"]["statuses"],
            ["rejected", "failed"],
        )
        self.assertEqual(presets["audit-period-confirm-exceptions"]["options"]["method"], "confirm_current")

    def test_runtime_report_presets_include_submit_once_trade_audit_exception_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-daily-submit-once-exceptions", presets)
        self.assertIn("audit-period-submit-once-exceptions", presets)
        self.assertEqual(presets["audit-daily-submit-once-exceptions"]["options"]["method"], "buy_submit_once")
        self.assertEqual(
            presets["audit-daily-submit-once-exceptions"]["options"]["statuses"],
            ["rejected", "failed"],
        )
        self.assertEqual(presets["audit-period-submit-once-exceptions"]["options"]["method"], "buy_submit_once")

    def test_runtime_report_presets_include_pingan_submit_once_trade_audit_exception_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-daily-pingan-submit-once-exceptions", presets)
        self.assertIn("audit-period-pingan-submit-once-exceptions", presets)
        self.assertEqual(
            presets["audit-daily-pingan-submit-once-exceptions"]["options"]["broker"],
            "pingan",
        )
        self.assertEqual(
            presets["audit-daily-pingan-submit-once-exceptions"]["options"]["method"],
            "buy_submit_once",
        )
        self.assertEqual(
            presets["audit-daily-pingan-submit-once-exceptions"]["options"]["statuses"],
            ["rejected", "failed"],
        )
        self.assertEqual(
            presets["audit-period-pingan-submit-once-exceptions"]["options"]["broker"],
            "pingan",
        )

    def test_runtime_report_presets_include_buy_trade_audit_exception_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-daily-buy-exceptions", presets)
        self.assertIn("audit-period-buy-exceptions", presets)
        self.assertEqual(presets["audit-daily-buy-exceptions"]["options"]["method"], "buy")
        self.assertEqual(
            presets["audit-daily-buy-exceptions"]["options"]["statuses"],
            ["rejected", "failed"],
        )
        self.assertEqual(presets["audit-period-buy-exceptions"]["options"]["method"], "buy")

    def test_runtime_report_presets_include_pingan_buy_trade_audit_exception_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-daily-pingan-buy-exceptions", presets)
        self.assertIn("audit-period-pingan-buy-exceptions", presets)
        self.assertEqual(presets["audit-daily-pingan-buy-exceptions"]["options"]["broker"], "pingan")
        self.assertEqual(presets["audit-daily-pingan-buy-exceptions"]["options"]["method"], "buy")
        self.assertEqual(
            presets["audit-daily-pingan-buy-exceptions"]["options"]["statuses"],
            ["rejected", "failed"],
        )
        self.assertEqual(presets["audit-period-pingan-buy-exceptions"]["options"]["broker"], "pingan")

    def test_runtime_report_presets_include_sell_trade_audit_exception_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-daily-sell-exceptions", presets)
        self.assertIn("audit-period-sell-exceptions", presets)
        self.assertEqual(presets["audit-daily-sell-exceptions"]["options"]["method"], "sell")
        self.assertEqual(
            presets["audit-daily-sell-exceptions"]["options"]["statuses"],
            ["rejected", "failed"],
        )
        self.assertEqual(presets["audit-period-sell-exceptions"]["options"]["method"], "sell")

    def test_runtime_report_presets_include_pingan_sell_trade_audit_exception_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-daily-pingan-sell-exceptions", presets)
        self.assertIn("audit-period-pingan-sell-exceptions", presets)
        self.assertEqual(presets["audit-daily-pingan-sell-exceptions"]["options"]["broker"], "pingan")
        self.assertEqual(presets["audit-daily-pingan-sell-exceptions"]["options"]["method"], "sell")
        self.assertEqual(
            presets["audit-daily-pingan-sell-exceptions"]["options"]["statuses"],
            ["rejected", "failed"],
        )
        self.assertEqual(presets["audit-period-pingan-sell-exceptions"]["options"]["broker"], "pingan")

    def test_runtime_report_presets_include_submit_path_trade_audit_exception_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-daily-submit-path-exceptions", presets)
        self.assertIn("audit-period-submit-path-exceptions", presets)
        self.assertEqual(
            presets["audit-daily-submit-path-exceptions"]["options"]["methods"],
            ["buy_submit_once", "confirm_current"],
        )
        self.assertEqual(
            presets["audit-daily-submit-path-exceptions"]["options"]["statuses"],
            ["rejected", "failed"],
        )
        self.assertEqual(
            presets["audit-period-submit-path-exceptions"]["options"]["methods"],
            ["buy_submit_once", "confirm_current"],
        )

    def test_runtime_report_presets_include_pingan_submit_path_trade_audit_exception_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-daily-pingan-submit-path-exceptions", presets)
        self.assertIn("audit-period-pingan-submit-path-exceptions", presets)
        self.assertEqual(
            presets["audit-daily-pingan-submit-path-exceptions"]["options"]["broker"],
            "pingan",
        )
        self.assertEqual(
            presets["audit-daily-pingan-submit-path-exceptions"]["options"]["methods"],
            ["buy_submit_once", "confirm_current"],
        )
        self.assertEqual(
            presets["audit-daily-pingan-submit-path-exceptions"]["options"]["statuses"],
            ["rejected", "failed"],
        )
        self.assertEqual(
            presets["audit-period-pingan-submit-path-exceptions"]["options"]["broker"],
            "pingan",
        )

    def test_runtime_report_presets_include_pingan_order_trade_audit_exception_presets(self) -> None:
        presets = load_report_presets()
        self.assertIn("audit-daily-pingan-order-exceptions", presets)
        self.assertIn("audit-period-pingan-order-exceptions", presets)
        self.assertEqual(
            presets["audit-daily-pingan-order-exceptions"]["options"]["broker"],
            "pingan",
        )
        self.assertEqual(
            presets["audit-daily-pingan-order-exceptions"]["options"]["methods"],
            ["buy", "sell"],
        )
        self.assertEqual(
            presets["audit-daily-pingan-order-exceptions"]["options"]["statuses"],
            ["rejected", "failed"],
        )
        self.assertEqual(
            presets["audit-period-pingan-order-exceptions"]["options"]["broker"],
            "pingan",
        )

    def test_resolve_report_preset_prefers_explicit_overrides(self) -> None:
        presets = {
            "daily-review": {
                "command": "daily",
                "profile": "daily_trade_report",
                "options": {"timezone": "Asia/Shanghai", "recent_limit": 20},
            }
        }
        resolved = resolve_report_preset("daily-review", overrides={"options": {"timezone": "UTC"}}, presets=presets)
        self.assertEqual(resolved["command"], "daily")
        self.assertEqual(resolved["profile"], "daily_trade_report")
        self.assertEqual(resolved["options"]["timezone"], "UTC")
        self.assertEqual(resolved["options"]["recent_limit"], 20)

    def test_resolve_report_preset_uses_default_profile_for_audit_lookup_command(self) -> None:
        presets = {
            "audit-trace": {
                "command": "audit-lookup",
                "options": {"audit_id": "audit-001"},
            }
        }
        resolved = resolve_report_preset("audit-trace", presets=presets)
        self.assertEqual(resolved["command"], "audit-lookup")
        self.assertEqual(resolved["profile"], "trade_audit_lookup")

    def test_resolve_report_preset_uses_default_profile_for_audit_daily_and_period_commands(self) -> None:
        presets = {
            "audit-daily": {"command": "audit-daily", "options": {"date": "2026-04-29"}},
            "audit-period": {"command": "audit-period", "options": {"start_date": "2026-04-28"}},
        }
        daily = resolve_report_preset("audit-daily", presets=presets)
        period = resolve_report_preset("audit-period", presets=presets)
        self.assertEqual(daily["profile"], "trade_audit_daily_report")
        self.assertEqual(period["profile"], "trade_audit_period_report")

    def test_get_task_preset_path_is_absolute(self) -> None:
        self.assertTrue(get_task_preset_path().is_absolute())
        self.assertEqual(get_task_preset_path().name, "task-presets.json")

    def test_load_task_presets_reads_json_object(self) -> None:
        with TemporaryDirectory() as temp_dir:
            preset_path = Path(temp_dir) / "task-presets.json"
            preset_path.write_text('{"guarded-default": {"command": "guarded-trade-buy", "options": {"port": "COM3"}}}', encoding="utf-8")
            presets = load_task_presets(preset_path)
        self.assertEqual(presets["guarded-default"]["command"], "guarded-trade-buy")

    def test_resolve_task_preset_prefers_explicit_overrides(self) -> None:
        presets = {
            "guarded-default": {
                "command": "guarded-trade-buy",
                "profile": "guarded_trade_buy",
                "trade_profile": "balanced",
                "options": {"port": "COM3", "required_block_code": "ZXG"},
            }
        }
        resolved = resolve_task_preset("guarded-default", overrides={"options": {"port": "COM9"}}, presets=presets)
        self.assertEqual(resolved["command"], "guarded-trade-buy")
        self.assertEqual(resolved["profile"], "guarded_trade_buy")
        self.assertEqual(resolved["trade_profile"], "balanced")
        self.assertEqual(resolved["options"]["port"], "COM9")
        self.assertEqual(resolved["options"]["required_block_code"], "ZXG")

    def test_resolve_task_preset_uses_default_profile_for_split_step_trade_commands(self) -> None:
        presets = {
            "submit-ready-default": {"command": "trade-submit-ready", "options": {"port": "COM3"}},
            "confirm-current-default": {"command": "trade-confirm-current", "options": {"close_result_dialog": False}},
        }
        submit_ready = resolve_task_preset("submit-ready-default", presets=presets)
        confirm_current = resolve_task_preset("confirm-current-default", presets=presets)
        self.assertEqual(submit_ready["profile"], "trade_submit_ready")
        self.assertEqual(confirm_current["profile"], "trade_confirm_current")

    def test_resolve_task_preset_uses_default_profile_for_trade_audit_lookup_command(self) -> None:
        presets = {
            "audit-trace": {"command": "trade-audit-lookup", "options": {"audit_id": "audit-001"}},
        }
        resolved = resolve_task_preset("audit-trace", presets=presets)
        self.assertEqual(resolved["command"], "trade-audit-lookup")
        self.assertEqual(resolved["profile"], "trade_audit_lookup")

    def test_resolve_task_preset_uses_default_profile_for_trade_audit_daily_and_period_commands(self) -> None:
        presets = {
            "audit-daily": {"command": "trade-audit-daily-report", "options": {"date": "2026-04-29"}},
            "audit-period": {"command": "trade-audit-period-report", "options": {"start_date": "2026-04-28"}},
        }
        daily = resolve_task_preset("audit-daily", presets=presets)
        period = resolve_task_preset("audit-period", presets=presets)
        self.assertEqual(daily["profile"], "trade_audit_daily_report")
        self.assertEqual(period["profile"], "trade_audit_period_report")

    def test_runtime_task_presets_include_split_step_trade_presets(self) -> None:
        presets = load_task_presets()
        self.assertIn("submit-ready-default", presets)
        self.assertIn("confirm-current-default", presets)
        self.assertEqual(presets["submit-ready-default"]["command"], "trade-submit-ready")
        self.assertEqual(presets["confirm-current-default"]["command"], "trade-confirm-current")

    def test_get_command_catalog_path_is_absolute(self) -> None:
        self.assertTrue(get_command_catalog_path().is_absolute())
        self.assertEqual(get_command_catalog_path().name, "command-catalog.json")

    def test_load_command_catalog_reads_json_object(self) -> None:
        with TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "command-catalog.json"
            catalog_path.write_text('{"daily-review": {"source": "report", "preset": "daily-review"}}', encoding="utf-8")
            entries = load_command_catalog(catalog_path)
        self.assertEqual(entries["daily-review"]["source"], "report")

    def test_runtime_command_catalog_includes_trade_audit_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-daily-review", entries)
        self.assertIn("audit-daily-confirmed", entries)
        self.assertIn("audit-period-review", entries)
        self.assertEqual(entries["audit-daily-review"]["source"], "report")
        self.assertEqual(entries["audit-daily-review"]["preset"], "audit-daily-review")

    def test_runtime_command_catalog_includes_pingan_trade_audit_review_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-daily-pingan-review", entries)
        self.assertIn("audit-period-pingan-review", entries)
        self.assertEqual(entries["audit-daily-pingan-review"]["source"], "report")
        self.assertEqual(entries["audit-daily-pingan-review"]["preset"], "audit-daily-pingan-review")
        self.assertEqual(entries["audit-period-pingan-review"]["preset"], "audit-period-pingan-review")

    def test_runtime_command_catalog_includes_rejected_trade_audit_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-daily-rejected", entries)
        self.assertIn("audit-period-rejected", entries)
        self.assertEqual(entries["audit-daily-rejected"]["source"], "report")
        self.assertEqual(entries["audit-daily-rejected"]["preset"], "audit-daily-rejected")

    def test_runtime_command_catalog_includes_confirmed_and_replayed_trade_audit_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-period-confirmed", entries)
        self.assertIn("audit-daily-replayed", entries)
        self.assertIn("audit-period-replayed", entries)
        self.assertEqual(entries["audit-period-confirmed"]["preset"], "audit-period-confirmed")
        self.assertEqual(entries["audit-daily-replayed"]["preset"], "audit-daily-replayed")

    def test_runtime_command_catalog_includes_pingan_confirmed_and_replayed_trade_audit_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-daily-pingan-confirmed", entries)
        self.assertIn("audit-period-pingan-confirmed", entries)
        self.assertIn("audit-daily-pingan-replayed", entries)
        self.assertIn("audit-period-pingan-replayed", entries)
        self.assertEqual(entries["audit-daily-pingan-confirmed"]["preset"], "audit-daily-pingan-confirmed")
        self.assertEqual(entries["audit-period-pingan-replayed"]["preset"], "audit-period-pingan-replayed")

    def test_runtime_command_catalog_includes_failed_trade_audit_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-daily-failed", entries)
        self.assertIn("audit-period-failed", entries)
        self.assertEqual(entries["audit-daily-failed"]["source"], "report")
        self.assertEqual(entries["audit-daily-failed"]["preset"], "audit-daily-failed")

    def test_runtime_command_catalog_includes_trade_audit_exception_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-daily-exceptions", entries)
        self.assertIn("audit-period-exceptions", entries)
        self.assertEqual(entries["audit-daily-exceptions"]["preset"], "audit-daily-exceptions")

    def test_runtime_command_catalog_includes_pingan_trade_audit_exception_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-daily-pingan-exceptions", entries)
        self.assertIn("audit-period-pingan-exceptions", entries)
        self.assertEqual(
            entries["audit-daily-pingan-exceptions"]["preset"],
            "audit-daily-pingan-exceptions",
        )
        self.assertEqual(
            entries["audit-period-pingan-exceptions"]["preset"],
            "audit-period-pingan-exceptions",
        )

    def test_runtime_command_catalog_includes_pingan_rejected_and_failed_trade_audit_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-daily-pingan-rejected", entries)
        self.assertIn("audit-period-pingan-rejected", entries)
        self.assertIn("audit-daily-pingan-failed", entries)
        self.assertIn("audit-period-pingan-failed", entries)
        self.assertEqual(entries["audit-daily-pingan-rejected"]["preset"], "audit-daily-pingan-rejected")
        self.assertEqual(entries["audit-period-pingan-failed"]["preset"], "audit-period-pingan-failed")

    def test_runtime_command_catalog_includes_confirm_oriented_trade_audit_exception_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-daily-confirm-exceptions", entries)
        self.assertIn("audit-period-confirm-exceptions", entries)
        self.assertEqual(entries["audit-daily-confirm-exceptions"]["preset"], "audit-daily-confirm-exceptions")
        self.assertEqual(entries["audit-period-confirm-exceptions"]["preset"], "audit-period-confirm-exceptions")

    def test_runtime_command_catalog_includes_submit_once_trade_audit_exception_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-daily-submit-once-exceptions", entries)
        self.assertIn("audit-period-submit-once-exceptions", entries)
        self.assertEqual(entries["audit-daily-submit-once-exceptions"]["preset"], "audit-daily-submit-once-exceptions")
        self.assertEqual(entries["audit-period-submit-once-exceptions"]["preset"], "audit-period-submit-once-exceptions")

    def test_runtime_command_catalog_includes_pingan_submit_once_trade_audit_exception_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-daily-pingan-submit-once-exceptions", entries)
        self.assertIn("audit-period-pingan-submit-once-exceptions", entries)
        self.assertEqual(
            entries["audit-daily-pingan-submit-once-exceptions"]["preset"],
            "audit-daily-pingan-submit-once-exceptions",
        )
        self.assertEqual(
            entries["audit-period-pingan-submit-once-exceptions"]["preset"],
            "audit-period-pingan-submit-once-exceptions",
        )

    def test_runtime_command_catalog_includes_buy_trade_audit_exception_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-daily-buy-exceptions", entries)
        self.assertIn("audit-period-buy-exceptions", entries)
        self.assertEqual(entries["audit-daily-buy-exceptions"]["preset"], "audit-daily-buy-exceptions")
        self.assertEqual(entries["audit-period-buy-exceptions"]["preset"], "audit-period-buy-exceptions")

    def test_runtime_command_catalog_includes_pingan_buy_trade_audit_exception_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-daily-pingan-buy-exceptions", entries)
        self.assertIn("audit-period-pingan-buy-exceptions", entries)
        self.assertEqual(
            entries["audit-daily-pingan-buy-exceptions"]["preset"],
            "audit-daily-pingan-buy-exceptions",
        )
        self.assertEqual(
            entries["audit-period-pingan-buy-exceptions"]["preset"],
            "audit-period-pingan-buy-exceptions",
        )

    def test_runtime_command_catalog_includes_sell_trade_audit_exception_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-daily-sell-exceptions", entries)
        self.assertIn("audit-period-sell-exceptions", entries)
        self.assertEqual(entries["audit-daily-sell-exceptions"]["preset"], "audit-daily-sell-exceptions")
        self.assertEqual(entries["audit-period-sell-exceptions"]["preset"], "audit-period-sell-exceptions")

    def test_runtime_command_catalog_includes_pingan_sell_trade_audit_exception_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-daily-pingan-sell-exceptions", entries)
        self.assertIn("audit-period-pingan-sell-exceptions", entries)
        self.assertEqual(
            entries["audit-daily-pingan-sell-exceptions"]["preset"],
            "audit-daily-pingan-sell-exceptions",
        )
        self.assertEqual(
            entries["audit-period-pingan-sell-exceptions"]["preset"],
            "audit-period-pingan-sell-exceptions",
        )

    def test_runtime_command_catalog_includes_submit_path_trade_audit_exception_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-daily-submit-path-exceptions", entries)
        self.assertIn("audit-period-submit-path-exceptions", entries)
        self.assertEqual(entries["audit-daily-submit-path-exceptions"]["preset"], "audit-daily-submit-path-exceptions")
        self.assertEqual(entries["audit-period-submit-path-exceptions"]["preset"], "audit-period-submit-path-exceptions")

    def test_runtime_command_catalog_includes_pingan_submit_path_trade_audit_exception_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-daily-pingan-submit-path-exceptions", entries)
        self.assertIn("audit-period-pingan-submit-path-exceptions", entries)
        self.assertEqual(
            entries["audit-daily-pingan-submit-path-exceptions"]["preset"],
            "audit-daily-pingan-submit-path-exceptions",
        )
        self.assertEqual(
            entries["audit-period-pingan-submit-path-exceptions"]["preset"],
            "audit-period-pingan-submit-path-exceptions",
        )

    def test_runtime_command_catalog_includes_pingan_order_trade_audit_exception_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("audit-daily-pingan-order-exceptions", entries)
        self.assertIn("audit-period-pingan-order-exceptions", entries)
        self.assertEqual(
            entries["audit-daily-pingan-order-exceptions"]["preset"],
            "audit-daily-pingan-order-exceptions",
        )
        self.assertEqual(
            entries["audit-period-pingan-order-exceptions"]["preset"],
            "audit-period-pingan-order-exceptions",
        )

    def test_runtime_command_catalog_includes_split_step_trade_entries(self) -> None:
        entries = load_command_catalog()
        self.assertIn("task-submit-ready", entries)
        self.assertIn("task-confirm-current", entries)
        self.assertEqual(entries["task-submit-ready"]["source"], "task")
        self.assertEqual(entries["task-submit-ready"]["preset"], "submit-ready-default")
        self.assertEqual(entries["task-confirm-current"]["preset"], "confirm-current-default")

    def test_resolve_command_catalog_entry_validates_source_and_preset(self) -> None:
        entries = {
            "guarded-buy": {
                "source": "task",
                "preset": "guarded-default",
                "description": "Guarded task alias",
                "labels": ["trade", "guarded"],
            }
        }
        resolved = resolve_command_catalog_entry("guarded-buy", entries=entries)
        self.assertEqual(resolved["source"], "task")
        self.assertEqual(resolved["preset"], "guarded-default")
        self.assertEqual(resolved["description"], "Guarded task alias")
        self.assertEqual(resolved["labels"], ["trade", "guarded"])

    def test_resolve_command_catalog_entry_normalizes_labels(self) -> None:
        entries = {
            "daily-review": {
                "source": "report",
                "preset": "daily-review",
                "labels": ["daily", "review", "daily"],
            }
        }
        resolved = resolve_command_catalog_entry("daily-review", entries=entries)
        self.assertEqual(resolved["labels"], ["daily", "review"])

    def test_get_command_bundle_path_is_absolute(self) -> None:
        self.assertTrue(get_command_bundle_path().is_absolute())
        self.assertEqual(get_command_bundle_path().name, "command-bundles.json")

    def test_load_command_bundles_reads_json_object(self) -> None:
        with TemporaryDirectory() as temp_dir:
            bundle_path = Path(temp_dir) / "command-bundles.json"
            bundle_path.write_text(
                '{"refresh-review": {"steps": [{"entry": "refresh-env"}]}}',
                encoding="utf-8",
            )
            bundles = load_command_bundles(bundle_path)
        self.assertEqual(bundles["refresh-review"]["steps"][0]["entry"], "refresh-env")

    def test_runtime_command_bundles_include_trade_audit_bundle(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-diagnostics", bundles)
        resolved = resolve_command_bundle("audit-diagnostics", bundles=bundles, entries=load_command_catalog())
        self.assertEqual(resolved["steps"][0]["entry"], "recent-failures")
        self.assertEqual(resolved["steps"][1]["entry"], "audit-daily-review")

    def test_runtime_command_bundles_include_pingan_trade_audit_review_bundle(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-pingan-review", bundles)
        resolved = resolve_command_bundle(
            "audit-pingan-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(resolved["steps"][0]["entry"], "recent-failures")
        self.assertEqual(resolved["steps"][1]["entry"], "audit-daily-pingan-review")

    def test_runtime_command_bundles_include_richer_trade_audit_bundles(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-rejection-diagnostics", bundles)
        self.assertIn("confirm-complete-review", bundles)
        rejection = resolve_command_bundle(
            "audit-rejection-diagnostics",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        confirm = resolve_command_bundle(
            "confirm-complete-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(rejection["steps"][0]["entry"], "recent-failures")
        self.assertEqual(rejection["steps"][1]["entry"], "audit-daily-rejected")
        self.assertEqual(confirm["steps"][0]["entry"], "task-confirm-current")
        self.assertEqual(confirm["steps"][1]["entry"], "daily-success")
        self.assertEqual(confirm["steps"][2]["entry"], "audit-daily-confirmed")

    def test_runtime_command_bundles_include_pingan_confirm_complete_review_bundle(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("confirm-pingan-complete-review", bundles)
        resolved = resolve_command_bundle(
            "confirm-pingan-complete-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(resolved["steps"][0]["entry"], "task-confirm-current")
        self.assertEqual(resolved["steps"][1]["entry"], "daily-success")
        self.assertEqual(resolved["steps"][2]["entry"], "audit-daily-pingan-confirmed")

    def test_runtime_command_bundles_include_confirmed_and_replayed_trade_audit_review_bundles(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-confirmed-review", bundles)
        self.assertIn("audit-replay-review", bundles)
        confirmed = resolve_command_bundle(
            "audit-confirmed-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        replayed = resolve_command_bundle(
            "audit-replay-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(confirmed["steps"][0]["entry"], "daily-success")
        self.assertEqual(confirmed["steps"][1]["entry"], "audit-daily-confirmed")
        self.assertEqual(replayed["steps"][0]["entry"], "recent-ledger")
        self.assertEqual(replayed["steps"][1]["entry"], "audit-daily-replayed")

    def test_runtime_command_bundles_include_pingan_confirmed_and_replayed_trade_audit_review_bundles(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-pingan-confirmed-review", bundles)
        self.assertIn("audit-pingan-replay-review", bundles)
        confirmed = resolve_command_bundle(
            "audit-pingan-confirmed-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        replayed = resolve_command_bundle(
            "audit-pingan-replay-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(confirmed["steps"][0]["entry"], "daily-success")
        self.assertEqual(confirmed["steps"][1]["entry"], "audit-daily-pingan-confirmed")
        self.assertEqual(replayed["steps"][0]["entry"], "recent-ledger")
        self.assertEqual(replayed["steps"][1]["entry"], "audit-daily-pingan-replayed")

    def test_runtime_command_bundles_include_failed_trade_audit_bundle(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-failure-diagnostics", bundles)
        failed = resolve_command_bundle(
            "audit-failure-diagnostics",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(failed["steps"][0]["entry"], "recent-failures")
        self.assertEqual(failed["steps"][1]["entry"], "audit-daily-failed")

    def test_runtime_command_bundles_include_trade_audit_exception_bundle(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-exception-diagnostics", bundles)
        exception = resolve_command_bundle(
            "audit-exception-diagnostics",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(exception["steps"][0]["entry"], "recent-failures")
        self.assertEqual(exception["steps"][1]["entry"], "audit-daily-exceptions")

    def test_runtime_command_bundles_include_pingan_trade_audit_exception_bundle(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-pingan-exception-diagnostics", bundles)
        diagnostics = resolve_command_bundle(
            "audit-pingan-exception-diagnostics",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(diagnostics["steps"][0]["entry"], "recent-failures")
        self.assertEqual(diagnostics["steps"][1]["entry"], "audit-daily-pingan-exceptions")

    def test_runtime_command_bundles_include_pingan_rejected_and_failed_trade_audit_bundles(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-pingan-rejection-diagnostics", bundles)
        self.assertIn("audit-pingan-failure-diagnostics", bundles)
        rejected = resolve_command_bundle(
            "audit-pingan-rejection-diagnostics",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        failed = resolve_command_bundle(
            "audit-pingan-failure-diagnostics",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(rejected["steps"][0]["entry"], "recent-failures")
        self.assertEqual(rejected["steps"][1]["entry"], "audit-daily-pingan-rejected")
        self.assertEqual(failed["steps"][0]["entry"], "recent-failures")
        self.assertEqual(failed["steps"][1]["entry"], "audit-daily-pingan-failed")

    def test_runtime_command_bundles_include_confirm_oriented_trade_audit_exception_bundles(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-confirm-exception-diagnostics", bundles)
        self.assertIn("confirm-exception-review", bundles)
        diagnostics = resolve_command_bundle(
            "audit-confirm-exception-diagnostics",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        followup = resolve_command_bundle(
            "confirm-exception-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(diagnostics["steps"][0]["entry"], "recent-failures")
        self.assertEqual(diagnostics["steps"][1]["entry"], "audit-daily-confirm-exceptions")
        self.assertEqual(followup["steps"][0]["entry"], "task-confirm-current")
        self.assertEqual(followup["steps"][1]["entry"], "audit-daily-confirm-exceptions")

    def test_runtime_command_bundles_include_submit_once_trade_audit_exception_bundles(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-submit-once-exception-diagnostics", bundles)
        self.assertIn("submit-once-exception-review", bundles)
        diagnostics = resolve_command_bundle(
            "audit-submit-once-exception-diagnostics",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        followup = resolve_command_bundle(
            "submit-once-exception-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(diagnostics["steps"][0]["entry"], "recent-failures")
        self.assertEqual(diagnostics["steps"][1]["entry"], "audit-daily-submit-once-exceptions")
        self.assertEqual(followup["steps"][0]["entry"], "task-submit-once")
        self.assertEqual(followup["steps"][1]["entry"], "audit-daily-submit-once-exceptions")

    def test_runtime_command_bundles_include_pingan_submit_once_trade_audit_exception_bundles(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-pingan-submit-once-exception-diagnostics", bundles)
        self.assertIn("submit-once-pingan-exception-review", bundles)
        diagnostics = resolve_command_bundle(
            "audit-pingan-submit-once-exception-diagnostics",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        followup = resolve_command_bundle(
            "submit-once-pingan-exception-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(diagnostics["steps"][0]["entry"], "recent-failures")
        self.assertEqual(diagnostics["steps"][1]["entry"], "audit-daily-pingan-submit-once-exceptions")
        self.assertEqual(followup["steps"][0]["entry"], "task-submit-once")
        self.assertEqual(followup["steps"][1]["entry"], "audit-daily-pingan-submit-once-exceptions")

    def test_runtime_command_bundles_include_submit_once_trade_audit_review_bundles(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("submit-once-audit-review", bundles)
        self.assertIn("submit-once-pingan-audit-review", bundles)
        review = resolve_command_bundle(
            "submit-once-audit-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        pingan_review = resolve_command_bundle(
            "submit-once-pingan-audit-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(review["steps"][0]["entry"], "task-submit-once")
        self.assertEqual(review["steps"][1]["entry"], "audit-daily-review")
        self.assertEqual(pingan_review["steps"][0]["entry"], "task-submit-once")
        self.assertEqual(pingan_review["steps"][1]["entry"], "audit-daily-pingan-review")

    def test_runtime_command_bundles_include_buy_trade_audit_exception_bundles(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-buy-exception-diagnostics", bundles)
        self.assertIn("guarded-buy-exception-review", bundles)
        diagnostics = resolve_command_bundle(
            "audit-buy-exception-diagnostics",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        followup = resolve_command_bundle(
            "guarded-buy-exception-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(diagnostics["steps"][0]["entry"], "recent-failures")
        self.assertEqual(diagnostics["steps"][1]["entry"], "audit-daily-buy-exceptions")
        self.assertEqual(followup["steps"][0]["entry"], "guarded-buy")
        self.assertEqual(followup["steps"][1]["entry"], "audit-daily-buy-exceptions")

    def test_runtime_command_bundles_include_guarded_buy_trade_audit_review_bundles(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("guarded-buy-audit-review", bundles)
        self.assertIn("guarded-pingan-buy-audit-review", bundles)
        review = resolve_command_bundle(
            "guarded-buy-audit-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        pingan_review = resolve_command_bundle(
            "guarded-pingan-buy-audit-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(review["steps"][0]["entry"], "guarded-buy")
        self.assertEqual(review["steps"][1]["entry"], "audit-daily-review")
        self.assertEqual(pingan_review["steps"][0]["entry"], "guarded-buy")
        self.assertEqual(pingan_review["steps"][1]["entry"], "audit-daily-pingan-review")

    def test_runtime_command_bundles_include_pingan_buy_trade_audit_exception_bundles(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-pingan-buy-exception-diagnostics", bundles)
        self.assertIn("guarded-pingan-buy-exception-review", bundles)
        diagnostics = resolve_command_bundle(
            "audit-pingan-buy-exception-diagnostics",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        followup = resolve_command_bundle(
            "guarded-pingan-buy-exception-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(diagnostics["steps"][0]["entry"], "recent-failures")
        self.assertEqual(diagnostics["steps"][1]["entry"], "audit-daily-pingan-buy-exceptions")
        self.assertEqual(followup["steps"][0]["entry"], "guarded-buy")
        self.assertEqual(followup["steps"][1]["entry"], "audit-daily-pingan-buy-exceptions")

    def test_runtime_command_bundles_include_sell_trade_audit_exception_bundle(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-sell-exception-diagnostics", bundles)
        diagnostics = resolve_command_bundle(
            "audit-sell-exception-diagnostics",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(diagnostics["steps"][0]["entry"], "recent-failures")
        self.assertEqual(diagnostics["steps"][1]["entry"], "audit-daily-sell-exceptions")

    def test_runtime_command_bundles_include_pingan_sell_trade_audit_exception_bundle(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-pingan-sell-exception-diagnostics", bundles)
        diagnostics = resolve_command_bundle(
            "audit-pingan-sell-exception-diagnostics",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(diagnostics["steps"][0]["entry"], "recent-failures")
        self.assertEqual(diagnostics["steps"][1]["entry"], "audit-daily-pingan-sell-exceptions")

    def test_runtime_command_bundles_include_submit_path_trade_audit_exception_bundles(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-submit-path-exception-diagnostics", bundles)
        self.assertIn("confirm-submit-path-exception-review", bundles)
        diagnostics = resolve_command_bundle(
            "audit-submit-path-exception-diagnostics",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        followup = resolve_command_bundle(
            "confirm-submit-path-exception-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(diagnostics["steps"][0]["entry"], "recent-failures")
        self.assertEqual(diagnostics["steps"][1]["entry"], "audit-daily-submit-path-exceptions")
        self.assertEqual(followup["steps"][0]["entry"], "task-confirm-current")
        self.assertEqual(followup["steps"][1]["entry"], "audit-daily-submit-path-exceptions")

    def test_runtime_command_bundles_include_pingan_submit_path_trade_audit_exception_bundles(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-pingan-submit-path-exception-diagnostics", bundles)
        self.assertIn("confirm-pingan-submit-path-exception-review", bundles)
        diagnostics = resolve_command_bundle(
            "audit-pingan-submit-path-exception-diagnostics",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        followup = resolve_command_bundle(
            "confirm-pingan-submit-path-exception-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(diagnostics["steps"][0]["entry"], "recent-failures")
        self.assertEqual(diagnostics["steps"][1]["entry"], "audit-daily-pingan-submit-path-exceptions")
        self.assertEqual(followup["steps"][0]["entry"], "task-confirm-current")
        self.assertEqual(followup["steps"][1]["entry"], "audit-daily-pingan-submit-path-exceptions")

    def test_runtime_command_bundles_include_pingan_order_trade_audit_exception_bundle(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-pingan-order-exception-diagnostics", bundles)
        diagnostics = resolve_command_bundle(
            "audit-pingan-order-exception-diagnostics",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(diagnostics["steps"][0]["entry"], "recent-failures")
        self.assertEqual(diagnostics["steps"][1]["entry"], "audit-daily-pingan-order-exceptions")

    def test_runtime_command_bundles_include_pingan_confirm_trade_audit_exception_bundles(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("audit-pingan-confirm-exception-diagnostics", bundles)
        self.assertIn("confirm-pingan-exception-review", bundles)
        diagnostics = resolve_command_bundle(
            "audit-pingan-confirm-exception-diagnostics",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        followup = resolve_command_bundle(
            "confirm-pingan-exception-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(diagnostics["steps"][0]["entry"], "recent-failures")
        self.assertEqual(diagnostics["steps"][1]["entry"], "audit-daily-pingan-confirm-exceptions")
        self.assertEqual(followup["steps"][0]["entry"], "task-confirm-current")
        self.assertEqual(followup["steps"][1]["entry"], "audit-daily-pingan-confirm-exceptions")

    def test_runtime_command_bundles_include_split_step_confirm_followup_bundle(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("confirm-audit-review", bundles)
        resolved = resolve_command_bundle("confirm-audit-review", bundles=bundles, entries=load_command_catalog())
        self.assertEqual(resolved["steps"][0]["entry"], "task-confirm-current")
        self.assertEqual(resolved["steps"][1]["entry"], "audit-daily-review")

    def test_runtime_command_bundles_include_split_step_confirm_pingan_followup_bundle(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("confirm-pingan-audit-review", bundles)
        resolved = resolve_command_bundle(
            "confirm-pingan-audit-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(resolved["steps"][0]["entry"], "task-confirm-current")
        self.assertEqual(resolved["steps"][1]["entry"], "audit-daily-pingan-review")

    def test_runtime_command_bundles_include_split_step_submit_ready_followup_bundles(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("submit-ready-audit-review", bundles)
        self.assertIn("submit-ready-exception-review", bundles)
        audit_review = resolve_command_bundle("submit-ready-audit-review", bundles=bundles, entries=load_command_catalog())
        exception_review = resolve_command_bundle("submit-ready-exception-review", bundles=bundles, entries=load_command_catalog())
        self.assertEqual(audit_review["steps"][0]["entry"], "task-submit-ready")
        self.assertEqual(audit_review["steps"][1]["entry"], "audit-daily-review")
        self.assertEqual(exception_review["steps"][0]["entry"], "task-submit-ready")
        self.assertEqual(exception_review["steps"][1]["entry"], "audit-daily-exceptions")

    def test_runtime_command_bundles_include_split_step_submit_ready_pingan_followup_bundles(self) -> None:
        bundles = load_command_bundles()
        self.assertIn("submit-ready-pingan-audit-review", bundles)
        self.assertIn("submit-ready-pingan-exception-review", bundles)
        audit_review = resolve_command_bundle(
            "submit-ready-pingan-audit-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        exception_review = resolve_command_bundle(
            "submit-ready-pingan-exception-review",
            bundles=bundles,
            entries=load_command_catalog(),
        )
        self.assertEqual(audit_review["steps"][0]["entry"], "task-submit-ready")
        self.assertEqual(audit_review["steps"][1]["entry"], "audit-daily-pingan-review")
        self.assertEqual(exception_review["steps"][0]["entry"], "task-submit-ready")
        self.assertEqual(exception_review["steps"][1]["entry"], "audit-daily-pingan-exceptions")

    def test_resolve_command_bundle_validates_steps_and_referenced_entries(self) -> None:
        bundles = {
            "refresh-review": {
                "description": "Refresh then review",
                "labels": ["morning", "review"],
                "steps": [
                    {"entry": "refresh-env", "name": "refresh"},
                    {"entry": "recent-ledger", "options": {"limit": 5}},
                ],
            }
        }
        entries = {
            "refresh-env": {"source": "task", "preset": "refresh-default", "description": "Refresh"},
            "recent-ledger": {"source": "report", "preset": "recent-ledger", "description": "Ledger"},
        }
        resolved = resolve_command_bundle("refresh-review", bundles=bundles, entries=entries)
        self.assertEqual(resolved["description"], "Refresh then review")
        self.assertEqual(resolved["labels"], ["morning", "review"])
        self.assertEqual(len(resolved["steps"]), 2)
        self.assertEqual(resolved["steps"][0]["index"], 1)
        self.assertEqual(resolved["steps"][0]["name"], "refresh")
        self.assertEqual(resolved["steps"][0]["source"], "task")
        self.assertEqual(resolved["steps"][1]["index"], 2)
        self.assertEqual(resolved["steps"][1]["name"], "recent-ledger")
        self.assertEqual(resolved["steps"][1]["preset"], "recent-ledger")
        self.assertEqual(resolved["steps"][1]["options"]["limit"], 5)

    def test_resolve_command_bundle_rejects_duplicate_step_names(self) -> None:
        bundles = {
            "refresh-review": {
                "steps": [
                    {"entry": "refresh-env", "name": "check"},
                    {"entry": "recent-ledger", "name": "check"},
                ],
            }
        }
        entries = {
            "refresh-env": {"source": "task", "preset": "refresh-default", "description": "Refresh"},
            "recent-ledger": {"source": "report", "preset": "recent-ledger", "description": "Ledger"},
        }
        with self.assertRaisesRegex(ValueError, "duplicate step name"):
            resolve_command_bundle("refresh-review", bundles=bundles, entries=entries)

    def test_resolve_command_bundle_normalizes_labels(self) -> None:
        bundles = {
            "refresh-review": {
                "labels": ["morning", "review", "morning"],
                "steps": [
                    {"entry": "refresh-env"},
                ],
            }
        }
        entries = {
            "refresh-env": {"source": "task", "preset": "refresh-default", "description": "Refresh"},
        }
        resolved = resolve_command_bundle("refresh-review", bundles=bundles, entries=entries)
        self.assertEqual(resolved["labels"], ["morning", "review"])


class MarketApiTests(unittest.TestCase):
    def test_snapshot_delegates_to_bridge(self) -> None:
        with patch("tdxquant.api.market.run_tdx_data_snapshot") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = MarketApi(strategy_path="strategy.py")
            result = api.snapshot(stock_code="688260.SH", field_list=["Now"])
        self.assertIs(result, expected)
        mocked.assert_called_once_with(stock_code="688260.SH", field_list=["Now"], strategy_path="strategy.py")

    def test_full_tick_delegates_to_bridge(self) -> None:
        with patch("tdxquant.api.market.run_tdx_full_tick") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = MarketApi(strategy_path="strategy.py")
            result = api.full_tick(stock_code="688260.SH", field_list=["Now"])
        self.assertIs(result, expected)
        mocked.assert_called_once_with(stock_code="688260.SH", field_list=["Now"], strategy_path="strategy.py")

    def test_kline_uses_explicit_arguments(self) -> None:
        with patch("tdxquant.api.market.run_tdx_data_kline") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = MarketApi(strategy_path="strategy.py")
            result = api.kline(
                stock_list=["688260.SH"],
                period="1d",
                start_time="20250101",
                end_time="20250201",
                count=10,
                dividend_type="front",
                field_list=["close"],
                fill_data=False,
            )
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            stock_list=["688260.SH"],
            period="1d",
            start_time="20250101",
            end_time="20250201",
            count=10,
            dividend_type="front",
            field_list=["close"],
            fill_data=False,
            strategy_path="strategy.py",
        )


class MetaApiTests(unittest.TestCase):
    def test_financial_data_forwards_arguments(self) -> None:
        with patch("tdxquant.api.financial.run_tdx_financial_data") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = FinancialApi(strategy_path="strategy.py")
            result = api.financial_data(
                stock_list=["688318.SH"],
                field_list=["FN1", "FN2"],
                start_time="20240101",
                end_time="20241231",
                report_type="announce_time",
            )
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            stock_list=["688318.SH"],
            field_list=["FN1", "FN2"],
            start_time="20240101",
            end_time="20241231",
            report_type="announce_time",
            strategy_path="strategy.py",
        )

    def test_financial_data_by_date_forwards_arguments(self) -> None:
        with patch("tdxquant.api.financial.run_tdx_financial_data_by_date") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = FinancialApi(strategy_path="strategy.py")
            result = api.financial_data_by_date(
                stock_list=["688318.SH"],
                field_list=["FN193"],
                year=2025,
                mmdd=331,
            )
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            stock_list=["688318.SH"],
            field_list=["FN193"],
            year=2025,
            mmdd=331,
            strategy_path="strategy.py",
        )

    def test_stock_transaction_data_forwards_arguments(self) -> None:
        transaction_module = import_module("tdxquant.api.transaction")
        transaction_api_class = getattr(transaction_module, "TransactionApi")
        with patch("tdxquant.api.transaction.run_tdx_stock_transaction_data") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = transaction_api_class(strategy_path="strategy.py")
            result = api.stock_transaction_data(
                stock_list=["600519.SH"],
                field_list=["GP01", "GP02"],
                start_time="20240101",
                end_time="20241231",
            )
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            stock_list=["600519.SH"],
            field_list=["GP01", "GP02"],
            start_time="20240101",
            end_time="20241231",
            strategy_path="strategy.py",
        )

    def test_stock_transaction_data_by_date_forwards_zero_date_arguments(self) -> None:
        transaction_module = import_module("tdxquant.api.transaction")
        transaction_api_class = getattr(transaction_module, "TransactionApi")
        with patch("tdxquant.api.transaction.run_tdx_stock_transaction_data_by_date") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = transaction_api_class(strategy_path="strategy.py")
            result = api.stock_transaction_data_by_date(
                stock_list=["600519.SH"],
                field_list=["GP01"],
                year=0,
                mmdd=0,
            )
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            stock_list=["600519.SH"],
            field_list=["GP01"],
            year=0,
            mmdd=0,
            strategy_path="strategy.py",
        )

    def test_sector_transaction_data_forwards_arguments(self) -> None:
        transaction_module = import_module("tdxquant.api.transaction")
        transaction_api_class = getattr(transaction_module, "TransactionApi")
        with patch("tdxquant.api.transaction.run_tdx_sector_transaction_data") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = transaction_api_class(strategy_path="strategy.py")
            result = api.sector_transaction_data(
                stock_list=["880660.SH"],
                field_list=["BK5", "BK6"],
                start_time="20240101",
                end_time="20241231",
            )
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            stock_list=["880660.SH"],
            field_list=["BK5", "BK6"],
            start_time="20240101",
            end_time="20241231",
            strategy_path="strategy.py",
        )

    def test_sector_transaction_data_by_date_forwards_zero_date_arguments(self) -> None:
        transaction_module = import_module("tdxquant.api.transaction")
        transaction_api_class = getattr(transaction_module, "TransactionApi")
        with patch("tdxquant.api.transaction.run_tdx_sector_transaction_data_by_date") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = transaction_api_class(strategy_path="strategy.py")
            result = api.sector_transaction_data_by_date(
                stock_list=["880660.SH"],
                field_list=["BK9"],
                year=0,
                mmdd=0,
            )
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            stock_list=["880660.SH"],
            field_list=["BK9"],
            year=0,
            mmdd=0,
            strategy_path="strategy.py",
        )

    def test_market_transaction_data_forwards_arguments(self) -> None:
        transaction_module = import_module("tdxquant.api.transaction")
        transaction_api_class = getattr(transaction_module, "TransactionApi")
        with patch("tdxquant.api.transaction.run_tdx_market_transaction_data") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = transaction_api_class(strategy_path="strategy.py")
            result = api.market_transaction_data(
                field_list=["SC01", "SC02"],
                start_time="20250101",
                end_time="20250102",
            )
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            field_list=["SC01", "SC02"],
            start_time="20250101",
            end_time="20250102",
            strategy_path="strategy.py",
        )

    def test_market_transaction_data_by_date_forwards_zero_date_arguments(self) -> None:
        transaction_module = import_module("tdxquant.api.transaction")
        transaction_api_class = getattr(transaction_module, "TransactionApi")
        with patch("tdxquant.api.transaction.run_tdx_market_transaction_data_by_date") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = transaction_api_class(strategy_path="strategy.py")
            result = api.market_transaction_data_by_date(
                field_list=["SC06"],
                year=0,
                mmdd=0,
            )
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            field_list=["SC06"],
            year=0,
            mmdd=0,
            strategy_path="strategy.py",
        )

    def test_divid_factors_forwards_arguments(self) -> None:
        with patch("tdxquant.api.meta.run_tdx_divid_factors") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = MetaApi(strategy_path="strategy.py")
            result = api.divid_factors(stock_code="688318.SH", start_time="20200101", end_time="20241231")
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            stock_code="688318.SH",
            start_time="20200101",
            end_time="20241231",
            strategy_path="strategy.py",
        )

    def test_ipo_info_forwards_arguments(self) -> None:
        with patch("tdxquant.api.meta.run_tdx_ipo_info") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = MetaApi(strategy_path="strategy.py")
            result = api.ipo_info(ipo_type=2, ipo_date=1)
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            ipo_type=2,
            ipo_date=1,
            strategy_path="strategy.py",
        )

    def test_sector_list_forwards_list_type(self) -> None:
        with patch("tdxquant.api.meta.run_tdx_data_sector_list") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = MetaApi(strategy_path="strategy.py")
            result = api.sector_list(list_type=1)
        self.assertIs(result, expected)
        mocked.assert_called_once_with(list_type=1, strategy_path="strategy.py")

    def test_sector_stocks_forwards_list_type(self) -> None:
        with patch("tdxquant.api.meta.run_tdx_data_sector_stocks") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = MetaApi(strategy_path="strategy.py")
            result = api.sector_stocks(block_code="钛金属", block_type=0, list_type=1)
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            block_code="钛金属",
            block_type=0,
            list_type=1,
            strategy_path="strategy.py",
        )

    def test_gp_one_data_forwards_arguments(self) -> None:
        with patch("tdxquant.api.meta.run_tdx_gp_one_data") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = MetaApi(strategy_path="strategy.py")
            result = api.gp_one_data(stock_list=["688318.SH"], field_list=["GO1", "GO2"])
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            stock_list=["688318.SH"],
            field_list=["GO1", "GO2"],
            strategy_path="strategy.py",
        )


class FormulaApiTests(unittest.TestCase):
    def test_formula_zb_delegates_to_bridge(self) -> None:
        with patch("tdxquant.api.formula.run_tdx_formula_zb") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = FormulaApi(strategy_path="strategy.py")
            result = api.zb(formula_name="MACD", formula_arg="12,26,9", xsflag=2)
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            formula_name="MACD",
            formula_arg="12,26,9",
            xsflag=2,
            strategy_path="strategy.py",
        )

    def test_formula_screen_delegates_to_bridge(self) -> None:
        with patch("tdxquant.api.formula.run_tdx_formula_screen") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = FormulaApi(strategy_path="strategy.py")
            result = api.screen(
                formula_name="UPN",
                stock_list=["000001.SZ", "600519.SH"],
                formula_arg="3",
                return_count=3,
                return_date=True,
                stock_period="1d",
                start_time="20260101",
                end_time="20260201",
                count=5,
                dividend_type=1,
            )
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            formula_name="UPN",
            stock_list=["000001.SZ", "600519.SH"],
            formula_arg="3",
            return_count=3,
            return_date=True,
            stock_period="1d",
            start_time="20260101",
            end_time="20260201",
            count=5,
            dividend_type=1,
            strategy_path="strategy.py",
        )


class BlockApiTests(unittest.TestCase):
    def test_read_watchlist_snapshot_delegates_to_bridge(self) -> None:
        with patch("tdxquant.api.block.run_tdx_block_read_watchlist_snapshot") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = BlockApi(strategy_path="strategy.py")
            result = api.read_watchlist_snapshot(block_code="ZXG")
        self.assertIs(result, expected)
        mocked.assert_called_once_with(block_code="ZXG", strategy_path="strategy.py")

    def test_user_sectors_delegates_to_bridge(self) -> None:
        with patch("tdxquant.api.block.run_tdx_get_user_sector") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = BlockApi(strategy_path="strategy.py")
            result = api.user_sectors()
        self.assertIs(result, expected)
        mocked.assert_called_once_with(strategy_path="strategy.py")

    def test_create_sector_delegates_to_bridge(self) -> None:
        with patch("tdxquant.api.block.run_tdx_create_sector") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = BlockApi(strategy_path="strategy.py")
            result = api.create_sector(block_code="CSBK", block_name="测试板块")
        self.assertIs(result, expected)
        mocked.assert_called_once_with(block_code="CSBK", block_name="测试板块", strategy_path="strategy.py")

    def test_delete_sector_delegates_to_bridge(self) -> None:
        with patch("tdxquant.api.block.run_tdx_delete_sector") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = BlockApi(strategy_path="strategy.py")
            result = api.delete_sector(block_code="CSBK")
        self.assertIs(result, expected)
        mocked.assert_called_once_with(block_code="CSBK", strategy_path="strategy.py")

    def test_rename_sector_delegates_to_bridge(self) -> None:
        with patch("tdxquant.api.block.run_tdx_rename_sector") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = BlockApi(strategy_path="strategy.py")
            result = api.rename_sector(block_code="CSBK", block_name="测试板块重命名")
        self.assertIs(result, expected)
        mocked.assert_called_once_with(block_code="CSBK", block_name="测试板块重命名", strategy_path="strategy.py")

    def test_clear_sector_delegates_to_bridge(self) -> None:
        with patch("tdxquant.api.block.run_tdx_clear_sector") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = BlockApi(strategy_path="strategy.py")
            result = api.clear_sector(block_code="CSBK")
        self.assertIs(result, expected)
        mocked.assert_called_once_with(block_code="CSBK", strategy_path="strategy.py")

    def test_send_user_block_delegates_to_bridge(self) -> None:
        with patch("tdxquant.api.block.run_tdx_send_user_block") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = BlockApi(strategy_path="strategy.py")
            result = api.send_user_block(block_code="ZXG", stocks=["000001", "000002"], show=True)
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            block_code="ZXG",
            stocks=["000001", "000002"],
            show=True,
            strategy_path="strategy.py",
        )


class RuntimeApiTests(unittest.TestCase):
    def test_capabilities_delegates_to_bridge(self) -> None:
        with patch("tdxquant.api.runtime.run_tdx_provider_capabilities") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = RuntimeApi(strategy_path="strategy.py")
            result = api.capabilities()
        self.assertIs(result, expected)
        mocked.assert_called_once_with()

    def test_trading_dates_delegates_to_bridge(self) -> None:
        with patch("tdxquant.api.runtime.run_tdx_get_trading_dates") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = RuntimeApi(strategy_path="strategy.py")
            result = api.trading_dates(market="SH", start_time="20250101", end_time="20250201", count=10)
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            market="SH",
            start_time="20250101",
            end_time="20250201",
            count=10,
            strategy_path="strategy.py",
        )

    def test_refresh_kline_delegates_to_bridge(self) -> None:
        with patch("tdxquant.api.runtime.run_tdx_refresh_kline") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = RuntimeApi(strategy_path="strategy.py")
            result = api.refresh_kline(stock_list=["688260.SH"], period="1d")
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            stock_list=["688260.SH"],
            period="1d",
            strategy_path="strategy.py",
        )

    def test_download_file_delegates_to_bridge(self) -> None:
        with patch("tdxquant.api.runtime.run_tdx_download_file") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = RuntimeApi(strategy_path="strategy.py")
            result = api.download_file(stock_code="688318.SH", down_time="20250101", down_type=1)
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            stock_code="688318.SH",
            down_time="20250101",
            down_type=1,
            strategy_path="strategy.py",
        )

    def test_send_warn_delegates_to_bridge(self) -> None:
        with patch("tdxquant.api.runtime.run_tdx_send_warn") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = RuntimeApi(strategy_path="strategy.py")
            result = api.send_warn(
                stock_list=["688318.SH", "600519.SH"],
                time_list=["20251215141115", "20251215142100"],
                price_list=["123.45"],
                close_list=["122.50"],
                volume_list=["1000"],
                bs_flag_list=["0"],
                warn_type_list=["0"],
                reason_list=["价格突破预警线"],
                count=2,
            )
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            stock_list=["688318.SH", "600519.SH"],
            time_list=["20251215141115", "20251215142100"],
            price_list=["123.45"],
            close_list=["122.50"],
            volume_list=["1000"],
            bs_flag_list=["0"],
            warn_type_list=["0"],
            reason_list=["价格突破预警线"],
            count=2,
            strategy_path="strategy.py",
        )

    def test_open_subscription_session_delegates_to_bridge(self) -> None:
        bridge_session = object()
        with patch("tdxquant.api.runtime.run_tdx_open_subscription_session", return_value=bridge_session) as mocked:
            api = RuntimeApi(strategy_path="strategy.py")
            session = api.open_subscription_session()
        self.assertIs(session, bridge_session)
        mocked.assert_called_once_with(strategy_path="strategy.py")

    def test_health_delegates_to_bridge(self) -> None:
        with patch("tdxquant.api.runtime.run_tdx_provider_health") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = RuntimeApi(strategy_path="strategy.py")
            result = api.health(window_key="通达信金融终端", hid_port="COM3")
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            window_key="通达信金融终端",
            strategy_path="strategy.py",
            hid_port="COM3",
        )

    def test_doctor_delegates_to_bridge(self) -> None:
        with patch("tdxquant.api.runtime.run_tdx_provider_doctor") as mocked:
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            mocked.return_value = expected
            api = RuntimeApi(strategy_path="strategy.py")
            result = api.doctor(window_key="通达信金融终端", hid_port="COM4")
        self.assertIs(result, expected)
        mocked.assert_called_once_with(
            window_key="通达信金融终端",
            strategy_path="strategy.py",
            hid_port="COM4",
        )


class _FakeRuntimeSubscriptionSession:
    def __init__(self) -> None:
        self.session_id = "session-001"
        self.strategy_path = "strategy.py"
        self.closed = False
        self.subscribe_calls: list[tuple[list[str], object]] = []
        self.unsubscribe_calls: list[list[str]] = []
        self.list_calls = 0
        self.close_calls = 0

    def subscribe_hq(self, stock_list: list[str], callback) -> Result:
        self.subscribe_calls.append((list(stock_list), callback))
        return Result(ok=True, code=ErrorCode.OK, message="subscribed", data={})

    def unsubscribe_hq(self, stock_list: list[str]) -> Result:
        self.unsubscribe_calls.append(list(stock_list))
        return Result(ok=True, code=ErrorCode.OK, message="unsubscribed", data={})

    def get_subscribe_hq_stock_list(self) -> Result:
        self.list_calls += 1
        return Result(ok=True, code=ErrorCode.OK, message="listed", data={})

    def close(self) -> None:
        self.close_calls += 1
        self.closed = True


class _FakeTaskRuntimeSubscriptionSession:
    def __init__(self, *, events: list[object] | None = None) -> None:
        self.session_id = "provider-session-001"
        self.strategy_path = "strategy.py"
        self.closed = False
        self.subscribe_calls: list[tuple[list[str], object]] = []
        self.unsubscribe_calls: list[list[str]] = []
        self.close_calls = 0
        self._events = list(events or [])

    def subscribe_hq(self, stock_list: list[str], callback) -> Result:
        self.subscribe_calls.append((list(stock_list), callback))
        for event in self._events:
            callback(event)
        return Result(ok=True, code=ErrorCode.OK, message="subscribed", data={"registered": len(stock_list)})

    def unsubscribe_hq(self, stock_list: list[str]) -> Result:
        self.unsubscribe_calls.append(list(stock_list))
        return Result(ok=True, code=ErrorCode.OK, message="unsubscribed", data={"removed": len(stock_list)})

    def close(self) -> None:
        self.close_calls += 1
        self.closed = True


class TdxApiManagerTests(unittest.TestCase):
    def test_run_tdx_block_read_watchlist_snapshot_normalizes_custom_sector_members(self) -> None:
        bridge = import_module("tdxquant.api.bridge")
        sectors_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={"result": [{"Code": "ZXG", "Name": "自选股"}]},
        )
        stocks_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={"result": ["600519.SH", "000001.SZ", "600519.SH"]},
            warnings=["raw-warning"],
        )
        with (
            patch.object(bridge, "run_tdx_get_user_sector", return_value=sectors_result) as mocked_sectors,
            patch.object(bridge, "run_tdx_data_sector_stocks", return_value=stocks_result) as mocked_stocks,
        ):
            result = bridge.run_tdx_block_read_watchlist_snapshot(block_code="ZXG", strategy_path="strategy.py")
        mocked_sectors.assert_called_once_with(strategy_path="strategy.py")
        mocked_stocks.assert_called_once_with(
            block_code="ZXG",
            block_type=1,
            list_type=0,
            strategy_path="strategy.py",
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.data["snapshot"]["block_code"], "ZXG")
        self.assertEqual(result.data["snapshot"]["symbols"], ["600519.SH", "000001.SZ"])
        self.assertEqual(result.data["snapshot"]["source_metadata"]["sector_name"], "自选股")
        self.assertEqual(result.data["snapshot"]["source_metadata"]["raw_member_count"], 3)
        self.assertEqual(result.warnings, ["raw-warning", "Deduplicated 1 repeated members in block ZXG"])

    def test_run_tdx_block_read_watchlist_snapshot_returns_invalid_request_for_missing_block(self) -> None:
        bridge = import_module("tdxquant.api.bridge")
        sectors_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={"result": [{"Code": "ABCD", "Name": "其他板块"}]},
        )
        with (
            patch.object(bridge, "run_tdx_get_user_sector", return_value=sectors_result) as mocked_sectors,
            patch.object(bridge, "run_tdx_data_sector_stocks") as mocked_stocks,
        ):
            result = bridge.run_tdx_block_read_watchlist_snapshot(block_code="ZXG", strategy_path="strategy.py")
        mocked_sectors.assert_called_once_with(strategy_path="strategy.py")
        mocked_stocks.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(result.message, "block_code not found: ZXG")

    def test_run_tdx_block_read_watchlist_snapshot_returns_empty_snapshot_for_empty_block(self) -> None:
        bridge = import_module("tdxquant.api.bridge")
        sectors_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={"result": [{"Code": "ZXG", "Name": "空板块"}]},
        )
        stocks_result = Result(ok=True, code=ErrorCode.OK, message="ok", data={"result": []})
        with (
            patch.object(bridge, "run_tdx_get_user_sector", return_value=sectors_result),
            patch.object(bridge, "run_tdx_data_sector_stocks", return_value=stocks_result),
        ):
            result = bridge.run_tdx_block_read_watchlist_snapshot(block_code="ZXG", strategy_path="strategy.py")
        self.assertTrue(result.ok)
        self.assertEqual(result.code, ErrorCode.OK)
        self.assertEqual(result.data["snapshot"]["symbols"], [])
        self.assertEqual(result.data["snapshot"]["symbol_count"], 0)
        self.assertEqual(result.data["snapshot"]["source_metadata"]["sector_name"], "空板块")

    def test_run_tdx_block_read_watchlist_snapshot_preserves_explicit_bj_suffix(self) -> None:
        bridge = import_module("tdxquant.api.bridge")
        sectors_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={"result": [{"Code": "ZXG", "Name": "北交所板块"}]},
        )
        stocks_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={"result": ["430001.BJ", "920001.BJ", "430001.BJ"]},
        )
        with (
            patch.object(bridge, "run_tdx_get_user_sector", return_value=sectors_result),
            patch.object(bridge, "run_tdx_data_sector_stocks", return_value=stocks_result),
        ):
            result = bridge.run_tdx_block_read_watchlist_snapshot(block_code="ZXG", strategy_path="strategy.py")
        self.assertTrue(result.ok)
        self.assertEqual(result.data["snapshot"]["symbols"], ["430001.BJ", "920001.BJ"])
        self.assertEqual(result.data["snapshot"]["source_metadata"]["duplicate_count"], 1)

    def test_public_import_is_available(self) -> None:
        manager = TdxApiManager(profile="default")
        self.assertEqual(manager.profile_name, "default")

    def test_manager_formula_screen_replay_mode_uses_default_fixture_without_live_call(self) -> None:
        live_result = Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message="live formula screen should not run in replay mode",
        )
        manager = TdxApiManager(profile="default", provider_mode="replay")
        with patch.object(type(manager._formula_api), "screen", return_value=live_result) as mocked_screen:
            result = manager.formula.screen(
                formula_name="UPN",
                stock_list=["000001.SZ"],
                formula_arg="3",
            )
        self.assertTrue(result.ok)
        self.assertEqual(result.message, "screened formula matches")
        self.assertEqual(result.data["matched_symbols"], ["000001.SZ"])
        self.assertEqual(result.data["manager"]["method"], "screen")
        mocked_screen.assert_not_called()

    def test_manager_replay_mode_rejects_unsupported_capability_without_live_fallback(self) -> None:
        live_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="live snapshot should not run in replay mode",
            data={"rows": [{"symbol": "688260.SH"}]},
        )
        manager = TdxApiManager(profile="default", provider_mode="replay")
        with patch.object(type(manager._market_api), "snapshot", return_value=live_result) as mocked_snapshot:
            result = manager.market.snapshot("688260.SH")
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertIn("unsupported", result.message)
        mocked_snapshot.assert_not_called()

    def test_manager_formula_screen_replay_mode_accepts_explicit_fixture_path(self) -> None:
        fixture_payload = load_provider_replay_fixture("formula-screen-failure")
        with TemporaryDirectory() as temp_dir:
            fixture_path = Path(temp_dir) / "formula-screen-failure.json"
            fixture_path.write_text(json.dumps(fixture_payload, ensure_ascii=False), encoding="utf-8")
            live_result = Result(ok=True, code=ErrorCode.OK, message="live formula screen should not run")
            manager = TdxApiManager(
                profile="default",
                provider_mode="replay",
                replay_fixture_path=str(fixture_path),
            )
            with patch.object(type(manager._formula_api), "screen", return_value=live_result) as mocked_screen:
                result = manager.formula.screen(
                    formula_name="UPN",
                    stock_list=["000001.SZ"],
                )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(result.message, "formula argument is invalid")
        self.assertEqual(result.data["manager"]["method"], "screen")
        mocked_screen.assert_not_called()

    def test_manager_snapshot_uses_provider_result_envelope(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"rows": [{"symbol": "688260.SH"}]})
        with patch("tdxquant.api.market.run_tdx_data_snapshot", return_value=expected):
            manager = TdxApiManager(profile="brief", strategy_path="strategy.py")
            result = manager.market.snapshot("688260.SH")
        payload = result.to_dict()
        self.assertIn("success", payload)
        self.assertIn("ok", payload)
        self.assertTrue(payload["success"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["capability"], "market.snapshot")
        self.assertIn("capability_version", payload)
        self.assertIn("schema_version", payload)
        self.assertIn("started_at", payload)
        self.assertIn("finished_at", payload)
        self.assertIn("elapsed_ms", payload)
        self.assertIn("runtime", payload)
        self.assertEqual(payload["runtime"]["provider"], "tdxquant")
        self.assertEqual(payload["runtime"]["mode"], "manager")
        self.assertEqual(payload["data"]["rows"], [{"symbol": "688260.SH"}])
        self.assertEqual(payload["data"]["api_profile"]["name"], "brief")
        self.assertEqual(payload["data"]["manager"]["method"], "snapshot")
        self.assertIsInstance(payload["warnings"], list)
        self.assertIsInstance(payload["data"], dict)
        self.assertEqual(payload["artifacts"], [])

    def test_manager_snapshot_failure_uses_provider_result_envelope(self) -> None:
        expected = Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message="snapshot failed",
            data={},
            warnings=["probe-warning"],
            next_action="retry",
        )
        with patch("tdxquant.api.market.run_tdx_data_snapshot", return_value=expected):
            manager = TdxApiManager(profile="brief", strategy_path="strategy.py")
            result = manager.market.snapshot("688260.SH")
        payload = result.to_dict()
        self.assertFalse(payload["success"])
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["code"], ErrorCode.EXECUTION_FAILED.value)
        self.assertEqual(payload["message"], "snapshot failed")
        self.assertEqual(payload["warnings"], ["probe-warning"])
        self.assertEqual(payload["data"]["next_action"], "retry")
        self.assertEqual(payload["capability"], "market.snapshot")
        self.assertEqual(payload["runtime"]["mode"], "manager")

    def test_manager_runtime_health_envelope_preserves_diagnostic_success_semantics(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"overall_status": "unavailable", "checks": {}})
        with patch("tdxquant.api.runtime.run_tdx_provider_health", return_value=expected):
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.runtime.health(window_key="平安证券")
        payload = result.to_dict()
        self.assertTrue(payload["success"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["capability"], "runtime.health")
        self.assertEqual(payload["data"]["overall_status"], "unavailable")
        self.assertIsInstance(payload["warnings"], list)
        self.assertIsInstance(payload["artifacts"], list)

    def test_manager_snapshot_attaches_metadata(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.market.run_tdx_data_snapshot", return_value=expected):
            manager = TdxApiManager(profile="brief", strategy_path="strategy.py")
            result = manager.market.snapshot("688260.SH")
        self.assertEqual(result.data["api_profile"]["name"], "brief")
        self.assertEqual(result.data["manager"]["domain"], "market")
        self.assertEqual(result.data["manager"]["method"], "snapshot")
        self.assertEqual(result.data["api_profile"]["options"]["field_list"], ["Now", "Volume"])
        self.assertIn("manager_call", result.data["timing"])

    def test_manager_full_tick_attaches_metadata(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.market.run_tdx_full_tick", return_value=expected):
            manager = TdxApiManager(profile="brief", strategy_path="strategy.py")
            result = manager.market.full_tick("688260.SH")
        self.assertEqual(result.data["api_profile"]["name"], "brief")
        self.assertEqual(result.data["manager"]["domain"], "market")
        self.assertEqual(result.data["manager"]["method"], "full_tick")
        self.assertEqual(result.data["api_profile"]["options"]["field_list"], ["Now", "Volume"])
        self.assertIn("manager_call", result.data["timing"])

    def test_manager_kline_explicit_arguments_override_profile_defaults(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.market.run_tdx_data_kline", return_value=expected) as mocked:
            manager = TdxApiManager(profile="research", strategy_path="strategy.py")
            result = manager.market.kline(
                stock_list=["688260.SH"],
                period="1d",
                dividend_type="back",
                fields=["close"],
                fill_data=False,
            )
        mocked.assert_called_once()
        self.assertEqual(result.data["api_profile"]["options"]["field_list"], ["close"])
        self.assertEqual(result.data["api_profile"]["options"]["kline_dividend_type"], "back")
        self.assertFalse(result.data["api_profile"]["options"]["kline_fill_data"])

    def test_manager_meta_list_type_uses_profile_default(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.meta.run_tdx_stock_list", return_value=expected) as mocked:
            manager = TdxApiManager(profile="named_list", strategy_path="strategy.py")
            result = manager.meta.stock_list(market="16")
        mocked.assert_called_once_with(market="16", list_type=1, strategy_path="strategy.py")
        self.assertEqual(result.data["api_profile"]["options"]["list_type"], 1)

    def test_manager_meta_divid_factors_attaches_metadata(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.meta.run_tdx_divid_factors", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.meta.divid_factors(stock_code="688318.SH", start_time="20200101", end_time="20241231")
        mocked.assert_called_once_with(
            stock_code="688318.SH",
            start_time="20200101",
            end_time="20241231",
            strategy_path="strategy.py",
        )
        self.assertEqual(result.data["manager"]["domain"], "meta")
        self.assertEqual(result.data["manager"]["method"], "divid_factors")
        self.assertEqual(result.data["api_profile"]["options"]["stock_code"], "688318.SH")
        self.assertEqual(result.data["api_profile"]["options"]["start_time"], "20200101")
        self.assertEqual(result.data["api_profile"]["options"]["end_time"], "20241231")

    def test_manager_meta_ipo_info_attaches_metadata(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.meta.run_tdx_ipo_info", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.meta.ipo_info(ipo_type=2, ipo_date=1)
        mocked.assert_called_once_with(ipo_type=2, ipo_date=1, strategy_path="strategy.py")
        self.assertEqual(result.data["manager"]["domain"], "meta")
        self.assertEqual(result.data["manager"]["method"], "ipo_info")
        self.assertEqual(result.data["api_profile"]["options"]["ipo_type"], 2)
        self.assertEqual(result.data["api_profile"]["options"]["ipo_date"], 1)

    def test_manager_financial_data_attaches_metadata_and_uses_explicit_fields(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.financial.run_tdx_financial_data", return_value=expected) as mocked:
            manager = TdxApiManager(
                profile="default",
                strategy_path="strategy.py",
                profile_overrides={"default_fields": {"financial_data": ["SHOULD_NOT_USE"]}},
            )
            result = manager.financial.financial_data(
                stock_list=["688318.SH"],
                fields=["FN1", "FN2"],
                start_time="20240101",
                end_time="20241231",
                report_type="announce_time",
            )
        mocked.assert_called_once_with(
            stock_list=["688318.SH"],
            field_list=["FN1", "FN2"],
            start_time="20240101",
            end_time="20241231",
            report_type="announce_time",
            strategy_path="strategy.py",
        )
        self.assertEqual(result.data["manager"]["domain"], "financial")
        self.assertEqual(result.data["manager"]["method"], "financial_data")
        self.assertEqual(result.data["api_profile"]["options"]["field_list"], ["FN1", "FN2"])
        self.assertEqual(result.data["api_profile"]["options"]["report_type"], "announce_time")
        self.assertIn("manager_call", result.data["timing"])

    def test_manager_financial_data_by_date_attaches_metadata(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.financial.run_tdx_financial_data_by_date", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.financial.financial_data_by_date(
                stock_list=["688318.SH"],
                fields=["FN193"],
                year=2025,
                mmdd=331,
            )
        mocked.assert_called_once_with(
            stock_list=["688318.SH"],
            field_list=["FN193"],
            year=2025,
            mmdd=331,
            strategy_path="strategy.py",
        )
        self.assertEqual(result.data["manager"]["domain"], "financial")
        self.assertEqual(result.data["manager"]["method"], "financial_data_by_date")
        self.assertEqual(result.data["api_profile"]["options"]["field_list"], ["FN193"])
        self.assertEqual(result.data["api_profile"]["options"]["year"], 2025)
        self.assertEqual(result.data["api_profile"]["options"]["mmdd"], 331)
        self.assertIn("manager_call", result.data["timing"])

    def test_manager_stock_transaction_data_attaches_metadata_and_uses_explicit_fields(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.transaction.run_tdx_stock_transaction_data", return_value=expected) as mocked:
            manager = TdxApiManager(
                profile="default",
                strategy_path="strategy.py",
                profile_overrides={"default_fields": {"stock_transaction_data": ["SHOULD_NOT_USE"]}},
            )
            result = manager.transaction.stock_transaction_data(
                stock_list=["600519.SH"],
                fields=["GP01", "GP02"],
                start_time="20240101",
                end_time="20241231",
            )
        mocked.assert_called_once_with(
            stock_list=["600519.SH"],
            field_list=["GP01", "GP02"],
            start_time="20240101",
            end_time="20241231",
            strategy_path="strategy.py",
        )
        self.assertEqual(result.data["manager"]["domain"], "transaction")
        self.assertEqual(result.data["manager"]["method"], "stock_transaction_data")
        self.assertEqual(result.data["api_profile"]["options"]["field_list"], ["GP01", "GP02"])
        self.assertEqual(result.data["api_profile"]["options"]["start_time"], "20240101")
        self.assertEqual(result.data["api_profile"]["options"]["end_time"], "20241231")
        self.assertIn("manager_call", result.data["timing"])

    def test_manager_stock_transaction_data_by_date_preserves_zero_date_metadata(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.transaction.run_tdx_stock_transaction_data_by_date", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.transaction.stock_transaction_data_by_date(
                stock_list=["600519.SH"],
                fields=["GP01"],
                year=0,
                mmdd=0,
            )
        mocked.assert_called_once_with(
            stock_list=["600519.SH"],
            field_list=["GP01"],
            year=0,
            mmdd=0,
            strategy_path="strategy.py",
        )
        self.assertEqual(result.data["manager"]["domain"], "transaction")
        self.assertEqual(result.data["manager"]["method"], "stock_transaction_data_by_date")
        self.assertEqual(result.data["api_profile"]["options"]["field_list"], ["GP01"])
        self.assertEqual(result.data["api_profile"]["options"]["year"], 0)
        self.assertEqual(result.data["api_profile"]["options"]["mmdd"], 0)
        self.assertIn("manager_call", result.data["timing"])

    def test_manager_sector_transaction_data_attaches_metadata_and_uses_explicit_fields(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.transaction.run_tdx_sector_transaction_data", return_value=expected) as mocked:
            manager = TdxApiManager(
                profile="default",
                strategy_path="strategy.py",
                profile_overrides={"default_fields": {"sector_transaction_data": ["SHOULD_NOT_USE"]}},
            )
            result = manager.transaction.sector_transaction_data(
                stock_list=["880660.SH"],
                fields=["BK5", "BK6"],
                start_time="20240101",
                end_time="20241231",
            )
        mocked.assert_called_once_with(
            stock_list=["880660.SH"],
            field_list=["BK5", "BK6"],
            start_time="20240101",
            end_time="20241231",
            strategy_path="strategy.py",
        )
        self.assertEqual(result.data["manager"]["domain"], "transaction")
        self.assertEqual(result.data["manager"]["method"], "sector_transaction_data")
        self.assertEqual(result.data["api_profile"]["options"]["field_list"], ["BK5", "BK6"])
        self.assertEqual(result.data["api_profile"]["options"]["start_time"], "20240101")
        self.assertEqual(result.data["api_profile"]["options"]["end_time"], "20241231")
        self.assertIn("manager_call", result.data["timing"])

    def test_manager_sector_transaction_data_by_date_preserves_zero_date_metadata(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.transaction.run_tdx_sector_transaction_data_by_date", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.transaction.sector_transaction_data_by_date(
                stock_list=["880660.SH"],
                fields=["BK9"],
                year=0,
                mmdd=0,
            )
        mocked.assert_called_once_with(
            stock_list=["880660.SH"],
            field_list=["BK9"],
            year=0,
            mmdd=0,
            strategy_path="strategy.py",
        )
        self.assertEqual(result.data["manager"]["domain"], "transaction")
        self.assertEqual(result.data["manager"]["method"], "sector_transaction_data_by_date")
        self.assertEqual(result.data["api_profile"]["options"]["field_list"], ["BK9"])
        self.assertEqual(result.data["api_profile"]["options"]["year"], 0)
        self.assertEqual(result.data["api_profile"]["options"]["mmdd"], 0)
        self.assertIn("manager_call", result.data["timing"])

    def test_manager_market_transaction_data_attaches_metadata_and_uses_explicit_fields(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.transaction.run_tdx_market_transaction_data", return_value=expected) as mocked:
            manager = TdxApiManager(
                profile="default",
                strategy_path="strategy.py",
                profile_overrides={"default_fields": {"market_transaction_data": ["SHOULD_NOT_USE"]}},
            )
            result = manager.transaction.market_transaction_data(
                fields=["SC01", "SC02"],
                start_time="20250101",
                end_time="20250102",
            )
        mocked.assert_called_once_with(
            field_list=["SC01", "SC02"],
            start_time="20250101",
            end_time="20250102",
            strategy_path="strategy.py",
        )
        self.assertEqual(result.data["manager"]["domain"], "transaction")
        self.assertEqual(result.data["manager"]["method"], "market_transaction_data")
        self.assertEqual(result.data["api_profile"]["options"]["field_list"], ["SC01", "SC02"])
        self.assertEqual(result.data["api_profile"]["options"]["start_time"], "20250101")
        self.assertEqual(result.data["api_profile"]["options"]["end_time"], "20250102")
        self.assertIn("manager_call", result.data["timing"])

    def test_manager_market_transaction_data_by_date_preserves_zero_date_metadata(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.transaction.run_tdx_market_transaction_data_by_date", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.transaction.market_transaction_data_by_date(
                fields=["SC06"],
                year=0,
                mmdd=0,
            )
        mocked.assert_called_once_with(
            field_list=["SC06"],
            year=0,
            mmdd=0,
            strategy_path="strategy.py",
        )
        self.assertEqual(result.data["manager"]["domain"], "transaction")
        self.assertEqual(result.data["manager"]["method"], "market_transaction_data_by_date")
        self.assertEqual(result.data["api_profile"]["options"]["field_list"], ["SC06"])
        self.assertEqual(result.data["api_profile"]["options"]["year"], 0)
        self.assertEqual(result.data["api_profile"]["options"]["mmdd"], 0)
        self.assertIn("manager_call", result.data["timing"])

    def test_refresh_cache_is_manager_level_action(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.manager.run_tdx_refresh_cache", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.refresh_cache()
        mocked.assert_called_once_with(market="AG", force=False, strategy_path="strategy.py")
        self.assertEqual(result.data["manager"]["domain"], "manager")
        self.assertEqual(result.data["manager"]["method"], "refresh_cache")

    def test_manager_runtime_trading_dates_uses_profile_defaults(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.runtime.run_tdx_get_trading_dates", return_value=expected) as mocked:
            manager = TdxApiManager(
                profile="default",
                strategy_path="strategy.py",
                profile_overrides={"trading_dates_market": "SH", "trading_dates_count": 5},
            )
            result = manager.runtime.trading_dates()
        mocked.assert_called_once_with(
            market="SH",
            start_time="",
            end_time="",
            count=5,
            strategy_path="strategy.py",
        )
        self.assertEqual(result.data["manager"]["domain"], "runtime")
        self.assertEqual(result.data["manager"]["method"], "trading_dates")
        self.assertEqual(result.data["api_profile"]["options"]["trading_dates_market"], "SH")
        self.assertEqual(result.data["api_profile"]["options"]["trading_dates_count"], 5)

    def test_manager_runtime_refresh_kline_attaches_metadata(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.runtime.run_tdx_refresh_kline", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.runtime.refresh_kline(stock_list=["688260.SH"], period="1d")
        mocked.assert_called_once_with(
            stock_list=["688260.SH"],
            period="1d",
            strategy_path="strategy.py",
        )
        self.assertEqual(result.data["manager"]["domain"], "runtime")
        self.assertEqual(result.data["manager"]["method"], "refresh_kline")
        self.assertEqual(result.data["api_profile"]["options"]["stock_list"], ["688260.SH"])
        self.assertEqual(result.data["api_profile"]["options"]["period"], "1d")

    def test_manager_runtime_download_file_attaches_metadata(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.runtime.run_tdx_download_file", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.runtime.download_file(stock_code="688318.SH", down_time="20250101", down_type=2)
        mocked.assert_called_once_with(
            stock_code="688318.SH",
            down_time="20250101",
            down_type=2,
            strategy_path="strategy.py",
        )
        self.assertEqual(result.data["manager"]["domain"], "runtime")
        self.assertEqual(result.data["manager"]["method"], "download_file")
        self.assertEqual(result.data["api_profile"]["options"]["stock_code"], "688318.SH")
        self.assertEqual(result.data["api_profile"]["options"]["down_time"], "20250101")
        self.assertEqual(result.data["api_profile"]["options"]["down_type"], 2)

    def test_manager_runtime_capabilities_attaches_metadata(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "capabilities": [],
                "summary": {"total": 0, "by_domain": {}, "by_stability": {}, "by_side_effect_level": {}},
                "grading": {"stability_levels": [], "side_effect_levels": []},
            },
        )
        with patch("tdxquant.api.runtime.run_tdx_provider_capabilities", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.runtime.capabilities()
        mocked.assert_called_once_with()
        self.assertEqual(result.data["manager"]["domain"], "runtime")
        self.assertEqual(result.data["manager"]["method"], "capabilities")
        self.assertEqual(result.data["api_profile"]["name"], "default")
        self.assertIn("manager_call", result.data["timing"])
        payload = result.to_dict()
        self.assertTrue(payload["success"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["capability"], "runtime.capabilities")
        self.assertIn("summary", payload["data"])
        self.assertIn("grading", payload["data"])

    def test_manager_runtime_health_attaches_metadata_and_forwards_probe_args(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "overall_status": "degraded",
                "checks": {},
                "recommended_actions": ["retry query runtime"],
                "recommended_action_items": [
                    {
                        "id": "query_runtime",
                        "summary": "retry query runtime",
                        "severity": "error",
                        "related_checks": ["query_runtime"],
                    }
                ],
            },
        )
        with patch("tdxquant.api.runtime.run_tdx_provider_health", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.runtime.health(window_key="平安证券", hid_port="COM3")
        mocked.assert_called_once_with(
            window_key="平安证券",
            strategy_path="strategy.py",
            hid_port="COM3",
        )
        self.assertEqual(result.data["manager"]["domain"], "runtime")
        self.assertEqual(result.data["manager"]["method"], "health")
        self.assertEqual(result.data["api_profile"]["options"]["window_key"], "平安证券")
        self.assertEqual(result.data["api_profile"]["options"]["hid_port"], "COM3")
        self.assertEqual(result.data["overall_status"], "degraded")
        self.assertIn("recommended_action_items", result.data)

    def test_manager_runtime_doctor_attaches_metadata_and_forwards_probe_args(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "overall_status": "unavailable",
                "findings": [
                    {
                        "id": "query_runtime",
                        "severity": "error",
                        "status": "failed",
                        "summary": "runtime failed",
                        "critical": True,
                        "related_checks": ["query_runtime"],
                        "recommended_action_id": "query_runtime",
                    }
                ],
                "recommended_action_items": [
                    {
                        "id": "query_runtime",
                        "summary": "restart runtime",
                        "severity": "error",
                        "related_checks": ["query_runtime"],
                    }
                ],
            },
        )
        with patch("tdxquant.api.runtime.run_tdx_provider_doctor", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.runtime.doctor(window_key="通达信金融终端", hid_port="COM9")
        mocked.assert_called_once_with(
            window_key="通达信金融终端",
            strategy_path="strategy.py",
            hid_port="COM9",
        )
        self.assertEqual(result.data["manager"]["domain"], "runtime")
        self.assertEqual(result.data["manager"]["method"], "doctor")
        self.assertEqual(result.data["api_profile"]["options"]["window_key"], "通达信金融终端")
        self.assertEqual(result.data["api_profile"]["options"]["hid_port"], "COM9")
        self.assertEqual(result.data["overall_status"], "unavailable")
        payload = result.to_dict()
        self.assertTrue(payload["success"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["capability"], "runtime.doctor")
        self.assertIn("recommended_action_items", payload["data"])
        self.assertIn("recommended_action_id", payload["data"]["findings"][0])

    def test_manager_runtime_send_warn_attaches_metadata_and_preserves_count(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.runtime.run_tdx_send_warn", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.runtime.send_warn(
                stock_list=["688318.SH", "600519.SH"],
                time_list=["20251215141115", "20251215142100"],
                price_list=["123.45"],
                close_list=["122.50"],
                volume_list=["1000"],
                bs_flag_list=["0"],
                warn_type_list=["0"],
                reason_list=["价格突破预警线"],
                count=2,
            )
        mocked.assert_called_once_with(
            stock_list=["688318.SH", "600519.SH"],
            time_list=["20251215141115", "20251215142100"],
            price_list=["123.45"],
            close_list=["122.50"],
            volume_list=["1000"],
            bs_flag_list=["0"],
            warn_type_list=["0"],
            reason_list=["价格突破预警线"],
            count=2,
            strategy_path="strategy.py",
        )
        self.assertEqual(result.data["manager"]["domain"], "runtime")
        self.assertEqual(result.data["manager"]["method"], "send_warn")
        self.assertEqual(result.data["api_profile"]["options"]["stock_list"], ["688318.SH", "600519.SH"])
        self.assertEqual(result.data["api_profile"]["options"]["time_list"], ["20251215141115", "20251215142100"])
        self.assertEqual(result.data["api_profile"]["options"]["price_list"], ["123.45"])
        self.assertEqual(result.data["api_profile"]["options"]["close_list"], ["122.50"])
        self.assertEqual(result.data["api_profile"]["options"]["volume_list"], ["1000"])
        self.assertEqual(result.data["api_profile"]["options"]["bs_flag_list"], ["0"])
        self.assertEqual(result.data["api_profile"]["options"]["warn_type_list"], ["0"])
        self.assertEqual(result.data["api_profile"]["options"]["reason_list"], ["价格突破预警线"])
        self.assertEqual(result.data["api_profile"]["options"]["count"], 2)

    def test_manager_runtime_open_subscription_session_returns_session_wrapper(self) -> None:
        raw_session = _FakeRuntimeSubscriptionSession()
        with patch("tdxquant.api.runtime.run_tdx_open_subscription_session", return_value=raw_session) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            session = manager.runtime.open_subscription_session()
        mocked.assert_called_once_with(strategy_path="strategy.py")
        self.assertEqual(session.session_id, "session-001")

    def test_manager_runtime_subscription_session_attaches_metadata(self) -> None:
        raw_session = _FakeRuntimeSubscriptionSession()
        callback = object()
        with patch("tdxquant.api.runtime.run_tdx_open_subscription_session", return_value=raw_session):
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            session = manager.runtime.open_subscription_session()
            subscribe_result = session.subscribe_hq(stock_list=["688318.SH"], callback=callback)
            list_result = session.get_subscribe_hq_stock_list()
            unsubscribe_result = session.unsubscribe_hq(stock_list=["688318.SH"])

        self.assertEqual(raw_session.subscribe_calls, [(["688318.SH"], callback)])
        self.assertEqual(raw_session.list_calls, 1)
        self.assertEqual(raw_session.unsubscribe_calls, [["688318.SH"]])

        self.assertEqual(subscribe_result.data["manager"]["domain"], "runtime")
        self.assertEqual(subscribe_result.data["manager"]["method"], "subscribe_hq")
        self.assertEqual(subscribe_result.data["runtime_session"]["session_id"], "session-001")
        self.assertEqual(subscribe_result.data["api_profile"]["options"]["stock_list"], ["688318.SH"])
        self.assertIn("manager_call", subscribe_result.data["timing"])

        self.assertEqual(list_result.data["manager"]["method"], "get_subscribe_hq_stock_list")
        self.assertEqual(list_result.data["runtime_session"]["session_id"], "session-001")
        self.assertEqual(list_result.data["api_profile"]["options"]["session_id"], "session-001")

        self.assertEqual(unsubscribe_result.data["manager"]["method"], "unsubscribe_hq")
        self.assertEqual(unsubscribe_result.data["runtime_session"]["session_id"], "session-001")
        self.assertEqual(unsubscribe_result.data["api_profile"]["options"]["stock_list"], ["688318.SH"])

    def test_manager_formula_attaches_metadata(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.formula.run_tdx_formula_xg", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.formula.xg("MY_FORMULA", "A")
        mocked.assert_called_once_with(formula_name="MY_FORMULA", formula_arg="A", strategy_path="strategy.py")
        self.assertEqual(result.data["manager"]["domain"], "formula")
        self.assertEqual(result.data["manager"]["method"], "xg")

    def test_manager_formula_screen_attaches_metadata(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={"matched_symbols": ["600519.SH"], "rows": []},
        )
        with patch("tdxquant.api.formula.run_tdx_formula_screen", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.formula.screen(
                formula_name="UPN",
                stock_list=["000001.SZ", "600519.SH"],
                formula_arg="3",
                return_count=2,
                return_date=True,
                count=5,
                dividend_type=1,
            )
        mocked.assert_called_once_with(
            formula_name="UPN",
            stock_list=["000001.SZ", "600519.SH"],
            formula_arg="3",
            return_count=2,
            return_date=True,
            stock_period="1d",
            start_time="",
            end_time="",
            count=5,
            dividend_type=1,
            strategy_path="strategy.py",
        )
        self.assertEqual(result.data["manager"]["domain"], "formula")
        self.assertEqual(result.data["manager"]["method"], "screen")
        self.assertEqual(result.data["matched_symbols"], ["600519.SH"])

    def test_manager_block_attaches_metadata(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.block.run_tdx_send_user_block", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.block.send_user_block("ZXG", ["000001"], show=False)
        mocked.assert_called_once_with(block_code="ZXG", stocks=["000001"], show=False, strategy_path="strategy.py")
        self.assertEqual(result.data["manager"]["domain"], "block")
        self.assertEqual(result.data["manager"]["method"], "send_user_block")

    def test_manager_block_user_sectors_attaches_metadata(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.block.run_tdx_get_user_sector", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.block.user_sectors()
        mocked.assert_called_once_with(strategy_path="strategy.py")
        self.assertEqual(result.data["manager"]["domain"], "block")
        self.assertEqual(result.data["manager"]["method"], "user_sectors")

    def test_manager_block_create_sector_attaches_metadata(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.block.run_tdx_create_sector", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.block.create_sector("CSBK", "测试板块")
        mocked.assert_called_once_with(block_code="CSBK", block_name="测试板块", strategy_path="strategy.py")
        self.assertEqual(result.data["manager"]["domain"], "block")
        self.assertEqual(result.data["manager"]["method"], "create_sector")
        self.assertEqual(result.data["api_profile"]["options"]["block_code"], "CSBK")
        self.assertEqual(result.data["api_profile"]["options"]["block_name"], "测试板块")

    def test_manager_block_delete_sector_attaches_metadata(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.block.run_tdx_delete_sector", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.block.delete_sector("CSBK")
        mocked.assert_called_once_with(block_code="CSBK", strategy_path="strategy.py")
        self.assertEqual(result.data["manager"]["method"], "delete_sector")
        self.assertEqual(result.data["api_profile"]["options"]["block_code"], "CSBK")

    def test_manager_block_rename_sector_attaches_metadata(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.block.run_tdx_rename_sector", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.block.rename_sector("CSBK", "测试板块重命名")
        mocked.assert_called_once_with(block_code="CSBK", block_name="测试板块重命名", strategy_path="strategy.py")
        self.assertEqual(result.data["manager"]["method"], "rename_sector")
        self.assertEqual(result.data["api_profile"]["options"]["block_name"], "测试板块重命名")

    def test_manager_block_clear_sector_attaches_metadata(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.block.run_tdx_clear_sector", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.block.clear_sector("CSBK")
        mocked.assert_called_once_with(block_code="CSBK", strategy_path="strategy.py")
        self.assertEqual(result.data["manager"]["method"], "clear_sector")
        self.assertEqual(result.data["api_profile"]["options"]["block_code"], "CSBK")

    def test_manager_block_create_sector_preserves_mutation_summary_and_provider_artifacts(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="created",
            data={
                "block_mutation": {
                    "schema_version": "2026-04-28",
                    "mutation_id": "mut-001",
                    "mutation_key": "mk-001",
                    "operation": "create_sector",
                    "status": "applied",
                    "block_code": "CSBK",
                    "block_name": "测试板块",
                },
                "artifacts": {
                    "audit_log_path": "runtime/block-mutations/mut-001.json",
                },
            },
        )
        expected._provider_artifacts = [
            {
                "kind": "block_mutation_audit",
                "path": "runtime/block-mutations/mut-001.json",
            }
        ]
        with patch("tdxquant.api.block.run_tdx_create_sector", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.block.create_sector(
                "CSBK",
                "测试板块",
                mutation_key="mk-001",
                audit_dir="runtime/block-mutations",
            )
        mocked.assert_called_once_with(
            block_code="CSBK",
            block_name="测试板块",
            mutation_key="mk-001",
            audit_dir="runtime/block-mutations",
            strategy_path="strategy.py",
        )
        payload = result.to_dict()
        self.assertEqual(payload["data"]["block_mutation"]["mutation_key"], "mk-001")
        self.assertEqual(payload["data"]["artifacts"]["audit_log_path"], "runtime/block-mutations/mut-001.json")
        self.assertEqual(payload["artifacts"][0]["kind"], "block_mutation_audit")
        self.assertEqual(payload["artifacts"][0]["path"], "runtime/block-mutations/mut-001.json")

    def test_manager_block_send_user_block_forwards_mutation_safety_options(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="updated",
            data={
                "block_mutation": {
                    "schema_version": "2026-04-28",
                    "mutation_id": "mut-002",
                    "mutation_key": "mk-send-1",
                    "operation": "send_user_block",
                    "status": "applied",
                    "block_code": "ZXG",
                    "requested_stock_count": 1,
                    "show": True,
                },
                "artifacts": {
                    "audit_log_path": "runtime/block-mutations/mut-002.json",
                },
            },
        )
        with patch("tdxquant.api.block.run_tdx_send_user_block", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.block.send_user_block(
                "ZXG",
                ["000001.SZ"],
                show=True,
                mutation_key="mk-send-1",
                audit_dir="runtime/block-mutations",
            )
        mocked.assert_called_once_with(
            block_code="ZXG",
            stocks=["000001.SZ"],
            show=True,
            mutation_key="mk-send-1",
            audit_dir="runtime/block-mutations",
            strategy_path="strategy.py",
        )
        self.assertEqual(result.data["block_mutation"]["operation"], "send_user_block")
        self.assertEqual(result.data["block_mutation"]["requested_stock_count"], 1)

    def test_manager_block_send_user_block_preserves_governance_contract(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="skipped",
            data={
                "block_mutation": {
                    "schema_version": "2026-05-02",
                    "mutation_id": "mut-003",
                    "mutation_key": "mk-noop-1",
                    "operation": "send_user_block",
                    "status": "noop",
                    "governance_decision": "skip",
                    "governance_reason": "already_applied",
                    "block_code": "ZXG",
                    "requested_stock_count": 2,
                    "show": False,
                },
                "artifacts": {
                    "audit_log_path": "runtime/block-mutations/mut-003.json",
                },
            },
        )
        with patch("tdxquant.api.block.run_tdx_send_user_block", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.block.send_user_block(
                "ZXG",
                ["000001.SZ", "600519.SH"],
                show=False,
                mutation_key="mk-noop-1",
                audit_dir="runtime/block-mutations",
            )
        mocked.assert_called_once_with(
            block_code="ZXG",
            stocks=["000001.SZ", "600519.SH"],
            show=False,
            mutation_key="mk-noop-1",
            audit_dir="runtime/block-mutations",
            strategy_path="strategy.py",
        )
        payload = result.to_dict()
        self.assertEqual(payload["data"]["block_mutation"]["status"], "noop")
        self.assertEqual(payload["data"]["block_mutation"]["governance_decision"], "skip")
        self.assertEqual(payload["data"]["block_mutation"]["governance_reason"], "already_applied")
        self.assertEqual(payload["data"]["artifacts"]["audit_log_path"], "runtime/block-mutations/mut-003.json")

    def test_manager_block_sync_watchlist_attaches_metadata(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="planned block sync",
            data={
                "sync": {
                    "block_code": "ZXG",
                    "mode": "replace",
                    "dry_run": True,
                    "governance_decision": "execute",
                }
            },
        )
        with patch("tdxquant.api.block.run_tdx_block_sync", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.block.sync_watchlist(
                block_code="ZXG",
                symbols=["000001.SZ", "600519.SH"],
                mode="replace",
                create_if_missing=True,
                dry_run=True,
                show=True,
                mutation_key="sync-001",
                audit_dir="runtime/block-sync",
            )
        mocked.assert_called_once_with(
            block_code="ZXG",
            symbols=["000001.SZ", "600519.SH"],
            mode="replace",
            create_if_missing=True,
            dry_run=True,
            show=True,
            mutation_key="sync-001",
            audit_dir="runtime/block-sync",
            strategy_path="strategy.py",
        )
        self.assertEqual(result.data["manager"]["domain"], "block")
        self.assertEqual(result.data["manager"]["method"], "sync_watchlist")
        self.assertEqual(result.data["api_profile"]["options"]["block_code"], "ZXG")
        self.assertEqual(result.data["sync"]["mode"], "replace")

    def test_manager_block_read_watchlist_snapshot_attaches_metadata(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="normalized block snapshot",
            data={
                "snapshot": {
                    "block_code": "ZXG",
                    "symbols": ["000001.SZ"],
                    "symbol_count": 1,
                }
            },
        )
        with patch("tdxquant.api.block.run_tdx_block_read_watchlist_snapshot", return_value=expected) as mocked:
            manager = TdxApiManager(profile="default", strategy_path="strategy.py")
            result = manager.block.read_watchlist_snapshot(block_code="ZXG")
        mocked.assert_called_once_with(block_code="ZXG", strategy_path="strategy.py")
        self.assertTrue(result.ok)
        self.assertEqual(result.data["snapshot"]["block_code"], "ZXG")
        self.assertEqual(result.data["manager"]["domain"], "block")
        self.assertEqual(result.data["manager"]["method"], "read_watchlist_snapshot")
        self.assertEqual(result.data["api_profile"]["options"]["block_code"], "ZXG")


class TdxTaskManagerTests(unittest.TestCase):
    def test_public_import_is_available(self) -> None:
        manager = TdxTaskManager(profile="default")
        self.assertEqual(manager.profile_name, "default")

    def test_task_block_sync_attaches_task_metadata_and_forwards_symbols(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="planned block sync",
            data={
                "sync": {
                    "block_code": "ZXG",
                    "mode": "merge",
                    "dry_run": True,
                }
            },
        )
        manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
        with patch.object(type(manager.api_manager.block), "sync_watchlist", return_value=expected) as mocked:
            result = manager.block_sync(
                block_code="ZXG",
                symbols=["000001.SZ", "600519.SH"],
                mode="merge",
                create_if_missing=True,
                dry_run=True,
                show=True,
                mutation_key="sync-001",
                audit_dir="runtime/block-sync",
            )
        mocked.assert_called_once_with(
            block_code="ZXG",
            symbols=["000001.SZ", "600519.SH"],
            mode="merge",
            create_if_missing=True,
            dry_run=True,
            show=True,
            mutation_key="sync-001",
            audit_dir="runtime/block-sync",
        )
        self.assertEqual(result.data["task"]["name"], "block_sync")
        self.assertEqual(result.data["task_profile"]["name"], "default")
        self.assertIn("task_call", result.data["timing"])
        self.assertEqual(result.data["sync"]["block_code"], "ZXG")

    def test_task_formula_scan_attaches_task_metadata(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with patch("tdxquant.api.formula.run_tdx_formula_process_mul_xg", return_value=expected) as mocked:
            manager = TdxTaskManager(profile="formula_scan", strategy_path="strategy.py")
            result = manager.formula_scan(formula_name="SCAN", stock_list=["000001"])
        mocked.assert_called_once()
        self.assertEqual(result.data["task"]["name"], "formula_scan")
        self.assertEqual(result.data["task_profile"]["name"], "formula_scan")
        self.assertIn("task_call", result.data["timing"])

    def test_task_sector_research_composes_meta_calls(self) -> None:
        sector_result = Result(ok=True, code=ErrorCode.OK, message="ok", data={"stocks": [{"code": "000001"}]})
        metrics_result = Result(ok=True, code=ErrorCode.OK, message="ok", data={"rows": []})
        manager = TdxTaskManager(profile="sector_research", strategy_path="strategy.py")
        with (
            patch.object(type(manager.api_manager.meta), "sector_stocks", return_value=sector_result) as mocked_sector,
            patch.object(type(manager.api_manager.meta), "gp_one_data", return_value=metrics_result) as mocked_gp_one,
        ):
            result = manager.sector_research(block_code="ZXG")
        mocked_sector.assert_called_once()
        mocked_gp_one.assert_called_once_with(stock_list=["000001"], fields=["Now", "Volume", "Amount"])
        self.assertTrue(result.ok)
        self.assertEqual(result.data["task"]["name"], "sector_research")

    def test_task_watchlist_overview_uses_profile_fields(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        manager = TdxTaskManager(profile="watchlist_overview", strategy_path="strategy.py")
        with patch.object(type(manager.api_manager.meta), "gp_one_data", return_value=expected) as mocked_gp_one:
            result = manager.watchlist_overview(stock_list=["000001", "000002"])
        mocked_gp_one.assert_called_once_with(stock_list=["000001", "000002"], fields=["Now", "Volume"])
        self.assertEqual(result.data["task"]["name"], "watchlist_overview")

    def test_task_block_read_watchlist_uses_provider_snapshot_and_attaches_task_metadata(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="normalized block snapshot",
            data={"snapshot": {"block_code": "ZXG", "symbols": ["600519.SH"]}},
        )
        manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
        with patch.object(
            type(manager.api_manager.block),
            "read_watchlist_snapshot",
            return_value=expected,
        ) as mocked_snapshot:
            result = manager.block_read_watchlist(block_code="ZXG")

        mocked_snapshot.assert_called_once_with(block_code="ZXG")
        self.assertIs(result, expected)
        self.assertEqual(result.data["task"]["name"], "block_read_watchlist")
        self.assertEqual(result.data["task_profile"]["name"], "default")
        self.assertIn("task_call", result.data["timing"])

    def test_task_block_read_watchlist_preserves_provider_failure_contract(self) -> None:
        expected = Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="block_code not found: ZXG",
            data={},
        )
        manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
        with patch.object(
            type(manager.api_manager.block),
            "read_watchlist_snapshot",
            return_value=expected,
        ):
            result = manager.block_read_watchlist(block_code="ZXG")

        self.assertIs(result, expected)
        self.assertEqual(result.data["task"]["name"], "block_read_watchlist")

    def test_task_block_read_full_adds_read_summary_and_task_metadata(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="normalized block snapshot",
            data={
                "snapshot": {
                    "block_code": "ZXG",
                    "symbols": ["600519.SH"],
                    "symbol_count": 1,
                    "source": "tongdaxin.custom_sector",
                    "source_metadata": {
                        "sector_name": "自选股",
                        "raw_member_count": 2,
                        "duplicate_count": 1,
                    },
                }
            },
            warnings=["duplicate members removed"],
        )
        manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
        with patch.object(
            type(manager.api_manager.block),
            "read_watchlist_snapshot",
            return_value=expected,
        ) as mocked_snapshot:
            result = manager.block_read_full(block_code="ZXG")

        mocked_snapshot.assert_called_once_with(block_code="ZXG")
        self.assertIs(result, expected)
        self.assertEqual(
            result.data["read_full"],
            {
                "sector_name": "自选股",
                "raw_member_count": 2,
                "duplicate_count": 1,
                "warnings_present": True,
            },
        )
        self.assertEqual(result.data["task"]["name"], "block_read_full")
        self.assertEqual(result.data["task_profile"]["name"], "default")
        self.assertIn("task_call", result.data["timing"])

    def test_task_block_read_full_preserves_provider_failure_contract(self) -> None:
        expected = Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="block_code not found: ZXG",
            data={"diagnostic": {"block_code": "ZXG"}},
            warnings=["provider warning"],
            next_action="Inspect the block code and retry.",
        )
        manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
        with patch.object(
            type(manager.api_manager.block),
            "read_watchlist_snapshot",
            return_value=expected,
        ):
            result = manager.block_read_full(block_code="ZXG")

        self.assertIs(result, expected)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(result.message, "block_code not found: ZXG")
        self.assertEqual(result.data["diagnostic"], {"block_code": "ZXG"})
        self.assertEqual(result.warnings, ["provider warning"])
        self.assertEqual(result.next_action, "Inspect the block code and retry.")
        self.assertNotIn("read_full", result.data)
        self.assertEqual(result.data["task"]["name"], "block_read_full")

    def test_task_block_read_full_tolerates_partial_source_metadata(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="normalized block snapshot",
            data={
                "snapshot": {
                    "block_code": "ZXG",
                    "symbols": [],
                    "symbol_count": 0,
                    "source": "tongdaxin.custom_sector",
                    "source_metadata": {"sector_name": "空板块"},
                }
            },
            warnings=[],
        )
        manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
        with patch.object(
            type(manager.api_manager.block),
            "read_watchlist_snapshot",
            return_value=expected,
        ):
            result = manager.block_read_full(block_code="ZXG")

        self.assertEqual(
            result.data["read_full"],
            {
                "sector_name": "空板块",
                "raw_member_count": None,
                "duplicate_count": None,
                "warnings_present": False,
            },
        )

    def test_task_block_read_watchlist_export_writes_snapshot_json(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="normalized block snapshot",
            data={"snapshot": {"block_code": "ZXG", "symbols": ["600519.SH"], "symbol_count": 1}},
        )
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "zxg.json"
            manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
            with patch.object(
                type(manager.api_manager.block),
                "read_watchlist_snapshot",
                return_value=expected,
            ) as mocked_snapshot:
                result = manager.block_read_watchlist_export(block_code="ZXG", output=str(output_path))

            mocked_snapshot.assert_called_once_with(block_code="ZXG")
            self.assertTrue(output_path.exists())
            self.assertEqual(json.loads(output_path.read_text(encoding="utf-8")), expected.data["snapshot"])
            self.assertEqual(result.data["export"]["output_path"], str(output_path.resolve()))
            self.assertFalse(result.data["export"]["overwritten"])
            self.assertGreater(result.data["export"]["file_size"], 0)
            self.assertEqual(result.data["task"]["name"], "block_read_watchlist_export")

    def test_task_block_read_watchlist_export_passthroughs_provider_failure_without_writing_file(self) -> None:
        expected = Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="block_code not found: ZXG",
            data={},
        )
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "zxg.json"
            manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
            with patch.object(
                type(manager.api_manager.block),
                "read_watchlist_snapshot",
                return_value=expected,
            ) as mocked_snapshot:
                result = manager.block_read_watchlist_export(block_code="ZXG", output=str(output_path))

            mocked_snapshot.assert_called_once_with(block_code="ZXG")
            self.assertIs(result, expected)
            self.assertFalse(output_path.exists())
            self.assertNotIn("export", result.data)
            self.assertEqual(result.data["task"]["name"], "block_read_watchlist_export")

    def test_task_block_read_watchlist_export_rejects_existing_file_without_overwrite(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="normalized block snapshot",
            data={
                "snapshot": {"block_code": "ZXG", "symbols": ["600519.SH"], "symbol_count": 1},
                "provider_context": {"source": "fixture"},
            },
            warnings=["provider-warning"],
            next_action="provider-next-action",
            _provider_artifacts=[{"kind": "provider-log", "path": "runtime/provider.log"}],
        )
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "zxg.json"
            output_path.write_text('{"stale": true}\n', encoding="utf-8")
            original_contents = output_path.read_text(encoding="utf-8")
            manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
            with patch.object(
                type(manager.api_manager.block),
                "read_watchlist_snapshot",
                return_value=expected,
            ):
                result = manager.block_read_watchlist_export(block_code="ZXG", output=str(output_path))

            self.assertFalse(result.ok)
            self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
            self.assertIs(result, expected)
            self.assertEqual(result.data["snapshot"]["block_code"], "ZXG")
            self.assertEqual(result.data["provider_context"], {"source": "fixture"})
            self.assertEqual(result.warnings, ["provider-warning"])
            self.assertEqual(result.to_provider_dict()["artifacts"], [{"kind": "provider-log", "path": "runtime/provider.log"}])
            self.assertEqual(result.data["export"]["output_path"], str(output_path.resolve()))
            self.assertIn("exists", result.data["export"]["error"])
            self.assertEqual(output_path.read_text(encoding="utf-8"), original_contents)
            self.assertEqual(result.data["task"]["name"], "block_read_watchlist_export")

    def test_task_block_read_watchlist_export_rejects_existing_file_before_writable_probe(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="normalized block snapshot",
            data={"snapshot": {"block_code": "ZXG", "symbols": ["600519.SH"], "symbol_count": 1}},
        )
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "zxg.json"
            output_path.write_text('{"stale": true}\n', encoding="utf-8")
            manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
            with (
                patch.object(
                    type(manager.api_manager.block),
                    "read_watchlist_snapshot",
                    return_value=expected,
                ),
                patch("tdxquant.api.task._probe_directory_writable", side_effect=OSError("permission denied")) as mocked_probe,
            ):
                result = manager.block_read_watchlist_export(block_code="ZXG", output=str(output_path))

            self.assertFalse(result.ok)
            self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
            self.assertIn("exists", result.data["export"]["error"])
            self.assertNotIn("permission denied", result.data["export"]["error"])
            mocked_probe.assert_not_called()
            self.assertEqual(result.data["task"]["name"], "block_read_watchlist_export")

    def test_task_block_read_watchlist_export_overwrites_when_enabled(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="normalized block snapshot",
            data={"snapshot": {"block_code": "ZXG", "symbols": ["600519.SH"], "symbol_count": 1}},
        )
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "zxg.json"
            output_path.write_text('{"stale": true}\n', encoding="utf-8")
            manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
            with patch.object(
                type(manager.api_manager.block),
                "read_watchlist_snapshot",
                return_value=expected,
            ):
                result = manager.block_read_watchlist_export(block_code="ZXG", output=str(output_path), overwrite=True)

            self.assertTrue(result.ok)
            self.assertEqual(json.loads(output_path.read_text(encoding="utf-8")), expected.data["snapshot"])
            self.assertTrue(result.data["export"]["overwritten"])
            self.assertEqual(result.data["task"]["name"], "block_read_watchlist_export")

    def test_task_block_read_watchlist_export_preserves_snapshot_when_write_fails(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="normalized block snapshot",
            data={
                "snapshot": {"block_code": "ZXG", "symbols": ["600519.SH"], "symbol_count": 1},
                "provider_context": {"source": "fixture"},
            },
            warnings=["provider-warning"],
            next_action="provider-next-action",
            _provider_artifacts=[{"kind": "provider-log", "path": "runtime/provider.log"}],
        )
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "zxg.json"
            manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
            with (
                patch.object(
                    type(manager.api_manager.block),
                    "read_watchlist_snapshot",
                    return_value=expected,
                ),
                patch("tdxquant.api.task._write_json_file_atomic", side_effect=OSError("disk full")),
            ):
                result = manager.block_read_watchlist_export(block_code="ZXG", output=str(output_path))

            self.assertFalse(result.ok)
            self.assertEqual(result.code, ErrorCode.EXECUTION_FAILED)
            self.assertIs(result, expected)
            self.assertEqual(result.data["snapshot"], expected.data["snapshot"])
            self.assertEqual(result.data["provider_context"], {"source": "fixture"})
            self.assertEqual(result.warnings, ["provider-warning"])
            self.assertEqual(result.to_provider_dict()["artifacts"], [{"kind": "provider-log", "path": "runtime/provider.log"}])
            self.assertEqual(result.data["export"]["output_path"], str(output_path.resolve()))
            self.assertIn("disk full", result.data["export"]["error"])
            self.assertFalse(output_path.exists())
            self.assertEqual(list(Path(temp_dir).glob(".*.tmp")), [])
            self.assertEqual(result.data["task"]["name"], "block_read_watchlist_export")

    def test_task_block_read_watchlist_export_rejects_missing_or_malformed_snapshot(self) -> None:
        manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
        malformed_results = [
            Result(ok=True, code=ErrorCode.OK, message="normalized block snapshot", data={}),
            Result(ok=True, code=ErrorCode.OK, message="normalized block snapshot", data={"snapshot": ["600519.SH"]}),
        ]

        with TemporaryDirectory() as temp_dir:
            for index, expected in enumerate(malformed_results):
                output_path = Path(temp_dir) / f"bad-{index}.json"
                with patch.object(
                    type(manager.api_manager.block),
                    "read_watchlist_snapshot",
                    return_value=expected,
                ):
                    result = manager.block_read_watchlist_export(block_code="ZXG", output=str(output_path))

                self.assertFalse(result.ok)
                self.assertEqual(result.code, ErrorCode.EXECUTION_FAILED)
                self.assertEqual(result.data["export"]["output_path"], str(output_path.resolve()))
                self.assertIn("snapshot", result.data["export"]["error"])
                self.assertFalse(output_path.exists())
                self.assertEqual(result.data["task"]["name"], "block_read_watchlist_export")

    def test_task_block_read_watchlist_export_rejects_unresolvable_output_path(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="normalized block snapshot",
            data={"snapshot": {"block_code": "ZXG", "symbols": ["600519.SH"], "symbol_count": 1}},
        )
        manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
        with (
            patch.object(
                type(manager.api_manager.block),
                "read_watchlist_snapshot",
                return_value=expected,
            ),
            patch("tdxquant.api.task.Path.resolve", side_effect=RuntimeError("symlink loop detected")),
        ):
            result = manager.block_read_watchlist_export(block_code="ZXG", output="broken-link/zxg.json")

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(result.data["export"]["output_path"], "broken-link/zxg.json")
        self.assertIn("symlink loop detected", result.data["export"]["error"])
        self.assertEqual(result.data["task"]["name"], "block_read_watchlist_export")

    def test_task_block_read_watchlist_export_rejects_unwritable_parent_directory_as_invalid_request(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="normalized block snapshot",
            data={
                "snapshot": {"block_code": "ZXG", "symbols": ["600519.SH"], "symbol_count": 1},
                "provider_context": {"source": "fixture"},
            },
            warnings=["provider-warning"],
            _provider_artifacts=[{"kind": "provider-log", "path": "runtime/provider.log"}],
        )
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "nested" / "zxg.json"
            output_path.parent.mkdir()
            manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
            with (
                patch.object(
                    type(manager.api_manager.block),
                    "read_watchlist_snapshot",
                    return_value=expected,
                ),
                patch("tdxquant.api.task._probe_directory_writable", side_effect=OSError("permission denied")),
            ):
                result = manager.block_read_watchlist_export(block_code="ZXG", output=str(output_path))

            self.assertFalse(result.ok)
            self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
            self.assertIs(result, expected)
            self.assertEqual(result.data["snapshot"], expected.data["snapshot"])
            self.assertEqual(result.data["provider_context"], {"source": "fixture"})
            self.assertEqual(result.warnings, ["provider-warning"])
            self.assertEqual(result.to_provider_dict()["artifacts"], [{"kind": "provider-log", "path": "runtime/provider.log"}])
            self.assertEqual(result.data["export"]["output_path"], str(output_path.resolve()))
            self.assertIn("permission denied", result.data["export"]["error"])
            self.assertFalse(output_path.exists())
            self.assertEqual(result.data["task"]["name"], "block_read_watchlist_export")

    def test_task_block_read_watchlist_export_rejects_invalid_output_path_without_crashing(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="normalized block snapshot",
            data={"snapshot": {"block_code": "ZXG", "symbols": ["600519.SH"], "symbol_count": 1}},
        )
        manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
        with (
            patch.object(
                type(manager.api_manager.block),
                "read_watchlist_snapshot",
                return_value=expected,
            ),
            patch("tdxquant.api.task.Path.resolve", side_effect=RuntimeError("symlink loop")),
        ):
            result = manager.block_read_watchlist_export(block_code="ZXG", output="runtime/exports/zxg.json")

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(result.data["snapshot"], expected.data["snapshot"])
        self.assertEqual(result.data["export"]["output_path"], "runtime/exports/zxg.json")
        self.assertIn("symlink loop", result.data["export"]["error"])
        self.assertEqual(result.data["task"]["name"], "block_read_watchlist_export")

    def test_task_block_read_watchlist_export_rejects_directory_output_path(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="normalized block snapshot",
            data={"snapshot": {"block_code": "ZXG", "symbols": ["600519.SH"], "symbol_count": 1}},
        )
        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
            with patch.object(
                type(manager.api_manager.block),
                "read_watchlist_snapshot",
                return_value=expected,
            ):
                result = manager.block_read_watchlist_export(block_code="ZXG", output=str(output_dir))

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertIn("must be a file", result.message)
        self.assertEqual(result.data["snapshot"], expected.data["snapshot"])
        self.assertEqual(result.data["export"]["output_path"], str(output_dir.resolve()))
        self.assertIn("directory", result.data["export"]["error"])
        self.assertEqual(result.data["task"]["name"], "block_read_watchlist_export")

    def test_task_block_read_watchlist_export_existing_file_conflict_wins_before_probe_failure(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="normalized block snapshot",
            data={"snapshot": {"block_code": "ZXG", "symbols": ["600519.SH"], "symbol_count": 1}},
        )
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "zxg.json"
            output_path.write_text('{"stale": true}\n', encoding="utf-8")
            manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
            with (
                patch.object(
                    type(manager.api_manager.block),
                    "read_watchlist_snapshot",
                    return_value=expected,
                ),
                patch("tdxquant.api.task._probe_directory_writable", side_effect=OSError("permission denied")),
            ):
                result = manager.block_read_watchlist_export(block_code="ZXG", output=str(output_path))

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertIn("already exists", result.message)
        self.assertIn("already exists", result.data["export"]["error"])

    def test_task_block_read_watchlist_export_treats_racy_create_as_existing_file_conflict(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="normalized block snapshot",
            data={"snapshot": {"block_code": "ZXG", "symbols": ["600519.SH"], "symbol_count": 1}},
        )
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "zxg.json"
            manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
            with (
                patch.object(
                    type(manager.api_manager.block),
                    "read_watchlist_snapshot",
                    return_value=expected,
                ),
                patch("tdxquant.api.task._write_json_file_atomic", side_effect=FileExistsError("already exists")),
            ):
                result = manager.block_read_watchlist_export(block_code="ZXG", output=str(output_path))

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertIn("already exists", result.message)
        self.assertIn("already exists", result.data["export"]["error"])

    def test_task_sector_formula_scan_composes_meta_and_formula_calls(self) -> None:
        sector_result = Result(ok=True, code=ErrorCode.OK, message="ok", data={"stocks": [{"code": "000001"}, {"code": "000002"}]})
        scan_result = Result(ok=True, code=ErrorCode.OK, message="ok", data={"rows": []})
        manager = TdxTaskManager(profile="sector_formula_scan", strategy_path="strategy.py")
        with (
            patch.object(type(manager.api_manager.meta), "sector_stocks", return_value=sector_result) as mocked_sector,
            patch.object(type(manager.api_manager.formula), "process_mul_xg", return_value=scan_result) as mocked_scan,
        ):
            result = manager.sector_formula_scan(block_code="钛金属", formula_name="SCAN")
        mocked_sector.assert_called_once()
        mocked_scan.assert_called_once()
        self.assertTrue(result.ok)
        self.assertEqual(result.data["task"]["name"], "sector_formula_scan")

    def test_task_watchlist_export_writes_json_and_csv(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"rows": [{"code": "000001", "Now": 10.5}]})
        with TemporaryDirectory() as temp_dir:
            manager = TdxTaskManager(
                profile="watchlist_export",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir, "export_stem": "wl"},
            )
            with patch.object(type(manager.api_manager.meta), "gp_one_data", return_value=expected):
                result = manager.watchlist_export(stock_list=["000001"])
            json_path = Path(result.data["artifacts"]["json_output_path"])
            csv_path = Path(result.data["artifacts"]["csv_output_path"])
            self.assertTrue(json_path.exists())
            self.assertTrue(csv_path.exists())
            self.assertIn("000001", json_path.read_text(encoding="utf-8"))
            self.assertIn("Now", csv_path.read_text(encoding="utf-8"))
            self.assertEqual(result.data["task"]["name"], "watchlist_export")

    def test_task_subscription_watch_writes_event_artifacts_and_summary(self) -> None:
        fake_session = _FakeTaskRuntimeSubscriptionSession(
            events=[
                {
                    "600519.SH": {
                        "Now": 123.45,
                        "UpdateTime": "2026-04-28T09:30:01+08:00",
                    }
                }
            ]
        )
        with TemporaryDirectory() as temp_dir:
            manager = TdxTaskManager(
                profile="subscription_watch",
                strategy_path="strategy.py",
                profile_overrides={"run_root_dir": temp_dir, "poll_interval": 0.0},
            )
            with patch.object(type(manager.api_manager.runtime), "open_subscription_session", return_value=fake_session):
                result = manager.subscription_watch(stock_list=["600519.SH"], max_events=1, poll_interval=0.0)

            run_dir = Path(result.data["artifacts"]["run_dir"])
            manifest_path = Path(result.data["artifacts"]["manifest_path"])
            jsonl_path = Path(result.data["artifacts"]["events_jsonl_path"])
            csv_path = Path(result.data["artifacts"]["events_csv_path"])
            status_path = Path(result.data["artifacts"]["status_path"])
            summary_path = Path(result.data["artifacts"]["summary_path"])
            manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            status_payload = json.loads(status_path.read_text(encoding="utf-8"))
            summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))
            jsonl_lines = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["summary"]["event_count"], 1)
            self.assertEqual(result.data["summary"]["stop_reason"], "max_events")
            self.assertEqual(result.data["task"]["name"], "subscription_watch")
            self.assertEqual(run_dir.name, result.data["subscription"]["run_id"])
            self.assertTrue(run_dir.exists())
            self.assertTrue(manifest_path.exists())
            self.assertTrue(jsonl_path.exists())
            self.assertTrue(csv_path.exists())
            self.assertTrue(status_path.exists())
            self.assertTrue(summary_path.exists())
            self.assertEqual(manifest_payload["capability"], "subscription.watch")
            self.assertEqual(jsonl_lines[0]["symbol"], "600519.SH")
            self.assertEqual(jsonl_lines[0]["run_id"], result.data["subscription"]["run_id"])
            self.assertEqual(jsonl_lines[0]["sequence"], 1)
            self.assertEqual(jsonl_lines[0]["provider_instance_id"], "provider-session-001")
            self.assertEqual(status_payload["state"], "completed")
            self.assertEqual(status_payload["event_count"], 1)
            self.assertEqual(summary_payload["final_state"], "completed")
            self.assertEqual(summary_payload["stop_reason"], "max_events")
            self.assertEqual(fake_session.unsubscribe_calls, [["600519.SH"]])
            self.assertEqual(fake_session.close_calls, 1)

    def test_task_subscription_watch_handles_keyboard_interrupt_gracefully(self) -> None:
        fake_session = _FakeTaskRuntimeSubscriptionSession(events=[])
        with TemporaryDirectory() as temp_dir:
            manager = TdxTaskManager(
                profile="subscription_watch",
                strategy_path="strategy.py",
                profile_overrides={"run_root_dir": temp_dir, "poll_interval": 0.1},
            )
            with (
                patch.object(type(manager.api_manager.runtime), "open_subscription_session", return_value=fake_session),
                patch("tdxquant.api.task.time.sleep", side_effect=KeyboardInterrupt),
            ):
                result = manager.subscription_watch(stock_list=["600519.SH"], poll_interval=0.1)

            summary_path = Path(result.data["artifacts"]["summary_path"])
            summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))

        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["stop_reason"], "keyboard_interrupt")
        self.assertEqual(summary_payload["final_state"], "interrupted")
        self.assertEqual(summary_payload["stop_reason"], "keyboard_interrupt")
        self.assertEqual(fake_session.unsubscribe_calls, [["600519.SH"]])
        self.assertEqual(fake_session.close_calls, 1)

    def test_task_subscription_watch_honors_explicit_run_id(self) -> None:
        fake_session = _FakeTaskRuntimeSubscriptionSession(
            events=[
                {
                    "600519.SH": {
                        "Now": 123.45,
                        "UpdateTime": "2026-04-28T09:30:01+08:00",
                    }
                }
            ]
        )
        with TemporaryDirectory() as temp_dir:
            manager = TdxTaskManager(
                profile="subscription_watch",
                strategy_path="strategy.py",
                profile_overrides={"run_root_dir": temp_dir, "poll_interval": 0.0},
            )
            with patch.object(type(manager.api_manager.runtime), "open_subscription_session", return_value=fake_session):
                result = manager.subscription_watch(
                    stock_list=["600519.SH"],
                    max_events=1,
                    poll_interval=0.0,
                    run_id="custom-run-001",
                )

            run_dir = Path(result.data["artifacts"]["run_dir"])
            manifest_path = Path(result.data["artifacts"]["manifest_path"])
            status_path = Path(result.data["artifacts"]["status_path"])
            summary_path = Path(result.data["artifacts"]["summary_path"])
            events_path = Path(result.data["artifacts"]["events_jsonl_path"])
            manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            status_payload = json.loads(status_path.read_text(encoding="utf-8"))
            summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))

        self.assertTrue(result.ok)
        self.assertEqual(result.data["subscription"]["run_id"], "custom-run-001")
        self.assertEqual(run_dir.name, "custom-run-001")
        self.assertEqual(manifest_payload["run_id"], "custom-run-001")
        self.assertEqual(status_payload["run_id"], "custom-run-001")
        self.assertEqual(summary_payload["run_id"], "custom-run-001")
        self.assertEqual(events_path.parent, run_dir)

    def test_task_subscription_watch_replay_mode_materializes_completed_run_without_live_session(self) -> None:
        fake_session = _FakeTaskRuntimeSubscriptionSession(
            events=[
                {
                    "600519.SH": {
                        "Now": 999.0,
                        "UpdateTime": "2026-05-02T09:30:01+08:00",
                    }
                }
            ]
        )
        with TemporaryDirectory() as temp_dir:
            manager = TdxTaskManager(
                profile="subscription_watch",
                strategy_path="strategy.py",
                profile_overrides={"run_root_dir": temp_dir},
                provider_mode="replay",
            )
            with patch.object(type(manager.api_manager.runtime), "open_subscription_session", return_value=fake_session) as mocked_open:
                result = manager.subscription_watch(stock_list=["600519.SH"])

            manifest_path = Path(result.data["artifacts"]["manifest_path"])
            summary_path = Path(result.data["artifacts"]["summary_path"])
            events_path = Path(result.data["artifacts"]["events_jsonl_path"])
            manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))
            event_rows = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]

        self.assertTrue(result.ok)
        self.assertEqual(result.data["task"]["name"], "subscription_watch")
        self.assertEqual(result.data["summary"]["event_count"], 2)
        self.assertEqual(result.data["summary"]["stop_reason"], "max_events")
        self.assertIn("events_csv_path", result.data["artifacts"])
        self.assertIn("jsonl_output_path", result.data["artifacts"])
        self.assertIn("csv_output_path", result.data["artifacts"])
        self.assertIn("status_output_path", result.data["artifacts"])
        self.assertEqual(result.data["artifacts"]["jsonl_output_path"], result.data["artifacts"]["events_jsonl_path"])
        self.assertEqual(result.data["artifacts"]["csv_output_path"], result.data["artifacts"]["events_csv_path"])
        self.assertEqual(result.data["artifacts"]["status_output_path"], result.data["artifacts"]["status_path"])
        self.assertEqual(manifest_payload["provider_mode"], "replay")
        self.assertEqual(summary_payload["final_state"], "completed")
        self.assertEqual(event_rows[0]["run_id"], result.data["subscription"]["run_id"])
        mocked_open.assert_not_called()

    def test_task_subscription_watch_replay_mode_accepts_explicit_source_directory(self) -> None:
        source_manifest = load_provider_replay_fixture("subscription-watch-manifest")
        source_status = load_provider_replay_fixture("subscription-watch-status-completed")
        source_summary = load_provider_replay_fixture("subscription-watch-summary-completed")
        source_events = load_provider_replay_fixture("subscription-watch-events")
        source_run_id = source_manifest["run_id"]
        with TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source-run"
            source_dir.mkdir()
            (source_dir / "manifest.json").write_text(json.dumps(source_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            (source_dir / "status.json").write_text(json.dumps(source_status, ensure_ascii=False, indent=2), encoding="utf-8")
            (source_dir / "summary.json").write_text(json.dumps(source_summary, ensure_ascii=False, indent=2), encoding="utf-8")
            (source_dir / "events.jsonl").write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in source_events) + "\n",
                encoding="utf-8",
            )
            manager = TdxTaskManager(
                profile="subscription_watch",
                strategy_path="strategy.py",
                profile_overrides={"run_root_dir": str(Path(temp_dir) / "output")},
                provider_mode="replay",
                replay_fixture_path=str(source_dir),
            )
            with patch.object(type(manager.api_manager.runtime), "open_subscription_session") as mocked_open:
                result = manager.subscription_watch(stock_list=["600519.SH"])

        self.assertTrue(result.ok)
        self.assertNotEqual(result.data["subscription"]["run_id"], source_run_id)
        self.assertEqual(result.data["manifest"]["provider_mode"], "replay")
        self.assertTrue(result.data["artifacts"]["run_dir"].endswith(result.data["subscription"]["run_id"]))
        mocked_open.assert_not_called()

    def test_task_subscription_watch_replay_mode_rejects_incomplete_source_directory_without_live_session(self) -> None:
        with TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "broken-run"
            source_dir.mkdir()
            (source_dir / "manifest.json").write_text("{}", encoding="utf-8")
            (source_dir / "status.json").write_text("{}", encoding="utf-8")
            (source_dir / "summary.json").write_text("{}", encoding="utf-8")
            manager = TdxTaskManager(
                profile="subscription_watch",
                strategy_path="strategy.py",
                profile_overrides={"run_root_dir": str(Path(temp_dir) / "output")},
                provider_mode="replay",
                replay_fixture_path=str(source_dir),
            )

            with patch.object(type(manager.api_manager.runtime), "open_subscription_session") as mocked_open:
                result = manager.subscription_watch(stock_list=["600519.SH"])

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(result.data["replay_source"]["mode"], "replay")
        self.assertEqual(result.data["replay_source"]["capability"], "subscription.watch")
        self.assertIn("subscription.watch replay artifact does not exist", result.message)
        mocked_open.assert_not_called()

    def test_task_ledger_summary_reads_default_jsonl_and_filters(self) -> None:
        with TemporaryDirectory() as temp_dir:
            ledger_path = Path(temp_dir) / "guarded-trade-buy-ledger.jsonl"
            ledger_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-04-26T08:00:00+00:00",
                                "task_name": "guarded_trade_buy",
                                "code": "000001",
                                "trade_ok": True,
                                "contract_no": "B202604260001",
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-26T08:01:00+00:00",
                                "task_name": "guarded_trade_buy",
                                "code": "000002",
                                "trade_ok": False,
                                "contract_no": "B202604260002",
                            },
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            manager = TdxTaskManager(
                profile="ledger_summary",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir},
            )
            result = manager.ledger_summary(code="000001", trade_ok=True, limit=5)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["source"]["format"], "jsonl")
        self.assertEqual(result.data["summary"]["total_entries"], 2)
        self.assertEqual(result.data["summary"]["matched_entries"], 1)
        self.assertEqual(result.data["summary"]["success_count"], 1)
        self.assertEqual(result.data["entries"][0]["contract_no"], "B202604260001")
        self.assertEqual(result.data["task"]["name"], "ledger_summary")

    def test_task_ledger_summary_can_export_filtered_entries(self) -> None:
        with TemporaryDirectory() as temp_dir:
            ledger_path = Path(temp_dir) / "guarded-trade-buy-ledger.jsonl"
            ledger_path.write_text(
                json.dumps(
                    {
                        "timestamp": "2026-04-26T08:00:00+00:00",
                        "task_name": "guarded_trade_buy",
                        "code": "000001",
                        "trade_ok": True,
                        "contract_no": "B202604260001",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            manager = TdxTaskManager(
                profile="ledger_summary",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir, "export_stem": "ledger-view"},
            )
            result = manager.ledger_summary(json_output_path=str(Path(temp_dir) / "summary.json"))
            json_path = Path(result.data["artifacts"]["json_output_path"])
            csv_path = Path(result.data["artifacts"]["csv_output_path"])
            self.assertTrue(json_path.exists())
            self.assertTrue(csv_path.exists())
            self.assertIn("matched_entries", json_path.read_text(encoding="utf-8"))
            self.assertIn("contract_no", csv_path.read_text(encoding="utf-8"))

    def test_task_ledger_summary_returns_path_not_found_when_missing(self) -> None:
        with TemporaryDirectory() as temp_dir:
            manager = TdxTaskManager(
                profile="ledger_summary",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir},
            )
            result = manager.ledger_summary()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.PATH_NOT_FOUND)

    def test_task_daily_trade_report_uses_default_local_date(self) -> None:
        with TemporaryDirectory() as temp_dir:
            ledger_path = Path(temp_dir) / "guarded-trade-buy-ledger.jsonl"
            ledger_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-04-25T16:30:00+00:00",
                                "task_name": "guarded_trade_buy",
                                "code": "000001",
                                "price": "10.00",
                                "quantity": 100,
                                "trade_ok": True,
                                "contract_no": "B202604260101",
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-24T16:30:00+00:00",
                                "task_name": "guarded_trade_buy",
                                "code": "000002",
                                "price": "11.00",
                                "quantity": 200,
                                "trade_ok": False,
                                "contract_no": "B202604250101",
                            },
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            manager = TdxTaskManager(
                profile="daily_trade_report",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir},
            )
            with patch("tdxquant.api.task._current_local_date_iso", return_value="2026-04-26"):
                result = manager.daily_trade_report()
        self.assertTrue(result.ok)
        self.assertEqual(result.data["input"]["report_date"], "2026-04-26")
        self.assertEqual(result.data["summary"]["report_entries"], 1)
        self.assertEqual(result.data["summary"]["unique_codes"], ["000001"])
        self.assertEqual(result.data["task"]["name"], "daily_trade_report")

    def test_task_daily_trade_report_aggregates_explicit_date_and_exports(self) -> None:
        with TemporaryDirectory() as temp_dir:
            ledger_path = Path(temp_dir) / "guarded-trade-buy-ledger.jsonl"
            ledger_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-04-26T01:00:00+00:00",
                                "task_name": "guarded_trade_buy",
                                "code": "000001",
                                "price": "10.00",
                                "quantity": 100,
                                "trade_ok": True,
                                "contract_no": "B202604260201",
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-26T02:00:00+00:00",
                                "task_name": "guarded_trade_buy",
                                "code": "000001",
                                "price": "10.50",
                                "quantity": 200,
                                "trade_ok": False,
                                "contract_no": "B202604260202",
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-26T03:00:00+00:00",
                                "task_name": "guarded_trade_buy",
                                "code": "000002",
                                "price": "8.00",
                                "quantity": 100,
                                "trade_ok": True,
                                "contract_no": "B202604260203",
                            },
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            manager = TdxTaskManager(
                profile="daily_trade_report",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir, "export_stem": "daily-report"},
            )
            result = manager.daily_trade_report(
                report_date="2026-04-26",
                timezone_name="UTC",
                json_output_path=str(Path(temp_dir) / "daily.json"),
            )
            json_path = Path(result.data["artifacts"]["json_output_path"])
            csv_path = Path(result.data["artifacts"]["csv_output_path"])
            by_code_rows = {row["code"]: row for row in result.data["by_code"]}
            self.assertTrue(json_path.exists())
            self.assertTrue(csv_path.exists())
            self.assertEqual(result.data["summary"]["report_entries"], 3)
            self.assertEqual(result.data["summary"]["total_quantity"], 400)
            self.assertEqual(result.data["summary"]["total_amount"], 3900.0)
            self.assertEqual(by_code_rows["000001"]["entries_count"], 2)
            self.assertEqual(by_code_rows["000001"]["success_count"], 1)
            self.assertEqual(by_code_rows["000001"]["failed_count"], 1)
            self.assertIn("total_amount", csv_path.read_text(encoding="utf-8"))
            self.assertIn("report_entries", json_path.read_text(encoding="utf-8"))

    def test_task_trade_report_lookup_loads_unique_report_by_contract_no(self) -> None:
        with TemporaryDirectory() as temp_dir:
            report_json_path = Path(temp_dir) / "guarded-000001.json"
            report_json_path.write_text(
                json.dumps({"trade_result": {"ok": True}, "result_dialog": {"contract_no": "B202604260301"}}, ensure_ascii=False),
                encoding="utf-8",
            )
            report_csv_path = Path(temp_dir) / "guarded-000001.csv"
            report_csv_path.write_text("code,contract_no\n000001,B202604260301\n", encoding="utf-8")
            ledger_path = Path(temp_dir) / "guarded-trade-buy-ledger.jsonl"
            ledger_path.write_text(
                json.dumps(
                    {
                        "timestamp": "2026-04-26T04:00:00+00:00",
                        "task_name": "guarded_trade_buy",
                        "code": "000001",
                        "price": "10.00",
                        "quantity": 100,
                        "trade_ok": True,
                        "contract_no": "B202604260301",
                        "report_json_path": str(report_json_path),
                        "report_csv_path": str(report_csv_path),
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            manager = TdxTaskManager(
                profile="trade_report_lookup",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir},
            )
            result = manager.trade_report_lookup(contract_no="B202604260301")
        self.assertTrue(result.ok)
        self.assertTrue(result.data["summary"]["unique_match"])
        self.assertTrue(result.data["summary"]["loaded_report"])
        self.assertEqual(result.data["entries"][0]["report_json_path"], str(report_json_path))
        self.assertTrue(result.data["entries"][0]["report_json_exists"])
        self.assertEqual(result.data["report"]["result_dialog"]["contract_no"], "B202604260301")
        self.assertEqual(result.data["task"]["name"], "trade_report_lookup")

    def test_task_trade_report_lookup_returns_code_candidates_newest_first_and_exports(self) -> None:
        with TemporaryDirectory() as temp_dir:
            ledger_path = Path(temp_dir) / "guarded-trade-buy-ledger.jsonl"
            ledger_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-04-26T01:00:00+00:00",
                                "task_name": "guarded_trade_buy",
                                "code": "000001",
                                "trade_ok": True,
                                "contract_no": "B202604260401",
                                "report_json_path": str(Path(temp_dir) / "r1.json"),
                                "report_csv_path": str(Path(temp_dir) / "r1.csv"),
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-26T02:00:00+00:00",
                                "task_name": "guarded_trade_buy",
                                "code": "000001",
                                "trade_ok": False,
                                "contract_no": "B202604260402",
                                "report_json_path": str(Path(temp_dir) / "r2.json"),
                                "report_csv_path": str(Path(temp_dir) / "r2.csv"),
                            },
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            manager = TdxTaskManager(
                profile="trade_report_lookup",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir, "export_stem": "lookup-view"},
            )
            result = manager.trade_report_lookup(
                code="000001",
                report_date="2026-04-26",
                timezone_name="UTC",
                json_output_path=str(Path(temp_dir) / "lookup.json"),
            )
            json_path = Path(result.data["artifacts"]["json_output_path"])
            csv_path = Path(result.data["artifacts"]["csv_output_path"])
            self.assertTrue(result.ok)
            self.assertEqual(result.data["summary"]["matched_entries"], 2)
            self.assertEqual(result.data["entries"][0]["contract_no"], "B202604260402")
            self.assertEqual(result.data["entries"][1]["contract_no"], "B202604260401")
            self.assertTrue(json_path.exists())
            self.assertTrue(csv_path.exists())
            self.assertIn("unique_match", json_path.read_text(encoding="utf-8"))
            self.assertIn("report_json_exists", csv_path.read_text(encoding="utf-8"))

    def test_task_trade_report_lookup_requires_contract_no_or_code(self) -> None:
        manager = TdxTaskManager(profile="trade_report_lookup", strategy_path="strategy.py")
        result = manager.trade_report_lookup()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)

    def test_task_trade_audit_lookup_loads_unique_audit_by_audit_id(self) -> None:
        with TemporaryDirectory() as temp_dir:
            audit_dir = Path(temp_dir) / "trade-audits"
            audit_dir.mkdir(parents=True, exist_ok=True)
            audit_path = audit_dir / "20260429T010203Z-buy-confirmed-audit001.json"
            audit_path.write_text(
                json.dumps(
                    {
                        "schema_version": "2026-04-29",
                        "trade_audit": {
                            "schema_version": "2026-04-29",
                            "audit_id": "audit-001",
                            "recorded_at": "2026-04-29T01:02:03+00:00",
                            "status": "confirmed",
                            "broker": "pingan",
                            "method": "buy",
                            "contract_no": "B202604290001",
                            "submission_key": "submit-001",
                            "side_effect_level": "live_side_effecting",
                            "risk_gate_passed": True,
                            "idempotency_decision": "record_new",
                        },
                        "result": {"ok": True, "code": 0, "message": "ok", "data": {"code": "000001"}},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            manager = TdxTaskManager(
                profile="trade_audit_lookup",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir, "audit_dir": str(audit_dir)},
            )
            result = manager.trade_audit_lookup(audit_id="audit-001")
        self.assertTrue(result.ok)
        self.assertTrue(result.data["summary"]["unique_match"])
        self.assertTrue(result.data["summary"]["loaded_audit"])
        self.assertEqual(result.data["entries"][0]["audit_id"], "audit-001")
        self.assertEqual(result.data["entries"][0]["audit_path"], str(audit_path))
        self.assertEqual(result.data["audit"]["trade_audit"]["contract_no"], "B202604290001")
        self.assertEqual(result.data["task"]["name"], "trade_audit_lookup")

    def test_task_trade_audit_lookup_returns_code_candidates_newest_first_and_exports(self) -> None:
        with TemporaryDirectory() as temp_dir:
            audit_dir = Path(temp_dir) / "trade-audits"
            audit_dir.mkdir(parents=True, exist_ok=True)
            (audit_dir / "old.json").write_text(
                json.dumps(
                    {
                        "trade_audit": {
                            "audit_id": "audit-101",
                            "recorded_at": "2026-04-29T01:00:00+00:00",
                            "status": "confirmed",
                            "broker": "pingan",
                            "method": "buy",
                            "contract_no": "B202604290101",
                            "submission_key": "submit-101",
                        },
                        "result": {"data": {"code": "000001"}},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (audit_dir / "new.json").write_text(
                json.dumps(
                    {
                        "trade_audit": {
                            "audit_id": "audit-102",
                            "recorded_at": "2026-04-29T02:00:00+00:00",
                            "status": "replayed",
                            "broker": "pingan",
                            "method": "buy_submit_once",
                            "contract_no": "B202604290102",
                            "submission_key": "submit-102",
                        },
                        "result": {"data": {"code": "000001"}},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            manager = TdxTaskManager(
                profile="trade_audit_lookup",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir, "export_stem": "audit-lookup", "audit_dir": str(audit_dir)},
            )
            result = manager.trade_audit_lookup(
                code="000001",
                json_output_path=str(Path(temp_dir) / "audit-lookup.json"),
            )
            json_path = Path(result.data["artifacts"]["json_output_path"])
            csv_path = Path(result.data["artifacts"]["csv_output_path"])
            self.assertTrue(result.ok)
            self.assertEqual(result.data["summary"]["matched_entries"], 2)
            self.assertEqual(result.data["entries"][0]["audit_id"], "audit-102")
            self.assertEqual(result.data["entries"][1]["audit_id"], "audit-101")
            self.assertTrue(json_path.exists())
            self.assertTrue(csv_path.exists())
            self.assertIn("unique_match", json_path.read_text(encoding="utf-8"))
            self.assertIn("audit_id", csv_path.read_text(encoding="utf-8"))

    def test_task_trade_audit_lookup_requires_primary_filter(self) -> None:
        manager = TdxTaskManager(profile="trade_audit_lookup", strategy_path="strategy.py")
        result = manager.trade_audit_lookup(status="confirmed")
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)

    def test_task_trade_audit_lookup_returns_path_not_found_when_missing(self) -> None:
        with TemporaryDirectory() as temp_dir:
            manager = TdxTaskManager(
                profile="trade_audit_lookup",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir, "audit_dir": str(Path(temp_dir) / "missing-audits")},
            )
            result = manager.trade_audit_lookup(audit_id="audit-001")
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.PATH_NOT_FOUND)

    def test_task_trade_audit_daily_report_uses_default_local_date(self) -> None:
        with TemporaryDirectory() as temp_dir:
            audit_dir = Path(temp_dir) / "trade-audits"
            audit_dir.mkdir(parents=True, exist_ok=True)
            (audit_dir / "a1.json").write_text(
                json.dumps(
                    {
                        "trade_audit": {
                            "audit_id": "audit-201",
                            "recorded_at": "2026-04-28T16:30:00+00:00",
                            "status": "confirmed",
                            "broker": "pingan",
                            "method": "buy",
                            "contract_no": "B202604290201",
                            "submission_key": "submit-201",
                        },
                        "result": {"data": {"code": "000001"}},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (audit_dir / "a2.json").write_text(
                json.dumps(
                    {
                        "trade_audit": {
                            "audit_id": "audit-202",
                            "recorded_at": "2026-04-27T16:30:00+00:00",
                            "status": "rejected",
                            "broker": "pingan",
                            "method": "buy_submit_once",
                            "contract_no": "B202604280202",
                            "submission_key": "submit-202",
                        },
                        "result": {"data": {"code": "000002"}},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            manager = TdxTaskManager(
                profile="trade_audit_daily_report",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir, "audit_dir": str(audit_dir)},
            )
            with patch("tdxquant.api.task._current_local_date_iso", return_value="2026-04-29"):
                result = manager.trade_audit_daily_report()
        self.assertTrue(result.ok)
        self.assertEqual(result.data["input"]["report_date"], "2026-04-29")
        self.assertEqual(result.data["summary"]["report_entries"], 1)
        self.assertEqual(result.data["summary"]["unique_codes"], ["000001"])
        self.assertEqual(result.data["by_status"][0]["status"], "confirmed")
        self.assertEqual(result.data["task"]["name"], "trade_audit_daily_report")

    def test_task_trade_audit_daily_report_supports_multi_status_filter(self) -> None:
        with TemporaryDirectory() as temp_dir:
            audit_dir = Path(temp_dir) / "trade-audits"
            audit_dir.mkdir(parents=True, exist_ok=True)
            for name, status in [
                ("a1.json", "confirmed"),
                ("a2.json", "rejected"),
                ("a3.json", "failed"),
            ]:
                (audit_dir / name).write_text(
                    json.dumps(
                        {
                            "trade_audit": {
                                "audit_id": name.replace(".json", ""),
                                "recorded_at": "2026-04-29T03:00:00+00:00",
                                "status": status,
                                "broker": "pingan",
                                "method": "buy",
                                "contract_no": f"B{name[:2]}",
                                "submission_key": f"S{name[:2]}",
                            },
                            "result": {"data": {"code": "000001"}},
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
            manager = TdxTaskManager(
                profile="trade_audit_daily_report",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir, "audit_dir": str(audit_dir)},
            )
            result = manager.trade_audit_daily_report(
                report_date="2026-04-29",
                timezone_name="UTC",
                statuses=["rejected", "failed"],
            )
        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["report_entries"], 2)
        self.assertEqual(result.data["input"]["statuses"], ["rejected", "failed"])
        by_status_rows = {row["status"]: row for row in result.data["by_status"]}
        self.assertEqual(set(by_status_rows.keys()), {"rejected", "failed"})

    def test_task_trade_audit_daily_report_rejects_mixed_single_and_multi_status_filters(self) -> None:
        manager = TdxTaskManager(profile="trade_audit_daily_report", strategy_path="strategy.py")
        result = manager.trade_audit_daily_report(report_date="2026-04-29", status="rejected", statuses=["failed"])
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)

    def test_task_trade_audit_daily_report_supports_multi_method_filter(self) -> None:
        with TemporaryDirectory() as temp_dir:
            audit_dir = Path(temp_dir) / "trade-audits"
            audit_dir.mkdir(parents=True, exist_ok=True)
            for name, method in [
                ("a1.json", "buy"),
                ("a2.json", "buy_submit_once"),
                ("a3.json", "confirm_current"),
            ]:
                (audit_dir / name).write_text(
                    json.dumps(
                        {
                            "trade_audit": {
                                "audit_id": name.replace(".json", ""),
                                "recorded_at": "2026-04-29T03:00:00+00:00",
                                "status": "rejected",
                                "broker": "pingan",
                                "method": method,
                                "contract_no": f"B{name[:2]}",
                                "submission_key": f"S{name[:2]}",
                            },
                            "result": {"data": {"code": "000001"}},
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
            manager = TdxTaskManager(
                profile="trade_audit_daily_report",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir, "audit_dir": str(audit_dir)},
            )
            result = manager.trade_audit_daily_report(
                report_date="2026-04-29",
                timezone_name="UTC",
                methods=["buy_submit_once", "confirm_current"],
            )
        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["report_entries"], 2)
        self.assertEqual(result.data["input"]["methods"], ["buy_submit_once", "confirm_current"])
        returned_methods = {entry["method"] for entry in result.data["entries"]}
        self.assertEqual(returned_methods, {"buy_submit_once", "confirm_current"})

    def test_task_trade_audit_daily_report_rejects_mixed_single_and_multi_method_filters(self) -> None:
        manager = TdxTaskManager(profile="trade_audit_daily_report", strategy_path="strategy.py")
        result = manager.trade_audit_daily_report(
            report_date="2026-04-29",
            method="buy_submit_once",
            methods=["confirm_current"],
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)

    def test_task_trade_audit_period_report_aggregates_multi_day_range_and_exports(self) -> None:
        with TemporaryDirectory() as temp_dir:
            audit_dir = Path(temp_dir) / "trade-audits"
            audit_dir.mkdir(parents=True, exist_ok=True)
            for name, recorded_at, status, method, code in [
                ("a1.json", "2026-04-28T01:00:00+00:00", "confirmed", "buy", "000001"),
                ("a2.json", "2026-04-28T02:00:00+00:00", "replayed", "buy_submit_once", "000001"),
                ("a3.json", "2026-04-29T03:00:00+00:00", "rejected", "confirm_current", "000002"),
            ]:
                (audit_dir / name).write_text(
                    json.dumps(
                        {
                            "trade_audit": {
                                "audit_id": name.replace(".json", ""),
                                "recorded_at": recorded_at,
                                "status": status,
                                "broker": "pingan",
                                "method": method,
                                "contract_no": f"B{name[:2]}",
                                "submission_key": f"S{name[:2]}",
                            },
                            "result": {"data": {"code": code}},
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
            manager = TdxTaskManager(
                profile="trade_audit_period_report",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir, "export_stem": "audit-period", "audit_dir": str(audit_dir)},
            )
            result = manager.trade_audit_period_report(
                start_date="2026-04-28",
                end_date="2026-04-29",
                timezone_name="UTC",
                json_output_path=str(Path(temp_dir) / "audit-period.json"),
            )
            json_path = Path(result.data["artifacts"]["json_output_path"])
            csv_path = Path(result.data["artifacts"]["csv_output_path"])
            by_code_rows = {row["code"]: row for row in result.data["by_code"]}
            by_status_rows = {row["status"]: row for row in result.data["by_status"]}
            by_day_rows = {row["report_date"]: row for row in result.data["by_day"]}
            self.assertTrue(json_path.exists())
            self.assertTrue(csv_path.exists())
            self.assertEqual(result.data["summary"]["report_entries"], 3)
            self.assertEqual(result.data["summary"]["trade_days"], 2)
            self.assertEqual(result.data["summary"]["unique_codes"], ["000001", "000002"])
            self.assertEqual(by_code_rows["000001"]["entries_count"], 2)
            self.assertEqual(by_status_rows["confirmed"]["entries_count"], 1)
            self.assertEqual(by_status_rows["replayed"]["entries_count"], 1)
            self.assertEqual(by_status_rows["rejected"]["entries_count"], 1)
            self.assertEqual(by_day_rows["2026-04-28"]["entries_count"], 2)
            self.assertIn("trade_days", json_path.read_text(encoding="utf-8"))
            self.assertIn("report_date", csv_path.read_text(encoding="utf-8"))

    def test_task_trade_audit_period_report_supports_multi_status_filter(self) -> None:
        with TemporaryDirectory() as temp_dir:
            audit_dir = Path(temp_dir) / "trade-audits"
            audit_dir.mkdir(parents=True, exist_ok=True)
            for name, recorded_at, status in [
                ("a1.json", "2026-04-28T01:00:00+00:00", "confirmed"),
                ("a2.json", "2026-04-28T02:00:00+00:00", "rejected"),
                ("a3.json", "2026-04-29T03:00:00+00:00", "failed"),
            ]:
                (audit_dir / name).write_text(
                    json.dumps(
                        {
                            "trade_audit": {
                                "audit_id": name.replace(".json", ""),
                                "recorded_at": recorded_at,
                                "status": status,
                                "broker": "pingan",
                                "method": "buy",
                                "contract_no": f"B{name[:2]}",
                                "submission_key": f"S{name[:2]}",
                            },
                            "result": {"data": {"code": "000001"}},
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
            manager = TdxTaskManager(
                profile="trade_audit_period_report",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir, "audit_dir": str(audit_dir)},
            )
            result = manager.trade_audit_period_report(
                start_date="2026-04-28",
                end_date="2026-04-29",
                timezone_name="UTC",
                statuses=["rejected", "failed"],
            )
        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["report_entries"], 2)
        self.assertEqual(result.data["input"]["statuses"], ["rejected", "failed"])
        by_status_rows = {row["status"]: row for row in result.data["by_status"]}
        self.assertEqual(set(by_status_rows.keys()), {"rejected", "failed"})

    def test_task_trade_audit_period_report_supports_multi_method_filter(self) -> None:
        with TemporaryDirectory() as temp_dir:
            audit_dir = Path(temp_dir) / "trade-audits"
            audit_dir.mkdir(parents=True, exist_ok=True)
            for name, recorded_at, method in [
                ("a1.json", "2026-04-28T01:00:00+00:00", "buy"),
                ("a2.json", "2026-04-28T02:00:00+00:00", "buy_submit_once"),
                ("a3.json", "2026-04-29T03:00:00+00:00", "confirm_current"),
            ]:
                (audit_dir / name).write_text(
                    json.dumps(
                        {
                            "trade_audit": {
                                "audit_id": name.replace(".json", ""),
                                "recorded_at": recorded_at,
                                "status": "failed",
                                "broker": "pingan",
                                "method": method,
                                "contract_no": f"B{name[:2]}",
                                "submission_key": f"S{name[:2]}",
                            },
                            "result": {"data": {"code": "000001"}},
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
            manager = TdxTaskManager(
                profile="trade_audit_period_report",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir, "audit_dir": str(audit_dir)},
            )
            result = manager.trade_audit_period_report(
                start_date="2026-04-28",
                end_date="2026-04-29",
                timezone_name="UTC",
                methods=["buy_submit_once", "confirm_current"],
            )
        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["report_entries"], 2)
        self.assertEqual(result.data["input"]["methods"], ["buy_submit_once", "confirm_current"])
        returned_methods = {entry["method"] for entry in result.data["entries"]}
        self.assertEqual(returned_methods, {"buy_submit_once", "confirm_current"})

    def test_task_trade_audit_period_report_requires_boundary(self) -> None:
        manager = TdxTaskManager(profile="trade_audit_period_report", strategy_path="strategy.py")
        result = manager.trade_audit_period_report()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)

    def test_task_trade_period_report_uses_single_boundary_as_single_day(self) -> None:
        with TemporaryDirectory() as temp_dir:
            ledger_path = Path(temp_dir) / "guarded-trade-buy-ledger.jsonl"
            ledger_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-04-26T01:00:00+00:00",
                                "task_name": "guarded_trade_buy",
                                "code": "000001",
                                "price": "10.00",
                                "quantity": 100,
                                "trade_ok": True,
                                "contract_no": "B202604260501",
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-27T01:00:00+00:00",
                                "task_name": "guarded_trade_buy",
                                "code": "000002",
                                "price": "11.00",
                                "quantity": 100,
                                "trade_ok": False,
                                "contract_no": "B202604270501",
                            },
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            manager = TdxTaskManager(
                profile="trade_period_report",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir},
            )
            result = manager.trade_period_report(start_date="2026-04-26", timezone_name="UTC")
        self.assertTrue(result.ok)
        self.assertEqual(result.data["input"]["start_date"], "2026-04-26")
        self.assertEqual(result.data["input"]["end_date"], "2026-04-26")
        self.assertEqual(result.data["summary"]["report_entries"], 1)
        self.assertEqual(result.data["summary"]["trade_days"], 1)
        self.assertEqual(result.data["task"]["name"], "trade_period_report")

    def test_task_trade_period_report_aggregates_multi_day_range_and_exports(self) -> None:
        with TemporaryDirectory() as temp_dir:
            ledger_path = Path(temp_dir) / "guarded-trade-buy-ledger.jsonl"
            ledger_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-04-25T01:00:00+00:00",
                                "task_name": "guarded_trade_buy",
                                "code": "000001",
                                "price": "10.00",
                                "quantity": 100,
                                "trade_ok": True,
                                "contract_no": "B202604250601",
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-26T01:00:00+00:00",
                                "task_name": "guarded_trade_buy",
                                "code": "000001",
                                "price": "10.50",
                                "quantity": 200,
                                "trade_ok": False,
                                "contract_no": "B202604260601",
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-26T02:00:00+00:00",
                                "task_name": "guarded_trade_buy",
                                "code": "000002",
                                "price": "8.00",
                                "quantity": 100,
                                "trade_ok": True,
                                "contract_no": "B202604260602",
                            },
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            manager = TdxTaskManager(
                profile="trade_period_report",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir, "export_stem": "period-view"},
            )
            result = manager.trade_period_report(
                start_date="2026-04-25",
                end_date="2026-04-26",
                timezone_name="UTC",
                json_output_path=str(Path(temp_dir) / "period.json"),
            )
            json_path = Path(result.data["artifacts"]["json_output_path"])
            csv_path = Path(result.data["artifacts"]["csv_output_path"])
            by_day_rows = {row["report_date"]: row for row in result.data["by_day"]}
            self.assertTrue(result.ok)
            self.assertEqual(result.data["summary"]["report_entries"], 3)
            self.assertEqual(result.data["summary"]["trade_days"], 2)
            self.assertEqual(result.data["summary"]["total_quantity"], 400)
            self.assertEqual(result.data["summary"]["total_amount"], 3900.0)
            self.assertEqual(by_day_rows["2026-04-25"]["entries_count"], 1)
            self.assertEqual(by_day_rows["2026-04-26"]["entries_count"], 2)
            self.assertTrue(json_path.exists())
            self.assertTrue(csv_path.exists())
            self.assertIn("trade_days", json_path.read_text(encoding="utf-8"))
            self.assertIn("report_date", csv_path.read_text(encoding="utf-8"))

    def test_task_trade_period_report_requires_boundary(self) -> None:
        manager = TdxTaskManager(profile="trade_period_report", strategy_path="strategy.py")
        result = manager.trade_period_report()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)

    def test_task_sector_research_export_writes_json_and_csv(self) -> None:
        sector_result = Result(ok=True, code=ErrorCode.OK, message="ok", data={"stocks": [{"code": "000001"}]})
        metrics_result = Result(ok=True, code=ErrorCode.OK, message="ok", data={"rows": [{"code": "000001", "Now": 10.5}]})
        with TemporaryDirectory() as temp_dir:
            manager = TdxTaskManager(
                profile="sector_research_export",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir, "export_stem": "sector"},
            )
            with (
                patch.object(type(manager.api_manager.meta), "sector_stocks", return_value=sector_result),
                patch.object(type(manager.api_manager.meta), "gp_one_data", return_value=metrics_result),
            ):
                result = manager.sector_research_export(block_code="ZXG")
            json_path = Path(result.data["artifacts"]["json_output_path"])
            csv_path = Path(result.data["artifacts"]["csv_output_path"])
            self.assertTrue(json_path.exists())
            self.assertTrue(csv_path.exists())
            self.assertIn("stock_codes", json_path.read_text(encoding="utf-8"))
            self.assertIn("Now", csv_path.read_text(encoding="utf-8"))
            self.assertEqual(result.data["task"]["name"], "sector_research_export")

    def test_task_trade_buy_can_refresh_before_trade(self) -> None:
        refresh_result = Result(ok=True, code=ErrorCode.OK, message="refreshed", data={})
        trade_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "artifacts": {"last_order_state_path": "runtime/pingan-last-order.json"},
                "result_dialog": {"contract_no": "B202604260003"},
            },
        )
        manager = TdxTaskManager(profile="trade_buy", strategy_path="strategy.py")
        with (
            patch.object(type(manager.api_manager), "refresh_cache", return_value=refresh_result) as mocked_refresh,
            patch.object(type(manager.trade_manager.pingan), "buy", return_value=trade_result) as mocked_trade,
        ):
            result = manager.trade_buy(
                port="COM3",
                code="000001",
                price="10.00",
                quantity=100,
                submission_key="task-buy-001",
                max_price=10.50,
                refresh_before_trade=True,
            )
        mocked_refresh.assert_called_once_with(market="AG", force=False)
        mocked_trade.assert_called_once_with(
            port="COM3",
            baudrate=115200,
            timeout=2.0,
            code="000001",
            price="10.00",
            quantity=100,
            max_depth=12,
            close_result_dialog=True,
            submission_key="task-buy-001",
            max_price=10.50,
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.data["task"]["name"], "trade_buy")
        self.assertEqual(result.data["result_dialog"]["contract_no"], "B202604260003")
        self.assertEqual(result.data["input"]["submission_key"], "task-buy-001")
        self.assertEqual(result.data["input"]["max_price"], 10.50)

    def test_task_trade_submit_once_uses_trade_manager_profile(self) -> None:
        trade_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "artifacts": {"last_order_state_path": "runtime/pingan-last-order.json"},
                "result_dialog": {"contract_no": "B202604260004"},
            },
        )
        manager = TdxTaskManager(profile="trade_submit_once", strategy_path="strategy.py")
        with patch.object(type(manager.trade_manager.pingan), "buy_submit_once", return_value=trade_result) as mocked_trade:
            result = manager.trade_submit_once(
                port="COM3",
                code="000001",
                price="10.00",
                quantity=100,
                submission_key="task-submit-001",
                max_price=10.50,
            )
        mocked_trade.assert_called_once_with(
            port="COM3",
            baudrate=115200,
            timeout=2.0,
            code="000001",
            price="10.00",
            quantity=100,
            max_depth=12,
            close_result_dialog=True,
            submission_key="task-submit-001",
            max_price=10.50,
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.data["task"]["name"], "trade_submit_once")
        self.assertIn("task_call", result.data["timing"])
        self.assertEqual(result.data["input"]["submission_key"], "task-submit-001")
        self.assertEqual(result.data["input"]["max_price"], 10.50)

    def test_task_trade_submit_ready_can_refresh_before_submit_boundary(self) -> None:
        refresh_result = Result(ok=True, code=ErrorCode.OK, message="refreshed", data={})
        trade_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ready",
            data={
                "submit_ready": {"overall_status": "ok", "manual_confirmation_required": True},
                "trade_safety": {"side_effect_level": "local_state_mutating"},
            },
        )
        manager = TdxTaskManager(profile="trade_submit_ready", strategy_path="strategy.py")
        with (
            patch.object(type(manager.api_manager), "refresh_cache", return_value=refresh_result) as mocked_refresh,
            patch.object(type(manager.trade_manager.pingan), "submit_ready", return_value=trade_result) as mocked_submit_ready,
        ):
            result = manager.trade_submit_ready(
                port="COM3",
                code="000001",
                price="10.00",
                quantity=100,
                max_price=10.20,
                refresh_before_trade=True,
                dialog_lookup_mode="win32_experimental",
                confirm_timeout=2.5,
            )
        mocked_refresh.assert_called_once_with(market="AG", force=False)
        mocked_submit_ready.assert_called_once_with(
            port="COM3",
            baudrate=115200,
            timeout=2.0,
            code="000001",
            price="10.00",
            quantity=100,
            max_depth=12,
            max_price=10.20,
            dialog_lookup_mode="win32_experimental",
            confirm_timeout=2.5,
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.data["input"]["refresh_before_trade"], True)
        self.assertEqual(result.data["refresh_result"]["message"], "refreshed")
        self.assertEqual(result.data["trade_result"]["data"]["submit_ready"]["overall_status"], "ok")
        self.assertEqual(result.data["task"]["name"], "trade_submit_ready")

    def test_task_trade_confirm_current_uses_trade_manager_boundary_workflow(self) -> None:
        trade_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="confirmed",
            data={
                "confirm_current": {"overall_status": "ok", "confirmation_advanced": True},
                "result_dialog": {"title": "提示"},
                "artifacts": {"last_order_state_path": "runtime/pingan-last-order.json"},
                "trade_safety": {"side_effect_level": "live_side_effecting"},
            },
        )
        manager = TdxTaskManager(profile="trade_confirm_current", strategy_path="strategy.py")
        with patch.object(type(manager.trade_manager.pingan), "confirm_current", return_value=trade_result) as mocked_confirm:
            result = manager.trade_confirm_current(
                dialog_lookup_mode="win32_experimental",
                confirm_timeout=2.0,
                result_timeout=3.0,
                close_result_dialog=False,
                result_close_pre_delay=0.3,
            )
        mocked_confirm.assert_called_once_with(
            dialog_lookup_mode="win32_experimental",
            confirm_timeout=2.0,
            result_timeout=3.0,
            close_result_dialog=False,
            result_close_pre_delay=0.3,
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.data["input"]["close_result_dialog"], False)
        self.assertEqual(result.data["trade_result"]["data"]["confirm_current"]["overall_status"], "ok")
        self.assertEqual(result.data["result_dialog"]["title"], "提示")
        self.assertEqual(result.data["task"]["name"], "trade_confirm_current")

    def test_task_guarded_trade_buy_runs_prechecks_and_writes_report(self) -> None:
        snapshot_result = Result(ok=True, code=ErrorCode.OK, message="ok", data={"rows": [{"Now": 10.2}]})
        block_result = Result(ok=True, code=ErrorCode.OK, message="ok", data={"stocks": [{"code": "000001"}]})
        trade_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "artifacts": {"last_order_state_path": "runtime/pingan-last-order.json"},
                "result_dialog": {"contract_no": "B202604260005"},
            },
        )
        with TemporaryDirectory() as temp_dir:
            manager = TdxTaskManager(
                profile="guarded_trade_buy",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir, "export_stem": "guarded"},
            )
            with (
                patch.object(type(manager.api_manager.market), "snapshot", return_value=snapshot_result) as mocked_snapshot,
                patch.object(type(manager.api_manager.meta), "sector_stocks", return_value=block_result) as mocked_block,
                patch.object(type(manager), "trade_buy", return_value=trade_result) as mocked_trade_buy,
            ):
                result = manager.guarded_trade_buy(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="guarded-task-001",
                    max_price=10.40,
                    max_snapshot_price=10.5,
                    required_block_code="ZXG",
                )
            mocked_snapshot.assert_called_once_with("000001", fields=["Now"])
            mocked_block.assert_called_once_with(block_code="ZXG", block_type=0, list_type=None)
            mocked_trade_buy.assert_called_once_with(
                port="COM3",
                code="000001",
                price="10.00",
                quantity=100,
                baudrate=115200,
                timeout=2.0,
                max_depth=12,
                close_result_dialog=True,
                submission_key="guarded-task-001",
                max_price=10.40,
                refresh_before_trade=None,
                refresh_market=None,
                refresh_force=None,
            )
            json_path = Path(result.data["artifacts"]["json_output_path"])
            csv_path = Path(result.data["artifacts"]["csv_output_path"])
            ledger_jsonl_path = Path(result.data["artifacts"]["ledger_jsonl_path"])
            ledger_csv_path = Path(result.data["artifacts"]["ledger_csv_path"])
            self.assertTrue(json_path.exists())
            self.assertTrue(csv_path.exists())
            self.assertTrue(ledger_jsonl_path.exists())
            self.assertTrue(ledger_csv_path.exists())
            self.assertEqual(result.data["input"]["submission_key"], "guarded-task-001")
            self.assertEqual(result.data["input"]["max_price"], 10.40)
            self.assertIn("guarded_trade_buy", ledger_jsonl_path.read_text(encoding="utf-8"))
            self.assertIn("contract_no", ledger_csv_path.read_text(encoding="utf-8"))
            self.assertEqual(result.data["task"]["name"], "guarded_trade_buy")
            self.assertEqual(result.data["result_dialog"]["contract_no"], "B202604260005")

    def test_task_guarded_trade_buy_blocks_when_snapshot_price_is_too_high(self) -> None:
        snapshot_result = Result(ok=True, code=ErrorCode.OK, message="ok", data={"rows": [{"Now": 10.8}]})
        manager = TdxTaskManager(profile="guarded_trade_buy", strategy_path="strategy.py")
        with (
            patch.object(type(manager.api_manager.market), "snapshot", return_value=snapshot_result) as mocked_snapshot,
            patch.object(type(manager), "trade_buy") as mocked_trade_buy,
        ):
            result = manager.guarded_trade_buy(
                port="COM3",
                code="000001",
                price="10.00",
                quantity=100,
                max_snapshot_price=10.5,
            )
        mocked_snapshot.assert_called_once_with("000001", fields=["Now"])
        mocked_trade_buy.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)

    def test_task_guarded_trade_buy_runs_formula_precheck(self) -> None:
        snapshot_result = Result(ok=True, code=ErrorCode.OK, message="ok", data={"rows": [{"Now": 10.2}]})
        formula_result = Result(ok=True, code=ErrorCode.OK, message="ok", data={"rows": [{"code": "000001"}]})
        trade_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "artifacts": {"last_order_state_path": "runtime/pingan-last-order.json"},
                "result_dialog": {"contract_no": "B202604260006"},
            },
        )
        with TemporaryDirectory() as temp_dir:
            manager = TdxTaskManager(
                profile="guarded_trade_buy",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir, "export_stem": "guarded-formula"},
            )
            with (
                patch.object(type(manager.api_manager.market), "snapshot", return_value=snapshot_result),
                patch.object(type(manager), "formula_scan", return_value=formula_result) as mocked_formula_scan,
                patch.object(type(manager), "trade_buy", return_value=trade_result) as mocked_trade_buy,
            ):
                result = manager.guarded_trade_buy(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    max_snapshot_price=10.5,
                    formula_name="SCAN",
                )
            mocked_formula_scan.assert_called_once_with(
                formula_name="SCAN",
                stock_list=["000001"],
                formula_arg="",
                return_count=1,
                return_date=False,
                stock_period="1d",
                start_time="",
                end_time="",
                count=0,
                dividend_type=0,
            )
            mocked_trade_buy.assert_called_once()
            self.assertTrue(result.data["prechecks"]["formula_check_passed"])

    def test_task_guarded_trade_buy_blocks_when_formula_does_not_match(self) -> None:
        formula_result = Result(ok=True, code=ErrorCode.OK, message="ok", data={"rows": []})
        manager = TdxTaskManager(profile="guarded_trade_buy", strategy_path="strategy.py")
        with (
            patch.object(type(manager), "formula_scan", return_value=formula_result) as mocked_formula_scan,
            patch.object(type(manager), "trade_buy") as mocked_trade_buy,
        ):
            result = manager.guarded_trade_buy(
                port="COM3",
                code="000001",
                price="10.00",
                quantity=100,
                formula_name="SCAN",
            )
        mocked_formula_scan.assert_called_once()
        mocked_trade_buy.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)


if __name__ == "__main__":
    unittest.main()
