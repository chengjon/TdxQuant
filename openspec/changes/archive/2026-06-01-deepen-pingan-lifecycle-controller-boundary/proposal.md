## Why

PingAn lifecycle supervisor control is implemented and tested, but the supervisor tick path still mixes owner-lock gate evaluation, broker health probing, restart/backoff decision-making, statefile writes, and optional recorded-PID process restart in one large function. A controller decision boundary will make the high-risk lifecycle path easier to test and extend without changing real desktop automation behavior.

## What Changes

- Add a dedicated PingAn lifecycle controller boundary for supervisor owner-gate and restart/backoff decisions.
- Route the existing PingAn lifecycle supervisor tick through that controller boundary for the selected pure decision steps.
- Preserve existing `TdxTradeManager.pingan.lifecycle_supervisor_tick(...)` and `lifecycle_supervisor_run(...)` public behavior.
- Keep actual process restart, broker health check, owner lock statefile writes, and desktop UI automation on the existing guarded paths.
- Add tests for the controller boundary and existing trade manager behavior.
- Update `FUNCTION_TREE.md` evidence after implementation.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-desktop-trading-management`: PingAn lifecycle supervisor gains an explicit controller decision boundary while preserving existing lifecycle control behavior.

## Impact

- Affected code: `tdxquant/trade/manager.py`, new lifecycle controller module under `tdxquant/trade/`.
- Affected tests: focused lifecycle tests in `tests/test_trade_manager.py`.
- Affected docs/evidence: `FUNCTION_TREE.md`, archived OpenSpec change, and `tdx-desktop-trading-management` spec.
- No command-line interface change.
- No broker automation, order submission, UIA/HID, or process execution semantic change.
