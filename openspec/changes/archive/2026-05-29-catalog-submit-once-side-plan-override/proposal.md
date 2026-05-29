## Why

D-08 catalog planning now exposes direct submit-once input coverage, but generic `catalog plan` / `catalog preview` cannot accept a side override. Operators can only inspect the preset default side unless they switch to side-specific task entries.

Adding a plan/preview-only `--side` override makes the generic submit-once catalog entry useful for read-only buy/sell boundary checks without widening catalog execution.

## What Changes

- Allow `catalog plan` and `catalog preview` to accept `--side buy|sell`.
- Keep `catalog run` unchanged so this slice does not add a new execution-side override.
- Add tests proving `submit-once` plan/preview side override is reflected in `trade_plan_boundary`.
- Update `FUNCTION_TREE.md` D-08 evidence and boundary.

## Capabilities

### New Capabilities

- `tdx-command-catalog`: expose non-executing submit-once side override previews in catalog plan/preview summaries.

### Modified Capabilities

- None.

## Impact

- CLI parser/planning metadata: `tdxquant/cli.py`
- Tests: `tests/test_api_cli.py`
- Registry: `FUNCTION_TREE.md`

