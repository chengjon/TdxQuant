## Design

The change registers the existing `trade health` workflow for catalog discovery and non-executing planning.

`runtime/trade-presets.json` receives a preset whose `command` is `health`. The preset supplies stable defaults for the PingAn desktop health probe, including a serial `port` so the planned input boundary can show whether the health check would include HID ping coverage.

`runtime/command-catalog.json` receives a source `trade` entry named `trade-health-pingan-readiness`. `catalog plan` and `catalog preview` resolve source `trade` presets without dispatching; this change extends the trade boundary map so `health` reports `input_kind=desktop_health_readiness` and port coverage.

## Boundaries

- The catalog path is read-only for `plan` and `preview`; it must not dispatch `trade health`.
- Registering the entry does not execute buy, sell, submit-once, submit-ready, confirm-current, task, report, provider, or bundle steps.
- The entry does not claim full workflow-builder support, production trading readiness, or broker liveness.
- A direct `catalog run --entry trade-health-pingan-readiness` would invoke the existing read-only `trade health` path; this change does not alter that workflow's desktop/provider behavior.

