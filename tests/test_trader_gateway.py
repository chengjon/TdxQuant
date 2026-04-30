from __future__ import annotations

import json
import unittest
from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory

from tdxquant.trader.models import (
    GatewayCapabilities,
    OrderPlacementResult,
    OrderSide,
    OrderStatus,
    SecurityOrderRequest,
    SecurityOrderSnapshot,
    TradeFill,
)
from tdxquant.trader.registry import TraderGatewayRegistry
from tdxquant.trader.service import TradeService
from tdxquant.trader.store import TraderStore


def _ts(value: str = "2026-04-30T10:00:00+00:00") -> datetime:
    return datetime.fromisoformat(value).astimezone(UTC)


class _FakeGateway:
    def __init__(self) -> None:
        self.connected = False
        self.last_request: SecurityOrderRequest | None = None
        self.capabilities = GatewayCapabilities(
            supports_cancel=False,
            supports_account_query=False,
            supports_position_query=False,
            supports_push_events=False,
            supports_order_sync=False,
            supports_trade_sync=True,
        )
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
        self.trade_fills: list[TradeFill] = [
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

    def connect(self) -> None:
        self.connected = True

    def heartbeat(self) -> bool:
        return self.connected

    def place_order(self, request: SecurityOrderRequest) -> OrderPlacementResult:
        self.last_request = request
        return OrderPlacementResult(
            snapshot=replace(
                self.snapshot,
                client_order_id=request.client_order_id,
                symbol=request.symbol,
                market=request.market,
                side=request.side,
                requested_quantity=request.quantity,
                remaining_quantity=request.quantity,
                limit_price=request.limit_price,
            ),
            trade_fills=[],
            adapter_events=[{"step": "fake_submit", "ok": True}],
        )

    def query_order(self, gateway_order_id: str) -> SecurityOrderSnapshot | None:
        if gateway_order_id == self.snapshot.gateway_order_id:
            return self.snapshot
        return None

    def query_trades(self, since: datetime | None = None) -> list[TradeFill]:
        if since is None:
            return list(self.trade_fills)
        return [fill for fill in self.trade_fills if fill.traded_at >= since]

    def sync_today_trades(self) -> list[TradeFill]:
        return list(self.trade_fills)


class SecurityOrderRequestTests(unittest.TestCase):
    def test_validate_accepts_first_phase_cash_limit_request(self) -> None:
        request = SecurityOrderRequest(
            broker="pingan_desktop",
            client_order_id="client-001",
            symbol="000001",
            market="SZ",
            side=OrderSide.BUY,
            quantity=100,
            limit_price=Decimal("10.50"),
        )
        self.assertEqual(request.validate(), [])

    def test_validate_rejects_out_of_scope_request(self) -> None:
        request = SecurityOrderRequest(
            broker="pingan_desktop",
            client_order_id="client-002",
            symbol="abc",
            market="US",
            side="short",  # type: ignore[arg-type]
            quantity=0,
            limit_price=Decimal("-1"),
            order_type="market",
        )
        issues = request.validate()
        self.assertIn("symbol must be a 6-digit numeric string", issues)
        self.assertIn("market must be one of: SH, SZ", issues)
        self.assertIn("side must be buy or sell", issues)
        self.assertIn("quantity must be a positive multiple of 100", issues)
        self.assertIn("limit_price must be positive", issues)
        self.assertIn("order_type must be limit for the first phase", issues)


class TraderGatewayRegistryTests(unittest.TestCase):
    def test_registry_resolves_registered_gateway(self) -> None:
        registry = TraderGatewayRegistry()
        gateway = _FakeGateway()
        registry.register("pingan_desktop", gateway)
        self.assertIs(registry.resolve("pingan_desktop"), gateway)

    def test_registry_rejects_unknown_broker(self) -> None:
        registry = TraderGatewayRegistry()
        with self.assertRaises(KeyError):
            registry.resolve("missing")


class TraderStoreTests(unittest.TestCase):
    def test_store_persists_snapshot_and_trade_fill_as_strings(self) -> None:
        snapshot = SecurityOrderSnapshot(
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
        fill = TradeFill(
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
        with TemporaryDirectory() as temp_dir:
            store = TraderStore(Path(temp_dir) / "runtime" / "trader")
            snapshot_path = store.write_order_snapshot(snapshot)
            fill_path = store.append_trade_fill(fill)
            snapshot_row = json.loads(snapshot_path.read_text(encoding="utf-8").splitlines()[-1])
            fill_row = json.loads(fill_path.read_text(encoding="utf-8").splitlines()[-1])
            latest_orders = json.loads((Path(temp_dir) / "runtime" / "trader" / "latest-orders.json").read_text(encoding="utf-8"))
            latest_trades = json.loads((Path(temp_dir) / "runtime" / "trader" / "latest-trades.json").read_text(encoding="utf-8"))
        self.assertEqual(snapshot_row["limit_price"], "10.50")
        self.assertEqual(snapshot_row["avg_fill_price"], "0")
        self.assertEqual(fill_row["price"], "10.50")
        self.assertEqual(latest_orders["gw-001"]["limit_price"], "10.50")
        self.assertEqual(latest_trades[0]["trade_id"], "fill-001")


class TradeServiceTests(unittest.TestCase):
    def test_service_connects_places_order_and_persists_snapshot(self) -> None:
        gateway = _FakeGateway()
        registry = TraderGatewayRegistry()
        registry.register("pingan_desktop", gateway)
        request = SecurityOrderRequest(
            broker="pingan_desktop",
            client_order_id="client-001",
            symbol="000001",
            market="SZ",
            side=OrderSide.BUY,
            quantity=100,
            limit_price=Decimal("10.50"),
        )
        with TemporaryDirectory() as temp_dir:
            service = TradeService(registry=registry, store=TraderStore(Path(temp_dir) / "runtime" / "trader"))
            service.connect("pingan_desktop")
            self.assertTrue(service.heartbeat("pingan_desktop"))
            snapshot = service.place_order(request)
            persisted = service.query_order("gw-001")
            events_path = Path(temp_dir) / "runtime" / "trader" / "order-events.jsonl"
            events_exist = events_path.exists()

        self.assertEqual(gateway.last_request, request)
        self.assertEqual(snapshot.gateway_order_id, "gw-001")
        self.assertIsNotNone(persisted)
        self.assertEqual(persisted.limit_price, Decimal("10.50"))
        self.assertTrue(events_exist)

    def test_service_syncs_today_trades_into_store(self) -> None:
        gateway = _FakeGateway()
        registry = TraderGatewayRegistry()
        registry.register("pingan_desktop", gateway)
        with TemporaryDirectory() as temp_dir:
            service = TradeService(registry=registry, store=TraderStore(Path(temp_dir) / "runtime" / "trader"))
            fills = service.sync_today_trades("pingan_desktop")
            queried = service.query_trades()

        self.assertEqual(len(fills), 1)
        self.assertEqual(len(queried), 1)
        self.assertEqual(queried[0].trade_id, "fill-001")

    def test_service_recovers_tracked_orders_and_trades_from_existing_store(self) -> None:
        gateway = _FakeGateway()
        registry = TraderGatewayRegistry()
        registry.register("pingan_desktop", gateway)
        request = SecurityOrderRequest(
            broker="pingan_desktop",
            client_order_id="client-restore-001",
            symbol="000001",
            market="SZ",
            side=OrderSide.BUY,
            quantity=100,
            limit_price=Decimal("10.50"),
        )
        with TemporaryDirectory() as temp_dir:
            store = TraderStore(Path(temp_dir) / "runtime" / "trader")
            service = TradeService(registry=registry, store=store)
            placed = service.place_order(request)
            service.sync_today_trades("pingan_desktop")

            recovered_service = TradeService(registry=registry, store=TraderStore(Path(temp_dir) / "runtime" / "trader"))
            recovered_order = recovered_service.query_order(placed.gateway_order_id)
            recovered_trades = recovered_service.query_trades()

        self.assertIsNotNone(recovered_order)
        self.assertEqual(recovered_order.client_order_id, "client-restore-001")
        self.assertEqual(len(recovered_trades), 1)
        self.assertEqual(recovered_trades[0].trade_id, "fill-001")

    def test_service_rejects_invalid_request_before_gateway_execution(self) -> None:
        gateway = _FakeGateway()
        registry = TraderGatewayRegistry()
        registry.register("pingan_desktop", gateway)
        request = SecurityOrderRequest(
            broker="pingan_desktop",
            client_order_id="client-001",
            symbol="bad",
            market="SZ",
            side=OrderSide.BUY,
            quantity=100,
            limit_price=Decimal("10.50"),
        )
        with TemporaryDirectory() as temp_dir:
            service = TradeService(registry=registry, store=TraderStore(Path(temp_dir) / "runtime" / "trader"))
            with self.assertRaises(ValueError):
                service.place_order(request)

        self.assertIsNone(gateway.last_request)
