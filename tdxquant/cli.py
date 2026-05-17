from __future__ import annotations

import argparse
import copy
import json
import sys
import time
from decimal import Decimal
from pathlib import Path
from typing import TextIO
from uuid import uuid4

from .brokers import PingAnBrokerAdapter
from .api import TdxApiManager, TdxTaskManager
from .catalog import (
    load_command_bundles,
    load_command_catalog,
    resolve_command_bundle,
    resolve_command_bundle_step_range,
    resolve_command_catalog_entry,
)
from .trade import (
    TRADE_COMMAND_DEFAULT_PROFILES,
    TdxTradeManager,
    build_pingan_last_order_state_payload,
    extract_pingan_contract_no,
    get_pingan_last_order_state_path,
    get_pingan_submission_ledger_path,
    load_trade_presets,
    load_trade_profiles,
    resolve_trade_preset,
    resolve_trade_profile,
    write_pingan_last_order_state,
)
from .trader import OrderSide, OrderStatus, SecurityOrderRequest, TradeService, TraderGatewayRegistry, TraderStore
from .trader.adapters import PingAnDesktopTraderGateway
from .reporting import REPORT_COMMAND_DEFAULT_PROFILES, load_report_presets, resolve_report_preset
from .tasking import TASK_COMMAND_DEFAULT_PROFILES, load_task_presets, resolve_task_preset
from .desktop.hid import build_type_command, normalize_hid_key, run_hid_ping, run_hid_send, validate_hid_wire_command
from .desktop.inspect import enumerate_controls, find_main_window
from .bridge_registry import run_bridge_watch_start, run_bridge_watch_status, run_bridge_watch_stop
from .bridge_http import serve_bridge_from_config
from .models import ErrorCode, OrderRequest, Result
from .result_contract import DEFAULT_CAPABILITY_VERSION, DEFAULT_SCHEMA_VERSION, build_runtime_metadata, format_rfc3339, utc_now
from .api.bridge import (
    run_tdx_bridge_health,
    run_tdx_cb_info,
    run_tdx_clear_sector,
    run_tdx_create_sector,
    run_tdx_data_kline,
    run_tdx_divid_factors,
    run_tdx_financial_data,
    run_tdx_financial_data_by_date,
    run_tdx_market_transaction_data,
    run_tdx_market_transaction_data_by_date,
    run_tdx_sector_transaction_data,
    run_tdx_sector_transaction_data_by_date,
    run_tdx_stock_transaction_data,
    run_tdx_stock_transaction_data_by_date,
    run_tdx_stock_list,
    run_tdx_data_sector_list,
    run_tdx_data_sector_stocks,
    run_tdx_data_snapshot,
    run_tdx_data_stock_info,
    run_tdx_delete_sector,
    run_tdx_gb_info,
    run_tdx_get_user_sector,
    run_tdx_gp_one_data,
    run_tdx_ipo_info,
    run_tdx_market_snapshot,
    run_tdx_more_info,
    run_tdx_provider_capabilities,
    run_tdx_provider_doctor,
    run_tdx_provider_health,
    run_tdx_download_file,
    run_tdx_refresh_cache,
    run_tdx_refresh_kline,
    run_tdx_send_warn,
    run_tdx_rename_sector,
    run_tdx_send_user_block,
    run_tdx_get_trading_dates,
    run_tdx_formula_exp,
    run_tdx_formula_format_data,
    run_tdx_formula_get_data,
    run_tdx_formula_process_mul_xg,
    run_tdx_formula_process_mul_zb,
    run_tdx_formula_screen,
    run_tdx_formula_set_data,
    run_tdx_formula_set_data_info,
    run_tdx_formula_xg,
    run_tdx_formula_zb,
)
from .desktop.uia import (
    activate_uia_element,
    analyze_uia_snapshot,
    click_uia_center,
    click_uia_element,
    click_uia_path,
    inspect_uia_tree,
    inspect_uia_dialogs,
    inspect_uia_windows,
    list_uia_combobox_items,
    read_uia_element,
    run_pingan_hid_submit_probe,
    run_pingan_probe,
    set_uia_text,
    select_uia_combobox_item,
    wait_for_uia_dialog,
)
from .desktop.win32 import (
    IS_WINDOWS,
    click,
    focus_window,
    get_class_name,
    get_control_id,
    get_foreground_window,
    get_gui_thread_focus,
    get_window_exstyle,
    get_window_style,
    get_parent,
    get_rect,
    get_text,
    post_message,
    post_wm_command,
    register_window_message,
    restore_foreground_window,
    send_button_mouse_click,
    send_ctrl_a,
    send_delete_key,
    send_enter,
    send_space,
    send_tab,
    send_wm_command,
    set_text,
    type_text,
    type_text_keybd,
)

PINGAN_LAST_ORDER_STATE_PATH = get_pingan_last_order_state_path()
PINGAN_SUBMISSION_LEDGER_PATH = get_pingan_submission_ledger_path()
TRADER_RUNTIME_DIR = Path(__file__).resolve().parents[1] / "runtime" / "trader"
PINGAN_BUY_PROFILE_NAMES = ("stable", "balanced", "fast", "turbo")
PINGAN_BUY_PROFILES: dict[str, dict[str, object]] = {
    name: dict(resolve_trade_profile(name, profiles=load_trade_profiles()))
    for name in PINGAN_BUY_PROFILE_NAMES
}


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
    subparser.add_argument("--create-if-missing", action=argparse.BooleanOptionalAction, default=False)
    subparser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=False)
    subparser.add_argument("--show", action=argparse.BooleanOptionalAction, default=True)
    _add_block_mutation_arguments(subparser)


def _add_task_common_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--profile", default="default")
    subparser.add_argument("--api-profile")
    subparser.add_argument("--trade-profile")
    subparser.add_argument("--strategy-path")
    subparser.add_argument("--output", help="Optional path to write the JSON result")


def _add_replay_provider_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--provider-mode", choices=("live", "replay"), default="live")
    replay_group = subparser.add_mutually_exclusive_group()
    replay_group.add_argument("--fixture")
    replay_group.add_argument("--fixture-path")


def _add_report_common_arguments(subparser: argparse.ArgumentParser, *, default_profile: str | None = None) -> None:
    if default_profile is None:
        subparser.add_argument("--profile")
    else:
        subparser.add_argument("--profile", default=default_profile)
    subparser.add_argument("--api-profile")
    subparser.add_argument("--strategy-path")
    subparser.add_argument("--output", help="Optional path to write the JSON result")


def _add_trade_common_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--port", required=True)
    subparser.add_argument("--baudrate", type=int, default=115200)
    subparser.add_argument("--timeout", type=float, default=2.0)
    subparser.add_argument("--code", required=True)
    subparser.add_argument("--price", required=True)
    subparser.add_argument("--quantity", required=True, type=int)
    subparser.add_argument("--max-depth", type=int, default=12)
    subparser.add_argument("--close-result-dialog", action=argparse.BooleanOptionalAction, default=True)
    _add_trade_safety_arguments(subparser)


def _add_trade_safety_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--submission-key")
    subparser.add_argument("--max-price", type=float)


def _add_trade_order_place_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--broker", default="pingan_desktop")
    subparser.add_argument("--profile", default="balanced")
    subparser.add_argument("--port", required=True)
    subparser.add_argument("--baudrate", type=int, default=115200)
    subparser.add_argument("--timeout", type=float, default=2.0)
    subparser.add_argument("--market", required=True, choices=["SH", "SZ"])
    subparser.add_argument("--side", required=True, choices=["buy", "sell"])
    subparser.add_argument("--code", required=True)
    subparser.add_argument("--price", required=True)
    subparser.add_argument("--quantity", required=True, type=int)
    subparser.add_argument("--client-order-id")
    subparser.add_argument("--store-dir")
    subparser.add_argument("--max-depth", type=int, default=12)
    subparser.add_argument("--close-result-dialog", action=argparse.BooleanOptionalAction, default=True)
    _add_trade_safety_arguments(subparser)


def _add_trade_order_query_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--gateway-order-id", required=True)
    subparser.add_argument("--store-dir")


def _add_trade_trade_query_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--store-dir")


def _add_trade_buy_profile_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--profile", choices=["stable", "balanced", "fast", "turbo"], default="balanced")
    subparser.add_argument(
        "--price-quantity-input-mode",
        choices=["uia", "win32", "hybrid_win32"],
        help="How price/quantity edits are written in the fast path. Code input always stays on UIA.",
    )
    subparser.add_argument(
        "--dialog-lookup-mode",
        choices=["uia", "win32_experimental"],
        help="How confirm/result dialogs are found. The experimental mode is opt-in and falls back to UIA on failure.",
    )
    subparser.add_argument("--capture-final-uia", action=argparse.BooleanOptionalAction)
    subparser.add_argument("--hid-pre-delay", type=float)
    subparser.add_argument("--post-delay", type=float)
    subparser.add_argument("--dialog-timeout", type=float)
    subparser.add_argument("--confirm-timeout", type=float)
    subparser.add_argument("--confirm-post-delay", type=float)
    subparser.add_argument("--result-timeout", type=float)
    subparser.add_argument("--result-close-pre-delay", type=float)


def _add_trade_submit_once_profile_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--hid-pre-delay", type=float, default=0.0)
    subparser.add_argument("--post-delay", type=float, default=1.0)
    subparser.add_argument("--dialog-timeout", type=float, default=2.5)
    subparser.add_argument("--confirm-timeout", type=float, default=3.0)
    subparser.add_argument("--confirm-post-delay", type=float, default=1.0)
    subparser.add_argument("--result-timeout", type=float, default=3.0)
    subparser.add_argument("--result-close-pre-delay", type=float, default=0.0)
    subparser.add_argument("--capture-final-uia", action=argparse.BooleanOptionalAction, default=True)


