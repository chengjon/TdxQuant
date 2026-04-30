from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from .models import OrderPlacementResult, SecurityOrderRequest, SecurityOrderSnapshot, TradeFill
from .registry import TraderGatewayRegistry
from .store import TraderStore


class TradeService:
    def __init__(self, *, registry: TraderGatewayRegistry, store: TraderStore) -> None:
        self.registry = registry
        self.store = store

    def connect(self, broker: str) -> None:
        self.registry.resolve(broker).connect()

    def heartbeat(self, broker: str) -> bool:
        return bool(self.registry.resolve(broker).heartbeat())

    def place_order(self, request: SecurityOrderRequest) -> SecurityOrderSnapshot:
        issues = request.validate()
        if issues:
            raise ValueError("; ".join(issues))
        result = self.registry.resolve(request.broker).place_order(request)
        self._persist_order_result(result, request)
        return result.snapshot

    def query_order(self, gateway_order_id: str) -> SecurityOrderSnapshot | None:
        return self.store.get_order_snapshot(gateway_order_id)

    def query_trades(self) -> list[TradeFill]:
        return self.store.list_trade_fills()

    def sync_today_trades(self, broker: str) -> list[TradeFill]:
        fills = self.registry.resolve(broker).sync_today_trades()
        for fill in fills:
            self.store.append_trade_fill(fill)
        return fills

    def _persist_order_result(self, result: OrderPlacementResult, request: SecurityOrderRequest) -> None:
        recorded_at = datetime.now(UTC).isoformat()
        self.store.append_order_event(
            {
                "event_id": uuid4().hex,
                "event": "place_order",
                "recorded_at": recorded_at,
                "broker": request.broker,
                "client_order_id": request.client_order_id,
                "gateway_order_id": result.snapshot.gateway_order_id,
                "status": result.snapshot.to_dict()["status"],
                "adapter_events": list(result.adapter_events),
            }
        )
        self.store.write_order_snapshot(result.snapshot)
        for fill in result.trade_fills:
            self.store.append_trade_fill(fill)
