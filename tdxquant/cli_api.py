from __future__ import annotations

import argparse
import json
from pathlib import Path

from .api import TdxApiManager
from .models import ErrorCode, Result


def _add_api_common_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--profile", default="default")
    subparser.add_argument("--strategy-path")
    _add_replay_provider_arguments(subparser)
    subparser.add_argument("--output", help="Optional path to write the JSON result")


def _add_block_mutation_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--mutation-key")
    subparser.add_argument("--audit-dir")


def _add_block_sync_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--block-code", required=True)
    subparser.add_argument("--stock", action="append", default=[])
    subparser.add_argument("--mode", choices=("replace", "merge"), default="replace")
    subparser.add_argument("--write-policy", choices=("replace", "merge", "replace_dry_run", "merge_dry_run"))
    subparser.add_argument("--create-if-missing", action=argparse.BooleanOptionalAction, default=False)
    subparser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=False)
    subparser.add_argument("--show", action=argparse.BooleanOptionalAction, default=True)
    _add_block_mutation_arguments(subparser)


def _add_replay_provider_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--provider-mode", choices=("live", "replay"), default="live")
    replay_group = subparser.add_mutually_exclusive_group()
    replay_group.add_argument("--fixture")
    replay_group.add_argument("--fixture-path")


_SUPPORTED_API_REPLAY_COMMANDS = {
    "capabilities",
    "health",
    "doctor",
    "formula-screen",
    "market-snapshot",
    "full-tick",
    "stock-info",
    "more-info",
    "cb-info",
    "gb-info",
    "ipo-info",
    "gp-one",
    "divid-factors",
    "sector-list",
    "stock-transaction-data-by-date",
    "sector-transaction-data",
    "sector-transaction-data-by-date",
    "market-transaction-data-by-date",
    "subscription-subscribe",
    "subscription-unsubscribe",
    "subscription-list",
    "send-user-block",
    "block-read-watchlist",
}

_API_REPLAY_CAPABILITIES = {
    "snapshot": "market.snapshot",
    "market-snapshot": "market.market_snapshot",
    "full-tick": "market.full_tick",
    "stock-info": "market.stock_info",
    "more-info": "market.more_info",
    "cb-info": "market.cb_info",
    "gb-info": "meta.gb_info",
    "ipo-info": "meta.ipo_info",
    "gp-one": "meta.gp_one_data",
    "divid-factors": "meta.divid_factors",
    "sector-list": "meta.sector_list",
    "stock-transaction-data-by-date": "transaction.stock_transaction_data_by_date",
    "sector-transaction-data": "transaction.sector_transaction_data",
    "sector-transaction-data-by-date": "transaction.sector_transaction_data_by_date",
    "market-transaction-data-by-date": "transaction.market_transaction_data_by_date",
    "subscription-subscribe": "subscription.subscribe_hq",
    "subscription-unsubscribe": "subscription.unsubscribe_hq",
    "subscription-list": "subscription.get_subscribe_hq_stock_list",
    "send-user-block": "block.send_user_block",
    "block-read-watchlist": "block.read_watchlist_snapshot",
    "formula-screen": "formula.screen",
}


def _build_cli_replay_failure_result(*, capability: str, message: str) -> Result:
    return Result(
        ok=False,
        code=ErrorCode.INVALID_REQUEST,
        message=message,
        data={
            "replay_source": {
                "mode": "replay",
                "capability": capability,
            }
        },
    )


def _infer_api_replay_capability(args: argparse.Namespace) -> str:
    return _API_REPLAY_CAPABILITIES.get(args.api_command, f"api.{args.api_command}")


def _reject_unsupported_api_replay(args: argparse.Namespace) -> Result | None:
    if getattr(args, "provider_mode", "live") != "replay":
        return None
    if args.api_command in _SUPPORTED_API_REPLAY_COMMANDS:
        return None
    return _build_cli_replay_failure_result(
        capability=_infer_api_replay_capability(args),
        message=f"unsupported replay api command: {args.api_command}",
    )

