## Why

After the confirm-current seam extraction, `TdxTradeManager.pingan.confirm_current(...)` still owns the boundary rejection result builder for lifecycle owner-lock and broker-readiness gate failures. That builder is strategy code: it chooses failed gate identity, message, next action, result code, input echo, confirm-current status payload, and health-check shape.

Keeping it inside the manager keeps confirm-current policy spread across the manager and seam module. Moving it behind the confirm-current seam module makes D-07 easier to maintain without changing public behavior.

## What Changes

- Add a confirm-current boundary rejection context and builder in `tdxquant/trade/pingan_execution.py`.
- Cover the builder directly for owner-lock and broker-readiness rejection shapes.
- Route `TdxTradeManager.pingan.confirm_current(...)` to the module builder instead of keeping the nested manager builder.
- Update `FUNCTION_TREE.md` with D-07 evidence and boundaries.

## Non-Goals

- No public CLI, task, catalog, or API changes.
- No behavior change for dialog lookup/click/result-close paths.
- No change to artifact schemas or state paths.
- No live broker readiness, production trading readiness, or manual acceptance claim.

## Modified Capability

- `tdx-desktop-trading-management`

