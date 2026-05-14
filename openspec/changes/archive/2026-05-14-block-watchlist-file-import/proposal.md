## Why

Block sync already accepts an in-memory symbol list, but upstream workflows often produce watchlists as files. Without a first-class import adapter, callers must hand-roll parsing and validation before using `block.sync_watchlist`, which weakens dry-run review and error consistency.

## What Changes

- Add a file-backed watchlist import adapter with an explicit JSON schema.
- Add parser and validator behavior for block code, mode, symbols, and duplicate/invalid symbol handling.
- Add dry-run planning output that shows the normalized sync request without mutating TDX blocks.
- Wire imported watchlists into the existing `block.sync_watchlist` path so file import reuses current sync governance.
- Preserve the existing block sync contract and avoid bidirectional sync or writing back to upstream source files.

## Capabilities

### New Capabilities
- `tdx-block-watchlist-file-import`: File schema, parser/validator, dry-run plan, and sync adapter for importing watchlists into block sync.

### Modified Capabilities
- `tdx-provider-block-sync`: Block sync gains an explicit file-import adapter path that must reuse existing sync governance and dry-run semantics.

## Impact

- Affected code: new watchlist import helper module and focused block import tests.
- Affected provider path: `block.sync_watchlist` receives normalized symbols from file import but keeps existing mutation behavior.
- No new live provider capability, no bidirectional sync, and no writes to upstream source files.
