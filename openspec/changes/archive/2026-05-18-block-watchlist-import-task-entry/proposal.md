# block-watchlist-import-task-entry

## Why

`FUNCTION_TREE.md` E-03 records that JSON watchlist import has a core adapter but lacks CLI/catalog/task wrapper coverage. Operators can validate and sync an import file through Python APIs, but there is no stable task/catalog entry that exposes the workflow in the same daily command surface as other block watchlist tasks.

This change adds a thin task-level wrapper and catalog entry for the existing JSON-only import adapter. It keeps the source file schema and block sync safety model unchanged.

## What Changes

- Add task CLI parsing and dispatch for `task block-watchlist-import`.
- Add task preset and command catalog entries for a plan-oriented ZXG JSON watchlist import.
- Add focused parser, dispatch, and catalog plan tests.
- Update `FUNCTION_TREE.md` E-03 evidence and boundary.

## Capabilities

### Modified Capabilities

- `tdx-block-watchlist-file-import`
- `tdx-command-catalog`

## Impact

- Runtime behavior: no new file schema, no CSV/TXT support, no source-file writeback.
- Safety: import execution still delegates to existing `block.sync_watchlist` governance and mutation audit behavior.
- CLI/catalog: new wrapper is a stable entry point; catalog plan remains non-executing.
