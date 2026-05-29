import argparse
import io
import json
import unittest
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, mock_open, patch

from tdxquant.cli import (
    _handle_api_subcommand,
    _handle_bridge_subcommand,
    _handle_catalog_subcommand,
    _handle_provider_replay_subcommand,
    _handle_report_subcommand,
    _select_catalog_output_payload,
    _run_flat_replay_provider_command,
    _handle_task_subcommand,
    _handle_trade_subcommand,
    _run_trade_buy,
    _run_trade_broker_capabilities,
    _run_trade_confirm_current,
    _run_trade_sell,
    _run_trade_submit_ready,
    _run_trade_dialog_readiness,
    _run_trade_health,
    _run_trade_preflight,
    _run_trade_submit_once,
    build_parser,
    main,
)
from tdxquant.models import ErrorCode, Result
from tdxquant.trader.models import OrderSide, OrderStatus, SecurityOrderSnapshot


def _trader_ts(value: str = "2026-04-30T10:00:00+00:00") -> datetime:
    return datetime.fromisoformat(value).astimezone(UTC)


def _snapshot(
    *,
    gateway_order_id: str,
    status: OrderStatus = OrderStatus.SUBMITTED,
    reject_reason: str = "",
) -> SecurityOrderSnapshot:
    return SecurityOrderSnapshot(
        gateway_order_id=gateway_order_id,
        client_order_id=f"client-{gateway_order_id}",
        broker_order_id=f"broker-{gateway_order_id}" if status == OrderStatus.SUBMITTED else None,
        broker="pingan_desktop",
        symbol="000001",
        market="SZ",
        side=OrderSide.BUY,
        status=status,
        requested_quantity=100,
        filled_quantity=0,
        remaining_quantity=100,
        limit_price=Decimal("10.00"),
        avg_fill_price=Decimal("0"),
        reject_reason=reject_reason,
        placed_at=_trader_ts(),
        updated_at=_trader_ts(),
        source="live",
    )


class ApiCliParserTests(unittest.TestCase):
    def test_bridge_serve_command_requires_config(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["bridge", "serve"])

    def test_bridge_serve_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["bridge", "serve", "--config", "runtime/bridge/worker-bridge.json"])
        self.assertEqual(args.command, "bridge")
        self.assertEqual(args.bridge_command, "serve")
        self.assertEqual(args.config, "runtime/bridge/worker-bridge.json")

    def test_bridge_watch_status_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "bridge",
                "watch-status",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--heartbeat-stale-after-seconds",
                "60",
                "--watermark-stale-after-seconds",
                "120",
                "--reconnect-stale-after-seconds",
                "180",
            ]
        )
        self.assertEqual(args.command, "bridge")
        self.assertEqual(args.bridge_command, "watch-status")
        self.assertEqual(args.registry, "runtime/bridge/master-workers.json")
        self.assertEqual(args.worker, "worker-a")
        self.assertEqual(args.heartbeat_stale_after_seconds, 60.0)
        self.assertEqual(args.watermark_stale_after_seconds, 120.0)
        self.assertEqual(args.reconnect_stale_after_seconds, 180.0)
        self.assertEqual(args.view, "detailed")

    def test_bridge_watch_status_summary_view_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "bridge",
                "watch-status",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--view",
                "summary",
            ]
        )
        self.assertEqual(args.command, "bridge")
        self.assertEqual(args.bridge_command, "watch-status")
        self.assertEqual(args.view, "summary")

    def test_bridge_watch_status_diagnostics_view_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "bridge",
                "watch-status",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--view",
                "diagnostics",
            ]
        )
        self.assertEqual(args.command, "bridge")
        self.assertEqual(args.bridge_command, "watch-status")
        self.assertEqual(args.view, "diagnostics")

    def test_bridge_watch_status_runbook_view_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "bridge",
                "watch-status",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--view",
                "runbook",
            ]
        )
        self.assertEqual(args.command, "bridge")
        self.assertEqual(args.bridge_command, "watch-status")
        self.assertEqual(args.view, "runbook")

    def test_bridge_watch_events_commands_parse(self) -> None:
        parser = build_parser()
        events = parser.parse_args(
            [
                "bridge",
                "watch-events",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--run-id",
                "run-001",
                "--tail",
                "25",
            ]
        )
        stream = parser.parse_args(
            [
                "bridge",
                "watch-events-stream",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--run-id",
                "run-001",
                "--from",
                "run-001:event:7",
                "--no-follow",
                "--heartbeat-seconds",
                "5",
            ]
        )

        self.assertEqual(events.bridge_command, "watch-events")
        self.assertEqual(events.run_id, "run-001")
        self.assertEqual(events.tail, 25)
        self.assertEqual(stream.bridge_command, "watch-events-stream")
        self.assertEqual(stream.from_cursor, "run-001:event:7")
        self.assertFalse(stream.follow)
        self.assertEqual(stream.heartbeat_seconds, 5)

    def test_bridge_watch_start_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "bridge",
                "watch-start",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--code",
                "000001.SZ",
                "--code",
                "600519.SH",
                "--max-events",
                "5",
                "--max-seconds",
                "30",
                "--poll-interval",
                "0.5",
                "--idempotency-key",
                "idem-001",
            ]
        )
        self.assertEqual(args.bridge_command, "watch-start")
        self.assertEqual(args.code, ["000001.SZ", "600519.SH"])
        self.assertEqual(args.max_events, 5)
        self.assertEqual(args.max_seconds, 30.0)
        self.assertEqual(args.poll_interval, 0.5)
        self.assertEqual(args.idempotency_key, "idem-001")

    def test_bridge_watch_start_command_requires_registry_worker_and_code(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["bridge", "watch-start"])

    def test_bridge_watch_stop_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["bridge", "watch-stop", "--registry", "runtime/bridge/master-workers.json", "--worker", "worker-a"])
        self.assertEqual(args.bridge_command, "watch-stop")
        self.assertEqual(args.registry, "runtime/bridge/master-workers.json")
        self.assertEqual(args.worker, "worker-a")

    def test_bridge_watch_restart_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "bridge",
                "watch-restart",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--reason",
                "operator_restart",
                "--grace-period-seconds",
                "2",
            ]
        )
        self.assertEqual(args.bridge_command, "watch-restart")
        self.assertEqual(args.registry, "runtime/bridge/master-workers.json")
        self.assertEqual(args.worker, "worker-a")
        self.assertEqual(args.reason, "operator_restart")
        self.assertEqual(args.grace_period_seconds, 2)

    def test_bridge_watch_restart_preflight_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "bridge",
                "watch-restart-preflight",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
            ]
        )
        self.assertEqual(args.bridge_command, "watch-restart-preflight")
        self.assertEqual(args.registry, "runtime/bridge/master-workers.json")
        self.assertEqual(args.worker, "worker-a")

    def test_bridge_watch_supervisor_tick_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "bridge",
                "watch-supervisor-tick",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--reason",
                "manual_tick",
            ]
        )
        self.assertEqual(args.bridge_command, "watch-supervisor-tick")
        self.assertEqual(args.registry, "runtime/bridge/master-workers.json")
        self.assertEqual(args.worker, "worker-a")
        self.assertEqual(args.reason, "manual_tick")

    def test_bridge_watch_supervisor_run_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "bridge",
                "watch-supervisor-run",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--max-ticks",
                "3",
                "--interval-seconds",
                "0.25",
                "--reason",
                "manual_supervise",
            ]
        )
        self.assertEqual(args.bridge_command, "watch-supervisor-run")
        self.assertEqual(args.registry, "runtime/bridge/master-workers.json")
        self.assertEqual(args.worker, "worker-a")
        self.assertEqual(args.max_ticks, 3)
        self.assertEqual(args.interval_seconds, 0.25)
        self.assertEqual(args.reason, "manual_supervise")

    def test_bridge_watch_supervisor_daemon_status_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "bridge",
                "watch-supervisor-daemon-status",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
            ]
        )
        self.assertEqual(args.bridge_command, "watch-supervisor-daemon-status")
        self.assertEqual(args.registry, "runtime/bridge/master-workers.json")
        self.assertEqual(args.worker, "worker-a")

    def test_bridge_watch_supervisor_daemon_start_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "bridge",
                "watch-supervisor-daemon-start",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--max-ticks",
                "3",
                "--interval-seconds",
                "0.25",
                "--loop-sleep-seconds",
                "1.5",
                "--reason",
                "manual_daemon_start",
                "--owner-token",
                "owner-1",
            ]
        )
        self.assertEqual(args.bridge_command, "watch-supervisor-daemon-start")
        self.assertEqual(args.registry, "runtime/bridge/master-workers.json")
        self.assertEqual(args.worker, "worker-a")
        self.assertEqual(args.max_ticks, 3)
        self.assertEqual(args.interval_seconds, 0.25)
        self.assertEqual(args.loop_sleep_seconds, 1.5)
        self.assertEqual(args.reason, "manual_daemon_start")
        self.assertEqual(args.owner_token, "owner-1")

    def test_bridge_watch_supervisor_daemon_stop_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "bridge",
                "watch-supervisor-daemon-stop",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--owner-token",
                "owner-1",
                "--reason",
                "manual_daemon_stop",
            ]
        )
        self.assertEqual(args.bridge_command, "watch-supervisor-daemon-stop")
        self.assertEqual(args.registry, "runtime/bridge/master-workers.json")
        self.assertEqual(args.worker, "worker-a")
        self.assertEqual(args.owner_token, "owner-1")
        self.assertEqual(args.reason, "manual_daemon_stop")

    def test_api_capabilities_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "capabilities"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "capabilities")

    def test_api_health_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "health", "--window-key", "平安证券", "--hid-port", "COM3"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "health")
        self.assertEqual(args.window_key, "平安证券")
        self.assertEqual(args.hid_port, "COM3")

    def test_api_subscription_one_shot_commands_parse(self) -> None:
        parser = build_parser()
        subscribe = parser.parse_args(["api", "subscription-subscribe", "--code", "688318.SH", "--code", "600519.SH"])
        unsubscribe = parser.parse_args(["api", "subscription-unsubscribe", "--code", "688318.SH"])
        listing = parser.parse_args(["api", "subscription-list"])

        self.assertEqual(subscribe.api_command, "subscription-subscribe")
        self.assertEqual(subscribe.code, ["688318.SH", "600519.SH"])
        self.assertEqual(unsubscribe.api_command, "subscription-unsubscribe")
        self.assertEqual(unsubscribe.code, ["688318.SH"])
        self.assertEqual(listing.api_command, "subscription-list")

    def test_api_doctor_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "doctor", "--window-key", "通达信金融终端"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "doctor")
        self.assertEqual(args.window_key, "通达信金融终端")

    def test_api_snapshot_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "snapshot", "--code", "688260.SH"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "snapshot")
        self.assertEqual(args.code, "688260.SH")
        self.assertEqual(args.profile, "default")

    def test_api_market_snapshot_command_parses_replay_arguments(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "market-snapshot",
                "--code",
                "000001.SZ",
                "--field",
                "Now",
                "--field",
                "Volume",
                "--provider-mode",
                "replay",
            ]
        )
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "market-snapshot")
        self.assertEqual(args.code, "000001.SZ")
        self.assertEqual(args.field, ["Now", "Volume"])
        self.assertEqual(args.provider_mode, "replay")

    def test_api_sector_list_command_parses_replay_arguments(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "sector-list", "--list-type", "0", "--provider-mode", "replay"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "sector-list")
        self.assertEqual(args.list_type, 0)
        self.assertEqual(args.provider_mode, "replay")

    def test_api_sector_stocks_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "sector-stocks", "--sector", "钛金属", "--list-type", "1"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "sector-stocks")
        self.assertEqual(args.sector, "钛金属")
        self.assertEqual(args.list_type, 1)

    def test_api_block_read_watchlist_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "block-read-watchlist", "--block-code", "ZXG"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "block-read-watchlist")
        self.assertEqual(args.block_code, "ZXG")

    def test_api_formula_xg_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "formula-xg", "--formula-name", "MY_FORMULA"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "formula-xg")
        self.assertEqual(args.formula_name, "MY_FORMULA")

    def test_api_formula_capabilities_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "formula-capabilities"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "formula-capabilities")

    def test_api_formula_screen_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "formula-screen",
                "--formula-name",
                "UPN",
                "--code",
                "000001.SZ",
                "--return-count",
                "3",
                "--return-date",
            ]
        )
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "formula-screen")
        self.assertEqual(args.formula_name, "UPN")
        self.assertEqual(args.code, ["000001.SZ"])
        self.assertEqual(args.return_count, 3)
        self.assertTrue(args.return_date)

    def test_api_formula_screen_replay_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "formula-screen",
                "--formula-name",
                "UPN",
                "--code",
                "000001.SZ",
                "--provider-mode",
                "replay",
                "--fixture",
                "formula-screen-failure",
            ]
        )
        self.assertEqual(args.provider_mode, "replay")
        self.assertEqual(args.fixture, "formula-screen-failure")
        self.assertIsNone(args.fixture_path)

    def test_api_replay_fixture_and_fixture_path_are_mutually_exclusive(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(
                [
                    "api",
                    "formula-screen",
                    "--formula-name",
                    "UPN",
                    "--code",
                    "000001.SZ",
                    "--provider-mode",
                    "replay",
                    "--fixture",
                    "formula-screen-success",
                    "--fixture-path",
                    "runtime/custom.json",
                ]
            )

    def test_api_kline_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "kline", "--code", "688260.SH", "--period", "1d", "--fill-data"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "kline")
        self.assertEqual(args.code, ["688260.SH"])
        self.assertEqual(args.period, "1d")
        self.assertTrue(args.fill_data)

    def test_api_full_tick_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "full-tick", "--code", "688260.SH"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "full-tick")
        self.assertEqual(args.code, "688260.SH")

    def test_api_full_tick_command_parses_replay_arguments(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "full-tick",
                "--code",
                "688260.SH",
                "--field",
                "Now",
                "--field",
                "Volume",
                "--provider-mode",
                "replay",
            ]
        )
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "full-tick")
        self.assertEqual(args.code, "688260.SH")
        self.assertEqual(args.field, ["Now", "Volume"])
        self.assertEqual(args.provider_mode, "replay")

    def test_api_trading_dates_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "trading-dates", "--market", "SH", "--count", "10"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "trading-dates")
        self.assertEqual(args.market, "SH")
        self.assertEqual(args.count, 10)

    def test_api_refresh_kline_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "refresh-kline", "--code", "688260.SH", "--period", "1d"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "refresh-kline")
        self.assertEqual(args.code, ["688260.SH"])
        self.assertEqual(args.period, "1d")

    def test_api_download_file_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "download-file", "--code", "688318.SH", "--down-time", "20250101", "--down-type", "2"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "download-file")
        self.assertEqual(args.code, "688318.SH")
        self.assertEqual(args.down_time, "20250101")
        self.assertEqual(args.down_type, 2)

    def test_api_send_warn_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "send-warn",
                "--code",
                "688318.SH",
                "--code",
                "600519.SH",
                "--time",
                "20251215141115",
                "--time",
                "20251215142100",
                "--price",
                "123.45",
                "--close",
                "122.50",
                "--volume",
                "1000",
                "--bs-flag",
                "0",
                "--warn-type",
                "0",
                "--reason",
                "价格突破预警线",
                "--count",
                "2",
            ]
        )
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "send-warn")
        self.assertEqual(args.code, ["688318.SH", "600519.SH"])
        self.assertEqual(args.time, ["20251215141115", "20251215142100"])
        self.assertEqual(args.price, ["123.45"])
        self.assertEqual(args.close, ["122.50"])
        self.assertEqual(args.volume, ["1000"])
        self.assertEqual(args.bs_flag, ["0"])
        self.assertEqual(args.warn_type, ["0"])
        self.assertEqual(args.reason, ["价格突破预警线"])
        self.assertEqual(args.count, 2)

    def test_api_send_warn_command_requires_time(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["api", "send-warn", "--code", "688318.SH"])

    def test_tdx_send_warn_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-send-warn",
                "--code",
                "688318.SH",
                "--time",
                "20251215141115",
                "--price",
                "123.45",
                "--close",
                "122.50",
                "--volume",
                "1000",
                "--bs-flag",
                "0",
                "--warn-type",
                "0",
                "--reason",
                "价格突破预警线",
                "--count",
                "1",
            ]
        )
        self.assertEqual(args.command, "tdx-send-warn")
        self.assertEqual(args.code, ["688318.SH"])
        self.assertEqual(args.time, ["20251215141115"])
        self.assertEqual(args.price, ["123.45"])
        self.assertEqual(args.close, ["122.50"])
        self.assertEqual(args.volume, ["1000"])
        self.assertEqual(args.bs_flag, ["0"])
        self.assertEqual(args.warn_type, ["0"])
        self.assertEqual(args.reason, ["价格突破预警线"])
        self.assertEqual(args.count, 1)

    def test_tdx_capabilities_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["tdx-capabilities"])
        self.assertEqual(args.command, "tdx-capabilities")

    def test_tdx_capabilities_replay_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["tdx-capabilities", "--provider-mode", "replay", "--fixture", "runtime-capabilities-success"]
        )
        self.assertEqual(args.command, "tdx-capabilities")
        self.assertEqual(args.provider_mode, "replay")
        self.assertEqual(args.fixture, "runtime-capabilities-success")

    def test_tdx_health_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["tdx-health", "--window-key", "平安证券", "--hid-port", "COM5"])
        self.assertEqual(args.command, "tdx-health")
        self.assertEqual(args.window_key, "平安证券")
        self.assertEqual(args.hid_port, "COM5")

    def test_tdx_doctor_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["tdx-doctor", "--window-key", "通达信金融终端"])
        self.assertEqual(args.command, "tdx-doctor")
        self.assertEqual(args.window_key, "通达信金融终端")

    def test_tdx_formula_screen_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["tdx-formula-screen", "--formula-name", "UPN", "--code", "000001.SZ"])
        self.assertEqual(args.command, "tdx-formula-screen")
        self.assertEqual(args.formula_name, "UPN")
        self.assertEqual(args.code, ["000001.SZ"])

    def test_tdx_block_read_watchlist_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["tdx-block-read-watchlist", "--block-code", "ZXG"])
        self.assertEqual(args.command, "tdx-block-read-watchlist")
        self.assertEqual(args.block_code, "ZXG")

    def test_api_divid_factors_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "divid-factors", "--code", "688318.SH", "--start-time", "20200101", "--end-time", "20241231"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "divid-factors")
        self.assertEqual(args.code, "688318.SH")
        self.assertEqual(args.start_time, "20200101")
        self.assertEqual(args.end_time, "20241231")

    def test_api_ipo_info_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "ipo-info", "--ipo-type", "2", "--ipo-date", "1"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "ipo-info")
        self.assertEqual(args.ipo_type, 2)
        self.assertEqual(args.ipo_date, 1)

    def test_api_financial_data_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "financial-data",
                "--code",
                "688318.SH",
                "--field",
                "FN1",
                "--field",
                "FN2",
                "--start-time",
                "20240101",
                "--end-time",
                "20241231",
                "--report-type",
                "announce_time",
            ]
        )
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "financial-data")
        self.assertEqual(args.code, ["688318.SH"])
        self.assertEqual(args.field, ["FN1", "FN2"])
        self.assertEqual(args.start_time, "20240101")
        self.assertEqual(args.end_time, "20241231")
        self.assertEqual(args.report_type, "announce_time")

    def test_api_financial_data_by_date_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "financial-data-by-date",
                "--code",
                "688318.SH",
                "--field",
                "FN193",
                "--year",
                "2025",
                "--mmdd",
                "331",
            ]
        )
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "financial-data-by-date")
        self.assertEqual(args.code, ["688318.SH"])
        self.assertEqual(args.field, ["FN193"])
        self.assertEqual(args.year, 2025)
        self.assertEqual(args.mmdd, 331)

    def test_api_financial_data_command_requires_field(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["api", "financial-data", "--code", "688318.SH"])

    def test_api_stock_transaction_data_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "stock-transaction-data",
                "--code",
                "600519.SH",
                "--field",
                "GP01",
                "--field",
                "GP02",
                "--start-time",
                "20240101",
                "--end-time",
                "20241231",
            ]
        )
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "stock-transaction-data")
        self.assertEqual(args.code, ["600519.SH"])
        self.assertEqual(args.field, ["GP01", "GP02"])
        self.assertEqual(args.start_time, "20240101")
        self.assertEqual(args.end_time, "20241231")

    def test_api_stock_transaction_data_by_date_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "stock-transaction-data-by-date",
                "--code",
                "600519.SH",
                "--field",
                "GP01",
                "--year",
                "0",
                "--mmdd",
                "0",
            ]
        )
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "stock-transaction-data-by-date")
        self.assertEqual(args.code, ["600519.SH"])
        self.assertEqual(args.field, ["GP01"])
        self.assertEqual(args.year, 0)
        self.assertEqual(args.mmdd, 0)

    def test_api_stock_transaction_data_command_requires_field(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["api", "stock-transaction-data", "--code", "600519.SH"])

    def test_tdx_data_stock_transaction_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-stock-transaction",
                "--code",
                "600519.SH",
                "--field",
                "GP01",
                "--field",
                "GP02",
                "--start-time",
                "20240101",
                "--end-time",
                "20241231",
            ]
        )
        self.assertEqual(args.command, "tdx-data-stock-transaction")
        self.assertEqual(args.code, ["600519.SH"])
        self.assertEqual(args.field, ["GP01", "GP02"])
        self.assertEqual(args.start_time, "20240101")
        self.assertEqual(args.end_time, "20241231")

    def test_tdx_data_market_snapshot_command_parses_replay_arguments(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-market-snapshot",
                "--code",
                "000001.SZ",
                "--field",
                "Now",
                "--field",
                "Volume",
                "--provider-mode",
                "replay",
            ]
        )
        self.assertEqual(args.command, "tdx-data-market-snapshot")
        self.assertEqual(args.code, "000001.SZ")
        self.assertEqual(args.field, ["Now", "Volume"])
        self.assertEqual(args.provider_mode, "replay")

    def test_tdx_data_stock_transaction_by_date_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-stock-transaction-by-date",
                "--code",
                "600519.SH",
                "--field",
                "GP01",
                "--year",
                "0",
                "--mmdd",
                "0",
            ]
        )
        self.assertEqual(args.command, "tdx-data-stock-transaction-by-date")
        self.assertEqual(args.code, ["600519.SH"])
        self.assertEqual(args.field, ["GP01"])
        self.assertEqual(args.year, 0)
        self.assertEqual(args.mmdd, 0)

    def test_tdx_data_stock_transaction_by_date_command_parses_replay_arguments(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-stock-transaction-by-date",
                "--code",
                "000001.SZ",
                "--field",
                "price",
                "--year",
                "2025",
                "--mmdd",
                "101",
                "--provider-mode",
                "replay",
            ]
        )
        self.assertEqual(args.command, "tdx-data-stock-transaction-by-date")
        self.assertEqual(args.provider_mode, "replay")
        self.assertEqual(args.code, ["000001.SZ"])
        self.assertEqual(args.field, ["price"])
        self.assertEqual(args.year, 2025)
        self.assertEqual(args.mmdd, 101)

    def test_tdx_data_sector_list_command_parses_replay_arguments(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["tdx-data-sector-list", "--list-type", "0", "--provider-mode", "replay"])
        self.assertEqual(args.command, "tdx-data-sector-list")
        self.assertEqual(args.list_type, 0)
        self.assertEqual(args.provider_mode, "replay")

    def test_api_sector_transaction_data_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "sector-transaction-data",
                "--code",
                "880660.SH",
                "--field",
                "BK5",
                "--field",
                "BK6",
                "--start-time",
                "20240101",
                "--end-time",
                "20241231",
            ]
        )
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "sector-transaction-data")
        self.assertEqual(args.code, ["880660.SH"])
        self.assertEqual(args.field, ["BK5", "BK6"])
        self.assertEqual(args.start_time, "20240101")
        self.assertEqual(args.end_time, "20241231")

    def test_api_sector_transaction_data_by_date_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "sector-transaction-data-by-date",
                "--code",
                "880660.SH",
                "--field",
                "BK9",
                "--year",
                "0",
                "--mmdd",
                "0",
            ]
        )
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "sector-transaction-data-by-date")
        self.assertEqual(args.code, ["880660.SH"])
        self.assertEqual(args.field, ["BK9"])
        self.assertEqual(args.year, 0)
        self.assertEqual(args.mmdd, 0)

    def test_api_sector_transaction_data_command_requires_field(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["api", "sector-transaction-data", "--code", "880660.SH"])

    def test_tdx_data_sector_transaction_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-sector-transaction",
                "--code",
                "880660.SH",
                "--field",
                "BK5",
                "--field",
                "BK6",
                "--start-time",
                "20240101",
                "--end-time",
                "20241231",
            ]
        )
        self.assertEqual(args.command, "tdx-data-sector-transaction")
        self.assertEqual(args.code, ["880660.SH"])
        self.assertEqual(args.field, ["BK5", "BK6"])
        self.assertEqual(args.start_time, "20240101")
        self.assertEqual(args.end_time, "20241231")

    def test_tdx_data_sector_transaction_command_parses_replay_arguments(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-sector-transaction",
                "--code",
                "880660.SH",
                "--code",
                "880001.SH",
                "--field",
                "BK5",
                "--field",
                "BK6",
                "--start-time",
                "20240101",
                "--end-time",
                "20241231",
                "--provider-mode",
                "replay",
            ]
        )
        self.assertEqual(args.command, "tdx-data-sector-transaction")
        self.assertEqual(args.provider_mode, "replay")
        self.assertEqual(args.code, ["880660.SH", "880001.SH"])
        self.assertEqual(args.field, ["BK5", "BK6"])
        self.assertEqual(args.start_time, "20240101")
        self.assertEqual(args.end_time, "20241231")

    def test_tdx_data_sector_transaction_by_date_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-sector-transaction-by-date",
                "--code",
                "880660.SH",
                "--field",
                "BK9",
                "--year",
                "0",
                "--mmdd",
                "0",
            ]
        )
        self.assertEqual(args.command, "tdx-data-sector-transaction-by-date")
        self.assertEqual(args.code, ["880660.SH"])
        self.assertEqual(args.field, ["BK9"])
        self.assertEqual(args.year, 0)
        self.assertEqual(args.mmdd, 0)

    def test_tdx_data_sector_transaction_by_date_command_parses_replay_arguments(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-sector-transaction-by-date",
                "--code",
                "880660.SH",
                "--field",
                "BK9",
                "--field",
                "BK10",
                "--year",
                "2025",
                "--mmdd",
                "101",
                "--provider-mode",
                "replay",
            ]
        )
        self.assertEqual(args.command, "tdx-data-sector-transaction-by-date")
        self.assertEqual(args.provider_mode, "replay")
        self.assertEqual(args.code, ["880660.SH"])
        self.assertEqual(args.field, ["BK9", "BK10"])
        self.assertEqual(args.year, 2025)
        self.assertEqual(args.mmdd, 101)

    def test_api_market_transaction_data_command_parses_without_code(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "market-transaction-data",
                "--field",
                "SC01",
                "--field",
                "SC02",
                "--start-time",
                "20250101",
                "--end-time",
                "20250102",
            ]
        )
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "market-transaction-data")
        self.assertEqual(args.field, ["SC01", "SC02"])
        self.assertFalse(hasattr(args, "code"))
        self.assertEqual(args.start_time, "20250101")
        self.assertEqual(args.end_time, "20250102")

    def test_api_market_transaction_data_by_date_command_parses_without_code(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "market-transaction-data-by-date",
                "--field",
                "SC06",
                "--year",
                "0",
                "--mmdd",
                "0",
            ]
        )
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "market-transaction-data-by-date")
        self.assertEqual(args.field, ["SC06"])
        self.assertFalse(hasattr(args, "code"))
        self.assertEqual(args.year, 0)
        self.assertEqual(args.mmdd, 0)

    def test_api_market_transaction_data_command_requires_field(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["api", "market-transaction-data"])

    def test_tdx_data_market_transaction_command_parses_without_code(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-market-transaction",
                "--field",
                "SC01",
                "--field",
                "SC02",
                "--start-time",
                "20250101",
                "--end-time",
                "20250102",
            ]
        )
        self.assertEqual(args.command, "tdx-data-market-transaction")
        self.assertEqual(args.field, ["SC01", "SC02"])
        self.assertFalse(hasattr(args, "code"))
        self.assertEqual(args.start_time, "20250101")
        self.assertEqual(args.end_time, "20250102")

    def test_tdx_data_market_transaction_by_date_command_parses_without_code(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-market-transaction-by-date",
                "--field",
                "SC06",
                "--year",
                "0",
                "--mmdd",
                "0",
            ]
        )
        self.assertEqual(args.command, "tdx-data-market-transaction-by-date")
        self.assertEqual(args.field, ["SC06"])
        self.assertFalse(hasattr(args, "code"))
        self.assertEqual(args.year, 0)
        self.assertEqual(args.mmdd, 0)

    def test_tdx_data_market_transaction_by_date_command_parses_replay_arguments(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-market-transaction-by-date",
                "--field",
                "field_a",
                "--field",
                "field_b",
                "--year",
                "2025",
                "--mmdd",
                "101",
                "--provider-mode",
                "replay",
            ]
        )
        self.assertEqual(args.command, "tdx-data-market-transaction-by-date")
        self.assertEqual(args.provider_mode, "replay")
        self.assertEqual(args.field, ["field_a", "field_b"])
        self.assertEqual(args.year, 2025)
        self.assertEqual(args.mmdd, 101)

    def test_tdx_data_financial_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-financial",
                "--code",
                "688318.SH",
                "--field",
                "FN1",
                "--field",
                "FN2",
                "--start-time",
                "20240101",
                "--end-time",
                "20241231",
            ]
        )
        self.assertEqual(args.command, "tdx-data-financial")
        self.assertEqual(args.code, ["688318.SH"])
        self.assertEqual(args.field, ["FN1", "FN2"])
        self.assertEqual(args.start_time, "20240101")
        self.assertEqual(args.end_time, "20241231")
        self.assertEqual(args.report_type, "report_time")

    def test_tdx_data_financial_by_date_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-financial-by-date",
                "--code",
                "688318.SH",
                "--field",
                "FN193",
                "--year",
                "2025",
                "--mmdd",
                "331",
            ]
        )
        self.assertEqual(args.command, "tdx-data-financial-by-date")
        self.assertEqual(args.code, ["688318.SH"])
        self.assertEqual(args.field, ["FN193"])
        self.assertEqual(args.year, 2025)
        self.assertEqual(args.mmdd, 331)

    def test_api_user_sectors_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "user-sectors"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "user-sectors")

    def test_api_create_sector_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "create-sector", "--block-code", "CSBK", "--block-name", "测试板块"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "create-sector")
        self.assertEqual(args.block_code, "CSBK")
        self.assertEqual(args.block_name, "测试板块")

    def test_api_create_sector_command_parses_mutation_safety_options(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "create-sector",
                "--block-code",
                "CSBK",
                "--block-name",
                "测试板块",
                "--mutation-key",
                "mk-001",
                "--audit-dir",
                "runtime/block-mutations",
            ]
        )
        self.assertEqual(args.mutation_key, "mk-001")
        self.assertEqual(args.audit_dir, "runtime/block-mutations")

    def test_api_delete_sector_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "delete-sector", "--block-code", "CSBK"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "delete-sector")
        self.assertEqual(args.block_code, "CSBK")

    def test_api_rename_sector_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "rename-sector", "--block-code", "CSBK", "--block-name", "测试板块重命名"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "rename-sector")
        self.assertEqual(args.block_code, "CSBK")
        self.assertEqual(args.block_name, "测试板块重命名")

    def test_api_clear_sector_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "clear-sector", "--block-code", "CSBK"])
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "clear-sector")
        self.assertEqual(args.block_code, "CSBK")

    def test_tdx_send_user_block_command_parses_mutation_safety_options(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-send-user-block",
                "--block-code",
                "ZXG",
                "--stock",
                "000001.SZ",
                "--mutation-key",
                "mk-send-1",
                "--audit-dir",
                "runtime/block-mutations",
            ]
        )
        self.assertEqual(args.command, "tdx-send-user-block")
        self.assertEqual(args.mutation_key, "mk-send-1")
        self.assertEqual(args.audit_dir, "runtime/block-mutations")

    def test_api_block_sync_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "block-sync",
                "--block-code",
                "ZXG",
                "--stock",
                "000001.SZ",
                "--mode",
                "merge",
                "--write-policy",
                "merge_dry_run",
                "--create-if-missing",
                "--dry-run",
                "--show",
                "--mutation-key",
                "sync-001",
                "--audit-dir",
                "runtime/block-sync",
            ]
        )
        self.assertEqual(args.command, "api")
        self.assertEqual(args.api_command, "block-sync")
        self.assertEqual(args.block_code, "ZXG")
        self.assertEqual(args.stock, ["000001.SZ"])
        self.assertEqual(args.mode, "merge")
        self.assertEqual(args.write_policy, "merge_dry_run")
        self.assertTrue(args.create_if_missing)
        self.assertTrue(args.dry_run)
        self.assertTrue(args.show)
        self.assertEqual(args.mutation_key, "sync-001")
        self.assertEqual(args.audit_dir, "runtime/block-sync")

    def test_task_sector_research_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "sector-research", "--sector", "钛金属"])
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "sector-research")
        self.assertEqual(args.sector, "钛金属")

    def test_task_watchlist_overview_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "watchlist-overview", "--code", "000001"])
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "watchlist-overview")
        self.assertEqual(args.code, ["000001"])

    def test_task_block_sync_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "block-sync",
                "--block-code",
                "ZXG",
                "--stock",
                "000001.SZ",
                "--stock",
                "600519.SH",
                "--mode",
                "merge",
                "--write-policy",
                "merge_dry_run",
                "--create-if-missing",
                "--dry-run",
                "--show",
                "--mutation-key",
                "sync-001",
                "--audit-dir",
                "runtime/block-sync",
            ]
        )
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "block-sync")
        self.assertEqual(args.block_code, "ZXG")
        self.assertEqual(args.stock, ["000001.SZ", "600519.SH"])
        self.assertEqual(args.mode, "merge")
        self.assertEqual(args.write_policy, "merge_dry_run")
        self.assertTrue(args.create_if_missing)
        self.assertTrue(args.dry_run)
        self.assertTrue(args.show)
        self.assertEqual(args.mutation_key, "sync-001")
        self.assertEqual(args.audit_dir, "runtime/block-sync")

    def test_task_block_watchlist_import_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "block-watchlist-import",
                "--input",
                "runtime/watchlist-imports/zxg-watchlist-import.example.json",
                "--no-dry-run",
                "--no-show",
                "--audit-dir",
                "runtime/block-sync",
            ]
        )
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "block-watchlist-import")
        self.assertEqual(args.input_path, "runtime/watchlist-imports/zxg-watchlist-import.example.json")
        self.assertFalse(args.dry_run)
        self.assertFalse(args.show)
        self.assertEqual(args.audit_dir, "runtime/block-sync")

    def test_provider_replay_serve_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["provider-replay", "serve", "--config", "runtime/provider-transport-replay.example.json"]
        )
        self.assertEqual(args.command, "provider-replay")
        self.assertEqual(args.provider_replay_command, "serve")
        self.assertEqual(args.config, "runtime/provider-transport-replay.example.json")

    def test_provider_replay_config_check_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["provider-replay", "config-check", "--config", "runtime/provider-transport-replay.example.json"]
        )
        self.assertEqual(args.command, "provider-replay")
        self.assertEqual(args.provider_replay_command, "config-check")
        self.assertEqual(args.config, "runtime/provider-transport-replay.example.json")
        self.assertEqual(args.view, "detailed")

    def test_provider_replay_config_check_summary_view_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "provider-replay",
                "config-check",
                "--config",
                "runtime/provider-transport-replay.example.json",
                "--view",
                "summary",
            ]
        )
        self.assertEqual(args.command, "provider-replay")
        self.assertEqual(args.provider_replay_command, "config-check")
        self.assertEqual(args.config, "runtime/provider-transport-replay.example.json")
        self.assertEqual(args.view, "summary")

    def test_provider_replay_status_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "provider-replay",
                "status",
                "--config",
                "runtime/provider-transport-replay.example.json",
                "--probe-health",
                "--probe-watch-status",
                "--probe-watch-events",
                "--probe-watch-stream",
                "--probe-all",
                "--probe-timeout",
                "1.5",
                "--view",
                "summary",
            ]
        )
        self.assertEqual(args.command, "provider-replay")
        self.assertEqual(args.provider_replay_command, "status")
        self.assertEqual(args.config, "runtime/provider-transport-replay.example.json")
        self.assertEqual(args.probe_health, True)
        self.assertEqual(args.probe_watch_status, True)
        self.assertEqual(args.probe_watch_events, True)
        self.assertEqual(args.probe_watch_stream, True)
        self.assertEqual(args.probe_all, True)
        self.assertEqual(args.probe_timeout, 1.5)
        self.assertEqual(args.view, "summary")

    def test_provider_replay_lifecycle_plan_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "provider-replay",
                "lifecycle-plan",
                "--config",
                "runtime/provider-transport-replay.example.json",
                "--operation",
                "stop",
                "--include-statefile-check",
            ]
        )
        self.assertEqual(args.command, "provider-replay")
        self.assertEqual(args.provider_replay_command, "lifecycle-plan")
        self.assertEqual(args.config, "runtime/provider-transport-replay.example.json")
        self.assertEqual(args.operation, "stop")
        self.assertEqual(args.include_statefile_check, True)
        self.assertEqual(args.stale_after_seconds, 300.0)
        self.assertEqual(args.view, "detailed")

    def test_provider_replay_lifecycle_state_check_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "provider-replay",
                "lifecycle-state-check",
                "--config",
                "runtime/provider-transport-replay.example.json",
            ]
        )
        self.assertEqual(args.command, "provider-replay")
        self.assertEqual(args.provider_replay_command, "lifecycle-state-check")
        self.assertEqual(args.config, "runtime/provider-transport-replay.example.json")
        self.assertEqual(args.stale_after_seconds, 300.0)
        self.assertEqual(args.view, "detailed")

    def test_provider_replay_lifecycle_readiness_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "provider-replay",
                "lifecycle-readiness",
                "--config",
                "runtime/provider-transport-replay.example.json",
            ]
        )
        self.assertEqual(args.command, "provider-replay")
        self.assertEqual(args.provider_replay_command, "lifecycle-readiness")
        self.assertEqual(args.config, "runtime/provider-transport-replay.example.json")
        self.assertEqual(args.include_statefile_check, False)
        self.assertEqual(args.include_ownership_check, False)
        self.assertEqual(args.expected_owner_token, None)
        self.assertEqual(args.inspect_process_identity, False)
        self.assertEqual(args.stale_after_seconds, 300.0)
        self.assertEqual(args.view, "detailed")

    def test_provider_replay_daemon_start_status_stop_commands_parse(self) -> None:
        parser = build_parser()
        start_args = parser.parse_args(
            [
                "provider-replay",
                "daemon",
                "start",
                "--config",
                "runtime/provider-transport-replay.example.json",
                "--owner-token",
                "owner-token-a",
                "--generation",
                "3",
            ]
        )
        status_args = parser.parse_args(
            [
                "provider-replay",
                "daemon",
                "status",
                "--config",
                "runtime/provider-transport-replay.example.json",
                "--stale-after-seconds",
                "45",
                "--expected-owner-token",
                "owner-token-a",
                "--inspect-process-identity",
            ]
        )
        stop_args = parser.parse_args(
            [
                "provider-replay",
                "daemon",
                "stop",
                "--config",
                "runtime/provider-transport-replay.example.json",
                "--owner-token",
                "owner-token-a",
            ]
        )
        supervise_args = parser.parse_args(
            [
                "provider-replay",
                "daemon",
                "supervise",
                "--config",
                "runtime/provider-transport-replay.example.json",
                "--owner-token",
                "owner-token-a",
                "--generation",
                "4",
                "--poll-interval",
                "0.25",
                "--restart-policy",
                "on-failure",
                "--max-restarts",
                "2",
                "--backoff-seconds",
                "0.5",
            ]
        )

        self.assertEqual(start_args.provider_replay_command, "daemon")
        self.assertEqual(start_args.provider_replay_daemon_command, "start")
        self.assertEqual(start_args.owner_token, "owner-token-a")
        self.assertEqual(start_args.generation, 3)
        self.assertEqual(status_args.provider_replay_daemon_command, "status")
        self.assertEqual(status_args.stale_after_seconds, 45.0)
        self.assertEqual(status_args.expected_owner_token, "owner-token-a")
        self.assertEqual(status_args.inspect_process_identity, True)
        self.assertEqual(stop_args.provider_replay_daemon_command, "stop")
        self.assertEqual(stop_args.owner_token, "owner-token-a")
        self.assertEqual(supervise_args.provider_replay_daemon_command, "supervise")
        self.assertEqual(supervise_args.owner_token, "owner-token-a")
        self.assertEqual(supervise_args.generation, 4)
        self.assertEqual(supervise_args.poll_interval, 0.25)
        self.assertEqual(supervise_args.restart_policy, "on-failure")
        self.assertEqual(supervise_args.max_restarts, 2)
        self.assertEqual(supervise_args.backoff_seconds, 0.5)

    def test_task_block_read_watchlist_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "block-read-watchlist", "--block-code", "ZXG"])
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "block-read-watchlist")
        self.assertEqual(args.block_code, "ZXG")

    def test_task_block_read_full_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "block-read-full", "--block-code", "ZXG"])
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "block-read-full")
        self.assertEqual(args.block_code, "ZXG")

    def test_task_block_read_watchlist_export_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "block-read-watchlist-export",
                "--block-code",
                "ZXG",
                "--output",
                "runtime/exports/zxg.json",
                "--overwrite",
            ]
        )
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "block-read-watchlist-export")
        self.assertEqual(args.block_code, "ZXG")
        self.assertEqual(args.export_output, "runtime/exports/zxg.json")
        self.assertTrue(args.overwrite)

    def test_task_watchlist_export_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "watchlist-export", "--code", "000001"])
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "watchlist-export")
        self.assertEqual(args.code, ["000001"])

    def test_task_subscription_watch_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "subscription-watch",
                "--code",
                "600519.SH",
                "--code",
                "000001.SZ",
                "--max-events",
                "5",
                "--max-seconds",
                "10",
                "--poll-interval",
                "0.5",
            ]
        )
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "subscription-watch")
        self.assertEqual(args.code, ["600519.SH", "000001.SZ"])
        self.assertEqual(args.max_events, 5)
        self.assertEqual(args.max_seconds, 10.0)
        self.assertEqual(args.poll_interval, 0.5)

    def test_task_subscription_watch_replay_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "subscription-watch",
                "--code",
                "600519.SH",
                "--provider-mode",
                "replay",
                "--fixture-path",
                "runtime/subscription-replay/manifest.json",
            ]
        )
        self.assertEqual(args.provider_mode, "replay")
        self.assertIsNone(args.fixture)
        self.assertEqual(args.fixture_path, "runtime/subscription-replay/manifest.json")

    def test_task_ledger_summary_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "ledger-summary", "--code", "000001", "--trade-ok"])
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "ledger-summary")
        self.assertEqual(args.code, "000001")
        self.assertTrue(args.trade_ok)

    def test_task_daily_trade_report_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "daily-trade-report", "--date", "2026-04-26", "--trade-ok"])
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "daily-trade-report")
        self.assertEqual(args.date, "2026-04-26")
        self.assertTrue(args.trade_ok)

    def test_task_trade_report_lookup_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "trade-report-lookup", "--contract-no", "B202604260301"])
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "trade-report-lookup")
        self.assertEqual(args.contract_no, "B202604260301")

    def test_task_trade_audit_lookup_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "trade-audit-lookup", "--audit-id", "audit-001", "--status", "confirmed"])
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "trade-audit-lookup")
        self.assertEqual(args.audit_id, "audit-001")
        self.assertEqual(args.status, "confirmed")

    def test_task_trade_audit_daily_report_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "trade-audit-daily-report", "--date", "2026-04-29", "--status", "confirmed"])
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "trade-audit-daily-report")
        self.assertEqual(args.date, "2026-04-29")
        self.assertEqual(args.status, "confirmed")

    def test_task_trade_audit_daily_report_command_parses_multi_status(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["task", "trade-audit-daily-report", "--date", "2026-04-29", "--status-any", "rejected", "--status-any", "failed"]
        )
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "trade-audit-daily-report")
        self.assertEqual(args.statuses, ["rejected", "failed"])

    def test_task_trade_audit_daily_report_command_parses_multi_method(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["task", "trade-audit-daily-report", "--date", "2026-04-29", "--method-any", "buy_submit_once", "--method-any", "confirm_current"]
        )
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "trade-audit-daily-report")
        self.assertEqual(args.methods, ["buy_submit_once", "confirm_current"])

    def test_task_trade_audit_period_report_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "trade-audit-period-report", "--start-date", "2026-04-28", "--end-date", "2026-04-29"])
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "trade-audit-period-report")
        self.assertEqual(args.start_date, "2026-04-28")
        self.assertEqual(args.end_date, "2026-04-29")

    def test_task_trade_audit_cross_ledger_query_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "trade-audit-cross-ledger-query",
                "--audit-dir",
                "runtime/trade-audits",
                "--submission-ledger-path",
                "runtime/pingan-submission-ledger.jsonl",
                "--task-ledger-jsonl-path",
                "runtime/exports/guarded-trade-buy-ledger.jsonl",
                "--cache-output-path",
                "runtime/exports/trade-audit-index-cache.json",
                "--code",
                "000001",
                "--status",
                "confirmed",
                "--limit",
                "5",
            ]
        )
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "trade-audit-cross-ledger-query")
        self.assertEqual(args.audit_dir, "runtime/trade-audits")
        self.assertEqual(args.submission_ledger_path, "runtime/pingan-submission-ledger.jsonl")
        self.assertEqual(args.task_ledger_jsonl_path, "runtime/exports/guarded-trade-buy-ledger.jsonl")
        self.assertEqual(args.cache_output_path, "runtime/exports/trade-audit-index-cache.json")
        self.assertEqual(args.code, "000001")
        self.assertEqual(args.status, "confirmed")
        self.assertEqual(args.limit, 5)

    def test_task_trade_period_report_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "trade-period-report", "--start-date", "2026-04-25", "--end-date", "2026-04-26"])
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "trade-period-report")
        self.assertEqual(args.start_date, "2026-04-25")
        self.assertEqual(args.end_date, "2026-04-26")

    def test_task_trade_buy_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "trade-buy",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--submission-key",
                "task-buy-001",
                "--max-price",
                "10.50",
            ]
        )
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "trade-buy")
        self.assertIsNone(args.refresh_before_trade)
        self.assertEqual(args.submission_key, "task-buy-001")
        self.assertEqual(args.max_price, 10.50)

    def test_task_trade_sell_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "trade-sell",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--submission-key",
                "task-sell-001",
                "--max-price",
                "10.50",
            ]
        )
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "trade-sell")
        self.assertIsNone(args.refresh_before_trade)
        self.assertEqual(args.submission_key, "task-sell-001")
        self.assertEqual(args.max_price, 10.50)

    def test_task_trade_submit_once_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "trade-submit-once",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--submission-key",
                "task-submit-001",
                "--max-price",
                "10.50",
            ]
        )
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "trade-submit-once")
        self.assertEqual(args.side, "buy")
        self.assertIsNone(args.refresh_before_trade)
        self.assertEqual(args.submission_key, "task-submit-001")
        self.assertEqual(args.max_price, 10.50)

    def test_task_trade_submit_once_sell_side_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "trade-submit-once",
                "--side",
                "sell",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "trade-submit-once")
        self.assertEqual(args.side, "sell")

    def test_task_trade_submit_ready_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "trade-submit-ready",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--max-price",
                "10.50",
                "--dialog-lookup-mode",
                "win32_experimental",
                "--confirm-timeout",
                "2.5",
                "--refresh-before-trade",
            ]
        )
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "trade-submit-ready")
        self.assertEqual(args.max_price, 10.50)
        self.assertEqual(args.dialog_lookup_mode, "win32_experimental")
        self.assertEqual(args.confirm_timeout, 2.5)
        self.assertEqual(args.refresh_before_trade, True)

    def test_task_trade_confirm_current_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "trade-confirm-current",
                "--dialog-lookup-mode",
                "win32_experimental",
                "--confirm-timeout",
                "2.0",
                "--result-timeout",
                "3.0",
                "--no-close-result-dialog",
                "--result-close-pre-delay",
                "0.3",
            ]
        )
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "trade-confirm-current")
        self.assertEqual(args.dialog_lookup_mode, "win32_experimental")
        self.assertEqual(args.confirm_timeout, 2.0)
        self.assertEqual(args.result_timeout, 3.0)
        self.assertFalse(args.close_result_dialog)
        self.assertEqual(args.result_close_pre_delay, 0.3)

    def test_task_guarded_trade_buy_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "guarded-trade-buy",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--max-snapshot-price",
                "10.50",
                "--submission-key",
                "guarded-task-001",
                "--max-price",
                "10.40",
            ]
        )
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "guarded-trade-buy")
        self.assertEqual(args.max_snapshot_price, 10.50)
        self.assertEqual(args.submission_key, "guarded-task-001")
        self.assertEqual(args.max_price, 10.40)
        self.assertEqual(args.formula_return_count, 1)

    def test_task_presets_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "presets"])
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "presets")

    def test_task_run_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "run",
                "--preset",
                "guarded-default",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--submission-key",
                "preset-run-001",
                "--max-price",
                "10.30",
            ]
        )
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "run")
        self.assertEqual(args.preset, "guarded-default")
        self.assertEqual(args.code, "000001")
        self.assertEqual(args.submission_key, "preset-run-001")
        self.assertEqual(args.max_price, 10.30)

    def test_task_run_block_read_watchlist_export_preset_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "run",
                "--preset",
                "export-zxg-watchlist",
                "--export-output",
                "runtime/exports/zxg-override.json",
                "--overwrite",
            ]
        )
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "run")
        self.assertEqual(args.preset, "export-zxg-watchlist")
        self.assertEqual(args.export_output, "runtime/exports/zxg-override.json")
        self.assertTrue(args.overwrite)

    def test_task_run_parser_accepts_read_zxg_watchlist_block_code_override(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "run", "--preset", "read-zxg-watchlist", "--block-code", "ZXG"])
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "run")
        self.assertEqual(args.preset, "read-zxg-watchlist")
        self.assertEqual(args.block_code, "ZXG")

    def test_pingan_buy_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "pingan-buy",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--submission-key",
                "buy-20260428-001",
                "--max-price",
                "10.50",
            ]
        )
        self.assertEqual(args.command, "pingan-buy")
        self.assertEqual(args.profile, "balanced")
        self.assertEqual(args.submission_key, "buy-20260428-001")
        self.assertEqual(args.max_price, 10.50)

    def test_pingan_buy_submit_once_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "pingan-buy-submit-once",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--submission-key",
                "submit-20260428-001",
                "--max-price",
                "10.50",
            ]
        )
        self.assertEqual(args.command, "pingan-buy-submit-once")
        self.assertTrue(args.close_result_dialog)
        self.assertEqual(args.submission_key, "submit-20260428-001")
        self.assertEqual(args.max_price, 10.50)

    def test_trade_buy_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "buy",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--submission-key",
                "trade-20260428-001",
                "--max-price",
                "10.50",
            ]
        )
        self.assertEqual(args.command, "trade")
        self.assertEqual(args.trade_command, "buy")
        self.assertEqual(args.profile, "balanced")
        self.assertEqual(args.submission_key, "trade-20260428-001")
        self.assertEqual(args.max_price, 10.50)

    def test_trade_sell_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "sell",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--submission-key",
                "trade-sell-20260428-001",
                "--max-price",
                "10.50",
            ]
        )
        self.assertEqual(args.command, "trade")
        self.assertEqual(args.trade_command, "sell")
        self.assertEqual(args.profile, "balanced")
        self.assertEqual(args.submission_key, "trade-sell-20260428-001")
        self.assertEqual(args.max_price, 10.50)

    def test_trade_submit_once_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "submit-once",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--submission-key",
                "trade-submit-20260428-001",
                "--max-price",
                "10.50",
            ]
        )
        self.assertEqual(args.command, "trade")
        self.assertEqual(args.trade_command, "submit-once")
        self.assertEqual(args.side, "buy")
        self.assertTrue(args.close_result_dialog)
        self.assertEqual(args.submission_key, "trade-submit-20260428-001")
        self.assertEqual(args.max_price, 10.50)

    def test_trade_submit_once_sell_side_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "submit-once",
                "--side",
                "sell",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        self.assertEqual(args.command, "trade")
        self.assertEqual(args.trade_command, "submit-once")
        self.assertEqual(args.side, "sell")

    def test_trade_health_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "health",
                "--port",
                "COM3",
                "--baudrate",
                "9600",
                "--timeout",
                "1.5",
                "--pre-delay",
                "0.2",
            ]
        )
        self.assertEqual(args.command, "trade")
        self.assertEqual(args.trade_command, "health")
        self.assertEqual(args.port, "COM3")
        self.assertEqual(args.baudrate, 9600)
        self.assertEqual(args.timeout, 1.5)
        self.assertEqual(args.pre_delay, 0.2)

    def test_trade_preflight_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "preflight",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--submission-key",
                "preflight-001",
                "--max-price",
                "10.50",
            ]
        )
        self.assertEqual(args.command, "trade")
        self.assertEqual(args.trade_command, "preflight")
        self.assertEqual(args.port, "COM3")
        self.assertEqual(args.code, "000001")
        self.assertEqual(args.submission_key, "preflight-001")
        self.assertEqual(args.max_price, 10.50)

    def test_trade_dialog_readiness_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "dialog-readiness",
                "--dialog",
                "confirm",
                "--require-visible",
                "--dialog-lookup-mode",
                "win32_experimental",
                "--confirm-timeout",
                "1.2",
                "--result-timeout",
                "1.8",
            ]
        )
        self.assertEqual(args.command, "trade")
        self.assertEqual(args.trade_command, "dialog-readiness")
        self.assertEqual(args.dialog, "confirm")
        self.assertTrue(args.require_visible)
        self.assertEqual(args.dialog_lookup_mode, "win32_experimental")
        self.assertEqual(args.confirm_timeout, 1.2)
        self.assertEqual(args.result_timeout, 1.8)

    def test_trade_submit_ready_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "submit-ready",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--max-price",
                "10.50",
                "--dialog-lookup-mode",
                "win32_experimental",
                "--confirm-timeout",
                "1.2",
            ]
        )
        self.assertEqual(args.command, "trade")
        self.assertEqual(args.trade_command, "submit-ready")
        self.assertEqual(args.port, "COM3")
        self.assertEqual(args.max_price, 10.50)
        self.assertEqual(args.dialog_lookup_mode, "win32_experimental")
        self.assertEqual(args.confirm_timeout, 1.2)

    def test_trade_confirm_current_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "confirm-current",
                "--dialog-lookup-mode",
                "win32_experimental",
                "--confirm-timeout",
                "1.2",
                "--result-timeout",
                "1.8",
                "--close-result-dialog",
            ]
        )
        self.assertEqual(args.command, "trade")
        self.assertEqual(args.trade_command, "confirm-current")
        self.assertEqual(args.dialog_lookup_mode, "win32_experimental")
        self.assertEqual(args.confirm_timeout, 1.2)
        self.assertEqual(args.result_timeout, 1.8)
        self.assertTrue(args.close_result_dialog)

    def test_trade_presets_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["trade", "presets"])
        self.assertEqual(args.command, "trade")
        self.assertEqual(args.trade_command, "presets")

    def test_trade_run_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "run",
                "--preset",
                "turbo-buy",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--submission-key",
                "trade-run-20260428-001",
                "--max-price",
                "10.50",
            ]
        )
        self.assertEqual(args.command, "trade")
        self.assertEqual(args.trade_command, "run")
        self.assertEqual(args.preset, "turbo-buy")
        self.assertEqual(args.code, "000001")
        self.assertEqual(args.submission_key, "trade-run-20260428-001")
        self.assertEqual(args.max_price, 10.50)

    def test_report_daily_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "daily", "--date", "2026-04-26"])
        self.assertEqual(args.command, "report")
        self.assertEqual(args.report_command, "daily")
        self.assertEqual(args.profile, "daily_trade_report")

    def test_report_lookup_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "lookup", "--contract-no", "B202604260301"])
        self.assertEqual(args.command, "report")
        self.assertEqual(args.report_command, "lookup")
        self.assertEqual(args.profile, "trade_report_lookup")

    def test_report_audit_lookup_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "audit-lookup", "--submission-key", "submit-001"])
        self.assertEqual(args.command, "report")
        self.assertEqual(args.report_command, "audit-lookup")
        self.assertEqual(args.profile, "trade_audit_lookup")
        self.assertEqual(args.submission_key, "submit-001")

    def test_report_audit_daily_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "audit-daily", "--date", "2026-04-29"])
        self.assertEqual(args.command, "report")
        self.assertEqual(args.report_command, "audit-daily")
        self.assertEqual(args.profile, "trade_audit_daily_report")

    def test_report_audit_period_command_parses_multi_status(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["report", "audit-period", "--start-date", "2026-04-28", "--status-any", "rejected", "--status-any", "failed"]
        )
        self.assertEqual(args.command, "report")
        self.assertEqual(args.report_command, "audit-period")
        self.assertEqual(args.statuses, ["rejected", "failed"])

    def test_report_audit_period_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "audit-period", "--start-date", "2026-04-28"])
        self.assertEqual(args.command, "report")
        self.assertEqual(args.report_command, "audit-period")
        self.assertEqual(args.profile, "trade_audit_period_report")

    def test_report_period_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "period", "--start-date", "2026-04-25"])
        self.assertEqual(args.command, "report")
        self.assertEqual(args.report_command, "period")
        self.assertEqual(args.profile, "trade_period_report")

    def test_report_ledger_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "ledger", "--code", "000001"])
        self.assertEqual(args.command, "report")
        self.assertEqual(args.report_command, "ledger")
        self.assertEqual(args.profile, "ledger_summary")

    def test_report_presets_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "presets"])
        self.assertEqual(args.command, "report")
        self.assertEqual(args.report_command, "presets")

    def test_report_run_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "run", "--preset", "daily-review", "--timezone", "UTC"])
        self.assertEqual(args.command, "report")
        self.assertEqual(args.report_command, "run")
        self.assertEqual(args.preset, "daily-review")
        self.assertEqual(args.timezone, "UTC")

    def test_catalog_list_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list"])
        self.assertEqual(args.command, "catalog")
        self.assertEqual(args.catalog_command, "list")

    def test_catalog_list_summary_view_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--view", "summary"])
        self.assertEqual(args.command, "catalog")
        self.assertEqual(args.catalog_command, "list")
        self.assertEqual(args.view, "summary")

    def test_catalog_bundle_list_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "bundle", "--bundle", "refresh-review", "--label", "morning"])
        self.assertEqual(args.command, "catalog")
        self.assertEqual(args.catalog_command, "list")
        self.assertEqual(args.kind, "bundle")
        self.assertEqual(args.bundle, "refresh-review")
        self.assertEqual(args.label, "morning")

    def test_catalog_validate_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "validate", "--kind", "bundle", "--label", "followup"])
        self.assertEqual(args.command, "catalog")
        self.assertEqual(args.catalog_command, "validate")
        self.assertEqual(args.kind, "bundle")
        self.assertIsNone(args.entry)
        self.assertIsNone(args.bundle)
        self.assertEqual(args.label, "followup")

    def test_catalog_validate_summary_view_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["catalog", "validate", "--kind", "bundle", "--label", "followup", "--view", "summary"]
        )
        self.assertEqual(args.command, "catalog")
        self.assertEqual(args.catalog_command, "validate")
        self.assertEqual(args.kind, "bundle")
        self.assertEqual(args.label, "followup")
        self.assertEqual(args.view, "summary")

    def test_catalog_run_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--entry", "turbo-buy", "--code", "000001", "--price", "10.00", "--quantity", "100"])
        self.assertEqual(args.command, "catalog")
        self.assertEqual(args.catalog_command, "run")
        self.assertEqual(args.entry, "turbo-buy")
        self.assertEqual(args.code, "000001")

    def test_catalog_run_rejects_side_override(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["catalog", "run", "--entry", "submit-once", "--side", "sell"])

    def test_catalog_bundle_run_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--bundle", "guarded-review-buy", "--code", "000001"])
        self.assertEqual(args.command, "catalog")
        self.assertEqual(args.catalog_command, "run")
        self.assertEqual(args.bundle, "guarded-review-buy")
        self.assertEqual(args.code, "000001")

    def test_catalog_bundle_run_step_selection_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["catalog", "run", "--bundle", "guarded-review-buy", "--from-step", "trade", "--to-step", "review"]
        )
        self.assertEqual(args.from_step, "trade")
        self.assertEqual(args.to_step, "review")
        self.assertIsNone(args.only_step)

    def test_catalog_bundle_run_only_step_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--bundle", "guarded-review-buy", "--only-step", "2"])
        self.assertEqual(args.only_step, "2")

    def test_catalog_run_summary_view_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--entry", "daily-review", "--view", "summary"])
        self.assertEqual(args.view, "summary")

    def test_catalog_plan_entry_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--entry", "daily-review", "--timezone", "UTC"])
        self.assertEqual(args.command, "catalog")
        self.assertEqual(args.catalog_command, "plan")
        self.assertEqual(args.entry, "daily-review")
        self.assertEqual(args.timezone, "UTC")

    def test_catalog_plan_bundle_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--bundle", "guarded-review-buy", "--only-step", "review"])
        self.assertEqual(args.command, "catalog")
        self.assertEqual(args.catalog_command, "plan")
        self.assertEqual(args.bundle, "guarded-review-buy")
        self.assertEqual(args.only_step, "review")

    def test_catalog_bundle_plan_accepts_block_code_override(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--bundle", "read-zxg-review", "--block-code", "MYZXG"])
        self.assertEqual(args.command, "catalog")
        self.assertEqual(args.catalog_command, "plan")
        self.assertEqual(args.bundle, "read-zxg-review")
        self.assertEqual(args.block_code, "MYZXG")

    def test_catalog_run_bundle_rejects_export_output_override(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["catalog", "run", "--bundle", "read-zxg-review-and-export", "--export-output", "runtime/exports/alt.json"])

    def test_catalog_run_bundle_rejects_overwrite_override(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["catalog", "run", "--bundle", "read-zxg-review-and-export", "--overwrite"])

    def test_catalog_plan_summary_view_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--entry", "daily-review", "--view", "summary"])
        self.assertEqual(args.view, "summary")


class ProviderReplayCliDispatchTests(unittest.TestCase):
    def test_handle_provider_replay_config_check_returns_summary_without_serving(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "provider-replay.json"
            lifecycle_state_file = Path(temp_dir) / "provider-replay.state.json"
            lifecycle_state_file.write_text(
                json.dumps(
                    {
                        "schema_version": "tdx.provider_replay.lifecycle_state.v1",
                        "provider_id": "provider-replay-a",
                        "pid": 12345,
                        "state": "running",
                        "updated_at": "2000-01-01T00:00:00Z",
                    }
                ),
                encoding="utf-8",
            )
            config_path.write_text(
                json.dumps(
                    {
                        "provider_id": "provider-replay-a",
                        "bind_host": "127.0.0.1",
                        "port": 0,
                        "token": "secret",
                        "master_allowlist": ["127.0.0.1"],
                        "replay_fixture": "market-snapshot-default",
                        "lifecycle_state_file": str(lifecycle_state_file),
                    }
                ),
                encoding="utf-8",
            )
            args = parser.parse_args(["provider-replay", "config-check", "--config", str(config_path)])
            with patch("tdxquant.cli.serve_provider_transport_replay") as mocked_serve:
                result = _handle_provider_replay_subcommand(args)

        self.assertTrue(result.ok)
        self.assertEqual(result.data["config"]["provider_id"], "provider-replay-a")
        self.assertEqual(result.data["config"]["bind_host"], "127.0.0.1")
        self.assertEqual(result.data["config"]["port"], 0)
        self.assertEqual(result.data["config"]["master_allowlist_count"], 1)
        self.assertEqual(result.data["config"]["replay_fixture"], "market-snapshot-default")
        mocked_serve.assert_not_called()

    def test_handle_provider_replay_config_check_summary_view_is_config_only(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "provider-replay.json"
            lifecycle_state_file = Path(temp_dir) / "provider-replay.state.json"
            lifecycle_state_file.write_text(
                json.dumps(
                    {
                        "schema_version": "tdx.provider_replay.lifecycle_state.v1",
                        "provider_id": "provider-replay-a",
                        "pid": 12345,
                        "state": "running",
                        "updated_at": "2000-01-01T00:00:00Z",
                    }
                ),
                encoding="utf-8",
            )
            config_path.write_text(
                json.dumps(
                    {
                        "provider_id": "provider-replay-a",
                        "bind_host": "127.0.0.1",
                        "port": 0,
                        "token": "secret",
                        "master_allowlist": ["127.0.0.1"],
                        "replay_fixture": "market-snapshot-default",
                        "lifecycle_state_file": str(lifecycle_state_file),
                    }
                ),
                encoding="utf-8",
            )
            args = parser.parse_args(
                ["provider-replay", "config-check", "--config", str(config_path), "--view", "summary"]
            )
            with (
                patch("tdxquant.cli.serve_provider_transport_replay") as mocked_serve,
                patch("tdxquant.cli.probe_provider_transport_replay_health") as mocked_probe,
                patch("tdxquant.cli.probe_provider_transport_replay_watch_status") as mocked_watch_status_probe,
                patch("tdxquant.cli.probe_provider_transport_replay_watch_events") as mocked_watch_events_probe,
                patch("tdxquant.cli.probe_provider_transport_replay_watch_stream") as mocked_watch_stream_probe,
            ):
                result = _handle_provider_replay_subcommand(args)

        self.assertTrue(result.ok)
        self.assertEqual(result.data["config"]["provider_id"], "provider-replay-a")
        self.assertNotIn("token", result.data["config"])
        self.assertEqual(result.data["config"]["lifecycle_state_file_provided"], True)
        self.assertEqual(result.data["summary_view"]["mode"], "config-check")
        self.assertEqual(result.data["summary_view"]["provider_id"], "provider-replay-a")
        self.assertEqual(result.data["summary_view"]["bind_host"], "127.0.0.1")
        self.assertEqual(result.data["summary_view"]["port"], 0)
        self.assertEqual(result.data["summary_view"]["master_allowlist_count"], 1)
        self.assertEqual(result.data["summary_view"]["replay_fixture"], "market-snapshot-default")
        self.assertEqual(result.data["summary_view"]["lifecycle_state_file_provided"], True)
        self.assertEqual(result.data["summary_view"]["statefile_inspected"], False)
        self.assertEqual(result.data["summary_view"]["statefile_written"], False)
        self.assertEqual(result.data["summary_view"]["serve_started"], False)
        self.assertEqual(result.data["summary_view"]["probe_requested"], False)
        self.assertEqual(result.data["summary_view"]["daemon_lifecycle_managed"], False)
        self.assertIn("config_validation_only", result.data["summary_view"]["boundaries"])
        self.assertIn("server_not_started", result.data["summary_view"]["boundaries"])
        self.assertIn("probe_not_requested", result.data["summary_view"]["boundaries"])
        self.assertIn("statefile_not_inspected", result.data["summary_view"]["boundaries"])
        self.assertIn("daemon_lifecycle_not_managed", result.data["summary_view"]["boundaries"])
        self.assertFalse(lifecycle_state_file.exists())
        mocked_serve.assert_not_called()
        mocked_probe.assert_not_called()
        mocked_watch_status_probe.assert_not_called()
        mocked_watch_events_probe.assert_not_called()
        mocked_watch_stream_probe.assert_not_called()

    def test_handle_provider_replay_lifecycle_plan_reports_blocked_stop_without_dispatch(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "provider-replay.json"
            lifecycle_state_file = Path(temp_dir) / "provider-replay.state.json"
            lifecycle_state_file.write_text(
                json.dumps(
                    {
                        "schema_version": "tdx.provider_replay.lifecycle_state.v1",
                        "provider_id": "provider-replay-a",
                        "pid": 12345,
                        "state": "running",
                        "updated_at": "2000-01-01T00:00:00Z",
                    }
                ),
                encoding="utf-8",
            )
            config_path.write_text(
                json.dumps(
                    {
                        "provider_id": "provider-replay-a",
                        "bind_host": "127.0.0.1",
                        "port": 0,
                        "token": "secret",
                        "master_allowlist": ["127.0.0.1"],
                        "replay_fixture": "market-snapshot-default",
                        "lifecycle_state_file": str(lifecycle_state_file),
                    }
                ),
                encoding="utf-8",
            )
            args = parser.parse_args(
                [
                    "provider-replay",
                    "lifecycle-plan",
                    "--config",
                    str(config_path),
                    "--operation",
                    "stop",
                    "--include-statefile-check",
                    "--stale-after-seconds",
                    "60",
                ]
            )
            with (
                patch("tdxquant.cli.serve_provider_transport_replay") as mocked_serve,
                patch("tdxquant.cli.probe_provider_transport_replay_health") as mocked_probe,
                patch("tdxquant.cli.probe_provider_transport_replay_watch_status") as mocked_watch_status_probe,
                patch("tdxquant.cli.probe_provider_transport_replay_watch_events") as mocked_watch_events_probe,
                patch("tdxquant.cli.probe_provider_transport_replay_watch_stream") as mocked_watch_stream_probe,
            ):
                result = _handle_provider_replay_subcommand(args)
                lifecycle_state_file_exists_after_call = lifecycle_state_file.exists()

        self.assertTrue(result.ok)
        self.assertEqual(result.data["plan"]["execution_mode"], "non_executing_lifecycle_plan")
        self.assertEqual(result.data["plan"]["operation"], "stop")
        self.assertEqual(result.data["plan"]["operation_status"], "blocked")
        self.assertEqual(result.data["plan"]["implemented"], True)
        self.assertEqual(result.data["plan"]["dispatch_executed"], False)
        self.assertEqual(result.data["plan"]["control_allowed"], False)
        self.assertEqual(result.data["plan"]["lifecycle_control_status"], "operator_opt_in_available")
        self.assertEqual(result.data["plan"]["blocking_reason"], "lifecycle_statefile_not_current")
        self.assertEqual(result.data["plan"]["ownership_required"], True)
        self.assertEqual(result.data["plan"]["operator_action_required"], True)
        self.assertEqual(result.data["plan"]["statefile_configured"], True)
        self.assertEqual(result.data["plan"]["statefile_check_included"], True)
        self.assertEqual(result.data["plan"]["statefile_check_status"], "valid")
        self.assertEqual(result.data["plan"]["statefile_schema_valid"], True)
        self.assertEqual(result.data["plan"]["statefile_provider_id_matches"], True)
        self.assertEqual(result.data["plan"]["statefile_stale"], True)
        self.assertEqual(result.data["plan"]["statefile_diagnostics"]["check_status"], "valid")
        self.assertEqual(result.data["plan"]["statefile_diagnostics"]["control_allowed"], False)
        self.assertEqual(result.data["plan"]["dispatch_executed"], False)
        self.assertEqual(result.data["plan"]["control_allowed"], False)
        self.assertEqual(result.data["plan"]["supervision_status"], "operator_opt_in_available")
        self.assertIn("lifecycle_controller", result.data["plan"]["required_capabilities"])
        self.assertEqual(result.data["plan"]["boundary"], "read_only_lifecycle_plan; no_control_dispatch")
        self.assertTrue(lifecycle_state_file_exists_after_call)
        mocked_serve.assert_not_called()
        mocked_probe.assert_not_called()
        mocked_watch_status_probe.assert_not_called()
        mocked_watch_events_probe.assert_not_called()
        mocked_watch_stream_probe.assert_not_called()

    def test_handle_provider_replay_lifecycle_plan_excludes_statefile_check_by_default(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "provider-replay.json"
            lifecycle_state_file = Path(temp_dir) / "provider-replay.state.json"
            config_path.write_text(
                json.dumps(
                    {
                        "provider_id": "provider-replay-a",
                        "bind_host": "127.0.0.1",
                        "port": 0,
                        "token": "secret",
                        "master_allowlist": ["127.0.0.1"],
                        "replay_fixture": "market-snapshot-default",
                        "lifecycle_state_file": str(lifecycle_state_file),
                    }
                ),
                encoding="utf-8",
            )
            args = parser.parse_args(
                ["provider-replay", "lifecycle-plan", "--config", str(config_path), "--operation", "stop"]
            )
            with patch("tdxquant.cli.check_provider_replay_lifecycle_statefile") as mocked_statefile_check:
                result = _handle_provider_replay_subcommand(args)

        self.assertTrue(result.ok)
        self.assertEqual(result.data["plan"]["statefile_configured"], True)
        self.assertEqual(result.data["plan"]["statefile_check_included"], False)
        self.assertIsNone(result.data["plan"]["statefile_check_status"])
        self.assertIsNone(result.data["plan"]["statefile_diagnostics"])
        mocked_statefile_check.assert_not_called()

    def test_handle_provider_replay_lifecycle_readiness_reports_blocked_without_statefile_read(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "provider-replay.json"
            lifecycle_state_file = Path(temp_dir) / "provider-replay.state.json"
            config_path.write_text(
                json.dumps(
                    {
                        "provider_id": "provider-replay-a",
                        "bind_host": "127.0.0.1",
                        "port": 0,
                        "token": "secret",
                        "master_allowlist": ["127.0.0.1"],
                        "replay_fixture": "market-snapshot-default",
                        "lifecycle_state_file": str(lifecycle_state_file),
                    }
                ),
                encoding="utf-8",
            )
            args = parser.parse_args(["provider-replay", "lifecycle-readiness", "--config", str(config_path)])
            with patch("tdxquant.cli.check_provider_replay_lifecycle_statefile") as mocked_statefile_check:
                result = _handle_provider_replay_subcommand(args)

        self.assertTrue(result.ok)
        self.assertEqual(result.data["readiness"]["readiness_status"], "blocked")
        self.assertEqual(result.data["readiness"]["ready"], False)
        self.assertEqual(result.data["readiness"]["control_allowed"], False)
        self.assertEqual(result.data["readiness"]["dispatch_executed"], False)
        self.assertEqual(result.data["readiness"]["statefile_check_included"], False)
        self.assertIn("lifecycle_controller", result.data["readiness"]["satisfied_requirements"])
        self.assertNotIn("lifecycle_controller", result.data["readiness"]["missing_requirements"])
        self.assertIn("owned_process_identity", result.data["readiness"]["missing_requirements"])
        self.assertIn("supervisor_loop", result.data["readiness"]["satisfied_requirements"])
        self.assertIn("operator_opt_in_control", result.data["readiness"]["satisfied_requirements"])
        self.assertNotIn("supervisor_loop", result.data["readiness"]["missing_requirements"])
        self.assertNotIn("operator_opt_in_control", result.data["readiness"]["missing_requirements"])
        self.assertIn("valid_lifecycle_statefile", result.data["readiness"]["missing_requirements"])
        self.assertEqual(result.data["readiness"]["missing_requirement_count"], 2)
        self.assertEqual(result.data["readiness"]["boundary"], "read_only_lifecycle_readiness; no_control_dispatch")
        mocked_statefile_check.assert_not_called()

    def test_handle_provider_replay_lifecycle_readiness_summary_counts_valid_statefile_prerequisite(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "provider-replay.json"
            state_path = Path(temp_dir) / "provider-replay.state.json"
            state_path.write_text(
                json.dumps(
                    {
                        "schema_version": "tdx.provider_replay.lifecycle_state.v1",
                        "provider_id": "provider-replay-a",
                        "pid": 12345,
                        "state": "running",
                        "updated_at": "2999-01-01T00:00:00Z",
                    }
                ),
                encoding="utf-8",
            )
            config_path.write_text(
                json.dumps(
                    {
                        "provider_id": "provider-replay-a",
                        "bind_host": "127.0.0.1",
                        "port": 0,
                        "token": "secret",
                        "master_allowlist": ["127.0.0.1"],
                        "replay_fixture": "market-snapshot-default",
                        "lifecycle_state_file": str(state_path),
                    }
                ),
                encoding="utf-8",
            )
            args = parser.parse_args(
                [
                    "provider-replay",
                    "lifecycle-readiness",
                    "--config",
                    str(config_path),
                    "--include-statefile-check",
                    "--view",
                    "summary",
                ]
            )
            result = _handle_provider_replay_subcommand(args)

        self.assertTrue(result.ok)
        self.assertEqual(result.data["readiness"]["ready"], False)
        self.assertEqual(result.data["readiness"]["control_allowed"], False)
        self.assertEqual(result.data["readiness"]["statefile_check_included"], True)
        self.assertEqual(result.data["readiness"]["statefile_check_status"], "valid")
        self.assertEqual(result.data["readiness"]["statefile_schema_valid"], True)
        self.assertEqual(result.data["readiness"]["statefile_provider_id_matches"], True)
        self.assertEqual(result.data["readiness"]["statefile_stale"], False)
        self.assertIn("valid_lifecycle_statefile", result.data["readiness"]["satisfied_requirements"])
        self.assertIn("lifecycle_controller", result.data["readiness"]["satisfied_requirements"])
        self.assertIn("supervisor_loop", result.data["readiness"]["satisfied_requirements"])
        self.assertIn("operator_opt_in_control", result.data["readiness"]["satisfied_requirements"])
        self.assertNotIn("valid_lifecycle_statefile", result.data["readiness"]["missing_requirements"])
        self.assertNotIn("lifecycle_controller", result.data["readiness"]["missing_requirements"])
        self.assertNotIn("supervisor_loop", result.data["readiness"]["missing_requirements"])
        self.assertNotIn("operator_opt_in_control", result.data["readiness"]["missing_requirements"])
        self.assertIn("owned_process_identity", result.data["readiness"]["missing_requirements"])
        self.assertEqual(result.data["summary_view"]["mode"], "lifecycle-readiness")
        self.assertEqual(result.data["summary_view"]["ready"], False)
        self.assertEqual(result.data["summary_view"]["readiness_status"], "blocked")
        self.assertEqual(result.data["summary_view"]["control_allowed"], False)
        self.assertEqual(
            result.data["summary_view"]["missing_requirement_count"],
            result.data["readiness"]["missing_requirement_count"],
        )
        self.assertEqual(result.data["summary_view"]["statefile_check_status"], "valid")

    def test_handle_provider_replay_lifecycle_readiness_counts_owned_process_identity_when_proven(
        self,
    ) -> None:
        parser = build_parser()
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "provider-replay.json"
            state_path = Path(temp_dir) / "provider-replay.state.json"
            state_path.write_text(
                json.dumps(
                    {
                        "schema_version": "tdx.provider_replay.lifecycle_state.v1",
                        "provider_id": "provider-replay-a",
                        "pid": 4321,
                        "state": "running",
                        "updated_at": "2999-01-01T00:00:00Z",
                    }
                ),
                encoding="utf-8",
            )
            config_path.write_text(
                json.dumps(
                    {
                        "provider_id": "provider-replay-a",
                        "bind_host": "127.0.0.1",
                        "port": 0,
                        "token": "secret",
                        "master_allowlist": ["127.0.0.1"],
                        "replay_fixture": "market-snapshot-default",
                        "lifecycle_state_file": str(state_path),
                    }
                ),
                encoding="utf-8",
            )
            args = parser.parse_args(
                [
                    "provider-replay",
                    "lifecycle-readiness",
                    "--config",
                    str(config_path),
                    "--include-statefile-check",
                    "--include-ownership-check",
                    "--expected-owner-token",
                    "owner-token-a",
                    "--view",
                    "summary",
                ]
            )
            with patch(
                "tdxquant.cli.get_provider_replay_managed_daemon_status",
                return_value={
                    "daemon_status": "running",
                    "pid": 4321,
                    "ownership": {
                        "ownership_status": "owned",
                        "owned_process": True,
                        "pid_live": True,
                        "owner_token_matches": True,
                        "config_hash_matches": True,
                        "process_identity_checked": False,
                        "process_identity_matches": None,
                        "control_allowed": True,
                    },
                },
            ) as mocked_status:
                result = _handle_provider_replay_subcommand(args)

        self.assertTrue(result.ok)
        self.assertEqual(result.data["readiness"]["readiness_status"], "ready")
        self.assertEqual(result.data["readiness"]["ready"], True)
        self.assertEqual(result.data["readiness"]["control_allowed"], True)
        self.assertEqual(result.data["readiness"]["ownership_check_included"], True)
        self.assertEqual(result.data["readiness"]["ownership_status"], "owned")
        self.assertEqual(result.data["readiness"]["owned_process"], True)
        self.assertIn("lifecycle_controller", result.data["readiness"]["satisfied_requirements"])
        self.assertIn("supervisor_loop", result.data["readiness"]["satisfied_requirements"])
        self.assertIn("operator_opt_in_control", result.data["readiness"]["satisfied_requirements"])
        self.assertIn("owned_process_identity", result.data["readiness"]["satisfied_requirements"])
        self.assertNotIn("lifecycle_controller", result.data["readiness"]["missing_requirements"])
        self.assertNotIn("supervisor_loop", result.data["readiness"]["missing_requirements"])
        self.assertNotIn("operator_opt_in_control", result.data["readiness"]["missing_requirements"])
        self.assertNotIn("owned_process_identity", result.data["readiness"]["missing_requirements"])
        self.assertEqual(result.data["readiness"]["missing_requirement_count"], 0)
        self.assertEqual(result.data["ownership"]["ownership_status"], "owned")
        self.assertEqual(result.data["summary_view"]["readiness_status"], "ready")
        self.assertEqual(result.data["summary_view"]["ready"], True)
        self.assertEqual(result.data["summary_view"]["control_allowed"], True)
        self.assertEqual(result.data["summary_view"]["ownership_status"], "owned")
        self.assertEqual(result.data["summary_view"]["owned_process"], True)
        mocked_status.assert_called_once()
        self.assertEqual(mocked_status.call_args.kwargs["expected_owner_token"], "owner-token-a")

    def test_handle_provider_replay_daemon_start_status_stop_dispatches_to_managed_helpers(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "provider-replay.json"
            state_path = Path(temp_dir) / "provider-replay.state.json"
            config_path.write_text(
                json.dumps(
                    {
                        "provider_id": "provider-replay-a",
                        "bind_host": "127.0.0.1",
                        "port": 0,
                        "token": "secret",
                        "master_allowlist": ["127.0.0.1"],
                        "replay_fixture": "market-snapshot-default",
                        "lifecycle_state_file": str(state_path),
                    }
                ),
                encoding="utf-8",
            )
            start_args = parser.parse_args(
                [
                    "provider-replay",
                    "daemon",
                    "start",
                    "--config",
                    str(config_path),
                    "--owner-token",
                    "owner-token-a",
                    "--generation",
                    "3",
                ]
            )
            status_args = parser.parse_args(
                [
                    "provider-replay",
                    "daemon",
                    "status",
                    "--config",
                    str(config_path),
                    "--expected-owner-token",
                    "owner-token-a",
                ]
            )
            stop_args = parser.parse_args(
                [
                    "provider-replay",
                    "daemon",
                    "stop",
                    "--config",
                    str(config_path),
                    "--owner-token",
                    "owner-token-a",
                ]
            )
            supervise_args = parser.parse_args(
                [
                    "provider-replay",
                    "daemon",
                    "supervise",
                    "--config",
                    str(config_path),
                    "--owner-token",
                    "owner-token-a",
                    "--generation",
                    "4",
                    "--poll-interval",
                    "0.25",
                    "--restart-policy",
                    "on-failure",
                    "--max-restarts",
                    "2",
                    "--backoff-seconds",
                    "0.5",
                ]
            )
            with (
                patch(
                    "tdxquant.cli.start_provider_replay_managed_daemon",
                    return_value={"start_status": "started", "pid": 4321},
                ) as mocked_start,
                patch(
                    "tdxquant.cli.get_provider_replay_managed_daemon_status",
                    return_value={"daemon_status": "running", "pid": 4321},
                ) as mocked_status,
                patch(
                    "tdxquant.cli.stop_provider_replay_managed_daemon",
                    return_value={"stop_status": "signal_sent", "pid": 4321},
                ) as mocked_stop,
                patch(
                    "tdxquant.cli.run_provider_replay_managed_daemon_supervisor",
                    return_value={"supervisor_status": "child_exited", "pid": 4321},
                ) as mocked_supervise,
            ):
                start_result = _handle_provider_replay_subcommand(start_args)
                status_result = _handle_provider_replay_subcommand(status_args)
                stop_result = _handle_provider_replay_subcommand(stop_args)
                supervise_result = _handle_provider_replay_subcommand(supervise_args)

        self.assertTrue(start_result.ok)
        self.assertEqual(start_result.data["daemon"]["start_status"], "started")
        self.assertTrue(status_result.ok)
        self.assertEqual(status_result.data["daemon"]["daemon_status"], "running")
        self.assertTrue(stop_result.ok)
        self.assertEqual(stop_result.data["daemon"]["stop_status"], "signal_sent")
        self.assertTrue(supervise_result.ok)
        self.assertEqual(supervise_result.data["daemon"]["supervisor_status"], "child_exited")
        mocked_start.assert_called_once()
        mocked_status.assert_called_once()
        mocked_stop.assert_called_once()
        mocked_supervise.assert_called_once()
        self.assertEqual(mocked_start.call_args.kwargs["config_path"], config_path)
        self.assertEqual(mocked_start.call_args.kwargs["owner_token"], "owner-token-a")
        self.assertEqual(mocked_start.call_args.kwargs["generation"], 3)
        self.assertEqual(mocked_status.call_args.kwargs["expected_owner_token"], "owner-token-a")
        self.assertEqual(mocked_stop.call_args.kwargs["owner_token"], "owner-token-a")
        self.assertEqual(mocked_supervise.call_args.kwargs["owner_token"], "owner-token-a")
        self.assertEqual(mocked_supervise.call_args.kwargs["generation"], 4)
        self.assertEqual(mocked_supervise.call_args.kwargs["poll_interval"], 0.25)
        self.assertEqual(mocked_supervise.call_args.kwargs["restart_policy"], "on-failure")
        self.assertEqual(mocked_supervise.call_args.kwargs["max_restarts"], 2)
        self.assertEqual(mocked_supervise.call_args.kwargs["backoff_seconds"], 0.5)

    def test_handle_provider_replay_lifecycle_plan_summary_reports_blocked_restart(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "provider-replay.json"
            state_path = Path(temp_dir) / "provider-replay.state.json"
            state_path.write_text(
                json.dumps(
                    {
                        "schema_version": "tdx.provider_replay.lifecycle_state.v1",
                        "provider_id": "provider-replay-a",
                        "pid": 12345,
                        "state": "running",
                        "updated_at": "2000-01-01T00:00:00Z",
                    }
                ),
                encoding="utf-8",
            )
            config_path.write_text(
                json.dumps(
                    {
                        "provider_id": "provider-replay-a",
                        "bind_host": "127.0.0.1",
                        "port": 0,
                        "token": "secret",
                        "master_allowlist": ["127.0.0.1"],
                        "replay_fixture": "market-snapshot-default",
                        "lifecycle_state_file": str(state_path),
                    }
                ),
                encoding="utf-8",
            )
            args = parser.parse_args(
                [
                    "provider-replay",
                    "lifecycle-plan",
                    "--config",
                    str(config_path),
                    "--operation",
                    "restart",
                    "--include-statefile-check",
                    "--stale-after-seconds",
                    "60",
                    "--view",
                    "summary",
                ]
            )
            result = _handle_provider_replay_subcommand(args)

        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary_view"]["mode"], "lifecycle-plan")
        self.assertEqual(result.data["summary_view"]["provider_id"], "provider-replay-a")
        self.assertEqual(result.data["summary_view"]["operation"], "restart")
        self.assertEqual(result.data["summary_view"]["operation_status"], "blocked")
        self.assertEqual(result.data["summary_view"]["dispatch_executed"], False)
        self.assertEqual(result.data["summary_view"]["control_allowed"], False)
        self.assertEqual(result.data["summary_view"]["lifecycle_control_status"], "operator_opt_in_available")
        self.assertEqual(result.data["summary_view"]["blocking_reason"], "operator_invocation_required")
        self.assertEqual(result.data["summary_view"]["statefile_configured"], True)
        self.assertEqual(result.data["summary_view"]["statefile_check_included"], True)
        self.assertEqual(result.data["summary_view"]["statefile_check_status"], "valid")
        self.assertEqual(result.data["summary_view"]["statefile_schema_valid"], True)
        self.assertEqual(result.data["summary_view"]["statefile_provider_id_matches"], True)
        self.assertEqual(result.data["summary_view"]["statefile_stale"], True)
        self.assertEqual(result.data["summary_view"]["supervision_status"], "operator_opt_in_available")
        self.assertEqual(result.data["summary_view"]["boundary"], "read_only_lifecycle_plan; no_control_dispatch")

    def test_handle_provider_replay_lifecycle_state_check_reports_valid_stale_statefile(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "provider-replay.json"
            state_path = Path(temp_dir) / "provider-replay.state.json"
            state_path.write_text(
                json.dumps(
                    {
                        "schema_version": "tdx.provider_replay.lifecycle_state.v1",
                        "provider_id": "provider-replay-a",
                        "pid": 12345,
                        "state": "running",
                        "updated_at": "2000-01-01T00:00:00Z",
                    }
                ),
                encoding="utf-8",
            )
            config_path.write_text(
                json.dumps(
                    {
                        "provider_id": "provider-replay-a",
                        "bind_host": "127.0.0.1",
                        "port": 0,
                        "token": "secret",
                        "master_allowlist": ["127.0.0.1"],
                        "replay_fixture": "market-snapshot-default",
                        "lifecycle_state_file": str(state_path),
                    }
                ),
                encoding="utf-8",
            )
            args = parser.parse_args(
                [
                    "provider-replay",
                    "lifecycle-state-check",
                    "--config",
                    str(config_path),
                    "--stale-after-seconds",
                    "60",
                ]
            )
            with patch("tdxquant.cli.serve_provider_transport_replay") as mocked_serve:
                result = _handle_provider_replay_subcommand(args)

        self.assertTrue(result.ok)
        self.assertEqual(result.data["statefile_check"]["check_status"], "valid")
        self.assertEqual(result.data["statefile_check"]["read_attempted"], True)
        self.assertEqual(result.data["statefile_check"]["write_attempted"], False)
        self.assertEqual(result.data["statefile_check"]["schema_valid"], True)
        self.assertEqual(result.data["statefile_check"]["provider_id_matches"], True)
        self.assertEqual(result.data["statefile_check"]["stale_after_seconds"], 60.0)
        self.assertEqual(result.data["statefile_check"]["stale"], True)
        self.assertEqual(result.data["statefile_check"]["control_allowed"], False)
        mocked_serve.assert_not_called()

    def test_handle_provider_replay_lifecycle_state_check_summary_reports_missing_statefile(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "provider-replay.json"
            state_path = Path(temp_dir) / "missing.state.json"
            config_path.write_text(
                json.dumps(
                    {
                        "provider_id": "provider-replay-a",
                        "bind_host": "127.0.0.1",
                        "port": 0,
                        "token": "secret",
                        "master_allowlist": ["127.0.0.1"],
                        "replay_fixture": "market-snapshot-default",
                        "lifecycle_state_file": str(state_path),
                    }
                ),
                encoding="utf-8",
            )
            args = parser.parse_args(
                [
                    "provider-replay",
                    "lifecycle-state-check",
                    "--config",
                    str(config_path),
                    "--view",
                    "summary",
                ]
            )
            result = _handle_provider_replay_subcommand(args)

        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary_view"]["mode"], "lifecycle-state-check")
        self.assertEqual(result.data["summary_view"]["provider_id"], "provider-replay-a")
        self.assertEqual(result.data["summary_view"]["check_status"], "missing")
        self.assertEqual(result.data["summary_view"]["schema_valid"], None)
        self.assertEqual(result.data["summary_view"]["provider_id_matches"], None)
        self.assertEqual(result.data["summary_view"]["stale"], None)
        self.assertEqual(result.data["summary_view"]["control_allowed"], False)
        self.assertEqual(result.data["summary_view"]["boundary"], "read_only_statefile_check; no_lifecycle_control")

    def test_handle_provider_replay_status_returns_lifecycle_boundary_without_serving(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "provider-replay.json"
            config_path.write_text(
                json.dumps(
                    {
                        "provider_id": "provider-replay-a",
                        "bind_host": "127.0.0.1",
                        "port": 0,
                        "token": "secret",
                        "master_allowlist": ["127.0.0.1"],
                        "replay_fixture": "market-snapshot-default",
                    }
                ),
                encoding="utf-8",
            )
            args = parser.parse_args(
                [
                    "provider-replay",
                    "status",
                    "--config",
                    str(config_path),
                    "--probe-all",
                    "--probe-timeout",
                    "1.5",
                    "--view",
                    "summary",
                ]
            )
            health_probe_result = {
                "enabled": True,
                "status": "healthy",
                "reachable": True,
                "http_status": 200,
                "timeout_seconds": 1.5,
                "service": "provider-transport-replay",
            }
            watch_status_probe_result = {
                "enabled": True,
                "target": "watch_status",
                "endpoint": "/provider/v1/replay/watch/status",
                "status": "healthy",
                "reachable": True,
                "http_status": 200,
                "timeout_seconds": 1.5,
                "service": "provider-transport-replay",
            }
            watch_events_probe_result = {
                "enabled": True,
                "target": "watch_events",
                "endpoint": "/provider/v1/replay/watch/events",
                "status": "healthy",
                "reachable": True,
                "http_status": 200,
                "timeout_seconds": 1.5,
                "service": "provider-transport-replay",
                "event_count": 2,
            }
            watch_stream_probe_result = {
                "enabled": True,
                "target": "watch_stream",
                "endpoint": "/provider/v1/replay/watch/events/stream",
                "status": "unhealthy",
                "reachable": False,
                "http_status": None,
                "error_code": "stream_timeout",
                "timeout_seconds": 1.5,
                "error": {"code": "stream_timeout", "message": "stream probe timed out"},
            }
            with (
                patch("tdxquant.cli.serve_provider_transport_replay") as mocked_serve,
                patch("tdxquant.cli.probe_provider_transport_replay_health", return_value=health_probe_result) as mocked_probe,
                patch(
                    "tdxquant.cli.probe_provider_transport_replay_watch_status",
                    return_value=watch_status_probe_result,
                ) as mocked_watch_status_probe,
                patch(
                    "tdxquant.cli.probe_provider_transport_replay_watch_events",
                    return_value=watch_events_probe_result,
                ) as mocked_watch_events_probe,
                patch(
                    "tdxquant.cli.probe_provider_transport_replay_watch_stream",
                    return_value=watch_stream_probe_result,
                ) as mocked_watch_stream_probe,
            ):
                result = _handle_provider_replay_subcommand(args)

        self.assertTrue(result.ok)
        self.assertEqual(result.data["status"]["provider_id"], "provider-replay-a")
        self.assertEqual(result.data["status"]["transport_mode"], "replay_only")
        self.assertEqual(result.data["status"]["lifecycle"]["start_stop_managed"], False)
        self.assertEqual(result.data["status"]["runtime"]["runtime_observed"], True)
        self.assertEqual(result.data["status"]["runtime"]["health_probe"]["status"], "healthy")
        self.assertEqual(result.data["status"]["runtime"]["watch_status_probe"]["status"], "healthy")
        self.assertEqual(
            result.data["status"]["runtime"]["watch_status_probe"]["endpoint"],
            "/provider/v1/replay/watch/status",
        )
        self.assertEqual(result.data["status"]["runtime"]["watch_events_probe"]["status"], "healthy")
        self.assertEqual(
            result.data["status"]["runtime"]["watch_events_probe"]["endpoint"],
            "/provider/v1/replay/watch/events",
        )
        self.assertEqual(result.data["status"]["runtime"]["watch_stream_probe"]["status"], "unhealthy")
        self.assertEqual(result.data["status"]["runtime"]["watch_stream_probe"]["error_code"], "stream_timeout")
        self.assertEqual(
            result.data["status"]["runtime"]["watch_stream_probe"]["endpoint"],
            "/provider/v1/replay/watch/events/stream",
        )
        self.assertEqual(result.data["status"]["capabilities"]["writes_supported"], False)
        self.assertEqual(result.data["summary_view"]["mode"], "summary")
        self.assertEqual(result.data["summary_view"]["provider_id"], "provider-replay-a")
        self.assertEqual(result.data["summary_view"]["transport_mode"], "replay_only")
        self.assertEqual(result.data["summary_view"]["security"]["bearer_token_required"], True)
        self.assertEqual(result.data["summary_view"]["security"]["source_allowlist_enabled"], True)
        self.assertEqual(result.data["summary_view"]["security"]["master_allowlist_count"], 1)
        self.assertNotIn("token", result.data["summary_view"]["security"])
        self.assertNotIn("master_allowlist", result.data["summary_view"]["security"])
        self.assertEqual(result.data["summary_view"]["replay_source"]["source_kind"], "built_in_fixture")
        self.assertEqual(result.data["summary_view"]["replay_source"]["fixture"], "market-snapshot-default")
        self.assertEqual(result.data["summary_view"]["replay_source"]["fixture_path_provided"], False)
        self.assertNotIn("fixture_path", result.data["summary_view"]["replay_source"])
        self.assertEqual(result.data["summary_view"]["capabilities"]["read_only"], True)
        self.assertEqual(result.data["summary_view"]["capabilities"]["writes_supported"], False)
        self.assertEqual(
            result.data["summary_view"]["capabilities"]["endpoint_count"],
            len(result.data["status"]["capabilities"]["endpoints"]),
        )
        self.assertEqual(
            result.data["summary_view"]["capabilities"]["endpoint_samples"],
            [
                "/provider/v1/replay/health",
                "/provider/v1/replay/fixtures",
                "/provider/v1/replay/result",
            ],
        )
        self.assertEqual(result.data["summary_view"]["capabilities"]["endpoint_sample_limit"], 3)
        self.assertEqual(result.data["summary_view"]["capabilities"]["endpoint_sample_truncated"], True)
        self.assertEqual(
            result.data["summary_view"]["capabilities"]["endpoint_family_counts"],
            {"core": 3, "watch": 3},
        )
        self.assertNotIn("endpoints", result.data["summary_view"]["capabilities"])
        self.assertEqual(result.data["summary_view"]["lifecycle"]["start_stop_managed"], False)
        self.assertEqual(result.data["summary_view"]["lifecycle"]["daemon_managed"], False)
        self.assertEqual(result.data["summary_view"]["lifecycle"]["control_supported"], False)
        self.assertEqual(result.data["summary_view"]["lifecycle"]["managed_operation_count"], 0)
        self.assertEqual(
            result.data["summary_view"]["lifecycle"]["ownership_summary"],
            result.data["status"]["lifecycle"]["ownership_summary"],
        )
        self.assertEqual(
            result.data["summary_view"]["lifecycle"]["control_summary"],
            result.data["status"]["lifecycle"]["control_summary"],
        )
        self.assertEqual(
            result.data["summary_view"]["lifecycle"]["operation_summary"],
            result.data["status"]["lifecycle"]["operation_summary"],
        )
        self.assertEqual(
            result.data["summary_view"]["lifecycle"]["backoff_summary"],
            result.data["status"]["lifecycle"]["backoff_summary"],
        )
        self.assertEqual(
            result.data["summary_view"]["lifecycle"]["supervision_summary"],
            result.data["status"]["lifecycle"]["supervision_summary"],
        )
        self.assertEqual(result.data["summary_view"]["runtime"]["runtime_observed"], True)
        self.assertEqual(result.data["summary_view"]["runtime"]["probe_requested"], True)
        self.assertEqual(
            result.data["summary_view"]["status_summary"],
            {
                "provider_id": "provider-replay-a",
                "transport_mode": "replay_only",
                "source_kind": "built_in_fixture",
                "fixture": "market-snapshot-default",
                "read_only": True,
                "writes_supported": False,
                "endpoint_count": len(result.data["status"]["capabilities"]["endpoints"]),
                "probe_requested": True,
                "requested_probe_count": 4,
                "failed_probe_count": 1,
                "probe_status": "degraded",
                "probe_request_coverage_status": "complete",
                "has_problem_probe": True,
                "primary_problem_probe": "watch_stream_probe",
                "control_supported": False,
                "managed_operation_count": 0,
                "lifecycle_ownership_status": "not_managed",
                "lifecycle_owned_process": False,
                "lifecycle_control_status": "unsupported",
                "lifecycle_blocking_reason": "lifecycle_control_not_implemented",
                "lifecycle_operation_count": 4,
                "lifecycle_available_operation_count": 0,
                "lifecycle_blocked_operation_count": 4,
                "lifecycle_primary_blocked_operation": "start",
                "lifecycle_supervision_status": "not_supervised",
                "lifecycle_supervisor_configured": False,
                "lifecycle_desired_state": "unmanaged",
                "lifecycle_observed_state": "not_observed",
                "lifecycle_process_identity_status": "not_tracked",
                "boundary_count": len(result.data["status"]["boundaries"]),
                "runtime_observed": True,
                "live_runtime_required": result.data["status"]["runtime"]["live_runtime_required"],
            },
        )
        self.assertEqual(result.data["summary_view"]["probe_summary"]["status"], "degraded")
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["request_coverage_status"],
            "complete",
        )
        self.assertEqual(result.data["summary_view"]["probe_summary"]["total_count"], 4)
        self.assertEqual(result.data["summary_view"]["probe_summary"]["requested_count"], 4)
        self.assertEqual(result.data["summary_view"]["probe_summary"]["unhealthy_count"], 1)
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["primary_requested_probe"],
            "health_probe",
        )
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["primary_healthy_probe"],
            "health_probe",
        )
        self.assertEqual(result.data["summary_view"]["probe_summary"]["has_healthy_probe"], True)
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["primary_failed_probe"],
            "watch_stream_probe",
        )
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["primary_unhealthy_probe"],
            "watch_stream_probe",
        )
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["primary_problem_probe"],
            "watch_stream_probe",
        )
        self.assertIsNone(result.data["summary_view"]["probe_summary"]["primary_not_requested_probe"])
        self.assertEqual(result.data["summary_view"]["probe_summary"]["has_requested_probe"], True)
        self.assertEqual(result.data["summary_view"]["probe_summary"]["has_not_requested_probe"], False)
        self.assertEqual(result.data["summary_view"]["probe_summary"]["all_probes_requested"], True)
        self.assertEqual(result.data["summary_view"]["probe_summary"]["has_failed_probe"], True)
        self.assertEqual(result.data["summary_view"]["probe_summary"]["has_unhealthy_probe"], True)
        self.assertEqual(result.data["summary_view"]["probe_summary"]["has_problem_probe"], True)
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["request_summary"],
            {
                "status": result.data["summary_view"]["probe_summary"]["request_coverage_status"],
                "total_count": result.data["summary_view"]["probe_summary"]["total_count"],
                "requested_count": result.data["summary_view"]["probe_summary"]["requested_count"],
                "not_requested_count": result.data["summary_view"]["probe_summary"]["not_requested_count"],
                "healthy_count": result.data["summary_view"]["probe_summary"]["healthy_count"],
                "failed_count": result.data["summary_view"]["probe_summary"]["failed_count"],
                "unhealthy_count": result.data["summary_view"]["probe_summary"]["unhealthy_count"],
                "primary_requested_probe": result.data["summary_view"]["probe_summary"][
                    "primary_requested_probe"
                ],
                "primary_not_requested_probe": result.data["summary_view"]["probe_summary"][
                    "primary_not_requested_probe"
                ],
            },
        )
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["health_summary"],
            {
                "status": result.data["summary_view"]["probe_summary"]["status"],
                "healthy_count": result.data["summary_view"]["probe_summary"]["healthy_count"],
                "failed_count": result.data["summary_view"]["probe_summary"]["failed_count"],
                "unhealthy_count": result.data["summary_view"]["probe_summary"]["unhealthy_count"],
                "has_healthy_probe": result.data["summary_view"]["probe_summary"]["has_healthy_probe"],
                "has_failed_probe": result.data["summary_view"]["probe_summary"]["has_failed_probe"],
                "has_unhealthy_probe": result.data["summary_view"]["probe_summary"]["has_unhealthy_probe"],
                "status_key_count": result.data["summary_view"]["probe_summary"]["status_key_count"],
                "primary_healthy_probe": result.data["summary_view"]["probe_summary"]["primary_healthy_probe"],
                "primary_failed_probe": result.data["summary_view"]["probe_summary"]["primary_failed_probe"],
                "primary_unhealthy_probe": result.data["summary_view"]["probe_summary"][
                    "primary_unhealthy_probe"
                ],
            },
        )
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["outcome_summary"],
            {
                "status": "degraded",
                "request_coverage_status": "complete",
                "total_count": 4,
                "requested_count": 4,
                "healthy_count": 3,
                "failed_count": 1,
                "unhealthy_count": 1,
                "not_requested_count": 0,
                "all_probes_requested": True,
                "has_failed_probe": True,
                "has_unhealthy_probe": True,
                "primary_problem_probe": "watch_stream_probe",
                "primary_error_sample_probe": "watch_stream_probe",
                "primary_error_sample_status": "unhealthy",
            },
        )
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["advisory_summary"],
            {
                "status": "degraded",
                "request_coverage_status": "complete",
                "total_count": 4,
                "requested_count": 4,
                "healthy_count": 3,
                "failed_count": 1,
                "unhealthy_count": 1,
                "has_requested_probe": True,
                "has_healthy_probe": True,
                "has_failed_probe": True,
                "has_unhealthy_probe": True,
                "has_problem_probe": True,
                "primary_problem_probe": "watch_stream_probe",
                "primary_error_sample_probe": "watch_stream_probe",
                "boundary": "read_only_probe_summary",
            },
        )
        self.assertEqual(result.data["summary_view"]["probe_summary"]["status_counts"], {"healthy": 3, "unhealthy": 1})
        self.assertEqual(result.data["summary_view"]["probe_summary"]["failed_status_counts"], {"unhealthy": 1})
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["requested_reachability_counts"],
            {"reachable": 3, "unreachable": 1},
        )
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["healthy_reachability_counts"],
            {"reachable": 3},
        )
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["failed_reachability_counts"],
            {"unreachable": 1},
        )
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["requested_http_status_counts"],
            {"200": 3},
        )
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["healthy_http_status_counts"],
            {"200": 3},
        )
        self.assertEqual(result.data["summary_view"]["probe_summary"]["failed_http_status_counts"], {})
        self.assertEqual(result.data["summary_view"]["probe_summary"]["error_code_counts"], {"stream_timeout": 1})
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["failed_error_code_counts"],
            {"stream_timeout": 1},
        )
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["error_samples"],
            [{"probe": "watch_stream_probe", "status": "unhealthy", "error_code": "stream_timeout"}],
        )
        self.assertEqual(result.data["summary_view"]["probe_summary"]["error_sample_count"], 1)
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["error_sample_status_counts"],
            {"unhealthy": 1},
        )
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["error_sample_probe_counts"],
            {"watch_stream_probe": 1},
        )
        self.assertEqual(result.data["summary_view"]["probe_summary"]["error_sample_http_status_counts"], {})
        self.assertEqual(result.data["summary_view"]["probe_summary"]["error_sample_http_status_key_count"], 0)
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["error_sample_reachability_counts"],
            {"unreachable": 1},
        )
        self.assertEqual(result.data["summary_view"]["probe_summary"]["error_sample_reachability_key_count"], 1)
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["primary_error_sample_reachability"],
            "unreachable",
        )
        self.assertEqual(result.data["summary_view"]["probe_summary"]["error_sample_limit"], 3)
        self.assertEqual(result.data["summary_view"]["probe_summary"]["has_visible_error_sample"], True)
        self.assertEqual(result.data["summary_view"]["probe_summary"]["error_sample_truncated"], False)
        self.assertEqual(result.data["summary_view"]["probe_summary"]["has_hidden_error_sample"], False)
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["error_sample_summary"],
            {
                "count": 1,
                "visible_count": 1,
                "hidden_count": 0,
                "limit": 3,
                "truncated": False,
                "primary_probe": "watch_stream_probe",
                "primary_status": "unhealthy",
                "primary_error_code": "stream_timeout",
                "primary_http_status": None,
                "primary_reachability": "unreachable",
            },
        )
        self.assertEqual(result.data["summary_view"]["probe_summary"]["has_error_sample"], True)
        self.assertEqual(
            result.data["summary_view"]["probe_summary"]["healthy"],
            ["health_probe", "watch_status_probe", "watch_events_probe"],
        )
        self.assertEqual(result.data["summary_view"]["probe_summary"]["unhealthy"], ["watch_stream_probe"])
        self.assertEqual(result.data["summary_view"]["probe_summary"]["failed"], ["watch_stream_probe"])
        self.assertEqual(result.data["summary_view"]["probe_summary"]["not_requested"], [])
        self.assertIn("no daemon start/stop lifecycle management", result.data["summary_view"]["boundaries"])
        mocked_serve.assert_not_called()
        mocked_probe.assert_called_once()
        self.assertEqual(mocked_probe.call_args.kwargs["timeout_seconds"], 1.5)
        mocked_watch_status_probe.assert_called_once()
        self.assertEqual(mocked_watch_status_probe.call_args.kwargs["timeout_seconds"], 1.5)
        mocked_watch_events_probe.assert_called_once()
        self.assertEqual(mocked_watch_events_probe.call_args.kwargs["timeout_seconds"], 1.5)
        mocked_watch_stream_probe.assert_called_once()
        self.assertEqual(mocked_watch_stream_probe.call_args.kwargs["timeout_seconds"], 1.5)

    def test_handle_provider_replay_status_summary_reports_configured_managed_lifecycle(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "provider-replay.json"
            state_path = Path(temp_dir) / "provider-replay.state.json"
            config_path.write_text(
                json.dumps(
                    {
                        "provider_id": "provider-replay-a",
                        "bind_host": "127.0.0.1",
                        "port": 0,
                        "token": "secret",
                        "master_allowlist": ["127.0.0.1"],
                        "replay_fixture": "market-snapshot-default",
                        "lifecycle_state_file": str(state_path),
                    }
                ),
                encoding="utf-8",
            )
            args = parser.parse_args(
                [
                    "provider-replay",
                    "status",
                    "--config",
                    str(config_path),
                    "--view",
                    "summary",
                ]
            )
            with (
                patch("tdxquant.cli.serve_provider_transport_replay") as mocked_serve,
                patch("tdxquant.cli.start_provider_replay_managed_daemon") as mocked_start,
                patch("tdxquant.cli.stop_provider_replay_managed_daemon") as mocked_stop,
                patch("tdxquant.cli.run_provider_replay_managed_daemon_supervisor") as mocked_supervise,
            ):
                result = _handle_provider_replay_subcommand(args)

        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary_view"]["lifecycle"]["start_stop_managed"], True)
        self.assertEqual(result.data["summary_view"]["lifecycle"]["daemon_managed"], True)
        self.assertEqual(result.data["summary_view"]["lifecycle"]["restart_policy"], "operator_opt_in")
        self.assertEqual(result.data["summary_view"]["lifecycle"]["control_supported"], True)
        self.assertEqual(result.data["summary_view"]["lifecycle"]["managed_operation_count"], 3)
        self.assertEqual(
            result.data["summary_view"]["lifecycle"]["control_summary"]["control_status"],
            "operator_opt_in_available",
        )
        self.assertEqual(
            result.data["summary_view"]["lifecycle"]["control_summary"]["available_operations"],
            ["start", "status", "stop", "supervise", "restart_backoff"],
        )
        self.assertEqual(
            result.data["summary_view"]["lifecycle"]["operation_summary"]["available_count"],
            5,
        )
        self.assertEqual(
            result.data["summary_view"]["lifecycle"]["supervision_summary"]["supervision_status"],
            "operator_opt_in_available",
        )
        self.assertEqual(result.data["summary_view"]["status_summary"]["control_supported"], True)
        self.assertEqual(result.data["summary_view"]["status_summary"]["managed_operation_count"], 3)
        self.assertEqual(
            result.data["summary_view"]["status_summary"]["lifecycle_control_status"],
            "operator_opt_in_available",
        )
        self.assertEqual(
            result.data["summary_view"]["status_summary"]["lifecycle_supervision_status"],
            "operator_opt_in_available",
        )
        self.assertFalse(state_path.exists())
        mocked_serve.assert_not_called()
        mocked_start.assert_not_called()
        mocked_stop.assert_not_called()
        mocked_supervise.assert_not_called()

    def test_handle_provider_replay_serve_delegates_to_foreground_server(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["provider-replay", "serve", "--config", "runtime/provider-transport-replay.example.json"])
        loaded_config = MagicMock(provider_id="provider-replay-a", bind_host="127.0.0.1", port=0)
        with (
            patch("tdxquant.cli.load_provider_transport_replay_config", return_value=loaded_config) as mocked_load,
            patch("tdxquant.cli.serve_provider_transport_replay", return_value=0) as mocked_serve,
        ):
            result = _handle_provider_replay_subcommand(args)

        self.assertTrue(result.ok)
        self.assertEqual(result.data["exit_code"], 0)
        mocked_load.assert_called_once_with("runtime/provider-transport-replay.example.json")
        mocked_serve.assert_called_once_with(loaded_config)


class ApiCliDispatchTests(unittest.TestCase):
    def test_handle_api_snapshot_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "snapshot", "--code", "688260.SH"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.market.snapshot.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager:
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(profile="default", strategy_path=None)
        manager.market.snapshot.assert_called_once_with("688260.SH", fields=None)

    def test_handle_api_formula_screen_replay_uses_manager_replay_configuration(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "formula-screen",
                "--formula-name",
                "UPN",
                "--code",
                "000001.SZ",
                "--provider-mode",
                "replay",
                "--fixture",
                "formula-screen-failure",
            ]
        )
        expected = Result(ok=False, code=ErrorCode.INVALID_REQUEST, message="fixture failure")
        manager = MagicMock()
        manager.formula.screen.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager:
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture="formula-screen-failure",
            replay_fixture_path=None,
        )
        manager.formula.screen.assert_called_once_with(
            formula_name="UPN",
            stock_list=["000001.SZ"],
            formula_arg="",
            return_count=1,
            return_date=False,
            stock_period="1d",
            start_time="",
            end_time="",
            count=0,
            dividend_type=0,
        )

    def test_handle_api_snapshot_replay_rejects_unsupported_command_before_manager_construction(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "snapshot", "--code", "000001.SZ", "--provider-mode", "replay"])
        with patch("tdxquant.cli.TdxApiManager") as mocked_manager:
            result = _handle_api_subcommand(args)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(result.message, "unsupported replay api command: snapshot")
        self.assertEqual(result.data["replay_source"]["mode"], "replay")
        self.assertEqual(result.data["replay_source"]["capability"], "market.snapshot")
        mocked_manager.assert_not_called()

    def test_handle_api_market_snapshot_replay_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "market-snapshot",
                "--code",
                "000001.SZ",
                "--field",
                "Now",
                "--field",
                "Volume",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "market.market_snapshot"}},
        )
        manager = MagicMock()
        manager.market.market_snapshot.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager:
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.market.market_snapshot.assert_called_once_with("000001.SZ", fields=["Now", "Volume"])

    def test_handle_api_subscription_one_shot_replay_uses_manager(self) -> None:
        parser = build_parser()
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"operation": {"scope": "one_shot"}},
        )
        manager = MagicMock()
        manager.runtime.subscription_subscribe.return_value = expected
        manager.runtime.subscription_unsubscribe.return_value = expected
        manager.runtime.subscription_list.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager:
            subscribe = _handle_api_subcommand(
                parser.parse_args(
                    ["api", "subscription-subscribe", "--code", "688318.SH", "--provider-mode", "replay"]
                )
            )
            unsubscribe = _handle_api_subcommand(
                parser.parse_args(
                    ["api", "subscription-unsubscribe", "--code", "688318.SH", "--provider-mode", "replay"]
                )
            )
            listing = _handle_api_subcommand(parser.parse_args(["api", "subscription-list", "--provider-mode", "replay"]))
        self.assertIs(subscribe, expected)
        self.assertIs(unsubscribe, expected)
        self.assertIs(listing, expected)
        self.assertEqual(mocked_manager.call_count, 3)
        mocked_manager.assert_any_call(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.runtime.subscription_subscribe.assert_called_once_with(stock_list=["688318.SH"])
        manager.runtime.subscription_unsubscribe.assert_called_once_with(stock_list=["688318.SH"])
        manager.runtime.subscription_list.assert_called_once_with()

    def test_handle_api_stock_info_replay_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "stock-info",
                "--code",
                "688260.SH",
                "--field",
                "symbol",
                "--field",
                "name",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "market.stock_info"}},
        )
        manager = MagicMock()
        manager.market.stock_info.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager:
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.market.stock_info.assert_called_once_with("688260.SH", fields=["symbol", "name"])

    def test_handle_api_more_info_replay_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "more-info",
                "--code",
                "688260.SH",
                "--field",
                "symbol",
                "--field",
                "industry",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "market.more_info"}},
        )
        manager = MagicMock()
        manager.market.more_info.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager:
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.market.more_info.assert_called_once_with("688260.SH", fields=["symbol", "industry"])

    def test_handle_api_cb_info_replay_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "cb-info",
                "--code",
                "113015.SZ",
                "--field",
                "symbol",
                "--field",
                "name",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "market.cb_info"}},
        )
        manager = MagicMock()
        manager.market.cb_info.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager:
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.market.cb_info.assert_called_once_with("113015.SZ", fields=["symbol", "name"])

    def test_handle_api_gb_info_replay_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "gb-info",
                "--code",
                "000001.SZ",
                "--date",
                "20250101",
                "--date",
                "20241231",
                "--count",
                "2",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "meta.gb_info"}},
        )
        manager = MagicMock()
        manager.meta.gb_info.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager:
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.meta.gb_info.assert_called_once_with(
            stock_code="000001.SZ",
            date_list=["20250101", "20241231"],
            count=2,
        )

    def test_handle_api_ipo_info_replay_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "ipo-info",
                "--ipo-type",
                "2",
                "--ipo-date",
                "1",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "meta.ipo_info"}},
        )
        manager = MagicMock()
        manager.meta.ipo_info.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager:
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.meta.ipo_info.assert_called_once_with(ipo_type=2, ipo_date=1)

    def test_handle_api_gp_one_replay_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "gp-one",
                "--code",
                "000001.SZ",
                "--code",
                "600519.SH",
                "--field",
                "Now",
                "--field",
                "Volume",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "meta.gp_one_data"}},
        )
        manager = MagicMock()
        manager.meta.gp_one_data.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager:
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.meta.gp_one_data.assert_called_once_with(
            stock_list=["000001.SZ", "600519.SH"],
            fields=["Now", "Volume"],
        )

    def test_handle_api_divid_factors_replay_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "divid-factors",
                "--code",
                "688318.SH",
                "--start-time",
                "20200101",
                "--end-time",
                "20241231",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "meta.divid_factors"}},
        )
        manager = MagicMock()
        manager.meta.divid_factors.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager:
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.meta.divid_factors.assert_called_once_with(
            stock_code="688318.SH",
            start_time="20200101",
            end_time="20241231",
        )

    def test_handle_api_kline_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "kline", "--code", "688260.SH", "--period", "1d"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.market.kline.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.market.kline.assert_called_once_with(
            stock_list=["688260.SH"],
            period="1d",
            start_time="",
            end_time="",
            count=-1,
            dividend_type=None,
            fields=None,
            fill_data=None,
        )

    def test_handle_api_full_tick_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "full-tick", "--code", "688260.SH"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.market.full_tick.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.market.full_tick.assert_called_once_with("688260.SH", fields=None)

    def test_handle_api_full_tick_replay_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "full-tick",
                "--code",
                "688260.SH",
                "--field",
                "Now",
                "--field",
                "Volume",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "market.full_tick"}},
        )
        manager = MagicMock()
        manager.market.full_tick.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager:
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.market.full_tick.assert_called_once_with("688260.SH", fields=["Now", "Volume"])

    def test_handle_api_capabilities_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "capabilities"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.runtime.capabilities.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.runtime.capabilities.assert_called_once_with()

    def test_handle_api_subscription_one_shot_uses_manager(self) -> None:
        parser = build_parser()
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.runtime.subscription_subscribe.return_value = expected
        manager.runtime.subscription_unsubscribe.return_value = expected
        manager.runtime.subscription_list.return_value = expected

        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            subscribe_result = _handle_api_subcommand(
                parser.parse_args(["api", "subscription-subscribe", "--code", "688318.SH"])
            )
            unsubscribe_result = _handle_api_subcommand(
                parser.parse_args(["api", "subscription-unsubscribe", "--code", "688318.SH"])
            )
            list_result = _handle_api_subcommand(parser.parse_args(["api", "subscription-list"]))

        self.assertIs(subscribe_result, expected)
        self.assertIs(unsubscribe_result, expected)
        self.assertIs(list_result, expected)
        manager.runtime.subscription_subscribe.assert_called_once_with(stock_list=["688318.SH"])
        manager.runtime.subscription_unsubscribe.assert_called_once_with(stock_list=["688318.SH"])
        manager.runtime.subscription_list.assert_called_once_with()

    def test_handle_api_trading_dates_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "trading-dates", "--market", "SH", "--start-time", "20250101", "--count", "10"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.runtime.trading_dates.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.runtime.trading_dates.assert_called_once_with(
            market="SH",
            start_time="20250101",
            end_time="",
            count=10,
        )

    def test_handle_api_refresh_kline_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "refresh-kline", "--code", "688260.SH", "--period", "1d"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.runtime.refresh_kline.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.runtime.refresh_kline.assert_called_once_with(
            stock_list=["688260.SH"],
            period="1d",
        )

    def test_handle_api_download_file_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "download-file", "--code", "688318.SH", "--down-time", "20250101", "--down-type", "2"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.runtime.download_file.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.runtime.download_file.assert_called_once_with(
            stock_code="688318.SH",
            down_time="20250101",
            down_type=2,
        )

    def test_handle_api_health_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "health", "--window-key", "平安证券", "--hid-port", "COM3"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.runtime.health.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.runtime.health.assert_called_once_with(window_key="平安证券", hid_port="COM3")

    def test_handle_api_send_warn_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "send-warn",
                "--code",
                "688318.SH",
                "--code",
                "600519.SH",
                "--time",
                "20251215141115",
                "--time",
                "20251215142100",
                "--price",
                "123.45",
                "--close",
                "122.50",
                "--volume",
                "1000",
                "--bs-flag",
                "0",
                "--warn-type",
                "0",
                "--reason",
                "价格突破预警线",
                "--count",
                "2",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.runtime.send_warn.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.runtime.send_warn.assert_called_once_with(
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

    def test_handle_api_doctor_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "doctor", "--window-key", "通达信金融终端"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.runtime.doctor.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.runtime.doctor.assert_called_once_with(window_key="通达信金融终端", hid_port=None)

    def test_handle_api_divid_factors_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "divid-factors", "--code", "688318.SH", "--start-time", "20200101", "--end-time", "20241231"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.meta.divid_factors.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.meta.divid_factors.assert_called_once_with(
            stock_code="688318.SH",
            start_time="20200101",
            end_time="20241231",
        )

    def test_handle_api_ipo_info_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "ipo-info", "--ipo-type", "2", "--ipo-date", "1"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.meta.ipo_info.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.meta.ipo_info.assert_called_once_with(
            ipo_type=2,
            ipo_date=1,
        )

    def test_handle_api_financial_data_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "financial-data",
                "--code",
                "688318.SH",
                "--field",
                "FN1",
                "--field",
                "FN2",
                "--start-time",
                "20240101",
                "--end-time",
                "20241231",
                "--report-type",
                "announce_time",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.financial.financial_data.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.financial.financial_data.assert_called_once_with(
            stock_list=["688318.SH"],
            fields=["FN1", "FN2"],
            start_time="20240101",
            end_time="20241231",
            report_type="announce_time",
        )

    def test_handle_api_financial_data_by_date_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "financial-data-by-date",
                "--code",
                "688318.SH",
                "--field",
                "FN193",
                "--year",
                "2025",
                "--mmdd",
                "331",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.financial.financial_data_by_date.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.financial.financial_data_by_date.assert_called_once_with(
            stock_list=["688318.SH"],
            fields=["FN193"],
            year=2025,
            mmdd=331,
        )

    def test_handle_api_stock_transaction_data_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "stock-transaction-data",
                "--code",
                "600519.SH",
                "--field",
                "GP01",
                "--field",
                "GP02",
                "--start-time",
                "20240101",
                "--end-time",
                "20241231",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.transaction.stock_transaction_data.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.transaction.stock_transaction_data.assert_called_once_with(
            stock_list=["600519.SH"],
            fields=["GP01", "GP02"],
            start_time="20240101",
            end_time="20241231",
        )

    def test_handle_api_stock_transaction_data_by_date_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "stock-transaction-data-by-date",
                "--code",
                "600519.SH",
                "--field",
                "GP01",
                "--year",
                "0",
                "--mmdd",
                "0",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.transaction.stock_transaction_data_by_date.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.transaction.stock_transaction_data_by_date.assert_called_once_with(
            stock_list=["600519.SH"],
            fields=["GP01"],
            year=0,
            mmdd=0,
        )

    def test_handle_api_stock_transaction_data_by_date_replay_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "stock-transaction-data-by-date",
                "--code",
                "000001.SZ",
                "--code",
                "000002.SZ",
                "--field",
                "price",
                "--field",
                "volume",
                "--year",
                "2025",
                "--mmdd",
                "101",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "transaction.stock_transaction_data_by_date"}},
        )
        manager = MagicMock()
        manager.transaction.stock_transaction_data_by_date.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager:
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.transaction.stock_transaction_data_by_date.assert_called_once_with(
            stock_list=["000001.SZ", "000002.SZ"],
            fields=["price", "volume"],
            year=2025,
            mmdd=101,
        )

    def test_handle_api_sector_list_replay_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "sector-list", "--list-type", "0", "--provider-mode", "replay"])
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "meta.sector_list"}},
        )
        manager = MagicMock()
        manager.meta.sector_list.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager:
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.meta.sector_list.assert_called_once_with(list_type=0)

    def test_handle_api_sector_transaction_data_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "sector-transaction-data",
                "--code",
                "880660.SH",
                "--field",
                "BK5",
                "--field",
                "BK6",
                "--start-time",
                "20240101",
                "--end-time",
                "20241231",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.transaction.sector_transaction_data.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.transaction.sector_transaction_data.assert_called_once_with(
            stock_list=["880660.SH"],
            fields=["BK5", "BK6"],
            start_time="20240101",
            end_time="20241231",
        )

    def test_handle_api_sector_transaction_data_replay_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "sector-transaction-data",
                "--code",
                "880660.SH",
                "--code",
                "880001.SH",
                "--field",
                "BK5",
                "--field",
                "BK6",
                "--start-time",
                "20240101",
                "--end-time",
                "20241231",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "transaction.sector_transaction_data"}},
        )
        manager = MagicMock()
        manager.transaction.sector_transaction_data.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager:
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.transaction.sector_transaction_data.assert_called_once_with(
            stock_list=["880660.SH", "880001.SH"],
            fields=["BK5", "BK6"],
            start_time="20240101",
            end_time="20241231",
        )

    def test_handle_api_sector_transaction_data_by_date_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "sector-transaction-data-by-date",
                "--code",
                "880660.SH",
                "--field",
                "BK9",
                "--year",
                "0",
                "--mmdd",
                "0",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.transaction.sector_transaction_data_by_date.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.transaction.sector_transaction_data_by_date.assert_called_once_with(
            stock_list=["880660.SH"],
            fields=["BK9"],
            year=0,
            mmdd=0,
        )

    def test_handle_api_sector_transaction_data_by_date_replay_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "sector-transaction-data-by-date",
                "--code",
                "880660.SH",
                "--code",
                "880001.SH",
                "--field",
                "BK9",
                "--field",
                "BK10",
                "--year",
                "2025",
                "--mmdd",
                "101",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "transaction.sector_transaction_data_by_date"}},
        )
        manager = MagicMock()
        manager.transaction.sector_transaction_data_by_date.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager:
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.transaction.sector_transaction_data_by_date.assert_called_once_with(
            stock_list=["880660.SH", "880001.SH"],
            fields=["BK9", "BK10"],
            year=2025,
            mmdd=101,
        )

    def test_handle_api_market_transaction_data_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "market-transaction-data",
                "--field",
                "SC01",
                "--field",
                "SC02",
                "--start-time",
                "20250101",
                "--end-time",
                "20250102",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.transaction.market_transaction_data.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.transaction.market_transaction_data.assert_called_once_with(
            fields=["SC01", "SC02"],
            start_time="20250101",
            end_time="20250102",
        )

    def test_handle_api_market_transaction_data_by_date_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "market-transaction-data-by-date",
                "--field",
                "SC06",
                "--year",
                "0",
                "--mmdd",
                "0",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.transaction.market_transaction_data_by_date.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.transaction.market_transaction_data_by_date.assert_called_once_with(
            fields=["SC06"],
            year=0,
            mmdd=0,
        )

    def test_handle_api_market_transaction_data_by_date_replay_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "market-transaction-data-by-date",
                "--field",
                "field_a",
                "--field",
                "field_b",
                "--year",
                "2025",
                "--mmdd",
                "101",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "transaction.market_transaction_data_by_date"}},
        )
        manager = MagicMock()
        manager.transaction.market_transaction_data_by_date.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager:
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.transaction.market_transaction_data_by_date.assert_called_once_with(
            fields=["field_a", "field_b"],
            year=2025,
            mmdd=101,
        )

    def test_handle_api_invalid_profile_returns_invalid_request(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "snapshot", "--code", "688260.SH"])
        with patch("tdxquant.cli.TdxApiManager", side_effect=ValueError("unsupported api profile: bad")):
            result = _handle_api_subcommand(args)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)

    def test_handle_api_formula_xg_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "formula-xg", "--formula-name", "SCAN"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.formula.xg.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.formula.xg.assert_called_once_with(formula_name="SCAN", formula_arg="")

    def test_handle_api_formula_capabilities_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "formula-capabilities"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.formula.capabilities.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.formula.capabilities.assert_called_once_with()
        manager.formula.xg.assert_not_called()
        manager.formula.screen.assert_not_called()

    def test_handle_api_formula_screen_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "formula-screen",
                "--formula-name",
                "UPN",
                "--code",
                "000001.SZ",
                "--code",
                "600519.SH",
                "--formula-arg",
                "3",
                "--return-count",
                "3",
                "--return-date",
                "--count",
                "5",
                "--dividend-type",
                "1",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.formula.screen.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.formula.screen.assert_called_once_with(
            formula_name="UPN",
            stock_list=["000001.SZ", "600519.SH"],
            formula_arg="3",
            return_count=3,
            return_date=True,
            stock_period="1d",
            start_time="",
            end_time="",
            count=5,
            dividend_type=1,
        )

    def test_handle_api_send_user_block_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "send-user-block", "--block-code", "ZXG", "--stock", "000001"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block.send_user_block.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.block.send_user_block.assert_called_once_with(block_code="ZXG", stocks=["000001"], show=False)

    def test_handle_api_send_user_block_forwards_mutation_safety_options(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "send-user-block",
                "--block-code",
                "ZXG",
                "--stock",
                "000001",
                "--show",
                "--mutation-key",
                "mk-send-1",
                "--audit-dir",
                "runtime/block-mutations",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block.send_user_block.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.block.send_user_block.assert_called_once_with(
            block_code="ZXG",
            stocks=["000001"],
            show=True,
            mutation_key="mk-send-1",
            audit_dir="runtime/block-mutations",
        )

    def test_handle_api_send_user_block_replay_uses_replay_manager_configuration(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "send-user-block",
                "--block-code",
                "ZXG",
                "--stock",
                "000001",
                "--provider-mode",
                "replay",
                "--fixture",
                "block-send-user-block-noop",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="noop", data={"block_mutation": {"status": "noop"}})
        manager = MagicMock()
        manager.block.send_user_block.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager:
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture="block-send-user-block-noop",
            replay_fixture_path=None,
        )
        manager.block.send_user_block.assert_called_once_with(block_code="ZXG", stocks=["000001"], show=False)

    def test_handle_api_block_read_watchlist_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "block-read-watchlist", "--block-code", "ZXG"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"snapshot": {"block_code": "ZXG"}})
        manager = MagicMock()
        manager.block.read_watchlist_snapshot.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.block.read_watchlist_snapshot.assert_called_once_with(block_code="ZXG")

    def test_handle_api_block_sync_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "block-sync",
                "--block-code",
                "ZXG",
                "--stock",
                "000001.SZ",
                "--stock",
                "600519.SH",
                "--mode",
                "merge",
                "--write-policy",
                "merge_dry_run",
                "--create-if-missing",
                "--dry-run",
                "--show",
                "--mutation-key",
                "sync-001",
                "--audit-dir",
                "runtime/block-sync",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="planned", data={"sync": {"mode": "merge"}})
        manager = MagicMock()
        manager.block.sync_watchlist.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.block.sync_watchlist.assert_called_once_with(
            block_code="ZXG",
            symbols=["000001.SZ", "600519.SH"],
            mode="merge",
            write_policy="merge_dry_run",
            create_if_missing=True,
            dry_run=True,
            show=True,
            mutation_key="sync-001",
            audit_dir="runtime/block-sync",
        )

    def test_run_flat_replay_provider_command_returns_replay_source_for_unsupported_command(self) -> None:
        args = argparse.Namespace(
            command="tdx-data-kline",
            provider_mode="replay",
            strategy_path=None,
            fixture=None,
            fixture_path=None,
        )
        result = _run_flat_replay_provider_command(args)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(result.data["replay_source"]["mode"], "replay")
        self.assertEqual(result.data["replay_source"]["capability"], "tdx-data-kline")

    def test_handle_api_user_sectors_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "user-sectors"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block.user_sectors.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.block.user_sectors.assert_called_once_with()

    def test_handle_api_create_sector_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "create-sector", "--block-code", "CSBK", "--block-name", "测试板块"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block.create_sector.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.block.create_sector.assert_called_once_with(block_code="CSBK", block_name="测试板块")

    def test_handle_api_create_sector_forwards_mutation_safety_options(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "api",
                "create-sector",
                "--block-code",
                "CSBK",
                "--block-name",
                "测试板块",
                "--mutation-key",
                "mk-001",
                "--audit-dir",
                "runtime/block-mutations",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block.create_sector.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.block.create_sector.assert_called_once_with(
            block_code="CSBK",
            block_name="测试板块",
            mutation_key="mk-001",
            audit_dir="runtime/block-mutations",
        )

    def test_handle_api_delete_sector_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "delete-sector", "--block-code", "CSBK"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block.delete_sector.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.block.delete_sector.assert_called_once_with(block_code="CSBK")

    def test_handle_api_rename_sector_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "rename-sector", "--block-code", "CSBK", "--block-name", "测试板块重命名"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block.rename_sector.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.block.rename_sector.assert_called_once_with(block_code="CSBK", block_name="测试板块重命名")

    def test_handle_api_clear_sector_uses_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "clear-sector", "--block-code", "CSBK"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block.clear_sector.return_value = expected
        with patch("tdxquant.cli.TdxApiManager", return_value=manager):
            result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.block.clear_sector.assert_called_once_with(block_code="CSBK")

    def test_handle_catalog_list_returns_resolved_metadata(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--entry", "daily-review"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["selected_entry"], "daily-review")
        self.assertEqual(result.data["entries"][0]["name"], "daily-review")
        self.assertEqual(result.data["entries"][0]["source"], "report")
        self.assertEqual(result.data["entries"][0]["preset"], "daily-review")
        self.assertEqual(result.data["entries"][0]["command"], "daily")
        self.assertIsInstance(result.data["entries"][0]["labels"], list)
        self.assertIn("summary_view", result.data)

    def test_handle_catalog_list_builds_summary_view(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "bundle", "--label", "morning"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        summary_view = result.data["summary_view"]
        self.assertEqual(summary_view["mode"], "list")
        self.assertEqual(summary_view["kind"], "bundle")
        self.assertEqual(summary_view["selected_label"], "morning")
        self.assertTrue(all("step_names" in row for row in summary_view["bundles"]))

    def test_handle_catalog_bundle_list_returns_resolved_metadata(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "bundle", "--bundle", "refresh-review"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["selected_bundle"], "refresh-review")
        self.assertEqual(result.data["bundles"][0]["name"], "refresh-review")
        self.assertIsInstance(result.data["bundles"][0]["labels"], list)
        self.assertEqual(result.data["bundles"][0]["steps"][0]["index"], 1)
        self.assertEqual(result.data["bundles"][0]["steps"][0]["name"], "refresh")
        self.assertEqual(result.data["bundles"][0]["steps"][0]["entry"], "refresh-env")

    def test_handle_catalog_list_filters_entries_by_label(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "entry", "--label", "report"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertGreater(len(result.data["entries"]), 0)
        self.assertTrue(all("report" in row["labels"] for row in result.data["entries"]))

    def test_handle_catalog_list_includes_block_watchlist_import_entry(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "entry", "--label", "import"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        entry_names = [row["name"] for row in result.data["entries"]]
        self.assertIn("plan-zxg-watchlist-import", entry_names)

    def test_handle_catalog_list_includes_block_sync_write_policy_entry(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "entry", "--label", "sync"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        entry_names = [row["name"] for row in result.data["entries"]]
        self.assertIn("plan-zxg-block-sync-merge", entry_names)

    def test_handle_catalog_list_returns_entry_label_discovery_metadata(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "entry", "--label", "report", "--view", "summary"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        discovery = result.data["discovery"]
        summary_view = result.data["summary_view"]
        self.assertEqual(discovery["selected_label"], "report")
        self.assertEqual(discovery["matched_entry_count"], result.data["summary"]["entry_count"])
        self.assertIn("report", discovery["available_entry_labels"])
        self.assertEqual(summary_view["available_entry_labels"], discovery["available_entry_labels"])
        self.assertEqual(
            summary_view["available_entry_label_count"],
            len(summary_view["available_entry_labels"]),
        )

    def test_handle_catalog_list_filters_bundles_by_label(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "bundle", "--label", "diagnostics"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertGreater(len(result.data["bundles"]), 0)
        self.assertTrue(all("diagnostics" in row["labels"] for row in result.data["bundles"]))

    def test_handle_catalog_list_returns_bundle_label_discovery_metadata(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "bundle", "--label", "diagnostics", "--view", "summary"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        discovery = result.data["discovery"]
        summary_view = result.data["summary_view"]
        self.assertEqual(discovery["selected_label"], "diagnostics")
        self.assertEqual(discovery["matched_bundle_count"], result.data["summary"]["bundle_count"])
        self.assertIn("diagnostics", discovery["available_bundle_labels"])
        self.assertEqual(summary_view["available_bundle_labels"], discovery["available_bundle_labels"])
        self.assertEqual(
            summary_view["available_bundle_label_count"],
            len(summary_view["available_bundle_labels"]),
        )

    def test_handle_catalog_bundle_list_includes_read_zxg_review(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "bundle"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        bundle_names = [row["name"] for row in result.data["bundles"]]
        self.assertIn("read-zxg-review", bundle_names)

    def test_handle_catalog_bundle_list_includes_read_zxg_review_and_export(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "bundle"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        bundle_names = [row["name"] for row in result.data["bundles"]]
        self.assertIn("read-zxg-review-and-export", bundle_names)

    def test_handle_catalog_list_exposes_task_report_combo_bundle(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "bundle", "--label", "followup"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        combo = next(
            row for row in result.data["bundles"] if row["name"] == "confirm-complete-review"
        )
        self.assertEqual(combo["step_count"], 3)
        self.assertEqual([step["source"] for step in combo["steps"]], ["task", "report", "report"])
        self.assertEqual(
            [step["entry"] for step in combo["steps"]],
            ["task-confirm-current", "daily-success", "audit-daily-confirmed"],
        )

    def test_handle_catalog_validate_all_resolves_registry_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "validate", "--kind", "all"])

        result = _handle_catalog_subcommand(args)

        self.assertTrue(result.ok)
        validation = result.data["validation"]
        self.assertEqual(validation["kind"], "all")
        self.assertEqual(validation["invalid_count"], 0)
        self.assertEqual(validation["valid"], True)
        self.assertGreater(validation["entry_count"], 0)
        self.assertGreater(validation["bundle_count"], 0)
        self.assertGreater(validation["task_report_bundle_count"], 0)
        self.assertGreater(validation["bundle_step_source_entry_counts"]["task:task-confirm-current"], 0)
        self.assertGreater(validation["bundle_step_source_entry_counts"]["report:daily-success"], 0)
        self.assertEqual(
            validation["bundle_step_count"],
            sum(validation["bundle_step_source_entry_counts"].values()),
        )
        self.assertGreater(validation["entry_source_counts"]["report"], 0)
        self.assertGreater(validation["entry_source_counts"]["task"], 0)
        self.assertGreater(validation["entry_source_counts"]["trade"], 0)
        self.assertGreater(validation["entry_label_counts"]["report"], 0)
        self.assertGreater(validation["entry_label_counts"]["task"], 0)
        self.assertEqual(validation["errors"], [])

    def test_handle_catalog_validate_entry_only_has_empty_bundle_source_entry_counts(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "validate", "--kind", "entry"])

        result = _handle_catalog_subcommand(args)

        self.assertTrue(result.ok)
        validation = result.data["validation"]
        self.assertEqual(validation["kind"], "entry")
        self.assertGreater(validation["entry_count"], 0)
        self.assertEqual(validation["bundle_count"], 0)
        self.assertEqual(validation["bundle_step_count"], 0)
        self.assertEqual(validation["bundle_step_source_entry_counts"], {})

    def test_handle_catalog_validate_followup_bundles_counts_task_report_combos(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "validate", "--kind", "bundle", "--label", "followup"])

        result = _handle_catalog_subcommand(args)

        self.assertTrue(result.ok)
        validation = result.data["validation"]
        self.assertEqual(validation["kind"], "bundle")
        self.assertEqual(validation["selected_label"], "followup")
        self.assertEqual(validation["entry_count"], 0)
        self.assertEqual(validation["entry_source_counts"], {})
        self.assertEqual(validation["entry_label_counts"], {})
        self.assertEqual(validation["invalid_count"], 0)
        self.assertEqual(validation["valid"], True)
        self.assertGreaterEqual(validation["bundle_count"], validation["task_report_bundle_count"])
        self.assertGreaterEqual(validation["bundle_step_count"], validation["task_report_bundle_step_count"])
        self.assertEqual(validation["bundle_label_counts"]["followup"], validation["bundle_count"])
        self.assertEqual(validation["bundle_step_count"], sum(validation["bundle_step_source_counts"].values()))
        self.assertEqual(validation["bundle_step_count"], sum(validation["bundle_step_name_counts"].values()))
        self.assertEqual(validation["bundle_step_count"], sum(validation["bundle_step_entry_counts"].values()))
        self.assertEqual(validation["bundle_step_count"], sum(validation["bundle_step_source_name_counts"].values()))
        self.assertEqual(validation["bundle_step_option_key_counts"]["limit"], 3)
        self.assertEqual(validation["bundle_step_source_option_key_counts"]["report:limit"], 3)
        self.assertEqual(
            sum(validation["bundle_step_source_option_key_counts"].values()),
            sum(validation["bundle_step_option_key_counts"].values()),
        )
        self.assertGreater(validation["bundle_step_source_counts"]["task"], 0)
        self.assertGreater(validation["bundle_step_source_counts"]["report"], 0)
        self.assertGreater(validation["bundle_step_name_counts"]["audit"], 0)
        self.assertGreater(validation["bundle_step_name_counts"]["trade"], 0)
        self.assertGreater(validation["bundle_step_entry_counts"]["daily-success"], 0)
        self.assertGreater(validation["bundle_step_entry_counts"]["guarded-buy"], 0)
        self.assertGreater(validation["bundle_step_source_name_counts"]["report:audit"], 0)
        self.assertGreater(validation["bundle_step_source_name_counts"]["task:trade"], 0)
        self.assertGreaterEqual(
            validation["bundle_label_counts"]["pingan"],
            validation["task_report_bundle_label_counts"]["pingan"],
        )
        self.assertGreater(validation["task_report_bundle_count"], 0)
        self.assertEqual(len(validation["task_report_bundle_samples"]), 5)
        self.assertEqual(validation["task_report_bundle_sample_limit"], 5)
        self.assertEqual(validation["task_report_bundle_sample_truncated"], True)
        self.assertLessEqual(
            len(validation["task_report_bundle_samples"]), validation["task_report_bundle_sample_limit"]
        )
        self.assertEqual(validation["task_report_bundle_samples"][0], "buy-pingan-complete-review")
        self.assertEqual(
            validation["task_report_bundle_step_count"],
            sum(validation["task_report_bundle_step_source_counts"].values()),
        )
        self.assertEqual(
            validation["task_report_bundle_step_count"],
            sum(validation["task_report_bundle_step_name_counts"].values()),
        )
        self.assertEqual(
            validation["task_report_bundle_step_count"],
            sum(validation["task_report_bundle_step_source_name_counts"].values()),
        )
        self.assertEqual(
            validation["task_report_bundle_step_count"],
            sum(validation["task_report_bundle_step_entry_counts"].values()),
        )
        self.assertEqual(validation["task_report_bundle_step_option_key_counts"]["limit"], 3)
        self.assertEqual(
            validation["task_report_bundle_step_source_option_key_counts"]["report:limit"],
            3,
        )
        self.assertEqual(
            sum(validation["task_report_bundle_step_source_option_key_counts"].values()),
            sum(validation["task_report_bundle_step_option_key_counts"].values()),
        )
        self.assertGreater(validation["task_report_bundle_step_count"], validation["task_report_bundle_count"])
        self.assertGreater(validation["task_report_bundle_step_source_counts"]["task"], 0)
        self.assertGreater(validation["task_report_bundle_step_source_counts"]["report"], 0)
        self.assertNotIn("trade", validation["task_report_bundle_step_source_counts"])
        self.assertGreater(validation["task_report_bundle_step_name_counts"]["audit"], 0)
        self.assertGreater(validation["task_report_bundle_step_name_counts"]["trade"], 0)
        self.assertGreater(validation["task_report_bundle_step_source_name_counts"]["report:audit"], 0)
        self.assertGreater(validation["task_report_bundle_step_source_name_counts"]["task:trade"], 0)
        self.assertGreater(
            validation["task_report_bundle_step_source_entry_counts"]["task:task-confirm-current"],
            0,
        )
        self.assertGreater(
            validation["task_report_bundle_step_source_entry_counts"]["report:daily-success"],
            0,
        )
        self.assertEqual(
            validation["task_report_bundle_step_count"],
            sum(validation["task_report_bundle_step_source_entry_counts"].values()),
        )
        self.assertGreater(validation["task_report_bundle_step_entry_counts"]["daily-success"], 0)
        self.assertGreater(validation["task_report_bundle_step_entry_counts"]["guarded-buy"], 0)
        self.assertEqual(
            validation["task_report_bundle_label_counts"]["followup"],
            validation["task_report_bundle_count"],
        )
        self.assertGreater(validation["task_report_bundle_label_counts"]["pingan"], 0)
        self.assertEqual(validation["submit_once_bundle_step_option_key_counts"]["limit"], 1)
        self.assertEqual(
            validation["submit_once_bundle_step_source_option_key_counts"]["report:limit"],
            1,
        )
        self.assertEqual(
            validation["submit_once_bundle_step_count"],
            sum(validation["submit_once_bundle_step_source_counts"].values()),
        )
        self.assertEqual(
            validation["submit_once_bundle_step_count"],
            sum(validation["submit_once_bundle_step_source_entry_counts"].values()),
        )
        self.assertGreater(
            validation["submit_once_bundle_step_source_entry_counts"]["report:recent-ledger"],
            0,
        )
        self.assertGreater(validation["submit_once_bundle_step_count"], validation["submit_once_bundle_count"])
        self.assertEqual(
            sum(validation["submit_once_bundle_step_source_option_key_counts"].values()),
            sum(validation["submit_once_bundle_step_option_key_counts"].values()),
        )
        self.assertEqual(
            validation["pingan_bundle_step_count"],
            sum(validation["pingan_bundle_step_source_counts"].values()),
        )
        self.assertEqual(
            validation["pingan_bundle_step_count"],
            sum(validation["pingan_bundle_step_source_entry_counts"].values()),
        )
        self.assertGreater(
            validation["pingan_bundle_step_source_entry_counts"]["task:task-confirm-current"],
            0,
        )
        self.assertGreater(validation["pingan_bundle_step_count"], validation["pingan_bundle_count"])
        self.assertEqual(validation["pingan_bundle_step_option_key_counts"], {})
        self.assertEqual(validation["pingan_bundle_step_source_option_key_counts"], {})

    def test_handle_catalog_validate_summary_view_projects_counts_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["catalog", "validate", "--kind", "bundle", "--label", "followup", "--view", "summary"]
        )

        result = _handle_catalog_subcommand(args)

        self.assertTrue(result.ok)
        validation = result.data["validation"]
        summary_view = result.data["summary_view"]
        self.assertEqual(summary_view["mode"], "validate")
        self.assertEqual(summary_view["kind"], "bundle")
        self.assertEqual(summary_view["selected_label"], "followup")
        self.assertEqual(summary_view["entry_count"], 0)
        self.assertEqual(summary_view["entry_source_counts"], validation["entry_source_counts"])
        self.assertEqual(summary_view["entry_source_key_count"], len(summary_view["entry_source_counts"]))
        self.assertEqual(summary_view["entry_source_counts"], {})
        self.assertEqual(summary_view["entry_label_counts"], validation["entry_label_counts"])
        self.assertEqual(summary_view["entry_label_key_count"], len(summary_view["entry_label_counts"]))
        self.assertEqual(summary_view["entry_label_counts"], {})
        self.assertEqual(
            summary_view["entry_summary"],
            {
                "count": 0,
                "source_key_count": 0,
                "label_key_count": 0,
            },
        )
        self.assertEqual(summary_view["bundle_count"], validation["bundle_count"])
        self.assertEqual(summary_view["bundle_step_count"], validation["bundle_step_count"])
        self.assertEqual(summary_view["bundle_step_source_counts"], validation["bundle_step_source_counts"])
        self.assertEqual(
            summary_view["bundle_step_source_key_count"],
            len(summary_view["bundle_step_source_counts"]),
        )
        self.assertEqual(summary_view["bundle_step_count"], sum(summary_view["bundle_step_source_counts"].values()))
        self.assertEqual(summary_view["bundle_step_name_counts"], validation["bundle_step_name_counts"])
        self.assertEqual(summary_view["bundle_step_name_key_count"], len(summary_view["bundle_step_name_counts"]))
        self.assertEqual(summary_view["bundle_step_count"], sum(summary_view["bundle_step_name_counts"].values()))
        self.assertEqual(summary_view["bundle_step_entry_counts"], validation["bundle_step_entry_counts"])
        self.assertEqual(summary_view["bundle_step_entry_key_count"], len(summary_view["bundle_step_entry_counts"]))
        self.assertEqual(summary_view["bundle_step_count"], sum(summary_view["bundle_step_entry_counts"].values()))
        self.assertEqual(
            summary_view["bundle_step_option_key_counts"], validation["bundle_step_option_key_counts"]
        )
        self.assertEqual(
            summary_view["bundle_step_option_key_count"],
            len(summary_view["bundle_step_option_key_counts"]),
        )
        self.assertEqual(summary_view["bundle_step_option_key_counts"]["limit"], 3)
        self.assertEqual(
            summary_view["bundle_step_source_option_key_counts"],
            validation["bundle_step_source_option_key_counts"],
        )
        self.assertEqual(
            summary_view["bundle_step_source_option_key_count"],
            len(summary_view["bundle_step_source_option_key_counts"]),
        )
        self.assertEqual(summary_view["bundle_step_source_option_key_counts"]["report:limit"], 3)
        self.assertEqual(
            sum(summary_view["bundle_step_source_option_key_counts"].values()),
            sum(summary_view["bundle_step_option_key_counts"].values()),
        )
        self.assertEqual(summary_view["bundle_step_source_name_counts"], validation["bundle_step_source_name_counts"])
        self.assertEqual(
            summary_view["bundle_step_source_name_key_count"],
            len(summary_view["bundle_step_source_name_counts"]),
        )
        self.assertEqual(summary_view["bundle_step_count"], sum(summary_view["bundle_step_source_name_counts"].values()))
        self.assertEqual(
            summary_view["bundle_step_source_entry_counts"],
            validation["bundle_step_source_entry_counts"],
        )
        self.assertEqual(
            summary_view["bundle_step_source_entry_key_count"],
            len(summary_view["bundle_step_source_entry_counts"]),
        )
        self.assertEqual(
            summary_view["bundle_step_count"],
            sum(summary_view["bundle_step_source_entry_counts"].values()),
        )
        self.assertEqual(summary_view["bundle_label_counts"], validation["bundle_label_counts"])
        self.assertEqual(summary_view["bundle_label_key_count"], len(summary_view["bundle_label_counts"]))
        self.assertEqual(summary_view["bundle_label_counts"]["followup"], summary_view["bundle_count"])
        label_keys = set(summary_view["entry_label_counts"]) | set(summary_view["bundle_label_counts"])
        self.assertEqual(
            summary_view["label_summary"],
            {
                "selected_label": "followup",
                "entry_key_count": summary_view["entry_label_key_count"],
                "bundle_key_count": summary_view["bundle_label_key_count"],
                "total_key_count": len(label_keys),
                "selected_entry_count": 0,
                "selected_bundle_count": summary_view["bundle_label_counts"]["followup"],
                "selected_total_count": summary_view["bundle_label_counts"]["followup"],
                "has_selected_label": True,
            },
        )
        source_keys = set(summary_view["entry_source_counts"]) | set(
            summary_view["bundle_step_source_counts"]
        )
        self.assertEqual(
            summary_view["source_summary"],
            {
                "entry_key_count": summary_view["entry_source_key_count"],
                "bundle_step_key_count": summary_view["bundle_step_source_key_count"],
                "total_key_count": len(source_keys),
                "entry_count": summary_view["entry_count"],
                "bundle_step_count": summary_view["bundle_step_count"],
                "has_entry_sources": False,
                "has_bundle_step_sources": True,
            },
        )
        self.assertIn("bundle_samples", summary_view)
        self.assertEqual(summary_view["bundle_samples"], validation["bundle_samples"])
        self.assertEqual(summary_view["bundle_sample_count"], len(summary_view["bundle_samples"]))
        self.assertEqual(summary_view["bundle_sample_limit"], validation["bundle_sample_limit"])
        self.assertEqual(
            summary_view["bundle_sample_truncated"],
            validation["bundle_sample_truncated"],
        )
        self.assertEqual(summary_view["bundle_sample_truncated"], True)
        self.assertEqual(
            summary_view["bundle_summary"],
            {
                "selected_bundle": None,
                "selected_label": "followup",
                "count": summary_view["bundle_count"],
                "step_count": summary_view["bundle_step_count"],
                "sample_count": summary_view["bundle_sample_count"],
                "sample_limit": summary_view["bundle_sample_limit"],
                "sample_truncated": summary_view["bundle_sample_truncated"],
                "label_key_count": summary_view["bundle_label_key_count"],
                "has_bundles": True,
                "has_selected_bundle": False,
            },
        )
        self.assertEqual(
            summary_view["catalog_summary"],
            {
                "mode": "validate",
                "kind": "bundle",
                "selected_entry": None,
                "selected_bundle": None,
                "selected_label": "followup",
                "valid": summary_view["valid"],
                "invalid_count": summary_view["invalid_count"],
                "non_execution": summary_view["non_execution"],
                "entry_count": summary_view["entry_count"],
                "bundle_count": summary_view["bundle_count"],
                "bundle_step_count": summary_view["bundle_step_count"],
                "label_key_count": summary_view["label_summary"]["total_key_count"],
                "source_key_count": summary_view["source_summary"]["total_key_count"],
                "has_entries": False,
                "has_bundles": True,
                "has_invalid_entries": False,
                "has_selected_label": True,
            },
        )
        self.assertEqual(
            summary_view["bundle_step_summary"],
            {
                "bundle_count": summary_view["bundle_count"],
                "step_count": summary_view["bundle_step_count"],
                "sample_count": summary_view["bundle_sample_count"],
                "sample_limit": summary_view["bundle_sample_limit"],
                "sample_truncated": summary_view["bundle_sample_truncated"],
                "label_key_count": summary_view["bundle_label_key_count"],
                "step_source_key_count": summary_view["bundle_step_source_key_count"],
                "step_name_key_count": summary_view["bundle_step_name_key_count"],
                "step_entry_key_count": summary_view["bundle_step_entry_key_count"],
                "step_source_name_key_count": summary_view["bundle_step_source_name_key_count"],
                "step_source_entry_key_count": summary_view["bundle_step_source_entry_key_count"],
                "step_option_key_count": summary_view["bundle_step_option_key_count"],
                "step_source_option_key_count": summary_view["bundle_step_source_option_key_count"],
            },
        )
        self.assertEqual(summary_view["task_report_bundle_count"], validation["task_report_bundle_count"])
        self.assertEqual(summary_view["task_report_bundle_step_count"], validation["task_report_bundle_step_count"])
        self.assertEqual(summary_view["task_report_bundle_samples"], validation["task_report_bundle_samples"])
        self.assertEqual(
            summary_view["task_report_bundle_sample_count"],
            len(summary_view["task_report_bundle_samples"]),
        )
        self.assertEqual(
            summary_view["task_report_bundle_sample_limit"], validation["task_report_bundle_sample_limit"]
        )
        self.assertEqual(
            summary_view["task_report_bundle_sample_truncated"],
            validation["task_report_bundle_sample_truncated"],
        )
        self.assertEqual(summary_view["task_report_bundle_sample_truncated"], True)
        self.assertEqual(summary_view["task_report_bundle_samples"][0], "buy-pingan-complete-review")
        self.assertEqual(
            summary_view["task_report_bundle_summary"],
            {
                "count": summary_view["task_report_bundle_count"],
                "step_count": summary_view["task_report_bundle_step_count"],
                "sample_count": summary_view["task_report_bundle_sample_count"],
                "sample_limit": summary_view["task_report_bundle_sample_limit"],
                "sample_truncated": summary_view["task_report_bundle_sample_truncated"],
                "label_key_count": summary_view["task_report_bundle_label_key_count"],
                "step_source_key_count": summary_view["task_report_bundle_step_source_key_count"],
                "step_name_key_count": summary_view["task_report_bundle_step_name_key_count"],
                "step_source_name_key_count": summary_view["task_report_bundle_step_source_name_key_count"],
                "step_entry_key_count": summary_view["task_report_bundle_step_entry_key_count"],
                "step_source_entry_key_count": summary_view["task_report_bundle_step_source_entry_key_count"],
                "step_option_key_count": summary_view["task_report_bundle_step_option_key_count"],
                "step_source_option_key_count": summary_view[
                    "task_report_bundle_step_source_option_key_count"
                ],
            },
        )
        self.assertEqual(
            summary_view["task_report_bundle_step_source_counts"],
            validation["task_report_bundle_step_source_counts"],
        )
        self.assertEqual(
            summary_view["task_report_bundle_step_source_key_count"],
            len(summary_view["task_report_bundle_step_source_counts"]),
        )
        self.assertGreater(summary_view["task_report_bundle_step_source_counts"]["task"], 0)
        self.assertGreater(summary_view["task_report_bundle_step_source_counts"]["report"], 0)
        self.assertEqual(
            summary_view["task_report_bundle_step_count"],
            sum(summary_view["task_report_bundle_step_source_counts"].values()),
        )
        self.assertEqual(
            summary_view["task_report_bundle_step_name_counts"],
            validation["task_report_bundle_step_name_counts"],
        )
        self.assertEqual(
            summary_view["task_report_bundle_step_name_key_count"],
            len(summary_view["task_report_bundle_step_name_counts"]),
        )
        self.assertEqual(
            summary_view["task_report_bundle_step_count"],
            sum(summary_view["task_report_bundle_step_name_counts"].values()),
        )
        self.assertEqual(
            summary_view["task_report_bundle_step_source_name_counts"],
            validation["task_report_bundle_step_source_name_counts"],
        )
        self.assertEqual(
            summary_view["task_report_bundle_step_source_name_key_count"],
            len(summary_view["task_report_bundle_step_source_name_counts"]),
        )
        self.assertEqual(
            summary_view["task_report_bundle_step_count"],
            sum(summary_view["task_report_bundle_step_source_name_counts"].values()),
        )
        self.assertEqual(
            summary_view["task_report_bundle_step_source_entry_counts"],
            validation["task_report_bundle_step_source_entry_counts"],
        )
        self.assertEqual(
            summary_view["task_report_bundle_step_source_entry_key_count"],
            len(summary_view["task_report_bundle_step_source_entry_counts"]),
        )
        self.assertEqual(
            summary_view["task_report_bundle_step_count"],
            sum(summary_view["task_report_bundle_step_source_entry_counts"].values()),
        )
        self.assertEqual(
            summary_view["task_report_bundle_step_entry_counts"],
            validation["task_report_bundle_step_entry_counts"],
        )
        self.assertEqual(
            summary_view["task_report_bundle_step_entry_key_count"],
            len(summary_view["task_report_bundle_step_entry_counts"]),
        )
        self.assertEqual(
            summary_view["task_report_bundle_step_count"],
            sum(summary_view["task_report_bundle_step_entry_counts"].values()),
        )
        self.assertEqual(
            summary_view["task_report_bundle_step_option_key_counts"],
            validation["task_report_bundle_step_option_key_counts"],
        )
        self.assertEqual(
            summary_view["task_report_bundle_step_option_key_count"],
            len(summary_view["task_report_bundle_step_option_key_counts"]),
        )
        self.assertEqual(summary_view["task_report_bundle_step_option_key_counts"]["limit"], 3)
        self.assertEqual(
            summary_view["task_report_bundle_step_source_option_key_counts"],
            validation["task_report_bundle_step_source_option_key_counts"],
        )
        self.assertEqual(
            summary_view["task_report_bundle_step_source_option_key_count"],
            len(summary_view["task_report_bundle_step_source_option_key_counts"]),
        )
        self.assertEqual(
            summary_view["task_report_bundle_step_source_option_key_counts"]["report:limit"],
            3,
        )
        self.assertEqual(
            sum(summary_view["task_report_bundle_step_source_option_key_counts"].values()),
            sum(summary_view["task_report_bundle_step_option_key_counts"].values()),
        )
        self.assertEqual(
            summary_view["task_report_bundle_label_counts"],
            validation["task_report_bundle_label_counts"],
        )
        self.assertEqual(
            summary_view["task_report_bundle_label_key_count"],
            len(summary_view["task_report_bundle_label_counts"]),
        )
        self.assertEqual(
            summary_view["task_report_bundle_label_counts"]["followup"],
            summary_view["task_report_bundle_count"],
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_count"],
            validation["submit_once_bundle_step_count"],
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_count"],
            sum(summary_view["submit_once_bundle_step_source_counts"].values()),
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_source_entry_counts"],
            validation["submit_once_bundle_step_source_entry_counts"],
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_source_entry_key_count"],
            len(summary_view["submit_once_bundle_step_source_entry_counts"]),
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_count"],
            sum(summary_view["submit_once_bundle_step_source_entry_counts"].values()),
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_option_key_counts"],
            validation["submit_once_bundle_step_option_key_counts"],
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_option_key_count"],
            len(summary_view["submit_once_bundle_step_option_key_counts"]),
        )
        self.assertEqual(summary_view["submit_once_bundle_step_option_key_counts"]["limit"], 1)
        self.assertEqual(
            summary_view["submit_once_bundle_step_source_option_key_counts"],
            validation["submit_once_bundle_step_source_option_key_counts"],
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_source_option_key_count"],
            len(summary_view["submit_once_bundle_step_source_option_key_counts"]),
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_source_option_key_counts"]["report:limit"],
            1,
        )
        self.assertEqual(
            sum(summary_view["submit_once_bundle_step_source_option_key_counts"].values()),
            sum(summary_view["submit_once_bundle_step_option_key_counts"].values()),
        )
        self.assertEqual(
            summary_view["pingan_bundle_step_option_key_counts"],
            validation["pingan_bundle_step_option_key_counts"],
        )
        self.assertEqual(
            summary_view["pingan_bundle_step_option_key_count"],
            len(summary_view["pingan_bundle_step_option_key_counts"]),
        )
        self.assertEqual(
            summary_view["pingan_bundle_step_count"],
            validation["pingan_bundle_step_count"],
        )
        self.assertEqual(
            summary_view["pingan_bundle_step_count"],
            sum(summary_view["pingan_bundle_step_source_counts"].values()),
        )
        self.assertEqual(
            summary_view["pingan_bundle_step_source_entry_counts"],
            validation["pingan_bundle_step_source_entry_counts"],
        )
        self.assertEqual(
            summary_view["pingan_bundle_step_source_entry_key_count"],
            len(summary_view["pingan_bundle_step_source_entry_counts"]),
        )
        self.assertEqual(
            summary_view["pingan_bundle_step_count"],
            sum(summary_view["pingan_bundle_step_source_entry_counts"].values()),
        )
        self.assertEqual(summary_view["pingan_bundle_step_option_key_counts"], {})
        self.assertEqual(
            summary_view["pingan_bundle_step_source_option_key_counts"],
            validation["pingan_bundle_step_source_option_key_counts"],
        )
        self.assertEqual(
            summary_view["pingan_bundle_step_source_option_key_count"],
            len(summary_view["pingan_bundle_step_source_option_key_counts"]),
        )
        self.assertEqual(summary_view["pingan_bundle_step_source_option_key_counts"], {})
        self.assertEqual(summary_view["invalid_count"], 0)
        self.assertEqual(summary_view["valid"], True)
        self.assertEqual(summary_view["non_execution"], True)
        self.assertEqual(
            summary_view["validation_outcome"],
            {
                "kind": "bundle",
                "selected_label": "followup",
                "entry_count": 0,
                "bundle_count": summary_view["bundle_count"],
                "invalid_count": 0,
                "valid": True,
                "non_execution": True,
                "ok": True,
                "code": summary_view["code"],
                "message": summary_view["message"],
                "has_invalid_entries": False,
                "has_selected_label": True,
            },
        )
        self.assertNotIn("entries", summary_view)
        self.assertNotIn("bundles", summary_view)

    def test_handle_catalog_validate_entry_summary_view_projects_entry_label_counts(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["catalog", "validate", "--kind", "entry", "--label", "report", "--view", "summary"]
        )

        result = _handle_catalog_subcommand(args)

        self.assertTrue(result.ok)
        validation = result.data["validation"]
        summary_view = result.data["summary_view"]
        self.assertGreater(validation["entry_count"], 0)
        self.assertEqual(validation["bundle_count"], 0)
        self.assertEqual(validation["entry_source_counts"]["report"], validation["entry_count"])
        self.assertEqual(summary_view["entry_source_counts"], validation["entry_source_counts"])
        self.assertEqual(summary_view["entry_source_key_count"], len(summary_view["entry_source_counts"]))
        self.assertEqual(summary_view["entry_source_counts"]["report"], summary_view["entry_count"])
        self.assertEqual(validation["entry_label_counts"]["report"], validation["entry_count"])
        self.assertEqual(summary_view["entry_label_counts"], validation["entry_label_counts"])
        self.assertEqual(summary_view["entry_label_key_count"], len(summary_view["entry_label_counts"]))
        self.assertEqual(summary_view["entry_label_counts"]["report"], summary_view["entry_count"])
        self.assertEqual(
            summary_view["entry_summary"],
            {
                "count": summary_view["entry_count"],
                "source_key_count": summary_view["entry_source_key_count"],
                "label_key_count": summary_view["entry_label_key_count"],
            },
        )
        source_keys = set(summary_view["entry_source_counts"]) | set(
            summary_view["bundle_step_source_counts"]
        )
        self.assertEqual(
            summary_view["source_summary"],
            {
                "entry_key_count": summary_view["entry_source_key_count"],
                "bundle_step_key_count": summary_view["bundle_step_source_key_count"],
                "total_key_count": len(source_keys),
                "entry_count": summary_view["entry_count"],
                "bundle_step_count": summary_view["bundle_step_count"],
                "has_entry_sources": True,
                "has_bundle_step_sources": False,
            },
        )
        self.assertEqual(validation["bundle_step_source_option_key_counts"], {})
        self.assertEqual(summary_view["bundle_step_source_option_key_counts"], {})
        self.assertEqual(validation["task_report_bundle_step_source_option_key_counts"], {})
        self.assertEqual(summary_view["task_report_bundle_step_source_option_key_counts"], {})
        self.assertEqual(validation["submit_once_bundle_step_option_key_counts"], {})
        self.assertEqual(summary_view["submit_once_bundle_step_option_key_counts"], {})
        self.assertEqual(validation["pingan_bundle_step_option_key_counts"], {})
        self.assertEqual(summary_view["pingan_bundle_step_option_key_counts"], {})
        self.assertEqual(validation["submit_once_bundle_step_source_option_key_counts"], {})
        self.assertEqual(summary_view["submit_once_bundle_step_source_option_key_counts"], {})
        self.assertEqual(validation["pingan_bundle_step_source_option_key_counts"], {})
        self.assertEqual(summary_view["pingan_bundle_step_source_option_key_counts"], {})
        self.assertEqual(validation["submit_once_bundle_step_count"], 0)
        self.assertEqual(summary_view["submit_once_bundle_step_count"], 0)
        self.assertEqual(validation["pingan_bundle_step_count"], 0)
        self.assertEqual(summary_view["pingan_bundle_step_count"], 0)
        self.assertEqual(validation["submit_once_bundle_step_source_entry_counts"], {})
        self.assertEqual(summary_view["submit_once_bundle_step_source_entry_counts"], {})
        self.assertEqual(validation["pingan_bundle_step_source_entry_counts"], {})
        self.assertEqual(summary_view["pingan_bundle_step_source_entry_counts"], {})
        self.assertEqual(summary_view["bundle_label_counts"], {})
        self.assertEqual(summary_view["bundle_samples"], [])
        self.assertEqual(summary_view["bundle_sample_count"], 0)
        self.assertFalse(summary_view["bundle_sample_truncated"])
        self.assertEqual(
            summary_view["bundle_step_summary"],
            {
                "bundle_count": 0,
                "step_count": 0,
                "sample_count": summary_view["bundle_sample_count"],
                "sample_limit": summary_view["bundle_sample_limit"],
                "sample_truncated": summary_view["bundle_sample_truncated"],
                "label_key_count": 0,
                "step_source_key_count": 0,
                "step_name_key_count": 0,
                "step_entry_key_count": 0,
                "step_source_name_key_count": 0,
                "step_source_entry_key_count": 0,
                "step_option_key_count": 0,
                "step_source_option_key_count": 0,
            },
        )
        self.assertEqual(summary_view["non_execution"], True)
        self.assertNotIn("entries", summary_view)
        self.assertNotIn("bundles", summary_view)

    def test_handle_catalog_validate_diagnostics_label_has_zero_task_report_step_count(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["catalog", "validate", "--kind", "bundle", "--label", "diagnostics", "--view", "summary"]
        )

        result = _handle_catalog_subcommand(args)

        self.assertTrue(result.ok)
        validation = result.data["validation"]
        summary_view = result.data["summary_view"]
        self.assertGreater(validation["bundle_count"], 0)
        self.assertGreater(validation["bundle_step_count"], 0)
        self.assertEqual(validation["bundle_step_count"], sum(validation["bundle_step_source_counts"].values()))
        self.assertEqual(validation["bundle_label_counts"]["diagnostics"], validation["bundle_count"])
        self.assertEqual(validation["task_report_bundle_count"], 0)
        self.assertEqual(validation["task_report_bundle_step_count"], 0)
        self.assertEqual(validation["task_report_bundle_step_source_counts"], {})
        self.assertEqual(validation["task_report_bundle_step_source_name_counts"], {})
        self.assertEqual(validation["task_report_bundle_step_source_entry_counts"], {})
        self.assertEqual(validation["task_report_bundle_step_entry_counts"], {})
        self.assertEqual(validation["task_report_bundle_label_counts"], {})
        self.assertEqual(
            summary_view["task_report_bundle_summary"],
            {
                "count": 0,
                "step_count": 0,
                "sample_count": 0,
                "sample_limit": validation["task_report_bundle_sample_limit"],
                "sample_truncated": False,
                "label_key_count": 0,
                "step_source_key_count": 0,
                "step_name_key_count": 0,
                "step_source_name_key_count": 0,
                "step_entry_key_count": 0,
                "step_source_entry_key_count": 0,
                "step_option_key_count": 0,
                "step_source_option_key_count": 0,
            },
        )

    def test_handle_catalog_validate_summary_view_projects_submit_once_samples(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["catalog", "validate", "--kind", "bundle", "--label", "submit-once", "--view", "summary"]
        )

        result = _handle_catalog_subcommand(args)

        self.assertTrue(result.ok)
        validation = result.data["validation"]
        summary_view = result.data["summary_view"]
        self.assertEqual(summary_view["selected_label"], "submit-once")
        self.assertEqual(summary_view["submit_once_bundle_count"], validation["submit_once_bundle_count"])
        self.assertGreater(summary_view["submit_once_bundle_count"], 0)
        self.assertEqual(
            summary_view["submit_once_bundle_step_count"],
            validation["submit_once_bundle_step_count"],
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_count"],
            sum(summary_view["submit_once_bundle_step_source_counts"].values()),
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_source_entry_counts"],
            validation["submit_once_bundle_step_source_entry_counts"],
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_source_entry_key_count"],
            len(summary_view["submit_once_bundle_step_source_entry_counts"]),
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_count"],
            sum(summary_view["submit_once_bundle_step_source_entry_counts"].values()),
        )
        self.assertGreater(
            validation["submit_once_bundle_step_source_entry_counts"]["report:recent-failures"],
            0,
        )
        self.assertGreater(
            summary_view["submit_once_bundle_step_count"],
            summary_view["submit_once_bundle_count"],
        )
        self.assertEqual(
            summary_view["submit_once_bundle_label_counts"],
            validation["submit_once_bundle_label_counts"],
        )
        self.assertEqual(
            summary_view["submit_once_bundle_label_key_count"],
            len(summary_view["submit_once_bundle_label_counts"]),
        )
        self.assertGreater(validation["submit_once_bundle_label_counts"]["submit-once"], 0)
        self.assertEqual(
            summary_view["submit_once_bundle_step_source_counts"],
            validation["submit_once_bundle_step_source_counts"],
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_source_key_count"],
            len(summary_view["submit_once_bundle_step_source_counts"]),
        )
        self.assertGreater(validation["submit_once_bundle_step_source_counts"]["report"], 0)
        self.assertEqual(
            summary_view["submit_once_bundle_step_name_counts"],
            validation["submit_once_bundle_step_name_counts"],
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_name_key_count"],
            len(summary_view["submit_once_bundle_step_name_counts"]),
        )
        self.assertGreater(validation["submit_once_bundle_step_name_counts"]["audit"], 0)
        self.assertGreater(validation["submit_once_bundle_step_name_counts"]["failures"], 0)
        self.assertEqual(
            summary_view["submit_once_bundle_step_source_name_counts"],
            validation["submit_once_bundle_step_source_name_counts"],
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_source_name_key_count"],
            len(summary_view["submit_once_bundle_step_source_name_counts"]),
        )
        self.assertGreater(validation["submit_once_bundle_step_source_name_counts"]["report:audit"], 0)
        self.assertGreater(validation["submit_once_bundle_step_source_name_counts"]["report:failures"], 0)
        self.assertEqual(
            summary_view["submit_once_bundle_step_entry_counts"],
            validation["submit_once_bundle_step_entry_counts"],
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_entry_key_count"],
            len(summary_view["submit_once_bundle_step_entry_counts"]),
        )
        self.assertGreater(validation["submit_once_bundle_step_entry_counts"]["recent-failures"], 0)
        self.assertGreater(
            validation["submit_once_bundle_step_entry_counts"]["audit-daily-pingan-submit-once-exceptions"],
            0,
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_option_key_counts"],
            validation["submit_once_bundle_step_option_key_counts"],
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_option_key_count"],
            len(summary_view["submit_once_bundle_step_option_key_counts"]),
        )
        self.assertEqual(validation["submit_once_bundle_step_option_key_counts"], {})
        self.assertEqual(
            summary_view["submit_once_bundle_step_source_option_key_counts"],
            validation["submit_once_bundle_step_source_option_key_counts"],
        )
        self.assertEqual(
            summary_view["submit_once_bundle_step_source_option_key_count"],
            len(summary_view["submit_once_bundle_step_source_option_key_counts"]),
        )
        self.assertEqual(validation["submit_once_bundle_step_source_option_key_counts"], {})
        self.assertEqual(summary_view["submit_once_bundle_samples"], validation["submit_once_bundle_samples"])
        self.assertEqual(
            summary_view["submit_once_bundle_sample_count"],
            len(summary_view["submit_once_bundle_samples"]),
        )
        self.assertEqual(
            summary_view["submit_once_bundle_sample_limit"],
            validation["submit_once_bundle_sample_limit"],
        )
        self.assertEqual(
            summary_view["submit_once_bundle_sample_truncated"],
            validation["submit_once_bundle_sample_truncated"],
        )
        self.assertEqual(summary_view["submit_once_bundle_sample_truncated"], True)
        self.assertEqual(
            summary_view["submit_once_bundle_samples"][0],
            "audit-pingan-submit-once-exception-diagnostics",
        )
        self.assertEqual(
            summary_view["submit_once_bundle_summary"],
            {
                "count": summary_view["submit_once_bundle_count"],
                "step_count": summary_view["submit_once_bundle_step_count"],
                "sample_count": summary_view["submit_once_bundle_sample_count"],
                "sample_limit": summary_view["submit_once_bundle_sample_limit"],
                "sample_truncated": summary_view["submit_once_bundle_sample_truncated"],
                "label_key_count": summary_view["submit_once_bundle_label_key_count"],
                "step_source_key_count": summary_view["submit_once_bundle_step_source_key_count"],
                "step_name_key_count": summary_view["submit_once_bundle_step_name_key_count"],
                "step_source_name_key_count": summary_view["submit_once_bundle_step_source_name_key_count"],
                "step_entry_key_count": summary_view["submit_once_bundle_step_entry_key_count"],
                "step_source_entry_key_count": summary_view["submit_once_bundle_step_source_entry_key_count"],
                "step_option_key_count": summary_view["submit_once_bundle_step_option_key_count"],
                "step_source_option_key_count": summary_view[
                    "submit_once_bundle_step_source_option_key_count"
                ],
            },
        )
        self.assertEqual(summary_view["non_execution"], True)
        self.assertNotIn("entries", summary_view)
        self.assertNotIn("bundles", summary_view)

    def test_handle_catalog_validate_summary_view_projects_pingan_samples(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["catalog", "validate", "--kind", "bundle", "--label", "pingan", "--view", "summary"]
        )

        result = _handle_catalog_subcommand(args)

        self.assertTrue(result.ok)
        validation = result.data["validation"]
        summary_view = result.data["summary_view"]
        self.assertEqual(summary_view["selected_label"], "pingan")
        self.assertEqual(summary_view["pingan_bundle_count"], validation["pingan_bundle_count"])
        self.assertGreater(summary_view["pingan_bundle_count"], 0)
        self.assertEqual(summary_view["pingan_bundle_step_count"], validation["pingan_bundle_step_count"])
        self.assertEqual(
            summary_view["pingan_bundle_step_count"],
            sum(summary_view["pingan_bundle_step_source_counts"].values()),
        )
        self.assertEqual(
            summary_view["pingan_bundle_step_source_entry_counts"],
            validation["pingan_bundle_step_source_entry_counts"],
        )
        self.assertEqual(
            summary_view["pingan_bundle_step_source_entry_key_count"],
            len(summary_view["pingan_bundle_step_source_entry_counts"]),
        )
        self.assertEqual(
            summary_view["pingan_bundle_step_count"],
            sum(summary_view["pingan_bundle_step_source_entry_counts"].values()),
        )
        self.assertGreater(
            validation["pingan_bundle_step_source_entry_counts"]["task:task-confirm-current"],
            0,
        )
        self.assertGreater(summary_view["pingan_bundle_step_count"], summary_view["pingan_bundle_count"])
        self.assertEqual(summary_view["pingan_bundle_label_counts"], validation["pingan_bundle_label_counts"])
        self.assertEqual(
            summary_view["pingan_bundle_label_key_count"],
            len(summary_view["pingan_bundle_label_counts"]),
        )
        self.assertEqual(validation["pingan_bundle_label_counts"]["pingan"], validation["pingan_bundle_count"])
        self.assertEqual(
            summary_view["pingan_bundle_step_source_counts"],
            validation["pingan_bundle_step_source_counts"],
        )
        self.assertEqual(
            summary_view["pingan_bundle_step_source_key_count"],
            len(summary_view["pingan_bundle_step_source_counts"]),
        )
        self.assertGreater(validation["pingan_bundle_step_source_counts"]["task"], 0)
        self.assertGreater(validation["pingan_bundle_step_source_counts"]["report"], 0)
        self.assertEqual(
            summary_view["pingan_bundle_step_name_counts"],
            validation["pingan_bundle_step_name_counts"],
        )
        self.assertEqual(
            summary_view["pingan_bundle_step_name_key_count"],
            len(summary_view["pingan_bundle_step_name_counts"]),
        )
        self.assertGreater(validation["pingan_bundle_step_name_counts"]["audit"], 0)
        self.assertGreater(validation["pingan_bundle_step_name_counts"]["trade"], 0)
        self.assertEqual(
            summary_view["pingan_bundle_step_source_name_counts"],
            validation["pingan_bundle_step_source_name_counts"],
        )
        self.assertEqual(
            summary_view["pingan_bundle_step_source_name_key_count"],
            len(summary_view["pingan_bundle_step_source_name_counts"]),
        )
        self.assertGreater(validation["pingan_bundle_step_source_name_counts"]["report:audit"], 0)
        self.assertGreater(validation["pingan_bundle_step_source_name_counts"]["task:trade"], 0)
        self.assertEqual(
            summary_view["pingan_bundle_step_entry_counts"],
            validation["pingan_bundle_step_entry_counts"],
        )
        self.assertEqual(
            summary_view["pingan_bundle_step_entry_key_count"],
            len(summary_view["pingan_bundle_step_entry_counts"]),
        )
        self.assertGreater(validation["pingan_bundle_step_entry_counts"]["recent-failures"], 0)
        self.assertGreater(validation["pingan_bundle_step_entry_counts"]["task-confirm-current"], 0)
        self.assertEqual(
            summary_view["pingan_bundle_step_option_key_counts"],
            validation["pingan_bundle_step_option_key_counts"],
        )
        self.assertEqual(
            summary_view["pingan_bundle_step_option_key_count"],
            len(summary_view["pingan_bundle_step_option_key_counts"]),
        )
        self.assertEqual(validation["pingan_bundle_step_option_key_counts"], {})
        self.assertEqual(
            summary_view["pingan_bundle_step_source_option_key_counts"],
            validation["pingan_bundle_step_source_option_key_counts"],
        )
        self.assertEqual(
            summary_view["pingan_bundle_step_source_option_key_count"],
            len(summary_view["pingan_bundle_step_source_option_key_counts"]),
        )
        self.assertEqual(validation["pingan_bundle_step_source_option_key_counts"], {})
        self.assertEqual(summary_view["pingan_bundle_samples"], validation["pingan_bundle_samples"])
        self.assertEqual(summary_view["pingan_bundle_sample_count"], len(summary_view["pingan_bundle_samples"]))
        self.assertEqual(summary_view["pingan_bundle_sample_limit"], validation["pingan_bundle_sample_limit"])
        self.assertEqual(
            summary_view["pingan_bundle_sample_truncated"],
            validation["pingan_bundle_sample_truncated"],
        )
        self.assertEqual(summary_view["pingan_bundle_sample_truncated"], True)
        self.assertEqual(summary_view["pingan_bundle_samples"][0], "audit-pingan-buy-exception-diagnostics")
        self.assertEqual(
            summary_view["pingan_bundle_summary"],
            {
                "count": summary_view["pingan_bundle_count"],
                "step_count": summary_view["pingan_bundle_step_count"],
                "sample_count": summary_view["pingan_bundle_sample_count"],
                "sample_limit": summary_view["pingan_bundle_sample_limit"],
                "sample_truncated": summary_view["pingan_bundle_sample_truncated"],
                "label_key_count": summary_view["pingan_bundle_label_key_count"],
                "step_source_key_count": summary_view["pingan_bundle_step_source_key_count"],
                "step_name_key_count": summary_view["pingan_bundle_step_name_key_count"],
                "step_source_name_key_count": summary_view["pingan_bundle_step_source_name_key_count"],
                "step_entry_key_count": summary_view["pingan_bundle_step_entry_key_count"],
                "step_source_entry_key_count": summary_view["pingan_bundle_step_source_entry_key_count"],
                "step_option_key_count": summary_view["pingan_bundle_step_option_key_count"],
                "step_source_option_key_count": summary_view["pingan_bundle_step_source_option_key_count"],
            },
        )
        self.assertEqual(summary_view["non_execution"], True)
        self.assertNotIn("entries", summary_view)
        self.assertNotIn("bundles", summary_view)

    def test_handle_catalog_validate_summary_view_projects_empty_bundle_samples(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["catalog", "validate", "--kind", "bundle", "--label", "no-such-label", "--view", "summary"]
        )

        result = _handle_catalog_subcommand(args)

        self.assertTrue(result.ok)
        summary_view = result.data["summary_view"]
        self.assertEqual(summary_view["kind"], "bundle")
        self.assertEqual(summary_view["selected_label"], "no-such-label")
        self.assertEqual(summary_view["bundle_count"], 0)
        self.assertEqual(
            summary_view["label_summary"],
            {
                "selected_label": "no-such-label",
                "entry_key_count": 0,
                "bundle_key_count": 0,
                "total_key_count": 0,
                "selected_entry_count": 0,
                "selected_bundle_count": 0,
                "selected_total_count": 0,
                "has_selected_label": False,
            },
        )
        self.assertEqual(summary_view["bundle_samples"], [])
        self.assertEqual(summary_view["bundle_sample_count"], 0)
        self.assertFalse(summary_view["bundle_sample_truncated"])
        self.assertEqual(
            summary_view["bundle_summary"],
            {
                "selected_bundle": None,
                "selected_label": "no-such-label",
                "count": 0,
                "step_count": 0,
                "sample_count": 0,
                "sample_limit": summary_view["bundle_sample_limit"],
                "sample_truncated": False,
                "label_key_count": 0,
                "has_bundles": False,
                "has_selected_bundle": False,
            },
        )
        self.assertEqual(
            summary_view["catalog_summary"],
            {
                "mode": "validate",
                "kind": "bundle",
                "selected_entry": None,
                "selected_bundle": None,
                "selected_label": "no-such-label",
                "valid": summary_view["valid"],
                "invalid_count": summary_view["invalid_count"],
                "non_execution": summary_view["non_execution"],
                "entry_count": 0,
                "bundle_count": 0,
                "bundle_step_count": 0,
                "label_key_count": summary_view["label_summary"]["total_key_count"],
                "source_key_count": summary_view["source_summary"]["total_key_count"],
                "has_entries": False,
                "has_bundles": False,
                "has_invalid_entries": False,
                "has_selected_label": False,
            },
        )
        self.assertEqual(
            summary_view["bundle_step_summary"]["sample_count"],
            summary_view["bundle_sample_count"],
        )
        self.assertEqual(
            summary_view["bundle_step_summary"]["sample_limit"],
            summary_view["bundle_sample_limit"],
        )
        self.assertEqual(
            summary_view["bundle_step_summary"]["sample_truncated"],
            summary_view["bundle_sample_truncated"],
        )

    def test_handle_catalog_validate_missing_bundle_returns_invalid_request(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "validate", "--bundle", "missing-review"])

        result = _handle_catalog_subcommand(args)

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        validation = result.data["validation"]
        self.assertEqual(validation["selected_bundle"], "missing-review")
        self.assertEqual(validation["invalid_count"], 1)
        self.assertEqual(validation["valid"], False)
        self.assertEqual(validation["errors"][0]["target_type"], "bundle")
        self.assertEqual(validation["errors"][0]["target"], "missing-review")

    def test_handle_catalog_validate_summary_view_keeps_missing_target_error(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "validate", "--bundle", "missing-review", "--view", "summary"])

        result = _handle_catalog_subcommand(args)

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        summary_view = result.data["summary_view"]
        self.assertEqual(summary_view["mode"], "validate")
        self.assertEqual(summary_view["kind"], "bundle")
        self.assertEqual(summary_view["selected_bundle"], "missing-review")
        self.assertEqual(summary_view["invalid_count"], 1)
        self.assertEqual(summary_view["valid"], False)
        self.assertEqual(summary_view["non_execution"], True)
        self.assertEqual(summary_view["errors"][0]["target_type"], "bundle")
        self.assertEqual(summary_view["errors"][0]["target"], "missing-review")

    def test_handle_catalog_list_exposes_confirm_current_pingan_aliases(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "bundle", "--label", "confirm-current"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        bundle_names = [row["name"] for row in result.data["bundles"]]
        self.assertIn("confirm-current-pingan-complete-review", bundle_names)
        self.assertIn("confirm-current-pingan-exception-review", bundle_names)
        self.assertIn("confirm-current-pingan-rejection-review", bundle_names)
        self.assertIn("confirm-current-pingan-failure-review", bundle_names)
        alias = next(
            row for row in result.data["bundles"] if row["name"] == "confirm-current-pingan-exception-review"
        )
        self.assertEqual(alias["step_count"], 2)
        self.assertEqual([step["source"] for step in alias["steps"]], ["task", "report"])
        self.assertEqual(
            [step["entry"] for step in alias["steps"]],
            ["task-confirm-current", "audit-daily-pingan-confirm-exceptions"],
        )

    def test_handle_catalog_list_exposes_task_sell_entry(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "entry", "--label", "sell"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        entry = next(row for row in result.data["entries"] if row["name"] == "task-sell")
        self.assertEqual(entry["source"], "task")
        self.assertEqual(entry["preset"], "task-sell-default")
        self.assertIn("sell", entry["labels"])

    def test_handle_catalog_list_exposes_sell_submit_once_task_entry(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "entry", "--label", "sell-submit-once"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        entry = next(row for row in result.data["entries"] if row["name"] == "task-sell-submit-once")
        self.assertEqual(entry["source"], "task")
        self.assertEqual(entry["preset"], "sell-submit-once-default")
        self.assertIn("sell-submit-once", entry["labels"])

    def test_handle_catalog_list_exposes_buy_submit_once_task_entry(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "entry", "--label", "buy-submit-once"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        entry = next(row for row in result.data["entries"] if row["name"] == "task-buy-submit-once")
        self.assertEqual(entry["source"], "task")
        self.assertEqual(entry["preset"], "buy-submit-once-default")
        self.assertIn("buy-submit-once", entry["labels"])

    def test_handle_catalog_list_exposes_direct_submit_once_trade_entry(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "entry", "--label", "submit-once", "--view", "summary"])
        result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        entry = next(row for row in output_payload["entries"] if row["name"] == "submit-once")
        self.assertEqual(entry["source"], "trade")
        self.assertEqual(entry["command"], "submit-once")
        self.assertIn("submit-once", entry["labels"])

    def test_handle_catalog_list_exposes_trade_preflight_entry(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "entry", "--label", "preflight", "--view", "summary"])
        result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        entry = next(row for row in output_payload["entries"] if row["name"] == "trade-preflight-pingan-readiness")
        self.assertEqual(entry["source"], "trade")
        self.assertEqual(entry["command"], "preflight")
        self.assertIn("preflight", entry["labels"])
        self.assertIn("readiness", entry["labels"])

    def test_handle_catalog_list_exposes_trade_health_entry(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "entry", "--label", "health", "--view", "summary"])
        result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        entry = next(row for row in output_payload["entries"] if row["name"] == "trade-health-pingan-readiness")
        self.assertEqual(entry["source"], "trade")
        self.assertEqual(entry["command"], "health")
        self.assertIn("health", entry["labels"])
        self.assertIn("readiness", entry["labels"])

    def test_handle_catalog_bundle_list_returns_read_zxg_review_metadata(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "bundle", "--bundle", "read-zxg-review"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["selected_bundle"], "read-zxg-review")
        self.assertEqual(result.data["bundles"][0]["name"], "read-zxg-review")
        self.assertEqual(result.data["bundles"][0]["steps"][0]["entry"], "read-zxg-watchlist")
        self.assertEqual(result.data["bundles"][0]["steps"][1]["entry"], "read-zxg-full")

    def test_handle_catalog_bundle_list_returns_read_zxg_review_and_export_metadata(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "bundle", "--bundle", "read-zxg-review-and-export"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["selected_bundle"], "read-zxg-review-and-export")
        self.assertEqual(result.data["bundles"][0]["name"], "read-zxg-review-and-export")
        self.assertEqual(len(result.data["bundles"][0]["steps"]), 3)
        self.assertEqual(result.data["bundles"][0]["steps"][0]["entry"], "read-zxg-watchlist")
        self.assertEqual(result.data["bundles"][0]["steps"][1]["entry"], "read-zxg-full")
        self.assertEqual(result.data["bundles"][0]["steps"][2]["entry"], "export-zxg-watchlist")

    def test_handle_catalog_list_default_includes_export_watchlist_entry(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        entry_names = [row["name"] for row in result.data["entries"]]
        self.assertIn("export-zxg-watchlist", entry_names)

    def test_handle_catalog_list_default_includes_read_zxg_full_entry(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        entry_names = [entry["name"] for entry in result.data["entries"]]
        self.assertIn("read-zxg-full", entry_names)

    def test_handle_catalog_list_default_includes_read_zxg_watchlist_entry(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        entry_names = [entry["name"] for entry in result.data["entries"]]
        self.assertIn("read-zxg-watchlist", entry_names)

    def test_handle_catalog_list_returns_export_watchlist_entry_metadata(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--entry", "export-zxg-watchlist"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["selected_entry"], "export-zxg-watchlist")
        self.assertEqual(result.data["entries"][0]["name"], "export-zxg-watchlist")
        self.assertEqual(result.data["entries"][0]["source"], "task")
        self.assertEqual(result.data["entries"][0]["preset"], "export-zxg-watchlist")
        self.assertEqual(result.data["entries"][0]["command"], "block-read-watchlist-export")

    def test_handle_catalog_list_returns_read_zxg_full_entry_metadata(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--entry", "read-zxg-full"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["selected_entry"], "read-zxg-full")
        self.assertEqual(result.data["summary"]["entry_count"], 1)
        self.assertEqual(result.data["entries"][0]["name"], "read-zxg-full")
        self.assertEqual(result.data["entries"][0]["source"], "task")
        self.assertEqual(result.data["entries"][0]["preset"], "read-zxg-full")
        self.assertEqual(result.data["entries"][0]["command"], "block-read-full")

    def test_handle_catalog_list_returns_read_zxg_watchlist_entry_metadata(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--entry", "read-zxg-watchlist"])
        result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["selected_entry"], "read-zxg-watchlist")
        self.assertEqual(result.data["summary"]["entry_count"], 1)
        self.assertEqual(result.data["entries"][0]["name"], "read-zxg-watchlist")
        self.assertEqual(result.data["entries"][0]["source"], "task")
        self.assertEqual(result.data["entries"][0]["preset"], "read-zxg-watchlist")
        self.assertEqual(result.data["entries"][0]["command"], "block-read-watchlist")

    def test_handle_catalog_list_uses_stable_ordering(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "entry"])
        custom_entries = {
            "alpha": {
                "source": "report",
                "preset": "daily-review",
                "description": "alpha",
                "labels": ["report"],
            },
            "zeta": {
                "source": "task",
                "preset": "refresh-default",
                "description": "zeta",
                "labels": ["task", "maintenance", "refresh"],
            },
            "beta": {
                "source": "report",
                "preset": "recent-ledger",
                "description": "beta",
                "labels": ["report", "review"],
            },
        }
        with patch("tdxquant.cli.load_command_catalog", return_value=custom_entries), patch(
            "tdxquant.cli.load_command_bundles", return_value={}
        ):
            result = _handle_catalog_subcommand(args)
        ordered_names = [row["name"] for row in result.data["entries"]]
        self.assertEqual(ordered_names, ["zeta", "beta", "alpha"])

    def test_handle_catalog_report_entry_dispatches_through_report_subcommand(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--entry", "daily-review"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        with patch("tdxquant.cli._handle_report_subcommand", return_value=expected) as mocked_handler:
            result = _handle_catalog_subcommand(args)
        self.assertIs(result, expected)
        self.assertIn("summary_view", result.data)
        forwarded = mocked_handler.call_args.args[0]
        self.assertEqual(forwarded.command, "report")
        self.assertEqual(forwarded.report_command, "run")
        self.assertEqual(forwarded.preset, "daily-review")

    def test_handle_catalog_run_entry_builds_summary_view(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--entry", "turbo-buy", "--code", "000001", "--price", "10.00", "--quantity", "100"])
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={"result_dialog": {"contract_no": "B123"}, "input": {"code": "000001", "price": "10.00", "quantity": 100}},
        )
        with patch("tdxquant.cli._run_trade_buy", return_value=expected):
            result = _handle_catalog_subcommand(args)
        summary_view = result.data["summary_view"]
        self.assertEqual(summary_view["mode"], "run")
        self.assertEqual(summary_view["target"]["type"], "entry")
        self.assertEqual(summary_view["target"]["name"], "turbo-buy")
        self.assertEqual(summary_view["contract_no"], "B123")

    def test_handle_catalog_task_entry_dispatches_through_task_subcommand(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["catalog", "run", "--entry", "guarded-buy", "--code", "000001", "--price", "10.00", "--quantity", "100"]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        with patch("tdxquant.cli._handle_task_subcommand", return_value=expected) as mocked_handler:
            result = _handle_catalog_subcommand(args)
        self.assertIs(result, expected)
        forwarded = mocked_handler.call_args.args[0]
        self.assertEqual(forwarded.command, "task")
        self.assertEqual(forwarded.task_command, "run")
        self.assertEqual(forwarded.preset, "guarded-default")

    def test_handle_catalog_watchlist_entry_dispatches_through_task_subcommand(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--entry", "export-zxg-watchlist"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        with patch("tdxquant.cli._handle_task_subcommand", return_value=expected) as mocked_handler:
            result = _handle_catalog_subcommand(args)
        self.assertIs(result, expected)
        forwarded = mocked_handler.call_args.args[0]
        self.assertEqual(forwarded.command, "task")
        self.assertEqual(forwarded.task_command, "run")
        self.assertEqual(forwarded.preset, "export-zxg-watchlist")

    def test_handle_catalog_read_zxg_full_entry_dispatches_through_task_subcommand(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--entry", "read-zxg-full"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        with patch("tdxquant.cli._handle_task_subcommand", return_value=expected) as mocked_handler:
            result = _handle_catalog_subcommand(args)
        self.assertIs(result, expected)
        mocked_handler.assert_called_once()
        forwarded = mocked_handler.call_args.args[0]
        self.assertEqual(forwarded.command, "task")
        self.assertEqual(forwarded.task_command, "run")
        self.assertEqual(forwarded.preset, "read-zxg-full")

    def test_handle_catalog_read_zxg_watchlist_entry_dispatches_through_task_subcommand(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--entry", "read-zxg-watchlist"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        with patch("tdxquant.cli._handle_task_subcommand", return_value=expected) as mocked_handler:
            result = _handle_catalog_subcommand(args)
        self.assertIs(result, expected)
        mocked_handler.assert_called_once()
        forwarded = mocked_handler.call_args.args[0]
        self.assertEqual(forwarded.command, "task")
        self.assertEqual(forwarded.task_command, "run")
        self.assertEqual(forwarded.preset, "read-zxg-watchlist")

    def test_handle_catalog_trade_entry_preserves_explicit_overrides(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "run",
                "--entry",
                "turbo-buy",
                "--port",
                "COM9",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        with patch("tdxquant.cli._run_trade_buy", return_value=expected) as mocked_trade_buy:
            result = _handle_catalog_subcommand(args)
        self.assertIs(result, expected)
        forwarded = mocked_trade_buy.call_args.args[0]
        self.assertEqual(forwarded.trade_command, "buy")
        self.assertEqual(forwarded.preset, "turbo-buy")
        self.assertEqual(forwarded.port, "COM9")

    def test_handle_catalog_invalid_source_returns_invalid_request(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--entry", "broken-entry"])
        with patch(
            "tdxquant.cli.resolve_command_catalog_entry",
            return_value={"source": "broken", "preset": "x", "description": ""},
        ):
            result = _handle_catalog_subcommand(args)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)

    def test_handle_catalog_plan_entry_returns_resolved_dispatch_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--entry", "daily-review", "--timezone", "UTC"])
        with patch("tdxquant.cli._handle_report_subcommand") as mocked_report_handler:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_entry"]["name"], "daily-review")
        self.assertEqual(result.data["dispatch"]["source"], "report")
        self.assertEqual(result.data["dispatch"]["command_group"], "report")
        self.assertEqual(result.data["dispatch"]["command_name"], "daily")
        self.assertEqual(result.data["resolved_args"]["timezone"], "UTC")
        self.assertIn("summary_view", result.data)
        self.assertEqual(result.data["summary_view"]["mode"], "plan")
        mocked_report_handler.assert_not_called()

    def test_handle_catalog_preview_entry_returns_preview_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "preview", "--entry", "daily-review", "--timezone", "UTC"])
        with patch("tdxquant.cli._handle_report_subcommand") as mocked_report_handler:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["mode"], "preview")
        self.assertEqual(result.data["summary_view"]["mode"], "preview")
        self.assertEqual(result.data["summary_view"]["target"]["name"], "daily-review")
        self.assertEqual(result.data["summary_view"]["resolved_args"]["timezone"], "UTC")
        mocked_report_handler.assert_not_called()

    def test_handle_catalog_plan_watchlist_entry_returns_resolved_dispatch_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--entry", "export-zxg-watchlist"])
        with patch("tdxquant.cli._handle_task_subcommand") as mocked_task_handler:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_entry"]["name"], "export-zxg-watchlist")
        self.assertEqual(result.data["dispatch"]["source"], "task")
        self.assertEqual(result.data["dispatch"]["command_group"], "task")
        self.assertEqual(result.data["dispatch"]["command_name"], "block-read-watchlist-export")
        self.assertEqual(result.data["resolved_args"]["block_code"], "ZXG")
        self.assertEqual(result.data["resolved_args"]["export_output"], "runtime/exports/zxg.json")
        self.assertFalse(result.data["resolved_args"]["overwrite"])
        mocked_task_handler.assert_not_called()

    def test_handle_catalog_plan_block_watchlist_import_entry_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--entry", "plan-zxg-watchlist-import"])
        with patch("tdxquant.cli._handle_task_subcommand") as mocked_task_handler:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_entry"]["name"], "plan-zxg-watchlist-import")
        self.assertEqual(result.data["dispatch"]["source"], "task")
        self.assertEqual(result.data["dispatch"]["command_group"], "task")
        self.assertEqual(result.data["dispatch"]["command_name"], "block-watchlist-import")
        self.assertEqual(
            result.data["resolved_args"]["input_path"],
            "runtime/watchlist-imports/zxg-watchlist-import.example.json",
        )
        self.assertTrue(result.data["resolved_args"]["dry_run"])
        self.assertTrue(result.data["resolved_args"]["show"])
        mocked_task_handler.assert_not_called()

    def test_handle_catalog_plan_block_sync_write_policy_entry_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--entry", "plan-zxg-block-sync-merge"])
        with patch("tdxquant.cli._handle_task_subcommand") as mocked_task_handler:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_entry"]["name"], "plan-zxg-block-sync-merge")
        self.assertEqual(result.data["dispatch"]["source"], "task")
        self.assertEqual(result.data["dispatch"]["command_group"], "task")
        self.assertEqual(result.data["dispatch"]["command_name"], "block-sync")
        self.assertEqual(result.data["resolved_args"]["block_code"], "ZXG")
        self.assertEqual(result.data["resolved_args"]["stock"], ["000001.SZ", "600519.SH"])
        self.assertEqual(result.data["resolved_args"]["write_policy"], "merge_dry_run")
        self.assertTrue(result.data["resolved_args"]["show"])
        mocked_task_handler.assert_not_called()

    def test_handle_catalog_plan_read_zxg_full_returns_resolved_dispatch_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--entry", "read-zxg-full"])
        with patch("tdxquant.cli._handle_task_subcommand") as mocked_task_handler:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_entry"]["name"], "read-zxg-full")
        self.assertEqual(result.data["dispatch"]["source"], "task")
        self.assertEqual(result.data["dispatch"]["command_group"], "task")
        self.assertEqual(result.data["dispatch"]["command_name"], "block-read-full")
        self.assertEqual(result.data["resolved_args"]["task_command"], "block-read-full")
        self.assertEqual(result.data["resolved_args"]["block_code"], "ZXG")
        mocked_task_handler.assert_not_called()

    def test_handle_catalog_plan_read_zxg_watchlist_returns_resolved_dispatch_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--entry", "read-zxg-watchlist"])
        with patch("tdxquant.cli._handle_task_subcommand") as mocked_task_handler:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_entry"]["name"], "read-zxg-watchlist")
        self.assertEqual(result.data["dispatch"]["source"], "task")
        self.assertEqual(result.data["dispatch"]["command_group"], "task")
        self.assertEqual(result.data["dispatch"]["command_name"], "block-read-watchlist")
        self.assertEqual(result.data["resolved_args"]["profile"], "default")
        self.assertEqual(result.data["resolved_args"]["api_profile"], "safe_read")
        self.assertEqual(result.data["resolved_args"]["task_command"], "block-read-watchlist")
        self.assertEqual(result.data["resolved_args"]["block_code"], "ZXG")
        self.assertEqual(result.data["summary_view"]["resolved_args"]["profile"], "default")
        self.assertEqual(result.data["summary_view"]["resolved_args"]["api_profile"], "safe_read")
        mocked_task_handler.assert_not_called()

    def test_handle_catalog_plan_bundle_returns_selected_steps_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--bundle", "guarded-review-buy", "--only-step", "review"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "guarded-review-buy")
        self.assertEqual(result.data["catalog_bundle"]["selected_from_step"], "review")
        self.assertEqual(result.data["catalog_bundle"]["selected_step_count"], 1)
        self.assertEqual(len(result.data["steps"]), 1)
        self.assertEqual(result.data["steps"][0]["name"], "review")
        self.assertEqual(result.data["steps"][0]["dispatch"]["command_group"], "report")
        self.assertEqual(result.data["steps"][0]["resolved_args"]["limit"], 5)
        self.assertEqual(result.data["summary_view"]["selected_step_count"], 1)
        self.assertEqual(result.data["summary_view"]["step_resolved_arg_key_counts"], {"limit": 1, "profile": 1})
        self.assertEqual(result.data["summary_view"]["step_resolved_arg_key_count"], 2)
        self.assertEqual(
            result.data["summary_view"]["step_source_resolved_arg_key_counts"],
            {"report:limit": 1, "report:profile": 1},
        )
        self.assertEqual(result.data["summary_view"]["step_source_resolved_arg_key_count"], 2)
        self.assertEqual(
            result.data["summary_view"]["selected_step_summary"]["step_resolved_arg_key_count"],
            2,
        )
        self.assertEqual(
            result.data["summary_view"]["selected_step_summary"]["step_source_resolved_arg_key_count"],
            2,
        )
        self.assertEqual(result.data["summary_view"]["selected_step_summary"]["first_step_source"], "report")
        self.assertEqual(result.data["summary_view"]["selected_step_summary"]["last_step_source"], "report")
        self.assertEqual(result.data["summary_view"]["selected_step_summary"]["first_step_command_name"], "ledger")
        self.assertEqual(result.data["summary_view"]["selected_step_summary"]["last_step_command_name"], "ledger")
        self.assertEqual(result.data["summary_view"]["selected_step_summary"]["first_step_index"], 2)
        self.assertEqual(result.data["summary_view"]["selected_step_summary"]["last_step_index"], 2)
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_buy_pingan_complete_bundle_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--bundle",
                "buy-pingan-complete-review",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "buy-pingan-complete-review")
        self.assertEqual(
            [step["entry"] for step in result.data["steps"]],
            ["task-buy", "daily-success", "audit-daily-pingan-confirmed"],
        )
        self.assertEqual(result.data["steps"][0]["dispatch"]["command_name"], "trade-buy")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_buy_pingan_exception_bundle_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--bundle",
                "buy-pingan-exception-review",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "buy-pingan-exception-review")
        self.assertEqual(
            [step["entry"] for step in result.data["steps"]],
            ["task-buy", "audit-daily-pingan-buy-exceptions"],
        )
        self.assertEqual(result.data["steps"][0]["dispatch"]["command_name"], "trade-buy")
        self.assertEqual(result.data["steps"][1]["dispatch"]["command_name"], "audit-daily")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_buy_pingan_rejection_bundle_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--bundle",
                "buy-pingan-rejection-review",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "buy-pingan-rejection-review")
        self.assertEqual(
            [step["entry"] for step in result.data["steps"]],
            ["task-buy", "audit-daily-pingan-buy-rejected"],
        )
        self.assertEqual(result.data["steps"][0]["dispatch"]["command_name"], "trade-buy")
        self.assertEqual(result.data["steps"][1]["dispatch"]["command_name"], "audit-daily")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_buy_pingan_failure_bundle_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--bundle",
                "buy-pingan-failure-review",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "buy-pingan-failure-review")
        self.assertEqual(
            [step["entry"] for step in result.data["steps"]],
            ["task-buy", "audit-daily-pingan-buy-failed"],
        )
        self.assertEqual(result.data["steps"][0]["dispatch"]["command_name"], "trade-buy")
        self.assertEqual(result.data["steps"][1]["dispatch"]["command_name"], "audit-daily")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_guarded_pingan_buy_complete_bundle_stays_available(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--bundle",
                "guarded-pingan-buy-complete-review",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "guarded-pingan-buy-complete-review")
        self.assertEqual(
            [step["entry"] for step in result.data["steps"]],
            ["guarded-buy", "daily-success", "audit-daily-pingan-confirmed"],
        )
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_guarded_pingan_buy_exception_bundle_stays_available(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--bundle",
                "guarded-pingan-buy-exception-review",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "guarded-pingan-buy-exception-review")
        self.assertEqual(
            [step["entry"] for step in result.data["steps"]],
            ["guarded-buy", "audit-daily-pingan-buy-exceptions"],
        )
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_task_report_combo_bundle_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--bundle", "confirm-complete-review"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "confirm-complete-review")
        self.assertEqual(result.data["catalog_bundle"]["selected_step_count"], 3)
        self.assertEqual([step["name"] for step in result.data["steps"]], ["confirm", "success", "audit"])
        self.assertEqual(
            [step["dispatch"]["command_group"] for step in result.data["steps"]],
            ["task", "report", "report"],
        )
        self.assertEqual(result.data["steps"][0]["dispatch"]["command_name"], "trade-confirm-current")
        self.assertEqual(result.data["steps"][1]["dispatch"]["command_name"], "daily")
        self.assertEqual(result.data["steps"][2]["dispatch"]["command_name"], "audit-daily")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_task_report_combo_summary_counts_step_sources(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--bundle", "confirm-complete-review", "--view", "summary"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        self.assertEqual(output_payload["target"]["name"], "confirm-complete-review")
        self.assertEqual(output_payload["selected_step_count"], 3)
        self.assertEqual(output_payload["step_source_counts"], {"task": 1, "report": 2})
        self.assertEqual(output_payload["step_source_key_count"], 2)
        self.assertEqual(output_payload["step_name_counts"], {"audit": 1, "confirm": 1, "success": 1})
        self.assertEqual(output_payload["step_name_key_count"], 3)
        self.assertEqual(
            output_payload["step_source_name_counts"],
            {"report:audit": 1, "report:success": 1, "task:confirm": 1},
        )
        self.assertEqual(output_payload["step_source_name_key_count"], 3)
        self.assertEqual(
            output_payload["step_entry_counts"],
            {"audit-daily-confirmed": 1, "daily-success": 1, "task-confirm-current": 1},
        )
        self.assertEqual(output_payload["step_entry_key_count"], 3)
        self.assertEqual(
            output_payload["step_source_entry_counts"],
            {"report:audit-daily-confirmed": 1, "report:daily-success": 1, "task:task-confirm-current": 1},
        )
        self.assertEqual(output_payload["step_source_entry_key_count"], 3)
        self.assertEqual(output_payload["constraints"]["execution_mode"], "non_executing")
        self.assertFalse(output_payload["constraints"]["dispatch_executed"])
        self.assertEqual(
            output_payload["plan_outcome"],
            {
                "mode": "plan",
                "target_type": "bundle",
                "target_name": "confirm-complete-review",
                "selected_step_count": 3,
                "step_source_key_count": 2,
                "ok": True,
                "code": output_payload["code"],
                "message": output_payload["message"],
                "execution_mode": "non_executing",
                "dispatch_executed": False,
                "non_execution": True,
                "has_steps": True,
            },
        )
        self.assertEqual(
            output_payload["selected_step_summary"],
            {
                "selected_from_step": "confirm",
                "selected_to_step": "audit",
                "selected_step_count": 3,
                "first_step_index": 1,
                "last_step_index": 3,
                "first_step_name": "confirm",
                "last_step_name": "audit",
                "first_step_source": "task",
                "last_step_source": "report",
                "first_step_command_name": "trade-confirm-current",
                "last_step_command_name": "audit-daily",
                "first_step_entry": "task-confirm-current",
                "last_step_entry": "audit-daily-confirmed",
                "step_source_key_count": 2,
                "step_name_counts": {"audit": 1, "confirm": 1, "success": 1},
                "step_name_key_count": 3,
                "step_entry_counts": {
                    "audit-daily-confirmed": 1,
                    "daily-success": 1,
                    "task-confirm-current": 1,
                },
                "step_entry_key_count": 3,
                "step_source_name_counts": {
                    "report:audit": 1,
                    "report:success": 1,
                    "task:confirm": 1,
                },
                "step_source_name_key_count": 3,
                "step_source_entry_counts": {
                    "report:audit-daily-confirmed": 1,
                    "report:daily-success": 1,
                    "task:task-confirm-current": 1,
                },
                "step_source_entry_key_count": 3,
                "step_resolved_arg_key_count": 5,
                "step_source_resolved_arg_key_count": 6,
                "trade_plan_boundary_step_count": 1,
                "trade_plan_boundary_sides": [],
                "has_step_slice": True,
                "has_steps": True,
            },
        )
        self.assertEqual(
            output_payload["plan_summary"],
            {
                "mode": "plan",
                "target_type": "bundle",
                "target_name": "confirm-complete-review",
                "execution_mode": "non_executing",
                "non_execution": True,
                "dispatch_executed": False,
                "ok": True,
                "code": output_payload["code"],
                "selected_from_step": "confirm",
                "selected_to_step": "audit",
                "first_step_index": 1,
                "last_step_index": 3,
                "first_step_name": "confirm",
                "last_step_name": "audit",
                "first_step_source": "task",
                "last_step_source": "report",
                "first_step_command_name": "trade-confirm-current",
                "last_step_command_name": "audit-daily",
                "first_step_entry": "task-confirm-current",
                "last_step_entry": "audit-daily-confirmed",
                "selected_step_count": 3,
                "step_source_key_count": 2,
                "step_name_counts": {"audit": 1, "confirm": 1, "success": 1},
                "step_name_key_count": 3,
                "step_entry_counts": {
                    "audit-daily-confirmed": 1,
                    "daily-success": 1,
                    "task-confirm-current": 1,
                },
                "step_entry_key_count": 3,
                "step_source_name_counts": {
                    "report:audit": 1,
                    "report:success": 1,
                    "task:confirm": 1,
                },
                "step_source_name_key_count": 3,
                "step_source_entry_counts": {
                    "report:audit-daily-confirmed": 1,
                    "report:daily-success": 1,
                    "task:task-confirm-current": 1,
                },
                "step_source_entry_key_count": 3,
                "step_resolved_arg_key_count": 5,
                "step_source_resolved_arg_key_count": 6,
                "trade_plan_boundary_step_count": 1,
                "trade_plan_boundary_sides": [],
                "has_steps": True,
                "has_step_slice": True,
            },
        )
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_preview_task_report_combo_summary_exposes_plan_summary(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "preview", "--bundle", "confirm-complete-review", "--view", "summary"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)

        self.assertTrue(result.ok)
        self.assertEqual(output_payload["plan_summary"]["mode"], "preview")
        self.assertEqual(output_payload["plan_summary"]["target_type"], "bundle")
        self.assertEqual(output_payload["plan_summary"]["target_name"], "confirm-complete-review")
        self.assertEqual(output_payload["plan_summary"]["non_execution"], True)
        self.assertEqual(output_payload["plan_summary"]["dispatch_executed"], False)
        self.assertEqual(
            output_payload["plan_summary"]["selected_step_count"],
            output_payload["selected_step_summary"]["selected_step_count"],
        )
        self.assertEqual(
            output_payload["plan_summary"]["step_source_key_count"],
            output_payload["selected_step_summary"]["step_source_key_count"],
        )
        self.assertEqual(
            output_payload["plan_summary"]["step_name_counts"],
            output_payload["selected_step_summary"]["step_name_counts"],
        )
        self.assertEqual(
            output_payload["plan_summary"]["step_entry_counts"],
            output_payload["selected_step_summary"]["step_entry_counts"],
        )
        self.assertEqual(
            output_payload["plan_summary"]["step_source_name_counts"],
            output_payload["selected_step_summary"]["step_source_name_counts"],
        )
        self.assertEqual(
            output_payload["plan_summary"]["step_source_entry_counts"],
            output_payload["selected_step_summary"]["step_source_entry_counts"],
        )
        self.assertEqual(output_payload["plan_summary"]["has_steps"], True)
        self.assertEqual(output_payload["plan_summary"]["has_step_slice"], True)
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_confirm_current_pingan_bundle_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--bundle", "confirm-current-pingan-exception-review"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "confirm-current-pingan-exception-review")
        self.assertEqual(result.data["catalog_bundle"]["selected_step_count"], 2)
        self.assertEqual([step["name"] for step in result.data["steps"]], ["confirm", "audit"])
        self.assertEqual(
            [step["dispatch"]["command_group"] for step in result.data["steps"]],
            ["task", "report"],
        )
        self.assertEqual(result.data["steps"][0]["dispatch"]["command_name"], "trade-confirm-current")
        self.assertEqual(result.data["steps"][1]["dispatch"]["command_name"], "audit-daily")
        self.assertEqual(result.data["summary_view"]["selected_step_count"], 2)
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_confirm_current_pingan_complete_bundle_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--bundle", "confirm-current-pingan-complete-review"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "confirm-current-pingan-complete-review")
        self.assertEqual(result.data["catalog_bundle"]["selected_step_count"], 3)
        self.assertEqual([step["entry"] for step in result.data["steps"]], ["task-confirm-current", "daily-success", "audit-daily-pingan-confirmed"])
        self.assertEqual([step["name"] for step in result.data["steps"]], ["confirm", "success", "audit"])
        self.assertEqual(
            [step["dispatch"]["command_group"] for step in result.data["steps"]],
            ["task", "report", "report"],
        )
        self.assertEqual(result.data["steps"][0]["dispatch"]["command_name"], "trade-confirm-current")
        self.assertEqual(result.data["steps"][1]["dispatch"]["command_name"], "daily")
        self.assertEqual(result.data["steps"][2]["dispatch"]["command_name"], "audit-daily")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_confirm_pingan_complete_bundle_stays_available(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--bundle", "confirm-pingan-complete-review"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "confirm-pingan-complete-review")
        self.assertEqual([step["entry"] for step in result.data["steps"]], ["task-confirm-current", "daily-success", "audit-daily-pingan-confirmed"])
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_task_sell_entry_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["catalog", "plan", "--entry", "task-sell", "--code", "000001.SZ", "--price", "10.00", "--quantity", "100"]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_entry"]["name"], "task-sell")
        self.assertEqual(result.data["dispatch"]["command_group"], "task")
        self.assertEqual(result.data["dispatch"]["command_name"], "trade-sell")
        self.assertEqual(result.data["resolved_args"]["task_command"], "trade-sell")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_task_buy_summary_exposes_trade_boundary(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--entry",
                "task-buy",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--view",
                "summary",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        boundary = output_payload["trade_plan_boundary"]
        self.assertEqual(boundary["trade_command"], "trade-buy")
        self.assertEqual(boundary["input_kind"], "order")
        self.assertEqual(boundary["execution_mode"], "non_executing_catalog_plan")
        self.assertEqual(boundary["dispatch_executed"], False)
        self.assertEqual(boundary["required_input_fields"], ["port", "code", "price", "quantity"])
        self.assertEqual(boundary["provided_input_fields"], ["port", "code", "price", "quantity"])
        self.assertEqual(boundary["missing_input_fields"], [])
        self.assertEqual(boundary["required_input_count"], 4)
        self.assertEqual(boundary["provided_input_count"], 4)
        self.assertEqual(boundary["missing_input_count"], 0)
        self.assertEqual(boundary["input_coverage_status"], "complete")
        self.assertEqual(boundary["live_trade_requires_explicit_run"], True)
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_preview_task_buy_summary_exposes_trade_boundary(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "preview",
                "--entry",
                "task-buy",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--view",
                "summary",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        boundary = output_payload["trade_plan_boundary"]
        self.assertEqual(boundary["trade_command"], "trade-buy")
        self.assertEqual(boundary["input_kind"], "order")
        self.assertEqual(boundary["execution_mode"], "non_executing_catalog_plan")
        self.assertEqual(boundary["dispatch_executed"], False)
        self.assertEqual(boundary["required_input_fields"], ["port", "code", "price", "quantity"])
        self.assertEqual(boundary["provided_input_fields"], ["port", "code", "price", "quantity"])
        self.assertEqual(boundary["missing_input_fields"], [])
        self.assertEqual(boundary["input_coverage_status"], "complete")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_task_sell_summary_exposes_trade_boundary(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--entry",
                "task-sell",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--view",
                "summary",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        boundary = output_payload["trade_plan_boundary"]
        self.assertEqual(boundary["trade_command"], "trade-sell")
        self.assertEqual(boundary["execution_mode"], "non_executing_catalog_plan")
        self.assertEqual(boundary["dispatch_executed"], False)
        self.assertEqual(boundary["required_input_fields"], ["port", "code", "price", "quantity"])
        self.assertEqual(boundary["provided_input_fields"], ["port", "code", "price", "quantity"])
        self.assertEqual(boundary["missing_input_fields"], [])
        self.assertEqual(boundary["required_input_count"], 4)
        self.assertEqual(boundary["provided_input_count"], 4)
        self.assertEqual(boundary["missing_input_count"], 0)
        self.assertEqual(boundary["input_coverage_status"], "complete")
        self.assertEqual(boundary["live_trade_requires_explicit_run"], True)
        self.assertEqual(output_payload["constraints"]["execution_mode"], "non_executing")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_task_sell_summary_marks_missing_trade_inputs(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--entry", "task-sell", "--view", "summary"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        boundary = output_payload["trade_plan_boundary"]
        self.assertEqual(boundary["trade_command"], "trade-sell")
        self.assertEqual(boundary["required_input_fields"], ["port", "code", "price", "quantity"])
        self.assertEqual(boundary["provided_input_fields"], ["port"])
        self.assertEqual(boundary["missing_input_fields"], ["code", "price", "quantity"])
        self.assertEqual(boundary["required_input_count"], 4)
        self.assertEqual(boundary["provided_input_count"], 1)
        self.assertEqual(boundary["missing_input_count"], 3)
        self.assertEqual(boundary["input_coverage_status"], "missing_required_inputs")
        self.assertEqual(boundary["dispatch_executed"], False)
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_task_confirm_current_summary_exposes_trade_boundary(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--entry", "task-confirm-current", "--view", "summary"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        boundary = output_payload["trade_plan_boundary"]
        self.assertEqual(boundary["trade_command"], "trade-confirm-current")
        self.assertEqual(boundary["input_kind"], "confirmation")
        self.assertEqual(boundary["execution_mode"], "non_executing_catalog_plan")
        self.assertEqual(boundary["dispatch_executed"], False)
        self.assertEqual(boundary["required_input_fields"], [])
        self.assertEqual(boundary["provided_input_fields"], [])
        self.assertEqual(boundary["missing_input_fields"], [])
        self.assertEqual(boundary["required_input_count"], 0)
        self.assertEqual(boundary["provided_input_count"], 0)
        self.assertEqual(boundary["missing_input_count"], 0)
        self.assertEqual(boundary["input_coverage_status"], "no_required_inputs")
        self.assertEqual(boundary["live_trade_requires_explicit_run"], True)
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_preview_task_confirm_current_summary_exposes_trade_boundary(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "preview", "--entry", "task-confirm-current", "--view", "summary"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        boundary = output_payload["trade_plan_boundary"]
        self.assertEqual(boundary["trade_command"], "trade-confirm-current")
        self.assertEqual(boundary["input_kind"], "confirmation")
        self.assertEqual(boundary["execution_mode"], "non_executing_catalog_plan")
        self.assertEqual(boundary["dispatch_executed"], False)
        self.assertEqual(boundary["required_input_fields"], [])
        self.assertEqual(boundary["provided_input_fields"], [])
        self.assertEqual(boundary["missing_input_fields"], [])
        self.assertEqual(boundary["input_coverage_status"], "no_required_inputs")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_trade_preflight_summary_exposes_readiness_boundary(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--entry",
                "trade-preflight-pingan-readiness",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--view",
                "summary",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        self.assertEqual(output_payload["dispatch"]["command_group"], "trade")
        self.assertEqual(output_payload["dispatch"]["command_name"], "preflight")
        boundary = output_payload["trade_plan_boundary"]
        self.assertEqual(boundary["trade_command"], "preflight")
        self.assertEqual(boundary["input_kind"], "preflight_order_readiness")
        self.assertEqual(boundary["execution_mode"], "non_executing_catalog_plan")
        self.assertEqual(boundary["dispatch_executed"], False)
        self.assertEqual(boundary["required_input_fields"], ["port", "code", "price", "quantity"])
        self.assertEqual(boundary["provided_input_fields"], ["port", "code", "price", "quantity"])
        self.assertEqual(boundary["missing_input_fields"], [])
        self.assertEqual(boundary["input_coverage_status"], "complete")
        self.assertEqual(output_payload["constraints"]["execution_mode"], "non_executing")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_trade_preflight_summary_marks_missing_order_inputs(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--entry", "trade-preflight-pingan-readiness", "--view", "summary"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        boundary = output_payload["trade_plan_boundary"]
        self.assertEqual(boundary["trade_command"], "preflight")
        self.assertEqual(boundary["input_kind"], "preflight_order_readiness")
        self.assertEqual(boundary["required_input_fields"], ["port", "code", "price", "quantity"])
        self.assertEqual(boundary["provided_input_fields"], ["port"])
        self.assertEqual(boundary["missing_input_fields"], ["code", "price", "quantity"])
        self.assertEqual(boundary["required_input_count"], 4)
        self.assertEqual(boundary["provided_input_count"], 1)
        self.assertEqual(boundary["missing_input_count"], 3)
        self.assertEqual(boundary["input_coverage_status"], "missing_required_inputs")
        self.assertEqual(boundary["dispatch_executed"], False)
        self.assertEqual(output_payload["constraints"]["dispatch_executed"], False)
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_direct_submit_once_summary_exposes_side_boundary(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--entry",
                "submit-once",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--view",
                "summary",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        self.assertEqual(output_payload["dispatch"]["command_group"], "trade")
        self.assertEqual(output_payload["dispatch"]["command_name"], "submit-once")
        boundary = output_payload["trade_plan_boundary"]
        self.assertEqual(boundary["trade_command"], "submit-once")
        self.assertEqual(boundary["side"], "buy")
        self.assertEqual(boundary["input_kind"], "submit_once_order")
        self.assertEqual(boundary["execution_mode"], "non_executing_catalog_plan")
        self.assertEqual(boundary["dispatch_executed"], False)
        self.assertEqual(boundary["required_input_fields"], ["side", "port", "code", "price", "quantity"])
        self.assertEqual(boundary["provided_input_fields"], ["side", "port", "code", "price", "quantity"])
        self.assertEqual(boundary["missing_input_fields"], [])
        self.assertEqual(boundary["input_coverage_status"], "complete")
        self.assertEqual(output_payload["constraints"]["execution_mode"], "non_executing")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_direct_submit_once_summary_marks_missing_order_inputs(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--entry", "submit-once", "--view", "summary"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        boundary = output_payload["trade_plan_boundary"]
        self.assertEqual(boundary["trade_command"], "submit-once")
        self.assertEqual(boundary["side"], "buy")
        self.assertEqual(boundary["required_input_fields"], ["side", "port", "code", "price", "quantity"])
        self.assertEqual(boundary["provided_input_fields"], ["side", "port"])
        self.assertEqual(boundary["missing_input_fields"], ["code", "price", "quantity"])
        self.assertEqual(boundary["required_input_count"], 5)
        self.assertEqual(boundary["provided_input_count"], 2)
        self.assertEqual(boundary["missing_input_count"], 3)
        self.assertEqual(boundary["input_coverage_status"], "missing_required_inputs")
        self.assertEqual(boundary["dispatch_executed"], False)
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_direct_submit_once_summary_accepts_side_override(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--entry",
                "submit-once",
                "--side",
                "sell",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--view",
                "summary",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        boundary = output_payload["trade_plan_boundary"]
        self.assertEqual(boundary["trade_command"], "submit-once")
        self.assertEqual(boundary["side"], "sell")
        self.assertEqual(boundary["provided_input_fields"], ["side", "port", "code", "price", "quantity"])
        self.assertEqual(boundary["missing_input_fields"], [])
        self.assertEqual(output_payload["constraints"]["dispatch_executed"], False)
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_preview_task_submit_once_summary_accepts_side_override(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "preview",
                "--entry",
                "task-submit-once",
                "--side",
                "sell",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--view",
                "summary",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        boundary = output_payload["trade_plan_boundary"]
        self.assertEqual(boundary["trade_command"], "trade-submit-once")
        self.assertEqual(boundary["side"], "sell")
        self.assertEqual(boundary["provided_input_fields"], ["side", "port", "code", "price", "quantity"])
        self.assertEqual(boundary["missing_input_fields"], [])
        self.assertEqual(output_payload["constraints"]["dispatch_executed"], False)
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_task_buy_submit_once_plan_and_preview_expose_side_boundary(self) -> None:
        parser = build_parser()
        for catalog_command in ("plan", "preview"):
            with self.subTest(catalog_command=catalog_command):
                args = parser.parse_args(
                    [
                        "catalog",
                        catalog_command,
                        "--entry",
                        "task-buy-submit-once",
                        "--view",
                        "summary",
                    ]
                )
                with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
                    result = _handle_catalog_subcommand(args)
                output_payload = _select_catalog_output_payload(args, result)
                self.assertTrue(result.ok)
                boundary = output_payload["trade_plan_boundary"]
                self.assertEqual(boundary["trade_command"], "trade-submit-once")
                self.assertEqual(boundary["side"], "buy")
                self.assertEqual(boundary["input_kind"], "submit_once_order")
                self.assertEqual(boundary["execution_mode"], "non_executing_catalog_plan")
                self.assertEqual(boundary["dispatch_executed"], False)
                self.assertEqual(boundary["required_input_fields"], ["side", "port", "code", "price", "quantity"])
                self.assertEqual(boundary["provided_input_fields"], ["side", "port"])
                self.assertEqual(boundary["missing_input_fields"], ["code", "price", "quantity"])
                self.assertEqual(boundary["input_coverage_status"], "missing_required_inputs")
                mocked_dispatch.assert_not_called()

    def test_handle_catalog_task_sell_submit_once_plan_and_preview_expose_side_boundary(self) -> None:
        parser = build_parser()
        for catalog_command in ("plan", "preview"):
            with self.subTest(catalog_command=catalog_command):
                args = parser.parse_args(
                    [
                        "catalog",
                        catalog_command,
                        "--entry",
                        "task-sell-submit-once",
                        "--view",
                        "summary",
                    ]
                )
                with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
                    result = _handle_catalog_subcommand(args)
                output_payload = _select_catalog_output_payload(args, result)
                self.assertTrue(result.ok)
                boundary = output_payload["trade_plan_boundary"]
                self.assertEqual(boundary["trade_command"], "trade-submit-once")
                self.assertEqual(boundary["side"], "sell")
                self.assertEqual(boundary["input_kind"], "submit_once_order")
                self.assertEqual(boundary["execution_mode"], "non_executing_catalog_plan")
                self.assertEqual(boundary["dispatch_executed"], False)
                self.assertEqual(boundary["required_input_fields"], ["side", "port", "code", "price", "quantity"])
                self.assertEqual(boundary["provided_input_fields"], ["side", "port"])
                self.assertEqual(boundary["missing_input_fields"], ["code", "price", "quantity"])
                self.assertEqual(boundary["input_coverage_status"], "missing_required_inputs")
                mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_sell_submit_once_bundle_ignores_top_level_side_override(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--bundle",
                "sell-submit-once-pingan-complete-review",
                "--side",
                "buy",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--view",
                "summary",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        first_step = output_payload["steps"][0]
        self.assertEqual(first_step["entry"], "task-sell-submit-once")
        boundary = first_step["trade_plan_boundary"]
        self.assertEqual(boundary["trade_command"], "trade-submit-once")
        self.assertEqual(boundary["side"], "sell")
        self.assertEqual(boundary["provided_input_fields"], ["side", "port", "code", "price", "quantity"])
        self.assertEqual(output_payload["constraints"]["dispatch_executed"], False)
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_submit_once_bundle_plan_and_preview_expose_boundary_rollup(self) -> None:
        parser = build_parser()
        cases = [
            ("buy-submit-once-pingan-complete-review", "buy", "task-buy-submit-once"),
            ("sell-submit-once-pingan-complete-review", "sell", "task-sell-submit-once"),
        ]
        for bundle_name, expected_side, expected_entry in cases:
            for catalog_command in ("plan", "preview"):
                with self.subTest(bundle_name=bundle_name, catalog_command=catalog_command):
                    args = parser.parse_args(
                        [
                            "catalog",
                            catalog_command,
                            "--bundle",
                            bundle_name,
                            "--view",
                            "summary",
                        ]
                    )
                    with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
                        result = _handle_catalog_subcommand(args)
                    output_payload = _select_catalog_output_payload(args, result)
                    self.assertTrue(result.ok)
                    self.assertEqual(output_payload["trade_plan_boundary_step_count"], 1)
                    self.assertEqual(output_payload["trade_plan_boundary_sides"], [expected_side])
                    self.assertEqual(output_payload["plan_summary"]["trade_plan_boundary_step_count"], 1)
                    self.assertEqual(
                        output_payload["plan_summary"]["trade_plan_boundary_sides"],
                        [expected_side],
                    )
                    first_step = output_payload["steps"][0]
                    self.assertEqual(first_step["entry"], expected_entry)
                    self.assertEqual(first_step["trade_plan_boundary"]["side"], expected_side)
                    self.assertEqual(output_payload["constraints"]["dispatch_executed"], False)
                    mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_trade_health_summary_exposes_readiness_boundary(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--entry", "trade-health-pingan-readiness", "--view", "summary"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        self.assertEqual(output_payload["dispatch"]["command_group"], "trade")
        self.assertEqual(output_payload["dispatch"]["command_name"], "health")
        boundary = output_payload["trade_plan_boundary"]
        self.assertEqual(boundary["trade_command"], "health")
        self.assertEqual(boundary["input_kind"], "desktop_health_readiness")
        self.assertEqual(boundary["execution_mode"], "non_executing_catalog_plan")
        self.assertEqual(boundary["dispatch_executed"], False)
        self.assertEqual(boundary["required_input_fields"], ["port"])
        self.assertEqual(boundary["provided_input_fields"], ["port"])
        self.assertEqual(boundary["missing_input_fields"], [])
        self.assertEqual(boundary["input_coverage_status"], "complete")
        self.assertEqual(output_payload["constraints"]["execution_mode"], "non_executing")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_confirm_current_summary_marks_no_required_inputs(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--entry", "task-confirm-current", "--view", "summary"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        boundary = output_payload["trade_plan_boundary"]
        self.assertEqual(boundary["trade_command"], "trade-confirm-current")
        self.assertEqual(boundary["required_input_fields"], [])
        self.assertEqual(boundary["provided_input_fields"], [])
        self.assertEqual(boundary["missing_input_fields"], [])
        self.assertEqual(boundary["required_input_count"], 0)
        self.assertEqual(boundary["provided_input_count"], 0)
        self.assertEqual(boundary["missing_input_count"], 0)
        self.assertEqual(boundary["input_coverage_status"], "no_required_inputs")
        self.assertEqual(boundary["dispatch_executed"], False)
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_sell_followup_bundle_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--bundle",
                "sell-pingan-exception-review",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "sell-pingan-exception-review")
        self.assertEqual([step["name"] for step in result.data["steps"]], ["trade", "audit"])
        self.assertEqual(
            [step["dispatch"]["command_group"] for step in result.data["steps"]],
            ["task", "report"],
        )
        self.assertEqual(result.data["steps"][0]["entry"], "task-sell")
        self.assertEqual(result.data["steps"][0]["dispatch"]["command_name"], "trade-sell")
        self.assertEqual(result.data["steps"][1]["entry"], "audit-daily-pingan-sell-exceptions")
        self.assertEqual(result.data["steps"][1]["dispatch"]["command_name"], "audit-daily")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_sell_pingan_complete_bundle_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--bundle",
                "sell-pingan-complete-review",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "sell-pingan-complete-review")
        self.assertEqual(
            [step["entry"] for step in result.data["steps"]],
            ["task-sell", "daily-success", "audit-daily-pingan-confirmed"],
        )
        self.assertEqual(result.data["steps"][0]["dispatch"]["command_name"], "trade-sell")
        self.assertEqual(result.data["steps"][1]["dispatch"]["command_name"], "daily")
        self.assertEqual(result.data["steps"][2]["dispatch"]["command_name"], "audit-daily")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_sell_pingan_rejection_bundle_stays_available(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--bundle",
                "sell-pingan-rejection-review",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "sell-pingan-rejection-review")
        self.assertEqual(
            [step["entry"] for step in result.data["steps"]],
            ["task-sell", "audit-daily-pingan-sell-rejected"],
        )
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_sell_submit_once_entry_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--entry",
                "task-sell-submit-once",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_entry"]["name"], "task-sell-submit-once")
        self.assertEqual(result.data["dispatch"]["command_group"], "task")
        self.assertEqual(result.data["dispatch"]["command_name"], "trade-submit-once")
        self.assertEqual(result.data["resolved_args"]["task_command"], "trade-submit-once")
        self.assertEqual(result.data["resolved_args"]["side"], "sell")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_buy_submit_once_entry_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--entry",
                "task-buy-submit-once",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_entry"]["name"], "task-buy-submit-once")
        self.assertEqual(result.data["dispatch"]["command_group"], "task")
        self.assertEqual(result.data["dispatch"]["command_name"], "trade-submit-once")
        self.assertEqual(result.data["resolved_args"]["task_command"], "trade-submit-once")
        self.assertEqual(result.data["resolved_args"]["side"], "buy")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_sell_submit_once_summary_exposes_side_boundary(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--entry",
                "task-sell-submit-once",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--view",
                "summary",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        boundary = output_payload["trade_plan_boundary"]
        self.assertEqual(boundary["trade_command"], "trade-submit-once")
        self.assertEqual(boundary["side"], "sell")
        self.assertEqual(boundary["input_kind"], "submit_once_order")
        self.assertEqual(boundary["required_input_fields"], ["side", "port", "code", "price", "quantity"])
        self.assertEqual(boundary["provided_input_fields"], ["side", "port", "code", "price", "quantity"])
        self.assertEqual(boundary["missing_input_fields"], [])
        self.assertEqual(boundary["required_input_count"], 5)
        self.assertEqual(boundary["provided_input_count"], 5)
        self.assertEqual(boundary["missing_input_count"], 0)
        self.assertEqual(boundary["input_coverage_status"], "complete")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_sell_submit_once_bundle_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--bundle",
                "sell-submit-once-pingan-exception-review",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "sell-submit-once-pingan-exception-review")
        self.assertEqual([step["entry"] for step in result.data["steps"]], ["task-sell-submit-once", "audit-daily-pingan-sell-submit-once-exceptions"])
        self.assertEqual(result.data["steps"][0]["dispatch"]["command_name"], "trade-submit-once")
        self.assertEqual(result.data["steps"][0]["resolved_args"]["side"], "sell")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_sell_submit_once_pingan_complete_bundle_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--bundle",
                "sell-submit-once-pingan-complete-review",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "sell-submit-once-pingan-complete-review")
        self.assertEqual(
            [step["entry"] for step in result.data["steps"]],
            ["task-sell-submit-once", "daily-success", "audit-daily-pingan-confirmed"],
        )
        self.assertEqual(result.data["steps"][0]["dispatch"]["command_name"], "trade-submit-once")
        self.assertEqual(result.data["steps"][0]["resolved_args"]["side"], "sell")
        self.assertEqual(result.data["steps"][1]["dispatch"]["command_name"], "daily")
        self.assertEqual(result.data["steps"][2]["dispatch"]["command_name"], "audit-daily")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_sell_submit_once_pingan_rejection_bundle_stays_available(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--bundle",
                "sell-submit-once-pingan-rejection-review",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "sell-submit-once-pingan-rejection-review")
        self.assertEqual(
            [step["entry"] for step in result.data["steps"]],
            ["task-sell-submit-once", "audit-daily-pingan-sell-submit-once-rejected"],
        )
        self.assertEqual(result.data["steps"][0]["resolved_args"]["side"], "sell")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_buy_submit_once_bundle_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--bundle",
                "buy-submit-once-pingan-exception-review",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "buy-submit-once-pingan-exception-review")
        self.assertEqual(
            [step["entry"] for step in result.data["steps"]],
            ["task-buy-submit-once", "audit-daily-pingan-submit-once-exceptions"],
        )
        self.assertEqual(result.data["steps"][0]["dispatch"]["command_name"], "trade-submit-once")
        self.assertEqual(result.data["steps"][0]["resolved_args"]["side"], "buy")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_buy_submit_once_complete_bundle_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--bundle",
                "buy-submit-once-pingan-complete-review",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "buy-submit-once-pingan-complete-review")
        self.assertEqual(
            [step["entry"] for step in result.data["steps"]],
            ["task-buy-submit-once", "daily-success", "audit-daily-pingan-confirmed"],
        )
        self.assertEqual(result.data["steps"][0]["dispatch"]["command_name"], "trade-submit-once")
        self.assertEqual(result.data["steps"][0]["resolved_args"]["side"], "buy")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_submit_once_bundle_summary_marks_only_trade_steps(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--bundle",
                "buy-submit-once-pingan-complete-review",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--view",
                "summary",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        self.assertEqual(output_payload["selected_step_count"], 3)
        trade_boundary = output_payload["steps"][0]["trade_plan_boundary"]
        self.assertEqual(trade_boundary["trade_command"], "trade-submit-once")
        self.assertEqual(trade_boundary["side"], "buy")
        self.assertEqual(trade_boundary["execution_mode"], "non_executing_catalog_plan")
        self.assertEqual(trade_boundary["dispatch_executed"], False)
        self.assertEqual(trade_boundary["required_input_count"], 5)
        self.assertEqual(trade_boundary["provided_input_count"], 5)
        self.assertEqual(trade_boundary["missing_input_count"], 0)
        self.assertNotIn("trade_plan_boundary", output_payload["steps"][1])
        self.assertNotIn("trade_plan_boundary", output_payload["steps"][2])
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_generic_submit_once_complete_bundle_stays_available(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--bundle",
                "submit-once-pingan-complete-review",
                "--code",
                "000001.SZ",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "submit-once-pingan-complete-review")
        self.assertEqual(
            [step["entry"] for step in result.data["steps"]],
            ["task-submit-once", "daily-success", "audit-daily-pingan-confirmed"],
        )
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_preview_bundle_summary_view_is_reduced(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["catalog", "preview", "--bundle", "guarded-review-buy", "--only-step", "review", "--view", "summary"]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        self.assertEqual(output_payload["mode"], "preview")
        self.assertEqual(output_payload["target"]["type"], "bundle")
        self.assertEqual(output_payload["selected_step_count"], 1)
        self.assertEqual(output_payload["step_source_counts"], {"report": 1})
        self.assertEqual(output_payload["step_source_key_count"], 1)
        self.assertEqual(output_payload["step_name_counts"], {"review": 1})
        self.assertEqual(output_payload["step_name_key_count"], 1)
        self.assertEqual(output_payload["step_source_name_counts"], {"report:review": 1})
        self.assertEqual(output_payload["step_source_name_key_count"], 1)
        self.assertEqual(output_payload["step_entry_counts"], {"recent-ledger": 1})
        self.assertEqual(output_payload["step_entry_key_count"], 1)
        self.assertEqual(output_payload["step_source_entry_counts"], {"report:recent-ledger": 1})
        self.assertEqual(output_payload["step_source_entry_key_count"], 1)
        self.assertEqual(output_payload["step_resolved_arg_key_counts"], {"limit": 1, "profile": 1})
        self.assertEqual(output_payload["step_resolved_arg_key_count"], 2)
        self.assertEqual(
            output_payload["step_source_resolved_arg_key_counts"],
            {"report:limit": 1, "report:profile": 1},
        )
        self.assertEqual(output_payload["step_source_resolved_arg_key_count"], 2)
        self.assertEqual(output_payload["steps"][0]["name"], "review")
        self.assertNotIn("catalog_bundle", output_payload)
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_entry_summary_includes_provenance_and_constraints(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--entry", "daily-review", "--view", "summary"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["provenance"]["mode"], "plan")
        self.assertEqual(result.data["provenance"]["target_type"], "entry")
        self.assertEqual(result.data["provenance"]["target_name"], "daily-review")
        self.assertTrue(result.data["provenance"]["catalog_path"].endswith("runtime/command-catalog.json"))
        self.assertEqual(result.data["constraints"]["execution_mode"], "non_executing")
        self.assertFalse(result.data["constraints"]["dispatch_executed"])
        self.assertEqual(output_payload["provenance"]["target_name"], "daily-review")
        self.assertEqual(output_payload["constraints"]["execution_mode"], "non_executing")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_preview_bundle_summary_includes_provenance_and_constraints(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["catalog", "preview", "--bundle", "guarded-review-buy", "--only-step", "review", "--view", "summary"]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        self.assertEqual(output_payload["provenance"]["mode"], "preview")
        self.assertEqual(output_payload["provenance"]["target_type"], "bundle")
        self.assertEqual(output_payload["provenance"]["target_name"], "guarded-review-buy")
        self.assertTrue(output_payload["provenance"]["catalog_path"].endswith("runtime/command-catalog.json"))
        self.assertTrue(output_payload["provenance"]["bundle_path"].endswith("runtime/command-bundles.json"))
        self.assertEqual(output_payload["constraints"]["execution_mode"], "non_executing")
        self.assertFalse(output_payload["constraints"]["dispatch_executed"])
        self.assertFalse(output_payload["constraints"]["schema_mutation"])
        self.assertFalse(output_payload["constraints"]["run_semantics_changed"])
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_read_zxg_review_bundle_returns_resolved_steps(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--bundle", "read-zxg-review"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "read-zxg-review")
        self.assertEqual(result.data["catalog_bundle"]["selected_step_count"], 2)
        self.assertEqual(result.data["steps"][0]["entry"], "read-zxg-watchlist")
        self.assertEqual(result.data["steps"][1]["entry"], "read-zxg-full")
        self.assertEqual(result.data["steps"][0]["resolved_args"]["block_code"], "ZXG")
        self.assertEqual(result.data["steps"][1]["resolved_args"]["block_code"], "ZXG")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_broker_capabilities_entry_without_execution(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--entry", "broker-capabilities", "--view", "summary"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        output_payload = _select_catalog_output_payload(args, result)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_entry"]["source"], "trade")
        self.assertEqual(result.data["catalog_entry"]["preset"], "broker-capabilities-default")
        self.assertEqual(result.data["dispatch"]["command_name"], "broker-capabilities")
        self.assertEqual(result.data["resolved_args"]["broker"], "pingan_desktop")
        self.assertEqual(output_payload["target"]["name"], "broker-capabilities")
        self.assertEqual(output_payload["resolved_args"]["broker"], "pingan_desktop")
        self.assertFalse(output_payload["constraints"]["dispatch_executed"])
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_read_zxg_review_and_export_bundle_returns_resolved_steps(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--bundle", "read-zxg-review-and-export"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["catalog_bundle"]["name"], "read-zxg-review-and-export")
        self.assertEqual(result.data["catalog_bundle"]["selected_step_count"], 3)
        self.assertEqual(result.data["steps"][0]["entry"], "read-zxg-watchlist")
        self.assertEqual(result.data["steps"][1]["entry"], "read-zxg-full")
        self.assertEqual(result.data["steps"][2]["entry"], "export-zxg-watchlist")
        self.assertEqual(result.data["steps"][0]["resolved_args"]["block_code"], "ZXG")
        self.assertEqual(result.data["steps"][1]["resolved_args"]["block_code"], "ZXG")
        self.assertEqual(result.data["steps"][2]["resolved_args"]["block_code"], "ZXG")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_read_zxg_review_bundle_applies_block_code_override_to_both_steps(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "plan", "--bundle", "read-zxg-review", "--block-code", "MYZXG", "--view", "summary"])
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["steps"][0]["resolved_args"]["block_code"], "MYZXG")
        self.assertEqual(result.data["steps"][1]["resolved_args"]["block_code"], "MYZXG")
        self.assertEqual(result.data["summary_view"]["steps"][0]["resolved_args"]["block_code"], "MYZXG")
        self.assertEqual(result.data["summary_view"]["steps"][1]["resolved_args"]["block_code"], "MYZXG")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_sell_submit_once_pingan_review_preserves_sell_side(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "plan",
                "--bundle",
                "sell-submit-once-pingan-exception-review",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--view",
                "summary",
            ]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["steps"][0]["entry"], "task-sell-submit-once")
        self.assertEqual(result.data["steps"][0]["resolved_args"]["side"], "sell")
        self.assertEqual(result.data["steps"][1]["entry"], "audit-daily-pingan-sell-submit-once-exceptions")
        self.assertEqual(result.data["summary_view"]["steps"][0]["resolved_args"]["side"], "sell")
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_plan_read_zxg_review_and_export_bundle_applies_block_code_override(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["catalog", "plan", "--bundle", "read-zxg-review-and-export", "--block-code", "MYZXG", "--view", "summary"]
        )
        with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["steps"][0]["resolved_args"]["block_code"], "MYZXG")
        self.assertEqual(result.data["steps"][1]["resolved_args"]["block_code"], "MYZXG")
        self.assertEqual(result.data["steps"][2]["resolved_args"]["block_code"], "MYZXG")
        self.assertEqual(result.data["steps"][2]["resolved_args"]["export_output"], "runtime/exports/zxg.json")
        self.assertEqual(result.data["summary_view"]["steps"][0]["resolved_args"]["block_code"], "MYZXG")
        self.assertEqual(result.data["summary_view"]["steps"][1]["resolved_args"]["block_code"], "MYZXG")
        self.assertEqual(result.data["summary_view"]["steps"][2]["resolved_args"]["block_code"], "MYZXG")
        self.assertNotIn("export_output", result.data["summary_view"]["steps"][2]["resolved_args"])
        mocked_dispatch.assert_not_called()

    def test_handle_catalog_bundle_dispatches_steps_sequentially(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "catalog",
                "run",
                "--bundle",
                "guarded-review-buy",
                "--port",
                "COM9",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--output",
                "bundle.json",
            ]
        )
        bundle = {
            "description": "Guarded trade then report",
            "steps": [
                {
                    "index": 1,
                    "name": "trade",
                    "entry": "guarded-buy",
                    "source": "task",
                    "preset": "guarded-default",
                    "description": "",
                    "options": {"port": "COM3"},
                },
                {
                    "index": 2,
                    "name": "review",
                    "entry": "recent-ledger",
                    "source": "report",
                    "preset": "recent-ledger",
                    "description": "",
                    "options": {"limit": 5},
                },
            ],
        }
        step_results = [
            Result(ok=True, code=ErrorCode.OK, message="trade-ok"),
            Result(ok=True, code=ErrorCode.OK, message="report-ok"),
        ]
        with patch("tdxquant.cli.resolve_command_bundle", return_value=bundle), patch(
            "tdxquant.cli._dispatch_catalog_resolved_entry",
            side_effect=step_results,
        ) as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(mocked_dispatch.call_count, 2)
        first_args = mocked_dispatch.call_args_list[0].kwargs["args"]
        second_args = mocked_dispatch.call_args_list[1].kwargs["args"]
        self.assertEqual(first_args.port, "COM9")
        self.assertIsNone(first_args.output)
        self.assertEqual(second_args.limit, 5)
        self.assertEqual(result.data["catalog_bundle"]["name"], "guarded-review-buy")
        self.assertEqual(len(result.data["catalog_bundle"]["steps"]), 2)
        self.assertEqual(result.data["catalog_bundle"]["selected_step_count"], 2)

    def test_handle_catalog_bundle_stops_after_failed_step(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--bundle", "guarded-review-buy"])
        bundle = {
            "description": "Guarded trade then report",
            "steps": [
                {"index": 1, "name": "trade", "entry": "guarded-buy", "source": "task", "preset": "guarded-default", "description": "", "options": {}},
                {"index": 2, "name": "review", "entry": "recent-ledger", "source": "report", "preset": "recent-ledger", "description": "", "options": {}},
            ],
        }
        with patch("tdxquant.cli.resolve_command_bundle", return_value=bundle), patch(
            "tdxquant.cli._dispatch_catalog_resolved_entry",
            side_effect=[Result(ok=False, code=ErrorCode.EXECUTION_FAILED, message="trade-failed")],
        ) as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertFalse(result.ok)
        self.assertEqual(mocked_dispatch.call_count, 1)
        self.assertEqual(result.data["catalog_bundle"]["failed_step"]["entry"], "guarded-buy")

    def test_handle_catalog_read_zxg_review_bundle_dispatches_steps_sequentially(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--bundle", "read-zxg-review"])
        bundle = {
            "description": "snapshot then full",
            "steps": [
                {"index": 1, "name": "snapshot", "entry": "read-zxg-watchlist", "source": "task", "preset": "read-zxg-watchlist", "description": "", "options": {}},
                {"index": 2, "name": "full", "entry": "read-zxg-full", "source": "task", "preset": "read-zxg-full", "description": "", "options": {}},
            ],
        }
        with patch("tdxquant.cli.resolve_command_bundle", return_value=bundle), patch(
            "tdxquant.cli._dispatch_catalog_resolved_entry",
            side_effect=[Result(ok=True, code=ErrorCode.OK, message="snapshot-ok"), Result(ok=True, code=ErrorCode.OK, message="full-ok")],
        ) as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(mocked_dispatch.call_count, 2)
        self.assertEqual(result.data["catalog_bundle"]["name"], "read-zxg-review")
        self.assertEqual(result.data["catalog_bundle"]["selected_step_count"], 2)

    def test_handle_catalog_read_zxg_review_bundle_applies_block_code_override_to_both_steps(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--bundle", "read-zxg-review", "--block-code", "MYZXG"])
        bundle = {
            "description": "snapshot then full",
            "steps": [
                {"index": 1, "name": "snapshot", "entry": "read-zxg-watchlist", "source": "task", "preset": "read-zxg-watchlist", "description": "", "options": {}},
                {"index": 2, "name": "full", "entry": "read-zxg-full", "source": "task", "preset": "read-zxg-full", "description": "", "options": {}},
            ],
        }
        with patch("tdxquant.cli.resolve_command_bundle", return_value=bundle), patch(
            "tdxquant.cli._dispatch_catalog_resolved_entry",
            side_effect=[Result(ok=True, code=ErrorCode.OK, message="snapshot-ok"), Result(ok=True, code=ErrorCode.OK, message="full-ok")],
        ) as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(mocked_dispatch.call_count, 2)
        first_args = mocked_dispatch.call_args_list[0].kwargs["args"]
        second_args = mocked_dispatch.call_args_list[1].kwargs["args"]
        self.assertEqual(first_args.block_code, "MYZXG")
        self.assertEqual(second_args.block_code, "MYZXG")

    def test_handle_catalog_read_zxg_review_bundle_stops_after_snapshot_failure(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--bundle", "read-zxg-review"])
        bundle = {
            "description": "snapshot then full",
            "steps": [
                {"index": 1, "name": "snapshot", "entry": "read-zxg-watchlist", "source": "task", "preset": "read-zxg-watchlist", "description": "", "options": {}},
                {"index": 2, "name": "full", "entry": "read-zxg-full", "source": "task", "preset": "read-zxg-full", "description": "", "options": {}},
            ],
        }
        with patch("tdxquant.cli.resolve_command_bundle", return_value=bundle), patch(
            "tdxquant.cli._dispatch_catalog_resolved_entry",
            side_effect=[Result(ok=False, code=ErrorCode.EXECUTION_FAILED, message="snapshot-failed")],
        ) as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertFalse(result.ok)
        self.assertEqual(mocked_dispatch.call_count, 1)
        self.assertEqual(result.data["catalog_bundle"]["failed_step"]["entry"], "read-zxg-watchlist")

    def test_handle_catalog_read_zxg_review_and_export_bundle_dispatches_steps_sequentially(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--bundle", "read-zxg-review-and-export"])
        bundle = {
            "description": "snapshot then full then export",
            "steps": [
                {"index": 1, "name": "snapshot", "entry": "read-zxg-watchlist", "source": "task", "preset": "read-zxg-watchlist", "description": "", "options": {}},
                {"index": 2, "name": "full", "entry": "read-zxg-full", "source": "task", "preset": "read-zxg-full", "description": "", "options": {}},
                {"index": 3, "name": "export", "entry": "export-zxg-watchlist", "source": "task", "preset": "export-zxg-watchlist", "description": "", "options": {}},
            ],
        }
        with patch("tdxquant.cli.resolve_command_bundle", return_value=bundle), patch(
            "tdxquant.cli._dispatch_catalog_resolved_entry",
            side_effect=[
                Result(ok=True, code=ErrorCode.OK, message="snapshot-ok"),
                Result(ok=True, code=ErrorCode.OK, message="full-ok"),
                Result(ok=True, code=ErrorCode.OK, message="export-ok"),
            ],
        ) as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(mocked_dispatch.call_count, 3)
        self.assertEqual(mocked_dispatch.call_args_list[0].kwargs["entry_name"], "read-zxg-watchlist")
        self.assertEqual(mocked_dispatch.call_args_list[1].kwargs["entry_name"], "read-zxg-full")
        self.assertEqual(mocked_dispatch.call_args_list[2].kwargs["entry_name"], "export-zxg-watchlist")
        self.assertEqual(result.data["catalog_bundle"]["name"], "read-zxg-review-and-export")
        self.assertEqual(result.data["catalog_bundle"]["selected_step_count"], 3)

    def test_handle_catalog_read_zxg_review_and_export_bundle_applies_block_code_override_to_all_steps(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--bundle", "read-zxg-review-and-export", "--block-code", "MYZXG"])
        bundle = {
            "description": "snapshot then full then export",
            "steps": [
                {"index": 1, "name": "snapshot", "entry": "read-zxg-watchlist", "source": "task", "preset": "read-zxg-watchlist", "description": "", "options": {}},
                {"index": 2, "name": "full", "entry": "read-zxg-full", "source": "task", "preset": "read-zxg-full", "description": "", "options": {}},
                {"index": 3, "name": "export", "entry": "export-zxg-watchlist", "source": "task", "preset": "export-zxg-watchlist", "description": "", "options": {}},
            ],
        }
        with patch("tdxquant.cli.resolve_command_bundle", return_value=bundle), patch(
            "tdxquant.cli._dispatch_catalog_resolved_entry",
            side_effect=[
                Result(ok=True, code=ErrorCode.OK, message="snapshot-ok"),
                Result(ok=True, code=ErrorCode.OK, message="full-ok"),
                Result(ok=True, code=ErrorCode.OK, message="export-ok"),
            ],
        ) as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(mocked_dispatch.call_count, 3)
        self.assertEqual(mocked_dispatch.call_args_list[0].kwargs["entry_name"], "read-zxg-watchlist")
        self.assertEqual(mocked_dispatch.call_args_list[1].kwargs["entry_name"], "read-zxg-full")
        self.assertEqual(mocked_dispatch.call_args_list[2].kwargs["entry_name"], "export-zxg-watchlist")
        first_args = mocked_dispatch.call_args_list[0].kwargs["args"]
        second_args = mocked_dispatch.call_args_list[1].kwargs["args"]
        third_args = mocked_dispatch.call_args_list[2].kwargs["args"]
        self.assertEqual(first_args.block_code, "MYZXG")
        self.assertEqual(second_args.block_code, "MYZXG")
        self.assertEqual(third_args.block_code, "MYZXG")

    def test_handle_catalog_read_zxg_review_and_export_bundle_stops_before_export_when_full_step_fails(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--bundle", "read-zxg-review-and-export"])
        bundle = {
            "description": "snapshot then full then export",
            "steps": [
                {"index": 1, "name": "snapshot", "entry": "read-zxg-watchlist", "source": "task", "preset": "read-zxg-watchlist", "description": "", "options": {}},
                {"index": 2, "name": "full", "entry": "read-zxg-full", "source": "task", "preset": "read-zxg-full", "description": "", "options": {}},
                {"index": 3, "name": "export", "entry": "export-zxg-watchlist", "source": "task", "preset": "export-zxg-watchlist", "description": "", "options": {}},
            ],
        }
        with patch("tdxquant.cli.resolve_command_bundle", return_value=bundle), patch(
            "tdxquant.cli._dispatch_catalog_resolved_entry",
            side_effect=[
                Result(ok=True, code=ErrorCode.OK, message="snapshot-ok"),
                Result(ok=False, code=ErrorCode.EXECUTION_FAILED, message="full-failed"),
            ],
        ) as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertFalse(result.ok)
        self.assertEqual(mocked_dispatch.call_count, 2)
        self.assertEqual(result.data["catalog_bundle"]["failed_step"]["entry"], "read-zxg-full")

    def test_handle_catalog_read_zxg_review_and_export_bundle_stops_at_export_failure(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--bundle", "read-zxg-review-and-export"])
        bundle = {
            "description": "snapshot then full then export",
            "steps": [
                {"index": 1, "name": "snapshot", "entry": "read-zxg-watchlist", "source": "task", "preset": "read-zxg-watchlist", "description": "", "options": {}},
                {"index": 2, "name": "full", "entry": "read-zxg-full", "source": "task", "preset": "read-zxg-full", "description": "", "options": {}},
                {"index": 3, "name": "export", "entry": "export-zxg-watchlist", "source": "task", "preset": "export-zxg-watchlist", "description": "", "options": {}},
            ],
        }
        with patch("tdxquant.cli.resolve_command_bundle", return_value=bundle), patch(
            "tdxquant.cli._dispatch_catalog_resolved_entry",
            side_effect=[
                Result(ok=True, code=ErrorCode.OK, message="snapshot-ok"),
                Result(ok=True, code=ErrorCode.OK, message="full-ok"),
                Result(ok=False, code=ErrorCode.EXECUTION_FAILED, message="export-failed"),
            ],
        ) as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertFalse(result.ok)
        self.assertEqual(mocked_dispatch.call_count, 3)
        self.assertEqual(result.data["catalog_bundle"]["failed_step"]["entry"], "export-zxg-watchlist")

    def test_handle_catalog_bundle_only_step_executes_selected_step(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--bundle", "guarded-review-buy", "--only-step", "review"])
        bundle = {
            "description": "Guarded trade then report",
            "steps": [
                {"index": 1, "name": "trade", "entry": "guarded-buy", "source": "task", "preset": "guarded-default", "description": "", "options": {}},
                {"index": 2, "name": "review", "entry": "recent-ledger", "source": "report", "preset": "recent-ledger", "description": "", "options": {"limit": 5}},
            ],
        }
        with patch("tdxquant.cli.resolve_command_bundle", return_value=bundle), patch(
            "tdxquant.cli._dispatch_catalog_resolved_entry",
            return_value=Result(ok=True, code=ErrorCode.OK, message="report-ok"),
        ) as mocked_dispatch:
            result = _handle_catalog_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(mocked_dispatch.call_count, 1)
        dispatched_args = mocked_dispatch.call_args.kwargs
        self.assertEqual(dispatched_args["entry_name"], "recent-ledger")
        self.assertEqual(result.data["catalog_bundle"]["selected_from_step"], "review")
        self.assertEqual(result.data["catalog_bundle"]["selected_to_step"], "review")
        self.assertEqual(result.data["catalog_bundle"]["selected_step_count"], 1)

    def test_handle_catalog_bundle_rejects_invalid_step_range(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["catalog", "run", "--bundle", "guarded-review-buy", "--from-step", "review", "--to-step", "trade"])
        bundle = {
            "description": "Guarded trade then report",
            "steps": [
                {"index": 1, "name": "trade", "entry": "guarded-buy", "source": "task", "preset": "guarded-default", "description": "", "options": {}},
                {"index": 2, "name": "review", "entry": "recent-ledger", "source": "report", "preset": "recent-ledger", "description": "", "options": {"limit": 5}},
            ],
        }
        with patch("tdxquant.cli.resolve_command_bundle", return_value=bundle):
            result = _handle_catalog_subcommand(args)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)

    def test_handle_api_formula_set_data_reads_json_file(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as temp_dir:
            data_path = Path(temp_dir) / "stock-data.json"
            data_path.write_text(json.dumps([{"close": 1.0}]), encoding="utf-8")
            args = parser.parse_args(
                [
                    "api",
                    "formula-set-data",
                    "--code",
                    "000001",
                    "--stock-data-file",
                    str(data_path),
                    "--count",
                    "1",
                ]
            )
            expected = Result(ok=True, code=ErrorCode.OK, message="ok")
            manager = MagicMock()
            manager.formula.set_data.return_value = expected
            with patch("tdxquant.cli.TdxApiManager", return_value=manager):
                result = _handle_api_subcommand(args)
        self.assertIs(result, expected)
        manager.formula.set_data.assert_called_once_with(
            stock_code="000001",
            stock_period="1d",
            stock_data=[{"close": 1.0}],
            count=1,
            dividend_type=0,
        )


class TaskCliDispatchTests(unittest.TestCase):
    def test_handle_task_presets_lists_available_presets(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "presets"])
        with patch(
            "tdxquant.cli.load_task_presets",
            return_value={
                "guarded-default": {
                    "command": "guarded-trade-buy",
                    "description": "guarded trade",
                    "profile": "guarded_trade_buy",
                    "options": {"port": "COM3"},
                },
                "refresh-default": {
                    "command": "refresh-environment",
                    "description": "refresh",
                    "profile": "maintenance",
                    "options": {"market": "AG"},
                },
            },
        ):
            result = _handle_task_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["preset_count"], 2)
        self.assertEqual(result.data["presets"][0]["name"], "guarded-default")

    def test_handle_task_presets_lists_export_watchlist_preset(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "presets"])
        with patch(
            "tdxquant.cli.load_task_presets",
            return_value={
                "export-zxg-watchlist": {
                    "command": "block-read-watchlist-export",
                    "description": "export zxg snapshot",
                    "profile": "default",
                    "api_profile": "safe_read",
                    "options": {
                        "block_code": "ZXG",
                        "export_output": "runtime/exports/zxg.json",
                        "overwrite": False,
                    },
                }
            },
        ):
            result = _handle_task_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["preset_count"], 1)
        self.assertEqual(result.data["presets"][0]["name"], "export-zxg-watchlist")
        self.assertEqual(result.data["presets"][0]["command"], "block-read-watchlist-export")

    def test_handle_task_presets_lists_block_read_full_preset(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "presets"])
        with patch(
            "tdxquant.cli.load_task_presets",
            return_value={
                "read-zxg-full": {
                    "command": "block-read-full",
                    "description": "read zxg diagnostics",
                    "options": {"block_code": "ZXG"},
                }
            },
        ):
            result = _handle_task_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["preset_count"], 1)
        self.assertEqual(result.data["presets"][0]["name"], "read-zxg-full")
        self.assertEqual(result.data["presets"][0]["command"], "block-read-full")
        self.assertEqual(result.data["presets"][0]["profile"], "default")

    def test_handle_task_presets_lists_block_read_watchlist_preset(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "presets"])
        with patch(
            "tdxquant.cli.load_task_presets",
            return_value={
                "read-zxg-watchlist": {
                    "command": "block-read-watchlist",
                    "description": "read zxg watchlist snapshot",
                    "options": {"block_code": "ZXG"},
                }
            },
        ):
            result = _handle_task_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["preset_count"], 1)
        self.assertEqual(result.data["presets"][0]["name"], "read-zxg-watchlist")
        self.assertEqual(result.data["presets"][0]["command"], "block-read-watchlist")
        self.assertEqual(result.data["presets"][0]["profile"], "default")
        self.assertEqual(result.data["presets"][0]["options"]["block_code"], "ZXG")

    def test_handle_task_run_uses_guarded_preset_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["task", "run", "--preset", "guarded-default", "--code", "000001", "--price", "10.00", "--quantity", "100"]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.guarded_trade_buy.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_task_preset",
                return_value={
                    "command": "guarded-trade-buy",
                    "profile": "guarded_trade_buy",
                    "api_profile": "safe_read",
                    "trade_profile": "balanced",
                    "strategy_path": None,
                    "options": {
                        "port": "COM3",
                        "timeout": 2.0,
                        "max_depth": 12,
                        "close_result_dialog": True,
                        "submission_key": "preset-submission-key",
                        "max_price": 10.45,
                        "required_block_code": "ZXG",
                        "max_snapshot_price": 10.50,
                    },
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager) as mocked_manager,
        ):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="guarded_trade_buy",
            api_profile="safe_read",
            trade_profile="balanced",
            strategy_path=None,
            title_keyword="平安证券",
            exe_path=None,
        )
        manager.guarded_trade_buy.assert_called_once_with(
            port="COM3",
            baudrate=115200,
            timeout=2.0,
            code="000001",
            price="10.00",
            quantity=100,
            max_depth=12,
            close_result_dialog=True,
            submission_key="preset-submission-key",
            max_price=10.45,
            refresh_before_trade=None,
            refresh_market=None,
            refresh_force=None,
            max_snapshot_price=10.50,
            required_block_code="ZXG",
            required_block_type=0,
            required_list_type=None,
            formula_name=None,
            formula_arg="",
            formula_return_count=1,
            formula_return_date=False,
            formula_stock_period="1d",
            formula_start_time="",
            formula_end_time="",
            formula_count=0,
            formula_dividend_type=0,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_task_run_prefers_explicit_cli_overrides(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "run",
                "--preset",
                "guarded-default",
                "--port",
                "COM9",
                "--profile",
                "trade_buy",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--submission-key",
                "cli-submission-key",
                "--max-price",
                "10.20",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.guarded_trade_buy.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_task_preset",
                return_value={
                    "command": "guarded-trade-buy",
                    "profile": "guarded_trade_buy",
                    "api_profile": "safe_read",
                    "trade_profile": "balanced",
                    "strategy_path": None,
                    "options": {"port": "COM3", "submission_key": "preset-submission-key", "max_price": 10.60},
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.guarded_trade_buy.assert_called_once()
        self.assertEqual(manager.guarded_trade_buy.call_args.kwargs["port"], "COM9")
        self.assertEqual(manager.guarded_trade_buy.call_args.kwargs["submission_key"], "cli-submission-key")
        self.assertEqual(manager.guarded_trade_buy.call_args.kwargs["max_price"], 10.20)

    def test_handle_task_run_uses_refresh_preset(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "run", "--preset", "refresh-default"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.refresh_environment.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_task_preset",
                return_value={
                    "command": "refresh-environment",
                    "profile": "maintenance",
                    "api_profile": "safe_read",
                    "trade_profile": None,
                    "strategy_path": None,
                    "options": {"market": "AG", "force": True},
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.refresh_environment.assert_called_once_with(market="AG", force=True)

    def test_handle_task_run_uses_submit_ready_preset_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "run", "--preset", "submit-ready-default"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_submit_ready.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_task_preset",
                return_value={
                    "command": "trade-submit-ready",
                    "profile": "trade_submit_ready",
                    "api_profile": "safe_read",
                    "trade_profile": "balanced",
                    "strategy_path": None,
                    "options": {
                        "port": "COM3",
                        "code": "000001",
                        "price": "10.00",
                        "quantity": 100,
                        "max_price": 10.20,
                        "dialog_lookup_mode": "win32_experimental",
                        "confirm_timeout": 2.5,
                        "refresh_before_trade": True,
                    },
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_submit_ready.assert_called_once_with(
            port="COM3",
            baudrate=115200,
            timeout=2.0,
            code="000001",
            price="10.00",
            quantity=100,
            max_depth=12,
            max_price=10.20,
            refresh_before_trade=True,
            refresh_market=None,
            refresh_force=None,
            dialog_lookup_mode="win32_experimental",
            confirm_timeout=2.5,
        )

    def test_handle_task_run_uses_confirm_current_preset_without_order_fields(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "run", "--preset", "confirm-current-default", "--result-timeout", "4.0"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_confirm_current.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_task_preset",
                return_value={
                    "command": "trade-confirm-current",
                    "profile": "trade_confirm_current",
                    "api_profile": "safe_read",
                    "trade_profile": "balanced",
                    "strategy_path": None,
                    "options": {
                        "dialog_lookup_mode": "win32_experimental",
                        "confirm_timeout": 2.0,
                        "result_timeout": 3.0,
                        "close_result_dialog": False,
                    },
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_confirm_current.assert_called_once_with(
            dialog_lookup_mode="win32_experimental",
            confirm_timeout=2.0,
            result_timeout=4.0,
            close_result_dialog=False,
            result_close_pre_delay=None,
        )

    def test_handle_task_run_rejects_unsupported_preset_command(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "run", "--preset", "bad"])
        with patch(
            "tdxquant.cli.resolve_task_preset",
            return_value={
                "command": "watchlist-overview",
                "profile": "watchlist_overview",
                "api_profile": "brief",
                "trade_profile": None,
                "strategy_path": None,
                "options": {},
            },
        ):
            result = _handle_task_subcommand(args)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)

    def test_task_run_parser_accepts_block_code_override(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "run", "--preset", "read-zxg-full", "--block-code", "ZXG"])
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "run")
        self.assertEqual(args.preset, "read-zxg-full")
        self.assertEqual(args.block_code, "ZXG")

    def test_task_run_parser_accepts_watchlist_import_input_override(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "run",
                "--preset",
                "plan-zxg-watchlist-import",
                "--input",
                "runtime/watchlist-imports/custom.json",
            ]
        )
        self.assertEqual(args.command, "task")
        self.assertEqual(args.task_command, "run")
        self.assertEqual(args.preset, "plan-zxg-watchlist-import")
        self.assertEqual(args.input_path, "runtime/watchlist-imports/custom.json")

    def test_handle_task_run_uses_block_read_full_preset_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "run", "--preset", "read-zxg-full"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block_read_full.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_task_preset",
                return_value={
                    "command": "block-read-full",
                    "profile": "default",
                    "api_profile": "safe_read",
                    "trade_profile": None,
                    "strategy_path": None,
                    "options": {
                        "block_code": "ZXG",
                    },
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.block_read_full.assert_called_once_with(block_code="ZXG")

    def test_handle_task_run_prefers_block_read_full_cli_override(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "run", "--preset", "read-zxg-full", "--block-code", "MYZXG"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block_read_full.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_task_preset",
                return_value={
                    "command": "block-read-full",
                    "profile": "default",
                    "api_profile": "safe_read",
                    "trade_profile": None,
                    "strategy_path": None,
                    "options": {
                        "block_code": "ZXG",
                    },
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.block_read_full.assert_called_once_with(block_code="MYZXG")

    def test_handle_task_run_uses_block_read_watchlist_export_preset_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "run", "--preset", "export-zxg-watchlist"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block_read_watchlist_export.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_task_preset",
                return_value={
                    "command": "block-read-watchlist-export",
                    "profile": "default",
                    "api_profile": "safe_read",
                    "trade_profile": None,
                    "strategy_path": None,
                    "options": {
                        "block_code": "ZXG",
                        "export_output": "runtime/exports/zxg.json",
                        "overwrite": False,
                    },
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.block_read_watchlist_export.assert_called_once_with(
            block_code="ZXG",
            output="runtime/exports/zxg.json",
            overwrite=False,
        )

    def test_handle_task_run_prefers_block_read_watchlist_export_cli_overrides(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "run",
                "--preset",
                "export-zxg-watchlist",
                "--export-output",
                "runtime/exports/zxg-override.json",
                "--overwrite",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block_read_watchlist_export.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_task_preset",
                return_value={
                    "command": "block-read-watchlist-export",
                    "profile": "default",
                    "api_profile": "safe_read",
                    "trade_profile": None,
                    "strategy_path": None,
                    "options": {
                        "block_code": "ZXG",
                        "export_output": "runtime/exports/zxg.json",
                        "overwrite": False,
                    },
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.block_read_watchlist_export.assert_called_once_with(
            block_code="ZXG",
            output="runtime/exports/zxg-override.json",
            overwrite=True,
        )

    def test_handle_task_run_uses_block_read_watchlist_preset_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "run", "--preset", "read-zxg-watchlist"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block_read_watchlist.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_task_preset",
                return_value={
                    "command": "block-read-watchlist",
                    "profile": "default",
                    "api_profile": "safe_read",
                    "trade_profile": None,
                    "strategy_path": None,
                    "options": {
                        "block_code": "ZXG",
                    },
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.block_read_watchlist.assert_called_once_with(block_code="ZXG")

    def test_handle_task_run_uses_block_watchlist_import_preset_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "run", "--preset", "plan-zxg-watchlist-import"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block_watchlist_import.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_task_preset",
                return_value={
                    "command": "block-watchlist-import",
                    "profile": "default",
                    "api_profile": "safe_read",
                    "trade_profile": None,
                    "strategy_path": None,
                    "options": {
                        "input_path": "runtime/watchlist-imports/zxg-watchlist-import.example.json",
                        "dry_run": True,
                        "show": True,
                    },
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.block_watchlist_import.assert_called_once_with(
            input_path="runtime/watchlist-imports/zxg-watchlist-import.example.json",
            dry_run=True,
            show=True,
            audit_dir=None,
        )

    def test_handle_task_run_uses_block_sync_write_policy_preset_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "run", "--preset", "plan-zxg-block-sync-merge"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block_sync.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_task_preset",
                return_value={
                    "command": "block-sync",
                    "profile": "default",
                    "api_profile": "safe_read",
                    "trade_profile": None,
                    "strategy_path": None,
                    "options": {
                        "block_code": "ZXG",
                        "stock": ["000001.SZ", "600519.SH"],
                        "write_policy": "merge_dry_run",
                        "dry_run": True,
                        "show": True,
                    },
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.block_sync.assert_called_once_with(
            block_code="ZXG",
            symbols=["000001.SZ", "600519.SH"],
            mode="replace",
            write_policy="merge_dry_run",
            create_if_missing=False,
            dry_run=True,
            show=True,
            mutation_key=None,
            audit_dir=None,
        )

    def test_handle_task_run_prefers_block_read_watchlist_cli_overrides(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "run", "--preset", "read-zxg-watchlist", "--block-code", "MYZXG"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block_read_watchlist.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_task_preset",
                return_value={
                    "command": "block-read-watchlist",
                    "profile": "default",
                    "api_profile": "safe_read",
                    "trade_profile": None,
                    "strategy_path": None,
                    "options": {
                        "block_code": "ZXG",
                    },
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.block_read_watchlist.assert_called_once_with(block_code="MYZXG")

    def test_handle_task_run_rejects_block_read_watchlist_preset_missing_required_fields(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "run", "--preset", "read-zxg-watchlist"])
        with (
            patch(
                "tdxquant.cli.resolve_task_preset",
                return_value={
                    "command": "block-read-watchlist",
                    "profile": "default",
                    "api_profile": "safe_read",
                    "trade_profile": None,
                    "strategy_path": None,
                    "options": {},
                },
            ),
            patch("tdxquant.cli.TdxTaskManager") as mocked_manager,
        ):
            result = _handle_task_subcommand(args)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(result.message, "task preset execution requires: block_code")
        mocked_manager.assert_not_called()

    def test_handle_task_run_rejects_block_read_watchlist_export_preset_missing_required_fields(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "run", "--preset", "export-zxg-watchlist"])
        with patch(
            "tdxquant.cli.resolve_task_preset",
            return_value={
                "command": "block-read-watchlist-export",
                "profile": "default",
                "api_profile": "safe_read",
                "trade_profile": None,
                "strategy_path": None,
                "options": {"block_code": "ZXG"},
            },
        ):
            result = _handle_task_subcommand(args)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertIn("export_output", result.message)

    def test_handle_task_run_rejects_block_read_full_preset_missing_block_code(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "run", "--preset", "read-zxg-full"])
        with (
            patch(
                "tdxquant.cli.resolve_task_preset",
                return_value={
                    "command": "block-read-full",
                    "profile": "default",
                    "api_profile": "safe_read",
                    "trade_profile": None,
                    "strategy_path": None,
                    "options": {},
                },
            ),
            patch("tdxquant.cli.TdxTaskManager") as mocked_manager,
        ):
            result = _handle_task_subcommand(args)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(result.message, "task preset execution requires: block_code")
        mocked_manager.assert_not_called()

    def test_handle_task_sector_research_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "sector-research", "--sector", "钛金属"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.sector_research.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager) as mocked_manager:
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            api_profile=None,
            trade_profile=None,
            strategy_path=None,
            title_keyword="平安证券",
            exe_path=None,
        )
        manager.sector_research.assert_called_once_with(block_code="钛金属", block_type=0, list_type=None, fields=None)

    def test_handle_task_invalid_profile_returns_invalid_request(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "refresh-environment"])
        with patch("tdxquant.cli.TdxTaskManager", side_effect=ValueError("unsupported task profile: bad")):
            result = _handle_task_subcommand(args)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)

    def test_handle_task_watchlist_overview_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "watchlist-overview", "--code", "000001", "--code", "000002"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.watchlist_overview.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.watchlist_overview.assert_called_once_with(stock_list=["000001", "000002"], fields=None)

    def test_handle_task_block_sync_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "block-sync",
                "--block-code",
                "ZXG",
                "--stock",
                "000001.SZ",
                "--stock",
                "600519.SH",
                "--mode",
                "merge",
                "--write-policy",
                "merge_dry_run",
                "--create-if-missing",
                "--dry-run",
                "--show",
                "--mutation-key",
                "sync-001",
                "--audit-dir",
                "runtime/block-sync",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block_sync.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.block_sync.assert_called_once_with(
            block_code="ZXG",
            symbols=["000001.SZ", "600519.SH"],
            mode="merge",
            write_policy="merge_dry_run",
            create_if_missing=True,
            dry_run=True,
            show=True,
            mutation_key="sync-001",
            audit_dir="runtime/block-sync",
        )

    def test_handle_task_block_watchlist_import_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "block-watchlist-import",
                "--input",
                "runtime/watchlist-imports/zxg-watchlist-import.example.json",
                "--dry-run",
                "--show",
                "--audit-dir",
                "runtime/block-sync",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block_watchlist_import.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.block_watchlist_import.assert_called_once_with(
            input_path="runtime/watchlist-imports/zxg-watchlist-import.example.json",
            dry_run=True,
            show=True,
            audit_dir="runtime/block-sync",
        )

    def test_handle_task_block_read_watchlist_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "block-read-watchlist", "--block-code", "ZXG"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block_read_watchlist.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.block_read_watchlist.assert_called_once_with(block_code="ZXG")

    def test_handle_task_block_read_full_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "block-read-full", "--block-code", "ZXG"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block_read_full.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.block_read_full.assert_called_once_with(block_code="ZXG")

    def test_handle_task_block_read_watchlist_export_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "block-read-watchlist-export",
                "--block-code",
                "ZXG",
                "--output",
                "runtime/exports/zxg.json",
                "--overwrite",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.block_read_watchlist_export.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.block_read_watchlist_export.assert_called_once_with(
            block_code="ZXG",
            output="runtime/exports/zxg.json",
            overwrite=True,
        )

    def test_handle_task_sector_formula_scan_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "sector-formula-scan", "--sector", "钛金属", "--formula-name", "SCAN"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.sector_formula_scan.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.sector_formula_scan.assert_called_once_with(
            block_code="钛金属",
            formula_name="SCAN",
            block_type=0,
            list_type=None,
            formula_arg="",
            return_count=1,
            return_date=False,
            stock_period="1d",
            start_time="",
            end_time="",
            count=0,
            dividend_type=0,
        )

    def test_handle_task_watchlist_export_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "watchlist-export", "--code", "000001"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.watchlist_export.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.watchlist_export.assert_called_once_with(
            stock_list=["000001"],
            fields=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_task_subscription_watch_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "subscription-watch",
                "--code",
                "600519.SH",
                "--max-events",
                "5",
                "--max-seconds",
                "10",
                "--poll-interval",
                "0.5",
                "--jsonl-output-path",
                "runtime/watch.jsonl",
                "--csv-output-path",
                "runtime/watch.csv",
                "--status-output-path",
                "runtime/watch-status.json",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.subscription_watch.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.subscription_watch.assert_called_once_with(
            stock_list=["600519.SH"],
            max_events=5,
            max_seconds=10.0,
            poll_interval=0.5,
            jsonl_output_path="runtime/watch.jsonl",
            csv_output_path="runtime/watch.csv",
            status_output_path="runtime/watch-status.json",
        )

    def test_handle_task_subscription_watch_replay_builds_task_manager_with_replay_configuration(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "subscription-watch",
                "--code",
                "600519.SH",
                "--provider-mode",
                "replay",
                "--fixture",
                "subscription-watch-manifest",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.subscription_watch.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager) as mocked_manager:
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            api_profile=None,
            trade_profile=None,
            strategy_path=None,
            title_keyword="平安证券",
            exe_path=None,
            provider_mode="replay",
            replay_fixture="subscription-watch-manifest",
            replay_fixture_path=None,
        )
        manager.subscription_watch.assert_called_once_with(
            stock_list=["600519.SH"],
            max_events=None,
            max_seconds=None,
            poll_interval=None,
            jsonl_output_path=None,
            csv_output_path=None,
            status_output_path=None,
        )

    def test_handle_task_ledger_summary_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "ledger-summary", "--code", "000001", "--trade-ok"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.ledger_summary.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.ledger_summary.assert_called_once_with(
            limit=None,
            code="000001",
            contract_no=None,
            trade_ok=True,
            task_name=None,
            ledger_jsonl_path=None,
            ledger_csv_path=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_task_daily_trade_report_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "daily-trade-report", "--date", "2026-04-26", "--trade-ok"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.daily_trade_report.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.daily_trade_report.assert_called_once_with(
            report_date="2026-04-26",
            timezone_name=None,
            recent_limit=None,
            code=None,
            trade_ok=True,
            task_name=None,
            ledger_jsonl_path=None,
            ledger_csv_path=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_task_trade_report_lookup_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "trade-report-lookup", "--contract-no", "B202604260301"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_report_lookup.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_report_lookup.assert_called_once_with(
            contract_no="B202604260301",
            code=None,
            report_date=None,
            timezone_name=None,
            limit=None,
            trade_ok=None,
            task_name=None,
            ledger_jsonl_path=None,
            ledger_csv_path=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_task_trade_audit_lookup_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "trade-audit-lookup", "--audit-id", "audit-001", "--status", "confirmed"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_audit_lookup.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_audit_lookup.assert_called_once_with(
            audit_id="audit-001",
            contract_no=None,
            submission_key=None,
            code=None,
            status="confirmed",
            limit=None,
            audit_dir=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_task_trade_audit_daily_report_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "trade-audit-daily-report", "--date", "2026-04-29", "--status", "confirmed"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_audit_daily_report.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_audit_daily_report.assert_called_once_with(
            report_date="2026-04-29",
            timezone_name=None,
            recent_limit=None,
            code=None,
            status="confirmed",
            statuses=None,
            method=None,
            broker=None,
            submission_key=None,
            audit_dir=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_task_trade_audit_daily_report_uses_multi_statuses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["task", "trade-audit-daily-report", "--date", "2026-04-29", "--status-any", "rejected", "--status-any", "failed"]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_audit_daily_report.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_audit_daily_report.assert_called_once_with(
            report_date="2026-04-29",
            timezone_name=None,
            recent_limit=None,
            code=None,
            status=None,
            statuses=["rejected", "failed"],
            method=None,
            broker=None,
            submission_key=None,
            audit_dir=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_task_trade_audit_daily_report_uses_multi_methods(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["task", "trade-audit-daily-report", "--date", "2026-04-29", "--method-any", "buy_submit_once", "--method-any", "confirm_current"]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_audit_daily_report.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_audit_daily_report.assert_called_once_with(
            report_date="2026-04-29",
            timezone_name=None,
            recent_limit=None,
            code=None,
            status=None,
            statuses=None,
            method=None,
            methods=["buy_submit_once", "confirm_current"],
            broker=None,
            submission_key=None,
            audit_dir=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_task_trade_audit_daily_report_rejects_mixed_status_filters(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["task", "trade-audit-daily-report", "--date", "2026-04-29", "--status", "confirmed", "--status-any", "failed"]
        )
        manager = MagicMock()
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        manager.trade_audit_daily_report.assert_not_called()

    def test_handle_task_trade_audit_daily_report_rejects_mixed_method_filters(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["task", "trade-audit-daily-report", "--date", "2026-04-29", "--method", "buy_submit_once", "--method-any", "confirm_current"]
        )
        manager = MagicMock()
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        manager.trade_audit_daily_report.assert_not_called()

    def test_handle_task_trade_audit_period_report_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "trade-audit-period-report", "--start-date", "2026-04-28", "--end-date", "2026-04-29"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_audit_period_report.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_audit_period_report.assert_called_once_with(
            start_date="2026-04-28",
            end_date="2026-04-29",
            timezone_name=None,
            recent_limit=None,
            code=None,
            status=None,
            statuses=None,
            method=None,
            broker=None,
            submission_key=None,
            audit_dir=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_task_trade_period_report_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "trade-period-report", "--start-date", "2026-04-25", "--end-date", "2026-04-26"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_period_report.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_period_report.assert_called_once_with(
            start_date="2026-04-25",
            end_date="2026-04-26",
            timezone_name=None,
            recent_limit=None,
            code=None,
            trade_ok=None,
            task_name=None,
            ledger_jsonl_path=None,
            ledger_csv_path=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_task_sector_research_export_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "sector-research-export", "--sector", "钛金属"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.sector_research_export.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.sector_research_export.assert_called_once_with(
            block_code="钛金属",
            block_type=0,
            list_type=None,
            fields=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_task_trade_buy_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "trade-buy", "--port", "COM3", "--code", "000001", "--price", "10.00", "--quantity", "100"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_buy.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager) as mocked_manager:
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            api_profile=None,
            trade_profile=None,
            strategy_path=None,
            title_keyword="平安证券",
            exe_path=None,
        )
        manager.trade_buy.assert_called_once_with(
            port="COM3",
            baudrate=115200,
            timeout=2.0,
            code="000001",
            price="10.00",
            quantity=100,
            max_depth=12,
            close_result_dialog=True,
            submission_key=None,
            max_price=None,
            refresh_before_trade=None,
            refresh_market=None,
            refresh_force=None,
        )

    def test_handle_task_trade_sell_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "trade-sell", "--port", "COM3", "--code", "000001", "--price", "10.00", "--quantity", "100"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_sell.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager) as mocked_manager:
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            api_profile=None,
            trade_profile=None,
            strategy_path=None,
            title_keyword="平安证券",
            exe_path=None,
        )
        manager.trade_sell.assert_called_once_with(
            port="COM3",
            baudrate=115200,
            timeout=2.0,
            code="000001",
            price="10.00",
            quantity=100,
            max_depth=12,
            close_result_dialog=True,
            submission_key=None,
            max_price=None,
            refresh_before_trade=None,
            refresh_market=None,
            refresh_force=None,
        )

    def test_handle_task_trade_submit_once_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "trade-submit-once", "--port", "COM3", "--code", "000001", "--price", "10.00", "--quantity", "100"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_submit_once.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_submit_once.assert_called_once_with(
            port="COM3",
            baudrate=115200,
            timeout=2.0,
            side="buy",
            code="000001",
            price="10.00",
            quantity=100,
            max_depth=12,
            close_result_dialog=True,
            submission_key=None,
            max_price=None,
            refresh_before_trade=None,
            refresh_market=None,
            refresh_force=None,
        )

    def test_handle_task_trade_submit_once_forwards_sell_side_to_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "trade-submit-once",
                "--side",
                "sell",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_submit_once.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        self.assertEqual(manager.trade_submit_once.call_args.kwargs["side"], "sell")

    def test_handle_task_trade_submit_ready_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "trade-submit-ready",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--max-price",
                "10.20",
                "--dialog-lookup-mode",
                "win32_experimental",
                "--confirm-timeout",
                "2.5",
                "--refresh-before-trade",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_submit_ready.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_submit_ready.assert_called_once_with(
            port="COM3",
            baudrate=115200,
            timeout=2.0,
            code="000001",
            price="10.00",
            quantity=100,
            max_depth=12,
            max_price=10.20,
            refresh_before_trade=True,
            refresh_market=None,
            refresh_force=None,
            dialog_lookup_mode="win32_experimental",
            confirm_timeout=2.5,
        )

    def test_handle_task_trade_confirm_current_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "trade-confirm-current",
                "--dialog-lookup-mode",
                "win32_experimental",
                "--confirm-timeout",
                "2.0",
                "--result-timeout",
                "3.0",
                "--no-close-result-dialog",
                "--result-close-pre-delay",
                "0.3",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_confirm_current.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_confirm_current.assert_called_once_with(
            dialog_lookup_mode="win32_experimental",
            confirm_timeout=2.0,
            result_timeout=3.0,
            close_result_dialog=False,
            result_close_pre_delay=0.3,
        )

    def test_handle_task_guarded_trade_buy_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "task",
                "guarded-trade-buy",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--max-snapshot-price",
                "10.50",
                "--required-block-code",
                "ZXG",
                "--formula-name",
                "SCAN",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.guarded_trade_buy.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_task_subcommand(args)
        self.assertIs(result, expected)
        manager.guarded_trade_buy.assert_called_once_with(
            port="COM3",
            baudrate=115200,
            timeout=2.0,
            code="000001",
            price="10.00",
            quantity=100,
            max_depth=12,
            close_result_dialog=True,
            submission_key=None,
            max_price=None,
            refresh_before_trade=None,
            refresh_market=None,
            refresh_force=None,
            max_snapshot_price=10.50,
            required_block_code="ZXG",
            required_block_type=0,
            required_list_type=None,
            formula_name="SCAN",
            formula_arg="",
            formula_return_count=1,
            formula_return_date=False,
            formula_stock_period="1d",
            formula_start_time="",
            formula_end_time="",
            formula_count=0,
            formula_dividend_type=0,
            json_output_path=None,
            csv_output_path=None,
        )


class TradeCliDispatchTests(unittest.TestCase):
    def test_handle_trade_presets_lists_available_presets(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["trade", "presets"])
        with patch(
            "tdxquant.cli.load_trade_presets",
            return_value={
                "turbo-buy": {"command": "buy", "description": "turbo buy", "profile": "turbo", "options": {"port": "COM3"}},
                "submit-once-default": {
                    "command": "submit-once",
                    "description": "submit once",
                    "profile": "submit_once",
                    "options": {"port": "COM3"},
                },
            },
        ):
            result = _handle_trade_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["preset_count"], 2)
        self.assertEqual(result.data["presets"][0]["name"], "submit-once-default")

    def test_handle_trade_run_uses_buy_preset_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["trade", "run", "--preset", "turbo-buy", "--code", "000001", "--price", "10.00", "--quantity", "100"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"result_dialog": {}})
        with (
            patch(
                "tdxquant.cli.resolve_trade_preset",
                return_value={
                    "command": "buy",
                    "profile": "turbo",
                    "title_key": "平安证券",
                    "exe_path": None,
                    "options": {"port": "COM3", "timeout": 2.0, "max_depth": 12, "close_result_dialog": True},
                },
            ),
            patch("tdxquant.cli._run_trade_buy", return_value=expected) as mocked,
        ):
            result = _handle_trade_subcommand(args)
        self.assertIs(result, expected)
        called_args = mocked.call_args.args[0]
        self.assertEqual(called_args.profile, "turbo")
        self.assertEqual(called_args.port, "COM3")
        self.assertEqual(called_args.code, "000001")

    def test_handle_trade_run_prefers_explicit_cli_overrides(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "run",
                "--preset",
                "turbo-buy",
                "--port",
                "COM9",
                "--profile",
                "balanced",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--submission-key",
                "explicit-key",
                "--max-price",
                "10.50",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"result_dialog": {}})
        with (
            patch(
                "tdxquant.cli.resolve_trade_preset",
                return_value={
                    "command": "buy",
                    "profile": "turbo",
                    "title_key": "平安证券",
                    "exe_path": None,
                    "options": {"port": "COM3", "timeout": 2.0, "submission_key": "preset-key", "max_price": 11.0},
                },
            ),
            patch("tdxquant.cli._run_trade_buy", return_value=expected) as mocked,
        ):
            result = _handle_trade_subcommand(args)
        self.assertIs(result, expected)
        called_args = mocked.call_args.args[0]
        self.assertEqual(called_args.profile, "balanced")
        self.assertEqual(called_args.port, "COM9")
        self.assertEqual(called_args.submission_key, "explicit-key")
        self.assertEqual(called_args.max_price, 10.50)

    def test_handle_trade_run_uses_submit_once_preset(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["trade", "run", "--preset", "submit-once-default", "--code", "000001", "--price", "10.00", "--quantity", "100"]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"result_dialog": {}})
        with (
            patch(
                "tdxquant.cli.resolve_trade_preset",
                return_value={
                    "command": "submit-once",
                    "profile": "submit_once",
                    "title_key": "平安证券",
                    "exe_path": None,
                    "options": {"port": "COM3", "confirm_timeout": 3.0},
                },
            ),
            patch("tdxquant.cli._run_trade_submit_once", return_value=expected) as mocked,
        ):
            result = _handle_trade_subcommand(args)
        self.assertIs(result, expected)
        called_args = mocked.call_args.args[0]
        self.assertEqual(called_args.profile, "submit_once")
        self.assertEqual(called_args.port, "COM3")
        self.assertEqual(called_args.confirm_timeout, 3.0)

    def test_handle_trade_run_broker_capabilities_preset_without_order_fields(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["trade", "run", "--preset", "broker-capabilities-default"])
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={"broker_capabilities": {"overall_status": "boundary_only"}},
        )
        with patch("tdxquant.cli._run_trade_broker_capabilities", return_value=expected) as mocked:
            result = _handle_trade_subcommand(args)
        self.assertIs(result, expected)
        called_args = mocked.call_args.args[0]
        self.assertEqual(called_args.trade_command, "broker-capabilities")
        self.assertEqual(called_args.profile, "balanced")
        self.assertEqual(called_args.broker, "pingan_desktop")
        self.assertIsNone(called_args.code)
        self.assertIsNone(called_args.price)
        self.assertIsNone(called_args.quantity)

    def test_handle_trade_run_rejects_unsupported_preset_command(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["trade", "run", "--preset", "bad", "--code", "000001", "--price", "10.00", "--quantity", "100"])
        with patch(
            "tdxquant.cli.resolve_trade_preset",
            return_value={"command": "probe", "profile": "turbo", "title_key": "平安证券", "exe_path": None, "options": {}},
        ):
            result = _handle_trade_subcommand(args)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)

    def test_handle_trade_buy_uses_trade_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["trade", "buy", "--port", "COM3", "--code", "000001", "--price", "10.00", "--quantity", "100"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"trade_profile": {"name": "balanced", "options": {}}, "result_dialog": {}})
        with patch("tdxquant.cli._run_trade_buy", return_value=expected) as mocked:
            result = _handle_trade_subcommand(args)
        self.assertIs(result, expected)
        mocked.assert_called_once_with(args)

    def test_handle_trade_submit_once_uses_trade_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["trade", "submit-once", "--port", "COM3", "--code", "000001", "--price", "10.00", "--quantity", "100"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"result_dialog": {}})
        with patch("tdxquant.cli._run_trade_submit_once", return_value=expected) as mocked:
            result = _handle_trade_subcommand(args)
        self.assertIs(result, expected)
        mocked.assert_called_once_with(args)

    def test_handle_trade_health_uses_trade_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["trade", "health", "--port", "COM3", "--pre-delay", "0.2"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"health": {"overall_status": "ok"}})
        with patch("tdxquant.cli._run_trade_health", return_value=expected) as mocked:
            result = _handle_trade_subcommand(args)
        self.assertIs(result, expected)
        mocked.assert_called_once_with(args)

    def test_handle_trade_preflight_uses_trade_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["trade", "preflight", "--port", "COM3", "--code", "000001", "--price", "10.00", "--quantity", "100"]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"preflight": {"overall_status": "ok"}})
        with patch("tdxquant.cli._run_trade_preflight", return_value=expected) as mocked:
            result = _handle_trade_subcommand(args)
        self.assertIs(result, expected)
        mocked.assert_called_once_with(args)

    def test_handle_trade_dialog_readiness_uses_trade_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["trade", "dialog-readiness", "--dialog", "confirm", "--require-visible"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"dialog_readiness": {"overall_status": "ok"}})
        with patch("tdxquant.cli._run_trade_dialog_readiness", return_value=expected) as mocked:
            result = _handle_trade_subcommand(args)
        self.assertIs(result, expected)
        mocked.assert_called_once_with(args)

    def test_handle_trade_submit_ready_uses_trade_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["trade", "submit-ready", "--port", "COM3", "--code", "000001", "--price", "10.00", "--quantity", "100"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"submit_ready": {"overall_status": "ok"}})
        with patch("tdxquant.cli._run_trade_submit_ready", return_value=expected) as mocked:
            result = _handle_trade_subcommand(args)
        self.assertIs(result, expected)
        mocked.assert_called_once_with(args)

    def test_handle_trade_broker_capabilities_uses_trade_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["trade", "broker-capabilities", "--broker", "pingan_desktop"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"broker_capabilities": {"overall_status": "ok"}})
        with patch("tdxquant.cli._run_trade_broker_capabilities", return_value=expected) as mocked:
            result = _handle_trade_subcommand(args)
        self.assertIs(result, expected)
        mocked.assert_called_once_with(args)

    def test_handle_trade_confirm_current_uses_trade_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["trade", "confirm-current"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"confirm_current": {"overall_status": "ok"}})
        with patch("tdxquant.cli._run_trade_confirm_current", return_value=expected) as mocked:
            result = _handle_trade_subcommand(args)
        self.assertIs(result, expected)
        mocked.assert_called_once_with(args)

    def test_run_trade_buy_forwards_safety_controls(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "buy",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--submission-key",
                "buy-20260428-002",
                "--max-price",
                "10.50",
            ]
        )
        snapshot = _snapshot(gateway_order_id="gw-001")
        service = MagicMock()
        service.place_order.return_value = snapshot
        with patch("tdxquant.cli._build_trader_service", return_value=service) as mocked_builder:
            result = _run_trade_buy(args)
        mocked_builder.assert_called_once()
        request = service.place_order.call_args.args[0]
        self.assertEqual(request.side, OrderSide.BUY)
        self.assertEqual(request.symbol, "000001")
        self.assertEqual(request.submission_key, "buy-20260428-002")
        self.assertEqual(request.limit_price, Decimal("10.00"))
        self.assertTrue(result.ok)
        self.assertEqual(result.data["order"]["gateway_order_id"], "gw-001")
        self.assertEqual(result.data["execution_profile"]["name"], "balanced")

    def test_run_trade_sell_forwards_safety_controls(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "sell",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--submission-key",
                "sell-20260428-002",
                "--max-price",
                "10.50",
            ]
        )
        snapshot = _snapshot(gateway_order_id="gw-sell-001")
        service = MagicMock()
        service.place_order.return_value = snapshot
        with patch("tdxquant.cli._build_trader_service", return_value=service) as mocked_builder:
            result = _run_trade_sell(args)
        mocked_builder.assert_called_once()
        request = service.place_order.call_args.args[0]
        self.assertEqual(request.side, OrderSide.SELL)
        self.assertEqual(request.symbol, "000001")
        self.assertEqual(request.submission_key, "sell-20260428-002")
        self.assertEqual(request.limit_price, Decimal("10.00"))
        self.assertTrue(result.ok)
        self.assertEqual(result.data["order"]["gateway_order_id"], "gw-sell-001")
        self.assertEqual(result.data["execution_profile"]["name"], "balanced")

    def test_run_trade_submit_once_forwards_safety_controls(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "submit-once",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--submission-key",
                "submit-20260428-002",
                "--max-price",
                "10.50",
            ]
        )
        snapshot = _snapshot(gateway_order_id="gw-002")
        service = MagicMock()
        service.place_order.return_value = snapshot
        with patch("tdxquant.cli._build_trader_service", return_value=service) as mocked_builder:
            result = _run_trade_submit_once(args)
        self.assertEqual(mocked_builder.call_args.kwargs["execution_mode"], "submit_once")
        request = service.place_order.call_args.args[0]
        self.assertEqual(request.side, OrderSide.BUY)
        self.assertEqual(request.submission_key, "submit-20260428-002")
        self.assertTrue(result.ok)
        self.assertEqual(result.data["order"]["gateway_order_id"], "gw-002")
        self.assertEqual(result.data["execution_profile"]["name"], "submit_once")

    def test_run_trade_submit_once_forwards_explicit_sell_side(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "submit-once",
                "--side",
                "sell",
                "--port",
                "COM3",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
            ]
        )
        snapshot = _snapshot(gateway_order_id="gw-sell-001")
        service = MagicMock()
        service.place_order.return_value = snapshot
        with patch("tdxquant.cli._build_trader_service", return_value=service):
            result = _run_trade_submit_once(args)
        request = service.place_order.call_args.args[0]
        self.assertEqual(request.side, OrderSide.SELL)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["order"]["gateway_order_id"], "gw-sell-001")

    def test_run_trade_buy_returns_failed_result_when_snapshot_failed(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["trade", "buy", "--port", "COM3", "--code", "000001", "--price", "10.00", "--quantity", "100"])
        service = MagicMock()
        service.place_order.return_value = _snapshot(
            gateway_order_id="gw-failed",
            status=OrderStatus.FAILED,
            reject_reason="desktop execution failed",
        )
        with patch("tdxquant.cli._build_trader_service", return_value=service):
            result = _run_trade_buy(args)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.EXECUTION_FAILED)
        self.assertIn("desktop execution failed", result.message)

    def test_run_trade_health_forwards_requested_hid_ping(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["trade", "health", "--port", "COM3", "--baudrate", "9600", "--timeout", "1.5", "--pre-delay", "0.2"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"health": {"overall_status": "ok"}})
        manager = MagicMock()
        manager.pingan.health.return_value = expected
        with patch("tdxquant.cli.TdxTradeManager", return_value=manager):
            result = _run_trade_health(args)
        self.assertIs(result, expected)
        manager.pingan.health.assert_called_once_with(
            port="COM3",
            baudrate=9600,
            timeout=1.5,
            pre_delay=0.2,
        )

    def test_run_trade_preflight_forwards_trade_request(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "preflight",
                "--port",
                "COM3",
                "--baudrate",
                "9600",
                "--timeout",
                "1.5",
                "--pre-delay",
                "0.2",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--submission-key",
                "preflight-001",
                "--max-price",
                "10.50",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"preflight": {"overall_status": "ok"}})
        manager = MagicMock()
        manager.pingan.preflight.return_value = expected
        with patch("tdxquant.cli.TdxTradeManager", return_value=manager):
            result = _run_trade_preflight(args)
        self.assertIs(result, expected)
        manager.pingan.preflight.assert_called_once_with(
            port="COM3",
            baudrate=9600,
            timeout=1.5,
            pre_delay=0.2,
            code="000001",
            price="10.00",
            quantity=100,
            submission_key="preflight-001",
            max_price=10.50,
        )

    def test_run_trade_dialog_readiness_forwards_lookup_arguments(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "dialog-readiness",
                "--dialog",
                "result",
                "--require-visible",
                "--dialog-lookup-mode",
                "win32_experimental",
                "--confirm-timeout",
                "1.2",
                "--result-timeout",
                "1.8",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"dialog_readiness": {"overall_status": "ok"}})
        manager = MagicMock()
        manager.pingan.dialog_readiness.return_value = expected
        with patch("tdxquant.cli.TdxTradeManager", return_value=manager):
            result = _run_trade_dialog_readiness(args)
        self.assertIs(result, expected)
        manager.pingan.dialog_readiness.assert_called_once_with(
            dialog="result",
            require_visible=True,
            dialog_lookup_mode="win32_experimental",
            confirm_timeout=1.2,
            result_timeout=1.8,
        )

    def test_run_trade_submit_ready_forwards_boundary_arguments(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "submit-ready",
                "--port",
                "COM3",
                "--baudrate",
                "9600",
                "--timeout",
                "1.5",
                "--code",
                "000001",
                "--price",
                "10.00",
                "--quantity",
                "100",
                "--max-price",
                "10.50",
                "--dialog-lookup-mode",
                "win32_experimental",
                "--confirm-timeout",
                "1.2",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"submit_ready": {"overall_status": "ok"}})
        manager = MagicMock()
        manager.pingan.submit_ready.return_value = expected
        with patch("tdxquant.cli.TdxTradeManager", return_value=manager):
            result = _run_trade_submit_ready(args)
        self.assertIs(result, expected)
        manager.pingan.submit_ready.assert_called_once_with(
            port="COM3",
            baudrate=9600,
            timeout=1.5,
            code="000001",
            price="10.00",
            quantity=100,
            max_depth=12,
            max_price=10.50,
            dialog_lookup_mode="win32_experimental",
            confirm_timeout=1.2,
        )

    def test_run_trade_broker_capabilities_forwards_to_trade_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["trade", "broker-capabilities", "--broker", "pingan_desktop"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"broker_capabilities": {"overall_status": "ok"}})
        manager = MagicMock()
        manager.pingan.extended_broker_capabilities.return_value = expected
        with patch("tdxquant.cli.TdxTradeManager", return_value=manager) as trade_manager:
            result = _run_trade_broker_capabilities(args)
        self.assertIs(result, expected)
        trade_manager.assert_called_once_with(profile="balanced", title_keyword="平安证券", exe_path=None)
        manager.pingan.extended_broker_capabilities.assert_called_once_with()

    def test_run_trade_broker_capabilities_rejects_unsupported_broker(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["trade", "broker-capabilities", "--broker", "other"])

        result = _run_trade_broker_capabilities(args)

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertIn("unsupported broker", result.message)
        self.assertEqual(result.data["supported_brokers"], ["pingan_desktop"])

    def test_run_trade_confirm_current_forwards_boundary_arguments(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "confirm-current",
                "--dialog-lookup-mode",
                "win32_experimental",
                "--confirm-timeout",
                "1.2",
                "--result-timeout",
                "1.8",
                "--close-result-dialog",
            ]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"confirm_current": {"overall_status": "ok"}})
        manager = MagicMock()
        manager.pingan.confirm_current.return_value = expected
        with patch("tdxquant.cli.TdxTradeManager", return_value=manager):
            result = _run_trade_confirm_current(args)
        self.assertIs(result, expected)
        manager.pingan.confirm_current.assert_called_once_with(
            dialog_lookup_mode="win32_experimental",
            confirm_timeout=1.2,
            result_timeout=1.8,
            close_result_dialog=True,
        )


class ReportCliDispatchTests(unittest.TestCase):
    def test_handle_report_presets_lists_available_presets(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "presets"])
        with patch(
            "tdxquant.cli.load_report_presets",
            return_value={
                "daily-review": {"command": "daily", "description": "daily report", "options": {"recent_limit": 20}},
                "success-ledger": {"command": "ledger", "description": "success only", "options": {"trade_ok": True}},
            },
        ):
            result = _handle_report_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["preset_count"], 2)
        self.assertEqual(result.data["presets"][0]["name"], "daily-review")
        self.assertEqual(result.data["presets"][0]["command"], "daily")

    def test_handle_report_run_uses_preset_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "run", "--preset", "daily-review"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.daily_trade_report.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_report_preset",
                return_value={
                    "command": "daily",
                    "profile": "daily_trade_report",
                    "options": {"timezone": "Asia/Shanghai", "recent_limit": 20, "trade_ok": True},
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager) as mocked_manager,
        ):
            result = _handle_report_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="daily_trade_report",
            api_profile=None,
            trade_profile=None,
            strategy_path=None,
            title_keyword="平安证券",
            exe_path=None,
        )
        manager.daily_trade_report.assert_called_once_with(
            report_date=None,
            timezone_name="Asia/Shanghai",
            recent_limit=20,
            code=None,
            trade_ok=True,
            task_name=None,
            ledger_jsonl_path=None,
            ledger_csv_path=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_report_run_uses_audit_exception_preset_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "run", "--preset", "audit-daily-exceptions"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_audit_daily_report.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_report_preset",
                return_value={
                    "command": "audit-daily",
                    "profile": "trade_audit_daily_report",
                    "options": {"timezone": "Asia/Shanghai", "recent_limit": 20, "statuses": ["rejected", "failed"]},
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_report_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_audit_daily_report.assert_called_once_with(
            report_date=None,
            timezone_name="Asia/Shanghai",
            recent_limit=20,
            code=None,
            status=None,
            statuses=["rejected", "failed"],
            method=None,
            broker=None,
            submission_key=None,
            audit_dir=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_report_run_uses_confirm_oriented_audit_exception_preset_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "run", "--preset", "audit-daily-confirm-exceptions"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_audit_daily_report.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_report_preset",
                return_value={
                    "command": "audit-daily",
                    "profile": "trade_audit_daily_report",
                    "options": {
                        "timezone": "Asia/Shanghai",
                        "recent_limit": 20,
                        "method": "confirm_current",
                        "statuses": ["rejected", "failed"],
                    },
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_report_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_audit_daily_report.assert_called_once_with(
            report_date=None,
            timezone_name="Asia/Shanghai",
            recent_limit=20,
            code=None,
            status=None,
            statuses=["rejected", "failed"],
            method="confirm_current",
            broker=None,
            submission_key=None,
            audit_dir=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_report_run_uses_submit_once_audit_exception_preset_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "run", "--preset", "audit-daily-submit-once-exceptions"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_audit_daily_report.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_report_preset",
                return_value={
                    "command": "audit-daily",
                    "profile": "trade_audit_daily_report",
                    "options": {
                        "timezone": "Asia/Shanghai",
                        "recent_limit": 20,
                        "method": "buy_submit_once",
                        "statuses": ["rejected", "failed"],
                    },
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_report_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_audit_daily_report.assert_called_once_with(
            report_date=None,
            timezone_name="Asia/Shanghai",
            recent_limit=20,
            code=None,
            status=None,
            statuses=["rejected", "failed"],
            method="buy_submit_once",
            broker=None,
            submission_key=None,
            audit_dir=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_report_run_uses_buy_audit_exception_preset_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "run", "--preset", "audit-daily-buy-exceptions"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_audit_daily_report.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_report_preset",
                return_value={
                    "command": "audit-daily",
                    "profile": "trade_audit_daily_report",
                    "options": {
                        "timezone": "Asia/Shanghai",
                        "recent_limit": 20,
                        "method": "buy",
                        "statuses": ["rejected", "failed"],
                    },
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_report_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_audit_daily_report.assert_called_once_with(
            report_date=None,
            timezone_name="Asia/Shanghai",
            recent_limit=20,
            code=None,
            status=None,
            statuses=["rejected", "failed"],
            method="buy",
            broker=None,
            submission_key=None,
            audit_dir=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_report_run_uses_submit_path_audit_exception_preset_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "run", "--preset", "audit-daily-submit-path-exceptions"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_audit_daily_report.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_report_preset",
                return_value={
                    "command": "audit-daily",
                    "profile": "trade_audit_daily_report",
                    "options": {
                        "timezone": "Asia/Shanghai",
                        "recent_limit": 20,
                        "methods": ["buy_submit_once", "confirm_current"],
                        "statuses": ["rejected", "failed"],
                    },
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_report_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_audit_daily_report.assert_called_once_with(
            report_date=None,
            timezone_name="Asia/Shanghai",
            recent_limit=20,
            code=None,
            status=None,
            statuses=["rejected", "failed"],
            method=None,
            methods=["buy_submit_once", "confirm_current"],
            broker=None,
            submission_key=None,
            audit_dir=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_report_run_uses_pingan_submit_path_audit_exception_preset_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "run", "--preset", "audit-daily-pingan-submit-path-exceptions"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_audit_daily_report.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_report_preset",
                return_value={
                    "command": "audit-daily",
                    "profile": "trade_audit_daily_report",
                    "options": {
                        "timezone": "Asia/Shanghai",
                        "recent_limit": 20,
                        "broker": "pingan",
                        "methods": ["buy_submit_once", "confirm_current"],
                        "statuses": ["rejected", "failed"],
                    },
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_report_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_audit_daily_report.assert_called_once_with(
            report_date=None,
            timezone_name="Asia/Shanghai",
            recent_limit=20,
            code=None,
            status=None,
            statuses=["rejected", "failed"],
            method=None,
            methods=["buy_submit_once", "confirm_current"],
            broker="pingan",
            submission_key=None,
            audit_dir=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_report_run_prefers_explicit_cli_overrides(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["report", "run", "--preset", "daily-review", "--timezone", "UTC", "--recent-limit", "5"]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.daily_trade_report.return_value = expected
        with (
            patch(
                "tdxquant.cli.resolve_report_preset",
                return_value={
                    "command": "daily",
                    "profile": "daily_trade_report",
                    "options": {"timezone": "Asia/Shanghai", "recent_limit": 20},
                },
            ),
            patch("tdxquant.cli.TdxTaskManager", return_value=manager),
        ):
            result = _handle_report_subcommand(args)
        self.assertIs(result, expected)
        manager.daily_trade_report.assert_called_once_with(
            report_date=None,
            timezone_name="UTC",
            recent_limit=5,
            code=None,
            trade_ok=None,
            task_name=None,
            ledger_jsonl_path=None,
            ledger_csv_path=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_report_run_rejects_unsupported_preset_command(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "run", "--preset", "bad-preset"])
        with patch(
            "tdxquant.cli.resolve_report_preset",
            return_value={"command": "watchlist", "profile": "daily_trade_report", "options": {}},
        ):
            result = _handle_report_subcommand(args)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)

    def test_handle_report_daily_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "daily", "--date", "2026-04-26"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.daily_trade_report.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager) as mocked_manager:
            result = _handle_report_subcommand(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="daily_trade_report",
            api_profile=None,
            trade_profile=None,
            strategy_path=None,
            title_keyword="平安证券",
            exe_path=None,
        )
        manager.daily_trade_report.assert_called_once_with(
            report_date="2026-04-26",
            timezone_name=None,
            recent_limit=None,
            code=None,
            trade_ok=None,
            task_name=None,
            ledger_jsonl_path=None,
            ledger_csv_path=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_report_lookup_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "lookup", "--contract-no", "B202604260301"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_report_lookup.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_report_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_report_lookup.assert_called_once_with(
            contract_no="B202604260301",
            code=None,
            report_date=None,
            timezone_name=None,
            limit=None,
            trade_ok=None,
            task_name=None,
            ledger_jsonl_path=None,
            ledger_csv_path=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_report_audit_lookup_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "audit-lookup", "--submission-key", "submit-001"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_audit_lookup.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_report_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_audit_lookup.assert_called_once_with(
            audit_id=None,
            contract_no=None,
            submission_key="submit-001",
            code=None,
            status=None,
            limit=None,
            audit_dir=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_report_audit_daily_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "audit-daily", "--date", "2026-04-29"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_audit_daily_report.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_report_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_audit_daily_report.assert_called_once_with(
            report_date="2026-04-29",
            timezone_name=None,
            recent_limit=None,
            code=None,
            status=None,
            statuses=None,
            method=None,
            broker=None,
            submission_key=None,
            audit_dir=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_report_audit_period_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "audit-period", "--start-date", "2026-04-28"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_audit_period_report.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_report_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_audit_period_report.assert_called_once_with(
            start_date="2026-04-28",
            end_date=None,
            timezone_name=None,
            recent_limit=None,
            code=None,
            status=None,
            statuses=None,
            method=None,
            broker=None,
            submission_key=None,
            audit_dir=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_report_audit_period_uses_multi_statuses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["report", "audit-period", "--start-date", "2026-04-28", "--status-any", "rejected", "--status-any", "failed"]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_audit_period_report.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_report_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_audit_period_report.assert_called_once_with(
            start_date="2026-04-28",
            end_date=None,
            timezone_name=None,
            recent_limit=None,
            code=None,
            status=None,
            statuses=["rejected", "failed"],
            method=None,
            broker=None,
            submission_key=None,
            audit_dir=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_report_audit_period_uses_multi_methods(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["report", "audit-period", "--start-date", "2026-04-28", "--method-any", "buy_submit_once", "--method-any", "confirm_current"]
        )
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_audit_period_report.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_report_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_audit_period_report.assert_called_once_with(
            start_date="2026-04-28",
            end_date=None,
            timezone_name=None,
            recent_limit=None,
            code=None,
            status=None,
            statuses=None,
            method=None,
            methods=["buy_submit_once", "confirm_current"],
            broker=None,
            submission_key=None,
            audit_dir=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_report_period_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "period", "--start-date", "2026-04-25", "--end-date", "2026-04-26"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.trade_period_report.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_report_subcommand(args)
        self.assertIs(result, expected)
        manager.trade_period_report.assert_called_once_with(
            start_date="2026-04-25",
            end_date="2026-04-26",
            timezone_name=None,
            recent_limit=None,
            code=None,
            trade_ok=None,
            task_name=None,
            ledger_jsonl_path=None,
            ledger_csv_path=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_handle_report_ledger_uses_task_manager(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["report", "ledger", "--code", "000001"])
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        manager = MagicMock()
        manager.ledger_summary.return_value = expected
        with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
            result = _handle_report_subcommand(args)
        self.assertIs(result, expected)
        manager.ledger_summary.assert_called_once_with(
            limit=None,
            code="000001",
            contract_no=None,
            trade_ok=None,
            task_name=None,
            ledger_jsonl_path=None,
            ledger_csv_path=None,
            json_output_path=None,
            csv_output_path=None,
        )

    def test_main_pingan_buy_uses_trade_manager(self) -> None:
        service = MagicMock()
        service.place_order.return_value = _snapshot(gateway_order_id="gw-main-buy")
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli._build_trader_service", return_value=service) as mocked_service_builder,
            patch("tdxquant.cli._emit_pingan_contract_log"),
            patch("sys.argv", ["tdxquant", "pingan-buy", "--port", "COM3", "--code", "000001", "--price", "10.00", "--quantity", "100"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked_service_builder.assert_called_once()
        service.place_order.assert_called_once()

    def test_main_bridge_serve_dispatches_to_bridge_http_server(self) -> None:
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.serve_bridge_from_config", return_value=0) as mocked,
            patch("sys.argv", ["tdxquant", "bridge", "serve", "--config", "runtime/bridge/worker-bridge.json"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with("runtime/bridge/worker-bridge.json")

    def test_handle_bridge_watch_status_dispatches_registry_client(self) -> None:
        args = build_parser().parse_args(
            [
                "bridge",
                "watch-status",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--heartbeat-stale-after-seconds",
                "60",
                "--watermark-stale-after-seconds",
                "120",
                "--reconnect-stale-after-seconds",
                "180",
            ]
        )
        with (
            patch("tdxquant.cli.run_bridge_watch_status", return_value={"ok": True, "result": {"status": "idle"}}) as mocked_run,
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 0)
        mocked_run.assert_called_once_with(
            registry_path="runtime/bridge/master-workers.json",
            worker_id="worker-a",
            heartbeat_stale_after_seconds=60.0,
            watermark_stale_after_seconds=120.0,
            reconnect_stale_after_seconds=180.0,
        )
        self.assertEqual(json.loads(stdout.getvalue()), {"ok": True, "result": {"status": "idle"}})

    def test_handle_bridge_watch_restart_dispatches_registry_client(self) -> None:
        args = build_parser().parse_args(
            [
                "bridge",
                "watch-restart",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--reason",
                "operator_restart",
                "--grace-period-seconds",
                "2",
            ]
        )
        with (
            patch(
                "tdxquant.cli.run_bridge_watch_restart",
                return_value={"ok": True, "result": {"status": "restarted"}},
            ) as mocked_run,
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 0)
        mocked_run.assert_called_once_with(
            registry_path="runtime/bridge/master-workers.json",
            worker_id="worker-a",
            reason="operator_restart",
            grace_period_seconds=2,
        )
        self.assertEqual(json.loads(stdout.getvalue()), {"ok": True, "result": {"status": "restarted"}})

    def test_handle_bridge_watch_restart_preflight_dispatches_registry_client(self) -> None:
        args = build_parser().parse_args(
            [
                "bridge",
                "watch-restart-preflight",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
            ]
        )
        with (
            patch(
                "tdxquant.cli.run_bridge_watch_restart_preflight",
                return_value={"ok": True, "result": {"ready": True}},
            ) as mocked_run,
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 0)
        mocked_run.assert_called_once_with(
            registry_path="runtime/bridge/master-workers.json",
            worker_id="worker-a",
        )
        self.assertEqual(json.loads(stdout.getvalue()), {"ok": True, "result": {"ready": True}})

    def test_handle_bridge_watch_supervisor_tick_dispatches_registry_client(self) -> None:
        args = build_parser().parse_args(
            [
                "bridge",
                "watch-supervisor-tick",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--reason",
                "manual_tick",
            ]
        )
        with (
            patch(
                "tdxquant.cli.run_bridge_watch_supervisor_tick",
                return_value={"ok": True, "result": {"status": "noop"}},
            ) as mocked_run,
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 0)
        mocked_run.assert_called_once_with(
            registry_path="runtime/bridge/master-workers.json",
            worker_id="worker-a",
            reason="manual_tick",
        )
        self.assertEqual(json.loads(stdout.getvalue()), {"ok": True, "result": {"status": "noop"}})

    def test_handle_bridge_watch_supervisor_run_dispatches_registry_client(self) -> None:
        args = build_parser().parse_args(
            [
                "bridge",
                "watch-supervisor-run",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--max-ticks",
                "3",
                "--interval-seconds",
                "0.25",
                "--reason",
                "manual_supervise",
            ]
        )
        with (
            patch(
                "tdxquant.cli.run_bridge_watch_supervisor_run",
                return_value={"ok": True, "result": {"status": "waiting", "tick_count": 3}},
            ) as mocked_run,
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 0)
        mocked_run.assert_called_once_with(
            registry_path="runtime/bridge/master-workers.json",
            worker_id="worker-a",
            max_ticks=3,
            interval_seconds=0.25,
            reason="manual_supervise",
        )
        self.assertEqual(json.loads(stdout.getvalue()), {"ok": True, "result": {"status": "waiting", "tick_count": 3}})

    def test_handle_bridge_watch_supervisor_daemon_status_dispatches_registry_client(self) -> None:
        args = build_parser().parse_args(
            [
                "bridge",
                "watch-supervisor-daemon-status",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
            ]
        )
        with (
            patch(
                "tdxquant.cli.run_bridge_watch_supervisor_daemon_status",
                return_value={"ok": True, "result": {"state": "running"}},
            ) as mocked_run,
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 0)
        mocked_run.assert_called_once_with(
            registry_path="runtime/bridge/master-workers.json",
            worker_id="worker-a",
        )
        self.assertEqual(json.loads(stdout.getvalue()), {"ok": True, "result": {"state": "running"}})

    def test_handle_bridge_watch_supervisor_daemon_start_dispatches_registry_client(self) -> None:
        args = build_parser().parse_args(
            [
                "bridge",
                "watch-supervisor-daemon-start",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--max-ticks",
                "3",
                "--interval-seconds",
                "0.25",
                "--loop-sleep-seconds",
                "1.5",
                "--reason",
                "manual_daemon_start",
                "--owner-token",
                "owner-1",
            ]
        )
        with (
            patch(
                "tdxquant.cli.run_bridge_watch_supervisor_daemon_start",
                return_value={"ok": True, "result": {"state": "starting"}},
            ) as mocked_run,
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 0)
        mocked_run.assert_called_once_with(
            registry_path="runtime/bridge/master-workers.json",
            worker_id="worker-a",
            max_ticks=3,
            interval_seconds=0.25,
            loop_sleep_seconds=1.5,
            reason="manual_daemon_start",
            owner_token="owner-1",
        )
        self.assertEqual(json.loads(stdout.getvalue()), {"ok": True, "result": {"state": "starting"}})

    def test_handle_bridge_watch_supervisor_daemon_stop_dispatches_registry_client(self) -> None:
        args = build_parser().parse_args(
            [
                "bridge",
                "watch-supervisor-daemon-stop",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--owner-token",
                "owner-1",
                "--reason",
                "manual_daemon_stop",
            ]
        )
        with (
            patch(
                "tdxquant.cli.run_bridge_watch_supervisor_daemon_stop",
                return_value={"ok": True, "result": {"state": "stopping"}},
            ) as mocked_run,
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 0)
        mocked_run.assert_called_once_with(
            registry_path="runtime/bridge/master-workers.json",
            worker_id="worker-a",
            owner_token="owner-1",
            reason="manual_daemon_stop",
        )
        self.assertEqual(json.loads(stdout.getvalue()), {"ok": True, "result": {"state": "stopping"}})

    def test_handle_bridge_watch_status_summary_view_projects_statefile_ownership(self) -> None:
        args = build_parser().parse_args(
            [
                "bridge",
                "watch-status",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--view",
                "summary",
            ]
        )
        ownership = {
            "schema_version": "tdx.subscription_watch.statefile_ownership.v1",
            "status": "mismatch",
            "reason_codes": ["PIDFILE_MISSING", "PID_MISMATCH"],
            "statefile_exists": True,
            "pidfile_exists": False,
            "lockfile_exists": False,
            "active": True,
            "control_state": "starting",
            "payload_pid": 4321,
            "owned_pid": None,
            "pid_matches_owned_state": False,
            "process_alive": False,
            "boundary": "local_statefile_pidfile_only;does_not_claim_provider_readiness_or_lifecycle_control",
        }
        lifecycle_readiness = {
            "schema_version": "tdx.subscription_watch.lifecycle_readiness.v1",
            "ready": False,
            "decision": "blocked",
            "reason_codes": ["STATEFILE_OWNERSHIP_NOT_OWNED_ACTIVE"],
            "run_id": "run-001",
            "state": "starting",
            "active": True,
            "has_start_request": False,
            "start_request_summary": None,
            "restart_backoff_active": False,
            "statefile_ownership_status": "mismatch",
            "statefile_pid_matches_owned_state": False,
            "statefile_process_alive": False,
            "supervisor_daemon_status": "missing",
            "supervisor_daemon_control_allowed": False,
            "boundary": "read_only_lifecycle_readiness;does_not_execute_lifecycle_control",
        }
        detailed_payload = {
            "ok": True,
            "result": {
                "status": "starting",
                "control": {"state": "starting", "active": True, "run_id": "run-001", "pid": 4321},
                "watch_status": None,
                "statefile_ownership": ownership,
                "status_summary": {
                        "schema_version": "tdx.subscription_watch.status_summary.v1",
                        "overall_status": "starting",
                        "boundary": "summary_projection_only; optional heartbeat/watermark/reconnect staleness evaluation only; does not change reconnect/backoff behavior",
                        "statefile_ownership": ownership,
                        "lifecycle_readiness": lifecycle_readiness,
                    },
                },
            }
        with (
            patch("tdxquant.cli.run_bridge_watch_status", return_value=detailed_payload) as mocked_run,
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 0)
        mocked_run.assert_called_once_with(
            registry_path="runtime/bridge/master-workers.json",
            worker_id="worker-a",
            heartbeat_stale_after_seconds=None,
            watermark_stale_after_seconds=None,
            reconnect_stale_after_seconds=None,
        )
        output = json.loads(stdout.getvalue())
        self.assertEqual(output["result"]["status_summary"]["statefile_ownership"], ownership)
        self.assertEqual(output["result"]["status_summary"]["lifecycle_readiness"], lifecycle_readiness)
        self.assertEqual(
            output["result"]["status_summary"]["boundary"],
            "summary_projection_only; optional heartbeat/watermark/reconnect staleness evaluation only; does not change reconnect/backoff behavior",
        )
        self.assertNotIn("statefile_ownership", output["result"]["runtime"])

    def test_handle_bridge_watch_status_summary_view_projects_governance_rollup(self) -> None:
        args = build_parser().parse_args(
            [
                "bridge",
                "watch-status",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--heartbeat-stale-after-seconds",
                "60",
                "--reconnect-stale-after-seconds",
                "180",
                "--view",
                "summary",
            ]
        )
        detailed_payload = {
            "ok": True,
                "result": {
                    "status": "running",
                    "control": {"state": "running", "active": True, "run_id": "run-001", "pid": 1234},
                    "watch_status": {"state": "running", "run_id": "run-001"},
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
                            "watch_state": "running",
                            "has_watch_status": True,
                            "has_control_run_id": True,
                            "has_watch_run_id": True,
                            "run_id_match": True,
                            "state_match": True,
                            "has_control_pid": True,
                            "has_mismatch": False,
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
                        "heartbeat": {"staleness": "stale"},
                        "watermark": {"staleness": "not_evaluated"},
                        "governance": {
                        "decision": "manual_review",
                        "requires_manual_review": True,
                        "staleness_evaluated": True,
                        "boundary": "advisory_only; does_not_trigger_reconnect_backoff_restart_or_lifecycle_changes",
                        "reasons": [
                            "heartbeat:stale",
                            "watermark:stale",
                            "reconnect:stale",
                            "overall_status:degraded",
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
                        "action_summary": {
                            "count": 4,
                            "primary_action": "review_subscription_watch_heartbeat",
                            "primary_reason": "heartbeat:stale",
                            "primary_reason_source": "heartbeat",
                            "primary_severity": "review",
                            "severity": "review",
                            "severity_key_count": 1,
                            "action_name_counts": {
                                "review_subscription_watch_heartbeat": 1,
                                "review_subscription_watch_reconnect": 1,
                                "review_subscription_watch_resilience": 1,
                                "review_subscription_watch_watermark": 1,
                            },
                            "action_name_key_count": 4,
                            "reason_source_counts": {
                                "heartbeat": 1,
                                "overall_status": 1,
                                "reconnect": 1,
                                "watermark": 1,
                            },
                            "reason_source_key_count": 4,
                            "reason_code_counts": {
                                "heartbeat:stale": 1,
                                "overall_status:degraded": 1,
                                "reconnect:stale": 1,
                                "watermark:stale": 1,
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
                        "action_count": 4,
                        "actions": [
                            {
                                "action": "review_subscription_watch_heartbeat",
                                "reason": "heartbeat:stale",
                                "severity": "review",
                                "description": "Inspect heartbeat freshness.",
                            },
                            {
                                "action": "review_subscription_watch_watermark",
                                "reason": "watermark:stale",
                                "severity": "review",
                                "description": "Inspect event watermark freshness.",
                            },
                            {
                                "action": "review_subscription_watch_reconnect",
                                "reason": "reconnect:stale",
                                "severity": "review",
                                "description": "Inspect reconnect duration.",
                            },
                            {
                                "action": "review_subscription_watch_resilience",
                                "reason": "overall_status:degraded",
                                "severity": "review",
                                "description": "Inspect long-run process health.",
                            },
                        ],
                        "evaluation_summary": {
                            "evaluated_components": ["heartbeat"],
                            "primary_evaluated_component": "heartbeat",
                            "stale_components": ["heartbeat"],
                            "primary_stale_component": "heartbeat",
                            "has_stale_component": True,
                            "primary_fresh_component": None,
                            "has_fresh_component": False,
                            "not_evaluated_components": ["watermark", "reconnect"],
                            "primary_not_evaluated_component": "watermark",
                            "has_not_evaluated_component": True,
                            "all_components_evaluated": False,
                            "evaluated_count": 1,
                            "stale_count": 1,
                            "fresh_count": 0,
                            "not_evaluated_count": 2,
                            "component_status_counts": {"not_evaluated": 2, "stale": 1},
                            "component_status_key_count": 2,
                            "evaluated_status_counts": {"stale": 1},
                            "evaluated_status_key_count": 1,
                        },
                    },
                },
            },
        }
        with (
            patch("tdxquant.cli.run_bridge_watch_status", return_value=detailed_payload) as mocked_run,
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 0)
        mocked_run.assert_called_once_with(
            registry_path="runtime/bridge/master-workers.json",
            worker_id="worker-a",
            heartbeat_stale_after_seconds=60.0,
            watermark_stale_after_seconds=None,
            reconnect_stale_after_seconds=180.0,
        )
        self.assertEqual(
            json.loads(stdout.getvalue()),
            {
                "ok": True,
                "result": {
                    "mode": "summary",
                    "worker": "worker-a",
                    "status": "manual_review",
                    "runtime": {
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
                            "watch_state": "running",
                            "has_watch_status": True,
                            "has_control_run_id": True,
                            "has_watch_run_id": True,
                            "run_id_match": True,
                            "state_match": True,
                            "has_control_pid": True,
                            "has_mismatch": False,
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
                        "heartbeat": {"staleness": "stale"},
                        "watermark": {"staleness": "not_evaluated"},
                    },
                    "governance": {
                        "decision": "manual_review",
                        "requires_manual_review": True,
                        "staleness_evaluated": True,
                        "boundary": "advisory_only; does_not_trigger_reconnect_backoff_restart_or_lifecycle_changes",
                        "reason_count": 4,
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
                        "reason_samples": ["heartbeat:stale", "watermark:stale", "reconnect:stale"],
                        "reason_sample_count": 3,
                        "reason_sample_hidden_count": 1,
                        "reason_sample_limit": 3,
                        "reason_sample_truncated": True,
                        "action_count": 4,
                        "action_summary": {
                            "count": 4,
                            "primary_action": "review_subscription_watch_heartbeat",
                            "primary_reason": "heartbeat:stale",
                            "primary_reason_source": "heartbeat",
                            "primary_severity": "review",
                            "severity": "review",
                            "severity_key_count": 1,
                            "action_name_counts": {
                                "review_subscription_watch_heartbeat": 1,
                                "review_subscription_watch_reconnect": 1,
                                "review_subscription_watch_resilience": 1,
                                "review_subscription_watch_watermark": 1,
                            },
                            "action_name_key_count": 4,
                            "reason_source_counts": {
                                "heartbeat": 1,
                                "overall_status": 1,
                                "reconnect": 1,
                                "watermark": 1,
                            },
                            "reason_source_key_count": 4,
                            "reason_code_counts": {
                                "heartbeat:stale": 1,
                                "overall_status:degraded": 1,
                                "reconnect:stale": 1,
                                "watermark:stale": 1,
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
                        "decision_summary": {
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
                            "primary_action": "review_subscription_watch_heartbeat",
                            "primary_action_reason": "heartbeat:stale",
                            "primary_action_reason_source": "heartbeat",
                            "has_reasons": True,
                            "has_actions": True,
                        },
                        "action_samples": [
                            {
                                "action": "review_subscription_watch_heartbeat",
                                "reason": "heartbeat:stale",
                                "severity": "review",
                            },
                            {
                                "action": "review_subscription_watch_watermark",
                                "reason": "watermark:stale",
                                "severity": "review",
                            },
                            {
                                "action": "review_subscription_watch_reconnect",
                                "reason": "reconnect:stale",
                                "severity": "review",
                            },
                        ],
                        "action_sample_count": 3,
                        "action_sample_hidden_count": 1,
                        "action_sample_limit": 3,
                        "action_sample_truncated": True,
                        "sample_summary": {
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
                        "evaluation_summary": {
                            "evaluated_components": ["heartbeat"],
                            "primary_evaluated_component": "heartbeat",
                            "stale_components": ["heartbeat"],
                            "primary_stale_component": "heartbeat",
                            "has_stale_component": True,
                            "primary_fresh_component": None,
                            "has_fresh_component": False,
                            "not_evaluated_components": ["watermark", "reconnect"],
                            "primary_not_evaluated_component": "watermark",
                            "has_not_evaluated_component": True,
                            "all_components_evaluated": False,
                            "evaluated_count": 1,
                            "stale_count": 1,
                            "fresh_count": 0,
                            "not_evaluated_count": 2,
                            "component_status_counts": {"not_evaluated": 2, "stale": 1},
                            "component_status_key_count": 2,
                            "evaluated_status_counts": {"stale": 1},
                            "evaluated_status_key_count": 1,
                        },
                        "evaluation_rollup": {
                            "staleness_evaluated": True,
                            "evaluated_count": 1,
                            "stale_count": 1,
                            "fresh_count": 0,
                            "not_evaluated_count": 2,
                            "primary_evaluated_component": "heartbeat",
                            "primary_stale_component": "heartbeat",
                            "primary_fresh_component": None,
                            "primary_not_evaluated_component": "watermark",
                            "has_evaluated_component": True,
                            "has_stale_component": True,
                            "has_fresh_component": False,
                            "has_not_evaluated_component": True,
                            "all_components_evaluated": False,
                            "component_status_key_count": 2,
                            "evaluated_status_key_count": 1,
                        },
                    },
                },
            },
        )
        summary_payload = json.loads(stdout.getvalue())["result"]
        self.assertNotIn("control", summary_payload)
        self.assertNotIn("watch_status", summary_payload)
        self.assertNotIn("reasons", summary_payload["governance"])
        self.assertNotIn("actions", summary_payload["governance"])
        self.assertEqual(summary_payload["governance"]["reason_sample_count"], 3)
        self.assertEqual(summary_payload["governance"]["reason_sample_hidden_count"], 1)
        self.assertEqual(summary_payload["governance"]["action_sample_count"], 3)
        self.assertEqual(summary_payload["governance"]["action_sample_hidden_count"], 1)
        self.assertEqual(
            summary_payload["governance"]["sample_summary"],
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

    def test_handle_bridge_watch_status_diagnostics_view_projects_rollup_flags(self) -> None:
        args = build_parser().parse_args(
            [
                "bridge",
                "watch-status",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--view",
                "diagnostics",
            ]
        )
        detailed_payload = {
            "ok": True,
            "result": {
                "status": "running",
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
                "watch_status": {"state": "degraded", "run_id": "run-002"},
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
                    "lifecycle_readiness": {
                        "schema_version": "tdx.subscription_watch.lifecycle_readiness.v1",
                        "ready": False,
                        "decision": "blocked",
                        "reason_codes": ["BACKOFF_ACTIVE"],
                        "run_id": "run-001",
                        "state": "running",
                        "active": True,
                        "has_start_request": True,
                        "start_request_summary": {
                            "stock_count": 2,
                            "has_max_events": True,
                            "has_max_seconds": True,
                            "has_poll_interval": True,
                        },
                        "restart_backoff_active": True,
                        "statefile_ownership_status": "owned_active",
                        "statefile_pid_matches_owned_state": True,
                        "statefile_process_alive": True,
                        "supervisor_daemon_status": "running",
                        "supervisor_daemon_control_allowed": True,
                        "boundary": "read_only_lifecycle_readiness;does_not_execute_lifecycle_control",
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
            },
        }
        with (
            patch("tdxquant.cli.run_bridge_watch_status", return_value=detailed_payload) as mocked_run,
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 0)
        mocked_run.assert_called_once_with(
            registry_path="runtime/bridge/master-workers.json",
            worker_id="worker-a",
            heartbeat_stale_after_seconds=None,
            watermark_stale_after_seconds=None,
            reconnect_stale_after_seconds=None,
        )
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["result"]["mode"], "diagnostics")
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
                "lifecycle_readiness": {
                    "schema_version": "tdx.subscription_watch.lifecycle_readiness.v1",
                    "ready": False,
                    "decision": "blocked",
                    "reason_codes": ["BACKOFF_ACTIVE"],
                    "run_id": "run-001",
                    "state": "running",
                    "active": True,
                    "has_start_request": True,
                    "start_request_summary": {
                        "stock_count": 2,
                        "has_max_events": True,
                        "has_max_seconds": True,
                        "has_poll_interval": True,
                    },
                    "restart_backoff_active": True,
                    "statefile_ownership_status": "owned_active",
                    "statefile_pid_matches_owned_state": True,
                    "statefile_process_alive": True,
                    "supervisor_daemon_status": "running",
                    "supervisor_daemon_control_allowed": True,
                    "boundary": "read_only_lifecycle_readiness;does_not_execute_lifecycle_control",
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

    def test_handle_bridge_watch_status_runbook_view_projects_operator_checklist(self) -> None:
        args = build_parser().parse_args(
            [
                "bridge",
                "watch-status",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--view",
                "runbook",
            ]
        )
        detailed_payload = {
            "ok": True,
            "result": {
                "status": "running",
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
                "watch_status": {"state": "running", "run_id": "run-001"},
                "status_summary": {
                    "schema_version": "tdx.subscription_watch.status_summary.v1",
                    "overall_status": "active",
                    "control_rollup": {"control_state": "running", "control_active": True},
                    "consistency_rollup": {
                        "control_state": "running",
                        "watch_state": "running",
                        "has_watch_status": True,
                        "run_id_match": True,
                        "state_match": True,
                        "has_mismatch": False,
                    },
                    "lifecycle_readiness": {
                        "schema_version": "tdx.subscription_watch.lifecycle_readiness.v1",
                        "ready": True,
                        "decision": "ready",
                        "reason_codes": [],
                        "run_id": "run-001",
                        "state": "running",
                        "active": True,
                        "has_start_request": True,
                        "start_request_summary": {
                            "stock_count": 2,
                            "has_max_events": True,
                            "has_max_seconds": True,
                            "has_poll_interval": True,
                        },
                        "restart_backoff_active": False,
                        "statefile_ownership_status": "owned_active",
                        "statefile_pid_matches_owned_state": True,
                        "statefile_process_alive": True,
                        "supervisor_daemon_status": "missing",
                        "supervisor_daemon_control_allowed": False,
                        "boundary": "read_only_lifecycle_readiness;does_not_execute_lifecycle_control",
                    },
                    "governance": {
                        "decision": "observe",
                        "requires_manual_review": False,
                        "staleness_evaluated": True,
                        "boundary": "advisory_only; does_not_trigger_reconnect_backoff_restart_or_lifecycle_changes",
                        "evaluation_summary": {
                            "has_stale_component": False,
                            "has_not_evaluated_component": False,
                            "all_components_evaluated": True,
                        },
                    },
                },
            },
        }
        with (
            patch("tdxquant.cli.run_bridge_watch_status", return_value=detailed_payload) as mocked_run,
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 0)
        mocked_run.assert_called_once_with(
            registry_path="runtime/bridge/master-workers.json",
            worker_id="worker-a",
            heartbeat_stale_after_seconds=None,
            watermark_stale_after_seconds=None,
            reconnect_stale_after_seconds=None,
        )
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["result"]["mode"], "runbook")
        self.assertEqual(
            payload["result"]["runbook"],
            {
                "schema_version": "tdx.subscription_watch.operator_runbook.v1",
                "decision": "ready",
                "manual_review_required": False,
                "check_count": 5,
                "blocking_check_count": 0,
                "checks": [
                    {
                        "code": "lifecycle_readiness",
                        "status": "passed",
                        "decision": "ready",
                        "reason_codes": [],
                        "action": "none",
                    },
                    {
                        "code": "governance_review",
                        "status": "passed",
                        "requires_manual_review": False,
                        "action": "none",
                    },
                    {
                        "code": "runtime_consistency",
                        "status": "passed",
                        "has_mismatch": False,
                        "action": "none",
                    },
                    {
                        "code": "staleness",
                        "status": "passed",
                        "has_stale_component": False,
                        "has_not_evaluated_component": False,
                        "action": "none",
                    },
                    {
                        "code": "restart_backoff",
                        "status": "passed",
                        "active": False,
                        "action": "none",
                    },
                ],
                "boundary": "read_only_operator_runbook;does_not_execute_lifecycle_control",
            },
        )
        self.assertNotIn("control", payload["result"])
        self.assertNotIn("watch_status", payload["result"])

    def test_handle_bridge_watch_events_dispatches_registry_client(self) -> None:
        args = build_parser().parse_args(
            [
                "bridge",
                "watch-events",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--run-id",
                "run-001",
                "--tail",
                "25",
            ]
        )
        with (
            patch("tdxquant.cli.run_bridge_watch_events", return_value={"ok": True, "result": {"events": []}}) as mocked_run,
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 0)
        mocked_run.assert_called_once_with(
            registry_path="runtime/bridge/master-workers.json",
            worker_id="worker-a",
            run_id="run-001",
            tail=25,
        )
        self.assertEqual(json.loads(stdout.getvalue()), {"ok": True, "result": {"events": []}})

    def test_handle_bridge_watch_events_stream_dispatches_registry_client_as_raw_text(self) -> None:
        args = build_parser().parse_args(
            [
                "bridge",
                "watch-events-stream",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--run-id",
                "run-001",
                "--from",
                "run-001:event:7",
                "--no-follow",
                "--heartbeat-seconds",
                "5",
            ]
        )
        with (
            patch("tdxquant.cli.run_bridge_watch_event_stream", return_value="event: heartbeat\n\n") as mocked_run,
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 0)
        mocked_run.assert_called_once_with(
            registry_path="runtime/bridge/master-workers.json",
            worker_id="worker-a",
            run_id="run-001",
            from_cursor="run-001:event:7",
            follow=False,
            heartbeat_seconds=5,
        )
        self.assertEqual(stdout.getvalue(), "event: heartbeat\n\n")

    def test_handle_bridge_watch_start_dispatches_registry_client(self) -> None:
        args = build_parser().parse_args(
            [
                "bridge",
                "watch-start",
                "--registry",
                "runtime/bridge/master-workers.json",
                "--worker",
                "worker-a",
                "--code",
                "000001.SZ",
                "--max-events",
                "5",
                "--max-seconds",
                "30",
                "--poll-interval",
                "0.5",
                "--idempotency-key",
                "idem-001",
            ]
        )
        with (
            patch("tdxquant.cli.run_bridge_watch_start", return_value={"ok": True, "result": {"status": "started"}}) as mocked_run,
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 0)
        mocked_run.assert_called_once_with(
            registry_path="runtime/bridge/master-workers.json",
            worker_id="worker-a",
            stock_list=["000001.SZ"],
            max_events=5,
            max_seconds=30.0,
            poll_interval=0.5,
            idempotency_key="idem-001",
        )
        self.assertEqual(json.loads(stdout.getvalue()), {"ok": True, "result": {"status": "started"}})

    def test_handle_bridge_watch_stop_dispatches_registry_client(self) -> None:
        args = build_parser().parse_args(
            ["bridge", "watch-stop", "--registry", "runtime/bridge/master-workers.json", "--worker", "worker-a"]
        )
        with (
            patch("tdxquant.cli.run_bridge_watch_stop", return_value={"ok": True, "result": {"status": "stopping"}}) as mocked_run,
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 0)
        mocked_run.assert_called_once_with(registry_path="runtime/bridge/master-workers.json", worker_id="worker-a")
        self.assertEqual(json.loads(stdout.getvalue()), {"ok": True, "result": {"status": "stopping"}})

    def test_handle_bridge_watch_status_returns_json_failure_for_unknown_worker(self) -> None:
        args = build_parser().parse_args(
            ["bridge", "watch-status", "--registry", "runtime/bridge/master-workers.json", "--worker", "worker-a"]
        )
        with (
            patch("tdxquant.cli.run_bridge_watch_status", side_effect=ValueError("unknown worker: worker-a")),
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            json.loads(stdout.getvalue()),
            {
                "ok": False,
                "result": None,
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "unknown worker: worker-a",
                    "details": {},
                },
            },
        )

    def test_handle_bridge_watch_status_returns_json_failure_for_missing_registry_path(self) -> None:
        args = build_parser().parse_args(
            ["bridge", "watch-status", "--registry", "runtime/bridge/missing.json", "--worker", "worker-a"]
        )
        with (
            patch("tdxquant.cli.run_bridge_watch_status", side_effect=FileNotFoundError("runtime/bridge/missing.json")),
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            json.loads(stdout.getvalue()),
            {
                "ok": False,
                "result": None,
                "error": {
                    "code": "REGISTRY_NOT_FOUND",
                    "message": "runtime/bridge/missing.json",
                    "details": {},
                },
            },
        )

    def test_handle_bridge_watch_status_returns_json_failure_for_missing_token_env(self) -> None:
        args = build_parser().parse_args(
            ["bridge", "watch-status", "--registry", "runtime/bridge/master-workers.json", "--worker", "worker-a"]
        )
        with (
            patch(
                "tdxquant.cli.run_bridge_watch_status",
                side_effect=ValueError("missing bridge token in environment: BRIDGE_TOKEN_A"),
            ),
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            json.loads(stdout.getvalue()),
            {
                "ok": False,
                "result": None,
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "missing bridge token in environment: BRIDGE_TOKEN_A",
                    "details": {},
                },
            },
        )

    def test_handle_bridge_watch_status_returns_json_failure_for_bridge_request_failure(self) -> None:
        args = build_parser().parse_args(
            ["bridge", "watch-status", "--registry", "runtime/bridge/master-workers.json", "--worker", "worker-a"]
        )
        with (
            patch("tdxquant.cli.run_bridge_watch_status", side_effect=RuntimeError("bridge worker request failed: timed out")),
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            exit_code = _handle_bridge_subcommand(args)

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            json.loads(stdout.getvalue()),
            {
                "ok": False,
                "result": None,
                "error": {
                    "code": "BRIDGE_REQUEST_FAILED",
                    "message": "bridge worker request failed: timed out",
                    "details": {},
                },
            },
        )

    def test_main_pingan_buy_submit_once_uses_trade_manager(self) -> None:
        service = MagicMock()
        service.place_order.return_value = _snapshot(gateway_order_id="gw-main-submit-once")
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli._build_trader_service", return_value=service) as mocked_service_builder,
            patch("tdxquant.cli._emit_pingan_contract_log"),
            patch(
                "sys.argv",
                [
                    "tdxquant",
                    "pingan-buy-submit-once",
                    "--port",
                    "COM3",
                    "--code",
                    "000001",
                    "--price",
                    "10.00",
                    "--quantity",
                    "100",
                ],
            ),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        self.assertEqual(mocked_service_builder.call_args.kwargs["execution_mode"], "submit_once")
        service.place_order.assert_called_once()

    def test_main_trade_buy_uses_trade_subcommand_handler(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"result_dialog": {}})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli._handle_trade_subcommand", return_value=expected) as mocked,
            patch("tdxquant.cli._emit_pingan_contract_log"),
            patch("sys.argv", ["tdxquant", "trade", "buy", "--port", "COM3", "--code", "000001", "--price", "10.00", "--quantity", "100"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once()

    def test_main_trade_submit_once_uses_trade_subcommand_handler(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"result_dialog": {}})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli._handle_trade_subcommand", return_value=expected) as mocked,
            patch("tdxquant.cli._emit_pingan_contract_log"),
            patch("sys.argv", ["tdxquant", "trade", "submit-once", "--port", "COM3", "--code", "000001", "--price", "10.00", "--quantity", "100"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once()

    def test_main_report_daily_uses_report_subcommand_handler(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli._handle_report_subcommand", return_value=expected) as mocked,
            patch("sys.argv", ["tdxquant", "report", "daily", "--date", "2026-04-26"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once()

    def test_main_tdx_get_trading_dates_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_get_trading_dates", return_value=expected) as mocked,
            patch("sys.argv", ["tdxquant", "tdx-get-trading-dates", "--market", "SH", "--count", "10"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(
            market="SH",
            start_time="",
            end_time="",
            count=10,
            strategy_path=None,
        )

    def test_main_tdx_data_divid_factors_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_divid_factors", return_value=expected) as mocked,
            patch(
                "sys.argv",
                ["tdxquant", "tdx-data-divid-factors", "--code", "688318.SH", "--start-time", "20200101", "--end-time", "20241231"],
            ),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(
            stock_code="688318.SH",
            start_time="20200101",
            end_time="20241231",
            strategy_path=None,
        )

    def test_main_tdx_data_ipo_info_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_ipo_info", return_value=expected) as mocked,
            patch("sys.argv", ["tdxquant", "tdx-data-ipo-info", "--ipo-type", "2", "--ipo-date", "1"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(
            ipo_type=2,
            ipo_date=1,
            strategy_path=None,
        )

    def test_main_tdx_data_financial_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_financial_data", return_value=expected) as mocked,
            patch(
                "sys.argv",
                [
                    "tdxquant",
                    "tdx-data-financial",
                    "--code",
                    "688318.SH",
                    "--field",
                    "FN1",
                    "--field",
                    "FN2",
                    "--start-time",
                    "20240101",
                    "--end-time",
                    "20241231",
                    "--report-type",
                    "announce_time",
                ],
            ),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(
            stock_list=["688318.SH"],
            field_list=["FN1", "FN2"],
            start_time="20240101",
            end_time="20241231",
            report_type="announce_time",
            strategy_path=None,
        )

    def test_main_tdx_data_financial_by_date_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_financial_data_by_date", return_value=expected) as mocked,
            patch(
                "sys.argv",
                [
                    "tdxquant",
                    "tdx-data-financial-by-date",
                    "--code",
                    "688318.SH",
                    "--field",
                    "FN193",
                    "--year",
                    "2025",
                    "--mmdd",
                    "331",
                ],
            ),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(
            stock_list=["688318.SH"],
            field_list=["FN193"],
            year=2025,
            mmdd=331,
            strategy_path=None,
        )

    def test_main_tdx_data_stock_transaction_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_stock_transaction_data", return_value=expected) as mocked,
            patch(
                "sys.argv",
                [
                    "tdxquant",
                    "tdx-data-stock-transaction",
                    "--code",
                    "600519.SH",
                    "--field",
                    "GP01",
                    "--field",
                    "GP02",
                    "--start-time",
                    "20240101",
                    "--end-time",
                    "20241231",
                ],
            ),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(
            stock_list=["600519.SH"],
            field_list=["GP01", "GP02"],
            start_time="20240101",
            end_time="20241231",
            strategy_path=None,
        )

    def test_main_tdx_data_stock_transaction_by_date_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_stock_transaction_data_by_date", return_value=expected) as mocked,
            patch(
                "sys.argv",
                [
                    "tdxquant",
                    "tdx-data-stock-transaction-by-date",
                    "--code",
                    "600519.SH",
                    "--field",
                    "GP01",
                    "--year",
                    "0",
                    "--mmdd",
                    "0",
                ],
            ),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(
            stock_list=["600519.SH"],
            field_list=["GP01"],
            year=0,
            mmdd=0,
            strategy_path=None,
        )

    def test_main_tdx_data_sector_transaction_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_sector_transaction_data", return_value=expected) as mocked,
            patch(
                "sys.argv",
                [
                    "tdxquant",
                    "tdx-data-sector-transaction",
                    "--code",
                    "880660.SH",
                    "--field",
                    "BK5",
                    "--field",
                    "BK6",
                    "--start-time",
                    "20240101",
                    "--end-time",
                    "20241231",
                ],
            ),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(
            stock_list=["880660.SH"],
            field_list=["BK5", "BK6"],
            start_time="20240101",
            end_time="20241231",
            strategy_path=None,
        )

    def test_main_tdx_data_sector_transaction_by_date_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_sector_transaction_data_by_date", return_value=expected) as mocked,
            patch(
                "sys.argv",
                [
                    "tdxquant",
                    "tdx-data-sector-transaction-by-date",
                    "--code",
                    "880660.SH",
                    "--field",
                    "BK9",
                    "--year",
                    "0",
                    "--mmdd",
                    "0",
                ],
            ),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(
            stock_list=["880660.SH"],
            field_list=["BK9"],
            year=0,
            mmdd=0,
            strategy_path=None,
        )

    def test_main_tdx_data_market_transaction_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_market_transaction_data", return_value=expected) as mocked,
            patch(
                "sys.argv",
                [
                    "tdxquant",
                    "tdx-data-market-transaction",
                    "--field",
                    "SC01",
                    "--field",
                    "SC02",
                    "--start-time",
                    "20250101",
                    "--end-time",
                    "20250102",
                ],
            ),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(
            field_list=["SC01", "SC02"],
            start_time="20250101",
            end_time="20250102",
            strategy_path=None,
        )

    def test_main_tdx_data_market_transaction_by_date_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_market_transaction_data_by_date", return_value=expected) as mocked,
            patch(
                "sys.argv",
                [
                    "tdxquant",
                    "tdx-data-market-transaction-by-date",
                    "--field",
                    "SC06",
                    "--year",
                    "0",
                    "--mmdd",
                    "0",
                ],
            ),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(
            field_list=["SC06"],
            year=0,
            mmdd=0,
            strategy_path=None,
        )

    def test_main_tdx_refresh_kline_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_refresh_kline", return_value=expected) as mocked,
            patch("sys.argv", ["tdxquant", "tdx-refresh-kline", "--code", "688260.SH", "--period", "1d"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(
            stock_list=["688260.SH"],
            period="1d",
            strategy_path=None,
        )

    def test_main_tdx_download_file_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_download_file", return_value=expected) as mocked,
            patch(
                "sys.argv",
                ["tdxquant", "tdx-download-file", "--code", "688318.SH", "--down-time", "20250101", "--down-type", "1"],
            ),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(
            stock_code="688318.SH",
            down_time="20250101",
            down_type=1,
            strategy_path=None,
        )

    def test_main_tdx_send_warn_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_send_warn", return_value=expected) as mocked,
            patch(
                "sys.argv",
                [
                    "tdxquant",
                    "tdx-send-warn",
                    "--code",
                    "688318.SH",
                    "--code",
                    "600519.SH",
                    "--time",
                    "20251215141115",
                    "--time",
                    "20251215142100",
                    "--price",
                    "123.45",
                    "--close",
                    "122.50",
                    "--volume",
                    "1000",
                    "--bs-flag",
                    "0",
                    "--warn-type",
                    "0",
                    "--reason",
                    "价格突破预警线",
                    "--count",
                    "2",
                ],
            ),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
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
            strategy_path=None,
        )

    def test_main_tdx_get_user_sector_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_get_user_sector", return_value=expected) as mocked,
            patch("sys.argv", ["tdxquant", "tdx-get-user-sector"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(strategy_path=None)

    def test_main_tdx_capabilities_replay_uses_manager_instead_of_live_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"summary": {"total": 4}})
        manager = MagicMock()
        manager.runtime.capabilities.return_value = expected
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_provider_capabilities", side_effect=AssertionError("live bridge must not run")),
            patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager,
            patch("sys.argv", ["tdxquant", "tdx-capabilities", "--provider-mode", "replay"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.runtime.capabilities.assert_called_once_with()

    def test_flat_tdx_data_stock_info_replay_uses_manager_instead_of_live_bridge(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-stock-info",
                "--code",
                "688260.SH",
                "--field",
                "symbol",
                "--field",
                "name",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "market.stock_info"}},
        )
        manager = MagicMock()
        manager.market.stock_info.return_value = expected
        with (
            patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager,
            patch("tdxquant.cli.run_tdx_data_stock_info", side_effect=AssertionError("live bridge called")),
        ):
            result = _run_flat_replay_provider_command(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.market.stock_info.assert_called_once_with("688260.SH", fields=["symbol", "name"])

    def test_flat_tdx_data_market_snapshot_replay_uses_manager_instead_of_live_bridge(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-market-snapshot",
                "--code",
                "000001.SZ",
                "--field",
                "Now",
                "--field",
                "Volume",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "market.market_snapshot"}},
        )
        manager = MagicMock()
        manager.market.market_snapshot.return_value = expected
        with (
            patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager,
            patch("tdxquant.cli.run_tdx_market_snapshot", side_effect=AssertionError("live bridge called")),
        ):
            result = _run_flat_replay_provider_command(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.market.market_snapshot.assert_called_once_with("000001.SZ", fields=["Now", "Volume"])

    def test_flat_tdx_data_more_info_replay_uses_manager_instead_of_live_bridge(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-more-info",
                "--code",
                "688260.SH",
                "--field",
                "symbol",
                "--field",
                "industry",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "market.more_info"}},
        )
        manager = MagicMock()
        manager.market.more_info.return_value = expected
        with (
            patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager,
            patch("tdxquant.cli.run_tdx_more_info", side_effect=AssertionError("live bridge called")),
        ):
            result = _run_flat_replay_provider_command(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.market.more_info.assert_called_once_with("688260.SH", fields=["symbol", "industry"])

    def test_flat_tdx_data_cb_info_replay_uses_manager_instead_of_live_bridge(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-cb-info",
                "--code",
                "113015.SZ",
                "--field",
                "symbol",
                "--field",
                "name",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "market.cb_info"}},
        )
        manager = MagicMock()
        manager.market.cb_info.return_value = expected
        with (
            patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager,
            patch("tdxquant.cli.run_tdx_cb_info", side_effect=AssertionError("live bridge called")),
        ):
            result = _run_flat_replay_provider_command(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.market.cb_info.assert_called_once_with("113015.SZ", fields=["symbol", "name"])

    def test_flat_tdx_data_gb_info_replay_uses_manager_instead_of_live_bridge(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-gb-info",
                "--code",
                "000001.SZ",
                "--date",
                "20250101",
                "--date",
                "20241231",
                "--count",
                "2",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "meta.gb_info"}},
        )
        manager = MagicMock()
        manager.meta.gb_info.return_value = expected
        with (
            patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager,
            patch("tdxquant.cli.run_tdx_gb_info", side_effect=AssertionError("live bridge called")),
        ):
            result = _run_flat_replay_provider_command(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.meta.gb_info.assert_called_once_with(
            stock_code="000001.SZ",
            date_list=["20250101", "20241231"],
            count=2,
        )

    def test_flat_tdx_data_ipo_info_replay_uses_manager_instead_of_live_bridge(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-ipo-info",
                "--ipo-type",
                "2",
                "--ipo-date",
                "1",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "meta.ipo_info"}},
        )
        manager = MagicMock()
        manager.meta.ipo_info.return_value = expected
        with (
            patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager,
            patch("tdxquant.cli.run_tdx_ipo_info", side_effect=AssertionError("live bridge called")),
        ):
            result = _run_flat_replay_provider_command(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.meta.ipo_info.assert_called_once_with(ipo_type=2, ipo_date=1)

    def test_flat_tdx_data_gp_one_replay_uses_manager_instead_of_live_bridge(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-gp-one",
                "--code",
                "000001.SZ",
                "--code",
                "600519.SH",
                "--field",
                "Now",
                "--field",
                "Volume",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "meta.gp_one_data"}},
        )
        manager = MagicMock()
        manager.meta.gp_one_data.return_value = expected
        with (
            patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager,
            patch("tdxquant.cli.run_tdx_gp_one_data", side_effect=AssertionError("live bridge called")),
        ):
            result = _run_flat_replay_provider_command(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.meta.gp_one_data.assert_called_once_with(
            stock_list=["000001.SZ", "600519.SH"],
            fields=["Now", "Volume"],
        )

    def test_flat_tdx_data_divid_factors_replay_uses_manager_instead_of_live_bridge(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-divid-factors",
                "--code",
                "688318.SH",
                "--start-time",
                "20200101",
                "--end-time",
                "20241231",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "meta.divid_factors"}},
        )
        manager = MagicMock()
        manager.meta.divid_factors.return_value = expected
        with (
            patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager,
            patch("tdxquant.cli.run_tdx_divid_factors", side_effect=AssertionError("live bridge called")),
        ):
            result = _run_flat_replay_provider_command(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.meta.divid_factors.assert_called_once_with(
            stock_code="688318.SH",
            start_time="20200101",
            end_time="20241231",
        )

    def test_flat_tdx_data_sector_list_replay_uses_manager_instead_of_live_bridge(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["tdx-data-sector-list", "--list-type", "0", "--provider-mode", "replay"])
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "meta.sector_list"}},
        )
        manager = MagicMock()
        manager.meta.sector_list.return_value = expected
        with (
            patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager,
            patch("tdxquant.cli.run_tdx_data_sector_list", side_effect=AssertionError("live bridge called")),
        ):
            result = _run_flat_replay_provider_command(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.meta.sector_list.assert_called_once_with(list_type=0)

    def test_flat_tdx_data_stock_transaction_by_date_replay_uses_manager_instead_of_live_bridge(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-stock-transaction-by-date",
                "--code",
                "000001.SZ",
                "--code",
                "000002.SZ",
                "--field",
                "price",
                "--field",
                "volume",
                "--year",
                "2025",
                "--mmdd",
                "101",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "transaction.stock_transaction_data_by_date"}},
        )
        manager = MagicMock()
        manager.transaction.stock_transaction_data_by_date.return_value = expected
        with (
            patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager,
            patch(
                "tdxquant.cli.run_tdx_stock_transaction_data_by_date",
                side_effect=AssertionError("live bridge called"),
            ),
        ):
            result = _run_flat_replay_provider_command(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.transaction.stock_transaction_data_by_date.assert_called_once_with(
            stock_list=["000001.SZ", "000002.SZ"],
            fields=["price", "volume"],
            year=2025,
            mmdd=101,
        )

    def test_flat_tdx_data_market_transaction_by_date_replay_uses_manager_instead_of_live_bridge(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-market-transaction-by-date",
                "--field",
                "field_a",
                "--field",
                "field_b",
                "--year",
                "2025",
                "--mmdd",
                "101",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "transaction.market_transaction_data_by_date"}},
        )
        manager = MagicMock()
        manager.transaction.market_transaction_data_by_date.return_value = expected
        with (
            patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager,
            patch(
                "tdxquant.cli.run_tdx_market_transaction_data_by_date",
                side_effect=AssertionError("live bridge called"),
            ),
        ):
            result = _run_flat_replay_provider_command(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.transaction.market_transaction_data_by_date.assert_called_once_with(
            fields=["field_a", "field_b"],
            year=2025,
            mmdd=101,
        )

    def test_flat_tdx_data_sector_transaction_by_date_replay_uses_manager_instead_of_live_bridge(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-sector-transaction-by-date",
                "--code",
                "880660.SH",
                "--code",
                "880001.SH",
                "--field",
                "BK9",
                "--field",
                "BK10",
                "--year",
                "2025",
                "--mmdd",
                "101",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "transaction.sector_transaction_data_by_date"}},
        )
        manager = MagicMock()
        manager.transaction.sector_transaction_data_by_date.return_value = expected
        with (
            patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager,
            patch(
                "tdxquant.cli.run_tdx_sector_transaction_data_by_date",
                side_effect=AssertionError("live bridge called"),
            ),
        ):
            result = _run_flat_replay_provider_command(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.transaction.sector_transaction_data_by_date.assert_called_once_with(
            stock_list=["880660.SH", "880001.SH"],
            fields=["BK9", "BK10"],
            year=2025,
            mmdd=101,
        )

    def test_flat_tdx_data_sector_transaction_replay_uses_manager_instead_of_live_bridge(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "tdx-data-sector-transaction",
                "--code",
                "880660.SH",
                "--code",
                "880001.SH",
                "--field",
                "BK5",
                "--field",
                "BK6",
                "--start-time",
                "20240101",
                "--end-time",
                "20241231",
                "--provider-mode",
                "replay",
            ]
        )
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="fixture",
            data={"query_meta": {"query_kind": "transaction.sector_transaction_data"}},
        )
        manager = MagicMock()
        manager.transaction.sector_transaction_data.return_value = expected
        with (
            patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager,
            patch(
                "tdxquant.cli.run_tdx_sector_transaction_data",
                side_effect=AssertionError("live bridge called"),
            ),
        ):
            result = _run_flat_replay_provider_command(args)
        self.assertIs(result, expected)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="replay",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.transaction.sector_transaction_data.assert_called_once_with(
            stock_list=["880660.SH", "880001.SH"],
            fields=["BK5", "BK6"],
            start_time="20240101",
            end_time="20241231",
        )

    def test_main_tdx_create_sector_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_create_sector", return_value=expected) as mocked,
            patch("sys.argv", ["tdxquant", "tdx-create-sector", "--block-code", "CSBK", "--block-name", "测试板块"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(block_code="CSBK", block_name="测试板块", strategy_path=None)

    def test_main_tdx_create_sector_forwards_mutation_safety_options(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_create_sector", return_value=expected) as mocked,
            patch(
                "sys.argv",
                [
                    "tdxquant",
                    "tdx-create-sector",
                    "--block-code",
                    "CSBK",
                    "--block-name",
                    "测试板块",
                    "--mutation-key",
                    "mk-001",
                    "--audit-dir",
                    "runtime/block-mutations",
                ],
            ),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(
            block_code="CSBK",
            block_name="测试板块",
            mutation_key="mk-001",
            audit_dir="runtime/block-mutations",
            strategy_path=None,
        )

    def test_main_tdx_delete_sector_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_delete_sector", return_value=expected) as mocked,
            patch("sys.argv", ["tdxquant", "tdx-delete-sector", "--block-code", "CSBK"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(block_code="CSBK", strategy_path=None)

    def test_main_tdx_rename_sector_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_rename_sector", return_value=expected) as mocked,
            patch("sys.argv", ["tdxquant", "tdx-rename-sector", "--block-code", "CSBK", "--block-name", "测试板块重命名"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(block_code="CSBK", block_name="测试板块重命名", strategy_path=None)

    def test_main_tdx_clear_sector_uses_bridge(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_clear_sector", return_value=expected) as mocked,
            patch("sys.argv", ["tdxquant", "tdx-clear-sector", "--block-code", "CSBK"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(block_code="CSBK", strategy_path=None)

    def test_main_tdx_send_user_block_forwards_mutation_safety_options(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_send_user_block", return_value=expected) as mocked,
            patch(
                "sys.argv",
                [
                    "tdxquant",
                    "tdx-send-user-block",
                    "--block-code",
                    "ZXG",
                    "--stock",
                    "000001.SZ",
                    "--show",
                    "--mutation-key",
                    "mk-send-1",
                    "--audit-dir",
                    "runtime/block-mutations",
                ],
            ),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked.assert_called_once_with(
            block_code="ZXG",
            stocks=["000001.SZ"],
            show=True,
            mutation_key="mk-send-1",
            audit_dir="runtime/block-mutations",
            strategy_path=None,
        )

    def test_main_tdx_send_user_block_rejected_prints_provider_result_envelope_and_nonzero_exit(self) -> None:
        expected = Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="rejected send_user_block because the current block state conflicts with the requested target state",
            data={
                "block_mutation": {
                    "schema_version": "2026-05-02",
                    "mutation_id": "mut-004",
                    "mutation_key": "mk-reject-1",
                    "operation": "send_user_block",
                    "status": "rejected",
                    "governance_decision": "reject",
                    "governance_reason": "missing_block",
                    "block_code": "MISSING",
                    "requested_stock_count": 1,
                    "show": True,
                },
                "artifacts": {
                    "audit_log_path": "runtime/block-mutations/mut-004.json",
                },
            },
        )
        expected._provider_artifacts = [
            {
                "kind": "block_mutation_audit",
                "path": "runtime/block-mutations/mut-004.json",
            }
        ]
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_send_user_block", return_value=expected),
            patch("builtins.print") as mocked_stdout_print,
            patch(
                "sys.argv",
                [
                    "tdxquant",
                    "tdx-send-user-block",
                    "--block-code",
                    "MISSING",
                    "--stock",
                    "000001.SZ",
                    "--show",
                    "--mutation-key",
                    "mk-reject-1",
                    "--audit-dir",
                    "runtime/block-mutations",
                ],
            ),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 1)
        parsed = json.loads(mocked_stdout_print.call_args.args[0])
        self.assertFalse(parsed["success"])
        self.assertFalse(parsed["ok"])
        self.assertEqual(parsed["code"], ErrorCode.INVALID_REQUEST.value)
        self.assertEqual(parsed["data"]["block_mutation"]["status"], "rejected")
        self.assertEqual(parsed["data"]["block_mutation"]["governance_reason"], "missing_block")
        self.assertEqual(parsed["artifacts"][0]["kind"], "block_mutation_audit")
        self.assertEqual(parsed["artifacts"][0]["path"], "runtime/block-mutations/mut-004.json")

    def test_main_tdx_block_read_watchlist_uses_manager(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={"snapshot": {"block_code": "ZXG", "symbols": ["000001.SZ"]}},
        )
        manager = MagicMock()
        manager.block.read_watchlist_snapshot.return_value = expected
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.TdxApiManager", return_value=manager) as mocked_manager,
            patch("builtins.print") as mocked_stdout_print,
            patch("sys.argv", ["tdxquant", "tdx-block-read-watchlist", "--block-code", "ZXG"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        mocked_manager.assert_called_once_with(
            profile="default",
            strategy_path=None,
            provider_mode="live",
            replay_fixture=None,
            replay_fixture_path=None,
        )
        manager.block.read_watchlist_snapshot.assert_called_once_with(block_code="ZXG")
        parsed = json.loads(mocked_stdout_print.call_args.args[0])
        self.assertTrue(parsed["ok"])
        self.assertEqual(parsed["capability"], "block.read_watchlist_snapshot")
        self.assertEqual(parsed["data"]["snapshot"]["block_code"], "ZXG")

    def test_main_api_block_read_watchlist_prints_provider_result_envelope(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={"snapshot": {"block_code": "ZXG", "symbols": ["000001.SZ"]}},
        )
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli._handle_api_subcommand", return_value=expected),
            patch("builtins.print") as mocked_stdout_print,
            patch("sys.argv", ["tdxquant", "api", "block-read-watchlist", "--block-code", "ZXG"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        parsed = json.loads(mocked_stdout_print.call_args.args[0])
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["capability"], "block.read_watchlist_snapshot")
        self.assertEqual(parsed["data"]["snapshot"]["block_code"], "ZXG")

    def test_main_catalog_summary_view_prints_summary_payload(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "summary_view": {
                    "mode": "run",
                    "target": {"type": "entry", "name": "daily-review"},
                    "ok": True,
                }
            },
        )
        mocked_print = mock_open()
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli._handle_catalog_subcommand", return_value=expected),
            patch("tdxquant.cli._emit_pingan_contract_log"),
            patch("pathlib.Path.write_text"),
            patch("builtins.print") as mocked_stdout_print,
            patch("sys.argv", ["tdxquant", "catalog", "run", "--entry", "daily-review", "--view", "summary"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        printed_payload = mocked_stdout_print.call_args.args[0]
        parsed = json.loads(printed_payload)
        self.assertEqual(parsed["mode"], "run")
        self.assertEqual(parsed["target"]["name"], "daily-review")

    def test_main_catalog_validate_summary_view_prints_summary_payload(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="validated command catalog registry",
            data={
                "summary_view": {
                    "mode": "validate",
                    "kind": "bundle",
                    "selected_label": "followup",
                    "bundle_count": 12,
                    "task_report_bundle_count": 12,
                    "task_report_bundle_samples": ["buy-pingan-complete-review", "confirm-complete-review"],
                    "invalid_count": 0,
                    "valid": True,
                    "non_execution": True,
                }
            },
        )
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli._handle_catalog_subcommand", return_value=expected),
            patch("builtins.print") as mocked_stdout_print,
            patch("sys.argv", ["tdxquant", "catalog", "validate", "--kind", "bundle", "--label", "followup", "--view", "summary"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        printed_payload = mocked_stdout_print.call_args.args[0]
        parsed = json.loads(printed_payload)
        self.assertEqual(parsed["mode"], "validate")
        self.assertEqual(parsed["kind"], "bundle")
        self.assertEqual(parsed["selected_label"], "followup")
        self.assertEqual(parsed["task_report_bundle_samples"], ["buy-pingan-complete-review", "confirm-complete-review"])
        self.assertEqual(parsed["non_execution"], True)

    def test_main_api_snapshot_prints_provider_result_envelope(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"rows": [{"symbol": "688260.SH"}]})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli._handle_api_subcommand", return_value=expected),
            patch("builtins.print") as mocked_stdout_print,
            patch("sys.argv", ["tdxquant", "api", "snapshot", "--code", "688260.SH"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        parsed = json.loads(mocked_stdout_print.call_args.args[0])
        self.assertTrue(parsed["success"])
        self.assertTrue(parsed["ok"])
        self.assertEqual(parsed["code"], ErrorCode.OK.value)
        self.assertEqual(parsed["capability"], "api.snapshot")
        self.assertIn("capability_version", parsed)
        self.assertIn("schema_version", parsed)
        self.assertEqual(parsed["runtime"]["provider"], "tdxquant")
        self.assertEqual(parsed["runtime"]["mode"], "cli")
        self.assertEqual(parsed["data"]["rows"], [{"symbol": "688260.SH"}])
        self.assertEqual(parsed["artifacts"], [])

    def test_main_api_snapshot_failure_prints_provider_result_envelope_and_nonzero_exit(self) -> None:
        expected = Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="bad request",
            data={},
            warnings=["warn"],
            next_action="fix-input",
        )
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli._handle_api_subcommand", return_value=expected),
            patch("builtins.print") as mocked_stdout_print,
            patch("sys.argv", ["tdxquant", "api", "snapshot", "--code", "688260.SH"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 1)
        parsed = json.loads(mocked_stdout_print.call_args.args[0])
        self.assertFalse(parsed["success"])
        self.assertFalse(parsed["ok"])
        self.assertEqual(parsed["code"], ErrorCode.INVALID_REQUEST.value)
        self.assertEqual(parsed["message"], "bad request")
        self.assertEqual(parsed["warnings"], ["warn"])
        self.assertEqual(parsed["data"]["next_action"], "fix-input")
        self.assertEqual(parsed["capability"], "api.snapshot")

    def test_main_api_snapshot_replay_output_file_matches_stdout_json(self) -> None:
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "snapshot.json"
            stdout_buffer = io.StringIO()
            with (
                patch("tdxquant.cli.PingAnBrokerAdapter"),
                patch(
                    "sys.argv",
                    [
                        "tdxquant",
                        "api",
                        "snapshot",
                        "--code",
                        "000001.SZ",
                        "--provider-mode",
                        "replay",
                        "--output",
                        str(output_path),
                    ],
                ),
                patch("sys.stdout", stdout_buffer),
            ):
                exit_code = main()
            stdout_payload = json.loads(stdout_buffer.getvalue())
            file_payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout_payload, file_payload)
        self.assertEqual(stdout_payload["data"]["replay_source"]["mode"], "replay")

    def test_main_tdx_data_stock_info_prints_provider_result_envelope(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"rows": [{"symbol": "688260.SH"}]})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_data_stock_info", return_value=expected),
            patch("builtins.print") as mocked_stdout_print,
            patch("sys.argv", ["tdxquant", "tdx-data-stock-info", "--code", "688260.SH"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        parsed = json.loads(mocked_stdout_print.call_args.args[0])
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["capability"], "bridge.stock-info")
        self.assertEqual(parsed["runtime"]["mode"], "cli")
        self.assertEqual(parsed["data"]["rows"], [{"symbol": "688260.SH"}])

    def test_main_api_capabilities_prints_provider_result_envelope(self) -> None:
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
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli._handle_api_subcommand", return_value=expected),
            patch("builtins.print") as mocked_stdout_print,
            patch("sys.argv", ["tdxquant", "api", "capabilities"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        parsed = json.loads(mocked_stdout_print.call_args.args[0])
        self.assertTrue(parsed["success"])
        self.assertTrue(parsed["ok"])
        self.assertEqual(parsed["capability"], "api.capabilities")
        self.assertEqual(parsed["runtime"]["mode"], "cli")
        self.assertEqual(parsed["data"]["summary"]["total"], 0)
        self.assertIn("grading", parsed["data"])

    def test_main_tdx_health_prints_provider_result_envelope_and_keeps_structured_success(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "overall_status": "unavailable",
                "checks": {},
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
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_provider_health", return_value=expected),
            patch("builtins.print") as mocked_stdout_print,
            patch("sys.argv", ["tdxquant", "tdx-health", "--window-key", "平安证券"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        parsed = json.loads(mocked_stdout_print.call_args.args[0])
        self.assertTrue(parsed["success"])
        self.assertTrue(parsed["ok"])
        self.assertEqual(parsed["capability"], "bridge.health")
        self.assertEqual(parsed["data"]["overall_status"], "unavailable")
        self.assertIn("recommended_action_items", parsed["data"])

    def test_main_api_formula_screen_prints_provider_result_envelope(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"matched_symbols": ["600519.SH"], "rows": []})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli._handle_api_subcommand", return_value=expected),
            patch("builtins.print") as mocked_stdout_print,
            patch("sys.argv", ["tdxquant", "api", "formula-screen", "--formula-name", "UPN", "--code", "600519.SH"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        parsed = json.loads(mocked_stdout_print.call_args.args[0])
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["capability"], "formula.screen")
        self.assertEqual(parsed["data"]["matched_symbols"], ["600519.SH"])

    def test_main_tdx_formula_screen_prints_provider_result_envelope(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok", data={"matched_symbols": ["600519.SH"], "rows": []})
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli.run_tdx_formula_screen", return_value=expected),
            patch("builtins.print") as mocked_stdout_print,
            patch("sys.argv", ["tdxquant", "tdx-formula-screen", "--formula-name", "UPN", "--code", "600519.SH"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        parsed = json.loads(mocked_stdout_print.call_args.args[0])
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["capability"], "formula.screen")
        self.assertEqual(parsed["data"]["matched_symbols"], ["600519.SH"])

    def test_main_catalog_list_summary_view_prints_summary_payload(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="listed command catalog entries",
            data={
                "summary_view": {
                    "mode": "list",
                    "kind": "entry",
                    "entries": [{"name": "daily-review", "source": "report"}],
                }
            },
        )
        with (
            patch("tdxquant.cli.PingAnBrokerAdapter"),
            patch("tdxquant.cli._handle_catalog_subcommand", return_value=expected),
            patch("builtins.print") as mocked_stdout_print,
            patch("sys.argv", ["tdxquant", "catalog", "list", "--view", "summary"]),
        ):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        printed_payload = mocked_stdout_print.call_args.args[0]
        parsed = json.loads(printed_payload)
        self.assertEqual(parsed["mode"], "list")
        self.assertEqual(parsed["entries"][0]["name"], "daily-review")


if __name__ == "__main__":
    unittest.main()
