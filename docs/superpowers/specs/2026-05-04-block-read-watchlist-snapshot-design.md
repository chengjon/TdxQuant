# Block Read Watchlist Snapshot Design

Date: 2026-05-04
Topic: `block-read-watchlist-snapshot`

## Goal

Add a stable provider-level read capability that converts one TongDaXin custom sector into a normalized watchlist snapshot for upper-layer systems.

This capability is read-only. It does not write back to any upper-layer system, and it does not export files in v1.

## Why This Exists

The project already has a stable forward sync path:

- `watchlist -> TongDaXin block`
- `block.sync_watchlist(...)`

What is still missing is the reverse read path:

- `TongDaXin block -> normalized watchlist snapshot`

Without that reverse path, upper layers still need to:

- call raw block read APIs,
- normalize symbol formats,
- deduplicate members,
- distinguish missing block vs empty block,
- and build their own read contract repeatedly.

This design creates a dedicated provider capability for that snapshot instead of exposing raw custom-sector data directly.

## Relationship To Existing Read APIs

This capability is not a new raw data source. V1 should be implemented as a normalized wrapper around the existing raw block-member read path:

- Python raw read today: `manager.meta.sector_stocks(...)`
- Bridge/runtime raw read today: the existing sector-stocks bridge path behind `MetaApi.sector_stocks(...)`

In practice, the current bridge/runtime implementation is a two-step read:

1. query `user_sectors` to confirm the custom sector exists and resolve `sector_name`
2. query `sector_stocks` to read raw members

This extra existence check is what allows V1 to distinguish:

- missing block
- existing but empty block

The boundary is:

- `meta.sector_stocks`
  - remains the raw TongDaXin sector-member query
  - keeps its existing query-oriented shape
  - may expose raw member rows and query metadata
- `block.read_watchlist_snapshot`
  - is a higher-level provider capability
  - reads a single custom sector
  - normalizes members into a stable watchlist snapshot
  - distinguishes missing block vs empty block
  - deduplicates and preserves first-seen order

So this is a **wrapper capability**, not a replacement for `meta.sector_stocks`.

## Scope

### In Scope

- One dedicated provider capability for reading a single block into a normalized watchlist snapshot
- Python manager entrypoint
- Nested CLI entrypoint
- Flat CLI compatibility entrypoint
- Replay fixtures
- Capability discovery metadata

### Out of Scope

- Task-layer wrapper
- CSV / JSON / watchlist file export
- Writing back to an upper-layer system
- Batch export of multiple blocks
- Bidirectional sync orchestration

## Recommended Interface

### Python

```python
manager.block.read_watchlist_snapshot(block_code="ZXG")
```

### Nested CLI

```bash
tdxquant api block-read-watchlist --block-code ZXG
```

### Flat CLI

```bash
tdxquant tdx-block-read-watchlist --block-code ZXG
```

## Request Contract

V1 request is intentionally minimal.

### Required

- `block_code`

### Not Included In V1

- `dry_run`
- `mode`
- `mutation_key`
- `show`
- `request_label`

This is a pure read capability, so it should not inherit write/sync controls.

## Response Contract

The capability returns a normalized watchlist snapshot, not raw TongDaXin block rows.

### Top-Level

- `success`
- `code`
- `message`
- `warnings`
- `artifacts`
- `data.snapshot`

### `data.snapshot`

- `block_code`
- `symbols`
- `symbol_count`
- `source`
- `source_metadata`

### `symbols`

Rules:

- normalized to standard symbol form, e.g. `000001.SZ`, `600519.SH`
- preserves the original TongDaXin member order
- deduplicates repeated members by first occurrence

### `symbol_count`

- equals the final normalized symbol count
- does not equal raw block row count if deduplication occurred

### `source`

V1 fixed value:

- `tongdaxin.custom_sector`

### `source_metadata`

Minimum V1 fields:

- `sector_name`
- `raw_member_count`
- `duplicate_count`

Where:

- `raw_member_count` is the raw member count before deduplication
- `duplicate_count` is the number of removed duplicate members

## Semantic Rules

### 1. Missing Block

If `block_code` does not exist:

- return a stable failure
- do not return an empty snapshot

Reason:

- “missing block” and “existing empty block” are different states
- treating missing as empty could cause destructive upper-layer sync behavior

Recommended behavior:

- `success=false`
- `code=invalid_request`
- failure message mentions the missing `block_code`
- `warnings=[]`

