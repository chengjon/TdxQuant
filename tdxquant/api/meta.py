from __future__ import annotations

from .bridge import (
    run_tdx_data_sector_list,
    run_tdx_data_sector_stocks,
    run_tdx_divid_factors,
    run_tdx_gb_info,
    run_tdx_gb_info_by_date,
    run_tdx_get_relation,
    run_tdx_gp_one_data,
    run_tdx_ipo_info,
    run_tdx_stock_list,
)
from ..models import Result


class MetaApi:
    __slots__ = ("strategy_path",)

    def __init__(self, strategy_path: str | None = None) -> None:
        self.strategy_path = strategy_path

    def stock_list(self, market: str | None, list_type: int) -> Result:
        return run_tdx_stock_list(market=market, list_type=list_type, strategy_path=self.strategy_path)

    def sector_list(self, list_type: int) -> Result:
        return run_tdx_data_sector_list(list_type=list_type, strategy_path=self.strategy_path)

    def sector_stocks(self, block_code: str, block_type: int, list_type: int) -> Result:
        return run_tdx_data_sector_stocks(
            block_code=block_code,
            block_type=block_type,
            list_type=list_type,
            strategy_path=self.strategy_path,
        )

    def divid_factors(self, stock_code: str, start_time: str, end_time: str) -> Result:
        return run_tdx_divid_factors(
            stock_code=stock_code,
            start_time=start_time,
            end_time=end_time,
            strategy_path=self.strategy_path,
        )

    def ipo_info(self, ipo_type: int, ipo_date: int) -> Result:
        return run_tdx_ipo_info(
            ipo_type=ipo_type,
            ipo_date=ipo_date,
            strategy_path=self.strategy_path,
        )

    def gb_info(self, stock_code: str, date_list: list[str], count: int) -> Result:
        return run_tdx_gb_info(
            stock_code=stock_code,
            date_list=date_list,
            count=count,
            strategy_path=self.strategy_path,
        )

    def gp_one_data(self, stock_list: list[str], field_list: list[str]) -> Result:
        return run_tdx_gp_one_data(
            stock_list=stock_list,
            field_list=field_list,
            strategy_path=self.strategy_path,
        )

    def get_relation(self, stock_code: str, relation_type: int) -> Result:
        return run_tdx_get_relation(
            stock_code=stock_code,
            relation_type=relation_type,
            strategy_path=self.strategy_path,
        )

    def gb_info_by_date(self, stock_code: str, date: str) -> Result:
        return run_tdx_gb_info_by_date(
            stock_code=stock_code,
            date=date,
            strategy_path=self.strategy_path,
        )
