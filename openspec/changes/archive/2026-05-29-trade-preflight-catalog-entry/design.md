## Design

The change reuses the existing `trade preflight` implementation and only registers it for catalog discovery/planning.

`runtime/trade-presets.json` receives a preset whose `command` is `preflight`. The preset supplies stable environment defaults (`profile`, `title_key`, `port`, `baudrate`, `timeout`, `pre_delay`) while leaving order-shaped inputs (`code`, `price`, `quantity`) caller-provided.

`runtime/command-catalog.json` receives a source `trade` entry named `trade-preflight-pingan-readiness`. `catalog plan` and `catalog preview` already resolve source `trade` presets without dispatching; this change extends their trade boundary map so `preflight` reports the same required input coverage fields as order-shaped trade commands, with `input_kind=preflight_order_readiness`.

## Boundaries

- The catalog path is read-only for `plan` and `preview`; it must not dispatch `trade preflight`.
- Registering the entry does not execute buy, sell, submit-once, submit-ready, confirm-current, task, report, or bundle steps.
- The entry does not claim full workflow-builder support or production trading readiness.
- A direct `catalog run --entry trade-preflight-pingan-readiness` would invoke the existing read-only `trade preflight` path; this change does not alter that workflow's desktop/provider behavior.