### 2. Empty Block

If the block exists but has no members:

- return success
- `symbols=[]`
- `symbol_count=0`

This is a successful empty snapshot.

### 3. Order Preservation

The output `symbols` list preserves TongDaXin’s original member order.

Do not sort it.

Reason:

- preserves the most information
- upper layers that want set semantics can sort later
- upstream order cannot be recovered if we reorder first

### 4. Duplicate Members

If the raw block contains repeated codes:

- deduplicate by first occurrence
- preserve the first-seen order

This makes the output match a stable watchlist contract instead of a raw row dump.

If `duplicate_count > 0`, the capability should also append a stable warning indicating that repeated members were removed from the snapshot.

### 5. Symbol Normalization

Successful results always return normalized symbols:

- `000001.SZ`
- `600519.SH`

This should match the same symbol contract already used by `block.sync_watchlist`.

### 6. Invalid or Non-Normalizable Members

If a block contains members that cannot be normalized:

- return a stable failure
- do not silently skip those members

Reason:

- this capability promises a normalized snapshot
- silently dropping invalid members would make the snapshot look complete when it is not

Recommended outcome:

- `success=false`
- `code=invalid_request`
- machine-readable error detail may include sample invalid members

### 7. Invalid `block_code` Input

If `block_code` is empty, blank, or fails the accepted block-code format:

- return a stable validation failure
- do not treat it as a missing block

Recommended outcome:

- `success=false`
- `code=invalid_request`
- `message` identifies invalid `block_code` input rather than missing runtime state

## Replay Fixtures

Minimum representative fixture set:

1. `block-read-watchlist-success.json`
   - block exists
   - has members
   - returns normalized, deduplicated symbols

2. `block-read-watchlist-empty.json`
   - block exists
   - has zero members
   - returns success with `symbols=[]`

3. `block-read-watchlist-missing-block.json`
   - block does not exist
   - returns stable failure

4. `block-read-watchlist-invalid-member.json`
   - block exists
   - contains at least one non-normalizable member
   - returns stable failure

5. optional but recommended: `block-read-watchlist-invalid-block-code.json`
   - request block code is blank or malformed
   - returns stable validation failure

V1 does not require replay coverage for blank or malformed `block_code` if that validation is already locked by focused logic tests before the bridge/runtime layer. In the current implementation, this remains an optional fixture rather than a required replay artifact.

## Capability Discovery Metadata

This capability should appear in `runtime.capabilities` with query-oriented metadata.

Recommended metadata:

- `name=block.read_watchlist_snapshot`
- `domain=block`
- `stability`
- `side_effect_level=read_only`
- `supports_replay=true`
- `query_metadata`
  - `query_shapes=[{ "query_kind": "block.read_watchlist_snapshot", "selectors": ["block_code"], "query_params": [] }]`
  - `supports_empty_results=true`

Implementation note:

- this should reuse the same discovery extension point already used by query-contract hardening
- i.e. capability metadata should be registered through the existing discovery path that already emits `query_metadata`
- this change should not introduce a second parallel metadata registration model

This lets upper layers know:

- it is read-only,
- it only accepts one `block_code`,
- and it returns a stable query-shaped watchlist snapshot.

Behavior such as:

- preserving original member order
- deduplicating repeated members
- normalizing symbols

remains part of the capability contract itself and replay fixtures, not additional `query_metadata` fields in V1 discovery output.

## Why V1 Does Not Add Task or Export

This work is intended to stabilize the provider-level read contract first.

So v1 explicitly does not add:

- `task block-read-watchlist`
- file export
- direct upper-layer writeback

The sequence should be:

1. provider-level read capability
2. optional task wrapper
3. optional export or orchestration

This prevents the task layer or export workflow from defining the canonical contract by accident.

## Testing Focus

V1 should at least lock:

- success snapshot with normalization and deduplication
- empty block success
- missing block stable failure
- invalid block code stable failure
- invalid member stable failure
- order preservation
- replay fixture coverage
- capability discovery metadata

## Open Questions

- None for v1. The main behavior and scope decisions are already fixed.

## Forward-Looking Note

V1 intentionally uses `invalid_request` for several distinct failure classes, including:

- blank or malformed `block_code`
- missing block
- non-normalizable members

This keeps the first version aligned with the current `ErrorCode` surface. If upper layers later need machine-readable branching between “missing block” and “invalid block contents”, V2 may need to split these failure modes into narrower error-code classes.
