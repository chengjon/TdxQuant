## 1. Specification

- [x] 1.1 Add `tdx-desktop-trading-management` delta spec for confirm-current rejection result builder ownership.
- [x] 1.2 Validate the OpenSpec change before implementation.

## 2. Red Tests

- [x] 2.1 Add direct builder tests for owner-lock and broker-readiness rejection result shapes.
- [x] 2.2 Run focused builder tests and confirm they fail before the builder is exported.

## 3. Implementation

- [x] 3.1 Add confirm-current rejection context and builder in `tdxquant/trade/pingan_execution.py`.
- [x] 3.2 Route `TdxTradeManager.pingan.confirm_current(...)` through the module builder.
- [x] 3.3 Update `FUNCTION_TREE.md` D-07 evidence and boundary.

## 4. Verification

- [x] 4.1 Run focused PingAn trade manager/execution/gateway tests.
- [x] 4.2 Run `openspec validate --all --strict`.
- [x] 4.3 Run `git diff --check`.
- [x] 4.4 Run `python scripts/validate_function_tree_registry.py`.
- [x] 4.5 Archive the OpenSpec change and repeat verification.
