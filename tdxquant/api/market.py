from __future__ import annotations

from .bridge import (
    run_tdx_cb_info,
    run_tdx_data_kline,
    run_tdx_data_snapshot,
    run_tdx_data_stock_info,
    run_tdx_full_tick,
    run_tdx_get_pricevol,
    run_tdx_get_trackzs_etf_info,
    run_tdx_market_snapshot,
    run_tdx_more_info,
)
from ..models import Result


class MarketApi:
    __slots__ = ("strategy_path",)

    def __init__(self, strategy_path: str | None = None) -> None:
        self.strategy_path = strategy_path

    def snapshot(self, stock_code: str, field_list: list[str]) -> Result:
        return run_tdx_data_snapshot(stock_code=stock_code, field_list=field_list, strategy_path=self.strategy_path)

    def full_tick(self, stock_code: str, field_list: list[str]) -> Result:
        return run_tdx_full_tick(stock_code=stock_code, field_list=field_list, strategy_path=self.strategy_path)

    def market_snapshot(self, stock_code: str, field_list: list[str]) -> Result:
        return run_tdx_market_snapshot(stock_code=stock_code, field_list=field_list, strategy_path=self.strategy_path)

    def kline(
        self,
        stock_list: list[str],
        period: str,
        start_time: str,
        end_time: str,
        count: int,
        dividend_type: str,
        field_list: list[str],
        fill_data: bool,
    ) -> Result:
        return run_tdx_data_kline(
            stock_list=stock_list,
            period=period,
            start_time=start_time,
            end_time=end_time,
            count=count,
            dividend_type=dividend_type,
            field_list=field_list,
            fill_data=fill_data,
            strategy_path=self.strategy_path,
        )

    def stock_info(self, stock_code: str, field_list: list[str]) -> Result:
        return run_tdx_data_stock_info(stock_code=stock_code, field_list=field_list, strategy_path=self.strategy_path)

    def more_info(self, stock_code: str, field_list: list[str]) -> Result:
        return run_tdx_more_info(stock_code=stock_code, field_list=field_list, strategy_path=self.strategy_path)

    def cb_info(self, stock_code: str, field_list: list[str]) -> Result:
        return run_tdx_cb_info(stock_code=stock_code, field_list=field_list, strategy_path=self.strategy_path)

    def get_pricevol(
        self,
        stock_code: str,
        period: str,
        start_time: str = "",
        end_time: str = "",
        count: int = -1,
        dividend_type: str = "none",
    ) -> Result:
        return run_tdx_get_pricevol(
            stock_code=stock_code,
            period=period,
            start_time=start_time,
            end_time=end_time,
            count=count,
            dividend_type=dividend_type,
            strategy_path=self.strategy_path,
        )

    def get_trackzs_etf_info(self, stock_code: str) -> Result:
        return run_tdx_get_trackzs_etf_info(stock_code=stock_code, strategy_path=self.strategy_path)