def _add_trade_run_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--profile")
    subparser.add_argument("--port")
    subparser.add_argument("--baudrate", type=int)
    subparser.add_argument("--timeout", type=float)
    subparser.add_argument("--code")
    subparser.add_argument("--price")
    subparser.add_argument("--quantity", type=int)
    subparser.add_argument("--max-depth", type=int)
    subparser.add_argument("--close-result-dialog", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--price-quantity-input-mode", choices=["uia", "win32", "hybrid_win32"])
    subparser.add_argument("--dialog-lookup-mode", choices=["uia", "win32_experimental"])
    subparser.add_argument("--capture-final-uia", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--hid-pre-delay", type=float)
    subparser.add_argument("--post-delay", type=float)
    subparser.add_argument("--dialog-timeout", type=float)
    subparser.add_argument("--confirm-timeout", type=float)
    subparser.add_argument("--confirm-post-delay", type=float)
    subparser.add_argument("--result-timeout", type=float)
    subparser.add_argument("--result-close-pre-delay", type=float)
    _add_trade_safety_arguments(subparser)


def _add_trade_health_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--profile", default="balanced")
    subparser.add_argument("--port")
    subparser.add_argument("--baudrate", type=int, default=115200)
    subparser.add_argument("--timeout", type=float, default=2.0)
    subparser.add_argument("--pre-delay", type=float, default=0.0)


def _add_trade_preflight_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--profile", default="balanced")
    subparser.add_argument("--port", required=True)
    subparser.add_argument("--baudrate", type=int, default=115200)
    subparser.add_argument("--timeout", type=float, default=2.0)
    subparser.add_argument("--pre-delay", type=float, default=0.0)
    subparser.add_argument("--code", required=True)
    subparser.add_argument("--price", required=True)
    subparser.add_argument("--quantity", required=True, type=int)
    _add_trade_safety_arguments(subparser)


def _add_trade_submit_ready_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--profile", default="balanced")
    subparser.add_argument("--port", required=True)
    subparser.add_argument("--baudrate", type=int, default=115200)
    subparser.add_argument("--timeout", type=float, default=2.0)
    subparser.add_argument("--code", required=True)
    subparser.add_argument("--price", required=True)
    subparser.add_argument("--quantity", required=True, type=int)
    subparser.add_argument("--max-depth", type=int, default=12)
    subparser.add_argument("--max-price", type=float)
    subparser.add_argument("--dialog-lookup-mode", choices=["uia", "win32_experimental"])
    subparser.add_argument("--confirm-timeout", type=float)


def _add_trade_confirm_current_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--profile", default="balanced")
    subparser.add_argument("--dialog-lookup-mode", choices=["uia", "win32_experimental"])
    subparser.add_argument("--confirm-timeout", type=float)
    subparser.add_argument("--result-timeout", type=float)
    subparser.add_argument("--close-result-dialog", action=argparse.BooleanOptionalAction, default=True)
    subparser.add_argument("--result-close-pre-delay", type=float)


def _add_trade_dialog_readiness_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--profile", default="balanced")
    subparser.add_argument("--dialog", choices=["confirm", "result", "both"], default="both")
    subparser.add_argument("--require-visible", action=argparse.BooleanOptionalAction, default=False)
    subparser.add_argument("--dialog-lookup-mode", choices=["uia", "win32_experimental"])
    subparser.add_argument("--confirm-timeout", type=float)
    subparser.add_argument("--result-timeout", type=float)


def _add_task_trade_submit_ready_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--port", required=True)
    subparser.add_argument("--baudrate", type=int, default=115200)
    subparser.add_argument("--timeout", type=float, default=2.0)
    subparser.add_argument("--code", required=True)
    subparser.add_argument("--price", required=True)
    subparser.add_argument("--quantity", required=True, type=int)
    subparser.add_argument("--max-depth", type=int, default=12)
    subparser.add_argument("--max-price", type=float)
    subparser.add_argument("--dialog-lookup-mode", choices=["uia", "win32_experimental"])
    subparser.add_argument("--confirm-timeout", type=float)
    subparser.add_argument("--refresh-before-trade", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--refresh-market")
    subparser.add_argument("--refresh-force", action=argparse.BooleanOptionalAction, default=None)


def _add_task_trade_confirm_current_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--dialog-lookup-mode", choices=["uia", "win32_experimental"])
    subparser.add_argument("--confirm-timeout", type=float)
    subparser.add_argument("--result-timeout", type=float)
    subparser.add_argument("--close-result-dialog", action=argparse.BooleanOptionalAction, default=True)
    subparser.add_argument("--result-close-pre-delay", type=float)


def _add_task_run_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--profile")
    subparser.add_argument("--api-profile")
    subparser.add_argument("--trade-profile")
    subparser.add_argument("--strategy-path")
    subparser.add_argument("--block-code")
    subparser.add_argument("--port")
    subparser.add_argument("--baudrate", type=int)
    subparser.add_argument("--timeout", type=float)
    subparser.add_argument("--code")
    subparser.add_argument("--price")
    subparser.add_argument("--quantity", type=int)
    subparser.add_argument("--max-depth", type=int)
    subparser.add_argument("--close-result-dialog", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--dialog-lookup-mode", choices=["uia", "win32_experimental"])
    subparser.add_argument("--confirm-timeout", type=float)
    subparser.add_argument("--result-timeout", type=float)
    subparser.add_argument("--result-close-pre-delay", type=float)
    _add_trade_safety_arguments(subparser)
    subparser.add_argument("--refresh-before-trade", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--refresh-market")
    subparser.add_argument("--refresh-force", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--market")
    subparser.add_argument("--force", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--max-snapshot-price", type=float)
    subparser.add_argument("--required-block-code")
    subparser.add_argument("--required-block-type", type=int)
    subparser.add_argument("--required-list-type", type=int)
    subparser.add_argument("--formula-name")
    subparser.add_argument("--formula-arg")
    subparser.add_argument("--formula-return-count", type=int)
    subparser.add_argument("--formula-return-date", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--formula-stock-period")
    subparser.add_argument("--formula-start-time")
    subparser.add_argument("--formula-end-time")
    subparser.add_argument("--formula-count", type=int)
    subparser.add_argument("--formula-dividend-type", type=int)
    subparser.add_argument("--json-output-path")
    subparser.add_argument("--csv-output-path")
    subparser.add_argument("--export-output")
    subparser.add_argument("--overwrite", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--output", help="Optional path to write the JSON result")


def _add_ledger_summary_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--limit", type=int)
    subparser.add_argument("--code")
    subparser.add_argument("--contract-no")
    subparser.add_argument("--trade-ok", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--task-name")
    subparser.add_argument("--ledger-jsonl-path")
    subparser.add_argument("--ledger-csv-path")
    subparser.add_argument("--json-output-path")
    subparser.add_argument("--csv-output-path")


def _add_daily_trade_report_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--date")
    subparser.add_argument("--timezone")
    subparser.add_argument("--recent-limit", type=int)
    subparser.add_argument("--code")
    subparser.add_argument("--trade-ok", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--task-name")
    subparser.add_argument("--ledger-jsonl-path")
    subparser.add_argument("--ledger-csv-path")
    subparser.add_argument("--json-output-path")
    subparser.add_argument("--csv-output-path")


def _add_trade_report_lookup_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--contract-no")
    subparser.add_argument("--code")
    subparser.add_argument("--date")
    subparser.add_argument("--timezone")
    subparser.add_argument("--limit", type=int)
    subparser.add_argument("--trade-ok", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--task-name")
    subparser.add_argument("--ledger-jsonl-path")
    subparser.add_argument("--ledger-csv-path")
    subparser.add_argument("--json-output-path")
    subparser.add_argument("--csv-output-path")


def _add_trade_audit_lookup_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--audit-id")
    subparser.add_argument("--contract-no")
    subparser.add_argument("--submission-key")
    subparser.add_argument("--code")
    subparser.add_argument("--status")
    subparser.add_argument("--limit", type=int)
    subparser.add_argument("--audit-dir")
    subparser.add_argument("--json-output-path")
    subparser.add_argument("--csv-output-path")


def _add_trade_audit_daily_report_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--date")
    subparser.add_argument("--timezone")
    subparser.add_argument("--recent-limit", type=int)
    subparser.add_argument("--code")
    subparser.add_argument("--status")
    subparser.add_argument("--status-any", dest="statuses", action="append")
    subparser.add_argument("--method")
    subparser.add_argument("--method-any", dest="methods", action="append")
    subparser.add_argument("--broker")
    subparser.add_argument("--submission-key")
    subparser.add_argument("--audit-dir")
    subparser.add_argument("--json-output-path")
    subparser.add_argument("--csv-output-path")


def _add_trade_audit_period_report_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--start-date")
    subparser.add_argument("--end-date")
    subparser.add_argument("--timezone")
    subparser.add_argument("--recent-limit", type=int)
    subparser.add_argument("--code")
    subparser.add_argument("--status")
    subparser.add_argument("--status-any", dest="statuses", action="append")
    subparser.add_argument("--method")
    subparser.add_argument("--method-any", dest="methods", action="append")
    subparser.add_argument("--broker")
    subparser.add_argument("--submission-key")
    subparser.add_argument("--audit-dir")
    subparser.add_argument("--json-output-path")
    subparser.add_argument("--csv-output-path")


def _add_trade_audit_cross_ledger_query_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--audit-id")
    subparser.add_argument("--contract-no")
    subparser.add_argument("--submission-key")
    subparser.add_argument("--code")
    subparser.add_argument("--status")
    subparser.add_argument("--limit", type=int)
    subparser.add_argument("--audit-dir")
    subparser.add_argument("--submission-ledger-path")
    subparser.add_argument("--task-ledger-jsonl-path")
    subparser.add_argument("--task-ledger-csv-path")
    subparser.add_argument("--cache-output-path")
    subparser.add_argument("--json-output-path")
    subparser.add_argument("--csv-output-path")


def _add_trade_period_report_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--start-date")
    subparser.add_argument("--end-date")
    subparser.add_argument("--timezone")
    subparser.add_argument("--recent-limit", type=int)
    subparser.add_argument("--code")
    subparser.add_argument("--trade-ok", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--task-name")
    subparser.add_argument("--ledger-jsonl-path")
    subparser.add_argument("--ledger-csv-path")
    subparser.add_argument("--json-output-path")
    subparser.add_argument("--csv-output-path")


def _add_catalog_run_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--view", choices=["detailed", "summary"], default="detailed")
    subparser.add_argument("--from-step")
    subparser.add_argument("--to-step")
    subparser.add_argument("--only-step")
    subparser.add_argument("--profile")
    subparser.add_argument("--api-profile")
    subparser.add_argument("--trade-profile")
    subparser.add_argument("--strategy-path")
    subparser.add_argument("--port")
    subparser.add_argument("--baudrate", type=int)
    subparser.add_argument("--timeout", type=float)
    subparser.add_argument("--block-code")
    subparser.add_argument("--code")
    subparser.add_argument("--price")
    subparser.add_argument("--quantity", type=int)
    subparser.add_argument("--max-depth", type=int)
    subparser.add_argument("--close-result-dialog", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--price-quantity-input-mode", choices=["uia", "win32", "hybrid_win32"])
    subparser.add_argument("--dialog-lookup-mode", choices=["uia", "win32_experimental"])
    subparser.add_argument("--capture-final-uia", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--hid-pre-delay", type=float)
    subparser.add_argument("--post-delay", type=float)
    subparser.add_argument("--dialog-timeout", type=float)
    subparser.add_argument("--confirm-timeout", type=float)
    subparser.add_argument("--confirm-post-delay", type=float)
    subparser.add_argument("--result-timeout", type=float)
    subparser.add_argument("--result-close-pre-delay", type=float)
    subparser.add_argument("--refresh-before-trade", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--refresh-market")
    subparser.add_argument("--refresh-force", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--market")
    subparser.add_argument("--force", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--max-snapshot-price", type=float)
    subparser.add_argument("--required-block-code")
    subparser.add_argument("--required-block-type", type=int)
    subparser.add_argument("--required-list-type", type=int)
    subparser.add_argument("--formula-name")
    subparser.add_argument("--formula-arg")
    subparser.add_argument("--formula-return-count", type=int)
    subparser.add_argument("--formula-return-date", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--formula-stock-period")
    subparser.add_argument("--formula-start-time")
    subparser.add_argument("--formula-end-time")
    subparser.add_argument("--formula-count", type=int)
    subparser.add_argument("--formula-dividend-type", type=int)
    subparser.add_argument("--limit", type=int)
    subparser.add_argument("--contract-no")
    subparser.add_argument("--date")
    subparser.add_argument("--timezone")
    subparser.add_argument("--recent-limit", type=int)
    subparser.add_argument("--start-date")
    subparser.add_argument("--end-date")
    subparser.add_argument("--trade-ok", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--task-name")
    subparser.add_argument("--ledger-jsonl-path")
    subparser.add_argument("--ledger-csv-path")
    subparser.add_argument("--json-output-path")
    subparser.add_argument("--csv-output-path")
    subparser.add_argument("--output", help="Optional path to write the JSON result")


def _build_catalog_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> argparse.ArgumentParser:
    catalog_parser = subparsers.add_parser("catalog")
    catalog_subparsers = catalog_parser.add_subparsers(dest="catalog_command", required=True)

    catalog_list_parser = catalog_subparsers.add_parser("list")
    catalog_list_parser.add_argument("--view", choices=["detailed", "summary"], default="detailed")
    catalog_list_parser.add_argument("--kind", choices=["entry", "bundle", "all"], default="entry")
    catalog_list_filter_group = catalog_list_parser.add_mutually_exclusive_group()
    catalog_list_filter_group.add_argument("--entry")
    catalog_list_filter_group.add_argument("--bundle")
    catalog_list_parser.add_argument("--label")
    catalog_list_parser.add_argument("--output", help="Optional path to write the JSON result")

    catalog_run_parser = catalog_subparsers.add_parser("run")
    catalog_run_filter_group = catalog_run_parser.add_mutually_exclusive_group(required=True)
    catalog_run_filter_group.add_argument("--entry")
    catalog_run_filter_group.add_argument("--bundle")
    _add_catalog_run_arguments(catalog_run_parser)

    catalog_plan_parser = catalog_subparsers.add_parser("plan")
    catalog_plan_filter_group = catalog_plan_parser.add_mutually_exclusive_group(required=True)
    catalog_plan_filter_group.add_argument("--entry")
    catalog_plan_filter_group.add_argument("--bundle")
    _add_catalog_run_arguments(catalog_plan_parser)

    catalog_preview_parser = catalog_subparsers.add_parser("preview")
    catalog_preview_filter_group = catalog_preview_parser.add_mutually_exclusive_group(required=True)
    catalog_preview_filter_group.add_argument("--entry")
    catalog_preview_filter_group.add_argument("--bundle")
    _add_catalog_run_arguments(catalog_preview_parser)

    return catalog_parser


def _build_bridge_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> argparse.ArgumentParser:
    bridge_parser = subparsers.add_parser("bridge")
    bridge_subparsers = bridge_parser.add_subparsers(dest="bridge_command", required=True)

    bridge_serve_parser = bridge_subparsers.add_parser("serve")
    bridge_serve_parser.add_argument("--config", required=True)

    bridge_watch_status_parser = bridge_subparsers.add_parser("watch-status")
    bridge_watch_status_parser.add_argument("--registry", required=True)
    bridge_watch_status_parser.add_argument("--worker", required=True)

    bridge_watch_start_parser = bridge_subparsers.add_parser("watch-start")
    bridge_watch_start_parser.add_argument("--registry", required=True)
    bridge_watch_start_parser.add_argument("--worker", required=True)
    bridge_watch_start_parser.add_argument("--code", action="append", required=True)
    bridge_watch_start_parser.add_argument("--max-events", type=int)
    bridge_watch_start_parser.add_argument("--max-seconds", type=float)
    bridge_watch_start_parser.add_argument("--poll-interval", type=float)
    bridge_watch_start_parser.add_argument("--idempotency-key")

    bridge_watch_stop_parser = bridge_subparsers.add_parser("watch-stop")
    bridge_watch_stop_parser.add_argument("--registry", required=True)
    bridge_watch_stop_parser.add_argument("--worker", required=True)

    return bridge_parser


def _add_report_run_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--date")
    subparser.add_argument("--start-date")
    subparser.add_argument("--end-date")
    subparser.add_argument("--timezone")
    subparser.add_argument("--recent-limit", type=int)
    subparser.add_argument("--limit", type=int)
    subparser.add_argument("--code")
    subparser.add_argument("--contract-no")
    subparser.add_argument("--status")
    subparser.add_argument("--status-any", dest="statuses", action="append")
    subparser.add_argument("--method")
    subparser.add_argument("--method-any", dest="methods", action="append")
    subparser.add_argument("--broker")
    subparser.add_argument("--submission-key")
    subparser.add_argument("--audit-dir")
    subparser.add_argument("--trade-ok", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--task-name")
    subparser.add_argument("--ledger-jsonl-path")
    subparser.add_argument("--ledger-csv-path")
    subparser.add_argument("--json-output-path")
    subparser.add_argument("--csv-output-path")


def _build_api_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> argparse.ArgumentParser:
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

    return api_parser


def _build_task_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> argparse.ArgumentParser:
    task_parser = subparsers.add_parser("task")
    task_subparsers = task_parser.add_subparsers(dest="task_command", required=True)

    task_sector_research_parser = task_subparsers.add_parser("sector-research")
    task_sector_research_parser.add_argument("--sector", required=True)
    task_sector_research_parser.add_argument("--block-type", type=int, default=0, choices=[0, 1])
    task_sector_research_parser.add_argument("--list-type", type=int, choices=[0, 1])
    task_sector_research_parser.add_argument("--field", action="append", default=None)
    _add_task_common_arguments(task_sector_research_parser)

    task_formula_scan_parser = task_subparsers.add_parser("formula-scan")
    task_formula_scan_parser.add_argument("--formula-name", required=True)
    task_formula_scan_parser.add_argument("--formula-arg", default="")
    task_formula_scan_parser.add_argument("--return-count", default=1, type=int)
    task_formula_scan_parser.add_argument("--return-date", action=argparse.BooleanOptionalAction, default=False)
    task_formula_scan_parser.add_argument("--code", action="append", required=True)
    task_formula_scan_parser.add_argument("--stock-period", default="1d")
    task_formula_scan_parser.add_argument("--start-time", default="")
    task_formula_scan_parser.add_argument("--end-time", default="")
    task_formula_scan_parser.add_argument("--count", default=0, type=int)
    task_formula_scan_parser.add_argument("--dividend-type", default=0, type=int, choices=[0, 1, 2])
    _add_task_common_arguments(task_formula_scan_parser)

    task_watchlist_overview_parser = task_subparsers.add_parser("watchlist-overview")
    task_watchlist_overview_parser.add_argument("--code", action="append", required=True)
    task_watchlist_overview_parser.add_argument("--field", action="append", default=None)
    _add_task_common_arguments(task_watchlist_overview_parser)

    task_block_sync_parser = task_subparsers.add_parser("block-sync")
    _add_block_sync_arguments(task_block_sync_parser)
    _add_task_common_arguments(task_block_sync_parser)

    task_block_read_watchlist_parser = task_subparsers.add_parser("block-read-watchlist")
    task_block_read_watchlist_parser.add_argument("--block-code", required=True)
    _add_task_common_arguments(task_block_read_watchlist_parser)

    task_block_read_full_parser = task_subparsers.add_parser("block-read-full")
    task_block_read_full_parser.add_argument("--block-code", required=True)
    _add_task_common_arguments(task_block_read_full_parser)

    task_block_read_watchlist_export_parser = task_subparsers.add_parser("block-read-watchlist-export")
    task_block_read_watchlist_export_parser.add_argument("--block-code", required=True)
    task_block_read_watchlist_export_parser.add_argument("--output", dest="export_output", required=True)
    task_block_read_watchlist_export_parser.add_argument("--overwrite", action="store_true", default=False)
    task_block_read_watchlist_export_parser.add_argument("--profile", default="default")
    task_block_read_watchlist_export_parser.add_argument("--api-profile")
    task_block_read_watchlist_export_parser.add_argument("--trade-profile")
    task_block_read_watchlist_export_parser.add_argument("--strategy-path")

    task_watchlist_export_parser = task_subparsers.add_parser("watchlist-export")
    task_watchlist_export_parser.add_argument("--code", action="append", required=True)
    task_watchlist_export_parser.add_argument("--field", action="append", default=None)
    task_watchlist_export_parser.add_argument("--json-output-path")
    task_watchlist_export_parser.add_argument("--csv-output-path")
    _add_task_common_arguments(task_watchlist_export_parser)

    task_subscription_watch_parser = task_subparsers.add_parser("subscription-watch")
    task_subscription_watch_parser.add_argument("--code", action="append", required=True)
    task_subscription_watch_parser.add_argument("--max-events", type=int)
    task_subscription_watch_parser.add_argument("--max-seconds", type=float)
    task_subscription_watch_parser.add_argument("--poll-interval", type=float, default=None)
    task_subscription_watch_parser.add_argument("--jsonl-output-path")
    task_subscription_watch_parser.add_argument("--csv-output-path")
    task_subscription_watch_parser.add_argument("--status-output-path")
    _add_replay_provider_arguments(task_subscription_watch_parser)
    _add_task_common_arguments(task_subscription_watch_parser)

    task_ledger_summary_parser = task_subparsers.add_parser("ledger-summary")
    _add_ledger_summary_arguments(task_ledger_summary_parser)
    _add_task_common_arguments(task_ledger_summary_parser)

    task_daily_trade_report_parser = task_subparsers.add_parser("daily-trade-report")
    _add_daily_trade_report_arguments(task_daily_trade_report_parser)
    _add_task_common_arguments(task_daily_trade_report_parser)

    task_trade_report_lookup_parser = task_subparsers.add_parser("trade-report-lookup")
    _add_trade_report_lookup_arguments(task_trade_report_lookup_parser)
    _add_task_common_arguments(task_trade_report_lookup_parser)

    task_trade_audit_lookup_parser = task_subparsers.add_parser("trade-audit-lookup")
    _add_trade_audit_lookup_arguments(task_trade_audit_lookup_parser)
    _add_task_common_arguments(task_trade_audit_lookup_parser)

    task_trade_audit_daily_report_parser = task_subparsers.add_parser("trade-audit-daily-report")
    _add_trade_audit_daily_report_arguments(task_trade_audit_daily_report_parser)
    _add_task_common_arguments(task_trade_audit_daily_report_parser)

    task_trade_audit_period_report_parser = task_subparsers.add_parser("trade-audit-period-report")
    _add_trade_audit_period_report_arguments(task_trade_audit_period_report_parser)
    _add_task_common_arguments(task_trade_audit_period_report_parser)

    task_trade_audit_cross_ledger_query_parser = task_subparsers.add_parser("trade-audit-cross-ledger-query")
    _add_trade_audit_cross_ledger_query_arguments(task_trade_audit_cross_ledger_query_parser)
    _add_task_common_arguments(task_trade_audit_cross_ledger_query_parser)

    task_trade_period_report_parser = task_subparsers.add_parser("trade-period-report")
    _add_trade_period_report_arguments(task_trade_period_report_parser)
    _add_task_common_arguments(task_trade_period_report_parser)

    task_sector_formula_scan_parser = task_subparsers.add_parser("sector-formula-scan")
    task_sector_formula_scan_parser.add_argument("--sector", required=True)
    task_sector_formula_scan_parser.add_argument("--formula-name", required=True)
    task_sector_formula_scan_parser.add_argument("--block-type", type=int, default=0, choices=[0, 1])
    task_sector_formula_scan_parser.add_argument("--list-type", type=int, choices=[0, 1])
    task_sector_formula_scan_parser.add_argument("--formula-arg", default="")
    task_sector_formula_scan_parser.add_argument("--return-count", default=1, type=int)
    task_sector_formula_scan_parser.add_argument("--return-date", action=argparse.BooleanOptionalAction, default=False)
    task_sector_formula_scan_parser.add_argument("--stock-period", default="1d")
    task_sector_formula_scan_parser.add_argument("--start-time", default="")
    task_sector_formula_scan_parser.add_argument("--end-time", default="")
    task_sector_formula_scan_parser.add_argument("--count", default=0, type=int)
    task_sector_formula_scan_parser.add_argument("--dividend-type", default=0, type=int, choices=[0, 1, 2])
    _add_task_common_arguments(task_sector_formula_scan_parser)

    task_sector_research_export_parser = task_subparsers.add_parser("sector-research-export")
    task_sector_research_export_parser.add_argument("--sector", required=True)
    task_sector_research_export_parser.add_argument("--block-type", type=int, default=0, choices=[0, 1])
    task_sector_research_export_parser.add_argument("--list-type", type=int, choices=[0, 1])
    task_sector_research_export_parser.add_argument("--field", action="append", default=None)
    task_sector_research_export_parser.add_argument("--json-output-path")
    task_sector_research_export_parser.add_argument("--csv-output-path")
    _add_task_common_arguments(task_sector_research_export_parser)

    task_refresh_environment_parser = task_subparsers.add_parser("refresh-environment")
    task_refresh_environment_parser.add_argument("--market")
    task_refresh_environment_parser.add_argument("--force", action=argparse.BooleanOptionalAction, default=None)
    _add_task_common_arguments(task_refresh_environment_parser)

    task_trade_buy_parser = task_subparsers.add_parser("trade-buy")
    _add_trade_common_arguments(task_trade_buy_parser)
    task_trade_buy_parser.add_argument("--refresh-before-trade", action=argparse.BooleanOptionalAction, default=None)
    task_trade_buy_parser.add_argument("--refresh-market")
    task_trade_buy_parser.add_argument("--refresh-force", action=argparse.BooleanOptionalAction, default=None)
    _add_task_common_arguments(task_trade_buy_parser)

    task_trade_submit_once_parser = task_subparsers.add_parser("trade-submit-once")
    _add_trade_common_arguments(task_trade_submit_once_parser)
    task_trade_submit_once_parser.add_argument("--refresh-before-trade", action=argparse.BooleanOptionalAction, default=None)
    task_trade_submit_once_parser.add_argument("--refresh-market")
    task_trade_submit_once_parser.add_argument("--refresh-force", action=argparse.BooleanOptionalAction, default=None)
    _add_task_common_arguments(task_trade_submit_once_parser)

    task_trade_submit_ready_parser = task_subparsers.add_parser("trade-submit-ready")
    _add_task_trade_submit_ready_arguments(task_trade_submit_ready_parser)
    _add_task_common_arguments(task_trade_submit_ready_parser)

    task_trade_confirm_current_parser = task_subparsers.add_parser("trade-confirm-current")
    _add_task_trade_confirm_current_arguments(task_trade_confirm_current_parser)
    _add_task_common_arguments(task_trade_confirm_current_parser)

    task_guarded_trade_buy_parser = task_subparsers.add_parser("guarded-trade-buy")
    _add_trade_common_arguments(task_guarded_trade_buy_parser)
    task_guarded_trade_buy_parser.add_argument("--refresh-before-trade", action=argparse.BooleanOptionalAction, default=None)
    task_guarded_trade_buy_parser.add_argument("--refresh-market")
    task_guarded_trade_buy_parser.add_argument("--refresh-force", action=argparse.BooleanOptionalAction, default=None)
    task_guarded_trade_buy_parser.add_argument("--max-snapshot-price", type=float)
    task_guarded_trade_buy_parser.add_argument("--required-block-code")
    task_guarded_trade_buy_parser.add_argument("--required-block-type", type=int, default=0, choices=[0, 1])
    task_guarded_trade_buy_parser.add_argument("--required-list-type", type=int, choices=[0, 1])
    task_guarded_trade_buy_parser.add_argument("--formula-name")
    task_guarded_trade_buy_parser.add_argument("--formula-arg", default="")
    task_guarded_trade_buy_parser.add_argument("--formula-return-count", default=1, type=int)
    task_guarded_trade_buy_parser.add_argument("--formula-return-date", action=argparse.BooleanOptionalAction, default=False)
    task_guarded_trade_buy_parser.add_argument("--formula-stock-period", default="1d")
    task_guarded_trade_buy_parser.add_argument("--formula-start-time", default="")
    task_guarded_trade_buy_parser.add_argument("--formula-end-time", default="")
    task_guarded_trade_buy_parser.add_argument("--formula-count", default=0, type=int)
    task_guarded_trade_buy_parser.add_argument("--formula-dividend-type", default=0, type=int, choices=[0, 1, 2])
    task_guarded_trade_buy_parser.add_argument("--json-output-path")
    task_guarded_trade_buy_parser.add_argument("--csv-output-path")
    _add_task_common_arguments(task_guarded_trade_buy_parser)

    task_presets_parser = task_subparsers.add_parser("presets")
    task_presets_parser.add_argument("--preset")
    task_presets_parser.add_argument("--output", help="Optional path to write the JSON result")

    task_run_parser = task_subparsers.add_parser("run")
    task_run_parser.add_argument("--preset", required=True)
    _add_task_run_arguments(task_run_parser)

    return task_parser


def _build_report_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> argparse.ArgumentParser:
    report_parser = subparsers.add_parser("report")
    report_subparsers = report_parser.add_subparsers(dest="report_command", required=True)

    report_ledger_parser = report_subparsers.add_parser("ledger")
    _add_ledger_summary_arguments(report_ledger_parser)
    _add_report_common_arguments(report_ledger_parser, default_profile="ledger_summary")

    report_daily_parser = report_subparsers.add_parser("daily")
    _add_daily_trade_report_arguments(report_daily_parser)
    _add_report_common_arguments(report_daily_parser, default_profile="daily_trade_report")

    report_lookup_parser = report_subparsers.add_parser("lookup")
    _add_trade_report_lookup_arguments(report_lookup_parser)
    _add_report_common_arguments(report_lookup_parser, default_profile="trade_report_lookup")

    report_audit_lookup_parser = report_subparsers.add_parser("audit-lookup")
    _add_trade_audit_lookup_arguments(report_audit_lookup_parser)
    _add_report_common_arguments(report_audit_lookup_parser, default_profile="trade_audit_lookup")

    report_audit_daily_parser = report_subparsers.add_parser("audit-daily")
    _add_trade_audit_daily_report_arguments(report_audit_daily_parser)
    _add_report_common_arguments(report_audit_daily_parser, default_profile="trade_audit_daily_report")

    report_audit_period_parser = report_subparsers.add_parser("audit-period")
    _add_trade_audit_period_report_arguments(report_audit_period_parser)
    _add_report_common_arguments(report_audit_period_parser, default_profile="trade_audit_period_report")

    report_period_parser = report_subparsers.add_parser("period")
    _add_trade_period_report_arguments(report_period_parser)
    _add_report_common_arguments(report_period_parser, default_profile="trade_period_report")

    report_presets_parser = report_subparsers.add_parser("presets")
    report_presets_parser.add_argument("--preset")
    _add_report_common_arguments(report_presets_parser)

    report_run_parser = report_subparsers.add_parser("run")
    report_run_parser.add_argument("--preset", required=True)
    _add_report_run_arguments(report_run_parser)
    _add_report_common_arguments(report_run_parser)

    return report_parser


def _build_trade_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> argparse.ArgumentParser:
    trade_parser = subparsers.add_parser("trade")
    trade_subparsers = trade_parser.add_subparsers(dest="trade_command", required=True)

    trade_order_place_parser = trade_subparsers.add_parser("order-place")
    _add_trade_order_place_arguments(trade_order_place_parser)
    trade_order_place_parser.add_argument("--output", help="Optional path to write the JSON result")

    trade_order_query_parser = trade_subparsers.add_parser("order-query")
    _add_trade_order_query_arguments(trade_order_query_parser)
    trade_order_query_parser.add_argument("--output", help="Optional path to write the JSON result")

    trade_trade_query_parser = trade_subparsers.add_parser("trade-query")
    _add_trade_trade_query_arguments(trade_trade_query_parser)
    trade_trade_query_parser.add_argument("--output", help="Optional path to write the JSON result")

    trade_health_parser = trade_subparsers.add_parser("health")
    _add_trade_health_arguments(trade_health_parser)
    trade_health_parser.add_argument("--output", help="Optional path to write the JSON result")

    trade_preflight_parser = trade_subparsers.add_parser("preflight")
    _add_trade_preflight_arguments(trade_preflight_parser)
    trade_preflight_parser.add_argument("--output", help="Optional path to write the JSON result")

    trade_submit_ready_parser = trade_subparsers.add_parser("submit-ready")
    _add_trade_submit_ready_arguments(trade_submit_ready_parser)
    trade_submit_ready_parser.add_argument("--output", help="Optional path to write the JSON result")

    trade_confirm_current_parser = trade_subparsers.add_parser("confirm-current")
    _add_trade_confirm_current_arguments(trade_confirm_current_parser)
    trade_confirm_current_parser.add_argument("--output", help="Optional path to write the JSON result")

    trade_dialog_readiness_parser = trade_subparsers.add_parser("dialog-readiness")
    _add_trade_dialog_readiness_arguments(trade_dialog_readiness_parser)
    trade_dialog_readiness_parser.add_argument("--output", help="Optional path to write the JSON result")

    trade_broker_capabilities_parser = trade_subparsers.add_parser("broker-capabilities")
    trade_broker_capabilities_parser.add_argument("--broker", default="pingan_desktop")
    trade_broker_capabilities_parser.add_argument("--profile", default="balanced")
    trade_broker_capabilities_parser.add_argument("--output", help="Optional path to write the JSON result")

    trade_buy_parser = trade_subparsers.add_parser("buy")
    _add_trade_common_arguments(trade_buy_parser)
    _add_trade_buy_profile_arguments(trade_buy_parser)
    trade_buy_parser.add_argument("--output", help="Optional path to write the JSON result")

    trade_submit_once_parser = trade_subparsers.add_parser("submit-once")
    _add_trade_common_arguments(trade_submit_once_parser)
    _add_trade_submit_once_profile_arguments(trade_submit_once_parser)
    trade_submit_once_parser.add_argument("--output", help="Optional path to write the JSON result")

    trade_presets_parser = trade_subparsers.add_parser("presets")
    trade_presets_parser.add_argument("--preset")
    trade_presets_parser.add_argument("--output", help="Optional path to write the JSON result")

    trade_run_parser = trade_subparsers.add_parser("run")
    trade_run_parser.add_argument("--preset", required=True)
    _add_trade_run_arguments(trade_run_parser)
    trade_run_parser.add_argument("--output", help="Optional path to write the JSON result")

    return trade_parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TongDaXin / Ping An bridge and desktop automation CLI")
    parser.add_argument("--exe-path", help="Explicit Windows or WSL path to TdxW.exe")
    parser.add_argument("--title-key", default="平安证券", help="Top-level window title keyword")

    subparsers = parser.add_subparsers(dest="command", required=True)
    _build_api_parser(subparsers)
    _build_task_parser(subparsers)
    _build_report_parser(subparsers)
    _build_trade_parser(subparsers)
    _build_catalog_parser(subparsers)
    _build_bridge_parser(subparsers)
    health_parser = subparsers.add_parser("health-check")
    inspect_parser = subparsers.add_parser("inspect")
    uia_windows_parser = subparsers.add_parser("uia-windows")
    uia_windows_parser.add_argument("--window-key", help="Optional keyword to filter desktop top-level windows")
    uia_inspect_parser = subparsers.add_parser("uia-inspect")
    uia_inspect_parser.add_argument("--max-depth", type=int, default=6)
    uia_dialogs_parser = subparsers.add_parser("uia-dialogs")
    uia_dialogs_parser.add_argument("--window-key", help="Optional keyword to filter dialog title/class")
    uia_dialogs_parser.add_argument("--max-depth", type=int, default=4)
    uia_dialogs_parser.add_argument("--include-all-windows", action="store_true")
    uia_wait_dialog_parser = subparsers.add_parser("uia-wait-dialog")
    uia_wait_dialog_parser.add_argument("--window-key", help="Optional keyword to filter dialog title/class")
    uia_wait_dialog_parser.add_argument("--max-depth", type=int, default=4)
    uia_wait_dialog_parser.add_argument("--include-all-windows", action="store_true")
    uia_wait_dialog_parser.add_argument("--timeout", type=float, default=8.0)
    uia_wait_dialog_parser.add_argument("--poll-interval", type=float, default=0.25)
    uia_wait_dialog_parser.add_argument("--exclude-handle", type=int)
    uia_wait_dialog_parser.add_argument("--exclude-handles", type=int, nargs="*")
    uia_wait_dialog_parser.add_argument("--exclude-class-name", action="append", default=[])
    uia_wait_dialog_parser.add_argument("--baseline-handle", type=int, action="append", default=[])
    uia_wait_dialog_parser.add_argument("--require-new-handle", action="store_true")
    uia_wait_dialog_parser.add_argument("--foreground-only", action="store_true")
    uia_click_parser = subparsers.add_parser("uia-click")
    uia_click_parser.add_argument("--automation-id")
    uia_click_parser.add_argument("--name")
    uia_click_parser.add_argument("--control-type")
    uia_click_parser.add_argument("--timeout", type=float, default=5.0)
    uia_click_parser.add_argument("--post-delay", type=float, default=0.5)
    uia_click_path_parser = subparsers.add_parser("uia-click-path")
    uia_click_path_parser.add_argument("--path", required=True)
    uia_click_path_parser.add_argument("--timeout", type=float, default=5.0)
    uia_click_path_parser.add_argument("--post-delay", type=float, default=0.5)
    uia_click_center_parser = subparsers.add_parser("uia-click-center")
    uia_click_center_parser.add_argument("--automation-id")
    uia_click_center_parser.add_argument("--name")
    uia_click_center_parser.add_argument("--control-type")
    uia_click_center_parser.add_argument("--timeout", type=float, default=5.0)
    uia_click_center_parser.add_argument("--post-delay", type=float, default=0.5)
    uia_activate_parser = subparsers.add_parser("uia-activate")
    uia_activate_parser.add_argument("--automation-id")
    uia_activate_parser.add_argument("--name")
    uia_activate_parser.add_argument("--control-type")
    uia_activate_parser.add_argument(
        "--strategy",
        default="auto",
        choices=["auto", "invoke", "click_input", "bm_click", "wm_command", "enter_key"],
    )
    uia_activate_parser.add_argument("--timeout", type=float, default=5.0)
    uia_activate_parser.add_argument("--post-delay", type=float, default=0.5)
    uia_set_text_parser = subparsers.add_parser("uia-set-text")
    uia_set_text_parser.add_argument("--value", required=True)
    uia_set_text_parser.add_argument("--automation-id")
    uia_set_text_parser.add_argument("--name")
    uia_set_text_parser.add_argument("--control-type", default="Edit")
    uia_set_text_parser.add_argument("--timeout", type=float, default=5.0)
    uia_set_text_parser.add_argument("--post-delay", type=float, default=0.2)
    uia_read_parser = subparsers.add_parser("uia-read")
    uia_read_parser.add_argument("--automation-id")
    uia_read_parser.add_argument("--name")
    uia_read_parser.add_argument("--control-type")
    uia_read_parser.add_argument("--timeout", type=float, default=5.0)
    uia_combobox_items_parser = subparsers.add_parser("uia-combobox-items")
    uia_combobox_items_parser.add_argument("--automation-id")
    uia_combobox_items_parser.add_argument("--name")
    uia_combobox_items_parser.add_argument("--timeout", type=float, default=5.0)
    uia_combobox_items_parser.add_argument("--post-delay", type=float, default=0.5)
    uia_combobox_select_parser = subparsers.add_parser("uia-combobox-select")
    uia_combobox_select_parser.add_argument("--item-name", required=True)
    uia_combobox_select_parser.add_argument("--automation-id")
    uia_combobox_select_parser.add_argument("--name")
    uia_combobox_select_parser.add_argument("--timeout", type=float, default=5.0)
    uia_combobox_select_parser.add_argument("--post-delay", type=float, default=0.5)
    detect_parser = subparsers.add_parser("detect")
    detect_snapshot_parser = subparsers.add_parser("detect-snapshot")
    detect_snapshot_parser.add_argument("--snapshot", required=True, help="Path to inspect JSON output")
    uia_detect_snapshot_parser = subparsers.add_parser("uia-detect-snapshot")
    uia_detect_snapshot_parser.add_argument("--snapshot", required=True, help="Path to UIA inspect JSON output")
    pingan_probe_parser = subparsers.add_parser("pingan-probe")
    pingan_probe_parser.add_argument("--code", required=True)
    pingan_probe_parser.add_argument("--price", required=True)
    pingan_probe_parser.add_argument("--quantity", required=True, type=int)
    pingan_probe_parser.add_argument("--post-delay", type=float, default=1.0)
    pingan_probe_parser.add_argument("--max-depth", type=int, default=12)
    pingan_hid_submit_probe_parser = subparsers.add_parser("pingan-hid-submit-probe")
    pingan_hid_submit_probe_parser.add_argument("--port", required=True)
    pingan_hid_submit_probe_parser.add_argument("--baudrate", type=int, default=115200)
    pingan_hid_submit_probe_parser.add_argument("--timeout", type=float, default=2.0)
    pingan_hid_submit_probe_parser.add_argument("--hid-pre-delay", type=float, default=0.0)
    pingan_hid_submit_probe_parser.add_argument("--code", required=True)
    pingan_hid_submit_probe_parser.add_argument("--price", required=True)
    pingan_hid_submit_probe_parser.add_argument("--quantity", required=True, type=int)
    pingan_hid_submit_probe_parser.add_argument(
        "--submit-mode",
        default="button_enter",
        choices=["button_enter", "quantity_tab_enter"],
    )
    pingan_hid_submit_probe_parser.add_argument("--post-delay", type=float, default=1.0)
    pingan_hid_submit_probe_parser.add_argument("--max-depth", type=int, default=12)
    pingan_hid_submit_probe_parser.add_argument("--dialog-timeout", type=float, default=2.5)
    pingan_buy_submit_once_parser = subparsers.add_parser("pingan-buy-submit-once")
    pingan_buy_submit_once_parser.add_argument("--port", required=True)
    pingan_buy_submit_once_parser.add_argument("--baudrate", type=int, default=115200)
    pingan_buy_submit_once_parser.add_argument("--timeout", type=float, default=2.0)
    pingan_buy_submit_once_parser.add_argument("--hid-pre-delay", type=float, default=0.0)
    pingan_buy_submit_once_parser.add_argument("--code", required=True)
    pingan_buy_submit_once_parser.add_argument("--price", required=True)
    pingan_buy_submit_once_parser.add_argument("--quantity", required=True, type=int)
    pingan_buy_submit_once_parser.add_argument("--post-delay", type=float, default=1.0)
    pingan_buy_submit_once_parser.add_argument("--max-depth", type=int, default=12)
    pingan_buy_submit_once_parser.add_argument("--dialog-timeout", type=float, default=2.5)
    pingan_buy_submit_once_parser.add_argument("--confirm-timeout", type=float, default=3.0)
    pingan_buy_submit_once_parser.add_argument("--confirm-post-delay", type=float, default=1.0)
    pingan_buy_submit_once_parser.add_argument("--result-timeout", type=float, default=3.0)
    pingan_buy_submit_once_parser.add_argument("--close-result-dialog", action=argparse.BooleanOptionalAction, default=True)
    pingan_buy_submit_once_parser.add_argument("--result-close-pre-delay", type=float, default=0.0)
    pingan_buy_submit_once_parser.add_argument("--capture-final-uia", action=argparse.BooleanOptionalAction, default=True)
    _add_trade_safety_arguments(pingan_buy_submit_once_parser)
    pingan_buy_parser = subparsers.add_parser("pingan-buy")
    pingan_buy_parser.add_argument("--port", required=True)
    pingan_buy_parser.add_argument("--baudrate", type=int, default=115200)
    pingan_buy_parser.add_argument("--timeout", type=float, default=2.0)
    pingan_buy_parser.add_argument("--code", required=True)
    pingan_buy_parser.add_argument("--price", required=True)
    pingan_buy_parser.add_argument("--quantity", required=True, type=int)
    pingan_buy_parser.add_argument("--profile", choices=["stable", "balanced", "fast", "turbo"], default="balanced")
    pingan_buy_parser.add_argument(
        "--price-quantity-input-mode",
        choices=["uia", "win32", "hybrid_win32"],
        help="How price/quantity edits are written in the fast path. Code input always stays on UIA.",
    )
    pingan_buy_parser.add_argument(
        "--dialog-lookup-mode",
        choices=["uia", "win32_experimental"],
        help="How confirm/result dialogs are found. The experimental mode is opt-in and falls back to UIA on failure.",
    )
    pingan_buy_parser.add_argument("--close-result-dialog", action=argparse.BooleanOptionalAction, default=True)
    pingan_buy_parser.add_argument("--max-depth", type=int, default=12)
    pingan_buy_parser.add_argument("--capture-final-uia", action=argparse.BooleanOptionalAction)
    pingan_buy_parser.add_argument("--hid-pre-delay", type=float)
    pingan_buy_parser.add_argument("--post-delay", type=float)
    pingan_buy_parser.add_argument("--dialog-timeout", type=float)
    pingan_buy_parser.add_argument("--confirm-timeout", type=float)
    pingan_buy_parser.add_argument("--confirm-post-delay", type=float)
    pingan_buy_parser.add_argument("--result-timeout", type=float)
    pingan_buy_parser.add_argument("--result-close-pre-delay", type=float)
    _add_trade_safety_arguments(pingan_buy_parser)
    tdx_capabilities_parser = subparsers.add_parser("tdx-capabilities")
    _add_replay_provider_arguments(tdx_capabilities_parser)
    tdx_health_parser = subparsers.add_parser("tdx-health")
    tdx_health_parser.add_argument("--window-key", default="通达信金融终端")
    tdx_health_parser.add_argument("--hid-port")
    tdx_health_parser.add_argument("--strategy-path")
    _add_replay_provider_arguments(tdx_health_parser)
    tdx_doctor_parser = subparsers.add_parser("tdx-doctor")
    tdx_doctor_parser.add_argument("--window-key", default="通达信金融终端")
    tdx_doctor_parser.add_argument("--hid-port")
    tdx_doctor_parser.add_argument("--strategy-path")
    _add_replay_provider_arguments(tdx_doctor_parser)
    tdx_probe_parser = subparsers.add_parser("tdx-probe")
    tdx_probe_parser.add_argument("--window-key", default="通达信", help="Top-level window keyword for TongDaXin")
    tdx_probe_parser.add_argument("--max-depth", type=int, default=12)
    tdx_stock_message_parser = subparsers.add_parser("tdx-stock-message")
    tdx_stock_message_parser.add_argument("--window-key", default="通达信金融终端")
    tdx_stock_message_parser.add_argument("--code", required=True, help="6-digit stock code, for example 000001")
    tdx_stock_message_parser.add_argument("--market", choices=["auto", "sh", "sz"], default="auto")
    tdx_stock_message_parser.add_argument("--post-delay", type=float, default=1.0)
    tdx_stock_message_parser.add_argument("--max-depth", type=int, default=12)
    tdx_bridge_health_parser = subparsers.add_parser("tdx-bridge-health")
    tdx_bridge_health_parser.add_argument("--window-key", default="通达信金融终端")
    tdx_bridge_health_parser.add_argument("--strategy-path")
    tdx_bridge_health_parser.add_argument("--hid-port")
    tdx_trade_probe_parser = subparsers.add_parser("tdx-trade-probe")
    tdx_trade_probe_parser.add_argument("--window-key", default="通达信金融终端")
    tdx_trade_probe_parser.add_argument("--max-depth", type=int, default=12)
    tdx_trade_hid_ping_parser = subparsers.add_parser("tdx-trade-hid-ping")
    tdx_trade_hid_ping_parser.add_argument("--port", required=True)
    tdx_trade_hid_ping_parser.add_argument("--baudrate", type=int, default=115200)
    tdx_trade_hid_ping_parser.add_argument("--timeout", type=float, default=2.0)
    tdx_trade_hid_ping_parser.add_argument("--pre-delay", type=float, default=0.0)
    tdx_trade_hid_send_parser = subparsers.add_parser("tdx-trade-hid-send")
    tdx_trade_hid_send_parser.add_argument("--port", required=True)
    tdx_trade_hid_send_parser.add_argument("--baudrate", type=int, default=115200)
    tdx_trade_hid_send_parser.add_argument("--timeout", type=float, default=2.0)
    tdx_trade_hid_send_parser.add_argument("--pre-delay", type=float, default=0.0)
    tdx_trade_hid_send_parser.add_argument("--wire-command", required=True)
    tdx_trade_buy_probe_parser = subparsers.add_parser("tdx-trade-buy-probe")
    tdx_trade_buy_probe_parser.add_argument("--window-key", default="通达信金融终端")
    tdx_trade_buy_probe_parser.add_argument("--port", required=True)
    tdx_trade_buy_probe_parser.add_argument("--baudrate", type=int, default=115200)
    tdx_trade_buy_probe_parser.add_argument("--timeout", type=float, default=2.0)
    tdx_trade_buy_probe_parser.add_argument("--code", required=True)
    tdx_trade_buy_probe_parser.add_argument("--price", required=True)
    tdx_trade_buy_probe_parser.add_argument("--quantity", required=True, type=int)
    tdx_trade_buy_probe_parser.add_argument("--commit-key", choices=["none", "tab", "enter"], default="tab")
    tdx_trade_buy_probe_parser.add_argument(
        "--submit-strategy",
        default="post_wm_command_parent",
        choices=[
            "bm_click",
            "wm_command_parent",
            "post_wm_command_parent",
            "enter_key",
            "space_key",
            "mouse_message",
            "wm_command_ancestor_2",
            "post_wm_command_ancestor_2",
            "wm_command_ancestor_3",
            "post_wm_command_ancestor_3",
            "wm_command_ancestor_4",
            "post_wm_command_ancestor_4",
            "wm_command_ancestor_5",
            "post_wm_command_ancestor_5",
        ],
    )
    tdx_trade_buy_probe_parser.add_argument("--pre-clear", action="store_true")
    tdx_trade_buy_probe_parser.add_argument("--post-delay", type=float, default=1.0)
    tdx_trade_buy_probe_parser.add_argument("--max-depth", type=int, default=12)
    tdx_trade_buy_probe_parser.add_argument("--dialog-timeout", type=float, default=2.5)
    tdx_trade_buy_probe_parser.add_argument("--dry-run", action="store_true")
    tdx_data_snapshot_parser = subparsers.add_parser("tdx-data-snapshot")
    tdx_data_snapshot_parser.add_argument("--code", required=True)
    tdx_data_snapshot_parser.add_argument("--field", action="append", default=[])
    tdx_data_snapshot_parser.add_argument("--strategy-path")
    tdx_data_market_snapshot_parser = subparsers.add_parser("tdx-data-market-snapshot")
    tdx_data_market_snapshot_parser.add_argument("--code", required=True)
    tdx_data_market_snapshot_parser.add_argument("--field", action="append", default=[])
    tdx_data_market_snapshot_parser.add_argument("--strategy-path")
    tdx_data_kline_parser = subparsers.add_parser("tdx-data-kline")
    tdx_data_kline_parser.add_argument("--code", action="append", required=True)
    tdx_data_kline_parser.add_argument("--period", required=True)
    tdx_data_kline_parser.add_argument("--start-time", default="")
    tdx_data_kline_parser.add_argument("--end-time", default="")
    tdx_data_kline_parser.add_argument("--count", type=int, default=-1)
    tdx_data_kline_parser.add_argument("--dividend-type", default="none", choices=["none", "front", "back"])
    tdx_data_kline_parser.add_argument("--field", action="append", default=[])
    tdx_data_kline_parser.add_argument("--fill-data", action=argparse.BooleanOptionalAction, default=True)
    tdx_data_kline_parser.add_argument("--strategy-path")
    tdx_data_stock_info_parser = subparsers.add_parser("tdx-data-stock-info")
    tdx_data_stock_info_parser.add_argument("--code", required=True)
    tdx_data_stock_info_parser.add_argument("--field", action="append", default=[])
    tdx_data_stock_info_parser.add_argument("--strategy-path")
    tdx_data_stock_list_parser = subparsers.add_parser("tdx-data-stock-list")
    tdx_data_stock_list_parser.add_argument("--market")
    tdx_data_stock_list_parser.add_argument("--list-type", type=int, default=0, choices=[0, 1])
    tdx_data_stock_list_parser.add_argument("--strategy-path")
    tdx_data_more_info_parser = subparsers.add_parser("tdx-data-more-info")
    tdx_data_more_info_parser.add_argument("--code", required=True)
    tdx_data_more_info_parser.add_argument("--field", action="append", default=[])
    tdx_data_more_info_parser.add_argument("--strategy-path")
    tdx_data_cb_info_parser = subparsers.add_parser("tdx-data-cb-info")
    tdx_data_cb_info_parser.add_argument("--code", required=True)
    tdx_data_cb_info_parser.add_argument("--field", action="append", default=[])
    tdx_data_cb_info_parser.add_argument("--strategy-path")
    tdx_data_gb_info_parser = subparsers.add_parser("tdx-data-gb-info")
    tdx_data_gb_info_parser.add_argument("--code", required=True)
    tdx_data_gb_info_parser.add_argument("--date", action="append", required=True)
    tdx_data_gb_info_parser.add_argument("--count", type=int, required=True)
    tdx_data_gb_info_parser.add_argument("--strategy-path")
    tdx_data_gp_one_parser = subparsers.add_parser("tdx-data-gp-one")
    tdx_data_gp_one_parser.add_argument("--code", action="append", required=True)
    tdx_data_gp_one_parser.add_argument("--field", action="append", required=True)
    tdx_data_gp_one_parser.add_argument("--strategy-path")
    tdx_data_divid_factors_parser = subparsers.add_parser("tdx-data-divid-factors")
    tdx_data_divid_factors_parser.add_argument("--code", required=True)
    tdx_data_divid_factors_parser.add_argument("--start-time", default="")
    tdx_data_divid_factors_parser.add_argument("--end-time", default="")
    tdx_data_divid_factors_parser.add_argument("--strategy-path")
    tdx_data_ipo_info_parser = subparsers.add_parser("tdx-data-ipo-info")
    tdx_data_ipo_info_parser.add_argument("--ipo-type", default=0, type=int, choices=[0, 1, 2])
    tdx_data_ipo_info_parser.add_argument("--ipo-date", default=0, type=int, choices=[0, 1])
    tdx_data_ipo_info_parser.add_argument("--strategy-path")
    tdx_data_financial_parser = subparsers.add_parser("tdx-data-financial")
    tdx_data_financial_parser.add_argument("--code", action="append", required=True)
    tdx_data_financial_parser.add_argument("--field", action="append", required=True)
    tdx_data_financial_parser.add_argument("--start-time", default="")
    tdx_data_financial_parser.add_argument("--end-time", default="")
    tdx_data_financial_parser.add_argument("--report-type", default="report_time")
    tdx_data_financial_parser.add_argument("--strategy-path")
    tdx_data_financial_by_date_parser = subparsers.add_parser("tdx-data-financial-by-date")
    tdx_data_financial_by_date_parser.add_argument("--code", action="append", required=True)
    tdx_data_financial_by_date_parser.add_argument("--field", action="append", required=True)
    tdx_data_financial_by_date_parser.add_argument("--year", required=True, type=int)
    tdx_data_financial_by_date_parser.add_argument("--mmdd", required=True, type=int)
    tdx_data_financial_by_date_parser.add_argument("--strategy-path")
    tdx_data_stock_transaction_parser = subparsers.add_parser("tdx-data-stock-transaction")
    tdx_data_stock_transaction_parser.add_argument("--code", action="append", required=True)
    tdx_data_stock_transaction_parser.add_argument("--field", action="append", required=True)
    tdx_data_stock_transaction_parser.add_argument("--start-time", default="")
    tdx_data_stock_transaction_parser.add_argument("--end-time", default="")
    tdx_data_stock_transaction_parser.add_argument("--strategy-path")
    tdx_data_stock_transaction_by_date_parser = subparsers.add_parser("tdx-data-stock-transaction-by-date")
    tdx_data_stock_transaction_by_date_parser.add_argument("--code", action="append", required=True)
    tdx_data_stock_transaction_by_date_parser.add_argument("--field", action="append", required=True)
    tdx_data_stock_transaction_by_date_parser.add_argument("--year", required=True, type=int)
    tdx_data_stock_transaction_by_date_parser.add_argument("--mmdd", required=True, type=int)
    tdx_data_stock_transaction_by_date_parser.add_argument("--strategy-path")
    tdx_data_sector_transaction_parser = subparsers.add_parser("tdx-data-sector-transaction")
    tdx_data_sector_transaction_parser.add_argument("--code", action="append", required=True)
    tdx_data_sector_transaction_parser.add_argument("--field", action="append", required=True)
    tdx_data_sector_transaction_parser.add_argument("--start-time", default="")
    tdx_data_sector_transaction_parser.add_argument("--end-time", default="")
    tdx_data_sector_transaction_parser.add_argument("--strategy-path")
    tdx_data_sector_transaction_by_date_parser = subparsers.add_parser("tdx-data-sector-transaction-by-date")
    tdx_data_sector_transaction_by_date_parser.add_argument("--code", action="append", required=True)
    tdx_data_sector_transaction_by_date_parser.add_argument("--field", action="append", required=True)
    tdx_data_sector_transaction_by_date_parser.add_argument("--year", required=True, type=int)
    tdx_data_sector_transaction_by_date_parser.add_argument("--mmdd", required=True, type=int)
    tdx_data_sector_transaction_by_date_parser.add_argument("--strategy-path")
    tdx_data_market_transaction_parser = subparsers.add_parser("tdx-data-market-transaction")
    tdx_data_market_transaction_parser.add_argument("--field", action="append", required=True)
    tdx_data_market_transaction_parser.add_argument("--start-time", default="")
    tdx_data_market_transaction_parser.add_argument("--end-time", default="")
    tdx_data_market_transaction_parser.add_argument("--strategy-path")
    tdx_data_market_transaction_by_date_parser = subparsers.add_parser("tdx-data-market-transaction-by-date")
    tdx_data_market_transaction_by_date_parser.add_argument("--field", action="append", required=True)
    tdx_data_market_transaction_by_date_parser.add_argument("--year", required=True, type=int)
    tdx_data_market_transaction_by_date_parser.add_argument("--mmdd", required=True, type=int)
    tdx_data_market_transaction_by_date_parser.add_argument("--strategy-path")
    tdx_data_sector_list_parser = subparsers.add_parser("tdx-data-sector-list")
    tdx_data_sector_list_parser.add_argument("--list-type", type=int, default=0, choices=[0, 1])
    tdx_data_sector_list_parser.add_argument("--strategy-path")
    tdx_data_sector_stocks_parser = subparsers.add_parser("tdx-data-sector-stocks")
    tdx_data_sector_stocks_parser.add_argument("--sector", required=True)
    tdx_data_sector_stocks_parser.add_argument("--block-type", type=int, default=0, choices=[0, 1])
    tdx_data_sector_stocks_parser.add_argument("--list-type", type=int, default=0, choices=[0, 1])
    tdx_data_sector_stocks_parser.add_argument("--strategy-path")
    tdx_refresh_cache_parser = subparsers.add_parser("tdx-refresh-cache")
    tdx_refresh_cache_parser.add_argument("--market", default="AG")
    tdx_refresh_cache_parser.add_argument("--force", action=argparse.BooleanOptionalAction, default=False)
    tdx_refresh_cache_parser.add_argument("--strategy-path")
    tdx_get_trading_dates_parser = subparsers.add_parser("tdx-get-trading-dates")
    tdx_get_trading_dates_parser.add_argument("--market", default="SH")
    tdx_get_trading_dates_parser.add_argument("--start-time", default="")
    tdx_get_trading_dates_parser.add_argument("--end-time", default="")
    tdx_get_trading_dates_parser.add_argument("--count", type=int, default=-1)
    tdx_get_trading_dates_parser.add_argument("--strategy-path")
    tdx_refresh_kline_parser = subparsers.add_parser("tdx-refresh-kline")
    tdx_refresh_kline_parser.add_argument("--code", action="append", required=True)
    tdx_refresh_kline_parser.add_argument("--period", required=True)
    tdx_refresh_kline_parser.add_argument("--strategy-path")
    tdx_download_file_parser = subparsers.add_parser("tdx-download-file")
    tdx_download_file_parser.add_argument("--code", required=True)
    tdx_download_file_parser.add_argument("--down-time", default="")
    tdx_download_file_parser.add_argument("--down-type", required=True, type=int, choices=[1, 2, 3, 4])
    tdx_download_file_parser.add_argument("--strategy-path")
    tdx_send_warn_parser = subparsers.add_parser("tdx-send-warn")
    tdx_send_warn_parser.add_argument("--code", action="append", required=True)
    tdx_send_warn_parser.add_argument("--time", action="append", required=True)
    tdx_send_warn_parser.add_argument("--price", action="append")
    tdx_send_warn_parser.add_argument("--close", action="append")
    tdx_send_warn_parser.add_argument("--volume", action="append")
    tdx_send_warn_parser.add_argument("--bs-flag", action="append")
    tdx_send_warn_parser.add_argument("--warn-type", action="append")
    tdx_send_warn_parser.add_argument("--reason", action="append")
    tdx_send_warn_parser.add_argument("--count", type=int, default=1)
    tdx_send_warn_parser.add_argument("--strategy-path")
    tdx_get_user_sector_parser = subparsers.add_parser("tdx-get-user-sector")
    tdx_get_user_sector_parser.add_argument("--strategy-path")
    tdx_create_sector_parser = subparsers.add_parser("tdx-create-sector")
    tdx_create_sector_parser.add_argument("--block-code", required=True)
    tdx_create_sector_parser.add_argument("--block-name", required=True)
    _add_block_mutation_arguments(tdx_create_sector_parser)
    tdx_create_sector_parser.add_argument("--strategy-path")
    tdx_delete_sector_parser = subparsers.add_parser("tdx-delete-sector")
    tdx_delete_sector_parser.add_argument("--block-code", required=True)
    _add_block_mutation_arguments(tdx_delete_sector_parser)
    tdx_delete_sector_parser.add_argument("--strategy-path")
    tdx_rename_sector_parser = subparsers.add_parser("tdx-rename-sector")
    tdx_rename_sector_parser.add_argument("--block-code", required=True)
    tdx_rename_sector_parser.add_argument("--block-name", required=True)
    _add_block_mutation_arguments(tdx_rename_sector_parser)
    tdx_rename_sector_parser.add_argument("--strategy-path")
    tdx_clear_sector_parser = subparsers.add_parser("tdx-clear-sector")
    tdx_clear_sector_parser.add_argument("--block-code", required=True)
    _add_block_mutation_arguments(tdx_clear_sector_parser)
    tdx_clear_sector_parser.add_argument("--strategy-path")
    tdx_send_user_block_parser = subparsers.add_parser("tdx-send-user-block")
    tdx_send_user_block_parser.add_argument("--block-code", required=True)
    tdx_send_user_block_parser.add_argument("--stock", action="append", default=[])
    tdx_send_user_block_parser.add_argument("--show", action=argparse.BooleanOptionalAction, default=False)
    _add_block_mutation_arguments(tdx_send_user_block_parser)
    tdx_send_user_block_parser.add_argument("--strategy-path")
    _add_replay_provider_arguments(tdx_send_user_block_parser)
    tdx_block_read_watchlist_parser = subparsers.add_parser("tdx-block-read-watchlist")
    tdx_block_read_watchlist_parser.add_argument("--block-code", required=True)
    tdx_block_read_watchlist_parser.add_argument("--strategy-path")
    _add_replay_provider_arguments(tdx_block_read_watchlist_parser)
    tdx_formula_format_data_parser = subparsers.add_parser("tdx-formula-format-data")
    tdx_formula_format_data_parser.add_argument("--input-json-file", required=True)
    tdx_formula_format_data_parser.add_argument("--strategy-path")
    tdx_formula_set_data_parser = subparsers.add_parser("tdx-formula-set-data")
    tdx_formula_set_data_parser.add_argument("--code", required=True)
    tdx_formula_set_data_parser.add_argument("--stock-period", default="1d")
    tdx_formula_set_data_parser.add_argument("--stock-data-file", required=True)
    tdx_formula_set_data_parser.add_argument("--count", required=True, type=int)
    tdx_formula_set_data_parser.add_argument("--dividend-type", default=0, type=int, choices=[0, 1, 2])
    tdx_formula_set_data_parser.add_argument("--strategy-path")
    tdx_formula_set_data_info_parser = subparsers.add_parser("tdx-formula-set-data-info")
    tdx_formula_set_data_info_parser.add_argument("--code", required=True)
    tdx_formula_set_data_info_parser.add_argument("--stock-period", default="1d")
    tdx_formula_set_data_info_parser.add_argument("--start-time", default="")
    tdx_formula_set_data_info_parser.add_argument("--end-time", default="")
    tdx_formula_set_data_info_parser.add_argument("--count", default=-1, type=int)
    tdx_formula_set_data_info_parser.add_argument("--dividend-type", default=0, type=int, choices=[0, 1, 2])
    tdx_formula_set_data_info_parser.add_argument("--strategy-path")
    tdx_formula_get_data_parser = subparsers.add_parser("tdx-formula-get-data")
    tdx_formula_get_data_parser.add_argument("--strategy-path")
    tdx_formula_zb_parser = subparsers.add_parser("tdx-formula-zb")
    tdx_formula_zb_parser.add_argument("--formula-name", required=True)
    tdx_formula_zb_parser.add_argument("--formula-arg", default="")
    tdx_formula_zb_parser.add_argument("--xsflag", default=-1, type=int)
    tdx_formula_zb_parser.add_argument("--strategy-path")
    tdx_formula_xg_parser = subparsers.add_parser("tdx-formula-xg")
    tdx_formula_xg_parser.add_argument("--formula-name", required=True)
    tdx_formula_xg_parser.add_argument("--formula-arg", default="")
    tdx_formula_xg_parser.add_argument("--strategy-path")
    tdx_formula_screen_parser = subparsers.add_parser("tdx-formula-screen")
    tdx_formula_screen_parser.add_argument("--formula-name", required=True)
    tdx_formula_screen_parser.add_argument("--formula-arg", default="")
    tdx_formula_screen_parser.add_argument("--return-count", default=1, type=int)
    tdx_formula_screen_parser.add_argument("--return-date", action=argparse.BooleanOptionalAction, default=False)
    tdx_formula_screen_parser.add_argument("--code", action="append", required=True)
    tdx_formula_screen_parser.add_argument("--stock-period", default="1d")
    tdx_formula_screen_parser.add_argument("--start-time", default="")
    tdx_formula_screen_parser.add_argument("--end-time", default="")
    tdx_formula_screen_parser.add_argument("--count", default=0, type=int)
    _add_replay_provider_arguments(tdx_formula_screen_parser)
    tdx_formula_screen_parser.add_argument("--dividend-type", default=0, type=int, choices=[0, 1, 2])
    tdx_formula_screen_parser.add_argument("--strategy-path")
    tdx_formula_exp_parser = subparsers.add_parser("tdx-formula-exp")
    tdx_formula_exp_parser.add_argument("--formula-name", required=True)
    tdx_formula_exp_parser.add_argument("--formula-arg", default="")
    tdx_formula_exp_parser.add_argument("--strategy-path")
    tdx_formula_mul_xg_parser = subparsers.add_parser("tdx-formula-mul-xg")
    tdx_formula_mul_xg_parser.add_argument("--formula-name", required=True)
    tdx_formula_mul_xg_parser.add_argument("--formula-arg", default="")
    tdx_formula_mul_xg_parser.add_argument("--return-count", default=1, type=int)
    tdx_formula_mul_xg_parser.add_argument("--return-date", action=argparse.BooleanOptionalAction, default=False)
    tdx_formula_mul_xg_parser.add_argument("--code", action="append", required=True)
    tdx_formula_mul_xg_parser.add_argument("--stock-period", default="1d")
    tdx_formula_mul_xg_parser.add_argument("--start-time", default="")
    tdx_formula_mul_xg_parser.add_argument("--end-time", default="")
    tdx_formula_mul_xg_parser.add_argument("--count", default=0, type=int)
    tdx_formula_mul_xg_parser.add_argument("--dividend-type", default=0, type=int, choices=[0, 1, 2])
    tdx_formula_mul_xg_parser.add_argument("--strategy-path")
    tdx_formula_mul_zb_parser = subparsers.add_parser("tdx-formula-mul-zb")
    tdx_formula_mul_zb_parser.add_argument("--formula-name", required=True)
    tdx_formula_mul_zb_parser.add_argument("--formula-arg", default="")
    tdx_formula_mul_zb_parser.add_argument("--xsflag", default=-1, type=int)
    tdx_formula_mul_zb_parser.add_argument("--return-count", default=1, type=int)
    tdx_formula_mul_zb_parser.add_argument("--return-date", action=argparse.BooleanOptionalAction, default=False)
    tdx_formula_mul_zb_parser.add_argument("--code", action="append", required=True)
    tdx_formula_mul_zb_parser.add_argument("--stock-period", default="1d")
    tdx_formula_mul_zb_parser.add_argument("--start-time", default="")
    tdx_formula_mul_zb_parser.add_argument("--end-time", default="")
    tdx_formula_mul_zb_parser.add_argument("--count", default=0, type=int)
    tdx_formula_mul_zb_parser.add_argument("--dividend-type", default=0, type=int, choices=[0, 1, 2])
    tdx_formula_mul_zb_parser.add_argument("--strategy-path")
    hid_ping_parser = subparsers.add_parser("hid-ping")
    hid_ping_parser.add_argument("--port", required=True)
    hid_ping_parser.add_argument("--baudrate", type=int, default=115200)
    hid_ping_parser.add_argument("--timeout", type=float, default=2.0)
    hid_ping_parser.add_argument("--pre-delay", type=float, default=0.0)
    hid_send_parser = subparsers.add_parser("hid-send")
    hid_send_parser.add_argument("--port", required=True)
    hid_send_parser.add_argument("--baudrate", type=int, default=115200)
    hid_send_parser.add_argument("--timeout", type=float, default=2.0)
    hid_send_parser.add_argument("--pre-delay", type=float, default=0.0)
    hid_send_parser.add_argument("--wire-command", required=True)
    win32_read_parser = subparsers.add_parser("win32-read")
    win32_read_parser.add_argument("--hwnd", required=True, type=int)
    win32_set_text_parser = subparsers.add_parser("win32-set-text")
    win32_set_text_parser.add_argument("--hwnd", required=True, type=int)
    win32_set_text_parser.add_argument("--value", required=True)
    win32_set_text_parser.add_argument("--post-delay", type=float, default=0.2)
    win32_type_text_parser = subparsers.add_parser("win32-type-text")
    win32_type_text_parser.add_argument("--hwnd", required=True, type=int)
    win32_type_text_parser.add_argument("--value", required=True)
    win32_type_text_parser.add_argument("--post-delay", type=float, default=0.2)
    win32_click_parser = subparsers.add_parser("win32-click")
    win32_click_parser.add_argument("--hwnd", required=True, type=int)
    win32_click_parser.add_argument(
        "--strategy",
        default="bm_click",
        choices=["bm_click", "wm_command", "post_wm_command", "enter_key", "space_key", "tab_key", "mouse_message"],
    )
    win32_click_parser.add_argument("--post-delay", type=float, default=0.5)
    tdx_submit_probe_parser = subparsers.add_parser("tdx-submit-probe")
    tdx_submit_probe_parser.add_argument("--window-key", default="通达信金融终端")
    tdx_submit_probe_parser.add_argument("--hwnd", required=True, type=int)
    tdx_submit_probe_parser.add_argument("--post-delay", type=float, default=1.0)
    tdx_submit_probe_parser.add_argument("--max-depth", type=int, default=12)
    tdx_submit_once_parser = subparsers.add_parser("tdx-submit-once")
    tdx_submit_once_parser.add_argument("--window-key", default="通达信金融终端")
    tdx_submit_once_parser.add_argument("--hwnd", required=True, type=int)
    tdx_submit_once_parser.add_argument(
        "--strategy",
        required=True,
        choices=[
            "bm_click",
            "wm_command_parent",
            "post_wm_command_parent",
            "enter_key",
            "space_key",
            "mouse_message",
            "wm_command_ancestor_2",
            "post_wm_command_ancestor_2",
            "wm_command_ancestor_3",
            "post_wm_command_ancestor_3",
            "wm_command_ancestor_4",
            "post_wm_command_ancestor_4",
            "wm_command_ancestor_5",
            "post_wm_command_ancestor_5",
        ],
    )
    tdx_submit_once_parser.add_argument("--post-delay", type=float, default=1.0)
    tdx_submit_once_parser.add_argument("--max-depth", type=int, default=12)
    tdx_submit_once_parser.add_argument("--dialog-timeout", type=float, default=2.5)
    tdx_buy_probe_parser = subparsers.add_parser("tdx-buy-probe")
    tdx_buy_probe_parser.add_argument("--window-key", default="通达信金融终端", help="Top-level window keyword for TongDaXin")
    tdx_buy_probe_parser.add_argument("--code", required=True)
    tdx_buy_probe_parser.add_argument("--price", required=True)
    tdx_buy_probe_parser.add_argument("--quantity", required=True, type=int)
    tdx_buy_probe_parser.add_argument(
        "--code-input",
        default="set_text",
        choices=["set_text", "type_text", "keybd_event"],
    )
    tdx_buy_probe_parser.add_argument(
        "--submit-strategy",
        default="bm_click",
        choices=["bm_click", "wm_command", "enter_key"],
    )
    tdx_buy_probe_parser.add_argument(
        "--code-commit",
        default="none",
        choices=["none", "enter_key", "tab_key"],
    )
    tdx_buy_probe_parser.add_argument("--post-delay", type=float, default=1.0)
    tdx_buy_probe_parser.add_argument("--max-depth", type=int, default=12)
    tdx_buy_probe_stock_context_parser = subparsers.add_parser("tdx-buy-probe-stock-context")
    tdx_buy_probe_stock_context_parser.add_argument("--window-key", default="通达信金融终端")
    tdx_buy_probe_stock_context_parser.add_argument("--code", required=True)
    tdx_buy_probe_stock_context_parser.add_argument("--market", choices=["auto", "sh", "sz"], default="auto")
    tdx_buy_probe_stock_context_parser.add_argument("--price", required=True)
    tdx_buy_probe_stock_context_parser.add_argument("--quantity", required=True, type=int)
    tdx_buy_probe_stock_context_parser.add_argument(
        "--submit-strategy",
        default="wm_command",
        choices=["bm_click", "wm_command", "enter_key"],
    )
    tdx_buy_probe_stock_context_parser.add_argument("--post-delay", type=float, default=1.0)
    tdx_buy_probe_stock_context_parser.add_argument("--max-depth", type=int, default=12)
    tdx_hid_buy_probe_parser = subparsers.add_parser("tdx-hid-buy-probe")
    tdx_hid_buy_probe_parser.add_argument("--window-key", default="通达信金融终端")
    tdx_hid_buy_probe_parser.add_argument("--port", required=True)
    tdx_hid_buy_probe_parser.add_argument("--baudrate", type=int, default=115200)
    tdx_hid_buy_probe_parser.add_argument("--timeout", type=float, default=2.0)
    tdx_hid_buy_probe_parser.add_argument("--code", required=True)
    tdx_hid_buy_probe_parser.add_argument("--price", required=True)
    tdx_hid_buy_probe_parser.add_argument("--quantity", required=True, type=int)
    tdx_hid_buy_probe_parser.add_argument("--commit-key", choices=["none", "tab", "enter"], default="tab")
    tdx_hid_buy_probe_parser.add_argument(
        "--submit-strategy",
        default="post_wm_command_parent",
        choices=[
            "bm_click",
            "wm_command_parent",
            "post_wm_command_parent",
            "enter_key",
            "space_key",
            "mouse_message",
            "wm_command_ancestor_2",
            "post_wm_command_ancestor_2",
            "wm_command_ancestor_3",
            "post_wm_command_ancestor_3",
            "wm_command_ancestor_4",
            "post_wm_command_ancestor_4",
            "wm_command_ancestor_5",
            "post_wm_command_ancestor_5",
        ],
    )
    tdx_hid_buy_probe_parser.add_argument("--pre-clear", action="store_true")
    tdx_hid_buy_probe_parser.add_argument("--post-delay", type=float, default=1.0)
    tdx_hid_buy_probe_parser.add_argument("--max-depth", type=int, default=12)
    tdx_hid_buy_probe_parser.add_argument("--dialog-timeout", type=float, default=2.5)
    tdx_hid_buy_probe_parser.add_argument("--dry-run", action="store_true")

    buy_parser = subparsers.add_parser("buy")
    buy_parser.add_argument("--code", required=True)
    buy_parser.add_argument("--quantity", required=True, type=int)
    buy_parser.add_argument("--price")
    buy_parser.add_argument("--dry-run", action="store_true")

    for subparser in (
        health_parser,
        inspect_parser,
        uia_windows_parser,
        uia_inspect_parser,
        uia_dialogs_parser,
        uia_wait_dialog_parser,
        uia_click_parser,
        uia_click_path_parser,
        uia_click_center_parser,
        uia_activate_parser,
        uia_set_text_parser,
        uia_read_parser,
        uia_combobox_items_parser,
        uia_combobox_select_parser,
        detect_parser,
        detect_snapshot_parser,
        uia_detect_snapshot_parser,
        pingan_probe_parser,
        pingan_hid_submit_probe_parser,
        pingan_buy_submit_once_parser,
        pingan_buy_parser,
        tdx_probe_parser,
        tdx_stock_message_parser,
        tdx_bridge_health_parser,
        tdx_trade_probe_parser,
        tdx_trade_hid_ping_parser,
        tdx_trade_hid_send_parser,
        tdx_trade_buy_probe_parser,
        tdx_data_snapshot_parser,
        tdx_data_market_snapshot_parser,
        tdx_data_kline_parser,
        tdx_data_stock_info_parser,
        tdx_data_stock_list_parser,
        tdx_data_more_info_parser,
        tdx_data_cb_info_parser,
        tdx_data_gb_info_parser,
        tdx_data_gp_one_parser,
        tdx_data_divid_factors_parser,
        tdx_data_ipo_info_parser,
        tdx_data_sector_list_parser,
        tdx_data_sector_stocks_parser,
        tdx_refresh_cache_parser,
        tdx_get_trading_dates_parser,
        tdx_refresh_kline_parser,
        tdx_download_file_parser,
        tdx_get_user_sector_parser,
        tdx_create_sector_parser,
        tdx_delete_sector_parser,
        tdx_rename_sector_parser,
        tdx_clear_sector_parser,
        tdx_send_user_block_parser,
        tdx_formula_format_data_parser,
        tdx_formula_set_data_parser,
        tdx_formula_set_data_info_parser,
        tdx_formula_get_data_parser,
        tdx_formula_zb_parser,
        tdx_formula_xg_parser,
        tdx_formula_exp_parser,
        tdx_formula_mul_xg_parser,
        tdx_formula_mul_zb_parser,
        hid_ping_parser,
        hid_send_parser,
        win32_read_parser,
        win32_set_text_parser,
        win32_type_text_parser,
        win32_click_parser,
        tdx_submit_probe_parser,
        tdx_submit_once_parser,
        tdx_buy_probe_parser,
        tdx_buy_probe_stock_context_parser,
        tdx_hid_buy_probe_parser,
        buy_parser,
    ):
        subparser.add_argument("--output", help="Optional path to write the JSON result")
    return parser


def _resolve_pingan_contract_no(result: Result) -> str | None:
    return extract_pingan_contract_no(result)


def _build_pingan_last_order_state_payload(result: Result) -> dict[str, object]:
    return build_pingan_last_order_state_payload(result)


def _write_pingan_last_order_state(result: Result, state_path: Path = PINGAN_LAST_ORDER_STATE_PATH) -> Path:
    return write_pingan_last_order_state(result, state_path=state_path)


def _emit_pingan_contract_log(contract_no: str | None, stream: TextIO = sys.stderr) -> None:
    if contract_no:
        print(f"[pingan-buy-submit-once] contract_no={contract_no}", file=stream)


def _resolve_pingan_buy_profile(profile_name: str) -> dict[str, object]:
    try:
        return dict(resolve_trade_profile(profile_name))
    except ValueError as exc:
        raise ValueError(f"unsupported pingan buy profile: {profile_name}") from exc


def _build_pingan_buy_submit_options(profile_name: str, overrides: dict[str, object]) -> dict[str, object]:
    options = _resolve_pingan_buy_profile(profile_name)
    for key, value in overrides.items():
        if value is not None:
            options[key] = value
    return options


def _build_trade_command_compat_result(
    snapshot: SecurityOrderSnapshot,
    *,
    profile_name: str,
    message: str,
) -> Result:
    contract_no = snapshot.broker_order_id or snapshot.gateway_order_id
    ok, code, result_message = _resolve_order_snapshot_result(snapshot, success_message=message)
    return Result(
        ok=ok,
        code=code,
        message=result_message,
        data={
            "order": snapshot.to_dict(),
            "result_dialog": {"contract_no": contract_no},
            "execution_profile": {"name": profile_name, "options": {}},
        },
    )


def _resolve_order_snapshot_result(
    snapshot: SecurityOrderSnapshot,
    *,
    success_message: str,
) -> tuple[bool, ErrorCode, str]:
    if snapshot.status == OrderStatus.REJECTED:
        return False, ErrorCode.INVALID_REQUEST, snapshot.reject_reason or success_message
    if snapshot.status == OrderStatus.FAILED:
        return False, ErrorCode.EXECUTION_FAILED, snapshot.reject_reason or success_message
    return True, ErrorCode.OK, success_message


def _run_trade_buy(args: argparse.Namespace) -> Result:
    try:
        service = _build_trader_service(args, execution_mode="buy")
        request = SecurityOrderRequest(
            broker="pingan_desktop",
            client_order_id=str(getattr(args, "client_order_id", None) or f"trade-buy-{uuid4().hex[:12]}"),
            submission_key=args.submission_key,
            symbol=str(args.code),
            market="SZ",
            side=OrderSide.BUY,
            quantity=int(args.quantity),
            limit_price=Decimal(str(args.price)),
        )
        snapshot = service.place_order(request)
        return _build_trade_command_compat_result(snapshot, profile_name=str(args.profile), message="completed trade buy command")
    except ValueError as exc:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))
    except NotImplementedError as exc:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))
    except RuntimeError as exc:
        return Result(ok=False, code=ErrorCode.EXECUTION_FAILED, message=str(exc))


def _run_trade_submit_once(args: argparse.Namespace) -> Result:
    profile_name = getattr(args, "profile", None) or "submit_once"
    try:
        service = _build_trader_service(args, execution_mode="submit_once")
        request = SecurityOrderRequest(
            broker="pingan_desktop",
            client_order_id=str(getattr(args, "client_order_id", None) or f"trade-submit-once-{uuid4().hex[:12]}"),
            submission_key=args.submission_key,
            symbol=str(args.code),
            market="SZ",
            side=OrderSide.BUY,
            quantity=int(args.quantity),
            limit_price=Decimal(str(args.price)),
        )
        snapshot = service.place_order(request)
        return _build_trade_command_compat_result(snapshot, profile_name=str(profile_name), message="completed trade submit-once command")
    except ValueError as exc:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))
    except NotImplementedError as exc:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))
    except RuntimeError as exc:
        return Result(ok=False, code=ErrorCode.EXECUTION_FAILED, message=str(exc))


def _run_trade_health(args: argparse.Namespace) -> Result:
    trade_manager = TdxTradeManager(
        profile=getattr(args, "profile", None) or "balanced",
        title_keyword=args.title_key,
        exe_path=args.exe_path,
        state_path=str(PINGAN_LAST_ORDER_STATE_PATH),
        submission_ledger_path=str(PINGAN_SUBMISSION_LEDGER_PATH),
    )
    return trade_manager.pingan.health(
        port=args.port,
        baudrate=args.baudrate,
        timeout=args.timeout,
        pre_delay=args.pre_delay,
    )


def _run_trade_broker_capabilities(args: argparse.Namespace) -> Result:
    broker = str(getattr(args, "broker", None) or "pingan_desktop")
    if broker != "pingan_desktop":
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message=f"unsupported broker for extended broker capability probe: {broker}",
            data={"supported_brokers": ["pingan_desktop"]},
        )
    trade_manager = TdxTradeManager(
        profile=getattr(args, "profile", None) or "balanced",
        title_keyword=args.title_key,
        exe_path=args.exe_path,
    )
    return trade_manager.pingan.extended_broker_capabilities()


def _run_trade_preflight(args: argparse.Namespace) -> Result:
    trade_manager = TdxTradeManager(
        profile=getattr(args, "profile", None) or "balanced",
        title_keyword=args.title_key,
        exe_path=args.exe_path,
        state_path=str(PINGAN_LAST_ORDER_STATE_PATH),
        submission_ledger_path=str(PINGAN_SUBMISSION_LEDGER_PATH),
    )
    return trade_manager.pingan.preflight(
        port=args.port,
        baudrate=args.baudrate,
        timeout=args.timeout,
        pre_delay=args.pre_delay,
        code=args.code,
        price=args.price,
        quantity=args.quantity,
        submission_key=args.submission_key,
        max_price=args.max_price,
    )


def _run_trade_submit_ready(args: argparse.Namespace) -> Result:
    trade_manager = TdxTradeManager(
        profile=getattr(args, "profile", None) or "balanced",
        title_keyword=args.title_key,
        exe_path=args.exe_path,
        state_path=str(PINGAN_LAST_ORDER_STATE_PATH),
        submission_ledger_path=str(PINGAN_SUBMISSION_LEDGER_PATH),
    )
    return trade_manager.pingan.submit_ready(
        port=args.port,
        baudrate=args.baudrate,
        timeout=args.timeout,
        code=args.code,
        price=args.price,
        quantity=args.quantity,
        max_depth=args.max_depth,
        max_price=args.max_price,
        dialog_lookup_mode=args.dialog_lookup_mode,
        confirm_timeout=args.confirm_timeout,
    )


def _run_trade_confirm_current(args: argparse.Namespace) -> Result:
    trade_manager = TdxTradeManager(
        profile=getattr(args, "profile", None) or "balanced",
        title_keyword=args.title_key,
        exe_path=args.exe_path,
        state_path=str(PINGAN_LAST_ORDER_STATE_PATH),
        submission_ledger_path=str(PINGAN_SUBMISSION_LEDGER_PATH),
    )
    kwargs: dict[str, Any] = {
        "dialog_lookup_mode": args.dialog_lookup_mode,
        "confirm_timeout": args.confirm_timeout,
        "result_timeout": args.result_timeout,
        "close_result_dialog": args.close_result_dialog,
    }
    if args.result_close_pre_delay is not None:
        kwargs["result_close_pre_delay"] = args.result_close_pre_delay
    return trade_manager.pingan.confirm_current(**kwargs)


def _run_trade_dialog_readiness(args: argparse.Namespace) -> Result:
    trade_manager = TdxTradeManager(
        profile=getattr(args, "profile", None) or "balanced",
        title_keyword=args.title_key,
        exe_path=args.exe_path,
        state_path=str(PINGAN_LAST_ORDER_STATE_PATH),
        submission_ledger_path=str(PINGAN_SUBMISSION_LEDGER_PATH),
    )
    return trade_manager.pingan.dialog_readiness(
        dialog=args.dialog,
        require_visible=args.require_visible,
        dialog_lookup_mode=args.dialog_lookup_mode,
        confirm_timeout=args.confirm_timeout,
        result_timeout=args.result_timeout,
    )


def _build_trader_service(args: argparse.Namespace, *, execution_mode: str = "buy") -> TradeService:
    broker = getattr(args, "broker", None) or "pingan_desktop"
    registry = TraderGatewayRegistry()
    if broker != "pingan_desktop":
        raise ValueError(f"unsupported trader broker: {broker}")
    registry.register(
        broker,
        PingAnDesktopTraderGateway(
            execution_mode=execution_mode,
            port=getattr(args, "port", None),
            baudrate=int(getattr(args, "baudrate", 115200) or 115200),
            timeout=float(getattr(args, "timeout", 2.0) or 2.0),
            max_depth=int(getattr(args, "max_depth", 12) or 12),
            close_result_dialog=bool(getattr(args, "close_result_dialog", True)),
            profile=str(getattr(args, "profile", "balanced") or "balanced"),
            title_keyword=str(getattr(args, "title_key", "平安证券")),
            exe_path=getattr(args, "exe_path", None),
            max_price=getattr(args, "max_price", None),
        ),
    )
    store_dir = Path(getattr(args, "store_dir", None) or TRADER_RUNTIME_DIR)
    return TradeService(registry=registry, store=TraderStore(store_dir))


def _run_trade_order_place(args: argparse.Namespace) -> Result:
    try:
        service = _build_trader_service(args)
        request = SecurityOrderRequest(
            broker=str(args.broker),
            client_order_id=str(args.client_order_id or f"{args.broker}-{uuid4().hex[:12]}"),
            submission_key=args.submission_key,
            symbol=str(args.code),
            market=str(args.market).upper(),
            side=OrderSide(str(args.side).lower()),
            quantity=int(args.quantity),
            limit_price=Decimal(str(args.price)),
        )
        snapshot = service.place_order(request)
        ok, code, message = _resolve_order_snapshot_result(snapshot, success_message="completed trade order-place command")
        return Result(
            ok=ok,
            code=code,
            message=message,
            data={"order": snapshot.to_dict()},
        )
    except ValueError as exc:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))
    except NotImplementedError as exc:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))
    except RuntimeError as exc:
        return Result(ok=False, code=ErrorCode.EXECUTION_FAILED, message=str(exc))


def _run_trade_order_query(args: argparse.Namespace) -> Result:
    try:
        service = _build_trader_service(args)
    except ValueError as exc:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))
    order = service.query_order(args.gateway_order_id)
    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="completed trade order-query command",
        data={"order": None if order is None else order.to_dict()},
    )


def _run_trade_trade_query(args: argparse.Namespace) -> Result:
    try:
        service = _build_trader_service(args)
    except ValueError as exc:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))
    trades = service.query_trades()
    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="completed trade trade-query command",
        data={"trades": [trade.to_dict() for trade in trades]},
    )


def _build_trade_preset_namespace(args: argparse.Namespace) -> argparse.Namespace:
    resolved_preset = resolve_trade_preset(args.preset)
    command_name = str(resolved_preset.get("command", "")).strip()
    if command_name not in TRADE_COMMAND_DEFAULT_PROFILES:
        raise ValueError(f"unsupported trade preset command: {command_name}")

    merged = dict(vars(args))
    for key, value in resolved_preset.get("options", {}).items():
        if key not in merged or merged.get(key) is None:
            merged[key] = value
    if merged.get("profile") is None:
        merged["profile"] = resolved_preset.get("profile") or TRADE_COMMAND_DEFAULT_PROFILES.get(command_name)
    if merged.get("exe_path") is None:
        merged["exe_path"] = resolved_preset.get("exe_path")
    if merged.get("title_key") == "平安证券" and resolved_preset.get("title_key"):
        merged["title_key"] = resolved_preset.get("title_key")

    merged["baudrate"] = 115200 if merged.get("baudrate") is None else merged["baudrate"]
    merged["timeout"] = 2.0 if merged.get("timeout") is None else merged["timeout"]
    merged["max_depth"] = 12 if merged.get("max_depth") is None else merged["max_depth"]
    merged["close_result_dialog"] = True if merged.get("close_result_dialog") is None else merged["close_result_dialog"]
    merged["trade_command"] = command_name

    missing_required = [name for name in ("port", "code", "price", "quantity") if merged.get(name) is None]
    if missing_required:
        joined = ", ".join(missing_required)
        raise ValueError(f"trade preset execution requires: {joined}")
    return argparse.Namespace(**merged)


def _list_trade_presets(args: argparse.Namespace) -> Result:
    presets = load_trade_presets()
    if args.preset:
        filtered_items = [(name, value) for name, value in presets.items() if name == args.preset]
    else:
        filtered_items = sorted(presets.items(), key=lambda item: item[0])
    preset_rows = []
    for name, value in filtered_items:
        resolved = resolve_trade_preset(name, presets=presets)
        preset_rows.append(
            {
                "name": name,
                "command": resolved.get("command"),
                "profile": resolved.get("profile"),
                "title_key": resolved.get("title_key"),
                "exe_path": resolved.get("exe_path"),
                "description": resolved.get("description"),
                "options": resolved.get("options"),
            }
        )
    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="listed trade presets",
        data={
            "summary": {
                "preset_count": len(preset_rows),
                "selected_preset": args.preset,
            },
            "presets": preset_rows,
        },
    )


def _resolve_catalog_preset_metadata(source: str, preset_name: str) -> dict[str, object]:
    if source == "report":
        return resolve_report_preset(preset_name)
    if source == "trade":
        return resolve_trade_preset(preset_name)
    if source == "task":
        return resolve_task_preset(preset_name)
    raise ValueError(f"unsupported catalog source: {source}")


def _build_catalog_dispatch_namespace(args: argparse.Namespace, *, source: str, preset_name: str) -> argparse.Namespace:
    merged = dict(vars(args))
    merged["preset"] = preset_name
    if source == "report":
        merged["command"] = "report"
        merged["report_command"] = "run"
        return argparse.Namespace(**merged)
    if source == "trade":
        merged["command"] = "trade"
        merged["trade_command"] = "run"
        return argparse.Namespace(**merged)
    if source == "task":
        merged["command"] = "task"
        merged["task_command"] = "run"
        return argparse.Namespace(**merged)
    raise ValueError(f"unsupported catalog source: {source}")


def _dispatch_catalog_resolved_entry(args: argparse.Namespace, *, entry_name: str, source: str, preset_name: str) -> Result:
    forwarded = _build_catalog_dispatch_namespace(args, source=source, preset_name=preset_name)
    if source == "report":
        result = _handle_report_subcommand(forwarded)
    elif source == "trade":
        result = _handle_trade_subcommand(forwarded)
    elif source == "task":
        result = _handle_task_subcommand(forwarded)
    else:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=f"unsupported catalog source: {source}")
    result.data.setdefault(
        "catalog_entry",
        {
            "name": entry_name,
            "source": source,
            "preset": preset_name,
        },
    )
    return result


