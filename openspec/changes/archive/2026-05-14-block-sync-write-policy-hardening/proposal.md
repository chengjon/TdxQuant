## Why

`block.sync_watchlist` already supports replace/merge sync and mutation-key replay checks, but write intent is still split across `mode`, `dry_run`, and caller convention. Making write policy explicit improves reviewability, audit artifacts, and conflict feedback before higher-level task/catalog wrappers depend on it.

## What Changes

- Add an explicit block sync write policy enum that maps to existing replace/merge/dry-run behavior.
- Add policy-derived request metadata and audit artifact fields.
- Harden mutation-key replay/conflict feedback so identical replays and conflicting requests are machine-readable.
- Add focused tests for policy mapping, replay, conflict, and audit metadata.
- Preserve existing block sync behavior and avoid changing snapshot reads or provider schema shape.

## Capabilities

### New Capabilities
- `tdx-block-sync-write-policy`: Explicit write policy contract and audit metadata for block sync write intent.

### Modified Capabilities
- `tdx-provider-block-sync`: Block sync gains policy metadata, policy validation, and stronger mutation-key replay/conflict feedback while reusing existing sync behavior.

## Impact

- Affected code: `tdxquant/block_sync.py` and focused block sync tests.
- Affected specs: new write policy capability plus block sync requirements.
- No change to `block.read_watchlist_snapshot`, no new provider schema family, and no broad task/catalog wrapper work in this slice.
