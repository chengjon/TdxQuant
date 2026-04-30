## 1. OpenSpec And Tests

- [x] 1.1 Add trade manager tests for `submission_key`, `trade_safety`, and pre-trade rejection behavior.
- [x] 1.2 Add CLI parser and dispatch tests for safety-control arguments on nested, flat, and preset-driven trade commands.

## 2. Trade Safety Implementation

- [x] 2.1 Implement shared trade safety helpers and artifact payload updates in `tdxquant/trade/context.py`.
- [x] 2.2 Extend `TdxTradeManager` stable Ping An workflows to run the pre-trade risk gate and attach normalized safety metadata.
- [x] 2.3 Extend stable trade CLI entrypoints to parse and forward `submission_key` and `max_price`.

## 3. Documentation And Verification

- [x] 3.1 Update project docs and function map to reflect the first trade safety hardening slice.
- [x] 3.2 Run focused pytest, compile, and OpenSpec validation for the new change.
