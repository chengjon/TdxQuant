## Design

The aggregation is a pure projection over the same `filtered_entries` used by the existing cross-ledger query. It runs before `limit` is applied so users can request a small row sample while still seeing counts for the complete filtered set.

The returned payload gains an `aggregation` object:

- `by_status`: count rows by normalized status string.
- `by_method`: count rows by normalized method string.
- `by_broker`: count rows by normalized broker string.
- `by_broker_method_status`: rows containing `broker`, `method`, `status`, and `count`.

Missing dimension values are represented as `"unknown"` so the summary remains deterministic and does not drop malformed but indexable audit entries.

## Boundary

The aggregation is count-only and read-only. It does not compute amount, price, quantity, PnL, execution quality, or risk metrics.