def _build_catalog_bundle_step_namespace(args: argparse.Namespace, *, step: dict[str, object]) -> argparse.Namespace:
    merged = dict(vars(args))
    for key, value in dict(step.get("options", {})).items():
        if key not in merged or merged.get(key) is None:
            merged[key] = value
    # Bundle-level output writes the aggregate result only.
    merged["output"] = None
    return argparse.Namespace(**merged)


def _serialize_catalog_value(value: object) -> object:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, list):
        return [_serialize_catalog_value(item) for item in value]
    if isinstance(value, tuple):
        return [_serialize_catalog_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _serialize_catalog_value(item) for key, item in value.items()}
    return str(value)


def _serialize_catalog_namespace(args: argparse.Namespace) -> dict[str, object]:
    return {key: _serialize_catalog_value(value) for key, value in vars(args).items()}


def _extract_catalog_key_fields(payload: dict[str, object]) -> dict[str, object]:
    keys = (
        "block_code",
        "code",
        "price",
        "quantity",
        "port",
        "profile",
        "api_profile",
        "trade_profile",
        "date",
        "start_date",
        "end_date",
        "timezone",
        "limit",
        "recent_limit",
        "contract_no",
        "market",
        "force",
        "refresh_before_trade",
        "refresh_market",
        "formula_name",
    )
    return {key: payload[key] for key in keys if key in payload and payload[key] is not None}


