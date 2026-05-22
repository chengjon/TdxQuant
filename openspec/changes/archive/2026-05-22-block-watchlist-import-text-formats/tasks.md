## 1. Tests

- [x] 1.1 Add failing parser tests for CSV and TXT watchlist imports.
- [x] 1.2 Add failing validation tests for malformed text imports.
- [x] 1.3 Add a failing task dry-run test proving text imports reuse the existing task path.

## 2. Implementation

- [x] 2.1 Add CSV/TXT format detection and parsers in `tdxquant/block_watchlist_import.py`.
- [x] 2.2 Preserve existing JSON behavior and normalize text imports into `WatchlistImportRequest`.
- [x] 2.3 Add representative runtime text-format sample files if useful for operator discovery.
- [x] 2.4 Update `FUNCTION_TREE.md` E-03 evidence and boundary without claiming bidirectional sync or source writeback.

## 3. Verification

- [x] 3.1 Run focused pytest for block watchlist import and API CLI coverage.
- [x] 3.2 Run OpenSpec strict validation, `git diff --check`, and the FUNCTION_TREE registry validator.
- [x] 3.3 Archive the OpenSpec change, rerun verification, and commit the completed slice.
