# Design

## Scope

This change adds one representative stock-info query replay path. It does not attempt to close all remaining E-07 fixture gaps.

## Fixture Shape

The new fixture uses the existing synchronous provider-result JSON shape:

- `capability`: `market.stock_info`
- `data.rows`: representative domain-native rows
- `data.query_meta`: hardened query metadata with `query_kind`, `query_params`, `requested_fields`, `selectors`, and row count information
- `runtime.provider_mode`: `replay`

This keeps the fixture compatible with `build_replay_result(...)` and the existing provider result contract.

## Replay Dispatch

`TdxApiManager.market.stock_info(...)` will call `_dispatch_sync_capability("market.stock_info", live_call)` so replay mode resolves a fixture and live mode continues to call the existing bridge implementation.

The default fixture map will add:

```python
"market.stock_info": "market-stock-info-success"
```

## CLI Entry Points

Two CLI surfaces should be covered:

- `api stock-info --provider-mode replay`
- `tdx-data-stock-info --provider-mode replay`

Both routes should instantiate `TdxApiManager(provider_mode="replay", ...)` and avoid the live stock-info bridge. The flat command keeps the existing flat provider envelope behavior while sourcing the data from the manager replay path.

## Boundaries

- This does not add replay fixtures for `market.more_info`, `market.cb_info`, `meta.gb_info`, `meta.ipo_info`, or other uncovered edge queries.
- This does not change live TongDaXin runtime behavior.
- This does not make replay mode implicit; callers still opt in with `provider_mode="replay"` or `--provider-mode replay`.
