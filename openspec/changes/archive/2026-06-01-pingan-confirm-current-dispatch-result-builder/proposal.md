## Why

`TdxTradeManager.pingan.confirm_current(...)` now routes through a confirm-current seam, and boundary gate rejection construction has moved into `tdxquant/trade/pingan_execution.py`. The dispatch callback still constructs confirm-current lookup failure, click failure, and advanced/warning result payloads inline in the manager.

Those payloads are pure result construction: they echo resolved request inputs, carry `confirm_current` status, checks, warnings, next action, and result dialog payload. Moving this construction behind the confirm-current seam module reduces manager-local policy without changing UI lookup/click behavior.

## What Changes

- Add a confirm-current dispatch context and pure dispatch result builder in `tdxquant/trade/pingan_execution.py`.
- Cover lookup failure and advanced/warning result shapes directly.
- Route the manager dispatch callback through the module builder while leaving UI lookup/click primitives in the manager.
- Update `FUNCTION_TREE.md` D-07 evidence and boundary.

## Non-Goals

- No public CLI, task, catalog, or API changes.
- No change to dialog lookup, Win32/UIA click behavior, result-dialog close behavior, artifact schemas, or state paths.
- No live broker readiness, production trading readiness, or manual acceptance claim.

## Modified Capability

- `tdx-desktop-trading-management`

