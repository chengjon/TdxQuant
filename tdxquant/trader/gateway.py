from __future__ import annotations

from datetime import datetime
from typing import Protocol

from .models import GatewayCapabilities, OrderPlacementResult, SecurityOrderRequest, SecurityOrderSnapshot, TradeFill


class SecuritiesTraderGateway(Protocol):
    capabilities: GatewayCapabilities

    def connect(self) -> None:
        raise NotImplementedError

    def heartbeat(self) -> bool:
        raise NotImplementedError

    def place_order(self, request: SecurityOrderRequest) -> OrderPlacementResult:
        raise NotImplementedError

    def query_order(self, gateway_order_id: str) -> SecurityOrderSnapshot | None:
        raise NotImplementedError

    def query_trades(self, since: datetime | None = None) -> list[TradeFill]:
        raise NotImplementedError

    def sync_today_trades(self) -> list[TradeFill]:
        raise NotImplementedError