def build_api_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> argparse.ArgumentParser:
    api_parser = subparsers.add_parser("api")
    api_subparsers = api_parser.add_subparsers(dest="api_command", required=True)

    api_capabilities_parser = api_subparsers.add_parser("capabilities")
    _add_api_common_arguments(api_capabilities_parser)

    api_health_parser = api_subparsers.add_parser("health")
    api_health_parser.add_argument("--window-key", default="通达信金融终端")
    api_health_parser.add_argument("--hid-port")
    _add_api_common_arguments(api_health_parser)

    api_doctor_parser = api_subparsers.add_parser("doctor")
    api_doctor_parser.add_argument("--window-key", default="通达信金融终端")
    api_doctor_parser.add_argument("--hid-port")
    _add_api_common_arguments(api_doctor_parser)

    api_subscription_subscribe_parser = api_subparsers.add_parser("subscription-subscribe")
    api_subscription_subscribe_parser.add_argument("--code", action="append", required=True)
    _add_api_common_arguments(api_subscription_subscribe_parser)

    api_subscription_unsubscribe_parser = api_subparsers.add_parser("subscription-unsubscribe")
    api_subscription_unsubscribe_parser.add_argument("--code", action="append", required=True)
    _add_api_common_arguments(api_subscription_unsubscribe_parser)

    api_subscription_list_parser = api_subparsers.add_parser("subscription-list")
    _add_api_common_arguments(api_subscription_list_parser)

    api_snapshot_parser = api_subparsers.add_parser("snapshot")
    api_snapshot_parser.add_argument("--code", required=True)
    api_snapshot_parser.add_argument("--field", action="append", default=None)
    _add_api_common_arguments(api_snapshot_parser)

    api_market_snapshot_parser = api_subparsers.add_parser("market-snapshot")
    api_market_snapshot_parser.add_argument("--code", required=True)
    api_market_snapshot_parser.add_argument("--field", action="append", default=None)
    _add_api_common_arguments(api_market_snapshot_parser)

    api_kline_parser = api_subparsers.add_parser("kline")
    api_kline_parser.add_argument("--code", action="append", required=True)
    api_kline_parser.add_argument("--period", required=True)
    api_kline_parser.add_argument("--start-time", default="")
    api_kline_parser.add_argument("--end-time", default="")
    api_kline_parser.add_argument("--count", type=int, default=-1)
    api_kline_parser.add_argument("--dividend-type", choices=["none", "front", "back"])
    api_kline_parser.add_argument("--field", action="append", default=None)
    api_kline_parser.add_argument("--fill-data", action=argparse.BooleanOptionalAction, default=None)
    _add_api_common_arguments(api_kline_parser)

    api_full_tick_parser = api_subparsers.add_parser("full-tick")
    api_full_tick_parser.add_argument("--code", required=True)
    api_full_tick_parser.add_argument("--field", action="append", default=None)
    _add_api_common_arguments(api_full_tick_parser)

    api_stock_info_parser = api_subparsers.add_parser("stock-info")
    api_stock_info_parser.add_argument("--code", required=True)
    api_stock_info_parser.add_argument("--field", action="append", default=None)
    _add_api_common_arguments(api_stock_info_parser)

    api_more_info_parser = api_subparsers.add_parser("more-info")
    api_more_info_parser.add_argument("--code", required=True)
    api_more_info_parser.add_argument("--field", action="append", default=None)
    _add_api_common_arguments(api_more_info_parser)

    api_cb_info_parser = api_subparsers.add_parser("cb-info")
    api_cb_info_parser.add_argument("--code", required=True)
    api_cb_info_parser.add_argument("--field", action="append", default=None)
    _add_api_common_arguments(api_cb_info_parser)

    api_stock_list_parser = api_subparsers.add_parser("stock-list")
    api_stock_list_parser.add_argument("--market")
    api_stock_list_parser.add_argument("--list-type", type=int, choices=[0, 1])
    _add_api_common_arguments(api_stock_list_parser)

    api_sector_list_parser = api_subparsers.add_parser("sector-list")
    api_sector_list_parser.add_argument("--list-type", type=int, choices=[0, 1])
    _add_api_common_arguments(api_sector_list_parser)

    api_sector_stocks_parser = api_subparsers.add_parser("sector-stocks")
    api_sector_stocks_parser.add_argument("--sector", required=True)
    api_sector_stocks_parser.add_argument("--block-type", type=int, default=0, choices=[0, 1])
    api_sector_stocks_parser.add_argument("--list-type", type=int, choices=[0, 1])
    _add_api_common_arguments(api_sector_stocks_parser)

    api_gb_info_parser = api_subparsers.add_parser("gb-info")
    api_gb_info_parser.add_argument("--code", required=True)
    api_gb_info_parser.add_argument("--date", action="append", required=True)
    api_gb_info_parser.add_argument("--count", type=int, required=True)
    _add_api_common_arguments(api_gb_info_parser)

    api_gp_one_parser = api_subparsers.add_parser("gp-one")
    api_gp_one_parser.add_argument("--code", action="append", required=True)
    api_gp_one_parser.add_argument("--field", action="append", required=True)
    _add_api_common_arguments(api_gp_one_parser)

    api_divid_factors_parser = api_subparsers.add_parser("divid-factors")
    api_divid_factors_parser.add_argument("--code", required=True)
    api_divid_factors_parser.add_argument("--start-time", default="")
    api_divid_factors_parser.add_argument("--end-time", default="")
    _add_api_common_arguments(api_divid_factors_parser)

    api_ipo_info_parser = api_subparsers.add_parser("ipo-info")
    api_ipo_info_parser.add_argument("--ipo-type", default=0, type=int, choices=[0, 1, 2])
    api_ipo_info_parser.add_argument("--ipo-date", default=0, type=int, choices=[0, 1])
    _add_api_common_arguments(api_ipo_info_parser)

    api_financial_data_parser = api_subparsers.add_parser("financial-data")
    api_financial_data_parser.add_argument("--code", action="append", required=True)
    api_financial_data_parser.add_argument("--field", action="append", required=True)
    api_financial_data_parser.add_argument("--start-time", default="")
    api_financial_data_parser.add_argument("--end-time", default="")
    api_financial_data_parser.add_argument("--report-type", default="report_time")
    _add_api_common_arguments(api_financial_data_parser)

    api_financial_data_by_date_parser = api_subparsers.add_parser("financial-data-by-date")
    api_financial_data_by_date_parser.add_argument("--code", action="append", required=True)
    api_financial_data_by_date_parser.add_argument("--field", action="append", required=True)
    api_financial_data_by_date_parser.add_argument("--year", required=True, type=int)
    api_financial_data_by_date_parser.add_argument("--mmdd", required=True, type=int)
    _add_api_common_arguments(api_financial_data_by_date_parser)

    api_stock_transaction_data_parser = api_subparsers.add_parser("stock-transaction-data")
    api_stock_transaction_data_parser.add_argument("--code", action="append", required=True)
    api_stock_transaction_data_parser.add_argument("--field", action="append", required=True)
    api_stock_transaction_data_parser.add_argument("--start-time", default="")
    api_stock_transaction_data_parser.add_argument("--end-time", default="")
    _add_api_common_arguments(api_stock_transaction_data_parser)

    api_stock_transaction_data_by_date_parser = api_subparsers.add_parser("stock-transaction-data-by-date")
    api_stock_transaction_data_by_date_parser.add_argument("--code", action="append", required=True)
    api_stock_transaction_data_by_date_parser.add_argument("--field", action="append", required=True)
    api_stock_transaction_data_by_date_parser.add_argument("--year", required=True, type=int)
    api_stock_transaction_data_by_date_parser.add_argument("--mmdd", required=True, type=int)
    _add_api_common_arguments(api_stock_transaction_data_by_date_parser)

    api_sector_transaction_data_parser = api_subparsers.add_parser("sector-transaction-data")
    api_sector_transaction_data_parser.add_argument("--code", action="append", required=True)
    api_sector_transaction_data_parser.add_argument("--field", action="append", required=True)
    api_sector_transaction_data_parser.add_argument("--start-time", default="")
    api_sector_transaction_data_parser.add_argument("--end-time", default="")
    _add_api_common_arguments(api_sector_transaction_data_parser)

    api_sector_transaction_data_by_date_parser = api_subparsers.add_parser("sector-transaction-data-by-date")
    api_sector_transaction_data_by_date_parser.add_argument("--code", action="append", required=True)
    api_sector_transaction_data_by_date_parser.add_argument("--field", action="append", required=True)
    api_sector_transaction_data_by_date_parser.add_argument("--year", required=True, type=int)
    api_sector_transaction_data_by_date_parser.add_argument("--mmdd", required=True, type=int)
    _add_api_common_arguments(api_sector_transaction_data_by_date_parser)

    api_market_transaction_data_parser = api_subparsers.add_parser("market-transaction-data")
    api_market_transaction_data_parser.add_argument("--field", action="append", required=True)
    api_market_transaction_data_parser.add_argument("--start-time", default="")
    api_market_transaction_data_parser.add_argument("--end-time", default="")
    _add_api_common_arguments(api_market_transaction_data_parser)

    api_market_transaction_data_by_date_parser = api_subparsers.add_parser("market-transaction-data-by-date")
    api_market_transaction_data_by_date_parser.add_argument("--field", action="append", required=True)
    api_market_transaction_data_by_date_parser.add_argument("--year", required=True, type=int)
    api_market_transaction_data_by_date_parser.add_argument("--mmdd", required=True, type=int)
    _add_api_common_arguments(api_market_transaction_data_by_date_parser)

    api_refresh_cache_parser = api_subparsers.add_parser("refresh-cache")
    api_refresh_cache_parser.add_argument("--market")
    api_refresh_cache_parser.add_argument("--force", action=argparse.BooleanOptionalAction, default=None)
    _add_api_common_arguments(api_refresh_cache_parser)

    api_trading_dates_parser = api_subparsers.add_parser("trading-dates")
    api_trading_dates_parser.add_argument("--market")
    api_trading_dates_parser.add_argument("--start-time", default="")
    api_trading_dates_parser.add_argument("--end-time", default="")
    api_trading_dates_parser.add_argument("--count", type=int)
    _add_api_common_arguments(api_trading_dates_parser)

    api_refresh_kline_parser = api_subparsers.add_parser("refresh-kline")
    api_refresh_kline_parser.add_argument("--code", action="append", required=True)
    api_refresh_kline_parser.add_argument("--period", required=True)
    _add_api_common_arguments(api_refresh_kline_parser)

    api_download_file_parser = api_subparsers.add_parser("download-file")
    api_download_file_parser.add_argument("--code", required=True)
    api_download_file_parser.add_argument("--down-time", default="")
    api_download_file_parser.add_argument("--down-type", required=True, type=int, choices=[1, 2, 3, 4])
    _add_api_common_arguments(api_download_file_parser)

    api_send_warn_parser = api_subparsers.add_parser("send-warn")
    api_send_warn_parser.add_argument("--code", action="append", required=True)
    api_send_warn_parser.add_argument("--time", action="append", required=True)
    api_send_warn_parser.add_argument("--price", action="append")
    api_send_warn_parser.add_argument("--close", action="append")
    api_send_warn_parser.add_argument("--volume", action="append")
    api_send_warn_parser.add_argument("--bs-flag", action="append")
    api_send_warn_parser.add_argument("--warn-type", action="append")
    api_send_warn_parser.add_argument("--reason", action="append")
    api_send_warn_parser.add_argument("--count", type=int, default=1)
    _add_api_common_arguments(api_send_warn_parser)

    api_user_sectors_parser = api_subparsers.add_parser("user-sectors")
    _add_api_common_arguments(api_user_sectors_parser)

    api_create_sector_parser = api_subparsers.add_parser("create-sector")
    api_create_sector_parser.add_argument("--block-code", required=True)
    api_create_sector_parser.add_argument("--block-name", required=True)
    _add_block_mutation_arguments(api_create_sector_parser)
    _add_api_common_arguments(api_create_sector_parser)

    api_delete_sector_parser = api_subparsers.add_parser("delete-sector")
    api_delete_sector_parser.add_argument("--block-code", required=True)
    _add_block_mutation_arguments(api_delete_sector_parser)
    _add_api_common_arguments(api_delete_sector_parser)

    api_rename_sector_parser = api_subparsers.add_parser("rename-sector")
    api_rename_sector_parser.add_argument("--block-code", required=True)
    api_rename_sector_parser.add_argument("--block-name", required=True)
    _add_block_mutation_arguments(api_rename_sector_parser)
    _add_api_common_arguments(api_rename_sector_parser)

    api_clear_sector_parser = api_subparsers.add_parser("clear-sector")
    api_clear_sector_parser.add_argument("--block-code", required=True)
    _add_block_mutation_arguments(api_clear_sector_parser)
    _add_api_common_arguments(api_clear_sector_parser)

    api_send_user_block_parser = api_subparsers.add_parser("send-user-block")
    api_send_user_block_parser.add_argument("--block-code", required=True)
    api_send_user_block_parser.add_argument("--stock", action="append", default=[])
    api_send_user_block_parser.add_argument("--show", action=argparse.BooleanOptionalAction, default=False)
    _add_block_mutation_arguments(api_send_user_block_parser)
    _add_api_common_arguments(api_send_user_block_parser)

    api_block_read_watchlist_parser = api_subparsers.add_parser("block-read-watchlist")
    api_block_read_watchlist_parser.add_argument("--block-code", required=True)
    _add_api_common_arguments(api_block_read_watchlist_parser)

    api_block_sync_parser = api_subparsers.add_parser("block-sync")
    _add_block_sync_arguments(api_block_sync_parser)
    _add_api_common_arguments(api_block_sync_parser)

    api_formula_capabilities_parser = api_subparsers.add_parser("formula-capabilities")
    _add_api_common_arguments(api_formula_capabilities_parser)

    api_formula_format_data_parser = api_subparsers.add_parser("formula-format-data")
    api_formula_format_data_parser.add_argument("--input-json-file", required=True)
    _add_api_common_arguments(api_formula_format_data_parser)

    api_formula_set_data_parser = api_subparsers.add_parser("formula-set-data")
    api_formula_set_data_parser.add_argument("--code", required=True)
    api_formula_set_data_parser.add_argument("--stock-period", default="1d")
    api_formula_set_data_parser.add_argument("--stock-data-file", required=True)
    api_formula_set_data_parser.add_argument("--count", required=True, type=int)
    api_formula_set_data_parser.add_argument("--dividend-type", default=0, type=int, choices=[0, 1, 2])
    _add_api_common_arguments(api_formula_set_data_parser)

    api_formula_set_data_info_parser = api_subparsers.add_parser("formula-set-data-info")
    api_formula_set_data_info_parser.add_argument("--code", required=True)
    api_formula_set_data_info_parser.add_argument("--stock-period", default="1d")
    api_formula_set_data_info_parser.add_argument("--start-time", default="")
    api_formula_set_data_info_parser.add_argument("--end-time", default="")
    api_formula_set_data_info_parser.add_argument("--count", default=-1, type=int)
    api_formula_set_data_info_parser.add_argument("--dividend-type", default=0, type=int, choices=[0, 1, 2])
    _add_api_common_arguments(api_formula_set_data_info_parser)

    api_formula_get_data_parser = api_subparsers.add_parser("formula-get-data")
    _add_api_common_arguments(api_formula_get_data_parser)

    api_formula_zb_parser = api_subparsers.add_parser("formula-zb")
    api_formula_zb_parser.add_argument("--formula-name", required=True)
    api_formula_zb_parser.add_argument("--formula-arg", default="")
    api_formula_zb_parser.add_argument("--xsflag", default=-1, type=int)
    _add_api_common_arguments(api_formula_zb_parser)

    api_formula_xg_parser = api_subparsers.add_parser("formula-xg")
    api_formula_xg_parser.add_argument("--formula-name", required=True)
    api_formula_xg_parser.add_argument("--formula-arg", default="")
    _add_api_common_arguments(api_formula_xg_parser)

    api_formula_screen_parser = api_subparsers.add_parser("formula-screen")
    api_formula_screen_parser.add_argument("--formula-name", required=True)
    api_formula_screen_parser.add_argument("--formula-arg", default="")
    api_formula_screen_parser.add_argument("--return-count", default=1, type=int)
    api_formula_screen_parser.add_argument("--return-date", action=argparse.BooleanOptionalAction, default=False)
    api_formula_screen_parser.add_argument("--code", action="append", required=True)
    api_formula_screen_parser.add_argument("--stock-period", default="1d")
    api_formula_screen_parser.add_argument("--start-time", default="")
    api_formula_screen_parser.add_argument("--end-time", default="")
    api_formula_screen_parser.add_argument("--count", default=0, type=int)
    api_formula_screen_parser.add_argument("--dividend-type", default=0, type=int, choices=[0, 1, 2])
    _add_api_common_arguments(api_formula_screen_parser)

    api_formula_exp_parser = api_subparsers.add_parser("formula-exp")
    api_formula_exp_parser.add_argument("--formula-name", required=True)
    api_formula_exp_parser.add_argument("--formula-arg", default="")
    _add_api_common_arguments(api_formula_exp_parser)

    api_formula_mul_xg_parser = api_subparsers.add_parser("formula-mul-xg")
    api_formula_mul_xg_parser.add_argument("--formula-name", required=True)
    api_formula_mul_xg_parser.add_argument("--formula-arg", default="")
    api_formula_mul_xg_parser.add_argument("--return-count", default=1, type=int)
    api_formula_mul_xg_parser.add_argument("--return-date", action=argparse.BooleanOptionalAction, default=False)
    api_formula_mul_xg_parser.add_argument("--code", action="append", required=True)
    api_formula_mul_xg_parser.add_argument("--stock-period", default="1d")
    api_formula_mul_xg_parser.add_argument("--start-time", default="")
    api_formula_mul_xg_parser.add_argument("--end-time", default="")
    api_formula_mul_xg_parser.add_argument("--count", default=0, type=int)
    api_formula_mul_xg_parser.add_argument("--dividend-type", default=0, type=int, choices=[0, 1, 2])
    _add_api_common_arguments(api_formula_mul_xg_parser)

    api_formula_mul_zb_parser = api_subparsers.add_parser("formula-mul-zb")
    api_formula_mul_zb_parser.add_argument("--formula-name", required=True)
    api_formula_mul_zb_parser.add_argument("--formula-arg", default="")
    api_formula_mul_zb_parser.add_argument("--xsflag", default=-1, type=int)
    api_formula_mul_zb_parser.add_argument("--return-count", default=1, type=int)
    api_formula_mul_zb_parser.add_argument("--return-date", action=argparse.BooleanOptionalAction, default=False)
    api_formula_mul_zb_parser.add_argument("--code", action="append", required=True)
    api_formula_mul_zb_parser.add_argument("--stock-period", default="1d")
    api_formula_mul_zb_parser.add_argument("--start-time", default="")
    api_formula_mul_zb_parser.add_argument("--end-time", default="")
    api_formula_mul_zb_parser.add_argument("--count", default=0, type=int)
    api_formula_mul_zb_parser.add_argument("--dividend-type", default=0, type=int, choices=[0, 1, 2])
    _add_api_common_arguments(api_formula_mul_zb_parser)

    # --- Group A: send_message, send_file, send_bt_data ---
    api_send_message_parser = api_subparsers.add_parser("send-message")
    api_send_message_parser.add_argument("--msg", required=True)
    _add_api_common_arguments(api_send_message_parser)

    api_send_file_parser = api_subparsers.add_parser("send-file")
    api_send_file_parser.add_argument("--file", required=True)
    _add_api_common_arguments(api_send_file_parser)

    api_send_bt_data_parser = api_subparsers.add_parser("send-bt-data")
    api_send_bt_data_parser.add_argument("--code", required=True)
    api_send_bt_data_parser.add_argument("--time", action="append", required=True)
    api_send_bt_data_parser.add_argument("--data", action="append", required=True)
    api_send_bt_data_parser.add_argument("--count", type=int, default=1)
    _add_api_common_arguments(api_send_bt_data_parser)

    # --- Group B: documented-only functions ---
    api_get_relation_parser = api_subparsers.add_parser("get-relation")
    api_get_relation_parser.add_argument("--code", required=True)
    api_get_relation_parser.add_argument("--relation-type", required=True, type=int)
    _add_api_common_arguments(api_get_relation_parser)

    api_gb_info_by_date_parser = api_subparsers.add_parser("gb-info-by-date")
    api_gb_info_by_date_parser.add_argument("--code", required=True)
    api_gb_info_by_date_parser.add_argument("--date", required=True)
    _add_api_common_arguments(api_gb_info_by_date_parser)

    api_get_pricevol_parser = api_subparsers.add_parser("get-pricevol")
    api_get_pricevol_parser.add_argument("--code", required=True)
    api_get_pricevol_parser.add_argument("--period", default="1d")
    api_get_pricevol_parser.add_argument("--start-time", default="")
    api_get_pricevol_parser.add_argument("--end-time", default="")
    api_get_pricevol_parser.add_argument("--count", type=int, default=-1)
    api_get_pricevol_parser.add_argument("--dividend-type", choices=["none", "front", "back"])
    _add_api_common_arguments(api_get_pricevol_parser)

    api_get_trackzs_etf_info_parser = api_subparsers.add_parser("get-trackzs-etf-info")
    api_get_trackzs_etf_info_parser.add_argument("--code", required=True)
    _add_api_common_arguments(api_get_trackzs_etf_info_parser)

    api_formula_get_all_parser = api_subparsers.add_parser("formula-get-all")
    _add_api_common_arguments(api_formula_get_all_parser)

    api_formula_get_info_parser = api_subparsers.add_parser("formula-get-info")
    api_formula_get_info_parser.add_argument("--formula-name", required=True)
    _add_api_common_arguments(api_formula_get_info_parser)

    api_print_to_tdx_parser = api_subparsers.add_parser("print-to-tdx")
    api_print_to_tdx_parser.add_argument("--input-json-file", required=True)
    api_print_to_tdx_parser.add_argument("--sp-name", default="")
    api_print_to_tdx_parser.add_argument("--xml-filename", default="")
    _add_api_common_arguments(api_print_to_tdx_parser)

    api_exec_to_tdx_parser = api_subparsers.add_parser("exec-to-tdx")
    api_exec_to_tdx_parser.add_argument("--url", required=True)
    _add_api_common_arguments(api_exec_to_tdx_parser)

    # --- Group C: trading domain ---
    api_stock_account_parser = api_subparsers.add_parser("stock-account")
    api_stock_account_parser.add_argument("--account", default="")
    api_stock_account_parser.add_argument("--account-type", default="stock", choices=["stock", "credit", "future", "option"])
    _add_api_common_arguments(api_stock_account_parser)

    api_order_stock_parser = api_subparsers.add_parser("order-stock")
    api_order_stock_parser.add_argument("--account-id", required=True, type=int)
    api_order_stock_parser.add_argument("--code", required=True)
    api_order_stock_parser.add_argument("--order-type", required=True, type=int)
    api_order_stock_parser.add_argument("--order-volume", required=True, type=int)
    api_order_stock_parser.add_argument("--price-type", required=True, type=int, choices=[0, 1, 2, 3])
    api_order_stock_parser.add_argument("--price", required=True, type=float)
    _add_api_common_arguments(api_order_stock_parser)

    api_query_stock_orders_parser = api_subparsers.add_parser("query-stock-orders")
    api_query_stock_orders_parser.add_argument("--account-id", required=True, type=int)
    api_query_stock_orders_parser.add_argument("--code", default="")
    _add_api_common_arguments(api_query_stock_orders_parser)

    api_query_stock_positions_parser = api_subparsers.add_parser("query-stock-positions")
    api_query_stock_positions_parser.add_argument("--account-id", required=True, type=int)
    _add_api_common_arguments(api_query_stock_positions_parser)

    api_cancel_order_stock_parser = api_subparsers.add_parser("cancel-order-stock")
    api_cancel_order_stock_parser.add_argument("--account-id", required=True, type=int)
    api_cancel_order_stock_parser.add_argument("--code", required=True)
    api_cancel_order_stock_parser.add_argument("--order-id", required=True)
    _add_api_common_arguments(api_cancel_order_stock_parser)

    api_query_stock_asset_parser = api_subparsers.add_parser("query-stock-asset")
    api_query_stock_asset_parser.add_argument("--account-id", required=True, type=int)
    _add_api_common_arguments(api_query_stock_asset_parser)

    return api_parser

