from __future__ import annotations

from typing import Any

from ..models import Result
from ..replay_provider import execute_sync_replay, is_replay_mode, normalize_provider_mode
from .block import BlockApi
from .bridge import run_tdx_refresh_cache
from .context import attach_manager_metadata, capture_api_timing, resolve_api_profile
from .financial import FinancialApi
from .formula import FormulaApi
from .market import MarketApi
from .meta import MetaApi
from .runtime import RuntimeApi
from .transaction import TransactionApi


class _MarketManagerProxy:
    __slots__ = ("_manager",)

    def __init__(self, manager: "TdxApiManager") -> None:
        self._manager = manager

    def snapshot(self, stock_code: str, fields: list[str] | None = None) -> Result:
        field_list = self._manager._resolve_fields("snapshot", fields)
        effective_profile = self._manager._build_effective_profile({"field_list": field_list})
        result, timing = capture_api_timing(
            "market.snapshot",
            lambda: self._manager._dispatch_sync_capability(
                "market.snapshot",
                lambda: self._manager._market_api.snapshot(stock_code=stock_code, field_list=field_list),
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="market",
            method="snapshot",
            timing=timing,
        )

    def full_tick(self, stock_code: str, fields: list[str] | None = None) -> Result:
        field_list = self._manager._resolve_fields("snapshot", fields)
        effective_profile = self._manager._build_effective_profile({"field_list": field_list})
        result, timing = capture_api_timing(
            "market.full_tick",
            lambda: self._manager._market_api.full_tick(stock_code=stock_code, field_list=field_list),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="market",
            method="full_tick",
            timing=timing,
        )

    def market_snapshot(self, stock_code: str, fields: list[str] | None = None) -> Result:
        field_list = self._manager._resolve_fields("market_snapshot", fields)
        effective_profile = self._manager._build_effective_profile({"field_list": field_list})
        result, timing = capture_api_timing(
            "market.market_snapshot",
            lambda: self._manager._market_api.market_snapshot(stock_code=stock_code, field_list=field_list),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="market",
            method="market_snapshot",
            timing=timing,
        )

    def kline(
        self,
        stock_list: list[str],
        period: str,
        start_time: str = "",
        end_time: str = "",
        count: int = -1,
        dividend_type: str | None = None,
        fields: list[str] | None = None,
        fill_data: bool | None = None,
    ) -> Result:
        field_list = self._manager._resolve_fields("kline", fields)
        resolved_dividend_type = dividend_type if dividend_type is not None else str(self._manager.profile_options.get("kline_dividend_type", "none"))
        resolved_fill_data = fill_data if fill_data is not None else bool(self._manager.profile_options.get("kline_fill_data", True))
        effective_profile = self._manager._build_effective_profile(
            {
                "field_list": field_list,
                "kline_dividend_type": resolved_dividend_type,
                "kline_fill_data": resolved_fill_data,
            }
        )
        result, timing = capture_api_timing(
            "market.kline",
            lambda: self._manager._market_api.kline(
                stock_list=stock_list,
                period=period,
                start_time=start_time,
                end_time=end_time,
                count=count,
                dividend_type=resolved_dividend_type,
                field_list=field_list,
                fill_data=resolved_fill_data,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="market",
            method="kline",
            timing=timing,
        )

    def stock_info(self, stock_code: str, fields: list[str] | None = None) -> Result:
        field_list = self._manager._resolve_fields("stock_info", fields)
        effective_profile = self._manager._build_effective_profile({"field_list": field_list})
        result, timing = capture_api_timing(
            "market.stock_info",
            lambda: self._manager._market_api.stock_info(stock_code=stock_code, field_list=field_list),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="market",
            method="stock_info",
            timing=timing,
        )

    def more_info(self, stock_code: str, fields: list[str] | None = None) -> Result:
        field_list = self._manager._resolve_fields("more_info", fields)
        effective_profile = self._manager._build_effective_profile({"field_list": field_list})
        result, timing = capture_api_timing(
            "market.more_info",
            lambda: self._manager._market_api.more_info(stock_code=stock_code, field_list=field_list),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="market",
            method="more_info",
            timing=timing,
        )

    def cb_info(self, stock_code: str, fields: list[str] | None = None) -> Result:
        field_list = self._manager._resolve_fields("cb_info", fields)
        effective_profile = self._manager._build_effective_profile({"field_list": field_list})
        result, timing = capture_api_timing(
            "market.cb_info",
            lambda: self._manager._market_api.cb_info(stock_code=stock_code, field_list=field_list),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="market",
            method="cb_info",
            timing=timing,
        )


class _MetaManagerProxy:
    __slots__ = ("_manager",)

    def __init__(self, manager: "TdxApiManager") -> None:
        self._manager = manager

    def stock_list(self, market: str | None = None, list_type: int | None = None) -> Result:
        resolved_list_type = self._manager._resolve_list_type(list_type)
        effective_profile = self._manager._build_effective_profile({"list_type": resolved_list_type})
        result, timing = capture_api_timing(
            "meta.stock_list",
            lambda: self._manager._meta_api.stock_list(market=market, list_type=resolved_list_type),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="meta",
            method="stock_list",
            timing=timing,
        )

    def sector_list(self, list_type: int | None = None) -> Result:
        resolved_list_type = self._manager._resolve_list_type(list_type)
        effective_profile = self._manager._build_effective_profile({"list_type": resolved_list_type})
        result, timing = capture_api_timing(
            "meta.sector_list",
            lambda: self._manager._meta_api.sector_list(list_type=resolved_list_type),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="meta",
            method="sector_list",
            timing=timing,
        )

    def sector_stocks(self, block_code: str, block_type: int = 0, list_type: int | None = None) -> Result:
        resolved_list_type = self._manager._resolve_list_type(list_type)
        effective_profile = self._manager._build_effective_profile({"list_type": resolved_list_type})
        result, timing = capture_api_timing(
            "meta.sector_stocks",
            lambda: self._manager._meta_api.sector_stocks(
                block_code=block_code,
                block_type=block_type,
                list_type=resolved_list_type,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="meta",
            method="sector_stocks",
            timing=timing,
        )

    def divid_factors(self, stock_code: str, start_time: str = "", end_time: str = "") -> Result:
        effective_profile = self._manager._build_effective_profile(
            {
                "stock_code": stock_code,
                "start_time": start_time,
                "end_time": end_time,
            }
        )
        result, timing = capture_api_timing(
            "meta.divid_factors",
            lambda: self._manager._meta_api.divid_factors(stock_code=stock_code, start_time=start_time, end_time=end_time),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="meta",
            method="divid_factors",
            timing=timing,
        )

    def ipo_info(self, ipo_type: int = 0, ipo_date: int = 0) -> Result:
        effective_profile = self._manager._build_effective_profile(
            {
                "ipo_type": ipo_type,
                "ipo_date": ipo_date,
            }
        )
        result, timing = capture_api_timing(
            "meta.ipo_info",
            lambda: self._manager._meta_api.ipo_info(ipo_type=ipo_type, ipo_date=ipo_date),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="meta",
            method="ipo_info",
            timing=timing,
        )

    def gb_info(self, stock_code: str, date_list: list[str], count: int) -> Result:
        effective_profile = self._manager._build_effective_profile({})
        result, timing = capture_api_timing(
            "meta.gb_info",
            lambda: self._manager._meta_api.gb_info(stock_code=stock_code, date_list=date_list, count=count),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="meta",
            method="gb_info",
            timing=timing,
        )

    def gp_one_data(self, stock_list: list[str], fields: list[str]) -> Result:
        effective_profile = self._manager._build_effective_profile({"field_list": list(fields)})
        result, timing = capture_api_timing(
            "meta.gp_one_data",
            lambda: self._manager._meta_api.gp_one_data(stock_list=stock_list, field_list=list(fields)),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="meta",
            method="gp_one_data",
            timing=timing,
        )


class _FormulaManagerProxy:
    __slots__ = ("_manager",)

    def __init__(self, manager: "TdxApiManager") -> None:
        self._manager = manager

    def format_data(self, kline_payload: dict[str, Any]) -> Result:
        effective_profile = self._manager._build_effective_profile({})
        result, timing = capture_api_timing(
            "formula.format_data",
            lambda: self._manager._formula_api.format_data(kline_payload=kline_payload),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="formula",
            method="format_data",
            timing=timing,
        )

    def set_data(
        self,
        stock_code: str,
        stock_period: str,
        stock_data: list[Any],
        count: int,
        dividend_type: int,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile({})
        result, timing = capture_api_timing(
            "formula.set_data",
            lambda: self._manager._formula_api.set_data(
                stock_code=stock_code,
                stock_period=stock_period,
                stock_data=stock_data,
                count=count,
                dividend_type=dividend_type,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="formula",
            method="set_data",
            timing=timing,
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
        effective_profile = self._manager._build_effective_profile({})
        result, timing = capture_api_timing(
            "formula.set_data_info",
            lambda: self._manager._formula_api.set_data_info(
                stock_code=stock_code,
                stock_period=stock_period,
                start_time=start_time,
                end_time=end_time,
                count=count,
                dividend_type=dividend_type,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="formula",
            method="set_data_info",
            timing=timing,
        )

    def get_data(self) -> Result:
        effective_profile = self._manager._build_effective_profile({})
        result, timing = capture_api_timing("formula.get_data", lambda: self._manager._formula_api.get_data())
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="formula",
            method="get_data",
            timing=timing,
        )

    def zb(self, formula_name: str, formula_arg: str = "", xsflag: int = -1) -> Result:
        effective_profile = self._manager._build_effective_profile({})
        result, timing = capture_api_timing(
            "formula.zb",
            lambda: self._manager._formula_api.zb(formula_name=formula_name, formula_arg=formula_arg, xsflag=xsflag),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="formula",
            method="zb",
            timing=timing,
        )

    def xg(self, formula_name: str, formula_arg: str = "") -> Result:
        effective_profile = self._manager._build_effective_profile({})
        result, timing = capture_api_timing(
            "formula.xg",
            lambda: self._manager._formula_api.xg(formula_name=formula_name, formula_arg=formula_arg),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="formula",
            method="xg",
            timing=timing,
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
        effective_profile = self._manager._build_effective_profile(
            {
                "formula_name": formula_name,
                "stock_list": list(stock_list),
                "formula_arg": formula_arg,
                "return_count": return_count,
                "return_date": return_date,
                "stock_period": stock_period,
                "start_time": start_time,
                "end_time": end_time,
                "count": count,
                "dividend_type": dividend_type,
            }
        )
        result, timing = capture_api_timing(
            "formula.screen",
            lambda: self._manager._dispatch_sync_capability(
                "formula.screen",
                lambda: self._manager._formula_api.screen(
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
                ),
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="formula",
            method="screen",
            timing=timing,
        )

    def exp(self, formula_name: str, formula_arg: str = "") -> Result:
        effective_profile = self._manager._build_effective_profile({})
        result, timing = capture_api_timing(
            "formula.exp",
            lambda: self._manager._formula_api.exp(formula_name=formula_name, formula_arg=formula_arg),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="formula",
            method="exp",
            timing=timing,
        )

    def process_mul_xg(
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
        effective_profile = self._manager._build_effective_profile({})
        result, timing = capture_api_timing(
            "formula.process_mul_xg",
            lambda: self._manager._formula_api.process_mul_xg(
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
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="formula",
            method="process_mul_xg",
            timing=timing,
        )

    def process_mul_zb(
        self,
        formula_name: str,
        stock_list: list[str],
        *,
        formula_arg: str = "",
        xsflag: int = -1,
        return_count: int = 1,
        return_date: bool = False,
        stock_period: str = "1d",
        start_time: str = "",
        end_time: str = "",
        count: int = 0,
        dividend_type: int = 0,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile({})
        result, timing = capture_api_timing(
            "formula.process_mul_zb",
            lambda: self._manager._formula_api.process_mul_zb(
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
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="formula",
            method="process_mul_zb",
            timing=timing,
        )


class _FinancialManagerProxy:
    __slots__ = ("_manager",)

    def __init__(self, manager: "TdxApiManager") -> None:
        self._manager = manager

    def financial_data(
        self,
        stock_list: list[str],
        fields: list[str],
        start_time: str = "",
        end_time: str = "",
        report_type: str = "report_time",
    ) -> Result:
        field_list = list(fields)
        effective_profile = self._manager._build_effective_profile(
            {
                "field_list": field_list,
                "start_time": start_time,
                "end_time": end_time,
                "report_type": report_type,
            }
        )
        result, timing = capture_api_timing(
            "financial.financial_data",
            lambda: self._manager._financial_api.financial_data(
                stock_list=stock_list,
                field_list=field_list,
                start_time=start_time,
                end_time=end_time,
                report_type=report_type,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="financial",
            method="financial_data",
            timing=timing,
        )

    def financial_data_by_date(
        self,
        stock_list: list[str],
        fields: list[str],
        year: int,
        mmdd: int,
    ) -> Result:
        field_list = list(fields)
        effective_profile = self._manager._build_effective_profile(
            {
                "field_list": field_list,
                "year": year,
                "mmdd": mmdd,
            }
        )
        result, timing = capture_api_timing(
            "financial.financial_data_by_date",
            lambda: self._manager._financial_api.financial_data_by_date(
                stock_list=stock_list,
                field_list=field_list,
                year=year,
                mmdd=mmdd,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="financial",
            method="financial_data_by_date",
            timing=timing,
        )


class _TransactionManagerProxy:
    __slots__ = ("_manager",)

    def __init__(self, manager: "TdxApiManager") -> None:
        self._manager = manager

    def stock_transaction_data(
        self,
        stock_list: list[str],
        fields: list[str],
        start_time: str = "",
        end_time: str = "",
    ) -> Result:
        field_list = list(fields)
        effective_profile = self._manager._build_effective_profile(
            {
                "field_list": field_list,
                "start_time": start_time,
                "end_time": end_time,
            }
        )
        result, timing = capture_api_timing(
            "transaction.stock_transaction_data",
            lambda: self._manager._transaction_api.stock_transaction_data(
                stock_list=stock_list,
                field_list=field_list,
                start_time=start_time,
                end_time=end_time,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="transaction",
            method="stock_transaction_data",
            timing=timing,
        )

    def stock_transaction_data_by_date(
        self,
        stock_list: list[str],
        fields: list[str],
        year: int,
        mmdd: int,
    ) -> Result:
        field_list = list(fields)
        effective_profile = self._manager._build_effective_profile(
            {
                "field_list": field_list,
                "year": year,
                "mmdd": mmdd,
            }
        )
        result, timing = capture_api_timing(
            "transaction.stock_transaction_data_by_date",
            lambda: self._manager._transaction_api.stock_transaction_data_by_date(
                stock_list=stock_list,
                field_list=field_list,
                year=year,
                mmdd=mmdd,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="transaction",
            method="stock_transaction_data_by_date",
            timing=timing,
        )

    def sector_transaction_data(
        self,
        stock_list: list[str],
        fields: list[str],
        start_time: str = "",
        end_time: str = "",
    ) -> Result:
        field_list = list(fields)
        effective_profile = self._manager._build_effective_profile(
            {
                "field_list": field_list,
                "start_time": start_time,
                "end_time": end_time,
            }
        )
        result, timing = capture_api_timing(
            "transaction.sector_transaction_data",
            lambda: self._manager._transaction_api.sector_transaction_data(
                stock_list=stock_list,
                field_list=field_list,
                start_time=start_time,
                end_time=end_time,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="transaction",
            method="sector_transaction_data",
            timing=timing,
        )

    def sector_transaction_data_by_date(
        self,
        stock_list: list[str],
        fields: list[str],
        year: int,
        mmdd: int,
    ) -> Result:
        field_list = list(fields)
        effective_profile = self._manager._build_effective_profile(
            {
                "field_list": field_list,
                "year": year,
                "mmdd": mmdd,
            }
        )
        result, timing = capture_api_timing(
            "transaction.sector_transaction_data_by_date",
            lambda: self._manager._transaction_api.sector_transaction_data_by_date(
                stock_list=stock_list,
                field_list=field_list,
                year=year,
                mmdd=mmdd,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="transaction",
            method="sector_transaction_data_by_date",
            timing=timing,
        )

    def market_transaction_data(
        self,
        fields: list[str],
        start_time: str = "",
        end_time: str = "",
    ) -> Result:
        field_list = list(fields)
        effective_profile = self._manager._build_effective_profile(
            {
                "field_list": field_list,
                "start_time": start_time,
                "end_time": end_time,
            }
        )
        result, timing = capture_api_timing(
            "transaction.market_transaction_data",
            lambda: self._manager._transaction_api.market_transaction_data(
                field_list=field_list,
                start_time=start_time,
                end_time=end_time,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="transaction",
            method="market_transaction_data",
            timing=timing,
        )

    def market_transaction_data_by_date(
        self,
        fields: list[str],
        year: int,
        mmdd: int,
    ) -> Result:
        field_list = list(fields)
        effective_profile = self._manager._build_effective_profile(
            {
                "field_list": field_list,
                "year": year,
                "mmdd": mmdd,
            }
        )
        result, timing = capture_api_timing(
            "transaction.market_transaction_data_by_date",
            lambda: self._manager._transaction_api.market_transaction_data_by_date(
                field_list=field_list,
                year=year,
                mmdd=mmdd,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="transaction",
            method="market_transaction_data_by_date",
            timing=timing,
        )


class _RuntimeManagerProxy:
    __slots__ = ("_manager",)

    def __init__(self, manager: "TdxApiManager") -> None:
        self._manager = manager

    def capabilities(self) -> Result:
        effective_profile = self._manager._build_effective_profile({})
        result, timing = capture_api_timing(
            "runtime.capabilities",
            lambda: self._manager._dispatch_sync_capability(
                "runtime.capabilities",
                lambda: self._manager._runtime_api.capabilities(),
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="runtime",
            method="capabilities",
            timing=timing,
        )

    def trading_dates(
        self,
        market: str | None = None,
        start_time: str = "",
        end_time: str = "",
        count: int | None = None,
    ) -> Result:
        resolved_market = market if market is not None else str(self._manager.profile_options.get("trading_dates_market", "SH"))
        resolved_count = count if count is not None else int(self._manager.profile_options.get("trading_dates_count", -1))
        effective_profile = self._manager._build_effective_profile(
            {
                "trading_dates_market": resolved_market,
                "start_time": start_time,
                "end_time": end_time,
                "trading_dates_count": resolved_count,
            }
        )
        result, timing = capture_api_timing(
            "runtime.trading_dates",
            lambda: self._manager._runtime_api.trading_dates(
                market=resolved_market,
                start_time=start_time,
                end_time=end_time,
                count=resolved_count,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="runtime",
            method="trading_dates",
            timing=timing,
        )

    def refresh_kline(self, stock_list: list[str], period: str) -> Result:
        effective_profile = self._manager._build_effective_profile({"stock_list": list(stock_list), "period": period})
        result, timing = capture_api_timing(
            "runtime.refresh_kline",
            lambda: self._manager._runtime_api.refresh_kline(stock_list=stock_list, period=period),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="runtime",
            method="refresh_kline",
            timing=timing,
        )

    def download_file(self, stock_code: str, down_time: str = "", down_type: int = 1) -> Result:
        effective_profile = self._manager._build_effective_profile(
            {
                "stock_code": stock_code,
                "down_time": down_time,
                "down_type": down_type,
            }
        )
        result, timing = capture_api_timing(
            "runtime.download_file",
            lambda: self._manager._runtime_api.download_file(
                stock_code=stock_code,
                down_time=down_time,
                down_type=down_type,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="runtime",
            method="download_file",
            timing=timing,
        )

    def send_warn(
        self,
        stock_list: list[str],
        time_list: list[str],
        price_list: list[str] | None = None,
        close_list: list[str] | None = None,
        volume_list: list[str] | None = None,
        bs_flag_list: list[str] | None = None,
        warn_type_list: list[str] | None = None,
        reason_list: list[str] | None = None,
        count: int = 1,
    ) -> Result:
        resolved_price_list = list(price_list or [])
        resolved_close_list = list(close_list or [])
        resolved_volume_list = list(volume_list or [])
        resolved_bs_flag_list = list(bs_flag_list or [])
        resolved_warn_type_list = list(warn_type_list or [])
        resolved_reason_list = list(reason_list or [])
        effective_profile = self._manager._build_effective_profile(
            {
                "stock_list": list(stock_list),
                "time_list": list(time_list),
                "price_list": resolved_price_list,
                "close_list": resolved_close_list,
                "volume_list": resolved_volume_list,
                "bs_flag_list": resolved_bs_flag_list,
                "warn_type_list": resolved_warn_type_list,
                "reason_list": resolved_reason_list,
                "count": count,
            }
        )
        result, timing = capture_api_timing(
            "runtime.send_warn",
            lambda: self._manager._runtime_api.send_warn(
                stock_list=stock_list,
                time_list=time_list,
                price_list=resolved_price_list,
                close_list=resolved_close_list,
                volume_list=resolved_volume_list,
                bs_flag_list=resolved_bs_flag_list,
                warn_type_list=resolved_warn_type_list,
                reason_list=resolved_reason_list,
                count=count,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="runtime",
            method="send_warn",
            timing=timing,
        )

    def open_subscription_session(self):
        raw_session = self._manager._runtime_api.open_subscription_session()
        return _RuntimeManagerSubscriptionSession(manager=self._manager, raw_session=raw_session)

    def health(self, window_key: str = "通达信金融终端", hid_port: str | None = None) -> Result:
        effective_profile = self._manager._build_effective_profile({"window_key": window_key, "hid_port": hid_port})
        result, timing = capture_api_timing(
            "runtime.health",
            lambda: self._manager._dispatch_sync_capability(
                "runtime.health",
                lambda: self._manager._runtime_api.health(window_key=window_key, hid_port=hid_port),
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="runtime",
            method="health",
            timing=timing,
        )

    def doctor(self, window_key: str = "通达信金融终端", hid_port: str | None = None) -> Result:
        effective_profile = self._manager._build_effective_profile({"window_key": window_key, "hid_port": hid_port})
        result, timing = capture_api_timing(
            "runtime.doctor",
            lambda: self._manager._dispatch_sync_capability(
                "runtime.doctor",
                lambda: self._manager._runtime_api.doctor(window_key=window_key, hid_port=hid_port),
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="runtime",
            method="doctor",
            timing=timing,
        )


class _RuntimeManagerSubscriptionSession:
    __slots__ = ("_manager", "_raw_session", "session_id", "strategy_path")

    def __init__(self, manager: "TdxApiManager", raw_session: Any) -> None:
        self._manager = manager
        self._raw_session = raw_session
        self.session_id = str(getattr(raw_session, "session_id", ""))
        self.strategy_path = getattr(raw_session, "strategy_path", manager.strategy_path)

    def __enter__(self) -> "_RuntimeManagerSubscriptionSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    @property
    def closed(self) -> bool:
        return bool(getattr(self._raw_session, "closed", False))

    def _attach_session_metadata(self, result: Result) -> Result:
        result.data["runtime_session"] = {
            "session_id": self.session_id,
            "strategy_path": self.strategy_path,
            "closed": self.closed,
        }
        return result

    def subscribe_hq(self, stock_list: list[str], callback) -> Result:
        effective_profile = self._manager._build_effective_profile(
            {
                "session_id": self.session_id,
                "stock_list": list(stock_list),
            }
        )
        result, timing = capture_api_timing(
            "runtime.subscribe_hq",
            lambda: self._raw_session.subscribe_hq(stock_list=stock_list, callback=callback),
        )
        self._attach_session_metadata(result)
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="runtime",
            method="subscribe_hq",
            timing=timing,
        )

    def unsubscribe_hq(self, stock_list: list[str]) -> Result:
        effective_profile = self._manager._build_effective_profile(
            {
                "session_id": self.session_id,
                "stock_list": list(stock_list),
            }
        )
        result, timing = capture_api_timing(
            "runtime.unsubscribe_hq",
            lambda: self._raw_session.unsubscribe_hq(stock_list=stock_list),
        )
        self._attach_session_metadata(result)
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="runtime",
            method="unsubscribe_hq",
            timing=timing,
        )

    def get_subscribe_hq_stock_list(self) -> Result:
        effective_profile = self._manager._build_effective_profile({"session_id": self.session_id})
        result, timing = capture_api_timing(
            "runtime.get_subscribe_hq_stock_list",
            lambda: self._raw_session.get_subscribe_hq_stock_list(),
        )
        self._attach_session_metadata(result)
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="runtime",
            method="get_subscribe_hq_stock_list",
            timing=timing,
        )

    def close(self) -> None:
        self._raw_session.close()


class _BlockManagerProxy:
    __slots__ = ("_manager",)

    def __init__(self, manager: "TdxApiManager") -> None:
        self._manager = manager

    def user_sectors(self) -> Result:
        effective_profile = self._manager._build_effective_profile({})
        result, timing = capture_api_timing(
            "block.user_sectors",
            lambda: self._manager._block_api.user_sectors(),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="block",
            method="user_sectors",
            timing=timing,
        )

    def read_watchlist_snapshot(self, block_code: str) -> Result:
        effective_profile = self._manager._build_effective_profile({"block_code": block_code})
        result, timing = capture_api_timing(
            "block.read_watchlist_snapshot",
            lambda: self._manager._block_api.read_watchlist_snapshot(block_code=block_code),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="block",
            method="read_watchlist_snapshot",
            timing=timing,
        )

    def create_sector(
        self,
        block_code: str,
        block_name: str,
        mutation_key: str | None = None,
        audit_dir: str | None = None,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile(
            {
                "block_code": block_code,
                "block_name": block_name,
                "mutation_key": mutation_key,
                "audit_dir": audit_dir,
            }
        )
        options: dict[str, str] = {}
        if mutation_key is not None:
            options["mutation_key"] = mutation_key
        if audit_dir is not None:
            options["audit_dir"] = audit_dir
        result, timing = capture_api_timing(
            "block.create_sector",
            lambda: self._manager._block_api.create_sector(
                block_code=block_code,
                block_name=block_name,
                **options,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="block",
            method="create_sector",
            timing=timing,
        )

    def delete_sector(
        self,
        block_code: str,
        mutation_key: str | None = None,
        audit_dir: str | None = None,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile(
            {
                "block_code": block_code,
                "mutation_key": mutation_key,
                "audit_dir": audit_dir,
            }
        )
        options: dict[str, str] = {}
        if mutation_key is not None:
            options["mutation_key"] = mutation_key
        if audit_dir is not None:
            options["audit_dir"] = audit_dir
        result, timing = capture_api_timing(
            "block.delete_sector",
            lambda: self._manager._block_api.delete_sector(
                block_code=block_code,
                **options,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="block",
            method="delete_sector",
            timing=timing,
        )

    def rename_sector(
        self,
        block_code: str,
        block_name: str,
        mutation_key: str | None = None,
        audit_dir: str | None = None,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile(
            {
                "block_code": block_code,
                "block_name": block_name,
                "mutation_key": mutation_key,
                "audit_dir": audit_dir,
            }
        )
        options: dict[str, str] = {}
        if mutation_key is not None:
            options["mutation_key"] = mutation_key
        if audit_dir is not None:
            options["audit_dir"] = audit_dir
        result, timing = capture_api_timing(
            "block.rename_sector",
            lambda: self._manager._block_api.rename_sector(
                block_code=block_code,
                block_name=block_name,
                **options,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="block",
            method="rename_sector",
            timing=timing,
        )

    def clear_sector(
        self,
        block_code: str,
        mutation_key: str | None = None,
        audit_dir: str | None = None,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile(
            {
                "block_code": block_code,
                "mutation_key": mutation_key,
                "audit_dir": audit_dir,
            }
        )
        options: dict[str, str] = {}
        if mutation_key is not None:
            options["mutation_key"] = mutation_key
        if audit_dir is not None:
            options["audit_dir"] = audit_dir
        result, timing = capture_api_timing(
            "block.clear_sector",
            lambda: self._manager._block_api.clear_sector(
                block_code=block_code,
                **options,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="block",
            method="clear_sector",
            timing=timing,
        )

    def send_user_block(
        self,
        block_code: str,
        stocks: list[str],
        show: bool = False,
        mutation_key: str | None = None,
        audit_dir: str | None = None,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile(
            {
                "block_code": block_code,
                "stocks": list(stocks),
                "show": show,
                "mutation_key": mutation_key,
                "audit_dir": audit_dir,
            }
        )
        options: dict[str, str] = {}
        if mutation_key is not None:
            options["mutation_key"] = mutation_key
        if audit_dir is not None:
            options["audit_dir"] = audit_dir
        result, timing = capture_api_timing(
            "block.send_user_block",
            lambda: self._manager._dispatch_sync_capability(
                "block.send_user_block",
                lambda: self._manager._block_api.send_user_block(
                    block_code=block_code,
                    stocks=stocks,
                    show=show,
                    **options,
                ),
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="block",
            method="send_user_block",
            timing=timing,
        )

    def sync_watchlist(
        self,
        block_code: str,
        symbols: list[str],
        mode: str = "replace",
        create_if_missing: bool = False,
        dry_run: bool = False,
        show: bool = True,
        write_policy: str | None = None,
        mutation_key: str | None = None,
        audit_dir: str | None = None,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile(
            {
                "block_code": block_code,
                "symbols": list(symbols),
                "mode": mode,
                "create_if_missing": create_if_missing,
                "dry_run": dry_run,
                "show": show,
                "write_policy": write_policy,
                "mutation_key": mutation_key,
                "audit_dir": audit_dir,
            }
        )
        options: dict[str, str] = {}
        if mutation_key is not None:
            options["mutation_key"] = mutation_key
        if audit_dir is not None:
            options["audit_dir"] = audit_dir
        result, timing = capture_api_timing(
            "block.sync_watchlist",
            lambda: self._manager._dispatch_sync_capability(
                "block.sync_watchlist",
                lambda: self._manager._block_api.sync_watchlist(
                    block_code=block_code,
                    symbols=symbols,
                    mode=mode,
                    create_if_missing=create_if_missing,
                    dry_run=dry_run,
                    show=show,
                    write_policy=write_policy,
                    **options,
                ),
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            domain="block",
            method="sync_watchlist",
            timing=timing,
        )


class TdxApiManager:
    __slots__ = (
        "profile_name",
        "profile_options",
        "strategy_path",
        "provider_mode",
        "replay_fixture",
        "replay_fixture_path",
        "replay_fixture_map",
        "_market_api",
        "_meta_api",
        "_financial_api",
        "_transaction_api",
        "_formula_api",
        "_runtime_api",
        "_block_api",
        "market",
        "meta",
        "financial",
        "transaction",
        "formula",
        "runtime",
        "block",
    )

    def __init__(
        self,
        *,
        profile: str = "default",
        strategy_path: str | None = None,
        profile_overrides: dict[str, Any] | None = None,
        provider_mode: str = "live",
        replay_fixture: str | None = None,
        replay_fixture_path: str | None = None,
        replay_fixture_map: dict[str, Any] | None = None,
    ) -> None:
        self.profile_name = profile
        self.profile_options = resolve_api_profile(profile, overrides=profile_overrides)
        self.strategy_path = strategy_path
        self.provider_mode = normalize_provider_mode(provider_mode)
        self.replay_fixture = replay_fixture
        self.replay_fixture_path = replay_fixture_path
        self.replay_fixture_map = dict(replay_fixture_map or {})
        self._market_api = MarketApi(strategy_path=strategy_path)
        self._meta_api = MetaApi(strategy_path=strategy_path)
        self._financial_api = FinancialApi(strategy_path=strategy_path)
        self._transaction_api = TransactionApi(strategy_path=strategy_path)
        self._formula_api = FormulaApi(strategy_path=strategy_path)
        self._runtime_api = RuntimeApi(strategy_path=strategy_path)
        self._block_api = BlockApi(strategy_path=strategy_path)
        self.market = _MarketManagerProxy(self)
        self.meta = _MetaManagerProxy(self)
        self.financial = _FinancialManagerProxy(self)
        self.transaction = _TransactionManagerProxy(self)
        self.formula = _FormulaManagerProxy(self)
        self.runtime = _RuntimeManagerProxy(self)
        self.block = _BlockManagerProxy(self)

    def _resolve_fields(self, field_key: str, explicit_fields: list[str] | None) -> list[str]:
        if explicit_fields is not None:
            return list(explicit_fields)
        default_fields = self.profile_options.get("default_fields", {})
        if isinstance(default_fields, dict):
            selected = default_fields.get(field_key, [])
            if isinstance(selected, list):
                return list(selected)
        return []

    def _resolve_list_type(self, explicit_list_type: int | None) -> int:
        if explicit_list_type is not None:
            return int(explicit_list_type)
        return int(self.profile_options.get("list_type", 0))

    def _build_effective_profile(self, overrides: dict[str, Any]) -> dict[str, Any]:
        effective = dict(self.profile_options)
        for key, value in overrides.items():
            effective[key] = value
        return effective

    def _is_replay_mode(self) -> bool:
        return is_replay_mode(self.provider_mode)

    def _execute_sync_replay(self, capability: str) -> Result:
        return execute_sync_replay(
            capability,
            replay_fixture=self.replay_fixture,
            replay_fixture_path=self.replay_fixture_path,
            replay_fixture_map=self.replay_fixture_map,
        )

    def _dispatch_sync_capability(self, capability: str, live_call: Any) -> Result:
        if self._is_replay_mode():
            return self._execute_sync_replay(capability)
        return live_call()

    def refresh_cache(self, market: str | None = None, force: bool | None = None) -> Result:
        resolved_market = market if market is not None else str(self.profile_options.get("refresh_market", "AG"))
        resolved_force = force if force is not None else bool(self.profile_options.get("refresh_force", False))
        effective_profile = self._build_effective_profile({"refresh_market": resolved_market, "refresh_force": resolved_force})
        result, timing = capture_api_timing(
            "manager.refresh_cache",
            lambda: run_tdx_refresh_cache(
                market=resolved_market,
                force=resolved_force,
                strategy_path=self.strategy_path,
            ),
        )
        return attach_manager_metadata(
            result,
            profile_name=self.profile_name,
            profile_options=effective_profile,
            domain="manager",
            method="refresh_cache",
            timing=timing,
        )
