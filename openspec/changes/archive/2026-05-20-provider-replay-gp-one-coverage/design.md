# Design

## Scope

This change covers only `meta.gp_one_data`. It does not add replay support for `meta.divid_factors`, transaction by-date variants, or other remaining E-07 edge capabilities.

## Fixture Shape

The `meta-gp-one-success` fixture follows the existing synchronous provider-result JSON contract:

- `capability`: `meta.gp_one_data`
- `data.rows`: representative per-security metadata rows for requested symbols and fields
- `data.query_meta`: `query_kind`, `row_count`, `requested_fields`, `returned_fields`, `symbols`, and `query_params`
- `runtime.mode`: `replay`

## Replay Dispatch

`TdxApiManager.meta.gp_one_data(...)` will use `_dispatch_sync_capability("meta.gp_one_data", live_call)` so replay mode resolves the fixture and live mode continues to call the existing bridge implementation.

## CLI Entry Points

Replay mode should be available only when explicitly requested:

- `api gp-one --provider-mode replay`
- `tdx-data-gp-one --provider-mode replay`

The flat command keeps the existing provider envelope semantics while sourcing data from the manager replay path.

