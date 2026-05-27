from __future__ import annotations

from ..models import Result
from .bridge import (
    run_tdx_download_file,
    run_tdx_exec_to_tdx,
    run_tdx_get_trading_dates,
    run_tdx_open_subscription_session,
    run_tdx_print_to_tdx,
    run_tdx_provider_capabilities,
    run_tdx_provider_doctor,
    run_tdx_provider_health,
    run_tdx_refresh_kline,
    run_tdx_send_bt_data,
    run_tdx_send_file,
    run_tdx_send_message,
    run_tdx_send_warn,
    run_tdx_subscription_list,
    run_tdx_subscription_subscribe,
    run_tdx_subscription_unsubscribe,
)


class RuntimeApi:
    __slots__ = ("strategy_path",)

    def __init__(self, strategy_path: str | None = None) -> None:
        self.strategy_path = strategy_path

    def capabilities(self) -> Result:
        return run_tdx_provider_capabilities()

    def trading_dates(
        self,
        market: str,
        start_time: str,
        end_time: str,
        count: int,
    ) -> Result:
        return run_tdx_get_trading_dates(
            market=market,
            start_time=start_time,
            end_time=end_time,
            count=count,
            strategy_path=self.strategy_path,
        )

    def refresh_kline(self, stock_list: list[str], period: str) -> Result:
        return run_tdx_refresh_kline(
            stock_list=stock_list,
            period=period,
            strategy_path=self.strategy_path,
        )

    def download_file(self, stock_code: str, down_time: str, down_type: int) -> Result:
        return run_tdx_download_file(
            stock_code=stock_code,
            down_time=down_time,
            down_type=down_type,
            strategy_path=self.strategy_path,
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
        return run_tdx_send_warn(
            stock_list=stock_list,
            time_list=time_list,
            price_list=list(price_list or []),
            close_list=list(close_list or []),
            volume_list=list(volume_list or []),
            bs_flag_list=list(bs_flag_list or []),
            warn_type_list=list(warn_type_list or []),
            reason_list=list(reason_list or []),
            count=count,
            strategy_path=self.strategy_path,
        )

    def open_subscription_session(self):
        return run_tdx_open_subscription_session(strategy_path=self.strategy_path)

    def subscription_subscribe(self, stock_list: list[str]) -> Result:
        return run_tdx_subscription_subscribe(stock_list=stock_list, strategy_path=self.strategy_path)

    def subscription_unsubscribe(self, stock_list: list[str]) -> Result:
        return run_tdx_subscription_unsubscribe(stock_list=stock_list, strategy_path=self.strategy_path)

    def subscription_list(self) -> Result:
        return run_tdx_subscription_list(strategy_path=self.strategy_path)

    def health(self, window_key: str = "通达信金融终端", hid_port: str | None = None) -> Result:
        return run_tdx_provider_health(
            window_key=window_key,
            strategy_path=self.strategy_path,
            hid_port=hid_port,
        )

    def doctor(self, window_key: str = "通达信金融终端", hid_port: str | None = None) -> Result:
        return run_tdx_provider_doctor(
            window_key=window_key,
            strategy_path=self.strategy_path,
            hid_port=hid_port,
        )

    def send_message(self, msg_str: str) -> Result:
        return run_tdx_send_message(msg_str=msg_str, strategy_path=self.strategy_path)

    def send_file(self, file: str) -> Result:
        return run_tdx_send_file(file=file, strategy_path=self.strategy_path)

    def send_bt_data(
        self,
        stock_code: str,
        time_list: list[str],
        data_list: list[list[str]],
        count: int = 1,
    ) -> Result:
        return run_tdx_send_bt_data(
            stock_code=stock_code,
            time_list=time_list,
            data_list=data_list,
            count=count,
            strategy_path=self.strategy_path,
        )

    def print_to_tdx(
        self,
        df_list: list,
        sp_name: str = "",
        xml_filename: str = "",
        jsn_filenames: list[str] | None = None,
        vertical: int | None = None,
        horizontal: int | None = None,
        height: list | None = None,
        table_names: list[str] | None = None,
    ) -> Result:
        return run_tdx_print_to_tdx(
            df_list=df_list,
            sp_name=sp_name,
            xml_filename=xml_filename,
            jsn_filenames=jsn_filenames,
            vertical=vertical,
            horizontal=horizontal,
            height=height,
            table_names=table_names,
            strategy_path=self.strategy_path,
        )

    def exec_to_tdx(self, url: str) -> Result:
        return run_tdx_exec_to_tdx(url=url, strategy_path=self.strategy_path)
