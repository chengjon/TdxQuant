## Why

D-07 already has a stable `trade preflight` CLI path for PingAn desktop readiness checks, but the command catalog cannot discover or plan that read-only workflow as a first-class entry. Operators can see buy/sell/submit/confirm catalog coverage, while preflight remains outside the registry.

Adding a preflight catalog entry makes the existing read-only readiness path visible to `catalog list` and `catalog plan` without executing a trade workflow.

## What Changes

- Add a trade preset for PingAn preflight readiness.
- Add a `trade-preflight-pingan-readiness` command catalog entry with `trade`, `pingan`, `preflight`, and `readiness` labels.
- Extend catalog plan/preview trade input boundary metadata to recognize `preflight` as an order-shaped read-only readiness workflow.
- Update `FUNCTION_TREE.md` D-07 evidence and boundary.

## Capabilities

### New Capabilities

- `tdx-command-catalog`: expose a plan-able PingAn trade preflight entry and non-executing input coverage summary.

### Modified Capabilities

- None.

## Impact

- Runtime catalog/preset data: `runtime/command-catalog.json`, `runtime/trade-presets.json`
- CLI planning metadata: `tdxquant/cli.py`
- Trade preset registry: `tdxquant/trade/preset.py`
- Tests: `tests/test_api_cli.py`
- Registry: `FUNCTION_TREE.md`

