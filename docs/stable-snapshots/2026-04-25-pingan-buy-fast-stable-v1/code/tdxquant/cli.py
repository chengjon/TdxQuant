from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import TextIO

from .brokers import PingAnBrokerAdapter
from .hid_bridge import build_type_command, normalize_hid_key, run_hid_ping, run_hid_send, validate_hid_wire_command
from .inspector import enumerate_controls, find_main_window
from .models import ErrorCode, OrderRequest, Result
from .tdx_api_bridge import (
    run_tdx_bridge_health,
    run_tdx_data_kline,
    run_tdx_data_sector_list,
    run_tdx_data_sector_stocks,
    run_tdx_data_snapshot,
    run_tdx_data_stock_info,
    run_tdx_formula_exp,
    run_tdx_formula_format_data,
    run_tdx_formula_get_data,
    run_tdx_formula_process_mul_xg,
    run_tdx_formula_process_mul_zb,
    run_tdx_formula_set_data,
    run_tdx_formula_set_data_info,
    run_tdx_formula_xg,
    run_tdx_formula_zb,
)
from .uia_inspector import (
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
    run_pingan_buy_fast,
    run_pingan_buy_submit_once,
    run_pingan_hid_submit_probe,
    run_pingan_probe,
    set_uia_text,
    select_uia_combobox_item,
    wait_for_uia_dialog,
)
from .win32_api import (
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

PINGAN_LAST_ORDER_STATE_PATH = Path("runtime/pingan-last-order.json")
PINGAN_BUY_PROFILES: dict[str, dict[str, object]] = {
    "stable": {
        "hid_pre_delay": 0.5,
        "post_delay": 0.5,
        "dialog_timeout": 3.0,
        "confirm_timeout": 2.5,
        "confirm_post_delay": 0.3,
        "result_timeout": 2.5,
        "result_close_pre_delay": 0.0,
        "capture_final_uia": False,
        "price_quantity_input_mode": "uia",
    },
    "balanced": {
        "hid_pre_delay": 0.2,
        "post_delay": 0.2,
        "dialog_timeout": 2.0,
        "confirm_timeout": 1.5,
        "confirm_post_delay": 0.1,
        "result_timeout": 1.5,
        "result_close_pre_delay": 0.0,
        "capture_final_uia": False,
        "price_quantity_input_mode": "uia",
    },
    "fast": {
        "hid_pre_delay": 0.0,
        "post_delay": 0.1,
        "dialog_timeout": 1.2,
        "confirm_timeout": 1.0,
        "confirm_post_delay": 0.0,
        "result_timeout": 1.0,
        "result_close_pre_delay": 0.0,
        "capture_final_uia": False,
        "price_quantity_input_mode": "uia",
    },
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TongDaXin / Ping An bridge and desktop automation CLI")
    parser.add_argument("--exe-path", help="Explicit Windows or WSL path to TdxW.exe")
    parser.add_argument("--title-key", default="平安证券", help="Top-level window title keyword")

    subparsers = parser.add_subparsers(dest="command", required=True)
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
    pingan_buy_parser = subparsers.add_parser("pingan-buy")
    pingan_buy_parser.add_argument("--port", required=True)
    pingan_buy_parser.add_argument("--baudrate", type=int, default=115200)
    pingan_buy_parser.add_argument("--timeout", type=float, default=2.0)
    pingan_buy_parser.add_argument("--code", required=True)
    pingan_buy_parser.add_argument("--price", required=True)
    pingan_buy_parser.add_argument("--quantity", required=True, type=int)
    pingan_buy_parser.add_argument("--profile", choices=["stable", "balanced", "fast"], default="balanced")
    pingan_buy_parser.add_argument(
        "--price-quantity-input-mode",
        choices=["uia", "win32", "hybrid_win32"],
        help="How price/quantity edits are written in the fast path. Code input always stays on UIA.",
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
    tdx_data_sector_list_parser = subparsers.add_parser("tdx-data-sector-list")
    tdx_data_sector_list_parser.add_argument("--strategy-path")
    tdx_data_sector_stocks_parser = subparsers.add_parser("tdx-data-sector-stocks")
    tdx_data_sector_stocks_parser.add_argument("--sector", required=True)
    tdx_data_sector_stocks_parser.add_argument("--block-type", type=int, default=0, choices=[0, 1])
    tdx_data_sector_stocks_parser.add_argument("--strategy-path")
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
        tdx_data_kline_parser,
        tdx_data_stock_info_parser,
        tdx_data_sector_list_parser,
        tdx_data_sector_stocks_parser,
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
    result_dialog = result.data.get("result_dialog", {})
    contract_no = result_dialog.get("contract_no")
    return str(contract_no) if contract_no else None


def _build_pingan_last_order_state_payload(result: Result) -> dict[str, object]:
    return {
        "ok": result.ok,
        "code": result.code.value,
        "message": result.message,
        "contract_no": _resolve_pingan_contract_no(result),
        "input": result.data.get("input", {}),
        "result_dialog": result.data.get("result_dialog", {}),
        "warnings": result.warnings,
        "next_action": result.next_action,
    }


def _write_pingan_last_order_state(result: Result, state_path: Path = PINGAN_LAST_ORDER_STATE_PATH) -> Path:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(_build_pingan_last_order_state_payload(result), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state_path


def _emit_pingan_contract_log(contract_no: str | None, stream: TextIO = sys.stderr) -> None:
    if contract_no:
        print(f"[pingan-buy-submit-once] contract_no={contract_no}", file=stream)


def _resolve_pingan_buy_profile(profile_name: str) -> dict[str, object]:
    try:
        return dict(PINGAN_BUY_PROFILES[profile_name])
    except KeyError as exc:
        raise ValueError(f"unsupported pingan buy profile: {profile_name}") from exc


def _build_pingan_buy_submit_options(profile_name: str, overrides: dict[str, object]) -> dict[str, object]:
    options = _resolve_pingan_buy_profile(profile_name)
    for key, value in overrides.items():
        if value is not None:
            options[key] = value
    return options


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    adapter = PingAnBrokerAdapter(title_keyword=args.title_key, exe_path=args.exe_path)
    command_started_at = time.perf_counter()
    if args.command == "health-check":
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
        result = run_pingan_buy_submit_once(
            args.title_key,
            port=args.port,
            baudrate=args.baudrate,
            timeout=args.timeout,
            hid_pre_delay=args.hid_pre_delay,
            code=args.code,
            price=args.price,
            quantity=args.quantity,
            post_delay=args.post_delay,
            max_depth=args.max_depth,
            dialog_timeout=args.dialog_timeout,
            confirm_timeout=args.confirm_timeout,
            confirm_post_delay=args.confirm_post_delay,
            result_timeout=args.result_timeout,
            close_result_dialog=args.close_result_dialog,
            result_close_pre_delay=args.result_close_pre_delay,
            capture_final_uia=args.capture_final_uia,
        )
    elif args.command == "pingan-buy":
        profile_options = _build_pingan_buy_submit_options(
            profile_name=args.profile,
            overrides={
                "hid_pre_delay": args.hid_pre_delay,
                "post_delay": args.post_delay,
                "dialog_timeout": args.dialog_timeout,
                "confirm_timeout": args.confirm_timeout,
                "confirm_post_delay": args.confirm_post_delay,
                "result_timeout": args.result_timeout,
                "result_close_pre_delay": args.result_close_pre_delay,
                "capture_final_uia": args.capture_final_uia,
                "price_quantity_input_mode": args.price_quantity_input_mode,
            },
        )
        result = run_pingan_buy_fast(
            args.title_key,
            port=args.port,
            baudrate=args.baudrate,
            timeout=args.timeout,
            hid_pre_delay=float(profile_options["hid_pre_delay"]),
            code=args.code,
            price=args.price,
            quantity=args.quantity,
            post_delay=float(profile_options["post_delay"]),
            max_depth=args.max_depth,
            dialog_timeout=float(profile_options["dialog_timeout"]),
            confirm_timeout=float(profile_options["confirm_timeout"]),
            confirm_post_delay=float(profile_options["confirm_post_delay"]),
            result_timeout=float(profile_options["result_timeout"]),
            price_quantity_input_mode=str(profile_options["price_quantity_input_mode"]),
            close_result_dialog=args.close_result_dialog,
            result_close_pre_delay=float(profile_options["result_close_pre_delay"]),
            capture_final_uia=bool(profile_options["capture_final_uia"]),
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
    elif args.command == "tdx-data-sector-list":
        result = run_tdx_data_sector_list(strategy_path=args.strategy_path)
    elif args.command == "tdx-data-sector-stocks":
        result = run_tdx_data_sector_stocks(
            block_code=args.sector,
            block_type=args.block_type,
            strategy_path=args.strategy_path,
        )
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
    if args.command in {"pingan-buy-submit-once", "pingan-buy"}:
        if args.command == "pingan-buy":
            result.data.setdefault("execution_profile", {"name": args.profile, "options": profile_options})
        state_path = _write_pingan_last_order_state(result)
        result.data.setdefault("artifacts", {})["last_order_state_path"] = str(state_path)
        _emit_pingan_contract_log(_resolve_pingan_contract_no(result))
    serialized = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    if args.output:
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
