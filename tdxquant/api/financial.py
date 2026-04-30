from __future__ import annotations

from ..models import Result
from .bridge import run_tdx_financial_data, run_tdx_financial_data_by_date


class FinancialApi:
    __slots__ = ("strategy_path",)

    def __init__(self, strategy_path: str | None = None) -> None:
        self.strategy_path = strategy_path

    def financial_data(
        self,
        stock_list: list[str],
        field_list: list[str],
        start_time: str,
        end_time: str,
        report_type: str,
    ) -> Result:
        return run_tdx_financial_data(
            stock_list=stock_list,
            field_list=field_list,
            start_time=start_time,
            end_time=end_time,
            report_type=report_type,
            strategy_path=self.strategy_path,
        )

    def financial_data_by_date(
        self,
        stock_list: list[str],
        field_list: list[str],
        year: int,
        mmdd: int,
    ) -> Result:
        return run_tdx_financial_data_by_date(
            stock_list=stock_list,
            field_list=field_list,
            year=year,
            mmdd=mmdd,
            strategy_path=self.strategy_path,
        )
