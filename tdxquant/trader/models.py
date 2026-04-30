from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any

from .enums import OrderSide, OrderStatus


def _serialize_decimal(value: Decimal) -> str:
    return str(value)


def _serialize_datetime(value: datetime) -> str:
    return value.isoformat()


def _normalize_side(value: OrderSide | str) -> str:
    return value.value if isinstance(value, OrderSide) else str(value).lower().strip()


def _normalize_status(value: OrderStatus | str) -> str:
    return value.value if isinstance(value, OrderStatus) else str(value).lower().strip()


@dataclass(slots=True)
class GatewayCapabilities:
    supports_cancel: bool
    supports_account_query: bool
    supports_position_query: bool
    supports_push_events: bool
    supports_order_sync: bool
    supports_trade_sync: bool

    def to_dict(self) -> dict[str, bool]:
        return {
            "supports_cancel": self.supports_cancel,
            "supports_account_query": self.supports_account_query,
            "supports_position_query": self.supports_position_query,
            "supports_push_events": self.supports_push_events,
            "supports_order_sync": self.supports_order_sync,
            "supports_trade_sync": self.supports_trade_sync,
        }


@dataclass(slots=True)
class SecurityOrderRequest:
    broker: str
    client_order_id: str
    symbol: str
    market: str
    side: OrderSide | str
    quantity: int
    limit_price: Decimal
    order_type: str = "limit"
    time_in_force: str = "day"
    account_id: str | None = None
    submission_key: str | None = None

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not str(self.symbol).isdigit() or len(str(self.symbol)) != 6:
            issues.append("symbol must be a 6-digit numeric string")
        if str(self.market).upper() not in {"SH", "SZ"}:
            issues.append("market must be one of: SH, SZ")
        if _normalize_side(self.side) not in {OrderSide.BUY.value, OrderSide.SELL.value}:
            issues.append("side must be buy or sell")
        if self.quantity <= 0 or self.quantity % 100 != 0:
            issues.append("quantity must be a positive multiple of 100")
        if self.limit_price <= 0:
            issues.append("limit_price must be positive")
        if str(self.order_type).lower() != "limit":
            issues.append("order_type must be limit for the first phase")
        if not str(self.client_order_id).strip():
            issues.append("client_order_id is required")
        if not str(self.broker).strip():
            issues.append("broker is required")
        return issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "broker": self.broker,
            "client_order_id": self.client_order_id,
            "symbol": self.symbol,
            "market": self.market,
            "side": _normalize_side(self.side),
            "quantity": self.quantity,
            "limit_price": _serialize_decimal(self.limit_price),
            "order_type": self.order_type,
            "time_in_force": self.time_in_force,
            "account_id": self.account_id,
            "submission_key": self.submission_key,
        }


@dataclass(slots=True)
class SecurityOrderSnapshot:
    gateway_order_id: str
    client_order_id: str
    broker_order_id: str | None
    broker: str
    symbol: str
    market: str
    side: OrderSide | str
    status: OrderStatus | str
    requested_quantity: int
    filled_quantity: int
    remaining_quantity: int
    limit_price: Decimal
    avg_fill_price: Decimal
    reject_reason: str
    placed_at: datetime
    updated_at: datetime
    source: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "gateway_order_id": self.gateway_order_id,
            "client_order_id": self.client_order_id,
            "broker_order_id": self.broker_order_id,
            "broker": self.broker,
            "symbol": self.symbol,
            "market": self.market,
            "side": _normalize_side(self.side),
            "status": _normalize_status(self.status),
            "requested_quantity": self.requested_quantity,
            "filled_quantity": self.filled_quantity,
            "remaining_quantity": self.remaining_quantity,
            "limit_price": _serialize_decimal(self.limit_price),
            "avg_fill_price": _serialize_decimal(self.avg_fill_price),
            "reject_reason": self.reject_reason,
            "placed_at": _serialize_datetime(self.placed_at),
            "updated_at": _serialize_datetime(self.updated_at),
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SecurityOrderSnapshot":
        return cls(
            gateway_order_id=str(payload["gateway_order_id"]),
            client_order_id=str(payload["client_order_id"]),
            broker_order_id=None if payload.get("broker_order_id") in (None, "") else str(payload["broker_order_id"]),
            broker=str(payload["broker"]),
            symbol=str(payload["symbol"]),
            market=str(payload["market"]),
            side=OrderSide(str(payload["side"])),
            status=OrderStatus(str(payload["status"])),
            requested_quantity=int(payload["requested_quantity"]),
            filled_quantity=int(payload["filled_quantity"]),
            remaining_quantity=int(payload["remaining_quantity"]),
            limit_price=Decimal(str(payload["limit_price"])),
            avg_fill_price=Decimal(str(payload["avg_fill_price"])),
            reject_reason=str(payload.get("reject_reason", "")),
            placed_at=datetime.fromisoformat(str(payload["placed_at"])),
            updated_at=datetime.fromisoformat(str(payload["updated_at"])),
            source=str(payload["source"]),
        )


@dataclass(slots=True)
class TradeFill:
    trade_id: str
    gateway_order_id: str
    broker_order_id: str | None
    client_order_id: str
    broker: str
    symbol: str
    market: str
    side: OrderSide | str
    quantity: int
    price: Decimal
    traded_at: datetime
    source: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "trade_id": self.trade_id,
            "gateway_order_id": self.gateway_order_id,
            "broker_order_id": self.broker_order_id,
            "client_order_id": self.client_order_id,
            "broker": self.broker,
            "symbol": self.symbol,
            "market": self.market,
            "side": _normalize_side(self.side),
            "quantity": self.quantity,
            "price": _serialize_decimal(self.price),
            "traded_at": _serialize_datetime(self.traded_at),
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TradeFill":
        return cls(
            trade_id=str(payload["trade_id"]),
            gateway_order_id=str(payload["gateway_order_id"]),
            broker_order_id=None if payload.get("broker_order_id") in (None, "") else str(payload["broker_order_id"]),
            client_order_id=str(payload["client_order_id"]),
            broker=str(payload["broker"]),
            symbol=str(payload["symbol"]),
            market=str(payload["market"]),
            side=OrderSide(str(payload["side"])),
            quantity=int(payload["quantity"]),
            price=Decimal(str(payload["price"])),
            traded_at=datetime.fromisoformat(str(payload["traded_at"])),
            source=str(payload["source"]),
        )


@dataclass(slots=True)
class OrderPlacementResult:
    snapshot: SecurityOrderSnapshot
    trade_fills: list[TradeFill] = field(default_factory=list)
    adapter_events: list[dict[str, Any]] = field(default_factory=list)
