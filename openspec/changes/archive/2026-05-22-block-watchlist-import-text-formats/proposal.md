## Why

`FUNCTION_TREE.md` E-03 still registers block watchlist file import as partial because the current adapter is JSON-only. Operators commonly maintain watchlists as simple CSV exports or TXT symbol lists, and forcing those through the JSON schema adds avoidable manual conversion before they can use the existing dry-run and guarded block sync path.

## What Changes

- Extend `load_watchlist_import_file(...)` to accept CSV and TXT inputs in addition to the existing JSON schema.
- Normalize text imports into the existing `WatchlistImportRequest` contract so `plan_watchlist_import(...)`, task dry-run, and guarded sync delegation keep the same behavior.
- Add validation for missing `block_code`, missing symbols, malformed rows, and conflicting CSV block codes before block sync is invoked.
- Update `FUNCTION_TREE.md` E-03 with explicit evidence and boundaries for JSON/CSV/TXT import.

## Non-Goals

- No source file writeback or bidirectional sync.
- No new block sync write policy semantics.
- No live provider bypass; all execution still flows through existing `block.sync_watchlist` governance.
- No new catalog workflow builder.

