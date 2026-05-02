from __future__ import annotations

import unittest
from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import patch

from tdxquant.cli import _handle_trade_subcommand, build_parser
from tdxquant.models import ErrorCode
from tdxquant.trader.models import OrderSide, OrderStatus, SecurityOrderSnapshot, TradeFill


def _ts(value: str = "2026-04-30T10:00:00+00:00") -> datetime:
    return datetime.fromisoformat(value).astimezone(UTC)


class _FakeTradeService:
    def __init__(self) -> None:
        self.last_request = None
        self.last_query = None
        self.snapshot = SecurityOrderSnapshot(
            gateway_order_id="gw-001",
            client_order_id="client-001",
            broker_order_id="broker-001",
            broker="pingan_desktop",
            symbol="000001",
            market="SZ",
            side=OrderSide.BUY,
            status=OrderStatus.SUBMITTED,
            requested_quantity=100,
            filled_quantity=0,
            remaining_quantity=100,
            limit_price=Decimal("10.50"),
            avg_fill_price=Decimal("0"),
            reject_reason="",
            placed_at=_ts(),
            updated_at=_ts(),
            source="live",
        )
        self.fills = [
            TradeFill(
                trade_id="fill-001",
                gateway_order_id="gw-001",
                broker_order_id="broker-001",
                client_order_id="client-001",
                broker="pingan_desktop",
                symbol="000001",
                market="SZ",
                side=OrderSide.BUY,
                quantity=100,
                price=Decimal("10.50"),
                traded_at=_ts("2026-04-30T10:01:00+00:00"),
                source="sync",
            )
        ]

    def place_order(self, request):
        self.last_request = request
        return self.snapshot

    def query_order(self, gateway_order_id: str):
        self.last_query = gateway_order_id
        return self.snapshot if gateway_order_id == "gw-001" else None

    def query_trades(self):
        return list(self.fills)


class TraderCliParserTests(unittest.TestCase):
    def test_trade_order_place_parser_accepts_broker_neutral_arguments(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "order-place",
                "--broker",
                "pingan_desktop",
                "--port",
                "COM3",
                "--market",
                "SZ",
                "--side",
                "buy",
                "--code",
                "000001",
                "--price",
                "10.50",
                "--quantity",
                "100",
            ]
        )
        self.assertEqual(args.trade_command, "order-place")
        self.assertEqual(args.broker, "pingan_desktop")
        self.assertEqual(args.side, "buy")


class TraderCliDispatchTests(unittest.TestCase):
    def test_handle_trade_order_place_dispatches_to_trade_service(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "order-place",
                "--broker",
                "pingan_desktop",
                "--port",
                "COM3",
                "--market",
                "SZ",
                "--side",
                "buy",
                "--code",
                "000001",
                "--price",
                "10.50",
                "--quantity",
                "100",
                "--client-order-id",
                "client-001",
            ]
        )
        service = _FakeTradeService()
        with patch("tdxquant.cli._build_trader_service", return_value=service):
            result = _handle_trade_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(service.last_request.client_order_id, "client-001")
        self.assertEqual(service.last_request.side, OrderSide.BUY)
        self.assertEqual(result.data["order"]["gateway_order_id"], "gw-001")

    def test_handle_trade_order_place_returns_failed_result_when_snapshot_failed(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "trade",
                "order-place",
                "--broker",
                "pingan_desktop",
                "--port",
                "COM3",
                "--market",
                "SZ",
                "--side",
                "buy",
                "--code",
                "000001",
                "--price",
                "10.50",
                "--quantity",
                "100",
                "--client-order-id",
                "client-001",
            ]
        )
        service = _FakeTradeService()
        service.snapshot = replace(
            service.snapshot,
            status=OrderStatus.FAILED,
            reject_reason="desktop execution failed",
        )
        with patch("tdxquant.cli._build_trader_service", return_value=service):
            result = _handle_trade_subcommand(args)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.EXECUTION_FAILED)
        self.assertIn("desktop execution failed", result.message)

    def test_handle_trade_order_query_dispatches_to_trade_service(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["trade", "order-query", "--gateway-order-id", "gw-001"])
        service = _FakeTradeService()
        with patch("tdxquant.cli._build_trader_service", return_value=service):
            result = _handle_trade_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(service.last_query, "gw-001")
        self.assertEqual(result.data["order"]["gateway_order_id"], "gw-001")

    def test_handle_trade_trade_query_dispatches_to_trade_service(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["trade", "trade-query"])
        service = _FakeTradeService()
        with patch("tdxquant.cli._build_trader_service", return_value=service):
            result = _handle_trade_subcommand(args)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["trades"][0]["trade_id"], "fill-001")
