## Context

`tdxquant.block_sync.sync_watchlist_to_block(...)` already owns the block mutation decision path, including normalization, dry-run behavior, audit artifacts, and mutation-key replay/conflict checks. The missing piece is a stable adapter for file-sourced watchlists.

## Goals / Non-Goals

**Goals:**

- Define one explicit JSON input schema for watchlist import.
- Normalize and validate symbols before sync.
- Provide a dry-run plan that callers can review without invoking live block writes.
- Connect file import to existing `sync_watchlist_to_block(...)` rather than creating a second sync implementation.

**Non-Goals:**

- No CSV/TXT import in this first slice.
- No bidirectional sync.
- No source-file rewrite or upstream system writeback.
- No new provider mutation semantics beyond existing `block.sync_watchlist`.

## Decisions

1. Use JSON-only schema for the first slice.
   - The file must be a JSON object with `schema_version`, `block_code`, optional `block_name`, optional `mode`, optional `create_if_missing`, optional `mutation_key`, and `symbols`.
   - `symbols` may contain strings or objects with a `symbol` field so upstream exports can preserve metadata without forcing this adapter to model it.

2. Keep validation separate from execution.
   - `load_watchlist_import_file(...)` returns normalized request data.
   - `plan_watchlist_import(...)` returns a dry-run-oriented plan.
   - `sync_watchlist_import_file(...)` delegates to `sync_watchlist_to_block(...)`.

3. Reuse existing sync governance.
   - Imported symbols are passed into `sync_watchlist_to_block(...)` with explicit `dry_run`, `mode`, `create_if_missing`, and `mutation_key`.
   - This avoids duplicate mutation rules and keeps audit behavior owned by block sync.

## Risks / Trade-offs

- JSON-only support may be narrower than some upstream exports. This keeps the first contract precise; CSV/TXT can be added later with explicit schema tests.
- Object symbols preserve only the `symbol` field for sync. Other fields remain source metadata, not block sync contract inputs.

## Migration

No migration is required. Existing `block.sync_watchlist` callers continue to pass in-memory symbol lists. File import is additive.

## Open Questions

- Whether future slices should add CSV/TXT parsers.
- Whether catalog/task/CLI wrappers should expose this adapter after the core contract stabilizes.