def _count_catalog_labels(row: dict[str, object]) -> int:
    labels = row.get("labels")
    if isinstance(labels, (list, tuple, set)):
        return len(labels)
    return 0


def _collect_catalog_labels(rows: list[dict[str, object]]) -> list[str]:
    labels: set[str] = set()
    for row in rows:
        raw_labels = row.get("labels")
        if not isinstance(raw_labels, list):
            continue
        for label in raw_labels:
            if isinstance(label, str) and label:
                labels.add(label)
    return sorted(labels)


def _sort_catalog_named_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(rows, key=lambda row: (-_count_catalog_labels(row), str(row.get("name", ""))))


def _build_catalog_summary_view(args: argparse.Namespace, result: Result) -> dict[str, object] | None:
    if args.catalog_command == "list":
        summary_payload = result.data.get("summary", {})
        if not isinstance(summary_payload, dict):
            return None
        entry_summaries: list[dict[str, object]] = []
        entries = result.data.get("entries", [])
        if isinstance(entries, list):
            for row in entries:
                if not isinstance(row, dict):
                    continue
                entry_summaries.append(
                    {
                        "name": row.get("name"),
                        "source": row.get("source"),
                        "command": row.get("command"),
                        "labels": copy.deepcopy(row.get("labels")),
                        "description": row.get("description"),
                    }
                )
        bundle_summaries: list[dict[str, object]] = []
        bundles = result.data.get("bundles", [])
        if isinstance(bundles, list):
            for row in bundles:
                if not isinstance(row, dict):
                    continue
                step_names: list[object] = []
                steps = row.get("steps", [])
                if isinstance(steps, list):
                    step_names = [
                        step.get("name")
                        for step in steps
                        if isinstance(step, dict) and step.get("name") is not None
                    ]
                bundle_summaries.append(
                    {
                        "name": row.get("name"),
                        "labels": copy.deepcopy(row.get("labels")),
                        "step_count": row.get("step_count"),
                        "step_names": step_names,
                        "description": row.get("description"),
                    }
                )
        return {
            "mode": "list",
            "kind": summary_payload.get("kind"),
            "selected_entry": summary_payload.get("selected_entry"),
            "selected_bundle": summary_payload.get("selected_bundle"),
            "selected_label": summary_payload.get("selected_label"),
            "entry_count": summary_payload.get("entry_count"),
            "bundle_count": summary_payload.get("bundle_count"),
            "matched_entry_count": summary_payload.get("matched_entry_count"),
            "matched_bundle_count": summary_payload.get("matched_bundle_count"),
            "available_entry_labels": copy.deepcopy(summary_payload.get("available_entry_labels")),
            "available_bundle_labels": copy.deepcopy(summary_payload.get("available_bundle_labels")),
            "entries": entry_summaries,
            "bundles": bundle_summaries,
        }

    if args.catalog_command not in {"run", "plan", "preview"}:
        return None

    mode = args.catalog_command
    if "catalog_entry" in result.data:
        entry_meta = dict(result.data["catalog_entry"])
        summary: dict[str, object] = {
            "mode": mode,
            "target": {
                "type": "entry",
                "name": entry_meta.get("name"),
                "source": entry_meta.get("source"),
                "preset": entry_meta.get("preset"),
            },
            "ok": result.ok,
            "code": result.code.value,
            "message": result.message,
        }
        if "dispatch" in result.data:
            summary["dispatch"] = copy.deepcopy(result.data["dispatch"])
        if mode in {"plan", "preview"}:
            resolved_args = result.data.get("resolved_args", {})
            if isinstance(resolved_args, dict):
                summary["resolved_args"] = _extract_catalog_key_fields(resolved_args)
        else:
            input_payload = result.data.get("input", {})
            if isinstance(input_payload, dict):
                key_input = _extract_catalog_key_fields(input_payload)
                if key_input:
                    summary["input"] = key_input
            contract_no = _resolve_pingan_contract_no(result)
            if contract_no is not None:
                summary["contract_no"] = contract_no
        return summary

    if "catalog_bundle" in result.data:
        bundle_meta = dict(result.data["catalog_bundle"])
        summary = {
            "mode": mode,
            "target": {
                "type": "bundle",
                "name": bundle_meta.get("name"),
            },
            "ok": result.ok,
            "code": result.code.value,
            "message": result.message,
            "selected_from_step": bundle_meta.get("selected_from_step"),
            "selected_to_step": bundle_meta.get("selected_to_step"),
            "selected_step_count": bundle_meta.get("selected_step_count"),
        }
        if mode in {"plan", "preview"}:
            plan_steps: list[dict[str, object]] = []
            steps = result.data.get("steps", [])
            if isinstance(steps, list):
                for step in steps:
                    if not isinstance(step, dict):
                        continue
                    step_view = {
                        "index": step.get("index"),
                        "name": step.get("name"),
                        "entry": step.get("entry"),
                    }
                    if isinstance(step.get("dispatch"), dict):
                        step_view["dispatch"] = copy.deepcopy(step["dispatch"])
                    if isinstance(step.get("resolved_args"), dict):
                        step_view["resolved_args"] = _extract_catalog_key_fields(step["resolved_args"])
                    plan_steps.append(step_view)
            summary["steps"] = plan_steps
        else:
            run_steps: list[dict[str, object]] = []
            steps = bundle_meta.get("steps", [])
            if isinstance(steps, list):
                for step in steps:
                    if not isinstance(step, dict):
                        continue
                    run_steps.append(
                        {
                            "index": step.get("index"),
                            "name": step.get("name"),
                            "entry": step.get("entry"),
                            "ok": step.get("ok"),
                            "code": step.get("code"),
                            "message": step.get("message"),
                        }
                    )
            summary["steps"] = run_steps
            if bundle_meta.get("trade_contract_no") is not None:
                summary["trade_contract_no"] = bundle_meta.get("trade_contract_no")
        return summary

    return None


