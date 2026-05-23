from __future__ import annotations

import unittest
from decimal import Decimal

from tdxquant.models import ErrorCode, Result
from tdxquant.trader.adapters.pingan_desktop import PingAnDesktopTraderGateway
from tdxquant.trader.models import OrderSide, OrderStatus, SecurityOrderRequest


class _FakePingAnProxy:
    def __init__(self) -> None:
        self.health_calls: list[dict[str, object]] = []
        self.buy_calls: list[dict[str, object]] = []
        self.sell_calls: list[dict[str, object]] = []
        self.buy_submit_once_calls: list[dict[str, object]] = []
        self.sell_submit_once_calls: list[dict[str, object]] = []
        self.health_result = Result(ok=True, code=ErrorCode.OK, message="health ok", data={})
        self.buy_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="buy ok",
            data={
                "result_dialog": {"contract_no": "B202604300001"},
                "trade_audit": {"status": "confirmed"},
            },
        )
        self.sell_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="sell ok",
            data={
                "result_dialog": {"contract_no": "S202604300001"},
                "trade_audit": {"status": "confirmed"},
            },
        )
        self.buy_submit_once_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="submit once ok",
            data={
                "result_dialog": {"contract_no": "B202604300002"},
                "trade_audit": {"status": "confirmed"},
            },
        )
        self.sell_submit_once_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="sell submit once ok",
            data={
                "result_dialog": {"contract_no": "S202604300002"},
                "trade_audit": {"status": "confirmed"},
            },
        )

    def health(self, **kwargs: object) -> Result:
        self.health_calls.append(dict(kwargs))
        return self.health_result

    def buy(self, **kwargs: object) -> Result:
        self.buy_calls.append(dict(kwargs))
        return self.buy_result

    def sell(self, **kwargs: object) -> Result:
        self.sell_calls.append(dict(kwargs))
        return self.sell_result

    def buy_submit_once(self, **kwargs: object) -> Result:
        self.buy_submit_once_calls.append(dict(kwargs))
        return self.buy_submit_once_result

    def sell_submit_once(self, **kwargs: object) -> Result:
        self.sell_submit_once_calls.append(dict(kwargs))
        return self.sell_submit_once_result


class _FakeTradeManager:
    def __init__(self) -> None:
        self.pingan = _FakePingAnProxy()


class PingAnDesktopTraderGatewayTests(unittest.TestCase):
    def test_connect_and_heartbeat_delegate_to_trade_manager_health(self) -> None:
        manager = _FakeTradeManager()
        gateway = PingAnDesktopTraderGateway(manager=manager, port="COM3", baudrate=115200, timeout=2.0)

        gateway.connect()

        self.assertTrue(gateway.heartbeat())
        self.assertEqual(len(manager.pingan.health_calls), 2)
        self.assertEqual(manager.pingan.health_calls[0]["port"], "COM3")
        self.assertEqual(manager.pingan.health_calls[0]["baudrate"], 115200)

    def test_place_order_maps_successful_buy_to_submitted_snapshot(self) -> None:
        manager = _FakeTradeManager()
        gateway = PingAnDesktopTraderGateway(manager=manager, port="COM3")
        request = SecurityOrderRequest(
            broker="pingan_desktop",
            client_order_id="client-001",
            symbol="000001",
            market="SZ",
            side=OrderSide.BUY,
            quantity=100,
            limit_price=Decimal("10.50"),
        )

        placement = gateway.place_order(request)

        self.assertEqual(placement.snapshot.gateway_order_id, "B202604300001")
        self.assertEqual(placement.snapshot.broker_order_id, "B202604300001")
        self.assertEqual(placement.snapshot.status, OrderStatus.SUBMITTED)
        self.assertEqual(placement.snapshot.side, OrderSide.BUY)
        self.assertEqual(placement.snapshot.limit_price, Decimal("10.50"))
        self.assertEqual(manager.pingan.buy_calls[0]["port"], "COM3")
        self.assertEqual(manager.pingan.buy_calls[0]["code"], "000001")
        self.assertEqual(manager.pingan.buy_calls[0]["price"], "10.50")
        self.assertEqual(manager.pingan.buy_calls[0]["quantity"], 100)
        self.assertEqual(placement.adapter_events[0]["step"], "pingan_buy")

    def test_place_order_maps_successful_sell_to_submitted_snapshot(self) -> None:
        manager = _FakeTradeManager()
        gateway = PingAnDesktopTraderGateway(manager=manager, port="COM3")
        request = SecurityOrderRequest(
            broker="pingan_desktop",
            client_order_id="client-002",
            symbol="000001",
            market="SZ",
            side=OrderSide.SELL,
            quantity=100,
            limit_price=Decimal("10.50"),
        )

        placement = gateway.place_order(request)

        self.assertEqual(placement.snapshot.gateway_order_id, "S202604300001")
        self.assertEqual(placement.snapshot.broker_order_id, "S202604300001")
        self.assertEqual(placement.snapshot.status, OrderStatus.SUBMITTED)
        self.assertEqual(placement.snapshot.side, OrderSide.SELL)
        self.assertEqual(manager.pingan.sell_calls[0]["port"], "COM3")
        self.assertEqual(manager.pingan.sell_calls[0]["code"], "000001")
        self.assertEqual(manager.pingan.sell_calls[0]["price"], "10.50")
        self.assertEqual(manager.pingan.sell_calls[0]["quantity"], 100)
        self.assertEqual(placement.adapter_events[0]["step"], "pingan_sell")

    def test_place_order_uses_submit_once_execution_mode_when_requested(self) -> None:
        manager = _FakeTradeManager()
        gateway = PingAnDesktopTraderGateway(manager=manager, port="COM3", execution_mode="submit_once")
        request = SecurityOrderRequest(
            broker="pingan_desktop",
            client_order_id="client-003",
            symbol="000001",
            market="SZ",
            side=OrderSide.BUY,
            quantity=100,
            limit_price=Decimal("10.50"),
            submission_key="submit-001",
        )

        placement = gateway.place_order(request)

        self.assertEqual(placement.snapshot.gateway_order_id, "B202604300002")
        self.assertEqual(manager.pingan.buy_submit_once_calls[0]["submission_key"], "submit-001")
        self.assertEqual(placement.adapter_events[0]["step"], "pingan_buy_submit_once")

    def test_place_order_routes_submit_once_sell_to_sell_submit_once_identity(self) -> None:
        manager = _FakeTradeManager()
        gateway = PingAnDesktopTraderGateway(manager=manager, port="COM3", execution_mode="submit_once")
        request = SecurityOrderRequest(
            broker="pingan_desktop",
            client_order_id="client-004",
            symbol="000001",
            market="SZ",
            side=OrderSide.SELL,
            quantity=100,
            limit_price=Decimal("10.50"),
            submission_key="submit-sell-001",
        )

        placement = gateway.place_order(request)

        self.assertEqual(placement.snapshot.gateway_order_id, "S202604300002")
        self.assertEqual(placement.snapshot.broker_order_id, "S202604300002")
        self.assertEqual(placement.snapshot.status, OrderStatus.SUBMITTED)
        self.assertEqual(placement.snapshot.side, OrderSide.SELL)
        self.assertEqual(len(manager.pingan.buy_submit_once_calls), 0)
        self.assertEqual(len(manager.pingan.sell_calls), 0)
        self.assertEqual(manager.pingan.sell_submit_once_calls[0]["submission_key"], "submit-sell-001")
        self.assertEqual(placement.adapter_events[0]["step"], "pingan_sell_submit_once")
