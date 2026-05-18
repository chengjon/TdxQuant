# Design

## Scope

This change covers only `meta.gb_info`. It does not add replay support for `meta.ipo_info` or other remaining E-07 edge capabilities.

## Fixture Shape

The `meta-gb-info-success` fixture follows the existing synchronous provider-result JSON contract:

- `capability`: `meta.gb_info`
- `data.rows`: representative bonus-share/dividend metadata rows
- `data.query_meta`: `query_kind`, `row_count`, `requested_fields`, `returned_fields`, `symbol`, and `query_params`
- `runtime.mode`: `replay`

## Replay Dispatch

`TdxApiManager.meta.gb_info(...)` will use `_dispatch_sync_capability("meta.gb_info", live_call)` so replay mode resolves the fixture and live mode continues to call the existing bridge implementation.

## CLI Entry Points

Replay mode should be available only when explicitly requested:

- `api gb-info --provider-mode replay`
- `tdx-data-gb-info --provider-mode replay`

The flat command keeps the existing provider envelope semantics while sourcing data from the manager replay path.

