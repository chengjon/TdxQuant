# PingAn Confirm-Current Handler Bundle

## Why

D-07 has already moved PingAn confirm-current request preparation, gate rejection result construction, and dispatch result envelope construction into the internal execution seam. The remaining call into `execute_pingan_confirm_current(...)` still passes several result callbacks as separate keyword arguments, unlike the order seam which now groups equivalent callbacks behind an internal handler bundle.

Grouping the confirm-current callbacks gives the confirm seam the same bounded call shape as the order seam: one request, one gate, one dispatch callback, and one handler object for result policy. This keeps follow-up D-07 work focused on execution locality without changing public manager behavior.

## What Changes

- Add an internal `PingAnConfirmCurrentExecutionHandlers` bundle for confirm-current rejection, metadata, safety metadata, and finalize callbacks.
- Let `execute_pingan_confirm_current(...)` accept `handlers=` while keeping the existing individual callback keyword arguments as compatibility inputs.
- Route the `TdxTradeManager.pingan.confirm_current(...)` manager callsite through the grouped handler object.
- Add focused tests proving the handler bundle path preserves confirm-current timing, metadata, safety, finalize, and dispatch behavior.
- Register the D-07 evidence and boundary in `FUNCTION_TREE.md`.

## Non-Goals

- No public CLI, task, catalog, or API changes.
- No workflow builder, desktop primitive extraction, broker readiness claim, or production trading readiness claim.
- No change to dialog lookup, Win32/UIA click behavior, result-dialog close behavior, artifact schemas, state paths, or audit schemas.
- No removal of legacy individual callback keyword arguments.

## Modified Capability

- `tdx-desktop-trading-management`
