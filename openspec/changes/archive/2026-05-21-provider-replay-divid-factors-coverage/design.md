# Design

## Scope

This change covers only `meta.divid_factors`. It does not add replay support for transaction by-date variants or other remaining E-07 edge capabilities.

## Fixture Shape

The `meta-divid-factors-success` fixture follows the existing synchronous provider-result JSON contract:

- `capability`: `meta.divid_factors`
- `data.rows`: representative dividend-factor rows for a requested symbol and date range
- `data.query_meta`: `query_kind`, `row_count`, `requested_fields`, `returned_fields`, `symbol`, `start_time`, `end_time`, and `query_params`
- `runtime.mode`: `replay`

## Replay Dispatch

`TdxApiManager.meta.divid_factors(...)` will use `_dispatch_sync_capability("meta.divid_factors", live_call)` so replay mode resolves the fixture and live mode continues to call the existing bridge implementation.

## CLI Entry Points

Replay mode should be available only when explicitly requested:

- `api divid-factors --provider-mode replay`
- `tdx-data-divid-factors --provider-mode replay`

The flat command keeps the existing provider envelope semantics while sourcing data from the manager replay path.

