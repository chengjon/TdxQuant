# Design

## Scope

This change covers only `market.cb_info`. It does not add replay support for `meta.gb_info`, `meta.ipo_info`, or other remaining E-07 edge capabilities.

## Fixture Shape

The `market-cb-info-success` fixture follows the existing synchronous provider-result JSON contract:

- `capability`: `market.cb_info`
- `data.rows`: representative convertible-bond metadata rows
- `data.query_meta`: `query_kind`, `row_count`, `requested_fields`, `returned_fields`, `symbol`, and `query_params`
- `runtime.mode`: `replay`

## Replay Dispatch

`TdxApiManager.market.cb_info(...)` will use `_dispatch_sync_capability("market.cb_info", live_call)` so replay mode resolves the fixture and live mode continues to call the existing bridge implementation.

## CLI Entry Points

Replay mode should be available only when explicitly requested:

- `api cb-info --provider-mode replay`
- `tdx-data-cb-info --provider-mode replay`

The flat command keeps the existing provider envelope semantics while sourcing data from the manager replay path.