def _select_catalog_output_payload(args: argparse.Namespace, result: Result) -> dict[str, object]:
    if (
        args.command == "catalog"
        and getattr(args, "view", "detailed") == "summary"
        and isinstance(result.data.get("summary_view"), dict)
    ):
        return copy.deepcopy(result.data["summary_view"])
    return result.to_dict()


_FLAT_PROVIDER_RESULT_COMMANDS = {
    "tdx-capabilities",
    "tdx-health",
    "tdx-doctor",
    "tdx-data-snapshot",
    "tdx-data-stock-info",
    "tdx-data-kline",
    "tdx-data-sector-list",
    "tdx-data-sector-stocks",
    "tdx-data-divid-factors",
    "tdx-data-ipo-info",
    "tdx-data-financial",
    "tdx-data-financial-by-date",
    "tdx-data-stock-transaction",
    "tdx-data-stock-transaction-by-date",
    "tdx-data-sector-transaction",
    "tdx-data-sector-transaction-by-date",
    "tdx-data-market-transaction",
    "tdx-data-market-transaction-by-date",
    "tdx-refresh-cache",
    "tdx-get-trading-dates",
    "tdx-refresh-kline",
    "tdx-download-file",
    "tdx-send-warn",
    "tdx-get-user-sector",
    "tdx-create-sector",
    "tdx-delete-sector",
    "tdx-rename-sector",
    "tdx-clear-sector",
    "tdx-send-user-block",
    "tdx-block-read-watchlist",
    "tdx-formula-format-data",
    "tdx-formula-set-data",
    "tdx-formula-set-data-info",
    "tdx-formula-get-data",
    "tdx-formula-zb",
    "tdx-formula-xg",
    "tdx-formula-screen",
    "tdx-formula-exp",
    "tdx-formula-mul-xg",
    "tdx-formula-mul-zb",
}


def _uses_provider_result_contract(args: argparse.Namespace) -> bool:
    if args.command == "api":
        return True
    return args.command in _FLAT_PROVIDER_RESULT_COMMANDS


def _resolve_provider_result_capability(args: argparse.Namespace) -> str:
    if args.command == "api" and args.api_command == "formula-screen":
        return "formula.screen"
    if args.command == "api" and args.api_command == "block-read-watchlist":
        return "block.read_watchlist_snapshot"
    if args.command == "tdx-formula-screen":
        return "formula.screen"
    if args.command == "tdx-block-read-watchlist":
        return "block.read_watchlist_snapshot"
    if args.command == "api":
        return f"api.{args.api_command}"
    if args.command.startswith("tdx-data-"):
        return f"bridge.{args.command[len('tdx-data-'):]}"
    if args.command.startswith("tdx-"):
        return f"bridge.{args.command[len('tdx-'):]}"
    return args.command


def _build_provider_result_payload(
    args: argparse.Namespace,
    result: Result,
    *,
    started_at: str,
    finished_at: str,
    elapsed_ms: float,
) -> dict[str, object]:
    return result.to_provider_dict(
        capability=_resolve_provider_result_capability(args),
        capability_version=DEFAULT_CAPABILITY_VERSION,
        schema_version=DEFAULT_SCHEMA_VERSION,
        started_at=started_at,
        finished_at=finished_at,
        elapsed_ms=elapsed_ms,
        runtime=build_runtime_metadata(mode="cli"),
    )


_SUPPORTED_API_REPLAY_COMMANDS = {
    "capabilities",
    "health",
    "doctor",
    "formula-screen",
    "send-user-block",
    "block-read-watchlist",
}

_API_REPLAY_CAPABILITIES = {
    "snapshot": "market.snapshot",
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


def _run_flat_replay_provider_command(args: argparse.Namespace) -> Result | None:
    if getattr(args, "provider_mode", "live") != "replay":
        return None
    try:
        manager = TdxApiManager(
            profile="default",
            strategy_path=getattr(args, "strategy_path", None),
            provider_mode="replay",
            replay_fixture=getattr(args, "fixture", None),
            replay_fixture_path=getattr(args, "fixture_path", None),
        )
    except ValueError as exc:
        return _build_cli_replay_failure_result(capability=str(args.command), message=str(exc))

    if args.command == "tdx-capabilities":
        return manager.runtime.capabilities()
    if args.command == "tdx-health":
        return manager.runtime.health(window_key=args.window_key, hid_port=args.hid_port)
    if args.command == "tdx-doctor":
        return manager.runtime.doctor(window_key=args.window_key, hid_port=args.hid_port)
    if args.command == "tdx-send-user-block":
        return manager.block.send_user_block(
            block_code=args.block_code,
            stocks=args.stock,
            show=args.show,
            mutation_key=args.mutation_key,
            audit_dir=args.audit_dir,
        )
    if args.command == "tdx-block-read-watchlist":
        return manager.block.read_watchlist_snapshot(block_code=args.block_code)
    if args.command == "tdx-formula-screen":
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
    return _build_cli_replay_failure_result(
        capability=str(args.command),
        message=f"unsupported replay flat command: {args.command}",
    )


def _build_catalog_resolved_execution_namespace(
    args: argparse.Namespace,
    *,
    source: str,
    preset_name: str,
) -> argparse.Namespace:
    forwarded = _build_catalog_dispatch_namespace(args, source=source, preset_name=preset_name)
    if source == "report":
        return _build_report_preset_namespace(forwarded)
    if source == "trade":
        return _build_trade_preset_namespace(forwarded)
    if source == "task":
        return _build_task_preset_namespace(forwarded)
    raise ValueError(f"unsupported catalog source: {source}")


def _plan_catalog_resolved_entry(
    args: argparse.Namespace,
    *,
    entry_name: str,
    source: str,
    preset_name: str,
) -> Result:
    resolved_args = _build_catalog_resolved_execution_namespace(args, source=source, preset_name=preset_name)
    command_name_key = f"{source}_command"
    result = Result(
        ok=True,
        code=ErrorCode.OK,
        message="planned command catalog entry",
        data={
            "mode": args.catalog_command,
            "catalog_entry": {
                "name": entry_name,
                "source": source,
                "preset": preset_name,
            },
            "dispatch": {
                "source": source,
                "preset": preset_name,
                "command_group": source,
                "command_name": getattr(resolved_args, command_name_key, None),
            },
            "resolved_args": _serialize_catalog_namespace(resolved_args),
        },
    )
    result.data["summary_view"] = _build_catalog_summary_view(args, result)
    return result


def _plan_catalog_bundle(args: argparse.Namespace) -> Result:
    resolved_bundle = resolve_command_bundle(args.bundle)
    selected_range = resolve_command_bundle_step_range(
        resolved_bundle,
        only_step=getattr(args, "only_step", None),
        from_step=getattr(args, "from_step", None),
        to_step=getattr(args, "to_step", None),
    )
    step_rows: list[dict[str, object]] = []
    for step in selected_range["steps"]:
        step_args = _build_catalog_bundle_step_namespace(args, step=step)
        resolved_args = _build_catalog_resolved_execution_namespace(
            step_args,
            source=str(step["source"]),
            preset_name=str(step["preset"]),
        )
        command_name_key = f"{step['source']}_command"
        step_rows.append(
            {
                "index": step["index"],
                "name": step["name"],
                "entry": step["entry"],
                "dispatch": {
                    "source": step["source"],
                    "preset": step["preset"],
                    "command_group": step["source"],
                    "command_name": getattr(resolved_args, command_name_key, None),
                },
                "resolved_args": _serialize_catalog_namespace(resolved_args),
            }
        )
    result = Result(
        ok=True,
        code=ErrorCode.OK,
        message="planned command catalog bundle",
        data={
            "mode": args.catalog_command,
            "catalog_bundle": {
                "name": args.bundle,
                "description": resolved_bundle["description"],
                "step_count": len(resolved_bundle["steps"]),
                "selected_from_step": selected_range["start_name"],
                "selected_to_step": selected_range["end_name"],
                "selected_step_count": len(selected_range["steps"]),
            },
            "steps": step_rows,
        },
    )
    result.data["summary_view"] = _build_catalog_summary_view(args, result)
    return result


def _list_catalog_entries(args: argparse.Namespace) -> Result:
    entries = load_command_catalog()
    selected_entry = getattr(args, "entry", None)
    selected_bundle = getattr(args, "bundle", None)
    selected_label = getattr(args, "label", None)
    effective_kind = args.kind
    if selected_bundle:
        effective_kind = "bundle"
    elif selected_entry:
        effective_kind = "entry"

    if selected_entry:
        filtered_items = [(name, value) for name, value in entries.items() if name == args.entry]
    elif effective_kind in {"entry", "all"}:
        filtered_items = sorted(entries.items(), key=lambda item: item[0])
    else:
        filtered_items = []

    available_entry_rows: list[dict[str, object]] = []
    for name, _value in sorted(entries.items(), key=lambda item: item[0]):
        resolved = resolve_command_catalog_entry(name, entries=entries)
        mapped = _resolve_catalog_preset_metadata(resolved["source"], resolved["preset"])
        available_entry_rows.append(
            {
                "name": name,
                "source": resolved["source"],
                "preset": resolved["preset"],
                "labels": resolved["labels"],
                "command": mapped.get("command"),
                "description": resolved["description"] or mapped.get("description"),
            }
        )

    entry_rows = []
    for name, _value in filtered_items:
        resolved = resolve_command_catalog_entry(name, entries=entries)
        if selected_label and selected_label not in resolved["labels"]:
            continue
        mapped = _resolve_catalog_preset_metadata(resolved["source"], resolved["preset"])
        entry_rows.append(
            {
                "name": name,
                "source": resolved["source"],
                "preset": resolved["preset"],
                "labels": resolved["labels"],
                "command": mapped.get("command"),
                "profile": mapped.get("profile"),
                "api_profile": mapped.get("api_profile"),
                "trade_profile": mapped.get("trade_profile"),
                "title_key": mapped.get("title_key"),
                "exe_path": mapped.get("exe_path"),
                "description": resolved["description"] or mapped.get("description"),
                "options": mapped.get("options"),
            }
        )
    entry_rows = _sort_catalog_named_rows(entry_rows)

    bundle_rows = []
    available_bundle_rows: list[dict[str, object]] = []
    if effective_kind in {"bundle", "all"}:
        bundles = load_command_bundles()
        for name, _value in sorted(bundles.items(), key=lambda item: item[0]):
            resolved_bundle = resolve_command_bundle(name, bundles=bundles, entries=entries)
            available_bundle_rows.append(
                {
                    "name": name,
                    "description": resolved_bundle["description"],
                    "labels": resolved_bundle["labels"],
                    "step_count": len(resolved_bundle["steps"]),
                }
            )
        if selected_bundle:
            filtered_bundle_items = [(name, value) for name, value in bundles.items() if name == selected_bundle]
        else:
            filtered_bundle_items = sorted(bundles.items(), key=lambda item: item[0])
        for name, _value in filtered_bundle_items:
            resolved_bundle = resolve_command_bundle(name, bundles=bundles, entries=entries)
            if selected_label and selected_label not in resolved_bundle["labels"]:
                continue
            step_rows = []
            for step in resolved_bundle["steps"]:
                mapped = _resolve_catalog_preset_metadata(step["source"], step["preset"])
                step_rows.append(
                    {
                        "index": step["index"],
                        "name": step["name"],
                        "entry": step["entry"],
                        "source": step["source"],
                        "preset": step["preset"],
                        "command": mapped.get("command"),
                        "profile": mapped.get("profile"),
                        "api_profile": mapped.get("api_profile"),
                        "trade_profile": mapped.get("trade_profile"),
                        "title_key": mapped.get("title_key"),
                        "exe_path": mapped.get("exe_path"),
                        "description": step["description"] or mapped.get("description"),
                        "options": step["options"],
                    }
                )
            bundle_rows.append(
                {
                    "name": name,
                    "description": resolved_bundle["description"],
                    "labels": resolved_bundle["labels"],
                    "step_count": len(step_rows),
                    "steps": step_rows,
                }
            )
    bundle_rows = _sort_catalog_named_rows(bundle_rows)
    available_entry_labels = _collect_catalog_labels(available_entry_rows)
    available_bundle_labels = _collect_catalog_labels(available_bundle_rows)
    discovery = {
        "selected_label": selected_label,
        "available_entry_labels": available_entry_labels,
        "available_bundle_labels": available_bundle_labels,
        "matched_entry_count": len(entry_rows),
        "matched_bundle_count": len(bundle_rows),
    }

    result = Result(
        ok=True,
        code=ErrorCode.OK,
        message="listed command catalog entries",
        data={
            "summary": {
                "kind": effective_kind,
                "entry_count": len(entry_rows),
                "matched_entry_count": len(entry_rows),
                "selected_entry": selected_entry,
                "bundle_count": len(bundle_rows),
                "matched_bundle_count": len(bundle_rows),
                "selected_bundle": selected_bundle,
                "selected_label": selected_label,
                "available_entry_labels": available_entry_labels,
                "available_bundle_labels": available_bundle_labels,
            },
            "discovery": discovery,
            "entries": entry_rows,
            "bundles": bundle_rows,
        },
    )
    result.data["summary_view"] = _build_catalog_summary_view(args, result)
    return result


def _run_catalog_bundle(args: argparse.Namespace) -> Result:
    try:
        resolved_bundle = resolve_command_bundle(args.bundle)
        selected_range = resolve_command_bundle_step_range(
            resolved_bundle,
            only_step=getattr(args, "only_step", None),
            from_step=getattr(args, "from_step", None),
            to_step=getattr(args, "to_step", None),
        )
    except ValueError as exc:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))

    bundle_started_at = time.perf_counter()
    step_rows: list[dict[str, object]] = []
    warnings: list[str] = []
    failed_step: dict[str, object] | None = None
    failed_result: Result | None = None
    trade_contract_no: str | None = None
    trade_result_dialog: dict[str, object] | None = None
    trade_input: dict[str, object] | None = None
    contains_trade_step = False

    for step in selected_range["steps"]:
        step_args = _build_catalog_bundle_step_namespace(args, step=step)
        step_result = _dispatch_catalog_resolved_entry(
            args=step_args,
            entry_name=str(step["entry"]),
            source=str(step["source"]),
            preset_name=str(step["preset"]),
        )
        contains_trade_step = contains_trade_step or bool(step_result.data.get("result_dialog")) or str(step["source"]) == "trade"
        contract_no = _resolve_pingan_contract_no(step_result)
        if trade_contract_no is None and contract_no:
            trade_contract_no = contract_no
            if isinstance(step_result.data.get("result_dialog"), dict):
                trade_result_dialog = copy.deepcopy(step_result.data["result_dialog"])
            if isinstance(step_result.data.get("input"), dict):
                trade_input = copy.deepcopy(step_result.data["input"])
        warnings.extend(step_result.warnings)
        step_view = {
            "index": step["index"],
            "name": step["name"],
            "entry": step["entry"],
            "source": step["source"],
            "preset": step["preset"],
            "description": step["description"],
            "ok": step_result.ok,
            "code": step_result.code.value,
            "message": step_result.message,
            "result": step_result.to_dict(),
        }
        step_rows.append(step_view)
        if not step_result.ok:
            failed_step = step_view
            failed_result = step_result
            break

    total_ms = round((time.perf_counter() - bundle_started_at) * 1000, 3)
    data: dict[str, object] = {
        "catalog_bundle": {
            "name": args.bundle,
            "description": resolved_bundle["description"],
            "step_count": len(resolved_bundle["steps"]),
            "selected_from_step": selected_range["start_name"],
            "selected_to_step": selected_range["end_name"],
            "selected_step_count": len(selected_range["steps"]),
            "executed_step_count": len(step_rows),
            "completed_step_count": sum(1 for row in step_rows if row["ok"]),
            "contains_trade_step": contains_trade_step,
            "trade_contract_no": trade_contract_no,
            "steps": step_rows,
            "failed_step": failed_step,
        },
        "timing": {
            "catalog_bundle": {
                "name": args.bundle,
                "total_ms": total_ms,
                "selected_step_count": len(selected_range["steps"]),
            }
        },
    }
    if trade_result_dialog is not None:
        data["result_dialog"] = trade_result_dialog
    if trade_input is not None:
        data["input"] = trade_input

    if failed_result is not None:
        return Result(
            ok=False,
            code=failed_result.code,
            message=f"command catalog bundle failed at step {failed_step['index']}: {failed_step['entry']}",
            data=data,
            warnings=warnings,
            next_action=failed_result.next_action,
        )

    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="executed command catalog bundle",
        data=data,
        warnings=warnings,
    )


