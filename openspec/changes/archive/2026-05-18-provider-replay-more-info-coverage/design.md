# Design

## Scope

This change covers only `market.more_info`. It does not add replay support for `market.cb_info`, `meta.gb_info`, `meta.ipo_info`, or other remaining E-07 edge capabilities.

## Fixture Shape

The new `market-more-info-success` fixture follows the existing synchronous provider-result JSON contract:

- `capability`: `market.more_info`
- `data.rows`: representative domain-native metadata rows
- `data.query_meta`: `query_kind`, `row_count`, `requested_fields`, `returned_fields`, `symbol`, and `query_params`
- `runtime.mode`: `replay`

## Replay Dispatch

`TdxApiManager.market.more_info(...)` will wrap its live bridge call in:

```python
self._manager._dispatch_sync_capability("market.more_info", live_call)
```

The replay default fixture map will register:

```python
"market.more_info": "market-more-info-success"
```

## CLI Entry Points

The nested API and flat data commands should both opt into the manager replay path only when the caller explicitly passes `--provider-mode replay`:

- `api more-info --provider-mode replay`
- `tdx-data-more-info --provider-mode replay`

Live command behavior and output envelope semantics remain unchanged.
