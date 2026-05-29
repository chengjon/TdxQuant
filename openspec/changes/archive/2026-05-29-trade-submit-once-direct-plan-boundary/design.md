## Design

The change treats the direct trade-source `submit-once` catalog entry like the existing task submit-once entries for planning purposes.

`runtime/trade-presets.json` keeps routing through the existing `submit-once` command but makes its default `side=buy` explicit in preset options. This mirrors current execution behavior, where direct submit-once defaults to buy when no side is provided.

`tdxquant/cli.py` extends `CATALOG_TRADE_PLAN_REQUIRED_FIELDS` and `CATALOG_TRADE_PLAN_INPUT_KIND` for command name `submit-once`. The existing boundary builder then reports required/provided/missing fields and includes side metadata for direct and task submit-once plans.

## Boundaries

- `catalog plan` and `catalog preview` remain non-executing and must not dispatch the trade preset.
- The change does not execute `trade submit-once`, task workflows, reports, bundles, providers, buy/sell, submit-ready, or confirm-current.
- The direct trade-source entry still uses existing submit-once behavior; this does not create a new desktop execution primitive.
- The default side projection is catalog/preset metadata and does not prove real broker readiness, safety approval, or production trading availability.