def _handle_api_subcommand(args: argparse.Namespace) -> Result:
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
        manager = TdxApiManager(**manager_kwargs)
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
            create_if_missing=args.create_if_missing,
            dry_run=args.dry_run,
            show=args.show,
            **options,
        )
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
    return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=f"unsupported api subcommand: {args.api_command}")


def _build_task_manager(args: argparse.Namespace) -> TdxTaskManager:
    manager_kwargs: dict[str, object] = {
        "profile": args.profile,
        "api_profile": getattr(args, "api_profile", None),
        "trade_profile": getattr(args, "trade_profile", None),
        "strategy_path": getattr(args, "strategy_path", None),
        "title_keyword": args.title_key,
        "exe_path": args.exe_path,
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
    return TdxTaskManager(**manager_kwargs)


def _dispatch_report_workflow(manager: TdxTaskManager, args: argparse.Namespace, command_name: str) -> Result | None:
    status = getattr(args, "status", None)
    if isinstance(status, str):
        status = status.strip() or None
    raw_statuses = getattr(args, "statuses", None)
    statuses = None
    if raw_statuses is not None:
        normalized_statuses = [str(item).strip() for item in raw_statuses if str(item).strip()]
        if normalized_statuses:
            statuses = normalized_statuses
    if status is not None and statuses is not None and command_name in {
        "trade-audit-daily-report",
        "audit-daily",
        "trade-audit-period-report",
        "audit-period",
    }:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="status and statuses cannot be used together",
        )
    method = getattr(args, "method", None)
    if isinstance(method, str):
        method = method.strip() or None
    raw_methods = getattr(args, "methods", None)
    methods = None
    if raw_methods is not None:
        normalized_methods = [str(item).strip() for item in raw_methods if str(item).strip()]
        if normalized_methods:
            methods = normalized_methods
    if method is not None and methods is not None and command_name in {
        "trade-audit-daily-report",
        "audit-daily",
        "trade-audit-period-report",
        "audit-period",
    }:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="method and methods cannot be used together",
        )

    if command_name in {"ledger-summary", "ledger"}:
        return manager.ledger_summary(
            limit=args.limit,
            code=args.code,
            contract_no=args.contract_no,
            trade_ok=args.trade_ok,
            task_name=args.task_name,
            ledger_jsonl_path=args.ledger_jsonl_path,
            ledger_csv_path=args.ledger_csv_path,
            json_output_path=args.json_output_path,
            csv_output_path=args.csv_output_path,
        )
    if command_name in {"daily-trade-report", "daily"}:
        return manager.daily_trade_report(
            report_date=args.date,
            timezone_name=args.timezone,
            recent_limit=args.recent_limit,
            code=args.code,
            trade_ok=args.trade_ok,
            task_name=args.task_name,
            ledger_jsonl_path=args.ledger_jsonl_path,
            ledger_csv_path=args.ledger_csv_path,
            json_output_path=args.json_output_path,
            csv_output_path=args.csv_output_path,
        )
    if command_name in {"trade-report-lookup", "lookup"}:
        return manager.trade_report_lookup(
            contract_no=args.contract_no,
            code=args.code,
            report_date=args.date,
            timezone_name=args.timezone,
            limit=args.limit,
            trade_ok=args.trade_ok,
            task_name=args.task_name,
            ledger_jsonl_path=args.ledger_jsonl_path,
            ledger_csv_path=args.ledger_csv_path,
            json_output_path=args.json_output_path,
            csv_output_path=args.csv_output_path,
        )
    if command_name in {"trade-audit-lookup", "audit-lookup"}:
        return manager.trade_audit_lookup(
            audit_id=args.audit_id,
            contract_no=args.contract_no,
            submission_key=args.submission_key,
            code=args.code,
            status=status,
            limit=args.limit,
            audit_dir=args.audit_dir,
            json_output_path=args.json_output_path,
            csv_output_path=args.csv_output_path,
        )
    if command_name in {"trade-audit-daily-report", "audit-daily"}:
        daily_kwargs = dict(
            report_date=args.date,
            timezone_name=args.timezone,
            recent_limit=args.recent_limit,
            code=args.code,
            status=status,
            statuses=statuses,
            method=method,
            broker=getattr(args, "broker", None),
            submission_key=getattr(args, "submission_key", None),
            audit_dir=getattr(args, "audit_dir", None),
            json_output_path=args.json_output_path,
            csv_output_path=args.csv_output_path,
        )
        if methods is not None:
            daily_kwargs["methods"] = methods
        return manager.trade_audit_daily_report(**daily_kwargs)
    if command_name in {"trade-audit-period-report", "audit-period"}:
        period_kwargs = dict(
            start_date=args.start_date,
            end_date=args.end_date,
            timezone_name=args.timezone,
            recent_limit=args.recent_limit,
            code=args.code,
            status=status,
            statuses=statuses,
            method=method,
            broker=getattr(args, "broker", None),
            submission_key=getattr(args, "submission_key", None),
            audit_dir=getattr(args, "audit_dir", None),
            json_output_path=args.json_output_path,
            csv_output_path=args.csv_output_path,
        )
        if methods is not None:
            period_kwargs["methods"] = methods
        return manager.trade_audit_period_report(**period_kwargs)
    if command_name == "trade-audit-cross-ledger-query":
        return manager.trade_audit_cross_ledger_query(
            audit_dir=args.audit_dir,
            submission_ledger_path=args.submission_ledger_path,
            task_ledger_jsonl_path=args.task_ledger_jsonl_path,
            task_ledger_csv_path=args.task_ledger_csv_path,
            cache_output_path=args.cache_output_path,
            audit_id=args.audit_id,
            contract_no=args.contract_no,
            submission_key=args.submission_key,
            code=args.code,
            status=status,
            limit=args.limit,
            json_output_path=args.json_output_path,
            csv_output_path=args.csv_output_path,
        )
    if command_name in {"trade-period-report", "period"}:
        return manager.trade_period_report(
            start_date=args.start_date,
            end_date=args.end_date,
            timezone_name=args.timezone,
            recent_limit=args.recent_limit,
            code=args.code,
            trade_ok=args.trade_ok,
            task_name=args.task_name,
            ledger_jsonl_path=args.ledger_jsonl_path,
            ledger_csv_path=args.ledger_csv_path,
            json_output_path=args.json_output_path,
            csv_output_path=args.csv_output_path,
        )
    return None


def _build_report_preset_namespace(args: argparse.Namespace) -> argparse.Namespace:
    resolved_preset = resolve_report_preset(args.preset)
    command_name = str(resolved_preset.get("command", "")).strip()
    if command_name not in REPORT_COMMAND_DEFAULT_PROFILES:
        raise ValueError(f"unsupported report preset command: {command_name}")

    merged = dict(vars(args))
    for key, value in resolved_preset.get("options", {}).items():
        if key not in merged or merged.get(key) is None:
            merged[key] = value
    if merged.get("profile") is None:
        merged["profile"] = resolved_preset.get("profile") or REPORT_COMMAND_DEFAULT_PROFILES.get(command_name)
    if merged.get("api_profile") is None:
        merged["api_profile"] = resolved_preset.get("api_profile")
    if merged.get("strategy_path") is None:
        merged["strategy_path"] = resolved_preset.get("strategy_path")
    merged["report_command"] = command_name
    return argparse.Namespace(**merged)


def _list_report_presets(args: argparse.Namespace) -> Result:
    presets = load_report_presets()
    if args.preset:
        filtered_items = [(name, value) for name, value in presets.items() if name == args.preset]
    else:
        filtered_items = sorted(presets.items(), key=lambda item: item[0])
    preset_rows = []
    for name, value in filtered_items:
        resolved = resolve_report_preset(name, presets=presets)
        preset_rows.append(
            {
                "name": name,
                "command": resolved.get("command"),
                "profile": resolved.get("profile"),
                "description": resolved.get("description"),
                "options": resolved.get("options"),
            }
        )
    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="listed report presets",
        data={
            "summary": {
                "preset_count": len(preset_rows),
                "selected_preset": args.preset,
            },
            "presets": preset_rows,
        },
    )


def _build_task_preset_namespace(args: argparse.Namespace) -> argparse.Namespace:
    resolved_preset = resolve_task_preset(args.preset)
    command_name = str(resolved_preset.get("command", "")).strip()
    if command_name not in TASK_COMMAND_DEFAULT_PROFILES:
        raise ValueError(f"unsupported task preset command: {command_name}")

    merged = dict(vars(args))
    for key, value in resolved_preset.get("options", {}).items():
        if key not in merged or merged.get(key) is None:
            merged[key] = value
    if merged.get("profile") is None:
        merged["profile"] = resolved_preset.get("profile") or TASK_COMMAND_DEFAULT_PROFILES.get(command_name)
    if merged.get("api_profile") is None:
        merged["api_profile"] = resolved_preset.get("api_profile")
    if merged.get("trade_profile") is None:
        merged["trade_profile"] = resolved_preset.get("trade_profile")
    if merged.get("strategy_path") is None:
        merged["strategy_path"] = resolved_preset.get("strategy_path")
    if merged.get("exe_path") is None:
        merged["exe_path"] = resolved_preset.get("exe_path")
    if merged.get("title_key") == "平安证券" and resolved_preset.get("title_key"):
        merged["title_key"] = resolved_preset.get("title_key")

    if command_name in {"trade-buy", "trade-submit-once", "trade-submit-ready", "guarded-trade-buy"}:
        merged["baudrate"] = 115200 if merged.get("baudrate") is None else merged["baudrate"]
        merged["timeout"] = 2.0 if merged.get("timeout") is None else merged["timeout"]
        merged["max_depth"] = 12 if merged.get("max_depth") is None else merged["max_depth"]

    if command_name in {"trade-buy", "trade-submit-once", "guarded-trade-buy", "trade-confirm-current"}:
        merged["close_result_dialog"] = True if merged.get("close_result_dialog") is None else merged["close_result_dialog"]

    if command_name == "guarded-trade-buy":
        merged["required_block_type"] = 0 if merged.get("required_block_type") is None else merged["required_block_type"]
        merged["formula_arg"] = "" if merged.get("formula_arg") is None else merged["formula_arg"]
        merged["formula_return_count"] = 1 if merged.get("formula_return_count") is None else merged["formula_return_count"]
        merged["formula_return_date"] = False if merged.get("formula_return_date") is None else merged["formula_return_date"]
        merged["formula_stock_period"] = "1d" if merged.get("formula_stock_period") is None else merged["formula_stock_period"]
        merged["formula_start_time"] = "" if merged.get("formula_start_time") is None else merged["formula_start_time"]
        merged["formula_end_time"] = "" if merged.get("formula_end_time") is None else merged["formula_end_time"]
        merged["formula_count"] = 0 if merged.get("formula_count") is None else merged["formula_count"]
        merged["formula_dividend_type"] = 0 if merged.get("formula_dividend_type") is None else merged["formula_dividend_type"]

    if command_name == "refresh-environment":
        merged["task_command"] = command_name
        return argparse.Namespace(**merged)

    if command_name == "block-read-watchlist":
        missing_required = [name for name in ("block_code",) if merged.get(name) in (None, "")]
        if missing_required:
            raise ValueError(f"task preset execution requires: {', '.join(missing_required)}")

    if command_name == "block-read-watchlist-export":
        missing_required = [name for name in ("block_code", "export_output") if merged.get(name) in (None, "")]
        if missing_required:
            raise ValueError(f"task preset execution requires: {', '.join(missing_required)}")

    if command_name == "block-read-full":
        missing_required = [name for name in ("block_code",) if merged.get(name) in (None, "")]
        if missing_required:
            raise ValueError(f"task preset execution requires: {', '.join(missing_required)}")

    if command_name in {"trade-buy", "trade-submit-once", "trade-submit-ready", "guarded-trade-buy"}:
        missing_required = [name for name in ("port", "code", "price", "quantity") if merged.get(name) is None]
        if missing_required:
            raise ValueError(f"task preset execution requires: {', '.join(missing_required)}")

    merged["task_command"] = command_name
    return argparse.Namespace(**merged)


def _list_task_presets(args: argparse.Namespace) -> Result:
    presets = load_task_presets()
    if args.preset:
        filtered_items = [(name, value) for name, value in presets.items() if name == args.preset]
    else:
        filtered_items = sorted(presets.items(), key=lambda item: item[0])
    preset_rows = []
    for name, value in filtered_items:
        resolved = resolve_task_preset(name, presets=presets)
        preset_rows.append(
            {
                "name": name,
                "command": resolved.get("command"),
                "profile": resolved.get("profile"),
                "api_profile": resolved.get("api_profile"),
                "trade_profile": resolved.get("trade_profile"),
                "description": resolved.get("description"),
                "options": resolved.get("options"),
            }
        )
    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="listed task presets",
        data={
            "summary": {
                "preset_count": len(preset_rows),
                "selected_preset": args.preset,
            },
            "presets": preset_rows,
        },
    )


def _handle_task_subcommand(args: argparse.Namespace) -> Result:
    try:
        if args.task_command == "presets":
            return _list_task_presets(args)
        if args.task_command == "run":
            args = _build_task_preset_namespace(args)
    except ValueError as exc:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))

    try:
        manager = _build_task_manager(args)
    except ValueError as exc:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))

    report_result = _dispatch_report_workflow(manager, args, args.task_command)
    if report_result is not None:
        return report_result

    if args.task_command == "sector-research":
        return manager.sector_research(
            block_code=args.sector,
            block_type=args.block_type,
            list_type=args.list_type,
            fields=args.field,
        )
    if args.task_command == "formula-scan":
        return manager.formula_scan(
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
    if args.task_command == "watchlist-overview":
        return manager.watchlist_overview(stock_list=args.code, fields=args.field)
    if args.task_command == "block-sync":
        return manager.block_sync(
            block_code=args.block_code,
            symbols=args.stock,
            mode=args.mode,
            create_if_missing=args.create_if_missing,
            dry_run=args.dry_run,
            show=args.show,
            mutation_key=args.mutation_key,
            audit_dir=args.audit_dir,
        )
    if args.task_command == "block-read-watchlist":
        return manager.block_read_watchlist(block_code=args.block_code)
    if args.task_command == "block-read-full":
        return manager.block_read_full(block_code=args.block_code)
    if args.task_command == "block-read-watchlist-export":
        return manager.block_read_watchlist_export(
            block_code=args.block_code,
            output=args.export_output,
            overwrite=args.overwrite,
        )
    if args.task_command == "watchlist-export":
        return manager.watchlist_export(
            stock_list=args.code,
            fields=args.field,
            json_output_path=args.json_output_path,
            csv_output_path=args.csv_output_path,
        )
    if args.task_command == "subscription-watch":
        return manager.subscription_watch(
            stock_list=args.code,
            max_events=args.max_events,
            max_seconds=args.max_seconds,
            poll_interval=args.poll_interval,
            jsonl_output_path=args.jsonl_output_path,
            csv_output_path=args.csv_output_path,
            status_output_path=args.status_output_path,
        )
    if args.task_command == "sector-formula-scan":
        return manager.sector_formula_scan(
            block_code=args.sector,
            formula_name=args.formula_name,
            block_type=args.block_type,
            list_type=args.list_type,
            formula_arg=args.formula_arg,
            return_count=args.return_count,
            return_date=args.return_date,
            stock_period=args.stock_period,
            start_time=args.start_time,
            end_time=args.end_time,
            count=args.count,
            dividend_type=args.dividend_type,
        )
    if args.task_command == "sector-research-export":
        return manager.sector_research_export(
            block_code=args.sector,
            block_type=args.block_type,
            list_type=args.list_type,
            fields=args.field,
            json_output_path=args.json_output_path,
            csv_output_path=args.csv_output_path,
        )
    if args.task_command == "refresh-environment":
        return manager.refresh_environment(market=args.market, force=args.force)
    if args.task_command == "trade-buy":
        return manager.trade_buy(
            port=args.port,
            baudrate=args.baudrate,
            timeout=args.timeout,
            code=args.code,
            price=args.price,
            quantity=args.quantity,
            max_depth=args.max_depth,
            close_result_dialog=args.close_result_dialog,
            submission_key=args.submission_key,
            max_price=args.max_price,
            refresh_before_trade=args.refresh_before_trade,
            refresh_market=args.refresh_market,
            refresh_force=args.refresh_force,
        )
    if args.task_command == "trade-submit-once":
        return manager.trade_submit_once(
            port=args.port,
            baudrate=args.baudrate,
            timeout=args.timeout,
            code=args.code,
            price=args.price,
            quantity=args.quantity,
            max_depth=args.max_depth,
            close_result_dialog=args.close_result_dialog,
            submission_key=args.submission_key,
            max_price=args.max_price,
            refresh_before_trade=args.refresh_before_trade,
            refresh_market=args.refresh_market,
            refresh_force=args.refresh_force,
        )
    if args.task_command == "trade-submit-ready":
        return manager.trade_submit_ready(
            port=args.port,
            baudrate=args.baudrate,
            timeout=args.timeout,
            code=args.code,
            price=args.price,
            quantity=args.quantity,
            max_depth=args.max_depth,
            max_price=args.max_price,
            refresh_before_trade=args.refresh_before_trade,
            refresh_market=args.refresh_market,
            refresh_force=args.refresh_force,
            dialog_lookup_mode=args.dialog_lookup_mode,
            confirm_timeout=args.confirm_timeout,
        )
    if args.task_command == "trade-confirm-current":
        return manager.trade_confirm_current(
            dialog_lookup_mode=args.dialog_lookup_mode,
            confirm_timeout=args.confirm_timeout,
            result_timeout=args.result_timeout,
            close_result_dialog=args.close_result_dialog,
            result_close_pre_delay=args.result_close_pre_delay,
        )
    if args.task_command == "guarded-trade-buy":
        return manager.guarded_trade_buy(
            port=args.port,
            baudrate=args.baudrate,
            timeout=args.timeout,
            code=args.code,
            price=args.price,
            quantity=args.quantity,
            max_depth=args.max_depth,
            close_result_dialog=args.close_result_dialog,
            submission_key=args.submission_key,
            max_price=args.max_price,
            refresh_before_trade=args.refresh_before_trade,
            refresh_market=args.refresh_market,
            refresh_force=args.refresh_force,
            max_snapshot_price=args.max_snapshot_price,
            required_block_code=args.required_block_code,
            required_block_type=args.required_block_type,
            required_list_type=args.required_list_type,
            formula_name=args.formula_name,
            formula_arg=args.formula_arg,
            formula_return_count=args.formula_return_count,
            formula_return_date=args.formula_return_date,
            formula_stock_period=args.formula_stock_period,
            formula_start_time=args.formula_start_time,
            formula_end_time=args.formula_end_time,
            formula_count=args.formula_count,
            formula_dividend_type=args.formula_dividend_type,
            json_output_path=args.json_output_path,
            csv_output_path=args.csv_output_path,
        )
    return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=f"unsupported task subcommand: {args.task_command}")


def _handle_report_subcommand(args: argparse.Namespace) -> Result:
    try:
        if args.report_command == "presets":
            return _list_report_presets(args)
        if args.report_command == "run":
            args = _build_report_preset_namespace(args)
    except ValueError as exc:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))

    try:
        manager = _build_task_manager(args)
    except ValueError as exc:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))
    result = _dispatch_report_workflow(manager, args, args.report_command)
    if result is not None:
        return result
    return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=f"unsupported report subcommand: {args.report_command}")


def _handle_trade_subcommand(args: argparse.Namespace) -> Result:
    try:
        if args.trade_command == "presets":
            return _list_trade_presets(args)
        if args.trade_command == "run":
            args = _build_trade_preset_namespace(args)
    except ValueError as exc:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))

    if args.trade_command == "order-place":
        return _run_trade_order_place(args)
    if args.trade_command == "order-query":
        return _run_trade_order_query(args)
    if args.trade_command == "trade-query":
        return _run_trade_trade_query(args)
    if args.trade_command == "buy":
        return _run_trade_buy(args)
    if args.trade_command == "submit-once":
        return _run_trade_submit_once(args)
    if args.trade_command == "health":
        return _run_trade_health(args)
    if args.trade_command == "preflight":
        return _run_trade_preflight(args)
    if args.trade_command == "submit-ready":
        return _run_trade_submit_ready(args)
    if args.trade_command == "confirm-current":
        return _run_trade_confirm_current(args)
    if args.trade_command == "dialog-readiness":
        return _run_trade_dialog_readiness(args)
    if args.trade_command == "broker-capabilities":
        return _run_trade_broker_capabilities(args)
    return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=f"unsupported trade subcommand: {args.trade_command}")


def _handle_catalog_subcommand(args: argparse.Namespace) -> Result:
    try:
        if args.catalog_command == "list":
            return _list_catalog_entries(args)
        if args.catalog_command in {"plan", "preview"}:
            if getattr(args, "bundle", None):
                return _plan_catalog_bundle(args)
            resolved = resolve_command_catalog_entry(args.entry)
            return _plan_catalog_resolved_entry(
                args=args,
                entry_name=args.entry,
                source=resolved["source"],
                preset_name=resolved["preset"],
            )
        if getattr(args, "bundle", None):
            result = _run_catalog_bundle(args)
            result.data["summary_view"] = _build_catalog_summary_view(args, result)
            return result
        resolved = resolve_command_catalog_entry(args.entry)
        result = _dispatch_catalog_resolved_entry(
            args=args,
            entry_name=args.entry,
            source=resolved["source"],
            preset_name=resolved["preset"],
        )
        result.data["summary_view"] = _build_catalog_summary_view(args, result)
        return result
    except ValueError as exc:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))


def _handle_bridge_subcommand(args: argparse.Namespace) -> int:
    try:
        if args.bridge_command == "serve":
            return serve_bridge_from_config(args.config)
        if args.bridge_command == "watch-status":
            return _emit_bridge_payload(run_bridge_watch_status(registry_path=args.registry, worker_id=args.worker))
        if args.bridge_command == "watch-start":
            return _emit_bridge_payload(
                run_bridge_watch_start(
                    registry_path=args.registry,
                    worker_id=args.worker,
                    stock_list=args.code,
                    max_events=args.max_events,
                    max_seconds=args.max_seconds,
                    poll_interval=args.poll_interval,
                    idempotency_key=args.idempotency_key,
                )
            )
        if args.bridge_command == "watch-stop":
            return _emit_bridge_payload(run_bridge_watch_stop(registry_path=args.registry, worker_id=args.worker))
        return 2
    except Exception as exc:
        return _emit_bridge_payload(_build_bridge_local_failure(exc))


