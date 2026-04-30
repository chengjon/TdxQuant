from __future__ import annotations

from .gateway import SecuritiesTraderGateway


class TraderGatewayRegistry:
    def __init__(self) -> None:
        self._gateways: dict[str, SecuritiesTraderGateway] = {}

    def register(self, broker: str, gateway: SecuritiesTraderGateway) -> None:
        self._gateways[str(broker).strip().lower()] = gateway

    def resolve(self, broker: str) -> SecuritiesTraderGateway:
        key = str(broker).strip().lower()
        try:
            return self._gateways[key]
        except KeyError as exc:
            raise KeyError(f"unsupported securities trader broker: {broker}") from exc
