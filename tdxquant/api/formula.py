from __future__ import annotations

from typing import Any

from ..models import Result
from .bridge import (
    run_tdx_formula_exp,
    run_tdx_formula_format_data,
    run_tdx_formula_get_all,
    run_tdx_formula_get_data,
    run_tdx_formula_get_info,
    run_tdx_formula_process_mul_xg,
    run_tdx_formula_process_mul_zb,
    run_tdx_formula_screen,
    run_tdx_formula_set_data,
    run_tdx_formula_set_data_info,
    run_tdx_formula_xg,
    run_tdx_formula_zb,
)


class FormulaApi:
    __slots__ = ("strategy_path",)

    def __init__(self, strategy_path: str | None = None) -> None:
        self.strategy_path = strategy_path

    def format_data(self, kline_payload: dict[str, Any]) -> Result:
        return run_tdx_formula_format_data(kline_payload=kline_payload, strategy_path=self.strategy_path)

    def set_data(
        self,
        stock_code: str,
        stock_period: str,
        stock_data: list[Any],
        count: int,
        dividend_type: int,
    ) -> Result:
        return run_tdx_formula_set_data(
            stock_code=stock_code,
            stock_period=stock_period,
            stock_data=stock_data,
            count=count,
            dividend_type=dividend_type,
            strategy_path=self.strategy_path,
        )

    def set_data_info(
        self,
        stock_code: str,
        stock_period: str,
        start_time: str,
        end_time: str,
        count: int,
        dividend_type: int,
    ) -> Result:
        return run_tdx_formula_set_data_info(
            stock_code=stock_code,
            stock_period=stock_period,
            start_time=start_time,
            end_time=end_time,
            count=count,
            dividend_type=dividend_type,
            strategy_path=self.strategy_path,
        )

    def get_data(self) -> Result:
        return run_tdx_formula_get_data(strategy_path=self.strategy_path)

    def zb(self, formula_name: str, formula_arg: str, xsflag: int) -> Result:
        return run_tdx_formula_zb(
            formula_name=formula_name,
            formula_arg=formula_arg,
            xsflag=xsflag,
            strategy_path=self.strategy_path,
        )

    def xg(self, formula_name: str, formula_arg: str) -> Result:
        return run_tdx_formula_xg(
            formula_name=formula_name,
            formula_arg=formula_arg,
            strategy_path=self.strategy_path,
        )

    def exp(self, formula_name: str, formula_arg: str) -> Result:
        return run_tdx_formula_exp(
            formula_name=formula_name,
            formula_arg=formula_arg,
            strategy_path=self.strategy_path,
        )

    def process_mul_xg(
        self,
        formula_name: str,
        formula_arg: str,
        return_count: int,
        return_date: bool,
        stock_list: list[str],
        stock_period: str,
        start_time: str,
        end_time: str,
        count: int,
        dividend_type: int,
    ) -> Result:
        return run_tdx_formula_process_mul_xg(
            formula_name=formula_name,
            formula_arg=formula_arg,
            return_count=return_count,
            return_date=return_date,
            stock_list=stock_list,
            stock_period=stock_period,
            start_time=start_time,
            end_time=end_time,
            count=count,
            dividend_type=dividend_type,
            strategy_path=self.strategy_path,
        )

    def screen(
        self,
        formula_name: str,
        stock_list: list[str],
        *,
        formula_arg: str = "",
        return_count: int = 1,
        return_date: bool = False,
        stock_period: str = "1d",
        start_time: str = "",
        end_time: str = "",
        count: int = 0,
        dividend_type: int = 0,
    ) -> Result:
        return run_tdx_formula_screen(
            formula_name=formula_name,
            stock_list=stock_list,
            formula_arg=formula_arg,
            return_count=return_count,
            return_date=return_date,
            stock_period=stock_period,
            start_time=start_time,
            end_time=end_time,
            count=count,
            dividend_type=dividend_type,
            strategy_path=self.strategy_path,
        )

    def process_mul_zb(
        self,
        formula_name: str,
        formula_arg: str,
        xsflag: int,
        return_count: int,
        return_date: bool,
        stock_list: list[str],
        stock_period: str,
        start_time: str,
        end_time: str,
        count: int,
        dividend_type: int,
    ) -> Result:
        return run_tdx_formula_process_mul_zb(
            formula_name=formula_name,
            formula_arg=formula_arg,
            xsflag=xsflag,
            return_count=return_count,
            return_date=return_date,
            stock_list=stock_list,
            stock_period=stock_period,
            start_time=start_time,
            end_time=end_time,
            count=count,
            dividend_type=dividend_type,
            strategy_path=self.strategy_path,
        )

    def get_all(self) -> Result:
        return run_tdx_formula_get_all(strategy_path=self.strategy_path)

    def get_info(self, formula_name: str) -> Result:
        return run_tdx_formula_get_info(formula_name=formula_name, strategy_path=self.strategy_path)