def _emit_bridge_payload(payload: dict[str, object]) -> int:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    sys.stdout.write("\n")
    return 0 if payload.get("ok") else 1


def _build_bridge_local_failure(exc: Exception) -> dict[str, object]:
    code = "INTERNAL_ERROR"
    if isinstance(exc, FileNotFoundError):
        code = "REGISTRY_NOT_FOUND"
    elif isinstance(exc, ValueError):
        code = "INVALID_REQUEST"
    elif isinstance(exc, RuntimeError):
        code = "BRIDGE_REQUEST_FAILED"
    return {
        "ok": False,
        "result": None,
        "error": {
            "code": code,
            "message": str(exc),
            "details": {},
        },
    }


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "bridge":
        return _handle_bridge_subcommand(args)
    adapter = PingAnBrokerAdapter(title_keyword=args.title_key, exe_path=args.exe_path)
    command_started_wall = utc_now()
    command_started_at = time.perf_counter()
    if args.command == "api":
        result = _handle_api_subcommand(args)
    elif args.command == "task":
        result = _handle_task_subcommand(args)
    elif args.command == "report":
        result = _handle_report_subcommand(args)
    elif args.command == "trade":
        result = _handle_trade_subcommand(args)
    elif args.command == "catalog":
        result = _handle_catalog_subcommand(args)
    elif (replay_result := _run_flat_replay_provider_command(args)) is not None:
        result = replay_result
    elif args.command == "health-check":
        result = adapter.health_check()
    elif args.command == "inspect":
        result = adapter.inspect()
    elif args.command == "uia-windows":
        result = inspect_uia_windows(args.window_key)
    elif args.command == "uia-inspect":
        result = inspect_uia_tree(args.title_key, max_depth=args.max_depth)
    elif args.command == "uia-dialogs":
        result = inspect_uia_dialogs(
            title_keyword=args.window_key,
            max_depth=args.max_depth,
            include_all_windows=args.include_all_windows,
        )
    elif args.command == "uia-wait-dialog":
        result = wait_for_uia_dialog(
            title_keyword=args.window_key,
            max_depth=args.max_depth,
            include_all_windows=args.include_all_windows,
            timeout=args.timeout,
            poll_interval=args.poll_interval,
            exclude_handle=args.exclude_handle,
            exclude_class_names=args.exclude_class_name,
            exclude_handles=args.exclude_handles,
            baseline_handles=args.baseline_handle,
            require_new_handle=args.require_new_handle,
            foreground_only=args.foreground_only,
        )
    elif args.command == "uia-click":
        result = click_uia_element(
            args.title_key,
            automation_id=args.automation_id,
            name=args.name,
            control_type=args.control_type,
            timeout=args.timeout,
            post_delay=args.post_delay,
        )
    elif args.command == "uia-click-path":
        result = click_uia_path(
            args.title_key,
            path=args.path,
            timeout=args.timeout,
            post_delay=args.post_delay,
        )
    elif args.command == "uia-click-center":
        result = click_uia_center(
            args.title_key,
            automation_id=args.automation_id,
            name=args.name,
            control_type=args.control_type,
            timeout=args.timeout,
            post_delay=args.post_delay,
        )
    elif args.command == "uia-activate":
        result = activate_uia_element(
            args.title_key,
            automation_id=args.automation_id,
            name=args.name,
            control_type=args.control_type,
            strategy=args.strategy,
            timeout=args.timeout,
            post_delay=args.post_delay,
        )
    elif args.command == "uia-set-text":
        result = set_uia_text(
            args.title_key,
            value=args.value,
            automation_id=args.automation_id,
            name=args.name,
            control_type=args.control_type,
            timeout=args.timeout,
            post_delay=args.post_delay,
        )
    elif args.command == "uia-read":
        result = read_uia_element(
            args.title_key,
            automation_id=args.automation_id,
            name=args.name,
            control_type=args.control_type,
            timeout=args.timeout,
        )
    elif args.command == "uia-combobox-items":
        result = list_uia_combobox_items(
            args.title_key,
            automation_id=args.automation_id,
            name=args.name,
            timeout=args.timeout,
            post_delay=args.post_delay,
        )
    elif args.command == "uia-combobox-select":
        result = select_uia_combobox_item(
            args.title_key,
            item_name=args.item_name,
            automation_id=args.automation_id,
            name=args.name,
            timeout=args.timeout,
            post_delay=args.post_delay,
        )
    elif args.command == "detect":
        result = adapter.detect()
    elif args.command == "detect-snapshot":
        snapshot = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
        payload = snapshot.get("data", snapshot)
        result = adapter.detect_from_snapshot(payload)
    elif args.command == "uia-detect-snapshot":
        snapshot = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
        payload = snapshot.get("data", snapshot)
        result = analyze_uia_snapshot(payload)
    elif args.command == "pingan-probe":
        result = run_pingan_probe(
            args.title_key,
            code=args.code,
            price=args.price,
            quantity=args.quantity,
            post_delay=args.post_delay,
            max_depth=args.max_depth,
        )
    elif args.command == "pingan-hid-submit-probe":
        result = run_pingan_hid_submit_probe(
            args.title_key,
            port=args.port,
            baudrate=args.baudrate,
            timeout=args.timeout,
            hid_pre_delay=args.hid_pre_delay,
            code=args.code,
            price=args.price,
            quantity=args.quantity,
            submit_mode=args.submit_mode,
            post_delay=args.post_delay,
            max_depth=args.max_depth,
            dialog_timeout=args.dialog_timeout,
        )
    elif args.command == "pingan-buy-submit-once":
        result = _run_trade_submit_once(args)
    elif args.command == "pingan-buy":
        result = _run_trade_buy(args)
    elif args.command == "tdx-capabilities":
        result = run_tdx_provider_capabilities()
    elif args.command == "tdx-health":
        result = run_tdx_provider_health(
            window_key=args.window_key,
            strategy_path=args.strategy_path,
            hid_port=args.hid_port,
        )
    elif args.command == "tdx-doctor":
        result = run_tdx_provider_doctor(
            window_key=args.window_key,
            strategy_path=args.strategy_path,
            hid_port=args.hid_port,
        )
    elif args.command == "tdx-probe":
        result = run_tdx_probe(args.window_key, args.max_depth)
    elif args.command == "tdx-stock-message":
        result = run_tdx_stock_message(
            window_key=args.window_key,
            code=args.code,
            market=args.market,
            post_delay=args.post_delay,
            max_depth=args.max_depth,
        )
    elif args.command == "tdx-bridge-health":
        main_window_result = find_main_window(args.window_key) if IS_WINDOWS else None
        result = run_tdx_bridge_health(
            window_key=args.window_key,
            strategy_path=args.strategy_path,
            hid_port=args.hid_port,
            main_window_result=main_window_result,
        )
    elif args.command == "tdx-trade-probe":
        result = run_tdx_trade_probe(window_key=args.window_key, max_depth=args.max_depth)
    elif args.command == "tdx-trade-hid-ping":
        result = run_tdx_trade_hid_ping(port=args.port, baudrate=args.baudrate, timeout=args.timeout, pre_delay=args.pre_delay)
    elif args.command == "tdx-trade-hid-send":
        result = run_tdx_trade_hid_send(
            port=args.port,
            baudrate=args.baudrate,
            timeout=args.timeout,
            pre_delay=args.pre_delay,
            command=args.wire_command,
        )
    elif args.command == "tdx-trade-buy-probe":
        result = run_tdx_trade_buy_probe(
            window_key=args.window_key,
            port=args.port,
            baudrate=args.baudrate,
            timeout=args.timeout,
            code=args.code,
            price=args.price,
            quantity=args.quantity,
            commit_key=args.commit_key,
            submit_strategy=args.submit_strategy,
            pre_clear=args.pre_clear,
            post_delay=args.post_delay,
            max_depth=args.max_depth,
            dialog_timeout=args.dialog_timeout,
            dry_run=args.dry_run,
        )
    elif args.command == "tdx-data-snapshot":
        result = run_tdx_data_snapshot(
            stock_code=args.code,
            field_list=args.field,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-market-snapshot":
        result = run_tdx_market_snapshot(
            stock_code=args.code,
            field_list=args.field,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-kline":
        result = run_tdx_data_kline(
            stock_list=args.code,
            period=args.period,
            start_time=args.start_time,
            end_time=args.end_time,
            count=args.count,
            dividend_type=args.dividend_type,
            field_list=args.field,
            fill_data=args.fill_data,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-stock-info":
        result = run_tdx_data_stock_info(
            stock_code=args.code,
            field_list=args.field,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-stock-list":
        result = run_tdx_stock_list(
            market=args.market,
            list_type=args.list_type,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-more-info":
        result = run_tdx_more_info(
            stock_code=args.code,
            field_list=args.field,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-cb-info":
        result = run_tdx_cb_info(
            stock_code=args.code,
            field_list=args.field,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-gb-info":
        result = run_tdx_gb_info(
            stock_code=args.code,
            date_list=args.date,
            count=args.count,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-gp-one":
        result = run_tdx_gp_one_data(
            stock_list=args.code,
            field_list=args.field,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-divid-factors":
        result = run_tdx_divid_factors(
            stock_code=args.code,
            start_time=args.start_time,
            end_time=args.end_time,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-ipo-info":
        result = run_tdx_ipo_info(
            ipo_type=args.ipo_type,
            ipo_date=args.ipo_date,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-financial":
        result = run_tdx_financial_data(
            stock_list=args.code,
            field_list=args.field,
            start_time=args.start_time,
            end_time=args.end_time,
            report_type=args.report_type,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-financial-by-date":
        result = run_tdx_financial_data_by_date(
            stock_list=args.code,
            field_list=args.field,
            year=args.year,
            mmdd=args.mmdd,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-stock-transaction":
        result = run_tdx_stock_transaction_data(
            stock_list=args.code,
            field_list=args.field,
            start_time=args.start_time,
            end_time=args.end_time,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-stock-transaction-by-date":
        result = run_tdx_stock_transaction_data_by_date(
            stock_list=args.code,
            field_list=args.field,
            year=args.year,
            mmdd=args.mmdd,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-sector-transaction":
        result = run_tdx_sector_transaction_data(
            stock_list=args.code,
            field_list=args.field,
            start_time=args.start_time,
            end_time=args.end_time,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-sector-transaction-by-date":
        result = run_tdx_sector_transaction_data_by_date(
            stock_list=args.code,
            field_list=args.field,
            year=args.year,
            mmdd=args.mmdd,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-market-transaction":
        result = run_tdx_market_transaction_data(
            field_list=args.field,
            start_time=args.start_time,
            end_time=args.end_time,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-market-transaction-by-date":
        result = run_tdx_market_transaction_data_by_date(
            field_list=args.field,
            year=args.year,
            mmdd=args.mmdd,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-sector-list":
        result = run_tdx_data_sector_list(
            list_type=args.list_type,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-data-sector-stocks":
        result = run_tdx_data_sector_stocks(
            block_code=args.sector,
            block_type=args.block_type,
            list_type=args.list_type,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-refresh-cache":
        result = run_tdx_refresh_cache(
            market=args.market,
            force=args.force,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-get-trading-dates":
        result = run_tdx_get_trading_dates(
            market=args.market,
            start_time=args.start_time,
            end_time=args.end_time,
            count=args.count,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-refresh-kline":
        result = run_tdx_refresh_kline(
            stock_list=args.code,
            period=args.period,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-download-file":
        result = run_tdx_download_file(
            stock_code=args.code,
            down_time=args.down_time,
            down_type=args.down_type,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-send-warn":
        result = run_tdx_send_warn(
            stock_list=args.code,
            time_list=args.time,
            price_list=args.price or [],
            close_list=args.close or [],
            volume_list=args.volume or [],
            bs_flag_list=args.bs_flag or [],
            warn_type_list=args.warn_type or [],
            reason_list=args.reason or [],
            count=args.count,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-get-user-sector":
        result = run_tdx_get_user_sector(
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-create-sector":
        options = {}
        if args.mutation_key is not None:
            options["mutation_key"] = args.mutation_key
        if args.audit_dir is not None:
            options["audit_dir"] = args.audit_dir
        result = run_tdx_create_sector(
            block_code=args.block_code,
            block_name=args.block_name,
            **options,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-delete-sector":
        options = {}
        if args.mutation_key is not None:
            options["mutation_key"] = args.mutation_key
        if args.audit_dir is not None:
            options["audit_dir"] = args.audit_dir
        result = run_tdx_delete_sector(
            block_code=args.block_code,
            **options,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-rename-sector":
        options = {}
        if args.mutation_key is not None:
            options["mutation_key"] = args.mutation_key
        if args.audit_dir is not None:
            options["audit_dir"] = args.audit_dir
        result = run_tdx_rename_sector(
            block_code=args.block_code,
            block_name=args.block_name,
            **options,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-clear-sector":
        options = {}
        if args.mutation_key is not None:
            options["mutation_key"] = args.mutation_key
        if args.audit_dir is not None:
            options["audit_dir"] = args.audit_dir
        result = run_tdx_clear_sector(
            block_code=args.block_code,
            **options,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-send-user-block":
        options = {}
        if args.mutation_key is not None:
            options["mutation_key"] = args.mutation_key
        if args.audit_dir is not None:
            options["audit_dir"] = args.audit_dir
        result = run_tdx_send_user_block(
            block_code=args.block_code,
            stocks=args.stock,
            show=args.show,
            **options,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-block-read-watchlist":
        manager = TdxApiManager(
            profile="default",
            strategy_path=args.strategy_path,
            provider_mode=getattr(args, "provider_mode", "live"),
            replay_fixture=getattr(args, "fixture", None),
            replay_fixture_path=getattr(args, "fixture_path", None),
        )
        result = manager.block.read_watchlist_snapshot(block_code=args.block_code)
    elif args.command == "tdx-formula-format-data":
        result = run_tdx_formula_format_data(
            kline_payload=json.loads(Path(args.input_json_file).read_text(encoding="utf-8")),
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-formula-set-data":
        result = run_tdx_formula_set_data(
            stock_code=args.code,
            stock_period=args.stock_period,
            stock_data=json.loads(Path(args.stock_data_file).read_text(encoding="utf-8")),
            count=args.count,
            dividend_type=args.dividend_type,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-formula-set-data-info":
        result = run_tdx_formula_set_data_info(
            stock_code=args.code,
            stock_period=args.stock_period,
            start_time=args.start_time,
            end_time=args.end_time,
            count=args.count,
            dividend_type=args.dividend_type,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-formula-get-data":
        result = run_tdx_formula_get_data(strategy_path=args.strategy_path)
    elif args.command == "tdx-formula-zb":
        result = run_tdx_formula_zb(
            formula_name=args.formula_name,
            formula_arg=args.formula_arg,
            xsflag=args.xsflag,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-formula-xg":
        result = run_tdx_formula_xg(
            formula_name=args.formula_name,
            formula_arg=args.formula_arg,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-formula-screen":
        result = run_tdx_formula_screen(
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
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-formula-exp":
        result = run_tdx_formula_exp(
            formula_name=args.formula_name,
            formula_arg=args.formula_arg,
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-formula-mul-xg":
        result = run_tdx_formula_process_mul_xg(
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
            strategy_path=args.strategy_path,
        )
    elif args.command == "tdx-formula-mul-zb":
        result = run_tdx_formula_process_mul_zb(
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
            strategy_path=args.strategy_path,
        )
    elif args.command == "hid-ping":
        result = run_hid_ping(port=args.port, baudrate=args.baudrate, timeout=args.timeout, pre_delay=args.pre_delay)
    elif args.command == "hid-send":
        result = run_hid_send(port=args.port, baudrate=args.baudrate, timeout=args.timeout, pre_delay=args.pre_delay, command=args.wire_command)
    elif args.command == "win32-read":
        result = run_win32_read(args.hwnd)
    elif args.command == "win32-set-text":
        result = run_win32_set_text(args.hwnd, args.value, args.post_delay)
    elif args.command == "win32-type-text":
        result = run_win32_type_text(args.hwnd, args.value, args.post_delay)
    elif args.command == "win32-click":
        result = run_win32_click(args.hwnd, args.strategy, args.post_delay)
    elif args.command == "tdx-submit-probe":
        result = run_tdx_submit_probe(
            window_key=args.window_key,
            hwnd=args.hwnd,
            post_delay=args.post_delay,
            max_depth=args.max_depth,
        )
    elif args.command == "tdx-submit-once":
        result = run_tdx_submit_once(
            window_key=args.window_key,
            hwnd=args.hwnd,
            strategy=args.strategy,
            post_delay=args.post_delay,
            max_depth=args.max_depth,
            dialog_timeout=args.dialog_timeout,
        )
    elif args.command == "tdx-buy-probe":
        result = run_tdx_buy_probe(
            window_key=args.window_key,
            code=args.code,
            price=args.price,
            quantity=args.quantity,
            code_input=args.code_input,
            submit_strategy=args.submit_strategy,
            code_commit=args.code_commit,
            post_delay=args.post_delay,
            max_depth=args.max_depth,
        )
    elif args.command == "tdx-buy-probe-stock-context":
        result = run_tdx_buy_probe_stock_context(
            window_key=args.window_key,
            code=args.code,
            market=args.market,
            price=args.price,
            quantity=args.quantity,
            submit_strategy=args.submit_strategy,
            post_delay=args.post_delay,
            max_depth=args.max_depth,
        )
    elif args.command == "tdx-hid-buy-probe":
        result = run_tdx_hid_buy_probe(
            window_key=args.window_key,
            port=args.port,
            baudrate=args.baudrate,
            timeout=args.timeout,
            code=args.code,
            price=args.price,
            quantity=args.quantity,
            commit_key=args.commit_key,
            submit_strategy=args.submit_strategy,
            pre_clear=args.pre_clear,
            post_delay=args.post_delay,
            max_depth=args.max_depth,
            dialog_timeout=args.dialog_timeout,
            dry_run=args.dry_run,
        )
    else:
        order = OrderRequest(code=args.code, quantity=args.quantity, price=args.price, dry_run=args.dry_run)
        result = adapter.buy(order)
    total_ms = round((time.perf_counter() - command_started_at) * 1000, 3)
    result.data.setdefault("timing", {})["total_ms"] = total_ms
    if args.command in {"pingan-buy-submit-once", "pingan-buy"} or (
        args.command == "trade" and getattr(args, "trade_command", None) in {"buy", "submit-once"}
    ) or (
        args.command == "catalog"
        and (
            result.data.get("catalog_entry", {}).get("source") == "trade"
            or result.data.get("catalog_bundle", {}).get("trade_contract_no") is not None
        )
    ):
        _emit_pingan_contract_log(_resolve_pingan_contract_no(result))
    command_finished_wall = utc_now()
    if _uses_provider_result_contract(args):
        output_payload = _build_provider_result_payload(
            args,
            result,
            started_at=format_rfc3339(command_started_wall),
            finished_at=format_rfc3339(command_finished_wall),
            elapsed_ms=total_ms,
        )
    else:
        output_payload = _select_catalog_output_payload(args, result)
    serialized = json.dumps(output_payload, ensure_ascii=False, indent=2)
    if getattr(args, "output", None):
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)
    return 0 if result.ok else 1


def run_tdx_probe(window_key: str, max_depth: int) -> object:
    window_result = inspect_uia_windows(window_key)
    main_window_result = find_main_window(window_key)
    controls_result = None
    if main_window_result.ok:
        controls_result = enumerate_controls(int(main_window_result.data["main_hwnd"]))
    else:
        controls_result = main_window_result
    uia_result = inspect_uia_tree(window_key, max_depth=max_depth)
    ok = window_result.ok and main_window_result.ok and controls_result.ok and uia_result.ok
    return Result(
        ok=ok,
        code=ErrorCode.OK if ok else ErrorCode.CONTROL_NOT_FOUND,
        message="completed TongDaXin probe" if ok else "TongDaXin probe encountered an error",
        data={
            "window_key": window_key,
            "windows": window_result.to_dict(),
            "main_window": main_window_result.to_dict(),
            "controls": controls_result.to_dict(),
            "uia": uia_result.to_dict(),
        },
    )


def _tdx_stock_value(code: str, market: str) -> tuple[int, str]:
    normalized = code.strip()
    if not normalized.isdigit() or len(normalized) != 6:
        raise ValueError("stock code must be a 6-digit numeric string")
    resolved_market = market
    if resolved_market == "auto":
        if normalized.startswith(("5", "6", "9")):
            resolved_market = "sh"
        else:
            resolved_market = "sz"
    prefix = "7" if resolved_market == "sh" else "6"
    return int(prefix + normalized), resolved_market


def run_tdx_stock_message(window_key: str, code: str, market: str, post_delay: float, max_depth: int) -> Result:
    guard = _require_windows_result("tdx-stock-message")
    if guard:
        return guard
    try:
        stock_value, resolved_market = _tdx_stock_value(code, market)
    except ValueError as exc:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message=str(exc),
            data={"code": code, "market": market},
        )

    main_window_result = find_main_window(window_key)
    if not main_window_result.ok:
        return main_window_result
    main_hwnd = int(main_window_result.data["main_hwnd"])
    before_probe = run_tdx_probe(window_key, max_depth)
    try:
        uwm_stock = register_window_message("Stock")
        post_message(main_hwnd, uwm_stock, stock_value, 0)
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to post Stock message: {exc}",
            data={"window_key": window_key, "main_hwnd": main_hwnd, "code": code, "market": resolved_market},
        )

    if post_delay > 0:
        import time

        time.sleep(post_delay)
    after_probe = run_tdx_probe(window_key, max_depth)
    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="posted TongDaXin Stock registered message",
        data={
            "window_key": window_key,
            "main_hwnd": main_hwnd,
            "code": code,
            "market": resolved_market,
            "stock_value": stock_value,
            "registered_message": "Stock",
            "registered_message_id": uwm_stock,
            "before_probe": before_probe.to_dict(),
            "after_probe": after_probe.to_dict(),
        },
        warnings=[
            "该命令只验证通达信主窗口是否接受 Stock 注册消息，不代表交易页代码输入已被业务层接受。",
        ],
    )


def _require_windows_result(action: str) -> Result | None:
    if IS_WINDOWS:
        return None
    return Result(
        ok=False,
        code=ErrorCode.UNSUPPORTED_PLATFORM,
        message=f"{action} is only available from native Windows Python",
        next_action="Run the command from Windows Python instead of WSL/Linux.",
    )


def _serialize_hwnd(hwnd: int) -> dict[str, object]:
    return {
        "hwnd": hwnd,
        "class_name": get_class_name(hwnd),
        "text": get_text(hwnd),
        "parent_hwnd": get_parent(hwnd),
        "control_id": get_control_id(hwnd),
        "rect": get_rect(hwnd),
    }


def run_win32_read(hwnd: int) -> Result:
    guard = _require_windows_result("win32-read")
    if guard:
        return guard
    try:
        return Result(ok=True, code=ErrorCode.OK, message="read Win32 control", data=_serialize_hwnd(hwnd))
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to read Win32 control: {exc}",
            data={"hwnd": hwnd},
        )


def run_win32_set_text(hwnd: int, value: str, post_delay: float) -> Result:
    guard = _require_windows_result("win32-set-text")
    if guard:
        return guard
    try:
        before = _serialize_hwnd(hwnd)
        set_text(hwnd, value)
        if post_delay > 0:
            import time

            time.sleep(post_delay)
        after = _serialize_hwnd(hwnd)
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message="set Win32 control text",
            data={"before": before, "after": after, "value": value},
        )
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to set Win32 control text: {exc}",
            data={"hwnd": hwnd, "value": value},
        )


def run_win32_type_text(hwnd: int, value: str, post_delay: float) -> Result:
    guard = _require_windows_result("win32-type-text")
    if guard:
        return guard
    try:
        before = _serialize_hwnd(hwnd)
        type_text(hwnd, value, clear_first=True)
        if post_delay > 0:
            import time

            time.sleep(post_delay)
        after = _serialize_hwnd(hwnd)
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message="typed Win32 control text",
            data={"before": before, "after": after, "value": value},
        )
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to type Win32 control text: {exc}",
            data={"hwnd": hwnd, "value": value},
        )


def run_win32_keybd_type_text(hwnd: int, value: str, post_delay: float) -> Result:
    guard = _require_windows_result("win32-keybd-type-text")
    if guard:
        return guard
    try:
        before = _serialize_hwnd(hwnd)
        focus_window(hwnd, settle_delay=0.1)
        send_ctrl_a(delay=0.02)
        send_delete_key(delay=0.02)
        type_text_keybd(value, key_delay=0.02)
        if post_delay > 0:
            import time

            time.sleep(post_delay)
        after = _serialize_hwnd(hwnd)
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message="typed Win32 control text via keybd_event",
            data={"before": before, "after": after, "value": value},
        )
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to type Win32 control text via keybd_event: {exc}",
            data={"hwnd": hwnd, "value": value},
        )


def run_win32_click(hwnd: int, strategy: str, post_delay: float) -> Result:
    guard = _require_windows_result("win32-click")
    if guard:
        return guard
    try:
        before = _serialize_hwnd(hwnd)
        if strategy == "bm_click":
            click(hwnd)
        elif strategy == "enter_key":
            send_enter(hwnd)
        elif strategy == "tab_key":
            send_tab(hwnd)
        elif strategy == "wm_command":
            parent = get_parent(hwnd)
            control_id = get_control_id(hwnd)
            if parent is None or control_id is None:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="wm_command requires a valid parent handle and control id",
                    data={"hwnd": hwnd, "parent_hwnd": parent, "control_id": control_id},
                )
            send_wm_command(parent, control_id, hwnd)
        else:
            return Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message="unsupported Win32 click strategy",
                data={"strategy": strategy},
            )
        if post_delay > 0:
            import time

            time.sleep(post_delay)
        after = _serialize_hwnd(hwnd)
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message=f"clicked Win32 control via {strategy}",
            data={"before": before, "after": after, "strategy": strategy},
        )
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to click Win32 control: {exc}",
            data={"hwnd": hwnd, "strategy": strategy},
        )


def _tdx_buy_handles() -> dict[str, int]:
    return {
        "shareholder_combo": 3150368,
        "code_edit": 725916,
        "price_edit": 398452,
        "quantity_edit": 592962,
        "submit_button": 331326,
    }


def _capture_step(steps: list[dict[str, object]], step: str, result: Result) -> Result:
    steps.append({"step": step, "result": result.to_dict()})
    return result


def _tdx_trade_protocol() -> dict[str, object]:
    return {
        "hid_commands": [
            "PING",
            "KEY TAB",
            "KEY ENTER",
            "KEY ESC",
            "KEY DELETE",
            "KEY CTRL+A",
            "TYPE <6-digit-code>",
            "TYPE <6-digit-code> TAB",
            "TYPE <6-digit-code> ENTER",
        ],
        "notes": [
            "bridge 正式入口只允许最小 HID 命令集，不接受任意自定义串口指令。",
            "建议继续使用明显不能成交的低价做买入链路验证。",
        ],
    }


def run_tdx_trade_probe(window_key: str, max_depth: int) -> Result:
    guard = _require_windows_result("tdx-trade-probe")
    if guard:
        return guard

    handles = _tdx_buy_handles()
    main_window_result = find_main_window(window_key)
    if not main_window_result.ok:
        return main_window_result
    main_hwnd = int(main_window_result.data["main_hwnd"])
    probe_result = run_tdx_probe(window_key, max_depth)
    evidence = {name: run_win32_read(hwnd).to_dict() for name, hwnd in handles.items()}
    missing = [name for name, payload in evidence.items() if not payload["ok"]]
    warnings: list[str] = []
    if missing:
        warnings.append(f"部分买入区句柄无法读取: {', '.join(missing)}")
    warnings.append("当前句柄集合基于实测版本，如客户端升级后失效，应先重新探测。")
    ok = probe_result.ok and not missing
    return Result(
        ok=ok,
        code=ErrorCode.OK if ok else ErrorCode.CONTROL_NOT_FOUND,
        message="probed TongDaXin trading bridge prerequisites" if ok else "TongDaXin trading bridge probe found missing buy-page prerequisites",
        data={
            "window_key": window_key,
            "main_hwnd": main_hwnd,
            "handles": handles,
            "evidence": evidence,
            "probe": probe_result.to_dict(),
            "protocol": _tdx_trade_protocol(),
        },
        warnings=warnings,
        next_action=None if ok else "Bring TongDaXin to the classic buy page, then run `tdx-trade-probe` again.",
    )


def run_tdx_trade_hid_ping(port: str, baudrate: int, timeout: float, pre_delay: float = 0.0) -> Result:
    result = run_hid_ping(port=port, baudrate=baudrate, timeout=timeout, pre_delay=pre_delay)
    result.data["protocol"] = _tdx_trade_protocol()
    result.data["bridge_command"] = "tdx-trade-hid-ping"
    return result


def run_tdx_trade_hid_send(port: str, baudrate: int, timeout: float, command: str, pre_delay: float = 0.0) -> Result:
    try:
        normalized_command = validate_hid_wire_command(command)
    except ValueError as exc:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message=str(exc),
            data={"command": command, "protocol": _tdx_trade_protocol()},
            next_action="Use only the minimal bridge HID commands: PING, KEY, or TYPE.",
        )

    result = run_hid_send(port=port, baudrate=baudrate, timeout=timeout, pre_delay=pre_delay, command=normalized_command)
    result.data["bridge_command"] = "tdx-trade-hid-send"
    result.data["normalized_command"] = normalized_command
    result.data["protocol"] = _tdx_trade_protocol()
    return result


def run_tdx_trade_buy_probe(
    window_key: str,
    port: str,
    baudrate: int,
    timeout: float,
    code: str,
    price: str,
    quantity: int,
    commit_key: str,
    submit_strategy: str,
    pre_clear: bool,
    post_delay: float,
    max_depth: int,
    dialog_timeout: float,
    dry_run: bool,
) -> Result:
    result = run_tdx_hid_buy_probe(
        window_key=window_key,
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        code=code,
        price=price,
        quantity=quantity,
        commit_key=commit_key,
        submit_strategy=submit_strategy,
        pre_clear=pre_clear,
        post_delay=post_delay,
        max_depth=max_depth,
        dialog_timeout=dialog_timeout,
        dry_run=dry_run,
    )
    result.data["bridge_command"] = "tdx-trade-buy-probe"
    result.data["protocol"] = _tdx_trade_protocol()
    return result


def _validate_foreground_focus(window_key: str, main_hwnd: int, focus_hwnd: int) -> Result:
    foreground_hwnd = get_foreground_window()
    gui_focus_hwnd = get_gui_thread_focus(main_hwnd)
    ok = foreground_hwnd == main_hwnd and gui_focus_hwnd == focus_hwnd
    warnings: list[str] = []
    if foreground_hwnd != main_hwnd:
        warnings.append("通达信主窗口当前不在前台，HID 输入可能会打到错误程序。")
    if gui_focus_hwnd != focus_hwnd:
        warnings.append("代码框当前不在焦点上，HID 输入可能不会进入证券代码框。")
    return Result(
        ok=ok,
        code=ErrorCode.OK if ok else ErrorCode.EXECUTION_FAILED,
        message="validated TongDaXin foreground/focus state" if ok else "TongDaXin foreground/focus validation failed",
        data={
            "window_key": window_key,
            "main_hwnd": main_hwnd,
            "foreground_hwnd": foreground_hwnd,
            "expected_focus_hwnd": focus_hwnd,
            "gui_thread_focus_hwnd": gui_focus_hwnd,
        },
        warnings=warnings,
    )


def run_tdx_hid_buy_probe(
    window_key: str,
    port: str,
    baudrate: int,
    timeout: float,
    code: str,
    price: str,
    quantity: int,
    commit_key: str,
    submit_strategy: str,
    pre_clear: bool,
    post_delay: float,
    max_depth: int,
    dialog_timeout: float,
    dry_run: bool,
) -> Result:
    guard = _require_windows_result("tdx-hid-buy-probe")
    if guard:
        return guard

    handles = _tdx_buy_handles()
    steps: list[dict[str, object]] = []
    main_window_result = find_main_window(window_key)
    if not main_window_result.ok:
        return main_window_result
    main_hwnd = int(main_window_result.data["main_hwnd"])

    _capture_step(steps, "probe_before", run_tdx_probe(window_key, max_depth))
    _capture_step(steps, "read_code_before", run_win32_read(handles["code_edit"]))
    _capture_step(steps, "read_price_before", run_win32_read(handles["price_edit"]))
    _capture_step(steps, "read_quantity_before", run_win32_read(handles["quantity_edit"]))

    restore_foreground_window(main_hwnd, settle_delay=0.2)
    focus_window(handles["code_edit"], settle_delay=0.1)
    focus_result = _capture_step(steps, "validate_focus_before_hid", _validate_foreground_focus(window_key, main_hwnd, handles["code_edit"]))
    if not focus_result.ok:
        return Result(
            ok=False,
            code=focus_result.code,
            message="TongDaXin HID probe aborted before input",
            data={
                "window_key": window_key,
                "port": port,
                "baudrate": baudrate,
                "timeout": timeout,
                "input": {
                    "code": code,
                    "price": price,
                    "quantity": quantity,
                    "commit_key": commit_key,
                    "submit_strategy": submit_strategy,
                    "pre_clear": pre_clear,
                    "dry_run": dry_run,
                },
                "handles": handles,
                "steps": steps,
            },
            warnings=focus_result.warnings,
            next_action="Bring TongDaXin to the foreground, focus the stock code input, then run the command again.",
        )

    if dry_run:
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message="validated TongDaXin HID preflight only",
            data={
                "window_key": window_key,
                "port": port,
                "baudrate": baudrate,
                "timeout": timeout,
                "input": {
                    "code": code,
                    "price": price,
                    "quantity": quantity,
                    "commit_key": commit_key,
                    "submit_strategy": submit_strategy,
                    "pre_clear": pre_clear,
                    "dry_run": dry_run,
                },
                "handles": handles,
                "steps": steps,
            },
            warnings=[
                "dry-run 只做窗口与焦点校验，不会实际向 HID 设备发送按键。",
            ],
        )

    if pre_clear:
        _capture_step(steps, "hid_key_ctrl_a", run_hid_send(port=port, baudrate=baudrate, timeout=timeout, command=f"KEY {normalize_hid_key('ctrl+a')}"))
        _capture_step(steps, "hid_key_delete", run_hid_send(port=port, baudrate=baudrate, timeout=timeout, command=f"KEY {normalize_hid_key('delete')}"))

    try:
        hid_command = build_type_command(code, commit_key=commit_key)
    except ValueError as exc:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message=str(exc),
            data={"code": code, "commit_key": commit_key},
        )

    hid_result = _capture_step(steps, "hid_type_code", run_hid_send(port=port, baudrate=baudrate, timeout=timeout, command=hid_command))
    _capture_step(steps, "read_code_after_hid", run_win32_read(handles["code_edit"]))
    if not hid_result.ok:
        return Result(
            ok=False,
            code=hid_result.code,
            message="TongDaXin HID code input failed",
            data={
                "window_key": window_key,
                "port": port,
                "baudrate": baudrate,
                "timeout": timeout,
                "handles": handles,
                "steps": steps,
            },
        )

    _capture_step(steps, "set_price", run_win32_set_text(handles["price_edit"], price, post_delay=0.3))
    _capture_step(steps, "set_quantity", run_win32_set_text(handles["quantity_edit"], str(quantity), post_delay=0.3))
    _capture_step(steps, "read_price_after", run_win32_read(handles["price_edit"]))
    _capture_step(steps, "read_quantity_after", run_win32_read(handles["quantity_edit"]))
    submit_result = _capture_step(
        steps,
        "submit",
        run_tdx_submit_once(
            window_key=window_key,
            hwnd=handles["submit_button"],
            strategy=submit_strategy,
            post_delay=post_delay,
            max_depth=max_depth,
            dialog_timeout=dialog_timeout,
        ),
    )
    _capture_step(steps, "probe_after", run_tdx_probe(window_key, max_depth))

    return Result(
        ok=hid_result.ok and submit_result.ok,
        code=ErrorCode.OK if hid_result.ok and submit_result.ok else ErrorCode.EXECUTION_FAILED,
        message="completed TongDaXin HID buy probe" if hid_result.ok and submit_result.ok else "TongDaXin HID buy probe encountered an error",
        data={
            "window_key": window_key,
            "port": port,
            "baudrate": baudrate,
            "timeout": timeout,
            "input": {
                "code": code,
                "price": price,
                "quantity": quantity,
                "commit_key": commit_key,
                "submit_strategy": submit_strategy,
                "pre_clear": pre_clear,
                "post_delay": post_delay,
                "max_depth": max_depth,
                "dialog_timeout": dialog_timeout,
            },
            "handles": handles,
            "steps": steps,
        },
        warnings=[
            "该命令要求 TongDaXin 主窗口已经在当前桌面会话中可见，并且允许被置前。",
            "如果提交后仍然出现“请输入证券代码!”，说明 HID 输入序列仍需调整，例如切换为 ENTER 或增加额外确认步骤。",
        ],
    )


def run_tdx_buy_probe(
    window_key: str,
    code: str,
    price: str,
    quantity: int,
    code_input: str,
    submit_strategy: str,
    code_commit: str,
    post_delay: float,
    max_depth: int,
) -> Result:
    guard = _require_windows_result("tdx-buy-probe")
    if guard:
        return guard

    handles = _tdx_buy_handles()
    steps: list[dict[str, object]] = []

    _capture_step(steps, "probe_before", run_tdx_probe(window_key, max_depth))
    _capture_step(steps, "read_code_before", run_win32_read(handles["code_edit"]))
    _capture_step(steps, "read_price_before", run_win32_read(handles["price_edit"]))
    _capture_step(steps, "read_quantity_before", run_win32_read(handles["quantity_edit"]))
    if code_input == "type_text":
        _capture_step(steps, "set_code", run_win32_type_text(handles["code_edit"], code, post_delay=0.3))
    elif code_input == "keybd_event":
        _capture_step(steps, "set_code", run_win32_keybd_type_text(handles["code_edit"], code, post_delay=0.3))
    else:
        _capture_step(steps, "set_code", run_win32_set_text(handles["code_edit"], code, post_delay=0.3))
    if code_commit != "none":
        _capture_step(steps, "commit_code", run_win32_click(handles["code_edit"], code_commit, post_delay=0.3))
    _capture_step(steps, "set_price", run_win32_set_text(handles["price_edit"], price, post_delay=0.3))
    _capture_step(steps, "set_quantity", run_win32_set_text(handles["quantity_edit"], str(quantity), post_delay=0.3))
    _capture_step(steps, "read_code_after", run_win32_read(handles["code_edit"]))
    _capture_step(steps, "read_price_after", run_win32_read(handles["price_edit"]))
    _capture_step(steps, "read_quantity_after", run_win32_read(handles["quantity_edit"]))
    submit_result = _capture_step(steps, "submit", run_win32_click(handles["submit_button"], submit_strategy, post_delay))
    _capture_step(steps, "probe_after", run_tdx_probe(window_key, max_depth))

    warnings = [
        "当前句柄映射基于真实通达信控件树抓取，仍然属于版本相关绑定。",
        "该探测不会处理提交后的确认弹窗；如果出现确认框，需要再抓一次控件树补齐下一跳。",
    ]
    return Result(
        ok=submit_result.ok,
        code=ErrorCode.OK if submit_result.ok else submit_result.code,
        message="completed TongDaXin buy probe" if submit_result.ok else "TongDaXin buy probe encountered an error",
        data={
            "window_key": window_key,
            "input": {
                "code": code,
                "price": price,
                "quantity": quantity,
                "code_input": code_input,
                "submit_strategy": submit_strategy,
                "code_commit": code_commit,
                "post_delay": post_delay,
                "max_depth": max_depth,
            },
            "handles": handles,
            "steps": steps,
        },
        warnings=warnings,
    )


def run_tdx_buy_probe_stock_context(
    window_key: str,
    code: str,
    market: str,
    price: str,
    quantity: int,
    submit_strategy: str,
    post_delay: float,
    max_depth: int,
) -> Result:
    guard = _require_windows_result("tdx-buy-probe-stock-context")
    if guard:
        return guard

    handles = _tdx_buy_handles()
    steps: list[dict[str, object]] = []

    _capture_step(steps, "probe_before", run_tdx_probe(window_key, max_depth))
    _capture_step(steps, "stock_message", run_tdx_stock_message(window_key, code, market, post_delay=max(0.5, post_delay), max_depth=max_depth))
    _capture_step(steps, "read_code_after_stock_message", run_win32_read(handles["code_edit"]))
    _capture_step(steps, "set_price", run_win32_set_text(handles["price_edit"], price, post_delay=0.3))
    _capture_step(steps, "set_quantity", run_win32_set_text(handles["quantity_edit"], str(quantity), post_delay=0.3))
    _capture_step(steps, "read_price_after", run_win32_read(handles["price_edit"]))
    _capture_step(steps, "read_quantity_after", run_win32_read(handles["quantity_edit"]))
    submit_result = _capture_step(steps, "submit", run_win32_click(handles["submit_button"], submit_strategy, post_delay))
    _capture_step(steps, "probe_after", run_tdx_probe(window_key, max_depth))

    return Result(
        ok=submit_result.ok,
        code=ErrorCode.OK if submit_result.ok else submit_result.code,
        message="completed TongDaXin stock-context buy probe" if submit_result.ok else "TongDaXin stock-context buy probe encountered an error",
        data={
            "window_key": window_key,
            "input": {
                "code": code,
                "market": market,
                "price": price,
                "quantity": quantity,
                "submit_strategy": submit_strategy,
                "post_delay": post_delay,
                "max_depth": max_depth,
            },
            "handles": handles,
            "steps": steps,
        },
        warnings=[
            "该探测依赖 Stock 注册消息切换主证券上下文，但不会向代码编辑框写入文本。",
            "如果提交后仍然提示请输入证券代码，说明交易业务层不接受仅靠主窗口证券上下文完成下单。",
        ],
    )


def _ancestor_chain(hwnd: int, max_depth: int = 8) -> list[dict[str, object]]:
    chain: list[dict[str, object]] = []
    current = hwnd
    seen: set[int] = set()
    depth = 0
    while current and current not in seen and depth < max_depth:
        seen.add(current)
        item = _serialize_hwnd(current)
        item["style"] = get_window_style(current)
        item["exstyle"] = get_window_exstyle(current)
        chain.append(item)
        parent = get_parent(current)
        if parent is None:
            break
        current = parent
        depth += 1
    return chain


def run_tdx_submit_probe(window_key: str, hwnd: int, post_delay: float, max_depth: int) -> Result:
    guard = _require_windows_result("tdx-submit-probe")
    if guard:
        return guard

    control_id = get_control_id(hwnd)
    chain = _ancestor_chain(hwnd)
    attempts: list[tuple[str, callable]] = [
        ("bm_click", lambda: click(hwnd)),
        ("wm_command_parent", lambda: send_wm_command(chain[1]["hwnd"], control_id, hwnd) if len(chain) > 1 and control_id else None),
        ("post_wm_command_parent", lambda: post_wm_command(chain[1]["hwnd"], control_id, hwnd) if len(chain) > 1 and control_id else None),
        ("enter_key", lambda: send_enter(hwnd)),
        ("space_key", lambda: send_space(hwnd)),
        ("mouse_message", lambda: send_button_mouse_click(hwnd)),
    ]
    for level in range(2, min(len(chain), 6)):
        attempts.append(
            (
                f"wm_command_ancestor_{level}",
                lambda level=level: send_wm_command(chain[level]["hwnd"], control_id, hwnd) if control_id else None,
            )
        )
        attempts.append(
            (
                f"post_wm_command_ancestor_{level}",
                lambda level=level: post_wm_command(chain[level]["hwnd"], control_id, hwnd) if control_id else None,
            )
        )

    steps: list[dict[str, object]] = []

    def capture(step: str, result: Result) -> Result:
        steps.append({"step": step, "result": result.to_dict()})
        return result

    capture("probe_before", run_tdx_probe(window_key, max_depth))
    capture("button_before", run_win32_read(hwnd))

    import time

    for label, fn in attempts:
        if "wm_command" in label and control_id is None:
            steps.append(
                {
                    "step": label,
                    "result": Result(
                        ok=False,
                        code=ErrorCode.INVALID_REQUEST,
                        message="control id unavailable for wm_command strategy",
                        data={"hwnd": hwnd},
                    ).to_dict(),
                }
            )
            continue
        try:
            fn()
            if post_delay > 0:
                time.sleep(post_delay)
            steps.append(
                {
                    "step": label,
                    "result": Result(
                        ok=True,
                        code=ErrorCode.OK,
                        message=f"submitted via {label}",
                        data={"hwnd": hwnd},
                    ).to_dict(),
                }
            )
        except Exception as exc:
            steps.append(
                {
                    "step": label,
                    "result": Result(
                        ok=False,
                        code=ErrorCode.EXECUTION_FAILED,
                        message=f"{label} failed: {exc}",
                        data={"hwnd": hwnd},
                    ).to_dict(),
                }
            )
        capture(f"probe_after_{label}", run_tdx_probe(window_key, max_depth))

    capture("button_after", run_win32_read(hwnd))

    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="completed TongDaXin submit probe",
        data={
            "window_key": window_key,
            "button": _serialize_hwnd(hwnd),
            "ancestor_chain": chain,
            "steps": steps,
        },
        warnings=[
            "该命令会连续尝试多种非物理提交策略，仅用于低价不成交前提下的链路归因。",
            "请在确认代码/价格/数量已经填入后再运行。",
        ],
    )


def run_tdx_submit_once(
    window_key: str,
    hwnd: int,
    strategy: str,
    post_delay: float,
    max_depth: int,
    dialog_timeout: float,
) -> Result:
    guard = _require_windows_result("tdx-submit-once")
    if guard:
        return guard

    control_id = get_control_id(hwnd)
    chain = _ancestor_chain(hwnd)
    action = {
        "bm_click": lambda: click(hwnd),
        "wm_command_parent": lambda: send_wm_command(chain[1]["hwnd"], control_id, hwnd),
        "post_wm_command_parent": lambda: post_wm_command(chain[1]["hwnd"], control_id, hwnd),
        "enter_key": lambda: send_enter(hwnd),
        "space_key": lambda: send_space(hwnd),
        "mouse_message": lambda: send_button_mouse_click(hwnd),
        "wm_command_ancestor_2": lambda: send_wm_command(chain[2]["hwnd"], control_id, hwnd),
        "post_wm_command_ancestor_2": lambda: post_wm_command(chain[2]["hwnd"], control_id, hwnd),
        "wm_command_ancestor_3": lambda: send_wm_command(chain[3]["hwnd"], control_id, hwnd),
        "post_wm_command_ancestor_3": lambda: post_wm_command(chain[3]["hwnd"], control_id, hwnd),
        "wm_command_ancestor_4": lambda: send_wm_command(chain[4]["hwnd"], control_id, hwnd),
        "post_wm_command_ancestor_4": lambda: post_wm_command(chain[4]["hwnd"], control_id, hwnd),
        "wm_command_ancestor_5": lambda: send_wm_command(chain[5]["hwnd"], control_id, hwnd),
        "post_wm_command_ancestor_5": lambda: post_wm_command(chain[5]["hwnd"], control_id, hwnd),
    }.get(strategy)
    if action is None:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="unsupported TongDaXin submit strategy",
            data={"strategy": strategy},
        )
    if "wm_command" in strategy and control_id is None:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="control id unavailable for wm_command strategy",
            data={"hwnd": hwnd, "strategy": strategy},
        )
    required_depth = 1
    if "_ancestor_" in strategy:
        required_depth = int(strategy.rsplit("_", 1)[-1])
    if len(chain) <= required_depth:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="ancestor chain is too short for the requested strategy",
            data={"strategy": strategy, "ancestor_chain": chain},
        )

    before_probe = run_tdx_probe(window_key, max_depth)
    before_button = run_win32_read(hwnd)
    main_window_result = find_main_window(window_key)
    main_hwnd = int(main_window_result.data["main_hwnd"]) if main_window_result.ok else None
    try:
        action()
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"submit strategy failed: {exc}",
            data={"strategy": strategy, "hwnd": hwnd, "ancestor_chain": chain},
        )

    if post_delay > 0:
        import time
        time.sleep(post_delay)

    dialog_capture = wait_for_uia_dialog(
        title_keyword=None,
        max_depth=6,
        include_all_windows=True,
        timeout=dialog_timeout,
        poll_interval=0.2,
        exclude_handle=main_hwnd,
        exclude_class_names=[
            "Shell_TrayWnd",
            "Shell_SecondaryTrayWnd",
            "Progman",
            "CASCADIA_HOSTING_WINDOW_CLASS",
            "PX_WINDOW_CLASS",
            "Chrome_WidgetWin_1",
            "MozillaWindowClass",
            "CEF-OSC-WIDGET",
            "Qt51514QWindowIcon",
            "TdxW_MainFrame_Class",
        ],
    )
    after_probe = run_tdx_probe(window_key, max_depth)
    after_button = run_win32_read(hwnd)
    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="completed TongDaXin single submit attempt",
        data={
            "window_key": window_key,
            "strategy": strategy,
            "dialog_timeout": dialog_timeout,
            "button": _serialize_hwnd(hwnd),
            "ancestor_chain": chain,
            "before_probe": before_probe.to_dict(),
            "before_button": before_button.to_dict(),
            "dialog_capture": dialog_capture.to_dict(),
            "after_probe": after_probe.to_dict(),
            "after_button": after_button.to_dict(),
        },
        warnings=[
            "该命令只执行一次指定提交策略，并在提交后短时间内等待潜在业务弹窗。",
        ],
    )


if __name__ == "__main__":
    raise SystemExit(main())
