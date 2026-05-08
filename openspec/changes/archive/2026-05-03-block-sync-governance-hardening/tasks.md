## 0. Prerequisite Governance Alignment

- [x] 0.1 Verify the archived `block-write-governance-hardening` implementation state against current bridge code and document the exact gaps that block sync depends on.
- [x] 0.2 Upgrade the five block write bridges to the current `apply_block_mutation_safety(...)` governance signature by passing deferred `execute_write` callbacks and real `observed_state` probes before any runtime write occurs.

## 1. Block Sync Capability Core

- [x] 1.1 Add a dedicated block sync orchestration entrypoint that accepts normalized sync requests and coordinates state probes plus execution planning.
- [x] 1.2 Add canonical symbol normalization and diff computation helpers for `observed_symbols`, `desired_symbols`, `added_symbols`, `removed_symbols`, and `unchanged_symbols`.
- [x] 1.3 Implement `replace` and `merge` decision rules on top of the shared diff computation.
- [x] 1.4 Implement `create_if_missing`, `show`, and `dry_run` semantics without bypassing the existing governance decision flow.
- [x] 1.5 Add sync-level `mutation_key` replay/conflict handling based on the canonical sync request rather than on a single underlying write.

## 2. Manager And CLI Integration

- [x] 2.1 Expose the new capability through `TdxApiManager.block.sync_watchlist(...)` while keeping current block write entrypoints unchanged.
- [x] 2.2 Add nested `api block-sync` and flat `tdx-block-sync` CLI entrypoints with stable argument parsing for `mode`, `create_if_missing`, `dry_run`, `show`, and `mutation_key`.
- [x] 2.3 Return a stable sync-focused result contract with `data.sync`, `created_block`, `would_create_block`, underlying `data.block_mutation` metadata, and audit artifact descriptors.

## 3. Governance Reuse, Fixtures, And Tests

- [x] 3.1 Reuse existing `block_mutation` governance and audit logic for real writes triggered by block sync, including create-then-send flows, without reusing the sync-level `mutation_key` as the underlying write mutation key.
- [x] 3.2 Add representative replay fixtures for block sync applied, noop, rejected, and dry-run plan outcomes using a documented naming convention.
- [x] 3.3 Add targeted tests covering `replace`, `merge`, `create_if_missing`, `dry_run`, `show`, and sync-level `mutation_key` replay/conflict behavior across bridge, manager, and CLI layers.
- [x] 3.4 Add error-path tests for empty symbol input, state-probe failure, and partial create-then-send failure.

## 4. Docs And Validation

- [x] 4.1 Update block sync, block mutation safety, replay fixture, Function Map, and Next Steps documentation to reflect the new capability and remaining roadmap.
- [x] 4.2 Run targeted pytest coverage and `openspec validate block-sync-governance-hardening --type change --strict`.
