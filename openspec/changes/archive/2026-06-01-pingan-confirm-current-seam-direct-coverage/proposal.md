## Why

`TdxTradeManager.pingan.confirm_current(...)` now routes through the internal `PingAnConfirmCurrentExecutionRequest` / `execute_pingan_confirm_current` seam. The manager delegation test proves the routing boundary, but the seam itself should have direct tests for its three behavioral branches:

- rejected gate returns without UI dispatch,
- non-advanced confirm result receives manager/safety metadata without finalized artifact writes,
- advanced confirm result finalizes through the manager artifact path.

Direct seam coverage reduces the chance that a later manager cleanup changes confirm-current semantics by accident.

## What Changes

- Add direct tests for `execute_pingan_confirm_current`.
- Verify gate rejection does not dispatch and attaches `side_effect_level=none`.
- Verify non-advanced dispatch attaches metadata and safety data without finalize.
- Verify advanced dispatch calls finalize with `request_context=None` and `method=confirm_current`.

## Non-Goals

- No production code behavior change.
- No public CLI, task, catalog, or API changes.
- No changes to dialog lookup, Win32/UIA click behavior, artifact schemas, or runtime state paths.
- No live broker readiness, production trading readiness, or manual acceptance claim.

## Modified Capability

- `tdx-desktop-trading-management`

