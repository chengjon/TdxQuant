## Why

D-08 has side-explicit task catalog entries for buy/sell submit-once, but the direct trade-source `submit-once` catalog entry still plans without `trade_plan_boundary`. That leaves the registry unable to summarize input coverage for the direct trade preset, even though it already exists in the catalog.

Adding the direct submit-once plan boundary makes the existing entry's non-executing plan semantics explicit without running a desktop workflow.

## What Changes

- Add a `submit-once` label to the existing direct trade catalog entry.
- Make the direct `submit-once-default` trade preset explicitly declare its default side as `buy`.
- Extend catalog plan/preview trade boundary metadata to recognize direct trade-source `submit-once`.
- Update `FUNCTION_TREE.md` D-08 evidence and boundary.

## Capabilities

### New Capabilities

- `tdx-command-catalog`: expose direct trade-source submit-once input coverage metadata in non-executing catalog plan/preview summaries.

### Modified Capabilities

- None.

## Impact

- Runtime catalog/preset data: `runtime/command-catalog.json`, `runtime/trade-presets.json`
- CLI planning metadata: `tdxquant/cli.py`
- Tests: `tests/test_api_cli.py`
- Registry: `FUNCTION_TREE.md`

