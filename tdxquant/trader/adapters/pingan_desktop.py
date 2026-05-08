from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal

from ...models import ErrorCode, Result
from ...trade import TdxTradeManager
from ..enums import OrderSide, OrderStatus
from ..models import GatewayCapabilities, OrderPlacementResult, SecurityOrderRequest, SecurityOrderSnapshot, TradeFill


@dataclass(slots=True)
class PingAnDesktopTraderGateway:
    execution_mode: str = "buy"
    port: str | None = None
    baudrate: int = 115200
    timeout: float = 2.0
    max_depth: int = 12
    close_result_dialog: bool = True
    profile: str = "balanced"
    title_keyword: str = "平安证券"
    exe_path: str | None = None
    max_price: float | None = None
    manager: TdxTradeManager | None = None
    capabilities: GatewayCapabilities = field(init=False)

    def __post_init__(self) -> None:
        self.capabilities = GatewayCapabilities(
            supports_cancel=False,
            supports_account_query=False,
            supports_position_query=False,
            supports_push_events=False,
            supports_order_sync=False,
            supports_trade_sync=False,
        )
        if self.manager is None:
            self.manager = TdxTradeManager(profile=self.profile, title_keyword=self.title_keyword, exe_path=self.exe_path)

    def connect(self) -> None:
        result = self._require_manager().pingan.health(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
        if not result.ok:
            raise RuntimeError(result.message)

    def heartbeat(self) -> bool:
        result = self._require_manager().pingan.health(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
        return bool(result.ok)

    def place_order(self, request: SecurityOrderRequest) -> OrderPlacementResult:
        side = request.side if isinstance(request.side, OrderSide) else OrderSide(str(request.side).lower())
        if not self.port:
            raise ValueError("PingAnDesktopTraderGateway requires a serial port")
        if side == OrderSide.SELL:
            result = self._require_manager().pingan.sell(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                code=request.symbol,
                price=str(request.limit_price),
                quantity=request.quantity,
                max_depth=self.max_depth,
                close_result_dialog=self.close_result_dialog,
                submission_key=request.submission_key,
                max_price=self.max_price,
            )
            adapter_step = "pingan_sell_submit_once" if self.execution_mode == "submit_once" else "pingan_sell"
        elif self.execution_mode == "submit_once":
            result = self._require_manager().pingan.buy_submit_once(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                code=request.symbol,
                price=str(request.limit_price),
                quantity=request.quantity,
                max_depth=self.max_depth,
                close_result_dialog=self.close_result_dialog,
                submission_key=request.submission_key,
                max_price=self.max_price,
            )
            adapter_step = "pingan_buy_submit_once"
        else:
            result = self._require_manager().pingan.buy(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                code=request.symbol,
                price=str(request.limit_price),
                quantity=request.quantity,
                max_depth=self.max_depth,
                close_result_dialog=self.close_result_dialog,
                submission_key=request.submission_key,
                max_price=self.max_price,
            )
            adapter_step = "pingan_buy"
        snapshot = self._build_snapshot(request=request, result=result)
        return OrderPlacementResult(
            snapshot=snapshot,
            trade_fills=[],
            adapter_events=[
                {
                    "step": adapter_step,
                    "ok": result.ok,
                    "message": result.message,
                    "trade_audit_status": result.data.get("trade_audit", {}).get("status"),
                    "contract_no": result.data.get("result_dialog", {}).get("contract_no"),
                }
            ],
        )

    def query_order(self, gateway_order_id: str) -> SecurityOrderSnapshot | None:
        return None

    def query_trades(self, since: datetime | None = None) -> list[TradeFill]:
        return []

    def sync_today_trades(self) -> list[TradeFill]:
        return []

    def _build_snapshot(self, *, request: SecurityOrderRequest, result: Result) -> SecurityOrderSnapshot:
        contract_no = str(result.data.get("result_dialog", {}).get("contract_no") or "").strip() or None
        now = datetime.now(UTC)
        side = request.side if isinstance(request.side, OrderSide) else OrderSide(str(request.side).lower())
        if result.ok:
            status = OrderStatus.SUBMITTED
        elif result.code == ErrorCode.INVALID_REQUEST or result.data.get("trade_audit", {}).get("status") == "rejected":
            status = OrderStatus.REJECTED
        else:
            status = OrderStatus.FAILED
        return SecurityOrderSnapshot(
            gateway_order_id=contract_no or request.client_order_id,
            client_order_id=request.client_order_id,
            broker_order_id=contract_no,
            broker="pingan_desktop",
            symbol=request.symbol,
            market=request.market,
            side=side,
            status=status,
            requested_quantity=request.quantity,
            filled_quantity=0,
            remaining_quantity=request.quantity,
            limit_price=Decimal(str(request.limit_price)),
            avg_fill_price=Decimal("0"),
            reject_reason="" if result.ok else result.message,
            placed_at=now,
            updated_at=now,
            source="live",
        )

    def _require_manager(self) -> TdxTradeManager:
        if self.manager is None:
            raise RuntimeError("trade manager is unavailable")
        return self.manager
