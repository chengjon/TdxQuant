# Design

## Scope

This change covers only `meta.ipo_info`. It does not add replay support for other remaining E-07 edge capabilities.

## Fixture Shape

The `meta-ipo-info-success` fixture follows the existing synchronous provider-result JSON contract:

- `capability`: `meta.ipo_info`
- `data.rows`: representative IPO metadata rows
- `data.query_meta`: `query_kind`, `row_count`, `requested_fields`, `returned_fields`, `ipo_type`, `ipo_date`, and `query_params`
- `runtime.mode`: `replay`

## Replay Dispatch

`TdxApiManager.meta.ipo_info(...)` will use `_dispatch_sync_capability("meta.ipo_info", live_call)` so replay mode resolves the fixture and live mode continues to call the existing bridge implementation.

## CLI Entry Points

Replay mode should be available only when explicitly requested:

- `api ipo-info --provider-mode replay`
- `tdx-data-ipo-info --provider-mode replay`

The flat command keeps the existing provider envelope semantics while sourcing data from the manager replay path.

