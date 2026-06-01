## Why

`execute_pingan_order` is now the internal order seam for PingAn buy, sell, and submit-once flows. Direct tests already cover successful dispatch/finalize, failed risk gate, and duplicate replay. The `reject_conflict` idempotency branch is still only covered indirectly by manager-level behavior.

Adding a direct seam test locks the conflict branch contract: no desktop dispatch, conflict result builder is used, finalize receives a conflict risk gate, and request context remains the normalized order context.

## What Changes

- Add a direct `execute_pingan_order` test for `idempotency.decision == "reject_conflict"`.
- Verify no dispatch occurs and finalize receives the expected conflict risk gate and request context.
- Update `FUNCTION_TREE.md` D-08 evidence and boundary.

## Non-Goals

- No production behavior change.
- No public CLI, task, catalog, or API changes.
- No changes to desktop primitives, artifact schemas, or runtime state paths.
- No live broker readiness, production trading readiness, or manual acceptance claim.

## Modified Capability

- `tdx-desktop-trading-management`

