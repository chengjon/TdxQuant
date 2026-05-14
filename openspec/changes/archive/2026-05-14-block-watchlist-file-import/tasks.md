## 1. Import Schema And Parser

- [x] 1.1 Add focused failing tests for valid JSON watchlist import parsing and normalization.
- [x] 1.2 Add parser/validator for the explicit JSON import schema.
- [x] 1.3 Cover malformed input: missing symbols, empty symbols, and malformed symbol objects.

## 2. Dry-Run Planning

- [x] 2.1 Add focused failing tests for dry-run plan output.
- [x] 2.2 Implement plan output with source path, block code, mode, create-if-missing, normalized symbols, and symbol count.

## 3. Block Sync Wiring

- [x] 3.1 Add focused failing tests proving imported watchlists delegate to `sync_watchlist_to_block`.
- [x] 3.2 Implement `sync_watchlist_import_file(...)` adapter preserving mode, create-if-missing, dry-run, and mutation-key options.
- [x] 3.3 Update `FUNCTION_TREE.md` to mark file import status and boundaries accurately.

## 4. Verification

- [x] 4.1 Run focused block watchlist import tests.
- [x] 4.2 Run strict OpenSpec validation.
- [x] 4.3 Run `git diff --check`.
