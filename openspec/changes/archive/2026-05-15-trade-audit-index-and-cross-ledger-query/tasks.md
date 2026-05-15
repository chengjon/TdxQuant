## 1. Contract Tests

- [x] 1.1 Add focused failing tests for trade audit index cache shape and corrupt audit tolerance.
- [x] 1.2 Add focused failing tests for exact-key cross-ledger joins and damaged JSONL tolerance.
- [x] 1.3 Add focused failing tests for manager/CLI read-only query entrypoint.

## 2. Core Implementation

- [x] 2.1 Implement normalized trade audit index cache helpers.
- [x] 2.2 Implement read-only submission/task ledger loaders with warnings for malformed rows.
- [x] 2.3 Implement cross-ledger join, filters, newest-first ordering, limits, and summary metadata.

## 3. Task And CLI Wiring

- [x] 3.1 Add `TdxTaskManager` query method with task metadata and export/cache artifact support.
- [x] 3.2 Add task CLI parsing and dispatch for the read-only query.
- [x] 3.3 Register default task/report profile mappings where the existing preset system expects them.

## 4. Registry And Specs

- [x] 4.1 Update `FUNCTION_TREE.md` status/evidence/boundary for the audit index/cross-ledger node.
- [x] 4.2 Run strict OpenSpec validation for the active change.

## 5. Verification

- [x] 5.1 Run focused task/audit tests.
- [x] 5.2 Run strict OpenSpec validation for all specs.
- [x] 5.3 Run `git diff --check`.
