## Why

D-07 now exposes catalog planning for the read-only preflight path, but the earlier `trade health` readiness check is still not discoverable as a command catalog entry. Operators can plan order-shaped readiness, yet the broker/HID health pre-check remains outside the registry.

Adding a health catalog entry makes the existing read-only health workflow discoverable before any buy/sell/confirm path is considered.

## What Changes

- Add a trade preset for PingAn desktop health readiness.
- Add a `trade-health-pingan-readiness` command catalog entry with `trade`, `pingan`, `health`, and `readiness` labels.
- Extend catalog plan/preview trade boundary metadata to recognize `health` as a read-only desktop health workflow.
- Update `FUNCTION_TREE.md` D-07 evidence and boundary.

## Capabilities

### New Capabilities

- `tdx-command-catalog`: expose a plan-able PingAn trade health readiness entry and non-executing input coverage summary.

### Modified Capabilities

- None.

## Impact

- Runtime catalog/preset data: `runtime/command-catalog.json`, `runtime/trade-presets.json`
- CLI planning metadata: `tdxquant/cli.py`
- Trade preset registry: `tdxquant/trade/preset.py`
- Tests: `tests/test_api_cli.py`
- Registry: `FUNCTION_TREE.md`

