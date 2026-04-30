"""Desktop trading management modules."""

from .context import (
    append_pingan_order_event,
    append_pingan_submission_ledger_entry,
    build_result_from_submission_ledger_row,
    build_trade_submission_fingerprint,
    build_pingan_last_order_state_payload,
    evaluate_trade_submission_idempotency,
    extract_pingan_contract_no,
    get_pingan_last_order_state_path,
    get_pingan_order_event_log_path,
    get_pingan_submission_ledger_path,
    get_trade_profile_path,
    load_pingan_submission_ledger_rows,
    load_trade_profiles,
    resolve_trade_profile,
    write_pingan_last_order_state,
)
from .manager import TdxTradeManager
from .preset import (
    TRADE_COMMAND_DEFAULT_PROFILES,
    get_trade_preset_path,
    load_trade_presets,
    resolve_trade_preset,
)

__all__ = [
    "TdxTradeManager",
    "append_pingan_order_event",
    "append_pingan_submission_ledger_entry",
    "build_result_from_submission_ledger_row",
    "build_trade_submission_fingerprint",
    "build_pingan_last_order_state_payload",
    "evaluate_trade_submission_idempotency",
    "extract_pingan_contract_no",
    "get_pingan_last_order_state_path",
    "get_pingan_order_event_log_path",
    "get_pingan_submission_ledger_path",
    "get_trade_profile_path",
    "get_trade_preset_path",
    "load_pingan_submission_ledger_rows",
    "load_trade_profiles",
    "load_trade_presets",
    "resolve_trade_profile",
    "resolve_trade_preset",
    "TRADE_COMMAND_DEFAULT_PROFILES",
    "write_pingan_last_order_state",
]