def handle_api_subcommand(args: argparse.Namespace, *, manager_factory=TdxApiManager) -> Result:
    replay_rejection = _reject_unsupported_api_replay(args)
    if replay_rejection is not None:
        return replay_rejection
    try:
        manager_kwargs: dict[str, object] = {
            "profile": args.profile,
            "strategy_path": args.strategy_path,
        }
        if (
            getattr(args, "provider_mode", "live") != "live"
            or getattr(args, "fixture", None) is not None
            or getattr(args, "fixture_path", None) is not None
        ):
            manager_kwargs.update(
                {
                    "provider_mode": getattr(args, "provider_mode", "live"),
                    "replay_fixture": getattr(args, "fixture", None),
                    "replay_fixture_path": getattr(args, "fixture_path", None),
                }
            )
        manager = manager_factory(**manager_kwargs)
    except ValueError as exc:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))

    if args.api_command == "capabilities":
        return manager.runtime.capabilities()
    if args.api_command == "health":
        return manager.runtime.health(window_key=args.window_key, hid_port=args.hid_port)
    if args.api_command == "doctor":
        return manager.runtime.doctor(window_key=args.window_key, hid_port=args.hid_port)
    if args.api_command == "subscription-subscribe":
        return manager.runtime.subscription_subscribe(stock_list=args.code)
    if args.api_command == "subscription-unsubscribe":
        return manager.runtime.subscription_unsubscribe(stock_list=args.code)
    if args.api_command == "subscription-list":
        return manager.runtime.subscription_list()
    if args.api_command == "snapshot":
        return manager.market.snapshot(args.code, fields=args.field)
    if args.api_command == "market-snapshot":
        return manager.market.market_snapshot(args.code, fields=args.field)
    if args.api_command == "kline":
        return manager.market.kline(
            stock_list=args.code,
            period=args.period,
            start_time=args.start_time,
            end_time=args.end_time,
            count=args.count,
            dividend_type=args.dividend_type,
            fields=args.field,
            fill_data=args.fill_data,
        )
    if args.api_command == "full-tick":
        return manager.market.full_tick(args.code, fields=args.field)
    if args.api_command == "stock-info":
        return manager.market.stock_info(args.code, fields=args.field)
    if args.api_command == "more-info":
        return manager.market.more_info(args.code, fields=args.field)
    if args.api_command == "cb-info":
        return manager.market.cb_info(args.code, fields=args.field)
    if args.api_command == "stock-list":
        return manager.meta.stock_list(market=args.market, list_type=args.list_type)
    if args.api_command == "sector-list":
        return manager.meta.sector_list(list_type=args.list_type)
    if args.api_command == "sector-stocks":
        return manager.meta.sector_stocks(
            block_code=args.sector,
            block_type=args.block_type,
            list_type=args.list_type,
        )
    if args.api_command == "gb-info":
        return manager.meta.gb_info(stock_code=args.code, date_list=args.date, count=args.count)
    if args.api_command == "gp-one":
        return manager.meta.gp_one_data(stock_list=args.code, fields=args.field)
    if args.api_command == "divid-factors":
        return manager.meta.divid_factors(stock_code=args.code, start_time=args.start_time, end_time=args.end_time)
    if args.api_command == "ipo-info":
        return manager.meta.ipo_info(ipo_type=args.ipo_type, ipo_date=args.ipo_date)
    if args.api_command == "financial-data":
        return manager.financial.financial_data(
            stock_list=args.code,
            fields=args.field,
            start_time=args.start_time,
            end_time=args.end_time,
            report_type=args.report_type,
        )
    if args.api_command == "financial-data-by-date":
        return manager.financial.financial_data_by_date(
            stock_list=args.code,
            fields=args.field,
            year=args.year,
            mmdd=args.mmdd,
        )
    if args.api_command == "stock-transaction-data":
        return manager.transaction.stock_transaction_data(
            stock_list=args.code,
            fields=args.field,
            start_time=args.start_time,
            end_time=args.end_time,
        )
    if args.api_command == "stock-transaction-data-by-date":
        return manager.transaction.stock_transaction_data_by_date(
            stock_list=args.code,
            fields=args.field,
            year=args.year,
            mmdd=args.mmdd,
        )
    if args.api_command == "sector-transaction-data":
        return manager.transaction.sector_transaction_data(
            stock_list=args.code,
            fields=args.field,
            start_time=args.start_time,
            end_time=args.end_time,
        )
    if args.api_command == "sector-transaction-data-by-date":
        return manager.transaction.sector_transaction_data_by_date(
            stock_list=args.code,
            fields=args.field,
            year=args.year,
            mmdd=args.mmdd,
        )
    if args.api_command == "market-transaction-data":
        return manager.transaction.market_transaction_data(
            fields=args.field,
            start_time=args.start_time,
            end_time=args.end_time,
        )
    if args.api_command == "market-transaction-data-by-date":
        return manager.transaction.market_transaction_data_by_date(
            fields=args.field,
            year=args.year,
            mmdd=args.mmdd,
        )
    if args.api_command == "refresh-cache":
        return manager.refresh_cache(market=args.market, force=args.force)
    if args.api_command == "trading-dates":
        return manager.runtime.trading_dates(
            market=args.market,
            start_time=args.start_time,
            end_time=args.end_time,
            count=args.count,
        )
    if args.api_command == "refresh-kline":
        return manager.runtime.refresh_kline(stock_list=args.code, period=args.period)
    if args.api_command == "download-file":
        return manager.runtime.download_file(stock_code=args.code, down_time=args.down_time, down_type=args.down_type)
    if args.api_command == "send-warn":
        return manager.runtime.send_warn(
            stock_list=args.code,
            time_list=args.time,
            price_list=args.price or [],
            close_list=args.close or [],
            volume_list=args.volume or [],
            bs_flag_list=args.bs_flag or [],
            warn_type_list=args.warn_type or [],
            reason_list=args.reason or [],
            count=args.count,
        )
    if args.api_command == "user-sectors":
        return manager.block.user_sectors()
    if args.api_command == "create-sector":
        options: dict[str, object] = {}
        if args.mutation_key is not None:
            options["mutation_key"] = args.mutation_key
        if args.audit_dir is not None:
            options["audit_dir"] = args.audit_dir
        return manager.block.create_sector(
            block_code=args.block_code,
            block_name=args.block_name,
            **options,
        )
    if args.api_command == "delete-sector":
        options = {}
        if args.mutation_key is not None:
            options["mutation_key"] = args.mutation_key
        if args.audit_dir is not None:
            options["audit_dir"] = args.audit_dir
        return manager.block.delete_sector(
            block_code=args.block_code,
            **options,
        )
    if args.api_command == "rename-sector":
        options = {}
        if args.mutation_key is not None:
            options["mutation_key"] = args.mutation_key
        if args.audit_dir is not None:
            options["audit_dir"] = args.audit_dir
        return manager.block.rename_sector(
            block_code=args.block_code,
            block_name=args.block_name,
            **options,
        )
    if args.api_command == "clear-sector":
        options = {}
        if args.mutation_key is not None:
            options["mutation_key"] = args.mutation_key
        if args.audit_dir is not None:
            options["audit_dir"] = args.audit_dir
        return manager.block.clear_sector(
            block_code=args.block_code,
            **options,
        )
    if args.api_command == "send-user-block":
        options = {}
        if args.mutation_key is not None:
            options["mutation_key"] = args.mutation_key
        if args.audit_dir is not None:
            options["audit_dir"] = args.audit_dir
        return manager.block.send_user_block(
            block_code=args.block_code,
            stocks=args.stock,
            show=args.show,
            **options,
        )
    if args.api_command == "block-read-watchlist":
        return manager.block.read_watchlist_snapshot(block_code=args.block_code)
    if args.api_command == "block-sync":
        options = {}
        if args.mutation_key is not None:
            options["mutation_key"] = args.mutation_key
        if args.audit_dir is not None:
            options["audit_dir"] = args.audit_dir
        return manager.block.sync_watchlist(
            block_code=args.block_code,
            symbols=args.stock,
            mode=args.mode,
            write_policy=args.write_policy,
            create_if_missing=args.create_if_missing,
            dry_run=args.dry_run,
            show=args.show,
            **options,
        )
    if args.api_command == "formula-capabilities":
        return manager.formula.capabilities()
    if args.api_command == "formula-format-data":
        return manager.formula.format_data(json.loads(Path(args.input_json_file).read_text(encoding="utf-8")))
    if args.api_command == "formula-set-data":
        return manager.formula.set_data(
            stock_code=args.code,
            stock_period=args.stock_period,
            stock_data=json.loads(Path(args.stock_data_file).read_text(encoding="utf-8")),
            count=args.count,
            dividend_type=args.dividend_type,
        )
    if args.api_command == "formula-set-data-info":
        return manager.formula.set_data_info(
            stock_code=args.code,
            stock_period=args.stock_period,
            start_time=args.start_time,
            end_time=args.end_time,
            count=args.count,
            dividend_type=args.dividend_type,
        )
    if args.api_command == "formula-get-data":
        return manager.formula.get_data()
    if args.api_command == "formula-zb":
        return manager.formula.zb(formula_name=args.formula_name, formula_arg=args.formula_arg, xsflag=args.xsflag)
    if args.api_command == "formula-xg":
        return manager.formula.xg(formula_name=args.formula_name, formula_arg=args.formula_arg)
    if args.api_command == "formula-screen":
        return manager.formula.screen(
            formula_name=args.formula_name,
            stock_list=args.code,
            formula_arg=args.formula_arg,
            return_count=args.return_count,
            return_date=args.return_date,
            stock_period=args.stock_period,
            start_time=args.start_time,
            end_time=args.end_time,
            count=args.count,
            dividend_type=args.dividend_type,
        )
    if args.api_command == "formula-exp":
        return manager.formula.exp(formula_name=args.formula_name, formula_arg=args.formula_arg)
    if args.api_command == "formula-mul-xg":
        return manager.formula.process_mul_xg(
            formula_name=args.formula_name,
            formula_arg=args.formula_arg,
            return_count=args.return_count,
            return_date=args.return_date,
            stock_list=args.code,
            stock_period=args.stock_period,
            start_time=args.start_time,
            end_time=args.end_time,
            count=args.count,
            dividend_type=args.dividend_type,
        )
    if args.api_command == "formula-mul-zb":
        return manager.formula.process_mul_zb(
            formula_name=args.formula_name,
            formula_arg=args.formula_arg,
            xsflag=args.xsflag,
            return_count=args.return_count,
            return_date=args.return_date,
            stock_list=args.code,
            stock_period=args.stock_period,
            start_time=args.start_time,
            end_time=args.end_time,
            count=args.count,
            dividend_type=args.dividend_type,
        )
    if args.api_command == "send-message":
        return manager.runtime.send_message(msg_str=args.msg)
    if args.api_command == "send-file":
        return manager.runtime.send_file(file=args.file)
    if args.api_command == "send-bt-data":
        return manager.runtime.send_bt_data(
            stock_code=args.code,
            time_list=args.time,
            data_list=[[v] for v in (args.data or [])],
            count=args.count,
        )
    if args.api_command == "get-relation":
        return manager.meta.get_relation(stock_code=args.code, relation_type=args.relation_type)
    if args.api_command == "gb-info-by-date":
        return manager.meta.gb_info_by_date(stock_code=args.code, date=args.date)
    if args.api_command == "get-pricevol":
        return manager.market.get_pricevol(
            stock_code=args.code,
            period=args.period,
            start_time=args.start_time,
            end_time=args.end_time,
            count=args.count,
            dividend_type=args.dividend_type or "none",
        )
    if args.api_command == "get-trackzs-etf-info":
        return manager.market.get_trackzs_etf_info(stock_code=args.code)
    if args.api_command == "formula-get-all":
        return manager.formula.get_all()
    if args.api_command == "formula-get-info":
        return manager.formula.get_info(formula_name=args.formula_name)
    if args.api_command == "print-to-tdx":
        payload = json.loads(Path(args.input_json_file).read_text(encoding="utf-8"))
        return manager.runtime.print_to_tdx(**payload)
    if args.api_command == "exec-to-tdx":
        return manager.runtime.exec_to_tdx(url=args.url)
    if args.api_command == "stock-account":
        return manager.trade.stock_account(account=args.account, account_type=args.account_type)
    if args.api_command == "order-stock":
        return manager.trade.order_stock(
            account_id=args.account_id,
            stock_code=args.code,
            order_type=args.order_type,
            order_volume=args.order_volume,
            price_type=args.price_type,
            price=args.price,
        )
    if args.api_command == "query-stock-orders":
        return manager.trade.query_stock_orders(account_id=args.account_id, stock_code=args.code)
    if args.api_command == "query-stock-positions":
        return manager.trade.query_stock_positions(account_id=args.account_id)
    if args.api_command == "cancel-order-stock":
        return manager.trade.cancel_order_stock(
            account_id=args.account_id,
            stock_code=args.code,
            order_id=args.order_id,
        )
    if args.api_command == "query-stock-asset":
        return manager.trade.query_stock_asset(account_id=args.account_id)
    return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=f"unsupported api subcommand: {args.api_command}")

__all__ = ["build_api_parser", "handle_api_subcommand"]
