## 1. OpenSpec And Tests

- [x] 1.1 Add RED tests for finalized trade-audit artifact writing, persisted audit correlation, and non-side-effecting workflows.

## 2. Trade Audit Governance Implementation

- [x] 2.1 Add normalized trade-audit summary and immutable audit-artifact helpers to the desktop trade persistence path.
- [x] 2.2 Extend `TdxTradeManager` artifact governance so finalized workflows expose audit artifact paths and discovery-style workflows expose the audit target path.

## 3. Documentation And Verification

- [x] 3.1 Update docs to show the new trade-audit contract and the reduced remaining trade-governance gap.
- [x] 3.2 Run focused pytest, full `tests/`, compile, and OpenSpec validation; archive the change if complete.
