## Context

The manager callsites for `buy`, `buy_submit_once`, `sell`, and `sell_submit_once` all pass the same group of profile-derived values to desktop runner functions. Some paths use the fast order fields `price_quantity_input_mode` and `dialog_lookup_mode`; the buy submit-once path does not.

## Design

Add `PingAnOrderDispatchOptions` in `tdxquant/trade/pingan_execution.py` with normalized fields:

- serial/runtime fields: `port`, `baudrate`, `timeout`
- profile/callsite timing fields: `hid_pre_delay`, `post_delay`, `max_depth`, `dialog_timeout`, `confirm_timeout`, `confirm_post_delay`, `result_timeout`
- result behavior fields: `close_result_dialog`, `result_close_pre_delay`, `capture_final_uia`
- optional fast path fields: `price_quantity_input_mode`, `dialog_lookup_mode`

The object exposes:

- `base_kwargs(code, price, quantity)` for runners that do not accept input-mode lookup fields
- `fast_kwargs(code, price, quantity)` for `run_pingan_buy_fast` / `run_pingan_sell_fast`

Add `TdxTradeManager._build_pingan_order_dispatch_options(...)` to combine callsite arguments and profile options into that object. Order callsites continue to choose the desktop runner and pass `**options.base_kwargs(...)` or `**options.fast_kwargs(...)`.

## Non-Goals

- No movement of desktop UIA/HID runner functions into the execution module.
- No change to `execute_pingan_order` behavior.
- No change to public CLI/task/catalog arguments or registry.
- No live broker readiness or production trading readiness evidence.
