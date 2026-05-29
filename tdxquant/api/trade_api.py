from __future__ import annotations

from ..models import Result
from .bridge import (
    run_tdx_cancel_order_stock,
    run_tdx_order_stock,
    run_tdx_query_stock_asset,
    run_tdx_query_stock_orders,
    run_tdx_query_stock_positions,
    run_tdx_stock_account,
)


class TradeApi:
    __slots__ = ("strategy_path",)

    def __init__(self, strategy_path: str | None = None) -> None:
        self.strategy_path = strategy_path

    def stock_account(self, account: str = "", account_type: str = "stock") -> Result:
        return run_tdx_stock_account(
            account=account,
            account_type=account_type,
            strategy_path=self.strategy_path,
        )

    def order_stock(
        self,
        account_id: int,
        stock_code: str,
        order_type: int,
        order_volume: int,
        price_type: int,
        price: float,
    ) -> Result:
        return run_tdx_order_stock(
            account_id=account_id,
            stock_code=stock_code,
            order_type=order_type,
            order_volume=order_volume,
            price_type=price_type,
            price=price,
            strategy_path=self.strategy_path,
        )

    def query_stock_orders(self, account_id: int, stock_code: str = "") -> Result:
        return run_tdx_query_stock_orders(
            account_id=account_id,
            stock_code=stock_code,
            strategy_path=self.strategy_path,
        )

    def query_stock_positions(self, account_id: int) -> Result:
        return run_tdx_query_stock_positions(
            account_id=account_id,
            strategy_path=self.strategy_path,
        )

    def cancel_order_stock(self, account_id: int, stock_code: str, order_id: str) -> Result:
        return run_tdx_cancel_order_stock(
            account_id=account_id,
            stock_code=stock_code,
            order_id=order_id,
            strategy_path=self.strategy_path,
        )

    def query_stock_asset(self, account_id: int) -> Result:
        return run_tdx_query_stock_asset(
            account_id=account_id,
            strategy_path=self.strategy_path,
        )
