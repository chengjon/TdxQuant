"""Broker-neutral securities trader foundation."""

from .enums import OrderSide, OrderStatus
from .gateway import SecuritiesTraderGateway
from .models import (
    GatewayCapabilities,
    OrderPlacementResult,
    SecurityOrderRequest,
    SecurityOrderSnapshot,
    TradeFill,
)
from .registry import TraderGatewayRegistry
from .service import TradeService
from .store import TraderStore

__all__ = [
    "GatewayCapabilities",
    "OrderPlacementResult",
    "OrderSide",
    "OrderStatus",
    "SecurityOrderRequest",
    "SecurityOrderSnapshot",
    "SecuritiesTraderGateway",
    "TradeFill",
    "TradeService",
    "TraderGatewayRegistry",
    "TraderStore",
]
